import ascon_params::WORD_SIZE;

module register (
    input  logic clk,
    input  logic reset_n,
    input  logic load,
    input  logic [WORD_SIZE-1:0] data_in,
    output logic [WORD_SIZE-1:0] data_out
);

    logic [WORD_SIZE-1:0] reg_q;

    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n)
            reg_q <= '0;
        else if (load)
            reg_q <= data_in;
    end

    assign data_out = reg_q;

endmodule
