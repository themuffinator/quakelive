from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_CGAME_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_UI_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"
AI_CHAT_PATH = REPO_ROOT / "src" / "code" / "game" / "ai_chat.c"
AI_DMQ3_PATH = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
AI_TEAM_PATH = REPO_ROOT / "src" / "code" / "game" / "ai_team.c"
CG_DRAW_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_EVENT_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_INFO_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_info.c"
CG_NEWDRAW_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_PLAYERS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_SERVERCMDS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
G_BOT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_bot.c"
BG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
G_CLIENT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
G_CMDS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"
G_MAIN_PATH = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
G_UTILS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_utils.c"
NET_CHAN_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "net_chan.c"
QCOMMON_H_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "qcommon.h"
COMMON_C_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
MATCH_STATE_KEYS_PATH = REPO_ROOT / "src" / "game" / "match_state_keys.h"
QL_UI_IMPORTS_PATH = REPO_ROOT / "src" / "code" / "client" / "ql_ui_imports.inc"
SV_CCMDS_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_ccmds.c"
NETCODE_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "engine-netcode-parity-audit-2026-04-16.md"
)


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _snippet_after(text: str, marker: str, line_count: int) -> str:
	lines = text.splitlines()

	for index, line in enumerate(lines):
		if marker in line:
			return "\n".join(lines[index : index + line_count])

	raise AssertionError(f"marker not found: {marker}")


def test_cl_setserverinfo_matches_recovered_retail_field_set() -> None:
	cl_main = _read_text(CL_MAIN_PATH)
	snippet = _snippet_after(
		cl_main,
		"static void CL_SetServerInfo(serverInfo_t *server, const char *info, int ping) {",
		16,
	)

	for expected in (
		"server->clients = atoi(Info_ValueForKey(info, NET_GetClientsInfoKey()));",
		"Q_strncpyz(server->hostName,Info_ValueForKey(info, NET_GetHostnameInfoKey()), MAX_NAME_LENGTH);",
		"Q_strncpyz(server->mapName, Info_ValueForKey(info, NET_GetMapnameInfoKey()), MAX_NAME_LENGTH);",
		"server->maxClients = atoi(Info_ValueForKey(info, NET_GetMaxClientsInfoKey()));",
		"Q_strncpyz(server->game,Info_ValueForKey(info, NET_GetGameInfoKey()), MAX_NAME_LENGTH);",
		"server->gameType = atoi(Info_ValueForKey(info, NET_GetGametypeInfoKey()));",
		"server->netType = atoi(Info_ValueForKey(info, NET_GetNetTypeInfoKey()));",
		"server->ping = ping;",
	):
		assert expected in snippet

	for forbidden in (
		'server->minPing = atoi(Info_ValueForKey(info, "minping"));',
		'server->maxPing = atoi(Info_ValueForKey(info, "maxping"));',
		'server->punkbuster = atoi(Info_ValueForKey(info, "punkbuster"));',
	):
		assert forbidden not in snippet


def test_lan_getserverinfo_exports_profile_owned_ui_keys() -> None:
	cl_ui = _read_text(CL_UI_PATH)
	snippet = _snippet_after(
		cl_ui,
		"static void LAN_GetServerInfo( int source, int n, char *buf, int buflen ) {",
		48,
	)

	for expected in (
		"Info_SetValueForKey( info, NET_GetHostnameInfoKey(), server->hostName);",
		"Info_SetValueForKey( info, NET_GetMapnameInfoKey(), server->mapName);",
		'Info_SetValueForKey( info, NET_GetClientsInfoKey(), va("%i",server->clients));',
		'Info_SetValueForKey( info, NET_GetMaxClientsInfoKey(), va("%i",server->maxClients));',
		'Info_SetValueForKey( info, NET_GetPingInfoKey(), va("%i",server->ping));',
		'Info_SetValueForKey( info, NET_GetLegacyMinPingInfoKey(), va("%i",server->minPing));',
		'Info_SetValueForKey( info, NET_GetLegacyMaxPingInfoKey(), va("%i",server->maxPing));',
		"Info_SetValueForKey( info, NET_GetGameInfoKey(), server->game);",
		'Info_SetValueForKey( info, NET_GetGametypeInfoKey(), va("%i",server->gameType));',
		'Info_SetValueForKey( info, NET_GetNetTypeInfoKey(), va("%i",server->netType));',
		"Info_SetValueForKey( info, NET_GetAddressInfoKey(), NET_AdrToString(server->adr));",
		'Info_SetValueForKey( info, NET_GetPunkbusterInfoKey(), va("%i", server->punkbuster));',
	):
		assert expected in snippet

	for forbidden in (
		'Info_SetValueForKey( info, "hostname", server->hostName);',
		'Info_SetValueForKey( info, "mapname", server->mapName);',
		'Info_SetValueForKey( info, "clients", va("%i",server->clients));',
		'Info_SetValueForKey( info, "sv_maxclients", va("%i",server->maxClients));',
		'Info_SetValueForKey( info, "ping", va("%i",server->ping));',
		'Info_SetValueForKey( info, "minping", va("%i",server->minPing));',
		'Info_SetValueForKey( info, "maxping", va("%i",server->maxPing));',
		'Info_SetValueForKey( info, "game", server->game);',
		'Info_SetValueForKey( info, "gametype", va("%i",server->gameType));',
		'Info_SetValueForKey( info, "nettype", va("%i",server->netType));',
		'Info_SetValueForKey( info, "addr", NET_AdrToString(server->adr));',
		'Info_SetValueForKey( info, "punkbuster", va("%i", server->punkbuster));',
	):
		assert forbidden not in snippet


def test_cl_serverinfopacket_nettype_matches_recovered_retail_contract() -> None:
	cl_main = _read_text(CL_MAIN_PATH)
	snippet = _snippet_after(
		cl_main,
		"void CL_ServerInfoPacket( netadr_t from, msg_t *msg ) {",
		64,
	)

	assert 'if ( from.type == NA_BROADCAST || from.type == NA_IP ) {' in snippet
	assert "type = 1;" in snippet
	assert "type = 0;" in snippet
	assert 'Info_SetValueForKey( cl_pinglist[i].info, NET_GetNetTypeInfoKey(), va("%d", type) );' in snippet

	for forbidden in (
		"char*\tstr;",
		"case NA_IPX:",
		"case NA_BROADCAST_IPX:",
		'str = "udp";',
		'str = "ipx";',
		'type = 2;',
	):
		assert forbidden not in snippet


def test_warmup_ready_configstring_uses_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	sv_main = _read_text(REPO_ROOT / "src" / "code" / "server" / "sv_main.c")
	g_main = _read_text(G_MAIN_PATH)
	cg_servercmds = _read_text(CG_SERVERCMDS_PATH)

	assert '#define MATCH_STATE_KEY_WARMUP_READY_PERCENT "pct"' in keys_h
	assert '#define MATCH_STATE_KEY_WARMUP_READY_COUNT "ready"' in keys_h
	assert '#define MATCH_STATE_KEY_WARMUP_READY_ELIGIBLE "eligible"' in keys_h
	assert '#include "../../game/match_state_keys.h"' in sv_main
	assert '#include "../game/match_state_keys.h"' in g_main

	sv_snippet = _snippet_after(
		sv_main,
		"qboolean SV_CheckWarmupReadiness( qboolean announce ) {",
		44,
	)
	game_snippet = _snippet_after(
		g_main,
		"static void G_PublishWarmupReadyConfigstring( int readyCount, int eligibleCount, int readyMask ) {",
		36,
	)
	cgame_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_ParseWarmupReadyStatus( void ) {",
		40,
	)

	for expected in (
		'Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_PERCENT, va( "%i", sv_warmupReadyPercentage->integer ) );',
		'Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_COUNT, va( "%i", ready ) );',
		'Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_ELIGIBLE, va( "%i", eligible ) );',
	):
		assert expected in sv_snippet

	for expected in (
		"Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_PERCENT, value );",
		"Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_COUNT, value );",
		"Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_ELIGIBLE, value );",
	):
		assert expected in game_snippet

	for expected in (
		"Info_ValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_PERCENT )",
		"Info_ValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_COUNT )",
		"Info_ValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_ELIGIBLE )",
	):
		assert expected in cgame_snippet

	for forbidden in (
		'Info_SetValueForKey( info, "pct"',
		'Info_SetValueForKey( info, "ready"',
		'Info_SetValueForKey( info, "eligible"',
		'Info_ValueForKey( info, "pct" )',
		'Info_ValueForKey( info, "ready" )',
		'Info_ValueForKey( info, "eligible" )',
	):
		assert forbidden not in sv_snippet
		assert forbidden not in game_snippet
		assert forbidden not in cgame_snippet


def test_forced_cosmetics_configstring_uses_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	g_main = _read_text(G_MAIN_PATH)
	cg_servercmds = _read_text(CG_SERVERCMDS_PATH)

	assert '#define FORCED_COSMETICS_KEY_SMALL_SCOREBOARD "sb"' in keys_h
	assert '#define FORCED_COSMETICS_KEY_HUD "hud"' in keys_h
	assert '#define FORCED_COSMETICS_KEY_DAMAGE "dmg"' in keys_h
	assert '#define FORCED_COSMETICS_KEY_ATMOSPHERE "atm"' in keys_h
	assert '#include "../game/match_state_keys.h"' in g_main
	assert '#include "../../game/match_state_keys.h"' in cg_servercmds

	game_snippet = _snippet_after(
		g_main,
		"void G_UpdateForcedCosmeticsConfigstring( qboolean forceBroadcast ) {",
		36,
	)
	cgame_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_ParseForcedCosmetics( void ) {",
		48,
	)

	for expected in (
		"Info_SetValueForKey( info, FORCED_COSMETICS_KEY_SMALL_SCOREBOARD, g_forceSmallScoreboardMessage.integer ? \"1\" : \"0\" );",
		"Info_SetValueForKey( info, FORCED_COSMETICS_KEY_HUD, g_forceSendConfigstring.integer ? \"1\" : \"0\" );",
		"Info_SetValueForKey( info, FORCED_COSMETICS_KEY_DAMAGE, g_forceDmgThroughSurface.integer ? \"1\" : \"0\" );",
		"Info_SetValueForKey( info, FORCED_COSMETICS_KEY_ATMOSPHERE, atmosphere );",
	):
		assert expected in game_snippet

	for expected in (
		"Info_ValueForKey( info, FORCED_COSMETICS_KEY_SMALL_SCOREBOARD )",
		"Info_ValueForKey( info, FORCED_COSMETICS_KEY_HUD )",
		"Info_ValueForKey( info, FORCED_COSMETICS_KEY_DAMAGE )",
		"Info_ValueForKey( info, FORCED_COSMETICS_KEY_ATMOSPHERE )",
	):
		assert expected in cgame_snippet

	for forbidden in (
		'Info_SetValueForKey( info, "sb"',
		'Info_SetValueForKey( info, "hud"',
		'Info_SetValueForKey( info, "dmg"',
		'Info_SetValueForKey( info, "atm"',
		'Info_ValueForKey( info, "sb" )',
		'Info_ValueForKey( info, "hud" )',
		'Info_ValueForKey( info, "dmg" )',
		'Info_ValueForKey( info, "atm" )',
	):
		assert forbidden not in game_snippet
		assert forbidden not in cgame_snippet


def test_server_settings_configstring_uses_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	g_main = _read_text(G_MAIN_PATH)
	cg_servercmds = _read_text(CG_SERVERCMDS_PATH)

	assert '#define SERVER_SETTINGS_KEY_ARMOR_TIERED "armor_tiered"' in keys_h
	assert '#define SERVER_SETTINGS_KEY_QUAD_DAMAGE_FACTOR "g_quadDamageFactor"' in keys_h
	assert '#define SERVER_SETTINGS_KEY_GRAVITY "g_gravity"' in keys_h
	assert '#include "../game/match_state_keys.h"' in g_main
	assert '#include "../../game/match_state_keys.h"' in cg_servercmds

	game_snippet = _snippet_after(
		g_main,
		"static void G_UpdateServerSettingsInfoConfigstrings( qboolean forceBroadcast ) {",
		24,
	)
	armor_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_ParseArmorTieredConfigString( void ) {",
		20,
	)
	settings_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_ParseServerSettingsInfoConfigStrings( void ) {",
		18,
	)

	for expected in (
		'Info_SetValueForKey( payloadA, SERVER_SETTINGS_KEY_ARMOR_TIERED, va( "%i", g_armorTiered.integer ) );',
		'Info_SetValueForKey( payloadB, SERVER_SETTINGS_KEY_QUAD_DAMAGE_FACTOR, va( "%i", g_quadDamageFactor.integer ) );',
		'Info_SetValueForKey( payloadB, SERVER_SETTINGS_KEY_GRAVITY, va( "%i", g_gravity.integer ) );',
	):
		assert expected in game_snippet

	assert "Info_ValueForKey( info, SERVER_SETTINGS_KEY_ARMOR_TIERED )" in armor_snippet
	assert "Info_ValueForKey( info, SERVER_SETTINGS_KEY_QUAD_DAMAGE_FACTOR )" in settings_snippet
	assert "Info_ValueForKey( info, SERVER_SETTINGS_KEY_GRAVITY )" in settings_snippet

	for forbidden in (
		'Info_SetValueForKey( payloadA, "armor_tiered"',
		'Info_SetValueForKey( payloadB, "g_quadDamageFactor"',
		'Info_SetValueForKey( payloadB, "g_gravity"',
		'Info_ValueForKey( info, "armor_tiered" )',
		'Info_ValueForKey( info, "g_quadDamageFactor" )',
		'Info_ValueForKey( info, "g_gravity" )',
	):
		assert forbidden not in game_snippet
		assert forbidden not in armor_snippet
		assert forbidden not in settings_snippet


def test_player_appearance_configstring_uses_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	g_main = _read_text(G_MAIN_PATH)
	cg_servercmds = _read_text(CG_SERVERCMDS_PATH)

	for expected in (
		'#define PLAYER_APPEARANCE_KEY_PLAYERMODEL_OVERRIDE "g_playermodelOverride"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERHEADMODEL_OVERRIDE "g_playerheadmodelOverride"',
		'#define PLAYER_APPEARANCE_KEY_ALLOW_CUSTOM_HEADMODELS "g_allowCustomHeadmodels"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE "g_playerheadScale"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE_OFFSET "g_playerheadScaleOffset"',
		'#define PLAYER_APPEARANCE_KEY_PLAYERMODEL_SCALE "g_playerModelScale"',
	):
		assert expected in keys_h

	assert '#include "../game/match_state_keys.h"' in g_main
	assert '#include "../../game/match_state_keys.h"' in cg_servercmds

	game_snippet = _snippet_after(
		g_main,
		"static void G_UpdatePlayerAppearanceConfigstring( qboolean forceBroadcast ) {",
		26,
	)
	cgame_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_ParsePlayerAppearanceConfigString( void ) {",
		68,
	)

	for expected in (
		"Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_OVERRIDE, g_playermodelOverride.string );",
		"Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEADMODEL_OVERRIDE, g_playerheadmodelOverride.string );",
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_ALLOW_CUSTOM_HEADMODELS, va( "%i", g_allowCustomHeadmodels.integer ) );',
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE, va( "%g", g_playerheadScale.value ) );',
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE_OFFSET, va( "%g", g_playerheadScaleOffset.value ) );',
		'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_SCALE, va( "%g", g_playerModelScale.value ) );',
	):
		assert expected in game_snippet

	for expected in (
		"Info_ValueForKey( info, PLAYER_APPEARANCE_KEY_PLAYERMODEL_OVERRIDE )",
		"Info_ValueForKey( info, PLAYER_APPEARANCE_KEY_PLAYERHEADMODEL_OVERRIDE )",
		"Info_ValueForKey( info, PLAYER_APPEARANCE_KEY_ALLOW_CUSTOM_HEADMODELS )",
		"Info_ValueForKey( info, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE )",
		"Info_ValueForKey( info, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE_OFFSET )",
		"Info_ValueForKey( info, PLAYER_APPEARANCE_KEY_PLAYERMODEL_SCALE )",
	):
		assert expected in cgame_snippet

	for forbidden in (
		'Info_SetValueForKey( payload, "g_playermodelOverride"',
		'Info_SetValueForKey( payload, "g_playerheadmodelOverride"',
		'Info_SetValueForKey( payload, "g_allowCustomHeadmodels"',
		'Info_SetValueForKey( payload, "g_playerheadScale"',
		'Info_SetValueForKey( payload, "g_playerheadScaleOffset"',
		'Info_SetValueForKey( payload, "g_playerModelScale"',
		'Info_ValueForKey( info, "g_playermodelOverride" )',
		'Info_ValueForKey( info, "g_playerheadmodelOverride" )',
		'Info_ValueForKey( info, "g_allowCustomHeadmodels" )',
		'Info_ValueForKey( info, "g_playerheadScale" )',
		'Info_ValueForKey( info, "g_playerheadScaleOffset" )',
		'Info_ValueForKey( info, "g_playerModelScale" )',
	):
		assert forbidden not in game_snippet
		assert forbidden not in cgame_snippet


def test_rotation_vote_configstrings_use_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	sv_ccmds = _read_text(SV_CCMDS_PATH)
	g_main = _read_text(G_MAIN_PATH)
	g_cmds = _read_text(G_CMDS_PATH)
	cg_servercmds = _read_text(CG_SERVERCMDS_PATH)

	for expected in (
		"#define ROTATION_VOTE_SLOT_COUNT 3",
		"#define ROTATION_VOTE_KEY_BUFFER_SIZE 16",
		'#define ROTATION_VOTE_KEY_MAP_FORMAT "map_%i"',
		'#define ROTATION_VOTE_KEY_TITLE_FORMAT "title_%i"',
		'#define ROTATION_VOTE_KEY_CONFIG_FORMAT "cfg_%i"',
		'#define ROTATION_VOTE_KEY_GAMETYPE_FORMAT "gt_%i"',
		'#define ROTATION_VOTE_KEY_COUNT_FORMAT "%i"',
	):
		assert expected in keys_h

	assert '#include "../../game/match_state_keys.h"' in sv_ccmds
	assert '#include "../../game/match_state_keys.h"' in g_cmds
	assert '#include "../game/match_state_keys.h"' in g_main
	assert '#include "../../game/match_state_keys.h"' in cg_servercmds

	sv_build_snippet = _snippet_after(
		sv_ccmds,
		"static void SV_MapPoolBuildNextMapsCvar( void ) {",
		66,
	)
	g_counts_snippet = _snippet_after(
		g_main,
		"static void G_PublishNextMapVoteCounts( void ) {",
		24,
	)
	g_publish_snippet = _snippet_after(
		g_main,
		"static void G_PublishRotationPreviewConfigstrings( void ) {",
		52,
	)
	g_select_snippet = _snippet_after(
		g_main,
		"static int G_SelectNextMapVoteSlot( void ) {",
		42,
	)
	g_exit_snippet = _snippet_after(
		g_main,
		"void ExitLevel (void) {",
		70,
	)
	g_tallies_snippet = _snippet_after(
		g_cmds,
		"void G_UpdateNextMapVoteTallies( void ) {",
		48,
	)
	g_vote_snippet = _snippet_after(
		g_cmds,
		"qboolean G_HandleNextMapVote( gentity_t *ent ) {",
		72,
	)
	cgame_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_ParseRotationVoteConfigStrings( void ) {",
		62,
	)

	for expected in (
		"Info_SetValueForKey( nextmaps, va( ROTATION_VOTE_KEY_MAP_FORMAT, slot ), entry->mapName );",
		"Info_SetValueForKey( nextmaps, va( ROTATION_VOTE_KEY_TITLE_FORMAT, slot ), entry->mapTitle );",
		"Info_SetValueForKey( nextmaps, va( ROTATION_VOTE_KEY_CONFIG_FORMAT, slot ), entry->factoryId );",
		"Info_SetValueForKey( nextmaps, va( ROTATION_VOTE_KEY_GAMETYPE_FORMAT, slot ), entry->factoryTitle );",
		"while ( slot < ROTATION_VOTE_SLOT_COUNT ) {",
	):
		assert expected in sv_build_snippet

	for expected in (
		"for ( slot = 0; slot < ROTATION_VOTE_SLOT_COUNT; slot++ ) {",
		"char\tkey[ROTATION_VOTE_KEY_BUFFER_SIZE];",
		"Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_COUNT_FORMAT, slot );",
		"Info_SetValueForKey( counts, key, value );",
	):
		assert expected in g_counts_snippet

	for expected in (
		"Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_MAP_FORMAT, slot );",
		"Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_TITLE_FORMAT, slot );",
		"Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_GAMETYPE_FORMAT, slot );",
		"Info_SetValueForKey( titles, key, value );",
	):
		assert expected in g_publish_snippet

	for expected in (
		"int\t\ttiedSlots[ROTATION_VOTE_SLOT_COUNT];",
		"for ( slot = 0; slot < ROTATION_VOTE_SLOT_COUNT; slot++ ) {",
		"Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_MAP_FORMAT, slot );",
	):
		assert expected in g_select_snippet

	assert "Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_MAP_FORMAT, selectedSlot );" in g_exit_snippet
	assert "Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_CONFIG_FORMAT, selectedSlot );" in g_exit_snippet

	for expected in (
		"for ( slot = 0; slot < ROTATION_VOTE_SLOT_COUNT; slot++ ) {",
		"if ( selection < 1 || selection > ROTATION_VOTE_SLOT_COUNT ) {",
		"Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_COUNT_FORMAT, slot );",
	):
		assert expected in g_tallies_snippet

	assert "if ( voteSelection < 1 || voteSelection > ROTATION_VOTE_SLOT_COUNT ) {" in g_vote_snippet
	assert "Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_MAP_FORMAT, voteSelection - 1 );" in g_vote_snippet
	assert "Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_TITLE_FORMAT, voteSelection - 1 );" in g_vote_snippet

	for expected in (
		"for ( slot = 0; slot < ROTATION_VOTE_SLOT_COUNT; slot++ ) {",
		"char\tinfoKey[ROTATION_VOTE_KEY_BUFFER_SIZE];",
		"Com_sprintf( infoKey, sizeof( infoKey ), ROTATION_VOTE_KEY_MAP_FORMAT, slot );",
		"Com_sprintf( infoKey, sizeof( infoKey ), ROTATION_VOTE_KEY_TITLE_FORMAT, slot );",
		"Com_sprintf( infoKey, sizeof( infoKey ), ROTATION_VOTE_KEY_GAMETYPE_FORMAT, slot );",
		"Com_sprintf( infoKey, sizeof( infoKey ), ROTATION_VOTE_KEY_COUNT_FORMAT, slot );",
	):
		assert expected in cgame_snippet

	for forbidden in (
		'va( "map_%i", slot )',
		'va( "title_%i", slot )',
		'va( "cfg_%i", slot )',
		'va( "gt_%i", slot )',
		'Com_sprintf( key, sizeof( key ), "map_%i"',
		'Com_sprintf( key, sizeof( key ), "title_%i"',
		'Com_sprintf( key, sizeof( key ), "cfg_%i"',
		'Com_sprintf( key, sizeof( key ), "gt_%i"',
		'Com_sprintf( infoKey, sizeof( infoKey ), "map_%i"',
		'Com_sprintf( infoKey, sizeof( infoKey ), "title_%i"',
		'Com_sprintf( infoKey, sizeof( infoKey ), "gt_%i"',
		"slot < 3",
		"selection > 3",
		"voteSelection > 3",
		"slot >= 3",
		"char\tkey[16]",
		"char\tinfoKey[16]",
	):
		for snippet in (
			sv_build_snippet,
			g_counts_snippet,
			g_publish_snippet,
			g_select_snippet,
			g_exit_snippet,
			g_tallies_snippet,
			g_vote_snippet,
			cgame_snippet,
		):
			assert forbidden not in snippet


def test_player_info_configstring_uses_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	g_client = _read_text(G_CLIENT_PATH)
	cg_players = _read_text(CG_PLAYERS_PATH)
	cg_draw = _read_text(CG_DRAW_PATH)
	cg_event = _read_text(CG_EVENT_PATH)
	cg_info = _read_text(CG_INFO_PATH)
	g_utils = _read_text(G_UTILS_PATH)
	ai_chat = _read_text(AI_CHAT_PATH)
	ai_dmq3 = _read_text(AI_DMQ3_PATH)
	ai_team = _read_text(AI_TEAM_PATH)

	for expected in (
		'#define PLAYER_INFO_KEY_NAME "n"',
		'#define PLAYER_INFO_KEY_TEAM "t"',
		'#define PLAYER_INFO_KEY_MODEL "model"',
		'#define PLAYER_INFO_KEY_HEADMODEL "hmodel"',
		'#define PLAYER_INFO_KEY_REDTEAM "g_redteam"',
		'#define PLAYER_INFO_KEY_BLUETEAM "g_blueteam"',
		'#define PLAYER_INFO_KEY_COUNTRY "country"',
		'#define PLAYER_INFO_KEY_COLOR1 "c1"',
		'#define PLAYER_INFO_KEY_COLOR2 "c2"',
		'#define PLAYER_INFO_KEY_HANDICAP "hc"',
		'#define PLAYER_INFO_KEY_WINS "w"',
		'#define PLAYER_INFO_KEY_LOSSES "l"',
		'#define PLAYER_INFO_KEY_SKILL "skill"',
		'#define PLAYER_INFO_KEY_TEAMTASK "tt"',
		'#define PLAYER_INFO_KEY_TEAMLEADER "tl"',
		'#define PLAYER_INFO_KEY_READY "rp"',
		'#define PLAYER_INFO_KEY_PRIVILEGE "p"',
		'#define PLAYER_INFO_KEY_SPECTATE_ONLY "so"',
		'#define PLAYER_INFO_KEY_SPECTATOR_QUEUE "pq"',
	):
		assert expected in keys_h

	for source in (g_client, g_utils, ai_chat, ai_dmq3, ai_team):
		assert '#include "../game/match_state_keys.h"' in source
	for source in (cg_players, cg_draw, cg_event, cg_info):
		assert '#include "../../game/match_state_keys.h"' in source

	game_snippet = _snippet_after(
		g_client,
		"void ClientUserinfoChanged( int clientNum ) {",
		320,
	)
	cgame_snippet = _snippet_after(
		cg_players,
		"void CG_NewClientInfo( int clientNum ) {",
		130,
	)

	for expected in (
		'PLAYER_INFO_KEY_NAME "\\\\%s\\\\" PLAYER_INFO_KEY_TEAM "\\\\%i\\\\"',
		'PLAYER_INFO_KEY_MODEL "\\\\%s\\\\" PLAYER_INFO_KEY_HEADMODEL "\\\\%s\\\\"',
		'PLAYER_INFO_KEY_COUNTRY "\\\\%s\\\\" PLAYER_INFO_KEY_COLOR1 "\\\\%s\\\\"',
		'PLAYER_INFO_KEY_COLOR2 "\\\\%s\\\\" PLAYER_INFO_KEY_HANDICAP "\\\\%i\\\\"',
		'PLAYER_INFO_KEY_WINS "\\\\%i\\\\" PLAYER_INFO_KEY_LOSSES "\\\\%i\\\\"',
		'PLAYER_INFO_KEY_SKILL "\\\\%s\\\\" PLAYER_INFO_KEY_TEAMTASK "\\\\%d\\\\"',
		'PLAYER_INFO_KEY_REDTEAM "\\\\%s\\\\" PLAYER_INFO_KEY_BLUETEAM "\\\\%s\\\\"',
		"trap_SetConfigstring( CS_PLAYERS+clientNum, s );",
	):
		assert expected in game_snippet

	for expected in (
		"Info_ValueForKey(configstring, PLAYER_INFO_KEY_NAME)",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_COLOR1 )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_COLOR2 )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_SKILL )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_HANDICAP )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_WINS )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_LOSSES )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_TEAM )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_TEAMTASK )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_TEAMLEADER )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_SPECTATE_ONLY )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_SPECTATOR_QUEUE )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_REDTEAM )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_BLUETEAM )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_COUNTRY )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_MODEL )",
		"Info_ValueForKey( configstring, PLAYER_INFO_KEY_HEADMODEL )",
	):
		assert expected in cgame_snippet

	for helper_source, expectations in (
		(cg_draw, ("Info_ValueForKey(  info, PLAYER_INFO_KEY_NAME )",)),
		(cg_event, ("Info_ValueForKey( playerInfo, PLAYER_INFO_KEY_NAME )",)),
		(cg_info, ("Info_ValueForKey( info, PLAYER_INFO_KEY_MODEL )", "Info_ValueForKey( info, PLAYER_INFO_KEY_NAME )")),
		(g_utils, ("Info_ValueForKey( configstring, PLAYER_INFO_KEY_NAME )",)),
		(ai_chat, ("Info_ValueForKey(buf, PLAYER_INFO_KEY_NAME)", "Info_ValueForKey(buf, PLAYER_INFO_KEY_TEAM)")),
		(ai_dmq3, ("Info_ValueForKey(info, PLAYER_INFO_KEY_TEAM)", "Info_ValueForKey(buf, PLAYER_INFO_KEY_NAME)", "Info_ValueForKey(buf, PLAYER_INFO_KEY_MODEL)")),
		(ai_team, ("Info_ValueForKey(buf, PLAYER_INFO_KEY_NAME)", "Info_ValueForKey(buf, PLAYER_INFO_KEY_TEAM)")),
	):
		for expected in expectations:
			assert expected in helper_source

	for forbidden in (
		'"n\\\\%s\\\\t\\\\%i"',
		'"model\\\\%s\\\\hmodel\\\\%s"',
		'"country\\\\%s\\\\c1\\\\%s"',
		'"g_redteam\\\\%s\\\\g_blueteam\\\\%s"',
	):
		assert forbidden not in game_snippet

	for forbidden in (
		'Info_ValueForKey(configstring, "n")',
		'Info_ValueForKey( configstring, "c1" )',
		'Info_ValueForKey( configstring, "c2" )',
		'Info_ValueForKey( configstring, "skill" )',
		'Info_ValueForKey( configstring, "hc" )',
		'Info_ValueForKey( configstring, "w" )',
		'Info_ValueForKey( configstring, "l" )',
		'Info_ValueForKey( configstring, "t" )',
		'Info_ValueForKey( configstring, "tt" )',
		'Info_ValueForKey( configstring, "tl" )',
		'Info_ValueForKey( configstring, "so" )',
		'Info_ValueForKey( configstring, "pq" )',
		'Info_ValueForKey( configstring, "g_redteam" )',
		'Info_ValueForKey( configstring, "g_blueteam" )',
		'Info_ValueForKey( configstring, "country" )',
		'Info_ValueForKey( configstring, "model" )',
		'Info_ValueForKey( configstring, "hmodel" )',
	):
		assert forbidden not in cgame_snippet


def test_serverinfo_configstring_uses_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	cg_servercmds = _read_text(CG_SERVERCMDS_PATH)
	cg_draw = _read_text(CG_DRAW_PATH)
	cg_newdraw = _read_text(CG_NEWDRAW_PATH)
	cg_info = _read_text(CG_INFO_PATH)
	ai_chat = _read_text(AI_CHAT_PATH)
	ai_dmq3 = _read_text(AI_DMQ3_PATH)
	g_bot = _read_text(G_BOT_PATH)
	g_main = _read_text(G_MAIN_PATH)

	for expected in (
		'#define SERVERINFO_KEY_MAPNAME "mapname"',
		'#define SERVERINFO_KEY_GAMETYPE "g_gametype"',
		'#define SERVERINFO_KEY_DMFLAGS "dmflags"',
		'#define SERVERINFO_KEY_TEAMFLAGS "teamflags"',
		'#define SERVERINFO_KEY_FRAGLIMIT "fraglimit"',
		'#define SERVERINFO_KEY_CAPTURELIMIT "capturelimit"',
		'#define SERVERINFO_KEY_SCORELIMIT "scorelimit"',
		'#define SERVERINFO_KEY_TIMELIMIT "timelimit"',
		'#define SERVERINFO_KEY_ROUNDLIMIT "roundlimit"',
		'#define SERVERINFO_KEY_ROUNDTIMELIMIT "roundtimelimit"',
		'#define SERVERINFO_KEY_VOTEFLAGS "g_voteFlags"',
		'#define SERVERINFO_KEY_MAXCLIENTS "sv_maxclients"',
		'#define SERVERINFO_KEY_TEAMSIZE "teamsize"',
		'#define SERVERINFO_KEY_WEAPON_RESPAWN "g_weaponRespawn"',
		'#define SERVERINFO_KEY_LOADOUT "loadout"',
		'#define SERVERINFO_KEY_LEGACY_LOADOUT "g_loadout"',
		'#define SERVERINFO_KEY_FACTORY_TITLE "g_factoryTitle"',
		'#define SERVERINFO_KEY_RED_TEAM "g_redTeam"',
		'#define SERVERINFO_KEY_BLUE_TEAM "g_blueTeam"',
	):
		assert expected in keys_h

	for source in (cg_servercmds, cg_draw, cg_newdraw, cg_info):
		assert '#include "../../game/match_state_keys.h"' in source
	for source in (ai_chat, ai_dmq3, g_bot, g_main):
		assert '#include "../game/match_state_keys.h"' in source

	game_info_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_SetGameInfoCvars( void ) {",
		28,
	)
	factory_title_snippet = _snippet_after(
		cg_servercmds,
		"static void CG_ParseFactoryTitleServerinfo( const char *info ) {",
		34,
	)
	parse_snippet = _snippet_after(
		cg_servercmds,
		"void CG_ParseServerinfo( void ) {",
		90,
	)

	assert "trap_Cvar_Update( &g_training );" in game_info_snippet
	assert "if ( g_training.integer ) {" in game_info_snippet
	assert "value = info ? Info_ValueForKey( info, SERVERINFO_KEY_FACTORY_TITLE ) : \"\";" in factory_title_snippet

	for expected in (
		"gametypeValue = Info_ValueForKey( info, SERVERINFO_KEY_GAMETYPE );",
		"cgs.dmflags = atoi( Info_ValueForKey( info, SERVERINFO_KEY_DMFLAGS ) );",
		"cgs.teamflags = atoi( Info_ValueForKey( info, SERVERINFO_KEY_TEAMFLAGS ) );",
		"cgs.fraglimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_FRAGLIMIT ) );",
		"cgs.capturelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_CAPTURELIMIT ) );",
		"cgs.scorelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_SCORELIMIT ) );",
		"cgs.timelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_TIMELIMIT ) );",
		"cgs.roundlimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_ROUNDLIMIT ) );",
		"voteFlagsValue = Info_ValueForKey( info, SERVERINFO_KEY_VOTEFLAGS );",
		"cgs.maxclients = atoi( Info_ValueForKey( info, SERVERINFO_KEY_MAXCLIENTS ) );",
		"weaponRespawnValue = Info_ValueForKey( info, SERVERINFO_KEY_WEAPON_RESPAWN );",
		'trap_Cvar_Set( "g_weaponRespawn", weaponRespawnValue );',
		"playerCountTeamSizeValue = Info_ValueForKey( info, SERVERINFO_KEY_TEAMSIZE );",
		"serverLoadout = Info_ValueForKey( info, SERVERINFO_KEY_LOADOUT );",
		"serverLoadout = Info_ValueForKey( info, SERVERINFO_KEY_LEGACY_LOADOUT );",
		"mapname = CG_NormalizeMapFilename( Info_ValueForKey( info, SERVERINFO_KEY_MAPNAME ) );",
		'CG_SetTeamNameCvar( "g_redteam", Info_ValueForKey( info, SERVERINFO_KEY_RED_TEAM ), DEFAULT_REDTEAM_NAME, cgs.redTeam, sizeof( cgs.redTeam ) );',
		'CG_SetTeamNameCvar( "g_blueteam", Info_ValueForKey( info, SERVERINFO_KEY_BLUE_TEAM ), DEFAULT_BLUETEAM_NAME, cgs.blueTeam, sizeof( cgs.blueTeam ) );',
		"voteFlagsString = Info_ValueForKey( info, SERVERINFO_KEY_VOTEFLAGS );",
	):
		assert expected in parse_snippet

	for helper_source, expectations in (
		(cg_draw, ("Info_ValueForKey( info, SERVERINFO_KEY_SCORELIMIT )", "Info_ValueForKey( info, SERVERINFO_KEY_ROUNDLIMIT )", "trap_Cvar_Update( &g_training );")),
		(cg_newdraw, ("Info_ValueForKey( info, SERVERINFO_KEY_ROUNDTIMELIMIT )", "Info_ValueForKey( serverInfo, SERVERINFO_KEY_MAPNAME )")),
		(cg_info, ("Info_ValueForKey( info, SERVERINFO_KEY_MAPNAME )",)),
		(ai_chat, ("Info_ValueForKey( info, SERVERINFO_KEY_MAPNAME )",)),
		(ai_dmq3, ("Info_ValueForKey( info, SERVERINFO_KEY_MAPNAME )",)),
		(g_bot, ("Info_ValueForKey( serverinfo, SERVERINFO_KEY_MAPNAME )",)),
		(g_main, ("Info_ValueForKey( serverinfo, SERVERINFO_KEY_MAPNAME )",)),
	):
		for expected in expectations:
			assert expected in helper_source

	for forbidden in (
		'Info_ValueForKey( info, "g_training" )',
		'Info_ValueForKey( info, "g_factoryTitle" )',
		'Info_ValueForKey( info, "g_gametype" )',
		'Info_ValueForKey( info, "dmflags" )',
		'Info_ValueForKey( info, "teamflags" )',
		'Info_ValueForKey( info, "fraglimit" )',
		'Info_ValueForKey( info, "capturelimit" )',
		'Info_ValueForKey( info, "g_scorelimit" )',
		'Info_ValueForKey( info, "timelimit" )',
		'Info_ValueForKey( info, "roundlimit" )',
		'Info_ValueForKey( info, "g_voteFlags" )',
		'Info_ValueForKey( info, "sv_maxclients" )',
		'Info_ValueForKey( info, "g_weaponRespawn" )',
		'Info_ValueForKey( info, "teamsize" )',
		'Info_ValueForKey( info, "loadout" )',
		'Info_ValueForKey( info, "g_loadout" )',
		'Info_ValueForKey( info, "mapname" )',
		'Info_ValueForKey( info, "g_redTeam" )',
		'Info_ValueForKey( info, "g_blueTeam" )',
	):
		assert forbidden not in game_info_snippet
		assert forbidden not in factory_title_snippet
		assert forbidden not in parse_snippet

	for forbidden in (
		'Info_ValueForKey( info, "roundtimelimit" )',
		'Info_ValueForKey( serverInfo, "mapname" )',
		'Info_ValueForKey( serverinfo, "mapname" )',
	):
		for source in (cg_draw, cg_newdraw, cg_info, ai_chat, ai_dmq3, g_bot, g_main):
			assert forbidden not in source


def test_arena_metadata_uses_shared_key_contract() -> None:
	keys_h = _read_text(MATCH_STATE_KEYS_PATH)
	sv_ccmds = _read_text(SV_CCMDS_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	g_bot = _read_text(G_BOT_PATH)
	bg_public = _read_text(BG_PUBLIC_PATH)

	for expected in (
		'#define ARENA_INFO_KEY_MAP "map"',
		'#define ARENA_INFO_KEY_LONGNAME "longname"',
		'#define ARENA_INFO_KEY_TYPE "type"',
		'#define ARENA_INFO_KEY_NUM "num"',
		'#define ARENA_INFO_KEY_FRAGLIMIT "fraglimit"',
		'#define ARENA_INFO_KEY_TIMELIMIT "timelimit"',
		'#define ARENA_INFO_KEY_SPECIAL "special"',
		'#define ARENA_INFO_KEY_BOTS "bots"',
	):
		assert expected in keys_h

	assert '#include "../../game/match_state_keys.h"' in sv_ccmds
	assert '#include "../../game/match_state_keys.h"' in cl_cgame
	assert '#include "../game/match_state_keys.h"' in g_bot
	assert "#define\tMAX_ARENAS_TEXT\t\t0x4000" in bg_public
	assert "#define CL_WEB_MAX_MAPS 256" in cl_cgame

	sv_lookup_snippet = _snippet_after(
		sv_ccmds,
		"static const char *SV_GetArenaInfoByMap( const char *map ) {",
		24,
	)
	sv_type_support_snippet = _snippet_after(
		sv_ccmds,
		"static qboolean SV_ArenaTypeSupportsGametype( const char *types, gametype_t gametype ) {",
		50,
	)
	sv_gametype_snippet = _snippet_after(
		sv_ccmds,
		"static qboolean SV_MapSupportsGametype( const char *mapName, gametype_t gametype ) {",
		58,
	)
	sv_title_snippet = _snippet_after(
		sv_ccmds,
		"static void SV_GetArenaDisplayTitle( const char *mapName, char *buffer, int bufferSize ) {",
		34,
	)
	client_snippet = _snippet_after(
		cl_cgame,
		"static void CL_WebHost_ParseArenaInfosToJson( char *data, char *buffer, size_t bufferSize, char seenMaps[][MAX_QPATH], int *entryCount ) {",
		66,
	)
	game_load_snippet = _snippet_after(
		g_bot,
		"static void G_LoadArenas( void ) {",
		70,
	)
	game_lookup_snippet = _snippet_after(
		g_bot,
		"const char *G_GetArenaInfoByMap( const char *map ) {",
		20,
	)
	game_gametype_snippet = _snippet_after(
		g_bot,
		"qboolean G_MapSupportsGametype( const char *map, gametype_t gametype ) {",
		62,
	)
	game_init_snippet = _snippet_after(
		g_bot,
		"void G_InitBots( qboolean restart ) {",
		80,
	)

	for expected in (
		"Info_ValueForKey( s_svArenaInfos[index], ARENA_INFO_KEY_MAP )",
		"Info_ValueForKey( info, ARENA_INFO_KEY_TYPE )",
		"Info_ValueForKey( arenaInfo, ARENA_INFO_KEY_LONGNAME )",
	):
		assert expected in sv_lookup_snippet + sv_gametype_snippet + sv_title_snippet

	for expected in (
		'SV_ArenaTypeContains( types, "duel" )',
		'SV_ArenaTypeContains( types, "race" )',
		'SV_ArenaTypeContains( types, "overload" )',
		'SV_ArenaTypeContains( types, "hh" )',
		'SV_ArenaTypeContains( types, "har" )',
		'SV_ArenaTypeContains( types, "ft" )',
		'SV_ArenaTypeContains( types, "dom" )',
		'SV_ArenaTypeContains( types, "ad" )',
		'SV_ArenaTypeContains( types, "rr" )',
	):
		assert expected in sv_type_support_snippet

	for forbidden in (
		'"clanarena"',
		'"obelisk"',
		'"freezetag"',
		'"attackdefend"',
		'"redrover"',
	):
		assert forbidden not in sv_type_support_snippet

	for expected in (
		"mapName = Info_ValueForKey( info, ARENA_INFO_KEY_MAP );",
		"longName = Info_ValueForKey( info, ARENA_INFO_KEY_LONGNAME );",
		"typeList = Info_ValueForKey( info, ARENA_INFO_KEY_TYPE );",
	):
		assert expected in client_snippet

	for expected in (
		"Info_SetValueForKey( g_arenaInfos[n], ARENA_INFO_KEY_NUM, va( \"%i\", n ) );",
		"Info_ValueForKey( g_arenaInfos[n], ARENA_INFO_KEY_MAP )",
		"Info_ValueForKey( info, ARENA_INFO_KEY_TYPE )",
		"Info_ValueForKey( arenainfo, ARENA_INFO_KEY_FRAGLIMIT )",
		"Info_ValueForKey( arenainfo, ARENA_INFO_KEY_TIMELIMIT )",
		"Info_ValueForKey( arenainfo, ARENA_INFO_KEY_SPECIAL )",
		"Info_ValueForKey( arenainfo, ARENA_INFO_KEY_BOTS )",
	):
		assert expected in game_load_snippet + game_lookup_snippet + game_gametype_snippet + game_init_snippet

	for forbidden in (
		'Info_ValueForKey( s_svArenaInfos[index], "map" )',
		'Info_ValueForKey( info, "type" )',
		'Info_ValueForKey( arenaInfo, "longname" )',
		'mapName = Info_ValueForKey( info, "map" );',
		'longName = Info_ValueForKey( info, "longname" );',
		'typeList = Info_ValueForKey( info, "type" );',
		'Info_SetValueForKey( g_arenaInfos[n], "num"',
		'Info_ValueForKey( g_arenaInfos[n], "map" )',
		'Info_ValueForKey( arenainfo, "fraglimit" )',
		'Info_ValueForKey( arenainfo, "timelimit" )',
		'Info_ValueForKey( arenainfo, "special" )',
		'Info_ValueForKey( arenainfo, "bots" )',
	):
		assert forbidden not in sv_lookup_snippet
		assert forbidden not in sv_gametype_snippet
		assert forbidden not in sv_title_snippet
		assert forbidden not in client_snippet
		assert forbidden not in game_load_snippet
		assert forbidden not in game_lookup_snippet
		assert forbidden not in game_gametype_snippet
		assert forbidden not in game_init_snippet


def test_retail_steam_protocol_version_matches_hlil_constants() -> None:
	qcommon_h = _read_text(QCOMMON_H_PATH)
	common_c = _read_text(COMMON_C_PATH)
	audit_note = _read_text(NETCODE_AUDIT_PATH)

	assert "#define\tQL_RETAIL_PROTOCOL_VERSION\t91" in qcommon_h
	assert "#define\tPROTOCOL_VERSION\tQL_RETAIL_PROTOCOL_VERSION" in qcommon_h
	assert "typedef struct {" in qcommon_h
	assert "const char\t\t*getChallengeCommand;" in qcommon_h
	assert "const char\t\t*challengeResponseCommand;" in qcommon_h
	assert "const char\t\t*connectCommand;" in qcommon_h
	assert "const char\t\t*connectResponseCommand;" in qcommon_h
	assert "const char\t\t*getInfoCommand;" in qcommon_h
	assert "const char\t\t*infoResponseCommand;" in qcommon_h
	assert "const char\t\t*getStatusCommand;" in qcommon_h
	assert "const char\t\t*statusResponseCommand;" in qcommon_h
	assert "const char\t\t*disconnectCommand;" in qcommon_h
	assert "const char\t\t*printCommand;" in qcommon_h
	assert "const char\t\t*echoCommand;" in qcommon_h
	assert "const char\t\t*rconCommand;" in qcommon_h
	assert "const char\t\t*getServersCommand;" in qcommon_h
	assert "const char\t\t*serversResponseCommand;" in qcommon_h
	assert "const char\t\t*getMotdCommand;" in qcommon_h
	assert "const char\t\t*motdResponseCommand;" in qcommon_h
	assert "const char\t\t*getKeyAuthorizeCommand;" in qcommon_h
	assert "const char\t\t*keyAuthorizeResponseCommand;" in qcommon_h
	assert "const char\t\t*getIpAuthorizeCommand;" in qcommon_h
	assert "const char\t\t*ipAuthorizeResponseCommand;" in qcommon_h
	assert "const char\t\t*heartbeatCommand;" in qcommon_h
	assert "const char\t\t*heartbeatGameName;" in qcommon_h
	assert "const char\t\t*downloadCommand;" in qcommon_h
	assert "const char\t\t*nextDownloadCommand;" in qcommon_h
	assert "const char\t\t*stopDownloadCommand;" in qcommon_h
	assert "const char\t\t*doneDownloadCommand;" in qcommon_h
	assert "const char\t\t*pureChecksumsCommand;" in qcommon_h
	assert "const char\t\t*encodedPureChecksumsCommand;" in qcommon_h
	assert "const char\t\t*pureResetCommand;" in qcommon_h
	assert "const char\t\t*userinfoCommand;" in qcommon_h
	assert "const char\t\t*reliableDisconnectCommand;" in qcommon_h
	assert "const char\t\t*protocolInfoKey;" in qcommon_h
	assert "const char\t\t*qportInfoKey;" in qcommon_h
	assert "const char\t\t*challengeInfoKey;" in qcommon_h
	assert "const char\t\t*motdChallengeInfoKey;" in qcommon_h
	assert "const char\t\t*motdInfoKey;" in qcommon_h
	assert "const char\t\t*motdRendererInfoKey;" in qcommon_h
	assert "const char\t\t*motdVersionInfoKey;" in qcommon_h
	assert "const char\t\t*hostnameInfoKey;" in qcommon_h
	assert "const char\t\t*mapnameInfoKey;" in qcommon_h
	assert "const char\t\t*clientsInfoKey;" in qcommon_h
	assert "const char\t\t*botPlayersInfoKey;" in qcommon_h
	assert "const char\t\t*vacInfoKey;" in qcommon_h
	assert "const char\t\t*serverTypeInfoKey;" in qcommon_h
	assert "const char\t\t*maxClientsInfoKey;" in qcommon_h
	assert "const char\t\t*gametypeInfoKey;" in qcommon_h
	assert "const char\t\t*pureInfoKey;" in qcommon_h
	assert "const char\t\t*minPingInfoKey;" in qcommon_h
	assert "const char\t\t*maxPingInfoKey;" in qcommon_h
	assert "const char\t\t*pingInfoKey;" in qcommon_h
	assert "const char\t\t*legacyMinPingInfoKey;" in qcommon_h
	assert "const char\t\t*legacyMaxPingInfoKey;" in qcommon_h
	assert "const char\t\t*gameInfoKey;" in qcommon_h
	assert "const char\t\t*netTypeInfoKey;" in qcommon_h
	assert "const char\t\t*addressInfoKey;" in qcommon_h
	assert "const char\t\t*punkbusterInfoKey;" in qcommon_h
	assert "const char\t\t*keywordsInfoKey;" in qcommon_h
	assert "const char\t\t*clientIpInfoKey;" in qcommon_h
	assert "const char\t\t*passwordInfoKey;" in qcommon_h
	assert "const char\t\t*nameInfoKey;" in qcommon_h
	assert "const char\t\t*rateInfoKey;" in qcommon_h
	assert "const char\t\t*handicapInfoKey;" in qcommon_h
	assert "const char\t\t*snapsInfoKey;" in qcommon_h
	assert "const char\t\t*serverIdInfoKey;" in qcommon_h
	assert "const char\t\t*cheatsInfoKey;" in qcommon_h
	assert "const char\t\t*paksInfoKey;" in qcommon_h
	assert "const char\t\t*pakNamesInfoKey;" in qcommon_h
	assert "const char\t\t*referencedPaksInfoKey;" in qcommon_h
	assert "const char\t\t*referencedPakNamesInfoKey;" in qcommon_h
	assert "const char\t\t*fsGameInfoKey;" in qcommon_h
	assert "const char\t\t*systemPureInfoKey;" in qcommon_h
	assert "int\t\t\t\tconnectProtocol;" in qcommon_h
	assert "qboolean\t\tusesNetchanClientQport;" in qcommon_h
	assert "qboolean\t\tusesReliableXorCodec;" in qcommon_h
	assert "qboolean\t\tusesLegacyQ3Authorize;" in qcommon_h
	assert "qboolean\t\tsupportsPlatformAuth;" in qcommon_h
	assert "const netprofile_desc_t *NET_GetProtocolProfile( void );" in qcommon_h

	assert "static const netprofile_desc_t s_netProtocolProfile = {" in common_c
	assert "NETPROFILE_QL_RETAIL," in common_c
	assert '"ql-retail-steam",' in common_c
	assert '"getchallenge",' in common_c
	assert '"challengeResponse",' in common_c
	assert '"connect",' in common_c
	assert '"connectResponse",' in common_c
	assert '"getinfo",' in common_c
	assert '"infoResponse",' in common_c
	assert '"getstatus",' in common_c
	assert '"statusResponse",' in common_c
	assert '"disconnect",' in common_c
	assert '"print",' in common_c
	assert '"echo",' in common_c
	assert '"rcon",' in common_c
	assert '"getservers",' in common_c
	assert '"getserversResponse",' in common_c
	assert '"getmotd",' in common_c
	assert '"motd",' in common_c
	assert '"getKeyAuthorize",' in common_c
	assert '"keyAuthorize",' in common_c
	assert '"getIpAuthorize",' in common_c
	assert '"ipAuthorize",' in common_c
	assert '"heartbeat",' in common_c
	assert '"QuakeArena-1",' in common_c
	assert '"download",' in common_c
	assert '"nextdl",' in common_c
	assert '"stopdl",' in common_c
	assert '"donedl",' in common_c
	assert '"cp",' in common_c
	assert '"Yf",' in common_c
	assert '"vdr",' in common_c
	assert '"userinfo",' in common_c
	assert '"protocol",' in common_c
	assert '"qport",' in common_c
	assert '"challenge",' in common_c
	assert '"motd",' in common_c
	assert '"renderer",' in common_c
	assert '"version",' in common_c
	assert '"hostname",' in common_c
	assert '"mapname",' in common_c
	assert '"clients",' in common_c
	assert '"botPlayers",' in common_c
	assert '"vac",' in common_c
	assert '"serverType",' in common_c
	assert '"sv_maxclients",' in common_c
	assert '"gametype",' in common_c
	assert '"pure",' in common_c
	assert '"minPing",' in common_c
	assert '"maxPing",' in common_c
	assert '"ping",' in common_c
	assert '"minping",' in common_c
	assert '"maxping",' in common_c
	assert '"game",' in common_c
	assert '"nettype",' in common_c
	assert '"addr",' in common_c
	assert '"punkbuster",' in common_c
	assert '"sv_keywords",' in common_c
	assert '"ip",' in common_c
	assert '"password",' in common_c
	assert '"name",' in common_c
	assert '"rate",' in common_c
	assert '"handicap",' in common_c
	assert '"snaps",' in common_c
	assert '"sv_serverid",' in common_c
	assert '"sv_cheats",' in common_c
	assert '"sv_paks",' in common_c
	assert '"sv_pakNames",' in common_c
	assert '"sv_referencedPaks",' in common_c
	assert '"sv_referencedPakNames",' in common_c
	assert '"fs_game",' in common_c
	assert '"sv_pure",' in common_c
	assert "QL_RETAIL_PROTOCOL_VERSION," in common_c
	assert "qfalse,\n\tNET_PROFILE_SUPPORTS_PLATFORM_AUTH,\n\tqfalse," in common_c
	assert "int demo_protocols[] =\n{ QL_RETAIL_PROTOCOL_VERSION, 0 };" in common_c
	assert "{ 66, 67, 68, 0 }" not in common_c

	assert "0x5b / 91" in audit_note
	assert "`data_5684dc = 0x5b`" in audit_note
	assert "`data_5684e0 = 0`" in audit_note
	assert "`dm_91`" in audit_note


def test_retail_protocol_profile_is_used_by_handshake_and_demo_paths() -> None:
	cl_main = _read_text(CL_MAIN_PATH)
	net_chan = _read_text(NET_CHAN_PATH)
	common_c = _read_text(COMMON_C_PATH)
	qcommon_h = _read_text(QCOMMON_H_PATH)

	sv_init = (REPO_ROOT / "src" / "code" / "server" / "sv_init.c").read_text(encoding="utf-8")
	sv_main = (REPO_ROOT / "src" / "code" / "server" / "sv_main.c").read_text(encoding="utf-8")
	sv_client = (REPO_ROOT / "src" / "code" / "server" / "sv_client.c").read_text(encoding="utf-8")
	cl_cgame = (REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c").read_text(encoding="utf-8")
	cl_net_chan = (REPO_ROOT / "src" / "code" / "client" / "cl_net_chan.c").read_text(encoding="utf-8")
	cl_parse = (REPO_ROOT / "src" / "code" / "client" / "cl_parse.c").read_text(encoding="utf-8")
	sv_net_chan = (REPO_ROOT / "src" / "code" / "server" / "sv_net_chan.c").read_text(encoding="utf-8")
	files_c = (REPO_ROOT / "src" / "code" / "qcommon" / "files.c").read_text(encoding="utf-8")

	assert "int NET_ProtocolVersion( void ) {" in common_c
	assert "int NET_DemoProtocol( void ) {" in common_c
	assert "qboolean NET_ProtocolSupports( int protocol ) {" in common_c
	assert "qboolean NET_IsGetChallengeRequest( const char *command ) {" in common_c
	assert "qboolean NET_IsChallengeResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsConnectRequest( const char *command ) {" in common_c
	assert "qboolean NET_IsConnectResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsGetInfoRequest( const char *command ) {" in common_c
	assert "qboolean NET_IsInfoResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsGetStatusRequest( const char *command ) {" in common_c
	assert "qboolean NET_IsStatusResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsDisconnectCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsPrintCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsEchoCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsRconCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsGetServersRequest( const char *command ) {" in common_c
	assert "qboolean NET_IsServersResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsMotdResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsKeyAuthorizeResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsIpAuthorizeResponse( const char *command ) {" in common_c
	assert "qboolean NET_IsDownloadRequestCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsDownloadNextCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsDownloadStopCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsDownloadDoneCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsPureChecksumsCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsPureResetCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsUserinfoCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsReliableDisconnectCommand( const char *command ) {" in common_c
	assert "qboolean NET_IsConnectRequestPacket( const msg_t *msg ) {" in common_c
	assert "const char *NET_GetDownloadRequestCommand( void ) {" in common_c
	assert "void\t\tNET_OutOfBandRaw( netsrc_t sock, netadr_t adr, const byte *data, int len );" in qcommon_h
	assert "void NET_OutOfBandRaw( netsrc_t sock, netadr_t adr, const byte *data, int len ) {" in net_chan
	assert "const char *NET_GetPrintCommand( void ) {" in common_c
	assert "const char *NET_GetEchoCommand( void ) {" in common_c
	assert "const char *NET_GetRconCommand( void ) {" in common_c
	assert "const char *NET_GetServersRequestCommand( void ) {" in common_c
	assert "const char *NET_GetServersResponseCommand( void ) {" in common_c
	assert "const char *NET_GetMotdRequestCommand( void ) {" in common_c
	assert "const char *NET_GetMotdResponseCommand( void ) {" in common_c
	assert "const char *NET_GetKeyAuthorizeRequestCommand( void ) {" in common_c
	assert "const char *NET_GetKeyAuthorizeResponseCommand( void ) {" in common_c
	assert "const char *NET_GetIpAuthorizeRequestCommand( void ) {" in common_c
	assert "const char *NET_GetIpAuthorizeResponseCommand( void ) {" in common_c
	assert "const char *NET_GetHeartbeatCommand( void ) {" in common_c
	assert "const char *NET_GetHeartbeatGameName( void ) {" in common_c
	assert "const char *NET_GetDownloadNextCommand( void ) {" in common_c
	assert "const char *NET_GetDownloadStopCommand( void ) {" in common_c
	assert "const char *NET_GetDownloadDoneCommand( void ) {" in common_c
	assert "const char *NET_GetPureChecksumsCommand( void ) {" in common_c
	assert "const char *NET_GetEncodedPureChecksumsCommand( void ) {" in common_c
	assert "const char *NET_GetPureResetCommand( void ) {" in common_c
	assert "const char *NET_GetUserinfoCommand( void ) {" in common_c
	assert "const char *NET_GetReliableDisconnectCommand( void ) {" in common_c
	assert "const char *NET_GetProtocolInfoKey( void ) {" in common_c
	assert "const char *NET_GetQportInfoKey( void ) {" in common_c
	assert "const char *NET_GetChallengeInfoKey( void ) {" in common_c
	assert "const char *NET_GetMotdChallengeInfoKey( void ) {" in common_c
	assert "const char *NET_GetMotdInfoKey( void ) {" in common_c
	assert "const char *NET_GetMotdRendererInfoKey( void ) {" in common_c
	assert "const char *NET_GetMotdVersionInfoKey( void ) {" in common_c
	assert "const char *NET_GetHostnameInfoKey( void ) {" in common_c
	assert "const char *NET_GetMapnameInfoKey( void ) {" in common_c
	assert "const char *NET_GetClientsInfoKey( void ) {" in common_c
	assert "const char *NET_GetBotPlayersInfoKey( void ) {" in common_c
	assert "const char *NET_GetVACInfoKey( void ) {" in common_c
	assert "const char *NET_GetServerTypeInfoKey( void ) {" in common_c
	assert "const char *NET_GetMaxClientsInfoKey( void ) {" in common_c
	assert "const char *NET_GetGametypeInfoKey( void ) {" in common_c
	assert "const char *NET_GetPureInfoKey( void ) {" in common_c
	assert "const char *NET_GetMinPingInfoKey( void ) {" in common_c
	assert "const char *NET_GetMaxPingInfoKey( void ) {" in common_c
	assert "const char *NET_GetPingInfoKey( void ) {" in common_c
	assert "const char *NET_GetLegacyMinPingInfoKey( void ) {" in common_c
	assert "const char *NET_GetLegacyMaxPingInfoKey( void ) {" in common_c
	assert "const char *NET_GetGameInfoKey( void ) {" in common_c
	assert "const char *NET_GetNetTypeInfoKey( void ) {" in common_c
	assert "const char *NET_GetAddressInfoKey( void ) {" in common_c
	assert "const char *NET_GetPunkbusterInfoKey( void ) {" in common_c
	assert "const char *NET_GetKeywordsInfoKey( void ) {" in common_c
	assert "const char *NET_GetClientIpInfoKey( void ) {" in common_c
	assert "const char *NET_GetPasswordInfoKey( void ) {" in common_c
	assert "const char *NET_GetNameInfoKey( void ) {" in common_c
	assert "const char *NET_GetRateInfoKey( void ) {" in common_c
	assert "const char *NET_GetHandicapInfoKey( void ) {" in common_c
	assert "const char *NET_GetSnapsInfoKey( void ) {" in common_c
	assert "const char *NET_GetServerIdInfoKey( void ) {" in common_c
	assert "const char *NET_GetCheatsInfoKey( void ) {" in common_c
	assert "const char *NET_GetPaksInfoKey( void ) {" in common_c
	assert "const char *NET_GetPakNamesInfoKey( void ) {" in common_c
	assert "const char *NET_GetReferencedPaksInfoKey( void ) {" in common_c
	assert "const char *NET_GetReferencedPakNamesInfoKey( void ) {" in common_c
	assert "const char *NET_GetFsGameInfoKey( void ) {" in common_c
	assert "const char *NET_GetSystemPureInfoKey( void ) {" in common_c
	assert "qboolean NET_ProtocolUsesClientQport( void ) {" in common_c
	assert "qboolean NET_ProtocolUsesNetchanClientQport( void ) {" in common_c
	assert "qboolean NET_ProtocolUsesReliableXorCodec( void ) {" in common_c
	assert "qboolean NET_ProtocolUsesLegacyAuthorize( void ) {" in common_c
	assert "qboolean NET_ProtocolUsesCompressedConnect( void ) {" in common_c
	assert "qboolean NET_ProtocolSupportsPlatformAuth( void ) {" in common_c

	assert 'Cvar_Get ("protocol", va("%i", NET_ProtocolVersion()), CVAR_SERVERINFO | CVAR_ROM);' in sv_init
	assert 'Info_SetValueForKey( infostring, NET_GetProtocolInfoKey(), va("%i", NET_ProtocolVersion()) );' in sv_main
	assert 'if ( !NET_ProtocolSupports( version ) ) {' in sv_client
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s\\nServer uses protocol version %i.\\n", NET_GetPrintCommand(), NET_ProtocolVersion() );' in sv_client
	assert 'if ( !NET_ProtocolSupports( prot ) ) {' in cl_main
	assert 'Info_SetValueForKey( info, NET_GetProtocolInfoKey(), va("%i", NET_ProtocolVersion() ) );' in cl_main
	assert 'Info_SetValueForKey( info, NET_GetQportInfoKey(), va("%i", port ) );' in cl_main
	assert 'Info_SetValueForKey( info, NET_GetChallengeInfoKey(), va("%i", clc.challenge ) );' in cl_main
	assert 'version = atoi( Info_ValueForKey( userinfo, NET_GetProtocolInfoKey() ) );' in sv_client
	assert 'challenge = atoi( Info_ValueForKey( userinfo, NET_GetChallengeInfoKey() ) );' in sv_client
	assert 'qport = atoi( Info_ValueForKey( userinfo, NET_GetQportInfoKey() ) );' in sv_client
	assert 'Info_SetValueForKey( userinfo, NET_GetClientIpInfoKey(), NET_AdrToString( from ) );' in sv_client
	assert 'Info_SetValueForKey( userinfo, NET_GetClientIpInfoKey(), "localhost" );' in sv_client
	assert 'password = Info_ValueForKey( userinfo, NET_GetPasswordInfoKey() );' in sv_client
	assert 'Q_strncpyz( cl->name, Info_ValueForKey (cl->userinfo, NET_GetNameInfoKey()), sizeof(cl->name) );' in sv_client
	assert 'val = Info_ValueForKey (cl->userinfo, NET_GetRateInfoKey());' in sv_client
	assert 'val = Info_ValueForKey (cl->userinfo, NET_GetHandicapInfoKey());' in sv_client
	assert 'Info_SetValueForKey( cl->userinfo, NET_GetHandicapInfoKey(), "100" );' in sv_client
	assert 'val = Info_ValueForKey (cl->userinfo, NET_GetSnapsInfoKey());' in sv_client
	assert 'val = Info_ValueForKey (cl->userinfo, NET_GetClientIpInfoKey());' in sv_client
	assert 'Info_SetValueForKey( cl->userinfo, NET_GetClientIpInfoKey(), NET_AdrToString( cl->netchan.remoteAddress ) );' in sv_client
	assert 'prot = atoi( Info_ValueForKey( infoString, NET_GetProtocolInfoKey() ) );' in cl_main
	assert 'Info_SetValueForKey( infostring, NET_GetChallengeInfoKey(), Cmd_Argv(1) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetHostnameInfoKey(), sv_hostname->string );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetMapnameInfoKey(), sv_mapname->string );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetClientsInfoKey(), va("%i", count) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetClientsInfoKey(), va("%i", visibleClients) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetBotPlayersInfoKey(), va("%i", botCount) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetVACInfoKey(), va("%i", sv_vac->integer) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetServerTypeInfoKey(), va("%i", sv_serverType->integer) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetMaxClientsInfoKey(),' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetGametypeInfoKey(), va("%i", sv_gametype->integer ) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetPureInfoKey(), va("%i", sv_pure->integer ) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetMinPingInfoKey(), va("%i", sv_minPing->integer) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetMaxPingInfoKey(), va("%i", sv_maxPing->integer) );' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetGameInfoKey(), gamedir );' in sv_main
	assert 'Info_ValueForKey( infostring, NET_GetKeywordsInfoKey() )' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetKeywordsInfoKey(), keywords );' in sv_main
	assert "static qboolean CL_BuildSteamChallengeRequest( byte *data, int dataSize, int *dataLength ) {" in cl_main
	assert "QL_ClientAuth_RequestSteamChallengeTicket( ticket, sizeof( ticket ), &ticketLength, &steamIdLow, &steamIdHigh )" in cl_main
	assert "payloadLength = commandLength + 1 + 8 + ticketLength;" in cl_main
	assert "CL_WriteSteamChallengeWord( data + commandLength + 1, steamIdLow );" in cl_main
	assert "CL_WriteSteamChallengeWord( data + commandLength + 5, steamIdHigh );" in cl_main
	assert "Com_Memcpy( data + commandLength + 9, ticket, ticketLength );" in cl_main
	assert "NET_OutOfBandRaw( NS_CLIENT, clc.serverAddress, data, dataLength );" in cl_main
	assert 'NET_OutOfBandPrint( NS_CLIENT, clc.serverAddress, "%s", NET_GetChallengeRequestCommand() );' in cl_main
	assert "CL_SendChallengeRequest();" in cl_main
	assert 'Com_sprintf( data, sizeof( data ), "%s \\"%s\\"", NET_GetConnectRequestCommand(), info );' in cl_main
	assert 'if ( NET_IsChallengeResponse( c ) ) {' in cl_main
	assert 'if ( NET_IsConnectResponse( c ) ) {' in cl_main
	assert 'if ( NET_IsInfoResponse( c ) ) {' in cl_main
	assert 'if ( NET_IsStatusResponse( c ) ) {' in cl_main
	assert 'if ( NET_IsDisconnectCommand( c ) ) {' in cl_main
	assert 'NET_OutOfBandPrint( NS_CLIENT, to, "%s", NET_GetStatusRequestCommand() );' in cl_main
	assert 'Com_sprintf( message, sizeof( message ), "\\377\\377\\377\\377%s xxx", NET_GetInfoRequestCommand() );' in cl_main
	assert 'NET_OutOfBandPrint( NS_CLIENT, cl_pinglist[j].adr, "%s xxx", NET_GetInfoRequestCommand() );' in cl_main
	assert 'Com_sprintf( command, sizeof( command ), "%s %s", NET_GetServersRequestCommand(), protocol );' in cl_main
	assert "if ( NET_IsServersResponse( c ) ) {" in cl_main
	assert 'Info_SetValueForKey( info, NET_GetMotdChallengeInfoKey(), cls.updateChallenge );' in cl_main
	assert 'Info_SetValueForKey( info, NET_GetMotdRendererInfoKey(), cls.glconfig.renderer_string );' in cl_main
	assert 'Info_SetValueForKey( info, NET_GetMotdVersionInfoKey(), com_version->string );' in cl_main
	assert "server->clients = atoi(Info_ValueForKey(info, NET_GetClientsInfoKey()));" in cl_main
	assert "Q_strncpyz(server->hostName,Info_ValueForKey(info, NET_GetHostnameInfoKey()), MAX_NAME_LENGTH);" in cl_main
	assert "Q_strncpyz(server->mapName, Info_ValueForKey(info, NET_GetMapnameInfoKey()), MAX_NAME_LENGTH);" in cl_main
	assert "server->maxClients = atoi(Info_ValueForKey(info, NET_GetMaxClientsInfoKey()));" in cl_main
	assert "Q_strncpyz(server->game,Info_ValueForKey(info, NET_GetGameInfoKey()), MAX_NAME_LENGTH);" in cl_main
	assert "server->gameType = atoi(Info_ValueForKey(info, NET_GetGametypeInfoKey()));" in cl_main
	assert "server->netType = atoi(Info_ValueForKey(info, NET_GetNetTypeInfoKey()));" in cl_main
	assert 'Info_SetValueForKey( cl_pinglist[i].info, NET_GetNetTypeInfoKey(), va("%d", type) );' in cl_main
	assert 'NET_OutOfBandPrint( NS_CLIENT, cls.updateServer, "%s \\"%s\\"\\n", NET_GetMotdRequestCommand(), info );' in cl_main
	assert "challenge = Info_ValueForKey( info, NET_GetMotdChallengeInfoKey() );" in cl_main
	assert "challenge = Info_ValueForKey( info, NET_GetMotdInfoKey() );" in cl_main
	assert "if ( NET_IsMotdResponse( c ) ) {" in cl_main
	assert 'va("%s %i %s", NET_GetKeyAuthorizeRequestCommand(), Cvar_VariableIntegerValue( "cl_anonymous" ), authorizePayload)' in cl_main
	assert "if ( NET_IsKeyAuthorizeResponse( c ) ) {" in cl_main

	for source in (cl_main, cl_cgame, files_c):
		assert "NET_DemoProtocol()" in source

	assert "NET_ProtocolUsesLegacyAuthorize() && !Sys_IsLANAddress( clc.serverAddress )" in cl_main
	assert "NET_ProtocolSupportsPlatformAuth()" in cl_main
	assert "protocol profile %s does not use the Quake III authorize lane" in cl_main
	assert "protocol profile %s does not use the Quake III authorize lane" in sv_client
	assert 'if ( NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket( msg ) ) {' in sv_main
	assert "if ( NET_IsGetStatusRequest( c ) ) {" in sv_main
	assert "} else if ( NET_IsGetInfoRequest( c ) ) {" in sv_main
	assert "} else if ( NET_IsGetChallengeRequest( c ) ) {" in sv_main
	assert "SV_GetChallenge( from, msg );" in sv_main
	assert "} else if ( NET_IsConnectRequest( c ) ) {" in sv_main
	assert "} else if ( NET_IsIpAuthorizeResponse( c ) ) {" in sv_main
	assert "} else if ( NET_IsRconCommand( c ) ) {" in sv_main
	assert "} else if ( NET_IsDisconnectCommand( c ) ) {" in sv_main
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s\\n%s\\n%s", NET_GetStatusResponseCommand(), infostring, status );' in sv_main
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s\\n%s", NET_GetInfoResponseCommand(), infostring );' in sv_main
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s", NET_GetDisconnectCommand() );' in sv_main
	assert 'NET_OutOfBandPrint( NS_SERVER, svs.redirectAddress, "%s\\n%s", NET_GetPrintCommand(), outputbuf );' in sv_main
	assert 'NET_OutOfBandPrint( NS_SERVER, adr[i], "%s %s\\n", NET_GetHeartbeatCommand(), NET_GetHeartbeatGameName() );' in sv_main
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s %i", NET_GetChallengeResponseCommand(), challenge->challenge );' in sv_client
	assert "static qboolean SV_ParseSteamChallengeAuth( challenge_t *challenge, const msg_t *msg, const char **rejectMessage ) {" in sv_client
	assert "steamIdOffset = 4 + (int)strlen( command ) + 1;" in sv_client
	assert "ticketOffset = steamIdOffset + 8;" in sv_client
	assert "ticketLength = msg->cursize - ticketOffset;" in sv_client
	assert "ticketLength <= QL_STEAM_CHALLENGE_TOKEN_MIN_LENGTH" in sv_client
	assert "ticketLength > QL_STEAM_AUTH_TICKET_MAX_LENGTH" in sv_client
	assert '*rejectMessage = "No Steam auth token.";' in sv_client
	assert '*rejectMessage = "Auth token too large.";' in sv_client
	assert "SV_CapturePlatformAuthFromChallenge( newcl, &svs.challenges[challengeIndex] )" in sv_client
	assert 'Info_SetValueForKey( userinfo, "steam", newcl->platformSteamId );' in sv_client
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s", NET_GetConnectResponseCommand() );' in sv_client
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s\\nServer uses protocol version %i.\\n", NET_GetPrintCommand(), NET_ProtocolVersion() );' in sv_client
	assert 'NET_OutOfBandPrint( NS_SERVER, svs.authorizeAddress,' in sv_client
	assert '"%s %i %i.%i.%i.%i %s 0 %s", NET_GetIpAuthorizeRequestCommand(), svs.challenges[i].challenge,' in sv_client
	assert "if ( NET_ProtocolUsesCompressedConnect() ) {" in cl_main
	assert "if ( NET_IsEchoCommand( c ) ) {" in cl_main
	assert "if ( NET_IsPrintCommand( c ) ) {" in cl_main
	assert "NET_ProtocolUsesNetchanClientQport()" in net_chan
	assert "NET_ProtocolUsesReliableXorCodec()" in cl_net_chan
	assert "NET_ProtocolUsesReliableXorCodec()" in sv_net_chan
	assert 'CL_AddReliableCommand( va("%s %s", NET_GetDownloadRequestCommand(), remoteName) );' in cl_main
	assert 'CL_AddReliableCommand( NET_GetDownloadDoneCommand() );' in cl_main
	assert 'CL_AddReliableCommand( NET_GetDownloadStopCommand() );' in cl_parse
	assert 'CL_AddReliableCommand( va("%s %d", NET_GetDownloadNextCommand(), clc.downloadBlock) );' in cl_parse
	assert 'cl.serverId = atoi( Info_ValueForKey( systemInfo, NET_GetServerIdInfoKey() ) );' in cl_parse
	assert 's = Info_ValueForKey( systemInfo, NET_GetCheatsInfoKey() );' in cl_parse
	assert 's = Info_ValueForKey( systemInfo, NET_GetPaksInfoKey() );' in cl_parse
	assert 't = Info_ValueForKey( systemInfo, NET_GetPakNamesInfoKey() );' in cl_parse
	assert 's = Info_ValueForKey( systemInfo, NET_GetReferencedPaksInfoKey() );' in cl_parse
	assert 't = Info_ValueForKey( systemInfo, NET_GetReferencedPakNamesInfoKey() );' in cl_parse
	assert 'if ( !Q_stricmp( key, NET_GetFsGameInfoKey() ) ) {' in cl_parse
	assert 'if ( !gameSet && *Cvar_VariableString( NET_GetFsGameInfoKey() ) ) {' in cl_parse
	assert 'Cvar_Set( NET_GetFsGameInfoKey(), "" );' in cl_parse
	assert 'cl_connectedToPureServer = Cvar_VariableValue( NET_GetSystemPureInfoKey() );' in cl_parse
	assert "{NULL, NET_GetDownloadRequestCommand, SV_BeginDownload_f}," in sv_client
	assert "{NULL, NET_GetDownloadNextCommand, SV_NextDownload_f}," in sv_client
	assert "{NULL, NET_GetDownloadStopCommand, SV_StopDownload_f}," in sv_client
	assert "{NULL, NET_GetDownloadDoneCommand, SV_DoneDownload_f}," in sv_client
	assert "pureCommand = NET_GetEncodedPureChecksumsCommand();" in cl_main
	assert 'Com_sprintf(cMsg, sizeof(cMsg), "%s ", pureCommand);' in cl_main
	assert "pureCommandLength = strlen( pureCommand );" in cl_main
	assert "for (i = 0; i < pureCommandLength; i++) {" in cl_main
	assert "CL_AddReliableCommand( NET_GetPureResetCommand() );" in cl_main
	assert "{NULL, NET_GetPureChecksumsCommand, SV_VerifyPaks_f}," in sv_client
	assert "{NULL, NET_GetPureResetCommand, SV_ResetPureClient_f}," in sv_client
	assert "CL_AddReliableCommand( NET_GetReliableDisconnectCommand() );" in cl_main
	assert 'CL_AddReliableCommand( va("%s \\"%s\\"", NET_GetUserinfoCommand(), Cvar_InfoString( CVAR_USERINFO ) ) );' in cl_main
	assert "userinfoCommand = NET_GetUserinfoCommand();" in cl_main
	assert "userinfoCommandLength = strlen( userinfoCommand );" in cl_main
	assert "Q_stricmpn( cursor, userinfoCommand, userinfoCommandLength )" in cl_main
	assert 'SV_SendServerCommand( drop, "%s \\"%s\\"", NET_GetReliableDisconnectCommand(), reason);' in sv_client
	assert "{NULL, NET_GetUserinfoCommand, SV_UpdateUserinfo_f}," in sv_client
	assert "{NULL, NET_GetReliableDisconnectCommand, SV_Disconnect_f}," in sv_client
	assert "commandName = u->name ? u->name : u->profileName();" in sv_client
	assert "strstr(cl->lastClientCommandString, NET_GetDownloadNextCommand())" in sv_client
	assert "PROTOCOL_VERSION\tQL_RETAIL_PROTOCOL_VERSION" in qcommon_h
	assert "PROTOCOL_VERSION" not in net_chan

	for hardcoded in (
		'NET_OutOfBandPrint(NS_CLIENT, clc.serverAddress, "getchallenge");',
		'if ( !Q_stricmp(c, "challengeResponse") ) {',
		'if ( !Q_stricmp(c, "connectResponse") ) {',
		'if (!Q_stricmp(c, "getchallenge")) {',
		'if (!Q_stricmp(c, "connect")) {',
		'if (!Q_stricmp(c, "getstatus")) {',
		'if (!Q_stricmp(c, "getinfo")) {',
		'if ( !Q_stricmp(c, "infoResponse") ) {',
		'if ( !Q_stricmp(c, "statusResponse") ) {',
		'if ( !Q_stricmp(c, "echo") ) {',
		'if ( !Q_stricmp(c, "print") ) {',
		'} else if (!Q_stricmp(c, "rcon")) {',
		'if ( !Q_stricmp(c, "keyAuthorize") ) {',
		'} else if (!Q_stricmp(c, "ipAuthorize")) {',
		'if ( !Q_strncmp(c, "getserversResponse", 18) ) {',
		'if ( !Q_stricmp(c, "motd") ) {',
		'NET_OutOfBandPrint( NS_CLIENT, to, "getstatus" );',
		'NET_OutOfBandPrint( NS_CLIENT, cl_pinglist[j].adr, "getinfo xxx" );',
		'NET_OutOfBandPrint( NS_CLIENT, cls.updateServer, "getmotd \\"%s\\"\\n", info );',
		'va("getKeyAuthorize %i %s", Cvar_VariableIntegerValue( "cl_anonymous" ), authorizePayload)',
		'NET_OutOfBandPrint( NS_SERVER, from, "connectResponse" );',
		'NET_OutOfBandPrint( NS_SERVER, from, "disconnect" );',
		'Com_sprintf( command, sizeof( command ), "getservers %s", protocol );',
		'Com_DPrintf( "sending getIpAuthorize for %s\\n", NET_AdrToString( from ));',
		'"getIpAuthorize %i %i.%i.%i.%i %s 0 %s",  svs.challenges[i].challenge,',
		'NET_OutOfBandPrint( NS_SERVER, adr[i], "heartbeat %s\\n", HEARTBEAT_GAME );',
		'#define HEARTBEAT_GAME\t"QuakeArena-1"',
		'NET_OutOfBandPrint( NS_SERVER, svs.redirectAddress, "print\\n%s", outputbuf );',
		'NET_OutOfBandPrint( NS_SERVER, from, "print\\nServer uses protocol version %i.\\n", NET_ProtocolVersion() );',
		'Info_SetValueForKey( info, "protocol", va("%i", NET_ProtocolVersion() ) );',
		'Info_SetValueForKey( info, "qport", va("%i", port ) );',
		'Info_SetValueForKey( info, "challenge", va("%i", clc.challenge ) );',
		'Info_SetValueForKey( info, "challenge", cls.updateChallenge );',
		'Info_SetValueForKey( info, "renderer", cls.glconfig.renderer_string );',
		'Info_SetValueForKey( info, "version", com_version->string );',
		'challenge = Info_ValueForKey( info, "challenge" );',
		'challenge = Info_ValueForKey( info, "motd" );',
		'version = atoi( Info_ValueForKey( userinfo, "protocol" ) );',
		'challenge = atoi( Info_ValueForKey( userinfo, "challenge" ) );',
		'qport = atoi( Info_ValueForKey( userinfo, "qport" ) );',
		'Info_SetValueForKey( userinfo, "ip", NET_AdrToString( from ) );',
		'Info_SetValueForKey( userinfo, "ip", "localhost" );',
		'password = Info_ValueForKey( userinfo, "password" );',
		'Q_strncpyz( cl->name, Info_ValueForKey (cl->userinfo, "name"), sizeof(cl->name) );',
		'val = Info_ValueForKey (cl->userinfo, "rate");',
		'val = Info_ValueForKey (cl->userinfo, "handicap");',
		'Info_SetValueForKey( cl->userinfo, "handicap", "100" );',
		'val = Info_ValueForKey (cl->userinfo, "snaps");',
		'val = Info_ValueForKey (cl->userinfo, "ip");',
		'Info_SetValueForKey( cl->userinfo, "ip", NET_AdrToString( cl->netchan.remoteAddress ) );',
		'Info_SetValueForKey( cl->userinfo, "ip", "localhost" );',
		'prot = atoi( Info_ValueForKey( infoString, "protocol" ) );',
		'cl.serverId = atoi( Info_ValueForKey( systemInfo, "sv_serverid" ) );',
		's = Info_ValueForKey( systemInfo, "sv_cheats" );',
		's = Info_ValueForKey( systemInfo, "sv_paks" );',
		't = Info_ValueForKey( systemInfo, "sv_pakNames" );',
		's = Info_ValueForKey( systemInfo, "sv_referencedPaks" );',
		't = Info_ValueForKey( systemInfo, "sv_referencedPakNames" );',
		'if ( !Q_stricmp( key, "fs_game" ) ) {',
		'if ( !gameSet && *Cvar_VariableString("fs_game") ) {',
		'Cvar_Set( "fs_game", "" );',
		'cl_connectedToPureServer = Cvar_VariableValue( "sv_pure" );',
		'Info_SetValueForKey( infostring, "protocol", va("%i", NET_ProtocolVersion()) );',
		'CL_AddReliableCommand( va("download %s", remoteName) );',
		'CL_AddReliableCommand( "donedl" );',
		'CL_AddReliableCommand( "stopdl" );',
		'CL_AddReliableCommand( va("nextdl %d", clc.downloadBlock) );',
		'{"download", SV_BeginDownload_f},',
		'{"nextdl", SV_NextDownload_f},',
		'{"stopdl", SV_StopDownload_f},',
		'{"donedl", SV_DoneDownload_f},',
		'strstr(cl->lastClientCommandString, "nextdl")',
		'{"cp", NULL, SV_VerifyPaks_f},',
		'{"vdr", NULL, SV_ResetPureClient_f},',
		'CL_AddReliableCommand( va("vdr") );',
		'Com_sprintf(cMsg, sizeof(cMsg), "Yf ");',
		'CL_AddReliableCommand( "disconnect" );',
		'CL_AddReliableCommand( va("userinfo \\"%s\\"", Cvar_InfoString( CVAR_USERINFO ) ) );',
		'SV_SendServerCommand( drop, "disconnect \\"%s\\"", reason);',
		'{"userinfo", NULL, SV_UpdateUserinfo_f},',
		'{"disconnect", NULL, SV_Disconnect_f},',
		'Q_stricmpn( cursor, "userinfo", 8 )',
	):
		assert hardcoded not in cl_main
		assert hardcoded not in sv_main
		assert hardcoded not in sv_client
		assert hardcoded not in cl_parse


def test_ping_helper_lane_does_not_keep_unrecovered_update_wrapper() -> None:
	cl_main = _read_text(CL_MAIN_PATH)
	get_ping_marker = "void CL_GetPing( int n, char *buf, int buflen, int *pingtime )"
	get_ping_info_marker = "void CL_GetPingInfo( int n, char *buf, int buflen )"

	assert "void CL_UpdateServerInfo( int n )" not in cl_main
	between = cl_main.split(get_ping_marker, 1)[1].split(get_ping_info_marker, 1)[0]
	assert "CL_UpdateServerInfo" not in between
	assert (
		"CL_SetServerInfoByAddress(cl_pinglist[n].adr, cl_pinglist[n].info, cl_pinglist[n].time);"
		in between
	)


def test_shared_net_address_helpers_match_retail_type_contracts() -> None:
	net_chan = _read_text(NET_CHAN_PATH)
	compare_base = _snippet_after(
		net_chan,
		"qboolean\tNET_CompareBaseAdr (netadr_t a, netadr_t b)",
		18,
	)
	compare_adr = _snippet_after(
		net_chan,
		"qboolean\tNET_CompareAdr (netadr_t a, netadr_t b)",
		20,
	)

	assert "if (a.type == NA_LOOPBACK)" in compare_base
	assert "if (a.type == NA_IP)" in compare_base
	assert 'Com_Printf ("NET_CompareBaseAdr: bad address type\\n");' in compare_base
	assert "if (a.type == NA_LOOPBACK || a.type == NA_BOT)" in compare_adr
	assert "if (a.type == NA_IP)" in compare_adr
	assert 'Com_Printf ("NET_CompareAdr: bad address type\\n");' in compare_adr

	for forbidden in (
		"if (a.type == NA_IPX)",
		"memcmp(a.ipx, b.ipx, 10)",
	):
		assert forbidden not in compare_base
		assert forbidden not in compare_adr


def test_native_lan_cache_import_slots_stay_retail_noops() -> None:
	ql_ui_imports = _read_text(QL_UI_IMPORTS_PATH)
	cl_ui = _read_text(CL_UI_PATH)
	audit_note = _read_text(NETCODE_AUDIT_PATH)

	save_snippet = _snippet_after(
		ql_ui_imports,
		"static void QDECL QL_UI_trap_LAN_SaveCachedServers(  ) {",
		4,
	)
	load_snippet = _snippet_after(
		ql_ui_imports,
		"static void QDECL QL_UI_trap_LAN_LoadCachedServers(  ) {",
		4,
	)

	assert "Retail native import slot is a no-op." in save_snippet
	assert "Retail native import slot is a no-op." in load_snippet
	assert "UI_Import_Syscall( UI_LAN_SAVECACHEDSERVERS );" not in save_snippet
	assert "UI_Import_Syscall( UI_LAN_LOADCACHEDSERVERS );" not in load_snippet

	assert (
		"ql_ui_imports[UI_QL_IMPORT_LAN_LOADCACHEDSERVERS] = "
		"(ql_import_f)QL_UI_trap_LAN_LoadCachedServers;"
	) in cl_ui
	assert (
		"ql_ui_imports[UI_QL_IMPORT_LAN_SAVECACHEDSERVERS] = "
		"(ql_import_f)QL_UI_trap_LAN_SaveCachedServers;"
	) in cl_ui

	assert "CL_SetServerInfo" in audit_note
	assert "QLUIImport_LAN_LoadCachedServers" in audit_note
	assert "QLUIImport_LAN_SaveCachedServers" in audit_note
