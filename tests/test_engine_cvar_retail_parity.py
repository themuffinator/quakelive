from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

WIN_GLIMP = REPO_ROOT / "src" / "code" / "win32" / "win_glimp.c"
WIN_INPUT = REPO_ROOT / "src" / "code" / "win32" / "win_input.c"
WIN_NET = REPO_ROOT / "src" / "code" / "win32" / "win_net.c"
WIN_WNDPROC = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"
CL_MAIN = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_CONSOLE = REPO_ROOT / "src" / "code" / "client" / "cl_console.c"
CL_CIN = REPO_ROOT / "src" / "code" / "client" / "cl_cin.c"
SND_DMA = REPO_ROOT / "src" / "code" / "client" / "snd_dma.c"
SND_MIX = REPO_ROOT / "src" / "code" / "client" / "snd_mix.c"
SV_INIT = REPO_ROOT / "src" / "code" / "server" / "sv_init.c"
SV_MAIN = REPO_ROOT / "src" / "code" / "server" / "sv_main.c"
SV_SNAPSHOT = REPO_ROOT / "src" / "code" / "server" / "sv_snapshot.c"
SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SV_CLIENT = REPO_ROOT / "src" / "code" / "server" / "sv_client.c"
SV_CCMDS = REPO_ROOT / "src" / "code" / "server" / "sv_ccmds.c"
CL_PARSE = REPO_ROOT / "src" / "code" / "client" / "cl_parse.c"
COMMON = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
TR_INIT = REPO_ROOT / "src" / "code" / "renderer" / "tr_init.c"
QCOMMON_CVAR = REPO_ROOT / "src" / "code" / "qcommon" / "cvar.c"
FILES = REPO_ROOT / "src" / "code" / "qcommon" / "files.c"
NET_CHAN = REPO_ROOT / "src" / "code" / "qcommon" / "net_chan.c"
AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
BE_AAS_FILE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_file.c"
SERVER_H = REPO_ROOT / "src" / "code" / "server" / "server.h"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8", errors="ignore")


def test_engine_cvar_registrations_match_targeted_retail_contracts() -> None:
	win_glimp = _read_text(WIN_GLIMP)
	win_input = _read_text(WIN_INPUT)
	win_wndproc = _read_text(WIN_WNDPROC)
	cl_main = _read_text(CL_MAIN)
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
	assert 'if ( cl_demoRecordMessage->integer >= 2 ) {' in cl_main
	assert 'if ( cl_demoRecordMessage->integer ) {' in cl_main

	assert 'cl_platform = Cvar_Get ("cl_platform", "1", CVAR_ROM );' in cl_main

	assert 'sv_serverType = Cvar_Get ("sv_serverType", "0", CVAR_ARCHIVE );' in sv_init
	assert 'serverType = sv_serverType ? sv_serverType->integer : 0;' in sv_main
	assert 'Info_SetValueForKey( infostring, "serverType", va("%i", sv_serverType->integer) );' in sv_main
	assert 'serverType = sv_serverType ? sv_serverType->integer : 0;' in sv_client


def test_engine_cvar_second_tranche_matches_retail_contracts() -> None:
	cl_main = _read_text(CL_MAIN)
	cl_console = _read_text(CL_CONSOLE)
	sv_init = _read_text(SV_INIT)
	sv_client = _read_text(SV_CLIENT)
	cl_input = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_input.c")
	cl_cgame = _read_text(REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c")

	assert 'con_opacity = Cvar_GetBounded( "con_opacity", "0.9", "0.1", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_console
	assert 'color[3] = con_opacity ? Com_Clamp( 0.1f, 1.0f, con_opacity->value ) : 0.9f;' in cl_console

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
	assert 'if ( cl_autoTimeNudge->integer ) {' in cl_cgame

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

	assert 'Cvar_Get ("protocol", va("%i", PROTOCOL_VERSION), CVAR_SERVERINFO | CVAR_ROM);' in sv_init
	assert 'version = atoi( Info_ValueForKey( userinfo, "protocol" ) );' in sv_client
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "print\\nServer uses protocol version %i.\\n", PROTOCOL_VERSION );' in sv_client
	assert 'Info_SetValueForKey( infostring, "protocol", va("%i", PROTOCOL_VERSION) );' in sv_main

	assert 'sv_mapname = Cvar_Get ("mapname", "nomap", CVAR_SERVERINFO | CVAR_ROM);' in sv_init
	assert 'Cvar_Set( "mapname", server );' in sv_init
	assert 'Info_SetValueForKey( infostring, "mapname", sv_mapname->string );' in sv_main

	assert 'sv_privateClients = Cvar_Get ("sv_privateClients", "0", CVAR_SERVERINFO);' in sv_init
	assert 'startIndex = sv_privateClients->integer;' in sv_client
	assert 'sv_maxclients->integer - sv_privateClients->integer' in sv_main

	assert 'sv_maxclients = Cvar_Get ("sv_maxclients", "8", CVAR_SERVERINFO | CVAR_LATCH);' in sv_init
	assert 'QL_Steamworks_ServerSetMaxPlayerCount( sv_maxclients ? sv_maxclients->integer : 0 );' in sv_main
	assert 'svs.clients = Z_Malloc (sizeof(client_t) * sv_maxclients->integer );' in sv_init

	assert 'Cvar_Get ("sv_cheats", "1", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'if ( Cvar_VariableIntegerValue( "sv_cheats" ) ) {' in sv_main
	assert 'SV_SteamServerAppendGameTag( tags, size, "cheats" );' in sv_main

	assert 'sv_serverid = Cvar_Get ("sv_serverid", "0", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_serverid", va("%i", sv.serverId ) );' in sv_init
	assert 'Cvar_Set( "sv_serverid", va("%i", sv.serverId ) );' in sv_ccmds
	assert 'cl.serverId = atoi( Info_ValueForKey( systemInfo, "sv_serverid" ) );' in cl_parse

	assert 'sv_pure = Cvar_Get ("sv_pure", "1", CVAR_SYSTEMINFO | CVAR_INIT );' in sv_init
	assert 'if ( sv_pure->integer ) {' in sv_init
	assert 'if ( sv_pure->integer != 0 ) {' in sv_client
	assert 'cl_connectedToPureServer = Cvar_VariableValue( "sv_pure" );' in cl_parse

	assert 'sv_privatePassword = Cvar_Get ("sv_privatePassword", "", CVAR_TEMP );' in sv_init
	assert 'password = Info_ValueForKey( userinfo, "password" );' in sv_client
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
	ai_main = _read_text(AI_MAIN)
	be_aas_file = _read_text(BE_AAS_FILE)
	server_h = _read_text(SERVER_H)
	qcommon_cm_trace = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "cm_trace.c")

	assert 'Cvar_Get ("sv_paks", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_paks", p );' in sv_init
	assert 'Cvar_Set( "sv_paks", "" );' in sv_init
	assert 's = Info_ValueForKey( systemInfo, "sv_paks" );' in cl_parse
	assert 'FS_PureServerSetLoadedPaks( s, t );' in cl_parse

	assert 'Cvar_Get ("sv_pakNames", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_pakNames", p );' in sv_init
	assert 'Cvar_Set( "sv_pakNames", "" );' in sv_init
	assert 't = Info_ValueForKey( systemInfo, "sv_pakNames" );' in cl_parse
	assert 'void FS_PureServerSetLoadedPaks( const char *pakSums, const char *pakNames ) {' in files

	assert 'Cvar_Get ("sv_referencedPaks", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_referencedPaks", p );' in sv_init
	assert 's = Info_ValueForKey( systemInfo, "sv_referencedPaks" );' in cl_parse
	assert 'FS_PureServerSetReferencedPaks( s, t );' in cl_parse

	assert 'Cvar_Get ("sv_referencedPakNames", "", CVAR_SYSTEMINFO | CVAR_ROM );' in sv_init
	assert 'Cvar_Set( "sv_referencedPakNames", p );' in sv_init
	assert 't = Info_ValueForKey( systemInfo, "sv_referencedPakNames" );' in cl_parse
	assert 'void FS_PureServerSetReferencedPaks( const char *pakSums, const char *pakNames ) {' in files

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
	common = _read_text(COMMON)
	cmd = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "cmd.c")

	assert 'con_background = Cvar_GetBounded( "con_background", "0", "0", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in cl_console
	assert 'else if ( con_background && con_background->integer > 0 && cls.consoleShader ) {' in cl_console

	assert 'con_matchlimit = Cvar_Get( "con_matchlimit", "16", 0 );' in cl_console
	assert 'limit = ( con_matchlimit && con_matchlimit->integer > 0 ) ? con_matchlimit->integer : 16;' in cl_console

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

	assert 'cl_run = Cvar_Get ("cl_run", "1", CVAR_ARCHIVE);' in cl_main
	assert 'if ( in_speed.active ^ cl_run->integer ) {' in cl_input

	assert 'cl_viewAccel = Cvar_Get ("cl_viewAccel", "1.7", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'cl.viewangles[YAW] -= cl_viewAccel->value * m_yaw->value * mx;' in cl_input
	assert 'cl.viewangles[PITCH] += cl_viewAccel->value * m_pitch->value * my;' in cl_input

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
	assert 'accelSensitivity += cl_sensitivity->value;' in cl_input

	assert 'cl_mouseAccel = Cvar_Get ("cl_mouseAccel", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'accelSensitivity = cl_mouseAccel->value * powf( rate - cl_mouseAccelOffset->value, cl_mouseAccelPower->value );' in cl_input

	assert 'cl_mouseAccelPower = Cvar_Get ("cl_mouseAccelPower", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl_mouseAccelPower->value' in cl_input

	assert 'cl_mouseSensCap = Cvar_Get ("cl_mouseSensCap", "0", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'if ( cl_mouseSensCap->value > 0.0f && accelSensitivity > cl_mouseSensCap->value ) {' in cl_input

	assert 'm_filter = Cvar_Get ("m_filter", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'if ( m_filter->integer ) {' in cl_input

	assert 'm_cpi = Cvar_Get ("m_cpi", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'translatedDx = CL_TranslateRetailMouseDelta( dx, m_cpi->value );' in cl_input
	assert 'cpiScale = m_cpi->value;' in cl_input
	assert 'cpiScale = 1000.0f / cpiScale;' in cl_input


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
	assert 'cl.viewangles[PITCH] += cl_viewAccel->value * m_pitch->value * my;' in cl_input

	assert 'm_side = Cvar_Get ("m_side", "0.25", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert 'cmd->rightmove = ClampChar( cmd->rightmove + m_side->value * mx );' in cl_input

	assert 'm_yaw = Cvar_Get ("m_yaw", "0.022", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'cl.viewangles[YAW] -= cl_viewAccel->value * m_yaw->value * mx;' in cl_input

	assert 'Cvar_Get( "cl_maxPing", "800", CVAR_ARCHIVE );' in cl_main
	assert 'maxPing = Cvar_VariableIntegerValue( "cl_maxPing" );' in cl_main
	assert 'if( maxPing < 100 ) {' in cl_main

	assert 'Cvar_Get ("name", "UnnamedPlayer", CVAR_USERINFO | CVAR_ROM );' in cl_main
	assert 'Cvar_Set( "name", personaName );' in cl_main
	assert 'Cvar_Set( "name", "anon" );' in cl_main

	assert 'Cvar_Get ("country", "", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert 'Cvar_VariableStringBuffer( "country", country, sizeof( country ) );' in cl_main
	assert 'Cvar_Set( "country", country );' in cl_main
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
	assert '{ &cg_autoAction, "cg_autoAction", "0", CVAR_ARCHIVE | CVAR_LATCH },' in cg_main
	assert 'cg.autoActionFlags = cg_autoAction.integer;' in cg_main
	assert 'flags = cg.autoActionFlags;' in cg_main

	assert 'Cvar_Get ("cg_autoHop", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert '{ &cg_autoHop, "cg_autoHop", "1", CVAR_ARCHIVE | CVAR_LATCH },' in cg_main
	assert 'cg.autoHopEnabled = (qboolean)( cg_autoHop.integer != 0 );' in cg_main

	assert 'Cvar_Get ("cg_predictItems", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in cl_main
	assert '{ &cg_predictItems, "cg_predictItems", "1", CVAR_ARCHIVE },' in cg_main
	assert 'if ( !cg_predictItems.integer ) {' in cg_predict
	assert 's = Info_ValueForKey( userinfo, "cg_predictItems" );' in g_client

	assert 'Cvar_Get ("cg_viewsize", "100", CVAR_ARCHIVE | CVAR_CLOUD );' in cl_main
	assert '{ &cg_viewsize, "cg_viewsize", "100", CVAR_ARCHIVE },' in cg_main
	assert 'if (cg_viewsize.integer < 30) {' in cg_view
	assert 'trap_Cvar_Set("cg_viewsize", va("%i",(int)(cg_viewsize.integer+10)));' in cg_consolecmds

	assert 'Cvar_Get ("handicap", "100", CVAR_USERINFO | CVAR_TEMP );' in cl_main
	assert 'health = atoi( Info_ValueForKey( userinfo, "handicap" ) );' in g_client
	assert 'val = Info_ValueForKey (cl->userinfo, "handicap");' in sv_client
	assert 'Info_SetValueForKey( cl->userinfo, "handicap", "100" );' in sv_client

	assert 'Cvar_Get ("headmodel", "sarge", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );' in cl_main
	assert 'Cvar_Set( "headmodel", arg );' in cl_main
	assert 'trap_Cvar_Register(NULL, "headmodel", DEFAULT_HEAD, CVAR_USERINFO | CVAR_ARCHIVE );' in cg_main
	assert 'Q_strncpyz( headModel, Info_ValueForKey (userinfo, "headmodel"), sizeof( headModel ) );' in g_client

	assert 'Cvar_Get ("password", "", CVAR_USERINFO | CVAR_TEMP);' in cl_main
	assert 'Cvar_Set( "password", password );' in cl_main
	assert 'value = Info_ValueForKey (userinfo, "password");' in g_client
	assert 'password = Info_ValueForKey( userinfo, "password" );' in sv_client
	assert 'if ( !Q_stricmp( var->name, "cl_cdkey" ) || !Q_stricmp( var->name, "password" ) ) {' in cvar

	assert 'Cvar_Get ("sex", "male", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );' in cl_main
	assert '} else if ( !Q_stricmp( token, "sex" ) ) {' in cg_players
	assert 'ci->gender = GENDER_FEMALE;' in cg_players

	assert 'Cvar_Get ("teamtask", "0", CVAR_USERINFO | CVAR_PROTECTED );' in cl_main
	assert 'teamTask = atoi(Info_ValueForKey(userinfo, "teamtask"));' in g_client
	assert 'trap_SendClientCommand( va( "teamtask %d\\n", cgs.acceptTask ) );' in cg_consolecmds


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
	assert 'Cvar_Get ("web_browserActive", "0", CVAR_ROM );' in cl_main
	assert 'Cmd_AddCommand ("web_browserActive", CL_Web_BrowserActive_f );' in cl_main
	assert 'Cvar_Set( "web_browserActive", active ? "1" : "0" );' in cl_cgame
	assert 'browserActive = trap_Cvar_VariableValue( "web_browserActive" );' in cg_draw

	assert 'com_buildScript = Cvar_Get( "com_build", "0", 0 );' in common
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in common
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in cl_main
	assert 'if ( com_buildScript && com_buildScript->integer ) {' in sv_init
	assert '{ &cg_buildScript, "com_build", "0", 0 },' in cg_main
	assert 'if( g_gametype.integer == GT_SINGLE_PLAYER || trap_Cvar_VariableIntegerValue( "com_build" ) ) {' in g_main

	assert 'com_version = Cvar_Get ("version", s, CVAR_ROM | CVAR_SERVERINFO );' in common
	assert 'Info_SetValueForKey( info, "version", com_version->string );' in cl_main
	assert 'trap_Cvar_VariableStringBuffer( "version", str, sizeof(str) );' in g_rankings


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
	assert 'Cvar_VariableIntegerValue( "web_browserActive" ) == 1 || ( com_idleSleep && com_idleSleep->integer == 1 )' in common
	assert 'Com_IdleSleep( minMsec - msec );' in common
	assert 'dueTime.QuadPart = -( (LONGLONG)msec * 10000 );' in common
	assert 'usleep( msec * 1000 );' in common

	assert 'cl_freezeDemo = Cvar_Get ("cl_freezeDemo", "0", CVAR_TEMP );' in cl_main
	assert 'if ( clc.demoplaying && cl_freezeDemo->integer ) {' in cl_cgame
	assert 'freezeDemo = trap_Cvar_VariableValue( "cl_freezeDemo" );' in cg_draw

	assert 'cl_mouseAccelDebug = Cvar_Get ("cl_mouseAccelDebug", "0", 0 );' in cl_main
	assert 'if ( cl_mouseAccelDebug->integer ) {' in cl_input
	assert 'mouse accel: rate %.3f offset %.3f power %.3f accel %.3f sens %.3f cap %.3f\\n' in cl_input

	assert 'Cvar_Get ("dmflags", "0", CVAR_SERVERINFO);' in sv_init
	assert '{ &g_dmflags, "dmflags", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qtrue  },' in g_main
	assert 'cgs.dmflags = atoi( Info_ValueForKey( info, "dmflags" ) );' in cg_servercmds

	assert 'Cvar_Get ("fraglimit", "20", CVAR_SERVERINFO);' in sv_init
	assert '{ &g_fraglimit, "fraglimit", "20", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },' in g_main
	assert 'cgs.fraglimit = atoi( Info_ValueForKey( info, "fraglimit" ) );' in cg_servercmds
	assert 'if ( level.teamScores[TEAM_RED] >= g_fraglimit.integer ) {' in g_main

	assert 'Cvar_Get ("timelimit", "0", CVAR_SERVERINFO);' in sv_init
	assert '{ &g_timelimit, "timelimit", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },' in g_main
	assert 'cgs.timelimit = atoi( Info_ValueForKey( info, "timelimit" ) );' in cg_servercmds
	assert 'if ( g_timelimit.integer && !level.warmupTime ) {' in g_main

	assert 'sv_gametype = Cvar_Get ("g_gametype", "0", CVAR_SERVERINFO | CVAR_LATCH );' in sv_init
	assert '{ &g_gametype, "g_gametype", "0", CVAR_SERVERINFO | CVAR_USERINFO | CVAR_LATCH, 0, qfalse  },' in g_main
	assert 'cgs.gametype = atoi( gametypeValue );' in cg_servercmds
	assert 'trap_Cvar_Set("g_gametype", va("%i", cgs.gametype));' in cg_servercmds


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
	assert 'com_pid = Cvar_Get( "com_pid", Com_CurrentProcessIdString(), CVAR_ROM );' in common
	assert 'pidLength = FS_ReadFile( "profile.pid", (void **)&pidBuffer );' in common
	assert 'if ( com_ignorecrash && com_ignorecrash->integer ) {' in common
	assert 'if ( retainedPid > 0 && com_pid && retainedPid != com_pid->integer ) {' in common
	assert 'Cvar_Set( "com_crashed", "1" );' in common
	assert 'FS_WriteFile( "profile.pid", value, strlen( value ) );' in common
	assert 'Com_WriteProfilePidMarker( com_pid ? com_pid->string : Com_CurrentProcessIdString() );' in common
	assert 'Com_WriteProfilePidMarker( "0" );' in common

	assert 'sv_hostname = Cvar_Get ("sv_hostname", "noname", CVAR_SERVERINFO | CVAR_ARCHIVE );' in sv_init
	assert 'sv_hostname = Cvar_Get ("sv_hostname", defaultHostname, CVAR_SERVERINFO | CVAR_ARCHIVE );' in sv_init
	assert 'QL_Steamworks_ServerSetServerName( sv_hostname->string );' in sv_main
	assert 'Info_SetValueForKey( infostring, "hostname", sv_hostname->string );' in sv_main
	assert 'trap_Cvar_VariableStringBuffer( "sv_hostname", hostname, sizeof( hostname ) );' in g_main

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
	assert 'MSG_WriteShort( &send, qport->integer );' in net_chan
	assert 'port = Cvar_VariableValue ("net_qport");' in cl_main
	assert 'Info_SetValueForKey( info, "qport", va("%i", port ) );' in cl_main
	assert 'Netchan_Setup (NS_CLIENT, &clc.netchan, from, Cvar_VariableValue( "net_qport" ) );' in cl_main

	assert 'ip = Cvar_Get( "net_ip", "localhost", CVAR_LATCH );' in win_net
	assert 'Cvar_VariableStringBuffer( "net_ip", netIp, sizeof( netIp ) );' in common
	assert 'Cvar_VariableStringBuffer( "net_ip", resolvedIp, sizeof( resolvedIp ) );' in sv_zmq

	assert 'netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );' in win_net
	assert 'Cvar_SetValue( "net_port", port + i );' in win_net
	assert 'netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );' in common
	assert 'netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );' in sv_zmq
	assert 's_zmqRconIp = Cvar_Get( "zmq_rcon_ip", "0.0.0.0", CVAR_ARCHIVE );' in sv_zmq
	assert 's_zmqRconPort = Cvar_Get( "zmq_rcon_port", "28960", CVAR_ARCHIVE );' in sv_zmq

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


def test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts() -> None:
	snd_dma = _read_text(SND_DMA)
	snd_mix = _read_text(SND_MIX)
	cg_view = _read_text(CG_VIEW)
	cg_servercmds = _read_text(CG_SERVERCMDS)

	assert 's_announcerVolume = Cvar_GetBounded( "s_announcerVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'if ( entchannel == CHAN_ANNOUNCER && s_announcerVolume ) {' in snd_dma
	assert 'trap_S_StartLocalSound( sfx, CHAN_ANNOUNCER );' in cg_view

	assert 's_doppler = Cvar_Get( "s_doppler", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in snd_dma
	assert 'if (s_doppler->integer && VectorLengthSquared(velocity)>0.0) {' in snd_dma

	assert 'cv = Cvar_Get ("s_initsound", "1", 0);' in snd_dma
	assert 'if ( !cv->integer ) {' in snd_dma
	assert 'Com_Printf ("not initializing.\\n");' in snd_dma

	assert 's_mixahead = Cvar_Get( "s_mixahead", "0.140", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in snd_dma
	assert 'ma = s_mixahead->value * dma.speed;' in snd_dma

	assert 's_mixPreStep = Cvar_Get( "s_mixPreStep", "0.05", CVAR_ARCHIVE | CVAR_PROTECTED );' in snd_dma
	assert 's_paintedtime = s_soundtime + s_mixPreStep->value * dma.speed;' in snd_dma

	assert 's_musicVolume = Cvar_GetBounded( "s_musicvolume", "0.5", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'musicVolume = (musicVolume + (s_musicVolume->value * 2))/4.0f;' in snd_dma

	assert 's_show = Cvar_Get ("s_show", "0", CVAR_CHEAT);' in snd_dma
	assert 'if ( s_show->integer == 1 ) {' in snd_dma
	assert 'if ( s_show->integer == 2 ) {' in snd_dma

	assert 's_testsound = Cvar_Get ("s_testsound", "0", CVAR_CHEAT);' in snd_dma
	assert 'if ( s_testsound->integer ) {' in snd_mix

	assert 's_voiceVolume = Cvar_GetBounded( "s_voiceVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'else if ( entchannel == CHAN_VOICE && s_voiceVolume ) {' in snd_dma
	assert 'trap_S_StartLocalSound( vchat->snd, CHAN_VOICE);' in cg_servercmds

	assert 's_volume = Cvar_GetBounded( "s_volume", "0.8", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 'snd_vol = s_volume->value*255;' in snd_mix
	assert 'ch->master_vol = S_ChannelMasterVolume( entchannel );' in snd_dma


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
	assert 'if ( cl_mouseAccelDebug->integer ) {' in cl_input
	assert 'Com_Printf( "mouse accel: rate %.3f offset %.3f power %.3f accel %.3f sens %.3f cap %.3f\\n",' in cl_input

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

	assert 'r_texturebits = ri.Cvar_Get( "r_texturebits", "32", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'ri.Printf( PRINT_ALL, "texture bits: %d\\n", r_texturebits->integer );' in tr_init

	assert 'r_colorbits = ri.Cvar_Get( "r_colorbits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'dm.dmBitsPerPel = r_colorbits->integer;' in win_glimp

	assert 'r_stencilbits = ri.Cvar_Get( "r_stencilbits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_stencilbits = ri.Cvar_Get( "r_stencilbits", "8", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'stencilbits = r_stencilbits->integer;' in win_glimp

	assert 'r_depthbits = ri.Cvar_Get( "r_depthbits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'depthbits = r_depthbits->integer;' in win_glimp

	assert 'r_mode = ri.Cvar_Get( "r_mode", "3", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'return r_mode->integer;' in tr_init
	assert 'ri.Printf( PRINT_WARNING, "WARNING: invalid r_mode %d, resetting to 3\\n", r_mode->integer );' in tr_init
	assert 'ri.Cvar_Set( "r_mode", "3" );' in tr_init

	assert 'r_fullscreen = ri.Cvar_Get( "r_fullscreen", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_fullscreen = Cvar_Get ("r_fullscreen", "1", CVAR_ARCHIVE | CVAR_LATCH );' in win_wndproc

	assert 'r_windowedMode = ri.Cvar_Get( "r_windowedMode", "12", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'return r_windowedMode->integer;' in tr_init
	assert 'ri.Printf( PRINT_WARNING, "WARNING: invalid r_windowedMode %d, resetting to 12\\n", r_windowedMode->integer );' in tr_init
	assert 'ri.Cvar_Set( "r_windowedMode", "12" );' in tr_init
	assert 'Cvar_SetValue( "r_windowedMode", -1 );' in win_wndproc

	assert 'r_customwidth = ri.Cvar_Get( "r_customwidth", "1600", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert '*width = r_customwidth->integer;' in tr_init
	assert 'ri.Printf( PRINT_WARNING, "WARNING: invalid r_customwidth %d, resetting to 1600\\n", r_customwidth->integer );' in tr_init
	assert 'ri.Cvar_Set( "r_customwidth", "1600" );' in tr_init

	assert 'r_customheight = ri.Cvar_Get( "r_customheight", "1024", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert '*height = r_customheight->integer;' in tr_init
	assert 'ri.Printf( PRINT_WARNING, "WARNING: invalid r_customheight %d, resetting to 1024\\n", r_customheight->integer );' in tr_init
	assert 'ri.Cvar_Set( "r_customheight", "1024" );' in tr_init

	assert 'r_aspectRatio = ri.Cvar_Get( "r_aspectRatio", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_aspectRatio, 0, 3, qtrue );' in tr_init
	assert 'ri.Cvar_Set( "r_aspectRatio", va( "%d", GLW_GetModeAspectRatioPreset( width, height ) ) );' in win_glimp

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
	assert '&& strcmp( Cvar_VariableString("r_glDriver"), _3DFX_DRIVER_NAME) )' in win_input

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

	assert 'r_fastsky = ri.Cvar_Get( "r_fastsky", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );' in tr_init
	assert 'if ( r_noportals->integer || (r_fastsky->integer == 1) ) {' in tr_main
	assert 'if ( r_fastsky->integer ) {' in tr_sky
	assert 'if ( r_fastsky->integer && !( backEnd.refdef.rdflags & RDF_NOWORLDMODEL ) )' in tr_backend

	assert 'r_dynamiclight = ri.Cvar_Get( "r_dynamiclight", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
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

	assert 'r_gamma = ri.Cvar_Get( "r_gamma", "1.2", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'r_gamma = ri.Cvar_Get( "r_gamma", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'ri.Cvar_Set( "r_gamma", "0.5" );' in tr_image
	assert 'gammaRecip = 1.0f / r_gamma->value;' in tr_backend

	assert 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'contrast = r_contrast ? r_contrast->value : 1.0f;' in tr_backend

	assert 'r_railWidth = ri.Cvar_Get( "r_railWidth", "16", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'int\t\tspanWidth = r_railWidth->integer;' in tr_surface

	assert 'r_railCoreWidth = ri.Cvar_Get( "r_railCoreWidth", "6", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'DoRailCore( start, end, right, len, r_railCoreWidth->integer );' in tr_surface

	assert 'r_railSegmentLength = ri.Cvar_Get( "r_railSegmentLength", "32", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'numSegs = ( len ) / r_railSegmentLength->value;' in tr_surface


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
	assert 'overbright = 2.0f * r_overBrightBits->value;' in tr_backend

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

	assert 'r_nocull = ri.Cvar_Get ("r_nocull", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_nocull->integer ) {' in tr_world

	assert 'r_novis = ri.Cvar_Get ("r_novis", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_novis->integer || tr.viewCluster == -1 ) {' in tr_world

	assert 'r_showcluster = ri.Cvar_Get ("r_showcluster", "0", CVAR_CHEAT);' in tr_init
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

	assert 'r_showtris = ri.Cvar_Get ("r_showtris", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_showtris->integer ) {' in tr_shade
	assert 'DrawTris (input);' in tr_shade

	assert 'r_showsky = ri.Cvar_Get ("r_showsky", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_showsky->integer ) {' in tr_sky
	assert 'qglDepthRange( 0.0, 0.0 );' in tr_sky

	assert 'r_shownormals = ri.Cvar_Get ("r_shownormals", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_shownormals->integer ) {' in tr_shade
	assert 'DrawNormals (input);' in tr_shade

	assert 'r_noportals = ri.Cvar_Get ("r_noportals", "0", CVAR_CHEAT);' in tr_init
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

	assert 'r_norefresh = ri.Cvar_Get ("r_norefresh", "0", CVAR_CHEAT);' in tr_init
	assert 'if ( r_norefresh->integer ) {' in tr_scene

	assert 'r_drawentities = ri.Cvar_Get ("r_drawentities", "1", CVAR_CHEAT );' in tr_init
	assert 'if ( !r_drawentities->integer ) {' in tr_main

	assert 'r_nocurves = ri.Cvar_Get ("r_nocurves", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_nocurves->integer ) {' in tr_world
	assert 'return qtrue;' in tr_world

	assert 'r_drawworld = ri.Cvar_Get ("r_drawworld", "1", CVAR_CHEAT );' in tr_init
	assert 'if ( !r_drawworld->integer ) {' in tr_world

	assert 'r_lightmap = ri.Cvar_Get ("r_lightmap", "0", 0 );' in tr_init
	assert 'if ( r_lightmap->integer == 2 )' in tr_bsp
	assert 'if ( r_lightmap->integer ) {' in tr_shade

	assert 'r_nobind = ri.Cvar_Get ("r_nobind", "0", CVAR_CHEAT);' in tr_init
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

	assert 'r_lockpvs = ri.Cvar_Get ("r_lockpvs", "0", CVAR_CHEAT);' in tr_init
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

	assert 'r_directedScale = ri.Cvar_Get( "r_directedScale", "1", CVAR_CHEAT );' in tr_init
	assert 'VectorScale( ent->directedLight, r_directedScale->value, ent->directedLight );' in tr_light

	assert 'r_debugLight = ri.Cvar_Get( "r_debuglight", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_debugLight->integer ) {' in tr_light
	assert 'LogLight( ent );' in tr_light

	assert 'r_debugFontAtlas = ri.Cvar_Get( "r_debugFontAtlas", "0", CVAR_TEMP );' in tr_init
	assert 'if ( r_debugFontAtlas->integer ) {' in tr_backend
	assert 'RB_ShowFontAtlas();' in tr_backend

	assert 'r_debugSort = ri.Cvar_Get( "r_debugSort", "0", CVAR_CHEAT );' in tr_init
	assert 'if ( r_debugSort->integer && r_debugSort->integer < tess.shader->sort ) {' in tr_shade

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

	assert 'r_enablePostProcess = ri.Cvar_Get( "r_enablePostProcess", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
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

	assert 'r_ext_compressed_textures = ri.Cvar_Get( "r_ext_compressed_textures", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_compressed_textures->integer )' in win_glimp

	assert 'r_ext_gamma_control = ri.Cvar_Get( "r_ext_gamma_control", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( !r_ignorehwgamma->integer && r_ext_gamma_control->integer )' in win_glimp

	assert 'r_ext_multitexture = ri.Cvar_Get( "r_ext_multitexture", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_multitexture->integer )' in win_glimp

	assert 'r_ext_compiled_vertex_array = ri.Cvar_Get( "r_ext_compiled_vertex_array", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'if ( r_ext_compiled_vertex_array->integer )' in win_glimp


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

	assert 'r_ambientScale = ri.Cvar_Get( "r_ambientScale", "10", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_ambientScale, 1, 100, qtrue );' in tr_init
	assert 'VectorScale( ent->ambientLight, r_ambientScale->value, ent->ambientLight );' in tr_light

	assert 'r_lodCurveError = ri.Cvar_Get( "r_lodCurveError", "250", CVAR_CHEAT );' in tr_init
	assert 'if ( r_lodCurveError->value < 0 ) {' in tr_surface
	assert 'return r_lodCurveError->value / d;' in tr_surface

	assert 'r_lodbias = ri.Cvar_Get( "r_lodBias", "-2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_lodbias, -2, 2, qtrue );' in tr_init
	assert 'lod += r_lodbias->integer;' in tr_mesh

	assert 'r_lodscale = ri.Cvar_Get( "r_lodScale", "10", CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'AssertCvarRange( r_lodscale, 1, 50, qtrue );' in tr_init
	assert 'lodscale = r_lodscale->value;' in tr_mesh

	assert 'r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
	assert 'r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );' in tr_init
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

	assert 'r_uiFullScreen = ri.Cvar_Get( "r_uiFullScreen", "0", 0);' in tr_init
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
	assert 'if ( !sv_vac || !sv_vac->integer ) {' in sv_client
	assert 'Info_SetValueForKey( infostring, "vac", va("%i", sv_vac->integer) );' in sv_main

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

	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' in tr_init
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
	assert 'RBPP_BindRectangleTexture( 0, s_postProcess.sceneTarget.texture );' in tr_backend
	assert 'RBPP_BindRenderTarget( &s_postProcess.bloomBrightTarget );' in tr_backend
	assert 'RBPP_BindRectangleTexture( 0, s_postProcess.bloomDownsampleTarget.texture );' in tr_backend

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

	assert 'r_picmip = ri.Cvar_Get ("r_picmip", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert 'AssertCvarRange( r_picmip, 0, 16, qtrue );' in tr_init
	assert 'ri.Printf( PRINT_ALL, "picmip: %d\\n", r_picmip->integer );' in tr_init
	assert 'scaled_width >>= r_picmip->integer;' in tr_image
	assert 'scaled_height >>= r_picmip->integer;' in tr_image
	assert 'ri.Cvar_Set( "r_picmip", "2" );' in win_glimp
	assert 'ri.Cvar_Set( "r_picmip", "1" );' in win_glimp


def test_engine_cvar_thirtythird_server_botlib_tranche_matches_retail_contracts() -> None:
	sv_bot = _read_text(REPO_ROOT / "src" / "code" / "server" / "sv_bot.c")
	be_interface = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c")
	be_aas_main = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c")
	be_aas_reach = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_aas_reach.c")
	be_ai_char = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_ai_char.c")
	be_ai_chat = _read_text(REPO_ROOT / "src" / "code" / "botlib" / "be_ai_chat.c")

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
