// tb_core.sv — standalone verification of the vendored rprimas ascon_core (V4: 64-bit, UROL=1).
// 1. Runs the 5 NIST KATs (same vectors as tb_verify.sv / sanity_check.py) through the
//    raw BDI interface; checks ct + tag byte-exact against .venv/bin/python ascon_ref.
// 2. Checks the internal state register is REAL unmasked state: after finalization
//    x3,x4 hold tag1,tag2 (key already folded in by KADD_4).
// Compile (from vivado_ascon/): verilator --binary --timing -Wno-fatal -Wno-WIDTH
//   with -Irtl_ref, sources tb_core.sv + rtl_ref/*.sv, output /tmp/tb_core
`timescale 1ns/1ps
`include "rtl_ref/config.sv"

module tb_core;
    reg clk = 0;
    reg rst = 1;
    reg [63:0] key, bdi;
    reg key_valid = 0;
    reg [7:0] bdi_valid = 0;
    reg bdi_eot = 0, bdi_eoi = 0;
    data_t bdi_type = D_INVALID;
    mode_t mode = M_INVALID;
    reg bdo_ready = 1;
    reg bdo_eoo = 0;

    wire key_ready, bdi_ready, bdo_valid, auth, auth_valid;
    wire [63:0] bdo;
    data_t bdo_type;
    wire bdo_eot;

    always #5 clk = ~clk;

    ascon_core uut (
        .clk(clk), .rst(rst),
        .key(key), .key_valid(key_valid), .key_ready(key_ready),
        .bdi(bdi), .bdi_valid(bdi_valid), .bdi_ready(bdi_ready),
        .bdi_type(bdi_type), .bdi_eot(bdi_eot), .bdi_eoi(bdi_eoi),
        .mode(mode),
        .bdo(bdo), .bdo_valid(bdo_valid), .bdo_ready(bdo_ready),
        .bdo_type(bdo_type), .bdo_eot(bdo_eot), .bdo_eoo(bdo_eoo),
        .auth(auth), .auth_valid(auth_valid)
    );

    // hierarchical taps into the single unshared state register
    wire [63:0] st3 = uut.state_q[3][0];
    wire [63:0] st4 = uut.state_q[4][0];
    wire [4:0] cfsm = uut.fsm_q;  // 2=LD_KEY 3=LD_NPUB 5=KADD_2 6=ABS_AD 7=PAD_AD 10=ABS_MSG

    typedef struct {
        logic [63:0] k1, k2, n1, n2, tag1, tag2;
        logic [31:0] ct;
    } vector_t;

    vector_t vectors [5] = '{
        '{64'h0706050403020100, 64'h0f0e0d0c0b0a0908, 64'h0706050403020100, 64'h0f0e0d0c0b0a0908, 64'he54f6a6b6af9c819, 64'hba8ac760a719a7ca, 32'h6a8c3719},
        '{64'hbebafecaefbeadde, 64'h0706050403020100, 64'h8070605040302010, 64'h00f0e0d0c0b0a090, 64'h0873a89fbcb9f094, 64'h284fc348e68f825c, 32'h4193dcd1},
        '{64'h0000000000000000, 64'h0000000000000000, 64'h0000000000000000, 64'h0000000000000000, 64'h2e1ec88e69562a3e, 64'h7d7dd280e8153805, 32'hb5cf6197},
        '{64'hffffffffffffffff, 64'hffffffffffffffff, 64'hffffffffffffffff, 64'hffffffffffffffff, 64'h29be1bd47a3f9d6a, 64'h8b1094682036f49b, 32'h5abb4e86},
        '{64'hefcdab8967452301, 64'hefcdab8967452301, 64'h1032547698badcfe, 64'h1032547698badcfe, 64'h8d40526137742050, 64'h272e55217270d4c9, 32'hf396c44d}
    };

    task automatic send_key(input [63:0] kk1, input [63:0] kk2);
        begin
            while (cfsm != 5'd2) @(negedge clk);   // LD_KEY
            @(negedge clk);
            key = kk1; key_valid = 1;
            @(negedge clk);
            key = kk2;
            @(negedge clk);
            key_valid = 0; key = '0;
        end
    endtask

    // present a beat while the core is in any of the accepting states; hold until
    // it leaves them (consumption is data-driven, not bdi_ready-driven)
    // concurrent output capture (beats appear while beats are being driven)
    reg collecting = 0;
    reg [63:0] cap_ct, cap_t1, cap_t2;
    reg ct_ok = 0, t1_ok = 0, t2_ok = 0;
    always @(negedge clk) begin
        if (collecting && bdo_valid) begin
            if (bdo_type == D_MSG && !ct_ok) begin cap_ct = bdo; ct_ok = 1; end
            if (bdo_type == D_TAG && !t1_ok) begin cap_t1 = bdo; t1_ok = 1; end
            else if (bdo_type == D_TAG && !t2_ok) begin cap_t2 = bdo; t2_ok = 1; end
        end
    end

    task automatic send_beat(input [3:0] accept_states [0:2], input int n_accept,
                             input data_t typ, input [63:0] data,
                             input [7:0] vb, input logic eot, input logic eoi);
        begin
            while (!(cfsm == accept_states[0] || cfsm == accept_states[1]
                     || (n_accept > 2 && cfsm == accept_states[2])))
                @(negedge clk);
            bdi_type = typ; bdi = data; bdi_valid = vb;
            bdi_eot = eot; bdi_eoi = eoi;
            do @(negedge clk);
            while (cfsm == accept_states[0] || cfsm == accept_states[1]
                   || (n_accept > 2 && cfsm == accept_states[2]));
            bdi_valid = 0; bdi_eot = 0; bdi_eoi = 0; bdi = '0;
        end
    endtask

    task automatic run_vector(input int idx, output int errs);
        logic [63:0] ct_lo, tg1, tg2;        begin
            errs = 0;
            rst = 1;
            mode = M_INVALID; key_valid = 0; bdi_valid = 0; bdi_eot = 0; bdi_eoi = 0;
            bdi_type = D_INVALID; bdi = '0; key = '0;
            repeat (3) @(negedge clk);
            rst = 0;
            repeat (2) @(negedge clk);

            // mode+key_valid must become visible on the SAME edge,
            // otherwise the core samples IDLE+mode with key_valid==0
            // and skips LD_KEY entirely.
            @(negedge clk);
            mode = M_AEAD128_ENC; key = vectors[idx].k1; key_valid = 1;
            while (cfsm != 5'd2 && cfsm != 5'd3) begin
                @(negedge clk);
                $display("DBG waiting start: cfsm=%0d mode=%h kvalid=%b", cfsm, mode, key_valid);
            end
            if (cfsm == 5'd3)
                $display("WARN v%0d: core skipped LD_KEY (went straight to LD_NPUB)", idx);
            else
                $display("DBG v%0d in LD_KEY, presenting beats", idx);
            @(negedge clk);
            $display("DBG after b1: wcnt=%0d cfsm=%0d", uut.word_cnt_q, cfsm);
            key = vectors[idx].k2;
            @(negedge clk);
            $display("DBG after b2: wcnt=%0d cfsm=%0d", uut.word_cnt_q, cfsm);
            key_valid = 0; key = '0;
            // nonce: two consecutive beats inside LD_NPUB
            while (cfsm != 5'd3) @(negedge clk);
            bdi_type = D_NONCE; bdi_valid = 8'hFF;
            bdi = vectors[idx].n1;
            @(negedge clk);
            bdi = vectors[idx].n2;
            @(negedge clk);
            bdi_valid = 0; bdi = '0;
            begin
                logic [3:0] acc [0:2];
                acc[0] = 5'd5; acc[1] = 5'd6; acc[2] = 5'd7;     // KADD_2, ABS_AD, PAD_AD
                send_beat(acc, 3, D_AD, 64'h0, 8'h0F, 1, 0);
                acc[0] = 5'd10; acc[1] = 5'd11; acc[2] = 5'd99;  // ABS_MSG, PAD_MSG
                cap_ct = 'x; cap_t1 = 'x; cap_t2 = 'x;
                ct_ok = 0; t1_ok = 0; t2_ok = 0; collecting = 1;
                send_beat(acc, 2, D_MSG, 64'h0, 8'h0F, 1, 1);
                wait (ct_ok && t1_ok && t2_ok);
                collecting = 0;
            end
            ct_lo = cap_ct; tg1 = cap_t1; tg2 = cap_t2;
            mode = M_INVALID;

            $display("v%0d CT=%08x TAG=%016h%016h", idx, ct_lo[31:0], tg2, tg1);
            if (ct_lo[31:0] !== vectors[idx].ct) begin
                $display("FAIL v%0d ct", idx); errs++;
            end
            if (tg1 !== vectors[idx].tag1 || tg2 !== vectors[idx].tag2) begin
                $display("FAIL v%0d tag", idx); errs++;
            end

            repeat (4) @(negedge clk);
            if ({st4, st3} !== {tg2, tg1}) begin
                $display("FAIL v%0d: final state x3,x4 != tag -> state not real/unobservable", idx);
                errs++;
            end else begin
                $display("v%0d state observable: x3=%016h x4=%016h == tag words", idx, st3, st4);
            end
        end
    endtask

    always @(negedge clk)
        if ($time < 600)
            $display("t=%0t cfsm=%0d wcnt=%0d kvalid=%b bdiv=%h bdi=%h",
                     $time, uut.fsm_q, uut.word_cnt_q, key_valid, bdi_valid, bdi);

    integer errors = 0;
    integer ve;
    integer watchdog = 0;
    always @(posedge clk) begin
        watchdog <= watchdog + 1;
        if (watchdog > 5000) begin
            $display("WATCHDOG: cfsm=%0d mode=%0d key_valid=%0d bdi_valid=%0h",
                     cfsm, mode, key_valid, bdi_valid);
            $finish;
        end
    end
    initial begin
        $dumpfile("/tmp/tb_core.fst");
        $dumpvars(0, tb_core);
        for (int i = 0; i < 5; i++) begin
            run_vector(i, ve);
            errors += ve;
        end
        if (errors == 0) $display("ALL CORE CHECKS PASS");
        else $display("CORE FAILURES: %0d", errors);
        $finish;
    end
endmodule
