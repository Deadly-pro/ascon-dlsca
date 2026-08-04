#!/usr/bin/env python3
"""program_cw305.py — program the Ascon bitstream onto the CW305 SPI flash.

No CW-Lite needed. The CW305 programs over its own USB (2b3e:c305).

Usage:
    python3 program_cw305.py [path/to/ascon_cw305_top.bit]
"""
import os
import sys
import chipwhisperer as cw

def main():
    BIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "vivado_ascon", "ascon_cw305_top.bit")
    if len(sys.argv) > 1:
        BIT = sys.argv[1]

    print("[!] MODE SWITCHES must be set to USB (M0=1 M1=1 M2=1) for the shim to load.")
    print("[!] After programming, flip to SPI (M0=1 M1=0 M2=0) and power-cycle to boot from flash.")
    print("[+] Opening CW305 target (own USB, no capture scope needed) ...")
    # fpga_id programs the SPI-flash passthrough bitstream, which spi_mode()
    # needs in order to reach the SPI flash through the FPGA.
    fpga = cw.target(None, cw.targets.CW305, fpga_id='100t')  # for CW305_100t

    print(f"[+] Programming SPI flash with {BIT} ...")
    spi = fpga.spi_mode()     # loads passthrough bitstream, returns FPGASPI object
    spi.erase_chip(timeout=120000)  # wipes the whole flash (~25-50s); error out instead of hanging forever
    with open(BIT, 'rb') as f:
        data = list(f.read())
    spi.program(data)         # also verifies by default

    print("[+] PROGRAMMED OK — Ascon bitstream stored in SPI flash (loads at power-on)")
    fpga.dis()

if __name__ == "__main__":
    main()
