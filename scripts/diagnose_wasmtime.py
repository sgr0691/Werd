"""Print a minimal local diagnostic for wasmtime execution."""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnose local wasmtime execution with a simple WASM fixture."
    )
    parser.add_argument(
        "--module",
        default=str(Path(__file__).resolve().parents[1] / "fixtures" / "echo.wasm"),
        help="Path to the WASM module to load.",
    )
    parser.add_argument(
        "--function",
        default="run",
        help="Exported function to call.",
    )
    parser.add_argument(
        "--value",
        default=7,
        type=int,
        help="Integer value to pass to the function.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    print(f"python_executable={sys.executable}")
    print(f"python_version={sys.version.splitlines()[0]}")
    print(f"platform={platform.platform()}")
    print(f"machine={platform.machine()}")
    print(f"module_path={Path(args.module).resolve()}")
    print(f"function={args.function}")
    print(f"value={args.value}")

    try:
        import wasmtime

        print(f"wasmtime_module={wasmtime.__file__}")
        print(f"wasmtime_version={getattr(wasmtime, '__version__', 'unknown')}")

        store = wasmtime.Store()
        module = wasmtime.Module.from_file(store.engine, args.module)
        instance = wasmtime.Instance(store, module, [])
        export = instance.exports(store).get(args.function)

        if export is None:
            print("status=error")
            print("error=function not found")
            return 1

        print("status=calling")
        result = export(store, args.value)
        print("status=ok")
        print(f"result={result}")
        return 0
    except BaseException as exc:
        print("status=error")
        print(f"error_type={type(exc).__name__}")
        print(f"error={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
