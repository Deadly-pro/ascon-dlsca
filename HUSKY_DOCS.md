# CW-Husky Reference — ADC/Clock/Trigger Details

Technical reference for the ChipWhisperer-Husky capture board as used in this
project. The operational runbook with commands lives in `HUSKY_SETUP.md`.

## Product summary

- Successor to the CW1173 ChipWhisperer-Lite
- 12-bit 200 MS/s ADC (Husky Plus: 250 MS/s)
- Clock generation range 5-200 MHz
- Gain -6.5 dB to +55 dB (software-controllable; this project uses the CW305
  +20 dB fixed stage plus programmable gain)
- Sample buffer 131124 samples (Husky Plus: 327828)
- USB 2.0, VID 0x2B3E, PID 0xACE5
- ADC offset adjustment [0, 2^32) clock cycles
- Trigger modules: Basic (rising/falling/high/low), Analog threshold, SAD
  (sum of absolute differences), UART, Edge count, Arm Trace, sequenced
- Presampling and phase adjustment supported

## ADC clock config (critical)

On the Husky the ADC clock is set via three fields:

```python
scope.clock.clkgen_src   # 'system' (internal PLL) or 'extclk' (external)
scope.clock.adc_mul      # 1 or 4 (ADC clock multiplier)
scope.clock.clkgen_freq  # PLL output frequency, Hz
```

Actual ADC sample rate = `clkgen_freq * adc_mul`.

The old CW-Lite style `scope.clock.adc_src = 'clkgen_x4'` is accepted for
backwards compatibility but maps to `adc_mul = 4`:

| Setting | Resulting sample rate | Effect |
|---------|----------------------|--------|
| `adc_src='clkgen_x4'` + `clkgen_freq=40e6` | 160 MS/s | Wrong for this project |
| `clkgen_src='system'` + `adc_mul=1` + `clkgen_freq=40e6` | 40 MS/s | Correct |

The pipeline (all captures, all profiles) is built around 40 MS/s, so every
script calls `scope_config.setup_scope_clock()` which sets the fields
explicitly.

## Triggering

Basic trigger inputs: TIO1-4, nRST, SMB, User IO D0-7

For this project the CW305 asserts a trigger on TIO4 when the crypto core
starts. Set:

```python
scope.trigger.module = 'basic'
scope.trigger.triggers = 'tio4'
```

Captures still come back valid when the trigger times out (`ret=False`):
the trace contains the operation, just at an arbitrary offset. The pipeline
aligns traces by software cross-correlation in `preprocess.py`, so timeout
captures are usable. This is by design and handled automatically.

## Firmware

The SAM3U firmware on the Husky is not auto-updated. A warning in the logs

```
Your firmware (0.51.0) is outdated - latest is 0.53.0
```

is informational. Update it once per machine with:

```python
import chipwhisperer as cw
cw.update_firmware('husky')   # or 'cwhuskyplus' on a Husky Plus
```

Then unplug and replug the USB-C cable.

## Connecting the CW305

- 20-pin ribbon: CW305 -> Husky (carries TIO4 trigger, tio_clkout, and the
  analog power trace)
- CW305 USB: dedicated USB-A/Type-B cable to the PC (FPGA programming +
  register control)
- Husky USB-C: to the PC (ADC capture)

No SMA cables required.

## Scope detection in code

`scope_config.is_husky(scope)` checks the `_is_husky` attribute. All capture
scripts call the shared helpers so the code base runs identically on a
CW-Lite, CW-Husky, or CW-Husky Plus.