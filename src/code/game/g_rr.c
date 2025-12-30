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
// g_rr.c
//

#include "g_local.h"

void G_RRInitClient( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RED_ROVER ) {
		return;
	}

	ent->client->rrInfectionState = RR_STATE_SURVIVOR;
	ent->client->rrInfectionChangeTime = 0;
	ent->client->rrAccumulatedDamage = 0;
}

void G_RRProcessClient( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RED_ROVER ) {
		return;
	}

	// Infection logic would go here if enabled
	if ( g_rrInfected.integer ) {
		// ...
	}
}

void G_RRHandlePlayerDeath( gentity_t *victim, gentity_t *attacker ) {
	if ( g_gametype.integer != GT_RED_ROVER ) {
		return;
	}

	if ( g_rrInfected.integer ) {
		// Handle infection transfer
	} else {
		// Swap teams
		if ( victim->client->sess.sessionTeam == TEAM_RED ) {
			victim->client->sess.sessionTeam = TEAM_BLUE;
		} else if ( victim->client->sess.sessionTeam == TEAM_BLUE ) {
			victim->client->sess.sessionTeam = TEAM_RED;
		}
		victim->client->sess.teamLeader = qfalse;
		ClientUserinfoChanged( victim->s.number );
	}
}

void G_RRHandleDamageScore( gentity_t *attacker, gentity_t *targ, int damage ) {
	if ( g_gametype.integer != GT_RED_ROVER ) {
		return;
	}

	// Score based on damage dealt
	if ( attacker && attacker->client && targ && targ->client ) {
		attacker->client->ps.persistant[PERS_SCORE] += damage;
	}
}

void G_RRResetRoundState( void ) {
	// Reset any round-specific RR state
}

void G_RRTrackRoundActivity( void ) {
	// Monitor round progress
}
