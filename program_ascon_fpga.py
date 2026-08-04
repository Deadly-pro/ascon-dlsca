#!/usr/bin/env python3
"""program_ascon_fpga.py — load Ascon bitstream into CW305 FPGA over USB (volatile).

This is what you want for CAPTURE: programs the FPGA fabric directly over USB,
no SPI flash involved. Design is live immediately, gone on power-off.

Requires mode switches set to USB (M0=1 M1=1 M2=1).

Usage:
    python3 program_ascon_fpga.py [path/to/ascon_cw305_top.bit]
"""
import sys
import chipwhisperer as cw

def main():
    BIT = "/home/deadly-pro/ascon/vivado_ascon/ascon_cw305_top.bit"
    if len(sys.argv) > 1:
        BIT = sys.argv[1]

    print(f"[+] Programming FPGA over USB with {BIT} ...")
    fpga = cw.target(None, cw.targets.CW305, bsfile=BIT)
    ok = fpga.is_programmed()
    print(f"[+] is_programmed = {ok}")
    if not ok:
        print("[!] FPGA did NOT program. Check: mode switches on USB, power-cycle, USB cable.")
        sys.exit(1)
    print("[+] Ascon design is LIVE in the FPGA (volatile). Ready for capture.")
    fpga.dis()

if __name__ == "__main__":
    main()
