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
// cg_weapons.c -- events and effects dealing with weapons
#include "cg_local.h"

#define CG_PREDICTED_HITSCAN_LIFETIME 200

typedef struct {
	const char	*shaderName;
	int		segments;
} cgLightningStyleDef_t;

static const cgLightningStyleDef_t cg_lightningStyleDefs[CG_MAX_LIGHTNING_STYLES] = {
	{ "lightningBolt1", 1 },
	{ "lightningBolt2", 1 },
	{ "lightningBolt3", 2 },
	{ "lightningBolt4", 1 },
	{ "lightningBolt5", 3 }
};

static int		cg_lightningImpactFrameTime;
static int		cg_lightningImpactCount;
static int		cg_weaponTogglePrevious;
static int		cg_weaponToggleFallback;
static qboolean	CG_GetStoredPredictedBeam( weapon_t weapon, vec3_t start, vec3_t end, qboolean *hitWorld );

/*
==========================
CG_GetLocalPlayerWeaponTeam

Resolves the local team the same way the retail weapon-color helpers do.
==========================
*/
static team_t CG_GetLocalPlayerWeaponTeam( void ) {
	if ( cg.snap ) {
		return (team_t)cg.snap->ps.persistant[PERS_TEAM];
	}
	if ( cg.clientNum >= 0 && cg.clientNum < MAX_CLIENTS ) {
		const clientInfo_t	*selfInfo;

		selfInfo = &cgs.clientinfo[cg.clientNum];
		if ( selfInfo->infoValid ) {
			return selfInfo->team;
		}
	}

	return TEAM_FREE;
}

/*
==========================
CG_ClientInfoToClientNum

Converts a clientInfo pointer back into a stable client index when possible.
==========================
*/
static int CG_ClientInfoToClientNum( const clientInfo_t *ci ) {
	if ( !ci ) {
		return -1;
	}
	if ( ci < cgs.clientinfo || ci >= cgs.clientinfo + MAX_CLIENTS ) {
		return -1;
	}

	return (int)( ci - cgs.clientinfo );
}

/*
==========================
CG_CopyBaseWeaponColor

Retail falls back to the raw user weapon colors for the local player and for
non-overridden clients.
==========================
*/
static void CG_CopyBaseWeaponColor( const clientInfo_t *ci, qboolean secondary, vec3_t colorOut ) {
	if ( !colorOut ) {
		return;
	}
	if ( !ci ) {
		VectorSet( colorOut, 1.0f, 1.0f, 1.0f );
		return;
	}

	if ( secondary ) {
		VectorCopy( ci->color2, colorOut );
	} else {
		VectorCopy( ci->color1, colorOut );
	}
}

/*
==========================
CG_PackWeaponColorBytes

Stores a normalized RGB triplet as packed render bytes, optionally dimmed by
the retail rail-ring tint scale.
==========================
*/
static void CG_PackWeaponColorBytes( const vec3_t color, float scale, byte *rgbOut ) {
	int		i;
	float	channel;

	if ( !rgbOut ) {
		return;
	}
	if ( !color ) {
		rgbOut[0] = 255;
		rgbOut[1] = 255;
		rgbOut[2] = 255;
		return;
	}

	for ( i = 0; i < 3; i++ ) {
		channel = color[i] * scale * 255.0f;
		if ( channel < 0.0f ) {
			channel = 0.0f;
		} else if ( channel > 255.0f ) {
			channel = 255.0f;
		}
		rgbOut[i] = (byte)channel;
	}
}

/*
==========================
CG_ShouldOverrideWeaponColor

Retail only applies team/enemy weapon-color forcing to other clients. The local
player always falls back to the raw weapon colors.
==========================
*/
static qboolean CG_ShouldOverrideWeaponColor( const clientInfo_t *ci ) {
	team_t	localTeam;
	int		clientNum;

	clientNum = CG_ClientInfoToClientNum( ci );
	if ( clientNum < 0 || clientNum == cg.clientNum ) {
		return qfalse;
	}

	if ( cgs.gametype < GT_TEAM ) {
		return (qboolean)cg_forceEnemyWeaponColor.integer;
	}

	localTeam = CG_GetLocalPlayerWeaponTeam();
	if ( localTeam > TEAM_FREE && localTeam != TEAM_SPECTATOR &&
		ci->team > TEAM_FREE && ci->team != TEAM_SPECTATOR &&
		localTeam == ci->team ) {
		return (qboolean)cg_forceTeamWeaponColor.integer;
	}

	return (qboolean)cg_forceEnemyWeaponColor.integer;
}

/*
==========================
CG_ResolveClientWeaponColor

Retail override helper shared by the rail core, flash, and impact-mark paths.
The byte output remains full-bright while the paired float tint is pre-scaled
for the local-entity fade users.
==========================
*/
static qboolean CG_ResolveClientWeaponColor( const clientInfo_t *ci, byte *rgbOut, vec3_t colorOut ) {
	if ( !ci || !CG_ShouldOverrideWeaponColor( ci ) ) {
		return qfalse;
	}

	CG_PackWeaponColorBytes( ci->upperColor, 1.0f, rgbOut );
	if ( colorOut ) {
		VectorScale( ci->upperColor, 0.75f, colorOut );
	}

	return qtrue;
}

/*
===============================
CG_ResolveClientWeaponColorBytes

Retail byte-only sibling used by the rail-ring path, which stores the dimmed
ring tint directly in the render RGBA bytes.
===============================
*/
static qboolean CG_ResolveClientWeaponColorBytes( const clientInfo_t *ci, byte *rgbOut ) {
	if ( !ci || !CG_ShouldOverrideWeaponColor( ci ) ) {
		return qfalse;
	}

	CG_PackWeaponColorBytes( ci->upperColor, 0.75f, rgbOut );
	return qtrue;
}

/*
===========================
CG_GetViewWeaponFovOffset

Retail shares this FOV-driven vertical gun offset between the first-person
weapon placement path and the local rail-start adjustment.
===========================
*/
static float CG_GetViewWeaponFovOffset( void ) {
	if ( cg_fov.integer > 90 ) {
		return -0.2f * ( cg_fov.integer - 90 );
	}

	return 0.0f;
}

/*
=========================================
CG_GetLocalRailThirdPersonVerticalOffset

Retail uses model-specific vertical nudges for the local third-person rail
origin. The promoted names come directly from the HLIL string comparisons.
=========================================
*/
static float CG_GetLocalRailThirdPersonVerticalOffset( const clientInfo_t *ci ) {
	static const char *const raisedModels[] = {
		"bitterman",
		"major",
		"orbb",
		"razor",
		"sarge",
		"slash",
		"visor",
		"xaero"
	};
	int	i;

	if ( ci ) {
		for ( i = 0; i < ARRAY_LEN( raisedModels ); i++ ) {
			if ( !Q_stricmp( ci->modelName, raisedModels[i] ) ) {
				return 1.0f;
			}
		}
		if ( !Q_stricmp( ci->modelName, "ranger" ) ) {
			return -4.0f;
		}
		if ( !Q_stricmp( ci->modelName, "uriel" ) ) {
			return -8.0f;
		}
	}

	return -3.5f;
}

/*
==========================
CG_AdjustRailTrailStart

Retail offsets the recovered muzzle origin differently for remote shooters, the
local first-person weapon view, and the local third-person chasecam path.
==========================
*/
static void CG_AdjustRailTrailStart( const clientInfo_t *ci, vec3_t start ) {
	int		clientNum;
	float	fovOffset;

	clientNum = CG_ClientInfoToClientNum( ci );
	if ( clientNum != cg.clientNum ) {
		VectorMA( start, 5.0f, cg.refdef.viewaxis[1], start );
		VectorMA( start, -4.0f, cg.refdef.viewaxis[2], start );
		return;
	}

	if ( cg.renderingThirdPerson ) {
		VectorMA( start, -5.5f, cg.refdef.viewaxis[1], start );
		VectorMA( start, CG_GetLocalRailThirdPersonVerticalOffset( ci ), cg.refdef.viewaxis[2], start );
		return;
	}

	fovOffset = CG_GetViewWeaponFovOffset();
	VectorMA( start, cg_gun_x.value + 5.0f, cg.refdef.viewaxis[0], start );
	VectorMA( start, cg_gun_y.value * 0.75f, cg.refdef.viewaxis[1], start );
	VectorMA( start, cg_gun_z.value + fovOffset - 5.0f, cg.refdef.viewaxis[2], start );
}

/*
===========================
CG_GetDamageThroughProbeDistance

Retail parses the backside damage-through probe distance from configstring
`0x2A5`; the reconstructed source names that slot
`CS_DOMINATION_CAPTURE_TIME`, and it still defaults to `5`.
===========================
*/
static float CG_GetDamageThroughProbeDistance( void ) {
	const char	*value;
	float		probeDistance;

	probeDistance = 5.0f;
	value = CG_ConfigString( CS_DOMINATION_CAPTURE_TIME );
	if ( value && *value ) {
		probeDistance = (float)atof( value );
	}
	if ( probeDistance <= 0.0f ) {
		probeDistance = 5.0f;
	}

	return probeDistance;
}

/*
===============
CG_GetWeaponReloadTime

Returns the active reload duration from the live pmove cache, falling back to
the shared defaults when the replicated override is absent.
===============
*/
static int CG_GetWeaponReloadTime( weapon_t weapon ) {
	const pmove_settings_t	*defaults;
	int			reloadTime;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return 0;
	}

	reloadTime = cg_pmoveSettings.weaponReloadTimes[weapon];
	if ( reloadTime > 0 ) {
		return reloadTime;
	}

	defaults = PM_GetDefaultSettings();
	if ( defaults ) {
		return defaults->weaponReloadTimes[weapon];
	}

	return 0;
}

/*
===============
CG_SetWeaponSelect

Keeps the last two local weapon selections in sync so retail `weapon toggle`
semantics survive autoswitches, respawns, and other non-command changes.
===============
*/
void CG_SetWeaponSelect( int weapon ) {
	if ( cg.weaponSelect == weapon ) {
		return;
	}

	cg_weaponToggleFallback = cg_weaponTogglePrevious;
	cg_weaponTogglePrevious = cg.weaponSelect;
	cg.weaponSelect = weapon;
}

/*
==========================
CG_MachineGunEjectBrass
==========================
*/
static void CG_MachineGunEjectBrass( centity_t *cent ) {
	localEntity_t	*le;
	refEntity_t		*re;
	vec3_t			velocity, xvelocity;
	vec3_t			offset, xoffset;
	float			waterScale = 1.0f;
	vec3_t			v[3];

	if ( cg_brassTime.integer <= 0 ) {
		return;
	}

	le = CG_AllocLocalEntity();
	re = &le->refEntity;

	velocity[0] = 0;
	velocity[1] = -50 + 40 * crandom();
	velocity[2] = 100 + 50 * crandom();

	le->leType = LE_FRAGMENT;
	le->startTime = cg.time;
	le->endTime = le->startTime + cg_brassTime.integer + ( cg_brassTime.integer / 4 ) * random();

	le->pos.trType = TR_GRAVITY;
	le->pos.trTime = cg.time - (rand()&15);

	AnglesToAxis( cent->lerpAngles, v );

	offset[0] = 8;
	offset[1] = -4;
	offset[2] = 24;

	xoffset[0] = offset[0] * v[0][0] + offset[1] * v[1][0] + offset[2] * v[2][0];
	xoffset[1] = offset[0] * v[0][1] + offset[1] * v[1][1] + offset[2] * v[2][1];
	xoffset[2] = offset[0] * v[0][2] + offset[1] * v[1][2] + offset[2] * v[2][2];
	VectorAdd( cent->lerpOrigin, xoffset, re->origin );

	VectorCopy( re->origin, le->pos.trBase );

	if ( CG_PointContents( re->origin, -1 ) & CONTENTS_WATER ) {
		waterScale = 0.10f;
	}

	xvelocity[0] = velocity[0] * v[0][0] + velocity[1] * v[1][0] + velocity[2] * v[2][0];
	xvelocity[1] = velocity[0] * v[0][1] + velocity[1] * v[1][1] + velocity[2] * v[2][1];
	xvelocity[2] = velocity[0] * v[0][2] + velocity[1] * v[1][2] + velocity[2] * v[2][2];
	VectorScale( xvelocity, waterScale, le->pos.trDelta );

	AxisCopy( axisDefault, re->axis );
	re->hModel = cgs.media.machinegunBrassModel;

	le->bounceFactor = 0.4 * waterScale;

	le->angles.trType = TR_LINEAR;
	le->angles.trTime = cg.time;
	le->angles.trBase[0] = rand()&31;
	le->angles.trBase[1] = rand()&31;
	le->angles.trBase[2] = rand()&31;
	le->angles.trDelta[0] = 2;
	le->angles.trDelta[1] = 1;
	le->angles.trDelta[2] = 0;

	le->leFlags = LEF_TUMBLE;
	le->fragmentBounceSoundType = LEBS_BRASS;
	le->fragmentMarkType = LEMT_NONE;
}

/*
==========================
CG_ShotgunEjectBrass
==========================
*/
static void CG_ShotgunEjectBrass( centity_t *cent ) {
	localEntity_t	*le;
	refEntity_t		*re;
	vec3_t			velocity, xvelocity;
	vec3_t			offset, xoffset;
	vec3_t			v[3];
	int				i;

	if ( cg_brassTime.integer <= 0 ) {
		return;
	}

	for ( i = 0; i < 2; i++ ) {
		float	waterScale = 1.0f;

		le = CG_AllocLocalEntity();
		re = &le->refEntity;

		velocity[0] = 60 + 60 * crandom();
		if ( i == 0 ) {
			velocity[1] = 40 + 10 * crandom();
		} else {
			velocity[1] = -40 + 10 * crandom();
		}
		velocity[2] = 100 + 50 * crandom();

		le->leType = LE_FRAGMENT;
		le->startTime = cg.time;
		le->endTime = le->startTime + cg_brassTime.integer*3 + cg_brassTime.integer * random();

		le->pos.trType = TR_GRAVITY;
		le->pos.trTime = cg.time;

		AnglesToAxis( cent->lerpAngles, v );

		offset[0] = 8;
		offset[1] = 0;
		offset[2] = 24;

		xoffset[0] = offset[0] * v[0][0] + offset[1] * v[1][0] + offset[2] * v[2][0];
		xoffset[1] = offset[0] * v[0][1] + offset[1] * v[1][1] + offset[2] * v[2][1];
		xoffset[2] = offset[0] * v[0][2] + offset[1] * v[1][2] + offset[2] * v[2][2];
		VectorAdd( cent->lerpOrigin, xoffset, re->origin );
		VectorCopy( re->origin, le->pos.trBase );
		if ( CG_PointContents( re->origin, -1 ) & CONTENTS_WATER ) {
			waterScale = 0.10f;
		}

		xvelocity[0] = velocity[0] * v[0][0] + velocity[1] * v[1][0] + velocity[2] * v[2][0];
		xvelocity[1] = velocity[0] * v[0][1] + velocity[1] * v[1][1] + velocity[2] * v[2][1];
		xvelocity[2] = velocity[0] * v[0][2] + velocity[1] * v[1][2] + velocity[2] * v[2][2];
		VectorScale( xvelocity, waterScale, le->pos.trDelta );

		AxisCopy( axisDefault, re->axis );
		re->hModel = cgs.media.shotgunBrassModel;
		le->bounceFactor = 0.3f;

		le->angles.trType = TR_LINEAR;
		le->angles.trTime = cg.time;
		le->angles.trBase[0] = rand()&31;
		le->angles.trBase[1] = rand()&31;
		le->angles.trBase[2] = rand()&31;
		le->angles.trDelta[0] = 1;
		le->angles.trDelta[1] = 0.5;
		le->angles.trDelta[2] = 0;

		le->leFlags = LEF_TUMBLE;
		le->fragmentBounceSoundType = LEBS_BRASS;
		le->fragmentMarkType = LEMT_NONE;
	}
}


/*
==========================
CG_NailgunEjectBrass
==========================
*/
static void CG_NailgunEjectBrass( centity_t *cent ) {
	localEntity_t	*smoke;
	vec3_t			origin;
	vec3_t			v[3];
	vec3_t			offset;
	vec3_t			xoffset;
	vec3_t			up;

	AnglesToAxis( cent->lerpAngles, v );

	offset[0] = 0;
	offset[1] = -12;
	offset[2] = 24;

	xoffset[0] = offset[0] * v[0][0] + offset[1] * v[1][0] + offset[2] * v[2][0];
	xoffset[1] = offset[0] * v[0][1] + offset[1] * v[1][1] + offset[2] * v[2][1];
	xoffset[2] = offset[0] * v[0][2] + offset[1] * v[1][2] + offset[2] * v[2][2];
	VectorAdd( cent->lerpOrigin, xoffset, origin );

	VectorSet( up, 0, 0, 64 );

	smoke = CG_SmokePuff( origin, up, 32, 1, 1, 1, 0.33f, 700, cg.time, 0, 0, cgs.media.smokePuffShader );
	// use the optimized local entity add
	smoke->leType = LE_SCALE_FADE;
}


/*
==========================
CG_SpawnRailRing

Retail `cg_railStyle 1` uses the renderer-side `RT_RAIL_RINGS` beam instead of
the older sprite spiral.
==========================
*/
static void CG_SpawnRailRing( const vec3_t start, const vec3_t end, const clientInfo_t *ci ) {
	localEntity_t	*le;
	refEntity_t	*re;
	vec3_t		color;
	byte		rgb[3];

	le = CG_AllocLocalEntity();
	re = &le->refEntity;

	le->leType = LE_FADE_RGB;
	le->startTime = cg.time;
	le->endTime = cg.time + cg_railTrailTime.value;
	if ( le->endTime <= le->startTime ) {
		le->endTime = le->startTime + 1;
	}
	le->lifeRate = 1.0f / ( le->endTime - le->startTime );

	re->shaderTime = cg.time / 1000.0f;
	re->reType = RT_RAIL_RINGS;
	re->customShader = cgs.media.railRingsShader;
	VectorCopy( start, re->origin );
	VectorCopy( end, re->oldorigin );

	if ( !CG_ResolveClientWeaponColorBytes( ci, rgb ) ) {
		CG_CopyBaseWeaponColor( ci, qtrue, color );
		CG_PackWeaponColorBytes( color, 1.0f, rgb );
	}
	re->shaderRGBA[0] = rgb[0];
	re->shaderRGBA[1] = rgb[1];
	re->shaderRGBA[2] = rgb[2];
	re->shaderRGBA[3] = 255;

	if ( !CG_ResolveClientWeaponColor( ci, NULL, le->color ) ) {
		CG_CopyBaseWeaponColor( ci, qtrue, color );
		VectorScale( color, 0.75f, le->color );
	}
	le->color[3] = 1.0f;
}

/*
==========================
CG_RailTrail
==========================
*/
void CG_RailTrail (clientInfo_t *ci, vec3_t start, vec3_t end) {
	vec3_t axis[36], move, move2, next_move, vec, temp;
	vec3_t color;
	float  len;
	int    i, j, skip;
	byte	rgb[3];
 
	localEntity_t *le;
	refEntity_t   *re;
 
#define RADIUS   4
#define ROTATION 1
#define SPACING  5
 
	CG_AdjustRailTrailStart( ci, start );
	VectorCopy (start, move);
	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);
	PerpendicularVector(temp, vec);
	for (i = 0 ; i < 36; i++) {
		RotatePointAroundVector(axis[i], vec, temp, i * 10);//banshee 2.4 was 10
	}
 
	le = CG_AllocLocalEntity();
	re = &le->refEntity;
 
	le->leType = LE_FADE_RGB;
	le->startTime = cg.time;
	le->endTime = cg.time + cg_railTrailTime.value;
	le->lifeRate = 1.0 / (le->endTime - le->startTime);
 
	re->shaderTime = cg.time / 1000.0f;
	re->reType = RT_RAIL_CORE;
	re->customShader = cgs.media.railCoreShader;
 
	VectorCopy(start, re->origin);
	VectorCopy(end, re->oldorigin);

	if ( !CG_ResolveClientWeaponColor( ci, rgb, le->color ) ) {
		CG_CopyBaseWeaponColor( ci, qfalse, color );
		CG_PackWeaponColorBytes( color, 1.0f, rgb );
		VectorScale( color, 0.75f, le->color );
	}
	re->shaderRGBA[0] = rgb[0];
	re->shaderRGBA[1] = rgb[1];
	re->shaderRGBA[2] = rgb[2];
	re->shaderRGBA[3] = 255;
	le->color[3] = 1.0f;

	AxisClear( re->axis );
 
	VectorMA(move, 20, vec, move);
	VectorCopy(move, next_move);
	VectorScale (vec, SPACING, vec);

	if ( cg_railStyle.integer != 2 ) {
		CG_SpawnRailRing( start, end, ci );
		return;
	}
	skip = -1;
 
	j = 18;
    for (i = 0; i < len; i += SPACING) {
		if (i != skip) {
			skip = i + SPACING;
			le = CG_AllocLocalEntity();
            re = &le->refEntity;
            le->leFlags = LEF_PUFF_DONT_SCALE;
			le->leType = LE_MOVE_SCALE_FADE;
            le->startTime = cg.time;
            le->endTime = cg.time + (i>>1) + 600;
            le->lifeRate = 1.0 / (le->endTime - le->startTime);

            re->shaderTime = cg.time / 1000.0f;
            re->reType = RT_SPRITE;
            re->radius = 1.1f;
			re->customShader = cgs.media.railRingsShader;

			if ( !CG_ResolveClientWeaponColorBytes( ci, rgb ) ) {
				CG_CopyBaseWeaponColor( ci, qtrue, color );
				CG_PackWeaponColorBytes( color, 1.0f, rgb );
			}
			re->shaderRGBA[0] = rgb[0];
			re->shaderRGBA[1] = rgb[1];
			re->shaderRGBA[2] = rgb[2];
			re->shaderRGBA[3] = 255;

			if ( !CG_ResolveClientWeaponColor( ci, NULL, le->color ) ) {
				CG_CopyBaseWeaponColor( ci, qtrue, color );
				VectorScale( color, 0.75f, le->color );
			}
            le->color[3] = 1.0f;

            le->pos.trType = TR_LINEAR;
            le->pos.trTime = cg.time;

			VectorCopy( move, move2);
            VectorMA(move2, RADIUS , axis[j], move2);
            VectorCopy(move2, le->pos.trBase);

            le->pos.trDelta[0] = axis[j][0]*6;
            le->pos.trDelta[1] = axis[j][1]*6;
            le->pos.trDelta[2] = axis[j][2]*6;
		}

        VectorAdd (move, vec, move);

        j = j + ROTATION < 36 ? j + ROTATION : (j + ROTATION) % 36;
	}
}

/*
==========================
CG_RocketTrail
==========================
*/
static void CG_RocketTrail( centity_t *ent, const weaponInfo_t *wi ) {
	int		step;
	vec3_t	origin, lastPos;
	int		t;
	int		startTime, contents;
	int		lastContents;
	entityState_t	*es;
	vec3_t	up;
	localEntity_t	*smoke;

	if ( cg_noProjectileTrail.integer ) {
		return;
	}

	up[0] = 0;
	up[1] = 0;
	up[2] = 0;

	step = 50;

	es = &ent->currentState;
	startTime = ent->trailTime;
	t = step * ( (startTime + step) / step );

	BG_EvaluateTrajectory( &es->pos, cg.time, origin );
	contents = CG_PointContents( origin, -1 );

	// if object (e.g. grenade) is stationary, don't toss up smoke
	if ( es->pos.trType == TR_STATIONARY ) {
		ent->trailTime = cg.time;
		return;
	}

	BG_EvaluateTrajectory( &es->pos, ent->trailTime, lastPos );
	lastContents = CG_PointContents( lastPos, -1 );

	ent->trailTime = cg.time;

	if ( contents & ( CONTENTS_WATER | CONTENTS_SLIME | CONTENTS_LAVA ) ) {
		if ( contents & lastContents & CONTENTS_WATER ) {
			CG_BubbleTrail( lastPos, origin, 8 );
		}
		return;
	}

	for ( ; t <= ent->trailTime ; t += step ) {
		BG_EvaluateTrajectory( &es->pos, t, lastPos );

		smoke = CG_SmokePuff( lastPos, up, 
					  wi->trailRadius, 
					  1, 1, 1, 0.33f,
					  wi->wiTrailTime, 
					  t,
					  0,
					  0, 
					  cgs.media.smokePuffShader );
		// use the optimized local entity add
		smoke->leType = LE_SCALE_FADE;
	}

}

/*
==========================
CG_NailTrail
==========================
*/
static void CG_NailTrail( centity_t *ent, const weaponInfo_t *wi ) {
	int		step;
	vec3_t	origin, lastPos;
	int		t;
	int		startTime, contents;
	int		lastContents;
	entityState_t	*es;
	vec3_t	up;
	localEntity_t	*smoke;

	if ( cg_noProjectileTrail.integer ) {
		return;
	}

	up[0] = 0;
	up[1] = 0;
	up[2] = 0;

	step = 50;

	es = &ent->currentState;
	startTime = ent->trailTime;
	t = step * ( (startTime + step) / step );

	BG_EvaluateTrajectory( &es->pos, cg.time, origin );
	contents = CG_PointContents( origin, -1 );

	// if object (e.g. grenade) is stationary, don't toss up smoke
	if ( es->pos.trType == TR_STATIONARY ) {
		ent->trailTime = cg.time;
		return;
	}

	BG_EvaluateTrajectory( &es->pos, ent->trailTime, lastPos );
	lastContents = CG_PointContents( lastPos, -1 );

	ent->trailTime = cg.time;

	if ( contents & ( CONTENTS_WATER | CONTENTS_SLIME | CONTENTS_LAVA ) ) {
		if ( contents & lastContents & CONTENTS_WATER ) {
			CG_BubbleTrail( lastPos, origin, 8 );
		}
		return;
	}

	for ( ; t <= ent->trailTime ; t += step ) {
		BG_EvaluateTrajectory( &es->pos, t, lastPos );

		smoke = CG_SmokePuff( lastPos, up, 
					  wi->trailRadius, 
					  1, 1, 1, 0.33f,
					  wi->wiTrailTime, 
					  t,
					  0,
					  0, 
					  cgs.media.nailPuffShader );
		// use the optimized local entity add
		smoke->leType = LE_SCALE_FADE;
	}

}

/*
==========================
CG_NailTrail
==========================
*/
static void CG_PlasmaTrail( centity_t *cent, const weaponInfo_t *wi ) {
	localEntity_t	*le;
	refEntity_t		*re;
	entityState_t	*es;
	vec3_t			velocity, xvelocity, origin;
	vec3_t			offset, xoffset;
	vec3_t			v[3];
	int				t, startTime, step;

	float	waterScale = 1.0f;

	if ( cg_noProjectileTrail.integer || cg_oldPlasma.integer ) {
		return;
	}

	step = 50;

	es = &cent->currentState;
	startTime = cent->trailTime;
	t = step * ( (startTime + step) / step );

	BG_EvaluateTrajectory( &es->pos, cg.time, origin );

	le = CG_AllocLocalEntity();
	re = &le->refEntity;

	velocity[0] = 60 - 120 * crandom();
	velocity[1] = 40 - 80 * crandom();
	velocity[2] = 100 - 200 * crandom();

	le->leType = LE_MOVE_SCALE_FADE;
	le->leFlags = LEF_TUMBLE;
	le->fragmentBounceSoundType = LEBS_NONE;
	le->fragmentMarkType = LEMT_NONE;

	le->startTime = cg.time;
	le->endTime = le->startTime + 600;

	le->pos.trType = TR_GRAVITY;
	le->pos.trTime = cg.time;

	AnglesToAxis( cent->lerpAngles, v );

	offset[0] = 2;
	offset[1] = 2;
	offset[2] = 2;

	xoffset[0] = offset[0] * v[0][0] + offset[1] * v[1][0] + offset[2] * v[2][0];
	xoffset[1] = offset[0] * v[0][1] + offset[1] * v[1][1] + offset[2] * v[2][1];
	xoffset[2] = offset[0] * v[0][2] + offset[1] * v[1][2] + offset[2] * v[2][2];

	VectorAdd( origin, xoffset, re->origin );
	VectorCopy( re->origin, le->pos.trBase );

	if ( CG_PointContents( re->origin, -1 ) & CONTENTS_WATER ) {
		waterScale = 0.10f;
	}

	xvelocity[0] = velocity[0] * v[0][0] + velocity[1] * v[1][0] + velocity[2] * v[2][0];
	xvelocity[1] = velocity[0] * v[0][1] + velocity[1] * v[1][1] + velocity[2] * v[2][1];
	xvelocity[2] = velocity[0] * v[0][2] + velocity[1] * v[1][2] + velocity[2] * v[2][2];
	VectorScale( xvelocity, waterScale, le->pos.trDelta );

	AxisCopy( axisDefault, re->axis );
    re->shaderTime = cg.time / 1000.0f;
    re->reType = RT_SPRITE;
    re->radius = 0.25f;
	re->customShader = cgs.media.railRingsShader;
	le->bounceFactor = 0.3f;

    re->shaderRGBA[0] = wi->flashDlightColor[0] * 63;
    re->shaderRGBA[1] = wi->flashDlightColor[1] * 63;
    re->shaderRGBA[2] = wi->flashDlightColor[2] * 63;
    re->shaderRGBA[3] = 63;

    le->color[0] = wi->flashDlightColor[0] * 0.2;
    le->color[1] = wi->flashDlightColor[1] * 0.2;
    le->color[2] = wi->flashDlightColor[2] * 0.2;
    le->color[3] = 0.25f;

	le->angles.trType = TR_LINEAR;
	le->angles.trTime = cg.time;
	le->angles.trBase[0] = rand()&31;
	le->angles.trBase[1] = rand()&31;
	le->angles.trBase[2] = rand()&31;
	le->angles.trDelta[0] = 1;
	le->angles.trDelta[1] = 0.5;
	le->angles.trDelta[2] = 0;

}
/*
==========================
CG_GrappleTrail
==========================
*/
void CG_GrappleTrail( centity_t *ent, const weaponInfo_t *wi ) {
	vec3_t	origin;
	entityState_t	*es;
	vec3_t			forward, up;
	refEntity_t		beam;

	es = &ent->currentState;

	BG_EvaluateTrajectory( &es->pos, cg.time, origin );
	ent->trailTime = cg.time;

	memset( &beam, 0, sizeof( beam ) );
	VectorCopy ( cg_entities[ ent->currentState.otherEntityNum ].lerpOrigin, beam.origin );
	beam.origin[2] += DEFAULT_VIEWHEIGHT;
	AngleVectors( cg_entities[ ent->currentState.otherEntityNum ].lerpAngles, forward, NULL, up );
	VectorMA( beam.origin, 14, forward, beam.origin );
	VectorMA( beam.origin, -6, up, beam.origin );
	VectorCopy( origin, beam.oldorigin );

	if (Distance( beam.origin, beam.oldorigin ) < 64 )
		return; // Don't draw if close

	beam.reType = RT_LIGHTNING;
	if ( cgs.media.grapplingChainShader ) {
		beam.customShader = cgs.media.grapplingChainShader;
	} else {
		beam.customShader = cgs.media.lightningShader;
	}

	AxisClear( beam.axis );
	beam.shaderRGBA[0] = 0xff;
	beam.shaderRGBA[1] = 0xff;
	beam.shaderRGBA[2] = 0xff;
	beam.shaderRGBA[3] = 0xff;
	trap_R_AddRefEntityToScene( &beam );
}

/*
==========================
CG_GrenadeTrail
==========================
*/
static void CG_GrenadeTrail( centity_t *ent, const weaponInfo_t *wi ) {
	CG_RocketTrail( ent, wi );
}


/*
=================
CG_RegisterWeapon

The server says this item is used on this level
=================
*/
void CG_RegisterWeapon( int weaponNum ) {
	weaponInfo_t	*weaponInfo;
	gitem_t			*item, *ammo;
	char			path[MAX_QPATH];
	vec3_t			mins, maxs;
	int				i;

	weaponInfo = &cg_weapons[weaponNum];

	if ( weaponNum == 0 ) {
		return;
	}

	if ( weaponInfo->registered ) {
		return;
	}

	memset( weaponInfo, 0, sizeof( *weaponInfo ) );
	weaponInfo->registered = qtrue;

	for ( item = bg_itemlist + 1 ; item->classname ; item++ ) {
		if ( item->giType == IT_WEAPON && BG_WeaponForItemTag( item->giTag ) == weaponNum ) {
			weaponInfo->item = item;
			break;
		}
	}
	if ( !item->classname ) {
		CG_Error( "Couldn't find weapon %i", weaponNum );
	}
	CG_RegisterItemVisuals( item - bg_itemlist );

	// load cmodel before model so filecache works
	weaponInfo->weaponModel = trap_R_RegisterModel( item->world_model[0] );

	// calc midpoint for rotation
	trap_R_ModelBounds( weaponInfo->weaponModel, mins, maxs );
	for ( i = 0 ; i < 3 ; i++ ) {
		weaponInfo->weaponMidpoint[i] = mins[i] + 0.5 * ( maxs[i] - mins[i] );
	}

	weaponInfo->weaponIcon = trap_R_RegisterShader( item->icon );
	weaponInfo->ammoIcon = trap_R_RegisterShader( item->icon );

	for ( ammo = bg_itemlist + 1 ; ammo->classname ; ammo++ ) {
		if ( ammo->giType == IT_AMMO && BG_WeaponForItemTag( ammo->giTag ) == weaponNum ) {
			break;
		}
	}
	if ( ammo->classname && ammo->world_model[0] ) {
		weaponInfo->ammoModel = trap_R_RegisterModel( ammo->world_model[0] );
	}

	strcpy( path, item->world_model[0] );
	COM_StripExtension( path, path );
	strcat( path, "_flash.md3" );
	weaponInfo->flashModel = trap_R_RegisterModel( path );

	strcpy( path, item->world_model[0] );
	COM_StripExtension( path, path );
	strcat( path, "_barrel.md3" );
	weaponInfo->barrelModel = trap_R_RegisterModel( path );

	strcpy( path, item->world_model[0] );
	COM_StripExtension( path, path );
	strcat( path, "_hand.md3" );
	weaponInfo->handsModel = trap_R_RegisterModel( path );

	if ( !weaponInfo->handsModel ) {
		weaponInfo->handsModel = trap_R_RegisterModel( "models/weapons2/shotgun/shotgun_hand.md3" );
	}

	weaponInfo->loopFireSound = qfalse;

	switch ( weaponNum ) {
	case WP_GAUNTLET:
		MAKERGB( weaponInfo->flashDlightColor, 0.6f, 0.6f, 1.0f );
		weaponInfo->firingSound = trap_S_RegisterSound( "sound/weapons/melee/fstrun.ogg", qfalse );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/melee/fstatck.ogg", qfalse );
		break;

	case WP_LIGHTNING:
		MAKERGB( weaponInfo->flashDlightColor, 0.6f, 0.6f, 1.0f );
		weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/melee/fsthum.ogg", qfalse );
		weaponInfo->firingSound = trap_S_RegisterSound( "sound/weapons/lightning/lg_hum.ogg", qfalse );

		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/lightning/lg_fire.ogg", qfalse );
		cgs.media.lightningShader = trap_R_RegisterShader( "lightningBolt1" );
		{
			int		styleIndex;

			for ( styleIndex = 0; styleIndex < CG_MAX_LIGHTNING_STYLES; ++styleIndex ) {
				const char		*styleName;

				styleName = cg_lightningStyleDefs[styleIndex].shaderName;
				if ( !styleName || !styleName[0] ) {
					cgs.media.lightningStyleShaders[styleIndex] = 0;
					continue;
				}

				cgs.media.lightningStyleShaders[styleIndex] = trap_R_RegisterShader( styleName );
			}

			if ( cgs.media.lightningStyleShaders[0] ) {
				cgs.media.lightningShader = cgs.media.lightningStyleShaders[0];
			} else {
				cgs.media.lightningStyleShaders[0] = cgs.media.lightningShader;
			}
		}
		cgs.media.lightningExplosionModel = trap_R_RegisterModel( "models/weaphits/crackle.md3" );
		cgs.media.sfx_lghit1 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit.ogg", qfalse );
		cgs.media.sfx_lghit2 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit2.ogg", qfalse );
		cgs.media.sfx_lghit3 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit3.ogg", qfalse );

		break;

	case WP_GRAPPLING_HOOK:
		MAKERGB( weaponInfo->flashDlightColor, 0.6f, 0.6f, 1.0f );
		weaponInfo->missileModel = trap_R_RegisterModel( "models/weapons2/grapple/grapple_hook.md3" );
		weaponInfo->missileTrailFunc = CG_GrappleTrail;
		weaponInfo->missileDlight = 200;
		weaponInfo->wiTrailTime = 2000;
		weaponInfo->trailRadius = 64;
		MAKERGB( weaponInfo->missileDlightColor, 1, 0.75f, 0 );
		cgs.media.grapplingChainShader = trap_R_RegisterShader( "grapplingChain" );
		weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/grapple/grhang.ogg", qfalse );
		weaponInfo->firingSound = trap_S_RegisterSound( "sound/weapons/grapple/grfire.ogg", qfalse );
		weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/grapple/grfire.ogg", qfalse );
		trap_S_RegisterSound( "sound/weapons/grapple/grpull.ogg", qfalse );
		trap_S_RegisterSound( "sound/weapons/grapple/grreset.ogg", qfalse );
		break;

	case WP_CHAINGUN:
		weaponInfo->firingSound = trap_S_RegisterSound( "sound/weapons/vulcan/wvulfire.ogg", qfalse );
		weaponInfo->loopFireSound = qtrue;
		MAKERGB( weaponInfo->flashDlightColor, 1, 1, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf1b.ogg", qfalse );
		weaponInfo->flashSound[1] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf2b.ogg", qfalse );
		weaponInfo->flashSound[2] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf3b.ogg", qfalse );
		weaponInfo->flashSound[3] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf4b.ogg", qfalse );
		weaponInfo->ejectBrassFunc = CG_MachineGunEjectBrass;
		cgs.media.bulletExplosionShader = trap_R_RegisterShader( "bulletExplosion" );
		break;

	case WP_MACHINEGUN:
		MAKERGB( weaponInfo->flashDlightColor, 1, 1, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/machinegun/machgf1b.ogg", qfalse );
		weaponInfo->flashSound[1] = trap_S_RegisterSound( "sound/weapons/machinegun/machgf2b.ogg", qfalse );
		weaponInfo->flashSound[2] = trap_S_RegisterSound( "sound/weapons/machinegun/machgf3b.ogg", qfalse );
		weaponInfo->flashSound[3] = trap_S_RegisterSound( "sound/weapons/machinegun/machgf4b.ogg", qfalse );
		weaponInfo->ejectBrassFunc = CG_MachineGunEjectBrass;
		cgs.media.bulletExplosionShader = trap_R_RegisterShader( "bulletExplosion" );
		break;

	case WP_HEAVY_MACHINEGUN:
		MAKERGB( weaponInfo->flashDlightColor, 1, 1, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/hmg/machgf1b.ogg", qfalse );
		weaponInfo->flashSound[1] = trap_S_RegisterSound( "sound/weapons/hmg/machgf2b.ogg", qfalse );
		weaponInfo->flashSound[2] = trap_S_RegisterSound( "sound/weapons/hmg/machgf3b.ogg", qfalse );
		weaponInfo->flashSound[3] = trap_S_RegisterSound( "sound/weapons/hmg/machgf4b.ogg", qfalse );
		cgs.media.bulletExplosionShader = trap_R_RegisterShader( "bulletExplosion" );
		break;

	case WP_SHOTGUN:
		MAKERGB( weaponInfo->flashDlightColor, 1, 1, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/shotgun/sshotf1b.ogg", qfalse );
		weaponInfo->ejectBrassFunc = CG_ShotgunEjectBrass;
		break;

	case WP_ROCKET_LAUNCHER:
		weaponInfo->missileModel = trap_R_RegisterModel( "models/ammo/rocket/rocket.md3" );
		weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/rocket/rockfly.ogg", qfalse );
		weaponInfo->missileTrailFunc = CG_RocketTrail;
		weaponInfo->missileDlight = 200;
		weaponInfo->wiTrailTime = 2000;
		weaponInfo->trailRadius = 64;
		
		MAKERGB( weaponInfo->missileDlightColor, 1, 0.75f, 0 );
		MAKERGB( weaponInfo->flashDlightColor, 1, 0.75f, 0 );

		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/rocket/rocklf1a.ogg", qfalse );
		cgs.media.rocketExplosionShader = trap_R_RegisterShader( "rocketExplosion" );
		break;

	case WP_PROX_LAUNCHER:
		weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/proxmine.md3" );
		weaponInfo->missileTrailFunc = CG_GrenadeTrail;
		weaponInfo->wiTrailTime = 700;
		weaponInfo->trailRadius = 32;
		MAKERGB( weaponInfo->flashDlightColor, 1, 0.70f, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/proxmine/wstbfire.ogg", qfalse );
		cgs.media.grenadeExplosionShader = trap_R_RegisterShader( "grenadeExplosion" );
		break;

	case WP_GRENADE_LAUNCHER:
		weaponInfo->missileModel = trap_R_RegisterModel( "models/ammo/grenade1.md3" );
		weaponInfo->missileTrailFunc = CG_GrenadeTrail;
		weaponInfo->wiTrailTime = 700;
		weaponInfo->trailRadius = 32;
		MAKERGB( weaponInfo->flashDlightColor, 1, 0.70f, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/grenade/grenlf1a.ogg", qfalse );
		cgs.media.grenadeExplosionShader = trap_R_RegisterShader( "grenadeExplosion" );
		break;

	case WP_NAILGUN:
		weaponInfo->ejectBrassFunc = CG_NailgunEjectBrass;
		weaponInfo->missileTrailFunc = CG_NailTrail;
//		weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/nailgun/wnalflit.ogg", qfalse );
		weaponInfo->trailRadius = 16;
		weaponInfo->wiTrailTime = 250;
		weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/nail.md3" );
		MAKERGB( weaponInfo->flashDlightColor, 1, 0.75f, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/nailgun/wnalfire.ogg", qfalse );
		break;

	case WP_PLASMAGUN:
//		weaponInfo->missileModel = cgs.media.invulnerabilityPowerupModel;
		weaponInfo->missileTrailFunc = CG_PlasmaTrail;
		weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/plasma/lasfly.ogg", qfalse );
		MAKERGB( weaponInfo->flashDlightColor, 0.6f, 0.6f, 1.0f );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/plasma/hyprbf1a.ogg", qfalse );
		cgs.media.plasmaExplosionShader = trap_R_RegisterShader( "plasmaExplosion" );
		cgs.media.railRingsShader = trap_R_RegisterShader( "railDisc" );
		break;

	case WP_RAILGUN:
		weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/railgun/rg_hum.ogg", qfalse );
		MAKERGB( weaponInfo->flashDlightColor, 1, 0.5f, 0 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/railgun/railgf1a.ogg", qfalse );
		cgs.media.railExplosionShader = trap_R_RegisterShader( "railExplosion" );
		cgs.media.railRingsShader = trap_R_RegisterShader( "railDisc" );
		cgs.media.railCoreShader = trap_R_RegisterShader( "railCore" );
		break;

	case WP_BFG:
		weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/bfg/bfg_hum.ogg", qfalse );
		MAKERGB( weaponInfo->flashDlightColor, 1, 0.7f, 1 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/bfg/bfg_fire.ogg", qfalse );
		cgs.media.bfgExplosionShader = trap_R_RegisterShader( "bfgExplosion" );
		weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/bfg.md3" );
		weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/rocket/rockfly.ogg", qfalse );
		break;

	 default:
		MAKERGB( weaponInfo->flashDlightColor, 1, 1, 1 );
		weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/rocket/rocklf1a.ogg", qfalse );
		break;
	}
}

/*
=================
CG_RegisterItemVisuals

The server says this item is used on this level
=================
*/
void CG_RegisterItemVisuals( int itemNum ) {
	itemInfo_t		*itemInfo;
	gitem_t			*item;

	if ( itemNum < 0 || itemNum >= bg_numItems ) {
		CG_Error( "CG_RegisterItemVisuals: itemNum %d out of range [0-%d]", itemNum, bg_numItems-1 );
	}

	itemInfo = &cg_items[ itemNum ];
	if ( itemInfo->registered ) {
		return;
	}

	item = &bg_itemlist[ itemNum ];

	memset( itemInfo, 0, sizeof( &itemInfo ) );
	itemInfo->registered = qtrue;

	itemInfo->models[0] = trap_R_RegisterModel( item->world_model[0] );

	itemInfo->icon = trap_R_RegisterShader( item->icon );

	if ( item->giType == IT_WEAPON ) {
		CG_RegisterWeapon( BG_WeaponForItemTag( item->giTag ) );
	}

	//
	// powerups have an accompanying ring or sphere
	//
	if ( item->giType == IT_POWERUP || item->giType == IT_HEALTH || 
		item->giType == IT_ARMOR || item->giType == IT_HOLDABLE ) {
		if ( item->world_model[1] ) {
			itemInfo->models[1] = trap_R_RegisterModel( item->world_model[1] );
		}
	}
}


/*
========================================================================================

VIEW WEAPON

========================================================================================
*/

/*
=================
CG_MapTorsoToWeaponFrame

=================
*/
static int CG_MapTorsoToWeaponFrame( clientInfo_t *ci, int frame ) {

	// change weapon
	if ( frame >= ci->animations[TORSO_DROP].firstFrame 
		&& frame < ci->animations[TORSO_DROP].firstFrame + 9 ) {
		return frame - ci->animations[TORSO_DROP].firstFrame + 6;
	}

	// stand attack
	if ( frame >= ci->animations[TORSO_ATTACK].firstFrame 
		&& frame < ci->animations[TORSO_ATTACK].firstFrame + 6 ) {
		return 1 + frame - ci->animations[TORSO_ATTACK].firstFrame;
	}

	// stand attack 2
	if ( frame >= ci->animations[TORSO_ATTACK2].firstFrame 
		&& frame < ci->animations[TORSO_ATTACK2].firstFrame + 6 ) {
		return 1 + frame - ci->animations[TORSO_ATTACK2].firstFrame;
	}
	
	return 0;
}


/*
==============
CG_CalculateWeaponPosition
==============
*/
static void CG_CalculateWeaponPosition( vec3_t origin, vec3_t angles ) {
	float	scale;
	int		delta;
	float	fracsin;

	VectorCopy( cg.refdef.vieworg, origin );
	VectorCopy( cg.refdefViewAngles, angles );

	// on odd legs, invert some angles
	if ( cg.bobcycle & 1 ) {
		scale = -cg.xyspeed;
	} else {
		scale = cg.xyspeed;
	}

	// gun angles from bobbing
	angles[ROLL] += scale * cg.bobfracsin * 0.005;
	angles[YAW] += scale * cg.bobfracsin * 0.01;
	angles[PITCH] += cg.xyspeed * cg.bobfracsin * 0.005;

	// drop the weapon when landing
	delta = cg.time - cg.landTime;
	if ( delta < LAND_DEFLECT_TIME ) {
		origin[2] += cg.landChange*0.25 * delta / LAND_DEFLECT_TIME;
	} else if ( delta < LAND_DEFLECT_TIME + LAND_RETURN_TIME ) {
		origin[2] += cg.landChange*0.25 * 
			(LAND_DEFLECT_TIME + LAND_RETURN_TIME - delta) / LAND_RETURN_TIME;
	}

#if 0
	// drop the weapon when stair climbing
	delta = cg.time - cg.stepTime;
	if ( delta < STEP_TIME/2 ) {
		origin[2] -= cg.stepChange*0.25 * delta / (STEP_TIME/2);
	} else if ( delta < STEP_TIME ) {
		origin[2] -= cg.stepChange*0.25 * (STEP_TIME - delta) / (STEP_TIME/2);
	}
#endif

	// idle drift
	scale = cg.xyspeed + 40;
	fracsin = sin( cg.time * 0.001 );
	angles[ROLL] += scale * fracsin * 0.01;
	angles[YAW] += scale * fracsin * 0.01;
	angles[PITCH] += scale * fracsin * 0.01;
}




/*
=============
CG_LightningActiveStyleIndex

Returns the zero-based lightning style index derived from cg_lightningStyle.
=============
*/
static int CG_LightningActiveStyleIndex( void ) {
	int		style;
	int		index;

	style = cg_lightningStyle.integer;
	index = style - 1;
	if ( index < 0 ) {
		index = 0;
	}
	if ( index >= CG_MAX_LIGHTNING_STYLES ) {
		index = CG_MAX_LIGHTNING_STYLES - 1;
	}

	return index;
}


/*
=============
CG_LightningCurrentShader

Fetches the shader handle for the active lightning style.
=============
*/
static qhandle_t CG_LightningCurrentShader( void ) {
	int		index;
	qhandle_t	handle;

	index = CG_LightningActiveStyleIndex();
	handle = cgs.media.lightningStyleShaders[index];
	if ( !handle ) {
		handle = cgs.media.lightningShader;
	}
	return handle;
}


/*
=============
CG_LightningSegmentCount

Returns the number of beam submissions to draw for the active style.
=============
*/
static int CG_LightningSegmentCount( void ) {
	int		index;
	int		segments;

	index = CG_LightningActiveStyleIndex();
	segments = cg_lightningStyleDefs[index].segments;
	if ( segments <= 0 ) {
		segments = 1;
	}
	return segments;
}


/*
=============
CG_SubmitLightningBeams

Submits the lightning beam to the renderer the requested number of times.
=============
*/
static void CG_SubmitLightningBeams( const refEntity_t *beamTemplate, int segmentCount ) {
	int		i;
	refEntity_t	beam;

	if ( segmentCount <= 0 ) {
		segmentCount = 1;
	}

	for ( i = 0; i < segmentCount; ++i ) {
		beam = *beamTemplate;
		beam.shaderTime += (float)i * 0.01f;
		trap_R_AddRefEntityToScene( &beam );
	}
}


/*
=============
CG_CanDrawLightningImpact

Checks whether the lightning impact effect can be emitted this frame.
=============
*/
static qboolean CG_CanDrawLightningImpact( void ) {
	int		cap;

	if ( cg_lightningImpact.integer == 0 ) {
		return qfalse;
	}

	cap = cg_lightningImpactCap.integer;
	if ( cap <= 0 ) {
		return qfalse;
	}

	if ( cg.time != cg_lightningImpactFrameTime ) {
		cg_lightningImpactFrameTime = cg.time;
		cg_lightningImpactCount = 0;
	}

	if ( cg_lightningImpactCount >= cap ) {
		return qfalse;
	}

	cg_lightningImpactCount++;
	return qtrue;
}


/*
=============
CG_DrawLightningImpact

Spawns the lightning impact model when the beam hits a surface.
=============
*/
static void CG_DrawLightningImpact( const vec3_t endPos, const vec3_t dir ) {
	refEntity_t	beam;
	vec3_t	angles;
	vec3_t	origin;

	if ( !CG_CanDrawLightningImpact() || !cgs.media.lightningExplosionModel ) {
		return;
	}

	memset( &beam, 0, sizeof( beam ) );
	beam.hModel = cgs.media.lightningExplosionModel;

	VectorMA( endPos, -16, dir, origin );
	VectorCopy( origin, beam.origin );

	angles[0] = rand() % 360;
	angles[1] = rand() % 360;
	angles[2] = rand() % 360;
	AnglesToAxis( angles, beam.axis );
	trap_R_AddRefEntityToScene( &beam );
}

/*
===============
CG_LightningBolt

Origin will be the exact tag point, which is slightly
different than the muzzle point used for determining hits.
The cent should be the non-predicted cent if it is from the player,
so the endpoint will reflect the simulated strike (lagging the predicted
angle)
===============
*/
static void CG_LightningBolt( centity_t *cent, vec3_t origin ) {
	trace_t	 trace;
	refEntity_t	 beam;
	vec3_t	 forward;
	vec3_t	 muzzlePoint, endPoint;
	qboolean	 usedPrediction;
	qboolean	 addImpact;
	vec3_t	 storedStart;
	vec3_t	 storedEnd;
	qboolean	 storedHit;
	vec3_t	 impactPoint;

	if ( cent->currentState.weapon != WP_LIGHTNING ) {
		return;
	}

	memset( &beam, 0, sizeof( beam ) );
	usedPrediction = qfalse;
	addImpact = qfalse;

	if ( cg.predictLocalRailshots && cent->currentState.number == cg.predictedPlayerState.clientNum ) {
		if ( CG_GetStoredPredictedBeam( WP_LIGHTNING, storedStart, storedEnd, &storedHit ) ) {
			usedPrediction = qtrue;
			addImpact = storedHit;
			VectorCopy( storedStart, beam.origin );
			VectorCopy( storedEnd, beam.oldorigin );
			VectorCopy( storedEnd, impactPoint );
		}
	}

	if ( !usedPrediction ) {
		// CPMA  "true" lightning
		if ( ( cent->currentState.number == cg.predictedPlayerState.clientNum ) && ( cg_trueLightning.value != 0 ) ) {
			vec3_t angle;
			int i;

			for ( i = 0; i < 3; i++ ) {
				float a = cent->lerpAngles[i] - cg.refdefViewAngles[i];
				if ( a > 180 ) {
					a -= 360;
				}
				if ( a < -180 ) {
					a += 360;
				}

				angle[i] = cg.refdefViewAngles[i] + a * ( 1.0 - cg_trueLightning.value );
				if ( angle[i] < 0 ) {
					angle[i] += 360;
				}
				if ( angle[i] > 360 ) {
					angle[i] -= 360;
				}
			}

			AngleVectors( angle, forward, NULL, NULL );
			VectorCopy( cent->lerpOrigin, muzzlePoint );
		} else {
			AngleVectors( cent->lerpAngles, forward, NULL, NULL );
			VectorCopy( cent->lerpOrigin, muzzlePoint );
		}

		// FIXME: crouch
		muzzlePoint[2] += DEFAULT_VIEWHEIGHT;

		VectorMA( muzzlePoint, 14, forward, muzzlePoint );

		// project forward by the lightning range
		VectorMA( muzzlePoint, LIGHTNING_RANGE, forward, endPoint );

		// see if it hit a wall
		CG_Trace( &trace, muzzlePoint, vec3_origin, vec3_origin, endPoint,
				cent->currentState.number, MASK_SHOT );

		// this is the endpoint
		VectorCopy( trace.endpos, beam.oldorigin );

		// use the provided origin, even though it may be slightly
		// different than the muzzle origin
		VectorCopy( origin, beam.origin );
		VectorCopy( trace.endpos, impactPoint );
		addImpact = ( trace.fraction < 1.0f );
	}

	beam.reType = RT_LIGHTNING;
	beam.customShader = CG_LightningCurrentShader();
	CG_SubmitLightningBeams( &beam, CG_LightningSegmentCount() );

	// add the impact flare if it hit something
	if ( addImpact ) {
		vec3_t angles;
		vec3_t dir;

		VectorSubtract( beam.oldorigin, beam.origin, dir );
		VectorNormalize( dir );

		memset( &beam, 0, sizeof( beam ) );
		beam.hModel = cgs.media.lightningExplosionModel;

		VectorMA( impactPoint, -16, dir, beam.origin );

		// make a random orientation
		angles[0] = rand() % 360;
		angles[1] = rand() % 360;
		angles[2] = rand() % 360;
		AnglesToAxis( angles, beam.axis );
		trap_R_AddRefEntityToScene( &beam );
		CG_DrawLightningImpact( impactPoint, dir );
	}

}
/*

static void CG_LightningBolt( centity_t *cent, vec3_t origin ) {
	trace_t		trace;
	refEntity_t		beam;
	vec3_t			forward;
	vec3_t			muzzlePoint, endPoint;

	if ( cent->currentState.weapon != WP_LIGHTNING ) {
		return;
	}

	memset( &beam, 0, sizeof( beam ) );

	// find muzzle point for this frame
	VectorCopy( cent->lerpOrigin, muzzlePoint );
	AngleVectors( cent->lerpAngles, forward, NULL, NULL );

	// FIXME: crouch
	muzzlePoint[2] += DEFAULT_VIEWHEIGHT;

	VectorMA( muzzlePoint, 14, forward, muzzlePoint );

	// project forward by the lightning range
	VectorMA( muzzlePoint, LIGHTNING_RANGE, forward, endPoint );

	// see if it hit a wall
	CG_Trace( &trace, muzzlePoint, vec3_origin, vec3_origin, endPoint, 
		cent->currentState.number, MASK_SHOT );

	// this is the endpoint
	VectorCopy( trace.endpos, beam.oldorigin );

	// use the provided origin, even though it may be slightly
	// different than the muzzle origin
	VectorCopy( origin, beam.origin );

	beam.reType = RT_LIGHTNING;
	beam.customShader = cgs.media.lightningShader;
	trap_R_AddRefEntityToScene( &beam );

	// add the impact flare if it hit something
	if ( trace.fraction < 1.0 ) {
		vec3_t	angles;
		vec3_t	dir;

		VectorSubtract( beam.oldorigin, beam.origin, dir );
		VectorNormalize( dir );

		memset( &beam, 0, sizeof( beam ) );
		beam.hModel = cgs.media.lightningExplosionModel;

		VectorMA( trace.endpos, -16, dir, beam.origin );

		// make a random orientation
		angles[0] = rand() % 360;
		angles[1] = rand() % 360;
		angles[2] = rand() % 360;
		AnglesToAxis( angles, beam.axis );
		trap_R_AddRefEntityToScene( &beam );
	}
}
*/

/*
=====================
CG_SnapVectorTowards

Matches the server rail snap helper so predicted local rail endpoints are
rounded the same way as the later event payload.
=====================
*/
static void CG_SnapVectorTowards( vec3_t v, vec3_t to ) {
	int		i;

	for ( i = 0; i < 3; i++ ) {
		if ( to[i] <= v[i] ) {
			v[i] = (float)( (int)v[i] );
		} else {
			v[i] = (float)( (int)v[i] + 1 );
		}
	}
}

/*
===============================
CG_BuildPredictedRailForPlayerState

Retail local rail prediction walks through up to four pass-through hits before
submitting the final trail and impact. Rebuild that terminal client trace from
the predicted player state so the predicted event matches the later server one.
===============================
*/
qboolean CG_BuildPredictedRailForPlayerState( const playerState_t *ps, int clientNum,
	vec3_t start, vec3_t end, vec3_t impactDir, qboolean *addImpact ) {
	trace_t	trace;
	vec3_t	forward;
	vec3_t	right;
	vec3_t	up;
	vec3_t	muzzle;
	vec3_t	traceStart;
	vec3_t	finish;
	int		railHits;

	if ( !ps ) {
		return qfalse;
	}
	if ( !cg.predictLocalRailshots ) {
		return qfalse;
	}
	if ( clientNum != cg.predictedPlayerState.clientNum ) {
		return qfalse;
	}

	VectorCopy( ps->origin, muzzle );
	muzzle[2] += ps->viewheight;
	AngleVectors( ps->viewangles, forward, right, up );
	VectorMA( muzzle, 5, forward, muzzle );

	VectorCopy( muzzle, traceStart );
	VectorCopy( muzzle, start );
	VectorMA( start, 4, right, start );
	VectorMA( start, -1, up, start );
	VectorMA( traceStart, 8192, forward, finish );

	railHits = 0;
	do {
		CG_Trace( &trace, traceStart, vec3_origin, vec3_origin, finish, clientNum, MASK_SHOT );
		if ( trace.entityNum >= ENTITYNUM_MAX_NORMAL || trace.allsolid ) {
			break;
		}
		if ( trace.contents & CONTENTS_SOLID ) {
			break;
		}

		railHits++;
		if ( railHits >= 4 ) {
			break;
		}

		VectorCopy( trace.endpos, traceStart );
		VectorMA( traceStart, 1.0f, forward, traceStart );
	} while ( qtrue );

	VectorCopy( trace.endpos, end );
	CG_SnapVectorTowards( end, muzzle );

	if ( addImpact ) {
		*addImpact = (qboolean)( !( trace.surfaceFlags & SURF_NOIMPACT ) );
	}
	if ( impactDir ) {
		VectorCopy( trace.plane.normal, impactDir );
	}

	return qtrue;
}

/*
===============================
CG_BuildPredictedBeamForPlayerState

Builds the predicted muzzle start/end pair for local hitscan weapons using a
supplied predicted player state.
===============================
*/
qboolean CG_BuildPredictedBeamForPlayerState( const playerState_t *ps, int clientNum, weapon_t weapon,
	vec3_t start, vec3_t end, qboolean *hitWorld ) {
	trace_t	trace;
	vec3_t	forward;
	vec3_t	right;
	vec3_t	up;
	vec3_t	muzzle;
	vec3_t	traceStart;
	vec3_t	finish;
	qboolean	localHit;

	if ( !ps ) {
		return qfalse;
	}
	if ( !cg.predictLocalRailshots ) {
		return qfalse;
	}
	if ( clientNum != cg.predictedPlayerState.clientNum ) {
		return qfalse;
	}
	if ( weapon != WP_RAILGUN && weapon != WP_LIGHTNING ) {
		return qfalse;
	}

	VectorCopy( ps->origin, muzzle );
	muzzle[2] += ps->viewheight;
	AngleVectors( ps->viewangles, forward, right, up );
	VectorMA( muzzle, 14, forward, muzzle );

	VectorCopy( muzzle, traceStart );
	VectorCopy( muzzle, start );
	if ( weapon == WP_RAILGUN ) {
		VectorMA( start, 4, right, start );
		VectorMA( start, -1, up, start );
		VectorMA( traceStart, 8192, forward, finish );
	} else {
		VectorMA( traceStart, LIGHTNING_RANGE, forward, finish );
	}

	CG_Trace( &trace, traceStart, vec3_origin, vec3_origin, finish, clientNum, MASK_SHOT );
	VectorCopy( trace.endpos, end );
	localHit = ( trace.fraction < 1.0f );
	if ( hitWorld ) {
		*hitWorld = localHit;
	}

	return qtrue;
}

/*
=============
CG_BuildPredictedBeam

Builds the predicted muzzle start/end pair for local hitscan weapons.
=============
*/
static qboolean CG_BuildPredictedBeam( centity_t *cent, weapon_t weapon, vec3_t start, vec3_t end, qboolean *hitWorld ) {
	return CG_BuildPredictedBeamForPlayerState( &cg.predictedPlayerState, cent->currentState.number,
		weapon, start, end, hitWorld );
}

/*
=============
CG_GetStoredPredictedBeam

Returns the cached start/end data for a previously predicted hitscan.
=============
*/
static qboolean CG_GetStoredPredictedBeam( weapon_t weapon, vec3_t start, vec3_t end, qboolean *hitWorld ) {
	if ( !cg.predictLocalRailshots ) {
		return qfalse;
	}

	switch ( weapon ) {
	case WP_RAILGUN:
		if ( !cg.predictedLocalRailValid ) {
			return qfalse;
		}
		if ( cg.time - cg.predictedLocalRailTime > CG_PREDICTED_HITSCAN_LIFETIME ) {
			return qfalse;
		}
		VectorCopy( cg.predictedLocalRailStart, start );
		VectorCopy( cg.predictedLocalRailEnd, end );
		if ( hitWorld ) {
			*hitWorld = cg.predictedLocalRailHit;
		}
		return qtrue;
	case WP_LIGHTNING:
		if ( !cg.predictedLocalLightningValid ) {
			return qfalse;
		}
		if ( cg.time - cg.predictedLocalLightningTime > CG_PREDICTED_HITSCAN_LIFETIME ) {
			return qfalse;
		}
		VectorCopy( cg.predictedLocalLightningStart, start );
		VectorCopy( cg.predictedLocalLightningEnd, end );
		if ( hitWorld ) {
			*hitWorld = cg.predictedLocalLightningHit;
		}
		return qtrue;
	default:
		break;
	}

	return qfalse;
}

/*
===============
CG_SpawnRailTrail

Origin will be the exact tag point, which is slightly
different than the muzzle point used for determining hits.
===============
*/
static void CG_SpawnRailTrail( centity_t *cent, vec3_t origin ) {
	clientInfo_t	*ci;
	vec3_t	start;
	vec3_t	end;

	if ( cent->currentState.weapon != WP_RAILGUN ) {
		return;
	}
	if ( !cent->pe.railgunFlash ) {
		return;
	}

	cent->pe.railgunFlash = qfalse;
	VectorCopy( origin, start );
	VectorCopy( cent->pe.railgunImpact, end );
	ci = &cgs.clientinfo[ cent->currentState.clientNum ];
	CG_RailTrail( ci, start, end );
}


/*
======================
CG_MachinegunSpinAngle
======================
*/
#define		SPIN_SPEED	0.9
#define		COAST_TIME	1000
static float	CG_MachinegunSpinAngle( centity_t *cent ) {
	int		delta;
	float	angle;
	float	speed;

	delta = cg.time - cent->pe.barrelTime;
	if ( cent->pe.barrelSpinning ) {
		angle = cent->pe.barrelAngle + delta * SPIN_SPEED;
	} else {
		if ( delta > COAST_TIME ) {
			delta = COAST_TIME;
		}

		speed = 0.5 * ( SPIN_SPEED + (float)( COAST_TIME - delta ) / COAST_TIME );
		angle = cent->pe.barrelAngle + delta * speed;
	}

	if ( cent->pe.barrelSpinning == !(cent->currentState.eFlags & EF_FIRING) ) {
		cent->pe.barrelTime = cg.time;
		cent->pe.barrelAngle = AngleMod( angle );
		cent->pe.barrelSpinning = !!(cent->currentState.eFlags & EF_FIRING);
		if ( cent->currentState.weapon == WP_CHAINGUN && !cent->pe.barrelSpinning ) {
			trap_S_StartSound( NULL, cent->currentState.number, CHAN_WEAPON, cgs.media.sfx_chgwind );
		}
	}

	return angle;
}


/*
========================
CG_AddWeaponWithPowerups
========================
*/
static void CG_AddWeaponWithPowerups( const centity_t *cent, refEntity_t *gun ) {
	int		powerups;

	powerups = cent->currentState.powerups;

	// add powerup effects
	if ( powerups & ( 1 << PW_INVIS ) ) {
		gun->customShader = cgs.media.invisShader;
		trap_R_AddRefEntityToScene( gun );
	} else {
		trap_R_AddRefEntityToScene( gun );

		if ( powerups & ( 1 << PW_BATTLESUIT ) ) {
			gun->customShader = cgs.media.battleWeaponShader;
			trap_R_AddRefEntityToScene( gun );
		}
		if ( powerups & ( 1 << PW_QUAD ) ) {
			gun->customShader = cgs.media.quadWeaponShader;
			trap_R_AddRefEntityToScene( gun );
		}
	}
}


/*
=============
CG_AddPlayerWeapon

Used for both the view weapon (ps is valid) and the world modelother character models (ps is NULL)
The main player will have this called for BOTH cases, so effects like light and
sound should only be done on the world model case.
=============
*/
void CG_AddPlayerWeapon( refEntity_t *parent, playerState_t *ps, centity_t *cent, int team ) {
	refEntity_t	gun;
	refEntity_t	barrel;
	refEntity_t	ammo;
	refEntity_t	flash;
	vec3_t		angles;
	weapon_t	weaponNum;
	weaponInfo_t	*weapon;
	centity_t	*nonPredictedCent;
	qboolean	drawFlash;
	qboolean	continuousFlash;
//	int	col;

	weaponNum = cent->currentState.weapon;

	CG_RegisterWeapon( weaponNum );
	weapon = &cg_weapons[weaponNum];
	// Retail registers cg_muzzleFlash but does not gate the flash path on it.
	drawFlash = qtrue;
	continuousFlash = ( weaponNum == WP_LIGHTNING || weaponNum == WP_GAUNTLET || weaponNum == WP_GRAPPLING_HOOK );

	// add the weapon
	memset( &gun, 0, sizeof( gun ) );
	VectorCopy( parent->lightingOrigin, gun.lightingOrigin );
	gun.shadowPlane = parent->shadowPlane;
	gun.renderfx = parent->renderfx;

	// set custom shading for railgun refire rate
	if ( ps ) {
		if ( cg.predictedPlayerState.weapon == WP_RAILGUN 
			&& cg.predictedPlayerState.weaponstate == WEAPON_FIRING ) {
			float	f;
			int	railReloadTime;

			railReloadTime = CG_GetWeaponReloadTime( WP_RAILGUN );
			if ( railReloadTime <= 0 ) {
				railReloadTime = 1500;
			}

			f = (float)cg.predictedPlayerState.weaponTime / (float)railReloadTime;
			gun.shaderRGBA[1] = 0;
			gun.shaderRGBA[0] = 
			gun.shaderRGBA[2] = 255 * ( 1.0 - f );
		} else {
			gun.shaderRGBA[0] = 255;
			gun.shaderRGBA[1] = 255;
			gun.shaderRGBA[2] = 255;
			gun.shaderRGBA[3] = 255;
		}
	}

	gun.hModel = weapon->weaponModel;
	if (!gun.hModel) {
		return;
	}

	if ( !ps ) {
		// add weapon ready sound
		cent->pe.lightningFiring = qfalse;
		if ( ( cent->currentState.eFlags & EF_FIRING ) && weapon->firingSound ) {
			// lightning gun and guantlet make a different sound when fire is held down
			trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, weapon->firingSound );
			cent->pe.lightningFiring = qtrue;
		} else if ( weapon->readySound ) {
			trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, weapon->readySound );
		}
	}

	CG_PositionEntityOnTag( &gun, parent, parent->hModel, "tag_weapon");

	CG_AddWeaponWithPowerups( cent, &gun );

	// add the spinning barrel
	if ( weapon->barrelModel ) {
		memset( &barrel, 0, sizeof( barrel ) );
		VectorCopy( parent->lightingOrigin, barrel.lightingOrigin );
		barrel.shadowPlane = parent->shadowPlane;
		barrel.renderfx = parent->renderfx;

		barrel.hModel = weapon->barrelModel;
		angles[YAW] = 0;
		angles[PITCH] = 0;
		angles[ROLL] = CG_MachinegunSpinAngle( cent );
		AnglesToAxis( angles, barrel.axis );

		CG_PositionRotatedEntityOnTag( &barrel, &gun, weapon->weaponModel, "tag_barrel" );

		CG_AddWeaponWithPowerups( cent, &barrel );
	}

	if ( weaponNum == WP_GRAPPLING_HOOK && weapon->ammoModel && !( cent->currentState.eFlags & EF_FIRING ) ) {
		memset( &ammo, 0, sizeof( ammo ) );
		VectorCopy( parent->lightingOrigin, ammo.lightingOrigin );
		ammo.shadowPlane = parent->shadowPlane;
		ammo.renderfx = parent->renderfx;
		ammo.hModel = weapon->ammoModel;
		AxisClear( ammo.axis );

		CG_PositionRotatedEntityOnTag( &ammo, &gun, weapon->weaponModel, "tag_ammo" );
		CG_AddWeaponWithPowerups( cent, &ammo );
	}

	// make sure we aren't looking at cg.predictedPlayerEntity for LG
	nonPredictedCent = &cg_entities[cent->currentState.clientNum];

	// if the index of the nonPredictedCent is not the same as the clientNum
	// then this is a fake player (like on teh single player podiums), so
	// go ahead and use the cent
	if( ( nonPredictedCent - cg_entities ) != cent->currentState.clientNum ) {
		nonPredictedCent = cent;
	}

	// add the flash
	if ( continuousFlash && ( nonPredictedCent->currentState.eFlags & EF_FIRING ) ) {
		// continuous flash
	} else {
		// impulse flash
		if ( drawFlash ) {
			if ( cg.time - cent->muzzleFlashTime > MUZZLE_FLASH_TIME && !cent->pe.railgunFlash ) {
				return;
			}
		} else if ( weaponNum != WP_RAILGUN ) {
			return;
		}
	}

	memset( &flash, 0, sizeof( flash ) );
	VectorCopy( parent->lightingOrigin, flash.lightingOrigin );
	flash.shadowPlane = parent->shadowPlane;
	flash.renderfx = drawFlash ? parent->renderfx : 0;

	flash.hModel = weapon->flashModel;
	if (!flash.hModel) {
		return;
	}
	angles[YAW] = 0;
	angles[PITCH] = 0;
	angles[ROLL] = crandom() * 10;
	AnglesToAxis( angles, flash.axis );

	// colorize the railgun blast
	if ( weaponNum == WP_RAILGUN ) {
		clientInfo_t	*ci;
		byte		rgb[3];
		vec3_t		color;

		ci = &cgs.clientinfo[ cent->currentState.clientNum ];
		if ( !CG_ResolveClientWeaponColor( ci, rgb, NULL ) ) {
			CG_CopyBaseWeaponColor( ci, qfalse, color );
			CG_PackWeaponColorBytes( color, 1.0f, rgb );
		}
		flash.shaderRGBA[0] = rgb[0];
		flash.shaderRGBA[1] = rgb[1];
		flash.shaderRGBA[2] = rgb[2];
	}

	CG_PositionRotatedEntityOnTag( &flash, &gun, weapon->weaponModel, "tag_flash");
	if ( drawFlash ) {
		trap_R_AddRefEntityToScene( &flash );
	}

	if ( ps || cg.renderingThirdPerson ||
		cent->currentState.number != cg.predictedPlayerState.clientNum ) {
		// add lightning bolt
		CG_LightningBolt( nonPredictedCent, flash.origin );

		// add rail trail
		CG_SpawnRailTrail( cent, flash.origin );

		if ( weapon->flashDlightColor[0] || weapon->flashDlightColor[1] || weapon->flashDlightColor[2] ) {
			trap_R_AddLightToScene( flash.origin, 300 + (rand()&31), weapon->flashDlightColor[0],
				weapon->flashDlightColor[1], weapon->flashDlightColor[2] );
		}
	}
}

/*
==============
CG_AddViewWeapon

Add the weapon, and flash for the player's view
==============
*/
void CG_AddViewWeapon( playerState_t *ps ) {
	refEntity_t	hand;
	centity_t	*cent;
	clientInfo_t	*ci;
	float		fovOffset;
	vec3_t		angles;
	weaponInfo_t	*weapon;

	if ( ps->persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
		return;
	}

	if ( ps->pm_type == PM_INTERMISSION ) {
		return;
	}

	// no gun if in third person view or a camera is active
	//if ( cg.renderingThirdPerson || cg.cameraMode) {
	if ( cg.renderingThirdPerson ) {
		return;
	}


	// allow the gun to be completely removed
	if ( !cg_drawGun.integer ) {
		vec3_t		origin;

		if ( cg.predictedPlayerState.eFlags & EF_FIRING ) {
			// special hack for lightning gun...
			VectorCopy( cg.refdef.vieworg, origin );
			VectorMA( origin, -8, cg.refdef.viewaxis[2], origin );
			CG_LightningBolt( &cg_entities[ps->clientNum], origin );
		}
		return;
	}

	// don't draw if testing a gun model
	if ( cg.testGun ) {
		return;
	}

	fovOffset = CG_GetViewWeaponFovOffset();

	cent = &cg.predictedPlayerEntity;	// &cg_entities[cg.snap->ps.clientNum];
	CG_RegisterWeapon( ps->weapon );
	weapon = &cg_weapons[ ps->weapon ];

	memset (&hand, 0, sizeof(hand));

	// set up gun position
	CG_CalculateWeaponPosition( hand.origin, angles );

	VectorMA( hand.origin, cg_gun_x.value, cg.refdef.viewaxis[0], hand.origin );
	VectorMA( hand.origin, cg_gun_y.value, cg.refdef.viewaxis[1], hand.origin );
	VectorMA( hand.origin, (cg_gun_z.value+fovOffset), cg.refdef.viewaxis[2], hand.origin );

	AnglesToAxis( angles, hand.axis );

	// map torso animations to weapon animations
	if ( cg_gun_frame.integer ) {
		// development tool
		hand.frame = hand.oldframe = cg_gun_frame.integer;
		hand.backlerp = 0;
	} else {
		// get clientinfo for animation map
		ci = &cgs.clientinfo[ cent->currentState.clientNum ];
		hand.frame = CG_MapTorsoToWeaponFrame( ci, cent->pe.torso.frame );
		hand.oldframe = CG_MapTorsoToWeaponFrame( ci, cent->pe.torso.oldFrame );
		hand.backlerp = cent->pe.torso.backlerp;
	}

	hand.hModel = weapon->handsModel;
	hand.renderfx = RF_DEPTHHACK | RF_FIRST_PERSON | RF_MINLIGHT;

	// add everything onto the hand
	CG_AddPlayerWeapon( &hand, ps, &cg.predictedPlayerEntity, ps->persistant[PERS_TEAM] );
}

/*
==============================================================================

WEAPON SELECTION

==============================================================================
*/

/*
========================
CG_DrawWeaponSelectStrip

Draws the centered retail weapon-strip branch shared by the recovered wrapper.
========================
*/
static void CG_DrawWeaponSelectStrip( void ) {
	int		i;
	int		bits;
	int		count;
	int		x, y, w;
	char	*name;
	float	*color;

	// don't display if dead
	if ( cg.predictedPlayerState.stats[STAT_HEALTH] <= 0 ) {
		return;
	}

	color = CG_FadeColor( cg.weaponSelectTime, WEAPON_SELECT_TIME );
	if ( !color ) {
		return;
	}
	trap_R_SetColor( color );

	// showing weapon select clears pickup item display, but not the blend blob
	cg.itemPickupTime = 0;

	// count the number of weapons owned
	bits = cg.snap->ps.stats[ STAT_WEAPONS ];
	count = 0;
	for ( i = WP_MACHINEGUN ; i < WP_NUM_WEAPONS ; i++ ) {
		if ( bits & ( 1 << i ) ) {
			count++;
		}
	}

	x = 320 - count * 20;
	y = 380;

	for ( i = WP_MACHINEGUN ; i < WP_NUM_WEAPONS ; i++ ) {
		if ( !( bits & ( 1 << i ) ) ) {
			continue;
		}

		CG_RegisterWeapon( i );

		// draw weapon icon
		CG_DrawPic( x, y, 32, 32, cg_weapons[i].weaponIcon );

		// draw selection marker
		if ( i == cg.weaponSelect ) {
			CG_DrawPic( x-4, y-4, 40, 40, cgs.media.selectShader );
		}

		// no ammo cross on top
		if ( !cg.snap->ps.ammo[ i ] ) {
			CG_DrawPic( x, y, 32, 32, cgs.media.noammoShader );
		}

		x += 40;
	}

	// draw the selected name
	if ( cg_weapons[ cg.weaponSelect ].item ) {
		name = cg_weapons[ cg.weaponSelect ].item->pickup_name;
		if ( name ) {
			w = CG_DrawStrlen( name ) * BIGCHAR_WIDTH;
			x = ( SCREEN_WIDTH - w ) / 2;
			CG_DrawBigStringColor(x, y - 22, name, color);
		}
	}

	trap_R_SetColor( NULL );
}

/*
==========================
CG_ShouldDrawFullWeaponBarEntry

Returns qtrue when the legacy menu-HUD bar should include an unowned weapon
that is already registered for the current map.
==========================
*/
static qboolean CG_ShouldDrawFullWeaponBarEntry( int weapon ) {
	if ( !cg_drawFullWeaponBar.integer ) {
		return qfalse;
	}
	if ( weapon < WP_MACHINEGUN || weapon >= WP_NUM_WEAPONS ) {
		return qfalse;
	}

	return (qboolean)( cg_weapons[weapon].registered && cg_weapons[weapon].weaponIcon != 0 );
}

/*
==========================
CG_ShouldDrawLegacyWeaponBarEntry

Matches the retail entry filter for the left, right, and centered menu-HUD
weapon-bar layouts.
==========================
*/
static qboolean CG_ShouldDrawLegacyWeaponBarEntry( int weapon, int ownedBits ) {
	if ( weapon < WP_MACHINEGUN || weapon >= WP_NUM_WEAPONS ) {
		return qfalse;
	}

	if ( ownedBits & ( 1 << weapon ) ) {
		CG_RegisterWeapon( weapon );
		return (qboolean)( cg_weapons[weapon].weaponIcon != 0 );
	}

	return CG_ShouldDrawFullWeaponBarEntry( weapon );
}

/*
==========================
CG_CountLegacyWeaponBarEntries

Counts the visible entries for the retail left, right, and centered menu-HUD
weapon-bar layouts.
==========================
*/
static int CG_CountLegacyWeaponBarEntries( int ownedBits ) {
	int		count;
	int		weapon;

	count = 0;
	for ( weapon = WP_MACHINEGUN; weapon < WP_NUM_WEAPONS; weapon++ ) {
		if ( CG_ShouldDrawLegacyWeaponBarEntry( weapon, ownedBits ) ) {
			count++;
		}
	}

	return count;
}

/*
==========================
CG_GetLegacyWeaponBarLayout

Builds the retail position and offset constants for the left, right, and
centered menu-HUD weapon-bar styles.
==========================
*/
static void CG_GetLegacyWeaponBarLayout( int count, float *x, float *y, float *stepX, float *stepY, float *ammoX, float *selectX, float *infiniteAmmoX ) {
	switch ( cg_weaponBar.integer ) {
	case 2:
		*x = 623.0f;
		*y = 94.0f;
		*stepX = 0.0f;
		*stepY = 22.0f;
		*ammoX = -3.0f;
		*selectX = -33.0f;
		*infiniteAmmoX = -19.0f;
		break;

	case 3:
		*x = 320.0f - count * 55.0f * 0.5f;
		*y = 413.0f;
		*stepX = 55.0f;
		*stepY = 0.0f;
		*ammoX = 20.0f;
		*selectX = -4.0f;
		*infiniteAmmoX = 12.0f;
		break;

	case 1:
	default:
		*x = 1.0f;
		*y = 94.0f;
		*stepX = 0.0f;
		*stepY = 22.0f;
		*ammoX = 20.0f;
		*selectX = -4.0f;
		*infiniteAmmoX = 18.0f;
		break;
	}
}

/*
==========================
CG_GetLegacyWeaponBarAmmoColor

Applies the retail empty-ammo and subtle low-ammo text tinting used by the
legacy menu-HUD weapon bar.
==========================
*/
static void CG_GetLegacyWeaponBarAmmoColor( int weapon, vec4_t color ) {
	int		ammo;
	int		threshold;

	ammo = cg.snap->ps.ammo[weapon];
	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = 1.0f;

	if ( ammo == 0 && cg_lowAmmoWeaponBarWarning.integer != 0 ) {
		color[0] = 1.0f;
		color[1] = 0.0f;
		color[2] = 0.0f;
		color[3] = 0.8f;
		return;
	}

	if ( ammo <= 0 || cg_lowAmmoWeaponBarWarning.integer < 2 ) {
		return;
	}

	threshold = (int)( BG_GetWeaponMaxAmmo( (weapon_t)weapon ) * cg.lowAmmoWarningPercentile );
	if ( ammo < threshold ) {
		color[0] = 1.0f;
		color[1] = 0.8f;
		color[2] = 0.2f;
		color[3] = 1.0f;
	}
}

/*
==========================
CG_DrawLegacyWeaponBarAmmo

Draws the retail ammo label used by the left, right, and centered menu-HUD
weapon-bar styles.
==========================
*/
static void CG_DrawLegacyWeaponBarAmmo( float x, float y, float ammoX, float infiniteAmmoX, int weapon ) {
	char		buffer[8];
	vec4_t		color;
	float		textX;
	int		ammo;

	ammo = cg.snap->ps.ammo[weapon];
	if ( ammo < 0 ) {
		if ( cgs.media.infiniteAmmoShader ) {
			CG_DrawPic( x + infiniteAmmoX, y, 16.0f, 16.0f, cgs.media.infiniteAmmoShader );
		}
		return;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%d", ammo );
	CG_GetLegacyWeaponBarAmmoColor( weapon, color );

	if ( cg_weaponBar.integer == 2 ) {
		textX = x + ammoX - (float)CG_Text_Width( buffer, 0.24f, 0 );
	} else {
		textX = x + ammoX;
	}

	CG_Text_Paint( textX, y + 13.0f, 0.24f, color, buffer, 0.0f, 0, ITEM_TEXTSTYLE_NORMAL );
}

/*
==========================
CG_DrawLegacyWeaponSelect

Restores the retail left, right, and centered menu-HUD weapon-bar layouts
behind `cg_weaponBar` values 1-3.
==========================
*/
static void CG_DrawLegacyWeaponSelect( void ) {
	int		count;
	int		ownedBits;
	int		weapon;
	float		x;
	float		y;
	float		stepX;
	float		stepY;
	float		ammoX;
	float		selectX;
	float		infiniteAmmoX;

	ownedBits = cg.snap->ps.stats[STAT_WEAPONS];
	count = CG_CountLegacyWeaponBarEntries( ownedBits );
	if ( count <= 0 ) {
		return;
	}

	CG_GetLegacyWeaponBarLayout( count, &x, &y, &stepX, &stepY, &ammoX, &selectX, &infiniteAmmoX );

	for ( weapon = WP_MACHINEGUN; weapon < WP_NUM_WEAPONS; weapon++ ) {
		if ( !CG_ShouldDrawLegacyWeaponBarEntry( weapon, ownedBits ) ) {
			continue;
		}

		CG_DrawPic( x, y, 16.0f, 16.0f, cg_weapons[weapon].weaponIcon );

		if ( weapon == cg.weaponSelect ) {
			qhandle_t	selectionShader;

			selectionShader = cgs.media.weaponBarLitShader;
			if ( selectionShader == 0 ) {
				selectionShader = cgs.media.selectShader;
			}
			CG_DrawPic( x + selectX, y - 2.0f, 52.0f, 20.0f, selectionShader );
		}

		if ( ownedBits & ( 1 << weapon ) ) {
			CG_DrawLegacyWeaponBarAmmo( x, y, ammoX, infiniteAmmoX, weapon );
		}

		x += stepX;
		y += stepY;
	}
}

/*
==========================
CG_DrawMenuHudWeaponSelect

Retail outer wrapper for the menu-HUD weapon-select seam.
==========================
*/
static void CG_DrawMenuHudWeaponSelect( void ) {
	if ( !cg.snap || cg.weaponSelectTime <= 0 || cg_weaponBar.integer == 0 ) {
		return;
	}
	if ( cg.predictedPlayerState.stats[STAT_HEALTH] <= 0 ) {
		return;
	}

	if ( cg_weaponBar.integer == 4 ) {
		CG_DrawWeaponSelectStrip();
		return;
	}

	CG_DrawLegacyWeaponSelect();
}

/*
===================
CG_DrawWeaponSelect
===================
*/
void CG_DrawWeaponSelect( void ) {
	CG_DrawMenuHudWeaponSelect();
}


/*
===============
CG_WeaponSelectable
===============
*/
static qboolean CG_WeaponSelectable( int i ) {
	int	ammo;

	if ( !( cg.snap->ps.stats[ STAT_WEAPONS ] & ( 1 << i ) ) ) {
		return qfalse;
	}

	ammo = cg.snap->ps.ammo[i];
	if ( ammo == -1 ) {
		return qtrue;
	}
	if ( ammo > 0 ) {
		return qtrue;
	}

	return ( cg_switchToEmpty.integer != 0 );
}

/*
========================
CG_CycleWeaponSelection

Retail shared weapon-cycling helper used by the forward and backward command
wrappers.
========================
*/
static void CG_CycleWeaponSelection( qboolean next ) {
	int		i;
	int		selected;

	if ( !cg.snap ) {
		return;
	}
	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return;
	}

	cg.weaponSelectTime = cg.time;
	selected = cg.weaponSelect;

	for ( i = 0 ; i < MAX_WEAPONS ; i++ ) {
		if ( next ) {
			selected++;
			if ( selected == MAX_WEAPONS ) {
				selected = 0;
			}
		} else {
			selected--;
			if ( selected < 0 ) {
				selected = WP_NUM_WEAPONS;
			}
		}

		if ( selected == WP_GAUNTLET || selected == WP_NUM_WEAPONS ) {
			continue;
		}
		if ( CG_WeaponSelectable( selected ) ) {
			CG_SetWeaponSelect( selected );
			return;
		}
	}
}

/*
=====================
CG_SelectHighestWeapon

Retail out-of-ammo fallback that walks the owned weapon set from the highest
slot down and skips the `WP_NUM_WEAPONS` sentinel.
=====================
*/
static void CG_SelectHighestWeapon( void ) {
	int		i;

	cg.weaponSelectTime = cg.time;

	for ( i = MAX_WEAPONS - 1 ; i > 0 ; i-- ) {
		if ( i == WP_NUM_WEAPONS ) {
			continue;
		}
		if ( CG_WeaponSelectable( i ) ) {
			CG_SetWeaponSelect( i );
			return;
		}
	}
}

/*
=============================
CG_SelectHighestWeaponExcluding

Retail drop-weapon fallback that skips the weapon being removed from the local
selection walk.
=============================
*/
void CG_SelectHighestWeaponExcluding( weapon_t excludedWeapon ) {
	int		i;

	if ( !cg.snap ) {
		return;
	}
	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return;
	}

	cg.weaponSelectTime = cg.time;

	for ( i = MAX_WEAPONS - 1 ; i > 0 ; i-- ) {
		if ( i == WP_NUM_WEAPONS || i == excludedWeapon ) {
			continue;
		}
		if ( CG_WeaponSelectable( i ) ) {
			CG_SetWeaponSelect( i );
			return;
		}
	}
}

/*
===============
CG_NextWeapon_f
===============
*/
void CG_NextWeapon_f( void ) {
	CG_CycleWeaponSelection( qtrue );
}

/*
===============
CG_PrevWeapon_f
===============
*/
void CG_PrevWeapon_f( void ) {
	CG_CycleWeaponSelection( qfalse );
}

/*
===============
CG_Weapon_f
===============
*/
void CG_Weapon_f( void ) {
	const char	*arg;
	int		num;
	int		primaryWeapon;

	if ( !cg.snap ) {
		return;
	}
	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return;
	}

	arg = CG_Argv( 1 );
	if ( !Q_stricmp( arg, "toggle" ) ) {
		num = cg_weaponTogglePrevious;
		if ( !CG_WeaponSelectable( num ) && !cg_switchToEmpty.integer ) {
			primaryWeapon = cg_weaponPrimary.integer;
			if ( primaryWeapon > 0 && primaryWeapon < MAX_WEAPONS ) {
				if ( num != primaryWeapon ) {
					num = primaryWeapon;
				} else {
					num = cg_weaponToggleFallback;
				}
			}
		}
	} else {
		num = atoi( arg );
	}

	if ( num < 1 || num > 15 ) {
		return;
	}

	cg.weaponSelectTime = cg.time;

	if ( ! ( cg.snap->ps.stats[STAT_WEAPONS] & ( 1 << num ) ) ) {
		return;		// don't have the weapon
	}

	if ( !CG_WeaponSelectable( num ) ) {
		return;
	}

	CG_SetWeaponSelect( num );
}

/*
===================
CG_OutOfAmmoChange

The current weapon has just run out of ammo
===================
*/
void CG_OutOfAmmoChange( void ) {
	if ( !cg_switchOnEmpty.integer ) {
		return;
	}

	CG_SelectHighestWeapon();
}



/*
===================================================================================================

WEAPON EVENTS

===================================================================================================
*/

/*
================
CG_FireWeapon

Caused by an EV_FIRE_WEAPON event
================
*/
void CG_FireWeapon( centity_t *cent ) {
	entityState_t *ent;
	int				c;
	weaponInfo_t	*weap;

	ent = &cent->currentState;
	if ( ent->weapon == WP_NONE ) {
		return;
	}
	if ( ent->weapon >= WP_NUM_WEAPONS ) {
		CG_Error( "CG_FireWeapon: ent->weapon >= WP_NUM_WEAPONS" );
		return;
	}
	weap = &cg_weapons[ ent->weapon ];

	// mark the entity as muzzle flashing, so when it is added it will
	// append the flash to the weapon model
	cent->muzzleFlashTime = cg.time;

	if ( cg.predictLocalRailshots && cent->currentState.number == cg.predictedPlayerState.clientNum ) {
		qboolean		hitWorld = qfalse;

		if ( ent->weapon == WP_LIGHTNING ) {
			vec3_t		predictedStart;
			vec3_t		predictedEnd;

			if ( CG_BuildPredictedBeam( cent, WP_LIGHTNING, predictedStart, predictedEnd, &hitWorld ) ) {
				cg.predictedLocalLightningValid = qtrue;
				cg.predictedLocalLightningTime = cg.time;
				cg.predictedLocalLightningHit = hitWorld;
				VectorCopy( predictedStart, cg.predictedLocalLightningStart );
				VectorCopy( predictedEnd, cg.predictedLocalLightningEnd );
				CG_LightningBoltBeam( predictedStart, predictedEnd );
			} else {
				cg.predictedLocalLightningValid = qfalse;
			}
		}
	}

	// lightning gun only does this this on initial press
	if ( ent->weapon == WP_LIGHTNING ) {
		if ( cent->pe.lightningFiring ) {
			return;
		}
	}

	// play quad sound if needed
	if ( cent->currentState.powerups & ( 1 << PW_QUAD ) ) {
		trap_S_StartSound (NULL, cent->currentState.number, CHAN_ITEM, cgs.media.quadSound );
	}

	// play a sound
	for ( c = 0 ; c < 4 ; c++ ) {
		if ( !weap->flashSound[c] ) {
			break;
		}
	}
	if ( c > 0 ) {
		c = rand() % c;
		if ( weap->flashSound[c] )
		{
			trap_S_StartSound( NULL, ent->number, CHAN_WEAPON, weap->flashSound[c] );
		}
	}

	// do brass ejection
	if ( weap->ejectBrassFunc && cg_brassTime.integer > 0 ) {
		weap->ejectBrassFunc( cent );
	}
}


/*
=================
CG_MissileHitWall

Caused by an EV_MISSILE_MISS event, or directly by local bullet tracing
=================
*/
void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType ) {
	qhandle_t		mod;
	qhandle_t		mark;
	qhandle_t		shader;
	sfxHandle_t		sfx;
	float			radius;
	float			light;
	vec3_t			lightColor;
	localEntity_t	*le;
	int				r;
	qboolean		alphaFade;
	qboolean		isSprite;
	int				duration;
	vec3_t			sprOrg;
	vec3_t			sprVel;

	mark = 0;
	radius = 32;
	sfx = 0;
	mod = 0;
	shader = 0;
	light = 0;
	lightColor[0] = 1;
	lightColor[1] = 1;
	lightColor[2] = 0;

	// set defaults
	isSprite = qfalse;
	duration = 600;

	switch ( weapon ) {
	default:
	case WP_NAILGUN:
		if( soundType == IMPACTSOUND_FLESH ) {
			sfx = cgs.media.sfx_nghitflesh;
		} else if( soundType == IMPACTSOUND_METAL ) {
			sfx = cgs.media.sfx_nghitmetal;
		} else {
			sfx = cgs.media.sfx_nghit;
		}
		mark = cgs.media.holeMarkShader;
		radius = 12;
		break;
	case WP_LIGHTNING:
		// no explosion at LG impact, it is added with the beam
		r = rand() & 3;
		if ( r < 2 ) {
			sfx = cgs.media.sfx_lghit2;
		} else if ( r == 2 ) {
			sfx = cgs.media.sfx_lghit1;
		} else {
			sfx = cgs.media.sfx_lghit3;
		}
		mark = cgs.media.holeMarkShader;
		radius = 12;
		break;
	case WP_PROX_LAUNCHER:
		mod = cgs.media.dishFlashModel;
		shader = cgs.media.grenadeExplosionShader;
		sfx = cgs.media.sfx_proxexp;
		mark = cgs.media.burnMarkShader;
		radius = 64;
		light = 300;
		isSprite = qtrue;
		break;
	case WP_GRENADE_LAUNCHER:
		mod = cgs.media.dishFlashModel;
		shader = cgs.media.grenadeExplosionShader;
		sfx = cgs.media.sfx_rockexp;
		mark = cgs.media.burnMarkShader;
		radius = 64;
		light = 300;
		isSprite = qtrue;
		break;
	case WP_ROCKET_LAUNCHER:
		mod = cgs.media.dishFlashModel;
		shader = cgs.media.rocketExplosionShader;
		sfx = cgs.media.sfx_rockexp;
		mark = cgs.media.burnMarkShader;
		radius = 64;
		light = 300;
		isSprite = qtrue;
		duration = 1000;
		lightColor[0] = 1;
		lightColor[1] = 0.75;
		lightColor[2] = 0.0;
		if (cg_oldRocket.integer == 0) {
			// explosion sprite animation
			VectorMA( origin, 24, dir, sprOrg );
			VectorScale( dir, 64, sprVel );

			CG_ParticleExplosion( "explode1", sprOrg, sprVel, 1400, 20, 30 );
		}
		break;
	case WP_RAILGUN:
		mod = cgs.media.ringFlashModel;
		shader = cgs.media.railExplosionShader;
		sfx = cgs.media.sfx_plasmaexp;
		mark = cgs.media.energyMarkShader;
		radius = 24;
		break;
	case WP_PLASMAGUN:
		mod = cgs.media.ringFlashModel;
		shader = cgs.media.plasmaExplosionShader;
		sfx = cgs.media.sfx_plasmaexp;
		mark = cgs.media.energyMarkShader;
		radius = 16;
		break;
	case WP_BFG:
		mod = cgs.media.dishFlashModel;
		shader = cgs.media.bfgExplosionShader;
		sfx = cgs.media.sfx_rockexp;
		mark = cgs.media.burnMarkShader;
		radius = 32;
		isSprite = qtrue;
		break;
	case WP_HEAVY_MACHINEGUN:
		mod = cgs.media.bulletFlashModel;
		shader = cgs.media.bulletExplosionShader;
		mark = cgs.media.bulletMarkShader;
		radius = 4;
		break;
	case WP_SHOTGUN:
		mod = cgs.media.bulletFlashModel;
		shader = cgs.media.bulletExplosionShader;
		mark = cgs.media.bulletMarkShader;
		sfx = 0;
		radius = 4;
		break;

	case WP_CHAINGUN:
		mod = cgs.media.bulletFlashModel;
		if( soundType == IMPACTSOUND_FLESH ) {
			sfx = cgs.media.sfx_chghitflesh;
		} else if( soundType == IMPACTSOUND_METAL ) {
			sfx = cgs.media.sfx_chghitmetal;
		} else {
			sfx = cgs.media.sfx_chghit;
		}
		mark = cgs.media.bulletMarkShader;

		r = rand() & 3;
		if ( r < 2 ) {
			sfx = cgs.media.sfx_ric1;
		} else if ( r == 2 ) {
			sfx = cgs.media.sfx_ric2;
		} else {
			sfx = cgs.media.sfx_ric3;
		}

		radius = 8;
		break;

	case WP_MACHINEGUN:
		mod = cgs.media.bulletFlashModel;
		shader = cgs.media.bulletExplosionShader;
		mark = cgs.media.bulletMarkShader;

		r = rand() & 3;
		if ( r == 0 ) {
			sfx = cgs.media.sfx_ric1;
		} else if ( r == 1 ) {
			sfx = cgs.media.sfx_ric2;
		} else {
			sfx = cgs.media.sfx_ric3;
		}

		radius = 8;
		break;
	}

	if ( sfx ) {
		trap_S_StartSound( origin, ENTITYNUM_WORLD, CHAN_AUTO, sfx );
	}

	//
	// create the explosion
	//
	if ( mod ) {
		le = CG_MakeExplosion( origin, dir, 
							   mod,	shader,
							   duration, isSprite );
		le->light = light;
		VectorCopy( lightColor, le->lightColor );
		if ( weapon == WP_RAILGUN && clientNum >= 0 && clientNum < MAX_CLIENTS ) {
			// colorize with client color
			VectorCopy( cgs.clientinfo[clientNum].color1, le->color );
		}
	}

	//
	// impact mark
	//
	alphaFade = (mark == cgs.media.energyMarkShader);	// plasma fades alpha, all others fade color
	if ( weapon == WP_RAILGUN ) {
		clientInfo_t	*ci;
		vec3_t		color;

		ci = NULL;
		if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
			ci = &cgs.clientinfo[clientNum];
		}
		if ( !CG_ResolveClientWeaponColor( ci, NULL, color ) ) {
			CG_CopyBaseWeaponColor( ci, qfalse, color );
		}
		CG_ImpactMark( mark, origin, dir, random()*360, color[0],color[1], color[2],1, alphaFade, radius, qfalse );
	} else {
		CG_ImpactMark( mark, origin, dir, random()*360, 1,1,1,1, alphaFade, radius, qfalse );
	}
}


/*
=================
CG_MissileHitPlayer
=================
*/
void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum ) {
	CG_Bleed( origin, entityNum );

	// some weapons will make an explosion with the blood, while
	// others will just make the blood
	switch ( weapon ) {
	case WP_GRENADE_LAUNCHER:
	case WP_ROCKET_LAUNCHER:
	case WP_NAILGUN:
	case WP_CHAINGUN:
	case WP_PROX_LAUNCHER:
		CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );
		break;
	default:
		break;
	}
}

/*
=========================
CG_MissileHitWallDmgThrough

Retail damage-through impacts probe slightly beyond the original hit, project a
second burn mark on the backside face, and throw ten `surfacePuff` debris
sprites before falling through to the normal wall-impact path.
=========================
*/
void CG_MissileHitWallDmgThrough( vec3_t origin, vec3_t dir, int weapon ) {
	trace_t		trace;
	vec3_t		probeOrigin;
	vec3_t		puffOrigin;
	vec3_t		velocity;
	float		probeDistance;
	float		speed;
	int		i;

	probeDistance = CG_GetDamageThroughProbeDistance();
	VectorMA( origin, probeDistance, dir, probeOrigin );
	CG_Trace( &trace, probeOrigin, NULL, NULL, origin, ENTITYNUM_NONE, CONTENTS_SOLID );

	if ( trace.fraction < 1.0f && !trace.startsolid ) {
		if ( cg_addMarks.integer && cgs.media.burnMarkShader ) {
			CG_ImpactMark( cgs.media.burnMarkShader, trace.endpos, trace.plane.normal,
				random() * 360.0f, 1.0f, 1.0f, 1.0f, 1.0f, qfalse, 64.0f, qfalse );
		}

		if ( cgs.media.surfacePuffShader ) {
			VectorAdd( trace.endpos, trace.plane.normal, puffOrigin );

			for ( i = 0; i < 10; i++ ) {
				speed = 250.0f + ( ( random() - 0.5f ) * 300.0f );
				VectorScale( trace.plane.normal, speed, velocity );
				velocity[0] += 50.0f - ( ( random() - 0.5f ) * 100.0f );
				velocity[1] += 50.0f - ( ( random() - 0.5f ) * 100.0f );
				velocity[2] += 50.0f - ( ( random() - 0.5f ) * 100.0f );

				CG_SmokePuff( puffOrigin, velocity,
					24.0f,
					0.8f, 0.8f, 0.7f, 1.0f,
					400.0f - ( speed / 500.0f ) * 200.0f,
					cg.time,
					0,
					0,
					cgs.media.surfacePuffShader );
			}
		}
	}

	CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_DEFAULT );
}



/*
============================================================================

SHOTGUN TRACING

============================================================================
*/

/*
================
CG_ShotgunPellet
================
*/
static void CG_ShotgunPellet( vec3_t start, vec3_t end, int skipNum ) {
	trace_t		tr;
	int sourceContentType, destContentType;

	CG_Trace( &tr, start, NULL, NULL, end, skipNum, MASK_SHOT );

	sourceContentType = trap_CM_PointContents( start, 0 );
	destContentType = trap_CM_PointContents( tr.endpos, 0 );

	// FIXME: should probably move this cruft into CG_BubbleTrail
	if ( sourceContentType == destContentType ) {
		if ( sourceContentType & CONTENTS_WATER ) {
			CG_BubbleTrail( start, tr.endpos, 32 );
		}
	} else if ( sourceContentType & CONTENTS_WATER ) {
		trace_t trace;

		trap_CM_BoxTrace( &trace, end, start, NULL, NULL, 0, CONTENTS_WATER );
		CG_BubbleTrail( start, trace.endpos, 32 );
	} else if ( destContentType & CONTENTS_WATER ) {
		trace_t trace;

		trap_CM_BoxTrace( &trace, start, end, NULL, NULL, 0, CONTENTS_WATER );
		CG_BubbleTrail( tr.endpos, trace.endpos, 32 );
	}

	if (  tr.surfaceFlags & SURF_NOIMPACT ) {
		return;
	}

	if ( cg_entities[tr.entityNum].currentState.eType == ET_PLAYER ) {
		CG_MissileHitPlayer( WP_SHOTGUN, tr.endpos, tr.plane.normal, tr.entityNum );
	} else {
		if ( tr.surfaceFlags & SURF_NOIMPACT ) {
			// SURF_NOIMPACT will not make a flame puff or a mark
			return;
		}
		if ( tr.surfaceFlags & SURF_METALSTEPS ) {
			CG_MissileHitWall( WP_SHOTGUN, 0, tr.endpos, tr.plane.normal, IMPACTSOUND_METAL );
		} else {
			CG_MissileHitWall( WP_SHOTGUN, 0, tr.endpos, tr.plane.normal, IMPACTSOUND_DEFAULT );
		}
	}
}

/*
================
CG_ShotgunPattern

Perform the same traces the server did to locate the
hit splashes
================
*/
static void CG_ShotgunPattern( vec3_t origin, vec3_t origin2, int seed, int otherEntNum ) {
	int			i;
	float		r, u;
	vec3_t		end;
	vec3_t		forward, right, up;

	// derive the right and up vectors from the forward vector, because
	// the client won't have any other information
	VectorNormalize2( origin2, forward );
	PerpendicularVector( right, forward );
	CrossProduct( forward, right, up );

	// generate the "random" spread pattern
	for ( i = 0 ; i < DEFAULT_SHOTGUN_COUNT ; i++ ) {
		if ( cg_trueShotgun.integer ) {
			if ( i < 6 ) {
				float angle = i * 60.0f;
				r = 4000.0f * cos( DEG2RAD( angle ) );
				u = 4000.0f * sin( DEG2RAD( angle ) );
			} else if ( i < 12 ) {
				float angle = ( i - 6 ) * 60.0f + 30.0f;
				r = 8000.0f * cos( DEG2RAD( angle ) );
				u = 8000.0f * sin( DEG2RAD( angle ) );
			} else {
				float angle = ( i - 12 ) * 45.0f;
				r = 12000.0f * cos( DEG2RAD( angle ) );
				u = 12000.0f * sin( DEG2RAD( angle ) );
			}
		} else {
			r = Q_crandom( &seed ) * DEFAULT_SHOTGUN_SPREAD * 16;
			u = Q_crandom( &seed ) * DEFAULT_SHOTGUN_SPREAD * 16;
		}

		VectorMA( origin, 8192 * 16, forward, end);
		VectorMA (end, r, right, end);
		VectorMA (end, u, up, end);

		CG_ShotgunPellet( origin, end, otherEntNum );
	}
}

/*
==============
CG_ShotgunFire
==============
*/
void CG_ShotgunFire( entityState_t *es ) {
	vec3_t	v;
	int		contents;

	VectorSubtract( es->origin2, es->pos.trBase, v );
	VectorNormalize( v );
	VectorScale( v, 32, v );
	VectorAdd( es->pos.trBase, v, v );
	if ( cgs.glconfig.hardwareType != GLHW_RAGEPRO ) {
		// ragepro can't alpha fade, so don't even bother with smoke
		vec3_t			up;

		contents = trap_CM_PointContents( es->pos.trBase, 0 );
		if ( !( contents & CONTENTS_WATER ) ) {
			VectorSet( up, 0, 0, 8 );
			CG_SmokePuff( v, up, 32, 1, 1, 1, 0.33f, 900, cg.time, 0, LEF_PUFF_DONT_SCALE, cgs.media.shotgunSmokePuffShader );
		}
	}
	CG_ShotgunPattern( es->pos.trBase, es->origin2, es->eventParm, es->otherEntityNum );
}

/*
===================
CG_ShotgunKillEffect

Reconstructs the retail shotgun finisher gore burst around the victim origin.
===================
*/
void CG_ShotgunKillEffect( centity_t *cent, const entityState_t *es ) {
	localEntity_t	*blood;
	qhandle_t		bloodShader;
	vec3_t			puffOrigin;
	int			entityNum;
	int			burstCount;
	int			i;

	if ( !cent ) {
		return;
	}
	if ( !cg_blood.integer || !cgs.media.bloodSprayShaders[0] ) {
		return;
	}

	entityNum = ENTITYNUM_NONE;
	if ( es && es->otherEntityNum >= 0 && es->otherEntityNum < MAX_GENTITIES ) {
		entityNum = es->otherEntityNum;
	}

	burstCount = 10;
	if ( es ) {
		if ( es->time > 0 ) {
			burstCount = es->time;
		} else if ( es->eventParm > 0 ) {
			burstCount = es->eventParm;
		}
	}

	burstCount /= 5;
	if ( burstCount < 1 ) {
		burstCount = 1;
	} else if ( burstCount > 8 ) {
		burstCount = 8;
	}

	for ( i = 0; i < burstCount; i++ ) {
		VectorCopy( cent->lerpOrigin, puffOrigin );
		puffOrigin[0] += crandom() * 16.0f;
		puffOrigin[1] += crandom() * 16.0f;
		puffOrigin[2] += 8.0f + random() * 24.0f;
		CG_Bleed( puffOrigin, entityNum );

		puffOrigin[0] += crandom() * 6.0f;
		puffOrigin[1] += crandom() * 6.0f;
		puffOrigin[2] += crandom() * 6.0f;
		CG_Bleed( puffOrigin, entityNum );

		bloodShader = cgs.media.bloodSprayShaders[rand() & 3];
		blood = CG_SmokePuff( puffOrigin, vec3_origin,
			24.0f,
			1.0f, 1.0f, 1.0f, 1.0f,
			400,
			cg.time,
			0,
			0,
			bloodShader );
		blood->leType = LE_FALL_SCALE_FADE;
		blood->pos.trDelta[2] = 20.0f;
		if ( cg.snap && entityNum == cg.snap->ps.clientNum ) {
			blood->refEntity.renderfx |= RF_THIRD_PERSON;
		}
	}
}

/*
============================================================================

BULLETS

============================================================================
*/


/*
===============
CG_Tracer
===============
*/
void CG_Tracer( vec3_t source, vec3_t dest ) {
	vec3_t		forward, right;
	polyVert_t	verts[4];
	vec3_t		line;
	float		len, begin, end;
	vec3_t		start, finish;
	vec3_t		midpoint;

	// tracer
	VectorSubtract( dest, source, forward );
	len = VectorNormalize( forward );

	// start at least a little ways from the muzzle
	if ( len < 100 ) {
		return;
	}
	begin = 50 + random() * (len - 60);
	end = begin + cg_tracerLength.value;
	if ( end > len ) {
		end = len;
	}
	VectorMA( source, begin, forward, start );
	VectorMA( source, end, forward, finish );

	line[0] = DotProduct( forward, cg.refdef.viewaxis[1] );
	line[1] = DotProduct( forward, cg.refdef.viewaxis[2] );

	VectorScale( cg.refdef.viewaxis[1], line[1], right );
	VectorMA( right, -line[0], cg.refdef.viewaxis[2], right );
	VectorNormalize( right );

	VectorMA( finish, cg_tracerWidth.value, right, verts[0].xyz );
	verts[0].st[0] = 0;
	verts[0].st[1] = 1;
	verts[0].modulate[0] = 255;
	verts[0].modulate[1] = 255;
	verts[0].modulate[2] = 255;
	verts[0].modulate[3] = 255;

	VectorMA( finish, -cg_tracerWidth.value, right, verts[1].xyz );
	verts[1].st[0] = 1;
	verts[1].st[1] = 0;
	verts[1].modulate[0] = 255;
	verts[1].modulate[1] = 255;
	verts[1].modulate[2] = 255;
	verts[1].modulate[3] = 255;

	VectorMA( start, -cg_tracerWidth.value, right, verts[2].xyz );
	verts[2].st[0] = 1;
	verts[2].st[1] = 1;
	verts[2].modulate[0] = 255;
	verts[2].modulate[1] = 255;
	verts[2].modulate[2] = 255;
	verts[2].modulate[3] = 255;

	VectorMA( start, cg_tracerWidth.value, right, verts[3].xyz );
	verts[3].st[0] = 0;
	verts[3].st[1] = 0;
	verts[3].modulate[0] = 255;
	verts[3].modulate[1] = 255;
	verts[3].modulate[2] = 255;
	verts[3].modulate[3] = 255;

	trap_R_AddPolyToScene( cgs.media.tracerShader, 4, verts );

	midpoint[0] = ( start[0] + finish[0] ) * 0.5;
	midpoint[1] = ( start[1] + finish[1] ) * 0.5;
	midpoint[2] = ( start[2] + finish[2] ) * 0.5;

	// add the tracer sound
	trap_S_StartSound( midpoint, ENTITYNUM_WORLD, CHAN_AUTO, cgs.media.tracerSound );

}


/*
======================
CG_CalcMuzzlePoint
======================
*/
static qboolean	CG_CalcMuzzlePoint( int entityNum, vec3_t muzzle ) {
	vec3_t		forward;
	centity_t	*cent;
	int			anim;

	if ( entityNum == cg.snap->ps.clientNum ) {
		VectorCopy( cg.snap->ps.origin, muzzle );
		muzzle[2] += cg.snap->ps.viewheight;
		AngleVectors( cg.snap->ps.viewangles, forward, NULL, NULL );
		VectorMA( muzzle, 14, forward, muzzle );
		return qtrue;
	}

	cent = &cg_entities[entityNum];
	if ( !cent->currentValid ) {
		return qfalse;
	}

	VectorCopy( cent->currentState.pos.trBase, muzzle );

	AngleVectors( cent->currentState.apos.trBase, forward, NULL, NULL );
	anim = cent->currentState.legsAnim & ~ANIM_TOGGLEBIT;
	if ( anim == LEGS_WALKCR || anim == LEGS_IDLECR ) {
		muzzle[2] += CROUCH_VIEWHEIGHT;
	} else {
		muzzle[2] += DEFAULT_VIEWHEIGHT;
	}

	VectorMA( muzzle, 14, forward, muzzle );

	return qtrue;

}

/*
======================
CG_Bullet

Renders bullet effects.
======================
*/
void CG_Bullet( vec3_t end, int sourceEntityNum, vec3_t normal, qboolean flesh, int fleshEntityNum ) {
	trace_t trace;
	int sourceContentType, destContentType;
	vec3_t		start;

	// if the shooter is currently valid, calc a source point and possibly
	// do trail effects
	if ( sourceEntityNum >= 0 && cg_tracerChance.value > 0 ) {
		if ( CG_CalcMuzzlePoint( sourceEntityNum, start ) ) {
			sourceContentType = trap_CM_PointContents( start, 0 );
			destContentType = trap_CM_PointContents( end, 0 );

			// do a complete bubble trail if necessary
			if ( ( sourceContentType == destContentType ) && ( sourceContentType & CONTENTS_WATER ) ) {
				CG_BubbleTrail( start, end, 32 );
			}
			// bubble trail from water into air
			else if ( ( sourceContentType & CONTENTS_WATER ) ) {
				trap_CM_BoxTrace( &trace, end, start, NULL, NULL, 0, CONTENTS_WATER );
				CG_BubbleTrail( start, trace.endpos, 32 );
			}
			// bubble trail from air into water
			else if ( ( destContentType & CONTENTS_WATER ) ) {
				trap_CM_BoxTrace( &trace, start, end, NULL, NULL, 0, CONTENTS_WATER );
				CG_BubbleTrail( trace.endpos, end, 32 );
			}

			// draw a tracer
			if ( random() < cg_tracerChance.value ) {
				CG_Tracer( start, end );
			}
		}
	}

	// impact splash and mark
	if ( flesh ) {
		CG_Bleed( end, fleshEntityNum );
	} else {
		CG_MissileHitWall( WP_MACHINEGUN, 0, end, normal, IMPACTSOUND_DEFAULT );
	}

}
