/* 
ChipWhisperer Artix Target - Example of connections between example registers
and rest of system.

Copyright (c) 2016-2020, NewAE Technology Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted without restriction. Note that modules within
the project may have additional restrictions, please carefully inspect
additional licenses.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of NewAE Technology Inc.
*/

`timescale 1ns / 1ps
`default_nettype none

module cw305_top #(
    parameter pBYTECNT_SIZE = 7,
    parameter pADDR_WIDTH = 21,
    parameter pPT_WIDTH = 128,
    parameter pCT_WIDTH = 128,
    parameter pKEY_WIDTH = 128,
    parameter pTAG_WIDTH = 128,
    parameter pNONCE_WIDTH = 128,
    parameter pSTATE_WIDTH = 320
)(
    // USB Interface
    input wire                          usb_clk,        // Clock
`ifdef SS2_WRAPPER
    output wire                         usb_clk_buf,    // if needed by parent module
    input  wire [7:0]                   usb_data,
    output wire [7:0]                   usb_dout,
`else
    inout wire [7:0]                    usb_data,       // Data for write/read
`endif
    input wire [pADDR_WIDTH-1:0]        usb_addr,       // Address
    input wire                          usb_rdn,        // !RD, low when addr valid for read
    input wire                          usb_wrn,        // !WR, low when data+addr valid for write
    input wire                          usb_cen,        // !CE, active low chip enable
    input wire                          usb_trigger,    // High when trigger requested

    // Buttons/LEDs on Board
    input wire                          j16_sel,        // DIP switch J16
    input wire                          k16_sel,        // DIP switch K16
    input wire                          k15_sel,        // DIP switch K15
    input wire                          l14_sel,        // DIP Switch L14
    input wire                          pushbutton,     // Pushbutton SW4, connected to R1, used here as reset
    output wire                         led1,           // red LED
    output wire                         led2,           // green LED
    output wire                         led3,           // blue LED

    // PLL
    input wire                          pll_clk1,       //PLL Clock Channel #1
    //input wire                        pll_clk2,       //PLL Clock Channel #2 (unused in this example)

    // 20-Pin Connector Stuff
    output wire                         tio_trigger,
    output wire                         tio_clkout,
    input  wire                         tio_clkin

    // Block Interface to Crypto Core
`ifdef USE_BLOCK_INTERFACE
   ,output wire                         crypto_clk,
    output wire                         crypto_rst,
    output wire [pPT_WIDTH-1:0]         crypto_textout,
    output wire [pKEY_WIDTH-1:0]        crypto_keyout,
    input  wire [pCT_WIDTH-1:0]         crypto_cipherin,
    output wire                         crypto_start,
    input wire                          crypto_ready,
    input wire                          crypto_done,
    input wire                          crypto_busy,
    input wire                          crypto_idle
`endif
    );

    wire [pKEY_WIDTH-1:0] crypt_key;
    wire [pPT_WIDTH-1:0] crypt_textout;
    wire [pCT_WIDTH-1:0] crypt_cipherin;
    wire [pNONCE_WIDTH-1:0] crypt_noncein;
    wire crypt_selin;
    wire crypt_init;
    wire crypt_ready;
    wire crypt_start;
    wire crypt_done;
    wire crypt_busy;

    wire [pCT_WIDTH-1:0] crypt_cipherout;
    wire [pPT_WIDTH-1:0] crypt_textin;
    wire [pSTATE_WIDTH-1:0] crypt_stateout;

    wire isout;
    wire [pADDR_WIDTH-pBYTECNT_SIZE-1:0] reg_address;
    wire [pBYTECNT_SIZE-1:0] reg_bytecnt;
    wire reg_addrvalid;
    wire [7:0] write_data;
    wire [7:0] read_data;
    wire [7:0] control;
    wire reg_read;
    wire reg_write;
    wire [4:0] clk_settings;
    wire crypt_clk;

    wire resetn = pushbutton; // resetn is active low, control[0] is used to reset the core
    //wire resetn_hw = 1'b1;
    wire resetn_sw = ~control[0];
    wire reset = !resetn;
    wire reset_sw_i = !resetn_sw;

    `ifndef SS2_WRAPPER
        wire usb_clk_buf;
        wire [7:0] usb_dout;
        assign usb_data = isout? usb_dout : 8'bZ;
    `endif

    // USB CLK Heartbeat
    reg [24:0] usb_timer_heartbeat;
    always @(posedge usb_clk_buf) usb_timer_heartbeat <= usb_timer_heartbeat +  25'd1;
    assign led1 = usb_timer_heartbeat[24];

    // CRYPT CLK Heartbeat
    reg [22:0] crypt_clk_heartbeat;
    always @(posedge crypt_clk) crypt_clk_heartbeat <= crypt_clk_heartbeat +  23'd1;
    assign led2 = crypt_clk_heartbeat[22];


    cw305_usb_reg_fe #(
       .pBYTECNT_SIZE           (pBYTECNT_SIZE),
       .pADDR_WIDTH             (pADDR_WIDTH)
    ) U_usb_reg_fe (
       .rst                     (reset),
       .usb_clk                 (usb_clk_buf),
       .usb_din                 (usb_data),
       .usb_dout                (usb_dout),
       .usb_rdn                 (usb_rdn),
       .usb_wrn                 (usb_wrn),
       .usb_cen                 (usb_cen),
       .usb_alen                (1'b0),                 // unused
       .usb_addr                (usb_addr),
       .usb_isout               (isout),
       .reg_address             (reg_address),
       .reg_bytecnt             (reg_bytecnt),
       .reg_datao               (write_data),
       .reg_datai               (read_data),
       .reg_read                (reg_read),
       .reg_write               (reg_write),
       .reg_addrvalid           (reg_addrvalid)
    );

    // Signals from USB (to be added to register file)
    wire [127:0] ad_in; // declaration in module
    wire [127:0] ptx_in;
    wire         msg_valid;
    wire         msg_last;
    wire         msg_eot;
    wire        load_data;
    wire         msg_select;
    wire [4:0]   valid_bytes_ad;
    wire [4:0]   valid_bytes_ptx; 

    reg fsm_msg_valid;
    reg fsm_msg_last;
    reg fsm_start;
    reg fsm_msg_eot;
    reg fsm_msg_select;
    reg start_capture;

    assign msg_valid = fsm_msg_valid;
    assign msg_last = fsm_msg_last;
    assign msg_eot = fsm_msg_eot;
    assign msg_select = fsm_msg_select;
    assign crypt_start = fsm_start; // start del core ascon

    // output
    wire [127:0] ciphertext;
    wire [63:0] tag1, tag2;
    wire ready_tag, ready_for_data; 
    wire read_data_core;
    wire ciphertext_valid; 
    /*
    // ====== DEBUG PROBES — BEGIN ======
    (* mark_debug = "true", keep = "true" *) reg         dbg_ciphertext_valid;
    (* mark_debug = "true", keep = "true" *) reg [127:0]  dbg_ciphertext;
    (* mark_debug = "true", keep = "true" *) reg [319:0]  dbg_state_reg;
    // ====== DEBUG PROBES — END ======
    */
    cw305_reg_ascon #(
       .pBYTECNT_SIZE           (pBYTECNT_SIZE),
       .pADDR_WIDTH             (pADDR_WIDTH),
       .pPT_WIDTH               (pPT_WIDTH),
       .pCT_WIDTH               (pCT_WIDTH),
       .pKEY_WIDTH              (pKEY_WIDTH),
       .pTAG_WIDTH              (pTAG_WIDTH),
       .pNONCE_WIDTH            (pNONCE_WIDTH),
       .pSTATE_WIDTH            (pSTATE_WIDTH)
    ) U_reg_ascon (
       .reset_i                 (reset),
       .reset_sw_i              (reset_sw_i),
       .crypto_clk              (crypt_clk),
       .usb_clk                 (usb_clk_buf),
       .reg_address             (reg_address[pADDR_WIDTH-pBYTECNT_SIZE-1:0]),
       .reg_bytecnt             (reg_bytecnt),
       .read_data               (read_data),
       .write_data              (write_data),
       .reg_read                (reg_read),
       .reg_write               (reg_write),
       .reg_addrvalid           (reg_addrvalid),

       .exttrigger_in           (usb_trigger),

       .I_textout               (128'b0),               // unused usato in decript
       .I_cipherout_valid       (ciphertext_valid),
       .I_cipherout             (crypt_cipherout),
       .I_stateout              (crypt_stateout),
       .I_ready_tag             (ready_tag),
       .I_tagout                ({tag2, tag1}),          // tag output
       .I_ready                 (crypt_ready),
       .I_done                  (crypt_done),
       .I_busy                  (crypt_busy),
       .I_read_data_core             (read_data_core),             // Signal to read data

       .O_valid_bytes_ad           (valid_bytes_ad),
       .O_valid_bytes_msg          (valid_bytes_ptx), // Number of valid input bytes
       .O_control               (control),          
       .O_clksettings           (clk_settings),
       .O_user_led              (led3),
       .O_key                   (crypt_key),
       .O_textin                (ad_in),
       .O_textin_buffer_msg     (ptx_in), // Buffer for textin
       .O_cipherin              (),                     // unused used in decryption
       //.O_tagin                 ({tag2, tag1}),
       .O_noncein               (crypt_noncein),
       .O_start                 (load_data) // O_Start set via control[0]; asserted on next clock cycle
    );

`ifdef ICE40
    assign usb_clk_buf = usb_clk;
    assign crypt_clk = usb_clk;
    assign tio_clkout = usb_clk;
`else
    clocks U_clocks (
       .usb_clk                 (usb_clk),
       .usb_clk_buf             (usb_clk_buf),
       .I_j16_sel               (j16_sel),
       .I_k16_sel               (k16_sel),
       .I_clock_reg             (clk_settings),
       .I_cw_clkin              (tio_clkin),
       .I_pll_clk1              (pll_clk1),
       .O_cw_clkout             (tio_clkout),
       .O_cryptoclk             (crypt_clk)
    );
`endif

wire ascon_clk;
wire [127:0] ascon_key;
wire [127:0] ascon_nonce;
wire [319:0] ascon_state;
wire ascon_load;
wire ascon_busy;
wire ascon_done;

assign ascon_clk = crypt_clk;
assign ascon_key = crypt_key;
assign ascon_nonce = crypt_noncein;
assign crypt_stateout = ascon_state;
assign ascon_load = crypt_start;
assign crypt_ready = 1'b1;
assign crypt_busy = ascon_busy;


// divisione chiave e nonce
wire [63:0] key2   = crypt_key[127:64];
wire [63:0] key1   = crypt_key[63:0];
wire [63:0] nonce2 = crypt_noncein[127:64];
wire [63:0] nonce1 = crypt_noncein[63:0];
wire [63:0] iv     = 64'h00001000808c0001;

ascon_top u_ascon_top (
    .clk                (crypt_clk),
    .reset_n            (resetn & resetn_sw),
    .reset_n_lfsr       (resetn),
    .start              (crypt_start),

    .key1               (key1),
    .key2               (key2),
    .load_data          (load_data), // When key is valid

    .nonce1             (nonce1),
    .nonce2             (nonce2),
    .initialVector      (iv),

    .data_in            (msg_select ? ptx_in : ad_in),
    .valid_data_in      (msg_valid),
    .last_block         (msg_last),
    .valid_bytes        (msg_select ? valid_bytes_ptx : valid_bytes_ad),
    .EOT                (msg_eot),

    .state_reg_out      (ascon_state), // State register output (not used in this example)
    .ciphertext_valid   (ciphertext_valid),
    .ciphertext         (ciphertext),
    .done               (ascon_done),
    .ready_tag          (ready_tag),
    .tag1               (tag1),
    .tag2               (tag2),
    .read_data          (read_data_core),
    .ready_for_data     (ready_for_data)
);  

// Status signals for CW305
assign crypt_busy     = ~ready_for_data;
assign crypt_stateout = ascon_state; // To be read via USB
assign tio_trigger    = (state != IDLE) && (state != DONE);
assign crypt_done = ascon_done;
assign crypt_cipherout = ciphertext;

    // FSM to control core operations:

    parameter IDLE = 3'd0, LOAD_DATA = 3'd1, PROCESS_AD = 3'd2, PROCESS_MSG = 3'd3, DONE = 3'd4;
    reg [2:0] state, next_state;


    always @(posedge crypt_clk or negedge resetn or negedge resetn_sw) begin
        if (!resetn || !resetn_sw)
            state <= IDLE;
        else
            state <= next_state;
    end

    always @(*) begin
        next_state = state;
        case (state)
            IDLE:
                if (load_data)
                    next_state = LOAD_DATA;

            LOAD_DATA:
                if (crypt_start)
                    next_state = PROCESS_AD;

            PROCESS_AD:
                if (read_data_core)
                    next_state = PROCESS_MSG;

            PROCESS_MSG:
                if (ready_tag)
                    next_state = DONE;

            DONE:
                if (!ready_tag)
                    next_state = IDLE;

            default: next_state = IDLE;
        endcase
    end

    always @(*) begin
        fsm_msg_valid = 0;
        fsm_msg_last = 0;
        fsm_msg_eot = 0; 
        fsm_start = 0;
        fsm_msg_select = 0;
        start_capture = 0;
        case (state)
            IDLE: begin
                //niente
            end

            LOAD_DATA: begin
                fsm_start = 1;
            end

            PROCESS_AD: begin
                start_capture = 1;
                fsm_msg_valid = 1; // Valid data
                fsm_msg_last = 1; // Last block (no valid bytes present)
                fsm_msg_eot = 0; // EOT (no valid bytes present)
                fsm_msg_select = 0; // Authentication data
            end

            PROCESS_MSG: begin
                fsm_msg_valid = 1; // Valid data
                fsm_msg_last = 1; // Last block (no valid bytes present)
                fsm_msg_eot = 1; // EOT (no valid bytes present)
                fsm_msg_select = 1; // Plaintext/ciphertext data
            end

            DONE: begin
                // Nothing
            end
        endcase
    end
    /*
    // ====== DEBUG CAPTURE - BEGIN ======
    always @(posedge crypt_clk or negedge resetn or negedge resetn_sw) begin
        if (!resetn || !resetn_sw) begin
            dbg_ciphertext_valid <= 1'b0;
            dbg_ciphertext       <= {128{1'b0}};
            dbg_state_reg        <= {320{1'b0}};
        end else begin
            // Capture flag every cycle (convenient for ILA trigger)
            dbg_ciphertext_valid <= ciphertext_valid;
    
            // Snapshot ciphertext when valid (prevents pulse loss)
            if (ciphertext_valid)
                dbg_ciphertext <= ciphertext;
    
            // Continuous state snapshot (useful for observing evolution)
            dbg_state_reg <= ascon_state;
        end
    end
    // ====== DEBUG CAPTURE - END ====== */


endmodule


`default_nettype wire