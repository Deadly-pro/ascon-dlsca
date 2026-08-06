import ascon_params::WORD_SIZE;
import ascon_params::PAR;
import ascon_params::d;
import ascon_params::SHIFT_WIDTH;
import ascon_params::PADDED_WIDTH;

module shift_register (
    input  logic clk,
    input  logic reset_n,
    input  logic load,
    input  logic shift_en,
    input  logic [WORD_SIZE-1:0] data_in,
    output logic [SHIFT_WIDTH-1:0] data_out
);

    logic [PADDED_WIDTH-1:0] shift_reg; // <-- lascia così

    // Riempio il registro con i dati + padding a sinistra
    always_ff @(posedge clk or negedge reset_n) begin
        if (reset_n == 0) begin
            shift_reg <= '0;
        end else if (load) begin
            shift_reg <= { {(PADDED_WIDTH-WORD_SIZE){1'b0}}, data_in }; // zero padding on the left
        end else if (shift_en) begin
            shift_reg <= { {SHIFT_WIDTH{1'b0}}, shift_reg[PADDED_WIDTH-1:SHIFT_WIDTH] };
        end
    end

    assign data_out = shift_reg[SHIFT_WIDTH-1:0];

endmodule
