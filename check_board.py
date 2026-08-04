#!/usr/bin/env python3
"""Diagnostic: check CW305 board connection and FPGA state."""
import sys
import traceback

def main():
    print("=== CW305 Board Diagnostic ===")
    print("Python:", sys.version.split()[0])

    import chipwhisperer as cw
    print("ChipWhisperer version:", getattr(cw, "__version__", "unknown"))

    # 1. Connect scope
    print("\n[1] Connecting scope...")
    scope = cw.scope()
    print("Scope connected:", scope)

    # 2. Connect CW305 target
    print("\n[2] Connecting CW305 target...")
    target = cw.target(scope, cw.targets.CW305)
    print("Target connected:", target)

    # 3. Check FPGA
    print("\n[3] Checking FPGA...")
    fpga = target.fpga
    fpga_id = fpga.fpga_id()
    print("FPGA ID:", fpga_id)

    # 4. Read FPGA config info
    try:
        dnas = fpga.read_dna()
        print("FPGA DNA:", hex(dnas) if dnas else "N/A")
    except Exception as e:
        print("DNA read failed:", e)

    try:
        cd = fpga.fpga_read_ver()
        print("FPGA read ver:", cd)
    except Exception as e:
        print("read_ver failed:", e)

    # 5. Check PLL state
    print("\n[4] Checking PLLs...")
    for i in range(3):
        try:
            en = target.pll.pll_enabled(i)
            print(f"  PLL{i} enabled:", en)
        except Exception as e:
            print(f"  PLL{i} check failed:", e)

    # 6. Close cleanly
    print("\n[5] Disconnecting...")
    target.dis()
    scope.dis()
    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FATAL:", e)
        traceback.print_exc()
