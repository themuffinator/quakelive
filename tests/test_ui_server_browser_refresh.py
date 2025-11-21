from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_server_browser_refresh_text_matches_reference() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "Getting info for %d servers (ESC to cancel)" in ui_main
    assert "ui_lastServerRefresh_%i" in ui_main

    reference = (
        REPO_ROOT
        / "references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt"
    ).read_text(encoding="utf-8", errors="ignore")
    assert "ui_lastServerRefresh_%i" in reference
    assert "Refresh Time: %s" in reference
    assert "Getting info for %d servers (ESC to cancel)" in reference
