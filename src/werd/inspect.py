"""Inspect WASM modules."""

import wasmtime
from typing import Dict, Any, List


def inspect_module(path: str) -> Dict[str, Any]:
    """Inspect a WASM module and return information about it."""
    engine = wasmtime.Engine()
    module = wasmtime.Module.from_file(engine, path)

    # Get imports
    imports = []
    for imp in module.imports:
        # Determine kind from the type of imp.type
        type_class_name = imp.type.__class__.__name__
        kind_map = {
            "FuncType": "func",
            "MemoryType": "memory",
            "TableType": "table",
            "GlobalType": "global",
        }
        kind = kind_map.get(
            type_class_name, type_class_name.lower().replace("type", "")
        )

        imports.append(
            {
                "module": imp.module,
                "name": imp.name,
                "kind": kind,
            }
        )

    # Get exports
    exports = []
    for exp in module.exports:
        # Determine kind from the type of exp.type
        type_class_name = exp.type.__class__.__name__
        kind_map = {
            "FuncType": "func",
            "MemoryType": "memory",
            "TableType": "table",
            "GlobalType": "global",
        }
        kind = kind_map.get(
            type_class_name, type_class_name.lower().replace("type", "")
        )

        exports.append(
            {
                "name": exp.name,
                "kind": kind,
                "type": str(exp.type),
            }
        )

    # Get memory info
    memories = []
    # Check exports for memories since newer wasmtime doesn't expose memories directly on module
    for exp in module.exports:
        if exp.type.__class__.__name__ == "MemoryType":
            memtype = exp.type
            memories.append(
                {
                    "min": memtype.min,
                    "max": memtype.max
                    if memtype.max != wasmtime.Limits.U64_MAX
                    else None,
                }
            )

    # Get table info
    tables = []
    # Check exports for tables
    for exp in module.exports:
        if exp.type.__class__.__name__ == "TableType":
            tabtype = exp.type
            tables.append(
                {
                    "element": tabtype.element.name,
                    "min": tabtype.min,
                    "max": tabtype.max
                    if tabtype.max != wasmtime.Limits.U64_MAX
                    else None,
                }
            )

    return {
        "module": path,
        "imports": imports,
        "exports": exports,
        "memories": memories,
        "tables": tables,
    }
