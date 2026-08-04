# Auto-generated: build Ascon bitstream for CW305-100t
set PART xc7a100tftg256-2
set TOP cw305_top_ascon
set PROJ_DIR [file normalize [file dirname [info script]]]
set srcs [glob -directory [file join $PROJ_DIR src] *.v]
set ascon_srcs [glob -directory [file join $PROJ_DIR src ascon] *.v]
set xdc [file join $PROJ_DIR constrs cw305.xdc]
create_project -in_memory -part $PART
set_property verilog_define {ASCON_CORE} [current_fileset]
read_verilog $srcs
read_verilog $ascon_srcs
read_xdc $xdc
synth_design -top $TOP -part $PART -verilog_define ASCON_CORE
opt_design
place_design
route_design
write_bitstream -force [file join $PROJ_DIR ascon_cw305_top.bit]
write_checkpoint -force [file join $PROJ_DIR ascon_cw305_routed.dcp]
puts "=== BUILD DONE ==="
