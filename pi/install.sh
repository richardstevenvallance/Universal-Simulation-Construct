#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${DEXFORGE_DIR:-$HOME/dexforge}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi

. .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "DexForge dependencies installed."
echo "Run: cd $APP_DIR/backend && ../.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8765"
