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
// cg_screen.c -- handle screen feedback events

#include "cg_local.h"

/*
================
CG_DamageBlendBlob

First person view damage feedback (red blob)
================
*/
void CG_DamageBlendBlob( void ) {
	int			t;
	int			maxTime;
	refEntity_t		ent;

	if ( !cg.damageValue ) {
		return;
	}

	// rage pro systems can't fade blends, so don't obscure the screen
	if ( cgs.glconfig.hardwareType == GLHW_RAGEPRO ) {
		return;
	}

	maxTime = DAMAGE_TIME;
	t = cg.time - cg.damageTime;
	if ( t <= 0 || t >= maxTime ) {
		return;
	}

	memset( &ent, 0, sizeof( ent ) );
	ent.reType = RT_SPRITE;
	ent.renderfx = RF_FIRST_PERSON;

	VectorMA( cg.refdef.vieworg, 8, cg.refdef.viewaxis[0], ent.origin );
	VectorMA( ent.origin, cg.damageX * -8, cg.refdef.viewaxis[1], ent.origin );
	VectorMA( ent.origin, cg.damageY * 8, cg.refdef.viewaxis[2], ent.origin );

	ent.radius = cg.damageValue * 0.4 * ( 1.0 - (float)t / maxTime );

	if ( cg.snap->ps.stats[STAT_HEALTH] <= 30 ) {
		ent.customShader = cgs.media.bloodExplosionShader;
	} else {
		ent.customShader = cgs.media.viewBloodShader;
	}
	trap_R_AddRefEntityToScene( &ent );
}

/*
================
CG_DrawScreenDamage

2D screen damage feedback
================
*/
void CG_DrawScreenDamage( void ) {
	vec4_t		color;
	float		alpha;
	int			t;

	if ( !cg.damageValue ) {
		return;
	}

	// rage pro systems can't fade blends, so don't obscure the screen
	if ( cgs.glconfig.hardwareType == GLHW_RAGEPRO ) {
		return;
	}

	t = cg.time - cg.damageTime;
	if ( t <= 0 || t >= DAMAGE_TIME ) {
		return;
	}

	alpha = cg.screenDamageAlpha * ( 1.0 - (float)t / DAMAGE_TIME );
	if ( alpha <= 0 ) {
		return;
	}

	// Use the configured color
	VectorCopy( cg.screenDamageColor, color );
	color[3] = alpha / 255.0f;

	trap_R_SetColor( color );
	CG_DrawPic( 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, cgs.media.whiteShader );
	trap_R_SetColor( NULL );
}
