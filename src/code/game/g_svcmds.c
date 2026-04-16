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

// this file holds commands that can be executed by the server console, but not remote clients

#include <stdlib.h>
#include "g_local.h"


/*
==============================================================================

PACKET FILTERING
 

You can add or remove addresses from the filter list with:

addip <ip>
removeip <ip>

The ip address is specified in dot format, and you can use '*' to match any value
so you can specify an entire class C network with "addip 192.246.40.*"

Removeip will only remove an address specified exactly the same way.  You cannot addip a subnet, then removeip a single host.

listip
Prints the current list of filters.

g_filterban <0 or 1>

If 1 (the default), then ip addresses matching the current list will be prohibited from entering the game.  This is the default setting.

If 0, then only addresses matching the list will be allowed.  This lets you easily set up a private game, or a game that only allows players from your local network.

TTimo NOTE: for persistence, bans are stored in g_banIPs cvar MAX_CVAR_VALUE_STRING
The size of the cvar string buffer is limiting the banning to around 20 masks
this could be improved by putting some g_banIPs2 g_banIps3 etc. maybe
still, you should rely on PB for banning instead

==============================================================================
*/

typedef struct ipFilter_s
{
	unsigned	mask;
	unsigned	compare;
} ipFilter_t;

#define	MAX_IPFILTERS	1024

static ipFilter_t	ipFilters[MAX_IPFILTERS];
static int			numIPFilters;

/*
=================
StringToFilter
=================
*/
static qboolean StringToFilter (char *s, ipFilter_t *f)
{
	char	num[128];
	int		i, j;
	byte	b[4];
	byte	m[4];
	
	for (i=0 ; i<4 ; i++)
	{
		b[i] = 0;
		m[i] = 0;
	}
	
	for (i=0 ; i<4 ; i++)
	{
		if (*s < '0' || *s > '9')
		{
			if (*s == '*') // 'match any'
			{
				// b[i] and m[i] to 0
				s++;
				if (!*s)
					break;
				s++;
				continue;
			}
			G_Printf( "Bad filter address: %s\n", s );
			return qfalse;
		}
		
		j = 0;
		while (*s >= '0' && *s <= '9')
		{
			num[j++] = *s++;
		}
		num[j] = 0;
		b[i] = atoi(num);
		m[i] = 255;

		if (!*s)
			break;
		s++;
	}
	
	f->mask = *(unsigned *)m;
	f->compare = *(unsigned *)b;
	
	return qtrue;
}

/*
=================
UpdateIPBans
=================
*/
static void UpdateIPBans (void)
{
	byte	b[4];
	byte	m[4];
	int		i,j;
	char	iplist_final[MAX_CVAR_VALUE_STRING];
	char	ip[64];

	*iplist_final = 0;
	for (i = 0 ; i < numIPFilters ; i++)
	{
		if (ipFilters[i].compare == 0xffffffff)
			continue;

		*(unsigned *)b = ipFilters[i].compare;
		*(unsigned *)m = ipFilters[i].mask;
		*ip = 0;
		for (j = 0 ; j < 4 ; j++)
		{
			if (m[j]!=255)
				Q_strcat(ip, sizeof(ip), "*");
			else
				Q_strcat(ip, sizeof(ip), va("%i", b[j]));
			Q_strcat(ip, sizeof(ip), (j<3) ? "." : " ");
		}		
		if (strlen(iplist_final)+strlen(ip) < MAX_CVAR_VALUE_STRING)
		{
			Q_strcat( iplist_final, sizeof(iplist_final), ip);
		}
		else
		{
			Com_Printf("g_banIPs overflowed at MAX_CVAR_VALUE_STRING\n");
			break;
		}
	}

	trap_Cvar_Set( "g_banIPs", iplist_final );
}

/*
=================
G_FilterPacket
=================
*/
qboolean G_FilterPacket (char *from)
{
	int		i;
	unsigned	in;
	byte m[4];
	char *p;

	i = 0;
	p = from;
	while (*p && i < 4) {
		m[i] = 0;
		while (*p >= '0' && *p <= '9') {
			m[i] = m[i]*10 + (*p - '0');
			p++;
		}
		if (!*p || *p == ':')
			break;
		i++, p++;
	}
	
	in = *(unsigned *)m;

	for (i=0 ; i<numIPFilters ; i++)
		if ( (in & ipFilters[i].mask) == ipFilters[i].compare)
			return g_filterBan.integer != 0;

	return g_filterBan.integer == 0;
}

/*
=================
AddIP
=================
*/
static void AddIP( char *str )
{
	int		i;

	for (i = 0 ; i < numIPFilters ; i++)
		if (ipFilters[i].compare == 0xffffffff)
			break;		// free spot
	if (i == numIPFilters)
	{
		if (numIPFilters == MAX_IPFILTERS)
		{
			G_Printf ("IP filter list is full\n");
			return;
		}
		numIPFilters++;
	}
	
	if (!StringToFilter (str, &ipFilters[i]))
		ipFilters[i].compare = 0xffffffffu;

	UpdateIPBans();
}

/*
=================
G_ProcessIPBans
=================
*/
void G_ProcessIPBans(void) 
{
	char *s, *t;
	char		str[MAX_CVAR_VALUE_STRING];

	Q_strncpyz( str, g_banIPs.string, sizeof(str) );

	for (t = s = g_banIPs.string; *t; /* */ ) {
		s = strchr(s, ' ');
		if (!s)
			break;
		while (*s == ' ')
			*s++ = 0;
		if (*t)
			AddIP( t );
		t = s;
	}
}


/*
=================
Svcmd_AddIP_f
=================
*/
void Svcmd_AddIP_f (void)
{
	char		str[MAX_TOKEN_CHARS];

	if ( trap_Argc() < 2 ) {
		G_Printf("Usage:  addip <ip-mask>\n");
		return;
	}

	trap_Argv( 1, str, sizeof( str ) );

	AddIP( str );

}

/*
=================
Svcmd_RemoveIP_f
=================
*/
void Svcmd_RemoveIP_f (void)
{
	ipFilter_t	f;
	int			i;
	char		str[MAX_TOKEN_CHARS];

	if ( trap_Argc() < 2 ) {
		G_Printf("Usage:  sv removeip <ip-mask>\n");
		return;
	}

	trap_Argv( 1, str, sizeof( str ) );

	if (!StringToFilter (str, &f))
		return;

	for (i=0 ; i<numIPFilters ; i++) {
		if (ipFilters[i].mask == f.mask	&&
			ipFilters[i].compare == f.compare) {
			ipFilters[i].compare = 0xffffffffu;
			G_Printf ("Removed.\n");

			UpdateIPBans();
			return;
		}
	}

	G_Printf ( "Didn't find %s.\n", str );
}

/*
===================
Svcmd_EntityList_f
===================
*/
void	Svcmd_EntityList_f (void) {
	int			e;
	gentity_t		*check;

	check = g_entities+1;
	for (e = 1; e < level.num_entities ; e++, check++) {
		if ( !check->inuse ) {
			continue;
		}
		G_Printf("%3i:", e);
		switch ( check->s.eType ) {
		case ET_GENERAL:
			G_Printf("ET_GENERAL          ");
			break;
		case ET_PLAYER:
			G_Printf("ET_PLAYER           ");
			break;
		case ET_ITEM:
			G_Printf("ET_ITEM             ");
			break;
		case ET_MISSILE:
			G_Printf("ET_MISSILE          ");
			break;
		case ET_MOVER:
			G_Printf("ET_MOVER            ");
			break;
		case ET_BEAM:
			G_Printf("ET_BEAM             ");
			break;
		case ET_PORTAL:
			G_Printf("ET_PORTAL           ");
			break;
		case ET_SPEAKER:
			G_Printf("ET_SPEAKER          ");
			break;
		case ET_PUSH_TRIGGER:
			G_Printf("ET_PUSH_TRIGGER     ");
			break;
		case ET_TELEPORT_TRIGGER:
			G_Printf("ET_TELEPORT_TRIGGER ");
			break;
		case ET_INVISIBLE:
			G_Printf("ET_INVISIBLE        ");
			break;
		case ET_GRAPPLE:
			G_Printf("ET_GRAPPLE          ");
			break;
		default:
			G_Printf("%3i                 ", check->s.eType);
			break;
		}

		if ( check->classname ) {
			G_Printf("%s", check->classname);
		}
		G_Printf("\n");
	}
}

gclient_t	*ClientForString( const char *s ) {
	gclient_t	*cl;
	int			i;
	int			idnum;

	// numeric values are just slot numbers
	if ( s[0] >= '0' && s[0] <= '9' ) {
		idnum = atoi( s );
		if ( idnum < 0 || idnum >= level.maxclients ) {
			Com_Printf( "Bad client slot: %i\n", idnum );
			return NULL;
		}

		cl = &level.clients[idnum];
		if ( cl->pers.connected == CON_DISCONNECTED ) {
			G_Printf( "Client %i is not connected\n", idnum );
			return NULL;
		}
		return cl;
	}

	// check for a name match
	for ( i=0 ; i < level.maxclients ; i++ ) {
		cl = &level.clients[i];
		if ( cl->pers.connected == CON_DISCONNECTED ) {
			continue;
		}
		if ( !Q_stricmp( cl->pers.netname, s ) ) {
			return cl;
		}
	}

	G_Printf( "User %s is not on the server\n", s );

	return NULL;
}

/*
===================
Svcmd_DumpVars_f

Prints a compact playerstate snapshot for the selected client.
===================
*/
static void Svcmd_DumpVars_f( void ) {
	gclient_t	*cl;
	char		str[MAX_TOKEN_CHARS];

	trap_Argv( 1, str, sizeof( str ) );
	cl = ClientForString( str );
	if ( !cl ) {
		return;
	}

	G_Printf( "Data Dump: (%s)\n", cl->pers.netname );
	G_Printf( "clientNum: %d\n", ( int )( cl - level.clients ) );
	G_Printf( "pm_type: 0x%08x\n", cl->ps.pm_type );
	G_Printf( "pm_flags: 0x%08x\n", cl->ps.pm_flags );
	G_Printf( "pm_time: %d\n", cl->ps.pm_time );
	G_Printf( "eFlags: %d\n", cl->ps.eFlags );
	G_Printf( "origin: (%0.3f, %0.3f, %0.3f)\n", cl->ps.origin[0], cl->ps.origin[1], cl->ps.origin[2] );
}

/*
===================
Svcmd_EntityDebug_f

Prints the retained entity parse/spawn summary and optional per-class counts.
===================
*/
static void Svcmd_EntityDebug_f( void ) {
	char		mode[MAX_TOKEN_CHARS];
	qboolean	includeClasses;

	includeClasses = qfalse;
	if ( trap_Argc() > 1 ) {
		trap_Argv( 1, mode, sizeof( mode ) );
		if ( !Q_stricmp( mode, "classes" ) || !Q_stricmp( mode, "all" ) ) {
			includeClasses = qtrue;
		}
	}

	G_EntityDebug_PrintSummary( includeClasses );
}

/*
===================
Svcmd_ForceTeam_f

forceteam <player> <team>
===================
*/
void	Svcmd_ForceTeam_f( void ) {
	gclient_t	*cl;
	char		str[MAX_TOKEN_CHARS];

	// find the player
	trap_Argv( 1, str, sizeof( str ) );
	cl = ClientForString( str );
	if ( !cl ) {
		return;
	}

	// set the team
	trap_Argv( 2, str, sizeof( str ) );
	SetTeam( &g_entities[cl - level.clients], str );
}

/*
=============
Svcmd_GameCrash_f

Mirrors the retail developer-only hard crash path exposed through ConsoleCommand.
=============
*/
static void Svcmd_GameCrash_f( void ) {
	if ( trap_Cvar_VariableIntegerValue( "developer" ) < 1 ) {
		return;
	}

	*(volatile int *)0 = 0x12345678;
}

/*
=============
Svcmd_ReloadAccess_f

Reloads the cached access list and refreshes connected-client privilege tiers.
=============
*/
static void Svcmd_ReloadAccess_f( void ) {
	G_ReloadAdminAccess();
}

/*
=============
Svcmd_FloodStatus_f

Reports the current flood protection counters for each connected client.
=============
*/
static void Svcmd_FloodStatus_f( void ) {
	int			maxCount;
	int			decay;
	int			visibleClients;
	qboolean	found;
	int			i;

	maxCount = g_floodprot_maxcount.integer;
	decay = g_floodprot_decay.integer;
	if ( maxCount <= 0 || decay <= 0 ) {
		G_Printf( "Flood protection is disabled. Set g_floodprot_maxcount and g_floodprot_decay to enable it.\n" );
		return;
	}

	G_Printf( "Flood protection window: %d uses / %dms decay / drop-on-overflow\n", maxCount, decay );
	found = qfalse;
	visibleClients = 0;

	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t       *cl;
		char            lastBuffer[32];
		const char      *lastDesc;
		const char      *state;
		int             sinceLast;

		cl = &level.clients[i];
		if ( cl->pers.connected == CON_DISCONNECTED ) {
			continue;
		}

		visibleClients++;
		sinceLast = ( cl->floodLastTime > 0 ) ? level.time - cl->floodLastTime : -1;
		if ( sinceLast >= 0 ) {
			Com_sprintf( lastBuffer, sizeof( lastBuffer ), "%ims ago", sinceLast );
			lastDesc = lastBuffer;
		} else {
			lastDesc = "no activity";
		}

		if ( cl->floodCount <= 0 ) {
			continue;
		}

		state = ( cl->floodCount > maxCount ) ? "pending_drop" : "tracking";
		found = qtrue;
		G_Printf( "#%i %s: count=%i state=%s last=%s\n", i, cl->pers.netname, cl->floodCount, state, lastDesc );
	}

	if ( !found ) {
		if ( visibleClients > 0 ) {
			G_Printf( "No clients currently have flood counters pending decay or drop.\n" );
		} else {
			G_Printf( "No active clients to report.\n" );
		}
	}
}

char	*ConcatArgs( int start );

/*
=================
Svcmd_TeamSize_f
=================
*/
void Svcmd_TeamSize_f( void ) {
	char	str[MAX_TOKEN_CHARS];
	int		size;

	if ( trap_Argc() < 2 ) {
		G_Printf("Usage:  teamsize <size>\n");
		return;
	}

	trap_Argv( 1, str, sizeof( str ) );
	size = atoi( str );

	if ( size < 0 ) {
		size = 0;
	}

	trap_Cvar_Set( "g_teamSizeMin", va("%i", size) );
}

/*
=================
Cmd_CoinToss_f
=================
*/
void Cmd_CoinToss_f( void ) {
	int result = rand() % 2;
	trap_SendServerCommand( -1, va("cp \"Coin Toss: %s\n\"", result ? "HEADS" : "TAILS" ) );
	trap_SendServerCommand( -1, va("print \"Coin Toss: %s\n\"", result ? "HEADS" : "TAILS" ) );
}

/*
=================
Cmd_RandomMap_f
=================
*/
void Cmd_RandomMap_f( void ) {
	// For now, this just restarts the map as we don't have a map list loaded
	// Ideally this would pick from a map cycle
	trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
}

/*
=================
Svcmd_ScorestatsDump_f

Pushes a full scoreboard refresh so scorestats-side ownerdraw payloads can be inspected at runtime.
=================
*/
static void Svcmd_ScorestatsDump_f( void ) {
	SendScoreboardMessageToAllClients();
}

/*
=================
ConsoleCommand

=================
*/
qboolean	ConsoleCommand( void ) {
	char	cmd[MAX_TOKEN_CHARS];
	char	arg[MAX_TOKEN_CHARS];

	trap_Argv( 0, cmd, sizeof( cmd ) );

	if ( Q_stricmp (cmd, "entitylist") == 0 ) {
		Svcmd_EntityList_f();
		return qtrue;
	}
	if ( Q_stricmp( cmd, "entitydebug" ) == 0 ) {
		Svcmd_EntityDebug_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "forceteam") == 0 ) {
		Svcmd_ForceTeam_f();
		return qtrue;
	}
	if (Q_stricmp (cmd, "game_memory") == 0) {
		Svcmd_GameMem_f();
		return qtrue;
	}
	if (Q_stricmp (cmd, "addbot") == 0) {
		Svcmd_AddBot_f();
		return qtrue;
	}
	if (Q_stricmp (cmd, "botlist") == 0) {
		Svcmd_BotList_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "game_crash") == 0 ) {
		Svcmd_GameCrash_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "forceshuffle") == 0 ) {
		Cmd_ShuffleTeams_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "dumpvars") == 0 ) {
		Svcmd_DumpVars_f();
		return qtrue;
	}
	// Retail qagame still recognizes these legacy debug tokens, but the
	// committed HLIL shows them resolving to a handled no-op inside
	// ConsoleCommand rather than to a separate worker body.
	if ( Q_stricmp( cmd, "markstate" ) == 0 ||
		Q_stricmp( cmd, "diffstate" ) == 0 ||
		Q_stricmp( cmd, "dumpentities" ) == 0 ||
		Q_stricmp( cmd, "printentitystates" ) == 0 ) {
		return qtrue;
	}
	if ( Q_stricmp (cmd, "reload_access") == 0 ) {
		Svcmd_ReloadAccess_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "shuffle_teams") == 0 ) {
		Cmd_ShuffleTeams_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "teamsize") == 0 ) {
		Svcmd_TeamSize_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "cointoss") == 0 ) {
		Cmd_CoinToss_f();
		return qtrue;
	}
	if ( Q_stricmp (cmd, "randommap") == 0 ) {
		Cmd_RandomMap_f();
		return qtrue;
	}
	if ( Q_stricmp( cmd, "scorestats_dump" ) == 0 ) {
		Svcmd_ScorestatsDump_f();
		return qtrue;
	}
	if ( Q_stricmp( cmd, "floodstatus" ) == 0 ) {
		Svcmd_FloodStatus_f();
		return qtrue;
	}
	if (Q_stricmp (cmd, "abort_podium") == 0) {
		Svcmd_AbortPodium_f();
		return qtrue;
	}

	if ( Q_stricmp( cmd, "reload_factories" ) == 0 ) {
		Factory_Reload_f();
		return qtrue;
	}

	if (Q_stricmp (cmd, "addip") == 0) {
		Svcmd_AddIP_f();
		return qtrue;
	}

	if (Q_stricmp (cmd, "removeip") == 0) {
		Svcmd_RemoveIP_f();
		return qtrue;
	}

	if (Q_stricmp (cmd, "listip") == 0) {
		trap_SendConsoleCommand( EXEC_NOW, "g_banIPs\n" );
		return qtrue;
	}

	if ( Q_stricmp( cmd, "racepoint" ) == 0 ) {
		if ( g_gametype.integer != GT_RACE ) {
			G_Printf( GAMEPRINT_RACEPOINT_RACE_ONLY );
			return qtrue;
		}

		if ( trap_Argc() > 1 ) {
			trap_Argv( 1, arg, sizeof( arg ) );
			if ( !Q_stricmp( arg, "clear" ) ) {
				G_RaceServerClearPoints();
				return qtrue;
			}

			if ( !Q_stricmp( arg, "dump" ) ) {
				G_RaceServerDumpPoints();
				return qtrue;
			}
		}

		G_Printf( "RacePoint spawns must be issued by a player.\n" );
		return qtrue;
	}

	if ( Q_stricmp( cmd, "race_init" ) == 0 ) {
		if ( g_gametype.integer == GT_RACE ) {
			G_RaceBroadcastInitCommand( -1 );
		}
		return qtrue;
	}

	if ( Q_stricmp( cmd, "race_info" ) == 0 ) {
		if ( g_gametype.integer == GT_RACE ) {
			G_RaceSendInfoCommand( -1 );
		}
		return qtrue;
	}

	if ( !Q_stricmpn( cmd, "admin_race_point_", 17 ) ) {
		if ( g_gametype.integer == GT_RACE ) {
			int index = atoi( cmd + 17 );
			if ( !G_RaceSendPointMetadataCommand( -1, index ) ) {
				G_Printf( GAMEPRINT_RACEPOINT_INVALID_INDEX, index );
			}
		} else {
			G_Printf( GAMEPRINT_RACEPOINT_RACE_ONLY );
		}
		return qtrue;
	}

	if (g_dedicated.integer) {
		if (Q_stricmp (cmd, "say") == 0) {
			trap_SendServerCommand( -1, va("print \"server: %s\"", ConcatArgs(1) ) );
			return qtrue;
		}
		// everything else will also be printed as a say command
		trap_SendServerCommand( -1, va("print \"server: %s\"", ConcatArgs(0) ) );
		return qtrue;
	}

	return qfalse;
}

