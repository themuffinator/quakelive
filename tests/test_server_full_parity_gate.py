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
		and "QL_Steamworks_ServerInitWithVersion( steamIp" in common
		and "QL_Steamworks_ServerShutdown();" in sv_init
		and "void SV_SteamServerInitCallbacks( void ) {" in sv_client
		and "qboolean QL_Steamworks_RegisterServerCallbacks( const ql_steam_server_callback_bindings_t *bindings ) {" in platform_steamworks
		and "if ( !com_sv_running || !com_sv_running->integer ) {" in sv_main
		and "if ( svs.clients && sv_maxclients ) {" in sv_main
		and "if ( !sv.gameClients || sv.gameClientSize <= 0 ) {" in sv_main
		and "test_server_game_server_wrappers_reconstruct_mapped_server_slots" in platform_services_tests
		and "test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle" in platform_services_tests
		and "test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control" in platform_services_tests
		and "test_steam_gameserver_published_state_launch_callback_is_startup_safe" in platform_services_tests
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
			"server_frame_startup_guard_present": (
				"if ( !QL_Steamworks_ServerIsInitialised() ) {" in sv_main
				and "if ( !com_sv_running || !com_sv_running->integer ) {" in sv_main
				and "QL_Steamworks_RunServerCallbacks();" in sv_main
				and sv_main.index("if ( !QL_Steamworks_ServerIsInitialised() ) {") < sv_main.index(
					"if ( !com_sv_running || !com_sv_running->integer ) {"
				)
				and sv_main.index("if ( !com_sv_running || !com_sv_running->integer ) {") < sv_main.index(
					"QL_Steamworks_RunServerCallbacks();"
				)
			),
			"published_state_startup_guard_present": (
				"if ( svs.clients && sv_maxclients ) {" in sv_main
				and "for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {" in sv_main
				and "if ( !sv.gameClients || sv.gameClientSize <= 0 ) {" in sv_main
				and "playerState = SV_GameClientNum( i );" in sv_main
			),
			"focused_validation_present": (
				"test_server_game_server_wrappers_reconstruct_mapped_server_slots" in platform_services_tests
				and "test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle" in platform_services_tests
				and "test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control" in platform_services_tests
				and "test_steam_gameserver_published_state_launch_callback_is_startup_safe" in platform_services_tests
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
		and "static void idZMQ_ApplyPasswords( void ) {" in sv_zmq
		and "if ( !s_zmq.authActorReady ) {" in sv_zmq
		and '#define QL_ZMQ_RUNTIME_UNAVAILABLE_FORMAT "ZMQ runtime unavailable: %s\\n"' in sv_zmq
		and '#define QL_ZMQ_RUNTIME_DISABLED_MESSAGE "ZMQ runtime disabled by build policy (QL_BUILD_ONLINE_SERVICES=0); keeping retained fallback paths.\\n"' in sv_zmq
		and '#define QL_ZMQ_RUNTIME_LOAD_FAILED_REASON "unable to load libzmq"' in sv_zmq
		and '#define QL_ZMQ_RUNTIME_EXPORTS_MISSING_REASON "libzmq is missing required exports"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_CTX_NEW "zmq_ctx_new"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_CTX_TERM "zmq_ctx_term"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_SOCKET "zmq_socket"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_CLOSE "zmq_close"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_BIND "zmq_bind"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_SEND "zmq_send"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_RECV "zmq_recv"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_POLL "zmq_poll"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_ERRNO "zmq_errno"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_STRERROR "zmq_strerror"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_SETSOCKOPT "zmq_setsockopt"' in sv_zmq
		and '#define QL_ZMQ_EXPORT_GETSOCKOPT "zmq_getsockopt"' in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_new, QL_ZMQ_EXPORT_CTX_NEW )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_term, QL_ZMQ_EXPORT_CTX_TERM )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_socket, QL_ZMQ_EXPORT_SOCKET )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_close, QL_ZMQ_EXPORT_CLOSE )" in sv_zmq
		and "#define QL_ZMQ_CONTEXT_SLOT_EMPTY NULL" in sv_zmq
		and "s_zmq.context = QL_ZMQ_CONTEXT_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.context = NULL;" not in sv_zmq
		and "#define QL_ZMQ_LIBRARY_SLOT_EMPTY NULL" in sv_zmq
		and "s_zmq.library = QL_ZMQ_LIBRARY_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.library = NULL;" not in sv_zmq
		and "#define QL_ZMQ_SYMBOL_SLOT_EMPTY NULL" in sv_zmq
		and "s_zmq.zmq_ctx_new = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.zmq_strerror = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.zmq_ctx_new = NULL;" not in sv_zmq
		and "#define QL_ZMQ_RCON_POLL_SLOT_EMPTY NULL" in sv_zmq
		and "s_zmq.rconPollSocket = QL_ZMQ_RCON_POLL_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.rconPollSocket = NULL;" not in sv_zmq
		and "#define QL_ZMQ_SOCKET_SLOT_EMPTY NULL" in sv_zmq
		and "*socketPointer = QL_ZMQ_SOCKET_SLOT_EMPTY;" in sv_zmq
		and "*socketPointer = NULL;" not in sv_zmq
		and "idZMQ_CloseSocket( &socket );" in sv_zmq
		and "s_zmq.zmq_close( socket );" not in sv_zmq
		and sv_zmq.count("s_zmq.zmq_close(") == 1
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_bind, QL_ZMQ_EXPORT_BIND )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_send, QL_ZMQ_EXPORT_SEND )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_recv, QL_ZMQ_EXPORT_RECV )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_poll, QL_ZMQ_EXPORT_POLL )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_errno, QL_ZMQ_EXPORT_ERRNO )" in sv_zmq
		and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_strerror, QL_ZMQ_EXPORT_STRERROR )" in sv_zmq
		and "idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_setsockopt, QL_ZMQ_EXPORT_SETSOCKOPT );" in sv_zmq
		and "idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_getsockopt, QL_ZMQ_EXPORT_GETSOCKOPT );" in sv_zmq
		and "Com_Printf( QL_ZMQ_RUNTIME_DISABLED_MESSAGE );" in sv_zmq
		and "Com_Printf( QL_ZMQ_RUNTIME_UNAVAILABLE_FORMAT, reason );" in sv_zmq
		and "idZMQ_LogRuntimeUnavailable( QL_ZMQ_RUNTIME_LOAD_FAILED_REASON );" in sv_zmq
		and "idZMQ_LogRuntimeUnavailable( QL_ZMQ_RUNTIME_EXPORTS_MISSING_REASON );" in sv_zmq
		and '#define QL_ZMQ_PASSFILE "zmqpass.txt"' in sv_zmq
		and '#define QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT "Failed to open %s\\n"' in sv_zmq
		and '#define QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT "stats_stats=%s\\n"' in sv_zmq
		and '#define QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT "rcon_rcon=%s\\n"' in sv_zmq
		and "#define QL_ZMQ_PASSFILE_RECORD_SLACK 32" in sv_zmq
		and "#define QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE ( MAX_STRING_CHARS + QL_ZMQ_PASSFILE_RECORD_SLACK )" in sv_zmq
		and "char line[QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE];" in sv_zmq
		and "char line[MAX_STRING_CHARS + 32];" not in sv_zmq
		and '#define QL_ZMQ_AUTH_KEY_FORMAT "%s_%s"' in sv_zmq
		and "#define QL_ZMQ_ENDPOINT_EMPTY QL_ZMQ_STRING_TERMINATOR" in sv_zmq
		and "s_zmq.rconEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;" in sv_zmq
		and "s_zmq.statsEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;" in sv_zmq
		and "s_zmq.rconEndpoint[0] = '\\0';" not in sv_zmq
		and "s_zmq.statsEndpoint[0] = '\\0';" not in sv_zmq
		and "Com_Printf( QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT, QL_ZMQ_PASSFILE );" in sv_zmq
		and "Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT, s_zmq.statsPassword );" in sv_zmq
		and "Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT, s_zmq.rconPassword );" in sv_zmq
		and '#define QL_ZMQ_DOMAIN_RCON "rcon"' in sv_zmq
		and '#define QL_ZMQ_DOMAIN_STATS "stats"' in sv_zmq
		and '#define QL_ZMQ_AUTH_EMPTY_FRAME ""' in sv_zmq
		and "#define QL_ZMQ_AUTH_EMPTY_USER_ID QL_ZMQ_AUTH_EMPTY_FRAME" in sv_zmq
		and "#define QL_ZMQ_AUTH_EMPTY_CREDENTIAL QL_ZMQ_AUTH_EMPTY_FRAME" in sv_zmq
		and "idZMQ_SendAuthFrame( s_zmq.authSocket, QL_ZMQ_AUTH_EMPTY_FRAME, qfalse );" in sv_zmq
		and "userId = QL_ZMQ_AUTH_EMPTY_USER_ID;" in sv_zmq
		and "*userId = QL_ZMQ_AUTH_EMPTY_USER_ID;" in sv_zmq
		and "#define QL_ZMQ_ZAP_VERSION_BUFFER_SIZE 16" in sv_zmq
		and "#define QL_ZMQ_ZAP_REQUEST_ID_BUFFER_SIZE 64" in sv_zmq
		and "#define QL_ZMQ_ZAP_DOMAIN_BUFFER_SIZE 64" in sv_zmq
		and "#define QL_ZMQ_ZAP_ADDRESS_BUFFER_SIZE 128" in sv_zmq
		and "#define QL_ZMQ_ZAP_IDENTITY_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY" in sv_zmq
		and "#define QL_ZMQ_ZAP_MECHANISM_BUFFER_SIZE 16" in sv_zmq
		and "#define QL_ZMQ_ZAP_USERNAME_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY" in sv_zmq
		and "#define QL_ZMQ_ZAP_PASSWORD_BUFFER_SIZE MAX_STRING_CHARS" in sv_zmq
		and "#define QL_ZMQ_ZAP_EMPTY_FIELD QL_ZMQ_STRING_TERMINATOR" in sv_zmq
		and "char version[QL_ZMQ_ZAP_VERSION_BUFFER_SIZE];" in sv_zmq
		and "char requestId[QL_ZMQ_ZAP_REQUEST_ID_BUFFER_SIZE];" in sv_zmq
		and "char domain[QL_ZMQ_ZAP_DOMAIN_BUFFER_SIZE];" in sv_zmq
		and "char address[QL_ZMQ_ZAP_ADDRESS_BUFFER_SIZE];" in sv_zmq
		and "char identity[QL_ZMQ_ZAP_IDENTITY_BUFFER_SIZE];" in sv_zmq
		and "char mechanism[QL_ZMQ_ZAP_MECHANISM_BUFFER_SIZE];" in sv_zmq
		and "char username[QL_ZMQ_ZAP_USERNAME_BUFFER_SIZE];" in sv_zmq
		and "char password[QL_ZMQ_ZAP_PASSWORD_BUFFER_SIZE];" in sv_zmq
		and "requestId[0] = QL_ZMQ_ZAP_EMPTY_FIELD;" in sv_zmq
		and '#define QL_ZMQ_DRAIN_SCRATCH_SIZE MAX_STRING_CHARS' in sv_zmq
		and "#define QL_ZMQ_STRING_TERMINATOR_LENGTH 1" in sv_zmq
		and "#define QL_ZMQ_STRING_TERMINATOR '\\0'" in sv_zmq
		and "#define QL_ZMQ_RCVMORE_NONE 0" in sv_zmq
		and "#define QL_ZMQ_GETSOCKOPT_SUCCESS 0" in sv_zmq
		and "#define QL_ZMQ_FRAME_MORE qtrue" in sv_zmq
		and "#define QL_ZMQ_FRAME_NO_MORE qfalse" in sv_zmq
		and "length = s_zmq.zmq_recv( socket, buffer, bufferSize > 0 ? bufferSize - QL_ZMQ_STRING_TERMINATOR_LENGTH : 0, QL_ZMQ_DONTWAIT );" in sv_zmq
		and "*more = QL_ZMQ_FRAME_NO_MORE;" in sv_zmq
		and "*more = QL_ZMQ_FRAME_MORE;" in sv_zmq
		and "more = QL_ZMQ_FRAME_NO_MORE;" in sv_zmq
		and "s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == QL_ZMQ_GETSOCKOPT_SUCCESS && moreValue != QL_ZMQ_RCVMORE_NONE" in sv_zmq
		and "s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == 0 && moreValue" not in sv_zmq
		and "*more = qfalse;" not in sv_zmq
		and "*more = qtrue;" not in sv_zmq
		and "char scratch[QL_ZMQ_DRAIN_SCRATCH_SIZE];" in sv_zmq
		and "#define QL_ZMQ_SOCKET_OPTION_DISABLED 0" in sv_zmq
		and "#define QL_ZMQ_SOCKET_OPTION_ENABLED 1" in sv_zmq
		and "#define QL_ZMQ_SOCKET_OPTION_INT_SIZE sizeof( int )" in sv_zmq
		and "s_zmq.zmq_setsockopt( socket, option, &value, QL_ZMQ_SOCKET_OPTION_INT_SIZE );" in sv_zmq
		and "s_zmq.zmq_setsockopt( socket, option, &value, sizeof( value ) );" not in sv_zmq
		and "#define QL_ZMQ_SOCKET_OPTION_STRING_SIZE( value ) strlen( value )" in sv_zmq
		and "s_zmq.zmq_setsockopt( socket, option, value, QL_ZMQ_SOCKET_OPTION_STRING_SIZE( value ) );" in sv_zmq
		and "s_zmq.zmq_setsockopt( socket, option, value, strlen( value ) );" not in sv_zmq
		and "idZMQ_TrySetSocketInt( socket, QL_ZMQ_ROUTER_MANDATORY, QL_ZMQ_SOCKET_OPTION_ENABLED );" in sv_zmq
		and "idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.rconPassword[0] ? QL_ZMQ_SOCKET_OPTION_ENABLED : QL_ZMQ_SOCKET_OPTION_DISABLED );" in sv_zmq
		and "idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.statsPassword[0] ? QL_ZMQ_SOCKET_OPTION_ENABLED : QL_ZMQ_SOCKET_OPTION_DISABLED );" in sv_zmq
		and "#define QL_ZMQ_NO_FLAGS 0" in sv_zmq
		and "#define QL_ZMQ_POLL_FD_NONE 0" in sv_zmq
		and "#define QL_ZMQ_POLL_REVENTS_NONE 0" in sv_zmq
		and "#define QL_ZMQ_SINGLE_POLL_ITEM 1" in sv_zmq
		and "#define QL_ZMQ_POLL_TIMEOUT_IMMEDIATE 0" in sv_zmq
		and "#define QL_ZMQ_POLL_READY_MIN 1" in sv_zmq
		and "#define QL_ZMQ_BIND_SUCCESS 0" in sv_zmq
		and "#define QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY" in sv_zmq
		and "#define QL_ZMQ_RCON_COMMAND_BUFFER_SIZE MAX_STRING_CHARS" in sv_zmq
		and "#define QL_ZMQ_FRAME_READ_SUCCESS_MIN 0" in sv_zmq
		and "#define QL_ZMQ_RCON_MIN_IDENTITY_LENGTH 1" in sv_zmq
		and "#define QL_ZMQ_RCON_MIN_COMMAND_LENGTH 1" in sv_zmq
		and "#define QL_ZMQ_RCON_PEER_COUNT_EMPTY 0" in sv_zmq
		and "char identity[QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE];" in sv_zmq
		and "char command[QL_ZMQ_RCON_COMMAND_BUFFER_SIZE];" in sv_zmq
		and "commandLength >= QL_ZMQ_FRAME_READ_SUCCESS_MIN" in sv_zmq
		and "identityLength < QL_ZMQ_RCON_MIN_IDENTITY_LENGTH" in sv_zmq
		and "commandLength < QL_ZMQ_RCON_MIN_COMMAND_LENGTH" in sv_zmq
		and "if ( s_zmq.rconPeerCount > QL_ZMQ_RCON_PEER_COUNT_EMPTY ) {" in sv_zmq
		and "s_zmq.rconPeerCount = QL_ZMQ_RCON_PEER_COUNT_EMPTY;" in sv_zmq
		and "s_zmq.rconPeerCount > 0" not in sv_zmq
		and "s_zmq.rconPeerCount = 0;" not in sv_zmq
		and "commandLength >= 0" not in sv_zmq
		and "identityLength <= 0" not in sv_zmq
		and "commandLength <= 0" not in sv_zmq
		and "flags = more ? QL_ZMQ_SNDMORE : QL_ZMQ_NO_FLAGS;" in sv_zmq
		and "s_zmq.zmq_send( s_zmq.pubSocket, message, strlen( message ), QL_ZMQ_NO_FLAGS );" in sv_zmq
		and "#define QL_ZMQ_SEND_DONTWAIT QL_ZMQ_DONTWAIT" in sv_zmq
		and "#define QL_ZMQ_SEND_MORE_DONTWAIT ( QL_ZMQ_SNDMORE | QL_ZMQ_DONTWAIT )" in sv_zmq
		and "#define QL_ZMQ_SEND_SUCCESS_MIN 0" in sv_zmq
		and "idZMQ_SendAuthFrame( s_zmq.authSocket, version, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
		and "s_zmq.zmq_send( s_zmq.rconSocket, peer->identity, peer->identityLength, QL_ZMQ_SEND_MORE_DONTWAIT ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
		and "s_zmq.zmq_send( s_zmq.rconSocket, payload, strlen( payload ), QL_ZMQ_SEND_DONTWAIT );" in sv_zmq
		and "QL_ZMQ_SEND_MORE_DONTWAIT ) < 0" not in sv_zmq
		and "s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE )" in sv_zmq
		and "while ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) >= QL_ZMQ_POLL_READY_MIN && ( item.revents & QL_ZMQ_POLLIN ) ) {" in sv_zmq
		and "if ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) < QL_ZMQ_POLL_READY_MIN || !( item.revents & QL_ZMQ_POLLIN ) ) {" in sv_zmq
		and "QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) > 0" not in sv_zmq
		and "QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) <= 0" not in sv_zmq
		and "item.fd = QL_ZMQ_POLL_FD_NONE;" in sv_zmq
		and "item.revents = QL_ZMQ_POLL_REVENTS_NONE;" in sv_zmq
		and "item.fd = 0;" not in sv_zmq
		and "item.revents = 0;" not in sv_zmq
		and "idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, QL_ZMQ_DOMAIN_RCON );" in sv_zmq
		and "idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, QL_ZMQ_DOMAIN_STATS );" in sv_zmq
		and '#define QL_ZMQ_DEFAULT_NET_PORT_FORMAT "%i"' in sv_zmq
		and "#define QL_ZMQ_CVAR_INIT_FLAGS CVAR_INIT" in sv_zmq
		and "#define QL_ZMQ_CVAR_PASSWORD_FLAGS CVAR_ARCHIVE" in sv_zmq
		and "#define QL_ZMQ_CVAR_NET_FALLBACK_FLAGS CVAR_LATCH" in sv_zmq
		and "Cvar_Get( QL_ZMQ_CVAR_RCON_ENABLE, QL_ZMQ_DEFAULT_DISABLED, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
		and "Cvar_Get( QL_ZMQ_CVAR_STATS_ENABLE, QL_ZMQ_DEFAULT_DISABLED, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
		and "Cvar_Get( QL_ZMQ_CVAR_STATS_PASSWORD, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_PASSWORD_FLAGS );" in sv_zmq
		and "Cvar_Get( QL_ZMQ_CVAR_RCON_PASSWORD, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_PASSWORD_FLAGS );" in sv_zmq
		and "Cvar_Get( QL_ZMQ_CVAR_NET_PORT, va( QL_ZMQ_DEFAULT_NET_PORT_FORMAT, PORT_SERVER ), QL_ZMQ_CVAR_NET_FALLBACK_FLAGS );" in sv_zmq
		and "#define QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE 64" in sv_zmq
		and "char resolvedIp[QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE];" in sv_zmq
		and "char resolvedIp[64];" not in sv_zmq
		and "qboolean\t\t\t\tauthActorReady;" in sv_zmq
		and "idZMQ_PumpAuthSocket();" in sv_zmq
		and '#define QL_ZMQ_PUBLICATION_TYPE_KEY "TYPE"' in sv_zmq
		and '#define QL_ZMQ_PUBLICATION_DATA_KEY "DATA"' in sv_zmq
		and '#define QL_ZMQ_MATCH_REPORT_TYPE "MATCH_REPORT"' in sv_zmq
		and '#define QL_ZMQ_STATS_TRANSCRIPT "zmq_stats.ndjson"' in sv_zmq
		and "#define QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY 0" in sv_zmq
		and '#define QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR "\\n"' in sv_zmq
		and "#define QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR_LENGTH 1" in sv_zmq
		and "s_zmq.statsTranscript = QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY;" in sv_zmq
		and "s_zmq.statsTranscript = 0;" not in sv_zmq
		and "FS_Write( QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR, QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR_LENGTH, s_zmq.statsTranscript );" in sv_zmq
		and "idZMQ_Publish( QL_ZMQ_MATCH_REPORT_TYPE, (const char *)report );" in sv_zmq
		and '#define QL_ZMQ_RCON_BIND_SUCCESS_FORMAT "zmq RCON socket: %s\\n"' in sv_zmq
		and '#define QL_ZMQ_STATS_BIND_SUCCESS_FORMAT "zmq PUB socket: %s\\n"' in sv_zmq
		and "#define QL_ZMQ_RCON_BROADCAST_ACTIVE qtrue" in sv_zmq
		and "#define QL_ZMQ_RCON_BROADCAST_IDLE qfalse" in sv_zmq
		and '#define QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT "zmq RCON client disconnected: %s\\n"' in sv_zmq
		and '#define QL_ZMQ_RCON_CLIENT_CONNECT_FORMAT "zmq RCON client connected: %s\\n"' in sv_zmq
		and '#define QL_ZMQ_RCON_COMMAND_FORMAT "zmq RCON command from %s: %s\\n"' in sv_zmq
		and "#define QL_ZMQ_RCON_EMPTY_PAYLOAD QL_ZMQ_DEFAULT_EMPTY" in sv_zmq
		and "#define QL_ZMQ_RCON_PEER_SLOT_EMPTY NULL" in sv_zmq
		and "payload = message ? message : QL_ZMQ_RCON_EMPTY_PAYLOAD;" in sv_zmq
		and "s_zmq.rconPeers = QL_ZMQ_RCON_PEER_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.rconPeerRoot = QL_ZMQ_RCON_PEER_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.rconPeerLast = QL_ZMQ_RCON_PEER_SLOT_EMPTY;" in sv_zmq
		and "s_zmq.rconPeers = NULL;" not in sv_zmq
		and "Com_Printf( QL_ZMQ_RCON_BIND_SUCCESS_FORMAT, s_zmq.rconEndpoint );" in sv_zmq
		and "Com_Printf( QL_ZMQ_STATS_BIND_SUCCESS_FORMAT, s_zmq.statsEndpoint );" in sv_zmq
		and "if ( s_zmq.zmq_bind( socket, QL_ZMQ_ZAP_ENDPOINT ) != QL_ZMQ_BIND_SUCCESS ) {" in sv_zmq
		and "if ( s_zmq.zmq_bind( socket, s_zmq.rconEndpoint ) != QL_ZMQ_BIND_SUCCESS ) {" in sv_zmq
		and "if ( s_zmq.zmq_bind( socket, s_zmq.statsEndpoint ) != QL_ZMQ_BIND_SUCCESS ) {" in sv_zmq
		and "zmq_bind( socket, QL_ZMQ_ZAP_ENDPOINT ) != 0" not in sv_zmq
		and "zmq_bind( socket, s_zmq.rconEndpoint ) != 0" not in sv_zmq
		and "zmq_bind( socket, s_zmq.statsEndpoint ) != 0" not in sv_zmq
		and "Com_Printf( QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT, peer->label );" in sv_zmq
		and "s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_ACTIVE;" in sv_zmq
		and "s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_IDLE;" in sv_zmq
		and "s_zmq.broadcastingRconOutput = qtrue;" not in sv_zmq
		and "s_zmq.broadcastingRconOutput = qfalse;" not in sv_zmq
		and "Com_Printf( QL_ZMQ_RCON_CLIENT_CONNECT_FORMAT, peer->label );" in sv_zmq
		and "Com_Printf( QL_ZMQ_RCON_COMMAND_FORMAT, peer->label, command );" in sv_zmq
		and "test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners" in platform_services_tests
		and "test_zmq_password_refresh_actor_source_shape_round_643_is_pinned" in platform_services_tests
		and "test_zmq_stats_init_idempotent_wrapper_round_644_is_pinned" in platform_services_tests
		and "test_zmq_rcon_frame_pump_is_poll_only_round_645_is_pinned" in platform_services_tests
		and "test_zmq_rcon_broadcast_disconnect_branch_round_646_is_pinned" in platform_services_tests
		and "test_zmq_rcon_broadcast_null_payload_round_647_is_pinned" in platform_services_tests
		and "test_zmq_rcon_broadcast_reentrancy_guard_round_751_is_pinned" in platform_services_tests
		and "test_zmq_stats_endpoint_net_ip_round_648_is_pinned" in platform_services_tests
		and "test_zmq_socket_bind_failure_retention_round_649_is_pinned" in platform_services_tests
		and "test_zmq_rcon_resolved_poll_slot_round_650_is_pinned" in platform_services_tests
		and "test_zmq_auth_actor_ready_shutdown_order_round_651_is_pinned" in platform_services_tests
		and "test_zmq_password_apply_auth_gate_round_652_is_pinned" in platform_services_tests
		and "test_zmq_shutdown_owner_split_round_653_is_pinned" in platform_services_tests
		and "test_zmq_endpoint_empty_clear_boundary_round_691_is_pinned" in platform_services_tests
		and "test_zmq_runtime_shutdown_skips_peer_clear_round_654_is_pinned" in platform_services_tests
		and "test_zmq_peer_tree_iterator_boundary_round_655_is_pinned" in platform_services_tests
		and "test_zmq_rcon_peer_count_floor_round_724_is_pinned" in platform_services_tests
		and "test_zmq_rcon_peer_table_slot_clear_round_747_is_pinned" in platform_services_tests
		and "test_zmq_public_wrapper_tailcalls_round_656_are_pinned" in platform_services_tests
		and "test_zmq_retained_idzmq_layout_boundary_round_657_is_pinned" in platform_services_tests
		and "test_zmq_checked_zsock_lifecycle_provenance_round_658_is_pinned" in platform_services_tests
		and "test_zmq_socket_close_slot_clear_round_736_is_pinned" in platform_services_tests
		and "test_zmq_auth_bind_failure_close_slot_round_738_is_pinned" in platform_services_tests
		and "test_zmq_context_shutdown_slot_clear_round_740_is_pinned" in platform_services_tests
		and "test_zmq_external_runtime_library_slot_clear_round_742_is_pinned" in platform_services_tests
		and "test_zmq_external_runtime_resolved_symbol_slot_clear_round_743_is_pinned" in platform_services_tests
		and "test_zmq_rcon_poll_slot_clear_order_round_746_is_pinned" in platform_services_tests
		and "test_zmq_auth_actor_verbose_handshake_boundary_round_659_is_pinned" in platform_services_tests
		and "test_zmq_password_plain_notification_boundary_round_660_is_pinned" in platform_services_tests
		and "test_zmq_endpoint_cvar_literal_boundary_round_661_is_pinned" in platform_services_tests
		and "test_zmq_cvar_flag_boundary_round_697_is_pinned" in platform_services_tests
		and "test_zmq_rcon_positive_frame_gate_round_698_is_pinned" in platform_services_tests
		and "test_zmq_endpoint_ip_scratch_buffer_round_721_is_pinned" in platform_services_tests
		and "test_zmq_zap_domain_constant_boundary_round_662_is_pinned" in platform_services_tests
		and "test_zmq_rcon_peer_log_format_boundary_round_663_is_pinned" in platform_services_tests
		and "test_zmq_stats_publication_envelope_boundary_round_664_is_pinned" in platform_services_tests
		and "test_zmq_passfile_failed_open_boundary_round_665_is_pinned" in platform_services_tests
		and "test_zmq_passfile_record_buffer_round_722_is_pinned" in platform_services_tests
		and "test_zmq_external_runtime_loader_boundary_round_666_is_pinned" in platform_services_tests
		and "test_zmq_external_runtime_export_names_round_692_is_pinned" in platform_services_tests
		and "test_zmq_manual_zap_auth_response_boundary_round_667_is_pinned" in platform_services_tests
		and "test_zmq_zap_request_buffer_boundary_round_689_is_pinned" in platform_services_tests
		and "test_zmq_receive_frame_drain_boundary_round_668_is_pinned" in platform_services_tests
		and "test_zmq_receive_frame_more_flag_round_752_is_pinned" in platform_services_tests
		and "test_zmq_receive_string_terminator_boundary_round_684_is_pinned" in platform_services_tests
		and "test_zmq_stats_transcript_line_boundary_round_669_is_pinned" in platform_services_tests
		and "test_zmq_stats_transcript_handle_clear_round_749_is_pinned" in platform_services_tests
		and "test_zmq_stats_default_port_format_boundary_round_671_is_pinned" in platform_services_tests
		and "test_zmq_rcon_empty_payload_constant_boundary_round_672_is_pinned" in platform_services_tests
		and "test_zmq_socket_option_boolean_boundary_round_674_is_pinned" in platform_services_tests
		and "test_zmq_socket_option_int_size_round_733_is_pinned" in platform_services_tests
		and "test_zmq_socket_option_string_size_round_734_is_pinned" in platform_services_tests
		and "test_zmq_no_flags_and_immediate_poll_boundary_round_676_is_pinned" in platform_services_tests
		and "test_zmq_single_poll_item_boundary_round_679_is_pinned" in platform_services_tests
		and "test_zmq_poll_item_zero_state_boundary_round_680_is_pinned" in platform_services_tests
		and "test_zmq_rcon_receive_buffer_boundary_round_682_is_pinned" in platform_services_tests
		and "test_zmq_rcon_broadcast_send_flag_boundary_round_686_is_pinned" in platform_services_tests
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
				"static void idZMQ_ApplyPasswords( void ) {" in sv_zmq
				and "if ( !s_zmq.authActorReady ) {" in sv_zmq
				and '#define QL_ZMQ_PASSFILE "zmqpass.txt"' in sv_zmq
				and '#define QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT "Failed to open %s\\n"' in sv_zmq
				and '#define QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT "stats_stats=%s\\n"' in sv_zmq
				and '#define QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT "rcon_rcon=%s\\n"' in sv_zmq
				and "#define QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE ( MAX_STRING_CHARS + QL_ZMQ_PASSFILE_RECORD_SLACK )" in sv_zmq
				and "char line[QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE];" in sv_zmq
				and '#define QL_ZMQ_AUTH_KEY_FORMAT "%s_%s"' in sv_zmq
				and "Com_Printf( QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT, QL_ZMQ_PASSFILE );" in sv_zmq
				and "Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT, s_zmq.statsPassword );" in sv_zmq
				and "Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT, s_zmq.rconPassword );" in sv_zmq
			),
			"endpoint_empty_clears_present": (
				"#define QL_ZMQ_ENDPOINT_EMPTY QL_ZMQ_STRING_TERMINATOR" in sv_zmq
				and "s_zmq.rconEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;" in sv_zmq
				and "s_zmq.statsEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;" in sv_zmq
				and "s_zmq.rconEndpoint[0] = '\\0';" not in sv_zmq
				and "s_zmq.statsEndpoint[0] = '\\0';" not in sv_zmq
			),
			"passfile_record_buffer_present": (
				"#define QL_ZMQ_PASSFILE_RECORD_SLACK 32" in sv_zmq
				and "#define QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE ( MAX_STRING_CHARS + QL_ZMQ_PASSFILE_RECORD_SLACK )" in sv_zmq
				and "char line[QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE];" in sv_zmq
				and "char line[MAX_STRING_CHARS + 32];" not in sv_zmq
				and "Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT, s_zmq.statsPassword );" in sv_zmq
				and "Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT, s_zmq.rconPassword );" in sv_zmq
			),
			"zap_domain_wiring_present": (
				"idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, QL_ZMQ_DOMAIN_RCON );" in sv_zmq
				and "idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, QL_ZMQ_DOMAIN_STATS );" in sv_zmq
			),
			"socket_option_string_size_present": (
				"#define QL_ZMQ_SOCKET_OPTION_STRING_SIZE( value ) strlen( value )" in sv_zmq
				and "s_zmq.zmq_setsockopt( socket, option, value, QL_ZMQ_SOCKET_OPTION_STRING_SIZE( value ) );" in sv_zmq
				and "s_zmq.zmq_setsockopt( socket, option, value, strlen( value ) );" not in sv_zmq
				and "zsock_set_zap_domain" not in sv_zmq
			),
			"stats_default_port_present": (
				'#define QL_ZMQ_DEFAULT_NET_PORT_FORMAT "%i"' in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_NET_PORT, va( QL_ZMQ_DEFAULT_NET_PORT_FORMAT, PORT_SERVER ), QL_ZMQ_CVAR_NET_FALLBACK_FLAGS );" in sv_zmq
			),
			"cvar_flag_boundary_present": (
				"#define QL_ZMQ_CVAR_INIT_FLAGS CVAR_INIT" in sv_zmq
				and "#define QL_ZMQ_CVAR_PASSWORD_FLAGS CVAR_ARCHIVE" in sv_zmq
				and "#define QL_ZMQ_CVAR_NET_FALLBACK_FLAGS CVAR_LATCH" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_RCON_ENABLE, QL_ZMQ_DEFAULT_DISABLED, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_STATS_ENABLE, QL_ZMQ_DEFAULT_DISABLED, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_RCON_IP, QL_ZMQ_DEFAULT_RCON_IP, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_RCON_PORT, QL_ZMQ_DEFAULT_RCON_PORT, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_STATS_IP, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_STATS_PORT, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_INIT_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_STATS_PASSWORD, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_PASSWORD_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_RCON_PASSWORD, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_PASSWORD_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_NET_IP, QL_ZMQ_DEFAULT_NET_IP, QL_ZMQ_CVAR_NET_FALLBACK_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_NET_PORT, va( QL_ZMQ_DEFAULT_NET_PORT_FORMAT, PORT_SERVER ), QL_ZMQ_CVAR_NET_FALLBACK_FLAGS );" in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_RCON_ENABLE, QL_ZMQ_DEFAULT_DISABLED, CVAR_INIT );" not in sv_zmq
				and "Cvar_Get( QL_ZMQ_CVAR_RCON_PASSWORD, QL_ZMQ_DEFAULT_EMPTY, CVAR_ARCHIVE );" not in sv_zmq
			),
			"endpoint_ip_scratch_buffer_present": (
				"#define QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE 64" in sv_zmq
				and "char resolvedIp[QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE];" in sv_zmq
				and "char resolvedIp[64];" not in sv_zmq
				and "idZMQ_ResolveStatsHost( resolvedIp, sizeof( resolvedIp ) );" in sv_zmq
				and "Q_strncpyz( resolvedIp, QL_ZMQ_DEFAULT_RCON_IP, sizeof( resolvedIp ) );" in sv_zmq
			),
			"auth_pump_present": "idZMQ_PumpAuthSocket();" in sv_zmq,
			"auth_actor_ready_present": "qboolean\t\t\t\tauthActorReady;" in sv_zmq,
			"manual_zap_response_present": (
				'#define QL_ZMQ_AUTH_EMPTY_FRAME ""' in sv_zmq
				and "#define QL_ZMQ_AUTH_EMPTY_USER_ID QL_ZMQ_AUTH_EMPTY_FRAME" in sv_zmq
				and "#define QL_ZMQ_AUTH_EMPTY_CREDENTIAL QL_ZMQ_AUTH_EMPTY_FRAME" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, version, qtrue )" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, requestId, qtrue )" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, statusCode, qtrue )" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, statusText, qtrue )" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, userId, qtrue )" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, QL_ZMQ_AUTH_EMPTY_FRAME, qfalse );" in sv_zmq
				and "userId = QL_ZMQ_AUTH_EMPTY_USER_ID;" in sv_zmq
				and "*userId = QL_ZMQ_AUTH_EMPTY_USER_ID;" in sv_zmq
			),
			"zap_request_buffers_present": (
				"#define QL_ZMQ_ZAP_VERSION_BUFFER_SIZE 16" in sv_zmq
				and "#define QL_ZMQ_ZAP_REQUEST_ID_BUFFER_SIZE 64" in sv_zmq
				and "#define QL_ZMQ_ZAP_DOMAIN_BUFFER_SIZE 64" in sv_zmq
				and "#define QL_ZMQ_ZAP_ADDRESS_BUFFER_SIZE 128" in sv_zmq
				and "#define QL_ZMQ_ZAP_IDENTITY_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY" in sv_zmq
				and "#define QL_ZMQ_ZAP_MECHANISM_BUFFER_SIZE 16" in sv_zmq
				and "#define QL_ZMQ_ZAP_USERNAME_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY" in sv_zmq
				and "#define QL_ZMQ_ZAP_PASSWORD_BUFFER_SIZE MAX_STRING_CHARS" in sv_zmq
				and "#define QL_ZMQ_ZAP_EMPTY_FIELD QL_ZMQ_STRING_TERMINATOR" in sv_zmq
				and "char version[QL_ZMQ_ZAP_VERSION_BUFFER_SIZE];" in sv_zmq
				and "char requestId[QL_ZMQ_ZAP_REQUEST_ID_BUFFER_SIZE];" in sv_zmq
				and "char domain[QL_ZMQ_ZAP_DOMAIN_BUFFER_SIZE];" in sv_zmq
				and "char address[QL_ZMQ_ZAP_ADDRESS_BUFFER_SIZE];" in sv_zmq
				and "char identity[QL_ZMQ_ZAP_IDENTITY_BUFFER_SIZE];" in sv_zmq
				and "char mechanism[QL_ZMQ_ZAP_MECHANISM_BUFFER_SIZE];" in sv_zmq
				and "char username[QL_ZMQ_ZAP_USERNAME_BUFFER_SIZE];" in sv_zmq
				and "char password[QL_ZMQ_ZAP_PASSWORD_BUFFER_SIZE];" in sv_zmq
				and "requestId[0] = QL_ZMQ_ZAP_EMPTY_FIELD;" in sv_zmq
				and "char version[16];" not in sv_zmq
				and "char requestId[64];" not in sv_zmq
				and "requestId[0] = '\\0';" not in sv_zmq
			),
			"receive_frame_drain_present": (
				'#define QL_ZMQ_DRAIN_SCRATCH_SIZE MAX_STRING_CHARS' in sv_zmq
				and "length = s_zmq.zmq_recv( socket, buffer, bufferSize > 0 ? bufferSize - QL_ZMQ_STRING_TERMINATOR_LENGTH : 0, QL_ZMQ_DONTWAIT );" in sv_zmq
				and "if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {" in sv_zmq
				and "s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == QL_ZMQ_GETSOCKOPT_SUCCESS && moreValue != QL_ZMQ_RCVMORE_NONE" in sv_zmq
				and "char scratch[QL_ZMQ_DRAIN_SCRATCH_SIZE];" in sv_zmq
				and "idZMQ_ReadFrameString( socket, scratch, sizeof( scratch ), &more ) < QL_ZMQ_FRAME_READ_SUCCESS_MIN" in sv_zmq
				and "idZMQ_DrainRemainingFrames( s_zmq.authSocket, more );" in sv_zmq
				and "idZMQ_DrainRemainingFrames( s_zmq.rconSocket, more );" in sv_zmq
			),
			"rcvmore_getsockopt_success_present": (
				"#define QL_ZMQ_GETSOCKOPT_SUCCESS 0" in sv_zmq
				and "#define QL_ZMQ_RCVMORE_NONE 0" in sv_zmq
				and "moreValue = QL_ZMQ_RCVMORE_NONE;" in sv_zmq
				and "s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == QL_ZMQ_GETSOCKOPT_SUCCESS && moreValue != QL_ZMQ_RCVMORE_NONE" in sv_zmq
				and "s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == 0 && moreValue" not in sv_zmq
				and "zsock_rcvmore(" not in sv_zmq
			),
			"receive_frame_more_flag_present": (
				"#define QL_ZMQ_FRAME_MORE qtrue" in sv_zmq
				and "#define QL_ZMQ_FRAME_NO_MORE qfalse" in sv_zmq
				and "*more = QL_ZMQ_FRAME_NO_MORE;" in sv_zmq
				and "*more = QL_ZMQ_FRAME_MORE;" in sv_zmq
				and "more = QL_ZMQ_FRAME_NO_MORE;" in sv_zmq
				and "*more = qfalse;" not in sv_zmq
				and "*more = qtrue;" not in sv_zmq
				and "moreValue = QL_ZMQ_RCVMORE_NONE;" in sv_zmq
				and "s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == QL_ZMQ_GETSOCKOPT_SUCCESS && moreValue != QL_ZMQ_RCVMORE_NONE" in sv_zmq
				and "zstr_recv(" not in sv_zmq
				and "zsock_rcvmore(" not in sv_zmq
			),
			"frame_read_failure_threshold_present": (
				"#define QL_ZMQ_FRAME_READ_SUCCESS_MIN 0" in sv_zmq
				and "if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {" in sv_zmq
				and "idZMQ_ReadFrameString( socket, scratch, sizeof( scratch ), &more ) < QL_ZMQ_FRAME_READ_SUCCESS_MIN" in sv_zmq
				and "commandLength >= QL_ZMQ_FRAME_READ_SUCCESS_MIN" in sv_zmq
				and "if ( length < 0 ) {" not in sv_zmq
				and "idZMQ_ReadFrameString( socket, scratch, sizeof( scratch ), &more ) < 0" not in sv_zmq
				and "zstr_recv(" not in sv_zmq
				and "zstr_free(" not in sv_zmq
				and "zmq_msg_recv(" not in sv_zmq
			),
			"receive_string_terminator_present": (
				"#define QL_ZMQ_STRING_TERMINATOR_LENGTH 1" in sv_zmq
				and "#define QL_ZMQ_STRING_TERMINATOR '\\0'" in sv_zmq
				and "#define QL_ZMQ_RCVMORE_NONE 0" in sv_zmq
				and "buffer[0] = QL_ZMQ_STRING_TERMINATOR;" in sv_zmq
				and "bufferSize > 0 ? bufferSize - QL_ZMQ_STRING_TERMINATOR_LENGTH : 0" in sv_zmq
				and "length = (int)bufferSize - QL_ZMQ_STRING_TERMINATOR_LENGTH;" in sv_zmq
				and "buffer[length] = QL_ZMQ_STRING_TERMINATOR;" in sv_zmq
				and "moreValue = QL_ZMQ_RCVMORE_NONE;" in sv_zmq
				and "bufferSize - 1" not in sv_zmq
			),
			"socket_option_booleans_present": (
				"#define QL_ZMQ_SOCKET_OPTION_DISABLED 0" in sv_zmq
				and "#define QL_ZMQ_SOCKET_OPTION_ENABLED 1" in sv_zmq
				and "idZMQ_TrySetSocketInt( socket, QL_ZMQ_ROUTER_MANDATORY, QL_ZMQ_SOCKET_OPTION_ENABLED );" in sv_zmq
				and "idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.rconPassword[0] ? QL_ZMQ_SOCKET_OPTION_ENABLED : QL_ZMQ_SOCKET_OPTION_DISABLED );" in sv_zmq
				and "idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.statsPassword[0] ? QL_ZMQ_SOCKET_OPTION_ENABLED : QL_ZMQ_SOCKET_OPTION_DISABLED );" in sv_zmq
			),
			"socket_option_int_size_present": (
				"#define QL_ZMQ_SOCKET_OPTION_INT_SIZE sizeof( int )" in sv_zmq
				and "s_zmq.zmq_setsockopt( socket, option, &value, QL_ZMQ_SOCKET_OPTION_INT_SIZE );" in sv_zmq
				and "s_zmq.zmq_setsockopt( socket, option, &value, sizeof( value ) );" not in sv_zmq
				and "zsock_set_plain_server" not in sv_zmq
				and "zsock_set_router_mandatory" not in sv_zmq
			),
			"no_flags_and_immediate_poll_present": (
				"#define QL_ZMQ_NO_FLAGS 0" in sv_zmq
				and "#define QL_ZMQ_POLL_TIMEOUT_IMMEDIATE 0" in sv_zmq
				and "flags = more ? QL_ZMQ_SNDMORE : QL_ZMQ_NO_FLAGS;" in sv_zmq
				and "s_zmq.zmq_send( s_zmq.pubSocket, message, strlen( message ), QL_ZMQ_NO_FLAGS );" in sv_zmq
				and "s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE )" in sv_zmq
			),
			"single_poll_item_present": (
				"#define QL_ZMQ_SINGLE_POLL_ITEM 1" in sv_zmq
				and "while ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) >= QL_ZMQ_POLL_READY_MIN && ( item.revents & QL_ZMQ_POLLIN ) ) {" in sv_zmq
				and "if ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) < QL_ZMQ_POLL_READY_MIN || !( item.revents & QL_ZMQ_POLLIN ) ) {" in sv_zmq
				and "s_zmq.zmq_poll( &item, 1, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE )" not in sv_zmq
			),
			"poll_ready_threshold_present": (
				"#define QL_ZMQ_POLL_READY_MIN 1" in sv_zmq
				and "while ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) >= QL_ZMQ_POLL_READY_MIN && ( item.revents & QL_ZMQ_POLLIN ) ) {" in sv_zmq
				and "if ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) < QL_ZMQ_POLL_READY_MIN || !( item.revents & QL_ZMQ_POLLIN ) ) {" in sv_zmq
				and "QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) > 0" not in sv_zmq
				and "QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) <= 0" not in sv_zmq
				and "zmq_poll(" not in sv_zmq.replace("s_zmq.zmq_poll(", "")
			),
			"poll_item_zero_state_present": (
				"#define QL_ZMQ_POLL_FD_NONE 0" in sv_zmq
				and "#define QL_ZMQ_POLL_REVENTS_NONE 0" in sv_zmq
				and "item.fd = QL_ZMQ_POLL_FD_NONE;" in sv_zmq
				and "item.revents = QL_ZMQ_POLL_REVENTS_NONE;" in sv_zmq
				and "item.fd = 0;" not in sv_zmq
				and "item.revents = 0;" not in sv_zmq
			),
			"rcon_receive_buffers_present": (
				"#define QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY" in sv_zmq
				and "#define QL_ZMQ_RCON_COMMAND_BUFFER_SIZE MAX_STRING_CHARS" in sv_zmq
				and "char identity[QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE];" in sv_zmq
				and "char command[QL_ZMQ_RCON_COMMAND_BUFFER_SIZE];" in sv_zmq
				and "identityLength = idZMQ_ReadFrameString( s_zmq.rconSocket, identity, sizeof( identity ), &more );" in sv_zmq
				and "commandLength = idZMQ_ReadRconCommand( command, sizeof( command ) );" in sv_zmq
			),
			"rcon_positive_frame_gate_present": (
				"#define QL_ZMQ_FRAME_READ_SUCCESS_MIN 0" in sv_zmq
				and "#define QL_ZMQ_RCON_MIN_IDENTITY_LENGTH 1" in sv_zmq
				and "#define QL_ZMQ_RCON_MIN_COMMAND_LENGTH 1" in sv_zmq
				and "commandLength >= QL_ZMQ_FRAME_READ_SUCCESS_MIN" in sv_zmq
				and "identityLength < QL_ZMQ_RCON_MIN_IDENTITY_LENGTH" in sv_zmq
				and "commandLength < QL_ZMQ_RCON_MIN_COMMAND_LENGTH" in sv_zmq
				and "commandLength >= 0" not in sv_zmq
				and "identityLength <= 0" not in sv_zmq
				and "commandLength <= 0" not in sv_zmq
			),
			"rcon_peer_count_floor_present": (
				"#define QL_ZMQ_RCON_PEER_COUNT_EMPTY 0" in sv_zmq
				and "s_zmq.rconPeerCount++;" in sv_zmq
				and "if ( s_zmq.rconPeerCount > QL_ZMQ_RCON_PEER_COUNT_EMPTY ) {" in sv_zmq
				and "s_zmq.rconPeerCount--;" in sv_zmq
				and "s_zmq.rconPeerCount = QL_ZMQ_RCON_PEER_COUNT_EMPTY;" in sv_zmq
				and "s_zmq.rconPeerCount > 0" not in sv_zmq
				and "s_zmq.rconPeerCount = 0;" not in sv_zmq
			),
			"rcon_peer_table_slot_clear_present": (
				"#define QL_ZMQ_RCON_PEER_SLOT_EMPTY NULL" in sv_zmq
				and "idZMQ_FreeRconPeerSubtree( s_zmq.rconPeerRoot );" in sv_zmq
				and "s_zmq.rconPeers = QL_ZMQ_RCON_PEER_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.rconPeerRoot = QL_ZMQ_RCON_PEER_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.rconPeerLast = QL_ZMQ_RCON_PEER_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.rconPeerCount = QL_ZMQ_RCON_PEER_COUNT_EMPTY;" in sv_zmq
				and "s_zmq.rconPeers = NULL;" not in sv_zmq
				and "idZMQ_EraseRconPeerRange( s_zmq.rconPeers, NULL );" in sv_zmq
				and "idZMQ_ClearRconPeers();" in sv_zmq
				and "std_tree_" not in sv_zmq
			),
			"external_runtime_loader_present": (
				'#define QL_ZMQ_RUNTIME_UNAVAILABLE_FORMAT "ZMQ runtime unavailable: %s\\n"' in sv_zmq
				and '#define QL_ZMQ_RUNTIME_DISABLED_MESSAGE "ZMQ runtime disabled by build policy (QL_BUILD_ONLINE_SERVICES=0); keeping retained fallback paths.\\n"' in sv_zmq
				and '#define QL_ZMQ_RUNTIME_LOAD_FAILED_REASON "unable to load libzmq"' in sv_zmq
				and '#define QL_ZMQ_RUNTIME_EXPORTS_MISSING_REASON "libzmq is missing required exports"' in sv_zmq
				and "Com_Printf( QL_ZMQ_RUNTIME_DISABLED_MESSAGE );" in sv_zmq
				and "Com_Printf( QL_ZMQ_RUNTIME_UNAVAILABLE_FORMAT, reason );" in sv_zmq
				and "idZMQ_LogRuntimeUnavailable( QL_ZMQ_RUNTIME_LOAD_FAILED_REASON );" in sv_zmq
				and "idZMQ_LogRuntimeUnavailable( QL_ZMQ_RUNTIME_EXPORTS_MISSING_REASON );" in sv_zmq
			),
			"external_runtime_export_names_present": (
				'#define QL_ZMQ_EXPORT_CTX_NEW "zmq_ctx_new"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_CTX_TERM "zmq_ctx_term"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_SOCKET "zmq_socket"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_CLOSE "zmq_close"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_BIND "zmq_bind"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_SEND "zmq_send"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_RECV "zmq_recv"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_POLL "zmq_poll"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_ERRNO "zmq_errno"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_STRERROR "zmq_strerror"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_SETSOCKOPT "zmq_setsockopt"' in sv_zmq
				and '#define QL_ZMQ_EXPORT_GETSOCKOPT "zmq_getsockopt"' in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_new, QL_ZMQ_EXPORT_CTX_NEW )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_term, QL_ZMQ_EXPORT_CTX_TERM )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_socket, QL_ZMQ_EXPORT_SOCKET )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_close, QL_ZMQ_EXPORT_CLOSE )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_bind, QL_ZMQ_EXPORT_BIND )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_send, QL_ZMQ_EXPORT_SEND )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_recv, QL_ZMQ_EXPORT_RECV )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_poll, QL_ZMQ_EXPORT_POLL )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_errno, QL_ZMQ_EXPORT_ERRNO )" in sv_zmq
				and "idZMQ_LoadSymbol( (void **)&s_zmq.zmq_strerror, QL_ZMQ_EXPORT_STRERROR )" in sv_zmq
				and "idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_setsockopt, QL_ZMQ_EXPORT_SETSOCKOPT );" in sv_zmq
				and "idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_getsockopt, QL_ZMQ_EXPORT_GETSOCKOPT );" in sv_zmq
				and 'idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_new, "zmq_ctx_new" )' not in sv_zmq
				and 'idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_setsockopt, "zmq_setsockopt" );' not in sv_zmq
			),
			"context_shutdown_slot_clear_present": (
				"#define QL_ZMQ_CONTEXT_SLOT_EMPTY NULL" in sv_zmq
				and "if ( s_zmq.context && s_zmq.zmq_ctx_term ) {" in sv_zmq
				and "s_zmq.zmq_ctx_term( s_zmq.context );" in sv_zmq
				and "s_zmq.context = QL_ZMQ_CONTEXT_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.context = NULL;" not in sv_zmq
				and "zmq_ctx_t_term(" not in sv_zmq
				and "zmq_term(" not in sv_zmq
			),
			"external_runtime_library_slot_clear_present": (
				"#define QL_ZMQ_LIBRARY_SLOT_EMPTY NULL" in sv_zmq
				and "QL_ZMQ_CLOSE();" in sv_zmq
				and "s_zmq.library = QL_ZMQ_LIBRARY_SLOT_EMPTY;" in sv_zmq
				and sv_zmq.count("s_zmq.library = QL_ZMQ_LIBRARY_SLOT_EMPTY;") == 2
				and "s_zmq.library = NULL;" not in sv_zmq
				and "idZMQ_ResetResolvedSymbols();" in sv_zmq
				and "idZMQ_UnloadLibrary();" in sv_zmq
				and "#include <zmq.h>" not in sv_zmq
				and "zsys_shutdown(" not in sv_zmq
			),
			"external_runtime_resolved_symbol_slot_clear_present": (
				"#define QL_ZMQ_SYMBOL_SLOT_EMPTY NULL" in sv_zmq
				and "s_zmq.zmq_ctx_new = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_ctx_term = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_socket = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_close = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_bind = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_setsockopt = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_getsockopt = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_send = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_recv = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_poll = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_errno = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and "s_zmq.zmq_strerror = QL_ZMQ_SYMBOL_SLOT_EMPTY;" in sv_zmq
				and sv_zmq.count("= QL_ZMQ_SYMBOL_SLOT_EMPTY;") == 12
				and "s_zmq.zmq_ctx_new = NULL;" not in sv_zmq
				and "idZMQ_ResetResolvedSymbols();" in sv_zmq
				and "#include <zmq.h>" not in sv_zmq
			),
			"rcon_poll_slot_clear_present": (
				"#define QL_ZMQ_RCON_POLL_SLOT_EMPTY NULL" in sv_zmq
				and "s_zmq.rconPollSocket = QL_ZMQ_RCON_POLL_SLOT_EMPTY;" in sv_zmq
				and sv_zmq.count("s_zmq.rconPollSocket = QL_ZMQ_RCON_POLL_SLOT_EMPTY;") == 2
				and "s_zmq.rconPollSocket = NULL;" not in sv_zmq
				and "s_zmq.rconPollSocket = s_zmq.rconSocket;" in sv_zmq
				and "if ( !s_zmq.rconSocket || !s_zmq.rconPollSocket || !s_zmq.zmq_poll || !s_zmq.zmq_recv ) {" in sv_zmq
				and "item.socket = s_zmq.rconPollSocket;" in sv_zmq
				and "zsock_resolve(" not in sv_zmq
				and "zsock_destroy_checked" not in sv_zmq
			),
			"socket_close_slot_clear_present": (
				"#define QL_ZMQ_SOCKET_SLOT_EMPTY NULL" in sv_zmq
				and "if ( *socketPointer && s_zmq.zmq_close ) {" in sv_zmq
				and "s_zmq.zmq_close( *socketPointer );" in sv_zmq
				and "*socketPointer = QL_ZMQ_SOCKET_SLOT_EMPTY;" in sv_zmq
				and "*socketPointer = NULL;" not in sv_zmq
				and "zsock_destroy_checked" not in sv_zmq
				and "zsys_close(" not in sv_zmq
			),
			"auth_bind_failure_close_slot_present": (
				"if ( s_zmq.zmq_bind( socket, QL_ZMQ_ZAP_ENDPOINT ) != QL_ZMQ_BIND_SUCCESS ) {" in sv_zmq
				and "idZMQ_LogRuntimeUnavailable( va( QL_ZMQ_AUTH_SOCKET_BIND_FAILED_FORMAT, idZMQ_LastErrorString() ) );" in sv_zmq
				and "idZMQ_CloseSocket( &socket );" in sv_zmq
				and "s_zmq.zmq_close( socket );" not in sv_zmq
				and sv_zmq.count("s_zmq.zmq_close(") == 1
			),
			"bind_success_threshold_present": (
				"#define QL_ZMQ_BIND_SUCCESS 0" in sv_zmq
				and "if ( s_zmq.zmq_bind( socket, QL_ZMQ_ZAP_ENDPOINT ) != QL_ZMQ_BIND_SUCCESS ) {" in sv_zmq
				and "if ( s_zmq.zmq_bind( socket, s_zmq.rconEndpoint ) != QL_ZMQ_BIND_SUCCESS ) {" in sv_zmq
				and "if ( s_zmq.zmq_bind( socket, s_zmq.statsEndpoint ) != QL_ZMQ_BIND_SUCCESS ) {" in sv_zmq
				and "zmq_bind( socket, QL_ZMQ_ZAP_ENDPOINT ) != 0" not in sv_zmq
				and "zmq_bind( socket, s_zmq.rconEndpoint ) != 0" not in sv_zmq
				and "zmq_bind( socket, s_zmq.statsEndpoint ) != 0" not in sv_zmq
				and "zsock_bind(" not in sv_zmq
			),
			"typed_publication_present": (
				'#define QL_ZMQ_PUBLICATION_TYPE_KEY "TYPE"' in sv_zmq
				and '#define QL_ZMQ_PUBLICATION_DATA_KEY "DATA"' in sv_zmq
				and '#define QL_ZMQ_MATCH_REPORT_TYPE "MATCH_REPORT"' in sv_zmq
				and "Com_sprintf( buffer, bufferSize, QL_ZMQ_PUBLICATION_PAYLOAD_FORMAT, type, payload );" in sv_zmq
				and "Com_sprintf( buffer, bufferSize, QL_ZMQ_PUBLICATION_NULL_PAYLOAD_FORMAT, type );" in sv_zmq
				and "idZMQ_Publish( QL_ZMQ_MATCH_REPORT_TYPE, (const char *)report );" in sv_zmq
			),
			"stats_transcript_line_present": (
				'#define QL_ZMQ_STATS_TRANSCRIPT "zmq_stats.ndjson"' in sv_zmq
				and '#define QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR "\\n"' in sv_zmq
				and "#define QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR_LENGTH 1" in sv_zmq
				and "s_zmq.statsTranscript = FS_FOpenFileWrite( QL_ZMQ_STATS_TRANSCRIPT );" in sv_zmq
				and "FS_Write( QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR, QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR_LENGTH, s_zmq.statsTranscript );" in sv_zmq
			),
			"stats_transcript_handle_clear_present": (
				"#define QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY 0" in sv_zmq
				and "if ( s_zmq.statsTranscript ) {" in sv_zmq
				and "FS_FCloseFile( s_zmq.statsTranscript );" in sv_zmq
				and "s_zmq.statsTranscript = QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY;" in sv_zmq
				and "s_zmq.statsTranscript = 0;" not in sv_zmq
				and "idZMQ_CloseStatsTranscript();" in sv_zmq
				and "idZMQ_CloseSocket( &s_zmq.pubSocket );" in sv_zmq
				and "Zmq_ShutdownStatsPublisher();" in sv_init
				and "Zmq_ShutdownStatsPublisher();" not in sv_zmq[sv_zmq.index("void Zmq_ShutdownRuntime( void ) {"):]
				and "zstr_send(" not in sv_zmq
			),
			"rcon_peer_log_formats_present": (
				'#define QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT "zmq RCON client disconnected: %s\\n"' in sv_zmq
				and '#define QL_ZMQ_RCON_CLIENT_CONNECT_FORMAT "zmq RCON client connected: %s\\n"' in sv_zmq
				and '#define QL_ZMQ_RCON_COMMAND_FORMAT "zmq RCON command from %s: %s\\n"' in sv_zmq
				and "Com_Printf( QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT, peer->label );" in sv_zmq
				and "Com_Printf( QL_ZMQ_RCON_CLIENT_CONNECT_FORMAT, peer->label );" in sv_zmq
				and "Com_Printf( QL_ZMQ_RCON_COMMAND_FORMAT, peer->label, command );" in sv_zmq
			),
			"rcon_broadcast_reentrancy_guard_present": (
				"#define QL_ZMQ_RCON_BROADCAST_ACTIVE qtrue" in sv_zmq
				and "#define QL_ZMQ_RCON_BROADCAST_IDLE qfalse" in sv_zmq
				and "qboolean\t\t\t\tbroadcastingRconOutput;" in sv_zmq
				and "if ( s_zmq.broadcastingRconOutput ) {" in sv_zmq
				and "s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_ACTIVE;" in sv_zmq
				and "s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_IDLE;" in sv_zmq
				and "s_zmq.broadcastingRconOutput = qtrue;" not in sv_zmq
				and "s_zmq.broadcastingRconOutput = qfalse;" not in sv_zmq
				and "Com_Printf( QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT, peer->label );" in sv_zmq
				and "Zmq_BroadcastRconOutput( msg );" in common
				and "zstr_send(" not in sv_zmq
				and "zstr_sendm(" not in sv_zmq
			),
			"rcon_empty_payload_present": (
				"#define QL_ZMQ_RCON_EMPTY_PAYLOAD QL_ZMQ_DEFAULT_EMPTY" in sv_zmq
				and "payload = message ? message : QL_ZMQ_RCON_EMPTY_PAYLOAD;" in sv_zmq
				and "s_zmq.zmq_send( s_zmq.rconSocket, payload, strlen( payload ), QL_ZMQ_SEND_DONTWAIT );" in sv_zmq
			),
			"rcon_broadcast_send_flags_present": (
				"#define QL_ZMQ_SEND_DONTWAIT QL_ZMQ_DONTWAIT" in sv_zmq
				and "#define QL_ZMQ_SEND_MORE_DONTWAIT ( QL_ZMQ_SNDMORE | QL_ZMQ_DONTWAIT )" in sv_zmq
				and "s_zmq.zmq_send( s_zmq.rconSocket, peer->identity, peer->identityLength, QL_ZMQ_SEND_MORE_DONTWAIT ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
				and "s_zmq.zmq_send( s_zmq.rconSocket, payload, strlen( payload ), QL_ZMQ_SEND_DONTWAIT );" in sv_zmq
				and "peer->identity, peer->identityLength, QL_ZMQ_SNDMORE | QL_ZMQ_DONTWAIT" not in sv_zmq
			),
			"send_success_threshold_present": (
				"#define QL_ZMQ_SEND_SUCCESS_MIN 0" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, version, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, requestId, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, statusCode, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, statusText, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
				and "idZMQ_SendAuthFrame( s_zmq.authSocket, userId, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
				and "s_zmq.zmq_send( s_zmq.rconSocket, peer->identity, peer->identityLength, QL_ZMQ_SEND_MORE_DONTWAIT ) < QL_ZMQ_SEND_SUCCESS_MIN" in sv_zmq
				and "QL_ZMQ_SEND_MORE_DONTWAIT ) < 0" not in sv_zmq
				and "zstr_send(" not in sv_zmq
				and "zstr_sendm(" not in sv_zmq
				and "s_send_string(" not in sv_zmq
			),
			"focused_validation_present": (
				"test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners" in platform_services_tests
				and "test_zmq_password_refresh_actor_source_shape_round_643_is_pinned" in platform_services_tests
				and "test_zmq_stats_init_idempotent_wrapper_round_644_is_pinned" in platform_services_tests
				and "test_zmq_rcon_frame_pump_is_poll_only_round_645_is_pinned" in platform_services_tests
				and "test_zmq_rcon_broadcast_disconnect_branch_round_646_is_pinned" in platform_services_tests
				and "test_zmq_rcon_broadcast_null_payload_round_647_is_pinned" in platform_services_tests
				and "test_zmq_stats_endpoint_net_ip_round_648_is_pinned" in platform_services_tests
				and "test_zmq_socket_bind_failure_retention_round_649_is_pinned" in platform_services_tests
				and "test_zmq_bind_success_threshold_round_730_is_pinned" in platform_services_tests
				and "test_zmq_rcon_resolved_poll_slot_round_650_is_pinned" in platform_services_tests
				and "test_zmq_auth_actor_ready_shutdown_order_round_651_is_pinned" in platform_services_tests
				and "test_zmq_password_apply_auth_gate_round_652_is_pinned" in platform_services_tests
				and "test_zmq_shutdown_owner_split_round_653_is_pinned" in platform_services_tests
				and "test_zmq_endpoint_empty_clear_boundary_round_691_is_pinned" in platform_services_tests
				and "test_zmq_runtime_shutdown_skips_peer_clear_round_654_is_pinned" in platform_services_tests
				and "test_zmq_peer_tree_iterator_boundary_round_655_is_pinned" in platform_services_tests
				and "test_zmq_rcon_peer_count_floor_round_724_is_pinned" in platform_services_tests
				and "test_zmq_rcon_peer_table_slot_clear_round_747_is_pinned" in platform_services_tests
				and "test_zmq_public_wrapper_tailcalls_round_656_are_pinned" in platform_services_tests
				and "test_zmq_retained_idzmq_layout_boundary_round_657_is_pinned" in platform_services_tests
				and "test_zmq_checked_zsock_lifecycle_provenance_round_658_is_pinned" in platform_services_tests
				and "test_zmq_socket_close_slot_clear_round_736_is_pinned" in platform_services_tests
				and "test_zmq_auth_bind_failure_close_slot_round_738_is_pinned" in platform_services_tests
				and "test_zmq_context_shutdown_slot_clear_round_740_is_pinned" in platform_services_tests
				and "test_zmq_external_runtime_library_slot_clear_round_742_is_pinned" in platform_services_tests
				and "test_zmq_external_runtime_resolved_symbol_slot_clear_round_743_is_pinned" in platform_services_tests
				and "test_zmq_rcon_poll_slot_clear_order_round_746_is_pinned" in platform_services_tests
				and "test_zmq_auth_actor_verbose_handshake_boundary_round_659_is_pinned" in platform_services_tests
				and "test_zmq_password_plain_notification_boundary_round_660_is_pinned" in platform_services_tests
				and "test_zmq_endpoint_cvar_literal_boundary_round_661_is_pinned" in platform_services_tests
				and "test_zmq_cvar_flag_boundary_round_697_is_pinned" in platform_services_tests
				and "test_zmq_endpoint_ip_scratch_buffer_round_721_is_pinned" in platform_services_tests
				and "test_zmq_zap_domain_constant_boundary_round_662_is_pinned" in platform_services_tests
				and "test_zmq_rcon_peer_log_format_boundary_round_663_is_pinned" in platform_services_tests
				and "test_zmq_rcon_broadcast_reentrancy_guard_round_751_is_pinned" in platform_services_tests
				and "test_zmq_stats_publication_envelope_boundary_round_664_is_pinned" in platform_services_tests
				and "test_zmq_passfile_failed_open_boundary_round_665_is_pinned" in platform_services_tests
				and "test_zmq_passfile_record_buffer_round_722_is_pinned" in platform_services_tests
				and "test_zmq_external_runtime_loader_boundary_round_666_is_pinned" in platform_services_tests
				and "test_zmq_external_runtime_export_names_round_692_is_pinned" in platform_services_tests
				and "test_zmq_manual_zap_auth_response_boundary_round_667_is_pinned" in platform_services_tests
				and "test_zmq_zap_request_buffer_boundary_round_689_is_pinned" in platform_services_tests
				and "test_zmq_receive_frame_drain_boundary_round_668_is_pinned" in platform_services_tests
				and "test_zmq_rcvmore_getsockopt_success_round_732_is_pinned" in platform_services_tests
				and "test_zmq_receive_frame_more_flag_round_752_is_pinned" in platform_services_tests
				and "test_zmq_frame_read_failure_threshold_round_728_is_pinned" in platform_services_tests
				and "test_zmq_receive_string_terminator_boundary_round_684_is_pinned" in platform_services_tests
				and "test_zmq_stats_transcript_line_boundary_round_669_is_pinned" in platform_services_tests
				and "test_zmq_stats_transcript_handle_clear_round_749_is_pinned" in platform_services_tests
				and "test_zmq_stats_default_port_format_boundary_round_671_is_pinned" in platform_services_tests
				and "test_zmq_rcon_empty_payload_constant_boundary_round_672_is_pinned" in platform_services_tests
				and "test_zmq_socket_option_boolean_boundary_round_674_is_pinned" in platform_services_tests
				and "test_zmq_socket_option_int_size_round_733_is_pinned" in platform_services_tests
				and "test_zmq_socket_option_string_size_round_734_is_pinned" in platform_services_tests
				and "test_zmq_no_flags_and_immediate_poll_boundary_round_676_is_pinned" in platform_services_tests
				and "test_zmq_single_poll_item_boundary_round_679_is_pinned" in platform_services_tests
				and "test_zmq_poll_item_zero_state_boundary_round_680_is_pinned" in platform_services_tests
				and "test_zmq_poll_ready_threshold_round_727_is_pinned" in platform_services_tests
				and "test_zmq_rcon_receive_buffer_boundary_round_682_is_pinned" in platform_services_tests
				and "test_zmq_rcon_broadcast_send_flag_boundary_round_686_is_pinned" in platform_services_tests
				and "test_zmq_send_success_threshold_round_726_is_pinned" in platform_services_tests
			),
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
		and 'Cvar_Get ("sv_rankingsProvider", "Unavailable", CVAR_ROM );' in sv_init
		and 'Cvar_Get ("sv_rankingsPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init
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
				and 'Cvar_Get ("sv_rankingsProvider", "Unavailable", CVAR_ROM );' in sv_init
				and 'Cvar_Get ("sv_rankingsPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init
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
