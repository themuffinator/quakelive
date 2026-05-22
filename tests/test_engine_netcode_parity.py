from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_UI_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"
NET_CHAN_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "net_chan.c"
QCOMMON_H_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "qcommon.h"
COMMON_C_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
QL_UI_IMPORTS_PATH = REPO_ROOT / "src" / "code" / "client" / "ql_ui_imports.inc"
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
		'server->clients = atoi(Info_ValueForKey(info, "clients"));',
		'Q_strncpyz(server->hostName,Info_ValueForKey(info, "hostname"), MAX_NAME_LENGTH);',
		'Q_strncpyz(server->mapName, Info_ValueForKey(info, "mapname"), MAX_NAME_LENGTH);',
		'server->maxClients = atoi(Info_ValueForKey(info, "sv_maxclients"));',
		'Q_strncpyz(server->game,Info_ValueForKey(info, "game"), MAX_NAME_LENGTH);',
		'server->gameType = atoi(Info_ValueForKey(info, "gametype"));',
		'server->netType = atoi(Info_ValueForKey(info, "nettype"));',
		"server->ping = ping;",
	):
		assert expected in snippet

	for forbidden in (
		'server->minPing = atoi(Info_ValueForKey(info, "minping"));',
		'server->maxPing = atoi(Info_ValueForKey(info, "maxping"));',
		'server->punkbuster = atoi(Info_ValueForKey(info, "punkbuster"));',
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
	assert 'Info_SetValueForKey( cl_pinglist[i].info, "nettype", va("%d", type) );' in snippet

	for forbidden in (
		"char*\tstr;",
		"case NA_IPX:",
		"case NA_BROADCAST_IPX:",
		'str = "udp";',
		'str = "ipx";',
		'type = 2;',
	):
		assert forbidden not in snippet


def test_retail_steam_protocol_version_matches_hlil_constants() -> None:
	qcommon_h = _read_text(QCOMMON_H_PATH)
	common_c = _read_text(COMMON_C_PATH)
	audit_note = _read_text(NETCODE_AUDIT_PATH)

	assert "#define\tPROTOCOL_VERSION\t91" in qcommon_h
	assert "int demo_protocols[] =\n{ 91, 0 };" in common_c
	assert "{ 66, 67, 68, 0 }" not in common_c

	assert "0x5b / 91" in audit_note
	assert "`data_5684dc = 0x5b`" in audit_note
	assert "`data_5684e0 = 0`" in audit_note
	assert "`dm_91`" in audit_note


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
