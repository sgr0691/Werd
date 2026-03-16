"""Werd runtime for executing WASM modules."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Union

import wasmtime

from .errors import WerdError


class Runtime:
    """Main Werd runtime class."""

    def __init__(self, max_memory_mb: int = 32, timeout_ms: int = 200):
        """Initialize the runtime with limits.

        Args:
            max_memory_mb: Maximum memory in MB for WASM module
            timeout_ms: Timeout in milliseconds for execution
        """
        self.max_memory_mb = max_memory_mb
        self.timeout_ms = timeout_ms

        # Configure engine
        # Note: fuel consumption can cause hangs in some wasmtime versions
        # We'll create a simple engine for now
        config = wasmtime.Config()
        self.engine = wasmtime.Engine(config)

    def load(self, path: str) -> "PluginInstance":
        """Load a WASM module from the given path.

        Args:
            path: Path to the WASM module

        Returns:
            PluginInstance for interacting with the loaded module
        """
        try:
            resolved_path = str(Path(path).resolve())
            store = wasmtime.Store(self.engine)
            module = wasmtime.Module.from_file(self.engine, resolved_path)
            instance = wasmtime.Instance(store, module, [])
            return PluginInstance(
                instance=instance,
                store=store,
                module=module,
                module_path=resolved_path,
                timeout_ms=self.timeout_ms,
            )
        except Exception as e:
            raise WerdError(f"Failed to load WASM module: {e}")


class PluginInstance:
    """Instance of a loaded WASM plugin."""

    def __init__(
        self,
        instance: wasmtime.Instance,
        store: wasmtime.Store,
        module: wasmtime.Module,
        module_path: str,
        timeout_ms: int,
    ):
        """Initialize plugin instance.

        Args:
            instance: Wasmtime instance
            store: Wasmtime store
            module: Wasmtime module
        """
        self.instance = instance
        self.store = store
        self.module = module
        self.module_path = module_path
        self.timeout_ms = timeout_ms

    def call(self, function_name: str, input_data: Union[Dict[str, Any], Any]) -> Any:
        """Call an exported function on the plugin.

        Args:
            function_name: Name of the function to call
            input_data: Input data to pass to the function

        Returns:
            Output from the function

        Note:
            Function execution is isolated in a subprocess so hangs or crashes in
            the `wasmtime` Python bindings cannot wedge the parent process.
        """
        try:
            export = self.instance.exports(self.store).get(function_name)
            if not export:
                raise WerdError(f"Function '{function_name}' not found in module")

            if export.__class__.__name__ != "Func":
                raise WerdError(f"Export '{function_name}' is not a function")

            func_type = export.type(self.store)
            params, response_shape = _marshal_input(input_data, func_type.params)
            results = _execute_in_subprocess(
                module_path=self.module_path,
                function_name=function_name,
                params=params,
                timeout_ms=self.timeout_ms,
            )
            return _format_output(results, response_shape, func_type.results)

        except Exception as e:
            if isinstance(e, WerdError):
                raise
            raise WerdError(f"Failed to call function '{function_name}': {e}")


def _marshal_input(input_data: Union[Dict[str, Any], Any], param_types: List[Any]):
    """Convert Python input into positional WASM params."""
    if not param_types:
        if input_data in (None, {}, []):
            return [], {"kind": "none"}
        raise WerdError("Function takes no parameters")

    if len(param_types) == 1:
        if isinstance(input_data, dict):
            if len(input_data) != 1:
                raise WerdError(
                    "Single-parameter functions require exactly one input field"
                )
            key, value = next(iter(input_data.items()))
            return [_coerce_value(value, param_types[0])], {
                "kind": "single_field_dict",
                "key": key,
            }

        return [_coerce_value(input_data, param_types[0])], {"kind": "scalar"}

    if not isinstance(input_data, list):
        raise WerdError("Multi-parameter functions require a JSON array input")

    if len(input_data) != len(param_types):
        raise WerdError(
            f"Expected {len(param_types)} parameters but received {len(input_data)}"
        )

    params = [
        _coerce_value(value, param_type)
        for value, param_type in zip(input_data, param_types)
    ]
    return params, {"kind": "list"}


def _coerce_value(value: Any, param_type: Any) -> Any:
    """Coerce a JSON value into a simple WASM scalar."""
    wasm_type = str(param_type)
    if wasm_type in {"i32", "i64"}:
        if isinstance(value, bool) or not isinstance(value, int):
            raise WerdError(f"Expected integer for {wasm_type} parameter")
        return value
    if wasm_type in {"f32", "f64"}:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise WerdError(f"Expected number for {wasm_type} parameter")
        return value
    raise WerdError(f"Unsupported WASM parameter type: {wasm_type}")


def _execute_in_subprocess(
    module_path: str, function_name: str, params: List[Any], timeout_ms: int
) -> List[Any]:
    """Execute the WASM function in a child Python process."""
    timeout_s = max(timeout_ms / 1000, 0.1)
    payload = json.dumps(params)
    cmd = [sys.executable, "-m", "werd._executor", module_path, function_name, payload]

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as exc:
        raise WerdError(
            f"WASM execution timed out after {timeout_ms}ms in isolated executor"
        ) from exc

    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        detail = stderr or stdout or "no diagnostic output"
        raise WerdError(
            "WASM execution failed in isolated executor "
            f"(exit code {completed.returncode}): {detail}"
        )

    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise WerdError("Executor returned invalid JSON output") from exc

    if "results" not in response or not isinstance(response["results"], list):
        raise WerdError("Executor response is missing a valid results payload")

    return response["results"]


def _format_output(results: List[Any], response_shape: Dict[str, Any], result_types: List[Any]):
    """Convert positional WASM results back to the public Python shape."""
    if len(results) != len(result_types):
        raise WerdError(
            f"Expected {len(result_types)} result values but received {len(results)}"
        )

    if not results:
        return None

    if response_shape["kind"] == "single_field_dict" and len(results) == 1:
        return {response_shape["key"]: results[0]}

    if len(results) == 1:
        return results[0]

    return results
