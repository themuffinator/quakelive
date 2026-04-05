"""Guard the retail-backed cgame scoreboard social path against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_CONSOLECMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"


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


def test_clientmute_command_routes_identity_words_through_native_callback() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static void CG_ClientMute_f")

	assert '{ "clientmute", CG_ClientMute_f }' in source
	assert 'trap_Argv( 1, arg, sizeof( arg ) );' in block
	assert 'clientNum = atoi( arg );' in block
	assert 'clientNum < 0 || clientNum >= MAX_CLIENTS' in block
	assert 'ci = &cgs.clientinfo[clientNum];' in block
	assert 'if ( ( ci->identityLow | ci->identityHigh ) == 0 ) {' in block
	assert 'trap_QL_ToggleClientMute( ci->identityLow, ci->identityHigh );' in block
	assert 'cg.clientMuted[clientNum] = (qboolean)!cg.clientMuted[clientNum];' not in block


def test_scoreboard_headers_track_local_social_state_and_media() -> None:
	source = CG_LOCAL.read_text(encoding="utf-8")

	assert "qboolean\t\tclientMuted[MAX_CLIENTS];" in source
	assert "qhandle_t\tscoreMutedShader;" in source
	assert "qhandle_t\tscoreSpeakingShader;" in source


def test_scoreboard_feeders_register_and_return_retail_social_icons() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	mute_block = _block_from_marker(source, "static qboolean CG_IsClientMutedLocally")
	helper_block = _block_from_marker(source, "static qhandle_t CG_FeederSocialHandle")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	image_block = _block_from_marker(source, "static qhandle_t CG_FeederItemImage")

	for expected in (
		'cgs.media.scoreMutedShader = trap_R_RegisterShaderNoMip( "ui/assets/score/muted" );',
		'cgs.media.scoreSpeakingShader = trap_R_RegisterShaderNoMip( "ui/assets/score/speaking" );',
	):
		assert expected in source

	assert "cg.clientMuted[clientNum] = trap_QL_IsClientMuted( ci->identityLow, ci->identityHigh ) ? qtrue : qfalse;" in mute_block
	assert "return cg.clientMuted[clientNum];" in mute_block
	assert "if ( CG_IsClientMutedLocally( clientNum ) ) {" in helper_block
	assert "return cgs.media.scoreMutedShader;" in helper_block
	assert "if ( !CG_ShouldDisplayVoiceIndicator() ) {" in helper_block
	assert "if ( cg.time - speakingState->time > 2500 ) {" in helper_block
	assert "return cgs.media.scoreSpeakingShader;" in helper_block

	assert "return CG_FeederItemTextScoreboard( index, column, handle );" in text_block
	assert "return CG_FeederItemTextTDMFreezeTeamList( team, index, column, handle );" in text_block
	assert "row->socialHandle = CG_FeederSocialHandle( row->clientNum );" in source
	assert "if ( row->socialHandle ) {" in source
	assert "*handle = row->socialHandle;" in source
	assert "*handle = CG_StatusHandle( row->info->teamTask );" in source

	assert "scoreboard icons through the feeder-text handle out-param instead." in source
	assert "return 0;" in image_block


def test_speaking_sidecar_helper_tracks_retail_voice_indicator_state() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	helper_block = _block_from_marker(main_source, "void *CG_SetClientSpeakingState")

	assert "cgs.currentVoiceClient = clientNum;" in helper_block
	assert "cg.voiceTime = cg.time;" in helper_block
	assert "cgs.currentVoiceClient = -1;" in helper_block
	assert "return ci;" in helper_block
	assert "CG_SetClientSpeakingState( clientNum, qtrue );" in servercmds_source


def test_server_chat_and_host_mute_imports_stay_identity_backed() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	client_source = CL_CGAME.read_text(encoding="utf-8")
	server_block = _block_from_marker(servercmds_source, "static qboolean CG_IsServerChatClientMuted")
	is_muted_block = _block_from_marker(client_source, "static int QDECL QL_CG_trap_IsClientMuted")
	toggle_block = _block_from_marker(client_source, "static int QDECL QL_CG_trap_ToggleClientMute")

	assert "cg.clientMuted[clientNum] = trap_QL_IsClientMuted( ci->identityLow, ci->identityHigh ) ? qtrue : qfalse;" in server_block
	assert "return cg.clientMuted[clientNum];" in server_block
	assert "static uint64_t ql_cgame_mutedIdentitySet[MAX_CLIENTS];" in client_source
	assert "static int ql_cgame_mutedIdentityCount = 0;" in client_source
	assert "identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );" in is_muted_block
	assert "return QL_CG_FindMutedIdentityIndex( identity ) >= 0;" in is_muted_block
	assert "index = QL_CG_FindMutedIdentityIndex( identity );" in toggle_block
	assert "ql_cgame_mutedIdentitySet[index] = ql_cgame_mutedIdentitySet[ql_cgame_mutedIdentityCount];" in toggle_block
	assert "ql_cgame_mutedIdentitySet[ql_cgame_mutedIdentityCount++] = identity;" in toggle_block
	assert "ql_cgame_imports[CG_QL_IMPORT_IS_CLIENT_MUTED] = (ql_import_f)QL_CG_trap_IsClientMuted;" in client_source
	assert "ql_cgame_imports[CG_QL_IMPORT_TOGGLE_CLIENT_MUTE] = (ql_import_f)QL_CG_trap_ToggleClientMute;" in client_source
