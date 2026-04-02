/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
//
/*
=======================================================================

USER INTERFACE MAIN

=======================================================================
*/

// use this to get a demo build without an explicit demo build, i.e. to get the demo ui files to build
//#define PRE_RELEASE_TADEMO

#include "ui_local.h"
#include "../../common/platform/platform_config.h"
#include <stdint.h>
#include <stdlib.h>

uiInfo_t uiInfo;

#if QL_PLATFORM_HAS_ONLINE_SERVICES
#define UI_BROWSER_AWESOMIUM_DEFAULT "1"
#else
#define UI_BROWSER_AWESOMIUM_DEFAULT "0"
#endif

static const char *MonthAbbrev[] = {
	"Jan","Feb","Mar",
	"Apr","May","Jun",
	"Jul","Aug","Sep",
	"Oct","Nov","Dec"
};


static const char *skillLevels[] = {
  "I Can Win",
  "Bring It On",
  "Hurt Me Plenty",
  "Hardcore",
  "Nightmare"
};

static const int numSkillLevels = sizeof(skillLevels) / sizeof(const char*);


static const char *netSources[] = {
	"Local",
	"Mplayer",
	"Internet",
	"Favorites"
};
static const int numNetSources = sizeof(netSources) / sizeof(const char*);

static const serverFilter_t serverFilters[] = {
	{"All", "" },
	{"Quake 3 Arena", "" },
	{"Team Arena", "missionpack" },
	{"Rocket Arena", "arena" },
	{"Alliance", "alliance20" },
	{"Weapons Factory Arena", "wfa" },
	{"OSP", "osp" },
};

static const char *teamArenaGameTypes[] = {
	"FFA",
	"TOURNAMENT",
	"SP",
	"TEAM DM",
	"CTF",
	"1FCTF",
	"OVERLOAD",
	"HARVESTER",
	"TEAMTOURNAMENT"
};

static int const numTeamArenaGameTypes = sizeof(teamArenaGameTypes) / sizeof(const char*);


static const char *teamArenaGameNames[] = {
	"Free For All",
	"Tournament",
	"Single Player",
	"Team Deathmatch",
	"Capture the Flag",
	"One Flag CTF",
	"Overload",
	"Harvester",
	"Team Tournament",
};

static int const numTeamArenaGameNames = sizeof(teamArenaGameNames) / sizeof(const char*);


static const int numServerFilters = sizeof(serverFilters) / sizeof(serverFilter_t);

static const char *sortKeys[] = {
	"Server Name",
	"Map Name",
	"Open Player Spots",
	"Game Type",
	"Ping Time"
};
static const int numSortKeys = sizeof(sortKeys) / sizeof(const char*);

static char* netnames[] = {
	"???",
	"UDP",
	"IPX",
	NULL
};


static int gamecodetoui[] = {4,2,3,0,5,1,6};
static int uitogamecode[] = {4,6,2,3,1,5,7};


static void UI_StartServerRefresh(qboolean full);
void UI_StopServerRefresh( void );
static void UI_DoServerRefresh( void );
static void UI_FeederSelection(float feederID, int index);
static void UI_BuildServerDisplayList(qboolean force);
static void UI_BuildServerStatus(qboolean force);
static void UI_BuildFindPlayerList(qboolean force);
static int QDECL UI_ServersQsortCompare( const void *arg1, const void *arg2 );
static int UI_MapCountByGameType(qboolean singlePlayer);
static int UI_HeadCountByTeam( void );
static void UI_GetTeamColor(vec4_t *color);
static void UI_ParseGameInfo(const char *teamFile);
static void UI_ParseTeamInfo(const char *teamFile);
static void UI_LoadCountries(void);
	static const char *UI_SelectedMap(int index, int *actual);
	static const char *UI_SelectedHead(int index, int *actual);
	static int UI_GetIndexFromSelection(int actual);
	static const char *UI_GetCallvoteGametypeToken(int gametype);
	static int UI_GetCallvoteRotationGametype(const mapRotationInfo_t *rotation);
	static int UI_CVMapCountByGameType(void);
	static void UI_SelectCallvoteMap(int index);
	static void UI_SetCurrentNetMap(int mapIndex);
	int Text_Width(const char *text, float scale, int limit);
	void Text_Paint(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style);
	void _UI_Init( qboolean inGameLoad );
	void _UI_Shutdown( void );
	void UI_LoadNonIngame( void );

	int ProcessNewUI( int command, int arg0, int arg1, int arg2, int arg3, int arg4, int arg5, int arg6 );

	/*
	================
	vmMain

	This is the only way control passes into the module.
	This must be the very first function compiled into the .qvm file
	================
	*/
	vmCvar_t  ui_new;
	vmCvar_t  ui_debug;
	vmCvar_t  ui_initialized;
	vmCvar_t  ui_teamArenaFirstRun;
	vmCvar_t  ui_menuFlow;
	vmCvar_t  ui_browserAwesomium;
	extern vmCvar_t ui_cvGameType;

	static uiMenuFlow_t ui_activeMenuFlow = UI_MENU_FLOW_QUAKELIVE;
	static qboolean ui_browserActiveKnown = qfalse;
	static qboolean ui_browserActiveState = qfalse;
	static const char *ui_browserRefreshCommand = "web_stopRefresh\n";

	/*
	=============
	UI_StringRepresentsTrue

	Returns qtrue when a text value should be interpreted as enabled.
	=============
	*/
	static qboolean UI_StringRepresentsTrue(const char *value) {
		if (!value || !value[0]) {
			return qfalse;
		}

		if (value[0] == '0' && value[1] == '\0') {
			return qfalse;
		}

		if (!Q_stricmp(value, "false") || !Q_stricmp(value, "no") || !Q_stricmp(value, "off")) {
			return qfalse;
		}

		return qtrue;
	}

	/*
	=============
	UI_ExternalEcosystemsDisabled

	Checks environment toggles that force external browser integration off.
	=============
	*/
	static qboolean UI_ExternalEcosystemsDisabled(void) {
		const char *value;

		value = getenv("QL_DISABLE_EXTERNAL_ECOSYSTEMS");
		if (UI_StringRepresentsTrue(value)) {
			return qtrue;
		}

		value = getenv("QL_DISABLE_AWESOMIUM");
		if (UI_StringRepresentsTrue(value)) {
			return qtrue;
		}

		value = getenv("QL_DISABLE_STEAMWORKS");
		return UI_StringRepresentsTrue(value);
	}

	/*
	=============
	UI_MenuFileEquals
	=============
	*/
	static qboolean UI_MenuFileEquals(const char *lhs, const char *rhs) {
        return (lhs && rhs) ? (Q_stricmp(lhs, rhs) == 0) : qfalse;
}

/*
=============
UI_UpdateForceModelSettings

Synchronizes the UI force model cvars with the current force model and skin
state, while refreshing the head feeder selection.
=============
*/
static void UI_UpdateForceModelSettings(qboolean team) {
	char model[MAX_QPATH];
	const char *modelCvar;
	const char *skinCvar;
	const char *uiModelCvar;
	const char *uiSkinCvar;
	const char *uiBrightCvar;
	const char *modelValue;
	char *slash;

	modelCvar = team ? "cg_teamModel" : "cg_enemyModel";
	skinCvar = team ? "cg_forceTeamSkin" : "cg_forceEnemySkin";
	uiModelCvar = team ? "ui_teamModel" : "ui_enemyModel";
	uiSkinCvar = team ? "ui_forceTeamSkin" : "ui_forceEnemySkin";
	uiBrightCvar = team ? "ui_teamModelBright" : "ui_enemyModelBright";

	trap_Cvar_VariableStringBuffer(modelCvar, model, sizeof(model));
	slash = strchr(model, '/');
	trap_Cvar_Set(uiBrightCvar, (slash && Q_stricmp(slash + 1, "bright") == 0) ? "1" : "0");
	if (slash) {
		*slash = '\0';
	}
	modelValue = (model[0]) ? model : "No";
	trap_Cvar_Set(uiModelCvar, modelValue);
	trap_Cvar_Set(uiSkinCvar, UI_Cvar_VariableString(skinCvar));
	UI_FeederSelection(FEEDER_HEADS, 0);
	Menu_SetFeederSelection(NULL, FEEDER_HEADS, 0, NULL);
}

/*
=============
UI_MenuFileExists

Check whether a menu definition file can be opened via the virtual FS.
=============
*/
static qboolean UI_MenuFileExists(const char *menuFile) {
	fileHandle_t handle;
	int length;

	if (!menuFile || !*menuFile) {
		return qfalse;
	}

	length = trap_FS_FOpenFile(menuFile, &handle, FS_READ);
	if (length > 0) {
		trap_FS_FCloseFile(handle);
		return qtrue;
	}

	return qfalse;
}

/*
=============
UI_BrowserOverlayAvailable

Check whether the Awesomium overlay is enabled.
=============
*/
qboolean UI_BrowserOverlayAvailable(void) {
	if (UI_ExternalEcosystemsDisabled()) {
		return qfalse;
	}

	return ui_browserAwesomium.integer != 0;
}

/*
=============
UI_ResolveMenuFlowInternal

Resolve which menu flow should be active, preferring the browser overlay and
falling back to bridge scripts when the overlay is unavailable.
=============
*/
static uiMenuFlow_t UI_ResolveMenuFlowInternal(void) {
	if (UI_BrowserOverlayAvailable()) {
		return UI_MENU_FLOW_QUAKELIVE;
	}

	if (UI_BrowserBridgeAvailable()) {
		return UI_MENU_FLOW_BRIDGED;
	}

	return UI_MENU_FLOW_QUAKELIVE;
}

/*
=============
UI_SetBrowserActive

Inform the engine overlay about whether the Awesomium-driven UI is active.
=============
*/
static void UI_SetBrowserActive(qboolean active) {
	if (ui_browserActiveKnown && ui_browserActiveState == active) {
		return;
	}

	ui_browserActiveState = active;
	ui_browserActiveKnown = qtrue;
	trap_Cmd_ExecuteText(EXEC_NOW, active ? "web_browserActive 1\n" : "web_browserActive 0\n");
}

/*
=============
UI_SetActiveMenuFlow

Apply the resolved menu flow selection to runtime state.
=============
*/
static void UI_SetActiveMenuFlow(uiMenuFlow_t flow) {
	ui_activeMenuFlow = flow;
	ui_new.integer = (flow != UI_MENU_FLOW_LEGACY);
	UI_SetBrowserActive(flow == UI_MENU_FLOW_QUAKELIVE);
	UI_BrowserBridge_SetActive(flow == UI_MENU_FLOW_BRIDGED);
}

/*
=============
UI_ServerBrowserEnabled

Determine if the native server browser should remain enabled.
=============
*/
static qboolean UI_ServerBrowserEnabled(void) {
	return (ui_activeMenuFlow == UI_MENU_FLOW_BRIDGED);
}

/*
=============
UI_UpdateActiveMenuFlowForFile

Update the active menu flow based on which menu file set is being loaded.
=============
*/
static void UI_UpdateActiveMenuFlowForFile(const char *menuFile) {
	if (UI_MenuFileEquals(menuFile, UI_MENU_FILE_QUAKELIVE) || UI_MenuFileEquals(menuFile, UI_INGAME_FILE_QUAKELIVE)) {
		UI_SetActiveMenuFlow(UI_MENU_FLOW_QUAKELIVE);
	} else if (UI_MenuFileEquals(menuFile, UI_MENU_FILE_QUAKELIVE_BRIDGE) || UI_MenuFileEquals(menuFile, UI_INGAME_FILE_QUAKELIVE_BRIDGE)) {
		UI_SetActiveMenuFlow(UI_MENU_FLOW_BRIDGED);
	}
}

/*
=============
UI_DefaultMenuFile

Resolve the root menu definition file, preferring Quake Live scripts.
=============
*/
const char *UI_DefaultMenuFile(void) {
	const char *menuFile;

	menuFile = (ui_activeMenuFlow == UI_MENU_FLOW_LEGACY) ? UI_MENU_FILE_LEGACY : UI_MENU_FILE_QUAKELIVE;
	if (ui_activeMenuFlow == UI_MENU_FLOW_BRIDGED) {
		menuFile = UI_MENU_FILE_QUAKELIVE_BRIDGE;
	}

	return (UI_MenuFileExists(menuFile)) ? menuFile : UI_MENU_FILE_QUAKELIVE;
}

/*
=============
UI_DefaultIngameFile

Resolve the in-game menu definition file, preferring Quake Live scripts.
=============
*/
const char *UI_DefaultIngameFile(void) {
	const char *menuFile;

	menuFile = (ui_activeMenuFlow == UI_MENU_FLOW_LEGACY) ? UI_INGAME_FILE_LEGACY : UI_INGAME_FILE_QUAKELIVE;
	if (ui_activeMenuFlow == UI_MENU_FLOW_BRIDGED) {
		menuFile = UI_INGAME_FILE_QUAKELIVE_BRIDGE;
	}

	return (UI_MenuFileExists(menuFile)) ? menuFile : UI_INGAME_FILE_QUAKELIVE;
}

/*
=============
UI_UpdateActiveMenuFlow

Refresh the menu flow state from the current runtime configuration.
=============
*/
static void UI_UpdateActiveMenuFlow(void) {
	UI_SetActiveMenuFlow(UI_ResolveMenuFlowInternal());
}

/*
=============
UI_ApplyMenuFlowChange

Apply a menu flow change and optionally reload the UI to pick up new defaults.
=============
*/
void UI_ApplyMenuFlowChange(uiMenuFlow_t flow, qboolean reload) {
	trap_Cvar_SetValue("ui_menuFlow", flow);
	UI_UpdateActiveMenuFlow();
	if (reload) {
		UI_Load();
	}
}

/*
=============
UI_RefreshDisplayContextScale

Refreshes the retail-compatible 640x480 scale state from the current renderer config.
=============
*/
static int UI_RefreshDisplayContextScale(void) {
	trap_GetGlconfig(&uiInfo.uiDC.glconfig);

	uiInfo.uiDC.yscale = uiInfo.uiDC.glconfig.vidHeight * (1.0f / 480.0f);
	uiInfo.uiDC.xscale = uiInfo.uiDC.glconfig.vidWidth * (1.0f / 640.0f);
	if (uiInfo.uiDC.glconfig.vidWidth * SCREEN_HEIGHT > uiInfo.uiDC.glconfig.vidHeight * SCREEN_WIDTH) {
		uiInfo.uiDC.bias = 0.5f * (uiInfo.uiDC.glconfig.vidWidth - (uiInfo.uiDC.glconfig.vidHeight * (640.0f / 480.0f)));
	} else {
		uiInfo.uiDC.bias = 0.0f;
	}

	return uiInfo.uiDC.glconfig.vidWidth * SCREEN_HEIGHT;
}

/*
=============
UI_RefreshDisplayContext

Refreshes the UI display context scale state and republishes the active display context.
=============
*/
static int UI_RefreshDisplayContext(void) {
	int result = UI_RefreshDisplayContextScale();

	Init_Display(&uiInfo.uiDC);
	return result;
}

/*
=============
UI_ForEachArenaName

Visits each loaded arena display name for native host consumers.
=============
*/
static void UI_ForEachArenaName(uiArenaNameCallback_t callback) {
	int i;

	if (!callback) {
		return;
	}

	if (uiInfo.mapCount < 1) {
		UI_LoadArenas();
	}

	for (i = 0; i < uiInfo.mapCount; i++) {
		if (uiInfo.mapList[i].mapName) {
			callback(uiInfo.mapList[i].mapName);
		}
	}
}

/*
=============
UI_DrawAdvertisementWaitScreen

Paints the optional named menu and the retail advertisement wait prompts.
=============
*/
static void UI_DrawAdvertisementWaitScreen(const char *menuName) {
	static const char *waitingText = "Waiting on Advertisement";
	static const char *cancelText = "Press ESC to cancel";
	menuDef_t *menu;
	float scale;
	float x;

	if (menuName && menuName[0]) {
		menu = Menus_FindByName(menuName);
		if (menu) {
			Menu_Paint(menu, qtrue);
		}
	}

	scale = 0.5f;

	x = 320.0f - (Text_Width(waitingText, scale, 0) * 0.5f);
	Text_Paint(x, 178.0f, scale, colorWhite, waitingText, 0.0f, 0, 0);

	x = 320.0f - (Text_Width(cancelText, scale, 0) * 0.5f);
	Text_Paint(x, 440.0f, scale, colorWhite, cancelText, 0.0f, 0, 0);
}

/*
=============
UI_InitAdvertisementBridge

Initialises the retail advertisement bridge when a host implementation exists.
=============
*/
static void UI_InitAdvertisementBridge(void) {
#ifndef Q3_VM
	trap_QL_InitAdvertisementBridge();
#endif
}

/*
=============
UI_SetupAdvertCellShader

Provides the retail advert-cell setup callback with a default-content fallback.
=============
*/
static qhandle_t UI_SetupAdvertCellShader(const char *defaultContent, const rectDef_t *rect, int cellId) {
#ifndef Q3_VM
	qhandle_t shader = trap_QL_SetupAdvertCellShader( defaultContent, rect, cellId );

	if ( shader ) {
		return shader;
	}
#endif

	(void)rect;
	(void)cellId;

	if (!defaultContent || !defaultContent[0]) {
		return 0;
	}

	return trap_R_RegisterShaderNoMip(defaultContent);
}

/*
=============
UI_RefreshAdvertCellShader

Provides the retail advert-cell refresh callback with a default-content fallback.
=============
*/
static qhandle_t UI_RefreshAdvertCellShader(const char *defaultContent, const rectDef_t *rect, int cellId) {
#ifndef Q3_VM
	qhandle_t shader = trap_QL_RefreshAdvertCellShader( defaultContent, rect, cellId );

	if ( shader ) {
		return shader;
	}
#endif

	(void)rect;
	(void)cellId;

	if (!defaultContent || !defaultContent[0]) {
		return 0;
	}

	return trap_R_RegisterShaderNoMip(defaultContent);
}

/*
=============
UI_ActivateAdvert

Handles the retail activateAdvert script command when no external bridge is present.
=============
*/
static void UI_ActivateAdvert(int cellId) {
#ifndef Q3_VM
	trap_QL_ActivateAdvert( cellId );
#else
	(void)cellId;
#endif
}

void _UI_KeyEvent( int key, qboolean down );
void _UI_MouseEvent( int dx, int dy );
void _UI_Refresh( int realtime );
qboolean _UI_IsFullscreen( void );
void _UI_SetActiveMenu( uiMenuCommand_t menu );
void UI_Load( void );

/*
================
UI_NativeInit
================
*/
static void UI_NativeInit( qboolean inGameLoad ) {
	_UI_Init( inGameLoad );
}

/*
================
UI_NativeKeyEvent
================
*/
static void UI_NativeKeyEvent( int key, qboolean down, int time ) {
	(void)time;
	_UI_KeyEvent( key, down );
}

/*
================
UI_NativeDrawConnectScreen
================
*/
static void UI_NativeDrawConnectScreen( qboolean overlay ) {
	UI_DrawConnectScreen( overlay );
}

int vmMain( int command, int arg0, int arg1, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8, int arg9, int arg10, int arg11  ) {
	switch ( command ) {
	case UI_GETAPIVERSION:
		return UI_QL_API_VERSION;

	case UI_INIT:
		UI_NativeInit( arg0 ? qtrue : qfalse );
		return 0;

	case UI_SHUTDOWN:
		_UI_Shutdown();
		return 0;

	case UI_KEY_EVENT:
		UI_NativeKeyEvent( arg0, arg1 ? qtrue : qfalse, arg2 );
		return 0;

	case UI_MOUSE_EVENT:
		_UI_MouseEvent( arg0, arg1 );
		return 0;

	case UI_REFRESH:
		_UI_Refresh( arg0 );
		return 0;

	case UI_IS_FULLSCREEN:
		return _UI_IsFullscreen();

	case UI_SET_ACTIVE_MENU:
		_UI_SetActiveMenu( arg0 );
		return 0;

	case UI_CONSOLE_COMMAND:
		return UI_ConsoleCommand(arg0);

	case UI_DRAW_CONNECT_SCREEN:
		UI_NativeDrawConnectScreen( arg0 ? qtrue : qfalse );
		return 0;
	case UI_HASUNIQUECDKEY: // mod authors need to observe this
		return qtrue; // bk010117 - change this to qfalse for mods!
	case UI_REFRESH_DISPLAY_CONTEXT:
		return UI_RefreshDisplayContext();
	case UI_MENUS_ANY_VISIBLE:
		return Menus_AnyVisible();
	case UI_FOR_EACH_ARENA_NAME:
		UI_ForEachArenaName((uiArenaNameCallback_t)(intptr_t)arg0);
		return 0;
	case UI_DRAW_ADVERTISEMENT_WAIT_SCREEN:
		UI_DrawAdvertisementWaitScreen((const char *)(intptr_t)arg0);
		return 0;
}

	return -1;
}

/*
================
UI_NativeHasUniqueCDKey
================
*/
static qboolean UI_NativeHasUniqueCDKey( void ) {
	return qtrue;
}

static void *ui_nativeExports[UI_NATIVE_EXPORT_COUNT] = {
	[UI_NATIVE_EXPORT_INIT] = UI_NativeInit,
	[UI_NATIVE_EXPORT_SHUTDOWN] = _UI_Shutdown,
	[UI_NATIVE_EXPORT_KEY_EVENT] = UI_NativeKeyEvent,
	[UI_NATIVE_EXPORT_MOUSE_EVENT] = _UI_MouseEvent,
	[UI_NATIVE_EXPORT_REFRESH] = _UI_Refresh,
	[UI_NATIVE_EXPORT_IS_FULLSCREEN] = _UI_IsFullscreen,
	[UI_NATIVE_EXPORT_SET_ACTIVE_MENU] = _UI_SetActiveMenu,
	[UI_NATIVE_EXPORT_CONSOLE_COMMAND] = UI_ConsoleCommand,
	[UI_NATIVE_EXPORT_DRAW_CONNECT_SCREEN] = UI_NativeDrawConnectScreen,
	[UI_NATIVE_EXPORT_HAS_UNIQUE_CD_KEY] = UI_NativeHasUniqueCDKey,
	[UI_NATIVE_EXPORT_REFRESH_DISPLAY_CONTEXT] = UI_RefreshDisplayContext,
	[UI_NATIVE_EXPORT_MENUS_ANY_VISIBLE] = Menus_AnyVisible,
	[UI_NATIVE_EXPORT_FOR_EACH_ARENA_NAME] = UI_ForEachArenaName,
	[UI_NATIVE_EXPORT_DRAW_ADVERTISEMENT_WAIT_SCREEN] = UI_DrawAdvertisementWaitScreen
};

/*
================
UI_GetNativeExportTable
================
*/
void **UI_GetNativeExportTable( void ) {
	return ui_nativeExports;
}

static const char *const uiQLTextureNames[] = {
	"ui/assets/3_cursor3",
	"ui/assets/backscreen_smoke",
	"ui/assets/bluechip.tga",
	"ui/assets/button_back.tga",
	"ui/assets/fadebox.tga",
	"ui/assets/framebutton.tga",
	"ui/assets/gradientbar2.tga",
	"ui/assets/hud/a100.tga",
	"ui/assets/hud/a100line.tga",
	"ui/assets/hud/a200.tga",
	"ui/assets/hud/a200line.tga",
	"ui/assets/hud/armor.tga",
	"ui/assets/hud/bteambgl.tga",
	"ui/assets/hud/bteambgr.tga",
	"ui/assets/hud/chatl.tga",
	"ui/assets/hud/chatm.tga",
	"ui/assets/hud/chatr.tga",
	"ui/assets/hud/ctf.tga",
	"ui/assets/hud/dm.tga",
	"ui/assets/hud/flag",
	"ui/assets/hud/h100.tga",
	"ui/assets/hud/h100line.tga",
	"ui/assets/hud/h200.tga",
	"ui/assets/hud/h200line.tga",
	"ui/assets/hud/health.tga",
	"ui/assets/hud/healthalert",
	"ui/assets/hud/roundbox.tga",
	"ui/assets/hud/rteambgl.tga",
	"ui/assets/hud/rteambgr.tga",
	"ui/assets/hud/scoreboxl.tga",
	"ui/assets/hud/scoreboxl2.tga",
	"ui/assets/hud/scoreboxl2a.tga",
	"ui/assets/hud/scoreboxm.tga",
	"ui/assets/hud/scoreboxm2.tga",
	"ui/assets/hud/scoreboxr.tga",
	"ui/assets/hud/scoreboxr2.tga",
	"ui/assets/hud/shadowl.tga",
	"ui/assets/hud/shadowr.tga",
	"ui/assets/hud/tdm.tga",
	"ui/assets/hud/teamonl.tga",
	"ui/assets/hud/teamonm.tga",
	"ui/assets/hud/teamonr.tga",
	"ui/assets/hud/tourn.tga",
	"ui/assets/hud/weaplit2.tga",
	"ui/assets/leftbutton.tga",
	"ui/assets/main_menu/content_background.tga",
	"ui/assets/main_menu/header.tga",
	"ui/assets/main_menu/hmg.tga",
	"ui/assets/main_menu/lg.tga",
	"ui/assets/main_menu/pg.tga",
	"ui/assets/main_menu/ql_logo.tga",
	"ui/assets/main_menu/rg.tga",
	"ui/assets/main_menu/rl.tga",
	"ui/assets/main_menu/sg.tga",
	"ui/assets/medal_accuracy.tga",
	"ui/assets/medal_assist.tga",
	"ui/assets/medal_capture.tga",
	"ui/assets/medal_defend.tga",
	"ui/assets/medal_excellent.tga",
	"ui/assets/medal_gauntlet.tga",
	"ui/assets/medal_impressive.tga",
	"ui/assets/menu/boxb.tga",
	"ui/assets/menu/boxbl.tga",
	"ui/assets/menu/boxbr.tga",
	"ui/assets/menu/boxt.tga",
	"ui/assets/menu/boxtl.tga",
	"ui/assets/menu/boxtr.tga",
	"ui/assets/menu/centerbg_fade.tga",
	"ui/assets/menu/fade.tga",
	"ui/assets/redchip.tga",
	"ui/assets/rightbutton.tga",
	"ui/assets/score/adbr.tga",
	"ui/assets/score/adtl.tga",
	"ui/assets/score/adtm.tga",
	"ui/assets/score/adtr.tga",
	"ui/assets/score/arrow.tga",
	"ui/assets/score/arrowgray.tga",
	"ui/assets/score/bg_tabmenu.tga",
	"ui/assets/score/bgfill.tga",
	"ui/assets/score/bgfill_blue.tga",
	"ui/assets/score/bgfill_red.tga",
	"ui/assets/score/blue_team_player_bar.tga",
	"ui/assets/score/btn.tga",
	"ui/assets/score/ca_score_blu.tga",
	"ui/assets/score/ca_score_red.tga",
	"ui/assets/score/dom_score_blu.tga",
	"ui/assets/score/dom_score_red.tga",
	"ui/assets/score/flagb.tga",
	"ui/assets/score/flagr.tga",
	"ui/assets/score/frame_bl.tga",
	"ui/assets/score/frame_bottom.tga",
	"ui/assets/score/frame_br.tga",
	"ui/assets/score/frame_left.tga",
	"ui/assets/score/frame_mid.tga",
	"ui/assets/score/frame_right.tga",
	"ui/assets/score/frameb.tga",
	"ui/assets/score/framebl.tga",
	"ui/assets/score/framebr.tga",
	"ui/assets/score/framel.tga",
	"ui/assets/score/framem.tga",
	"ui/assets/score/framer.tga",
	"ui/assets/score/framet.tga",
	"ui/assets/score/frametl.tga",
	"ui/assets/score/frametr.tga",
	"ui/assets/score/gradientbar2.tga",
	"ui/assets/score/gtbox.tga",
	"ui/assets/score/ink_fade_left.tga",
	"ui/assets/score/ink_fade_right.tga",
	"ui/assets/score/logo2.tga",
	"ui/assets/score/medal_assist_sm.tga",
	"ui/assets/score/medal_capture_sm.tga",
	"ui/assets/score/medal_defend_sm.tga",
	"ui/assets/score/navbarl.tga",
	"ui/assets/score/navbarm.tga",
	"ui/assets/score/navbarr.tga",
	"ui/assets/score/navfriends.tga",
	"ui/assets/score/navleft.tga",
	"ui/assets/score/navright.tga",
	"ui/assets/score/not_ready.tga",
	"ui/assets/score/ping.tga",
	"ui/assets/score/red_team_player_bar.tga",
	"ui/assets/score/rr_remaining_enemy.tga",
	"ui/assets/score/rr_remaining_team.tga",
	"ui/assets/score/sb_borderangle.tga",
	"ui/assets/score/sb_borderend.tga",
	"ui/assets/score/sb_borderline.tga",
	"ui/assets/score/sb_borderstart.tga",
	"ui/assets/score/scoreb.tga",
	"ui/assets/score/scorebl.tga",
	"ui/assets/score/scorebox.tga",
	"ui/assets/score/scorebox_blue.tga",
	"ui/assets/score/scorebox_follow.tga",
	"ui/assets/score/scorebox_red.tga",
	"ui/assets/score/scorebox_spec.tga",
	"ui/assets/score/scorebr.tga",
	"ui/assets/score/scorel.tga",
	"ui/assets/score/scorem.tga",
	"ui/assets/score/scorer.tga",
	"ui/assets/score/scoretl.tga",
	"ui/assets/score/scoretl2.tga",
	"ui/assets/score/scoretl2_blue.tga",
	"ui/assets/score/scoretl2_red.tga",
	"ui/assets/score/scoretl3.tga",
	"ui/assets/score/scoretl_blue.tga",
	"ui/assets/score/scoretl_red.tga",
	"ui/assets/score/scoretm.tga",
	"ui/assets/score/scoretm3.tga",
	"ui/assets/score/scoretr.tga",
	"ui/assets/score/scoretr3.tga",
	"ui/assets/score/specl.tga",
	"ui/assets/score/specm.tga",
	"ui/assets/score/specr.tga",
	"ui/assets/score/statsfilll.tga",
	"ui/assets/score/statsfillm.tga",
	"ui/assets/score/statsfillr.tga",
	"ui/assets/score/statsl.tga",
	"ui/assets/score/statsm.tga",
	"ui/assets/score/statsr.tga",
	"ui/assets/score/votecast_backlit.tga"
};

static void UI_RegisterQLMenuAssets( void ) {
	int i;
	int count = sizeof( uiQLTextureNames ) / sizeof( uiQLTextureNames[0] );

	for ( i = 0; i < count; i++ ) {
		trap_R_RegisterShaderNoMip( uiQLTextureNames[i] );
	}
		}

/*
=============
AssetCache

Registers fonts, shaders, and shared UI textures for the frontend.
=============
*/
void AssetCache() {
	int n;

	if ( !uiInfo.uiDC.Assets.fontRegistered ) {
		trap_R_RegisterFont( QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE, &uiInfo.uiDC.Assets.textFont );
		trap_R_RegisterFont( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &uiInfo.uiDC.Assets.smallFont );
		trap_R_RegisterFont( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &uiInfo.uiDC.Assets.bigFont );
		uiInfo.uiDC.Assets.fontRegistered = qtrue;
	}
	//if (Assets.textFont == NULL) {
	//}
	//Assets.background = trap_R_RegisterShaderNoMip( ASSET_BACKGROUND );
	//Com_Printf("Menu Size: %i bytes\n", sizeof(Menus));
	uiInfo.uiDC.Assets.gradientBar = trap_R_RegisterShaderNoMip( ASSET_GRADIENTBAR );
	uiInfo.uiDC.Assets.fxBasePic = trap_R_RegisterShaderNoMip( ART_FX_BASE );
	uiInfo.uiDC.Assets.fxPic[0] = trap_R_RegisterShaderNoMip( ART_FX_RED );
	uiInfo.uiDC.Assets.fxPic[1] = trap_R_RegisterShaderNoMip( ART_FX_YELLOW );
	uiInfo.uiDC.Assets.fxPic[2] = trap_R_RegisterShaderNoMip( ART_FX_GREEN );
	uiInfo.uiDC.Assets.fxPic[3] = trap_R_RegisterShaderNoMip( ART_FX_TEAL );
	uiInfo.uiDC.Assets.fxPic[4] = trap_R_RegisterShaderNoMip( ART_FX_BLUE );
	uiInfo.uiDC.Assets.fxPic[5] = trap_R_RegisterShaderNoMip( ART_FX_CYAN );
	uiInfo.uiDC.Assets.fxPic[6] = trap_R_RegisterShaderNoMip( ART_FX_WHITE );
	uiInfo.uiDC.Assets.scrollBar = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR );
	uiInfo.uiDC.Assets.scrollBarArrowDown = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWDOWN );
	uiInfo.uiDC.Assets.scrollBarArrowUp = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWUP );
	uiInfo.uiDC.Assets.scrollBarArrowLeft = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWLEFT );
	uiInfo.uiDC.Assets.scrollBarArrowRight = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWRIGHT );
	uiInfo.uiDC.Assets.scrollBarThumb = trap_R_RegisterShaderNoMip( ASSET_SCROLL_THUMB );
	uiInfo.uiDC.Assets.sliderBar = trap_R_RegisterShaderNoMip( ASSET_SLIDER_BAR );
	uiInfo.uiDC.Assets.sliderThumb = trap_R_RegisterShaderNoMip( ASSET_SLIDER_THUMB );

	for( n = 0; n < NUM_CROSSHAIRS; n++ ) {
		uiInfo.uiDC.Assets.crosshairShader[n] = trap_R_RegisterShaderNoMip( va("gfx/2d/crosshair%c", 'a' + n ) );
	}

	UI_RegisterQLMenuAssets();

	uiInfo.newHighScoreSound = trap_S_RegisterSound("sound/feedback/voc_newhighscore.wav", qfalse);
		}

void _UI_DrawSides(float x, float y, float w, float h, float size) {
	UI_AdjustFrom640( &x, &y, &w, &h );
	size *= uiInfo.uiDC.xscale;
	trap_R_DrawStretchPic( x, y, size, h, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
	trap_R_DrawStretchPic( x + w - size, y, size, h, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
		}

void _UI_DrawTopBottom(float x, float y, float w, float h, float size) {
	UI_AdjustFrom640( &x, &y, &w, &h );
	size *= uiInfo.uiDC.yscale;
	trap_R_DrawStretchPic( x, y, w, size, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
	trap_R_DrawStretchPic( x, y + h - size, w, size, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
		}
/*
================
UI_DrawRect

Coordinates are 640*480 virtual values
=================
*/
void _UI_DrawRect( float x, float y, float width, float height, float size, const float *color ) {
	trap_R_SetColor( color );

  _UI_DrawTopBottom(x, y, width, height, size);
  _UI_DrawSides(x, y, width, height, size);

	trap_R_SetColor( NULL );
		}

/*
=================
UI_SelectTextFont

Uses the retail per-item font bucket when present and otherwise preserves the
legacy scale-driven font selection used by the existing UI code.
=================
*/
static fontInfo_t *UI_SelectTextFont(float scale, int fontIndex) {
	if (fontIndex != ITEM_FONT_INHERIT) {
		switch (fontIndex) {
			case FONT_DEFAULT:
				return &uiInfo.uiDC.Assets.textFont;

			case FONT_SANS:
			case FONT_MONO:
				return &uiInfo.uiDC.Assets.smallFont;
		}
	}

	if (scale <= ui_smallFont.value) {
		return &uiInfo.uiDC.Assets.smallFont;
	}

	if (scale >= ui_bigFont.value) {
		return &uiInfo.uiDC.Assets.bigFont;
	}

	return &uiInfo.uiDC.Assets.textFont;
}

/*
=================
Text_WidthExt
=================
*/
static int Text_WidthExt(const char *text, float scale, int limit, int fontIndex) {
	int count, len;
	float out;
	glyphInfo_t *glyph;
	float useScale;
	const char *s = text;
	fontInfo_t *font = UI_SelectTextFont(scale, fontIndex);

	useScale = scale * font->glyphScale;
	out = 0;
	if (text) {
		len = strlen(text);
		if (limit > 0 && len > limit) {
			len = limit;
		}
		count = 0;
		while (s && *s && count < len) {
			if (Q_IsColorString(s)) {
				s += 2;
				continue;
			}

			glyph = &font->glyphs[(int)*s];
			out += glyph->xSkip;
			s++;
			count++;
		}
	}
	return out * useScale;
}

/*
=================
Text_Width
=================
*/
int Text_Width(const char *text, float scale, int limit) {
	return Text_WidthExt(text, scale, limit, ITEM_FONT_INHERIT);
}

/*
=================
Text_HeightExt
=================
*/
static int Text_HeightExt(const char *text, float scale, int limit, int fontIndex) {
	int len, count;
	float max;
	glyphInfo_t *glyph;
	float useScale;
	const char *s = text; // bk001206 - unsigned
	fontInfo_t *font = UI_SelectTextFont(scale, fontIndex);

	useScale = scale * font->glyphScale;
	max = 0;
	if (text) {
		len = strlen(text);
		if (limit > 0 && len > limit) {
			len = limit;
		}
		count = 0;
		while (s && *s && count < len) {
			if (Q_IsColorString(s)) {
				s += 2;
				continue;
			}

			glyph = &font->glyphs[(int)*s]; // TTimo: FIXME: getting nasty warnings without the cast, hopefully this doesn't break the VM build
			if (max < glyph->height) {
				max = glyph->height;
			}
			s++;
			count++;
		}
	}
	return max * useScale;
}

/*
=================
Text_Height
=================
*/
int Text_Height(const char *text, float scale, int limit) {
	return Text_HeightExt(text, scale, limit, ITEM_FONT_INHERIT);
}

void Text_PaintChar(float x, float y, float width, float height, float scale, float s, float t, float s2, float t2, qhandle_t hShader) {
  float w, h;
  w = width * scale;
  h = height * scale;
  UI_AdjustFrom640( &x, &y, &w, &h );
  trap_R_DrawStretchPic( x, y, w, h, s, t, s2, t2, hShader );
		}

/*
=================
Text_PaintExt
=================
*/
static void Text_PaintExt(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style, int fontIndex) {
	int len, count;
	vec4_t newColor;
	glyphInfo_t *glyph;
	float useScale;
	fontInfo_t *font = UI_SelectTextFont(scale, fontIndex);

	useScale = scale * font->glyphScale;
	if (text) {
		const char *s = text; // bk001206 - unsigned
		trap_R_SetColor(color);
		memcpy(&newColor[0], &color[0], sizeof(vec4_t));
		len = strlen(text);
		if (limit > 0 && len > limit) {
			len = limit;
		}
		count = 0;
		while (s && *s && count < len) {
			glyph = &font->glyphs[(int)*s]; // TTimo: FIXME: getting nasty warnings without the cast, hopefully this doesn't break the VM build
			if (Q_IsColorString(s)) {
				memcpy(newColor, g_color_table[ColorIndex(*(s + 1))], sizeof(newColor));
				newColor[3] = color[3];
				trap_R_SetColor(newColor);
				s += 2;
				continue;
			}

			{
				float yadj = useScale * glyph->top;
				if (style == ITEM_TEXTSTYLE_SHADOWED || style == ITEM_TEXTSTYLE_SHADOWEDMORE) {
					int ofs = style == ITEM_TEXTSTYLE_SHADOWED ? 1 : 2;
					colorBlack[3] = newColor[3];
					trap_R_SetColor(colorBlack);
					Text_PaintChar(x + ofs, y - yadj + ofs,
						glyph->imageWidth,
						glyph->imageHeight,
						useScale,
						glyph->s,
						glyph->t,
						glyph->s2,
						glyph->t2,
						glyph->glyph);
					trap_R_SetColor(newColor);
					colorBlack[3] = 1.0;
				}
				Text_PaintChar(x, y - yadj,
					glyph->imageWidth,
					glyph->imageHeight,
					useScale,
					glyph->s,
					glyph->t,
					glyph->s2,
					glyph->t2,
					glyph->glyph);
			}

			x += (glyph->xSkip * useScale) + adjust;
			s++;
			count++;
		}
		trap_R_SetColor(NULL);
	}
}

/*
=================
Text_Paint
=================
*/
void Text_Paint(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style) {
	Text_PaintExt(x, y, scale, color, text, adjust, limit, style, ITEM_FONT_INHERIT);
}

/*
=================
Text_PaintWithCursorExt
=================
*/
static void Text_PaintWithCursorExt(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex) {
	int len, count;
	vec4_t newColor;
	glyphInfo_t *glyph, *glyph2;
	float yadj;
	float useScale;
	fontInfo_t *font = UI_SelectTextFont(scale, fontIndex);

	useScale = scale * font->glyphScale;
	if (text) {
		const char *s = text; // bk001206 - unsigned
		trap_R_SetColor(color);
		memcpy(&newColor[0], &color[0], sizeof(vec4_t));
		len = strlen(text);
		if (limit > 0 && len > limit) {
			len = limit;
		}
		count = 0;
		glyph2 = &font->glyphs[(int)cursor]; // bk001206 - possible signed char
		while (s && *s && count < len) {
			glyph = &font->glyphs[(int)*s]; // TTimo: FIXME: getting nasty warnings without the cast, hopefully this doesn't break the VM build
			if (Q_IsColorString(s)) {
				memcpy(newColor, g_color_table[ColorIndex(*(s + 1))], sizeof(newColor));
				newColor[3] = color[3];
				trap_R_SetColor(newColor);
				s += 2;
				continue;
			}

			yadj = useScale * glyph->top;
			if (style == ITEM_TEXTSTYLE_SHADOWED || style == ITEM_TEXTSTYLE_SHADOWEDMORE) {
				int ofs = style == ITEM_TEXTSTYLE_SHADOWED ? 1 : 2;
				colorBlack[3] = newColor[3];
				trap_R_SetColor(colorBlack);
				Text_PaintChar(x + ofs, y - yadj + ofs,
					glyph->imageWidth,
					glyph->imageHeight,
					useScale,
					glyph->s,
					glyph->t,
					glyph->s2,
					glyph->t2,
					glyph->glyph);
				colorBlack[3] = 1.0;
				trap_R_SetColor(newColor);
			}
			Text_PaintChar(x, y - yadj,
				glyph->imageWidth,
				glyph->imageHeight,
				useScale,
				glyph->s,
				glyph->t,
				glyph->s2,
				glyph->t2,
				glyph->glyph);

			yadj = useScale * glyph2->top;
			if (count == cursorPos && !((uiInfo.uiDC.realTime / BLINK_DIVISOR) & 1)) {
				Text_PaintChar(x, y - yadj,
					glyph2->imageWidth,
					glyph2->imageHeight,
					useScale,
					glyph2->s,
					glyph2->t,
					glyph2->s2,
					glyph2->t2,
					glyph2->glyph);
			}

			x += (glyph->xSkip * useScale);
			s++;
			count++;
		}
		if (cursorPos == len && !((uiInfo.uiDC.realTime / BLINK_DIVISOR) & 1)) {
			yadj = useScale * glyph2->top;
			Text_PaintChar(x, y - yadj,
				glyph2->imageWidth,
				glyph2->imageHeight,
				useScale,
				glyph2->s,
				glyph2->t,
				glyph2->s2,
				glyph2->t2,
				glyph2->glyph);
		}

		trap_R_SetColor(NULL);
	}
}

/*
=================
Text_PaintWithCursor
=================
*/
void Text_PaintWithCursor(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style) {
	Text_PaintWithCursorExt(x, y, scale, color, text, cursorPos, cursor, limit, style, ITEM_FONT_INHERIT);
}


static void Text_Paint_Limit(float *maxX, float x, float y, float scale, vec4_t color, const char* text, float adjust, int limit) {
  int len, count;
	vec4_t newColor;
	glyphInfo_t *glyph;
  if (text) {
    const char *s = text; // bk001206 - unsigned
		float max = *maxX;
		float useScale;
		fontInfo_t *font = &uiInfo.uiDC.Assets.textFont;
		if (scale <= ui_smallFont.value) {
			font = &uiInfo.uiDC.Assets.smallFont;
		} else if (scale > ui_bigFont.value) {
			font = &uiInfo.uiDC.Assets.bigFont;
		}
		useScale = scale * font->glyphScale;
		trap_R_SetColor( color );
    len = strlen(text);					 
		if (limit > 0 && len > limit) {
			len = limit;
		}
		count = 0;
		while (s && *s && count < len) {
			glyph = &font->glyphs[(int)*s]; // TTimo: FIXME: getting nasty warnings without the cast, hopefully this doesn't break the VM build
			if ( Q_IsColorString( s ) ) {
				memcpy( newColor, g_color_table[ColorIndex(*(s+1))], sizeof( newColor ) );
				newColor[3] = color[3];
				trap_R_SetColor( newColor );
				s += 2;
				continue;
			} else {
	      float yadj = useScale * glyph->top;
				if (Text_Width(s, useScale, 1) + x > max) {
					*maxX = 0;
					break;
				}
		    Text_PaintChar(x, y - yadj, 
			                 glyph->imageWidth,
				               glyph->imageHeight,
				               useScale, 
						           glyph->s,
								       glyph->t,
								       glyph->s2,
									     glyph->t2,
										   glyph->glyph);
	      x += (glyph->xSkip * useScale) + adjust;
				*maxX = x;
				count++;
				s++;
	    }
		}
	  trap_R_SetColor( NULL );
  }

		}


/*
=================
UI_SyncMenuStateFromCvars
=================
*/
static void UI_SyncMenuStateFromCvars( void ) {
	int colorIndex;

	colorIndex = (int)trap_Cvar_VariableValue( "color1" );
	if ( colorIndex < 1 || colorIndex > ARRAY_LEN( gamecodetoui ) ) {
		colorIndex = 1;
	}

	uiInfo.effectsColor = gamecodetoui[colorIndex - 1];
	uiInfo.currentCrosshair = (int)trap_Cvar_VariableValue( "cg_drawCrosshair" );
	trap_Cvar_Set( "ui_mousePitch", ( trap_Cvar_VariableValue( "m_pitch" ) >= 0 ) ? "0" : "1" );
}

/*
=================
_UI_Refresh
=================
*/

void UI_DrawCenteredPic(qhandle_t image, int w, int h) {
  int x, y;
  x = (SCREEN_WIDTH - w) / 2;
  y = (SCREEN_HEIGHT - h) / 2;
  UI_DrawHandlePic(x, y, w, h, image);
		}

int frameCount = 0;
int startTime;

#define	UI_FPS_FRAMES	4
void _UI_Refresh( int realtime )
{
	static int index;
	static int	previousTimes[UI_FPS_FRAMES];

	//if ( !( trap_Key_GetCatcher() & KEYCATCH_UI ) ) {
	//	return;
	//}

	uiInfo.uiDC.frameTime = realtime - uiInfo.uiDC.realTime;
	uiInfo.uiDC.realTime = realtime;

	previousTimes[index % UI_FPS_FRAMES] = uiInfo.uiDC.frameTime;
	index++;
	if ( index > UI_FPS_FRAMES ) {
		int i, total;
		// average multiple frames together to smooth changes out a bit
		total = 0;
		for ( i = 0 ; i < UI_FPS_FRAMES ; i++ ) {
			total += previousTimes[i];
		}
		if ( !total ) {
			total = 1;
		}
		uiInfo.uiDC.FPS = 1000 * UI_FPS_FRAMES / total;
	}



	UI_UpdateCvars();

	if (Menu_Count() > 0) {
		// paint all the menus
		Menu_PaintAll();
		// refresh server browser list
		UI_DoServerRefresh();
		// refresh server status
		UI_BuildServerStatus(qfalse);
		// refresh find player list
		UI_BuildFindPlayerList(qfalse);
	} 
	
	// draw cursor
	UI_SetColor( NULL );
	if (Menu_Count() > 0) {
		UI_DrawHandlePic( uiInfo.uiDC.cursorx-16, uiInfo.uiDC.cursory-16, 32, 32, uiInfo.uiDC.Assets.cursor);
	}

#ifndef NDEBUG
	if (uiInfo.uiDC.debug)
	{
		// cursor coordinates
		//FIXME
		//UI_DrawString( 0, 0, va("(%d,%d)",uis.cursorx,uis.cursory), UI_LEFT|UI_SMALLFONT, colorRed );
	}
#endif

		}

/*
=================
_UI_Shutdown
=================
*/
void _UI_Shutdown( void ) {
	trap_LAN_SaveCachedServers();
		}

char *defaultMenu = NULL;

/*
=================
UI_GetRetailMenuPathAlias

Resolves the known Quake Live metadata tables that moved under ui/.
=================
*/
static const char *UI_GetRetailMenuPathAlias( const char *filename ) {
	if ( !filename || !filename[0] ) {
		return filename;
	}

	if ( strchr( filename, '/' ) || strchr( filename, '\\' ) ) {
		return filename;
	}

	if ( !Q_stricmp( filename, "teaminfo.txt" ) ) {
		return "ui/teaminfo.txt";
	}

	if ( !Q_stricmp( filename, "country.txt" ) ) {
		return "ui/country.txt";
	}

	return filename;
}

/*
=================
GetMenuBuffer
=================
*/
char *GetMenuBuffer(const char *filename) {
	const char	*resolvedFilename;
	int		len;
	fileHandle_t	f;
	static char buf[MAX_MENUFILE];

	resolvedFilename = UI_GetRetailMenuPathAlias( filename );
	len = trap_FS_FOpenFile( resolvedFilename, &f, FS_READ );
	if ( !f && resolvedFilename != filename ) {
		len = trap_FS_FOpenFile( filename, &f, FS_READ );
	}
	if ( !f ) {
		trap_Print( va( S_COLOR_RED "menu file not found: %s, using default\n", filename ) );
		return defaultMenu;
	}
	if ( len >= MAX_MENUFILE ) {
		trap_Print( va( S_COLOR_RED "menu file too large: %s is %i, max allowed is %i", filename, len, MAX_MENUFILE ) );
		trap_FS_FCloseFile( f );
		return defaultMenu;
	}

	trap_FS_Read( buf, len, f );
	buf[len] = 0;
	trap_FS_FCloseFile( f );
	//COM_Compress(buf);
  return buf;

		}

qboolean Asset_Parse(int handle) {
	pc_token_t token;
	const char *tempStr;

	if (!trap_PC_ReadToken(handle, &token))
		return qfalse;
	if (Q_stricmp(token.string, "{") != 0) {
		return qfalse;
	}
    
	while ( 1 ) {

		memset(&token, 0, sizeof(pc_token_t));

		if (!trap_PC_ReadToken(handle, &token))
			return qfalse;

		if (Q_stricmp(token.string, "}") == 0) {
			return qtrue;
		}

		// font
		if (Q_stricmp(token.string, "font") == 0) {
			int pointSize;
			const char *fontPath;
			if (!PC_String_Parse(handle, &tempStr) || !PC_Int_Parse(handle,&pointSize)) {
				return qfalse;
			}
			fontPath = tempStr;
			UI_NormalizeFontPath( &fontPath, &pointSize, QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE );
			trap_R_RegisterFont(fontPath, pointSize, &uiInfo.uiDC.Assets.textFont);
			uiInfo.uiDC.Assets.fontRegistered = qtrue;
			continue;
		}

		if (Q_stricmp(token.string, "smallFont") == 0) {
			int pointSize;
			const char *fontPath;
			if (!PC_String_Parse(handle, &tempStr) || !PC_Int_Parse(handle,&pointSize)) {
				return qfalse;
			}
			fontPath = tempStr;
			UI_NormalizeFontPath( &fontPath, &pointSize, QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE );
			trap_R_RegisterFont(fontPath, pointSize, &uiInfo.uiDC.Assets.smallFont);
			continue;
		}

		if (Q_stricmp(token.string, "bigFont") == 0) {
			int pointSize;
			const char *fontPath;
			if (!PC_String_Parse(handle, &tempStr) || !PC_Int_Parse(handle,&pointSize)) {
				return qfalse;
			}
			fontPath = tempStr;
			UI_NormalizeFontPath( &fontPath, &pointSize, QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE );
			trap_R_RegisterFont(fontPath, pointSize, &uiInfo.uiDC.Assets.bigFont);
			continue;
		}

		// gradientbar
		if (Q_stricmp(token.string, "gradientbar") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			uiInfo.uiDC.Assets.gradientBar = trap_R_RegisterShaderNoMip(tempStr);
			continue;
		}

		// enterMenuSound
		if (Q_stricmp(token.string, "menuEnterSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			uiInfo.uiDC.Assets.menuEnterSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		// exitMenuSound
		if (Q_stricmp(token.string, "menuExitSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			uiInfo.uiDC.Assets.menuExitSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		// itemFocusSound
		if (Q_stricmp(token.string, "itemFocusSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			uiInfo.uiDC.Assets.itemFocusSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		// menuBuzzSound
		if (Q_stricmp(token.string, "menuBuzzSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			uiInfo.uiDC.Assets.menuBuzzSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		if (Q_stricmp(token.string, "cursor") == 0) {
			if (!PC_String_Parse(handle, &uiInfo.uiDC.Assets.cursorStr)) {
				return qfalse;
			}
			uiInfo.uiDC.Assets.cursor = trap_R_RegisterShaderNoMip( uiInfo.uiDC.Assets.cursorStr);
			continue;
		}

		if (Q_stricmp(token.string, "fadeClamp") == 0) {
			if (!PC_Float_Parse(handle, &uiInfo.uiDC.Assets.fadeClamp)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "fadeCycle") == 0) {
			if (!PC_Int_Parse(handle, &uiInfo.uiDC.Assets.fadeCycle)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "fadeAmount") == 0) {
			if (!PC_Float_Parse(handle, &uiInfo.uiDC.Assets.fadeAmount)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "shadowX") == 0) {
			if (!PC_Float_Parse(handle, &uiInfo.uiDC.Assets.shadowX)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "shadowY") == 0) {
			if (!PC_Float_Parse(handle, &uiInfo.uiDC.Assets.shadowY)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "shadowColor") == 0) {
			if (!PC_Color_Parse(handle, &uiInfo.uiDC.Assets.shadowColor)) {
				return qfalse;
			}
			uiInfo.uiDC.Assets.shadowFadeClamp = uiInfo.uiDC.Assets.shadowColor[3];
			continue;
		}

	}
	return qfalse;
		}

void Font_Report() {
  int i;
  Com_Printf("Font Info\n");
  Com_Printf("=========\n");
  for ( i = 32; i < 96; i++) {
    Com_Printf("Glyph handle %i: %i\n", i, uiInfo.uiDC.Assets.textFont.glyphs[i].glyph);
  }
		}

void UI_Report() {
  String_Report();
  //Font_Report();

		}

void UI_ParseMenu(const char *menuFile) {
	int handle;
	pc_token_t token;

	Com_Printf("Parsing menu file:%s\n", menuFile);

	handle = trap_PC_LoadSource(menuFile);
	if (!handle) {
		return;
	}

	while ( 1 ) {
		memset(&token, 0, sizeof(pc_token_t));
		if (!trap_PC_ReadToken( handle, &token )) {
			break;
		}

		//if ( Q_stricmp( token, "{" ) ) {
		//	Com_Printf( "Missing { in menu file\n" );
		//	break;
		//}

		//if ( menuCount == MAX_MENUS ) {
		//	Com_Printf( "Too many menus!\n" );
		//	break;
		//}

		if ( token.string[0] == '}' ) {
			break;
		}

		if (Q_stricmp(token.string, "assetGlobalDef") == 0) {
			if (Asset_Parse(handle)) {
				continue;
			} else {
				break;
			}
		}

		if (Q_stricmp(token.string, "menudef") == 0) {
			// start a new menu
			Menu_New(handle);
		}
	}
	trap_PC_FreeSource(handle);
		}

qboolean Load_Menu(int handle) {
	pc_token_t token;

	if (!trap_PC_ReadToken(handle, &token))
		return qfalse;
	if (token.string[0] != '{') {
		return qfalse;
	}

	while ( 1 ) {

		if (!trap_PC_ReadToken(handle, &token))
			return qfalse;
    
		if ( token.string[0] == 0 ) {
			return qfalse;
		}

		if ( token.string[0] == '}' ) {
			return qtrue;
		}

		UI_ParseMenu(token.string); 
	}
	return qfalse;
		}

/*
=============
UI_LoadMenus
=============
*/
void UI_LoadMenus(const char *menuFile, qboolean reset) {
pc_token_t token;
int handle;
int start;

	start = trap_Milliseconds();

	handle = trap_PC_LoadSource(menuFile);
	if (!handle) {
		const char *fallback = UI_DefaultMenuFile();
		const char *fatalFallback = fallback;

		trap_Error(va(S_COLOR_YELLOW "menu file not found: %s, using default\n", menuFile));
		if (!UI_MenuFileEquals(menuFile, fallback)) {
			menuFile = fallback;
			handle = trap_PC_LoadSource(menuFile);
		}
		if (!handle && !UI_MenuFileEquals(fallback, UI_MENU_FILE_LEGACY)) {
			fatalFallback = UI_MENU_FILE_LEGACY;
			menuFile = fatalFallback;
			handle = trap_PC_LoadSource(menuFile);
		}
		if (!handle) {
			trap_Error(va(S_COLOR_RED "default menu file not found: %s, unable to continue!\n", fatalFallback));
		}
	}


	UI_UpdateActiveMenuFlowForFile(menuFile);
	UI_SetBrowserActive(ui_activeMenuFlow == UI_MENU_FLOW_QUAKELIVE);
	UI_BrowserBridge_SetActive(ui_activeMenuFlow == UI_MENU_FLOW_BRIDGED);

	if (reset) {
		Menu_Reset();
	}

	while ( 1 ) {
		if (!trap_PC_ReadToken(handle, &token))
			break;
		if( token.string[0] == 0 || token.string[0] == '}') {
			break;
		}

		if ( token.string[0] == '}' ) {
			break;
		}

		if (Q_stricmp(token.string, "loadmenu") == 0) {
			if (Load_Menu(handle)) {
				continue;
			} else {
				break;
			}
		}
	}

	Com_Printf("UI menu load time = %d milli seconds\n", trap_Milliseconds() - start);

	trap_PC_FreeSource( handle );
		}

/*
=============
UI_ApplyRetailMenuFixups

Hide source-only widgets from drifted read-only menu files so the active
runtime stays aligned with the shipped retail menu set.
=============
*/
static void UI_ApplyRetailMenuFixups( void ) {
	menuDef_t *menu;

	menu = Menus_FindByName( "ingame_join" );
	if ( menu != NULL ) {
		Menu_ShowItemByName( menu, "country_label", qfalse );
		Menu_ShowItemByName( menu, "country_list", qfalse );
	}
}

/*
=============
UI_Load

Reload menu definitions and supporting data, respecting the active menu flow.
=============
*/
void UI_Load() {
	char lastName[1024];
	menuDef_t *menu = Menu_GetFocused();
	const char *menuSet = UI_Cvar_VariableString("ui_menuFiles");
	const char *ingameSet;

	if (menu && menu->window.name) {
		strcpy(lastName, menu->window.name);
	}
	UI_UpdateActiveMenuFlow();
	if (menuSet == NULL || menuSet[0] == '\0') {
		menuSet = UI_DefaultMenuFile();
	}

	String_Init();

#ifdef PRE_RELEASE_TADEMO
	UI_ParseGameInfo("demogameinfo.txt");
#else
	UI_ParseGameInfo("gameinfo.txt");
	UI_LoadArenas();
#endif

	ingameSet = UI_DefaultIngameFile();
	Com_Printf("UI: loading %s (flow %d) with ingame %s\n", menuSet, ui_activeMenuFlow, ingameSet);

	UI_LoadMenus(menuSet, qtrue);
	UI_LoadMenus(ingameSet, qfalse);
	if (UI_MenuFileExists("ui/comp_spectator.menu")) {
		UI_ParseMenu("ui/comp_spectator.menu");
	}
	if (UI_MenuFileExists("ui/comp_spectator_follow.menu")) {
		UI_ParseMenu("ui/comp_spectator_follow.menu");
	}
	UI_ApplyRetailMenuFixups();
	Menus_CloseAll();
	Menus_ActivateByName(lastName);

}

static const char *handicapValues[] = {"None","95","90","85","80","75","70","65","60","55","50","45","40","35","30","25","20","15","10","5",NULL};

static void UI_DrawHandicap(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  int i, h;

  h = Com_Clamp( 5, 100, trap_Cvar_VariableValue("handicap") );
  i = 20 - h / 5;

  Text_Paint(rect->x, rect->y, scale, color, handicapValues[i], 0, 0, textStyle);
		}

static void UI_DrawClanName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  Text_Paint(rect->x, rect->y, scale, color, UI_Cvar_VariableString("ui_teamName"), 0, 0, textStyle);
		}


static void UI_SetCapFragLimits(qboolean uiVars) {
	int cap = 5;
	int frag = 10;
	if (uiInfo.gameTypes[ui_gameType.integer].gtEnum == GT_OBELISK) {
		cap = 4;
	} else if (uiInfo.gameTypes[ui_gameType.integer].gtEnum == GT_HARVESTER) {
		cap = 15;
	}
	if (uiVars) {
		trap_Cvar_Set("ui_captureLimit", va("%d", cap));
		trap_Cvar_Set("ui_fragLimit", va("%d", frag));
	} else {
		trap_Cvar_Set("capturelimit", va("%d", cap));
		trap_Cvar_Set("fraglimit", va("%d", frag));
	}
		}
// ui_gameType assumes gametype 0 is -1 ALL and will not show
static void UI_DrawGameType(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  Text_Paint(rect->x, rect->y, scale, color, uiInfo.gameTypes[ui_gameType.integer].gameType, 0, 0, textStyle);
		}

static void UI_DrawNetGameType(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	if (ui_netGameType.integer < 0 || ui_netGameType.integer > uiInfo.numGameTypes) {
		trap_Cvar_Set("ui_netGameType", "0");
		trap_Cvar_Set("ui_actualNetGameType", "0");
	}
  Text_Paint(rect->x, rect->y, scale, color, uiInfo.gameTypes[ui_netGameType.integer].gameType , 0, 0, textStyle);
		}

static void UI_DrawJoinGameType(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	if (ui_joinGameType.integer < 0 || ui_joinGameType.integer > uiInfo.numJoinGameTypes) {
		trap_Cvar_Set("ui_joinGameType", "0");
	}
  Text_Paint(rect->x, rect->y, scale, color, uiInfo.joinGameTypes[ui_joinGameType.integer].gameType , 0, 0, textStyle);
		}



static int UI_TeamIndexFromName(const char *name) {
  int i;

  if (name && *name) {
    for (i = 0; i < uiInfo.teamCount; i++) {
      if (Q_stricmp(name, uiInfo.teamList[i].teamName) == 0) {
        return i;
      }
    }
  } 

  return 0;

		}

static void UI_DrawClanLogo(rectDef_t *rect, float scale, vec4_t color) {
  int i;
  i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
  if (i >= 0 && i < uiInfo.teamCount) {
  	trap_R_SetColor( color );

		if (uiInfo.teamList[i].teamIcon == -1) {
      uiInfo.teamList[i].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[i].imageName);
      uiInfo.teamList[i].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[i].imageName));
      uiInfo.teamList[i].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[i].imageName));
		}

  	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon);
    trap_R_SetColor(NULL);
  }
		}

static void UI_DrawClanCinematic(rectDef_t *rect, float scale, vec4_t color) {
  int i;
  i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
  if (i >= 0 && i < uiInfo.teamCount) {

		if (uiInfo.teamList[i].cinematic >= -2) {
			if (uiInfo.teamList[i].cinematic == -1) {
				uiInfo.teamList[i].cinematic = trap_CIN_PlayCinematic(va("%s.roq", uiInfo.teamList[i].imageName), 0, 0, 0, 0, (CIN_loop | CIN_silent) );
			}
			if (uiInfo.teamList[i].cinematic >= 0) {
			  trap_CIN_RunCinematic(uiInfo.teamList[i].cinematic);
				trap_CIN_SetExtents(uiInfo.teamList[i].cinematic, rect->x, rect->y, rect->w, rect->h);
	 			trap_CIN_DrawCinematic(uiInfo.teamList[i].cinematic);
			} else {
			  	trap_R_SetColor( color );
				UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon_Metal);
				trap_R_SetColor(NULL);
				uiInfo.teamList[i].cinematic = -2;
			}
		} else {
	  	trap_R_SetColor( color );
			UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon);
			trap_R_SetColor(NULL);
		}
	}

		}

static void UI_DrawPreviewCinematic(rectDef_t *rect, float scale, vec4_t color) {
	if (uiInfo.previewMovie > -2) {
		uiInfo.previewMovie = trap_CIN_PlayCinematic(va("%s.roq", uiInfo.movieList[uiInfo.movieIndex]), 0, 0, 0, 0, (CIN_loop | CIN_silent) );
		if (uiInfo.previewMovie >= 0) {
		  trap_CIN_RunCinematic(uiInfo.previewMovie);
			trap_CIN_SetExtents(uiInfo.previewMovie, rect->x, rect->y, rect->w, rect->h);
 			trap_CIN_DrawCinematic(uiInfo.previewMovie);
		} else {
			uiInfo.previewMovie = -2;
		}
	} 

		}



static void UI_DrawSkill(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  int i;
	i = trap_Cvar_VariableValue( "g_spSkill" );
  if (i < 1 || i > numSkillLevels) {
    i = 1;
  }
  Text_Paint(rect->x, rect->y, scale, color, skillLevels[i-1],0, 0, textStyle);
		}


static void UI_DrawTeamName(rectDef_t *rect, float scale, vec4_t color, qboolean blue, int textStyle) {
  int i;
  i = UI_TeamIndexFromName(UI_Cvar_VariableString((blue) ? "ui_blueTeam" : "ui_redTeam"));
  if (i >= 0 && i < uiInfo.teamCount) {
    Text_Paint(rect->x, rect->y, scale, color, va("%s: %s", (blue) ? "Blue" : "Red", uiInfo.teamList[i].teamName),0, 0, textStyle);
  }
		}

static void UI_DrawTeamMember(rectDef_t *rect, float scale, vec4_t color, qboolean blue, int num, int textStyle) {
	// 0 - None
	// 1 - Human
	// 2..NumCharacters - Bot
	int value = trap_Cvar_VariableValue(va(blue ? "ui_blueteam%i" : "ui_redteam%i", num));
	const char *text;
	if (value <= 0) {
		text = "Closed";
	} else if (value == 1) {
		text = "Human";
	} else {
		value -= 2;

		if (ui_actualNetGameType.integer >= GT_TEAM) {
			if (value >= uiInfo.characterCount) {
				value = 0;
			}
			text = uiInfo.characterList[value].name;
		} else {
			if (value >= UI_GetNumBots()) {
				value = 0;
			}
			text = UI_GetBotNameByNumber(value);
		}
	}
  Text_Paint(rect->x, rect->y, scale, color, text, 0, 0, textStyle);
		}

static void UI_DrawEffects(rectDef_t *rect, float scale, vec4_t color) {
	UI_DrawHandlePic( rect->x, rect->y - 14, 128, 8, uiInfo.uiDC.Assets.fxBasePic );
	UI_DrawHandlePic( rect->x + uiInfo.effectsColor * 16 + 8, rect->y - 16, 16, 12, uiInfo.uiDC.Assets.fxPic[uiInfo.effectsColor] );
		}

static void UI_DrawMapPreview(rectDef_t *rect, float scale, vec4_t color, qboolean net) {
	int map = (net) ? ui_currentNetMap.integer : ui_currentMap.integer;
	if (map < 0 || map > uiInfo.mapCount) {
		if (net) {
			ui_currentNetMap.integer = 0;
			trap_Cvar_Set("ui_currentNetMap", "0");
		} else {
			ui_currentMap.integer = 0;
			trap_Cvar_Set("ui_currentMap", "0");
		}
		map = 0;
	}

	if (uiInfo.mapList[map].levelShot == -1) {
		uiInfo.mapList[map].levelShot = trap_R_RegisterShaderNoMip(uiInfo.mapList[map].imageName);
	}

	if (uiInfo.mapList[map].levelShot > 0) {
		UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.mapList[map].levelShot);
	} else {
		UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, trap_R_RegisterShaderNoMip("menu/art/unknownmap"));
	}
}						 


static void UI_DrawMapTimeToBeat(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	int minutes, seconds, time;
	if (ui_currentMap.integer < 0 || ui_currentMap.integer > uiInfo.mapCount) {
		ui_currentMap.integer = 0;
		trap_Cvar_Set("ui_currentMap", "0");
	}

	time = uiInfo.mapList[ui_currentMap.integer].timeToBeat[uiInfo.gameTypes[ui_gameType.integer].gtEnum];

	minutes = time / 60;
	seconds = time % 60;

  Text_Paint(rect->x, rect->y, scale, color, va("%02i:%02i", minutes, seconds), 0, 0, textStyle);
		}



static void UI_DrawMapCinematic(rectDef_t *rect, float scale, vec4_t color, qboolean net) {

	int map = (net) ? ui_currentNetMap.integer : ui_currentMap.integer; 
	if (map < 0 || map > uiInfo.mapCount) {
		if (net) {
			ui_currentNetMap.integer = 0;
			trap_Cvar_Set("ui_currentNetMap", "0");
		} else {
			ui_currentMap.integer = 0;
			trap_Cvar_Set("ui_currentMap", "0");
		}
		map = 0;
	}

	if (uiInfo.mapList[map].cinematic >= -1) {
		if (uiInfo.mapList[map].cinematic == -1) {
			uiInfo.mapList[map].cinematic = trap_CIN_PlayCinematic(va("%s.roq", uiInfo.mapList[map].mapLoadName), 0, 0, 0, 0, (CIN_loop | CIN_silent) );
		}
		if (uiInfo.mapList[map].cinematic >= 0) {
		  trap_CIN_RunCinematic(uiInfo.mapList[map].cinematic);
		  trap_CIN_SetExtents(uiInfo.mapList[map].cinematic, rect->x, rect->y, rect->w, rect->h);
 			trap_CIN_DrawCinematic(uiInfo.mapList[map].cinematic);
		} else {
			uiInfo.mapList[map].cinematic = -2;
		}
	} else {
		UI_DrawMapPreview(rect, scale, color, net);
	}
		}



static qboolean updateModel = qtrue;
static qboolean q3Model = qfalse;

static void UI_DrawPlayerModel(rectDef_t *rect) {
  static playerInfo_t info;
  char model[MAX_QPATH];
  char team[256];
	char head[256];
	vec3_t	viewangles;
	vec3_t	moveangles;

	  if (trap_Cvar_VariableValue("ui_Q3Model")) {
	  strcpy(model, UI_Cvar_VariableString("model"));
		strcpy(head, UI_Cvar_VariableString("headmodel"));
		if (!q3Model) {
			q3Model = qtrue;
			updateModel = qtrue;
		}
		team[0] = '\0';
	} else {

		strcpy(team, UI_Cvar_VariableString("ui_teamName"));
		strcpy(model, UI_Cvar_VariableString("team_model"));
		strcpy(head, UI_Cvar_VariableString("team_headmodel"));
		if (q3Model) {
			q3Model = qfalse;
			updateModel = qtrue;
		}
	}
  if (updateModel) {
  	memset( &info, 0, sizeof(playerInfo_t) );
  	viewangles[YAW]   = 180 - 10;
  	viewangles[PITCH] = 0;
  	viewangles[ROLL]  = 0;
  	VectorClear( moveangles );
    UI_PlayerInfo_SetModel( &info, model, head, team);
    UI_PlayerInfo_SetInfo( &info, LEGS_IDLE, TORSO_STAND, viewangles, vec3_origin, WP_MACHINEGUN, qfalse );
//		UI_RegisterClientModelname( &info, model, head, team);
    updateModel = qfalse;
  }

  UI_DrawPlayer( rect->x, rect->y, rect->w, rect->h, &info, uiInfo.uiDC.realTime / 2);

		}

static void UI_DrawNetSource(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	if (ui_netSource.integer < 0 || ui_netSource.integer > numNetSources) {
		ui_netSource.integer = 0;
	}
  Text_Paint(rect->x, rect->y, scale, color, va("Source: %s", netSources[ui_netSource.integer]), 0, 0, textStyle);
		}

static void UI_DrawNetMapPreview(rectDef_t *rect, float scale, vec4_t color) {

	if (uiInfo.serverStatus.currentServerPreview > 0) {
		UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.serverStatus.currentServerPreview);
	} else {
		UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, trap_R_RegisterShaderNoMip("menu/art/unknownmap"));
	}
		}

static void UI_DrawNetMapCinematic(rectDef_t *rect, float scale, vec4_t color) {
	if (ui_currentNetMap.integer < 0 || ui_currentNetMap.integer > uiInfo.mapCount) {
		ui_currentNetMap.integer = 0;
		trap_Cvar_Set("ui_currentNetMap", "0");
	}

	if (uiInfo.serverStatus.currentServerCinematic >= 0) {
	  trap_CIN_RunCinematic(uiInfo.serverStatus.currentServerCinematic);
	  trap_CIN_SetExtents(uiInfo.serverStatus.currentServerCinematic, rect->x, rect->y, rect->w, rect->h);
 	  trap_CIN_DrawCinematic(uiInfo.serverStatus.currentServerCinematic);
	} else {
		UI_DrawNetMapPreview(rect, scale, color);
	}
		}



static void UI_DrawNetFilter(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	if (ui_serverFilterType.integer < 0 || ui_serverFilterType.integer > numServerFilters) {
		ui_serverFilterType.integer = 0;
	}
  Text_Paint(rect->x, rect->y, scale, color, va("Filter: %s", serverFilters[ui_serverFilterType.integer].description), 0, 0, textStyle);
		}


static void UI_DrawTier(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  int i;
	i = trap_Cvar_VariableValue( "ui_currentTier" );
  if (i < 0 || i >= uiInfo.tierCount) {
    i = 0;
  }
  Text_Paint(rect->x, rect->y, scale, color, va("Tier: %s", uiInfo.tierList[i].tierName),0, 0, textStyle);
		}

static void UI_DrawTierMap(rectDef_t *rect, int index) {
  int i;
	i = trap_Cvar_VariableValue( "ui_currentTier" );
  if (i < 0 || i >= uiInfo.tierCount) {
    i = 0;
  }

	if (uiInfo.tierList[i].mapHandles[index] == -1) {
		uiInfo.tierList[i].mapHandles[index] = trap_R_RegisterShaderNoMip(va("levelshots/%s", uiInfo.tierList[i].maps[index]));
	}
												 
	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.tierList[i].mapHandles[index]);
		}

static const char *UI_EnglishMapName(const char *map) {
	int i;
	for (i = 0; i < uiInfo.mapCount; i++) {
		if (Q_stricmp(map, uiInfo.mapList[i].mapLoadName) == 0) {
			return uiInfo.mapList[i].mapName;
		}
	}
	return "";
		}

static void UI_DrawTierMapName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  int i, j;
	i = trap_Cvar_VariableValue( "ui_currentTier" );
  if (i < 0 || i >= uiInfo.tierCount) {
    i = 0;
  }
	j = trap_Cvar_VariableValue("ui_currentMap");
	if (j < 0 || j > MAPS_PER_TIER) {
		j = 0;
	}

  Text_Paint(rect->x, rect->y, scale, color, UI_EnglishMapName(uiInfo.tierList[i].maps[j]), 0, 0, textStyle);
		}

static void UI_DrawTierGameType(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  int i, j;
	i = trap_Cvar_VariableValue( "ui_currentTier" );
  if (i < 0 || i >= uiInfo.tierCount) {
    i = 0;
  }
	j = trap_Cvar_VariableValue("ui_currentMap");
	if (j < 0 || j > MAPS_PER_TIER) {
		j = 0;
	}

  Text_Paint(rect->x, rect->y, scale, color, uiInfo.gameTypes[uiInfo.tierList[i].gameTypes[j]].gameType , 0, 0, textStyle);
		}



static const char *UI_AIFromName(const char *name) {
	int j;
	for (j = 0; j < uiInfo.aliasCount; j++) {
		if (Q_stricmp(uiInfo.aliasList[j].name, name) == 0) {
			return uiInfo.aliasList[j].ai;
		}
	}
	return "James";
		}







static qboolean updateOpponentModel = qtrue;
static void UI_DrawOpponent(rectDef_t *rect) {
  static playerInfo_t info2;
  char model[MAX_QPATH];
  char headmodel[MAX_QPATH];
  char team[256];
	vec3_t	viewangles;
	vec3_t	moveangles;
  
	if (updateOpponentModel) {
		
		strcpy(model, UI_Cvar_VariableString("ui_opponentModel"));
	  strcpy(headmodel, UI_Cvar_VariableString("ui_opponentModel"));
		team[0] = '\0';

  	memset( &info2, 0, sizeof(playerInfo_t) );
  	viewangles[YAW]   = 180 - 10;
  	viewangles[PITCH] = 0;
  	viewangles[ROLL]  = 0;
  	VectorClear( moveangles );
    UI_PlayerInfo_SetModel( &info2, model, headmodel, "");
    UI_PlayerInfo_SetInfo( &info2, LEGS_IDLE, TORSO_STAND, viewangles, vec3_origin, WP_MACHINEGUN, qfalse );
		UI_RegisterClientModelname( &info2, model, headmodel, team);
    updateOpponentModel = qfalse;
  }

  UI_DrawPlayer( rect->x, rect->y, rect->w, rect->h, &info2, uiInfo.uiDC.realTime / 2);

		}

static void UI_NextOpponent() {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));
  int j = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
	i++;
	if (i >= uiInfo.teamCount) {
		i = 0;
	}
	if (i == j) {
		i++;
		if ( i >= uiInfo.teamCount) {
			i = 0;
		}
	}
 	trap_Cvar_Set( "ui_opponentName", uiInfo.teamList[i].teamName );
		}

static void UI_PriorOpponent() {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));
  int j = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
	i--;
	if (i < 0) {
		i = uiInfo.teamCount - 1;
	}
	if (i == j) {
		i--;
		if ( i < 0) {
			i = uiInfo.teamCount - 1;
		}
	}
 	trap_Cvar_Set( "ui_opponentName", uiInfo.teamList[i].teamName );
		}

static void	UI_DrawPlayerLogo(rectDef_t *rect, vec3_t color) {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));

	if (uiInfo.teamList[i].teamIcon == -1) {
    uiInfo.teamList[i].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[i].imageName);
    uiInfo.teamList[i].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[i].imageName));
    uiInfo.teamList[i].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[i].imageName));
	}

 	trap_R_SetColor( color );
	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon );
 	trap_R_SetColor( NULL );
		}

static void	UI_DrawPlayerLogoMetal(rectDef_t *rect, vec3_t color) {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
	if (uiInfo.teamList[i].teamIcon == -1) {
    uiInfo.teamList[i].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[i].imageName);
    uiInfo.teamList[i].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[i].imageName));
    uiInfo.teamList[i].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[i].imageName));
	}

 	trap_R_SetColor( color );
	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon_Metal );
 	trap_R_SetColor( NULL );
		}

static void	UI_DrawPlayerLogoName(rectDef_t *rect, vec3_t color) {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
	if (uiInfo.teamList[i].teamIcon == -1) {
    uiInfo.teamList[i].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[i].imageName);
    uiInfo.teamList[i].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[i].imageName));
    uiInfo.teamList[i].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[i].imageName));
	}

 	trap_R_SetColor( color );
	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon_Name );
 	trap_R_SetColor( NULL );
		}

static void	UI_DrawOpponentLogo(rectDef_t *rect, vec3_t color) {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));
	if (uiInfo.teamList[i].teamIcon == -1) {
    uiInfo.teamList[i].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[i].imageName);
    uiInfo.teamList[i].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[i].imageName));
    uiInfo.teamList[i].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[i].imageName));
	}

 	trap_R_SetColor( color );
	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon );
 	trap_R_SetColor( NULL );
		}

static void	UI_DrawOpponentLogoMetal(rectDef_t *rect, vec3_t color) {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));
	if (uiInfo.teamList[i].teamIcon == -1) {
    uiInfo.teamList[i].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[i].imageName);
    uiInfo.teamList[i].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[i].imageName));
    uiInfo.teamList[i].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[i].imageName));
	}

 	trap_R_SetColor( color );
	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon_Metal );
 	trap_R_SetColor( NULL );
		}

static void	UI_DrawOpponentLogoName(rectDef_t *rect, vec3_t color) {
  int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));
	if (uiInfo.teamList[i].teamIcon == -1) {
    uiInfo.teamList[i].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[i].imageName);
    uiInfo.teamList[i].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[i].imageName));
    uiInfo.teamList[i].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[i].imageName));
	}

 	trap_R_SetColor( color );
	UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.teamList[i].teamIcon_Name );
 	trap_R_SetColor( NULL );
		}

static void UI_DrawAllMapsSelection(rectDef_t *rect, float scale, vec4_t color, int textStyle, qboolean net) {
	int map = (net) ? ui_currentNetMap.integer : ui_currentMap.integer;
	if (map >= 0 && map < uiInfo.mapCount) {
	  Text_Paint(rect->x, rect->y, scale, color, uiInfo.mapList[map].mapName, 0, 0, textStyle);
	}
		}

static void UI_DrawOpponentName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  Text_Paint(rect->x, rect->y, scale, color, UI_Cvar_VariableString("ui_opponentName"), 0, 0, textStyle);
		}


static int UI_OwnerDrawWidth(int ownerDraw, float scale) {
	int i, h, value;
	const char *text;
	const char *s = NULL;

  switch (ownerDraw) {
    case UI_HANDICAP:
			  h = Com_Clamp( 5, 100, trap_Cvar_VariableValue("handicap") );
				i = 20 - h / 5;
				s = handicapValues[i];
      break;
    case UI_CLANNAME:
				s = UI_Cvar_VariableString("ui_teamName");
      break;
    case UI_GAMETYPE:
				s = uiInfo.gameTypes[ui_gameType.integer].gameType;
      break;
    case UI_SKILL:
				i = trap_Cvar_VariableValue( "g_spSkill" );
				if (i < 1 || i > numSkillLevels) {
					i = 1;
				}
			  s = skillLevels[i-1];
      break;
    case UI_BLUETEAMNAME:
			  i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_blueTeam"));
			  if (i >= 0 && i < uiInfo.teamCount) {
			    s = va("%s: %s", "Blue", uiInfo.teamList[i].teamName);
			  }
      break;
    case UI_REDTEAMNAME:
			  i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_redTeam"));
			  if (i >= 0 && i < uiInfo.teamCount) {
			    s = va("%s: %s", "Red", uiInfo.teamList[i].teamName);
			  }
      break;
    case UI_BLUETEAM1:
		case UI_BLUETEAM2:
		case UI_BLUETEAM3:
		case UI_BLUETEAM4:
		case UI_BLUETEAM5:
			value = trap_Cvar_VariableValue(va("ui_blueteam%i", ownerDraw-UI_BLUETEAM1 + 1));
			if (value <= 0) {
				text = "Closed";
			} else if (value == 1) {
				text = "Human";
			} else {
				value -= 2;
				if (value >= uiInfo.aliasCount) {
					value = 0;
				}
				text = uiInfo.aliasList[value].name;
			}
			s = va("%i. %s", ownerDraw-UI_BLUETEAM1 + 1, text);
      break;
    case UI_REDTEAM1:
		case UI_REDTEAM2:
		case UI_REDTEAM3:
		case UI_REDTEAM4:
		case UI_REDTEAM5:
			value = trap_Cvar_VariableValue(va("ui_redteam%i", ownerDraw-UI_REDTEAM1 + 1));
			if (value <= 0) {
				text = "Closed";
			} else if (value == 1) {
				text = "Human";
			} else {
				value -= 2;
				if (value >= uiInfo.aliasCount) {
					value = 0;
				}
				text = uiInfo.aliasList[value].name;
			}
			s = va("%i. %s", ownerDraw-UI_REDTEAM1 + 1, text);
      break;
		case UI_NETSOURCE:
			if (ui_netSource.integer < 0 || ui_netSource.integer > uiInfo.numJoinGameTypes) {
				ui_netSource.integer = 0;
			}
			s = va("Source: %s", netSources[ui_netSource.integer]);
			break;
		case UI_NETFILTER:
			if (ui_serverFilterType.integer < 0 || ui_serverFilterType.integer > numServerFilters) {
				ui_serverFilterType.integer = 0;
			}
			s = va("Filter: %s", serverFilters[ui_serverFilterType.integer].description );
			break;
		case UI_TIER:
			break;
		case UI_TIER_MAPNAME:
			break;
		case UI_TIER_GAMETYPE:
			break;
		case UI_ALLMAPS_SELECTION:
			break;
		case UI_OPPONENT_NAME:
			break;
		case UI_KEYBINDSTATUS:
			if (Display_KeyBindPending()) {
				s = "Waiting for new key... Press ESC...";
			} else {
				s = "Press ENTER or CLICK to change, Press BACKSPACE to clear";
			}
			break;
		case UI_SERVERREFRESHDATE:
			s = UI_Cvar_VariableString(va("ui_lastServerRefresh_%i", ui_netSource.integer));
			break;
    default:
      break;
  }

	if (s) {
		return Text_Width(s, scale, 0);
	}
	return 0;
		}

static void UI_DrawBotName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	int value = uiInfo.botIndex;
	int game = trap_Cvar_VariableValue("g_gametype");
	const char *text = "";
	if (game >= GT_TEAM) {
		if (value >= uiInfo.characterCount) {
			value = 0;
		}
		text = uiInfo.characterList[value].name;
	} else {
		if (value >= UI_GetNumBots()) {
			value = 0;
		}
		text = UI_GetBotNameByNumber(value);
	}
  Text_Paint(rect->x, rect->y, scale, color, text, 0, 0, textStyle);
		}

static void UI_DrawBotSkill(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	if (uiInfo.skillIndex >= 0 && uiInfo.skillIndex < numSkillLevels) {
	  Text_Paint(rect->x, rect->y, scale, color, skillLevels[uiInfo.skillIndex], 0, 0, textStyle);
	}
		}

static void UI_DrawRedBlue(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
  Text_Paint(rect->x, rect->y, scale, color, (uiInfo.redBlue == 0) ? "Red" : "Blue", 0, 0, textStyle);
		}

#define UI_CROSSHAIR_COLOR_COUNT	27

static const vec3_t uiCrosshairPalette[UI_CROSSHAIR_COLOR_COUNT] = {
	{ 1.00f, 1.00f, 1.00f },
	{ 1.00f, 1.00f, 1.00f },
	{ 0.90f, 0.90f, 0.90f },
	{ 0.75f, 0.75f, 0.75f },
	{ 0.50f, 0.50f, 0.50f },
	{ 0.25f, 0.25f, 0.25f },
	{ 0.00f, 0.00f, 0.00f },
	{ 1.00f, 0.35f, 0.35f },
	{ 1.00f, 0.00f, 0.00f },
	{ 0.70f, 0.00f, 0.00f },
	{ 1.00f, 0.55f, 0.00f },
	{ 1.00f, 0.80f, 0.00f },
	{ 1.00f, 1.00f, 0.00f },
	{ 0.80f, 1.00f, 0.00f },
	{ 0.55f, 1.00f, 0.00f },
	{ 0.00f, 1.00f, 0.00f },
	{ 0.00f, 1.00f, 0.55f },
	{ 0.00f, 1.00f, 0.80f },
	{ 0.00f, 1.00f, 1.00f },
	{ 0.00f, 0.80f, 1.00f },
	{ 0.00f, 0.55f, 1.00f },
	{ 0.00f, 0.00f, 1.00f },
	{ 0.35f, 0.00f, 1.00f },
	{ 0.55f, 0.00f, 1.00f },
	{ 0.80f, 0.00f, 1.00f },
	{ 1.00f, 0.00f, 1.00f },
	{ 1.00f, 0.00f, 0.55f }
};

typedef struct {
	const char *token;
	const char *iconPath;
} uiStartingWeaponIconInfo_t;

#define UI_STARTING_WEAPON_ICON_COUNT	14

static const uiStartingWeaponIconInfo_t uiStartingWeaponIcons[UI_STARTING_WEAPON_ICON_COUNT] = {
	{ "g", "icons/iconw_gauntlet.tga" },
	{ "mg", "icons/iconw_machinegun.tga" },
	{ "sg", "icons/iconw_shotgun.tga" },
	{ "gl", "icons/iconw_grenade.tga" },
	{ "rl", "icons/iconw_rocket.tga" },
	{ "lg", "icons/iconw_lightning.tga" },
	{ "rg", "icons/iconw_railgun.tga" },
	{ "pg", "icons/iconw_plasma.tga" },
	{ "bfg", "icons/iconw_bfg.tga" },
	{ "gh", "icons/iconw_grapple.tga" },
	{ "ng", "icons/iconw_nailgun.tga" },
	{ "pl", "icons/iconw_proxlauncher.tga" },
	{ "cg", "icons/iconw_chaingun.tga" },
	{ "hmg", "icons/weap_hmg.tga" }
};

static qhandle_t uiStartingWeaponIconHandles[UI_STARTING_WEAPON_ICON_COUNT];
static qhandle_t uiModifiedWeaponIconHandle;
static void UI_EnsureStartingWeaponIcons( void );

/*
=============
UI_GetCrosshairColorIndex

Returns the retail palette-backed crosshair color index, defaulting to 1.
=============
*/
static int UI_GetCrosshairColorIndex( void ) {
	int index;

	index = (int)trap_Cvar_VariableValue( "cg_crosshairColor" );
	if ( index < 1 || index >= UI_CROSSHAIR_COLOR_COUNT ) {
		index = 1;
	}

	return index;
}

/*
=============
UI_GetCrosshairPreviewColor

Resolves the preview crosshair color using the retail health-color and palette rules.
=============
*/
static void UI_GetCrosshairPreviewColor( const vec4_t baseColor, vec4_t previewColor ) {
	float brightness;
	int i;

	brightness = Com_Clamp( 0.0f, 2.0f, trap_Cvar_VariableValue( "cg_crosshairBrightness" ) );
	if ( trap_Cvar_VariableValue( "cg_crosshairHealth" ) != 0.0f ) {
		VectorCopy( baseColor, previewColor );
	} else {
		VectorCopy( uiCrosshairPalette[UI_GetCrosshairColorIndex()], previewColor );
	}

	for ( i = 0; i < 3; i++ ) {
		previewColor[i] = Com_Clamp( 0.0f, 1.0f, previewColor[i] * brightness );
	}
	previewColor[3] = Com_Clamp( 0.0f, 1.0f, brightness );
}

/*
=============
UI_DrawCrosshairColor

Paints the retail crosshair color chooser using the numbered palette range.
=============
*/
static void UI_DrawCrosshairColor( rectDef_t *rect ) {
	vec4_t swatchColor;
	vec4_t outlineColor;
	float segmentWidth;
	float top;
	float x;
	int i;
	int selected;

	selected = UI_GetCrosshairColorIndex() - 1;
	segmentWidth = rect->w / (float)( UI_CROSSHAIR_COLOR_COUNT - 1 );
	if ( segmentWidth <= 0.0f ) {
		return;
	}

	top = rect->y - rect->h + ( rect->h - 12.0f );
	if ( top < rect->y - rect->h ) {
		top = rect->y - rect->h;
	}

	for ( i = 1; i < UI_CROSSHAIR_COLOR_COUNT; i++ ) {
		x = rect->x + ( i - 1 ) * segmentWidth;
		VectorCopy( uiCrosshairPalette[i], swatchColor );
		swatchColor[3] = 1.0f;
		UI_FillRect( x, top + 2.0f, segmentWidth, 8.0f, swatchColor );
	}

	outlineColor[0] = 1.0f;
	outlineColor[1] = 1.0f;
	outlineColor[2] = 1.0f;
	outlineColor[3] = 1.0f;
	_UI_DrawRect( rect->x + selected * segmentWidth, top, segmentWidth, 12.0f, 1.0f, outlineColor );
}

static void UI_DrawCrosshair(rectDef_t *rect, float scale, vec4_t color) {
	vec4_t previewColor;
	float size;
	float x;
	float y;

	if (uiInfo.currentCrosshair < 0 || uiInfo.currentCrosshair >= NUM_CROSSHAIRS) {
		uiInfo.currentCrosshair = 0;
	}

	if (uiInfo.currentCrosshair == 0) {
		return;
	}

	UI_GetCrosshairPreviewColor(color, previewColor);
	size = trap_Cvar_VariableValue("cg_crosshairSize");
	if (size < 16.0f) {
		size = 16.0f;
	}
	if (rect->w > 0.0f && size > rect->w) {
		size = rect->w;
	}
	if (rect->h > 0.0f && size > rect->h) {
		size = rect->h;
	}
	x = rect->x + (rect->w - size) * 0.5f;
	y = rect->y - rect->h + (rect->h - size) * 0.5f;

	trap_R_SetColor(previewColor);
	UI_DrawHandlePic(x, y, size, size, uiInfo.uiDC.Assets.crosshairShader[uiInfo.currentCrosshair]);
	trap_R_SetColor(NULL);
		}

/*
=============
UI_DrawAdvert

Paints the current advert shader for retail Quake Live advert ownerdraw items.
=============
*/
static void UI_DrawAdvert(rectDef_t *rect, vec4_t color, qhandle_t shader) {
	if (!rect || !shader) {
		return;
	}

	trap_R_SetColor(color);
	UI_DrawHandlePic(rect->x, rect->y, rect->w, rect->h, shader);

#ifndef Q3_VM
	{
		int pixelArea;

		// Retail UI fires the slot-83 advert callback after drawing with an opaque first token and the draw area.
		// The retail host provider is a no-op stub; the advert shader handle is the closest local proxy for that token.
		pixelArea = (int)(rect->w * rect->h);
		trap_QL_UpdateAdvert( shader, pixelArea );
	}
#endif

	trap_R_SetColor(NULL);
}

/*
=============
UI_DrawVoteString

Paints the active vote string centered within the ownerdraw rect.
=============
*/
static void UI_DrawVoteString(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	const char *voteString;
	float x;

	voteString = UI_Cvar_VariableString("ui_votestring");
	if (!voteString || !voteString[0]) {
		return;
	}

	x = rect->x + (rect->w - Text_Width(voteString, scale, 0)) * 0.5f;
	Text_Paint(x, rect->y, scale, color, voteString, 0, 0, textStyle);
}

#define UI_SERVER_SETTINGS_COLUMN_ROWS		8
#define UI_SERVER_SETTINGS_COLUMN_WIDTH	110.0f
#define UI_SERVER_SETTINGS_LINE_HEIGHT		12.0f
#define UI_SERVER_SETTINGS_COLUMN_RESET	84.0f
#define UI_SERVER_SETTINGS_ICON_SIZE		8.0f
#define UI_SERVER_SETTINGS_ICON_SPACING	12.0f
#define UI_SERVER_SETTINGS_ICON_WRAP		8
#define UI_SERVER_SETTINGS_WEAPON_MASK	CUSTOM_SETTING_WEAPON_MASK

/*
=============
UI_QLGametypeName

Returns the retail-facing gametype label used by status widgets.
=============
*/
static const char *UI_QLGametypeName( int gametype ) {
	static const char *const qlGametypeNames[GT_MAX_GAME_TYPE] = {
		"Free For All",
		"Duel",
		"Race",
		"Team Deathmatch",
		"Clan Arena",
		"Capture the Flag",
		"1-Flag CTF",
		"Overload",
		"Harvester",
		"Freeze Tag",
		"Domination",
		"Attack & Defend",
		"Red Rover"
	};

	if ( gametype < 0 || gametype >= GT_MAX_GAME_TYPE ) {
		return "Unknown Gametype";
	}

	return qlGametypeNames[gametype];
}

/*
=============
UI_GetServerSettingInt

Parses an integer field from the current serverinfo configstring payload.
=============
*/
static qboolean UI_GetServerSettingInt( const char *serverInfo, const char *key, int *valueOut ) {
	const char *valueText;

	if ( valueOut == NULL || key == NULL || key[0] == '\0' ) {
		return qfalse;
	}

	valueText = ( serverInfo != NULL ) ? Info_ValueForKey( serverInfo, key ) : "";
	if ( valueText == NULL || valueText[0] == '\0' ) {
		return qfalse;
	}

	*valueOut = atoi( valueText );
	return qtrue;
}

/*
=============
UI_GetInfoSettingInt

Parses an integer field from an info-string configstring payload.
=============
*/
static qboolean UI_GetInfoSettingInt( const char *settingsText, const char *key, int *valueOut ) {
	const char *valueText;

	if ( settingsText == NULL || key == NULL || valueOut == NULL ) {
		return qfalse;
	}

	valueText = Info_ValueForKey( settingsText, key );
	if ( valueText == NULL || valueText[0] == '\0' ) {
		return qfalse;
	}

	*valueOut = atoi( valueText );
	return qtrue;
}

/*
=============
UI_ServerSettingsWeaponHiddenForGametype

Returns whether the retail server-settings weapon strip suppresses the icon for
the active gametype.
=============
*/
static qboolean UI_ServerSettingsWeaponHiddenForGametype( unsigned int weaponBit, int gametype ) {
	if ( gametype != GT_SINGLE_PLAYER ) {
		return qfalse;
	}

	switch ( weaponBit ) {
	case CUSTOM_SETTING_SHOTGUN:
	case CUSTOM_SETTING_GRENADE_LAUNCHER:
	case CUSTOM_SETTING_ROCKET_LAUNCHER:
	case CUSTOM_SETTING_RAILGUN:
	case CUSTOM_SETTING_PLASMAGUN:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=============
UI_AdvanceServerSettingsCursor

Moves the retail settings-panel cursor forward, wrapping into the next column
after eight entries.
=============
*/
static void UI_AdvanceServerSettingsCursor( float *x, float *y, int *rowCount ) {
	if ( x == NULL || y == NULL || rowCount == NULL ) {
		return;
	}

	*rowCount += 1;
	*y += UI_SERVER_SETTINGS_LINE_HEIGHT;
	if ( *rowCount >= UI_SERVER_SETTINGS_COLUMN_ROWS ) {
		*rowCount = 0;
		*x += UI_SERVER_SETTINGS_COLUMN_WIDTH;
		*y -= UI_SERVER_SETTINGS_COLUMN_RESET;
	}
}

/*
=============
UI_DrawServerSettingsEntry

Draws one retail server-settings row and advances the layout cursor.
=============
*/
static void UI_DrawServerSettingsEntry( float *x, float *y, int *rowCount, float scale, vec4_t color, int textStyle, const char *text ) {
	if ( text == NULL || text[0] == '\0' ) {
		return;
	}

	Text_Paint( *x, *y, scale, color, text, 0, 0, textStyle );
	UI_AdvanceServerSettingsCursor( x, y, rowCount );
}

/*
=============
UI_DrawServerSettingsModifiedWeapons

Draws the retail modified-weapons icon strip for the low custom-settings mask
bits that qagame already exposes through `CS_CUSTOM_SETTINGS`.
=============
*/
static void UI_DrawServerSettingsModifiedWeapons( float x, float y, unsigned int weaponMask, int gametype ) {
	int i;
	int iconCount;
	unsigned int weaponBit;

	UI_EnsureStartingWeaponIcons();

	if ( uiModifiedWeaponIconHandle == 0 ) {
		uiModifiedWeaponIconHandle = trap_R_RegisterShaderNoMip( "icons/modified" );
		if ( uiModifiedWeaponIconHandle == 0 ) {
			uiModifiedWeaponIconHandle = trap_R_RegisterShaderNoMip( "icons/modified.png" );
		}
	}

	y += 6.0f;
	iconCount = 0;
	for ( i = 0; i < 13; i++ ) {
		weaponBit = 1u << i;
		if ( ( weaponMask & weaponBit ) == 0 ) {
			continue;
		}
		if ( UI_ServerSettingsWeaponHiddenForGametype( weaponBit, gametype ) ) {
			continue;
		}

		if ( uiStartingWeaponIconHandles[i] != 0 ) {
			UI_DrawHandlePic( x, y, UI_SERVER_SETTINGS_ICON_SIZE, UI_SERVER_SETTINGS_ICON_SIZE, uiStartingWeaponIconHandles[i] );
		}
		if ( uiModifiedWeaponIconHandle != 0 ) {
			UI_DrawHandlePic( x + 6.0f, y + 4.0f, 4.0f, 4.0f, uiModifiedWeaponIconHandle );
		}

		iconCount++;
		x += UI_SERVER_SETTINGS_ICON_SPACING;
		if ( iconCount >= UI_SERVER_SETTINGS_ICON_WRAP ) {
			iconCount = 0;
			y += UI_SERVER_SETTINGS_ICON_SPACING;
			x -= 96.0f;
		}
	}
}

/*
=============
UI_DrawServerSettings

Reconstructs the retail `UI_SERVER_SETTINGS` ownerdraw from the current server
payload surface, using serverinfo, the recovered `0x2A9`/`0x2AA` slab, and
`CS_CUSTOM_SETTINGS`.
=============
*/
static void UI_DrawServerSettings( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char serverInfo[MAX_INFO_STRING];
	char serverSettingsA[MAX_INFO_STRING];
	char serverSettingsB[MAX_INFO_STRING];
	char customSettings[MAX_INFO_STRING];
	char text[64];
	float x;
	float y;
	uint64_t customSettingsMask;
	unsigned int modifiedWeaponMask;
	int rowCount;
	int gametype;
	int value;

	if ( rect == NULL ) {
		return;
	}

	trap_GetConfigString( CS_SERVERINFO, serverInfo, sizeof( serverInfo ) );
	trap_GetConfigString( CS_SERVER_SETTINGS_INFO_A, serverSettingsA, sizeof( serverSettingsA ) );
	trap_GetConfigString( CS_SERVER_SETTINGS_INFO_B, serverSettingsB, sizeof( serverSettingsB ) );
	trap_GetConfigString( CS_CUSTOM_SETTINGS, customSettings, sizeof( customSettings ) );

	x = rect->x;
	y = rect->y;
	rowCount = 0;
	customSettingsMask = strtoull( customSettings, NULL, 10 );

	if ( !UI_GetServerSettingInt( serverInfo, "g_gametype", &gametype ) ) {
		gametype = -1;
	}
	UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, UI_QLGametypeName( gametype ) );

	if ( UI_GetServerSettingInt( serverInfo, "timelimit", &value ) ) {
		Com_sprintf( text, sizeof( text ), "Time Limit: %i", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( gametype >= 0 && gametype < GT_CLAN_ARENA &&
		UI_GetServerSettingInt( serverInfo, "fraglimit", &value ) ) {
		Com_sprintf( text, sizeof( text ), "Frag Limit: %i", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( gametype >= GT_TEAM &&
		UI_GetServerSettingInt( serverInfo, "mercylimit", &value ) &&
		value != 0 ) {
		Com_sprintf( text, sizeof( text ), "Mercy Limit: %i", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( gametype == GT_CTF &&
		UI_GetServerSettingInt( serverInfo, "capturelimit", &value ) ) {
		Com_sprintf( text, sizeof( text ), "Capture Limit: %i", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( ( gametype == GT_CLAN_ARENA || gametype == GT_FREEZE ||
		gametype == GT_ATTACK_DEFEND || gametype == GT_RED_ROVER ) &&
		UI_GetServerSettingInt( serverInfo, "roundlimit", &value ) ) {
		Com_sprintf( text, sizeof( text ), "Round Limit: %i", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( ( gametype == GT_DOMINATION || gametype == GT_ATTACK_DEFEND ) &&
		UI_GetServerSettingInt( serverInfo, "g_scorelimit", &value ) ) {
		Com_sprintf( text, sizeof( text ), "Score Limit: %i", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_AIR_CONTROL ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Air Control" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_RAMP_JUMP ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Ramp Jumping" );
	}

	if ( UI_GetInfoSettingInt( serverSettingsA, "armor_tiered", &value ) && value != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Tiered Armor" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_WEAPON_SWITCHING ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Weapon Switching" );
	}

	if ( UI_GetInfoSettingInt( serverSettingsB, "g_quadDamageFactor", &value ) && value != 3 ) {
		Com_sprintf( text, sizeof( text ), "%ix Quad", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_PHYSICS ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Physics" );
	}

	if ( UI_GetInfoSettingInt( serverSettingsB, "g_gravity", &value ) && value != 800 ) {
		Com_sprintf( text, sizeof( text ), "Gravity %i", value );
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, text );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_INSTAGIB ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "InstaGib" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_QUAD_HOG ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Quad Hog" );
	}

	if ( gametype == GT_RED_ROVER && ( customSettingsMask & CUSTOM_SETTING_INFECTED ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Infected" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_REGEN_HEALTH ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Regen Health" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_DROP_HEALTH ) != 0 &&
		 ( customSettingsMask & CUSTOM_SETTING_INSTAGIB ) == 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Drop Health" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_VAMPIRIC_DAMAGE ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Vampiric Damage" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_ITEM_SPAWNING ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Item Spawning" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_HEADSHOTS ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Headshots" );
	}

	if ( ( customSettingsMask & CUSTOM_SETTING_RAIL_JUMPING ) != 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Rail Jumping" );
	}

	modifiedWeaponMask = (unsigned int)( customSettingsMask & UI_SERVER_SETTINGS_WEAPON_MASK );
	if ( modifiedWeaponMask == 0 ) {
		UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "Default Settings" );
		return;
	}

	UI_DrawServerSettingsEntry( &x, &y, &rowCount, scale, color, textStyle, "MODIFIED WEAPONS:" );
	UI_DrawServerSettingsModifiedWeapons( x, y, modifiedWeaponMask, gametype );
}

/*
=============
UI_EnsureStartingWeaponIcons

Registers the retail starting-weapon preview icons on demand.
=============
*/
static void UI_EnsureStartingWeaponIcons( void ) {
	int i;

	for ( i = 0; i < UI_STARTING_WEAPON_ICON_COUNT; i++ ) {
		if ( uiStartingWeaponIconHandles[i] == 0 ) {
			uiStartingWeaponIconHandles[i] = trap_R_RegisterShaderNoMip( uiStartingWeaponIcons[i].iconPath );
		}
	}
}

/*
=============
UI_StartingWeaponIndexFromToken

Maps the queued-primary token to the retail starting-weapon icon ordering.
=============
*/
static int UI_StartingWeaponIndexFromToken( const char *value ) {
	char buffer[128];
	char *cursor;
	char *token;
	int i;

	if ( !value || !value[0] ) {
		return 0;
	}

	Q_strncpyz( buffer, value, sizeof( buffer ) );
	cursor = buffer;
	token = COM_ParseExt( &cursor, qtrue );
	if ( !token[0] ) {
		return 0;
	}

	for ( i = 0; i < UI_STARTING_WEAPON_ICON_COUNT; i++ ) {
		if ( !Q_stricmp( token, uiStartingWeaponIcons[i].token ) ) {
			return i + 1;
		}
	}

	if ( !Q_stricmp( token, "gauntlet" ) ) {
		return 1;
	}
	if ( !Q_stricmp( token, "machinegun" ) ) {
		return 2;
	}
	if ( !Q_stricmp( token, "shotgun" ) ) {
		return 3;
	}
	if ( !Q_stricmp( token, "grenade" ) || !Q_stricmp( token, "grenade_launcher" ) ) {
		return 4;
	}
	if ( !Q_stricmp( token, "rocket" ) || !Q_stricmp( token, "rocket_launcher" ) ) {
		return 5;
	}
	if ( !Q_stricmp( token, "lightning" ) ) {
		return 6;
	}
	if ( !Q_stricmp( token, "railgun" ) ) {
		return 7;
	}
	if ( !Q_stricmp( token, "plasma" ) || !Q_stricmp( token, "plasmagun" ) ) {
		return 8;
	}
	if ( !Q_stricmp( token, "grapple" ) || !Q_stricmp( token, "grappling_hook" ) ) {
		return 10;
	}
	if ( !Q_stricmp( token, "nailgun" ) ) {
		return 11;
	}
	if ( !Q_stricmp( token, "prox" ) || !Q_stricmp( token, "proxlauncher" ) || !Q_stricmp( token, "prox_launcher" ) ) {
		return 12;
	}
	if ( !Q_stricmp( token, "chaingun" ) ) {
		return 13;
	}
	if ( !Q_stricmp( token, "heavy_machinegun" ) ) {
		return 14;
	}

	return 0;
}

/*
=============
UI_DrawStartingWeapons

Draws the retail loadout icon strip plus the queued-primary preview.
=============
*/
static void UI_DrawStartingWeapons( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char loadoutMaskText[MAX_INFO_STRING];
	int queuedIndex;
	int i;
	float xOffset;
	float plusX;
	float plusY;
	float plusWidth;
	unsigned int loadoutMask;
	qhandle_t shader;

	if ( !rect || rect->w <= 0.0f || rect->h <= 0.0f ) {
		return;
	}

	UI_EnsureStartingWeaponIcons();
	trap_GetConfigString( CS_LOADOUT_MASK, loadoutMaskText, sizeof( loadoutMaskText ) );
	loadoutMask = loadoutMaskText[0] ? (unsigned int)strtoul( loadoutMaskText, NULL, 0 ) : 0u;
	xOffset = 0.0f;

	for ( i = 0; i < UI_STARTING_WEAPON_ICON_COUNT; i++ ) {
		if ( ( loadoutMask & ( 1u << i ) ) == 0 ) {
			continue;
		}

		shader = uiStartingWeaponIconHandles[i];
		if ( shader != 0 ) {
			trap_R_SetColor( colorWhite );
			UI_DrawHandlePic( rect->x + xOffset, rect->y, rect->w, rect->h, shader );
			trap_R_SetColor( NULL );
		}

		xOffset += rect->w * 1.5f;
	}

	if ( trap_Cvar_VariableValue( "cg_loadout" ) == 0.0f ) {
		return;
	}

	plusWidth = Text_Width( "+", scale, 0 );
	plusX = rect->x + xOffset;
	if ( plusWidth < rect->w ) {
		plusX += ( rect->w - plusWidth ) * 0.5f;
	}
	plusY = rect->y + rect->h * 0.5f + Text_Height( "+", scale, 0 ) * 0.5f;
	Text_Paint( plusX, plusY, scale, color, "+", 0, 0, textStyle );

	queuedIndex = UI_StartingWeaponIndexFromToken( UI_Cvar_VariableString( "cg_weaponPrimaryQueued" ) );
	if ( queuedIndex <= 0 || queuedIndex > UI_STARTING_WEAPON_ICON_COUNT ) {
		queuedIndex = UI_STARTING_WEAPON_ICON_COUNT;
	}

	shader = uiStartingWeaponIconHandles[queuedIndex - 1];
	if ( shader != 0 ) {
		trap_R_SetColor( colorWhite );
		UI_DrawHandlePic( rect->x + xOffset + rect->w, rect->y, rect->w, rect->h, shader );
		trap_R_SetColor( NULL );
	}
}

#define UI_NEXTMAP_CONFIGSTRING	0x29A

/*
=============
UI_GetNextMapText

Fetches the retail next-map label from the undocumented configstring slot used
by `UI_DrawNextMap`, then falls back to the mirrored rotation preview payload
when the direct slot is not populated yet.
=============
*/
static const char *UI_GetNextMapText( void ) {
	static char nextMapText[MAX_INFO_STRING];
	char rotationTitles[MAX_INFO_STRING];
	const char *valueText;

	nextMapText[0] = '\0';
	trap_GetConfigString( UI_NEXTMAP_CONFIGSTRING, nextMapText, sizeof( nextMapText ) );
	if ( nextMapText[0] != '\0' ) {
		return nextMapText;
	}

	trap_GetConfigString( CS_ROTATION_TITLES, rotationTitles, sizeof( rotationTitles ) );
	valueText = Info_ValueForKey( rotationTitles, "title_0" );
	if ( valueText == NULL || valueText[0] == '\0' ) {
		valueText = Info_ValueForKey( rotationTitles, "map_0" );
	}
	if ( valueText != NULL && valueText[0] != '\0' ) {
		Q_strncpyz( nextMapText, valueText, sizeof( nextMapText ) );
		return nextMapText;
	}

	return "";
}

/*
=============
UI_DrawNextMap

Restores the retail `UI_NEXTMAP` ownerdraw by painting the next-map label from
the same configstring seam used by the native UI, with the mirrored rotation
payload as the only compatibility fallback.
=============
*/
static void UI_DrawNextMap( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	const char *nextMapText;

	if ( rect == NULL ) {
		return;
	}

	nextMapText = UI_GetNextMapText();
	if ( nextMapText == NULL || nextMapText[0] == '\0' ) {
		return;
	}

	Text_Paint( rect->x, rect->y, scale, color, nextMapText, 0, 0, textStyle );
}



/*
===============
UI_BuildPlayerList
===============
*/
static void UI_BuildPlayerList() {
	uiClientState_t	cs;
	int		n, count, team, team2, playerTeamNumber;
	char	info[MAX_INFO_STRING];

	trap_GetClientState( &cs );
	trap_GetConfigString( CS_PLAYERS + cs.clientNum, info, MAX_INFO_STRING );
	uiInfo.playerNumber = cs.clientNum;
	uiInfo.teamLeader = atoi(Info_ValueForKey(info, "tl"));
	team = atoi(Info_ValueForKey(info, "t"));
	trap_GetConfigString( CS_SERVERINFO, info, sizeof(info) );
	count = atoi( Info_ValueForKey( info, "sv_maxclients" ) );
	uiInfo.playerCount = 0;
	uiInfo.myTeamCount = 0;
	playerTeamNumber = 0;
	for( n = 0; n < count; n++ ) {
		trap_GetConfigString( CS_PLAYERS + n, info, MAX_INFO_STRING );

		if (info[0]) {
			Q_strncpyz( uiInfo.playerNames[uiInfo.playerCount], Info_ValueForKey( info, "n" ), MAX_NAME_LENGTH );
			Q_CleanStr( uiInfo.playerNames[uiInfo.playerCount] );
			uiInfo.playerCount++;
			team2 = atoi(Info_ValueForKey(info, "t"));
			if (team2 == team) {
				Q_strncpyz( uiInfo.teamNames[uiInfo.myTeamCount], Info_ValueForKey( info, "n" ), MAX_NAME_LENGTH );
				Q_CleanStr( uiInfo.teamNames[uiInfo.myTeamCount] );
				uiInfo.teamClientNums[uiInfo.myTeamCount] = n;
				if (uiInfo.playerNumber == n) {
					playerTeamNumber = uiInfo.myTeamCount;
				}
				uiInfo.myTeamCount++;
			}
		}
	}

	if (!uiInfo.teamLeader) {
		trap_Cvar_Set("cg_selectedPlayer", va("%d", playerTeamNumber));
	}

	n = trap_Cvar_VariableValue("cg_selectedPlayer");
	if (n < 0 || n > uiInfo.myTeamCount) {
		n = 0;
	}
	if (n < uiInfo.myTeamCount) {
		trap_Cvar_Set("cg_selectedPlayerName", uiInfo.teamNames[n]);
	}
		}


static void UI_DrawSelectedPlayer(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	if (uiInfo.uiDC.realTime > uiInfo.playerRefresh) {
		uiInfo.playerRefresh = uiInfo.uiDC.realTime + 3000;
		UI_BuildPlayerList();
	}
  Text_Paint(rect->x, rect->y, scale, color, (uiInfo.teamLeader) ? UI_Cvar_VariableString("cg_selectedPlayerName") : UI_Cvar_VariableString("name") , 0, 0, textStyle);
		}

static void UI_DrawServerRefreshDate(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	if (uiInfo.serverStatus.refreshActive) {
		vec4_t lowLight, newColor;
		lowLight[0] = 0.8 * color[0]; 
		lowLight[1] = 0.8 * color[1]; 
		lowLight[2] = 0.8 * color[2]; 
		lowLight[3] = 0.8 * color[3]; 
		LerpColor(color,lowLight,newColor,0.5+0.5*sin(uiInfo.uiDC.realTime / PULSE_DIVISOR));
	  Text_Paint(rect->x, rect->y, scale, newColor, va("Getting info for %d servers (ESC to cancel)", trap_LAN_GetServerCount(ui_netSource.integer)), 0, 0, textStyle);
	} else {
		char buff[64];
		Q_strncpyz(buff, UI_Cvar_VariableString(va("ui_lastServerRefresh_%i", ui_netSource.integer)), 64);
	  Text_Paint(rect->x, rect->y, scale, color, va("Refresh Time: %s", buff), 0, 0, textStyle);
	}
		}

static void UI_DrawServerMOTD(rectDef_t *rect, float scale, vec4_t color) {
	if (uiInfo.serverStatus.motdLen) {
		float maxX;
	 
		if (uiInfo.serverStatus.motdWidth == -1) {
			uiInfo.serverStatus.motdWidth = 0;
			uiInfo.serverStatus.motdPaintX = rect->x + 1;
			uiInfo.serverStatus.motdPaintX2 = -1;
		}

		if (uiInfo.serverStatus.motdOffset > uiInfo.serverStatus.motdLen) {
			uiInfo.serverStatus.motdOffset = 0;
			uiInfo.serverStatus.motdPaintX = rect->x + 1;
			uiInfo.serverStatus.motdPaintX2 = -1;
		}

		if (uiInfo.uiDC.realTime > uiInfo.serverStatus.motdTime) {
			uiInfo.serverStatus.motdTime = uiInfo.uiDC.realTime + 10;
			if (uiInfo.serverStatus.motdPaintX <= rect->x + 2) {
				if (uiInfo.serverStatus.motdOffset < uiInfo.serverStatus.motdLen) {
					uiInfo.serverStatus.motdPaintX += Text_Width(&uiInfo.serverStatus.motd[uiInfo.serverStatus.motdOffset], scale, 1) - 1;
					uiInfo.serverStatus.motdOffset++;
				} else {
					uiInfo.serverStatus.motdOffset = 0;
					if (uiInfo.serverStatus.motdPaintX2 >= 0) {
						uiInfo.serverStatus.motdPaintX = uiInfo.serverStatus.motdPaintX2;
					} else {
						uiInfo.serverStatus.motdPaintX = rect->x + rect->w - 2;
					}
					uiInfo.serverStatus.motdPaintX2 = -1;
				}
			} else {
				//serverStatus.motdPaintX--;
				uiInfo.serverStatus.motdPaintX -= 2;
				if (uiInfo.serverStatus.motdPaintX2 >= 0) {
					//serverStatus.motdPaintX2--;
					uiInfo.serverStatus.motdPaintX2 -= 2;
				}
			}
		}

		maxX = rect->x + rect->w - 2;
		Text_Paint_Limit(&maxX, uiInfo.serverStatus.motdPaintX, rect->y + rect->h - 3, scale, color, &uiInfo.serverStatus.motd[uiInfo.serverStatus.motdOffset], 0, 0); 
		if (uiInfo.serverStatus.motdPaintX2 >= 0) {
			float maxX2 = rect->x + rect->w - 2;
			Text_Paint_Limit(&maxX2, uiInfo.serverStatus.motdPaintX2, rect->y + rect->h - 3, scale, color, uiInfo.serverStatus.motd, 0, uiInfo.serverStatus.motdOffset); 
		}
		if (uiInfo.serverStatus.motdOffset && maxX > 0) {
			// if we have an offset ( we are skipping the first part of the string ) and we fit the string
			if (uiInfo.serverStatus.motdPaintX2 == -1) {
						uiInfo.serverStatus.motdPaintX2 = rect->x + rect->w - 2;
			}
		} else {
			uiInfo.serverStatus.motdPaintX2 = -1;
		}

	}
		}

static void UI_DrawKeyBindStatus(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
//	int ofs = 0; TTimo: unused
	if (Display_KeyBindPending()) {
		Text_Paint(rect->x, rect->y, scale, color, "Waiting for new key... Press ESC...", 0, 0, textStyle);
	} else {
		Text_Paint(rect->x, rect->y, scale, color, "Press ENTER or CLICK to change, Press BACKSPACE to clear", 0, 0, textStyle);
	}
		}

static void UI_DrawGLInfo(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char * eptr;
	char buff[1024];
	const char *lines[64];
	int y, numLines, i;

	Text_Paint(rect->x + 2, rect->y, scale, color, va("VENDOR: %s", uiInfo.uiDC.glconfig.vendor_string), 0, 30, textStyle);
	Text_Paint(rect->x + 2, rect->y + 15, scale, color, va("VERSION: %s: %s", uiInfo.uiDC.glconfig.version_string,uiInfo.uiDC.glconfig.renderer_string), 0, 30, textStyle);
	Text_Paint(rect->x + 2, rect->y + 30, scale, color, va ("PIXELFORMAT: color(%d-bits) Z(%d-bits) stencil(%d-bits)", uiInfo.uiDC.glconfig.colorBits, uiInfo.uiDC.glconfig.depthBits, uiInfo.uiDC.glconfig.stencilBits), 0, 30, textStyle);

	// build null terminated extension strings
  // TTimo: https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=399
  // in TA this was not directly crashing, but displaying a nasty broken shader right in the middle
  // brought down the string size to 1024, there's not much that can be shown on the screen anyway
	Q_strncpyz(buff, uiInfo.uiDC.glconfig.extensions_string, 1024);
	eptr = buff;
	y = rect->y + 45;
	numLines = 0;
	while ( y < rect->y + rect->h && *eptr )
	{
		while ( *eptr && *eptr == ' ' )
			*eptr++ = '\0';

		// track start of valid string
		if (*eptr && *eptr != ' ') {
			lines[numLines++] = eptr;
		}

		while ( *eptr && *eptr != ' ' )
			eptr++;
	}

	i = 0;
	while (i < numLines) {
		Text_Paint(rect->x + 2, y, scale, color, lines[i++], 0, 20, textStyle);
		if (i < numLines) {
			Text_Paint(rect->x + rect->w / 2, y, scale, color, lines[i++], 0, 20, textStyle);
		}
		y += 10;
		if (y > rect->y + rect->h - 11) {
			break;
		}
	}


		}

// FIXME: table drive
//
static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	rectDef_t rect;

  rect.x = x + text_x;
  rect.y = y + text_y;
  rect.w = w;
  rect.h = h;

  switch (ownerDraw) {
    case UI_HANDICAP:
      UI_DrawHandicap(&rect, scale, color, textStyle);
      break;
    case UI_EFFECTS:
      UI_DrawEffects(&rect, scale, color);
      break;
    case UI_PLAYERMODEL:
      UI_DrawPlayerModel(&rect);
      break;
    case UI_CLANNAME:
      UI_DrawClanName(&rect, scale, color, textStyle);
      break;
    case UI_CLANLOGO:
      UI_DrawClanLogo(&rect, scale, color);
      break;
    case UI_CLANCINEMATIC:
      UI_DrawClanCinematic(&rect, scale, color);
      break;
    case UI_PREVIEWCINEMATIC:
      UI_DrawPreviewCinematic(&rect, scale, color);
      break;
    case UI_GAMETYPE:
      UI_DrawGameType(&rect, scale, color, textStyle);
      break;
    case UI_NETGAMETYPE:
      UI_DrawNetGameType(&rect, scale, color, textStyle);
      break;
    case UI_JOINGAMETYPE:
	  UI_DrawJoinGameType(&rect, scale, color, textStyle);
	  break;
    case UI_MAPPREVIEW:
      UI_DrawMapPreview(&rect, scale, color, qtrue);
      break;
    case UI_MAP_TIMETOBEAT:
      UI_DrawMapTimeToBeat(&rect, scale, color, textStyle);
      break;
    case UI_MAPCINEMATIC:
      UI_DrawMapCinematic(&rect, scale, color, qfalse);
      break;
    case UI_STARTMAPCINEMATIC:
      UI_DrawMapCinematic(&rect, scale, color, qtrue);
      break;
    case UI_SKILL:
      UI_DrawSkill(&rect, scale, color, textStyle);
      break;
    case UI_BLUETEAMNAME:
      UI_DrawTeamName(&rect, scale, color, qtrue, textStyle);
      break;
    case UI_REDTEAMNAME:
      UI_DrawTeamName(&rect, scale, color, qfalse, textStyle);
      break;
    case UI_BLUETEAM1:
		case UI_BLUETEAM2:
		case UI_BLUETEAM3:
		case UI_BLUETEAM4:
		case UI_BLUETEAM5:
      UI_DrawTeamMember(&rect, scale, color, qtrue, ownerDraw - UI_BLUETEAM1 + 1, textStyle);
      break;
    case UI_REDTEAM1:
		case UI_REDTEAM2:
		case UI_REDTEAM3:
		case UI_REDTEAM4:
		case UI_REDTEAM5:
      UI_DrawTeamMember(&rect, scale, color, qfalse, ownerDraw - UI_REDTEAM1 + 1, textStyle);
      break;
		case UI_NETSOURCE:
      UI_DrawNetSource(&rect, scale, color, textStyle);
			break;
    case UI_NETMAPPREVIEW:
      UI_DrawNetMapPreview(&rect, scale, color);
      break;
    case UI_NETMAPCINEMATIC:
      UI_DrawNetMapCinematic(&rect, scale, color);
      break;
		case UI_NETFILTER:
      UI_DrawNetFilter(&rect, scale, color, textStyle);
			break;
		case UI_TIER:
			UI_DrawTier(&rect, scale, color, textStyle);
			break;
		case UI_OPPONENTMODEL:
			UI_DrawOpponent(&rect);
			break;
		case UI_TIERMAP1:
			UI_DrawTierMap(&rect, 0);
			break;
		case UI_TIERMAP2:
			UI_DrawTierMap(&rect, 1);
			break;
		case UI_TIERMAP3:
			UI_DrawTierMap(&rect, 2);
			break;
		case UI_PLAYERLOGO:
			UI_DrawPlayerLogo(&rect, color);
			break;
		case UI_PLAYERLOGO_METAL:
			UI_DrawPlayerLogoMetal(&rect, color);
			break;
		case UI_PLAYERLOGO_NAME:
			UI_DrawPlayerLogoName(&rect, color);
			break;
		case UI_OPPONENTLOGO:
			UI_DrawOpponentLogo(&rect, color);
			break;
		case UI_OPPONENTLOGO_METAL:
			UI_DrawOpponentLogoMetal(&rect, color);
			break;
		case UI_OPPONENTLOGO_NAME:
			UI_DrawOpponentLogoName(&rect, color);
			break;
		case UI_TIER_MAPNAME:
			UI_DrawTierMapName(&rect, scale, color, textStyle);
			break;
		case UI_TIER_GAMETYPE:
			UI_DrawTierGameType(&rect, scale, color, textStyle);
			break;
		case UI_ALLMAPS_SELECTION:
			UI_DrawAllMapsSelection(&rect, scale, color, textStyle, qtrue);
			break;
		case UI_MAPS_SELECTION:
			UI_DrawAllMapsSelection(&rect, scale, color, textStyle, qfalse);
			break;
		case UI_OPPONENT_NAME:
			UI_DrawOpponentName(&rect, scale, color, textStyle);
			break;
		case UI_BOTNAME:
			UI_DrawBotName(&rect, scale, color, textStyle);
			break;
		case UI_BOTSKILL:
			UI_DrawBotSkill(&rect, scale, color, textStyle);
			break;
		case UI_REDBLUE:
			UI_DrawRedBlue(&rect, scale, color, textStyle);
			break;
		case UI_CROSSHAIR:
			UI_DrawCrosshair(&rect, scale, color);
			break;
		case UI_CROSSHAIR_COLOR:
			UI_DrawCrosshairColor(&rect);
			break;
		case UI_ADVERT:
			UI_DrawAdvert(&rect, color, shader);
			break;
		case UI_NEXTMAP:
			UI_DrawNextMap(&rect, scale, color, textStyle);
			break;
		case UI_SELECTEDPLAYER:
			UI_DrawSelectedPlayer(&rect, scale, color, textStyle);
			break;
		case UI_VOTESTRING:
			UI_DrawVoteString(&rect, scale, color, textStyle);
			break;
		case UI_SERVER_SETTINGS:
			UI_DrawServerSettings(&rect, scale, color, textStyle);
			break;
		case UI_STARTING_WEAPONS:
			UI_DrawStartingWeapons(&rect, scale, color, textStyle);
			break;
		case UI_SERVERREFRESHDATE:
			UI_DrawServerRefreshDate(&rect, scale, color, textStyle);
			break;
		case UI_SERVERMOTD:
			UI_DrawServerMOTD(&rect, scale, color);
			break;
		case UI_GLINFO:
			UI_DrawGLInfo(&rect,scale, color, textStyle);
			break;
		case UI_KEYBINDSTATUS:
			UI_DrawKeyBindStatus(&rect,scale, color, textStyle);
			break;
    default:
      break;
  }

		}

static qboolean UI_OwnerDrawVisible(int flags) {
	qboolean vis = qtrue;

	while (flags) {

		if (flags & UI_SHOW_FFA) {
			if (trap_Cvar_VariableValue("g_gametype") != GT_FFA) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_FFA;
		}

		if (flags & UI_SHOW_NOTFFA) {
			if (trap_Cvar_VariableValue("g_gametype") == GT_FFA) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_NOTFFA;
		}

		if (flags & UI_SHOW_LEADER) {
			// these need to show when this client can give orders to a player or a group
			if (!uiInfo.teamLeader) {
				vis = qfalse;
			} else {
				// if showing yourself
				if (ui_selectedPlayer.integer < uiInfo.myTeamCount && uiInfo.teamClientNums[ui_selectedPlayer.integer] == uiInfo.playerNumber) { 
					vis = qfalse;
				}
			}
			flags &= ~UI_SHOW_LEADER;
		} 
		if (flags & UI_SHOW_NOTLEADER) {
			// these need to show when this client is assigning their own status or they are NOT the leader
			if (uiInfo.teamLeader) {
				// if not showing yourself
				if (!(ui_selectedPlayer.integer < uiInfo.myTeamCount && uiInfo.teamClientNums[ui_selectedPlayer.integer] == uiInfo.playerNumber)) { 
					vis = qfalse;
				}
				// these need to show when this client can give orders to a player or a group
			}
			flags &= ~UI_SHOW_NOTLEADER;
		} 
		if (flags & UI_SHOW_FAVORITESERVERS) {
			// this assumes you only put this type of display flag on something showing in the proper context
			if (ui_netSource.integer != AS_FAVORITES) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_FAVORITESERVERS;
		} 
		if (flags & UI_SHOW_NOTFAVORITESERVERS) {
			// this assumes you only put this type of display flag on something showing in the proper context
			if (ui_netSource.integer == AS_FAVORITES) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_NOTFAVORITESERVERS;
		} 
		if (flags & UI_SHOW_ANYTEAMGAME) {
			if (uiInfo.gameTypes[ui_gameType.integer].gtEnum <= GT_TEAM ) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_ANYTEAMGAME;
		} 
		if (flags & UI_SHOW_ANYNONTEAMGAME) {
			if (uiInfo.gameTypes[ui_gameType.integer].gtEnum > GT_TEAM ) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_ANYNONTEAMGAME;
		} 
		if (flags & UI_SHOW_NETANYTEAMGAME) {
			if (uiInfo.gameTypes[ui_netGameType.integer].gtEnum <= GT_TEAM ) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_NETANYTEAMGAME;
		} 
		if (flags & UI_SHOW_NETANYNONTEAMGAME) {
			if (uiInfo.gameTypes[ui_netGameType.integer].gtEnum > GT_TEAM ) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_NETANYNONTEAMGAME;
		} 
		if (flags & UI_SHOW_NEWHIGHSCORE) {
			if (uiInfo.newHighScoreTime < uiInfo.uiDC.realTime) {
				vis = qfalse;
			} else {
				if (uiInfo.soundHighScore) {
					if (trap_Cvar_VariableValue("sv_killserver") == 0) {
						// wait on server to go down before playing sound
						trap_S_StartLocalSound(uiInfo.newHighScoreSound, CHAN_ANNOUNCER);
						uiInfo.soundHighScore = qfalse;
					}
				}
			}
			flags &= ~UI_SHOW_NEWHIGHSCORE;
		} 
		if (flags & UI_SHOW_NEWBESTTIME) {
			if (uiInfo.newBestTime < uiInfo.uiDC.realTime) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_NEWBESTTIME;
		} 
		if (flags & UI_SHOW_DEMOAVAILABLE) {
			if (!uiInfo.demoAvailable) {
				vis = qfalse;
			}
			flags &= ~UI_SHOW_DEMOAVAILABLE;
		} else {
			flags = 0;
		}
	}
  return vis;
		}

static qboolean UI_Handicap_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
    int h;
    h = Com_Clamp( 5, 100, trap_Cvar_VariableValue("handicap") );
		if (key == K_MOUSE2) {
	    h -= 5;
		} else {
	    h += 5;
		}
    if (h > 100) {
      h = 5;
    } else if (h < 0) {
			h = 100;
		}
  	trap_Cvar_Set( "handicap", va( "%i", h) );
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_Effects_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {

		if (key == K_MOUSE2) {
	    uiInfo.effectsColor--;
		} else {
	    uiInfo.effectsColor++;
		}

    if( uiInfo.effectsColor > 6 ) {
	  	uiInfo.effectsColor = 0;
		} else if (uiInfo.effectsColor < 0) {
	  	uiInfo.effectsColor = 6;
		}

	  trap_Cvar_SetValue( "color1", uitogamecode[uiInfo.effectsColor] );
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_ClanName_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
    int i;
    i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
		if (uiInfo.teamList[i].cinematic >= 0) {
		  trap_CIN_StopCinematic(uiInfo.teamList[i].cinematic);
			uiInfo.teamList[i].cinematic = -1;
		}
		if (key == K_MOUSE2) {
	    i--;
		} else {
	    i++;
		}
    if (i >= uiInfo.teamCount) {
      i = 0;
    } else if (i < 0) {
			i = uiInfo.teamCount - 1;
		}
  	trap_Cvar_Set( "ui_teamName", uiInfo.teamList[i].teamName);
	UI_HeadCountByTeam();
	UI_FeederSelection(FEEDER_HEADS, 0);
	updateModel = qtrue;
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_GameType_HandleKey(int flags, float *special, int key, qboolean resetMap) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		int oldCount = UI_MapCountByGameType(qtrue);

		// hard coded mess here
		if (key == K_MOUSE2) {
			ui_gameType.integer--;
			if (ui_gameType.integer == 2) {
				ui_gameType.integer = 1;
			} else if (ui_gameType.integer < 2) {
				ui_gameType.integer = uiInfo.numGameTypes - 1;
			}
		} else {
			ui_gameType.integer++;
			if (ui_gameType.integer >= uiInfo.numGameTypes) {
				ui_gameType.integer = 1;
			} else if (ui_gameType.integer == 2) {
				ui_gameType.integer = 3;
			}
		}
    
		if (uiInfo.gameTypes[ui_gameType.integer].gtEnum == GT_TOURNAMENT) {
			trap_Cvar_Set("ui_Q3Model", "1");
		} else {
			trap_Cvar_Set("ui_Q3Model", "0");
		}

		trap_Cvar_Set("ui_gameType", va("%d", ui_gameType.integer));
		UI_SetCapFragLimits(qtrue);
		UI_LoadBestScores(uiInfo.mapList[ui_currentMap.integer].mapLoadName, uiInfo.gameTypes[ui_gameType.integer].gtEnum);
		if (resetMap && oldCount != UI_MapCountByGameType(qtrue)) {
	  	trap_Cvar_Set( "ui_currentMap", "0");
			Menu_SetFeederSelection(NULL, FEEDER_MAPS, 0, NULL);
		}
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_NetGameType_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {

		if (key == K_MOUSE2) {
			ui_netGameType.integer--;
		} else {
			ui_netGameType.integer++;
		}

    if (ui_netGameType.integer < 0) {
      ui_netGameType.integer = uiInfo.numGameTypes - 1;
		} else if (ui_netGameType.integer >= uiInfo.numGameTypes) {
      ui_netGameType.integer = 0;
    } 

  	trap_Cvar_Set( "ui_netGameType", va("%d", ui_netGameType.integer));
  	trap_Cvar_Set( "ui_actualnetGameType", va("%d", uiInfo.gameTypes[ui_netGameType.integer].gtEnum));
  	trap_Cvar_Set( "ui_currentNetMap", "0");
		UI_MapCountByGameType(qfalse);
		Menu_SetFeederSelection(NULL, FEEDER_ALLMAPS, 0, NULL);
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_JoinGameType_HandleKey(int flags, float *special, int key) {
	if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {

		if (key == K_MOUSE2) {
			ui_joinGameType.integer--;
		} else {
			ui_joinGameType.integer++;
		}

		if (ui_joinGameType.integer < 0) {
			ui_joinGameType.integer = uiInfo.numJoinGameTypes - 1;
		} else if (ui_joinGameType.integer >= uiInfo.numJoinGameTypes) {
			ui_joinGameType.integer = 0;
		}

		trap_Cvar_Set( "ui_joinGameType", va("%d", ui_joinGameType.integer));
		UI_BuildServerDisplayList(qtrue);
		return qtrue;
	}
	return qfalse;
		}



static qboolean UI_Skill_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
  	int i = trap_Cvar_VariableValue( "g_spSkill" );

		if (key == K_MOUSE2) {
	    i--;
		} else {
	    i++;
		}

    if (i < 1) {
			i = numSkillLevels;
		} else if (i > numSkillLevels) {
      i = 1;
    }

    trap_Cvar_Set("g_spSkill", va("%i", i));
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_TeamName_HandleKey(int flags, float *special, int key, qboolean blue) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
    int i;
    i = UI_TeamIndexFromName(UI_Cvar_VariableString((blue) ? "ui_blueTeam" : "ui_redTeam"));

		if (key == K_MOUSE2) {
	    i--;
		} else {
	    i++;
		}

    if (i >= uiInfo.teamCount) {
      i = 0;
    } else if (i < 0) {
			i = uiInfo.teamCount - 1;
		}

    trap_Cvar_Set( (blue) ? "ui_blueTeam" : "ui_redTeam", uiInfo.teamList[i].teamName);

    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_TeamMember_HandleKey(int flags, float *special, int key, qboolean blue, int num) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		// 0 - None
		// 1 - Human
		// 2..NumCharacters - Bot
		char *cvar = va(blue ? "ui_blueteam%i" : "ui_redteam%i", num);
		int value = trap_Cvar_VariableValue(cvar);

		if (key == K_MOUSE2) {
			value--;
		} else {
			value++;
		}

		if (ui_actualNetGameType.integer >= GT_TEAM) {
			if (value >= uiInfo.characterCount + 2) {
				value = 0;
			} else if (value < 0) {
				value = uiInfo.characterCount + 2 - 1;
			}
		} else {
			if (value >= UI_GetNumBots() + 2) {
				value = 0;
			} else if (value < 0) {
				value = UI_GetNumBots() + 2 - 1;
			}
		}

		trap_Cvar_Set(cvar, va("%i", value));
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_NetSource_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		
		if (key == K_MOUSE2) {
			ui_netSource.integer--;
			if (ui_netSource.integer == AS_MPLAYER)
				ui_netSource.integer--;
		} else {
			ui_netSource.integer++;
			if (ui_netSource.integer == AS_MPLAYER)
				ui_netSource.integer++;
		}
    
		if (ui_netSource.integer >= numNetSources) {
      ui_netSource.integer = 0;
    } else if (ui_netSource.integer < 0) {
      ui_netSource.integer = numNetSources - 1;
		}

		UI_BuildServerDisplayList(qtrue);
		if (ui_netSource.integer != AS_GLOBAL) {
			UI_StartServerRefresh(qtrue);
		}
  	trap_Cvar_Set( "ui_netSource", va("%d", ui_netSource.integer));
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_NetFilter_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {

		if (key == K_MOUSE2) {
			ui_serverFilterType.integer--;
		} else {
			ui_serverFilterType.integer++;
		}

    if (ui_serverFilterType.integer >= numServerFilters) {
      ui_serverFilterType.integer = 0;
    } else if (ui_serverFilterType.integer < 0) {
      ui_serverFilterType.integer = numServerFilters - 1;
		}
		UI_BuildServerDisplayList(qtrue);
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_OpponentName_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		if (key == K_MOUSE2) {
			UI_PriorOpponent();
		} else {
			UI_NextOpponent();
		}
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_BotName_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		int game = trap_Cvar_VariableValue("g_gametype");
		int value = uiInfo.botIndex;

		if (key == K_MOUSE2) {
			value--;
		} else {
			value++;
		}

		if (game >= GT_TEAM) {
			if (value >= uiInfo.characterCount + 2) {
				value = 0;
			} else if (value < 0) {
				value = uiInfo.characterCount + 2 - 1;
			}
		} else {
			if (value >= UI_GetNumBots() + 2) {
				value = 0;
			} else if (value < 0) {
				value = UI_GetNumBots() + 2 - 1;
			}
		}
		uiInfo.botIndex = value;
    return qtrue;
  }
  return qfalse;
		}

static qboolean UI_BotSkill_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		if (key == K_MOUSE2) {
			uiInfo.skillIndex--;
		} else {
			uiInfo.skillIndex++;
		}
		if (uiInfo.skillIndex >= numSkillLevels) {
			uiInfo.skillIndex = 0;
		} else if (uiInfo.skillIndex < 0) {
			uiInfo.skillIndex = numSkillLevels-1;
		}
    return qtrue;
  }
	return qfalse;
		}

static qboolean UI_RedBlue_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		uiInfo.redBlue ^= 1;
		return qtrue;
	}
	return qfalse;
		}

static qboolean UI_Crosshair_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		if (key == K_MOUSE2) {
			uiInfo.currentCrosshair--;
		} else {
			uiInfo.currentCrosshair++;
		}

		if (uiInfo.currentCrosshair >= NUM_CROSSHAIRS) {
			uiInfo.currentCrosshair = 0;
		} else if (uiInfo.currentCrosshair < 0) {
			uiInfo.currentCrosshair = NUM_CROSSHAIRS - 1;
		}
		trap_Cvar_Set("cg_drawCrosshair", va("%d", uiInfo.currentCrosshair)); 
		return qtrue;
	}
	return qfalse;
		}

/*
=============
UI_CrosshairColor_HandleKey

Advances the retail numbered crosshair color palette.
=============
*/
static qboolean UI_CrosshairColor_HandleKey(int flags, float *special, int key) {
	int colorIndex;

	if (key != K_MOUSE1 && key != K_MOUSE2 && key != K_ENTER && key != K_KP_ENTER) {
		return qfalse;
	}

	colorIndex = UI_GetCrosshairColorIndex();
	if (key == K_MOUSE2) {
		colorIndex--;
	} else {
		colorIndex++;
	}

	if (colorIndex >= UI_CROSSHAIR_COLOR_COUNT) {
		colorIndex = 1;
	} else if (colorIndex < 1) {
		colorIndex = UI_CROSSHAIR_COLOR_COUNT - 1;
	}

	trap_Cvar_Set("cg_crosshairColor", va("%d", colorIndex));
	return qtrue;
}



static qboolean UI_SelectedPlayer_HandleKey(int flags, float *special, int key) {
  if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {
		int selected;

		UI_BuildPlayerList();
		if (!uiInfo.teamLeader) {
			return qfalse;
		}
		selected = trap_Cvar_VariableValue("cg_selectedPlayer");
		
		if (key == K_MOUSE2) {
			selected--;
		} else {
			selected++;
		}

		if (selected > uiInfo.myTeamCount) {
			selected = 0;
		} else if (selected < 0) {
			selected = uiInfo.myTeamCount;
		}

		if (selected == uiInfo.myTeamCount) {
		 	trap_Cvar_Set( "cg_selectedPlayerName", "Everyone");
		} else {
		 	trap_Cvar_Set( "cg_selectedPlayerName", uiInfo.teamNames[selected]);
		}
	 	trap_Cvar_Set( "cg_selectedPlayer", va("%d", selected));
	}
	return qfalse;
		}


static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {
  switch (ownerDraw) {
    case UI_HANDICAP:
      return UI_Handicap_HandleKey(flags, special, key);
      break;
    case UI_EFFECTS:
      return UI_Effects_HandleKey(flags, special, key);
      break;
    case UI_CLANNAME:
      return UI_ClanName_HandleKey(flags, special, key);
      break;
    case UI_GAMETYPE:
      return UI_GameType_HandleKey(flags, special, key, qtrue);
      break;
    case UI_NETGAMETYPE:
      return UI_NetGameType_HandleKey(flags, special, key);
      break;
    case UI_JOINGAMETYPE:
      return UI_JoinGameType_HandleKey(flags, special, key);
      break;
    case UI_SKILL:
      return UI_Skill_HandleKey(flags, special, key);
      break;
    case UI_BLUETEAMNAME:
      return UI_TeamName_HandleKey(flags, special, key, qtrue);
      break;
    case UI_REDTEAMNAME:
      return UI_TeamName_HandleKey(flags, special, key, qfalse);
      break;
    case UI_BLUETEAM1:
		case UI_BLUETEAM2:
		case UI_BLUETEAM3:
		case UI_BLUETEAM4:
		case UI_BLUETEAM5:
      UI_TeamMember_HandleKey(flags, special, key, qtrue, ownerDraw - UI_BLUETEAM1 + 1);
      break;
    case UI_REDTEAM1:
		case UI_REDTEAM2:
		case UI_REDTEAM3:
		case UI_REDTEAM4:
		case UI_REDTEAM5:
      UI_TeamMember_HandleKey(flags, special, key, qfalse, ownerDraw - UI_REDTEAM1 + 1);
      break;
		case UI_NETSOURCE:
      UI_NetSource_HandleKey(flags, special, key);
			break;
		case UI_NETFILTER:
      UI_NetFilter_HandleKey(flags, special, key);
			break;
		case UI_OPPONENT_NAME:
			UI_OpponentName_HandleKey(flags, special, key);
			break;
		case UI_BOTNAME:
			return UI_BotName_HandleKey(flags, special, key);
			break;
		case UI_BOTSKILL:
			return UI_BotSkill_HandleKey(flags, special, key);
			break;
		case UI_REDBLUE:
			UI_RedBlue_HandleKey(flags, special, key);
			break;
		case UI_CROSSHAIR:
			UI_Crosshair_HandleKey(flags, special, key);
			break;
		case UI_CROSSHAIR_COLOR:
			return UI_CrosshairColor_HandleKey(flags, special, key);
			break;
		case UI_SELECTEDPLAYER:
			UI_SelectedPlayer_HandleKey(flags, special, key);
			break;
    default:
      break;
  }

  return qfalse;
		}


static float UI_GetValue(int ownerDraw) {
  return 0;
		}

/*
=================
UI_ServersQsortCompare
=================
*/
static int QDECL UI_ServersQsortCompare( const void *arg1, const void *arg2 ) {
	return trap_LAN_CompareServers( ui_netSource.integer, uiInfo.serverStatus.sortKey, uiInfo.serverStatus.sortDir, *(int*)arg1, *(int*)arg2);
		}


/*
=================
UI_ServersSort
=================
*/
void UI_ServersSort(int column, qboolean force) {

	if ( !force ) {
		if ( uiInfo.serverStatus.sortKey == column ) {
			return;
		}
	}

	uiInfo.serverStatus.sortKey = column;
	qsort( &uiInfo.serverStatus.displayServers[0], uiInfo.serverStatus.numDisplayServers, sizeof(int), UI_ServersQsortCompare);
		}

/*
static void UI_StartSinglePlayer() {
	int i,j, k, skill;
	char buff[1024];
	i = trap_Cvar_VariableValue( "ui_currentTier" );
  if (i < 0 || i >= tierCount) {
    i = 0;
  }
	j = trap_Cvar_VariableValue("ui_currentMap");
	if (j < 0 || j > MAPS_PER_TIER) {
		j = 0;
	}

 	trap_Cvar_SetValue( "singleplayer", 1 );
	trap_Cvar_SetValue( "g_gametype", Com_Clamp( 0, GT_MAX_GAME_TYPE - 1, tierList[i].gameTypes[j] ) );
	trap_Cmd_ExecuteText( EXEC_APPEND, va( "wait ; wait ; map %s\n", tierList[i].maps[j] ) );
	skill = trap_Cvar_VariableValue( "g_spSkill" );

	if (j == MAPS_PER_TIER-1) {
		k = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));
		Com_sprintf( buff, sizeof(buff), "wait ; addbot %s %i %s 250 %s\n", UI_AIFromName(teamList[k].teamMembers[0]), skill, "", teamList[k].teamMembers[0]);
	} else {
		k = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));
		for (i = 0; i < PLAYERS_PER_TEAM; i++) {
			Com_sprintf( buff, sizeof(buff), "wait ; addbot %s %i %s 250 %s\n", UI_AIFromName(teamList[k].teamMembers[i]), skill, "Blue", teamList[k].teamMembers[i]);
			trap_Cmd_ExecuteText( EXEC_APPEND, buff );
		}

		k = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
		for (i = 1; i < PLAYERS_PER_TEAM; i++) {
			Com_sprintf( buff, sizeof(buff), "wait ; addbot %s %i %s 250 %s\n", UI_AIFromName(teamList[k].teamMembers[i]), skill, "Red", teamList[k].teamMembers[i]);
			trap_Cmd_ExecuteText( EXEC_APPEND, buff );
		}
		trap_Cmd_ExecuteText( EXEC_APPEND, "wait 5; team Red\n" );
	}
	

		}
*/

/*
===============
UI_LoadMods
===============
*/
static void UI_LoadMods() {
	int		numdirs;
	char	dirlist[2048];
	char	*dirptr;
  char  *descptr;
	int		i;
	int		dirlen;

	uiInfo.modCount = 0;
	numdirs = trap_FS_GetFileList( "$modlist", "", dirlist, sizeof(dirlist) );
	dirptr  = dirlist;
	for( i = 0; i < numdirs; i++ ) {
		dirlen = strlen( dirptr ) + 1;
    descptr = dirptr + dirlen;
		uiInfo.modList[uiInfo.modCount].modName = String_Alloc(dirptr);
		uiInfo.modList[uiInfo.modCount].modDescr = String_Alloc(descptr);
    dirptr += dirlen + strlen(descptr) + 1;
		uiInfo.modCount++;
		if (uiInfo.modCount >= MAX_MODS) {
			break;
		}
	}

		}


/*
=============
UI_LoadCountries

Loads the retail ui/country.txt table so dropdown feeders can enumerate country codes.
=============
*/
static void UI_LoadCountries(void) {
	char	*token;
	char	*p;
	char	*buff;

	uiInfo.countryCount = 0;
	buff = GetMenuBuffer("ui/country.txt");
	if (!buff) {
		return;
	}

	p = buff;
	while (1) {
		token = COM_ParseExt(&p, qtrue);
		if (!token || token[0] == '\0') {
			break;
		}

		if (uiInfo.countryCount >= (int)(sizeof(uiInfo.countryList) / sizeof(uiInfo.countryList[0]))) {
			break;
		}

		uiInfo.countryList[uiInfo.countryCount++] = String_Alloc(token);
	}
		}

/*
===============
UI_LoadMovies
===============
*/
static void UI_LoadMovies() {
	char	movielist[4096];
	char	*moviename;
	int		i, len;

	uiInfo.movieCount = trap_FS_GetFileList( "video", "roq", movielist, 4096 );

	if (uiInfo.movieCount) {
		if (uiInfo.movieCount > MAX_MOVIES) {
			uiInfo.movieCount = MAX_MOVIES;
		}
		moviename = movielist;
		for ( i = 0; i < uiInfo.movieCount; i++ ) {
			len = strlen( moviename );
			if (!Q_stricmp(moviename +  len - 4,".roq")) {
				moviename[len-4] = '\0';
			}
			Q_strupr(moviename);
			uiInfo.movieList[i] = String_Alloc(moviename);
			moviename += len + 1;
		}
	}

		}



/*
===============
UI_LoadDemos
===============
*/
static void UI_LoadDemos() {
	char	demolist[4096];
	char demoExt[32];
	char	*demoname;
	int		i, len;

	Com_sprintf(demoExt, sizeof(demoExt), "dm_%d", (int)trap_Cvar_VariableValue("protocol"));

	uiInfo.demoCount = trap_FS_GetFileList( "demos", demoExt, demolist, 4096 );

	Com_sprintf(demoExt, sizeof(demoExt), ".dm_%d", (int)trap_Cvar_VariableValue("protocol"));

	if (uiInfo.demoCount) {
		if (uiInfo.demoCount > MAX_DEMOS) {
			uiInfo.demoCount = MAX_DEMOS;
		}
		demoname = demolist;
		for ( i = 0; i < uiInfo.demoCount; i++ ) {
			len = strlen( demoname );
			if (!Q_stricmp(demoname +  len - strlen(demoExt), demoExt)) {
				demoname[len-strlen(demoExt)] = '\0';
			}
			Q_strupr(demoname);
			uiInfo.demoList[i] = String_Alloc(demoname);
			demoname += len + 1;
		}
	}

		}


static qboolean UI_SetNextMap(int actual, int index) {
	int i;
	for (i = actual + 1; i < uiInfo.mapCount; i++) {
		if (uiInfo.mapList[i].active) {
			Menu_SetFeederSelection(NULL, FEEDER_MAPS, index + 1, "skirmish");
			return qtrue;
		}
	}
	return qfalse;
		}


static void UI_StartSkirmish(qboolean next) {
	int i, k, g, delay, temp;
	float skill;
	char buff[MAX_STRING_CHARS];

	if (next) {
		int actual;
		int index = trap_Cvar_VariableValue("ui_mapIndex");
	 	UI_MapCountByGameType(qtrue);
		UI_SelectedMap(index, &actual);
		if (UI_SetNextMap(actual, index)) {
		} else {
			UI_GameType_HandleKey(0, 0, K_MOUSE1, qfalse);
			UI_MapCountByGameType(qtrue);
			Menu_SetFeederSelection(NULL, FEEDER_MAPS, 0, "skirmish");
		}
	}

	g = uiInfo.gameTypes[ui_gameType.integer].gtEnum;
	trap_Cvar_SetValue( "g_gametype", g );
	trap_Cmd_ExecuteText( EXEC_APPEND, va( "wait ; wait ; map %s\n", uiInfo.mapList[ui_currentMap.integer].mapLoadName) );
	skill = trap_Cvar_VariableValue( "g_spSkill" );
	trap_Cvar_Set("ui_scoreMap", uiInfo.mapList[ui_currentMap.integer].mapName);

	k = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_opponentName"));

	trap_Cvar_Set("ui_singlePlayerActive", "1");

	// set up sp overrides, will be replaced on postgame
	temp = trap_Cvar_VariableValue( "capturelimit" );
	trap_Cvar_Set("ui_saveCaptureLimit", va("%i", temp));
	temp = trap_Cvar_VariableValue( "fraglimit" );
	trap_Cvar_Set("ui_saveFragLimit", va("%i", temp));

	UI_SetCapFragLimits(qfalse);

	temp = trap_Cvar_VariableValue( "g_doWarmup" );
	trap_Cvar_Set("ui_doWarmup", va("%i", temp));
	temp = trap_Cvar_VariableValue( "g_friendlyFire" );
	trap_Cvar_Set("ui_friendlyFire", va("%i", temp));
	temp = trap_Cvar_VariableValue( "g_warmup" );
	trap_Cvar_Set("ui_Warmup", va("%i", temp));
	temp = trap_Cvar_VariableValue( "sv_pure" );
	trap_Cvar_Set("ui_pure", va("%i", temp));

	trap_Cvar_Set("cg_cameraOrbit", "0");
	trap_Cvar_Set("cg_thirdPerson", "0");
	trap_Cvar_Set("g_doWarmup", "1");
	trap_Cvar_Set("g_warmup", "15");
	trap_Cvar_Set("sv_pure", "0");
	trap_Cvar_Set("g_friendlyFire", "0");
	trap_Cvar_Set("g_redTeam", UI_Cvar_VariableString("ui_teamName"));
	trap_Cvar_Set("g_blueTeam", UI_Cvar_VariableString("ui_opponentName"));

	if (trap_Cvar_VariableValue("ui_recordSPDemo")) {
		Com_sprintf(buff, MAX_STRING_CHARS, "%s_%i", uiInfo.mapList[ui_currentMap.integer].mapLoadName, g);
		trap_Cvar_Set("ui_recordSPDemoName", buff);
	}

	delay = 500;

	if (g == GT_TOURNAMENT) {
		trap_Cvar_Set("sv_maxClients", "2");
		Com_sprintf( buff, sizeof(buff), "wait ; addbot %s %f "", %i \n", uiInfo.mapList[ui_currentMap.integer].opponentName, skill, delay);
		trap_Cmd_ExecuteText( EXEC_APPEND, buff );
	} else {
		temp = uiInfo.mapList[ui_currentMap.integer].teamMembers * 2;
		trap_Cvar_Set("sv_maxClients", va("%d", temp));
		for (i =0; i < uiInfo.mapList[ui_currentMap.integer].teamMembers; i++) {
			Com_sprintf( buff, sizeof(buff), "addbot %s %f %s %i %s\n", UI_AIFromName(uiInfo.teamList[k].teamMembers[i]), skill, (g == GT_FFA) ? "" : "Blue", delay, uiInfo.teamList[k].teamMembers[i]);
			trap_Cmd_ExecuteText( EXEC_APPEND, buff );
			delay += 500;
		}
		k = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
		for (i =0; i < uiInfo.mapList[ui_currentMap.integer].teamMembers-1; i++) {
			Com_sprintf( buff, sizeof(buff), "addbot %s %f %s %i %s\n", UI_AIFromName(uiInfo.teamList[k].teamMembers[i]), skill, (g == GT_FFA) ? "" : "Red", delay, uiInfo.teamList[k].teamMembers[i]);
			trap_Cmd_ExecuteText( EXEC_APPEND, buff );
			delay += 500;
		}
	}
	if (g >= GT_TEAM ) {
		trap_Cmd_ExecuteText( EXEC_APPEND, "wait 5; team Red\n" );
	}
		}

static void UI_Update(const char *name) {
	int	val = trap_Cvar_VariableValue(name);

 	if (Q_stricmp(name, "ui_SetName") == 0) {
		trap_Cvar_Set( "name", UI_Cvar_VariableString("ui_Name"));
 	} else if (Q_stricmp(name, "ui_setRate") == 0) {
		float rate = trap_Cvar_VariableValue("rate");
		if (rate >= 5000) {
			trap_Cvar_Set("cl_maxpackets", "30");
			trap_Cvar_Set("cl_packetdup", "1");
		} else if (rate >= 4000) {
			trap_Cvar_Set("cl_maxpackets", "15");
			trap_Cvar_Set("cl_packetdup", "2");		// favor less prediction errors when there's packet loss
		} else {
			trap_Cvar_Set("cl_maxpackets", "15");
			trap_Cvar_Set("cl_packetdup", "1");		// favor lower bandwidth
		}
 	} else if (Q_stricmp(name, "ui_GetName") == 0) {
		trap_Cvar_Set( "ui_Name", UI_Cvar_VariableString("name"));
 	} else if (Q_stricmp(name, "r_colorbits") == 0) {
		switch (val) {
			case 0:
				trap_Cvar_SetValue( "r_depthbits", 0 );
				trap_Cvar_SetValue( "r_stencilbits", 0 );
			break;
			case 16:
				trap_Cvar_SetValue( "r_depthbits", 16 );
				trap_Cvar_SetValue( "r_stencilbits", 0 );
			break;
			case 32:
				trap_Cvar_SetValue( "r_depthbits", 24 );
			break;
		}
	} else if (Q_stricmp(name, "r_lodbias") == 0) {
		switch (val) {
			case 0:
				trap_Cvar_SetValue( "r_subdivisions", 4 );
			break;
			case 1:
				trap_Cvar_SetValue( "r_subdivisions", 12 );
			break;
			case 2:
				trap_Cvar_SetValue( "r_subdivisions", 20 );
			break;
		}
	} else if (Q_stricmp(name, "ui_glCustom") == 0) {
		switch (val) {
			case 0:	// high quality
				trap_Cvar_SetValue( "r_fullScreen", 1 );
				trap_Cvar_SetValue( "r_subdivisions", 4 );
				trap_Cvar_SetValue( "r_vertexlight", 0 );
				trap_Cvar_SetValue( "r_lodbias", 0 );
				trap_Cvar_SetValue( "r_colorbits", 32 );
				trap_Cvar_SetValue( "r_depthbits", 24 );
				trap_Cvar_SetValue( "r_picmip", 0 );
				trap_Cvar_SetValue( "r_mode", 4 );
				trap_Cvar_SetValue( "r_texturebits", 32 );
				trap_Cvar_SetValue( "r_fastSky", 0 );
				trap_Cvar_SetValue( "r_inGameVideo", 1 );
				trap_Cvar_SetValue( "cg_shadows", 1 );
				trap_Cvar_SetValue( "cg_brassTime", 2500 );
				trap_Cvar_Set( "r_texturemode", "GL_LINEAR_MIPMAP_LINEAR" );
			break;
			case 1: // normal 
				trap_Cvar_SetValue( "r_fullScreen", 1 );
				trap_Cvar_SetValue( "r_subdivisions", 12 );
				trap_Cvar_SetValue( "r_vertexlight", 0 );
				trap_Cvar_SetValue( "r_lodbias", 0 );
				trap_Cvar_SetValue( "r_colorbits", 0 );
				trap_Cvar_SetValue( "r_depthbits", 24 );
				trap_Cvar_SetValue( "r_picmip", 1 );
				trap_Cvar_SetValue( "r_mode", 3 );
				trap_Cvar_SetValue( "r_texturebits", 0 );
				trap_Cvar_SetValue( "r_fastSky", 0 );
				trap_Cvar_SetValue( "r_inGameVideo", 1 );
				trap_Cvar_SetValue( "cg_brassTime", 2500 );
				trap_Cvar_Set( "r_texturemode", "GL_LINEAR_MIPMAP_LINEAR" );
				trap_Cvar_SetValue( "cg_shadows", 0 );
			break;
			case 2: // fast
				trap_Cvar_SetValue( "r_fullScreen", 1 );
				trap_Cvar_SetValue( "r_subdivisions", 8 );
				trap_Cvar_SetValue( "r_vertexlight", 0 );
				trap_Cvar_SetValue( "r_lodbias", 1 );
				trap_Cvar_SetValue( "r_colorbits", 0 );
				trap_Cvar_SetValue( "r_depthbits", 0 );
				trap_Cvar_SetValue( "r_picmip", 1 );
				trap_Cvar_SetValue( "r_mode", 3 );
				trap_Cvar_SetValue( "r_texturebits", 0 );
				trap_Cvar_SetValue( "cg_shadows", 0 );
				trap_Cvar_SetValue( "r_fastSky", 1 );
				trap_Cvar_SetValue( "r_inGameVideo", 0 );
				trap_Cvar_SetValue( "cg_brassTime", 0 );
				trap_Cvar_Set( "r_texturemode", "GL_LINEAR_MIPMAP_NEAREST" );
			break;
			case 3: // fastest
				trap_Cvar_SetValue( "r_fullScreen", 1 );
				trap_Cvar_SetValue( "r_subdivisions", 20 );
				trap_Cvar_SetValue( "r_vertexlight", 1 );
				trap_Cvar_SetValue( "r_lodbias", 2 );
				trap_Cvar_SetValue( "r_colorbits", 16 );
				trap_Cvar_SetValue( "r_depthbits", 16 );
				trap_Cvar_SetValue( "r_mode", 3 );
				trap_Cvar_SetValue( "r_picmip", 2 );
				trap_Cvar_SetValue( "r_texturebits", 16 );
				trap_Cvar_SetValue( "cg_shadows", 0 );
				trap_Cvar_SetValue( "cg_brassTime", 0 );
				trap_Cvar_SetValue( "r_fastSky", 1 );
				trap_Cvar_SetValue( "r_inGameVideo", 0 );
				trap_Cvar_Set( "r_texturemode", "GL_LINEAR_MIPMAP_NEAREST" );
			break;
		}
	} else if (Q_stricmp(name, "ui_mousePitch") == 0) {
		if (val == 0) {
			trap_Cvar_SetValue( "m_pitch", 0.022f );
		} else {
			trap_Cvar_SetValue( "m_pitch", -0.022f );
		}
	}
}

/*
=============
UI_RunMenuScript

Execute menu-driven script commands, including browser overlay hooks.
=============
*/
/*
=============
UI_GetSelectedAdminClientNum

Resolve the current selection to a clientNum for admin menu commands.
=============
*/
static qboolean UI_GetSelectedAdminClientNum(const char *scriptName, int *clientNum) {
	int selected;

	if (!clientNum) {
		Com_Printf("UI: %s missing clientNum storage.\n", scriptName ? scriptName : "admin command");
		return qfalse;
	}

	UI_BuildPlayerList();
	selected = trap_Cvar_VariableValue("cg_selectedPlayer");

	if (selected < 0 || selected >= uiInfo.myTeamCount) {
		Com_Printf("UI: %s requires a valid selected player (cg_selectedPlayer=%d, teamCount=%d).\n",
			scriptName ? scriptName : "admin command", selected, uiInfo.myTeamCount);
		return qfalse;
	}

	*clientNum = uiInfo.teamClientNums[selected];
	return qtrue;
}

static void UI_RunMenuScript(char **args) {
	const char *name, *name2;
	char buff[1024];

	if (String_Parse(args, &name)) {
		if (Q_stricmp(name, "stopRefresh") == 0) {
			UI_StopServerRefresh();
			if (UI_BrowserOverlayAvailable() && ui_browserRefreshCommand && *ui_browserRefreshCommand) {
				trap_Cmd_ExecuteText(EXEC_NOW, ui_browserRefreshCommand);
			} else {
				Com_DPrintf("UI: stopRefresh requested without browser overlay; only native refresh stopped.\n");
			}
			return;
		}

		if (Q_stricmp(name, "web_showBrowser") == 0) {
			qboolean overlayAvailable;

			if (String_Parse(args, &name2)) {
				Com_sprintf(buff, sizeof(buff), "web_showBrowser %s\n", name2);
			} else {
				Com_sprintf(buff, sizeof(buff), "web_showBrowser\n");
			}

			overlayAvailable = UI_BrowserOverlayAvailable();
			if (!overlayAvailable) {
				if (UI_BrowserBridgeAvailable()) {
					Com_Printf("UI: browser overlay unavailable; enabling bridge menus for web_showBrowser.\n");
					UI_ApplyMenuFlowChange(UI_MENU_FLOW_BRIDGED, qtrue);
				} else {
					Com_Printf("UI: browser overlay unavailable; web_showBrowser stubbed.\n");
				}
				return;
			}

			UI_SetBrowserActive(qtrue);
			trap_Cmd_ExecuteText(EXEC_NOW, buff);
			return;
		}
		if (Q_stricmp(name, "StartServer") == 0) {
			int i, clients, oldclients;
			float skill;
			trap_Cvar_Set("cg_thirdPerson", "0");
			trap_Cvar_Set("cg_cameraOrbit", "0");
			trap_Cvar_Set("ui_singlePlayerActive", "0");
			trap_Cvar_SetValue( "dedicated", Com_Clamp( 0, 2, ui_dedicated.integer ) );
			trap_Cvar_SetValue( "g_gametype", Com_Clamp( 0, GT_MAX_GAME_TYPE - 1, uiInfo.gameTypes[ui_netGameType.integer].gtEnum ) );
			trap_Cvar_Set("g_redTeam", UI_Cvar_VariableString("ui_teamName"));
			trap_Cvar_Set("g_blueTeam", UI_Cvar_VariableString("ui_opponentName"));
			trap_Cmd_ExecuteText( EXEC_APPEND, va( "wait ; wait ; map %s\n", uiInfo.mapList[ui_currentNetMap.integer].mapLoadName ) );
			skill = trap_Cvar_VariableValue( "g_spSkill" );
			// set max clients based on spots
			oldclients = trap_Cvar_VariableValue( "sv_maxClients" );
			clients = 0;
			for (i = 0; i < PLAYERS_PER_TEAM; i++) {
				int bot = trap_Cvar_VariableValue( va("ui_blueteam%i", i+1));
				if (bot >= 0) {
					clients++;
				}
				bot = trap_Cvar_VariableValue( va("ui_redteam%i", i+1));
				if (bot >= 0) {
					clients++;
				}
			}
			if (clients == 0) {
				clients = 8;
			}
			
			if (oldclients > clients) {
				clients = oldclients;
			}

			trap_Cvar_Set("sv_maxClients", va("%d",clients));

			for (i = 0; i < PLAYERS_PER_TEAM; i++) {
				int bot = trap_Cvar_VariableValue( va("ui_blueteam%i", i+1));
				if (bot > 1) {
					if (ui_actualNetGameType.integer >= GT_TEAM) {
						Com_sprintf( buff, sizeof(buff), "addbot %s %f %s\n", uiInfo.characterList[bot-2].name, skill, "Blue");
					} else {
						Com_sprintf( buff, sizeof(buff), "addbot %s %f \n", UI_GetBotNameByNumber(bot-2), skill);
					}
					trap_Cmd_ExecuteText( EXEC_APPEND, buff );
				}
				bot = trap_Cvar_VariableValue( va("ui_redteam%i", i+1));
				if (bot > 1) {
					if (ui_actualNetGameType.integer >= GT_TEAM) {
						Com_sprintf( buff, sizeof(buff), "addbot %s %f %s\n", uiInfo.characterList[bot-2].name, skill, "Red");
					} else {
						Com_sprintf( buff, sizeof(buff), "addbot %s %f \n", UI_GetBotNameByNumber(bot-2), skill);
					}
					trap_Cmd_ExecuteText( EXEC_APPEND, buff );
				}
			}
		} else if (Q_stricmp(name, "updateSPMenu") == 0) {
			UI_SetCapFragLimits(qtrue);
			UI_MapCountByGameType(qtrue);
			ui_mapIndex.integer = UI_GetIndexFromSelection(ui_currentMap.integer);
			trap_Cvar_Set("ui_mapIndex", va("%d", ui_mapIndex.integer));
			Menu_SetFeederSelection(NULL, FEEDER_MAPS, ui_mapIndex.integer, "skirmish");
			UI_GameType_HandleKey(0, 0, K_MOUSE1, qfalse);
			UI_GameType_HandleKey(0, 0, K_MOUSE2, qfalse);
		} else if (Q_stricmp(name, "resetDefaults") == 0) {
			trap_Cmd_ExecuteText( EXEC_APPEND, "exec default.cfg\n");
			trap_Cmd_ExecuteText( EXEC_APPEND, "cvar_restart\n");
			Controls_SetDefaults();
			trap_Cvar_Set("com_introPlayed", "1" );
			trap_Cmd_ExecuteText( EXEC_APPEND, "vid_restart\n" );
		} else if (Q_stricmp(name, "getCDKey") == 0) {
			char out[17];
			trap_GetCDKey(buff, 17);
			trap_Cvar_Set("cdkey1", "");
			trap_Cvar_Set("cdkey2", "");
			trap_Cvar_Set("cdkey3", "");
			trap_Cvar_Set("cdkey4", "");
			if (strlen(buff) == CDKEY_LEN) {
				Q_strncpyz(out, buff, 5);
				trap_Cvar_Set("cdkey1", out);
				Q_strncpyz(out, buff + 4, 5);
				trap_Cvar_Set("cdkey2", out);
				Q_strncpyz(out, buff + 8, 5);
				trap_Cvar_Set("cdkey3", out);
				Q_strncpyz(out, buff + 12, 5);
				trap_Cvar_Set("cdkey4", out);
			}

		} else if (Q_stricmp(name, "verifyCDKey") == 0) {
			buff[0] = '\0';
			Q_strcat(buff, 1024, UI_Cvar_VariableString("cdkey1")); 
			Q_strcat(buff, 1024, UI_Cvar_VariableString("cdkey2")); 
			Q_strcat(buff, 1024, UI_Cvar_VariableString("cdkey3")); 
			Q_strcat(buff, 1024, UI_Cvar_VariableString("cdkey4")); 
			trap_Cvar_Set("cdkey", buff);
			if (trap_VerifyCDKey(buff, UI_Cvar_VariableString("cdkeychecksum"))) {
				trap_Cvar_Set("ui_cdkeyvalid", "CD Key Appears to be valid.");
				trap_SetCDKey(buff);
			} else {
				trap_Cvar_Set("ui_cdkeyvalid", "CD Key does not appear to be valid.");
			}
		} else if (Q_stricmp(name, "loadArenas") == 0) {
			UI_LoadArenas();
			UI_MapCountByGameType(qfalse);
			Menu_SetFeederSelection(NULL, FEEDER_ALLMAPS, 0, "createserver");
		} else if (Q_stricmp(name, "saveControls") == 0) {
			Controls_SetConfig(qtrue);
		} else if (Q_stricmp(name, "loadControls") == 0) {
			Controls_GetConfig();
		} else if (Q_stricmp(name, "clearError") == 0 || Q_stricmp(name, "clearComError") == 0) {
			trap_Cvar_Set("com_errorMessage", "");
		} else if (Q_stricmp(name, "loadGameInfo") == 0) {
#ifdef PRE_RELEASE_TADEMO
			UI_ParseGameInfo("demogameinfo.txt");
#else
			UI_ParseGameInfo("gameinfo.txt");
#endif
			UI_LoadBestScores(uiInfo.mapList[ui_currentMap.integer].mapLoadName, uiInfo.gameTypes[ui_gameType.integer].gtEnum);
		} else if (Q_stricmp(name, "resetScores") == 0) {
			UI_ClearScores();
		} else if (Q_stricmp(name, "RefreshServers") == 0) {
			UI_StartServerRefresh(qtrue);
			UI_BuildServerDisplayList(qtrue);
		} else if (Q_stricmp(name, "RefreshFilter") == 0) {
			UI_StartServerRefresh(qfalse);
			UI_BuildServerDisplayList(qtrue);
		} else if (Q_stricmp(name, "RunSPDemo") == 0) {
			if (uiInfo.demoAvailable) {
			  trap_Cmd_ExecuteText( EXEC_APPEND, va("demo %s_%i\n", uiInfo.mapList[ui_currentMap.integer].mapLoadName, uiInfo.gameTypes[ui_gameType.integer].gtEnum));
			}
		} else if (Q_stricmp(name, "LoadDemos") == 0) {
			UI_LoadDemos();
		} else if (Q_stricmp(name, "LoadMovies") == 0) {
			UI_LoadMovies();
		} else if (Q_stricmp(name, "LoadMods") == 0) {
			UI_LoadMods();
		} else if (Q_stricmp(name, "playMovie") == 0) {
			if (uiInfo.previewMovie >= 0) {
			  trap_CIN_StopCinematic(uiInfo.previewMovie);
			}
			trap_Cmd_ExecuteText( EXEC_APPEND, va("cinematic %s.roq 2\n", uiInfo.movieList[uiInfo.movieIndex]));
		} else if (Q_stricmp(name, "RunMod") == 0) {
			trap_Cvar_Set( "fs_game", uiInfo.modList[uiInfo.modIndex].modName);
			trap_Cmd_ExecuteText( EXEC_APPEND, "vid_restart;" );
		} else if (Q_stricmp(name, "RunDemo") == 0) {
			trap_Cmd_ExecuteText( EXEC_APPEND, va("demo %s\n", uiInfo.demoList[uiInfo.demoIndex]));
		} else if (Q_stricmp(name, "Quake3") == 0) {
			trap_Cvar_Set( "fs_game", "");
			trap_Cmd_ExecuteText( EXEC_APPEND, "vid_restart;" );
		} else if (Q_stricmp(name, "closeJoin") == 0) {
			if (uiInfo.serverStatus.refreshActive) {
				UI_StopMenuRefresh();
				UI_BuildServerDisplayList(qtrue);
			} else {
				Menus_CloseByName("joinserver");
				Menus_OpenByName("main");
			}
		} else if (Q_stricmp(name, "StopRefresh") == 0) {
			UI_StopMenuRefresh();
		} else if (Q_stricmp(name, "UpdateFilter") == 0) {
			if (ui_netSource.integer == AS_LOCAL) {
				UI_StartServerRefresh(qtrue);
			}
			UI_BuildServerDisplayList(qtrue);
			UI_FeederSelection(FEEDER_SERVERS, 0);
		} else if (Q_stricmp(name, "ServerStatus") == 0) {
			trap_LAN_GetServerAddressString(ui_netSource.integer, uiInfo.serverStatus.displayServers[uiInfo.serverStatus.currentServer], uiInfo.serverStatusAddress, sizeof(uiInfo.serverStatusAddress));
			UI_BuildServerStatus(qtrue);
		} else if (Q_stricmp(name, "FoundPlayerServerStatus") == 0) {
			Q_strncpyz(uiInfo.serverStatusAddress, uiInfo.foundPlayerServerAddresses[uiInfo.currentFoundPlayerServer], sizeof(uiInfo.serverStatusAddress));
			UI_BuildServerStatus(qtrue);
			Menu_SetFeederSelection(NULL, FEEDER_FINDPLAYER, 0, NULL);
		} else if (Q_stricmp(name, "FindPlayer") == 0) {
			UI_BuildFindPlayerList(qtrue);
			// clear the displayed server status info
			uiInfo.serverStatusInfo.numLines = 0;
			Menu_SetFeederSelection(NULL, FEEDER_FINDPLAYER, 0, NULL);
		} else if (Q_stricmp(name, "JoinServer") == 0) {
			trap_Cvar_Set("cg_thirdPerson", "0");
			trap_Cvar_Set("cg_cameraOrbit", "0");
			trap_Cvar_Set("ui_singlePlayerActive", "0");
			if (uiInfo.serverStatus.currentServer >= 0 && uiInfo.serverStatus.currentServer < uiInfo.serverStatus.numDisplayServers) {
				trap_LAN_GetServerAddressString(ui_netSource.integer, uiInfo.serverStatus.displayServers[uiInfo.serverStatus.currentServer], buff, 1024);
				trap_Cmd_ExecuteText( EXEC_APPEND, va( "connect %s\n", buff ) );
			}
		} else if (Q_stricmp(name, "FoundPlayerJoinServer") == 0) {
			trap_Cvar_Set("ui_singlePlayerActive", "0");
			if (uiInfo.currentFoundPlayerServer >= 0 && uiInfo.currentFoundPlayerServer < uiInfo.numFoundPlayerServers) {
				trap_Cmd_ExecuteText( EXEC_APPEND, va( "connect %s\n", uiInfo.foundPlayerServerAddresses[uiInfo.currentFoundPlayerServer] ) );
			}
		} else if (Q_stricmp(name, "Quit") == 0) {
			trap_Cvar_Set("ui_singlePlayerActive", "0");
			trap_Cmd_ExecuteText( EXEC_NOW, "quit");
		} else if (Q_stricmp(name, "Controls") == 0) {
		  trap_Cvar_Set( "cl_paused", "1" );
			trap_Key_SetCatcher( KEYCATCH_UI );
			Menus_CloseAll();
			Menus_ActivateByName("setup_menu2");
		} else if (Q_stricmp(name, "Leave") == 0) {
			UI_LeaveGame();
		} else if (Q_stricmp(name, "teamModelChanged") == 0) {
			UI_UpdateForceModelSettings(qtrue);
		} else if (Q_stricmp(name, "teamColorDefaults") == 0) {
			trap_Cvar_Set("ui_teamHeadColor", "96");
			trap_Cvar_Set("ui_teamUpperColor", "96");
			trap_Cvar_Set("ui_teamLowerColor", "96");
			trap_Cvar_Set("cg_teamHeadColor", "96");
			trap_Cvar_Set("cg_teamUpperColor", "96");
			trap_Cvar_Set("cg_teamLowerColor", "96");
		} else if (Q_stricmp(name, "enemyModelChanged") == 0) {
			UI_UpdateForceModelSettings(qfalse);
		} else if (Q_stricmp(name, "enemyColorDefaults") == 0) {
			trap_Cvar_Set("ui_enemyHeadColor", "27");
			trap_Cvar_Set("ui_enemyUpperColor", "27");
			trap_Cvar_Set("ui_enemyLowerColor", "27");
			trap_Cvar_Set("cg_enemyHeadColor", "27");
			trap_Cvar_Set("cg_enemyUpperColor", "27");
			trap_Cvar_Set("cg_enemyLowerColor", "27");
                } else if (Q_stricmp(name, "ServerSort") == 0) {
                        int sortColumn;
                        if (Int_Parse(args, &sortColumn)) {
                                // if same column we're already sorting on then flip the direction
                                if (sortColumn == uiInfo.serverStatus.sortKey) {
					uiInfo.serverStatus.sortDir = !uiInfo.serverStatus.sortDir;
				}
				// make sure we sort again
				UI_ServersSort(sortColumn, qtrue);
			}
		} else if (Q_stricmp(name, "nextSkirmish") == 0) {
			UI_StartSkirmish(qtrue);
		} else if (Q_stricmp(name, "SkirmishStart") == 0) {
			UI_StartSkirmish(qfalse);
		} else if (Q_stricmp(name, "closeingame") == 0) {
			UI_CloseInGameMenu();
		} else if (Q_stricmp(name, "clientviewProfile") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("clientviewprofile %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "clientFriendInvite") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("clientfriendinvite %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "clientmutePlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("clientmute %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "kickPlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("callvote clientkick %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "tempbanPlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("tempban %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "banPlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("ban %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "mutePlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("mute %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "unmutePlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("unmute %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "modPlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("addmod %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "adminPlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("addadmin %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "deopPlayer") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("demote %i\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "putred") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("put %i r\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "putblue") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("put %i b\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "putspec") == 0) {
			int clientNum;

			if (UI_GetSelectedAdminClientNum(name, &clientNum)) {
				trap_Cmd_ExecuteText(EXEC_APPEND, va("put %i s\n", clientNum));
				UI_CloseInGameMenu();
			}
		} else if (Q_stricmp(name, "voteMap") == 0) {
			if (ui_currentNetMap.integer >= 0 && ui_currentNetMap.integer < uiInfo.mapCount) {
				const char *gametypeToken = "";
				const char *mapName = uiInfo.mapList[ui_currentNetMap.integer].mapLoadName;

				if (ui_cvGameType.integer != -1) {
					gametypeToken = UI_GetCallvoteGametypeToken(ui_cvGameType.integer);
				}

				trap_Cmd_ExecuteText(EXEC_APPEND, va("callvote map %s %s\n", mapName, gametypeToken));
			}
		} else if (Q_stricmp(name, "updateCallvoteMapPreview") == 0) {
			UI_FeederSelection(FEEDER_CVMAPS, ui_mapIndex.integer);
		} else if (Q_stricmp(name, "voteKick") == 0) {
			if (uiInfo.playerIndex >= 0 && uiInfo.playerIndex < uiInfo.playerCount) {
				trap_Cmd_ExecuteText( EXEC_APPEND, va("callvote kick %s\n",uiInfo.playerNames[uiInfo.playerIndex]) );
			}
		} else if (Q_stricmp(name, "voteGame") == 0) {
			if (ui_netGameType.integer >= 0 && ui_netGameType.integer < uiInfo.numGameTypes) {
				trap_Cmd_ExecuteText( EXEC_APPEND, va("callvote g_gametype %i\n",uiInfo.gameTypes[ui_netGameType.integer].gtEnum) );
			}
		} else if (Q_stricmp(name, "voteLeader") == 0) {
			if (uiInfo.teamIndex >= 0 && uiInfo.teamIndex < uiInfo.myTeamCount) {
				trap_Cmd_ExecuteText( EXEC_APPEND, va("callteamvote leader %s\n",uiInfo.teamNames[uiInfo.teamIndex]) );
			}
		} else if (Q_stricmp(name, "addBot") == 0) {
			if (trap_Cvar_VariableValue("g_gametype") >= GT_TEAM) {
				trap_Cmd_ExecuteText( EXEC_APPEND, va("addbot %s %i %s\n", uiInfo.characterList[uiInfo.botIndex].name, uiInfo.skillIndex+1, (uiInfo.redBlue == 0) ? "Red" : "Blue") );
			} else {
				trap_Cmd_ExecuteText( EXEC_APPEND, va("addbot %s %i %s\n", UI_GetBotNameByNumber(uiInfo.botIndex), uiInfo.skillIndex+1, (uiInfo.redBlue == 0) ? "Red" : "Blue") );
			}
		} else if (Q_stricmp(name, "addFavorite") == 0) {
			if (ui_netSource.integer != AS_FAVORITES) {
				char name[MAX_NAME_LENGTH];
				char addr[MAX_NAME_LENGTH];
				int res;

				trap_LAN_GetServerInfo(ui_netSource.integer, uiInfo.serverStatus.displayServers[uiInfo.serverStatus.currentServer], buff, MAX_STRING_CHARS);
				name[0] = addr[0] = '\0';
				Q_strncpyz(name, 	Info_ValueForKey(buff, "hostname"), MAX_NAME_LENGTH);
				Q_strncpyz(addr, 	Info_ValueForKey(buff, "addr"), MAX_NAME_LENGTH);
				if (strlen(name) > 0 && strlen(addr) > 0) {
					res = trap_LAN_AddServer(AS_FAVORITES, name, addr);
					if (res == 0) {
						// server already in the list
						Com_Printf("Favorite already in list\n");
					}
					else if (res == -1) {
						// list full
						Com_Printf("Favorite list full\n");
					}
					else {
						// successfully added
						Com_Printf("Added favorite server %s\n", addr);
					}
				}
			}
		} else if (Q_stricmp(name, "deleteFavorite") == 0) {
			if (ui_netSource.integer == AS_FAVORITES) {
				char addr[MAX_NAME_LENGTH];
				trap_LAN_GetServerInfo(ui_netSource.integer, uiInfo.serverStatus.displayServers[uiInfo.serverStatus.currentServer], buff, MAX_STRING_CHARS);
				addr[0] = '\0';
				Q_strncpyz(addr, 	Info_ValueForKey(buff, "addr"), MAX_NAME_LENGTH);
				if (strlen(addr) > 0) {
					trap_LAN_RemoveServer(AS_FAVORITES, addr);
				}
			}
		} else if (Q_stricmp(name, "createFavorite") == 0) {
			if (ui_netSource.integer == AS_FAVORITES) {
				char name[MAX_NAME_LENGTH];
				char addr[MAX_NAME_LENGTH];
				int res;

				name[0] = addr[0] = '\0';
				Q_strncpyz(name, 	UI_Cvar_VariableString("ui_favoriteName"), MAX_NAME_LENGTH);
				Q_strncpyz(addr, 	UI_Cvar_VariableString("ui_favoriteAddress"), MAX_NAME_LENGTH);
				if (strlen(name) > 0 && strlen(addr) > 0) {
					res = trap_LAN_AddServer(AS_FAVORITES, name, addr);
					if (res == 0) {
						// server already in the list
						Com_Printf("Favorite already in list\n");
					}
					else if (res == -1) {
						// list full
						Com_Printf("Favorite list full\n");
					}
					else {
						// successfully added
						Com_Printf("Added favorite server %s\n", addr);
					}
				}
			}
		} else if (Q_stricmp(name, "glCustom") == 0) {
			trap_Cvar_Set("ui_glCustom", "4");
		} else if (Q_stricmp(name, "update") == 0) {
			if (String_Parse(args, &name2)) {
				UI_Update(name2);
			}
		} else if (Q_stricmp(name, "setPbClStatus") == 0) {
			int stat;
			if ( Int_Parse( args, &stat ) )
				trap_SetPbClStatus( stat );
		}
		else {
			Com_Printf("unknown UI script %s\n", name);
		}
	}
}

static void UI_GetTeamColor(vec4_t *color) {
		}

/*
==================
UI_MapCountByGameType
==================
*/
static int UI_MapCountByGameType(qboolean singlePlayer) {
	int i, c, game;
	c = 0;
	game = singlePlayer ? uiInfo.gameTypes[ui_gameType.integer].gtEnum : uiInfo.gameTypes[ui_netGameType.integer].gtEnum;
	if (game == GT_SINGLE_PLAYER) {
		game++;
	} 
	if (game == GT_TEAM) {
		game = GT_FFA;
	}

	for (i = 0; i < uiInfo.mapCount; i++) {
		uiInfo.mapList[i].active = qfalse;
		if ( uiInfo.mapList[i].typeBits & (1 << game)) {
			if (singlePlayer) {
				if (!(uiInfo.mapList[i].typeBits & (1 << GT_SINGLE_PLAYER))) {
					continue;
				}
			}
			c++;
			uiInfo.mapList[i].active = qtrue;
		}
	}
	return c;
		}

qboolean UI_hasSkinForBase(const char *base, const char *team) {
	char	test[1024];
	
	Com_sprintf( test, sizeof( test ), "models/players/%s/%s/lower_default.skin", base, team );

	if (trap_FS_FOpenFile(test, 0, FS_READ)) {
		return qtrue;
	}
	Com_sprintf( test, sizeof( test ), "models/players/characters/%s/%s/lower_default.skin", base, team );

	if (trap_FS_FOpenFile(test, 0, FS_READ)) {
		return qtrue;
	}
	return qfalse;
		}

/*
==================
UI_MapCountByTeam
==================
*/
static int UI_HeadCountByTeam() {
	static int init = 0;
	int i, j, k, c, tIndex;
	
	c = 0;
	if (!init) {
		for (i = 0; i < uiInfo.characterCount; i++) {
			uiInfo.characterList[i].reference = 0;
			for (j = 0; j < uiInfo.teamCount; j++) {
			  if (UI_hasSkinForBase(uiInfo.characterList[i].base, uiInfo.teamList[j].teamName)) {
					uiInfo.characterList[i].reference |= (1<<j);
			  }
			}
		}
		init = 1;
	}

	tIndex = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));

	// do names
	for (i = 0; i < uiInfo.characterCount; i++) {
		uiInfo.characterList[i].active = qfalse;
		for(j = 0; j < TEAM_MEMBERS; j++) {
			if (uiInfo.teamList[tIndex].teamMembers[j] != NULL) {
				if (uiInfo.characterList[i].reference&(1<<tIndex)) {// && Q_stricmp(uiInfo.teamList[tIndex].teamMembers[j], uiInfo.characterList[i].name)==0) {
					uiInfo.characterList[i].active = qtrue;
					c++;
					break;
				}
			}
		}
	}

	// and then aliases
	for(j = 0; j < TEAM_MEMBERS; j++) {
		for(k = 0; k < uiInfo.aliasCount; k++) {
			if (uiInfo.aliasList[k].name != NULL) {
				if (Q_stricmp(uiInfo.teamList[tIndex].teamMembers[j], uiInfo.aliasList[k].name)==0) {
					for (i = 0; i < uiInfo.characterCount; i++) {
						if (uiInfo.characterList[i].headImage != -1 && uiInfo.characterList[i].reference&(1<<tIndex) && Q_stricmp(uiInfo.aliasList[k].ai, uiInfo.characterList[i].name)==0) {
							if (uiInfo.characterList[i].active == qfalse) {
								uiInfo.characterList[i].active = qtrue;
								c++;
							}
							break;
						}
					}
				}
			}
		}
	}
	return c;
		}

/*
==================
UI_InsertServerIntoDisplayList
==================
*/
static void UI_InsertServerIntoDisplayList(int num, int position) {
	int i;

	if (position < 0 || position > uiInfo.serverStatus.numDisplayServers ) {
		return;
	}
	//
	uiInfo.serverStatus.numDisplayServers++;
	for (i = uiInfo.serverStatus.numDisplayServers; i > position; i--) {
		uiInfo.serverStatus.displayServers[i] = uiInfo.serverStatus.displayServers[i-1];
	}
	uiInfo.serverStatus.displayServers[position] = num;
		}

/*
==================
UI_RemoveServerFromDisplayList
==================
*/
static void UI_RemoveServerFromDisplayList(int num) {
	int i, j;

	for (i = 0; i < uiInfo.serverStatus.numDisplayServers; i++) {
		if (uiInfo.serverStatus.displayServers[i] == num) {
			uiInfo.serverStatus.numDisplayServers--;
			for (j = i; j < uiInfo.serverStatus.numDisplayServers; j++) {
				uiInfo.serverStatus.displayServers[j] = uiInfo.serverStatus.displayServers[j+1];
			}
			return;
		}
	}
		}

/*
==================
UI_BinaryServerInsertion
==================
*/
static void UI_BinaryServerInsertion(int num) {
	int mid, offset, res, len;

	// use binary search to insert server
	len = uiInfo.serverStatus.numDisplayServers;
	mid = len;
	offset = 0;
	res = 0;
	while(mid > 0) {
		mid = len >> 1;
		//
		res = trap_LAN_CompareServers( ui_netSource.integer, uiInfo.serverStatus.sortKey,
					uiInfo.serverStatus.sortDir, num, uiInfo.serverStatus.displayServers[offset+mid]);
		// if equal
		if (res == 0) {
			UI_InsertServerIntoDisplayList(num, offset+mid);
			return;
		}
		// if larger
		else if (res == 1) {
			offset += mid;
			len -= mid;
		}
		// if smaller
		else {
			len -= mid;
		}
	}
	if (res == 1) {
		offset++;
	}
	UI_InsertServerIntoDisplayList(num, offset);
		}

/*
==================
UI_BuildServerDisplayList
==================
*/
static void UI_BuildServerDisplayList(qboolean force) {
	int i, count, clients, maxClients, ping, game, len, visible;
	char info[MAX_STRING_CHARS];
//	qboolean startRefresh = qtrue; TTimo: unused
	static int numinvisible;

	if (!UI_ServerBrowserEnabled()) {
		return;
	}

	if (!(force || uiInfo.uiDC.realTime > uiInfo.serverStatus.nextDisplayRefresh)) {
		return;
	}
	// if we shouldn't reset
	if ( force == 2 ) {
		force = 0;
	}

	// do motd updates here too
	trap_Cvar_VariableStringBuffer( "cl_motdString", uiInfo.serverStatus.motd, sizeof(uiInfo.serverStatus.motd) );
	len = strlen(uiInfo.serverStatus.motd);
	if (len == 0) {
		strcpy(uiInfo.serverStatus.motd, "Welcome to Team Arena!");
		len = strlen(uiInfo.serverStatus.motd);
	} 
	if (len != uiInfo.serverStatus.motdLen) {
		uiInfo.serverStatus.motdLen = len;
		uiInfo.serverStatus.motdWidth = -1;
	} 

	if (force) {
		numinvisible = 0;
		// clear number of displayed servers
		uiInfo.serverStatus.numDisplayServers = 0;
		uiInfo.serverStatus.numPlayersOnServers = 0;
		// set list box index to zero
		Menu_SetFeederSelection(NULL, FEEDER_SERVERS, 0, NULL);
		// mark all servers as visible so we store ping updates for them
		trap_LAN_MarkServerVisible(ui_netSource.integer, -1, qtrue);
	}

	// get the server count (comes from the master)
	count = trap_LAN_GetServerCount(ui_netSource.integer);
	if (count == -1 || (ui_netSource.integer == AS_LOCAL && count == 0) ) {
		// still waiting on a response from the master
		uiInfo.serverStatus.numDisplayServers = 0;
		uiInfo.serverStatus.numPlayersOnServers = 0;
		uiInfo.serverStatus.nextDisplayRefresh = uiInfo.uiDC.realTime + 500;
		return;
	}

	visible = qfalse;
	for (i = 0; i < count; i++) {
		// if we already got info for this server
		if (!trap_LAN_ServerIsVisible(ui_netSource.integer, i)) {
			continue;
		}
		visible = qtrue;
		// get the ping for this server
		ping = trap_LAN_GetServerPing(ui_netSource.integer, i);
		if (ping > 0 || ui_netSource.integer == AS_FAVORITES) {

			trap_LAN_GetServerInfo(ui_netSource.integer, i, info, MAX_STRING_CHARS);

			clients = atoi(Info_ValueForKey(info, "clients"));
			uiInfo.serverStatus.numPlayersOnServers += clients;

			if (ui_browserShowEmpty.integer == 0) {
				if (clients == 0) {
					trap_LAN_MarkServerVisible(ui_netSource.integer, i, qfalse);
					continue;
				}
			}

			if (ui_browserShowFull.integer == 0) {
				maxClients = atoi(Info_ValueForKey(info, "sv_maxclients"));
				if (clients == maxClients) {
					trap_LAN_MarkServerVisible(ui_netSource.integer, i, qfalse);
					continue;
				}
			}

			if (uiInfo.joinGameTypes[ui_joinGameType.integer].gtEnum != -1) {
				game = atoi(Info_ValueForKey(info, "gametype"));
				if (game != uiInfo.joinGameTypes[ui_joinGameType.integer].gtEnum) {
					trap_LAN_MarkServerVisible(ui_netSource.integer, i, qfalse);
					continue;
				}
			}
				
			if (ui_serverFilterType.integer > 0) {
				if (Q_stricmp(Info_ValueForKey(info, "game"), serverFilters[ui_serverFilterType.integer].basedir) != 0) {
					trap_LAN_MarkServerVisible(ui_netSource.integer, i, qfalse);
					continue;
				}
			}
			// make sure we never add a favorite server twice
			if (ui_netSource.integer == AS_FAVORITES) {
				UI_RemoveServerFromDisplayList(i);
			}
			// insert the server into the list
			UI_BinaryServerInsertion(i);
			// done with this server
			if (ping > 0) {
				trap_LAN_MarkServerVisible(ui_netSource.integer, i, qfalse);
				numinvisible++;
			}
		}
	}

	uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime;

	// if there were no servers visible for ping updates
	if (!visible) {
//		UI_StopServerRefresh();
//		uiInfo.serverStatus.nextDisplayRefresh = 0;
	}
		}

typedef struct
{
	char *name, *altName;
} serverStatusCvar_t;

serverStatusCvar_t serverStatusCvars[] = {
	{"sv_hostname", "Name"},
	{"Address", ""},
	{"gamename", "Game name"},
	{"g_gametype", "Game type"},
	{"mapname", "Map"},
	{"version", ""},
	{"protocol", ""},
	{"timelimit", ""},
	{"fraglimit", ""},
	{NULL, NULL}
};

/*
==================
UI_SortServerStatusInfo
==================
*/
static void UI_SortServerStatusInfo( serverStatusInfo_t *info ) {
	int i, j, index;
	char *tmp1, *tmp2;
	static const char *const qlGametypeNames[GT_MAX_GAME_TYPE] = {
		"Free For All",
		"Duel",
		"Race",
		"Team Deathmatch",
		"Clan Arena",
		"Capture the Flag",
		"1-Flag CTF",
		"Overload",
		"Harvester",
		"Freeze Tag",
		"Domination",
		"Attack & Defend",
		"Red Rover",
	};

	// FIXME: if \"gamename\" == \"baseq3\" or \"missionpack\" then
	// replace the gametype number by FFA, CTF etc.
	//
	index = 0;
	for (i = 0; serverStatusCvars[i].name; i++) {
		for (j = 0; j < info->numLines; j++) {
			if ( !info->lines[j][1] || info->lines[j][1][0] ) {
				continue;
			}
			if ( !Q_stricmp(serverStatusCvars[i].name, info->lines[j][0]) ) {
				// swap lines
				tmp1 = info->lines[index][0];
				tmp2 = info->lines[index][3];
				info->lines[index][0] = info->lines[j][0];
				info->lines[index][3] = info->lines[j][3];
				info->lines[j][0] = tmp1;
				info->lines[j][3] = tmp2;
				//
				if ( strlen(serverStatusCvars[i].altName) ) {
					info->lines[index][0] = serverStatusCvars[i].altName;
				}
				if ( !Q_stricmp(serverStatusCvars[i].name, "g_gametype") ) {
					int gametype;

					gametype = atoi( info->lines[index][3] );
					if ( gametype >= 0 && gametype < GT_MAX_GAME_TYPE && qlGametypeNames[gametype] ) {
						info->lines[index][3] = (char *)qlGametypeNames[gametype];
					}
				}
				index++;
			}
		}
	}
}

/*
==================
UI_GetServerStatusInfo
==================
*/
static int UI_GetServerStatusInfo( const char *serverAddress, serverStatusInfo_t *info ) {
	char *p, *score, *ping, *name;
	int i, len;

	if (!info) {
		trap_LAN_ServerStatus( serverAddress, NULL, 0);
		return qfalse;
	}
	memset(info, 0, sizeof(*info));
	if ( trap_LAN_ServerStatus( serverAddress, info->text, sizeof(info->text)) ) {
		Q_strncpyz(info->address, serverAddress, sizeof(info->address));
		p = info->text;
		info->numLines = 0;
		info->lines[info->numLines][0] = "Address";
		info->lines[info->numLines][1] = "";
		info->lines[info->numLines][2] = "";
		info->lines[info->numLines][3] = info->address;
		info->numLines++;
		// get the cvars
		while (p && *p) {
			p = strchr(p, '\\');
			if (!p) break;
			*p++ = '\0';
			if (*p == '\\')
				break;
			info->lines[info->numLines][0] = p;
			info->lines[info->numLines][1] = "";
			info->lines[info->numLines][2] = "";
			p = strchr(p, '\\');
			if (!p) break;
			*p++ = '\0';
			info->lines[info->numLines][3] = p;

			info->numLines++;
			if (info->numLines >= MAX_SERVERSTATUS_LINES)
				break;
		}
		// get the player list
		if (info->numLines < MAX_SERVERSTATUS_LINES-3) {
			// empty line
			info->lines[info->numLines][0] = "";
			info->lines[info->numLines][1] = "";
			info->lines[info->numLines][2] = "";
			info->lines[info->numLines][3] = "";
			info->numLines++;
			// header
			info->lines[info->numLines][0] = "num";
			info->lines[info->numLines][1] = "score";
			info->lines[info->numLines][2] = "ping";
			info->lines[info->numLines][3] = "name";
			info->numLines++;
			// parse players
			i = 0;
			len = 0;
			while (p && *p) {
				if (*p == '\\')
					*p++ = '\0';
				if (!p)
					break;
				score = p;
				p = strchr(p, ' ');
				if (!p)
					break;
				*p++ = '\0';
				ping = p;
				p = strchr(p, ' ');
				if (!p)
					break;
				*p++ = '\0';
				name = p;
				Com_sprintf(&info->pings[len], sizeof(info->pings)-len, "%d", i);
				info->lines[info->numLines][0] = &info->pings[len];
				len += strlen(&info->pings[len]) + 1;
				info->lines[info->numLines][1] = score;
				info->lines[info->numLines][2] = ping;
				info->lines[info->numLines][3] = name;
				info->numLines++;
				if (info->numLines >= MAX_SERVERSTATUS_LINES)
					break;
				p = strchr(p, '\\');
				if (!p)
					break;
				*p++ = '\0';
				//
				i++;
			}
		}
		UI_SortServerStatusInfo( info );
		return qtrue;
	}
	return qfalse;
		}

/*
==================
stristr
==================
*/
static char *stristr(char *str, char *charset) {
	int i;

	while(*str) {
		for (i = 0; charset[i] && str[i]; i++) {
			if (toupper(charset[i]) != toupper(str[i])) break;
		}
		if (!charset[i]) return str;
		str++;
	}
	return NULL;
	}

/*
==================
UI_BuildFindPlayerList
==================
*/
static void UI_BuildFindPlayerList(qboolean force) {
	if (!UI_ServerBrowserEnabled()) {
		return;
	}
	static int numFound, numTimeOuts;
	int i, j, resend;
	serverStatusInfo_t info;
	char name[MAX_NAME_LENGTH+2];
	char infoString[MAX_STRING_CHARS];

	if (!force) {
		if (!uiInfo.nextFindPlayerRefresh || uiInfo.nextFindPlayerRefresh > uiInfo.uiDC.realTime) {
			return;
		}
	}
	else {
		memset(&uiInfo.pendingServerStatus, 0, sizeof(uiInfo.pendingServerStatus));
		uiInfo.numFoundPlayerServers = 0;
		uiInfo.currentFoundPlayerServer = 0;
		trap_Cvar_VariableStringBuffer( "ui_findPlayer", uiInfo.findPlayerName, sizeof(uiInfo.findPlayerName));
		Q_CleanStr(uiInfo.findPlayerName);
		// should have a string of some length
		if (!strlen(uiInfo.findPlayerName)) {
			uiInfo.nextFindPlayerRefresh = 0;
			return;
		}
		// set resend time
		resend = ui_serverStatusTimeOut.integer / 2 - 10;
		if (resend < 50) {
			resend = 50;
		}
		trap_Cvar_Set("cl_serverStatusResendTime", va("%d", resend));
		// reset all server status requests
		trap_LAN_ServerStatus( NULL, NULL, 0);
		//
		uiInfo.numFoundPlayerServers = 1;
		Com_sprintf(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1],
						sizeof(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1]),
							"searching %d...", uiInfo.pendingServerStatus.num);
		numFound = 0;
		numTimeOuts++;
	}
	for (i = 0; i < MAX_SERVERSTATUSREQUESTS; i++) {
		// if this pending server is valid
		if (uiInfo.pendingServerStatus.server[i].valid) {
			// try to get the server status for this server
			if (UI_GetServerStatusInfo( uiInfo.pendingServerStatus.server[i].adrstr, &info ) ) {
				//
				numFound++;
				// parse through the server status lines
				for (j = 0; j < info.numLines; j++) {
					// should have ping info
					if ( !info.lines[j][2] || !info.lines[j][2][0] ) {
						continue;
					}
					// clean string first
					Q_strncpyz(name, info.lines[j][3], sizeof(name));
					Q_CleanStr(name);
					// if the player name is a substring
					if (stristr(name, uiInfo.findPlayerName)) {
						// add to found server list if we have space (always leave space for a line with the number found)
						if (uiInfo.numFoundPlayerServers < MAX_FOUNDPLAYER_SERVERS-1) {
							//
							Q_strncpyz(uiInfo.foundPlayerServerAddresses[uiInfo.numFoundPlayerServers-1],
										uiInfo.pendingServerStatus.server[i].adrstr,
											sizeof(uiInfo.foundPlayerServerAddresses[0]));
							Q_strncpyz(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1],
										uiInfo.pendingServerStatus.server[i].name,
											sizeof(uiInfo.foundPlayerServerNames[0]));
							uiInfo.numFoundPlayerServers++;
						}
						else {
							// can't add any more so we're done
							uiInfo.pendingServerStatus.num = uiInfo.serverStatus.numDisplayServers;
						}
					}
				}
				Com_sprintf(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1],
								sizeof(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1]),
									"searching %d/%d...", uiInfo.pendingServerStatus.num, numFound);
				// retrieved the server status so reuse this spot
				uiInfo.pendingServerStatus.server[i].valid = qfalse;
			}
		}
		// if empty pending slot or timed out
		if (!uiInfo.pendingServerStatus.server[i].valid ||
			uiInfo.pendingServerStatus.server[i].startTime < uiInfo.uiDC.realTime - ui_serverStatusTimeOut.integer) {
			if (uiInfo.pendingServerStatus.server[i].valid) {
				numTimeOuts++;
			}
			// reset server status request for this address
			UI_GetServerStatusInfo( uiInfo.pendingServerStatus.server[i].adrstr, NULL );
			// reuse pending slot
			uiInfo.pendingServerStatus.server[i].valid = qfalse;
			// if we didn't try to get the status of all servers in the main browser yet
			if (uiInfo.pendingServerStatus.num < uiInfo.serverStatus.numDisplayServers) {
				uiInfo.pendingServerStatus.server[i].startTime = uiInfo.uiDC.realTime;
				trap_LAN_GetServerAddressString(ui_netSource.integer, uiInfo.serverStatus.displayServers[uiInfo.pendingServerStatus.num],
							uiInfo.pendingServerStatus.server[i].adrstr, sizeof(uiInfo.pendingServerStatus.server[i].adrstr));
				trap_LAN_GetServerInfo(ui_netSource.integer, uiInfo.serverStatus.displayServers[uiInfo.pendingServerStatus.num], infoString, sizeof(infoString));
				Q_strncpyz(uiInfo.pendingServerStatus.server[i].name, Info_ValueForKey(infoString, "hostname"), sizeof(uiInfo.pendingServerStatus.server[0].name));
				uiInfo.pendingServerStatus.server[i].valid = qtrue;
				uiInfo.pendingServerStatus.num++;
				Com_sprintf(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1],
								sizeof(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1]),
									"searching %d/%d...", uiInfo.pendingServerStatus.num, numFound);
			}
		}
	}
	for (i = 0; i < MAX_SERVERSTATUSREQUESTS; i++) {
		if (uiInfo.pendingServerStatus.server[i].valid) {
			break;
		}
	}
	// if still trying to retrieve server status info
	if (i < MAX_SERVERSTATUSREQUESTS) {
		uiInfo.nextFindPlayerRefresh = uiInfo.uiDC.realTime + 25;
	}
	else {
		// add a line that shows the number of servers found
		if (!uiInfo.numFoundPlayerServers) {
			Com_sprintf(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1], sizeof(uiInfo.foundPlayerServerAddresses[0]), "no servers found");
		}
		else {
			Com_sprintf(uiInfo.foundPlayerServerNames[uiInfo.numFoundPlayerServers-1], sizeof(uiInfo.foundPlayerServerAddresses[0]),
						"%d server%s found with player %s", uiInfo.numFoundPlayerServers-1,
						uiInfo.numFoundPlayerServers == 2 ? "":"s", uiInfo.findPlayerName);
		}
		uiInfo.nextFindPlayerRefresh = 0;
		// show the server status info for the selected server
		UI_FeederSelection(FEEDER_FINDPLAYER, uiInfo.currentFoundPlayerServer);
	}
		}

/*
==================
UI_BuildServerStatus
==================
*/
static void UI_BuildServerStatus(qboolean force) {

	if (!UI_ServerBrowserEnabled()) {
		return;
	}

	if (uiInfo.nextFindPlayerRefresh) {
		return;
	}
	if (!force) {
		if (!uiInfo.nextServerStatusRefresh || uiInfo.nextServerStatusRefresh > uiInfo.uiDC.realTime) {
			return;
		}
	}
	else {
		Menu_SetFeederSelection(NULL, FEEDER_SERVERSTATUS, 0, NULL);
		uiInfo.serverStatusInfo.numLines = 0;
		// reset all server status requests
		trap_LAN_ServerStatus( NULL, NULL, 0);
	}
	if (uiInfo.serverStatus.currentServer < 0 || uiInfo.serverStatus.currentServer > uiInfo.serverStatus.numDisplayServers || uiInfo.serverStatus.numDisplayServers == 0) {
		return;
	}
	if (UI_GetServerStatusInfo( uiInfo.serverStatusAddress, &uiInfo.serverStatusInfo ) ) {
		uiInfo.nextServerStatusRefresh = 0;
		UI_GetServerStatusInfo( uiInfo.serverStatusAddress, NULL );
	}
	else {
		uiInfo.nextServerStatusRefresh = uiInfo.uiDC.realTime + 500;
	}
		}

/*
=============
UI_FeederCount

Returns the number of entries available for each UI feeder.
=============
*/
static int UI_FeederCount(float feederID) {
	if (feederID == FEEDER_HEADS) {
		return UI_HeadCountByTeam();
	}

	if (feederID == FEEDER_Q3HEADS) {
		return uiInfo.q3HeadCount;
	}

	if (feederID == FEEDER_MAPS || feederID == FEEDER_ALLMAPS) {
		return UI_MapCountByGameType((feederID == FEEDER_MAPS) ? qtrue : qfalse);
	}

	if (feederID == FEEDER_CVMAPS) {
		return UI_CVMapCountByGameType();
	}

	if (feederID == FEEDER_SERVERS) {
		if (!UI_ServerBrowserEnabled()) {
			return 0;
		}

		return uiInfo.serverStatus.numDisplayServers;
	}

	if (feederID == FEEDER_SERVERSTATUS) {
		return uiInfo.serverStatusInfo.numLines;
	}

	if (feederID == FEEDER_FINDPLAYER) {
		return uiInfo.numFoundPlayerServers;
	}

	if (feederID == FEEDER_PLAYER_LIST) {
		if (uiInfo.uiDC.realTime > uiInfo.playerRefresh) {
			uiInfo.playerRefresh = uiInfo.uiDC.realTime + 3000;
			UI_BuildPlayerList();
		}

		return uiInfo.playerCount;
	}

	if (feederID == FEEDER_TEAM_LIST) {
		if (uiInfo.uiDC.realTime > uiInfo.playerRefresh) {
			uiInfo.playerRefresh = uiInfo.uiDC.realTime + 3000;
			UI_BuildPlayerList();
		}

		return uiInfo.myTeamCount;
	}

	if (feederID == FEEDER_MODS) {
		return uiInfo.modCount;
	}

	if (feederID == FEEDER_CINEMATICS) {
		return uiInfo.movieCount;
	}

	if (feederID == FEEDER_DEMOS) {
		return uiInfo.demoCount;
	}

	if (feederID == FEEDER_COUNTRIES) {
		return uiInfo.countryCount;
	}

	return 0;
}

/*
=============
UI_SelectedMap

Returns the active map entry for a feeder row while reporting the backing index.
=============
*/
static const char *UI_SelectedMap(int index, int *actual) {
	int i, c;

	c = 0;
	*actual = 0;
	for (i = 0; i < uiInfo.mapCount; i++) {
		if (uiInfo.mapList[i].active) {
			if (c == index) {
				*actual = i;
				return uiInfo.mapList[i].mapName;
			}

			c++;
		}
	}

	return "";
}

static const char *UI_SelectedHead(int index, int *actual) {
	int i, c;
	c = 0;
	*actual = 0;
	for (i = 0; i < uiInfo.characterCount; i++) {
		if (uiInfo.characterList[i].active) {
			if (c == index) {
				*actual = i;
				return uiInfo.characterList[i].name;
			} else {
				c++;
			}
		}
	}
	return "";
		}

/*
=============
UI_GetIndexFromSelection

Converts a backing map index into the display slot while skipping inactive arenas.
=============
*/
static int UI_GetIndexFromSelection(int actual) {
	int i;
	int c;

	c = 0;
	for (i = 0; i < uiInfo.mapCount; i++) {
		if (uiInfo.mapList[i].active) {
			if (i == actual) {
				return c;
			}
			c++;
		}
	}

	return 0;
		}

/*
=============
UI_GetCallvoteGametypeToken

Returns the retail short factory token for the selected callvote gametype.
=============
*/
static const char *UI_GetCallvoteGametypeToken(int gametype) {
	switch (gametype) {
		case GT_FFA:
			return "ffa";
		case GT_TOURNAMENT:
			return "duel";
		case GT_SINGLE_PLAYER:
			return "race";
		case GT_TEAM:
			return "tdm";
		case GT_CLAN_ARENA:
			return "ca";
		case GT_CTF:
			return "ctf";
		case GT_1FCTF:
			return "oneflag";
		case GT_HARVESTER:
			return "har";
		case GT_FREEZE:
			return "ft";
		case GT_DOMINATION:
			return "dom";
		case GT_ATTACK_DEFEND:
			return "ad";
		case GT_RED_ROVER:
			return "rr";
		default:
			return "";
	}
		}

/*
=============
UI_GetFilteredCallvoteGametype

Normalizes the callvote gametype filter so out-of-range values fall back to Default.
=============
*/
static int UI_GetFilteredCallvoteGametype(void) {
	int gametype;

	gametype = ui_cvGameType.integer;
	if (gametype < -1 || gametype >= GT_MAX_GAME_TYPE) {
			return -1;
	}

	return gametype;
		}

/*
=============
UI_ParseCallvoteGametypeToken

Converts textual factory tokens to the corresponding gametype enumeration.
=============
*/
int UI_ParseCallvoteGametypeToken(const char *token) {
	int value;

	if (token == NULL || token[0] == '\0') {
			return -1;
	}

	if (token[0] == '-' || (token[0] >= '0' && token[0] <= '9')) {
		value = atoi(token);
		if (value >= -1 && value < GT_MAX_GAME_TYPE) {
			return value;
		}
	}

	if (!Q_stricmp(token, "default")) {
			return -1;
	}
	if (!Q_stricmp(token, "ffa") || !Q_stricmp(token, "dm")
		|| !Q_stricmp(token, "freeforall") || !Q_stricmp(token, "free for all")) {
		return GT_FFA;
	}
	if (!Q_stricmp(token, "duel") || !Q_stricmp(token, "tournament")) {
		return GT_TOURNAMENT;
	}
	if (!Q_stricmp(token, "race") || !Q_stricmp(token, "singleplayer") || !Q_stricmp(token, "sp")) {
		return GT_SINGLE_PLAYER;
	}
	if (!Q_stricmp(token, "tdm") || !Q_stricmp(token, "team") || !Q_stricmp(token, "team deathmatch")) {
		return GT_TEAM;
	}
	if (!Q_stricmp(token, "clanarena") || !Q_stricmpn(token, "ca", 2)) {
		return GT_CLAN_ARENA;
	}
	if (!Q_stricmp(token, "ctf")) {
		return GT_CTF;
	}
	if (!Q_stricmp(token, "oneflag") || !Q_stricmp(token, "1fctf") || !Q_stricmpn(token, "1f", 2)) {
		return GT_1FCTF;
	}
	if (!Q_stricmp(token, "overload") || !Q_stricmp(token, "obelisk")) {
		return GT_OBELISK;
	}
	if (!Q_stricmp(token, "harvester") || !Q_stricmp(token, "har")) {
		return GT_HARVESTER;
	}
	if (!Q_stricmp(token, "freeze") || !Q_stricmp(token, "freezetag") || !Q_stricmpn(token, "ft", 2)) {
		return GT_FREEZE;
	}
	if (!Q_stricmp(token, "domination") || !Q_stricmp(token, "dom")) {
		return GT_DOMINATION;
	}
	if (!Q_stricmp(token, "attackdefend") || !Q_stricmp(token, "attack defend") || !Q_stricmp(token, "ad")) {
		return GT_ATTACK_DEFEND;
	}
	if (!Q_stricmp(token, "redrover") || !Q_stricmp(token, "rr")) {
		return GT_RED_ROVER;
	}

		return -1;
		}

/*
=============
UI_GetCallvoteRotationGametype

Derives the gametype associated with a cached rotation entry.
=============
*/
static int UI_GetCallvoteRotationGametype(const mapRotationInfo_t *rotation) {
	int gametype;

	if (rotation == NULL) {
			return -1;
	}

	if (rotation->factoryGameType[0]) {
		gametype = UI_ParseCallvoteGametypeToken(rotation->factoryGameType);
		if (gametype >= -1) {
			return gametype;
		}
	}

	if (rotation->factoryId[0]) {
		gametype = UI_ParseCallvoteGametypeToken(rotation->factoryId);
		if (gametype >= -1) {
			return gametype;
		}
	}

		return -1;
		}

/*
=============
UI_RotationMatchesGametype

Checks whether a rotation entry should be displayed for the active gametype filter.
=============
*/
static qboolean UI_RotationMatchesGametype(const mapRotationInfo_t *rotation, int gametype) {
	int entryGametype;

	if (rotation == NULL) {
		return qfalse;
	}

	if (gametype < 0) {
		return qtrue;
	}

	entryGametype = UI_GetCallvoteRotationGametype(rotation);
	if (entryGametype < 0) {
		return qfalse;
	}

	return (entryGametype == gametype) ? qtrue : qfalse;
		}

/*
=============
UI_CVMapCountByGameType

Builds the retail callvote-visible map slab from the filtered rotation cache.
=============
*/
static int UI_CVMapCountByGameType(void) {
	int count;
	int gametype;
	int i;

	count = 0;
	gametype = UI_GetFilteredCallvoteGametype();
	for (i = 0; i < uiInfo.mapCount; i++) {
		uiInfo.mapList[i].active = qfalse;
	}

	for (i = 0; i < uiInfo.mapRotationCount; i++) {
		int mapIndex;

		if (!UI_RotationMatchesGametype(&uiInfo.mapRotations[i], gametype)) {
			continue;
		}

		mapIndex = uiInfo.mapRotations[i].mapIndex;
		if (mapIndex < 0 || mapIndex >= uiInfo.mapCount) {
			continue;
		}
		if (uiInfo.mapList[mapIndex].active) {
			continue;
		}

		uiInfo.mapList[mapIndex].active = qtrue;
		count++;
	}

	return count;
		}

/*
=============
UI_SelectCallvoteMap

Applies the retail FEEDER_CVMAPS selection side effects after rebuilding the
callvote-visible map set for the current filter.
=============
*/
static void UI_SelectCallvoteMap(int index) {
	int actual;
	int available;

	available = UI_CVMapCountByGameType();
	if (index < 0 || index >= available) {
		return;
	}

	UI_SelectedMap(index, &actual);
	if (actual < 0 || actual >= uiInfo.mapCount || !uiInfo.mapList[actual].active) {
		return;
	}

	trap_Cvar_Set("ui_mapIndex", va("%d", index));
	ui_mapIndex.integer = index;
	UI_SetCurrentNetMap(actual);
}

/*
=============
UI_SetCurrentNetMap

Centralizes the shared net-map cinematic playback wiring.
=============
*/
static void UI_SetCurrentNetMap(int mapIndex) {
	int previous;

	if (mapIndex < 0 || mapIndex >= uiInfo.mapCount) {
		return;
	}

	previous = ui_currentNetMap.integer;
	if (previous >= 0 && previous < uiInfo.mapCount) {
		if (uiInfo.mapList[previous].cinematic >= 0) {
			trap_CIN_StopCinematic(uiInfo.mapList[previous].cinematic);
			uiInfo.mapList[previous].cinematic = -1;
		}
	}

	ui_currentNetMap.integer = mapIndex;
	trap_Cvar_Set("ui_currentNetMap", va("%d", mapIndex));

	if (uiInfo.mapList[mapIndex].cinematic >= 0) {
		trap_CIN_StopCinematic(uiInfo.mapList[mapIndex].cinematic);
		uiInfo.mapList[mapIndex].cinematic = -1;
	}

	uiInfo.mapList[mapIndex].cinematic = trap_CIN_PlayCinematic(
		va("%s.roq", uiInfo.mapList[mapIndex].mapLoadName), 0, 0, 0, 0, (CIN_loop | CIN_silent));
		}

static void UI_UpdatePendingPings() { 
	if (!UI_ServerBrowserEnabled()) {
		return;
	}
	trap_LAN_ResetPings(ui_netSource.integer);
	uiInfo.serverStatus.refreshActive = qtrue;
	uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime + 1000;

		}

/*
=============
UI_FeederItemText

Returns the display text for each feeder entry while leaving selection effects
to UI_FeederSelection.
=============
*/
static const char *UI_FeederItemText(float feederID, int index, int column, qhandle_t *handle) {
        static char info[MAX_STRING_CHARS];
        static char hostname[1024];
        static char clientBuff[32];
        static int lastColumn = -1;
        static int lastTime = 0;
        *handle = -1;
        if (feederID == FEEDER_HEADS) {
                int actual;
                return UI_SelectedHead(index, &actual);
        } else if (feederID == FEEDER_Q3HEADS) {
                if (index >= 0 && index < uiInfo.q3HeadCount) {
                        return uiInfo.q3HeadNames[index];
                }
        } else if (feederID == FEEDER_MAPS || feederID == FEEDER_ALLMAPS) {
                int actual;
                return UI_SelectedMap(index, &actual);
        } else if (feederID == FEEDER_CVMAPS) {
				int actual;

				UI_CVMapCountByGameType();
				return UI_SelectedMap(index, &actual);
        } else if (feederID == FEEDER_SERVERS) {
                if (!UI_ServerBrowserEnabled()) {
                        return "";
                }
                if (index >= 0 && index < uiInfo.serverStatus.numDisplayServers) {
                        int ping, game, punkbuster;
                        if (lastColumn != column || lastTime > uiInfo.uiDC.realTime + 5000) {
                                trap_LAN_GetServerInfo(ui_netSource.integer, uiInfo.serverStatus.displayServers[index], info, MAX_STRING_CHARS);
                                lastColumn = column;
                                lastTime = uiInfo.uiDC.realTime;
                        }
                        ping = atoi(Info_ValueForKey(info, "ping"));
                        if (ping == -1) {
                                // if we ever see a ping that is out of date, do a server refresh
                                // UI_UpdatePendingPings();
                        }
                        switch (column) {
                                case SORT_HOST :
                                        if (ping <= 0) {
                                                return Info_ValueForKey(info, "addr");
                                        } else {
                                                if ( ui_netSource.integer == AS_LOCAL ) {
                                                        Com_sprintf( hostname, sizeof(hostname), "%s [%s]",
                                                                                        Info_ValueForKey(info, "hostname"),
                                                                                        netnames[atoi(Info_ValueForKey(info, "nettype"))] );
                                                        return hostname;
                                                }
                                                else {
                                                        Com_sprintf( hostname, sizeof(hostname), "%s", Info_ValueForKey(info, "hostname"));
                                                        return hostname;
                                                }
                                        }
                                case SORT_MAP : return Info_ValueForKey(info, "mapname");
                                case SORT_CLIENTS :
                                        Com_sprintf( clientBuff, sizeof(clientBuff), "%s (%s)", Info_ValueForKey(info, "clients"), Info_ValueForKey(info, "sv_maxclients"));
                                        return clientBuff;
                                case SORT_GAME :
                                        game = atoi(Info_ValueForKey(info, "gametype"));
                                        if (game >= 0 && game < numTeamArenaGameTypes) {
                                                return teamArenaGameTypes[game];
                                        } else {
                                                return "Unknown";
                                        }
                                case SORT_PING :
                                        if (ping <= 0) {
                                                return "...";
                                        } else {
                                                return Info_ValueForKey(info, "ping");
                                        }
                                case SORT_PUNKBUSTER:
                                        punkbuster = atoi(Info_ValueForKey(info, "punkbuster"));
                                        if ( punkbuster ) {
                                                return "Yes";
                                        } else {
                                                return "No";
                                        }
                        }
                }
        } else if (feederID == FEEDER_SERVERSTATUS) {
                if ( index >= 0 && index < uiInfo.serverStatusInfo.numLines ) {
                        if ( column >= 0 && column < 4 ) {
                                return uiInfo.serverStatusInfo.lines[index][column];
                        }
                }
        } else if (feederID == FEEDER_FINDPLAYER) {
                if ( index >= 0 && index < uiInfo.numFoundPlayerServers ) {
                        //return uiInfo.foundPlayerServerAddresses[index];
                        return uiInfo.foundPlayerServerNames[index];
                }
        } else if (feederID == FEEDER_PLAYER_LIST) {
                if (index >= 0 && index < uiInfo.playerCount) {
                        return uiInfo.playerNames[index];
                }
        } else if (feederID == FEEDER_TEAM_LIST) {
                if (index >= 0 && index < uiInfo.myTeamCount) {
                        return uiInfo.teamNames[index];
                }
        } else if (feederID == FEEDER_MODS) {
if (index >= 0 && index < uiInfo.modCount) {
if (uiInfo.modList[index].modDescr && *uiInfo.modList[index].modDescr) {
        return uiInfo.modList[index].modDescr;
		} else {
        return uiInfo.modList[index].modName;
}
}
        } else if (feederID == FEEDER_CINEMATICS) {
        if (index >= 0 && index < uiInfo.movieCount) {
        return uiInfo.movieList[index];
}
        } else if (feederID == FEEDER_DEMOS) {
        if (index >= 0 && index < uiInfo.demoCount) {
        return uiInfo.demoList[index];
}
	} else if (feederID == FEEDER_COUNTRIES) {
		if (index >= 0 && index < uiInfo.countryCount) {
			return uiInfo.countryList[index];
		}
	}
	return "";
	}

	static qhandle_t UI_FeederItemImage(float feederID, int index) {
	if (feederID == FEEDER_HEADS) {
	int actual;
	UI_SelectedHead(index, &actual);
	index = actual;
	if (index >= 0 && index < uiInfo.characterCount) {
		if (uiInfo.characterList[index].headImage == -1) {
			uiInfo.characterList[index].headImage = trap_R_RegisterShaderNoMip(uiInfo.characterList[index].imageName);
		}
		return uiInfo.characterList[index].headImage;
	}
	} else if (feederID == FEEDER_Q3HEADS) {
	if (index >= 0 && index < uiInfo.q3HeadCount) {
	return uiInfo.q3HeadIcons[index];
	}
	} else if (feederID == FEEDER_ALLMAPS || feederID == FEEDER_MAPS) {
		int actual;
		UI_SelectedMap(index, &actual);
		index = actual;
		if (index >= 0 && index < uiInfo.mapCount) {
			if (uiInfo.mapList[index].levelShot == -1) {
				uiInfo.mapList[index].levelShot = trap_R_RegisterShaderNoMip(uiInfo.mapList[index].imageName);
			}
			return uiInfo.mapList[index].levelShot;
		}
	} else if (feederID == FEEDER_CVMAPS) {
		int actual;

		UI_CVMapCountByGameType();
		UI_SelectedMap(index, &actual);
		if (actual >= 0 && actual < uiInfo.mapCount && uiInfo.mapList[actual].active) {
			if (uiInfo.mapList[actual].levelShot == -1) {
				uiInfo.mapList[actual].levelShot = trap_R_RegisterShaderNoMip(uiInfo.mapList[actual].imageName);
			}
	return uiInfo.mapList[actual].levelShot;
	}
	}

	return 0;
	}

	/*
	=============
	UI_FeederSelection

	Handles selection side effects when a feeder item is chosen.
	=============
	*/
	static void UI_FeederSelection(float feederID, int index) {
	static char info[MAX_STRING_CHARS];
	  if (feederID == FEEDER_HEADS) {
	int actual;
	UI_SelectedHead(index, &actual);
	index = actual;
	    if (index >= 0 && index < uiInfo.characterCount) {
		trap_Cvar_Set( "team_model", va("%s", uiInfo.characterList[index].base));
		trap_Cvar_Set( "team_headmodel", va("*%s", uiInfo.characterList[index].name)); 
		updateModel = qtrue;
	    }
	  } else if (feederID == FEEDER_Q3HEADS) {
	    if (index >= 0 && index < uiInfo.q3HeadCount) {
	      trap_Cvar_Set( "model", uiInfo.q3HeadNames[index]);
	      trap_Cvar_Set( "headmodel", uiInfo.q3HeadNames[index]);
			updateModel = qtrue;
		}
	} else if (feederID == FEEDER_MAPS || feederID == FEEDER_ALLMAPS) {
	    int actual, previous, map;
		map = (feederID == FEEDER_ALLMAPS) ? ui_currentNetMap.integer : ui_currentMap.integer;
		if (uiInfo.mapList[map].cinematic >= 0) {
		  trap_CIN_StopCinematic(uiInfo.mapList[map].cinematic);
		  uiInfo.mapList[map].cinematic = -1;
		}
		UI_SelectedMap(index, &actual);
		trap_Cvar_Set("ui_mapIndex", va("%d", index));
		ui_mapIndex.integer = index;

		if (feederID == FEEDER_MAPS) {
			previous = ui_currentMap.integer;
			if (previous >= 0 && previous < uiInfo.mapCount) {
				if (uiInfo.mapList[previous].cinematic >= 0) {
					trap_CIN_StopCinematic(uiInfo.mapList[previous].cinematic);
					uiInfo.mapList[previous].cinematic = -1;
				}
			}

			ui_currentMap.integer = actual;
			trap_Cvar_Set("ui_currentMap", va("%d", actual));
			uiInfo.mapList[ui_currentMap.integer].cinematic = trap_CIN_PlayCinematic(
				va("%s.roq", uiInfo.mapList[ui_currentMap.integer].mapLoadName), 0, 0, 0, 0, (CIN_loop | CIN_silent));
			UI_LoadBestScores(uiInfo.mapList[ui_currentMap.integer].mapLoadName, uiInfo.gameTypes[ui_gameType.integer].gtEnum);
			trap_Cvar_Set("ui_opponentModel", uiInfo.mapList[ui_currentMap.integer].opponentName);
			updateOpponentModel = qtrue;
		} else {
			UI_SetCurrentNetMap(actual);
		}
	} else if (feederID == FEEDER_CVMAPS) {
		UI_SelectCallvoteMap(index);
	} else if (feederID == FEEDER_SERVERS) {
	const char *mapName = NULL;

	if (!UI_ServerBrowserEnabled()) {
	return;
	}

	if (index < 0 || index >= uiInfo.serverStatus.numDisplayServers) {
	return;
	}

	uiInfo.serverStatus.currentServer = index;
	trap_LAN_GetServerInfo(ui_netSource.integer, uiInfo.serverStatus.displayServers[index], info, MAX_STRING_CHARS);
	uiInfo.serverStatus.currentServerPreview = trap_R_RegisterShaderNoMip(va("levelshots/%s", Info_ValueForKey(info, "mapname")));
	if (uiInfo.serverStatus.currentServerCinematic >= 0) {
	trap_CIN_StopCinematic(uiInfo.serverStatus.currentServerCinematic);
	uiInfo.serverStatus.currentServerCinematic = -1;
	}
	mapName = Info_ValueForKey(info, "mapname");
	if (mapName && *mapName) {
	uiInfo.serverStatus.currentServerCinematic = trap_CIN_PlayCinematic(va("%s.roq", mapName), 0, 0, 0, 0, (CIN_loop | CIN_silent));
	}
	  } else if (feederID == FEEDER_SERVERSTATUS) {
		//
	  } else if (feederID == FEEDER_FINDPLAYER) {
	  uiInfo.currentFoundPlayerServer = index;
	  //
	  if ( index < uiInfo.numFoundPlayerServers-1) {
			// build a new server status for this server
			Q_strncpyz(uiInfo.serverStatusAddress, uiInfo.foundPlayerServerAddresses[uiInfo.currentFoundPlayerServer], sizeof(uiInfo.serverStatusAddress));
			Menu_SetFeederSelection(NULL, FEEDER_SERVERSTATUS, 0, NULL);
			UI_BuildServerStatus(qtrue);
	  }
	  } else if (feederID == FEEDER_PLAYER_LIST) {
		uiInfo.playerIndex = index;
	  } else if (feederID == FEEDER_TEAM_LIST) {
		uiInfo.teamIndex = index;
	  } else if (feederID == FEEDER_MODS) {
		uiInfo.modIndex = index;
	  } else if (feederID == FEEDER_CINEMATICS) {
		uiInfo.movieIndex = index;
		if (uiInfo.previewMovie >= 0) {
		  trap_CIN_StopCinematic(uiInfo.previewMovie);
		}
		uiInfo.previewMovie = -1;
	} else if (feederID == FEEDER_DEMOS) {
		uiInfo.demoIndex = index;
	} else if (feederID == FEEDER_COUNTRIES) {
		if (index >= 0 && index < uiInfo.countryCount) {
			trap_Cvar_Set("ui_country", uiInfo.countryList[index]);
	}
	}
		}

static qboolean Team_Parse(char **p) {
  char *token;
  const char *tempStr;
	int i;

  token = COM_ParseExt(p, qtrue);

  if (token[0] != '{') {
    return qfalse;
  }

  while ( 1 ) {

    token = COM_ParseExt(p, qtrue);
    
    if (Q_stricmp(token, "}") == 0) {
      return qtrue;
    }

    if ( !token || token[0] == 0 ) {
      return qfalse;
    }

    if (token[0] == '{') {
      // seven tokens per line, team name and icon, and 5 team member names
      if (!String_Parse(p, &uiInfo.teamList[uiInfo.teamCount].teamName) || !String_Parse(p, &tempStr)) {
        return qfalse;
      }
    

			uiInfo.teamList[uiInfo.teamCount].imageName = tempStr;
	    uiInfo.teamList[uiInfo.teamCount].teamIcon = trap_R_RegisterShaderNoMip(uiInfo.teamList[uiInfo.teamCount].imageName);
		  uiInfo.teamList[uiInfo.teamCount].teamIcon_Metal = trap_R_RegisterShaderNoMip(va("%s_metal",uiInfo.teamList[uiInfo.teamCount].imageName));
			uiInfo.teamList[uiInfo.teamCount].teamIcon_Name = trap_R_RegisterShaderNoMip(va("%s_name", uiInfo.teamList[uiInfo.teamCount].imageName));

			uiInfo.teamList[uiInfo.teamCount].cinematic = -1;

			for (i = 0; i < TEAM_MEMBERS; i++) {
				uiInfo.teamList[uiInfo.teamCount].teamMembers[i] = NULL;
				if (!String_Parse(p, &uiInfo.teamList[uiInfo.teamCount].teamMembers[i])) {
					return qfalse;
				}
			}

      Com_Printf("Loaded team %s with team icon %s.\n", uiInfo.teamList[uiInfo.teamCount].teamName, tempStr);
      if (uiInfo.teamCount < MAX_TEAMS) {
        uiInfo.teamCount++;
      } else {
        Com_Printf("Too many teams, last team replaced!\n");
      }
      token = COM_ParseExt(p, qtrue);
      if (token[0] != '}') {
        return qfalse;
      }
    }
  }

  return qfalse;
		}

static qboolean Character_Parse(char **p) {
  char *token;
  const char *tempStr;

  token = COM_ParseExt(p, qtrue);

  if (token[0] != '{') {
    return qfalse;
  }


  while ( 1 ) {
    token = COM_ParseExt(p, qtrue);

    if (Q_stricmp(token, "}") == 0) {
      return qtrue;
    }

    if ( !token || token[0] == 0 ) {
      return qfalse;
    }

    if (token[0] == '{') {
      // two tokens per line, character name and sex
      if (!String_Parse(p, &uiInfo.characterList[uiInfo.characterCount].name) || !String_Parse(p, &tempStr)) {
        return qfalse;
      }
    
      uiInfo.characterList[uiInfo.characterCount].headImage = -1;
			uiInfo.characterList[uiInfo.characterCount].imageName = String_Alloc(va("models/players/heads/%s/icon_default.tga", uiInfo.characterList[uiInfo.characterCount].name));

	  if (tempStr && (!Q_stricmp(tempStr, "female"))) {
        uiInfo.characterList[uiInfo.characterCount].base = String_Alloc(va("Janet"));
      } else if (tempStr && (!Q_stricmp(tempStr, "male"))) {
        uiInfo.characterList[uiInfo.characterCount].base = String_Alloc(va("James"));
	  } else {
        uiInfo.characterList[uiInfo.characterCount].base = String_Alloc(va("%s",tempStr));
	  }

      Com_Printf("Loaded %s character %s.\n", uiInfo.characterList[uiInfo.characterCount].base, uiInfo.characterList[uiInfo.characterCount].name);
      if (uiInfo.characterCount < MAX_HEADS) {
        uiInfo.characterCount++;
      } else {
        Com_Printf("Too many characters, last character replaced!\n");
      }
     
      token = COM_ParseExt(p, qtrue);
      if (token[0] != '}') {
        return qfalse;
      }
    }
  }

  return qfalse;
		}


static qboolean Alias_Parse(char **p) {
  char *token;

  token = COM_ParseExt(p, qtrue);

  if (token[0] != '{') {
    return qfalse;
  }

  while ( 1 ) {
    token = COM_ParseExt(p, qtrue);

    if (Q_stricmp(token, "}") == 0) {
      return qtrue;
    }

    if ( !token || token[0] == 0 ) {
      return qfalse;
    }

    if (token[0] == '{') {
      // three tokens per line, character name, bot alias, and preferred action a - all purpose, d - defense, o - offense
      if (!String_Parse(p, &uiInfo.aliasList[uiInfo.aliasCount].name) || !String_Parse(p, &uiInfo.aliasList[uiInfo.aliasCount].ai) || !String_Parse(p, &uiInfo.aliasList[uiInfo.aliasCount].action)) {
        return qfalse;
      }
    
      Com_Printf("Loaded character alias %s using character ai %s.\n", uiInfo.aliasList[uiInfo.aliasCount].name, uiInfo.aliasList[uiInfo.aliasCount].ai);
      if (uiInfo.aliasCount < MAX_ALIASES) {
        uiInfo.aliasCount++;
      } else {
        Com_Printf("Too many aliases, last alias replaced!\n");
      }
     
      token = COM_ParseExt(p, qtrue);
      if (token[0] != '}') {
        return qfalse;
      }
    }
  }

  return qfalse;
		}



// mode 
// 0 - high level parsing
// 1 - team parsing
// 2 - character parsing
static void UI_ParseTeamInfo(const char *teamFile) {
	char	*token;
  char *p;
  char *buff = NULL;
  //static int mode = 0; TTimo: unused

  buff = GetMenuBuffer(teamFile);
  if (!buff) {
    return;
  }

  p = buff;

	while ( 1 ) {
		token = COM_ParseExt( &p, qtrue );
		if( !token || token[0] == 0 || token[0] == '}') {
			break;
		}

		if ( Q_stricmp( token, "}" ) == 0 ) {
      break;
    }

    if (Q_stricmp(token, "teams") == 0) {

      if (Team_Parse(&p)) {
        continue;
      } else {
        break;
      }
    }

    if (Q_stricmp(token, "characters") == 0) {
      Character_Parse(&p);
    }

    if (Q_stricmp(token, "aliases") == 0) {
      Alias_Parse(&p);
    }

  }

		}


static qboolean GameType_Parse(char **p, qboolean join) {
	char *token;

	token = COM_ParseExt(p, qtrue);

	if (token[0] != '{') {
		return qfalse;
	}

	if (join) {
		uiInfo.numJoinGameTypes = 0;
	} else {
		uiInfo.numGameTypes = 0;
	}

	while ( 1 ) {
		token = COM_ParseExt(p, qtrue);

		if (Q_stricmp(token, "}") == 0) {
			return qtrue;
		}

		if ( !token || token[0] == 0 ) {
			return qfalse;
		}

		if (token[0] == '{') {
			// two tokens per line, character name and sex
			if (join) {
				if (!String_Parse(p, &uiInfo.joinGameTypes[uiInfo.numJoinGameTypes].gameType) || !Int_Parse(p, &uiInfo.joinGameTypes[uiInfo.numJoinGameTypes].gtEnum)) {
					return qfalse;
				}
			} else {
				if (!String_Parse(p, &uiInfo.gameTypes[uiInfo.numGameTypes].gameType) || !Int_Parse(p, &uiInfo.gameTypes[uiInfo.numGameTypes].gtEnum)) {
					return qfalse;
				}
			}
    
			if (join) {
				if (uiInfo.numJoinGameTypes < MAX_GAMETYPES) {
					uiInfo.numJoinGameTypes++;
				} else {
					Com_Printf("Too many net game types, last one replace!\n");
				}		
			} else {
				if (uiInfo.numGameTypes < MAX_GAMETYPES) {
					uiInfo.numGameTypes++;
				} else {
					Com_Printf("Too many game types, last one replace!\n");
				}		
			}
     
			token = COM_ParseExt(p, qtrue);
			if (token[0] != '}') {
				return qfalse;
			}
		}
	}
	return qfalse;
		}

static qboolean MapList_Parse(char **p) {
	char *token;

	token = COM_ParseExt(p, qtrue);

	if (token[0] != '{') {
		return qfalse;
	}

	uiInfo.mapCount = 0;

	while ( 1 ) {
		token = COM_ParseExt(p, qtrue);

		if (Q_stricmp(token, "}") == 0) {
			return qtrue;
		}

		if ( !token || token[0] == 0 ) {
			return qfalse;
		}

		if (token[0] == '{') {
			if (!String_Parse(p, &uiInfo.mapList[uiInfo.mapCount].mapName) || !String_Parse(p, &uiInfo.mapList[uiInfo.mapCount].mapLoadName) 
				||!Int_Parse(p, &uiInfo.mapList[uiInfo.mapCount].teamMembers) ) {
				return qfalse;
			}

			if (!String_Parse(p, &uiInfo.mapList[uiInfo.mapCount].opponentName)) {
				return qfalse;
			}

			uiInfo.mapList[uiInfo.mapCount].typeBits = 0;

			while (1) {
				token = COM_ParseExt(p, qtrue);
				if (token[0] >= '0' && token[0] <= '9') {
					uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << (token[0] - 0x030));
					if (!Int_Parse(p, &uiInfo.mapList[uiInfo.mapCount].timeToBeat[token[0] - 0x30])) {
						return qfalse;
					}
				} else {
					break;
				} 
			}

			//mapList[mapCount].imageName = String_Alloc(va("levelshots/%s", mapList[mapCount].mapLoadName));
			//if (uiInfo.mapCount == 0) {
			  // only load the first cinematic, selection loads the others
  			//  uiInfo.mapList[uiInfo.mapCount].cinematic = trap_CIN_PlayCinematic(va("%s.roq",uiInfo.mapList[uiInfo.mapCount].mapLoadName), qfalse, qfalse, qtrue, 0, 0, 0, 0);
			//}
  		uiInfo.mapList[uiInfo.mapCount].cinematic = -1;
			uiInfo.mapList[uiInfo.mapCount].levelShot = trap_R_RegisterShaderNoMip(va("levelshots/%s_small", uiInfo.mapList[uiInfo.mapCount].mapLoadName));

			if (uiInfo.mapCount < MAX_MAPS) {
				uiInfo.mapCount++;
			} else {
				Com_Printf("Too many maps, last one replaced!\n");
			}
		}
	}
	return qfalse;
		}

static void UI_ParseGameInfo(const char *teamFile) {
	char	*token;
	char *p;
	char *buff = NULL;
	//int mode = 0; TTimo: unused

	buff = GetMenuBuffer(teamFile);
	if (!buff) {
		return;
	}

	p = buff;

	while ( 1 ) {
		token = COM_ParseExt( &p, qtrue );
		if( !token || token[0] == 0 || token[0] == '}') {
			break;
		}

		if ( Q_stricmp( token, "}" ) == 0 ) {
			break;
		}

		if (Q_stricmp(token, "gametypes") == 0) {

			if (GameType_Parse(&p, qfalse)) {
				continue;
			} else {
				break;
			}
		}

		if (Q_stricmp(token, "joingametypes") == 0) {

			if (GameType_Parse(&p, qtrue)) {
				continue;
			} else {
				break;
			}
		}

		if (Q_stricmp(token, "maps") == 0) {
			// start a new menu
			MapList_Parse(&p);
		}

	}
		}

/*
=============
UI_Pause

Pause or resume the client while toggling the UI keycatcher.
=============
*/
static void UI_Pause(qboolean b) {
	if (b) {
		// pause the game and set the ui keycatcher
		trap_Cvar_Set( "cl_paused", "1" );
		trap_Key_SetCatcher( KEYCATCH_UI );
	} else {
		// unpause the game and clear the ui keycatcher
		trap_Key_SetCatcher( trap_Key_GetCatcher() & ~KEYCATCH_UI );
		trap_Key_ClearStates();
		trap_Cvar_Set( "cl_paused", "0" );
	}
		}


/*
=============
UI_LauncherPlayCinematic

Play a silent cinematic for launcher surfaces, registering a renderer-owned shader handle.
Arguments mirror the legacy autoplay hook: path, loop toggle, and optional width/height.
=============
*/
static qhandle_t UI_LauncherPlayCinematic(const char *name, qboolean loop, int width, int height) {
	int flags = CIN_silent | CIN_shader;

	if (loop) {
		flags |= CIN_loop;
	}

	return trap_CIN_PlayCinematic(name, 0, 0, width, height, flags);
		}

/*
=============
UI_PlayCinematic

Fallback UI cinematic helper for silent looping playback without shader registration.
=============
*/
static int UI_PlayCinematic(const char *name, float x, float y, float w, float h) {
	return trap_CIN_PlayCinematic(name, x, y, w, h, (CIN_loop | CIN_silent));
		}

/*
=============
UI_StopCinematic
=============
*/
static void UI_StopCinematic(int handle) {
	if (handle >= 0) {
		trap_CIN_StopCinematic(handle);
	} else {
		handle = abs(handle);
		if (handle == UI_MAPCINEMATIC) {
			if (uiInfo.mapList[ui_currentMap.integer].cinematic >= 0) {
				trap_CIN_StopCinematic(uiInfo.mapList[ui_currentMap.integer].cinematic);
				uiInfo.mapList[ui_currentMap.integer].cinematic = -1;
			}
		} else if (handle == UI_NETMAPCINEMATIC) {
			if (uiInfo.serverStatus.currentServerCinematic >= 0) {
				trap_CIN_StopCinematic(uiInfo.serverStatus.currentServerCinematic);
				uiInfo.serverStatus.currentServerCinematic = -1;
			}
		} else if (handle == UI_CLANCINEMATIC) {
			int i = UI_TeamIndexFromName(UI_Cvar_VariableString("ui_teamName"));
			if (i >= 0 && i < uiInfo.teamCount) {
				if (uiInfo.teamList[i].cinematic >= 0) {
					trap_CIN_StopCinematic(uiInfo.teamList[i].cinematic);
					uiInfo.teamList[i].cinematic = -1;
				}
			}
		}
	}
		}


/*
=============
UI_DrawCinematic
=============
*/
static void UI_DrawCinematic(int handle, float x, float y, float w, float h) {
	trap_CIN_SetExtents(handle, x, y, w, h);
	trap_CIN_DrawCinematic(handle);
		}

/*
=============
UI_RunCinematicFrame
=============
*/
static void UI_RunCinematicFrame(int handle) {
	trap_CIN_RunCinematic(handle);
		}

typedef struct {
	char		modelName[64];
	char		skinName[64];
	qhandle_t	iconShader;
	int			hasValidatedSkin;
} uiPlayerModelEntry_t;

static uiPlayerModelEntry_t ui_playerModelEntries[MAX_PLAYERMODELS];
static int ui_playerModelEntryCount;

/*
=================
UI_PlayerModelSkinIsAlias
=================
*/
static qboolean UI_PlayerModelSkinIsAlias( const char *skinName ) {
	if ( !skinName || !skinName[0] ) {
		return qfalse;
	}

	return (Q_stricmp( skinName, "blue" ) == 0 ||
		Q_stricmp( skinName, "bright" ) == 0 ||
		Q_stricmp( skinName, "red" ) == 0 ||
		Q_stricmp( skinName, "sport" ) == 0 ||
		Q_stricmp( skinName, "sport_blue" ) == 0 ||
		Q_stricmp( skinName, "sport_red" ) == 0) ? qtrue : qfalse;
}

/*
=================
UI_AddPlayerModelEntry
=================
*/
static void UI_AddPlayerModelEntry( const char *modelName, const char *skinName, const char *iconShaderName ) {
	int i;
	uiPlayerModelEntry_t *entry;

	if ( !modelName || !modelName[0] || !skinName || !skinName[0] || !iconShaderName || !iconShaderName[0] ) {
		return;
	}

	for ( i = 0; i < ui_playerModelEntryCount; i++ ) {
		if ( Q_stricmp( ui_playerModelEntries[i].modelName, modelName ) == 0 &&
			Q_stricmp( ui_playerModelEntries[i].skinName, skinName ) == 0 ) {
			return;
		}
	}

	if ( ui_playerModelEntryCount >= MAX_PLAYERMODELS ) {
		return;
	}

	entry = &ui_playerModelEntries[ui_playerModelEntryCount++];
	Q_strncpyz( entry->modelName, modelName, sizeof( entry->modelName ) );
	Q_strncpyz( entry->skinName, skinName, sizeof( entry->skinName ) );
	entry->iconShader = trap_R_RegisterShaderNoMip( iconShaderName );
	entry->hasValidatedSkin = 0;
}

/*
=================
UI_PlayerModelEntryHasSkin
=================
*/
static qboolean UI_PlayerModelEntryHasSkin( int index ) {
	char filename[MAX_QPATH];
	uiPlayerModelEntry_t *entry;

	if ( index < 0 || index >= ui_playerModelEntryCount ) {
		return qfalse;
	}

	entry = &ui_playerModelEntries[index];
	if ( entry->hasValidatedSkin ) {
		return qtrue;
	}

	/*
	Retail uix86.dll validates player-model entries by probing the lower skin
	path directly. The writable source still discovers candidates from icon art,
	then applies the same lower-skin validation before exposing the Q3 head bank.
	*/
	Com_sprintf( filename, sizeof( filename ), "models/players/%s/lower_%s.skin", entry->modelName, entry->skinName );
	if ( trap_FS_FOpenFile( filename, 0, FS_READ ) <= 0 ) {
		return qfalse;
	}

	entry->hasValidatedSkin = 1;
	return qtrue;
}

/*
=================
UI_CountPlayerModelEntries
=================
*/
static int UI_CountPlayerModelEntries( qboolean skipAliasSkins ) {
	int i;
	int count;

	count = 0;

	for ( i = 0; i < ui_playerModelEntryCount; i++ ) {
		if ( skipAliasSkins && UI_PlayerModelSkinIsAlias( ui_playerModelEntries[i].skinName ) ) {
			continue;
		}

		if ( UI_PlayerModelEntryHasSkin( i ) ) {
			count++;
		}
	}

	return count;
}


/*
=================
PlayerModel_BuildList
=================
*/
static void UI_BuildQ3Model_List( void )
{
	int		numdirs;
	int		numfiles;
	char	dirlist[2048];
	char	filelist[2048];
	char	skinname[64];
	char	iconShaderName[MAX_QPATH];
	char*	dirptr;
	char*	fileptr;
	int		i;
	int		j;
	int		dirlen;
	int		filelen;

	ui_playerModelEntryCount = 0;
	uiInfo.q3HeadCount = 0;

	// iterate directory of all player models
	numdirs = trap_FS_GetFileList("models/players", "/", dirlist, 2048 );
	dirptr  = dirlist;
	for (i=0; i<numdirs && uiInfo.q3HeadCount < MAX_PLAYERMODELS; i++,dirptr+=dirlen+1)
	{
		dirlen = strlen(dirptr);
		
		if (dirlen && dirptr[dirlen-1]=='/') dirptr[dirlen-1]='\0';

		if (!strcmp(dirptr,".") || !strcmp(dirptr,".."))
			continue;
			
		// iterate all skin files in directory
		numfiles = trap_FS_GetFileList( va("models/players/%s",dirptr), "tga", filelist, 2048 );
		fileptr  = filelist;
		for (j=0; j<numfiles && uiInfo.q3HeadCount < MAX_PLAYERMODELS;j++,fileptr+=filelen+1)
		{
			filelen = strlen(fileptr);

			COM_StripExtension(fileptr,skinname);

			if (Q_stricmpn(skinname, "icon_", 5) == 0 && skinname[5] != '\0')
			{
				Com_sprintf( iconShaderName, sizeof( iconShaderName ), "models/players/%s/%s", dirptr, skinname );
				UI_AddPlayerModelEntry( dirptr, skinname + 5, iconShaderName );
			}

		}
	}

	for ( i = 0; i < ui_playerModelEntryCount && uiInfo.q3HeadCount < MAX_PLAYERMODELS; i++ ) {
		if ( UI_PlayerModelSkinIsAlias( ui_playerModelEntries[i].skinName ) ) {
			continue;
		}

		if ( !UI_PlayerModelEntryHasSkin( i ) ) {
			continue;
		}

		if ( Q_stricmp( ui_playerModelEntries[i].skinName, "default" ) == 0 ) {
			Com_sprintf( uiInfo.q3HeadNames[uiInfo.q3HeadCount], sizeof( uiInfo.q3HeadNames[uiInfo.q3HeadCount] ),
				"%s", ui_playerModelEntries[i].modelName );
		} else {
			Com_sprintf( uiInfo.q3HeadNames[uiInfo.q3HeadCount], sizeof( uiInfo.q3HeadNames[uiInfo.q3HeadCount] ),
				"%s/%s", ui_playerModelEntries[i].modelName, ui_playerModelEntries[i].skinName );
		}

		uiInfo.q3HeadIcons[uiInfo.q3HeadCount] = ui_playerModelEntries[i].iconShader;
		uiInfo.q3HeadCount++;
	}

		}

/*
=================
UI_ListPlayerModels
=================
*/
void UI_ListPlayerModels( void ) {
	int i;

	UI_BuildQ3Model_List();
	UI_CountPlayerModelEntries( qfalse );

	Com_Printf( "Player Models\n" );
	Com_Printf( "=============\n" );

	for ( i = 0; i < ui_playerModelEntryCount; i++ ) {
		if ( !UI_PlayerModelEntryHasSkin( i ) ) {
			continue;
		}

		if ( Q_stricmp( ui_playerModelEntries[i].skinName, "default" ) == 0 ) {
			Com_Printf( "%s\n", ui_playerModelEntries[i].modelName );
		} else {
			Com_Printf( "%s/%s\n", ui_playerModelEntries[i].modelName, ui_playerModelEntries[i].skinName );
		}
	}
}



/*
=================
UI_Init
=================
*/
void _UI_Init( qboolean inGameLoad ) {
	const char *menuSet;
	int start;

	//uiInfo.inGameLoad = inGameLoad;

	UI_RegisterCvars();
	UI_UpdateCvars();
	// Retail _UI_Init seeds the callvote map filter back to Default before menu scripts run.
	trap_Cvar_Set("ui_cvGameType", "-1");
	trap_Cvar_Update(&ui_cvGameType);
	if (UI_ExternalEcosystemsDisabled()) {
		if (ui_browserAwesomium.integer != 0) {
			trap_Cvar_Set("ui_browserAwesomium", "0");
			trap_Cvar_Update(&ui_browserAwesomium);
		}
		trap_Cvar_Set("web_browserActive", "0");
		Com_Printf("UI: external ecosystems disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS/QL_DISABLE_AWESOMIUM/QL_DISABLE_STEAMWORKS).\n");
	}
	UI_InitMemory();

	// cache redundant calulations
	UI_RefreshDisplayContextScale();


  //UI_Load();
	uiInfo.uiDC.registerShaderNoMip = &trap_R_RegisterShaderNoMip;
	uiInfo.uiDC.setColor = &UI_SetColor;
	uiInfo.uiDC.drawHandlePic = &UI_DrawHandlePic;
	uiInfo.uiDC.drawStretchPic = &trap_R_DrawStretchPic;
	uiInfo.uiDC.drawText = &Text_Paint;
	uiInfo.uiDC.drawTextExt = &Text_PaintExt;
	uiInfo.uiDC.textWidth = &Text_Width;
	uiInfo.uiDC.textWidthExt = &Text_WidthExt;
	uiInfo.uiDC.textHeight = &Text_Height;
	uiInfo.uiDC.textHeightExt = &Text_HeightExt;
	uiInfo.uiDC.registerModel = &trap_R_RegisterModel;
	uiInfo.uiDC.modelBounds = &trap_R_ModelBounds;
	uiInfo.uiDC.fillRect = &UI_FillRect;
	uiInfo.uiDC.drawRect = &_UI_DrawRect;
	uiInfo.uiDC.drawSides = &_UI_DrawSides;
	uiInfo.uiDC.drawTopBottom = &_UI_DrawTopBottom;
	uiInfo.uiDC.clearScene = &trap_R_ClearScene;
	uiInfo.uiDC.drawSides = &_UI_DrawSides;
	uiInfo.uiDC.addRefEntityToScene = &trap_R_AddRefEntityToScene;
	uiInfo.uiDC.renderScene = &trap_R_RenderScene;
	uiInfo.uiDC.registerFont = &trap_R_RegisterFont;
	uiInfo.uiDC.ownerDrawItem = &UI_OwnerDraw;
	uiInfo.uiDC.getValue = &UI_GetValue;
	uiInfo.uiDC.ownerDrawVisible = &UI_OwnerDrawVisible;
	uiInfo.uiDC.runScript = &UI_RunMenuScript;
	uiInfo.uiDC.getTeamColor = &UI_GetTeamColor;
	uiInfo.uiDC.setCVar = trap_Cvar_Set;
	uiInfo.uiDC.getCVarString = trap_Cvar_VariableStringBuffer;
	uiInfo.uiDC.getCVarValue = trap_Cvar_VariableValue;
	uiInfo.uiDC.drawTextWithCursor = &Text_PaintWithCursor;
	uiInfo.uiDC.drawTextWithCursorExt = &Text_PaintWithCursorExt;
	uiInfo.uiDC.setOverstrikeMode = &trap_Key_SetOverstrikeMode;
	uiInfo.uiDC.getOverstrikeMode = &trap_Key_GetOverstrikeMode;
	uiInfo.uiDC.startLocalSound = &trap_S_StartLocalSound;
	uiInfo.uiDC.ownerDrawHandleKey = &UI_OwnerDrawHandleKey;
	uiInfo.uiDC.feederCount = &UI_FeederCount;
	uiInfo.uiDC.feederItemImage = &UI_FeederItemImage;
	uiInfo.uiDC.feederItemText = &UI_FeederItemText;
	uiInfo.uiDC.feederSelection = &UI_FeederSelection;
	uiInfo.uiDC.setBinding = &trap_Key_SetBinding;
	uiInfo.uiDC.getBindingBuf = &trap_Key_GetBindingBuf;
	uiInfo.uiDC.keynumToStringBuf = &trap_Key_KeynumToStringBuf;
	uiInfo.uiDC.executeText = &trap_Cmd_ExecuteText;
	uiInfo.uiDC.Error = &Com_Error; 
	uiInfo.uiDC.Print = &Com_Printf; 
	uiInfo.uiDC.Pause = &UI_Pause;
	uiInfo.uiDC.ownerDrawWidth = &UI_OwnerDrawWidth;
	uiInfo.uiDC.registerSound = &trap_S_RegisterSound;
	uiInfo.uiDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;
	uiInfo.uiDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;
	uiInfo.uiDC.playCinematic = &UI_PlayCinematic;
	uiInfo.uiDC.playLauncherCinematic = &UI_LauncherPlayCinematic;
	uiInfo.uiDC.stopCinematic = &UI_StopCinematic;
	uiInfo.uiDC.drawCinematic = &UI_DrawCinematic;
	uiInfo.uiDC.runCinematicFrame = &UI_RunCinematicFrame;
	uiInfo.uiDC.adjustFrom640 = &UI_AdjustFrom640;

	// Retail uix86.dll calls the advertisement-bridge init import before wiring the Quake Live advert callbacks.
	UI_InitAdvertisementBridge();

	uiInfo.uiDC.setupAdvertCellShader = &UI_SetupAdvertCellShader;
	uiInfo.uiDC.refreshAdvertCellShader = &UI_RefreshAdvertCellShader;
	uiInfo.uiDC.activateAdvert = &UI_ActivateAdvert;
	uiInfo.uiDC.initAdvertisementBridge = &UI_InitAdvertisementBridge;

	Init_Display(&uiInfo.uiDC);

	String_Init();
  
	uiInfo.uiDC.cursor	= trap_R_RegisterShaderNoMip( "menu/art/3_cursor2" );
	uiInfo.uiDC.whiteShader = trap_R_RegisterShaderNoMip( "white" );

	AssetCache();

	start = trap_Milliseconds();

	uiInfo.teamCount = 0;
	uiInfo.characterCount = 0;
	uiInfo.aliasCount = 0;
	uiInfo.countryCount = 0;

	UI_LoadCountries();

#ifdef PRE_RELEASE_TADEMO
	UI_ParseTeamInfo("demoteaminfo.txt");
	UI_ParseGameInfo("demogameinfo.txt");
#else
	UI_ParseTeamInfo("ui/teaminfo.txt");
#endif

        menuSet = UI_Cvar_VariableString("ui_menuFiles");
        UI_UpdateActiveMenuFlow();
        if (menuSet == NULL || menuSet[0] == '\0') {
                menuSet = UI_DefaultMenuFile();
        }

#if 0
	if (uiInfo.inGameLoad) {
		UI_LoadMenus("ui/ingame.txt", qtrue);
	} else { // bk010222: left this: UI_LoadMenus(menuSet, qtrue);
	}
#else 
        UI_LoadMenus(menuSet, qtrue);
        UI_LoadMenus(UI_DefaultIngameFile(), qfalse);
#endif
	UI_ApplyRetailMenuFixups();
	
	Menus_CloseAll();

	trap_LAN_LoadCachedServers();
	UI_LoadBestScores(uiInfo.mapList[ui_currentMap.integer].mapLoadName, uiInfo.gameTypes[ui_gameType.integer].gtEnum);

	UI_BuildQ3Model_List();
	UI_LoadBots();

	// sets defaults for ui temp cvars
	UI_SyncMenuStateFromCvars();

	uiInfo.serverStatus.currentServerCinematic = -1;
	uiInfo.previewMovie = -1;

	if (trap_Cvar_VariableValue("ui_TeamArenaFirstRun") == 0) {
		trap_Cvar_Set("s_volume", "0.8");
		trap_Cvar_Set("s_musicvolume", "0.5");
		trap_Cvar_Set("ui_TeamArenaFirstRun", "1");
	}

	trap_Cvar_Register(NULL, "debug_protocol", "", 0 );

	trap_Cvar_Set("ui_actualNetGameType", va("%d", ui_netGameType.integer));
		}


/*
=================
UI_KeyEvent
=================
*/
void _UI_KeyEvent( int key, qboolean down ) {

  if (Menu_Count() > 0) {
    menuDef_t *menu = Menu_GetFocused();
		if (menu) {
			if (key == K_ESCAPE && down && !Menus_AnyFullScreenVisible()) {
				Menus_CloseAll();
			} else {
				Menu_HandleKey(menu, key, down );
			}
		} else {
			trap_Key_SetCatcher( trap_Key_GetCatcher() & ~KEYCATCH_UI );
			trap_Key_ClearStates();
			trap_Cvar_Set( "cl_paused", "0" );
		}
  }

  //if ((s > 0) && (s != menu_null_sound)) {
	//  trap_S_StartLocalSound( s, CHAN_LOCAL_SOUND );
  //}
		}

/*
=================
UI_MouseEvent
=================
*/
void _UI_MouseEvent( int dx, int dy )
{
	// update mouse screen position
	uiInfo.uiDC.cursorx += dx;
	if (uiInfo.uiDC.cursorx < 0)
		uiInfo.uiDC.cursorx = 0;
	else if (uiInfo.uiDC.cursorx > SCREEN_WIDTH)
		uiInfo.uiDC.cursorx = SCREEN_WIDTH;

	uiInfo.uiDC.cursory += dy;
	if (uiInfo.uiDC.cursory < 0)
		uiInfo.uiDC.cursory = 0;
	else if (uiInfo.uiDC.cursory > SCREEN_HEIGHT)
		uiInfo.uiDC.cursory = SCREEN_HEIGHT;

  if (Menu_Count() > 0) {
    //menuDef_t *menu = Menu_GetFocused();
    //Menu_HandleMouseMove(menu, uiInfo.uiDC.cursorx, uiInfo.uiDC.cursory);
		Display_MouseMove(NULL, uiInfo.uiDC.cursorx, uiInfo.uiDC.cursory);
  }

		}

void UI_LoadNonIngame() {
        const char *menuSet = UI_Cvar_VariableString("ui_menuFiles");
        UI_UpdateActiveMenuFlow();
        if (menuSet == NULL || menuSet[0] == '\0') {
                menuSet = UI_DefaultMenuFile();
        }
        UI_LoadMenus(menuSet, qfalse);
        UI_LoadMenus(UI_DefaultIngameFile(), qfalse);
        uiInfo.inGameLoad = qfalse;
		}

void _UI_SetActiveMenu( uiMenuCommand_t menu ) {
	char buf[256];

	UI_SetBrowserActive(ui_activeMenuFlow == UI_MENU_FLOW_QUAKELIVE);
	UI_BrowserBridge_SetActive(ui_activeMenuFlow == UI_MENU_FLOW_BRIDGED);

	// this should be the ONLY way the menu system is brought up
	// enusure minumum menu data is cached
  if (Menu_Count() > 0) {
		vec3_t v;
		v[0] = v[1] = v[2] = 0;
	  switch ( menu ) {
	  case UIMENU_NONE:
			trap_Key_SetCatcher( trap_Key_GetCatcher() & ~KEYCATCH_UI );
			trap_Key_ClearStates();
			trap_Cvar_Set( "cl_paused", "0" );
			Menus_CloseAll();

		  return;
	  case UIMENU_MAIN:
			//trap_Cvar_Set( "sv_killserver", "1" );
			trap_Key_SetCatcher( KEYCATCH_UI );
			UI_SyncMenuStateFromCvars();
			if (uiInfo.inGameLoad) {
				UI_LoadNonIngame();
			}
			Menus_CloseAll();
			Menus_ActivateByName("main");
			trap_Cvar_VariableStringBuffer("com_errorMessage", buf, sizeof(buf));
			trap_S_StartBackgroundTrack( "music/fla_mp05", NULL );
			if (strlen(buf)) {
				if (!ui_singlePlayerActive.integer) {
					Menus_ActivateByName("error_popmenu");
				} else {
					trap_Cvar_Set("com_errorMessage", "");
				}
			}
		  return;
	  case UIMENU_TEAM:
			trap_Key_SetCatcher( KEYCATCH_UI );
			Menus_ActivateByName("joingame_menu");
		  return;
	  case UIMENU_NEED_CD:
			// no cd check in TA
			//trap_Key_SetCatcher( KEYCATCH_UI );
      //Menus_ActivateByName("needcd");
		  //UI_ConfirmMenu( "Insert the CD", NULL, NeedCDAction );
		  return;
	  case UIMENU_BAD_CD_KEY:
			// no cd check in TA
			//trap_Key_SetCatcher( KEYCATCH_UI );
      //Menus_ActivateByName("badcd");
//UI_ConfirmMenu( "CD Key Error", NULL, NeedCDKeyAction );
		  return;
	  case UIMENU_INGAME:
		  trap_Cvar_Set( "cl_paused", "1" );
			UI_SyncMenuStateFromCvars();
			// Retail resets the ingame callvote filter each time the menu is reopened.
			trap_Cvar_Set( "ui_cvGameType", "-1" );
			trap_Cvar_Update( &ui_cvGameType );
			trap_Key_SetCatcher( KEYCATCH_UI );
			UI_BuildPlayerList();
			Menus_CloseAll();
			Menus_ActivateByName("ingame");
		  return;
	  }
  }
		}

qboolean _UI_IsFullscreen( void ) {
	return Menus_AnyFullScreenVisible();
		}



static connstate_t	lastConnState;
static char			lastLoadingText[MAX_INFO_VALUE];

static void UI_ReadableSize ( char *buf, int bufsize, int value )
{
	if (value > 1024*1024*1024 ) { // gigs
		Com_sprintf( buf, bufsize, "%d", value / (1024*1024*1024) );
		Com_sprintf( buf+strlen(buf), bufsize-strlen(buf), ".%02d GB", 
			(value % (1024*1024*1024))*100 / (1024*1024*1024) );
	} else if (value > 1024*1024 ) { // megs
		Com_sprintf( buf, bufsize, "%d", value / (1024*1024) );
		Com_sprintf( buf+strlen(buf), bufsize-strlen(buf), ".%02d MB", 
			(value % (1024*1024))*100 / (1024*1024) );
	} else if (value > 1024 ) { // kilos
		Com_sprintf( buf, bufsize, "%d KB", value / 1024 );
	} else { // bytes
		Com_sprintf( buf, bufsize, "%d bytes", value );
	}
		}

// Assumes time is in msec
static void UI_PrintTime ( char *buf, int bufsize, int time ) {
	time /= 1000;  // change to seconds

	if (time > 3600) { // in the hours range
		Com_sprintf( buf, bufsize, "%d hr %d min", time / 3600, (time % 3600) / 60 );
	} else if (time > 60) { // mins
		Com_sprintf( buf, bufsize, "%d min %d sec", time / 60, time % 60 );
	} else  { // secs
		Com_sprintf( buf, bufsize, "%d sec", time );
	}
		}

void Text_PaintCenter(float x, float y, float scale, vec4_t color, const char *text, float adjust) {
	int len = Text_Width(text, scale, 0);
	Text_Paint(x - len / 2, y, scale, color, text, 0, 0, ITEM_TEXTSTYLE_SHADOWEDMORE);
		}

void Text_PaintCenter_AutoWrapped(float x, float y, float xmax, float ystep, float scale, vec4_t color, const char *str, float adjust) {
	int width;
	char *s1,*s2,*s3;
	char c_bcp;
	char buf[1024];

	if (!str || str[0]=='\0')
		return;

	Q_strncpyz(buf, str, sizeof(buf));
	s1 = s2 = s3 = buf;

	while (1) {
		do {
			s3++;
		} while (*s3!=' ' && *s3!='\0');
		c_bcp = *s3;
		*s3 = '\0';
		width = Text_Width(s1, scale, 0);
		*s3 = c_bcp;
		if (width > xmax) {
			if (s1==s2)
			{
				// fuck, don't have a clean cut, we'll overflow
				s2 = s3;
			}
			*s2 = '\0';
			Text_PaintCenter(x, y, scale, color, s1, adjust);
			y += ystep;
			if (c_bcp == '\0')
      {
				// that was the last word
        // we could start a new loop, but that wouldn't be much use
        // even if the word is too long, we would overflow it (see above)
        // so just print it now if needed
        s2++;
        if (*s2 != '\0') // if we are printing an overflowing line we have s2 == s3
          Text_PaintCenter(x, y, scale, color, s2, adjust);
        break;
      }
			s2++;
			s1 = s2;
			s3 = s2;
		}
		else
		{
			s2 = s3;
			if (c_bcp == '\0') // we reached the end
			{
				Text_PaintCenter(x, y, scale, color, s1, adjust);
				break;
			}
		}
	}
		}

static void UI_DisplayDownloadInfo( const char *downloadName, float centerPoint, float yStart, float scale ) {
	static char dlText[]	= "Downloading:";
	static char etaText[]	= "Estimated time left:";
	static char xferText[]	= "Transfer rate:";

	int downloadSize, downloadCount, downloadTime;
	char dlSizeBuf[64], totalSizeBuf[64], xferRateBuf[64], dlTimeBuf[64];
	int xferRate;
	int leftWidth;
	const char *s;

	downloadSize = trap_Cvar_VariableValue( "cl_downloadSize" );
	downloadCount = trap_Cvar_VariableValue( "cl_downloadCount" );
	downloadTime = trap_Cvar_VariableValue( "cl_downloadTime" );

	leftWidth = 320;

	UI_SetColor(colorWhite);
	Text_PaintCenter(centerPoint, yStart + 112, scale, colorWhite, dlText, 0);
	Text_PaintCenter(centerPoint, yStart + 192, scale, colorWhite, etaText, 0);
	Text_PaintCenter(centerPoint, yStart + 248, scale, colorWhite, xferText, 0);

	if (downloadSize > 0) {
		s = va( "%s (%d%%)", downloadName, downloadCount * 100 / downloadSize );
	} else {
		s = downloadName;
	}

	Text_PaintCenter(centerPoint, yStart+136, scale, colorWhite, s, 0);

	UI_ReadableSize( dlSizeBuf,		sizeof dlSizeBuf,		downloadCount );
	UI_ReadableSize( totalSizeBuf,	sizeof totalSizeBuf,	downloadSize );

	if (downloadCount < 4096 || !downloadTime) {
		Text_PaintCenter(leftWidth, yStart+216, scale, colorWhite, "estimating", 0);
		Text_PaintCenter(leftWidth, yStart+160, scale, colorWhite, va("(%s of %s copied)", dlSizeBuf, totalSizeBuf), 0);
	} else {
		if ((uiInfo.uiDC.realTime - downloadTime) / 1000) {
			xferRate = downloadCount / ((uiInfo.uiDC.realTime - downloadTime) / 1000);
		} else {
			xferRate = 0;
		}
		UI_ReadableSize( xferRateBuf, sizeof xferRateBuf, xferRate );

		// Extrapolate estimated completion time
		if (downloadSize && xferRate) {
			int n = downloadSize / xferRate; // estimated time for entire d/l in secs

			// We do it in K (/1024) because we'd overflow around 4MB
			UI_PrintTime ( dlTimeBuf, sizeof dlTimeBuf, 
				(n - (((downloadCount/1024) * n) / (downloadSize/1024))) * 1000);

			Text_PaintCenter(leftWidth, yStart+216, scale, colorWhite, dlTimeBuf, 0);
			Text_PaintCenter(leftWidth, yStart+160, scale, colorWhite, va("(%s of %s copied)", dlSizeBuf, totalSizeBuf), 0);
		} else {
			Text_PaintCenter(leftWidth, yStart+216, scale, colorWhite, "estimating", 0);
			if (downloadSize) {
				Text_PaintCenter(leftWidth, yStart+160, scale, colorWhite, va("(%s of %s copied)", dlSizeBuf, totalSizeBuf), 0);
			} else {
				Text_PaintCenter(leftWidth, yStart+160, scale, colorWhite, va("(%s copied)", dlSizeBuf), 0);
			}
		}

		if (xferRate) {
			Text_PaintCenter(leftWidth, yStart+272, scale, colorWhite, va("%s/Sec", xferRateBuf), 0);
		}
	}
		}

/*
========================
UI_DrawConnectScreen

This will also be overlaid on the cgame info screen during loading
to prevent it from blinking away too rapidly on local or lan games.
========================
*/
void UI_DrawConnectScreen( qboolean overlay ) {
	char			*s;
	uiClientState_t	cstate;
	char			info[MAX_INFO_VALUE];
	char text[256];
	float centerPoint, yStart, scale;
	
	menuDef_t *menu = Menus_FindByName("Connect");


	if ( !overlay && menu ) {
		Menu_Paint(menu, qtrue);
	}

	if (!overlay) {
		centerPoint = 320;
		yStart = 130;
		scale = 0.5f;
	} else {
		centerPoint = 320;
		yStart = 32;
		scale = 0.6f;
		return;
	}

	// see what information we should display
	trap_GetClientState( &cstate );

	info[0] = '\0';
	if( trap_GetConfigString( CS_SERVERINFO, info, sizeof(info) ) ) {
		Text_PaintCenter(centerPoint, yStart, scale, colorWhite, va( "Loading %s", Info_ValueForKey( info, "mapname" )), 0);
	}

	if (!Q_stricmp(cstate.servername,"localhost")) {
		Text_PaintCenter(centerPoint, yStart + 48, scale, colorWhite, va("Starting up..."), ITEM_TEXTSTYLE_SHADOWEDMORE);
	} else {
		strcpy(text, va("Connecting to %s", cstate.servername));
		Text_PaintCenter(centerPoint, yStart + 48, scale, colorWhite,text , ITEM_TEXTSTYLE_SHADOWEDMORE);
	}

	// display global MOTD at bottom
	Text_PaintCenter(centerPoint, 600, scale, colorWhite, Info_ValueForKey( cstate.updateInfoString, "motd" ), 0);
	// print any server info (server full, bad version, etc)
	if ( cstate.connState < CA_CONNECTED ) {
		Text_PaintCenter_AutoWrapped(centerPoint, yStart + 176, 630, 20, scale, colorWhite, cstate.messageString, 0);
	}

	if ( lastConnState > cstate.connState ) {
		lastLoadingText[0] = '\0';
	}
	lastConnState = cstate.connState;

	switch ( cstate.connState ) {
	case CA_CONNECTING:
		s = va("Awaiting connection...%i", cstate.connectPacketCount);
		break;
	case CA_CHALLENGING:
		s = va("Awaiting challenge...%i", cstate.connectPacketCount);
		break;
	case CA_CONNECTED: {
		char downloadName[MAX_INFO_VALUE];

			trap_Cvar_VariableStringBuffer( "cl_downloadName", downloadName, sizeof(downloadName) );
			if (*downloadName) {
				UI_DisplayDownloadInfo( downloadName, centerPoint, yStart, scale );
				return;
			}
		}
		s = "Awaiting gamestate...";
		break;
	case CA_LOADING:
		return;
	case CA_PRIMED:
		return;
	default:
		return;
	}


	if (Q_stricmp(cstate.servername,"localhost")) {
		Text_PaintCenter(centerPoint, yStart + 80, scale, colorWhite, s, 0);
	}

	// password required / connection rejected information goes here
		}


/*
================
cvars
================
*/

typedef struct {
	vmCvar_t	*vmCvar;
	char		*cvarName;
	char		*defaultString;
	int			cvarFlags;
} cvarTable_t;

vmCvar_t	ui_ffa_fraglimit;
vmCvar_t	ui_ffa_timelimit;

vmCvar_t	ui_tourney_fraglimit;
vmCvar_t	ui_tourney_timelimit;

vmCvar_t	ui_team_fraglimit;
vmCvar_t	ui_team_timelimit;
vmCvar_t	ui_team_friendly;

vmCvar_t	ui_ctf_capturelimit;
vmCvar_t	ui_ctf_timelimit;
vmCvar_t	ui_ctf_friendly;

vmCvar_t	ui_arenasFile;
vmCvar_t	ui_botsFile;
vmCvar_t	ui_spScores1;
vmCvar_t	ui_spScores2;
vmCvar_t	ui_spScores3;
vmCvar_t	ui_spScores4;
vmCvar_t	ui_spScores5;
vmCvar_t	ui_spAwards;
vmCvar_t	ui_spVideos;
vmCvar_t	ui_spSkill;

vmCvar_t	ui_spSelection;

vmCvar_t	ui_browserMaster;
vmCvar_t	ui_browserGameType;
vmCvar_t	ui_browserSortKey;
vmCvar_t	ui_browserShowFull;
vmCvar_t	ui_browserShowEmpty;

vmCvar_t	ui_brassTime;
vmCvar_t	ui_drawCrosshair;
vmCvar_t	ui_drawCrosshairNames;
vmCvar_t	ui_marks;

vmCvar_t	ui_globalpreset;
vmCvar_t	ui_screenDamage_Team_preset;
vmCvar_t	ui_screenDamage_preset;

vmCvar_t	ui_server1;
vmCvar_t	ui_server2;
vmCvar_t	ui_server3;
vmCvar_t	ui_server4;
vmCvar_t	ui_server5;
vmCvar_t	ui_server6;
vmCvar_t	ui_server7;
vmCvar_t	ui_server8;
vmCvar_t	ui_server9;
vmCvar_t	ui_server10;
vmCvar_t	ui_server11;
vmCvar_t	ui_server12;
vmCvar_t	ui_server13;
vmCvar_t	ui_server14;
vmCvar_t	ui_server15;
vmCvar_t	ui_server16;

vmCvar_t	ui_cdkeychecked;

vmCvar_t	ui_redteam;
vmCvar_t	ui_redteam1;
vmCvar_t	ui_redteam2;
vmCvar_t	ui_redteam3;
vmCvar_t	ui_redteam4;
vmCvar_t	ui_redteam5;
vmCvar_t	ui_blueteam;
vmCvar_t	ui_blueteam1;
vmCvar_t	ui_blueteam2;
vmCvar_t	ui_blueteam3;
vmCvar_t	ui_blueteam4;
vmCvar_t	ui_blueteam5;
vmCvar_t	ui_teamName;
vmCvar_t	ui_dedicated;
vmCvar_t	ui_gameType;
vmCvar_t	ui_netGameType;
vmCvar_t	ui_actualNetGameType;
vmCvar_t	ui_cvGameType;
vmCvar_t	ui_joinGameType;
vmCvar_t	ui_netSource;
vmCvar_t	ui_serverFilterType;
vmCvar_t	ui_opponentName;
vmCvar_t	ui_menuFiles;
vmCvar_t	ui_currentTier;
vmCvar_t	ui_currentMap;
vmCvar_t	ui_currentNetMap;
vmCvar_t	ui_mapIndex;
vmCvar_t	ui_currentOpponent;
vmCvar_t	ui_selectedPlayer;
vmCvar_t	ui_selectedPlayerName;
vmCvar_t	ui_lastServerRefresh_0;
vmCvar_t	ui_lastServerRefresh_1;
vmCvar_t	ui_lastServerRefresh_2;
vmCvar_t	ui_lastServerRefresh_3;
vmCvar_t	ui_singlePlayerActive;
vmCvar_t	ui_scoreAccuracy;
vmCvar_t	ui_scoreImpressives;
vmCvar_t	ui_scoreExcellents;
vmCvar_t	ui_scoreCaptures;
vmCvar_t	ui_scoreDefends;
vmCvar_t	ui_scoreAssists;
vmCvar_t	ui_scoreGauntlets;
vmCvar_t	ui_scoreScore;
vmCvar_t	ui_scorePerfect;
vmCvar_t	ui_scoreTeam;
vmCvar_t	ui_scoreBase;
vmCvar_t	ui_scoreTimeBonus;
vmCvar_t	ui_scoreSkillBonus;
vmCvar_t	ui_scoreShutoutBonus;
vmCvar_t	ui_scoreTime;
vmCvar_t	ui_scoreAccuracy2;
vmCvar_t	ui_scoreImpressives2;
vmCvar_t	ui_scoreExcellents2;
vmCvar_t	ui_scoreCaptures2;
vmCvar_t	ui_scoreDefends2;
vmCvar_t	ui_scoreAssists2;
vmCvar_t	ui_scoreGauntlets2;
vmCvar_t	ui_scoreScore2;
vmCvar_t	ui_scorePerfect2;
vmCvar_t	ui_scoreTeam2;
vmCvar_t	ui_scoreBase2;
vmCvar_t	ui_scoreTimeBonus2;
vmCvar_t	ui_scoreSkillBonus2;
vmCvar_t	ui_scoreShutoutBonus2;
vmCvar_t	ui_scoreTime2;
vmCvar_t	ui_captureLimit;
vmCvar_t	ui_fragLimit;
vmCvar_t	ui_smallFont;
vmCvar_t	ui_bigFont;
vmCvar_t	ui_findPlayer;
vmCvar_t	ui_Q3Model;
vmCvar_t	ui_hudFiles;
vmCvar_t	ui_recordSPDemo;
vmCvar_t	ui_realCaptureLimit;
vmCvar_t	ui_realWarmUp;
vmCvar_t	ui_serverStatusTimeOut;
vmCvar_t	ui_mapVotingDisabled;
vmCvar_t	ui_gameTypeVotingDisabled;
vmCvar_t	ui_bloomPreset;
	vmCvar_t	ui_teamModel;
	vmCvar_t	ui_teamModelBright;
	vmCvar_t	ui_enemyModel;
	vmCvar_t	ui_enemyModelBright;
vmCvar_t	ui_forceEnemySkin;
vmCvar_t	ui_forceTeamSkin;
vmCvar_t	ui_enemyHeadColor;
vmCvar_t	ui_enemyLowerColor;
vmCvar_t	ui_enemyUpperColor;
vmCvar_t	ui_teamHeadColor;
vmCvar_t	ui_teamLowerColor;
vmCvar_t	ui_teamUpperColor;
vmCvar_t	ui_mousePitch;
vmCvar_t	ui_screenDamage;
vmCvar_t	ui_screenDamage_Team;
vmCvar_t	ui_teammateIndicator;
vmCvar_t	ui_drawRewards;
vmCvar_t	ui_postProcessPreset;
vmCvar_t	ui_marksPreset;
vmCvar_t	ui_lightingModelPreset;
vmCvar_t	ui_lowAmmoPreset;
vmCvar_t	ui_impactSparks;
vmCvar_t	ui_announcer;
vmCvar_t	ui_voteactive;
vmCvar_t	ui_endMapVotingDisabled;
vmCvar_t	ui_mainmenu;
vmCvar_t	ui_priv;
vmCvar_t	ui_warmup;
vmCvar_t	ui_doWarmup;
vmCvar_t	ui_friendlyFire;
vmCvar_t	ui_Warmup;
vmCvar_t	ui_pure;
vmCvar_t	ui_saveCaptureLimit;
vmCvar_t	ui_saveFragLimit;
vmCvar_t	ui_recordSPDemoName;
vmCvar_t	ui_glCustom;
vmCvar_t	ui_country;
vmCvar_t	ui_opponentModel;
vmCvar_t	ui_cdkeyvalid;


// bk001129 - made static to avoid aliasing
static cvarTable_t		cvarTable[] = {
	{ &ui_ffa_fraglimit, "ui_ffa_fraglimit", "20", CVAR_ARCHIVE },
	{ &ui_ffa_timelimit, "ui_ffa_timelimit", "0", CVAR_ARCHIVE },

	{ &ui_tourney_fraglimit, "ui_tourney_fraglimit", "0", CVAR_ARCHIVE },
	{ &ui_tourney_timelimit, "ui_tourney_timelimit", "15", CVAR_ARCHIVE },

	{ &ui_team_fraglimit, "ui_team_fraglimit", "0", CVAR_ARCHIVE },
	{ &ui_team_timelimit, "ui_team_timelimit", "20", CVAR_ARCHIVE },
	{ &ui_team_friendly, "ui_team_friendly",  "1", CVAR_ARCHIVE },

	{ &ui_ctf_capturelimit, "ui_ctf_capturelimit", "8", CVAR_ARCHIVE },
	{ &ui_ctf_timelimit, "ui_ctf_timelimit", "30", CVAR_ARCHIVE },
	{ &ui_ctf_friendly, "ui_ctf_friendly",  "0", CVAR_ARCHIVE },

	{ &ui_arenasFile, "g_arenasFile", "", CVAR_INIT|CVAR_ROM },
	{ &ui_botsFile, "g_botsFile", "", CVAR_INIT|CVAR_ROM },
	{ &ui_spScores1, "g_spScores1", "", CVAR_ARCHIVE | CVAR_ROM },
	{ &ui_spScores2, "g_spScores2", "", CVAR_ARCHIVE | CVAR_ROM },
	{ &ui_spScores3, "g_spScores3", "", CVAR_ARCHIVE | CVAR_ROM },
	{ &ui_spScores4, "g_spScores4", "", CVAR_ARCHIVE | CVAR_ROM },
	{ &ui_spScores5, "g_spScores5", "", CVAR_ARCHIVE | CVAR_ROM },
	{ &ui_spAwards, "g_spAwards", "", CVAR_ARCHIVE | CVAR_ROM },
	{ &ui_spVideos, "g_spVideos", "", CVAR_ARCHIVE | CVAR_ROM },
	{ &ui_spSkill, "g_spSkill", "2", CVAR_ARCHIVE },

	{ &ui_spSelection, "ui_spSelection", "", CVAR_ROM },

	{ &ui_browserMaster, "ui_browserMaster", "0", CVAR_ARCHIVE },
	{ &ui_browserGameType, "ui_browserGameType", "0", CVAR_ARCHIVE },
	{ &ui_browserSortKey, "ui_browserSortKey", "4", CVAR_ARCHIVE },
	{ &ui_browserShowFull, "ui_browserShowFull", "1", CVAR_ARCHIVE },
	{ &ui_browserShowEmpty, "ui_browserShowEmpty", "1", CVAR_ARCHIVE },

	{ &ui_brassTime, "cg_brassTime", "2500", CVAR_ARCHIVE },
	{ &ui_drawCrosshair, "cg_drawCrosshair", "4", CVAR_ARCHIVE },
	{ &ui_drawCrosshairNames, "cg_drawCrosshairNames", "1", CVAR_ARCHIVE },
	{ &ui_marks, "cg_marks", "1", CVAR_ARCHIVE },

	{ &ui_server1, "server1", "", CVAR_ARCHIVE },
	{ &ui_server2, "server2", "", CVAR_ARCHIVE },
	{ &ui_server3, "server3", "", CVAR_ARCHIVE },
	{ &ui_server4, "server4", "", CVAR_ARCHIVE },
	{ &ui_server5, "server5", "", CVAR_ARCHIVE },
	{ &ui_server6, "server6", "", CVAR_ARCHIVE },
	{ &ui_server7, "server7", "", CVAR_ARCHIVE },
	{ &ui_server8, "server8", "", CVAR_ARCHIVE },
	{ &ui_server9, "server9", "", CVAR_ARCHIVE },
	{ &ui_server10, "server10", "", CVAR_ARCHIVE },
	{ &ui_server11, "server11", "", CVAR_ARCHIVE },
	{ &ui_server12, "server12", "", CVAR_ARCHIVE },
	{ &ui_server13, "server13", "", CVAR_ARCHIVE },
	{ &ui_server14, "server14", "", CVAR_ARCHIVE },
	{ &ui_server15, "server15", "", CVAR_ARCHIVE },
	{ &ui_server16, "server16", "", CVAR_ARCHIVE },
	{ &ui_cdkeychecked, "ui_cdkeychecked", "0", CVAR_ROM },
	{ &ui_new, "ui_new", "0", CVAR_TEMP },
	{ &ui_debug, "ui_debug", "0", CVAR_TEMP },
	{ &ui_initialized, "ui_initialized", "0", CVAR_TEMP },
	{ &ui_teamName, "ui_teamName", "Pagans", CVAR_ARCHIVE },
	{ &ui_opponentName, "ui_opponentName", "Stroggs", CVAR_ARCHIVE },
	{ &ui_redteam, "ui_redteam", "Pagans", CVAR_ARCHIVE },
	{ &ui_blueteam, "ui_blueteam", "Stroggs", CVAR_ARCHIVE },
	{ &ui_dedicated, "ui_dedicated", "0", CVAR_ARCHIVE },
	{ &ui_gameType, "ui_gameType", "3", CVAR_ARCHIVE },
	{ &ui_joinGameType, "ui_joinGameType", "0", CVAR_ARCHIVE },
	{ &ui_netGameType, "ui_netGameType", "3", CVAR_ARCHIVE },
	{ &ui_actualNetGameType, "ui_actualNetGameType", "3", CVAR_ARCHIVE },
	{ &ui_cvGameType, "ui_cvGameType", "-1", CVAR_ARCHIVE },
	{ &ui_redteam1, "ui_redteam1", "0", CVAR_ARCHIVE },
	{ &ui_redteam2, "ui_redteam2", "0", CVAR_ARCHIVE },
	{ &ui_redteam3, "ui_redteam3", "0", CVAR_ARCHIVE },
	{ &ui_redteam4, "ui_redteam4", "0", CVAR_ARCHIVE },
	{ &ui_redteam5, "ui_redteam5", "0", CVAR_ARCHIVE },
	{ &ui_blueteam1, "ui_blueteam1", "0", CVAR_ARCHIVE },
	{ &ui_blueteam2, "ui_blueteam2", "0", CVAR_ARCHIVE },
	{ &ui_blueteam3, "ui_blueteam3", "0", CVAR_ARCHIVE },
	{ &ui_blueteam4, "ui_blueteam4", "0", CVAR_ARCHIVE },
	{ &ui_blueteam5, "ui_blueteam5", "0", CVAR_ARCHIVE },
	{ &ui_netSource, "ui_netSource", "0", CVAR_ARCHIVE },
	{ &ui_menuFiles, "ui_menuFiles", UI_MENU_FILE_QUAKELIVE, CVAR_ARCHIVE },
	{ &ui_menuFlow, "ui_menuFlow", "1", CVAR_ARCHIVE },
	{ &ui_globalpreset, "ui_globalpreset", "0", CVAR_ARCHIVE },
	{ &ui_screenDamage_Team_preset, "ui_screenDamage_Team_preset", "0", CVAR_ARCHIVE },
	{ &ui_screenDamage_preset, "ui_screenDamage_preset", "0", CVAR_ARCHIVE },
	{ &ui_browserAwesomium, "ui_browserAwesomium", UI_BROWSER_AWESOMIUM_DEFAULT, CVAR_TEMP },
	{ &ui_currentTier, "ui_currentTier", "0", CVAR_ARCHIVE },
	{ &ui_currentMap, "ui_currentMap", "0", CVAR_ARCHIVE },
	{ &ui_currentNetMap, "ui_currentNetMap", "0", CVAR_ARCHIVE },
	{ &ui_mapIndex, "ui_mapIndex", "0", CVAR_ARCHIVE },
	{ &ui_currentOpponent, "ui_currentOpponent", "0", CVAR_ARCHIVE },
	{ &ui_selectedPlayer, "cg_selectedPlayer", "0", CVAR_ARCHIVE},
	{ &ui_selectedPlayerName, "cg_selectedPlayerName", "", CVAR_ARCHIVE},
	{ &ui_lastServerRefresh_0, "ui_lastServerRefresh_0", "", CVAR_ARCHIVE},
	{ &ui_lastServerRefresh_1, "ui_lastServerRefresh_1", "", CVAR_ARCHIVE},
	{ &ui_lastServerRefresh_2, "ui_lastServerRefresh_2", "", CVAR_ARCHIVE},
	{ &ui_lastServerRefresh_3, "ui_lastServerRefresh_3", "", CVAR_ARCHIVE},
	{ &ui_singlePlayerActive, "ui_singlePlayerActive", "0", 0},
	{ &ui_scoreAccuracy, "ui_scoreAccuracy", "0", CVAR_ARCHIVE},
	{ &ui_scoreImpressives, "ui_scoreImpressives", "0", CVAR_ARCHIVE},
	{ &ui_scoreExcellents, "ui_scoreExcellents", "0", CVAR_ARCHIVE},
	{ &ui_scoreCaptures, "ui_scoreCaptures", "0", CVAR_ARCHIVE},
	{ &ui_scoreDefends, "ui_scoreDefends", "0", CVAR_ARCHIVE},
	{ &ui_scoreAssists, "ui_scoreAssists", "0", CVAR_ARCHIVE},
	{ &ui_scoreGauntlets, "ui_scoreGauntlets", "0", CVAR_ARCHIVE},
	{ &ui_scoreScore, "ui_scoreScore", "0", CVAR_ARCHIVE},
	{ &ui_scorePerfect, "ui_scorePerfect", "0", CVAR_ARCHIVE},
	{ &ui_scoreTeam, "ui_scoreTeam", "0 to 0", CVAR_ARCHIVE},
	{ &ui_scoreBase, "ui_scoreBase", "0", CVAR_ARCHIVE},
	{ &ui_scoreTime, "ui_scoreTime", "00:00", CVAR_ARCHIVE},
	{ &ui_scoreTimeBonus, "ui_scoreTimeBonus", "0", CVAR_ARCHIVE},
	{ &ui_scoreSkillBonus, "ui_scoreSkillBonus", "0", CVAR_ARCHIVE},
	{ &ui_scoreShutoutBonus, "ui_scoreShutoutBonus", "0", CVAR_ARCHIVE},
	{ &ui_scoreAccuracy2, "ui_scoreAccuracy2", "0", CVAR_ARCHIVE},
	{ &ui_scoreImpressives2, "ui_scoreImpressives2", "0", CVAR_ARCHIVE},
	{ &ui_scoreExcellents2, "ui_scoreExcellents2", "0", CVAR_ARCHIVE},
	{ &ui_scoreCaptures2, "ui_scoreCaptures2", "0", CVAR_ARCHIVE},
	{ &ui_scoreDefends2, "ui_scoreDefends2", "0", CVAR_ARCHIVE},
	{ &ui_scoreAssists2, "ui_scoreAssists2", "0", CVAR_ARCHIVE},
	{ &ui_scoreGauntlets2, "ui_scoreGauntlets2", "0", CVAR_ARCHIVE},
	{ &ui_scoreScore2, "ui_scoreScore2", "0", CVAR_ARCHIVE},
	{ &ui_scorePerfect2, "ui_scorePerfect2", "0", CVAR_ARCHIVE},
	{ &ui_scoreTeam2, "ui_scoreTeam2", "0 to 0", CVAR_ARCHIVE},
	{ &ui_scoreBase2, "ui_scoreBase2", "0", CVAR_ARCHIVE},
	{ &ui_scoreTime2, "ui_scoreTime2", "00:00", CVAR_ARCHIVE},
	{ &ui_scoreTimeBonus2, "ui_scoreTimeBonus2", "0", CVAR_ARCHIVE},
	{ &ui_scoreSkillBonus2, "ui_scoreSkillBonus2", "0", CVAR_ARCHIVE},
	{ &ui_scoreShutoutBonus2, "ui_scoreShutoutBonus2", "0", CVAR_ARCHIVE},
	{ &ui_fragLimit, "ui_fragLimit", "10", 0},
	{ &ui_captureLimit, "ui_captureLimit", "5", 0},
	{ &ui_smallFont, "ui_smallFont", "0.25", CVAR_ARCHIVE},
	{ &ui_bigFont, "ui_bigFont", "0.4", CVAR_ARCHIVE},
	{ &ui_findPlayer, "ui_findPlayer", "Sarge", CVAR_ARCHIVE},
	{ &ui_Q3Model, "ui_q3model", "0", CVAR_ARCHIVE},
	{ &ui_hudFiles, "cg_hudFiles", "ui/hud3.txt", CVAR_ARCHIVE},
	{ &ui_recordSPDemo, "ui_recordSPDemo", "0", CVAR_ARCHIVE},
	{ &ui_teamArenaFirstRun, "ui_teamArenaFirstRun", "0", CVAR_ARCHIVE},
	{ &ui_realWarmUp, "g_warmup", "20", CVAR_ARCHIVE},
	{ &ui_realCaptureLimit, "capturelimit", "8", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART},
	{ &ui_bloomPreset, "ui_bloomPreset", "0", CVAR_ARCHIVE},
	{ &ui_enemyModel, "ui_enemyModel", "", CVAR_ARCHIVE},
	{ &ui_enemyModelBright, "ui_enemyModelBright", "0", CVAR_ARCHIVE},
	{ &ui_forceEnemySkin, "ui_forceEnemySkin", "", CVAR_ARCHIVE},
	{ &ui_teamModel, "ui_teamModel", "", CVAR_ARCHIVE},
	{ &ui_teamModelBright, "ui_teamModelBright", "0", CVAR_ARCHIVE},
	{ &ui_forceTeamSkin, "ui_forceTeamSkin", "", CVAR_ARCHIVE},
	{ &ui_enemyHeadColor, "ui_enemyHeadColor", "0", CVAR_ARCHIVE},
	{ &ui_enemyLowerColor, "ui_enemyLowerColor", "0", CVAR_ARCHIVE},
	{ &ui_enemyUpperColor, "ui_enemyUpperColor", "0", CVAR_ARCHIVE},
	{ &ui_teamHeadColor, "ui_teamHeadColor", "0", CVAR_ARCHIVE},
	{ &ui_teamLowerColor, "ui_teamLowerColor", "0", CVAR_ARCHIVE},
	{ &ui_teamUpperColor, "ui_teamUpperColor", "0", CVAR_ARCHIVE},
	{ &ui_mousePitch, "ui_mousePitch", "0", CVAR_ARCHIVE},
	{ &ui_screenDamage, "ui_screenDamage", "0", CVAR_ARCHIVE},
	{ &ui_screenDamage_Team, "ui_screenDamage_Team", "0", CVAR_ARCHIVE},
	{ &ui_teammateIndicator, "ui_teammateIndicator", "0", CVAR_ARCHIVE},
	{ &ui_drawRewards, "ui_drawRewards", "0", CVAR_ARCHIVE},
	{ &ui_postProcessPreset, "ui_postProcessPreset", "0", CVAR_ARCHIVE},
	{ &ui_marksPreset, "ui_marksPreset", "0", CVAR_ARCHIVE},
	{ &ui_lightingModelPreset, "ui_lightingModelPreset", "0", CVAR_ARCHIVE},
	{ &ui_lowAmmoPreset, "ui_lowAmmoPreset", "0", CVAR_ARCHIVE},
	{ &ui_impactSparks, "ui_impactSparks", "0", CVAR_ARCHIVE},
	{ &ui_announcer, "ui_announcer", "1", CVAR_ARCHIVE},
	{ &ui_voteactive, "ui_voteactive", "0", CVAR_TEMP},
	{ &ui_endMapVotingDisabled, "ui_endMapVotingDisabled", "0", CVAR_TEMP},
	{ &ui_mainmenu, "ui_mainmenu", "0", CVAR_TEMP},
	{ &ui_priv, "ui_priv", "0", CVAR_TEMP},
	{ &ui_warmup, "ui_warmup", "0", CVAR_TEMP},
	{ &ui_doWarmup, "ui_doWarmup", "0", CVAR_TEMP},
	{ &ui_friendlyFire, "ui_friendlyFire", "0", CVAR_TEMP},
	{ &ui_Warmup, "ui_Warmup", "0", CVAR_TEMP},
	{ &ui_pure, "ui_pure", "0", CVAR_TEMP},
	{ &ui_saveCaptureLimit, "ui_saveCaptureLimit", "0", CVAR_TEMP},
	{ &ui_saveFragLimit, "ui_saveFragLimit", "0", CVAR_TEMP},
	{ &ui_recordSPDemoName, "ui_recordSPDemoName", "", CVAR_TEMP},
	{ &ui_glCustom, "ui_glCustom", "0", CVAR_ARCHIVE},
	{ &ui_country, "ui_country", "", CVAR_ARCHIVE},
	{ &ui_opponentModel, "ui_opponentModel", "", CVAR_ARCHIVE},
	{ &ui_cdkeyvalid, "ui_cdkeyvalid", "", CVAR_TEMP},
	{ &ui_serverStatusTimeOut, "ui_serverStatusTimeOut", "7000", CVAR_ARCHIVE},
	{ &ui_mapVotingDisabled, "ui_mapVotingDisabled", "0", CVAR_TEMP},
	{ &ui_gameTypeVotingDisabled, "ui_gameTypeVotingDisabled", "0", CVAR_TEMP},

};

// bk001129 - made static to avoid aliasing
static int		cvarTableSize = sizeof(cvarTable) / sizeof(cvarTable[0]);


/*
=================
UI_RegisterCvars
=================
*/
void UI_RegisterCvars( void ) {
	int			i;
	cvarTable_t	*cv;

	for ( i = 0, cv = cvarTable ; i < cvarTableSize ; i++, cv++ ) {
		trap_Cvar_Register( cv->vmCvar, cv->cvarName, cv->defaultString, cv->cvarFlags );
	}
		}

/*
=================
UI_UpdateCvars
=================
*/
void UI_UpdateCvars( void ) {
	int			i;
	cvarTable_t	*cv;

	for ( i = 0, cv = cvarTable ; i < cvarTableSize ; i++, cv++ ) {
		trap_Cvar_Update( cv->vmCvar );
	}
		}


/*
=================
ArenaServers_StopRefresh
=================
*/
void UI_StopServerRefresh( void )
{
        int count;

if (!UI_ServerBrowserEnabled()) {
uiInfo.serverStatus.refreshActive = qfalse;
return;
}

if (!uiInfo.serverStatus.refreshActive) {
                // not currently refreshing
                return;
        }
	uiInfo.serverStatus.refreshActive = qfalse;
	Com_Printf("%d servers listed in browser with %d players.\n",
					uiInfo.serverStatus.numDisplayServers,
					uiInfo.serverStatus.numPlayersOnServers);
	count = trap_LAN_GetServerCount(ui_netSource.integer);
	if (count - uiInfo.serverStatus.numDisplayServers > 0) {
		Com_Printf("%d servers not listed due to packet loss or pings higher than %d\n",
						count - uiInfo.serverStatus.numDisplayServers,
						(int) trap_Cvar_VariableValue("cl_maxPing"));
	}

		}

/*
=================
ArenaServers_MaxPing
=================
*/

/*
=================
UI_DoServerRefresh
=================
*/
static void UI_DoServerRefresh( void )
{
        qboolean wait = qfalse;

        if (!UI_ServerBrowserEnabled()) {
                uiInfo.serverStatus.refreshActive = qfalse;
                return;
        }

        if (!uiInfo.serverStatus.refreshActive) {
                return;
        }
	if (ui_netSource.integer != AS_FAVORITES) {
		if (ui_netSource.integer == AS_LOCAL) {
			if (!trap_LAN_GetServerCount(ui_netSource.integer)) {
				wait = qtrue;
			}
		} else {
			if (trap_LAN_GetServerCount(ui_netSource.integer) < 0) {
				wait = qtrue;
			}
		}
	}

	if (uiInfo.uiDC.realTime < uiInfo.serverStatus.refreshtime) {
		if (wait) {
			return;
		}
	}

	// if still trying to retrieve pings
	if (trap_LAN_UpdateVisiblePings(ui_netSource.integer)) {
		uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime + 1000;
	} else if (!wait) {
		// get the last servers in the list
		UI_BuildServerDisplayList(2);
		// stop the refresh
		UI_StopServerRefresh();
	}
	//
	UI_BuildServerDisplayList(qfalse);
		}

/*
=================
UI_StartServerRefresh
=================
*/
static void UI_StartServerRefresh(qboolean full)
	{
	int		i;
	char	*ptr;

	if (!UI_ServerBrowserEnabled()) {
	uiInfo.serverStatus.refreshActive = qfalse;
	return;
	}

	qtime_t q;
	trap_RealTime(&q);
	trap_Cvar_Set( va("ui_lastServerRefresh_%i", ui_netSource.integer), va("%s-%i, %i at %i:%i", MonthAbbrev[q.tm_mon],q.tm_mday, 1900+q.tm_year,q.tm_hour,q.tm_min));

	if (!full) {
		UI_UpdatePendingPings();
		return;
	}

	uiInfo.serverStatus.refreshActive = qtrue;
	uiInfo.serverStatus.nextDisplayRefresh = uiInfo.uiDC.realTime + 1000;
	// clear number of displayed servers
	uiInfo.serverStatus.numDisplayServers = 0;
	uiInfo.serverStatus.numPlayersOnServers = 0;
	// mark all servers as visible so we store ping updates for them
	trap_LAN_MarkServerVisible(ui_netSource.integer, -1, qtrue);
	// reset all the pings
	trap_LAN_ResetPings(ui_netSource.integer);
	//
	if( ui_netSource.integer == AS_LOCAL ) {
		trap_Cmd_ExecuteText( EXEC_NOW, "localservers\n" );
		uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime + 1000;
		return;
	}

	uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime + 5000;
	if( ui_netSource.integer == AS_GLOBAL || ui_netSource.integer == AS_MPLAYER ) {
		if( ui_netSource.integer == AS_GLOBAL ) {
			i = 0;
		}
		else {
			i = 1;
		}

		ptr = UI_Cvar_VariableString("debug_protocol");
		if (strlen(ptr)) {
			trap_Cmd_ExecuteText( EXEC_NOW, va( "globalservers %d %s full empty\n", i, ptr));
		}
		else {
			trap_Cmd_ExecuteText( EXEC_NOW, va( "globalservers %d %d full empty\n", i, (int)trap_Cvar_VariableValue( "protocol" ) ) );
		}
	}
		}
