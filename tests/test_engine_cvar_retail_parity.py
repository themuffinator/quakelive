from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

WIN_GLIMP = REPO_ROOT / "src" / "code" / "win32" / "win_glimp.c"
WIN_INPUT = REPO_ROOT / "src" / "code" / "win32" / "win_input.c"
WIN_NET = REPO_ROOT / "src" / "code" / "win32" / "win_net.c"
WIN_WNDPROC = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"
CL_MAIN = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_CONSOLE = REPO_ROOT / "src" / "code" / "client" / "cl_console.c"
CL_KEYS = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
CL_CIN = REPO_ROOT / "src" / "code" / "client" / "cl_cin.c"
CL_UI = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"
SND_DMA = REPO_ROOT / "src" / "code" / "client" / "snd_dma.c"
SND_MIX = REPO_ROOT / "src" / "code" / "client" / "snd_mix.c"
SV_INIT = REPO_ROOT / "src" / "code" / "server" / "sv_init.c"
SV_MAIN = REPO_ROOT / "src" / "code" / "server" / "sv_main.c"
SV_SNAPSHOT = REPO_ROOT / "src" / "code" / "server" / "sv_snapshot.c"
SV_BOT = REPO_ROOT / "src" / "code" / "server" / "sv_bot.c"
SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SV_CLIENT = REPO_ROOT / "src" / "code" / "server" / "sv_client.c"
SV_CCMDS = REPO_ROOT / "src" / "code" / "server" / "sv_ccmds.c"
CL_PARSE = REPO_ROOT / "src" / "code" / "client" / "cl_parse.c"
COMMON = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
TR_INIT = REPO_ROOT / "src" / "code" / "renderer" / "tr_init.c"
QCOMMON_CVAR = REPO_ROOT / "src" / "code" / "qcommon" / "cvar.c"
FILES = REPO_ROOT / "src" / "code" / "qcommon" / "files.c"
NET_CHAN = REPO_ROOT / "src" / "code" / "qcommon" / "net_chan.c"
UI_MAIN = REPO_ROOT / "src" / "code" / "ui" / "ui_main.c"
AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
BE_AAS_FILE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_file.c"
SERVER_H = REPO_ROOT / "src" / "code" / "server" / "server.h"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
QL_STEAM_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part01.txt"
)
QL_STEAM_HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part02.txt"
)
QL_STEAM_HLIL_PART05 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part05.txt"
)
QL_STEAM_HLIL_PART06 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part06.txt"
)
QL_STEAM_GHIDRA_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "decompile_top_functions.c"
)
QL_UI_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "uix86.all"
	/ "uix86.dll_hlil_split"
	/ "uix86.dll_hlil_part01.txt"
)
QL_UI_GHIDRA_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "uix86"
	/ "decompile_top_functions.c"
)
QL_CGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "cgamex86.dll"
	/ "cgamex86.dll_hlil_split"
	/ "cgamex86.dll_hlil_part02.txt"
)
QL_CGAME_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "cgamex86.dll"
	/ "cgamex86.dll_hlil_split"
	/ "cgamex86.dll_hlil_part01.txt"
)
QL_QAGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8", errors="ignore")


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


RETAIL_CON_CVAR_REGISTRATIONS = (
	(
		"con_background",
		'con_background = Cvar_GetBounded( "con_background", "0", "0", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		'004b4a68      sub_4cdd30(x87_r0, x87_r1, x87_r2, "con_background", U"0", U"0", U"1", 0x81800)',
	),
	(
		"con_height",
		'con_height = Cvar_GetBounded( "con_height", "0.5", "0.1", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		'004b4a7e      sub_4cdd30(x87_r3, x87_r4, x87_r5, "con_height", "0.5", "0.1", U"1", 0x81800)',
	),
	(
		"con_matchlimit",
		'con_matchlimit = Cvar_Get( "con_matchlimit", "16", 0 );',
		'004b4a94  data_165d624 = sub_4ce0d0(x87_r6, "con_matchlimit", "16", 0)',
	),
	(
		"con_noprint",
		'con_noprint = Cvar_Get( "con_noprint", "0", 0 );',
		'004b4aba  data_165d618 = sub_4ce0d0(x87_r0, "con_noprint", U"0", 0)',
	),
	(
		"con_opacity",
		'con_opacity = Cvar_GetBounded( "con_opacity", "0.9", "0.1", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		'004b4add      sub_4cdd30(x87_r2, x87_r3, x87_r4, "con_opacity", "0.9", "0.1", U"1", 0x81800)',
	),
	(
		"con_scale",
		'con_scale = Cvar_GetBounded( "con_scale", "0.5", "0.5", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		'004b4b00      sub_4cdd30(x87_r5, x87_r6, x87_r7, "con_scale", "0.5", "0.5", U"1", 0x81800)',
	),
	(
		"con_speed",
		'con_speed = Cvar_GetBounded( "con_speed", "3", "0.1", "1000", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		'004b4b19      sub_4cdd30(x87_r0, x87_r1, x87_r2, "con_speed", U"3", "0.1", "1000", 0x81800)',
	),
	(
		"con_timestamps",
		'con_timestamps = Cvar_Get( "con_timestamps", "0", CVAR_PROTECTED | CVAR_CLOUD );',
		'004b4b2b  data_16dd688 = sub_4ce0d0(x87_r3, "con_timestamps", U"0", 0x80800)',
	),
)


RETAIL_CON_CVAR_WIRING = {
	"con_background": (
		"else if ( con_background && con_background->integer > 0 ) {",
		"SCR_DrawPic( 0, 0, SCREEN_WIDTH, y, cls.consoleShader );",
	),
	"con_height": (
		"con.finalFrac = con_height ? Com_Clamp( 0.1f, 1.0f, con_height->value ) : 0.5f;",
	),
	"con_matchlimit": (
		"limit = con_matchlimit ? con_matchlimit->integer : 16;",
	),
	"con_noprint": (
		"if ( con_noprint && con_noprint->integer ) {",
	),
	"con_opacity": (
		"color[3] = con_opacity ? con_opacity->value : 0.9f;",
	),
	"con_scale": (
		"scale = con_scale->value;",
		"return Com_Clamp( 0.5f, 1.0f, scale );",
		"pixelScale = Con_GetScale() * Con_GetScreenScale();",
	),
	"con_speed": (
		"con.displayFrac -= ( con_speed ? Com_Clamp( 0.1f, 1000.0f, con_speed->value ) : 3.0f ) * cls.realFrametime * 0.001f;",
		"con.displayFrac += ( con_speed ? Com_Clamp( 0.1f, 1000.0f, con_speed->value ) : 3.0f ) * cls.realFrametime * 0.001f;",
	),
	"con_timestamps": (
		"timestampMode = con_timestamps->integer;",
		"if ( cgvm && con_timestamps && con_timestamps->integer == 1 ) {",
		"Con_FormatTimestamp( timestamp, sizeof( timestamp ) );",
	),
}


def _registered_console_con_cvars(source: str) -> list[str]:
	return [
		line.strip()
		for line in source.splitlines()
		if "Cvar_Get" in line and '"con_' in line
	]


def test_console_cvar_surface_matches_retail_hlil() -> None:
	cl_console = _read_text(CL_CONSOLE)
	hlil_registration = _read_text(QL_STEAM_HLIL_PART04)
	hlil_strings = _read_text(QL_STEAM_HLIL_PART06)

	registered = _registered_console_con_cvars(cl_console)
	hlil_con_names = sorted(
		{
			name
			for match in re.findall(r'"(con_[A-Za-z0-9_]+)"|U"(con_[A-Za-z0-9_]+)"', hlil_registration + hlil_strings)
			for name in match
			if name
		}
	)

	assert hlil_con_names == [name for name, _, _ in RETAIL_CON_CVAR_REGISTRATIONS]
	assert registered == [registration for _, registration, _ in RETAIL_CON_CVAR_REGISTRATIONS]
	for _, _, evidence in RETAIL_CON_CVAR_REGISTRATIONS:
		assert evidence in hlil_registration
	assert "con_notifytime" not in cl_console
	assert "con_notifytime" not in hlil_registration
	assert "scr_conspeed" not in "\n".join(registered)


def test_console_cvar_functional_wiring_matches_retail_hlil_surface() -> None:
	cl_console = _read_text(CL_CONSOLE)

	for cvar_name, snippets in RETAIL_CON_CVAR_WIRING.items():
		for snippet in snippets:
			assert snippet in cl_console, cvar_name

	assert cl_console.count( "color[3] = con_opacity ? con_opacity->value : 0.9f;" ) >= 2
	assert "CON_NOTIFY_TIME\t3000" in cl_console
	assert 'Cvar_Get( "con_notifytime"' not in cl_console
	assert 'Cvar_Get( "scr_conspeed"' not in cl_console


def test_engine_cvar_registrations_match_targeted_retail_contracts() -> None:
	win_glimp = _read_text(WIN_GLIMP)
	win_input = _read_text(WIN_INPUT)
	win_wndproc = _read_text(WIN_WNDPROC)
	cl_main = _read_text(CL_MAIN)
	cl_scrn = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_scrn.c")
	cl_console = _read_text(CL_CONSOLE)
	sv_init = _read_text(SV_INIT)
	sv_main = _read_text(SV_MAIN)
	sv_client = _read_text(SV_CLIENT)

	assert 'vid_xpos = Cvar_Get ("vid_xpos", "3", CVAR_ARCHIVE);' in win_wndproc
	assert 'Cvar_SetValue( "vid_xpos", xPos + r.left);' in win_wndproc
	assert 'ri.Cvar_Get( "vid_xpos", "0", CVAR_ARCHIVE );' in win_glimp
	assert 'if ( !Q_stricmp( name, "vid_xpos" ) || !Q_stricmp( name, "vid_ypos" ) ) {' in cl_main

	assert 'vid_ypos = Cvar_Get ("vid_ypos", "22", CVAR_ARCHIVE);' in win_wndproc
	assert 'Cvar_SetValue( "vid_ypos", yPos + r.top);' in win_wndproc
	assert 'ri.Cvar_Get( "vid_ypos", "0", CVAR_ARCHIVE );' in win_glimp

	assert 'cvar_t *lastValidRenderer = ri.Cvar_Get( "r_lastValidRenderer", "(uninitialized)", CVAR_ARCHIVE );' in win_glimp
	assert 'ri.Cvar_Set( "r_lastValidRenderer", glConfig.renderer_string );' in win_glimp

	assert 'r_allowSoftwareGL = ri.Cvar_Get( "r_allowSoftwareGL", "0", CVAR_LATCH );' in win_glimp
	assert 'if ( !r_allowSoftwareGL->integer )' in win_glimp

	assert 'in_mouseMode\t\t\t= Cvar_Get ("in_mouseMode",\t\t\t\t"undefined",\tCVAR_ROM | CVAR_TEMP | CVAR_CLOUD);' in win_input
	assert 'Cvar_Set( "in_mouseMode", mode );' in win_input
	assert '"win32(Raw)"' in win_input
	assert '"DirectInput"' in win_input
	assert '"win32"' in win_input

	assert 'in_raw_useWindowHandle\t= Cvar_Get ("in_raw_useWindowHandle",\t"0",\t\tCVAR_ARCHIVE);' in win_input
	assert 'in_raw_useWindowHandle && in_raw_useWindowHandle->integer' in win_input

	assert 'con_height = Cvar_GetBounded( "con_height", "0.5", "0.1", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_console
	assert 'con.finalFrac = con_height ? Com_Clamp( 0.1f, 1.0f, con_height->value ) : 0.5f;' in cl_console

	assert 'cl_demoRecordMessage = Cvar_Get ("cl_demoRecordMessage", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( !cl_demoRecordMessage || !cl_demoRecordMessage->integer ) {' in cl_scrn
	assert 'if ( cl_demoRecordMessage->integer == 1 ) {' in cl_scrn
	assert 'else if ( cl_demoRecordMessage->integer == 2 ) {' in cl_scrn
	assert 'demo: wrote' not in cl_main

	assert 'cl_platform = Cvar_Get ("cl_platform", "1", CVAR_ROM );' in cl_main

	assert 'sv_serverType = Cvar_Get ("sv_serverType", "0", CVAR_ARCHIVE );' in sv_init
	assert 'serverType = sv_serverType ? sv_serverType->integer : 0;' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetServerTypeInfoKey(), va("%i", sv_serverType->integer) );' in sv_main
	assert 'serverType = sv_serverType ? sv_serverType->integer : 0;' in sv_client


def test_engine_cvar_second_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_console = _read_text(CL_CONSOLE)
	sv_init = _read_text(SV_INIT)
	sv_client = _read_text(SV_CLIENT)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")

	assert 'con_opacity = Cvar_GetBounded( "con_opacity", "0.9", "0.1", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_console
	assert cl_console.count( 'color[3] = con_opacity ? con_opacity->value : 0.9f;' ) >= 2

	assert 'con_scale = Cvar_GetBounded( "con_scale", "0.5", "0.5", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_console
	assert 'scale = con_scale->value;' in cl_console

	assert 'con_speed = Cvar_GetBounded( "con_speed", "3", "0.1", "1000", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_console
	assert 'con.displayFrac += ( con_speed ? Com_Clamp( 0.1f, 1000.0f, con_speed->value ) : 3.0f ) * cls.realFrametime * 0.001f;' in cl_console

	assert 'con_timestamps = Cvar_Get( "con_timestamps", "0", CVAR_PROTECTED | CVAR_CLOUD );' in cl_console
	assert 'if ( cgvm && con_timestamps && con_timestamps->integer == 1 ) {' in cl_console

	assert 'cl_allowConsoleChat = Cvar_Get ("cl_allowConsoleChat", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_allowConsoleChat && cl_allowConsoleChat->integer ) {' in cl_main

	assert 'cl_timeNudge = Cvar_GetBounded( "cl_timeNudge", "0", "-20", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED );' in cl_main
	assert 'tn = cl_timeNudge->integer;' in cl_cgame

	assert 'cl_autoTimeNudge = Cvar_GetBounded( "cl_autoTimeNudge", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED );' in cl_main
	assert 'Cvar_Get( "cg_spectating", "0", CVAR_ROM );' in cl_main
	assert 'static int cl_autoTimeNudgePrevious;' in cl_cgame
	assert 'static int CL_SelectClientTimeNudge( void ) {' in cl_cgame
	assert 'if ( Cvar_VariableIntegerValue( "cg_spectating" ) ) {' in cl_cgame
	assert 'else if ( Sys_IsLANAddress( clc.serverAddress ) ) {' in cl_cgame
	assert 'else if ( !cl_autoTimeNudge->integer ) {' in cl_cgame
	assert 'tn = (int)( (float)cl.snap.ping * -0.5f );' in cl_cgame
	assert 'if ( cl_autoTimeNudgePrevious != 0 && cl_autoTimeNudgePrevious != tn ) {' in cl_cgame
	assert 'cl_autoTimeNudgePrevious = tn;' in cl_cgame
	assert 'tn = CL_SelectClientTimeNudge();' in cl_cgame

	assert 'cl_maxpackets = Cvar_Get ("cl_maxpackets", "125", CVAR_CHEAT );' in cl_main
	assert 'if ( cl_maxpackets->integer < 15 ) {' in cl_input
	assert 'Cvar_Set( "cl_maxpackets", "125" );' in cl_input

	assert 'cl_mouseAccelOffset = Cvar_Get ("cl_mouseAccelOffset", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl_mouseAccelOffset->value' in cl_input

	assert 'sv_floodProtect = Cvar_Get ("sv_floodProtect", "10", CVAR_ARCHIVE );' in sv_init
	assert 'sv_floodProtect->integer &&' in sv_client

	assert 'Cvar_GetBounded( "rate", "25000", "8000", "25000", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_LATCH | CVAR_VM_CREATED );' in cl_main
	assert 'Cvar_GetBounded( "color1", "7", "1", "26", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_main
	assert 'Cvar_GetBounded( "color2", "25", "1", "26", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_main


def test_engine_cvar_third_server_tranche_matches_retail_contracts() -> None:
	sv_init = _read_text(SV_INIT)
	sv_main = _read_text(SV_MAIN)
	sv_client = _read_text(SV_CLIENT)
	sv_ccmds = _read_text(SV_CCMDS)
	cl_parse = _read_text(CL_PARSE)

	assert 'Cvar_Get ("protocol", va("%i", NET_ProtocolVersion()), CVAR_SERVERINFO | CVAR_ROM);' in sv_init
	assert 'version = atoi( Info_ValueForKey( userinfo, NET_GetProtocolInfoKey() ) );' in sv_client
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s\\nServer uses protocol version %i.\\n", NET_GetPrintCommand(), NET_ProtocolVersion() );' in sv_client
	assert 'Info_SetValueForKey( infostring, NET_GetProtocolInfoKey(), va("%i", NET_ProtocolVersion()) );' in sv_main

	assert 'sv_mapname = Cvar_Get ("mapname", "nomap", CVAR_SERVERINFO | CVAR_ROM);' in sv_init
	assert 'Cvar_Set( "mapname", server );' in sv_init
	assert 'Info_SetValueForKey( infostring, NET_GetMapnameInfoKey(), sv_mapname->string );' in sv_main

	assert 'sv_privateClients = Cvar_Get ("sv_privateClients", "0", CVAR_SERVERINFO);' in sv_init
	assert 'startIndex = sv_privateClients->integer;' in sv_client
	assert 'sv_maxclients->integer - sv_privateClients->integer' in sv_main

	assert 'sv_maxclients = Cvar_Get ("sv_maxclients", "8", CVAR_SERVERINFO | CVAR_LATCH);' in sv_init
	assert 'if ( !QL_Steamworks_ServerSetMaxPlayerCount( sv_maxclients ? sv_maxclients->integer : 0 ) ) {' in sv_main
	assert 'svs.clients = Z_Malloc (sizeof(client_t) * sv_maxclients->integer );' in sv_init

	assert 'Cvar_Get ("sv_cheats", "1", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'if ( Cvar_VariableIntegerValue( "sv_cheats" ) ) {' in sv_main
	assert 'SV_SteamServerAppendGameTag( tags, size, "cheats" );' in sv_main

	assert 'sv_serverid = Cvar_Get ("sv_serverid", "0", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_serverid", va("%i", sv.serverId ) );' in sv_init
	assert 'Cvar_Set( "sv_serverid", va("%i", sv.serverId ) );' in sv_ccmds
	assert 'cl.serverId = atoi( Info_ValueForKey( systemInfo, NET_GetServerIdInfoKey() ) );' in cl_parse

	assert 'sv_pure = Cvar_Get ("sv_pure", "1", CVAR_SYSTEMINFO | CVAR_INIT );' in sv_init
	assert 'if ( sv_pure->integer ) {' in sv_init
	assert 'if ( sv_pure->integer != 0 ) {' in sv_client
	assert 'cl_connectedToPureServer = Cvar_VariableValue( NET_GetSystemPureInfoKey() );' in cl_parse

	assert 'sv_privatePassword = Cvar_Get ("sv_privatePassword", "", CVAR_TEMP );' in sv_init
	assert 'password = Info_ValueForKey( userinfo, NET_GetPasswordInfoKey() );' in sv_client
	assert 'if ( !strcmp( password, sv_privatePassword->string ) ) {' in sv_client

	assert 'sv_fps = Cvar_Get ("sv_fps", "40", CVAR_ROM );' in sv_init
	assert 'if ( sv_fps->integer < 1 ) {' in sv_main
	assert 'frameMsec = 1000 / sv_fps->integer ;' in sv_main

	assert 'sv_timeout = Cvar_Get ("sv_timeout", "40", CVAR_TEMP );' in sv_init
	assert 'droppoint = svs.time - 1000 * sv_timeout->integer;' in sv_main


def test_engine_cvar_fourth_server_tranche_matches_retail_contracts() -> None:
	cl_cin = _read_text(CL_CIN)
	cl_main = _read_text(CL_MAIN)
	sv_init = _read_text(SV_INIT)
	sv_main = _read_text(SV_MAIN)
	sv_snapshot = _read_text(SV_SNAPSHOT)
	sv_game = _read_text(SV_GAME)
	sv_client = _read_text(SV_CLIENT)
	common = _read_text(COMMON)

	assert 'Cvar_Get ("nextmap", "", CVAR_TEMP );' in sv_init
	assert 'Cvar_Set( "nextmap", "map_restart 0");' in sv_init
	assert 'Cbuf_AddText( "vstr nextmap\\n" );' in sv_main
	assert 'Cvar_Set( "nextmap", "cinematic intro.RoQ" );' in common
	assert 's = Cvar_VariableString( "nextmap" );' in cl_cin

	assert 'sv_reconnectlimit = Cvar_Get ("sv_reconnectlimit", "3", 0);' in sv_init
	assert '< (sv_reconnectlimit->integer * 1000)) {' in sv_client

	assert 'sv_padPackets = Cvar_GetBounded( "sv_padPackets", "0", "0", "0", CVAR_VM_CREATED );' in sv_init
	assert 'if ( sv_padPackets->integer ) {' in sv_snapshot
	assert 'MSG_WriteByte (msg, svc_nop);' in sv_snapshot

	assert 'sv_killserver = Cvar_Get ("sv_killserver", "0", 0);' in sv_init
	assert 'Cvar_Set( "sv_killserver", "1" );' in cl_main
	assert 'if ( sv_killserver->integer ) {' in sv_main
	assert 'if ( !com_sv_running->integer || ( sv_killserver && sv_killserver->integer ) ) {' in common

	assert 'sv_lanForceRate = Cvar_Get ("sv_lanForceRate", "1", CVAR_ARCHIVE );' in sv_init
	assert 'if ( client->netchan.remoteAddress.type == NA_LOOPBACK || (sv_lanForceRate->integer && Sys_IsLANAddress (client->netchan.remoteAddress)) ) {' in sv_snapshot
	assert 'if ( Sys_IsLANAddress( cl->netchan.remoteAddress ) && com_dedicated->integer != 2 && sv_lanForceRate->integer == 1) {' in sv_client

	assert 'sv_idleExit = Cvar_Get ("sv_idleExit", "120", 0 );' in sv_init
	assert 'if ( !sv_idleExit || sv_idleExit->integer <= 0 ) {' in sv_main
	assert 's_svIdleExitDeadline = currentTime + sv_idleExit->integer * 1000;' in sv_main
	assert 'SV_CheckIdleServerExit( Sys_Milliseconds() );' in common

	assert 'sv_errorExit = Cvar_Get ("sv_errorExit", "1", 0 );' in sv_init
	assert 'if ( !sv_errorExit ) {' in sv_main
	assert 'if ( sv_errorExit->integer == 2 || ( sv_errorExit->integer == 1 && com_sv_running && com_sv_running->integer ) ) {' in sv_main

	assert 'sv_quitOnExitLevel = Cvar_Get ("sv_quitOnExitLevel", "0", 0 );' in sv_init
	assert 'if ( !sv_quitOnExitLevel || !sv_quitOnExitLevel->integer ) {' in sv_main
	assert 'Com_Quit_f();' in sv_main
	assert 'SV_Shutdown( "Server quit on exit level\\n" );' in sv_main

	assert 'sv_altEntDir = Cvar_Get ("sv_altEntDir", "", 0 );' in sv_init
	assert 'if ( sv_altEntDir && sv_altEntDir->string[0] ) {' in sv_game
	assert 'Com_sprintf( altEntPath, sizeof( altEntPath ), "%s/%s.ent", sv_altEntDir->string, mapName );' in sv_game

	assert 'sv_dumpEntities = Cvar_Get ("sv_dumpEntities", "0", 0 );' in sv_init
	assert 'if ( sv_dumpEntities && sv_dumpEntities->integer > 0 ) {' in sv_game
	assert 'FS_WriteFile( dumpPath, entityString, (int)strlen( entityString ) );' in sv_game


def test_engine_cvar_fifth_server_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_parse = _read_text(CL_PARSE)
	sv_init = _read_text(SV_INIT)
	sv_main = _read_text(SV_MAIN)
	files = _read_text(FILES)
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	ai_main = _read_text(AI_MAIN)
	be_aas_file = _read_text(BE_AAS_FILE)
	server_h = _read_text(SERVER_H)
	qcommon_cm_trace = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "cm_trace.c")
	referenced_sums_block = _extract_function_block(files, "const char *FS_ReferencedPakChecksums( void ) {")
	referenced_names_block = _extract_function_block(files, "const char *FS_ReferencedPakNames( void ) {")

	assert 'Cvar_Get ("sv_paks", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_paks", p );' in sv_init
	assert 'Cvar_Set( "sv_paks", "" );' in sv_init
	assert 's = Info_ValueForKey( systemInfo, NET_GetPaksInfoKey() );' in cl_parse
	assert 'FS_PureServerSetLoadedPaks( s, t );' in cl_parse

	assert 'Cvar_Get ("sv_pakNames", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_pakNames", p );' in sv_init
	assert 'Cvar_Set( "sv_pakNames", "" );' in sv_init
	assert 't = Info_ValueForKey( systemInfo, NET_GetPakNamesInfoKey() );' in cl_parse
	assert 'void FS_PureServerSetLoadedPaks( const char *pakSums, const char *pakNames ) {' in files

	assert 'Cvar_Get ("sv_referencedPaks", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_referencedPaks", p );' in sv_init
	assert 's = Info_ValueForKey( systemInfo, NET_GetReferencedPaksInfoKey() );' in cl_parse
	assert 'FS_PureServerSetReferencedPaks( s, t );' in cl_parse

	assert 'Cvar_Get ("sv_referencedPakNames", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_referencedPakNames", p );' in sv_init
	assert 't = Info_ValueForKey( systemInfo, NET_GetReferencedPakNamesInfoKey() );' in cl_parse
	assert 'void FS_PureServerSetReferencedPaks( const char *pakSums, const char *pakNames ) {' in files
	assert "if ( search->pack->referenced )" in referenced_sums_block
	assert "if ( search->pack->referenced )" in referenced_names_block
	assert "Q_stricmpn(search->pack->pakGamename" not in referenced_sums_block
	assert "Q_stricmpn(search->pack->pakGamename" not in referenced_names_block
	assert "004d1de0      if (eax_1 != 0 && *(eax_1 + 0x310) != 0)" in retail_hlil
	assert "004d1e62          if (*(eax_1 + 0x310) != 0)" in retail_hlil

	assert 'Cvar_Get ("sv_referencedSteamworks", "", CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_referencedSteamworks", referencedSteamworks );' in sv_init
	assert 'SV_SetConfigstring( 0x2cb, referencedSteamworks );' in sv_init
	assert '#define CL_STEAM_WORKSHOP_ITEMS_CONFIGSTRING 0x2cb' in cl_main
	assert 'requiredItems = CL_GetConfigStringValue( CL_STEAM_WORKSHOP_ITEMS_CONFIGSTRING );' in cl_main

	assert 'sv_zombietime = Cvar_Get ("sv_zombietime", "2", CVAR_TEMP );' in sv_init
	assert 'zombiepoint = svs.time - 1000 * sv_zombietime->integer;' in sv_main

	assert 'sv_mapChecksum = Cvar_Get ("sv_mapChecksum", "", CVAR_ROM);' in sv_init
	assert 'Cvar_Set( "sv_mapChecksum", va("%i",checksum) );' in sv_init
	assert 'trap_Cvar_VariableStringBuffer("sv_mapChecksum", buf, sizeof(buf));' in ai_main
	assert 'aasworld.bspchecksum = atoi(LibVarGetString( "sv_mapChecksum"));' in be_aas_file

	assert 'sv_tags = Cvar_Get ("sv_tags", "", CVAR_ARCHIVE );' in sv_init
	assert 'if ( sv_tags && sv_tags->string[0] ) {' in sv_main
	assert 'Q_strncpyz( tagCustom, sv_tags->string, sizeof( tagCustom ) );' in sv_main

	assert 'sv_cylinderScale = Cvar_Get ("sv_cylinderScale", "1.1f", 0 );' in sv_init
	assert 'radius *= Cvar_Get( "sv_cylinderScale", "1.1f", 0 )->value;' in qcommon_cm_trace

	assert 'sv_showloss = Cvar_Get ("sv_showloss", "0", 0);' in sv_init
	assert 'cvar_t\t*sv_showloss;' in sv_main
	assert 'extern\tcvar_t\t*sv_showloss;' in server_h


def test_engine_cvar_sixth_client_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_console = _read_text(CL_CONSOLE)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	win_input = _read_text(WIN_INPUT)
	common = _read_text(COMMON)
	cmd = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "cmd.c")

	assert 'con_background = Cvar_GetBounded( "con_background", "0", "0", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_console
	assert 'else if ( con_background && con_background->integer > 0 ) {' in cl_console

	assert 'con_matchlimit = Cvar_Get( "con_matchlimit", "16", 0 );' in cl_console
	assert 'limit = con_matchlimit ? con_matchlimit->integer : 16;' in cl_console

	assert 'con_noprint = Cvar_Get( "con_noprint", "0", 0 );' in cl_console
	assert 'if ( con_noprint && con_noprint->integer ) {' in cl_console

	assert 'cl_timeout = Cvar_Get ("cl_timeout", "40", 0);' in cl_main
	assert 'cls.realtime - clc.lastPacketTime > cl_timeout->value*1000' in cl_main

	assert 'cl_packetdup = Cvar_Get ("cl_packetdup", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_packetdup->integer < 0 ) {' in cl_input
	assert 'Cvar_Set( "cl_packetdup", "5" );' in cl_input
	assert 'oldPacketNum = (clc.netchan.outgoingSequence - 1 - cl_packetdup->integer) & PACKET_MASK;' in cl_input

	assert 'cl_quitOnDemoCompleted = Cvar_Get ("cl_quitOnDemoCompleted", "0", 0 );' in cl_main
	assert 'cvar_t\t*cl_quitOnDemoCompleted;' in cl_main
	assert "if ( cl_quitOnDemoCompleted && cl_quitOnDemoCompleted->integer ) {" in cl_main
	assert 'Cbuf_AddText( "quit\\n" );' in cl_main

	assert 'cl_run = Cvar_Get ("cl_run", "1", CVAR_ARCHIVE);' in cl_main
	assert 'if ( in_speed.active ^ cl_run->integer ) {' in cl_input

	assert 'cl_viewAccel = Cvar_Get ("cl_viewAccel", "1.7", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'accel = cl_viewAccel ? cl_viewAccel->value : 1.0f;' in win_input
	assert 'cl.viewangles[YAW] -= cl_viewAccel->value * m_yaw->value * mx;' not in cl_input
	assert 'cl.viewangles[PITCH] += cl_viewAccel->value * m_pitch->value * my;' not in cl_input

	assert 'cl_serverStatusResendTime = Cvar_Get ("cl_serverStatusResendTime", "750", 0);' in cl_main
	assert 'serverStatus->startTime < Com_Milliseconds() - cl_serverStatusResendTime->integer' in cl_main

	assert 'com_cl_running = Cvar_Get ("cl_running", "0", CVAR_ROM);' in common
	assert 'Cvar_Set( "cl_running", "1" );' in cl_main
	assert 'Cvar_Set( "cl_running", "0" );' in cl_main
	assert 'if ( com_cl_running && com_cl_running->integer && CL_GameCommand() ) {' in cmd
	assert 'if ( com_cl_running && com_cl_running->integer && UI_GameCommand() ) {' in cmd


def test_engine_cvar_seventh_client_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_parse = _read_text(CL_PARSE)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	msg = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "msg.c")

	assert 'cl_avidemo = Cvar_Get ("cl_avidemo", "0", 0);' in cl_main
	assert 'if ( cl_avidemo->integer && msec) {' in cl_main
	assert 'msec = (1000 / cl_avidemo->integer) * com_timescale->value;' in cl_main

	assert 'cl_avidemo_latch = Cvar_Get ("cl_avidemo_latch", "0", 0 );' in cl_main
	assert 'if ( cl_avidemo_latch->integer ) {' in cl_main
	assert 'Cvar_SetValue( "cl_avidemo", cl_avidemo_latch->integer );' in cl_main
	assert 'Cvar_Set( "cl_avidemo_latch", "0" );' in cl_main

	assert 'cl_avidemo_mintime = Cvar_Get ("cl_avidemo_mintime", "0", 0 );' in cl_main
	assert 'if ( !cl_avidemo_mintime->integer || cl.serverTime > cl_avidemo_mintime->integer ) {' in cl_main
	assert 'if ( !cl_avidemo_mintime->integer || cl.serverTime >= cl_avidemo_mintime->integer ) {' in cl_main

	assert 'cl_avidemo_maxtime = Cvar_Get ("cl_avidemo_maxtime", "0", 0 );' in cl_main
	assert 'if ( cl_avidemo_maxtime->integer && cl.serverTime > cl_avidemo_maxtime->integer ) {' in cl_main
	assert 'CL_Disconnect_f();' in cl_main

	assert 'cl_forceavidemo = Cvar_Get ("cl_forceavidemo", "0", 0);' in cl_main
	assert 'if ( cls.state == CA_ACTIVE || cl_forceavidemo->integer) {' in cl_main

	assert 'cl_motd = Cvar_Get ("cl_motd", "1", 0);' in cl_main
	assert 'if ( !cl_motd->integer ) {' in cl_main

	assert 'cl_motdString = Cvar_Get( "cl_motdString", "", CVAR_ROM );' in cl_main
	assert 'Cvar_Set( "cl_motdString", challenge );' in cl_main

	assert 'cl_shownet = Cvar_Get ("cl_shownet", "0", CVAR_TEMP );' in cl_main
	assert 'if ( cl_shownet->integer >= 2) {' in cl_parse
	assert 'cl_shownet->integer == 4' in msg
	assert 'cl_shownet->integer >= 2 || cl_shownet->integer == -1' in msg

	assert 'cl_showSend = Cvar_Get ("cl_showSend", "0", CVAR_TEMP );' in cl_main
	assert 'if ( cl_showSend->integer ) {' in cl_input

	assert 'cl_showTimeDelta = Cvar_Get ("cl_showTimeDelta", "0", CVAR_TEMP );' in cl_main
	assert 'if ( cl_showTimeDelta->integer ) {' in cl_cgame


def test_engine_cvar_eighth_client_input_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")

	assert 'cl_anglespeedkey = Cvar_Get ("cl_anglespeedkey", "1.5", CVAR_CHEAT );' in cl_main
	assert 'speed = 0.001 * cls.frametime * cl_anglespeedkey->value;' in cl_input
	assert 'anglespeed = 0.001 * cls.frametime * cl_anglespeedkey->value;' in cl_input

	assert 'cl_yawspeed = Cvar_Get ("cl_yawspeed", "140", CVAR_CHEAT );' in cl_main
	assert 'cl.viewangles[YAW] -= speed*cl_yawspeed->value*CL_KeyState (&in_right);' in cl_input
	assert 'cl.viewangles[YAW] += anglespeed * cl_yawspeed->value * cl.joystickAxis[AXIS_SIDE];' in cl_input

	assert 'cl_pitchspeed = Cvar_Get ("cl_pitchspeed", "140", CVAR_CHEAT );' in cl_main
	assert 'cl.viewangles[PITCH] -= speed*cl_pitchspeed->value * CL_KeyState (&in_lookup);' in cl_input
	assert 'cl.viewangles[PITCH] += anglespeed * cl_pitchspeed->value * cl.joystickAxis[AXIS_FORWARD];' in cl_input

	assert 'cl_freelook = Cvar_Get( "cl_freelook", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( !cl_freelook->integer ) {' in cl_input
	assert 'if ( (in_mlooking || cl_freelook->integer) && !in_strafe.active ) {' in cl_input

	assert 'cl_sensitivity = Cvar_Get ("sensitivity", "4", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'sensitivity = cl_sensitivity->value;' in cl_input

	assert 'cl_mouseAccel = Cvar_Get ("cl_mouseAccel", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_mouseAccel->value != 0.0f ) {' in cl_input
	assert 'accelRate = fabsf( cl_mouseAccel->value ) * rate;' in cl_input
	assert 'accelSensitivity = powf( accelRate, power );' in cl_input
	assert 'sensitivity -= accelSensitivity;' in cl_input
	assert 'sensitivity += accelSensitivity;' in cl_input

	assert 'cl_mouseAccelPower = Cvar_Get ("cl_mouseAccelPower", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'power = cl_mouseAccelPower->value - 1.0f;' in cl_input

	assert 'cl_mouseSensCap = Cvar_Get ("cl_mouseSensCap", "0", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_mouseSensCap->value > 0.0f && cl_mouseSensCap->value < sensitivity ) {' in cl_input

	assert 'm_filter = Cvar_Get ("m_filter", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'static void CL_BeginMouseFilter( void ) {' in cl_input
	assert 'Cvar_Set( "m_filter", "31" );' in cl_input
	assert 'CL_EndMouseFilter();' in cl_input

	assert 'm_cpi = Cvar_Get ("m_cpi", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cpiScale = m_cpi->value / CL_MOUSE_CPI_INCHES_PER_CM;' in cl_input
	assert 'rate *= 1000.0f;' in cl_input
	assert 'translatedDx = CL_TranslateRetailMouseDelta( dx, m_cpi->value );' not in cl_input
	assert 'Cvar_Get( "cg_ignoreMouseInput", "0", CVAR_ROM );' in cl_main
	assert 'if ( Cvar_VariableIntegerValue( "cg_ignoreMouseInput" ) ) {' in cl_input


def test_engine_cvar_ninth_client_misc_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_cin = _read_text(CL_CIN)
	tr_init = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_init.c")

	assert 'cl_activeAction = Cvar_Get( "activeAction", "", CVAR_TEMP );' in cl_main
	assert 'if ( cl_activeAction->string[0] ) {' in cl_cgame
	assert 'Cbuf_AddText( cl_activeAction->string );' in cl_cgame
	assert 'Cvar_Set( "activeAction", "" );' in cl_cgame

	assert 'cl_inGameVideo = Cvar_Get ("r_inGameVideo", "1", CVAR_ARCHIVE);' in cl_main
	assert 'r_inGameVideo = ri.Cvar_Get( "r_inGameVideo", "1", CVAR_ARCHIVE );' in tr_init
	assert 'cinTable[currentHandle].playonwalls = cl_inGameVideo->integer;' in cl_cin
	assert 'if (cl_inGameVideo->integer == 0 && cinTable[handle].playonwalls == 1) {' in cl_cin

	assert 'm_forward = Cvar_Get ("m_forward", "0.25", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'cmd->forwardmove = ClampChar( cmd->forwardmove - m_forward->value * my );' in cl_input

	assert 'm_pitch = Cvar_Get ("m_pitch", "0.022", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl.viewangles[PITCH] += m_pitch->value * mouseScale * my;' in cl_input

	assert 'm_side = Cvar_Get ("m_side", "0.25", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'cmd->rightmove = ClampChar( cmd->rightmove + m_side->value * mx );' in cl_input

	assert 'm_yaw = Cvar_Get ("m_yaw", "0.022", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl.viewangles[YAW] -= m_yaw->value * mouseScale * mx;' in cl_input

	assert 'Cvar_Get( "cl_maxPing", "800", CVAR_ARCHIVE );' in cl_main
	assert 'maxPing = Cvar_VariableIntegerValue( "cl_maxPing" );' in cl_main
	assert 'if( maxPing < 100 ) {' in cl_main

	assert 'Cvar_Get ("name", "UnnamedPlayer", CVAR_USERINFO | CVAR_ROM );' in cl_main
	assert 'Cvar_Set( "name", personaName );' in cl_main
	assert 'Cvar_Set( "name", "anon" );' in cl_main

	assert 'Cvar_Get ("country", "", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'Cvar_VariableStringBuffer( "country", country, sizeof( country ) );' in cl_main
	assert 'Cvar_Set( "country", country );' in cl_main
	assert 'SteamClient_SyncPersonaNameCvar();' in cl_main
	assert 'CL_Steam_SeedCountryCvar();' in cl_main

	assert 'Cvar_Get ("model", "sarge", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );' in cl_main
	assert 'void CL_SetModel_f( void ) {' in cl_main
	assert 'Cvar_Set( "model", arg );' in cl_main
	assert 'Cmd_AddCommand ("model", CL_SetModel_f );' in cl_main


def test_engine_cvar_tenth_client_userinfo_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cg_main = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c")
	cg_predict = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c")
	cg_view = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c")
	cg_players = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c")
	cg_consolecmds = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c")
	g_client = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_client.c")
	sv_client = _read_text(SV_CLIENT)
	cvar = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "cvar.c")

	assert 'Cvar_Get ("cl_anonymous", "0", CVAR_USERINFO | CVAR_ARCHIVE );' in cl_main
	assert 'Cvar_VariableIntegerValue( "cl_anonymous" )' in cl_main
	assert 'Cvar_Get ("cl_anonymous", "0", CVAR_INIT|CVAR_SYSTEMINFO );' not in cl_main

	assert 'Cvar_Get ("cg_autoAction", "", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert '{ &cg_autoAction, "cg_autoAction", "3", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "3" },' in cg_main
	assert 'cg.autoActionFlags = cg_autoAction.integer;' in cg_main
	assert 'flags = cg.autoActionFlags;' in cg_main

	assert 'Cvar_Get ("cg_autoHop", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert '{ &cg_autoHop, "cg_autoHop", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD, "0", "1" },' in cg_main
	assert 'cg.autoHopEnabled = (qboolean)( cg_autoHop.integer != 0 );' in cg_main
	assert 'cg.predictedPlayerState.pm_flags &= ~PMF_REQUIRE_JUMP_RELEASE;' in cg_predict
	assert 'cg.predictedPlayerState.pm_flags |= PMF_REQUIRE_JUMP_RELEASE;' in cg_predict
	assert 's = Info_ValueForKey( userinfo, "cg_autoHop" );' in g_client
	assert 'client->ps.pm_flags |= PMF_REQUIRE_JUMP_RELEASE;' in g_client
	assert 'client->ps.pm_flags &= ~PMF_REQUIRE_JUMP_RELEASE;' in g_client

	assert 'Cvar_Get ("cg_predictItems", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert '{ &cg_predictItems, "cg_predictItems", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD },' in cg_main
	assert 'if ( !cg_predictItems.integer ) {' in cg_predict
	assert 's = Info_ValueForKey( userinfo, "cg_predictItems" );' in g_client

	assert 'Cvar_Get ("cg_viewsize", "100", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert '{ &cg_viewsize, "cg_viewsize", "100", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "30", "100" },' in cg_main
	assert 'if (cg_viewsize.integer < 30) {' in cg_view
	assert 'trap_Cvar_Set("cg_viewsize", va("%i",(int)(cg_viewsize.integer+10)));' in cg_consolecmds

	assert 'Cvar_Get ("handicap", "100", CVAR_USERINFO | CVAR_TEMP );' in cl_main
	assert 'health = atoi( Info_ValueForKey( userinfo, "handicap" ) );' in g_client
	assert 'val = Info_ValueForKey (cl->userinfo, NET_GetHandicapInfoKey());' in sv_client
	assert 'Info_SetValueForKey( cl->userinfo, NET_GetHandicapInfoKey(), "100" );' in sv_client

	assert 'Cvar_Get ("headmodel", "sarge", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );' in cl_main
	assert 'Cvar_Set( "headmodel", arg );' in cl_main
	assert 'trap_Cvar_Register(NULL, "headmodel", DEFAULT_HEAD, CVAR_USERINFO | CVAR_ARCHIVE );' in cg_main
	assert 'trap_Cvar_Register(NULL, "fov", "", CVAR_USERINFO | CVAR_ROM );' in cg_main
	assert 'Q_strncpyz( headModel, Info_ValueForKey (userinfo, "headmodel"), sizeof( headModel ) );' in g_client

	assert 'Cvar_Get ("password", "", CVAR_USERINFO | CVAR_TEMP);' in cl_main
	assert 'Cvar_Set( "password", password );' in cl_main
	assert 'value = Info_ValueForKey (userinfo, "password");' in g_client
	assert 'password = Info_ValueForKey( userinfo, NET_GetPasswordInfoKey() );' in sv_client
	assert 'if ( !Q_stricmp( var->name, "cl_cdkey" ) || !Q_stricmp( var->name, "password" ) ) {' in cvar

	assert 'Cvar_Get ("sex", "male", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );' in cl_main
	assert '} else if ( !Q_stricmp( token, "sex" ) ) {' in cg_players
	assert 'ci->gender = GENDER_FEMALE;' in cg_players

	assert 'Cvar_Get ("teamtask", "0", CVAR_USERINFO | CVAR_PROTECTED );' in cl_main
	assert 'teamTask = atoi(Info_ValueForKey(userinfo, "teamtask"));' in g_client
	assert 'trap_SendClientCommand( va( "teamtask %d\\n", cgs.acceptTask ) );' in cg_consolecmds


def test_engine_cvar_early_cgame_preinit_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cg_main = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c")
	cg_event = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c")
	cg_predict = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c")

	assert 'Cvar_GetBounded( "cg_autoswitch", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_main
	assert 'Cvar_Get ("cg_autoswitch", "1", CVAR_ARCHIVE);' not in cl_main
	assert '{ &cg_autoswitch, "cg_autoswitch", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },' in cg_main
	assert "if ( cg_autoswitch.integer && weapon != WP_MACHINEGUN ) {" in cg_event

	assert '{ &cg_autoProjectileNudge, "cg_autoProjectileNudge", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },' in cg_main
	assert "cg.autoProjectileNudgeEnabled = (qboolean)( cg_autoProjectileNudge.integer != 0 );" in cg_main
	assert "if ( cg.autoProjectileNudgeEnabled && cg.snap ) {" in cg_predict


def test_engine_cvar_eleventh_common_tranche_matches_retail_contracts() -> None:
	common = _read_text(COMMON)

	assert 'com_maxfps = Cvar_GetBounded( "com_maxfps", "125", "30", "250", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD );' in common
	assert 'if ( !com_dedicated->integer && com_maxfps->integer > 0 && !com_timedemo->integer ) {' in common
	assert 'minMsec = 1000 / com_maxfps->integer;' in common

	assert 'com_developer = Cvar_Get( "developer", "0", CVAR_TEMP );' in common
	assert 'com_developer = Cvar_Get ("developer", "0", CVAR_TEMP );' in common
	assert 'Com_StartupVariable( "developer" );' in common
	assert 'if ( !com_developer || !com_developer->integer ) {' in common
	assert 'if ( com_developer && com_developer->integer ) {' in common

	assert 'com_logfile = Cvar_Get( "logfile", "0", CVAR_TEMP );' in common
	assert 'com_logfile = Cvar_Get ("logfile", "0", CVAR_TEMP );' in common
	assert 'Com_StartupVariable( "logfile" );' in common
	assert 'if ( com_logfile && com_logfile->integer ) {' in common
	assert 'if ( com_logfile->integer > 1 ) {' in common

	assert common.count('com_appendlogfile = Cvar_Get( "appendlogfile", "0", CVAR_TEMP );') == 2
	assert 'Com_StartupVariable( "appendlogfile" );' in common
	assert 'if ( com_appendlogfile && com_appendlogfile->integer ) {' in common
	assert 'logfile = FS_FOpenFileAppend( "qconsole.log" );' in common
	assert 'logfile = FS_FOpenFileWrite( "qconsole.log" );' in common

	assert 'com_timescale = Cvar_Get ("timescale", "1", CVAR_CHEAT | CVAR_SYSTEMINFO );' in common
	assert '} else if ( com_timescale->value ) {' in common
	assert 'msec *= com_timescale->value;' in common
	assert 'if ( msec < 1 && com_timescale->value) {' in common

	assert 'com_fixedtime = Cvar_Get ("fixedtime", "0", CVAR_CHEAT);' in common
	assert 'if ( com_fixedtime->integer ) {' in common
	assert 'msec = com_fixedtime->integer;' in common

	assert 'com_showtrace = Cvar_Get ("com_showtrace", "0", CVAR_CHEAT);' in common
	assert 'if ( com_showtrace->integer ) {' in common
	assert 'Com_Printf ("%4i traces  (%ib %ip) %4i points\\n", c_traces,' in common

	assert 'com_dropsim = Cvar_Get ("com_dropsim", "0", CVAR_CHEAT);' in common
	assert 'if ( com_dropsim->value > 0 ) {' in common
	assert 'if ( Q_random( &seed ) < com_dropsim->value ) {' in common

	assert 'com_viewlog = Cvar_Get( "viewlog", "0", CVAR_CHEAT );' in common
	assert 'Cvar_Set( "viewlog", "1" );' in common
	assert 'if ( com_viewlog->modified ) {' in common
	assert 'Sys_ShowConsole( com_viewlog->integer, qfalse );' in common

	assert 'com_speeds = Cvar_Get ("com_speeds", "0", 0);' in common
	assert 'if ( com_speeds->integer ) {' in common
	assert 'Com_Printf ("frame:%i all:%3i sv:%3i ev:%3i cl:%3i gm:%3i rf:%3i bk:%3i\\n",' in common


def test_engine_cvar_twelfth_common_misc_tranche_matches_retail_contracts() -> None:
	common = _read_text(COMMON)
	cl_main = _read_text(CL_MAIN)
	cl_console = _read_text(CL_CONSOLE)
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	cl_keys = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_keys.c")
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_parse = _read_text(CL_PARSE)
	cg_main = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c")
	cg_local = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h")
	cg_players = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c")
	cg_servercmds = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c")
	cg_draw = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c")
	g_main = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_main.c")
	g_rankings = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_rankings.c")
	sv_init = _read_text(SV_INIT)
	sv_main = _read_text(SV_MAIN)

	assert 'com_timedemo = Cvar_Get ("timedemo", "0", CVAR_CHEAT);' in common
	assert 'cl_timedemo = Cvar_Get ("timedemo", "0", 0);' in cl_main
	assert 'if ( !com_dedicated->integer && com_maxfps->integer > 0 && !com_timedemo->integer ) {' in common
	assert 'if ( cl_timedemo->integer ) {' in cl_cgame
	assert 'cl.serverTime = clc.timeDemoBaseTime + clc.timeDemoFrames * 50;' in cl_cgame

	assert 'com_cameraMode = Cvar_Get ("com_cameraMode", "0", CVAR_CHEAT);' in common
	assert '{ &cg_cameraMode, "com_cameraMode", "0", CVAR_CHEAT},' in cg_main
	assert '} else if (com_cameraMode->integer) {' in common
	assert 'if (Cvar_VariableValue ("com_cameraMode") == 0) {' in cl_keys

	assert 'cl_paused = Cvar_Get ("cl_paused", "0", CVAR_ROM);' in common
	assert 'Cvar_Set( "cl_paused", "0" );' in cl_main
	assert 'Cvar_Set( "cl_paused", "0" );' in cl_parse
	assert 'if ( com_sv_running->integer && sv_paused->integer && cl_paused->integer ) {' in cl_input
	assert 'if ( sv_paused->integer && cl_paused->integer && com_sv_running->integer ) {' in cl_cgame

	assert 'sv_paused = Cvar_Get ("sv_paused", "0", CVAR_ROM);' in common
	assert 'if (sv_paused->integer)' in sv_main
	assert 'Cvar_Set("sv_paused", "0");' in sv_main
	assert 'if (!sv_paused->integer)' in sv_main
	assert 'Cvar_Set("sv_paused", "1");' in sv_main

	assert 'com_sv_running = Cvar_Get ("sv_running", "0", CVAR_ROM);' in common
	assert 'Cvar_Set( "sv_running", "1" );' in sv_init
	assert 'Cvar_Set( "sv_running", "0" );' in sv_init
	assert 'if ( !com_sv_running->integer ) {' in common
	assert 'trap_Cvar_VariableStringBuffer( "sv_running", var, sizeof( var ) );' in cg_main

	assert 'com_allowConsole = Cvar_Get( "com_allowConsole", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in common
	assert 'if ( com_allowConsole && !com_allowConsole->integer ) {' in cl_console
	assert "Com_Printf( \"com_allowConsole won't allow toggleconsole command\\n\" );" in cl_console

	assert 'com_introPlayed = Cvar_Get( "com_introplayed", "0", CVAR_ARCHIVE);' in common
	assert 'if( !com_introPlayed->integer ) {' in common
	assert 'Cvar_Set( com_introPlayed->name, "1" );' in common
	assert 'Cvar_Set( "nextmap", "cinematic intro.RoQ" );' in common

	assert 'Cvar_Get( "web_browserActive", "0", CVAR_ROM );' in common
	assert 'cvar_t\t*com_webBrowserActive;' in common
	assert 'com_webBrowserActive = Cvar_Get( "web_browserActive", "0", CVAR_ROM );' in common
	assert 'Cvar_Get ("web_browserActive", "0", CVAR_ROM );' not in cl_main
	assert 'Cvar_Get ("web_browserActive", "0", CVAR_ROM );' in cl_cgame
	assert 'Cmd_AddCommand ("web_browserActive", CL_Web_BrowserActive_f );' not in cl_main
	assert 'Cvar_Set( "web_browserActive", "1" );' in cl_cgame
	assert 'Cvar_Set( "web_browserActive", "0" );' in cl_cgame
	assert 'browserActive = trap_Cvar_VariableValue( "web_browserActive" );' in cg_draw

	assert 'com_buildScript = Cvar_Get( "com_build", "0", 0 );' in common
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in common
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in cl_main
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in sv_init
	assert 'cg_buildScript' not in "\n".join((cg_main, cg_local, cg_players, cg_servercmds))
	assert '{ &cg_buildScript, "com_build", "0", 0 },' not in cg_main
	assert 'vmCvar_t\tcg_buildScript;' not in cg_main
	assert 'extern\tvmCvar_t\t\tcg_buildScript;' not in cg_local
	assert 'if ( cgs.gametype >= GT_TEAM || trap_Cvar_VariableValue( "com_build" ) ) {' in cg_main
	assert 'if ( items[ i ] == \'1\' || trap_Cvar_VariableValue( "com_build" ) ) {' in cg_main
	assert 'if ( trap_Cvar_VariableValue( "com_build" ) ) {' in cg_players
	assert 'cg_deferPlayers.integer && !trap_Cvar_VariableValue( "com_build" ) && !cg.loading' in cg_players
	assert 'if ( trap_Cvar_VariableValue( "com_build" ) ) {' in cg_servercmds
	assert 'if( g_gametype.integer == GT_SINGLE_PLAYER || trap_Cvar_VariableIntegerValue( "com_build" ) ) {' in g_main

	assert 'com_version = Cvar_Get ("version", s, CVAR_ROM | CVAR_SERVERINFO );' in common
	assert 'Info_SetValueForKey( info, NET_GetMotdVersionInfoKey(), com_version->string );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer( "version", str, sizeof(str) );' in g_rankings


def test_selected_com_cvars_match_retail_defaults_flags_and_wiring() -> None:
	common = _read_text(COMMON)
	qcommon_h = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "qcommon.h")
	cvar = _read_text(QCOMMON_CVAR)
	files = _read_text(FILES)
	cl_console = _read_text(CL_CONSOLE)
	cl_keys = _read_text(CL_KEYS)
	cl_main = _read_text(CL_MAIN)
	ui_main = _read_text(UI_MAIN)
	cg_main = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c")
	cg_local = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h")
	cg_players = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c")
	cg_servercmds = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c")
	cg_effects = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_effects.c")
	cg_weapons = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c")
	g_main = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_main.c")
	g_local = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_local.h")
	g_combat = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_combat.c")
	g_misc = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_misc.c")
	g_advertisement_block = _extract_function_block(g_misc, "void SP_advertisement( gentity_t *ent ) {")
	sv_init = _read_text(SV_INIT)
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	retail_cgame_resource_hlil = _read_text(QL_CGAME_HLIL_PART01)
	retail_cgame_hlil = _read_text(QL_CGAME_HLIL_PART02)
	retail_qagame_hlil = _read_text(QL_QAGAME_HLIL_PART02)
	ui_hlil = _read_text(QL_UI_HLIL_PART01)

	assert 'sub_4cdd30(x87_r0, x87_r1, x87_r2, "com_maxfps", "125", "30", "250", 0x81001)' in retail_hlil
	assert 'char const (* data_1007848c)[0xb] = data_1006a968 {"com_maxfps"}' in retail_cgame_hlil
	assert 'void* data_10078490 = 0x1006a964' in retail_cgame_hlil
	assert 'void* data_10078494 = data_1006ab94' in retail_cgame_hlil
	assert 'void* data_10078498 = 0x1006b4f4' in retail_cgame_hlil
	assert '01 18 08 00' in retail_cgame_hlil
	assert 'com_maxfps = Cvar_GetBounded( "com_maxfps", "125", "30", "250", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD );' in common
	assert "vmCvar_t\tcg_maxfps;" in cg_main
	assert '{ &cg_maxfps, "com_maxfps", "125", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "30", "250" },' in cg_main
	assert 'if ( !com_dedicated->integer && com_maxfps->integer > 0 && !com_timedemo->integer ) {' in common
	assert 'minMsec = 1000 / com_maxfps->integer;' in common

	assert 'com_blood' not in retail_hlil
	assert 'com_blood' not in retail_ghidra
	assert 'com_blood' not in common
	assert 'com_blood' not in qcommon_h
	assert '{ &cg_blood, "cg_blood", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },' in cg_main
	assert 'g_blood' not in g_main
	assert 'g_blood' not in g_local
	assert 'if ( !cg_blood.integer || !cgs.media.bloodSprayShaders[0] ) {' in cg_effects
	assert 'if ( !cg_blood.integer || !cgs.media.bloodSprayShaders[0] ) {' in cg_weapons
	assert 'if ( ( self->health <= GIB_HEALTH && !( contents & CONTENTS_NODROP ) ) || meansOfDeath == MOD_SUICIDE ) {' in g_combat

	assert 'data_145c9fc = sub_4ce0d0(x87_r5, "com_showtrace", U"0", 0x200)' in retail_hlil
	assert 'com_showtrace = Cvar_Get ("com_showtrace", "0", CVAR_CHEAT);' in common
	assert 'if ( com_showtrace->integer ) {' in common
	assert 'Com_Printf ("%4i traces  (%ib %ip) %4i points\\n", c_traces,' in common

	assert 'data_145c9f8 = sub_4ce0d0(x87_r7, "com_dropsim", U"0", 0x200)' in retail_hlil
	assert 'com_dropsim = Cvar_Get ("com_dropsim", "0", CVAR_CHEAT);' in common
	assert 'if ( com_dropsim->value > 0 ) {' in common
	assert 'if ( Q_random( &seed ) < com_dropsim->value ) {' in common

	assert 'data_145c9e0 = sub_4ce0d0(x87_r3, "com_speeds", U"0", 0)' in retail_hlil
	assert 'com_speeds = Cvar_Get ("com_speeds", "0", 0);' in common
	assert 'if ( com_speeds->integer ) {' in common
	assert 'Com_Printf ("frame:%i all:%3i sv:%3i ev:%3i cl:%3i gm:%3i rf:%3i bk:%3i\\n",' in common

	assert 'data_145b940 = sub_4ce0d0(x87_r7, "com_cameraMode", U"0", 0x200)' in retail_hlil
	assert 'com_cameraMode = Cvar_Get ("com_cameraMode", "0", CVAR_CHEAT);' in common
	assert '{ &cg_cameraMode, "comCameraMode", "0", CVAR_CHEAT},' not in cg_main
	assert '{ &cg_cameraMode, "com_cameraMode", "0", CVAR_CHEAT},' in cg_main
	assert '} else if (com_cameraMode->integer) {' in common
	assert 'if (Cvar_VariableValue ("com_cameraMode") == 0) {' in cl_keys

	assert 'data_145b948 = sub_4ce0d0(x87_r1, "com_build", U"0", 0)' in retail_hlil
	assert '(*(data_1074cccc + 0x28))("com_build")' in retail_cgame_resource_hlil
	assert '{"com_build"}' not in retail_cgame_hlil
	assert 'com_buildScript = Cvar_Get( "com_build", "0", 0 );' in common
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in common
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in files
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in cl_main
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in sv_init
	assert 'cg_buildScript' not in "\n".join((cg_main, cg_local, cg_players, cg_servercmds))
	assert '{ &cg_buildScript, "com_build", "0", 0 },' not in cg_main
	assert 'vmCvar_t\tcg_buildScript;' not in cg_main
	assert 'extern\tvmCvar_t\t\tcg_buildScript;' not in cg_local
	assert 'if ( cgs.gametype >= GT_TEAM || trap_Cvar_VariableValue( "com_build" ) ) {' in cg_main
	assert 'if ( items[ i ] == \'1\' || trap_Cvar_VariableValue( "com_build" ) ) {' in cg_main
	assert 'if ( trap_Cvar_VariableValue( "com_build" ) ) {' in cg_players
	assert 'cg_deferPlayers.integer && !trap_Cvar_VariableValue( "com_build" ) && !cg.loading' in cg_players
	assert 'if ( trap_Cvar_VariableValue( "com_build" ) ) {' in cg_servercmds
	assert 'if( g_gametype.integer == GT_SINGLE_PLAYER || trap_Cvar_VariableIntegerValue( "com_build" ) ) {' in g_main
	assert '10059ef8  (*(data_104b13ac + 0x2c))("com_build")' in retail_qagame_hlil
	assert 'sub_10065c00("cellId", &data_1007d0a8, &var_44)' in retail_qagame_hlil
	assert 'char const data_10087f48[0x2a] = "advertisement entity with no cellId at %s", 0' in retail_qagame_hlil
	assert 'if ( trap_Cvar_VariableValue( "com_build" ) ) {' in g_advertisement_block
	assert 'G_SpawnString( "cellId", "", &cellId );' in g_advertisement_block
	assert 'G_Error( "advertisement entity with no cellId at %s", vtos( ent->s.origin ) );' in g_advertisement_block
	assert 'G_Printf( "advertisement entity with no cellId' not in g_advertisement_block
	assert g_advertisement_block.index('if ( trap_Cvar_VariableValue( "com_build" ) ) {') < g_advertisement_block.index('G_FreeEntity( ent );')

	assert 'data_145ca54 = sub_4ce0d0(x87_r3, "com_introplayed", U"0", 1)' in retail_hlil
	assert 'com_introPlayed = Cvar_Get( "com_introplayed", "0", CVAR_ARCHIVE);' in common
	assert 'if( !com_introPlayed->integer ) {' in common
	assert 'Cvar_Set( com_introPlayed->name, "1" );' in common
	assert 'trap_Cvar_Set("com_introPlayed", "1" );' in ui_main
	assert 'var_4c8_11 = "com_introPlayed"' in ui_hlil
	assert 'letter = tolower(fname[i]);' in cvar
	assert 'if (!Q_stricmp(var_name, var->name)) {' in cvar

	assert 'data_145b944 = sub_4ce0d0(x87_r5, "com_idleSleep", U"1", 0x80001)' in retail_hlil
	assert 'com_idleSleep = Cvar_Get( "com_idleSleep", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in common
	assert '( com_webBrowserActive && com_webBrowserActive->integer == 1 ) || ( com_idleSleep && com_idleSleep->integer == 1 )' in common
	assert 'Com_IdleSleep( minMsec - msec );' in common

	assert 'void** eax_37 = sub_4ce0d0(x87_r1, "com_allowConsole", U"1", 0x80801)' in retail_hlil
	assert 'com_allowConsole = Cvar_Get( "com_allowConsole", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in common
	assert 'if ( com_allowConsole && !com_allowConsole->integer ) {' in cl_console
	assert "Com_Printf( \"com_allowConsole won't allow toggleconsole command\\n\" );" in cl_console


def test_selected_com_cvars_second_batch_match_retail_defaults_flags_and_wiring() -> None:
	common = _read_text(COMMON)
	cvar = _read_text(QCOMMON_CVAR)
	snd_mem = _read_text(REPO_ROOT / "src" / "code" / "client" / "snd_mem.c")
	cl_cin = _read_text(CL_CIN)
	cl_main = _read_text(CL_MAIN)
	win_main = _read_text(REPO_ROOT / "src" / "code" / "win32" / "win_main.c")
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'int32_t esi = sub_4ce0d0(x87_r0, "com_zoneMegs", "64", 0x21)[0xc]' in retail_hlil
	assert '#define DEF_COMZONEMEGS "64"' in common
	assert 'Com_StartupVariable( "com_zoneMegs" );' in common
	assert 'cv = Cvar_Get( "com_zoneMegs", DEF_COMZONEMEGS, CVAR_LATCH | CVAR_ARCHIVE );' in common
	assert 'if ( cv->integer < 20 ) {' in common
	assert 's_zoneTotal = 1024 * 1024 * 16;' in common
	assert 's_zoneTotal = cv->integer * 1024 * 1024;' in common

	assert 'void** eax = sub_4ce0d0(x87_r0, "com_hunkMegs", "128", 0x21)' in retail_hlil
	assert '#define DEF_COMHUNKMEGS "128"' in common
	assert '#define MIN_COMHUNKMEGS 128' in common
	assert '#define MIN_DEDICATED_COMHUNKMEGS 1' in common
	assert 'Com_StartupVariable( "com_hunkMegs" );' in common
	assert 'cv = Cvar_Get( "com_hunkMegs", DEF_COMHUNKMEGS, CVAR_LATCH | CVAR_ARCHIVE );' in common
	assert 'nMinAlloc = MIN_DEDICATED_COMHUNKMEGS;' in common
	assert 'nMinAlloc = MIN_COMHUNKMEGS;' in common
	assert 's_hunkTotal = cv->integer * 1024 * 1024;' in common
	assert '"com_jp"' not in retail_hlil
	assert '"com_jp"' not in retail_ghidra
	assert 'com_jp' not in common
	assert 'void Hunk_Trash( void ) {' in common
	assert '"com_blindlyLoadDLLs"' not in retail_hlil
	assert '"com_blindlyLoadDLLs"' not in retail_ghidra
	assert 'com_blindlyLoadDLLs' not in win_main
	assert 'if( ((timestamp - lastWarning) > (5 * 60000)) && !Cvar_VariableIntegerValue( "dedicated" ) ) {' in win_main
	assert '"com_noErrorInterrupt"' not in retail_hlil
	assert '"com_noErrorInterrupt"' not in retail_ghidra
	assert 'com_noErrorInterrupt' not in common
	assert 'int 0x03' not in common

	assert 'int32_t esi_2 = sub_4ce0d0(x87_r0, "com_soundMegs", "16", 0x21)[0xc] * 0x202000' in retail_hlil
	assert '#define DEF_COMSOUNDMEGS "16"' in snd_mem
	assert 'cv = Cvar_Get( "com_soundMegs", DEF_COMSOUNDMEGS, CVAR_LATCH | CVAR_ARCHIVE );' in snd_mem
	assert 'scs = (cv->integer*1024);' in snd_mem
	assert 'scs = (cv->integer*1536);' not in snd_mem
	assert 'buffer = malloc(scs*sizeof(sndBuffer) );' in snd_mem
	assert 'freelist = p + scs - 1;' in snd_mem

	assert 'FUN_004c8a70("com_ignorecrash");' in retail_ghidra
	assert 'data_1205e40 = sub_4ce0d0(x87_r0, "com_ignorecrash", U"0", 0)' in retail_hlil
	assert 'Com_StartupVariable( "com_ignorecrash" );' in common
	assert 'com_ignorecrash = Cvar_Get( "com_ignorecrash", "0", 0 );' in common
	assert 'if ( com_ignorecrash && com_ignorecrash->integer ) {' in common
	assert '&& ( !com_ignorecrash || !com_ignorecrash->integer ) ) {' in common

	assert 'data_1205e44 = sub_4ce0d0(x87_r2, "com_crashed", U"0", 0x100)' in retail_hlil
	assert 'com_crashed = Cvar_Get( "com_crashed", "0", CVAR_TEMP );' in common
	assert 'Cvar_Set( "com_crashed", "1" );' in common
	assert 'if ( com_crashed && com_crashed->integer' in common

	assert 'data_1205e3c = sub_4ce0d0(x87_r4, "com_pid", sub_4d9220(&data_52d9b4), 0x40)' in retail_hlil
	assert 'Com_sprintf( pidString, sizeof( pidString ), "%lu", (unsigned long)GetCurrentProcessId() );' in common
	assert 'Com_sprintf( pidString, sizeof( pidString ), "%lu", (unsigned long)getpid() );' in common
	assert 'com_pid = Cvar_Get( "com_pid", pidString, CVAR_ROM );' in common
	assert 'if ( retainedPid > 0 && com_pid && retainedPid != com_pid->integer ) {' in common
	assert 'FS_WriteFile( "profile.pid", pidValue, strlen( pidValue ) );' in common

	assert 'data_1459924 = sub_4ce0d0(x87_r3, "developer", U"0", 0x100)' in retail_hlil
	assert 'com_developer = Cvar_Get( "developer", "0", CVAR_TEMP );' in common
	assert 'com_developer = Cvar_Get ("developer", "0", CVAR_TEMP );' in common
	assert 'Com_StartupVariable( "developer" );' in common
	assert 'if ( !com_developer || !com_developer->integer ) {' in common
	assert 'Cmd_AddCommand ("error", Com_Error_f);' in common

	assert 'data_145b958 = sub_4ce0d0(x87_r5, "logfile", U"0", 0x100)' in retail_hlil
	assert 'com_logfile = Cvar_Get( "logfile", "0", CVAR_TEMP );' in common
	assert 'com_logfile = Cvar_Get ("logfile", "0", CVAR_TEMP );' in common
	assert 'if ( com_logfile && com_logfile->integer ) {' in common
	assert 'if ( com_logfile->integer > 1 ) {' in common
	assert 'logfile = FS_FOpenFileWrite( "qconsole.log" );' in common

	assert 'data_1205e34 = sub_4ce0d0(x87_r7, "appendlogfile", U"0", 0x100)' in retail_hlil
	assert common.count('com_appendlogfile = Cvar_Get( "appendlogfile", "0", CVAR_TEMP );') == 2
	assert 'if ( com_appendlogfile && com_appendlogfile->integer ) {' in common
	assert 'logfile = FS_FOpenFileAppend( "qconsole.log" );' in common

	assert 'data_145b960 = sub_4ce0d0(x87_r1, "timescale", U"1", 0x208)' in retail_hlil
	assert 'com_timescale = Cvar_Get ("timescale", "1", CVAR_CHEAT | CVAR_SYSTEMINFO );' in common
	assert '} else if ( com_timescale->value ) {' in common
	assert 'msec *= com_timescale->value;' in common
	assert 'if ( msec < 1 && com_timescale->value) {' in common
	assert 'CL_ScaledMilliseconds()*com_timescale->value' in cl_cin
	assert 'msec = (1000 / cl_avidemo->integer) * com_timescale->value;' in cl_main
	assert 'if ( (var->flags & CVAR_CHEAT) && !cvar_cheats->integer )' in cvar


def test_selected_com_cvars_startup_alias_batch_match_retail_defaults_flags_and_wiring() -> None:
	common = _read_text(COMMON)
	cvar = _read_text(QCOMMON_CVAR)
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	cl_main = _read_text(CL_MAIN)
	cl_console = _read_text(CL_CONSOLE)
	ui_main = _read_text(UI_MAIN)
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_strings = _read_text(QL_STEAM_HLIL_PART06)
	ui_hlil = _read_text(QL_UI_HLIL_PART01)
	com_error_body = common[
		common.index("void QDECL Com_Error")
		:common.index("Com_Quit_f")
	]
	com_error_publish_block = com_error_body[
		com_error_body.index("va_start (argptr,fmt);")
		:com_error_body.index("if ( code == ERR_SERVERDISCONNECT ) {")
	]

	assert 'sub_4cd250("com_errorMessage", &data_145b9e0)' in retail_hlil
	assert 'sub_4cd250("com_errorMessage", &data_54f9da)' in retail_hlil
	assert 'sub_4cd250("com_errorMessage", &data_54f9da)' in _read_text(QL_STEAM_HLIL_PART05)
	assert '(*(data_106b40a8 + 0x24))("com_errorMessage", &var_104, 0x100)' in ui_hlil
	assert 'Cvar_Set("com_errorMessage", com_errorMessage);' in common
	assert 'if ( code != ERR_DISCONNECT && code != ERR_NEED_CD ) {' not in com_error_publish_block
	assert 'if ( code == ERR_DISCONNECT ) {' in common
	assert 'Cvar_Set("com_errorMessage", "");' in common
	assert 'Cvar_Set( "com_errorMessage", "" );' in common
	assert 'Cvar_Set( "com_errorMessage", message );' in cl_cgame
	assert 'Cvar_Set( "com_errorMessage", "" );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer("com_errorMessage", buf, sizeof(buf));' in ui_main
	assert 'trap_Cvar_Set("com_errorMessage", "");' in ui_main
	assert 'Cvar_Get( "com_errorMessage"' not in common
	assert 'return Cvar_Get (var_name, value, 0);' in cvar

	assert 'sub_4cd250("com_errormessage", &data_54f9da)' in retail_hlil
	assert 'char const data_540cf0[0x11] = "com_errormessage", 0' in retail_strings
	assert 'Cvar_Set( "com_errorMessage", "" );' in common
	assert 'letter = tolower(fname[i]);' in cvar
	assert 'if (!Q_stricmp(var_name, var->name)) {' in cvar

	assert 'sub_4cd250("com_ignoreCrash", U"1")' in retail_hlil
	assert 'char const data_540ce0[0x10] = "com_ignoreCrash", 0' in retail_strings
	assert 'if ( !FS_FileExists( QL_CONFIG_HARDWARE_FILE ) ) {' in common
	assert 'Cvar_Set( "com_ignoreCrash", "1" );' in common

	assert 'sub_4c8a70("com_ignorecrash")' in retail_hlil
	assert 'data_1205e40 = sub_4ce0d0(x87_r0, "com_ignorecrash", U"0", 0)' in retail_hlil
	assert 'Com_StartupVariable( "com_ignorecrash" );' in common
	assert 'com_ignorecrash = Cvar_Get( "com_ignorecrash", "0", 0 );' in common
	assert 'if ( com_crashed && com_crashed->integer' in common
	assert '&& ( !com_ignorecrash || !com_ignorecrash->integer ) ) {' in common

	assert 'sub_4c8a70("journal")' in retail_hlil
	assert 'void** eax = sub_4ce0d0(x87_r0, "journal", U"0", 0x10)' in retail_hlil
	assert 'sub_4cd250("com_journal", U"0")' in retail_hlil
	assert 'Com_StartupVariable( "journal" );' in common
	assert 'com_journal = Cvar_Get ("journal", "0", CVAR_INIT);' in common
	assert 'Cvar_Set( "com_journal", "0" );' in common

	assert 'data_1205e44 = sub_4ce0d0(x87_r2, "com_crashed", U"0", 0x100)' in retail_hlil
	assert 'com_crashed = Cvar_Get( "com_crashed", "0", CVAR_TEMP );' in common
	assert 'Cvar_Set( "com_crashed", "1" );' in common
	assert 'if ( com_crashed && com_crashed->integer' in common

	assert 'data_1205e3c = sub_4ce0d0(x87_r4, "com_pid", sub_4d9220(&data_52d9b4), 0x40)' in retail_hlil
	assert 'com_pid = Cvar_Get( "com_pid", pidString, CVAR_ROM );' in common
	assert 'Com_ProfilePidIsCurrentProcess' in common
	assert 'FS_WriteFile( "profile.pid", pidValue, strlen( pidValue ) );' in common

	assert 'var_4c8_11 = "com_introPlayed"' in ui_hlil
	assert 'trap_Cvar_Set("com_introPlayed", "1" );' in ui_main
	assert 'data_145ca54 = sub_4ce0d0(x87_r3, "com_introplayed", U"0", 1)' in retail_hlil
	assert 'com_introPlayed = Cvar_Get( "com_introplayed", "0", CVAR_ARCHIVE);' in common
	assert 'if( !com_introPlayed->integer ) {' in common
	assert 'Cvar_Set( com_introPlayed->name, "1" );' in common

	assert 'void** eax_37 = sub_4ce0d0(x87_r1, "com_allowConsole", U"1", 0x80801)' in retail_hlil
	assert 'com_allowConsole = Cvar_Get( "com_allowConsole", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in common
	assert 'if ( com_allowConsole && !com_allowConsole->integer ) {' in cl_console
	assert "Com_Printf( \"com_allowConsole won't allow toggleconsole command\\n\" );" in cl_console


def test_engine_cvar_thirteenth_filesystem_tranche_matches_retail_contracts() -> None:
	files = _read_text(FILES)

	assert 'fs_debug = Cvar_Get( "fs_debug", "0", 0 );' in files
	assert 'if ( fs_debug->integer ) {' in files
	assert 'Com_Printf( "FS_FOpenFileRead: %s (found in' in files
	assert 'Com_Printf( "FS_SV_FOpenFileRead (fs_homepath): %s\\n", ospath );' in files

	assert 'fs_copyfiles = Cvar_Get( "fs_copyfiles", "0", CVAR_INIT );' in files
	assert 'if ( fs_copyfiles->integer' in files
	assert '|| fs_copyfiles->integer == 2' in files
	assert 'FS_CopyFile( netpath, copypath );' in files

	assert 'fs_copypath = Cvar_Get( "fs_copypath", "", CVAR_INIT );' in files
	assert 'copypath = FS_BuildOSPath( fs_copypath->string, dir->gamedir, filename );' in files
	assert 'copyFile = fopen( copypath, "wb" );' in files
	assert 'fclose( copyFile );' in files

	assert 'fs_cdpath = Cvar_Get ("fs_cdpath", Sys_DefaultCDPath(), CVAR_INIT );' in files
	assert 'Com_StartupVariable( "fs_cdpath" );' in files
	assert 'FS_AddGameDirectory( fs_cdpath->string, gameName );' in files
	assert 'Com_Printf( "FS_SV_FOpenFileRead (fs_cdpath) : %s\\n", ospath );' in files

	assert 'fs_basepath = Cvar_Get ("fs_basepath", Sys_DefaultInstallPath(), CVAR_INIT );' in files
	assert 'Com_StartupVariable( "fs_basepath" );' in files
	assert 'FS_AddGameDirectory( fs_basepath->string, gameName );' in files

	assert 'fs_basegame = Cvar_Get ("fs_basegame", "", CVAR_INIT );' in files
	assert 'if ( fs_basegame->string[0] && !Q_stricmp( gameName, BASEGAME ) && Q_stricmp( fs_basegame->string, gameName ) ) {' in files
	assert 'FS_AddGameDirectory(fs_basepath->string, fs_basegame->string);' in files

	assert 'fs_skipWorkshop = Cvar_Get( "fs_skipWorkshop", "0", CVAR_INIT );' in files
	assert 'if ( fs_skipWorkshop && fs_skipWorkshop->integer ) {' in files
	assert 'FS_SteamWorkshopInit( gameName );' in files

	assert 'fs_homepath = Cvar_Get ("fs_homepath", homePath, CVAR_INIT );' in files
	assert 'Com_StartupVariable( "fs_homepath" );' in files
	assert 'FS_AddGameDirectory ( fs_homepath->string, gameName );' in files

	assert 'fs_gamedirvar = Cvar_Get ("fs_game", "", CVAR_INIT|CVAR_SYSTEMINFO );' in files
	assert 'Com_StartupVariable( "fs_game" );' in files
	assert 'if ( fs_gamedirvar->string[0] && !Q_stricmp( gameName, BASEGAME ) && Q_stricmp( fs_gamedirvar->string, gameName ) ) {' in files
	assert 'fs = Cvar_Get ("fs_game", "", CVAR_INIT|CVAR_SYSTEMINFO );' in files

	assert 'fs_restrict = Cvar_Get ("fs_restrict", "", CVAR_INIT );' in files
	assert 'Com_StartupVariable( "fs_restrict" );' in files
	assert 'if ( fs_restrict && fs_restrict->integer ) {' in files
	assert 'Cvar_Set( "fs_restrict", "0" );' in files


def test_engine_cvar_fourteenth_core_timing_tranche_matches_retail_contracts() -> None:
	common = _read_text(COMMON)
	cl_main = _read_text(CL_MAIN)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	client_h = _read_text(REPO_ROOT / "src" / "code" / "client" / "client.h")
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	cg_draw = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c")
	cg_servercmds = _read_text(REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c")
	g_main = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_main.c")
	sv_init = _read_text(SV_INIT)

	assert 'cv = Cvar_Get( "com_zoneMegs", DEF_COMZONEMEGS, CVAR_LATCH | CVAR_ARCHIVE );' in common
	assert 'if ( cv->integer < 20 ) {' in common
	assert 's_zoneTotal = cv->integer * 1024 * 1024;' in common

	assert 'cv = Cvar_Get( "com_hunkMegs", DEF_COMHUNKMEGS, CVAR_LATCH | CVAR_ARCHIVE );' in common
	assert 'if (com_dedicated && com_dedicated->integer) {' in common
	assert 's_hunkTotal = cv->integer * 1024 * 1024;' in common

	assert 'com_journal = Cvar_Get ("journal", "0", CVAR_INIT);' in common
	assert 'if ( com_journal->integer == 1 ) {' in common
	assert 'FS_FOpenFileWrite( "journal.dat" );' in common
	assert 'FS_FOpenFileRead( "journaldata.dat", &com_journalDataFile, qtrue );' in common

	assert 'com_idleSleep = Cvar_Get( "com_idleSleep", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in common
	assert '( com_webBrowserActive && com_webBrowserActive->integer == 1 ) || ( com_idleSleep && com_idleSleep->integer == 1 )' in common
	assert 'Com_IdleSleep( minMsec - msec );' in common
	assert 'dueTime.QuadPart = -( (LONGLONG)msec * 10000 );' in common
	assert 'usleep( msec * 1000 );' in common

	assert 'cl_freezeDemo = Cvar_Get ("cl_freezeDemo", "0", CVAR_TEMP );' in cl_main
	assert 'if ( clc.demoplaying && cl_freezeDemo->integer ) {' in cl_cgame
	assert 'freezeDemo = trap_Cvar_VariableValue( "cl_freezeDemo" );' in cg_draw

	assert 'cl_mouseAccelDebug = Cvar_Get ("cl_mouseAccelDebug", "0", 0 );' in cl_main
	assert 'static FILE\t\t*cl_mouseAccelDebugLog;' in cl_input
	assert 'Cvar_VariableStringBuffer( "fs_homepath", homepath, sizeof( homepath ) );' in cl_input
	assert 'path = FS_BuildOSPath( homepath, "", "mouse.log" );' in cl_input
	assert 'fprintf( cl_mouseAccelDebugLog, "mx my frame_msec rate power\\n" );' in cl_input
	assert 'fprintf( cl_mouseAccelDebugLog, "%g %g %d ", mx, my, frame_msec );' in cl_input
	assert 'Com_Printf( "mouse accel:' not in cl_input
	assert 'cl_mouseAccelStyle' not in cl_main
	assert 'cl_mouseAccelStyle' not in cl_input
	assert 'cl_mouseAccelStyle' not in client_h

	assert 'Cvar_Get ("dmflags", "0", CVAR_SERVERINFO);' in sv_init
	assert '{ &g_dmflags, "dmflags", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qtrue  },' in g_main
	assert "cgs.dmflags = atoi( Info_ValueForKey( info, SERVERINFO_KEY_DMFLAGS ) );" in cg_servercmds

	assert 'Cvar_Get ("fraglimit", "20", CVAR_SERVERINFO);' in sv_init
	assert '{ &g_fraglimit, "fraglimit", "20", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },' in g_main
	assert "cgs.fraglimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_FRAGLIMIT ) );" in cg_servercmds
	assert 'if ( level.teamScores[TEAM_RED] >= g_fraglimit.integer ) {' in g_main

	assert 'Cvar_Get ("timelimit", "0", CVAR_SERVERINFO);' in sv_init
	assert '{ &g_timelimit, "timelimit", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },' in g_main
	assert "cgs.timelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_TIMELIMIT ) );" in cg_servercmds
	assert 'if ( g_timelimit.integer && !level.warmupTime ) {' in g_main

	assert 'sv_gametype = Cvar_Get ("g_gametype", "0", CVAR_SERVERINFO | CVAR_LATCH );' in sv_init
	assert '{ &g_gametype, "g_gametype", "0", CVAR_SERVERINFO | CVAR_USERINFO | CVAR_LATCH, 0, qfalse  },' in g_main
	assert 'cgs.gametype = atoi( gametypeValue );' in cg_servercmds
	assert 'trap_Cvar_Set("g_gametype", va("%i", cgs.gametype));' in cg_servercmds


def test_engine_cvar_thirtyfourth_client_cl_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_keys = _read_text(CL_KEYS)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	cl_scrn = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_scrn.c")
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'DAT_01647ef4 = FUN_004ce0d0("cl_allowConsoleChat",&DAT_0054ffe0,0x80801);' in retail_ghidra
	assert 'cl_allowConsoleChat = Cvar_Get ("cl_allowConsoleChat", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( ( !cl_allowConsoleChat || !cl_allowConsoleChat->integer )' in cl_keys
	assert 'Cbuf_AddText ("cmd say ");' in cl_keys

	assert 'DAT_015ee394 = FUN_004ce0d0("cl_demoRecordMessage",&DAT_0052f5d8,0x80801);' in retail_ghidra
	assert 'cl_demoRecordMessage = Cvar_Get ("cl_demoRecordMessage", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_demoRecordMessage->integer == 1 ) {' in cl_scrn
	assert 'else if ( cl_demoRecordMessage->integer == 2 ) {' in cl_scrn

	assert 'data_1627c50 = sub_4ce0d0(x87_r5, "cl_freezeDemo", U"0", 0x100)' in retail_hlil
	assert 'cl_freezeDemo = Cvar_Get ("cl_freezeDemo", "0", CVAR_TEMP );' in cl_main
	assert 'if ( clc.demoplaying && cl_freezeDemo->integer ) {' in cl_cgame
	assert 'Cbuf_ExecuteText( EXEC_APPEND, "toggle cl_freezeDemo\\n" );' in cl_keys

	assert 'data_1627c3c = sub_4ce0d0(x87_r5, "cl_maxpackets", "125", 0x200)' in retail_hlil
	assert 'cl_maxpackets = Cvar_Get ("cl_maxpackets", "125", CVAR_CHEAT );' in cl_main
	assert 'Cvar_Set( "cl_maxpackets", "15" );' in cl_input
	assert 'Cvar_Set( "cl_maxpackets", "125" );' in cl_input
	assert 'if ( delta < 1000 / cl_maxpackets->integer ) {' in cl_input

	assert 'data_15f672c = sub_4ce0d0(x87_r1, "cl_packetdup", U"1", 0x80001)' in retail_hlil
	assert 'cl_packetdup = Cvar_Get ("cl_packetdup", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'Cvar_Set( "cl_packetdup", "0" );' in cl_input
	assert 'Cvar_Set( "cl_packetdup", "5" );' in cl_input
	assert 'oldPacketNum = (clc.netchan.outgoingSequence - 1 - cl_packetdup->integer) & PACKET_MASK;' in cl_input

	assert '"cl_timeNudge", U"0", "-20", U"0", 0x1801)' in retail_hlil
	assert 'cl_timeNudge = Cvar_GetBounded( "cl_timeNudge", "0", "-20", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED );' in cl_main
	assert 'tn = cl_timeNudge->integer;' in cl_cgame

	assert '"cl_autoTimeNudge", U"0", U"0", U"1", 0x1801)' in retail_hlil
	assert 'cl_autoTimeNudge = Cvar_GetBounded( "cl_autoTimeNudge", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED );' in cl_main
	assert '} else if ( !cl_autoTimeNudge->integer ) {' in cl_cgame
	assert 'tn = (int)( (float)cl.snap.ping * -0.5f );' in cl_cgame
	assert 'static int CL_ClampTimeNudge( int tn ) {' in cl_cgame
	assert 'tn = CL_ClampTimeNudge( tn );' in cl_cgame

	assert 'data_1647ee8 = sub_4ce0d0(x87_r5, "cl_quitOnDemoCompleted", U"0", 0)' in retail_hlil
	assert 'cl_quitOnDemoCompleted = Cvar_Get ("cl_quitOnDemoCompleted", "0", 0 );' in cl_main
	assert 'if ( cl_quitOnDemoCompleted && cl_quitOnDemoCompleted->integer ) {' in cl_main
	assert 'Cbuf_AddText( "quit\\n" );' in cl_main

	assert 'data_1647ef8 = sub_4ce0d0(x87_r3, "cl_serverStatusResendTime", "750", 0)' in retail_hlil
	assert 'cl_serverStatusResendTime = Cvar_Get ("cl_serverStatusResendTime", "750", 0);' in cl_main
	assert 'serverStatus->startTime < Com_Milliseconds() - cl_serverStatusResendTime->integer' in cl_main

	assert 'data_1627c58 = sub_4ce0d0(x87_r1, "cl_showTimeDelta", U"0", 0x100)' in retail_hlil
	assert 'cl_showTimeDelta = Cvar_Get ("cl_showTimeDelta", "0", CVAR_TEMP );' in cl_main
	assert 'if ( cl_showTimeDelta->integer ) {' in cl_cgame


def test_engine_cvar_thirtyfifth_client_demo_input_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'DAT_0146cc4c = FUN_004ce0d0("cl_avidemo",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'DAT_01627c44 = FUN_004ce0d0("cl_avidemo_latch",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'DAT_015f6734 = FUN_004ce0d0("cl_avidemo_mintime",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'DAT_01647efc = FUN_004ce0d0("cl_avidemo_maxtime",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'DAT_01528b78 = FUN_004ce0d0("cl_forceavidemo",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'cl_avidemo = Cvar_Get ("cl_avidemo", "0", 0);' in cl_main
	assert 'cl_avidemo_latch = Cvar_Get ("cl_avidemo_latch", "0", 0 );' in cl_main
	assert 'cl_avidemo_mintime = Cvar_Get ("cl_avidemo_mintime", "0", 0 );' in cl_main
	assert 'cl_avidemo_maxtime = Cvar_Get ("cl_avidemo_maxtime", "0", 0 );' in cl_main
	assert 'cl_forceavidemo = Cvar_Get ("cl_forceavidemo", "0", 0);' in cl_main
	assert 'if ( cl_avidemo_latch->integer ) {' in cl_main
	assert 'if ( !cl_avidemo_mintime->integer || cl.serverTime > cl_avidemo_mintime->integer ) {' in cl_main
	assert 'Cvar_SetValue( "cl_avidemo", cl_avidemo_latch->integer );' in cl_main
	assert 'Cvar_Set( "cl_avidemo_latch", "0" );' in cl_main
	assert 'if ( cl_avidemo->integer && msec) {' in cl_main
	assert 'if ( cls.state == CA_ACTIVE || cl_forceavidemo->integer) {' in cl_main
	assert 'if ( cl_avidemo_maxtime->integer && cl.serverTime > cl_avidemo_maxtime->integer ) {' in cl_main
	assert 'CL_Disconnect_f();' in cl_main
	assert 'Cbuf_ExecuteText( EXEC_NOW, "screenshot silent\\n" );' in cl_main
	assert 'msec = (1000 / cl_avidemo->integer) * com_timescale->value;' in cl_main
	assert 'sub_4cd250("cl_avidemo", sub_4d9220(&data_52d9b4))' in retail_hlil
	assert 'sub_4cd250("cl_avidemo_latch", U"0")' in retail_hlil
	assert 'sub_4c8900(ecx_2, "screenshot silent\\n")' in retail_hlil
	assert 'divs.dp.d(0x3e8, *(data_146cc4c + 0x30))' in retail_hlil

	assert 'DAT_0165d5f8 = FUN_004ce0d0("cl_anglespeedkey",&DAT_0053f200,0x200);' in retail_ghidra
	assert 'DAT_0164b0f8 = FUN_004ce0d0("cl_yawspeed",&DAT_0053f0d8,0x200);' in retail_ghidra
	assert 'DAT_0165d5b8 = FUN_004ce0d0("cl_pitchspeed",&DAT_0053f0d8,0x200);' in retail_ghidra
	assert 'cl_anglespeedkey = Cvar_Get ("cl_anglespeedkey", "1.5", CVAR_CHEAT );' in cl_main
	assert 'cl_yawspeed = Cvar_Get ("cl_yawspeed", "140", CVAR_CHEAT );' in cl_main
	assert 'cl_pitchspeed = Cvar_Get ("cl_pitchspeed", "140", CVAR_CHEAT );' in cl_main
	assert 'speed = 0.001 * cls.frametime * cl_anglespeedkey->value;' in cl_input
	assert 'cl.viewangles[YAW] -= speed*cl_yawspeed->value*CL_KeyState (&in_right);' in cl_input
	assert 'cl.viewangles[YAW] += speed*cl_yawspeed->value*CL_KeyState (&in_left);' in cl_input
	assert 'cl.viewangles[PITCH] -= speed*cl_pitchspeed->value * CL_KeyState (&in_lookup);' in cl_input
	assert 'cl.viewangles[PITCH] += speed*cl_pitchspeed->value * CL_KeyState (&in_lookdown);' in cl_input
	assert 'anglespeed = 0.001 * cls.frametime * cl_anglespeedkey->value;' in cl_input
	assert 'cl.viewangles[YAW] += anglespeed * cl_yawspeed->value * cl.joystickAxis[AXIS_SIDE];' in cl_input
	assert 'cl.viewangles[PITCH] += anglespeed * cl_pitchspeed->value * cl.joystickAxis[AXIS_FORWARD];' in cl_input
	assert 'x87_r7_1 = x87_r7_1 * fconvert.t(*(data_165d5f8 + 0x2c))' in retail_hlil
	assert 'void* esi_1 = data_164b0f8' in retail_hlil
	assert 'void* esi_2 = data_165d5b8' in retail_hlil

	assert 'DAT_0165d5d8 = FUN_004ce0d0("cl_run",&DAT_00551624,1);' in retail_ghidra
	assert 'cl_run = Cvar_Get ("cl_run", "1", CVAR_ARCHIVE);' in cl_main
	assert cl_input.count( 'if ( in_speed.active ^ cl_run->integer ) {' ) >= 2
	assert 'movespeed = 127;' in cl_input
	assert 'movespeed = 64;' in cl_input
	assert 'movespeed = 2;' in cl_input
	assert 'movespeed = 1;' in cl_input
	assert 'if (*(data_165d5d8 + 0x30) == data_165d5b0)' in retail_hlil

	assert 'DAT_01647f10 = FUN_004ce0d0("cl_freelook",&DAT_00551624,0x80801);' in retail_ghidra
	assert 'cl_freelook = Cvar_Get( "cl_freelook", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( !cl_freelook->integer ) {' in cl_input
	assert 'if ( (in_mlooking || cl_freelook->integer) && !in_strafe.active ) {' in cl_input
	assert 'if ((data_165d59c == 0 && *(data_1647f10 + 0x30) == 0) || data_165d590 != 0)' in retail_hlil
	assert 'if (*(result + 0x30) == 0)' in retail_hlil


def test_engine_cvar_thirtysixth_client_debug_identity_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_parse = _read_text(CL_PARSE)
	msg = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "msg.c")
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'DAT_01528b8c = FUN_004ce0d0("cl_shownet",&DAT_0054ffe0,0x100);' in retail_ghidra
	assert 'cl_shownet = Cvar_Get ("cl_shownet", "0", CVAR_TEMP );' in cl_main
	assert 'if ( cl_shownet->integer >= 2)' in cl_parse
	assert 'if ( cl_shownet->integer == 3 ) {' in cl_parse
	assert 'cl_shownet->integer == 4' in msg
	assert 'cl_shownet->integer >= 2 || cl_shownet->integer == -1' in msg
	assert 'cl_shownet->integer >= 2 || cl_shownet->integer == -2' in msg
	assert 'data_1528b8c = sub_4ce0d0(x87_r5, "cl_shownet", U"0", 0x100)' in retail_hlil
	assert 'if (*(data_1528b8c + 0x30) == 3)' in retail_hlil
	assert 'if (*(data_1528b8c + 0x30) s>= 2)' in retail_hlil
	assert 'if (*(data_1528b8c + 0x30) == 4)' in retail_hlil

	assert 'DAT_0146cc40 = FUN_004ce0d0("cl_showSend",&DAT_0054ffe0,0x100);' in retail_ghidra
	assert 'cl_showSend = Cvar_Get ("cl_showSend", "0", CVAR_TEMP );' in cl_main
	assert 'if ( cl_showSend->integer ) {' in cl_input
	assert 'data_146cc40 = sub_4ce0d0(x87_r7, "cl_showSend", U"0", 0x100)' in retail_hlil
	assert 'if (*(data_146cc40 + 0x30) != 0)' in retail_hlil

	assert 'FUN_004ce0d0("cl_anonymous",&DAT_0054ffe0,3);' in retail_ghidra
	assert 'Cvar_Get ("cl_anonymous", "0", CVAR_USERINFO | CVAR_ARCHIVE );' in cl_main
	assert 'Cvar_VariableIntegerValue( "cl_anonymous" )' in cl_main
	assert 'sub_4ce0d0(x87_r2, "cl_anonymous", U"0", 3)' in retail_hlil

	assert 'FUN_004ce0d0("cl_platform",&DAT_00551624,0x40);' in retail_ghidra
	assert 'cl_platform = Cvar_Get ("cl_platform", "1", CVAR_ROM );' in cl_main
	assert 'sub_4ce0d0(x87_r4, "cl_platform", U"1", 0x40)' in retail_hlil

	assert 'FUN_004ce0d0("cl_maxPing",&DAT_00539fc0,1);' in retail_ghidra
	assert 'Cvar_Get( "cl_maxPing", "800", CVAR_ARCHIVE );' in cl_main
	assert 'maxPing = Cvar_VariableIntegerValue( "cl_maxPing" );' in cl_main
	assert 'if( maxPing < 100 ) {' in cl_main
	assert 'if (time < maxPing)' in cl_main
	assert 'sub_4ce0d0(x87_r6, "cl_maxPing", "800", 1)' in retail_hlil
	assert 'eax_2, ecx_4 = sub_4ccd80("cl_maxPing")' in retail_hlil
	assert 'if (eax_2 s< 0x64)' in retail_hlil

	assert 'DAT_015f6730 = FUN_004ce0d0("cl_mouseAccel",&DAT_0054ffe0,0x80801);' in retail_ghidra
	assert 'DAT_015f6724 = FUN_004ce0d0("cl_mouseAccelDebug",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'DAT_0146cd00 = FUN_004ce0d0("cl_mouseAccelOffset",&DAT_0054ffe0,0x80801);' in retail_ghidra
	assert 'DAT_0146cc3c = FUN_004ce0d0("cl_mouseAccelPower",&DAT_0052f5d8,0x80801);' in retail_ghidra
	assert 'DAT_01647ee4 = FUN_004ce0d0("cl_mouseSensCap",&DAT_0054ffe0,0x80001);' in retail_ghidra
	assert 'cl_mouseAccel = Cvar_Get ("cl_mouseAccel", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl_mouseAccelDebug = Cvar_Get ("cl_mouseAccelDebug", "0", 0 );' in cl_main
	assert 'cl_mouseAccelOffset = Cvar_Get ("cl_mouseAccelOffset", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl_mouseAccelPower = Cvar_Get ("cl_mouseAccelPower", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl_mouseSensCap = Cvar_Get ("cl_mouseSensCap", "0", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_mouseAccel->value != 0.0f ) {' in cl_input
	assert 'rate -= cl_mouseAccelOffset->value;' in cl_input
	assert 'power = cl_mouseAccelPower->value - 1.0f;' in cl_input
	assert 'accelRate = fabsf( cl_mouseAccel->value ) * rate;' in cl_input
	assert 'if ( cl_mouseAccel->value <= 0.0f ) {' in cl_input
	assert 'if ( cl_mouseSensCap->value > 0.0f && cl_mouseSensCap->value < sensitivity ) {' in cl_input
	assert 'if ( !cl_mouseAccelDebug || !cl_mouseAccelDebug->integer ) {' in cl_input
	assert 'path = FS_BuildOSPath( homepath, "", "mouse.log" );' in cl_input
	assert 'fprintf( cl_mouseAccelDebugLog, "mx my frame_msec rate power\\n" );' in cl_input
	assert 'data_15f6730 = sub_4ce0d0(x87_r3, "cl_mouseAccel", U"0", 0x80801)' in retail_hlil
	assert 'data_15f6724 = sub_4ce0d0(x87_r5, "cl_mouseAccelDebug", U"0", 0)' in retail_hlil
	assert 'data_146cd00 = sub_4ce0d0(x87_r7, "cl_mouseAccelOffset", U"0", 0x80801)' in retail_hlil
	assert 'data_146cc3c = sub_4ce0d0(x87_r1, "cl_mouseAccelPower", U"2", 0x80801)' in retail_hlil
	assert 'data_1647ee4 = sub_4ce0d0(x87_r3, "cl_mouseSensCap", U"0", 0x80001)' in retail_hlil
	assert 'void* edi_1 = data_15f6730' in retail_hlil
	assert 'void* ecx_2 = data_146cd00' in retail_hlil
	assert 'fconvert.t(*(data_146cc3c + 0x2c)) - fconvert.t(1.0)' in retail_hlil
	assert 'long double temp2_1 = fconvert.t(*(data_1647ee4 + 0x2c))' in retail_hlil


def test_engine_cvar_thirtyseventh_client_lifecycle_workshop_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_scrn = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_scrn.c")
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	cl_parse = _read_text(CL_PARSE)
	cl_ui = _read_text(CL_UI)
	common = _read_text(COMMON)
	cmd = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "cmd.c")
	ui_main = _read_text(UI_MAIN)
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	ui_hlil = _read_text(QL_UI_HLIL_PART01)
	ui_ghidra = _read_text(QL_UI_GHIDRA_DECOMPILE)

	assert '_DAT_01627c40 = FUN_004ce0d0("cl_motd",&DAT_00551624,0);' in retail_ghidra
	assert 'cl_motd = Cvar_Get ("cl_motd", "1", 0);' in cl_main
	assert 'if ( cl_motd && cl_motd->integer ) {' in cl_main
	assert 'if ( !cl_motd->integer ) {' in cl_main
	assert 'data_1627c40 = sub_4ce0d0(x87_r7, "cl_motd", U"1", 0)' in retail_hlil

	assert '_DAT_01627c4c = FUN_004ce0d0("cl_motdString",&DAT_0054f9da,0x40);' in retail_ghidra
	assert 'cl_motdString = Cvar_Get( "cl_motdString", "", CVAR_ROM );' in cl_main
	assert 'Cvar_Set( "cl_motdString", challenge );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer( "cl_motdString", uiInfo.serverStatus.motd, sizeof(uiInfo.serverStatus.motd) );' in ui_main
	assert 'data_1627c4c = sub_4ce0d0(x87_r1, "cl_motdString", &data_54f9da, 0x40)' in retail_hlil
	assert '(*(data_106b40a8 + 0x24))("cl_motdString", &data_107644d0, 0x400)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x24))("cl_motdString",&DAT_107644d0,0x400);' in ui_ghidra

	assert 'DAT_01528b7c = FUN_004ce0d0("cl_timeout",&DAT_0052f2e4,0);' in retail_ghidra
	assert 'cl_timeout = Cvar_Get ("cl_timeout", "40", 0);' in cl_main
	assert 'cls.realtime - clc.lastPacketTime > cl_timeout->value*1000' in cl_main
	assert 'data_1528b7c = sub_4ce0d0(x87_r2, "cl_timeout", "40", 0)' in retail_hlil

	assert 'cl_nodelta = Cvar_Get ("cl_nodelta", "0", 0);' in cl_input
	assert 'if ( cl_nodelta->integer || !cl.snap.valid || clc.demowaiting' in cl_input
	assert 'data_146ccfc = sub_4ce0d0(x87_r0, "cl_nodelta", U"0", 0)' in retail_hlil

	assert 'cl_debugMove = Cvar_Get ("cl_debugMove", "0", 0);' in cl_input
	assert 'if ( cl_debugMove->integer ) {' in cl_input
	assert 'if ( cl_debugMove->integer == 1 ) {' in cl_input
	assert 'if ( cl_debugMove->integer == 2 ) {' in cl_input
	assert 'if ( cl_debuggraph->integer || cl_timegraph->integer || cl_debugMove->integer ) {' in cl_scrn
	assert 'void** result = sub_4ce0d0(x87_r2, "cl_debugMove", U"0", 0)' in retail_hlil

	assert 'DAT_0145b95c = FUN_004ce0d0("cl_paused",&DAT_0054ffe0,0x40);' in retail_ghidra
	assert 'cl_paused = Cvar_Get ("cl_paused", "0", CVAR_ROM);' in common
	assert 'Cvar_Set( "cl_paused", "0" );' in cl_main
	assert 'Cvar_Set( "cl_paused", "0" );' in cl_parse
	assert 'if ( com_sv_running->integer && sv_paused->integer && cl_paused->integer ) {' in cl_input
	assert 'if ( sv_paused->integer && cl_paused->integer && com_sv_running->integer ) {' in cl_cgame
	assert 'data_145b95c = sub_4ce0d0(x87_r1, "cl_paused", U"0", 0x40)' in retail_hlil
	assert 'sub_4cd250("cl_paused", U"0")' in retail_hlil

	assert 'DAT_01205e30 = FUN_004ce0d0("cl_running",&DAT_0054ffe0,0x40);' in retail_ghidra
	assert 'com_cl_running = Cvar_Get ("cl_running", "0", CVAR_ROM);' in common
	assert 'Cvar_Set( "cl_running", "1" );' in cl_main
	assert 'Cvar_Set( "cl_running", "0" );' in cl_main
	assert 'if ( com_cl_running && com_cl_running->integer && CL_GameCommand() ) {' in cmd
	assert 'if ( com_cl_running && com_cl_running->integer && UI_GameCommand() ) {' in cmd
	assert 'data_1205e30 = sub_4ce0d0(x87_r7, "cl_running", U"0", 0x40)' in retail_hlil
	assert 'sub_4cd250("cl_running", U"1")' in retail_hlil

	assert 'Cvar_Get( "cl_downloadItem", "", CVAR_TEMP );' in cl_main
	assert 'Cvar_Set( "cl_downloadItem", itemString );' in cl_main
	assert '(*(data_106b40a8 + 0x24))("cl_downloadItem", &var_d0, 0x40)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x24))("cl_downloadItem",local_d0,0x40);' in ui_ghidra
	assert 'sub_4cd250("cl_downloadItem", sub_4d9220(&data_52d0f4))' in retail_hlil

	assert 'Cvar_Get( "cl_downloadName", "", CVAR_TEMP );' in cl_main
	assert 'Cvar_Set( "cl_downloadName", "" );' in cl_main
	assert 'Cvar_Set( "cl_downloadName", downloadName );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer( "cl_downloadName", downloadName, sizeof(downloadName) );' in ui_main
	assert '(*(data_106b40a8 + 0x24))("cl_downloadName", &arg_110c, 0x400)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x24))("cl_downloadName",acStack_404,0x400);' in ui_ghidra
	assert 'sub_4cd250("cl_downloadName", &data_54f9da)' in retail_hlil
	assert 'sub_4cd250("cl_downloadName", sub_4d9220("Workshop item %i of %i"))' in retail_hlil

	assert 'Cvar_Get( "cl_downloadTime", "0", CVAR_TEMP );' in cl_main
	assert 'Cvar_SetValue( "cl_downloadTime", cls.realtime );' in cl_main
	assert 'CL_GetWorkshopDownloadInfo( itemIdLow, itemIdHigh, &downloaded, &total )' in cl_ui
	assert 'SteamUGC_GetItemDownloadInfo( itemIdLow, itemIdHigh, &downloaded, &total );' in cl_ui
	assert '(*(data_106b40a8 + 0x28))("cl_downloadTime")' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x28))("cl_downloadTime");' in ui_ghidra
	assert 'sub_4cd270("cl_downloadTime", fconvert.s(float.t(data_1528cc8)))' in retail_hlil


def test_engine_cvar_thirtyeighth_client_native_ui_bridge_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_parse = _read_text(CL_PARSE)
	ui_main = _read_text(UI_MAIN)
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	ui_hlil = _read_text(QL_UI_HLIL_PART01)
	ui_ghidra = _read_text(QL_UI_GHIDRA_DECOMPILE)

	assert 'DAT_01627c3c = FUN_004ce0d0("cl_maxpackets",&DAT_0053d9f8,0x200);' in retail_ghidra
	assert 'cl_maxpackets = Cvar_Get ("cl_maxpackets", "125", CVAR_CHEAT );' in cl_main
	assert 'if ( cl_maxpackets->integer < 15 ) {' in cl_input
	assert 'Cvar_Set( "cl_maxpackets", "125" );' in cl_input
	assert 'if ( delta < 1000 / cl_maxpackets->integer ) {' in cl_input
	assert 'trap_Cvar_Set("cl_maxpackets", "30");' in ui_main
	assert 'trap_Cvar_Set("cl_maxpackets", "15");' in ui_main
	assert 'data_1627c3c = sub_4ce0d0(x87_r5, "cl_maxpackets", "125", 0x200)' in retail_hlil
	assert '(*(data_106b40a8 + 0x1c))("cl_maxpackets", &data_1002648c)' in ui_hlil
	assert '(*(data_106b40a8 + 0x1c))("cl_maxpackets", &data_10026480)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x1c))("cl_maxpackets",&DAT_1002648c);' in ui_ghidra

	assert 'DAT_015f672c = FUN_004ce0d0("cl_packetdup",&DAT_00551624,0x80001);' in retail_ghidra
	assert 'cl_packetdup = Cvar_Get ("cl_packetdup", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_packetdup->integer < 0 ) {' in cl_input
	assert 'Cvar_Set( "cl_packetdup", "5" );' in cl_input
	assert 'oldPacketNum = (clc.netchan.outgoingSequence - 1 - cl_packetdup->integer) & PACKET_MASK;' in cl_input
	assert 'trap_Cvar_Set("cl_packetdup", "1");' in ui_main
	assert 'trap_Cvar_Set("cl_packetdup", "2");' in ui_main
	assert 'data_15f672c = sub_4ce0d0(x87_r1, "cl_packetdup", U"1", 0x80001)' in retail_hlil
	assert '(*(data_106b40a8 + 0x1c))("cl_packetdup", &data_1002729c)' in ui_hlil
	assert '(*(data_106b40a8 + 0x1c))("cl_packetdup", &data_100272b0)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x1c))("cl_packetdup",&DAT_1002729c);' in ui_ghidra

	ui_update = _extract_function_block(ui_main, "static void UI_Update(const char *name) {")
	colorbits_start = ui_update.index('} else if (Q_stricmp(name, "r_colorBits") == 0) {')
	colorbits_end = ui_update.index('} else if (Q_stricmp(name, "ui_mousePitch") == 0) {', colorbits_start)
	colorbits_block = ui_update[colorbits_start:colorbits_end]

	assert 'result = sub_100016c0("r_colorBits", 0x1869f, arg1)' in ui_hlil
	assert '(*(data_106b40a8 + 0x1c))("r_depthBits", &data_100252c0)' in ui_hlil
	assert '(*(data_106b40a8 + 0x1c))("r_stencilBits", &data_100252c0)' in ui_hlil
	assert '"ui_glCustom"' not in ui_hlil
	assert '"r_lodBias"' not in ui_hlil
	assert '"r_lodbias"' not in ui_hlil
	assert 'Q_stricmp(name, "r_colorBits") == 0' in colorbits_block
	assert 'trap_Cvar_SetValue( "r_depthBits", 0 );' in colorbits_block
	assert 'trap_Cvar_SetValue( "r_stencilBits", 0 );' in colorbits_block
	assert 'trap_Cvar_SetValue( "r_depthBits", 16 );' in colorbits_block
	assert 'trap_Cvar_SetValue( "r_depthBits", 24 );' in colorbits_block
	assert 'Q_stricmp(name, "r_colorbits") == 0' not in colorbits_block
	assert 'trap_Cvar_SetValue( "r_depthbits",' not in colorbits_block
	assert 'trap_Cvar_SetValue( "r_stencilbits",' not in colorbits_block
	assert 'Q_stricmp(name, "r_lodbias") == 0' not in ui_update
	assert 'Q_stricmp(name, "ui_glCustom") == 0' not in ui_update
	assert 'trap_Cvar_SetValue( "r_fullScreen",' not in ui_update
	assert 'trap_Cvar_SetValue( "r_subdivisions",' not in ui_update
	assert 'trap_Cvar_SetValue( "r_vertexlight",' not in ui_update
	assert 'trap_Cvar_SetValue( "r_lodbias",' not in ui_update
	assert 'trap_Cvar_SetValue( "r_colorbits",' not in ui_update
	assert 'trap_Cvar_SetValue( "r_texturebits",' not in ui_update
	assert 'trap_Cvar_Set( "r_texturemode",' not in ui_update

	assert 'DAT_01647ef8 = FUN_004ce0d0("cl_serverStatusResendTime",&DAT_0053f098,0);' in retail_ghidra
	assert 'cl_serverStatusResendTime = Cvar_Get ("cl_serverStatusResendTime", "750", 0);' in cl_main
	assert 'serverStatus->startTime < Com_Milliseconds() - cl_serverStatusResendTime->integer' in cl_main
	assert 'trap_Cvar_Set("cl_serverStatusResendTime", va("%d", resend));' in ui_main
	assert 'data_1647ef8 = sub_4ce0d0(x87_r3, "cl_serverStatusResendTime", "750", 0)' in retail_hlil
	assert '(*(data_106b40a8 + 0x1c))("cl_serverStatusResendTime",' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x1c))("cl_serverStatusResendTime",uVar3);' in ui_ghidra

	assert 'FUN_004ce0d0("cl_maxPing",&DAT_00539fc0,1);' in retail_ghidra
	assert 'Cvar_Get( "cl_maxPing", "800", CVAR_ARCHIVE );' in cl_main
	assert 'maxPing = Cvar_VariableIntegerValue( "cl_maxPing" );' in cl_main
	assert 'if( maxPing < 100 ) {' in cl_main
	assert 'if (time < maxPing)' in cl_main
	assert 'trap_Cvar_VariableValue("cl_maxPing")' in ui_main
	assert 'sub_4ce0d0(x87_r6, "cl_maxPing", "800", 1)' in retail_hlil
	assert '(*(data_106b40a8 + 0x28))("cl_maxPing")' in ui_hlil

	assert '_DAT_01627c4c = FUN_004ce0d0("cl_motdString",&DAT_0054f9da,0x40);' in retail_ghidra
	assert 'cl_motdString = Cvar_Get( "cl_motdString", "", CVAR_ROM );' in cl_main
	assert 'Cvar_Set( "cl_motdString", challenge );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer( "cl_motdString", uiInfo.serverStatus.motd, sizeof(uiInfo.serverStatus.motd) );' in ui_main
	assert 'data_1627c4c = sub_4ce0d0(x87_r1, "cl_motdString", &data_54f9da, 0x40)' in retail_hlil
	assert '(*(data_106b40a8 + 0x24))("cl_motdString", &data_107644d0, 0x400)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x24))("cl_motdString",&DAT_107644d0,0x400);' in ui_ghidra

	assert 'Cvar_Get( "cl_downloadItem", "", CVAR_TEMP );' in cl_main
	assert 'Cvar_Set( "cl_downloadItem", "" );' in cl_main
	assert 'Cvar_Set( "cl_downloadItem", itemString );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer( "cl_downloadItem", downloadItem, sizeof( downloadItem ) );' in ui_main
	assert '(*(data_106b40a8 + 0x24))("cl_downloadItem", &var_d0, 0x40)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x24))("cl_downloadItem",local_d0,0x40);' in ui_ghidra
	assert 'sub_4cd250("cl_downloadItem", sub_4d9220(&data_52d0f4))' in retail_hlil

	assert 'Cvar_Get( "cl_downloadName", "", CVAR_TEMP );' in cl_main
	assert 'Cvar_Set( "cl_downloadName", "" );' in cl_main
	assert 'Cvar_Set( "cl_downloadName", remoteName );' in cl_main
	assert 'Cvar_Set( "cl_downloadName", downloadName );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer( "cl_downloadName", downloadName, sizeof(downloadName) );' in ui_main
	assert '(*(data_106b40a8 + 0x24))("cl_downloadName", &arg_110c, 0x400)' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x24))("cl_downloadName",acStack_404,0x400);' in ui_ghidra
	assert 'sub_4cd250("cl_downloadName", &data_54f9da)' in retail_hlil
	assert 'sub_4cd250("cl_downloadName", sub_4d9220("Workshop item %i of %i"))' in retail_hlil

	assert 'Cvar_Get( "cl_downloadTime", "0", CVAR_TEMP );' in cl_main
	assert 'Cvar_SetValue( "cl_downloadTime", cls.realtime );' in cl_main
	assert 'downloadTime = trap_Cvar_VariableValue( "cl_downloadTime" );' in ui_main
	assert '(*(data_106b40a8 + 0x28))("cl_downloadTime")' in ui_hlil
	assert '(**(code **)(DAT_106b40a8 + 0x28))("cl_downloadTime");' in ui_ghidra
	assert 'sub_4cd270("cl_downloadTime", fconvert.s(float.t(data_1528cc8)))' in retail_hlil

	assert 'Cvar_Get( "cl_downloadCount", "0", CVAR_TEMP );' in cl_main
	assert 'Cvar_Set( "cl_downloadCount", "0" );' in cl_main
	assert 'Cvar_Set( "cl_downloadCount", downloaded );' in cl_main
	assert 'Cvar_SetValue( "cl_downloadCount", clc.downloadCount );' in cl_parse
	assert 'downloadCount = (unsigned long long)(int)trap_Cvar_VariableValue( "cl_downloadCount" );' in ui_main

	assert 'Cvar_Get( "cl_downloadSize", "0", CVAR_TEMP );' in cl_main
	assert 'Cvar_Set( "cl_downloadSize", "0" );' in cl_main
	assert 'Cvar_Set( "cl_downloadSize", total );' in cl_main
	assert 'Cvar_SetValue( "cl_downloadSize", clc.downloadSize );' in cl_parse
	assert 'downloadSize = (unsigned long long)(int)trap_Cvar_VariableValue( "cl_downloadSize" );' in ui_main

	native_progress_start = ui_hlil.index('(*(data_106b40a8 + 0x24))("cl_downloadItem", &var_d0, 0x40)')
	native_progress_block = ui_hlil[native_progress_start:native_progress_start + 700]
	assert "cl_downloadCount" not in native_progress_block
	assert "cl_downloadSize" not in native_progress_block
	assert '(*(data_106b40a8 + 0x180))(var_14c, var_148, &var_15c, &var_164)' in native_progress_block


def test_engine_cvar_thirtyninth_client_service_disclosure_tranche_matches_guarded_retail_divergence_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	platform_services = _read_text(REPO_ROOT / "src" / "common" / "platform" / "platform_services.c")
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	service_cvars = [
		("cl_onlineServicesMode", "Unavailable", "QL_GetOnlineServicesModeLabel()"),
		("cl_onlineServicesPolicy", "compatibility-unavailable", "QL_GetOnlineServicesPolicyLabel()"),
		("cl_onlineServicesParityScope", "unclassified", "QL_GetOnlineServicesParityScopeLabel()"),
		("cl_onlineServicesParityReason", "unclassified", "QL_GetOnlineServicesParityReasonLabel()"),
		("cl_identityBootstrapMode", "Unavailable", "CL_GetIdentityBootstrapModeLabel()"),
		("cl_identityBootstrapPolicy", "compatibility-unavailable", "CL_GetIdentityBootstrapPolicyLabel()"),
		("cl_voiceServiceMode", "Unavailable", "CL_GetVoiceServiceModeLabel()"),
		("cl_voiceServicePolicy", "compatibility-unavailable", "CL_GetVoiceServicePolicyLabel()"),
		("cl_workshopProvider", "Unavailable", "CL_GetWorkshopServiceProviderLabel()"),
		("cl_workshopPolicy", "compatibility-unavailable", "CL_GetWorkshopServicePolicyLabel()"),
		("cl_matchmakingProvider", "Unavailable", "CL_GetMatchmakingServiceProviderLabel()"),
		("cl_matchmakingPolicy", "compatibility-unavailable", "CL_GetMatchmakingServicePolicyLabel()"),
		("cl_statsProvider", "Unavailable", "CL_GetStatsServiceProviderLabel()"),
		("cl_statsPolicy", "compatibility-unavailable", "CL_GetStatsServicePolicyLabel()"),
		("cl_socialOverlayProvider", "Unavailable", "CL_GetSocialOverlayServiceProviderLabel()"),
		("cl_socialOverlayPolicy", "compatibility-unavailable", "CL_GetSocialOverlayServicePolicyLabel()"),
	]

	for name, default, provider in service_cvars:
		assert f'Cvar_Get ("{name}", "{default}", CVAR_ROM );' in cl_main
		assert f'Cvar_Set( "{name}", {provider} );' in cl_main
		assert f'"{name}"' not in retail_hlil
		assert f'"{name}"' not in retail_ghidra

	assert "static void CL_RefreshPlatformServiceCvars( void ) {" in cl_main
	assert cl_main.count("CL_RefreshPlatformServiceCvars();") >= 2
	assert 'return "Build-disabled default (QL_BUILD_ONLINE_SERVICES=0)";' in platform_services
	assert 'return "compatibility-unavailable";' in platform_services
	assert 'return "permanent-bounded-divergence";' in platform_services
	assert 'return "default builds keep Quake Live online services disabled until a documented open replacement exists";' in platform_services
	assert 'static const char *CL_GetIdentityBootstrapModeLabel( void ) {' in cl_main
	assert 'static const char *CL_GetVoiceServiceModeLabel( void ) {' in cl_main
	assert 'return QL_GetOnlineServicesModeLabel();' in cl_main
	assert 'return QL_GetOnlineServicesPolicyLabel();' in cl_main
	assert 'static const char *CL_GetWorkshopServiceProviderLabel( void ) {' in cl_main
	assert 'return QL_DescribePlatformFeaturePolicy( CL_GetWorkshopServiceDescriptor() );' in cl_main
	assert 'Workshop %s via %s [%s]: %s\\n' in cl_main
	assert 'static const ql_platform_feature_descriptor *CL_GetMatchmakingServiceDescriptor( void ) {' in cl_main
	assert 'static const char *CL_GetMatchmakingServiceProviderLabel( void ) {' in cl_main
	assert 'return QL_DescribePlatformFeaturePolicy( CL_GetMatchmakingServiceDescriptor() );' in cl_main
	assert 'static const ql_platform_feature_descriptor *CL_GetStatsServiceDescriptor( void ) {' in cl_main
	assert 'static const char *CL_GetStatsServiceProviderLabel( void ) {' in cl_main
	assert 'return QL_DescribePlatformFeaturePolicy( CL_GetStatsServiceDescriptor() );' in cl_main
	assert 'static const ql_platform_feature_descriptor *CL_GetSocialOverlayServiceDescriptor( void ) {' in cl_main
	assert 'static const char *CL_GetSocialOverlayServiceProviderLabel( void ) {' in cl_main
	assert 'return QL_DescribePlatformFeaturePolicy( CL_GetSocialOverlayServiceDescriptor() );' in cl_main


def test_engine_cvar_fortieth_client_remaining_cl_surface_matches_resolved_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	client_h = _read_text(REPO_ROOT / "src" / "code" / "client" / "client.h")
	cl_console = _read_text(CL_CONSOLE)
	mac_controller = _read_text(REPO_ROOT / "src" / "code" / "macosx" / "Q3Controller.m")
	retail_hlil = _read_text(QL_STEAM_HLIL_PART04)
	retail_strings = _read_text(QL_STEAM_HLIL_PART06)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	removed_source_only_cvars = [
		"cl_allowDownload",
		"cl_contimestamps",
		"cl_conXOffset",
		"cl_guid",
		"cl_noprint",
		"cl_punkbuster",
		"cl_showBanner",
	]
	checked_sources = [cl_main, client_h, cl_console, mac_controller]

	for name in removed_source_only_cvars:
		for source in checked_sources:
			assert name not in source
		assert f'"{name}"' not in retail_hlil
		assert f'"{name}"' not in retail_strings
		assert f'"{name}"' not in retail_ghidra

	assert 'Con_DrawConsoleLineText( con.xadjust + charWidth, v, text, con.linewidth );' in cl_console
	assert 'Con_DrawConsoleLineText( cl_conXOffset->integer' not in cl_console
	assert 'if ( FS_ComparePaks( clc.downloadList, sizeof( clc.downloadList ) , qtrue ) ) {' in cl_main
	assert 'WARNING: You are missing some files referenced by the server' not in cl_main

	assert 'Cvar_Set( "cl_currentServerAddress", server );' in cl_main
	assert 'CL_WebView_PublishGameStartForAddress( &clc.serverAddress );' in cl_main
	assert 'Cvar_Get( "cl_currentServerAddress"' not in cl_main
	assert 'Cvar_Get ("cl_currentServerAddress"' not in cl_main
	assert 'sub_4cd250("cl_currentServerAddress", eax_2)' in retail_hlil
	assert 'char const data_53e44c[0x18] = "cl_currentServerAddress", 0' in retail_strings

	retail_cl_init_block = retail_hlil[
		retail_hlil.index("004bc690    int32_t __fastcall sub_4bc690")
		:retail_hlil.index('004bccff  sub_4c81d0("record", sub_4b8430)')
	]
	assert '"cl_currentServerAddress"' not in retail_cl_init_block


def test_engine_cvar_fifteenth_server_state_tranche_matches_retail_contracts() -> None:
	common = _read_text(COMMON)
	sv_init = _read_text(SV_INIT)
	sv_main = _read_text(SV_MAIN)
	sv_ccmds = _read_text(SV_CCMDS)
	server_h = _read_text(SERVER_H)
	ui_gameinfo = _read_text(REPO_ROOT / "src" / "code" / "ui" / "ui_gameinfo.c")
	g_main = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_main.c")
	g_vote = _read_text(REPO_ROOT / "src" / "code" / "game" / "g_vote.c")

	assert 'com_ignorecrash = Cvar_Get( "com_ignorecrash", "0", 0 );' in common
	assert 'com_crashed = Cvar_Get( "com_crashed", "0", CVAR_TEMP );' in common
	assert 'com_pid = Cvar_Get( "com_pid", pidString, CVAR_ROM );' in common
	assert 'pidLength = FS_FOpenFileRead( "profile.pid", &f, qtrue );' in common
	assert 'Com_Memset( pidBuffer, 0, sizeof( pidBuffer ) );' in common
	assert 'if ( FS_Read( pidBuffer, sizeof( pidBuffer ) - 1, f ) < 0 ) {' in common
	assert 'if ( com_ignorecrash && com_ignorecrash->integer ) {' in common
	assert 'if ( retainedPid > 0 && com_pid && retainedPid != com_pid->integer ) {' in common
	assert 'Cvar_Set( "com_crashed", "1" );' in common
	assert 'pidValue = com_pid ? com_pid->string : pidString;' in common
	assert 'FS_WriteFile( "profile.pid", pidValue, strlen( pidValue ) );' in common
	assert 'FS_WriteFile( "profile.pid", "0", 1 );' in common

	assert 'sv_hostname = Cvar_Get ("sv_hostname", "noname", CVAR_SERVERINFO | CVAR_ARCHIVE );' in sv_init
	assert 'sv_hostname = Cvar_Get ("sv_hostname", defaultHostname, CVAR_SERVERINFO | CVAR_ARCHIVE );' in sv_init
	assert 'if ( !QL_Steamworks_ServerSetServerName( sv_hostname->string ) ) {' in sv_main
	assert 'Info_SetValueForKey( infostring, NET_GetHostnameInfoKey(), sv_hostname->string );' in sv_main
	assert 'trap_Cvar_VariableStringBuffer( "sv_hostname", hostname, sizeof( hostname ) );' in g_main

	assert 'extern\tcvar_t\t*sv_masterAdvertise;' in server_h
	assert 'sv_masterAdvertise = Cvar_Get ("sv_master", "1", CVAR_ARCHIVE );' in sv_init
	assert 'sv_master[0] = Cvar_Get ("sv_master1", "", 0 );' in sv_init

	assert 'sv_mapPoolFile = Cvar_Get ("sv_mapPoolFile", "mappool.txt", CVAR_ARCHIVE );' in sv_init
	assert 'static const char *fileCvars[] = { "ui_mapPoolFile", "sv_mapPoolFile", NULL };' in ui_gameinfo
	assert 'UI_LoadMapRotationsFromFile( "mappool.txt" );' in ui_gameinfo

	assert 'sv_includeCurrentMapInVote = Cvar_Get ("sv_includeCurrentMapInVote", "0", CVAR_TEMP );' in sv_init

	assert 'sv_gtid = Cvar_Get ("sv_gtid", "", CVAR_SERVERINFO | CVAR_ROM );' in sv_init
	assert 'serverInfo = Cvar_InfoString( CVAR_SERVERINFO );' in sv_main
	assert 'SV_SetConfigstring( CS_SERVERINFO, serverInfo );' in sv_main

	assert 'extern\tcvar_t\t*sv_ammoPack;' in server_h
	assert 'sv_ammoPack = Cvar_Get ("g_ammoPack", "1", CVAR_LATCH );' in sv_init
	assert 'if ( sv_maxclients->modified || sv_gametype->modified || ( sv_ammoPack && sv_ammoPack->modified ) ) {' in sv_ccmds
	assert 'trap_Cvar_Set( "g_ammoPack", "0" );' in g_vote
	assert 'trap_Cvar_Set( "g_ammoPack", "1" );' in g_vote

	assert 'sv_idleRestart = Cvar_Get ("sv_idleRestart", "1", 0 );' in sv_init
	assert 'if ( sv_idleRestart && sv_idleRestart->integer && svs.time > 0x5265c00 && SV_CountActiveHumanClients() == 0 ) {' in sv_main
	assert 'SV_Shutdown( "Restarting idle server" );' in sv_main
	assert 'Cbuf_AddText( "vstr nextmap\\n" );' in sv_main

	assert 'sv_quitOnEmpty = Cvar_Get ("sv_quitOnEmpty", "0", 0 );' in sv_init
	assert 'if ( sv_quitOnEmpty && sv_quitOnEmpty->integer > 0 ) {' in sv_main
	assert 'Com_Printf( "server has been empty for %d seconds, quit\\n", sv_quitOnEmpty->integer );' in sv_main
	assert 'Cbuf_AddText( "quit\\n" );' in sv_main


def test_engine_cvar_sixteenth_win32_input_tranche_matches_retail_contracts() -> None:
	win_input = _read_text(WIN_INPUT)

	assert 'in_midi\t\t\t\t\t= Cvar_Get ("in_midi",\t\t\t\t\t"0",\t\tCVAR_ARCHIVE);' in win_input
	assert 'Cmd_AddCommand( "midiinfo", MidiInfo_f );' in win_input
	assert 'Com_Printf( "\\nMIDI control:       %s\\n", enableStrings[in_midi->integer != 0] );' in win_input
	assert 'if ( !Cvar_VariableValue( "in_midi" ) )' in win_input

	assert 'in_midiport\t\t\t\t= Cvar_Get ("in_midiport",\t\t\t\t"1",\t\tCVAR_ARCHIVE);' in win_input
	assert 'Com_Printf( "port:               %d\\n", in_midiport->integer );' in win_input

	assert 'in_midichannel\t\t\t= Cvar_Get ("in_midichannel",\t\t\t"1",\t\tCVAR_ARCHIVE);' in win_input
	assert 'if ( ( ( message & 0x0f ) + 1 ) == in_midichannel->integer )' in win_input

	assert 'in_mididevice\t\t\t= Cvar_Get ("in_mididevice",\t\t\t"0",\t\tCVAR_ARCHIVE);' in win_input
	assert 'Com_Printf( "current device:     %d\\n", in_mididevice->integer );' in win_input
	assert 'midiInOpen( &s_midiInfo.hMidiIn,' in win_input
	assert 'in_mididevice->integer,' in win_input

	assert 'in_debugMouse\t\t\t= Cvar_Get ("in_debugMouse",\t\t\t"0",\t\tCVAR_TEMP);' in win_input
	assert 'if ( in_debugMouse && in_debugMouse->integer ) {' in win_input
	assert 'Com_Printf( "Raw Input buffer overflow!\\n" );' in win_input

	assert 'in_joystick\t\t\t\t= Cvar_Get ("in_joystick",\t\t\t\t"1",\t\tCVAR_ARCHIVE|CVAR_LATCH);' in win_input
	assert 'if (! in_joystick->integer ) {' in win_input
	assert 'in_joystick->modified = qfalse;' in win_input

	assert 'in_joyBallScale\t\t\t= Cvar_Get ("in_joyBallScale",\t\t\t"1.0",\t\tCVAR_ARCHIVE);' in win_input

	assert 'in_debugJoystick\t\t= Cvar_Get ("in_debugjoystick",\t\t\t"0",\t\tCVAR_TEMP);' in win_input
	assert 'if ( in_debugJoystick->integer ) {' in win_input
	assert 'Com_Printf( "%8x %5i %5.2f %5.2f %5.2f %5.2f %6i %6i\\n",' in win_input

	assert 'joy_threshold\t\t\t= Cvar_Get ("joy_threshold",\t\t\t"0.15",\t\tCVAR_ARCHIVE);' in win_input
	assert 'if ( fAxisValue < -joy_threshold->value ) {' in win_input
	assert '} else if ( fAxisValue > joy_threshold->value ) {' in win_input

	assert 'in_nograb\t\t\t\t= Cvar_Get ("in_nograb",\t\t\t\t"0",\t\tCVAR_TEMP);' in win_input
	assert 'if ( s_wmv.mouseActive && ( !in_nograb || !in_nograb->integer ) ) {' in win_input
	assert 'if ( in_nograb && in_nograb->integer ) {' in win_input
	assert 'IN_DeactivateMouse();' in win_input


def test_engine_cvar_seventeenth_network_bootstrap_tranche_matches_retail_contracts() -> None:
	net_chan = _read_text(NET_CHAN)
	win_net = _read_text(WIN_NET)
	cl_main = _read_text(CL_MAIN)
	common = _read_text(COMMON)
	sv_zmq = _read_text(REPO_ROOT / "src" / "code" / "server" / "sv_zmq.c")

	assert 'qport = Cvar_Get ("net_qport", va("%i", port), CVAR_INIT );' in net_chan
	assert 'if ( chan->sock == NS_CLIENT && NET_ProtocolUsesNetchanClientQport() ) {' in net_chan
	assert 'if ( chan->sock == NS_SERVER && NET_ProtocolUsesNetchanClientQport() ) {' in net_chan
	assert 'MSG_WriteShort( &send, qport->integer );' in net_chan
	assert 'port = Cvar_VariableValue ("net_qport");' in cl_main
	assert 'if ( NET_ProtocolUsesClientQport() ) {' in cl_main
	assert 'Info_SetValueForKey( info, NET_GetQportInfoKey(), va("%i", port ) );' in cl_main
	assert 'Netchan_Setup (NS_CLIENT, &clc.netchan, from, Cvar_VariableValue( "net_qport" ) );' in cl_main

	assert 'ip = Cvar_Get( "net_ip", "localhost", CVAR_LATCH );' in win_net
	assert 'Cvar_VariableStringBuffer( "net_ip", netIp, sizeof( netIp ) );' in common
	assert 'Cvar_VariableStringBuffer( "net_ip", resolvedIp, sizeof( resolvedIp ) );' in sv_zmq

	assert 'netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );' in win_net
	assert 'Cvar_SetValue( "net_port", port + i );' in win_net
	assert 'netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );' in common
	assert 'netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );' in sv_zmq
	assert 's_zmqRconEnable = Cvar_Get( "zmq_rcon_enable", "0", CVAR_INIT );' in sv_zmq
	assert 's_zmqStatsEnable = Cvar_Get( "zmq_stats_enable", "0", CVAR_INIT );' in sv_zmq
	assert 's_zmqRconIp = Cvar_Get( "zmq_rcon_ip", "0.0.0.0", CVAR_INIT );' in sv_zmq
	assert 's_zmqRconPort = Cvar_Get( "zmq_rcon_port", "28960", CVAR_INIT );' in sv_zmq
	assert 's_zmqStatsIp = Cvar_Get( "zmq_stats_ip", "", CVAR_INIT );' in sv_zmq
	assert 's_zmqStatsPort = Cvar_Get( "zmq_stats_port", "", CVAR_INIT );' in sv_zmq
	assert 's_zmqStatsPassword = Cvar_Get( "zmq_stats_password", "", CVAR_ARCHIVE );' in sv_zmq
	assert 's_zmqRconPassword = Cvar_Get( "zmq_rcon_password", "", CVAR_ARCHIVE );' in sv_zmq
	assert 'Cvar_Get( "zmq_stats_password", "", CVAR_ARCHIVE | CVAR_PROTECTED );' not in sv_zmq
	assert 'Cvar_Get( "zmq_rcon_password", "", CVAR_ARCHIVE | CVAR_PROTECTED );' not in sv_zmq

	assert 'net_strict = Cvar_Get( "net_strict", "0", 0 );' in win_net
	assert 'if ( net_strict->integer ) {' in win_net
	assert 'Com_Error( ERR_FATAL, "net_strict enabled: couldn\'t allocate %s:%d", ip->string, port );' in win_net

	assert 'net_noudp = Cvar_Get( "net_noudp", "0", CVAR_LATCH | CVAR_ARCHIVE );' in win_net
	assert 'if( net_noudp && net_noudp->modified ) {' in win_net
	assert 'if (! net_noudp->integer ) {' in win_net

	assert 'net_socksEnabled = Cvar_Get( "net_socksEnabled", "0", CVAR_LATCH | CVAR_ARCHIVE );' in win_net
	assert 'if ( net_socksEnabled->integer ) {' in win_net
	assert 'NET_OpenSocks( port );' in win_net
	assert 'NET_OpenSocks( port + i );' in win_net

	assert 'net_socksServer = Cvar_Get( "net_socksServer", "", CVAR_LATCH | CVAR_ARCHIVE );' in win_net
	assert 'h = gethostbyname( net_socksServer->string );' in win_net

	assert 'net_socksPort = Cvar_Get( "net_socksPort", "1080", CVAR_LATCH | CVAR_ARCHIVE );' in win_net
	assert 'address.sin_port = htons( (short)net_socksPort->integer );' in win_net

	assert 'net_socksUsername = Cvar_Get( "net_socksUsername", "", CVAR_LATCH | CVAR_ARCHIVE );' in win_net
	assert 'ulen = strlen( net_socksUsername->string );' in win_net
	assert 'memcpy( &buf[2], net_socksUsername->string, ulen );' in win_net

	assert 'net_socksPassword = Cvar_Get( "net_socksPassword", "", CVAR_LATCH | CVAR_ARCHIVE );' in win_net
	assert 'plen = strlen( net_socksPassword->string );' in win_net
	assert 'memcpy( &buf[3 + ulen], net_socksPassword->string, plen );' in win_net


def test_engine_network_event_wait_path_matches_retail_contracts() -> None:
	win_net = _read_text(WIN_NET)

	assert 'static WSAEVENT\tip_socket_event = (WSAEVENT)INVALID_HANDLE_VALUE;' in win_net
	assert win_net.count( 'hEventObject = CreateEventA( NULL, qfalse, qfalse, NULL );' ) == 2
	assert win_net.count( 'ip_socket_event = hEventObject;' ) == 2
	assert win_net.count( 'WSAEventSelect( ip_socket, hEventObject, FD_READ );' ) == 2
	assert 'WSACloseEvent( ip_socket_event );' in win_net
	assert 'ip_socket_event = (WSAEVENT)INVALID_HANDLE_VALUE;' in win_net
	assert win_net.index( 'WSACloseEvent( ip_socket_event );' ) < win_net.index( 'closesocket( ip_socket );' )
	assert 'if ( ip_socket_event != (WSAEVENT)INVALID_HANDLE_VALUE ) {' in win_net
	assert 'WSAWaitForMultipleEvents( 1, &ip_socket_event, qfalse, msec, qtrue );' in win_net


def test_engine_network_address_string_parsers_match_retail_contracts() -> None:
	win_net = _read_text(WIN_NET)

	assert 'qboolean Sys_StringToSockaddr( const char *s, struct sockaddr *sadr ) {' in win_net
	assert '((struct sockaddr_in *)sadr)->sin_family = AF_INET;' in win_net
	assert 'if( s[0] >= \'0\' && s[0] <= \'9\' ) {' in win_net
	assert '*(int *)&((struct sockaddr_in *)sadr)->sin_addr = inet_addr(s);' in win_net
	assert 'if( ( h = gethostbyname( s ) ) == 0 ) {' in win_net
	assert '*(int *)&((struct sockaddr_in *)sadr)->sin_addr = *(int *)h->h_addr_list[0];' in win_net

	assert 'qboolean Sys_StringToAdr( const char *s, netadr_t *a ) {' in win_net
	assert '*(int *)&a->ip = inet_addr(s);' in win_net
	assert '*(int *)&a->ip = *(int *)h->h_addr_list[0];' in win_net
	assert 'a->type = NA_IP;' in win_net
	assert 'a->port = 0;' in win_net

	assert 'if( ( strlen( s ) == 21 ) && ( s[8] == \'.\' ) ) {' not in win_net


def test_engine_win32_network_transport_matches_retail_contracts() -> None:
	win_net = _read_text(WIN_NET)

	assert 'static cvar_t\t*net_noipx;' not in win_net
	assert 'static SOCKET\tipx_socket;' not in win_net

	assert 'else if( a->type == NA_IPX ) {' not in win_net
	assert 'else if( a->type == NA_BROADCAST_IPX ) {' not in win_net
	assert 'else if( s->sa_family == AF_IPX ) {' not in win_net

	assert 'for( protocol = 0 ; protocol < 2 ; protocol++ )' not in win_net
	assert 'ret = recvfrom( ip_socket, net_message->data, net_message->maxsize, 0, (struct sockaddr *)&from, &fromlen );' in win_net
	assert 'if( !ip_socket ) {' in win_net
	assert 'net_socket = ipx_socket;' not in win_net
	assert 'if( to.type != NA_BROADCAST && to.type != NA_IP ) {' in win_net
	assert 'if( ( err == WSAEADDRNOTAVAIL ) && to.type == NA_BROADCAST ) {' in win_net
	assert 'if( adr.type == NA_IPX ) {' not in win_net

	assert 'int NET_IPXSocket( int port ) {' not in win_net
	assert 'void NET_OpenIPX( void ) {' not in win_net

	assert 'net_noudp = Cvar_Get( "net_noudp", "0", CVAR_LATCH | CVAR_ARCHIVE );' in win_net
	assert 'net_noipx = Cvar_Get( "net_noipx", "0", CVAR_LATCH | CVAR_ARCHIVE );' not in win_net
	assert 'if( net_noudp->integer ) {' in win_net
	assert 'if( net_noudp->integer && net_noipx->integer ) {' not in win_net
	assert 'if (! net_noudp->integer ) {' in win_net
	assert 'NET_OpenIPX();' not in win_net


def test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts() -> None:
	snd_dma = _read_text(SND_DMA)
	snd_mix = _read_text(SND_MIX)
	cg_view = _read_text(CG_VIEW)
	cg_servercmds = _read_text(CG_SERVERCMDS)

	init_start = snd_dma.index("void S_Init( void ) {")
	init_end = snd_dma.index("\tif ( !cv->integer ) {", init_start)
	init_registrations = [
		line.strip()
		for line in snd_dma[init_start:init_end].splitlines()
		if "Cvar_Get" in line and '"s_' in line
	]
	assert init_registrations == [
		's_announcerVolume = Cvar_GetBounded( "s_announcerVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		's_doppler = Cvar_Get( "s_doppler", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );',
		'cv = Cvar_Get ("s_initsound", "1", 0);',
		's_mixahead = Cvar_Get( "s_mixahead", "0.140", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );',
		's_mixPreStep = Cvar_Get( "s_mixPreStep", "0.05", CVAR_ARCHIVE | CVAR_PROTECTED );',
		's_musicVolume = Cvar_GetBounded( "s_musicvolume", "0.5", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		's_pvs = Cvar_GetBounded( "s_pvs", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		's_voiceVolume = Cvar_GetBounded( "s_voiceVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
		's_voiceStep = Cvar_Get( "s_voiceStep", "0.02", CVAR_ARCHIVE | CVAR_PROTECTED );',
		's_show = Cvar_Get ("s_show", "0", CVAR_CHEAT);',
		's_testsound = Cvar_Get ("s_testsound", "0", CVAR_CHEAT);',
		's_volume = Cvar_GetBounded( "s_volume", "0.8", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );',
	]

	assert 's_announcerVolume = Cvar_GetBounded( "s_announcerVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'if ( entchannel == CHAN_ANNOUNCER && s_announcerVolume ) {' not in snd_dma
	assert "s_announcerVolume->value" not in snd_dma
	assert 'trap_S_StartLocalSound( sfx, CHAN_ANNOUNCER );' in cg_view

	assert 's_doppler = Cvar_Get( "s_doppler", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in snd_dma
	assert 'if (s_doppler->integer && VectorLengthSquared(velocity)>0.0) {' in snd_dma

	assert 'cv = Cvar_Get ("s_initsound", "1", 0);' in snd_dma
	assert 'if ( !cv->integer ) {' in snd_dma
	assert 'Com_Printf ("not initializing.\\n");' in snd_dma

	update_start = snd_dma.index("void S_Update_(void) {")
	update_end = snd_dma.index("console functions", update_start)
	update_block = snd_dma[update_start:update_end]

	assert 's_mixahead = Cvar_Get( "s_mixahead", "0.140", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in snd_dma
	assert 'ma = s_mixahead->value * dma.speed;' in update_block
	assert 'endtime = s_soundtime + ma;' in update_block
	assert 'op = s_mixPreStep->value + sane*dma.speed*0.01;' not in update_block
	assert 'lastTime' not in update_block

	assert 's_mixPreStep = Cvar_Get( "s_mixPreStep", "0.05", CVAR_ARCHIVE | CVAR_PROTECTED );' in snd_dma
	assert 's_paintedtime = s_soundtime + s_mixPreStep->value * dma.speed;' in snd_dma

	assert 's_musicVolume = Cvar_GetBounded( "s_musicvolume", "0.5", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'musicVolume = (musicVolume + (s_musicVolume->value * 2))/4.0f;' in snd_dma

	assert 's_pvs = Cvar_GetBounded( "s_pvs", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'if ( s_pvs && s_pvs->integer && !S_OriginInPVS( listener_origin, origin ) ) {' in snd_dma

	assert 's_show = Cvar_Get ("s_show", "0", CVAR_CHEAT);' in snd_dma
	assert 'if ( s_show->integer == 1 ) {' in snd_dma
	assert 'if ( s_show->integer == 2 ) {' in snd_dma

	assert 's_testsound = Cvar_Get ("s_testsound", "0", CVAR_CHEAT);' in snd_dma
	assert 'if ( s_testsound->integer ) {' in snd_mix

	assert 's_voiceVolume = Cvar_GetBounded( "s_voiceVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'else if ( entchannel == CHAN_VOICE && s_voiceVolume ) {' not in snd_dma
	assert 'if ( s_voiceVolume && s_voiceVolume->value > 0.0f ) {' in snd_mix
	assert 'trap_S_StartLocalSound( vchat->snd, CHAN_VOICE);' in cg_servercmds

	assert 's_voiceStep = Cvar_Get( "s_voiceStep", "0.02", CVAR_ARCHIVE | CVAR_PROTECTED );' in snd_dma
	assert 'startSample += (int)( s_voiceStep->value * dma.speed );' in snd_dma

	assert 's_volume = Cvar_GetBounded( "s_volume", "0.8", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'snd_vol = s_volume->value*255;' in snd_mix
	assert 'ch->master_vol = (int)( volume * 127.0f );' in snd_dma
	assert 'ch->master_vol = S_ChannelMasterVolume( entchannel );' not in snd_dma


def test_engine_cvar_nineteenth_win32_joystick_analog_tranche_matches_retail_contracts() -> None:
	win_input = _read_text(WIN_INPUT)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	common = _read_text(COMMON)

	assert 'in_mouse\t\t\t\t= Cvar_Get ("in_mouse",\t\t\t\t\t"2",\t\tCVAR_ARCHIVE|CVAR_LATCH|CVAR_CLOUD);' in win_input

	assert 'in_joystickInverted' in win_input
	assert 'Cvar_Get ("in_joystick_inverted",' in win_input
	assert '"0",\t\tCVAR_ARCHIVE);' in win_input

	assert 'in_joyHorizViewSensitivity' in win_input
	assert 'Cvar_Get ("in_joyHorizViewSensitivity",\t"20.0",\tCVAR_ARCHIVE);' in win_input
	assert 'in_joyVertViewSensitivity' in win_input
	assert 'Cvar_Get ("in_joyVertViewSensitivity",\t"15.0",\tCVAR_ARCHIVE);' in win_input
	assert 'in_joyHorizViewDeadzone' in win_input
	assert 'Cvar_Get ("in_joyHorizViewDeadzone",\t"0.15",\tCVAR_ARCHIVE);' in win_input
	assert 'in_joyVertViewDeadzone' in win_input
	assert 'Cvar_Get ("in_joyVertViewDeadzone",\t"0.15",\tCVAR_ARCHIVE);' in win_input
	assert 'in_joyHorizMoveDeadzone' in win_input
	assert 'Cvar_Get ("in_joyHorizMoveDeadzone",\t"0.50",\tCVAR_ARCHIVE);' in win_input
	assert 'in_joyVertMoveDeadzone' in win_input
	assert 'Cvar_Get ("in_joyVertMoveDeadzone",\t"0.15",\tCVAR_ARCHIVE);' in win_input

	assert 'joy.oldmoveaxisstate[AXIS_SIDE] = 0;' in win_input
	assert 'joy.oldmoveaxisstate[AXIS_FORWARD] = 0;' in win_input
	assert 'Cvar_Set( "ui_joyavail", "0" );' in win_input
	assert 'Cvar_Set( "ui_joyavail", "1" );' in win_input

	assert 'Sys_QueEvent( g_wv.sysMsgTime, SE_JOYSTICK_AXIS, axis, value, 0, NULL );' in win_input
	assert 'side = IN_JoyRoundToInt( fAxisValue * in_joyBallScale->value * 127.0f );' in win_input
	assert 'IN_QueueJoystickAxis( AXIS_SIDE, side );' in win_input
	assert 'forward = IN_JoyRoundToInt( fAxisValue * in_joyBallScale->value * 127.0f );' in win_input
	assert 'IN_QueueJoystickAxis( AXIS_FORWARD, forward );' in win_input
	assert 'for (i = 2; i < joy.jc.wNumAxes && i < 4 ; i++) {' in win_input

	assert 'if ( joy.jc.wNumAxes >= 5 ) {' in win_input
	assert 'x = IN_JoyMouseMove( JoyToF( joy.ji.dwRpos ), in_joyHorizViewDeadzone->value, in_joyHorizViewSensitivity->value, qfalse );' in win_input
	assert 'y = IN_JoyMouseMove( JoyToF( joy.ji.dwUpos ), in_joyVertViewDeadzone->value, in_joyVertViewSensitivity->value, in_joystickInverted && in_joystickInverted->integer );' in win_input
	assert 'accel = cl_viewAccel ? cl_viewAccel->value : 1.0f;' in win_input
	assert 'move = powf( fabsf( move ), accel ) * sign;' in win_input
	assert 'Sys_QueEvent( g_wv.sysMsgTime, SE_MOUSE, x, y, 0, NULL );' in win_input

	assert 'void CL_JoystickEvent( int axis, int value, int time ) {' in cl_input
	assert 'cl.joystickAxis[axis] = value;' in cl_input
	assert 'case SE_JOYSTICK_AXIS:' in common


def test_engine_cvar_twentieth_client_debug_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_scrn = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_scrn.c")
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	client_h = _read_text(REPO_ROOT / "src" / "code" / "client" / "client.h")

	assert 'cl_freezeDemo = Cvar_Get ("cl_freezeDemo", "0", CVAR_TEMP );' in cl_main
	assert 'if ( clc.demoplaying && cl_freezeDemo->integer ) {' in cl_cgame
	assert '// cl_freezeDemo is used to lock a demo in place for single frame advances' in cl_cgame

	assert 'cl_mouseAccelDebug = Cvar_Get ("cl_mouseAccelDebug", "0", 0 );' in cl_main
	assert 'CL_UpdateMouseAccelDebugLog();' in cl_input
	assert 'if ( !cl_mouseAccelDebug || !cl_mouseAccelDebug->integer ) {' in cl_input
	assert 'fclose( cl_mouseAccelDebugLog );' in cl_input
	assert 'fprintf( cl_mouseAccelDebugLog, "\\n" );' in cl_input
	assert 'cl_mouseAccelStyle' not in cl_main
	assert 'cl_mouseAccelStyle' not in client_h

	assert 'cl_nodelta = Cvar_Get ("cl_nodelta", "0", 0);' in cl_input
	assert 'if ( cl_nodelta->integer || !cl.snap.valid || clc.demowaiting' in cl_input

	assert 'cl_debugMove = Cvar_Get ("cl_debugMove", "0", 0);' in cl_input
	assert 'if ( cl_debugMove->integer ) {' in cl_input
	assert 'if ( cl_debugMove->integer == 1 ) {' in cl_input
	assert 'if ( cl_debugMove->integer == 2 ) {' in cl_input
	assert 'if ( cl_debuggraph->integer || cl_timegraph->integer || cl_debugMove->integer ) {' in cl_scrn

	assert 'cl_timegraph = Cvar_Get ("timegraph", "0", CVAR_CHEAT);' in cl_scrn
	assert 'if ( cl_timegraph->integer ) {' in cl_main

	assert 'cl_debuggraph = Cvar_Get ("debuggraph", "0", CVAR_CHEAT);' in cl_scrn
	assert 'if ( cl_debuggraph->integer || cl_timegraph->integer || cl_debugMove->integer ) {' in cl_scrn

	assert 'cl_graphheight = Cvar_Get ("graphheight", "32", CVAR_CHEAT);' in cl_scrn
	assert 're.DrawStretchPic(x, y - cl_graphheight->integer,' in cl_scrn
	assert 'h = (int)v % cl_graphheight->integer;' in cl_scrn

	assert 'cl_graphscale = Cvar_Get ("graphscale", "1", CVAR_CHEAT);' in cl_scrn
	assert 'v = v * cl_graphscale->integer + cl_graphshift->integer;' in cl_scrn

	assert 'cl_graphshift = Cvar_Get ("graphshift", "0", CVAR_CHEAT);' in cl_scrn
	assert 'v = v * cl_graphscale->integer + cl_graphshift->integer;' in cl_scrn

	assert 'cl_showmouserate' not in cl_main
	assert 'cl_showMouseRate' not in cl_main
	assert 'cl_showmouserate' not in cl_input
	assert 'cl_showMouseRate' not in cl_input
	assert 'cl_showMouseRate' not in client_h


def test_engine_cvar_twentyfirst_renderer_mode_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	win_glimp = _read_text(WIN_GLIMP)
	win_wndproc = _read_text(WIN_WNDPROC)
	cvar = _read_text(QCOMMON_CVAR)

	assert 'if (!Q_stricmp(var_name, var->name)) {' in cvar

	assert 'r_texturebits = ri.Cvar_Get( "r_textureBits", "32", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_texturebits = ri.Cvar_Get( "r_texturebits", "32", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' not in tr_init
	assert 'ri.Printf( PRINT_ALL, "texture bits: %d\\n", r_texturebits->integer );' in tr_init

	assert 'r_colorbits = ri.Cvar_Get( "r_colorBits", "32", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'dm.dmBitsPerPel = r_colorbits->integer;' in win_glimp

	assert 'r_stencilbits = ri.Cvar_Get( "r_stencilBits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_stencilbits = ri.Cvar_Get( "r_stencilbits", "8", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' not in tr_init
	assert 'stencilbits = r_stencilbits->integer;' in win_glimp

	assert 'r_depthbits = ri.Cvar_Get( "r_depthBits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'depthbits = r_depthbits->integer;' in win_glimp

	assert 'r_mode = ri.Cvar_Get( "r_mode", "-2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'return r_mode->integer;' in tr_init
	assert 'ri.Printf( PRINT_WARNING, "WARNING: invalid r_mode %d, resetting to 3\\n", r_mode->integer );' in tr_init
	assert 'ri.Cvar_Set( "r_mode", "3" );' in tr_init
	assert 'if ( mode < -2 ) {' in tr_init
	assert 'if ( mode == -2 ) {' in tr_init

	assert 'r_fullscreen = ri.Cvar_Get( "r_fullscreen", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_fullscreen = Cvar_Get ("r_fullscreen", "1", CVAR_ARCHIVE | CVAR_LATCH );' in win_wndproc

	assert 'r_windowedMode = ri.Cvar_Get( "r_windowedMode", "12", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'r_windowedWidth = ri.Cvar_Get( "r_windowedWidth", "1600", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'r_windowedHeight = ri.Cvar_Get( "r_windowedHeight", "1024", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'return r_windowedMode->integer;' in tr_init
	assert 'WARNING: invalid r_windowedMode' not in tr_init
	assert 'WARNING: invalid r_windowedWidth' not in tr_init
	assert 'WARNING: invalid r_windowedHeight' not in tr_init
	assert 'if ( *width <= 0 || *height <= 0 ) {' not in tr_init
	assert 'Cvar_SetValue( "r_windowedMode", -1 );' in win_wndproc

	assert 'r_customwidth = ri.Cvar_Get( "r_customWidth", "1600", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert '*width = r_customwidth->integer;' in tr_init
	assert 'ri.Printf( PRINT_WARNING, "WARNING: invalid r_customWidth %d, resetting to 1600\\n", r_customwidth->integer );' in tr_init
	assert 'ri.Cvar_Set( "r_customWidth", "1600" );' in tr_init

	assert 'r_customheight = ri.Cvar_Get( "r_customHeight", "1024", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert '*height = r_customheight->integer;' in tr_init
	assert 'ri.Printf( PRINT_WARNING, "WARNING: invalid r_customHeight %d, resetting to 1024\\n", r_customheight->integer );' in tr_init
	assert 'ri.Cvar_Set( "r_customHeight", "1024" );' in tr_init

	assert 'r_aspectRatio = ri.Cvar_Get( "r_aspectRatio", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_aspectRatio, 0, 3, qtrue );' in tr_init
	assert 'int\t\t\taspectRatio;' in tr_init
	assert '*aspectRatio = R_GetModeAspectRatioPreset( *width, *height );' in tr_init
	assert '*aspectRatio = vm->aspectRatio;' in tr_init
	assert '{ "Mode 17: 1280x1024",\t\t1280,\t1024,\t3 },' in tr_init
	assert 'static qboolean GLW_GetModeInfo( int *width, int *height, int *aspectRatio, int mode, qboolean fullscreen )' in win_glimp
	assert 'if ( mode != -2 )' in win_glimp
	assert 'if ( devmode.dmBitsPerPel == 32 && devmode.dmPelsWidth > bestWidth )' in win_glimp
	assert 'ri.Cvar_Set( "r_aspectRatio", va( "%d", modeAspect ) );' in win_glimp

	assert 'r_windowedWidth = Cvar_Get( "r_windowedWidth", "0", CVAR_ARCHIVE );' in win_wndproc
	assert 'r_windowedHeight = Cvar_Get( "r_windowedHeight", "0", CVAR_ARCHIVE );' in win_wndproc
	assert 'if ( r_windowedWidth->integer != rect.right || r_windowedHeight->integer != rect.bottom ) {' in win_wndproc
	assert 'Cvar_SetValue( "r_windowedWidth", rect.right );' in win_wndproc
	assert 'Cvar_SetValue( "r_windowedHeight", rect.bottom );' in win_wndproc


def test_engine_cvar_twentysecond_renderer_startup_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	win_glimp = _read_text(WIN_GLIMP)
	win_input = _read_text(WIN_INPUT)
	cl_main = _read_text(CL_MAIN)
	tr_shader = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shader.c")
	tr_image = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c")
	tr_bsp = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_bsp.c")
	tr_scene = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_scene.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")

	assert 'r_glDriver = ri.Cvar_Get( "r_glDriver", OPENGL_DRIVER_NAME, CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( !GLW_LoadOpenGL( r_glDriver->string ) )' in win_glimp
	assert 'if ( !Q_stricmp( r_glDriver->string, OPENGL_DRIVER_NAME ) )' in win_glimp
	assert 'else if ( !Q_stricmp( r_glDriver->string, _3DFX_DRIVER_NAME ) )' in win_glimp
	assert 'cls.keyCatchers & ~( KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS )' in win_input

	assert 'r_allowExtensions = ri.Cvar_Get( "r_allowExtensions", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( !r_allowExtensions->integer )' in win_glimp

	assert 'r_detailTextures = ri.Cvar_Get( "r_detailtextures", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( pStage->isDetail && !r_detailTextures->integer ) {' in tr_shader

	assert 'r_stereo = ri.Cvar_Get( "r_stereo", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'GLW_CreatePFD( &pfd, colorbits, depthbits, stencilbits, r_stereo->integer );' in win_glimp
	assert 'if ( !( pfd.dwFlags & PFD_STEREO ) && ( r_stereo->integer != 0 ) )' in win_glimp

	assert 'r_simpleMipMaps = ri.Cvar_Get( "r_simpleMipMaps", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( !r_simpleMipMaps->integer ) {' in tr_image

	assert 'r_vertexLight = ri.Cvar_Get( "r_vertexLight", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'if ( r_vertexLight->integer || glConfig.hardwareType == GLHW_PERMEDIA2 ) {' in tr_bsp
	assert 'if ( pStage->bundle[0].vertexLightmap && ( (r_vertexLight->integer && !r_uiFullScreen->integer) || glConfig.hardwareType == GLHW_PERMEDIA2 ) && r_lightmap->integer )' in tr_shade
	assert 'r_vertexLight->integer == 1 ||' in tr_scene

	assert 'r_smp = ri.Cvar_Get( "r_smp", "0", CVAR_ROM );' in tr_init
	assert 'if ( r_smp->integer ) {' in tr_scene
	assert 'if ( !r_smp->integer ) {' in tr_cmds
	assert 'if ( !r_smp->integer || data == backEndData[0]->commands.cmds ) {' in tr_backend
	assert 'if (r_smp->integer) {' in tr_shader

	assert 'r_ignoreFastPath = ri.Cvar_Get( "r_ignoreFastPath", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_ignoreFastPath->integer )' in tr_shader

	assert 'r_displayRefresh = ri.Cvar_Get( "r_displayRefresh", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_displayRefresh, 0, 240, qtrue );' in tr_init
	assert 'dm.dmDisplayFrequency = r_displayRefresh->integer;' in win_glimp

	assert 'r_noFastRestart = ri.Cvar_Get( "r_noFastRestart", "0", CVAR_ARCHIVE );' in tr_init
	assert 'AssertCvarRange( r_noFastRestart, 0, 1, qtrue );' in tr_init
	assert 'if ( !Cvar_VariableIntegerValue( "r_noFastRestart" ) && Cmd_Argc() > 1 && !Q_stricmp( Cmd_Argv( 1 ), "fast" ) ) {' in cl_main


def test_engine_cvar_twentythird_renderer_runtime_tuning_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_main = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_main.c")
	tr_sky = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_sky.c")
	tr_scene = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_scene.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	tr_image = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c")
	tr_surface = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_surface.c")
	win_glimp = _read_text(WIN_GLIMP)

	assert 'r_fastsky = ri.Cvar_Get( "r_fastSky", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'if ( r_noportals->integer || (r_fastsky->integer == 1) ) {' in tr_main
	assert 'if ( r_fastsky->integer ) {' in tr_sky
	assert 'if ( r_fastsky->integer && !( backEnd.refdef.rdflags & RDF_NOWORLDMODEL ) )' in tr_backend

	assert 'r_dynamiclight = ri.Cvar_Get( "r_dynamicLight", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'if ( r_dynamiclight->integer == 0 ||' in tr_scene

	assert 'r_teleporterFlash = ri.Cvar_Get( "r_teleporterFlash", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_teleporterFlash, 0, 1, qtrue );' in tr_init
	assert 'if ( !r_teleporterFlash || !r_teleporterFlash->integer ) {' in tr_backend
	assert 'ri.Printf( PRINT_DEVELOPER, "QA: r_teleporterFlash overlay active\\n" );' in tr_backend

	assert 'r_textureMode = ri.Cvar_Get( "r_textureMode", "GL_LINEAR_MIPMAP_LINEAR", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'GL_TextureMode( r_textureMode->string );' in tr_cmds
	assert 'ri.Cvar_Set( "r_textureMode", "GL_LINEAR_MIPMAP_NEAREST" );' in win_glimp

	assert 'r_swapInterval = ri.Cvar_Get( "r_swapInterval", "0", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'if ( r_swapInterval->modified ) {' in win_glimp
	assert 'qwglSwapIntervalEXT( r_swapInterval->integer );' in win_glimp

	assert 'r_gamma = ri.Cvar_Get( "r_gamma", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'r_gamma = ri.Cvar_Get( "r_gamma", "1.2", CVAR_ARCHIVE | CVAR_CLOUD );' not in tr_init
	assert 'ri.Cvar_Set( "r_gamma", "0.5" );' in tr_image
	assert 'web_browserActive = ri.Cvar_Get( "web_browserActive", "0", CVAR_ROM );' in tr_init
	assert 'if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {' in tr_backend
	assert 'gammaRecip = 1.0f / r_gamma->value;' in tr_backend

	assert 'r_contrast = ri.Cvar_Get( "r_contrast", "1.0", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_contrast ) {' in tr_backend
	assert 'contrast = r_contrast->value;' in tr_backend

	assert 'r_railWidth = ri.Cvar_Get( "r_railWidth", "16", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'int\t\tspanWidth = r_railWidth->integer;' in tr_surface

	assert 'r_railCoreWidth = ri.Cvar_Get( "r_railCoreWidth", "6", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'DoRailCore( start, end, right, len, r_railCoreWidth->integer );' in tr_surface

	assert 'r_railSegmentLength = ri.Cvar_Get( "r_railSegmentLength", "32", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'numSegs = ( len ) / r_railSegmentLength->value;' in tr_surface


def test_engine_cvar_thirtyeighth_renderer_image_quality_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_local = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_local.h")
	tr_image = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c")
	tr_bsp = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_bsp.c")
	tr_shader = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shader.c")
	tr_scene = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_scene.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	win_glimp = _read_text(WIN_GLIMP)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'DAT_01740d98 = (*DAT_01740d40)("r_picmip",&DAT_0054ffe0,0x80821);' in retail_ghidra
	assert 'r_picmip = ri.Cvar_Get ("r_picmip", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_picmip, 0, 16, qtrue );' in tr_init
	assert 'scaled_width >>= r_picmip->integer;' in tr_image
	assert 'scaled_height >>= r_picmip->integer;' in tr_image

	assert 'DAT_01740f68 = (*DAT_01740d40)("r_roundImagesDown",&DAT_00551624,0x21);' in retail_ghidra
	assert 'r_roundImagesDown = ri.Cvar_Get ("r_roundImagesDown", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_roundImagesDown->integer && scaled_width > width )' in tr_image
	assert 'if ( r_roundImagesDown->integer && scaled_height > height )' in tr_image

	assert 'DAT_01740dbc = (*DAT_01740d40)("r_colorMipLevels",&DAT_0054ffe0,0x20);' in retail_ghidra
	assert 'r_colorMipLevels = ri.Cvar_Get ("r_colorMipLevels", "0", CVAR_LATCH );' in tr_init
	assert 'if ( r_colorMipLevels->integer ) {' in tr_image
	assert 'R_BlendOverTexture' in tr_image

	assert 'DAT_01743c1c = (*DAT_01740d40)("r_detailtextures",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_detailTextures = ri.Cvar_Get( "r_detailtextures", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( pStage->isDetail && !r_detailTextures->integer ) {' in tr_shader

	assert 'DAT_01740f98 = (*DAT_01740d40)("r_simpleMipMaps",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_simpleMipMaps = ri.Cvar_Get( "r_simpleMipMaps", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( !r_simpleMipMaps->integer ) {' in tr_image
	assert 'R_MipMap2( (unsigned *)in, width, height );' in tr_image

	assert 'DAT_01740ec4 = (*DAT_01740d40)("r_vertexLight",&DAT_0054ffe0,0x80821);' in retail_ghidra
	assert 'r_vertexLight = ri.Cvar_Get( "r_vertexLight", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'if ( r_vertexLight->integer || glConfig.hardwareType == GLHW_PERMEDIA2 ) {' in tr_bsp
	assert 'if ( pStage->bundle[0].vertexLightmap && ( (r_vertexLight->integer && !r_uiFullScreen->integer) || glConfig.hardwareType == GLHW_PERMEDIA2 ) && r_lightmap->integer )' in tr_shade
	assert 'r_vertexLight->integer == 1 ||' in tr_scene

	assert 'DAT_01740f00 = (*DAT_01740d40)("r_overBrightBits",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_overBrightBits = ri.Cvar_Get ("r_overBrightBits", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'tr.overbrightBits = r_overBrightBits->integer;' in tr_image
	assert 'overbright = 2.0f * r_overBrightBits->integer;' in tr_backend

	assert 'DAT_01740ebc = (*DAT_01740d40)("r_mapOverBrightBits",&DAT_0052f5d8,0x80021);' in retail_ghidra
	assert 'r_mapOverBrightBits = ri.Cvar_Get ("r_mapOverBrightBits", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'shift = r_mapOverBrightBits->integer - tr.overbrightBits;' in tr_bsp

	assert '("r_mapOverBrightCap",&DAT_0052f17c,&DAT_0054ffe0,&DAT_0052f17c,' in retail_ghidra
	assert 'r_mapOverBrightCap = ri.Cvar_GetBounded( "r_mapOverBrightCap", "255", "0", "255", CVAR_ARCHIVE | CVAR_LATCH | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert "extern\tcvar_t\t*r_mapOverBrightCap;" in tr_local
	assert 'cap = r_mapOverBrightCap ? r_mapOverBrightCap->integer : 255;' in tr_bsp
	assert 'r = r * cap / max;' in tr_bsp

	assert 'DAT_01740ddc = (*DAT_01740d40)("r_gamma",&DAT_00551624,0x80001);' in retail_ghidra
	assert 'r_gamma = ri.Cvar_Get( "r_gamma", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'r_gamma = ri.Cvar_Get( "r_gamma", "1.2", CVAR_ARCHIVE | CVAR_CLOUD );' not in tr_init
	assert 'ri.Cvar_Set( "r_gamma", "0.5" );' in tr_image
	assert 'if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {' in tr_backend


def test_engine_cvar_thirtyninth_renderer_misc_runtime_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_local = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_local.h")
	tr_shader = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shader.c")
	tr_scene = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_scene.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_curve = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_curve.c")
	tr_surface = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_surface.c")
	tr_font = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_font.c")
	tr_image = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	common = _read_text(COMMON)
	cl_main = _read_text(CL_MAIN)
	qcommon_cvar = _read_text(QCOMMON_CVAR)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	retail_hlil_part06 = _read_text(QL_STEAM_HLIL_PART06)

	assert 'DAT_01740e8c = (*DAT_01740d40)("r_uifullscreen",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'r_uiFullScreen = ri.Cvar_Get( "r_uifullscreen", "0", 0);' in tr_init
	assert 'r_uiFullScreen = ri.Cvar_Get( "r_uiFullScreen", "0", 0);' not in tr_init
	assert 'Cvar_Set("r_uiFullScreen", "1");' in common
	assert 'Cvar_Set("r_uiFullScreen", "1");' in cl_main
	assert 'Cvar_Set("r_uiFullScreen", "0");' in cl_main
	assert 'if (!Q_stricmp(var_name, var->name)) {' in qcommon_cvar
	assert 'if ( pStage->bundle[0].vertexLightmap && ( (r_vertexLight->integer && !r_uiFullScreen->integer) || glConfig.hardwareType == GLHW_PERMEDIA2 ) && r_lightmap->integer )' in tr_shade

	assert 'DAT_01740f9c = (*DAT_01740d40)("r_subdivisions",&DAT_0052ef24,0x40);' in retail_ghidra
	assert '0052ef24  data_52ef24:' in retail_hlil_part06
	assert 'r_subdivisions = ri.Cvar_Get ("r_subdivisions", "4", CVAR_ROM);' in tr_init
	assert 'if ( maxLen <= r_subdivisions->value ) {' in tr_curve

	assert 'DAT_01740f90 = (*DAT_01740d40)("r_smp",&DAT_0054ffe0,0x40);' in retail_ghidra
	assert 'r_smp = ri.Cvar_Get( "r_smp", "0", CVAR_ROM );' in tr_init
	assert 'if ( r_smp->integer ) {' in tr_scene
	assert 'if ( !r_smp->integer ) {' in tr_cmds
	assert 'if ( !r_smp->integer || data == backEndData[0]->commands.cmds ) {' in tr_backend
	assert 'if (r_smp->integer) {' in tr_shader

	assert 'DAT_01740ee4 = (*DAT_01740d40)("r_ignoreFastPath",&DAT_00551624,0x21);' in retail_ghidra
	assert 'r_ignoreFastPath = ri.Cvar_Get( "r_ignoreFastPath", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_ignoreFastPath->integer )' in tr_shader

	assert 'DAT_01740f4c = (*DAT_01740d40)("r_ignoreGLErrors",&DAT_00551624,1);' in retail_ghidra
	assert 'r_ignoreGLErrors = ri.Cvar_Get( "r_ignoreGLErrors", "1", CVAR_ARCHIVE );' in tr_init
	assert 'if ( !r_ignoreGLErrors->integer ) {' in tr_cmds

	assert '_DAT_01740e10 = (*DAT_01740d40)("r_ignore",&DAT_00551624,0x200);' in retail_ghidra
	assert 'r_ignore = ri.Cvar_Get( "r_ignore", "1", CVAR_CHEAT );' in tr_init
	assert 'VectorMA( origin, r_ignore->value, dir, origin );' in tr_surface
	assert 'left[0] = r_ignore->value;' in tr_surface
	assert 'up[1] = r_ignore->value;' in tr_surface

	assert 'DAT_01740dac = (*DAT_01740d40)("r_intensity",&DAT_00551624,0x21);' in retail_ghidra
	assert 'r_intensity = ri.Cvar_Get ("r_intensity", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_intensity->value <= 1 ) {' in tr_image
	assert 'ri.Cvar_Set( "r_intensity", "1" );' in tr_image
	assert 'j = i * r_intensity->value;' in tr_image

	assert '_DAT_01740f10 = (*DAT_01740d40)("r_saveFontData",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'r_saveFontData = ri.Cvar_Get( "r_saveFontData", "0", 0 );' in tr_init
	assert 'if ( r_saveFontData->integer ) {' in tr_font
	assert 'WriteTGA( pageName, imageBuff, R_FONT_ATLAS_SIZE, R_FONT_ATLAS_SIZE );' in tr_font
	assert 'ri.FS_WriteFile( cacheName, font, sizeof( fontInfo_t ) );' in tr_font

	assert 'uVar1 = FUN_004d9220(&DAT_0052d9b4,600,0);' in retail_ghidra
	assert 'DAT_01740f60 = (*DAT_01740d40)("r_maxPolys",uVar1);' in retail_ghidra
	assert 'r_maxpolys = ri.Cvar_Get( "r_maxPolys", va("%d", MAX_POLYS), 0);' in tr_init
	assert 'r_maxpolys = ri.Cvar_Get( "r_maxpolys", va("%d", MAX_POLYS), 0);' not in tr_init
	assert '#define\tMAX_POLYS\t\t600' in tr_local
	assert 'max_polys = r_maxpolys->integer;' in tr_init
	assert 'if (max_polys < MAX_POLYS)' in tr_init
	assert 'max_polys = MAX_POLYS;' in tr_init

	assert 'uVar1 = FUN_004d9220(&DAT_0052d9b4,3000,0);' in retail_ghidra
	assert 'DAT_01740eec = (*DAT_01740d40)("r_maxPolyVerts",uVar1);' in retail_ghidra
	assert 'r_maxpolyverts = ri.Cvar_Get( "r_maxPolyVerts", va("%d", MAX_POLYVERTS), 0);' in tr_init
	assert 'r_maxpolyverts = ri.Cvar_Get( "r_maxpolyverts", va("%d", MAX_POLYVERTS), 0);' not in tr_init
	assert '#define\tMAX_POLYVERTS\t3000' in tr_local
	assert 'max_polyverts = r_maxpolyverts->integer;' in tr_init
	assert 'if (max_polyverts < MAX_POLYVERTS)' in tr_init
	assert 'max_polyverts = MAX_POLYVERTS;' in tr_init


def test_engine_cvar_fortieth_renderer_status_sky_batch_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_local = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_local.h")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_sky = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_sky.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	win_glimp = _read_text(WIN_GLIMP)
	cl_main = _read_text(CL_MAIN)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	retail_hlil = _read_text(QL_STEAM_HLIL_PART02)

	assert 'DAT_01740eb4 = (*DAT_01740d40)("r_fastSkyColor","0x000000",0x80801);' in retail_ghidra
	assert 'r_fastSkyColor = ri.Cvar_Get( "r_fastSkyColor", "0x000000", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'extern cvar_t\t*r_fastSkyColor;' in tr_local
	assert 'static void RB_GetFastSkyClearColor( vec3_t color ) {' in tr_backend
	assert 'rgb = strtoul( string, &end, 0 );' in tr_backend
	assert 'qglClearColor( fastSkyColor[0], fastSkyColor[1], fastSkyColor[2], 1.0f );' in tr_backend

	assert 'DAT_01740ee8 = (*DAT_01740d40)("r_forceMergeEntities",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_forceMergeEntities = ri.Cvar_Get( "r_forceMergeEntities", "0", CVAR_CHEAT );' in tr_init
	assert 'extern\tcvar_t\t*r_forceMergeEntities;' in tr_local
	assert '|| ( entityNum != oldEntityNum && !r_forceMergeEntities->integer && !shader->entityMergable ) ) {' in tr_backend

	assert '_DAT_01740efc = (*DAT_01740d40)("r_gl_vendor",&DAT_0052f284,0x840);' in retail_ghidra
	assert 'r_glVendor = ri.Cvar_Get( "r_gl_vendor", "None", CVAR_ROM | CVAR_PROTECTED );' in tr_init
	assert 'ri.Cvar_Set( "r_gl_vendor", glConfig.vendor_string );' in win_glimp

	assert '_DAT_01743c04 = (*DAT_01740d40)("r_gl_renderer",&DAT_0052f284,0x840);' in retail_ghidra
	assert 'r_glRenderer = ri.Cvar_Get( "r_gl_renderer", "None", CVAR_ROM | CVAR_PROTECTED );' in tr_init
	assert 'ri.Cvar_Set( "r_gl_renderer", glConfig.renderer_string );' in win_glimp

	assert '_DAT_01740e08 = (*DAT_01740d40)("r_gl_reserved",&DAT_0054ffe0,0x840);' in retail_ghidra
	assert 'r_glReserved = ri.Cvar_Get( "r_gl_reserved", "0", CVAR_ROM | CVAR_PROTECTED );' in tr_init
	assert '(*DAT_01740d48)("r_gl_reserved",&DAT_00551624);' in retail_ghidra
	assert 'ri.Cvar_Set( "r_gl_reserved", "1" );' in win_glimp
	assert 'if ( qglGenQueriesARB && qglDeleteQueriesARB && qglIsQueryARB &&' in win_glimp

	assert 'DAT_01740e74 = (*DAT_01740d40)("r_stereo",&DAT_0054ffe0,0x21);' in retail_ghidra
	assert 'r_stereo = ri.Cvar_Get( "r_stereo", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'GLW_CreatePFD( &pfd, colorbits, depthbits, stencilbits, r_stereo->integer );' in win_glimp
	assert 'if ( !( pfd.dwFlags & PFD_STEREO ) && ( r_stereo->integer != 0 ) )' in win_glimp

	assert 'DAT_01740e20 = (*DAT_01740d40)("r_drawSkyFloor",&DAT_00551624,0x80001);' in retail_ghidra
	assert 'if (*(data_1740e20 + 0x30) != 0 || j != 5)' in retail_hlil
	assert 'r_drawSkyFloor = ri.Cvar_Get( "r_drawSkyFloor", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_drawSkyFloor, 0, 1, qtrue );' in tr_init
	assert 'if ( i == 5 && ( !r_drawSkyFloor || !r_drawSkyFloor->integer ) )' in tr_sky

	assert '_DAT_01740e18 = (*DAT_01740d40)("r_noFastRestart",&DAT_0054ffe0,1);' in retail_ghidra
	assert 'r_noFastRestart = ri.Cvar_Get( "r_noFastRestart", "0", CVAR_ARCHIVE );' in tr_init
	assert 'AssertCvarRange( r_noFastRestart, 0, 1, qtrue );' in tr_init
	assert 'if ( !Cvar_VariableIntegerValue( "r_noFastRestart" ) && Cmd_Argc() > 1 && !Q_stricmp( Cmd_Argv( 1 ), "fast" ) ) {' in cl_main

	assert 'DAT_01740ea4 = (*DAT_01740d40)("r_skipSmallBatches",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_skipSmallBatches = ri.Cvar_Get( "r_skipSmallBatches", "0", CVAR_CHEAT );' in tr_init
	assert 'AssertCvarRange( r_skipSmallBatches, 0, 1, qtrue );' in tr_init
	assert 'if ( r_skipSmallBatches && r_skipSmallBatches->integer && numIndexes > 0 && numIndexes <= SMALL_BATCH_INDEX_THRESHOLD ) {' in tr_shade

	assert 'DAT_01740f84 = (*DAT_01740d40)("r_teleporterFlash",&DAT_00551624,0x80801);' in retail_ghidra
	assert 'r_teleporterFlash = ri.Cvar_Get( "r_teleporterFlash", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_teleporterFlash, 0, 1, qtrue );' in tr_init
	assert 'if ( !r_teleporterFlash || !r_teleporterFlash->integer ) {' in tr_backend
	assert 'ri.Printf( PRINT_DEVELOPER, "QA: r_teleporterFlash overlay active\\n" );' in tr_backend


def test_engine_cvar_fortyfirst_renderer_platform_scene_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	tr_main = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_main.c")
	tr_surface = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_surface.c")
	win_glimp = _read_text(WIN_GLIMP)
	cl_main = _read_text(CL_MAIN)
	cl_cin = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cin.c")
	ui_main = _read_text(UI_MAIN)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	retail_hlil = _read_text(QL_STEAM_HLIL_PART02)

	assert '0046c2ff  data_1740d40("r_lastValidRenderer", "(uninitialized)", 1)' in retail_hlil
	assert 'cvar_t *lastValidRenderer = ri.Cvar_Get( "r_lastValidRenderer", "(uninitialized)", CVAR_ARCHIVE );' in win_glimp
	assert 'if ( Q_stricmp( lastValidRenderer->string, glConfig.renderer_string ) )' in win_glimp
	assert 'ri.Cvar_Set( "r_lastValidRenderer", glConfig.renderer_string );' in win_glimp

	assert '0046c396  data_16e40ec = data_1740d40("r_allowSoftwareGL", &data_54ffe0, 0x20)' in retail_hlil
	assert 'r_allowSoftwareGL = ri.Cvar_Get( "r_allowSoftwareGL", "0", CVAR_LATCH );' in win_glimp
	assert 'if ( !r_allowSoftwareGL->integer )' in win_glimp
	assert 'ri.Printf( PRINT_ALL, "...using software emulation\\n" );' in win_glimp

	assert '_DAT_01740f54 = (*DAT_01740d40)("r_inGameVideo",&DAT_00551624,1);' in retail_ghidra
	assert 'DAT_01647eec = FUN_004ce0d0("r_inGameVideo",&DAT_00551624,1);' in retail_ghidra
	assert 'r_inGameVideo = ri.Cvar_Get( "r_inGameVideo", "1", CVAR_ARCHIVE );' in tr_init
	assert 'cl_inGameVideo = Cvar_Get ("r_inGameVideo", "1", CVAR_ARCHIVE);' in cl_main
	assert 'cinTable[currentHandle].playonwalls = cl_inGameVideo->integer;' in cl_cin
	assert 'if (cl_inGameVideo->integer == 0 && cinTable[handle].playonwalls == 1) {' in cl_cin
	assert 'trap_Cvar_SetValue( "r_inGameVideo", 1 );' in ui_main
	assert 'trap_Cvar_SetValue( "r_inGameVideo", 0 );' in ui_main

	assert 'DAT_01740e40 = (*DAT_01740d40)("r_contrast",&DAT_00551620,0x80001);' in retail_ghidra
	assert 'r_contrast = ri.Cvar_Get( "r_contrast", "1.0", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert '( r_contrast && r_contrast->modified )' in tr_cmds
	assert 'RBPP_SetColorCorrectUniformsFromCvars();' in tr_cmds
	assert 'contrast = r_contrast->value;' in tr_backend

	assert 'DAT_01740edc = (*DAT_01740d40)("r_railWidth",&DAT_0052f040,0x80001);' in retail_ghidra
	assert 'r_railWidth = ri.Cvar_Get( "r_railWidth", "16", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'int\t\tspanWidth = r_railWidth->integer;' in tr_surface

	assert 'DAT_01740e60 = (*DAT_01740d40)("r_railCoreWidth",&DAT_0052f068,0x80001);' in retail_ghidra
	assert 'r_railCoreWidth = ri.Cvar_Get( "r_railCoreWidth", "6", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'DoRailCore( start, end, right, len, r_railCoreWidth->integer );' in tr_surface

	assert 'DAT_01740e4c = (*DAT_01740d40)("r_railSegmentLength",&DAT_0052f574,0x80001);' in retail_ghidra
	assert 'r_railSegmentLength = ri.Cvar_Get( "r_railSegmentLength", "32", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'numSegs = ( len ) / r_railSegmentLength->value;' in tr_surface
	assert 'VectorScale( vec, r_railSegmentLength->value, vec );' in tr_surface

	assert 'DAT_01740de0 = (*DAT_01740d40)("r_portalOnly",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_portalOnly = ri.Cvar_Get ("r_portalOnly", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_portalOnly->integer ) {' in tr_main

	assert 'DAT_01740f6c = (*DAT_01740d40)("r_speeds",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_speeds = ri.Cvar_Get ("r_speeds", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( !r_speeds->integer ) {' in tr_cmds
	assert 'else if ( r_speeds->integer == 6 )' in tr_cmds
	assert 'if ( r_speeds->integer ) {' in tr_backend

	assert 'DAT_01740de4 = (*DAT_01740d40)("r_textureMode","GL_LINEAR_MIPMAP_LINEAR",0x80001);' in retail_ghidra
	assert 'r_textureMode = ri.Cvar_Get( "r_textureMode", "GL_LINEAR_MIPMAP_LINEAR", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'GL_TextureMode( r_textureMode->string );' in tr_cmds
	assert 'ri.Cvar_Set( "r_textureMode", "GL_LINEAR_MIPMAP_NEAREST" );' in win_glimp
	assert 'ri.Cvar_Set( "r_textureMode", "GL_LINEAR_MIPMAP_LINEAR" );' in win_glimp
	assert 'ri.Cvar_Set( "r_texturemode", "GL_LINEAR_MIPMAP_LINEAR" );' not in win_glimp


def test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	retail_hlil_part01 = _read_text(QL_STEAM_HLIL_PART01)
	retail_hlil_part02 = _read_text(QL_STEAM_HLIL_PART02)

	assert 'DAT_01740ed4 = (*DAT_01740d40)("r_enablePostProcess",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_enablePostProcess = ri.Cvar_Get( "r_enablePostProcess", "0", CVAR_ROM );' in tr_init
	assert 'r_enablePostProcess = ri.Cvar_Get( "r_enablePostProcess", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' not in tr_init
	assert 'ri.Cvar_Set( "r_enablePostProcess", "0" );' in tr_init
	assert 'AssertCvarRange( r_enablePostProcess, 0, 1, qtrue );' in tr_init
	assert 'triggerReset = (qboolean)(r_enablePostProcess && r_enablePostProcess->modified);' in tr_init
	assert 'wantPostProcess = (qboolean)(r_enablePostProcess && r_enablePostProcess->integer);' in tr_backend
	assert 'if ( !wantPostProcess ) {' in tr_backend

	assert 'DAT_01740e38 = (*DAT_01740d40)("r_enableBloom",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_enableBloom = ri.Cvar_Get( "r_enableBloom", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_enableBloom, 0, 2, qtrue );' in tr_init
	assert 'triggerReset = (qboolean)(triggerReset || (r_enableBloom && r_enableBloom->modified));' in tr_init
	assert 'static int RBPP_GetBloomMode( void ) {' in tr_backend
	assert 'if ( r_enableBloom->integer == 1 ) {' in tr_backend
	assert 'if ( bloomMode == 2 &&' in tr_backend

	assert 'DAT_01740f04 = (*DAT_01740d40)("r_enableColorCorrect",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_enableColorCorrect = ri.Cvar_Get( "r_enableColorCorrect", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_enableColorCorrect, 0, 1, qtrue );' in tr_init
	assert 'colorCorrectEnabled = (qboolean)(r_enablePostProcess && r_enablePostProcess->integer &&' in tr_init
	assert 'wantColorCorrect = (qboolean)(wantPostProcess && r_enableColorCorrect && r_enableColorCorrect->integer);' in tr_backend
	assert 'backEnd.colorCorrectActive = RBPP_InitColorCorrectResources();' in tr_backend

	assert 'DAT_01740e58 = (*DAT_01740d40)("r_postProcessActive",&DAT_0054ffe0,0x140);' in retail_ghidra
	assert 'r_postProcessActive = ri.Cvar_Get( "r_postProcessActive", "0", CVAR_TEMP | CVAR_ROM );' in tr_init
	assert 'data_1740d48("r_postProcessActive", sub_4d9220(&data_52d9b4))' in retail_hlil_part02
	assert 'ri.Cvar_Set( "r_postProcessActive", backEnd.postProcessActive ? "1" : "0" );' in tr_backend
	assert 'return backEnd.postProcessActive;' in tr_backend

	assert 'DAT_01740eb8 = (*DAT_01740d40)("r_bloomActive",&DAT_0054ffe0,0x80140);' in retail_ghidra
	assert 'r_bloomActive = ri.Cvar_Get( "r_bloomActive", "0", CVAR_TEMP | CVAR_ROM | CVAR_CLOUD );' in tr_init
	assert 'data_1740d48("r_bloomActive", &data_54ffe0)' in retail_hlil_part01
	assert 'data_1740d48("r_bloomActive", &data_551624, var_8_5)' in retail_hlil_part01
	assert 'ri.Cvar_Set( "r_bloomActive", backEnd.bloomActive ? "1" : "0" );' in tr_backend
	assert 'if ( !cmd || !backEnd.bloomActive || !s_postProcess.sceneTarget.initialized ||' in tr_backend

	assert 'DAT_01740d90 = (*DAT_01740d40)("r_colorCorrectActive",&DAT_0054ffe0,0x140);' in retail_ghidra
	assert 'r_colorCorrectActive = ri.Cvar_Get( "r_colorCorrectActive", "0", CVAR_TEMP | CVAR_ROM );' in tr_init
	assert 'data_1740d48("r_colorCorrectActive", sub_4d9220(&data_52d9b4))' in retail_hlil_part02
	assert 'ri.Cvar_Set( "r_colorCorrectActive", backEnd.colorCorrectActive ? "1" : "0" );' in tr_backend
	assert 'if ( !cmd || !backEnd.colorCorrectActive || !cmd->colorCorrectTexture || !cmd->colorCorrectProgram ) {' in tr_backend

	assert '_DAT_01740f78 = (*DAT_01740d44)("r_bloomPasses",&DAT_00551624,&DAT_00551624,&DAT_0052f5d8,0x82821)' in retail_ghidra
	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' in tr_init
	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' not in tr_init
	assert 'AssertCvarRange( r_bloomPasses, 1, 2, qtrue );' in tr_init
	assert 'r_bloomPasses' not in tr_backend

	assert 'DAT_01743c10 = (*DAT_01740d44)("r_bloomIntensity",&DAT_0052e590,&DAT_0052f660,&DAT_0052f5f0,' in retail_ghidra
	assert 'r_bloomIntensity = ri.Cvar_GetBounded( "r_bloomIntensity", "0.5", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomIntensity, 0.0f, 10.0f, qfalse );' in tr_init
	assert '( r_bloomIntensity && r_bloomIntensity->modified ) ||' in tr_cmds
	assert 'bloomIntensity = r_bloomIntensity ? r_bloomIntensity->value : 0.5f;' in tr_backend
	assert 's_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.bloomIntensityUniform, bloomIntensity );' in tr_backend

	assert 'DAT_01740e84 = (*DAT_01740d44)("r_bloomBrightThreshold",&DAT_0052f610,&DAT_0052f660,&DAT_00551620,' in retail_ghidra
	assert 'r_bloomBrightThreshold = ri.Cvar_GetBounded( "r_bloomBrightThreshold", "0.25", "0.0", "1.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomBrightThreshold, 0.0f, 1.0f, qfalse );' in tr_init
	assert '( r_bloomBrightThreshold && r_bloomBrightThreshold->modified ) ||' in tr_cmds
	assert 'brightThreshold = r_bloomBrightThreshold ? r_bloomBrightThreshold->value : 0.25f;' in tr_backend
	assert 's_postProcess.procs.qglUniform1fARBFunc( s_postProcess.brightPassProgram.brightThresholdUniform, brightThreshold );' in tr_backend

	assert '_DAT_01740dc8 =' in retail_ghidra
	assert '(*DAT_01740d44)("r_bloomBlurScale",&DAT_0052f660,&DAT_00551620,&DAT_0052f62c,0x81801);' in retail_ghidra
	assert 'r_bloomBlurScale = ri.Cvar_GetBounded( "r_bloomBlurScale", "0.0", "1.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomBlurScale, 1.0f, 2.0f, qfalse );' in tr_init
	assert 'r_bloomBlurScale' not in tr_backend
	assert '"p_blurScale"' not in tr_backend


def test_engine_cvar_fortythird_renderer_backend_drawstate_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_bsp = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_bsp.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	win_glimp = _read_text(WIN_GLIMP)
	win_qgl = _read_text(REPO_ROOT / "src" / "code" / "win32" / "win_qgl.c")
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	retail_hlil_part02 = _read_text(QL_STEAM_HLIL_PART02)

	assert 'DAT_01740e98 = (*DAT_01740d40)("r_clear",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_clear = ri.Cvar_Get ("r_clear", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_clear->integer ) {' in tr_backend
	assert 'qglClearColor( 1, 0, 0.5, 1 );' in tr_backend
	assert 'qglClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );' in tr_backend

	assert 'DAT_01740e94 = (*DAT_01740d40)("r_drawBuffer","GL_BACK",0x200);' in retail_ghidra
	assert 'r_drawBuffer = ri.Cvar_Get( "r_drawBuffer", "GL_BACK", CVAR_CHEAT );' in tr_init
	assert 'if ( !Q_stricmp( r_drawBuffer->string, "GL_FRONT" ) ) {' in tr_cmds
	assert 'cmd->buffer = (int)GL_FRONT;' in tr_cmds
	assert 'cmd->buffer = (int)GL_BACK;' in tr_cmds
	assert 'if ( Q_stricmp( r_drawBuffer->string, "GL_FRONT" ) != 0 )' in win_glimp

	assert 'DAT_01740f80 = (*DAT_01740d40)("r_logFile",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_logFile = ri.Cvar_Get( "r_logFile", "0", CVAR_CHEAT );' in tr_init
	assert 'result = data_1740d48("r_logFile", sub_4d9220(&data_52d9b4))' in retail_hlil_part02
	assert 'QGL_EnableLogging( r_logFile->integer );' in win_glimp
	assert 'QGL_EnableLogging( r_logFile->integer );' in win_qgl
	assert 'ri.Cvar_Set( "r_logFile", va("%d", r_logFile->integer - 1 ) );' in win_qgl
	assert 'if ( r_logFile->integer )' in tr_shade

	assert 'DAT_01740da8 = (*DAT_01740d40)("r_lightmap",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'r_lightmap = ri.Cvar_Get ("r_lightmap", "0", 0 );' in tr_init
	assert 'if ( r_lightmap->integer == 2 )' in tr_bsp
	assert 'if ( r_lightmap->integer ) {' in tr_shade
	assert 'if ( r_lightmap->integer && ( pStage->bundle[0].isLightmap || pStage->bundle[1].isLightmap || pStage->bundle[0].vertexLightmap ) )' in tr_shade

	assert 'DAT_01740dd0 = (*DAT_01740d40)("r_measureOverdraw",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_measureOverdraw = ri.Cvar_Get( "r_measureOverdraw", "0", CVAR_CHEAT );' in tr_init
	assert 'data_1740d48("r_measureOverdraw", &data_54ffe0)' in retail_hlil_part02
	assert 'if ( r_measureOverdraw->integer )' in tr_cmds
	assert 'ri.Cvar_Set( "r_measureOverdraw", "0" );' in tr_cmds
	assert 'qglEnable( GL_STENCIL_TEST );' in tr_cmds
	assert 'if ( r_measureOverdraw->integer || r_shadows->integer == 2 )' in tr_backend
	assert 'qglReadPixels( 0, 0, glConfig.vidWidth, glConfig.vidHeight, GL_STENCIL_INDEX, GL_UNSIGNED_BYTE, stencilReadback );' in tr_backend

	assert 'DAT_01740e50 = (*DAT_01740d40)("r_offsetfactor",&DAT_0052f0f4,0x200);' in retail_ghidra
	assert 'r_offsetFactor = ri.Cvar_Get( "r_offsetfactor", "-1", CVAR_CHEAT );' in tr_init
	assert 'qglPolygonOffset( r_offsetFactor->value, r_offsetUnits->value );' in tr_shade

	assert 'DAT_01740ed0 = (*DAT_01740d40)("r_offsetunits",&DAT_0052f1dc,0x200);' in retail_ghidra
	assert 'r_offsetUnits = ri.Cvar_Get( "r_offsetunits", "-2", CVAR_CHEAT );' in tr_init
	assert 'if ( input->shader->polygonOffset )' in tr_shade

	assert 'DAT_01740f58 = (*DAT_01740d40)("r_primitives",&DAT_0054ffe0,1);' in retail_ghidra
	assert 'r_primitives = ri.Cvar_Get( "r_primitives", "0", CVAR_ARCHIVE );' in tr_init
	assert 'primitives = r_primitives->integer;' in tr_init
	assert 'primitives = r_primitives->integer;' in tr_shade
	assert 'if ( primitives == 0 ) {' in tr_shade

	assert 'DAT_01740f74 = (*DAT_01740d40)("r_swapInterval",&DAT_0054ffe0,0x80001);' in retail_ghidra
	assert 'r_swapInterval = ri.Cvar_Get( "r_swapInterval", "0", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'r_swapInterval->modified = qtrue;\t// force a set next frame' in win_glimp
	assert 'if ( r_swapInterval->modified ) {' in win_glimp
	assert 'qwglSwapIntervalEXT( r_swapInterval->integer );' in win_glimp

	assert 'DAT_01740d94 = (*DAT_01740d40)("r_verbose",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_verbose = ri.Cvar_Get( "r_verbose", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_verbose->integer )' in win_glimp
	assert 'ri.Printf( PRINT_ALL, "...PFD %d rejected, software acceleration\\n", i );' in win_glimp
	assert 'ri.Printf( PRINT_ALL, "...PFD %d rejected, not RGBA\\n", i );' in win_glimp
	assert 'ri.Printf( PRINT_ALL, "...PFD %d rejected, improper flags (%x instead of %x)\\n", i, pfds[i].dwFlags, pPFD->dwFlags );' in win_glimp


def test_engine_cvar_twentyfourth_renderer_lighting_quality_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_world = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_world.c")
	tr_flares = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_flares.c")
	tr_bsp = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_bsp.c")
	tr_image = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_sky = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_sky.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	cl_main = _read_text(CL_MAIN)
	cl_cin = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cin.c")
	ui_main = _read_text(REPO_ROOT / "src" / "code" / "ui" / "ui_main.c")
	win_glimp = _read_text(WIN_GLIMP)

	assert 'r_roundImagesDown = ri.Cvar_Get ("r_roundImagesDown", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_roundImagesDown->integer && scaled_width > width )' in tr_image
	assert 'if ( r_roundImagesDown->integer && scaled_height > height )' in tr_image

	assert 'r_overBrightBits = ri.Cvar_Get ("r_overBrightBits", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'tr.overbrightBits = r_overBrightBits->integer;' in tr_image
	assert 'if ( !RBPP_ColorCorrectEnabled() && !glConfig.deviceSupportsGamma ) {' in tr_image
	assert 'if ( !RBPP_ColorCorrectEnabled() && glConfig.deviceSupportsGamma )' in tr_image
	assert 'overbright = 2.0f * r_overBrightBits->integer;' in tr_backend
	assert 'if ( overbright <= 1.0f ) {' in tr_backend

	assert 'r_mapOverBrightBits = ri.Cvar_Get ("r_mapOverBrightBits", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'shift = r_mapOverBrightBits->integer - tr.overbrightBits;' in tr_bsp

	assert 'r_intensity = ri.Cvar_Get ("r_intensity", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_intensity->value <= 1 ) {' in tr_image
	assert 'ri.Cvar_Set( "r_intensity", "1" );' in tr_image
	assert 'j = i * r_intensity->value;' in tr_image

	assert 'r_flares = ri.Cvar_Get ("r_flares", "0", CVAR_ARCHIVE );' in tr_init
	assert 'if ( !r_flares->integer ) {' in tr_flares

	assert 'r_ignoreGLErrors = ri.Cvar_Get( "r_ignoreGLErrors", "1", CVAR_ARCHIVE );' in tr_init
	assert 'if ( !r_ignoreGLErrors->integer ) {' in tr_cmds
	assert 'ri.Error( ERR_FATAL, "RE_BeginFrame() - glGetError() failed (0x%x)!\\n", err );' in tr_cmds

	assert 'r_inGameVideo = ri.Cvar_Get( "r_inGameVideo", "1", CVAR_ARCHIVE );' in tr_init
	assert 'cl_inGameVideo = Cvar_Get ("r_inGameVideo", "1", CVAR_ARCHIVE);' in cl_main
	assert 'cinTable[currentHandle].playonwalls = cl_inGameVideo->integer;' in cl_cin
	assert 'if (cl_inGameVideo->integer == 0 && cinTable[handle].playonwalls == 1) {' in cl_cin
	assert 'trap_Cvar_SetValue( "r_inGameVideo", 1 );' in ui_main
	assert 'trap_Cvar_SetValue( "r_inGameVideo", 0 );' in ui_main

	assert 'r_drawSun = ri.Cvar_Get( "r_drawSun", "0", CVAR_ARCHIVE );' in tr_init
	assert 'if ( !r_drawSun->integer ) {' in tr_sky

	assert 'r_finish = ri.Cvar_Get ("r_finish", "0", CVAR_ARCHIVE);' in tr_init
	assert 'if ( r_finish->integer == 1 && !glState.finishCalled ) {' in tr_backend
	assert 'if ( r_finish->integer == 0 ) {' in tr_backend
	assert 'ri.Cvar_Set( "r_finish", "0" );' in win_glimp

	assert 'r_facePlaneCull = ri.Cvar_Get ("r_facePlaneCull", "1", CVAR_ARCHIVE );' in tr_init
	assert 'if ( !r_facePlaneCull->integer ) {' in tr_world


def test_engine_cvar_twentyfifth_renderer_debug_execution_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_bsp = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_bsp.c")
	tr_curve = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_curve.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	tr_shader = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shader.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")

	assert 'r_fullbright = ri.Cvar_Get ("r_fullbright", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'if ( r_fullbright->integer ) {' in tr_bsp
	assert 'lightmapNum = LIGHTMAP_WHITEIMAGE;' in tr_bsp

	assert 'r_subdivisions = ri.Cvar_Get ("r_subdivisions", "4", CVAR_ROM);' in tr_init
	assert 'if ( maxLen <= r_subdivisions->value ) {' in tr_curve

	assert 'r_primitives = ri.Cvar_Get( "r_primitives", "0", CVAR_ARCHIVE );' in tr_init
	assert 'primitives = r_primitives->integer;' in tr_init
	assert 'primitives = r_primitives->integer;' in tr_shade

	assert 'r_printShaders = ri.Cvar_Get( "r_printShaders", "0", 0 );' in tr_init
	assert 'if ( r_printShaders->integer ) {' in tr_shader
	assert 'ri.Printf( PRINT_ALL, "*SHADER* %s\\n", name );' in tr_shader

	assert 'r_showImages = ri.Cvar_Get( "r_showImages", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_showImages->integer == 2 ) {' in tr_backend
	assert 'if ( r_showImages->integer ) {' in tr_backend

	assert 'r_showSmp = ri.Cvar_Get ("r_showSmp", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_showSmp->integer ) {' in tr_cmds
	assert 'ri.Printf( PRINT_ALL, "R" );' in tr_cmds
	assert 'ri.Printf( PRINT_ALL, "." );' in tr_cmds

	assert 'r_skipBackEnd = ri.Cvar_Get ("r_skipBackEnd", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( !r_skipBackEnd->integer ) {' in tr_cmds

	assert 'r_skipLargeBatches = ri.Cvar_Get( "r_skipLargeBatches", "0", CVAR_CHEAT );' in tr_init
	assert 'AssertCvarRange( r_skipLargeBatches, 0, 1, qtrue );' in tr_init
	assert 'if ( r_skipLargeBatches && r_skipLargeBatches->integer && numIndexes >= LARGE_BATCH_INDEX_THRESHOLD ) {' in tr_shade

	assert 'r_skipSmallBatches = ri.Cvar_Get( "r_skipSmallBatches", "0", CVAR_CHEAT );' in tr_init
	assert 'AssertCvarRange( r_skipSmallBatches, 0, 1, qtrue );' in tr_init
	assert 'if ( r_skipSmallBatches && r_skipSmallBatches->integer && numIndexes > 0 && numIndexes <= SMALL_BATCH_INDEX_THRESHOLD ) {' in tr_shade

	assert 'r_measureOverdraw = ri.Cvar_Get( "r_measureOverdraw", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_measureOverdraw->integer )' in tr_cmds
	assert 'ri.Cvar_Set( "r_measureOverdraw", "0" );' in tr_cmds
	assert 'if ( r_measureOverdraw->integer || r_shadows->integer == 2 )' in tr_backend


def test_engine_cvar_thirtysixth_renderer_debug_overlay_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_bsp = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_bsp.c")
	tr_shader = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shader.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	tr_light = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_light.c")
	tr_world = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_world.c")
	tr_main = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_main.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'DAT_01740e80 = (*DAT_01740d40)("r_fullbright",&DAT_0054ffe0,0x80821);' in retail_ghidra
	assert 'r_fullbright = ri.Cvar_Get ("r_fullbright", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'if ( r_fullbright->integer ) {' in tr_bsp
	assert 'lightmapNum = LIGHTMAP_WHITEIMAGE;' in tr_bsp

	assert 'DAT_01740f14 = (*DAT_01740d40)("r_singleShader",&DAT_0054ffe0,0x220);' in retail_ghidra
	assert 'r_singleShader = ri.Cvar_Get ("r_singleShader", "0", CVAR_CHEAT | CVAR_LATCH );' in tr_init
	assert 'if ( r_singleShader->integer && !surf->shader->isSky ) {' in tr_bsp
	assert 'surf->shader = tr.defaultShader;' in tr_bsp

	assert 'DAT_01740dc4 = (*DAT_01740d40)("r_printShaders",&DAT_0054ffe0,0);' in retail_ghidra
	assert 'r_printShaders = ri.Cvar_Get( "r_printShaders", "0", 0 );' in tr_init
	assert 'if ( r_printShaders->integer ) {' in tr_shader
	assert 'ri.Printf( PRINT_ALL, "*SHADER* %s\\n", name );' in tr_shader

	assert 'DAT_01740d9c = (*DAT_01740d40)("r_showImages",&DAT_0054ffe0,0x100);' in retail_ghidra
	assert 'r_showImages = ri.Cvar_Get( "r_showImages", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_showImages->integer == 2 ) {' in tr_backend
	assert 'if ( r_showImages->integer ) {' in tr_backend

	assert 'DAT_01740f50 = (*DAT_01740d40)("r_showSmp",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_showSmp = ri.Cvar_Get ("r_showSmp", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_showSmp->integer ) {' in tr_cmds
	assert 'ri.Printf( PRINT_ALL, "R" );' in tr_cmds
	assert 'ri.Printf( PRINT_ALL, "." );' in tr_cmds

	assert 'DAT_01740ef4 = (*DAT_01740d40)("r_skipBackEnd",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_skipBackEnd = ri.Cvar_Get ("r_skipBackEnd", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( !r_skipBackEnd->integer ) {' in tr_cmds

	assert 'DAT_01740dfc = (*DAT_01740d40)("r_skipLargeBatches",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_skipLargeBatches = ri.Cvar_Get( "r_skipLargeBatches", "0", CVAR_CHEAT );' in tr_init
	assert 'AssertCvarRange( r_skipLargeBatches, 0, 1, qtrue );' in tr_init
	assert 'if ( r_skipLargeBatches && r_skipLargeBatches->integer && numIndexes >= LARGE_BATCH_INDEX_THRESHOLD ) {' in tr_shade

	assert 'DAT_01740e3c = (*DAT_01740d40)("r_debuglight",&DAT_0054ffe0,0x100);' in retail_ghidra
	assert 'r_debugLight = ri.Cvar_Get( "r_debuglight", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_debugLight->integer ) {' in tr_light
	assert 'LogLight( ent );' in tr_light

	assert 'DAT_01740d8c = (*DAT_01740d40)("r_debugFontAtlas",&DAT_0054ffe0,0x100);' in retail_ghidra
	assert 'r_debugFontAtlas = ri.Cvar_Get( "r_debugFontAtlas", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_debugFontAtlas->integer ) {' in tr_backend
	assert 'RB_ShowFontAtlas();' in tr_backend

	assert 'DAT_01740f7c = (*DAT_01740d40)("r_debugAds",&DAT_0054ffe0,0x100);' in retail_ghidra
	assert 'r_debugAds = ri.Cvar_Get( "r_debugAds", "0", CVAR_TEMP );' in tr_init
	assert 'r_debugAds = ri.Cvar_Get( "r_debugAds", "0", CVAR_CHEAT );' not in tr_init
	assert 'R_DebugAdvertisements();' in tr_main
	assert 'if ( !r_debugAds || !r_debugAds->integer || tr.viewParms.frameSceneNum != 1 ) {' in tr_world
	assert 'ri.AdvertisementBridge_GetCellLabel( advertisement->cellId, buffer, sizeof( buffer ) );' in tr_world


def test_engine_cvar_twentysixth_renderer_visibility_debug_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_world = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_world.c")
	tr_main = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_main.c")
	tr_sky = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_sky.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	tr_shader = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shader.c")
	win_glimp = _read_text(WIN_GLIMP)
	win_qgl = _read_text(REPO_ROOT / "src" / "code" / "win32" / "win_qgl.c")
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'DAT_01740e90 = (*DAT_01740d40)("r_noCull",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_nocull = ri.Cvar_Get ("r_noCull", "0", CVAR_CHEAT);' in tr_init
	assert 'r_nocull = ri.Cvar_Get ("r_nocull", "0", CVAR_CHEAT);' not in tr_init
	assert 'if ( r_nocull->integer ) {' in tr_world

	assert 'r_novis = ri.Cvar_Get ("r_noVis", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_novis->integer || tr.viewCluster == -1 ) {' in tr_world

	assert 'DAT_01740db4 = (*DAT_01740d40)("r_showCluster",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_showcluster = ri.Cvar_Get ("r_showCluster", "0", CVAR_CHEAT);' in tr_init
	assert 'r_showcluster = ri.Cvar_Get ("r_showcluster", "0", CVAR_CHEAT);' not in tr_init
	assert 'if ( r_showcluster->modified || r_showcluster->integer ) {' in tr_world
	assert 'ri.Printf( PRINT_ALL, "cluster:%i  area:%i\\n", cluster, leaf->area );' in tr_world

	assert 'r_speeds = ri.Cvar_Get ("r_speeds", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( !r_speeds->integer ) {' in tr_cmds
	assert 'if ( r_speeds->integer == 1 ) {' in tr_cmds
	assert 'else if ( r_speeds->integer == 6 )' in tr_cmds
	assert 'if ( r_speeds->integer ) {' in tr_backend
	assert 'ri.Printf( PRINT_ALL, "qglTexSubImage2D %i, %i: %i msec\\n", cols, rows, end - start );' in tr_backend

	assert 'r_verbose = ri.Cvar_Get( "r_verbose", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_verbose->integer )' in win_glimp
	assert 'ri.Printf( PRINT_ALL, "...PFD %d rejected, software acceleration\\n", i );' in win_glimp

	assert 'r_logFile = ri.Cvar_Get( "r_logFile", "0", CVAR_CHEAT );' in tr_init
	assert 'QGL_EnableLogging( r_logFile->integer );' in win_qgl
	assert 'ri.Cvar_Set( "r_logFile", va("%d", r_logFile->integer - 1 ) );' in win_qgl
	assert 'if ( r_logFile->integer ) {' in tr_shade
	assert 'GLimp_LogComment( va("--- RB_StageIteratorLightmappedMultitexture( %s ) ---\\n", tess.shader->name) );' in tr_shade

	assert 'DAT_01740e88 = (*DAT_01740d40)("r_showTris",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_showtris = ri.Cvar_Get ("r_showTris", "0", CVAR_CHEAT);' in tr_init
	assert 'r_showtris = ri.Cvar_Get ("r_showtris", "0", CVAR_CHEAT);' not in tr_init
	assert 'if ( r_showtris->integer || ( r_debugShaderIndex->integer' in tr_shade
	assert 'DrawTris (input);' in tr_shade

	assert 'DAT_01740f64 = (*DAT_01740d40)("r_showSky",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_showsky = ri.Cvar_Get ("r_showSky", "0", CVAR_CHEAT);' in tr_init
	assert 'r_showsky = ri.Cvar_Get ("r_showsky", "0", CVAR_CHEAT);' not in tr_init
	assert 'if ( r_showsky->integer ) {' in tr_sky
	assert 'qglDepthRange( 0.0, 0.0 );' in tr_sky

	assert 'DAT_01740dec = (*DAT_01740d40)("r_showNormals",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_shownormals = ri.Cvar_Get ("r_showNormals", "0", CVAR_CHEAT);' in tr_init
	assert 'r_shownormals = ri.Cvar_Get ("r_shownormals", "0", CVAR_CHEAT);' not in tr_init
	assert 'if ( r_shownormals->integer ) {' in tr_shade
	assert 'DrawNormals (input);' in tr_shade

	assert 'DAT_01743c0c = (*DAT_01740d40)("r_noPortals",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_noportals = ri.Cvar_Get ("r_noPortals", "0", CVAR_CHEAT);' in tr_init
	assert 'r_noportals = ri.Cvar_Get ("r_noportals", "0", CVAR_CHEAT);' not in tr_init
	assert 'if ( r_noportals->integer || (r_fastsky->integer == 1) ) {' in tr_main


def test_engine_cvar_twentyseventh_renderer_world_override_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_scene = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_scene.c")
	tr_world = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_world.c")
	tr_main = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_main.c")
	tr_bsp = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_bsp.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_cmds = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_cmds.c")
	win_glimp = _read_text(WIN_GLIMP)
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'r_norefresh = ri.Cvar_Get ("r_noRefresh", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_norefresh->integer ) {' in tr_scene

	assert 'r_drawentities = ri.Cvar_Get ("r_drawEntities", "1", CVAR_CHEAT );' in tr_init
	assert 'if ( !r_drawentities->integer ) {' in tr_main

	assert 'DAT_01740dcc = (*DAT_01740d40)("r_noCurves",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_nocurves = ri.Cvar_Get ("r_noCurves", "0", CVAR_CHEAT );' in tr_init
	assert 'r_nocurves = ri.Cvar_Get ("r_nocurves", "0", CVAR_CHEAT );' not in tr_init
	assert 'if ( r_nocurves->integer ) {' in tr_world
	assert 'return qtrue;' in tr_world

	assert 'r_drawworld = ri.Cvar_Get ("r_drawWorld", "1", CVAR_CHEAT );' in tr_init
	assert 'if ( !r_drawworld->integer ) {' in tr_world

	assert 'r_lightmap = ri.Cvar_Get ("r_lightmap", "0", 0 );' in tr_init
	assert 'if ( r_lightmap->integer == 2 )' in tr_bsp
	assert 'if ( r_lightmap->integer ) {' in tr_shade

	assert 'DAT_01740e6c = (*DAT_01740d40)("r_noBind",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_nobind = ri.Cvar_Get ("r_noBind", "0", CVAR_CHEAT);' in tr_init
	assert 'r_nobind = ri.Cvar_Get ("r_nobind", "0", CVAR_CHEAT);' not in tr_init
	assert 'if ( r_nobind->integer && tr.dlightImage ) {' in tr_backend

	assert 'r_clear = ri.Cvar_Get ("r_clear", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_clear->integer ) {' in tr_backend
	assert 'qglClearColor( 1, 0, 0.5, 1 );' in tr_backend
	assert 'qglClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );' in tr_backend

	assert 'r_drawBuffer = ri.Cvar_Get( "r_drawBuffer", "GL_BACK", CVAR_CHEAT );' in tr_init
	assert 'if ( !Q_stricmp( r_drawBuffer->string, "GL_FRONT" ) ) {' in tr_cmds
	assert 'cmd->buffer = (int)GL_FRONT;' in tr_cmds
	assert 'cmd->buffer = (int)GL_BACK;' in tr_cmds
	assert 'if ( Q_stricmp( r_drawBuffer->string, "GL_FRONT" ) != 0 )' in win_glimp

	assert 'r_lockpvs = ri.Cvar_Get ("r_lockPVS", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_lockpvs->integer ) {' in tr_world

	assert 'r_portalOnly = ri.Cvar_Get ("r_portalOnly", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_portalOnly->integer ) {' in tr_main


def test_engine_cvar_twentyeighth_renderer_diagnostics_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_light = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_light.c")
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	tr_main = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_main.c")
	tr_surface = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_surface.c")
	tr_font = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_font.c")
	cm_patch = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "cm_patch.c")
	linux_glimp = _read_text(REPO_ROOT / "src" / "code" / "unix" / "linux_glimp.c")
	macosx_glimp = _read_text(REPO_ROOT / "src" / "code" / "macosx" / "macosx_glimp.m")
	macosx_display = _read_text(REPO_ROOT / "src" / "code" / "macosx" / "macosx_display.m")
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)

	assert 'r_directedScale = ri.Cvar_Get( "r_directedScale", "1", CVAR_CHEAT );' in tr_init
	assert 'VectorScale( ent->directedLight, r_directedScale->value, ent->directedLight );' in tr_light

	assert 'r_debugLight = ri.Cvar_Get( "r_debuglight", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_debugLight->integer ) {' in tr_light
	assert 'LogLight( ent );' in tr_light

	assert 'r_debugFontAtlas = ri.Cvar_Get( "r_debugFontAtlas", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_debugFontAtlas->integer ) {' in tr_backend
	assert 'RB_ShowFontAtlas();' in tr_backend

	assert 'DAT_01740e48 = (*DAT_01740d40)("r_debugShaderIndex",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_debugShaderIndex = ri.Cvar_Get( "r_debugShaderIndex", "0", CVAR_CHEAT );' in tr_init
	assert 'r_debugShaderIndex->integer == tess.shader->index' in tr_shade

	assert 'DAT_01740f48 = (*DAT_01740d40)("r_debugSort",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_debugSort = ri.Cvar_Get( "r_debugSort", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_debugSort->integer && r_debugSort->integer < tess.shader->sort' in tr_shade

	assert 'DAT_01740ea0 = (*DAT_01740d40)("r_debugSortExcept",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_debugSortExcept = ri.Cvar_Get( "r_debugSortExcept", "0", CVAR_CHEAT );' in tr_init
	assert '&& (float)r_debugSortExcept->integer != tess.shader->sort ) {' in tr_shade

	assert 'r_customaspect = ri.Cvar_Get( "r_customaspect"' not in tr_init
	assert 'r_dlightBacks = ri.Cvar_Get( "r_dlightBacks"' not in tr_init
	assert 'r_previousglDriver' not in linux_glimp
	assert 'r_enablerender' not in macosx_glimp
	assert 'r_appleTransformHint' not in macosx_glimp
	assert 'r_minDisplayRefresh' not in macosx_display
	assert 'r_maxDisplayRefresh' not in macosx_display

	assert 'DAT_01743c00 = (*DAT_01740d40)("r_debugSurface",&DAT_0054ffe0,0x200);' in retail_ghidra
	assert 'r_debugSurface = ri.Cvar_Get ("r_debugSurface", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( !r_debugSurface->integer ) {' in tr_main
	assert 'ri.CM_DrawDebugSurface( R_DebugPolygon );' in tr_main

	assert 'r_ignore = ri.Cvar_Get( "r_ignore", "1", CVAR_CHEAT );' in tr_init
	assert 'VectorMA( origin, r_ignore->value, dir, origin );' in tr_surface
	assert 'left[0] = r_ignore->value;' in tr_surface
	assert 'up[1] = r_ignore->value;' in tr_surface

	assert 'r_saveFontData = ri.Cvar_Get( "r_saveFontData", "0", 0 );' in tr_init
	assert 'if ( r_saveFontData->integer ) {' in tr_font
	assert 'WriteTGA( pageName, imageBuff, R_FONT_ATLAS_SIZE, R_FONT_ATLAS_SIZE );' in tr_font
	assert 'ri.FS_WriteFile( cacheName, font, sizeof( fontInfo_t ) );' in tr_font

	assert 'r_offsetFactor = ri.Cvar_Get( "r_offsetfactor", "-1", CVAR_CHEAT );' in tr_init
	assert 'r_offsetUnits = ri.Cvar_Get( "r_offsetunits", "-2", CVAR_CHEAT );' in tr_init
	assert 'qglPolygonOffset( r_offsetFactor->value, r_offsetUnits->value );' in tr_shade

	assert 'cv = Cvar_Get( "r_debugSurfaceUpdate", "1", 0 );' in cm_patch
	assert 'if (cv->integer) {' in cm_patch
	assert 'if (cv && cv->integer) {' in cm_patch
	assert 'debugPatchCollide = pc;' in cm_patch
	assert 'debugFacet = facet;' in cm_patch


def test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_public = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_public.h")
	cl_main = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_main.c")
	win_glimp = _read_text(REPO_ROOT / "src" / "code" / "win32" / "win_glimp.c")

	assert 'cvar_t\t*(*Cvar_GetBounded)( const char *name, const char *value, const char *minValue, const char *maxValue, int flags );' in tr_public
	assert "ri.Cvar_GetBounded = Cvar_GetBounded;" in cl_main

	assert 'r_enablePostProcess = ri.Cvar_Get( "r_enablePostProcess", "0", CVAR_ROM );' in tr_init
	assert 'r_enablePostProcess = ri.Cvar_Get( "r_enablePostProcess", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' not in tr_init
	assert 'ri.Cvar_Set( "r_enablePostProcess", "0" );' in tr_init
	assert 'AssertCvarRange( r_enablePostProcess, 0, 1, qtrue );' in tr_init
	assert 'triggerReset = (qboolean)(r_enablePostProcess && r_enablePostProcess->modified);' in tr_init
	assert 'wantPostProcess = (qboolean)(r_enablePostProcess && r_enablePostProcess->integer);' in tr_backend

	assert 'r_enableBloom = ri.Cvar_Get( "r_enableBloom", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_enableBloom, 0, 2, qtrue );' in tr_init
	assert 'triggerReset = (qboolean)(triggerReset || (r_enableBloom && r_enableBloom->modified));' in tr_init
	assert 'wantBloom = (qboolean)(wantPostProcess && r_enableBloom && r_enableBloom->integer);' in tr_backend

	assert 'r_enableColorCorrect = ri.Cvar_Get( "r_enableColorCorrect", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_enableColorCorrect, 0, 1, qtrue );' in tr_init
	assert 'triggerReset = (qboolean)(triggerReset || (r_enableColorCorrect && r_enableColorCorrect->modified));' in tr_init
	assert 'wantColorCorrect = (qboolean)(wantPostProcess && r_enableColorCorrect && r_enableColorCorrect->integer);' in tr_backend

	assert 'r_postProcessActive = ri.Cvar_Get( "r_postProcessActive", "0", CVAR_TEMP | CVAR_ROM );' in tr_init
	assert 'ri.Cvar_Set( "r_postProcessActive", backEnd.postProcessActive ? "1" : "0" );' in tr_backend

	assert 'r_bloomActive = ri.Cvar_Get( "r_bloomActive", "0", CVAR_TEMP | CVAR_ROM | CVAR_CLOUD );' in tr_init
	assert 'ri.Cvar_Set( "r_bloomActive", backEnd.bloomActive ? "1" : "0" );' in tr_backend

	assert 'r_colorCorrectActive = ri.Cvar_Get( "r_colorCorrectActive", "0", CVAR_TEMP | CVAR_ROM );' in tr_init
	assert 'ri.Cvar_Set( "r_colorCorrectActive", backEnd.colorCorrectActive ? "1" : "0" );' in tr_backend
	assert 'r_floatingPointFBOs = ri.Cvar_Get( "r_floatingPointFBOs", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_floatingPointFBOs && r_floatingPointFBOs->integer ) {' in tr_backend

	assert 'r_ext_compressed_textures = ri.Cvar_Get( "r_ext_compressed_textures", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_compressed_textures->integer )' in win_glimp

	assert 'r_ext_gamma_control = ri.Cvar_Get( "r_ext_gamma_control", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( !r_ignorehwgamma->integer && r_ext_gamma_control->integer )' in win_glimp

	assert 'r_ext_multitexture = ri.Cvar_Get( "r_ext_multitexture", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_multitexture->integer )' in win_glimp

	assert 'r_ext_compiled_vertex_array = ri.Cvar_Get( "r_ext_compiled_vertex_array", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_compiled_vertex_array->integer )' in win_glimp


def test_engine_cvar_thirtyseventh_renderer_extension_startup_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	win_glimp = _read_text(WIN_GLIMP)
	win_input = _read_text(WIN_INPUT)
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	retail_ghidra = _read_text(QL_STEAM_GHIDRA_DECOMPILE)
	retail_hlil_part02 = _read_text(QL_STEAM_HLIL_PART02)

	assert 'DAT_01740e64 = (*DAT_01740d40)("r_glDriver","opengl32",0x21);' in retail_ghidra
	assert 'r_glDriver = ri.Cvar_Get( "r_glDriver", OPENGL_DRIVER_NAME, CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( !GLW_LoadOpenGL( r_glDriver->string ) )' in win_glimp
	assert 'if ( !Q_stricmp( r_glDriver->string, OPENGL_DRIVER_NAME ) )' in win_glimp
	assert 'else if ( !Q_stricmp( r_glDriver->string, _3DFX_DRIVER_NAME ) )' in win_glimp
	assert 'cls.keyCatchers & ~( KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS )' in win_input

	assert 'DAT_01740dd4 = (*DAT_01740d40)("r_allowExtensions",&DAT_00551624,0x21);' in retail_ghidra
	assert 'r_allowExtensions = ri.Cvar_Get( "r_allowExtensions", "1", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( !r_allowExtensions->integer )' in win_glimp

	assert 'DAT_01740ef0 = (*DAT_01740d40)("r_ext_compressed_textures",&DAT_0054ffe0,0x80021);' in retail_ghidra
	assert 'r_ext_compressed_textures = ri.Cvar_Get( "r_ext_compressed_textures", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_compressed_textures->integer )' in win_glimp
	assert 'glConfig.textureCompression = TC_S3TC;' in win_glimp

	assert 'DAT_01740f18 = (*DAT_01740d40)("r_ext_gamma_control",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_ext_gamma_control = ri.Cvar_Get( "r_ext_gamma_control", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( !r_ignorehwgamma->integer && r_ext_gamma_control->integer )' in win_glimp
	assert 'qwglGetDeviceGammaRamp3DFX = ( BOOL ( WINAPI * )( HDC, LPVOID ) ) qwglGetProcAddress( "wglGetDeviceGammaRamp3DFX" );' in win_glimp

	assert 'DAT_01740db0 = (*DAT_01740d40)("r_ext_multitexture",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_ext_multitexture = ri.Cvar_Get( "r_ext_multitexture", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_multitexture->integer )' in win_glimp
	assert 'qglActiveTextureARB = ( PFNGLACTIVETEXTUREARBPROC ) qwglGetProcAddress( "glActiveTextureARB" );' in win_glimp

	assert 'DAT_01743c18 = (*DAT_01740d40)("r_ext_compiled_vertex_array",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_ext_compiled_vertex_array = ri.Cvar_Get( "r_ext_compiled_vertex_array", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_compiled_vertex_array->integer )' in win_glimp
	assert 'qglLockArraysEXT = ( void ( APIENTRY * )( int, int ) ) qwglGetProcAddress( "glLockArraysEXT" );' in win_glimp

	assert 'DAT_01743c08 = (*DAT_01740d40)("r_ext_texture_env_add",&DAT_00551624,0x80021);' in retail_ghidra
	assert 'r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' not in tr_init
	assert 'if ( r_ext_texture_env_add->integer )' in win_glimp
	assert 'glConfig.textureEnvAddAvailable = qtrue;' in win_glimp

	assert 'DAT_01740f08 = (*DAT_01740d40)("r_ignoreHWGamma",&DAT_0054ffe0,0x21);' in retail_ghidra
	assert 'r_ignorehwgamma = ri.Cvar_Get( "r_ignoreHWGamma", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( !r_ignorehwgamma->integer && r_ext_gamma_control->integer )' in win_glimp

	assert 'DAT_01740f70 = (*DAT_01740d40)("r_floatingPointFBOs",&DAT_0054ffe0,0x21);' in retail_ghidra
	assert 'r_floatingPointFBOs = ri.Cvar_Get( "r_floatingPointFBOs", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( r_floatingPointFBOs && r_floatingPointFBOs->integer ) {' in tr_backend
	assert 'internalFormat = GL_RGBA16;' in tr_backend
	assert 'pixelType = GL_FLOAT;' in tr_backend

	assert 'data_16e40e4 = data_1740d40("r_maskMinidriver", &data_54ffe0, 0x20)' in retail_hlil_part02
	assert 'r_maskMinidriver = ri.Cvar_Get( "r_maskMinidriver", "0", CVAR_LATCH );' in win_glimp
	assert 'if ( strstr( buffer, "opengl32" ) != 0 || r_maskMinidriver->integer )' in win_glimp


def test_engine_cvar_thirtieth_renderer_lod_auxiliary_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_light = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_light.c")
	tr_mesh = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_mesh.c")
	tr_surface = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_surface.c")
	tr_flares = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_flares.c")
	tr_main = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_main.c")
	tr_shade = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_shade.c")
	common = _read_text(COMMON)
	cl_main = _read_text(CL_MAIN)
	win_glimp = _read_text(WIN_GLIMP)

	assert 'r_ambientScale = ri.Cvar_GetBounded( "r_ambientScale", "10", "1", "100", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_ambientScale, 1, 100, qtrue );' in tr_init
	assert 'VectorScale( ent->ambientLight, r_ambientScale->value, ent->ambientLight );' in tr_light

	assert 'r_lodCurveError = ri.Cvar_Get( "r_lodCurveError", "250", CVAR_CHEAT );' in tr_init
	assert 'if ( r_lodCurveError->value < 0 ) {' in tr_surface
	assert 'return r_lodCurveError->value / d;' in tr_surface

	assert 'r_lodbias = ri.Cvar_GetBounded( "r_lodBias", "-2", "-2", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_lodbias, -2, 2, qtrue );' in tr_init
	assert 'lod += r_lodbias->integer;' in tr_mesh

	assert 'r_lodscale = ri.Cvar_GetBounded( "r_lodScale", "10", "1", "50", CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_lodscale, 1, 50, qtrue );' in tr_init
	assert 'lodscale = r_lodscale->value;' in tr_mesh

	assert 'r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' not in tr_init
	assert 'if ( r_ext_texture_env_add->integer )' in win_glimp

	assert 'r_ignorehwgamma = ri.Cvar_Get( "r_ignoreHWGamma", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'if ( !r_ignorehwgamma->integer && r_ext_gamma_control->integer )' in win_glimp

	assert 'r_flareSize = ri.Cvar_Get ("r_flareSize", "40", CVAR_CHEAT);' in tr_init
	assert 'r_flareFade = ri.Cvar_Get ("r_flareFade", "7", CVAR_CHEAT);' in tr_init
	assert 'fade = ( ( backEnd.refdef.time - f->fadeTime ) /1000.0f ) * r_flareFade->value;' in tr_flares
	assert 'size = backEnd.viewParms.viewportWidth * ( r_flareSize->value/640.0f + 8 / -f->eyeZ );' in tr_flares

	assert 'r_znear = ri.Cvar_Get( "r_znear", "1", CVAR_CHEAT );' in tr_init
	assert 'AssertCvarRange( r_znear, 0.001f, 200, qtrue );' in tr_init
	assert 'zNear\t= r_znear->value;' in tr_main

	assert 'r_drawSkyFloor = ri.Cvar_Get( "r_drawSkyFloor", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_drawSkyFloor, 0, 1, qtrue );' in tr_init

	assert 'r_uiFullScreen = ri.Cvar_Get( "r_uifullscreen", "0", 0);' in tr_init
	assert 'Cvar_Set("r_uiFullScreen", "1");' in common
	assert 'Cvar_Set("r_uiFullScreen", "1");' in cl_main
	assert 'Cvar_Set("r_uiFullScreen", "0");' in cl_main
	assert 'if ( pStage->bundle[0].vertexLightmap && ( (r_vertexLight->integer && !r_uiFullScreen->integer) || glConfig.hardwareType == GLHW_PERMEDIA2 ) && r_lightmap->integer )' in tr_shade


def test_engine_cvar_thirtyfirst_platform_vm_steam_tranche_matches_retail_contracts() -> None:
	common = _read_text(COMMON)
	vm = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "vm.c")
	win_main = _read_text(REPO_ROOT / "src" / "code" / "win32" / "win_main.c")
	win_glimp = _read_text(WIN_GLIMP)
	win_wndproc = _read_text(WIN_WNDPROC)
	tr_init = _read_text(TR_INIT)
	sv_init = _read_text(SV_INIT)
	sv_main = _read_text(SV_MAIN)
	sv_client = _read_text(SV_CLIENT)
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")
	cl_ui = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_ui.c")

	assert 'Cvar_Get( "win_hinstance", va("%i", (int)g_wv.hInstance), CVAR_ROM );' in win_main
	assert 'cv = ri.Cvar_Get( "win_hinstance", "", 0 );' in win_glimp
	assert 'sscanf( cv->string, "%i", (int *)&g_wv.hInstance );' in win_glimp

	assert 'Cvar_Get( "win_wndproc", va("%i", (int)MainWndProc), CVAR_ROM );' in win_main
	assert 'cv = ri.Cvar_Get( "win_wndproc", "", 0 );' in win_glimp
	assert 'sscanf( cv->string, "%i", (int *)&glw_state.wndproc );' in win_glimp

	assert 'Cvar_Get( "sys_cpustring", "detect", 0 );' in win_main
	assert 'Cvar_Set( "sys_cpustring", "generic" );' in win_main
	assert 'Cvar_Set( "sys_cpustring", "Intel Pentium III" );' in win_main
	assert 'Cvar_Set( "sys_cpustring", "AMD w/ 3DNow!" );' in win_main
	assert 'Com_Printf( "WARNING: unknown sys_cpustring \'%s\'\\n", Cvar_VariableString( "sys_cpustring" ) );' in win_main
	assert 'cvar_t *sys_cpustring = ri.Cvar_Get( "sys_cpustring", "", 0 );' in tr_init
	assert 'ri.Printf( PRINT_ALL, "CPU: %s\\n", sys_cpustring->string );' in tr_init

	assert 'r_maskMinidriver = ri.Cvar_Get( "r_maskMinidriver", "0", CVAR_LATCH );' in win_glimp
	assert 'if ( strstr( buffer, "opengl32" ) != 0 || r_maskMinidriver->integer )' in win_glimp

	assert 'if ( Com_ShouldDefaultDedicatedFromExecutable() ) {' in common
	assert 'Cvar_Get( "dedicated", "2", 0 );' in common
	assert 'com_dedicated = Cvar_Get ("dedicated", "1", CVAR_ROM);' in common
	assert 'com_dedicated = Cvar_Get ("dedicated", "0", CVAR_LATCH);' in common
	assert 'if ( com_dedicated->modified ) {' in common
	assert 'Cvar_Get( "dedicated", "0", 0 );' in common
	assert 'if ( !com_dedicated || com_dedicated->integer != 2 ) {' in sv_main
	assert 'if( ((timestamp - lastWarning) > (5 * 60000)) && !Cvar_VariableIntegerValue( "dedicated" )' in win_main

	assert 'Cvar_Get( "vm_cgame", "0", CVAR_ARCHIVE );' in vm
	assert 'interpret = Cvar_VariableValue( "vm_cgame" );' in cl_cgame

	assert 'Cvar_Get( "vm_ui", "0", CVAR_ARCHIVE );' in vm
	assert 'interpret = Cvar_VariableValue( "vm_ui" );' in cl_ui

	assert 'Cvar_Get( "sv_setSteamAccount", "", CVAR_ARCHIVE | CVAR_PROTECTED );' in common
	assert 'Cvar_Get ("sv_setSteamAccount", "", CVAR_ARCHIVE | CVAR_PROTECTED );' in sv_init
	assert 'Cvar_VariableStringBuffer( "sv_setSteamAccount", steamAccount, sizeof( steamAccount ) );' in common
	assert 'QL_Steamworks_ServerLogOn( steamAccount );' in common

	assert 'steamVac = Cvar_Get( "sv_vac", "1", CVAR_SERVERINFO | CVAR_ARCHIVE );' in common
	assert 'sv_vac = Cvar_Get ("sv_vac", "1", CVAR_SERVERINFO | CVAR_ARCHIVE );' in sv_init
	assert 'if ( !QL_Steamworks_ServerInit( steamIp, (uint16_t)netPort->integer, steamVac && steamVac->integer ? qtrue : qfalse, dedicated ) ) {' in common
	assert '"VAC is disabled on this server"' not in sv_client
	assert 'SV_LogVACStatus( &from, "accepted", ( sv_vac && sv_vac->integer ) ? "enabled" : "disabled",' in sv_client
	assert 'Info_SetValueForKey( infostring, NET_GetVACInfoKey(), va("%i", sv_vac->integer) );' in sv_main

	assert 'Cvar_Set( "arch", "winnt" );' in win_main
	assert 'Cvar_Set( "arch", "win98" );' in win_main
	assert 'Cvar_Set( "arch", "win95 osr2.x" );' in win_main
	assert 'Cvar_Set( "arch", "win95" );' in win_main
	assert 'Cvar_Set( "arch", "unknown Windows variant" );' in win_main
	assert 'if ( !Q_stricmp( Cvar_VariableString( "arch" ), "winnt" ) )' in win_wndproc
	assert 'RegisterHotKey( 0, 0, MOD_ALT, VK_TAB );' in win_wndproc
	assert 'UnregisterHotKey( 0, 0 );' in win_wndproc
	assert 'SystemParametersInfo( SPI_SCREENSAVERRUNNING, 1, &old, 0 );' in win_wndproc
	assert 'SystemParametersInfo( SPI_SCREENSAVERRUNNING, 0, &old, 0 );' in win_wndproc


def test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts() -> None:
	tr_init = _read_text(TR_INIT)
	tr_backend = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c")
	tr_image = _read_text(REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c")
	win_glimp = _read_text(WIN_GLIMP)

	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' in tr_init
	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' not in tr_init
	assert 'AssertCvarRange( r_bloomPasses, 1, 2, qtrue );' in tr_init
	assert 'static int RBPP_GetBloomMode( void ) {' in tr_backend
	assert 'bloomMode = RBPP_GetBloomMode();' in tr_backend
	assert 'if ( bloomMode == 2 ) {' in tr_backend
	assert 'passes = ( r_bloomPasses && r_bloomPasses->integer > 0 ) ? r_bloomPasses->integer : 1;' not in tr_backend

	assert 'r_bloomIntensity = ri.Cvar_GetBounded( "r_bloomIntensity", "0.5", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomIntensity, 0.0f, 10.0f, qfalse );' in tr_init
	assert 'bloomIntensity = r_bloomIntensity ? r_bloomIntensity->value : 0.5f;' in tr_backend
	assert 's_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.bloomIntensityUniform, bloomIntensity );' in tr_backend

	assert 'r_bloomBrightThreshold = ri.Cvar_GetBounded( "r_bloomBrightThreshold", "0.25", "0.0", "1.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomBrightThreshold, 0.0f, 1.0f, qfalse );' in tr_init
	assert 'brightThreshold = r_bloomBrightThreshold ? r_bloomBrightThreshold->value : 0.25f;' in tr_backend
	assert 's_postProcess.procs.qglUniform1fARBFunc( s_postProcess.brightPassProgram.brightThresholdUniform, brightThreshold );' in tr_backend
	assert 'RBPP_BindRenderTarget( &s_postProcess.bloomDownsampleTarget );' in tr_backend
	assert 'RBPP_BindRectangleTexture( 0, cmd->sceneTexture );' in tr_backend
	assert 'RBPP_BindRenderTarget( &s_postProcess.bloomBrightTarget );' in tr_backend
	assert 'RBPP_BindRectangleTexture( 0, cmd->bloomDownsampleTexture );' in tr_backend

	assert 'r_bloomBlurScale = ri.Cvar_GetBounded( "r_bloomBlurScale", "0.0", "1.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomBlurScale, 1.0f, 2.0f, qfalse );' in tr_init
	assert 'r_bloomBlurScale && r_bloomBlurScale->value > 0.0f' not in tr_backend
	assert '"p_blurStep"' not in tr_backend

	assert 'r_bloomBlurRadius = ri.Cvar_GetBounded( "r_bloomBlurRadius", "5", "1", "12", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomBlurRadius, 1, 12, qtrue );' in tr_init
	assert 'r_bloomBlurRadius && r_bloomBlurRadius->integer > 0' not in tr_backend

	assert 'r_bloomBlurFalloff = ri.Cvar_GetBounded( "r_bloomBlurFalloff", "0.0", "0.75", "1.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomBlurFalloff, 0.75f, 1.0f, qfalse );' in tr_init
	assert 'r_bloomBlurFalloff && r_bloomBlurFalloff->value > 0.0f' not in tr_backend
	assert '"p_blurFalloff"' not in tr_backend

	assert 'r_bloomSaturation = ri.Cvar_GetBounded( "r_bloomSaturation", "0.8", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomSaturation, 0.0f, 10.0f, qfalse );' in tr_init
	assert 'bloomSaturation = r_bloomSaturation ? r_bloomSaturation->value : 0.8f;' in tr_backend
	assert 's_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.bloomSaturationUniform, bloomSaturation );' in tr_backend

	assert 'r_bloomSceneIntensity = ri.Cvar_GetBounded( "r_bloomSceneIntensity", "1.0", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomSceneIntensity, 0.0f, 10.0f, qfalse );' in tr_init
	assert 'sceneIntensity = r_bloomSceneIntensity ? r_bloomSceneIntensity->value : 1.0f;' in tr_backend
	assert 's_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.sceneIntensityUniform, sceneIntensity );' in tr_backend

	assert 'r_bloomSceneSaturation = ri.Cvar_GetBounded( "r_bloomSceneSaturation", "1.0", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_bloomSceneSaturation, 0.0f, 10.0f, qfalse );' in tr_init
	assert 'sceneSaturation = r_bloomSceneSaturation ? r_bloomSceneSaturation->value : 1.0f;' in tr_backend
	assert 's_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.sceneSaturationUniform, sceneSaturation );' in tr_backend

	assert 'r_picmip = ri.Cvar_Get ("r_picmip", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_picmip, 0, 16, qtrue );' in tr_init
	assert 'ri.Printf( PRINT_ALL, "picmip: %d\\n", r_picmip->integer );' in tr_init
	assert 'scaled_width >>= r_picmip->integer;' in tr_image
	assert 'scaled_height >>= r_picmip->integer;' in tr_image
	assert 'ri.Cvar_Set( "r_picmip", "2" );' in win_glimp
	assert 'ri.Cvar_Set( "r_picmip", "1" );' in win_glimp


def test_engine_cvar_thirtythird_server_botlib_tranche_matches_retail_contracts() -> None:
	sv_bot = _read_text(REPO_ROOT / "src" / "code" / "server" / "sv_bot.c")
	sv_game = _read_text(REPO_ROOT / "src" / "code" / "server" / "sv_game.c")
	ai_main = _read_text(REPO_ROOT / "src" / "code" / "game" / "ai_main.c")
	ai_dmq3 = _read_text(REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c")
	q_shared = _read_text(REPO_ROOT / "src" / "code" / "game" / "q_shared.h")
	be_interface = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c")
	be_aas_main = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c")
	be_aas_reach = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_aas_reach.c")
	be_ai_char = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_ai_char.c")
	be_ai_chat = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_ai_chat.c")
	ql_steam_ghidra = _read_text(REPO_ROOT / "src2" / "ghidra" / "quakelive_steam" / "quakelive_steam_decomp.cpp")
	ql_steam_hlil_part04 = _read_text(
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "quakelive_steam.exe"
		/ "quakelive_steam.exe_hlil_split"
		/ "quakelive_steam.exe_hlil_part04.txt"
	)
	qagame_hlil_part01 = _read_text(
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "qagamex86.dll"
		/ "qagamex86.dll.bndb_hlil_split"
		/ "qagamex86.dll.bndb_hlil_part01.txt"
	)
	qagame_ghidra = _read_text(REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "qagamex86" / "decompile_top_functions.c")

	assert 'Cvar_Get("bot_enable", "1", CVAR_ROM);' in sv_bot
	assert 'var = Cvar_Get( "bot_enable", "1", CVAR_LATCH );' in sv_game
	assert 'Cvar_Get("bot_enable", &DAT_00551624, 0x40);' in ql_steam_ghidra
	assert 'sub_4ce0d0(x87_r0, "bot_enable", U"1", 0x40)' in ql_steam_hlil_part04

	assert 'Cvar_Get("bot_developer", "0", CVAR_CHEAT);' in sv_bot
	assert 'bot_developer = LibVarGetValue("bot_developer");' in be_interface
	assert 'if (bot_developer)' in be_aas_main

	assert 'Cvar_Get("bot_debug", "0", CVAR_CHEAT);' in sv_bot
	assert 'if (!bot_debug) bot_debug = Cvar_Get("bot_debug", "0", 0);' in sv_bot
	assert 'if (bot_enable && bot_debug->integer) {' in sv_bot

	assert 'Cvar_Get("bot_maxdebugpolys", "2", 0);' in sv_bot
	assert 'bot_maxdebugpolys = Cvar_VariableIntegerValue("bot_maxdebugpolys");' in sv_bot
	assert 'debugpolygons = Z_Malloc(sizeof(bot_debugpoly_t) * bot_maxdebugpolys);' in sv_bot
	assert 'for (i = 0; i < bot_maxdebugpolys; i++) {' in sv_bot

	assert 'Cvar_Get("bot_groundonly", "1", 0);' in sv_bot
	assert 'if (!bot_groundonly) bot_groundonly = Cvar_Get("bot_groundonly", "1", 0);' in sv_bot
	assert 'if (bot_groundonly->integer) parm0 |= 4;' in sv_bot

	assert 'Cvar_Get("bot_reachability", "0", 0);' in sv_bot
	assert 'if (!bot_reachability) bot_reachability = Cvar_Get("bot_reachability", "0", 0);' in sv_bot
	assert 'if (bot_reachability->integer) parm0 |= 2;' in sv_bot

	assert 'if (!bot_highlightarea) bot_highlightarea = Cvar_Get("bot_highlightarea", "0", 0);' in sv_bot
	assert 'botlib_export->BotLibVarSet("bot_highlightarea", bot_highlightarea->string);' in sv_bot

	assert 'Cvar_Get("bot_visualizejumppads", "0", CVAR_CHEAT);' in sv_bot
	assert 'bot_visualizejumppads = LibVarValue("bot_visualizejumppads", "0");' in be_aas_reach
	assert 'velocity, cmdmove, 0, 30, 0.1f, bboxmins, bboxmaxs, bot_visualizejumppads);' in be_aas_reach
	assert 'SE_ENTERLAVA|SE_HITGROUNDDAMAGE|SE_TOUCHJUMPPAD|SE_TOUCHTELEPORTER, 0, bot_visualizejumppads);' in be_aas_reach

	assert 'Cvar_Get("bot_reloadcharacters", "0", 0);' in sv_bot
	assert 'if (!LibVarGetValue("bot_reloadcharacters")) return;' in be_ai_char
	assert 'BotLoadCachedCharacter(charfile, skill, LibVarGetValue("bot_reloadcharacters"));' in be_ai_char
	assert 'if (!LibVarGetValue("bot_reloadcharacters"))' in be_ai_chat

	assert 'Cvar_Get("bot_testichat", "0", 0);' in sv_bot
	assert 'if (LibVarGetValue("bot_testichat")) {' in be_ai_chat
	assert 'botimport.Print(PRT_MESSAGE, "%s has %d chat lines\\n", type, t->numchatmessages);' in be_ai_chat

	assert 'Cvar_Get("bot_testrchat", "0", 0);' in sv_bot
	assert 'if (LibVarGetValue("bot_testrchat"))' in be_ai_chat

	assert 'Cvar_Get("bot_thinktime", "100", 0);' in sv_bot
	assert 'Cvar_Get("bot_thinktime", "100", CVAR_CHEAT);' not in sv_bot
	assert 'trap_Cvar_Register(&bot_thinktime, "bot_thinktime", "100", 0);' in ai_main
	assert 'trap_Cvar_Register(&bot_thinktime, "bot_thinktime", "100", CVAR_CHEAT);' not in ai_main
	assert 'Cvar_Get("bot_thinktime", &DAT_0052f690, 0);' in ql_steam_ghidra
	assert 'sub_4ce0d0(x87_r0, "bot_thinktime", "100", 0)' in ql_steam_hlil_part04
	assert '(*(data_104b13ac + 0x44))(0x105e3900, "bot_thinktime", &data_1007e154, 0)' in qagame_hlil_part01
	assert '(*(data_104b13ac + 0x44))(0x105e2de0, "bot_memorydump", &data_1007d0a8, 0x200)' in qagame_hlil_part01
	assert '(*(data_104b13ac + 0x44))(0x105e2ba0, "bot_saveroutingcache", &data_1007d0a8, 0x200)' in qagame_hlil_part01

	assert 'if (bot_memorydump.integer) {' in ai_main
	assert 'trap_BotLibVarSet("memorydump", "1");' in ai_main
	assert 'trap_Cvar_Set("bot_memorydump", "0");' in ai_main
	assert 'if (bot_saveroutingcache.integer) {' in ai_main
	assert 'trap_BotLibVarSet("saveroutingcache", "1");' in ai_main
	assert 'trap_Cvar_Set("bot_saveroutingcache", "0");' in ai_main
	assert 'if (bot_thinktime.integer > 200) {' in ai_main
	assert 'trap_Cvar_Set("bot_thinktime", "200");' in ai_main
	assert 'trap_BotLibVarSet("bot_showPath", "0");' in ai_main
	assert '(*(data_104b13ac + 0xcc))("memorydump", &data_1007d1d8)' in qagame_hlil_part01
	assert '(*(data_104b13ac + 0x3c))("bot_memorydump", &data_1007d0a8)' in qagame_hlil_part01
	assert '(*(data_104b13ac + 0xcc))("saveroutingcache", &data_1007d1d8)' in qagame_hlil_part01
	assert '(*(data_104b13ac + 0x3c))("bot_saveroutingcache", &data_1007d0a8)' in qagame_hlil_part01
	assert '(*(data_104b13ac + 0x3c))("bot_thinktime", &data_1007dfe0)' in qagame_hlil_part01
	assert '(*(data_104b13ac + 0xcc))("bot_showPath", 0x104b1cd4)' in qagame_hlil_part01

	assert 'Cvar_Get("bot_grapple", "1", 0);' in sv_bot
	assert 'Cvar_Get("bot_grapple", "0", 0);' not in sv_bot
	assert 'trap_Cvar_Register(&bot_grapple, "bot_grapple", "1", 0);' in ai_dmq3
	assert 'trap_Cvar_Register(&bot_grapple, "bot_grapple", "0", 0);' not in ai_dmq3
	assert 'Cvar_Get("bot_grapple", &DAT_00551624, 0);' in ql_steam_ghidra
	assert 'sub_4ce0d0(x87_r4, "bot_grapple", U"1", 0)' in ql_steam_hlil_part04
	assert '(**(code **)(DAT_104b13ac + 0x44))(&DAT_105e4280,"bot_grapple",&DAT_1007d1d8,0);' in qagame_ghidra

	assert '#define CVAR_CLOUD' in q_shared
	assert '0x80000' in q_shared
	assert 'trap_Cvar_Register(&bot_nochat, "bot_nochat", "0", CVAR_CLOUD);' in ai_dmq3
	assert 'trap_Cvar_Register(&bot_nochat, "bot_nochat", "0", 0);' not in ai_dmq3
	assert 'trap_Cvar_Register(&bot_challenge, "bot_challenge", "0", CVAR_CLOUD);' in ai_dmq3
	assert 'trap_Cvar_Register(&bot_challenge, "bot_challenge", "0", 0);' not in ai_dmq3
	assert '(**(code **)(DAT_104b13ac + 0x44))(&DAT_105e3d20,"bot_nochat",&DAT_1007d0a8,0x80000);' in qagame_ghidra
	assert '(**(code **)(DAT_104b13ac + 0x44))(&DAT_105e3e80,"bot_challenge",&DAT_1007d0a8,0x80000);' in qagame_ghidra


def test_engine_cvar_thirtyfourth_server_botlib_import_bridge_matches_retail_contracts() -> None:
	sv_bot = _read_text(SV_BOT)
	sv_game = _read_text(SV_GAME)
	botlib_h = _read_text(BOTLIB_H)
	aliases = json.loads(_read_text(REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	ql_steam_hlil_part04 = _read_text(QL_STEAM_HLIL_PART04)
	round_61 = _read_text(REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_61.md")

	for raw_name, normalized_name in (
		("sub_4DD0B0", "BotImport_Trace"),
		("sub_4DD160", "BotImport_EntityTrace"),
		("sub_4DD210", "BotImport_PointContents"),
		("sub_4DD230", "BotImport_inPVS"),
		("sub_4DD240", "BotImport_BSPEntityData"),
		("sub_4DD250", "BotImport_BSPModelMinsMaxsOrigin"),
		("sub_4DD350", "BotImport_GetMemory"),
		("sub_4DD370", "BotImport_FreeMemory"),
		("sub_4DD380", "BotImport_HunkAlloc"),
		("sub_4DD3B0", "BotImport_DebugPolygonCreate"),
		("sub_4DD430", "BotImport_DebugPolygonDelete"),
		("sub_4DD450", "BotImport_DebugLineCreate"),
		("sub_4DD480", "BotImport_DebugLineShow"),
		("sub_4DD640", "BotClientCommand"),
		("sub_4DD6A0", "SV_BotLibSetup"),
		("sub_4DD6D0", "SV_BotLibShutdown"),
		("sub_4DD940", "SV_BotInitBotLib"),
	):
		assert aliases[raw_name] == normalized_name
		assert f"`{raw_name} -> {normalized_name}`" in round_61

	botlib_import_decl = _extract_function_block(
		botlib_h,
		"typedef struct botlib_import_s",
	)
	botlib_init = _extract_function_block(sv_bot, "void SV_BotInitBotLib(void)")
	bot_trace = _extract_function_block(
		sv_bot,
		"void BotImport_Trace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int passent, int contentmask)",
	)
	bot_entity_trace = _extract_function_block(
		sv_bot,
		"void BotImport_EntityTrace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int entnum, int contentmask)",
	)
	bsp_entity_data = _extract_function_block(sv_bot, "char *BotImport_BSPEntityData(void)")
	bsp_model_bounds = _extract_function_block(
		sv_bot,
		"void BotImport_BSPModelMinsMaxsOrigin(int modelnum, vec3_t angles, vec3_t outmins, vec3_t outmaxs, vec3_t origin)",
	)
	debug_polygon_create = _extract_function_block(
		sv_bot,
		"int BotImport_DebugPolygonCreate(int color, int numPoints, vec3_t *points)",
	)
	debug_line_create = _extract_function_block(sv_bot, "int BotImport_DebugLineCreate(void)")
	debug_line_show = _extract_function_block(
		sv_bot,
		"void BotImport_DebugLineShow(int line, vec3_t start, vec3_t end, int color)",
	)
	debug_draw = _extract_function_block(
		sv_bot,
		"void BotDrawDebugPolygons(void (*drawPoly)(int color, int numPoints, float *points), int value)",
	)
	legacy_syscalls = _extract_function_block(
		sv_game,
		"static int SV_GameSystemCallsImpl( int *args, qboolean logContract )",
	)

	for expected in (
		"void\t\t(QDECL *Print)(int type, char *fmt, ...);",
		"void\t\t(*Trace)(bsp_trace_t *trace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int passent, int contentmask);",
		"void\t\t(*EntityTrace)(bsp_trace_t *trace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int entnum, int contentmask);",
		"int\t\t\t(*PointContents)(vec3_t point);",
		"int\t\t\t(*inPVS)(vec3_t p1, vec3_t p2);",
		"char\t\t*(*BSPEntityData)(void);",
		"void\t\t(*BSPModelMinsMaxsOrigin)(int modelnum, vec3_t angles, vec3_t mins, vec3_t maxs, vec3_t origin);",
		"void\t\t(*BotClientCommand)(int client, char *command);",
		"void\t\t*(*GetMemory)(int size);",
		"void\t\t(*FreeMemory)(void *ptr);",
		"int\t\t\t(*AvailableMemory)(void);",
		"void\t\t*(*HunkAlloc)(int size);",
		"int\t\t\t(*FS_FOpenFile)( const char *qpath, fileHandle_t *file, fsMode_t mode );",
		"int\t\t\t(*DebugLineCreate)(void);",
		"void\t\t(*DebugLineShow)(int line, vec3_t start, vec3_t end, int color);",
		"int\t\t\t(*DebugPolygonCreate)(int color, int numPoints, vec3_t *points);",
		"void\t\t(*DebugPolygonDelete)(int id);",
	):
		assert expected in botlib_import_decl

	for expected in (
		"botlib_import.Print = BotImport_Print;",
		"botlib_import.Trace = BotImport_Trace;",
		"botlib_import.EntityTrace = BotImport_EntityTrace;",
		"botlib_import.PointContents = BotImport_PointContents;",
		"botlib_import.inPVS = BotImport_inPVS;",
		"botlib_import.BSPEntityData = BotImport_BSPEntityData;",
		"botlib_import.BSPModelMinsMaxsOrigin = BotImport_BSPModelMinsMaxsOrigin;",
		"botlib_import.BotClientCommand = BotClientCommand;",
		"botlib_import.GetMemory = BotImport_GetMemory;",
		"botlib_import.FreeMemory = BotImport_FreeMemory;",
		"botlib_import.AvailableMemory = Z_AvailableMemory;",
		"botlib_import.HunkAlloc = BotImport_HunkAlloc;",
		"botlib_import.FS_FOpenFile = FS_FOpenFileByMode;",
		"botlib_import.DebugLineCreate = BotImport_DebugLineCreate;",
		"botlib_import.DebugLineDelete = BotImport_DebugPolygonDelete;",
		"botlib_import.DebugLineShow = BotImport_DebugLineShow;",
		"botlib_import.DebugPolygonCreate = BotImport_DebugPolygonCreate;",
		"botlib_import.DebugPolygonDelete = BotImport_DebugPolygonDelete;",
		"GetBotLibAPI( BOTLIB_API_VERSION, &botlib_import );",
	):
		assert expected in botlib_init

	for expected in (
		"int32_t (* var_5c)(int32_t arg1, int32_t arg2) = sub_4dcf90",
		"int32_t (* var_58)(int32_t* arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5,",
		"int32_t (* var_54)(int32_t* arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5,",
		"int32_t (* var_50)(float* arg1) = sub_4dd210",
		"int32_t (* var_4c)() = sub_4dd230",
		"int32_t (* var_48)() = j_sub_4c0250",
		"float* (* var_44)(int32_t arg1, float* arg2, float* arg3, float* arg4, float* arg5) =",
		"void* (* var_40)(int32_t arg1, char* arg2) = sub_4dd640",
		"void* (* var_3c)(int32_t arg1) = sub_4dd350",
		"int32_t (* var_38)() = sub_4dd370",
		"int32_t (* var_34)() = sub_4c9220",
		"char* (* var_30)(int32_t arg1) = sub_4dd380",
		"int32_t (* var_18)() = sub_4dd450",
		"int32_t (* var_14)(int32_t arg1) = sub_4dd430",
		"int32_t (* var_10)(int32_t arg1, float* arg2, float* arg3, int32_t arg4) = sub_4dd480",
		"int32_t (* var_c)(int32_t arg1, int32_t arg2, int32_t* arg3) = sub_4dd3b0",
		"int32_t (* var_8)(int32_t arg1) = sub_4dd430",
		"int32_t result = sub_4a83c0(2, &var_5c)",
	):
		assert expected in ql_steam_hlil_part04

	assert "SV_Trace(&trace, start, mins, maxs, end, passent, contentmask, qfalse);" in bot_trace
	assert "SV_ClipToEntity(&trace, start, mins, maxs, end, entnum, contentmask, qfalse);" in bot_entity_trace
	for trace_block in (bot_trace, bot_entity_trace):
		assert "bsptrace->allsolid = trace.allsolid;" in trace_block
		assert "bsptrace->startsolid = trace.startsolid;" in trace_block
		assert "bsptrace->fraction = trace.fraction;" in trace_block
		assert "VectorCopy(trace.endpos, bsptrace->endpos);" in trace_block
		assert "bsptrace->surface.value = trace.surfaceFlags;" in trace_block
		assert "bsptrace->ent = trace.entityNum;" in trace_block
		assert "bsptrace->exp_dist = 0;" in trace_block
		assert "bsptrace->sidenum = 0;" in trace_block
		assert "bsptrace->contents = 0;" in trace_block
	assert "004dd0e4  sub_4e6930(&var_40, arg2, arg3, arg4, arg5, arg6, arg7, 0)" in ql_steam_hlil_part04
	assert "004dd194  sub_4e6690(&var_40, arg2, arg3, arg4, arg5, arg6, arg7, 0)" in ql_steam_hlil_part04
	assert "004dd147  arg1[0xb] = fconvert.s(float.t(0))" in ql_steam_hlil_part04
	assert "004dd14a  arg1[0xc] = 0" in ql_steam_hlil_part04
	assert "004dd14d  arg1[0x13] = 0" in ql_steam_hlil_part04

	assert "return CM_EntityString();" in bsp_entity_data
	assert "004dd240    int32_t j_sub_4c0250()" in ql_steam_hlil_part04
	assert "004dd240  return sub_4c0250() __tailcall" in ql_steam_hlil_part04

	assert "h = CM_InlineModel(modelnum);" in bsp_model_bounds
	assert "CM_ModelBounds(h, mins, maxs);" in bsp_model_bounds
	assert "if ((angles[0] || angles[1] || angles[2])) {" in bsp_model_bounds
	assert "max = RadiusFromBounds(mins, maxs);" in bsp_model_bounds
	assert "if (outmins) VectorCopy(mins, outmins);" in bsp_model_bounds
	assert "if (outmaxs) VectorCopy(maxs, outmaxs);" in bsp_model_bounds
	assert "if (origin) VectorClear(origin);" in bsp_model_bounds
	assert "004dd27e  sub_4c0540(sub_4c0210(arg1), &var_14, &var_20)" in ql_steam_hlil_part04
	assert "004dd2c0      long double st0_1" in ql_steam_hlil_part04
	assert "004dd303  if (arg4 != 0)" in ql_steam_hlil_part04
	assert "004dd31a  arg5[2] = fconvert.s(x87_r7)" in ql_steam_hlil_part04

	assert "for (i = 1; i < bot_maxdebugpolys; i++)" in debug_polygon_create
	assert "if (i >= bot_maxdebugpolys)" in debug_polygon_create
	assert "poly->inuse = qtrue;" in debug_polygon_create
	assert "poly->color = color;" in debug_polygon_create
	assert "poly->numPoints = numPoints;" in debug_polygon_create
	assert "Com_Memcpy(poly->points, points, numPoints * sizeof(vec3_t));" in debug_polygon_create
	assert "return BotImport_DebugPolygonCreate(0, 0, points);" in debug_line_create
	assert "VectorMA(points[0], 2, cross, points[0]);" in debug_line_show
	assert "BotImport_DebugPolygonShow(line, color, 4, points);" in debug_line_show
	assert "004dd3b3  void* edx = data_12cdeb0" in ql_steam_hlil_part04
	assert "004dd3cf  if (ecx s> 1)" in ql_steam_hlil_part04
	assert "004dd415          *eax_7 = 1" in ql_steam_hlil_part04
	assert "004dd420          sub_4cb7d0(eax_7 + 0xc, arg3, arg2 * 0xc)" in ql_steam_hlil_part04
	assert "004dd468  void var_14" in ql_steam_hlil_part04
	assert "004dd468  int32_t result = sub_4dd3b0(0, 0, &var_14)" in ql_steam_hlil_part04
	assert "004dd615      *eax_6 = 1" in ql_steam_hlil_part04
	assert "004dd61b      eax_6[1] = arg4" in ql_steam_hlil_part04
	assert "004dd61e      eax_6[2] = 4" in ql_steam_hlil_part04
	assert "004dd62a      result = sub_4cb7d0(&eax_6[3], &var_44, 0x30)" in ql_steam_hlil_part04

	assert 'botlib_export->BotLibVarSet("bot_highlightarea", bot_highlightarea->string);' in debug_draw
	assert "botlib_export->Test(parm0, NULL, svs.clients[0].gentity->r.currentOrigin," in debug_draw
	assert "drawPoly(poly->color, poly->numPoints, (float *) poly->points);" in debug_draw
	assert "004dcf0d          (*(data_13e1844 + 0x1f8))(\"bot_highlightarea\", eax_3[1])" in ql_steam_hlil_part04
	assert "004dcf37          (*(data_13e1844 + 0x220))(esi_1, 0, eax_5 + 0x220, eax_5 + 0x22c)" in ql_steam_hlil_part04

	assert "case G_DEBUG_POLYGON_CREATE:" in legacy_syscalls
	assert "return BotImport_DebugPolygonCreate( args[1], args[2], VMA(3) );" in legacy_syscalls
	assert "case G_DEBUG_POLYGON_DELETE:" in legacy_syscalls
	assert "BotImport_DebugPolygonDelete( args[1] );" in legacy_syscalls
	assert "case BOTLIB_SETUP:" in legacy_syscalls
	assert "return SV_BotLibSetup();" in legacy_syscalls
