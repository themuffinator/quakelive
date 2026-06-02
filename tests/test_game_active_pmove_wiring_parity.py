from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
G_ACTIVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_active.c"
G_ARENAS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_arenas.c"
G_BOT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_bot.c"
G_CLIENT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
G_CMDS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"
G_COMBAT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_combat.c"
G_FACTORY_PATH = REPO_ROOT / "src" / "code" / "game" / "g_factory.c"
G_FREEZE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_freeze.c"
G_GAMETYPE_LIFECYCLE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_gametype_lifecycle.inc"
G_ITEMS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_items.c"
G_LOCAL_PATH = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
G_MAIN_PATH = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
G_MISSILE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_missile.c"
G_CONFIG_PATH = REPO_ROOT / "src" / "game" / "g_config.c"
G_WEAPON_PATH = REPO_ROOT / "src" / "code" / "game" / "g_weapon.c"
BG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
G_MATCH_CONFIG_PATH = REPO_ROOT / "src" / "game" / "g_match_config.c"
G_MEM_PATH = REPO_ROOT / "src" / "code" / "game" / "g_mem.c"
G_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_pmove.c"
G_SPAWN_PATH = REPO_ROOT / "src" / "code" / "game" / "g_spawn.c"
G_SVCMDS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_svcmds.c"
G_TEAM_PATH = REPO_ROOT / "src" / "code" / "game" / "g_team.c"
G_UTILS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_utils.c"
CG_ENTS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_MAIN_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_PLAYERS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
MATCH_STATE_KEYS_PATH = REPO_ROOT / "src" / "game" / "match_state_keys.h"
QAGAME_MAP_PATH = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
QAGAME_MAPPING_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "qagame-mapping.md"
QAGAME_HLIL_PART01_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part01.txt"
)
QAGAME_HLIL_PART02_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)
QAGAME_HLIL_PART03_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part03.txt"
)
CGAME_HLIL_PART02_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "cgamex86.dll"
	/ "cgamex86.dll_hlil_split"
	/ "cgamex86.dll_hlil_part02.txt"
)


def _function_body(source: str, signature: str) -> str:
	definition = f"{signature} {{"
	try:
		start = source.index(definition)
	except ValueError:
		start = source.index(signature)
	brace = source.index("{", start)
	depth = 1
	position = brace + 1
	while depth > 0:
		if source[position] == "{":
			depth += 1
		elif source[position] == "}":
			depth -= 1
		position += 1

	return source[brace + 1 : position - 1]


def _block_from_marker(source: str, marker: str) -> str:
	start = source.index(marker)
	brace = source.index("{", start)
	depth = 1
	position = brace + 1
	while depth > 0:
		if source[position] == "{":
			depth += 1
		elif source[position] == "}":
			depth -= 1
		position += 1

	return source[start:position]


def _text_block(source: str, start_marker: str, end_marker: str) -> str:
	start = source.index(start_marker)
	end = source.index(end_marker, start)
	return source[start:end]


def _symbol_comment(normalized_name: str) -> str:
	symbol_map = json.loads(QAGAME_MAP_PATH.read_text(encoding="utf-8"))
	for entry in symbol_map["functions"]:
		if entry["normalized_name"] == normalized_name:
			return entry["comment"]

	raise AssertionError(f"{normalized_name} missing from qagame symbol map")


def test_team_arena_environment_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	cg_main = CG_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")
	cgame_hlil = CGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_allTalk, "g_allTalk", "0", 0, 0, qfalse',
		'{ &g_motd, "g_motd", "", 0, 0, qfalse },',
		'{ &g_podiumDist, "g_podiumDist", "80", CVAR_GAMERULE, 0, qfalse },',
		'{ &g_podiumDrop, "g_podiumDrop", "70", CVAR_GAMERULE, 0, qfalse },',
		'{ &g_obeliskHealth, "g_obeliskHealth", "2500", CVAR_GAMERULE, 0, qfalse },',
		'{ &g_obeliskRegenPeriod, "g_obeliskRegenPeriod", "1", CVAR_GAMERULE, 0, qfalse },',
		'{ &g_obeliskRegenAmount, "g_obeliskRegenAmount", "15", CVAR_GAMERULE, 0, qfalse },',
		'{ &g_obeliskRespawnDelay, "g_obeliskRespawnDelay", "10", CVAR_GAMERULE, 0, qfalse },',
		'{ &g_cubeTimeout, "g_cubeTimeout", "30", CVAR_GAMERULE, 0, qfalse },',
		'{ &g_enableDust, "g_enableDust", "0", 0, 0, qtrue, qfalse },',
	):
		assert row in g_main

	assert '{ &cg_obeliskRespawnDelay, "g_obeliskRespawnDelay", "10", 0},' in cg_main
	assert '{ &cg_enableDust, "g_enableDust", "0", CVAR_SERVERINFO}' in cg_main

	for snippet in (
		'char const data_10087440[0xa] = "g_allTalk", 0',
		'char const data_10086968[0x7] = "g_motd", 0',
		'char const data_10082204[0xd] = "g_podiumDist", 0',
		'char const data_10082214[0xd] = "g_podiumDrop", 0',
		'38 30 00 00',
		'37 30 00 00',
		'char const data_100868d8[0x10] = "g_obeliskHealth", 0',
		'char const data_100868b8[0x15] = "g_obeliskRegenAmount", 0',
		'char const data_100868a0[0x15] = "g_obeliskRegenPeriod", 0',
		'char const data_10086888[0x16] = "g_obeliskRespawnDelay", 0',
		'char const data_10086fe4[0xd] = "g_enableDust", 0',
		'char const data_10087330[0xe] = "g_cubeTimeout", 0',
		'33 30 00 00',
	):
		assert snippet in qagame_strings

	alltalk_block = _text_block(
		qagame_hlil,
		'char const (* data_1008dbdc)[0xa] = data_10087440 {"g_allTalk"}',
		'char const (* data_1008dbf4)[0xb] = data_10087434 {"g_ammoPack"}',
	)
	cube_block = _text_block(
		qagame_hlil,
		'char const (* data_1008dd14)[0xe] = data_10087330 {"g_cubeTimeout"}',
		'char const (* data_1008dd2c)[0x11] = data_10087318 {"g_customSettings"}',
	)
	dust_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e194)[0xd] = data_10086fe4 {"g_enableDust"}',
		'char const (* data_1008e1ac)[0x18] = data_10086fcc {"g_enemyTeamRespawnRatio"}',
	)
	motd_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e974)[0x7] = data_10086968 {"g_motd"}',
		'char const (* data_1008e98c)[0xd] = data_10086958 {"g_nailbounce"}',
	)
	obelisk_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ea34)[0x10] = data_100868d8 {"g_obeliskHealth"}',
		'char const (* data_1008ea94)[0xb] = data_1008687c {"g_overtime"}',
	)
	podium_block = _text_block(
		qagame_hlil,
		'char const (* data_1008eb54)[0xd] = data_10082204 {"g_podiumDist"}',
		'char const (* data_1008eb84)[0x11] = data_100867d0 {"g_powerupRespawn"}',
	)

	assert "data_1007d0a8" in alltalk_block
	assert "00 00 00 00" in alltalk_block
	assert "data_1008732c" in cube_block
	assert "00 00 10 00" in cube_block
	assert "data_1007d0a8" in dust_block
	assert "00 00 00 00" in dust_block
	assert "data_1007c414" in motd_block
	assert "00 00 00 00" in motd_block
	assert obelisk_block.count("00 00 10 00") == 4
	assert "data_100868d0" in obelisk_block
	assert "data_1007e1d8" in obelisk_block
	assert "data_1007d1d8" in obelisk_block
	assert "data_1007e194" in obelisk_block
	assert podium_block.count("00 00 10 00") == 2
	assert "0x10087260" in podium_block
	assert "data_1007e20c" in podium_block

	assert 'char const (* data_1007734c)[0xd] = data_1006b794 {"g_enableDust"}' in cgame_hlil
	assert "1007735c                                                                                      04 00 00 00" in cgame_hlil
	assert 'char const (* data_100778bc)[0x16] = data_1006b328 {"g_obeliskRespawnDelay"}' in cgame_hlil
	assert "100778cc                                      00 00 00 00" in cgame_hlil


def test_team_arena_environment_cvars_keep_retail_behavioral_wiring() -> None:
	g_arenas = G_ARENAS_PATH.read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_cmds = G_CMDS_PATH.read_text(encoding="utf-8")
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_spawn = G_SPAWN_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")
	cg_ents = CG_ENTS_PATH.read_text(encoding="utf-8")
	cg_players = CG_PLAYERS_PATH.read_text(encoding="utf-8")

	assert 'if ( g_gametype.integer < GT_TEAM || g_allTalk.integer ) {' in g_team
	assert "!g_allTalk.integer" in g_cmds
	assert "Cross-team tells are disabled while g_allTalk is 0." in g_cmds
	assert "Spectators may only chat with other spectators unless g_allTalk is enabled." in g_cmds

	assert 'trap_SetConfigstring( CS_MOTD, g_motd.string );' in g_spawn
	assert "if ( g_motd.string[0] ) {" in g_client
	assert 'trap_SendServerCommand( clientNum, va("cp \\"%s\\"", g_motd.string ) );' in g_client

	assert 'trap_Cvar_VariableIntegerValue( "g_podiumDist" )' in g_arenas
	assert 'trap_Cvar_VariableIntegerValue( "g_podiumDrop" )' in g_arenas
	assert g_arenas.count('trap_Cvar_VariableIntegerValue( "g_podiumDist" )') == 2
	assert g_arenas.count('trap_Cvar_VariableIntegerValue( "g_podiumDrop" )') == 2

	for snippet in (
		"g_obeliskRegenPeriod.integer * 1000",
		"self->health >= g_obeliskHealth.integer",
		"self->health += g_obeliskRegenAmount.integer",
		"self->health = g_obeliskHealth.integer",
		"g_obeliskRespawnDelay.integer * 1000",
		"self->activator->s.modelindex2 = self->health * 0xff / g_obeliskHealth.integer;",
	):
		assert snippet in g_team
	assert "(cg_obeliskRespawnDelay.integer - 5) * 1000" in cg_ents

	assert "drop->nextthink = level.time + g_cubeTimeout.integer * 1000;" in g_combat
	assert 'trap_Cvar_Set( "g_enableDust", s );' in g_spawn
	assert "if (!cg_enableDust.integer)" in cg_players
	assert 'trap_SetConfigstring( CS_ENABLE_BREATH, s );' in g_spawn
	assert 'trap_Cvar_Set( "g_enableBreath", s );' not in g_spawn


def test_server_admin_factory_match_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_password, "g_password", "", CVAR_USERINFO, 0, qfalse',
		'{ &g_needpass, "g_needpass", "0", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse',
		'{ &g_banIPs, "g_banIPs", "", CVAR_ARCHIVE, 0, qfalse',
		'{ &g_filterBan, "g_filterBan", "1", CVAR_ARCHIVE, 0, qfalse',
		'{ &g_factoryTitle, "g_factoryTitle", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse',
		'{ &g_factory, "g_factory", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse',
		'{ &g_overtime, "g_overtime", "120", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_mercytime, "g_mercytime", "0", CVAR_NORESTART | CVAR_GAMERULE, 0, qfalse',
		'{ &g_autoAction, "g_autoAction", "0", 0, 0, qfalse',
		'{ &g_kickBadUserinfo, "g_kickBadUserinfo", "1", 0, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_10086870[0xb] = "g_password", 0',
		'char const data_1008687c[0xb] = "g_overtime", 0',
		'char const data_10086908[0xb] = "g_needpass", 0',
		'char const data_10086984[0xc] = "g_mercytime", 0',
		'char const data_10086be4[0x12] = "g_kickBadUserinfo", 0',
		'char const data_10086fa0[0xc] = "g_filterBan", 0',
		'char const data_10086fac[0xf] = "g_factoryTitle", 0',
		'char const data_10086fbc[0xa] = "g_factory", 0',
		'char const data_100873f4[0x9] = "g_banIPs", 0',
		'char const data_10087400[0xd] = "g_autoAction", 0',
		'1007c414                                                              00 00 00 00',
		'1007d0a8                          30 00 00 00',
		'1007d1d8                                                                          31 00 00 00',
		'100869c8                          31 32 30 00',
	):
		assert snippet in qagame_strings

	auto_ban_block = _text_block(
		qagame_hlil,
		'char const (* data_1008dc3c)[0xd] = data_10087400 {"g_autoAction"}',
		'char const (* data_1008dc6c)[0x13] = data_100873e0 {"g_battleSuitDampen"}',
	)
	factory_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e1c4)[0xa] = data_10086fbc {"g_factory"}',
		'char const (* data_1008e20c)[0xf] = data_10086f90 {"g_flightThrust"}',
	)
	kick_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e5fc)[0x12] = data_10086be4 {"g_kickBadUserinfo"}',
		'char const (* data_1008e614)[0xc] = data_10086bd8 {"g_knockback"}',
	)
	mercy_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e944)[0xc] = data_10086984 {"g_mercytime"}',
		'char const (* data_1008e95c)[0x12] = data_10086970 {"g_midAirMinHeight"}',
	)
	needpass_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ea04)[0xb] = data_10086908 {"g_needpass"}',
		'char const (* data_1008ea1c)[0x16] = data_100868f0 {"g_neutralFlagPingRate"}',
	)
	overtime_password_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ea94)[0xb] = data_1008687c {"g_overtime"}',
		'char const (* data_1008eac4)[0x12] = data_1008685c {"g_playerCylinders"}',
	)

	assert "data_1007d0a8" in auto_ban_block
	assert "00 00 00 00" in auto_ban_block
	assert "data_1007c414" in auto_ban_block
	assert "01 00 00 00" in auto_ban_block
	assert factory_block.count("data_1007c414") == 2
	assert factory_block.count("44 00 00 00") == 2
	assert "data_1007d1d8" in factory_block
	assert "01 00 00 00" in factory_block
	assert "data_1007d1d8" in kick_block
	assert "00 00 00 00" in kick_block
	assert "data_1007d0a8" in mercy_block
	assert "00 04 10 00" in mercy_block
	assert "data_1007d0a8" in needpass_block
	assert "44 00 00 00" in needpass_block
	assert "0x100869c8" in overtime_password_block
	assert "04 00 10 00" in overtime_password_block
	assert "data_1007c414" in overtime_password_block
	assert "02 00 00 00" in overtime_password_block


def test_server_admin_factory_match_cvars_keep_retail_behavioral_wiring() -> None:
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_factory = G_FACTORY_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_match_config = G_MATCH_CONFIG_PATH.read_text(encoding="utf-8")
	g_svcmds = G_SVCMDS_PATH.read_text(encoding="utf-8")
	g_utils = G_UTILS_PATH.read_text(encoding="utf-8")
	check_cvars_body = _function_body(g_main, "void CheckCvars( void )")
	check_exit_body = _function_body(g_main, "void CheckExitRules( void )")
	client_userinfo_body = _function_body(g_client, "void ClientUserinfoChanged( int clientNum )")
	factory_apply_body = _function_body(g_factory, "qboolean Factory_Apply( const factoryDefinition_t *factory, qboolean forceReapply )")
	factory_selection_body = _function_body(g_factory, "void Factory_ApplyCurrentSelection( qboolean forceReapply )")
	match_config_body = _function_body(g_match_config, "static matchFactoryConfig_t G_MatchConfig_Load( void )")
	auto_action_body = _function_body(g_utils, "void G_AutoAction( autoActionEvent_t event, const gentity_t *subject, const char *details )")

	assert "if ( g_password.modificationCount != lastMod ) {" in check_cvars_body
	assert 'trap_Cvar_Set( "g_needpass", "1" );' in check_cvars_body
	assert 'trap_Cvar_Set( "g_needpass", "0" );' in check_cvars_body
	assert check_cvars_body.index("g_password.modificationCount") < check_cvars_body.index('trap_Cvar_Set( "g_needpass", "1" );')

	assert "if ( g_kickBadUserinfo.integer ) {" in client_userinfo_body
	assert 'trap_DropClient( clientNum, "Bad userinfo" );' in client_userinfo_body
	assert 'trap_SendServerCommand( clientNum, "print \\"WARNING: Invalid userinfo detected.\\\\n\\"" );' in client_userinfo_body
	assert 'strcpy( userinfo, "\\\\name\\\\badinfo" );' in client_userinfo_body

	assert 'trap_Cvar_Set( "g_banIPs", iplist_final );' in g_svcmds
	assert "return g_filterBan.integer != 0;" in g_svcmds
	assert "return g_filterBan.integer == 0;" in g_svcmds

	assert 'trap_Cvar_Set( "g_factoryTitle", "" );' in factory_apply_body
	assert 'trap_Cvar_Set( "g_factoryTitle", factory->title ? factory->title : "" );' in factory_apply_body
	assert "trap_Cvar_Update( &g_factory );" in factory_selection_body
	assert "Factory_ApplyDefaultSelection( forceReapply );" in factory_selection_body
	assert "factory = Factory_FindById( g_factory.string );" in factory_selection_body
	assert 'trap_Cvar_Set( "g_factory", s_activeFactory->id );' in factory_selection_body

	assert 'config.overtimeLengthSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_overtime, DEFAULT_OVERTIME_LENGTH_SECONDS, "g_overtime" );' in match_config_body
	assert "mercyLimitMsec = G_BuildExitRuleLimitMsec( g_mercytime.integer, level.overtimeAccumulatedMsec );" in check_exit_body
	assert "if ( g_timelimit.integer == 0 || g_overtime.integer <= 0 ) {" in check_exit_body

	assert '!Q_stricmp( g_autoAction.string, "0" )' in auto_action_body
	assert "Q_strncpyz( config, g_autoAction.string, sizeof( config ) );" in auto_action_body
	assert "G_AutoAction_RunCommand( eventName, commandToken, subject, details );" in auto_action_body


def test_match_flow_warmup_timeout_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_gameState, "g_gameState", GAME_STATE_PRE_GAME, CVAR_SERVERINFO | CVAR_ROM, 0, qfalse',
		'{ &g_friendlyFire, "g_friendlyFire", "0", CVAR_GAMERULE, 0, qtrue',
		'{ &g_debugAlloc, "g_debugAlloc", "0", 0, 0, qfalse },',
		'{ &g_grantItemOnSpawn, "g_grantItemOnSpawn", "", CVAR_GAMERULE, 0, qfalse',
		'{ &g_doWarmup, "g_doWarmup", "1", CVAR_ARCHIVE, 0, qtrue',
		'{ &g_warmup, "g_warmup", "10", CVAR_ARCHIVE, 0, qtrue',
		'{ &g_warmupReadyDelay, "g_warmupReadyDelay", "0", 0, 0, qfalse',
		'{ &g_warmupReadyDelayAction, "g_warmupReadyDelayAction", "1", 0, 0, qfalse',
		'{ &g_timeoutCount, "g_timeoutCount", "0", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_timeoutLen, "g_timeoutLen", "60", CVAR_GAMERULE, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_10086d08[0xc] = "g_gameState", 0',
		'char const data_10086cfc[0x9] = "PRE_GAME", 0',
		'char const data_10086d34[0xf] = "g_friendlyFire", 0',
		'char const data_10087200[0xd] = "g_debugAlloc", 0',
		'char const data_10086ccc[0x13] = "g_grantItemOnSpawn", 0',
		'char const data_1007e25c[0xb] = "g_doWarmup", 0',
		'char const data_1007e268[0x9] = "g_warmup", 0',
		'char const data_10085da8[0x13] = "g_warmupReadyDelay", 0',
		'char const data_10085d8c[0x19] = "g_warmupReadyDelayAction", 0',
		'char const data_10085e70[0xf] = "g_timeoutCount", 0',
		'char const data_10085e60[0xd] = "g_timeoutLen", 0',
		'1008674b                                   00 36 30 00 00',
		'1007d0a8                          30 00 00 00',
		'1007d1d8                                                                          31 00 00 00',
		'1007e194                                                              31 30 00 00',
	):
		assert snippet in qagame_strings

	debug_block = _text_block(
		qagame_hlil,
		'char const (* data_1008def4)[0xd] = data_10087200 {"g_debugAlloc"}',
		'char const (* data_1008df0c)[0xe] = data_100871f0 {"g_debugDamage"}',
	)
	do_warmup_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e0bc)[0xb] = data_1007e25c {"g_doWarmup"}',
		'char const (* data_1008e0d4)[0xb] = data_100854b8 {"g_dropCmds"}',
	)
	friendly_state_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e44c)[0xf] = data_10086d34 {"g_friendlyFire"}',
		'char const (* data_1008e494)[0xb] = data_1007dac0 {"g_gametype"}',
	)
	grant_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e4c4)[0x13] = data_10086ccc {"g_grantItemOnSpawn"}',
		'char const (* data_1008e4dc)[0xa] = data_10086cc0 {"g_gravity"}',
	)
	timeout_block = _text_block(
		qagame_hlil,
		'char const (* data_1008f61c)[0xf] = data_10085e70 {"g_timeoutCount"}',
		'char const (* data_1008f64c)[0xb] = data_1007e22c {"g_training"}',
	)
	warmup_block = _text_block(
		qagame_hlil,
		'char const (* data_1008f73c)[0x9] = data_1007e268 {"g_warmup"}',
		'char const (* data_1008f79c)[0x19] = data_10085d70 {"sv_warmupReadyPercentage"}',
	)

	assert "data_1007d0a8" in debug_block
	assert "00 00 00 00" in debug_block
	assert "data_1007d1d8" in do_warmup_block
	assert "01 00 00 00" in do_warmup_block
	assert "data_1007d0a8" in friendly_state_block
	assert "00 00 10 00" in friendly_state_block
	assert 'data_10086cfc {"PRE_GAME"}' in friendly_state_block
	assert "44 00 00 00" in friendly_state_block
	assert "data_1007c414" in grant_block
	assert "00 00 10 00" in grant_block
	assert "data_1007d0a8" in timeout_block
	assert "04 00 10 00" in timeout_block
	assert "0x1008674c" in timeout_block
	assert "00 00 10 00" in timeout_block
	assert "data_1007e194" in warmup_block
	assert "01 00 00 00" in warmup_block
	assert "data_1007d0a8" in warmup_block
	assert "data_1007d1d8" in warmup_block
	assert warmup_block.count("00 00 00 00") >= 2


def test_match_flow_warmup_timeout_cvars_keep_retail_behavioral_wiring() -> None:
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_lifecycle = G_GAMETYPE_LIFECYCLE_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_match_config = G_MATCH_CONFIG_PATH.read_text(encoding="utf-8")
	g_mem = G_MEM_PATH.read_text(encoding="utf-8")
	g_spawn = G_SPAWN_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")
	game_state_body = _function_body(g_main, "void G_SetGameState( const char *state )")
	update_state_body = _function_body(g_main, "static void G_UpdateGameStateForLevel( void )")
	ready_delay_body = _function_body(g_main, "static void G_CheckReadyUpDelayAction( void )")
	level_timers_body = _function_body(g_main, "static void LevelCheckTimers( void )")
	duel_begin_body = _function_body(g_lifecycle, "static void G_DuelClientBegin( gentity_t *ent )")
	match_config_body = _function_body(g_match_config, "static matchFactoryConfig_t G_MatchConfig_Load( void )")
	memory_body = _function_body(g_mem, "void *G_Alloc( int size )")
	grant_body = _function_body(g_client, "static void G_GrantConfiguredItems( gentity_t *ent )")

	assert 'trap_Cvar_Set( "g_gameState", value );' in game_state_body
	assert "value = ( state && state[0] ) ? state : GAME_STATE_PRE_GAME;" in game_state_body
	assert "state = GAME_STATE_COUNT_DOWN;" in update_state_body
	assert "state = GAME_STATE_IN_PROGRESS;" in update_state_body
	assert "state = GAME_STATE_PRE_GAME;" in update_state_body
	assert "G_SetGameState( state );" in update_state_body

	assert "if ( g_debugAlloc.integer ) {" in memory_body
	assert 'G_Printf( "G_Alloc of %i bytes (%i left)\\n"' in memory_body
	assert "if ( !g_friendlyFire.integer ) {" in g_combat
	assert "if ( !g_friendlyFire.integer ) {" in g_team
	assert 'G_RunGrantScript( ent, g_grantItemOnSpawn.string );' in grant_body

	assert "} else if ( g_doWarmup.integer ) { // Turn it on" in g_spawn
	assert "if ( !g_doWarmup.integer ) {" in g_main
	assert "countdownSeconds = g_warmup.integer;" in duel_begin_body
	assert "level.warmupTime = level.time + ( countdownSeconds - 1 ) * 1000;" in duel_begin_body
	assert "if ( g_warmup.modificationCount != level.warmupModificationCount ) {" in g_main

	assert "g_warmupReadyDelay.integer <= 0" in ready_delay_body
	assert "level.readyUpDelayDeadline = level.time + g_warmupReadyDelay.integer * 1000;" in ready_delay_body
	assert "if ( g_warmupReadyDelayAction.integer == 1 ) {" in ready_delay_body
	assert "} else if ( g_warmupReadyDelayAction.integer == 2 ) {" in ready_delay_body

	assert 'config.timeoutLengthSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_timeoutLen, DEFAULT_TIMEOUT_LENGTH_SECONDS, "g_timeoutLen" );' in match_config_body
	assert 'config.timeoutCountPerTeam = G_MatchConfig_ReadNonNegativeCvar( &g_timeoutCount, DEFAULT_TIMEOUT_COUNT_PER_TEAM, "g_timeoutCount" );' in match_config_body
	assert "level.timeoutRemaining[team] = config->timeoutCountPerTeam;" in level_timers_body
	assert "G_UpdateMatchStateConfigString();" in level_timers_body


def test_domination_shuffle_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_domCapTime, "g_domCapTime", "5", CVAR_GAMERULE, 0, qfalse',
		'{ &g_domTeammateCapScale, "g_domTeammateCapScale", "0.5", CVAR_GAMERULE, 0, qfalse',
		'{ &g_domDistressThreshold, "g_domDistressThreshold", "75", CVAR_GAMERULE, 0, qfalse',
		'{ &g_domEnableContention, "g_domEnableContention", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_domNeutralFlag, "g_domNeutralFlag", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_domScoreRate, "g_domScoreRate", "5", CVAR_GAMERULE, 0, qfalse',
		'{ &g_shuffleTimedelay, "g_shuffle_timedelay", "5000", 0, 0, qfalse',
		'{ &g_shuffleMinPlayers, "g_shuffle_minplayers", "3", 0, 0, qfalse',
		'{ &g_shuffleAutomatic, "g_shuffle_automatic", "0", 0, 0, qfalse',
		'{ &g_shuffleAutomaticMinPlayers, "g_shuffle_automatic_minplayers", "6", 0, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_100870f0[0xd] = "g_domCapTime", 0',
		'char const data_10087080[0x16] = "g_domTeammateCapScale", 0',
		'char const data_100870d8[0x17] = "g_domDistressThreshold", 0',
		'char const data_100870bc[0x16] = "g_domEnableContention", 0',
		'char const data_100870a8[0x11] = "g_domNeutralFlag", 0',
		'char const data_10087098[0xf] = "g_domScoreRate", 0',
		'1008707c                                                                                      30 2e 35 00',
		'100870d2                                                        00 00 37 35 00 00',
		'char const data_100863b4[0x14] = "g_shuffle_timedelay", 0',
		'char const data_100863c8[0x15] = "g_shuffle_minplayers", 0',
		'char const data_100863e0[0x1f] = "g_shuffle_automatic_minplayers", 0',
		'char const data_10086400[0x14] = "g_shuffle_automatic", 0',
		'char const data_10086e6c[0x5] = "5000", 0',
		'100872b8                                                                          36 00 00 00',
		'100874e0  33 00 00 00',
	):
		assert snippet in qagame_strings

	domination_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e02c)[0xd] = data_100870f0 {"g_domCapTime"}',
		'char const (* data_1008e0bc)[0xb] = data_1007e25c {"g_doWarmup"}',
	)
	shuffle_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ef8c)[0x14] = data_10086400 {"g_shuffle_automatic"}',
		'char const (* data_1008efec)[0x16] = data_1008639c {"ui_singlePlayerActive"}',
	)

	assert domination_block.count("00 00 10 00") == 6
	assert "0x10087340" in domination_block
	assert "data_1008707c" in domination_block
	assert "0x100870d4" in domination_block
	assert "data_1007d1d8" in domination_block
	assert "data_1007d0a8" in domination_block

	assert "data_1007d0a8" in shuffle_block
	assert "0x100872b8" in shuffle_block
	assert "0x100874e0" in shuffle_block
	assert "data_10086e6c" in shuffle_block
	assert shuffle_block.count("00 00 00 00") >= 8


def test_domination_shuffle_cvars_keep_retail_behavioral_wiring() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")
	dom_capture_body = _function_body(g_team, "static int Team_DominationCaptureTime( void )")
	dom_score_body = _function_body(g_team, "static int Team_DominationScoreInterval( void )")
	dom_multiplier_body = _function_body(g_team, "static float Team_DominationCaptureMultiplier( int playerCount )")
	dom_update_body = _function_body(g_team, "static void Team_DominationUpdatePointState( dominationPoint_t *point, int captureTime )")
	dom_run_body = _function_body(g_team, "void Team_RunDomination( void )")
	dom_configstring_body = _function_body(g_main, "static void G_UpdateDominationCaptureTimeConfigstring( qboolean forceBroadcast )")
	shuffle_min_body = _function_body(g_team, "static int Team_GetAutoShuffleMinimumPlayers( void )")
	shuffle_should_body = _function_body(g_team, "static qboolean Team_ShouldAutoShuffle( const teamBalanceInfo_t *info )")
	shuffle_update_body = _function_body(g_team, "void Team_UpdateAutoShuffleState( void )")

	assert "seconds = g_domCapTime.integer;" in dom_capture_body
	assert "return seconds * 1000;" in dom_capture_body
	assert "seconds = g_domScoreRate.integer;" in dom_score_body
	assert "return seconds * 1000;" in dom_score_body
	assert "scale = g_domTeammateCapScale.value;" in dom_multiplier_body
	assert "if ( !g_domEnableContention.integer || redOccupants == blueOccupants ) {" in dom_update_body
	assert "if ( g_domEnableContention.integer ) {" in dom_update_body
	assert "point->neutralizing = ( g_domNeutralFlag.integer && point->ownerTeam != TEAM_FREE && point->ownerTeam != advanceTeam );" in dom_update_body
	assert "threshold = Com_Clamp( 0.0f, 100.0f, g_domDistressThreshold.value );" in dom_update_body
	assert "Team_DominationScoreInterval()" in dom_run_body
	assert "Team_DominationCaptureTime()" in dom_run_body
	assert "Com_sprintf( payload, sizeof( payload ), \"%f\", g_domCapTime.value );" in dom_configstring_body

	assert "int threshold = g_shuffleAutomaticMinPlayers.integer;" in shuffle_min_body
	assert "threshold = g_shuffleMinPlayers.integer;" in shuffle_min_body
	assert "if ( g_shuffleAutomatic.integer <= 0 ) {" in shuffle_should_body
	assert "delayMilliseconds = g_shuffleTimedelay.integer;" in shuffle_update_body
	assert "if ( delayMilliseconds <= 0 ) {" in shuffle_update_body
	assert "G_AutoShuffleCountdown_Arm( delayMilliseconds );" in shuffle_update_body
	assert "announceSeconds = ( delayMilliseconds + 999 ) / 1000;" in shuffle_update_body
	assert "delay * 1000" not in shuffle_update_body


def test_flag_physics_forced_override_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_flagBounce, "g_flagBounce", "0.25", CVAR_GAMERULE, 0, qfalse',
		'{ &g_flagPhysics, "g_flagPhysics", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_throwFlagVelocity, "g_throwFlagVelocity", "0", 0, 0, qfalse',
		'{ &g_throwFlagForwardMult, "g_throwFlagForwardMult", "2.5", 0, 0, qfalse',
		'{ &g_tackleFlag, "g_tackleFlag", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_droppedFlagBonus, "g_droppedFlagBonus", "1", CVAR_TEMP, 0, qfalse',
		'{ &g_neutralFlagPingTime, "g_neutralFlagPingRate", "2400", CVAR_GAMERULE, 0, qfalse',
		'{ &g_friendlyFireDampen, "g_friendlyFireDampen", "1.00", CVAR_GAMERULE, 0, qfalse',
		'{ &g_forceDmgThroughSurface, "g_forceDmgThroughSurface", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_forceAtmosphericEffects, "g_forceAtmosphericEffects", "", CVAR_GAMERULE, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_10086f64[0xd] = "g_flagBounce", 0',
		'char const data_10086f54[0xe] = "g_flagPhysics", 0',
		'char const data_10085e9c[0x14] = "g_throwFlagVelocity", 0',
		'char const data_10085e84[0x17] = "g_throwFlagForwardMult", 0',
		'10085e80  32 2e 35 00',
		'char const data_10085f34[0xd] = "g_tackleFlag", 0',
		'char const data_10087064[0x13] = "g_droppedFlagBonus", 0',
		'char const data_100868f0[0x16] = "g_neutralFlagPingRate", 0',
		'char const data_100868e8[0x5] = "2400", 0',
		'char const data_10086d1c[0x15] = "g_friendlyFireDampen", 0',
		'char const data_10086d14[0x5] = "1.00", 0',
		'char const data_10086f0c[0x19] = "g_forceDmgThroughSurface", 0',
		'char const data_10086ef0[0x1a] = "g_forceAtmosphericEffects", 0',
	):
		assert snippet in qagame_strings

	dropped_bonus_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e0ec)[0x13] = data_10087064 {"g_droppedFlagBonus"}',
		'char const (* data_1008e104)[0x14] = data_10087050 {"g_dropDamagedHealth"}',
	)
	flag_physics_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e23c)[0xd] = data_10086f64 {"g_flagBounce"}',
		'char const (* data_1008e26c)[0x12] = data_10086f40 {"g_floodprot_decay"}',
	)
	forced_override_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e29c)[0x19] = data_10086f0c {"g_forceDmgThroughSurface"}',
		'char const (* data_1008e2e4)[0x1e] = data_10086eb8 {"g_forceSmallScoreboardMessage"}',
	)
	friendly_fire_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e44c)[0xf] = data_10086d34 {"g_friendlyFire"}',
		'char const (* data_1008e47c)[0xc] = data_10086d08 {"g_gameState"}',
	)
	neutral_ping_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ea1c)[0x16] = data_100868f0 {"g_neutralFlagPingRate"}',
		'char const (* data_1008ea34)[0x10] = data_100868d8 {"g_obeliskHealth"}',
	)
	throw_tackle_block = _text_block(
		qagame_hlil,
		'char const (* data_1008f4fc)[0xd] = data_10085f34 {"g_tackleFlag"}',
		'char const (* data_1008f604)[0xa] = data_1007e274 {"timelimit"}',
	)

	assert "data_1007d1d8" in dropped_bonus_block
	assert "00 01 00 00" in dropped_bonus_block
	assert "data_100873d8" in flag_physics_block
	assert flag_physics_block.count("00 00 10 00") == 2
	assert "data_1007d0a8" in forced_override_block
	assert "data_1007c414" in forced_override_block
	assert forced_override_block.count("00 00 10 00") == 2
	assert "data_10086d14" in friendly_fire_block
	assert friendly_fire_block.count("00 00 10 00") == 2
	assert "data_100868e8" in neutral_ping_block
	assert "00 00 10 00" in neutral_ping_block
	assert "data_1007d0a8" in throw_tackle_block
	assert "0x10085e80" in throw_tackle_block
	assert throw_tackle_block.count("00 00 10 00") == 1


def test_flag_physics_forced_override_cvars_keep_retail_behavioral_wiring() -> None:
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_items = G_ITEMS_PATH.read_text(encoding="utf-8")
	g_local = G_LOCAL_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")
	update_flag_body = _function_body(g_main, "void G_UpdateFlagConfig( void )")
	item_velocity_body = _function_body(g_items, "static void G_BuildItemTossVelocity( gentity_t *ent, gitem_t *item, float angle, vec3_t velocity )")
	flag_velocity_body = _function_body(g_team, "static void G_BuildFlagDropVelocity( gentity_t *carrier, vec3_t velocity )")
	flag_physics_body = _function_body(g_team, "static void G_InitFlagDropPhysics( gentity_t *carrier, gentity_t *drop )")
	tackle_bonus_body = _function_body(g_team, "static qboolean G_HandleFlagTackleBonus( gentity_t *carrier, gentity_t *attacker, int flagTeam )")
	dropped_think_body = _function_body(g_team, "void Team_DroppedFlagThink( gentity_t *ent )")
	touch_flag_body = _function_body(g_team, "int Team_TouchOurFlag( gentity_t *ent, gentity_t *other, int team )")
	damage_body = _function_body(g_combat, "void G_Damage( gentity_t *targ, gentity_t *inflictor, gentity_t *attacker,\n\t\t\tvec3_t dir, vec3_t point, int damage, int dflags, int mod )")
	atmosphere_body = _function_body(g_main, "static const char *G_SelectForcedAtmosphere( void )")
	forced_body = _function_body(g_main, "void G_UpdateForcedCosmeticsConfigstring( qboolean forceBroadcast )")
	update_body = _function_body(g_main, "void G_UpdateCvars( void )")

	assert "float\t\tthrowFlagForwardMult;" in g_local
	assert "extern\tvmCvar_t\tg_friendlyFireDampen;" in g_local
	assert "g_flagConfig.flagBounce = bounce;" in update_flag_body
	assert "g_flagConfig.flagPhysics = ( g_flagPhysics.integer < 0 ) ? 0 : g_flagPhysics.integer;" in update_flag_body
	assert "g_flagConfig.throwFlagVelocity = ( g_throwFlagVelocity.integer < 0 ) ? 0 : g_throwFlagVelocity.integer;" in update_flag_body
	assert "g_flagConfig.throwFlagForwardMult = ( g_throwFlagForwardMult.value < 0.0f ) ? 0.0f : g_throwFlagForwardMult.value;" in update_flag_body
	assert "g_flagConfig.tackleFlag = ( g_tackleFlag.integer != 0 ) ? qtrue : qfalse;" in update_flag_body
	assert "g_flagConfig.droppedFlagBonus = ( g_droppedFlagBonus.integer < 0 ) ? 0 : g_droppedFlagBonus.integer;" in update_flag_body
	assert "g_flagConfig.neutralFlagPingTimeMs = ( g_neutralFlagPingTime.integer < 0 ) ? 0 : g_neutralFlagPingTime.integer;" in update_flag_body

	assert "if ( item->giType == IT_TEAM && g_flagConfig.flagPhysics ) {" in item_velocity_body
	assert "VectorScale( forward, g_flagConfig.throwFlagVelocity, velocity );" in item_velocity_body
	assert "VectorScale( ent->client->ps.velocity, g_flagConfig.throwFlagForwardMult, playerVelocity );" in item_velocity_body
	assert "velocity[2] += 200 + crandom() * 50;" in item_velocity_body
	assert "if ( g_flagConfig.flagPhysics > 0 ) {" in flag_velocity_body
	assert "VectorScale( forward, g_flagConfig.throwFlagVelocity, velocity );" in flag_velocity_body
	assert "VectorMA( velocity, g_flagConfig.throwFlagForwardMult, carrier->client->ps.velocity, velocity );" in flag_velocity_body
	assert "velocity[2] += 200.0f + crandom() * 50.0f;" in flag_velocity_body
	assert "drop->physicsBounce = bounce;" in flag_physics_body
	assert "if ( !g_flagConfig.tackleFlag ) {" in tackle_bonus_body
	assert "AddScore( attacker, carrier->r.currentOrigin, g_flagConfig.droppedFlagBonus );" in tackle_bonus_body
	assert "pingInterval = g_flagConfig.neutralFlagPingTimeMs;" in dropped_think_body
	assert "AddScore( other, ent->r.currentOrigin, g_flagConfig.droppedFlagBonus );" in touch_flag_body

	assert "if ( g_friendlyFireDampen.value != 1.0f ) {" in damage_body
	assert "friendlyFireScale = g_friendlyFireDampen.value;" in damage_body
	assert "damage = (int)( (float)damage * friendlyFireScale + 0.5f );" in damage_body
	assert "if ( g_forceAtmosphericEffects.string[0] ) {" in atmosphere_body
	assert 'Info_SetValueForKey( info, FORCED_COSMETICS_KEY_DAMAGE, g_forceDmgThroughSurface.integer ? "1" : "0" );' in forced_body
	assert "g_forceAtmosphericEffects.modificationCount != s_forceAtmosphericEffectsModCount" in update_body
	assert "g_forceDmgThroughSurface.modificationCount != s_forceDmgThroughSurfaceModCount" in update_body


def test_first_18_g_cvars_match_retail_defaults_flags_and_wiring() -> None:
	bg_public = BG_PUBLIC_PATH.read_text(encoding="utf-8")
	bg_pmove = (REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c").read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_cmds = G_CMDS_PATH.read_text(encoding="utf-8")
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_config = G_CONFIG_PATH.read_text(encoding="utf-8")
	g_items = G_ITEMS_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_missile = G_MISSILE_PATH.read_text(encoding="utf-8")
	g_spawn = G_SPAWN_PATH.read_text(encoding="utf-8")
	g_weapon = G_WEAPON_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_dmgThroughSurfaceAngularThreshold, "g_dmgThroughSurfaceAngularThreshold", "0.5f", CVAR_GAMERULE',
		'{ &g_dmgThroughSurfaceDampening, "g_dmgThroughSurfaceDampening", "0.5f", CVAR_GAMERULE',
		'{ &g_dmgThroughSurfaceDistance, "g_dmgThroughSurfaceDistance", "-33.1f", CVAR_GAMERULE',
		'{ &g_kamiAttenuate, "g_kamiAttenuate", "2048", CVAR_GAMERULE',
		'{ &g_kamiMinRatio, "g_kamiMinRatio", "0.1", CVAR_GAMERULE',
		'{ &g_maxFlightFuel, "g_maxFlightFuel", "16000", CVAR_GAMERULE',
		'{ &g_restarted, "g_restarted", "0", CVAR_ROM',
		'{ &g_rrDeathScorePenalty, "g_rrDeathScorePenalty", "-1", CVAR_GAMERULE',
		'{ &g_rrInfectedZombieFragBonus, "g_rrInfectedZombieFragBonus", "2", CVAR_GAMERULE',
		'{ &g_skipTrainingEnable, "g_skipTrainingEnable", "0", CVAR_SYSTEMINFO | CVAR_ROM',
		'{ &g_spawnArmor, "g_spawnArmor", "0", CVAR_GAMERULE',
		'{ &g_spawnArmorDmgScale, "g_spawnArmorDmgScale", "0.5", CVAR_GAMERULE',
		'{ &g_spawnDelay_key, "g_spawnDelay_key", "30", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE',
		'{ &g_spawnDelay_powerup, "g_spawnDelay_powerup", "45", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE',
		'{ NULL, "g_levelStartTime", "0", CVAR_SERVERINFO | CVAR_ROM',
		'{ &g_gametype, "g_gametype", "0", CVAR_SERVERINFO | CVAR_LATCH | CVAR_ROM',
		'{ &g_scorelimit, "scorelimit", "150", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART | CVAR_GAMERULE',
		'{ &g_enemyTeamRespawnRatio, "g_enemyTeamRespawnRatio", "1.5", CVAR_GAMERULE',
		'{ &g_switchTeamDelay, "g_switchTeamDelay", "3", CVAR_GAMERULE',
		'{ &g_armorTiered, "armor_tiered", "0", GAME_CVAR_FLAG_RETAIL_20000 | CVAR_GAMERULE',
		'{ &g_latchedHookOffset, "g_latchedHookOffset", "-2.0f", CVAR_GAMERULE',
		'{ &g_spawnMinDistance, "g_spawnMinDistance", "64", CVAR_GAMERULE',
		'{ &g_spawnRandomRatio, "g_spawnRandomRatio", "0.5", CVAR_GAMERULE',
		'{ &g_spawnDelayRandom_key, "g_spawnDelayRandom_key", "15", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE',
		'{ &g_spawnDelayRandom_powerup, "g_spawnDelayRandom_powerup", "15", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE',
		'{ &g_warmupDelay, "g_warmupDelay", "15", 0',
		'{ &g_training, "g_training", "0", CVAR_SYSTEMINFO | CVAR_GAMERULE',
		'{ &g_splashdamageOffset, "g_splashdamageOffset", "0.05", CVAR_GAMERULE',
	):
		assert row in g_main
	assert 'trap_Cvar_Register( NULL, "g_version", QL_GAME_VERSION, CVAR_ROM );' in g_main
	assert "G_RegisterCvarHelp" not in g_main

	for row in (
		'{ &g_regenHealthRate,      "g_regenHealthRate",      STRINGIZE( DEFAULT_REGEN_HEALTH_RATE_MILLISECONDS ), CVAR_GAMERULE',
		'{ &g_regenArmor,           "g_regenArmor",           STRINGIZE( DEFAULT_REGEN_ARMOR_DELAY_MILLISECONDS ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE',
		'{ &g_regenArmorRate,       "g_regenArmorRate",       STRINGIZE( DEFAULT_REGEN_ARMOR_RATE_MILLISECONDS ), CVAR_GAMERULE',
		'{ &g_regenArmorAfterHealth, "g_regenArmorAfterHealth", STRINGIZE( DEFAULT_REGEN_ARMOR_AFTER_HEALTH ), CVAR_GAMERULE',
	):
		assert row in g_config

	for snippet in (
		'char const data_1008714c[0x24] = "g_dmgThroughSurfaceAngularThreshold", 0',
		'char const data_10087124[0x1d] = "g_dmgThroughSurfaceDampening", 0',
		'char const data_10087108[0x1c] = "g_dmgThroughSurfaceDistance", 0',
		'char const data_10086c14[0x10] = "g_kamiAttenuate", 0',
		'char const data_10086bfc[0xf] = "g_kamiMinRatio", 0',
		'char const data_100869a4[0x10] = "g_maxFlightFuel", 0',
		'char const data_10084d8c[0x15] = "g_skipTrainingEnable", 0',
		'char const data_1008638c[0xd] = "g_spawnArmor", 0',
		'char const data_10086374[0x15] = "g_spawnArmorDmgScale", 0',
		'char const data_10086360[0x11] = "g_spawnDelay_key", 0',
		'char const data_10086330[0x15] = "g_spawnDelay_powerup", 0',
	):
		assert snippet in qagame_strings

	first_18_block = _text_block(
		qagame_hlil,
		"1008dfe4  char const (* data_1008dfe4)",
		"1008f0ac  char const (* data_1008f0ac)",
	)
	for snippet in (
		"data_1008714c",
		"g_dmgThroughSurfaceDampening",
		"g_dmgThroughSurfaceDistance",
		"g_kamiAttenuate",
		"g_kamiMinRatio",
		"g_maxFlightFuel",
		"g_regenArmor",
		"g_regenArmorAfterHealth",
		"g_regenArmorRate",
		"g_regenHealthRate",
		"g_restarted",
		"g_rrDeathScorePenalty",
		"g_rrInfectedZombieFragBonus",
		"g_skipTrainingEnable",
		"g_spawnArmor",
		"g_spawnArmorDmgScale",
		"g_spawnDelay_key",
		"g_spawnDelay_powerup",
	):
		assert snippet in first_18_block
	assert "48 00 00 00" in first_18_block
	assert "00 00 14 00" in first_18_block

	assert "STAT_PLAYER_ITEM_THRUST" in bg_public
	flight_move_body = _function_body(bg_pmove, "static void PM_FlyMove( void )")
	assert "static void G_ApplyFlightPowerupFuel" not in g_items
	assert "G_ClampFlightFuel" not in g_items
	assert "G_ApplyFlightPowerupFuel( other->client );" not in g_items
	assert "PM_BuildWishMove3D( wishdir, &wishspeed );" in flight_move_body
	assert "PM_Accelerate (wishdir, wishspeed, pm_flyaccelerate);" in flight_move_body
	assert "STAT_PLAYER_ITEM_THRUST" not in flight_move_body
	assert "STAT_PLAYER_ITEM_TIME" not in flight_move_body

	kami_body = _function_body(g_weapon, "static void KamikazeRadiusDamage( vec3_t origin, gentity_t *attacker, float damage, float radius )")
	assert "attenuate = g_kamiAttenuate.value;" in kami_body
	assert "minRatio = g_kamiMinRatio.value;" in kami_body
	assert "points = damage * ( 1.0f - dist / attenuate );" in kami_body

	damage_through_body = _function_body(g_combat, "static qboolean G_CanSplashDamageThroughSurface( int mod, float dist, float radius )")
	missile_through_body = _function_body(g_missile, "static qboolean G_ShouldEmitDamageThroughSurfaceImpact( const gentity_t *ent, const trace_t *trace )")
	assert "g_dmgThroughSurfaceDampening.value" in damage_through_body
	assert "g_dmgThroughSurfaceAngularThreshold.value" in missile_through_body
	assert "g_dmgThroughSurfaceDistance.value" in missile_through_body
	assert "EV_MISSILE_MISS_DMGTHROUGH" in g_missile

	spawn_armor_body = _function_body(g_client, "static void G_ApplySpawnArmor( gclient_t *client )")
	damage_body = _function_body(g_combat, "void G_Damage( gentity_t *targ, gentity_t *inflictor, gentity_t *attacker,\n\t\t\tvec3_t dir, vec3_t point, int damage, int dflags, int mod )")
	assert "client->ps.powerups[PW_NONE] = level.time - ( level.time % 1000 ) + g_spawnArmor.integer;" in spawn_armor_body
	assert "damage = (int)( (float)damage * spawnArmorScale );" in damage_body

	spawn_delay_body = _function_body(g_items, "void G_InitItemSpawnDelays( void )")
	finish_item_body = _function_body(g_items, "void FinishSpawningItem( gentity_t *ent )")
	assert "g_spawnDelayKeySeconds = G_ComputeRetailSpawnDelay( g_spawnDelay_key.integer" in spawn_delay_body
	assert "g_spawnDelayRandom_key.integer );" in spawn_delay_body
	assert "g_spawnDelayPowerupSeconds = G_ComputeRetailSpawnDelay( g_spawnDelay_powerup.integer" in spawn_delay_body
	assert "g_spawnDelayRandom_powerup.integer );" in spawn_delay_body
	assert "respawn = g_spawnDelayPowerupSeconds;" in finish_item_body
	assert "ent->item->giType == IT_KEY && g_spawnDelayKeySeconds > 0" in finish_item_body

	spawn_rank_body = _function_body(g_client, "static gentity_t *G_SelectRankedSpawnPointForTeamMode( gentity_t *spots[], int spotCount, team_t enemyTeam, qboolean requireInitial, vec3_t origin, vec3_t angles )")
	assert "#define\tMAX_RANKED_SPAWN_POINTS\t26" in g_client
	assert "#define\tRANKED_SPAWN_INITIAL_FLAG\t1" in g_client
	assert "#define\tRANKED_SPAWN_EXCLUDE_FLAG\t2" in g_client
	assert "static qboolean G_RankedSpawnPointAllowed( const gentity_t *spot ) {" in g_client
	assert "static qboolean G_RankedSpawnPointAllowedForMode( const gentity_t *spot, qboolean requireInitial ) {" in g_client
	assert "spot->spawnflags & RANKED_SPAWN_EXCLUDE_FLAG" in g_client
	assert "requireInitial && !( spot->spawnflags & RANKED_SPAWN_INITIAL_FLAG )" in g_client
	assert spawn_rank_body.count("G_RankedSpawnPointAllowedForMode( spot, requireInitial )") == 2
	assert "dist = delta[0];" in spawn_rank_body
	assert "if ( delta[1] > dist ) {" in spawn_rank_body
	assert "if ( g_enemyTeamRespawnRatio.value != 0.0f" in spawn_rank_body
	assert "&& ( enemyTeam == TEAM_RED || enemyTeam == TEAM_BLUE )" in spawn_rank_body
	assert "&& other->client->sess.sessionTeam == enemyTeam ) {" in spawn_rank_body
	assert "dist *= g_enemyTeamRespawnRatio.value;" in spawn_rank_body
	assert "selectionRatio = g_spawnRandomRatio.value;" in spawn_rank_body
	assert "if ( selectionRatio < 0.1f ) {" in spawn_rank_body
	assert "selectionRatio = 1.0f;" in spawn_rank_body
	assert "candidateCount = (float)rankedCount * selectionRatio;" in spawn_rank_body
	assert "if ( selectionCount < 3 ) {" in spawn_rank_body
	assert "if ( g_spawnMinDistance.integer > 0 ) {" in spawn_rank_body
	assert "rankedDistances[selectionCount - 1] < (float)g_spawnMinDistance.integer" in spawn_rank_body
	assert "return G_SelectRankedSpawnPointForTeam( spots, spotCount, TEAM_FREE, origin, angles );" in g_client
	assert "g_switchTeamDelay.integer ) );" in g_cmds
	assert "ent->client->switchTeamTime = level.time + g_switchTeamDelay.integer * 1000;" in g_cmds

	warmup_ready_body = _function_body(g_main, "qboolean G_WarmupReadyToStart( void )")
	assert "g_dedicated.integer && g_gametype.integer != GT_TOURNAMENT" in warmup_ready_body
	assert "level.time - level.startTime < g_warmupDelay.integer * 1000" in warmup_ready_body

	rr_death_body = _function_body(g_client, "void G_RRHandlePlayerDeath( team_t oldTeam, gentity_t *victim, gentity_t *attacker, int meansOfDeath )")
	assert "G_RRApplyScoreDelta( victim, g_rrDeathScorePenalty.integer );" in rr_death_body
	assert "G_RRApplyScoreDelta( attacker, g_rrInfectedZombieFragBonus.integer );" in rr_death_body
	assert 'trap_Cvar_Set( "g_restarted", "1" );' in g_main
	assert 'trap_Cvar_Set( "g_restarted", "0" );' in g_spawn
	assert 'trap_Cvar_Set( "g_skipTrainingEnable", "0" );' in g_cmds


def test_access_ad_flood_drop_knockback_and_vampiric_cvar_rows_match_retail_hlil_batch() -> None:
	g_config = G_CONFIG_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_accessFile, "g_accessFile", "access.txt", 0, 0, qfalse',
		'{ &g_adTouchScoreBonus, "g_adTouchScoreBonus", "1", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_adElimScoreBonus, "g_adElimScoreBonus", "2", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_adCaptureScoreBonus, "g_adCaptureScoreBonus", "3", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_floodprot_maxcount, "g_floodprot_maxcount", "10", 0, 0, qfalse',
		'{ &g_floodprot_decay, "g_floodprot_decay", "1000", 0, 0, qfalse',
		'{ &g_dropDamagedHealth, "g_dropDamagedHealth", "0", CVAR_TEMP | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_max_knockback, "g_max_knockback", "120", CVAR_GAMERULE, 0, qfalse',
		'{ &g_returnFlagOnSuicide, "g_returnFlagOnSuicide", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_vampiricDamage, "g_vampiricDamage", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse',
	):
		assert row in g_main

	assert '{ &g_max_knockback,        "g_max_knockback",        "120", CVAR_GAMERULE' in g_config
	assert "Upper clamp applied to positive computed knockback force." in g_main
	assert "Upper clamp applied to positive computed knockback force." in g_config

	for snippet in (
		'char const data_10087508[0xd] = "g_accessFile", 0',
		'char const data_100874fc[0xb] = "access.txt", 0',
		'char const data_100874b8[0x14] = "g_adTouchScoreBonus", 0',
		'char const data_100874cc[0x13] = "g_adElimScoreBonus", 0',
		'char const data_100874e4[0x16] = "g_adCaptureScoreBonus", 0',
		'100874e0  33 00 00 00',
		'char const data_10087050[0x14] = "g_dropDamagedHealth", 0',
		'char const data_10086f40[0x12] = "g_floodprot_decay", 0',
		'char const data_10086f28[0x15] = "g_floodprot_maxcount", 0',
		'char const data_100869cc[0x10] = "g_max_knockback", 0',
		'100869c8                          31 32 30 00',
		'char const data_10086660[0x16] = "g_returnFlagOnSuicide", 0',
		'char const data_10085e4c[0x11] = "g_vampiricDamage", 0',
	):
		assert snippet in qagame_strings

	access_bonus_block = _text_block(
		qagame_hlil,
		'char const (* data_1008daec)[0xd] = data_10087508 {"g_accessFile"}',
		'char const (* data_1008db4c)[0x18] = data_100874a0 {"g_allowCustomHeadmodels"}',
	)
	drop_health_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e104)[0x14] = data_10087050 {"g_dropDamagedHealth"}',
		'char const (* data_1008e11c)[0xf] = data_10087040 {"g_dropInactive"}',
	)
	flood_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e26c)[0x12] = data_10086f40 {"g_floodprot_decay"}',
		'char const (* data_1008e29c)[0x19] = data_10086f0c {"g_forceDmgThroughSurface"}',
	)
	max_knockback_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e8cc)[0x10] = data_100869cc {"g_max_knockback"}',
		'char const (* data_1008e8e4)[0xe] = data_1007c180 {"sv_maxclients"}',
	)
	return_flag_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ed4c)[0x16] = data_10086660 {"g_returnFlagOnSuicide"}',
		'char const (* data_1008ed64)[0x15] = data_10086648 {"g_rocketsplashOffset"}',
	)
	vampiric_block = _text_block(
		qagame_hlil,
		'char const (* data_1008f664)[0x11] = data_10085e4c {"g_vampiricDamage"}',
		'char const (* data_1008f67c)[0xf] = data_10085e3c {"g_velocity_bfg"}',
	)

	assert "data_100874fc" in access_bonus_block
	assert access_bonus_block.count("04 00 10 00") == 3
	assert "data_1007d0a8" in drop_health_block
	assert "00 01 14 00" in drop_health_block
	assert 'char const (* data_1008e270)[0x5] = data_1008747c {"1000"}' in flood_block
	assert "data_1007e194" in flood_block
	assert flood_block.count("00 00 00 00") >= 6
	assert "0x100869c8" in max_knockback_block
	assert "00 00 10 00" in max_knockback_block
	assert "data_1007d0a8" in return_flag_block
	assert "00 00 10 00" in return_flag_block
	assert "data_1007d0a8" in vampiric_block
	assert "00 00 14 00" in vampiric_block


def test_access_ad_flood_drop_knockback_and_vampiric_cvars_keep_retail_behavioral_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	g_cmds = G_CMDS_PATH.read_text(encoding="utf-8")
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_config = G_CONFIG_PATH.read_text(encoding="utf-8")
	g_items = G_ITEMS_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_svcmds = G_SVCMDS_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")

	active_flood_body = _function_body(g_active, "static qboolean G_CheckClientFlood( gentity_t *ent )")
	cmd_flood_body = _function_body(g_cmds, "static qboolean G_FloodLimited( gentity_t *ent, const char *action, qboolean recordUsage )")
	svcmd_flood_body = _function_body(g_svcmds, "static void Svcmd_FloodStatus_f( void )")
	knockback_config_body = _function_body(g_config, "void G_InitKnockbackConfig( void )")
	damage_body = _function_body(g_combat, "void G_Damage( gentity_t *targ, gentity_t *inflictor, gentity_t *attacker,\n\t\t\tvec3_t dir, vec3_t point, int damage, int dflags, int mod )")
	vampiric_body = _function_body(g_combat, "static void G_ApplyVampiricReward( gentity_t *targ, gentity_t *attacker, int healthDamage )")
	custom_mask_body = _function_body(g_main, "static uint64_t G_ComputeCustomSettingsMask( void )")
	dropped_health_body = _function_body(g_items, "static qboolean G_ShouldUseDroppedHealthCount( const gentity_t *ent )")
	flag_config_body = _function_body(g_main, "void G_UpdateFlagConfig( void )")
	access_load_body = _function_body(g_main, "static void G_LoadAdminAccessFile( void )")
	access_write_body = _function_body(g_main, "static void G_WriteAdminAccessFile( void )")

	for flood_body in (active_flood_body, cmd_flood_body, svcmd_flood_body):
		assert "maxCount = g_floodprot_maxcount.integer;" in flood_body
		assert "decay = g_floodprot_decay.integer;" in flood_body
		assert "maxCount <= 0 || decay <= 0" in flood_body

	assert 'trap_DropClient( ent - g_entities, "Dropped for flooding the server" );' in active_flood_body
	assert "client->floodCount++;" in cmd_flood_body

	assert "G_ADAwardBonus( attacker, self->r.currentOrigin, g_adElimScoreBonus.integer" in g_combat
	assert "G_ADAwardBonus( other, ent->r.currentOrigin, g_adCaptureScoreBonus.integer" in g_team
	assert "G_ADAwardBonus( other, ent->r.currentOrigin, g_adTouchScoreBonus.integer" in g_team
	assert "AddScore( player, origin, bonus );" in g_team
	assert "AddTeamScore( origin, player->client->sess.sessionTeam, bonus );" in g_team
	assert "G_ADAnnounceBonus( player, label, bonus );" in g_team
	assert 'Com_sprintf( command, sizeof( command ), "cp \\"%s ^7(+%i)\\"", label, bonus );' in g_team
	assert "G_TeamCommand( player->client->sess.sessionTeam, command );" in g_team

	assert "trap_FS_FOpenFile( g_accessFile.string, &handle, FS_READ );" in access_load_body
	assert "trap_FS_FOpenFile( g_accessFile.string, &handle, FS_WRITE );" in access_write_body
	assert "G_LoadAdminAccessFile();" in g_main

	assert 'g_knockbackConfig.maxKnockback = maxKnockback;' in knockback_config_body
	assert 'G_ReadKnockbackCvar( &g_max_knockback, DEFAULT_MAX_KNOCKBACK, "g_max_knockback" )' in knockback_config_body
	assert "maxKnockback = DEFAULT_MAX_KNOCKBACK;" in knockback_config_body
	assert "float maxKnockback = g_knockbackConfig.maxKnockback;" in damage_body
	assert "if ( maxKnockback <= 0.0f ) {" in damage_body
	assert damage_body.index("if ( maxKnockback <= 0.0f ) {") < damage_body.index("if ( knockbackValue > maxKnockback ) {")
	assert "if ( knockbackValue > maxKnockback ) {" in damage_body
	assert "knockbackValue = maxKnockback;" in damage_body

	assert "return g_dropDamagedHealth.integer ? qtrue : qfalse;" in dropped_health_body
	assert "if ( g_dropDamagedHealth.integer != 0 ) {" in custom_mask_body
	assert "mask |= CUSTOM_SETTING_DROP_HEALTH;" in custom_mask_body
	assert "vampiricScale = g_vampiricDamage.value;" in vampiric_body
	assert "healAmount = (int)( ( (float)healthDamage * vampiricScale ) + 0.5f );" in vampiric_body
	assert "G_ApplyVampiricReward( targ, attacker, take );" in damage_body
	assert "if ( g_vampiricDamage.value != 0.0f ) {" in custom_mask_body
	assert "mask |= CUSTOM_SETTING_VAMPIRIC_DAMAGE;" in custom_mask_body
	assert "g_flagConfig.returnOnSuicide = ( g_returnFlagOnSuicide.integer != 0 ) ? qtrue : qfalse;" in flag_config_body


def test_team_loadout_bot_and_drop_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_teamSpawnAsSpec, "g_teamSpawnAsSpec", "0", 0, 0, qfalse',
		'{ &g_teamSpecFreeCam, "g_teamSpecFreeCam", "0", 0, 0, qfalse',
		'{ &g_teamSpecSayEnable, "g_teamSpecSayEnable", "1", 0, 0, qfalse',
		'{ &g_teamSizeMin, "g_teamSizeMin", "1", CVAR_SERVERINFO, 0, qfalse',
		'{ &g_teamForcePresent, "g_teamForcePresent", "1", 0, 0, qfalse',
		'{ &g_disableLoadout, "g_disableLoadout", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_botSpawnList, "g_botSpawnList", "", 0, 0, qfalse',
		'{ &g_droppedPowerupsDecay, "g_droppedPowerupsDecay", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_dropPowerups, "g_dropPowerups", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_dropSkulls, "g_dropSkulls", "1", CVAR_GAMERULE, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_100822ac[0xf] = "g_botSpawnList", 0',
		'char const data_10085eb0[0x14] = "g_teamSpecSayEnable", 0',
		'char const data_10085ec4[0x12] = "g_teamSpecFreeCam", 0',
		'char const data_10085ed8[0x12] = "g_teamSpawnAsSpec", 0',
		'char const data_10085eec[0xe] = "g_teamSizeMin", 0',
		'char const data_10085efc[0x13] = "g_teamForcePresent", 0',
		'char const data_10087008[0xd] = "g_dropSkulls", 0',
		'char const data_10087018[0xf] = "g_dropPowerups", 0',
		'char const data_10087028[0x17] = "g_droppedPowerupsDecay", 0',
		'char const data_10087178[0x11] = "g_disableLoadout", 0',
	):
		assert snippet in qagame_strings

	bot_block = _text_block(
		qagame_hlil,
		'char const (* data_1008dc9c)[0xf] = data_100822ac {"g_botSpawnList"}',
		'char const (* data_1008dcb4)[0xd] = data_10087384 {"capturelimit"}',
	)
	disable_block = _text_block(
		qagame_hlil,
		'char const (* data_1008dfb4)[0x11] = data_10087178 {"g_disableLoadout"}',
		'char const (* data_1008dfcc)[0x8] = data_10087170 {"dmflags"}',
	)
	drop_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e134)[0x17] = data_10087028 {"g_droppedPowerupsDecay"}',
		'char const (* data_1008e17c)[0x13] = data_10086ff4 {"g_enableDebugTrace"}',
	)
	team_block = _text_block(
		qagame_hlil,
		'char const (* data_1008f544)[0x13] = data_10085efc {"g_teamForcePresent"}',
		'char const (* data_1008f5d4)[0x14] = data_10085e9c {"g_throwFlagVelocity"}',
	)

	assert "data_1007c414" in bot_block
	assert "00 00 00 00" in bot_block
	assert "data_1007d0a8" in disable_block
	assert "00 00 10 00" in disable_block
	assert drop_block.count("data_1007d1d8") == 3
	assert drop_block.count("00 00 10 00") == 3
	assert "data_1007d1d8" in team_block
	assert "data_1007d0a8" in team_block
	assert "data_10083e8c {\"teamsize\"}" in team_block
	assert "04 00 00 00" in team_block
	assert team_block.count("00 00 00 00") >= 5


def test_team_loadout_bot_and_drop_cvars_keep_retail_behavioral_wiring() -> None:
	g_bot = G_BOT_PATH.read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_cmds = G_CMDS_PATH.read_text(encoding="utf-8")
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_items = G_ITEMS_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_rankings = (REPO_ROOT / "src" / "code" / "game" / "g_rankings.c").read_text(encoding="utf-8")
	g_session = (REPO_ROOT / "src" / "code" / "game" / "g_session.c").read_text(encoding="utf-8")
	g_spawn = G_SPAWN_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")
	g_vote = (REPO_ROOT / "src" / "code" / "game" / "g_vote.c").read_text(encoding="utf-8")

	bot_list_body = _function_body(g_bot, "static qboolean G_ConsumeBotSpawnList( void )")
	minplayers_body = _function_body(g_bot, "void G_CheckMinimumPlayers( void )")
	update_cvars_body = _function_body(g_main, "void G_UpdateCvars( void )")
	team_minimum_body = _function_body(g_team, "qboolean Team_HasMinimumPlayersForWarmup( void )")
	team_ratio_body = _function_body(g_team, "int Team_GetRespawnRatioForTeam( team_t team )")

	assert "trap_Cvar_Update( &g_botSpawnList );" in bot_list_body
	assert "G_CountHumanPlayers( -1 ) <= 0" in bot_list_body
	assert 'trap_Cvar_Set( "g_botSpawnList", "" );' in bot_list_body
	assert 'trap_SendConsoleCommand( EXEC_INSERT, va( "addbot %s %f %s %i\\n", bot, skill, "", 0 ) );' in bot_list_body
	assert 'trap_Cvar_Set( "g_botSpawnList", remainder );' in bot_list_body
	assert "if (checkminimumplayers_time > level.time - 1000) {" in minplayers_body
	assert "if (G_ConsumeBotSpawnList()) return;" in minplayers_body

	assert "required = Team_GetRequiredPlayersPerTeam();" in team_minimum_body
	assert "if ( g_teamForcePresent.integer ) {" in team_minimum_body
	assert "return ( info.redCount >= required && info.blueCount >= required ) ? qtrue : qfalse;" in team_minimum_body
	assert "required = Team_GetRequiredPlayersPerTeam();" in team_ratio_body
	assert "return ( count * 100 ) / required;" in team_ratio_body
	assert 'trap_Cvar_Set( "g_teamSizeMin", arg );' in g_cmds
	assert 'trap_Cvar_Set( "g_teamSizeMin", va( "%i", size ) );' in g_vote

	assert "if ( !level.teamLocks[team] && !g_teamSpawnAsSpec.integer ) {" in g_cmds
	assert "if ( g_teamSpawnAsSpec.integer && g_gametype.integer >= GT_TEAM && level.warmupTime != 0 ) {" in g_session
	assert "G_DefaultSpectatorState" not in g_cmds
	assert "ent->client->sess.spectatorState = SPECTATOR_FREE;" in g_cmds
	assert "G_ADResolveFollowTarget" not in g_team
	assert "FollowCycle( ent, 1 );" in g_team
	assert "ent->client->sess.spectatorState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;" in g_rankings
	assert "client->sess.sessionTeam == TEAM_SPECTATOR && !g_teamSpecFreeCam.integer" in g_client
	assert "if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR && !g_teamSpecSayEnable.integer ) {" in g_cmds
	assert "Spectator chat is disabled while g_teamSpecSayEnable is 0." in g_cmds

	assert "trap_Cvar_Update( &g_disableLoadout );" in g_spawn
	assert "trap_Cvar_Update( &g_loadout );" in g_spawn
	assert "serverMask = G_ParseDisableLoadoutString( g_disableLoadout.string );" in g_spawn
	assert 'trap_Cvar_Set( "g_disableLoadout", va( "%u", level.disableLoadoutMapMask ) );' in g_spawn
	assert "g_disableLoadout.modificationCount != s_disableLoadoutModCount" in update_cvars_body
	assert "disabledMask = level.disableLoadoutMapMask | serverMask;" in g_spawn
	assert "G_WriteDisableLoadoutConfigstrings( disabledMask, (unsigned int)g_factoryCvarConfig.startingWeaponsMask );" in g_spawn
	assert "g_loadout.modificationCount != s_loadoutModCount" in update_cvars_body
	assert "g_startingWeapons.modificationCount != s_startingWeaponsModCount" in update_cvars_body
	assert "loadoutConfigstringsDirty = qtrue;" in update_cvars_body

	for cvar_name in (
		"g_droppedPowerupsDecay",
		"g_dropPowerups",
		"g_dropSkulls",
	):
		assert cvar_name not in g_combat
		assert cvar_name not in g_items
		assert cvar_name not in g_team


def test_logging_debug_dropcmd_and_best_weapon_cvar_rows_match_retail_hlil_batch() -> None:
	g_local = G_LOCAL_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_log, "g_log", "", CVAR_ARCHIVE, 0, qfalse',
		'{ &g_logSync, "g_logSync", "0", CVAR_ARCHIVE, 0, qfalse',
		'{ &g_bestStartingWeapons, "g_bestStartingWeapons", "gh bfg rl lg rg hmg cg sg pg mg ng gl g pl", CVAR_GAMERULE, 0, qfalse',
		'{ &g_damagePlums, "g_damagePlums", "2", CVAR_GAMERULE, 0, qfalse',
		'{ &g_debugFlags, "g_debugFlags", "0", 0, 0, qfalse',
		'{ &g_debugInactivity, "g_debugInactivity", "0", 0, 0, qfalse',
		'{ &g_debugThawTime, "g_debugThawTime", "0", 0, 0, qfalse',
		'{ &g_debugVampiricDamage, "g_debugVampiricDamage", "0", 0, 0, qfalse',
		'{ &g_dropCmds, "g_dropCmds", "7", CVAR_GAMERULE, 0, qfalse',
		'{ &g_enableDebugTrace, "g_enableDebugTrace", "0", 0, 0, qfalse',
	):
		assert row in g_main

	for extern in (
		"extern vmCvar_t g_log;",
		"extern vmCvar_t g_logSync;",
		"extern vmCvar_t g_bestStartingWeapons;",
		"extern vmCvar_t g_damagePlums;",
		"extern vmCvar_t g_debugFlags;",
		"extern vmCvar_t g_debugInactivity;",
		"extern vmCvar_t g_debugThawTime;",
		"extern vmCvar_t g_debugVampiricDamage;",
		"extern vmCvar_t g_dropCmds;",
		"extern vmCvar_t g_enableDebugTrace;",
	):
		assert extern in g_local

	for snippet in (
		'char const data_100869e8[0x6] = "g_log", 0',
		'char const data_100869dc[0xa] = "g_logSync", 0',
		'char const data_10087394[0x2b] = "gh bfg rl lg rg hmg cg sg pg mg ng gl g pl", 0',
		'char const data_100873c0[0x16] = "g_bestStartingWeapons", 0',
		'char const data_10087210[0xe] = "g_damagePlums", 0',
		'char const data_100871e0[0xd] = "g_debugFlags", 0',
		'char const data_100871cc[0x12] = "g_debugInactivity", 0',
		'char const data_100871b0[0x10] = "g_debugThawTime", 0',
		'char const data_10087198[0x16] = "g_debugVampiricDamage", 0',
		'char const data_100854b8[0xb] = "g_dropCmds", 0',
		'10087077',
		'37 00 00 00',
		'char const data_10086ff4[0x13] = "g_enableDebugTrace", 0',
	):
		assert snippet in qagame_strings

	retail_rows = {
		"g_log": ('1008e89c  char const (* data_1008e89c)[0x6] = data_100869e8 {"g_log"}', "data_1007c414", "01 00 00 00"),
		"g_logSync": ('1008e8b4  char const (* data_1008e8b4)[0xa] = data_100869dc {"g_logSync"}', "data_1007d0a8", "01 00 00 00"),
		"g_bestStartingWeapons": ('1008dc84  char const (* data_1008dc84)[0x16] = data_100873c0 {"g_bestStartingWeapons"}', "data_10087394", "00 00 10 00"),
		"g_damagePlums": ('1008dedc  char const (* data_1008dedc)[0xe] = data_10087210 {"g_damagePlums"}', "data_1007d53c", "00 00 10 00"),
		"g_debugFlags": ('1008df24  char const (* data_1008df24)[0xd] = data_100871e0 {"g_debugFlags"}', "data_1007d0a8", "00 00 00 00"),
		"g_debugInactivity": ('1008df3c  char const (* data_1008df3c)[0x12] = data_100871cc {"g_debugInactivity"}', "data_1007d0a8", "00 00 00 00"),
		"g_debugThawTime": ('1008df6c  char const (* data_1008df6c)[0x10] = data_100871b0 {"g_debugThawTime"}', "data_1007d0a8", "00 00 00 00"),
		"g_debugVampiricDamage": ('1008df84  char const (* data_1008df84)[0x16] = data_10087198 {"g_debugVampiricDamage"}', "data_1007d0a8", "00 00 00 00"),
		"g_dropCmds": ('1008e0d4  char const (* data_1008e0d4)[0xb] = data_100854b8 {"g_dropCmds"}', "0x10087078", "00 00 10 00"),
		"g_enableDebugTrace": ('1008e17c  char const (* data_1008e17c)[0x13] = data_10086ff4 {"g_enableDebugTrace"}', "data_1007d0a8", "00 00 00 00"),
	}
	for marker, default_marker, flags_marker in retail_rows.values():
		row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
		assert default_marker in row_block
		assert flags_marker in row_block


def test_logging_debug_dropcmd_and_best_weapon_cvars_keep_retail_behavioral_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")
	init_body = _function_body(g_main, "void G_InitGame( int levelTime, int randomSeed, int restart )")
	log_body = _function_body(g_main, "void QDECL G_LogPrintf( const char *fmt, ... )")
	drop_cmds_body = _function_body(g_active, "static void G_SetDropCmdsAttackLockout( qboolean lockout )")
	lockout_body = _function_body(g_active, "void G_SetAllActiveClientAttackLockout( qboolean lockout )")

	assert "g_gametype.integer != GT_SINGLE_PLAYER && g_log.string[0]" in init_body
	assert "if ( g_logSync.integer ) {" in init_body
	assert "trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND_SYNC );" in init_body
	assert "trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND );" in init_body
	assert 'G_Printf( "WARNING: Couldn\'t open logfile: %s\\n", g_log.string );' in init_body
	assert "if ( !level.logFile ) {" in log_body
	assert "trap_FS_Write( string, strlen( string ), level.logFile );" in log_body

	assert "trap_Cvar_Update( &g_dropCmds );" in drop_cmds_body
	assert "dropCmds = g_dropCmds.integer;" in drop_cmds_body
	assert "dropCmds |= PMF_ATTACK_LOCKOUT;" in drop_cmds_body
	assert "dropCmds &= ~PMF_ATTACK_LOCKOUT;" in drop_cmds_body
	assert 'trap_Cvar_Set( "g_dropCmds", va( "%i", dropCmds ) );' in drop_cmds_body
	assert "G_SetDropCmdsAttackLockout( lockout );" in lockout_body
	assert lockout_body.index("G_SetDropCmdsAttackLockout( lockout );") < lockout_body.index("for ( clientNum = 0; clientNum < level.maxclients; clientNum++ )")

	assert "g_damagePlums.integer" not in g_combat
	for expected in (
		'1004c4a3                                  int32_t var_4c_5 = data_105aaeac | 4',
		'1004c4c3                                  ecx = (*(data_104b13ac + 0x3c))("g_dropCmds",',
		'1004c714                              int32_t var_4c_11 = eax_45 & 0xfffffffb',
		'1004c737                              ecx = (*(data_104b13ac + 0x3c))("g_dropCmds",',
	):
		assert expected in qagame_hlil


def test_round_freeze_timing_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_roundWarmupDelay, "g_roundWarmupDelay", "10000", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_roundDrawLivingCount, "g_roundDrawLivingCount", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_roundDrawHealthCount, "g_roundDrawHealthCount", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeThawTime, "g_freezeThawTime", "2000", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeThawTick, "g_freezeThawTick", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeThawRadius, "g_freezeThawRadius", "96", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeRoundDelay, "g_freezeRoundDelay", "4000", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeProtectedSpawnTime, "g_freezeProtectedSpawnTime", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeEnvironmentalRespawnDelay, "g_freezeEnvironmentalRespawnDelay", "5000", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeAutoThawTime, "g_freezeAutoThawTime", "120000", CVAR_GAMERULE, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_100865f4[0x6] = "10000", 0',
		'char const data_100865fc[0x13] = "g_roundWarmupDelay", 0',
		'char const data_10086610[0x17] = "g_roundDrawLivingCount", 0',
		'char const data_10086628[0x17] = "g_roundDrawHealthCount", 0',
		'char const data_10086d78[0x5] = "2000", 0',
		'char const data_10086d80[0x11] = "g_freezeThawTime", 0',
		'char const data_10086d94[0x11] = "g_freezeThawTick", 0',
		'10086da5                 00 00 00 39 36 00 00',
		'char const data_10086dac[0x13] = "g_freezeThawRadius", 0',
		'char const data_10086dc0[0x5] = "4000", 0',
		'char const data_10086dc8[0x13] = "g_freezeRoundDelay", 0',
		'char const data_10086e50[0x1b] = "g_freezeProtectedSpawnTime", 0',
		'char const data_10086e6c[0x5] = "5000", 0',
		'char const data_10086e74[0x22] = "g_freezeEnvironmentalRespawnDelay", 0',
		'char const data_10086e98[0x7] = "120000", 0',
		'char const data_10086ea0[0x15] = "g_freezeAutoThawTime", 0',
	):
		assert snippet in qagame_strings

	round_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ed7c)[0x17] = data_10086628 {"g_roundDrawHealthCount"}',
		'char const (* data_1008edc4)[0xb] = data_100865e8 {"roundlimit"}',
	)
	freeze_auto_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e314)[0x15] = data_10086ea0 {"g_freezeAutoThawTime"}',
		"1008e324  void* data_1008e324",
	)
	freeze_env_block = _text_block(
		qagame_hlil,
		"1008e32c  char const (* data_1008e32c)",
		"1008e33c  void* data_1008e33c",
	)
	freeze_protect_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e344)[0x1b] = data_10086e50 {"g_freezeProtectedSpawnTime"}',
		"1008e354  void* data_1008e354",
	)
	freeze_round_thaw_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e3bc)[0x13] = data_10086dc8 {"g_freezeRoundDelay"}',
		'char const (* data_1008e41c)[0x1b] = data_10086d5c {"g_freezeThawThroughSurface"}',
	)

	assert round_block.count("data_1007d1d8") == 2
	assert "data_100865f4" in round_block
	assert round_block.count("00 00 10 00") == 2
	assert "04 00 10 00" in round_block
	assert "data_10086e98" in freeze_auto_block
	assert "00 00 10 00" in freeze_auto_block
	assert "data_10086e6c" in freeze_env_block
	assert "00 00 10 00" in freeze_env_block
	assert "data_1007d0a8" in freeze_protect_block
	assert "00 00 10 00" in freeze_protect_block
	assert "data_10086dc0" in freeze_round_thaw_block
	assert "0x10086da8" in freeze_round_thaw_block
	assert "data_1007d1d8" in freeze_round_thaw_block
	assert "data_10086d78" in freeze_round_thaw_block
	assert freeze_round_thaw_block.count("00 00 10 00") == 3
	assert "04 00 10 00" in freeze_round_thaw_block


def test_round_freeze_timing_cvars_keep_retail_behavioral_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_combat = G_COMBAT_PATH.read_text(encoding="utf-8")
	g_freeze = G_FREEZE_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	ca_winner_body = _function_body(g_active, "static team_t G_CAResolveRoundWinner( const int counts[TEAM_NUM_TEAMS], const int health[TEAM_NUM_TEAMS] )")
	freeze_sync_body = _function_body(g_active, "void G_FreezeSyncCvars( void )")
	warmup_schedule_body = _function_body(g_active, "static void G_RoundScheduleWarmupDelay( void )")
	warmup_update_body = _function_body(g_active, "void G_RoundHandleWarmupDelayCvarUpdate( void )")
	freeze_winner_body = _function_body(g_active, "static team_t G_FreezeEvaluateRoundWinner( const int counts[TEAM_NUM_TEAMS], const int health[TEAM_NUM_TEAMS] )")
	freeze_end_body = _function_body(g_active, "static void G_FreezeHandleRoundEnd( team_t winner )")
	freeze_count_body = _function_body(g_freeze, "int G_FreezeCountThawHelpers( gentity_t *ent, gentity_t **helperOut )")
	freeze_state_body = _function_body(g_freeze, "static void G_FreezeSetClientFrozenState( gentity_t *ent, qboolean frozen, qboolean environmental, qboolean wasAuto, int helperNum )")
	client_end_body = _function_body(g_client, "void G_FreezeClientEndFrame( gentity_t *ent )")
	update_body = _function_body(g_main, "void G_UpdateCvars( void )")
	damage_body = _function_body(g_combat, "void G_Damage( gentity_t *targ, gentity_t *inflictor, gentity_t *attacker,\n\t\t\tvec3_t dir, vec3_t point, int damage, int dflags, int mod )")

	assert "if ( g_roundDrawLivingCount.integer && counts[TEAM_RED] != counts[TEAM_BLUE] ) {" in ca_winner_body
	assert "if ( health && g_roundDrawHealthCount.integer && health[TEAM_RED] != health[TEAM_BLUE] ) {" in ca_winner_body
	assert "if ( g_roundDrawLivingCount.integer && counts[TEAM_RED] != counts[TEAM_BLUE] ) {" in freeze_winner_body
	assert "if ( health && g_roundDrawHealthCount.integer && health[TEAM_RED] != health[TEAM_BLUE] ) {" in freeze_winner_body
	assert "if ( g_roundDrawLivingCount.integer ) {" in freeze_end_body
	assert "if ( g_roundDrawHealthCount.integer ) {" in freeze_end_body

	assert "delay = g_roundWarmupDelay.integer;" in warmup_schedule_body
	assert "level.warmupTime = level.time + delay;" in warmup_schedule_body
	assert "delay = g_roundWarmupDelay.integer;" in warmup_update_body
	assert "level.roundTransitionTime = ( delay > 0 ) ? level.time + delay : level.time;" in warmup_update_body
	assert "G_RoundHandleWarmupDelayCvarUpdate();" in update_body

	for expected in (
		"config->thawTime = g_freezeThawTime.integer;",
		"config->thawTick = g_freezeThawTick.integer;",
		"config->thawRadius = g_freezeThawRadius.integer;",
		"config->roundDelay = g_freezeRoundDelay.integer;",
		"config->protectedSpawnTime = ( g_freezeProtectedSpawnTime.integer > 0 )",
		"config->environmentalRespawnDelay = ( g_freezeEnvironmentalRespawnDelay.integer > 0 )",
		"config->autoThawTime = ( g_freezeAutoThawTime.integer > 0 )",
	):
		assert expected in freeze_sync_body

	assert "thawTick = level.freezeConfig.thawTick;" in client_end_body
	assert "thawTotal = level.freezeConfig.thawTime;" in client_end_body
	assert "client->freezeAccumulatedThaw += helperCount * thawTick;" in client_end_body
	assert "client->freezeNextThawTick = level.time + thawTick;" in client_end_body
	assert "if ( client->freezeAutoThawTime > 0 && level.time >= client->freezeAutoThawTime ) {" in client_end_body
	assert "client->freezeEnvironmentalRespawnTime > 0" in client_end_body
	assert "thawRadius = (float)level.freezeConfig.thawRadius;" in freeze_count_body
	assert "VectorLengthSquared( delta ) > thawRadius * thawRadius" in freeze_count_body
	assert "delay = level.freezeConfig.roundDelay;" in freeze_end_body
	assert "level.roundTransitionTime = ( delay > 0 ) ? level.time + delay : level.time;" in freeze_end_body
	assert "client->freezeAutoThawTime = level.time + level.freezeConfig.autoThawTime;" in freeze_state_body
	assert "client->freezeEnvironmentalRespawnTime = level.time + level.freezeConfig.environmentalRespawnDelay;" in freeze_state_body
	assert "protectTime = level.freezeConfig.protectedSpawnTime;" in freeze_state_body
	assert "client->freezeProtectedUntil = client->invulnerabilityTime;" in freeze_state_body
	assert "if ( G_FreezeGametypeEnabled() && client->freezeProtectedUntil > level.time ) {" in damage_body


def test_freeze_last_man_and_rr_zombie_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")
	qagame_usage = QAGAME_HLIL_PART01_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_freezeThawWinningTeam, "g_freezeThawWinningTeam", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeThawThroughSurface, "g_freezeThawThroughSurface", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeResetWeaponsOnRound, "g_freezeResetWeaponsOnRound", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeResetHealthOnRound, "g_freezeResetHealthOnRound", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeResetArmorOnRound, "g_freezeResetArmorOnRound", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_freezeRemovePowerupsOnRound, "g_freezeRemovePowerupsOnRound", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_lastManStandingWarning, "g_lastManStandingWarning", "1", 0, 0, qfalse',
		'{ &g_lastManStandingMessage, "g_lastManStandingMessage", "You are the last standing", 0, 0, qfalse',
		'{ &g_rrInfectedZombieHealthBonus, "g_rrInfectedZombieHealthBonus", "50", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedZombieSpeed, "g_rrInfectedZombieSpeed", "1.15", CVAR_GAMERULE, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_10086d44[0x18] = "g_freezeThawWinningTeam", 0',
		'char const data_10086d5c[0x1b] = "g_freezeThawThroughSurface", 0',
		'char const data_10086ddc[0x1c] = "g_freezeResetWeaponsOnRound", 0',
		'char const data_10086df8[0x1b] = "g_freezeResetHealthOnRound", 0',
		'char const data_10086e14[0x1a] = "g_freezeResetArmorOnRound", 0',
		'char const data_10086e30[0x1e] = "g_freezeRemovePowerupsOnRound", 0',
		'char const data_10086a30[0x19] = "g_lastManStandingWarning", 0',
		'char const data_10086a4c[0x1a] = "You are the last standing", 0',
		'char const data_10086a68[0x19] = "g_lastManStandingMessage", 0',
		'char const data_10086440[0x5] = "1.15", 0',
		'char const data_10086448[0x18] = "g_rrInfectedZombieSpeed", 0',
		'char const data_10086460[0x1e] = "g_rrInfectedZombieHealthBonus", 0',
	):
		assert snippet in qagame_strings

	freeze_reset_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e35c)[0x1e] = data_10086e30 {"g_freezeRemovePowerupsOnRound"}',
		'char const (* data_1008e3bc)[0x13] = data_10086dc8 {"g_freezeRoundDelay"}',
	)
	freeze_thaw_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e41c)[0x1b] = data_10086d5c {"g_freezeThawThroughSurface"}',
		'char const (* data_1008e44c)[0xf] = data_10086d34 {"g_friendlyFire"}',
	)
	last_man_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e824)[0x19] = data_10086a68 {"g_lastManStandingMessage"}',
		'char const (* data_1008e854)[0x14] = data_10086a1c {"g_latchedHookOffset"}',
	)
	rr_zombie_block = _text_block(
		qagame_hlil,
		'char const (* data_1008ef14)[0x1e] = data_10086460 {"g_rrInfectedZombieHealthBonus"}',
		'char const (* data_1008ef44)[0x14] = data_1008642c {"g_rrRoundScoreBonus"}',
	)

	for snippet in (
		'char const (* data_1008e35c)[0x1e] = data_10086e30 {"g_freezeRemovePowerupsOnRound"}',
		'char const (* data_1008e374)[0x1a] = data_10086e14 {"g_freezeResetArmorOnRound"}',
		'char const (* data_1008e38c)[0x1b] = data_10086df8 {"g_freezeResetHealthOnRound"}',
		'char const (* data_1008e3a4)[0x1c] = data_10086ddc {"g_freezeResetWeaponsOnRound"}',
	):
		assert snippet in freeze_reset_block
	assert freeze_reset_block.count("data_1007d1d8") == 4
	assert freeze_reset_block.count("00 00 10 00") == 4

	assert 'char const (* data_1008e41c)[0x1b] = data_10086d5c {"g_freezeThawThroughSurface"}' in freeze_thaw_block
	assert 'char const (* data_1008e434)[0x18] = data_10086d44 {"g_freezeThawWinningTeam"}' in freeze_thaw_block
	assert "data_1007d0a8" in freeze_thaw_block
	assert "data_1007d1d8" in freeze_thaw_block
	assert freeze_thaw_block.count("00 00 10 00") == 2

	assert 'char const (* data_1008e824)[0x19] = data_10086a68 {"g_lastManStandingMessage"}' in last_man_block
	assert 'char const (* data_1008e828)[0x1a] = data_10086a4c {"You are the last standing"}' in last_man_block
	assert 'char const (* data_1008e83c)[0x19] = data_10086a30 {"g_lastManStandingWarning"}' in last_man_block
	assert "data_1007d1d8" in last_man_block
	assert "1008e82c                                      00 00 00 00" in last_man_block
	assert "1008e844              00 00 00 00" in last_man_block

	assert 'char const (* data_1008ef14)[0x1e] = data_10086460 {"g_rrInfectedZombieHealthBonus"}' in rr_zombie_block
	assert 'char const (* data_1008ef2c)[0x18] = data_10086448 {"g_rrInfectedZombieSpeed"}' in rr_zombie_block
	assert "data_1007e1fc" in rr_zombie_block
	assert 'char const (* data_1008ef30)[0x5] = data_10086440 {"1.15"}' in rr_zombie_block
	assert rr_zombie_block.count("00 00 10 00") == 2
	assert "*(ecx + 0x2c8) = data_105a778c + data_1059a40c" in qagame_strings
	assert "ebp[0xd] = int.d(float.s(ebp[0xd]) f* data_10599208)" in qagame_usage


def test_freeze_last_man_and_rr_zombie_cvars_keep_retail_behavioral_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_freeze = G_FREEZE_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")
	freeze_sync_body = _function_body(g_active, "void G_FreezeSyncCvars( void )")
	freeze_reset_body = _function_body(g_active, "void G_FreezeResetClientForRound( gentity_t *ent )")
	freeze_winner_body = _function_body(g_active, "static team_t G_FreezeEvaluateRoundWinner( const int counts[TEAM_NUM_TEAMS], const int health[TEAM_NUM_TEAMS] )")
	freeze_thaw_winners_body = _function_body(g_active, "static void G_FreezeThawWinningPlayers( team_t winner )")
	freeze_count_body = _function_body(g_freeze, "int G_FreezeCountThawHelpers( gentity_t *ent, gentity_t **helperOut )")
	last_warning_body = _function_body(g_team, "qboolean G_LastManStandingWarningsEnabled( void )")
	last_message_body = _function_body(g_team, "static const char *G_LastManStandingMessage( void )")
	last_notify_body = _function_body(g_team, "static qboolean G_NotifyLastAlivePlayer( team_t team )")
	ad_notify_body = _function_body(g_team, "qboolean G_ADNotifyLastAlivePlayer( team_t team )")
	ca_notify_body = _function_body(g_team, "qboolean G_CANotifyLastAlivePlayer( team_t team )")
	freeze_notify_body = _function_body(g_team, "qboolean G_FreezeNotifyLastAlivePlayer( team_t team )")
	rr_notify_body = _function_body(g_team, "qboolean G_RRNotifyLastAlivePlayer( team_t team )")
	rr_spawn_body = _function_body(g_client, "static void G_RRFinalizeSpawnLoadout( gentity_t *ent )")
	rr_process_body = _function_body(g_client, "void G_RRProcessClient( gentity_t *ent )")

	for expected in (
		"config->thawThroughSurface = g_freezeThawThroughSurface.integer ? qtrue : qfalse;",
		"config->thawWinningTeam = g_freezeThawWinningTeam.integer ? qtrue : qfalse;",
		"config->resetWeapons = g_freezeResetWeaponsOnRound.integer ? qtrue : qfalse;",
		"config->resetHealth = g_freezeResetHealthOnRound.integer ? qtrue : qfalse;",
		"config->resetArmor = g_freezeResetArmorOnRound.integer ? qtrue : qfalse;",
		"config->removePowerups = g_freezeRemovePowerupsOnRound.integer ? qtrue : qfalse;",
	):
		assert expected in freeze_sync_body

	assert "if ( level.freezeConfig.resetWeapons ) {" in freeze_reset_body
	assert "G_RequestClientSpawn( ent, warmupSpawn, qfalse );" in freeze_reset_body
	assert "if ( level.freezeConfig.resetHealth ) {" in freeze_reset_body
	assert "if ( level.freezeConfig.resetArmor ) {" in freeze_reset_body
	assert "if ( level.freezeConfig.removePowerups ) {" in freeze_reset_body
	assert "memset( ent->client->ps.powerups, 0, sizeof( ent->client->ps.powerups ) );" in freeze_reset_body
	assert "if ( !level.freezeConfig.thawThroughSurface ) {" in freeze_count_body
	assert freeze_winner_body.count("G_FreezeThawWinningPlayers( winner );") >= 5
	assert "if ( !level.freezeConfig.thawWinningTeam ) {" in freeze_thaw_winners_body
	assert "G_FreezeThawClient( ent, qtrue, -1 );" in freeze_thaw_winners_body

	assert "if ( !g_lastManStandingWarning.integer ) {" in last_warning_body
	assert "if ( level.timeoutActive ) {" in last_warning_body
	assert "if ( g_lastManStandingMessage.string[0] ) {" in last_message_body
	assert 'return "You are the last standing";' in last_message_body
	assert "G_BroadcastGlobalTeamSound( vec3_origin, GTS_LAST_STANDING, -1, team, 0 );" in last_notify_body
	assert 'va( "cp \\"%s\\\\n\\"", G_LastManStandingMessage() )' in last_notify_body
	for body in (ad_notify_body, ca_notify_body, freeze_notify_body, rr_notify_body):
		assert "if ( !G_LastManStandingWarningsEnabled() ) {" in body
		assert "return G_NotifyLastAlivePlayer( team );" in body

	assert "client->pers.maxHealth = client->ps.stats[STAT_MAX_HEALTH] + g_rrInfectedZombieHealthBonus.integer;" in rr_spawn_body
	assert "client->ps.stats[STAT_MAX_HEALTH] = client->pers.maxHealth;" in rr_spawn_body
	assert "ent->health = client->ps.stats[STAT_HEALTH] = client->pers.maxHealth;" in rr_spawn_body
	assert "if ( g_rrInfectedZombieSpeed.value > 0.0f ) {" in rr_process_body
	assert "ent->client->ps.speed *= g_rrInfectedZombieSpeed.value;" in rr_process_body


def test_red_rover_infection_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_rrAllowNegativeScores, "g_rrAllowNegativeScores", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrDamageScoreBonus, "g_rrDamageScoreBonus", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfected, "g_rrInfected", "0", CVAR_LATCH | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedSpreadTime, "g_rrInfectedSpreadTime", "40", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedSpreadWarningTime, "g_rrInfectedSpreadWarningTime", "10", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedSurvivorMinSpeed, "g_rrInfectedSurvivorMinSpeed", "500.0f", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedSurvivorPingRate, "g_rrInfectedSurvivorPingRate", "2000", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedSurvivorScoreBonus, "g_rrInfectedSurvivorScoreBonus", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedSurvivorScoreMethod, "g_rrInfectedSurvivorScoreMethod", "2", CVAR_GAMERULE, 0, qfalse',
		'{ &g_rrInfectedSurvivorScoreRate, "g_rrInfectedSurvivorScoreRate", "30", CVAR_GAMERULE, 0, qfalse',
	):
		assert row in g_main

	for snippet in (
		'char const data_100865bc[0x18] = "g_rrAllowNegativeScores", 0',
		'char const data_100865a4[0x15] = "g_rrDamageScoreBonus", 0',
		'char const data_1008657c[0xd] = "g_rrInfected", 0',
		'1008740d                                         00 00 00 34 30 00 00',
		'char const data_10086564[0x17] = "g_rrInfectedSpreadTime", 0',
		'char const data_10086544[0x1e] = "g_rrInfectedSpreadWarningTime", 0',
		'char const data_1008651c[0x7] = "500.0f", 0',
		'char const data_10086524[0x1d] = "g_rrInfectedSurvivorMinSpeed", 0',
		'char const data_100864fc[0x1d] = "g_rrInfectedSurvivorPingRate", 0',
		'char const data_100864dc[0x1f] = "g_rrInfectedSurvivorScoreBonus", 0',
		'char const data_100864bc[0x20] = "g_rrInfectedSurvivorScoreMethod", 0',
		'char const data_1008649c[0x1e] = "g_rrInfectedSurvivorScoreRate", 0',
		'1007d53c                                                                                      32 00 00 00',
		'1008732c                                      33 30 00 00',
	):
		assert snippet in qagame_strings

	rr_block = _text_block(
		qagame_hlil,
		'char const (* data_1008edf4)[0x18] = data_100865bc {"g_rrAllowNegativeScores"}',
		'char const (* data_1008ef5c)[0x8] = data_10086424 {"g_runes"}',
	)

	for snippet in (
		'char const (* data_1008edf4)[0x18] = data_100865bc {"g_rrAllowNegativeScores"}',
		'char const (* data_1008ee0c)[0x15] = data_100865a4 {"g_rrDamageScoreBonus"}',
		'char const (* data_1008ee3c)[0xd] = data_1008657c {"g_rrInfected"}',
		'char const (* data_1008ee54)[0x17] = data_10086564 {"g_rrInfectedSpreadTime"}',
		'char const (* data_1008ee6c)[0x1e] = data_10086544 {"g_rrInfectedSpreadWarningTime"}',
		'char const (* data_1008ee84)[0x1d] = data_10086524 {"g_rrInfectedSurvivorMinSpeed"}',
		'char const (* data_1008ee9c)[0x1d] = data_100864fc {"g_rrInfectedSurvivorPingRate"}',
		'char const (* data_1008eeb4)[0x1f] = data_100864dc {"g_rrInfectedSurvivorScoreBonus"}',
		'char const (* data_1008eecc)[0x20] = data_100864bc {"g_rrInfectedSurvivorScoreMethod"}',
		'char const (* data_1008eee4)[0x1e] = data_1008649c {"g_rrInfectedSurvivorScoreRate"}',
	):
		assert snippet in rr_block

	assert "20 00 14 00" in rr_block
	assert rr_block.count("00 00 10 00") == 14
	assert "0x10087410" in rr_block
	assert "data_1007e194" in rr_block
	assert "data_1008651c" in rr_block
	assert "data_10086d78" in rr_block
	assert "data_1007d1d8" in rr_block
	assert "data_1007d53c" in rr_block
	assert "data_1008732c" in rr_block
	assert rr_block.count("data_1007d0a8") >= 4


def test_red_rover_infection_cvars_keep_retail_behavioral_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_cmds = G_CMDS_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_team = G_TEAM_PATH.read_text(encoding="utf-8")
	rr_active_body = _function_body(g_client, "static qboolean G_RRIsActive( void )")
	rr_apply_score_body = _function_body(g_client, "static void G_RRApplyScoreDelta( gentity_t *ent, int score )")
	rr_apply_raw_body = _function_body(g_client, "static void G_RRApplyRawScoreDelta( gentity_t *ent, int score )")
	rr_survival_body = _function_body(g_client, "static void G_RRApplySurvivalBonus( qboolean forceAward )")
	rr_set_state_body = _function_body(g_client, "static void G_RRSetClientState( gentity_t *ent, rrInfectionState_t state, qboolean announce )")
	rr_warn_body = _function_body(g_client, "static void G_RRWarnSurvivor( gentity_t *ent )")
	rr_spread_body = _function_body(g_client, "static void G_RRCheckInfectionSpread( void )")
	rr_process_body = _function_body(g_client, "void G_RRProcessClient( gentity_t *ent )")
	rr_winner_body = _function_body(g_client, "static team_t G_RRResolveCompletedRoundWinner( const int counts[TEAM_NUM_TEAMS] )")
	rr_completion_body = _function_body(g_client, "static qboolean G_RRCheckRoundCompletion( const int counts[TEAM_NUM_TEAMS] )")
	rr_completed_body = _function_body(g_client, "void G_RRHandleCompletedRound( void )")
	rr_death_body = _function_body(g_client, "void G_RRHandlePlayerDeath( team_t oldTeam, gentity_t *victim, gentity_t *attacker, int meansOfDeath )")
	rr_damage_body = _function_body(g_client, "void G_RRHandleDamageScore( gentity_t *attacker, gentity_t *targ, int damage )")
	rr_next_body = _function_body(g_active, "static rrRoundState_t G_RRNextRestartState( void )")
	rr_init_body = _function_body(g_active, "void G_RRInitRoundController( void )")
	rr_auto_join_body = _function_body(g_cmds, "static team_t G_RRResolveAutoJoinTeam( int clientNum )")
	rr_ping_config_body = _function_body(g_main, "static void G_UpdateRRInfectedSurvivorPingRateConfigstring( qboolean forceBroadcast )")
	custom_settings_body = _function_body(g_main, "static uint64_t G_ComputeCustomSettingsMask( void )")
	rr_last_alive_body = _function_body(g_team, "qboolean G_RRNotifyLastAlivePlayer( team_t team )")

	assert "if ( !g_rrInfected.integer ) {" in rr_active_body
	assert "return g_rrInfected.integer ? RR_ROUNDSTATE_INFECTION_SEED : RR_ROUNDSTATE_WARMUP;" in rr_next_body
	assert "if ( g_rrInfected.integer ) {" in rr_init_body
	assert "if ( g_gametype.integer != GT_RED_ROVER || !g_rrInfected.integer ) {" in rr_auto_join_body
	assert "if ( g_gametype.integer != GT_RED_ROVER || !g_rrInfected.integer ) {" in rr_last_alive_body
	assert "mask |= CUSTOM_SETTING_INFECTED;" in custom_settings_body

	assert "if ( score < 0 && !g_rrAllowNegativeScores.integer ) {" in rr_apply_score_body
	assert "if ( score < 0 && !g_rrAllowNegativeScores.integer ) {" in rr_apply_raw_body
	assert "bonus = G_RRResolveScoreValue( damage * g_rrDamageScoreBonus.value );" in rr_damage_body

	assert "scoreMethod = g_rrInfectedSurvivorScoreMethod.integer;" in rr_survival_body
	assert "scoreRateSeconds = g_rrInfectedSurvivorScoreRate.integer;" in rr_survival_body
	assert "score = G_RRResolveScoreValue( g_rrInfectedSurvivorScoreBonus.value );" in rr_survival_body
	assert "if ( g_rrInfectedSurvivorScoreMethod.integer == 0 ) {" in rr_damage_body
	assert "threshold = g_rrInfectedSurvivorScoreRate.integer;" in rr_damage_body
	assert "bonus = G_RRResolveScoreValue( g_rrInfectedSurvivorScoreBonus.value );" in rr_damage_body

	assert "spreadDelay = g_rrInfectedSpreadTime.integer;" in rr_set_state_body
	assert "warningDelay = g_rrInfectedSpreadWarningTime.integer;" in rr_set_state_body
	assert "ent->client->rrInfectionNextPingTime = level.time + g_rrInfectedSurvivorPingRate.integer;" in rr_set_state_body
	assert "if ( g_rrInfectedSurvivorPingRate.integer <= 0 ) {" in rr_warn_body
	assert "ent->client->rrInfectionNextPingTime = level.time + g_rrInfectedSurvivorPingRate.integer;" in rr_warn_body
	assert "if ( g_rrInfectedSpreadTime.integer <= 0 || level.rrLastInfectionTime < 0 ) {" in rr_spread_body
	assert "spreadDelayMs = g_rrInfectedSpreadTime.integer * 1000;" in rr_spread_body
	assert "warningDelayMs = g_rrInfectedSpreadWarningTime.integer * 1000;" in rr_spread_body
	assert "g_rrInfectedSpreadWarningTime.integer," in rr_spread_body
	assert "minSpeed = g_rrInfectedSurvivorMinSpeed.value;" in rr_process_body
	assert "ent->client->rrInfectionNextPingTime = level.time + g_rrInfectedSurvivorPingRate.integer;" in rr_process_body
	assert 'Com_sprintf( payload, sizeof( payload ), "%f", g_rrInfectedSurvivorPingRate.value );' in rr_ping_config_body
	assert "trap_SetConfigstring( CS_RR_INFECTED_SURVIVOR_PING_RATE, payload );" in rr_ping_config_body

	assert "if ( g_rrInfected.integer || level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE] ) {" in rr_winner_body
	assert "if ( g_rrInfected.integer && counts[TEAM_BLUE] == 1 ) {" in rr_completion_body
	assert "nextState = g_rrInfected.integer ? RR_ROUNDSTATE_INFECTION_SEED : RR_ROUNDSTATE_WARMUP;" in rr_completed_body
	assert "if ( !g_rrInfected.integer || oldTeam == TEAM_BLUE ) {" in rr_death_body
	assert "G_RRApplySurvivalBonus( qtrue );" in rr_death_body
	assert "G_RRApplyScoreDelta( victim, g_rrDeathScorePenalty.integer );" in rr_death_body
	assert "G_RRApplyScoreDelta( attacker, g_rrInfectedZombieFragBonus.integer );" in rr_death_body


def test_player_appearance_laghax_and_instagib_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")
	qagame_strings = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")

	assert "#define GAME_CVAR_FLAG_RETAIL_10000\t0x00010000" in g_main

	for row in (
		'{ &g_allowCustomHeadmodels, "g_allowCustomHeadmodels", "0", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_playerCylinders, "g_playerCylinders", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_playerheadmodelOverride, "g_playerheadmodelOverride", "", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_playerheadScale, "g_playerheadScale", "1.0", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_playerheadScaleOffset, "g_playerheadScaleOffset", "1.0", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_playermodelOverride, "g_playermodelOverride", "", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_playerModelScale, "g_playerModelScale", "1.1", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse',
		'{ &g_lagHaxHistory, "g_lagHaxHistory", "4", CVAR_LATCH, 0, qfalse',
		'{ &g_lagHaxMs, "g_lagHaxMs", "80", CVAR_LATCH, 0, qfalse',
		'{ &g_instaGib, "g_instaGib", "0", CVAR_SERVERINFO | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse },',
	):
		assert row in g_main

	for snippet in (
		'char const data_100874a0[0x18] = "g_allowCustomHeadmodels", 0',
		'char const data_1008685c[0x12] = "g_playerCylinders", 0',
		'char const data_10086840[0x1a] = "g_playerheadmodelOverride", 0',
		'char const data_1008682c[0x12] = "g_playerheadScale", 0',
		'char const data_10086814[0x18] = "g_playerheadScaleOffset", 0',
		'char const data_100867fc[0x16] = "g_playermodelOverride", 0',
		'char const data_100867e8[0x13] = "g_playerModelScale", 0',
		'100867e1     00 00 00 31 2e 31 00',
		'char const data_10086a94[0x10] = "g_lagHaxHistory", 0',
		'10086a90                                                  34 00 00 00',
		'char const data_10086a84[0xb] = "g_lagHaxMs", 0',
		'10087260  38 30 00 00',
		'char const data_10086c58[0xb] = "g_instaGib", 0',
		'10086ce0  31 2e 30 00',
	):
		assert snippet in qagame_strings

	allow_headmodels_block = _text_block(
		qagame_hlil,
		'char const (* data_1008db4c)[0x18] = data_100874a0 {"g_allowCustomHeadmodels"}',
		'char const (* data_1008db64)[0xf] = data_10087490 {"g_allowForfeit"}',
	)
	instagib_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e56c)[0xb] = data_10086c58 {"g_instaGib"}',
		'char const (* data_1008e584)[0x10] = data_10086c48 {"g_ironsights_mg"}',
	)
	laghax_block = _text_block(
		qagame_hlil,
		'char const (* data_1008e7f4)[0x10] = data_10086a94 {"g_lagHaxHistory"}',
		'char const (* data_1008e824)[0x19] = data_10086a68 {"g_lastManStandingMessage"}',
	)
	player_block = _text_block(
		qagame_hlil,
		'char const (* data_1008eac4)[0x12] = data_1008685c {"g_playerCylinders"}',
		'char const (* data_1008eb54)[0xd] = data_10082204 {"g_podiumDist"}',
	)

	assert "data_1007d0a8" in allow_headmodels_block
	assert "00 00 11 00" in allow_headmodels_block
	assert "data_1007d0a8" in instagib_block
	assert "04 00 14 00" in instagib_block
	assert "data_10086a90" in laghax_block
	assert "0x10087260" in laghax_block
	assert laghax_block.count("20 00 00 00") == 2
	assert "data_1007d1d8" in player_block
	assert "00 00 10 00" in player_block
	assert "data_1007c414" in player_block
	assert player_block.count("0x10086ce0") == 2
	assert "0x100867e4" in player_block
	assert player_block.count("00 00 11 00") == 5


def test_player_appearance_laghax_and_instagib_cvars_keep_retail_behavioral_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_pmove = G_PMOVE_PATH.read_text(encoding="utf-8")
	g_weapon = ( REPO_ROOT / "src" / "code" / "game" / "g_weapon.c" ).read_text(encoding="utf-8")
	match_keys = MATCH_STATE_KEYS_PATH.read_text(encoding="utf-8")
	update_body = _function_body(g_main, "void G_UpdateCvars( void )")
	player_cylinders_body = _function_body(g_main, "static void G_UpdatePlayerCylindersConfigstring( qboolean forceBroadcast )")
	player_appearance_body = _function_body(g_main, "static void G_UpdatePlayerAppearanceConfigstring( qboolean forceBroadcast )")
	custom_settings_body = _function_body(g_main, "static uint64_t G_ComputeCustomSettingsMask( void )")
	admin_config_body = _function_body(g_main, "static void G_SyncAdminConfig( void )")
	client_userinfo_body = _function_body(g_client, "void ClientUserinfoChanged( int clientNum )")
	laghax_init_body = _function_body(g_active, "void G_InitLagHaxHistory( void )")
	laghax_store_body = _function_body(g_active, "void G_StoreHistory( gentity_t *ent )")
	laghax_shift_body = _function_body(g_active, "void G_TimeShiftAllClients( gentity_t *skip, int time )")
	laghax_restore_body = _function_body(g_active, "void G_UnTimeShiftAllClients( void )")
	pmove_cache_body = _function_body(g_pmove, "static void G_PmoveCacheSettings( void )")
	pmove_reset_body = _function_body(g_pmove, "void G_PmoveResetFactoryManagedCvars( void )")
	pmove_refresh_body = _function_body(g_pmove, "void G_RefreshPmoveSettings( void )")

	for expected in (
		'#define PLAYER_APPEARANCE_KEY_PLAYERMODEL_OVERRIDE "g_playermodelOverride"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERHEADMODEL_OVERRIDE "g_playerheadmodelOverride"',
		'#define PLAYER_APPEARANCE_KEY_ALLOW_CUSTOM_HEADMODELS "g_allowCustomHeadmodels"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE "g_playerheadScale"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE_OFFSET "g_playerheadScaleOffset"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERMODEL_SCALE "g_playerModelScale"',
	):
		assert expected in match_keys

	assert 'Com_sprintf( payload, sizeof( payload ), "%i", g_playerCylinders.integer );' in player_cylinders_body
	assert "trap_SetConfigstring( CS_PLAYER_CYLINDERS, payload );" in player_cylinders_body
	assert "G_UpdatePlayerCylindersConfigstring( qfalse );" in update_body

	for expected in (
		"Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_OVERRIDE, g_playermodelOverride.string );",
		"Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEADMODEL_OVERRIDE, g_playerheadmodelOverride.string );",
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_ALLOW_CUSTOM_HEADMODELS, va( "%i", g_allowCustomHeadmodels.integer ) );',
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE, va( "%g", g_playerheadScale.value ) );',
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE_OFFSET, va( "%g", g_playerheadScaleOffset.value ) );',
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_SCALE, va( "%g", g_playerModelScale.value ) );',
		"trap_SetConfigstring( CS_PLAYER_APPEARANCE, payload );",
	):
		assert expected in player_appearance_body
	assert "G_UpdatePlayerAppearanceConfigstring( qfalse );" in update_body

	for expected in (
		"level.adminConfig.allowCustomHeadmodels = ( g_allowCustomHeadmodels.integer != 0 ) ? qtrue : qfalse;",
		"level.adminConfig.playerCylinders = ( g_playerCylinders.integer != 0 ) ? qtrue : qfalse;",
		"level.adminConfig.playerModelScale = g_playerModelScale.value;",
		"level.adminConfig.playerHeadScale = g_playerheadScale.value;",
		"level.adminConfig.playerHeadScaleOffset = g_playerheadScaleOffset.value;",
	):
		assert expected in admin_config_body

	for expected in (
		"if ( g_playermodelOverride.string[0] || g_playerheadmodelOverride.string[0] ) {",
		"Info_SetValueForKey( userinfo, \"model\", g_playermodelOverride.string );",
		"Info_SetValueForKey( userinfo, \"team_model\", g_playermodelOverride.string );",
		"Info_SetValueForKey( userinfo, \"headmodel\", g_playerheadmodelOverride.string );",
		"Info_SetValueForKey( userinfo, \"team_headmodel\", g_playerheadmodelOverride.string );",
	):
		assert expected in client_userinfo_body

	assert "historyCount = g_lagHaxHistory.integer;" in laghax_init_body
	assert "if ( historyCount <= 0 || g_lagHaxMs.integer <= 0 ) {" in laghax_init_body
	assert "G_StoreHistory( ent );" in g_active
	assert "history = history->next;" in laghax_store_body
	assert "if ( g_lagHaxMs.integer <= 0 || g_lagHaxHistory.integer <= 0 ) {" in laghax_shift_body
	assert "earliestTime = level.time - g_lagHaxMs.integer;" in laghax_shift_body
	assert "if ( g_lagHaxMs.integer <= 0 || g_lagHaxHistory.integer <= 0 ) {" in laghax_restore_body
	assert "&& g_lagHaxHistory.integer > 0" in g_weapon
	assert "&& g_lagHaxMs.integer > 0" in g_weapon
	assert "G_TimeShiftAllClients( ent, ent->client->ps.commandTime );" in g_weapon
	assert "G_UnTimeShiftAllClients();" in g_weapon

	assert "if ( g_instaGib.integer != 0 ) {" in pmove_cache_body
	assert "noPlayerClip = qtrue;" in pmove_cache_body
	assert "g_pmoveSettings.noPlayerClip = noPlayerClip;" in pmove_cache_body
	assert 'trap_Cvar_Set( "g_instaGib", "0" );' in pmove_reset_body
	assert 'G_PmoveUpdateCvar( &g_instaGib, "g_instaGib", qfalse );' in pmove_refresh_body
	assert "mask |= CUSTOM_SETTING_INSTAGIB;" in custom_settings_body
	assert '"INSTAGIB",' in g_main


def test_classic_server_gameplay_cvar_rows_match_retail_hlil_batch() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	hlil_part02 = QAGAME_HLIL_PART02_PATH.read_text(encoding="utf-8")
	hlil_part03 = QAGAME_HLIL_PART03_PATH.read_text(encoding="utf-8")

	for row in (
		'{ &g_speed, "g_speed", "320", CVAR_GAMERULE, 0, qtrue  },',
		'{ &g_gravity, "g_gravity", "800", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qtrue  },',
		'{ &g_weaponRespawn, "g_weaponRespawn", "5", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qtrue  },',
		'{ &g_inactivity, "g_inactivity", "0", 0, 0, qtrue },',
		'{ &g_inactivityWarning, "g_inactivityWarning", "10", 0, 0, qtrue',
		'{ &g_dropInactive, "g_dropInactive", "1", 0, 0, qfalse',
		'{ &g_debugMove, "g_debugMove", "0", 0, 0, qfalse },',
		'{ &g_debugDamage, "g_debugDamage", "0", 0, 0, qfalse },',
		'{ &g_teamAutoJoin, "g_teamAutoJoin", "0", CVAR_ARCHIVE, 0, qfalse',
		'{ &g_teamForceBalance, "g_teamForceBalance", "1", CVAR_ARCHIVE | CVAR_SERVERINFO',
	):
		assert row in g_main

	for snippet in (
		'char const data_10086254[0x8] = "g_speed", 0',
		'00 33 32 30 00',
		'char const data_10086cc0[0xa] = "g_gravity", 0',
		'38 30 30 00',
		'char const data_10085d58[0x10] = "g_weaponRespawn", 0',
		'35 00 00 00',
		'char const data_10086c88[0xd] = "g_inactivity", 0',
		'char const data_10086c74[0x14] = "g_inactivityWarning", 0',
		'31 30 00 00',
		'char const data_10087040[0xf] = "g_dropInactive", 0',
		'char const data_100871c0[0xc] = "g_debugMove", 0',
		'char const data_100871f0[0xe] = "g_debugDamage", 0',
		'char const data_10085f24[0xf] = "g_teamAutoJoin", 0',
		'char const data_10085f10[0x13] = "g_teamForceBalance", 0',
	):
		assert snippet in hlil_part02

	for snippet in (
		'char const (* data_1008f184)[0x8] = data_10086254 {"g_speed"}',
		'1008f18c                                      00 00 10 00',
		'char const (* data_1008e4dc)[0xa] = data_10086cc0 {"g_gravity"}',
		'1008e4e4              04 00 10 00',
		'char const (* data_1008f7b4)[0x10] = data_10085d58 {"g_weaponRespawn"}',
		'1008f7bc                                                                                      04 00 10 00',
		'char const (* data_1008e524)[0xd] = data_10086c88 {"g_inactivity"}',
		'void* data_1008e534 = sub_10052090',
		'char const (* data_1008e53c)[0x14] = data_10086c74 {"g_inactivityWarning"}',
		'char const (* data_1008e11c)[0xf] = data_10087040 {"g_dropInactive"}',
		'char const (* data_1008df54)[0xc] = data_100871c0 {"g_debugMove"}',
		'char const (* data_1008df0c)[0xe] = data_100871f0 {"g_debugDamage"}',
		'char const (* data_1008f514)[0xf] = data_10085f24 {"g_teamAutoJoin"}',
		'1008f51c                                                                                      01 00 00 00',
		'char const (* data_1008f52c)[0x13] = data_10085f10 {"g_teamForceBalance"}',
		'1008f534                                                              05 00 00 00',
	):
		assert snippet in hlil_part03


def test_legacy_game_only_cvars_are_not_registered_or_wired() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_local = G_LOCAL_PATH.read_text(encoding="utf-8")
	g_client = G_CLIENT_PATH.read_text(encoding="utf-8")
	g_bot = (REPO_ROOT / "src" / "code" / "game" / "g_bot.c").read_text(encoding="utf-8")
	g_items = G_ITEMS_PATH.read_text(encoding="utf-8")
	g_cmds = G_CMDS_PATH.read_text(encoding="utf-8")
	flag_config_body = _function_body(g_main, "void G_UpdateFlagConfig( void )")
	client_spawn_body = _function_body(g_client, "void ClientSpawn(gentity_t *ent)")
	pickup_weapon_body = _function_body(g_items, "int Pickup_Weapon (gentity_t *ent, gentity_t *other)")
	cmd_cvar_body = _function_body(g_cmds, "void Cmd_Cvar_f( gentity_t *ent )")
	cmd_team_body = _function_body(g_cmds, "void Cmd_Team_f( gentity_t *ent )")

	for cvar_name in (
		"g_maxGameClients",
		"g_quadfactor",
		"g_weaponTeamRespawn",
		"g_forcerespawn",
		"g_listEntity",
		"g_pauseAudio",
		"g_rankings",
		"g_floodprot_penalty",
		"g_spawnProtect",
		"g_flagDroppedTimeout",
		"g_enableBreath",
		"g_forcedAtmosphere",
		"g_damage_mg_team",
		"g_nailgravity",
		"g_ruleset",
		"g_synchronousClients",
		"g_factoryRespawnDelay",
		"g_factoryWarmupSpawnDelay",
		"g_factoryAllowItemDrops",
		"g_factoryAllowItemBounce",
		"g_redteam",
		"g_blueteam",
	):
		assert f'"{cvar_name}"' not in g_main
		assert f"vmCvar_t\t{cvar_name}" not in g_main
		assert f"vmCvar_t\t{cvar_name}" not in g_local
		assert f"vmCvar_t {cvar_name}" not in g_local

	assert "g_weaponTeamRespawn.integer" not in pickup_weapon_body
	assert "return g_weaponRespawn.integer;" in pickup_weapon_body
	assert '"g_quadfactor"' not in cmd_cvar_body
	assert '"g_forcerespawn"' not in cmd_cvar_body
	assert "g_maxGameClients.integer" not in cmd_team_body
	assert "g_spawnProtect.integer" not in client_spawn_body
	assert "client->invulnerabilityTime = 0;" in client_spawn_body
	assert "g_flagDroppedTimeout" not in flag_config_body
	assert "g_flagConfig.dropTimeoutMs = DEFAULT_FLAG_DROPPED_TIMEOUT_MS;" in flag_config_body
	assert '"g_arenasFile"' not in g_bot
	assert 'G_LoadArenasFromFile("scripts/arenas.txt");' in g_bot
	assert 'trap_Cvar_VariableStringBuffer( cvarName, buffer, bufferSize );' in g_main
	assert 'cvarName = SERVERINFO_KEY_RED_TEAM;' in g_main
	assert 'cvarName = SERVERINFO_KEY_BLUE_TEAM;' in g_main


def test_inactivity_cvars_drive_retail_warning_reset_and_fallback_paths() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_local = G_LOCAL_PATH.read_text(encoding="utf-8")
	hlil_part01 = QAGAME_HLIL_PART01_PATH.read_text(encoding="utf-8")
	timer_body = _function_body(g_active, "qboolean ClientInactivityTimer( gclient_t *client )")
	reset_body = _function_body(g_main, "static void G_ResetClientInactivityWarnings( void )")
	update_body = _function_body(g_main, "void G_UpdateCvars( void )")

	assert "vmCvar_t\tg_inactivityWarning;" in g_main
	assert "extern\tvmCvar_t\tg_inactivityWarning;" in g_local
	assert "warningSeconds = g_inactivityWarning.integer;" in timer_body
	assert "level.time > client->inactivityTime - warningSeconds * 1000" in timer_body
	assert 'va( "cp \\"%i second%s until dropped for inactivity!' in timer_body
	assert '\\n\\"' in timer_body
	assert '( warningSeconds == 1 ) ? "" : "s"' in timer_body
	assert "if ( !g_dropInactive.integer ) {" in timer_body
	assert 'SetTeam( &g_entities[clientNum], "spectator" );' in timer_body
	assert 'trap_DropClient( clientNum, "Dropped due to inactivity" );' in timer_body
	assert timer_body.index("if ( !g_dropInactive.integer ) {") < timer_body.index("trap_DropClient")
	assert timer_body.index("warningSeconds = g_inactivityWarning.integer;") < timer_body.index("trap_SendServerCommand")

	assert "level.clients[i].pers.connected == CON_CONNECTED" in reset_body
	assert "level.clients[i].inactivityWarning = qfalse;" in reset_body
	assert "s_inactivityModCount = g_inactivity.modificationCount;" in g_main
	assert "if ( g_inactivity.modificationCount != s_inactivityModCount ) {" in update_body
	assert "G_ResetClientInactivityWarnings();" in update_body

	assert "if (data_105a190c == 0)" in hlil_part01
	assert 'sub_100406d0(eax_3, edx_2, "spectator", arg2)' in hlil_part01
	assert 'data_1059ae2c' in hlil_part01
	assert "second%s until dropped fo" in hlil_part01


def test_g_runframe_client_slots_dispatch_clientthink_real_inline_like_retail() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_local = G_LOCAL_PATH.read_text(encoding="utf-8")
	qagame_mapping = QAGAME_MAPPING_PATH.read_text(encoding="utf-8")
	step_body = _function_body(g_main, "static void G_StepEntities( qlr_game_frame_context_t *ctx )")
	client_block = _block_from_marker(step_body, "if ( i < MAX_CLIENTS ) {")

	assert "void ClientThink_real( gentity_t *ent );" in g_local
	assert "G_RunClient( ent );" not in client_block
	assert "G_RunThink( ent );" in client_block
	assert "if ( ent->inuse && ent->client ) {" in client_block
	assert "if ( ent->r.svFlags & SVF_BOT ) {" in client_block
	assert "ent->client->pers.cmd.serverTime = level.time;" in client_block
	assert "ClientThink_real( ent );" in client_block
	assert client_block.index("G_RunThink( ent );") < client_block.index("ClientThink_real( ent );")
	assert client_block.index("ClientThink_real( ent );") < client_block.index("ctx->hooks.physics_step")
	assert client_block.index("ctx->hooks.physics_step") < client_block.index("ctx->hooks.client_think")
	assert "G_RunFrame` at `0x100594D0` does not appear to call a standalone `G_RunClient` helper" in qagame_mapping
	assert "dispatches `ClientThink_real` directly" in qagame_mapping


def test_clientthink_real_builds_retail_pmove_and_playerstate_pipeline() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	body = _function_body(g_active, "void ClientThink_real( gentity_t *ent )")

	for snippet in (
		"client->ps.forwardmove = ucmd->forwardmove;",
		"client->ps.rightmove = ucmd->rightmove;",
		"client->ps.upmove = ucmd->upmove;",
		"if ( ucmd->serverTime > level.time + 200 ) {",
		"if ( ucmd->serverTime < level.time - 1000 ) {",
		"msec = ucmd->serverTime - client->ps.commandTime;",
		"if ( msec > 200 ) {",
		"if ( pmove_msec.integer < 8 ) {",
		"else if (pmove_msec.integer > 33) {",
		"ucmd->serverTime = ((ucmd->serverTime + pmove_msec.integer-1) / pmove_msec.integer) * pmove_msec.integer;",
	):
		assert snippet in body

	scoreboard_block = _block_from_marker(body, "if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ) {")
	assert "client->ps.pm_flags |= PMF_NO_MOVE;" in scoreboard_block
	assert "SpectatorThink( ent, ucmd );" in scoreboard_block
	assert "client->ps.pm_flags &= ~PMF_NO_MOVE;" in scoreboard_block
	assert scoreboard_block.index("client->ps.pm_flags |= PMF_NO_MOVE;") < scoreboard_block.index("SpectatorThink( ent, ucmd );")
	assert scoreboard_block.index("SpectatorThink( ent, ucmd );") < scoreboard_block.index("client->ps.pm_flags &= ~PMF_NO_MOVE;")

	assert body.index("ClientInactivityTimer( client )") < body.index("G_CheckClientFlood( ent )")
	assert body.index("G_CheckClientFlood( ent )") < body.index("if ( client->noclip ) {")
	assert body.index("if ( client->noclip ) {") < body.index("client->ps.gravity = g_gravity.value;")
	assert body.index("client->ps.gravity = g_gravity.value;") < body.index("oldEventSequence = client->ps.eventSequence;")
	assert body.index("oldEventSequence = client->ps.eventSequence;") < body.index("memset (&pm, 0, sizeof(pm));")

	for snippet in (
		"pm.ps = &client->ps;",
		"pm.cmd = *ucmd;",
		"pm.tracemask = MASK_PLAYERSOLID & ~CONTENTS_BODY;",
		"pm.tracemask = MASK_PLAYERSOLID | CONTENTS_BOTCLIP;",
		"pm.tracemask = MASK_PLAYERSOLID;",
		"pm.tracemask &= ~CONTENTS_BODY;",
		"pm.pmoveSettings = &g_pmoveSettings;",
		"pm.trace = trap_Trace;",
		"pm.pointcontents = trap_PointContents;",
		"pm.debugLevel = g_debugMove.integer;",
		"pm.noFootsteps = ( g_dmflags.integer & DF_NO_FOOTSTEPS ) > 0;",
		"pm.pmove_fixed = pmove_fixed.integer | client->pers.pmoveFixed;",
		"pm.pmove_msec = pmove_msec.integer;",
	):
		assert snippet in body

	assert body.index("Pmove (&pm);") < body.index("BG_PlayerStateToEntityState( &ent->client->ps, &ent->s, qtrue );")
	assert body.index("BG_PlayerStateToEntityState( &ent->client->ps, &ent->s, qtrue );") < body.index("SendPendingPredictableEvents( &ent->client->ps );")
	assert body.index("SendPendingPredictableEvents( &ent->client->ps );") < body.index("ClientEvents( ent, oldEventSequence );")
	assert body.index("ClientEvents( ent, oldEventSequence );") < body.index("trap_LinkEntity (ent);")
	assert body.index("trap_LinkEntity (ent);") < body.index("G_TouchTriggers( ent );")
	assert body.index("G_TouchTriggers( ent );") < body.index("ClientImpacts( ent, &pm );")
	assert body.index("ClientImpacts( ent, &pm );") < body.index("ClientTimerActions( ent, msec );")


def test_spectator_impacts_and_predictable_event_sidecars_match_retail_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	spectator_body = _function_body(g_active, "void SpectatorThink( gentity_t *ent, usercmd_t *ucmd )")
	impacts_body = _function_body(g_active, "void ClientImpacts( gentity_t *ent, pmove_t *pm )")
	triggers_body = _function_body(g_active, "void\tG_TouchTriggers( gentity_t *ent )")
	predictable_body = _function_body(g_active, "void SendPendingPredictableEvents( playerState_t *ps )")

	for snippet in (
		"client->ps.pm_type = PM_SPECTATOR;",
		"client->ps.speed = 480;",
		"if ( ent->r.linked ) {",
		"trap_UnlinkEntity( ent );",
		"pm.ps = &client->ps;",
		"pm.cmd = *ucmd;",
		"pm.tracemask = MASK_PLAYERSOLID & ~CONTENTS_BODY;",
		"pm.pmoveSettings = &g_pmoveSettings;",
		"pm.trace = trap_Trace;",
		"pm.pointcontents = trap_PointContents;",
		"Pmove (&pm);",
		"VectorCopy( client->ps.origin, ent->s.origin );",
		"G_TouchTriggers( ent );",
		"FollowCycle( ent, 1 );",
		"return;",
		"( client->buttons & BUTTON_ANY ) && ! ( client->oldbuttons & BUTTON_ANY )",
		"StopFollowing( ent );",
	):
		assert snippet in spectator_body

	assert spectator_body.index("if ( ent->r.linked ) {") < spectator_body.index("client->ps.pm_type = PM_SPECTATOR;")
	assert spectator_body.index("trap_UnlinkEntity( ent );") < spectator_body.index("Pmove (&pm);")
	assert spectator_body.index("Pmove (&pm);") < spectator_body.index("G_TouchTriggers( ent );")
	assert "( client->buttons & BUTTON_ATTACK ) && ! ( client->oldbuttons & BUTTON_ATTACK )" in spectator_body
	assert spectator_body.index("FollowCycle( ent, 1 );") < spectator_body.index("( client->buttons & BUTTON_ANY ) && ! ( client->oldbuttons & BUTTON_ANY )")
	assert "Cmd_FollowCycle_f( ent, 1 );" not in spectator_body
	assert "( level.trainingMapActive && client->sess.spectatorState == SPECTATOR_FOLLOW )" in spectator_body

	assert "memset( &trace, 0, sizeof( trace ) );" in impacts_body
	assert "for (j=0 ; j<i ; j++) {" in impacts_body
	assert "if (pm->touchents[j] == pm->touchents[i] ) {" in impacts_body
	assert "( ent->r.svFlags & SVF_BOT ) && ( ent->touch )" in impacts_body
	assert "ent->touch( ent, other, &trace );" in impacts_body
	assert "if ( !other->touch ) {" in impacts_body
	assert "other->touch( other, ent, &trace );" in impacts_body
	assert impacts_body.index("if (j != i)") < impacts_body.index("( ent->r.svFlags & SVF_BOT ) && ( ent->touch )")
	assert impacts_body.index("( ent->r.svFlags & SVF_BOT ) && ( ent->touch )") < impacts_body.index("if ( !other->touch )")

	assert "static vec3_t\trange = { 40, 40, 52 };" in triggers_body
	assert "if ( ent->client->ps.stats[STAT_HEALTH] <= 0 ) {" in triggers_body
	assert "if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {" in triggers_body
	assert "hit->touch (hit, ent, &trace);" in triggers_body
	assert "ent->client->ps.jumppad_frame != ent->client->ps.pmove_framecount" in triggers_body
	assert "ent->client->ps.jumppad_ent = 0;" in triggers_body

	assert predictable_body.index("extEvent = ps->externalEvent;") < predictable_body.index("ps->externalEvent = 0;")
	assert predictable_body.index("ps->externalEvent = 0;") < predictable_body.index("BG_PlayerStateToEntityState( ps, &t->s, qtrue );")
	assert "t->s.eType = ET_EVENTS + event;" in predictable_body
	assert "t->s.eFlags |= EF_PLAYER_EVENT;" in predictable_body
	assert "t->s.otherEntityNum = ps->clientNum;" in predictable_body
	assert "t->r.svFlags |= SVF_NOTSINGLECLIENT;" in predictable_body
	assert "t->r.singleClient = ps->clientNum;" in predictable_body
	assert predictable_body.index("t->r.singleClient = ps->clientNum;") < predictable_body.index("ps->externalEvent = extEvent;")


def test_game_active_pmove_wiring_is_backed_by_committed_retail_evidence() -> None:
	qagame_mapping = QAGAME_MAPPING_PATH.read_text(encoding="utf-8")

	assert "Unique touch-entity walker" in _symbol_comment("ClientImpacts")
	assert "dispatches bot self-touch callbacks and touched-entity handlers after pmove" in _symbol_comment("ClientImpacts")
	assert "Spectator pmove path that sets PM_SPECTATOR" in _symbol_comment("SpectatorThink")
	assert "unlinks before pmove" in _symbol_comment("SpectatorThink")
	assert "BUTTON_ANY edge" in _symbol_comment("SpectatorThink")
	assert "turns pending playerstate events into temporary ET_EVENTS entities" in _symbol_comment("SendPendingPredictableEvents")
	assert "Main per-command client simulation path covering command-time clamping" in _symbol_comment("ClientThink_real")
	assert "pmove, events, linking, impacts, respawn checks, and once-per-second timers" in _symbol_comment("ClientThink_real")
	assert "`ClientThink_real` is a clean retail boundary at `0x10034C90`" in qagame_mapping
	assert "`G_RunFrame` at `0x100594D0` does not appear to call a standalone `G_RunClient` helper" in qagame_mapping
