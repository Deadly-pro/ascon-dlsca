#!/usr/bin/env bash
# run_pa_test.sh — Linux wrapper; delegates to the cross-platform Python
# orchestrator (single source of truth). Windows: use run_pa_test.bat.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/.venv/bin/python" "$ROOT/board_session/run_pa_test.py" "$@"
