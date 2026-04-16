from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_UI_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"
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
