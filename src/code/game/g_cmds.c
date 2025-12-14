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
#include "g_match_config.h"

#include "../../ui/menudef.h"			// for the voice chats

/*
==================
DeathmatchScoreboardMessage

==================
*/
void DeathmatchScoreboardMessage( gentity_t *ent ) {
	char		entry[1024];
	char		string[1400];
	int			stringlength;
	int			i, j;
	gclient_t	*cl;
	int			numSorted, scoreFlags, accuracy, perfect;

	// send the latest information on all clients
	string[0] = 0;
	stringlength = 0;
	scoreFlags = 0;

	numSorted = level.numConnectedClients;
	
	for (i=0 ; i < numSorted ; i++) {
		int		ping;

		cl = &level.clients[level.sortedClients[i]];

		if ( cl->pers.connected == CON_CONNECTING ) {
			ping = -1;
		} else {
			ping = cl->ps.ping < 999 ? cl->ps.ping : 999;
		}

		if( cl->accuracy_shots ) {
			accuracy = cl->accuracy_hits * 100 / cl->accuracy_shots;
		}
		else {
			accuracy = 0;
		}
		perfect = ( cl->ps.persistant[PERS_RANK] == 0 && cl->ps.persistant[PERS_KILLED] == 0 ) ? 1 : 0;

		Com_sprintf (entry, sizeof(entry),
			" %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i", level.sortedClients[i],
			cl->ps.persistant[PERS_SCORE], ping, (level.time - cl->pers.enterTime)/60000,
			scoreFlags, g_entities[level.sortedClients[i]].s.powerups, accuracy, 
			cl->ps.persistant[PERS_IMPRESSIVE_COUNT],
			cl->ps.persistant[PERS_EXCELLENT_COUNT],
			cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT], 
			cl->ps.persistant[PERS_DEFEND_COUNT], 
			cl->ps.persistant[PERS_ASSIST_COUNT], 
			perfect,
			cl->ps.persistant[PERS_CAPTURES],
			cl->pers.damageGiven);
		j = strlen(entry);
		if (stringlength + j > 1024)
			break;
		strcpy (string + stringlength, entry);
		stringlength += j;
	}

	trap_SendServerCommand( ent-g_entities, va("scores %i %i %i%s", i, 
		level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE],
		string ) );
}


/*
==================
Cmd_Score_f

Request current scoreboard information
==================
*/
void Cmd_Score_f( gentity_t *ent ) {
	if ( g_gametype.integer == GT_RACE ) {
		G_RaceSendScoreboard( ent );
		return;
	}

	DeathmatchScoreboardMessage( ent );
}

/*
==================
Cmd_Ready_f
==================
*/
void Cmd_Ready_f( gentity_t *ent ) {
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot ready up.\n\"" );
		return;
	}

	if ( level.warmupTime == 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"The match has already started.\n\"" );
		return;
	}

	if ( ent->client->ps.eFlags & EF_READY ) {
		trap_SendServerCommand( ent-g_entities, "print \"You are already ready.\n\"" );
		return;
	}

	ent->client->ps.eFlags |= EF_READY;
	trap_SendServerCommand( ent-g_entities, "print \"You are now ready.\n\"" );

	// check if everyone is ready
	// This logic might need to be in G_CheckWarmup or similar
}

/*
==================
Cmd_NotReady_f
==================
*/
void Cmd_NotReady_f( gentity_t *ent ) {
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot ready up.\n\"" );
		return;
	}

	if ( level.warmupTime <= 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"The match has already started.\n\"" );
		return;
	}

	if ( !(ent->client->ps.eFlags & EF_READY) ) {
		trap_SendServerCommand( ent-g_entities, "print \"You are already not ready.\n\"" );
		return;
	}

	ent->client->ps.eFlags &= ~EF_READY;
	trap_SendServerCommand( ent-g_entities, "print \"You are now not ready.\n\"" );
}

/*
==================
Cmd_Players_f
==================
*/
void Cmd_Players_f( gentity_t *ent ) {
	int		i;
	gclient_t	*cl;
	int		score;
	int		ping;
	char	*s;
	char	cleanName[MAX_NETNAME];

	trap_SendServerCommand( ent-g_entities, "print \"  ID Score Ping Name            \n\"" );
	trap_SendServerCommand( ent-g_entities, "print \"------------------------------\n\"" );

	for ( i=0 ; i < level.maxclients ; i++ ) {
		cl = &level.clients[i];
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}

		score = cl->ps.persistant[PERS_SCORE];
		ping = cl->ps.ping < 999 ? cl->ps.ping : 999;

		// QL style output
		s = cl->pers.netname;
		// sanitize name for display if needed
		Q_strncpyz( cleanName, s, sizeof(cleanName) );
		Q_CleanStr( cleanName );

		trap_SendServerCommand( ent-g_entities, va("print \"  %2i %5i %4i %s\n\"",
			i, score, ping, cleanName) );
	}
}

/*
==================
Cmd_Teams_f
==================
*/
void Cmd_Teams_f( gentity_t *ent ) {
	char	*str;

	if ( g_gametype.integer < GT_TEAM ) {
		trap_SendServerCommand( ent-g_entities, "print \"Teams are not enabled in this gametype.\n\"" );
		return;
	}

	trap_SendServerCommand( ent-g_entities, va("print \"Red Team: %i\n\"", level.teamScores[TEAM_RED] ) );
	trap_SendServerCommand( ent-g_entities, va("print \"Blue Team: %i\n\"", level.teamScores[TEAM_BLUE] ) );
}

/*
=================
Cmd_Acc_f
=================
*/
void Cmd_Acc_f( gentity_t *ent ) {
	int accuracy;

	if ( !ent->client ) {
		return;
	}

	if ( ent->client->accuracy_shots ) {
		accuracy = ent->client->accuracy_hits * 100 / ent->client->accuracy_shots;
	} else {
		accuracy = 0;
	}

	trap_SendServerCommand( ent-g_entities, va("print \"Accuracy: %i%% (%i hits / %i shots)\n\"",
		accuracy, ent->client->accuracy_hits, ent->client->accuracy_shots) );
}

/*
=================
Cmd_Cvar_f
=================
*/
void Cmd_Cvar_f( gentity_t *ent ) {
	char	arg[MAX_TOKEN_CHARS];
	char	val[MAX_TOKEN_CHARS];

	if ( trap_Argc() != 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: cvar <cvarname>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );

	// only allow checking safe cvars
	if ( Q_stricmp( arg, "g_gametype" ) &&
		 Q_stricmp( arg, "timelimit" ) &&
		 Q_stricmp( arg, "fraglimit" ) &&
		 Q_stricmp( arg, "capturelimit" ) &&
		 Q_stricmp( arg, "g_friendlyFire" ) &&
		 Q_stricmp( arg, "g_gravity" ) &&
		 Q_stricmp( arg, "g_speed" ) &&
		 Q_stricmp( arg, "g_knockback" ) &&
		 Q_stricmp( arg, "g_quadfactor" ) &&
		 Q_stricmp( arg, "g_weaponRespawn" ) &&
		 Q_stricmp( arg, "g_forcerespawn" ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Cvar is not public.\n\"" );
		return;
	}

	trap_Cvar_VariableStringBuffer( arg, val, sizeof( val ) );
	trap_SendServerCommand( ent-g_entities, va("print \"Cvar %s = %s\n\"", arg, val) );
}


/*
==================
CheatsOk
==================
*/
qboolean	CheatsOk( gentity_t *ent ) {
	if ( !g_cheats.integer ) {
		trap_SendServerCommand( ent-g_entities, va("print \"Cheats are not enabled on this server.\n\""));
		return qfalse;
	}
	if ( ent->health <= 0 ) {
		trap_SendServerCommand( ent-g_entities, va("print \"You must be alive to use this command.\n\""));
		return qfalse;
	}
	return qtrue;
}


/*
==================
ConcatArgs
==================
*/
char	*ConcatArgs( int start ) {
	int		i, c, tlen;
	static char	line[MAX_STRING_CHARS];
	int		len;
	char	arg[MAX_STRING_CHARS];

	len = 0;
	c = trap_Argc();
	for ( i = start ; i < c ; i++ ) {
		trap_Argv( i, arg, sizeof( arg ) );
		tlen = strlen( arg );
		if ( len + tlen >= MAX_STRING_CHARS - 1 ) {
			break;
		}
		memcpy( line + len, arg, tlen );
		len += tlen;
		if ( i != c - 1 ) {
			line[len] = ' ';
			len++;
		}
	}

	line[len] = 0;

	return line;
}

/*
============
G_FloodLimited

Applies the configured flood control policy and optionally records a usage.
============
*/
static qboolean G_FloodLimited( gentity_t *ent, const char *action, qboolean recordUsage ) {
	gclient_t		*client;
	const char	*label;
	int		maxCount;
	int		decay;

	if ( !ent || !ent->client ) {
		return qfalse;
	}

	maxCount = g_floodprot_maxcount.integer;
	decay = g_floodprot_decay.integer;
	if ( maxCount <= 0 || decay <= 0 ) {
		return qfalse;
	}

	client = ent->client;
	label = ( action && action[0] ) ? action : "issuing commands";

	if ( client->floodPenaltyTime > level.time ) {
		const int	remainingMs = client->floodPenaltyTime - level.time;
		const int	remainingSeconds = ( remainingMs + 999 ) / 1000;

		trap_SendServerCommand( ent - g_entities,
			va( "print \"Flood protection: wait %d second%s before %s.\\n\"",
			remainingSeconds, ( remainingSeconds == 1 ) ? "" : "s", label ) );
		return qtrue;
	}

	if ( !recordUsage ) {
		return qfalse;
	}

	if ( client->floodLastTime > 0 ) {
		const int elapsed = level.time - client->floodLastTime;
		if ( elapsed > 0 ) {
			int reduction = elapsed / decay;
			if ( reduction > 0 ) {
				client->floodCount -= reduction;
				if ( client->floodCount < 0 ) {
					client->floodCount = 0;
				}
			}
		}
	}

	client->floodLastTime = level.time;
	client->floodCount++;
	if ( client->floodCount > maxCount ) {
		int penalty = g_floodprot_penalty.integer;
		if ( penalty <= 0 ) {
			penalty = decay * maxCount;
			if ( penalty <= 0 ) {
				penalty = decay;
			}
		}

		client->floodPenaltyTime = level.time + penalty;
		client->floodCount = 0;

		trap_SendServerCommand( ent - g_entities,
			va( "print \"Flood protection triggered. Please wait %d second%s before %s.\\n\"",
			( penalty + 999 ) / 1000, ( ( penalty + 999 ) / 1000 ) == 1 ? "" : "s", label ) );
		G_LogPrintf( "floodprot: client %i (%s) blocked for %dms via %s\n",
			ent - g_entities, client->pers.netname, penalty, label );
		return qtrue;
	}

	return qfalse;
}
/*
=============
G_ClampItemTimerHeight

Ensures the timer height sent to clients always uses a sensible fallback and sane upper bound.
=============
*/
static int G_ClampItemTimerHeight( int rawHeight ) {
	if ( rawHeight <= 0 ) {
		return ITEM_TIMER_DEFAULT_HEIGHT;
	}

	if ( rawHeight > ITEM_TIMER_MAX_HEIGHT ) {
		return ITEM_TIMER_MAX_HEIGHT;
	}

	return rawHeight;
}


/*
=============
G_SendItemTimerState

Sends the current item timer configuration to a single client.
=============
*/
void G_SendItemTimerState( int clientNum, int enabled, int height ) {
	int	clampedHeight;

	clampedHeight = G_ClampItemTimerHeight( height );
	trap_SendServerCommand( clientNum, va( "itemcfg %i %i", enabled ? 1 : 0, clampedHeight ) );
}

/*
=============
G_BroadcastItemTimerState

Broadcasts the current item timer configuration to every connected client.
=============
*/
void G_BroadcastItemTimerState( int enabled, int height ) {
	G_SendItemTimerState( -1, enabled, height );
}


/*
==================
SanitizeString

Remove case and control characters
==================
*/
void SanitizeString( char *in, char *out ) {
	while ( *in ) {
		if ( *in == 27 ) {
			in += 2;		// skip color code
			continue;
		}
		if ( *in < 32 ) {
			in++;
			continue;
		}
		*out++ = tolower( *in++ );
	}

	*out = 0;
}

/*
==================
ClientNumberFromString

Returns a player number for either a number or name string
Returns -1 if invalid
==================
*/
int ClientNumberFromString( gentity_t *to, char *s ) {
	gclient_t	*cl;
	int			idnum;
	char		s2[MAX_STRING_CHARS];
	char		n2[MAX_STRING_CHARS];

	// numeric values are just slot numbers
	if (s[0] >= '0' && s[0] <= '9') {
		idnum = atoi( s );
		if ( idnum < 0 || idnum >= level.maxclients ) {
			trap_SendServerCommand( to-g_entities, va("print \"Bad client slot: %i\n\"", idnum));
			return -1;
		}

		cl = &level.clients[idnum];
		if ( cl->pers.connected != CON_CONNECTED ) {
			trap_SendServerCommand( to-g_entities, va("print \"Client %i is not active\n\"", idnum));
			return -1;
		}
		return idnum;
	}

	// check for a name match
	SanitizeString( s, s2 );
	for ( idnum=0,cl=level.clients ; idnum < level.maxclients ; idnum++,cl++ ) {
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		SanitizeString( cl->pers.netname, n2 );
		if ( !strcmp( n2, s2 ) ) {
			return idnum;
		}
	}

	trap_SendServerCommand( to-g_entities, va("print \"User %s is not on the server\n\"", s));
	return -1;
}


/*
=============
G_GiveItemByName

Grants inventory matching the `give` command tokens so non-cheat code paths can reuse the logic.
=============
*/
qboolean G_GiveItemByName( gentity_t *ent, const char *name ) {
	gitem_t		*it;
	gentity_t	*it_ent;
	trace_t	trace;
	int			 i;

	if ( !ent || !ent->client || !name || !name[0] ) {
		return qfalse;
	}

	if ( Q_stricmp( name, "health" ) == 0 ) {
		ent->health = ent->client->ps.stats[STAT_MAX_HEALTH];
		return qtrue;
	}

	if ( Q_stricmp( name, "weapons" ) == 0 ) {
		ent->client->ps.stats[STAT_WEAPONS] = ( 1 << WP_NUM_WEAPONS ) - 1 - ( 1 << WP_GRAPPLING_HOOK ) - ( 1 << WP_NONE );
		return qtrue;
	}

	if ( Q_stricmp( name, "ammo" ) == 0 ) {
		for ( i = 0 ; i < MAX_WEAPONS ; i++ ) {
			ent->client->ps.ammo[i] = 999;
		}
		return qtrue;
	}

	if ( Q_stricmp( name, "armor" ) == 0 ) {
		ent->client->ps.stats[STAT_ARMOR] = 200;
		return qtrue;
	}

	if ( Q_stricmp( name, "excellent" ) == 0 ) {
		ent->client->ps.persistant[PERS_EXCELLENT_COUNT]++;
		return qtrue;
	}
	if ( Q_stricmp( name, "impressive" ) == 0 ) {
		ent->client->ps.persistant[PERS_IMPRESSIVE_COUNT]++;
		return qtrue;
	}
	if ( Q_stricmp( name, "gauntletaward" ) == 0 ) {
		ent->client->ps.persistant[PERS_GAUNTLET_FRAG_COUNT]++;
		return qtrue;
	}
	if ( Q_stricmp( name, "defend" ) == 0 ) {
		ent->client->ps.persistant[PERS_DEFEND_COUNT]++;
		return qtrue;
	}
	if ( Q_stricmp( name, "assist" ) == 0 ) {
		ent->client->ps.persistant[PERS_ASSIST_COUNT]++;
		return qtrue;
	}

	it = BG_FindItem( name );
	if ( !it ) {
		return qfalse;
	}

	it_ent = G_Spawn();
	VectorCopy( ent->r.currentOrigin, it_ent->s.origin );
	it_ent->classname = it->classname;
	G_SpawnItem( it_ent, it );
	FinishSpawningItem( it_ent );
	memset( &trace, 0, sizeof( trace ) );
	Touch_Item( it_ent, ent, &trace );
	if ( it_ent->inuse ) {
		G_FreeEntity( it_ent );
	}

	return qtrue;
}

/*
==================
Cmd_Give_f

Give items to a client
==================
*/
void Cmd_Give_f (gentity_t *ent)
{
	char			*name;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	name = ConcatArgs( 1 );
	if ( !name[0] ) {
		return;
	}

	if ( Q_stricmp( name, "all" ) == 0 ) {
		G_GiveItemByName( ent, "health" );
		G_GiveItemByName( ent, "weapons" );
		G_GiveItemByName( ent, "ammo" );
		G_GiveItemByName( ent, "armor" );
		return;
	}

	G_GiveItemByName( ent, name );
}


/*
==================
Cmd_God_f

Sets client to godmode

argv(0) god
==================
*/
void Cmd_God_f (gentity_t *ent)
{
	char	*msg;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	ent->flags ^= FL_GODMODE;
	if (!(ent->flags & FL_GODMODE) )
		msg = "godmode OFF\n";
	else
		msg = "godmode ON\n";

	trap_SendServerCommand( ent-g_entities, va("print \"%s\"", msg));
}

/*
==================
Cmd_Notarget_f

Sets client to notarget

argv(0) notarget
==================
*/
void Cmd_Notarget_f( gentity_t *ent ) {
	char	*msg;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	ent->flags ^= FL_NOTARGET;
	if (!(ent->flags & FL_NOTARGET) )
		msg = "notarget OFF\n";
	else
		msg = "notarget ON\n";

	trap_SendServerCommand( ent-g_entities, va("print \"%s\"", msg));
}


/*
==================
Cmd_Noclip_f

argv(0) noclip
==================
*/
void Cmd_Noclip_f( gentity_t *ent ) {
	char	*msg;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	if ( ent->client->noclip ) {
		msg = "noclip OFF\n";
	} else {
		msg = "noclip ON\n";
	}
	ent->client->noclip = !ent->client->noclip;

	trap_SendServerCommand( ent-g_entities, va("print \"%s\"", msg));
}


/*
============
Cmd_ThawTarget_f

Cheat helper that lets developers thaw a frozen teammate directly by slot.
============
*/
static void Cmd_ThawTarget_f( gentity_t *ent ) {
	char	arg[MAX_TOKEN_CHARS];
	int		targetNum;
	gentity_t	*target;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( !G_FreezeGametypeEnabled() ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_FREEZE_ONLY "\"" );
		G_LogPrintf( "cmd: thawtarget denied outside Freeze for client %i\n", ent->client->ps.clientNum );
		return;
	}

	if ( !CheatsOk( ent ) ) {
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget missing argument from client %i\n", ent->client->ps.clientNum );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	targetNum = atoi( arg );
	if ( targetNum < 0 || targetNum >= level.maxclients ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget invalid slot %s from client %i\n", arg, ent->client->ps.clientNum );
		return;
	}

	target = &g_entities[targetNum];
	if ( !target->inuse || !target->client || target->client->pers.connected != CON_CONNECTED ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget unavailable client %i requested by %i\n", targetNum, ent->client->ps.clientNum );
		return;
	}

	if ( target->client->sess.sessionTeam != TEAM_RED && target->client->sess.sessionTeam != TEAM_BLUE ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget non-team target %i requested by %i\n", targetNum, ent->client->ps.clientNum );
		return;
	}

	if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR && ent->client->sess.sessionTeam != target->client->sess.sessionTeam ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget team mismatch client %i target %i\n", ent->client->ps.clientNum, targetNum );
		return;
	}

	if ( !target->client->freezeFrozen ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget requested for non-frozen client %i by %i\n", targetNum, ent->client->ps.clientNum );
		return;
	}

	G_FreezeThawClient( target, qfalse, ent - g_entities );
	G_LogPrintf( "cmd: thawtarget thawed client %i via client %i\n", targetNum, ent->client->ps.clientNum );
}

/*
==================
Cmd_LevelShot_f

This is just to help generate the level pictures
for the menus.  It goes to the intermission immediately
and sends over a command to the client to resize the view,
hide the scoreboard, and take a special screenshot
==================
*/
void Cmd_LevelShot_f( gentity_t *ent ) {
	if ( !CheatsOk( ent ) ) {
		return;
	}

	// doesn't work in single player
	if ( g_gametype.integer != 0 ) {
		trap_SendServerCommand( ent-g_entities, 
			"print \"Must be in g_gametype 0 for levelshot\n\"" );
		return;
	}

	BeginIntermission();
	trap_SendServerCommand( ent-g_entities, "clientLevelShot" );
}


void Cmd_TeamTask_f( gentity_t *ent ) {
	char userinfo[MAX_INFO_STRING];
	char		arg[MAX_TOKEN_CHARS];
	int task;
	int client = ent->client - level.clients;

	if ( trap_Argc() != 2 ) {
		return;
	}
	trap_Argv( 1, arg, sizeof( arg ) );
	task = atoi( arg );

	trap_GetUserinfo(client, userinfo, sizeof(userinfo));
	Info_SetValueForKey(userinfo, "teamtask", va("%d", task));
	trap_SetUserinfo(client, userinfo);
	ClientUserinfoChanged(client);
}



/*
=============
G_IsRoundCountdownActive
=============
*/
static qboolean G_IsRoundCountdownActive( void ) {
	if ( level.roundTransitionTime != ROUND_TRANSITION_NONE
		&& level.roundTransitionTime > level.time ) {
		return qtrue;
	}

	return qfalse;
}


/*
=============
G_ForfeitGametypeName
=============
*/
static const char *G_ForfeitGametypeName( int gametype ) {
	static const char *const s_forfeitGametypeNames[] = {
		"Free For All",
		"Duel",
		"Race",
		"Team Deathmatch",
		"Clan Arena",
		"Capture the Flag",
		"One Flag CTF",
		"Overload",
		"Harvester",
		"Freeze Tag",
		"Domination",
		"Attack and Defend",
		"Red Rover"
	};

	if ( gametype >= 0 && gametype < (int)( sizeof( s_forfeitGametypeNames ) / sizeof( s_forfeitGametypeNames[0] ) ) ) {
		return s_forfeitGametypeNames[gametype];
	}

	return "Unknown Gametype";
}


/*
=============
Cmd_Kill_f

Executes the self-kill command while honouring the g_allowKill cooldown.
=============
*/
void Cmd_Kill_f( gentity_t *ent ) {
	int	cooldown;

	if ( !ent || !ent->client ) {
		return;
	}
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}
	if ( ent->health <= 0 ) {
		return;
	}

	cooldown = g_allowKill.integer;
	if ( cooldown < 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Kill is not enabled on this server.\n\"" );
		return;
	}

	if ( cooldown > 0 ) {
		int	spawnElapsed;
		int	killElapsed;

		spawnElapsed = level.time - ent->client->respawnTime;
		if ( spawnElapsed < cooldown ) {
			return;
		}

		if ( ent->client->pers.killCommandTime >= 0 ) {
			killElapsed = level.time - ent->client->pers.killCommandTime;
			if ( killElapsed < cooldown ) {
				return;
			}
		}
	}

	ent->flags &= ~FL_GODMODE;
	ent->client->ps.stats[STAT_HEALTH] = ent->health = -999;
	ent->client->pers.killCommandTime = level.time;
	player_die( ent, ent, ent, 100000, MOD_SUICIDE );
}

/*
=============
Cmd_Forfeit_f

Processes the player forfeit command.
=============
*/
void Cmd_Forfeit_f( gentity_t *ent ) {
	int		gametype;
	const char	*gametypeName;
	team_t	team;
	team_t	losingTeam;
	int		redScore;
	int		blueScore;
	int		teammateCount;
	gclient_t	*opponent;
	int		opponentScore;
	int		i;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	if ( ent->health <= 0 ) {
		return;
	}

	if ( g_allowForfeit.integer <= 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeits are not enabled on this server.\\n\"" );
		return;
	}

	if ( level.warmupTime != 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is not available in warmup.\\n\"" );
		return;
	}

	if ( level.timeoutActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is not available during a pause or timeout.\\n\"" );
		return;
	}

	if ( G_IsRoundCountdownActive() ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is not available during a round countdown.\\n\"" );
		return;
	}

	gametype = g_gametype.integer;
	gametypeName = G_ForfeitGametypeName( gametype );

	if ( gametype == GT_FFA || gametype == GT_RACE || gametype == GT_RED_ROVER ) {
		trap_SendServerCommand( ent-g_entities, va( "print \"Forfeit is not available in %s.\\n\"", gametypeName ) );
		return;
	}

	if ( gametype >= GT_TEAM ) {
		team = ent->client->sess.sessionTeam;
		if ( team != TEAM_RED && team != TEAM_BLUE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to members of the losing team.\\n\"" );
			return;
		}

		redScore = level.teamScores[TEAM_RED];
		blueScore = level.teamScores[TEAM_BLUE];
		if ( redScore == blueScore ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to the losing player.\\n\"" );
			return;
		}

		losingTeam = ( redScore < blueScore ) ? TEAM_RED : TEAM_BLUE;
		if ( team != losingTeam ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to members of the losing team.\\n\"" );
			return;
		}

		teammateCount = TeamCount( ent->client->ps.clientNum, team );
		if ( teammateCount > 0 ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to the last remaining player on the losing team.\\n\"" );
			return;
		}

		G_ApplyForfeit( ent );
		return;
	}

	if ( gametype == GT_TOURNAMENT ) {
		opponent = NULL;
		opponentScore = 0;

		for ( i = 0; i < level.maxclients; i++ ) {
			gclient_t *client;

			if ( i == ent->client->ps.clientNum ) {
				continue;
			}

			client = &level.clients[i];
			if ( client->pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {
				continue;
			}

			opponent = client;
			opponentScore = client->ps.persistant[PERS_SCORE];
			break;
		}

		if ( !opponent ) {
			return;
		}

		if ( ent->client->ps.persistant[PERS_SCORE] >= opponentScore ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to the losing player.\\n\"" );
			return;
		}

		if ( ent->client->ps.pm_type != PM_NORMAL || ent->health <= 0 ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to the losing player.\\n\"" );
			return;
		}

		G_ApplyForfeit( ent );
		return;
	}

	trap_SendServerCommand( ent-g_entities, va( "print \"Forfeit is not available in %s.\\n\"", gametypeName ) );
}

/*
=================
BroadCastTeamChange

Let everyone know about a team change
=================
*/
void BroadcastTeamChange( gclient_t *client, int oldTeam )
{
	if ( client->sess.sessionTeam == TEAM_RED ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the red team.\n\"",
			client->pers.netname) );
	} else if ( client->sess.sessionTeam == TEAM_BLUE ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the blue team.\n\"",
		client->pers.netname));
	} else if ( client->sess.sessionTeam == TEAM_SPECTATOR && oldTeam != TEAM_SPECTATOR ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the spectators.\n\"",
		client->pers.netname));
	} else if ( client->sess.sessionTeam == TEAM_FREE ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the battle.\n\"",
		client->pers.netname));
	}
}

/*
=================
SetTeam
=================
*/
void SetTeam( gentity_t *ent, char *s ) {
	int					team, oldTeam;
	gclient_t			*client;
	int					clientNum;
	spectatorState_t	specState;
	int					specClient;
	int					teamLeader;

	//
	// see what change is requested
	//
	client = ent->client;

	clientNum = client - level.clients;
	specClient = 0;
	specState = SPECTATOR_NOT;
	if ( !Q_stricmp( s, "scoreboard" ) || !Q_stricmp( s, "score" )  ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_SCOREBOARD;
	} else if ( !Q_stricmp( s, "follow1" ) ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_FOLLOW;
		specClient = -1;
	} else if ( !Q_stricmp( s, "follow2" ) ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_FOLLOW;
		specClient = -2;
	} else if ( !Q_stricmp( s, "spectator" ) || !Q_stricmp( s, "s" ) ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_FREE;
	} else if ( g_gametype.integer >= GT_TEAM ) {
		// if running a team game, assign player to one of the teams
		specState = SPECTATOR_NOT;
		if ( !Q_stricmp( s, "red" ) || !Q_stricmp( s, "r" ) ) {
			team = TEAM_RED;
		} else if ( !Q_stricmp( s, "blue" ) || !Q_stricmp( s, "b" ) ) {
			team = TEAM_BLUE;
		} else if ( !Q_stricmp( s, "auto" ) ) {
			// pick the team with the least number of players
			team = PickTeam( clientNum );
		} else {
			// pick the team with the least number of players
			team = PickTeam( clientNum );
		}

		if ( g_teamForceBalance.integer  ) {
			int		counts[TEAM_NUM_TEAMS];

			counts[TEAM_BLUE] = TeamCount( ent->client->ps.clientNum, TEAM_BLUE );
			counts[TEAM_RED] = TeamCount( ent->client->ps.clientNum, TEAM_RED );

			// We allow a spread of two
			if ( team == TEAM_RED && counts[TEAM_RED] - counts[TEAM_BLUE] > 1 ) {
				trap_SendServerCommand( ent->client->ps.clientNum, 
					"cp \"Red team has too many players.\n\"" );
				return; // ignore the request
			}
			if ( team == TEAM_BLUE && counts[TEAM_BLUE] - counts[TEAM_RED] > 1 ) {
				trap_SendServerCommand( ent->client->ps.clientNum, 
					"cp \"Blue team has too many players.\n\"" );
				return; // ignore the request
			}

			// It's ok, the team we are switching to has less or same number of players
		}

	} else {
		// force them to spectators if there aren't any spots free
		team = TEAM_FREE;
	}

	if ( g_teamSpawnAsSpec.integer && g_gametype.integer >= GT_TEAM && team != TEAM_SPECTATOR ) {
		team = TEAM_SPECTATOR;
		specState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;
	}

	if ( team == TEAM_SPECTATOR && specState == SPECTATOR_FREE && !g_teamSpecFreeCam.integer ) {
		specState = SPECTATOR_SCOREBOARD;
	}

	// override decision if limiting the players
	if ( (g_gametype.integer == GT_TOURNAMENT)
		&& level.numNonSpectatorClients >= 2 ) {
		team = TEAM_SPECTATOR;
	} else if ( g_maxGameClients.integer > 0 && 
		level.numNonSpectatorClients >= g_maxGameClients.integer ) {
		team = TEAM_SPECTATOR;
	}

	//
	// decide if we will allow the change
	//
	oldTeam = client->sess.sessionTeam;
	if ( team == oldTeam && team != TEAM_SPECTATOR ) {
		return;
	}

	//
	// execute the team change
	//

	// if the player was dead leave the body
	if ( client->ps.stats[STAT_HEALTH] <= 0 ) {
		CopyToBodyQue(ent);
	}

	// he starts at 'base'
	client->pers.teamState.state = TEAM_BEGIN;
	if ( oldTeam != TEAM_SPECTATOR ) {
		// Kill him (makes sure he loses flags, etc)
		ent->flags &= ~FL_GODMODE;
		ent->client->ps.stats[STAT_HEALTH] = ent->health = 0;
		player_die (ent, ent, ent, 100000, MOD_SUICIDE);

	}
	// they go to the end of the line for tournements
	if ( team == TEAM_SPECTATOR ) {
		client->sess.spectatorTime = level.time;
	}

	client->sess.sessionTeam = team;
	client->sess.spectatorState = specState;
	client->sess.spectatorClient = specClient;

	client->lastKillCommandTime = 0;
	client->killCommandCooldownExpires = 0;
	client->friendlyFireComplaints = 0;
	client->friendlyFireComplaintEndTime = 0;
	client->teammateDamageGiven = 0;
	client->teammateDamageThisLife = 0;

	client->sess.teamLeader = qfalse;
	if ( team == TEAM_RED || team == TEAM_BLUE ) {
		teamLeader = TeamLeader( team );
		// if there is no team leader or the team leader is a bot and this client is not a bot
		if ( teamLeader == -1 || ( !(g_entities[clientNum].r.svFlags & SVF_BOT) && (g_entities[teamLeader].r.svFlags & SVF_BOT) ) ) {
			SetLeader( team, clientNum );
		}
	}
	// make sure there is a team leader on the team the player came from
	if ( oldTeam == TEAM_RED || oldTeam == TEAM_BLUE ) {
		CheckTeamLeader( oldTeam );
	}

	BroadcastTeamChange( client, oldTeam );

	// get and distribute relevent paramters
	ClientUserinfoChanged( clientNum );

	ClientBegin( clientNum );
}

/*
=================
StopFollowing

If the client being followed leaves the game, or you just want to drop
to free floating spectator mode
=================
*/
void StopFollowing( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	ent->client->ps.persistant[ PERS_TEAM ] = TEAM_SPECTATOR;
	ent->client->sess.sessionTeam = TEAM_SPECTATOR;
	ent->client->sess.spectatorState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;
	ent->client->sess.spectatorClient = -1;
	ent->client->lastKillCommandTime = 0;
	ent->client->killCommandCooldownExpires = 0;
	ent->client->friendlyFireComplaints = 0;
	ent->client->friendlyFireComplaintEndTime = 0;
	ent->client->teammateDamageGiven = 0;
	ent->client->teammateDamageThisLife = 0;
	ent->client->ps.pm_flags &= ~PMF_FOLLOW;
	ent->r.svFlags &= ~SVF_BOT;
	ent->client->ps.clientNum = ent - g_entities;
}

/*
=================
Cmd_Team_f
=================
*/
void Cmd_Team_f( gentity_t *ent ) {
	int			oldTeam;
	char		s[MAX_TOKEN_CHARS];

	if ( trap_Argc() != 2 ) {
		oldTeam = ent->client->sess.sessionTeam;
		switch ( oldTeam ) {
		case TEAM_BLUE:
			trap_SendServerCommand( ent-g_entities, "print \"Blue team\n\"" );
			break;
		case TEAM_RED:
			trap_SendServerCommand( ent-g_entities, "print \"Red team\n\"" );
			break;
		case TEAM_FREE:
			trap_SendServerCommand( ent-g_entities, "print \"Free team\n\"" );
			break;
		case TEAM_SPECTATOR:
			trap_SendServerCommand( ent-g_entities, "print \"Spectator team\n\"" );
			break;
		}
		return;
	}

	if ( ent->client->switchTeamTime > level.time ) {
		trap_SendServerCommand( ent-g_entities, "print \"May not switch teams more than once per 5 seconds.\n\"" );
		return;
	}

	// if they are playing a tournement game, count as a loss
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& ent->client->sess.sessionTeam == TEAM_FREE ) {
		ent->client->sess.losses++;
	}

	trap_Argv( 1, s, sizeof( s ) );

	SetTeam( ent, s );

	ent->client->switchTeamTime = level.time + 5000;
}


/*
=================
Cmd_Follow_f
=================
*/
void Cmd_Follow_f( gentity_t *ent ) {
	int			i;
	char	arg[MAX_TOKEN_CHARS];

	if ( !ent || !ent->client ) {
		return;
	}

	if ( level.trainingMapActive ) {
		if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
			StopFollowing( ent );
		}
		trap_SendServerCommand( ent-g_entities, "print \"Following is disabled in training.\n\"" );
		return;
	}

	if ( trap_Argc() != 2 ) {
		if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
			if ( g_teamSpecFreeCam.integer ) {
				StopFollowing( ent );
			} else {
				trap_SendServerCommand( ent-g_entities, "print \"Free-flying spectators are disabled while g_teamSpecFreeCam is 0.\n\"" );
			}
		}
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	i = ClientNumberFromString( ent, arg );
	if ( i == -1 ) {
		return;
	}

	// can't follow self
	if ( &level.clients[ i ] == ent->client ) {
		return;
	}

	// can't follow another spectator
	if ( level.clients[ i ].sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	// if they are playing a tournement game, count as a loss
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& ent->client->sess.sessionTeam == TEAM_FREE ) {
		ent->client->sess.losses++;
	}

	// first set them to spectator
	if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		SetTeam( ent, "spectator" );
	}

	ent->client->sess.spectatorState = SPECTATOR_FOLLOW;
	ent->client->sess.spectatorClient = i;

}

/*
=================
Cmd_FollowCycle_f
=================
*/
void Cmd_FollowCycle_f( gentity_t *ent, int dir ) {
	int		clientnum;
	int		original;

	if ( level.trainingMapActive ) {
		if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
			StopFollowing( ent );
		}
		trap_SendServerCommand( ent-g_entities, "print \"Following is disabled in training.\n\"" );
		return;
	}

	// if they are playing a tournement game, count as a loss
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& ent->client->sess.sessionTeam == TEAM_FREE ) {
		ent->client->sess.losses++;
	}
	// first set them to spectator
	if ( ent->client->sess.spectatorState == SPECTATOR_NOT ) {
		SetTeam( ent, "spectator" );
	}

	if ( dir != 1 && dir != -1 ) {
		G_Error( "Cmd_FollowCycle_f: bad dir %i", dir );
	}

	clientnum = ent->client->sess.spectatorClient;
	original = clientnum;
	do {
		clientnum += dir;
		if ( clientnum >= level.maxclients ) {
			clientnum = 0;
		}
		if ( clientnum < 0 ) {
			clientnum = level.maxclients - 1;
		}

		// can only follow connected clients
		if ( level.clients[ clientnum ].pers.connected != CON_CONNECTED ) {
			continue;
		}

		// can't follow another spectator
		if ( level.clients[ clientnum ].sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}

		// this is good, we can use it
		ent->client->sess.spectatorClient = clientnum;
		ent->client->sess.spectatorState = SPECTATOR_FOLLOW;
		return;
	} while ( clientnum != original );

	// leave it where it was
}


/*
=============
G_SayTo

Sends a chat message to a single recipient when chat permissions allow it.
=============
*/
static void G_SayTo( gentity_t *ent, gentity_t *other, int mode, int color, const char *name, const char *message ) {
	if ( !other ) {
		return;
	}
	if ( !other->inuse ) {
		return;
	}
	if ( !other->client ) {
		return;
	}
	if ( other->client->pers.connected != CON_CONNECTED ) {
		return;
	}
	if ( mode == SAY_TEAM && !OnSameTeam( ent, other ) ) {
		return;
	}

	if ( ent && ent->client && other->client ) {
		if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR && !g_teamSpecSayEnable.integer ) {
			if ( ent == other ) {
				trap_SendServerCommand( ent - g_entities, "print \"Spectator chat is disabled while g_teamSpecSayEnable is 0.\n\"" );
			}
			return;
		}

		const team_t		entTeam = ent->client->sess.sessionTeam;
		const team_t		otherTeam = other->client->sess.sessionTeam;
		const qboolean	isTeamGame = ( g_gametype.integer >= GT_TEAM );
		const qboolean	sameClient = ( ent == other );

		if ( entTeam == TEAM_SPECTATOR && otherTeam != TEAM_SPECTATOR && !sameClient && !g_allTalk.integer ) {
			if ( mode == SAY_TELL ) {
				trap_SendServerCommand( ent - g_entities, "print \"Spectators may only chat with other spectators unless g_allTalk is enabled.\n\"" );
			}
			return;
		}

		if ( isTeamGame && mode != SAY_TEAM && !g_allTalk.integer && entTeam != TEAM_SPECTATOR && otherTeam != TEAM_SPECTATOR && entTeam != otherTeam ) {
			if ( mode == SAY_TELL && !sameClient ) {
				trap_SendServerCommand( ent - g_entities, "print \"Cross-team tells are disabled while g_allTalk is 0.\n\"" );
			}
			return;
		}
	}

	// no chatting to players in tournements
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& other->client->sess.sessionTeam == TEAM_FREE
		&& ent->client->sess.sessionTeam != TEAM_FREE ) {
		return;
	}

	trap_SendServerCommand( other-g_entities, va( "%s \"%s%c%c%s\"",
		mode == SAY_TEAM ? "tchat" : "chat",
		name, Q_COLOR_ESCAPE, color, message));
}

#define EC		"\x19"

/*
=============
G_Say

Routes chat text according to chat mode and talk permissions.
=============
*/
void G_Say( gentity_t *ent, gentity_t *target, int mode, const char *chatText ) {
	int			j;
	gentity_t	*other;
	int			color;
	char		name[64];
	// don't let text be too long for malicious reasons
	char		text[MAX_SAY_TEXT];
	char		location[64];

	if ( g_gametype.integer < GT_TEAM && mode == SAY_TEAM ) {
		mode = SAY_ALL;
	}

	switch ( mode ) {
	default:
	case SAY_ALL:
		G_LogPrintf( "say: %s: %s\n", ent->client->pers.netname, chatText );
		Com_sprintf (name, sizeof(name), "%s%c%c"EC": ", ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE );
		color = COLOR_GREEN;
		break;
	case SAY_TEAM:
		G_LogPrintf( "sayteam: %s: %s\n", ent->client->pers.netname, chatText );
		if (Team_GetLocationMsg(ent, location, sizeof(location)))
			Com_sprintf (name, sizeof(name), EC"(%s%c%c"EC") (%s)"EC": ", 
				ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE, location);
		else
			Com_sprintf (name, sizeof(name), EC"(%s%c%c"EC")"EC": ", 
				ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE );
		color = COLOR_CYAN;
		break;
	case SAY_TELL:
		if (target && g_gametype.integer >= GT_TEAM &&
			target->client->sess.sessionTeam == ent->client->sess.sessionTeam &&
			Team_GetLocationMsg(ent, location, sizeof(location)))
			Com_sprintf (name, sizeof(name), EC"[%s%c%c"EC"] (%s)"EC": ", ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE, location );
		else
			Com_sprintf (name, sizeof(name), EC"[%s%c%c"EC"]"EC": ", ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE );
		color = COLOR_MAGENTA;
		break;
	}

	Q_strncpyz( text, chatText, sizeof(text) );

	if ( target ) {
		G_SayTo( ent, target, mode, color, name, text );
		return;
	}

	// echo the text to the console
	if ( g_dedicated.integer ) {
		G_Printf( "%s%s\n", name, text);
	}

	// send it to all the apropriate clients
	for (j = 0; j < level.maxclients; j++) {
		other = &g_entities[j];
		G_SayTo( ent, other, mode, color, name, text );
	}
}


/*
==================
Cmd_Say_f
==================
*/
static void Cmd_Say_f( gentity_t *ent, int mode, qboolean arg0 ) {
	char		*p;

	if ( trap_Argc () < 2 && !arg0 ) {
		return;
	}

	if (arg0)
	{
		p = ConcatArgs( 0 );
	}
	else
	{
		p = ConcatArgs( 1 );
	}

	if ( G_FloodLimited( ent, ( mode == SAY_TEAM ) ? "using team chat" : "chatting", qtrue ) ) {
		return;
	}

	G_Say( ent, NULL, mode, p );
}

/*
==================
Cmd_Tell_f
==================
*/
static void Cmd_Tell_f( gentity_t *ent ) {
	int			targetNum;
	gentity_t	*target;
	char		*p;
	char		arg[MAX_TOKEN_CHARS];

	if ( trap_Argc () < 2 ) {
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	targetNum = atoi( arg );
	if ( targetNum < 0 || targetNum >= level.maxclients ) {
		return;
	}

	target = &g_entities[targetNum];
	if ( !target || !target->inuse || !target->client ) {
		return;
	}

	p = ConcatArgs( 2 );

	if ( G_FloodLimited( ent, "sending tells", qtrue ) ) {
		return;
	}

	G_LogPrintf( "tell: %s to %s: %s\n", ent->client->pers.netname, target->client->pers.netname, p );
	G_Say( ent, target, SAY_TELL, p );
	// don't tell to the player self if it was already directed to this player
	// also don't send the chat back to a bot
	if ( ent != target && !(ent->r.svFlags & SVF_BOT)) {
		G_Say( ent, ent, SAY_TELL, p );
	}
}


static void G_VoiceTo( gentity_t *ent, gentity_t *other, int mode, const char *id, qboolean voiceonly ) {
	int color;
	char *cmd;

	if (!other) {
		return;
	}
	if (!other->inuse) {
		return;
	}
	if (!other->client) {
		return;
	}
	if ( mode == SAY_TEAM && !OnSameTeam(ent, other) ) {
		return;
	}
	// no chatting to players in tournements
	if ( (g_gametype.integer == GT_TOURNAMENT )) {
		return;
	}

	if (mode == SAY_TEAM) {
		color = COLOR_CYAN;
		cmd = "vtchat";
	}
	else if (mode == SAY_TELL) {
		color = COLOR_MAGENTA;
		cmd = "vtell";
	}
	else {
		color = COLOR_GREEN;
		cmd = "vchat";
	}

	trap_SendServerCommand( other-g_entities, va("%s %d %d %d %s", cmd, voiceonly, ent->s.number, color, id));
}

void G_Voice( gentity_t *ent, gentity_t *target, int mode, const char *id, qboolean voiceonly ) {
	int			j;
	gentity_t	*other;

	if ( g_gametype.integer < GT_TEAM && mode == SAY_TEAM ) {
		mode = SAY_ALL;
	}

	if ( target ) {
		G_VoiceTo( ent, target, mode, id, voiceonly );
		return;
	}

	// echo the text to the console
	if ( g_dedicated.integer ) {
		G_Printf( "voice: %s %s\n", ent->client->pers.netname, id);
	}

	// send it to all the apropriate clients
	for (j = 0; j < level.maxclients; j++) {
		other = &g_entities[j];
		G_VoiceTo( ent, other, mode, id, voiceonly );
	}
}

/*
==================
Cmd_Voice_f
==================
*/
static void Cmd_Voice_f( gentity_t *ent, int mode, qboolean arg0, qboolean voiceonly ) {
	char		*p;
	const char		*action;

	if ( trap_Argc () < 2 && !arg0 ) {
		return;
	}

	if (arg0)
	{
		p = ConcatArgs( 0 );
	}
	else
	{
		p = ConcatArgs( 1 );
	}

	if ( mode == SAY_TEAM ) {
		action = voiceonly ? "using team voice commands" : "using team voice chat";
	} else {
		action = voiceonly ? "using voice commands" : "using voice chat";
	}

	if ( G_FloodLimited( ent, action, qtrue ) ) {
		return;
	}

	G_Voice( ent, NULL, mode, p, voiceonly );
}

/*
==================
Cmd_VoiceTell_f
==================
*/
static void Cmd_VoiceTell_f( gentity_t *ent, qboolean voiceonly ) {
	int			targetNum;
	gentity_t	*target;
	char		*id;
	char		arg[MAX_TOKEN_CHARS];

	if ( trap_Argc () < 2 ) {
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	targetNum = atoi( arg );
	if ( targetNum < 0 || targetNum >= level.maxclients ) {
		return;
	}

	target = &g_entities[targetNum];
	if ( !target || !target->inuse || !target->client ) {
		return;
	}

	id = ConcatArgs( 2 );

	if ( G_FloodLimited( ent, voiceonly ? "sending private voice commands" : "sending private voice chats", qtrue ) ) {
		return;
	}

	G_LogPrintf( "vtell: %s to %s: %s\n", ent->client->pers.netname, target->client->pers.netname, id );
	G_Voice( ent, target, SAY_TELL, id, voiceonly );
	// don't tell to the player self if it was already directed to this player
	// also don't send the chat back to a bot
	if ( ent != target && !(ent->r.svFlags & SVF_BOT)) {
		G_Voice( ent, ent, SAY_TELL, id, voiceonly );
	}
}


/*
==================
Cmd_VoiceTaunt_f
==================
*/
static void Cmd_VoiceTaunt_f( gentity_t *ent ) {
	gentity_t *who;
	int i;

	if (!ent->client) {
		return;
	}

	if ( G_FloodLimited( ent, "sending voice taunts", qtrue ) ) {
		return;
	}

	// insult someone who just killed you
	if (ent->enemy && ent->enemy->client && ent->enemy->client->lastkilled_client == ent->s.number) {
		// i am a dead corpse
		if (!(ent->enemy->r.svFlags & SVF_BOT)) {
			G_Voice( ent, ent->enemy, SAY_TELL, VOICECHAT_DEATHINSULT, qfalse );
		}
		if (!(ent->r.svFlags & SVF_BOT)) {
			G_Voice( ent, ent,        SAY_TELL, VOICECHAT_DEATHINSULT, qfalse );
		}
		ent->enemy = NULL;
		return;
	}
	// insult someone you just killed
	if (ent->client->lastkilled_client >= 0 && ent->client->lastkilled_client != ent->s.number) {
		who = g_entities + ent->client->lastkilled_client;
		if (who->client) {
			// who is the person I just killed
			if (who->client->lasthurt_mod == MOD_GAUNTLET) {
				if (!(who->r.svFlags & SVF_BOT)) {
					G_Voice( ent, who, SAY_TELL, VOICECHAT_KILLGAUNTLET, qfalse );	// and I killed them with a gauntlet
				}
				if (!(ent->r.svFlags & SVF_BOT)) {
					G_Voice( ent, ent, SAY_TELL, VOICECHAT_KILLGAUNTLET, qfalse );
				}
			} else {
				if (!(who->r.svFlags & SVF_BOT)) {
					G_Voice( ent, who, SAY_TELL, VOICECHAT_KILLINSULT, qfalse );	// and I killed them with something else
				}
				if (!(ent->r.svFlags & SVF_BOT)) {
					G_Voice( ent, ent, SAY_TELL, VOICECHAT_KILLINSULT, qfalse );
				}
			}
			ent->client->lastkilled_client = -1;
			return;
		}
	}

	if (g_gametype.integer >= GT_TEAM) {
		// praise a team mate who just got a reward
		for(i = 0; i < MAX_CLIENTS; i++) {
			who = g_entities + i;
			if (who->client && who != ent && who->client->sess.sessionTeam == ent->client->sess.sessionTeam) {
				if (who->client->rewardTime > level.time) {
					if (!(who->r.svFlags & SVF_BOT)) {
						G_Voice( ent, who, SAY_TELL, VOICECHAT_PRAISE, qfalse );
					}
					if (!(ent->r.svFlags & SVF_BOT)) {
						G_Voice( ent, ent, SAY_TELL, VOICECHAT_PRAISE, qfalse );
					}
					return;
				}
			}
		}
	}

	// just say something
	G_Voice( ent, NULL, SAY_ALL, VOICECHAT_TAUNT, qfalse );
}



static char	*gc_orders[] = {
	"hold your position",
	"hold this position",
	"come here",
	"cover me",
	"guard location",
	"search and destroy",
	"report"
};

void Cmd_GameCommand_f( gentity_t *ent ) {
	int		player;
	int		order;
	char	str[MAX_TOKEN_CHARS];

	trap_Argv( 1, str, sizeof( str ) );
	player = atoi( str );
	trap_Argv( 2, str, sizeof( str ) );
	order = atoi( str );

	if ( player < 0 || player >= MAX_CLIENTS ) {
		return;
	}
	if ( order < 0 || order > sizeof(gc_orders)/sizeof(char *) ) {
		return;
	}
	if ( G_FloodLimited( ent, "issuing team commands", qtrue ) ) {
		return;
	}
	G_Say( ent, &g_entities[player], SAY_TELL, gc_orders[order] );
	G_Say( ent, ent, SAY_TELL, gc_orders[order] );
}

/*
==================
Cmd_Where_f
==================
*/
void Cmd_Where_f( gentity_t *ent ) {
	trap_SendServerCommand( ent-g_entities, va("print \"%s\n\"", vtos( ent->s.origin ) ) );
}

#define VF_NO_MAP				0x0001
#define VF_NO_MAP_RESTART		0x0002
#define VF_NO_NEXTMAP			0x0004
#define VF_NO_GAMETYPE			0x0008
#define VF_NO_KICK			0x0010
#define VF_NO_TIME_LIMIT		0x0040
#define VF_NO_FRAG_LIMIT		0x0080

static const char *gameNames[] = {
"Free For All",
"Duel",
"Race",
"Team Deathmatch",
"Clan Arena",
"Capture the Flag",
"One Flag CTF",
"Overload",
"Harvester",
"Freeze Tag",
"Domination",
"Attack and Defend",
"Red Rover"
};

/*
=============
G_VoteSelectionKey

Generate a stable hash so repeated vote attempts can be detected.
=============
*/
static int G_VoteSelectionKey( const char *command, const char *option ) {
	int		hash;
	const char	*scan;

	if ( !command || !*command ) {
		return -1;
	}

	hash = 5381;
	for ( scan = command ; *scan ; scan++ ) {
		hash = ( ( hash << 5 ) + hash ) ^ tolower( *scan );
	}

	if ( option && *option ) {
		for ( scan = option ; *scan ; scan++ ) {
			hash = ( ( hash << 5 ) + hash ) ^ tolower( *scan );
		}
	}

	return hash;
}

/*
==================
Cmd_CallVote_f
==================
*/
void Cmd_CallVote_f( gentity_t *ent ) {
	gclient_t       *client;
	char            arg1[MAX_STRING_TOKENS];
	char            arg2[MAX_STRING_TOKENS];
	char            arg3[MAX_STRING_TOKENS];
	char            buffer[MAX_STRING_CHARS];
	int             voteSelection;
	int             delayMsec;
	int             remaining;
	qboolean        isSpectator;
	qboolean        midGame;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;

	trap_Argv( 1, arg1, sizeof( arg1 ) );
	trap_Argv( 2, arg2, sizeof( arg2 ) );
	trap_Argv( 3, arg3, sizeof( arg3 ) );

	if ( strchr( arg1, ';' ) || strchr( arg2, ';' ) || strchr( arg3, ';' ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid vote string.\\n\"" );
		return;
	}

	delayMsec = g_voteDelay.integer > 0 ? g_voteDelay.integer * 1000 : 0;
	isSpectator = ( client->sess.sessionTeam == TEAM_SPECTATOR );
	midGame = ( level.warmupTime <= 0 && level.intermissiontime == 0 );

	if ( delayMsec > 0 ) {
		int             startWindow;

		startWindow = level.startTime + delayMsec;
		if ( level.time < startWindow ) {
			remaining = startWindow - level.time;
			trap_SendServerCommand( ent-g_entities,
				va( "print \"Voting will be allowed in %.1f seconds.\\n\"", remaining / 1000.0f ) );
			return;
		}

		if ( level.voteEligibleTime > level.time ) {
			remaining = level.voteEligibleTime - level.time;
			trap_SendServerCommand( ent-g_entities,
				va( "print \"Voting will be allowed in %.1f seconds.\\n\"", remaining / 1000.0f ) );
			return;
		}
	}

	if ( !g_allowVote.integer ) {
		trap_SendServerCommand( ent-g_entities, "print \"Public voting is not allowed here.\\n\"" );
		return;
	}

	if ( g_voteLimit.integer > 0 && client->pers.voteCount >= g_voteLimit.integer ) {
		trap_SendServerCommand( ent-g_entities, "print \"You have called the maximum number of votes.\\n\"" );
		return;
	}

	if ( isSpectator && !g_allowSpecVote.integer ) {
		trap_SendServerCommand( ent-g_entities, "print \"Not allowed to call a vote as spectator.\\n\"" );
		return;
	}

	if ( !g_allowVoteMidGame.integer && midGame ) {
		trap_SendServerCommand( ent-g_entities, "print \"Voting is only allowed during warmup.\\n\"" );
		return;
	}

	if ( level.voteTime ) {
		trap_SendServerCommand( ent-g_entities, "print \"A vote is already in progress.\\n\"" );
		return;
	}

	if ( level.voteExecuteTime && level.voteExecuteTime > level.time ) {
		trap_SendServerCommand( ent-g_entities, "print \"A vote is being executed.\\n\"" );
		return;
	}

	voteSelection = -1;

	if ( !Q_stricmp( arg1, "map_restart" ) ) {
		if ( g_voteFlags.integer & VF_NO_MAP_RESTART ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting on a map restart is disabled on this server.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "map_restart" );
		Q_strncpyz( level.voteDisplayString, level.voteString, sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, NULL );
	} else if ( !Q_stricmp( arg1, "nextmap" ) ) {
		if ( g_voteFlags.integer & VF_NO_NEXTMAP ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to move to the next map is disabled on this server.\\n\"" );
			return;
		}
		trap_Cvar_VariableStringBuffer( "nextmap", buffer, sizeof( buffer ) );
		if ( !buffer[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"nextmap not set.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "vstr nextmap" );
		Q_strncpyz( level.voteDisplayString, "nextmap", sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, buffer );
	} else if ( !Q_stricmp( arg1, "map" ) ) {
		int			len;
		fileHandle_t	f;
		const factoryDefinition_t *factoryOverride;
		char		voteOptionBuffer[MAX_STRING_TOKENS];
		const char	*voteOption;

		if ( g_voteFlags.integer & VF_NO_MAP ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the map being played is disabled on this server.\\n\"" );
			return;
		}
		if ( !arg2[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"Missing map name.\\n\"" );
			return;
		}
		Com_sprintf( buffer, sizeof( buffer ), "maps/%s.bsp", arg2 );
		len = trap_FS_FOpenFile( buffer, &f, FS_READ );
		if ( len <= 0 ) {
			trap_SendServerCommand( ent-g_entities, "print \"Map does not exist.\\n\"" );
			return;
		}
		trap_FS_FCloseFile( f );

		factoryOverride = NULL;
		voteOption = arg2;
		if ( arg3[0] ) {
			factoryOverride = Factory_FindById( arg3 );
			if ( !factoryOverride ) {
				trap_SendServerCommand( ent-g_entities, "print \"Invalid factory specified.\\n\"" );
				return;
			}
			if ( !G_MapSupportsGametype( arg2, factoryOverride->baseGametype ) ) {
				trap_SendServerCommand( ent-g_entities, "print \"Map not supported for this gametype.\\n\"" );
				return;
			}
			Com_sprintf( voteOptionBuffer, sizeof( voteOptionBuffer ), "%s %s", arg2, arg3 );
			voteOption = voteOptionBuffer;
		}

		trap_Cvar_VariableStringBuffer( "nextmap", buffer, sizeof( buffer ) );
		if ( buffer[0] ) {
			if ( factoryOverride ) {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s %s; set nextmap \"%s\"", arg2, arg3, buffer );
			} else {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s; set nextmap \"%s\"", arg2, buffer );
			}
		} else {
			if ( factoryOverride ) {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s %s", arg2, arg3 );
			} else {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s", arg2 );
			}
		}
		if ( factoryOverride ) {
			Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "map %s %s", arg2, arg3 );
		} else {
			Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "map %s", arg2 );
		}
		voteSelection = G_VoteSelectionKey( arg1, voteOption );
	} else if ( !Q_stricmp( arg1, "g_gametype" ) ) {
		int             gametype;

		if ( g_voteFlags.integer & VF_NO_GAMETYPE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the gametype being played is disabled on this server.\\n\"" );
			return;
		}

		gametype = atoi( arg2 );
		if ( gametype == GT_SINGLE_PLAYER || gametype < GT_FFA || gametype >= GT_MAX_GAME_TYPE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid gametype.\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_gametype %d", gametype );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_gametype %s", gameNames[gametype] );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "shuffle" ) ) {
		if ( g_gametype.integer < GT_TEAM ) {
			trap_SendServerCommand( ent-g_entities, "print \"Shuffle is only available in team games.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "shuffle_teams" );
		Q_strncpyz( level.voteDisplayString, "Shuffle Teams", sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, NULL );
	} else if ( !Q_stricmp( arg1, "teamsize" ) ) {
		if ( g_gametype.integer < GT_TEAM ) {
			trap_SendServerCommand( ent-g_entities, "print \"Teamsize is only available in team games.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "teamsize %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "teamsize %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "kick" ) ) {
		int             clientNum;

		if ( g_voteFlags.integer & VF_NO_KICK ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to kick a player is disabled on this server.\\n\"" );
			return;
		}

		if ( !arg2[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"Missing player name.\\n\"" );
			return;
		}

		if ( !Q_stricmp( arg2, "all" ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to kick all players is not allowed.\\n\"" );
			return;
		}

		clientNum = ClientNumberFromString( ent, arg2 );
		if ( clientNum == -1 ) {
			return;
		}

		if ( level.clients[clientNum].pers.localClient ) {
			trap_SendServerCommand( ent-g_entities, "print \"Cannot call a vote on the server host.\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "clientkick %d", clientNum );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "kick %s", level.clients[clientNum].pers.netname );
		voteSelection = G_VoteSelectionKey( arg1, level.clients[clientNum].pers.netname );
	} else if ( !Q_stricmp( arg1, "clientkick" ) ) {
		int             clientNum;

		if ( g_voteFlags.integer & VF_NO_KICK ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to kick a player is disabled on this server.\\n\"" );
			return;
		}

		clientNum = atoi( arg2 );
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid client slot.\n\"" );
			return;
		}

		if ( !g_entities[clientNum].inuse ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid player id.\n\"" );
			return;
		}

		if ( level.clients[clientNum].pers.localClient ) {
			trap_SendServerCommand( ent-g_entities, "print \"Cannot call a vote on the server host.\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "clientkick %d", clientNum );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "clientkick %d", clientNum );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "timelimit" ) ) {
		if ( g_voteFlags.integer & VF_NO_TIME_LIMIT ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the games time limit is disabled on this server.\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "timelimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "timelimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "fraglimit" ) ) {
		if ( g_voteFlags.integer & VF_NO_FRAG_LIMIT ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the games frag limit is disabled on this server.\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "fraglimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "fraglimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "scorelimit" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "scorelimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "scorelimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "roundlimit" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "roundlimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "roundlimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "cointoss" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "cointoss" );
		Q_strncpyz( level.voteDisplayString, "Coin Toss", sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, NULL );
	} else if ( !Q_stricmp( arg1, "randommap" ) ) {
		if ( g_voteFlags.integer & VF_NO_MAP ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the map being played is disabled on this server.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "randommap" );
		Q_strncpyz( level.voteDisplayString, "Random Map", sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, NULL );
	} else if ( !Q_stricmp( arg1, "ruleset" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "ruleset %s", arg2 );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "ruleset %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "mercylimit" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "mercylimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "mercylimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "floodprot" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_floodprot_maxcount %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "floodprot %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_friendlyFire" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_friendlyFire %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_friendlyFire %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_gravity" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_gravity %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_gravity %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_speed" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_speed %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_speed %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_doWarmup" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_doWarmup %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_doWarmup %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid vote string.\\n\"" );
		trap_SendServerCommand( ent-g_entities, "print \"Vote commands are: map_restart, nextmap, map <mapname>, g_gametype <n>, kick <player>, clientkick <clientnum>, g_doWarmup, timelimit <time>, fraglimit <frags>.\\n\"" );
		return;
	}

	if ( voteSelection != -1 && client->pers.voteDelayTime > 0
			&& client->pers.voteLastSelection == voteSelection
			&& level.time - client->pers.voteDelayTime < VOTE_THROTTLE_MSEC ) {
		trap_SendServerCommand( ent-g_entities, "print \"You already voted for this option.\\n\"" );
		return;
	}

	client->pers.voteCount++;
	G_RegisterVoteCall( client, ent-g_entities, voteSelection );
	trap_SendServerCommand( -1, va( "print \"%s called a vote.\\n\"", client->pers.netname ) );

	level.voteTime = level.time;
	level.voteYes = 1;
	level.voteNo = 0;

	if ( delayMsec > 0 ) {
		level.voteEligibleTime = level.time + delayMsec;
	}

	for ( voteSelection = 0 ; voteSelection < level.maxclients ; voteSelection++ ) {
		level.clients[voteSelection].ps.eFlags &= ~EF_VOTED;
	}
	client->ps.eFlags |= EF_VOTED;

	trap_SetConfigstring( CS_VOTE_TIME, va( "%i", level.voteTime ) );
	trap_SetConfigstring( CS_VOTE_STRING, level.voteDisplayString );
	trap_SetConfigstring( CS_VOTE_YES, va( "%i", level.voteYes ) );
	trap_SetConfigstring( CS_VOTE_NO, va( "%i", level.voteNo ) );
}


/*
=============
Cmd_Vote_f

Process a client's ballot during an active vote, applying spectator and throttle rules.
=============
*/
void Cmd_Vote_f( gentity_t *ent ) {
	char		msg[64];
	int		voteSelection;
	gclient_t	*client;

	if ( !level.voteTime ) {
		trap_SendServerCommand( ent-g_entities, "print \"No vote in progress.\n\"" );
		return;
	}

	client = ent->client;
	if ( !client ) {
		return;
	}

	trap_Argv( 1, msg, sizeof( msg ) );
	voteSelection = atoi( msg );
	if ( voteSelection <= 0 ) {
		if ( msg[0] == 'y' || msg[0] == 'Y' ) {
			voteSelection = 1;
		} else if ( msg[0] == 'n' || msg[0] == 'N' ) {
			voteSelection = 2;
		}
	}

	if ( client->sess.sessionTeam == TEAM_SPECTATOR && !g_allowSpecVote.integer ) {
		trap_SendServerCommand( ent-g_entities, "print \"You may not participate in this vote.\n\"" );
		return;
	}

	if ( client->ps.eFlags & EF_VOTED ) {
		trap_SendServerCommand( ent-g_entities, "print \"Vote already cast.\n\"" );
		return;
	}

	if ( client->pers.voteDelayTime > 0 && level.time - client->pers.voteDelayTime < VOTE_THROTTLE_MSEC ) {
		trap_SendServerCommand( ent-g_entities, "print \"You may only vote once every 2 seconds.\n\"" );
		return;
	}

	if ( voteSelection >= 0 && voteSelection == client->pers.voteLastSelection ) {
		trap_SendServerCommand( ent-g_entities, "print \"You already voted for this arena.\n\"" );
		return;
	}

	trap_SendServerCommand( ent-g_entities, "print \"Vote cast.\n\"" );

	client->ps.eFlags |= EF_VOTED;
	client->pers.voteDelayTime = level.time;
	client->pers.voteLastSelection = voteSelection;
	client->pers.voteLastEnableFrame = -1;

	trap_SendServerCommand( ent-g_entities, "disable_vote_ui" );

	if ( msg[0] == 'y' || msg[0] == 'Y' || msg[0] == '1' ) {
		level.voteYes++;
		trap_SetConfigstring( CS_VOTE_YES, va("%i", level.voteYes ) );
	} else {
		level.voteNo++;
		trap_SetConfigstring( CS_VOTE_NO, va("%i", level.voteNo ) );
	}

	// a majority will be determined in CheckVote, which will also account
	// for players entering or leaving
}

/*
==================
Cmd_CallTeamVote_f
==================
*/
void Cmd_CallTeamVote_f( gentity_t *ent ) {
	int		i, team, cs_offset;
	char	arg1[MAX_STRING_TOKENS];
	char	arg2[MAX_STRING_TOKENS];
	int		voteSelection;

	team = ent->client->sess.sessionTeam;
	voteSelection = -1;
	if ( team == TEAM_RED )
		cs_offset = 0;
	else if ( team == TEAM_BLUE )
		cs_offset = 1;
	else
		return;

	if ( !g_allowVote.integer ) {
		trap_SendServerCommand( ent-g_entities, "print \"Voting not allowed here.\n\"" );
		return;
	}

	if ( level.teamVoteTime[cs_offset] ) {
		trap_SendServerCommand( ent-g_entities, "print \"A team vote is already in progress.\n\"" );
		return;
	}
	if ( ent->client->pers.teamVoteCount >= MAX_VOTE_COUNT ) {
		trap_SendServerCommand( ent-g_entities, "print \"You have called the maximum number of team votes.\n\"" );
		return;
	}
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Not allowed to call a vote as spectator.\n\"" );
		return;
	}

	// make sure it is a valid command to vote on
	trap_Argv( 1, arg1, sizeof( arg1 ) );
	arg2[0] = '\0';
	for ( i = 2; i < trap_Argc(); i++ ) {
		if (i > 2)
			strcat(arg2, " ");
		trap_Argv( i, &arg2[strlen(arg2)], sizeof( arg2 ) - strlen(arg2) );
	}

	if( strchr( arg1, ';' ) || strchr( arg2, ';' ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid vote string.\n\"" );
		return;
	}

	if ( !Q_stricmp( arg1, "leader" ) ) {
		char netname[MAX_NETNAME], leader[MAX_NETNAME];

		if ( !arg2[0] ) {
			i = ent->client->ps.clientNum;
			voteSelection = i;
		}
		else {
			// numeric values are just slot numbers
			for (i = 0; i < 3; i++) {
				if ( !arg2[i] || arg2[i] < '0' || arg2[i] > '9' )
					break;
			}
			if ( i >= 3 || !arg2[i]) {
				i = atoi( arg2 );
				voteSelection = i;
				if ( i < 0 || i >= level.maxclients ) {
					trap_SendServerCommand( ent-g_entities, va("print \"Bad client slot: %i\n\"", i) );
					return;
				}

				if ( !g_entities[i].inuse ) {
					trap_SendServerCommand( ent-g_entities, va("print \"Client %i is not active\n\"", i) );
					return;
				}
			}
			else {
				Q_strncpyz(leader, arg2, sizeof(leader));
				Q_CleanStr(leader);
				for ( i = 0 ; i < level.maxclients ; i++ ) {
					if ( level.clients[i].pers.connected == CON_DISCONNECTED )
						continue;
					if (level.clients[i].sess.sessionTeam != team)
						continue;
					Q_strncpyz(netname, level.clients[i].pers.netname, sizeof(netname));
					Q_CleanStr(netname);
					if ( !Q_stricmp(netname, leader) ) {
						break;
					}
				}
				if ( i >= level.maxclients ) {
					trap_SendServerCommand( ent-g_entities, va("print \"%s is not a valid player on your team.\n\"", arg2) );
					return;
				}
			}
		}
		voteSelection = i;
		Com_sprintf(arg2, sizeof(arg2), "%d", i);
	} else {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid vote string.\n\"" );
		trap_SendServerCommand( ent-g_entities, "print \"Team vote commands are: leader <player>.\n\"" );
		return;
	}

	Com_sprintf( level.teamVoteString[cs_offset], sizeof( level.teamVoteString[cs_offset] ), "%s %s", arg1, arg2 );
	G_RegisterVoteCall( ent->client, ent - g_entities, voteSelection );

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].pers.connected == CON_DISCONNECTED )
			continue;
		if (level.clients[i].sess.sessionTeam == team)
			trap_SendServerCommand( i, va("print \"%s called a team vote.\n\"", ent->client->pers.netname ) );
	}

	// start the voting, the caller autoamtically votes yes
	level.teamVoteTime[cs_offset] = level.time;
	level.teamVoteYes[cs_offset] = 1;
	level.teamVoteNo[cs_offset] = 0;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam == team)
			level.clients[i].ps.eFlags &= ~EF_TEAMVOTED;
	}
	ent->client->ps.eFlags |= EF_TEAMVOTED;

	trap_SetConfigstring( CS_TEAMVOTE_TIME + cs_offset, va("%i", level.teamVoteTime[cs_offset] ) );
	trap_SetConfigstring( CS_TEAMVOTE_STRING + cs_offset, level.teamVoteString[cs_offset] );
	trap_SetConfigstring( CS_TEAMVOTE_YES + cs_offset, va("%i", level.teamVoteYes[cs_offset] ) );
	trap_SetConfigstring( CS_TEAMVOTE_NO + cs_offset, va("%i", level.teamVoteNo[cs_offset] ) );
}

/*
==================
Cmd_TeamVote_f
==================
*/
void Cmd_TeamVote_f( gentity_t *ent ) {
	int			team, cs_offset;
	char		msg[64];

	team = ent->client->sess.sessionTeam;
	if ( team == TEAM_RED )
		cs_offset = 0;
	else if ( team == TEAM_BLUE )
		cs_offset = 1;
	else
		return;

	if ( !level.teamVoteTime[cs_offset] ) {
		trap_SendServerCommand( ent-g_entities, "print \"No team vote in progress.\n\"" );
		return;
	}
	if ( ent->client->ps.eFlags & EF_TEAMVOTED ) {
		trap_SendServerCommand( ent-g_entities, "print \"Team vote already cast.\n\"" );
		return;
	}
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Not allowed to vote as spectator.\n\"" );
		return;
	}

	trap_SendServerCommand( ent-g_entities, "print \"Team vote cast.\n\"" );

	ent->client->ps.eFlags |= EF_TEAMVOTED;

	trap_Argv( 1, msg, sizeof( msg ) );

	if ( msg[0] == 'y' || msg[1] == 'Y' || msg[1] == '1' ) {
		level.teamVoteYes[cs_offset]++;
		trap_SetConfigstring( CS_TEAMVOTE_YES + cs_offset, va("%i", level.teamVoteYes[cs_offset] ) );
	} else {
		level.teamVoteNo[cs_offset]++;
		trap_SetConfigstring( CS_TEAMVOTE_NO + cs_offset, va("%i", level.teamVoteNo[cs_offset] ) );	
	}

	// a majority will be determined in TeamCheckVote, which will also account
	// for players entering or leaving
}


/*
=================
Cmd_SetViewpos_f
=================
*/
void Cmd_SetViewpos_f( gentity_t *ent ) {
	vec3_t		origin, angles;
	char		buffer[MAX_TOKEN_CHARS];
	int			i;

	if ( !g_cheats.integer ) {
		trap_SendServerCommand( ent-g_entities, va("print \"Cheats are not enabled on this server.\n\""));
		return;
	}
	if ( trap_Argc() != 5 ) {
		trap_SendServerCommand( ent-g_entities, va("print \"usage: setviewpos x y z yaw\n\""));
		return;
	}

	VectorClear( angles );
	for ( i = 0 ; i < 3 ; i++ ) {
		trap_Argv( i + 1, buffer, sizeof( buffer ) );
		origin[i] = atof( buffer );
	}

	trap_Argv( 4, buffer, sizeof( buffer ) );
	angles[YAW] = atof( buffer );

	TeleportPlayer( ent, origin, angles );
}



/*
=================
Cmd_Stats_f
=================
*/
void Cmd_Stats_f( gentity_t *ent ) {
	int i, shots, hits, accuracy;
	int totalShots = 0, totalHits = 0;
	gclient_t *client = ent->client;
	char *weaponNames[] = {
		"Gauntlet", "Machinegun", "HMG", "Shotgun", "Grenade", "Rocket",
		"Lightning", "Railgun", "Plasma", "BFG", "Grapple", "Nailgun",
		"Prox Mine", "Chaingun"
	};
	int weaponIndices[] = {
		WP_GAUNTLET, WP_MACHINEGUN, WP_HEAVY_MACHINEGUN, WP_SHOTGUN, WP_GRENADE_LAUNCHER, WP_ROCKET_LAUNCHER,
		WP_LIGHTNING, WP_RAILGUN, WP_PLASMAGUN, WP_BFG, WP_GRAPPLING_HOOK, WP_NAILGUN,
		WP_PROX_LAUNCHER, WP_CHAINGUN
	};

	if ( !client ) {
		return;
	}

	trap_SendServerCommand( ent-g_entities, va("print \"\nWeapon Stats for %s\n\"", client->pers.netname) );
	trap_SendServerCommand( ent-g_entities, "print \"Weapon     Accuracy   Hits   Shots\n\"" );
	trap_SendServerCommand( ent-g_entities, "print \"----------------------------------\n\"" );

	for ( i = 0; i < sizeof(weaponIndices) / sizeof(weaponIndices[0]); i++ ) {
		int w = weaponIndices[i];
		shots = client->pers.accuracy_shots[w];
		hits = client->pers.accuracy_hits[w];
		if ( shots > 0 ) {
			accuracy = hits * 100 / shots;
		} else {
			accuracy = 0;
		}

		if ( shots > 0 ) {
			trap_SendServerCommand( ent-g_entities, va("print \"%-10s %5i%% %6i %7i\n\"",
				weaponNames[i], accuracy, hits, shots) );
			totalShots += shots;
			totalHits += hits;
		}
	}

	if ( totalShots > 0 ) {
		accuracy = totalHits * 100 / totalShots;
	} else {
		accuracy = 0;
	}

	trap_SendServerCommand( ent-g_entities, "print \"----------------------------------\n\"" );
	trap_SendServerCommand( ent-g_entities, va("print \"Total      %5i%% %6i %7i\n\"",
		accuracy, totalHits, totalShots) );
	trap_SendServerCommand( ent-g_entities, va("print \"\nDamage Given: %i  Damage Received: %i\n\"",
		client->pers.damageGiven, client->pers.damageReceived) );
}

static qboolean G_ClientCanControlTimeouts( gentity_t *ent, team_t *teamOut ) {
	team_t team;

	if ( !ent->client ) {
		return qfalse;
	}

	if ( level.trainingMapActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"Timeouts are disabled in training.\n\"" );
		return qfalse;
	}

	team = ent->client->sess.sessionTeam;
	if ( team == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot control timeouts.\\n\"" );
		return qfalse;
	}

	if ( g_gametype.integer != GT_TOURNAMENT && g_gametype.integer < GT_TEAM ) {
		trap_SendServerCommand( ent-g_entities, "print \"Timeouts are disabled in this gametype.\\n\"" );
		return qfalse;
	}

	if ( g_gametype.integer >= GT_TEAM ) {
		if ( team != TEAM_RED && team != TEAM_BLUE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Join a team before calling a timeout.\\n\"" );
			return qfalse;
		}
		*teamOut = team;
	} else {
		*teamOut = TEAM_FREE;
	}

	return qtrue;
}

void Cmd_Timeout_f( gentity_t *ent ) {
	team_t team;
	int remaining;
	int timeoutLength;

	if ( level.timeoutActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"A timeout is already active.\\n\"" );
		return;
	}

	if ( !G_ClientCanControlTimeouts( ent, &team ) ) {
		return;
	}

	remaining = level.timeoutRemaining[team];
	if ( remaining <= 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"No timeouts remaining.\\n\"" );
		return;
	}

	level.timeoutActive = qtrue;
	level.timeoutTeam = team;
	level.timeoutOwner = ent->client->ps.clientNum;
	level.timeoutStartTime = level.time;

        timeoutLength = g_matchFactoryConfig.timeoutLengthSeconds;
        if ( timeoutLength > 0 ) {
                level.timeoutExpireTime = level.time + timeoutLength * 1000;
        } else {
                level.timeoutExpireTime = 0;
        }

	level.timeoutRemaining[team] = remaining - 1;
	if ( level.timeoutRemaining[team] < 0 ) {
		level.timeoutRemaining[team] = 0;
	}

	trap_SendServerCommand( -1, va( "print \"%s called a timeout (%i remaining).\\n\"", ent->client->pers.netname, level.timeoutRemaining[team] ) );
	G_LogPrintf( "match: timeout called team %i owner %i remaining %i length %i\n", team, level.timeoutOwner, level.timeoutRemaining[team], timeoutLength );

	G_UpdateMatchStateConfigString();
}

void Cmd_Timein_f( gentity_t *ent ) {
	int pausedDuration = 0;
	team_t owningTeam;
	int owner;

	if ( level.trainingMapActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"Training matches do not support timeouts.\n\"" );
		return;
	}

	if ( !level.timeoutActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"No timeout in progress.\\n\"" );
		return;
	}

	owningTeam = level.timeoutTeam;
	owner = level.timeoutOwner;

	if ( owningTeam == TEAM_FREE ) {
		if ( ent->client->ps.clientNum != owner ) {
			trap_SendServerCommand( ent-g_entities, "print \"Only the caller may resume play.\\n\"" );
			return;
		}
	} else if ( ent->client->sess.sessionTeam != owningTeam ) {
		trap_SendServerCommand( ent-g_entities, "print \"Only the calling team may resume play.\\n\"" );
		return;
	}

	if ( level.timeoutStartTime > 0 && level.time > level.timeoutStartTime ) {
		pausedDuration = level.time - level.timeoutStartTime;
	}

	G_ApplyTimeoutPauseDelta( pausedDuration );

	trap_SendServerCommand( -1, va( "print \"%s called time in.\\n\"", ent->client->pers.netname ) );
	G_LogPrintf( "match: timeout resumed team %i owner %i caller %i\n", owningTeam, owner, ent->client->ps.clientNum );

	G_ResetTimeoutState();
	G_UpdateMatchStateConfigString();
}

/*
=============
Cmd_Forfeit_f

Concedes the current match when permitted by the server configuration.
=============
*/
void Cmd_Forfeit_f( gentity_t *ent ) {
	team_t team;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( g_allowForfeit.integer <= 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is not enabled on this server.\n\"" );
		return;
	}

	if ( level.matchForfeited ) {
		trap_SendServerCommand( ent-g_entities, "print \"Match has already been forfeited.\n\"" );
		return;
	}

	if ( g_gametype.integer != GT_TOURNAMENT && g_gametype.integer < GT_TEAM ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available in duel or team modes.\n\"" );
		return;
	}

	team = ent->client->sess.sessionTeam;
	if ( g_gametype.integer >= GT_TEAM ) {
		if ( team != TEAM_RED && team != TEAM_BLUE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Join a team before forfeiting the match.\n\"" );
			return;
		}
	} else if ( team == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot forfeit matches.\n\"" );
		return;
	}

	G_HandleForfeit( ent );
}

/*
=================
Cmd_Complaint_f

Processes friendly-fire complaint responses from the victim.
=================
*/
static void Cmd_Complaint_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	gclient_t *client;
	int attackerNum;
	gentity_t *attacker;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;

	if ( client->complaintClient < 0 ) {
		client->complaintClient = -1;
		client->complaintEndTime = 0;
		return;
	}

	if ( client->complaintEndTime > 0 && client->complaintEndTime <= level.time ) {
		G_ComplaintResolve( ent, qfalse );
		return;
	}

	attackerNum = client->complaintClient;

	if ( attackerNum < 0 || attackerNum >= level.maxclients ) {
		client->complaintClient = -1;
		client->complaintEndTime = 0;
		trap_SendServerCommand( ent - g_entities, "complaint -3" );
		return;
	}

	attacker = &g_entities[attackerNum];

	if ( !attacker->client || attacker->client->pers.connected != CON_CONNECTED ) {
		client->complaintClient = -1;
		client->complaintEndTime = 0;
		trap_SendServerCommand( ent - g_entities, "complaint -3" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );

	if ( arg[0] == 'y' || arg[0] == 'Y' || arg[0] == '1' ) {
		G_ComplaintResolve( ent, qtrue );
		return;
	}

	G_ComplaintResolve( ent, qfalse );
}

/*
=================
ClientCommand
=================
*/
void ClientCommand( int clientNum ) {
	gentity_t *ent;
	char	cmd[MAX_TOKEN_CHARS];

	ent = g_entities + clientNum;
	if ( !ent->client ) {
		return;		// not fully in game yet
	}

	if ( G_FloodLimited( ent, "issuing commands", qfalse ) ) {
		return;
	}

	trap_Argv( 0, cmd, sizeof( cmd ) );

	if (Q_stricmp (cmd, "say") == 0) {
		Cmd_Say_f (ent, SAY_ALL, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "say_team") == 0) {
		Cmd_Say_f (ent, SAY_TEAM, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "tell") == 0) {
		Cmd_Tell_f ( ent );
		return;
	}
	if (Q_stricmp (cmd, "complaint") == 0) {
		Cmd_Complaint_f( ent );
		return;
	}
	if (Q_stricmp (cmd, "vsay") == 0) {
		Cmd_Voice_f (ent, SAY_ALL, qfalse, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "vsay_team") == 0) {
		Cmd_Voice_f (ent, SAY_TEAM, qfalse, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "vtell") == 0) {
		Cmd_VoiceTell_f ( ent, qfalse );
		return;
	}
	if (Q_stricmp (cmd, "vosay") == 0) {
		Cmd_Voice_f (ent, SAY_ALL, qfalse, qtrue);
		return;
	}
	if (Q_stricmp (cmd, "vosay_team") == 0) {
		Cmd_Voice_f (ent, SAY_TEAM, qfalse, qtrue);
		return;
	}
	if (Q_stricmp (cmd, "votell") == 0) {
		Cmd_VoiceTell_f ( ent, qtrue );
		return;
	}
	if (Q_stricmp (cmd, "vtaunt") == 0) {
		Cmd_VoiceTaunt_f ( ent );
		return;
	}
	if (Q_stricmp (cmd, "score") == 0) {
		Cmd_Score_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "ready") == 0) {
		Cmd_Ready_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "notready") == 0) {
		Cmd_NotReady_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "players") == 0) {
		Cmd_Players_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "teams") == 0) {
		Cmd_Teams_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "acc") == 0) {
		Cmd_Acc_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "cvar") == 0) {
		Cmd_Cvar_f (ent);
		return;
	}

	// ignore all other commands when at intermission
	if (level.intermissiontime) {
		Cmd_Say_f (ent, qfalse, qtrue);
		return;
	}

	if (Q_stricmp (cmd, "give") == 0)
		Cmd_Give_f (ent);
	else if (Q_stricmp (cmd, "god") == 0)
		Cmd_God_f (ent);
	else if (Q_stricmp (cmd, "notarget") == 0)
		Cmd_Notarget_f (ent);
	else if (Q_stricmp (cmd, "noclip") == 0)
		Cmd_Noclip_f (ent);
	else if (Q_stricmp (cmd, "thawtarget") == 0)
		Cmd_ThawTarget_f( ent );
	else if (Q_stricmp (cmd, "kill") == 0)
		Cmd_Kill_f (ent);
	else if (Q_stricmp (cmd, "forfeit") == 0)
		Cmd_Forfeit_f( ent );
	else if (Q_stricmp (cmd, "teamtask") == 0)
		Cmd_TeamTask_f (ent);
	else if (Q_stricmp (cmd, "levelshot") == 0)
		Cmd_LevelShot_f (ent);
	else if (Q_stricmp (cmd, "follow") == 0)
		Cmd_Follow_f (ent);
	else if (Q_stricmp (cmd, "follownext") == 0)
		Cmd_FollowCycle_f (ent, 1);
	else if (Q_stricmp (cmd, "followprev") == 0)
		Cmd_FollowCycle_f (ent, -1);
	else if (Q_stricmp (cmd, "team") == 0)
		Cmd_Team_f (ent);
	else if (Q_stricmp (cmd, "where") == 0)
		Cmd_Where_f (ent);
	else if (Q_stricmp (cmd, "callvote") == 0)
		Cmd_CallVote_f (ent);
	else if (Q_stricmp (cmd, "vote") == 0)
		Cmd_Vote_f (ent);
	else if (Q_stricmp (cmd, "callteamvote") == 0)
		Cmd_CallTeamVote_f (ent);
	else if (Q_stricmp (cmd, "teamvote") == 0)
		Cmd_TeamVote_f (ent);
	else if (Q_stricmp (cmd, "gc") == 0)
		Cmd_GameCommand_f( ent );
	else if ( !Q_stricmp( cmd, "timeout" ) || !Q_stricmp( cmd, "pause" ) )
		Cmd_Timeout_f( ent );
	else if ( !Q_stricmp( cmd, "timein" ) || !Q_stricmp( cmd, "resume" ) || !Q_stricmp( cmd, "unpause" ) )
		Cmd_Timein_f( ent );
	else if ( !Q_stricmp( cmd, "forfeit" ) )
		Cmd_Forfeit_f( ent );
	else if ( !Q_stricmp( cmd, "racepoint" ) )
		G_RaceAdminCommand( ent );
	else if ( !Q_stricmp( cmd, "race_init" ) ) {
		if ( g_gametype.integer == GT_RACE ) {
			G_RaceBroadcastInitCommand( ent - g_entities );
		} else {
			trap_SendServerCommand( clientNum, "print \"" GAMEPRINT_RACEPOINT_RACE_ONLY "\"" );
			G_LogPrintf( "cmd: %s denied outside Race for client %i\n", cmd, clientNum );
		}
	}
	else if ( !Q_stricmp( cmd, "race_info" ) ) {
		if ( g_gametype.integer == GT_RACE ) {
			G_RaceSendInfoCommand( ent - g_entities );
		} else {
			trap_SendServerCommand( clientNum, "print \"" GAMEPRINT_RACEPOINT_RACE_ONLY "\"" );
			G_LogPrintf( "cmd: %s denied outside Race for client %i\n", cmd, clientNum );
		}
	}
	else if ( !Q_stricmpn( cmd, "admin_race_point_", 17 ) ) {
		if ( g_gametype.integer == GT_RACE ) {
			int index = atoi( cmd + 17 );
			if ( !G_RaceSendPointMetadataCommand( ent - g_entities, index ) ) {
				trap_SendServerCommand( clientNum, va( "print \"" GAMEPRINT_RACEPOINT_INVALID_INDEX "\"", index ) );
				G_LogPrintf( "cmd: %s invalid index %i from client %i\n", cmd, index, clientNum );
			}
		} else {
			trap_SendServerCommand( clientNum, "print \"" GAMEPRINT_RACEPOINT_RACE_ONLY "\"" );
			G_LogPrintf( "cmd: %s denied outside Race for client %i\n", cmd, clientNum );
		}
	}
	else if (Q_stricmp (cmd, "setviewpos") == 0)
		Cmd_SetViewpos_f( ent );
	else if (Q_stricmp (cmd, "stats") == 0)
		Cmd_Stats_f( ent );
	else
		trap_SendServerCommand( clientNum, va("print \"unknown cmd %s\n\"", cmd ) );
}
