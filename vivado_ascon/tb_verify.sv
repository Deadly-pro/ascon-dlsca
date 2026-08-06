// tb_verify.sv — minimal testbench for ascon_top that drives a single
// encryption and compares ciphertext+tag against expected values read from
// a file written by the Python oracle.
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
    reg done_flag;

    // Read expected value from file
    integer fd;
    reg [255:0] line_buf;

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

    initial begin
        $dumpfile("tb_verify.fst");
        $dumpvars(0, tb_verify);

        // Read expected readback (32 hex chars = 128 bits)
        exp_ro = 0;
        fd = $fopen("tb_verify_exp.txt", "r");
        if (fd) begin
            $fgets(line_buf, fd);
            $fclose(fd);
            // Parse hex string to 128-bit value
            exp_ro = 128'h0;
            for (int i = 0; i < 32; i = i + 1) begin
                byte b;
                if (line_buf[i*8 +: 8] >= "0" && line_buf[i*8 +: 8] <= "9")
                    b = line_buf[i*8 +: 8] - "0";
                else if (line_buf[i*8 +: 8] >= "a" && line_buf[i*8 +: 8] <= "f")
                    b = line_buf[i*8 +: 8] - "a" + 10;
                else
                    b = line_buf[i*8 +: 8] - "A" + 10;
                exp_ro = (exp_ro << 4) | b;
            end
            $display("EXP readback = %032h", exp_ro);
        end else begin
            $display("WARNING: tb_verify_exp.txt not found, skipping expected check");
        end

        // Reset
        reset_n = 0;
        reset_n_lfsr = 0;
        #20;
        reset_n = 1;
        reset_n_lfsr = 1;
        #10;

        // Set key and nonce (case1: K=N=000102030405060708090a0b0c0d0e0f)
        key1 = 64'h0001020304050607;
        key2 = 64'h08090a0b0c0d0e0f;
        nonce1 = 64'h0001020304050607;
        nonce2 = 64'h08090a0b0c0d0e0f;

        // Start encryption
        start = 1;
        load_data = 1;
        @(posedge clk);
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
        @(posedge clk);
        valid_data_in = 0;

        // Wait for done
        done_flag = 0;
        repeat (1000) @(posedge clk) if (done) done_flag = 1;

        if (!done_flag) begin
            $display("FAIL: core never asserted done");
            $finish;
        end

        // Check ciphertext + tag
        wait(ciphertext_valid);
        $display("CT = %032h", ciphertext);

        wait(ready_tag);
        $display("TAG = %016h%016h", tag2, tag1);

        // Build readback = {tag[127:32], ct[31:0]} = {tag2[31:0], tag1, ciphertext[31:0]}
        reg [127:0] simulated_ro;
        simulated_ro = {tag2[31:0], tag1[63:0], ciphertext[31:0]};
        $display("SIM readback = %032h", simulated_ro);

        if (fd > 0) begin
            if (simulated_ro == exp_ro)
                $display("PASS: simulation matches expected readback");
            else
                $display("FAIL: sim=%032h exp=%032h", simulated_ro, exp_ro);
        end else begin
            $display("OK: simulation complete (no expected file)");
        end

        $finish;
    end

endmodule
