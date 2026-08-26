#!/usr/bin/env python3
r"""scope_config.py — device-aware scope/target setup shared by all capture scripts.

Auto-detects the capture hardware (CW-Husky vs CW-Lite/CW-Pro) and applies the
correct clock configuration, so the same script works on any setup:

* CW-Lite/CW-Pro : scope.clock.adc_src = 'clkgen_x4' (40 MS/s at clkgen 40e6)
* CW-Husky       : scope.clock.clkgen_src = 'system' + adc_mul = 1
                   (legacy adc_src='clkgen_x4' maps to adc_mul=4, giving
                   160 MS/s, which silently changes the sample window)

Also provides:

* connect_target()   : CW305 init (pll, clksettings, tio_clkout) + shallow wrapper
* configure_scope()  : samples/offset/gain/trigger + clock setup
* verify_scope()     : prints what was detected and its settings
* capture_ok()       : content-based trace sanity (std/len/clip)
* firmware_note()    : reports an outdated SAM3U firmware version if detected

Usage from any script:

    from scope_config import connect_target, configure_scope, verify_scope

    target = connect_target(args.bitstream)
    scope  = configure_scope(gain=args.gain, samples=args.samples,
                             offset=args.offset, sample_rate_hz=40e6)
    verify_scope(scope)
"""
import os
import sys

import chipwhisperer as cw

from cw305_ascon_shim import wrap

# ADC sample window defaults (matching the profiling captures)
DEFAULT_SAMPLE_RATE = 40e6       # Hz
DEFAULT_SAMPLES = 2000           # 0-50 us at 40 MHz
DEFAULT_GAIN = 20                # dB (CW305 +20 dB fixed stage assumed)

# Husky gain range is -15..+65 dB (rated); allow up to +90 for probing
# driver behavior beyond the rated maximum.
HUSKY_GAIN_MIN = -15.0
HUSKY_GAIN_MAX = 90.0
LITE_GAIN_MIN = -6.5
LITE_GAIN_MAX = 56.0


def is_husky(scope):
    """True if the given scope object is a CW-Husky (or Husky-Plus)."""
    return bool(getattr(scope, '_is_husky', False))


def scope_model_name(scope):
    """Human-readable model string for the attached scope."""
    if is_husky(scope):
        if getattr(scope, '_is_husky_plus', False):
            return 'CW-Husky Plus'
        return 'CW-Husky'
    return 'CW-Lite/CW-Pro'


def setup_scope_clock(scope, rate=DEFAULT_SAMPLE_RATE, extclk=False):
    """Point the ADC clock at `rate` Hz, correcting for the scope model.

    On a Husky the old adc_src string maps to adc_mul as a side effect; we set
    the fields explicitly so the real sample rate equals the requested one.

    extclk=True (Husky only): lock the ADC PLL onto the target's tio_clkout
    (the crypto clock) instead of the scope's own system PLL — phase-coherent
    captures, eliminates per-capture sampling-phase drift. `rate` must be an
    integer multiple of the crypto clock (10 MHz default -> adc_mul = rate/10e6).
    """
    if is_husky(scope):
        if extclk:
            crypto_hz = 10e6
            scope.clock.clkgen_src = 'extclk'
            scope.clock.clkgen_freq = crypto_hz
            scope.clock.adc_mul = int(round(rate / crypto_hz))
        else:
            scope.clock.clkgen_src = 'system'
            scope.clock.adc_mul = 1
            scope.clock.clkgen_freq = rate
    else:
        scope.clock.adc_src = 'clkgen_x4'
        scope.clock.clkgen_freq = rate
    scope.clock.reset_adc()


def setup_target_clock(target, crypto_hz=10e6):
    """Configure the CW305 PLL to feed the crypto core at `crypto_hz`."""
    target.vccint_set(1.0)
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(crypto_hz, 1)
    target.fpga_write(0x00, [0x19])   # REG_CLKSETTINGS: enable tio_clkout


def connect_target(bitstream, crypto_hz=10e6, program=True):
    """Program the CW305 and return the wrapped AsconMux handle.

    bitstream : path to the .bit file (None to skip programming)
    crypto_hz : PLL1 output frequency for the crypto core
    program   : False keeps the current FPGA configuration (no re-program)
    """
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=None if (not program or bitstream is None)
                       else bitstream,
                       fpga_id='100t', platform='cw305')
    if program and bitstream is not None:
        setup_target_clock(target, crypto_hz)
    target.clkusbautooff = True
    target.clksleeptime = 1
    t = wrap(target)
    return t


def configure_scope(gain=DEFAULT_GAIN, samples=DEFAULT_SAMPLES,
                    offset=700, sample_rate=DEFAULT_SAMPLE_RATE,
                    disable_glitch=True, extclk=False):
    """Open the scope and apply the standard capture settings.

    Returns the raw scope object. Raises RuntimeError if hardware is missing.
    """
    scope = cw.scope()
    if scope is None:
        raise RuntimeError(
            'No ChipWhisperer scope found. Check the USB connection and the '
            'udev rules (Linux) or driver (Windows).')

    # disable glitch output (it can corrupt captures if left enabled)
    if disable_glitch:
        try:
            scope.glitch.enabled = False
        except Exception:
            pass

    scope.gain.db = gain
    scope.adc.samples = samples
    scope.adc.offset = offset
    setup_scope_clock(scope, sample_rate, extclk=extclk)
    scope.trigger.triggers = 'tio4'
    return scope


def verify_scope(scope):
    """Print detected model and current scope settings (sanity helper)."""
    model = scope_model_name(scope)
    try:
        adc_freq = scope.clock.adc_freq
    except Exception:
        adc_freq = 0.0
    print(f'[+] scope      : {model}')
    print(f'[+] adc_freq   : {adc_freq/1e6 if adc_freq else 0:.1f} MHz')
    print(f'[+] samples    : {scope.adc.samples}')
    print(f'[+] offset     : {scope.adc.offset}')
    print(f'[+] gain       : {scope.gain.db:.1f} dB')
    print(f'[+] trigger    : {scope.trigger.triggers}')
    return model


def capture_ok(trace, samples, std_floor=0.001, clip_threshold=0.49):
    """Content-based trace sanity. Returns (ok, reason)."""
    if trace is None or trace.size < 64:
        return False, 'empty/short'
    if trace.size != samples:
        return False, f'len {trace.size} != {samples}'
    if not bool(trace.std() >= std_floor):
        return False, f'flat (std {trace.std():.4f} < {std_floor})'
    if float(abs(trace).max()) > clip_threshold:
        return False, f'clip (max {abs(trace).max():.4f} > {clip_threshold})'
    return True, 'ok'


def firmware_note():
    """Best-effort firmware version hint (warnings are only printed)."""
    try:
        import chipwhisperer
        return 'chipwhisperer %s' % getattr(chipwhisperer, '__version__', '?')
    except Exception:
        return 'chipwhisperer version unknown'


if __name__ == '__main__':
    print('[+] scope hardware probe')
    try:
        s = configure_scope()
        verify_scope(s)
        s.dis()
    except Exception as e:
        print(f'[!] probe failed: {e}')
        sys.exit(1)