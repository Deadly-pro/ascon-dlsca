// ascon_top.sv — CW305 top-level crypto module.
//
// Drives the LWC CryptoCore (ascon-hardware v1, unprotected, CCW=32) through
// the BDI/BDO protocol. The CryptoCore is the exact evaluated Ascon-AEAD128
// implementation from the official ascon-hardware SCA repository.
//
// External port list is IDENTICAL to the old ascon_top, so cw305_top.v,
// cw305_reg_ascon.v and the host shim need no changes:
//   - AD block presented on data_in during PROCESS_AD (valid_bytes), MSG
//     block on data_in during PROCESS_MSG; single-block phases assumed
//   - read_data pulses when the AD block is fully absorbed (drives the
//     wrapper's PROCESS_AD -> PROCESS_MSG transition)
//   - ciphertext/tag latched and held; ciphertext_valid/ready_tag pulse once;
//     done holds from tag until the next run is armed
//   - state_reg_out = LIVE internal Ascon state {x4,x3,x2,x1,x0} with each
//     64-bit lane in canonical byte order (matching Python labels)
//   - trigger pulses at the round-1 S-box computation (init permutation rcon=12)

module ascon_top (
    input  logic clk,
    input  logic reset_n,
    input  logic reset_n_lfsr,
    input  logic start,

    input  logic [63:0] key1,
    input  logic [63:0] key2,
    input  logic load_data,

    input  logic [63:0] nonce1,
    input  logic [63:0] nonce2,
    input  logic [63:0] initialVector,

    input  logic [127:0] data_in,
    input  logic valid_data_in,
    input  logic last_block,
    input  logic [4:0] valid_bytes,
    input  logic EOT,

    output logic [319:0]   state_reg_out,
    output logic           ciphertext_valid,
    output logic [127:0]   ciphertext,
    output logic           done,
    output logic           ready_tag,
    output logic [63:0]    tag1,
    output logic [63:0]    tag2,
    output logic           ready_for_data,
    output logic           read_data
`ifdef DEBUG
    , output logic [4:0]  dbg_fsm_debug,
      output logic [31:0] dbg_cnt_debug
`endif
);

    // ------------------------------------------------------------------
    // LWC CryptoCore (VHDL) — CCW=32, 1 round/cycle
    // ------------------------------------------------------------------
    logic        crypto_rst;
    logic [31:0] key, bdi, bdo;
    logic        key_valid, key_ready, key_update;
    logic        bdi_valid, bdi_ready;
    logic [3:0]  bdi_type;
    logic [3:0]  bdi_valid_bytes, bdi_pad_loc;
    logic [2:0]  bdi_size;
    logic        bdi_eot, bdi_eoi;
    logic        decrypt_in, hash_in;
    logic        bdo_valid, bdo_ready;
    logic [3:0]  bdo_type;
    logic [7:0]  dbg_fsm;
    logic [3:0]  dbg_cnt;
    logic [7:0]  dbg_widx;
    logic [319:0] dbg_state_raw;

    CryptoCore u_core (
        .clk(clk),
        .rst(crypto_rst),
        .key(key),
        .key_valid(key_valid),
        .key_ready(key_ready),
        .key_update(key_update),
        .bdi(bdi),
        .bdi_valid(bdi_valid),
        .bdi_ready(bdi_ready),
        .bdi_pad_loc(bdi_pad_loc),
        .bdi_valid_bytes(bdi_valid_bytes),
        .bdi_size(bdi_size),
        .bdi_eot(bdi_eot),
        .bdi_eoi(bdi_eoi),
        .bdi_type(bdi_type),
        .decrypt_in(decrypt_in),
        .hash_in(hash_in),
        .bdo(bdo),
        .bdo_valid(bdo_valid),
        .bdo_ready(bdo_ready),
        .bdo_type(bdo_type),
        .bdo_valid_bytes(),
        .end_of_block(),
        .msg_auth_valid(),
        .msg_auth_ready(1'b0),
        .msg_auth(),
        .dbg_state(dbg_state_raw),
        .dbg_fsm(dbg_fsm),
        .dbg_cnt(dbg_cnt),
        .dbg_widx(dbg_widx)
    );

    assign crypto_rst = ~reset_n;
    assign decrypt_in = 1'b0;
    assign hash_in    = 1'b0;

    // ------------------------------------------------------------------
    // Reverse byte order of each lane: dbg_state_raw has byte-reversed
    // lanes (internal core convention).  We un-reverse so state_reg_out
    // matches the canonical Ascon state ordering used by Python labels.
    // ------------------------------------------------------------------
    genvar l;
    generate
        for (l = 0; l < 5; l++) begin : lane_rev
            always_comb begin
                for (int j = 0; j < 8; j++) begin
                    state_reg_out[l*64 + j*8 +: 8] =
                        dbg_state_raw[l*64 + (7-j)*8 +: 8];
                end
            end
        end
    endgenerate

    // ------------------------------------------------------------------
    // Trigger: pulse at round-1 S-box (init permutation, first round)
    // INIT_PROCESS = 4 in state_t enumeration, rcon = dbg_cnt = 12
    // ------------------------------------------------------------------
    logic trigger_r;
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n)
            trigger_r <= 1'b0;
        else if (dbg_fsm == 8'd4 && dbg_cnt == 4'd12)
            trigger_r <= 1'b1;
        else
            trigger_r <= 1'b0;
    end

    // ------------------------------------------------------------------
    // Adapter FSM
    // ------------------------------------------------------------------
    typedef enum logic [4:0] {
        S_IDLE = 5'd0, S_KEY = 5'd1, S_NONCE = 5'd2, S_INIT = 5'd3,
        S_AD = 5'd4, S_AD_RD = 5'd5, S_MSG = 5'd6,
        S_FINAL = 5'd8, S_TAG = 5'd9, S_DONE = 5'd10
    } st_t;
    st_t state;

    logic [1:0] wcnt;   // word counter (0..3)

    // AD/PT blocks are absorbed byte-reversed per 32-bit word (confirmed by
    // instrumenting the reference testbench: bdi word = byte-reverse of the
    // input chunk). The key/nonce are stored raw in ascon_key_s (also
    // confirmed: KEYWORD dumps show raw register slices).
    function automatic [31:0] brev32(input logic [31:0] w);
        return {w[7:0], w[15:8], w[23:16], w[31:24]};
    endfunction

    // Key words: feed RAW LSB-first slices of the register (crypt_key has
    // byte k at [8k+:8]); the core reverse_bytes each input word internally.
    logic [31:0] kw [4];
    assign kw[0] = key1[31:0];
    assign kw[1] = key1[63:32];
    assign kw[2] = key2[31:0];
    assign kw[3] = key2[63:32];

    // Nonce words (same convention)
    logic [31:0] nw [4];
    assign nw[0] = nonce1[31:0];
    assign nw[1] = nonce1[63:32];
    assign nw[2] = nonce2[31:0];
    assign nw[3] = nonce2[63:32];

    // Latched, padded 64-bit AD and PT blocks (2 words each)
    logic [31:0] ad_w [2];
    logic [31:0] pt_w [2];
    logic [31:0] ct_w [2];
    logic [31:0] tag_w [4];
    logic [63:0] ad_blk, pt_blk;
    logic        ad_latched, pt_latched;

    // Word-slice the padded blocks: big-endian word 0 = first 4 bytes
    // (block MSB half), word 1 = bytes 4-7. The core byte-reverses each
    // input word internally.
    always_comb begin
        ad_w[0] = ad_blk[63:32];
        ad_w[1] = ad_blk[31:0];
        pt_w[0] = pt_blk[63:32];
        pt_w[1] = pt_blk[31:0];
    end

    // ------------------------------------------------------------------
    // AD latch: on start, sample data_in. The core adds the 0x80 padding
    // itself (PAD_AD/PAD_MSG + pad_bdi with bdi_pad_loc), so only the raw
    // valid bytes are latched. valid bytes are the TOP valid_bytes bytes of
    // data_in (per wrapper).
    // ------------------------------------------------------------------
    function automatic [63:0] raw_block(input logic [127:0] din,
                                        input logic [4:0]  vbytes);
        logic [63:0] blk;
        integer i;
        begin
            blk = '0;
            // Wrapper presents the first valid byte at din[7:0] (host writes
            // byte k to reg[8k+:8], O_textin = reg). Read the LOW bytes.
            for (i = 0; i < 8; i++) begin
                if (i < vbytes)
                    blk[(7-i)*8 +: 8] = din[i*8 +: 8];
            end
        end
        return blk;
    endfunction

    // ------------------------------------------------------------------
    // Key/BDI drive
    // ------------------------------------------------------------------
    always_comb begin
        key_valid  = 1'b0;
        key_update = 1'b0;
        key        = '0;
        if (state == S_KEY) begin
            key_valid  = 1'b1;
            key_update = 1'b1;
            key        = kw[wcnt];
        end
    end

    always_comb begin
        bdi_valid      = 1'b0;
        bdi_type       = 4'b0000;
        bdi_valid_bytes = 4'b1111;
        bdi_pad_loc    = 4'b0000;
        bdi_size       = 3'b100;
        bdi_eot        = 1'b0;
        bdi_eoi        = 1'b0;
        // AD/PT blocks are 4 bytes (valid_bytes=4): word 0 holds the data
        // (all 4 bytes valid), word 1 is empty with the 0x80 pad at byte 0.
        // The core bit-reverses pad_loc: "1000" -> pad_loc_s "0001".
        if (state == S_AD || (pt_latched && dbg_fsm == 8'd10 &&
            (state == S_AD_RD || state == S_MSG))) begin
            if (wcnt == 0) begin
                bdi_valid_bytes = 4'b1111;
                bdi_pad_loc    = 4'b0000;
            end else begin
                bdi_valid_bytes = 4'b0000;
                bdi_pad_loc    = 4'b1000;
            end
        end
        // Message phase: feed PT when the core is in ABSORB_MSG and the PT
        // block is latched (pt_latched avoids feeding a stale block).
        if (pt_latched && dbg_fsm == 8'd10 &&
            (state == S_AD_RD || state == S_MSG)) begin
            bdi_valid = 1'b1;
            bdi_type  = 4'b0100;  // HDR_PT
            if (wcnt == 1) begin
                bdi_eot = 1'b1;
                bdi_eoi = 1'b1;
            end
        end else begin
            case (state)
            S_NONCE: begin
                bdi_valid = 1'b1;
                bdi_type  = 4'b1101;  // HDR_NPUB
                if (wcnt == 3) bdi_eot = 1'b1;
            end
            S_AD: begin
                bdi_valid = 1'b1;
                bdi_type  = 4'b0001;  // HDR_AD
                if (wcnt == 1) bdi_eot = 1'b1;
            end
            S_MSG: begin
                bdi_valid = 1'b1;
                bdi_type  = 4'b0100;  // HDR_PT
                if (wcnt == 1) begin
                    bdi_eot = 1'b1;
                    bdi_eoi = 1'b1;
                end
            end
            endcase
        end
    end
    always_comb begin
        case (state)
            S_NONCE: bdi = nw[wcnt];
            S_AD:    bdi = ad_w[wcnt];
            S_MSG:   bdi = pt_w[wcnt];
            default: bdi = '0;
        endcase
        if (pt_latched && dbg_fsm == 8'd10 &&
            (state == S_AD_RD || state == S_MSG))
            bdi = pt_w[wcnt];
    end

    // BDO ready: the core needs it asserted during ABSORB_MSG (CT output
    // gates bdi_ready) and EXTRACT_TAG (tag output). Always-on is correct.
    assign bdo_ready = 1'b1;

    // ------------------------------------------------------------------
    // Main FSM
    // ------------------------------------------------------------------
    logic read_data_r, ready_tag_r, done_r, cv_r;
    assign read_data       = read_data_r;
    assign ready_tag       = ready_tag_r;
    assign done            = done_r;
    assign ciphertext_valid = cv_r;
    assign ciphertext = {ct_w[1], ct_w[0]};
    assign tag1 = {tag_w[1], tag_w[0]};
    assign tag2 = {tag_w[3], tag_w[2]};
    assign ready_for_data = 1'b0;  // not polled by the host

    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state <= S_IDLE;
            wcnt  <= '0;
            ad_latched <= 1'b0;
            pt_latched <= 1'b0;
            ad_blk <= '0;
            pt_blk <= '0;
            read_data_r <= 1'b0;
            ready_tag_r <= 1'b0;
            done_r      <= 1'b0;
            cv_r        <= 1'b0;
            for (int i = 0; i < 2; i++) begin
                // ad_w/pt_w are pure combinational (derived from ad_blk/pt_blk,
                // which are reset above) — do NOT reset them here or Vivado
                // keeps the GND driver and drops the real combinational value.
                ct_w[i] <= '0;
            end
            for (int i = 0; i < 4; i++) tag_w[i] <= '0;
        end else begin
            read_data_r <= 1'b0;
            ready_tag_r <= 1'b0;
            done_r      <= 1'b0;
            cv_r        <= 1'b0;

            case (state)
                S_IDLE: begin
                    wcnt <= '0;
                    pt_latched <= 1'b0;
                    if (start) begin
                        // data_in = ad_in during LOAD_DATA/PROCESS_AD
                        ad_blk    <= raw_block(data_in, valid_bytes);
                        ad_latched <= 1'b1;
                        state <= S_KEY;
                    end
                end

                S_KEY: begin
                    if (key_valid && key_ready) begin
                        if (wcnt == 3) begin state <= S_NONCE; wcnt <= '0; end
                        else wcnt <= wcnt + 1;
                    end
                end

                S_NONCE: begin
                    if (bdi_valid && bdi_ready) begin
                        if (wcnt == 3) begin state <= S_INIT; wcnt <= '0; end
                        else wcnt <= wcnt + 1;
                    end
                end

                S_INIT: begin
                    // Wait for core to reach ABSORB_AD (state_t pos = 6)
                    if (dbg_fsm == 8'd6) begin state <= S_AD; wcnt <= '0; end
                end

                S_AD: begin
                    if (bdi_valid && bdi_ready) begin
                        if (wcnt == 1) begin
                            read_data_r <= 1'b1;  // AD absorbed -> wrapper to PROCESS_MSG
                            state <= S_AD_RD;
                        end else wcnt <= wcnt + 1;
                    end
                end

                S_AD_RD: begin
                    // Message phase: first latch the PT block (data_in is now
                    // ptx_in), then on the next cycle feed/capture word 0 via
                    // the combinational gate once pt_latched is set.
                    if (dbg_fsm == 8'd10 && !pt_latched) begin
                        pt_blk    <= raw_block(data_in, valid_bytes);
                        pt_latched <= 1'b1;
                        wcnt      <= 2'd0;
                    end else if (dbg_fsm == 8'd10 && pt_latched &&
                                 bdi_valid && bdi_ready) begin
                        // word 0 fed combinationally, capture CT word 0
                        ct_w[0] <= bdo;
                        state   <= S_MSG;
                        wcnt    <= 2'd1;
                    end
                end

                S_MSG: begin
                    if (bdi_valid && bdi_ready) begin
                        ct_w[wcnt] <= bdo;   // CT during MSG absorption
                        if (wcnt == 1) begin
                            cv_r   <= 1'b1;
                            wcnt   <= '0;
                            state  <= S_FINAL;
                        end else wcnt <= wcnt + 1;
                    end
                end

                S_FINAL: begin
                    // Capture all 4 tag words as the core streams them from
                    // EXTRACT_TAG (widx 0..3, one per cycle, bdo_valid=1).
                    if (dbg_fsm == 8'd16 && bdo_valid && bdo_ready) begin
                        tag_w[wcnt] <= bdo;
                        if (wcnt == 3) begin
                            ready_tag_r <= 1'b1;
                            done_r      <= 1'b1;
                            state <= S_DONE;
                        end else wcnt <= wcnt + 1;
                    end
                end

                S_DONE: begin
                    state <= S_IDLE;
                end
            endcase
        end
    end

`ifdef DEBUG
    assign dbg_fsm_debug = {1'b0, dbg_fsm[3:0]};
    assign dbg_cnt_debug = {28'b0, dbg_cnt};
`endif

endmodule