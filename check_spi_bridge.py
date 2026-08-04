#!/usr/bin/env python3
"""check_spi_bridge.py — sanity-check the CW305 SPI bridge BEFORE a full erase+program.

If the SPI link is dead, program_cw305.py wastes a ~25s erase + verify cycle
and fails. This reads 16 bytes from flash addr 0 and just reports what came back.

Usage:
    python3 check_spi_bridge.py

Expectations:
    [255, 255, ...]         -> bridge alive, flash erased/empty -> proceed to program
    any non-zero/real data  -> bridge alive, flash has old data -> proceed
    [0, 0, 0, ...]          -> bridge dead (MISO stuck low) -> power-cycle / firmware, DON'T program yet
"""
import chipwhisperer as cw

fpga = cw.target(None, cw.targets.CW305, fpga_id='100t')
spi = fpga.spi_mode()
data = spi.read(16, 0)
print("Flash[0:16] =", data)
print("ALL_ZEROS:  ", all(b == 0 for b in data))
print("ERASED(FF): ", all(b == 0xFF for b in data))
fpga.dis()
