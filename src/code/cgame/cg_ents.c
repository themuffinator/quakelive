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
// cg_ents.c -- present snapshot entities, happens every single frame

#include "cg_local.h"


/*
======================
CG_PositionEntityOnTag

Modifies the entities position and axis by the given
tag location
======================
*/
void CG_PositionEntityOnTag( refEntity_t *entity, const refEntity_t *parent, 
							qhandle_t parentModel, char *tagName ) {
	int				i;
	orientation_t	lerped;
	
	// lerp the tag
	trap_R_LerpTag( &lerped, parentModel, parent->oldframe, parent->frame,
		1.0 - parent->backlerp, tagName );

	// FIXME: allow origin offsets along tag?
	VectorCopy( parent->origin, entity->origin );
	for ( i = 0 ; i < 3 ; i++ ) {
		VectorMA( entity->origin, lerped.origin[i], parent->axis[i], entity->origin );
	}

	// had to cast away the const to avoid compiler problems...
	MatrixMultiply( lerped.axis, ((refEntity_t *)parent)->axis, entity->axis );
	entity->backlerp = parent->backlerp;
}


/*
======================
CG_PositionRotatedEntityOnTag

Modifies the entities position and axis by the given
tag location
======================
*/
void CG_PositionRotatedEntityOnTag( refEntity_t *entity, const refEntity_t *parent, 
							qhandle_t parentModel, char *tagName ) {
	int				i;
	orientation_t	lerped;
	vec3_t			tempAxis[3];

//AxisClear( entity->axis );
	// lerp the tag
	trap_R_LerpTag( &lerped, parentModel, parent->oldframe, parent->frame,
		1.0 - parent->backlerp, tagName );

	// FIXME: allow origin offsets along tag?
	VectorCopy( parent->origin, entity->origin );
	for ( i = 0 ; i < 3 ; i++ ) {
		VectorMA( entity->origin, lerped.origin[i], parent->axis[i], entity->origin );
	}

	// had to cast away the const to avoid compiler problems...
	MatrixMultiply( entity->axis, lerped.axis, tempAxis );
	MatrixMultiply( tempAxis, ((refEntity_t *)parent)->axis, entity->axis );
}



/*
==========================================================================

FUNCTIONS CALLED EACH FRAME

==========================================================================
*/

/*
======================
CG_SetEntitySoundPosition

Also called by event processing code
======================
*/
void CG_SetEntitySoundPosition( centity_t *cent ) {
	if ( cent->currentState.solid == SOLID_BMODEL ) {
		vec3_t	origin;
		float	*v;

		v = cgs.inlineModelMidpoints[ cent->currentState.modelindex ];
		VectorAdd( cent->lerpOrigin, v, origin );
		trap_S_UpdateEntityPosition( cent->currentState.number, origin );
	} else {
		trap_S_UpdateEntityPosition( cent->currentState.number, cent->lerpOrigin );
	}
}

/*
==================
CG_EntityEffects

Add continuous entity effects, like local entity emission and lighting
==================
*/
static void CG_EntityEffects( centity_t *cent ) {

	// update sound origins
	CG_SetEntitySoundPosition( cent );

	// add loop sound
	if ( cent->currentState.loopSound ) {
		if (cent->currentState.eType != ET_SPEAKER) {
			trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, 
				cgs.gameSounds[ cent->currentState.loopSound ] );
		} else {
			trap_S_AddRealLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, 
				cgs.gameSounds[ cent->currentState.loopSound ] );
		}
	}


	// constant light glow
	if ( cent->currentState.constantLight ) {
		int		cl;
		int		i, r, g, b;

		cl = cent->currentState.constantLight;
		r = cl & 255;
		g = ( cl >> 8 ) & 255;
		b = ( cl >> 16 ) & 255;
		i = ( ( cl >> 24 ) & 255 ) * 4;
		trap_R_AddLightToScene( cent->lerpOrigin, i, r, g, b );
	}

}


/*
==================
CG_General
==================
*/
static void CG_General( centity_t *cent ) {
	refEntity_t			ent;
	entityState_t		*s1;

	s1 = &cent->currentState;

	// if set to invisible, skip
	if (!s1->modelindex) {
		return;
	}

	memset (&ent, 0, sizeof(ent));

	// set frame

	ent.frame = s1->frame;
	ent.oldframe = ent.frame;
	ent.backlerp = 0;

	VectorCopy( cent->lerpOrigin, ent.origin);
	VectorCopy( cent->lerpOrigin, ent.oldorigin);

	ent.hModel = cgs.gameModels[s1->modelindex];

	// player model
	if (s1->number == cg.snap->ps.clientNum) {
		ent.renderfx |= RF_THIRD_PERSON;	// only draw from mirrors
	}

	// convert angles to axis
	AnglesToAxis( cent->lerpAngles, ent.axis );

	// add to refresh list
	trap_R_AddRefEntityToScene (&ent);
}

/*
==================
CG_Speaker

Speaker entities can automatically play sounds
==================
*/
static void CG_Speaker( centity_t *cent ) {
	if ( ! cent->currentState.clientNum ) {	// FIXME: use something other than clientNum...
		return;		// not auto triggering
	}

	if ( cg.time < cent->miscTime ) {
		return;
	}

	trap_S_StartSound (NULL, cent->currentState.number, CHAN_ITEM, cgs.gameSounds[cent->currentState.eventParm] );

	//	ent->s.frame = ent->wait * 10;
	//	ent->s.clientNum = ent->random * 10;
	cent->miscTime = cg.time + cent->currentState.frame * 100 + cent->currentState.clientNum * 100 * crandom();
}

/*
=====================
CG_POILocalTeam

Returns the local team used by the retail POI objective/item icon splits.
=====================
*/
static team_t CG_POILocalTeam( void ) {
	if ( !cg.snap ) {
		return TEAM_FREE;
	}

	switch ( cg.snap->ps.persistant[PERS_TEAM] ) {
	case TEAM_RED:
		return TEAM_RED;
	case TEAM_BLUE:
		return TEAM_BLUE;
	default:
		break;
	}

	return TEAM_FREE;
}

/*
=========================
CG_POIObjectiveIndexForItem

Maps retail team-objective items onto the cached POI origin slots.
=========================
*/
static int CG_POIObjectiveIndexForItem( const gitem_t *item ) {
	if ( !item || item->giType != IT_TEAM ) {
		return -1;
	}

	switch ( item->giTag ) {
	case PW_REDFLAG:
		return CG_POI_OBJECTIVE_RED;
	case PW_BLUEFLAG:
		return CG_POI_OBJECTIVE_BLUE;
	case PW_NEUTRALFLAG:
		return CG_POI_OBJECTIVE_NEUTRAL;
	default:
		break;
	}

	return -1;
}

/*
========================
CG_UpdatePOIObjectiveCache

Persists the latest retail team-objective origin for player and item POI helpers.
========================
*/
static void CG_UpdatePOIObjectiveCache( const gitem_t *item, const vec3_t origin ) {
	int	objectiveIndex;

	objectiveIndex = CG_POIObjectiveIndexForItem( item );
	if ( objectiveIndex < 0 || objectiveIndex >= CG_POI_OBJECTIVE_COUNT ) {
		return;
	}

	VectorCopy( origin, cgs.poiObjectiveOrigins[objectiveIndex] );
	cgs.poiObjectiveValid[objectiveIndex] = qtrue;
}

/*
============================
CG_ItemPOIPowerupLiveShader

Resolves the retail live powerup POI sprite for a world item.
============================
*/
static qhandle_t CG_ItemPOIPowerupLiveShader( const gitem_t *item ) {
	if ( !item ) {
		return 0;
	}

	switch ( item->giTag ) {
	case PW_QUAD:
		return cgs.media.poiPowerupQuadShader;
	case PW_BATTLESUIT:
		return cgs.media.poiPowerupBattleSuitShader;
	case PW_HASTE:
		return cgs.media.poiPowerupHasteShader;
	case PW_INVIS:
		return cgs.media.poiPowerupInvisShader;
	case PW_REGEN:
		return cgs.media.poiPowerupRegenShader;
	default:
		break;
	}

	return 0;
}

/*
========================
CG_ItemPOIIsQuadHogWorldQuad

Returns qtrue for the retail Quad Hog dropped-world-quad seam that bypasses
the generic dropped-powerup POI rejection.
========================
*/
static qboolean CG_ItemPOIIsQuadHogWorldQuad( const centity_t *cent, const gitem_t *item ) {
	if ( !cent || !item ) {
		return qfalse;
	}

	if ( !cg_pmoveSettings.quadHogEnabled || cgs.gametype != GT_FFA ) {
		return qfalse;
	}

	if ( item->giType != IT_POWERUP || item->giTag != PW_QUAD ) {
		return qfalse;
	}

	return (qboolean)( cent->currentState.modelindex2 != 0 );
}

/*
========================
CG_ItemPOIPowerupMarker

Builds the retail powerup POI state, including incoming icons and distance alpha.
========================
*/
static qboolean CG_ItemPOIPowerupMarker( const centity_t *cent, const gitem_t *item, const vec3_t origin,
		qhandle_t *shader, float *alpha ) {
	int			markerTime;
	float		nearDistance;
	float		farDistance;
	float		distance;
	vec3_t		distanceOrigin;
	qboolean	quadHogWorldQuad;
	qboolean	incoming;

	if ( !shader || !alpha ) {
		return qfalse;
	}

	*shader = 0;
	*alpha = 1.0f;
	if ( !cent || !item ) {
		return qfalse;
	}

	quadHogWorldQuad = CG_ItemPOIIsQuadHogWorldQuad( cent, item );
	if ( quadHogWorldQuad ) {
		*shader = cgs.media.poiPowerupQuadShader;
	} else {
		*shader = CG_ItemPOIPowerupLiveShader( item );
	}
	if ( !*shader ) {
		return qfalse;
	}

	markerTime = cent->currentState.time;
	if ( !quadHogWorldQuad && cent->currentState.modelindex2 && markerTime < cg.time ) {
		return qfalse;
	}
	if ( !quadHogWorldQuad && cg.time < markerTime - 10000 ) {
		return qfalse;
	}

	incoming = (qboolean)( !quadHogWorldQuad && cg.time <= markerTime );
	if ( ( cent->currentState.eFlags & EF_NODRAW ) && !incoming ) {
		return qfalse;
	}

	if ( incoming ) {
		if ( !cgs.media.poiPowerupIncomingShader ) {
			return qfalse;
		}

		*shader = cgs.media.poiPowerupIncomingShader;
	}

	VectorCopy( origin, distanceOrigin );
	distanceOrigin[2] += 8.0f;
	distance = Distance( cg.refdef.vieworg, distanceOrigin );
	if ( cg.time <= markerTime ) {
		nearDistance = 256.0f;
		farDistance = 512.0f;
	} else {
		nearDistance = 512.0f;
		farDistance = 768.0f;
	}

	if ( distance <= nearDistance ) {
		*alpha = 0.0f;
		return qfalse;
	}
	if ( distance < farDistance ) {
		*alpha = ( distance - nearDistance ) * ( 1.0f / 256.0f );
		return qtrue;
	}

	*alpha = 1.0f - ( distance - farDistance ) * ( 1.0f / 1024.0f );
	if ( *alpha < 0.25f ) {
		*alpha = 0.25f;
	}

	return qtrue;
}

/*
=====================
CG_ItemPOITeamShader

Resolves the retail team-objective POI sprite for a flag item.
=====================
*/
static qhandle_t CG_ItemPOITeamShader( const gitem_t *item ) {
	team_t	localTeam;

	if ( !item ) {
		return 0;
	}

	localTeam = CG_POILocalTeam();
	switch ( item->giTag ) {
	case PW_REDFLAG:
		if ( localTeam == TEAM_RED ) {
			return cgs.media.poiDefendShader;
		}
		if ( localTeam == TEAM_BLUE ) {
			return cgs.media.poiAttackShader;
		}
		if ( cgs.redflag == FLAG_DROPPED && cgs.media.poiFlagDroppedRedShader ) {
			return cgs.media.poiFlagDroppedRedShader;
		}
		return cg_items[ITEM_INDEX( item )].icon;
	case PW_BLUEFLAG:
		if ( localTeam == TEAM_BLUE ) {
			return cgs.media.poiDefendShader;
		}
		if ( localTeam == TEAM_RED ) {
			return cgs.media.poiAttackShader;
		}
		if ( cgs.blueflag == FLAG_DROPPED && cgs.media.poiFlagDroppedBlueShader ) {
			return cgs.media.poiFlagDroppedBlueShader;
		}
		return cg_items[ITEM_INDEX( item )].icon;
	case PW_NEUTRALFLAG:
		if ( localTeam == TEAM_RED || localTeam == TEAM_BLUE ) {
			return cgs.media.poiCaptureShader;
		}
		if ( cgs.flagStatus == FLAG_DROPPED && cgs.media.poiFlagDroppedNeutralShader ) {
			return cgs.media.poiFlagDroppedNeutralShader;
		}
		return cg_items[ITEM_INDEX( item )].icon;
	default:
		break;
	}

	return 0;
}

/*
===================
CG_QueueItemPOIMarker

Queues the retail POI slab for persistent world items and objectives.
===================
*/
static void CG_QueueItemPOIMarker( centity_t *cent, const gitem_t *item, const vec3_t origin ) {
	cgQueuedWorldMarker_t	*marker;
	qhandle_t		shader;
	float			alpha;
	float			zOffset;

	if ( !cent || !item ) {
		return;
	}

	shader = 0;
	alpha = 1.0f;
	zOffset = 24.0f;
	switch ( item->giType ) {
	case IT_POWERUP:
		if ( !CG_ShouldDrawPOIMarkerMode( cg_powerupPOIs.integer, origin ) ) {
			return;
		}
		if ( !CG_ItemPOIPowerupMarker( cent, item, origin, &shader, &alpha ) ) {
			return;
		}
		zOffset = 0.0f;
		break;
	case IT_TEAM:
		if ( !cg_flagPOIs.integer ) {
			return;
		}
		shader = CG_ItemPOITeamShader( item );
		break;
	default:
		return;
	}

	if ( !shader ) {
		return;
	}

	marker = CG_AllocQueuedWorldMarkerForKey( CG_QUEUED_MARKER_KIND_ITEM_POI, cent->currentState.number );
	if ( !marker ) {
		return;
	}

	VectorCopy( origin, marker->origin );
	marker->origin[2] += zOffset;
	marker->duration = 200;
	marker->fadeDelay = 200;
	marker->size = CG_POIMarkerSizeForOrigin( marker->origin );
	marker->shader = shader;
	marker->color[3] = alpha;
}

/*
========================
CG_ItemUsesRespawnTimer

Returns qtrue for retail world items that mirror respawn-timer state through
entityState_t time fields.
========================
*/
static qboolean CG_ItemUsesRespawnTimer( const gitem_t *item ) {
	if ( !item ) {
		return qfalse;
	}

	if ( item->giType == IT_ARMOR && item->quantity >= 25 ) {
		return qtrue;
	}

	if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {
		return qtrue;
	}

	if ( item->giType == IT_POWERUP ) {
		switch ( item->giTag ) {
		case PW_QUAD:
		case PW_BATTLESUIT:
		case PW_HASTE:
		case PW_INVIS:
		case PW_REGEN:
			return qtrue;
		default:
			return qfalse;
		}
	}

	if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {
		return qtrue;
	}

	return qfalse;
}

/*
========================
CG_ItemRespawnTimerDuration

Returns the retail respawn-duration bucket used by major-item timer wedges
when qagame has not yet published an explicit duration.
========================
*/
static int CG_ItemRespawnTimerDuration( const gitem_t *item ) {
	if ( !item ) {
		return 0;
	}

	switch ( item->giType ) {
	case IT_ARMOR:
		if ( item->quantity >= 25 ) {
			return 25 * 1000;
		}
		break;
	case IT_HEALTH:
		if ( item->quantity >= 100 ) {
			return 35 * 1000;
		}
		break;
	case IT_POWERUP:
		switch ( item->giTag ) {
		case PW_QUAD:
		case PW_BATTLESUIT:
		case PW_HASTE:
		case PW_INVIS:
		case PW_REGEN:
			return 120 * 1000;
		default:
			break;
		}
		break;
	case IT_HOLDABLE:
		if ( BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {
			return 60 * 1000;
		}
		break;
	default:
		break;
	}

	return 0;
}

/*
========================
CG_ItemRespawnTimerIcon

Selects the retail timer icon family used by CG_DrawItemRespawnTimer.
========================
*/
static qhandle_t CG_ItemRespawnTimerIcon( const gitem_t *item, qboolean hiddenItem ) {
	if ( !item ) {
		return 0;
	}

	if ( hiddenItem ) {
		return cgs.media.itemTimerUnknownShader;
	}

	switch ( item->giType ) {
	case IT_ARMOR:
		return cgs.media.itemTimerArmorShader;
	case IT_HEALTH:
		if ( item->quantity >= 100 ) {
			return cgs.media.itemTimerHealthShader;
		}
		break;
	case IT_POWERUP:
		switch ( item->giTag ) {
		case PW_QUAD:
			return cgs.media.itemTimerQuadShader;
		case PW_BATTLESUIT:
			return cgs.media.itemTimerBattleSuitShader;
		case PW_HASTE:
			return cgs.media.itemTimerHasteShader;
		case PW_INVIS:
			return cgs.media.itemTimerInvisShader;
		case PW_REGEN:
			return cgs.media.itemTimerRegenShader;
		default:
			return cgs.media.itemTimerUnknownShader;
		}
	case IT_HOLDABLE:
		if ( BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {
			return cgs.media.itemTimerMedkitShader;
		}
		break;
	default:
		break;
	}

	return 0;
}

/*
========================
CG_ItemRespawnTimerSpriteRotation

Converts the retail particle timer angle into this renderer's RT_SPRITE
rotation space.
========================
*/
static float CG_ItemRespawnTimerSpriteRotation( float retailRotation ) {
	return retailRotation - 180.0f;
}

/*
========================
CG_ItemRespawnTimerSlices

Maps the retail respawn duration buckets onto the matching timer wedge family.
========================
*/
static void CG_ItemRespawnTimerSlices( int respawnDuration, qhandle_t *sliceShader, qhandle_t *currentSliceShader,
	int *sliceCount ) {
	int	durationBuckets;

	if ( !sliceShader || !currentSliceShader || !sliceCount ) {
		return;
	}

	*sliceShader = 0;
	*currentSliceShader = 0;
	*sliceCount = 0;
	if ( respawnDuration <= 0 ) {
		return;
	}

	durationBuckets = respawnDuration / 5000;
	if ( durationBuckets <= 5 ) {
		*sliceShader = cgs.media.itemTimerSlice5Shader;
		*currentSliceShader = cgs.media.itemTimerSlice5CurrentShader;
		*sliceCount = 5;
		return;
	}

	if ( durationBuckets <= 7 ) {
		*sliceShader = cgs.media.itemTimerSlice7Shader;
		*currentSliceShader = cgs.media.itemTimerSlice7CurrentShader;
		*sliceCount = 7;
		return;
	}

	if ( durationBuckets <= 12 ) {
		*sliceShader = cgs.media.itemTimerSlice12Shader;
		*currentSliceShader = cgs.media.itemTimerSlice12CurrentShader;
		*sliceCount = 12;
		return;
	}

	*sliceShader = cgs.media.itemTimerSlice24Shader;
	*currentSliceShader = cgs.media.itemTimerSlice24CurrentShader;
	*sliceCount = 24;
}

/*
========================
CG_DrawItemRespawnTimerSprite

Adds one timer icon or wedge sprite to the scene using the shared world-item
origin.
========================
*/
static void CG_DrawItemRespawnTimerSprite( qhandle_t shader, const vec3_t origin, float alpha, float rotation ) {
	refEntity_t	ent;
	int		alphaByte;

	if ( !shader || alpha <= 0.0f ) {
		return;
	}

	memset( &ent, 0, sizeof( ent ) );
	ent.reType = RT_SPRITE;
	VectorCopy( origin, ent.origin );
	VectorCopy( origin, ent.oldorigin );
	ent.radius = 16.0f;
	ent.rotation = CG_ItemRespawnTimerSpriteRotation( rotation );
	ent.customShader = shader;

	alphaByte = (int)( alpha * 255.0f );
	if ( alphaByte < 0 ) {
		alphaByte = 0;
	} else if ( alphaByte > 255 ) {
		alphaByte = 255;
	}

	ent.shaderRGBA[0] = 255;
	ent.shaderRGBA[1] = 255;
	ent.shaderRGBA[2] = 255;
	ent.shaderRGBA[3] = alphaByte;
	trap_R_AddRefEntityToScene( &ent );
}

/*
========================
CG_DrawItemRespawnTimer

Draws the retail world-item respawn timer icon and wedge countdown around one
major item.
========================
*/
static void CG_DrawItemRespawnTimer( const gitem_t *item, int respawnRemaining, int respawnDuration,
	const vec3_t origin, int elapsedSlice, qboolean hiddenItem ) {
	vec3_t		timerOrigin;
	float		distance;
	float		alpha;
	qhandle_t	iconShader;
	qhandle_t	sliceShader;
	qhandle_t	currentSliceShader;
	int		sliceCount;
	int		sliceStep;
	int		rotation;
	int		sliceIndex;

	if ( !item || !origin || !cg_itemTimers.integer ) {
		return;
	}

	if ( respawnRemaining <= 0 || respawnDuration <= 0 ) {
		return;
	}

	if ( respawnRemaining > respawnDuration ) {
		respawnRemaining = respawnDuration;
	}

	iconShader = CG_ItemRespawnTimerIcon( item, hiddenItem );
	if ( !iconShader ) {
		return;
	}

	VectorCopy( origin, timerOrigin );
	timerOrigin[2] += 8.0f;
	distance = Distance( cg.refdef.vieworg, timerOrigin );
	if ( distance <= 256.0f ) {
		alpha = 1.0f;
	} else if ( distance < 768.0f ) {
		alpha = ( 768.0f - distance ) * ( 1.0f / 512.0f );
	} else {
		return;
	}

	CG_ItemRespawnTimerSlices( respawnDuration, &sliceShader, &currentSliceShader, &sliceCount );
	if ( !sliceShader || !currentSliceShader || sliceCount <= 0 ) {
		return;
	}

	if ( elapsedSlice <= 0 ) {
		elapsedSlice = ( ( respawnDuration - respawnRemaining ) / 5000 ) + 1;
	}
	if ( elapsedSlice < 1 ) {
		elapsedSlice = 1;
	} else if ( elapsedSlice > sliceCount ) {
		elapsedSlice = sliceCount;
	}

	CG_DrawItemRespawnTimerSprite( iconShader, timerOrigin, alpha, 180.0f );

	sliceStep = 360 / sliceCount;
	rotation = -( 180 / sliceCount );
	for ( sliceIndex = 1; sliceIndex <= elapsedSlice; sliceIndex++ ) {
		rotation += sliceStep;
		CG_DrawItemRespawnTimerSprite( ( sliceIndex == elapsedSlice ) ? currentSliceShader : sliceShader,
			timerOrigin, alpha, (float)rotation );
	}
}

/*
==================
CG_Item
==================
*/
static void CG_Item( centity_t *cent ) {
	refEntity_t		ent;
	entityState_t	*es;
	gitem_t			*item;
	int				msec;
	float			frac;
	float			scale;
	int				respawnDuration;
	int				respawnRemaining;
	weaponInfo_t	*wi;
	char			skipItems[32];
	vec3_t			itemPOIOrigin;

	es = &cent->currentState;
	if ( es->modelindex >= bg_numItems ) {
		CG_Error( "Bad item index %i on entity", es->modelindex );
	}

	if ( !es->modelindex ) {
		return;
	}

	item = &bg_itemlist[ es->modelindex ];
	if ( CG_ItemUsesRespawnTimer( item ) && es->time > cg.time ) {
		respawnDuration = es->time2;
		if ( respawnDuration <= 0 ) {
			respawnDuration = CG_ItemRespawnTimerDuration( item );
		}

		if ( respawnDuration > 0 ) {
			respawnRemaining = es->time - cg.time;
			CG_DrawItemRespawnTimer( item, respawnRemaining, respawnDuration, cent->lerpOrigin, 0,
				(qboolean)( es->retailEventData != 0 ) );
		}
	}

	trap_Cvar_VariableStringBuffer( "cg_skipItems", skipItems, sizeof( skipItems ) );
	if ( skipItems[0] == '1' ) {
		return;
	}

	VectorCopy( cent->lerpOrigin, itemPOIOrigin );
	if ( !( es->eFlags & EF_NODRAW ) || item->giType == IT_POWERUP ) {
		CG_UpdatePOIObjectiveCache( item, itemPOIOrigin );
		CG_QueueItemPOIMarker( cent, item, itemPOIOrigin );
	}

	if ( es->eFlags & EF_NODRAW ) {
		return;
	}

	if ( cg_simpleItems.integer && item->giType != IT_TEAM ) {
		memset( &ent, 0, sizeof( ent ) );
		ent.reType = RT_SPRITE;
		VectorCopy( cent->lerpOrigin, ent.origin );
		if ( cg.simpleItemsBob > 0.0f ) {
			float		spriteBobScale;

			spriteBobScale = 0.005f + cent->currentState.number * 0.00001f;
			ent.origin[2] += cos( ( cg.time + 1000 ) * spriteBobScale ) * cg.simpleItemsBob;
		}
		ent.origin[2] += cg.simpleItemsHeightOffset;
		ent.radius = cg.simpleItemsRadius;
		ent.customShader = cg_items[es->modelindex].icon;
		ent.shaderRGBA[0] = 255;
		ent.shaderRGBA[1] = 255;
		ent.shaderRGBA[2] = 255;
		ent.shaderRGBA[3] = 255;
		trap_R_AddRefEntityToScene(&ent);
		return;
	}

	// items bob up and down continuously
	scale = 0.005 + cent->currentState.number * 0.00001;
	cent->lerpOrigin[2] += 4 + cos( ( cg.time + 1000 ) *  scale ) * 4;

	memset (&ent, 0, sizeof(ent));

	// autorotate at one of two speeds
	if ( item->giType == IT_HEALTH ) {
		VectorCopy( cg.autoAnglesFast, cent->lerpAngles );
		AxisCopy( cg.autoAxisFast, ent.axis );
	} else {
		VectorCopy( cg.autoAngles, cent->lerpAngles );
		AxisCopy( cg.autoAxis, ent.axis );
	}

	wi = NULL;
	// the weapons have their origin where they attatch to player
	// models, so we need to offset them or they will rotate
	// eccentricly
	if ( item->giType == IT_WEAPON ) {
		wi = &cg_weapons[BG_WeaponForItemTag( item->giTag )];
		cent->lerpOrigin[0] -= 
			wi->weaponMidpoint[0] * ent.axis[0][0] +
			wi->weaponMidpoint[1] * ent.axis[1][0] +
			wi->weaponMidpoint[2] * ent.axis[2][0];
		cent->lerpOrigin[1] -= 
			wi->weaponMidpoint[0] * ent.axis[0][1] +
			wi->weaponMidpoint[1] * ent.axis[1][1] +
			wi->weaponMidpoint[2] * ent.axis[2][1];
		cent->lerpOrigin[2] -= 
			wi->weaponMidpoint[0] * ent.axis[0][2] +
			wi->weaponMidpoint[1] * ent.axis[1][2] +
			wi->weaponMidpoint[2] * ent.axis[2][2];

		cent->lerpOrigin[2] += 8;	// an extra height boost
	}

	ent.hModel = cg_items[es->modelindex].models[0];

	VectorCopy( cent->lerpOrigin, ent.origin);
	VectorCopy( cent->lerpOrigin, ent.oldorigin);

	ent.nonNormalizedAxes = qfalse;

	// if just respawned, slowly scale up
	msec = cg.time - cent->miscTime;
	if ( msec >= 0 && msec < ITEM_SCALEUP_TIME ) {
		frac = (float)msec / ITEM_SCALEUP_TIME;
		VectorScale( ent.axis[0], frac, ent.axis[0] );
		VectorScale( ent.axis[1], frac, ent.axis[1] );
		VectorScale( ent.axis[2], frac, ent.axis[2] );
		ent.nonNormalizedAxes = qtrue;
	} else {
		frac = 1.0;
	}

	// items without glow textures need to keep a minimum light value
	// so they are always visible
	if ( ( item->giType == IT_WEAPON ) ||
		 ( item->giType == IT_ARMOR ) ) {
		ent.renderfx |= RF_MINLIGHT;
	}

	// increase the size of the weapons when they are presented as items
	if ( item->giType == IT_WEAPON ) {
		VectorScale( ent.axis[0], 1.5, ent.axis[0] );
		VectorScale( ent.axis[1], 1.5, ent.axis[1] );
		VectorScale( ent.axis[2], 1.5, ent.axis[2] );
		ent.nonNormalizedAxes = qtrue;
		trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, cgs.media.weaponHoverSound );
	}

	if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_KAMIKAZE ) {
		VectorScale( ent.axis[0], 2, ent.axis[0] );
		VectorScale( ent.axis[1], 2, ent.axis[1] );
		VectorScale( ent.axis[2], 2, ent.axis[2] );
		ent.nonNormalizedAxes = qtrue;
	}

	// add to refresh list
	trap_R_AddRefEntityToScene(&ent);

	if ( item->giType == IT_WEAPON && wi->barrelModel ) {
		refEntity_t	barrel;

		memset( &barrel, 0, sizeof( barrel ) );

		barrel.hModel = wi->barrelModel;

		VectorCopy( ent.lightingOrigin, barrel.lightingOrigin );
		barrel.shadowPlane = ent.shadowPlane;
		barrel.renderfx = ent.renderfx;

		CG_PositionRotatedEntityOnTag( &barrel, &ent, wi->weaponModel, "tag_barrel" );

		AxisCopy( ent.axis, barrel.axis );
		barrel.nonNormalizedAxes = ent.nonNormalizedAxes;

		trap_R_AddRefEntityToScene( &barrel );
	}

	// accompanying rings / spheres for powerups
	if ( !cg_simpleItems.integer ) 
	{
		vec3_t spinAngles;

		VectorClear( spinAngles );

		if ( item->giType == IT_HEALTH || item->giType == IT_POWERUP )
		{
			if ( ( ent.hModel = cg_items[es->modelindex].models[1] ) != 0 )
			{
				if ( item->giType == IT_POWERUP )
				{
					ent.origin[2] += 12;
					spinAngles[1] = ( cg.time & 1023 ) * 360 / -1024.0f;
				}
				AnglesToAxis( spinAngles, ent.axis );
				
				// scale up if respawning
				if ( frac != 1.0 ) {
					VectorScale( ent.axis[0], frac, ent.axis[0] );
					VectorScale( ent.axis[1], frac, ent.axis[1] );
					VectorScale( ent.axis[2], frac, ent.axis[2] );
					ent.nonNormalizedAxes = qtrue;
				}
				trap_R_AddRefEntityToScene( &ent );
			}
		}
	}
}

//============================================================================

/*
=============
CG_ApplyGrenadeEntityColor

Applies the cached grenade weapon color to the model entity color lane used by
retail rgbGen entity grenade shaders.
=============
*/
static void CG_ApplyGrenadeEntityColor( refEntity_t *ent ) {
	if ( !ent ) {
		return;
	}

	ent->shaderRGBA[0] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[0] ) * 255.0f );
	ent->shaderRGBA[1] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[1] ) * 255.0f );
	ent->shaderRGBA[2] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[2] ) * 255.0f );
	ent->shaderRGBA[3] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[3] ) * 255.0f );
}

/*
===============
CG_Missile
===============
*/
static void CG_Missile( centity_t *cent ) {
	refEntity_t			ent;
	entityState_t		*s1;
	const weaponInfo_t		*weapon;
//	int	col;

	s1 = &cent->currentState;
	if ( s1->weapon > WP_NUM_WEAPONS ) {
		s1->weapon = 0;
	}
	weapon = &cg_weapons[s1->weapon];

	// calculate the axis
	VectorCopy( s1->angles, cent->lerpAngles);

	// add trails
	if ( weapon->missileTrailFunc ) 
	{
		weapon->missileTrailFunc( cent, weapon );
	}
/*
	if ( cent->currentState.modelindex == TEAM_RED ) {
		col = 1;
	}
	else if ( cent->currentState.modelindex == TEAM_BLUE ) {
		col = 2;
	}
	else {
		col = 0;
	}

	// add dynamic light
	if ( weapon->missileDlight ) {
		trap_R_AddLightToScene(cent->lerpOrigin, weapon->missileDlight, 
			weapon->missileDlightColor[col][0], weapon->missileDlightColor[col][1], weapon->missileDlightColor[col][2] );
	}
*/
	// add dynamic light
	if ( weapon->missileDlight ) {
		trap_R_AddLightToScene(cent->lerpOrigin, weapon->missileDlight, 
			weapon->missileDlightColor[0], weapon->missileDlightColor[1], weapon->missileDlightColor[2] );
	}

	// add missile sound
	if ( weapon->missileSound ) {
		vec3_t	velocity;

		BG_EvaluateTrajectoryDelta( &cent->currentState.pos, cg.time, velocity );

		trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, velocity, weapon->missileSound );
	}

	// create the render entity
	memset (&ent, 0, sizeof(ent));
	VectorCopy( cent->lerpOrigin, ent.origin);
	VectorCopy( cent->lerpOrigin, ent.oldorigin);

	if ( cent->currentState.weapon == WP_PLASMAGUN ) {
		ent.reType = RT_SPRITE;
		ent.radius = 16;
		ent.rotation = 0;
		ent.customShader = cgs.media.plasmaBallShader;
		trap_R_AddRefEntityToScene( &ent );
		return;
	}

	// flicker between two skins
	ent.skinNum = cg.clientFrame & 1;
	ent.hModel = weapon->missileModel;
	ent.renderfx = weapon->missileRenderfx | RF_NOSHADOW;

	if ( cent->currentState.weapon == WP_PROX_LAUNCHER ) {
		if (s1->generic1 == TEAM_BLUE) {
			ent.hModel = cgs.media.blueProxMine;
		}
	}

	if ( cent->currentState.weapon == WP_GRENADE_LAUNCHER ) {
		CG_ApplyGrenadeEntityColor( &ent );
	}

	// convert direction of travel into axis
	if ( VectorNormalize2( s1->pos.trDelta, ent.axis[0] ) == 0 ) {
		ent.axis[0][2] = 1;
	}

	// spin as it moves
	if ( s1->pos.trType != TR_STATIONARY ) {
		RotateAroundDirection( ent.axis, cg.time / 4 );
	} else {
		if ( s1->weapon == WP_PROX_LAUNCHER ) {
			AnglesToAxis( cent->lerpAngles, ent.axis );
		}
		else
		{
			RotateAroundDirection( ent.axis, s1->time );
		}
	}

	// add to refresh list, possibly with quad glow
	CG_AddRefEntityWithPowerups( &ent, s1, TEAM_FREE );
}

/*
===============
CG_Grapple

This is called when the grapple is sitting up against the wall
===============
*/
static void CG_Grapple( centity_t *cent ) {
	refEntity_t			ent;
	entityState_t		*s1;
	const weaponInfo_t		*weapon;

	s1 = &cent->currentState;
	if ( s1->weapon > WP_NUM_WEAPONS ) {
		s1->weapon = 0;
	}
	weapon = &cg_weapons[s1->weapon];

	// calculate the axis
	VectorCopy( s1->angles, cent->lerpAngles);

#if 0 // FIXME add grapple pull sound here..?
	// add missile sound
	if ( weapon->missileSound ) {
		trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, weapon->missileSound );
	}
#endif

	// Will draw cable if needed
	CG_GrappleTrail ( cent, weapon );

	// create the render entity
	memset (&ent, 0, sizeof(ent));
	VectorCopy( cent->lerpOrigin, ent.origin);
	VectorCopy( cent->lerpOrigin, ent.oldorigin);

	// flicker between two skins
	ent.skinNum = cg.clientFrame & 1;
	ent.hModel = weapon->missileModel;
	ent.renderfx = weapon->missileRenderfx | RF_NOSHADOW;

	// convert direction of travel into axis
	if ( VectorNormalize2( s1->pos.trDelta, ent.axis[0] ) == 0 ) {
		ent.axis[0][2] = 1;
	}

	trap_R_AddRefEntityToScene( &ent );
}

/*
===============
CG_Mover
===============
*/
static void CG_Mover( centity_t *cent ) {
	refEntity_t			ent;
	entityState_t		*s1;

	s1 = &cent->currentState;

	// create the render entity
	memset (&ent, 0, sizeof(ent));
	VectorCopy( cent->lerpOrigin, ent.origin);
	VectorCopy( cent->lerpOrigin, ent.oldorigin);
	AnglesToAxis( cent->lerpAngles, ent.axis );

	ent.renderfx = RF_NOSHADOW;

	// flicker between two skins (FIXME?)
	ent.skinNum = ( cg.time >> 6 ) & 1;

	// get the model, either as a bmodel or a modelindex
	if ( s1->solid == SOLID_BMODEL ) {
		ent.hModel = cgs.inlineDrawModel[s1->modelindex];
	} else {
		ent.hModel = cgs.gameModels[s1->modelindex];
	}

	// add to refresh list
	trap_R_AddRefEntityToScene(&ent);

	// add the secondary model
	if ( s1->modelindex2 ) {
		ent.skinNum = 0;
		ent.hModel = cgs.gameModels[s1->modelindex2];
		trap_R_AddRefEntityToScene(&ent);
	}

}

/*
===============
CG_Beam

Also called as an event
===============
*/
void CG_Beam( centity_t *cent ) {
	localEntity_t		*le;
	refEntity_t			*beam;
	entityState_t		*s1;

	s1 = &cent->currentState;

	le = CG_AllocLocalEntity();
	le->leFlags = 0;
	le->leType = LE_SHOWREFENTITY;
	le->startTime = cg.time;
	le->endTime = cg.time + 500;
	le->lifeRate = 1.0f / ( le->endTime - le->startTime );
	le->color[0] = 0.75f;
	le->color[1] = 0.0f;
	le->color[2] = 0.0f;
	le->color[3] = 1.0f;

	beam = &le->refEntity;
	beam->reType = RT_RAIL_CORE;
	beam->customShader = cgs.media.railCoreShader;
	beam->shaderTime = cg.time / 1000.0f;
	beam->radius = 256.0f;
	beam->shaderRGBA[0] = 0xbf;
	beam->shaderRGBA[1] = 0x00;
	beam->shaderRGBA[2] = 0x00;
	beam->shaderRGBA[3] = 0xff;
	VectorCopy( s1->pos.trBase, beam->origin );
	VectorCopy( s1->origin2, beam->oldorigin );
	AxisClear( beam->axis );

}


/*
===============
CG_Portal
===============
*/
static void CG_Portal( centity_t *cent ) {
	refEntity_t			ent;
	entityState_t		*s1;

	s1 = &cent->currentState;

	// create the render entity
	memset (&ent, 0, sizeof(ent));
	VectorCopy( cent->lerpOrigin, ent.origin );
	VectorCopy( s1->origin2, ent.oldorigin );
	ByteToDir( s1->eventParm, ent.axis[0] );
	PerpendicularVector( ent.axis[1], ent.axis[0] );

	// negating this tends to get the directions like they want
	// we really should have a camera roll value
	VectorSubtract( vec3_origin, ent.axis[1], ent.axis[1] );

	CrossProduct( ent.axis[0], ent.axis[1], ent.axis[2] );
	ent.reType = RT_PORTALSURFACE;
	ent.oldframe = s1->powerups;
	ent.frame = s1->frame;		// rotation speed
	ent.skinNum = s1->clientNum/256.0 * 360;	// roll offset

	// add to refresh list
	trap_R_AddRefEntityToScene(&ent);
}


/*
=========================
CG_AdjustPositionForMover

Also called by client movement prediction code
=========================
*/
void CG_AdjustPositionForMover( const vec3_t in, int moverNum, int fromTime, int toTime, vec3_t out ) {
	centity_t	*cent;
	vec3_t	oldOrigin, origin, deltaOrigin;
	vec3_t	oldAngles, angles, deltaAngles;

	if ( moverNum <= 0 || moverNum >= ENTITYNUM_MAX_NORMAL ) {
		VectorCopy( in, out );
		return;
	}

	cent = &cg_entities[ moverNum ];
	if ( cent->currentState.eType != ET_MOVER ) {
		VectorCopy( in, out );
		return;
	}

	BG_EvaluateTrajectory( &cent->currentState.pos, fromTime, oldOrigin );
	BG_EvaluateTrajectory( &cent->currentState.apos, fromTime, oldAngles );

	BG_EvaluateTrajectory( &cent->currentState.pos, toTime, origin );
	BG_EvaluateTrajectory( &cent->currentState.apos, toTime, angles );

	VectorSubtract( origin, oldOrigin, deltaOrigin );
	VectorSubtract( angles, oldAngles, deltaAngles );

	VectorAdd( in, deltaOrigin, out );

	// FIXME: origin change when on a rotating object
}


/*
=============================
CG_InterpolateEntityPosition
=============================
*/
static void CG_InterpolateEntityPosition( centity_t *cent ) {
	vec3_t		current, next;
	float		f;

	// it would be an internal error to find an entity that interpolates without
	// a snapshot ahead of the current one
	if ( cg.nextSnap == NULL ) {
		CG_Error( "CG_InterpoateEntityPosition: cg.nextSnap == NULL" );
	}

	f = cg.frameInterpolation;

	// this will linearize a sine or parabolic curve, but it is important
	// to not extrapolate player positions if more recent data is available
	BG_EvaluateTrajectory( &cent->currentState.pos, cg.snap->serverTime, current );
	BG_EvaluateTrajectory( &cent->nextState.pos, cg.nextSnap->serverTime, next );

	cent->lerpOrigin[0] = current[0] + f * ( next[0] - current[0] );
	cent->lerpOrigin[1] = current[1] + f * ( next[1] - current[1] );
	cent->lerpOrigin[2] = current[2] + f * ( next[2] - current[2] );

	BG_EvaluateTrajectory( &cent->currentState.apos, cg.snap->serverTime, current );
	BG_EvaluateTrajectory( &cent->nextState.apos, cg.nextSnap->serverTime, next );

	cent->lerpAngles[0] = LerpAngle( current[0], next[0], f );
	cent->lerpAngles[1] = LerpAngle( current[1], next[1], f );
	cent->lerpAngles[2] = LerpAngle( current[2], next[2], f );

}

/*
===============
CG_CalcEntityLerpPositions

===============
*/
static void CG_CalcEntityLerpPositions( centity_t *cent ) {

	// if this player does not want to see extrapolated players
	if ( !cg_smoothClients.integer ) {
		// make sure the clients use TR_INTERPOLATE
		if ( cent->currentState.number < MAX_CLIENTS ) {
			cent->currentState.pos.trType = TR_INTERPOLATE;
			cent->nextState.pos.trType = TR_INTERPOLATE;
		}
	}

	if ( cent->interpolate && cent->currentState.pos.trType == TR_INTERPOLATE ) {
		CG_InterpolateEntityPosition( cent );
		return;
	}

	// first see if we can interpolate between two snaps for
	// linear extrapolated clients
	if ( cent->interpolate && cent->currentState.pos.trType == TR_LINEAR_STOP &&
											cent->currentState.number < MAX_CLIENTS) {
		CG_InterpolateEntityPosition( cent );
		return;
	}

	// just use the current frame and evaluate as best we can
	BG_EvaluateTrajectory( &cent->currentState.pos, cg.time, cent->lerpOrigin );
	BG_EvaluateTrajectory( &cent->currentState.apos, cg.time, cent->lerpAngles );

	// adjust for riding a mover if it wasn't rolled into the predicted
	// player state
	if ( cent != &cg.predictedPlayerEntity ) {
		CG_AdjustPositionForMover( cent->lerpOrigin, cent->currentState.groundEntityNum, 
		cg.snap->serverTime, cg.time, cent->lerpOrigin );
	}
}
#define DOM_POINT_ICON_HEIGHT 64.0f
#define DOM_POINT_NEAR_RADIUS 36.0f
#define DOM_POINT_FAR_RADIUS 24.0f

/*
=============
CG_DominationClampTeam

Normalizes potentially invalid team numbers to valid enums.
=============
*/
static team_t CG_DominationClampTeam( int value ) {
	if ( value >= TEAM_RED && value <= TEAM_SPECTATOR ) {
		return (team_t)value;
	}

	return TEAM_FREE;
}

/*
=============
CG_DominationProgressIndex

Converts the transmitted capture progress into a shader bucket.
=============
*/
static int CG_DominationProgressIndex( float progress ) {
	float	clamped;
	int		index;

	clamped = Com_Clamp( 0.0f, 1.0f, progress );
	index = (int)( clamped * DOM_POINT_STATE_COUNT );
	if ( index >= DOM_POINT_STATE_COUNT ) {
		index = DOM_POINT_STATE_COUNT - 1;
	}

	return index;
}

/*
=============
CG_DominationSelectShader

Picks the capture/defense overlay shader for a Domination point.
=============
*/
static qhandle_t CG_DominationSelectShader( qboolean capture, qboolean distress, int index ) {
	if ( index < 0 || index >= DOM_POINT_STATE_COUNT ) {
		return 0;
	}

	if ( capture ) {
		return distress ? cgs.media.domCapDistressShaders[index] : cgs.media.domCapShaders[index];
	}

	return distress ? cgs.media.domDefDistressShaders[index] : cgs.media.domDefShaders[index];
}

/*
=============
CG_DominationAddBillboard

Adds a sprite overlay for Domination control points.
=============
*/
static void CG_DominationAddBillboard( const centity_t *cent, qhandle_t shader, float height, float radius ) {
	refEntity_t ent;

	if ( !shader ) {
		return;
	}

	memset( &ent, 0, sizeof( ent ) );
	ent.reType = RT_SPRITE;
	ent.customShader = shader;
	ent.radius = radius;
	ent.rotation = 0.0f;
	ent.shaderRGBA[0] = 0xff;
	ent.shaderRGBA[1] = 0xff;
	ent.shaderRGBA[2] = 0xff;
	ent.shaderRGBA[3] = 0xff;
	VectorCopy( cent->lerpOrigin, ent.origin );
	ent.origin[2] += height;

	trap_R_AddRefEntityToScene( &ent );
}

/*
=============
CG_QueueDominationPointBillboard

Queues the retail Domination point overlay marker beneath the main model.
=============
*/
static void CG_QueueDominationPointBillboard( centity_t *cent ) {
	team_t		owner;
	team_t		capturing;
	team_t		viewerTeam;
	float		progress;
	int		progressIndex;
	qhandle_t	shader;
	qboolean	captureIcon;
	qboolean	distress;
	vec3_t	delta;
	float		distance;
	float		radius;

	if ( !cent ) {
		return;
	}

	owner = CG_DominationClampTeam( cent->currentState.modelindex );
	capturing = CG_DominationClampTeam( cent->currentState.modelindex2 );
	if ( capturing == TEAM_FREE ) {
		return;
	}

	viewerTeam = TEAM_FREE;
	if ( cg.snap ) {
		viewerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	}

	progress = (float)cent->currentState.frame / 255.0f;
	progressIndex = CG_DominationProgressIndex( progress );
	distress = qfalse;
	if ( cent->currentState.time2 > 0 ) {
		distress = ( cg.time - cent->currentState.time2 ) <= DOMINATION_DISTRESS_REPEAT_TIME;
	}

	captureIcon = qtrue;
	if ( viewerTeam == owner && owner != TEAM_FREE ) {
		captureIcon = qfalse;
	} else if ( viewerTeam == TEAM_FREE || viewerTeam == TEAM_SPECTATOR || owner == TEAM_FREE ) {
		captureIcon = qtrue;
	}

	shader = CG_DominationSelectShader( captureIcon, distress, progressIndex );
	if ( !shader ) {
		return;
	}

	VectorSubtract( cg.refdef.vieworg, cent->lerpOrigin, delta );
	distance = VectorLength( delta );
	radius = ( distance < 512.0f ) ? DOM_POINT_NEAR_RADIUS : DOM_POINT_FAR_RADIUS;

	CG_DominationAddBillboard( cent, shader, DOM_POINT_ICON_HEIGHT, radius );
}

/*
=============
CG_DominationPoint

Renders Domination capture points and their icon overlays.
=============
*/
static void CG_DominationPoint( centity_t *cent ) {
	refEntity_t	model;
	team_t		owner;
	team_t		capturing;
	team_t		viewerTeam;
	qboolean	distress;

	if ( !cgs.media.domPointModel ) {
		return;
	}

	owner = CG_DominationClampTeam( cent->currentState.modelindex );
	capturing = CG_DominationClampTeam( cent->currentState.modelindex2 );
	viewerTeam = TEAM_FREE;
	if ( cg.snap ) {
		viewerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	}

	memset( &model, 0, sizeof( model ) );
	model.reType = RT_MODEL;
	model.hModel = cgs.media.domPointModel;
	VectorCopy( cent->lerpOrigin, model.origin );
	VectorCopy( cent->lerpOrigin, model.lightingOrigin );
	AnglesToAxis( cent->currentState.angles, model.axis );
	switch ( owner ) {
	case TEAM_RED:
		model.customSkin = cgs.media.domPointSkinRed;
		break;
	case TEAM_BLUE:
		model.customSkin = cgs.media.domPointSkinBlue;
		break;
	case TEAM_FREE:
	default:
		model.customSkin = cgs.media.domPointSkinNeutral;
		break;
	}

	trap_R_AddRefEntityToScene( &model );

	if ( capturing == TEAM_FREE ) {
		cent->miscTime = 0;
		return;
	}

	distress = qfalse;
	if ( cent->currentState.time2 > 0 ) {
		distress = ( cg.time - cent->currentState.time2 ) <= DOMINATION_DISTRESS_REPEAT_TIME;
	}

	CG_QueueDominationPointBillboard( cent );

	if ( distress && viewerTeam == owner && owner != TEAM_FREE && cgs.media.dominationDistressSound ) {
		if ( cg.time - cent->miscTime >= DOMINATION_DISTRESS_REPEAT_TIME ) {
			trap_S_StartSound( cent->lerpOrigin, ENTITYNUM_NONE, CHAN_LOCAL, cgs.media.dominationDistressSound );
			cent->miscTime = cg.time;
		}
	} else if ( !distress ) {
		cent->miscTime = 0;
	}
}



/*
===============
CG_TeamBase
===============
*/
static void CG_TeamBase( centity_t *cent ) {
	refEntity_t model;
	vec3_t angles;
	int t, h;
	float c;

	if ( cgs.gametype == GT_DOMINATION ) {
		CG_DominationPoint( cent );
		return;
	}

	if ( cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF ) {
		// show the flag base
		memset(&model, 0, sizeof(model));
		model.reType = RT_MODEL;
		VectorCopy( cent->lerpOrigin, model.lightingOrigin );
		VectorCopy( cent->lerpOrigin, model.origin );
		AnglesToAxis( cent->currentState.angles, model.axis );
		if ( cent->currentState.modelindex == TEAM_RED ) {
			model.hModel = cgs.media.redFlagBaseModel;
		}
		else if ( cent->currentState.modelindex == TEAM_BLUE ) {
			model.hModel = cgs.media.blueFlagBaseModel;
		}
		else {
			model.hModel = cgs.media.neutralFlagBaseModel;
		}
		trap_R_AddRefEntityToScene( &model );
	}
	else if ( cgs.gametype == GT_OBELISK ) {
		// show the obelisk
		memset(&model, 0, sizeof(model));
		model.reType = RT_MODEL;
		VectorCopy( cent->lerpOrigin, model.lightingOrigin );
		VectorCopy( cent->lerpOrigin, model.origin );
		AnglesToAxis( cent->currentState.angles, model.axis );

		model.hModel = cgs.media.overloadBaseModel;
		trap_R_AddRefEntityToScene( &model );
		// if hit
		if ( cent->currentState.frame == 1) {
			// show hit model
			// modelindex2 is the health value of the obelisk
			c = cent->currentState.modelindex2;
			model.shaderRGBA[0] = 0xff;
			model.shaderRGBA[1] = c;
			model.shaderRGBA[2] = c;
			model.shaderRGBA[3] = 0xff;
			//
			model.hModel = cgs.media.overloadEnergyModel;
			trap_R_AddRefEntityToScene( &model );
		}
		// if respawning
		if ( cent->currentState.frame == 2) {
			if ( !cent->miscTime ) {
				cent->miscTime = cg.time;
			}
			t = cg.time - cent->miscTime;
			h = (cg_obeliskRespawnDelay.integer - 5) * 1000;
			//
			if (t > h) {
				c = (float) (t - h) / h;
				if (c > 1)
					c = 1;
			}
			else {
				c = 0;
			}
			// show the lights
			AnglesToAxis( cent->currentState.angles, model.axis );
			//
			model.shaderRGBA[0] = c * 0xff;
			model.shaderRGBA[1] = c * 0xff;
			model.shaderRGBA[2] = c * 0xff;
			model.shaderRGBA[3] = c * 0xff;

			model.hModel = cgs.media.overloadLightsModel;
			trap_R_AddRefEntityToScene( &model );
			// show the target
			if (t > h) {
				if ( !cent->muzzleFlashTime ) {
					trap_S_StartSound (cent->lerpOrigin, ENTITYNUM_NONE, CHAN_BODY,  cgs.media.obeliskRespawnSound);
					cent->muzzleFlashTime = 1;
				}
				VectorCopy(cent->currentState.angles, angles);
				angles[YAW] += (float) 16 * acos(1-c) * 180 / M_PI;
				AnglesToAxis( angles, model.axis );

				VectorScale( model.axis[0], c, model.axis[0]);
				VectorScale( model.axis[1], c, model.axis[1]);
				VectorScale( model.axis[2], c, model.axis[2]);

				model.shaderRGBA[0] = 0xff;
				model.shaderRGBA[1] = 0xff;
				model.shaderRGBA[2] = 0xff;
				model.shaderRGBA[3] = 0xff;
				//
				model.origin[2] += 56;
				model.hModel = cgs.media.overloadTargetModel;
				trap_R_AddRefEntityToScene( &model );
			}
			else {
				//FIXME: show animated smoke
			}
		}
		else {
			cent->miscTime = 0;
			cent->muzzleFlashTime = 0;
			// modelindex2 is the health value of the obelisk
			c = cent->currentState.modelindex2;
			model.shaderRGBA[0] = 0xff;
			model.shaderRGBA[1] = c;
			model.shaderRGBA[2] = c;
			model.shaderRGBA[3] = 0xff;
			// show the lights
			model.hModel = cgs.media.overloadLightsModel;
			trap_R_AddRefEntityToScene( &model );
			// show the target
			model.origin[2] += 56;
			model.hModel = cgs.media.overloadTargetModel;
			trap_R_AddRefEntityToScene( &model );
		}
	}
	else if ( cgs.gametype == GT_HARVESTER ) {
		// show harvester model
		memset(&model, 0, sizeof(model));
		model.reType = RT_MODEL;
		VectorCopy( cent->lerpOrigin, model.lightingOrigin );
		VectorCopy( cent->lerpOrigin, model.origin );
		AnglesToAxis( cent->currentState.angles, model.axis );

		if ( cent->currentState.modelindex == TEAM_RED ) {
			model.hModel = cgs.media.harvesterModel;
			model.customSkin = cgs.media.harvesterRedSkin;
		}
		else if ( cent->currentState.modelindex == TEAM_BLUE ) {
			model.hModel = cgs.media.harvesterModel;
			model.customSkin = cgs.media.harvesterBlueSkin;
		}
		else {
			model.hModel = cgs.media.harvesterNeutralModel;
			model.customSkin = 0;
		}
		trap_R_AddRefEntityToScene( &model );
	}
}

/*
===============
CG_AddCEntity

===============
*/
static void CG_AddCEntity( centity_t *cent ) {
	// event-only entities will have been dealt with already
	// Retail leaves the one-past-tail event slot on the slow path so it still
	// trips the bad-entity-type fault instead of being silently skipped.
	if ( cent->currentState.eType > ET_EVENTS
		&& cent->currentState.eType != ( ET_EVENTS + EV_NEW_HIGH_SCORE + 1 ) ) {
		return;
	}

	// calculate the current origin
	CG_CalcEntityLerpPositions( cent );

	// add automatic effects
	CG_EntityEffects( cent );

	switch ( cent->currentState.eType ) {
	default:
		CG_Error( "Bad entity type: %i\n", cent->currentState.eType );
		break;
	case ET_INVISIBLE:
	case ET_PUSH_TRIGGER:
	case ET_TELEPORT_TRIGGER:
		break;
	case ET_GENERAL:
		CG_General( cent );
		break;
	case ET_PLAYER:
		CG_Player( cent );
		break;
	case ET_ITEM:
		CG_Item( cent );
		break;
	case ET_MISSILE:
		CG_Missile( cent );
		break;
	case ET_MOVER:
		CG_Mover( cent );
		break;
	case ET_BEAM:
		CG_Beam( cent );
		break;
	case ET_PORTAL:
		CG_Portal( cent );
		break;
	case ET_SPEAKER:
		CG_Speaker( cent );
		break;
	case ET_GRAPPLE:
		CG_Grapple( cent );
		break;
	case ET_TEAM:
		CG_TeamBase( cent );
		break;
	}
}

/*
===============
CG_AddPacketEntities

===============
*/
void CG_AddPacketEntities( void ) {
	int					num;
	centity_t			*cent;
	playerState_t		*ps;

	// set cg.frameInterpolation
	if ( cg.nextSnap ) {
		int		delta;

		delta = (cg.nextSnap->serverTime - cg.snap->serverTime);
		if ( delta == 0 ) {
			cg.frameInterpolation = 0;
		} else {
			cg.frameInterpolation = (float)( cg.time - cg.snap->serverTime ) / delta;
		}
	} else {
		cg.frameInterpolation = 0;	// actually, it should never be used, because 
									// no entities should be marked as interpolating
	}

	// the auto-rotating items will all have the same axis
	cg.autoAngles[0] = 0;
	cg.autoAngles[1] = ( cg.time & 2047 ) * 360 / 2048.0;
	cg.autoAngles[2] = 0;

	cg.autoAnglesFast[0] = 0;
	cg.autoAnglesFast[1] = ( cg.time & 1023 ) * 360 / 1024.0f;
	cg.autoAnglesFast[2] = 0;

	AnglesToAxis( cg.autoAngles, cg.autoAxis );
	AnglesToAxis( cg.autoAnglesFast, cg.autoAxisFast );

	// generate and add the entity from the playerstate
	ps = &cg.predictedPlayerState;
	BG_PlayerStateToEntityState( ps, &cg.predictedPlayerEntity.currentState, qfalse );
	if ( !( ps->pm_flags & PMF_FOLLOW ) || ps->stats[STAT_HEALTH] <= GIB_HEALTH ) {
		CG_AddCEntity( &cg.predictedPlayerEntity );
	} else {
		CG_CalcEntityLerpPositions( &cg.predictedPlayerEntity );
		CG_EntityEffects( &cg.predictedPlayerEntity );
		CG_Player( &cg.predictedPlayerEntity );
	}

	// lerp the non-predicted value for lightning gun origins
	CG_CalcEntityLerpPositions( &cg_entities[ cg.snap->ps.clientNum ] );

	// add each entity sent over by the server
	for ( num = 0 ; num < cg.snap->numEntities ; num++ ) {
		cent = &cg_entities[ cg.snap->entities[ num ].number ];
		CG_AddCEntity( cent );
	}
}

