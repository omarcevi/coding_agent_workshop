"""Save your Gemini API key in .env. The key does not show on the screen when you paste it.

    uv run python scripts/set_key.py

This is the fallback for anyone without a Google Cloud billing account: scripts/setup.sh (Vertex AI
in your project) is the main path. Makes .env from .env.example if there is no .env yet, and sets
GOOGLE_GENAI_USE_VERTEXAI=FALSE so ADK uses the key. Works in Cloud Shell, on macOS, Linux and
Windows. Get a free key at https://aistudio.google.com/apikey
"""

from __future__ import annotations

import getpass
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def save(key: str, env: Path = ROOT / ".env", example: Path = ROOT / ".env.example") -> None:
    """Put GEMINI_API_KEY=<key> and GOOGLE_GENAI_USE_VERTEXAI=FALSE in env, in place of the old lines."""
    if not env.exists():
        shutil.copy(example, env)
    text = env.read_text(encoding="utf-8")
    for name, value in (("GEMINI_API_KEY", key), ("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")):
        line = f"{name}={value}"
        text, found = re.subn(rf"^{name}=.*$", lambda _: line, text, flags=re.M)
        if not found:
            text = f"{line}\n{text}"
    env.write_text(text, encoding="utf-8")


def main() -> int:
    key = getpass.getpass("Paste your Gemini API key, then press Enter (the key does not show): ").strip()
    if not key or " " in key:
        print("That is not a key. Get one at https://aistudio.google.com/apikey and run this command again.")
        return 1
    save(key)
    print("✅ Key saved in .env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
