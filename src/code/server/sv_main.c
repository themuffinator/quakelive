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

#include "server.h"
#include "../../common/platform/platform_steamworks.h"
#include <limits.h>
#include <stdlib.h>

serverStatic_t	svs;				// persistant server info
server_t		sv;					// local server
vm_t			*gvm = NULL;				// game virtual machine // bk001212 init

static qboolean SV_ClientEligibleForWarmupReady( const client_t *cl );
static qboolean SV_ClientReadyForWarmup( const client_t *cl );
static void SV_ComputeDisplayedCounts( int *clientCount, int *botCount );
static int s_botMaskRefreshTime = 0;
static int s_steamP2PKeepAliveTime = 0;
static int s_steamPublishedStateTime = 0;
static int s_steamPublishedNeedPass = -1;
static qboolean s_steamPublishedTagsInitialised = qfalse;
static int s_steamPublishedTagGametype = 0;
static int s_steamPublishedTagCheats = 0;
static int s_steamPublishedTagInstagib = 0;
static int s_steamPublishedTagRRInfected = 0;
static int s_steamPublishedTagQuadHog = 0;
static char s_steamPublishedTagGravity[MAX_CVAR_VALUE_STRING];
static char s_steamPublishedTagVampiric[MAX_CVAR_VALUE_STRING];
static char s_steamPublishedTagCustom[MAX_CVAR_VALUE_STRING];
static int s_svEmptyServerTime = -1;

/*
=============
SV_LogSteamServerNetworkingLifecycle

Publishes provider-aware diagnostics for the retained Steam GameServer
networking maintenance lane.
=============
*/
static void SV_LogSteamServerNetworkingLifecycle( const CSteamID *steamId, const char *stage, const char *detail ) {
	unsigned long long remoteId;

	remoteId = steamId ? (unsigned long long)steamId->value : 0ull;
	Com_DPrintf( "Steam server networking %s for %llu via %s [%s]: %s\n",
		stage ? stage : "update",
		remoteId,
		SV_GetSteamServerProviderLabel(), SV_GetSteamServerPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=============
SV_LogSteamServerPublishedState

Publishes provider-aware diagnostics for the retained Steam GameServer
published-state owner.
=============
*/
static void SV_LogSteamServerPublishedState( const CSteamID *steamId, const char *stage, const char *detail ) {
	unsigned long long remoteId;

	remoteId = steamId ? (unsigned long long)steamId->value : 0ull;
	Com_DPrintf( "Steam server published state %s for %llu via %s [%s]: %s\n",
		stage ? stage : "update",
		remoteId,
		SV_GetSteamServerProviderLabel(), SV_GetSteamServerPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=============
SV_ParseSteamIdToCSteamID

Converts a decimal SteamID string into a CSteamID container.
=============
*/
static qboolean SV_ParseSteamIdToCSteamID( const char *steamId, CSteamID *outId ) {
	unsigned long long value;
	const char *ch;

	if ( !steamId || !steamId[0] || !outId ) {
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

	outId->value = (uint64_t)value;
	return qtrue;
}

/*
=============
SV_GetClientSteamId

Extracts a client's SteamID as a CSteamID value.
=============
*/
static qboolean SV_GetClientSteamId( const client_t *cl, CSteamID *outId ) {
	if ( !cl || !outId ) {
		return qfalse;
	}

#if SV_HAS_PLATFORM_AUTH
	if ( cl->platformSteamId[0] ) {
		return SV_ParseSteamIdToCSteamID( cl->platformSteamId, outId );
	}
#endif

	outId->value = 0ull;
	return qfalse;
}

/*
=============
SV_ShouldRelayP2PPacket

Returns qtrue when a relayed P2P packet should be forwarded to the target slot.
=============
*/
static qboolean SV_ShouldRelayP2PPacket( int senderIndex, int targetIndex ) {
	return senderIndex != targetIndex ? qtrue : qfalse;
}

/*
=============
SV_SteamServerSendKeepAlive

Broadcasts the Steam P2P keepalive payload to connected clients.
=============
*/
static void SV_SteamServerSendKeepAlive( void ) {
	int			i;
	client_t	*cl;
	const char	keepAlive[] = "that's a good-ass dog";

	for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
		CSteamID steamId;

		if ( cl->state < CS_CONNECTED ) {
			continue;
		}

		if ( !SV_GetClientSteamId( cl, &steamId ) ) {
			continue;
		}

		if ( !QL_Steamworks_ServerSendP2PPacket( &steamId, keepAlive, (uint32_t)sizeof( keepAlive ), 2, 16 ) ) {
			SV_LogSteamServerNetworkingLifecycle( &steamId, "keepalive", "send failed" );
		}
	}
}

/*
=============
SV_SteamServerRelayP2PPackets

Reads P2P packets from Steam and relays them to other connected clients.
=============
*/
static void SV_SteamServerRelayP2PPackets( void ) {
	uint32_t	packetSize;

	while ( QL_Steamworks_ServerIsP2PPacketAvailable( &packetSize, 1 ) ) {
		char		*buffer;
		uint32_t	bytesRead = 0;
		CSteamID	remoteId;
		int			senderIndex = -1;
		int			i;
		client_t	*cl;

		if ( packetSize == 0 ) {
			break;
		}

		buffer = (char *)malloc( (size_t)packetSize + 1u );
		if ( !buffer ) {
			break;
		}

		if ( !QL_Steamworks_ServerReadP2PPacket( buffer + 1, packetSize, &bytesRead, &remoteId, 1 ) ) {
			SV_LogSteamServerNetworkingLifecycle( NULL, "p2p-read", "read failed" );
			free( buffer );
			continue;
		}

		for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
			CSteamID clientId;

			if ( cl->state < CS_CONNECTED ) {
				continue;
			}

			if ( !SV_GetClientSteamId( cl, &clientId ) ) {
				continue;
			}

			if ( clientId.value == remoteId.value ) {
				senderIndex = i;
				break;
			}
		}

		if ( senderIndex < 0 ) {
			SV_LogSteamServerNetworkingLifecycle( &remoteId, "p2p-relay", "sender not found" );
			free( buffer );
			continue;
		}

		buffer[0] = (char)senderIndex;

		for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
			CSteamID clientId;

			if ( cl->state < CS_CONNECTED ) {
				continue;
			}

			if ( !SV_ShouldRelayP2PPacket( senderIndex, i ) ) {
				continue;
			}

			if ( !SV_GetClientSteamId( cl, &clientId ) ) {
				continue;
			}

			if ( !QL_Steamworks_ServerSendP2PPacket( &clientId, buffer, bytesRead + 1, 1, 1 ) ) {
				SV_LogSteamServerNetworkingLifecycle( &clientId, "p2p-relay", "relay send failed" );
			}
		}

		free( buffer );
	}
}

/*
=============
SV_SteamServerDrainOutgoingPackets

Sends any queued Steam GameServer packets through the UDP socket.
=============
*/
static void SV_SteamServerDrainOutgoingPackets( void ) {
	uint8_t	buffer[1024];
	uint32_t	address;
	uint16_t	port;
	int			length;

	while ( (length = QL_Steamworks_ServerGetNextOutgoingPacket( buffer, sizeof( buffer ), &address, &port )) > 0 ) {
		netadr_t	adr;

		adr.type = NA_IP;
		adr.ip[0] = (byte)(address & 0xff);
		adr.ip[1] = (byte)((address >> 8) & 0xff);
		adr.ip[2] = (byte)((address >> 16) & 0xff);
		adr.ip[3] = (byte)((address >> 24) & 0xff);
		adr.port = (unsigned short)port;

		NET_SendPacket( NS_SERVER, length, buffer, adr );
	}
}

/*
=============
SV_SteamServerNetworkingFrame

Runs the Steam server networking maintenance loop.
=============
*/
static void SV_SteamServerNetworkingFrame( void ) {
	QL_Steamworks_RunServerCallbacks();

	if ( svs.time < s_steamP2PKeepAliveTime ) {
		s_steamP2PKeepAliveTime = 0;
	}
	if ( svs.time - s_steamP2PKeepAliveTime > 10000 ) {
		s_steamP2PKeepAliveTime = svs.time;
		SV_SteamServerSendKeepAlive();
	}

	SV_SteamServerRelayP2PPackets();
	SV_SteamServerDrainOutgoingPackets();
}

cvar_t	*sv_fps;				// time rate for running non-clients
cvar_t	*sv_timeout;			// seconds without any message
cvar_t	*sv_zombietime;			// seconds to sink messages after disconnect
cvar_t	*sv_rconPassword;		// password for remote server commands
cvar_t	*sv_privatePassword;	// password for the privateClient slots
cvar_t	*sv_allowDownload;
cvar_t	*sv_maxclients;

cvar_t	*sv_privateClients;		// number of clients reserved for password
cvar_t	*sv_hostname;
cvar_t	*sv_tags;
cvar_t	*sv_masterAdvertise;
cvar_t	*sv_master[MAX_MASTER_SERVERS];		// master server ip address
cvar_t	*sv_reconnectlimit;		// minimum seconds between connect messages
cvar_t	*sv_showloss;			// report when usercmds are lost
cvar_t	*sv_padPackets;			// add nop bytes to messages
cvar_t	*sv_killserver;			// menu system can set to 1 to shut server down
cvar_t	*sv_mapname;
cvar_t	*sv_mapChecksum;
cvar_t	*sv_serverid;
cvar_t	*sv_maxRate;
cvar_t	*sv_minPing;
cvar_t	*sv_maxPing;
cvar_t	*sv_gametype;
cvar_t	*sv_pure;
cvar_t	*sv_floodProtect;
cvar_t	*sv_lanForceRate; // dedicated 1 (LAN) server forces local client rates to 99999 (bug #491)
cvar_t	*sv_strictAuth;
cvar_t	*sv_mapPoolFile;
cvar_t	*sv_includeCurrentMapInVote;
cvar_t	*sv_gtid;
cvar_t	*sv_serverType;
cvar_t	*sv_ammoPack;
cvar_t	*sv_idleRestart;
cvar_t	*sv_idleExit;
cvar_t	*sv_errorExit;
cvar_t	*sv_quitOnEmpty;
cvar_t	*sv_quitOnExitLevel;
cvar_t	*sv_altEntDir;
cvar_t	*sv_dumpEntities;
cvar_t	*sv_cylinderScale;
cvar_t	*sv_warmupReadyPercentage;
cvar_t	*sv_vac;
cvar_t	*sv_maskBots;
cvar_t	*sv_enableRankings;
cvar_t	*sv_rankingsActive;
cvar_t	*sv_leagueName;
cvar_t	*net_fakevacban;
static int	s_svIdleExitDeadline;

/*
=============
SV_ClearIdleServerExit

Clears the retained dedicated idle-exit deadline when the server is active
again or when the policy is disabled.
=============
*/
void SV_ClearIdleServerExit( void ) {
	s_svIdleExitDeadline = 0;
}

/*
=============
SV_ShouldErrorExit

Reconstructs the retained sv_errorExit policy that upgrades ERR_DROP and
ERR_DISCONNECT into a fatal shutdown when requested.
=============
*/
qboolean SV_ShouldErrorExit( errorParm_t code ) {
	if ( code != ERR_DROP && code != ERR_DISCONNECT ) {
		return qfalse;
	}

	if ( !sv_errorExit ) {
		return qfalse;
	}

	if ( sv_errorExit->integer == 2 || ( sv_errorExit->integer == 1 && com_sv_running && com_sv_running->integer ) ) {
		Com_Printf( "sv_errorExit: configured to shut down on ERR_DROP or ERR_DISCONNECT\n" );
		return qtrue;
	}

	return qfalse;
}

/*
=============
SV_CheckIdleServerExit

Matches the retained dedicated idle-exit deadline handling used when the host
is running without an active server.
=============
*/
qboolean SV_CheckIdleServerExit( int currentTime ) {
	if ( !sv_idleExit || sv_idleExit->integer <= 0 ) {
		SV_ClearIdleServerExit();
		return qfalse;
	}

	if ( s_svIdleExitDeadline == 0 ) {
		s_svIdleExitDeadline = currentTime + sv_idleExit->integer * 1000;
		return qfalse;
	}

	if ( currentTime < s_svIdleExitDeadline - ( sv_idleExit->integer + 1 ) * 1000 || currentTime > s_svIdleExitDeadline + 5000 ) {
		SV_ClearIdleServerExit();
		return qfalse;
	}

	if ( s_svIdleExitDeadline < currentTime ) {
		Com_Error( ERR_FATAL, "shutting down idle dedicated server after sv_idleExit (%d) seconds", sv_idleExit->integer );
		return qtrue;
	}

	return qfalse;
}

/*
=============
SV_HandleQuitOnExitLevel

Checks sv_quitOnExitLevel and performs the shutdown or quit path.
=============
*/
qboolean SV_HandleQuitOnExitLevel( const char *context ) {
	const char	*actionContext;

	if ( !sv_quitOnExitLevel || !sv_quitOnExitLevel->integer ) {
		return qfalse;
	}

	actionContext = context ? context : "level exit";

	if ( sv_quitOnExitLevel->integer > 1 ) {
		Com_Printf( "sv_quitOnExitLevel %d: exiting after %s\n", sv_quitOnExitLevel->integer, actionContext );
		Com_Quit_f();
		return qtrue;
	}

	Com_Printf( "sv_quitOnExitLevel %d: shutting down after %s\n", sv_quitOnExitLevel->integer, actionContext );
	SV_Shutdown( "Server quit on exit level\n" );
	return qtrue;
}

/*
=============================================================================

EVENT MESSAGES

=============================================================================
*/

/*
===============
SV_ExpandNewlines

Converts newlines to "\n" so a line prints nicer
===============
*/
char	*SV_ExpandNewlines( char *in ) {
	static	char	string[1024];
	int		l;

	l = 0;
	while ( *in && l < sizeof(string) - 3 ) {
		if ( *in == '\n' ) {
			string[l++] = '\\';
			string[l++] = 'n';
		} else {
			string[l++] = *in;
		}
		in++;
	}
	string[l] = 0;

	return string;
}

/*
======================
SV_ReplacePendingServerCommands

  This is ugly
======================
*/
int SV_ReplacePendingServerCommands( client_t *client, const char *cmd ) {
	int i, index, csnum1, csnum2;

	for ( i = client->reliableSent+1; i <= client->reliableSequence; i++ ) {
		index = i & ( MAX_RELIABLE_COMMANDS - 1 );
		//
		if ( !Q_strncmp(cmd, client->reliableCommands[ index ], strlen("cs")) ) {
			sscanf(cmd, "cs %i", &csnum1);
			sscanf(client->reliableCommands[ index ], "cs %i", &csnum2);
			if ( csnum1 == csnum2 ) {
				Q_strncpyz( client->reliableCommands[ index ], cmd, sizeof( client->reliableCommands[ index ] ) );
				/*
				if ( client->netchan.remoteAddress.type != NA_BOT ) {
					Com_Printf( "WARNING: client %i removed double pending config string %i: %s\n", client-svs.clients, csnum1, cmd );
				}
				*/
				return qtrue;
			}
		}
	}
	return qfalse;
}

/*
======================
SV_AddServerCommand

The given command will be transmitted to the client, and is guaranteed to
not have future snapshot_t executed before it is executed
======================
*/
void SV_AddServerCommand( client_t *client, const char *cmd ) {
	int		index, i;

	// this is very ugly but it's also a waste to for instance send multiple config string updates
	// for the same config string index in one snapshot
//	if ( SV_ReplacePendingServerCommands( client, cmd ) ) {
//		return;
//	}

	client->reliableSequence++;
	// if we would be losing an old command that hasn't been acknowledged,
	// we must drop the connection
	// we check == instead of >= so a broadcast print added by SV_DropClient()
	// doesn't cause a recursive drop client
	if ( client->reliableSequence - client->reliableAcknowledge == MAX_RELIABLE_COMMANDS + 1 ) {
		Com_Printf( "===== pending server commands =====\n" );
		for ( i = client->reliableAcknowledge + 1 ; i <= client->reliableSequence ; i++ ) {
			Com_Printf( "cmd %5d: %s\n", i, client->reliableCommands[ i & (MAX_RELIABLE_COMMANDS-1) ] );
		}
		Com_Printf( "cmd %5d: %s\n", i, cmd );
		SV_DropClient( client, "Server command overflow" );
		return;
	}
	index = client->reliableSequence & ( MAX_RELIABLE_COMMANDS - 1 );
	Q_strncpyz( client->reliableCommands[ index ], cmd, sizeof( client->reliableCommands[ index ] ) );
}


/*
=================
SV_SendServerCommand

Sends a reliable command string to be interpreted by 
the client game module: "cp", "print", "chat", etc
A NULL client will broadcast to all clients
=================
*/
void QDECL SV_SendServerCommand(client_t *cl, const char *fmt, ...) {
	va_list		argptr;
	byte		message[MAX_MSGLEN];
	client_t	*client;
	int			j;
	
	va_start (argptr,fmt);
	Q_vsnprintf ((char *)message, sizeof(message), fmt,argptr);
	va_end (argptr);

	if ( cl != NULL ) {
		SV_AddServerCommand( cl, (char *)message );
		return;
	}

	// hack to echo broadcast prints to console
	if ( com_dedicated->integer && !strncmp( (char *)message, "print", 5) ) {
		Com_Printf ("broadcast: %s\n", SV_ExpandNewlines((char *)message) );
	}

	// send the data to all relevent clients
	for (j = 0, client = svs.clients; j < sv_maxclients->integer ; j++, client++) {
		if ( client->state < CS_PRIMED ) {
			continue;
		}
		SV_AddServerCommand( client, (char *)message );
	}
}


/*
==============================================================================

MASTER SERVER FUNCTIONS

==============================================================================
*/

/*
================
SV_LogMasterVACHeartbeat

Annotates heartbeat telemetry with the current VAC enablement state.
================
*/
static void SV_LogMasterVACHeartbeat( const netadr_t *adr, const char *masterName ) {
	const char *state;

	state = ( sv_vac && sv_vac->integer ) ? "enabled" : "disabled";

	NET_LogAuthTelemetry( NS_SERVER, adr, NULL, "vac", state, "heartbeat", NULL, masterName );
}

/*
================
SV_MasterHeartbeat

Send a message to the masters every few minutes to
let it know we are alive, and log information.
We will also have a heartbeat sent when a server
changes from empty to non-empty, and full to non-full,
but not on every player enter or exit.
================
*/
#define HEARTBEAT_MSEC	300*1000
#define HEARTBEAT_GAME	"QuakeArena-1"
void SV_MasterHeartbeat( void ) {
#if QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES
	static netadr_t	adr[MAX_MASTER_SERVERS];
	int			i;
	int			visibleClients;
	int			reportedBots;
	int			serverType;

	// "dedicated 1" is for lan play, "dedicated 2" is for inet public play
	if ( !com_dedicated || com_dedicated->integer != 2 ) {
		return;		// only dedicated servers send heartbeats
	}

	// if not time yet, don't send anything
	if ( svs.time < svs.nextHeartbeatTime ) {
		return;
	}
	svs.nextHeartbeatTime = svs.time + HEARTBEAT_MSEC;

	if ( sv_masterAdvertise && !sv_masterAdvertise->integer ) {
		return;
	}

	SV_ComputeDisplayedCounts( &visibleClients, &reportedBots );
	serverType = sv_serverType ? sv_serverType->integer : 0;

	// send to group masters
	for ( i = 0 ; i < MAX_MASTER_SERVERS ; i++ ) {
		if ( !sv_master[i]->string[0] ) {
			continue;
		}

		// see if we haven't already resolved the name
		// resolving usually causes hitches on win95, so only
		// do it when needed
		if ( sv_master[i]->modified ) {
			sv_master[i]->modified = qfalse;

			Com_Printf( "Resolving %s\n", sv_master[i]->string );
			if ( !NET_StringToAdr( sv_master[i]->string, &adr[i] ) ) {
				// if the address failed to resolve, clear it
				// so we don't take repeated dns hits
				Com_Printf( "Couldn't resolve address: %s\n", sv_master[i]->string );
				Cvar_Set( sv_master[i]->name, "" );
				sv_master[i]->modified = qfalse;
				continue;
			}
			if ( !strstr( ":", sv_master[i]->string ) ) {
				adr[i].port = BigShort( PORT_MASTER );
			}
			Com_Printf( "%s resolved to %i.%i.%i.%i:%i\n", sv_master[i]->string,
					adr[i].ip[0], adr[i].ip[1], adr[i].ip[2], adr[i].ip[3],
					BigShort( adr[i].port ) );
		}


		Com_Printf ("Sending heartbeat to %s (players: %i, botPlayers: %i, serverType: %i)\n", sv_master[i]->string, visibleClients, reportedBots, serverType );
		// this command should be changed if the server info / status format
		// ever incompatably changes
		NET_OutOfBandPrint( NS_SERVER, adr[i], "heartbeat %s\n", HEARTBEAT_GAME );

		SV_LogMasterVACHeartbeat( &adr[i], sv_master[i]->string );
	}
#else
	return;
#endif
}

/*
=================
SV_MasterShutdown

Informs all masters that this server is going down
=================
*/
void SV_MasterShutdown( void ) {
	// send a hearbeat right now
	svs.nextHeartbeatTime = -9999;
	SV_MasterHeartbeat();

	// send it again to minimize chance of drops
	svs.nextHeartbeatTime = -9999;
	SV_MasterHeartbeat();

	// when the master tries to poll the server, it won't respond, so
	// it will be removed from the list
}


/*
==============================================================================

CONNECTIONLESS COMMANDS

==============================================================================
*/

/*
===============
SV_ComputeDisplayedCounts

Calculates the reported player and bot totals, respecting bot masking.
===============
*/
static void SV_ComputeDisplayedCounts( int *clientCount, int *botCount ) {
	int				i;
	int				reportedBots;
	int				players;
	client_t	*cl;

	players = 0;
	reportedBots = 0;

	for ( i = sv_privateClients->integer ; i < sv_maxclients->integer ; i++ ) {
		cl = &svs.clients[i];

		if ( cl->state < CS_CONNECTED ) {
			continue;
		}

		if ( SV_ClientIsBot( cl ) ) {
			if ( sv_maskBots && sv_maskBots->integer ) {
				continue;
			}

			reportedBots++;
		}

		players++;
	}

	if ( clientCount ) {
		*clientCount = players;
	}

	if ( botCount ) {
		*botCount = reportedBots;
	}
}

/*
=============
SV_SteamServerGameDescription

Returns the retail-facing Steam game description for the active gametype.
=============
*/
static const char *SV_SteamServerGameDescription( int gametype ) {
	static const char *const s_gametypeDescriptions[GT_MAX_GAME_TYPE] = {
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

	return s_gametypeDescriptions[gametype];
}

/*
=============
SV_SteamServerGameTagName

Returns the retail Steam short gametype tag used in the published game-tags string.
=============
*/
static const char *SV_SteamServerGameTagName( int gametype ) {
	static const char *const s_gametypeTags[GT_MAX_GAME_TYPE] = {
		"ffa",
		"duel",
		"race",
		"tdm",
		"clanarena",
		"ctf",
		"oneflag",
		"overload",
		"harvester",
		"freezetag",
		"domination",
		"a&d",
		"redrover"
	};

	if ( gametype < 0 || gametype >= GT_MAX_GAME_TYPE ) {
		return "";
	}

	return s_gametypeTags[gametype];
}

/*
=============
SV_SteamServerAppendGameTag

Appends a single tag and keeps the retail comma-delimited builder format intact.
=============
*/
static void SV_SteamServerAppendGameTag( char *tags, int size, const char *tag ) {
	size_t length;

	if ( !tags || size <= 0 || !tag || !tag[0] ) {
		return;
	}

	Q_strcat( tags, size, tag );
	length = strlen( tags );
	if ( length > 0 && tags[length - 1] != ',' ) {
		Q_strcat( tags, size, "," );
	}
}

/*
=============
SV_SteamServerTrimGameTags

Removes the final comma before the string is published to Steam.
=============
*/
static void SV_SteamServerTrimGameTags( char *tags ) {
	size_t length;

	if ( !tags || !tags[0] ) {
		return;
	}

	length = strlen( tags );
	if ( length > 0 && tags[length - 1] == ',' ) {
		tags[length - 1] = '\0';
	}
}

/*
=============
SV_SteamServerBuildGameTags

Reconstructs the cvar-owned retail Steam game-tags tranche from the published-state owner.
=============
*/
static void SV_SteamServerBuildGameTags( char *tags, int size ) {
	int		gametype;
	float	gravity;

	if ( !tags || size <= 0 ) {
		return;
	}

	tags[0] = '\0';
	gametype = Cvar_VariableIntegerValue( "g_gametype" );
	SV_SteamServerAppendGameTag( tags, size, SV_SteamServerGameTagName( gametype ) );

	if ( Cvar_VariableIntegerValue( "sv_cheats" ) ) {
		SV_SteamServerAppendGameTag( tags, size, "cheats" );
	}

	if ( Cvar_VariableIntegerValue( "g_instagib" ) ) {
		SV_SteamServerAppendGameTag( tags, size, "instagib" );
	}

	gravity = Cvar_VariableValue( "g_gravity" );
	if ( gravity < 800.0f ) {
		SV_SteamServerAppendGameTag( tags, size, "lowgrav" );
	} else if ( gravity > 800.0f ) {
		SV_SteamServerAppendGameTag( tags, size, "highgrav" );
	}

	if ( Cvar_VariableValue( "g_vampiricDamage" ) > 0.0f ) {
		SV_SteamServerAppendGameTag( tags, size, "vampiric" );
	}

	if ( gametype == GT_RED_ROVER && Cvar_VariableIntegerValue( "g_rrInfected" ) ) {
		SV_SteamServerAppendGameTag( tags, size, "infected" );
	}

	if ( gametype == GT_FFA && Cvar_VariableIntegerValue( "g_quadhog" ) ) {
		SV_SteamServerAppendGameTag( tags, size, "quadhog" );
	}

	if ( sv_tags && sv_tags->string[0] ) {
		Q_strcat( tags, size, sv_tags->string );
		if ( tags[0] && tags[strlen( tags ) - 1] != ',' ) {
			Q_strcat( tags, size, "," );
		}
	}

	SV_SteamServerTrimGameTags( tags );
}

/*
=============
SV_SteamServerUpdatePublishedState

Reconstructs the mapped retail Steam game-server published-state owner.
=============
*/
void SV_SteamServerUpdatePublishedState( qboolean fullUpdate ) {
	int				i;
	int				now;
	int				needPass;
	int				tagGametype;
	int				tagCheats;
	int				tagInstagib;
	int				tagRRInfected;
	int				tagQuadHog;
	int				botCount;
	qboolean		refreshPlayers;
	qboolean		refreshTags;
	client_t		*cl;
	char			redScore[16];
	char			blueScore[16];
	char			tagGravity[MAX_CVAR_VALUE_STRING];
	char			tagVampiric[MAX_CVAR_VALUE_STRING];
	char			tagCustom[MAX_CVAR_VALUE_STRING];
	char			gameTags[MAX_CVAR_VALUE_STRING];
	char			detail[MAX_STRING_CHARS];

	if ( !QL_Steamworks_ServerIsInitialised() ) {
		return;
	}

	if ( fullUpdate || ( sv_maxclients && sv_maxclients->modified ) ) {
		if ( !QL_Steamworks_ServerSetMaxPlayerCount( sv_maxclients ? sv_maxclients->integer : 0 ) ) {
			SV_LogSteamServerPublishedState( NULL, "max-players", "publish failed" );
		}
	}

	needPass = Cvar_VariableIntegerValue( "g_needpass" );
	if ( fullUpdate || needPass != s_steamPublishedNeedPass ) {
		if ( !QL_Steamworks_ServerSetPasswordProtected( needPass ? qtrue : qfalse ) ) {
			SV_LogSteamServerPublishedState( NULL, "password-protected", "publish failed" );
		}
		s_steamPublishedNeedPass = needPass;
	}

	if ( fullUpdate || ( sv_hostname && sv_hostname->modified ) ) {
		if ( !QL_Steamworks_ServerSetServerName( sv_hostname->string ) ) {
			SV_LogSteamServerPublishedState( NULL, "server-name", "publish failed" );
		}
		sv_hostname->modified = qfalse;
	}

	if ( fullUpdate || ( sv_mapname && sv_mapname->modified ) ) {
		if ( !QL_Steamworks_ServerSetMapName( sv_mapname->string ) ) {
			SV_LogSteamServerPublishedState( NULL, "map-name", "publish failed" );
		}
		sv_mapname->modified = qfalse;
	}

	if ( fullUpdate || ( sv_gametype && sv_gametype->modified ) ) {
		if ( !QL_Steamworks_ServerSetGameDescription( SV_SteamServerGameDescription( sv_gametype->integer ) ) ) {
			SV_LogSteamServerPublishedState( NULL, "game-description", "publish failed" );
		}
	}

	tagGametype = Cvar_VariableIntegerValue( "g_gametype" );
	tagCheats = Cvar_VariableIntegerValue( "sv_cheats" );
	tagInstagib = Cvar_VariableIntegerValue( "g_instagib" );
	tagRRInfected = Cvar_VariableIntegerValue( "g_rrInfected" );
	tagQuadHog = Cvar_VariableIntegerValue( "g_quadhog" );
	Cvar_VariableStringBuffer( "g_gravity", tagGravity, sizeof( tagGravity ) );
	Cvar_VariableStringBuffer( "g_vampiricDamage", tagVampiric, sizeof( tagVampiric ) );

	if ( sv_tags ) {
		Q_strncpyz( tagCustom, sv_tags->string, sizeof( tagCustom ) );
	} else {
		tagCustom[0] = '\0';
	}

	refreshTags = fullUpdate;
	if ( !refreshTags && !s_steamPublishedTagsInitialised ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && tagGametype != s_steamPublishedTagGametype ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && tagCheats != s_steamPublishedTagCheats ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && tagInstagib != s_steamPublishedTagInstagib ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && tagRRInfected != s_steamPublishedTagRRInfected ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && tagQuadHog != s_steamPublishedTagQuadHog ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && Q_stricmp( tagGravity, s_steamPublishedTagGravity ) ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && Q_stricmp( tagVampiric, s_steamPublishedTagVampiric ) ) {
		refreshTags = qtrue;
	}
	if ( !refreshTags && Q_stricmp( tagCustom, s_steamPublishedTagCustom ) ) {
		refreshTags = qtrue;
	}

	if ( refreshTags ) {
		SV_SteamServerBuildGameTags( gameTags, sizeof( gameTags ) );
		if ( !QL_Steamworks_ServerSetGameTags( gameTags ) ) {
			SV_LogSteamServerPublishedState( NULL, "game-tags", "publish failed" );
		}
		s_steamPublishedTagsInitialised = qtrue;
		s_steamPublishedTagGametype = tagGametype;
		s_steamPublishedTagCheats = tagCheats;
		s_steamPublishedTagInstagib = tagInstagib;
		s_steamPublishedTagRRInfected = tagRRInfected;
		s_steamPublishedTagQuadHog = tagQuadHog;
		Q_strncpyz( s_steamPublishedTagGravity, tagGravity, sizeof( s_steamPublishedTagGravity ) );
		Q_strncpyz( s_steamPublishedTagVampiric, tagVampiric, sizeof( s_steamPublishedTagVampiric ) );
		Q_strncpyz( s_steamPublishedTagCustom, tagCustom, sizeof( s_steamPublishedTagCustom ) );
	}

	now = Sys_Milliseconds();
	if ( now < s_steamPublishedStateTime ) {
		s_steamPublishedStateTime = 0;
	}

	refreshPlayers = ( fullUpdate || now - s_steamPublishedStateTime > 3000 ) ? qtrue : qfalse;
	if ( !refreshPlayers ) {
		return;
	}

	s_steamPublishedStateTime = now;

	Cvar_VariableStringBuffer( "g_redScore", redScore, sizeof( redScore ) );
	Cvar_VariableStringBuffer( "g_blueScore", blueScore, sizeof( blueScore ) );
	if ( !QL_Steamworks_ServerSetKeyValue( "g_redScore", redScore ) ) {
		SV_LogSteamServerPublishedState( NULL, "key-value", "publish failed for g_redScore" );
	}
	if ( !QL_Steamworks_ServerSetKeyValue( "g_blueScore", blueScore ) ) {
		SV_LogSteamServerPublishedState( NULL, "key-value", "publish failed for g_blueScore" );
	}

	botCount = 0;

	for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
		CSteamID		steamId;
		const char		*rawName;
		char			playerName[MAX_NAME_LENGTH + 8];
		playerState_t	*playerState;

		if ( cl->state < CS_CONNECTED ) {
			continue;
		}

		if ( SV_ClientIsBot( cl ) ) {
			botCount++;
		}

		if ( !SV_GetClientSteamId( cl, &steamId ) ) {
			continue;
		}

		rawName = Info_ValueForKey( cl->userinfo, "name" );
		if ( !rawName || !rawName[0] ) {
			rawName = cl->name;
		}

		if ( SV_ClientIsBot( cl ) ) {
			Com_sprintf( playerName, sizeof( playerName ), "(Bot) %s", rawName );
		} else {
			Q_strncpyz( playerName, rawName, sizeof( playerName ) );
		}

		playerState = SV_GameClientNum( i );
		if ( !playerState ) {
			continue;
		}

		if ( !QL_Steamworks_ServerUpdateUserData( &steamId, playerName, (uint32_t)playerState->persistant[PERS_SCORE] ) ) {
			Com_sprintf( detail, sizeof( detail ), "publish failed for client %d (%s)", i, playerName );
			SV_LogSteamServerPublishedState( &steamId, "user-data", detail );
		}
	}

	if ( !QL_Steamworks_ServerSetBotPlayerCount( botCount ) ) {
		SV_LogSteamServerPublishedState( NULL, "bot-player-count", "publish failed" );
	}
}



/*
================
SVC_Status

Responds with all the info that qplug or qspy can see about the server
and all connected players.  Used for getting detailed information after
the simple info query.
================
*/
void SVC_Status( netadr_t from ) {
	char	player[1024];
	char	status[MAX_MSGLEN];
	int		i;
	int		botCount;
	int		visibleClients;
	client_t	*cl;
	playerState_t	*ps;
	int		statusLength;
	int		playerLength;
	char	infostring[MAX_INFO_STRING];

	// ignore if we are in single player
	if ( Cvar_VariableValue( "g_gametype" ) == GT_SINGLE_PLAYER ) {
		return;
	}

	strcpy( infostring, Cvar_InfoString( CVAR_SERVERINFO ) );

	// echo back the parameter to status. so master servers can use it as a challenge
	// to prevent timed spoofed reply packets that add ghost servers
	Info_SetValueForKey( infostring, "challenge", Cmd_Argv(1) );

	SV_ComputeDisplayedCounts( &visibleClients, &botCount );
	Info_SetValueForKey( infostring, "clients", va("%i", visibleClients) );
	Info_SetValueForKey( infostring, "botPlayers", va("%i", botCount) );
	Info_SetValueForKey( infostring, "vac", va("%i", sv_vac->integer) );
	Info_SetValueForKey( infostring, "serverType", va("%i", sv_serverType->integer) );

	// add "demo" to the sv_keywords if restricted
	if ( Cvar_VariableValue( "fs_restrict" ) ) {
		char	keywords[MAX_INFO_STRING];

		Com_sprintf( keywords, sizeof( keywords ), "demo %s",
			Info_ValueForKey( infostring, "sv_keywords" ) );
		Info_SetValueForKey( infostring, "sv_keywords", keywords );
	}

	status[0] = 0;
	statusLength = 0;

	for (i=0 ; i < sv_maxclients->integer ; i++) {
		cl = &svs.clients[i];
		if ( cl->state >= CS_CONNECTED ) {
			if ( sv_maskBots->integer && SV_ClientIsBot( cl ) ) {
				continue;
			}
			ps = SV_GameClientNum( i );
			Com_sprintf (player, sizeof(player), "%i %i \"%s\"\n", 
				ps->persistant[PERS_SCORE], cl->ping, cl->name);
			playerLength = strlen(player);
			if (statusLength + playerLength >= sizeof(status) ) {
				break;		// can't hold any more
			}
			strcpy (status + statusLength, player);
			statusLength += playerLength;
		}
	}

	NET_OutOfBandPrint( NS_SERVER, from, "statusResponse\n%s\n%s", infostring, status );
}


/*
================
SVC_Info

Responds with a short info message that should be enough to determine
if a user is interested in a server to do a full status
================
*/
void SVC_Info( netadr_t from ) {
	int			count;
	int		botCount;
	char	*gamedir;
	char	infostring[MAX_INFO_STRING];

	// ignore if we are in single player
	if ( Cvar_VariableValue( "g_gametype" ) == GT_SINGLE_PLAYER || Cvar_VariableValue("ui_singlePlayerActive")) {
		return;
	}

	SV_ComputeDisplayedCounts( &count, &botCount );

	infostring[0] = 0;

	// echo back the parameter to status. so servers can use it as a challenge
	// to prevent timed spoofed reply packets that add ghost servers
	Info_SetValueForKey( infostring, "challenge", Cmd_Argv(1) );

	Info_SetValueForKey( infostring, "protocol", va("%i", PROTOCOL_VERSION) );
	Info_SetValueForKey( infostring, "hostname", sv_hostname->string );
	Info_SetValueForKey( infostring, "mapname", sv_mapname->string );
	Info_SetValueForKey( infostring, "clients", va("%i", count) );
	Info_SetValueForKey( infostring, "botPlayers", va("%i", botCount) );
	Info_SetValueForKey( infostring, "vac", va("%i", sv_vac->integer) );
	Info_SetValueForKey( infostring, "serverType", va("%i", sv_serverType->integer) );
	Info_SetValueForKey( infostring, "sv_maxclients",
		va("%i", sv_maxclients->integer - sv_privateClients->integer ) );
	Info_SetValueForKey( infostring, "gametype", va("%i", sv_gametype->integer ) );
	Info_SetValueForKey( infostring, "pure", va("%i", sv_pure->integer ) );

	if ( sv_minPing->integer ) {
		Info_SetValueForKey( infostring, "minPing", va("%i", sv_minPing->integer) );
	}
	if ( sv_maxPing->integer ) {
		Info_SetValueForKey( infostring, "maxPing", va("%i", sv_maxPing->integer) );
	}
	gamedir = Cvar_VariableString( "fs_game" );
	if ( *gamedir ) {
		Info_SetValueForKey( infostring, "game", gamedir );
	}

	NET_OutOfBandPrint( NS_SERVER, from, "infoResponse\n%s", infostring );
}


/*
================
SVC_FlushRedirect

================
*/
void SV_FlushRedirect( char *outputbuf ) {
	NET_OutOfBandPrint( NS_SERVER, svs.redirectAddress, "print\n%s", outputbuf );
}

/*
===============
SVC_RemoteCommand

An rcon packet arrived from the network.
Shift down the remaining args
Redirect all printfs
===============
*/
void SVC_RemoteCommand( netadr_t from, msg_t *msg ) {
	qboolean	valid;
	unsigned int time;
	char		remaining[1024];
	// TTimo - scaled down to accumulate, but not overflow anything network wise, print wise etc.
	// (OOB messages are the bottleneck here)
#define SV_OUTPUTBUF_LENGTH (1024 - 16)
	char		sv_outputbuf[SV_OUTPUTBUF_LENGTH];
	static unsigned int lasttime = 0;
	char *cmd_aux;

	// TTimo - https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=534
	time = Com_Milliseconds();
	if (time<(lasttime+500)) {
		return;
	}
	lasttime = time;

	if ( !strlen( sv_rconPassword->string ) ||
		strcmp (Cmd_Argv(1), sv_rconPassword->string) ) {
		valid = qfalse;
		Com_Printf ("Bad rcon from %s:\n%s\n", NET_AdrToString (from), Cmd_Argv(2) );
	} else {
		valid = qtrue;
		Com_Printf ("Rcon from %s:\n%s\n", NET_AdrToString (from), Cmd_Argv(2) );
	}

	// start redirecting all print outputs to the packet
	svs.redirectAddress = from;
	Com_BeginRedirect (sv_outputbuf, SV_OUTPUTBUF_LENGTH, SV_FlushRedirect);

	if ( !strlen( sv_rconPassword->string ) ) {
		Com_Printf ("No rconpassword set on the server.\n");
	} else if ( !valid ) {
		Com_Printf ("Bad rconpassword.\n");
	} else {
		remaining[0] = 0;
		
		// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=543
		// get the command directly, "rcon <pass> <command>" to avoid quoting issues
		// extract the command by walking
		// since the cmd formatting can fuckup (amount of spaces), using a dumb step by step parsing
		cmd_aux = Cmd_Cmd();
		cmd_aux+=4;
		while(cmd_aux[0]==' ')
			cmd_aux++;
		while(cmd_aux[0] && cmd_aux[0]!=' ') // password
			cmd_aux++;
		while(cmd_aux[0]==' ')
			cmd_aux++;
		
		Q_strcat( remaining, sizeof(remaining), cmd_aux);
		
		Cmd_ExecuteString (remaining);

	}

	Com_EndRedirect ();
}

/*
=================
SV_ConnectionlessPacket

A connectionless packet has four leading 0xff
characters to distinguish it from a game channel.
Clients that are in the game can still send
connectionless packets.
=================
*/
void SV_ConnectionlessPacket( netadr_t from, msg_t *msg ) {
	char	*s;
	char	*c;

	MSG_BeginReadingOOB( msg );
	MSG_ReadLong( msg );		// skip the -1 marker

	if (!Q_strncmp("connect", &msg->data[4], 7)) {
		Huff_Decompress(msg, 12);
	}

	s = MSG_ReadStringLine( msg );
	Cmd_TokenizeString( s );

	c = Cmd_Argv(0);
	Com_DPrintf ("SV packet %s : %s\n", NET_AdrToString(from), c);

	if (!Q_stricmp(c, "getstatus")) {
		SVC_Status( from  );
  } else if (!Q_stricmp(c, "getinfo")) {
		SVC_Info( from );
	} else if (!Q_stricmp(c, "getchallenge")) {
		SV_GetChallenge( from );
	} else if (!Q_stricmp(c, "connect")) {
		SV_DirectConnect( from );
	} else if (!Q_stricmp(c, "ipAuthorize")) {
		SV_AuthorizeIpPacket( from );
	} else if (!Q_stricmp(c, "rcon")) {
		SVC_RemoteCommand( from, msg );
	} else if (!Q_stricmp(c, "disconnect")) {
		// if a client starts up a local server, we may see some spurious
		// server disconnect messages when their new server sees our final
		// sequenced messages to the old client
	} else {
		Com_DPrintf ("bad connectionless packet from %s:\n%s\n"
		, NET_AdrToString (from), s);
	}
}

/*
=============
SV_ClientEligibleForWarmupReady

Checks whether a client counts toward the warmup ready threshold.
=============
*/
static qboolean SV_ClientEligibleForWarmupReady( const client_t *cl ) {
	const char	*team;

	if ( cl->state < CS_CONNECTED ) {
		return qfalse;
	}

	if ( SV_ClientIsBot( cl ) ) {
		return qfalse;
	}

	team = Info_ValueForKey( cl->userinfo, "team" );
	if ( !Q_stricmp( team, "spectator" ) || !Q_stricmp( team, "s" ) || !Q_stricmp( team, "scoreboard" ) ) {
		return qfalse;
	}

	return qtrue;
}


/*
=============
SV_ClientReadyForWarmup

Determines if an eligible client has finished loading and entered the game.
=============
*/
static qboolean SV_ClientReadyForWarmup( const client_t *cl ) {
	if ( !SV_ClientEligibleForWarmupReady( cl ) ) {
		return qfalse;
	}

	return ( cl->state == CS_ACTIVE );
}


/*
=============
SV_CheckWarmupReadiness

Evaluates the warmup ready percentage and optionally announces deficiencies.
=============
*/
qboolean SV_CheckWarmupReadiness( qboolean announce ) {
	int		ready;
	int		eligible;
	int		percent;
	int		index;
	char	info[MAX_INFO_STRING];

	ready = 0;
	eligible = 0;

	for ( index = 0; index < sv_maxclients->integer; index++ ) {
		client_t *cl = svs.clients + index;

		if ( SV_ClientReadyForWarmup( cl ) ) {
			ready++;
			eligible++;
			continue;
		}

		if ( SV_ClientEligibleForWarmupReady( cl ) ) {
			eligible++;
		}
	}

	if ( eligible <= 0 ) {
		percent = 100;
	} else {
		percent = ( ready * 100 ) / eligible;
	}

	info[0] = '\0';
	Info_SetValueForKey( info, "pct", va( "%i", sv_warmupReadyPercentage->integer ) );
	Info_SetValueForKey( info, "ready", va( "%i", ready ) );
	Info_SetValueForKey( info, "eligible", va( "%i", eligible ) );
	SV_SetConfigstring( CS_WARMUP_READY, info );

	if ( sv_warmupReadyPercentage->integer <= 0 ) {
		return qtrue;
	}

	if ( percent >= sv_warmupReadyPercentage->integer ) {
		return qtrue;
	}

	if ( announce ) {
		SV_SendServerCommand( NULL, va( "print \"Warmup waiting: %i of %i players ready (%i%% required).\\n\"", ready, eligible, sv_warmupReadyPercentage->integer ) );
	}

	return qfalse;
}

//============================================================================

/*
=================
SV_ReadPackets
=================
*/
void SV_PacketEvent( netadr_t from, msg_t *msg ) {
	int			i;
	client_t	*cl;
	int			qport;

	// check for connectionless packet (0xffffffff) first
	if ( msg->cursize >= 4 && *(int *)msg->data == -1) {
		SV_ConnectionlessPacket( from, msg );
		return;
	}

	// read the qport out of the message so we can fix up
	// stupid address translating routers
	MSG_BeginReadingOOB( msg );
	MSG_ReadLong( msg );				// sequence number
	qport = MSG_ReadShort( msg ) & 0xffff;

	// find which client the message is from
	for (i=0, cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {
		if (cl->state == CS_FREE) {
			continue;
		}
		if ( !NET_CompareBaseAdr( from, cl->netchan.remoteAddress ) ) {
			continue;
		}
		// it is possible to have multiple clients from a single IP
		// address, so they are differentiated by the qport variable
		if (cl->netchan.qport != qport) {
			continue;
		}

		// the IP port can't be used to differentiate them, because
		// some address translating routers periodically change UDP
		// port assignments
		if (cl->netchan.remoteAddress.port != from.port) {
			Com_Printf( "SV_PacketEvent: fixing up a translated port\n" );
			cl->netchan.remoteAddress.port = from.port;
		}

		// make sure it is a valid, in sequence packet
		if (SV_Netchan_Process(cl, msg)) {
			// zombie clients still need to do the Netchan_Process
			// to make sure they don't need to retransmit the final
			// reliable message, but they don't do any other processing
			if (cl->state != CS_ZOMBIE) {
				cl->lastPacketTime = svs.time;	// don't timeout
				SV_ExecuteClientMessage( cl, msg );
			}
		}
		return;
	}
	
	// if we received a sequenced packet from an address we don't recognize,
	// send an out of band disconnect packet to it
	NET_OutOfBandPrint( NS_SERVER, from, "disconnect" );
}


/*
===================
SV_CalcPings

Updates the cl->ping variables
===================
*/
void SV_CalcPings( void ) {
	int			i, j;
	client_t	*cl;
	int			total, count;
	int			delta;
	playerState_t	*ps;

	for (i=0 ; i < sv_maxclients->integer ; i++) {
		cl = &svs.clients[i];
		if ( cl->state != CS_ACTIVE ) {
			cl->ping = 999;
			continue;
		}
		if ( !cl->gentity ) {
			cl->ping = 999;
			continue;
		}
		if ( cl->gentity->r.svFlags & SVF_BOT ) {
			cl->ping = 0;
			continue;
		}

		total = 0;
		count = 0;
		for ( j = 0 ; j < PACKET_BACKUP ; j++ ) {
			if ( cl->frames[j].messageAcked <= 0 ) {
				continue;
			}
			delta = cl->frames[j].messageAcked - cl->frames[j].messageSent;
			count++;
			total += delta;
		}
		if (!count) {
			cl->ping = 999;
		} else {
			cl->ping = total/count;
			if ( cl->ping > 999 ) {
				cl->ping = 999;
			}
		}

		// let the game dll know about the ping
		ps = SV_GameClientNum( i );
		ps->ping = cl->ping;
	}
}

/*
==================
SV_CountActiveHumanClients

Counts connected non-bot clients for retained empty-server policies.
==================
*/
static int SV_CountActiveHumanClients( void ) {
	int			i;
	int			count;
	client_t	*cl;

	count = 0;
	for ( i = 0, cl = svs.clients ; i < sv_maxclients->integer ; i++, cl++ ) {
		if ( cl->state >= CS_CONNECTED && !SV_ClientIsBot( cl ) ) {
			count++;
		}
	}

	return count;
}

/*
==================
SV_CheckTimeouts

If a packet has not been received from a client for timeout->integer 
seconds, drop the conneciton.  Server time is used instead of
realtime to avoid dropping the local client while debugging.

When a client is normally dropped, the client_t goes into a zombie state
for a few seconds to make sure any final reliable message gets resent
if necessary
==================
*/
void SV_CheckTimeouts( void ) {
	int		i;
	client_t	*cl;
	int			droppoint;
	int			zombiepoint;

	droppoint = svs.time - 1000 * sv_timeout->integer;
	zombiepoint = svs.time - 1000 * sv_zombietime->integer;

	for (i=0,cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {
		// message times may be wrong across a changelevel
		if (cl->lastPacketTime > svs.time) {
			cl->lastPacketTime = svs.time;
		}

		if (cl->state == CS_ZOMBIE
		&& cl->lastPacketTime < zombiepoint) {
			// using the client id cause the cl->name is empty at this point
			Com_DPrintf( "Going from CS_ZOMBIE to CS_FREE for client %d\n", i );
			cl->state = CS_FREE;	// can now be reused
			continue;
		}
		if ( cl->state >= CS_CONNECTED && cl->lastPacketTime < droppoint) {
			// wait several frames so a debugger session doesn't
			// cause a timeout
			if ( ++cl->timeoutCount > 5 ) {
				SV_DropClient (cl, "timed out"); 
				cl->state = CS_FREE;	// don't bother with zombie state
			}
		} else {
			cl->timeoutCount = 0;
		}
	}

	if ( SV_CountActiveHumanClients() > 0 ) {
		s_svEmptyServerTime = -1;
		return;
	}

	if ( s_svEmptyServerTime == -1 ) {
		s_svEmptyServerTime = svs.time;
		return;
	}

	if ( sv_quitOnEmpty && sv_quitOnEmpty->integer > 0 ) {
		int		quitPoint;

		quitPoint = svs.time - sv_quitOnEmpty->integer * 1000;
		if ( quitPoint > s_svEmptyServerTime ) {
			Com_Printf( "server has been empty for %d seconds, quit\n", sv_quitOnEmpty->integer );
			Cbuf_AddText( "quit\n" );
		}
	}
}


/*
==================
SV_CheckPaused
==================
*/
qboolean SV_CheckPaused( void ) {
	int		count;
	client_t	*cl;
	int		i;

	if ( !cl_paused->integer ) {
		return qfalse;
	}

	// only pause if there is just a single client connected
	count = 0;
	for (i=0,cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {
		if ( cl->state >= CS_CONNECTED && !SV_ClientIsBot( cl ) ) {
			count++;
		}
	}

	if ( count > 1 ) {
		// don't pause
		if (sv_paused->integer)
			Cvar_Set("sv_paused", "0");
		return qfalse;
	}

	if (!sv_paused->integer)
		Cvar_Set("sv_paused", "1");
	return qtrue;
}

/*
==================
SV_Frame

Player movement occurs as a result of packet events, which
happen before SV_Frame is called
==================
*/
void SV_Frame( int msec ) {
	int		frameMsec;
	int		startTime;
	int		i;
	client_t	*cl;
	char	*serverInfo;

	// the menu kills the server with this cvar
	if ( sv_killserver->integer ) {
		SV_Shutdown ("Server was killed.\n");
		Cvar_Set( "sv_killserver", "0" );
		return;
	}

	if ( !com_sv_running->integer ) {
		return;
	}

	SV_SteamServerNetworkingFrame();
	Zmq_UpdatePasswords();
	Zmq_PumpRcon();
	if ( svs.time < s_botMaskRefreshTime ) {
		s_botMaskRefreshTime = 0;
	}
	if ( svs.time - s_botMaskRefreshTime >= 10000 ) {
		// Keep entity SVF_BOT flags aligned with the live bot mask.
		s_botMaskRefreshTime = svs.time;
		for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
			if ( cl->state >= CS_CONNECTED ) {
				SV_BotRefreshEntityBotFlag( cl );
			}
		}
	}

	// allow pause if only the local client is connected
	if ( SV_CheckPaused() ) {
		return;
	}

	// if it isn't time for the next frame, do nothing
	if ( sv_fps->integer < 1 ) {
		Cvar_Set( "sv_fps", "10" );
	}
	frameMsec = 1000 / sv_fps->integer ;

	sv.timeResidual += msec;

	if (!com_dedicated->integer) SV_BotFrame( svs.time + sv.timeResidual );

	if ( com_dedicated->integer && sv.timeResidual < frameMsec ) {
		// NET_Sleep will give the OS time slices until either get a packet
		// or time enough for a server frame has gone by
		NET_Sleep(frameMsec - sv.timeResidual);
		return;
	}

	if ( sv_idleRestart && sv_idleRestart->integer && svs.time > 0x5265c00 && SV_CountActiveHumanClients() == 0 ) {
		SV_Shutdown( "Restarting idle server" );
		if ( SV_HandleQuitOnExitLevel( "idle server restart" ) ) {
			return;
		}
		Cbuf_AddText( "vstr nextmap\n" );
		return;
	}

	// if time is about to hit the 32nd bit, kick all clients
	// and clear sv.time, rather
	// than checking for negative time wraparound everywhere.
	// 2giga-milliseconds = 23 days, so it won't be too often
	if ( svs.time > 0x70000000 ) {
		SV_Shutdown( "Restarting server due to time wrapping" );
		if ( SV_HandleQuitOnExitLevel( "time wrapping restart" ) ) {
			return;
		}
		Cbuf_AddText( "vstr nextmap\n" );
		return;
	}
	// this can happen considerably earlier when lots of clients play and the map doesn't change
	if ( svs.nextSnapshotEntities >= 0x7FFFFFFE - svs.numSnapshotEntities ) {
		SV_Shutdown( "Restarting server due to numSnapshotEntities wrapping" );
		if ( SV_HandleQuitOnExitLevel( "numSnapshotEntities wrap restart" ) ) {
			return;
		}
		Cbuf_AddText( "vstr nextmap\n" );
		return;
	}

	if( sv.restartTime && svs.time >= sv.restartTime ) {
		if ( !SV_CheckWarmupReadiness( qtrue ) ) {
			sv.restartTime = svs.time + 1000;
			return;
		}
		sv.restartTime = 0;
		if ( SV_HandleQuitOnExitLevel( "scheduled map_restart" ) ) {
			return;
		}
		Cbuf_AddText( "map_restart 0\n" );
		return;
	}

	// update infostrings if anything has been changed
	if ( cvar_modifiedFlags & CVAR_SERVERINFO ) {
		serverInfo = Cvar_InfoString( CVAR_SERVERINFO );
		QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );
		SV_SetConfigstring( CS_SERVERINFO, serverInfo );
		cvar_modifiedFlags &= ~CVAR_SERVERINFO;
	}
	if ( cvar_modifiedFlags & CVAR_SYSTEMINFO ) {
		SV_SetConfigstring( CS_SYSTEMINFO, Cvar_InfoString_Big( CVAR_SYSTEMINFO ) );
		cvar_modifiedFlags &= ~CVAR_SYSTEMINFO;
	}

	SV_SteamServerUpdatePublishedState( qfalse );

	if ( com_speeds->integer ) {
		startTime = Sys_Milliseconds ();
	} else {
		startTime = 0;	// quite a compiler warning
	}

	// update ping based on the all received frames
	SV_CalcPings();

	if (com_dedicated->integer) SV_BotFrame( svs.time );

	// run the game simulation in chunks
	while ( sv.timeResidual >= frameMsec ) {
		sv.timeResidual -= frameMsec;
		svs.time += frameMsec;

		// let everything in the world think and move
		VM_Call( gvm, GAME_RUN_FRAME, svs.time );
	}

	if ( com_speeds->integer ) {
		time_game = Sys_Milliseconds () - startTime;
	}

	// check timeouts
	SV_CheckTimeouts();

	// send messages back to the clients
	SV_SendClientMessages();

	// send a heartbeat to the master if needed
	SV_MasterHeartbeat();
}

//============================================================================

