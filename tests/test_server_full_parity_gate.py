from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from tests._shared import (
	REPO_ROOT,
	contains_all as _contains_all,
	read_json as _read_json,
	section_text_for_id as _section_text_for_id,
	write_json as _write_json,
)

SERVER_FULL_PARITY_GATE_PATH = (
	REPO_ROOT / "artifacts" / "server_validation" / "logs" / "server_full_parity_gate.json"
)
SERVER_RUNTIME_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "server_validation" / "logs" / "server_runtime_evidence_20260410.json"
)
SERVER_PLAN_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "server-full-parity-audit-and-implementation-plan-2026-04-10.md"
)
SERVER_VALIDATION_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "server-validation-and-runtime-evidence-2026-04-10.md"
)
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "server-validation.yml"
BUILD_PIPELINE_PATH = REPO_ROOT / "docs" / "build-pipeline.md"
WINDOWS_NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "windows-native-pipeline.md"
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "IMPLEMENTATION_PLAN.md"
AUDIT_PATH = REPO_ROOT / "AUDIT.md"
RUNTIME_PROBE_PATH = REPO_ROOT / "tools" / "server" / "run_server_runtime_probe.ps1"

SERVER_H_PATH = REPO_ROOT / "src" / "code" / "server" / "server.h"
SV_CLIENT_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_client.c"
SV_GAME_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SV_INIT_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_init.c"
SV_MAIN_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_main.c"
SV_RANKINGS_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_rankings.c"
SV_ZMQ_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_zmq.c"
COMMON_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
PLATFORM_STEAMWORKS_PATH = REPO_ROOT / "src" / "common" / "platform" / "platform_steamworks.c"
PLATFORM_SERVICES_TEST_PATH = REPO_ROOT / "tests" / "test_platform_services.py"
FAKE_VACBAN_TEST_PATH = REPO_ROOT / "tests" / "test_fake_vacban.py"

GAP_ORDER = ("SV-G01", "SV-G02", "SV-G03", "SV-G04", "SV-G05", "SV-G06")

def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")

def _entry(gap_id: str, status: str, summary: str, details: dict[str, Any]) -> dict[str, Any]:
	return {
		"gap_id": gap_id,
		"status": status,
		"summary": summary,
		"details": details,
	}

def _query_field(fields: dict[str, Any], *names: str) -> str:
	for name in names:
		value = fields.get(name)
		if isinstance(value, str) and value:
			return value

	return ""

def _runtime_evidence_is_sufficient(runtime_evidence: dict[str, Any] | None) -> bool:
	if runtime_evidence is None:
		return False

	startup = runtime_evidence["startup"]
	metadata = runtime_evidence["metadata_publication"]
	shutdown = runtime_evidence["shutdown"]
	steam_runtime = runtime_evidence["steam_runtime"]
	zmq_runtime = runtime_evidence["zmq_runtime"]
	fields = metadata["query_response_fields"]

	return (
		runtime_evidence["artifact_version"] == 1
		and runtime_evidence["phase"] == "SV-P7"
		and runtime_evidence["parity_estimate"] == {"before": 97, "after": 100}
		and runtime_evidence["warnings"] == []
		and runtime_evidence["missing_log_markers"] == []
		and runtime_evidence["probe_script"] == "tools/server/run_server_runtime_probe.ps1"
		and startup["common_init_complete"] is True
		and startup["ip_socket_opened"] is True
		and startup["server_init_seen"] is True
		and startup["game_init_seen"] is True
		and startup["qagame_load_seen"] is True
		and metadata["query_response_seen"] is True
		and metadata["query_response_raw"]
		and fields["sv_hostname"] == "SVP7 Probe"
		and fields["mapname"] == "bloodrun"
		and _query_field(fields, "sv_vac", "vac") == "1"
		and _query_field(fields, "sv_serverType", "serverType") == "0"
		and fields["sv_maxclients"] == "8"
		and fields["sv_warmupReadyPercentage"] == "0.51"
		and shutdown["rcon_status_seen"] is True
		and shutdown["quit_command_sent"] is True
		and shutdown["process_exited"] is True
		and shutdown["exit_code"] == 0
		and isinstance(shutdown["server_shutdown_seen"], bool)
		and isinstance(shutdown["shutdown_game_seen"], bool)
		and isinstance(shutdown["sv_running_cleared"], bool)
		and isinstance(steam_runtime["heartbeat_seen"], bool)
		and isinstance(steam_runtime["server_auth_telemetry_seen"], bool)
		and isinstance(steam_runtime["connected_to_steam_servers_seen"], bool)
		and isinstance(steam_runtime["connect_failure_seen"], bool)
		and isinstance(steam_runtime["disconnected_from_steam_servers_seen"], bool)
		and zmq_runtime["enabled_requested"] is True
		and zmq_runtime["rcon_enabled_requested"] is True
		and isinstance(zmq_runtime["transcript_exists"], bool)
		and isinstance(zmq_runtime["rcon_socket_logged"], bool)
		and isinstance(zmq_runtime["pub_socket_logged"], bool)
		and isinstance(zmq_runtime["runtime_disabled_logged"], bool)
		and isinstance(zmq_runtime["runtime_unavailable_logged"], bool)
	)

def _build_server_full_parity_gate_report() -> dict[str, Any]:
	server_plan = _read_text(SERVER_PLAN_PATH)
	server_validation_note = _read_text(SERVER_VALIDATION_NOTE_PATH)
	workflow_text = _read_text(WORKFLOW_PATH)
	build_pipeline = _read_text(BUILD_PIPELINE_PATH)
	windows_native_pipeline = _read_text(WINDOWS_NATIVE_PIPELINE_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	server_h = _read_text(SERVER_H_PATH)
	sv_client = _read_text(SV_CLIENT_PATH)
	sv_game = _read_text(SV_GAME_PATH)
	sv_init = _read_text(SV_INIT_PATH)
	sv_main = _read_text(SV_MAIN_PATH)
	sv_rankings = _read_text(SV_RANKINGS_PATH)
	sv_zmq = _read_text(SV_ZMQ_PATH)
	common = _read_text(COMMON_PATH)
	platform_steamworks = _read_text(PLATFORM_STEAMWORKS_PATH)
	platform_services_tests = _read_text(PLATFORM_SERVICES_TEST_PATH)
	fake_vacban_tests = _read_text(FAKE_VACBAN_TEST_PATH)
	runtime_evidence = _read_json(SERVER_RUNTIME_EVIDENCE_PATH) if SERVER_RUNTIME_EVIDENCE_PATH.exists() else None

	runtime_evidence_sufficient = _runtime_evidence_is_sufficient(runtime_evidence)

	report: dict[str, Any] = {
		"artifact_version": 1,
		"phase": "SV-P7",
		"parity_estimate": {
			"before": 97,
			"after": 100,
		},
		"gap_order": list(GAP_ORDER),
		"tranches": {},
	}

	sv_g01_closed = "**Status:** Closed 2026-04-10" in _section_text_for_id(server_plan, "SV-G01")
	sv_g01_ok = (
		sv_g01_closed
		and "void Com_InitSteamGameServer( void ) {" in common
		and "QL_Steamworks_ServerInit( steamIp" in common
		and "QL_Steamworks_ServerShutdown();" in sv_init
		and "void SV_SteamServerInitCallbacks( void ) {" in sv_client
		and "qboolean QL_Steamworks_RegisterServerCallbacks( const ql_steam_server_callback_bindings_t *bindings ) {" in platform_steamworks
		and "test_server_game_server_wrappers_reconstruct_mapped_server_slots" in platform_services_tests
		and "test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle" in platform_services_tests
		and "test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control" in platform_services_tests
		and "test_fake_vacban_constants_match_hlil" in fake_vacban_tests
		and "test_fake_vacban_telemetry_payload" in fake_vacban_tests
	)
	report["tranches"]["SV-G01"] = _entry(
		"SV-G01",
		"pass" if sv_g01_ok else "fail",
		(
			"The Steam GameServer lifecycle, callback bundle, and auth-session owner remain source-backed and validated."
			if sv_g01_ok
			else "The Steam GameServer lifecycle/callback/auth lane is no longer fully pinned."
		),
		{
			"plan_marks_closed": sv_g01_closed,
			"bootstrap_owner_present": "void Com_InitSteamGameServer( void ) {" in common,
			"shutdown_owner_present": "QL_Steamworks_ServerShutdown();" in sv_init,
			"callback_owner_present": "void SV_SteamServerInitCallbacks( void ) {" in sv_client,
			"platform_callback_registration_present": "qboolean QL_Steamworks_RegisterServerCallbacks( const ql_steam_server_callback_bindings_t *bindings ) {" in platform_steamworks,
			"focused_validation_present": (
				"test_server_game_server_wrappers_reconstruct_mapped_server_slots" in platform_services_tests
				and "test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle" in platform_services_tests
				and "test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control" in platform_services_tests
				and "test_fake_vacban_constants_match_hlil" in fake_vacban_tests
				and "test_fake_vacban_telemetry_payload" in fake_vacban_tests
			),
		},
	)

	sv_g02_closed = "**Status:** Closed 2026-04-10" in _section_text_for_id(server_plan, "SV-G02")
	sv_g02_ok = (
		sv_g02_closed
		and "void Zmq_RegisterCvarsAndInitRcon( void ) {" in sv_zmq
		and "void Zmq_InitStatsPublisher( void ) {" in sv_zmq
		and "void Zmq_PumpRcon( void ) {" in sv_zmq
		and "void Zmq_ShutdownRuntime( void ) {" in sv_zmq
		and 'static void idZMQ_ApplyPasswords( qboolean rconModeChanged, qboolean statsModeChanged ) {' in sv_zmq
		and '#define QL_ZMQ_PASSFILE "zmqpass.txt"' in sv_zmq
		and 'Com_sprintf( line, sizeof( line ), "stats_stats=%s\\n", s_zmq.statsPassword );' in sv_zmq
		and 'Com_sprintf( line, sizeof( line ), "rcon_rcon=%s\\n", s_zmq.rconPassword );' in sv_zmq
		and 'idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "rcon" );' in sv_zmq
		and 'idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "stats" );' in sv_zmq
		and "idZMQ_PumpAuthSocket();" in sv_zmq
		and 'idZMQ_Publish( "MATCH_REPORT", (const char *)report );' in sv_zmq
		and 'Com_Printf( "zmq RCON socket: %s\\n", s_zmq.rconEndpoint );' in sv_zmq
		and 'Com_Printf( "zmq PUB socket: %s\\n", s_zmq.statsEndpoint );' in sv_zmq
		and "test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners" in platform_services_tests
	)
	report["tranches"]["SV-G02"] = _entry(
		"SV-G02",
		"pass" if sv_g02_ok else "fail",
		(
			"The retained server-owned idZMQ runtime/publication lane remains reconstructed and test-pinned."
			if sv_g02_ok
			else "The retained idZMQ runtime/publication lane is incomplete."
		),
		{
			"plan_marks_closed": sv_g02_closed,
			"runtime_register_owner_present": "void Zmq_RegisterCvarsAndInitRcon( void ) {" in sv_zmq,
			"stats_publisher_owner_present": "void Zmq_InitStatsPublisher( void ) {" in sv_zmq,
			"rcon_pump_owner_present": "void Zmq_PumpRcon( void ) {" in sv_zmq,
			"runtime_shutdown_owner_present": "void Zmq_ShutdownRuntime( void ) {" in sv_zmq,
			"password_apply_owner_present": (
				'static void idZMQ_ApplyPasswords( qboolean rconModeChanged, qboolean statsModeChanged ) {' in sv_zmq
				and '#define QL_ZMQ_PASSFILE "zmqpass.txt"' in sv_zmq
				and 'Com_sprintf( line, sizeof( line ), "stats_stats=%s\\n", s_zmq.statsPassword );' in sv_zmq
				and 'Com_sprintf( line, sizeof( line ), "rcon_rcon=%s\\n", s_zmq.rconPassword );' in sv_zmq
			),
			"zap_domain_wiring_present": (
				'idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "rcon" );' in sv_zmq
				and 'idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "stats" );' in sv_zmq
			),
			"auth_pump_present": "idZMQ_PumpAuthSocket();" in sv_zmq,
			"typed_publication_present": 'idZMQ_Publish( "MATCH_REPORT", (const char *)report );' in sv_zmq,
			"focused_validation_present": "test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners" in platform_services_tests,
		},
	)

	sv_g03_closed = "**Status:** Closed 2026-04-10" in _section_text_for_id(server_plan, "SV-G03")
	sv_g03_ok = (
		sv_g03_closed
		and "void SV_SteamStats_AddFieldValue( int clientNum, int statIndex, int delta ) {" in sv_client
		and "void SV_SteamStats_UnlockAchievement( int clientNum, int achievementId ) {" in sv_client
		and "qboolean SV_SteamStats_HasAchievement( int clientNum, int achievementId ) {" in sv_client
		and "SV_ClientAddSteamStat" in sv_game
		and "SV_ClientUnlockSteamAchievement" in sv_game
		and "SV_ClientHasSteamAchievement" in sv_game
		and "qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId ) {" in platform_steamworks
		and "qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId ) {" in platform_steamworks
		and "test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge" in platform_services_tests
	)
	report["tranches"]["SV-G03"] = _entry(
		"SV-G03",
		"pass" if sv_g03_ok else "fail",
		(
			"The qagame-facing Steam stat and achievement lane remains owned by the server host."
			if sv_g03_ok
			else "The qagame-facing Steam stat and achievement lane is incomplete."
		),
		{
			"plan_marks_closed": sv_g03_closed,
			"stat_owner_present": "void SV_SteamStats_AddFieldValue( int clientNum, int statIndex, int delta ) {" in sv_client,
			"achievement_owner_present": (
				"void SV_SteamStats_UnlockAchievement( int clientNum, int achievementId ) {" in sv_client
				and "qboolean SV_SteamStats_HasAchievement( int clientNum, int achievementId ) {" in sv_client
			),
			"qagame_bridge_present": (
				"SV_ClientAddSteamStat" in sv_game
				and "SV_ClientUnlockSteamAchievement" in sv_game
				and "SV_ClientHasSteamAchievement" in sv_game
			),
			"platform_wrapper_present": (
				"qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId ) {" in platform_steamworks
				and "qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId ) {" in platform_steamworks
			),
			"focused_validation_present": "test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge" in platform_services_tests,
		},
	)

	sv_g04_closed = "**Status:** Closed 2026-04-10" in _section_text_for_id(server_plan, "SV-G04")
	sv_g04_ok = (
		sv_g04_closed
		and 'sv_enableRankings = Cvar_Get ("sv_enableRankings", "0",' in sv_init
		and 'sv_rankingsActive = Cvar_Get ("sv_rankingsActive", "0",' in sv_init
		and 'sv_leagueName = Cvar_Get ("sv_leagueName", "",' in sv_init
		and "void SV_RankBegin( char *gamekey )" in sv_rankings
		and "test_server_rankings_policy_lane_stays_explicit_and_per_server" in platform_services_tests
	)
	report["tranches"]["SV-G04"] = _entry(
		"SV-G04",
		"pass" if sv_g04_ok else "fail",
		(
			"The rankings lane remains explicitly source-backed and default-disabled by policy rather than silently stubbed."
			if sv_g04_ok
			else "The rankings compatibility lane is incomplete."
		),
		{
			"plan_marks_closed": sv_g04_closed,
			"compatibility_cvars_present": (
				'sv_enableRankings = Cvar_Get ("sv_enableRankings", "0",' in sv_init
				and 'sv_rankingsActive = Cvar_Get ("sv_rankingsActive", "0",' in sv_init
				and 'sv_leagueName = Cvar_Get ("sv_leagueName", "",' in sv_init
			),
			"rank_begin_owner_present": "void SV_RankBegin( char *gamekey )" in sv_rankings,
			"focused_validation_present": "test_server_rankings_policy_lane_stays_explicit_and_per_server" in platform_services_tests,
		},
	)

	sv_g05_closed = "**Status:** Closed 2026-04-10" in _section_text_for_id(server_plan, "SV-G05")
	sv_g05_ok = (
		sv_g05_closed
		and 'sv_floodProtect = Cvar_Get ("sv_floodProtect", "10", CVAR_ARCHIVE );' in sv_init
		and 'sv_serverType = Cvar_Get ("sv_serverType", "0", CVAR_ARCHIVE );' in sv_init
		and 'sv_ammoPack = Cvar_Get ("g_ammoPack", "1", CVAR_LATCH );' in sv_init
		and 'sv_idleRestart = Cvar_Get ("sv_idleRestart", "1", 0 );' in sv_init
		and 'sv_idleExit = Cvar_Get ("sv_idleExit", "120", 0 );' in sv_init
		and 'sv_errorExit = Cvar_Get ("sv_errorExit", "1", 0 );' in sv_init
		and 'sv_quitOnEmpty = Cvar_Get ("sv_quitOnEmpty", "0", 0 );' in sv_init
		and 'sv_quitOnExitLevel = Cvar_Get ("sv_quitOnExitLevel", "0", 0 );' in sv_init
		and 'sv_fps = Cvar_Get ("sv_fps", "40", CVAR_ROM );' in sv_init
		and 'sv_timeout = Cvar_Get ("sv_timeout", "40", CVAR_TEMP );' in sv_init
		and 'sv_padPackets = Cvar_GetBounded( "sv_padPackets", "0", "0", "0", CVAR_VM_CREATED );' in sv_init
		and 'sv_cylinderScale = Cvar_Get ("sv_cylinderScale", "1.1f", 0 );' in sv_init
		and "qboolean SV_ShouldErrorExit( errorParm_t code ) {" in sv_main
		and "qboolean SV_CheckIdleServerExit( int currentTime ) {" in sv_main
		and "void SV_CheckTimeouts( void ) {" in sv_main
		and 'Com_Printf( "server has been empty for %d seconds, quit\\n", sv_quitOnEmpty->integer );' in sv_main
		and 'if ( sv_idleRestart && sv_idleRestart->integer && svs.time > 0x5265c00 && SV_CountActiveHumanClients() == 0 ) {' in sv_main
		and 'SV_Shutdown( "Restarting idle server" );' in sv_main
		and 'Cbuf_AddText( "vstr nextmap\\n" );' in sv_main
		and "static char *SV_GetGameEntityString( void ) {" in sv_game
		and "void Com_InitSteamGameServer( void ) {" in common
		and "test_server_control_plane_cvars_restore_retail_runtime_owners" in platform_services_tests
	)
	report["tranches"]["SV-G05"] = _entry(
		"SV-G05",
		"pass" if sv_g05_ok else "fail",
		(
			"The remaining retail control-plane cvars and owners remain source-backed and validated."
			if sv_g05_ok
			else "The remaining retail control-plane cvar/owner lane is incomplete."
		),
		{
			"plan_marks_closed": sv_g05_closed,
			"control_plane_cvars_present": (
				'sv_floodProtect = Cvar_Get ("sv_floodProtect", "10", CVAR_ARCHIVE );' in sv_init
				and 'sv_serverType = Cvar_Get ("sv_serverType", "0", CVAR_ARCHIVE );' in sv_init
				and 'sv_ammoPack = Cvar_Get ("g_ammoPack", "1", CVAR_LATCH );' in sv_init
				and 'sv_idleRestart = Cvar_Get ("sv_idleRestart", "1", 0 );' in sv_init
				and 'sv_idleExit = Cvar_Get ("sv_idleExit", "120", 0 );' in sv_init
				and 'sv_errorExit = Cvar_Get ("sv_errorExit", "1", 0 );' in sv_init
				and 'sv_quitOnEmpty = Cvar_Get ("sv_quitOnEmpty", "0", 0 );' in sv_init
				and 'sv_quitOnExitLevel = Cvar_Get ("sv_quitOnExitLevel", "0", 0 );' in sv_init
				and 'sv_fps = Cvar_Get ("sv_fps", "40", CVAR_ROM );' in sv_init
				and 'sv_timeout = Cvar_Get ("sv_timeout", "40", CVAR_TEMP );' in sv_init
				and 'sv_padPackets = Cvar_GetBounded( "sv_padPackets", "0", "0", "0", CVAR_VM_CREATED );' in sv_init
				and 'sv_cylinderScale = Cvar_Get ("sv_cylinderScale", "1.1f", 0 );' in sv_init
			),
			"shutdown_policy_owner_present": (
				"qboolean SV_ShouldErrorExit( errorParm_t code ) {" in sv_main
				and "qboolean SV_CheckIdleServerExit( int currentTime ) {" in sv_main
			),
			"empty_server_policy_present": (
				"void SV_CheckTimeouts( void ) {" in sv_main
				and 'Com_Printf( "server has been empty for %d seconds, quit\\n", sv_quitOnEmpty->integer );' in sv_main
			),
			"idle_restart_owner_present": (
				'if ( sv_idleRestart && sv_idleRestart->integer && svs.time > 0x5265c00 && SV_CountActiveHumanClients() == 0 ) {' in sv_main
				and 'SV_Shutdown( "Restarting idle server" );' in sv_main
				and 'Cbuf_AddText( "vstr nextmap\\n" );' in sv_main
			),
			"alt_entity_owner_present": "static char *SV_GetGameEntityString( void ) {" in sv_game,
			"focused_validation_present": "test_server_control_plane_cvars_restore_retail_runtime_owners" in platform_services_tests,
		},
	)

	sv_g06_closed = "**Status:** Closed on 2026-04-10" in _section_text_for_id(server_plan, "SV-G06")
	sv_g06_ok = (
		sv_g06_closed
		and RUNTIME_PROBE_PATH.exists()
		and runtime_evidence_sufficient
		and SERVER_VALIDATION_NOTE_PATH.exists()
		and _contains_all(
			server_validation_note,
			"server_runtime_evidence_20260410.json",
			"server_full_parity_gate.json",
			"`SV-P7` is now considered complete.",
			"`SV-G06` is now considered closed.",
		)
		and "## SV-P7 - Add a unified server parity gate and dedicated runtime evidence lane [COMPLETED 2026-04-10]" in server_plan
		and "tests/test_server_full_parity_gate.py" in workflow_text
		and "tests/test_platform_services.py" in workflow_text
		and "tools/server/run_server_runtime_probe.ps1" in workflow_text
		and "server_full_parity_gate.json" in build_pipeline
		and "server_runtime_evidence_20260410.json" in build_pipeline
		and "tools/server/run_server_runtime_probe.ps1" in build_pipeline
		and "server_full_parity_gate.json" in windows_native_pipeline
		and "server_runtime_evidence_20260410.json" in windows_native_pipeline
		and "tools/server/run_server_runtime_probe.ps1" in windows_native_pipeline
		and "### Task 100: Server SV-P7 parity gate and dedicated runtime-evidence closure [COMPLETED]" in implementation_plan
		and "Parity estimate: **before 97% -> after 100%**" in implementation_plan
		and _contains_all(
			audit,
			"The refreshed strict `server` estimate is now explicitly tracked as **100%**.",
			"`SV-P7` is now complete.",
			"No open gap remains in the audited server register.",
		)
	)
	report["tranches"]["SV-G06"] = _entry(
		"SV-G06",
		"pass" if sv_g06_ok else "fail",
		(
			"The server now has a dedicated parity gate, a tracked dedicated runtime-evidence bundle, and repo-level workflow/ledger wiring."
			if sv_g06_ok
			else "The dedicated server parity gate/runtime-evidence lane is incomplete."
		),
		{
			"plan_marks_closed": sv_g06_closed,
			"runtime_probe_present": RUNTIME_PROBE_PATH.exists(),
			"runtime_evidence_present": SERVER_RUNTIME_EVIDENCE_PATH.exists(),
			"runtime_evidence_sufficient": runtime_evidence_sufficient,
			"validation_note_present": SERVER_VALIDATION_NOTE_PATH.exists(),
			"workflow_references_gate": "tests/test_server_full_parity_gate.py" in workflow_text,
			"workflow_mentions_runtime_probe": "tools/server/run_server_runtime_probe.ps1" in workflow_text,
			"build_pipeline_mentions_gate": "server_full_parity_gate.json" in build_pipeline,
			"windows_pipeline_mentions_runtime_artifact": "server_runtime_evidence_20260410.json" in windows_native_pipeline,
			"implementation_plan_marks_sv_p7_completed": "### Task 100: Server SV-P7 parity gate and dedicated runtime-evidence closure [COMPLETED]" in implementation_plan,
			"audit_marks_server_full_closure": _contains_all(
				audit,
				"The refreshed strict `server` estimate is now explicitly tracked as **100%**.",
				"`SV-P7` is now complete.",
				"No open gap remains in the audited server register.",
			),
		},
	)

	non_passing_gap_ids = [
		gap_id
		for gap_id in GAP_ORDER
		if report["tranches"][gap_id]["status"] != "pass"
	]
	report["overall_status"] = "pass" if not non_passing_gap_ids else "fail"
	report["non_passing_gap_ids"] = non_passing_gap_ids
	report["summary"] = {
		"passing_count": sum(1 for gap_id in GAP_ORDER if report["tranches"][gap_id]["status"] == "pass"),
		"blocked_count": sum(1 for gap_id in GAP_ORDER if report["tranches"][gap_id]["status"] == "blocked"),
		"failing_count": sum(1 for gap_id in GAP_ORDER if report["tranches"][gap_id]["status"] == "fail"),
	}
	return report

def test_server_runtime_evidence_artifact_is_tracked_and_clean() -> None:
	runtime_evidence = _read_json(SERVER_RUNTIME_EVIDENCE_PATH)

	assert runtime_evidence["artifact_version"] == 1
	assert runtime_evidence["phase"] == "SV-P7"
	assert runtime_evidence["parity_estimate"] == {"before": 97, "after": 100}
	assert runtime_evidence["warnings"] == []
	assert runtime_evidence["missing_log_markers"] == []
	assert runtime_evidence["startup"]["common_init_complete"] is True
	assert runtime_evidence["startup"]["ip_socket_opened"] is True
	assert runtime_evidence["startup"]["server_init_seen"] is True
	assert runtime_evidence["startup"]["game_init_seen"] is True
	assert runtime_evidence["startup"]["qagame_load_seen"] is True
	assert runtime_evidence["metadata_publication"]["query_response_seen"] is True
	assert runtime_evidence["metadata_publication"]["query_response_fields"]["sv_hostname"] == "SVP7 Probe"
	assert runtime_evidence["metadata_publication"]["query_response_fields"]["mapname"] == "bloodrun"
	assert _query_field(runtime_evidence["metadata_publication"]["query_response_fields"], "sv_vac", "vac") == "1"
	assert _query_field(runtime_evidence["metadata_publication"]["query_response_fields"], "sv_serverType", "serverType") == "0"
	assert runtime_evidence["shutdown"]["rcon_status_seen"] is True
	assert runtime_evidence["shutdown"]["quit_command_sent"] is True
	assert runtime_evidence["shutdown"]["process_exited"] is True
	assert runtime_evidence["shutdown"]["exit_code"] == 0
	assert isinstance(runtime_evidence["shutdown"]["server_shutdown_seen"], bool)
	assert isinstance(runtime_evidence["shutdown"]["shutdown_game_seen"], bool)
	assert isinstance(runtime_evidence["shutdown"]["sv_running_cleared"], bool)
	assert runtime_evidence["zmq_runtime"]["enabled_requested"] is True
	assert runtime_evidence["zmq_runtime"]["rcon_enabled_requested"] is True
	assert _runtime_evidence_is_sufficient(runtime_evidence)

def test_server_full_parity_gate_writes_status_artifact() -> None:
	report = _build_server_full_parity_gate_report()
	_write_json(SERVER_FULL_PARITY_GATE_PATH, report)

	assert SERVER_FULL_PARITY_GATE_PATH.exists()
	assert _read_json(SERVER_FULL_PARITY_GATE_PATH) == report
	assert report["artifact_version"] == 1
	assert report["phase"] == "SV-P7"
	assert report["gap_order"] == list(GAP_ORDER)
	assert set(report["tranches"]) == set(GAP_ORDER)
	assert report["overall_status"] == "pass"
	assert report["non_passing_gap_ids"] == []
	assert report["summary"] == {
		"passing_count": 6,
		"blocked_count": 0,
		"failing_count": 0,
	}

	for gap_id in GAP_ORDER:
		entry = report["tranches"][gap_id]
		assert entry["gap_id"] == gap_id
		assert entry["status"] in {"pass", "fail", "blocked"}
		assert entry["summary"]

def test_server_full_parity_gate_release_mode() -> None:
	if os.environ.get("SERVER_FULL_PARITY_GATE_ENFORCE") != "1":
		pytest.skip("Set SERVER_FULL_PARITY_GATE_ENFORCE=1 to require a full server parity pass.")

	report = _build_server_full_parity_gate_report()
	_write_json(SERVER_FULL_PARITY_GATE_PATH, report)
	assert report["overall_status"] == "pass", (
		"Server full parity gate failed for "
		+ ", ".join(report["non_passing_gap_ids"])
	)
