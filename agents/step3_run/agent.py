"""Step 3: close the loop. The agent can run code and see what happened.

With file tools alone the agent edits code and hopes. With run_command it
can run the tests, read the failures, fix, and run them again. That loop is
what makes it a coding agent. ADK runs the loop for you: call the model, run
the tool it asks for, send back the result, repeat until it answers in text.

Try: "The tests are failing. Fix them."
"""

import subprocess
from pathlib import Path

from google.adk.agents import Agent

# The folder the agent works in. Recreate it with: uv run reset_workspace.py
WORKSPACE = Path(__file__).resolve().parents[2] / "workspace"
SKIP = {"__pycache__", ".pytest_cache"}


def list_files() -> dict:
    """Lists every file in the project, as paths relative to the project root."""
    files = [
        str(p.relative_to(WORKSPACE))
        for p in sorted(WORKSPACE.rglob("*"))
        if p.is_file() and not SKIP & set(p.parts)
    ]
    return {"files": files}


def read_file(path: str) -> dict:
    """Reads a text file from the project.

    Args:
        path: File path relative to the project root, e.g. "cart.py".
    """
    try:
        return {"content": (WORKSPACE / path).read_text()}
    except Exception as e:
        return {"error": str(e)}


def write_file(path: str, content: str) -> dict:
    """Creates a file, or replaces an existing file's contents.

    Args:
        path: File path relative to the project root, e.g. "cart.py".
        content: The complete new contents of the file.
    """
    try:
        file = WORKSPACE / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        return {"status": "ok", "path": path}
    except Exception as e:
        return {"error": str(e)}


def run_command(command: str) -> dict:
    """Runs a shell command in the project folder and returns its output.
    Use it to run code and tests, e.g. "python -m pytest".

    Args:
        command: The shell command to run.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=30,  # a hung command must not freeze the agent
        )
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 30 seconds."}
    return {
        "exit_code": result.returncode,
        # Keep the end of long output: that's where errors and test summaries are.
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


root_agent = Agent(
    name="coding_agent",
    model="gemini-3.8-flash",
    instruction=(
        "You are a coding agent working on a small Python project. "
        "Look before you answer: list the files, then read the ones that matter. "
        "When you change a file, write its complete new contents. "
        "After every change, run the tests with `python -m pytest` and keep "
        "fixing until they all pass. "
        "Finish with a short summary of what you changed and the test result."
    ),
    tools=[list_files, read_file, write_file, run_command],
)
