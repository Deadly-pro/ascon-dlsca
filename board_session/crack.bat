@echo off
REM crack.bat — MUST-crack session, no fallback. Runs the gate + config hunt.
REM Step 3 (attack) is manual after you pick the best config (see CRACK_PLAN.md).
REM Run from repo root:  board_session\crack.bat
setlocal
set ROOT=%~dp0..
cd /d "%ROOT%"
set PY=%ROOT%\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python

echo ============================================================
echo  [0/2] DEPENDENCIES  (torch needed - the attack crashed without it)
echo ============================================================
%PY% -c "import torch" 2>NUL && echo   torch OK || (
    echo   installing torch (CPU)...
    %PY% -m pip install torch --index-url https://download.pytorch.org/whl/cpu
    %PY% -c "import torch" || (echo   FAILED - check network/pip & pause & exit /b 1)
)

echo ============================================================
echo  [1/2] BOARD GATE  (verify_state 5/5 + sanity_check KAT)
echo ============================================================
%PY% verify_state.py -b vivado_ascon\ascon_cw305_top.bit -n 5
%PY% sanity_check.py -b vivado_ascon\ascon_cw305_top.bit
echo   Gate passed IF both printed PASS / 5/5 above.

echo ============================================================
echo  [2/2] CONFIG HUNT  (1000 traces each, template edge)
echo  Read each 'mean +X.XXXX nats' line. Pick the highest as best config.
echo ============================================================
echo.
echo  --- cfgA: gain 35, 10 MHz, extclk (PRIMARY - phase locked) ---
%PY% collect_dataset.py -n 1000 --samples 1200 --gain 35 --crypto-mhz 10 --extclk -o Dataset\cfgA.h5
%PY% training\template_edge.py --h5 Dataset\cfgA.h5 --n 1000 --fit-k 700
echo.
echo  --- cfgB: gain 35, 10 MHz, clkgen (baseline) ---
%PY% collect_dataset.py -n 1000 --samples 1200 --gain 35 --crypto-mhz 10 -o Dataset\cfgB.h5
%PY% training\template_edge.py --h5 Dataset\cfgB.h5 --n 1000 --fit-k 700
echo.
echo  --- cfgC: gain 35, 5 MHz, extclk (more samples/cycle) ---
%PY% collect_dataset.py -n 1000 --samples 1200 --gain 35 --crypto-mhz 5 --extclk -o Dataset\cfgC.h5
%PY% training\template_edge.py --h5 Dataset\cfgC.h5 --n 1000 --fit-k 700
echo.
echo  --- cfgD: gain 30, 10 MHz, extclk ---
%PY% collect_dataset.py -n 1000 --samples 1200 --gain 30 --crypto-mhz 10 --extclk -o Dataset\cfgD.h5
%PY% training\template_edge.py --h5 Dataset\cfgD.h5 --n 1000 --fit-k 700
echo.
echo ============================================================
echo  CONFIG HUNT DONE. Pick best config from the edges above.
echo  Now run the ATTACK from CRACK_PLAN.md (Test 2) with your choice.
echo ============================================================
pause