// ascon_datapath.sv
// Datapath pura: nessuna FSM dentro. Importa i parametri come in ascon_top.
import ascon_params::d;
import ascon_params::PAR;
import ascon_params::WORD_SIZE;
import ascon_params::COL_SIZE;
import ascon_params::STATE_WIDTH;
import ascon_params::SHIFT_PAR_D_PLUS_1;
import ascon_params::NUMBER_BIT_MASK;
import ascon_params::RAND_WIDTH;
import ascon_params::LFSR_WIDTH;

module ascon_datapath (
    input  logic clk,
    input  logic reset_n,
    input  logic reset_n_lfsr,

    // chiavi, nonce, IV
    input  logic [WORD_SIZE-1:0] key1,
    input  logic [WORD_SIZE-1:0] key2,
    input  logic [WORD_SIZE-1:0] nonce1,
    input  logic [WORD_SIZE-1:0] nonce2,
    input  logic [WORD_SIZE-1:0] initialVector,

    // dati
    input  logic [2*WORD_SIZE-1:0] data_in,
    input  logic [$clog2(2*WORD_SIZE/8):0] valid_bytes,

    // *** controlli che PRIMA arrivavano dalla FSM ***
    input  logic extra_padding_ff,
    input  logic shift_en,
    input  logic shift_type,      // 0: PAR, 1: (d+1)*PAR
    input  logic write_en,
    input  logic last_cycle,
    input  logic reg_key1_load,
    input  logic reg_key2_load,
    input  logic sel_mux_linear_diffusion_out_x3,
    input  logic sel_mux_linear_diffusion_out_x4,
    input  logic sel_init_load,
    input  logic sel_masked_round,
    input  logic sel_padding,
    input  logic sel_xor_signal,
    input  logic sel_absorb_data,
    input  logic [3:0] round_counter,
    input  logic unsigned [$clog2(NUMBER_BIT_MASK+1)-1:0] bit_counter,

    // *** uscite datapath ***
    output logic [STATE_WIDTH-1:0] state_reg_out,
    output logic [2*WORD_SIZE-1:0] ciphertext,
    output logic [WORD_SIZE-1:0]   tag1,
    output logic [WORD_SIZE-1:0]   tag2

`ifdef DEBUG
    ,output logic [$clog2(NUMBER_BIT_MASK+1)-1:0] debug_bitcounter,
     output logic [3:0]  debug_roundcounter,
     output logic [4:0]  debug_state,
     output logic [63:0] debug_state_0, debug_state_1, debug_state_2, debug_state_3, debug_state_4,
     output logic [63:0] debug_round_state_0, debug_round_state_1, debug_round_state_2, debug_round_state_3, debug_round_state_4,
     output logic [63:0] debug_sbox_nomasked_0, debug_sbox_nomasked_1, debug_sbox_nomasked_2, debug_sbox_nomasked_3, debug_sbox_nomasked_4,
     output logic [63:0] debug_linear_diffusion_state3, debug_linear_diffusion_state4
`endif
);

    // --------------------------------------------------------------------
    // LFSR sintetizzabile (niente translate_off)
    logic [RAND_WIDTH-1:0] lfsr_out; //output dell'LFSR
    logic [LFSR_WIDTH-1:0] lfsr_state_in;
    logic [LFSR_WIDTH-1:0] lfsr_state_out;
    // synopsys translate_off 
    lfsr lfst_inst (
        .data_in   ({RAND_WIDTH{1'b0}}),
        .state_in  (lfsr_state_in),
        .state_out (lfsr_state_out),
        .data_out  (lfsr_out)
    );
    // synopsys translate_on
    // reset dell'LFSR dedicato (TVLA)
    always_ff @(posedge clk or negedge reset_n_lfsr) begin
        if (!reset_n_lfsr)
            lfsr_state_in <= 31'h1234567;  // seed fisso
        else
            lfsr_state_in <= lfsr_state_out;
    end

    //segnali di randomicità :
    logic [d*COL_SIZE*PAR-1:0] random_masks;        // mask per shareCreator
    logic [(d+1)*d/2-1:0]      random_masks_sbox;   // mask per S-Box DOM
    assign random_masks      = lfsr_out[0+:d*COL_SIZE*PAR];
    assign random_masks_sbox = lfsr_out[d*COL_SIZE*PAR+:((d+1)*d/2)];

    // --------------------------------------------------------------------
    // Registri di stato per share
    logic [STATE_WIDTH-1:0]                  state_reg_in_shares     [d:0];
    logic [SHIFT_PAR_D_PLUS_1*COL_SIZE-1:0]  state_reg_out_shiftdplus1_shares [d:0];
    logic [SHIFT_PAR_D_PLUS_1*COL_SIZE-1:0]  state_reg_in_shiftdplus1_shares  [d:0];
    logic [PAR*COL_SIZE-1:0]                 state_reg_in_shift1_shares[d:0];
    logic [STATE_WIDTH-1:0]                  state_reg_out_shares     [d:0];

    genvar s;
    generate
        for (s = 0; s <= d; s++) begin : gen_state_regs
            // scrive solo lo share 0 (scalabile per qualsiasi d)
            localparam logic write_en_i = (s == 0) ? 1'b1 : 1'b0;

            state_register state_reg_share (
                .clk                (clk),
                .reset_n            (reset_n),
                .write_en           (write_en & write_en_i),
                .shift_en           (shift_en),
                .shift_type         (shift_type),
                .last_cycle         (last_cycle),
                .data_in            (state_reg_in_shares[s]),
                .in_shifted_dplus1  (state_reg_in_shiftdplus1_shares[s]),
                .in_shifted_1bit    (state_reg_in_shift1_shares[s]),
                .out_shifted_dplus1 (state_reg_out_shiftdplus1_shares[s]),
                .data_out           (state_reg_out_shares[s])
            );
        end
    endgenerate

    assign state_reg_out = state_reg_out_shares[0];

    // --------------------------------------------------------------------
    // Registri chiave
    logic [WORD_SIZE-1:0] reg_key1_out, reg_key2_out;

    register key1_reg (
        .clk     (clk),
        .reset_n (reset_n),
        .load    (reg_key1_load),
        .data_in (key1),
        .data_out(reg_key1_out)
    );

    register key2_reg (
        .clk     (clk),
        .reset_n (reset_n),
        .load    (reg_key2_load),
        .data_in (key2),
        .data_out(reg_key2_out)
    );

`ifdef DEBUG
    // sipo_debug: usa gli stessi enable del datapath per non introdurre nuove porte
    wire shift_enable_sipo = shift_en;
    wire last_cycle_sipo   = last_cycle;

    logic [WORD_SIZE-1:0] round_x0_debug, round_x1_debug, round_x2_debug, round_x3_debug, round_x4_debug;

    sipo_debug sipo_reg_x0_debug (
        .clk(clk), .reset_n(reset_n), .shift_en(shift_enable_sipo),
        .in_shifted_dplus1(mux_1st_x0[0+:SHIFT_PAR_D_PLUS_1]),
        .in_shifted_1bit  (mux_1st_x0[0+:PAR]),
        .shift_type(shift_type), .last_cycle(last_cycle_sipo),
        .data_out(round_x0_debug)
    );

    sipo_debug sipo_reg_x1_debug (
        .clk(clk), .reset_n(reset_n), .shift_en(shift_enable_sipo),
        .in_shifted_dplus1(mux_1st_x1[0+:SHIFT_PAR_D_PLUS_1]),
        .in_shifted_1bit  (mux_1st_x1[0+:PAR]),
        .shift_type(shift_type), .last_cycle(last_cycle_sipo),
        .data_out(round_x1_debug)
    );

    sipo_debug sipo_reg_x2_debug (
        .clk(clk), .reset_n(reset_n), .shift_en(shift_enable_sipo),
        .in_shifted_dplus1(mux_1st_x2[0+:SHIFT_PAR_D_PLUS_1]),
        .in_shifted_1bit  (mux_1st_x2[0+:PAR]),
        .shift_type(shift_type), .last_cycle(last_cycle_sipo),
        .data_out(round_x2_debug)
    );

    sipo_debug sipo_reg_x3_debug (
        .clk(clk), .reset_n(reset_n), .shift_en(shift_enable_sipo),
        .in_shifted_dplus1(mux_1st_x3[0+:SHIFT_PAR_D_PLUS_1]),
        .in_shifted_1bit  (mux_1st_x3[0+:PAR]),
        .shift_type(shift_type), .last_cycle(last_cycle_sipo),
        .data_out(round_x3_debug)
    );

    sipo_debug sipo_reg_x4_debug (
        .clk(clk), .reset_n(reset_n), .shift_en(shift_enable_sipo),
        .in_shifted_dplus1(mux_1st_x4[0+:SHIFT_PAR_D_PLUS_1]),
        .in_shifted_1bit  (mux_1st_x4[0+:PAR]),
        .shift_type(shift_type), .last_cycle(last_cycle_sipo),
        .data_out(round_x4_debug)
    );
`endif

    // --------------------------------------------------------------------
    // Input network: split in x0..x4
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x0;
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x1;
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x2;
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x3;
    logic [SHIFT_PAR_D_PLUS_1-1:0] state_reg_out_x4;

    assign state_reg_out_x0 = state_reg_out_shiftdplus1_shares[0][0+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x1 = state_reg_out_shiftdplus1_shares[0][SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x2 = state_reg_out_shiftdplus1_shares[0][2*SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x3 = state_reg_out_shiftdplus1_shares[0][3*SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];
    assign state_reg_out_x4 = state_reg_out_shiftdplus1_shares[0][4*SHIFT_PAR_D_PLUS_1+:SHIFT_PAR_D_PLUS_1];

    // b) RC application
    logic [(d+1)*PAR-1:0] mux_1st_x0, mux_1st_x1, mux_1st_x2, mux_1st_x3, mux_1st_x4;

    // === Round constant handling ===
    logic [63:0] round_constant_full;
    assign round_constant_full = 64'hF0 - (64'h0F * round_counter);

    localparam int RC_PADDED_WIDTH = ((64 + PAR - 1) / PAR) * PAR;
    logic [RC_PADDED_WIDTH-1:0] round_constant_padded;
    assign round_constant_padded = { {(RC_PADDED_WIDTH - 64){1'b0}}, round_constant_full };

    // === RC slice selection per share ===
    logic [PAR-1:0] rc_block[d:0];

    genvar i_input_net;
    generate
        for (i_input_net = 0; i_input_net < d+1; i_input_net++) begin : mux_logic
            localparam int BIT_COUNTER_MAX_FULL = NUMBER_BIT_MASK - 1;
            localparam [$clog2(NUMBER_BIT_MASK+1)-1:0] BIT_COUNTER_MAX =
                BIT_COUNTER_MAX_FULL[$clog2(NUMBER_BIT_MASK+1)-1:0];

            always_comb begin
                logic [PAR-1:0] rc_block_temp;
                if (bit_counter < BIT_COUNTER_MAX) begin
                    if (sel_masked_round) begin
                        rc_block_temp = round_constant_padded[(bit_counter * PAR) +: PAR];
                    end else begin
                        rc_block_temp = round_constant_padded[(((d+1) * bit_counter * PAR) + (i_input_net * PAR)) +: PAR];
                    end
                end else begin
                    rc_block_temp = '0;
                end
                rc_block[i_input_net] = rc_block_temp;
            end

            if (PAR*(d+1) <= 64) begin : gen_normal
                assign mux_1st_x0[i_input_net*PAR+:PAR] = state_reg_out_x0[i_input_net*PAR+:PAR];
                assign mux_1st_x1[i_input_net*PAR+:PAR] = state_reg_out_x1[i_input_net*PAR+:PAR];
                assign mux_1st_x2[i_input_net*PAR+:PAR] = state_reg_out_x2[i_input_net*PAR+:PAR] ^ rc_block[i_input_net];
                assign mux_1st_x3[i_input_net*PAR+:PAR] = state_reg_out_x3[i_input_net*PAR+:PAR];
                assign mux_1st_x4[i_input_net*PAR+:PAR] = state_reg_out_x4[i_input_net*PAR+:PAR];
            end else begin : gen_padded
                if (i_input_net < d) begin : gen_body
                    assign mux_1st_x0[i_input_net*PAR+:PAR] = state_reg_out_x0[i_input_net*PAR+:PAR];
                    assign mux_1st_x1[i_input_net*PAR+:PAR] = state_reg_out_x1[i_input_net*PAR+:PAR];
                    assign mux_1st_x2[i_input_net*PAR+:PAR] = state_reg_out_x2[i_input_net*PAR+:PAR] ^ rc_block[i_input_net];
                    assign mux_1st_x3[i_input_net*PAR+:PAR] = state_reg_out_x3[i_input_net*PAR+:PAR];
                    assign mux_1st_x4[i_input_net*PAR+:PAR] = state_reg_out_x4[i_input_net*PAR+:PAR];
                end else begin : gen_last
                    localparam int LAST_PAR_USED = 64 - (d * PAR);
                    assign mux_1st_x0[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x0[i_input_net*PAR+:LAST_PAR_USED] };
                    assign mux_1st_x1[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x1[i_input_net*PAR+:LAST_PAR_USED] };
                    assign mux_1st_x2[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x2[i_input_net*PAR+:LAST_PAR_USED] } ^ rc_block[i_input_net];
                    assign mux_1st_x3[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x3[i_input_net*PAR+:LAST_PAR_USED] };
                    assign mux_1st_x4[i_input_net*PAR+:PAR] = { {(PAR - LAST_PAR_USED){1'b0}}, state_reg_out_x4[i_input_net*PAR+:LAST_PAR_USED] };
                end
            end
        end
    endgenerate

    // === Creazione delle shares ===
    logic [(d+1)*PAR*COL_SIZE-1:0] shares_out;
    logic [PAR*COL_SIZE-1:0]       shares_in;

    assign shares_in = {mux_1st_x4[0+:PAR], mux_1st_x3[0+:PAR], mux_1st_x2[0+:PAR], mux_1st_x1[0+:PAR], mux_1st_x0[0+:PAR]};

    shareCreator share_creator(
        .data_in     (shares_in),
        .random_masks(random_masks),
        .shares_out  (shares_out)
    );

    // mux ingresso S-Box (shares vs colonne)
    logic [PAR*COL_SIZE-1:0] affine_layer_in [d:0];

    genvar i_affine;
    generate
        for (i_affine = 0; i_affine < d+1; i_affine++) begin : gen_affine_assign
            assign affine_layer_in[i_affine] = (sel_masked_round)
              ? shares_out[i_affine*PAR*COL_SIZE +: PAR*COL_SIZE]
              : {mux_1st_x4[i_affine*PAR+:PAR], mux_1st_x3[i_affine*PAR+:PAR], mux_1st_x2[i_affine*PAR+:PAR],
                 mux_1st_x1[i_affine*PAR+:PAR], mux_1st_x0[i_affine*PAR+:PAR]};
        end
    endgenerate

    // === First affine layer ===
    logic [PAR*COL_SIZE-1:0] affine_layer_out [d:0];

    genvar i_affine_out;
    generate
        for (i_affine_out = 0; i_affine_out< d+1; i_affine_out++) begin : affine_layer_1st
            assign affine_layer_out[i_affine_out] = {
                affine_layer_in[i_affine_out][4*PAR+:PAR] ^ affine_layer_in[i_affine_out][3*PAR+:PAR],
                affine_layer_in[i_affine_out][3*PAR+:PAR],
                affine_layer_in[i_affine_out][2*PAR+:PAR] ^ affine_layer_in[i_affine_out][PAR+:PAR],
                affine_layer_in[i_affine_out][PAR+:PAR],
                affine_layer_in[i_affine_out][0+:PAR] ^ affine_layer_in[i_affine_out][4*PAR+:PAR]
            };
        end
    endgenerate

    // === Preparazione input S-Box ===
    logic [(d+1)*COL_SIZE-1:0] next_sbox_input [PAR-1:0];
    genvar i_sbox, p_sbox;
    generate
        for (p_sbox=0; p_sbox < PAR; p_sbox++) begin : sbox_input_gen
            for (i_sbox=0; i_sbox < d+1; i_sbox++) begin
                assign next_sbox_input[p_sbox][i_sbox]                  = affine_layer_out[i_sbox][p_sbox];
                assign next_sbox_input[p_sbox][(d+1)+i_sbox]            = affine_layer_out[i_sbox][PAR+p_sbox];
                assign next_sbox_input[p_sbox][2*(d+1)+i_sbox]          = affine_layer_out[i_sbox][2*PAR+p_sbox];
                assign next_sbox_input[p_sbox][3*(d+1)+i_sbox]          = affine_layer_out[i_sbox][3*PAR+p_sbox];
                assign next_sbox_input[p_sbox][4*(d+1)+i_sbox]          = affine_layer_out[i_sbox][4*PAR+p_sbox];
            end
        end
    endgenerate

    logic [(d+1)*COL_SIZE-1:0] sbox_input[PAR-1:0];
    logic [(d+1)*COL_SIZE-1:0] sbox_output[PAR-1:0];
    logic [(d+1)*COL_SIZE-1:0] sbox_output_unmasked[PAR-1:0];

    always_ff @(posedge clk) begin
        for (int p = 0; p < PAR; p++) begin
            sbox_input[p] <= next_sbox_input[p];
        end
    end

    // === S-Box ===
    genvar p;
    generate
        if (d == 2) begin : gen_cog
            for (p = 0; p < PAR; p++) begin : gen_sbox
                logic [(d+1)*d/2-1:0] fresh_r;
                assign fresh_r = { state_reg_out[(35+p)%64], state_reg_out[(37+p)%64], state_reg_out[(11+p)%64]  };
                ascon_sbox_d2 u_sbox (
                    .clk(clk), .x_in(sbox_input[p]), .fresh_r(fresh_r),
                    .sel_masked_round(sel_masked_round),
                    .x_out(sbox_output[p]),
                    .x_out_noMask(sbox_output_unmasked[p])
                );
            end
        end else if (d == 1) begin : gen_no_cog
            for (p = 0; p < PAR; p++) begin : gen_sbox
                logic [(d+1)*d/2-1:0] fresh_r;
                assign fresh_r = state_reg_out[(11+p)%64];
                ascon_sbox_d2 u_sbox (
                    .clk(clk), .x_in(sbox_input[p]), .fresh_r(fresh_r),
                    .sel_masked_round(sel_masked_round),
                    .x_out(sbox_output[p]),
                    .x_out_noMask(sbox_output_unmasked[p])
                );
            end
        end else begin : gen_no_changing
            for (p = 0; p < PAR; p++) begin : gen_sbox
                logic [(d+1)*d/2-1:0] fresh_r;
                assign fresh_r = random_masks_sbox;
                ascon_sbox_d2 u_sbox (
                    .clk(clk), .x_in(sbox_input[p]), .fresh_r(fresh_r),
                    .sel_masked_round(sel_masked_round),
                    .x_out(sbox_output[p]),
                    .x_out_noMask(sbox_output_unmasked[p])
                );
            end
        end
    endgenerate

    // mux selezione fra output mascherato e non mascherato (per-elemento)
    logic [(d+1)*COL_SIZE-1:0] mux_sbox_out [PAR-1:0];
    generate
        for (genvar pp=0; pp<PAR; pp++) begin
            assign mux_sbox_out[pp] = sel_masked_round ? sbox_output[pp] : sbox_output_unmasked[pp];
        end
    endgenerate

    // === Secondo affine: ricomponi per dominio ===
    logic [PAR*COL_SIZE-1:0] affine_layer2nd_in [d:0];
    genvar i_2ndAffine, p_2ndAffine;
    generate
        for (i_2ndAffine = 0; i_2ndAffine < d+1; i_2ndAffine++) begin : gen_affine2nd
            for (p_2ndAffine = 0; p_2ndAffine < PAR; p_2ndAffine++) begin : gen_bit
                assign affine_layer2nd_in[i_2ndAffine][p_2ndAffine]           = mux_sbox_out[p_2ndAffine][i_2ndAffine];
                assign affine_layer2nd_in[i_2ndAffine][PAR + p_2ndAffine]     = mux_sbox_out[p_2ndAffine][(d+1) + i_2ndAffine];
                assign affine_layer2nd_in[i_2ndAffine][2*PAR + p_2ndAffine]   = mux_sbox_out[p_2ndAffine][2*(d+1) + i_2ndAffine];
                assign affine_layer2nd_in[i_2ndAffine][3*PAR + p_2ndAffine]   = mux_sbox_out[p_2ndAffine][3*(d+1) + i_2ndAffine];
                assign affine_layer2nd_in[i_2ndAffine][4*PAR + p_2ndAffine]   = mux_sbox_out[p_2ndAffine][4*(d+1) + i_2ndAffine];
            end
        end
    endgenerate

    // == Second affine layer ==
    logic [PAR*COL_SIZE-1:0] affine_layer2nd_out[d:0];
    genvar i_2ndAff_out;
    generate
        for (i_2ndAff_out = 0; i_2ndAff_out < d+1; i_2ndAff_out++) begin : affine_layer
            logic [PAR-1:0] affine_layer2nd_in_temp;
            always_comb begin
                if ((d % 2) == 1 && i_2ndAff_out > 0 && sel_masked_round == 1)
                    affine_layer2nd_in_temp = affine_layer2nd_in[i_2ndAff_out][2*PAR+:PAR];
                else
                    affine_layer2nd_in_temp = ~affine_layer2nd_in[i_2ndAff_out][2*PAR+:PAR];
            end

            assign affine_layer2nd_out[i_2ndAff_out] = {
                affine_layer2nd_in[i_2ndAff_out][4*PAR+:PAR],
                affine_layer2nd_in[i_2ndAff_out][3*PAR+:PAR] ^ affine_layer2nd_in[i_2ndAff_out][2*PAR+:PAR],
                affine_layer2nd_in_temp,
                affine_layer2nd_in[i_2ndAff_out][PAR+:PAR] ^ affine_layer2nd_in[i_2ndAff_out][0+:PAR],
                affine_layer2nd_in[i_2ndAff_out][0+:PAR] ^ affine_layer2nd_in[i_2ndAff_out][4*PAR+:PAR]
            };
        end
    endgenerate

`ifdef DEBUG
    // Ricombinazione shares per debug S-Box
    logic [STATE_WIDTH-1:0] recombine_shares_sbox;
    generate
        for (genvar bit_idx_sbox = 0; bit_idx_sbox < STATE_WIDTH; bit_idx_sbox++) begin : recombine_sbox_dbg
            logic [d:0] temp_bits_sbox;
            always_comb begin
                for (int st_reg_sbox = 0; st_reg_sbox <= d; st_reg_sbox++) begin
                    temp_bits_sbox[st_reg_sbox] = state_reg_out_shares[st_reg_sbox][bit_idx_sbox];
                end
                recombine_shares_sbox[bit_idx_sbox] = xor_tree(temp_bits_sbox, d+1);
            end
        end
    endgenerate
`endif

    // Ingresso seriale masked per tutti gli share
    always_comb begin
        for (int st = 0; st <= d; st++) begin
            state_reg_in_shift1_shares[st] = affine_layer2nd_out[st];
        end
    end

    // Ingresso non mascherato nello share 0
    generate
        if ((PAR * (d + 1)) <= 64) begin : gen_normal_pack
            for (genvar idx = 0; idx < COL_SIZE; idx++) begin : pack_affine
                for (genvar d_idx = 0; d_idx < d+1; d_idx++) begin : pack_affine_int
                    assign state_reg_in_shiftdplus1_shares[0][idx*PAR*(d+1)+PAR*d_idx +: PAR] =
                        affine_layer2nd_out[d_idx][idx*PAR +: PAR];
                end
            end
        end else begin : gen_truncate
            for (genvar idx = 0; idx < COL_SIZE; idx++) begin : pack_affine_trunc
                for (genvar d_idx = 0; d_idx < d+1; d_idx++) begin : pack_affine_trunc_int
                    if (PAR * d_idx < 64) begin : active_bits
                        localparam int USED_BITS = ((PAR * (d_idx + 1)) <= 64) ? PAR : (64 - PAR * d_idx);
                        assign state_reg_in_shiftdplus1_shares[0][idx*64 + PAR*d_idx +: USED_BITS] =
                            affine_layer2nd_out[d_idx][idx*PAR +: USED_BITS];
                    end
                end
            end
        end
    endgenerate

    // --------------------------------------------------------------------
    // Assorbimento / init / round mux
    logic [WORD_SIZE-1:0] state_reg_in_absorb[4:0];
    logic [STATE_WIDTH-1:0] init_data;
    logic [STATE_WIDTH-1:0] linear_diffusion_out;

    // padding
    logic [2*WORD_SIZE-1:0] data_in_padded;
    always_comb begin
        if (extra_padding_ff) begin
            data_in_padded = '0;
            data_in_padded = {8'h01, {(2*WORD_SIZE-8){1'b0}}};
        end
        else if (sel_padding) begin
            data_in_padded = '0;
            for (int unsigned i = 0; i < 16; i++) begin
                if (i < valid_bytes)
                    data_in_padded[127 - i*8 -: 8] = data_in[127 - i*8 -: 8];
            end
            data_in_padded[(127 - valid_bytes*8) -: 8] = 8'h01;
        end else begin
            data_in_padded = data_in;
        end
    end

    logic [2*WORD_SIZE-1:0] reverse_reg_data_out;

    function automatic logic [2*WORD_SIZE-1:0] reverse_bytes(input logic [2*WORD_SIZE-1:0] x);
        logic [2*WORD_SIZE-1:0] y;
        for (int i = 0; i < 8; i++) begin
            y[i*8 +: 8]              = x[(7-i)*8 +: 8];
            y[i*8 + WORD_SIZE +: 8]  = x[(7-i)*8 + WORD_SIZE +: 8];
        end
        return y;
    endfunction

    assign reverse_reg_data_out = (sel_padding) ? reverse_bytes(data_in_padded) : reverse_bytes(data_in);

    assign state_reg_in_absorb[0] = state_reg_out[0*WORD_SIZE +: WORD_SIZE] ^ reverse_reg_data_out[WORD_SIZE+:WORD_SIZE];
    assign state_reg_in_absorb[1] = state_reg_out[1*WORD_SIZE +: WORD_SIZE] ^ reverse_reg_data_out[0+:WORD_SIZE];
    assign state_reg_in_absorb[2] = state_reg_out[2*WORD_SIZE +: WORD_SIZE];
    assign state_reg_in_absorb[3] = state_reg_out[3*WORD_SIZE +: WORD_SIZE];
    assign state_reg_in_absorb[4] = state_reg_out[4*WORD_SIZE +: WORD_SIZE];

    assign init_data = { nonce2, nonce1, key2, key1, initialVector };

    assign ciphertext = {state_reg_in_absorb[1], state_reg_in_absorb[0]};

    logic [STATE_WIDTH-1:0] input_state;

    always_comb begin
        unique case ({sel_absorb_data, sel_init_load})
            2'b10: state_reg_in_shares[0] = {state_reg_in_absorb[4], state_reg_in_absorb[3], state_reg_in_absorb[2], state_reg_in_absorb[1], state_reg_in_absorb[0]};
            2'b01: state_reg_in_shares[0] = init_data;
            2'b00: state_reg_in_shares[0] = input_state;
            2'b11: state_reg_in_shares[0] = {state_reg_in_absorb[4], state_reg_in_absorb[3] ^ reg_key2_out, state_reg_in_absorb[2] ^ reg_key1_out, state_reg_in_absorb[1], state_reg_in_absorb[0]};
        endcase
    end

    // === Linear diffusion layer ===
    localparam int rotations_a[0:4] = '{19, 61, 1, 10, 7};
    localparam int rotations_b[0:4] = '{28, 39, 6, 17, 41};

    function automatic logic [63:0] rotr64(input logic [63:0] x, input int n);
        return (x >> n) | (x << (64 - n));
    endfunction

    logic [63:0] linear_diffusion_debug [0:4];

    // ricombinazione shares per L
    logic [STATE_WIDTH-1:0] recombine_shares;

    function automatic logic xor_tree (
        input logic [d:0] in,
        input int N
    );
        localparam int MAX_STAGE = $clog2(d+1) + 1;
        logic [(d+1)-1:0] stage [0:MAX_STAGE-1];
        int level = 0;
        int num = N;
        for (int i = 0; i < N; i++) stage[0][i] = in[i];
        while (num > 1) begin
            for (int i = 0; i < num / 2; i++) begin
                stage[level + 1][i] = stage[level][2*i] ^ stage[level][2*i + 1];
            end
            if (num % 2 == 1) begin
                stage[level + 1][num / 2] = stage[level][num - 1];
                num = num / 2 + 1;
            end else begin
                num = num / 2;
            end
            level++;
        end
        return stage[level][0];
    endfunction

    generate
        for (genvar bit_idx = 0; bit_idx < STATE_WIDTH; bit_idx++) begin : recombine
            logic [d:0] temp_bits;
            always_comb begin
                for (int st_reg = 0; st_reg <= d; st_reg++) begin
                    temp_bits[st_reg] = state_reg_out_shares[st_reg][bit_idx];
                end
                recombine_shares[bit_idx] = xor_tree(temp_bits, d+1);
            end
        end
    endgenerate

    generate
        for (genvar i = 0; i < 5; i++) begin : linear_diffusion_layer
            assign linear_diffusion_debug[i] = (sel_masked_round)
                ? (recombine_shares[i*64 +: 64]
                    ^ rotr64(recombine_shares[i*64 +: 64], rotations_a[i])
                    ^ rotr64(recombine_shares[i*64 +: 64], rotations_b[i]))
                : (state_reg_out[i*64 +: 64]
                    ^ rotr64(state_reg_out[i*64 +: 64], rotations_a[i])
                    ^ rotr64(state_reg_out[i*64 +: 64], rotations_b[i]));

            assign linear_diffusion_out[i*64 +: 64] = linear_diffusion_debug[i];
        end
    endgenerate

    // XOR con chiavi/signal
    logic [WORD_SIZE-1:0] mux_linear_diffusion_out_x4;
    logic [WORD_SIZE-1:0] mux_linear_diffusion_out_x3;
    logic [63:0]          xor_signal;

    assign xor_signal = (sel_xor_signal) ? reg_key2_out : {1'b1, {(WORD_SIZE-1){1'b0}}};

    assign mux_linear_diffusion_out_x4 = (sel_mux_linear_diffusion_out_x4)
                                        ? (linear_diffusion_debug[4] ^ xor_signal)
                                        :  linear_diffusion_debug[4];

    assign mux_linear_diffusion_out_x3 = (sel_mux_linear_diffusion_out_x3)
                                        ? (linear_diffusion_debug[3] ^ reg_key1_out)
                                        :  linear_diffusion_debug[3];

    assign input_state = {
        mux_linear_diffusion_out_x4,
        mux_linear_diffusion_out_x3,
        linear_diffusion_out[2*WORD_SIZE +: WORD_SIZE],
        linear_diffusion_out[1*WORD_SIZE +: WORD_SIZE],
        linear_diffusion_out[0*WORD_SIZE +: WORD_SIZE]
    };

    // Tag
    assign tag1 = linear_diffusion_out[3*WORD_SIZE+:WORD_SIZE] ^ reg_key1_out;
    assign tag2 = linear_diffusion_out[4*WORD_SIZE+:WORD_SIZE] ^ reg_key2_out;

`ifdef DEBUG
    // Uscite DEBUG assegnate (evita SYNOPSYS_UNCONNECTED)
    assign debug_bitcounter   = bit_counter;
    assign debug_roundcounter = round_counter;
    assign debug_state        = '0;

    assign debug_state_0 = state_reg_out[0*64 +: 64];
    assign debug_state_1 = state_reg_out[1*64 +: 64];
    assign debug_state_2 = state_reg_out[2*64 +: 64];
    assign debug_state_3 = state_reg_out[3*64 +: 64];
    assign debug_state_4 = state_reg_out[4*64 +: 64];

    assign debug_round_state_0 = round_x0_debug;
    assign debug_round_state_1 = round_x1_debug;
    assign debug_round_state_2 = round_x2_debug;
    assign debug_round_state_3 = round_x3_debug;
    assign debug_round_state_4 = round_x4_debug;

    assign debug_linear_diffusion_state3 = linear_diffusion_debug[3];
    assign debug_linear_diffusion_state4 = linear_diffusion_debug[4];

    assign debug_sbox_nomasked_0 = recombine_shares_sbox[0*64 +: 64];
    assign debug_sbox_nomasked_1 = recombine_shares_sbox[1*64 +: 64];
    assign debug_sbox_nomasked_2 = recombine_shares_sbox[2*64 +: 64];
    assign debug_sbox_nomasked_3 = recombine_shares_sbox[3*64 +: 64];
    assign debug_sbox_nomasked_4 = recombine_shares_sbox[4*64 +: 64];
`endif

endmodule
