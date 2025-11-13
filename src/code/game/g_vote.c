#include "g_local.h"
#include <limits.h>

/*
=============
G_VoteUpdateCachedDelay

Return the vote delay duration derived from g_voteDelay in milliseconds and
cache it on the level state for reuse.
=============
*/
static int G_VoteUpdateCachedDelay( void ) {
	float		seconds;
	int		delayMsec;

	seconds = g_voteDelay.value;
	if ( seconds <= 0.0f ) {
		level.voteDelayMsec = 0;
		return 0;
	}

	if ( seconds >= (float)INT_MAX / 1000.0f ) {
		delayMsec = INT_MAX;
	} else {
		delayMsec = (int)( seconds * 1000.0f );
	}

	level.voteDelayMsec = delayMsec;
	return delayMsec;
}

/*
=============
G_VoteUpdateCachedLimit

Compute the effective per-client vote call limit and cache it on the level
state, falling back to the legacy MAX_VOTE_COUNT when the cvar is unset.
=============
*/
static int G_VoteUpdateCachedLimit( void ) {
	int		limit;

	limit = g_voteLimit.integer;
	if ( limit <= 0 ) {
		limit = MAX_VOTE_COUNT;
	}

	level.voteLimit = limit;
	return limit;
}

/*
=============
G_VoteGetFlags

Return the current g_voteFlags mask while mirroring it into the level state so
other systems can make consistent decisions without poking the vmCvar_t.
=============
*/
int G_VoteGetFlags( void ) {
	level.voteFlags = g_voteFlags.integer;
	return level.voteFlags;
}

/*
=============
G_VoteFlagsDisableMask

Test whether a vote option represented by the provided mask is disabled by the
active g_voteFlags configuration.
=============
*/
qboolean G_VoteFlagsDisableMask( int mask ) {
	if ( !mask ) {
		return qfalse;
	}

	return ( G_VoteGetFlags() & mask ) != 0;
}

/*
=============
G_VoteGetLimit

Expose the active per-client vote limit so command handlers can make
rate-limiting decisions without duplicating the cvar fallback logic.
=============
*/
int G_VoteGetLimit( void ) {
	return G_VoteUpdateCachedLimit();
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

	client->pers.voteDelayTime = 0;
	client->pers.voteLastSelection = -1;
	client->pers.voteLastEnableFrame = -1;
	client->pers.voteLastTime = 0;
}

/*
=============
G_InitClientVoteThrottle

Initialise vote throttle defaults for a freshly connected client.
=============
*/
void G_InitClientVoteThrottle( gclient_t *client ) {
	int		initialDelay;

	G_ResetClientVoteThrottle( client );

	if ( !client ) {
		return;
	}

	initialDelay = G_VoteUpdateCachedDelay();
	G_VoteUpdateCachedLimit();
	G_VoteGetFlags();

	if ( initialDelay > 0 ) {
		client->pers.voteDelayTime = level.startTime;
		client->pers.voteLastTime = level.startTime;
	}
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
	client->pers.voteLastTime = level.time;
	if ( client->pers.voteCount < INT_MAX ) {
		client->pers.voteCount++;
	}

	level.voteLastCaller = clientNum;
	level.voteLastSelection = voteSelection;
	level.voteLastTime = level.time;

	G_VoteUpdateCachedDelay();
	G_VoteUpdateCachedLimit();
	G_VoteGetFlags();

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
	int		delayMsec;
	int		voteLimit;

	delayMsec = G_VoteUpdateCachedDelay();
	voteLimit = G_VoteUpdateCachedLimit();
	G_VoteGetFlags();

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gclient_t	*client;

		client = &level.clients[clientNum];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		if ( client->pers.voteDelayTime <= 0 ) {
			continue;
		}

		if ( delayMsec > 0 && level.time - client->pers.voteDelayTime < delayMsec ) {
			continue;
		}

		if ( voteLimit > 0 && client->pers.voteCount >= voteLimit ) {
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
