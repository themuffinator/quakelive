"""Guard the recovered cgame announcer and timer helper boundaries against drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_BG_PLAN = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md"


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


def test_cgame_announcer_path_helpers_restore_retail_named_boundary() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	profile_block = _block_from_marker(source, "static const char *CG_BuildAnnouncerSoundPathForProfile")
	path_block = _block_from_marker(source, "static const char *CG_BuildAnnouncerSoundPath")
	register_block = _block_from_marker(source, "static sfxHandle_t CG_RegisterRetailAnnouncerClip")

	for expected in (
		'folder = CG_RetailAnnouncerFolderForProfile( profile );',
		'return va( "sound/%s/%s", folder, sample );',
	):
		assert expected in profile_block

	for expected in (
		"switch ( cg_announcer.integer ) {",
		"case 0:",
		"case 2:",
		"case 3:",
		'trap_Cvar_Set( "cg_announcer", "1" );',
		"return CG_BuildAnnouncerSoundPathForProfile( profile, sample );",
	):
		assert expected in path_block

	for expected in (
		"pathStem = CG_BuildAnnouncerSoundPathForProfile( profile, sample );",
		'Com_sprintf( path, sizeof( path ), "%s%s", pathStem, exts[i] );',
	):
		assert expected in register_block

	assert 'Com_sprintf( path, sizeof( path ), "sound/%s/%s%s", folder, sample, exts[i] );' not in register_block


def test_cgame_timer_format_helpers_drive_retail_ownerdraw_call_sites() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	minutes_block = _block_from_marker(source, "static const char *CG_FormatMinutesSeconds")
	signed_block = _block_from_marker(source, "static const char *CG_FormatSignedWholeSeconds")
	entries_block = _block_from_marker(source, "static const cgTeamPickupSummaryEntry_t cgTeamPickupSummaryEntries[] =")
	summary_block = _block_from_marker(source, "static void CG_DrawTeamPickupSummaryOwnerDraw")
	timeheld_block = _block_from_marker(source, "static qboolean CG_BuildTeamTimeHeldText")
	level_timer_block = _block_from_marker(source, "static void CG_DrawLevelTimer")
	round_timer_block = _block_from_marker(source, "static void CG_DrawRoundTimer")

	for expected in (
		"if ( seconds < 0 ) {",
		'return va( "%i:%i%i", seconds / 60, ( seconds % 60 ) / 10, seconds % 10 );',
	):
		assert expected in minutes_block

	for expected in (
		'absoluteMilliseconds = (unsigned int)( -( milliseconds + 1 ) ) + 1u;',
		"wholeSeconds = (int)( ( absoluteMilliseconds + 500u ) / 1000u );",
		"if ( wholeSeconds < 1 ) {",
		'return va( "%s%1.0fs", signPrefix, (double)wholeSeconds );',
	):
		assert expected in signed_block

	assert "{ CG_TEAMSTAT_PICKUPS_YA, -1, CG_TEAM_PICKUP_SUMMARY_ICON_YA, 11 }" in entries_block
	assert "drawX = (float)(int)rect->x;" in summary_block
	assert "drawY = (float)(int)rect->y;" in summary_block
	assert "CG_Text_Paint( drawX + entry->countTextOffsetX, drawY + 8.0f, scale, color, countText, 0, 0, textStyle );" in summary_block
	assert "CG_Text_Paint( drawX + entry->countTextOffsetX, drawY + 15.0f, scale, color, countText, 0, 0, textStyle );" in summary_block
	assert 'Q_strncpyz( timeText, CG_FormatMinutesSeconds( timeHeld ), sizeof( timeText ) );' in summary_block
	assert 'Q_strncpyz( buffer, CG_FormatMinutesSeconds( value ), bufferSize );' in timeheld_block
	assert 'Q_strncpyz( buffer, CG_FormatMinutesSeconds( seconds ), sizeof( buffer ) );' in level_timer_block
	assert 'Q_strncpyz( buffer, CG_FormatMinutesSeconds( seconds ), sizeof( buffer ) );' in round_timer_block
	assert "roundStartTime = CG_GetMatchRoundStartTime();" in round_timer_block
	assert "roundTimeLimitSeconds = CG_GetRoundTimeLimitSeconds();" in round_timer_block
	assert "remainingMilliseconds = roundTimeLimitSeconds * 1000 - cg.time + roundStartTime;" in round_timer_block
	assert "if ( remainingMilliseconds <= 0 || remainingMilliseconds > 29999 ) {" in round_timer_block
	assert "seconds = ( remainingMilliseconds + 500 ) / 1000;" in round_timer_block

	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i:%i%i", seconds / 60, ( seconds % 60 ) / 10, seconds % 10 );' not in level_timer_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i:%i%i", seconds / 60, ( seconds % 60 ) / 10, seconds % 10 );' not in round_timer_block
	assert 'Com_sprintf( buffer, bufferSize, "%i:%i%i", value / 60, ( value % 60 ) / 10, value % 10 );' not in timeheld_block
	assert "seconds = CG_GetScoreboardTimerSeconds();" not in round_timer_block


def test_cgame_bg_plan_closes_cg_e_direct_owner_gap() -> None:
	plan = CG_BG_PLAN.read_text(encoding="utf-8")
	cg_e_rows = [line for line in plan.splitlines() if line.startswith("| `CG-E` |")]
	assert cg_e_rows
	cg_e_row = cg_e_rows[-1]

	for closed_name in (
		"`CG_BuildAnnouncerSoundPath`",
		"`CG_FormatMinutesSeconds`",
		"`CG_FormatSignedWholeSeconds`",
		"`CG_DrawClientModelPreview`",
		"`CG_ResolveClientModelColorBytes`",
	):
		assert closed_name not in cg_e_row

	assert cg_e_row.strip().endswith("| None |")
	assert "| `CG-E4` | Completed 2026-04-05 | Boundary-only |" in plan
