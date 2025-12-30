from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _extract_define(text: str, name: str) -> str:
    pattern = rf"#define\s+{re.escape(name)}\s+\"([^\"]+)\""
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"define for {name} not found")
    return match.group(1)


def test_ui_menu_defaults_use_existing_assets() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert '"ui_menuFiles", UI_MENU_FILE_QUAKELIVE' in ui_main
    assert '"ui_menuFlow", "0"' in ui_main

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    legacy_menu = _extract_define(ui_local, "UI_MENU_FILE_LEGACY")
    legacy_ingame = _extract_define(ui_local, "UI_INGAME_FILE_LEGACY")

    for menu_file in (legacy_menu, legacy_ingame):
        assert (REPO_ROOT / "src" / menu_file).exists(), menu_file
