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
// sv_game.c -- interface to the game dll

#include "server.h"

#include "../game/botlib.h"
#include "../qcommon/vm_local.h"
#include <limits.h>
#include <stdint.h>
#include "../../../src-re/include/fs_imports.h"

botlib_export_t	*botlib_export;
static char	sv_gameClientConnectDenied[MAX_STRING_CHARS];

void SV_GameError( const char *string ) {
	Com_Error( ERR_DROP, "%s", string );
}

void SV_GamePrint( const char *string ) {
	Com_Printf( "%s", string );
}

// these functions must be used instead of pointer arithmetic, because
// the game allocates gentities with private information after the server shared part
int	SV_NumForGentity( sharedEntity_t *ent ) {
	int		num;

	num = ( (byte *)ent - (byte *)sv.gentities ) / sv.gentitySize;

	return num;
}

sharedEntity_t *SV_GentityNum( int num ) {
	sharedEntity_t *ent;

	ent = (sharedEntity_t *)((byte *)sv.gentities + sv.gentitySize*(num));

	return ent;
}

playerState_t *SV_GameClientNum( int num ) {
	playerState_t	*ps;

	ps = (playerState_t *)((byte *)sv.gameClients + sv.gameClientSize*(num));

	return ps;
}

svEntity_t	*SV_SvEntityForGentity( sharedEntity_t *gEnt ) {
	if ( !gEnt || gEnt->s.number < 0 || gEnt->s.number >= MAX_GENTITIES ) {
		Com_Error( ERR_DROP, "SV_SvEntityForGentity: bad gEnt" );
	}
	return &sv.svEntities[ gEnt->s.number ];
}

sharedEntity_t *SV_GEntityForSvEntity( svEntity_t *svEnt ) {
	int		num;

	num = svEnt - sv.svEntities;
	return SV_GentityNum( num );
}

/*
===============
SV_GameSendServerCommand

Sends a command string to a client
===============
*/
void SV_GameSendServerCommand( int clientNum, const char *text ) {
	if ( clientNum == -1 ) {
		SV_SendServerCommand( NULL, "%s", text );
	} else {
		if ( clientNum < 0 || clientNum >= sv_maxclients->integer ) {
			return;
		}
		SV_SendServerCommand( svs.clients + clientNum, "%s", text );	
	}
}


/*
===============
SV_GameDropClient

Disconnects the client with a message
===============
*/
void SV_GameDropClient( int clientNum, const char *reason ) {
	if ( clientNum < 0 || clientNum >= sv_maxclients->integer ) {
		return;
	}
	SV_DropClient( svs.clients + clientNum, reason );	
}


/*
=================
SV_SetBrushModel

sets mins and maxs for inline bmodels
=================
*/
void SV_SetBrushModel( sharedEntity_t *ent, const char *name ) {
	clipHandle_t	h;
	vec3_t			mins, maxs;

	if (!name) {
		Com_Error( ERR_DROP, "SV_SetBrushModel: NULL" );
	}

	if (name[0] != '*') {
		Com_Error( ERR_DROP, "SV_SetBrushModel: %s isn't a brush model", name );
	}


	ent->s.modelindex = atoi( name + 1 );

	h = CM_InlineModel( ent->s.modelindex );
	CM_ModelBounds( h, mins, maxs );
	VectorCopy (mins, ent->r.mins);
	VectorCopy (maxs, ent->r.maxs);
	ent->r.bmodel = qtrue;

	ent->r.contents = -1;		// we don't know exactly what is in the brushes

	SV_LinkEntity( ent );		// FIXME: remove
}



/*
=================
SV_inPVS

Also checks portalareas so that doors block sight
=================
*/
qboolean SV_inPVS (const vec3_t p1, const vec3_t p2)
{
	int		leafnum;
	int		cluster;
	int		area1, area2;
	byte	*mask;

	leafnum = CM_PointLeafnum (p1);
	cluster = CM_LeafCluster (leafnum);
	area1 = CM_LeafArea (leafnum);
	mask = CM_ClusterPVS (cluster);

	leafnum = CM_PointLeafnum (p2);
	cluster = CM_LeafCluster (leafnum);
	area2 = CM_LeafArea (leafnum);
	if ( mask && (!(mask[cluster>>3] & (1<<(cluster&7)) ) ) )
		return qfalse;
	if (!CM_AreasConnected (area1, area2))
		return qfalse;		// a door blocks sight
	return qtrue;
}


/*
=================
SV_inPVSIgnorePortals

Does NOT check portalareas
=================
*/
qboolean SV_inPVSIgnorePortals( const vec3_t p1, const vec3_t p2)
{
	int		leafnum;
	int		cluster;
	int		area1, area2;
	byte	*mask;

	leafnum = CM_PointLeafnum (p1);
	cluster = CM_LeafCluster (leafnum);
	area1 = CM_LeafArea (leafnum);
	mask = CM_ClusterPVS (cluster);

	leafnum = CM_PointLeafnum (p2);
	cluster = CM_LeafCluster (leafnum);
	area2 = CM_LeafArea (leafnum);

	if ( mask && (!(mask[cluster>>3] & (1<<(cluster&7)) ) ) )
		return qfalse;

	return qtrue;
}


/*
========================
SV_AdjustAreaPortalState
========================
*/
void SV_AdjustAreaPortalState( sharedEntity_t *ent, qboolean open ) {
	svEntity_t	*svEnt;

	svEnt = SV_SvEntityForGentity( ent );
	if ( svEnt->areanum2 == -1 ) {
		return;
	}
	CM_AdjustAreaPortalState( svEnt->areanum, svEnt->areanum2, open );
}


/*
==================
SV_GameAreaEntities
==================
*/
qboolean	SV_EntityContact( vec3_t mins, vec3_t maxs, const sharedEntity_t *gEnt, int capsule ) {
	const float	*origin, *angles;
	clipHandle_t	ch;
	trace_t			trace;

	// check for exact collision
	origin = gEnt->r.currentOrigin;
	angles = gEnt->r.currentAngles;

	ch = SV_ClipHandleForEntity( gEnt );
	CM_TransformedBoxTrace ( &trace, vec3_origin, vec3_origin, mins, maxs,
		ch, -1, origin, angles, capsule );

	return trace.startsolid;
}


/*
===============
SV_GetServerinfo

===============
*/
void SV_GetServerinfo( char *buffer, int bufferSize ) {
	if ( bufferSize < 1 ) {
		Com_Error( ERR_DROP, "SV_GetServerinfo: bufferSize == %i", bufferSize );
	}
	Q_strncpyz( buffer, Cvar_InfoString( CVAR_SERVERINFO ), bufferSize );
}

/*
===============
SV_LocateGameData

===============
*/
void SV_LocateGameData( sharedEntity_t *gEnts, int numGEntities, int sizeofGEntity_t,
					   playerState_t *clients, int sizeofGameClient ) {
	sv.gentities = gEnts;
	sv.gentitySize = sizeofGEntity_t;
	sv.num_entities = numGEntities;

	sv.gameClients = clients;
	sv.gameClientSize = sizeofGameClient;
}


/*
===============
SV_GetUsercmd

===============
*/
void SV_GetUsercmd( int clientNum, usercmd_t *cmd ) {
	if ( clientNum < 0 || clientNum >= sv_maxclients->integer ) {
		Com_Error( ERR_DROP, "SV_GetUsercmd: bad clientNum:%i", clientNum );
	}
	*cmd = svs.clients[clientNum].lastUsercmd;
}

/*
=============
SV_ParseSteamIdString

Parses a decimal SteamID string into two 32-bit integer parts.
=============
*/
static qboolean SV_ParseSteamIdString( const char *steamId, uint32_t *steamIdLow, uint32_t *steamIdHigh ) {
	unsigned long long value;
	const char *ch;

	if ( !steamId || !steamId[0] || !steamIdLow || !steamIdHigh ) {
		return qfalse;
	}

	value = 0ull;

	for ( ch = steamId; *ch; ++ch ) {
		if ( *ch < '0' || *ch > '9' ) {
			return qfalse;
		}

		if ( value > (ULLONG_MAX / 10ull) ) {
			return qfalse;
		}

		value *= 10ull;

		if ( value > (ULLONG_MAX - (unsigned long long)(*ch - '0')) ) {
			return qfalse;
		}

		value += (unsigned long long)(*ch - '0');
	}

	*steamIdLow = (uint32_t)( value & 0xffffffffu );
	*steamIdHigh = (uint32_t)( ( value >> 32 ) & 0xffffffffu );

	return qtrue;
}

/*
=============
SV_GetAuthResultString

Returns the userinfo result label for authentication telemetry.
=============
*/
static const char *SV_GetAuthResultString( qlAuthResult result ) {
	switch ( result ) {
		case QL_AUTH_RESULT_ACCEPTED:
		return "accepted";
		case QL_AUTH_RESULT_DENIED:
		return "denied";
		case QL_AUTH_RESULT_ERROR:
		return "error";
		case QL_AUTH_RESULT_PENDING:
		default:
		return "pending";
	}
}

/*
=============
SV_GetAuthOutcomeString

Returns the userinfo outcome label for authentication telemetry.
=============
*/
static const char *SV_GetAuthOutcomeString( qlAuthOutcome outcome ) {
	switch ( outcome ) {
		case QL_AUTH_OUTCOME_SUCCESS:
		return "success";
		case QL_AUTH_OUTCOME_RETRY:
		return "retry";
		case QL_AUTH_OUTCOME_FAILURE:
		default:
		return "failure";
	}
}

/*
=============
SV_GetClientSteamId

Writes the client's SteamID components if supplied in the userinfo.
=============
*/
static qboolean SV_GetClientSteamId( int clientNum, uint32_t *steamIdLow, uint32_t *steamIdHigh ) {
	client_t *cl;

	if ( clientNum < 0 || clientNum >= sv_maxclients->integer ) {
		return qfalse;
	}

	cl = &svs.clients[clientNum];

	#if SV_HAS_PLATFORM_AUTH
	if ( cl->platformSteamId[0] ) {
		return SV_ParseSteamIdString( cl->platformSteamId, steamIdLow, steamIdHigh );
	}
	#endif

	return qfalse;
}

/*
=============
SV_VerifyClientSteamAuth

Validates the Steam authentication token captured from the client.
=============
*/
static qboolean SV_VerifyClientSteamAuth( int clientNum ) {
	#if !SV_HAS_PLATFORM_AUTH
	client_t *cl;

	if ( clientNum < 0 || clientNum >= sv_maxclients->integer ) {
		return qfalse;
	}

	cl = &svs.clients[clientNum];
	if ( NET_IsLocalAddress( cl->netchan.remoteAddress ) ) {
		return qtrue;
	}

	return qfalse;
	#else
	ql_auth_credential_t credential;
	ql_auth_response_t response;
	client_t *cl;

	if ( clientNum < 0 || clientNum >= sv_maxclients->integer ) {
		return qfalse;
	}

	cl = &svs.clients[clientNum];

	if ( !cl->platformAuthToken[0] ) {
		if ( NET_IsLocalAddress( cl->netchan.remoteAddress ) ) {
			cl->platformAuthSucceeded = qtrue;
			return qtrue;
		}
		return qfalse;
	}

	QL_InitAuthCredential( &credential );
	Com_Memset( &response, 0, sizeof( response ) );

	if ( !QL_ParsePlatformToken( cl->platformAuthToken, QL_AUTH_CREDENTIAL_STEAM, &credential ) ) {
		return qfalse;
	}

	if ( !QL_RequestExternalAuth( &credential, &response ) ) {
		return qfalse;
	}

	cl->platformAuthSucceeded = response.result == QL_AUTH_RESULT_ACCEPTED;
	Q_strncpyz( cl->platformAuthResult, SV_GetAuthResultString( response.result ), sizeof( cl->platformAuthResult ) );
	Q_strncpyz( cl->platformAuthOutcome, SV_GetAuthOutcomeString( response.outcome ), sizeof( cl->platformAuthOutcome ) );
	Q_strncpyz( cl->platformAuthMessage, response.message, sizeof( cl->platformAuthMessage ) );

	return cl->platformAuthSucceeded;
	#endif
}

//==============================================

static int	FloatAsInt( float f ) {
	union
	{
	    int i;
	    float f;
	} temp;
	
	temp.f = f;
	return temp.i;
}

/*
====================
SV_GameSystemCallsImpl

Implements the qagame trap surface for both legacy syscall dispatch and the
native import-table bridge.
====================
*/
//rcg010207 - see my comments in VM_DllSyscall(), in qcommon/vm.c ...
#if ((defined __linux__) && (defined __powerpc__))
#define VMA(x) ((void *) args[x])
#else
#define	VMA(x) VM_ArgPtr(args[x])
#endif

#define	VMF(x)	((float *)args)[x]

static int SV_GameSystemCallsImpl( int *args, qboolean logContract ) {
	if ( logContract ) {
		SyscallContract_LogEvent( "shim-game", "qagame", args, SYSCALL_CONTRACT_MAX_ARGS );
	}

	switch( args[0] ) {
	case G_PRINT:
		Com_Printf( "%s", VMA(1) );
		return 0;
	case G_ERROR:
		Com_Error( ERR_DROP, "%s", VMA(1) );
		return 0;
	case G_MILLISECONDS:
		return Sys_Milliseconds();
	case G_CVAR_REGISTER:
		Cvar_Register( VMA(1), VMA(2), VMA(3), args[4] ); 
		return 0;
	case G_CVAR_UPDATE:
		Cvar_Update( VMA(1) );
		return 0;
	case G_CVAR_SET:
		Cvar_Set( (const char *)VMA(1), (const char *)VMA(2) );
		return 0;
	case G_CVAR_VARIABLE_INTEGER_VALUE:
		return Cvar_VariableIntegerValue( (const char *)VMA(1) );
	case G_CVAR_VARIABLE_STRING_BUFFER:
		Cvar_VariableStringBuffer( VMA(1), VMA(2), args[3] );
		return 0;
	case G_ARGC:
		return Cmd_Argc();
	case G_ARGV:
		Cmd_ArgvBuffer( args[1], VMA(2), args[3] );
		return 0;
	case G_SEND_CONSOLE_COMMAND:
		Cbuf_ExecuteText( args[1], VMA(2) );
		return 0;

	case G_FS_FOPEN_FILE:
		return qlr_fs_imports.fopen_file_by_mode( VMA(1), VMA(2), args[3] );
	case G_FS_READ:
		qlr_fs_imports.read( VMA(1), args[2], args[3] );
		return 0;
	case G_FS_WRITE:
		qlr_fs_imports.write( VMA(1), args[2], args[3] );
		return 0;
	case G_FS_FCLOSE_FILE:
		qlr_fs_imports.fclose_file( args[1] );
		return 0;
	case G_FS_GETFILELIST:
		return qlr_fs_imports.get_file_list( VMA(1), VMA(2), VMA(3), args[4] );
	case G_FS_SEEK:
		return qlr_fs_imports.seek( args[1], args[2], args[3] );
	case G_LOCATE_GAME_DATA:
		SV_LocateGameData( VMA(1), args[2], args[3], VMA(4), args[5] );
		return 0;
	case G_DROP_CLIENT:
		SV_GameDropClient( args[1], VMA(2) );
		return 0;
	case G_SEND_SERVER_COMMAND:
		SV_GameSendServerCommand( args[1], VMA(2) );
		return 0;
	case G_LINKENTITY:
		SV_LinkEntity( VMA(1) );
		return 0;
	case G_UNLINKENTITY:
		SV_UnlinkEntity( VMA(1) );
		return 0;
	case G_ENTITIES_IN_BOX:
		return SV_AreaEntities( VMA(1), VMA(2), VMA(3), args[4] );
	case G_ENTITY_CONTACT:
		return SV_EntityContact( VMA(1), VMA(2), VMA(3), /*int capsule*/ qfalse ) ? qtrue : qfalse;
	case G_ENTITY_CONTACTCAPSULE:
		return SV_EntityContact( VMA(1), VMA(2), VMA(3), /*int capsule*/ qtrue ) ? qtrue : qfalse;
	case G_TRACE:
		SV_Trace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], /*int capsule*/ qfalse );
		return 0;
	case G_TRACECAPSULE:
		SV_Trace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], /*int capsule*/ qtrue );
		return 0;
	case G_POINT_CONTENTS:
		return SV_PointContents( VMA(1), args[2] );
	case G_SET_BRUSH_MODEL:
		SV_SetBrushModel( VMA(1), VMA(2) );
		return 0;
	case G_IN_PVS:
		return SV_inPVS( VMA(1), VMA(2) ) ? qtrue : qfalse;
	case G_IN_PVS_IGNORE_PORTALS:
		return SV_inPVSIgnorePortals( VMA(1), VMA(2) ) ? qtrue : qfalse;

	case G_SET_CONFIGSTRING:
		SV_SetConfigstring( args[1], VMA(2) );
		return 0;
	case G_GET_CONFIGSTRING:
		SV_GetConfigstring( args[1], VMA(2), args[3] );
		return 0;
	case G_SET_USERINFO:
		SV_SetUserinfo( args[1], VMA(2) );
		return 0;
	case G_GET_USERINFO:
		SV_GetUserinfo( args[1], VMA(2), args[3] );
		return 0;
	case G_GET_SERVERINFO:
		SV_GetServerinfo( VMA(1), args[2] );
		return 0;
	case G_STEAMID_QUERY:
		return SV_GetClientSteamId( args[1], (uint32_t *)VMA(2), (uint32_t *)VMA(3) ) ? qtrue : qfalse;
	case G_STEAM_AUTH_VALIDATE:
		return SV_VerifyClientSteamAuth( args[1] ) ? qtrue : qfalse;
	case G_RANK_BEGIN:
		SV_RankBegin( VMA(1) );
		return 0;
	case G_RANK_POLL:
		SV_RankPoll();
		return 0;
	case G_RANK_CHECK_INIT:
		return SV_RankCheckInit();
	case G_RANK_ACTIVE:
		return SV_RankActive();
	case G_RANK_USER_STATUS:
		return SV_RankUserStatus( args[1] );
	case G_RANK_USER_RESET:
		SV_RankUserReset( args[1] );
		return 0;
	case G_RANK_REPORT_INT:
		SV_RankReportInt( args[1], args[2], args[3], args[4], args[5] );
		return 0;
	case G_RANK_REPORT_STR:
		SV_RankReportStr( args[1], args[2], args[3], VMA(4) );
		return 0;
	case G_ADJUST_AREA_PORTAL_STATE:
		SV_AdjustAreaPortalState( VMA(1), args[2] ? qtrue : qfalse );
		return 0;
	case G_AREAS_CONNECTED:
		return CM_AreasConnected( args[1], args[2] );

	case G_BOT_ALLOCATE_CLIENT:
		return SV_BotAllocateClient();
	case G_BOT_FREE_CLIENT:
		SV_BotFreeClient( args[1] );
		return 0;

	case G_GET_USERCMD:
		SV_GetUsercmd( args[1], VMA(2) );
		return 0;
	case G_GET_ENTITY_TOKEN:
		{
			const char	*s;

			s = COM_Parse( &sv.entityParsePoint );
			Q_strncpyz( VMA(1), s, args[2] );
			if ( !sv.entityParsePoint && !s[0] ) {
				return qfalse;
			} else {
				return qtrue;
			}
		}

	case G_DEBUG_POLYGON_CREATE:
		return BotImport_DebugPolygonCreate( args[1], args[2], VMA(3) );
	case G_DEBUG_POLYGON_DELETE:
		BotImport_DebugPolygonDelete( args[1] );
		return 0;
	case G_REAL_TIME:
		return Com_RealTime( VMA(1) );
	case G_SNAPVECTOR:
		Sys_SnapVector( VMA(1) );
		return 0;

		//====================================

	case BOTLIB_SETUP:
		return SV_BotLibSetup();
	case BOTLIB_SHUTDOWN:
		return SV_BotLibShutdown();
	case BOTLIB_LIBVAR_SET:
		return botlib_export->BotLibVarSet( VMA(1), VMA(2) );
	case BOTLIB_LIBVAR_GET:
		return botlib_export->BotLibVarGet( VMA(1), VMA(2), args[3] );

	case BOTLIB_PC_ADD_GLOBAL_DEFINE:
		return botlib_export->PC_AddGlobalDefine( VMA(1) );
	case BOTLIB_PC_LOAD_SOURCE:
		return botlib_export->PC_LoadSourceHandle( VMA(1) );
	case BOTLIB_PC_FREE_SOURCE:
		return botlib_export->PC_FreeSourceHandle( args[1] );
	case BOTLIB_PC_READ_TOKEN:
		return botlib_export->PC_ReadTokenHandle( args[1], VMA(2) );
	case BOTLIB_PC_SOURCE_FILE_AND_LINE:
		return botlib_export->PC_SourceFileAndLine( args[1], VMA(2), VMA(3) );

	case BOTLIB_START_FRAME:
		return botlib_export->BotLibStartFrame( VMF(1) );
	case BOTLIB_LOAD_MAP:
		return botlib_export->BotLibLoadMap( VMA(1) );
	case BOTLIB_UPDATENTITY:
		return botlib_export->BotLibUpdateEntity( args[1], VMA(2) );
	case BOTLIB_TEST:
		return botlib_export->Test( args[1], VMA(2), VMA(3), VMA(4) );

	case BOTLIB_GET_SNAPSHOT_ENTITY:
		return SV_BotGetSnapshotEntity( args[1], args[2] );
	case BOTLIB_GET_CONSOLE_MESSAGE:
		return SV_BotGetConsoleMessage( args[1], VMA(2), args[3] );
	case BOTLIB_USER_COMMAND:
		SV_ClientThink( &svs.clients[args[1]], VMA(2) );
		return 0;

	case BOTLIB_AAS_BBOX_AREAS:
		return botlib_export->aas.AAS_BBoxAreas( VMA(1), VMA(2), VMA(3), args[4] );
	case BOTLIB_AAS_AREA_INFO:
		return botlib_export->aas.AAS_AreaInfo( args[1], VMA(2) );
	case BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL:
		return botlib_export->aas.AAS_AlternativeRouteGoals( VMA(1), args[2], VMA(3), args[4], args[5], VMA(6), args[7], args[8] );
	case BOTLIB_AAS_ENTITY_INFO:
		botlib_export->aas.AAS_EntityInfo( args[1], VMA(2) );
		return 0;

	case BOTLIB_AAS_INITIALIZED:
		return botlib_export->aas.AAS_Initialized();
	case BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX:
		botlib_export->aas.AAS_PresenceTypeBoundingBox( args[1], VMA(2), VMA(3) );
		return 0;
	case BOTLIB_AAS_TIME:
		return FloatAsInt( botlib_export->aas.AAS_Time() );

	case BOTLIB_AAS_POINT_AREA_NUM:
		return botlib_export->aas.AAS_PointAreaNum( VMA(1) );
	case BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX:
		return botlib_export->aas.AAS_PointReachabilityAreaIndex( VMA(1) );
	case BOTLIB_AAS_TRACE_AREAS:
		return botlib_export->aas.AAS_TraceAreas( VMA(1), VMA(2), VMA(3), VMA(4), args[5] );

	case BOTLIB_AAS_POINT_CONTENTS:
		return botlib_export->aas.AAS_PointContents( VMA(1) );
	case BOTLIB_AAS_NEXT_BSP_ENTITY:
		return botlib_export->aas.AAS_NextBSPEntity( args[1] );
	case BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY:
		return botlib_export->aas.AAS_ValueForBSPEpairKey( args[1], VMA(2), VMA(3), args[4] );
	case BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY:
		return botlib_export->aas.AAS_VectorForBSPEpairKey( args[1], VMA(2), VMA(3) );
	case BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY:
		return botlib_export->aas.AAS_FloatForBSPEpairKey( args[1], VMA(2), VMA(3) );
	case BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY:
		return botlib_export->aas.AAS_IntForBSPEpairKey( args[1], VMA(2), VMA(3) );

	case BOTLIB_AAS_AREA_REACHABILITY:
		return botlib_export->aas.AAS_AreaReachability( args[1] );

	case BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA:
		return botlib_export->aas.AAS_AreaTravelTimeToGoalArea( args[1], VMA(2), args[3], args[4] );
	case BOTLIB_AAS_ENABLE_ROUTING_AREA:
		return botlib_export->aas.AAS_EnableRoutingArea( args[1], args[2] );
	case BOTLIB_AAS_PREDICT_ROUTE:
		return botlib_export->aas.AAS_PredictRoute( VMA(1), args[2], VMA(3), args[4], args[5], args[6], args[7], args[8], args[9], args[10], args[11] );

	case BOTLIB_AAS_SWIMMING:
		return botlib_export->aas.AAS_Swimming( VMA(1) );
	case BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT:
		return botlib_export->aas.AAS_PredictClientMovement( VMA(1), args[2], VMA(3), args[4], args[5],
			VMA(6), VMA(7), args[8], args[9], VMF(10), args[11], args[12], args[13] );

	case BOTLIB_EA_SAY:
		botlib_export->ea.EA_Say( args[1], VMA(2) );
		return 0;
	case BOTLIB_EA_SAY_TEAM:
		botlib_export->ea.EA_SayTeam( args[1], VMA(2) );
		return 0;
	case BOTLIB_EA_COMMAND:
		botlib_export->ea.EA_Command( args[1], VMA(2) );
		return 0;

	case BOTLIB_EA_ACTION:
		botlib_export->ea.EA_Action( args[1], args[2] );
		break;
	case BOTLIB_EA_GESTURE:
		botlib_export->ea.EA_Gesture( args[1] );
		return 0;
	case BOTLIB_EA_TALK:
		botlib_export->ea.EA_Talk( args[1] );
		return 0;
	case BOTLIB_EA_ATTACK:
		botlib_export->ea.EA_Attack( args[1] );
		return 0;
	case BOTLIB_EA_USE:
		botlib_export->ea.EA_Use( args[1] );
		return 0;
	case BOTLIB_EA_RESPAWN:
		botlib_export->ea.EA_Respawn( args[1] );
		return 0;
	case BOTLIB_EA_CROUCH:
		botlib_export->ea.EA_Crouch( args[1] );
		return 0;
	case BOTLIB_EA_MOVE_UP:
		botlib_export->ea.EA_MoveUp( args[1] );
		return 0;
	case BOTLIB_EA_MOVE_DOWN:
		botlib_export->ea.EA_MoveDown( args[1] );
		return 0;
	case BOTLIB_EA_MOVE_FORWARD:
		botlib_export->ea.EA_MoveForward( args[1] );
		return 0;
	case BOTLIB_EA_MOVE_BACK:
		botlib_export->ea.EA_MoveBack( args[1] );
		return 0;
	case BOTLIB_EA_MOVE_LEFT:
		botlib_export->ea.EA_MoveLeft( args[1] );
		return 0;
	case BOTLIB_EA_MOVE_RIGHT:
		botlib_export->ea.EA_MoveRight( args[1] );
		return 0;

	case BOTLIB_EA_SELECT_WEAPON:
		botlib_export->ea.EA_SelectWeapon( args[1], args[2] );
		return 0;
	case BOTLIB_EA_JUMP:
		botlib_export->ea.EA_Jump( args[1] );
		return 0;
	case BOTLIB_EA_DELAYED_JUMP:
		botlib_export->ea.EA_DelayedJump( args[1] );
		return 0;
	case BOTLIB_EA_MOVE:
		botlib_export->ea.EA_Move( args[1], VMA(2), VMF(3) );
		return 0;
	case BOTLIB_EA_VIEW:
		botlib_export->ea.EA_View( args[1], VMA(2) );
		return 0;

	case BOTLIB_EA_END_REGULAR:
		botlib_export->ea.EA_EndRegular( args[1], VMF(2) );
		return 0;
	case BOTLIB_EA_GET_INPUT:
		botlib_export->ea.EA_GetInput( args[1], VMF(2), VMA(3) );
		return 0;
	case BOTLIB_EA_RESET_INPUT:
		botlib_export->ea.EA_ResetInput( args[1] );
		return 0;

	case BOTLIB_AI_LOAD_CHARACTER:
		return botlib_export->ai.BotLoadCharacter( VMA(1), VMF(2) );
	case BOTLIB_AI_FREE_CHARACTER:
		botlib_export->ai.BotFreeCharacter( args[1] );
		return 0;
	case BOTLIB_AI_CHARACTERISTIC_FLOAT:
		return FloatAsInt( botlib_export->ai.Characteristic_Float( args[1], args[2] ) );
	case BOTLIB_AI_CHARACTERISTIC_BFLOAT:
		return FloatAsInt( botlib_export->ai.Characteristic_BFloat( args[1], args[2], VMF(3), VMF(4) ) );
	case BOTLIB_AI_CHARACTERISTIC_INTEGER:
		return botlib_export->ai.Characteristic_Integer( args[1], args[2] );
	case BOTLIB_AI_CHARACTERISTIC_BINTEGER:
		return botlib_export->ai.Characteristic_BInteger( args[1], args[2], args[3], args[4] );
	case BOTLIB_AI_CHARACTERISTIC_STRING:
		botlib_export->ai.Characteristic_String( args[1], args[2], VMA(3), args[4] );
		return 0;

	case BOTLIB_AI_ALLOC_CHAT_STATE:
		return botlib_export->ai.BotAllocChatState();
	case BOTLIB_AI_FREE_CHAT_STATE:
		botlib_export->ai.BotFreeChatState( args[1] );
		return 0;
	case BOTLIB_AI_QUEUE_CONSOLE_MESSAGE:
		botlib_export->ai.BotQueueConsoleMessage( args[1], args[2], VMA(3) );
		return 0;
	case BOTLIB_AI_REMOVE_CONSOLE_MESSAGE:
		botlib_export->ai.BotRemoveConsoleMessage( args[1], args[2] );
		return 0;
	case BOTLIB_AI_NEXT_CONSOLE_MESSAGE:
		return botlib_export->ai.BotNextConsoleMessage( args[1], VMA(2) );
	case BOTLIB_AI_NUM_CONSOLE_MESSAGE:
		return botlib_export->ai.BotNumConsoleMessages( args[1] );
	case BOTLIB_AI_INITIAL_CHAT:
		botlib_export->ai.BotInitialChat( args[1], VMA(2), args[3], VMA(4), VMA(5), VMA(6), VMA(7), VMA(8), VMA(9), VMA(10), VMA(11) );
		return 0;
	case BOTLIB_AI_NUM_INITIAL_CHATS:
		return botlib_export->ai.BotNumInitialChats( args[1], VMA(2) );
	case BOTLIB_AI_REPLY_CHAT:
		return botlib_export->ai.BotReplyChat( args[1], VMA(2), args[3], args[4], VMA(5), VMA(6), VMA(7), VMA(8), VMA(9), VMA(10), VMA(11), VMA(12) );
	case BOTLIB_AI_CHAT_LENGTH:
		return botlib_export->ai.BotChatLength( args[1] );
	case BOTLIB_AI_ENTER_CHAT:
		botlib_export->ai.BotEnterChat( args[1], args[2], args[3] );
		return 0;
	case BOTLIB_AI_GET_CHAT_MESSAGE:
		botlib_export->ai.BotGetChatMessage( args[1], VMA(2), args[3] );
		return 0;
	case BOTLIB_AI_STRING_CONTAINS:
		return botlib_export->ai.StringContains( VMA(1), VMA(2), args[3] );
	case BOTLIB_AI_FIND_MATCH:
		return botlib_export->ai.BotFindMatch( VMA(1), VMA(2), args[3] );
	case BOTLIB_AI_MATCH_VARIABLE:
		botlib_export->ai.BotMatchVariable( VMA(1), args[2], VMA(3), args[4] );
		return 0;
	case BOTLIB_AI_UNIFY_WHITE_SPACES:
		botlib_export->ai.UnifyWhiteSpaces( VMA(1) );
		return 0;
	case BOTLIB_AI_REPLACE_SYNONYMS:
		botlib_export->ai.BotReplaceSynonyms( VMA(1), args[2] );
		return 0;
	case BOTLIB_AI_LOAD_CHAT_FILE:
		return botlib_export->ai.BotLoadChatFile( args[1], VMA(2), VMA(3) );
	case BOTLIB_AI_SET_CHAT_GENDER:
		botlib_export->ai.BotSetChatGender( args[1], args[2] );
		return 0;
	case BOTLIB_AI_SET_CHAT_NAME:
		botlib_export->ai.BotSetChatName( args[1], VMA(2), args[3] );
		return 0;

	case BOTLIB_AI_RESET_GOAL_STATE:
		botlib_export->ai.BotResetGoalState( args[1] );
		return 0;
	case BOTLIB_AI_RESET_AVOID_GOALS:
		botlib_export->ai.BotResetAvoidGoals( args[1] );
		return 0;
	case BOTLIB_AI_REMOVE_FROM_AVOID_GOALS:
		botlib_export->ai.BotRemoveFromAvoidGoals( args[1], args[2] );
		return 0;
	case BOTLIB_AI_PUSH_GOAL:
		botlib_export->ai.BotPushGoal( args[1], VMA(2) );
		return 0;
	case BOTLIB_AI_POP_GOAL:
		botlib_export->ai.BotPopGoal( args[1] );
		return 0;
	case BOTLIB_AI_EMPTY_GOAL_STACK:
		botlib_export->ai.BotEmptyGoalStack( args[1] );
		return 0;
	case BOTLIB_AI_DUMP_AVOID_GOALS:
		botlib_export->ai.BotDumpAvoidGoals( args[1] );
		return 0;
	case BOTLIB_AI_DUMP_GOAL_STACK:
		botlib_export->ai.BotDumpGoalStack( args[1] );
		return 0;
	case BOTLIB_AI_GOAL_NAME:
		botlib_export->ai.BotGoalName( args[1], VMA(2), args[3] );
		return 0;
	case BOTLIB_AI_GET_TOP_GOAL:
		return botlib_export->ai.BotGetTopGoal( args[1], VMA(2) );
	case BOTLIB_AI_GET_SECOND_GOAL:
		return botlib_export->ai.BotGetSecondGoal( args[1], VMA(2) );
	case BOTLIB_AI_CHOOSE_LTG_ITEM:
		return botlib_export->ai.BotChooseLTGItem( args[1], VMA(2), VMA(3), args[4] );
	case BOTLIB_AI_CHOOSE_NBG_ITEM:
		return botlib_export->ai.BotChooseNBGItem( args[1], VMA(2), VMA(3), args[4], VMA(5), VMF(6) );
	case BOTLIB_AI_TOUCHING_GOAL:
		return botlib_export->ai.BotTouchingGoal( VMA(1), VMA(2) );
	case BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE:
		return botlib_export->ai.BotItemGoalInVisButNotVisible( args[1], VMA(2), VMA(3), VMA(4) );
	case BOTLIB_AI_GET_LEVEL_ITEM_GOAL:
		return botlib_export->ai.BotGetLevelItemGoal( args[1], VMA(2), VMA(3) );
	case BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL:
		return botlib_export->ai.BotGetNextCampSpotGoal( args[1], VMA(2) );
	case BOTLIB_AI_GET_MAP_LOCATION_GOAL:
		return botlib_export->ai.BotGetMapLocationGoal( VMA(1), VMA(2) );
	case BOTLIB_AI_AVOID_GOAL_TIME:
		return FloatAsInt( botlib_export->ai.BotAvoidGoalTime( args[1], args[2] ) );
	case BOTLIB_AI_SET_AVOID_GOAL_TIME:
		botlib_export->ai.BotSetAvoidGoalTime( args[1], args[2], VMF(3));
		return 0;
	case BOTLIB_AI_INIT_LEVEL_ITEMS:
		botlib_export->ai.BotInitLevelItems();
		return 0;
	case BOTLIB_AI_UPDATE_ENTITY_ITEMS:
		botlib_export->ai.BotUpdateEntityItems();
		return 0;
	case BOTLIB_AI_LOAD_ITEM_WEIGHTS:
		return botlib_export->ai.BotLoadItemWeights( args[1], VMA(2) );
	case BOTLIB_AI_FREE_ITEM_WEIGHTS:
		botlib_export->ai.BotFreeItemWeights( args[1] );
		return 0;
	case BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC:
		botlib_export->ai.BotInterbreedGoalFuzzyLogic( args[1], args[2], args[3] );
		return 0;
	case BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC:
		botlib_export->ai.BotSaveGoalFuzzyLogic( args[1], VMA(2) );
		return 0;
	case BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC:
		botlib_export->ai.BotMutateGoalFuzzyLogic( args[1], VMF(2) );
		return 0;
	case BOTLIB_AI_ALLOC_GOAL_STATE:
		return botlib_export->ai.BotAllocGoalState( args[1] );
	case BOTLIB_AI_FREE_GOAL_STATE:
		botlib_export->ai.BotFreeGoalState( args[1] );
		return 0;

	case BOTLIB_AI_RESET_MOVE_STATE:
		botlib_export->ai.BotResetMoveState( args[1] );
		return 0;
	case BOTLIB_AI_ADD_AVOID_SPOT:
		botlib_export->ai.BotAddAvoidSpot( args[1], VMA(2), VMF(3), args[4] );
		return 0;
	case BOTLIB_AI_MOVE_TO_GOAL:
		botlib_export->ai.BotMoveToGoal( VMA(1), args[2], VMA(3), args[4] );
		return 0;
	case BOTLIB_AI_MOVE_IN_DIRECTION:
		return botlib_export->ai.BotMoveInDirection( args[1], VMA(2), VMF(3), args[4] );
	case BOTLIB_AI_RESET_AVOID_REACH:
		botlib_export->ai.BotResetAvoidReach( args[1] );
		return 0;
	case BOTLIB_AI_RESET_LAST_AVOID_REACH:
		botlib_export->ai.BotResetLastAvoidReach( args[1] );
		return 0;
	case BOTLIB_AI_REACHABILITY_AREA:
		return botlib_export->ai.BotReachabilityArea( VMA(1), args[2] );
	case BOTLIB_AI_MOVEMENT_VIEW_TARGET:
		return botlib_export->ai.BotMovementViewTarget( args[1], VMA(2), args[3], VMF(4), VMA(5) );
	case BOTLIB_AI_PREDICT_VISIBLE_POSITION:
		return botlib_export->ai.BotPredictVisiblePosition( VMA(1), args[2], VMA(3), args[4], VMA(5) );
	case BOTLIB_AI_ALLOC_MOVE_STATE:
		return botlib_export->ai.BotAllocMoveState();
	case BOTLIB_AI_FREE_MOVE_STATE:
		botlib_export->ai.BotFreeMoveState( args[1] );
		return 0;
	case BOTLIB_AI_INIT_MOVE_STATE:
		botlib_export->ai.BotInitMoveState( args[1], VMA(2) );
		return 0;

	case BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON:
		return botlib_export->ai.BotChooseBestFightWeapon( args[1], VMA(2) );
	case BOTLIB_AI_GET_WEAPON_INFO:
		botlib_export->ai.BotGetWeaponInfo( args[1], args[2], VMA(3) );
		return 0;
	case BOTLIB_AI_LOAD_WEAPON_WEIGHTS:
		return botlib_export->ai.BotLoadWeaponWeights( args[1], VMA(2) );
	case BOTLIB_AI_ALLOC_WEAPON_STATE:
		return botlib_export->ai.BotAllocWeaponState();
	case BOTLIB_AI_FREE_WEAPON_STATE:
		botlib_export->ai.BotFreeWeaponState( args[1] );
		return 0;
	case BOTLIB_AI_RESET_WEAPON_STATE:
		botlib_export->ai.BotResetWeaponState( args[1] );
		return 0;

	case BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION:
		return botlib_export->ai.GeneticParentsAndChildSelection(args[1], VMA(2), VMA(3), VMA(4), VMA(5));

	case TRAP_MEMSET:
		Com_Memset( VMA(1), args[2], args[3] );
		return 0;

	case TRAP_MEMCPY:
		Com_Memcpy( VMA(1), VMA(2), args[3] );
		return 0;

	case TRAP_STRNCPY:
		return (int)strncpy( VMA(1), VMA(2), args[3] );

	case TRAP_SIN:
		return FloatAsInt( sin( VMF(1) ) );

	case TRAP_COS:
		return FloatAsInt( cos( VMF(1) ) );

	case TRAP_ATAN2:
		return FloatAsInt( atan2( VMF(1), VMF(2) ) );

	case TRAP_SQRT:
		return FloatAsInt( sqrt( VMF(1) ) );

	case TRAP_MATRIXMULTIPLY:
		MatrixMultiply( VMA(1), VMA(2), VMA(3) );
		return 0;

	case TRAP_ANGLEVECTORS:
		AngleVectors( VMA(1), VMA(2), VMA(3), VMA(4) );
		return 0;

	case TRAP_PERPENDICULARVECTOR:
		PerpendicularVector( VMA(1), VMA(2) );
		return 0;

	case TRAP_FLOOR:
		return FloatAsInt( floor( VMF(1) ) );

	case TRAP_CEIL:
		return FloatAsInt( ceil( VMF(1) ) );


	default:
		Com_Error( ERR_DROP, "Bad game system trap: %i", args[0] );
	}
	return -1;
}

/*
====================
SV_GameSystemCalls
====================
*/
int SV_GameSystemCalls( int *args ) {
	return SV_GameSystemCallsImpl( args, qtrue );
}

/*
====================
G_Import_Syscall
====================
*/
static int QDECL G_Import_Syscall( int arg, ... ) {
#if ((defined __linux__) && (defined __powerpc__))
	int args[SYSCALL_CONTRACT_MAX_ARGS];
	int i;
	va_list ap;

	args[0] = arg;

	va_start(ap, arg);
	for (i = 1; i < SYSCALL_CONTRACT_MAX_ARGS; i++) {
		args[i] = va_arg(ap, int);
	}
	va_end(ap);

	return SV_GameSystemCallsImpl( args, qfalse );
#else
	return SV_GameSystemCallsImpl( &arg, qfalse );
#endif
}

#include "ql_game_imports.inc"

typedef void (QDECL *ql_import_f)( void );

static ql_import_f ql_game_imports[GAME_NATIVE_IMPORT_COUNT];

static const ql_import_f ql_game_compat_imports[GAME_LEGACY_IMPORT_COUNT] = {
	[G_PRINT] = (ql_import_f)QL_G_trap_Printf,
	[G_ERROR] = (ql_import_f)QL_G_trap_Error,
	[G_MILLISECONDS] = (ql_import_f)QL_G_trap_Milliseconds,
	[G_ARGC] = (ql_import_f)QL_G_trap_Argc,
	[G_ARGV] = (ql_import_f)QL_G_trap_Argv,
	[G_FS_FOPEN_FILE] = (ql_import_f)QL_G_trap_FS_FOpenFile,
	[G_FS_READ] = (ql_import_f)QL_G_trap_FS_Read,
	[G_FS_WRITE] = (ql_import_f)QL_G_trap_FS_Write,
	[G_FS_FCLOSE_FILE] = (ql_import_f)QL_G_trap_FS_FCloseFile,
	[G_FS_GETFILELIST] = (ql_import_f)QL_G_trap_FS_GetFileList,
	[G_FS_SEEK] = (ql_import_f)QL_G_trap_FS_Seek,
	[G_SEND_CONSOLE_COMMAND] = (ql_import_f)QL_G_trap_SendConsoleCommand,
	[G_CVAR_REGISTER] = (ql_import_f)QL_G_trap_Cvar_Register,
	[G_CVAR_UPDATE] = (ql_import_f)QL_G_trap_Cvar_Update,
	[G_CVAR_SET] = (ql_import_f)QL_G_trap_Cvar_Set,
	[G_CVAR_VARIABLE_INTEGER_VALUE] = (ql_import_f)QL_G_trap_Cvar_VariableIntegerValue,
	[G_CVAR_VARIABLE_STRING_BUFFER] = (ql_import_f)QL_G_trap_Cvar_VariableStringBuffer,
	[G_LOCATE_GAME_DATA] = (ql_import_f)QL_G_trap_LocateGameData,
	[G_DROP_CLIENT] = (ql_import_f)QL_G_trap_DropClient,
	[G_SEND_SERVER_COMMAND] = (ql_import_f)QL_G_trap_SendServerCommand,
	[G_SET_CONFIGSTRING] = (ql_import_f)QL_G_trap_SetConfigstring,
	[G_GET_CONFIGSTRING] = (ql_import_f)QL_G_trap_GetConfigstring,
	[G_GET_USERINFO] = (ql_import_f)QL_G_trap_GetUserinfo,
	[G_SET_USERINFO] = (ql_import_f)QL_G_trap_SetUserinfo,
	[G_GET_SERVERINFO] = (ql_import_f)QL_G_trap_GetServerinfo,
	[G_STEAMID_QUERY] = (ql_import_f)QL_G_trap_GetSteamId,
	[G_STEAM_AUTH_VALIDATE] = (ql_import_f)QL_G_trap_VerifySteamAuth,
	[G_RANK_BEGIN] = (ql_import_f)QL_G_trap_RankBegin,
	[G_RANK_POLL] = (ql_import_f)QL_G_trap_RankPoll,
	[G_RANK_CHECK_INIT] = (ql_import_f)QL_G_trap_RankCheckInit,
	[G_RANK_ACTIVE] = (ql_import_f)QL_G_trap_RankActive,
	[G_RANK_USER_STATUS] = (ql_import_f)QL_G_trap_RankUserStatus,
	[G_RANK_USER_RESET] = (ql_import_f)QL_G_trap_RankUserReset,
	[G_RANK_REPORT_INT] = (ql_import_f)QL_G_trap_RankReportInt,
	[G_RANK_REPORT_STR] = (ql_import_f)QL_G_trap_RankReportStr,
	[G_SET_BRUSH_MODEL] = (ql_import_f)QL_G_trap_SetBrushModel,
	[G_TRACE] = (ql_import_f)QL_G_trap_Trace,
	[G_TRACECAPSULE] = (ql_import_f)QL_G_trap_TraceCapsule,
	[G_POINT_CONTENTS] = (ql_import_f)QL_G_trap_PointContents,
	[G_IN_PVS] = (ql_import_f)QL_G_trap_InPVS,
	[G_IN_PVS_IGNORE_PORTALS] = (ql_import_f)QL_G_trap_InPVSIgnorePortals,
	[G_ADJUST_AREA_PORTAL_STATE] = (ql_import_f)QL_G_trap_AdjustAreaPortalState,
	[G_AREAS_CONNECTED] = (ql_import_f)QL_G_trap_AreasConnected,
	[G_LINKENTITY] = (ql_import_f)QL_G_trap_LinkEntity,
	[G_UNLINKENTITY] = (ql_import_f)QL_G_trap_UnlinkEntity,
	[G_ENTITIES_IN_BOX] = (ql_import_f)QL_G_trap_EntitiesInBox,
	[G_ENTITY_CONTACT] = (ql_import_f)QL_G_trap_EntityContact,
	[G_ENTITY_CONTACTCAPSULE] = (ql_import_f)QL_G_trap_EntityContactCapsule,
	[G_BOT_ALLOCATE_CLIENT] = (ql_import_f)QL_G_trap_BotAllocateClient,
	[G_BOT_FREE_CLIENT] = (ql_import_f)QL_G_trap_BotFreeClient,
	[G_GET_USERCMD] = (ql_import_f)QL_G_trap_GetUsercmd,
	[G_GET_ENTITY_TOKEN] = (ql_import_f)QL_G_trap_GetEntityToken,
	[G_DEBUG_POLYGON_CREATE] = (ql_import_f)QL_G_trap_DebugPolygonCreate,
	[G_DEBUG_POLYGON_DELETE] = (ql_import_f)QL_G_trap_DebugPolygonDelete,
	[G_REAL_TIME] = (ql_import_f)QL_G_trap_RealTime,
	[G_SNAPVECTOR] = (ql_import_f)QL_G_trap_SnapVector,
	[BOTLIB_SETUP] = (ql_import_f)QL_G_trap_BotLibSetup,
	[BOTLIB_SHUTDOWN] = (ql_import_f)QL_G_trap_BotLibShutdown,
	[BOTLIB_LIBVAR_SET] = (ql_import_f)QL_G_trap_BotLibVarSet,
	[BOTLIB_LIBVAR_GET] = (ql_import_f)QL_G_trap_BotLibVarGet,
	[BOTLIB_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_G_trap_BotLibDefine,
	[BOTLIB_START_FRAME] = (ql_import_f)QL_G_trap_BotLibStartFrame,
	[BOTLIB_LOAD_MAP] = (ql_import_f)QL_G_trap_BotLibLoadMap,
	[BOTLIB_UPDATENTITY] = (ql_import_f)QL_G_trap_BotLibUpdateEntity,
	[BOTLIB_TEST] = (ql_import_f)QL_G_trap_BotLibTest,
	[BOTLIB_GET_SNAPSHOT_ENTITY] = (ql_import_f)QL_G_trap_BotGetSnapshotEntity,
	[BOTLIB_GET_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotGetServerCommand,
	[BOTLIB_USER_COMMAND] = (ql_import_f)QL_G_trap_BotUserCommand,
	[BOTLIB_AAS_ENTITY_INFO] = (ql_import_f)QL_G_trap_AAS_EntityInfo,
	[BOTLIB_AAS_INITIALIZED] = (ql_import_f)QL_G_trap_AAS_Initialized,
	[BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX] = (ql_import_f)QL_G_trap_AAS_PresenceTypeBoundingBox,
	[BOTLIB_AAS_TIME] = (ql_import_f)QL_G_trap_AAS_Time,
	[BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum,
	[BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX] = (ql_import_f)QL_G_trap_AAS_PointReachabilityAreaIndex,
	[BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas,
	[BOTLIB_AAS_BBOX_AREAS] = (ql_import_f)QL_G_trap_AAS_BBoxAreas,
	[BOTLIB_AAS_AREA_INFO] = (ql_import_f)QL_G_trap_AAS_AreaInfo,
	[BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents,
	[BOTLIB_AAS_NEXT_BSP_ENTITY] = (ql_import_f)QL_G_trap_AAS_NextBSPEntity,
	[BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_ValueForBSPEpairKey,
	[BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_VectorForBSPEpairKey,
	[BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_FloatForBSPEpairKey,
	[BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_IntForBSPEpairKey,
	[BOTLIB_AAS_AREA_REACHABILITY] = (ql_import_f)QL_G_trap_AAS_AreaReachability,
	[BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea,
	[BOTLIB_AAS_ENABLE_ROUTING_AREA] = (ql_import_f)QL_G_trap_AAS_EnableRoutingArea,
	[BOTLIB_AAS_PREDICT_ROUTE] = (ql_import_f)QL_G_trap_AAS_PredictRoute,
	[BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL] = (ql_import_f)QL_G_trap_AAS_AlternativeRouteGoals,
	[BOTLIB_AAS_SWIMMING] = (ql_import_f)QL_G_trap_AAS_Swimming,
	[BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT] = (ql_import_f)QL_G_trap_AAS_PredictClientMovement,
	[BOTLIB_EA_SAY] = (ql_import_f)QL_G_trap_EA_Say,
	[BOTLIB_EA_SAY_TEAM] = (ql_import_f)QL_G_trap_EA_SayTeam,
	[BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command,
	[BOTLIB_EA_ACTION] = (ql_import_f)QL_G_trap_EA_Action,
	[BOTLIB_EA_GESTURE] = (ql_import_f)QL_G_trap_EA_Gesture,
	[BOTLIB_EA_TALK] = (ql_import_f)QL_G_trap_EA_Talk,
	[BOTLIB_EA_ATTACK] = (ql_import_f)QL_G_trap_EA_Attack,
	[BOTLIB_EA_USE] = (ql_import_f)QL_G_trap_EA_Use,
	[BOTLIB_EA_RESPAWN] = (ql_import_f)QL_G_trap_EA_Respawn,
	[BOTLIB_EA_CROUCH] = (ql_import_f)QL_G_trap_EA_Crouch,
	[BOTLIB_EA_MOVE_UP] = (ql_import_f)QL_G_trap_EA_MoveUp,
	[BOTLIB_EA_MOVE_DOWN] = (ql_import_f)QL_G_trap_EA_MoveDown,
	[BOTLIB_EA_MOVE_FORWARD] = (ql_import_f)QL_G_trap_EA_MoveForward,
	[BOTLIB_EA_MOVE_BACK] = (ql_import_f)QL_G_trap_EA_MoveBack,
	[BOTLIB_EA_MOVE_LEFT] = (ql_import_f)QL_G_trap_EA_MoveLeft,
	[BOTLIB_EA_MOVE_RIGHT] = (ql_import_f)QL_G_trap_EA_MoveRight,
	[BOTLIB_EA_SELECT_WEAPON] = (ql_import_f)QL_G_trap_EA_SelectWeapon,
	[BOTLIB_EA_JUMP] = (ql_import_f)QL_G_trap_EA_Jump,
	[BOTLIB_EA_DELAYED_JUMP] = (ql_import_f)QL_G_trap_EA_DelayedJump,
	[BOTLIB_EA_MOVE] = (ql_import_f)QL_G_trap_EA_Move,
	[BOTLIB_EA_VIEW] = (ql_import_f)QL_G_trap_EA_View,
	[BOTLIB_EA_END_REGULAR] = (ql_import_f)QL_G_trap_EA_EndRegular,
	[BOTLIB_EA_GET_INPUT] = (ql_import_f)QL_G_trap_EA_GetInput,
	[BOTLIB_EA_RESET_INPUT] = (ql_import_f)QL_G_trap_EA_ResetInput,
	[BOTLIB_AI_LOAD_CHARACTER] = (ql_import_f)QL_G_trap_BotLoadCharacter,
	[BOTLIB_AI_FREE_CHARACTER] = (ql_import_f)QL_G_trap_BotFreeCharacter,
	[BOTLIB_AI_CHARACTERISTIC_FLOAT] = (ql_import_f)QL_G_trap_Characteristic_Float,
	[BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat,
	[BOTLIB_AI_CHARACTERISTIC_INTEGER] = (ql_import_f)QL_G_trap_Characteristic_Integer,
	[BOTLIB_AI_CHARACTERISTIC_BINTEGER] = (ql_import_f)QL_G_trap_Characteristic_BInteger,
	[BOTLIB_AI_CHARACTERISTIC_STRING] = (ql_import_f)QL_G_trap_Characteristic_String,
	[BOTLIB_AI_ALLOC_CHAT_STATE] = (ql_import_f)QL_G_trap_BotAllocChatState,
	[BOTLIB_AI_FREE_CHAT_STATE] = (ql_import_f)QL_G_trap_BotFreeChatState,
	[BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage,
	[BOTLIB_AI_REMOVE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotRemoveConsoleMessage,
	[BOTLIB_AI_NEXT_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNextConsoleMessage,
	[BOTLIB_AI_NUM_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNumConsoleMessages,
	[BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat,
	[BOTLIB_AI_NUM_INITIAL_CHATS] = (ql_import_f)QL_G_trap_BotNumInitialChats,
	[BOTLIB_AI_REPLY_CHAT] = (ql_import_f)QL_G_trap_BotReplyChat,
	[BOTLIB_AI_CHAT_LENGTH] = (ql_import_f)QL_G_trap_BotChatLength,
	[BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat,
	[BOTLIB_AI_GET_CHAT_MESSAGE] = (ql_import_f)QL_G_trap_BotGetChatMessage,
	[BOTLIB_AI_STRING_CONTAINS] = (ql_import_f)QL_G_trap_StringContains,
	[BOTLIB_AI_FIND_MATCH] = (ql_import_f)QL_G_trap_BotFindMatch,
	[BOTLIB_AI_MATCH_VARIABLE] = (ql_import_f)QL_G_trap_BotMatchVariable,
	[BOTLIB_AI_UNIFY_WHITE_SPACES] = (ql_import_f)QL_G_trap_UnifyWhiteSpaces,
	[BOTLIB_AI_REPLACE_SYNONYMS] = (ql_import_f)QL_G_trap_BotReplaceSynonyms,
	[BOTLIB_AI_LOAD_CHAT_FILE] = (ql_import_f)QL_G_trap_BotLoadChatFile,
	[BOTLIB_AI_SET_CHAT_GENDER] = (ql_import_f)QL_G_trap_BotSetChatGender,
	[BOTLIB_AI_SET_CHAT_NAME] = (ql_import_f)QL_G_trap_BotSetChatName,
	[BOTLIB_AI_RESET_GOAL_STATE] = (ql_import_f)QL_G_trap_BotResetGoalState,
	[BOTLIB_AI_RESET_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotResetAvoidGoals,
	[BOTLIB_AI_REMOVE_FROM_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotRemoveFromAvoidGoals,
	[BOTLIB_AI_PUSH_GOAL] = (ql_import_f)QL_G_trap_BotPushGoal,
	[BOTLIB_AI_POP_GOAL] = (ql_import_f)QL_G_trap_BotPopGoal,
	[BOTLIB_AI_EMPTY_GOAL_STACK] = (ql_import_f)QL_G_trap_BotEmptyGoalStack,
	[BOTLIB_AI_DUMP_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotDumpAvoidGoals,
	[BOTLIB_AI_DUMP_GOAL_STACK] = (ql_import_f)QL_G_trap_BotDumpGoalStack,
	[BOTLIB_AI_GOAL_NAME] = (ql_import_f)QL_G_trap_BotGoalName,
	[BOTLIB_AI_GET_TOP_GOAL] = (ql_import_f)QL_G_trap_BotGetTopGoal,
	[BOTLIB_AI_GET_SECOND_GOAL] = (ql_import_f)QL_G_trap_BotGetSecondGoal,
	[BOTLIB_AI_CHOOSE_LTG_ITEM] = (ql_import_f)QL_G_trap_BotChooseLTGItem,
	[BOTLIB_AI_CHOOSE_NBG_ITEM] = (ql_import_f)QL_G_trap_BotChooseNBGItem,
	[BOTLIB_AI_TOUCHING_GOAL] = (ql_import_f)QL_G_trap_BotTouchingGoal,
	[BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE] = (ql_import_f)QL_G_trap_BotItemGoalInVisButNotVisible,
	[BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal,
	[BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL] = (ql_import_f)QL_G_trap_BotGetNextCampSpotGoal,
	[BOTLIB_AI_GET_MAP_LOCATION_GOAL] = (ql_import_f)QL_G_trap_BotGetMapLocationGoal,
	[BOTLIB_AI_AVOID_GOAL_TIME] = (ql_import_f)QL_G_trap_BotAvoidGoalTime,
	[BOTLIB_AI_SET_AVOID_GOAL_TIME] = (ql_import_f)QL_G_trap_BotSetAvoidGoalTime,
	[BOTLIB_AI_INIT_LEVEL_ITEMS] = (ql_import_f)QL_G_trap_BotInitLevelItems,
	[BOTLIB_AI_UPDATE_ENTITY_ITEMS] = (ql_import_f)QL_G_trap_BotUpdateEntityItems,
	[BOTLIB_AI_LOAD_ITEM_WEIGHTS] = (ql_import_f)QL_G_trap_BotLoadItemWeights,
	[BOTLIB_AI_FREE_ITEM_WEIGHTS] = (ql_import_f)QL_G_trap_BotFreeItemWeights,
	[BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC] = (ql_import_f)QL_G_trap_BotInterbreedGoalFuzzyLogic,
	[BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC] = (ql_import_f)QL_G_trap_BotSaveGoalFuzzyLogic,
	[BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC] = (ql_import_f)QL_G_trap_BotMutateGoalFuzzyLogic,
	[BOTLIB_AI_ALLOC_GOAL_STATE] = (ql_import_f)QL_G_trap_BotAllocGoalState,
	[BOTLIB_AI_FREE_GOAL_STATE] = (ql_import_f)QL_G_trap_BotFreeGoalState,
	[BOTLIB_AI_RESET_MOVE_STATE] = (ql_import_f)QL_G_trap_BotResetMoveState,
	[BOTLIB_AI_ADD_AVOID_SPOT] = (ql_import_f)QL_G_trap_BotAddAvoidSpot,
	[BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal,
	[BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection,
	[BOTLIB_AI_RESET_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetAvoidReach,
	[BOTLIB_AI_RESET_LAST_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetLastAvoidReach,
	[BOTLIB_AI_REACHABILITY_AREA] = (ql_import_f)QL_G_trap_BotReachabilityArea,
	[BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget,
	[BOTLIB_AI_PREDICT_VISIBLE_POSITION] = (ql_import_f)QL_G_trap_BotPredictVisiblePosition,
	[BOTLIB_AI_ALLOC_MOVE_STATE] = (ql_import_f)QL_G_trap_BotAllocMoveState,
	[BOTLIB_AI_FREE_MOVE_STATE] = (ql_import_f)QL_G_trap_BotFreeMoveState,
	[BOTLIB_AI_INIT_MOVE_STATE] = (ql_import_f)QL_G_trap_BotInitMoveState,
	[BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON] = (ql_import_f)QL_G_trap_BotChooseBestFightWeapon,
	[BOTLIB_AI_GET_WEAPON_INFO] = (ql_import_f)QL_G_trap_BotGetWeaponInfo,
	[BOTLIB_AI_LOAD_WEAPON_WEIGHTS] = (ql_import_f)QL_G_trap_BotLoadWeaponWeights,
	[BOTLIB_AI_ALLOC_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotAllocWeaponState,
	[BOTLIB_AI_FREE_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotFreeWeaponState,
	[BOTLIB_AI_RESET_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotResetWeaponState,
	[BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION] = (ql_import_f)QL_G_trap_GeneticParentsAndChildSelection,
	[BOTLIB_PC_LOAD_SOURCE] = (ql_import_f)QL_G_trap_PC_LoadSource,
	[BOTLIB_PC_FREE_SOURCE] = (ql_import_f)QL_G_trap_PC_FreeSource,
	[BOTLIB_PC_READ_TOKEN] = (ql_import_f)QL_G_trap_PC_ReadToken,
	[BOTLIB_PC_SOURCE_FILE_AND_LINE] = (ql_import_f)QL_G_trap_PC_SourceFileAndLine,
	[TRAP_MEMSET] = (ql_import_f)QL_G_trap_Memset,
	[TRAP_MEMCPY] = (ql_import_f)QL_G_trap_Memcpy,
	[TRAP_STRNCPY] = (ql_import_f)QL_G_trap_Strncpy,
	[TRAP_SIN] = (ql_import_f)QL_G_trap_Sin,
	[TRAP_COS] = (ql_import_f)QL_G_trap_Cos,
	[TRAP_ATAN2] = (ql_import_f)QL_G_trap_Atan2,
	[TRAP_SQRT] = (ql_import_f)QL_G_trap_Sqrt,
	[TRAP_MATRIXMULTIPLY] = (ql_import_f)QL_G_trap_MatrixMultiply,
	[TRAP_ANGLEVECTORS] = (ql_import_f)QL_G_trap_AngleVectors,
	[TRAP_PERPENDICULARVECTOR] = (ql_import_f)QL_G_trap_PerpendicularVector,
	[TRAP_FLOOR] = (ql_import_f)QL_G_trap_Floor,
	[TRAP_CEIL] = (ql_import_f)QL_G_trap_Ceil,
	[TRAP_TESTPRINTINT] = (ql_import_f)QL_G_trap_TestPrintInt,
	[TRAP_TESTPRINTFLOAT] = (ql_import_f)QL_G_trap_TestPrintFloat,
};

/*
=================
SV_ClientAddSteamStat

Retail qagame calls this raw native import when medal/stat events fire. The
open backend path is still unrecovered, so keep the slot alive as a no-op.
=================
*/
static void SV_ClientAddSteamStat( int clientNum, int statIndex, int delta ) {
	(void)clientNum;
	(void)statIndex;
	(void)delta;
}

/*
=================
SV_ClientUnlockSteamAchievement

Retail qagame treats this as a fire-and-forget backend hook.
=================
*/
static void SV_ClientUnlockSteamAchievement( int clientNum, int achievementId ) {
	(void)clientNum;
	(void)achievementId;
}

/*
=================
SV_ClientHasSteamAchievement

Retail qagame probes this before firing duplicate achievement unlocks.
=================
*/
static qboolean SV_ClientHasSteamAchievement( int clientNum, int achievementId ) {
	(void)clientNum;
	(void)achievementId;
	return qfalse;
}

/*
=================
SV_SubmitMatchReport

The recovered retail qagame publishes a JSON-like match report through this
native slot. Keep the ABI stable until the backend contract is reconstructed.
=================
*/
static void SV_SubmitMatchReport( void *report ) {
	(void)report;
}

/*
=================
SV_ReportPlayerEvent

Observed HLIL calls pass a SteamID pair, the client's retail stats block, an
event label, and a JSON-like payload object.
=================
*/
static void SV_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, void *payload ) {
	(void)steamIdLow;
	(void)steamIdHigh;
	(void)clientStats;
	(void)eventName;
	(void)payload;
}

/*
=================
QL_G_trap_SubmitMatchReport
=================
*/
static void QDECL QL_G_trap_SubmitMatchReport( void *report ) {
	SV_SubmitMatchReport( report );
}

/*
=================
QL_G_trap_ReportPlayerEvent
=================
*/
static void QDECL QL_G_trap_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, void *payload ) {
	SV_ReportPlayerEvent( steamIdLow, steamIdHigh, clientStats, eventName, payload );
}

/*
=================
QL_G_trap_AddSteamStat
=================
*/
static void QDECL QL_G_trap_AddSteamStat( int clientNum, int statIndex, int delta ) {
	SV_ClientAddSteamStat( clientNum, statIndex, delta );
}

/*
=================
QL_G_trap_UnlockSteamAchievement
=================
*/
static void QDECL QL_G_trap_UnlockSteamAchievement( int clientNum, int achievementId ) {
	SV_ClientUnlockSteamAchievement( clientNum, achievementId );
}

/*
=================
QL_G_trap_HasSteamAchievement
=================
*/
static qboolean QDECL QL_G_trap_HasSteamAchievement( int clientNum, int achievementId ) {
	return SV_ClientHasSteamAchievement( clientNum, achievementId );
}

/*
=================
SV_InitGameImports

Builds the retail qagame native import slab, then appends the legacy syscall
table as a compatibility tail for source-built qagame and unrecovered slots.
=================
*/
static void SV_InitGameImports( void ) {
	Com_Memset( ql_game_imports, 0, sizeof( ql_game_imports ) );

	ql_game_imports[G_QL_IMPORT_SEND_CONSOLE_COMMAND] = (ql_import_f)QL_G_trap_SendConsoleCommand;
	ql_game_imports[G_QL_IMPORT_PRINT] = (ql_import_f)QL_G_trap_Printf;
	ql_game_imports[G_QL_IMPORT_FS_WRITE] = (ql_import_f)QL_G_trap_FS_Write;
	ql_game_imports[G_QL_IMPORT_FS_READ] = (ql_import_f)QL_G_trap_FS_Read;
	ql_game_imports[G_QL_IMPORT_FS_GETFILELIST] = (ql_import_f)QL_G_trap_FS_GetFileList;
	ql_game_imports[G_QL_IMPORT_FS_FOPEN_FILE] = (ql_import_f)QL_G_trap_FS_FOpenFile;
	ql_game_imports[G_QL_IMPORT_FS_FCLOSE_FILE] = (ql_import_f)QL_G_trap_FS_FCloseFile;
	ql_game_imports[G_QL_IMPORT_ERROR] = (ql_import_f)QL_G_trap_Error;
	ql_game_imports[G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE] = (ql_import_f)QL_G_trap_Cvar_VariableIntegerValue;
	ql_game_imports[G_QL_IMPORT_CVAR_UPDATE] = (ql_import_f)QL_G_trap_Cvar_Update;
	ql_game_imports[G_QL_IMPORT_CVAR_VARIABLE_STRING_BUFFER] = (ql_import_f)QL_G_trap_Cvar_VariableStringBuffer;
	ql_game_imports[G_QL_IMPORT_CVAR_SET] = (ql_import_f)QL_G_trap_Cvar_Set;
	ql_game_imports[G_QL_IMPORT_CVAR_REGISTER] = (ql_import_f)QL_G_trap_Cvar_Register;
	ql_game_imports[G_QL_IMPORT_ARGV] = (ql_import_f)QL_G_trap_Argv;
	ql_game_imports[G_QL_IMPORT_ARGC] = (ql_import_f)QL_G_trap_Argc;
	ql_game_imports[G_QL_IMPORT_LOCATE_GAME_DATA] = (ql_import_f)QL_G_trap_LocateGameData;
	ql_game_imports[G_QL_IMPORT_DROP_CLIENT] = (ql_import_f)QL_G_trap_DropClient;
	ql_game_imports[G_QL_IMPORT_SEND_SERVER_COMMAND] = (ql_import_f)QL_G_trap_SendServerCommand;
	ql_game_imports[G_QL_IMPORT_SET_CONFIGSTRING] = (ql_import_f)QL_G_trap_SetConfigstring;
	ql_game_imports[G_QL_IMPORT_GET_CONFIGSTRING] = (ql_import_f)QL_G_trap_GetConfigstring;
	ql_game_imports[G_QL_IMPORT_GET_USERINFO] = (ql_import_f)QL_G_trap_GetUserinfo;
	ql_game_imports[G_QL_IMPORT_SET_USERINFO] = (ql_import_f)QL_G_trap_SetUserinfo;
	ql_game_imports[G_QL_IMPORT_GET_SERVERINFO] = (ql_import_f)QL_G_trap_GetServerinfo;
	ql_game_imports[G_QL_IMPORT_SET_BRUSH_MODEL] = (ql_import_f)QL_G_trap_SetBrushModel;
	ql_game_imports[G_QL_IMPORT_TRACE] = (ql_import_f)QL_G_trap_Trace;
	ql_game_imports[G_QL_IMPORT_TRACECAPSULE] = (ql_import_f)QL_G_trap_TraceCapsule;
	ql_game_imports[G_QL_IMPORT_POINT_CONTENTS] = (ql_import_f)QL_G_trap_PointContents;
	ql_game_imports[G_QL_IMPORT_IN_PVS] = (ql_import_f)QL_G_trap_InPVS;
	ql_game_imports[G_QL_IMPORT_ADJUST_AREA_PORTAL_STATE] = (ql_import_f)QL_G_trap_AdjustAreaPortalState;
	ql_game_imports[G_QL_IMPORT_UNLINK_ENTITY] = (ql_import_f)QL_G_trap_UnlinkEntity;
	ql_game_imports[G_QL_IMPORT_LINKENTITY] = (ql_import_f)QL_G_trap_LinkEntity;
	ql_game_imports[G_QL_IMPORT_ENTITIES_IN_BOX] = (ql_import_f)QL_G_trap_EntitiesInBox;
	ql_game_imports[G_QL_IMPORT_BOT_ALLOCATE_CLIENT] = (ql_import_f)QL_G_trap_BotAllocateClient;
	ql_game_imports[G_QL_IMPORT_GET_USERCMD] = (ql_import_f)QL_G_trap_GetUsercmd;
	ql_game_imports[G_QL_IMPORT_GET_ENTITY_TOKEN] = (ql_import_f)QL_G_trap_GetEntityToken;
	ql_game_imports[G_QL_IMPORT_BOTLIB_SETUP] = (ql_import_f)QL_G_trap_BotLibSetup;
	ql_game_imports[G_QL_IMPORT_BOTLIB_SHUTDOWN] = (ql_import_f)QL_G_trap_BotLibShutdown;
	ql_game_imports[G_QL_IMPORT_BOTLIB_LIBVAR_SET] = (ql_import_f)QL_G_trap_BotLibVarSet;
	ql_game_imports[G_QL_IMPORT_BOTLIB_LIBVAR_GET] = (ql_import_f)QL_G_trap_BotLibVarGet;
	ql_game_imports[G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_G_trap_BotLibDefine;
	ql_game_imports[G_QL_IMPORT_BOTLIB_START_FRAME] = (ql_import_f)QL_G_trap_BotLibStartFrame;
	ql_game_imports[G_QL_IMPORT_BOTLIB_LOAD_MAP] = (ql_import_f)QL_G_trap_BotLibLoadMap;
	ql_game_imports[G_QL_IMPORT_BOTLIB_UPDATE_ENTITY] = (ql_import_f)QL_G_trap_BotLibUpdateEntity;
	ql_game_imports[G_QL_IMPORT_BOTLIB_TEST] = (ql_import_f)QL_G_trap_BotLibTest;
	ql_game_imports[G_QL_IMPORT_BOTLIB_GET_SNAPSHOT_ENTITY] = (ql_import_f)QL_G_trap_BotGetSnapshotEntity;
	ql_game_imports[G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotGetServerCommand;
	ql_game_imports[G_QL_IMPORT_BOTLIB_USER_COMMAND] = (ql_import_f)QL_G_trap_BotUserCommand;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS] = (ql_import_f)QL_G_trap_AAS_BBoxAreas;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_INFO] = (ql_import_f)QL_G_trap_AAS_AreaInfo;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO] = (ql_import_f)QL_G_trap_AAS_EntityInfo;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_INITIALIZED] = (ql_import_f)QL_G_trap_AAS_Initialized;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX] = (ql_import_f)QL_G_trap_AAS_PresenceTypeBoundingBox;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TIME] = (ql_import_f)QL_G_trap_AAS_Time;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX] = (ql_import_f)QL_G_trap_AAS_PointReachabilityAreaIndex;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY] = (ql_import_f)QL_G_trap_AAS_NextBSPEntity;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_ValueForBSPEpairKey;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_VectorForBSPEpairKey;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_FloatForBSPEpairKey;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_IntForBSPEpairKey;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY] = (ql_import_f)QL_G_trap_AAS_AreaReachability;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA] = (ql_import_f)QL_G_trap_AAS_EnableRoutingArea;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL] = (ql_import_f)QL_G_trap_AAS_AlternativeRouteGoals;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_SWIMMING] = (ql_import_f)QL_G_trap_AAS_Swimming;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE] = (ql_import_f)QL_G_trap_AAS_PredictRoute;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BINTEGER] = (ql_import_f)QL_G_trap_Characteristic_BInteger;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING] = (ql_import_f)QL_G_trap_Characteristic_String;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_CHAT_STATE] = (ql_import_f)QL_G_trap_BotAllocChatState;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_CHAT_STATE] = (ql_import_f)QL_G_trap_BotFreeChatState;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNextConsoleMessage;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_NUM_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNumConsoleMessages;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_NUM_INITIAL_CHATS] = (ql_import_f)QL_G_trap_BotNumInitialChats;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE] = (ql_import_f)QL_G_trap_BotGetChatMessage;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FIND_MATCH] = (ql_import_f)QL_G_trap_BotFindMatch;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE] = (ql_import_f)QL_G_trap_BotMatchVariable;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_UNIFY_WHITE_SPACES] = (ql_import_f)QL_G_trap_UnifyWhiteSpaces;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REPLACE_SYNONYMS] = (ql_import_f)QL_G_trap_BotReplaceSynonyms;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_CHAT_FILE] = (ql_import_f)QL_G_trap_BotLoadChatFile;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER] = (ql_import_f)QL_G_trap_BotSetChatGender;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME] = (ql_import_f)QL_G_trap_BotSetChatName;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE] = (ql_import_f)QL_G_trap_BotResetGoalState;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotRemoveFromAvoidGoals;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotResetAvoidGoals;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_PUSH_GOAL] = (ql_import_f)QL_G_trap_BotPushGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_POP_GOAL] = (ql_import_f)QL_G_trap_BotPopGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GOAL_NAME] = (ql_import_f)QL_G_trap_BotGoalName;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL] = (ql_import_f)QL_G_trap_BotGetTopGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL] = (ql_import_f)QL_G_trap_BotGetSecondGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHOOSE_LTG_ITEM] = (ql_import_f)QL_G_trap_BotChooseLTGItem;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHOOSE_NBG_ITEM] = (ql_import_f)QL_G_trap_BotChooseNBGItem;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_TOUCHING_GOAL] = (ql_import_f)QL_G_trap_BotTouchingGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE] = (ql_import_f)QL_G_trap_BotItemGoalInVisButNotVisible;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL] = (ql_import_f)QL_G_trap_BotGetNextCampSpotGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_SET_AVOID_GOAL_TIME] = (ql_import_f)QL_G_trap_BotSetAvoidGoalTime;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS] = (ql_import_f)QL_G_trap_BotUpdateEntityItems;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetAvoidReach;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetLastAvoidReach;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE] = (ql_import_f)QL_G_trap_BotInitMoveState;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT] = (ql_import_f)QL_G_trap_BotAddAvoidSpot;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON] = (ql_import_f)QL_G_trap_BotChooseBestFightWeapon;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_WEAPON_INFO] = (ql_import_f)QL_G_trap_BotGetWeaponInfo;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_WEAPON_WEIGHTS] = (ql_import_f)QL_G_trap_BotLoadWeaponWeights;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotAllocWeaponState;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotFreeWeaponState;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotResetWeaponState;
	ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION] = (ql_import_f)QL_G_trap_GeneticParentsAndChildSelection;
	ql_game_imports[G_QL_IMPORT_SUBMIT_MATCH_REPORT] = (ql_import_f)QL_G_trap_SubmitMatchReport;
	ql_game_imports[G_QL_IMPORT_REPORT_PLAYER_EVENT] = (ql_import_f)QL_G_trap_ReportPlayerEvent;
	ql_game_imports[G_QL_IMPORT_STEAMID_QUERY] = (ql_import_f)QL_G_trap_GetSteamId;
	ql_game_imports[G_QL_IMPORT_STEAM_STAT_ADD] = (ql_import_f)QL_G_trap_AddSteamStat;
	ql_game_imports[G_QL_IMPORT_STEAM_UNLOCK_ACHIEVEMENT] = (ql_import_f)QL_G_trap_UnlockSteamAchievement;
	ql_game_imports[G_QL_IMPORT_STEAM_HAS_ACHIEVEMENT] = (ql_import_f)QL_G_trap_HasSteamAchievement;
	ql_game_imports[G_QL_IMPORT_STEAM_AUTH_VALIDATE] = (ql_import_f)QL_G_trap_VerifySteamAuth;

	Com_Memcpy( &ql_game_imports[G_QL_IMPORT_COMPAT_BASE], ql_game_compat_imports, sizeof( ql_game_compat_imports ) );
}

/*
===============
SV_ShutdownGameProgs

Called every time a map changes
===============
*/
void SV_ShutdownGameProgs( void ) {
	if ( !gvm ) {
		return;
	}
	VM_Call( gvm, GAME_SHUTDOWN, qfalse );
	VM_Free( gvm );
	gvm = NULL;
}

/*
==================
SV_InitGameVM

Called for both a full init and a restart
==================
*/
static void SV_InitGameVM( qboolean restart ) {
	int		i;

	// start the entity parsing at the beginning
	sv.entityParsePoint = CM_EntityString();

	// clear all gentity pointers that might still be set from
	// a previous level
	// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=522
	//   now done before GAME_INIT call
	for ( i = 0 ; i < sv_maxclients->integer ; i++ ) {
		svs.clients[i].gentity = NULL;
	}
	
	// use the current msec count for a random seed
	// init for this gamestate
	VM_Call( gvm, GAME_INIT, svs.time, Com_Milliseconds(), restart );
}



/*
===================
SV_RestartGameProgs

Called on a map_restart, but not on a normal map change
===================
*/
void SV_RestartGameProgs( void ) {
	if ( !gvm ) {
		return;
	}
	VM_Call( gvm, GAME_SHUTDOWN, qtrue );

	// do a restart instead of a free
	gvm = VM_Restart( gvm );
	if ( !gvm ) { // bk001212 - as done below
		Com_Error( ERR_FATAL, "VM_Restart on game failed" );
	}

	SV_InitGameVM( qtrue );
}


/*
=============
SV_LoadGameModule

Attempts to load the game VM, preferring a native module when present.
=============
*/
static vm_t *SV_LoadGameModule( vmInterpret_t interpret ) {
	vm_t	*vm;

	vm = NULL;
	SV_InitGameImports();

	if ( interpret != VMI_COMPILED ) {
		vm = VM_Create( "qagame", SV_GameSystemCalls, VMI_NATIVE, ql_game_imports, GAME_API_VERSION );
		if ( vm ) {
			if ( vm->dllHandle || interpret != VMI_BYTECODE || !vm->compiled ) {
				return vm;
			}
			VM_Free( vm );
			vm = NULL;
		}
	}

	return VM_Create( "qagame", SV_GameSystemCalls, interpret, ql_game_imports, GAME_API_VERSION );
}

/*
===============
SV_InitGameProgs

Called on a normal map change, not on a map_restart
===============
*/
void SV_InitGameProgs( void ) {
	cvar_t	*var;
	vmInterpret_t interpret;
	//FIXME these are temp while I make bots run in vm
	extern int	bot_enable;

	var = Cvar_Get( "bot_enable", "1", CVAR_LATCH );
	if ( var ) {
		bot_enable = var->integer;
	}
	else {
		bot_enable = 0;
	}

	// load the dll or bytecode
	interpret = Cvar_VariableValue( "vm_game" );
	gvm = SV_LoadGameModule( interpret );
	if ( !gvm ) {
		Com_Error( ERR_FATAL, "VM_Create on game failed" );
	}

	SV_InitGameVM( qfalse );
}

/*
====================
SV_GameClientConnect

Normalizes the native `GAME_CLIENT_CONNECT` denial string into engine-owned
storage so restart and reconnect owners do not depend on VM pointer lifetime.
====================
*/
const char *SV_GameClientConnect( int clientNum, qboolean firstTime, qboolean isBot ) {
	int			deniedOffset;
	const char	*denied;

	sv_gameClientConnectDenied[0] = '\0';

	if ( !gvm ) {
		return NULL;
	}

	deniedOffset = VM_Call( gvm, GAME_CLIENT_CONNECT, clientNum, firstTime, isBot );
	if ( !deniedOffset ) {
		return NULL;
	}

	denied = VM_ExplicitArgPtr( gvm, deniedOffset );
	if ( denied ) {
		Q_strncpyz( sv_gameClientConnectDenied, denied, sizeof( sv_gameClientConnectDenied ) );
	}

	return sv_gameClientConnectDenied;
}


/*
====================
SV_GameCommand

See if the current console command is claimed by the game
====================
*/
qboolean SV_GameCommand( void ) {
	if ( sv.state != SS_GAME ) {
		return qfalse;
	}

	return VM_Call( gvm, GAME_CONSOLE_COMMAND ) ? qtrue : qfalse;
}

