# PRD: Werd --- WebAssembly Plugin Runtime for Python

## Overview

Werd is an open‑source WebAssembly plugin runtime for Python
applications.

It enables developers to run sandboxed plugins compiled to WebAssembly
(`.wasm`) from languages such as Rust, Go, AssemblyScript, or C while
Python remains the orchestration layer.

Werd replaces unsafe Python plugin systems with a **portable,
deterministic, sandboxed execution model**.

Python becomes the **control plane** while WebAssembly becomes the
**execution layer**.

------------------------------------------------------------------------

# Problem

Most Python extension systems rely on:

-   Python module imports
-   subprocess execution
-   Docker containers
-   custom scripting

These approaches create problems:

1.  **Security risk** --- plugins may access filesystem or network
2.  **Dependency conflicts** --- Python environments break plugins
3.  **Isolation problems** --- plugins can crash the host
4.  **Distribution issues** --- plugins are difficult to package
    reliably

------------------------------------------------------------------------

# Solution

Use WebAssembly as the plugin execution format.

Benefits:

-   language‑agnostic plugins
-   deterministic execution
-   strong sandboxing
-   portable binaries
-   reproducible environments

Werd provides:

-   runtime for executing `.wasm`
-   sandbox policy layer
-   host bindings
-   tracing and diagnostics
-   CLI tooling
-   plugin lifecycle management

------------------------------------------------------------------------

# Target Users

Primary users:

-   SaaS platform engineers
-   Python backend developers
-   developer tooling teams

Secondary users:

-   AI infrastructure teams
-   workflow engine developers
-   internal developer platform teams

------------------------------------------------------------------------

# Core Design Principle

**Python orchestrates. WASM executes.**

Python manages:

-   plugin lifecycle
-   capability policies
-   tracing and diagnostics
-   host APIs

WASM modules perform the plugin logic.

------------------------------------------------------------------------

# System Architecture

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
    | - sandbox policy          |
    | - tracing / diagnostics   |
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
    | Rust / Go / C / etc       |
    +---------------------------+

Execution Flow

    compile plugin -> load .wasm -> validate exports -> instantiate -> execute -> trace result

------------------------------------------------------------------------

# CLI Interface (Full Scope)

The **Werd CLI** allows developers to run and inspect WASM modules
without embedding the runtime in an application.

This dramatically improves developer experience and makes the project
demo‑ready.

CLI commands:

## werd run

Execute a WASM module function.

Example:

    werd run plugin.wasm --function run --input '{"name":"Sergio"}'

Features:

-   load module
-   validate export
-   execute function
-   structured JSON input/output
-   timeout enforcement
-   memory limits
-   trace logs

Extended usage:

    werd run plugin.wasm \
      --function run \
      --input '{"name":"Sergio"}' \
      --timeout-ms 200 \
      --max-memory-mb 32 \
      --trace

------------------------------------------------------------------------

## werd inspect

Inspect a WASM module without running it.

Example:

    werd inspect plugin.wasm

Output includes:

-   exports
-   imports
-   memory limits
-   tables
-   host bindings required

Example output:

    Module: plugin.wasm

    Exports:
      run(i32) -> i32

    Imports:
      host.log

    Memory:
      min: 1 page
      max: 16 pages

------------------------------------------------------------------------

## Future CLI Commands

    werd validate plugin.wasm
    werd trace plugin.wasm
    werd manifest init
    werd pack
    werd publish

------------------------------------------------------------------------

# Python Runtime API

Example usage:

``` python
from werd import Runtime

runtime = Runtime(
    max_memory_mb=32,
    timeout_ms=200
)

plugin = runtime.load("plugin.wasm")

result = plugin.call("run", {"name": "Sergio"})

print(result)
```

------------------------------------------------------------------------

# Plugin Interface

Example Rust plugin:

``` rust
#[no_mangle]
pub extern "C" fn run(input_ptr: i32) -> i32
```

------------------------------------------------------------------------

# Red‑Green TDD Development Model

Development follows strict **test‑first** methodology.

### Cycle

1.  Write failing test
2.  Implement minimal functionality
3.  Refactor

------------------------------------------------------------------------

### Example: CLI Inspect

Red

``` python
def test_inspect_lists_exports():
    result = run_cli(["inspect","fixtures/echo.wasm"])
    assert "run" in result.stdout
```

Green

Implement minimal module inspection.

Refactor

Extract parsing logic.

------------------------------------------------------------------------

### Example: CLI Run

Red

``` python
def test_run_executes_export():
    result = run_cli([
        "run",
        "fixtures/echo.wasm",
        "--function","run",
        "--input",'{"msg":"hi"}'
    ])

    assert "hi" in result.stdout
```

Green

Implement minimal runtime execution.

Refactor

Separate CLI, runtime, and sandbox logic.

------------------------------------------------------------------------

# Repository Structure

    werd/

    src/
    werd/
    runtime.py
    loader.py
    sandbox.py
    inspect.py
    cli.py
    errors.py

    tests/
    test_runtime.py
    test_cli_run.py
    test_cli_inspect.py
    test_sandbox.py

    examples/
    rust_plugin/

    docs/
    PRD.md
    ARCHITECTURE.md

    pyproject.toml
    README.md

------------------------------------------------------------------------

# Technology Stack

Language:

Python

WASM Runtime:

Wasmtime Python bindings

Testing:

pytest

Optional:

Rust utilities for example plugins

------------------------------------------------------------------------

# Implementation Phases

## Phase 1 --- Minimal Runtime

-   load `.wasm`
-   execute exported function
-   Python API

## Phase 2 --- CLI

-   `werd inspect`
-   `werd run`
-   JSON input/output

## Phase 3 --- Sandbox

-   memory limits
-   timeout limits
-   capability model

## Phase 4 --- Plugin System

-   manifests
-   plugin versioning
-   packaging tools

## Phase 5 --- Ecosystem

-   plugin registry
-   plugin marketplace
-   remote execution

------------------------------------------------------------------------

# Success Metrics

-   GitHub stars
-   adoption in Python frameworks
-   plugin ecosystem growth
-   developer contributions

------------------------------------------------------------------------

# Non Goals

-   replacing container runtimes
-   implementing a WASM compiler
