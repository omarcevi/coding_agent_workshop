"""Step 2: give the agent hands. Tools to look at and change files.

ADK turns each plain Python function below into a tool. The model sees only
the function's name, its type hints and its docstring, so the docstring is
written for the model, not for you.

Try: "What's in my project, and what does cart.py do?"
     "Create hello.py that prints a greeting."
"""

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


# Tools return errors instead of raising them. ADK re-raises a tool's
# exception and ends the run, but an error the model can read is one it can
# recover from (e.g. "no such file", then it lists files and tries again).


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


root_agent = Agent(
    name="coding_agent",
    model="gemini-3.8-flash",
    instruction=(
        "You are a coding agent working on a small Python project. "
        "Look before you answer: list the files, then read the ones that matter. "
        "When you change a file, write its complete new contents. "
        "Finish with a short summary of what you did."
    ),
    tools=[list_files, read_file, write_file],
)
