@echo off
REM run_session.bat — Windows wrapper for the cross-platform session orchestrator.
REM Double-click this or run from cmd.exe; it finds the venv python and
REM delegates to board_session\run_session.py (single source of truth).
REM
REM Prerequisites (on the Windows endpoint):
REM   1. Python 3.10+ installed, chipwhisperer USB driver configured (Zadig)
REM   2. Repo cloned, venv made:  python -m venv .venv
REM      then: .venv\Scripts\pip install -r requirements.txt
REM   3. FPGA connected via USB, bitstream at vivado_ascon\ascon_cw305_top.bit
REM
REM Usage:
REM   double-click board_session\run_session.bat
REM   or from repo root:  board_session\run_session.bat

setlocal
set ROOT=%~dp0..
set PY=%ROOT%\.venv\Scripts\python.exe
if not exist "%PY%" (
    echo [!] .venv\Scripts\python.exe not found - trying system python
    set PY=python
)
echo [+] session orchestrator
echo [+] python: %PY%
echo [+] root:   %ROOT%
echo.
"%PY%" "%ROOT%\board_session\run_session.py"
set RC=%ERRORLEVEL%
if not "%RC%"=="0" (
    echo [!] session failed - see board_session\run_*\session.log
    pause
    exit /b %RC%
)
echo [+] session complete - see board_session\run_*\session.log
pause