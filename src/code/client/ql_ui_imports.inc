// Auto-generated ui import wrappers for Quake Live native DLLs.
// Generated from ui_syscalls.c; do not edit manually.

/*
==============
QL_UI_PASSFLOAT
==============
*/
static int QDECL QL_UI_PASSFLOAT( float x ) {
	float	floatTemp;
	floatTemp = x;
	return *(int *)&floatTemp;
}

/*
==============
QL_UI_trap_Print
==============
*/
static void QDECL QL_UI_trap_Print( const char *string ) {
	UI_Import_Syscall( UI_PRINT, string );
}

/*
==============
QL_UI_trap_Error
==============
*/
static void QDECL QL_UI_trap_Error( const char *string ) {
	UI_Import_Syscall( UI_ERROR, string );
}

/*
==============
QL_UI_trap_Milliseconds
==============
*/
static int QDECL QL_UI_trap_Milliseconds( void ) {
	return UI_Import_Syscall( UI_MILLISECONDS );
}

/*
==============
QL_UI_trap_Cvar_Register
==============
*/
static void QDECL QL_UI_trap_Cvar_Register( vmCvar_t *cvar, const char *var_name, const char *value, int flags ) {
	UI_Import_Syscall( UI_CVAR_REGISTER, cvar, var_name, value, flags );
}

/*
==============
QL_UI_trap_Cvar_Update
==============
*/
static void QDECL QL_UI_trap_Cvar_Update( vmCvar_t *cvar ) {
	UI_Import_Syscall( UI_CVAR_UPDATE, cvar );
}

/*
==============
QL_UI_trap_Cvar_Set
==============
*/
static void QDECL QL_UI_trap_Cvar_Set( const char *var_name, const char *value ) {
	UI_Import_Syscall( UI_CVAR_SET, var_name, value );
}

/*
==============
QL_UI_trap_Cvar_VariableValue
==============
*/
static float QDECL QL_UI_trap_Cvar_VariableValue( const char *var_name ) {
	int temp;
	temp = UI_Import_Syscall( UI_CVAR_VARIABLEVALUE, var_name );
	return (*(float*)&temp);
}

/*
==============
QL_UI_trap_Cvar_VariableStringBuffer
==============
*/
static void QDECL QL_UI_trap_Cvar_VariableStringBuffer( const char *var_name, char *buffer, int bufsize ) {
	UI_Import_Syscall( UI_CVAR_VARIABLESTRINGBUFFER, var_name, buffer, bufsize );
}

/*
==============
QL_UI_trap_Cvar_SetValue
==============
*/
static void QDECL QL_UI_trap_Cvar_SetValue( const char *var_name, float value ) {
	UI_Import_Syscall( UI_CVAR_SETVALUE, var_name, QL_UI_PASSFLOAT( value ) );
}

/*
==============
QL_UI_trap_Cvar_Reset
==============
*/
static void QDECL QL_UI_trap_Cvar_Reset( const char *name ) {
	UI_Import_Syscall( UI_CVAR_RESET, name );
}

/*
==============
QL_UI_trap_Cvar_Create
==============
*/
static void QDECL QL_UI_trap_Cvar_Create( const char *var_name, const char *var_value, int flags ) {
	UI_Import_Syscall( UI_CVAR_CREATE, var_name, var_value, flags );
}

/*
==============
QL_UI_trap_Cvar_InfoStringBuffer
==============
*/
static void QDECL QL_UI_trap_Cvar_InfoStringBuffer( int bit, char *buffer, int bufsize ) {
	UI_Import_Syscall( UI_CVAR_INFOSTRINGBUFFER, bit, buffer, bufsize );
}

/*
==============
QL_UI_trap_Argc
==============
*/
static int QDECL QL_UI_trap_Argc( void ) {
	return UI_Import_Syscall( UI_ARGC );
}

/*
==============
QL_UI_trap_Argv
==============
*/
static void QDECL QL_UI_trap_Argv( int n, char *buffer, int bufferLength ) {
	UI_Import_Syscall( UI_ARGV, n, buffer, bufferLength );
}

/*
==============
QL_UI_trap_Cmd_ExecuteText
==============
*/
static void QDECL QL_UI_trap_Cmd_ExecuteText( int exec_when, const char *text ) {
	UI_Import_Syscall( UI_CMD_EXECUTETEXT, exec_when, text );
}

/*
==============
QL_UI_trap_FS_FOpenFile
==============
*/
static int QDECL QL_UI_trap_FS_FOpenFile( const char *qpath, fileHandle_t *f, fsMode_t mode ) {
	return UI_Import_Syscall( UI_FS_FOPENFILE, qpath, f, mode );
}

/*
==============
QL_UI_trap_FS_Read
==============
*/
static void QDECL QL_UI_trap_FS_Read( void *buffer, int len, fileHandle_t f ) {
	UI_Import_Syscall( UI_FS_READ, buffer, len, f );
}

/*
==============
QL_UI_trap_FS_Write
==============
*/
static void QDECL QL_UI_trap_FS_Write( const void *buffer, int len, fileHandle_t f ) {
	UI_Import_Syscall( UI_FS_WRITE, buffer, len, f );
}

/*
==============
QL_UI_trap_FS_FCloseFile
==============
*/
static void QDECL QL_UI_trap_FS_FCloseFile( fileHandle_t f ) {
	UI_Import_Syscall( UI_FS_FCLOSEFILE, f );
}

/*
==============
QL_UI_trap_Launcher_ReadScreenshot
==============
*/
static int QDECL QL_UI_trap_Launcher_ReadScreenshot( const char *requestedName, void *buffer, int bufferSize ) {
	return UI_Import_Syscall( UI_LAUNCHER_READSCREENSHOT, requestedName, buffer, bufferSize );
}

/*
==============
QL_UI_trap_FS_GetFileList
==============
*/
static int QDECL QL_UI_trap_FS_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {
	return UI_Import_Syscall( UI_FS_GETFILELIST, path, extension, listbuf, bufsize );
}

/*
==============
QL_UI_trap_FS_Seek
==============
*/
static int QDECL QL_UI_trap_FS_Seek( fileHandle_t f, long offset, int origin ) {
	return UI_Import_Syscall( UI_FS_SEEK, f, offset, origin );
}

/*
==============
QL_UI_trap_R_RegisterModel
==============
*/
static qhandle_t QDECL QL_UI_trap_R_RegisterModel( const char *name ) {
	return UI_Import_Syscall( UI_R_REGISTERMODEL, name );
}

/*
==============
QL_UI_trap_R_RegisterSkin
==============
*/
static qhandle_t QDECL QL_UI_trap_R_RegisterSkin( const char *name ) {
	return UI_Import_Syscall( UI_R_REGISTERSKIN, name );
}

/*
==============
QL_UI_trap_R_RegisterFont
==============
*/
static void QDECL QL_UI_trap_R_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {
	UI_Import_Syscall( UI_R_REGISTERFONT, fontName, pointSize, font );
}

/*
==============
QL_UI_trap_R_RegisterShaderNoMip
==============
*/
static qhandle_t QDECL QL_UI_trap_R_RegisterShaderNoMip( const char *name ) {
	return UI_Import_Syscall( UI_R_REGISTERSHADERNOMIP, name );
}

/*
==============
QL_UI_trap_R_ClearScene
==============
*/
static void QDECL QL_UI_trap_R_ClearScene( void ) {
	UI_Import_Syscall( UI_R_CLEARSCENE );
}

/*
==============
QL_UI_trap_R_AddRefEntityToScene
==============
*/
static void QDECL QL_UI_trap_R_AddRefEntityToScene( const refEntity_t *re ) {
	UI_Import_Syscall( UI_R_ADDREFENTITYTOSCENE, re );
}

/*
==============
QL_UI_trap_R_AddPolyToScene
==============
*/
static void QDECL QL_UI_trap_R_AddPolyToScene( qhandle_t hShader , int numVerts, const polyVert_t *verts ) {
	UI_Import_Syscall( UI_R_ADDPOLYTOSCENE, hShader, numVerts, verts );
}

/*
==============
QL_UI_trap_R_AddLightToScene
==============
*/
static void QDECL QL_UI_trap_R_AddLightToScene( const vec3_t org, float intensity, float r, float g, float b ) {
	UI_Import_Syscall( UI_R_ADDLIGHTTOSCENE, org, QL_UI_PASSFLOAT(intensity), QL_UI_PASSFLOAT(r), QL_UI_PASSFLOAT(g), QL_UI_PASSFLOAT(b) );
}

/*
==============
QL_UI_trap_R_RenderScene
==============
*/
static void QDECL QL_UI_trap_R_RenderScene( const refdef_t *fd ) {
	UI_Import_Syscall( UI_R_RENDERSCENE, fd );
}

/*
==============
QL_UI_trap_R_SetColor
==============
*/
static void QDECL QL_UI_trap_R_SetColor( const float *rgba ) {
	UI_Import_Syscall( UI_R_SETCOLOR, rgba );
}

/*
==============
QL_UI_trap_R_DrawStretchPic
==============
*/
static void QDECL QL_UI_trap_R_DrawStretchPic( float x, float y, float w, float h, float s1, float t1, float s2, float t2, qhandle_t hShader ) {
	UI_Import_Syscall( UI_R_DRAWSTRETCHPIC, QL_UI_PASSFLOAT(x), QL_UI_PASSFLOAT(y), QL_UI_PASSFLOAT(w), QL_UI_PASSFLOAT(h), QL_UI_PASSFLOAT(s1), QL_UI_PASSFLOAT(t1), QL_UI_PASSFLOAT(s2), QL_UI_PASSFLOAT(t2), hShader );
}

/*
==============
QL_UI_trap_R_ModelBounds
==============
*/
static void QDECL QL_UI_trap_R_ModelBounds( clipHandle_t model, vec3_t mins, vec3_t maxs ) {
	UI_Import_Syscall( UI_R_MODELBOUNDS, model, mins, maxs );
}

/*
==============
QL_UI_trap_UpdateScreen
==============
*/
static void QDECL QL_UI_trap_UpdateScreen( void ) {
	UI_Import_Syscall( UI_UPDATESCREEN );
}

/*
==============
QL_UI_trap_CM_LerpTag
==============
*/
static int QDECL QL_UI_trap_CM_LerpTag( orientation_t *tag, clipHandle_t mod, int startFrame, int endFrame, float frac, const char *tagName ) {
	return UI_Import_Syscall( UI_CM_LERPTAG, tag, mod, startFrame, endFrame, QL_UI_PASSFLOAT(frac), tagName );
}

/*
==============
QL_UI_trap_S_StartLocalSound
==============
*/
static void QDECL QL_UI_trap_S_StartLocalSound( sfxHandle_t sfx, int channelNum ) {
	UI_Import_Syscall( UI_S_STARTLOCALSOUND, sfx, channelNum );
}

/*
==============
QL_UI_trap_S_RegisterSound
==============
*/
static sfxHandle_t QDECL QL_UI_trap_S_RegisterSound( const char *sample, qboolean compressed ) {
	return UI_Import_Syscall( UI_S_REGISTERSOUND, sample, compressed );
}

/*
==============
QL_UI_trap_Key_KeynumToStringBuf
==============
*/
static void QDECL QL_UI_trap_Key_KeynumToStringBuf( int keynum, char *buf, int buflen ) {
	UI_Import_Syscall( UI_KEY_KEYNUMTOSTRINGBUF, keynum, buf, buflen );
}

/*
==============
QL_UI_trap_Key_GetBindingBuf
==============
*/
static void QDECL QL_UI_trap_Key_GetBindingBuf( int keynum, char *buf, int buflen ) {
	UI_Import_Syscall( UI_KEY_GETBINDINGBUF, keynum, buf, buflen );
}

/*
==============
QL_UI_trap_Key_SetBinding
==============
*/
static void QDECL QL_UI_trap_Key_SetBinding( int keynum, const char *binding ) {
	UI_Import_Syscall( UI_KEY_SETBINDING, keynum, binding );
}

/*
==============
QL_UI_trap_Key_IsDown
==============
*/
static qboolean QDECL QL_UI_trap_Key_IsDown( int keynum ) {
	return UI_Import_Syscall( UI_KEY_ISDOWN, keynum );
}

/*
==============
QL_UI_trap_Key_GetOverstrikeMode
==============
*/
static qboolean QDECL QL_UI_trap_Key_GetOverstrikeMode( void ) {
	return UI_Import_Syscall( UI_KEY_GETOVERSTRIKEMODE );
}

/*
==============
QL_UI_trap_Key_SetOverstrikeMode
==============
*/
static void QDECL QL_UI_trap_Key_SetOverstrikeMode( qboolean state ) {
	UI_Import_Syscall( UI_KEY_SETOVERSTRIKEMODE, state );
}

/*
==============
QL_UI_trap_Key_ClearStates
==============
*/
static void QDECL QL_UI_trap_Key_ClearStates( void ) {
	UI_Import_Syscall( UI_KEY_CLEARSTATES );
}

/*
==============
QL_UI_trap_Key_GetCatcher
==============
*/
static int QDECL QL_UI_trap_Key_GetCatcher( void ) {
	return UI_Import_Syscall( UI_KEY_GETCATCHER );
}

/*
==============
QL_UI_trap_Key_SetCatcher
==============
*/
static void QDECL QL_UI_trap_Key_SetCatcher( int catcher ) {
	UI_Import_Syscall( UI_KEY_SETCATCHER, catcher );
}

/*
==============
QL_UI_trap_GetClipboardData
==============
*/
static void QDECL QL_UI_trap_GetClipboardData( char *buf, int bufsize ) {
	UI_Import_Syscall( UI_GETCLIPBOARDDATA, buf, bufsize );
}

/*
==============
QL_UI_trap_GetClientState
==============
*/
static void QDECL QL_UI_trap_GetClientState( uiClientState_t *state ) {
	UI_Import_Syscall( UI_GETCLIENTSTATE, state );
}

/*
==============
QL_UI_trap_GetGlconfig
==============
*/
static void QDECL QL_UI_trap_GetGlconfig( glconfig_t *glconfig ) {
	UI_Import_Syscall( UI_GETGLCONFIG, glconfig );
}

/*
==============
QL_UI_trap_GetConfigString
==============
*/
static int QDECL QL_UI_trap_GetConfigString( int index, char* buff, int buffsize ) {
	return UI_Import_Syscall( UI_GETCONFIGSTRING, index, buff, buffsize );
}

/*
==============
QL_UI_trap_LAN_GetServerCount
==============
*/
static int QDECL QL_UI_trap_LAN_GetServerCount( int source ) {
	return UI_Import_Syscall( UI_LAN_GETSERVERCOUNT, source );
}

/*
==============
QL_UI_trap_LAN_GetServerAddressString
==============
*/
static void QDECL QL_UI_trap_LAN_GetServerAddressString( int source, int n, char *buf, int buflen ) {
	UI_Import_Syscall( UI_LAN_GETSERVERADDRESSSTRING, source, n, buf, buflen );
}

/*
==============
QL_UI_trap_LAN_GetServerInfo
==============
*/
static void QDECL QL_UI_trap_LAN_GetServerInfo( int source, int n, char *buf, int buflen ) {
	UI_Import_Syscall( UI_LAN_GETSERVERINFO, source, n, buf, buflen );
}

/*
==============
QL_UI_trap_LAN_GetServerPing
==============
*/
static int QDECL QL_UI_trap_LAN_GetServerPing( int source, int n ) {
	return UI_Import_Syscall( UI_LAN_GETSERVERPING, source, n );
}

/*
==============
QL_UI_trap_LAN_GetPingQueueCount
==============
*/
static int QDECL QL_UI_trap_LAN_GetPingQueueCount( void ) {
	return UI_Import_Syscall( UI_LAN_GETPINGQUEUECOUNT );
}

/*
==============
QL_UI_trap_LAN_ServerStatus
==============
*/
static int QDECL QL_UI_trap_LAN_ServerStatus( const char *serverAddress, char *serverStatus, int maxLen ) {
	return UI_Import_Syscall( UI_LAN_SERVERSTATUS, serverAddress, serverStatus, maxLen );
}

/*
==============
QL_UI_trap_LAN_SaveCachedServers
==============
*/
static void QDECL QL_UI_trap_LAN_SaveCachedServers(  ) {
	/* Retail native import slot is a no-op. */
}

/*
==============
QL_UI_trap_LAN_LoadCachedServers
==============
*/
static void QDECL QL_UI_trap_LAN_LoadCachedServers(  ) {
	/* Retail native import slot is a no-op. */
}

/*
==============
QL_UI_trap_LAN_ResetPings
==============
*/
static void QDECL QL_UI_trap_LAN_ResetPings( int n ) {
	UI_Import_Syscall( UI_LAN_RESETPINGS, n );
}

/*
==============
QL_UI_trap_LAN_ClearPing
==============
*/
static void QDECL QL_UI_trap_LAN_ClearPing( int n ) {
	UI_Import_Syscall( UI_LAN_CLEARPING, n );
}

/*
==============
QL_UI_trap_LAN_GetPing
==============
*/
static void QDECL QL_UI_trap_LAN_GetPing( int n, char *buf, int buflen, int *pingtime ) {
	UI_Import_Syscall( UI_LAN_GETPING, n, buf, buflen, pingtime );
}

/*
==============
QL_UI_trap_LAN_GetPingInfo
==============
*/
static void QDECL QL_UI_trap_LAN_GetPingInfo( int n, char *buf, int buflen ) {
	UI_Import_Syscall( UI_LAN_GETPINGINFO, n, buf, buflen );
}

/*
==============
QL_UI_trap_LAN_MarkServerVisible
==============
*/
static void QDECL QL_UI_trap_LAN_MarkServerVisible( int source, int n, qboolean visible ) {
	UI_Import_Syscall( UI_LAN_MARKSERVERVISIBLE, source, n, visible );
}

/*
==============
QL_UI_trap_LAN_ServerIsVisible
==============
*/
static int QDECL QL_UI_trap_LAN_ServerIsVisible( int source, int n ) {
	return UI_Import_Syscall( UI_LAN_SERVERISVISIBLE, source, n );
}

/*
==============
QL_UI_trap_LAN_UpdateVisiblePings
==============
*/
static qboolean QDECL QL_UI_trap_LAN_UpdateVisiblePings( int source ) {
	return UI_Import_Syscall( UI_LAN_UPDATEVISIBLEPINGS, source );
}

/*
==============
QL_UI_trap_LAN_AddServer
==============
*/
static int QDECL QL_UI_trap_LAN_AddServer( int source, const char *name, const char *addr ) {
	return UI_Import_Syscall( UI_LAN_ADDSERVER, source, name, addr );
}

/*
==============
QL_UI_trap_LAN_RemoveServer
==============
*/
static void QDECL QL_UI_trap_LAN_RemoveServer( int source, const char *addr ) {
	UI_Import_Syscall( UI_LAN_REMOVESERVER, source, addr );
}

/*
==============
QL_UI_trap_LAN_CompareServers
==============
*/
static int QDECL QL_UI_trap_LAN_CompareServers( int source, int sortKey, int sortDir, int s1, int s2 ) {
	return UI_Import_Syscall( UI_LAN_COMPARESERVERS, source, sortKey, sortDir, s1, s2 );
}

/*
==============
QL_UI_trap_MemoryRemaining
==============
*/
static int QDECL QL_UI_trap_MemoryRemaining( void ) {
	return UI_Import_Syscall( UI_MEMORY_REMAINING );
}

/*
==============
QL_UI_trap_GetCDKey
==============
*/
static void QDECL QL_UI_trap_GetCDKey( char *buf, int buflen ) {
	UI_Import_Syscall( UI_GET_CDKEY, buf, buflen );
}

/*
==============
QL_UI_trap_SetCDKey
==============
*/
static void QDECL QL_UI_trap_SetCDKey( char *buf ) {
	UI_Import_Syscall( UI_SET_CDKEY, buf );
}

/*
==============
QL_UI_trap_PC_AddGlobalDefine
==============
*/
static int QDECL QL_UI_trap_PC_AddGlobalDefine( char *define ) {
	return UI_Import_Syscall( UI_PC_ADD_GLOBAL_DEFINE, define );
}

/*
==============
QL_UI_trap_PC_LoadSource
==============
*/
static int QDECL QL_UI_trap_PC_LoadSource( const char *filename ) {
	return UI_Import_Syscall( UI_PC_LOAD_SOURCE, filename );
}

/*
==============
QL_UI_trap_PC_FreeSource
==============
*/
static int QDECL QL_UI_trap_PC_FreeSource( int handle ) {
	return UI_Import_Syscall( UI_PC_FREE_SOURCE, handle );
}

/*
==============
QL_UI_trap_PC_ReadToken
==============
*/
static int QDECL QL_UI_trap_PC_ReadToken( int handle, pc_token_t *pc_token ) {
	return UI_Import_Syscall( UI_PC_READ_TOKEN, handle, pc_token );
}

/*
==============
QL_UI_trap_PC_SourceFileAndLine
==============
*/
static int QDECL QL_UI_trap_PC_SourceFileAndLine( int handle, char *filename, int *line ) {
	return UI_Import_Syscall( UI_PC_SOURCE_FILE_AND_LINE, handle, filename, line );
}

/*
==============
QL_UI_trap_S_StopBackgroundTrack
==============
*/
static void QDECL QL_UI_trap_S_StopBackgroundTrack( void ) {
	UI_Import_Syscall( UI_S_STOPBACKGROUNDTRACK );
}

/*
==============
QL_UI_trap_S_StartBackgroundTrack
==============
*/
static void QDECL QL_UI_trap_S_StartBackgroundTrack( const char *intro, const char *loop ) {
	UI_Import_Syscall( UI_S_STARTBACKGROUNDTRACK, intro, loop );
}

/*
==============
QL_UI_trap_RealTime
==============
*/
static int QDECL QL_UI_trap_RealTime( qtime_t *qtime ) {
	return UI_Import_Syscall( UI_REAL_TIME, qtime );
}

/*
==============
QL_UI_trap_CIN_PlayCinematic
==============
*/
static int QDECL QL_UI_trap_CIN_PlayCinematic( const char *arg0, int xpos, int ypos, int width, int height, int bits ) {
	return UI_Import_Syscall( UI_CIN_PLAYCINEMATIC, arg0, xpos, ypos, width, height, bits );
}

/*
==============
QL_UI_trap_CIN_StopCinematic
==============
*/
static e_status QDECL QL_UI_trap_CIN_StopCinematic( int handle ) {
	return UI_Import_Syscall( UI_CIN_STOPCINEMATIC, handle );
}

/*
==============
QL_UI_trap_CIN_RunCinematic
==============
*/
static e_status QDECL QL_UI_trap_CIN_RunCinematic( int handle ) {
	return UI_Import_Syscall( UI_CIN_RUNCINEMATIC, handle );
}

/*
==============
QL_UI_trap_CIN_DrawCinematic
==============
*/
static void QDECL QL_UI_trap_CIN_DrawCinematic( int handle ) {
	UI_Import_Syscall( UI_CIN_DRAWCINEMATIC, handle );
}

/*
==============
QL_UI_trap_CIN_SetExtents
==============
*/
static void QDECL QL_UI_trap_CIN_SetExtents( int handle, int x, int y, int w, int h ) {
	UI_Import_Syscall( UI_CIN_SETEXTENTS, handle, x, y, w, h );
}

/*
==============
QL_UI_trap_R_RemapShader
==============
*/
static void QDECL QL_UI_trap_R_RemapShader( const char *oldShader, const char *newShader, const char *timeOffset ) {
	UI_Import_Syscall( UI_R_REMAP_SHADER, oldShader, newShader, timeOffset );
}

/*
==============
QL_UI_trap_VerifyCDKey
==============
*/
static qboolean QDECL QL_UI_trap_VerifyCDKey( const char *key, const char *chksum ) {
	return UI_Import_Syscall( UI_VERIFY_CDKEY, key, chksum);
}

/*
==============
QL_UI_trap_SetPbClStatus
==============
*/
static void QDECL QL_UI_trap_SetPbClStatus( int status ) {
	UI_Import_Syscall( UI_SET_PBCLSTATUS, status );
}

/*
==============
QL_UI_trap_CM_LoadModel
==============
*/
static int QDECL QL_UI_trap_CM_LoadModel( const char *name ) {
	(void)name;
	return 0;
}

/*
==============
QL_UI_trap_Memset
==============
*/
static void *QDECL QL_UI_trap_Memset( void *dest, int c, int count ) {
	return memset( dest, c, count );
}

/*
==============
QL_UI_trap_Memcpy
==============
*/
static void *QDECL QL_UI_trap_Memcpy( void *dest, const void *src, int count ) {
	return memcpy( dest, src, count );
}

/*
==============
QL_UI_trap_Strncpy
==============
*/
static char *QDECL QL_UI_trap_Strncpy( char *dest, const char *src, int count ) {
	return strncpy( dest, src, count );
}

/*
==============
QL_UI_trap_Sin
==============
*/
static float QDECL QL_UI_trap_Sin( float x ) {
	return (float)sin( x );
}

/*
==============
QL_UI_trap_Cos
==============
*/
static float QDECL QL_UI_trap_Cos( float x ) {
	return (float)cos( x );
}

/*
==============
QL_UI_trap_Atan2
==============
*/
static float QDECL QL_UI_trap_Atan2( float y, float x ) {
	return (float)atan2( y, x );
}

/*
==============
QL_UI_trap_Sqrt
==============
*/
static float QDECL QL_UI_trap_Sqrt( float x ) {
	return (float)sqrt( x );
}

/*
==============
QL_UI_trap_Floor
==============
*/
static float QDECL QL_UI_trap_Floor( float x ) {
	return (float)floor( x );
}

/*
==============
QL_UI_trap_Ceil
==============
*/
static float QDECL QL_UI_trap_Ceil( float x ) {
	return (float)ceil( x );
}
