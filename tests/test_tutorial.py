"""tutorial.md is generated from the checkpoints: it must be up to date, so Cloud Shell never shows stale code."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_tutorial  # noqa: E402


def test_tutorial_is_up_to_date():
    assert (ROOT / "tutorial.md").read_text(encoding="utf-8") == build_tutorial.build(), (
        "tutorial.md is out of date: run `uv run python scripts/build_tutorial.py`"
    )


def test_tutorial_links_only_files_that_exist():
    import re

    text = (ROOT / "tutorial.md").read_text(encoding="utf-8")
    created_later = {".env", "workspace/hello.py", "workspace/cart.py"}  # made by set_key, reset_workspace, the agent
    for path in set(re.findall(r'filePath="([^"]+)"', text)) - created_later:
        assert (ROOT / path).exists(), path


def test_set_key_writes_the_key(tmp_path):
    import set_key

    example = tmp_path / ".env.example"
    example.write_text("GOOGLE_GENAI_USE_VERTEXAI=FALSE\nGEMINI_API_KEY=paste-your-key-here\n")
    env = tmp_path / ".env"
    set_key.save("test-key-123", env=env, example=example)
    assert env.read_text() == "GOOGLE_GENAI_USE_VERTEXAI=FALSE\nGEMINI_API_KEY=test-key-123\n"
    set_key.save("test-key-456", env=env, example=example)   # a second run replaces, never duplicates
    assert env.read_text().count("GEMINI_API_KEY=") == 1 and "test-key-456" in env.read_text()


def test_set_key_turns_vertex_ai_off(tmp_path):
    """A .env written by setup.sh uses Vertex AI; the fallback key only counts once that is off."""
    import set_key

    env = tmp_path / ".env"
    env.write_text("GOOGLE_GENAI_USE_VERTEXAI=TRUE\nGOOGLE_CLOUD_PROJECT=demo\nGOOGLE_CLOUD_LOCATION=global\n")
    set_key.save("test-key-789", env=env, example=tmp_path / "unused")
    text = env.read_text()
    assert "GOOGLE_GENAI_USE_VERTEXAI=FALSE" in text and "GOOGLE_GENAI_USE_VERTEXAI=TRUE" not in text
    assert "GEMINI_API_KEY=test-key-789" in text


def test_env_example_defaults_to_vertex_ai():
    lines = (ROOT / ".env.example").read_text().splitlines()
    assert "GOOGLE_GENAI_USE_VERTEXAI=TRUE" in lines and "GOOGLE_CLOUD_LOCATION=global" in lines
