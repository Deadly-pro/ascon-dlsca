# Build Ascon-128 (ascon-hardware-sca, unprotected, CCW=32) bitstream for CW305-100t
#
# Core: Robert Primas's official ascon-hardware-sca CryptoCore (VHDL), the
# unprotected Ascon-AEAD128 reference used for TVLA/SCA baselines. Driven by
# vivado_ascon/rtl/ascon_top.sv (port-identical adapter; the old top's wrapper
# cw305_top.v is unchanged). CryptoCore is self-contained; ascon_top.sv speaks
# its LWC BDI/BDO protocol directly, so the LWC/ wrapper files are NOT compiled.
#
# CCW=32 / CCSW=32 come from the LWC_config_ccw package (no Verilog define).
set PART xc7a100tftg256-2
set TOP  cw305_top
set PROJ_DIR [file normalize [file dirname [info script]]/vivado_ascon]
set fpga_srcs   [glob -directory [file join $PROJ_DIR fpga] *.v]
set sv_srcs     [list [file join $PROJ_DIR rtl ascon_top.sv]]
# ascon-hardware-sca VHDL, compiled leaf-first (packages before entities).
set vhd_srcs    [list \
    [file join $PROJ_DIR rtl_lwc LWC_config_32.vhd] \
    [file join $PROJ_DIR rtl_lwc LWC_config_ccw_32.vhd] \
    [file join $PROJ_DIR rtl_lwc LWC_config_ascon.vhd] \
    [file join $PROJ_DIR rtl_lwc design_pkg.vhd] \
    [file join $PROJ_DIR rtl_lwc NIST_LWAPI_pkg.vhd] \
    [file join $PROJ_DIR rtl_lwc CryptoCore.vhd] \
]
set xdc         [file join $PROJ_DIR fpga cw305.xdc]
set defs_dir    [file join $PROJ_DIR fpga]

create_project -in_memory -part $PART

# VHDL-2008: design_pkg uses unconstrained function returns (reverse_byte).
read_vhdl $vhd_srcs
set_property FILE_TYPE {VHDL 2008} [get_files {*.vhd}]

read_verilog -sv $fpga_srcs
read_verilog -sv $sv_srcs
read_xdc $xdc
set_property include_dirs [list $defs_dir [file join $PROJ_DIR rtl]] [current_fileset]

synth_design -top $TOP -part $PART
opt_design
place_design
route_design
write_bitstream -force [file join $PROJ_DIR ascon_cw305_top.bit]
write_checkpoint -force [file join $PROJ_DIR ascon_cw305_routed.dcp]
puts "=== BUILD DONE ==="
