# build_ascon_cw305.tcl - generate Ascon bitstream for CW305 (xc7a100tftg256-2)
# Robust PROJ_DIR anchored to THIS file's dir, not the tcl cwd.
set PART xc7a100tftg256-2
set TOP cw305_top_ascon
set script_path [info script]
if {$script_path eq ""} {
    set PROJ_DIR [file normalize [pwd]]
} else {
    set PROJ_DIR [file normalize [file dirname [file normalize $script_path]]]
}
puts "PROJ_DIR = $PROJ_DIR"
set srcs       [glob -directory [file join $PROJ_DIR src]      *.v]
set ascon_srcs [glob -directory [file join $PROJ_DIR src/ascon] *.v]
set xdc        [file join $PROJ_DIR constrs cw305.xdc]
puts "xdc = $xdc"
puts "found [llength $srcs] src, [llength $ascon_srcs] ascon"
if {[llength $srcs] == 0} {
    error "No *.v under $PROJ_DIR/src - run with absolute path to this tcl"
}
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
puts "=== BUILD DONE: [file join $PROJ_DIR ascon_cw305_top.bit] ==="
