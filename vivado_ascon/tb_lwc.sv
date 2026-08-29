// tb_lwc.sv — mixed-language KAT testbench for ascon_top + LWC CryptoCore.
// Runs the 5 NIST KAT vectors (AD=4 zero bytes, PT=4 zero bytes, the same
// vectors as sanity_check.py) and verifies ciphertext+tag byte-exact.
// Also samples dbg_state during the round-1 S-box for byte-order checks.

module tb_lwc;

    logic clk = 0, reset_n = 0;
    logic start, load_data;
    logic [63:0] key1, key2, nonce1, nonce2, initialVector;
    logic [127:0] data_in;
    logic valid_data_in, last_block, EOT;
    logic [4:0] valid_bytes;
    logic [319:0] state_reg_out;
    logic ciphertext_valid, done, ready_tag;
    logic [127:0] ciphertext;
    logic [63:0] tag1, tag2;
    logic ready_for_data, read_data;

    always #5 clk = ~clk;  // 100 MHz

    ascon_top u_dut (
        .clk(clk), .reset_n(reset_n), .reset_n_lfsr(1'b1), .start(start),
        .key1(key1), .key2(key2), .load_data(load_data),
        .nonce1(nonce1), .nonce2(nonce2), .initialVector(initialVector),
        .data_in(data_in), .valid_data_in(valid_data_in), .last_block(last_block),
        .valid_bytes(valid_bytes), .EOT(EOT),
        .state_reg_out(state_reg_out), .ciphertext_valid(ciphertext_valid),
        .ciphertext(ciphertext), .done(done), .ready_tag(ready_tag),
        .tag1(tag1), .tag2(tag2), .ready_for_data(ready_for_data),
        .read_data(read_data)
    );

    // KAT vectors: (key, nonce, ct4, tag16)
    typedef struct {
        logic [127:0] key;
        logic [127:0] nonce;
        logic [31:0]  ct;
        logic [127:0] tag;
    } kat_t;

    const kat_t KATS [5] = '{
        '{128'h000102030405060708090a0b0c0d0e0f, 128'h000102030405060708090a0b0c0d0e0f, 32'h19378c6a, 128'h19c8f96a6b6a4fe5caa719a760c78aba},
        '{128'hdeadbeefcafebabe0001020304050607, 128'h102030405060708090a0b0c0d0e0f000, 32'hd1dc9341, 128'h94f0b9bc9fa873085c828fe648c34f28},
        '{128'h00000000000000000000000000000000, 128'h00000000000000000000000000000000, 32'h9761cfb5, 128'h3e2a56698ec81e2e053815e880d27d7d},
        '{128'hffffffffffffffffffffffffffffffff, 128'hffffffffffffffffffffffffffffffff, 32'h864ebb5a, 128'h6a9d3f7ad41bbe299bf436206894108b},
        '{128'h0123456789abcdef0123456789abcdef, 128'hfedcba9876543210fedcba9876543210, 32'h4dc496f3, 128'h502074376152408dc9d4707221552e27}
    };

    int errs = 0;
    logic [319:0] r1_state_snapshot;
    logic r1_captured;
    logic g_cap = 0;  // capture only during vector 0

    // Pre-perm state: at the posedge where core enters INIT_PROCESS (4) with
    // cnt=12, ascon_state_s still holds IV||key||nonce (round-1 result is not
    // registered until the NEXT posedge).
    logic [319:0] pre_state_snapshot, pre_raw_snapshot;
    logic pre_captured;
    always_ff @(posedge clk) begin
        if (g_cap && u_dut.dbg_fsm == 8'd4 && u_dut.dbg_cnt == 4'd12) begin
            pre_state_snapshot <= state_reg_out;
            pre_raw_snapshot <= u_dut.dbg_state_raw;
            pre_captured <= 1'b1;
        end
    end

    // ABSORB_MSG state: after AD processing + domain separation
    logic [319:0] msg_state_snapshot;
    always_ff @(posedge clk) begin
        if (g_cap && u_dut.dbg_fsm == 8'd10 && u_dut.dbg_widx == 8'd0)
            msg_state_snapshot <= state_reg_out;
    end

    // Round-1 S-box output: at the posedge where cnt decrements to 11,
    // ascon_state_s holds the round-1 S-box result.
    logic [319:0] final_state_snapshot;
    always_ff @(posedge clk) begin
        if (g_cap && u_dut.dbg_fsm == 8'd16)  // EXTRACT_TAG first cycle
            final_state_snapshot <= state_reg_out;
    end

    always_ff @(posedge clk) begin
        if (g_cap && u_dut.dbg_fsm == 8'd4 && u_dut.dbg_cnt == 4'd11) begin
            r1_state_snapshot <= state_reg_out;
            r1_captured <= 1'b1;
        end
    end

    // Match the hardware register format: the host writes key bytes via
    // REG_KEY (byte-addressable), crypt_key = {key[15]..key[0]} as a
    // little-endian 128-bit value. key1 = crypt_key[63:0] = byte-reversed
    // key[0:8], key2 = crypt_key[127:64] = byte-reversed key[8:16].
    function automatic logic [63:0] rev8(input logic [63:0] w);
        return {w[7:0], w[15:8], w[23:16], w[31:24],
                w[39:32], w[47:40], w[55:48], w[63:56]};
    endfunction

    task automatic run_vector(int vi);
        automatic logic [127:0] exp_ct_t = {KATS[vi].ct, 96'h0};
        automatic logic [127:0] exp_tag = KATS[vi].tag;
        automatic logic [127:0] got_ct, got_tag;
        automatic int cycles = 0;
        begin
            g_cap <= (vi == 0);
            key1 <= rev8(KATS[vi].key[127:64]);  // key[0:8] -> little-endian reg
            key2 <= rev8(KATS[vi].key[63:0]);    // key[8:16]
            $display("[TB] vec %0d key1=%016h key2=%016h", vi, rev8(KATS[vi].key[127:64]), rev8(KATS[vi].key[63:0]));
            nonce1 <= rev8(KATS[vi].nonce[127:64]);
            nonce2 <= rev8(KATS[vi].nonce[63:0]);
            data_in <= {96'h0, 32'h00000000};  // AD = 4 zero bytes (top bytes)
            valid_bytes <= 5'd4;
            EOT <= 1'b0;
            start <= 1'b0;
            @(posedge clk);

            start <= 1'b1;
            @(posedge clk);
            start <= 1'b0;

            // AD phase: keep data_in = ad_in until read_data pulses
            wait (read_data == 1'b1);
            @(posedge clk);

            // MSG phase: data_in = ptx_in (4 zero bytes), EOT=1
            data_in <= {96'h0, 32'h00000000};
            EOT <= 1'b1;
            wait (ready_tag == 1'b1);
            @(posedge clk);

            got_ct  = {u_dut.ct_w[1], u_dut.ct_w[0]};
            got_tag = {u_dut.tag_w[3], u_dut.tag_w[2], u_dut.tag_w[1], u_dut.tag_w[0]};

            if (got_ct[127:96] !== exp_ct_t[127:96]) begin
                $display("[FAIL] vec %0d CT  got %08h exp %08h", vi, got_ct[127:96], exp_ct_t[127:96]);
                errs++;
            end else
                $display("[PASS] vec %0d CT  %08h", vi, got_ct[127:96]);
            if (got_tag !== exp_tag) begin
                $display("[FAIL] vec %0d TAG got %032h exp %032h", vi, got_tag, exp_tag);
                errs++;
            end else
                $display("[PASS] vec %0d TAG %032h", vi, got_tag);

            wait (done == 1'b1);
            @(posedge clk);
        end
    endtask

    initial begin
        r1_captured <= 1'b0;
        start = 0; load_data = 0; valid_data_in = 0; last_block = 0;
        data_in = '0; valid_bytes = '0; EOT = 0;
        key1 = '0; key2 = '0; nonce1 = '0; nonce2 = '0; initialVector = '0;

        repeat (4) @(posedge clk);
        reset_n <= 1'b1;
        repeat (4) @(posedge clk);

        for (int v = 0; v < 5; v++)
            run_vector(v);

        if (r1_captured)
            $display("[DBG] round1 state = %032h", r1_state_snapshot);
        else
            $display("[DBG] round1 state NOT captured");
        if (pre_captured) begin
            $display("[DBG] pre-perm state = %032h", pre_state_snapshot);
            $display("[DBG] pre-perm RAW   = %032h", pre_raw_snapshot);
        end else
            $display("[DBG] pre-perm state NOT captured");
        $display("[DBG] final state   = %032h", final_state_snapshot);
        $display("[DBG] absorb-msg st = %032h", msg_state_snapshot);

        if (errs == 0) begin
            $display("[+] ALL %0d/5 KAT VECTORS PASS", 5);
        end else begin
            $display("[!] %0d/5 KAT VECTORS FAILED", errs);
        end
        $finish;
    end

    // Dump state at each init-permutation cycle
    initial begin
        int n = 0;
        #80;
        while (n < 20) begin
            @(posedge clk);
            n++;
            if (u_dut.dbg_fsm == 8'd4)
                $display("[R] cyc=%0d cnt=%0d raw=%032h", n, u_dut.dbg_cnt, u_dut.dbg_state_raw);
        end
    end

endmodule