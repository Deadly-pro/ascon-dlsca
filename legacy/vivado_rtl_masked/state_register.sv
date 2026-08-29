// ============================================================================
// Module: state_register
// Description:
//   Parametric state register for the ASCON cipher algorithm (or similar).
//   Stores and manages 5 64-bit words representing the algorithm state.
//
//   Supports two primary operations:
//     - Parallel write of entire state (`write_en`),
//     - Serial shift of state in two modes:
//         • PAR-bit shift per word (unmasked),
//         • (d+1)*PAR-bit shift per word (masked).
//
//   Designed for masked architectures, adapting to parallelism degree and
//   masking order. Handles final cycle with reduced bit shifts via `last_cycle`.
//
//   Parameters:
//     - COL_SIZE: number of words (default: 5),
//     - WORD_SIZE: word size in bits (default: 64),
//     - PAR: parallelism degree,
//     - d: masking order,
//     - SHIFT_PAR[_LAST], SHIFT_PAR_D_PLUS_1[_LAST]: handle full/partial shifts.
//
//   Outputs:
//     - `data_out`: current complete state,
//     - `out_shifted_dplus1`: bit portion for masked shift.
//
// ============================================================================
import ascon_params::COL_SIZE;
import ascon_params::PAR;
import ascon_params::d;
import ascon_params::WORD_SIZE;
import ascon_params::SHIFT_PAR;
import ascon_params::SHIFT_PAR_D_PLUS_1;
import ascon_params::SHIFT_PAR_LAST;
import ascon_params::SHIFT_PAR_D_PLUS_1_LAST;

module state_register 
(
    input  logic clk,
    input  logic reset_n,
    input  logic write_en,
    input  logic shift_en,
    input  logic shift_type, // 1 = shift 1, 0 = shift d+1
    input  logic last_cycle, 

    input  logic [COL_SIZE*WORD_SIZE-1:0] data_in,
    input  logic [COL_SIZE*SHIFT_PAR_D_PLUS_1-1:0] in_shifted_dplus1,
    input  logic [COL_SIZE*SHIFT_PAR-1:0]          in_shifted_1bit,
    
    output logic [COL_SIZE*SHIFT_PAR_D_PLUS_1-1:0] out_shifted_dplus1,
    output logic [COL_SIZE*WORD_SIZE-1:0] data_out
);

    logic [WORD_SIZE-1:0] state [0:COL_SIZE-1];
    (* keep = "true" *) logic [WORD_SIZE-1:0] next_state [0:COL_SIZE-1];

    generate 
    if (SHIFT_PAR_D_PLUS_1_LAST < WORD_SIZE) begin : gen_case1
        always_comb begin
            for (int i = 0; i < COL_SIZE; i++) begin
                next_state[i] = state[i]; // Default

                if (shift_en) begin
                    if (shift_type) begin
                        if (last_cycle) begin
                            // Last cycle with PAR_LAST
                            next_state[i] = {in_shifted_1bit[i*SHIFT_PAR +: SHIFT_PAR_LAST], state[i][WORD_SIZE-1:SHIFT_PAR_LAST]};
                        end else begin
                            // Normal cycles
                            next_state[i] = {in_shifted_1bit[i*SHIFT_PAR +: SHIFT_PAR], state[i][WORD_SIZE-1:SHIFT_PAR]};
                        end
                    end else begin
                        if (last_cycle) begin
                            next_state[i] = {in_shifted_dplus1[i*SHIFT_PAR_D_PLUS_1 +: SHIFT_PAR_D_PLUS_1_LAST], state[i][WORD_SIZE-1:SHIFT_PAR_D_PLUS_1_LAST]};
                        end else begin
                            next_state[i] = {in_shifted_dplus1[i*SHIFT_PAR_D_PLUS_1 +: SHIFT_PAR_D_PLUS_1], state[i][WORD_SIZE-1:SHIFT_PAR_D_PLUS_1]};
                        end
                    end
                end else if (write_en) begin
                    next_state[i] = data_in[i*WORD_SIZE +: WORD_SIZE];
                end
            end
        end

    end else begin : gen_case2
        always_comb begin
            for (int i = 0; i < COL_SIZE; i++) begin
                next_state[i] = state[i]; // Default

                if (shift_en) begin
                    if (shift_type) begin
                        if (last_cycle) begin
                            // Last cycle with PAR_LAST
                            next_state[i] = {in_shifted_1bit[i*SHIFT_PAR +: SHIFT_PAR_LAST], state[i][WORD_SIZE-1:SHIFT_PAR_LAST]};
                        end else begin
                            // Normal cycles
                            next_state[i] = {in_shifted_1bit[i*SHIFT_PAR +: SHIFT_PAR], state[i][WORD_SIZE-1:SHIFT_PAR]};
                        end
                    end else begin
                        // Last cycle with PAR_LAST
                        next_state[i] = in_shifted_dplus1[i*SHIFT_PAR_D_PLUS_1 +: WORD_SIZE];
                    end
                end else if (write_en) begin
                    next_state[i] = data_in[i*WORD_SIZE +: WORD_SIZE];
                end
            end
        end
    end
    endgenerate

    // === Sequential block
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            for (int i = 0; i < COL_SIZE; i = i + 1) begin
                state[i] <= {WORD_SIZE{1'b0}}; // reset each word
            end
        end else begin
            for (int i = 0; i < COL_SIZE; i = i + 1) begin
                state[i] <= next_state[i];
            end
        end
    end
    
    // === Combinatorial output
    generate
    if (SHIFT_PAR_D_PLUS_1_LAST < WORD_SIZE) begin : gen_caseNoPArMAx
        always_comb begin
            for (int i = 0; i < COL_SIZE; i++) begin
                out_shifted_dplus1[i*SHIFT_PAR_D_PLUS_1 +: SHIFT_PAR_D_PLUS_1] =
                state[i][SHIFT_PAR_D_PLUS_1-1:0];
                data_out[i*WORD_SIZE +: WORD_SIZE] = state[i];
            end
        end
    end
    else begin : gen_caseNoPArMAx
        always_comb begin
            for (int i = 0; i < COL_SIZE; i++) begin
                out_shifted_dplus1[i*WORD_SIZE +: WORD_SIZE] =
                state[i][WORD_SIZE-1:0];
                data_out[i*WORD_SIZE +: WORD_SIZE] = state[i];
            end
        end
    end
    endgenerate

endmodule
