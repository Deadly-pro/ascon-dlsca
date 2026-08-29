# sim_lwc.tcl — mixed-language KAT simulation of ascon_top + LWC CryptoCore
set PROJ_DIR [file normalize [file dirname [info script]]/vivado_ascon]
set SIM_DIR  /tmp/sim_lwc

file mkdir $SIM_DIR
create_project -force sim_lwc $SIM_DIR -part xc7a100tftg256-2

# VHDL: LWC CryptoCore + config packages (order matters)
read_vhdl [file join $PROJ_DIR rtl_lwc LWC_config_32.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc LWC_config_ascon.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc LWC_config_ccw_32.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc design_pkg.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc NIST_LWAPI_pkg.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc CryptoCore.vhd]

# SV: adapter + testbench
read_verilog -sv [file join $PROJ_DIR rtl ascon_top.sv]
read_verilog -sv [file join $PROJ_DIR tb_lwc.sv]

# synth fileset top
set_property top tb_lwc [get_filesets sources_1]
set_property top_lib xil_defaultlib [get_filesets sources_1]

# simulation fileset: mirror sources + set top
update_compile_order -fileset sources_1
set_property top tb_lwc [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]
update_compile_order -fileset sim_1

launch_simulation -mode behavioral -simset sim_1
run -all
