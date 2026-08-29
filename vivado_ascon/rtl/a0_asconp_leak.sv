`ifndef INCL_ASCONP_LEAK
`define INCL_ASCONP_LEAK
// Licensed under the Creative Commons 1.0 Universal License (CC0), see LICENSE
// for details.
//
// Leakage amplifier module: a physically distinct, dont_touch-ed copy of the
// Ascon-p permutation cloud. Function-identical to the logic in asconp, with
// no outputs connected, so the crypto data path is byte-exact untouched. Its
// purpose is purely electrodynamic: its LUTs toggle with the same data each
// round, multiplying the data-dependent switching current on VCCINT. Vivado
// cannot merge it with asconp because the two sit in separate hierarchies and
// the instance carries DONT_TOUCH.
`include "config.sv"

module asconp_leak (
    input  logic [ 3:0] round_cnt,
    input  logic [63:0] x0_i,
    input  logic [63:0] x1_i,
    input  logic [63:0] x2_i,
    input  logic [63:0] x3_i,
    input  logic [63:0] x4_i,
    output logic [319:0] sink_o
);
  logic [UROL-1:0][63:0] a0, a1, a2, a3, a4;
  logic [UROL-1:0][63:0] b0, b1, b2, b3, b4;
  logic [UROL-1:0][63:0] c0, c1, c2, c3, c4;
  logic [UROL : 0][63:0] x0, x1, x2, x3, x4;
  logic [UROL-1:0][3:0] t;

  assign x0[0] = x0_i;
  assign x1[0] = x1_i;
  assign x2[0] = x2_i;
  assign x3[0] = x3_i;
  assign x4[0] = x4_i;

  genvar i;
  generate
    for (i = 0; i < UROL; i++) begin : g_leak_round
      assign t[i] = (4'hC) - (round_cnt - i);
      assign a0[i] = x0[i] ^ x4[i];
      assign a1[i] = x1[i];
      assign a2[i] = x2[i] ^ x1[i] ^ {56'd0, (4'hF - t[i]), t[i]};
      assign a3[i] = x3[i];
      assign a4[i] = x4[i] ^ x3[i];
      assign b0[i] = a0[i] ^ ((~a1[i]) & a2[i]);
      assign b1[i] = a1[i] ^ ((~a2[i]) & a3[i]);
      assign b2[i] = a2[i] ^ ((~a3[i]) & a4[i]);
      assign b3[i] = a3[i] ^ ((~a4[i]) & a0[i]);
      assign b4[i] = a4[i] ^ ((~a0[i]) & a1[i]);
      assign c0[i] = b0[i] ^ b4[i];
      assign c1[i] = b1[i] ^ b0[i];
      assign c2[i] = ~b2[i];
      assign c3[i] = b3[i] ^ b2[i];
      assign c4[i] = b4[i];
      assign x0[i+1] = c0[i] ^ {c0[i][18:0], c0[i][63:19]} ^ {c0[i][27:0], c0[i][63:28]};
      assign x1[i+1] = c1[i] ^ {c1[i][60:0], c1[i][63:61]} ^ {c1[i][38:0], c1[i][63:39]};
      assign x2[i+1] = c2[i] ^ {c2[i][0:0], c2[i][63:01]} ^ {c2[i][05:0], c2[i][63:06]};
      assign x3[i+1] = c3[i] ^ {c3[i][9:0], c3[i][63:10]} ^ {c3[i][16:0], c3[i][63:17]};
      assign x4[i+1] = c4[i] ^ {c4[i][6:0], c4[i][63:07]} ^ {c4[i][40:0], c4[i][63:41]};
    end
  endgenerate
  (* dont_touch = "true" *) assign sink_o = {x4[UROL], x3[UROL],
                                             x2[UROL], x1[UROL], x0[UROL]};
endmodule

`endif  // INCL_ASCONP_LEAK