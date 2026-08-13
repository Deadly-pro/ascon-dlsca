# Build Ascon-128 (compact-yet-fast-ascon) bitstream for CW305-100t
set PART xc7a100tftg256-2
set TOP  cw305_top
set PROJ_DIR [file normalize [file dirname [info script]]/vivado_ascon]
set fpga_srcs   [glob -directory [file join $PROJ_DIR fpga] *.v]
set rtl_srcs    [glob -directory [file join $PROJ_DIR rtl]  *.sv]
set xdc         [file join $PROJ_DIR fpga cw305.xdc]
set defs_dir    [file join $PROJ_DIR fpga]

create_project -in_memory -part $PART
if {[info exists env(ASCON_UNMASKED)]} {
    set_property verilog_define ASCON_UNMASKED [current_fileset]
}
read_verilog -sv $fpga_srcs
read_verilog -sv $rtl_srcs
read_xdc $xdc
set_property include_dirs $defs_dir [current_fileset]
synth_design -top $TOP -part $PART
opt_design
place_design
route_design
write_bitstream -force [file join $PROJ_DIR ascon_cw305_top.bit]
write_checkpoint -force [file join $PROJ_DIR ascon_cw305_routed.dcp]
puts "=== BUILD DONE ==="
