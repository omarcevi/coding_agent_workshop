"""Recreate workspace/ from a clean copy of demo_project/.

The agents only touch workspace/, so run this before each demo (or whenever
an agent has made a mess) to get the original buggy project back:

    uv run reset_workspace.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "demo_project"
WORKSPACE = ROOT / "workspace"

if __name__ == "__main__":
    shutil.rmtree(WORKSPACE, ignore_errors=True)
    shutil.copytree(
        SOURCE, WORKSPACE, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache")
    )
    files = sorted(p.name for p in WORKSPACE.iterdir())
    print(f"workspace/ reset from demo_project/: {', '.join(files)}")
