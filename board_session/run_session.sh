#!/usr/bin/env bash
# run_session.sh — Linux wrapper; delegates to the cross-platform Python
# orchestrator (single source of truth). Windows: use run_session.bat.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/.venv/bin/python" "$ROOT/board_session/run_session.py" "$@"