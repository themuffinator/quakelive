from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _block_from_marker(source: str, marker: str) -> str:
	start = source.index(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_battlesuit_damage_multiplier_matches_retail_ql() -> None:
	game_main = _read("src/code/game/g_main.c")
	game_combat = _read("src/code/game/g_combat.c")
	scale_block = _block_from_marker(game_combat, "static float G_BattleSuitDamageScale")
	battlesuit_start = game_combat.index("// battlesuit dampens damage in retail QL")
	battlesuit_end = game_combat.index("// add to the attacker's hit counter", battlesuit_start)
	battlesuit_block = game_combat[battlesuit_start:battlesuit_end]

	assert '{ &g_battleSuitDampen, "g_battleSuitDampen", "0.25",' in game_main
	assert "return g_battleSuitDampen.value;" in scale_block
	assert "0.5f" not in scale_block
	assert "scale <=" not in scale_block
	assert "scale >" not in scale_block

	assert "if ( client && client->ps.powerups[PW_BATTLESUIT] ) {" in battlesuit_block
	assert "G_AddEvent( targ, EV_POWERUP_BATTLESUIT, 0 );" in battlesuit_block
	assert "if ( mod != MOD_FALLING ) {" in battlesuit_block
	assert "damage *= G_BattleSuitDamageScale();" in battlesuit_block
	assert "DAMAGE_RADIUS" not in battlesuit_block
	assert "return;" not in battlesuit_block
