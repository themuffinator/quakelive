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
// cg_view.c -- setup all the parameters (position, angle, etc)
// for a 3D rendering
#include "cg_local.h"

static void CG_SetZoomState( qboolean zoomState );
static void CG_HandleZoomOutOnDeath( void );
static void CG_ResetViewAngleFilter( const vec3_t angles );
static void CG_FilterViewAngles( vec3_t angles );
static void CG_UpdateSpectatorCvar( void );

#define CG_VIEW_FILTER_TARGET_NONE	-1
#define CG_VIEW_FILTER_MAX_CVAR_SAMPLES	( CG_VIEW_FILTER_MAX_SAMPLES - 1 )
#define CG_BUFFERED_ANNOUNCER_COUNT	32
#define CG_BUFFERED_ANNOUNCER_DELAY	1500
#define CG_RETAIL_SELECTED_BOT_INFO_CONFIGSTRING	0x10

static int cg_viewFilterTargetKey = CG_VIEW_FILTER_TARGET_NONE;
static int cg_bufferedSoundHead;
static int cg_bufferedSoundTail;
static sfxHandle_t cg_bufferedSounds[CG_BUFFERED_ANNOUNCER_COUNT];
static int cg_bufferedSoundTimes[CG_BUFFERED_ANNOUNCER_COUNT];
static int cg_bufferedSoundDelays[CG_BUFFERED_ANNOUNCER_COUNT];


/*
=============
CG_GetTargetAspectDimensions

Returns qtrue when a valid r_aspectRatio preset is active, storing the
corresponding width/height pair.
=============
*/
static qboolean CG_GetTargetAspectDimensions( float *targetWidth, float *targetHeight ) {
	const char *ratioString;
	char	ratioBuffer[MAX_CVAR_VALUE_STRING];
	int ratio;

	trap_Cvar_VariableStringBuffer( "r_aspectRatio", ratioBuffer, sizeof( ratioBuffer ) );
	ratioString = ratioBuffer;
	ratio = atoi( ratioString );
	if ( ratio <= 0 ) {
		return qfalse;
	}

	switch ( ratio ) {
		case 1:
			*targetWidth = 16.0f;
			*targetHeight = 9.0f;
			return qtrue;
		case 2:
			*targetWidth = 16.0f;
			*targetHeight = 10.0f;
			return qtrue;
		case 3:
			*targetWidth = 5.0f;
			*targetHeight = 4.0f;
			return qtrue;
		default:
			return qfalse;
	}
}

/*
=============
CG_CalcHorPlusFov

Adjusts the provided horizontal FOV to match the requested r_aspectRatio
preset, mirroring Quake Live's Hor+ behaviour.
=============
*/
static float CG_CalcHorPlusFov( float baseFov ) {
	float baseWidth;
	float baseHeight;
	float targetWidth;
	float targetHeight;
	float x;
	float fovY;

	if ( !CG_GetTargetAspectDimensions( &targetWidth, &targetHeight ) ) {
		return baseFov;
	}

	baseWidth = 4.0f;
	baseHeight = 3.0f;
	x = baseWidth / tan( baseFov / 360.0f * M_PI );
	fovY = atan2( baseHeight, x );
	fovY = fovY * 360.0f / M_PI;

	x = targetHeight / tan( fovY / 360.0f * M_PI );
	return atan2( targetWidth, x ) * 360.0f / M_PI;
}

/*
=============
CG_CalcAspectAdjustedFovFromVertical

Matches the retail helper used by the smart third-person trace path. The input
FOV is treated as a 4:3 vertical FOV and expanded horizontally when an
`r_aspectRatio` preset is active.
=============
*/
static float CG_CalcAspectAdjustedFovFromVertical( float baseFov ) {
	float targetWidth;
	float targetHeight;
	float x;

	if ( !CG_GetTargetAspectDimensions( &targetWidth, &targetHeight ) ) {
		return baseFov;
	}

	x = targetHeight / tan( baseFov / 360.0f * M_PI );
	return atan2( targetWidth, x ) * 360.0f / M_PI;
}

/*
=============
CG_CalcSmartCameraTraceRange

Reconstructs the retail smart third-person trace radius from `cg_fov`,
`r_aspectRatio`, and `r_znear`.
=============
*/
static float CG_CalcSmartCameraTraceRange( void ) {
	char	zNearBuffer[MAX_CVAR_VALUE_STRING];
	float	zNear;
	float	x;
	float	fovY;
	float	fovX;

	trap_Cvar_VariableStringBuffer( "r_znear", zNearBuffer, sizeof( zNearBuffer ) );
	zNear = atof( zNearBuffer );

	x = 640.0f / tan( cg_fov.value / 360.0f * M_PI );
	fovY = atan2( 480.0f, x ) * 360.0f / M_PI;
	fovX = CG_CalcAspectAdjustedFovFromVertical( fovY );
	x = zNear / tan( ( 90.0f - fovX * 0.5f ) / 180.0f * M_PI );

	return sqrt( x * x + zNear * zNear );
}


/*
=============================================================================

  MODEL TESTING

The viewthing and gun positioning tools from Q2 have been integrated and
enhanced into a single model testing facility.

Model viewing can begin with either "testmodel <modelname>" or "testgun <modelname>".

The names must be the full pathname after the basedir, like 
"models/weapons/v_launch/tris.md3" or "players/male/tris.md3"

Testmodel will create a fake entity 100 units in front of the current view
position, directly facing the viewer.  It will remain immobile, so you can
move around it to view it from different angles.

Testgun will cause the model to follow the player around and supress the real
view weapon model.  The default frame 0 of most guns is completely off screen,
so you will probably have to cycle a couple frames to see it.

"nextframe", "prevframe", "nextskin", and "prevskin" commands will change the
frame or skin of the testmodel.  These are bound to F5, F6, F7, and F8 in
q3default.cfg.

If a gun is being tested, the "gun_x", "gun_y", and "gun_z" variables will let
you adjust the positioning.

Note that none of the model testing features update while the game is paused, so
it may be convenient to test with deathmatch set to 1 so that bringing down the
console doesn't pause the game.

=============================================================================
*/

/*
=================
CG_TestModel_f

Creates an entity in front of the current position, which
can then be moved around
=================
*/
void CG_TestModel_f (void) {
	vec3_t		angles;

	memset( &cg.testModelEntity, 0, sizeof(cg.testModelEntity) );
	if ( trap_Argc() < 2 ) {
		return;
	}

	Q_strncpyz (cg.testModelName, CG_Argv( 1 ), MAX_QPATH );
	cg.testModelEntity.hModel = trap_R_RegisterModel( cg.testModelName );

	if ( trap_Argc() == 3 ) {
		cg.testModelEntity.backlerp = atof( CG_Argv( 2 ) );
		cg.testModelEntity.frame = 1;
		cg.testModelEntity.oldframe = 0;
	}
	if (! cg.testModelEntity.hModel ) {
		CG_Printf( "Can't register model\n" );
		return;
	}

	VectorMA( cg.refdef.vieworg, 100, cg.refdef.viewaxis[0], cg.testModelEntity.origin );

	angles[PITCH] = 0;
	angles[YAW] = 180 + cg.refdefViewAngles[1];
	angles[ROLL] = 0;

	AnglesToAxis( angles, cg.testModelEntity.axis );
	cg.testGun = qfalse;
}

/*
=================
CG_TestGun_f

Replaces the current view weapon with the given model
=================
*/
void CG_TestGun_f (void) {
	CG_TestModel_f();
	cg.testGun = qtrue;
	cg.testModelEntity.renderfx = RF_MINLIGHT | RF_DEPTHHACK | RF_FIRST_PERSON;
}


void CG_TestModelNextFrame_f (void) {
	cg.testModelEntity.frame++;
	CG_Printf( "frame %i\n", cg.testModelEntity.frame );
}

void CG_TestModelPrevFrame_f (void) {
	cg.testModelEntity.frame--;
	if ( cg.testModelEntity.frame < 0 ) {
		cg.testModelEntity.frame = 0;
	}
	CG_Printf( "frame %i\n", cg.testModelEntity.frame );
}

void CG_TestModelNextSkin_f (void) {
	cg.testModelEntity.skinNum++;
	CG_Printf( "skin %i\n", cg.testModelEntity.skinNum );
}

void CG_TestModelPrevSkin_f (void) {
	cg.testModelEntity.skinNum--;
	if ( cg.testModelEntity.skinNum < 0 ) {
		cg.testModelEntity.skinNum = 0;
	}
	CG_Printf( "skin %i\n", cg.testModelEntity.skinNum );
}

static void CG_AddTestModel (void) {
	int		i;

	// re-register the model, because the level may have changed
	cg.testModelEntity.hModel = trap_R_RegisterModel( cg.testModelName );
	if (! cg.testModelEntity.hModel ) {
		CG_Printf ("Can't register model\n");
		return;
	}

	// if testing a gun, set the origin reletive to the view origin
	if ( cg.testGun ) {
		VectorCopy( cg.refdef.vieworg, cg.testModelEntity.origin );
		VectorCopy( cg.refdef.viewaxis[0], cg.testModelEntity.axis[0] );
		VectorCopy( cg.refdef.viewaxis[1], cg.testModelEntity.axis[1] );
		VectorCopy( cg.refdef.viewaxis[2], cg.testModelEntity.axis[2] );

		// allow the position to be adjusted
		for (i=0 ; i<3 ; i++) {
			cg.testModelEntity.origin[i] += cg.refdef.viewaxis[0][i] * cg_gun_x.value;
			cg.testModelEntity.origin[i] += cg.refdef.viewaxis[1][i] * cg_gun_y.value;
			cg.testModelEntity.origin[i] += cg.refdef.viewaxis[2][i] * cg_gun_z.value;
		}
	}

	trap_R_AddRefEntityToScene( &cg.testModelEntity );
}



//============================================================================


/*
=================
CG_CalcVrect

Sets the coordinates of the rendered window
=================
*/
static void CG_CalcVrect (void) {
	int		size;

	// the intermission should allways be full screen
	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		size = 100;
	} else {
		// bound normal viewsize
		if (cg_viewsize.integer < 30) {
			trap_Cvar_Set ("cg_viewsize","30");
			size = 30;
		} else if (cg_viewsize.integer > 100) {
			trap_Cvar_Set ("cg_viewsize","100");
			size = 100;
		} else {
			size = cg_viewsize.integer;
		}

	}
	cg.refdef.width = cgs.glconfig.vidWidth*size/100;
	cg.refdef.width &= ~1;

	cg.refdef.height = cgs.glconfig.vidHeight*size/100;
	cg.refdef.height &= ~1;

	cg.refdef.x = (cgs.glconfig.vidWidth - cg.refdef.width)/2;
	cg.refdef.y = (cgs.glconfig.vidHeight - cg.refdef.height)/2;
}

//==============================================================================


/*
===============
CG_OffsetThirdPersonViewSpecial

Matches the retail cg_thirdPerson == 2 camera helper, which applies the
configured yaw and pitch directly before offsetting straight back along the
resulting forward vector.
===============
*/
static void CG_OffsetThirdPersonViewSpecial( void ) {
	vec3_t		forward;

	cg.refdef.vieworg[2] += cg.predictedPlayerState.viewheight;

	if ( cg_thirdPersonAngle.value != 0.0f ) {
		cg.refdefViewAngles[YAW] += cg_thirdPersonAngle.value;
	}

	if ( cg_thirdPersonPitch.value != -1.0f ) {
		cg.refdefViewAngles[PITCH] = cg_thirdPersonPitch.value;
	}

	AngleVectors( cg.refdefViewAngles, forward, NULL, NULL );
	VectorMA( cg.refdef.vieworg, -cg_thirdPersonRange.value, forward, cg.refdef.vieworg );
}

/*
===============
CG_OffsetThirdPersonView

===============
*/
#define	FOCUS_DISTANCE	512
#define	THIRD_PERSON_PITCH_MIN	-45.0f
#define	THIRD_PERSON_PITCH_MAX	45.0f
static void CG_OffsetThirdPersonView( void ) {
	vec3_t		forward, right, up;
	vec3_t		view;
	vec3_t		smartStart;
	vec3_t		smartMins;
	vec3_t		smartMaxs;
	vec3_t		focusAngles;
	trace_t		trace;
	static vec3_t	mins = { -4, -4, -4 };
	static vec3_t	maxs = { 4, 4, 4 };
	vec3_t		focusPoint;
	float		focusDist;
	float		forwardScale, sideScale;
	float		smartTraceRange;
	float		zNear;
	char		zNearBuffer[MAX_CVAR_VALUE_STRING];
	qboolean	useSimpleTrace;

	if ( cg_thirdPerson.integer == 2 ) {
		CG_OffsetThirdPersonViewSpecial();
		return;
	}

	cg.refdef.vieworg[2] += cg.predictedPlayerState.viewheight;

	VectorCopy( cg.refdefViewAngles, focusAngles );

	// if dead, look at killer
	if ( cg.predictedPlayerState.stats[STAT_HEALTH] <= 0 ) {
		focusAngles[YAW] = cg.predictedPlayerState.stats[STAT_DEAD_YAW];
		cg.refdefViewAngles[YAW] = cg.predictedPlayerState.stats[STAT_DEAD_YAW];
		CG_HandleZoomOutOnDeath();

		if ( focusAngles[PITCH] > 45.0f ) {
			focusAngles[PITCH] = 45.0f;		// don't go too far overhead
		}
	}
	AngleVectors( focusAngles, forward, NULL, NULL );

	VectorMA( cg.refdef.vieworg, FOCUS_DISTANCE, forward, focusPoint );

	VectorCopy( cg.refdef.vieworg, view );

	view[2] += 8;

	cg.refdefViewAngles[PITCH] *= 0.5;

	AngleVectors( cg.refdefViewAngles, forward, right, up );

	forwardScale = cos( cg_thirdPersonAngle.value / 180 * M_PI );
	sideScale = sin( cg_thirdPersonAngle.value / 180 * M_PI );
	VectorMA( view, -cg_thirdPersonRange.value * forwardScale, forward, view );
	VectorMA( view, -cg_thirdPersonRange.value * sideScale, right, view );

	// trace a ray from the origin to the viewpoint to make sure the view isn't
	// in a solid block.  Use an 8 by 8 block to prevent the view from near clipping anything

	if ( !cg_cameraMode.integer ) {
		useSimpleTrace = qfalse;

		if ( ( cg_thirdPerson.integer == 0 || cg_cameraThirdPersonSmartMode.integer == 0 ) &&
			cg_cameraSmartMode.integer == 0 &&
			( cg.predictedPlayerState.pm_type == PM_INTERMISSION ||
			cg.predictedPlayerState.stats[STAT_HEALTH] > 0 ) ) {
			useSimpleTrace = qtrue;
		}

		if ( useSimpleTrace ) {
			CG_Trace( &trace, cg.refdef.vieworg, mins, maxs, view, cg.predictedPlayerState.clientNum, MASK_SOLID );

			if ( trace.fraction != 1.0f ) {
				VectorCopy( trace.endpos, view );
				view[2] += ( 1.0f - trace.fraction ) * 32.0f;
				// try another trace to this position, because a tunnel may have the ceiling
				// close enogh that this is poking out

				CG_Trace( &trace, cg.refdef.vieworg, mins, maxs, view, cg.predictedPlayerState.clientNum, MASK_SOLID );
				VectorCopy( trace.endpos, view );
			}
		} else {
			smartTraceRange = CG_CalcSmartCameraTraceRange();
			VectorSet( smartMins, -smartTraceRange, -smartTraceRange, -smartTraceRange );
			VectorSet( smartMaxs, smartTraceRange, smartTraceRange, smartTraceRange );
			VectorMA( view, cg_thirdPersonRange.value, forward, smartStart );

			CG_Trace( &trace, smartStart, smartMins, smartMaxs, view, cg.predictedPlayerState.clientNum, MASK_SOLID );

			if ( trace.fraction != 1.0f ) {
				trap_Cvar_VariableStringBuffer( "r_znear", zNearBuffer, sizeof( zNearBuffer ) );
				zNear = atof( zNearBuffer );
				VectorMA( trace.endpos, zNear, forward, view );
				view[2] += ( 1.0f - trace.fraction ) * 32.0f;

				CG_Trace( &trace, smartStart, smartMins, smartMaxs, view, cg.predictedPlayerState.clientNum, MASK_SOLID );
				if ( trace.fraction != 1.0f ) {
					VectorMA( trace.endpos, zNear, forward, view );
				}
			}
		}
	}


	VectorCopy( view, cg.refdef.vieworg );

	// select pitch to look at focus point from vieword
	VectorSubtract( focusPoint, cg.refdef.vieworg, focusPoint );
	focusDist = sqrt( focusPoint[0] * focusPoint[0] + focusPoint[1] * focusPoint[1] );
	if ( focusDist < 1 ) {
		focusDist = 1;	// should never happen
	}
	cg.refdefViewAngles[PITCH] = -180 / M_PI * atan2( focusPoint[2], focusDist );
	cg.refdefViewAngles[YAW] -= cg_thirdPersonAngle.value;
}


// this causes a compiler bug on mac MrC compiler
static void CG_StepOffset( void ) {
	int		timeDelta;
	
	// smooth out stair climbing
	timeDelta = cg.time - cg.stepTime;
	if ( timeDelta < STEP_TIME ) {
		cg.refdef.vieworg[2] -= cg.stepChange 
			* (STEP_TIME - timeDelta) / STEP_TIME;
	}
}

/*
===============
CG_OffsetFirstPersonView

===============
*/
static void CG_OffsetFirstPersonView( void ) {
	float			*origin;
	float			*angles;
	float			bob;
	float			ratio;
	float			delta;
	float			speed;
	float			f;
	float			kickScale;
	float			bobScale;
	vec3_t			predictedVelocity;
	int				timeDelta;
	
	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		CG_HandleZoomOutOnDeath();
		return;
	}

	origin = cg.refdef.vieworg;
	angles = cg.refdefViewAngles;
	kickScale = cg.kickScale;
	bobScale = cg.bobScale;

	// if dead, fix the angle and don't add any kick
	if ( cg.snap->ps.stats[STAT_HEALTH] <= 0 ) {
		angles[ROLL] = 40;
		angles[PITCH] = -15;
		angles[YAW] = cg.snap->ps.stats[STAT_DEAD_YAW];
		origin[2] += cg.predictedPlayerState.viewheight;
		CG_HandleZoomOutOnDeath();
		return;
	}

	// add angles based on weapon kick
	VectorAdd (angles, cg.kick_angles, angles);

	// add angles based on damage kick
	if ( cg.damageTime ) {
		ratio = cg.time - cg.damageTime;
		if ( ratio < DAMAGE_DEFLECT_TIME ) {
			ratio /= DAMAGE_DEFLECT_TIME;
			angles[PITCH] += ratio * cg.v_dmg_pitch * kickScale;
			angles[ROLL] += ratio * cg.v_dmg_roll * kickScale;
		} else {
			ratio = 1.0 - ( ratio - DAMAGE_DEFLECT_TIME ) / DAMAGE_RETURN_TIME;
			if ( ratio > 0 ) {
				angles[PITCH] += ratio * cg.v_dmg_pitch * kickScale;
				angles[ROLL] += ratio * cg.v_dmg_roll * kickScale;
			}
		}
	}

	// add pitch based on fall kick
#if 0
	ratio = ( cg.time - cg.landTime) / FALL_TIME;
	if (ratio < 0)
		ratio = 0;
	angles[PITCH] += ratio * cg.fall_value;
#endif

	// add angles based on velocity
	VectorCopy( cg.predictedPlayerState.velocity, predictedVelocity );

	delta = DotProduct ( predictedVelocity, cg.refdef.viewaxis[0]);
	angles[PITCH] += delta * cg_runpitch.value * bobScale;
	
	delta = DotProduct ( predictedVelocity, cg.refdef.viewaxis[1]);
	angles[ROLL] -= delta * cg_runroll.value * bobScale;

	// add angles based on bob

	// make sure the bob is visible even at low speeds
	speed = cg.xyspeed > 200 ? cg.xyspeed : 200;

	delta = cg.bobfracsin * cg_bobpitch.value * speed * bobScale;
	if (cg.predictedPlayerState.pm_flags & PMF_DUCKED)
		delta *= 3;		// crouching
	angles[PITCH] += delta;
	delta = cg.bobfracsin * cg_bobroll.value * speed * bobScale;
	if (cg.predictedPlayerState.pm_flags & PMF_DUCKED)
		delta *= 3;		// crouching accentuates roll
	if (cg.bobcycle & 1)
		delta = -delta;
	angles[ROLL] += delta;

//===================================

	// add view height
	origin[2] += cg.predictedPlayerState.viewheight;

	// smooth out duck height changes
	timeDelta = cg.time - cg.duckTime;
	if ( timeDelta < DUCK_TIME) {
		cg.refdef.vieworg[2] -= cg.duckChange 
			* (DUCK_TIME - timeDelta) / DUCK_TIME;
	}

	// add bob height
	bob = cg.bobfracsin * cg.xyspeed * cg_bobup.value * bobScale;
	if (bob > 6) {
		bob = 6;
	}

	origin[2] += bob;


	// add fall height
	delta = cg.time - cg.landTime;
	if ( delta < LAND_DEFLECT_TIME ) {
		f = delta / LAND_DEFLECT_TIME;
		cg.refdef.vieworg[2] += cg.landChange * f;
	} else if ( delta < LAND_DEFLECT_TIME + LAND_RETURN_TIME ) {
		delta -= LAND_DEFLECT_TIME;
		f = 1.0 - ( delta / LAND_RETURN_TIME );
		cg.refdef.vieworg[2] += cg.landChange * f;
	}

	// add step offset
	CG_StepOffset();

	// add kick offset

	VectorAdd (origin, cg.kick_origin, origin);

	// pivot the eye based on a neck length
#if 0
	{
#define	NECK_LENGTH		8
	vec3_t			forward, up;
 
	cg.refdef.vieworg[2] -= NECK_LENGTH;
	AngleVectors( cg.refdefViewAngles, forward, NULL, up );
	VectorMA( cg.refdef.vieworg, 3, forward, cg.refdef.vieworg );
	VectorMA( cg.refdef.vieworg, NECK_LENGTH, up, cg.refdef.vieworg );
	}
#endif
}

//======================================================================

/*
=============
CG_SetZoomState

Updates the zoom state if it changes.
=============
*/
static void CG_SetZoomState( qboolean zoomState ) {
	if ( cg.zoomed == zoomState ) {
		return;
	}

	cg.zoomed = zoomState;
	cg.zoomTime = cg.time;
}

/*
=============
CG_ZoomDown_f

Starts or toggles zoom mode based on cg_zoomToggle.
=============
*/
void CG_ZoomDown_f( void ) {
	int pmType = cg.snap ? cg.snap->ps.pm_type : cg.predictedPlayerState.pm_type;

	if ( pmType == PM_DEAD || pmType == PM_FREEZE ) {
		return;
	}

	if ( cg.zoomToggle ) {
		CG_SetZoomState( cg.zoomed ? qfalse : qtrue );
		return;
	}

	CG_SetZoomState( qtrue );
}

/*
=============
CG_ZoomUp_f

Ends zoom mode for hold-to-zoom bindings.
=============
*/
void CG_ZoomUp_f( void ) {
	if ( cg.zoomToggle ) {
		return;
	}

	CG_SetZoomState( qfalse );
}

/*
=============
CG_HandleZoomOutOnDeath

Releases the zoom when required by cg_zoomOutOnDeath.
=============
*/
static void CG_HandleZoomOutOnDeath( void ) {
	if ( !cg.zoomOutOnDeath ) {
		return;
	}

	if ( !cg.zoomed ) {
		return;
	}

	CG_SetZoomState( qfalse );
}


/*
=============
CG_ResetViewAngleFilter

Clears the view smoothing buffer using the supplied angles as a baseline.
=============
*/
static void CG_ResetViewAngleFilter( const vec3_t angles ) {
	cg.viewFilter.count = 0;
	cg.viewFilter.index = 0;
	cg.viewFilter.lastYaw = angles[YAW];
	cg.viewFilter.lastPitch = angles[PITCH];
	memset( cg.viewFilter.yawSamples, 0, sizeof( cg.viewFilter.yawSamples ) );
	memset( cg.viewFilter.pitchSamples, 0, sizeof( cg.viewFilter.pitchSamples ) );
}

/*
=============
CG_ViewFilterAverage

Returns the average stored in the retail view filter sample buffer.
=============
*/
static float CG_ViewFilterAverage( const float *samples, int count, int index ) {
	float sum = 0.0f;
	int i;
	int sampleIndex = index;

	if ( count <= 0 ) {
		return 0.0f;
	}

	for ( i = 0; i < count; i++ ) {
		sum += samples[sampleIndex];
		sampleIndex--;
		if ( sampleIndex < 0 ) {
			sampleIndex = CG_VIEW_FILTER_MAX_SAMPLES - 1;
		}
	}

	return sum / (float)count;
}

/*
=============
CG_GetViewFilterTargetKey

Returns the current spectator-camera target key so the retail smoothing ring
can be reset when the followed view changes.
=============
*/
static int CG_GetViewFilterTargetKey( void ) {
	if ( !cg.snap || !CG_IsSpectatorCamera() ) {
		return CG_VIEW_FILTER_TARGET_NONE;
	}

	return cg.snap->ps.clientNum;
}

/*
=============
CG_CalcZoomSensitivityScale

Returns the retail zoom-sensitivity ratio derived from the current zoomed
vertical FOV versus the unzoomed baseline vertical FOV for the active view.
=============
*/
static float CG_CalcZoomSensitivityScale( float currentFovY, float baseFovX ) {
	float x;
	float baseFovY;

	if ( currentFovY <= 0.0f || cg.refdef.width <= 0 || cg.refdef.height <= 0 ) {
		return 1.0f;
	}

	if ( baseFovX < 1.0f ) {
		baseFovX = 1.0f;
	} else if ( baseFovX > 130.0f ) {
		baseFovX = 130.0f;
	}

	x = cg.refdef.width / tan( baseFovX / 360.0f * M_PI );
	baseFovY = atan2( cg.refdef.height, x );
	baseFovY = baseFovY * 360.0f / M_PI;
	if ( baseFovY <= 0.0f ) {
		return 1.0f;
	}

	return currentFovY / baseFovY;
}

/*
=============
CG_FilterViewAngles

Applies HLIL-style smoothing to the spectator camera view angles.
=============
*/
static void CG_FilterViewAngles( vec3_t angles ) {
	int sampleLimit;
	int targetKey;
	int sampleIndex;
	int i;
	float averageYaw;
	float averagePitch;
	float yawDelta;
	float yawOffset;

	sampleLimit = cg_filter_angles.integer;
	if ( sampleLimit < 0 ) {
		trap_Cvar_Set( "cg_filter_angles", "0" );
		cg_filter_angles.integer = 0;
		cg_filter_angles.value = 0.0f;
		sampleLimit = 0;
	}
	if ( sampleLimit > CG_VIEW_FILTER_MAX_CVAR_SAMPLES ) {
		trap_Cvar_Set( "cg_filter_angles", va( "%d", CG_VIEW_FILTER_MAX_CVAR_SAMPLES ) );
		cg_filter_angles.integer = CG_VIEW_FILTER_MAX_CVAR_SAMPLES;
		cg_filter_angles.value = (float)CG_VIEW_FILTER_MAX_CVAR_SAMPLES;
		sampleLimit = CG_VIEW_FILTER_MAX_CVAR_SAMPLES;
	}

	targetKey = CG_GetViewFilterTargetKey();
	if ( sampleLimit == 0 || targetKey == CG_VIEW_FILTER_TARGET_NONE ) {
		cg_viewFilterTargetKey = targetKey;
		CG_ResetViewAngleFilter( angles );
		return;
	}

	if ( cg_viewFilterTargetKey != targetKey ) {
		cg_viewFilterTargetKey = targetKey;
		CG_ResetViewAngleFilter( angles );
	}

	if ( cg.viewFilter.count == 0 ) {
		CG_ResetViewAngleFilter( angles );
	}

	if ( cg.viewFilter.index >= CG_VIEW_FILTER_MAX_SAMPLES ) {
		cg.viewFilter.index = 0;
	}
	if ( cg.viewFilter.count > sampleLimit ) {
		cg.viewFilter.count = sampleLimit;
	}

	yawDelta = angles[YAW] - cg.viewFilter.lastYaw;
	if ( fabs( yawDelta ) > 350.0f ) {
		yawOffset = yawDelta >= 0.0f ? 360.0f : -360.0f;
		for ( i = 1; i < cg.viewFilter.count; i++ ) {
			sampleIndex = cg.viewFilter.index - i;
			if ( sampleIndex < 0 ) {
				sampleIndex += CG_VIEW_FILTER_MAX_SAMPLES;
			}
			cg.viewFilter.yawSamples[sampleIndex] += yawOffset;
		}
	}

	cg.viewFilter.lastYaw = angles[YAW];
	cg.viewFilter.lastPitch = angles[PITCH];
	cg.viewFilter.yawSamples[cg.viewFilter.index] = angles[YAW];
	cg.viewFilter.pitchSamples[cg.viewFilter.index] = angles[PITCH];
	if ( cg.viewFilter.count < sampleLimit ) {
		cg.viewFilter.count++;
	}

	averageYaw = CG_ViewFilterAverage( cg.viewFilter.yawSamples, cg.viewFilter.count, cg.viewFilter.index );
	averagePitch = CG_ViewFilterAverage( cg.viewFilter.pitchSamples, cg.viewFilter.count, cg.viewFilter.index );

	angles[YAW] = averageYaw;
	angles[PITCH] = averagePitch;
	cg.viewFilter.index = ( cg.viewFilter.index + 1 ) % CG_VIEW_FILTER_MAX_SAMPLES;
}

/*
=============
CG_ClearBufferedSounds

Clears the local announcer queue, matching the retail buffered-sound reset
behaviour when the queue is disabled or invalidated.
=============
*/
static void CG_ClearBufferedSounds( void ) {
	cg_bufferedSoundHead = 0;
	cg_bufferedSoundTail = 0;
	memset( cg_bufferedSounds, 0, sizeof( cg_bufferedSounds ) );
	memset( cg_bufferedSoundTimes, 0, sizeof( cg_bufferedSoundTimes ) );
	memset( cg_bufferedSoundDelays, 0, sizeof( cg_bufferedSoundDelays ) );
}

/*
=============
CG_ClearBufferedAnnouncements

Exposes the retail buffered-announcer reset path outside cg_view.c.
=============
*/
void CG_ClearBufferedAnnouncements( void ) {
	CG_ClearBufferedSounds();
}

/*
=============
CG_UpdateSpectatorCvar

Keeps the cg_spectating ROM cvar in sync with the current spectator state.
=============
*/
static void CG_UpdateSpectatorCvar( void ) {
	qboolean spectating = (qboolean)( cg.snap && cg.snap->ps.pm_type == PM_SPECTATOR );
	int desired = spectating ? 1 : 0;

	if ( cg_spectating.integer == desired ) {
		return;
	}

	trap_Cvar_Set( "cg_spectating", desired ? "1" : "0" );
	cg_spectating.integer = desired;
	cg_spectating.value = (float)desired;
}

/*
====================
CG_CalcFov

Fixed fov at intermissions, otherwise account for fov variable and zooms.
====================
*/
#define	WAVE_AMPLITUDE	1
#define	WAVE_FREQUENCY	0.4

static int CG_CalcFov( void ) {
	float	x;
	float	phase;
	float	v;
	int		contents;
	float	fov_x, fov_y;
	float	zoomFov;
	float	f;
	float	baseFovX = 90.0f;
	int		inwater;
	qboolean zoomScaling;

	if ( cg.predictedPlayerState.pm_type == PM_INTERMISSION ) {
		// if in intermission, use a fixed value
		fov_x = 90;
	} else {
		// user selectable
		if ( cgs.dmflags & DF_FIXED_FOV ) {
			// dmflag to prevent wide fov for all clients
			fov_x = 90;
		} else {
			fov_x = cg_fov.value;
			if ( fov_x < 1 ) {
				fov_x = 1;
			} else if ( fov_x > 130 ) {
				fov_x = 130;
			}
		}
		baseFovX = fov_x;

		// account for zooms
		zoomFov = cg_zoomFov.value;
		if ( zoomFov < 1 ) {
			zoomFov = 1;
		} else if ( zoomFov > 130 ) {
			zoomFov = 130;
		}
		zoomScaling = (qboolean)( cg_zoomScaling.integer != 0 );

		if ( cg.zoomed ) {
			if ( !zoomScaling ) {
				fov_x = zoomFov;
			} else {
				f = ( cg.time - cg.zoomTime ) / (float)ZOOM_TIME;
				if ( f > 1.0 ) {
					fov_x = zoomFov;
				} else {
					fov_x = fov_x + f * ( zoomFov - fov_x );
				}
			}
		} else {
			if ( !zoomScaling ) {
				fov_x = baseFovX;
			} else {
				f = ( cg.time - cg.zoomTime ) / (float)ZOOM_TIME;
				if ( f > 1.0 ) {
					fov_x = baseFovX;
				} else {
					fov_x = zoomFov + f * ( baseFovX - zoomFov );
				}
			}
		}
	}

	fov_x = CG_CalcHorPlusFov( fov_x );

	x = cg.refdef.width / tan( fov_x / 360 * M_PI );
	fov_y = atan2( cg.refdef.height, x );
	fov_y = fov_y * 360 / M_PI;

	// warp if underwater
	contents = CG_PointContents( cg.refdef.vieworg, -1 );
	if ( contents & ( CONTENTS_WATER | CONTENTS_SLIME | CONTENTS_LAVA ) ){
		phase = cg.time / 1000.0 * WAVE_FREQUENCY * M_PI * 2;
		v = WAVE_AMPLITUDE * sin( phase );
		fov_x += v;
		fov_y -= v;
		inwater = qtrue;
	}
	else {
		inwater = qfalse;
	}


	// set it
	cg.refdef.fov_x = fov_x;
	cg.refdef.fov_y = fov_y;

	if ( !cg.zoomed ) {
		cg.zoomSensitivity = 1.0f;
	} else if ( cg_zoomSensitivity.value > 0.0f ) {
		cg.zoomSensitivity = CG_CalcZoomSensitivityScale( cg.refdef.fov_y, baseFovX ) * cg_zoomSensitivity.value;
	} else {
		cg.zoomSensitivity = cg.refdef.fov_y / 75.0;
	}

	return inwater;
}

static int CG_CalcViewValues( void ) {
	playerState_t	*ps;

	memset( &cg.refdef, 0, sizeof( cg.refdef ) );

	// strings for in game rendering
	// Q_strncpyz( cg.refdef.text[0], "Park Ranger", sizeof(cg.refdef.text[0]) );
	// Q_strncpyz( cg.refdef.text[1], "19", sizeof(cg.refdef.text[1]) );

	// calculate size of 3D view
	CG_CalcVrect();

	ps = &cg.predictedPlayerState;
/*
	if (cg.cameraMode) {
		vec3_t origin, angles;
		if (trap_getCameraInfo(cg.time, &origin, &angles)) {
			VectorCopy(origin, cg.refdef.vieworg);
			angles[ROLL] = 0;
			VectorCopy(angles, cg.refdefViewAngles);
			AnglesToAxis( cg.refdefViewAngles, cg.refdef.viewaxis );
			return CG_CalcFov();
		} else {
			cg.cameraMode = qfalse;
		}
	}
*/
	// intermission view
	if ( ps->pm_type == PM_INTERMISSION ) {
		VectorCopy( ps->origin, cg.refdef.vieworg );
		VectorCopy( ps->viewangles, cg.refdefViewAngles );
		AnglesToAxis( cg.refdefViewAngles, cg.refdef.viewaxis );
		return CG_CalcFov();
	}

	cg.bobcycle = ( ps->bobCycle & 128 ) >> 7;
	cg.bobfracsin = fabs( sin( ( ps->bobCycle & 127 ) / 127.0 * M_PI ) );
	cg.xyspeed = sqrt( ps->velocity[0] * ps->velocity[0] +
		ps->velocity[1] * ps->velocity[1] );


	VectorCopy( ps->origin, cg.refdef.vieworg );
	VectorCopy( ps->viewangles, cg.refdefViewAngles );

	if (cg_cameraOrbit.integer) {
		if (cg.time > cg.nextOrbitTime) {
			cg.nextOrbitTime = cg.time + cg_cameraOrbitDelay.integer;
			cg_thirdPersonAngle.value += cg_cameraOrbit.value;
		}
	}
	// add error decay
	if ( cg_errorDecay.value > 0 ) {
		int		t;
		float	f;

		t = cg.time - cg.predictedErrorTime;
		f = ( cg_errorDecay.value - t ) / cg_errorDecay.value;
		if ( f > 0 && f < 1 ) {
			VectorMA( cg.refdef.vieworg, f, cg.predictedError, cg.refdef.vieworg );
		} else {
			cg.predictedErrorTime = 0;
		}
	}

	if ( cg.renderingThirdPerson ) {
		// back away from character
		CG_OffsetThirdPersonView();
	} else {
		// offset for local bobbing and kicks
		CG_OffsetFirstPersonView();
	}

	CG_FilterViewAngles( cg.refdefViewAngles );

	// position eye reletive to origin
	AnglesToAxis( cg.refdefViewAngles, cg.refdef.viewaxis );


	if ( cg.hyperspace ) {
		cg.refdef.rdflags |= RDF_NOWORLDMODEL | RDF_HYPERSPACE;
	}

	// field of view
	return CG_CalcFov();
}


/*
=====================
CG_PowerupTimerSounds
=====================
*/
static void CG_PowerupTimerSounds( void ) {
	int		i;
	int		t;

	// powerup timers going away
	for ( i = 0 ; i < MAX_POWERUPS ; i++ ) {
		t = cg.snap->ps.powerups[i];
		if ( t <= cg.time ) {
			continue;
		}
		if ( t - cg.time >= POWERUP_BLINKS * POWERUP_BLINK_TIME ) {
			continue;
		}
		if ( ( t - cg.time ) / POWERUP_BLINK_TIME != ( t - cg.oldTime ) / POWERUP_BLINK_TIME ) {
			trap_S_StartSound( NULL, cg.snap->ps.clientNum, CHAN_ITEM, cgs.media.wearOffSound );
		}
	}
}

/*
=====================
CG_AddBufferedSound
=====================
*/
void CG_AddBufferedSound( sfxHandle_t sfx ) {
	if ( !sfx ) {
		return;
	}
	if ( cgs.announcerProfile == ANNOUNCER_PROFILE_DISABLED ) {
		return;
	}

	cg_bufferedSounds[cg_bufferedSoundHead] = sfx;
	cg_bufferedSoundDelays[cg_bufferedSoundHead] = CG_BUFFERED_ANNOUNCER_DELAY;
	if ( cg_bufferedSoundTimes[cg_bufferedSoundHead] == 0 ) {
		cg_bufferedSoundTimes[cg_bufferedSoundHead] = cg.time;
	}

	cg_bufferedSoundHead = ( cg_bufferedSoundHead + 1 ) % CG_BUFFERED_ANNOUNCER_COUNT;
	if ( cg_bufferedSoundHead == cg_bufferedSoundTail ) {
		cg_bufferedSoundTail = ( cg_bufferedSoundTail + 1 ) % CG_BUFFERED_ANNOUNCER_COUNT;
	}
}

/*
=====================
CG_PlayBufferedSounds
=====================
*/
static void CG_PlayBufferedSounds( void ) {
	int nextIndex;
	sfxHandle_t sfx;

	if ( cgs.announcerProfile == ANNOUNCER_PROFILE_DISABLED ) {
		CG_ClearBufferedSounds();
		return;
	}

	if ( cg_bufferedSoundTimes[cg_bufferedSoundTail] > cg.time ) {
		return;
	}

	sfx = cg_bufferedSounds[cg_bufferedSoundTail];
	if ( !sfx || cg_bufferedSoundTail == cg_bufferedSoundHead ) {
		return;
	}

	nextIndex = ( cg_bufferedSoundTail + 1 ) % CG_BUFFERED_ANNOUNCER_COUNT;

	trap_S_StartLocalSound( sfx, CHAN_ANNOUNCER );

	cg_bufferedSoundTimes[nextIndex] = cg_bufferedSoundDelays[cg_bufferedSoundTail] + cg.time;
	cg_bufferedSounds[cg_bufferedSoundTail] = 0;
	cg_bufferedSoundTimes[cg_bufferedSoundTail] = 0;
	cg_bufferedSoundDelays[cg_bufferedSoundTail] = 0;
	cg_bufferedSoundTail = nextIndex;
}

//=========================================================================

/*
=================
CG_RunPendingFollowKiller

Sends the deferred retail follow-killer command once the obituary hold expires.
=================
*/
static void CG_RunPendingFollowKiller( void ) {
	if ( cg.pendingFollowKillerClient < 0 || cg.time < cg.pendingFollowKillerTime ) {
		return;
	}

	if ( cg.snap && ( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		trap_SendClientCommand( va( "follow %d", cg.pendingFollowKillerClient ) );
	}

	cg.pendingFollowKillerClient = -1;
	cg.pendingFollowKillerTime = 0;
}

/*
====================
CG_DrawBotAIDebugInfo
====================
*/
static void CG_DrawBotAIDebugInfo( void ) {
	static const char *const cgBotDebugKeys[] = {
		"e", "ed",
		"tg", "tgd",
		"sg", "sgd",
		"ainode", "ltg",
		"ban", "gan",
		"bh", "ba",
		"sk", "eh"
	};
	static const char *const cgBotDebugLabels[] = {
		"Enemy   = ", "Dist    = ",
		"LTG     = ", "Dist    = ",
		"NBG     = ", "Dist    = ",
		"AI Node = ", "LTGType = ",
		"Area#   = ", "G_Area# = ",
		"Health  = ", "Armor   = ",
		"Skill   = ", "Hear_E  = "
	};
	const char	*botInfo;
	char		values[ARRAY_LEN( cgBotDebugKeys )][15];
	char		line[64];
	float		y;
	int			i;

	if ( !cg.snap || cg.snap->ps.stats[STAT_HEALTH] <= 0 ) {
		return;
	}

	botInfo = CG_ConfigString( CG_RETAIL_SELECTED_BOT_INFO_CONFIGSTRING );
	if ( !botInfo[0] || Q_strncmp( botInfo, "e\\", 2 ) ) {
		return;
	}

	for ( i = 0; i < ARRAY_LEN( cgBotDebugKeys ); i++ ) {
		Q_strncpyz( values[i], Info_ValueForKey( botInfo, cgBotDebugKeys[i] ), sizeof( values[i] ) );
	}

	y = 300.0f;
	for ( i = 0; i < ARRAY_LEN( cgBotDebugKeys ); i += 2 ) {
		Com_sprintf( line, sizeof( line ), "%s%15s | %s%15s",
			cgBotDebugLabels[i], values[i], cgBotDebugLabels[i + 1], values[i + 1] );
		y += 16.0f;
		CG_Text_Paint( 140.0f, y, 0.12f, colorWhite, line, 0.0f, 0, 0 );
	}
}

/*
=================
CG_DrawActiveFrame

Generates and draws a game scene and status information at the given time.
=================
*/
void CG_DrawActiveFrame( int serverTime, stereoFrame_t stereoView, qboolean demoPlayback ) {
	int		inwater;

	cg.time = serverTime;
	cg.demoPlayback = demoPlayback;
	if ( cg.clientFrame == 0 ) {
		cg_viewFilterTargetKey = CG_VIEW_FILTER_TARGET_NONE;
		CG_ClearBufferedSounds();
	}

	// update cvars
	CG_UpdateCvars();

	// if we are only updating the screen as a loading
	// pacifier, don't even try to read snapshots
	if ( cg.infoScreenText[0] != 0 ) {
		CG_DrawInformation();
		return;
	}

	// any looped sounds will be respecified as entities
	// are added to the render list
	trap_S_ClearLoopingSounds(qfalse);

	// clear all the render lists
	trap_R_ClearScene();

	// set up cg.snap and possibly cg.nextSnap
	CG_ProcessSnapshots();

	// if we haven't received any snapshots yet, all
	// we can draw is the information screen
	if ( !cg.snap || ( cg.snap->snapFlags & SNAPFLAG_NOT_ACTIVE ) ) {
		CG_DrawInformation();
		return;
	}

	CG_RunQueuedAutoActions();

	// this counter will be bumped for every valid scene we generate
	cg.clientFrame++;

	// update cg.predictedPlayerState
	CG_PredictPlayerState();
	CG_UpdateSpectatorTracking();
	CG_UpdateSpectatorCvar();
	CG_RunPendingFollowKiller();

	// decide on third person view
	cg.renderingThirdPerson = (qboolean)( ( cg.snap->ps.stats[STAT_HEALTH] <= 0 )
		|| ( cg_thirdPerson.integer && ( cg.demoPlayback || cg_singlePlayerActive.integer ) ) );


	// build cg.refdef
	inwater = CG_CalcViewValues();

	// let the client system know what our weapon and zoom settings are
	trap_SetUserCmdValue( cg.weaponSelect, cg.zoomSensitivity );

	// first person blend blobs, done after AnglesToAxis
	if ( !cg.renderingThirdPerson ) {
		CG_DamageBlendBlob();
	}

	// build the render lists
	if ( !cg.hyperspace ) {
		CG_AddPacketEntities();			// adter calcViewValues, so predicted player state is correct
		CG_AddMarks();
		CG_AddParticles ();
		CG_AddLocalEntities();
	}
	CG_AddViewWeapon( &cg.predictedPlayerState );

	// add buffered sounds
	CG_PlayBufferedSounds();

	// play buffered voice chats
	CG_PlayBufferedVoiceChats();

	// finish up the rest of the refdef
	if ( cg.testModelEntity.hModel ) {
		CG_AddTestModel();
	}
	cg.refdef.time = cg.time;
	memcpy( cg.refdef.areamask, cg.snap->areamask, sizeof( cg.refdef.areamask ) );

	// warning sounds when powerup is wearing off
	CG_PowerupTimerSounds();

	// update audio positions
	trap_S_Respatialize( cg.snap->ps.clientNum, cg.refdef.vieworg, cg.refdef.viewaxis, inwater );

	// make sure the lagometerSample and frame timing isn't done twice when in stereo
	if ( stereoView != STEREO_RIGHT ) {
		cg.frametime = cg.time - cg.oldTime;
		if ( cg.frametime < 0 ) {
			cg.frametime = 0;
		}
		cg.oldTime = cg.time;
		CG_AddLagometerFrameInfo();
		CG_UpdateSpectatorItemPickups();
	}
	if (cg_timescale.value != cg_timescaleFadeEnd.value) {
		if (cg_timescale.value < cg_timescaleFadeEnd.value) {
			cg_timescale.value += cg_timescaleFadeSpeed.value * ((float)cg.frametime) / 1000;
			if (cg_timescale.value > cg_timescaleFadeEnd.value)
				cg_timescale.value = cg_timescaleFadeEnd.value;
		}
		else {
			cg_timescale.value -= cg_timescaleFadeSpeed.value * ((float)cg.frametime) / 1000;
			if (cg_timescale.value < cg_timescaleFadeEnd.value)
				cg_timescale.value = cg_timescaleFadeEnd.value;
		}
		if (cg_timescaleFadeSpeed.value) {
			trap_Cvar_Set("timescale", va("%f", cg_timescale.value));
		}
	}

	// actually issue the rendering calls
	CG_DrawActive( stereoView );
	CG_DrawBotAIDebugInfo();

	if ( cg_stats.integer ) {
		CG_Printf( "cg.clientFrame:%i\n", cg.clientFrame );
	}

	if ( cg.rageQuitTime == 1 ) {
		trap_SendConsoleCommand( "quit" );
	}
	if ( cg.rageQuitTime > 0 ) {
		cg.rageQuitTime--;
	}
}

