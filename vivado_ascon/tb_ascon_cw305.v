// tb_ascon_cw305.v — testbench to verify the Ascon CW305 wrapper handshake.
// Drives load_i once with a known key/nonce, waits for busy_o->low, then
// prints the ciphertext+tag in data_o. This validates the START (load_i)
// and END (busy/done) pulses WITHOUT hardware.
`timescale 1ns/1ps
`default_nettype none
module tb_ascon_cw305;

    reg clk = 0;
    reg load_i = 0;
    reg rst = 0;
    reg [127:0] key_i = 128'h000102030405060708090a0b0c0d0e0f;
    reg [127:0] data_i = 128'h000102030405060708090a0b0c0d0e0f; // nonce
    wire [127:0] data_o;
    wire busy_o, done_o, tio_trigger;

    // instantiate the actual wrapper
    ascon_cw305_core #(.k(128),.y(32),.l(0),.r(64),.a(12),.b(6)) uut (
        .clk(clk), .load_i(load_i), .key_i(key_i), .data_i(data_i),
        .data_o(data_o), .busy_o(busy_o), .done_o(done_o), .tio_trigger(tio_trigger)
    );

    always #5 clk = ~clk;

    integer cycles;
    initial begin
        // test: start
        @(posedge clk);
        load_i = 1; @(posedge clk);
        load_i = 0;

        cycles = 0;
        while (!done_o && cycles < 2000) begin
            @(posedge clk); cycles = cycles + 1;
        end
        @(posedge clk);
        $display("=== done after %0d cycles ===", cycles);
        $display("ciphertext/tag (data_o) = %32h", data_o);
        $display("busy=%0b done_o=%0b", busy_o, done_o);
        #20;
        if (done_o) $display("PASS: done pulse detected");
        else        $display("FAIL: never got done pulse");
        $finish;
    end
endmodule