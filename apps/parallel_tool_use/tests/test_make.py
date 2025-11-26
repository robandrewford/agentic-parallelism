import os
import subprocess
import pytest

# Helper to run a make target
def run_make(target: str):
    # Two levels up: apps/parallel_tool_use/tests -> repo root
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    result = subprocess.run(
        ["make", target],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result

# List of safe make targets to test
SAFE_TARGETS = [
    "env-setup",
    "install-deps",
    "test-unit",
]

@pytest.mark.parametrize("target", SAFE_TARGETS)
def test_make_target_success(target):
    """Run each make target and ensure it exits with code 0."""
    result = run_make(target)
    print(f"\n--- make {target} ---")
    print("stdout:\n", result.stdout)
    print("stderr:\n", result.stderr)
    assert result.returncode == 0, f"make {target} failed with exit code {result.returncode}"

def test_makefile_contains_targets():
    """Verify that each safe target is defined in the Makefile."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    makefile_path = os.path.join(repo_root, "Makefile")
    with open(makefile_path, "r") as f:
        content = f.read()
    missing = [t for t in SAFE_TARGETS if f"{t}:" not in content]
    assert not missing, f"Missing targets in Makefile: {', '.join(missing)}"
