# sim_lwc_ref.tcl — run the repo's OWN LWC_TB KAT testbench (proves core correct)
set PROJ_DIR [file normalize [file dirname [info script]]/vivado_ascon]
set SIM_DIR  /tmp/sim_lwc_ref

file mkdir $SIM_DIR
file copy -force [file join $PROJ_DIR rtl_lwc] $SIM_DIR/
file mkdir $SIM_DIR/rtl_lwc/KAT/v1
foreach f {pdi.txt sdi.txt do.txt} {
    file copy -force [file join /tmp/ascon_hw hardware ascon_lwc KAT v1 $f] $SIM_DIR/rtl_lwc/KAT/v1/
}
# LWC_config_tb reads KAT/v1/* relative to the xsim working directory
file mkdir [file join $SIM_DIR sim_lwc_ref.sim sim_1 behav xsim KAT v1]
foreach f {pdi.txt sdi.txt do.txt} {
    file copy -force [file join $SIM_DIR rtl_lwc KAT v1 $f] \
        [file join $SIM_DIR sim_lwc_ref.sim sim_1 behav xsim KAT v1]
}

create_project -force sim_lwc_ref $SIM_DIR -part xc7a100tftg256-2
set_property top LWC_TB [current_fileset]
set_property top_lib xil_defaultlib [current_fileset]

read_vhdl [file join $PROJ_DIR rtl_lwc LWC_config_32.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc LWC_config_ascon.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc LWC_config_ccw_32.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc LWC_config_tb.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc design_pkg.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc NIST_LWAPI_pkg.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc FIFO.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc data_piso.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc data_sipo.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc key_piso.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc PreProcessor.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc PostProcessor.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc LWC.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc CryptoCore.vhd]
read_vhdl [file join $PROJ_DIR rtl_lwc LWC_TB.vhd]

# LWC_TB uses VHDL-2008 protected types
set_property file_type {VHDL 2008} [get_files [file join $PROJ_DIR rtl_lwc LWC_TB.vhd]]

set_property top LWC_TB [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]
update_compile_order -fileset sim_1
launch_simulation -mode behavioral -simset sim_1
run -all
