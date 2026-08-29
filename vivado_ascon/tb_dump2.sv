`timescale 1ns/1ps
module tb_dump2;
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
    integer cyc;
    reg [255:0] mem [0:19];
    initial $readmemh("/tmp/vecs256.hex", mem);
    always #5 clk = ~clk;
    ascon_top uut (
        .clk(clk), .reset_n(reset_n), .reset_n_lfsr(reset_n_lfsr), .start(start),
        .key1(key1), .key2(key2), .load_data(load_data), .nonce1(nonce1), .nonce2(nonce2),
        .initialVector(iv), .data_in(data_in), .valid_data_in(valid_data_in),
        .last_block(last_block), .valid_bytes(valid_bytes), .EOT(EOT),
        .state_reg_out(state_reg), .ciphertext_valid(ciphertext_valid),
        .ciphertext(ciphertext), .done(done), .ready_tag(ready_tag),
        .tag1(tag1), .tag2(tag2), .read_data(read_data), .ready_for_data(ready_for_data)
    );
    initial begin
        reset_n = 0; reset_n_lfsr = 0;
        #20;
        reset_n = 1; reset_n_lfsr = 1;
        #10;
        for (int i = 0; i < 20; i = i + 1) begin
            // full reset between vectors so each load sequence is identical
            reset_n = 0; reset_n_lfsr = 0;
            start = 0; load_data = 0;
            repeat (4) @(posedge clk);
            reset_n = 1; reset_n_lfsr = 1;
            repeat (2) @(posedge clk);
            key1 = mem[i][63:0];
            key2 = mem[i][127:64];
            nonce1 = mem[i][191:128];
            nonce2 = mem[i][255:192];
            start = 1; load_data = 1;
            cyc = 0;
            $display("VEC %0d", i);
            repeat (64) begin
                @(posedge clk);
                cyc = cyc + 1;
                $display("C%0d %h", cyc, state_reg);
            end
            start = 0; load_data = 0;
        end
        $finish;
    end
endmodule
