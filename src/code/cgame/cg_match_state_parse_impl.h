#ifndef CG_MATCH_STATE_PARSE_IMPL_H
#define CG_MATCH_STATE_PARSE_IMPL_H

#include "../../game/match_state_keys.h"

/*
============
CG_InfoIntForMatchKey

Extracts an integer from the match-state info string payload, falling back to the provided default.
============
*/
static int CG_InfoIntForMatchKey( const char *info, const char *key, int defaultValue ) {
	const char *value;

	if ( !info || !key ) {
		return defaultValue;
	}

	value = Info_ValueForKey( info, key );
	if ( !value || !*value ) {
		return defaultValue;
	}

	return atoi( value );
}

/*
============
CG_ResetMatchStateFields

Clears cached match-state variables before parsing.
============
*/
static void CG_ResetMatchStateFields( void ) {
	int i;

	cgs.matchOvertimeActive = qfalse;
	cgs.matchOvertimeStartTime = 0;
	cgs.matchOvertimeEndTime = 0;
	cgs.matchOvertimeCount = 0;
	cgs.matchTimeoutActive = qfalse;
	cgs.matchTimeoutTeam = TEAM_FREE;
	cgs.matchTimeoutExpireTime = 0;
	cgs.matchTimeoutOwner = -1;
	for ( i = 0; i < TEAM_NUM_TEAMS; i++ ) {
		cgs.matchTimeoutRemaining[i] = 0;
	}
	cgs.matchTimeoutLengthSeconds = 0;
	cgs.matchTimeoutCountPerTeam = 0;
	cgs.matchOvertimeLengthSeconds = 0;
	cgs.matchSuddenDeathRespawnsEnabled = qfalse;
	cgs.matchSuddenDeathStartSeconds = 0;
	cgs.matchSuddenDeathTickSeconds = 0;
	cgs.matchSuddenDeathMaxSeconds = 0;
	cgs.matchSuddenDeathIncrementSeconds = 0;
	cgs.matchSuddenDeathPrintAnnouncements = qfalse;
	cgs.matchSuddenDeathSpawnDelayActive = qfalse;
	cgs.matchRoundTransitionTime = 0;
	cgs.matchRoundNumber = 0;
	cgs.matchRoundTurn = 0;
	cgs.matchRoundState = 0;
}

/*
============
CG_ParseMatchState

Parses the match state configstring and updates client state.
============
*/
static void CG_ParseMatchState( void ) {
	const char *info;
	int timeoutRemaining;

	CG_ResetMatchStateFields();

	info = CG_ConfigString( CS_MATCH_STATE );
	if ( !info || !*info ) {
		return;
	}

	cgs.matchRoundTransitionTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIME, 0 );
	cgs.matchRoundNumber = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_ROUND, 0 );
	cgs.matchRoundTurn = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TURN, 0 );
	cgs.matchRoundState = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_STATE, 0 );
	cgs.matchOvertimeActive = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_ACTIVE, 0 ) ? qtrue : qfalse;
	cgs.matchOvertimeStartTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_START, 0 );
	cgs.matchOvertimeEndTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_END, 0 );
	cgs.matchOvertimeCount = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_COUNT, 0 );
	cgs.matchOvertimeLengthSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_LENGTH, 0 );
	cgs.matchTimeoutActive = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_ACTIVE, 0 ) ? qtrue : qfalse;
	cgs.matchTimeoutTeam = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_TEAM, TEAM_FREE );
	cgs.matchTimeoutExpireTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_EXPIRE, 0 );
	cgs.matchTimeoutOwner = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_OWNER, -1 );
	timeoutRemaining = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_RED, 0 );
	if ( timeoutRemaining < 0 ) {
		timeoutRemaining = 0;
	}
	cgs.matchTimeoutRemaining[TEAM_RED] = timeoutRemaining;
	timeoutRemaining = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_BLUE, 0 );
	if ( timeoutRemaining < 0 ) {
		timeoutRemaining = 0;
	}
	cgs.matchTimeoutRemaining[TEAM_BLUE] = timeoutRemaining;
	cgs.matchTimeoutLengthSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_LENGTH, 0 );
	cgs.matchTimeoutCountPerTeam = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_COUNT, 0 );
	cgs.matchSuddenDeathRespawnsEnabled = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_RESPAWNS, 0 ) ? qtrue : qfalse;
	cgs.matchSuddenDeathStartSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_START, 0 );
	cgs.matchSuddenDeathTickSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_TICK, 0 );
	cgs.matchSuddenDeathMaxSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_MAX, 0 );
	cgs.matchSuddenDeathIncrementSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_INCREMENT, 0 );
	cgs.matchSuddenDeathPrintAnnouncements = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_PRINT, 0 ) ? qtrue : qfalse;
	cgs.matchSuddenDeathSpawnDelayActive = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_DELAY, 0 ) ? qtrue : qfalse;
}

#endif // CG_MATCH_STATE_PARSE_IMPL_H
