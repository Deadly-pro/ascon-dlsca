// tb_full.sv — exercises the two-beat (16-byte PT) path through the adapter,
// mirroring live_query.py: AD = 4 zero bytes, PT = 16 zero bytes.
`timescale 1ns/1ps
`include "config.sv"

module tb_full;
    reg clk = 0;
    reg reset_n = 0, reset_n_lfsr = 0, start = 0, load_data = 0;
    reg [63:0] key1, key2, nonce1, nonce2;
    reg [63:0] iv = 64'h00001000808c0001;
    reg [127:0] data_in = 0;
    reg valid_data_in = 0, last_block = 0, EOT = 0;
    reg [4:0] valid_bytes = 0;

    wire ciphertext_valid, done, ready_tag, read_data, ready_for_data;
    wire [127:0] ciphertext;
    wire [63:0] tag1, tag2;
    wire [319:0] state_reg;

    always #5 clk = ~clk;

    ascon_top uut (
        .clk(clk), .reset_n(reset_n), .reset_n_lfsr(reset_n_lfsr),
        .start(start), .key1(key1), .key2(key2), .load_data(load_data),
        .nonce1(nonce1), .nonce2(nonce2), .initialVector(iv),
        .data_in(data_in), .valid_data_in(valid_data_in),
        .last_block(last_block), .valid_bytes(valid_bytes), .EOT(EOT),
        .state_reg_out(state_reg), .ciphertext_valid(ciphertext_valid),
        .ciphertext(ciphertext), .done(done), .ready_tag(ready_tag),
        .tag1(tag1), .tag2(tag2), .read_data(read_data),
        .ready_for_data(ready_for_data)
    );

    integer errors = 0;

    initial begin
        key1 = 64'h0706050403020100; key2 = 64'h0f0e0d0c0b0a0908;
        nonce1 = 64'h0706050403020100; nonce2 = 64'h0f0e0d0c0b0a0908;

        reset_n = 0; reset_n_lfsr = 0;
        repeat (3) @(negedge clk);
        reset_n = 1; reset_n_lfsr = 1;
        repeat (2) @(negedge clk);

        // launch (mirror wrapper: start+load_data together)
        start = 1; load_data = 1;
        repeat (4) @(negedge clk);
        start = 0; load_data = 0;

        // AD block: 4 zero bytes
        wait (ready_for_data);
        @(negedge clk);
        data_in = 128'h0; valid_bytes = 5'd4; last_block = 1; EOT = 0;
        valid_data_in = 1;
        @(negedge clk);
        valid_data_in = 0; last_block = 0;

        // PT block: 16 zero bytes (two-beat path)
        wait (ready_for_data);
        @(negedge clk);
        data_in = 128'h0; valid_bytes = 5'd16; last_block = 1; EOT = 1;
        valid_data_in = 1;
        wait (ciphertext_valid);
        @(negedge clk);
        valid_data_in = 0; EOT = 0;

        if (ciphertext !== {64'h678418440f3c7887, 64'h598eb4976a8c3719}) begin
            $display("FAIL ct = %032h", ciphertext); errors++;
        end else $display("ct OK: %032h", ciphertext);

        wait (ready_tag);
        @(negedge clk);
        if ({tag2, tag1} !== {64'h76ede61f26413667, 64'h88792561083fc44e}) begin
            $display("FAIL tag = %032h", {tag2, tag1}); errors++;
        end else $display("tag OK");

        repeat (20) @(negedge clk);
        // state observability: after finalization x3,x4 == tag words
        if (state_reg[4*64 +: 64] !== tag2 || state_reg[3*64 +: 64] !== tag1) begin
            $display("FAIL state x3/x4 vs tag"); errors++;
        end else $display("live state observable through adapter OK");

        if (errors == 0) $display("FULL-PATH 16B TEST PASS");
        else $display("FAILURES: %0d", errors);
        $finish;
    end

    initial begin
        #100000;
        $display("WATCHDOG timeout"); $finish;
    end
endmodule
