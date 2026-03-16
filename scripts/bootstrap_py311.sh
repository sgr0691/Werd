#!/bin/sh

set -eu

if [ ! -x /opt/homebrew/bin/python3.11 ]; then
  echo "Missing /opt/homebrew/bin/python3.11" >&2
  exit 1
fi

/opt/homebrew/bin/python3.11 -m venv .venv-py311
.venv-py311/bin/python -m pip install --upgrade pip
.venv-py311/bin/python -m pip install -e ".[dev]"
