#include "ui_local.h"

static const char *const uiBridgeMenuSet =
"// bridge-friendly menu defs\n"
"{\n"
"loadMenu { \"ui/ql_bridge_main.menu\" }\n"
"loadMenu { \"ui/ql_bridge_browser.menu\" }\n"
"loadMenu { \"ui/ql_bridge_credentials.menu\" }\n"
"loadMenu { \"ui/main_options.menu\" }\n"
"loadMenu { \"ui/demo.menu\" }\n"
"loadMenu { \"ui/connect.menu\" }\n"
"loadMenu { \"ui/error.menu\" }\n"
"loadMenu { \"ui/quit.menu\" }\n"
"}\n";

static const char *const uiBridgeIngameMenuSet =
"// bridge-friendly ingame menu set\n"
"{\n"
"loadMenu { \"ui/ingame.menu\" }\n"
"loadMenu { \"ui/ingame_about.menu\" }\n"
"loadMenu { \"ui/ingame_addbot.menu\" }\n"
"loadMenu { \"ui/ingame_admin.menu\" }\n"
"loadMenu { \"ui/ingame_callvote.menu\" }\n"
"loadMenu { \"ui/ingame_controls.menu\" }\n"
"loadMenu { \"ui/ingame_join.menu\" }\n"
"loadMenu { \"ui/ingame_options.menu\" }\n"
"loadMenu { \"ui/ingame_vote.menu\" }\n"
"}\n";

static const char *const uiBridgeMainMenu =
"#include \"ui/menudef.h\"\n"
"\n"
"{\n"
"assetGlobalDef {\n"
"font \"fonts/font\" 16\n"
"smallFont \"fonts/smallfont\" 12\n"
"bigFont \"fonts/bigfont\" 20\n"
"cursor \"ui/assets/3_cursor3\"\n"
"gradientBar \"ui/assets/gradientbar2.tga\"\n"
"itemFocusSound \"sound/misc/menu2.wav\"\n"
"shadowColor 0.1 0.1 0.1 0.25\n"
"}\n"
"\n"
"menuDef {\n"
"name \"main\"\n"
"fullScreen MENU_TRUE\n"
"rect 0 0 640 480\n"
"visible MENU_TRUE\n"
"focusColor 1 .75 0 1\n"
"style WINDOW_STYLE_EMPTY\n"
"background \"ui/assets/backscreen_smoke\"\n"
"backgroundSize 0 0 1920 1080\n"
"\n"
"onOpen {\n"
"uiScript stopRefresh\n"
"}\n"
"\n"
"onESC { close main }\n"
"\n"
"itemDef {\n"
"name title\n"
"type ITEM_TYPE_TEXT\n"
"rect 60 40 520 40\n"
"text \"QUAKE LIVE (BRIDGE)\"\n"
"textscale .5\n"
"textalign ITEM_ALIGN_LEFT\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name playonline\n"
"text \"PLAY ONLINE\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 60 120 200 24\n"
"textscale .35\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 18\n"
"forecolor 1 1 1 1\n"
"action { close main ; open ql_bridge_browser }\n"
"}\n"
"\n"
"itemDef {\n"
"name credentials\n"
"text \"CREDENTIALS\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 60 160 200 24\n"
"textscale .35\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 18\n"
"forecolor 1 1 1 1\n"
"action { close main ; open ql_bridge_credentials }\n"
"}\n"
"\n"
"itemDef {\n"
"name options\n"
"text \"SETTINGS\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 60 200 200 24\n"
"textscale .35\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 18\n"
"forecolor 1 1 1 1\n"
"action { close main ; open main_options }\n"
"}\n"
"\n"
"itemDef {\n"
"name demo\n"
"text \"DEMOS\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 60 240 200 24\n"
"textscale .35\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 18\n"
"forecolor 1 1 1 1\n"
"action { close main ; open demo }\n"
"}\n"
"\n"
"itemDef {\n"
"name quit\n"
"text \"QUIT\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 60 280 200 24\n"
"textscale .35\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 18\n"
"forecolor 1 1 1 1\n"
"action { open quit_popmenu }\n"
"}\n"
"}\n"
"}\n";

static const char *const uiBridgeBrowserMenu =
"#include \"ui/menudef.h\"\n"
"\n"
"{\n"
"menuDef {\n"
"name \"ql_bridge_browser\"\n"
"fullScreen MENU_TRUE\n"
"rect 0 0 640 480\n"
"visible MENU_TRUE\n"
"focusColor 1 .75 0 1\n"
"style WINDOW_STYLE_EMPTY\n"
"background \"ui/assets/backscreen_smoke\"\n"
"backgroundSize 0 0 1920 1080\n"
"\n"
"onOpen {\n"
"uiScript RefreshServers\n"
"}\n"
"\n"
"onClose {\n"
"uiScript StopRefresh\n"
"}\n"
"\n"
"itemDef {\n"
"name title\n"
"type ITEM_TYPE_TEXT\n"
"rect 60 32 520 24\n"
"text \"SERVER BROWSER (BRIDGE)\"\n"
"textscale .45\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name source\n"
"type ITEM_TYPE_MULTI\n"
"rect 60 72 240 20\n"
"text \"Source\"\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 16\n"
"cvar \"ui_netSource\"\n"
"cvarFloatList { \"Local\" 0 \"Internet\" 2 \"Favorites\" 3 }\n"
"action { uiScript RefreshFilter }\n"
"}\n"
"\n"
"itemDef {\n"
"name showEmpty\n"
"type ITEM_TYPE_MULTI\n"
"rect 320 72 120 20\n"
"text \"Show Empty\"\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 16\n"
"cvar \"ui_browserShowEmpty\"\n"
"cvarFloatList { \"No\" 0 \"Yes\" 1 }\n"
"action { uiScript RefreshFilter }\n"
"}\n"
"\n"
"itemDef {\n"
"name showFull\n"
"type ITEM_TYPE_MULTI\n"
"rect 480 72 120 20\n"
"text \"Show Full\"\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 12\n"
"textaligny 16\n"
"cvar \"ui_browserShowFull\"\n"
"cvarFloatList { \"No\" 0 \"Yes\" 1 }\n"
"action { uiScript RefreshFilter }\n"
"}\n"
"\n"
"itemDef {\n"
"name servers\n"
"type ITEM_TYPE_LISTBOX\n"
"style WINDOW_STYLE_FILLED\n"
"rect 40 110 560 230\n"
"elementtype LISTBOX_TEXT\n"
"elementheight 16\n"
"columns 6 16 32 48 220 120 80\n"
"feeder FEEDER_SERVERS\n"
"forecolor 1 1 1 1\n"
"border WINDOW_BORDER_FULL\n"
"bordercolor 0.5 0.5 0.5 0.5\n"
"textscale .24\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 8\n"
"textaligny 12\n"
"doubleclick { uiScript JoinServer }\n"
"}\n"
"\n"
"itemDef {\n"
"name status\n"
"type ITEM_TYPE_LISTBOX\n"
"style WINDOW_STYLE_FILLED\n"
"rect 40 350 560 90\n"
"elementtype LISTBOX_TEXT\n"
"elementheight 14\n"
"columns 1 12\n"
"feeder FEEDER_SERVERSTATUS\n"
"forecolor 1 1 1 1\n"
"border WINDOW_BORDER_FULL\n"
"bordercolor 0.5 0.5 0.5 0.5\n"
"textscale .22\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 8\n"
"textaligny 10\n"
"}\n"
"\n"
"itemDef {\n"
"name refresh\n"
"text \"REFRESH\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 60 452 90 20\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 10\n"
"textaligny 16\n"
"forecolor 1 1 1 1\n"
"action { uiScript RefreshServers }\n"
"}\n"
"\n"
"itemDef {\n"
"name stop\n"
"text \"STOP\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 160 452 70 20\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 10\n"
"textaligny 16\n"
"forecolor 1 1 1 1\n"
"action { uiScript StopRefresh }\n"
"}\n"
"\n"
"itemDef {\n"
"name details\n"
"text \"DETAILS\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 250 452 80 20\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 10\n"
"textaligny 16\n"
"forecolor 1 1 1 1\n"
"action { uiScript ServerStatus }\n"
"}\n"
"\n"
"itemDef {\n"
"name join\n"
"text \"JOIN\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 340 452 70 20\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 10\n"
"textaligny 16\n"
"forecolor 1 1 1 1\n"
"action { uiScript JoinServer }\n"
"}\n"
"\n"
"itemDef {\n"
"name back\n"
"text \"BACK\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 430 452 70 20\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 10\n"
"textaligny 16\n"
"forecolor 1 1 1 1\n"
"action { uiScript StopRefresh ; close ql_bridge_browser ; open main }\n"
"}\n"
"}\n"
"}\n";

static const char *const uiBridgeCredentialsMenu =
"#include \"ui/menudef.h\"\n"
"\n"
"{\n"
"menuDef {\n"
"name \"ql_bridge_credentials\"\n"
"fullScreen MENU_TRUE\n"
"rect 0 0 640 480\n"
"visible MENU_TRUE\n"
"focusColor 1 .75 0 1\n"
"style WINDOW_STYLE_EMPTY\n"
"background \"ui/assets/backscreen_smoke\"\n"
"backgroundSize 0 0 1920 1080\n"
"\n"
"onOpen {\n"
"uiScript getCDKey\n"
"}\n"
"\n"
"onESC { close ql_bridge_credentials ; open main }\n"
"\n"
"itemDef {\n"
"name title\n"
"type ITEM_TYPE_TEXT\n"
"rect 60 40 520 24\n"
"text \"CD KEY\"\n"
"textscale .45\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name prompt\n"
"type ITEM_TYPE_TEXT\n"
"rect 60 80 520 18\n"
"text \"Please enter your CD Key.\"\n"
"textscale .30\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name credential1\n"
"type ITEM_TYPE_EDITFIELD\n"
"rect 60 120 100 20\n"
"text \"\"\n"
"cvar \"cdkey1\"\n"
"textscale .28\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name credential2\n"
"type ITEM_TYPE_EDITFIELD\n"
"rect 170 120 100 20\n"
"text \"\"\n"
"cvar \"cdkey2\"\n"
"textscale .28\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name credential3\n"
"type ITEM_TYPE_EDITFIELD\n"
"rect 280 120 100 20\n"
"text \"\"\n"
"cvar \"cdkey3\"\n"
"textscale .28\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name credential4\n"
"type ITEM_TYPE_EDITFIELD\n"
"rect 390 120 100 20\n"
"text \"\"\n"
"cvar \"cdkey4\"\n"
"textscale .28\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name status\n"
"type ITEM_TYPE_TEXT\n"
"rect 60 155 520 16\n"
"text \"${ui_cdkeyvalid}\"\n"
"textscale .25\n"
"forecolor 1 1 1 1\n"
"}\n"
"\n"
"itemDef {\n"
"name verify\n"
"text \"VERIFY\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 60 185 100 20\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 10\n"
"textaligny 16\n"
"forecolor 1 1 1 1\n"
"action { uiScript verifyCDKey }\n"
"}\n"
"\n"
"itemDef {\n"
"name back\n"
"text \"BACK\"\n"
"type ITEM_TYPE_BUTTON\n"
"rect 170 185 100 20\n"
"textscale .30\n"
"textalign ITEM_ALIGN_LEFT\n"
"textalignx 10\n"
"textaligny 16\n"
"forecolor 1 1 1 1\n"
"action { close ql_bridge_credentials ; open main }\n"
"}\n"
"}\n"
"}\n";

static qboolean ui_browserBridgeActive = qfalse;
static qboolean ui_browserBridgeAvailable = qfalse;
static qboolean ui_browserBridgeChecked = qfalse;

/*
=============
UI_BridgeFileExists

Helper wrapper that checks if a UI script is reachable through the virtual
filesystem so the bridge can gracefully fall back before init completes.
=============
*/
static qboolean UI_BridgeFileExists(const char *path) {
	fileHandle_t handle;
	int length;

	if (!path || !*path) {
		return qfalse;
	}

	length = trap_FS_FOpenFile(path, &handle, FS_READ);
	if (handle) {
		trap_FS_FCloseFile(handle);
	}

	return (length > 0);
}

/*
=============
UI_WriteBridgeFile

Generate an auto bridge asset in the user's writable directory so we don't
need to patch retail content.
=============
*/
static qboolean UI_WriteBridgeFile(const char *path, const char *data) {
	fileHandle_t handle;

	if (!path || !data) {
		return qfalse;
	}

	trap_FS_FOpenFile(path, &handle, FS_WRITE);
	if (!handle) {
		return qfalse;
	}

	trap_FS_Write(data, strlen(data), handle);
	trap_FS_FCloseFile(handle);
	return qtrue;
}

/*
=============
UI_WriteBridgeScripts

Emit the bridge menu script set on demand, avoiding changes to packaged
assets while still enabling the menu-based Quake Live flow.
=============
*/
static qboolean UI_WriteBridgeScripts(void) {
	qboolean ok = qtrue;

	if (!UI_BridgeFileExists(UI_MENU_FILE_QUAKELIVE_BRIDGE)) {
		ok = UI_WriteBridgeFile(UI_MENU_FILE_QUAKELIVE_BRIDGE, uiBridgeMenuSet) && ok;
	}

	if (!UI_BridgeFileExists(UI_INGAME_FILE_QUAKELIVE_BRIDGE)) {
		ok = UI_WriteBridgeFile(UI_INGAME_FILE_QUAKELIVE_BRIDGE, uiBridgeIngameMenuSet) && ok;
	}

	if (!UI_BridgeFileExists("ui/ql_bridge_main.menu")) {
		ok = UI_WriteBridgeFile("ui/ql_bridge_main.menu", uiBridgeMainMenu) && ok;
	}

	if (!UI_BridgeFileExists("ui/ql_bridge_browser.menu")) {
		ok = UI_WriteBridgeFile("ui/ql_bridge_browser.menu", uiBridgeBrowserMenu) && ok;
	}

	if (!UI_BridgeFileExists("ui/ql_bridge_credentials.menu")) {
		ok = UI_WriteBridgeFile("ui/ql_bridge_credentials.menu", uiBridgeCredentialsMenu) && ok;
	}

	if (!ok) {
		trap_Print( "UI_WriteBridgeScripts: Failed to write bridge menu files.\n" );
	}

	return ok;
}

/*
=============
UI_BrowserBridge_Init

Resolve bridge availability lazily so menu flow fallbacks can prefer scripted
Quake Live navigation when the Awesomium overlay is offline.
=============
*/
void UI_BrowserBridge_Init(void) {
	ui_browserBridgeChecked = qtrue;
	ui_browserBridgeAvailable = UI_WriteBridgeScripts();
}

/*
=============
UI_BrowserBridgeAvailable
=============
*/
qboolean UI_BrowserBridgeAvailable(void) {
	if (!ui_browserBridgeChecked) {
		UI_BrowserBridge_Init();
	}

	return ui_browserBridgeAvailable;
}

/*
=============
UI_BrowserBridge_SetActive

Mark the scripted Quake Live bridge as active when the runtime switches away
from the Awesomium overlay.
=============
*/
void UI_BrowserBridge_SetActive(qboolean active) {
	ui_browserBridgeActive = active;

	if (active && !ui_browserBridgeChecked) {
		UI_BrowserBridge_Init();
	}
}

/*
=============
UI_BrowserBridgeActive
=============
*/
qboolean UI_BrowserBridgeActive(void) {
	return ui_browserBridgeActive;
}

/*
=============
UI_BrowserBridgeMenuFile
=============
*/
const char *UI_BrowserBridgeMenuFile(void) {
	return UI_MENU_FILE_QUAKELIVE_BRIDGE;
}

/*
=============
UI_BrowserBridgeIngameFile
=============
*/
const char *UI_BrowserBridgeIngameFile(void) {
	return UI_INGAME_FILE_QUAKELIVE_BRIDGE;
}
