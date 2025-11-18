import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BG_MISC = REPO_ROOT / "src" / "code" / "game" / "bg_misc.c"
INV_HEADER = REPO_ROOT / "src" / "code" / "game" / "inv.h"


def _bg_item_names():
    prefixes = ("\"item_", "\"weapon_", "\"ammo_", "\"holdable_", "\"team_")
    names = []
    for line in BG_MISC.read_text().splitlines():
        stripped = line.strip()
        if any(stripped.startswith(prefix) for prefix in prefixes):
            names.append(stripped.split('"')[1])
    return names


def _modelindex_values():
	pattern = re.compile(r"^#define\s+MODELINDEX_[A-Z0-9_]+\s+(\d+)$", re.MULTILINE)
	return [int(match.group(1)) for match in pattern.finditer(INV_HEADER.read_text())]


def test_modelindex_definitions_match_bg_itemlist():
    item_names = _bg_item_names()
    model_indexes = _modelindex_values()
    assert len(model_indexes) == len(item_names), (
        "MODELINDEX_* definitions must cover every bg_itemlist entry"
    )
    assert model_indexes == list(range(1, len(item_names) + 1)), (
        "MODELINDEX_* values must stay sequential to match bg_itemlist order"
    )
