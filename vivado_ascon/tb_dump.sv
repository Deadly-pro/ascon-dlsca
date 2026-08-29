// tb_dump.sv — dump ascon_top internal state every cycle for the 5 KAT
// vectors, so the host script can locate the first-INIT (loaded) state and
// derive the exact per-column round-1 chi values the core computes.
`timescale 1ns/1ps
module tb_dump;
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
    typedef struct {
        logic [63:0] key1, key2, nonce1, nonce2;
    } vector_t;
    vector_t vectors [5] = '{
        '{64'h0706050403020100, 64'h0f0e0d0c0b0a0908, 64'h0706050403020100, 64'h0f0e0d0c0b0a0908},
        '{64'hbebafecaefbeadde, 64'h0706050403020100, 64'h8070605040302010, 64'h00f0e0d0c0b0a090},
        '{64'h0000000000000000, 64'h0000000000000000, 64'h0000000000000000, 64'h0000000000000000},
        '{64'hffffffffffffffff, 64'hffffffffffffffff, 64'hffffffffffffffff, 64'hffffffffffffffff},
        '{64'hefcdab8967452301, 64'hefcdab8967452301, 64'h1032547698badcfe, 64'h1032547698badcfe}
    };
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
    task set_ad_input;
        valid_data_in = 1; last_block = 1; EOT = 0; valid_bytes = 4; data_in = 0;
    endtask
    task set_pt_input;
        valid_data_in = 1; last_block = 1; EOT = 1; valid_bytes = 4; data_in = 0;
    endtask
    initial begin
        reset_n = 0; reset_n_lfsr = 0;
        #20;
        reset_n = 1; reset_n_lfsr = 1;
        #10;
        for (int i = 0; i < 5; i = i + 1) begin
            key1 = vectors[i].key1; key2 = vectors[i].key2;
            nonce1 = vectors[i].nonce1; nonce2 = vectors[i].nonce2;
            start = 1; load_data = 1;
            cyc = 0;
            $display("VEC %0d", i);
            repeat (40) begin
                @(posedge clk);
                cyc = cyc + 1;
                $display("C%0d %h", cyc, state_reg);
            end
            start = 0; load_data = 0;
            // let the adapter settle before next vector (mimic tb_verify drive)
            repeat (4) @(posedge clk);
        end
        $finish;
    end
endmodule