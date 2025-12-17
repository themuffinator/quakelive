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

#include "../../common/auth_credentials.h"
#include "../../common/platform/platform_config.h"
#include <limits.h>


/*
=============
G_ParseRatingScaleValue

Converts a userinfo token into a rating scale fallback value.
=============
*/
static float G_ParseRatingScaleValue( const char *value ) {
	float	scale;

	if ( !value || !value[0] ) {
		return 1.0f;
	}

	scale = (float)atof( value );
	if ( scale <= 0.0f ) {
		return 1.0f;
	}

	return scale;
}

/*
=============
	G_LoadClientRatingMetadata

Refreshes the cached rating metadata for the supplied client.
=============
*/
static void G_LoadClientRatingMetadata( gclient_t *client, const char *userinfo ) {
	const char	*damageScale;
	const char	*scoreScale;

	if ( !client ) {
		return;
	}

	if ( !userinfo ) {
		client->pers.ratingDamageScale = 1.0f;
		client->pers.ratingScoreScale = 1.0f;
		client->pers.ratingMetadataLoaded = qfalse;
	client->pers.itemProgressionTier = ( g_training.integer != 0 ) ? 0 : ITEM_UNLOCK_TIER_NONE;
	client->pers.progressionFlags = 0;
		return;
	}

	damageScale = Info_ValueForKey( userinfo, "rating_damage" );
	scoreScale = Info_ValueForKey( userinfo, "rating_score" );

	client->pers.ratingDamageScale = G_ParseRatingScaleValue( damageScale );
	client->pers.ratingScoreScale = G_ParseRatingScaleValue( scoreScale );
	client->pers.ratingMetadataLoaded = qtrue;
}

/*
=============
G_FreezeClientEndFrame

Runs the thaw and auto-respawn timers for frozen players.
=============
*/
void G_FreezeClientEndFrame( gentity_t *ent ) {
	gclient_t	*client;
	gentity_t	*helper;
	int		thawTick;
	int		thawTotal;
	int		helperCount;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( !G_FreezeGametypeEnabled() ) {
		return;
	}

	client = ent->client;
	thawTick = level.freezeConfig.thawTick;
	thawTotal = level.freezeConfig.thawTime;
	if ( thawTick <= 0 ) {
		thawTick = thawTotal;
	}
	if ( thawTick <= 0 ) {
		thawTick = 100;
	}
	if ( thawTotal <= 0 ) {
		thawTotal = 2000;
	}

	if ( client->freezeFrozen ) {
		helper = NULL;
		helperCount = G_FreezeCountThawHelpers( ent, &helper );
		if ( helperCount > 0 ) {
			if ( client->freezeNextThawTick <= level.time ) {
				client->freezeAccumulatedThaw += helperCount * thawTick;
				if ( client->freezeAccumulatedThaw > thawTotal ) {
					client->freezeAccumulatedThaw = thawTotal;
				}
				client->freezeNextThawTick = level.time + thawTick;
				client->freezeLastHelper = helper ? helper->s.number : -1;
			}
			if ( client->freezeAccumulatedThaw >= thawTotal ) {
				G_FreezeThawClient( ent, qfalse, client->freezeLastHelper );
				return;
			}
		} else {
			client->freezeAccumulatedThaw = 0;
			client->freezeNextThawTick = level.time + thawTick;
			client->freezeLastHelper = -1;
		}

		if ( client->freezeAutoThawTime > 0 && level.time >= client->freezeAutoThawTime ) {
			G_FreezeThawClient( ent, qtrue, -1 );
			return;
		}
		if ( client->freezeEnvironmentalRespawnTime > 0
		&& level.time >= client->freezeEnvironmentalRespawnTime ) {
			G_FreezeThawClient( ent, qtrue, -1 );
			return;
		}
	} else if ( client->freezeProtectedUntil > 0 && level.time >= client->freezeProtectedUntil ) {
		client->freezeProtectedUntil = 0;
	}
}

/*
=============
G_FreezeHandlePlayerDeath

Intercepts fatal damage so freeze rounds immobilize players instead of killing them.
=============
*/
qboolean G_FreezeHandlePlayerDeath( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int meansOfDeath ) {
	gclient_t	*client;
	gentity_t	*ent;
	int		killer;
	char		*killerName;
	char		*obit;
	int		contents;
	qboolean	environmental;
	int		i;

	if ( !G_FreezeGametypeEnabled() || !self || !self->client ) {
		return qfalse;
	}

	client = self->client;
	if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return qtrue;
	}

	if ( level.roundState != ROUNDSTATE_ACTIVE ) {
		return qfalse;
	}

	CheckAlmostCapture( self, attacker );
	CheckAlmostScored( self, attacker );

	if ( client->hook ) {
		Weapon_HookFree( client->hook );
	}
	if ( ( client->ps.eFlags & EF_TICKING ) && self->activator ) {
		client->ps.eFlags &= ~EF_TICKING;
		self->activator->think = G_FreeEntity;
		self->activator->nextthink = level.time;
	}

	environmental = qfalse;
	if ( attacker ) {
		killer = attacker->s.number;
		if ( attacker->client ) {
			killerName = attacker->client->pers.netname;
		} else {
			killerName = "<non-client>";
			environmental = qtrue;
		}
	} else {
		killer = ENTITYNUM_WORLD;
		killerName = "<world>";
		environmental = qtrue;
	}

	if ( killer < 0 || killer >= MAX_CLIENTS ) {
		killer = ENTITYNUM_WORLD;
		killerName = "<world>";
	}

	if ( meansOfDeath < 0 || meansOfDeath >= (int)( sizeof( modNames ) / sizeof( modNames[0] ) ) ) {
		obit = "<bad obituary>";
	} else {
		obit = modNames[ meansOfDeath ];
	}

	G_LogPrintf( "Kill: %i %i %i: %s killed %s by %s\n",
	killer, self->s.number, meansOfDeath, killerName,
	client->pers.netname, obit );

	ent = G_TempEntity( self->r.currentOrigin, EV_OBITUARY );
	ent->s.eventParm = meansOfDeath;
	ent->s.otherEntityNum = self->s.number;
	ent->s.otherEntityNum2 = killer;
	ent->r.svFlags = SVF_BROADCAST;

	self->enemy = attacker;
	client->ps.persistant[PERS_KILLED]++;

	if ( attacker && attacker->client ) {
		attacker->client->lastkilled_client = self->s.number;

		if ( attacker == self || OnSameTeam( self, attacker ) ) {
			AddScore( attacker, self->r.currentOrigin, -1 );
		} else {
			AddScore( attacker, self->r.currentOrigin, 1 );
			G_ADAwardBonus( attacker, self->r.currentOrigin, g_adElimScoreBonus.integer, S_COLOR_YELLOW "Elimination bonus" );

			if ( meansOfDeath == MOD_GAUNTLET ) {
				attacker->client->ps.persistant[PERS_GAUNTLET_FRAG_COUNT]++;
				attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP);
				attacker->client->ps.eFlags |= EF_AWARD_GAUNTLET;
				attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;
				client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_GAUNTLETREWARD;
			}

			if ( level.time - attacker->client->lastKillTime < CARNAGE_REWARD_TIME ) {
				attacker->client->ps.persistant[PERS_EXCELLENT_COUNT]++;
				attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP);
				attacker->client->ps.eFlags |= EF_AWARD_EXCELLENT;
				attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;
			}
			attacker->client->lastKillTime = level.time;
		}
	} else {
		AddScore( self, self->r.currentOrigin, -1 );
	}

	Team_FragBonuses( self, inflictor, attacker );
	G_RRHandlePlayerDeath( self, attacker );

	if ( meansOfDeath == MOD_SUICIDE ) {
		if ( client->ps.powerups[PW_NEUTRALFLAG] ) {
			Team_ReturnFlag( TEAM_FREE );
			client->ps.powerups[PW_NEUTRALFLAG] = 0;
		} else if ( client->ps.powerups[PW_REDFLAG] ) {
			Team_ReturnFlag( TEAM_RED );
			client->ps.powerups[PW_REDFLAG] = 0;
		} else if ( client->ps.powerups[PW_BLUEFLAG] ) {
			Team_ReturnFlag( TEAM_BLUE );
			client->ps.powerups[PW_BLUEFLAG] = 0;
		}
	} else {
		if ( client->ps.powerups[PW_NEUTRALFLAG] ) {
			Team_ReturnFlag( TEAM_FREE );
		} else if ( client->ps.powerups[PW_REDFLAG] ) {
			Team_ReturnFlag( TEAM_RED );
		} else if ( client->ps.powerups[PW_BLUEFLAG] ) {
			Team_ReturnFlag( TEAM_BLUE );
		}
	}
	TossClientPersistantPowerups( self );
	if ( g_gametype.integer == GT_HARVESTER ) {
		TossClientCubes( self );
	}

	Cmd_Score_f( self );
	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t *other;

		other = &level.clients[i];
		if ( other->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( other->sess.sessionTeam != TEAM_SPECTATOR ) {
			continue;
		}
		if ( other->sess.spectatorClient == self->s.number ) {
			Cmd_Score_f( g_entities + i );
		}
	}

	contents = trap_PointContents( self->r.currentOrigin, -1 );
	if ( !( contents & CONTENTS_NODROP ) ) {
		G_FreezeApplyFreezeState( self, environmental );
	} else {
		G_FreezeApplyFreezeState( self, qtrue );
	}

	return qtrue;
}



static const char *G_GetAuthOutcomeString( qlAuthOutcome outcome ) {
        switch ( outcome ) {
        case QL_AUTH_OUTCOME_SUCCESS:
                return "success";
        case QL_AUTH_OUTCOME_RETRY:
                return "retry";
        case QL_AUTH_OUTCOME_FAILURE:
                return "failure";
        default:
                break;
        }

        return "unknown";
}

static void G_WritePlatformAuthUserinfo( int clientNum, char *userinfo, const char *result, const char *outcome, const char *message ) {
        if ( !userinfo ) {
                return;
        }

        Info_SetValueForKey( userinfo, QL_AUTH_USERINFO_KEY_RESULT, result ? result : "" );
        Info_SetValueForKey( userinfo, QL_AUTH_USERINFO_KEY_OUTCOME, outcome ? outcome : "" );
        Info_SetValueForKey( userinfo, QL_AUTH_USERINFO_KEY_MESSAGE, message ? message : "" );

        trap_SetUserinfo( clientNum, userinfo );
}

static qboolean G_ParseSteamId( const char *steamId, unsigned long long *outValue ) {
        unsigned long long value;
        const char *ch;

        if ( !steamId || !steamId[0] || !outValue ) {
                return qfalse;
        }

        value = 0ull;

        for ( ch = steamId; *ch; ++ch ) {
                if ( *ch < '0' || *ch > '9' ) {
                        return qfalse;
                }

                // Detect overflow before multiplying.
                if ( value > (ULLONG_MAX / 10ull) ) {
                        return qfalse;
                }

                value *= 10ull;

                if ( value > (ULLONG_MAX - (unsigned long long)(*ch - '0')) ) {
                        return qfalse;
                }

                value += (unsigned long long)(*ch - '0');
        }

        *outValue = value;
        return qtrue;
}

static void G_BuildSteamAuthToken( const char *userinfo, char *buffer, size_t bufferSize ) {
	const char *auth;
	const char *authPart1;
	const char *authPart2;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';

	if ( !userinfo ) {
		return;
	}

	auth = Info_ValueForKey( userinfo, "auth" );
	authPart1 = Info_ValueForKey( userinfo, "author" );
	authPart2 = Info_ValueForKey( userinfo, "author2" );

	if ( auth && auth[0] ) {
		Q_strncpyz( buffer, auth, bufferSize );
		return;
	}

	if ( authPart1 && authPart1[0] ) {
		Q_strncpyz( buffer, authPart1, bufferSize );
	}

	if ( authPart2 && authPart2[0] ) {
		Q_strcat( buffer, bufferSize, authPart2 );
	}
}

static char *G_RunPlatformAuthChecks( int clientNum, char *userinfo, qboolean firstTime, qboolean isBot, gclient_t *client ) {
        ql_auth_credential_t credential;
        ql_auth_response_t response;
        char token[QL_AUTH_MAX_CREDENTIAL_STORAGE];
        const char *resultString;
        const char *outcomeString;

        if ( !firstTime || isBot || !userinfo || !client ) {
                G_WritePlatformAuthUserinfo( clientNum, userinfo, NULL, NULL, NULL );
                return NULL;
        }

        G_BuildSteamAuthToken( userinfo, token, sizeof( token ) );

        if ( !token[0] ) {
                G_WritePlatformAuthUserinfo( clientNum, userinfo, NULL, NULL, NULL );
                return NULL;
        }

        QL_InitAuthCredential( &credential );

        if ( !QL_ParsePlatformToken( token, QL_AUTH_CREDENTIAL_STEAM, &credential ) ) {
                Q_strncpyz( g_clientAuthDenyMessage, "Failed to verify Steam auth token", sizeof( g_clientAuthDenyMessage ) );
                G_LogPrintf( "SteamAuthRejected: %i %s\n", clientNum, g_clientAuthDenyMessage );
                G_WritePlatformAuthUserinfo( clientNum, userinfo, G_GetAuthResultString( QL_AUTH_RESULT_ERROR ), G_GetAuthOutcomeString( QL_AUTH_OUTCOME_FAILURE ), g_clientAuthDenyMessage );
                return g_clientAuthDenyMessage;
        }

        if ( !QL_RequestExternalAuth( &credential, &response ) || response.result != QL_AUTH_RESULT_ACCEPTED ) {
                const char *message = response.message[0] ? response.message : "Failed to verify Steam auth token";

                Q_strncpyz( g_clientAuthDenyMessage, message, sizeof( g_clientAuthDenyMessage ) );

                resultString = G_GetAuthResultString( response.result );
                outcomeString = G_GetAuthOutcomeString( response.outcome );

                if ( response.outcome == QL_AUTH_OUTCOME_RETRY ) {
                        G_LogPrintf( "SteamAuthRetry: %i %s\n", clientNum, g_clientAuthDenyMessage );
                } else {
                        G_LogPrintf( "SteamAuthRejected: %i %s\n", clientNum, g_clientAuthDenyMessage );
                }

                G_WritePlatformAuthUserinfo( clientNum, userinfo, resultString, outcomeString, g_clientAuthDenyMessage );
                return g_clientAuthDenyMessage;
        }

        resultString = G_GetAuthResultString( response.result );
        outcomeString = G_GetAuthOutcomeString( response.outcome );

        G_WritePlatformAuthUserinfo( clientNum, userinfo, resultString, outcomeString, response.message[0] ? response.message : NULL );

        if ( response.message[0] ) {
                G_LogPrintf( "SteamAuthAccepted: %i %s\n", clientNum, response.message );
        }

        return NULL;
}
#else
static char *G_RunPlatformAuthChecks( int clientNum, char *userinfo, qboolean firstTime, qboolean isBot, gclient_t *client ) {
        (void)clientNum;
        (void)userinfo;
        (void)firstTime;
        (void)isBot;
        (void)client;
	return NULL;
}
#endif

/*QUAKED info_player_deathmatch (1 0 1) (-16 -16 -24) (16 16 32) initial
potential spawning position for deathmatch games.
The first time a player enters the game, they will be at an 'initial' spot.
Targets will be fired when someone spawns in on them.
"nobots" will prevent bots from using this spot.
"nohumans" will prevent non-bots from using this spot.
*/
void SP_info_player_deathmatch( gentity_t *ent ) {
	int		i;

	G_SpawnInt( "nobots", "0", &i);
	if ( i ) {
		ent->flags |= FL_NO_BOTS;
	}
	G_SpawnInt( "nohumans", "0", &i );
	if ( i ) {
		ent->flags |= FL_NO_HUMANS;
	}
}

/*QUAKED info_player_start (1 0 0) (-16 -16 -24) (16 16 32)
equivelant to info_player_deathmatch
*/
void SP_info_player_start(gentity_t *ent) {
	ent->classname = "info_player_deathmatch";
	SP_info_player_deathmatch( ent );
}

/*QUAKED info_player_intermission (1 0 1) (-16 -16 -24) (16 16 32)
The intermission will be viewed from this point.  Target an info_notnull for the view direction.
*/
void SP_info_player_intermission( gentity_t *ent ) {

}



/*
=======================================================================

  SelectSpawnPoint

=======================================================================
*/

/*
================
SpotWouldTelefrag

================
*/
qboolean SpotWouldTelefrag( gentity_t *spot ) {
	int			i, num;
	int			touch[MAX_GENTITIES];
	gentity_t	*hit;
	vec3_t		mins, maxs;

	VectorAdd( spot->s.origin, playerMins, mins );
	VectorAdd( spot->s.origin, playerMaxs, maxs );
	num = trap_EntitiesInBox( mins, maxs, touch, MAX_GENTITIES );

	for (i=0 ; i<num ; i++) {
		hit = &g_entities[touch[i]];
		//if ( hit->client && hit->client->ps.stats[STAT_HEALTH] > 0 ) {
		if ( hit->client) {
			return qtrue;
		}

	}

	return qfalse;
}

/*
================
SelectNearestDeathmatchSpawnPoint

Find the spot that we DON'T want to use
================
*/
#define	MAX_SPAWN_POINTS	128
gentity_t *SelectNearestDeathmatchSpawnPoint( vec3_t from ) {
	gentity_t	*spot;
	vec3_t		delta;
	float		dist, nearestDist;
	gentity_t	*nearestSpot;

	nearestDist = 999999;
	nearestSpot = NULL;
	spot = NULL;

	while ((spot = G_Find (spot, FOFS(classname), "info_player_deathmatch")) != NULL) {

		VectorSubtract( spot->s.origin, from, delta );
		dist = VectorLength( delta );
		if ( dist < nearestDist ) {
			nearestDist = dist;
			nearestSpot = spot;
		}
	}

	return nearestSpot;
}


/*
================
SelectRandomDeathmatchSpawnPoint

go to a random point that doesn't telefrag
================
*/
#define	MAX_SPAWN_POINTS	128
gentity_t *SelectRandomDeathmatchSpawnPoint( void ) {
	gentity_t	*spot;
	int			count;
	int			selection;
	gentity_t	*spots[MAX_SPAWN_POINTS];

	count = 0;
	spot = NULL;

	while ((spot = G_Find (spot, FOFS(classname), "info_player_deathmatch")) != NULL) {
		if ( SpotWouldTelefrag( spot ) ) {
			continue;
		}
		spots[ count ] = spot;
		count++;
	}

	if ( !count ) {	// no spots that won't telefrag
		return G_Find( NULL, FOFS(classname), "info_player_deathmatch");
	}

	selection = rand() % count;
	return spots[ selection ];
}

/*
===========
SelectRandomFurthestSpawnPoint

Chooses a player start, deathmatch start, etc
============
*/
gentity_t *SelectRandomFurthestSpawnPoint ( vec3_t avoidPoint, vec3_t origin, vec3_t angles ) {
	gentity_t	*spot;
	vec3_t		delta;
	float		dist;
	float		list_dist[64];
	gentity_t	*list_spot[64];
	int			numSpots, rnd, i, j;

	numSpots = 0;
	spot = NULL;

	while ((spot = G_Find (spot, FOFS(classname), "info_player_deathmatch")) != NULL) {
		if ( SpotWouldTelefrag( spot ) ) {
			continue;
		}
		VectorSubtract( spot->s.origin, avoidPoint, delta );
		dist = VectorLength( delta );
		for (i = 0; i < numSpots; i++) {
			if ( dist > list_dist[i] ) {
				if ( numSpots >= 64 )
					numSpots = 64-1;
				for (j = numSpots; j > i; j--) {
					list_dist[j] = list_dist[j-1];
					list_spot[j] = list_spot[j-1];
				}
				list_dist[i] = dist;
				list_spot[i] = spot;
				numSpots++;
				if (numSpots > 64)
					numSpots = 64;
				break;
			}
		}
		if (i >= numSpots && numSpots < 64) {
			list_dist[numSpots] = dist;
			list_spot[numSpots] = spot;
			numSpots++;
		}
	}
	if (!numSpots) {
		spot = G_Find( NULL, FOFS(classname), "info_player_deathmatch");
		if (!spot)
			G_Error( "Couldn't find a spawn point" );
		VectorCopy (spot->s.origin, origin);
		origin[2] += 9;
		VectorCopy (spot->s.angles, angles);
		return spot;
	}

	// select a random spot from the spawn points furthest away
	rnd = random() * (numSpots / 2);

	VectorCopy (list_spot[rnd]->s.origin, origin);
	origin[2] += 9;
	VectorCopy (list_spot[rnd]->s.angles, angles);

	return list_spot[rnd];
}

/*
===========
SelectSpawnPoint

Chooses a player start, deathmatch start, etc
============
*/
gentity_t *SelectSpawnPoint ( vec3_t avoidPoint, vec3_t origin, vec3_t angles ) {
	return SelectRandomFurthestSpawnPoint( avoidPoint, origin, angles );

	/*
	gentity_t	*spot;
	gentity_t	*nearestSpot;

	nearestSpot = SelectNearestDeathmatchSpawnPoint( avoidPoint );

	spot = SelectRandomDeathmatchSpawnPoint ( );
	if ( spot == nearestSpot ) {
		// roll again if it would be real close to point of death
		spot = SelectRandomDeathmatchSpawnPoint ( );
		if ( spot == nearestSpot ) {
			// last try
			spot = SelectRandomDeathmatchSpawnPoint ( );
		}		
	}

	// find a single player start spot
	if (!spot) {
		G_Error( "Couldn't find a spawn point" );
	}

	VectorCopy (spot->s.origin, origin);
	origin[2] += 9;
	VectorCopy (spot->s.angles, angles);

	return spot;
	*/
}

/*
===========
SelectInitialSpawnPoint

Try to find a spawn point marked 'initial', otherwise
use normal spawn selection.
============
*/
gentity_t *SelectInitialSpawnPoint( vec3_t origin, vec3_t angles ) {
	gentity_t	*spot;

	spot = NULL;
	while ((spot = G_Find (spot, FOFS(classname), "info_player_deathmatch")) != NULL) {
		if ( spot->spawnflags & 1 ) {
			break;
		}
	}

	if ( !spot || SpotWouldTelefrag( spot ) ) {
		return SelectSpawnPoint( vec3_origin, origin, angles );
	}

	VectorCopy (spot->s.origin, origin);
	origin[2] += 9;
	VectorCopy (spot->s.angles, angles);

	return spot;
}

/*
===========
SelectSpectatorSpawnPoint

============
*/
gentity_t *SelectSpectatorSpawnPoint( vec3_t origin, vec3_t angles ) {
	FindIntermissionPoint();

	VectorCopy( level.intermission_origin, origin );
	VectorCopy( level.intermission_angle, angles );

	return NULL;
}

/*
=======================================================================

BODYQUE

=======================================================================
*/

/*
===============
InitBodyQue
===============
*/
void InitBodyQue (void) {
	int		i;
	gentity_t	*ent;

	level.bodyQueIndex = 0;
	for (i=0; i<BODY_QUEUE_SIZE ; i++) {
		ent = G_Spawn();
		ent->classname = "bodyque";
		ent->neverFree = qtrue;
		level.bodyQue[i] = ent;
	}
}

/*
=============
BodySink

After sitting around for five seconds, fall into the ground and dissapear
=============
*/
void BodySink( gentity_t *ent ) {
	if ( level.time - ent->timestamp > 6500 ) {
		// the body ques are never actually freed, they are just unlinked
		trap_UnlinkEntity( ent );
		ent->physicsObject = qfalse;
		return;	
	}
	ent->nextthink = level.time + 100;
	ent->s.pos.trBase[2] -= 1;
}

/*
=============
CopyToBodyQue

A player is respawning, so make an entity that looks
just like the existing corpse to leave behind.
=============
*/
void CopyToBodyQue( gentity_t *ent ) {
	gentity_t	*e;
	int i;
	gentity_t		*body;
	int			contents;

	trap_UnlinkEntity (ent);

	// if client is in a nodrop area, don't leave the body
	contents = trap_PointContents( ent->s.origin, -1 );
	if ( contents & CONTENTS_NODROP ) {
		return;
	}

	// grab a body que and cycle to the next one
	body = level.bodyQue[ level.bodyQueIndex ];
	level.bodyQueIndex = (level.bodyQueIndex + 1) % BODY_QUEUE_SIZE;

	trap_UnlinkEntity (body);

	body->s = ent->s;
	body->s.eFlags = EF_DEAD;		// clear EF_TALK, etc
	if ( ent->s.eFlags & EF_KAMIKAZE ) {
		body->s.eFlags |= EF_KAMIKAZE;

		// check if there is a kamikaze timer around for this owner
		for (i = 0; i < MAX_GENTITIES; i++) {
			e = &g_entities[i];
			if (!e->inuse)
				continue;
			if (e->activator != ent)
				continue;
			if (strcmp(e->classname, "kamikaze timer"))
				continue;
			e->activator = body;
			break;
		}
	}
	body->s.powerups = 0;	// clear powerups
	body->s.loopSound = 0;	// clear lava burning
	body->s.number = body - g_entities;
	body->timestamp = level.time;
	body->physicsObject = qtrue;
	body->physicsBounce = 0;		// don't bounce
	if ( body->s.groundEntityNum == ENTITYNUM_NONE ) {
		body->s.pos.trType = TR_GRAVITY;
		body->s.pos.trTime = level.time;
		VectorCopy( ent->client->ps.velocity, body->s.pos.trDelta );
	} else {
		body->s.pos.trType = TR_STATIONARY;
	}
	body->s.event = 0;

	// change the animation to the last-frame only, so the sequence
	// doesn't repeat anew for the body
	switch ( body->s.legsAnim & ~ANIM_TOGGLEBIT ) {
	case BOTH_DEATH1:
	case BOTH_DEAD1:
		body->s.torsoAnim = body->s.legsAnim = BOTH_DEAD1;
		break;
	case BOTH_DEATH2:
	case BOTH_DEAD2:
		body->s.torsoAnim = body->s.legsAnim = BOTH_DEAD2;
		break;
	case BOTH_DEATH3:
	case BOTH_DEAD3:
	default:
		body->s.torsoAnim = body->s.legsAnim = BOTH_DEAD3;
		break;
	}

	body->r.svFlags = ent->r.svFlags;
	VectorCopy (ent->r.mins, body->r.mins);
	VectorCopy (ent->r.maxs, body->r.maxs);
	VectorCopy (ent->r.absmin, body->r.absmin);
	VectorCopy (ent->r.absmax, body->r.absmax);

	body->clipmask = CONTENTS_SOLID | CONTENTS_PLAYERCLIP;
	body->r.contents = CONTENTS_CORPSE;
	body->r.ownerNum = ent->s.number;

	body->nextthink = level.time + 5000;
	body->think = BodySink;

	body->die = body_die;

	// don't take more damage if already gibbed
	if ( ent->health <= GIB_HEALTH ) {
		body->takedamage = qfalse;
	} else {
		body->takedamage = qtrue;
	}


	VectorCopy ( body->s.pos.trBase, body->r.currentOrigin );
	trap_LinkEntity (body);
}

//======================================================================


/*
==================
SetClientViewAngle

==================
*/
void SetClientViewAngle( gentity_t *ent, vec3_t angle ) {
	int			i;

	// set the delta angle
	for (i=0 ; i<3 ; i++) {
		int		cmdAngle;

		cmdAngle = ANGLE2SHORT(angle[i]);
		ent->client->ps.delta_angles[i] = cmdAngle - ent->client->pers.cmd.angles[i];
	}
	VectorCopy( angle, ent->s.angles );
	VectorCopy (ent->s.angles, ent->client->ps.viewangles);
}

/*
================
respawn
================
*/
void respawn( gentity_t *ent ) {
	gentity_t	*tent;
	qboolean	spawnedImmediately;
	qboolean	warmupSpawn;

	CopyToBodyQue( ent );
	warmupSpawn = ( level.warmupTime > 0 ) ? qtrue : qfalse;
	spawnedImmediately = G_RequestClientSpawn( ent, warmupSpawn, qfalse );

	if ( spawnedImmediately && ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		// add a teleportation effect
		tent = G_TempEntity( ent->client->ps.origin, EV_PLAYER_TELEPORT_IN );
		tent->s.clientNum = ent->s.clientNum;
	}
}

/*
================
TeamCount

Returns number of players on a team
================
*/
team_t TeamCount( int ignoreClientNum, int team ) {
	int		i;
	int		count = 0;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( i == ignoreClientNum ) {
			continue;
		}
		if ( level.clients[i].pers.connected == CON_DISCONNECTED ) {
			continue;
		}
		if ( level.clients[i].sess.sessionTeam == team ) {
			count++;
		}
	}

	return count;
}

/*
================
TeamLeader

Returns the client number of the team leader
================
*/
int TeamLeader( int team ) {
	int		i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].pers.connected == CON_DISCONNECTED ) {
			continue;
		}
		if ( level.clients[i].sess.sessionTeam == team ) {
			if ( level.clients[i].sess.teamLeader )
				return i;
		}
	}

	return -1;
}


/*
================
PickTeam

================
*/
team_t PickTeam( int ignoreClientNum ) {
	int		counts[TEAM_NUM_TEAMS];

	counts[TEAM_BLUE] = TeamCount( ignoreClientNum, TEAM_BLUE );
	counts[TEAM_RED] = TeamCount( ignoreClientNum, TEAM_RED );

	if ( counts[TEAM_BLUE] > counts[TEAM_RED] ) {
		return TEAM_RED;
	}
	if ( counts[TEAM_RED] > counts[TEAM_BLUE] ) {
		return TEAM_BLUE;
	}
	// equal team count, so join the team with the lowest score
	if ( level.teamScores[TEAM_BLUE] > level.teamScores[TEAM_RED] ) {
		return TEAM_RED;
	}
	return TEAM_BLUE;
}

/*
===========
ForceClientSkin

Forces a client's skin (for teamplay)
===========
*/
/*
static void ForceClientSkin( gclient_t *client, char *model, const char *skin ) {
	char *p;

	if ((p = Q_strrchr(model, '/')) != 0) {
		*p = 0;
	}

	Q_strcat(model, MAX_QPATH, "/");
	Q_strcat(model, MAX_QPATH, skin);
}
*/

/*
===========
ClientCheckName
============
*/
static void ClientCleanName( const char *in, char *out, int outSize ) {
	int		len, colorlessLen;
	char	ch;
	char	*p;
	int		spaces;

	//save room for trailing null byte
	outSize--;

	len = 0;
	colorlessLen = 0;
	p = out;
	*p = 0;
	spaces = 0;

	while( 1 ) {
		ch = *in++;
		if( !ch ) {
			break;
		}

		// don't allow leading spaces
		if( !*p && ch == ' ' ) {
			continue;
		}

		// check colors
		if( ch == Q_COLOR_ESCAPE ) {
			// solo trailing carat is not a color prefix
			if( !*in ) {
				break;
			}

			// don't allow black in a name, period
			if( ColorIndex(*in) == 0 ) {
				in++;
				continue;
			}

			// make sure room in dest for both chars
			if( len > outSize - 2 ) {
				break;
			}

			*out++ = ch;
			*out++ = *in++;
			len += 2;
			continue;
		}

		// don't allow too many consecutive spaces
		if( ch == ' ' ) {
			spaces++;
			if( spaces > 3 ) {
				continue;
			}
		}
		else {
			spaces = 0;
		}

		if( len > outSize - 1 ) {
			break;
		}

		*out++ = ch;
		colorlessLen++;
		len++;
	}
	*out = 0;

	// don't allow empty names
	if( *p == 0 || colorlessLen == 0 ) {
		Q_strncpyz( p, "UnnamedPlayer", outSize );
	}
}


/*
===========
ClientUserInfoChanged

Called from ClientConnect when the player first connects and
directly by the server system when the player updates a userinfo variable.

The game can override any of the settings and call trap_SetUserinfo
if desired.
============
*/
void ClientUserinfoChanged( int clientNum ) {
	gentity_t *ent;
	int		teamTask, teamLeader, team, health;
	char	*s;
	char	model[MAX_QPATH];
	char	headModel[MAX_QPATH];
	char	oldname[MAX_STRING_CHARS];
	gclient_t	*client;
	char	c1[MAX_INFO_STRING];
	char	c2[MAX_INFO_STRING];
	char	redTeam[MAX_INFO_STRING];
	char	blueTeam[MAX_INFO_STRING];
	char	userinfo[MAX_INFO_STRING];

	ent = g_entities + clientNum;
	client = ent->client;

	trap_GetUserinfo( clientNum, userinfo, sizeof( userinfo ) );

	// check for malformed or illegal info strings
	if ( !Info_Validate( userinfo ) ) {
		if ( g_kickBadUserinfo.integer ) {
			G_LogPrintf( "Dropping client %i for a deformed userinfo: %s\n", clientNum, userinfo );
			trap_DropClient( clientNum, "Bad userinfo" );
			return;
		}

		G_LogPrintf( "Found client %i with deformed userinfo, but cowardly refusing to kick: %s\n", clientNum, userinfo );
		trap_SendServerCommand( clientNum, "print \"WARNING: Invalid userinfo detected.\\n\"" );
		strcpy( userinfo, "\\name\\badinfo" );
	}

	G_LoadClientRatingMetadata( client, userinfo );
	G_RefreshClientRatingModifiers( client );

	// check for local client
	s = Info_ValueForKey( userinfo, "ip" );
	if ( !strcmp( s, "localhost" ) ) {
		client->pers.localClient = qtrue;
	}

	// check the item prediction
	s = Info_ValueForKey( userinfo, "cg_predictItems" );
	if ( !atoi( s ) ) {
		client->pers.predictItemPickup = qfalse;
	} else {
		client->pers.predictItemPickup = qtrue;
	}

	// set name
	Q_strncpyz ( oldname, client->pers.netname, sizeof( oldname ) );
	s = Info_ValueForKey (userinfo, "name");
	ClientCleanName( s, client->pers.netname, sizeof(client->pers.netname) );

	if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {
		if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ) {
			Q_strncpyz( client->pers.netname, "scoreboard", sizeof(client->pers.netname) );
		}
	}

	if ( client->pers.connected == CON_CONNECTED ) {
		if ( strcmp( oldname, client->pers.netname ) ) {
			trap_SendServerCommand( -1, va("print \"%s" S_COLOR_WHITE " renamed to %s\n\"", oldname, 
				client->pers.netname) );
		}
	}

	// set max health
	if (client->ps.powerups[PW_GUARD]) {
		client->pers.maxHealth = 200;
	} else {
		health = atoi( Info_ValueForKey( userinfo, "handicap" ) );
		client->pers.maxHealth = health;
		if ( client->pers.maxHealth < 1 || client->pers.maxHealth > 100 ) {
			client->pers.maxHealth = 100;
		}
	}
	client->ps.stats[STAT_MAX_HEALTH] = client->pers.maxHealth;

	// set model
	if( g_gametype.integer >= GT_TEAM ) {
		Q_strncpyz( model, Info_ValueForKey (userinfo, "team_model"), sizeof( model ) );
		Q_strncpyz( headModel, Info_ValueForKey (userinfo, "team_headmodel"), sizeof( headModel ) );
	} else {
		Q_strncpyz( model, Info_ValueForKey (userinfo, "model"), sizeof( model ) );
		Q_strncpyz( headModel, Info_ValueForKey (userinfo, "headmodel"), sizeof( headModel ) );
	}

	if ( g_playermodelOverride.string[0] || g_playerheadmodelOverride.string[0] ) {
		qboolean	userinfoModified = qfalse;
		qboolean	logModelOverride = qfalse;
		qboolean	logHeadOverride = qfalse;

		if ( g_playermodelOverride.string[0] ) {
			const char	*currentTeamModel;

			if ( Q_stricmp( model, g_playermodelOverride.string ) ) {
				logModelOverride = qtrue;
				userinfoModified = qtrue;
			}

			currentTeamModel = Info_ValueForKey( userinfo, "team_model" );
			if ( Q_stricmp( currentTeamModel, g_playermodelOverride.string ) ) {
				userinfoModified = qtrue;
			}

			Q_strncpyz( model, g_playermodelOverride.string, sizeof( model ) );
			Info_SetValueForKey( userinfo, "model", g_playermodelOverride.string );
			Info_SetValueForKey( userinfo, "team_model", g_playermodelOverride.string );
		}

		if ( g_playerheadmodelOverride.string[0] ) {
			const char	*currentTeamHeadModel;

			if ( Q_stricmp( headModel, g_playerheadmodelOverride.string ) ) {
				logHeadOverride = qtrue;
				userinfoModified = qtrue;
			}

			currentTeamHeadModel = Info_ValueForKey( userinfo, "team_headmodel" );
			if ( Q_stricmp( currentTeamHeadModel, g_playerheadmodelOverride.string ) ) {
				userinfoModified = qtrue;
			}

			Q_strncpyz( headModel, g_playerheadmodelOverride.string, sizeof( headModel ) );
			Info_SetValueForKey( userinfo, "headmodel", g_playerheadmodelOverride.string );
			Info_SetValueForKey( userinfo, "team_headmodel", g_playerheadmodelOverride.string );
		}

		if ( userinfoModified ) {
			trap_SetUserinfo( clientNum, userinfo );
			if ( logModelOverride ) {
				G_LogPrintf( "g_playermodelOverride enforced for client %i (%s): %s\n", clientNum, client->pers.netname, g_playermodelOverride.string );
			}
			if ( logHeadOverride ) {
				G_LogPrintf( "g_playerheadmodelOverride enforced for client %i (%s): %s\n", clientNum, client->pers.netname, g_playerheadmodelOverride.string );
			}
		}
	}

	// bots set their team a few frames later
	if (g_gametype.integer >= GT_TEAM && g_entities[clientNum].r.svFlags & SVF_BOT) {
		s = Info_ValueForKey( userinfo, "team" );
		if ( !Q_stricmp( s, "red" ) || !Q_stricmp( s, "r" ) ) {
			team = TEAM_RED;
		} else if ( !Q_stricmp( s, "blue" ) || !Q_stricmp( s, "b" ) ) {
			team = TEAM_BLUE;
		} else {
			// pick the team with the least number of players
			team = PickTeam( clientNum );
		}
	}
	else {
		team = client->sess.sessionTeam;
	}

/*	NOTE: all client side now

	// team
	switch( team ) {
	case TEAM_RED:
		ForceClientSkin(client, model, "red");
//		ForceClientSkin(client, headModel, "red");
		break;
	case TEAM_BLUE:
		ForceClientSkin(client, model, "blue");
//		ForceClientSkin(client, headModel, "blue");
		break;
	}
	// don't ever use a default skin in teamplay, it would just waste memory
	// however bots will always join a team but they spawn in as spectator
	if ( g_gametype.integer >= GT_TEAM && team == TEAM_SPECTATOR) {
		ForceClientSkin(client, model, "red");
//		ForceClientSkin(client, headModel, "red");
	}
*/

	if (g_gametype.integer >= GT_TEAM) {
		client->pers.teamInfo = qtrue;
	} else {
		s = Info_ValueForKey( userinfo, "teamoverlay" );
		if ( ! *s || atoi( s ) != 0 ) {
			client->pers.teamInfo = qtrue;
		} else {
			client->pers.teamInfo = qfalse;
		}
	}
	/*
	s = Info_ValueForKey( userinfo, "cg_pmove_fixed" );
	if ( !*s || atoi( s ) == 0 ) {
		client->pers.pmoveFixed = qfalse;
	}
	else {
		client->pers.pmoveFixed = qtrue;
	}
	*/

	// team task (0 = none, 1 = offence, 2 = defence)
	teamTask = atoi(Info_ValueForKey(userinfo, "teamtask"));
	// team Leader (1 = leader, 0 is normal player)
	teamLeader = client->sess.teamLeader;

	// colors
	strcpy(c1, Info_ValueForKey( userinfo, "color1" ));
	strcpy(c2, Info_ValueForKey( userinfo, "color2" ));

	strcpy(redTeam, Info_ValueForKey( userinfo, "g_redteam" ));
	strcpy(blueTeam, Info_ValueForKey( userinfo, "g_blueteam" ));

	// send over a subset of the userinfo keys so other clients can
	// print scoreboards, display models, and play custom sounds
	if ( ent->r.svFlags & SVF_BOT ) {
		s = va("n\\%s\\t\\%i\\model\\%s\\hmodel\\%s\\c1\\%s\\c2\\%s\\hc\\%i\\w\\%i\\l\\%i\\skill\\%s\\tt\\%d\\tl\\%d",
			client->pers.netname, team, model, headModel, c1, c2, 
			client->pers.maxHealth, client->sess.wins, client->sess.losses,
			Info_ValueForKey( userinfo, "skill" ), teamTask, teamLeader );
	} else {
		s = va("n\\%s\\t\\%i\\model\\%s\\hmodel\\%s\\g_redteam\\%s\\g_blueteam\\%s\\c1\\%s\\c2\\%s\\hc\\%i\\w\\%i\\l\\%i\\tt\\%d\\tl\\%d",
			client->pers.netname, client->sess.sessionTeam, model, headModel, redTeam, blueTeam, c1, c2, 
			client->pers.maxHealth, client->sess.wins, client->sess.losses, teamTask, teamLeader);
	}

	trap_SetConfigstring( CS_PLAYERS+clientNum, s );

	// this is not the userinfo, more like the configstring actually
	G_LogPrintf( "ClientUserinfoChanged: %i %s\n", clientNum, s );
}


/*
===========
ClientConnect

Called when a player begins connecting to the server.
Called again for every map change or tournement restart.

The session information will be valid after exit.

Return NULL if the client should be allowed, otherwise return
a string with the reason for denial.

Otherwise, the client will be sent the current gamestate
and will eventually get to ClientBegin.

firstTime will be qtrue the very first time a client connects
to the server machine, but qfalse on map changes and tournement
restarts.
============
*/
char *ClientConnect( int clientNum, qboolean firstTime, qboolean isBot ) {
	char		*value;
//	char		*areabits;
	gclient_t	*client;
	char		userinfo[MAX_INFO_STRING];
	gentity_t	*ent;

	ent = &g_entities[ clientNum ];
	ent->r.svFlags &= ~SVF_BOT;

	trap_GetUserinfo( clientNum, userinfo, sizeof( userinfo ) );

 	// IP filtering
 	// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=500
 	// recommanding PB based IP / GUID banning, the builtin system is pretty limited
 	// check to see if they are on the banned IP list
	value = Info_ValueForKey (userinfo, "ip");
	if ( G_FilterPacket( value ) ) {
		return "You are banned from this server.";
	}

  // we don't check password for bots and local client
  // NOTE: local client <-> "ip" "localhost"
  //   this means this client is not running in our current process
	if ( !( ent->r.svFlags & SVF_BOT ) && (strcmp(value, "localhost") != 0)) {
		// check for a password
		value = Info_ValueForKey (userinfo, "password");
		if ( g_password.string[0] && Q_stricmp( g_password.string, "none" ) &&
			strcmp( g_password.string, value) != 0) {
			return "Invalid password";
		}
	}

	// they can connect
	ent->client = level.clients + clientNum;
	client = ent->client;

//	areabits = client->areabits;

	memset( client, 0, sizeof(*client) );

	client->pers.connected = CON_CONNECTING;
	client->pers.killCommandTime = -1;
	client->pers.ratingDamageScale = 1.0f;
	client->pers.ratingScoreScale = 1.0f;
	client->pers.ratingMetadataLoaded = qfalse;
	client->pers.itemProgressionTier = ( g_training.integer != 0 ) ? 0 : ITEM_UNLOCK_TIER_NONE;
	client->pers.progressionFlags = 0;
	G_InitClientVoteThrottle( client );

	// read or initialize the session data
	if ( firstTime || level.newSession ) {
		G_InitSessionData( client, userinfo );
	}
	G_ReadSessionData( client );

	{
		char *authFailure = G_RunPlatformAuthChecks( clientNum, userinfo, firstTime, isBot, client );

		if ( authFailure ) {
			return authFailure;
		}
	}

	if( isBot ) {
		ent->r.svFlags |= SVF_BOT;
		ent->inuse = qtrue;
		if( !G_BotConnect( clientNum, !firstTime ) ) {
			return "BotConnectfailed";
		}
	}

	// get and distribute relevent paramters
	G_LogPrintf( "ClientConnect: %i\n", clientNum );
	G_LogPrintf( "ClientMask: %i %s\n", clientNum, ( ent->r.svFlags & SVF_BOT ) ? "bot" : "human" );
	ClientUserinfoChanged( clientNum );

	// don't do the "xxx connected" messages if they were caried over from previous level
	if ( firstTime ) {
		if ( level.time > 5000 ) {
			trap_SendServerCommand( -1, va("print \"%s" S_COLOR_WHITE " connected\n\"", client->pers.netname) );
		}
		// TODO: investigate whether Quake Live's native code sends an additional "priv" handshake
		// message here (sub_1003af1b). The HLIL dump suggests the engine verifies private-client
		// access immediately after the bot/auth checks.
	}

        if ( !isBot ) {
                const char *steamId = Info_ValueForKey( userinfo, "steamid" );

                if ( steamId && steamId[0] ) {

#if (QL_PLATFORM_HAS_STEAMWORKS || QL_PLATFORM_HAS_OPEN_STEAM)

// g_client.c -- client functions that don't happen every frame

static vec3_t	playerMins = {-15, -15, -24};
static vec3_t	playerMaxs = {15, 15, 32};

/*
=============
G_FreezeHelperHasLineOfSight

Ensures thaw credit can pass between a frozen client and a helper.
=============
*/
static qboolean G_FreezeHelperHasLineOfSight( gentity_t *ent, gentity_t *helper ) {
	trace_t		trace;
	vec3_t		start;
	vec3_t		end;

	VectorCopy( helper->r.currentOrigin, start );
	VectorCopy( ent->r.currentOrigin, end );
	if ( helper->client ) {
		start[2] += helper->client->ps.viewheight * 0.5f;
	}
	if ( ent->client ) {
		end[2] += ent->client->ps.viewheight * 0.5f;
	}

	trap_Trace( &trace, start, NULL, NULL, end, helper->s.number, MASK_SOLID );
	if ( trace.fraction < 1.0f && trace.entityNum != ent->s.number ) {
		return qfalse;
	}

	trap_Trace( &trace, end, NULL, NULL, start, ent->s.number, MASK_SOLID );
	if ( trace.fraction < 1.0f && trace.entityNum != helper->s.number ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_FreezeCountThawHelpers

Counts allies able to thaw the specified client and returns the primary helper.
=============
*/
static int G_FreezeCountThawHelpers( gentity_t *ent, gentity_t **primaryHelper ) {
	float		radius;
	float		radiusSq;
	int		clientNum;
	int		count;

	if ( primaryHelper ) {
		*primaryHelper = NULL;
	}
	if ( !ent || !ent->client ) {
		return 0;
	}

	radius = (float)level.freezeConfig.thawRadius;
	if ( radius <= 0.0f ) {
		return 0;
	}
	radiusSq = radius * radius;
	count = 0;

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*helper;
		vec3_t		delta;

		helper = &g_entities[clientNum];
		if ( helper == ent || !helper->inuse || !helper->client ) {
			continue;
		}
		if ( helper->client->sess.sessionTeam != ent->client->sess.sessionTeam ) {
			continue;
		}
		if ( helper->client->sess.sessionTeam != TEAM_RED
		&& helper->client->sess.sessionTeam != TEAM_BLUE ) {
			continue;
		}
		if ( helper->client->freezeFrozen ) {
			continue;
		}
		if ( helper->client->ps.pm_type == PM_DEAD ) {
			continue;
		}

		VectorSubtract( helper->r.currentOrigin, ent->r.currentOrigin, delta );
		if ( VectorLengthSquared( delta ) > radiusSq ) {
			continue;
		}

		if ( !level.freezeConfig.thawThroughSurface && !G_FreezeHelperHasLineOfSight( ent, helper ) ) {
			continue;
		}

		count++;
		if ( primaryHelper && !*primaryHelper ) {
			*primaryHelper = helper;
		}
	}

	return count;
}

/*
=============
G_FreezeInitClient

Clears the per-client freeze fields whenever a player spawns.
=============
*/
void G_FreezeInitClient( gentity_t *ent ) {
	gclient_t	*client;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;
	client->freezeFrozen = qfalse;
	client->freezeTime = 0;
	client->freezeNextThawTick = 0;
	client->freezeAccumulatedThaw = 0;
	client->freezeAutoThawTime = 0;
	client->freezeProtectedUntil = 0;
	client->freezeEnvironmentalRespawnTime = 0;
	client->freezeLastHelper = -1;
	if ( G_FreezeGametypeEnabled() && level.freezeConfig.protectedSpawnTime > 0 ) {
		client->freezeProtectedUntil = level.time + level.freezeConfig.protectedSpawnTime;
	}
}

/*
=============
G_FreezeApplyFreezeState

Transitions the victim into the frozen state rather than allowing death.
=============
*/
static void G_FreezeApplyFreezeState( gentity_t *self, qboolean environmental ) {
	gclient_t	*client;
	int		thawTick;

	if ( !self || !self->client ) {
		return;
	}

	client = self->client;
	client->freezeFrozen = qtrue;
	client->freezeTime = level.time;
	client->freezeAccumulatedThaw = 0;
	thawTick = level.freezeConfig.thawTick;
	if ( thawTick <= 0 ) {
		thawTick = level.freezeConfig.thawTime;
	}
	if ( thawTick <= 0 ) {
		thawTick = 100;
	}
	client->freezeNextThawTick = level.time + thawTick;
	client->freezeAutoThawTime = ( level.freezeConfig.autoThawTime > 0 )
		? level.time + level.freezeConfig.autoThawTime : 0;
	if ( environmental && level.freezeConfig.environmentalRespawnDelay > 0 ) {
		client->freezeEnvironmentalRespawnTime = level.time + level.freezeConfig.environmentalRespawnDelay;
	} else {
		client->freezeEnvironmentalRespawnTime = 0;
	}
	client->freezeProtectedUntil = 0;
	client->freezeLastHelper = -1;
	self->takedamage = qfalse;
	client->ps.pm_type = PM_FREEZE;
	client->ps.pm_flags |= PMF_TIME_KNOCKBACK;
	client->ps.pm_time = 0;
	VectorClear( client->ps.velocity );
	self->health = 1;
	client->ps.stats[STAT_HEALTH] = 1;
	client->respawnTime = INT_MAX;
	self->r.contents = CONTENTS_BODY;
	trap_LinkEntity( self );
}

/*
=============
G_FreezeThawClient

Restores a frozen player to the active state.
=============
*/
void G_FreezeThawClient( gentity_t *ent, qboolean wasAuto, int helperNum ) {
	gclient_t	*client;

	(void)wasAuto;
	(void)helperNum;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;
	client->freezeFrozen = qfalse;
	client->freezeTime = 0;
	client->freezeAccumulatedThaw = 0;
	client->freezeNextThawTick = 0;
	client->freezeAutoThawTime = 0;
	client->freezeEnvironmentalRespawnTime = 0;
	client->freezeLastHelper = -1;
	client->ps.pm_type = PM_NORMAL;
	ent->takedamage = qtrue;
	if ( level.freezeConfig.resetHealth ) {
		ent->health = client->ps.stats[STAT_MAX_HEALTH];
		client->ps.stats[STAT_HEALTH] = ent->health;
	}
	if ( level.freezeConfig.resetArmor ) {
		client->ps.stats[STAT_ARMOR] = g_factoryCvarConfig.startingArmor;
	}
	if ( level.freezeConfig.removePowerups ) {
		memset( client->ps.powerups, 0, sizeof( client->ps.powerups ) );
	}
	if ( level.freezeConfig.protectedSpawnTime > 0 ) {
		client->freezeProtectedUntil = level.time + level.freezeConfig.protectedSpawnTime;
	} else {
		client->freezeProtectedUntil = 0;
	}
	client->respawnTime = level.time;
	trap_LinkEntity( ent );
}

#if (QL_PLATFORM_HAS_STEAMWORKS || QL_PLATFORM_HAS_OPEN_STEAM)
static char g_clientAuthDenyMessage[QL_AUTH_MAX_RESPONSE_MESSAGE + 64];

static const char *G_GetAuthResultString( qlAuthResult result ) {
        switch ( result ) {
        case QL_AUTH_RESULT_PENDING:
                return "pending";
        case QL_AUTH_RESULT_ACCEPTED:
                return "accepted";
        case QL_AUTH_RESULT_DENIED:
                return "denied";
        case QL_AUTH_RESULT_ERROR:
                return "error";
        default:
                break;
        }

        return "unknown";
}
#if (QL_PLATFORM_HAS_STEAMWORKS || QL_PLATFORM_HAS_OPEN_STEAM)
                        unsigned long long parsedId;

                        if ( G_ParseSteamId( steamId, &parsedId ) ) {
                                trap_Printf( va( "%s connected with Steam ID %llu\n", client->pers.netname, parsedId ) );
                        } else {
                                trap_Printf( va( "%s connected with Steam ID %s\n", client->pers.netname, steamId ) );
                        }
#else
                        trap_Printf( va( "%s connected with Steam ID %s\n", client->pers.netname, steamId ) );
#endif
                }
        }

	if ( g_gametype.integer >= GT_TEAM &&
		client->sess.sessionTeam != TEAM_SPECTATOR ) {
		BroadcastTeamChange( client, -1 );
	}

	// count current clients and rank for scoreboard
	G_SendItemTimerState( clientNum, g_itemTimers.integer ? 1 : 0, g_itemHeight.integer );
	CalculateRanks();

	if ( !( ent->r.svFlags & SVF_BOT ) ) {
		char		autoDetail[MAX_INFO_STRING];
		const char		*ipInfo;

		ipInfo = Info_ValueForKey( userinfo, "ip" );
		Q_strncpyz( autoDetail, ipInfo ? ipInfo : "", sizeof( autoDetail ) );
		G_AutoAction( AUTOACTION_PLAYER_CONNECT, ent, autoDetail );
	}

	// for statistics
//	client->areabits = areabits;
//	if ( !client->areabits )
//		client->areabits = G_Alloc( (trap_AAS_PointReachabilityAreaIndex( NULL ) + 7) / 8 );

	if ( !firstTime && client->sess.sessionTeam == TEAM_SPECTATOR ) {
		client->ps.eFlags |= EF_TELEPORT_BIT;
	}

	return NULL;
}

/*
===========
ClientBegin

called when a client has finished connecting, and is ready
to be placed into the level.  This will happen every level load,
and on transition between teams, but doesn't happen on respawns
============
*/
void ClientBegin( int clientNum ) {
	gentity_t	*ent;
	gclient_t	*client;
	gentity_t	*tent;
	int			flags;
	qboolean	spawnedImmediately;
	qboolean	warmupSpawn;

	ent = g_entities + clientNum;

	client = level.clients + clientNum;

	G_ComplaintResetClient( client, qtrue );

	if ( ent->r.linked ) {
		trap_UnlinkEntity( ent );
	}
	G_InitGentity( ent );
	ent->touch = 0;
	ent->pain = 0;
	ent->client = client;

	client->pers.connected = CON_CONNECTED;
	client->pers.enterTime = level.time;
	client->pers.teamState.state = TEAM_BEGIN;

	client->lastKillCommandTime = 0;
	client->killCommandCooldownExpires = 0;
	client->friendlyFireComplaints = 0;
	client->friendlyFireComplaintEndTime = 0;
	client->teammateDamageGiven = 0;
	client->teammateDamageThisLife = 0;

	// save eflags around this, because changing teams will
	// cause this to happen with a valid entity, and we
	// want to make sure the teleport bit is set right
	// so the viewpoint doesn't interpolate through the
	// world to the new position
	flags = client->ps.eFlags;
	memset( &client->ps, 0, sizeof( client->ps ) );
	client->ps.eFlags = flags;

	// locate ent at a spawn point
	warmupSpawn = ( level.warmupTime > 0 ) ? qtrue : qfalse;
	spawnedImmediately = G_RequestClientSpawn( ent, warmupSpawn, qtrue );

	if ( spawnedImmediately && client->sess.sessionTeam != TEAM_SPECTATOR ) {
		// send event
		tent = G_TempEntity( ent->client->ps.origin, EV_PLAYER_TELEPORT_IN );
		tent->s.clientNum = ent->s.clientNum;

		if ( g_gametype.integer != GT_TOURNAMENT  ) {
			trap_SendServerCommand( -1, va("print \"%s" S_COLOR_WHITE " entered the game\n\"", client->pers.netname) );
		}
	}
	G_LogPrintf( "ClientBegin: %i\n", clientNum );

	G_GametypeClientBegin( ent );

	// count current clients and rank for scoreboard
	G_SendItemTimerState( clientNum, g_itemTimers.integer ? 1 : 0, g_itemHeight.integer );
	CalculateRanks();

	// Check g_motd
	if ( g_motd.string[0] ) {
		trap_SendServerCommand( clientNum, va("cp \"%s\"", g_motd.string ) );
	}

	// Check g_teamAutoJoin
	if ( g_teamAutoJoin.integer && ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		SetTeam( ent, "auto" );
	}
}

/*
==============================
G_SeedConfiguredSpawnAmmo

Consolidate g_startingAmmo_* lookups so every spawn loadout path
(g_startingWeapons, factories, scripted grants) applies the same
clamps and "infinite" semantics.
==============================
*/
static void G_SeedConfiguredSpawnAmmo( playerState_t *ps, weapon_t weapon, int configuredAmmo ) {
	if ( !ps || weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return;
	}

	if ( g_factoryCvarConfig.infiniteAmmo || configuredAmmo < 0 ) {
		ps->ammo[weapon] = -1;
		return;
	}

	ps->ammo[weapon] = configuredAmmo;
}

/*
=============
G_RunGrantScript

Shared grant parser used by duel and the spawn CVar helper.
=============
*/
void G_RunGrantScript( gentity_t *ent, const char *script ) {
	char		grantBuffer[MAX_CVAR_VALUE_STRING];
	char		grantToken[MAX_TOKEN_CHARS];
	const char		*cursor;
	int		tokenLength;

	if ( !ent || !ent->client || !script || !script[0] ) {
		return;
	}

	Q_strncpyz( grantBuffer, script, sizeof( grantBuffer ) );
	cursor = grantBuffer;

	while ( *cursor ) {
		while ( *cursor && ( *cursor <= ' ' || *cursor == ',' || *cursor == ';' ) ) {
			++cursor;
		}

		if ( !*cursor ) {
			break;
		}

		tokenLength = 0;
		while ( *cursor && *cursor != ',' && *cursor != ';' && *cursor > ' ' ) {
			if ( tokenLength < (int)sizeof( grantToken ) - 1 ) {
				grantToken[tokenLength++] = *cursor;
			}
			++cursor;
		}
		grantToken[tokenLength] = '\\0';

		if ( grantToken[0] ) {
			G_GiveItemByName( ent, grantToken );
		}
	}
}

/*
=============
G_GrantConfiguredItems

Parses g_grantItemOnSpawn and grants the requested `give` tokens at spawn time.
=============
*/
static void G_GrantConfiguredItems( gentity_t *ent ) {
	G_RunGrantScript( ent, g_grantItemOnSpawn.string );
}

/*
============
G_SelectFactorySpawnWeapon

Chooses an initial weapon based on the configured factory stat mask.
============
*/
static weapon_t G_SelectFactorySpawnWeapon( unsigned int statMask ) {
	weapon_t weapon;

	if ( statMask & ( 1u << WP_MACHINEGUN ) ) {
		return WP_MACHINEGUN;
	}

	for ( weapon = WP_NUM_WEAPONS - 1; weapon > WP_NONE; --weapon ) {
		if ( weapon == WP_MACHINEGUN ) {
			continue;
		}

		if ( statMask & ( 1u << weapon ) ) {
			return weapon;
		}
	}

	if ( statMask & ( 1u << WP_GAUNTLET ) ) {
		return WP_GAUNTLET;
	}

	return WP_MACHINEGUN;
}

/*
===========
ClientSpawn

Called every time a client is placed fresh in the world:
after the first ClientBegin, and after each respawn
Initializes all non-persistant parts of playerState
============
*/
/*
=============
ClientSpawn

Handles player respawns, seeding stats, inventory, and spawn state from the cached factory configuration.
=============
*/
void ClientSpawn(gentity_t *ent) {
	int		index;
	vec3_t	spawn_origin, spawn_angles;
	gclient_t	*client;
	int		i;
	weapon_t	spawnWeapon;
	clientPersistant_t	saved;
	clientSession_t		savedSess;
	int		persistant[MAX_PERSISTANT];
	gentity_t	*spawnPoint;
	int		flags;
	int		savedPing;
	int		savedLastKillCommandTime;
	int		savedKillCommandCooldownExpires;
	int		savedFriendlyFireComplaints;
	int		savedFriendlyFireComplaintEndTime;
	int		savedTeammateDamageGiven;
//	char	*savedAreaBits;
	int		accuracy_hits, accuracy_shots;
	int		eventSequence;
	char	userinfo[MAX_INFO_STRING];
	const factoryCvarConfig_t	*factoryConfig;
	int		baseHealth;
	int		spawnHealth;

	index = ent - g_entities;
	client = ent->client;
	ent->keyMask = 0;
	factoryConfig = &g_factoryCvarConfig;
	level.clientFactoryLoadoutQueued[index] = qfalse;

	if ( g_teamSpawnAsSpec.integer && g_gametype.integer >= GT_TEAM && client->sess.sessionTeam != TEAM_SPECTATOR ) {
		client->sess.sessionTeam = TEAM_SPECTATOR;
		client->sess.spectatorState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;
		client->sess.spectatorClient = -1;
	}

	if ( client->sess.sessionTeam == TEAM_SPECTATOR && !g_teamSpecFreeCam.integer
		&& client->sess.spectatorState == SPECTATOR_FREE ) {
		client->sess.spectatorState = SPECTATOR_SCOREBOARD;
	}

	// find a spawn point
	// do it before setting health back up, so farthest
	// ranging doesn't count this client
	if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {
		spawnPoint = SelectSpectatorSpawnPoint ( 
						spawn_origin, spawn_angles);
	} else if (g_gametype.integer >= GT_CTF ) {
		// all base oriented team games use the CTF spawn points
		spawnPoint = SelectCTFSpawnPoint ( 
						client->sess.sessionTeam, 
						client->pers.teamState.state, 
						spawn_origin, spawn_angles);
	} else {
		do {
			// the first spawn should be at a good looking spot
			if ( !client->pers.initialSpawn && client->pers.localClient ) {
				client->pers.initialSpawn = qtrue;
				spawnPoint = SelectInitialSpawnPoint( spawn_origin, spawn_angles );
			} else {
				// don't spawn near existing origin if possible
				spawnPoint = SelectSpawnPoint ( 
					client->ps.origin, 
					spawn_origin, spawn_angles);
			}

			// Tim needs to prevent bots from spawning at the initial point
			// on q3dm0...
			if ( ( spawnPoint->flags & FL_NO_BOTS ) && ( ent->r.svFlags & SVF_BOT ) ) {
				continue;	// try again
			}
			// just to be symetric, we have a nohumans option...
			if ( ( spawnPoint->flags & FL_NO_HUMANS ) && !( ent->r.svFlags & SVF_BOT ) ) {
				continue;	// try again
			}

			break;

		} while ( 1 );
	}
	client->pers.teamState.state = TEAM_ACTIVE;

	// always clear the kamikaze flag
	ent->s.eFlags &= ~EF_KAMIKAZE;

	// toggle the teleport bit so the client knows to not lerp
	// and never clear the voted flag
	flags = ent->client->ps.eFlags & (EF_TELEPORT_BIT | EF_VOTED | EF_TEAMVOTED);
	flags ^= EF_TELEPORT_BIT;

	// clear everything but the persistant data

	saved = client->pers;
	savedSess = client->sess;
	savedPing = client->ps.ping;
	savedLastKillCommandTime = client->lastKillCommandTime;
	savedKillCommandCooldownExpires = client->killCommandCooldownExpires;
	savedFriendlyFireComplaints = client->friendlyFireComplaints;
	savedFriendlyFireComplaintEndTime = client->friendlyFireComplaintEndTime;
	savedTeammateDamageGiven = client->teammateDamageGiven;
//	savedAreaBits = client->areabits;
	accuracy_hits = client->accuracy_hits;
	accuracy_shots = client->accuracy_shots;
	for ( i = 0 ; i < MAX_PERSISTANT ; i++ ) {
		persistant[i] = client->ps.persistant[i];
	}
	eventSequence = client->ps.eventSequence;

	memset (client, 0, sizeof(*client)); // bk FIXME: Com_Memset?

	client->pers = saved;
	client->sess = savedSess;
	client->ps.ping = savedPing;
//	client->areabits = savedAreaBits;
	client->accuracy_hits = accuracy_hits;
	client->accuracy_shots = accuracy_shots;
	client->lastkilled_client = -1;
	client->lastKillCommandTime = savedLastKillCommandTime;
	client->killCommandCooldownExpires = savedKillCommandCooldownExpires;
	client->friendlyFireComplaints = savedFriendlyFireComplaints;
	client->friendlyFireComplaintEndTime = savedFriendlyFireComplaintEndTime;
	client->teammateDamageGiven = savedTeammateDamageGiven;
	client->teammateDamageThisLife = 0;

	for ( i = 0 ; i < MAX_PERSISTANT ; i++ ) {
		client->ps.persistant[i] = persistant[i];
	}
	client->ps.eventSequence = eventSequence;
	// increment the spawncount so the client will detect the respawn
	client->ps.persistant[PERS_SPAWN_COUNT]++;
	client->ps.persistant[PERS_TEAM] = client->sess.sessionTeam;
	G_FreezeInitClient( ent );

	// set spawn protection time
	if ( g_spawnProtect.integer > 0 && client->sess.sessionTeam != TEAM_SPECTATOR ) {
		client->invulnerabilityTime = level.time + g_spawnProtect.integer;
	} else {
		client->invulnerabilityTime = 0;
	}

	client->airOutTime = level.time + 12000;

	trap_GetUserinfo( index, userinfo, sizeof(userinfo) );
	// set max health
	if ( g_startingHealth.integer > 0 ) {
		baseHealth = g_startingHealth.integer;
	} else {
		baseHealth = factoryConfig->startingHealth;
	}
	if ( baseHealth < 1 ) {
		baseHealth = 1;
	}
	client->pers.maxHealth = atoi( Info_ValueForKey( userinfo, "handicap" ) );
	if ( client->pers.maxHealth < 1 ) {
		client->pers.maxHealth = baseHealth;
	} else if ( client->pers.maxHealth > baseHealth ) {
		client->pers.maxHealth = baseHealth;
	}
	// clear entity values
	client->ps.stats[STAT_MAX_HEALTH] = client->pers.maxHealth;
	client->ps.eFlags = flags;

	G_RefreshClientRatingModifiers( client );

	ent->s.groundEntityNum = ENTITYNUM_NONE;
	ent->client = &level.clients[index];
	ent->takedamage = qtrue;
	ent->inuse = qtrue;
	ent->classname = "player";
	ent->r.contents = CONTENTS_BODY;
	ent->clipmask = MASK_PLAYERSOLID;
	ent->die = player_die;
	ent->waterlevel = 0;
	ent->watertype = 0;
	ent->flags = 0;
	
	VectorCopy (playerMins, ent->r.mins);
	VectorCopy (playerMaxs, ent->r.maxs);

	client->ps.clientNum = index;

	{
		unsigned int startingMask;

		if ( g_startingWeapons.integer > 0 ) {
			startingMask = g_startingWeapons.integer;
		} else {
			startingMask = g_factoryCvarConfig.startingWeaponsStatMask;
		}

		weapon_t weapon;
		const int startingAmmoTable[WP_NUM_WEAPONS] = {
			[WP_NONE] = 0,
			[WP_GAUNTLET] = g_startingAmmoConfig.gauntlet,
			[WP_MACHINEGUN] = g_startingAmmoConfig.machinegun,
			[WP_SHOTGUN] = g_startingAmmoConfig.shotgun,
			[WP_GRENADE_LAUNCHER] = g_startingAmmoConfig.grenadeLauncher,
			[WP_ROCKET_LAUNCHER] = g_startingAmmoConfig.rocketLauncher,
			[WP_LIGHTNING] = g_startingAmmoConfig.lightningGun,
			[WP_RAILGUN] = g_startingAmmoConfig.railgun,
			[WP_PLASMAGUN] = g_startingAmmoConfig.plasmagun,
			[WP_BFG] = g_startingAmmoConfig.bfg,
			[WP_GRAPPLING_HOOK] = g_startingAmmoConfig.grapplingHook,
			[WP_NAILGUN] = g_startingAmmoConfig.nailgun,
			[WP_PROX_LAUNCHER] = g_startingAmmoConfig.proximityLauncher,
			[WP_CHAINGUN] = g_startingAmmoConfig.chaingun,
			[WP_HEAVY_MACHINEGUN] = g_startingAmmoConfig.heavyMachinegun,
		};

		if ( startingMask == 0 ) {
			startingMask = ( 1u << WP_MACHINEGUN ) | ( 1u << WP_GAUNTLET );
		}

		client->ps.stats[STAT_WEAPONS] = startingMask;

		for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; ++weapon ) {
			if ( startingMask & ( 1u << weapon ) ) {
				G_SeedConfiguredSpawnAmmo( &client->ps, weapon, startingAmmoTable[weapon] );
			}
		}

		spawnWeapon = G_SelectFactorySpawnWeapon( startingMask );
	}

	// health will count down towards max_health
	spawnHealth = client->ps.stats[STAT_MAX_HEALTH] + factoryConfig->startingHealthBonus;
	if ( spawnHealth < 1 ) {
		spawnHealth = 1;
	}
	ent->health = client->ps.stats[STAT_HEALTH] = spawnHealth;

	if ( g_startingArmor.integer > 0 ) {
		client->ps.stats[STAT_ARMOR] = g_startingArmor.integer;
	} else if ( factoryConfig->startingArmor > 0 ) {
		client->ps.stats[STAT_ARMOR] = factoryConfig->startingArmor;
	}

	G_SetOrigin( ent, spawn_origin );
	VectorCopy( spawn_origin, client->ps.origin );

	// the respawned flag will be cleared after the attack and jump keys come up
	client->ps.pm_flags |= PMF_RESPAWNED;

	trap_GetUsercmd( client - level.clients, &ent->client->pers.cmd );
	SetClientViewAngle( ent, spawn_angles );

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {

	} else {
		G_KillBox( ent );
		trap_LinkEntity ( ent );

		// force the base weapon up
		client->ps.weapon = spawnWeapon;
		client->ps.weaponstate = WEAPON_READY;

	}

	// don't allow full run speed for a bit
	client->ps.pm_flags |= PMF_TIME_KNOCKBACK;
	client->ps.pm_time = 100;

	client->respawnTime = level.time;
	client->inactivityTime = level.time + g_inactivity.integer * 1000;
	client->latched_buttons = 0;

	// set default animations
	client->ps.torsoAnim = TORSO_STAND;
	client->ps.legsAnim = LEGS_IDLE;

	if ( level.intermissiontime ) {
		MoveClientToIntermission( ent );
	} else {
		// fire the targets of the spawn point
		G_UseTargets( spawnPoint, ent );

		// honor the factory-configured spawn weapon selection.
		client->ps.weapon = spawnWeapon;
	}

	// run a client frame to drop exactly to the floor,
	// initialize animations and other things
	client->ps.commandTime = level.time - 100;
	ent->client->pers.cmd.serverTime = level.time;
	ClientThink( ent-g_entities );

	// positively link the client, even if the command times are weird
	if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		BG_PlayerStateToEntityState( &client->ps, &ent->s, qtrue );
		VectorCopy( ent->client->ps.origin, ent->r.currentOrigin );
		trap_LinkEntity( ent );
	}

	// run the presend to set anything else
	G_GametypeClientSpawn( ent );
	G_GrantConfiguredItems( ent );
	G_RRInitClient( ent );
	ClientEndFrame( ent );

	// clear entity state values
	BG_PlayerStateToEntityState( &client->ps, &ent->s, qtrue );
}


/*
===========
ClientDisconnect

Called when a player drops from the server.
Will not be called between levels.

This should NOT be called directly by any game logic,
call trap_DropClient(), which will call this and do
server system housekeeping.
============
*/
void ClientDisconnect( int clientNum ) {
	gentity_t	*ent;
	gentity_t	*tent;
	int			i;

	// cleanup if we are kicking a bot that
	// hasn't spawned yet
	G_RemoveQueuedBotBegin( clientNum );

	ent = g_entities + clientNum;
	if ( !ent->client ) {
		return;
	}

	if ( !( ent->r.svFlags & SVF_BOT ) ) {
		char		userinfo[MAX_INFO_STRING];
		char		autoDetail[MAX_INFO_STRING];
		const char		*ipInfo;

		trap_GetUserinfo( clientNum, userinfo, sizeof( userinfo ) );
		ipInfo = Info_ValueForKey( userinfo, "ip" );
		Q_strncpyz( autoDetail, ipInfo ? ipInfo : "", sizeof( autoDetail ) );
		G_AutoAction( AUTOACTION_PLAYER_DISCONNECT, ent, autoDetail );
	}

	G_ComplaintClientDisconnected( clientNum );
	G_ComplaintResetClient( ent->client, qtrue );
	G_ResetClientVoteThrottle( ent->client );

	// stop any following clients
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].sess.sessionTeam == TEAM_SPECTATOR
			&& level.clients[i].sess.spectatorState == SPECTATOR_FOLLOW
			&& level.clients[i].sess.spectatorClient == clientNum ) {
			StopFollowing( &g_entities[i] );
		}
	}

	// send effect if they were completely connected
	if ( ent->client->pers.connected == CON_CONNECTED 
		&& ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		tent = G_TempEntity( ent->client->ps.origin, EV_PLAYER_TELEPORT_OUT );
		tent->s.clientNum = ent->s.clientNum;

		// They don't get to take powerups with them!
		// Especially important for stuff like CTF flags
		TossClientItems( ent, NULL, FLAG_DROP_CONTEXT_SCRIPTED, MOD_UNKNOWN );
		TossClientPersistantPowerups( ent );
		if( g_gametype.integer == GT_HARVESTER ) {
			TossClientCubes( ent );
		}

	}

	G_LogPrintf( "ClientDisconnect: %i\n", clientNum );

	// if we are playing in tourney mode and losing, give a win to the other player
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& !level.intermissiontime
		&& !level.warmupTime && level.sortedClients[1] == clientNum ) {
		level.clients[ level.sortedClients[0] ].sess.wins++;
		ClientUserinfoChanged( level.sortedClients[0] );
	}

	trap_UnlinkEntity (ent);
	ent->s.modelindex = 0;
	ent->inuse = qfalse;
	ent->classname = "disconnected";
	ent->client->pers.connected = CON_DISCONNECTED;
	ent->client->ps.persistant[PERS_TEAM] = TEAM_FREE;
	ent->client->sess.sessionTeam = TEAM_FREE;
	ent->client->lastKillCommandTime = 0;
	ent->client->killCommandCooldownExpires = 0;
	ent->client->friendlyFireComplaints = 0;
	ent->client->friendlyFireComplaintEndTime = 0;
	ent->client->teammateDamageGiven = 0;
	ent->client->teammateDamageThisLife = 0;

	trap_SetConfigstring( CS_PLAYERS + clientNum, "");

	CalculateRanks();

	if ( ent->r.svFlags & SVF_BOT ) {
		BotAIShutdownClient( clientNum, qfalse );
	}
}



/*
=============
G_RRIsActive

Returns qtrue when the Red Rover infection rule set should execute.
=============
*/
static qboolean G_RRIsActive( void ) {
	if ( g_gametype.integer != GT_RED_ROVER ) {
		return qfalse;
	}

	if ( !g_rrInfected.integer ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_RRResolveScoreValue

Rounds the floating-point cvar payload into an integer score value.
=============
*/
static int G_RRResolveScoreValue( float value ) {
	int			score;

	score = ( value >= 0.0f ) ? (int)( value + 0.5f ) : (int)( value - 0.5f );
	if ( score == 0 && value > 0.0f ) {
		score = 1;
	}

	return score;
}

/*
=============
G_RRAnnounceState

Sends a centerprint message informing a single client about their status.
=============
*/
static void G_RRAnnounceState( gentity_t *ent, const char *message ) {
	if ( !ent || !ent->client || !message || !message[0] ) {
		return;
	}

	trap_SendServerCommand( ent - g_entities, va( "cp \"%s\"", message ) );
}

/*
=============
G_RRApplyScoreDelta

Adds the provided delta to a client's score while respecting the
negative-score policy cvar.
=============
*/
static void G_RRApplyScoreDelta( gentity_t *ent, int score ) {
	int			current;

	if ( !ent || !ent->client || score == 0 ) {
		return;
	}

	if ( score < 0 && !g_rrAllowNegativeScores.integer ) {
		current = ent->client->ps.persistant[PERS_SCORE];
		if ( current + score < 0 ) {
			score = -current;
		}
	}

	if ( score != 0 ) {
		AddScore( ent, ent->r.currentOrigin, score );
	}
}

/*
=============
G_RRSetClientState

Transitions a player between survivor and infected states.
=============
*/
static void G_RRSetClientState( gentity_t *ent, rrInfectionState_t state, qboolean announce ) {
	int			spreadDelay;
	int			warningDelay;

	if ( !ent || !ent->client ) {
		return;
	}

	ent->client->rrInfectionState = state;
	ent->client->rrInfectionChangeTime = level.time;
	ent->client->rrAccumulatedDamage = 0;
	ent->client->ps.generic1 = ( state == RR_STATE_INFECTED ) ? 1 : 0;

	spreadDelay = g_rrInfectedSpreadTime.integer;
	if ( spreadDelay < 0 ) {
		spreadDelay = 0;
	}
	ent->client->rrInfectionNextSpreadTime = level.time + ( spreadDelay * 1000 );

	warningDelay = g_rrInfectedSpreadWarningTime.integer;
	if ( warningDelay < 0 ) {
		warningDelay = 0;
	}
	ent->client->rrInfectionNextWarningTime = ent->client->rrInfectionNextSpreadTime - ( warningDelay * 1000 );
	if ( ent->client->rrInfectionNextWarningTime < level.time ) {
		ent->client->rrInfectionNextWarningTime = level.time;
	}

	ent->client->rrInfectionNextPingTime = level.time + g_rrInfectedSurvivorPingRate.integer;

	if ( announce ) {
		if ( state == RR_STATE_INFECTED ) {
			G_RRAnnounceState( ent, "You have been infected!" );
		} else {
			G_RRAnnounceState( ent, "You are a survivor." );
		}
	}
}

/*
=============
G_RRInitClient

Initializes the infection state when a player spawns.
=============
*/
void G_RRInitClient( gentity_t *ent ) {
	if ( !G_RRIsActive() || !ent || !ent->client ) {
		return;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	if ( ent->client->sess.sessionTeam == TEAM_BLUE ) {
		G_RRSetClientState( ent, RR_STATE_INFECTED, qfalse );
		return;
	}

	G_RRSetClientState( ent, RR_STATE_SURVIVOR, qfalse );
}

/*
=============
G_RRWarnSurvivor

Periodically notifies slow survivors that they must keep moving.
=============
*/
static void G_RRWarnSurvivor( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	if ( g_rrInfectedSurvivorPingRate.integer <= 0 ) {
		return;
	}

	if ( ent->client->rrInfectionNextPingTime > level.time ) {
		return;
	}

	G_RRAnnounceState( ent, "Move it! Survivors that stall risk infection." );
	ent->client->rrInfectionNextPingTime = level.time + g_rrInfectedSurvivorPingRate.integer;
}

/*
=============
G_RRProcessClient

Runs per-frame infection logic for the specified player.
=============
*/
void G_RRProcessClient( gentity_t *ent ) {
	float		minSpeed;
	float		planarSpeedSq;
	float		minSpeedSq;

	if ( !G_RRIsActive() || !ent || !ent->client ) {
		return;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	if ( ent->client->rrInfectionState == RR_STATE_INFECTED ) {
		if ( g_rrInfectedZombieSpeed.value > 0.0f ) {
			ent->client->ps.speed *= g_rrInfectedZombieSpeed.value;
		}
		return;
	}

	minSpeed = g_rrInfectedSurvivorMinSpeed.value;
	if ( minSpeed > 0.0f ) {
		planarSpeedSq = ( ent->client->ps.velocity[0] * ent->client->ps.velocity[0] )
			+ ( ent->client->ps.velocity[1] * ent->client->ps.velocity[1] );
		minSpeedSq = minSpeed * minSpeed;
		if ( planarSpeedSq < minSpeedSq ) {
			G_RRWarnSurvivor( ent );
		} else {
			ent->client->rrInfectionNextPingTime = level.time + g_rrInfectedSurvivorPingRate.integer;
		}
	}

	if ( g_rrInfectedSpreadTime.integer > 0 ) {
		if ( ent->client->rrInfectionNextSpreadTime <= level.time ) {
			G_RRSetClientState( ent, RR_STATE_INFECTED, qtrue );
			return;
		}
		if ( ent->client->rrInfectionNextWarningTime > 0
			&& level.time >= ent->client->rrInfectionNextWarningTime ) {
			G_RRAnnounceState( ent, "Warning! The infection is spreading." );
			ent->client->rrInfectionNextWarningTime = 0;
		}
	}
}

/*
=============
G_RRGrantRoundBonus

Awards the configured round bonus to the specified team.
=============
*/
static void G_RRGrantRoundBonus( team_t team ) {
	int			score;
	int	clientNum;

	score = G_RRResolveScoreValue( g_rrRoundScoreBonus.value );
	if ( score <= 0 ) {
		return;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*target;

		target = &g_entities[clientNum];
		if ( !target->inuse || !target->client ) {
			continue;
		}

		if ( target->client->sess.sessionTeam != team ) {
			continue;
		}

		G_RRApplyScoreDelta( target, score );
	}
}

/*
=============
G_RRCheckRoundCompletion

Evaluates whether an active round has a winner yet.
=============
*/
static void G_RRCheckRoundCompletion( void ) {
	int			survivors;
	int			infected;
	int			clientNum;
	team_t	winner;

	if ( !G_RRIsActive() ) {
		return;
	}

	if ( level.roundState != ROUNDSTATE_ACTIVE ) {
		return;
	}

	survivors = 0;
	infected = 0;

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*scan = &g_entities[clientNum];
		if ( !scan->inuse || !scan->client ) {
			continue;
		}
		if ( scan->client->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}

		if ( scan->client->rrInfectionState == RR_STATE_INFECTED ) {
			infected++;
		} else {
			survivors++;
		}
	}

	if ( survivors > 0 && infected > 0 ) {
		return;
	}

	winner = ( survivors >= infected ) ? TEAM_RED : TEAM_BLUE;
	G_RRGrantRoundBonus( winner );
	level.roundState = ROUNDSTATE_COMPLETE;
	level.roundTransitionTime = level.time + 2000;
	G_UpdateMatchStateConfigString();
}

/*
=============
G_RRHandlePlayerDeath

Injects infection conversion logic when a client dies.
=============
*/
void G_RRHandlePlayerDeath( gentity_t *victim, gentity_t *attacker ) {
	if ( !G_RRIsActive() || !victim || !victim->client ) {
		return;
	}

	if ( victim->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	if ( attacker && attacker->client
		&& attacker->client->rrInfectionState == RR_STATE_INFECTED
		&& victim->client->rrInfectionState == RR_STATE_SURVIVOR ) {
		G_RRSetClientState( victim, RR_STATE_INFECTED, qtrue );
	}

	G_RRCheckRoundCompletion();
}

/*
=============
G_RRHandleDamageScore

Awards survivor score based on the configured scoring method.
=============
*/
void G_RRHandleDamageScore( gentity_t *attacker, gentity_t *targ, int damage ) {
	int			threshold;
	int			bonus;

	if ( !G_RRIsActive() || damage <= 0 ) {
		return;
	}

	if ( !attacker || !attacker->client || !targ || !targ->client ) {
		return;
	}

	if ( attacker->client->rrInfectionState != RR_STATE_SURVIVOR
		|| targ->client->rrInfectionState != RR_STATE_INFECTED ) {
		return;
	}

	if ( g_rrInfectedSurvivorScoreMethod.integer == 0 ) {
		threshold = g_rrInfectedSurvivorScoreRate.integer;
		if ( threshold <= 0 ) {
			return;
		}

		attacker->client->rrAccumulatedDamage += damage;
		bonus = G_RRResolveScoreValue( g_rrInfectedSurvivorScoreBonus.value );
		while ( attacker->client->rrAccumulatedDamage >= threshold && bonus > 0 ) {
			attacker->client->rrAccumulatedDamage -= threshold;
			G_RRApplyScoreDelta( attacker, bonus );
		}
		return;
	}

	bonus = G_RRResolveScoreValue( damage * g_rrDamageScoreBonus.value );
	if ( bonus > 0 ) {
		G_RRApplyScoreDelta( attacker, bonus );
	}
}

/*
=============
G_RRResetRoundState

Clears per-round state whenever the controller enters warmup.
=============
*/
void G_RRResetRoundState( void ) {
	int			clientNum;

	if ( !G_RRIsActive() ) {
		return;
	}

	level.roundStartTime = level.time;
	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*ent = &g_entities[clientNum];
		if ( !ent->inuse || !ent->client ) {
			continue;
		}
		G_RRInitClient( ent );
	}
}

/*
=============
G_RRTrackRoundActivity

Monitors round timers and completion state each frame.
=============
*/
void G_RRTrackRoundActivity( void ) {
	int			limit;

	if ( !G_RRIsActive() ) {
		return;
	}

	if ( level.roundState != ROUNDSTATE_ACTIVE ) {
		return;
	}

	G_RRCheckRoundCompletion();

	limit = roundtimelimit.integer;
	if ( limit <= 0 ) {
		return;
	}

	if ( level.time - level.roundStartTime >= limit * 1000 ) {
		G_RRGrantRoundBonus( TEAM_RED );
		level.roundState = ROUNDSTATE_COMPLETE;
		level.roundTransitionTime = level.time + 2000;
		G_UpdateMatchStateConfigString();
	}
}



