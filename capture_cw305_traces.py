#!/usr/bin/env python3
"""
capture_cw305_traces.py — capture an Ascon power-trace dataset from CW305 + CW-Lite.

Flow (CW305 register API — no SimpleSerial needed):
    loadEncryptionKey(key) -> loadInput(nonce) -> scope.arm() -> go() (triggers tio4)
    -> scope.capture() -> wait is_done() -> readOutput() -> save under Dataset/

Inputs are loaded BEFORE scope.arm() so the ADC trigger window stays in lockstep
with the op being sent/received (USB register writes take variable ms).

Ascon core (vivado_ascon/src/ascon_cw305_core.v): encrypts key+nonce (fixed zero
plaintext), outputs {tag[95:0], ciphertext[31:0]}; tio_trigger is high for the
whole (long, bit-serial) operation, so ADC samples must be sized to cover it.

Usage:
    # 1) quick validation + tune ADC samples (watch for trigger timeouts):
    python3 capture_cw305_traces.py -n 20 -s 20000
    # 2) full dataset:
    python3 capture_cw305_traces.py -n 1000 -s 25000
"""
import argparse
import os
import time
import h5py
import numpy as np
import chipwhisperer as cw

BIT = "/home/deadly-pro/ascon/vivado_ascon/ascon_cw305_top.bit"


def _drain(target, timeout=1.0):
    """Wait for the FPGA op to finish so tio_trigger deasserts before the next
    arm(). Needed even when the scope missed the trigger - the op already ran
    and a lingering high trigger would misalign/offset the next trace."""
    t0 = time.time()
    while not target.is_done() and time.time() - t0 < timeout:
        time.sleep(0.001)
    return target.is_done()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-n', '--num', type=int, default=1000, help='number of traces')
    ap.add_argument('-s', '--samples', type=int, default=20000,
                    help='ADC samples per trace (Ascon bit-serial core needs thousands)')
    ap.add_argument('-b', '--bitstream', default=BIT)
    ap.add_argument('-o', '--outdir', default='Dataset')
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    outfile = os.path.join(args.outdir, 'ascon_dataset.h5')

    # ---- scope (CW-Lite ADC) ----
    scope = cw.scope()
    scope.default_setup()
    scope.gain.db = 25
    scope.adc.samples = args.samples
    scope.adc.offset = 0
    scope.adc.basic_mode = "rising_edge"
    scope.trigger.triggers = "tio4"          # CW305 tio_trigger -> CW-Lite tio4
    scope.io.tio1 = "serial_rx"
    scope.io.tio2 = "serial_tx"
    scope.io.hs2 = "disabled"

    # ---- CW305 target: program bitstream + configure PLL/crypto clock ----
    target = cw.target(scope, cw.targets.CW305, force=True,
                       bsfile=args.bitstream, fpga_id='100t', platform='cw305')
    target.vccint_set(1.0)
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)    # crypto clock out -> pll_clk1
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(10e6, 1)      # 10 MHz crypto clock
    target.clkusbautooff = True              # drop USB clock noise during capture
    target.clksleeptime = 1

    # ADC clocked off the FPGA's crypto clock (4x oversample), must lock
    scope.clock.adc_src = "extclk_x4"
    for _ in range(5):
        scope.clock.reset_adc()
        time.sleep(1)
        if scope.clock.adc_locked:
            break
    assert scope.clock.adc_locked, \
        "ADC failed to lock - check tio_clkout/clock DIP switch (K16) and PLL"

    print(f"[+] Capturing {args.num} traces x {args.samples} samples -> {outfile}")

    traces, keys, nonces, cts = [], [], [], []
    for i in range(args.num):
        key = os.urandom(16)
        nonce = os.urandom(16)

        # Load ALL inputs BEFORE arming: USB register writes take variable ms,
        # so arm only once the FPGA is idle and inputs are latched. This keeps
        # the ADC trigger window in lockstep with the op being sent/received.
        target.loadEncryptionKey(key)
        target.loadInput(nonce)
        scope.arm()
        target.go()                       # pulses trigger; tio4 -> scope
        ret = scope.capture()
        if ret:
            print(f"    trace {i}: trigger timeout, skipping")
            _drain(target)
            continue

        t0 = time.time()
        while not target.is_done() and time.time() - t0 < 1.0:
            time.sleep(0.001)
        if not target.is_done():
            print(f"    trace {i}: FPGA still busy, skipping")
            continue
        ct = bytes(target.readOutput())

        traces.append(scope.get_last_trace())
        keys.append(key)
        nonces.append(nonce)
        cts.append(ct)

        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{args.num}")

    tr = np.array(traces, dtype=np.float32)
    with h5py.File(outfile, 'w') as f:
        f.create_dataset('traces', data=tr, compression='gzip')
        f.create_dataset('keys', data=np.frombuffer(b''.join(keys), np.uint8).reshape(-1, 16))
        f.create_dataset('nonces', data=np.frombuffer(b''.join(nonces), np.uint8).reshape(-1, 16))
        f.create_dataset('ciphertexts', data=np.frombuffer(b''.join(cts), np.uint8).reshape(-1, 16))
        f.attrs['adc_samples'] = args.samples
    print(f"[+] Saved {tr.shape[0]} traces -> {outfile}")

    target.dis()
    scope.dis()


if __name__ == '__main__':
    main()
