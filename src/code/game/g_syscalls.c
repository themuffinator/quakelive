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
#include "g_local.h"
#include <stdint.h>

// this file is only included when building a dll
// g_syscalls.asm is included instead when building a qvm
#ifdef Q3_VM
#error "Do not use in VM build"
#endif

typedef void (QDECL *ql_import_f)( void );
typedef intptr_t (QDECL *ql_import_invoke15_t)(
	intptr_t arg0, intptr_t arg1, intptr_t arg2, intptr_t arg3, intptr_t arg4,
	intptr_t arg5, intptr_t arg6, intptr_t arg7, intptr_t arg8, intptr_t arg9,
	intptr_t arg10, intptr_t arg11, intptr_t arg12, intptr_t arg13, intptr_t arg14
);

static int (QDECL *syscall)( int arg, ... ) = (int (QDECL *)( int, ...))-1;
static ql_import_f *g_imports = NULL;

void **G_GetNativeExportTable( void );

/*
=================
G_InvokeImport
=================
*/
static int QDECL G_InvokeImport( ql_import_f import, const intptr_t *args ) {
	return (int)((ql_import_invoke15_t)import)(
		args[0], args[1], args[2], args[3], args[4],
		args[5], args[6], args[7], args[8], args[9],
		args[10], args[11], args[12], args[13], args[14]
	);
}

/*
=================
G_MapNativeImport
=================
*/
static int G_MapNativeImport( int arg, const intptr_t *stack ) {
	(void)stack;

	switch ( arg ) {
	case G_SEND_CONSOLE_COMMAND: return G_QL_IMPORT_SEND_CONSOLE_COMMAND;
	case G_PRINT: return G_QL_IMPORT_PRINT;
	case G_FS_WRITE: return G_QL_IMPORT_FS_WRITE;
	case G_FS_READ: return G_QL_IMPORT_FS_READ;
	case G_FS_GETFILELIST: return G_QL_IMPORT_FS_GETFILELIST;
	case G_FS_FOPEN_FILE: return G_QL_IMPORT_FS_FOPEN_FILE;
	case G_FS_FCLOSE_FILE: return G_QL_IMPORT_FS_FCLOSE_FILE;
	case G_ERROR: return G_QL_IMPORT_ERROR;
	case G_CVAR_VARIABLE_INTEGER_VALUE: return G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE;
	case G_CVAR_UPDATE: return G_QL_IMPORT_CVAR_UPDATE;
	case G_CVAR_VARIABLE_STRING_BUFFER: return G_QL_IMPORT_CVAR_VARIABLE_STRING_BUFFER;
	case G_CVAR_SET: return G_QL_IMPORT_CVAR_SET;
	case G_CVAR_REGISTER: return G_QL_IMPORT_CVAR_REGISTER;
	case G_ARGV: return G_QL_IMPORT_ARGV;
	case G_ARGC: return G_QL_IMPORT_ARGC;
	case G_LOCATE_GAME_DATA: return G_QL_IMPORT_LOCATE_GAME_DATA;
	case G_DROP_CLIENT: return G_QL_IMPORT_DROP_CLIENT;
	case G_SEND_SERVER_COMMAND: return G_QL_IMPORT_SEND_SERVER_COMMAND;
	case G_SET_CONFIGSTRING: return G_QL_IMPORT_SET_CONFIGSTRING;
	case G_GET_CONFIGSTRING: return G_QL_IMPORT_GET_CONFIGSTRING;
	case G_GET_USERINFO: return G_QL_IMPORT_GET_USERINFO;
	case G_SET_USERINFO: return G_QL_IMPORT_SET_USERINFO;
	case G_GET_SERVERINFO: return G_QL_IMPORT_GET_SERVERINFO;
	case G_SET_BRUSH_MODEL: return G_QL_IMPORT_SET_BRUSH_MODEL;
	case G_TRACE: return G_QL_IMPORT_TRACE;
	case G_TRACECAPSULE: return G_QL_IMPORT_TRACECAPSULE;
	case G_POINT_CONTENTS: return G_QL_IMPORT_POINT_CONTENTS;
	case G_IN_PVS: return G_QL_IMPORT_IN_PVS;
	case G_ADJUST_AREA_PORTAL_STATE: return G_QL_IMPORT_ADJUST_AREA_PORTAL_STATE;
	case G_UNLINKENTITY: return G_QL_IMPORT_UNLINK_ENTITY;
	case G_LINKENTITY: return G_QL_IMPORT_LINKENTITY;
	case G_ENTITIES_IN_BOX: return G_QL_IMPORT_ENTITIES_IN_BOX;
	case G_BOT_ALLOCATE_CLIENT: return G_QL_IMPORT_BOT_ALLOCATE_CLIENT;
	case G_GET_USERCMD: return G_QL_IMPORT_GET_USERCMD;
	case G_GET_ENTITY_TOKEN: return G_QL_IMPORT_GET_ENTITY_TOKEN;
	case BOTLIB_SETUP: return G_QL_IMPORT_BOTLIB_SETUP;
	case BOTLIB_SHUTDOWN: return G_QL_IMPORT_BOTLIB_SHUTDOWN;
	case BOTLIB_LIBVAR_SET: return G_QL_IMPORT_BOTLIB_LIBVAR_SET;
	case BOTLIB_PC_ADD_GLOBAL_DEFINE: return G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE;
	case BOTLIB_LOAD_MAP: return G_QL_IMPORT_BOTLIB_LOAD_MAP;
	case BOTLIB_GET_SNAPSHOT_ENTITY: return G_QL_IMPORT_BOTLIB_GET_SNAPSHOT_ENTITY;
	case BOTLIB_GET_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE;
	case BOTLIB_USER_COMMAND: return G_QL_IMPORT_BOTLIB_USER_COMMAND;
	case BOTLIB_AAS_BBOX_AREAS: return G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS;
	case BOTLIB_AAS_AREA_INFO: return G_QL_IMPORT_BOTLIB_AAS_AREA_INFO;
	case BOTLIB_AAS_ENTITY_INFO: return G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO;
	case BOTLIB_AAS_INITIALIZED: return G_QL_IMPORT_BOTLIB_AAS_INITIALIZED;
	case BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX: return G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX;
	case BOTLIB_AAS_TIME: return G_QL_IMPORT_BOTLIB_AAS_TIME;
	case BOTLIB_AAS_POINT_AREA_NUM: return G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM;
	case BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX: return G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX;
	case BOTLIB_AAS_TRACE_AREAS: return G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS;
	case BOTLIB_AAS_POINT_CONTENTS: return G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS;
	case BOTLIB_AAS_NEXT_BSP_ENTITY: return G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY;
	case BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY;
	case BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY;
	case BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY;
	case BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY;
	case BOTLIB_AAS_AREA_REACHABILITY: return G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY;
	case BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA: return G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA;
	case BOTLIB_AAS_ENABLE_ROUTING_AREA: return G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA;
	case BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL: return G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL;
	case BOTLIB_AAS_SWIMMING: return G_QL_IMPORT_BOTLIB_AAS_SWIMMING;
	case BOTLIB_AAS_PREDICT_ROUTE: return G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE;
	case BOTLIB_AI_CHARACTERISTIC_BFLOAT: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT;
	case BOTLIB_AI_CHARACTERISTIC_BINTEGER: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BINTEGER;
	case BOTLIB_AI_CHARACTERISTIC_STRING: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING;
	case BOTLIB_AI_ALLOC_CHAT_STATE: return G_QL_IMPORT_BOTLIB_AI_ALLOC_CHAT_STATE;
	case BOTLIB_AI_FREE_CHAT_STATE: return G_QL_IMPORT_BOTLIB_AI_FREE_CHAT_STATE;
	case BOTLIB_AI_QUEUE_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE;
	case BOTLIB_AI_NEXT_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE;
	case BOTLIB_AI_NUM_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_NUM_CONSOLE_MESSAGE;
	case BOTLIB_AI_INITIAL_CHAT: return G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT;
	case BOTLIB_AI_NUM_INITIAL_CHATS: return G_QL_IMPORT_BOTLIB_AI_NUM_INITIAL_CHATS;
	case BOTLIB_AI_ENTER_CHAT: return G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT;
	case BOTLIB_AI_GET_CHAT_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE;
	case BOTLIB_AI_FIND_MATCH: return G_QL_IMPORT_BOTLIB_AI_FIND_MATCH;
	case BOTLIB_AI_MATCH_VARIABLE: return G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE;
	case BOTLIB_AI_UNIFY_WHITE_SPACES: return G_QL_IMPORT_BOTLIB_AI_UNIFY_WHITE_SPACES;
	case BOTLIB_AI_REPLACE_SYNONYMS: return G_QL_IMPORT_BOTLIB_AI_REPLACE_SYNONYMS;
	case BOTLIB_AI_LOAD_CHAT_FILE: return G_QL_IMPORT_BOTLIB_AI_LOAD_CHAT_FILE;
	case BOTLIB_AI_SET_CHAT_GENDER: return G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER;
	case BOTLIB_AI_SET_CHAT_NAME: return G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME;
	case BOTLIB_AI_RESET_GOAL_STATE: return G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE;
	case BOTLIB_AI_REMOVE_FROM_AVOID_GOALS: return G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS;
	case BOTLIB_AI_RESET_AVOID_GOALS: return G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS;
	case BOTLIB_AI_PUSH_GOAL: return G_QL_IMPORT_BOTLIB_AI_PUSH_GOAL;
	case BOTLIB_AI_POP_GOAL: return G_QL_IMPORT_BOTLIB_AI_POP_GOAL;
	case BOTLIB_AI_GOAL_NAME: return G_QL_IMPORT_BOTLIB_AI_GOAL_NAME;
	case BOTLIB_AI_GET_TOP_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL;
	case BOTLIB_AI_GET_SECOND_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL;
	case BOTLIB_AI_CHOOSE_LTG_ITEM: return G_QL_IMPORT_BOTLIB_AI_CHOOSE_LTG_ITEM;
	case BOTLIB_AI_CHOOSE_NBG_ITEM: return G_QL_IMPORT_BOTLIB_AI_CHOOSE_NBG_ITEM;
	case BOTLIB_AI_TOUCHING_GOAL: return G_QL_IMPORT_BOTLIB_AI_TOUCHING_GOAL;
	case BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE: return G_QL_IMPORT_BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE;
	case BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL;
	case BOTLIB_AI_GET_LEVEL_ITEM_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL;
	case BOTLIB_AI_SET_AVOID_GOAL_TIME: return G_QL_IMPORT_BOTLIB_AI_SET_AVOID_GOAL_TIME;
	case BOTLIB_AI_UPDATE_ENTITY_ITEMS: return G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS;
	case BOTLIB_AI_MOVE_TO_GOAL: return G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL;
	case BOTLIB_AI_MOVE_IN_DIRECTION: return G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION;
	case BOTLIB_AI_RESET_AVOID_REACH: return G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH;
	case BOTLIB_AI_RESET_LAST_AVOID_REACH: return G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH;
	case BOTLIB_AI_MOVEMENT_VIEW_TARGET: return G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET;
	case BOTLIB_AI_INIT_MOVE_STATE: return G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE;
	case BOTLIB_AI_ADD_AVOID_SPOT: return G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT;
	case BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON: return G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON;
	case BOTLIB_AI_GET_WEAPON_INFO: return G_QL_IMPORT_BOTLIB_AI_GET_WEAPON_INFO;
	case BOTLIB_AI_LOAD_WEAPON_WEIGHTS: return G_QL_IMPORT_BOTLIB_AI_LOAD_WEAPON_WEIGHTS;
	case BOTLIB_AI_ALLOC_WEAPON_STATE: return G_QL_IMPORT_BOTLIB_AI_ALLOC_WEAPON_STATE;
	case BOTLIB_AI_FREE_WEAPON_STATE: return G_QL_IMPORT_BOTLIB_AI_FREE_WEAPON_STATE;
	case BOTLIB_AI_RESET_WEAPON_STATE: return G_QL_IMPORT_BOTLIB_AI_RESET_WEAPON_STATE;
	case BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION: return G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION;
	case G_STEAMID_QUERY: return G_QL_IMPORT_STEAMID_QUERY;
	case G_STEAM_AUTH_VALIDATE: return G_QL_IMPORT_STEAM_AUTH_VALIDATE;
	default:
		if ( arg >= 0 && arg < GAME_LEGACY_IMPORT_COUNT ) {
			return G_QL_IMPORT_COMPAT_BASE + arg;
		}
		return -1;
	}
}

/*
=================
G_GetMappedImport
=================
*/
static ql_import_f G_GetMappedImport( int arg, const intptr_t *stack ) {
	int importIndex;

	if ( !g_imports ) {
		return NULL;
	}

	importIndex = G_MapNativeImport( arg, stack );
	if ( importIndex < 0 || importIndex >= GAME_NATIVE_IMPORT_COUNT ) {
		return NULL;
	}

	return g_imports[importIndex];
}

/*
=================
G_GetDirectImport
=================
*/
static ql_import_f G_GetDirectImport( int importIndex ) {
	if ( !g_imports ) {
		return NULL;
	}

	if ( importIndex < 0 || importIndex >= GAME_NATIVE_IMPORT_COUNT ) {
		return NULL;
	}

	return g_imports[importIndex];
}

/*
=================
G_NativeImportSyscall
=================
*/
static int QDECL G_NativeImportSyscall( int arg, ... ) {
	const intptr_t *stack;
	ql_import_f import;

	stack = (const intptr_t *)&arg;
	import = G_GetMappedImport( arg, stack );
	if ( !import ) {
		return 0;
	}

	return G_InvokeImport( import, &stack[1] );
}

/*
=================
dllEntry
=================
*/
void dllEntry( void **exports, void *imports, int *apiVersion ) {
	g_imports = (ql_import_f *)imports;
	syscall = G_NativeImportSyscall;

	if ( exports ) {
		*exports = G_GetNativeExportTable();
	}

	if ( apiVersion ) {
		*apiVersion = GAME_NATIVE_API_VERSION;
	}
}

int PASSFLOAT( float x ) {
	float	floatTemp;
	floatTemp = x;
	return *(int *)&floatTemp;
}

void	trap_Printf( const char *fmt ) {
	syscall( G_PRINT, fmt );
}

void	trap_Error( const char *fmt ) {
	syscall( G_ERROR, fmt );
}

int		trap_Milliseconds( void ) {
	return syscall( G_MILLISECONDS ); 
}
int		trap_Argc( void ) {
	return syscall( G_ARGC );
}

void	trap_Argv( int n, char *buffer, int bufferLength ) {
	syscall( G_ARGV, n, buffer, bufferLength );
}

int		trap_FS_FOpenFile( const char *qpath, fileHandle_t *f, fsMode_t mode ) {
	return syscall( G_FS_FOPEN_FILE, qpath, f, mode );
}

void	trap_FS_Read( void *buffer, int len, fileHandle_t f ) {
	syscall( G_FS_READ, buffer, len, f );
}

void	trap_FS_Write( const void *buffer, int len, fileHandle_t f ) {
	syscall( G_FS_WRITE, buffer, len, f );
}

void	trap_FS_FCloseFile( fileHandle_t f ) {
	syscall( G_FS_FCLOSE_FILE, f );
}

int trap_FS_GetFileList(  const char *path, const char *extension, char *listbuf, int bufsize ) {
	return syscall( G_FS_GETFILELIST, path, extension, listbuf, bufsize );
}

int trap_FS_Seek( fileHandle_t f, long offset, int origin ) {
	return syscall( G_FS_SEEK, f, offset, origin );
}

void	trap_SendConsoleCommand( int exec_when, const char *text ) {
	syscall( G_SEND_CONSOLE_COMMAND, exec_when, text );
}

void	trap_Cvar_Register( vmCvar_t *cvar, const char *var_name, const char *value, int flags ) {
	syscall( G_CVAR_REGISTER, cvar, var_name, value, flags );
}

void	trap_Cvar_Update( vmCvar_t *cvar ) {
	syscall( G_CVAR_UPDATE, cvar );
}

void trap_Cvar_Set( const char *var_name, const char *value ) {
	syscall( G_CVAR_SET, var_name, value );
}

int trap_Cvar_VariableIntegerValue( const char *var_name ) {
	return syscall( G_CVAR_VARIABLE_INTEGER_VALUE, var_name );
}

void trap_Cvar_VariableStringBuffer( const char *var_name, char *buffer, int bufsize ) {
	syscall( G_CVAR_VARIABLE_STRING_BUFFER, var_name, buffer, bufsize );
}


void trap_LocateGameData( gentity_t *gEnts, int numGEntities, int sizeofGEntity_t,
						 playerState_t *clients, int sizeofGClient ) {
	syscall( G_LOCATE_GAME_DATA, gEnts, numGEntities, sizeofGEntity_t, clients, sizeofGClient );
}

void trap_DropClient( int clientNum, const char *reason ) {
	syscall( G_DROP_CLIENT, clientNum, reason );
}

void trap_SendServerCommand( int clientNum, const char *text ) {
	syscall( G_SEND_SERVER_COMMAND, clientNum, text );
}

void trap_SetConfigstring( int num, const char *string ) {
	syscall( G_SET_CONFIGSTRING, num, string );
}

void trap_GetConfigstring( int num, char *buffer, int bufferSize ) {
	syscall( G_GET_CONFIGSTRING, num, buffer, bufferSize );
}

void trap_GetUserinfo( int num, char *buffer, int bufferSize ) {
	syscall( G_GET_USERINFO, num, buffer, bufferSize );
}

void trap_SetUserinfo( int num, const char *buffer ) {
	syscall( G_SET_USERINFO, num, buffer );
}

void trap_GetServerinfo( char *buffer, int bufferSize ) {
	syscall( G_GET_SERVERINFO, buffer, bufferSize );
}

/*
=============
trap_GetSteamId

Queries the engine for the client's SteamID split into 32-bit parts.
=============
*/
qboolean trap_GetSteamId( int clientNum, unsigned int *steamIdLow, unsigned int *steamIdHigh ) {
	return syscall( G_STEAMID_QUERY, clientNum, steamIdLow, steamIdHigh ) ? qtrue : qfalse;
}

/*
=============
trap_VerifySteamAuth

Validates the client's Steam authentication state on the server.
=============
*/
qboolean trap_VerifySteamAuth( int clientNum ) {
	return syscall( G_STEAM_AUTH_VALIDATE, clientNum ) ? qtrue : qfalse;
}

/*
=============
trap_SubmitMatchReport

Forwards the retail match-report submission hook through the native import slab.
=============
*/
void trap_SubmitMatchReport( void *report ) {
	ql_import_f import = G_GetDirectImport( G_QL_IMPORT_SUBMIT_MATCH_REPORT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( void * ))import)( report );
}

/*
=============
trap_ReportPlayerEvent

Forwards the retail per-player JSON event publisher through the native import slab.
=============
*/
void trap_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, void *payload ) {
	ql_import_f import = G_GetDirectImport( G_QL_IMPORT_REPORT_PLAYER_EVENT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( uint32_t, uint32_t, const void *, const char *, void * ))import)(
		steamIdLow,
		steamIdHigh,
		clientStats,
		eventName,
		payload
	);
}

/*
=============
trap_AddSteamStat

Forwards the retail additive Steam stat hook through the native import slab.
=============
*/
void trap_AddSteamStat( int clientNum, int statIndex, int delta ) {
	ql_import_f import = G_GetDirectImport( G_QL_IMPORT_STEAM_STAT_ADD );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( int, int, int ))import)( clientNum, statIndex, delta );
}

/*
=============
trap_UnlockSteamAchievement

Forwards the retail fire-and-forget achievement unlock hook.
=============
*/
void trap_UnlockSteamAchievement( int clientNum, int achievementId ) {
	ql_import_f import = G_GetDirectImport( G_QL_IMPORT_STEAM_UNLOCK_ACHIEVEMENT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( int, int ))import)( clientNum, achievementId );
}

/*
=============
trap_HasSteamAchievement

Queries the retail achievement gate before emitting duplicate unlocks.
=============
*/
qboolean trap_HasSteamAchievement( int clientNum, int achievementId ) {
	ql_import_f import = G_GetDirectImport( G_QL_IMPORT_STEAM_HAS_ACHIEVEMENT );

	if ( !import ) {
		return qfalse;
	}

	return ((qboolean (QDECL *)( int, int ))import)( clientNum, achievementId ) ? qtrue : qfalse;
}

/*
=============
trap_RankBegin

Starts a rankings session with the provided game key.
=============
*/
void trap_RankBegin( char *gamekey ) {
	syscall( G_RANK_BEGIN, gamekey );
}

/*
=============
trap_RankPoll

Processes pending ranking work queued by the engine.
=============
*/
void trap_RankPoll( void ) {
	syscall( G_RANK_POLL );
}

/*
=============
trap_RankCheckInit

Checks whether the rankings layer has been initialised.
=============
*/
qboolean trap_RankCheckInit( void ) {
	return syscall( G_RANK_CHECK_INIT ) ? qtrue : qfalse;
}

/*
=============
trap_RankActive

Reports whether rankings are currently active on the server.
=============
*/
qboolean trap_RankActive( void ) {
	return syscall( G_RANK_ACTIVE ) ? qtrue : qfalse;
}

/*
=============
trap_RankUserStatus

Queries the current rankings status for a specific client slot.
=============
*/
int trap_RankUserStatus( int index ) {
	return syscall( G_RANK_USER_STATUS, index );
}

/*
=============
trap_RankUserReset

Clears any rankings state cached for a specific client slot.
=============
*/
void trap_RankUserReset( int index ) {
	syscall( G_RANK_USER_RESET, index );
}

/*
=============
trap_RankReportInt

Submits an integer ranking report for one or two players.
=============
*/
void trap_RankReportInt( int index1, int index2, int key, int value, qboolean accum ) {
	syscall( G_RANK_REPORT_INT, index1, index2, key, value, accum ? qtrue : qfalse );
}

/*
=============
trap_RankReportStr

Submits a string ranking report for one or two players.
=============
*/
void trap_RankReportStr( int index1, int index2, int key, char *value ) {
	syscall( G_RANK_REPORT_STR, index1, index2, key, value );
}

void trap_SetBrushModel( gentity_t *ent, const char *name ) {
	syscall( G_SET_BRUSH_MODEL, ent, name );
}

void trap_Trace( trace_t *results, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, int passEntityNum, int contentmask ) {
	syscall( G_TRACE, results, start, mins, maxs, end, passEntityNum, contentmask );
}

void trap_TraceCapsule( trace_t *results, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, int passEntityNum, int contentmask ) {
	syscall( G_TRACECAPSULE, results, start, mins, maxs, end, passEntityNum, contentmask );
}

int trap_PointContents( const vec3_t point, int passEntityNum ) {
	return syscall( G_POINT_CONTENTS, point, passEntityNum );
}


qboolean trap_InPVS( const vec3_t p1, const vec3_t p2 ) {
	return syscall( G_IN_PVS, p1, p2 ) ? qtrue : qfalse;
}

qboolean trap_InPVSIgnorePortals( const vec3_t p1, const vec3_t p2 ) {
	return syscall( G_IN_PVS_IGNORE_PORTALS, p1, p2 ) ? qtrue : qfalse;
}

void trap_AdjustAreaPortalState( gentity_t *ent, qboolean open ) {
	syscall( G_ADJUST_AREA_PORTAL_STATE, ent, open ? qtrue : qfalse );
}

qboolean trap_AreasConnected( int area1, int area2 ) {
	return syscall( G_AREAS_CONNECTED, area1, area2 ) ? qtrue : qfalse;
}

void trap_LinkEntity( gentity_t *ent ) {
	syscall( G_LINKENTITY, ent );
}

void trap_UnlinkEntity( gentity_t *ent ) {
	syscall( G_UNLINKENTITY, ent );
}

int trap_EntitiesInBox( const vec3_t mins, const vec3_t maxs, int *list, int maxcount ) {
	return syscall( G_ENTITIES_IN_BOX, mins, maxs, list, maxcount );
}

qboolean trap_EntityContact( const vec3_t mins, const vec3_t maxs, const gentity_t *ent ) {
	return syscall( G_ENTITY_CONTACT, mins, maxs, ent ) ? qtrue : qfalse;
}

qboolean trap_EntityContactCapsule( const vec3_t mins, const vec3_t maxs, const gentity_t *ent ) {
	return syscall( G_ENTITY_CONTACTCAPSULE, mins, maxs, ent ) ? qtrue : qfalse;
}

int trap_BotAllocateClient( void ) {
	return syscall( G_BOT_ALLOCATE_CLIENT );
}

void trap_BotFreeClient( int clientNum ) {
	syscall( G_BOT_FREE_CLIENT, clientNum );
}

void trap_GetUsercmd( int clientNum, usercmd_t *cmd ) {
	syscall( G_GET_USERCMD, clientNum, cmd );
}

qboolean trap_GetEntityToken( char *buffer, int bufferSize ) {
	return syscall( G_GET_ENTITY_TOKEN, buffer, bufferSize ) ? qtrue : qfalse;
}

int trap_DebugPolygonCreate(int color, int numPoints, vec3_t *points) {
	return syscall( G_DEBUG_POLYGON_CREATE, color, numPoints, points );
}

void trap_DebugPolygonDelete(int id) {
	syscall( G_DEBUG_POLYGON_DELETE, id );
}

int trap_RealTime( qtime_t *qtime ) {
	return syscall( G_REAL_TIME, qtime );
}

void trap_SnapVector( float *v ) {
	syscall( G_SNAPVECTOR, v );
	return;
}

// BotLib traps start here
int trap_BotLibSetup( void ) {
	return syscall( BOTLIB_SETUP );
}

int trap_BotLibShutdown( void ) {
	return syscall( BOTLIB_SHUTDOWN );
}

int trap_BotLibVarSet(char *var_name, char *value) {
	return syscall( BOTLIB_LIBVAR_SET, var_name, value );
}

int trap_BotLibVarGet(char *var_name, char *value, int size) {
	return syscall( BOTLIB_LIBVAR_GET, var_name, value, size );
}

int trap_BotLibDefine(char *string) {
	return syscall( BOTLIB_PC_ADD_GLOBAL_DEFINE, string );
}

int trap_BotLibStartFrame(float time) {
	return syscall( BOTLIB_START_FRAME, PASSFLOAT( time ) );
}

int trap_BotLibLoadMap(const char *mapname) {
	return syscall( BOTLIB_LOAD_MAP, mapname );
}

int trap_BotLibUpdateEntity(int ent, void /* struct bot_updateentity_s */ *bue) {
	return syscall( BOTLIB_UPDATENTITY, ent, bue );
}

int trap_BotLibTest(int parm0, char *parm1, vec3_t parm2, vec3_t parm3) {
	return syscall( BOTLIB_TEST, parm0, parm1, parm2, parm3 );
}

int trap_BotGetSnapshotEntity( int clientNum, int sequence ) {
	return syscall( BOTLIB_GET_SNAPSHOT_ENTITY, clientNum, sequence );
}

int trap_BotGetServerCommand(int clientNum, char *message, int size) {
	return syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );
}

void trap_BotUserCommand(int clientNum, usercmd_t *ucmd) {
	syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );
}

void trap_AAS_EntityInfo(int entnum, void /* struct aas_entityinfo_s */ *info) {
	syscall( BOTLIB_AAS_ENTITY_INFO, entnum, info );
}

int trap_AAS_Initialized(void) {
	return syscall( BOTLIB_AAS_INITIALIZED );
}

void trap_AAS_PresenceTypeBoundingBox(int presencetype, vec3_t mins, vec3_t maxs) {
	syscall( BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX, presencetype, mins, maxs );
}

float trap_AAS_Time(void) {
	int temp;

	ql_import_f import = G_GetMappedImport( BOTLIB_AAS_TIME, NULL );

	if ( import ) {
		return ((float (QDECL *)( void ))import)();
	}

	temp = syscall( BOTLIB_AAS_TIME );
	return (*(float*)&temp);
}

int trap_AAS_PointAreaNum(vec3_t point) {
	return syscall( BOTLIB_AAS_POINT_AREA_NUM, point );
}

int trap_AAS_PointReachabilityAreaIndex(vec3_t point) {
	return syscall( BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX, point );
}

int trap_AAS_TraceAreas(vec3_t start, vec3_t end, int *areas, vec3_t *points, int maxareas) {
	return syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );
}

int trap_AAS_BBoxAreas(vec3_t absmins, vec3_t absmaxs, int *areas, int maxareas) {
	return syscall( BOTLIB_AAS_BBOX_AREAS, absmins, absmaxs, areas, maxareas );
}

int trap_AAS_AreaInfo( int areanum, void /* struct aas_areainfo_s */ *info ) {
	return syscall( BOTLIB_AAS_AREA_INFO, areanum, info );
}

int trap_AAS_PointContents(vec3_t point) {
	return syscall( BOTLIB_AAS_POINT_CONTENTS, point );
}

int trap_AAS_NextBSPEntity(int ent) {
	return syscall( BOTLIB_AAS_NEXT_BSP_ENTITY, ent );
}

int trap_AAS_ValueForBSPEpairKey(int ent, char *key, char *value, int size) {
	return syscall( BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY, ent, key, value, size );
}

int trap_AAS_VectorForBSPEpairKey(int ent, char *key, vec3_t v) {
	return syscall( BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY, ent, key, v );
}

int trap_AAS_FloatForBSPEpairKey(int ent, char *key, float *value) {
	return syscall( BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY, ent, key, value );
}

int trap_AAS_IntForBSPEpairKey(int ent, char *key, int *value) {
	return syscall( BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY, ent, key, value );
}

int trap_AAS_AreaReachability(int areanum) {
	return syscall( BOTLIB_AAS_AREA_REACHABILITY, areanum );
}

int trap_AAS_AreaTravelTimeToGoalArea(int areanum, vec3_t origin, int goalareanum, int travelflags) {
	return syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );
}

int trap_AAS_EnableRoutingArea( int areanum, int enable ) {
	return syscall( BOTLIB_AAS_ENABLE_ROUTING_AREA, areanum, enable );
}

int trap_AAS_PredictRoute(void /*struct aas_predictroute_s*/ *route, int areanum, vec3_t origin,
							int goalareanum, int travelflags, int maxareas, int maxtime,
							int stopevent, int stopcontents, int stoptfl, int stopareanum) {
	return syscall( BOTLIB_AAS_PREDICT_ROUTE, route, areanum, origin, goalareanum, travelflags, maxareas, maxtime, stopevent, stopcontents, stoptfl, stopareanum );
}

int trap_AAS_AlternativeRouteGoals(vec3_t start, int startareanum, vec3_t goal, int goalareanum, int travelflags,
										void /*struct aas_altroutegoal_s*/ *altroutegoals, int maxaltroutegoals,
										int type) {
	return syscall( BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL, start, startareanum, goal, goalareanum, travelflags, altroutegoals, maxaltroutegoals, type );
}

int trap_AAS_Swimming(vec3_t origin) {
	return syscall( BOTLIB_AAS_SWIMMING, origin );
}

int trap_AAS_PredictClientMovement(void /* struct aas_clientmove_s */ *move, int entnum, vec3_t origin, int presencetype, int onground, vec3_t velocity, vec3_t cmdmove, int cmdframes, int maxframes, float frametime, int stopevent, int stopareanum, int visualize) {
	return syscall( BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT, move, entnum, origin, presencetype, onground, velocity, cmdmove, cmdframes, maxframes, PASSFLOAT(frametime), stopevent, stopareanum, visualize );
}

void trap_EA_Say(int client, char *str) {
	syscall( BOTLIB_EA_SAY, client, str );
}

void trap_EA_SayTeam(int client, char *str) {
	syscall( BOTLIB_EA_SAY_TEAM, client, str );
}

void trap_EA_Command(int client, char *command) {
	syscall( BOTLIB_EA_COMMAND, client, command );
}

void trap_EA_Action(int client, int action) {
	syscall( BOTLIB_EA_ACTION, client, action );
}

void trap_EA_Gesture(int client) {
	syscall( BOTLIB_EA_GESTURE, client );
}

void trap_EA_Talk(int client) {
	syscall( BOTLIB_EA_TALK, client );
}

void trap_EA_Attack(int client) {
	syscall( BOTLIB_EA_ATTACK, client );
}

void trap_EA_Use(int client) {
	syscall( BOTLIB_EA_USE, client );
}

void trap_EA_Respawn(int client) {
	syscall( BOTLIB_EA_RESPAWN, client );
}

void trap_EA_Crouch(int client) {
	syscall( BOTLIB_EA_CROUCH, client );
}

void trap_EA_MoveUp(int client) {
	syscall( BOTLIB_EA_MOVE_UP, client );
}

void trap_EA_MoveDown(int client) {
	syscall( BOTLIB_EA_MOVE_DOWN, client );
}

void trap_EA_MoveForward(int client) {
	syscall( BOTLIB_EA_MOVE_FORWARD, client );
}

void trap_EA_MoveBack(int client) {
	syscall( BOTLIB_EA_MOVE_BACK, client );
}

void trap_EA_MoveLeft(int client) {
	syscall( BOTLIB_EA_MOVE_LEFT, client );
}

void trap_EA_MoveRight(int client) {
	syscall( BOTLIB_EA_MOVE_RIGHT, client );
}

void trap_EA_SelectWeapon(int client, int weapon) {
	syscall( BOTLIB_EA_SELECT_WEAPON, client, weapon );
}

void trap_EA_Jump(int client) {
	syscall( BOTLIB_EA_JUMP, client );
}

void trap_EA_DelayedJump(int client) {
	syscall( BOTLIB_EA_DELAYED_JUMP, client );
}

void trap_EA_Move(int client, vec3_t dir, float speed) {
	syscall( BOTLIB_EA_MOVE, client, dir, PASSFLOAT(speed) );
}

void trap_EA_View(int client, vec3_t viewangles) {
	syscall( BOTLIB_EA_VIEW, client, viewangles );
}

void trap_EA_EndRegular(int client, float thinktime) {
	syscall( BOTLIB_EA_END_REGULAR, client, PASSFLOAT(thinktime) );
}

void trap_EA_GetInput(int client, float thinktime, void /* struct bot_input_s */ *input) {
	syscall( BOTLIB_EA_GET_INPUT, client, PASSFLOAT(thinktime), input );
}

void trap_EA_ResetInput(int client) {
	syscall( BOTLIB_EA_RESET_INPUT, client );
}

int trap_BotLoadCharacter(char *charfile, float skill) {
	return syscall( BOTLIB_AI_LOAD_CHARACTER, charfile, PASSFLOAT(skill));
}

void trap_BotFreeCharacter(int character) {
	syscall( BOTLIB_AI_FREE_CHARACTER, character );
}

float trap_Characteristic_Float(int character, int index) {
	int temp;

	ql_import_f import = G_GetMappedImport( BOTLIB_AI_CHARACTERISTIC_FLOAT, NULL );

	if ( import ) {
		return ((float (QDECL *)( int, int ))import)( character, index );
	}

	temp = syscall( BOTLIB_AI_CHARACTERISTIC_FLOAT, character, index );
	return (*(float*)&temp);
}

float trap_Characteristic_BFloat(int character, int index, float min, float max) {
	int temp;

	ql_import_f import = G_GetMappedImport( BOTLIB_AI_CHARACTERISTIC_BFLOAT, NULL );

	if ( import ) {
		return ((float (QDECL *)( int, int, float, float ))import)( character, index, min, max );
	}

	temp = syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, PASSFLOAT(min), PASSFLOAT(max) );
	return (*(float*)&temp);
}

int trap_Characteristic_Integer(int character, int index) {
	return syscall( BOTLIB_AI_CHARACTERISTIC_INTEGER, character, index );
}

int trap_Characteristic_BInteger(int character, int index, int min, int max) {
	return syscall( BOTLIB_AI_CHARACTERISTIC_BINTEGER, character, index, min, max );
}

void trap_Characteristic_String(int character, int index, char *buf, int size) {
	syscall( BOTLIB_AI_CHARACTERISTIC_STRING, character, index, buf, size );
}

int trap_BotAllocChatState(void) {
	return syscall( BOTLIB_AI_ALLOC_CHAT_STATE );
}

void trap_BotFreeChatState(int handle) {
	syscall( BOTLIB_AI_FREE_CHAT_STATE, handle );
}

void trap_BotQueueConsoleMessage(int chatstate, int type, char *message) {
	syscall( BOTLIB_AI_QUEUE_CONSOLE_MESSAGE, chatstate, type, message );
}

void trap_BotRemoveConsoleMessage(int chatstate, int handle) {
	syscall( BOTLIB_AI_REMOVE_CONSOLE_MESSAGE, chatstate, handle );
}

int trap_BotNextConsoleMessage(int chatstate, void /* struct bot_consolemessage_s */ *cm) {
	return syscall( BOTLIB_AI_NEXT_CONSOLE_MESSAGE, chatstate, cm );
}

int trap_BotNumConsoleMessages(int chatstate) {
	return syscall( BOTLIB_AI_NUM_CONSOLE_MESSAGE, chatstate );
}

void trap_BotInitialChat(int chatstate, char *type, int mcontext, char *var0, char *var1, char *var2, char *var3, char *var4, char *var5, char *var6, char *var7 ) {
	syscall( BOTLIB_AI_INITIAL_CHAT, chatstate, type, mcontext, var0, var1, var2, var3, var4, var5, var6, var7 );
}

int	trap_BotNumInitialChats(int chatstate, char *type) {
	return syscall( BOTLIB_AI_NUM_INITIAL_CHATS, chatstate, type );
}

int trap_BotReplyChat(int chatstate, char *message, int mcontext, int vcontext, char *var0, char *var1, char *var2, char *var3, char *var4, char *var5, char *var6, char *var7 ) {
	return syscall( BOTLIB_AI_REPLY_CHAT, chatstate, message, mcontext, vcontext, var0, var1, var2, var3, var4, var5, var6, var7 );
}

int trap_BotChatLength(int chatstate) {
	return syscall( BOTLIB_AI_CHAT_LENGTH, chatstate );
}

void trap_BotEnterChat(int chatstate, int client, int sendto) {
	syscall( BOTLIB_AI_ENTER_CHAT, chatstate, client, sendto );
}

void trap_BotGetChatMessage(int chatstate, char *buf, int size) {
	syscall( BOTLIB_AI_GET_CHAT_MESSAGE, chatstate, buf, size);
}

int trap_StringContains(char *str1, char *str2, int casesensitive) {
	return syscall( BOTLIB_AI_STRING_CONTAINS, str1, str2, casesensitive );
}

int trap_BotFindMatch(char *str, void /* struct bot_match_s */ *match, unsigned long int context) {
	return syscall( BOTLIB_AI_FIND_MATCH, str, match, context );
}

void trap_BotMatchVariable(void /* struct bot_match_s */ *match, int variable, char *buf, int size) {
	syscall( BOTLIB_AI_MATCH_VARIABLE, match, variable, buf, size );
}

void trap_UnifyWhiteSpaces(char *string) {
	syscall( BOTLIB_AI_UNIFY_WHITE_SPACES, string );
}

void trap_BotReplaceSynonyms(char *string, unsigned long int context) {
	syscall( BOTLIB_AI_REPLACE_SYNONYMS, string, context );
}

int trap_BotLoadChatFile(int chatstate, char *chatfile, char *chatname) {
	return syscall( BOTLIB_AI_LOAD_CHAT_FILE, chatstate, chatfile, chatname );
}

void trap_BotSetChatGender(int chatstate, int gender) {
	syscall( BOTLIB_AI_SET_CHAT_GENDER, chatstate, gender );
}

void trap_BotSetChatName(int chatstate, char *name, int client) {
	syscall( BOTLIB_AI_SET_CHAT_NAME, chatstate, name, client );
}

void trap_BotResetGoalState(int goalstate) {
	syscall( BOTLIB_AI_RESET_GOAL_STATE, goalstate );
}

void trap_BotResetAvoidGoals(int goalstate) {
	syscall( BOTLIB_AI_RESET_AVOID_GOALS, goalstate );
}

void trap_BotRemoveFromAvoidGoals(int goalstate, int number) {
	syscall( BOTLIB_AI_REMOVE_FROM_AVOID_GOALS, goalstate, number);
}

void trap_BotPushGoal(int goalstate, void /* struct bot_goal_s */ *goal) {
	syscall( BOTLIB_AI_PUSH_GOAL, goalstate, goal );
}

void trap_BotPopGoal(int goalstate) {
	syscall( BOTLIB_AI_POP_GOAL, goalstate );
}

void trap_BotEmptyGoalStack(int goalstate) {
	syscall( BOTLIB_AI_EMPTY_GOAL_STACK, goalstate );
}

void trap_BotDumpAvoidGoals(int goalstate) {
	syscall( BOTLIB_AI_DUMP_AVOID_GOALS, goalstate );
}

void trap_BotDumpGoalStack(int goalstate) {
	syscall( BOTLIB_AI_DUMP_GOAL_STACK, goalstate );
}

void trap_BotGoalName(int number, char *name, int size) {
	syscall( BOTLIB_AI_GOAL_NAME, number, name, size );
}

int trap_BotGetTopGoal(int goalstate, void /* struct bot_goal_s */ *goal) {
	return syscall( BOTLIB_AI_GET_TOP_GOAL, goalstate, goal );
}

int trap_BotGetSecondGoal(int goalstate, void /* struct bot_goal_s */ *goal) {
	return syscall( BOTLIB_AI_GET_SECOND_GOAL, goalstate, goal );
}

int trap_BotChooseLTGItem(int goalstate, vec3_t origin, int *inventory, int travelflags) {
	return syscall( BOTLIB_AI_CHOOSE_LTG_ITEM, goalstate, origin, inventory, travelflags );
}

int trap_BotChooseNBGItem(int goalstate, vec3_t origin, int *inventory, int travelflags, void /* struct bot_goal_s */ *ltg, float maxtime) {
	return syscall( BOTLIB_AI_CHOOSE_NBG_ITEM, goalstate, origin, inventory, travelflags, ltg, PASSFLOAT(maxtime) );
}

int trap_BotTouchingGoal(vec3_t origin, void /* struct bot_goal_s */ *goal) {
	return syscall( BOTLIB_AI_TOUCHING_GOAL, origin, goal );
}

int trap_BotItemGoalInVisButNotVisible(int viewer, vec3_t eye, vec3_t viewangles, void /* struct bot_goal_s */ *goal) {
	return syscall( BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE, viewer, eye, viewangles, goal );
}

int trap_BotGetLevelItemGoal(int index, char *classname, void /* struct bot_goal_s */ *goal) {
	return syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );
}

int trap_BotGetNextCampSpotGoal(int num, void /* struct bot_goal_s */ *goal) {
	return syscall( BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL, num, goal );
}

int trap_BotGetMapLocationGoal(char *name, void /* struct bot_goal_s */ *goal) {
	return syscall( BOTLIB_AI_GET_MAP_LOCATION_GOAL, name, goal );
}

float trap_BotAvoidGoalTime(int goalstate, int number) {
	int temp;

	ql_import_f import = G_GetMappedImport( BOTLIB_AI_AVOID_GOAL_TIME, NULL );

	if ( import ) {
		return ((float (QDECL *)( int, int ))import)( goalstate, number );
	}

	temp = syscall( BOTLIB_AI_AVOID_GOAL_TIME, goalstate, number );
	return (*(float*)&temp);
}

void trap_BotSetAvoidGoalTime(int goalstate, int number, float avoidtime) {
	syscall( BOTLIB_AI_SET_AVOID_GOAL_TIME, goalstate, number, PASSFLOAT(avoidtime));
}

void trap_BotInitLevelItems(void) {
	syscall( BOTLIB_AI_INIT_LEVEL_ITEMS );
}

void trap_BotUpdateEntityItems(void) {
	syscall( BOTLIB_AI_UPDATE_ENTITY_ITEMS );
}

int trap_BotLoadItemWeights(int goalstate, char *filename) {
	return syscall( BOTLIB_AI_LOAD_ITEM_WEIGHTS, goalstate, filename );
}

void trap_BotFreeItemWeights(int goalstate) {
	syscall( BOTLIB_AI_FREE_ITEM_WEIGHTS, goalstate );
}

void trap_BotInterbreedGoalFuzzyLogic(int parent1, int parent2, int child) {
	syscall( BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC, parent1, parent2, child );
}

void trap_BotSaveGoalFuzzyLogic(int goalstate, char *filename) {
	syscall( BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC, goalstate, filename );
}

void trap_BotMutateGoalFuzzyLogic(int goalstate, float range) {
	syscall( BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC, goalstate, range );
}

int trap_BotAllocGoalState(int state) {
	return syscall( BOTLIB_AI_ALLOC_GOAL_STATE, state );
}

void trap_BotFreeGoalState(int handle) {
	syscall( BOTLIB_AI_FREE_GOAL_STATE, handle );
}

void trap_BotResetMoveState(int movestate) {
	syscall( BOTLIB_AI_RESET_MOVE_STATE, movestate );
}

void trap_BotAddAvoidSpot(int movestate, vec3_t origin, float radius, int type) {
	syscall( BOTLIB_AI_ADD_AVOID_SPOT, movestate, origin, PASSFLOAT(radius), type);
}

void trap_BotMoveToGoal(void /* struct bot_moveresult_s */ *result, int movestate, void /* struct bot_goal_s */ *goal, int travelflags) {
	syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );
}

int trap_BotMoveInDirection(int movestate, vec3_t dir, float speed, int type) {
	return syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, PASSFLOAT(speed), type );
}

void trap_BotResetAvoidReach(int movestate) {
	syscall( BOTLIB_AI_RESET_AVOID_REACH, movestate );
}

void trap_BotResetLastAvoidReach(int movestate) {
	syscall( BOTLIB_AI_RESET_LAST_AVOID_REACH,movestate  );
}

int trap_BotReachabilityArea(vec3_t origin, int testground) {
	return syscall( BOTLIB_AI_REACHABILITY_AREA, origin, testground );
}

int trap_BotMovementViewTarget(int movestate, void /* struct bot_goal_s */ *goal, int travelflags, float lookahead, vec3_t target) {
	return syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, PASSFLOAT(lookahead), target );
}

int trap_BotPredictVisiblePosition(vec3_t origin, int areanum, void /* struct bot_goal_s */ *goal, int travelflags, vec3_t target) {
	return syscall( BOTLIB_AI_PREDICT_VISIBLE_POSITION, origin, areanum, goal, travelflags, target );
}

int trap_BotAllocMoveState(void) {
	return syscall( BOTLIB_AI_ALLOC_MOVE_STATE );
}

void trap_BotFreeMoveState(int handle) {
	syscall( BOTLIB_AI_FREE_MOVE_STATE, handle );
}

void trap_BotInitMoveState(int handle, void /* struct bot_initmove_s */ *initmove) {
	syscall( BOTLIB_AI_INIT_MOVE_STATE, handle, initmove );
}

int trap_BotChooseBestFightWeapon(int weaponstate, int *inventory) {
	return syscall( BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON, weaponstate, inventory );
}

void trap_BotGetWeaponInfo(int weaponstate, int weapon, void /* struct weaponinfo_s */ *weaponinfo) {
	syscall( BOTLIB_AI_GET_WEAPON_INFO, weaponstate, weapon, weaponinfo );
}

int trap_BotLoadWeaponWeights(int weaponstate, char *filename) {
	return syscall( BOTLIB_AI_LOAD_WEAPON_WEIGHTS, weaponstate, filename );
}

int trap_BotAllocWeaponState(void) {
	return syscall( BOTLIB_AI_ALLOC_WEAPON_STATE );
}

void trap_BotFreeWeaponState(int weaponstate) {
	syscall( BOTLIB_AI_FREE_WEAPON_STATE, weaponstate );
}

void trap_BotResetWeaponState(int weaponstate) {
	syscall( BOTLIB_AI_RESET_WEAPON_STATE, weaponstate );
}

int trap_GeneticParentsAndChildSelection(int numranks, float *ranks, int *parent1, int *parent2, int *child) {
	return syscall( BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION, numranks, ranks, parent1, parent2, child );
}

int trap_PC_LoadSource( const char *filename ) {
	return syscall( BOTLIB_PC_LOAD_SOURCE, filename );
}

int trap_PC_FreeSource( int handle ) {
	return syscall( BOTLIB_PC_FREE_SOURCE, handle );
}

int trap_PC_ReadToken( int handle, pc_token_t *pc_token ) {
	return syscall( BOTLIB_PC_READ_TOKEN, handle, pc_token );
}

int trap_PC_SourceFileAndLine( int handle, char *filename, int *line ) {
	return syscall( BOTLIB_PC_SOURCE_FILE_AND_LINE, handle, filename, line );
}
