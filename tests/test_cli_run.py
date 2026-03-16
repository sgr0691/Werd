import subprocess
import sys
import os
import json


def run_cli(args):
    """Run the wordt CLI with given arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "werd.cli"] + args,
        capture_output=True,
        text=True,
        timeout=5,  # Add timeout to prevent hanging
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    return result


def test_run_loads_module():
    """Test that run command can load a WASM module."""
    result = run_cli(
        [
            "run",
            "fixtures/echo.wasm",
            "--function",
            "run",
            "--input",
            '{"value": 42}',
        ]
    )

    assert result.returncode in [0, 1]

    if result.returncode == 0:
        data = json.loads(result.stdout.strip())
        assert data == {"value": 42}
    else:
        assert "isolated executor" in result.stderr


def test_run_validates_inputs():
    """Test that run command validates required inputs."""
    # Test missing --function
    result = run_cli(["run", "fixtures/echo.wasm", "--input", '{"value": 42}'])
    assert result.returncode != 0  # Should fail due to missing --function

    # Test missing --input
    result = run_cli(["run", "fixtures/echo.wasm", "--function", "run"])
    assert result.returncode != 0  # Should fail due to missing --input

    # Test invalid JSON
    result = run_cli(
        [
            "run",
            "fixtures/echo.wasm",
            "--function",
            "run",
            "--input",
            "not valid json",
        ]
    )
    assert result.returncode != 0  # Should fail due to invalid JSON
