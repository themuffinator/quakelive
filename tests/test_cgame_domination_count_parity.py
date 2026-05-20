from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _extract_block(source: str, anchor: str) -> str:
	start = source.index(anchor)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start : index + 1]

	raise AssertionError(f"Unterminated block for {anchor}")


def test_domination_count_configstrings_share_retail_race_slots_safely() -> None:
	cgame_local_h = _read("src/code/cgame/cg_local.h")
	servercmds_c = _read("src/code/cgame/cg_servercmds.c")
	newdraw_c = _read("src/code/cgame/cg_newdraw.c")
	game_local_h = _read("src/code/game/g_local.h")
	game_team_c = _read("src/code/game/g_team.c")
	cgame_ghidra = _read("references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c")

	shared_block = _extract_block(servercmds_c, "static void CG_ParseSharedRaceDominationConfigStrings( void ) {")
	draw_block = _extract_block(newdraw_c, "static int CG_CountDominationOwnedFlags( team_t team ) {")
	game_block = _extract_block(game_team_c, "void G_UpdateDominationPointCountConfigstrings( void ) {")

	assert "int\t\tdominationOwnedPointCount[TEAM_NUM_TEAMS];" in cgame_local_h
	assert "void G_UpdateDominationPointCountConfigstrings( void );" in game_local_h

	assert "if ( cgs.gametype == GT_RACE ) {" in shared_block
	assert "CG_ParseRaceInfoString( CG_ConfigString( CS_RACE_INFO ) );" in shared_block
	assert "CG_ParseRaceStatusString( CG_ConfigString( CS_RACE_STATUS ) );" in shared_block
	assert "CG_ParseRaceInit();" in shared_block
	assert "if ( cgs.gametype != GT_DOMINATION && cgs.gametype != GT_ATTACK_DEFEND ) {" in shared_block
	assert "cgs.dominationOwnedPointCount[TEAM_RED] = value;" in shared_block
	assert "cgs.dominationOwnedPointCount[TEAM_BLUE] = value;" in shared_block

	assert "if ( cgs.gametype != GT_DOMINATION && cgs.gametype != GT_ATTACK_DEFEND ) {" in draw_block
	assert "return cgs.dominationOwnedPointCount[team];" in draw_block
	assert "cg.snap->numEntities" not in draw_block
	assert "!cg.snap" not in draw_block

	assert 'trap_SetConfigstring( CS_RACE_SCORES, redOwnedString );' in game_block
	assert 'trap_SetConfigstring( CS_RACE_INFO, blueOwnedString );' in game_block

	assert "if (iVar1 == 700) {" in cgame_ghidra
	assert "_DAT_10a404cc = atoi(_Str);" in cgame_ghidra
	assert "if (iVar1 == 0x2bd) {" in cgame_ghidra
	assert "_DAT_10a404d0 = atoi(_Str);" in cgame_ghidra
