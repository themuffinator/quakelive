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
/**********************************************************************
	UI_ATOMS.C

	User interface building blocks and support functions.
**********************************************************************/
#include "ui_local.h"
#include <string.h>

qboolean		m_entersound;		// after a frame, so caching won't disrupt the sound

// these are here so the functions in q_shared.c can link
#ifndef UI_HARD_LINKED

void QDECL Com_Error( int level, const char *error, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, error);
	vsprintf (text, error, argptr);
	va_end (argptr);

	trap_Error( va("%s", text) );
}

void QDECL Com_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, msg);
	vsprintf (text, msg, argptr);
	va_end (argptr);

	trap_Print( va("%s", text) );
}

/*
=============
Com_DPrintf

Route debug UI logging through the same trap-backed print channel in standalone
native UI builds where qcommon's developer print helper is not linked.
=============
*/
void QDECL Com_DPrintf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start( argptr, msg );
	vsprintf( text, msg, argptr );
	va_end( argptr );

	trap_Print( va("%s", text) );
}

/*
=============
Com_Memset

Provide the qcommon memory helper expected by the shared GPL UI modules when
the native UI DLL is linked without qcommon/common.c.
=============
*/
void Com_Memset( void *dest, const int val, const size_t count ) {
	memset( dest, val, count );
}

#endif

qboolean newUI = qfalse;
static int uiCachedImageCount = 0;

#define UI_IMAGE_CACHE_LIMIT 128

typedef struct uiCachedImage_s {
	char uri[MAX_STRING_CHARS];
	qhandle_t shader;
} uiCachedImage_t;

static uiCachedImage_t uiCachedImages[UI_IMAGE_CACHE_LIMIT];


/*
=============
UI_ImageCache_Reset

Clear the cached image table so lookups start fresh.
=============
*/
	static void UI_ImageCache_Reset( void ) {
	uiCachedImageCount = 0;
	Com_Memset( uiCachedImages, 0, sizeof( uiCachedImages ) );
}

/*
=============
	UI_ImageCache_Find

	Return the cached shader for the provided URI if present.
=============
*/
	static qhandle_t UI_ImageCache_Find( const char *uri ) {
	int i;

	if ( !uri || !uri[0] ) {
	return 0;
}

	for ( i = 0; i < uiCachedImageCount; i++ ) {
	if ( !Q_stricmp( uiCachedImages[i].uri, uri ) ) {
	return uiCachedImages[i].shader;
}
}

	return 0;
}

/*
=============
	UI_ImageCache_Store

	Persist a shader handle against its source URI in the cache.
=============
*/
	static void UI_ImageCache_Store( const char *uri, qhandle_t shader ) {
	int i;

	if ( uiCachedImageCount >= UI_IMAGE_CACHE_LIMIT ) {
	for ( i = 1; i < UI_IMAGE_CACHE_LIMIT; i++ ) {
	uiCachedImages[i - 1] = uiCachedImages[i];
}
	uiCachedImageCount = UI_IMAGE_CACHE_LIMIT - 1;
}

	Q_strncpyz( uiCachedImages[uiCachedImageCount].uri, uri, sizeof( uiCachedImages[uiCachedImageCount].uri ) );
	uiCachedImages[uiCachedImageCount].shader = shader;
	uiCachedImageCount++;
}

/*
=============
	UI_ImageCache_StripProtocol

	Remove a scheme prefix from a URI, returning the path portion.
=============
*/
	static const char *UI_ImageCache_StripProtocol( const char *uri ) {
	const char *separator;

	if ( !uri ) {
	return NULL;
}

	separator = strstr( uri, "://" );
	if ( separator ) {
	return separator + 3;
}

	separator = strchr( uri, ':' );
	if ( separator ) {
	return separator + 1;
}

	return uri;
}

/*
=============
	UI_ImageCache_IsSteamUri

	Detect whether the provided URI references a Steam-backed image.
=============
*/
	static qboolean UI_ImageCache_IsSteamUri( const char *uri ) {
	if ( !uri ) {
	return qfalse;
}

	return ( !Q_stricmpn( uri, "steam://", 8 ) || !Q_stricmpn( uri, "steam:", 6 ) ) ? qtrue : qfalse;
}

/*
=============
	UI_ImageCache_RewriteWebPath

	Normalize an HTTP-style URI into a quake path for registration.
=============
*/
	static qboolean UI_ImageCache_RewriteWebPath( const char *uri, char *outPath, int outSize ) {
	const char *trimmed;
	char localPath[MAX_QPATH];
	char webPath[MAX_QPATH];
	int i;

	if ( !uri || !outPath || outSize <= 0 ) {
	return qfalse;
}

	trimmed = UI_ImageCache_StripProtocol( uri );
	if ( !trimmed || !*trimmed ) {
	return qfalse;
}

	for ( i = 0; trimmed[i] && trimmed[i] != '?' && trimmed[i] != '#'; i++ ) {
	if ( i >= (int)sizeof( localPath ) - 1 ) {
	break;
}
	localPath[i] = trimmed[i];
}
	localPath[i] = '\0';

	if ( !*localPath || strstr( localPath, ".." ) ) {
	return qfalse;
}

	if ( !Q_stricmpn( localPath, "screenshots/", 12 ) ) {
	Q_strncpyz( outPath, localPath, outSize );
	return qtrue;
}

	trap_Cvar_VariableStringBuffer( "fs_webpath", webPath, sizeof( webPath ) );
	if ( !webPath[0] ) {
	return qfalse;
}

	Com_sprintf( outPath, outSize, "%s/%s", webPath, localPath );
	return qtrue;
}

/*
=============
	UI_ImageCache_ReadFromPak

	Prime a web.pak entry through FS_FOpenFileRead / FS_Read before registration.
=============
*/
	static qboolean UI_ImageCache_ReadFromPak( const char *qpath ) {
	fileHandle_t handle;
	byte scratch[1];
	int length;

	length = trap_FS_FOpenFile( qpath, &handle, FS_READ );
	if ( length <= 0 || !handle ) {
	return qfalse;
}

	if ( length > 0 ) {
	trap_FS_Read( scratch, 1, handle );
}

	trap_FS_FCloseFile( handle );
	return qtrue;
}

/*
=============
	UI_ImageCache_Register

	Resolve or create a shader handle for a URI, caching results for reuse.
=============
*/
	qhandle_t UI_ImageCache_Register( const char *uri ) {
	qhandle_t shader;
	char qpath[MAX_QPATH];

	shader = UI_ImageCache_Find( uri );
	if ( shader ) {
	return shader;
}

	if ( !uri || !uri[0] ) {
	return 0;
}

	if ( UI_ImageCache_IsSteamUri( uri ) ) {
	const char *steamPath = UI_ImageCache_StripProtocol( uri );
	Com_sprintf( qpath, sizeof( qpath ), "steam/%s", steamPath );
	} else if ( UI_ImageCache_RewriteWebPath( uri, qpath, sizeof( qpath ) ) ) {
	/* path rewritten into qpath */
	} else {
	Q_strncpyz( qpath, uri, sizeof( qpath ) );
}

	UI_ImageCache_ReadFromPak( qpath );
	shader = trap_R_RegisterShaderNoMip( qpath );

	if ( shader ) {
	UI_ImageCache_Store( uri, shader );
}

	return shader;
}

/*
=============
	UI_ImageCache_Shutdown

	Release cached image metadata when the UI shuts down.
=============
*/
	void UI_ImageCache_Shutdown( void ) {
	UI_ImageCache_Reset();
}


/*
=================
UI_ClampCvar
=================
*/
float UI_ClampCvar( float min, float max, float value )
{
	if ( value < min ) return min;
	if ( value > max ) return max;
	return value;
}

/*
=================
UI_StartDemoLoop
=================
*/
void UI_StartDemoLoop( void ) {
        trap_Cmd_ExecuteText( EXEC_APPEND, "d1\n" );
}


void UI_StopMenuRefresh( void ) {
        UI_StopServerRefresh();
        uiInfo.serverStatus.nextDisplayRefresh = 0;
        uiInfo.nextServerStatusRefresh = 0;
        uiInfo.nextFindPlayerRefresh = 0;
}

void UI_CloseInGameMenu( void ) {
        trap_Key_SetCatcher( trap_Key_GetCatcher() & ~KEYCATCH_UI );
        trap_Key_ClearStates();
        trap_Cvar_Set( "cl_paused", "0" );
        Menus_CloseAll();
}

void UI_LeaveGame( void ) {
        trap_Cmd_ExecuteText( EXEC_APPEND, "disconnect\n" );
        trap_Key_SetCatcher( KEYCATCH_UI );
        Menus_CloseAll();
        Menus_ActivateByName("main");
}




char *UI_Argv( int arg ) {
	static char	buffer[MAX_STRING_CHARS];

	trap_Argv( arg, buffer, sizeof( buffer ) );

	return buffer;
}


char *UI_Cvar_VariableString( const char *var_name ) {
	static char	buffer[MAX_STRING_CHARS];

	trap_Cvar_VariableStringBuffer( var_name, buffer, sizeof( buffer ) );

	return buffer;
}



void UI_SetBestScores(postGameInfo_t *newInfo, qboolean postGame) {
	trap_Cvar_Set("ui_scoreAccuracy",     va("%i%%", newInfo->accuracy));
	trap_Cvar_Set("ui_scoreImpressives",	va("%i", newInfo->impressives));
	trap_Cvar_Set("ui_scoreExcellents", 	va("%i", newInfo->excellents));
	trap_Cvar_Set("ui_scoreDefends", 			va("%i", newInfo->defends));
	trap_Cvar_Set("ui_scoreAssists", 			va("%i", newInfo->assists));
	trap_Cvar_Set("ui_scoreGauntlets", 		va("%i", newInfo->gauntlets));
	trap_Cvar_Set("ui_scoreScore", 				va("%i", newInfo->score));
	trap_Cvar_Set("ui_scorePerfect",	 		va("%i", newInfo->perfects));
	trap_Cvar_Set("ui_scoreTeam",					va("%i to %i", newInfo->redScore, newInfo->blueScore));
	trap_Cvar_Set("ui_scoreBase",					va("%i", newInfo->baseScore));
	trap_Cvar_Set("ui_scoreTimeBonus",		va("%i", newInfo->timeBonus));
	trap_Cvar_Set("ui_scoreSkillBonus",		va("%i", newInfo->skillBonus));
	trap_Cvar_Set("ui_scoreShutoutBonus",	va("%i", newInfo->shutoutBonus));
	trap_Cvar_Set("ui_scoreTime",					va("%02i:%02i", newInfo->time / 60, newInfo->time % 60));
	trap_Cvar_Set("ui_scoreCaptures",		va("%i", newInfo->captures));
  if (postGame) {
		trap_Cvar_Set("ui_scoreAccuracy2",     va("%i%%", newInfo->accuracy));
		trap_Cvar_Set("ui_scoreImpressives2",	va("%i", newInfo->impressives));
		trap_Cvar_Set("ui_scoreExcellents2", 	va("%i", newInfo->excellents));
		trap_Cvar_Set("ui_scoreDefends2", 			va("%i", newInfo->defends));
		trap_Cvar_Set("ui_scoreAssists2", 			va("%i", newInfo->assists));
		trap_Cvar_Set("ui_scoreGauntlets2", 		va("%i", newInfo->gauntlets));
		trap_Cvar_Set("ui_scoreScore2", 				va("%i", newInfo->score));
		trap_Cvar_Set("ui_scorePerfect2",	 		va("%i", newInfo->perfects));
		trap_Cvar_Set("ui_scoreTeam2",					va("%i to %i", newInfo->redScore, newInfo->blueScore));
		trap_Cvar_Set("ui_scoreBase2",					va("%i", newInfo->baseScore));
		trap_Cvar_Set("ui_scoreTimeBonus2",		va("%i", newInfo->timeBonus));
		trap_Cvar_Set("ui_scoreSkillBonus2",		va("%i", newInfo->skillBonus));
		trap_Cvar_Set("ui_scoreShutoutBonus2",	va("%i", newInfo->shutoutBonus));
		trap_Cvar_Set("ui_scoreTime2",					va("%02i:%02i", newInfo->time / 60, newInfo->time % 60));
		trap_Cvar_Set("ui_scoreCaptures2",		va("%i", newInfo->captures));
	}
}

void UI_LoadBestScores(const char *map, int game) {
	char		fileName[MAX_QPATH];
	fileHandle_t f;
	postGameInfo_t newInfo;

	memset(&newInfo, 0, sizeof(postGameInfo_t));
	uiInfo.demoAvailable = qfalse;

	// Retail reaches this helper with a populated current map/gametype selection.
	// The reconstructed runtime can hit it before gameinfo metadata exists, so keep
	// the zeroed score state and skip invalid file probes until that table is loaded.
	if ( !map || !map[0] || game < 0 || game >= GT_MAX_GAME_TYPE ) {
		UI_SetBestScores(&newInfo, qfalse);
		return;
	}

	Com_sprintf(fileName, MAX_QPATH, "games/%s_%i.game", map, game);
	if (trap_FS_FOpenFile(fileName, &f, FS_READ) >= 0) {
		int size = 0;
		trap_FS_Read(&size, sizeof(int), f);
		if (size == sizeof(postGameInfo_t)) {
			trap_FS_Read(&newInfo, sizeof(postGameInfo_t), f);
		}
		trap_FS_FCloseFile(f);
	}
	UI_SetBestScores(&newInfo, qfalse);

	Com_sprintf(fileName, MAX_QPATH, "demos/%s_%d.dm_%d", map, game, (int)trap_Cvar_VariableValue("protocol"));
	if (trap_FS_FOpenFile(fileName, &f, FS_READ) >= 0) {
		uiInfo.demoAvailable = qtrue;
		trap_FS_FCloseFile(f);
	} 
}

/*
===============
UI_ClearScores
===============
*/
void UI_ClearScores() {
	char	gameList[4096];
	char *gameFile;
	int		i, len, count, size;
	fileHandle_t f;
	postGameInfo_t newInfo;

	count = trap_FS_GetFileList( "games", "game", gameList, sizeof(gameList) );

	size = sizeof(postGameInfo_t);
	memset(&newInfo, 0, size);

	if (count > 0) {
		gameFile = gameList;
		for ( i = 0; i < count; i++ ) {
			len = strlen(gameFile);
			if (trap_FS_FOpenFile(va("games/%s",gameFile), &f, FS_WRITE) >= 0) {
				trap_FS_Write(&size, sizeof(int), f);
				trap_FS_Write(&newInfo, size, f);
				trap_FS_FCloseFile(f);
			}
			gameFile += len + 1;
		}
	}
	
	UI_SetBestScores(&newInfo, qfalse);

}



static void	UI_Cache_f() {
	Display_CacheAll();
	UI_CDKeyMenu_Cache();
}

/*
=======================
UI_ConsoleCommand_MenuClose
=======================
*/
static void UI_ConsoleCommand_MenuClose( void ) {
	char menuName[MAX_QPATH];

	if ( trap_Argc() < 2 ) {
		return;
	}

	Q_strncpyz( menuName, UI_Argv( 1 ), sizeof( menuName ) );
	if ( !menuName[0] ) {
		return;
	}

	Menus_CloseByName( menuName );
}

/*
=======================
UI_ConsoleCommand_MenuOpen
=======================
*/
static void UI_ConsoleCommand_MenuOpen( void ) {
	char menuName[MAX_QPATH];

	if ( trap_Argc() < 2 ) {
		return;
	}

	Q_strncpyz( menuName, UI_Argv( 1 ), sizeof( menuName ) );
	if ( !menuName[0] ) {
		return;
	}

	Menus_OpenByName( menuName );
}

/*
=======================
UI_CalcPostGameStats
=======================
*/
static void UI_CalcPostGameStats() {
	char		map[MAX_QPATH];
	char		fileName[MAX_QPATH];
	char		info[MAX_INFO_STRING];
	fileHandle_t f;
	int size, game, time, adjustedTime;
	postGameInfo_t oldInfo;
	postGameInfo_t newInfo;
	qboolean newHigh = qfalse;

	trap_GetConfigString( CS_SERVERINFO, info, sizeof(info) );
	Q_strncpyz( map, Info_ValueForKey( info, "mapname" ), sizeof(map) );
	game = atoi(Info_ValueForKey(info, "g_gametype"));

	// compose file name
	Com_sprintf(fileName, MAX_QPATH, "games/%s_%i.game", map, game);
	// see if we have one already
	memset(&oldInfo, 0, sizeof(postGameInfo_t));
	if (trap_FS_FOpenFile(fileName, &f, FS_READ) >= 0) {
	// if so load it
		size = 0;
		trap_FS_Read(&size, sizeof(int), f);
		if (size == sizeof(postGameInfo_t)) {
			trap_FS_Read(&oldInfo, sizeof(postGameInfo_t), f);
		}
		trap_FS_FCloseFile(f);
	}					 

	newInfo.accuracy = atoi(UI_Argv(3));
	newInfo.impressives = atoi(UI_Argv(4));
	newInfo.excellents = atoi(UI_Argv(5));
	newInfo.defends = atoi(UI_Argv(6));
	newInfo.assists = atoi(UI_Argv(7));
	newInfo.gauntlets = atoi(UI_Argv(8));
	newInfo.baseScore = atoi(UI_Argv(9));
	newInfo.perfects = atoi(UI_Argv(10));
	newInfo.redScore = atoi(UI_Argv(11));
	newInfo.blueScore = atoi(UI_Argv(12));
	time = atoi(UI_Argv(13));
	newInfo.captures = atoi(UI_Argv(14));

	newInfo.time = (time - trap_Cvar_VariableValue("ui_matchStartTime")) / 1000;
	adjustedTime = uiInfo.mapList[ui_currentMap.integer].timeToBeat[game];
	if (newInfo.time < adjustedTime) { 
		newInfo.timeBonus = (adjustedTime - newInfo.time) * 10;
	} else {
		newInfo.timeBonus = 0;
	}

	if (newInfo.redScore > newInfo.blueScore && newInfo.blueScore <= 0) {
		newInfo.shutoutBonus = 100;
	} else {
		newInfo.shutoutBonus = 0;
	}

	newInfo.skillBonus = trap_Cvar_VariableValue("g_spSkill");
	if (newInfo.skillBonus <= 0) {
		newInfo.skillBonus = 1;
	}
	newInfo.score = newInfo.baseScore + newInfo.shutoutBonus + newInfo.timeBonus;
	newInfo.score *= newInfo.skillBonus;

	// see if the score is higher for this one
	newHigh = (newInfo.redScore > newInfo.blueScore && newInfo.score > oldInfo.score);

	if  (newHigh) {
		// if so write out the new one
		uiInfo.newHighScoreTime = uiInfo.uiDC.realTime + 20000;
		if (trap_FS_FOpenFile(fileName, &f, FS_WRITE) >= 0) {
			size = sizeof(postGameInfo_t);
			trap_FS_Write(&size, sizeof(int), f);
			trap_FS_Write(&newInfo, sizeof(postGameInfo_t), f);
			trap_FS_FCloseFile(f);
		}
	}

	if (newInfo.time < oldInfo.time) {
		uiInfo.newBestTime = uiInfo.uiDC.realTime + 20000;
	}
 
	// put back all the ui overrides
	trap_Cvar_Set("capturelimit", UI_Cvar_VariableString("ui_saveCaptureLimit"));
	trap_Cvar_Set("fraglimit", UI_Cvar_VariableString("ui_saveFragLimit"));
	trap_Cvar_Set("g_doWarmup", UI_Cvar_VariableString("ui_doWarmup"));
	trap_Cvar_Set("g_Warmup", UI_Cvar_VariableString("ui_Warmup"));
	trap_Cvar_Set("sv_pure", UI_Cvar_VariableString("ui_pure"));
	trap_Cvar_Set("g_friendlyFire", UI_Cvar_VariableString("ui_friendlyFire"));

	UI_SetBestScores(&newInfo, qtrue);

}


/*
=================
UI_ConsoleCommand
=================
*/
qboolean UI_ConsoleCommand( int realTime ) {
	char	*cmd;

	uiInfo.uiDC.frameTime = realTime - uiInfo.uiDC.realTime;
	uiInfo.uiDC.realTime = realTime;

	cmd = UI_Argv( 0 );

	// ensure minimum menu data is available
	//Menu_Cache();

	if ( Q_stricmp(cmd, "web_showBrowser") == 0 ) {
		char buff[1024];
		const char *name2 = NULL;
		qboolean overlayAvailable;

		if (trap_Argc() > 1) {
			name2 = UI_Argv(1);
		}

		if (name2 && *name2) {
			Com_sprintf(buff, sizeof(buff), "web_showBrowser %s\n", name2);
		} else {
			Com_sprintf(buff, sizeof(buff), "web_showBrowser\n");
		}

		overlayAvailable = UI_BrowserOverlayAvailable();
		if (!overlayAvailable) {
			Com_Printf("UI: browser overlay unavailable; web_showBrowser stubbed.\n");
			return qtrue;
		}

		UI_ApplyMenuFlowChange(UI_MENU_FLOW_QUAKELIVE, qfalse);
		trap_Cmd_ExecuteText(EXEC_NOW, buff);
		return qfalse;
	}

	if ( Q_stricmp(cmd, "ui_useLegacyMenus") == 0 || Q_stricmp(cmd, "ui_emergencyLegacyMenus") == 0 ) {
		Com_Printf("UI: legacy Quake III menu flow has been removed; using Quake Live menus.\n");
		UI_ApplyMenuFlowChange(UI_MENU_FLOW_QUAKELIVE, qtrue);
		return qtrue;
	}

	if ( Q_stricmp(cmd, "ui_useQuakeLiveMenus") == 0 ) {
		if (!UI_BrowserOverlayAvailable()) {
			Com_Printf("UI: browser overlay unavailable; loading retail Quake Live menus without web integration.\n");
		}

		UI_ApplyMenuFlowChange(UI_MENU_FLOW_QUAKELIVE, qtrue);
		return qtrue;
	}

	if ( Q_stricmp(cmd, "ui_toggleMenuFlow") == 0 ) {
		if (!UI_BrowserOverlayAvailable()) {
			Com_Printf("UI: retail Quake Live menus already active; browser overlay unavailable.\n");
		}

		UI_ApplyMenuFlowChange(UI_MENU_FLOW_QUAKELIVE, qtrue);
		return qtrue;
	}

	if ( Q_stricmp (cmd, "ui_report") == 0 ) {
		UI_Report();
		return qtrue;
	}

	if ( Q_stricmp (cmd, "listPlayerModels") == 0 ) {
		UI_ListPlayerModels();
		return qtrue;
	}

	if ( Q_stricmp (cmd, "ui_load") == 0 ) {
		UI_Load();
		return qtrue;
	}

	if ( Q_stricmp (cmd, "postgame") == 0 ) {
		UI_CalcPostGameStats();
		return qtrue;
	}

	if ( Q_stricmp (cmd, "ui_cache") == 0 ) {
		UI_Cache_f();
		return qtrue;
	}

	if ( Q_stricmp (cmd, "menu_close") == 0 ) {
		UI_ConsoleCommand_MenuClose();
		return qtrue;
	}

	if ( Q_stricmp (cmd, "menu_open") == 0 ) {
		UI_ConsoleCommand_MenuOpen();
		return qtrue;
	}

	return qfalse;
}

/*
=================
UI_Shutdown
=================
*/
void UI_Shutdown( void ) {
	UI_ImageCache_Shutdown();
}

/*
================
UI_AdjustFrom640

Adjusted for resolution and screen aspect ratio
================
*/
void UI_AdjustFrom640( float *x, float *y, float *w, float *h ) {
	if ( x ) {
		*x = ( *x * uiInfo.uiDC.xscale ) + uiInfo.uiDC.bias;
	}

	if ( y ) {
		*y *= uiInfo.uiDC.yscale;
	}

	if ( w ) {
		*w *= uiInfo.uiDC.xscale;
	}

	if ( h ) {
		*h *= uiInfo.uiDC.yscale;
	}
}

void UI_DrawNamedPic( float x, float y, float width, float height, const char *picname ) {
	qhandle_t	hShader;

	hShader = UI_ImageCache_Register( picname );
	if ( !hShader ) {
		hShader = trap_R_RegisterShaderNoMip( picname );
	}
	UI_AdjustFrom640( &x, &y, &width, &height );
	trap_R_DrawStretchPic( x, y, width, height, 0, 0, 1, 1, hShader );
}

void UI_DrawHandlePic( float x, float y, float w, float h, qhandle_t hShader ) {
	float	s0;
	float	s1;
	float	t0;
	float	t1;

	if( w < 0 ) {	// flip about vertical
		w  = -w;
		s0 = 1;
		s1 = 0;
	}
	else {
		s0 = 0;
		s1 = 1;
	}

	if( h < 0 ) {	// flip about horizontal
		h  = -h;
		t0 = 1;
		t1 = 0;
	}
	else {
		t0 = 0;
		t1 = 1;
	}
	
	UI_AdjustFrom640( &x, &y, &w, &h );
	trap_R_DrawStretchPic( x, y, w, h, s0, t0, s1, t1, hShader );
}

/*
================
UI_FillRect

Coordinates are 640*480 virtual values
=================
*/
void UI_FillRect( float x, float y, float width, float height, const float *color ) {
	trap_R_SetColor( color );

	UI_AdjustFrom640( &x, &y, &width, &height );
	trap_R_DrawStretchPic( x, y, width, height, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );

	trap_R_SetColor( NULL );
}

void UI_DrawSides(float x, float y, float w, float h) {
	UI_AdjustFrom640( &x, &y, &w, &h );
	trap_R_DrawStretchPic( x, y, 1, h, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
	trap_R_DrawStretchPic( x + w - 1, y, 1, h, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
}

void UI_DrawTopBottom(float x, float y, float w, float h) {
	UI_AdjustFrom640( &x, &y, &w, &h );
	trap_R_DrawStretchPic( x, y, w, 1, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
	trap_R_DrawStretchPic( x, y + h - 1, w, 1, 0, 0, 0, 0, uiInfo.uiDC.whiteShader );
}
/*
================
UI_DrawRect

Coordinates are 640*480 virtual values
=================
*/
void UI_DrawRect( float x, float y, float width, float height, const float *color ) {
	trap_R_SetColor( color );

  UI_DrawTopBottom(x, y, width, height);
  UI_DrawSides(x, y, width, height);

	trap_R_SetColor( NULL );
}

void UI_SetColor( const float *rgba ) {
	trap_R_SetColor( rgba );
}

void UI_UpdateScreen( void ) {
	trap_UpdateScreen();
}


void UI_DrawTextBox (int x, int y, int width, int lines)
{
	UI_FillRect( x + BIGCHAR_WIDTH/2, y + BIGCHAR_HEIGHT/2, ( width + 1 ) * BIGCHAR_WIDTH, ( lines + 1 ) * BIGCHAR_HEIGHT, colorBlack );
	UI_DrawRect( x + BIGCHAR_WIDTH/2, y + BIGCHAR_HEIGHT/2, ( width + 1 ) * BIGCHAR_WIDTH, ( lines + 1 ) * BIGCHAR_HEIGHT, colorWhite );
}

qboolean UI_CursorInRect (int x, int y, int width, int height)
{
	if (uiInfo.uiDC.cursorx < x ||
		uiInfo.uiDC.cursory < y ||
		uiInfo.uiDC.cursorx > x+width ||
		uiInfo.uiDC.cursory > y+height)
		return qfalse;

	return qtrue;
}
