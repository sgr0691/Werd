"""Command-line interface for Werd."""

import argparse
import sys
import json

from .runtime import Runtime
from .inspect import inspect_module


def main():
    parser = argparse.ArgumentParser(prog="werd")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a WASM module")
    inspect_parser.add_argument("module", help="Path to the WASM module")

    # run command
    run_parser = subparsers.add_parser("run", help="Run a WASM module function")
    run_parser.add_argument("module", help="Path to the WASM module")
    run_parser.add_argument("--function", required=True, help="Function to execute")
    run_parser.add_argument(
        "--input", required=True, help="JSON input for the function"
    )
    run_parser.add_argument(
        "--timeout-ms", type=int, default=200, help="Timeout in milliseconds"
    )
    run_parser.add_argument(
        "--max-memory-mb", type=int, default=32, help="Maximum memory in MB"
    )
    run_parser.add_argument("--trace", action="store_true", help="Enable trace output")

    args = parser.parse_args()

    if args.command == "inspect":
        result = inspect_module(args.module)
        print(json.dumps(result, indent=2))
    elif args.command == "run":
        runtime = Runtime(max_memory_mb=args.max_memory_mb, timeout_ms=args.timeout_ms)
        plugin = runtime.load(args.module)

        # Parse input JSON
        try:
            input_data = json.loads(args.input)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)

        # Execute function
        try:
            result = plugin.call(args.function, input_data)
            print(json.dumps(result))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
