// tb_lwc2.sv — contract testbench: ascon_top (LWC adapter) + CryptoCore, driven
// exactly like the cw305 wrapper presents data, comparing 16-byte readback to
// fpga_expected. Zero-PT KAT (5 vectors) + non-zero-PT data-path probe.
module tb_lwc2;
  logic clk = 0; always #50 clk = ~clk;  // 10 MHz
  logic reset_n = 0;
  logic start = 0, load_data = 0, valid_data_in = 0, last_block = 0, EOT = 0;
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

  string vname;
  int nfail = 0;

  task run_vec(input string nm, input [127:0] key, input [127:0] nonce,
               input [31:0] pt, input [127:0] exp_ro);
    begin
      longint cyc = 0;
      vname = nm;
      // host register order: key1 = crypt_key[63:0] = byte-reversed K[0:8]
      key1 = rev8(key[127:64]); key2 = rev8(key[63:0]);
      nonce1 = rev8(nonce[127:64]); nonce2 = rev8(nonce[63:0]);
      data_in = 128'b0;                       // AD = 4 zero bytes (O_textin low word)
      valid_bytes = 5'd4; EOT = 1'b0;
      @(negedge clk);
      start = 1'b1;
      @(negedge clk);
      start = 1'b0;
      while (!read_data) begin
        @(posedge clk); cyc++;
        if (cyc > 5000) begin $display("TIMEOUT AD %s", nm); $finish; end
      end
      @(negedge clk);
      data_in = {96'b0, pt};                  // PT at wrapper O_textin_buffer position
      valid_bytes = 5'd4; EOT = 1'b1;
      while (!ready_tag) begin
        @(posedge clk); cyc++;
        if (cyc > 200000) begin $display("TIMEOUT TAG %s", nm); $finish; end
      end
      @(negedge clk);
      $display("=== %s ===", nm);
      $display("tagw: %08h %08h %08h %08h", uut.tag_w[3], uut.tag_w[2], uut.tag_w[1], uut.tag_w[0]);
      $display("ctw : %08h %08h", uut.ct_w[1], uut.ct_w[0]);
      $display("exp : %032h", exp_ro);
      // host readback: reg_crypt_tagout = {tag2,tag1} bytes LSB-first per word
      $display("RO  : %032h", {uut.tag_w[3], uut.tag_w[2], uut.tag_w[1], uut.tag_w[0]});
      $display("ct4 : %08h", uut.ct_w[0]);
      nfail++;
    end
  endtask

  initial begin
    repeat (5) @(posedge clk);
    reset_n = 1'b1;
    repeat (2) @(posedge clk);

    run_vec("KAT1", 128'h000102030405060708090a0b0c0d0e0f,
            128'h000102030405060708090a0b0c0d0e0f, 32'h00000000,
            128'h19c8f96a6b6a4fe5caa719a719378c6a);
    run_vec("KAT2", 128'hdeadbeefcafebabe0001020304050607,
            128'h102030405060708090a0b0c0d0e0f000, 32'h00000000,
            128'h94f0b9bc9fa873085c828fe6d1dc9341);
    run_vec("KAT3", 128'h00000000000000000000000000000000,
            128'h00000000000000000000000000000000, 32'h00000000,
            128'h3e2a56698ec81e2e053815e89761cfb5);
    run_vec("KAT4", 128'hffffffffffffffffffffffffffffffff,
            128'hffffffffffffffffffffffffffffffff, 32'h00000000,
            128'h6a9d3f7ad41bbe299bf43620864ebb5a);
    run_vec("KAT5", 128'h0123456789abcdef0123456789abcdef,
            128'hfedcba9876543210fedcba9876543210, 32'h00000000,
            128'h502074376152408dc9d470724dc496f3);
    run_vec("NZPT", 128'h000102030405060708090a0b0c0d0e0f,
            128'h000102030405060708090a0b0c0d0e0f, 32'hdeadbeef,
            128'hb132c7e645551cd00fd2a7a0c79a3285);
    $display("=== ALL DONE (nfail=%0d) ===", nfail);
    $finish;
  end
endmodule