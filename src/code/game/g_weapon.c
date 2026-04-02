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
// g_weapon.c 
// perform the server side effects of a weapon firing

#include "g_local.h"

static	float	s_quadFactor;
static	vec3_t	forward, right, up;
static	vec3_t	muzzle;

/*
=============
G_GetMachinegunIronsightScale

Returns the sanitized Quake Live machinegun tight-spread scalar.
=============
*/
static float G_GetMachinegunIronsightScale( void ) {
	float	scale;

	scale = g_weaponConfig.machinegunIronsightsScale;
	if ( scale <= 0.0f ) {
		scale = 1.0f;
	}

	return scale;
}

/*
=============
G_PlayerUsesMachinegunTightSpread

Retail applies g_ironsights_mg when the firing machinegun player is ducked.
=============
*/
static qboolean G_PlayerUsesMachinegunTightSpread( const gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return qfalse;
	}

	if ( ent->s.weapon != WP_MACHINEGUN ) {
		return qfalse;
	}

	return ( ent->client->ps.pm_flags & PMF_DUCKED ) ? qtrue : qfalse;
}

/*
=============
G_GetMuzzleForwardOffset

Returns the retail forward muzzle offset based on the player's crouch state.
=============
*/
static float G_GetMuzzleForwardOffset( const gentity_t *ent ) {
	if ( ent && ent->client && ( ent->client->ps.pm_flags & PMF_DUCKED ) ) {
		return 3.0f;
	}

	return 5.0f;
}

/*
=============
G_WeaponUsesLagHaxTimeshift

Returns qtrue for the hidden retail hitscan weapon set that brackets traces
with the lag-hax rewind helpers.
=============
*/
static qboolean G_WeaponUsesLagHaxTimeshift( weapon_t weapon ) {
	switch ( weapon ) {
	case WP_MACHINEGUN:
	case WP_HEAVY_MACHINEGUN:
	case WP_SHOTGUN:
	case WP_LIGHTNING:
	case WP_RAILGUN:
	case WP_CHAINGUN:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=============
G_GetChaingunSpread

Returns the retail chaingun spread derived from the current weaponTime spin-up.
=============
*/
static float G_GetChaingunSpread( const gentity_t *ent ) {
	float	weaponTime;
	float	spread;

	if ( !ent || !ent->client ) {
		return 700.0f;
	}

	weaponTime = ( float )ent->client->ps.weaponTime;
	if ( weaponTime < 0.0f ) {
		weaponTime = 0.0f;
	} else if ( weaponTime > 1000.0f ) {
		weaponTime = 1000.0f;
	}

	spread = 700.0f + ( weaponTime / 1000.0f ) * 700.0f;
	if ( spread < 700.0f ) {
		spread = 700.0f;
	} else if ( spread > 1400.0f ) {
		spread = 1400.0f;
	}

	return spread;
}

/*
=============
G_RoundFloatToInt

Rounds floating-point values to the nearest integer to mirror retail qagame helper usage.
=============
*/
static int G_RoundFloatToInt( float value ) {
	if ( value >= 0.0f ) {
		return (int)( value + 0.5f );
	}

	return (int)( value - 0.5f );
}

/*
=============
G_GetLightningDamageForDistance

Applies the retail lightning gun damage falloff steps based on beam distance.
=============
*/
static int G_GetLightningDamageForDistance( float distance ) {
	int	baseDamage;
	int	distancePastFalloff;
	int	falloffDamage;
	int	falloffRange;

	baseDamage = g_weaponConfig.lightningDamage;
	falloffDamage = g_weaponConfig.lightningFalloffDamage;
	falloffRange = g_weaponConfig.lightningFalloffRange;
	if ( falloffDamage <= 0 || falloffRange <= 0 ) {
		return baseDamage;
	}

	distancePastFalloff = G_RoundFloatToInt( distance - falloffRange );
	while ( distancePastFalloff > 0 ) {
		baseDamage -= falloffDamage;
		distancePastFalloff -= falloffRange;
	}

	if ( baseDamage < 1 ) {
		return 1;
	}

	return baseDamage;
}

/*
=============
G_ApplyRailJump

Applies the retail rail jump impulse when solid geometry is close to the muzzle.
=============
*/
static void G_ApplyRailJump( gentity_t *ent ) {
	trace_t	trace;
	vec3_t	end;
	vec3_t	pushDir;
	int		railJumpStrength;

	if ( !ent || !ent->client ) {
		return;
	}

	railJumpStrength = g_weaponConfig.railJumpStrength;
	if ( railJumpStrength <= 0 ) {
		return;
	}

	VectorMA( muzzle, 120.0f, forward, end );
	trap_Trace( &trace, muzzle, NULL, NULL, end, ent->s.number, CONTENTS_SOLID );
	if ( trace.fraction == 1.0f ) {
		return;
	}

	VectorCopy( forward, pushDir );
	VectorNormalize( pushDir );

	ent->client->ps.velocity[0] -= railJumpStrength * pushDir[0];
	ent->client->ps.velocity[1] -= railJumpStrength * pushDir[1];
	ent->client->ps.velocity[2] -= railJumpStrength * pushDir[2];
	ent->client->ps.velocity[2] += 20.0f;
}

/*
=============
G_GetShotgunPelletOffsets

Builds the deterministic 20-pellet Quake Live shotgun pattern.
=============
*/
static void G_GetShotgunPelletOffsets( int pelletIndex, float *r, float *u ) {
	float	angle;
	float	radius;

	if ( !r || !u ) {
		return;
	}

	if ( pelletIndex < 6 ) {
		angle = pelletIndex * 60.0f;
		radius = 4000.0f;
	} else if ( pelletIndex < 12 ) {
		angle = ( pelletIndex - 6 ) * 60.0f + 30.0f;
		radius = 8000.0f;
	} else {
		angle = ( pelletIndex - 12 ) * 45.0f;
		radius = 12000.0f;
	}

	*r = radius * cos( DEG2RAD( angle ) );
	*u = radius * sin( DEG2RAD( angle ) );
}

#define NUM_NAILSHOTS 15

/*
================
G_BounceProjectile
================
*/
void G_BounceProjectile( vec3_t start, vec3_t impact, vec3_t dir, vec3_t endout ) {
	vec3_t v, newv;
	float dot;

	VectorSubtract( impact, start, v );
	dot = DotProduct( v, dir );
	VectorMA( v, -2*dot, dir, newv );

	VectorNormalize(newv);
	VectorMA(impact, 8192, newv, endout);
}


/*
======================================================================

GAUNTLET

======================================================================
*/

/*
=============
Weapon_Gauntlet

Mirrors the retail gauntlet fire event emission.
=============
*/
void Weapon_Gauntlet( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	G_AddEvent( ent, EV_FIRE_WEAPON, 0 );
}


/*
=============
CheckGauntletAttack

Executes the retail 43-unit gauntlet melee trace.
=============
*/
qboolean CheckGauntletAttack( gentity_t *ent ) {
	trace_t		tr;
	vec3_t		end;
	gentity_t		*tent;
	gentity_t		*traceEnt;
	int				damage;
	float	reach;

	if ( !ent || !ent->client ) {
		return qfalse;
	}

	// set aiming directions
	AngleVectors( ent->client->ps.viewangles, forward, right, up );

	CalcMuzzlePoint( ent, forward, right, up, muzzle );

	reach = 43.0f;
	VectorMA( muzzle, reach, forward, end );

	trap_Trace( &tr, muzzle, NULL, NULL, end, ent->s.number, MASK_SHOT );
	if ( tr.surfaceFlags & SURF_NOIMPACT ) {
		return qfalse;
	}

	traceEnt = &g_entities[ tr.entityNum ];

	// send blood impact
	if ( traceEnt->takedamage && traceEnt->client ) {
		tent = G_TempEntity( tr.endpos, EV_MISSILE_HIT );
		tent->s.otherEntityNum = traceEnt->s.number;
		tent->s.eventParm = DirToByte( tr.plane.normal );
		tent->s.weapon = ent->s.weapon;
	}

	if ( !traceEnt->takedamage) {
		return qfalse;
	}

	if ( ent->client->ps.powerups[PW_QUAD] ) {
		G_AddEvent( ent, EV_POWERUP_QUAD, 0 );
		s_quadFactor = g_weaponConfig.quadDamageMultiplier;
	} else {
		s_quadFactor = 1;
	}

	damage = g_weaponConfig.gauntletDamage * s_quadFactor;
	G_Damage( traceEnt, ent, ent, forward, tr.endpos,
		damage, 0, MOD_GAUNTLET );

	return qtrue;
}


/*
======================================================================

MACHINEGUN

======================================================================
*/

/*
======================
SnapVectorTowards

Round a vector to integers for more efficient network
transmission, but make sure that it rounds towards a given point
rather than blindly truncating.  This prevents it from truncating 
into a wall.
======================
*/
void SnapVectorTowards( vec3_t v, vec3_t to ) {
	int		i;

	for ( i = 0 ; i < 3 ; i++ ) {
		if ( to[i] <= v[i] ) {
			v[i] = (int)v[i];
		} else {
			v[i] = (int)v[i] + 1;
		}
	}
}

#define	MACHINEGUN_SPREAD	150
#define	MACHINEGUN_DAMAGE	(g_weaponConfig.machinegunDamage)
#define	HEAVY_MACHINEGUN_SPREAD	350
#define	HEAVY_MACHINEGUN_DAMAGE	(g_weaponConfig.heavyMachinegunDamage)
#define	CHAINGUN_DAMAGE		(g_weaponConfig.chaingunDamage)

/*
=============
Bullet_Fire

Fires a generic hitscan bullet, applying ironsight spread scaling when needed.
=============
*/
void Bullet_Fire( gentity_t *ent, float spread, int damage, meansOfDeath_t mod ) {
	trace_t		tr;
	vec3_t		end;
	vec3_t		impactpoint, bouncedir;
	float		r;
	float		u;
	gentity_t	*tent;
	gentity_t	*traceEnt;
	int			i, passent;
	qboolean		ironsightKick;
	float		ironsightScale;

	ironsightKick = ( mod == MOD_MACHINEGUN ) && G_PlayerUsesMachinegunTightSpread( ent );
	ironsightScale = ironsightKick ? G_GetMachinegunIronsightScale() : 1.0f;

	damage *= s_quadFactor;

	r = random() * M_PI * 2.0f;
	u = sin( r ) * crandom() * spread * 16;
	r = cos( r ) * crandom() * spread * 16;
	if ( ironsightKick ) {
		u *= ironsightScale;
		r *= ironsightScale;
	}

	VectorMA( muzzle, 8192 * 16, forward, end );
	VectorMA( end, r, right, end );
	VectorMA( end, u, up, end );

	passent = ent->s.number;
	for ( i = 0; i < 10; i++ ) {

		trap_Trace( &tr, muzzle, NULL, NULL, end, passent, MASK_SHOT );
		if ( tr.surfaceFlags & SURF_NOIMPACT ) {
			return;
		}

		traceEnt = &g_entities[ tr.entityNum ];

		// snap the endpos to integers, but nudged towards the line
		SnapVectorTowards( tr.endpos, muzzle );

		// send bullet impact
		if ( traceEnt->takedamage && traceEnt->client ) {
			tent = G_TempEntity( tr.endpos, EV_BULLET_HIT_FLESH );
			tent->s.eventParm = traceEnt->s.number;
			if( LogAccuracyHit( traceEnt, ent ) ) {
				ent->client->accuracy_hits++;
				if ( mod == MOD_HMG ) {
					ent->client->pers.accuracy_hits[WP_HEAVY_MACHINEGUN]++;
				} else if ( mod == MOD_CHAINGUN ) {
					ent->client->pers.accuracy_hits[WP_CHAINGUN]++;
				} else {
					ent->client->pers.accuracy_hits[WP_MACHINEGUN]++;
				}
			}
		} else {
			tent = G_TempEntity( tr.endpos, EV_BULLET_HIT_WALL );
			tent->s.eventParm = DirToByte( tr.plane.normal );
		}
		tent->s.otherEntityNum = ent->s.number;

		if ( traceEnt->takedamage) {
			if ( traceEnt->client && traceEnt->client->invulnerabilityTime > level.time ) {
				if (G_InvulnerabilityEffect( traceEnt, forward, tr.endpos, impactpoint, bouncedir )) {
					G_BounceProjectile( muzzle, impactpoint, bouncedir, end );
					VectorCopy( impactpoint, muzzle );
					// the player can hit him/herself with the bounced rail
					passent = ENTITYNUM_NONE;
				}
				else {
					VectorCopy( tr.endpos, muzzle );
					passent = traceEnt->s.number;
				}
				continue;
			}
			else {
				G_Damage( traceEnt, ent, ent, forward, tr.endpos,
					 damage, 0, mod);
			}
		}
		break;
	}
}



/*
======================================================================

BFG

======================================================================
*/

void BFG_Fire ( gentity_t *ent ) {
	gentity_t	*m;

	m = fire_bfg (ent, muzzle, forward);
	m->damage *= s_quadFactor;
	m->splashDamage *= s_quadFactor;

//	VectorAdd( m->s.pos.trDelta, ent->client->ps.velocity, m->s.pos.trDelta );	// "real" physics
}


/*
======================================================================

SHOTGUN

======================================================================
*/

// DEFAULT_SHOTGUN_SPREAD and DEFAULT_SHOTGUN_COUNT	are in bg_public.h, because
// client predicts same spreads
#define	DEFAULT_SHOTGUN_DAMAGE	(g_weaponConfig.shotgunDamage)

qboolean ShotgunPellet( vec3_t start, vec3_t end, gentity_t *ent ) {
	trace_t		tr;
	int			damage, i, passent;
	gentity_t	*traceEnt;
	vec3_t		impactpoint, bouncedir;
	vec3_t		tr_start, tr_end;

	passent = ent->s.number;
	VectorCopy( start, tr_start );
	VectorCopy( end, tr_end );
	for (i = 0; i < 10; i++) {
		trap_Trace (&tr, tr_start, NULL, NULL, tr_end, passent, MASK_SHOT);
		traceEnt = &g_entities[ tr.entityNum ];

		// send bullet impact
		if (  tr.surfaceFlags & SURF_NOIMPACT ) {
			return qfalse;
		}

		if ( traceEnt->takedamage) {
			damage = DEFAULT_SHOTGUN_DAMAGE * s_quadFactor;
			if ( traceEnt->client && traceEnt->client->invulnerabilityTime > level.time ) {
				if (G_InvulnerabilityEffect( traceEnt, forward, tr.endpos, impactpoint, bouncedir )) {
					G_BounceProjectile( tr_start, impactpoint, bouncedir, tr_end );
					VectorCopy( impactpoint, tr_start );
					// the player can hit him/herself with the bounced rail
					passent = ENTITYNUM_NONE;
				}
				else {
					VectorCopy( tr.endpos, tr_start );
					passent = traceEnt->s.number;
				}
				continue;
			}
			else {
				G_Damage( traceEnt, ent, ent, forward, tr.endpos,
					damage, 0, MOD_SHOTGUN);
				if( LogAccuracyHit( traceEnt, ent ) ) {
					return qtrue;
				}
			}
		}
		return qfalse;
	}
	return qfalse;
}

// this should match CG_ShotgunPattern
void ShotgunPattern( vec3_t origin, vec3_t origin2, int seed, gentity_t *ent ) {
	int			i;
	float		r, u;
	vec3_t		end;
	vec3_t		forward, right, up;
	qboolean	hitClient = qfalse;

	(void)seed;

	// derive the right and up vectors from the forward vector, because
	// the client won't have any other information
	VectorNormalize2( origin2, forward );
	PerpendicularVector( right, forward );
	CrossProduct( forward, right, up );

	// generate the "random" spread pattern
	for ( i = 0 ; i < DEFAULT_SHOTGUN_COUNT ; i++ ) {
		G_GetShotgunPelletOffsets( i, &r, &u );

		VectorMA( origin, 8192 * 16, forward, end);
		VectorMA (end, r, right, end);
		VectorMA (end, u, up, end);
		if( ShotgunPellet( origin, end, ent ) && !hitClient ) {
			hitClient = qtrue;
			ent->client->accuracy_hits++;
			ent->client->pers.accuracy_hits[WP_SHOTGUN]++;
		}
	}
}


void weapon_supershotgun_fire (gentity_t *ent) {
	gentity_t		*tent;

	// send shotgun blast
	tent = G_TempEntity( muzzle, EV_SHOTGUN );
	VectorScale( forward, 4096, tent->s.origin2 );
	SnapVector( tent->s.origin2 );
	tent->s.eventParm = rand() & 255;		// seed for spread pattern
	tent->s.otherEntityNum = ent->s.number;

	ShotgunPattern( tent->s.pos.trBase, tent->s.origin2, tent->s.eventParm, ent );
}


/*
======================================================================

GRENADE LAUNCHER

======================================================================
*/

void weapon_grenadelauncher_fire (gentity_t *ent) {
	gentity_t	*m;

	// extra vertical velocity
	forward[2] += 0.2f;
	VectorNormalize( forward );

	m = fire_grenade (ent, muzzle, forward);
	m->damage *= s_quadFactor;
	m->splashDamage *= s_quadFactor;

//	VectorAdd( m->s.pos.trDelta, ent->client->ps.velocity, m->s.pos.trDelta );	// "real" physics
}

/*
======================================================================

ROCKET

======================================================================
*/

void Weapon_RocketLauncher_Fire (gentity_t *ent) {
	gentity_t	*m;

	m = fire_rocket (ent, muzzle, forward);
	m->damage *= s_quadFactor;
	m->splashDamage *= s_quadFactor;

//	VectorAdd( m->s.pos.trDelta, ent->client->ps.velocity, m->s.pos.trDelta );	// "real" physics
}


/*
======================================================================

PLASMA GUN

======================================================================
*/

void Weapon_Plasmagun_Fire (gentity_t *ent) {
	gentity_t	*m;

	m = fire_plasma (ent, muzzle, forward);
	m->damage *= s_quadFactor;
	m->splashDamage *= s_quadFactor;

//	VectorAdd( m->s.pos.trDelta, ent->client->ps.velocity, m->s.pos.trDelta );	// "real" physics
}

/*
======================================================================

RAILGUN

======================================================================
*/


/*
=================
weapon_railgun_fire
=================
*/
#define	MAX_RAIL_HITS	4
void weapon_railgun_fire (gentity_t *ent) {
	vec3_t		end;
	vec3_t impactpoint, bouncedir;
	trace_t		trace;
	gentity_t	*tent;
	gentity_t	*traceEnt;
	int			damage;
	int			i;
	int			hits;
	int			unlinked;
	int			passent;
	gentity_t	*unlinkedEntities[MAX_RAIL_HITS];

	damage = g_weaponConfig.railgunDamage * s_quadFactor;
	G_ApplyRailJump( ent );

	VectorMA (muzzle, 8192, forward, end);

	// trace only against the solids, so the railgun will go through people
	unlinked = 0;
	hits = 0;
	passent = ent->s.number;
	do {
		trap_Trace (&trace, muzzle, NULL, NULL, end, passent, MASK_SHOT );
		if ( trace.entityNum >= ENTITYNUM_MAX_NORMAL ) {
			break;
		}
		traceEnt = &g_entities[ trace.entityNum ];
		if ( traceEnt->takedamage ) {
			if ( traceEnt->client && traceEnt->client->invulnerabilityTime > level.time ) {
				if ( G_InvulnerabilityEffect( traceEnt, forward, trace.endpos, impactpoint, bouncedir ) ) {
					G_BounceProjectile( muzzle, impactpoint, bouncedir, end );
					// snap the endpos to integers to save net bandwidth, but nudged towards the line
					SnapVectorTowards( trace.endpos, muzzle );
					// send railgun beam effect
					tent = G_TempEntity( trace.endpos, EV_RAILTRAIL );
					// set player number for custom colors on the railtrail
					tent->s.clientNum = ent->s.clientNum;
					VectorCopy( muzzle, tent->s.origin2 );
					// move origin a bit to come closer to the drawn gun muzzle
					VectorMA( tent->s.origin2, 4, right, tent->s.origin2 );
					VectorMA( tent->s.origin2, -1, up, tent->s.origin2 );
					tent->s.eventParm = 255;	// don't make the explosion at the end
					//
					VectorCopy( impactpoint, muzzle );
					// the player can hit him/herself with the bounced rail
					passent = ENTITYNUM_NONE;
				}
			} else {
				if ( LogAccuracyHit( traceEnt, ent ) ) {
					hits++;
				}

				int			shotDamage;

				shotDamage = damage;

				G_Damage( traceEnt, ent, ent, forward, trace.endpos, shotDamage, 0, MOD_RAILGUN );
			}
		}
		if ( trace.contents & CONTENTS_SOLID ) {
			break;		// we hit something solid enough to stop the beam
		}
		// unlink this entity, so the next trace will go past it
		trap_UnlinkEntity( traceEnt );
		unlinkedEntities[unlinked] = traceEnt;
		unlinked++;
	} while ( unlinked < MAX_RAIL_HITS );

	// link back in any entities we unlinked
	for ( i = 0 ; i < unlinked ; i++ ) {
		trap_LinkEntity( unlinkedEntities[i] );
	}

	// the final trace endpos will be the terminal point of the rail trail

	// snap the endpos to integers to save net bandwidth, but nudged towards the line
	SnapVectorTowards( trace.endpos, muzzle );

	// send railgun beam effect
	tent = G_TempEntity( trace.endpos, EV_RAILTRAIL );

	// set player number for custom colors on the railtrail
	tent->s.clientNum = ent->s.clientNum;

	VectorCopy( muzzle, tent->s.origin2 );
	// move origin a bit to come closer to the drawn gun muzzle
	VectorMA( tent->s.origin2, 4, right, tent->s.origin2 );
	VectorMA( tent->s.origin2, -1, up, tent->s.origin2 );

	// no explosion at end if SURF_NOIMPACT, but still make the trail
	if ( trace.surfaceFlags & SURF_NOIMPACT ) {
		tent->s.eventParm = 255;	// don't make the explosion at the end
	} else {
		tent->s.eventParm = DirToByte( trace.plane.normal );
	}
	tent->s.clientNum = ent->s.clientNum;

	// give the shooter a reward sound if they have made two railgun hits in a row
	if ( hits == 0 ) {
		// complete miss
		ent->client->accurateCount = 0;
	} else {
		// check for "impressive" reward sound
		ent->client->accurateCount += hits;
		if ( ent->client->accurateCount >= 2 ) {
			ent->client->accurateCount -= 2;
			ent->client->ps.persistant[PERS_IMPRESSIVE_COUNT]++;
			G_RankSendPlayerMedal( ent, "IMPRESSIVE" );
			// add the sprite over the player's head
			ent->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
			ent->client->ps.eFlags |= EF_AWARD_IMPRESSIVE;
			ent->client->rewardTime = level.time + REWARD_SPRITE_TIME;
		}
		ent->client->accuracy_hits++;
		ent->client->pers.accuracy_hits[WP_RAILGUN]++;
	}

}


/*
======================================================================

GRAPPLING HOOK

======================================================================
*/

void Weapon_GrapplingHook_Fire (gentity_t *ent)
{
	gentity_t	*hook;

	if ( !ent->client->fireHeld && !ent->client->hook ) {
		hook = fire_grapple( ent, muzzle, forward );
		hook->damage *= s_quadFactor;
	}

	ent->client->fireHeld = qtrue;
}

void Weapon_HookFree (gentity_t *ent)
{
	ent->parent->client->hook = NULL;
	ent->parent->client->ps.pm_flags &= ~PMF_GRAPPLE_PULL;
	G_FreeEntity( ent );
}

void Weapon_HookThink (gentity_t *ent)
{
	if (ent->enemy) {
		vec3_t v, oldorigin;

		VectorCopy(ent->r.currentOrigin, oldorigin);
		v[0] = ent->enemy->r.currentOrigin[0] + (ent->enemy->r.mins[0] + ent->enemy->r.maxs[0]) * 0.5;
		v[1] = ent->enemy->r.currentOrigin[1] + (ent->enemy->r.mins[1] + ent->enemy->r.maxs[1]) * 0.5;
		v[2] = ent->enemy->r.currentOrigin[2] + (ent->enemy->r.mins[2] + ent->enemy->r.maxs[2]) * 0.5;
		SnapVectorTowards( v, oldorigin );	// save net bandwidth

		G_SetOrigin( ent, v );
	}

	VectorCopy( ent->r.currentOrigin, ent->parent->client->ps.grapplePoint);
}

/*
======================================================================

LIGHTNING GUN

======================================================================
*/

/*
=============
Weapon_LightningDischargeMask

Returns the contents mask for media that should trigger lightning discharge.
=============
*/
static int Weapon_LightningDischargeMask( void ) {
	return CONTENTS_WATER | CONTENTS_SLIME | CONTENTS_LAVA;
}

/*
=============
Weapon_LightningDischargeActive

Checks whether the configured lightning discharge feature is enabled.
=============
*/
static qboolean Weapon_LightningDischargeActive( void ) {
	return ( g_weaponConfig.lightningDischargeFlags > 0 );
}

#define LIGHTNING_DISCHARGE_DEFAULT_AMMO	150

/*
=============
Weapon_GetLightningDischargeAmmoCount

Returns the retail ammo pool consumed by a lightning discharge burst.
=============
*/
static int Weapon_GetLightningDischargeAmmoCount( const gentity_t *ent ) {
	int		ammoCount;

	if ( !ent || !ent->client ) {
		return LIGHTNING_DISCHARGE_DEFAULT_AMMO;
	}

	ammoCount = ent->client->ps.ammo[WP_LIGHTNING];
	if ( g_factoryCvarConfig.infiniteAmmo || ammoCount < 0 ) {
		return LIGHTNING_DISCHARGE_DEFAULT_AMMO;
	}

	ammoCount += 1;
	if ( ammoCount < 1 ) {
		return 1;
	}

	return ammoCount;
}

/*
=============
Weapon_LightningDischargeDamage

Applies the retail ammo-driven lightning discharge burst to nearby entities in hazardous media.
=============
*/
static qboolean Weapon_LightningDischargeDamage( vec3_t origin, gentity_t *attacker, float damage, float radius ) {
	float		points;
	float		dist;
	gentity_t	*ent;
	int		entityList[MAX_GENTITIES];
	int		numListedEntities;
	vec3_t		mins;
	vec3_t		maxs;
	vec3_t		v;
	vec3_t		dir;
	int		i;
	int		e;
	qboolean	hitClient;

	if ( !attacker || !attacker->client ) {
		return qfalse;
	}

	if ( radius < 1.0f ) {
		radius = 1.0f;
	}

	for ( i = 0; i < 3; i++ ) {
		mins[i] = origin[i] - radius;
		maxs[i] = origin[i] + radius;
	}

	hitClient = qfalse;
	numListedEntities = trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );
	for ( e = 0; e < numListedEntities; e++ ) {
		ent = &g_entities[ entityList[e] ];
		if ( !ent->takedamage ) {
			continue;
		}

		for ( i = 0; i < 3; i++ ) {
			if ( origin[i] < ent->r.absmin[i] ) {
				v[i] = ent->r.absmin[i] - origin[i];
			} else if ( origin[i] > ent->r.absmax[i] ) {
				v[i] = origin[i] - ent->r.absmax[i];
			} else {
				v[i] = 0.0f;
			}
		}

		dist = VectorLength( v );
		if ( dist >= radius ) {
			continue;
		}

		points = damage * ( 1.0f - dist / radius );
		if ( points < 1.0f ) {
			continue;
		}

		if ( !CanDamage( ent, origin ) ) {
			continue;
		}

		if ( LogAccuracyHit( ent, attacker ) ) {
			hitClient = qtrue;
		}

		VectorSubtract( ent->r.currentOrigin, origin, dir );
		dir[2] += 24.0f;
		G_Damage( ent, NULL, attacker, dir, origin, (int)points, DAMAGE_RADIUS, MOD_LIGHTNING_DISCHARGE );
	}

	return hitClient;
}

/*
=============
Weapon_LightningFire

Fires the lightning gun, optionally triggering a discharge when the trace or muzzle
intersects hazardous media.
=============
*/
void Weapon_LightningFire( gentity_t *ent ) {
	trace_t		tr;
	vec3_t		end;
	vec3_t impactpoint, bouncedir;
	vec3_t		dischargePoint;
	gentity_t	*traceEnt, *tent;
	float		distance;
	float		dischargeDamage;
	float		dischargeRadius;
	int			damage, i, passent;

	damage = g_weaponConfig.lightningDamage;

	passent = ent->s.number;
	for (i = 0; i < 10; i++) {
		VectorMA( muzzle, LIGHTNING_RANGE, forward, end );

		if ( Weapon_LightningDischargeActive() ) {
			int dischargeAmmo;
			int muzzleContents;

			muzzleContents = trap_PointContents( muzzle, ENTITYNUM_NONE );
			if ( muzzleContents & Weapon_LightningDischargeMask() ) {
				dischargeAmmo = Weapon_GetLightningDischargeAmmoCount( ent );
				dischargeDamage = dischargeAmmo * g_weaponConfig.lightningDamage;
				dischargeRadius = dischargeDamage + 16.0f;
				if ( !g_factoryCvarConfig.infiniteAmmo && ent->client->ps.ammo[WP_LIGHTNING] >= 0 ) {
					ent->client->ps.ammo[WP_LIGHTNING] = 0;
				}

				VectorCopy( muzzle, dischargePoint );
				tent = G_TempEntity( dischargePoint, EV_LIGHTNINGBOLT );
				VectorCopy( muzzle, tent->s.origin2 );
				SnapVector( tent->s.origin2 );

				if ( Weapon_LightningDischargeDamage( dischargePoint, ent, dischargeDamage, dischargeRadius ) ) {
					ent->client->accuracy_hits++;
					ent->client->pers.accuracy_hits[WP_LIGHTNING]++;
				}
				return;
			}
		}

		trap_Trace( &tr, muzzle, NULL, NULL, end, passent, MASK_SHOT );

		// if not the first trace (the lightning bounced of an invulnerability sphere)
		if (i) {
			// add bounced off lightning bolt temp entity
			// the first lightning bolt is a cgame only visual
			//
			tent = G_TempEntity( muzzle, EV_LIGHTNINGBOLT );
			VectorCopy( tr.endpos, end );
			SnapVector( end );
			VectorCopy( end, tent->s.origin2 );
		}
		if ( tr.entityNum == ENTITYNUM_NONE ) {
			return;
		}

		traceEnt = &g_entities[ tr.entityNum ];

		if ( traceEnt->takedamage) {
			if ( traceEnt->client && traceEnt->client->invulnerabilityTime > level.time ) {
				if (G_InvulnerabilityEffect( traceEnt, forward, tr.endpos, impactpoint, bouncedir )) {
					G_BounceProjectile( muzzle, impactpoint, bouncedir, end );
					VectorCopy( impactpoint, muzzle );
					VectorSubtract( end, impactpoint, forward );
					VectorNormalize(forward);
					// the player can hit him/herself with the bounced lightning
					passent = ENTITYNUM_NONE;
				}
				else {
					VectorCopy( tr.endpos, muzzle );
					passent = traceEnt->s.number;
				}
				continue;
			}
			else {
				distance = Distance( muzzle, tr.endpos );
				damage = G_GetLightningDamageForDistance( distance ) * s_quadFactor;
				G_Damage( traceEnt, ent, ent, forward, tr.endpos,
					damage, 0, MOD_LIGHTNING);
			}
		}

		if ( traceEnt->takedamage && traceEnt->client ) {
			tent = G_TempEntity( tr.endpos, EV_MISSILE_HIT );
			tent->s.otherEntityNum = traceEnt->s.number;
			tent->s.eventParm = DirToByte( tr.plane.normal );
			tent->s.weapon = ent->s.weapon;
			if( LogAccuracyHit( traceEnt, ent ) ) {
				ent->client->accuracy_hits++;
				ent->client->pers.accuracy_hits[WP_LIGHTNING]++;
			}
		} else if ( !( tr.surfaceFlags & SURF_NOIMPACT ) ) {
			tent = G_TempEntity( tr.endpos, EV_MISSILE_MISS );
			tent->s.eventParm = DirToByte( tr.plane.normal );
		}

		break;
	}
}

/*
======================================================================

NAILGUN

======================================================================
*/

void Weapon_Nailgun_Fire (gentity_t *ent) {
	gentity_t	*m;
	int			count;

	for( count = 0; count < NUM_NAILSHOTS; count++ ) {
		m = fire_nail (ent, muzzle, forward, right, up );
		m->damage *= s_quadFactor;
		m->splashDamage *= s_quadFactor;
	}

//	VectorAdd( m->s.pos.trDelta, ent->client->ps.velocity, m->s.pos.trDelta );	// "real" physics
}


/*
======================================================================

PROXIMITY MINE LAUNCHER

======================================================================
*/

void weapon_proxlauncher_fire (gentity_t *ent) {
	gentity_t	*m;

	// extra vertical velocity
	forward[2] += 0.2f;
	VectorNormalize( forward );

	m = fire_prox (ent, muzzle, forward);
	m->damage *= s_quadFactor;
	m->splashDamage *= s_quadFactor;

//	VectorAdd( m->s.pos.trDelta, ent->client->ps.velocity, m->s.pos.trDelta );	// "real" physics
}


//======================================================================


/*
===============
LogAccuracyHit
===============
*/
qboolean LogAccuracyHit( gentity_t *target, gentity_t *attacker ) {
	if( !target->takedamage ) {
		return qfalse;
	}

	if ( target == attacker ) {
		return qfalse;
	}

	if( !target->client ) {
		return qfalse;
	}

	if( !attacker->client ) {
		return qfalse;
	}

	if( target->client->ps.stats[STAT_HEALTH] <= 0 ) {
		return qfalse;
	}

	if ( OnSameTeam( target, attacker ) ) {
		return qfalse;
	}

	return qtrue;
}


/*
===============
CalcMuzzlePoint

set muzzle location relative to pivoting eye
===============
*/
void CalcMuzzlePoint ( gentity_t *ent, vec3_t forward, vec3_t right, vec3_t up, vec3_t muzzlePoint ) {
	VectorCopy( ent->s.pos.trBase, muzzlePoint );
	muzzlePoint[2] += ent->client->ps.viewheight;
	VectorMA( muzzlePoint, G_GetMuzzleForwardOffset( ent ), forward, muzzlePoint );
	// snap to integer coordinates for more efficient network bandwidth usage
	SnapVector( muzzlePoint );
}

/*
===============
CalcMuzzlePointOrigin

set muzzle location relative to pivoting eye
===============
*/
void CalcMuzzlePointOrigin ( gentity_t *ent, vec3_t origin, vec3_t forward, vec3_t right, vec3_t up, vec3_t muzzlePoint ) {
	(void)origin;

	VectorCopy( ent->s.pos.trBase, muzzlePoint );
	muzzlePoint[2] += ent->client->ps.viewheight;
	VectorMA( muzzlePoint, G_GetMuzzleForwardOffset( ent ), forward, muzzlePoint );
	// snap to integer coordinates for more efficient network bandwidth usage
	SnapVector( muzzlePoint );
}



/*
===============
FireWeapon
===============
*/
void FireWeapon( gentity_t *ent ) {
	qboolean	lagHaxActive;

	if ( ent->client->ps.powerups[PW_QUAD] ) {
		s_quadFactor = g_weaponConfig.quadDamageMultiplier;
	} else {
		s_quadFactor = 1;
	}

	// track shots taken for accuracy tracking.  Grapple is not a weapon and gauntet is just not tracked
	if( ent->s.weapon != WP_GRAPPLING_HOOK && ent->s.weapon != WP_GAUNTLET ) {
		if( ent->s.weapon == WP_SHOTGUN ) {
			ent->client->accuracy_shots += DEFAULT_SHOTGUN_COUNT;
			ent->client->pers.accuracy_shots[WP_SHOTGUN] += DEFAULT_SHOTGUN_COUNT;
		} else if( ent->s.weapon == WP_NAILGUN ) {
			ent->client->accuracy_shots += NUM_NAILSHOTS;
			ent->client->pers.accuracy_shots[WP_NAILGUN] += NUM_NAILSHOTS;
		} else {
			ent->client->accuracy_shots++;
			ent->client->pers.accuracy_shots[ent->s.weapon]++;
		}
	}

	// set aiming directions
	AngleVectors (ent->client->ps.viewangles, forward, right, up);

	CalcMuzzlePointOrigin ( ent, ent->client->oldOrigin, forward, right, up, muzzle );

	lagHaxActive = qfalse;
	if ( G_WeaponUsesLagHaxTimeshift( ent->s.weapon )
		&& g_lagHaxHistory.integer > 0
		&& g_lagHaxMs.integer > 0
		&& !( ent->r.svFlags & SVF_BOT ) ) {
		G_TimeShiftAllClients( ent, ent->client->ps.commandTime );
		lagHaxActive = qtrue;
	}

	// fire the specific weapon
	switch( ent->s.weapon ) {
	case WP_GAUNTLET:
		Weapon_Gauntlet( ent );
		break;
	case WP_LIGHTNING:
		Weapon_LightningFire( ent );
		break;
	case WP_SHOTGUN:
		weapon_supershotgun_fire( ent );
		break;
	case WP_MACHINEGUN:
		Bullet_Fire( ent, MACHINEGUN_SPREAD, MACHINEGUN_DAMAGE, MOD_MACHINEGUN );
		break;
	case WP_HEAVY_MACHINEGUN:
		Bullet_Fire( ent, HEAVY_MACHINEGUN_SPREAD, HEAVY_MACHINEGUN_DAMAGE, MOD_HMG );
		break;
	case WP_GRENADE_LAUNCHER:
		weapon_grenadelauncher_fire( ent );
		break;
	case WP_ROCKET_LAUNCHER:
		Weapon_RocketLauncher_Fire( ent );
		break;
	case WP_PLASMAGUN:
		Weapon_Plasmagun_Fire( ent );
		break;
	case WP_RAILGUN:
		weapon_railgun_fire( ent );
		break;
	case WP_BFG:
		BFG_Fire( ent );
		break;
	case WP_GRAPPLING_HOOK:
		Weapon_GrapplingHook_Fire( ent );
		break;
	case WP_NAILGUN:
		Weapon_Nailgun_Fire( ent );
		break;
	case WP_PROX_LAUNCHER:
		weapon_proxlauncher_fire( ent );
		break;
	case WP_CHAINGUN:
		Bullet_Fire( ent, G_GetChaingunSpread( ent ), CHAINGUN_DAMAGE, MOD_CHAINGUN );
		break;
default:
// FIXME		G_Error( "Bad ent->s.weapon" );
		break;
	}

	if ( lagHaxActive ) {
		G_UnTimeShiftAllClients();
	}
}



/*
===============
KamikazeRadiusDamage
===============
*/
static void KamikazeRadiusDamage( vec3_t origin, gentity_t *attacker, float damage, float radius ) {
	float		dist;
	gentity_t	*ent;
	int			entityList[MAX_GENTITIES];
	int			numListedEntities;
	vec3_t		mins, maxs;
	vec3_t		v;
	vec3_t		dir;
	int			i, e;

	if ( radius < 1 ) {
		radius = 1;
	}

	for ( i = 0 ; i < 3 ; i++ ) {
		mins[i] = origin[i] - radius;
		maxs[i] = origin[i] + radius;
	}

	numListedEntities = trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );

	for ( e = 0 ; e < numListedEntities ; e++ ) {
		ent = &g_entities[entityList[ e ]];

		if (!ent->takedamage) {
			continue;
		}

		// dont hit things we have already hit
		if( ent->kamikazeTime > level.time ) {
			continue;
		}

		// find the distance from the edge of the bounding box
		for ( i = 0 ; i < 3 ; i++ ) {
			if ( origin[i] < ent->r.absmin[i] ) {
				v[i] = ent->r.absmin[i] - origin[i];
			} else if ( origin[i] > ent->r.absmax[i] ) {
				v[i] = origin[i] - ent->r.absmax[i];
			} else {
				v[i] = 0;
			}
		}

		dist = VectorLength( v );
		if ( dist >= radius ) {
			continue;
		}

//		if( CanDamage (ent, origin) ) {
			VectorSubtract (ent->r.currentOrigin, origin, dir);
			// push the center of mass higher than the origin so players
			// get knocked into the air more
			dir[2] += 24;
			G_Damage( ent, NULL, attacker, dir, origin, damage, DAMAGE_RADIUS|DAMAGE_NO_TEAM_PROTECTION, MOD_KAMIKAZE );
			ent->kamikazeTime = level.time + 3000;
//		}
	}
}

/*
===============
KamikazeShockWave
===============
*/
static void KamikazeShockWave( vec3_t origin, gentity_t *attacker, float damage, float push, float radius ) {
	float		dist;
	gentity_t	*ent;
	int			entityList[MAX_GENTITIES];
	int			numListedEntities;
	vec3_t		mins, maxs;
	vec3_t		v;
	vec3_t		dir;
	int			i, e;

	if ( radius < 1 )
		radius = 1;

	for ( i = 0 ; i < 3 ; i++ ) {
		mins[i] = origin[i] - radius;
		maxs[i] = origin[i] + radius;
	}

	numListedEntities = trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );

	for ( e = 0 ; e < numListedEntities ; e++ ) {
		ent = &g_entities[entityList[ e ]];

		// dont hit things we have already hit
		if( ent->kamikazeShockTime > level.time ) {
			continue;
		}

		// find the distance from the edge of the bounding box
		for ( i = 0 ; i < 3 ; i++ ) {
			if ( origin[i] < ent->r.absmin[i] ) {
				v[i] = ent->r.absmin[i] - origin[i];
			} else if ( origin[i] > ent->r.absmax[i] ) {
				v[i] = origin[i] - ent->r.absmax[i];
			} else {
				v[i] = 0;
			}
		}

		dist = VectorLength( v );
		if ( dist >= radius ) {
			continue;
		}

//		if( CanDamage (ent, origin) ) {
			VectorSubtract (ent->r.currentOrigin, origin, dir);
			dir[2] += 24;
			G_Damage( ent, NULL, attacker, dir, origin, damage, DAMAGE_RADIUS|DAMAGE_NO_TEAM_PROTECTION, MOD_KAMIKAZE );
			//
			dir[2] = 0;
			VectorNormalize(dir);
			if ( ent->client ) {
				ent->client->ps.velocity[0] = dir[0] * push;
				ent->client->ps.velocity[1] = dir[1] * push;
				ent->client->ps.velocity[2] = 100;
			}
			ent->kamikazeShockTime = level.time + 3000;
//		}
	}
}

/*
===============
KamikazeDamage
===============
*/
static void KamikazeDamage( gentity_t *self ) {
	int i;
	float t;
	gentity_t *ent;
	vec3_t newangles;

	self->count += 100;

	if (self->count >= KAMI_SHOCKWAVE_STARTTIME) {
		// shockwave push back
		t = self->count - KAMI_SHOCKWAVE_STARTTIME;
		KamikazeShockWave(self->s.pos.trBase, self->activator, 25, 400,	(int) (float) t * KAMI_SHOCKWAVE_MAXRADIUS / (KAMI_SHOCKWAVE_ENDTIME - KAMI_SHOCKWAVE_STARTTIME) );
	}
	//
	if (self->count >= KAMI_EXPLODE_STARTTIME) {
		// do our damage
		t = self->count - KAMI_EXPLODE_STARTTIME;
		KamikazeRadiusDamage( self->s.pos.trBase, self->activator, 400,	(int) (float) t * KAMI_BOOMSPHERE_MAXRADIUS / (KAMI_IMPLODE_STARTTIME - KAMI_EXPLODE_STARTTIME) );
	}

	// either cycle or kill self
	if( self->count >= KAMI_SHOCKWAVE_ENDTIME ) {
		G_FreeEntity( self );
		return;
	}
	self->nextthink = level.time + 100;

	// add earth quake effect
	newangles[0] = crandom() * 2;
	newangles[1] = crandom() * 2;
	newangles[2] = 0;
	for (i = 0; i < MAX_CLIENTS; i++)
	{
		ent = &g_entities[i];
		if (!ent->inuse)
			continue;
		if (!ent->client)
			continue;

		if (ent->client->ps.groundEntityNum != ENTITYNUM_NONE) {
			ent->client->ps.velocity[0] += crandom() * 120;
			ent->client->ps.velocity[1] += crandom() * 120;
			ent->client->ps.velocity[2] = 30 + random() * 25;
		}

		ent->client->ps.delta_angles[0] += ANGLE2SHORT(newangles[0] - self->movedir[0]);
		ent->client->ps.delta_angles[1] += ANGLE2SHORT(newangles[1] - self->movedir[1]);
		ent->client->ps.delta_angles[2] += ANGLE2SHORT(newangles[2] - self->movedir[2]);
	}
	VectorCopy(newangles, self->movedir);
}

/*
===============
G_StartKamikaze
===============
*/
void G_StartKamikaze( gentity_t *ent ) {
	gentity_t	*explosion;
	gentity_t	*te;
	vec3_t		snapped;

	// start up the explosion logic
	explosion = G_Spawn();

	explosion->s.eType = ET_EVENTS + EV_KAMIKAZE;
	explosion->eventTime = level.time;

	if ( ent->client ) {
		VectorCopy( ent->s.pos.trBase, snapped );
	}
	else {
		VectorCopy( ent->activator->s.pos.trBase, snapped );
	}
	SnapVector( snapped );		// save network bandwidth
	G_SetOrigin( explosion, snapped );

	explosion->classname = "kamikaze";
	explosion->s.pos.trType = TR_STATIONARY;

	explosion->kamikazeTime = level.time;

	explosion->think = KamikazeDamage;
	explosion->nextthink = level.time + 100;
	explosion->count = 0;
	VectorClear(explosion->movedir);

	trap_LinkEntity( explosion );

	if (ent->client) {
		//
		explosion->activator = ent;
		//
		ent->s.eFlags &= ~EF_KAMIKAZE;
		// nuke the guy that used it
		G_Damage( ent, ent, ent, NULL, NULL, 100000, DAMAGE_NO_PROTECTION, MOD_KAMIKAZE );
	}
	else {
		if ( !strcmp(ent->activator->classname, "bodyque") ) {
			explosion->activator = &g_entities[ent->activator->r.ownerNum];
		}
		else {
			explosion->activator = ent->activator;
		}
	}

	// play global sound at all clients
	te = G_TempEntity(snapped, EV_GLOBAL_TEAM_SOUND );
	te->r.svFlags |= SVF_BROADCAST;
	te->s.eventParm = GTS_KAMIKAZE;
}
