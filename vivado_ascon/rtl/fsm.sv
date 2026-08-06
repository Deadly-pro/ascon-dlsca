// ============================================================================
// FSM Controller for ASCON-SCA Cipher Core
// ----------------------------------------------------------------------------
// This is a Mealy-type FSM controller responsible for sequencing the ASCON
// encryption algorithm operations. Outputs depend both on the state and input
// signals, allowing faster transitions and control reactivity.
//
// Key features:
// - Manages all ASCON processing stages: initialization, absorb (AD and MSG),
//   diffusion, padding, and finalization.
// - Handles conditional paths for masked/unmasked permutation rounds.
// - Supports data-dependent control: padding, last block handling, and EOT.
//
// Author: [Nico]
// ============================================================================
import ascon_params::d;
import ascon_params::WORD_SIZE;
import ascon_params::PAR;
import ascon_params::NUMBER_BIT_MASK; 
import ascon_params::NUMBER_BIT_NOMASK;

module fsm (
    input  logic clk,
    input  logic reset_n,
    input  logic start,

    input logic load_data,
    input logic valid_data_in,
    input logic last_block,
    input logic [$clog2(2*WORD_SIZE/8):0] valid_bytes,
    input logic EOT,

    output logic done, //se il processo è finito
    output logic tag_valid,
    output logic shift_en,
    output logic write_en,
    output logic shift_type,
    output logic last_cycle,

    output logic reg_key1_load,
    output logic reg_key2_load,

    output logic sel_mux_linear_diffusion_out_x3,
    output logic sel_mux_linear_diffusion_out_x4,
    output logic sel_init_load,  // a 1 se devo fare il load di inizializzazione
    output logic sel_masked_round, // a 1 se devo fare una permutazione mascherata
    output logic sel_padding, // a 1 se devo fare l'absorb di dati padded
    output logic sel_xor_signal,
    output logic sel_absorb_data,

    output logic ciphertext_valid,
    output logic ready_for_data,
    output logic read_data,
    output logic extra_padding_ff,

    output logic [$clog2(NUMBER_BIT_MASK+1)-1:0] bit_counter, //conta il numero di blocchi di bit processati 
    output logic [3:0] round_counter //conta i round da 0 a 12

    `ifdef DEBUG
        , 
        output logic [4:0]  debug_state,
        output logic shift_enable_sipo,
        output logic last_cycle_sipo 
    `endif
);

`ifdef DEBUG
    assign debug_state = current_state;
`endif

logic rst_cnt_4; // Reset round counter to 4
logic extra_padding; // Extra padding applied

typedef enum logic [4:0] {
    IDLE, //0
    INIT_LOAD, //01
    INIT_ROUND_SHIFT, //02
    INIT_ROUND_SHIFT_LAST, //03
    INIT_ROUND_DIFFUSE, //04
    INIT_ROUND_DIFFUSE_LAST, //05
    //PADDING_AD_DATA, //06
    //PADDING_EXTRA_AD_DATA,  //07
    ABSORB_AD_DATA, //06
    PROCESS_AD_SHIFT,//07 
    PROCESS_AD_SHIFT_LAST, //08 
    PROCESS_AD_DIFFUSE, //09
    PROCESS_AD_DIFFUSE_LAST, //0A
    //PADDING_MSG_DATA, //0B
    //PADDING_EXTRA_MSG_DATA, //0C 
    ABSORB_MSG_DATA, //0B
    PROCESS_MSG_SHIFT, //0C
    PROCESS_MSG_SHIFT_LAST, //0D
    PROCESS_MSG_DIFFUSE, //0E
    PROCESS_MSG_DIFFUSE_LAST, //0F
    FINALIZATION_SHIFT, //10
    FINALIZATION_SHIFT_LAST, //11
    FINALIZATION_DIFFUSE, //12
    SQUEEZE_TAG,
    DONE
} state_t;

/*(* mark_debug = "true" *)*/ state_t current_state;
state_t next_state;


logic [$clog2(NUMBER_BIT_MASK+1)-1:0] number_bits;
logic [3:0] number_round;

logic last_block_process, last_block_process_ff, last_block_process_load;
logic extra_padding_load;
logic round_counter_enable, rst_counter_round;

//Rete sequenziale per aggiornamento dello stato e contatori
always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        current_state <= IDLE;
        round_counter <= 0;
        bit_counter <= 0;
        last_block_process_ff <= 0;
        extra_padding_ff <= 0;
    end else begin
        current_state <= next_state;

        if (shift_en) begin
            if (bit_counter == number_bits) // Would need -1 without pipeline stages, but have two FF stages
                bit_counter <= 0;
            else
                bit_counter <= bit_counter + 1;
        end

        if (rst_counter_round == 1) begin
            round_counter <= 0;
        end else if (round_counter_enable) begin
            if (round_counter == number_round - 1) begin
                if (rst_cnt_4 == 1)
                    round_counter <= 4; // Unmasked permutations require 8 rounds (4 to 11)
                else
                    round_counter <= 0; // Masked permutations require 12 rounds (0 to 11)
            end else begin
                round_counter <= round_counter + 1;
            end
        end
        if (extra_padding_load == 1) begin
            extra_padding_ff <= extra_padding;
        end
        if (last_block_process_load == 1) begin
            last_block_process_ff <= last_block_process;
        end
    end
end

// Combinatorial state transition logic:
always_comb begin
    next_state = current_state; // default

    case (current_state)
        IDLE: begin
            if (load_data) begin
                next_state = INIT_LOAD;
            end
        end

        INIT_LOAD: begin
            if (start) next_state = INIT_ROUND_SHIFT;
        end

        INIT_ROUND_SHIFT: begin
            // Number of shifts - 1: For PAR = 1, perform 66 shifts (64 to process data + 2 FF stages)
            // PAR = 1, BIT_COUNTER_MAX = 64 (then one more shift in next stage, reaching 66)
            localparam int BIT_COUNTER_MAX_FULL = (64 + PAR - 1) / PAR; 
            localparam [$clog2(NUMBER_BIT_MASK+1)-1:0]  BIT_COUNTER_MAX = BIT_COUNTER_MAX_FULL[$clog2(NUMBER_BIT_MASK+1)-1:0];
            if (bit_counter == BIT_COUNTER_MAX)
                next_state = INIT_ROUND_SHIFT_LAST;
        end

        INIT_ROUND_SHIFT_LAST: begin
            if (round_counter == number_round - 1) next_state = INIT_ROUND_DIFFUSE_LAST;
            else next_state = INIT_ROUND_DIFFUSE;
        end

        INIT_ROUND_DIFFUSE: begin
            next_state = INIT_ROUND_SHIFT;
        end

        INIT_ROUND_DIFFUSE_LAST: begin
            next_state = ABSORB_AD_DATA;
        end

        ABSORB_AD_DATA: begin
            if (valid_data_in || extra_padding_ff == 1) begin
                next_state = PROCESS_AD_SHIFT;
            end
        end

        PROCESS_AD_SHIFT: begin
            if (bit_counter == NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] - 1)
                next_state = PROCESS_AD_SHIFT_LAST;
        end

        PROCESS_AD_SHIFT_LAST: begin
            if ((round_counter == number_round - 1)) next_state = PROCESS_AD_DIFFUSE_LAST;
            else next_state = PROCESS_AD_DIFFUSE;
        end

        PROCESS_AD_DIFFUSE: begin
            next_state = PROCESS_AD_SHIFT;
        end

        PROCESS_AD_DIFFUSE_LAST: begin
            if (last_block_process_ff == 1 && extra_padding_ff == 0) begin   // Indicates if last AD block already processed
                next_state = ABSORB_MSG_DATA;
            end else begin // Already processed all AD and EXTRA PADDING
                next_state = ABSORB_AD_DATA;      // More blocks to process
            end
        end

        ABSORB_MSG_DATA: begin
            if (valid_data_in == 1) begin // If valid data present
                next_state = PROCESS_MSG_SHIFT;
                if (EOT && !extra_padding) begin
                    next_state = FINALIZATION_SHIFT;
                end
            end else begin
                if (last_block_process_ff == 1 && extra_padding == 0) begin
                    next_state = FINALIZATION_SHIFT;
                end
            end
        end


        PROCESS_MSG_SHIFT: begin
            if (bit_counter == NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] - 1)
                next_state = PROCESS_MSG_SHIFT_LAST;
        end

        PROCESS_MSG_SHIFT_LAST: begin
            if (round_counter == number_round - 1)
                next_state = PROCESS_MSG_DIFFUSE_LAST;
            else next_state = PROCESS_MSG_DIFFUSE;
        end

        PROCESS_MSG_DIFFUSE: begin
            next_state = PROCESS_MSG_SHIFT;
        end

        PROCESS_MSG_DIFFUSE_LAST: begin
            next_state = ABSORB_MSG_DATA;
        end

        FINALIZATION_SHIFT: begin
            localparam int BIT_COUNTER_MAX_FULL = (64 + PAR - 1) / PAR;
            localparam [$clog2(NUMBER_BIT_MASK+1)-1:0]  BIT_COUNTER_MAX = BIT_COUNTER_MAX_FULL[$clog2(NUMBER_BIT_MASK+1)-1:0] ;
            if (bit_counter == BIT_COUNTER_MAX)
                next_state = FINALIZATION_SHIFT_LAST;
        end

        FINALIZATION_SHIFT_LAST: begin
            next_state = FINALIZATION_DIFFUSE;
        end

        FINALIZATION_DIFFUSE: begin
            if (round_counter == number_round - 1)
                next_state = SQUEEZE_TAG;
            else
                next_state = FINALIZATION_SHIFT;
        end

        SQUEEZE_TAG: begin
            next_state = DONE;
        end

        DONE: begin
            if (!start)
                next_state = IDLE;
        end

        default: next_state = IDLE;
    endcase
end

localparam int BYTE_W = 2*WORD_SIZE / 8;

// Combinatorial output calculation logic
always_comb begin
    ciphertext_valid = 0;       // 1 when ciphertext is valid
    tag_valid = 0;
    done = 0;               
    ready_for_data = 0;         // 1 when DUT is ready to receive new data
    round_counter_enable = 0;   // 1 when round complete (RC, S-BOX, LDL)

    // State transition control signals:
    extra_padding = 0;          // 1 if extra padding needed, last block + 16 valid bytes
    extra_padding_load = 0;     // 1 to sample corresponding signal

    // State register signals:
    write_en = 0;
    shift_en = 0;
    shift_type = 0;             // 0 -> shift PAR*(d+1) bits; 1 -> shift PAR bits
    last_cycle = 0;             // Final cycle flag (possible reduced shift per PAR, d+1)

    // MUX selectors:
    sel_init_load = 0;
    sel_mux_linear_diffusion_out_x3 = 0;
    sel_mux_linear_diffusion_out_x4 = 0;
    sel_masked_round = 1;
    rst_cnt_4 = 0; // Reset round counter to 4; otherwise 0
    sel_padding = 0;            // 1 if padding done; saved to FF; next ABSORB reads from register not interface
    sel_xor_signal = 0;         // 0: XOR with 0; 1: XOR with key1, key2
    sel_absorb_data = 0;        // 1 to load state^(AD or MSG) into state register
    
    // Key register loads:
    reg_key1_load = 0;
    reg_key2_load = 0;
    read_data = 0;
    // Signal to read from external interface

    number_round = 12;          // Could be parameter, but kept as local for now
    number_bits = 0;
    rst_counter_round = 0;

    last_block_process = 0;     // 1 when last block processed; for last block + extra padding handling
    last_block_process_load = 0;

    `ifdef DEBUG
        shift_enable_sipo = 0;   // Enable shifts for DEBUG registers
        last_cycle_sipo = 0;     // 1 during final shift cycle
    `endif

    case (current_state)
        IDLE: begin
            // niente
        end

        INIT_LOAD: begin
                // Load IV, nonce, and key:
                // Key register enables
                reg_key1_load = 1;  
                reg_key2_load = 1;  

                sel_init_load = 1; // Load init data into state_reg
                write_en = 1;  // Enable state_reg parallel load
        end

        INIT_ROUND_SHIFT: begin
            number_bits = NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ;  // Bits to process

            shift_en = 1; // Enable state_reg shift
            shift_type = 1; // PAR-bit shift
            
            `ifdef DEBUG
                shift_enable_sipo = 1;  // Enable DEBUG register shifts
                if (bit_counter == (NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0] - 2)) begin
                    last_cycle_sipo = 1; // Final cycle when shift count equals bit blocks
                                         // Note: 2 more shifts needed for state_reg completion (2 FF stages)
                end
            `endif
        end

        INIT_ROUND_SHIFT_LAST: begin
            number_bits = NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ;
            last_cycle = 1;  // Final shift cycle
            shift_en = 1;  
            `ifdef DEBUG
                shift_enable_sipo = 1;  // Enable SIPO shift
            `endif
            shift_type = 1; // PAR-bit shift
        end

        INIT_ROUND_DIFFUSE: begin
            number_bits = NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ;
            write_en = 1;
            round_counter_enable = 1;  // Permutation round complete
        end

        INIT_ROUND_DIFFUSE_LAST: begin
            round_counter_enable = 1; // Another permutation round complete
            // MUX selects S ^ (0*|Key1|Key2):
            sel_mux_linear_diffusion_out_x3 = 1; 
            sel_mux_linear_diffusion_out_x4 = 1;
            
            sel_xor_signal = 1; // Select XOR between x3 and key2
            write_en = 1; // Enable parallel load to state_reg
            number_bits = NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0];
            rst_cnt_4 = 1;
        end

        ABSORB_AD_DATA: begin
            number_bits =  NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0]; // Shifts to process all bits
            read_data = 1; // Signal external that reading data
            if (valid_data_in == 0 && extra_padding_ff == 0 ) begin
                ready_for_data = 1;
            end else if (extra_padding_ff == 1) begin
                extra_padding_load = 1; // Clear extra padding flag
                sel_padding = 1;
                sel_absorb_data = 1;
                write_en = 1;
            end else begin // If data is valid
                if (last_block == 1) begin
                    last_block_process = 1;
                    last_block_process_load  = 1;
                    if (int'(valid_bytes) < BYTE_W) begin
                        sel_padding = 1;
                    end else begin
                        extra_padding_load = 1;
                        extra_padding = 1;
                    end
                end
                write_en = 1;
                sel_absorb_data = 1;
            end
            sel_masked_round = 0;
        end

        PROCESS_AD_SHIFT: begin
            sel_masked_round = 0;
            number_bits = NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0]; // numero shift per processare tutti i bit
            shift_en = 1; //ad ogni ciclo processo PAR*(d+1) bit (shift_type = 0)
            `ifdef DEBUG
                shift_enable_sipo = 1;
                if (bit_counter == (NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] - 1)) begin
                    last_cycle_sipo = 1; //se sono all'ultimo ciclo di shift
                end
            `endif
        end

        PROCESS_AD_SHIFT_LAST: begin
            sel_masked_round = 0;
            `ifdef DEBUG
                shift_enable_sipo = 1;
            `endif
            number_bits =  NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ; // numero shift per processare tutti i bit
            last_cycle = 1;
            shift_en = 1; //ad ogni ciclo processo PAR*(d+1) bit (shift_type = 0)
        end

        PROCESS_AD_DIFFUSE: begin
            sel_masked_round = 0;
            write_en = 1;
            round_counter_enable = 1;
        end

        PROCESS_AD_DIFFUSE_LAST: begin
            if (last_block == 1) begin //Modifica a questa linea: aggiunta && last_block
                if (extra_padding_ff == 0 && last_block_process_ff == 1) begin
                    sel_mux_linear_diffusion_out_x4 = 1; //carico x4 ^ 0*1
                    last_block_process_load = 1;
                end
            end
            write_en = 1;
            round_counter_enable = 1;
            rst_cnt_4 = 1; //se devo resettare il contatore dei round a 4, altrimenti a 0
            number_bits =  NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ; // numero shift per processare tutti i bit
            sel_masked_round = 0;
        end

        ABSORB_MSG_DATA: begin
            read_data = 1; //segnalo all'esterno che sto leggendo i dati
            sel_masked_round = 0;
            number_bits =  NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ; // numero shift per processare tutti i bit
            sel_absorb_data = 1;
            if (valid_data_in == 0 && extra_padding_ff == 0) begin
                ready_for_data = 1;
            end else if (extra_padding_ff == 1) begin 
                //ciphertext_valid = 1;
                write_en = 1;
                sel_absorb_data = 1;

                extra_padding_load = 1; //Metto a 0 il flag ho fatto il padding extra
                sel_padding = 1;
                sel_init_load = 1;
                rst_counter_round = 1; //resetto il contatore dei round

            end else begin
                ciphertext_valid = 1;
                write_en = 1;
                sel_absorb_data = 1;
                last_block_process_load  = 1; //0 se non è l'ultimo blocco 1 altrimenti

                if (EOT == 1) begin
                    last_block_process = 1;
                    if (int'(valid_bytes) < BYTE_W) begin
                        sel_padding = 1;
                        sel_init_load = 1;
                        rst_counter_round = 1; //resetto il contatore dei round
                    end else begin
                        extra_padding_load = 1;
                        extra_padding = 1;
                    end
                end
            end
        end

        PROCESS_MSG_SHIFT: begin
            sel_masked_round = 0;
            number_bits = NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ; // numero shift per processare tutti i bit
            shift_en = 1; //ad ogni ciclo processo PAR*(d+1) bit (shift_type = 0)
            `ifdef DEBUG
                shift_enable_sipo = 1;
                if (bit_counter == (NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] -1)) begin
                  last_cycle_sipo = 1; //se sono all'ultimo ciclo di shift
                end
            `endif
        end

        PROCESS_MSG_SHIFT_LAST: begin
            sel_masked_round = 0;
            number_bits =  NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ; // numero shift per processare tutti i bit
            last_cycle = 1;
            `ifdef DEBUG
                shift_enable_sipo = 1;
            `endif
            shift_en = 1; //ad ogni ciclo processo PAR*(d+1) bit (shift_type = 0)
        end

        PROCESS_MSG_DIFFUSE: begin
            sel_masked_round = 0;
            number_bits =  NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0] ; // numero shift per processare tutti i bit
            write_en = 1;
            round_counter_enable = 1;
        end

        PROCESS_MSG_DIFFUSE_LAST: begin
            write_en = 1;
            round_counter_enable = 1;
            sel_masked_round = 0;
            if (extra_padding_ff == 1) begin
                //sel_masked_round = 1; //devo resettare round counter a 0
            end else begin
                //sel_masked_round = 0; //devo resettare round counter a 4
                rst_cnt_4 = 1; //se devo resettare il contatore dei round a 4, altrimenti a 0
            end
            number_bits =  NUMBER_BIT_NOMASK[$clog2(NUMBER_BIT_MASK+1)-1:0]; // numero shift per processare tutti i bit
        end

        FINALIZATION_SHIFT: begin
            number_bits = NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0];
            shift_en = 1;
            shift_type = 1; // shift 1
            `ifdef DEBUG
                shift_enable_sipo = 1;
                if (bit_counter == (NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0] - 2)) begin
                    last_cycle_sipo = 1; //se sono all'ultimo ciclo di shift
                end
            `endif
        end

        FINALIZATION_SHIFT_LAST: begin
            number_bits = NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0];
            last_cycle = 1;
            shift_en = 1;
            shift_type = 1; // shift 1
            `ifdef DEBUG
                shift_enable_sipo = 1;
            `endif
            sel_mux_linear_diffusion_out_x3 = 1;
            sel_mux_linear_diffusion_out_x4 = 1;
        end

        FINALIZATION_DIFFUSE: begin
            number_bits = NUMBER_BIT_MASK[$clog2(NUMBER_BIT_MASK+1)-1:0];
            //if (round_counter == number_round - 1) begin
            //    xor_signal = reg_key2_out;
            //    sel_mux_linear_diffusion_out_x4 = 1;
            //    sel_mux_linear_diffusion_out_x3 = 1;
            //end
            write_en = 1;
            round_counter_enable = 1;
            if (round_counter == number_round - 1)
                tag_valid = 1;
        end

        SQUEEZE_TAG: begin
            
        end

        DONE: begin
            done = 1;
        end

        default: begin
            // niente
        end
    endcase
end
endmodule
