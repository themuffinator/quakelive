from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = REPO_ROOT / "src" / "code" / "game"

def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text()

def test_spawn_and_spectator_cvars_registered() -> None:
    main_text = _read("src/code/game/g_main.c")
    for name in (
        "g_grantItemOnSpawn",
        "g_maxDeferredSpawns",
        "g_teamSpawnAsSpec",
        "g_teamSpecFreeCam",
        "g_teamSpecSayEnable",
    ):
        assert name in main_text, f"{name} missing from g_main.c"

def test_spawn_grant_helper_used() -> None:
    client_text = _read("src/code/game/g_client.c")
    assert "static void G_GrantConfiguredItems" in client_text
    assert "G_GrantConfiguredItems( ent );" in client_text

def test_spawn_queue_cap_enforced() -> None:
    spawn_text = _read("src/code/game/g_spawn.c")
    assert "G_CountQueuedSpawns" in spawn_text
    assert "g_maxDeferredSpawns" in spawn_text

def test_spectator_chat_and_follow_controls_documented() -> None:
    cmds_text = _read("src/code/game/g_cmds.c")
    assert "Spectator chat is disabled while g_teamSpecSayEnable is 0." in cmds_text
    assert "Free-flying spectators are disabled" in cmds_text

def test_docs_cover_new_cvars() -> None:
    docs_text = _read("docs/gameplay/cvars.md")
    for name in (
        "`g_grantItemOnSpawn`",
        "`g_maxDeferredSpawns`",
        "`g_teamSpawnAsSpec`",
        "`g_teamSpecFreeCam`",
        "`g_teamSpecSayEnable`",
    ):
        assert name in docs_text, f"Documentation missing entry for {name}"
