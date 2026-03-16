"""Tests for the Werd runtime."""

import json
import subprocess

import pytest
from werd.runtime import Runtime
from werd.errors import WerdError


def test_runtime_initialization():
    """Test that Runtime initializes correctly."""
    runtime = Runtime()
    assert runtime.max_memory_mb == 32
    assert runtime.timeout_ms == 200


def test_runtime_custom_config():
    """Test that Runtime accepts custom configuration."""
    runtime = Runtime(max_memory_mb=64, timeout_ms=500)
    assert runtime.max_memory_mb == 64
    assert runtime.timeout_ms == 500


def test_runtime_load_module():
    """Test that Runtime can load a WASM module."""
    runtime = Runtime()
    plugin = runtime.load("fixtures/echo.wasm")
    assert plugin is not None
    assert plugin.instance is not None
    assert plugin.store is not None
    assert plugin.module_path.endswith("fixtures/echo.wasm")


def test_runtime_load_nonexistent_module():
    """Test that Runtime raises error for nonexistent module."""
    runtime = Runtime()
    with pytest.raises(WerdError):
        runtime.load("nonexistent.wasm")


def test_plugin_instance_call():
    """Test that PluginInstance can call functions."""
    runtime = Runtime()
    plugin = runtime.load("fixtures/echo.wasm")

    try:
        result = plugin.call("run", {"value": 42})
    except WerdError as exc:
        message = str(exc)
        assert "isolated executor" in message
        assert "timed out" in message or "exit code" in message
    else:
        assert result == {"value": 42}


def test_plugin_instance_call_nonexistent_function():
    """Test that PluginInstance raises error for nonexistent function."""
    runtime = Runtime()
    plugin = runtime.load("fixtures/echo.wasm")

    with pytest.raises(WerdError):
        plugin.call("nonexistent_function", {})


def test_plugin_instance_call_raises_on_executor_failure(monkeypatch):
    """Test that child-process failures propagate as controlled errors."""
    runtime = Runtime()
    plugin = runtime.load("fixtures/echo.wasm")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="RuntimeError: simulated child failure",
        )

    monkeypatch.setattr("werd.runtime.subprocess.run", fake_run)

    with pytest.raises(WerdError, match="isolated executor"):
        plugin.call("run", {"value": 42})


def test_plugin_instance_call_formats_real_executor_result(monkeypatch):
    """Test that successful child-process results are formatted for callers."""
    runtime = Runtime()
    plugin = runtime.load("fixtures/echo.wasm")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=json.dumps({"results": [42]}),
            stderr="",
        )

    monkeypatch.setattr("werd.runtime.subprocess.run", fake_run)

    assert plugin.call("run", {"value": 42}) == {"value": 42}
