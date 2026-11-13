"""Pre-workshop check. Run it before Saturday:

    uv run check_setup.py

Every line should say OK. The last check makes one tiny call to Gemini to
prove your project (or API key) works. scripts/setup.sh runs it for you at the end.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL = "gemini-3.8-flash"
failed = False


def report(ok: bool, label: str, fix: str = "") -> None:
    global failed
    print(f"  {'OK  ' if ok else 'FAIL'}  {label}")
    if not ok:
        failed = True
        if fix:
            print(f"        -> {fix}")


print("Checking your workshop setup...\n")

report(sys.version_info >= (3, 11), f"Python {sys.version.split()[0]}", "Install Python 3.11 or newer.")

try:
    import google.adk

    report(True, f"google-adk {google.adk.__version__}")
except ImportError:
    report(False, "google-adk installed", "Run: uv sync")

env_file = ROOT / ".env"
if env_file.exists():
    from dotenv import load_dotenv

    load_dotenv(env_file)
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("1", "true")
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    if use_vertex:
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        report(bool(project) and project != "your-project-id", f".env uses Vertex AI in project {project}", "Run: bash scripts/setup.sh")
    else:
        report(
            bool(key) and key != "paste-your-key-here",
            ".env has a Gemini API key",
            "Get a key at https://aistudio.google.com/apikey, then run: uv run python scripts/set_key.py",
        )
else:
    report(False, ".env exists", "Run: bash scripts/setup.sh   (no billing account? uv run python scripts/set_key.py)")

report(
    (ROOT / "workspace" / "cart.py").exists(),
    "workspace/ exists",
    "Run: uv run reset_workspace.py",
)

if not failed:
    try:
        from google import genai

        client = genai.Client()  # keep a reference: a discarded Client closes its connection
        reply = client.models.generate_content(
            model=MODEL, contents="Reply with exactly one word: ready"
        )
        report(True, f"{MODEL} answered: {reply.text.strip()!r}")
    except Exception as e:
        hint = ("Run bash scripts/setup.sh again: it checks the project, billing, credentials and the API. "
                if use_vertex else "Check the key, or run uv run python scripts/set_key.py again. ")
        report(False, f"call {MODEL}", hint + f"{type(e).__name__}: {e}")

print("\nAll set. See you Saturday!" if not failed else "\nFix the FAIL lines above, then run this again.")
sys.exit(1 if failed else 0)
