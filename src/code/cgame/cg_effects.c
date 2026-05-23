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
// cg_effects.c -- these functions generate localentities, usually as a result
// of event processing

#include "cg_local.h"

qhandle_t cg_deathEffectShader;
qhandle_t cg_gibSphereModel;


/*
==================
CG_BubbleTrail

Bullets shot underwater
==================
*/
void CG_BubbleTrail( vec3_t start, vec3_t end, float spacing ) {
	vec3_t		move;
	vec3_t		vec;
	float		len;
	int			i;

	if ( !cg_bubbleTrail.integer ) {
		return;
	}

	VectorCopy (start, move);
	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);

	// advance a random amount first
	i = rand() % (int)spacing;
	VectorMA( move, i, vec, move );

	VectorScale (vec, spacing, vec);

	for ( ; i < len; i += spacing ) {
		localEntity_t	*le;
		refEntity_t		*re;

		le = CG_AllocLocalEntity();
		le->leFlags = LEF_PUFF_DONT_SCALE;
		le->leType = LE_MOVE_SCALE_FADE;
		le->startTime = cg.time;
		le->endTime = cg.time + 1000 + random() * 250;
		le->lifeRate = 1.0 / ( le->endTime - le->startTime );

		re = &le->refEntity;
		re->shaderTime = cg.time / 1000.0f;

		re->reType = RT_SPRITE;
		re->rotation = 0;
		re->radius = 3;
		re->customShader = cgs.media.waterBubbleShader;
		re->shaderRGBA[0] = 0xff;
		re->shaderRGBA[1] = 0xff;
		re->shaderRGBA[2] = 0xff;
		re->shaderRGBA[3] = 0xff;

		le->color[3] = 1.0;

		le->pos.trType = TR_LINEAR;
		le->pos.trTime = cg.time;
		VectorCopy( move, le->pos.trBase );
		le->pos.trDelta[0] = crandom()*5;
		le->pos.trDelta[1] = crandom()*5;
		le->pos.trDelta[2] = crandom()*5 + 6;

		VectorAdd (move, vec, move);
	}
}

/*
=====================
CG_SmokePuff

Adds a smoke puff or blood trail localEntity.
=====================
*/
localEntity_t *CG_SmokePuff( const vec3_t p, const vec3_t vel, 
				   float radius,
				   float r, float g, float b, float a,
				   float duration,
				   int startTime,
				   int fadeInTime,
				   int leFlags,
				   qhandle_t hShader ) {
	static int	seed = 0x92;
	localEntity_t	*le;
	refEntity_t		*re;
//	int fadeInTime = startTime + duration / 2;

	le = CG_AllocLocalEntity();
	le->leFlags = leFlags;
	le->radius = radius;

	re = &le->refEntity;
	re->rotation = Q_random( &seed ) * 360;
	re->radius = radius;
	re->shaderTime = startTime / 1000.0f;

	le->leType = LE_MOVE_SCALE_FADE;
	le->startTime = startTime;
	le->fadeInTime = fadeInTime;
	le->endTime = startTime + duration;
	if ( fadeInTime > startTime ) {
		le->lifeRate = 1.0 / ( le->endTime - le->fadeInTime );
	}
	else {
		le->lifeRate = 1.0 / ( le->endTime - le->startTime );
	}
	le->color[0] = r;
	le->color[1] = g; 
	le->color[2] = b;
	le->color[3] = a;


	le->pos.trType = TR_LINEAR;
	le->pos.trTime = startTime;
	VectorCopy( vel, le->pos.trDelta );
	VectorCopy( p, le->pos.trBase );

	VectorCopy( p, re->origin );
	re->customShader = hShader;

	// rage pro can't alpha fade, so use a different shader
	if ( cgs.glconfig.hardwareType == GLHW_RAGEPRO ) {
		re->customShader = cgs.media.smokePuffRageProShader;
		re->shaderRGBA[0] = 0xff;
		re->shaderRGBA[1] = 0xff;
		re->shaderRGBA[2] = 0xff;
		re->shaderRGBA[3] = 0xff;
	} else {
		re->shaderRGBA[0] = le->color[0] * 0xff;
		re->shaderRGBA[1] = le->color[1] * 0xff;
		re->shaderRGBA[2] = le->color[2] * 0xff;
		re->shaderRGBA[3] = 0xff;
	}

	re->reType = RT_SPRITE;
	re->radius = le->radius;

	return le;
}

/*
==================
CG_SpawnEffect

Player teleporting in or out
==================
*/
void CG_SpawnEffect( vec3_t org ) {
	localEntity_t	*le;
	refEntity_t		*re;

	le = CG_AllocLocalEntity();
	le->leFlags = 0;
	le->leType = LE_FADE_RGB;
	le->startTime = cg.time;
	le->endTime = cg.time + 500;
	le->lifeRate = 1.0 / ( le->endTime - le->startTime );

	le->color[0] = le->color[1] = le->color[2] = le->color[3] = 1.0;

	re = &le->refEntity;

	re->reType = RT_MODEL;
	re->shaderTime = cg.time / 1000.0f;

	re->hModel = cgs.media.teleportEffectModel;
	AxisClear( re->axis );

	VectorCopy( org, re->origin );
	re->origin[2] += 16;
}


/*
===============
CG_LightningBoltBeam
===============
*/
void CG_LightningBoltBeam( vec3_t start, vec3_t end ) {
	localEntity_t	*le;
	refEntity_t		*beam;
	int				styleIndex;

	le = CG_AllocLocalEntity();
	le->leFlags = 0;
	le->leType = LE_SHOWREFENTITY;
	le->startTime = cg.time;
	le->endTime = cg.time + 50;

	beam = &le->refEntity;

	VectorCopy( start, beam->origin );
	// this is the end point
	VectorCopy( end, beam->oldorigin );

	beam->reType = RT_LIGHTNING;
	beam->radius = 256.0f;

	styleIndex = cg_lightningStyle.integer - 1;
	if ( styleIndex < 0 ) {
		styleIndex = 0;
	} else if ( styleIndex >= CG_MAX_LIGHTNING_STYLES ) {
		styleIndex = CG_MAX_LIGHTNING_STYLES - 1;
	}

	beam->customShader = cgs.media.lightningStyleShaders[styleIndex];
	if ( !beam->customShader ) {
		beam->customShader = cgs.media.lightningShader;
	}
}

/*
==========================
CG_LightningDischargeEffect

Spawns the retail hazardous-lightning discharge sprite.
==========================
*/
void CG_LightningDischargeEffect( vec3_t origin, int magnitude ) {
	localEntity_t	*le;
	qhandle_t		shader;
	float			radius;
	int				duration;

	if ( magnitude < 0 ) {
		magnitude = 0;
	}

	shader = trap_R_RegisterShader( "models/weaphits/electric.tga" );
	radius = (float)( ( magnitude * 10 + 48 ) >> 4 );
	duration = magnitude + 300;

	le = CG_SmokePuff( origin, vec3_origin, radius,
		1.0f, 1.0f, 1.0f, 1.0f,
		(float)duration, cg.time, 0, 0, shader );
	le->leType = LE_SCALE_FADE;
}

/*
==================
CG_KamikazeEffect
==================
*/
void CG_KamikazeEffect( vec3_t org ) {
	localEntity_t	*le;
	refEntity_t		*re;

	le = CG_AllocLocalEntity();
	le->leFlags = 0;
	le->leType = LE_KAMIKAZE;
	le->startTime = cg.time;
	le->endTime = cg.time + 3000;//2250;
	le->lifeRate = 1.0 / ( le->endTime - le->startTime );

	le->color[0] = le->color[1] = le->color[2] = le->color[3] = 1.0;

	VectorClear(le->angles.trBase);

	re = &le->refEntity;

	re->reType = RT_MODEL;
	re->shaderTime = cg.time / 1000.0f;

	re->hModel = cgs.media.kamikazeEffectModel;

	VectorCopy( org, re->origin );

}

/*
==================
CG_ObeliskExplode
==================
*/
void CG_ObeliskExplode( vec3_t org, int entityNum ) {
	localEntity_t	*le;
	vec3_t origin;

	// create an explosion
	VectorCopy( org, origin );
	origin[2] += 64;
	le = CG_MakeExplosion( origin, vec3_origin,
						   cgs.media.dishFlashModel,
						   cgs.media.rocketExplosionShader,
						   600, qtrue );
	le->light = 300;
	le->lightColor[0] = 1;
	le->lightColor[1] = 0.75;
	le->lightColor[2] = 0.0;
}

/*
==================
CG_ObeliskPain
==================
*/
void CG_ObeliskPain( vec3_t org ) {
	int r;
	sfxHandle_t sfx;

	// hit sound
	r = rand() & 3;
	if ( r < 2 ) {
		sfx = cgs.media.obeliskHitSound1;
	} else if ( r == 2 ) {
		sfx = cgs.media.obeliskHitSound2;
	} else {
		sfx = cgs.media.obeliskHitSound3;
	}
	trap_S_StartSound ( org, ENTITYNUM_NONE, CHAN_BODY, sfx );
}


/*
==================
CG_InvulnerabilityImpact
==================
*/
void CG_InvulnerabilityImpact( vec3_t org, vec3_t angles ) {
	localEntity_t	*le;
	refEntity_t		*re;
	int				r;
	sfxHandle_t		sfx;

	le = CG_AllocLocalEntity();
	le->leFlags = 0;
	le->leType = LE_INVULIMPACT;
	le->startTime = cg.time;
	le->endTime = cg.time + 1000;
	le->lifeRate = 1.0 / ( le->endTime - le->startTime );

	le->color[0] = le->color[1] = le->color[2] = le->color[3] = 1.0;

	re = &le->refEntity;

	re->reType = RT_MODEL;
	re->shaderTime = cg.time / 1000.0f;

	re->hModel = cgs.media.invulnerabilityImpactModel;

	VectorCopy( org, re->origin );
	AnglesToAxis( angles, re->axis );

	r = rand() & 3;
	if ( r < 2 ) {
		sfx = cgs.media.invulnerabilityImpactSound1;
	} else if ( r == 2 ) {
		sfx = cgs.media.invulnerabilityImpactSound2;
	} else {
		sfx = cgs.media.invulnerabilityImpactSound3;
	}
	trap_S_StartSound (org, ENTITYNUM_NONE, CHAN_BODY, sfx );
}

/*
==================
CG_InvulnerabilityJuiced
==================
*/
void CG_InvulnerabilityJuiced( vec3_t org ) {
	localEntity_t	*le;
	refEntity_t		*re;
	vec3_t			angles;

	if ( !cgs.media.haveDlcGibs ) {
		CG_DetonateJuicedPlayer( org, qtrue );
		return;
	}

	le = CG_AllocLocalEntity();
	le->leFlags = 0;
	le->leType = LE_INVULJUICED;
	le->startTime = cg.time;
	le->endTime = cg.time + 10000;
	le->lifeRate = 1.0 / ( le->endTime - le->startTime );

	le->color[0] = le->color[1] = le->color[2] = le->color[3] = 1.0;

	re = &le->refEntity;

	re->reType = RT_MODEL;
	re->shaderTime = cg.time / 1000.0f;

	re->hModel = cgs.media.invulnerabilityJuicedModel;

	VectorCopy( org, re->origin );
	VectorClear(angles);
	AnglesToAxis( angles, re->axis );

	trap_S_StartSound (org, ENTITYNUM_NONE, CHAN_BODY, cgs.media.invulnerabilityJuicedSound );
}


/*
==================
CG_ScorePlum
==================
*/
void CG_ScorePlum( int client, vec3_t org, int score ) {
	localEntity_t	*le;
	refEntity_t		*re;
	vec3_t			angles;
	static vec3_t lastPos;

	// only visualize for the client that scored
	if (client != cg.predictedPlayerState.clientNum || cg_scorePlum.integer == 0) {
		return;
	}

	le = CG_AllocLocalEntity();
	le->leFlags = 0;
	le->leType = LE_SCOREPLUM;
	le->startTime = cg.time;
	le->endTime = cg.time + 4000;
	le->lifeRate = 1.0 / ( le->endTime - le->startTime );

	
	le->color[0] = le->color[1] = le->color[2] = le->color[3] = 1.0;
	le->radius = score;
	
	VectorCopy( org, le->pos.trBase );
	if ( org[2] >= lastPos[2] - 20.0f && org[2] <= lastPos[2] ) {
		le->pos.trBase[2] -= 20.0f;
	}

	//CG_Printf( "Plum origin %i %i %i -- %i\n", (int)org[0], (int)org[1], (int)org[2], (int)Distance(org, lastPos));
	VectorCopy(org, lastPos);


	re = &le->refEntity;

	re->reType = RT_SPRITE;
	re->radius = 16;

	VectorClear(angles);
	AnglesToAxis( angles, re->axis );
}


/*
====================
CG_MakeExplosion
====================
*/
localEntity_t *CG_MakeExplosion( vec3_t origin, vec3_t dir, 
								qhandle_t hModel, qhandle_t shader,
								int msec, qboolean isSprite ) {
	float			ang;
	localEntity_t	*ex;
	int				offset;
	vec3_t			tmpVec, newOrigin;

	if ( msec <= 0 ) {
		CG_Error( "CG_MakeExplosion: msec = %i", msec );
	}

	// skew the time a bit so they aren't all in sync
	offset = rand() & 63;

	ex = CG_AllocLocalEntity();
	if ( isSprite ) {
		ex->leType = LE_SPRITE_EXPLOSION;

		// randomly rotate sprite orientation
		ex->refEntity.rotation = rand() % 360;
		VectorScale( dir, 16, tmpVec );
		VectorAdd( tmpVec, origin, newOrigin );
	} else {
		ex->leType = LE_EXPLOSION;
		VectorCopy( origin, newOrigin );

		// set axis with random rotate
		if ( !dir ) {
			AxisClear( ex->refEntity.axis );
		} else {
			ang = rand() % 360;
			VectorCopy( dir, ex->refEntity.axis[0] );
			RotateAroundDirection( ex->refEntity.axis, ang );
		}
	}

	ex->startTime = cg.time - offset;
	ex->endTime = ex->startTime + msec;

	// bias the time so all shader effects start correctly
	ex->refEntity.shaderTime = ex->startTime / 1000.0f;

	ex->refEntity.hModel = hModel;
	ex->refEntity.customShader = shader;

	// set origin
	VectorCopy( newOrigin, ex->refEntity.origin );
	VectorCopy( newOrigin, ex->refEntity.oldorigin );

	ex->color[0] = ex->color[1] = ex->color[2] = ex->color[3] = 1.0f;

	return ex;
}


/*
=================
CG_Bleed

This is the spurt of blood when a character gets hit
=================
*/
void CG_Bleed( vec3_t origin, int entityNum ) {
	localEntity_t	*blood;
	qhandle_t		bloodShader;

	if ( !cg_blood.integer || !cgs.media.bloodSprayShaders[0] ) {
		return;
	}

	bloodShader = cgs.media.bloodSprayShaders[rand() & 3];
	blood = CG_SmokePuff( origin, vec3_origin,
					  32.0f,
					  1.0f, 1.0f, 1.0f, 1.0f,
					  500,
					  cg.time,
					  0,
					  0,
					  bloodShader );
	blood->leType = LE_FALL_SCALE_FADE;
	blood->pos.trDelta[2] = 40.0f;

	// don't show player's own blood in view
	if ( entityNum == cg.snap->ps.clientNum ) {
		blood->refEntity.renderfx |= RF_THIRD_PERSON;
	}
}



/*
==================
CG_SpawnDeathEffect
==================
*/
static void CG_SpawnDeathEffect( const vec3_t origin, qboolean elevatedShell ) {
	localEntity_t	*le;
	refEntity_t		*re;
	vec3_t			effectOrigin;

	if ( !cg_deathEffectShader ) {
		return;
	}

	VectorCopy( origin, effectOrigin );
	if ( elevatedShell ) {
		effectOrigin[2] += 26.0f;
	}

	le = CG_AllocLocalEntity();
	le->leFlags = LEF_PUFF_DONT_SCALE;
	le->leType = LE_DEATH_EFFECT;
	le->startTime = cg.time;
	le->endTime = cg.time + 500;
	le->lifeRate = 1.0f / ( le->endTime - le->startTime );
	le->color[0] = 0.25f;
	le->color[1] = 0.25f;
	le->color[2] = 0.25f;
	le->color[3] = 0.25f;
	le->radius = 50.0f;
	le->light = 400.0f;
	le->lightColor[0] = 1.0f;
	le->lightColor[1] = 0.75f;
	le->lightColor[2] = 0.0f;
	le->pos.trTime = cg.time;
	VectorCopy( effectOrigin, le->pos.trBase );

	re = &le->refEntity;
	re->reType = RT_SPRITE;
	re->customShader = cg_deathEffectShader;
	re->shaderTime = cg.time / 1000.0f;
	re->radius = le->radius;
	VectorCopy( effectOrigin, re->origin );
}

/*
==================
CG_SpawnBigExplodeTracer
==================
*/
static void CG_SpawnBigExplodeTracer( const vec3_t origin, int startTime, int lifetime ) {
	localEntity_t	*le;
	refEntity_t		*re;

	if ( !cgs.media.tracerShader ) {
		return;
	}

	le = CG_AllocLocalEntity();
	le->leFlags = LEF_PUFF_DONT_SCALE;
	le->leType = LE_BIGEXPLODE_TRACER;
	le->startTime = startTime;
	le->endTime = startTime + lifetime;
	le->fadeInTime = 0;
	le->lifeRate = 1.0f / ( le->endTime - le->startTime );
	le->color[0] = 0.5f;
	le->color[1] = 0.5f;
	le->color[2] = 0.5f;
	le->color[3] = 0.5f;
	le->radius = 3.0f;

	le->pos.trType = TR_QL_ACCEL;
	le->pos.trTime = startTime;
	VectorCopy( origin, le->pos.trBase );
	VectorClear( le->pos.trDelta );
	le->posTrajExtra = -240.0f;

	re = &le->refEntity;
	re->reType = RT_SPRITE;
	re->rotation = 0.0f;
	re->customShader = cgs.media.tracerShader;
	re->shaderTime = startTime / 1000.0f;
	re->radius = le->radius;
	VectorCopy( origin, re->origin );
}

/*
==================
CG_SpawnBigExplodeEffects

Retail fuses the death-effect shell and delayed tracer family under one owner.
==================
*/
static void CG_SpawnBigExplodeEffects( const vec3_t origin, qboolean elevatedShell ) {
	vec3_t	tracerOrigin;
	int		i;

	CG_SpawnDeathEffect( origin, elevatedShell );

	for ( i = 0; i < 36; i++ ) {
		tracerOrigin[0] = origin[0] + crandom() * 16.0f;
		tracerOrigin[1] = origin[1] + crandom() * 16.0f;
		if ( elevatedShell ) {
			tracerOrigin[2] = origin[2] + 20.0f + crandom() * 16.0f;
		}
		else {
			tracerOrigin[2] = origin[2] + 2.0f + crandom() * 4.0f;
		}

		CG_SpawnBigExplodeTracer( tracerOrigin, cg.time + crandom() * 500.0f,
			500 + crandom() * 250.0f );
	}
}

#define	EXP_RING_STEP					0.62831854820251465f
#define	EXP_RING_RADIUS				5.5f
#define	EXP_RING_RADIUS_JITTER		2.75f
#define	EXP_RING_CENTER_OFFSET		8.0f
#define	EXP_RING_VELOCITY			20.0f
#define	EXP_RING_VELOCITY_SCALE		21.0f
#define	EXP_RING_VELOCITY_JITTER	10.5f
#define	EXP_JUICED_ORIGIN_OFFSET	8.0f

void CG_LaunchExplode( const vec3_t origin, const vec3_t velocity, qhandle_t hModel );

/*
==================
CG_LaunchBigExplodeFragments

Retail no-DLC fallback uses a downward 10-step ring basis for the sphere burst.
==================
*/
static void CG_LaunchBigExplodeFragments( const vec3_t playerOrigin, qboolean elevatedShell ) {
	vec3_t	direction;
	vec3_t	origin;
	vec3_t	right;
	vec3_t	up;
	vec3_t	originBase;
	vec3_t	center;
	vec3_t	point;
	vec3_t	velocity;
	float	angle;
	float	rightRadius;
	float	upRadius;
	int		i;

	VectorSet( direction, 0.0f, 0.0f, -1.0f );
	PerpendicularVector( right, direction );
	CrossProduct( direction, right, up );
	VectorCopy( playerOrigin, origin );

	VectorCopy( playerOrigin, originBase );
	if ( elevatedShell ) {
		originBase[2] += EXP_JUICED_ORIGIN_OFFSET;
	}

	VectorMA( originBase, EXP_RING_CENTER_OFFSET, direction, center );

	for ( i = 0; i < 10; i++ ) {
		angle = i * EXP_RING_STEP;
		rightRadius = cos( angle ) * ( EXP_RING_RADIUS + crandom() * EXP_RING_RADIUS_JITTER );
		upRadius = sin( angle ) * ( EXP_RING_RADIUS + crandom() * EXP_RING_RADIUS_JITTER );

		VectorCopy( center, point );
		VectorMA( point, rightRadius, right, point );
		VectorMA( point, upRadius, up, point );

		VectorSubtract( point, originBase, velocity );
		VectorMA( velocity, EXP_RING_VELOCITY, direction, velocity );

		velocity[0] *= EXP_RING_VELOCITY_SCALE + crandom() * EXP_RING_VELOCITY_JITTER;
		velocity[1] *= EXP_RING_VELOCITY_SCALE + crandom() * EXP_RING_VELOCITY_JITTER;
		velocity[2] *= EXP_RING_VELOCITY_SCALE + crandom() * EXP_RING_VELOCITY_JITTER;

		CG_LaunchExplode( origin, velocity, cg_gibSphereModel );
	}
}

/*
==================
CG_LaunchFragmentEntity
==================
*/
static localEntity_t *CG_LaunchFragmentEntity( const vec3_t origin, const vec3_t velocity, qhandle_t hModel,
	leType_t leType, int baseLifetime, int randomLifetime, float bounceFactor,
	leFragmentBounceSoundType_t bounceSoundType, leFragmentMarkType_t markType ) {
	localEntity_t	*le;
	refEntity_t		*re;

	le = CG_AllocLocalEntity();
	re = &le->refEntity;

	le->leType = leType;
	le->startTime = cg.time;
	le->endTime = le->startTime + baseLifetime + random() * randomLifetime;

	VectorCopy( origin, re->origin );
	AxisCopy( axisDefault, re->axis );
	re->hModel = hModel;

	le->pos.trType = TR_GRAVITY;
	VectorCopy( origin, le->pos.trBase );
	VectorCopy( velocity, le->pos.trDelta );
	le->pos.trTime = cg.time;

	le->bounceFactor = bounceFactor;
	le->fragmentBounceSoundType = bounceSoundType;
	le->fragmentMarkType = markType;

	return le;
}

/*
==================
CG_LaunchGib
==================
*/
void CG_LaunchGib( vec3_t origin, vec3_t velocity, qhandle_t hModel ) {
	CG_LaunchFragmentEntity( origin, velocity, hModel, LE_FRAGMENT, 5000, 3000, 0.6f,
		LEBS_BLOOD, LEMT_BLOOD );
}

/*
==================
CG_LaunchThawGib
==================
*/
static void CG_LaunchThawGib( vec3_t origin, vec3_t velocity, qhandle_t hModel ) {
	CG_LaunchFragmentEntity( origin, velocity, hModel, LE_FRAGMENT, 5000, 3000, 0.6f,
		LEBS_ICE, LEMT_ICE );
}

/*
===================
CG_ThawPlayer

Retail thaw burst using alternating brain/abdomen shards.
===================
*/
#define	GIB_VELOCITY	250
#define	GIB_JUMP		250
void CG_ThawPlayer( vec3_t playerOrigin ) {
	vec3_t		origin, velocity;
	qhandle_t	thawModels[7];
	int			i;

	if ( !cg_blood.integer ) {
		return;
	}

	if ( !cgs.media.gibBrain || !cgs.media.gibAbdomen ) {
		return;
	}

	thawModels[0] = cgs.media.gibBrain;
	thawModels[1] = cgs.media.gibAbdomen;
	thawModels[2] = cgs.media.gibBrain;
	thawModels[3] = cgs.media.gibAbdomen;
	thawModels[4] = cgs.media.gibBrain;
	thawModels[5] = cgs.media.gibAbdomen;
	thawModels[6] = cgs.media.gibBrain;

	VectorCopy( playerOrigin, origin );

	for ( i = 0; i < ARRAY_LEN( thawModels ); i++ ) {
		velocity[0] = crandom() * GIB_VELOCITY;
		velocity[1] = crandom() * GIB_VELOCITY;
		velocity[2] = GIB_JUMP + crandom() * GIB_VELOCITY;
		CG_LaunchThawGib( origin, velocity, thawModels[i] );
	}
}

/*
===================
CG_GibPlayer

Generated a bunch of gibs launching out from the bodies location
===================
*/
void CG_GibPlayer( vec3_t playerOrigin ) {
	vec3_t	origin, velocity;
	qhandle_t	gibModels[13];
	int		i;

	if ( !cg_blood.integer ) {
		return;
	}

	if ( !cgs.media.haveDlcGibs ) {
		CG_BigExplode( playerOrigin );
		return;
	}

	gibModels[0] = cgs.media.gibChest;
	gibModels[1] = cgs.media.gibAbdomen;
	gibModels[2] = cgs.media.gibIntestine;
	gibModels[3] = cgs.media.gibArm;
	gibModels[4] = cgs.media.gibArm;
	gibModels[5] = cgs.media.gibForearm;
	gibModels[6] = cgs.media.gibForearm;
	gibModels[7] = cgs.media.gibFist;
	gibModels[8] = cgs.media.gibFist;
	gibModels[9] = cgs.media.gibLeg;
	gibModels[10] = cgs.media.gibLeg;
	gibModels[11] = cgs.media.gibFoot;
	gibModels[12] = cgs.media.gibFoot;

	if ( !( rand() & 1 ) ) {
		VectorCopy( playerOrigin, origin );
		velocity[0] = crandom() * GIB_VELOCITY;
		velocity[1] = crandom() * GIB_VELOCITY;
		velocity[2] = GIB_JUMP + crandom() * GIB_VELOCITY;
		CG_LaunchGib( origin, velocity, cgs.media.gibSkull );

		VectorCopy( playerOrigin, origin );
		velocity[0] = crandom() * GIB_VELOCITY;
		velocity[1] = crandom() * GIB_VELOCITY;
		velocity[2] = GIB_JUMP + crandom() * GIB_VELOCITY;
		CG_LaunchGib( origin, velocity, cgs.media.gibBrain );
	}

	for ( i = 0; i < ARRAY_LEN( gibModels ); i++ ) {
		VectorCopy( playerOrigin, origin );
		velocity[0] = crandom() * GIB_VELOCITY;
		velocity[1] = crandom() * GIB_VELOCITY;
		velocity[2] = GIB_JUMP + crandom() * GIB_VELOCITY;
		CG_LaunchGib( origin, velocity, gibModels[i] );
	}
}

/*
===================
CG_DetonateJuicedPlayer

Retail shares the juiced detonation wrapper between the event fallback and the
later invulnerability timeout.
===================
*/
void CG_DetonateJuicedPlayer( const vec3_t playerOrigin, qboolean immediateFallback ) {
	if ( cgs.media.haveDlcGibs ) {
		vec3_t	origin;

		VectorCopy( playerOrigin, origin );
		CG_GibPlayer( origin );
		return;
	}

	if ( cg_gibSphereModel ) {
		CG_LaunchBigExplodeFragments( playerOrigin, !immediateFallback );
	}

	CG_SpawnBigExplodeEffects( playerOrigin, !immediateFallback );
}

/*
==================
CG_LaunchExplode
==================
*/
void CG_LaunchExplode( const vec3_t origin, const vec3_t velocity, qhandle_t hModel ) {
	localEntity_t	*le;

	le = CG_LaunchFragmentEntity( origin, velocity, hModel, LE_FRAGMENT_14, 375, 750, 0.35f,
		LEBS_ELECTRO, LEMT_BURN_SMALL );
	le->pos.trType = TR_QL_ACCEL;
	le->posTrajExtra = 425.0f;
	le->startTime = cg.time + crandom() * 250.0f;
	le->endTime = le->startTime + 375 + random() * 750.0f;
}

/*
===================
CG_BigExplode

Retail no-DLC gib fallback using sphere fragments and the death-effect sprite.
===================
*/
void CG_BigExplode( vec3_t playerOrigin ) {
	if ( cg_gibSphereModel ) {
		CG_LaunchBigExplodeFragments( playerOrigin, qfalse );
	}

	CG_SpawnBigExplodeEffects( playerOrigin, qfalse );
}

/*
===================
CG_BigExplodeJuiced

Retail invulnerability fallback keeps the deathEffect/tracer shell elevated.
===================
*/
void CG_BigExplodeJuiced( vec3_t playerOrigin ) {
	if ( cg_gibSphereModel ) {
		CG_LaunchBigExplodeFragments( playerOrigin, qtrue );
	}

	CG_SpawnBigExplodeEffects( playerOrigin, qtrue );
}

