"""The written guide shows code from this repo. Keep it identical, so the website never shows stale code.

Every code block under a `<!-- source: path -->` comment in guide/coding-agent-workshop.md must appear,
character for character, in that file.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "guide" / "coding-agent-workshop.md"
SOURCED = re.findall(r"<!-- source: (\S+) -->\n```\w*\n(.*?)\n```", GUIDE.read_text(encoding="utf-8"), re.S)


def test_the_guide_has_sourced_snippets():
    assert len(SOURCED) >= 8


@pytest.mark.parametrize("path, code", SOURCED, ids=[f"{p}:{i}" for i, (p, _) in enumerate(SOURCED)])
def test_snippet_matches_its_file(path, code):
    assert code in (ROOT / path).read_text(encoding="utf-8"), f"the guide's snippet from {path} is out of date"
