# Werd

**Run sandboxed WebAssembly plugins in Python.**

Werd is an open-source Python-first runtime for loading and executing WebAssembly (`.wasm`) modules as portable, sandboxed plugins.

It gives Python applications a safer extension model than raw Python plugins by making Python the **control plane** and WebAssembly the **execution layer**.

Current status: module loading and inspection work in-process. Function execution is attempted in an isolated child process so `wasmtime` crashes or hangs fail closed instead of returning fabricated results.

Recommended local environment: Python 3.11 or newer. On this repository, `wasmtime 42.0.0` failed under Apple-provided Python 3.9.6 on macOS 15.7.3 but succeeded under Homebrew Python 3.11.14 on the same machine. This points to a local Python runtime issue, not a macOS 15.7.3 issue.

## Local Setup

```bash
./scripts/bootstrap_py311.sh
.venv-py311/bin/python -m pytest -q
.venv-py311/bin/python -m werd.cli run fixtures/echo.wasm --function run --input '{"value": 42}'
```

Verified result on this machine:

```text
18 passed in 0.57s
{"value": 42}
```

---

## Why Werd?

Most Python plugin systems rely on one of these approaches:

- importing Python modules directly
- spawning subprocesses
- running sidecar containers
- evaluating custom scripts

Those options can create real problems:

- plugins can access more than they should
- dependency conflicts are common
- extension environments are hard to reproduce
- isolation is weak or inconsistent

Werd solves that by letting plugin authors ship a `.wasm` module and letting host applications execute it inside a constrained runtime.

---

## What Werd is for

Werd is a good fit for:

- SaaS apps with customer-defined logic
- workflow engines with portable transform steps
- internal tools with safe extensions
- AI systems that need constrained execution
- developer platforms that want a plugin model without exposing the host process

---

## Core idea

**Python orchestrates. WASM executes.**

That means:

- Python handles loading, registration, policies, tracing, and host APIs
- WebAssembly modules handle the plugin logic itself
- The host can enforce time, memory, and capability constraints around plugin execution

---

## Architecture

```text
+---------------------------+
| Python Application        |
| - business logic          |
| - orchestration           |
| - host APIs               |
+-------------+-------------+
              |
              v
+---------------------------+
| Werd Runtime              |
| - module loader           |
| - plugin manager          |
| - capability checks       |
| - tracing / diagnostics   |
| - sandbox policy          |
+-------------+-------------+
              |
              v
+---------------------------+
| WASM Engine               |
| - instantiate module      |
| - call exported funcs     |
| - manage memory           |
| - enforce limits          |
+-------------+-------------+
              |
              v
+---------------------------+
| WASM Plugin Module        |
| - Rust / Go / C / etc.    |
| - exported entrypoints    |
| - deterministic logic     |
+---------------------------+
```

### Execution flow

```text
compile plugin -> load .wasm -> validate exports -> instantiate -> execute -> trace result
```

---

## Planned CLI

The Werd CLI is meant to make the runtime useful before users even embed it in their own Python app.

### `werd run`

Runs a WASM plugin entrypoint with structured input.

Example:

```bash
werd run plugin.wasm --function run --input '{"name":"Sergio"}'
```

Recommended local check:

```bash
.venv-py311/bin/python scripts/diagnose_wasmtime.py
```

What it should do:

- load a `.wasm` file
- validate the requested export exists
- execute the function
- return structured output
- surface runtime errors clearly
- optionally enforce time and memory limits

Current limitation:

- execution may fail on some local `macOS` / Python / `wasmtime` combinations
- when that happens, `werd run` returns a controlled runtime error from the isolated executor
- Werd does not simulate guest output anymore

Expected future flags:

```bash
werd run plugin.wasm \
  --function run \
  --input '{"name":"Sergio"}' \
  --timeout-ms 200 \
  --max-memory-mb 32 \
  --trace
```

### `werd inspect`

Inspects a WASM module without running it.

Example:

```bash
werd inspect plugin.wasm
```

What it should show:

- module imports
- module exports
- memory/table definitions
- manifest metadata if present
- hints about compatibility

Example output shape:

```text
Module: plugin.wasm
Exports:
  - run(i32) -> i32
Imports:
  - host.log
Memory:
  - min: 1 page
  - max: 16 pages
```

### Nice later CLI additions

```bash
werd validate plugin.wasm
werd trace plugin.wasm --function run --input '{"x":1}'
werd manifest init
werd pack
```

A practical first CLI scope is just:

- `werd run`
- `werd inspect`

That is enough to make the project feel real and demoable.

---

## Developer experience goals

Werd should feel like this:

```python
from werd import Runtime

runtime = Runtime(
    max_memory_mb=32,
    timeout_ms=200,
)

plugin = runtime.load("plugin.wasm")
result = plugin.call("run", {"name": "Sergio"})

print(result)
```

---

## Proposed repository structure

```text
werd/
âââ src/
â   âââ werd/
â       âââ __init__.py
â       âââ runtime.py
â       âââ loader.py
â       âââ sandbox.py
â       âââ inspect.py
â       âââ cli.py
â       âââ errors.py
âââ tests/
â   âââ test_runtime.py
â   âââ test_cli_run.py
â   âââ test_cli_inspect.py
â   âââ test_sandbox.py
âââ examples/
â   âââ rust_plugin/
âââ docs/
â   âââ PRD.md
â   âââ ARCHITECTURE.md
âââ pyproject.toml
âââ README.md
```

---

## MVP roadmap

### Phase 1: Minimal runtime
- load `.wasm`
- call exported functions
- minimal Python API
- basic runtime errors

### Phase 2: CLI
- `werd run`
- `werd inspect`
- JSON input and output
- useful terminal formatting

### Phase 3: sandbox controls
- timeout budget
- memory limits
- capability model
- trace output

### Phase 4: plugin system
- manifests
- versioning
- packaging
- richer host bindings

---

## Red-green TDD development style

Werd should be built test-first.

### Example for `werd inspect`

**Red**

Write a failing test:

```python
def test_inspect_lists_exports():
    result = run_cli(["inspect", "fixtures/echo.wasm"])
    assert "run" in result.stdout
```

**Green**

Implement the smallest possible inspection command that prints exports.

**Refactor**

Extract module parsing and formatting into reusable units.

### Example for `werd run`

**Red**

```python
def test_run_executes_exported_function():
    result = run_cli([
        "run",
        "fixtures/echo.wasm",
        "--function", "run",
        "--input", '{"msg":"hi"}',
    ])
    assert '"hi"' in result.stdout
```

**Green**

Implement the minimal runtime path to load the file and execute the function.

**Refactor**

Separate:
- argument parsing
- runtime setup
- module execution
- output formatting

---

## First commands to implement

### 1. Inspect a module

```bash
werd inspect examples/rust_plugin/plugin.wasm
```

### 2. Run a plugin function

```bash
werd run examples/rust_plugin/plugin.wasm --function run --input '{"value": 2}'
```

---

## Example positioning

> Werd is a Python runtime and CLI for executing WebAssembly plugins safely inside applications.

Or more simply:

> Portable, sandboxed extensions for Python apps.

---

## Status

Werd is currently in the design / early build stage.

The recommended first milestone is:

1. runtime loader
2. `werd inspect`
3. `werd run`
4. one Rust example plugin
5. end-to-end tests

---

## License

MIT
