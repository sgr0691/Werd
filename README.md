# Werd

Run sandboxed WebAssembly plugins from Python.

Werd is a small Python-first runtime for loading `.wasm` modules, inspecting their exports, and calling plugin entrypoints through a constrained execution path.

## Current Status

- Module loading works.
- Module inspection works.
- Function execution is isolated in a child process so `wasmtime` hangs or crashes fail closed.
- Use Python `3.11+` locally. On this repo, Apple Python `3.9.6` failed while Homebrew Python `3.11.14` worked on the same macOS `15.7.3` machine.

## Local Setup

```bash
./scripts/bootstrap_py311.sh
.venv-py311/bin/python -m pytest -q
```

## Quick Run

```bash
.venv-py311/bin/python -m werd.cli run fixtures/echo.wasm --function run --input '{"value": 42}'
.venv-py311/bin/python -m werd.cli inspect fixtures/echo.wasm
.venv-py311/bin/python scripts/diagnose_wasmtime.py
```

Expected working result for the echo fixture:

```text
{"value": 42}
```

## Python API

```python
from werd.runtime import Runtime

runtime = Runtime(timeout_ms=200, max_memory_mb=32)
plugin = runtime.load("fixtures/echo.wasm")
result = plugin.call("run", {"value": 42})

print(result)
```

## Important Limitation

Execution still depends on the local Python and `wasmtime` combination. If a call cannot execute safely, Werd returns a controlled runtime error instead of faking a guest result.
