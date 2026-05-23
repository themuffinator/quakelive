#include "g_local.h"
#include <string.h>

enum {
	VOTE_RESULT_PENDING = 1,
	VOTE_RESULT_PASSED,
	VOTE_RESULT_FAILED
};

/*
=============
G_ParseVoteString

Splits a queued vote string into its command token and optional argument tail.
=============
*/
static qboolean G_ParseVoteString( const char *voteString, char *command, size_t commandSize, char *args, size_t argsSize ) {
	const char	*cursor;
	int		commandLength;

	if ( !voteString || !voteString[0] || !command || commandSize == 0 ) {
		return qfalse;
	}

	if ( args && argsSize > 0 ) {
		args[0] = '\0';
	}

	cursor = voteString;
	while ( *cursor && *cursor <= ' ' ) {
		++cursor;
	}

	if ( !*cursor ) {
		command[0] = '\0';
		return qfalse;
	}

	commandLength = 0;
	while ( cursor[commandLength] && cursor[commandLength] > ' ' ) {
		++commandLength;
	}

	if ( commandLength >= (int)commandSize ) {
		commandLength = (int)commandSize - 1;
	}

	memcpy( command, cursor, commandLength );
	command[commandLength] = '\0';
	cursor += commandLength;

	while ( *cursor && *cursor <= ' ' ) {
		++cursor;
	}

	if ( args && argsSize > 0 ) {
		Q_strncpyz( args, cursor, argsSize );
	}

	return qtrue;
}

/*
=============
G_VoteArgsAreUnsignedInteger

Reports whether the parsed vote argument tail is a non-empty unsigned integer.
=============
*/
static qboolean G_VoteArgsAreUnsignedInteger( const char *args ) {
	const unsigned char	*scan;

	if ( !args || !args[0] ) {
		return qfalse;
	}

	for ( scan = (const unsigned char *)args; *scan; scan++ ) {
		if ( *scan < '0' || *scan > '9' ) {
			return qfalse;
		}
	}

	return qtrue;
}

/*
=============
G_ClearVoteState

Clears the active public vote state, matching the retail helper used by both
vote resolution and intermission bootstrap.
=============
*/
void G_ClearVoteState( void ) {
	int		clientNum;

	level.voteTime = 0;
	level.voteExecuteTime = 0;
	level.voteEligibleTime = 0;
	level.voteYes = 0;
	level.voteNo = 0;
	level.voteString[0] = '\0';
	level.voteDisplayString[0] = '\0';

	trap_SetConfigstring( CS_VOTE_TIME, "" );
	trap_SetConfigstring( CS_VOTE_STRING, "" );
	trap_SetConfigstring( CS_VOTE_YES, "0" );
	trap_SetConfigstring( CS_VOTE_NO, "0" );

	if ( !level.clients ) {
		return;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		level.clients[clientNum].pers.voteState = VOTE_STATE_NONE;
		level.clients[clientNum].ps.eFlags &= ~EF_VOTED;
	}
}

/*
=============
G_ResetClientVoteThrottle

Reset the vote throttle bookkeeping for a client so the UI can re-enable immediately.
=============
*/
void G_ResetClientVoteThrottle( gclient_t *client ) {
	if ( !client ) {
		return;
	}

	client->pers.voteState = VOTE_STATE_NONE;
	client->pers.voteDelayTime = 0;
	client->pers.voteLastSelection = -1;
	client->pers.voteLastEnableFrame = -1;
}

/*
=============
G_InitClientVoteThrottle

Initialise vote throttle defaults for a freshly connected client.
=============
*/
void G_InitClientVoteThrottle( gclient_t *client ) {
	G_ResetClientVoteThrottle( client );
}

/*
=============
G_RegisterVoteCall

Record a vote attempt so the caller's UI is hidden until the throttle expires.
=============
*/
void G_RegisterVoteCall( gclient_t *client, int clientNum, int voteSelection ) {
	if ( !client ) {
		return;
	}

	client->pers.voteDelayTime = level.time;
	client->pers.voteLastSelection = voteSelection;
	client->pers.voteLastEnableFrame = -1;

	trap_SendServerCommand( clientNum, "disable_vote_ui" );
}

/*
=============
G_UpdateVoteThrottle

Re-enable the vote UI once the throttle delay has elapsed for any connected client.
=============
*/
void G_UpdateVoteThrottle( void ) {
	int		clientNum;

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gclient_t	*client;

		client = &level.clients[clientNum];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		if ( client->pers.voteDelayTime <= 0 ) {
			continue;
		}

		if ( level.time - client->pers.voteDelayTime < VOTE_THROTTLE_MSEC ) {
			continue;
		}

		if ( client->pers.voteLastEnableFrame == level.framenum ) {
			continue;
		}

		trap_SendServerCommand( clientNum, "enable_vote_ui" );
		client->pers.voteDelayTime = 0;
		client->pers.voteLastEnableFrame = level.framenum;
	}
}

/*
=============
G_UpdateVoteCounts

Rebuilds the current public vote counts from each connected client's retail
vote-state latch and resolves privileged pass/veto shortcuts.
=============
*/
int G_UpdateVoteCounts( void ) {
	int		clientNum;
	int		eligibleCount;
	int		yesCount;
	int		noCount;

	eligibleCount = 0;
	yesCount = 0;
	noCount = 0;

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gclient_t	*client;

		client = &level.clients[clientNum];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		switch ( client->pers.voteState ) {
		case VOTE_STATE_ELIGIBLE:
			eligibleCount++;
			break;

		case VOTE_STATE_YES:
			eligibleCount++;
			yesCount++;
			break;

		case VOTE_STATE_NO:
			eligibleCount++;
			noCount++;
			break;

		case VOTE_STATE_FORCE_PASS:
			trap_SendServerCommand( -1, va( "print \"%s passed the vote.\\n\"", client->pers.netname ) );
			return VOTE_RESULT_PASSED;

		case VOTE_STATE_FORCE_VETO:
			trap_SendServerCommand( -1, va( "print \"%s vetoed the vote.\\n\"", client->pers.netname ) );
			return VOTE_RESULT_FAILED;

		default:
			break;
		}
	}

	level.voteYes = yesCount;
	level.voteNo = noCount;
	trap_SetConfigstring( CS_VOTE_YES, va( "%i", level.voteYes ) );
	trap_SetConfigstring( CS_VOTE_NO, va( "%i", level.voteNo ) );

	if ( yesCount > ( eligibleCount / 2 ) ) {
		return VOTE_RESULT_PASSED;
	}

	if ( noCount >= ( ( eligibleCount + 1 ) / 2 ) ) {
		return VOTE_RESULT_FAILED;
	}

	return VOTE_RESULT_PENDING;
}

/*
=============
G_TryExecuteVoteString

Consumes the retail Quake Live vote strings that execute through native helper
logic instead of the generic console-command path.
=============
*/
qboolean G_TryExecuteVoteString( const char *voteString ) {
	char	command[MAX_TOKEN_CHARS];
	char	args[MAX_STRING_CHARS];

	if ( !G_ParseVoteString( voteString, command, sizeof( command ), args, sizeof( args ) ) ) {
		return qfalse;
	}

	if ( !Q_stricmp( command, "cointoss" ) ) {
		const char	*result;

		result = ( rand() & 1 ) ? "HEADS" : "TAILS";
		trap_SendServerCommand( -1, va( "print \"^3The coin is: ^5%s^7\\n\"", result ) );
		return qtrue;
	}

	if ( !Q_stricmp( command, "random" ) ) {
		int upperLimit;

		if ( !G_VoteArgsAreUnsignedInteger( args ) ) {
			trap_SendServerCommand( -1, "print \"Usage: ^3\\callvote random <2 to 100>^7\\n\"" );
			trap_SendServerCommand( -1, "print \"       ^7Picks a number from 1 to <value>\\n\"" );
			trap_SendServerCommand( -1, "print \"       ^2callvote random 2 ^7mimics flipping a coin\\n\"" );
			return qtrue;
		}

		upperLimit = atoi( args );
		if ( upperLimit == 2 ) {
			const char	*result;

			result = ( rand() & 1 ) ? "HEADS" : "TAILS";
			trap_SendServerCommand( -1, va( "print \"^3The coin is: ^5%s^7\\n\"", result ) );
			return qtrue;
		}
		if ( upperLimit >= 3 && upperLimit <= 100 ) {
			trap_SendServerCommand( -1, va( "print \"^3Random number is: ^5%d^7\\n\"", ( rand() % upperLimit ) + 1 ) );
			return qtrue;
		}

		trap_SendServerCommand( -1, "print \"Usage: ^3\\callvote random <2 to 100>^7\\n\"" );
		trap_SendServerCommand( -1, "print \"       ^7Picks a number from 1 to <value>\\n\"" );
		trap_SendServerCommand( -1, "print \"       ^2callvote random 2 ^7mimics flipping a coin\\n\"" );
		return qtrue;
	}

	if ( !Q_stricmp( command, "loadouts" ) ) {
		if ( !args[0] ) {
			return qfalse;
		}

		if ( !Q_stricmp( args, "ON" ) ) {
			trap_Cvar_Set( "g_loadout", "1" );
			return qtrue;
		}
		if ( !Q_stricmp( args, "OFF" ) ) {
			trap_Cvar_Set( "g_loadout", "0" );
			return qtrue;
		}

		trap_SendServerCommand( -1, "print \"^3Valid loadout options are:    ^5ON    ^5OFF^7\\n\"" );
		return qtrue;
	}

	if ( !Q_stricmp( command, "ammo" ) ) {
		if ( !args[0] ) {
			return qfalse;
		}

		if ( !Q_stricmp( args, "GLOBAL" ) ) {
			trap_Cvar_Set( "g_ammoPack", "1" );
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			return qtrue;
		}
		if ( !Q_stricmp( args, "WEAP" ) ) {
			trap_Cvar_Set( "g_ammoPack", "0" );
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			return qtrue;
		}

		trap_SendServerCommand( -1, "print \"^3Valid loadout options are:    ^5GLOBAL    ^5WEAP^7\\n\"" );
		return qtrue;
	}

	if ( !Q_stricmp( command, "shuffle" ) || !Q_stricmp( command, "shuffle_teams" ) ) {
		Cmd_ShuffleTeams_f();
		return qtrue;
	}

	if ( !Q_stricmp( command, "teamsize" ) ) {
		int		size;
		int		redCount;
		int		blueCount;

		if ( !args[0] ) {
			return qfalse;
		}

		size = atoi( args );
		redCount = TeamCount( -1, TEAM_RED );
		blueCount = TeamCount( -1, TEAM_BLUE );
		if ( size > 0 && redCount > size ) {
			trap_SendServerCommand( -1, va( "print \"^1%s has more than %d players.\\n\"", "Red Team", size ) );
			return qtrue;
		}
		if ( size > 0 && blueCount > size ) {
			trap_SendServerCommand( -1, va( "print \"^1%s has more than %d players.\\n\"", "Blue Team", size ) );
			return qtrue;
		}

		trap_Cvar_Set( "g_teamSizeMin", va( "%i", size ) );
		return qtrue;
	}

	if ( !Q_stricmp( command, "timers" ) ) {
		int enabled;

		if ( !args[0] ) {
			return qfalse;
		}

		if ( !Q_stricmp( args, "ON" ) ) {
			enabled = 1;
		} else if ( !Q_stricmp( args, "OFF" ) ) {
			enabled = 0;
		} else {
			trap_SendServerCommand( -1, "print \"^3Valid item timer options are:    ^5ON    ^5OFF^7\\n\"" );
			return qtrue;
		}

		trap_Cvar_Set( "g_itemTimers", va( "%i", enabled ) );
		G_BroadcastItemTimerState( enabled, g_itemHeight.integer );
		return qtrue;
	}

	if ( !Q_stricmp( command, "weaprespawn" ) ) {
		if ( !args[0] ) {
			return qfalse;
		}

		trap_Cvar_Set( "g_weaponRespawn", va( "%i", atoi( args ) ) );
		return qtrue;
	}

	return qfalse;
}
