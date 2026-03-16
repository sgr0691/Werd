"""Load and validate WASM modules."""

import wasmtime
from typing import Any


def load_wasm_module(path: str) -> wasmtime.Store:
    """Load a WASM module from the given path."""
    store = wasmtime.Store()
    module = wasmtime.Module.from_file(store.engine, path)
    return wasmtime.Instance(store, module, [])
