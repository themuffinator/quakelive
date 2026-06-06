// Auto-generated game import wrappers for Quake Live native DLLs.
// Generated from g_syscalls.c; do not edit manually.

/*
==============
QL_G_PASSFLOAT
==============
*/
static int QDECL QL_G_PASSFLOAT( float x ) {
	float	floatTemp;
	floatTemp = x;
	return *(int *)&floatTemp;
}

/*
==============
QL_G_trap_Printf
==============
*/
static void QDECL QL_G_trap_Printf( const char *fmt ) {
	G_Import_Syscall( G_PRINT, fmt );
}

/*
==============
QL_G_trap_Error
==============
*/
static void QDECL QL_G_trap_Error( const char *fmt ) {
	G_Import_Syscall( G_ERROR, fmt );
}

/*
==============
QL_G_trap_Milliseconds
==============
*/
static int QDECL QL_G_trap_Milliseconds( void ) {
	return G_Import_Syscall( G_MILLISECONDS );
}

/*
==============
QL_G_trap_Argc
==============
*/
static int QDECL QL_G_trap_Argc( void ) {
	return G_Import_Syscall( G_ARGC );
}

/*
==============
QL_G_trap_Argv
==============
*/
static void QDECL QL_G_trap_Argv( int n, char *buffer, int bufferLength ) {
	G_Import_Syscall( G_ARGV, n, buffer, bufferLength );
}

/*
==============
QL_G_trap_FS_FOpenFile
==============
*/
static int QDECL QL_G_trap_FS_FOpenFile( const char *qpath, fileHandle_t *f, fsMode_t mode ) {
	return G_Import_Syscall( G_FS_FOPEN_FILE, qpath, f, mode );
}

/*
==============
QL_G_trap_FS_Read
==============
*/
static void QDECL QL_G_trap_FS_Read( void *buffer, int len, fileHandle_t f ) {
	G_Import_Syscall( G_FS_READ, buffer, len, f );
}

/*
==============
QL_G_trap_FS_Write
==============
*/
static void QDECL QL_G_trap_FS_Write( const void *buffer, int len, fileHandle_t f ) {
	G_Import_Syscall( G_FS_WRITE, buffer, len, f );
}

/*
==============
QL_G_trap_FS_FCloseFile
==============
*/
static void QDECL QL_G_trap_FS_FCloseFile( fileHandle_t f ) {
	G_Import_Syscall( G_FS_FCLOSE_FILE, f );
}

/*
==============
QL_G_trap_FS_GetFileList
==============
*/
static int QDECL QL_G_trap_FS_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {
	return G_Import_Syscall( G_FS_GETFILELIST, path, extension, listbuf, bufsize );
}

/*
==============
QL_G_trap_FS_Seek
==============
*/
static int QDECL QL_G_trap_FS_Seek( fileHandle_t f, long offset, int origin ) {
	return G_Import_Syscall( G_FS_SEEK, f, offset, origin );
}

/*
==============
QL_G_trap_SendConsoleCommand
==============
*/
static void QDECL QL_G_trap_SendConsoleCommand( int exec_when, const char *text ) {
	G_Import_Syscall( G_SEND_CONSOLE_COMMAND, exec_when, text );
}

/*
==============
QL_G_trap_Cvar_Register
==============
*/
static void QDECL QL_G_trap_Cvar_Register( vmCvar_t *cvar, const char *var_name, const char *value, int flags ) {
	G_Import_Syscall( G_CVAR_REGISTER, cvar, var_name, value, flags );
}

/*
==============
QL_G_trap_Cvar_Update
==============
*/
static void QDECL QL_G_trap_Cvar_Update( vmCvar_t *cvar ) {
	G_Import_Syscall( G_CVAR_UPDATE, cvar );
}

/*
==============
QL_G_trap_Cvar_Set
==============
*/
static void QDECL QL_G_trap_Cvar_Set( const char *var_name, const char *value ) {
	G_Import_Syscall( G_CVAR_SET, var_name, value );
}

/*
==============
QL_G_trap_Cvar_VariableIntegerValue
==============
*/
static int QDECL QL_G_trap_Cvar_VariableIntegerValue( const char *var_name ) {
	return G_Import_Syscall( G_CVAR_VARIABLE_INTEGER_VALUE, var_name );
}

/*
==============
QL_G_trap_Cvar_VariableStringBuffer
==============
*/
static void QDECL QL_G_trap_Cvar_VariableStringBuffer( const char *var_name, char *buffer, int bufsize ) {
	G_Import_Syscall( G_CVAR_VARIABLE_STRING_BUFFER, var_name, buffer, bufsize );
}

/*
==============
QL_G_trap_LocateGameData
==============
*/
static void QDECL QL_G_trap_LocateGameData( sharedEntity_t *gEnts, int numGEntities, int sizeofGEntity_t, playerState_t *clients, int sizeofGClient ) {
	G_Import_Syscall( G_LOCATE_GAME_DATA, gEnts, numGEntities, sizeofGEntity_t, clients, sizeofGClient );
}

/*
==============
QL_G_trap_DropClient
==============
*/
static void QDECL QL_G_trap_DropClient( int clientNum, const char *reason ) {
	G_Import_Syscall( G_DROP_CLIENT, clientNum, reason );
}

/*
==============
QL_G_trap_SendServerCommand
==============
*/
static void QDECL QL_G_trap_SendServerCommand( int clientNum, const char *text ) {
	G_Import_Syscall( G_SEND_SERVER_COMMAND, clientNum, text );
}

/*
==============
QL_G_trap_SetConfigstring
==============
*/
static void QDECL QL_G_trap_SetConfigstring( int num, const char *string ) {
	G_Import_Syscall( G_SET_CONFIGSTRING, num, string );
}

/*
==============
QL_G_trap_GetConfigstring
==============
*/
static void QDECL QL_G_trap_GetConfigstring( int num, char *buffer, int bufferSize ) {
	G_Import_Syscall( G_GET_CONFIGSTRING, num, buffer, bufferSize );
}

/*
==============
QL_G_trap_GetUserinfo
==============
*/
static void QDECL QL_G_trap_GetUserinfo( int num, char *buffer, int bufferSize ) {
	G_Import_Syscall( G_GET_USERINFO, num, buffer, bufferSize );
}

/*
==============
QL_G_trap_SetUserinfo
==============
*/
static void QDECL QL_G_trap_SetUserinfo( int num, const char *buffer ) {
	G_Import_Syscall( G_SET_USERINFO, num, buffer );
}

/*
==============
QL_G_trap_GetServerinfo
==============
*/
static void QDECL QL_G_trap_GetServerinfo( char *buffer, int bufferSize ) {
	G_Import_Syscall( G_GET_SERVERINFO, buffer, bufferSize );
}

/*
==============
QL_G_trap_GetSteamId
==============
*/
static qboolean QDECL QL_G_trap_GetSteamId( int clientNum, unsigned int *steamIdLow, unsigned int *steamIdHigh ) {
	return G_Import_Syscall( G_STEAMID_QUERY, clientNum, steamIdLow, steamIdHigh );
}

/*
==============
QL_G_trap_VerifySteamAuth
==============
*/
static qboolean QDECL QL_G_trap_VerifySteamAuth( int clientNum ) {
	return G_Import_Syscall( G_STEAM_AUTH_VALIDATE, clientNum );
}

/*
==============
QL_G_trap_RankBegin
==============
*/
static void QDECL QL_G_trap_RankBegin( char *gamekey ) {
	G_Import_Syscall( G_RANK_BEGIN, gamekey );
}

/*
==============
QL_G_trap_RankPoll
==============
*/
static void QDECL QL_G_trap_RankPoll( void ) {
	G_Import_Syscall( G_RANK_POLL );
}

/*
==============
QL_G_trap_RankCheckInit
==============
*/
static qboolean QDECL QL_G_trap_RankCheckInit( void ) {
	return G_Import_Syscall( G_RANK_CHECK_INIT );
}

/*
==============
QL_G_trap_RankActive
==============
*/
static qboolean QDECL QL_G_trap_RankActive( void ) {
	return G_Import_Syscall( G_RANK_ACTIVE );
}

/*
==============
QL_G_trap_RankUserStatus
==============
*/
static int QDECL QL_G_trap_RankUserStatus( int index ) {
	return G_Import_Syscall( G_RANK_USER_STATUS, index );
}

/*
==============
QL_G_trap_RankUserReset
==============
*/
static void QDECL QL_G_trap_RankUserReset( int index ) {
	G_Import_Syscall( G_RANK_USER_RESET, index );
}

/*
==============
QL_G_trap_RankReportInt
==============
*/
static void QDECL QL_G_trap_RankReportInt( int index1, int index2, int key, int value, qboolean accum ) {
	G_Import_Syscall( G_RANK_REPORT_INT, index1, index2, key, value, accum );
}

/*
==============
QL_G_trap_RankReportStr
==============
*/
static void QDECL QL_G_trap_RankReportStr( int index1, int index2, int key, char *value ) {
	G_Import_Syscall( G_RANK_REPORT_STR, index1, index2, key, value );
}

/*
==============
QL_G_trap_SetBrushModel
==============
*/
static void QDECL QL_G_trap_SetBrushModel( sharedEntity_t *ent, const char *name ) {
	G_Import_Syscall( G_SET_BRUSH_MODEL, ent, name );
}

/*
==============
QL_G_trap_Trace
==============
*/
static void QDECL QL_G_trap_Trace( trace_t *results, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, int passEntityNum, int contentmask ) {
	G_Import_Syscall( G_TRACE, results, start, mins, maxs, end, passEntityNum, contentmask );
}

/*
==============
QL_G_trap_TraceCapsule
==============
*/
static void QDECL QL_G_trap_TraceCapsule( trace_t *results, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, int passEntityNum, int contentmask ) {
	G_Import_Syscall( G_TRACECAPSULE, results, start, mins, maxs, end, passEntityNum, contentmask );
}

/*
==============
QL_G_trap_PointContents
==============
*/
static int QDECL QL_G_trap_PointContents( const vec3_t point, int passEntityNum ) {
	return G_Import_Syscall( G_POINT_CONTENTS, point, passEntityNum );
}

/*
==============
QL_G_trap_InPVS
==============
*/
static qboolean QDECL QL_G_trap_InPVS( const vec3_t p1, const vec3_t p2 ) {
	return G_Import_Syscall( G_IN_PVS, p1, p2 );
}

/*
==============
QL_G_trap_InPVSIgnorePortals
==============
*/
static qboolean QDECL QL_G_trap_InPVSIgnorePortals( const vec3_t p1, const vec3_t p2 ) {
	return G_Import_Syscall( G_IN_PVS_IGNORE_PORTALS, p1, p2 );
}

/*
==============
QL_G_trap_AdjustAreaPortalState
==============
*/
static void QDECL QL_G_trap_AdjustAreaPortalState( sharedEntity_t *ent, qboolean open ) {
	G_Import_Syscall( G_ADJUST_AREA_PORTAL_STATE, ent, open );
}

/*
==============
QL_G_trap_AreasConnected
==============
*/
static qboolean QDECL QL_G_trap_AreasConnected( int area1, int area2 ) {
	return G_Import_Syscall( G_AREAS_CONNECTED, area1, area2 );
}

/*
==============
QL_G_trap_LinkEntity
==============
*/
static void QDECL QL_G_trap_LinkEntity( sharedEntity_t *ent ) {
	G_Import_Syscall( G_LINKENTITY, ent );
}

/*
==============
QL_G_trap_UnlinkEntity
==============
*/
static void QDECL QL_G_trap_UnlinkEntity( sharedEntity_t *ent ) {
	G_Import_Syscall( G_UNLINKENTITY, ent );
}

/*
==============
QL_G_trap_EntitiesInBox
==============
*/
static int QDECL QL_G_trap_EntitiesInBox( const vec3_t mins, const vec3_t maxs, int *list, int maxcount ) {
	return G_Import_Syscall( G_ENTITIES_IN_BOX, mins, maxs, list, maxcount );
}

/*
==============
QL_G_trap_EntityContact
==============
*/
static qboolean QDECL QL_G_trap_EntityContact( const vec3_t mins, const vec3_t maxs, const sharedEntity_t *ent ) {
	return G_Import_Syscall( G_ENTITY_CONTACT, mins, maxs, ent );
}

/*
==============
QL_G_trap_EntityContactCapsule
==============
*/
static qboolean QDECL QL_G_trap_EntityContactCapsule( const vec3_t mins, const vec3_t maxs, const sharedEntity_t *ent ) {
	return G_Import_Syscall( G_ENTITY_CONTACTCAPSULE, mins, maxs, ent );
}

/*
==============
QL_G_trap_BotAllocateClient
==============
*/
static int QDECL QL_G_trap_BotAllocateClient( void ) {
	return G_Import_Syscall( G_BOT_ALLOCATE_CLIENT );
}

/*
==============
QL_G_trap_BotFreeClient
==============
*/
static void QDECL QL_G_trap_BotFreeClient( int clientNum ) {
	G_Import_Syscall( G_BOT_FREE_CLIENT, clientNum );
}

/*
==============
QL_G_trap_GetUsercmd
==============
*/
static void QDECL QL_G_trap_GetUsercmd( int clientNum, usercmd_t *cmd ) {
	G_Import_Syscall( G_GET_USERCMD, clientNum, cmd );
}

/*
==============
QL_G_trap_GetEntityToken
==============
*/
static qboolean QDECL QL_G_trap_GetEntityToken( char *buffer, int bufferSize ) {
	return G_Import_Syscall( G_GET_ENTITY_TOKEN, buffer, bufferSize );
}

/*
==============
QL_G_trap_DebugPolygonCreate
==============
*/
static int QDECL QL_G_trap_DebugPolygonCreate( int color, int numPoints, vec3_t *points ) {
	return G_Import_Syscall( G_DEBUG_POLYGON_CREATE, color, numPoints, points );
}

/*
==============
QL_G_trap_DebugPolygonDelete
==============
*/
static void QDECL QL_G_trap_DebugPolygonDelete( int id ) {
	G_Import_Syscall( G_DEBUG_POLYGON_DELETE, id );
}

/*
==============
QL_G_trap_RealTime
==============
*/
static int QDECL QL_G_trap_RealTime( qtime_t *qtime ) {
	return G_Import_Syscall( G_REAL_TIME, qtime );
}

/*
==============
QL_G_trap_SnapVector
==============
*/
static void QDECL QL_G_trap_SnapVector( float *v ) {
	G_Import_Syscall( G_SNAPVECTOR, v );
	return;
}

/*
==============
QL_G_trap_BotLibSetup
==============
*/
static int QDECL QL_G_trap_BotLibSetup( void ) {
	return G_Import_Syscall( BOTLIB_SETUP );
}

/*
==============
QL_G_trap_BotLibShutdown
==============
*/
static int QDECL QL_G_trap_BotLibShutdown( void ) {
	return G_Import_Syscall( BOTLIB_SHUTDOWN );
}

/*
==============
QL_G_trap_BotLibVarSet
==============
*/
static int QDECL QL_G_trap_BotLibVarSet( char *var_name, char *value ) {
	return G_Import_Syscall( BOTLIB_LIBVAR_SET, var_name, value );
}

/*
==============
QL_G_trap_BotLibVarGet
==============
*/
static int QDECL QL_G_trap_BotLibVarGet( char *var_name, char *value, int size ) {
	return G_Import_Syscall( BOTLIB_LIBVAR_GET, var_name, value, size );
}

/*
==============
QL_G_trap_BotLibDefine
==============
*/
static int QDECL QL_G_trap_BotLibDefine( char *string ) {
	return G_Import_Syscall( BOTLIB_PC_ADD_GLOBAL_DEFINE, string );
}

/*
==============
QL_G_trap_BotLibStartFrame
==============
*/
static int QDECL QL_G_trap_BotLibStartFrame( float time ) {
	return G_Import_Syscall( BOTLIB_START_FRAME, QL_G_PASSFLOAT( time ) );
}

/*
==============
QL_G_trap_BotLibLoadMap
==============
*/
static int QDECL QL_G_trap_BotLibLoadMap( const char *mapname ) {
	return G_Import_Syscall( BOTLIB_LOAD_MAP, mapname );
}

/*
==============
QL_G_trap_BotLibUpdateEntity
==============
*/
static int QDECL QL_G_trap_BotLibUpdateEntity( int ent, void /* struct bot_updateentity_s */ *bue ) {
	return G_Import_Syscall( BOTLIB_UPDATENTITY, ent, bue );
}

/*
==============
QL_G_trap_BotLibTest
==============
*/
static int QDECL QL_G_trap_BotLibTest( int parm0, char *parm1, vec3_t parm2, vec3_t parm3 ) {
	return G_Import_Syscall( BOTLIB_TEST, parm0, parm1, parm2, parm3 );
}

/*
==============
QL_G_trap_BotGetSnapshotEntity
==============
*/
static int QDECL QL_G_trap_BotGetSnapshotEntity( int clientNum, int sequence ) {
	return G_Import_Syscall( BOTLIB_GET_SNAPSHOT_ENTITY, clientNum, sequence );
}

/*
==============
QL_G_trap_BotGetServerCommand
==============
*/
static int QDECL QL_G_trap_BotGetServerCommand( int clientNum, char *message, int size ) {
	return G_Import_Syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );
}

/*
==============
QL_G_trap_BotUserCommand
==============
*/
static void QDECL QL_G_trap_BotUserCommand( int clientNum, usercmd_t *ucmd ) {
	G_Import_Syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );
}

/*
==============
QL_G_trap_AAS_EntityInfo
==============
*/
static void QDECL QL_G_trap_AAS_EntityInfo( int entnum, void /* struct aas_entityinfo_s */ *info ) {
	G_Import_Syscall( BOTLIB_AAS_ENTITY_INFO, entnum, info );
}

/*
==============
QL_G_trap_AAS_Initialized
==============
*/
static int QDECL QL_G_trap_AAS_Initialized( void ) {
	return G_Import_Syscall( BOTLIB_AAS_INITIALIZED );
}

/*
==============
QL_G_trap_AAS_PresenceTypeBoundingBox
==============
*/
static void QDECL QL_G_trap_AAS_PresenceTypeBoundingBox( int presencetype, vec3_t mins, vec3_t maxs ) {
	G_Import_Syscall( BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX, presencetype, mins, maxs );
}

/*
==============
QL_G_trap_AAS_Time
==============
*/
static float QDECL QL_G_trap_AAS_Time( void ) {
	int temp;
	temp = G_Import_Syscall( BOTLIB_AAS_TIME );
	return (*(float*)&temp);
}

/*
==============
QL_G_trap_AAS_PointAreaNum
==============
*/
static int QDECL QL_G_trap_AAS_PointAreaNum( vec3_t point ) {
	return G_Import_Syscall( BOTLIB_AAS_POINT_AREA_NUM, point );
}

/*
==============
QL_G_trap_AAS_PointReachabilityAreaIndex
==============
*/
static int QDECL QL_G_trap_AAS_PointReachabilityAreaIndex( vec3_t point ) {
	return G_Import_Syscall( BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX, point );
}

/*
==============
QL_G_trap_AAS_TraceAreas
==============
*/
static int QDECL QL_G_trap_AAS_TraceAreas( vec3_t start, vec3_t end, int *areas, vec3_t *points, int maxareas ) {
	return G_Import_Syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );
}

/*
==============
QL_G_trap_AAS_BBoxAreas
==============
*/
static int QDECL QL_G_trap_AAS_BBoxAreas( vec3_t absmins, vec3_t absmaxs, int *areas, int maxareas ) {
	return G_Import_Syscall( BOTLIB_AAS_BBOX_AREAS, absmins, absmaxs, areas, maxareas );
}

/*
==============
QL_G_trap_AAS_AreaInfo
==============
*/
static int QDECL QL_G_trap_AAS_AreaInfo( int areanum, void /* struct aas_areainfo_s */ *info ) {
	return G_Import_Syscall( BOTLIB_AAS_AREA_INFO, areanum, info );
}

/*
==============
QL_G_trap_AAS_PointContents
==============
*/
static int QDECL QL_G_trap_AAS_PointContents( vec3_t point ) {
	return G_Import_Syscall( BOTLIB_AAS_POINT_CONTENTS, point );
}

/*
==============
QL_G_trap_AAS_NextBSPEntity
==============
*/
static int QDECL QL_G_trap_AAS_NextBSPEntity( int ent ) {
	return G_Import_Syscall( BOTLIB_AAS_NEXT_BSP_ENTITY, ent );
}

/*
==============
QL_G_trap_AAS_ValueForBSPEpairKey
==============
*/
static int QDECL QL_G_trap_AAS_ValueForBSPEpairKey( int ent, char *key, char *value, int size ) {
	return G_Import_Syscall( BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY, ent, key, value, size );
}

/*
==============
QL_G_trap_AAS_VectorForBSPEpairKey
==============
*/
static int QDECL QL_G_trap_AAS_VectorForBSPEpairKey( int ent, char *key, vec3_t v ) {
	return G_Import_Syscall( BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY, ent, key, v );
}

/*
==============
QL_G_trap_AAS_FloatForBSPEpairKey
==============
*/
static int QDECL QL_G_trap_AAS_FloatForBSPEpairKey( int ent, char *key, float *value ) {
	return G_Import_Syscall( BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY, ent, key, value );
}

/*
==============
QL_G_trap_AAS_IntForBSPEpairKey
==============
*/
static int QDECL QL_G_trap_AAS_IntForBSPEpairKey( int ent, char *key, int *value ) {
	return G_Import_Syscall( BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY, ent, key, value );
}

/*
==============
QL_G_trap_AAS_AreaReachability
==============
*/
static int QDECL QL_G_trap_AAS_AreaReachability( int areanum ) {
	return G_Import_Syscall( BOTLIB_AAS_AREA_REACHABILITY, areanum );
}

/*
==============
QL_G_trap_AAS_AreaTravelTimeToGoalArea
==============
*/
static int QDECL QL_G_trap_AAS_AreaTravelTimeToGoalArea( int areanum, vec3_t origin, int goalareanum, int travelflags ) {
	return G_Import_Syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );
}

/*
==============
QL_G_trap_AAS_EnableRoutingArea
==============
*/
static int QDECL QL_G_trap_AAS_EnableRoutingArea( int areanum, int enable ) {
	return G_Import_Syscall( BOTLIB_AAS_ENABLE_ROUTING_AREA, areanum, enable );
}

/*
==============
QL_G_trap_AAS_PredictRoute
==============
*/
static int QDECL QL_G_trap_AAS_PredictRoute( void /*struct aas_predictroute_s*/ *route, int areanum, vec3_t origin, int goalareanum, int travelflags, int maxareas, int maxtime, int stopevent, int stopcontents, int stoptfl, int stopareanum ) {
	return G_Import_Syscall( BOTLIB_AAS_PREDICT_ROUTE, route, areanum, origin, goalareanum, travelflags, maxareas, maxtime, stopevent, stopcontents, stoptfl, stopareanum );
}

/*
==============
QL_G_trap_AAS_AlternativeRouteGoals
==============
*/
static int QDECL QL_G_trap_AAS_AlternativeRouteGoals( vec3_t start, int startareanum, vec3_t goal, int goalareanum, int travelflags, void /*struct aas_altroutegoal_s*/ *altroutegoals, int maxaltroutegoals, int type ) {
	return G_Import_Syscall( BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL, start, startareanum, goal, goalareanum, travelflags, altroutegoals, maxaltroutegoals, type );
}

/*
==============
QL_G_trap_AAS_Swimming
==============
*/
static int QDECL QL_G_trap_AAS_Swimming( vec3_t origin ) {
	return G_Import_Syscall( BOTLIB_AAS_SWIMMING, origin );
}

/*
==============
QL_G_trap_AAS_PredictClientMovement
==============
*/
static int QDECL QL_G_trap_AAS_PredictClientMovement( void /* struct aas_clientmove_s */ *move, int entnum, vec3_t origin, int presencetype, int onground, vec3_t velocity, vec3_t cmdmove, int cmdframes, int maxframes, float frametime, int stopevent, int stopareanum, int visualize ) {
	return G_Import_Syscall( BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT, move, entnum, origin, presencetype, onground, velocity, cmdmove, cmdframes, maxframes, QL_G_PASSFLOAT(frametime), stopevent, stopareanum, visualize );
}

/*
==============
QL_G_trap_EA_Say
==============
*/
static void QDECL QL_G_trap_EA_Say( int client, char *str ) {
	G_Import_Syscall( BOTLIB_EA_SAY, client, str );
}

/*
==============
QL_G_trap_EA_SayTeam
==============
*/
static void QDECL QL_G_trap_EA_SayTeam( int client, char *str ) {
	G_Import_Syscall( BOTLIB_EA_SAY_TEAM, client, str );
}

/*
==============
QL_G_trap_EA_Command
==============
*/
static void QDECL QL_G_trap_EA_Command( int client, char *command ) {
	G_Import_Syscall( BOTLIB_EA_COMMAND, client, command );
}

/*
==============
QL_G_trap_EA_Action
==============
*/
static void QDECL QL_G_trap_EA_Action( int client, int action ) {
	G_Import_Syscall( BOTLIB_EA_ACTION, client, action );
}

/*
==============
QL_G_trap_EA_Walk
==============
*/
static void QDECL QL_G_trap_EA_Walk( int client ) {
	botlib_export->ea.EA_Walk( client );
}

/*
==============
QL_G_trap_EA_Gesture
==============
*/
static void QDECL QL_G_trap_EA_Gesture( int client ) {
	G_Import_Syscall( BOTLIB_EA_GESTURE, client );
}

/*
==============
QL_G_trap_EA_Talk
==============
*/
static void QDECL QL_G_trap_EA_Talk( int client ) {
	G_Import_Syscall( BOTLIB_EA_TALK, client );
}

/*
==============
QL_G_trap_EA_Attack
==============
*/
static void QDECL QL_G_trap_EA_Attack( int client ) {
	G_Import_Syscall( BOTLIB_EA_ATTACK, client );
}

/*
==============
QL_G_trap_EA_Use
==============
*/
static void QDECL QL_G_trap_EA_Use( int client ) {
	G_Import_Syscall( BOTLIB_EA_USE, client );
}

/*
==============
QL_G_trap_EA_Respawn
==============
*/
static void QDECL QL_G_trap_EA_Respawn( int client ) {
	G_Import_Syscall( BOTLIB_EA_RESPAWN, client );
}

/*
==============
QL_G_trap_EA_Crouch
==============
*/
static void QDECL QL_G_trap_EA_Crouch( int client ) {
	G_Import_Syscall( BOTLIB_EA_CROUCH, client );
}

/*
==============
QL_G_trap_EA_MoveUp
==============
*/
static void QDECL QL_G_trap_EA_MoveUp( int client ) {
	G_Import_Syscall( BOTLIB_EA_MOVE_UP, client );
}

/*
==============
QL_G_trap_EA_MoveDown
==============
*/
static void QDECL QL_G_trap_EA_MoveDown( int client ) {
	G_Import_Syscall( BOTLIB_EA_MOVE_DOWN, client );
}

/*
==============
QL_G_trap_EA_MoveForward
==============
*/
static void QDECL QL_G_trap_EA_MoveForward( int client ) {
	G_Import_Syscall( BOTLIB_EA_MOVE_FORWARD, client );
}

/*
==============
QL_G_trap_EA_MoveBack
==============
*/
static void QDECL QL_G_trap_EA_MoveBack( int client ) {
	G_Import_Syscall( BOTLIB_EA_MOVE_BACK, client );
}

/*
==============
QL_G_trap_EA_MoveLeft
==============
*/
static void QDECL QL_G_trap_EA_MoveLeft( int client ) {
	G_Import_Syscall( BOTLIB_EA_MOVE_LEFT, client );
}

/*
==============
QL_G_trap_EA_MoveRight
==============
*/
static void QDECL QL_G_trap_EA_MoveRight( int client ) {
	G_Import_Syscall( BOTLIB_EA_MOVE_RIGHT, client );
}

/*
==============
QL_G_trap_EA_SelectWeapon
==============
*/
static void QDECL QL_G_trap_EA_SelectWeapon( int client, int weapon ) {
	G_Import_Syscall( BOTLIB_EA_SELECT_WEAPON, client, weapon );
}

/*
==============
QL_G_trap_EA_Jump
==============
*/
static void QDECL QL_G_trap_EA_Jump( int client ) {
	G_Import_Syscall( BOTLIB_EA_JUMP, client );
}

/*
==============
QL_G_trap_EA_DelayedJump
==============
*/
static void QDECL QL_G_trap_EA_DelayedJump( int client ) {
	G_Import_Syscall( BOTLIB_EA_DELAYED_JUMP, client );
}

/*
==============
QL_G_trap_EA_Move
==============
*/
static void QDECL QL_G_trap_EA_Move( int client, vec3_t dir, float speed ) {
	G_Import_Syscall( BOTLIB_EA_MOVE, client, dir, QL_G_PASSFLOAT(speed) );
}

/*
==============
QL_G_trap_EA_View
==============
*/
static void QDECL QL_G_trap_EA_View( int client, vec3_t viewangles ) {
	G_Import_Syscall( BOTLIB_EA_VIEW, client, viewangles );
}

/*
==============
QL_G_trap_EA_EndRegular
==============
*/
static void QDECL QL_G_trap_EA_EndRegular( int client, float thinktime ) {
	G_Import_Syscall( BOTLIB_EA_END_REGULAR, client, QL_G_PASSFLOAT(thinktime) );
}

/*
==============
QL_G_trap_EA_GetInput
==============
*/
static void QDECL QL_G_trap_EA_GetInput( int client, float thinktime, void /* struct bot_input_s */ *input ) {
	G_Import_Syscall( BOTLIB_EA_GET_INPUT, client, QL_G_PASSFLOAT(thinktime), input );
}

/*
==============
QL_G_trap_EA_ResetInput
==============
*/
static void QDECL QL_G_trap_EA_ResetInput( int client ) {
	G_Import_Syscall( BOTLIB_EA_RESET_INPUT, client );
}

/*
==============
QL_G_trap_BotLoadCharacter
==============
*/
static int QDECL QL_G_trap_BotLoadCharacter( char *charfile, float skill ) {
	return G_Import_Syscall( BOTLIB_AI_LOAD_CHARACTER, charfile, QL_G_PASSFLOAT(skill));
}

/*
==============
QL_G_trap_BotFreeCharacter
==============
*/
static void QDECL QL_G_trap_BotFreeCharacter( int character ) {
	G_Import_Syscall( BOTLIB_AI_FREE_CHARACTER, character );
}

/*
==============
QL_G_trap_Characteristic_Float
==============
*/
static float QDECL QL_G_trap_Characteristic_Float( int character, int index ) {
	int temp;
	temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_FLOAT, character, index );
	return (*(float*)&temp);
}

/*
==============
QL_G_trap_Characteristic_BFloat
==============
*/
static float QDECL QL_G_trap_Characteristic_BFloat( int character, int index, float min, float max ) {
	int temp;
	temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, QL_G_PASSFLOAT(min), QL_G_PASSFLOAT(max) );
	return (*(float*)&temp);
}

/*
==============
QL_G_trap_Characteristic_Integer
==============
*/
static int QDECL QL_G_trap_Characteristic_Integer( int character, int index ) {
	return G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_INTEGER, character, index );
}

/*
==============
QL_G_trap_Characteristic_BInteger
==============
*/
static int QDECL QL_G_trap_Characteristic_BInteger( int character, int index, int min, int max ) {
	return G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BINTEGER, character, index, min, max );
}

/*
==============
QL_G_trap_Characteristic_String
==============
*/
static void QDECL QL_G_trap_Characteristic_String( int character, int index, char *buf, int size ) {
	G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_STRING, character, index, buf, size );
}

/*
==============
QL_G_trap_BotAllocChatState
==============
*/
static int QDECL QL_G_trap_BotAllocChatState( void ) {
	return G_Import_Syscall( BOTLIB_AI_ALLOC_CHAT_STATE );
}

/*
==============
QL_G_trap_BotFreeChatState
==============
*/
static void QDECL QL_G_trap_BotFreeChatState( int handle ) {
	G_Import_Syscall( BOTLIB_AI_FREE_CHAT_STATE, handle );
}

/*
==============
QL_G_trap_BotQueueConsoleMessage
==============
*/
static void QDECL QL_G_trap_BotQueueConsoleMessage( int chatstate, int type, char *message ) {
	G_Import_Syscall( BOTLIB_AI_QUEUE_CONSOLE_MESSAGE, chatstate, type, message );
}

/*
==============
QL_G_trap_BotRemoveConsoleMessage
==============
*/
static void QDECL QL_G_trap_BotRemoveConsoleMessage( int chatstate, int handle ) {
	G_Import_Syscall( BOTLIB_AI_REMOVE_CONSOLE_MESSAGE, chatstate, handle );
}

/*
==============
QL_G_trap_BotNextConsoleMessage
==============
*/
static int QDECL QL_G_trap_BotNextConsoleMessage( int chatstate, void /* struct bot_consolemessage_s */ *cm ) {
	return G_Import_Syscall( BOTLIB_AI_NEXT_CONSOLE_MESSAGE, chatstate, cm );
}

/*
==============
QL_G_trap_BotNumConsoleMessages
==============
*/
static int QDECL QL_G_trap_BotNumConsoleMessages( int chatstate ) {
	return G_Import_Syscall( BOTLIB_AI_NUM_CONSOLE_MESSAGE, chatstate );
}

/*
==============
QL_G_trap_BotInitialChat
==============
*/
static void QDECL QL_G_trap_BotInitialChat( int chatstate, char *type, int mcontext, char *var0, char *var1, char *var2, char *var3, char *var4, char *var5, char *var6, char *var7 ) {
	G_Import_Syscall( BOTLIB_AI_INITIAL_CHAT, chatstate, type, mcontext, var0, var1, var2, var3, var4, var5, var6, var7 );
}

/*
==============
QL_G_trap_BotNumInitialChats
==============
*/
static int QDECL QL_G_trap_BotNumInitialChats( int chatstate, char *type ) {
	return G_Import_Syscall( BOTLIB_AI_NUM_INITIAL_CHATS, chatstate, type );
}

/*
==============
QL_G_trap_BotReplyChat
==============
*/
static int QDECL QL_G_trap_BotReplyChat( int chatstate, char *message, int mcontext, int vcontext, char *var0, char *var1, char *var2, char *var3, char *var4, char *var5, char *var6, char *var7 ) {
	return G_Import_Syscall( BOTLIB_AI_REPLY_CHAT, chatstate, message, mcontext, vcontext, var0, var1, var2, var3, var4, var5, var6, var7 );
}

/*
==============
QL_G_trap_BotChatLength
==============
*/
static int QDECL QL_G_trap_BotChatLength( int chatstate ) {
	return G_Import_Syscall( BOTLIB_AI_CHAT_LENGTH, chatstate );
}

/*
==============
QL_G_trap_BotEnterChat
==============
*/
static void QDECL QL_G_trap_BotEnterChat( int chatstate, int client, int sendto ) {
	G_Import_Syscall( BOTLIB_AI_ENTER_CHAT, chatstate, client, sendto );
}

/*
==============
QL_G_trap_BotGetChatMessage
==============
*/
static void QDECL QL_G_trap_BotGetChatMessage( int chatstate, char *buf, int size ) {
	G_Import_Syscall( BOTLIB_AI_GET_CHAT_MESSAGE, chatstate, buf, size);
}

/*
==============
QL_G_trap_StringContains
==============
*/
static int QDECL QL_G_trap_StringContains( char *str1, char *str2, int casesensitive ) {
	return G_Import_Syscall( BOTLIB_AI_STRING_CONTAINS, str1, str2, casesensitive );
}

/*
==============
QL_G_trap_BotFindMatch
==============
*/
static int QDECL QL_G_trap_BotFindMatch( char *str, void /* struct bot_match_s */ *match, unsigned long int context ) {
	return G_Import_Syscall( BOTLIB_AI_FIND_MATCH, str, match, context );
}

/*
==============
QL_G_trap_BotMatchVariable
==============
*/
static void QDECL QL_G_trap_BotMatchVariable( void /* struct bot_match_s */ *match, int variable, char *buf, int size ) {
	G_Import_Syscall( BOTLIB_AI_MATCH_VARIABLE, match, variable, buf, size );
}

/*
==============
QL_G_trap_UnifyWhiteSpaces
==============
*/
static void QDECL QL_G_trap_UnifyWhiteSpaces( char *string ) {
	G_Import_Syscall( BOTLIB_AI_UNIFY_WHITE_SPACES, string );
}

/*
==============
QL_G_trap_BotReplaceSynonyms
==============
*/
static void QDECL QL_G_trap_BotReplaceSynonyms( char *string, unsigned long int context ) {
	G_Import_Syscall( BOTLIB_AI_REPLACE_SYNONYMS, string, context );
}

/*
==============
QL_G_trap_BotLoadChatFile
==============
*/
static int QDECL QL_G_trap_BotLoadChatFile( int chatstate, char *chatfile, char *chatname ) {
	return G_Import_Syscall( BOTLIB_AI_LOAD_CHAT_FILE, chatstate, chatfile, chatname );
}

/*
==============
QL_G_trap_BotSetChatGender
==============
*/
static void QDECL QL_G_trap_BotSetChatGender( int chatstate, int gender ) {
	G_Import_Syscall( BOTLIB_AI_SET_CHAT_GENDER, chatstate, gender );
}

/*
==============
QL_G_trap_BotSetChatName
==============
*/
static void QDECL QL_G_trap_BotSetChatName( int chatstate, char *name, int client ) {
	G_Import_Syscall( BOTLIB_AI_SET_CHAT_NAME, chatstate, name, client );
}

/*
==============
QL_G_trap_BotResetGoalState
==============
*/
static void QDECL QL_G_trap_BotResetGoalState( int goalstate ) {
	G_Import_Syscall( BOTLIB_AI_RESET_GOAL_STATE, goalstate );
}

/*
==============
QL_G_trap_BotResetAvoidGoals
==============
*/
static void QDECL QL_G_trap_BotResetAvoidGoals( int goalstate ) {
	G_Import_Syscall( BOTLIB_AI_RESET_AVOID_GOALS, goalstate );
}

/*
==============
QL_G_trap_BotRemoveFromAvoidGoals
==============
*/
static void QDECL QL_G_trap_BotRemoveFromAvoidGoals( int goalstate, int number ) {
	G_Import_Syscall( BOTLIB_AI_REMOVE_FROM_AVOID_GOALS, goalstate, number);
}

/*
==============
QL_G_trap_BotPushGoal
==============
*/
static void QDECL QL_G_trap_BotPushGoal( int goalstate, void /* struct bot_goal_s */ *goal ) {
	G_Import_Syscall( BOTLIB_AI_PUSH_GOAL, goalstate, goal );
}

/*
==============
QL_G_trap_BotPopGoal
==============
*/
static void QDECL QL_G_trap_BotPopGoal( int goalstate ) {
	G_Import_Syscall( BOTLIB_AI_POP_GOAL, goalstate );
}

/*
==============
QL_G_trap_BotEmptyGoalStack
==============
*/
static void QDECL QL_G_trap_BotEmptyGoalStack( int goalstate ) {
	G_Import_Syscall( BOTLIB_AI_EMPTY_GOAL_STACK, goalstate );
}

/*
==============
QL_G_trap_BotDumpAvoidGoals
==============
*/
static void QDECL QL_G_trap_BotDumpAvoidGoals( int goalstate ) {
	G_Import_Syscall( BOTLIB_AI_DUMP_AVOID_GOALS, goalstate );
}

/*
==============
QL_G_trap_BotDumpGoalStack
==============
*/
static void QDECL QL_G_trap_BotDumpGoalStack( int goalstate ) {
	G_Import_Syscall( BOTLIB_AI_DUMP_GOAL_STACK, goalstate );
}

/*
==============
QL_G_trap_BotGoalName
==============
*/
static void QDECL QL_G_trap_BotGoalName( int number, char *name, int size ) {
	G_Import_Syscall( BOTLIB_AI_GOAL_NAME, number, name, size );
}

/*
==============
QL_G_trap_BotGetTopGoal
==============
*/
static int QDECL QL_G_trap_BotGetTopGoal( int goalstate, void /* struct bot_goal_s */ *goal ) {
	return G_Import_Syscall( BOTLIB_AI_GET_TOP_GOAL, goalstate, goal );
}

/*
==============
QL_G_trap_BotGetSecondGoal
==============
*/
static int QDECL QL_G_trap_BotGetSecondGoal( int goalstate, void /* struct bot_goal_s */ *goal ) {
	return G_Import_Syscall( BOTLIB_AI_GET_SECOND_GOAL, goalstate, goal );
}

/*
==============
QL_G_trap_BotChooseLTGItem
==============
*/
static int QDECL QL_G_trap_BotChooseLTGItem( int goalstate, vec3_t origin, int *inventory, int travelflags ) {
	return G_Import_Syscall( BOTLIB_AI_CHOOSE_LTG_ITEM, goalstate, origin, inventory, travelflags );
}

/*
==============
QL_G_trap_BotChooseNBGItem
==============
*/
static int QDECL QL_G_trap_BotChooseNBGItem( int goalstate, vec3_t origin, int *inventory, int travelflags, void /* struct bot_goal_s */ *ltg, float maxtime ) {
	return G_Import_Syscall( BOTLIB_AI_CHOOSE_NBG_ITEM, goalstate, origin, inventory, travelflags, ltg, QL_G_PASSFLOAT(maxtime) );
}

/*
==============
QL_G_trap_BotTouchingGoal
==============
*/
static int QDECL QL_G_trap_BotTouchingGoal( vec3_t origin, void /* struct bot_goal_s */ *goal ) {
	return G_Import_Syscall( BOTLIB_AI_TOUCHING_GOAL, origin, goal );
}

/*
==============
QL_G_trap_BotItemGoalInVisButNotVisible
==============
*/
static int QDECL QL_G_trap_BotItemGoalInVisButNotVisible( int viewer, vec3_t eye, vec3_t viewangles, void /* struct bot_goal_s */ *goal ) {
	return G_Import_Syscall( BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE, viewer, eye, viewangles, goal );
}

/*
==============
QL_G_trap_BotGetLevelItemGoal
==============
*/
static int QDECL QL_G_trap_BotGetLevelItemGoal( int index, char *classname, void /* struct bot_goal_s */ *goal ) {
	return G_Import_Syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );
}

/*
==============
QL_G_trap_BotGetNextCampSpotGoal
==============
*/
static int QDECL QL_G_trap_BotGetNextCampSpotGoal( int num, void /* struct bot_goal_s */ *goal ) {
	return G_Import_Syscall( BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL, num, goal );
}

/*
==============
QL_G_trap_BotGetMapLocationGoal
==============
*/
static int QDECL QL_G_trap_BotGetMapLocationGoal( char *name, void /* struct bot_goal_s */ *goal ) {
	return G_Import_Syscall( BOTLIB_AI_GET_MAP_LOCATION_GOAL, name, goal );
}

/*
==============
QL_G_trap_BotAvoidGoalTime
==============
*/
static float QDECL QL_G_trap_BotAvoidGoalTime( int goalstate, int number ) {
	int temp;
	temp = G_Import_Syscall( BOTLIB_AI_AVOID_GOAL_TIME, goalstate, number );
	return (*(float*)&temp);
}

/*
==============
QL_G_trap_BotSetAvoidGoalTime
==============
*/
static void QDECL QL_G_trap_BotSetAvoidGoalTime( int goalstate, int number, float avoidtime ) {
	G_Import_Syscall( BOTLIB_AI_SET_AVOID_GOAL_TIME, goalstate, number, QL_G_PASSFLOAT(avoidtime));
}

/*
==============
QL_G_trap_BotInitLevelItems
==============
*/
static void QDECL QL_G_trap_BotInitLevelItems( void ) {
	G_Import_Syscall( BOTLIB_AI_INIT_LEVEL_ITEMS );
}

/*
==============
QL_G_trap_BotUpdateEntityItems
==============
*/
static void QDECL QL_G_trap_BotUpdateEntityItems( void ) {
	G_Import_Syscall( BOTLIB_AI_UPDATE_ENTITY_ITEMS );
}

/*
==============
QL_G_trap_BotLoadItemWeights
==============
*/
static int QDECL QL_G_trap_BotLoadItemWeights( int goalstate, char *filename ) {
	return G_Import_Syscall( BOTLIB_AI_LOAD_ITEM_WEIGHTS, goalstate, filename );
}

/*
==============
QL_G_trap_BotFreeItemWeights
==============
*/
static void QDECL QL_G_trap_BotFreeItemWeights( int goalstate ) {
	G_Import_Syscall( BOTLIB_AI_FREE_ITEM_WEIGHTS, goalstate );
}

/*
==============
QL_G_trap_BotInterbreedGoalFuzzyLogic
==============
*/
static void QDECL QL_G_trap_BotInterbreedGoalFuzzyLogic( int parent1, int parent2, int child ) {
	G_Import_Syscall( BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC, parent1, parent2, child );
}

/*
==============
QL_G_trap_BotSaveGoalFuzzyLogic
==============
*/
static void QDECL QL_G_trap_BotSaveGoalFuzzyLogic( int goalstate, char *filename ) {
	G_Import_Syscall( BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC, goalstate, filename );
}

/*
==============
QL_G_trap_BotMutateGoalFuzzyLogic
==============
*/
static void QDECL QL_G_trap_BotMutateGoalFuzzyLogic( int goalstate, float range ) {
	G_Import_Syscall( BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC, goalstate, QL_G_PASSFLOAT(range) );
}

/*
==============
QL_G_trap_BotAllocGoalState
==============
*/
static int QDECL QL_G_trap_BotAllocGoalState( int state ) {
	return G_Import_Syscall( BOTLIB_AI_ALLOC_GOAL_STATE, state );
}

/*
==============
QL_G_trap_BotFreeGoalState
==============
*/
static void QDECL QL_G_trap_BotFreeGoalState( int handle ) {
	G_Import_Syscall( BOTLIB_AI_FREE_GOAL_STATE, handle );
}

/*
==============
QL_G_trap_BotResetMoveState
==============
*/
static void QDECL QL_G_trap_BotResetMoveState( int movestate ) {
	G_Import_Syscall( BOTLIB_AI_RESET_MOVE_STATE, movestate );
}

/*
==============
QL_G_trap_BotAddAvoidSpot
==============
*/
static void QDECL QL_G_trap_BotAddAvoidSpot( int movestate, vec3_t origin, float radius, int type ) {
	G_Import_Syscall( BOTLIB_AI_ADD_AVOID_SPOT, movestate, origin, QL_G_PASSFLOAT(radius), type);
}

/*
==============
QL_G_trap_BotMoveToGoal
==============
*/
static void QDECL QL_G_trap_BotMoveToGoal( void /* struct bot_moveresult_s */ *result, int movestate, void /* struct bot_goal_s */ *goal, int travelflags ) {
	G_Import_Syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );
}

/*
==============
QL_G_trap_BotMoveInDirection
==============
*/
static int QDECL QL_G_trap_BotMoveInDirection( int movestate, vec3_t dir, float speed, int type ) {
	return G_Import_Syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, QL_G_PASSFLOAT(speed), type );
}

/*
==============
QL_G_trap_BotResetAvoidReach
==============
*/
static void QDECL QL_G_trap_BotResetAvoidReach( int movestate ) {
	G_Import_Syscall( BOTLIB_AI_RESET_AVOID_REACH, movestate );
}

/*
==============
QL_G_trap_BotResetLastAvoidReach
==============
*/
static void QDECL QL_G_trap_BotResetLastAvoidReach( int movestate ) {
	G_Import_Syscall( BOTLIB_AI_RESET_LAST_AVOID_REACH,movestate  );
}

/*
==============
QL_G_trap_BotReachabilityArea
==============
*/
static int QDECL QL_G_trap_BotReachabilityArea( vec3_t origin, int testground ) {
	return G_Import_Syscall( BOTLIB_AI_REACHABILITY_AREA, origin, testground );
}

/*
==============
QL_G_trap_BotMovementViewTarget
==============
*/
static int QDECL QL_G_trap_BotMovementViewTarget( int movestate, void /* struct bot_goal_s */ *goal, int travelflags, float lookahead, vec3_t target ) {
	return G_Import_Syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, QL_G_PASSFLOAT(lookahead), target );
}

/*
==============
QL_G_trap_BotPredictVisiblePosition
==============
*/
static int QDECL QL_G_trap_BotPredictVisiblePosition( vec3_t origin, int areanum, void /* struct bot_goal_s */ *goal, int travelflags, vec3_t target ) {
	return G_Import_Syscall( BOTLIB_AI_PREDICT_VISIBLE_POSITION, origin, areanum, goal, travelflags, target );
}

/*
==============
QL_G_trap_BotAllocMoveState
==============
*/
static int QDECL QL_G_trap_BotAllocMoveState( void ) {
	return G_Import_Syscall( BOTLIB_AI_ALLOC_MOVE_STATE );
}

/*
==============
QL_G_trap_BotFreeMoveState
==============
*/
static void QDECL QL_G_trap_BotFreeMoveState( int handle ) {
	G_Import_Syscall( BOTLIB_AI_FREE_MOVE_STATE, handle );
}

/*
==============
QL_G_trap_BotInitMoveState
==============
*/
static void QDECL QL_G_trap_BotInitMoveState( int handle, void /* struct bot_initmove_s */ *initmove ) {
	G_Import_Syscall( BOTLIB_AI_INIT_MOVE_STATE, handle, initmove );
}

/*
==============
QL_G_trap_BotChooseBestFightWeapon
==============
*/
static int QDECL QL_G_trap_BotChooseBestFightWeapon( int weaponstate, int *inventory ) {
	return G_Import_Syscall( BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON, weaponstate, inventory );
}

/*
==============
QL_G_trap_BotGetWeaponInfo
==============
*/
static void QDECL QL_G_trap_BotGetWeaponInfo( int weaponstate, int weapon, void /* struct weaponinfo_s */ *weaponinfo ) {
	G_Import_Syscall( BOTLIB_AI_GET_WEAPON_INFO, weaponstate, weapon, weaponinfo );
}

/*
==============
QL_G_trap_BotLoadWeaponWeights
==============
*/
static int QDECL QL_G_trap_BotLoadWeaponWeights( int weaponstate, char *filename ) {
	return G_Import_Syscall( BOTLIB_AI_LOAD_WEAPON_WEIGHTS, weaponstate, filename );
}

/*
==============
QL_G_trap_BotAllocWeaponState
==============
*/
static int QDECL QL_G_trap_BotAllocWeaponState( void ) {
	return G_Import_Syscall( BOTLIB_AI_ALLOC_WEAPON_STATE );
}

/*
==============
QL_G_trap_BotFreeWeaponState
==============
*/
static void QDECL QL_G_trap_BotFreeWeaponState( int weaponstate ) {
	G_Import_Syscall( BOTLIB_AI_FREE_WEAPON_STATE, weaponstate );
}

/*
==============
QL_G_trap_BotResetWeaponState
==============
*/
static void QDECL QL_G_trap_BotResetWeaponState( int weaponstate ) {
	G_Import_Syscall( BOTLIB_AI_RESET_WEAPON_STATE, weaponstate );
}

/*
==============
QL_G_trap_GeneticParentsAndChildSelection
==============
*/
static int QDECL QL_G_trap_GeneticParentsAndChildSelection( int numranks, float *ranks, int *parent1, int *parent2, int *child ) {
	return G_Import_Syscall( BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION, numranks, ranks, parent1, parent2, child );
}

/*
==============
QL_G_trap_PC_LoadSource
==============
*/
static int QDECL QL_G_trap_PC_LoadSource( const char *filename ) {
	return G_Import_Syscall( BOTLIB_PC_LOAD_SOURCE, filename );
}

/*
==============
QL_G_trap_PC_FreeSource
==============
*/
static int QDECL QL_G_trap_PC_FreeSource( int handle ) {
	return G_Import_Syscall( BOTLIB_PC_FREE_SOURCE, handle );
}

/*
==============
QL_G_trap_PC_ReadToken
==============
*/
static int QDECL QL_G_trap_PC_ReadToken( int handle, pc_token_t *pc_token ) {
	return G_Import_Syscall( BOTLIB_PC_READ_TOKEN, handle, pc_token );
}

/*
==============
QL_G_trap_PC_SourceFileAndLine
==============
*/
static int QDECL QL_G_trap_PC_SourceFileAndLine( int handle, char *filename, int *line ) {
	return G_Import_Syscall( BOTLIB_PC_SOURCE_FILE_AND_LINE, handle, filename, line );
}

/*
==============
QL_G_trap_FactoryExists
==============
*/
static int QDECL QL_G_trap_FactoryExists( const char *id ) {
	return SV_FactoryExists( id );
}

/*
==============
QL_G_trap_Memset
==============
*/
static void *QDECL QL_G_trap_Memset( void *dest, int c, int count ) {
	return memset( dest, c, count );
}

/*
==============
QL_G_trap_Memcpy
==============
*/
static void *QDECL QL_G_trap_Memcpy( void *dest, const void *src, int count ) {
	return memcpy( dest, src, count );
}

/*
==============
QL_G_trap_Strncpy
==============
*/
static char *QDECL QL_G_trap_Strncpy( char *dest, const char *src, int count ) {
	return strncpy( dest, src, count );
}

/*
==============
QL_G_trap_Sin
==============
*/
static float QDECL QL_G_trap_Sin( float x ) {
	return (float)sin( x );
}

/*
==============
QL_G_trap_Cos
==============
*/
static float QDECL QL_G_trap_Cos( float x ) {
	return (float)cos( x );
}

/*
==============
QL_G_trap_Atan2
==============
*/
static float QDECL QL_G_trap_Atan2( float y, float x ) {
	return (float)atan2( y, x );
}

/*
==============
QL_G_trap_Sqrt
==============
*/
static float QDECL QL_G_trap_Sqrt( float x ) {
	return (float)sqrt( x );
}

/*
==============
QL_G_trap_MatrixMultiply
==============
*/
static void QDECL QL_G_trap_MatrixMultiply( float in1[3][3], float in2[3][3], float out[3][3] ) {
	MatrixMultiply( in1, in2, out );
}

/*
==============
QL_G_trap_AngleVectors
==============
*/
static void QDECL QL_G_trap_AngleVectors( const vec3_t angles, vec3_t forward, vec3_t right, vec3_t up ) {
	AngleVectors( angles, forward, right, up );
}

/*
==============
QL_G_trap_PerpendicularVector
==============
*/
static void QDECL QL_G_trap_PerpendicularVector( vec3_t dst, const vec3_t src ) {
	PerpendicularVector( dst, src );
}

/*
==============
QL_G_trap_Floor
==============
*/
static float QDECL QL_G_trap_Floor( float x ) {
	return (float)floor( x );
}

/*
==============
QL_G_trap_Ceil
==============
*/
static float QDECL QL_G_trap_Ceil( float x ) {
	return (float)ceil( x );
}

/*
==============
QL_G_trap_TestPrintInt
==============
*/
static void QDECL QL_G_trap_TestPrintInt( int value ) {
	(void)value;
}

/*
==============
QL_G_trap_TestPrintFloat
==============
*/
static void QDECL QL_G_trap_TestPrintFloat( float value ) {
	(void)value;
}
