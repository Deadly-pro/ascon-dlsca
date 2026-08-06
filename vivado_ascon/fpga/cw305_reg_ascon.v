/*
ChipWhisperer Artix Target - Example of connections between example registers
and rest of system.

Copyright (c) 2020, NewAE Technology Inc.
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

`default_nettype none `timescale 1ns / 1ps
`include "cw305_ascon_defines.v"

module cw305_reg_ascon #(
  parameter pADDR_WIDTH = 21,
  parameter pBYTECNT_SIZE = 7,
  parameter pDONE_EDGE_SENSITIVE = 1,
  parameter pPT_WIDTH = 128,
  parameter pCT_WIDTH = 128,
  parameter pKEY_WIDTH = 128,
  parameter pTAG_WIDTH = 128,
  parameter pPT_LENGTH = 2, // Number of blocks in ciphertext
  parameter pNONCE_WIDTH = 128,
  parameter pSTATE_WIDTH = 320,
  parameter pCRYPT_TYPE = 2,
  parameter pCRYPT_REV = 5,
  parameter pIDENTIFY = 8'h2e
) (

  // Interface to cw305_usb_reg_fe:
  input wire usb_clk,
  input wire crypto_clk,
  input wire reset_i,
  input wire reset_sw_i,  // Reset signal from the software interface
  input wire [pADDR_WIDTH-pBYTECNT_SIZE-1:0] reg_address,  // Address of register
  input wire [pBYTECNT_SIZE-1:0] reg_bytecnt,  // Current byte count
  output reg [7:0] read_data,  //
  input wire [7:0] write_data,  //
  input wire reg_read,  // Read flag. One clock cycle AFTER this flag is high
                        // valid data must be present on the read_data bus
  input wire reg_write,  // Write flag. When high on rising edge valid data is
                         // present on write_data
  input wire reg_addrvalid,  // Address valid flag

  // from top:
  input wire exttrigger_in,

  // register inputs:
  input wire [pPT_WIDTH-1:0] I_textout,
  input wire I_cipherout_valid,
  input wire I_read_data_core,
  input wire [pCT_WIDTH-1:0] I_cipherout,
  input wire [pSTATE_WIDTH-1:0] I_stateout,
  input wire I_ready_tag,  // Crypto core ready for tag input. Tie to '1' if not used.
  input wire [pTAG_WIDTH-1:0] I_tagout,  // tag output
  input wire I_ready,  /* Crypto core ready. Tie to '1' if not used. */
  input wire I_done,  /* Crypto done. Can be high for one crypto_clk cycle or longer. */
  input wire I_busy,  /* Crypto busy. */

  // register outputs:
  output wire [7:0] O_control,  // Control register output
  output wire [4:0] O_valid_bytes_ad,  // Number of valid bytes in textin/cipherin/tagin/noncein
  output wire [4:0] O_valid_bytes_msg,  // Number of valid bytes in textin/cipherin/tagin/noncein
  output reg [4:0] O_clksettings,
  output reg O_user_led,
  output wire [pKEY_WIDTH-1:0] O_key,
  output wire [pPT_WIDTH-1:0] O_textin,
  output wire [pPT_WIDTH-1:0] O_textin_buffer_msg, // Buffer for textin
  output wire [pCT_WIDTH-1:0] O_cipherin,
  //output wire [pTAG_WIDTH-1:0] O_tagin,
  output wire [pNONCE_WIDTH-1:0] O_noncein,
  output wire O_start  /* High for one crypto_clk cycle, indicates text ready. */

);

  reg  [             7:0] reg_read_data;
  reg  [   pCT_WIDTH-1:0] reg_crypt_cipherin;
  reg  [  pKEY_WIDTH-1:0] reg_crypt_key;
  reg  [   pPT_WIDTH-1:0] reg_crypt_textin;
  reg  [   pPT_WIDTH-1:0] reg_crypt_textin_buffer_msg; // Buffer for textin
  reg  [   pPT_WIDTH-1:0] reg_crypt_textout;
  reg  [   pCT_WIDTH-1:0] reg_crypt_cipherout;
  reg  [  pTAG_WIDTH-1:0] reg_crypt_tagout;
  reg  [pNONCE_WIDTH-1:0] reg_crypt_noncein;
  reg  [pSTATE_WIDTH-1:0] reg_crypt_stateout;
  reg                     reg_crypt_go_pulse;
  reg [7:0]               reg_control;  
  reg [15:0]               reg_valid_bytes_ad;
  reg [15:0]               reg_valid_bytes_msg;
   reg                     busy_usb;

  wire                    reg_crypt_go_pulse_crypt;
  wire [7:0]              status_reg;

  

  reg done_latched, ready_tag_latched, cipherout_valid_latched, read_data_core_latched, busy_usb_latched;
  reg status_read_ack;
  //Generazione del segnale stato_read_ack:
  always @(posedge usb_clk or posedge reset_i) begin
  if (reset_i)
    status_read_ack <= 1'b0;
  else
    status_read_ack <= (reg_read && reg_addrvalid && reg_address == `REG_CRYPT_STATUS);
  end

  // Latch the status signals to avoid glitches on the USB interface
  always @(posedge crypto_clk or posedge reset_i or posedge reset_sw_i) begin
    if (reset_i || reset_sw_i) begin
      done_latched <= 1'b0;
      ready_tag_latched <= 1'b0;
      cipherout_valid_latched <= 1'b0;
      read_data_core_latched <= 1'b0;
      busy_usb_latched <= 1'b0;
    end else begin
      if (busy_usb)
        busy_usb_latched <= 1'b1;
      else if (status_read_ack)
        busy_usb_latched <= 1'b0;
      
      if (I_done)
        done_latched <= 1'b1;
      else if (status_read_ack)
        done_latched <= 1'b0;

      if (I_ready_tag)
        ready_tag_latched <= 1'b1;
      else if (status_read_ack)
        ready_tag_latched <= 1'b0;

      if (I_cipherout_valid)
        cipherout_valid_latched <= 1'b1;
      else if (status_read_ack)
        cipherout_valid_latched <= 1'b0;

      if (I_read_data_core)
        read_data_core_latched <= 1'b1;
      else if (status_read_ack)
        read_data_core_latched <= 1'b0;
    end
  end

  assign status_reg[0] = busy_usb_latched;
  assign status_reg[1] = read_data_core_latched;
  assign status_reg[2] = cipherout_valid_latched;
  assign status_reg[3] = ready_tag_latched;
  assign status_reg[4] = done_latched;
  assign status_reg[7:5] = 3'b000;

  reg                     done_r;
  wire                    done_pulse;
  wire                    crypt_go_pulse;
  reg                     go_r;
  reg                     go;
  wire [            31:0] buildtime;

  (* ASYNC_REG = "TRUE" *)reg  [  pKEY_WIDTH-1:0] reg_crypt_key_crypt;
  (* ASYNC_REG = "TRUE" *)reg  [   pPT_WIDTH-1:0] reg_crypt_textin_crypt;
  (* ASYNC_REG = "TRUE" *)reg  [   pPT_WIDTH-1:0] reg_crypt_textin_buffer_msg_crypt; // Buffer for textin
  (* ASYNC_REG = "TRUE" *)reg  [  pTAG_WIDTH-1:0] reg_crypt_tagout_crypt;
  (* ASYNC_REG = "TRUE" *) reg [pTAG_WIDTH-1:0] reg_crypt_tagout_usb;
  (* ASYNC_REG = "TRUE" *)reg  [pNONCE_WIDTH-1:0] reg_crypt_noncein_crypt;
  (* ASYNC_REG = "TRUE" *)reg  [   pPT_WIDTH-1:0] reg_crypt_textout_usb;
  (* ASYNC_REG = "TRUE" *)reg  [   pCT_WIDTH-1:0] reg_crypt_cipherout_usb;
  (* ASYNC_REG = "TRUE" *)reg  [pSTATE_WIDTH-1:0] reg_crypt_stateout_usb;
  (* ASYNC_REG = "TRUE" *)reg  [           1:0] go_pipe;
  (* ASYNC_REG = "TRUE" *)reg  [           1:0] busy_pipe;


  always @(posedge crypto_clk) done_r <= I_done & pDONE_EDGE_SENSITIVE;
  assign done_pulse = I_done & ~done_r;

  always @(posedge crypto_clk) begin
    if (I_cipherout_valid) begin
      reg_crypt_cipherout <= I_cipherout;
      
    end
    reg_crypt_stateout  <= I_stateout;

    if (done_pulse) begin
      reg_crypt_textout   <= I_textout;
    end
  end

  // Save tag output from core when valid
  always @(posedge crypto_clk) begin
      if (I_ready_tag) begin
          reg_crypt_tagout <= I_tagout;
      end
  end

`ifdef ICE40
  // iCE40 target has just one clock domain, so there's no CDC to worry
  // about; it also can't afford to spare the extra registers:
  always @(*) begin
    reg_crypt_cipherout_usb  = reg_crypt_cipherout;
    reg_crypt_textout_usb    = reg_crypt_textout;
    reg_crypt_key_crypt      = reg_crypt_key;
    reg_crypt_textin_crypt   = reg_crypt_textin;
    reg_crypt_textin_buffer_msg_crypt = reg_crypt_textin_buffer_msg; // Buffer for textin
    reg_crypt_stateout_usb   = reg_crypt_stateout;
    reg_crypt_tagout_crypt    = reg_crypt_tagout;
    reg_crypt_noncein_crypt  = reg_crypt_noncein;
  end
`else
  always @(posedge usb_clk) begin
    reg_crypt_tagout_usb     <= reg_crypt_tagout;
    reg_crypt_textout_usb    <= reg_crypt_textout;
    reg_crypt_stateout_usb   <= reg_crypt_stateout;
    reg_crypt_cipherout_usb  <= reg_crypt_cipherout;
  end
  always @(posedge crypto_clk) begin
    reg_crypt_key_crypt     <= reg_crypt_key;
    reg_crypt_textin_crypt  <= reg_crypt_textin;
    reg_crypt_textin_buffer_msg_crypt <= reg_crypt_textin_buffer_msg; // Buffer for textin
    reg_crypt_tagout_crypt   <= reg_crypt_tagout;
    reg_crypt_noncein_crypt <= reg_crypt_noncein;
  end
`endif

  assign O_textin  = reg_crypt_textin_crypt;
  assign O_textin_buffer_msg = reg_crypt_textin_buffer_msg_crypt; // Buffer for textin
  assign O_key     = reg_crypt_key_crypt;
  assign O_noncein = reg_crypt_noncein_crypt;
  assign O_start   = crypt_go_pulse || reg_crypt_go_pulse_crypt;
  assign O_control = reg_control;
  assign O_valid_bytes_ad = reg_valid_bytes_ad;
  assign O_valid_bytes_msg = reg_valid_bytes_msg;
  //////////////////////////////////
  // read logic:
  //////////////////////////////////

  always @(*) begin
    if (reg_addrvalid && reg_read) begin
      case (reg_address)
        `REG_CLKSETTINGS:     reg_read_data = O_clksettings;
        `REG_USER_LED:        reg_read_data = O_user_led;
        `REG_CRYPT_TYPE:      reg_read_data = pCRYPT_TYPE;
        `REG_CRYPT_REV:       reg_read_data = pCRYPT_REV;
        `REG_IDENTIFY:        reg_read_data = pIDENTIFY;
        `REG_CRYPT_GO:       reg_read_data = busy_usb ? 8'h01 : 8'h00; // 0=idle, non-zero=busy (CW305 is_done compat)
        `REG_CRYPT_STATUS: reg_read_data = status_reg; 
        `REG_CRYPT_KEY:       reg_read_data = reg_crypt_key[reg_bytecnt*8+:8];
        `REG_CRYPT_TEXTIN:    reg_read_data = reg_crypt_textin[reg_bytecnt*8+:8];
        `REG_CRYPT_TEXTIN_BUFFER_MSG: reg_read_data = reg_crypt_textin_buffer_msg[reg_bytecnt*8+:8]; // Buffer for textin
        `REG_CRYPT_CIPHERIN:  reg_read_data = reg_crypt_cipherin[reg_bytecnt*8+:8];
        `REG_CRYPT_TAGOUT:     reg_read_data = reg_crypt_tagout_usb[reg_bytecnt*8+:8];
        `REG_CRYPT_NONCEIN:   reg_read_data = reg_crypt_noncein[reg_bytecnt*8+:8];
        `REG_CRYPT_TEXTOUT:   reg_read_data = reg_crypt_textout_usb[reg_bytecnt*8+:8];
        `REG_CRYPT_CIPHEROUT: reg_read_data = reg_crypt_cipherout_usb[reg_bytecnt*8+:8];
        `REG_CRYPT_STATEOUT:  reg_read_data = reg_crypt_stateout_usb[reg_bytecnt*8+:8];
        `REG_CONTROL:         reg_read_data = reg_control;
        `REG_VALID_BYTES_AD:  reg_read_data = reg_valid_bytes_ad[reg_bytecnt*8+:8];
        `REG_VALID_BYTES_MSG: reg_read_data = reg_valid_bytes_msg[reg_bytecnt*8+:8];
        `REG_BUILDTIME:       reg_read_data = buildtime[reg_bytecnt*8+:8];
        default:              reg_read_data = 0;
      endcase
    end else reg_read_data = 0;
  end

  // Register output read data to ease timing. If you need read data one clock
  // cycle earlier, simply remove this stage:
  always @(posedge usb_clk) read_data <= reg_read_data;

  //////////////////////////////////
  // write logic (USB clock domain):
  //////////////////////////////////
  always @(posedge usb_clk) begin
    if (reset_i) begin
      O_clksettings       <= 0;
      O_user_led          <= 0;
      reg_crypt_go_pulse  <= 1'b0;
      reg_control         <= 0;
      reg_crypt_textin    <= 0;
      reg_crypt_textin_buffer_msg <= 0; // Buffer for textin
      reg_crypt_cipherin  <= 0;
      reg_crypt_key       <= 0;
      reg_crypt_noncein   <= 0;
      reg_valid_bytes_ad  <= 0;
      reg_valid_bytes_msg <= 0;
    end else begin
      if (reg_addrvalid && reg_write) begin
        case (reg_address)
          `REG_CLKSETTINGS:    O_clksettings <= write_data;
          `REG_USER_LED:       O_user_led <= write_data;
          `REG_CRYPT_TEXTIN:   reg_crypt_textin[reg_bytecnt*8+:8] <= write_data;
          `REG_CRYPT_TEXTIN_BUFFER_MSG: reg_crypt_textin_buffer_msg[reg_bytecnt*8+:8] <= write_data; // Buffer for textin
          `REG_CRYPT_CIPHERIN: reg_crypt_cipherin[reg_bytecnt*8+:8] <= write_data;
          `REG_CRYPT_KEY:      reg_crypt_key[reg_bytecnt*8+:8] <= write_data;
          `REG_CRYPT_NONCEIN:  reg_crypt_noncein[reg_bytecnt*8+:8] <= write_data;
          `REG_CONTROL:        reg_control <= write_data;
          `REG_VALID_BYTES_AD:    reg_valid_bytes_ad[reg_bytecnt*8+:8] <= write_data;
          `REG_VALID_BYTES_MSG:   reg_valid_bytes_msg[reg_bytecnt*8+:8] <= write_data;
        endcase
      end
      // REG_CRYPT_GO register is special: writing it creates a pulse. Reading it gives you the "busy" status.
      if ((reg_addrvalid && reg_write && (reg_address == `REG_CRYPT_GO)))
        reg_crypt_go_pulse <= 1'b1;
      else reg_crypt_go_pulse <= 1'b0;

    end
  end

  always @(posedge crypto_clk) begin
    {go_r, go, go_pipe} <= {go, go_pipe, exttrigger_in};
  end
  assign crypt_go_pulse = go & !go_r;

  cdc_pulse U_go_pulse (
    .reset_i  (reset_i),
    .src_clk  (usb_clk),
    .src_pulse(reg_crypt_go_pulse),
    .dst_clk  (crypto_clk),
    .dst_pulse(reg_crypt_go_pulse_crypt)
  );

`ifdef ICE40
  always @(*) busy_usb = I_busy;
`else
  always @(posedge usb_clk) {busy_usb, busy_pipe} <= {busy_pipe, I_busy};
`endif


`ifdef ILA_REG
  ila_0 U_reg_ila (
    .clk    (usb_clk),            // input wire clk
    .probe0 (reg_address[7:0]),   // input wire [7:0]  probe0
    .probe1 (reg_bytecnt),        // input wire [6:0]  probe1
    .probe2 (read_data),          // input wire [7:0]  probe2
    .probe3 (write_data),         // input wire [7:0]  probe3
    .probe4 (reg_read),           // input wire [0:0]  probe4
    .probe5 (reg_write),          // input wire [0:0]  probe5
    .probe6 (reg_addrvalid),      // input wire [0:0]  probe6
    .probe7 (reg_read_data),      // input wire [7:0]  probe7
    .probe8 (exttrigger_in),      // input wire [0:0]  probe8
    .probe9 (1'b0),               // input wire [0:0]  probe9
    .probe10(reg_crypt_go_pulse)  // input wire [0:0]  probe10
  );
`endif

`ifdef ILA_CRYPTO
  ila_1 U_reg_aes (
    .clk   (crypto_clk),        // input wire clk
    .probe0(O_start),           // input wire [0:0]  probe0  
    .probe1(I_done),            // input wire [0:0]  probe1 
    .probe2(I_cipherout[7:0]),  // input wire [7:0]  probe2 
    .probe3(O_textin[7:0]),     // input wire [7:0]  probe3 
    .probe4(done_pulse)         // input wire [0:0]  probe4 
  );
`endif

`ifdef ICE40
  // dynamically generated by build process:
  `include "timestamp.v"
`else
`ifndef __ICARUS__
  USR_ACCESSE2 U_buildtime (
    .CFGCLK   (),
    .DATA     (buildtime),
    .DATAVALID()
  );
`else
  assign buildtime = 0;
`endif
`endif


endmodule

`default_nettype wire
