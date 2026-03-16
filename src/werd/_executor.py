"""Isolated child-process executor for WASM function calls."""

import json
import sys

import wasmtime


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "usage: python -m werd._executor <module_path> <function_name> <params_json>",
            file=sys.stderr,
        )
        return 2

    module_path, function_name, params_json = sys.argv[1:]

    try:
        params = json.loads(params_json)
        if not isinstance(params, list):
            raise TypeError("params_json must decode to a list")

        store = wasmtime.Store()
        module = wasmtime.Module.from_file(store.engine, module_path)
        instance = wasmtime.Instance(store, module, [])

        export = instance.exports(store).get(function_name)
        if export is None:
            raise ValueError(f"Function '{function_name}' not found in module")
        if export.__class__.__name__ != "Func":
            raise TypeError(f"Export '{function_name}' is not a function")

        result = export(store, *params)
        if result is None:
            results = []
        elif isinstance(result, tuple):
            results = list(result)
        else:
            results = [result]

        print(json.dumps({"results": results}))
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
