import subprocess
import sys
import os
import json


def run_cli(args):
    """Run the werd CLI with given arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "werd.cli"] + args,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    return result


def test_inspect_lists_exports():
    """Test that inspect command lists exports from a WASM module."""
    result = run_cli(["inspect", "fixtures/echo.wasm"])

    # Should succeed
    assert result.returncode == 0

    # Should contain the export name
    assert '"name": "run"' in result.stdout

    # Should be valid JSON
    data = json.loads(result.stdout)
    assert "exports" in data
    assert len(data["exports"]) == 1
    assert data["exports"][0]["name"] == "run"
