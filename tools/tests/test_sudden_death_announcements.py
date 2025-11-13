"""Regression coverage for sudden-death respawn announcement messaging."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_source(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _extract_function_body(source: str, signature: str) -> str:
    first = source.index(signature)
    try:
        start = source.index(signature, first + len(signature))
    except ValueError:
        start = first
    brace = source.index("{", start)
    depth = 1
    position = brace + 1
    while depth:
        char = source[position]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        position += 1
    return source[brace + 1 : position - 1]


def test_sudden_death_announcements_use_center_print_channel() -> None:
    source = _read_source("src/code/game/g_main.c")
    body = _extract_function_body(source, "static void G_TrackSuddenDeathAnnouncements( void )")

    assert "g_suddenDeathRespawn.integer <= 0" in body
    assert "cp \\\"Sudden-death respawns disabled\\n\\\"" in body
    assert "cp \\\"Sudden-death respawns available in %i seconds\\n\\\"" in body
    assert "cp \\\"Sudden-death respawns available now\\n\\\"" in body
    assert "print \\\"Sudden-death respawns" not in body
