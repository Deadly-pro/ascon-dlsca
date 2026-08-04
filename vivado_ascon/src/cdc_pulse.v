// cdc_pulse.v — behavioral CDC pulse synchronizer.
// Channels a single-cycle src pulse across two unrelated clock domains.
// Port names match the instantiation in cw305_reg_aes.v.
`default_nettype wire
`timescale 1ns / 1ps
module cdc_pulse (
    input  wire reset_i,     // async/active-high reset (src domain)
    input  wire src_clk,      // source clock
    input  wire src_pulse,    // single-cycle pulse in src domain
    input  wire dst_clk,      // destination clock
    output wire dst_pulse     // single-cycle pulse in dst domain
);

    reg src_toggle = 1'b0;
    reg [2:0] sync_sync = 3'b000;
    wire [2:0] sync_sync_q;

    // src side: flip toggle on each pulse
    always @(posedge src_clk or posedge reset_i) begin
        if (reset_i)
            src_toggle <= 1'b0;
        else if (src_pulse)
            src_toggle <= ~src_toggle;
    end

    // two-flop sync of toggle into dst clock
    always @(posedge dst_clk or posedge reset_i) begin
        if (reset_i)
            sync_sync <= 3'b000;
        else
            sync_sync <= {sync_sync[1:0], src_toggle};
    end
    assign sync_sync_q = sync_sync;

    // pulse on toggle edge
    assign dst_pulse = sync_sync_q[1] ^ sync_sync_q[2];
endmodule
