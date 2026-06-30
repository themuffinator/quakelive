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
#include "ui_local.h"
#include <stdint.h>

// this file is only included when building a dll
// syscalls.asm is included instead when building a qvm
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
static ql_import_f *ui_imports = NULL;

void **UI_GetNativeExportTable( void );

/*
=================
UI_MapNativeImport
=================
*/
static int UI_MapNativeImport( int arg ) {
	switch ( arg ) {
	case UI_ERROR: return UI_QL_IMPORT_ERROR;
	case UI_PRINT: return UI_QL_IMPORT_PRINT;
	case UI_MILLISECONDS: return UI_QL_IMPORT_MILLISECONDS;
	case UI_CVAR_SET: return UI_QL_IMPORT_CVAR_SET;
	case UI_CVAR_VARIABLEVALUE: return UI_QL_IMPORT_CVAR_VARIABLE_VALUE;
	case UI_CVAR_VARIABLESTRINGBUFFER: return UI_QL_IMPORT_CVAR_VARIABLE_STRING_BUFFER;
	case UI_CVAR_SETVALUE: return UI_QL_IMPORT_CVAR_SET_VALUE;
	case UI_CVAR_RESET: return UI_QL_IMPORT_CVAR_RESET;
	case UI_CVAR_CREATE: return UI_QL_IMPORT_CVAR_CREATE;
	case UI_CVAR_INFOSTRINGBUFFER: return UI_QL_IMPORT_CVAR_INFOSTRINGBUFFER;
	case UI_ARGC: return UI_QL_IMPORT_ARGC;
	case UI_ARGV: return UI_QL_IMPORT_ARGV;
	case UI_CMD_EXECUTETEXT: return UI_QL_IMPORT_CMD_EXECUTETEXT;
	case UI_FS_FOPENFILE: return UI_QL_IMPORT_FS_FOPENFILE;
	case UI_FS_READ: return UI_QL_IMPORT_FS_READ;
	case UI_FS_WRITE: return UI_QL_IMPORT_FS_WRITE;
	case UI_FS_FCLOSEFILE: return UI_QL_IMPORT_FS_FCLOSEFILE;
	case UI_FS_GETFILELIST: return UI_QL_IMPORT_FS_GETFILELIST;
	case UI_R_REGISTERMODEL: return UI_QL_IMPORT_R_REGISTERMODEL;
	case UI_R_REGISTERSKIN: return UI_QL_IMPORT_R_REGISTERSKIN;
	case UI_R_REGISTERSHADERNOMIP: return UI_QL_IMPORT_R_REGISTERSHADERNOMIP;
	case UI_R_CLEARSCENE: return UI_QL_IMPORT_R_CLEARSCENE;
	case UI_R_ADDREFENTITYTOSCENE: return UI_QL_IMPORT_R_ADDREFENTITYTOSCENE;
	case UI_R_ADDPOLYTOSCENE: return UI_QL_IMPORT_R_ADDPOLYTOSCENE;
	case UI_R_ADDLIGHTTOSCENE: return UI_QL_IMPORT_R_ADDLIGHTTOSCENE;
	case UI_R_RENDERSCENE: return UI_QL_IMPORT_R_RENDERSCENE;
	case UI_R_SETCOLOR: return UI_QL_IMPORT_R_SETCOLOR;
	case UI_R_DRAWSTRETCHPIC: return UI_QL_IMPORT_R_DRAWSTRETCHPIC;
	case UI_UPDATESCREEN: return UI_QL_IMPORT_UPDATESCREEN;
	case UI_CM_LERPTAG: return UI_QL_IMPORT_CM_LERPTAG;
	case UI_CM_LOADMODEL: return UI_QL_IMPORT_CM_LOADMODEL;
	case UI_S_REGISTERSOUND: return UI_QL_IMPORT_S_REGISTERSOUND;
	case UI_S_STARTLOCALSOUND: return UI_QL_IMPORT_S_STARTLOCALSOUND;
	case UI_KEY_KEYNUMTOSTRINGBUF: return UI_QL_IMPORT_KEY_KEYNUMTOSTRINGBUF;
	case UI_KEY_GETBINDINGBUF: return UI_QL_IMPORT_KEY_GETBINDINGBUF;
	case UI_KEY_SETBINDING: return UI_QL_IMPORT_KEY_SETBINDING;
	case UI_KEY_ISDOWN: return UI_QL_IMPORT_KEY_ISDOWN;
	case UI_KEY_GETOVERSTRIKEMODE: return UI_QL_IMPORT_KEY_GETOVERSTRIKEMODE;
	case UI_KEY_SETOVERSTRIKEMODE: return UI_QL_IMPORT_KEY_SETOVERSTRIKEMODE;
	case UI_KEY_CLEARSTATES: return UI_QL_IMPORT_KEY_CLEARSTATES;
	case UI_KEY_GETCATCHER: return UI_QL_IMPORT_KEY_GETCATCHER;
	case UI_KEY_SETCATCHER: return UI_QL_IMPORT_KEY_SETCATCHER;
	case UI_GETCLIPBOARDDATA: return UI_QL_IMPORT_GETCLIPBOARDDATA;
	case UI_GETGLCONFIG: return UI_QL_IMPORT_GETGLCONFIG;
	case UI_GETCLIENTSTATE: return UI_QL_IMPORT_GETCLIENTSTATE;
	case UI_GETCONFIGSTRING: return UI_QL_IMPORT_GETCONFIGSTRING;
	case UI_LAN_GETPINGQUEUECOUNT: return UI_QL_IMPORT_LAN_GETPINGQUEUECOUNT;
	case UI_LAN_CLEARPING: return UI_QL_IMPORT_LAN_CLEARPING;
	case UI_LAN_GETPING: return UI_QL_IMPORT_LAN_GETPING;
	case UI_LAN_GETPINGINFO: return UI_QL_IMPORT_LAN_GETPINGINFO;
	case UI_CVAR_REGISTER: return UI_QL_IMPORT_CVAR_REGISTER;
	case UI_CVAR_UPDATE: return UI_QL_IMPORT_CVAR_UPDATE;
	case UI_MEMORY_REMAINING: return UI_QL_IMPORT_MEMORY_REMAINING;
	case UI_GET_CDKEY: return UI_QL_IMPORT_GET_CDKEY;
	case UI_SET_CDKEY: return UI_QL_IMPORT_SET_CDKEY;
	case UI_R_REGISTERFONT: return UI_QL_IMPORT_R_REGISTERFONT;
	case UI_R_MODELBOUNDS: return UI_QL_IMPORT_R_MODELBOUNDS;
	case UI_PC_ADD_GLOBAL_DEFINE: return UI_QL_IMPORT_PC_ADD_GLOBAL_DEFINE;
	case UI_PC_LOAD_SOURCE: return UI_QL_IMPORT_PC_LOAD_SOURCE;
	case UI_PC_FREE_SOURCE: return UI_QL_IMPORT_PC_FREE_SOURCE;
	case UI_PC_READ_TOKEN: return UI_QL_IMPORT_PC_READ_TOKEN;
	case UI_PC_SOURCE_FILE_AND_LINE: return UI_QL_IMPORT_PC_SOURCE_FILE_AND_LINE;
	case UI_S_STOPBACKGROUNDTRACK: return UI_QL_IMPORT_S_STOPBACKGROUNDTRACK;
	case UI_S_STARTBACKGROUNDTRACK: return UI_QL_IMPORT_S_STARTBACKGROUNDTRACK;
	case UI_REAL_TIME: return UI_QL_IMPORT_REAL_TIME;
	case UI_LAN_GETSERVERCOUNT: return UI_QL_IMPORT_LAN_GETSERVERCOUNT;
	case UI_LAN_GETSERVERADDRESSSTRING: return UI_QL_IMPORT_LAN_GETSERVERADDRESSSTRING;
	case UI_LAN_GETSERVERINFO: return UI_QL_IMPORT_LAN_GETSERVERINFO;
	case UI_LAN_MARKSERVERVISIBLE: return UI_QL_IMPORT_LAN_MARKSERVERVISIBLE;
	case UI_LAN_UPDATEVISIBLEPINGS: return UI_QL_IMPORT_LAN_UPDATEVISIBLEPINGS;
	case UI_LAN_RESETPINGS: return UI_QL_IMPORT_LAN_RESETPINGS;
	case UI_LAN_LOADCACHEDSERVERS: return UI_QL_IMPORT_LAN_LOADCACHEDSERVERS;
	case UI_LAN_SAVECACHEDSERVERS: return UI_QL_IMPORT_LAN_SAVECACHEDSERVERS;
	case UI_LAN_ADDSERVER: return UI_QL_IMPORT_LAN_ADDSERVER;
	case UI_LAN_REMOVESERVER: return UI_QL_IMPORT_LAN_REMOVESERVER;
	case UI_CIN_PLAYCINEMATIC: return UI_QL_IMPORT_CIN_PLAYCINEMATIC;
	case UI_CIN_STOPCINEMATIC: return UI_QL_IMPORT_CIN_STOPCINEMATIC;
	case UI_CIN_RUNCINEMATIC: return UI_QL_IMPORT_CIN_RUNCINEMATIC;
	case UI_CIN_DRAWCINEMATIC: return UI_QL_IMPORT_CIN_DRAWCINEMATIC;
	case UI_CIN_SETEXTENTS: return UI_QL_IMPORT_CIN_SETEXTENTS;
	case UI_R_REMAP_SHADER: return UI_QL_IMPORT_R_REMAP_SHADER;
	case UI_VERIFY_CDKEY: return UI_QL_IMPORT_VERIFY_CDKEY;
	case UI_LAN_SERVERSTATUS: return UI_QL_IMPORT_LAN_SERVERSTATUS;
	case UI_LAN_GETSERVERPING: return UI_QL_IMPORT_LAN_GETSERVERPING;
	case UI_LAN_SERVERISVISIBLE: return UI_QL_IMPORT_LAN_SERVERISVISIBLE;
	case UI_LAN_COMPARESERVERS: return UI_QL_IMPORT_LAN_COMPARESERVERS;
	case UI_FS_SEEK: return UI_QL_IMPORT_FS_SEEK;
	case UI_SET_PBCLSTATUS: return UI_QL_IMPORT_SET_PBCLSTATUS;
	case UI_LAUNCHER_READSCREENSHOT: return UI_QL_IMPORT_LAUNCHER_READSCREENSHOT;
	default:
		return -1;
	}
}

/*
=================
UI_InvokeImport
=================
*/
static int QDECL UI_InvokeImport( ql_import_f import, const intptr_t *args ) {
	return (int)((ql_import_invoke15_t)import)(
		args[0], args[1], args[2], args[3], args[4],
		args[5], args[6], args[7], args[8], args[9],
		args[10], args[11], args[12], args[13], args[14]
	);
}

/*
=================
UI_NativeImportSyscall
=================
*/
static int QDECL UI_NativeImportSyscall( int arg, ... ) {
	const intptr_t *stack;
	ql_import_f import;
	int importIndex;

	if ( !ui_imports ) {
		return 0;
	}

	importIndex = UI_MapNativeImport( arg );
	if ( importIndex < 0 || importIndex >= UI_QL_NATIVE_IMPORT_COUNT ) {
		return 0;
	}

	import = ui_imports[importIndex];
	if ( !import ) {
		return 0;
	}

	stack = (const intptr_t *)&arg;
	return UI_InvokeImport( import, &stack[1] );
}

/*
=================
dllEntry
=================
*/
void dllEntry( void **exports, void *imports, int *apiVersion ) {
	ui_imports = (ql_import_f *)imports;
	syscall = UI_NativeImportSyscall;

	if ( exports ) {
		*exports = UI_GetNativeExportTable();
	}

	if ( apiVersion ) {
		*apiVersion = UI_QL_API_VERSION;
	}
}

int PASSFLOAT( float x ) {
	float	floatTemp;
	floatTemp = x;
	return *(int *)&floatTemp;
}

void trap_Print( const char *string ) {
	syscall( UI_PRINT, string );
}

void trap_Error( const char *string ) {
	syscall( UI_ERROR, string );
}

int trap_Milliseconds( void ) {
	return syscall( UI_MILLISECONDS ); 
}

void trap_Cvar_Register( vmCvar_t *cvar, const char *var_name, const char *value, int flags ) {
	syscall( UI_CVAR_REGISTER, cvar, var_name, value, flags );
}

void trap_Cvar_Update( vmCvar_t *cvar ) {
	syscall( UI_CVAR_UPDATE, cvar );
}

void trap_Cvar_Set( const char *var_name, const char *value ) {
	syscall( UI_CVAR_SET, var_name, value );
}

float trap_Cvar_VariableValue( const char *var_name ) {
	int temp;

	if ( ui_imports && ui_imports[UI_QL_IMPORT_CVAR_VARIABLE_VALUE] ) {
		return ((float (QDECL *)( const char * ))ui_imports[UI_QL_IMPORT_CVAR_VARIABLE_VALUE])( var_name );
	}

	temp = syscall( UI_CVAR_VARIABLEVALUE, var_name );
	return (*(float*)&temp);
}

void trap_Cvar_VariableStringBuffer( const char *var_name, char *buffer, int bufsize ) {
	syscall( UI_CVAR_VARIABLESTRINGBUFFER, var_name, buffer, bufsize );
}

void trap_Cvar_SetValue( const char *var_name, float value ) {
	syscall( UI_CVAR_SETVALUE, var_name, PASSFLOAT( value ) );
}

void trap_Cvar_Reset( const char *name ) {
	syscall( UI_CVAR_RESET, name ); 
}

void trap_Cvar_Create( const char *var_name, const char *var_value, int flags ) {
	syscall( UI_CVAR_CREATE, var_name, var_value, flags );
}

void trap_Cvar_InfoStringBuffer( int bit, char *buffer, int bufsize ) {
	syscall( UI_CVAR_INFOSTRINGBUFFER, bit, buffer, bufsize );
}

int trap_Argc( void ) {
	return syscall( UI_ARGC );
}

void trap_Argv( int n, char *buffer, int bufferLength ) {
	syscall( UI_ARGV, n, buffer, bufferLength );
}

void trap_Cmd_ExecuteText( int exec_when, const char *text ) {
	syscall( UI_CMD_EXECUTETEXT, exec_when, text );
}

int trap_FS_FOpenFile( const char *qpath, fileHandle_t *f, fsMode_t mode ) {
	return syscall( UI_FS_FOPENFILE, qpath, f, mode );
}

void trap_FS_Read( void *buffer, int len, fileHandle_t f ) {
	syscall( UI_FS_READ, buffer, len, f );
}

void trap_FS_Write( const void *buffer, int len, fileHandle_t f ) {
syscall( UI_FS_WRITE, buffer, len, f );
}

void trap_FS_FCloseFile( fileHandle_t f ) {
syscall( UI_FS_FCLOSEFILE, f );
}

/*
=============
trap_Launcher_ReadScreenshot

Read a screenshot file into the provided buffer through the launcher-safe syscall.
=============
*/
int trap_Launcher_ReadScreenshot( const char *requestedName, void *buffer, int bufferSize ) {
	return syscall( UI_LAUNCHER_READSCREENSHOT, requestedName, buffer, bufferSize );
}

int trap_FS_GetFileList(  const char *path, const char *extension, char *listbuf, int bufsize ) {
	return syscall( UI_FS_GETFILELIST, path, extension, listbuf, bufsize );
}

int trap_FS_Seek( fileHandle_t f, long offset, int origin ) {
	return syscall( UI_FS_SEEK, f, offset, origin );
}

qhandle_t trap_R_RegisterModel( const char *name ) {
	return syscall( UI_R_REGISTERMODEL, name );
}

qhandle_t trap_R_RegisterSkin( const char *name ) {
	return syscall( UI_R_REGISTERSKIN, name );
}

void trap_R_RegisterFont(const char *fontName, int pointSize, fontInfo_t *font) {
	syscall( UI_R_REGISTERFONT, fontName, pointSize, font );
}

qhandle_t trap_R_RegisterShaderNoMip( const char *name ) {
	return syscall( UI_R_REGISTERSHADERNOMIP, name );
}

void trap_R_ClearScene( void ) {
	syscall( UI_R_CLEARSCENE );
}

void trap_R_AddRefEntityToScene( const refEntity_t *re ) {
	syscall( UI_R_ADDREFENTITYTOSCENE, re );
}

void trap_R_AddPolyToScene( qhandle_t hShader , int numVerts, const polyVert_t *verts ) {
	syscall( UI_R_ADDPOLYTOSCENE, hShader, numVerts, verts );
}

void trap_R_AddLightToScene( const vec3_t org, float intensity, float r, float g, float b ) {
	syscall( UI_R_ADDLIGHTTOSCENE, org, PASSFLOAT(intensity), PASSFLOAT(r), PASSFLOAT(g), PASSFLOAT(b) );
}

void trap_R_RenderScene( const refdef_t *fd ) {
	syscall( UI_R_RENDERSCENE, fd );
}

void trap_R_SetColor( const float *rgba ) {
	syscall( UI_R_SETCOLOR, rgba );
}

void trap_R_DrawStretchPic( float x, float y, float w, float h, float s1, float t1, float s2, float t2, qhandle_t hShader ) {
	syscall( UI_R_DRAWSTRETCHPIC, PASSFLOAT(x), PASSFLOAT(y), PASSFLOAT(w), PASSFLOAT(h), PASSFLOAT(s1), PASSFLOAT(t1), PASSFLOAT(s2), PASSFLOAT(t2), hShader );
}

void	trap_R_ModelBounds( clipHandle_t model, vec3_t mins, vec3_t maxs ) {
	syscall( UI_R_MODELBOUNDS, model, mins, maxs );
}

void trap_UpdateScreen( void ) {
	syscall( UI_UPDATESCREEN );
}

int trap_CM_LerpTag( orientation_t *tag, clipHandle_t mod, int startFrame, int endFrame, float frac, const char *tagName ) {
	return syscall( UI_CM_LERPTAG, tag, mod, startFrame, endFrame, PASSFLOAT(frac), tagName );
}

void trap_S_StartLocalSound( sfxHandle_t sfx, int channelNum ) {
	syscall( UI_S_STARTLOCALSOUND, sfx, channelNum );
}

sfxHandle_t	trap_S_RegisterSound( const char *sample, qboolean compressed ) {
	return syscall( UI_S_REGISTERSOUND, sample, compressed ? qtrue : qfalse );
}

void trap_Key_KeynumToStringBuf( int keynum, char *buf, int buflen ) {
	syscall( UI_KEY_KEYNUMTOSTRINGBUF, keynum, buf, buflen );
}

void trap_Key_GetBindingBuf( int keynum, char *buf, int buflen ) {
	syscall( UI_KEY_GETBINDINGBUF, keynum, buf, buflen );
}

void trap_Key_SetBinding( int keynum, const char *binding ) {
	syscall( UI_KEY_SETBINDING, keynum, binding );
}

qboolean trap_Key_IsDown( int keynum ) {
	return syscall( UI_KEY_ISDOWN, keynum ) ? qtrue : qfalse;
}

qboolean trap_Key_GetOverstrikeMode( void ) {
	return syscall( UI_KEY_GETOVERSTRIKEMODE ) ? qtrue : qfalse;
}

void trap_Key_SetOverstrikeMode( qboolean state ) {
	syscall( UI_KEY_SETOVERSTRIKEMODE, state ? qtrue : qfalse );
}

void trap_Key_ClearStates( void ) {
	syscall( UI_KEY_CLEARSTATES );
}

int trap_Key_GetCatcher( void ) {
	return syscall( UI_KEY_GETCATCHER );
}

void trap_Key_SetCatcher( int catcher ) {
	syscall( UI_KEY_SETCATCHER, catcher );
}

void trap_GetClipboardData( char *buf, int bufsize ) {
	syscall( UI_GETCLIPBOARDDATA, buf, bufsize );
}

void trap_GetClientState( uiClientState_t *state ) {
	syscall( UI_GETCLIENTSTATE, state );
}

void trap_GetGlconfig( glconfig_t *glconfig ) {
	syscall( UI_GETGLCONFIG, glconfig );
}

int trap_GetConfigString( int index, char* buff, int buffsize ) {
	return syscall( UI_GETCONFIGSTRING, index, buff, buffsize );
}

int	trap_LAN_GetServerCount( int source ) {
	return syscall( UI_LAN_GETSERVERCOUNT, source );
}

void trap_LAN_GetServerAddressString( int source, int n, char *buf, int buflen ) {
	syscall( UI_LAN_GETSERVERADDRESSSTRING, source, n, buf, buflen );
}

void trap_LAN_GetServerInfo( int source, int n, char *buf, int buflen ) {
	syscall( UI_LAN_GETSERVERINFO, source, n, buf, buflen );
}

int trap_LAN_GetServerPing( int source, int n ) {
	return syscall( UI_LAN_GETSERVERPING, source, n );
}

int trap_LAN_GetPingQueueCount( void ) {
	return syscall( UI_LAN_GETPINGQUEUECOUNT );
}

int trap_LAN_ServerStatus( const char *serverAddress, char *serverStatus, int maxLen ) {
	return syscall( UI_LAN_SERVERSTATUS, serverAddress, serverStatus, maxLen );
}

void trap_LAN_SaveCachedServers() {
	syscall( UI_LAN_SAVECACHEDSERVERS );
}

void trap_LAN_LoadCachedServers() {
	syscall( UI_LAN_LOADCACHEDSERVERS );
}

void trap_LAN_ResetPings(int n) {
	syscall( UI_LAN_RESETPINGS, n );
}

void trap_LAN_ClearPing( int n ) {
	syscall( UI_LAN_CLEARPING, n );
}

void trap_LAN_GetPing( int n, char *buf, int buflen, int *pingtime ) {
	syscall( UI_LAN_GETPING, n, buf, buflen, pingtime );
}

void trap_LAN_GetPingInfo( int n, char *buf, int buflen ) {
	syscall( UI_LAN_GETPINGINFO, n, buf, buflen );
}

void trap_LAN_MarkServerVisible( int source, int n, qboolean visible ) {
	syscall( UI_LAN_MARKSERVERVISIBLE, source, n, visible ? qtrue : qfalse );
}

int trap_LAN_ServerIsVisible( int source, int n) {
	return syscall( UI_LAN_SERVERISVISIBLE, source, n );
}

qboolean trap_LAN_UpdateVisiblePings( int source ) {
	return syscall( UI_LAN_UPDATEVISIBLEPINGS, source ) ? qtrue : qfalse;
}

int trap_LAN_AddServer(int source, const char *name, const char *addr) {
	return syscall( UI_LAN_ADDSERVER, source, name, addr );
}

void trap_LAN_RemoveServer(int source, const char *addr) {
	syscall( UI_LAN_REMOVESERVER, source, addr );
}

int trap_LAN_CompareServers( int source, int sortKey, int sortDir, int s1, int s2 ) {
	return syscall( UI_LAN_COMPARESERVERS, source, sortKey, sortDir, s1, s2 );
}

int trap_MemoryRemaining( void ) {
	return syscall( UI_MEMORY_REMAINING );
}

void trap_GetCDKey( char *buf, int buflen ) {
	syscall( UI_GET_CDKEY, buf, buflen );
}

void trap_SetCDKey( char *buf ) {
	syscall( UI_SET_CDKEY, buf );
}

int trap_PC_AddGlobalDefine( char *define ) {
	return syscall( UI_PC_ADD_GLOBAL_DEFINE, define );
}

int trap_PC_LoadSource( const char *filename ) {
	return syscall( UI_PC_LOAD_SOURCE, filename );
}

int trap_PC_FreeSource( int handle ) {
	return syscall( UI_PC_FREE_SOURCE, handle );
}

int trap_PC_ReadToken( int handle, pc_token_t *pc_token ) {
	return syscall( UI_PC_READ_TOKEN, handle, pc_token );
}

int trap_PC_SourceFileAndLine( int handle, char *filename, int *line ) {
	return syscall( UI_PC_SOURCE_FILE_AND_LINE, handle, filename, line );
}

void trap_S_StopBackgroundTrack( void ) {
	syscall( UI_S_STOPBACKGROUNDTRACK );
}

void trap_S_StartBackgroundTrack( const char *intro, const char *loop) {
	syscall( UI_S_STARTBACKGROUNDTRACK, intro, loop );
}

int trap_RealTime(qtime_t *qtime) {
	return syscall( UI_REAL_TIME, qtime );
}

// this returns a handle.  arg0 is the name in the format "idlogo.roq", set arg1 to NULL, alteredstates to qfalse (do not alter gamestate)
int trap_CIN_PlayCinematic( const char *arg0, int xpos, int ypos, int width, int height, int bits) {
  return syscall(UI_CIN_PLAYCINEMATIC, arg0, xpos, ypos, width, height, bits);
}
 
// stops playing the cinematic and ends it.  should always return FMV_EOF
// cinematics must be stopped in reverse order of when they are started
e_status trap_CIN_StopCinematic(int handle) {
  return syscall(UI_CIN_STOPCINEMATIC, handle);
}


// will run a frame of the cinematic but will not draw it.  Will return FMV_EOF if the end of the cinematic has been reached.
e_status trap_CIN_RunCinematic (int handle) {
  return syscall(UI_CIN_RUNCINEMATIC, handle);
}
 

// draws the current frame
void trap_CIN_DrawCinematic (int handle) {
  syscall(UI_CIN_DRAWCINEMATIC, handle);
}
 

// allows you to resize the animation dynamically
void trap_CIN_SetExtents (int handle, int x, int y, int w, int h) {
  syscall(UI_CIN_SETEXTENTS, handle, x, y, w, h);
}


void	trap_R_RemapShader( const char *oldShader, const char *newShader, const char *timeOffset ) {
	syscall( UI_R_REMAP_SHADER, oldShader, newShader, timeOffset );
}

qboolean trap_VerifyCDKey( const char *key, const char *chksum) {
	return syscall( UI_VERIFY_CDKEY, key, chksum ) ? qtrue : qfalse;
}

void trap_SetPbClStatus( int status ) {
	syscall( UI_SET_PBCLSTATUS, status );
}

/*
=================
UI_GetNativeImportFunction
=================
*/
static ql_import_f UI_GetNativeImportFunction( int importIndex ) {
	if ( !ui_imports ) {
		return NULL;
	}

	if ( importIndex < 0 || importIndex >= UI_QL_NATIVE_IMPORT_COUNT ) {
		return NULL;
	}

	return ui_imports[importIndex];
}

/*
=================
trap_QL_InitAdvertisementBridge
=================
*/
void trap_QL_InitAdvertisementBridge( void ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( void ))import)();
}

/*
=================
trap_QL_SetupAdvertCellShader
=================
*/
qhandle_t trap_QL_SetupAdvertCellShader( const char *defaultContent, const rectDef_t *rect, int cellId ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER );

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
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER );

	if ( !import ) {
		return 0;
	}

	return ((qhandle_t (QDECL *)( const char *, const rectDef_t *, int ))import)( defaultContent, rect, cellId );
}

/*
=================
trap_QL_UpdateAdvert
=================
*/
void trap_QL_UpdateAdvert( int handleOrToken, int area ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_UNUSED_83 );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( int, int ))import)( handleOrToken, area );
}

/*
=================
trap_QL_ActivateAdvert
=================
*/
void trap_QL_ActivateAdvert( int cellId ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_ACTIVATE_ADVERT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( int ))import)( cellId );
}

/*
=================
trap_QL_SetCursorPos
=================
*/
qboolean trap_QL_SetCursorPos( int x, int y ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_SET_CURSOR_POS );

	if ( !import ) {
		return qfalse;
	}

	return ((int (QDECL *)( int, int ))import)( x, y ) ? qtrue : qfalse;
}

/*
=================
trap_QL_GetCursorPos
=================
*/
qboolean trap_QL_GetCursorPos( int *x, int *y ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_GET_CURSOR_POS );

	if ( !import ) {
		return qfalse;
	}

	return ((int (QDECL *)( int *, int * ))import)( x, y ) ? qtrue : qfalse;
}

/*
=================
trap_QL_IsSubscribedApp
=================
*/
qboolean trap_QL_IsSubscribedApp( int appId ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_IS_SUBSCRIBED_APP );

	if ( !import ) {
		return qfalse;
	}

	return ((int (QDECL *)( int ))import)( appId ) ? qtrue : qfalse;
}

/*
=================
trap_QL_DrawScaledText
=================
*/
void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int limit, float *maxX, qboolean forceColor ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_DRAW_SCALED_TEXT );

	if ( !import ) {
		return;
	}

	((void (QDECL *)( int, int, const char *, int, float, int, float *, int ))import)( x, y, text, fontHandle, scale, limit, maxX, forceColor ? qtrue : qfalse );
}

/*
=================
trap_QL_MeasureText
=================
*/
unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int limit, float *outLeft ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_MEASURE_TEXT );

	if ( !import ) {
		return 0;
	}

	return ((unsigned long long (QDECL *)( const char *, const char *, int, float, int, float * ))import)( text, end, fontHandle, scale, limit, outLeft );
}

/*
=================
trap_QL_GetItemDownloadInfo
=================
*/
void trap_QL_GetItemDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal ) {
	ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO );

	if ( !import ) {
		if ( outDownloaded ) {
			*outDownloaded = 0;
		}
		if ( outTotal ) {
			*outTotal = 0;
		}
		return;
	}

	((void (QDECL *)( unsigned int, unsigned int, unsigned long long *, unsigned long long * ))import)( itemIdLow, itemIdHigh, outDownloaded, outTotal );
}
