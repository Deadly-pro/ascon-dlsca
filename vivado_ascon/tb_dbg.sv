// tb_dbg.sv — one KAT vector with full FSM/handshake trace to locate the
// broken key/nonce/data transport.
module tb_dbg;
  logic clk = 0; always #50 clk = ~clk;
  logic reset_n = 0, start = 0, load_data = 0, valid_data_in = 0, last_block = 0, EOT = 0;
  logic [63:0] key1 = 0, key2 = 0, nonce1 = 0, nonce2 = 0;
  logic [63:0] initialVector = 64'h00001000808c0001;
  logic [127:0] data_in = 0;
  logic [4:0] valid_bytes = 0;
  logic [319:0] state_reg_out;
  logic ciphertext_valid, done, ready_tag, ready_for_data, read_data;
  logic [127:0] ciphertext;
  logic [63:0] tag1, tag2;

  ascon_top uut (.clk(clk), .reset_n(reset_n), .reset_n_lfsr(reset_n), .start(start),
    .key1(key1), .key2(key2), .load_data(load_data), .nonce1(nonce1), .nonce2(nonce2),
    .initialVector(initialVector), .data_in(data_in), .valid_data_in(valid_data_in),
    .last_block(last_block), .valid_bytes(valid_bytes), .EOT(EOT),
    .state_reg_out(state_reg_out), .ciphertext_valid(ciphertext_valid),
    .ciphertext(ciphertext), .done(done), .ready_tag(ready_tag), .tag1(tag1),
    .tag2(tag2), .ready_for_data(ready_for_data), .read_data(read_data));

  function automatic [63:0] rev8(input [63:0] v);
    for (int i = 0; i < 8; i++) rev8[i*8 +: 8] = v[(7-i)*8 +: 8];
  endfunction

  int prev_fsm = -1;
  always @(posedge clk) begin
    int fsm = uut.dbg_fsm;
    if (fsm != prev_fsm || uut.key_ready || uut.bdi_ready ||
        (uut.dbg_fsm == 4'd4 && uut.dbg_cnt == 4'd12)) begin
      $display("t=%0t fsm=%0d cnt=%0d widx=%0d st=%0d wcnt=%0d kv=%0d kr=%0d bv=%0d br=%0d kvldbyte=%b kp=%0d state=%032h",
        $time, uut.dbg_fsm, uut.dbg_cnt, uut.dbg_widx, uut.state, uut.wcnt,
        uut.key_valid, uut.key_ready, uut.bdi_valid, uut.bdi_ready,
        uut.bdi_valid_bytes, uut.bdi_pad_loc, uut.dbg_state_raw);
      prev_fsm = fsm;
    end
  end

  initial begin
    repeat (5) @(posedge clk);
    reset_n = 1'b1;
    repeat (2) @(posedge clk);
    $display("=== KAT1 debug ===");
    begin
      logic [127:0] key = 128'h000102030405060708090a0b0c0d0e0f;
      logic [127:0] nonce = 128'h000102030405060708090a0b0c0d0e0f;
      key1 = rev8(key[127:64]);
      key2 = rev8(key[63:0]);
      nonce1 = rev8(nonce[127:64]);
      nonce2 = rev8(nonce[63:0]);
    end
    data_in = 128'b0; valid_bytes = 5'd4; EOT = 1'b0;
    @(negedge clk); start = 1'b1;
    @(negedge clk); start = 1'b0;
    while (!read_data) @(posedge clk);
    @(negedge clk);
    data_in = {96'b0, 32'hdeadbeef}; valid_bytes = 5'd4; EOT = 1'b1;
    while (!ready_tag) @(posedge clk);
    $display("tagw: %08h %08h %08h %08h", uut.tag_w[3], uut.tag_w[2], uut.tag_w[1], uut.tag_w[0]);
    $display("ctw : %08h %08h", uut.ct_w[1], uut.ct_w[0]);
    $finish;
  end
endmodule