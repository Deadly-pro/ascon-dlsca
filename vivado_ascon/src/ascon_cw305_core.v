// ascon_cw305_core.v
// Parallel-load wrapper around the serialized ascon-hw-public Ascon core
// for the CW305 register interface (cw305_reg_aes.v).
// TI=0, FP=0: plain unprotected Ascon (best SCA leakage).
//
// CW305 crypto-core interface (matches cw305_top.v aes_core usage):
//   clk, load_i(pulse), key_i[127:0], data_i[127:0] (=nonce), busy_o,
//   done_o, data_o[127:0] (ciphertext in [y-1:0], tag in [127:128-y]).
//   tio_trigger = busy (for trace window around init).
//
// The ascon core loads key/nonce/AD/PT serially (LSB first) driven by its
// internal counter `i` (see ascon_encryption.v). This wrapper runs a
// lockstep bit counter, presents the right bit each cycle, then pulses
// encryption_start, then shifts out cipher + tag into data_o.

`default_nettype wire
`timescale 1ns / 1ps

module ascon_cw305_core #(
    parameter k = 128,
    parameter y = 32,
    parameter l = 32,
    parameter r = 64,
    parameter a = 12,
    parameter b = 6
)(
    input  wire        clk,
    input  wire        load_i,
    input  wire [127:0] key_i,
    input  wire [127:0] data_i,        // nonce
    output wire [127:0] data_o,        // ciphertext + tag
    output wire        busy_o,
    output wire        done_o,
    output wire        tio_trigger
);

    reg start_pulse;
    reg [1:0] start_count;
    wire core_rst = load_i;   // reset Ascon core counter in lockstep with our loader

    // --- lockstep serial bit counter + input shift regs ---
    reg [7:0] i;                 // matches core's internal i
    reg [k-1:0]  key_sr;
    reg [127:0]  nonce_sr;
    reg [y-1:0]  pt_sr;
    reg          started;        // core begun loading (i running)

    // --- output capture ---
    reg [127:0]  ct_sr;
    reg [127:0]  tag_sr;
    reg [7:0]    j;              // cipher shift-out counter
    reg [7:0]    jt;             // tag shift-out counter
    reg          done_r;
    reg          enc_was_ready;

    wire         enc_ready;
    wire         cipher_bit;
    wire         tag_bit;

    // Ascon core (bit-serial) from ascon-hw-public, plain config
    Ascon #(
        .k(k), .r(r), .a(a), .b(b), .l(l), .y(y), .TI(0), .FP(0)
    ) u_ascon (
        .clk                 (clk),
        .rst                 (core_rst),
        .keyxSI              ({4'd0, key_sr[0]}),
        .noncexSI            ({4'd0, nonce_sr[0]}),
        .associated_dataxSI  ({4'd0, 1'b0}),
        .plain_textxSI       ({4'd0, pt_sr[0]}),
        .encryption_startxSI (start_pulse),
        .decryption_startxSI (1'b0),
        .r_64xSI             (14'd0),
        .r_128xSI            (3'd0),
        .r_ptxSI             (3'd0),
        .cipher_textxSO      (cipher_bit),
        .plain_textxS0       (),
        .tagxSO              (tag_bit),
        .dec_tagxSO          (),
        .encryption_readyxSO (enc_ready),
        .decryption_readyxSO (),
        .message_authentication()
    );
    // drive trigger high while core is running
    assign tio_trigger = started;

    always @(posedge clk) begin
        if (load_i) begin
            // latch inputs and start the lockstep loader
            key_sr   <= key_i;
            nonce_sr <= data_i;
            pt_sr    <= 0;
            i        <= 0;
            started  <= 1;
            done_r   <= 0;
            ct_sr    <= 0;
            tag_sr   <= 0;
            j        <= 0;
            jt       <= 0;
            enc_was_ready <= 0;
            start_count <= 0;
            start_pulse  <= 0;
        end else begin
            if (started) begin
                // feed one serial bit per cycle (LSB first)
                key_sr   <= {key_sr[k-2:0], 1'b0};
                nonce_sr <= {nonce_sr[126:0], 1'b0};
                pt_sr    <= {pt_sr[y-2:0], 1'b0};
                i <= i + 1;

                // after all inputs loaded (i>k, i>128, i>l, i>y), pulse start
                if (start_pulse)
                    start_pulse <= 0;
                if (start_count[0]) begin
                    start_pulse <= 1;
                    start_count <= start_count + 1;
                end else if (i > k && i > 128 && i > l && i > y && !enc_was_ready) begin
                    start_count <= start_count + 1;
                end

                // capture cipher bits during encryption_ready
                if (enc_ready) begin
                    enc_was_ready <= 1;
                    if (j < y) begin
                        ct_sr[j] <= cipher_bit;
                        j <= j + 1;
                    end
                    if (jt < 128) begin
                        tag_sr[jt] <= tag_bit;
                        jt <= jt + 1;
                    end
                end

                // done when tag fully shifted out
                if (jt >= 128 && !done_r) begin
                    done_r <= 1;
                    started <= 0;
                end
            end
        end
    end

    assign data_o = {tag_sr[95:0], ct_sr[y-1:0]};
    assign busy_o = started;
    assign done_o = done_r;

endmodule
