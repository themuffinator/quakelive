from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT_STR = str(REPO_ROOT)
if _REPO_ROOT_STR not in sys.path:
	sys.path.insert(0, _REPO_ROOT_STR)

def read_json(path: Path) -> dict[str, Any]:
	"""Load a UTF-8 JSON file into a mapping."""

	return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, payload: dict[str, Any]) -> None:
	"""Write JSON with the repo's standard pretty-print formatting."""

	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

def contains_all(text: str, *needles: str) -> bool:
	"""Return True when *text* contains every supplied needle."""

	return all(needle in text for needle in needles)

def section_text_for_id(text: str, section_id: str) -> str:
	"""Extract a markdown level-2 section by its heading prefix."""

	match = re.search(rf"^## {re.escape(section_id)}\b.*$", text, re.MULTILINE)
	if match is None:
		return ""

	start = match.start()
	next_match = re.search(r"\n## ", text[match.end() :])
	if next_match is None:
		return text[start:]

	end = match.end() + next_match.start()
	return text[start:end]
