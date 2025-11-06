from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_source(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _extract_function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 1
    i = brace + 1
    while depth:
        char = source[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        i += 1
    return source[brace + 1 : i - 1]


def test_listen_server_slot_reclaim_uses_bot_mask_helper() -> None:
    source = _read_source("src/code/server/sv_client.c")
    body = _extract_function_body(source, "void SV_DirectConnect")

    assert "only bots on server" in body
    assert "SV_ClientIsBot( cl )" in body
    assert "lastBotSlot" in body
    assert "SV_DropClient( &svs.clients[lastBotSlot], \"only bots on server\" );" in body


def test_map_restart_refreshes_entity_masks_via_helper() -> None:
    source = _read_source("src/code/server/sv_ccmds.c")
    body = _extract_function_body(source, "static void SV_MapRestart_f")

    assert "isBot = SV_ClientIsBot( client );" in body
    assert "SV_ClientEnterWorld( client" in body


def test_drop_client_clears_bot_mask_when_reclaimed() -> None:
    source = _read_source("src/code/server/sv_client.c")
    body = _extract_function_body(source, "void SV_DropClient")

    assert "wasBot = SV_ClientIsBot( drop );" in body
    assert "if ( !wasBot )" in body
    assert "if ( wasBot ) {\n\t\tSV_BotFreeClient( drop - svs.clients );\n\t}" in body
