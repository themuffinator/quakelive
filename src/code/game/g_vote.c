#include "g_local.h"

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
