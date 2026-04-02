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

typedef struct g_lagHaxHistory_s {
	struct g_lagHaxHistory_s	*next;
	struct g_lagHaxHistory_s	*prev;
	vec3_t				currentOrigin;
	vec3_t				mins;
	vec3_t				maxs;
	int				time;
} g_lagHaxHistory_t;

typedef struct {
	vec3_t	currentOrigin;
	vec3_t	mins;
	vec3_t	maxs;
	int	time;
} g_lagHaxSave_t;

static g_lagHaxHistory_t	*g_lagHaxHistoryHeads[MAX_CLIENTS];
static g_lagHaxSave_t		g_lagHaxSaved[MAX_CLIENTS];

/*
=============
G_InitLagHaxHistory

Allocates the hidden retail lag-hax rewind history ring for each client slot.
=============
*/
void G_InitLagHaxHistory( void ) {
	int			clientNum;
	int			historyCount;
	g_lagHaxHistory_t	*history;
	g_lagHaxHistory_t	*cursor;
	int			i;

	memset( g_lagHaxHistoryHeads, 0, sizeof( g_lagHaxHistoryHeads ) );
	memset( g_lagHaxSaved, 0, sizeof( g_lagHaxSaved ) );

	if ( level.maxclients <= 0 ) {
		return;
	}

	historyCount = g_lagHaxHistory.integer;
	if ( historyCount <= 0 || g_lagHaxMs.integer <= 0 ) {
		return;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		history = G_Alloc( historyCount * (int)sizeof( *history ) );
		if ( !history ) {
			break;
		}

		g_lagHaxHistoryHeads[clientNum] = history;
		cursor = history;

		for ( i = 1; i < historyCount; i++ ) {
			cursor->time = 0;
			cursor->next = cursor + 1;
			cursor->next->prev = cursor;
			cursor = cursor->next;
		}

		cursor->time = 0;
		cursor->next = history;
		history->prev = cursor;
	}
}

/*
=============
G_ClearLagHaxHistory

Invalidates the current rewind head for the given client after spawn,
teleport, or disconnect transitions.
=============
*/
void G_ClearLagHaxHistory( gentity_t *ent ) {
	int			clientNum;
	g_lagHaxHistory_t	*history;

	if ( !ent ) {
		return;
	}

	clientNum = ent - g_entities;
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}

	history = g_lagHaxHistoryHeads[clientNum];
	if ( !history ) {
		return;
	}

	history->time = 0;
}

/*
=============
G_StoreHistory

Records the latest collision origin and bounds into the retail rewind ring.
Non-player entity states invalidate the current slot instead.
=============
*/
void G_StoreHistory( gentity_t *ent ) {
	int			clientNum;
	g_lagHaxHistory_t	*history;

	if ( !ent ) {
		return;
	}

	clientNum = ent - g_entities;
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}

	history = g_lagHaxHistoryHeads[clientNum];
	if ( !history ) {
		return;
	}

	history = history->next;
	g_lagHaxHistoryHeads[clientNum] = history;

	if ( ent->s.eType != ET_PLAYER ) {
		history->time = 0;
		return;
	}

	history->time = level.time;
	VectorCopy( ent->s.pos.trBase, history->currentOrigin );
	VectorCopy( ent->r.mins, history->mins );
	VectorCopy( ent->r.maxs, history->maxs );
}

/*
=============
G_TimeShiftClient

Rewinds a single target client toward the requested command time using the
retail history ring interpolation path.
=============
*/
static void G_TimeShiftClient( gentity_t *ent, int time ) {
	int			clientNum;
	g_lagHaxHistory_t	*older;
	g_lagHaxHistory_t	*newer;
	float			frac;
	vec3_t			delta;

	if ( !ent ) {
		return;
	}

	clientNum = ent - g_entities;
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}

	older = g_lagHaxHistoryHeads[clientNum];
	if ( !older ) {
		return;
	}

	newer = older;
	if ( time > older->time ) {
		return;
	}

	while ( time < older->time ) {
		newer = older;
		older = older->prev;
		if ( older->time >= newer->time ) {
			older = newer;
			break;
		}
	}

	if ( older->time == 0 ) {
		return;
	}

	trap_UnlinkEntity( ent );

	if ( newer == older ) {
		VectorCopy( newer->currentOrigin, ent->r.currentOrigin );
	} else if ( older->time != newer->time ) {
		frac = (float)( time - older->time ) / (float)( newer->time - older->time );
		VectorSubtract( newer->currentOrigin, older->currentOrigin, delta );
		VectorMA( older->currentOrigin, frac, delta, ent->r.currentOrigin );
	}

	VectorCopy( newer->mins, ent->r.mins );
	VectorCopy( newer->maxs, ent->r.maxs );
	trap_LinkEntity( ent );
}

/*
=============
G_TimeShiftAllClients

Rewinds eligible target clients around hitscan weapon traces for the hidden
retail lag-hax path.
=============
*/
void G_TimeShiftAllClients( gentity_t *skip, int time ) {
	int		clientNum;
	int		earliestTime;
	gentity_t	*ent;

	if ( !skip ) {
		return;
	}

	if ( g_lagHaxMs.integer <= 0 || g_lagHaxHistory.integer <= 0 ) {
		return;
	}

	if ( skip->r.svFlags & SVF_BOT ) {
		return;
	}

	earliestTime = level.time - g_lagHaxMs.integer;
	if ( time < earliestTime ) {
		time = earliestTime;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		ent = &g_entities[clientNum];
		g_lagHaxSaved[clientNum].time = 0;

		if ( !ent->client ) {
			continue;
		}

		if ( ent == skip ) {
			continue;
		}

		if ( ent->client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		if ( ent->client->ps.pm_type == PM_DEAD ) {
			continue;
		}

		VectorCopy( ent->r.currentOrigin, g_lagHaxSaved[clientNum].currentOrigin );
		VectorCopy( ent->r.mins, g_lagHaxSaved[clientNum].mins );
		VectorCopy( ent->r.maxs, g_lagHaxSaved[clientNum].maxs );
		g_lagHaxSaved[clientNum].time = level.time;

		G_TimeShiftClient( ent, time );
	}
}

/*
=============
G_UnTimeShiftAllClients

Restores any clients rewound during the current lag-hax hitscan pass.
=============
*/
void G_UnTimeShiftAllClients( void ) {
	int		clientNum;
	gentity_t	*ent;

	if ( g_lagHaxMs.integer <= 0 || g_lagHaxHistory.integer <= 0 ) {
		return;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		if ( g_lagHaxSaved[clientNum].time != level.time ) {
			continue;
		}

		ent = &g_entities[clientNum];
		VectorCopy( g_lagHaxSaved[clientNum].currentOrigin, ent->r.currentOrigin );
		VectorCopy( g_lagHaxSaved[clientNum].mins, ent->r.mins );
		VectorCopy( g_lagHaxSaved[clientNum].maxs, ent->r.maxs );
		trap_LinkEntity( ent );
	}
}


/*
===============
G_SetClientRatingModifiers

Applies rating metadata to the runtime damage and score modifiers for a client.
===============
*/
void G_SetClientRatingModifiers( gclient_t *client, float damageScale, float scoreScale ) {
	if ( !client ) {
		return;
	}

	if ( damageScale <= 0.0f ) {
		damageScale = 1.0f;
	}
	if ( scoreScale <= 0.0f ) {
		scoreScale = 1.0f;
	}

	client->damageModifier = damageScale;
	client->scoreModifier = scoreScale;
}


/*
=============
G_RefreshClientRatingModifiers

Synchronises the runtime rating modifiers with the cached persistence values.
=============
*/
void G_RefreshClientRatingModifiers( gclient_t *client ) {
	float	damageScale;
	float	scoreScale;

	if ( !client ) {
		return;
	}

	damageScale = client->pers.ratingDamageScale;
	scoreScale = client->pers.ratingScoreScale;

	if ( damageScale <= 0.0f ) {
		damageScale = 1.0f;
		client->pers.ratingDamageScale = damageScale;
	}

	if ( scoreScale <= 0.0f ) {
		scoreScale = 1.0f;
		client->pers.ratingScoreScale = scoreScale;
	}

	if ( client->damageModifier != damageScale || client->scoreModifier != scoreScale ) {
		G_SetClientRatingModifiers( client, damageScale, scoreScale );
	}
}


/*
===============
G_DamageFeedback

Called just before a snapshot is sent to the given player.
Totals up all damage and generates both the player_state_t
damage values to that client for pain blends and kicks, and
global pain sound events for all clients.
===============
*/
void P_DamageFeedback( gentity_t *player ) {
	gclient_t	*client;
	float	count;
	vec3_t	angles;

	client = player->client;
	if ( client->ps.pm_type == PM_DEAD ) {
		return;
	}

	// total points of damage shot at the player this frame
	count = client->damage_blood + client->damage_armor;
	if ( count == 0 ) {
		return;		// didn't take any damage
	}

	if ( count > 255 ) {
		count = 255;
	}

	// send the information to the client

	// world damage (falling, slime, etc) uses a special code
	// to make the blend blob centered instead of positional
	if ( client->damage_fromWorld ) {
		client->ps.damagePitch = 255;
		client->ps.damageYaw = 255;

		client->damage_fromWorld = qfalse;
	} else {
		vectoangles( client->damage_from, angles );
		client->ps.damagePitch = angles[PITCH]/360.0 * 256;
		client->ps.damageYaw = angles[YAW]/360.0 * 256;
	}

	// play an apropriate pain sound
	if ( (level.time > player->pain_debounce_time) && !(player->flags & FL_GODMODE) ) {
		player->pain_debounce_time = level.time + 700;
		G_AddEvent( player, EV_PAIN, player->health );
		client->ps.damageEvent++;
	}


	client->ps.damageCount = count;

	//
	// clear totals
	//
	client->damage_blood = 0;
	client->damage_armor = 0;
	client->damage_knockback = 0;
}



/*
=============
P_WorldEffects

Check for lava / slime contents and drowning
=============
*/
void P_WorldEffects( gentity_t *ent ) {
	qboolean	envirosuit;
	int			waterlevel;

	if ( ent->client->noclip ) {
		ent->client->airOutTime = level.time + 12000;	// don't need air
		return;
	}

	waterlevel = ent->waterlevel;

	envirosuit = ent->client->ps.powerups[PW_BATTLESUIT] > level.time;

	//
	// check for drowning
	//
	if ( waterlevel == 3 ) {
		// envirosuit give air
		if ( envirosuit ) {
			ent->client->airOutTime = level.time + 10000;
		}

		// if out of air, start drowning
		if ( ent->client->airOutTime < level.time) {
			// drown!
			ent->client->airOutTime += 1000;
			if ( ent->health > 0 ) {
				// take more damage the longer underwater
				ent->damage += 2;
				if (ent->damage > 15)
					ent->damage = 15;

				// play a gurp sound instead of a normal pain sound
				if (ent->health <= ent->damage) {
					G_Sound(ent, CHAN_VOICE, G_SoundIndex("*drown.wav"));
				} else if (rand()&1) {
					G_Sound(ent, CHAN_VOICE, G_SoundIndex("sound/player/gurp1.wav"));
				} else {
					G_Sound(ent, CHAN_VOICE, G_SoundIndex("sound/player/gurp2.wav"));
				}

				// don't play a normal pain sound
				ent->pain_debounce_time = level.time + 200;

				G_Damage (ent, NULL, NULL, NULL, NULL, 
					ent->damage, DAMAGE_NO_ARMOR, MOD_WATER);
			}
		}
	} else {
		ent->client->airOutTime = level.time + 12000;
		ent->damage = 2;
	}

	//
	// check for sizzle damage (move to pmove?)
	//
	if (waterlevel && 
		(ent->watertype&(CONTENTS_LAVA|CONTENTS_SLIME)) ) {
		if (ent->health > 0
			&& ent->pain_debounce_time <= level.time	) {

			if ( envirosuit ) {
				G_AddEvent( ent, EV_POWERUP_BATTLESUIT, 0 );
			} else {
				if (ent->watertype & CONTENTS_LAVA) {
					G_Damage (ent, NULL, NULL, NULL, NULL, 
						30*waterlevel, 0, MOD_LAVA);
				}

				if (ent->watertype & CONTENTS_SLIME) {
					G_Damage (ent, NULL, NULL, NULL, NULL, 
						10*waterlevel, 0, MOD_SLIME);
				}
			}
		}
	}
}



/*
===============
G_SetClientSound
===============
*/
void G_SetClientSound( gentity_t *ent ) {
	if( ent->s.eFlags & EF_TICKING ) {
		ent->client->ps.loopSound = G_SoundIndex( "sound/weapons/proxmine/wstbtick.wav");
	}
	else
	if (ent->waterlevel && (ent->watertype&(CONTENTS_LAVA|CONTENTS_SLIME)) ) {
		ent->client->ps.loopSound = level.snd_fry;
	} else {
		ent->client->ps.loopSound = 0;
	}
}



//==============================================================

/*
==============
ClientImpacts
==============
*/
void ClientImpacts( gentity_t *ent, pmove_t *pm ) {
	int		i, j;
	trace_t	trace;
	gentity_t	*other;

	memset( &trace, 0, sizeof( trace ) );
	for (i=0 ; i<pm->numtouch ; i++) {
		for (j=0 ; j<i ; j++) {
			if (pm->touchents[j] == pm->touchents[i] ) {
				break;
			}
		}
		if (j != i) {
			continue;	// duplicated
		}
		other = &g_entities[ pm->touchents[i] ];

		if ( ( ent->r.svFlags & SVF_BOT ) && ( ent->touch ) ) {
			ent->touch( ent, other, &trace );
		}

		if ( !other->touch ) {
			continue;
		}

		other->touch( other, ent, &trace );
	}

}

/*
============
G_TouchTriggers

Find all trigger entities that ent's current position touches.
Spectators will only interact with teleporters.
============
*/
void	G_TouchTriggers( gentity_t *ent ) {
	int			i, num;
	int			touch[MAX_GENTITIES];
	gentity_t	*hit;
	trace_t		trace;
	vec3_t		mins, maxs;
	static vec3_t	range = { 40, 40, 52 };

	if ( !ent->client ) {
		return;
	}

	// dead clients don't activate triggers!
	if ( ent->client->ps.stats[STAT_HEALTH] <= 0 ) {
		return;
	}

	VectorSubtract( ent->client->ps.origin, range, mins );
	VectorAdd( ent->client->ps.origin, range, maxs );

	num = trap_EntitiesInBox( mins, maxs, touch, MAX_GENTITIES );

	// can't use ent->absmin, because that has a one unit pad
	VectorAdd( ent->client->ps.origin, ent->r.mins, mins );
	VectorAdd( ent->client->ps.origin, ent->r.maxs, maxs );

	for ( i=0 ; i<num ; i++ ) {
		hit = &g_entities[touch[i]];

		if ( !hit->touch && !ent->touch ) {
			continue;
		}
		if ( !( hit->r.contents & CONTENTS_TRIGGER ) ) {
			continue;
		}

		// ignore most entities if a spectator
		if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
			if ( hit->s.eType != ET_TELEPORT_TRIGGER &&
				// this is ugly but adding a new ET_? type will
				// most likely cause network incompatibilities
				hit->touch != Touch_DoorTrigger) {
				continue;
			}
		}

		// use seperate code for determining if an item is picked up
		// so you don't have to actually contact its bounding box
		if ( hit->s.eType == ET_ITEM ) {
			if ( !BG_PlayerTouchesItem( &ent->client->ps, &hit->s, level.time ) ) {
				continue;
			}
		} else {
			if ( !trap_EntityContact( mins, maxs, hit ) ) {
				continue;
			}
		}

		memset( &trace, 0, sizeof(trace) );

		if ( hit->touch ) {
			hit->touch (hit, ent, &trace);
		}

		if ( ( ent->r.svFlags & SVF_BOT ) && ( ent->touch ) ) {
			ent->touch( ent, hit, &trace );
		}
	}

	// if we didn't touch a jump pad this pmove frame
	if ( ent->client->ps.jumppad_frame != ent->client->ps.pmove_framecount ) {
		ent->client->ps.jumppad_frame = 0;
		ent->client->ps.jumppad_ent = 0;
	}
}

/*
=================
SpectatorThink
=================
*/
void SpectatorThink( gentity_t *ent, usercmd_t *ucmd ) {
	pmove_t	pm;
	gclient_t	*client;

	client = ent->client;

	if ( client->sess.spectatorState != SPECTATOR_FOLLOW ) {
		client->ps.pm_type = PM_SPECTATOR;
		client->ps.speed = 400;	// faster than normal

		// set up for pmove
		memset (&pm, 0, sizeof(pm));
		pm.ps = &client->ps;
		pm.cmd = *ucmd;
		pm.tracemask = MASK_PLAYERSOLID & ~CONTENTS_BODY;	// spectators can fly through bodies
		pm.pmoveSettings = &g_pmoveSettings;
		pm.trace = trap_Trace;
		pm.pointcontents = trap_PointContents;

		// perform a pmove
		Pmove (&pm);
		// save results of pmove
		VectorCopy( client->ps.origin, ent->s.origin );

		G_TouchTriggers( ent );
		trap_UnlinkEntity( ent );
	} else {
		// If following POI, ensure position is updated
		if ( client->sess.spectatorClient <= -10 ) {
			int poiIndex = -(client->sess.spectatorClient + 10);
			if ( poiIndex >= 0 && poiIndex < level.numPois && level.pois[poiIndex].inuse ) {
				VectorCopy( level.pois[poiIndex].origin, client->ps.origin );
				VectorCopy( level.pois[poiIndex].angles, client->ps.viewangles );
				SetClientViewAngle( ent, level.pois[poiIndex].angles );
			}
		}
	}

	client->oldbuttons = client->buttons;
	client->buttons = ucmd->buttons;

	// attack button cycles through spectators
	if ( ( client->buttons & BUTTON_ATTACK ) && ! ( client->oldbuttons & BUTTON_ATTACK ) ) {
		Cmd_FollowCycle_f( ent, 1 );
	}
}



/*
=================
ClientInactivityTimer

Returns qfalse if the client is dropped
=================
*/
qboolean ClientInactivityTimer( gclient_t *client ) {
	if ( level.trainingMapActive ) {
		client->inactivityTime = level.time + 60 * 1000;
		client->inactivityWarning = qfalse;
		return qtrue;
	}

	if ( ! g_inactivity.integer ) {
		// give everyone some time, so if the operator sets g_inactivity during
		// gameplay, everyone isn't kicked
		client->inactivityTime = level.time + 60 * 1000;
		client->inactivityWarning = qfalse;
	} else if ( client->pers.cmd.forwardmove || 
		client->pers.cmd.rightmove || 
		client->pers.cmd.upmove ||
		(client->pers.cmd.buttons & BUTTON_ATTACK) ) {
		client->inactivityTime = level.time + g_inactivity.integer * 1000;
		client->inactivityWarning = qfalse;
	} else if ( !client->pers.localClient ) {
		if ( level.time > client->inactivityTime ) {
			trap_DropClient( client - level.clients, "Dropped due to inactivity" );
			return qfalse;
		}
		if ( level.time > client->inactivityTime - 10000 && !client->inactivityWarning ) {
			client->inactivityWarning = qtrue;
			trap_SendServerCommand( client - level.clients, "cp \"Ten seconds until inactivity drop!\n\"" );
		}
	}
	return qtrue;
}

/*
=================
G_CheckClientFlood

Retail qagame decays the shared flood counter from the active-client path and
drops clients once the burst limit is exceeded.
=================
*/
static qboolean G_CheckClientFlood( gentity_t *ent ) {
	gclient_t	*client;
	int		maxCount;
	int		decay;

	if ( !ent || !ent->client ) {
		return qtrue;
	}

	maxCount = g_floodprot_maxcount.integer;
	decay = g_floodprot_decay.integer;
	client = ent->client;
	client->floodPenaltyTime = 0;

	if ( maxCount <= 0 || decay <= 0 ) {
		return qtrue;
	}

	if ( client->floodCount > maxCount ) {
		trap_DropClient( ent - g_entities, "Dropped for flooding the server" );
		return qfalse;
	}

	if ( client->floodLastTime > 0 && level.time - client->floodLastTime > decay ) {
		client->floodLastTime = level.time;
		if ( client->floodCount > 0 ) {
			client->floodCount--;
		}
	}

	return qtrue;
}

/*
=============
G_FactoryHealthRegenEnabled

Returns whether retail-style factory health regeneration is configured.
=============
*/
static qboolean G_FactoryHealthRegenEnabled( void ) {
	return ( g_factoryCvarConfig.regenHealthDelayMilliseconds > 0
		&& g_factoryCvarConfig.regenHealthRateMilliseconds > 0 ) ? qtrue : qfalse;
}

/*
=============
G_FactoryArmorRegenEnabled

Returns whether retail-style factory armor regeneration is configured.
=============
*/
static qboolean G_FactoryArmorRegenEnabled( void ) {
	return ( g_factoryCvarConfig.regenArmorDelayMilliseconds > 0
		&& g_factoryCvarConfig.regenArmorRateMilliseconds > 0 ) ? qtrue : qfalse;
}

/*
=============
G_RunFactoryHealthRegen

Applies the mapped retail health-regen sidecar once the post-damage delay has elapsed.
=============
*/
static void G_RunFactoryHealthRegen( gentity_t *ent, int msec ) {
	gclient_t	*client;
	int		healthTarget;

	if ( !ent || !ent->client || msec <= 0 ) {
		return;
	}

	client = ent->client;
	if ( !G_FactoryHealthRegenEnabled() ) {
		return;
	}

	healthTarget = client->ps.stats[STAT_MAX_HEALTH];
	if ( ent->health >= healthTarget ) {
		client->factoryRegenHealthPending = qfalse;
		return;
	}

	if ( !client->factoryRegenHealthPending || client->factoryRegenLastDamageTime <= 0 ) {
		return;
	}

	if ( level.time - client->factoryRegenLastDamageTime <= g_factoryCvarConfig.regenHealthDelayMilliseconds ) {
		return;
	}

	client->factoryRegenHealthAccumulatorMs += msec;
	while ( client->factoryRegenHealthAccumulatorMs >= g_factoryCvarConfig.regenHealthRateMilliseconds ) {
		ent->health += 1;
		client->factoryRegenHealthAccumulatorMs -= g_factoryCvarConfig.regenHealthRateMilliseconds;
	}
}

/*
=============
G_RunFactoryArmorRegen

Applies the mapped retail armor-regen sidecar once the post-damage delay has elapsed.
=============
*/
static void G_RunFactoryArmorRegen( gentity_t *ent, int msec ) {
	gclient_t	*client;
	int		armorTarget;

	if ( !ent || !ent->client || msec <= 0 ) {
		return;
	}

	client = ent->client;
	if ( !G_FactoryArmorRegenEnabled() ) {
		return;
	}

	armorTarget = BG_GetArmorRegenTarget( &client->ps, g_armorTiered.integer ? qtrue : qfalse );
	if ( client->ps.stats[STAT_ARMOR] >= armorTarget ) {
		client->factoryRegenArmorPending = qfalse;
		return;
	}

	if ( !client->factoryRegenArmorPending ) {
		return;
	}

	if ( level.time - client->factoryRegenLastDamageTime <= g_factoryCvarConfig.regenArmorDelayMilliseconds ) {
		return;
	}

	if ( g_factoryCvarConfig.regenArmorAfterHealth && ent->health < client->ps.stats[STAT_MAX_HEALTH] ) {
		return;
	}

	client->factoryRegenArmorAccumulatorMs += msec;
	while ( client->factoryRegenArmorAccumulatorMs >= g_factoryCvarConfig.regenArmorRateMilliseconds ) {
		client->ps.stats[STAT_ARMOR] += 1;
		client->factoryRegenArmorAccumulatorMs -= g_factoryCvarConfig.regenArmorRateMilliseconds;
	}
}

/*
==================
ClientTimerActions

Runs once-per-second timers and the retail-style per-frame factory regen sidecars.
==================
*/
void ClientTimerActions( gentity_t *ent, int msec ) {
	gclient_t	*client;
	int			maxHealth;

	client = ent->client;
	client->timeResidual += msec;

	while ( client->timeResidual >= 1000 ) {
		client->timeResidual -= 1000;

		// regenerate
		if( bg_itemlist[client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_GUARD ) {
			maxHealth = client->ps.stats[STAT_MAX_HEALTH] / 2;
		}
		else if ( client->ps.powerups[PW_REGEN] ) {
			maxHealth = client->ps.stats[STAT_MAX_HEALTH];
		}
		else {
			maxHealth = 0;
		}
		if( maxHealth ) {
			if ( ent->health < maxHealth ) {
				ent->health += 15;
				if ( ent->health > maxHealth * 1.1 ) {
					ent->health = maxHealth * 1.1;
				}
				G_AddEvent( ent, EV_POWERUP_REGEN, 0 );
			} else if ( ent->health < maxHealth * 2) {
				ent->health += 5;
				if ( ent->health > maxHealth * 2 ) {
					ent->health = maxHealth * 2;
				}
				G_AddEvent( ent, EV_POWERUP_REGEN, 0 );
			}
		} else {
			// count down health when over max
			if ( ent->health > client->ps.stats[STAT_MAX_HEALTH] ) {
				ent->health--;
			}
		}

		// count down armor when over max
		if ( !g_armorTiered.integer && client->ps.stats[STAT_ARMOR] > client->ps.stats[STAT_MAX_HEALTH] ) {
			client->ps.stats[STAT_ARMOR]--;
		}
	}
	if( bg_itemlist[client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_AMMOREGEN ) {
		int w, max, inc, t, i;
		int weapList[] = {
			WP_MACHINEGUN,
			WP_SHOTGUN,
			WP_GRENADE_LAUNCHER,
			WP_ROCKET_LAUNCHER,
			WP_LIGHTNING,
			WP_RAILGUN,
			WP_PLASMAGUN,
			WP_BFG,
			WP_NAILGUN,
			WP_PROX_LAUNCHER,
			WP_CHAINGUN
		};
		int weapCount = ARRAY_LEN( weapList );
		//
		for ( i = 0; i < weapCount; i++ ) {
			w = weapList[i];

			switch ( w ) {
				case WP_MACHINEGUN: max = 50; inc = 4; t = 1000; break;
				case WP_SHOTGUN: max = 10; inc = 1; t = 1500; break;
				case WP_GRENADE_LAUNCHER: max = 10; inc = 1; t = 2000; break;
				case WP_ROCKET_LAUNCHER: max = 10; inc = 1; t = 1750; break;
				case WP_LIGHTNING: max = 50; inc = 5; t = 1500; break;
				case WP_RAILGUN: max = 10; inc = 1; t = 1750; break;
				case WP_PLASMAGUN: max = 50; inc = 5; t = 1500; break;
				case WP_BFG: max = 10; inc = 1; t = 4000; break;
				case WP_NAILGUN: max = 10; inc = 1; t = 1250; break;
				case WP_PROX_LAUNCHER: max = 5; inc = 1; t = 2000; break;
				case WP_CHAINGUN: max = 100; inc = 5; t = 1000; break;
				default: max = 0; inc = 0; t = 1000; break;
			}
			client->ammoTimes[w] += msec;
			if ( client->ps.ammo[w] >= max ) {
				client->ammoTimes[w] = 0;
			}
			if ( client->ammoTimes[w] >= t ) {
				while ( client->ammoTimes[w] >= t ) {
					client->ammoTimes[w] -= t;
				}
				client->ps.ammo[w] += inc;
				if ( client->ps.ammo[w] > max ) {
					client->ps.ammo[w] = max;
				}
			}
		}
	}

	G_RunFactoryHealthRegen( ent, msec );
	G_RunFactoryArmorRegen( ent, msec );
}

/*
====================
ClientIntermissionThink
====================
*/
void ClientIntermissionThink( gclient_t *client ) {
	client->ps.eFlags &= ~EF_TALK;
	client->ps.eFlags &= ~EF_FIRING;

	// the level will exit when everyone wants to or after timeouts

	// swap and latch button actions
	client->oldbuttons = client->buttons;
	client->buttons = client->pers.cmd.buttons;
	if ( client->buttons & ( BUTTON_ATTACK | BUTTON_USE_HOLDABLE ) & ( client->oldbuttons ^ client->buttons ) ) {
		// this used to be an ^1 but once a player says ready, it should stick
		client->readyToExit = 1;
	}
}


/*
================
ClientEvents

Events will be passed on to the clients for presentation,
but any server game effects are handled here
================
*/
void ClientEvents( gentity_t *ent, int oldEventSequence ) {
	int		i, j;
	int		event;
	gclient_t *client;
	int		damage;
	vec3_t	dir;
	vec3_t	origin, angles;
//	qboolean	fired;
	gitem_t *item;
	gentity_t *drop;

	client = ent->client;

	if ( oldEventSequence < client->ps.eventSequence - MAX_PS_EVENTS ) {
		oldEventSequence = client->ps.eventSequence - MAX_PS_EVENTS;
	}
	for ( i = oldEventSequence ; i < client->ps.eventSequence ; i++ ) {
		event = client->ps.events[ i & (MAX_PS_EVENTS-1) ];

		switch ( event ) {
		case EV_FALL_MEDIUM:
		case EV_FALL_FAR:
			if ( ent->s.eType != ET_PLAYER ) {
				break;		// not in the player model
			}
			if ( g_dmflags.integer & DF_NO_FALLING ) {
				break;
			}
			if ( event == EV_FALL_FAR ) {
				damage = 10;
			} else {
				damage = 5;
			}
			VectorSet (dir, 0, 0, 1);
			ent->pain_debounce_time = level.time + 200;	// no normal pain sound
			G_Damage (ent, NULL, NULL, NULL, NULL, damage, 0, MOD_FALLING);
			break;

		case EV_FIRE_WEAPON:
			FireWeapon( ent );
			break;

		case EV_USE_ITEM1:		// teleporter
			// drop flags in CTF
			item = NULL;
			j = 0;

			if ( ent->client->ps.powerups[ PW_REDFLAG ] ) {
				item = BG_FindItemForPowerup( PW_REDFLAG );
				j = PW_REDFLAG;
			} else if ( ent->client->ps.powerups[ PW_BLUEFLAG ] ) {
				item = BG_FindItemForPowerup( PW_BLUEFLAG );
				j = PW_BLUEFLAG;
			} else if ( ent->client->ps.powerups[ PW_NEUTRALFLAG ] ) {
				item = BG_FindItemForPowerup( PW_NEUTRALFLAG );
				j = PW_NEUTRALFLAG;
			}

		if ( item ) {
			int remaining = ent->client->ps.powerups[ j ];
			flagDropResult_t dropResult;
			gentity_t *dropped = NULL;

			dropResult = G_TossFlag( ent, j, FLAG_DROP_CONTEXT_SCRIPTED, NULL, MOD_UNKNOWN, &dropped );
			if ( dropResult == FLAG_DROP_RESULT_DROPPED && dropped ) {
				// decide how many seconds it has left
				dropped->count = ( remaining - level.time ) / 1000;
				if ( dropped->count < 1 ) {
					dropped->count = 1;
				}
			}
		}
			if ( g_gametype.integer == GT_HARVESTER ) {
				if ( ent->client->ps.generic1 > 0 ) {
					if ( ent->client->sess.sessionTeam == TEAM_RED ) {
						item = BG_FindItem( "Blue Cube" );
					} else {
						item = BG_FindItem( "Red Cube" );
					}
					if ( item ) {
						for ( j = 0; j < ent->client->ps.generic1; j++ ) {
							drop = Drop_Item( ent, item, 0 );
							if ( drop ) {
								if ( ent->client->sess.sessionTeam == TEAM_RED ) {
									drop->spawnflags = TEAM_BLUE;
								} else {
									drop->spawnflags = TEAM_RED;
								}
							}
						}
					}
					ent->client->ps.generic1 = 0;
				}
			}
			SelectSpawnPoint( ent->client->ps.origin, origin, angles );
			TeleportPlayer( ent, origin, angles );
			break;

		case EV_USE_ITEM2:		// medkit
			ent->health = ent->client->ps.stats[STAT_MAX_HEALTH] + 25;

			break;

		case EV_USE_ITEM3:		// kamikaze
			// make sure the invulnerability is off
			ent->client->invulnerabilityTime = 0;
			ent->client->holdableInvulnerabilityTime = 0;
			// start the kamikze
			G_StartKamikaze( ent );
			break;

		case EV_USE_ITEM4:		// portal
			if( ent->client->portalID ) {
				DropPortalSource( ent );
			}
			else {
				DropPortalDestination( ent );
			}
			break;
		case EV_USE_ITEM5:		// invulnerability
			ent->client->invulnerabilityTime = level.time + 10000;
			ent->client->holdableInvulnerabilityTime = ent->client->invulnerabilityTime;
			break;

default:
break;
}

G_FreezeRunFrame();
}

}

/*
==============
StuckInOtherClient
==============
*/
static int StuckInOtherClient(gentity_t *ent) {
	int i;
	gentity_t	*ent2;

	ent2 = &g_entities[0];
	for ( i = 0; i < MAX_CLIENTS; i++, ent2++ ) {
		if ( ent2 == ent ) {
			continue;
		}
		if ( !ent2->inuse ) {
			continue;
		}
		if ( !ent2->client ) {
			continue;
		}
		if ( ent2->health <= 0 ) {
			continue;
		}
		//
		if (ent2->r.absmin[0] > ent->r.absmax[0])
			continue;
		if (ent2->r.absmin[1] > ent->r.absmax[1])
			continue;
		if (ent2->r.absmin[2] > ent->r.absmax[2])
			continue;
		if (ent2->r.absmax[0] < ent->r.absmin[0])
			continue;
		if (ent2->r.absmax[1] < ent->r.absmin[1])
			continue;
		if (ent2->r.absmax[2] < ent->r.absmin[2])
			continue;
		return qtrue;
	}
	return qfalse;
}

void BotTestSolid(vec3_t origin);

/*
==============
SendPendingPredictableEvents
==============
*/
void SendPendingPredictableEvents( playerState_t *ps ) {
	gentity_t *t;
	int event, seq;
	int extEvent, number;

	// if there are still events pending
	if ( ps->entityEventSequence < ps->eventSequence ) {
		// create a temporary entity for this event which is sent to everyone
		// except the client who generated the event
		seq = ps->entityEventSequence & (MAX_PS_EVENTS-1);
		event = ps->events[ seq ] | ( ( ps->entityEventSequence & 3 ) << 8 );
		// set external event to zero before calling BG_PlayerStateToEntityState
		extEvent = ps->externalEvent;
		ps->externalEvent = 0;
		// create temporary entity for event
		t = G_TempEntity( ps->origin, event );
		number = t->s.number;
		BG_PlayerStateToEntityState( ps, &t->s, qtrue );
		t->s.number = number;
		t->s.eType = ET_EVENTS + event;
		t->s.eFlags |= EF_PLAYER_EVENT;
		t->s.otherEntityNum = ps->clientNum;
		// send to everyone except the client who generated the event
		t->r.svFlags |= SVF_NOTSINGLECLIENT;
		t->r.singleClient = ps->clientNum;
		// set back external event
		ps->externalEvent = extEvent;
	}
}

/*
==============
ClientThink

This will be called once for each client frame, which will
usually be a couple times for each server frame on fast clients.

If "g_synchronousClients 1" is set, this will be called exactly
once for each server frame, which makes for smooth demo recording.
==============
*/
void ClientThink_real( gentity_t *ent ) {
	gclient_t	*client;
	pmove_t		pm;
	int			oldEventSequence;
	int			msec;
	usercmd_t	*ucmd;

	client = ent->client;

	// don't think if the client is not yet connected (and thus not yet spawned in)
	if (client->pers.connected != CON_CONNECTED) {
		return;
	}
	// mark the time, so the connection sprite can be removed
	ucmd = &ent->client->pers.cmd;
	client->ps.forwardmove = ucmd->forwardmove;
	client->ps.rightmove = ucmd->rightmove;
	client->ps.upmove = ucmd->upmove;

	// sanity check the command time to prevent speedup cheating
	if ( ucmd->serverTime > level.time + 200 ) {
		ucmd->serverTime = level.time + 200;
//		G_Printf("serverTime <<<<<\n" );
	}
	if ( ucmd->serverTime < level.time - 1000 ) {
		ucmd->serverTime = level.time - 1000;
//		G_Printf("serverTime >>>>>\n" );
	} 

	msec = ucmd->serverTime - client->ps.commandTime;
	// following others may result in bad times, but we still want
	// to check for follow toggles
	if ( msec < 1 && client->sess.spectatorState != SPECTATOR_FOLLOW ) {
		return;
	}
	if ( msec > 200 ) {
		msec = 200;
	}

	if ( pmove_msec.integer < 8 ) {
		trap_Cvar_Set("pmove_msec", "8");
	}
	else if (pmove_msec.integer > 33) {
		trap_Cvar_Set("pmove_msec", "33");
	}

	if ( pmove_fixed.integer || client->pers.pmoveFixed ) {
		ucmd->serverTime = ((ucmd->serverTime + pmove_msec.integer-1) / pmove_msec.integer) * pmove_msec.integer;
		//if (ucmd->serverTime - client->ps.commandTime <= 0)
		//	return;
	}

	//
	// check for exiting intermission
	//
	if ( level.intermissiontime ) {
		ClientIntermissionThink( client );
		return;
	}

	// spectators don't do much
	if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {
		if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ) {
			return;
		}
		SpectatorThink( ent, ucmd );
		return;
	}

	// check for inactivity timer, but never drop the local client of a non-dedicated server
	if ( !ClientInactivityTimer( client ) ) {
		return;
	}

	if ( !G_CheckClientFlood( ent ) ) {
		return;
	}

	// clear the rewards if time
	if ( level.time > client->rewardTime ) {
		client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
	}

	if ( client->noclip ) {
		client->ps.pm_type = PM_NOCLIP;
	} else if ( client->ps.stats[STAT_HEALTH] <= 0 ) {
		client->ps.pm_type = PM_DEAD;
	} else if ( client->freezeFrozen ) {
		client->ps.pm_type = PM_FREEZE;
	} else {
		client->ps.pm_type = PM_NORMAL;
	}

	client->ps.gravity = g_gravity.value;

	// set speed
	client->ps.speed = g_speed.value;

	if( bg_itemlist[client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_SCOUT ) {
		client->ps.speed *= 1.5;
	}
	else
	if ( client->ps.powerups[PW_HASTE] ) {
		client->ps.speed *= 1.3;
	}
	if ( g_pmoveSettings.noPlayerClip && g_pmoveSettings.velocityGh > 0.0f ) {
		client->ps.speed = g_pmoveSettings.velocityGh;
	}

	G_RRProcessClient( ent );

	// Let go of the hook if we aren't firing
	if ( client->ps.weapon == WP_GRAPPLING_HOOK &&
		client->hook && !( ucmd->buttons & BUTTON_ATTACK ) ) {
		Weapon_HookFree(client->hook);
	}

	// set up for pmove
	oldEventSequence = client->ps.eventSequence;

	memset (&pm, 0, sizeof(pm));

	// check for the hit-scan gauntlet, don't let the action
	// go through as an attack unless it actually hits something
	if ( client->ps.weapon == WP_GAUNTLET && !( ucmd->buttons & BUTTON_TALK ) &&
		( ucmd->buttons & BUTTON_ATTACK ) && client->ps.weaponTime <= 0 ) {
		pm.gauntletHit = CheckGauntletAttack( ent );
	}

	if ( ent->flags & FL_FORCE_GESTURE ) {
		ent->flags &= ~FL_FORCE_GESTURE;
		ent->client->pers.cmd.buttons |= BUTTON_GESTURE;
	}

	// check for invulnerability expansion before doing the Pmove
	if (client->ps.powerups[PW_INVULNERABILITY] ) {
		if ( !(client->ps.pm_flags & PMF_INVULEXPAND) ) {
			vec3_t mins = { -42, -42, -42 };
			vec3_t maxs = { 42, 42, 42 };
			vec3_t oldmins, oldmaxs;

			VectorCopy (ent->r.mins, oldmins);
			VectorCopy (ent->r.maxs, oldmaxs);
			// expand
			VectorCopy (mins, ent->r.mins);
			VectorCopy (maxs, ent->r.maxs);
			trap_LinkEntity(ent);
			// check if this would get anyone stuck in this player
			if ( !StuckInOtherClient(ent) ) {
				// set flag so the expanded size will be set in PM_CheckDuck
				client->ps.pm_flags |= PMF_INVULEXPAND;
			}
			// set back
			VectorCopy (oldmins, ent->r.mins);
			VectorCopy (oldmaxs, ent->r.maxs);
			trap_LinkEntity(ent);
		}
	}

	pm.ps = &client->ps;
	pm.cmd = *ucmd;
	if ( pm.ps->pm_type == PM_DEAD ) {
		pm.tracemask = MASK_PLAYERSOLID & ~CONTENTS_BODY;
	}
	else if ( ent->r.svFlags & SVF_BOT ) {
		pm.tracemask = MASK_PLAYERSOLID | CONTENTS_BOTCLIP;
	}
	else {
		pm.tracemask = MASK_PLAYERSOLID;
	}
	if ( g_pmoveSettings.noPlayerClip ) {
		pm.tracemask &= ~CONTENTS_BODY;
	}
	if ( g_playerCylinders.integer ) {
		// Quake Live player cylinder approximation:
		// When enabled, we slightly reduce the bbox size for certain checks
		// or ensure the physics engine treats it as a cylinder.
		// For now, we enforce the standard QL bbox sizes if they differ.
		VectorSet( pm.mins, -15, -15, -24 );
		VectorSet( pm.maxs, 15, 15, 32 );
	}
	pm.pmoveSettings = &g_pmoveSettings;
	pm.trace = trap_Trace;
	pm.pointcontents = trap_PointContents;
	pm.debugLevel = g_debugMove.integer;
	pm.noFootsteps = ( g_dmflags.integer & DF_NO_FOOTSTEPS ) > 0;

	pm.pmove_fixed = pmove_fixed.integer | client->pers.pmoveFixed;
	pm.pmove_msec = pmove_msec.integer;

	VectorCopy( client->ps.origin, client->oldOrigin );

		if (level.intermissionQueued != 0 && g_singlePlayer.integer) {
			if ( level.time - level.intermissionQueued >= 1000  ) {
				pm.cmd.buttons = 0;
				pm.cmd.forwardmove = 0;
				pm.cmd.rightmove = 0;
				pm.cmd.upmove = 0;
				if ( level.time - level.intermissionQueued >= 2000 && level.time - level.intermissionQueued <= 2500 ) {
					trap_SendConsoleCommand( EXEC_APPEND, "centerview\n");
				}
				ent->client->ps.pm_type = PM_SPINTERMISSION;
			}
		}
		Pmove (&pm);

	// save results of pmove
	if ( ent->client->ps.eventSequence != oldEventSequence ) {
		ent->eventTime = level.time;
	}
	BG_PlayerStateToEntityState( &ent->client->ps, &ent->s, qtrue );
	SendPendingPredictableEvents( &ent->client->ps );

	if ( !( ent->client->ps.eFlags & EF_FIRING ) ) {
		client->fireHeld = qfalse;		// for grapple
	}

	// use the snapped origin for linking so it matches client predicted versions
	VectorCopy( ent->s.pos.trBase, ent->r.currentOrigin );

	VectorCopy (pm.mins, ent->r.mins);
	VectorCopy (pm.maxs, ent->r.maxs);

	ent->waterlevel = pm.waterlevel;
	ent->watertype = pm.watertype;

	// execute client events
	ClientEvents( ent, oldEventSequence );

	// link entity now, after any personal teleporters have been used
	trap_LinkEntity (ent);
	if ( !ent->client->noclip ) {
		G_TouchTriggers( ent );
	}

	// NOTE: now copy the exact origin over otherwise clients can be snapped into solid
	VectorCopy( ent->client->ps.origin, ent->r.currentOrigin );

	//test for solid areas in the AAS file
	BotTestAAS(ent->r.currentOrigin);

	// touch other objects
	ClientImpacts( ent, &pm );

	// save results of triggers and client events
	if (ent->client->ps.eventSequence != oldEventSequence) {
		ent->eventTime = level.time;
	}

	// swap and latch button actions
	client->oldbuttons = client->buttons;
	client->buttons = ucmd->buttons;
	client->latched_buttons |= client->buttons & ~client->oldbuttons;

	// check for respawning
	if ( client->ps.stats[STAT_HEALTH] <= 0 ) {
		// wait for the attack button to be pressed
		if ( level.time > client->respawnTime ) {
			// forcerespawn is to prevent users from waiting out powerups
			if ( g_forcerespawn.integer > 0 && 
				( level.time - client->respawnTime ) > g_forcerespawn.integer * 1000 ) {
				respawn( ent );
				return;
			}
		
			// pressing attack or use is the normal respawn method
			if ( ucmd->buttons & ( BUTTON_ATTACK | BUTTON_USE_HOLDABLE ) ) {
				respawn( ent );
			}
		}
		return;
	}

	// perform once-a-second actions
	ClientTimerActions( ent, msec );
}

/*
==================
ClientThink

A new command has arrived from the client
==================
*/
void ClientThink( int clientNum ) {
	gentity_t *ent;

	ent = g_entities + clientNum;
	trap_GetUsercmd( clientNum, &ent->client->pers.cmd );

	// mark the time we got info, so we can display the
	// phone jack if they don't get any for a while
	ent->client->lastCmdTime = level.time;

	if ( !(ent->r.svFlags & SVF_BOT) && !g_synchronousClients.integer ) {
		ClientThink_real( ent );
	}
}


void G_RunClient( gentity_t *ent ) {
	if ( !(ent->r.svFlags & SVF_BOT) && !g_synchronousClients.integer ) {
		return;
	}
	ent->client->pers.cmd.serverTime = level.time;
	ClientThink_real( ent );
}


/*
==================
SpectatorClientEndFrame

==================
*/
void SpectatorClientEndFrame( gentity_t *ent ) {
	gclient_t	*cl;

	if ( level.trainingMapActive && ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
		StopFollowing( ent );
	}

	// if we are doing a chase cam or a remote view, grab the latest info
	if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
		int		clientNum, flags;

		clientNum = ent->client->sess.spectatorClient;

		// team follow1 and team follow2 go to whatever clients are playing
		if ( clientNum == -1 ) {
			clientNum = level.follow1;
		} else if ( clientNum == -2 ) {
			clientNum = level.follow2;
		}

		if ( clientNum <= -10 ) {
			// POI following
			int poiIndex = -(clientNum + 10);
			if ( poiIndex >= 0 && poiIndex < level.numPois && level.pois[poiIndex].inuse ) {
				ent->client->ps.pm_flags |= PMF_FOLLOW;
				ent->client->ps.pm_type = PM_SPECTATOR;
				ent->client->ps.clientNum = ent->s.number;
				ent->client->ps.weapon = WP_NONE;
				ent->client->ps.stats[STAT_HEALTH] = 1;
				VectorCopy( level.pois[poiIndex].origin, ent->client->ps.origin );
				VectorCopy( level.pois[poiIndex].angles, ent->client->ps.viewangles );
				VectorCopy( level.pois[poiIndex].angles, ent->s.angles );
				return;
			} else {
				// POI gone?
				ent->client->sess.spectatorState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;
				ent->client->sess.spectatorClient = -1;
				if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
					ClientBegin( ent->client - level.clients );
				}
			}
		} else if ( clientNum >= 0 ) {
			cl = &level.clients[ clientNum ];
			if ( cl->pers.connected == CON_CONNECTED && cl->sess.sessionTeam != TEAM_SPECTATOR ) {
				flags = (cl->ps.eFlags & ~(EF_VOTED | EF_TEAMVOTED)) | (ent->client->ps.eFlags & (EF_VOTED | EF_TEAMVOTED));
				ent->client->ps = cl->ps;
				ent->client->ps.pm_flags |= PMF_FOLLOW;
				ent->client->ps.eFlags = flags;
				return;
			} else {
				// drop them to free spectators unless they are dedicated camera followers
				if ( ent->client->sess.spectatorClient >= 0 ) {
				ent->client->sess.spectatorState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;
				ent->client->sess.spectatorClient = -1;
				if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
					ClientBegin( ent->client - level.clients );
				}
				}
			}
		}
	}

	if ( ent->client->sess.spectatorState == SPECTATOR_SCOREBOARD ) {
		ent->client->ps.pm_flags |= PMF_SCOREBOARD;
	} else {
		ent->client->ps.pm_flags &= ~PMF_SCOREBOARD;
	}
}

/*
==============
ClientEndFrame

Called at the end of each server frame for each connected client
A fast client will have multiple ClientThink for each ClientEdFrame,
while a slow client may have multiple ClientEndFrame between ClientThink.
==============
*/
void ClientEndFrame( gentity_t *ent ) {
	int			i;
	clientPersistant_t	*pers;

	if ( ent->client->complaintClient >= 0 && ent->client->complaintEndTime > 0 && ent->client->complaintEndTime <= level.time ) {
		G_ComplaintResolve( ent, qfalse );
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR
		|| ( ( g_gametype.integer == GT_CLAN_ARENA || g_gametype.integer == GT_ATTACK_DEFEND )
			&& ent->client->ps.pm_type == PM_SPECTATOR ) ) {
		SpectatorClientEndFrame( ent );
		return;
	}

	pers = &ent->client->pers;
	if ( pers->ratingMetadataLoaded ) {
		G_RefreshClientRatingModifiers( ent->client );
	}
	G_FreezeClientEndFrame( ent );
	G_RankAccumulateWeaponTime( ent );

	// turn off any expired powerups
	for ( i = 0 ; i < MAX_POWERUPS ; i++ ) {
		if ( ent->client->ps.powerups[ i ] < level.time ) {
			ent->client->ps.powerups[ i ] = 0;
		}
	}

	// set powerup for player animation
	if( bg_itemlist[ent->client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_GUARD ) {
		ent->client->ps.powerups[PW_GUARD] = level.time;
	}
	if( bg_itemlist[ent->client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_SCOUT ) {
		ent->client->ps.powerups[PW_SCOUT] = level.time;
	}
	if( bg_itemlist[ent->client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_DOUBLER ) {
		ent->client->ps.powerups[PW_DOUBLER] = level.time;
	}
	if( bg_itemlist[ent->client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_AMMOREGEN ) {
		ent->client->ps.powerups[PW_AMMOREGEN] = level.time;
	}
	if ( ent->client->invulnerabilityTime > level.time ) {
		ent->client->ps.powerups[PW_INVULNERABILITY] = level.time;
	}
	{
		const gitem_t	*invulnerabilityItem;
		int				invulnerabilityItemNum;

		invulnerabilityItem = BG_FindItemForHoldable( HI_INVULNERABILITY );
		invulnerabilityItemNum = invulnerabilityItem ? (int)( invulnerabilityItem - bg_itemlist ) : 0;

		if ( ent->client->holdableInvulnerabilityTime > level.time ) {
			ent->client->ps.playerItemTimeMax = 10000;
			ent->client->ps.playerItemTime = ent->client->holdableInvulnerabilityTime - level.time;
			if ( invulnerabilityItemNum != 0 && ent->client->ps.stats[STAT_HOLDABLE_ITEM] == 0 ) {
				ent->client->ps.stats[STAT_HOLDABLE_ITEM] = invulnerabilityItemNum;
			}
		} else {
			if ( invulnerabilityItemNum != 0 &&
				ent->client->ps.stats[STAT_HOLDABLE_ITEM] == invulnerabilityItemNum &&
				ent->client->ps.playerItemTimeMax > 0 ) {
				ent->client->ps.stats[STAT_HOLDABLE_ITEM] = 0;
			}
			ent->client->holdableInvulnerabilityTime = 0;
			ent->client->ps.playerItemTimeMax = 0;
			ent->client->ps.playerItemTime = 0;
		}
	}

	// save network bandwidth
#if 0
	if ( !g_synchronousClients->integer && ent->client->ps.pm_type == PM_NORMAL ) {
		// FIXME: this must change eventually for non-sync demo recording
		VectorClear( ent->client->ps.viewangles );
	}
#endif

	//
	// If the end of unit layout is displayed, don't give
	// the player any normal movement attributes
	//
	if ( level.intermissiontime ) {
		return;
	}

	// burn from lava, etc
	P_WorldEffects (ent);

	// apply all the damage taken this frame
	P_DamageFeedback (ent);

	// add the EF_CONNECTION flag if we haven't gotten commands recently
	if ( level.time - ent->client->lastCmdTime > 1000 ) {
		ent->s.eFlags |= EF_CONNECTION;
	} else {
		ent->s.eFlags &= ~EF_CONNECTION;
	}

	ent->client->ps.stats[STAT_HEALTH] = ent->health;	// FIXME: get rid of ent->health...

	G_SetClientSound (ent);

	// set the latest infor
	BG_PlayerStateToEntityState( &ent->client->ps, &ent->s, qtrue );
	SendPendingPredictableEvents( &ent->client->ps );

	// set the bit for the reachability area the client is currently in
//	i = trap_AAS_PointReachabilityAreaIndex( ent->client->ps.origin );
//	ent->client->areabits[i >> 3] |= 1 << (i & 7);

	G_StoreHistory( ent );
}

/*
=============
G_Frame_BeginRoundWarmup

Transitions the round controller into the warmup state.
=============
*/
static void G_FreezeScheduleWarmupDelay( void );
static void G_FreezeResetClientsForRound( qboolean warmup );
static int G_FreezeResolveRoundState( void );
static int Freeze_RoundStateTransition( qboolean announce );
static void G_RRSeedInfectionTeams( void );
static void G_RRInitRoundController( void );
static int RR_RoundStateTransition( qboolean announce );
static qboolean G_Frame_CheckRoundLimit( void );
void G_Frame_BeginRoundWarmup( void ) {
	level.roundState = ROUNDSTATE_WARMUP;
	level.roundTransitionTime = ROUND_TRANSITION_NONE;
	level.roundStartTime = level.time;
	G_RRResetRoundState();
	if ( G_FreezeGametypeEnabled() ) {
		G_FreezeSyncCvars();
		G_FreezeResetClientsForRound( qtrue );
		G_FreezeScheduleWarmupDelay();
	}
	G_UpdateMatchStateConfigString();
}

/*
=============
G_RoundControllerGametypeEnabled

Returns qtrue when the round controller should run for the active gametype.
=============
*/
static qboolean G_RoundControllerGametypeEnabled( void ) {
	switch ( g_gametype.integer ) {
	case GT_CLAN_ARENA:
	case GT_ATTACK_DEFEND:
	case GT_RED_ROVER:
	case GT_FREEZE:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=============
G_ADShouldTimeoutActiveRound

Returns qtrue when the retail Attack & Defend active round should end on
roundtimelimit rather than elimination or objective capture.
=============
*/
static qboolean G_ADShouldTimeoutActiveRound( const int counts[TEAM_NUM_TEAMS] ) {
	int	attackingTeam;
	int	defendingTeam;

	if ( !counts ) {
		return qfalse;
	}

	attackingTeam = G_ADResolveAttackingTeam();
	defendingTeam = G_ADResolveDefendingTeam();
	if ( attackingTeam <= TEAM_FREE || defendingTeam <= TEAM_FREE ) {
		return qfalse;
	}

	if ( counts[attackingTeam] <= 0 || counts[defendingTeam] <= 0 ) {
		return qfalse;
	}

	if ( level.adRoundWinnerAlreadyScored ) {
		return qfalse;
	}

	if ( roundtimelimit.integer <= 0 ) {
		return qfalse;
	}

	return ( level.time - level.adStateChangeTime ) >= roundtimelimit.integer * 1000;
}

/*
=============
G_Frame_UpdateAttackDefendRoundController

Runs the Attack & Defend retail controller and advances round outcomes once a
side is eliminated or the active round times out.
=============
*/
static void G_Frame_UpdateAttackDefendRoundController( void ) {
	int		state;
	int		counts[TEAM_NUM_TEAMS];
	int		attackingTeam;
	int		defendingTeam;
	team_t	winner;

	if ( !Team_HasMinimumPlayersForWarmup() ) {
		if ( level.adRoundState != AD_ROUNDSTATE_INACTIVE
			|| level.roundState != ROUNDSTATE_INACTIVE
			|| level.roundTransitionTime != ROUND_TRANSITION_NONE ) {
			level.roundState = ROUNDSTATE_INACTIVE;
			level.adRoundState = AD_ROUNDSTATE_INACTIVE;
			level.adPendingRoundState = AD_ROUNDSTATE_INACTIVE;
			level.roundTransitionTime = ROUND_TRANSITION_NONE;
			level.adTurnIndex = 0;
			level.adRoundWinner = TEAM_FREE;
			level.adRoundWinnerAlreadyScored = qfalse;
			level.adStateChangeTime = level.time;
			if ( level.roundNumber <= 0 ) {
				level.roundNumber = 1;
			}
			G_ADResetScoreHistory();
			G_UpdateMatchStateConfigString();
		}
		return;
	}

	if ( level.roundNumber <= 0 ) {
		level.roundNumber = 1;
	}

	state = G_ADResolveRoundState();
	if ( state == AD_ROUNDSTATE_INACTIVE ) {
		level.adRoundState = AD_ROUNDSTATE_WARMUP;
		AD_RoundStateTransition( qtrue );
		return;
	}

	if ( state != AD_ROUNDSTATE_ACTIVE ) {
		return;
	}

	attackingTeam = G_ADResolveAttackingTeam();
	defendingTeam = G_ADResolveDefendingTeam();
	if ( attackingTeam <= TEAM_FREE || defendingTeam <= TEAM_FREE ) {
		return;
	}

	G_CountActivePlayersByTeam( counts );
	winner = TEAM_FREE;
	if ( counts[attackingTeam] <= 0 && counts[defendingTeam] > 0 ) {
		winner = defendingTeam;
	} else if ( counts[defendingTeam] <= 0 && counts[attackingTeam] > 0 ) {
		winner = attackingTeam;
	}

	if ( winner == TEAM_FREE && !G_ADShouldTimeoutActiveRound( counts ) ) {
		return;
	}

	level.adRoundWinner = winner;
	level.adRoundWinnerAlreadyScored = qfalse;
	level.adRoundState = AD_ROUNDSTATE_COMPLETE;
	AD_RoundStateTransition( qtrue );
}

/*
=============
G_Frame_BeginRoundActive

Transitions the controller into the active state and records timing data.
=============
*/
static void G_Frame_BeginRoundActive( void ) {
	level.roundState = ROUNDSTATE_ACTIVE;
	level.roundTransitionTime = ROUND_TRANSITION_NONE;
	level.roundStartTime = level.time;
	level.roundNumber++;
	if ( G_FreezeGametypeEnabled() ) {
		G_FreezeSyncCvars();
		G_FreezeResetClientsForRound( qfalse );
	}
	G_UpdateMatchStateConfigString();
}

/*
============
G_FreezeGametypeEnabled

Returns qtrue when the freeze ruleset should run for the active gametype.
============
*/
qboolean G_FreezeGametypeEnabled( void ) {
	return ( g_gametype.integer == GT_FREEZE ) ? qtrue : qfalse;
}

/*
============
G_FreezeResolveRoundState

Returns the active Freeze round-state view consumed by the retail controller helpers.
============
*/
static int G_FreezeResolveRoundState( void ) {
	if ( !G_FreezeGametypeEnabled() ) {
		return ROUNDSTATE_INACTIVE;
	}

	return level.roundState;
}

/*
=============
G_FreezeSyncCvars

Copies the current freeze-related CVars into the cached level state.
=============
*/
void G_FreezeSyncCvars( void ) {
	freezeRoundConfig_t	*config;

	config = &level.freezeConfig;
	config->thawTime = g_freezeThawTime.integer;
	if ( config->thawTime <= 0 ) {
		config->thawTime = 2000;
	}
	config->thawTick = g_freezeThawTick.integer;
	if ( config->thawTick <= 0 ) {
		config->thawTick = config->thawTime;
	}
	if ( config->thawTick <= 0 ) {
		config->thawTick = 100;
	}
	config->thawRadius = g_freezeThawRadius.integer;
	if ( config->thawRadius <= 0 ) {
		config->thawRadius = 96;
	}
	config->thawThroughSurface = g_freezeThawThroughSurface.integer ? qtrue : qfalse;
	config->thawWinningTeam = g_freezeThawWinningTeam.integer ? qtrue : qfalse;
	config->roundDelay = g_freezeRoundDelay.integer;
	if ( config->roundDelay < 0 ) {
		config->roundDelay = 0;
	}
	config->resetWeapons = g_freezeResetWeaponsOnRound.integer ? qtrue : qfalse;
	config->resetHealth = g_freezeResetHealthOnRound.integer ? qtrue : qfalse;
	config->resetArmor = g_freezeResetArmorOnRound.integer ? qtrue : qfalse;
	config->removePowerups = g_freezeRemovePowerupsOnRound.integer ? qtrue : qfalse;
	config->protectedSpawnTime = ( g_freezeProtectedSpawnTime.integer > 0 )
		? g_freezeProtectedSpawnTime.integer : 0;
	config->environmentalRespawnDelay = ( g_freezeEnvironmentalRespawnDelay.integer > 0 )
		? g_freezeEnvironmentalRespawnDelay.integer : 0;
	config->autoThawTime = ( g_freezeAutoThawTime.integer > 0 )
		? g_freezeAutoThawTime.integer : 0;
}

/*
============
G_FreezeScheduleWarmupDelay

Applies the configured warmup delay ahead of the next active freeze round.
============
*/
static void G_FreezeScheduleWarmupDelay( void ) {
	int			delay;

	if ( !G_FreezeGametypeEnabled() ) {
		return;
	}

	delay = g_roundWarmupDelay.integer;
	if ( delay > 0 ) {
		level.warmupTime = level.time + delay;
		trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
		G_UpdateReadyUpConfigstring();
		return;
	}

	level.warmupTime = 0;
	trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
	G_UpdateReadyUpConfigstring();
}

/*
=============
G_FreezeHandleWarmupDelayCvarUpdate

Reschedules the warmup countdown whenever g_roundWarmupDelay changes mid-warmup.
=============
*/
void G_FreezeHandleWarmupDelayCvarUpdate( void ) {
	if ( !G_FreezeGametypeEnabled() ) {
		return;
	}

	if ( level.roundState != ROUNDSTATE_WARMUP ) {
		return;
	}

	if ( level.warmupTime <= 0 ) {
		return;
	}

	G_FreezeScheduleWarmupDelay();
}

/*
============
G_FreezeResetClientsForRound

Respawns or restores each player before a freeze round begins.
============
*/
static void G_FreezeThawWinningPlayers( team_t winner );

/*
============
G_FreezeResetClientForRound

Respawns or restores one player before the next Freeze round begins.
============
*/
static void G_FreezeResetClientForRound( gentity_t *ent, qboolean warmup ) {
	if ( !ent || !ent->client ) {
		return;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	if ( level.freezeConfig.resetWeapons ) {
		G_RequestClientSpawn( ent, warmup, qfalse );
		return;
	}

	G_FreezeInitClient( ent );
	ent->client->freezeFrozen = qfalse;
	ent->client->ps.pm_type = PM_NORMAL;
	ent->client->respawnTime = level.time;
	ent->takedamage = qtrue;
	if ( level.freezeConfig.resetHealth ) {
		ent->health = ent->client->ps.stats[STAT_MAX_HEALTH];
		ent->client->ps.stats[STAT_HEALTH] = ent->health;
	}
	if ( level.freezeConfig.resetArmor ) {
		ent->client->ps.stats[STAT_ARMOR] = g_factoryCvarConfig.startingArmor;
		BG_UpdateArmorTierFromCurrentArmor( &ent->client->ps, g_armorTiered.integer ? qtrue : qfalse );
	}
	if ( level.freezeConfig.removePowerups ) {
		memset( ent->client->ps.powerups, 0, sizeof( ent->client->ps.powerups ) );
	}
}

static void G_FreezeResetClientsForRound( qboolean warmup ) {
	int			clientNum;

	if ( !G_FreezeGametypeEnabled() ) {
		return;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*ent;

		ent = &g_entities[clientNum];
		if ( !ent->inuse || !ent->client ) {
			continue;
		}
		G_FreezeResetClientForRound( ent, warmup );
	}
}

/*
============
G_TotalLivingHealthByTeam

Sums the living health pool for the specified Freeze team.
============
*/
static int G_TotalLivingHealthByTeam( team_t team ) {
	int		clientNum;
	int		totalHealth;

	totalHealth = 0;
	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return 0;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*ent;
		gclient_t	*client;

		ent = &g_entities[clientNum];
		client = ent->client;
		if ( !ent->inuse || !client ) {
			continue;
		}
		if ( client->pers.connected == CON_DISCONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != team ) {
			continue;
		}
		if ( client->ps.pm_type != PM_NORMAL ) {
			continue;
		}
		if ( ent->health > 0 ) {
			totalHealth += ent->health;
		}
	}

	return totalHealth;
}

/*
============
G_FreezeRecountLivingClients

Rebuilds the cached living-player and health tallies for each team.
============
*/
static void G_FreezeRecountLivingClients( void ) {
	int			team;

	G_CountActivePlayersByTeam( level.freezeLivingCount );
	for ( team = 0; team < TEAM_NUM_TEAMS; team++ ) {
		level.freezeLivingHealth[team] = 0;
	}
	level.freezeLivingHealth[TEAM_RED] = G_TotalLivingHealthByTeam( TEAM_RED );
	level.freezeLivingHealth[TEAM_BLUE] = G_TotalLivingHealthByTeam( TEAM_BLUE );
}

/*
============
G_FreezeTeamIsFullyFrozen

Returns qtrue once a Freeze team no longer has any unfrozen live members.
============
*/
static qboolean G_FreezeTeamIsFullyFrozen( team_t team ) {
	int		clientNum;

	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return qfalse;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*ent;
		gclient_t	*client;

		ent = &g_entities[clientNum];
		client = ent->client;
		if ( !ent->inuse || !client ) {
			continue;
		}
		if ( client->pers.connected == CON_DISCONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != team ) {
			continue;
		}
		if ( client->ps.pm_type == PM_DEAD ) {
			continue;
		}
		if ( !client->freezeFrozen ) {
			return qfalse;
		}
	}

	return qtrue;
}

/*
============
G_FreezeEvaluateRoundWinner

Returns the winning team once only one side has living players left.
============
*/
static team_t G_FreezeEvaluateRoundWinner( void ) {
	qboolean	redFrozen;
	qboolean	blueFrozen;
	team_t		winner;

	G_FreezeRecountLivingClients();
	redFrozen = G_FreezeTeamIsFullyFrozen( TEAM_RED );
	blueFrozen = G_FreezeTeamIsFullyFrozen( TEAM_BLUE );

	if ( redFrozen == blueFrozen ) {
		return TEAM_FREE;
	}
	winner = redFrozen ? TEAM_BLUE : TEAM_RED;
	if ( level.freezeConfig.thawWinningTeam ) {
		G_FreezeThawWinningPlayers( winner );
	}
	return winner;
}

/*
============
G_FreezeThawWinningPlayers

Automatically thaws members of the winning team when configured.
============
*/
static void G_FreezeThawWinningPlayers( team_t winner ) {
	int		clientNum;

	if ( !level.freezeConfig.thawWinningTeam ) {
		return;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*ent;
		gclient_t	*client;

		ent = &g_entities[clientNum];
		client = ent->client;
		if ( !ent->inuse || !client ) {
			continue;
		}
		if ( client->sess.sessionTeam != winner ) {
			continue;
		}
		if ( !client->freezeFrozen ) {
			continue;
		}

		G_FreezeThawClient( ent, qtrue, -1 );
	}
}

/*
============
G_FreezeHandleRoundEnd

Publishes configstrings and announcements when a freeze round completes.
============
*/
static void G_FreezeHandleRoundEnd( team_t winner ) {
	int			delay;
	const char	*winnerName;

	if ( winner != TEAM_RED && winner != TEAM_BLUE ) {
		return;
	}

	level.teamScores[winner]++;
	trap_SetConfigstring( CS_SCORES1, va( "%i", level.teamScores[TEAM_RED] ) );
	trap_SetConfigstring( CS_SCORES2, va( "%i", level.teamScores[TEAM_BLUE] ) );
	winnerName = ( winner == TEAM_RED ) ? "Red" : "Blue";
	trap_SendServerCommand( -1, va( "cp \"%s team wins the round\\n\"", winnerName ) );
	if ( g_roundDrawLivingCount.integer ) {
		trap_SendServerCommand( -1, va( "print \"Living players - Red: %i  Blue: %i\\n\"",
			level.freezeLivingCount[TEAM_RED], level.freezeLivingCount[TEAM_BLUE] ) );
	}
	if ( g_roundDrawHealthCount.integer ) {
		trap_SendServerCommand( -1, va( "print \"Total health - Red: %i  Blue: %i\\n\"",
			level.freezeLivingHealth[TEAM_RED], level.freezeLivingHealth[TEAM_BLUE] ) );
	}
	level.roundState = ROUNDSTATE_COMPLETE;
	delay = level.freezeConfig.roundDelay;
	level.roundTransitionTime = ( delay > 0 ) ? level.time + delay : level.time;
	G_UpdateMatchStateConfigString();
}

/*
=============
Freeze_RoundStateTransition

Runs the retail-style Freeze controller transition for the current internal state.
=============
*/
static int Freeze_RoundStateTransition( qboolean announce ) {
	(void)announce;

	if ( !G_FreezeGametypeEnabled() ) {
		return level.roundState;
	}

	switch ( G_FreezeResolveRoundState() ) {
	case ROUNDSTATE_INACTIVE:
		G_Frame_BeginRoundWarmup();
		break;

	case ROUNDSTATE_WARMUP:
		if ( g_gametype.integer >= GT_TEAM && !Team_HasMinimumPlayersForWarmup() ) {
			if ( level.warmupTime != -1 ) {
				level.warmupTime = -1;
				trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
				G_UpdateReadyUpConfigstring();
				G_LogPrintf( "Warmup:\n" );
			}
			break;
		}

		if ( level.warmupTime < 0 ) {
			G_FreezeScheduleWarmupDelay();
			break;
		}

		Team_ClampWarmupToShuffleCountdown();
		if ( level.warmupTime == 0 ) {
			G_Frame_BeginRoundActive();
		}
		break;

	case ROUNDSTATE_COMPLETE:
		if ( G_Frame_CheckRoundLimit() ) {
			break;
		}
		if ( level.roundTransitionTime == 0 ) {
			G_Frame_BeginRoundWarmup();
			break;
		}
		if ( level.roundTransitionTime > 0 && level.time >= level.roundTransitionTime ) {
			G_Frame_BeginRoundWarmup();
		}
		break;

	default:
		break;
	}

	return level.roundState;
}

/*
=============
G_Frame_CheckRoundLimit

Ends the match when the configured round limit has been reached.
=============
*/
static qboolean G_Frame_CheckRoundLimit( void ) {
	if ( roundlimit.integer <= 0 ) {
		return qfalse;
}

	if ( level.roundNumber < roundlimit.integer ) {
		return qfalse;
}

	trap_SendServerCommand( -1, "print \"Round limit hit.\n\"" );
	LogExit( "Round limit hit." );
	return qtrue;
}

/*
=============
G_RRSeedInfectionTeams

Reapplies the retail Red Rover infection role split from the active team assignments.
=============
*/
static void G_RRSeedInfectionTeams( void ) {
	gentity_t	*infectedClient;
	int		clientNum;
	int		infectedClientNum;

	if ( g_gametype.integer != GT_RED_ROVER || !g_rrInfected.integer ) {
		return;
	}

	infectedClientNum = -1;
	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gentity_t	*ent;

		ent = &g_entities[clientNum];
		if ( !ent->inuse || !ent->client ) {
			continue;
		}
		if ( ent->client->pers.connected == CON_DISCONNECTED ) {
			continue;
		}
		if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}

		if ( ent->client->sess.sessionTeam == TEAM_RED ) {
			ent->client->sess.sessionTeam = TEAM_BLUE;
			ent->client->sess.teamLeader = qfalse;
			G_RRInitClient( ent );
			ClientUserinfoChanged( clientNum );
		}
	}

	if ( level.rrCarryoverInfectedClientNum >= 0
		&& level.rrCarryoverInfectedClientNum < level.maxclients ) {
		gentity_t	*carryoverClient;

		carryoverClient = &g_entities[level.rrCarryoverInfectedClientNum];
		if ( carryoverClient->inuse && carryoverClient->client
			&& carryoverClient->client->pers.connected == CON_CONNECTED
			&& carryoverClient->client->sess.sessionTeam == TEAM_BLUE ) {
			infectedClientNum = level.rrCarryoverInfectedClientNum;
		}
	}

	if ( infectedClientNum < 0 && level.numPlayingClients > 0 ) {
		infectedClientNum = level.sortedClients[rand() % level.numPlayingClients];
	}

	level.rrSelectedInfectedClientNum = infectedClientNum;
	if ( infectedClientNum < 0 || infectedClientNum >= level.maxclients ) {
		return;
	}

	infectedClient = &g_entities[infectedClientNum];
	if ( !infectedClient->inuse || !infectedClient->client ) {
		return;
	}
	if ( infectedClient->client->pers.connected == CON_DISCONNECTED ) {
		return;
	}
	if ( infectedClient->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	if ( infectedClient->client->sess.sessionTeam != TEAM_RED ) {
		infectedClient->client->sess.sessionTeam = TEAM_RED;
		infectedClient->client->sess.teamLeader = qfalse;
		G_RRInitClient( infectedClient );
		ClientUserinfoChanged( infectedClientNum );
		return;
	}

	G_RRInitClient( infectedClient );
}

/*
=============
G_RRInitRoundController

Initializes the Red Rover round controller whenever the mode enters a new round phase.
=============
*/
static void G_RRInitRoundController( void ) {
	if ( g_gametype.integer != GT_RED_ROVER ) {
		return;
	}

	level.roundStartTime = level.time;
	G_RRSeedInfectionTeams();
	level.rrCarryoverInfectedClientNum = -1;
	level.rrLastInfectionTime = level.time;
	level.rrNextSurvivalBonusTime = 0;
	level.rrPendingMatchExit = qfalse;
}

/*
=============
RR_RoundStateTransition

Runs the retail-style Red Rover round controller for the current state.
=============
*/
static int RR_RoundStateTransition( qboolean announce ) {
	(void)announce;

	if ( g_gametype.integer != GT_RED_ROVER ) {
		return level.roundState;
	}

	switch ( level.roundState ) {
	case ROUNDSTATE_INACTIVE:
		G_Frame_BeginRoundWarmup();
		break;

	case ROUNDSTATE_WARMUP:
		if ( g_gametype.integer >= GT_TEAM && !Team_HasMinimumPlayersForWarmup() ) {
			if ( level.warmupTime != -1 ) {
				level.warmupTime = -1;
				trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
				G_UpdateReadyUpConfigstring();
				G_LogPrintf( "Warmup:\n" );
			}
			break;
		}

		if ( level.warmupTime < 0 ) {
			break;
		}

		Team_ClampWarmupToShuffleCountdown();
		if ( level.warmupTime == 0 ) {
			G_Frame_BeginRoundActive();
			G_RRInitRoundController();
		}
		break;

	case ROUNDSTATE_ACTIVE:
		G_RRTrackRoundActivity();
		break;

	case ROUNDSTATE_COMPLETE:
		if ( level.roundTransitionTime == 0 ) {
			G_Frame_BeginRoundWarmup();
			break;
		}
		if ( level.roundTransitionTime > 0 && level.time >= level.roundTransitionTime ) {
			if ( level.rrPendingMatchExit ) {
				if ( !G_RRCheckExitRules( qtrue ) ) {
					level.rrPendingMatchExit = qfalse;
					G_Frame_BeginRoundWarmup();
				}
			} else {
				G_Frame_BeginRoundWarmup();
			}
		}
		break;

	default:
		break;
	}

	return level.roundState;
}

/*
=============
G_Frame_UpdateRoundController

Runs per-frame updates for the round controller state machine.
=============
*/
void G_Frame_UpdateRoundController( void ) {
	if ( !G_RoundControllerGametypeEnabled() ) {
		if ( level.roundState != ROUNDSTATE_INACTIVE || level.roundTransitionTime != ROUND_TRANSITION_NONE ) {
			level.roundState = ROUNDSTATE_INACTIVE;
			level.roundTransitionTime = ROUND_TRANSITION_NONE;
			G_UpdateMatchStateConfigString();
		}
		return;
	}

	if ( g_gametype.integer == GT_ATTACK_DEFEND ) {
		G_Frame_UpdateAttackDefendRoundController();
		G_FreezeRunFrame();
		return;
	}

	if ( g_gametype.integer == GT_RED_ROVER ) {
		RR_RoundStateTransition( qtrue );
		G_FreezeRunFrame();
		return;
	}

	if ( g_gametype.integer == GT_FREEZE ) {
		Freeze_RoundStateTransition( qtrue );
		G_FreezeRunFrame();
		return;
	}

	switch ( level.roundState ) {
		case ROUNDSTATE_INACTIVE:
			G_Frame_BeginRoundWarmup();
			break;

	case ROUNDSTATE_WARMUP:
		if ( g_gametype.integer >= GT_TEAM && !Team_HasMinimumPlayersForWarmup() ) {
			if ( level.warmupTime != -1 ) {
				level.warmupTime = -1;
				trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
				G_UpdateReadyUpConfigstring();
				G_LogPrintf( "Warmup:\n" );
			}
			break;
		}

		if ( level.warmupTime < 0 ) {
			G_FreezeScheduleWarmupDelay();
			break;
		}

		Team_ClampWarmupToShuffleCountdown();
		if ( level.warmupTime == 0 ) {
			G_Frame_BeginRoundActive();
		}
		break;

		case ROUNDSTATE_ACTIVE:
			if ( g_gametype.integer == GT_RED_ROVER ) {
				G_RRTrackRoundActivity();
			}
			break;

		case ROUNDSTATE_COMPLETE:
			if ( G_Frame_CheckRoundLimit() ) {
				break;
			}
			if ( level.roundTransitionTime == 0 ) {
				G_Frame_BeginRoundWarmup();
				break;
			}

			if ( level.roundTransitionTime > 0 && level.time >= level.roundTransitionTime ) {
				G_Frame_BeginRoundWarmup();
			}
			break;

		default:
			break;
	}

	G_FreezeRunFrame();
}

/*
============
G_FreezeRunFrame

Monitors freeze-specific timers and round completion.
============
*/
void G_FreezeRunFrame( void ) {
	team_t	winner;

	if ( !G_FreezeGametypeEnabled() ) {
		return;
	}

	if ( G_FreezeResolveRoundState() == ROUNDSTATE_WARMUP ) {
		if ( level.warmupTime > 0 && level.time >= level.warmupTime ) {
			level.warmupTime = 0;
			trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
			G_UpdateReadyUpConfigstring();
		}
		return;
	}

	if ( G_FreezeResolveRoundState() != ROUNDSTATE_ACTIVE ) {
		return;
	}

	winner = G_FreezeEvaluateRoundWinner();
	if ( winner == TEAM_FREE ) {
		return;
	}

	G_FreezeHandleRoundEnd( winner );
}

