module circular_shift_register #(
    parameter int DATA_WIDTH = 64,
    parameter int PAR = 1
)
(
    input logic clk,
    input logic reset_n,
    input logic enable,
    input logic load,
    input logic [DATA_WIDTH-1:0] data_in,
    output logic [PAR-1:0] serial_out,
    output logic [DATA_WIDTH-1:0] data_out
);

    localparam int PADDED_WIDTH = ((DATA_WIDTH + PAR - 1) / PAR) * PAR; // Allineamento a PAR
    logic [PADDED_WIDTH-1:0] shift_reg;
    logic [PADDED_WIDTH-1:0] padded_data_in;

    // Assegnazione uscita parallela
    assign data_out = shift_reg[DATA_WIDTH-1:0];

    // Assegnazione uscita seriale: prendi i PAR bit meno significativi
    assign serial_out = shift_reg[PAR-1:0];

    // Padding a sinistra
    assign padded_data_in = { {(PADDED_WIDTH-DATA_WIDTH){1'b0}}, data_in }; // Padding a sinistra
    // Assegnazione del registro di shift
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            shift_reg <= '0;
        end else if (load) begin
            shift_reg <= padded_data_in; // Caricamento asincrono
        end else if (enable) begin
            shift_reg <= {shift_reg[0+:PAR], shift_reg[PADDED_WIDTH-1:PAR]}; // Shift circolare
        end
    end
endmodule
