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
// cg_syscalls.c -- this file is only included when building a dll
// cg_syscalls.asm is included instead when building a qvm
#ifdef Q3_VM
#error "Do not use in VM build"
#endif

#include "cg_local.h"
#include <stdint.h>

typedef void (QDECL *ql_import_f)( void );
typedef intptr_t (QDECL *ql_import_invoke15_t)(
	intptr_t arg0, intptr_t arg1, intptr_t arg2, intptr_t arg3, intptr_t arg4,
	intptr_t arg5, intptr_t arg6, intptr_t arg7, intptr_t arg8, intptr_t arg9,
	intptr_t arg10, intptr_t arg11, intptr_t arg12, intptr_t arg13, intptr_t arg14
);

static int (QDECL *syscall)( int arg, ... ) = (int (QDECL *)( int, ...))-1;
static ql_import_f *cg_imports = NULL;

void **CG_GetNativeExportTable( void );

/*
=================
CG_InvokeImport
=================
*/
static int QDECL CG_InvokeImport( ql_import_f import, const intptr_t *args ) {
	return (int)((ql_import_invoke15_t)import)(
		args[0], args[1], args[2], args[3], args[4],
		args[5], args[6], args[7], args[8], args[9],
		args[10], args[11], args[12], args[13], args[14]
	);
}

/*
=================
CG_MapNativeImport
=================
*/
static int CG_MapNativeImport( int arg, const intptr_t *stack ) {
	switch ( arg ) {
	case CG_PRINT: return CG_QL_IMPORT_PRINT;
	case CG_ERROR: return CG_QL_IMPORT_ERROR;
	case CG_MILLISECONDS: return CG_QL_IMPORT_MILLISECONDS;
	case CG_CVAR_REGISTER: return CG_QL_IMPORT_CVAR_REGISTER;
	case CG_CVAR_UPDATE: return CG_QL_IMPORT_CVAR_UPDATE;
	case CG_CVAR_SET: return CG_QL_IMPORT_CVAR_SET;
	case CG_CVAR_VARIABLESTRINGBUFFER: return CG_QL_IMPORT_CVAR_VARIABLESTRINGBUFFER;
	case CG_ARGC: return CG_QL_IMPORT_ARGC;
	case CG_ARGV: return CG_QL_IMPORT_ARGV;
	case CG_ARGS: return CG_QL_IMPORT_ARGS;
	case CG_FS_FOPENFILE: return CG_QL_IMPORT_FS_FOPENFILE;
	case CG_FS_READ: return CG_QL_IMPORT_FS_READ;
	case CG_FS_WRITE: return CG_QL_IMPORT_FS_WRITE;
	case CG_FS_FCLOSEFILE: return CG_QL_IMPORT_FS_FCLOSEFILE;
	case CG_SENDCONSOLECOMMAND: return CG_QL_IMPORT_SENDCONSOLECOMMAND;
	case CG_ADDCOMMAND: return CG_QL_IMPORT_ADDCOMMAND;
	case CG_SENDCLIENTCOMMAND: return CG_QL_IMPORT_SENDCLIENTCOMMAND;
	case CG_UPDATESCREEN: return CG_QL_IMPORT_UPDATESCREEN;
	case CG_CM_LOADMAP: return CG_QL_IMPORT_CM_LOADMAP;
	case CG_CM_NUMINLINEMODELS: return CG_QL_IMPORT_CM_NUMINLINEMODELS;
	case CG_CM_INLINEMODEL: return CG_QL_IMPORT_CM_INLINEMODEL;
	case CG_CM_LOADMODEL: return CG_QL_IMPORT_COMPAT_CM_LOADMODEL;
	case CG_CM_TEMPBOXMODEL: return CG_QL_IMPORT_CM_TEMPBOXMODEL;
	case CG_CM_POINTCONTENTS: return CG_QL_IMPORT_CM_POINTCONTENTS;
	case CG_CM_TRANSFORMEDPOINTCONTENTS: return CG_QL_IMPORT_CM_TRANSFORMEDPOINTCONTENTS;
	case CG_CM_BOXTRACE: return CG_QL_IMPORT_CM_BOXTRACE;
	case CG_CM_TRANSFORMEDBOXTRACE: return CG_QL_IMPORT_CM_TRANSFORMEDBOXTRACE;
	case CG_CM_MARKFRAGMENTS: return CG_QL_IMPORT_CM_MARKFRAGMENTS;
	case CG_S_STARTSOUND: return CG_QL_IMPORT_S_STARTSOUND;
	case CG_S_STARTLOCALSOUND: return CG_QL_IMPORT_S_STARTLOCALSOUND;
	case CG_S_CLEARLOOPINGSOUNDS:
		return ( stack && stack[1] ) ? CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL : CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME;
	case CG_S_ADDLOOPINGSOUND: return CG_QL_IMPORT_S_ADDLOOPINGSOUND;
	case CG_S_UPDATEENTITYPOSITION: return CG_QL_IMPORT_S_UPDATEENTITYPOSITION;
	case CG_S_RESPATIALIZE: return CG_QL_IMPORT_S_RESPATIALIZE;
	case CG_S_REGISTERSOUND: return CG_QL_IMPORT_S_REGISTERSOUND;
	case CG_S_STARTBACKGROUNDTRACK: return CG_QL_IMPORT_S_STARTBACKGROUNDTRACK;
	case CG_R_LOADWORLDMAP: return CG_QL_IMPORT_R_LOADWORLDMAP;
	case CG_R_REGISTERMODEL: return CG_QL_IMPORT_R_REGISTERMODEL;
	case CG_R_REGISTERSKIN: return CG_QL_IMPORT_R_REGISTERSKIN;
	case CG_R_REGISTERSHADER: return CG_QL_IMPORT_R_REGISTERSHADER;
	case CG_R_CLEARSCENE: return CG_QL_IMPORT_R_CLEARSCENE;
	case CG_R_ADDREFENTITYTOSCENE: return CG_QL_IMPORT_R_ADDREFENTITYTOSCENE;
	case CG_R_ADDPOLYTOSCENE: return CG_QL_IMPORT_R_ADDPOLYTOSCENE;
	case CG_R_ADDLIGHTTOSCENE: return CG_QL_IMPORT_R_ADDLIGHTTOSCENE;
	case CG_R_RENDERSCENE: return CG_QL_IMPORT_R_RENDERSCENE;
	case CG_R_SETCOLOR: return CG_QL_IMPORT_R_SETCOLOR;
	case CG_R_DRAWSTRETCHPIC: return CG_QL_IMPORT_R_DRAWSTRETCHPIC;
	case CG_R_MODELBOUNDS: return CG_QL_IMPORT_R_MODELBOUNDS;
	case CG_R_LERPTAG: return CG_QL_IMPORT_R_LERPTAG;
	case CG_GETGLCONFIG: return CG_QL_IMPORT_GETGLCONFIG;
	case CG_GETGAMESTATE: return CG_QL_IMPORT_GETGAMESTATE;
	case CG_GETCURRENTSNAPSHOTNUMBER: return CG_QL_IMPORT_GETCURRENTSNAPSHOTNUMBER;
	case CG_GETSNAPSHOT: return CG_QL_IMPORT_GETSNAPSHOT;
	case CG_GETSERVERCOMMAND: return CG_QL_IMPORT_GETSERVERCOMMAND;
	case CG_GETCURRENTCMDNUMBER: return CG_QL_IMPORT_GETCURRENTCMDNUMBER;
	case CG_GETUSERCMD: return CG_QL_IMPORT_GETUSERCMD;
	case CG_SETUSERCMDVALUE: return CG_QL_IMPORT_SETUSERCMDVALUE;
	case CG_R_REGISTERSHADERNOMIP: return CG_QL_IMPORT_R_REGISTERSHADERNOMIP;
	case CG_MEMORY_REMAINING: return CG_QL_IMPORT_MEMORY_REMAINING;
	case CG_R_REGISTERFONT: return CG_QL_IMPORT_R_REGISTERFONT;
	case CG_KEY_ISDOWN: return CG_QL_IMPORT_KEY_ISDOWN;
	case CG_KEY_GETCATCHER: return CG_QL_IMPORT_KEY_GETCATCHER;
	case CG_KEY_SETCATCHER: return CG_QL_IMPORT_KEY_SETCATCHER;
	case CG_KEY_GETKEY: return CG_QL_IMPORT_KEY_GETKEY;
	case CG_PC_ADD_GLOBAL_DEFINE: return CG_QL_IMPORT_COMPAT_PC_ADD_GLOBAL_DEFINE;
	case CG_PC_LOAD_SOURCE: return CG_QL_IMPORT_PC_LOAD_SOURCE;
	case CG_PC_FREE_SOURCE: return CG_QL_IMPORT_PC_FREE_SOURCE;
	case CG_PC_READ_TOKEN: return CG_QL_IMPORT_PC_READ_TOKEN;
	case CG_PC_SOURCE_FILE_AND_LINE: return CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE;
	case CG_S_STOPBACKGROUNDTRACK: return CG_QL_IMPORT_S_STOPBACKGROUNDTRACK;
	case CG_REAL_TIME: return CG_QL_IMPORT_REAL_TIME;
	case CG_SNAPVECTOR: return CG_QL_IMPORT_COMPAT_SNAPVECTOR;
	case CG_REMOVECOMMAND: return CG_QL_IMPORT_REMOVECOMMAND;
	case CG_R_LIGHTFORPOINT: return CG_QL_IMPORT_R_LIGHTFORPOINT;
	case CG_CIN_PLAYCINEMATIC: return CG_QL_IMPORT_CIN_PLAYCINEMATIC;
	case CG_CIN_STOPCINEMATIC: return CG_QL_IMPORT_CIN_STOPCINEMATIC;
	case CG_CIN_RUNCINEMATIC: return CG_QL_IMPORT_CIN_RUNCINEMATIC;
	case CG_CIN_DRAWCINEMATIC: return CG_QL_IMPORT_CIN_DRAWCINEMATIC;
	case CG_CIN_SETEXTENTS: return CG_QL_IMPORT_CIN_SETEXTENTS;
	case CG_R_REMAP_SHADER: return CG_QL_IMPORT_R_REMAP_SHADER;
	case CG_S_ADDREALLOOPINGSOUND: return CG_QL_IMPORT_COMPAT_S_ADDREALLOOPINGSOUND;
	case CG_S_STOPLOOPINGSOUND: return CG_QL_IMPORT_COMPAT_S_STOPLOOPINGSOUND;
	case CG_CM_TEMPCAPSULEMODEL: return CG_QL_IMPORT_CM_TEMPCAPSULEMODEL;
	case CG_CM_CAPSULETRACE: return CG_QL_IMPORT_CM_CAPSULETRACE;
	case CG_CM_TRANSFORMEDCAPSULETRACE: return CG_QL_IMPORT_CM_TRANSFORMEDCAPSULETRACE;
	case CG_R_ADDADDITIVELIGHTTOSCENE: return CG_QL_IMPORT_COMPAT_R_ADDADDITIVELIGHTTOSCENE;
	case CG_GET_ENTITY_TOKEN: return CG_QL_IMPORT_GET_ENTITY_TOKEN;
	case CG_R_ADDPOLYSTOSCENE: return CG_QL_IMPORT_R_ADDPOLYSTOSCENE;
	case CG_R_INPVS: return CG_QL_IMPORT_COMPAT_R_INPVS;
	case CG_FS_SEEK: return CG_QL_IMPORT_FS_SEEK;
	case CG_KEY_KEYNUMTOSTRINGBUF: return CG_QL_IMPORT_KEY_KEYNUMTOSTRINGBUF;
	case CG_KEY_GETBINDINGBUF: return CG_QL_IMPORT_KEY_GETBINDINGBUF;
	case CG_KEY_SETBINDING: return CG_QL_IMPORT_COMPAT_KEY_SETBINDING;
	case CG_KEY_GETOVERSTRIKEMODE: return CG_QL_IMPORT_COMPAT_KEY_GETOVERSTRIKEMODE;
	case CG_KEY_SETOVERSTRIKEMODE: return CG_QL_IMPORT_COMPAT_KEY_SETOVERSTRIKEMODE;
	case CG_CMD_EXECUTETEXT: return CG_QL_IMPORT_COMPAT_CMD_EXECUTETEXT;
	case CG_MEMSET: return CG_QL_IMPORT_COMPAT_MEMSET;
	case CG_MEMCPY: return CG_QL_IMPORT_COMPAT_MEMCPY;
	case CG_STRNCPY: return CG_QL_IMPORT_COMPAT_STRNCPY;
	case CG_SIN: return CG_QL_IMPORT_COMPAT_SIN;
	case CG_COS: return CG_QL_IMPORT_COMPAT_COS;
	case CG_ATAN2: return CG_QL_IMPORT_COMPAT_ATAN2;
	case CG_SQRT: return CG_QL_IMPORT_COMPAT_SQRT;
	case CG_FLOOR: return CG_QL_IMPORT_COMPAT_FLOOR;
	case CG_CEIL: return CG_QL_IMPORT_COMPAT_CEIL;
	case CG_TESTPRINTINT: return CG_QL_IMPORT_COMPAT_TESTPRINTINT;
	case CG_TESTPRINTFLOAT: return CG_QL_IMPORT_COMPAT_TESTPRINTFLOAT;
	case CG_ACOS: return CG_QL_IMPORT_COMPAT_ACOS;
	case CG_ADVERTISEMENTBRIDGE_INITCGAME: return CG_QL_IMPORT_ADVERTISEMENTBRIDGE_INITCGAME;
	case CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME: return CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME;
	case CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS: return CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_LOADING_VIEW_PARAMETERS;
	case CG_ADVERTISEMENTBRIDGE_SETFRAMETIME: return CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SETFRAMETIME;
	default:
		return -1;
	}
}

/*
=================
CG_NativeImportSyscall
=================
*/
static int QDECL CG_NativeImportSyscall( int arg, ... ) {
	const intptr_t *stack;
	ql_import_f import;
	int importIndex;

	if ( !cg_imports ) {
		return 0;
	}

	stack = (const intptr_t *)&arg;
	importIndex = CG_MapNativeImport( arg, stack );
	if ( importIndex < 0 || importIndex >= CGAME_NATIVE_IMPORT_COUNT ) {
		return 0;
	}

	import = cg_imports[importIndex];
	if ( !import ) {
		return 0;
	}

	return CG_InvokeImport( import, &stack[1] );
}

/*
=================
dllEntry
=================
*/
void dllEntry( void **exports, void *imports, int *apiVersion ) {
	cg_imports = (ql_import_f *)imports;
	syscall = CG_NativeImportSyscall;

	if ( exports ) {
		*exports = CG_GetNativeExportTable();
	}

	if ( apiVersion ) {
		*apiVersion = CGAME_NATIVE_API_VERSION;
	}
}


int PASSFLOAT( float x ) {
	float	floatTemp;
	floatTemp = x;
	return *(int *)&floatTemp;
}

void	trap_Print( const char *fmt ) {
	syscall( CG_PRINT, fmt );
}

void	trap_Error( const char *fmt ) {
	syscall( CG_ERROR, fmt );
}

int		trap_Milliseconds( void ) {
	return syscall( CG_MILLISECONDS ); 
}

void	trap_Cvar_Register( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, int flags ) {
	syscall( CG_CVAR_REGISTER, vmCvar, varName, defaultValue, flags );
}

void	trap_Cvar_Update( vmCvar_t *vmCvar ) {
	syscall( CG_CVAR_UPDATE, vmCvar );
}

void	trap_Cvar_Set( const char *var_name, const char *value ) {
	syscall( CG_CVAR_SET, var_name, value );
}

float trap_Cvar_VariableValue( const char *var_name ) {
	char	buffer[MAX_CVAR_VALUE_STRING];

	trap_Cvar_VariableStringBuffer( var_name, buffer, sizeof( buffer ) );
	return atof( buffer );
}

void trap_Cvar_VariableStringBuffer( const char *var_name, char *buffer, int bufsize ) {
	syscall( CG_CVAR_VARIABLESTRINGBUFFER, var_name, buffer, bufsize );
}

int		trap_Argc( void ) {
	return syscall( CG_ARGC );
}

void	trap_Argv( int n, char *buffer, int bufferLength ) {
	syscall( CG_ARGV, n, buffer, bufferLength );
}

void	trap_Args( char *buffer, int bufferLength ) {
	syscall( CG_ARGS, buffer, bufferLength );
}

/*
=================
trap_Cmd_ExecuteText
=================
*/
void trap_Cmd_ExecuteText( int exec_when, const char *text ) {
	syscall( CG_CMD_EXECUTETEXT, exec_when, text );
}

/*
=================
CG_GetNativeImportFunction
=================
*/
static ql_import_f CG_GetNativeImportFunction( int importIndex ) {
	if ( !cg_imports ) {
		return NULL;
	}

	if ( importIndex < 0 || importIndex >= CGAME_NATIVE_IMPORT_COUNT ) {
		return NULL;
	}

	return cg_imports[importIndex];
}

/*
=================
trap_QL_Cvar_RegisterRange
=================
*/
void trap_QL_Cvar_RegisterRange( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, float minimumValue, float maximumValue, int flags ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_CVAR_REGISTER_RANGE );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( vmCvar_t *, const char *, const char *, float, float, int ))import)( vmCvar, varName, defaultValue, minimumValue, maximumValue, flags );
}

/*
=================
trap_QL_Cvar_Reset
=================
*/
void trap_QL_Cvar_Reset( const char *varName ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_CVAR_RESET );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( const char * ))import)( varName );
}

/*
=================
trap_QL_FS_GetFileList
=================
*/
int trap_QL_FS_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_FS_GETFILELIST );

	if ( !import ) {
		return 0;
	}

	return ((int (QDECL *)( const char *, const char *, char *, int ))import)( path, extension, listbuf, bufsize );
}

/*
=================
trap_QL_S_StartSoundVolume
=================
*/
void trap_QL_S_StartSoundVolume( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfx, float volume ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_S_STARTSOUND_VOLUME );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( vec3_t, int, int, sfxHandle_t, float ))import)( origin, entityNum, entchannel, sfx, volume );
}

/*
=================
trap_QL_S_StartLocalSoundVolume
=================
*/
void trap_QL_S_StartLocalSoundVolume( sfxHandle_t sfx, int channelNum, float volume ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( sfxHandle_t, int, float ))import)( sfx, channelNum, volume );
}

/*
=================
trap_QL_SetupAdvertCellShader
=================
*/
qhandle_t trap_QL_SetupAdvertCellShader( const char *defaultContent, const rectDef_t *rect, int cellId ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_SETUP_ADVERT_CELL_SHADER );

	if ( !import ) {
		return 0;
	}

	return ((qhandle_t (QDECL *)( const char *, const rectDef_t *, int ))import)( defaultContent, rect, cellId );
}

/*
=================
trap_QL_RefreshAdvertCellShader
=================
*/
qhandle_t trap_QL_RefreshAdvertCellShader( const char *defaultContent, const rectDef_t *rect, int cellId ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER );

	if ( !import ) {
		return 0;
	}

	return ((qhandle_t (QDECL *)( const char *, const rectDef_t *, int ))import)( defaultContent, rect, cellId );
}

/*
=================
trap_QL_SetActiveAdvert
=================
*/
void trap_QL_SetActiveAdvert( int cellId ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_SET_ACTIVE_ADVERT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( int ))import)( cellId );
}

/*
=================
trap_QL_IsClientMuted
=================
*/
int trap_QL_IsClientMuted( unsigned int identityLow, unsigned int identityHigh ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_IS_CLIENT_MUTED );

	if ( import ) {
		return ((int (QDECL *)( unsigned int, unsigned int ))import)( identityLow, identityHigh );
	}

	return 0;
}

/*
=================
trap_QL_ToggleClientMute
=================
*/
int trap_QL_ToggleClientMute( unsigned int identityLow, unsigned int identityHigh ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_TOGGLE_CLIENT_MUTE );

	if ( import ) {
		return ((int (QDECL *)( unsigned int, unsigned int ))import)( identityLow, identityHigh );
	}

	return 0;
}

/*
=================
trap_QL_UpdateAdvert
=================
*/
void trap_QL_UpdateAdvert( int handleOrToken, int area ) {
	ql_import_f import;

	if ( !cg_imports ) {
		return;
	}

	import = cg_imports[CG_QL_IMPORT_UPDATE_ADVERT];

	if ( import ) {
		((void (QDECL *)( int, int ))import)( handleOrToken, area );
	}
}

/*
=================
trap_QL_AdvertisementBridge_SetMapPath
=================
*/
void trap_QL_AdvertisementBridge_SetMapPath( const char *mapPath ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SET_MAP_PATH );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( const char * ))import)( mapPath );
}

/*
=================
trap_AdvertisementBridge_InitCGame
=================
*/
void trap_AdvertisementBridge_InitCGame( void ) {
	syscall( CG_ADVERTISEMENTBRIDGE_INITCGAME );
}

/*
=================
trap_AdvertisementBridge_ShutdownCGame
=================
*/
void trap_AdvertisementBridge_ShutdownCGame( void ) {
	syscall( CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME );
}

/*
=================
trap_AdvertisementBridge_UpdateLoadingViewParameters
=================
*/
void trap_AdvertisementBridge_UpdateLoadingViewParameters( void ) {
	syscall( CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS );
}

/*
=================
trap_AdvertisementBridge_SetFrameTime
=================
*/
void trap_AdvertisementBridge_SetFrameTime( int frameTime ) {
	syscall( CG_ADVERTISEMENTBRIDGE_SETFRAMETIME, frameTime );
}

/*
=================
trap_QL_AdvertisementBridge_UpdateViewParameters
=================
*/
void trap_QL_AdvertisementBridge_UpdateViewParameters( void ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_VIEW_PARAMETERS );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( void ))import)();
}

/*
=================
trap_QL_AdvertisementBridge_ClearDelay
=================
*/
void trap_QL_AdvertisementBridge_ClearDelay( void ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_ADVERTISEMENTBRIDGE_CLEAR_DELAY );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( void ))import)();
}

/*
=================
trap_QL_TaggedCvarStringBuffer
=================
*/
void trap_QL_TaggedCvarStringBuffer( const char *varName, char *buffer ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( const char *, char * ))import)( varName, buffer );
}

/*
=================
trap_QL_R_MirrorPoint
=================
*/
void trap_QL_R_MirrorPoint( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_R_MIRROR_POINT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( vec3_t, orientation_t *, orientation_t *, vec3_t ))import)( in, surface, camera, out );
}

/*
=================
trap_QL_R_MirrorVector
=================
*/
void trap_QL_R_MirrorVector( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_R_MIRROR_VECTOR );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( vec3_t, orientation_t *, orientation_t *, vec3_t ))import)( in, surface, camera, out );
}

/*
=================
trap_QL_DrawScaledText
=================
*/
void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_DRAW_SCALED_TEXT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( int, int, const char *, int, float, int, float *, int ))import)( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor ? qtrue : qfalse );
}

/*
=================
trap_QL_MeasureText
=================
*/
unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_MEASURE_TEXT );

	if ( !import ) {
		return 0;
	}

	return ((unsigned long long (QDECL *)( const char *, const char *, int, float, int, float * ))import)( text, end, fontHandle, scale, maxX, outLeft );
}

/*
=================
trap_QL_GetAvatarImageHandle
=================
*/
qhandle_t trap_QL_GetAvatarImageHandle( unsigned int identityLow, unsigned int identityHigh ) {
	ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_GET_AVATAR_IMAGE_HANDLE );

	if ( !import ) {
		return 0;
	}

	return ((qhandle_t (QDECL *)( unsigned int, unsigned int ))import)( identityLow, identityHigh );
}

int		trap_FS_FOpenFile( const char *qpath, fileHandle_t *f, fsMode_t mode ) {
	return syscall( CG_FS_FOPENFILE, qpath, f, mode );
}

void	trap_FS_Read( void *buffer, int len, fileHandle_t f ) {
	syscall( CG_FS_READ, buffer, len, f );
}

void	trap_FS_Write( const void *buffer, int len, fileHandle_t f ) {
	syscall( CG_FS_WRITE, buffer, len, f );
}

void	trap_FS_FCloseFile( fileHandle_t f ) {
	syscall( CG_FS_FCLOSEFILE, f );
}

int trap_FS_Seek( fileHandle_t f, long offset, int origin ) {
	return syscall( CG_FS_SEEK, f, offset, origin );
}

void	trap_SendConsoleCommand( const char *text ) {
	syscall( CG_SENDCONSOLECOMMAND, text );
}

void	trap_AddCommand( const char *cmdName ) {
	syscall( CG_ADDCOMMAND, cmdName );
}

void	trap_RemoveCommand( const char *cmdName ) {
	syscall( CG_REMOVECOMMAND, cmdName );
}

void	trap_SendClientCommand( const char *s ) {
	syscall( CG_SENDCLIENTCOMMAND, s );
}

void	trap_UpdateScreen( void ) {
	syscall( CG_UPDATESCREEN );
}

void	trap_CM_LoadMap( const char *mapname ) {
	syscall( CG_CM_LOADMAP, mapname );
}

int		trap_CM_NumInlineModels( void ) {
	return syscall( CG_CM_NUMINLINEMODELS );
}

clipHandle_t trap_CM_InlineModel( int index ) {
	return syscall( CG_CM_INLINEMODEL, index );
}

/*
=================
trap_CM_LoadModel
=================
*/
clipHandle_t trap_CM_LoadModel( const char *name ) {
	return syscall( CG_CM_LOADMODEL, name );
}

clipHandle_t trap_CM_TempBoxModel( const vec3_t mins, const vec3_t maxs ) {
	return syscall( CG_CM_TEMPBOXMODEL, mins, maxs );
}

clipHandle_t trap_CM_TempCapsuleModel( const vec3_t mins, const vec3_t maxs ) {
	return syscall( CG_CM_TEMPCAPSULEMODEL, mins, maxs );
}

int		trap_CM_PointContents( const vec3_t p, clipHandle_t model ) {
	return syscall( CG_CM_POINTCONTENTS, p, model );
}

int		trap_CM_TransformedPointContents( const vec3_t p, clipHandle_t model, const vec3_t origin, const vec3_t angles ) {
	return syscall( CG_CM_TRANSFORMEDPOINTCONTENTS, p, model, origin, angles );
}

void	trap_CM_BoxTrace( trace_t *results, const vec3_t start, const vec3_t end,
						  const vec3_t mins, const vec3_t maxs,
						  clipHandle_t model, int brushmask ) {
	syscall( CG_CM_BOXTRACE, results, start, end, mins, maxs, model, brushmask );
}

void	trap_CM_CapsuleTrace( trace_t *results, const vec3_t start, const vec3_t end,
						  const vec3_t mins, const vec3_t maxs,
						  clipHandle_t model, int brushmask ) {
	syscall( CG_CM_CAPSULETRACE, results, start, end, mins, maxs, model, brushmask );
}

void	trap_CM_TransformedBoxTrace( trace_t *results, const vec3_t start, const vec3_t end,
						  const vec3_t mins, const vec3_t maxs,
						  clipHandle_t model, int brushmask,
						  const vec3_t origin, const vec3_t angles ) {
	syscall( CG_CM_TRANSFORMEDBOXTRACE, results, start, end, mins, maxs, model, brushmask, origin, angles );
}

void	trap_CM_TransformedCapsuleTrace( trace_t *results, const vec3_t start, const vec3_t end,
						  const vec3_t mins, const vec3_t maxs,
						  clipHandle_t model, int brushmask,
						  const vec3_t origin, const vec3_t angles ) {
	syscall( CG_CM_TRANSFORMEDCAPSULETRACE, results, start, end, mins, maxs, model, brushmask, origin, angles );
}

int		trap_CM_MarkFragments( int numPoints, const vec3_t *points, 
				const vec3_t projection,
				int maxPoints, vec3_t pointBuffer,
				int maxFragments, markFragment_t *fragmentBuffer ) {
	return syscall( CG_CM_MARKFRAGMENTS, numPoints, points, projection, maxPoints, pointBuffer, maxFragments, fragmentBuffer );
}

void	trap_S_StartSound( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfx ) {
	syscall( CG_S_STARTSOUND, origin, entityNum, entchannel, sfx );
}

void	trap_S_StartLocalSound( sfxHandle_t sfx, int channelNum ) {
	syscall( CG_S_STARTLOCALSOUND, sfx, channelNum );
}

void	trap_S_ClearLoopingSounds( qboolean killall ) {
	syscall( CG_S_CLEARLOOPINGSOUNDS, killall ? qtrue : qfalse );
}

void	trap_S_AddLoopingSound( int entityNum, const vec3_t origin, const vec3_t velocity, sfxHandle_t sfx ) {
	syscall( CG_S_ADDLOOPINGSOUND, entityNum, origin, velocity, sfx );
}

void	trap_S_AddRealLoopingSound( int entityNum, const vec3_t origin, const vec3_t velocity, sfxHandle_t sfx ) {
	syscall( CG_S_ADDREALLOOPINGSOUND, entityNum, origin, velocity, sfx );
}

void	trap_S_StopLoopingSound( int entityNum ) {
	syscall( CG_S_STOPLOOPINGSOUND, entityNum );
}

void	trap_S_UpdateEntityPosition( int entityNum, const vec3_t origin ) {
	syscall( CG_S_UPDATEENTITYPOSITION, entityNum, origin );
}

void	trap_S_Respatialize( int entityNum, const vec3_t origin, vec3_t axis[3], int inwater ) {
	syscall( CG_S_RESPATIALIZE, entityNum, origin, axis, inwater );
}

sfxHandle_t	trap_S_RegisterSound( const char *sample, qboolean compressed ) {
	return syscall( CG_S_REGISTERSOUND, sample, compressed ? qtrue : qfalse );
}

void	trap_S_StartBackgroundTrack( const char *intro, const char *loop ) {
	syscall( CG_S_STARTBACKGROUNDTRACK, intro, loop );
}

void	trap_R_LoadWorldMap( const char *mapname ) {
	syscall( CG_R_LOADWORLDMAP, mapname );
}

qhandle_t trap_R_RegisterModel( const char *name ) {
	return syscall( CG_R_REGISTERMODEL, name );
}

qhandle_t trap_R_RegisterSkin( const char *name ) {
	return syscall( CG_R_REGISTERSKIN, name );
}

qhandle_t trap_R_RegisterShader( const char *name ) {
	return syscall( CG_R_REGISTERSHADER, name );
}

qhandle_t trap_R_RegisterShaderNoMip( const char *name ) {
	return syscall( CG_R_REGISTERSHADERNOMIP, name );
}

void trap_R_RegisterFont(const char *fontName, int pointSize, fontInfo_t *font) {
	syscall(CG_R_REGISTERFONT, fontName, pointSize, font );
}

void	trap_R_ClearScene( void ) {
	syscall( CG_R_CLEARSCENE );
}

void	trap_R_AddRefEntityToScene( const refEntity_t *re ) {
	syscall( CG_R_ADDREFENTITYTOSCENE, re );
}

void	trap_R_AddPolyToScene( qhandle_t hShader , int numVerts, const polyVert_t *verts ) {
	syscall( CG_R_ADDPOLYTOSCENE, hShader, numVerts, verts );
}

void	trap_R_AddPolysToScene( qhandle_t hShader , int numVerts, const polyVert_t *verts, int num ) {
	syscall( CG_R_ADDPOLYSTOSCENE, hShader, numVerts, verts, num );
}

int		trap_R_LightForPoint( vec3_t point, vec3_t ambientLight, vec3_t directedLight, vec3_t lightDir ) {
	return syscall( CG_R_LIGHTFORPOINT, point, ambientLight, directedLight, lightDir );
}

void	trap_R_AddLightToScene( const vec3_t org, float intensity, float r, float g, float b ) {
	syscall( CG_R_ADDLIGHTTOSCENE, org, PASSFLOAT(intensity), PASSFLOAT(r), PASSFLOAT(g), PASSFLOAT(b) );
}

void	trap_R_AddAdditiveLightToScene( const vec3_t org, float intensity, float r, float g, float b ) {
	syscall( CG_R_ADDADDITIVELIGHTTOSCENE, org, PASSFLOAT(intensity), PASSFLOAT(r), PASSFLOAT(g), PASSFLOAT(b) );
}

void	trap_R_RenderScene( const refdef_t *fd ) {
	syscall( CG_R_RENDERSCENE, fd );
}

void	trap_R_SetColor( const float *rgba ) {
	syscall( CG_R_SETCOLOR, rgba );
}

void	trap_R_DrawStretchPic( float x, float y, float w, float h, 
							   float s1, float t1, float s2, float t2, qhandle_t hShader ) {
	syscall( CG_R_DRAWSTRETCHPIC, PASSFLOAT(x), PASSFLOAT(y), PASSFLOAT(w), PASSFLOAT(h), PASSFLOAT(s1), PASSFLOAT(t1), PASSFLOAT(s2), PASSFLOAT(t2), hShader );
}

void	trap_R_ModelBounds( clipHandle_t model, vec3_t mins, vec3_t maxs ) {
	syscall( CG_R_MODELBOUNDS, model, mins, maxs );
}

int		trap_R_LerpTag( orientation_t *tag, clipHandle_t mod, int startFrame, int endFrame, 
					   float frac, const char *tagName ) {
	return syscall( CG_R_LERPTAG, tag, mod, startFrame, endFrame, PASSFLOAT(frac), tagName );
}

void	trap_R_RemapShader( const char *oldShader, const char *newShader, const char *timeOffset ) {
	syscall( CG_R_REMAP_SHADER, oldShader, newShader, timeOffset );
}

void		trap_GetGlconfig( glconfig_t *glconfig ) {
	syscall( CG_GETGLCONFIG, glconfig );
}

void		trap_GetGameState( gameState_t *gamestate ) {
	syscall( CG_GETGAMESTATE, gamestate );
}

void		trap_GetCurrentSnapshotNumber( int *snapshotNumber, int *serverTime ) {
	syscall( CG_GETCURRENTSNAPSHOTNUMBER, snapshotNumber, serverTime );
}

qboolean	trap_GetSnapshot( int snapshotNumber, snapshot_t *snapshot ) {
	return syscall( CG_GETSNAPSHOT, snapshotNumber, snapshot ) ? qtrue : qfalse;
}

qboolean	trap_GetServerCommand( int serverCommandNumber ) {
	return syscall( CG_GETSERVERCOMMAND, serverCommandNumber ) ? qtrue : qfalse;
}

int			trap_GetCurrentCmdNumber( void ) {
	return syscall( CG_GETCURRENTCMDNUMBER );
}

qboolean	trap_GetUserCmd( int cmdNumber, usercmd_t *ucmd ) {
	return syscall( CG_GETUSERCMD, cmdNumber, ucmd ) ? qtrue : qfalse;
}

void		trap_SetUserCmdValue( int stateValue, int primaryValue, float sensitivityScale, int fov ) {
	syscall( CG_SETUSERCMDVALUE, stateValue, primaryValue, PASSFLOAT(sensitivityScale), fov );
}

void		testPrintInt( char *string, int i ) {
	syscall( CG_TESTPRINTINT, string, i );
}

void		testPrintFloat( char *string, float f ) {
	syscall( CG_TESTPRINTFLOAT, string, PASSFLOAT(f) );
}

int trap_MemoryRemaining( void ) {
	return syscall( CG_MEMORY_REMAINING );
}

qboolean trap_Key_IsDown( int keynum ) {
	return syscall( CG_KEY_ISDOWN, keynum ) ? qtrue : qfalse;
}

int trap_Key_GetCatcher( void ) {
	return syscall( CG_KEY_GETCATCHER );
}

void trap_Key_SetCatcher( int catcher ) {
	syscall( CG_KEY_SETCATCHER, catcher );
}

int trap_Key_GetKey( const char *binding ) {
	return syscall( CG_KEY_GETKEY, binding );
}

void trap_Key_KeynumToStringBuf( int keynum, char *buf, int buflen ) {
	syscall( CG_KEY_KEYNUMTOSTRINGBUF, keynum, buf, buflen );
}

/*
=================
trap_Key_GetBindingBuf
=================
*/
void trap_Key_GetBindingBuf( int keynum, char *buf, int buflen ) {
	syscall( CG_KEY_GETBINDINGBUF, keynum, buf, buflen );
}

/*
=================
trap_Key_SetBinding
=================
*/
void trap_Key_SetBinding( int keynum, const char *binding ) {
	syscall( CG_KEY_SETBINDING, keynum, binding );
}

/*
=================
trap_Key_GetOverstrikeMode
=================
*/
qboolean trap_Key_GetOverstrikeMode( void ) {
	return syscall( CG_KEY_GETOVERSTRIKEMODE ) ? qtrue : qfalse;
}

/*
=================
trap_Key_SetOverstrikeMode
=================
*/
void trap_Key_SetOverstrikeMode( qboolean state ) {
	syscall( CG_KEY_SETOVERSTRIKEMODE, state ? qtrue : qfalse );
}

int trap_PC_AddGlobalDefine( char *define ) {
	return syscall( CG_PC_ADD_GLOBAL_DEFINE, define );
}

int trap_PC_LoadSource( const char *filename ) {
	return syscall( CG_PC_LOAD_SOURCE, filename );
}

int trap_PC_FreeSource( int handle ) {
	return syscall( CG_PC_FREE_SOURCE, handle );
}

int trap_PC_ReadToken( int handle, pc_token_t *pc_token ) {
	return syscall( CG_PC_READ_TOKEN, handle, pc_token );
}

int trap_PC_SourceFileAndLine( int handle, char *filename, int *line ) {
	return syscall( CG_PC_SOURCE_FILE_AND_LINE, handle, filename, line );
}

void	trap_S_StopBackgroundTrack( void ) {
	syscall( CG_S_STOPBACKGROUNDTRACK );
}

int trap_RealTime(qtime_t *qtime) {
	return syscall( CG_REAL_TIME, qtime );
}

void trap_SnapVector( float *v ) {
	syscall( CG_SNAPVECTOR, v );
}

// this returns a handle.  arg0 is the name in the format "idlogo.roq", set arg1 to NULL, alteredstates to qfalse (do not alter gamestate)
int trap_CIN_PlayCinematic( const char *arg0, int xpos, int ypos, int width, int height, int bits) {
  return syscall(CG_CIN_PLAYCINEMATIC, arg0, xpos, ypos, width, height, bits);
}
 
// stops playing the cinematic and ends it.  should always return FMV_EOF
// cinematics must be stopped in reverse order of when they are started
e_status trap_CIN_StopCinematic(int handle) {
  return syscall(CG_CIN_STOPCINEMATIC, handle);
}


// will run a frame of the cinematic but will not draw it.  Will return FMV_EOF if the end of the cinematic has been reached.
e_status trap_CIN_RunCinematic (int handle) {
  return syscall(CG_CIN_RUNCINEMATIC, handle);
}
 

// draws the current frame
void trap_CIN_DrawCinematic (int handle) {
  syscall(CG_CIN_DRAWCINEMATIC, handle);
}
 

// allows you to resize the animation dynamically
void trap_CIN_SetExtents (int handle, int x, int y, int w, int h) {
  syscall(CG_CIN_SETEXTENTS, handle, x, y, w, h);
}

/*
qboolean trap_loadCamera( const char *name ) {
	return syscall( CG_LOADCAMERA, name );
}

void trap_startCamera(int time) {
	syscall(CG_STARTCAMERA, time);
}

qboolean trap_getCameraInfo( int time, vec3_t *origin, vec3_t *angles) {
	return syscall( CG_GETCAMERAINFO, time, origin, angles );
}
*/

qboolean trap_GetEntityToken( char *buffer, int bufferSize ) {
	return syscall( CG_GET_ENTITY_TOKEN, buffer, bufferSize ) ? qtrue : qfalse;
}

qboolean trap_R_inPVS( const vec3_t p1, const vec3_t p2 ) {
	return syscall( CG_R_INPVS, p1, p2 ) ? qtrue : qfalse;
}
