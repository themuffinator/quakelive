"""Guard the retail Attack and Defend round-scoreboard owner against drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_BG_PLAN = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md"
IMPLEMENTATION_PLAN = REPO_ROOT / "IMPLEMENTATION_PLAN.md"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
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


def test_ad_round_scoreboard_owner_restores_retail_grid_and_banner_strings() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	status_block = _block_from_marker(source, "static const char *CG_ADRoundScoreboardStatusText")
	draw_block = _block_from_marker(source, "static void CG_DrawADRoundScoreboard")
	warmup_block = _block_from_marker(source, "static void CG_DrawWarmupStatusText")

	for expected in (
		'value = Info_ValueForKey( info, "g_scorelimit" );',
		'value = Info_ValueForKey( info, "roundlimit" );',
		'return "Red Wins! Good Game";',
		'return "Last Chance";',
		'return "Match Point";',
	):
		assert expected in status_block

	for expected in (
		"CG_FillRect( 196.0f, 150.0f, 252.0f, 60.0f, panelColor );",
		"for ( column = 0; column < ( CG_AD_SCORE_HISTORY_LENGTH / 2 ); column++ ) {",
		"historyIndex = column * 2;",
		"roundNumber = roundWindowStart + column;",
		'CG_Text_PaintNoAdjust( 204.0f, 162.0f, 0.20f, colorWhite, "Round", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		'CG_Text_PaintNoAdjust( 204.0f, 178.0f, 0.25f, redColor, "Red", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		'CG_Text_PaintNoAdjust( 204.0f, 194.0f, 0.25f, blueColor, "Blue", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		'CG_Text_PaintNoAdjust( 416.0f, 162.0f, 0.25f, colorWhite, "Score", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		"cg.adScoreHistory[historyIndex]",
		"cg.adScoreHistory[historyIndex + 1]",
		"CG_ADRoundScoreboardStatusText();",
		"320.0f - (float)textWidth * 0.5f",
	):
		assert expected in draw_block

	attack_defend_branch = warmup_block[
		warmup_block.index("} else if ( gametype == GT_ATTACK_DEFEND && cgs.matchRoundState == ROUNDSTATE_WARMUP ) {") :
	]
	assert "CG_DrawADRoundScoreboard();" in attack_defend_branch
	assert attack_defend_branch.index("CG_DrawADRoundScoreboard();") < attack_defend_branch.index("attackingTeam =")


def test_plan_records_ad_round_scoreboard_slice_closed() -> None:
	plan = CG_BG_PLAN.read_text(encoding="utf-8")
	implementation_plan = IMPLEMENTATION_PLAN.read_text(encoding="utf-8")

	assert "| `CG-B3` | Completed 2026-04-05 |" in plan

	cg_b_rows = [line for line in plan.splitlines() if line.startswith("| `CG-B` |")]
	assert cg_b_rows
	assert cg_b_rows[-1].endswith("| None |")

	assert "Task 34: Cgame Attack and Defend round-scoreboard owner parity closure [COMPLETED]" in implementation_plan
