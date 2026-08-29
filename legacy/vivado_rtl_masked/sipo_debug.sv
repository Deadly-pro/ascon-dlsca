// ============================================================================
// Module: sipo_debug
// Description:
//   Debug-only serial-in/parallel-out (SIPO) shift register used exclusively
//   to trace and record round constant results in masked implementations
//   (e.g., ASCON).
//
//   Supports two modes:
//     - PAR-bit shift (unmasked),
//     - (d+1)*PAR-bit shift (masked).
//
//   Accumulates bits into `state` register, updated on `shift_en` cycles,
//   with support for partial final shifts via `last_cycle`.
//
//   Parameters:
//     - WORD_SIZE: accumulation register size,
//     - PAR: parallelism degree,
//     - d: masking order.
//
//   ⚠️ **Note**: Used only for debugging and verification purposes, not in
//   critical circuit operation.
// ============================================================================
import ascon_params::WORD_SIZE;
import ascon_params::PAR;
import ascon_params::d;
import ascon_params::SHIFT_PAR;
import ascon_params::SHIFT_PAR_D_PLUS_1;
import ascon_params::SHIFT_PAR_LAST;
import ascon_params::SHIFT_PAR_D_PLUS_1_LAST;

module sipo_debug (
    input  logic clk,
    input  logic reset_n,
    input  logic shift_en,
    input  logic shift_type,     // 1 = shift PAR, 0 = shift d+1
    input  logic last_cycle,     // indicates if this is the last shift to perform

    /* verilator lint_off UNUSED */
    input  logic [SHIFT_PAR_D_PLUS_1-1:0] in_shifted_dplus1,
    /* verilator lint_on UNUSED */
    input  logic [SHIFT_PAR-1:0]         in_shifted_1bit,
    output logic [WORD_SIZE-1:0] data_out
);

    logic [WORD_SIZE-1:0] state, next_state;

    // === Combinational logic for next_state
    generate 
        if (SHIFT_PAR_D_PLUS_1_LAST < WORD_SIZE) begin : gen_case1
            always_comb begin
                next_state = state;

                if (shift_en) begin
                    if (shift_type) begin
                        if (last_cycle)
                            next_state = {in_shifted_1bit[SHIFT_PAR_LAST-1:0], state[WORD_SIZE-1:SHIFT_PAR_LAST]};
                        else
                            next_state = {in_shifted_1bit, state[WORD_SIZE-1:SHIFT_PAR]};
                    end else begin
                        if (last_cycle)
                            next_state = {in_shifted_dplus1[SHIFT_PAR_D_PLUS_1_LAST-1:0], state[WORD_SIZE-1:SHIFT_PAR_D_PLUS_1_LAST]};
                        else
                            next_state = {in_shifted_dplus1, state[WORD_SIZE-1:SHIFT_PAR_D_PLUS_1]};
                    end
                end
            end
        end
        else begin : gen_case2
            always_comb begin
                next_state = state;

                if (shift_en) begin
                    if (shift_type) begin
                        if (last_cycle)
                            next_state = {in_shifted_1bit[SHIFT_PAR_LAST-1:0], state[WORD_SIZE-1:SHIFT_PAR_LAST]};
                        else
                            next_state = {in_shifted_1bit, state[WORD_SIZE-1:SHIFT_PAR]};
                    end else begin
                        next_state = in_shifted_dplus1[WORD_SIZE-1:0];
                    end
                end
            end
        end
    endgenerate
    // === Sequential block
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state <= '0;
        end else begin
            if (shift_en) begin
                state <= next_state;
            end
        end
    end

    assign data_out = state;
endmodule
