#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ ! -x .venv/bin/python ]; then
  echo "[start.sh] .venv missing or broken. Recreate with: python3.12 -m venv .venv" >&2
  exit 1
fi

exec .venv/bin/python main.py
