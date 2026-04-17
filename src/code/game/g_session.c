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
#include <time.h>


/*
=======================================================================

  SESSION DATA

Session data is the only data that stays persistant across level loads
and tournament restarts.
=======================================================================
*/

/*
================
G_WriteClientSessionData

Called on game shutdown
================
*/
void G_WriteClientSessionData( gclient_t *client ) {
	const char	*s;
	const char	*var;

	s = va("%i %ld %i %i %i %i %i %i %i %i %i %i",
		client->sess.sessionTeam,
		(long)client->sess.spectatorTime,
		client->sess.spectatorState,
		client->sess.spectatorClient,
		client->sess.selectedSpawnWeapon,
		client->sess.wins,
		client->sess.losses,
		client->sess.teamLeader,
		client->sess.privilege,
		client->sess.spectateOnly,
		client->sess.spectatorQueuePosition,
		client->sess.muted
		);

	var = va( "session%i", client - level.clients );

	trap_Cvar_Set( var, s );
}

/*
================
G_ReadSessionData

Called on a reconnect
================
*/
void G_ReadSessionData( gclient_t *client ) {
	char	s[MAX_STRING_CHARS];
	const char	*var;

	// bk001205 - format
	int teamLeader;
	int spectatorState;
	int sessionTeam;
	int privilege;
	int spectateOnly;
	int spectatorQueuePosition;
	int muted;
	int selectedSpawnWeapon;
	int sessionField34;
	int ignoredSessionTail;
	long spectatorTime;

	var = va( "session%i", client - level.clients );
	trap_Cvar_VariableStringBuffer( var, s, sizeof(s) );

	sessionTeam = TEAM_SPECTATOR;
	spectatorTime = 0;
	spectatorState = SPECTATOR_FREE;
	client->sess.spectatorClient = 0;
	selectedSpawnWeapon = 0;
	client->sess.wins = 0;
	client->sess.losses = 0;
	teamLeader = 0;
	privilege = 0;
	spectateOnly = 0;
	spectatorQueuePosition = 0;
	muted = 0;
	sessionField34 = 0;
	ignoredSessionTail = 0;
	sscanf( s, "%i %ld %i %i %i %i %i %i %i %i %i %i %i %i",
		&sessionTeam,                 // bk010221 - format
		&spectatorTime,
		&spectatorState,              // bk010221 - format
		&client->sess.spectatorClient,
		&selectedSpawnWeapon,
		&client->sess.wins,
		&client->sess.losses,
		&teamLeader,                  // bk010221 - format
		&privilege,
		&spectateOnly,
		&spectatorQueuePosition,
		&muted,
		&sessionField34,
		&ignoredSessionTail
		);
	client->sess.spectatorTime = (int)spectatorTime;
	client->sess.selectedSpawnWeapon = selectedSpawnWeapon;
	client->sess.privilege = privilege;
	client->sess.spectateOnly = spectateOnly;
	client->sess.spectatorQueuePosition = spectatorQueuePosition;
	client->sess.sessionField34 = sessionField34;
	client->sess.skill1 = 0;
	client->sess.skill2 = 0;
	client->sess.skill3 = 0;
	client->sess.muted = (qboolean)muted;
	client->sess.spectatorQueuePositionDirty = qfalse;

	// bk001205 - format issues
	client->sess.sessionTeam = (team_t)sessionTeam;
	client->sess.spectatorState = (spectatorState_t)spectatorState;
	if ( g_teamSpawnAsSpec.integer && g_gametype.integer >= GT_TEAM && level.warmupTime != 0 ) {
		client->sess.sessionTeam = TEAM_SPECTATOR;
	}
	client->sess.teamLeader = (qboolean)teamLeader;
}


/*
================
G_InitSessionData

Called on a first-time connect
================
*/
void G_InitSessionData( gclient_t *client, char *userinfo ) {
	clientSession_t	*sess;

	sess = &client->sess;

	// initial team determination
	if ( g_gametype.integer >= GT_TEAM && g_teamAutoJoin.integer ) {
		sess->sessionTeam = PickTeam( -1 );
		BroadcastTeamChange( client, -1 );
	} else {
		sess->sessionTeam = TEAM_SPECTATOR;
	}
	sess->spectatorState = SPECTATOR_FREE;
	sess->spectatorTime = (int)time( NULL );
	sess->selectedSpawnWeapon = 0;
	sess->spectateOnly = qfalse;
	sess->spectatorQueuePosition = 0;
	sess->spectatorQueuePositionDirty = qfalse;
	sess->muted = qfalse;
	sess->sessionField34 = 0;

	if ( client->pers.localClient ) {
		sess->privilege = PRIV_ROOT;
	} else if ( client->pers.steamIdValid ) {
		unsigned long long	steamIdValue;
		char			steamIdString[32];

		steamIdValue = ( (unsigned long long)client->pers.steamIdHigh << 32 ) | client->pers.steamIdLow;
		Com_sprintf( steamIdString, sizeof( steamIdString ), "%llu", steamIdValue );
		sess->privilege = G_AdminAccessForSteamID( steamIdString );
	} else {
		sess->privilege = G_AdminAccessForSteamID( Info_ValueForKey( userinfo, "steamid" ) );
	}
	sess->skill1 = 0;
	sess->skill2 = 0;
	sess->skill3 = 0;
	if ( g_gametype.integer == GT_TOURNAMENT ) {
		sess->spectateOnly = qtrue;
	}

	G_WriteClientSessionData( client );
}


/*
==================
G_WriteSessionData

==================
*/
void G_WriteSessionData( void ) {
	int		i;

	trap_Cvar_Set( "session", va("%i", g_gametype.integer) );
	if ( g_gametype.integer == GT_TOURNAMENT ) {
		G_UpdateTournamentQueuePositions();
	}

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].pers.connected == CON_CONNECTED ) {
			G_WriteClientSessionData( &level.clients[i] );
		}
	}
}
