// tb_verify.sv — multi-vector testbench for ascon_top.
// Drives the 5 NIST KAT vectors (same as sanity_check.py), compares the
// simulated host readback (tag[:12] + ct[:4], LSB-first like the FPGA reg
// file) against expected values from the Python oracle.
`timescale 1ns/1ps

module tb_verify;
    reg clk = 0;
    reg reset_n = 0;
    reg reset_n_lfsr = 0;
    reg start = 0;
    reg [63:0] key1, key2;
    reg [63:0] nonce1, nonce2;
    reg [63:0] iv = 64'h00001000808c0001;
    reg load_data = 0;
    reg [127:0] data_in = 0;
    reg valid_data_in = 0;
    reg last_block = 0;
    reg [4:0] valid_bytes = 0;
    reg EOT = 0;

    wire ciphertext_valid;
    wire [127:0] ciphertext;
    wire done;
    wire ready_tag;
    wire [63:0] tag1, tag2;
    wire read_data;
    wire ready_for_data;
    wire [319:0] state_reg;

    reg [127:0] exp_ro;       // expected readback from Python oracle
    reg [127:0] simulated_ro; // simulated readback, byte-reversed like FPGA reg file
    reg done_flag;
    reg [127:0] latched_ct;   // ciphertext latched on ciphertext_valid posedge
    reg [63:0]  latched_tag1, latched_tag2; // tag latched on ready_tag posedge
    integer errors;

    // The FPGA register file returns bytes LSB-first (reg_read_data =
    // reg_*[reg_bytecnt*8+:8]), so byte 0 of the host readback is bits [7:0]
    // of each captured register. Replicate that byte reversal here.
    function automatic [127:0] rev_bytes128(input [127:0] x);
        for (int i = 0; i < 16; i = i + 1)
            rev_bytes128[i*8 +: 8] = x[(15-i)*8 +: 8];
    endfunction
    function automatic [63:0] rev_bytes64(input [63:0] x);
        for (int i = 0; i < 8; i = i + 1)
            rev_bytes64[i*8 +: 8] = x[(7-i)*8 +: 8];
    endfunction
    function automatic [31:0] rev_bytes32(input [31:0] x);
        for (int i = 0; i < 4; i = i + 1)
            rev_bytes32[i*8 +: 8] = x[(3-i)*8 +: 8];
    endfunction

    // 5 NIST KAT vectors, byte order mirrored from the FPGA wrapper:
    // key1 = crypt_key[63:0] = host key bytes 0..7 LSB-first, etc.
    typedef struct {
        logic [63:0] key1, key2, nonce1, nonce2;
        logic [127:0] exp;
    } vector_t;
    vector_t vectors [5] = '{
        '{64'h0706050403020100, 64'h0f0e0d0c0b0a0908, 64'h0706050403020100, 64'h0f0e0d0c0b0a0908, 128'h19c8f96a6b6a4fe5caa719a719378c6a},
        '{64'hbebafecaefbeadde, 64'h0706050403020100, 64'h8070605040302010, 64'h00f0e0d0c0b0a090, 128'h94f0b9bc9fa873085c828fe6d1dc9341},
        '{64'h0000000000000000, 64'h0000000000000000, 64'h0000000000000000, 64'h0000000000000000, 128'h3e2a56698ec81e2e053815e89761cfb5},
        '{64'hffffffffffffffff, 64'hffffffffffffffff, 64'hffffffffffffffff, 64'hffffffffffffffff, 128'h6a9d3f7ad41bbe299bf43620864ebb5a},
        '{64'hefcdab8967452301, 64'hefcdab8967452301, 64'h1032547698badcfe, 64'h1032547698badcfe, 128'h502074376152408dc9d470724dc496f3}
    };

    always #5 clk = ~clk;

    ascon_top uut (
        .clk               (clk),
        .reset_n           (reset_n),
        .reset_n_lfsr      (reset_n_lfsr),
        .start             (start),
        .key1              (key1),
        .key2              (key2),
        .load_data         (load_data),
        .nonce1            (nonce1),
        .nonce2            (nonce2),
        .initialVector     (iv),
        .data_in           (data_in),
        .valid_data_in     (valid_data_in),
        .last_block        (last_block),
        .valid_bytes       (valid_bytes),
        .EOT               (EOT),
        .state_reg_out     (state_reg),
        .ciphertext_valid  (ciphertext_valid),
        .ciphertext        (ciphertext),
        .done              (done),
        .ready_tag         (ready_tag),
        .tag1              (tag1),
        .tag2              (tag2),
        .read_data         (read_data),
        .ready_for_data    (ready_for_data)
    );

    task set_ad_input;
        // 4 bytes of zero AD
        valid_data_in = 1;
        last_block = 1;
        EOT = 0;
        valid_bytes = 4;
        data_in = 0;
    endtask

    task set_pt_input;
        // 4 bytes of zero PT
        valid_data_in = 1;
        last_block = 1;
        EOT = 1;
        valid_bytes = 4;
        data_in = 0;
    endtask

    task automatic run_vector(input vector_t v, input integer idx);
        begin
            // Set key and nonce (mirror FPGA wrapper byte order)
            key1 = v.key1;
            key2 = v.key2;
            nonce1 = v.nonce1;
            nonce2 = v.nonce2;
            exp_ro = v.exp;

            // Start encryption
            // INIT_LOAD -> INIT_ROUND_SHIFT needs start high during a posedge while in INIT_LOAD;
            // hold both for several cycles to avoid a race with the FSM sampling them.
            start = 1;
            load_data = 1;
            repeat (4) @(posedge clk);
            start = 0;
            load_data = 0;

            // Wait for ready_for_data (core wants AD input)
            wait(ready_for_data);
            @(posedge clk);
            set_ad_input();
            @(posedge clk);
            valid_data_in = 0;

            // Wait for ready_for_data (core wants PT input) 
            wait(ready_for_data);
            @(posedge clk);
            set_pt_input();
            // ciphertext_valid pulses while valid_data_in==1 in ABSORB_MSG_DATA;
            // latch ciphertext on the posedge like the FPGA register file does.
            wait(ciphertext_valid);
            @(posedge clk);
            latched_ct = ciphertext;
            $display("CT = %032h", latched_ct);
            valid_data_in = 0;

            // tag_valid (ready_tag) pulses during the final diffusion round;
            // latch tag on the posedge like the FPGA register file does.
            wait(ready_tag);
            @(posedge clk);
            latched_tag2 = tag2;
            latched_tag1 = tag1;
            $display("TAG = %016h%016h", latched_tag2, latched_tag1);

            // Wait for done
            done_flag = 0;
            repeat (1000) @(posedge clk) if (done) done_flag = 1;

            if (!done_flag) begin
                $display("FAIL v%0d: core never asserted done", idx);
                errors = errors + 1;
            end

            // Build readback the way the FPGA host sees it: tag1 (8B, LSB-first),
            // then tag2 low 4B (LSB-first), then ciphertext low 4B (LSB-first).
            simulated_ro = {rev_bytes64(latched_tag1), rev_bytes32(latched_tag2[31:0]), rev_bytes32(latched_ct[31:0])};
            $display("SIM readback = %032h", simulated_ro);

            if (simulated_ro == exp_ro)
                $display("PASS v%0d: simulation matches expected readback", idx);
            else begin
                $display("FAIL v%0d: sim=%032h exp=%032h", idx, simulated_ro, exp_ro);
                errors = errors + 1;
            end
        end
    endtask

    initial begin
        $dumpfile("tb_verify.fst");
        $dumpvars(0, tb_verify);

        errors = 0;

        // Reset
        reset_n = 0;
        reset_n_lfsr = 0;
        #20;
        reset_n = 1;
        reset_n_lfsr = 1;
        #10;

        for (int i = 0; i < 5; i = i + 1) begin
            $display("=== vector %0d ===", i);
            run_vector(vectors[i], i);
        end

        if (errors == 0)
            $display("ALL 5 VECTORS PASS");
        else
            $display("FAILURES: %0d/5", errors);

        $finish;
    end

endmodule
