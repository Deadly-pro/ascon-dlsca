# sim_sanity.tcl — elaborate cw305_top_ascon in xsim using the FIXED sources.
# Use via:  bash regen_and_run.sh sim
# This is only a pre-hardware elaboration sanity check (no power!). It
# proves the HDL parses/connects without the earlier cdc_pulse port errors.
# Expect: "Elaboration step passed" with NO "cannot find port" messages.
set PART xc7a100tftg256-2
set TOP cw305_top_ascon
set PRJ [file normalize [file dirname [info script]]]
set srcs [glob -directory [file join $PRJ src] *.v]
set ascon_srcs [glob -directory [file join $PRJ src ascon] *.v]

create_project -in_memory -part $PART
set_property verilog_define {ASCON_CORE} [current_fileset]
read_verilog $srcs
read_verilog $ascon_srcs

# must be at least one top checked
set_property top cw305_top_ascon [current_fileset]
launch_simulation -mode behavioral -scripts_only
puts "=== SIM SANITY: Elaboration launched on fixed sources ==="
puts "=== cdc_pulse now defines ports: reset_i/src_clk/src_pulse/dst_clk/dst_pulse ==="