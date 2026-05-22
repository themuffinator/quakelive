from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

C_SOURCE = r"""
#include <math.h>
#include <string.h>
#include "q_shared.h"
#include "bg_public.h"

typedef enum {
	QLR_TRACE_MODE_NONE,
	QLR_TRACE_MODE_AIRSTEP_UNSUPPORTED,
	QLR_TRACE_MODE_LADDER_PROBE,
	QLR_TRACE_MODE_LEDGE_STEP,
} qlr_trace_mode_t;

#ifdef _WIN32
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

static qlr_trace_mode_t qlr_trace_mode;
static int qlr_trace_call_count;
static int qlr_trace_surface_flags;
static float qlr_trace_fraction;
static int qlr_last_trace_content_mask;
static int qlr_point_contents_values[2];
static int qlr_point_contents_call_count;

/*
=============
Com_Printf

Test stub that discards movement debug logging during fixture execution.
=============
*/
void Com_Printf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
trap_SnapVector

Stubbed trap call used by shared movement helpers.
=============
*/
void trap_SnapVector( float *v ) {
	(void)v;
}

/*
=============
Com_Error

Minimal error stub for movement harness builds.
=============
*/
void Com_Error( int level, const char *fmt, ... ) {
	(void)level;
	(void)fmt;
}

/*
=============
QLR_TestPointContents

Returns empty space for fixtures that do not exercise point-contents probes.
=============
*/
static int QLR_TestPointContents( const vec3_t point, int passEntityNum ) {
	(void)point;
	(void)passEntityNum;

	if ( qlr_point_contents_call_count < 2 ) {
		return qlr_point_contents_values[qlr_point_contents_call_count++];
	}

	qlr_point_contents_call_count++;
	return 0;
}

/*
=============
QLR_TestTrace

Supplies deterministic traces for the movement fixtures.
=============
*/
static void QLR_TestTrace( trace_t *trace, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, int passEntityNum, int contentMask ) {
	(void)mins;
	(void)maxs;
	(void)passEntityNum;

	memset( trace, 0, sizeof( *trace ) );
	trace->fraction = 1.0f;
	VectorCopy( end, trace->endpos );
	VectorSet( trace->plane.normal, 0.0f, 0.0f, 1.0f );
	qlr_last_trace_content_mask = contentMask;

	if ( qlr_trace_mode == QLR_TRACE_MODE_AIRSTEP_UNSUPPORTED ) {
		switch ( qlr_trace_call_count ) {
		case 0:
			trace->allsolid = qtrue;
			trace->fraction = 0.0f;
			VectorCopy( start, trace->endpos );
			break;
		case 1:
			VectorCopy( end, trace->endpos );
			break;
		case 2:
			VectorCopy( end, trace->endpos );
			break;
		default:
			break;
		}
	} else if ( qlr_trace_mode == QLR_TRACE_MODE_LADDER_PROBE ) {
		trace->fraction = qlr_trace_fraction;
		trace->surfaceFlags = qlr_trace_surface_flags;
		if ( trace->fraction < 1.0f ) {
			VectorCopy( start, trace->endpos );
		}
	} else if ( qlr_trace_mode == QLR_TRACE_MODE_LEDGE_STEP ) {
		switch ( qlr_trace_call_count ) {
		case 0:
			trace->fraction = 0.0f;
			VectorCopy( start, trace->endpos );
			VectorSet( trace->plane.normal, -1.0f, 0.0f, 0.0f );
			break;
		case 4:
			trace->fraction = 0.5f;
			VectorCopy( end, trace->endpos );
			VectorSet( trace->plane.normal, 0.0f, 0.0f, 1.0f );
			break;
		default:
			break;
		}
	}

	qlr_trace_call_count++;
}

#include "bg_pmove.c"

/*
=============
QLR_ResetMoveState

Initialises one deterministic movement state block for a fixture invocation.
=============
*/
static void QLR_ResetMoveState( pmove_t *localPM, playerState_t *localPS, pmove_settings_t *localSettings ) {
	memset( localPM, 0, sizeof( *localPM ) );
	memset( localPS, 0, sizeof( *localPS ) );
	memset( localSettings, 0, sizeof( *localSettings ) );
	memset( &pml, 0, sizeof( pml ) );

	localPM->ps = localPS;
	localPM->pmoveSettings = localSettings;
	localPM->trace = QLR_TestTrace;
	localPM->pointcontents = QLR_TestPointContents;
	localPM->tracemask = MASK_PLAYERSOLID;
	localPM->cmd.serverTime = 1000;

	localPS->gravity = 800;
	localPS->speed = 320;
	localPS->clientNum = 0;
	localPS->groundEntityNum = ENTITYNUM_NONE;

	VectorSet( localPM->mins, -15.0f, -15.0f, -24.0f );
	VectorSet( localPM->maxs, 15.0f, 15.0f, 32.0f );
	VectorSet( pml.forward, 1.0f, 0.0f, 0.0f );
	VectorSet( pml.right, 0.0f, 1.0f, 0.0f );
	VectorSet( pml.groundTrace.plane.normal, 0.0f, 0.0f, 1.0f );
	pml.frametime = 0.1f;
	pml.msec = 100;
	qlr_trace_mode = QLR_TRACE_MODE_NONE;
	qlr_trace_call_count = 0;
	qlr_trace_surface_flags = 0;
	qlr_trace_fraction = 1.0f;
	qlr_last_trace_content_mask = 0;
	qlr_point_contents_values[0] = 0;
	qlr_point_contents_values[1] = 0;
	qlr_point_contents_call_count = 0;
}

/*
=============
QLR_RunAddEventQueueFrame

Runs the retail predictable-event append helper through the two-slot queue wrap.
=============
*/
QLR_EXPORT int QLR_RunAddEventQueueFrame( int firstEvent, int secondEvent, int thirdEvent, int *eventSequence, int *event0, int *event1, int *parm0, int *parm1 ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	PM_AddEvent( firstEvent );
	PM_AddEvent( secondEvent );
	PM_AddEvent( thirdEvent );

	if ( eventSequence ) {
		*eventSequence = localPS.eventSequence;
	}
	if ( event0 ) {
		*event0 = localPS.events[0];
	}
	if ( event1 ) {
		*event1 = localPS.events[1];
	}
	if ( parm0 ) {
		*parm0 = localPS.eventParms[0];
	}
	if ( parm1 ) {
		*parm1 = localPS.eventParms[1];
	}

	pm = previousPM;
	return 0;
}

/*
=============
QLR_RunAddTouchEntFrame

Runs the retail touch-entity accumulator through world, duplicate, and cap gates.
=============
*/
QLR_EXPORT int QLR_RunAddTouchEntFrame( int *firstTouch, int *lastTouch ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int afterWorldCount;
	int afterDuplicateCount;
	int i;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	PM_AddTouchEnt( ENTITYNUM_WORLD );
	afterWorldCount = localPM.numtouch;

	PM_AddTouchEnt( 17 );
	PM_AddTouchEnt( 17 );
	afterDuplicateCount = localPM.numtouch;

	for ( i = 0; i < MAXTOUCH + 2; i++ ) {
		PM_AddTouchEnt( 100 + i );
	}

	if ( firstTouch ) {
		*firstTouch = localPM.touchents[0];
	}
	if ( lastTouch ) {
		*lastTouch = localPM.touchents[MAXTOUCH - 1];
	}

	result = ( afterWorldCount & 0xff )
		| ( ( afterDuplicateCount & 0xff ) << 8 )
		| ( ( localPM.numtouch & 0xff ) << 16 );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunAnimationHelperFrame

Runs one of the retail low-level animation helpers and writes raw animation and
timer state after the call.
=============
*/
QLR_EXPORT int QLR_RunAnimationHelperFrame( int helper, int pmType, int initialLegsAnim, int initialTorsoAnim, int legsTimer, int torsoTimer, int requestedAnim, int *legsAnim, int *torsoAnim, int *outLegsTimer, int *outTorsoTimer ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = pmType;
	localPS.legsAnim = initialLegsAnim;
	localPS.torsoAnim = initialTorsoAnim;
	localPS.legsTimer = legsTimer;
	localPS.torsoTimer = torsoTimer;

	switch ( helper ) {
	case 0:
		PM_StartTorsoAnim( requestedAnim );
		break;
	case 1:
		PM_StartLegsAnim( requestedAnim );
		break;
	case 2:
		PM_ContinueLegsAnim( requestedAnim );
		break;
	case 3:
		PM_ContinueTorsoAnim( requestedAnim );
		break;
	case 4:
		PM_ForceLegsAnim( requestedAnim );
		break;
	default:
		break;
	}

	if ( legsAnim ) {
		*legsAnim = localPS.legsAnim;
	}
	if ( torsoAnim ) {
		*torsoAnim = localPS.torsoAnim;
	}
	if ( outLegsTimer ) {
		*outLegsTimer = localPS.legsTimer;
	}
	if ( outTorsoTimer ) {
		*outTorsoTimer = localPS.torsoTimer;
	}

	pm = previousPM;
	return 0;
}

/*
=============
QLR_RunClipVelocityFrame

Runs the retail plane-clip helper for one input velocity and writes the result.
=============
*/
QLR_EXPORT int QLR_RunClipVelocityFrame( float velocityX, float velocityY, float velocityZ, float normalX, float normalY, float normalZ, float overbounce, float *outX, float *outY, float *outZ ) {
	vec3_t in;
	vec3_t normal;
	vec3_t out;

	VectorSet( in, velocityX, velocityY, velocityZ );
	VectorSet( normal, normalX, normalY, normalZ );
	VectorClear( out );

	PM_ClipVelocity( in, normal, out, overbounce );

	if ( outX ) {
		*outX = out[0];
	}
	if ( outY ) {
		*outY = out[1];
	}
	if ( outZ ) {
		*outZ = out[2];
	}

	return 0;
}

/*
=============
QLR_RunAccelerateFrame

Runs the retail acceleration helper and returns the resulting X velocity.
=============
*/
QLR_EXPORT float QLR_RunAccelerateFrame( float initialVelocityX, float wishspeed, float accel, float frametime ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	vec3_t wishdir;
	float result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.velocity[0] = initialVelocityX;
	VectorSet( wishdir, 1.0f, 0.0f, 0.0f );
	pml.frametime = frametime;

	PM_Accelerate( wishdir, wishspeed, accel );

	result = localPS.velocity[0];
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunCmdScaleFrame

Runs the retail command scale helper for one command vector.
=============
*/
QLR_EXPORT float QLR_RunCmdScaleFrame( int forwardmove, int rightmove, int upmove, int speed ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	float result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.speed = speed;
	localPM.cmd.forwardmove = (char)forwardmove;
	localPM.cmd.rightmove = (char)rightmove;
	localPM.cmd.upmove = (char)upmove;

	result = PM_CmdScale( &localPM.cmd );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunSetMovementDirFrame

Runs the retail movementDir mapper for one command pair.
=============
*/
QLR_EXPORT int QLR_RunSetMovementDirFrame( int forwardmove, int rightmove, int initialMovementDir ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.movementDir = initialMovementDir;
	localPM.cmd.forwardmove = (char)forwardmove;
	localPM.cmd.rightmove = (char)rightmove;

	PM_SetMovementDir();

	result = localPS.movementDir;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunCircleStrafeFriction

Runs the retail ground-friction branch and returns the resulting horizontal
speed after one frame.
=============
*/
QLR_EXPORT float QLR_RunCircleStrafeFriction( int diagonal ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	float speed;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	pm_aircontrol = 150.0f;
	pm_friction = 6.0f;
	pm_circlestrafe_friction = 5.5f;
	localPS.velocity[0] = 320.0f;
	localPS.movementDir = diagonal ? 1 : 0;
	localPM.cmd.forwardmove = 127;
	localPM.cmd.rightmove = diagonal ? 127 : 0;
	pml.walking = qtrue;

	PM_Friction();

	speed = sqrtf(
		localPS.velocity[0] * localPS.velocity[0]
		+ localPS.velocity[1] * localPS.velocity[1]
	);

	pm = previousPM;
	return speed;
}

/*
=============
QLR_RunDoubleJumpSequence

Exercises one retail air-double-jump sequence and returns a bitmask of the
three probe results: first jump, rejected immediate reuse, and accepted reuse
after clearing the ground-contact latch.
=============
*/
QLR_EXPORT int QLR_RunDoubleJumpSequence( float *firstVelocity, float *secondVelocity, float *thirdVelocity, int *latchAfterFirst, int *latchAfterSecond ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int results;
	qboolean firstJump;
	qboolean secondJump;
	qboolean thirdJump;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.doubleJump = qtrue;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localPM.cmd.upmove = 20;

	firstJump = PM_CheckJump( qtrue );
	if ( firstVelocity ) {
		*firstVelocity = localPS.velocity[2];
	}
	if ( latchAfterFirst ) {
		*latchAfterFirst = localPS.doubleJumped;
	}

	localPS.pm_flags &= ~PMF_JUMP_HELD;
	localPM.cmd.serverTime = 1200;
	secondJump = PM_CheckJump( qtrue );
	if ( secondVelocity ) {
		*secondVelocity = localPS.velocity[2];
	}
	if ( latchAfterSecond ) {
		*latchAfterSecond = localPS.doubleJumped;
	}

	localPS.pm_flags &= ~PMF_JUMP_HELD;
	localPS.doubleJumped = qfalse;
	localPM.cmd.serverTime = 1400;
	thirdJump = PM_CheckJump( qtrue );
	if ( thirdVelocity ) {
		*thirdVelocity = localPS.velocity[2];
	}

	results = ( firstJump ? 1 : 0 ) | ( secondJump ? 2 : 0 ) | ( thirdJump ? 4 : 0 );
	pm = previousPM;
	return results;
}

/*
=============
QLR_RunRampJumpVerticalTakeoff

Runs the shared jump gate with retail ramp-jump vertical accumulation enabled.
=============
*/
QLR_EXPORT float QLR_RunRampJumpVerticalTakeoff( float initialVelocityZ, float rampJumpScale, float jumpVelocityMax ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.chainJump = PM_JUMP_VELOCITY_MODE_SCALE;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = jumpVelocityMax;
	localSettings.rampJump = qtrue;
	localSettings.rampJumpScale = rampJumpScale;
	localPM.cmd.upmove = 20;
	localPS.velocity[2] = initialVelocityZ;

	PM_CheckJump( qfalse );

	pm = previousPM;
	return localPS.velocity[2];
}

/*
=============
QLR_RunChainJumpModeTakeoff

Runs the shared jump gate with a selected retail chain-jump velocity mode.
=============
*/
QLR_EXPORT float QLR_RunChainJumpModeTakeoff( int chainJumpMode, int airControl ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.chainJump = chainJumpMode;
	localSettings.chainJumpVelocity = 110.0f;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localSettings.jumpVelocityScaleAdd = 0.4f;
	localSettings.jumpVelocityTimeThreshold = 500.0f;
	localSettings.jumpVelocityTimeThresholdOffset = 0.6f;
	localSettings.stepJumpVelocity = 48.0f;
	localPM.cmd.serverTime = 100;
	localPM.cmd.upmove = 20;
	if ( airControl ) {
		localPS.pm_flags |= PMF_AIR_CONTROL;
	}

	PM_CheckJump( qfalse );

	pm = previousPM;
	return localPS.velocity[2];
}

/*
=============
QLR_RunChainJumpModeTakeoffAtTime

Runs the shared jump gate with a selected jump velocity mode and command time.
=============
*/
QLR_EXPORT float QLR_RunChainJumpModeTakeoffAtTime( int chainJumpMode, int airControl, int serverTime ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.chainJump = chainJumpMode;
	localSettings.chainJumpVelocity = 110.0f;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localSettings.jumpVelocityScaleAdd = 0.4f;
	localSettings.jumpVelocityTimeThreshold = 500.0f;
	localSettings.jumpVelocityTimeThresholdOffset = 0.6f;
	localSettings.stepJumpVelocity = 48.0f;
	localPM.cmd.serverTime = serverTime;
	localPM.cmd.upmove = 20;
	if ( airControl ) {
		localPS.pm_flags |= PMF_AIR_CONTROL;
	}

	PM_CheckJump( qfalse );

	pm = previousPM;
	return localPS.velocity[2];
}

/*
=============
QLR_RunChainJumpModeTakeoffWithMax

Runs the shared jump gate with a selected jump velocity mode and max clamp.
=============
*/
QLR_EXPORT float QLR_RunChainJumpModeTakeoffWithMax( int chainJumpMode, int airControl, int serverTime, float jumpVelocityMax ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.chainJump = chainJumpMode;
	localSettings.chainJumpVelocity = 110.0f;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = jumpVelocityMax;
	localSettings.jumpVelocityScaleAdd = 0.4f;
	localSettings.jumpVelocityTimeThreshold = 500.0f;
	localSettings.jumpVelocityTimeThresholdOffset = 0.6f;
	localSettings.stepJumpVelocity = 48.0f;
	localPM.cmd.serverTime = serverTime;
	localPM.cmd.upmove = 20;
	if ( airControl ) {
		localPS.pm_flags |= PMF_AIR_CONTROL;
	}

	PM_CheckJump( qfalse );

	pm = previousPM;
	return localPS.velocity[2];
}

/*
=============
QLR_RunStepJumpModeTakeoff

Runs the step-jump wrapper through the selected retail jump velocity mode.
=============
*/
QLR_EXPORT float QLR_RunStepJumpModeTakeoff( int chainJumpMode, int fromCrouchStep, float jumpVelocityMax ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.chainJump = chainJumpMode;
	localSettings.chainJumpVelocity = 110.0f;
	localSettings.crouchStepJump = qtrue;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = jumpVelocityMax;
	localSettings.jumpVelocityScaleAdd = 0.4f;
	localSettings.jumpVelocityTimeThreshold = 500.0f;
	localSettings.jumpVelocityTimeThresholdOffset = 0.6f;
	localSettings.stepJump = qtrue;
	localSettings.stepJumpVelocity = 48.0f;
	localPM.cmd.serverTime = 100;
	localPM.cmd.upmove = 20;
	if ( fromCrouchStep ) {
		localPS.pm_flags |= PMF_DUCKED;
	}

	PM_ApplyStepJump( 12.0f, fromCrouchStep ? qtrue : qfalse );

	pm = previousPM;
	return localPS.velocity[2];
}

/*
=============
QLR_RunStepJumpModeTakeoffAtTime

Runs the step-jump wrapper through the selected mode, profile, and command time.
=============
*/
QLR_EXPORT float QLR_RunStepJumpModeTakeoffAtTime( int chainJumpMode, int fromCrouchStep, int airControl, int serverTime, float jumpVelocityMax ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.chainJump = chainJumpMode;
	localSettings.chainJumpVelocity = 110.0f;
	localSettings.crouchStepJump = qtrue;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = jumpVelocityMax;
	localSettings.jumpVelocityScaleAdd = 0.4f;
	localSettings.jumpVelocityTimeThreshold = 500.0f;
	localSettings.jumpVelocityTimeThresholdOffset = 0.6f;
	localSettings.stepJump = qtrue;
	localSettings.stepJumpVelocity = 48.0f;
	localPM.cmd.serverTime = serverTime;
	localPM.cmd.upmove = 20;
	if ( fromCrouchStep ) {
		localPS.pm_flags |= PMF_DUCKED;
	}
	if ( airControl ) {
		localPS.pm_flags |= PMF_AIR_CONTROL;
	}

	PM_ApplyStepJump( 12.0f, fromCrouchStep ? qtrue : qfalse );

	pm = previousPM;
	return localPS.velocity[2];
}

/*
=============
QLR_RunHeldJumpGate

Runs the shared jump gate with a held jump input and returns whether the
retail auto-hop profile accepted the takeoff.
=============
*/
QLR_EXPORT int QLR_RunHeldJumpGate( int autoHop, int bunnyHop, int pmFlags, int respawned ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	qboolean accepted;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.autoHop = autoHop ? qtrue : qfalse;
	localSettings.bunnyHop = bunnyHop ? qtrue : qfalse;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localPS.pm_flags = pmFlags | PMF_JUMP_HELD;
	if ( respawned ) {
		localPS.pm_flags |= PMF_RESPAWNED;
	}
	localPM.cmd.upmove = 20;

	accepted = PM_CheckJump( qfalse );

	pm = previousPM;
	return accepted ? 1 : 0;
}

/*
=============
QLR_RunJumpPadLaunchJumpProbe

Runs normal and double-jump gates while a jump-pad launch latch is active.
=============
*/
QLR_EXPORT int QLR_RunJumpPadLaunchJumpProbe( float *velocityZ, int *upmove ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int results;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.autoHop = qtrue;
	localSettings.doubleJump = qtrue;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localPS.jumppad_ent = 7;
	localPS.jumppad_frame = localPS.pmove_framecount;
	localPS.velocity[2] = 800.0f;
	localPM.cmd.upmove = 20;

	results = PM_CheckJump( qfalse ) ? 1 : 0;
	localPM.cmd.upmove = 20;
	results |= PM_CheckJump( qtrue ) ? 2 : 0;

	if ( velocityZ ) {
		*velocityZ = localPS.velocity[2];
	}
	if ( upmove ) {
		*upmove = localPM.cmd.upmove;
	}

	pm = previousPM;
	return results;
}

/*
=============
QLR_RunJumpPadLaunchGroundedJumpProbe

Runs the jump gate while a non-vertical jump-pad launch latch is active.
=============
*/
QLR_EXPORT int QLR_RunJumpPadLaunchGroundedJumpProbe( float *velocityZ, int *upmove ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	qboolean accepted;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localSettings.autoHop = qtrue;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localPS.groundEntityNum = ENTITYNUM_WORLD;
	localPS.jumppad_ent = 7;
	localPS.jumppad_frame = localPS.pmove_framecount;
	localPM.cmd.upmove = 20;

	accepted = PM_CheckJump( qfalse );

	if ( velocityZ ) {
		*velocityZ = localPS.velocity[2];
	}
	if ( upmove ) {
		*upmove = localPM.cmd.upmove;
	}

	pm = previousPM;
	return accepted ? 1 : 0;
}

/*
=============
QLR_RunJumpPadLaunchAirStep

Runs an upward air-step collision while a jump-pad launch latch is active.
=============
*/
QLR_EXPORT int QLR_RunJumpPadLaunchAirStep( float *originZ, float *stepUp, float *velocityZ ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	qlr_trace_mode = QLR_TRACE_MODE_AIRSTEP_UNSUPPORTED;
	pm_airsteps = 1;
	pm_stepHeight = 22.0f;
	localPS.jumppad_ent = 7;
	localPS.jumppad_frame = localPS.pmove_framecount;
	localPS.velocity[0] = 100.0f;
	localPS.velocity[2] = 400.0f;

	PM_StepSlideMove( qfalse );

	if ( originZ ) {
		*originZ = localPS.origin[2];
	}
	if ( stepUp ) {
		*stepUp = pml.stepUp;
	}
	if ( velocityZ ) {
		*velocityZ = localPS.velocity[2];
	}

	pm = previousPM;
	return qlr_trace_call_count;
}

/*
=============
QLR_RunJumpPadLaunchGroundPlaneStep

Runs the generic step-up retry while a ground-plane latch is still present
during an upward jump-pad launch.
=============
*/
QLR_EXPORT int QLR_RunJumpPadLaunchGroundPlaneStep( float *originZ, float *stepUp, float *velocityZ ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	qlr_trace_mode = QLR_TRACE_MODE_LEDGE_STEP;
	pm_airsteps = 1;
	pm_stepHeight = 22.0f;
	pml.groundPlane = qtrue;
	VectorSet( pml.groundTrace.plane.normal, 0.0f, 0.0f, 1.0f );
	localPS.jumppad_ent = 7;
	localPS.jumppad_frame = localPS.pmove_framecount;
	localPS.velocity[0] = 100.0f;
	localPS.velocity[2] = 400.0f;

	PM_StepSlideMove( qfalse );

	if ( originZ ) {
		*originZ = localPS.origin[2];
	}
	if ( stepUp ) {
		*stepUp = pml.stepUp;
	}
	if ( velocityZ ) {
		*velocityZ = localPS.velocity[2];
	}

	pm = previousPM;
	return qlr_trace_call_count;
}

/*
=============
QLR_RunJumpPadLaunchPmoveHeldJump

Runs the full Pmove loop with held jump already latched when a jump-pad launch
velocity enters the frame.
=============
*/
QLR_EXPORT int QLR_RunJumpPadLaunchPmoveHeldJump( float *velocityZ, int *upmove, int *pmFlags ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );

	localPS.commandTime = 900;
	localPS.jumppad_ent = 7;
	localPS.jumppad_frame = localPS.pmove_framecount;
	localPS.pm_flags = PMF_JUMP_HELD;
	localPS.velocity[2] = 800.0f;
	localPM.cmd.serverTime = 1000;
	localPM.cmd.upmove = 20;

	Pmove( &localPM );

	if ( velocityZ ) {
		*velocityZ = localPS.velocity[2];
	}
	if ( upmove ) {
		*upmove = localPM.cmd.upmove;
	}
	if ( pmFlags ) {
		*pmFlags = localPS.pm_flags;
	}

	return localPS.doubleJumped;
}

/*
=============
QLR_RunUnsupportedAirStep

Runs the air-step suppression path where the projected endpoint cannot find
support inside the configured step height and returns the number of traces
consumed before the function exits.
=============
*/
QLR_EXPORT int QLR_RunUnsupportedAirStep( float *originZ, float *stepUp, float *velocityZ ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	qlr_trace_mode = QLR_TRACE_MODE_AIRSTEP_UNSUPPORTED;
	pm_airsteps = 0;
	pm_stepHeight = 22.0f;
	localPS.velocity[0] = 100.0f;
	localPS.velocity[2] = 40.0f;

	PM_StepSlideMove( qfalse );

	if ( originZ ) {
		*originZ = localPS.origin[2];
	}
	if ( stepUp ) {
		*stepUp = pml.stepUp;
	}
	if ( velocityZ ) {
		*velocityZ = localPS.velocity[2];
	}

	pm = previousPM;
	return qlr_trace_call_count;
}

/*
=============
QLR_RunCheckLadderProbe

Runs the retail ladder trace leaf and returns whether the ladder latch was set.
=============
*/
QLR_EXPORT int QLR_RunCheckLadderProbe( int surfaceFlags, float fraction, int *contentMask ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	qlr_trace_mode = QLR_TRACE_MODE_LADDER_PROBE;
	qlr_trace_surface_flags = surfaceFlags;
	qlr_trace_fraction = fraction;

	PM_CheckLadder();

	if ( contentMask ) {
		*contentMask = qlr_last_trace_content_mask;
	}
	result = pml.ladder ? 1 : 0;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunLadderMoveVerticalVelocity

Runs one ladder movement frame and returns the resulting vertical velocity.
=============
*/
QLR_EXPORT float QLR_RunLadderMoveVerticalVelocity( int upmove ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	float result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPM.cmd.upmove = (char)upmove;
	pm_accelerate = 10.0f;
	pml.frametime = 0.1f;
	pml.msec = 100;

	PM_LadderMove();

	result = localPS.velocity[2];
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunWaterJumpProbe

Runs the retail water-jump lip probe and returns whether it accepted the jump.
=============
*/
QLR_EXPORT int QLR_RunWaterJumpProbe( int waterlevel, int firstContents, int secondContents, float *velocityX, float *velocityZ, int *pmTime, int *pmFlags, int *pointCalls ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	qboolean accepted;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPM.waterlevel = waterlevel;
	qlr_point_contents_values[0] = firstContents;
	qlr_point_contents_values[1] = secondContents;

	accepted = PM_CheckWaterJump();

	if ( velocityX ) {
		*velocityX = localPS.velocity[0];
	}
	if ( velocityZ ) {
		*velocityZ = localPS.velocity[2];
	}
	if ( pmTime ) {
		*pmTime = localPS.pm_time;
	}
	if ( pmFlags ) {
		*pmFlags = localPS.pm_flags;
	}
	if ( pointCalls ) {
		*pointCalls = qlr_point_contents_call_count;
	}

	pm = previousPM;
	return accepted ? 1 : 0;
}

/*
=============
QLR_RunWaterMoveIdleSink

Runs the retail swimming idle fallback and returns the resulting vertical speed.
=============
*/
QLR_EXPORT float QLR_RunWaterMoveIdleSink( void ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	float result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPM.waterlevel = 3;
	pm_wateraccelerate = 4.0f;
	pml.frametime = 0.1f;
	pml.msec = 100;

	PM_WaterMove();

	result = localPS.velocity[2];
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunCrouchSlideFootstepFrame

Runs the PM_Footsteps crouch-slide movement gate with no directional input and
packs bobCycle plus whether the crouch-walk animation was selected.
=============
*/
QLR_EXPORT int QLR_RunCrouchSlideFootstepFrame( int crouchSlideTime ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.groundEntityNum = 0;
	localPS.velocity[0] = 320.0f;
	localPS.pm_flags = PMF_DUCKED | PMF_CROUCH_SLIDE;
	localPS.crouchSlideTime = crouchSlideTime;
	localPM.cmd.upmove = -127;

	PM_Footsteps();

	result = ( ( localPS.bobCycle & 0xff ) << 8 )
		| ( ( ( localPS.legsAnim & ~ANIM_TOGGLEBIT ) == LEGS_WALKCR ) ? 1 : 0 );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunCheckDuckCrouchSlideStandClear

Runs PM_CheckDuck through the retail stand-up crouch-slide cleanup gate and
returns the remaining crouchSlideTime.
=============
*/
QLR_EXPORT int QLR_RunCheckDuckCrouchSlideStandClear( int pmFlags, int crouchSlideTime, int groundPlane, int settingsCrouchSlide ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_flags = pmFlags;
	localPS.crouchSlideTime = crouchSlideTime;
	localSettings.crouchSlide = settingsCrouchSlide ? qtrue : qfalse;
	localPM.cmd.upmove = 0;
	pml.groundPlane = groundPlane ? qtrue : qfalse;

	PM_CheckDuck();

	result = localPS.crouchSlideTime;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunWaterEventsFrame

Runs PM_WaterEvents for a single transition and packs eventSequence plus the
first two event ids.
=============
*/
QLR_EXPORT int QLR_RunWaterEventsFrame( int pmType, int previousWaterlevel, int waterlevel, int invulnerabilityActive ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = pmType;
	localPS.powerups[PW_INVULNERABILITY] = invulnerabilityActive ? PM_INVULNERABILITY_ACTIVE_TIME : 0;
	localPM.waterlevel = waterlevel;
	pml.previous_waterlevel = previousWaterlevel;

	PM_WaterEvents();

	result = ( ( localPS.eventSequence & 0xff ) << 16 )
		| ( ( localPS.events[0] & 0xff ) << 8 )
		| ( localPS.events[1] & 0xff );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunFootstepSurfaceEvent

Runs the retail surface footstep selector for a single surface flag bundle.
=============
*/
QLR_EXPORT int QLR_RunFootstepSurfaceEvent( int noFootsteps, int surfaceFlags ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPM.noFootsteps = noFootsteps ? qtrue : qfalse;
	pml.groundTrace.surfaceFlags = surfaceFlags;

	result = PM_FootstepForSurface();
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunNoFootstepsCycleFrame

Runs PM_Footsteps across one bob-cycle boundary and packs the generated event
sequence and event id.
=============
*/
QLR_EXPORT int QLR_RunNoFootstepsCycleFrame( int noFootsteps ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPM.noFootsteps = noFootsteps ? qtrue : qfalse;
	localPS.groundEntityNum = 0;
	localPS.velocity[0] = 320.0f;
	localPM.cmd.forwardmove = 127;
	pml.msec = 200;

	PM_Footsteps();

	result = ( ( localPS.eventSequence & 0xff ) << 8 ) | ( localPS.events[0] & 0xff );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunFootstepVelocityGateFrame

Runs PM_Footsteps through the retail non-walking speed gate and packs bobCycle,
eventSequence, event id, and the selected legs animation family.
=============
*/
QLR_EXPORT int QLR_RunFootstepVelocityGateFrame( float velocityX, float velocityY, int backwards ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int anim;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.groundEntityNum = 0;
	localPS.velocity[0] = velocityX;
	localPS.velocity[1] = velocityY;
	if ( backwards ) {
		localPS.pm_flags = PMF_BACKWARDS_RUN;
		localPM.cmd.forwardmove = -127;
	} else {
		localPM.cmd.forwardmove = 127;
	}
	pml.msec = 200;

	PM_Footsteps();

	switch ( localPS.legsAnim & ~ANIM_TOGGLEBIT ) {
	case LEGS_RUN:
		anim = 1;
		break;
	case LEGS_WALK:
		anim = 2;
		break;
	case LEGS_BACK:
		anim = 3;
		break;
	case LEGS_BACKWALK:
		anim = 4;
		break;
	default:
		anim = 0;
		break;
	}

	result = ( ( localPS.bobCycle & 0xff ) << 24 )
		| ( ( localPS.eventSequence & 0xff ) << 16 )
		| ( ( localPS.events[0] & 0xff ) << 8 )
		| ( anim & 0xff );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunCrashLandHealthGate

Runs PM_CrashLand through the retail gib-health event gate and packs
eventSequence, event id, legsTimer, and bobCycle.
=============
*/
QLR_EXPORT int QLR_RunCrashLandHealthGate( int health ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.stats[STAT_HEALTH] = health;
	localPS.bobCycle = 99;
	localPS.gravity = 800;
	localPS.origin[2] = 0.0f;
	pml.previous_origin[2] = 0.0f;
	pml.previous_velocity[2] = -300.0f;
	pml.groundTrace.surfaceFlags = 0;
	localPM.waterlevel = 0;

	PM_CrashLand();

	result = ( ( localPS.eventSequence & 0xff ) << 24 )
		| ( ( localPS.events[0] & 0xff ) << 16 )
		| ( ( localPS.legsTimer & 0xff ) << 8 )
		| ( localPS.bobCycle & 0xff );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunCrashLandDoubleJumpLatch

Runs PM_CrashLand through the retail double-jump latch clear and returns the
post-landing doubleJumped state.
=============
*/
QLR_EXPORT int QLR_RunCrashLandDoubleJumpLatch( int pmFlags, int doubleJumped, float previousVelocityZ ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_flags = pmFlags;
	localPS.doubleJumped = doubleJumped ? qtrue : qfalse;
	localPS.stats[STAT_HEALTH] = 100;
	localPS.gravity = 800;
	localPS.origin[2] = 0.0f;
	pml.previous_origin[2] = 0.0f;
	pml.previous_velocity[2] = previousVelocityZ;
	pml.groundTrace.surfaceFlags = 0;
	localPM.waterlevel = 0;

	PM_CrashLand();

	result = localPS.doubleJumped ? 1 : 0;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunDropTimersCrouchSlide

Runs PM_DropTimers against the crouch-slide timer gate and returns the post
timer value.
=============
*/
QLR_EXPORT int QLR_RunDropTimersCrouchSlide( int pmFlags, int groundPlane, int crouchSlideTime, int msec ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_flags = pmFlags;
	localPS.crouchSlideTime = crouchSlideTime;
	pml.groundPlane = groundPlane ? qtrue : qfalse;
	pml.msec = msec;

	PM_DropTimers();

	result = localPS.crouchSlideTime;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunDropTimersFrame

Runs the retail timer decay helper and writes the post-frame misc, animation,
and crouch-slide timer state.
=============
*/
QLR_EXPORT int QLR_RunDropTimersFrame( int pmFlags, int pmTime, int legsTimer, int torsoTimer, int crouchSlideTime, int groundPlane, int msec, int *outFlags, int *outPmTime, int *outLegsTimer, int *outTorsoTimer, int *outCrouchSlideTime ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_flags = pmFlags;
	localPS.pm_time = pmTime;
	localPS.legsTimer = legsTimer;
	localPS.torsoTimer = torsoTimer;
	localPS.crouchSlideTime = crouchSlideTime;
	pml.groundPlane = groundPlane ? qtrue : qfalse;
	pml.msec = msec;

	PM_DropTimers();

	if ( outFlags ) {
		*outFlags = localPS.pm_flags;
	}
	if ( outPmTime ) {
		*outPmTime = localPS.pm_time;
	}
	if ( outLegsTimer ) {
		*outLegsTimer = localPS.legsTimer;
	}
	if ( outTorsoTimer ) {
		*outTorsoTimer = localPS.torsoTimer;
	}
	if ( outCrouchSlideTime ) {
		*outCrouchSlideTime = localPS.crouchSlideTime;
	}

	pm = previousPM;
	return 0;
}

/*
=============
QLR_RunUpdateViewAnglesGate

Runs the retail view-angle gate directly and returns whether pitch changed.
=============
*/
QLR_EXPORT int QLR_RunUpdateViewAnglesGate( int pmType, int health ) {
	playerState_t localPS;
	usercmd_t localCmd;

	memset( &localPS, 0, sizeof( localPS ) );
	memset( &localCmd, 0, sizeof( localCmd ) );

	localPS.pm_type = pmType;
	localPS.stats[STAT_HEALTH] = health;
	localCmd.angles[PITCH] = ANGLE2SHORT( 20.0f );

	PM_UpdateViewAngles( &localPS, &localCmd );

	return localPS.viewangles[PITCH] > 19.0f ? 1 : 0;
}

/*
=============
QLR_RunFreezePmoveViewAngles

Runs PmoveSingle through the PM_FREEZE path and returns whether command time and
viewangles still advanced before the freeze early return.
=============
*/
QLR_EXPORT int QLR_RunFreezePmoveViewAngles( void ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = PM_FREEZE;
	localPS.stats[STAT_HEALTH] = 0;
	localPS.commandTime = 900;
	localPM.cmd.serverTime = 1000;
	localPM.cmd.angles[YAW] = ANGLE2SHORT( 90.0f );

	PmoveSingle( &localPM );

	result = ( localPS.commandTime == 1000 ? 1 : 0 )
		| ( localPS.viewangles[YAW] > 89.0f ? 2 : 0 )
		| ( localPM.numtouch == 0 ? 4 : 0 );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunInvulnerabilityWalkFrame

Runs the retail PM_WalkMove invulnerability handoff with jump input queued and
packs whether the jump gate was bypassed, the mirror was armed, and input was
cleared by PM_InvulnerabilityMove.
=============
*/
QLR_EXPORT int QLR_RunInvulnerabilityWalkFrame( void ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	const gitem_t *invulnerabilityItem;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	invulnerabilityItem = BG_FindItemForHoldable( HI_INVULNERABILITY );
	localPS.groundEntityNum = 0;
	localPS.pm_type = PM_NORMAL;
	localPS.stats[STAT_HOLDABLE_ITEM] = (int)( invulnerabilityItem - bg_itemlist );
	localPS.pm_flags = PMF_USE_ITEM_HELD;
	localPS.stats[STAT_PLAYER_ITEM_TIME] = 10000;
	localPS.stats[STAT_PLAYER_ITEM_TIME_MAX] = 10000;
	localPS.stats[STAT_PLAYER_ITEM_RECHARGE] = 0;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localPM.cmd.upmove = 20;
	pml.groundPlane = qtrue;
	pml.walking = qtrue;

	PM_WalkMove();

	result = ( localPS.jumpTime == 0 ? 1 : 0 )
		| ( localPS.powerups[PW_INVULNERABILITY] == PM_INVULNERABILITY_ACTIVE_TIME ? 2 : 0 )
		| ( localPM.cmd.upmove == 0 ? 4 : 0 );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunInvulnerabilityTimerGateFrame

Runs the retail invulnerability timer dispatch gate and packs whether the
powerup mirror was armed, the held item survived, and input was cleared.
=============
*/
QLR_EXPORT int QLR_RunInvulnerabilityTimerGateFrame( int itemTime, int itemTimeMax ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	const gitem_t *invulnerabilityItem;
	pmove_t *previousPM;
	int invulnerabilityItemNum;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	invulnerabilityItem = BG_FindItemForHoldable( HI_INVULNERABILITY );
	invulnerabilityItemNum = (int)( invulnerabilityItem - bg_itemlist );
	localPS.groundEntityNum = 0;
	localPS.pm_type = PM_NORMAL;
	localPS.stats[STAT_HOLDABLE_ITEM] = invulnerabilityItemNum;
	localPS.pm_flags = PMF_USE_ITEM_HELD;
	localPS.stats[STAT_PLAYER_ITEM_TIME] = itemTime;
	localPS.stats[STAT_PLAYER_ITEM_TIME_MAX] = itemTimeMax;
	localPS.stats[STAT_PLAYER_ITEM_RECHARGE] = itemTimeMax;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localPM.cmd.upmove = 20;
	pml.groundPlane = qtrue;
	pml.walking = qtrue;

	PM_WalkMove();

	result = ( localPS.powerups[PW_INVULNERABILITY] == PM_INVULNERABILITY_ACTIVE_TIME ? 1 : 0 )
		| ( localPS.stats[STAT_HOLDABLE_ITEM] == invulnerabilityItemNum ? 2 : 0 )
		| ( localPM.cmd.upmove == 0 ? 4 : 0 );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunFiringFlagFrame

Runs one full movement frame and returns the post-pmove EF_FIRING state.
=============
*/
QLR_EXPORT int QLR_RunFiringFlagFrame( int pmType, int health, int weapon, int ammo, int buttons, int pmFlags ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = pmType;
	localPS.stats[STAT_HEALTH] = health;
	localPS.weapon = weapon;
	localPS.pm_flags = pmFlags;
	localPS.eFlags = EF_FIRING;
	localPM.cmd.buttons = buttons;
	localPM.cmd.weapon = weapon;

	if ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
		localPS.stats[STAT_WEAPONS] |= ( 1 << weapon );
		localPS.ammo[weapon] = ammo;
	}

	PmoveSingle( &localPM );

	result = localPS.eFlags & EF_FIRING;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunDeadTraceMaskFrame

Runs one frozen dead-player frame and returns whether CONTENTS_BODY remains in
the pmove tracemask after the retail invulnerability gate.
=============
*/
QLR_EXPORT int QLR_RunDeadTraceMaskFrame( int invulnerabilityActive ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = PM_FREEZE;
	localPS.stats[STAT_HEALTH] = 0;
	if ( invulnerabilityActive ) {
		localPS.powerups[PW_INVULNERABILITY] = 1;
	}

	PmoveSingle( &localPM );

	result = ( localPM.tracemask & CONTENTS_BODY ) ? 1 : 0;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunAnimateButtonFrame

Runs the retail torso-button animation helper and writes the resulting masked
torso animation, timer, and predictable event state.
=============
*/
QLR_EXPORT int QLR_RunAnimateButtonFrame( int buttons, int initialTorsoTimer, int *torsoAnim, int *torsoTimer, int *eventSequence, int *eventId ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = PM_NORMAL;
	localPS.torsoAnim = TORSO_STAND;
	localPS.torsoTimer = initialTorsoTimer;
	localPM.cmd.buttons = buttons;

	PM_Animate();

	if ( torsoAnim ) {
		*torsoAnim = localPS.torsoAnim & ~ANIM_TOGGLEBIT;
	}
	if ( torsoTimer ) {
		*torsoTimer = localPS.torsoTimer;
	}
	if ( eventSequence ) {
		*eventSequence = localPS.eventSequence;
	}
	if ( eventId ) {
		*eventId = localPS.events[0];
	}

	pm = previousPM;
	return 0;
}

/*
=============
QLR_RunTorsoAnimationFrame

Runs the post-weapon retail torso-idle helper and writes the resulting masked
torso animation and timer.
=============
*/
QLR_EXPORT int QLR_RunTorsoAnimationFrame( int pmType, int weaponState, int weapon, int initialTorsoAnim, int initialTorsoTimer, int *torsoAnim, int *torsoTimer ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = pmType;
	localPS.weaponstate = weaponState;
	localPS.weapon = weapon;
	localPS.torsoAnim = initialTorsoAnim;
	localPS.torsoTimer = initialTorsoTimer;

	PM_TorsoAnimation();

	if ( torsoAnim ) {
		*torsoAnim = localPS.torsoAnim & ~ANIM_TOGGLEBIT;
	}
	if ( torsoTimer ) {
		*torsoTimer = localPS.torsoTimer;
	}

	pm = previousPM;
	return 0;
}

/*
=============
QLR_RunWeaponResetFrame

Runs one full movement frame with PMF_WEAPON_RESET set and packs the post-pmove
weaponTime, weaponstate, PMF_WEAPON_RESET, and EF_FIRING state.
=============
*/
QLR_EXPORT int QLR_RunWeaponResetFrame( void ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = PM_NORMAL;
	localPS.stats[STAT_HEALTH] = 100;
	localPS.stats[STAT_WEAPONS] = ( 1 << WP_MACHINEGUN );
	localPS.ammo[WP_MACHINEGUN] = 10;
	localPS.weapon = WP_MACHINEGUN;
	localPS.weaponstate = WEAPON_READY;
	localPS.weaponTime = 0;
	localPS.eFlags = EF_FIRING;
	localPS.pm_flags = PMF_WEAPON_RESET;
	localPM.cmd.buttons = BUTTON_ATTACK;
	localPM.cmd.weapon = WP_MACHINEGUN;

	PmoveSingle( &localPM );

	result = ( ( localPS.weaponTime & 0xffff ) << 16 )
		| ( ( localPS.weaponstate & 0xff ) << 8 )
		| ( ( localPS.pm_flags & PMF_WEAPON_RESET ) ? 2 : 0 )
		| ( ( localPS.eFlags & EF_FIRING ) ? 1 : 0 );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunWeaponSentinelChangeFrame

Runs PM_Weapon through the retail WP_NUM_WEAPONS sentinel change path and packs
the sentinel weapon, ready state, unchanged timer, torso idle, and change event.
=============
*/
QLR_EXPORT int QLR_RunWeaponSentinelChangeFrame( void ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = PM_NORMAL;
	localPS.stats[STAT_HEALTH] = 100;
	localPS.stats[STAT_WEAPONS] = ( 1 << WP_MACHINEGUN ) | ( 1 << WP_NUM_WEAPONS );
	localPS.weapon = WP_MACHINEGUN;
	localPS.weaponstate = WEAPON_READY;
	localPS.weaponTime = 0;
	localPM.cmd.weapon = WP_NUM_WEAPONS;

	PM_Weapon();

	result = ( localPS.weapon == WP_NUM_WEAPONS ? 1 : 0 )
		| ( localPS.weaponstate == WEAPON_READY ? 2 : 0 )
		| ( localPS.weaponTime == 0 ? 4 : 0 )
		| ( ( localPS.torsoAnim & ~ANIM_TOGGLEBIT ) == TORSO_STAND ? 8 : 0 )
		| ( localPS.eventSequence == 1 && localPS.events[0] == EV_CHANGE_WEAPON ? 16 : 0 );
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunWeaponReloadScaleFrame

Runs PM_Weapon through one rocket-fire frame and returns the resulting refire
timer after retail powerup scaling.
=============
*/
QLR_EXPORT int QLR_RunWeaponReloadScaleFrame( int persistantPowerup, int hasteActive ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	gitem_t *itemDef;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = PM_NORMAL;
	localPS.stats[STAT_HEALTH] = 100;
	localPS.stats[STAT_WEAPONS] = ( 1 << WP_ROCKET_LAUNCHER );
	localPS.weapon = WP_ROCKET_LAUNCHER;
	localPS.weaponstate = WEAPON_READY;
	localPS.ammo[WP_ROCKET_LAUNCHER] = 5;
	localPM.cmd.buttons = BUTTON_ATTACK;
	localPM.cmd.weapon = WP_ROCKET_LAUNCHER;

	if ( persistantPowerup > PW_NONE && persistantPowerup < PW_NUM_POWERUPS ) {
		itemDef = BG_FindItemForPowerup( (powerup_t)persistantPowerup );
		if ( itemDef ) {
			localPS.stats[STAT_PERSISTANT_POWERUP] = (int)( itemDef - bg_itemlist );
		}
	}
	if ( hasteActive ) {
		localPS.powerups[PW_HASTE] = PM_INVULNERABILITY_ACTIVE_TIME;
	}

	PM_Weapon();

	result = localPS.weaponTime;
	pm = previousPM;
	return result;
}

/*
=============
QLR_RunChaingunSpinFrame

Runs PM_Weapon through one chaingun frame and packs weaponTime with the retail
spin-up stat after attack, full-spin, release, or attack-lockout paths.
=============
*/
QLR_EXPORT int QLR_RunChaingunSpinFrame( int initialSpin, int attack, int attackLockout ) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;
	pmove_t *previousPM;
	int result;

	QLR_ResetMoveState( &localPM, &localPS, &localSettings );
	previousPM = pm;
	pm = &localPM;

	localPS.pm_type = PM_NORMAL;
	localPS.stats[STAT_HEALTH] = 100;
	localPS.stats[STAT_WEAPONS] = ( 1 << WP_CHAINGUN );
	localPS.stats[STAT_CHAINGUN_SPINUP] = initialSpin;
	localPS.weapon = WP_CHAINGUN;
	localPS.weaponstate = WEAPON_READY;
	localPS.ammo[WP_CHAINGUN] = 5;
	localPM.cmd.weapon = WP_CHAINGUN;
	if ( attack ) {
		localPM.cmd.buttons |= BUTTON_ATTACK;
	}
	if ( attackLockout ) {
		localPS.pm_flags |= PMF_ATTACK_LOCKOUT;
	}

	PM_Weapon();

	result = ( ( localPS.weaponTime & 0xffff ) << 16 )
		| ( localPS.stats[STAT_CHAINGUN_SPINUP] & 0xffff );
	pm = previousPM;
	return result;
}
"""

SOURCES = [
	"src/code/game/bg_slidemove.c",
	"src/code/game/bg_lib.c",
	"src/code/game/bg_misc.c",
	"src/code/game/q_math.c",
	"src/code/game/q_shared.c",
]


def _find_c_compiler() -> str:
	compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
	if not compiler:
		pytest.skip("No C compiler found for pmove movement fixtures")

	return compiler


@pytest.fixture(scope="session")
def pmove_fixture_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("pmove_movement_fixtures")
	src_path = build_dir / "pmove_movement_fixtures.c"
	lib_path = build_dir / ("pmove_movement_fixtures.dll" if os.name == "nt" else "libpmove_movement_fixtures.so")
	compiler = _find_c_compiler()

	src_path.write_text(C_SOURCE, encoding="utf-8")

	compile_args = [
		compiler,
		"-shared",
	]

	if os.name != "nt":
		compile_args.extend(["-fPIC", "-lm"])
	else:
		compile_args.extend(["-DWIN32", "-D_CRT_SECURE_NO_WARNINGS", "-Wno-return-type"])

	compile_cmd = [
		*compile_args,
		"-Isrc/common",
		"-Isrc/code",
		"-Isrc/code/cgame",
		"-Isrc/code/game",
		"-Isrc/code/qcommon",
		str(src_path),
		*[str(REPO_ROOT / source) for source in SOURCES],
		"-o",
		str(lib_path),
	]
	subprocess.check_call(compile_cmd, cwd=REPO_ROOT)

	library = ctypes.CDLL(str(lib_path))
	library.QLR_RunAddEventQueueFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunAddEventQueueFrame.restype = ctypes.c_int
	library.QLR_RunAddTouchEntFrame.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunAddTouchEntFrame.restype = ctypes.c_int
	library.QLR_RunAnimationHelperFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunAnimationHelperFrame.restype = ctypes.c_int
	library.QLR_RunClipVelocityFrame.argtypes = [
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	library.QLR_RunClipVelocityFrame.restype = ctypes.c_int
	library.QLR_RunAccelerateFrame.argtypes = [
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
	]
	library.QLR_RunAccelerateFrame.restype = ctypes.c_float
	library.QLR_RunCmdScaleFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunCmdScaleFrame.restype = ctypes.c_float
	library.QLR_RunSetMovementDirFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunSetMovementDirFrame.restype = ctypes.c_int
	library.QLR_RunCircleStrafeFriction.argtypes = [ctypes.c_int]
	library.QLR_RunCircleStrafeFriction.restype = ctypes.c_float
	library.QLR_RunDoubleJumpSequence.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunDoubleJumpSequence.restype = ctypes.c_int
	library.QLR_RunRampJumpVerticalTakeoff.argtypes = [
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
	]
	library.QLR_RunRampJumpVerticalTakeoff.restype = ctypes.c_float
	library.QLR_RunChainJumpModeTakeoff.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunChainJumpModeTakeoff.restype = ctypes.c_float
	library.QLR_RunChainJumpModeTakeoffAtTime.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunChainJumpModeTakeoffAtTime.restype = ctypes.c_float
	library.QLR_RunChainJumpModeTakeoffWithMax.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_float,
	]
	library.QLR_RunChainJumpModeTakeoffWithMax.restype = ctypes.c_float
	library.QLR_RunStepJumpModeTakeoff.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_float,
	]
	library.QLR_RunStepJumpModeTakeoff.restype = ctypes.c_float
	library.QLR_RunStepJumpModeTakeoffAtTime.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_float,
	]
	library.QLR_RunStepJumpModeTakeoffAtTime.restype = ctypes.c_float
	library.QLR_RunHeldJumpGate.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunHeldJumpGate.restype = ctypes.c_int
	library.QLR_RunJumpPadLaunchJumpProbe.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunJumpPadLaunchJumpProbe.restype = ctypes.c_int
	library.QLR_RunJumpPadLaunchGroundedJumpProbe.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunJumpPadLaunchGroundedJumpProbe.restype = ctypes.c_int
	library.QLR_RunJumpPadLaunchAirStep.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	library.QLR_RunJumpPadLaunchAirStep.restype = ctypes.c_int
	library.QLR_RunJumpPadLaunchGroundPlaneStep.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	library.QLR_RunJumpPadLaunchGroundPlaneStep.restype = ctypes.c_int
	library.QLR_RunJumpPadLaunchPmoveHeldJump.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunJumpPadLaunchPmoveHeldJump.restype = ctypes.c_int
	library.QLR_RunUnsupportedAirStep.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	library.QLR_RunUnsupportedAirStep.restype = ctypes.c_int
	library.QLR_RunCheckLadderProbe.argtypes = [
		ctypes.c_int,
		ctypes.c_float,
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunCheckLadderProbe.restype = ctypes.c_int
	library.QLR_RunLadderMoveVerticalVelocity.argtypes = [ctypes.c_int]
	library.QLR_RunLadderMoveVerticalVelocity.restype = ctypes.c_float
	library.QLR_RunWaterJumpProbe.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunWaterJumpProbe.restype = ctypes.c_int
	library.QLR_RunWaterMoveIdleSink.argtypes = []
	library.QLR_RunWaterMoveIdleSink.restype = ctypes.c_float
	library.QLR_RunCrouchSlideFootstepFrame.argtypes = [ctypes.c_int]
	library.QLR_RunCrouchSlideFootstepFrame.restype = ctypes.c_int
	library.QLR_RunCheckDuckCrouchSlideStandClear.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunCheckDuckCrouchSlideStandClear.restype = ctypes.c_int
	library.QLR_RunWaterEventsFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunWaterEventsFrame.restype = ctypes.c_int
	library.QLR_RunFootstepSurfaceEvent.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunFootstepSurfaceEvent.restype = ctypes.c_int
	library.QLR_RunNoFootstepsCycleFrame.argtypes = [ctypes.c_int]
	library.QLR_RunNoFootstepsCycleFrame.restype = ctypes.c_int
	library.QLR_RunFootstepVelocityGateFrame.argtypes = [
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_int,
	]
	library.QLR_RunFootstepVelocityGateFrame.restype = ctypes.c_int
	library.QLR_RunCrashLandHealthGate.argtypes = [ctypes.c_int]
	library.QLR_RunCrashLandHealthGate.restype = ctypes.c_int
	library.QLR_RunCrashLandDoubleJumpLatch.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_float,
	]
	library.QLR_RunCrashLandDoubleJumpLatch.restype = ctypes.c_int
	library.QLR_RunDropTimersCrouchSlide.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunDropTimersCrouchSlide.restype = ctypes.c_int
	library.QLR_RunDropTimersFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunDropTimersFrame.restype = ctypes.c_int
	library.QLR_RunUpdateViewAnglesGate.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunUpdateViewAnglesGate.restype = ctypes.c_int
	library.QLR_RunFreezePmoveViewAngles.argtypes = []
	library.QLR_RunFreezePmoveViewAngles.restype = ctypes.c_int
	library.QLR_RunInvulnerabilityWalkFrame.argtypes = []
	library.QLR_RunInvulnerabilityWalkFrame.restype = ctypes.c_int
	library.QLR_RunInvulnerabilityTimerGateFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunInvulnerabilityTimerGateFrame.restype = ctypes.c_int
	library.QLR_RunFiringFlagFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunFiringFlagFrame.restype = ctypes.c_int
	library.QLR_RunDeadTraceMaskFrame.argtypes = [ctypes.c_int]
	library.QLR_RunDeadTraceMaskFrame.restype = ctypes.c_int
	library.QLR_RunAnimateButtonFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunAnimateButtonFrame.restype = ctypes.c_int
	library.QLR_RunTorsoAnimationFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunTorsoAnimationFrame.restype = ctypes.c_int
	library.QLR_RunWeaponResetFrame.argtypes = []
	library.QLR_RunWeaponResetFrame.restype = ctypes.c_int
	library.QLR_RunWeaponSentinelChangeFrame.argtypes = []
	library.QLR_RunWeaponSentinelChangeFrame.restype = ctypes.c_int
	library.QLR_RunWeaponReloadScaleFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunWeaponReloadScaleFrame.restype = ctypes.c_int
	library.QLR_RunChaingunSpinFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunChaingunSpinFrame.restype = ctypes.c_int
	return library


def test_add_event_queue_uses_retail_two_slot_wrap_and_zero_parms(pmove_fixture_harness: ctypes.CDLL) -> None:
	event_sequence = ctypes.c_int(0)
	event0 = ctypes.c_int(0)
	event1 = ctypes.c_int(0)
	parm0 = ctypes.c_int(-1)
	parm1 = ctypes.c_int(-1)

	assert pmove_fixture_harness.QLR_RunAddEventQueueFrame(
		41,
		42,
		43,
		ctypes.byref(event_sequence),
		ctypes.byref(event0),
		ctypes.byref(event1),
		ctypes.byref(parm0),
		ctypes.byref(parm1),
	) == 0
	assert event_sequence.value == 3
	assert event0.value == 43
	assert event1.value == 42
	assert parm0.value == 0
	assert parm1.value == 0


def test_add_touch_ent_skips_world_deduplicates_and_caps_the_retail_list(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	first_touch = ctypes.c_int(0)
	last_touch = ctypes.c_int(0)
	result = pmove_fixture_harness.QLR_RunAddTouchEntFrame(
		ctypes.byref(first_touch),
		ctypes.byref(last_touch),
	)

	assert result & 0xff == 0
	assert (result >> 8) & 0xff == 1
	assert (result >> 16) & 0xff == 32
	assert first_touch.value == 17
	assert last_touch.value == 130


def _run_animation_helper_frame(
	pmove_fixture_harness: ctypes.CDLL,
	helper: int,
	pm_type: int,
	initial_legs_anim: int,
	initial_torso_anim: int,
	legs_timer: int,
	torso_timer: int,
	requested_anim: int,
) -> tuple[int, int, int, int]:
	legs_anim = ctypes.c_int(0)
	torso_anim = ctypes.c_int(0)
	out_legs_timer = ctypes.c_int(0)
	out_torso_timer = ctypes.c_int(0)

	assert pmove_fixture_harness.QLR_RunAnimationHelperFrame(
		helper,
		pm_type,
		initial_legs_anim,
		initial_torso_anim,
		legs_timer,
		torso_timer,
		requested_anim,
		ctypes.byref(legs_anim),
		ctypes.byref(torso_anim),
		ctypes.byref(out_legs_timer),
		ctypes.byref(out_torso_timer),
	) == 0
	return legs_anim.value, torso_anim.value, out_legs_timer.value, out_torso_timer.value


def test_animation_helpers_toggle_torso_and_respect_dead_gate(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	pm_dead = 3
	helper_start_torso = 0
	helper_continue_torso = 3
	anim_togglebit = 128
	legs_idle = 22
	torso_attack = 7
	torso_stand = 11

	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_start_torso, pm_normal, legs_idle, torso_stand, 0, 0, torso_attack
	) == (legs_idle, anim_togglebit | torso_attack, 0, 0)
	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_start_torso, pm_dead, legs_idle, torso_stand, 0, 0, torso_attack
	) == (legs_idle, torso_stand, 0, 0)
	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_continue_torso, pm_normal, legs_idle, torso_stand, 0, 75, torso_attack
	) == (legs_idle, torso_stand, 0, 75)
	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_continue_torso, pm_normal, legs_idle, torso_stand, 0, 0, torso_stand
	) == (legs_idle, torso_stand, 0, 0)


def test_animation_helpers_keep_retail_legs_timer_and_force_semantics(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	pm_dead = 3
	helper_start_legs = 1
	helper_continue_legs = 2
	helper_force_legs = 4
	anim_togglebit = 128
	legs_idle = 22
	legs_run = 15
	torso_stand = 11

	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_start_legs, pm_normal, legs_idle, torso_stand, 50, 0, legs_run
	) == (legs_idle, torso_stand, 50, 0)
	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_continue_legs, pm_normal, legs_idle, torso_stand, 50, 0, legs_run
	) == (legs_idle, torso_stand, 50, 0)
	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_continue_legs, pm_normal, legs_run, torso_stand, 0, 0, legs_run
	) == (legs_run, torso_stand, 0, 0)
	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_force_legs, pm_normal, legs_idle, torso_stand, 50, 0, legs_run
	) == (anim_togglebit | legs_run, torso_stand, 0, 0)
	assert _run_animation_helper_frame(
		pmove_fixture_harness, helper_force_legs, pm_dead, legs_idle, torso_stand, 50, 0, legs_run
	) == (legs_idle, torso_stand, 0, 0)


def test_clip_velocity_uses_retail_overbounce_for_inward_and_outward_planes(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	out_x = ctypes.c_float(0.0)
	out_y = ctypes.c_float(0.0)
	out_z = ctypes.c_float(0.0)

	assert pmove_fixture_harness.QLR_RunClipVelocityFrame(
		ctypes.c_float(100.0),
		ctypes.c_float(5.0),
		ctypes.c_float(-50.0),
		ctypes.c_float(0.0),
		ctypes.c_float(0.0),
		ctypes.c_float(1.0),
		ctypes.c_float(1.001),
		ctypes.byref(out_x),
		ctypes.byref(out_y),
		ctypes.byref(out_z),
	) == 0
	assert out_x.value == pytest.approx(100.0, rel=1e-6)
	assert out_y.value == pytest.approx(5.0, rel=1e-6)
	assert out_z.value == pytest.approx(0.05, rel=1e-4)

	assert pmove_fixture_harness.QLR_RunClipVelocityFrame(
		ctypes.c_float(10.0),
		ctypes.c_float(0.0),
		ctypes.c_float(50.0),
		ctypes.c_float(0.0),
		ctypes.c_float(0.0),
		ctypes.c_float(1.0),
		ctypes.c_float(2.0),
		ctypes.byref(out_x),
		ctypes.byref(out_y),
		ctypes.byref(out_z),
	) == 0
	assert out_x.value == pytest.approx(10.0, rel=1e-6)
	assert out_z.value == pytest.approx(25.0, rel=1e-6)


def test_accelerate_clamps_to_wishspeed_and_preserves_overspeed(pmove_fixture_harness: ctypes.CDLL) -> None:
	assert pmove_fixture_harness.QLR_RunAccelerateFrame(
		ctypes.c_float(0.0), ctypes.c_float(320.0), ctypes.c_float(10.0), ctypes.c_float(0.1)
	) == pytest.approx(320.0, rel=1e-6)
	assert pmove_fixture_harness.QLR_RunAccelerateFrame(
		ctypes.c_float(300.0), ctypes.c_float(320.0), ctypes.c_float(10.0), ctypes.c_float(0.1)
	) == pytest.approx(320.0, rel=1e-6)
	assert pmove_fixture_harness.QLR_RunAccelerateFrame(
		ctypes.c_float(400.0), ctypes.c_float(320.0), ctypes.c_float(10.0), ctypes.c_float(0.1)
	) == pytest.approx(400.0, rel=1e-6)


def test_cmdscale_preserves_speed_budget_across_axial_and_diagonal_input(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunCmdScaleFrame(0, 0, 0, 320) == pytest.approx(0.0, abs=1e-6)
	assert pmove_fixture_harness.QLR_RunCmdScaleFrame(127, 0, 0, 320) == pytest.approx(
		320.0 / 127.0, rel=1e-6
	)
	assert pmove_fixture_harness.QLR_RunCmdScaleFrame(127, 127, 0, 320) == pytest.approx(
		320.0 / (127.0 * 2.0 ** 0.5), rel=1e-6
	)
	assert pmove_fixture_harness.QLR_RunCmdScaleFrame(127, 127, 127, 320) == pytest.approx(
		320.0 / (127.0 * 3.0 ** 0.5), rel=1e-6
	)


def test_set_movement_dir_maps_retail_eight_way_ring_and_idle_side_snap(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(127, 0, 4) == 0
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(127, -127, 0) == 1
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(0, -127, 0) == 2
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(-127, -127, 0) == 3
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(-127, 0, 0) == 4
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(-127, 127, 0) == 5
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(0, 127, 0) == 6
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(127, 127, 0) == 7
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(0, 0, 2) == 1
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(0, 0, 6) == 7
	assert pmove_fixture_harness.QLR_RunSetMovementDirFrame(0, 0, 4) == 4


def test_circle_strafe_friction_prefers_the_retail_diagonal_branch(pmove_fixture_harness: ctypes.CDLL) -> None:
	straight_speed = pmove_fixture_harness.QLR_RunCircleStrafeFriction(0)
	diagonal_speed = pmove_fixture_harness.QLR_RunCircleStrafeFriction(1)

	assert straight_speed == pytest.approx(128.0, rel=1e-6)
	assert diagonal_speed == pytest.approx(144.0, rel=1e-6)
	assert diagonal_speed > straight_speed


def test_double_jump_reuse_requires_the_latch_to_clear(pmove_fixture_harness: ctypes.CDLL) -> None:
	first_velocity = ctypes.c_float(0.0)
	second_velocity = ctypes.c_float(0.0)
	third_velocity = ctypes.c_float(0.0)
	latch_after_first = ctypes.c_int(0)
	latch_after_second = ctypes.c_int(0)

	results = pmove_fixture_harness.QLR_RunDoubleJumpSequence(
		ctypes.byref(first_velocity),
		ctypes.byref(second_velocity),
		ctypes.byref(third_velocity),
		ctypes.byref(latch_after_first),
		ctypes.byref(latch_after_second),
	)

	assert results & 0x1
	assert not (results & 0x2)
	assert results & 0x4
	assert first_velocity.value == pytest.approx(275.0, rel=1e-6)
	assert second_velocity.value == pytest.approx(275.0, rel=1e-6)
	assert third_velocity.value == pytest.approx(275.0, rel=1e-6)
	assert latch_after_first.value == 1
	assert latch_after_second.value == 1


def test_ramp_jump_accumulates_vertical_velocity_before_the_retail_max_clamp(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunRampJumpVerticalTakeoff(
		ctypes.c_float(500.0),
		ctypes.c_float(1.0),
		ctypes.c_float(700.0),
	) == pytest.approx(700.0, rel=1e-6)
	assert pmove_fixture_harness.QLR_RunRampJumpVerticalTakeoff(
		ctypes.c_float(-50.0),
		ctypes.c_float(1.0),
		ctypes.c_float(700.0),
	) == pytest.approx(275.0, rel=1e-6)


def test_chainjump_integer_mode_selects_retail_takeoff_velocity_branch(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoff(0, 0) == pytest.approx(275.0, rel=1e-6)
	assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoff(1, 0) == pytest.approx(363.0, rel=1e-6)
	assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoff(2, 0) == pytest.approx(385.0, rel=1e-6)
	assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoff(2, 1) == pytest.approx(385.0, rel=1e-6)


def test_aircontrol_chainjump_override_fades_to_base_at_the_retail_threshold(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoffAtTime(0, 1, 100) == pytest.approx(
		385.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoffAtTime(2, 1, 400) == pytest.approx(
		330.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoffAtTime(2, 1, 500) == pytest.approx(
		275.0,
		rel=1e-6,
	)


def test_chainjump_takeoff_velocity_is_clamped_after_non_ramp_mode_math(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	for chain_mode, air_control in (
		(1, 0),
		(2, 0),
		(0, 1),
	):
		assert pmove_fixture_harness.QLR_RunChainJumpModeTakeoffWithMax(
			chain_mode,
			air_control,
			100,
			ctypes.c_float(300.0),
		) == pytest.approx(300.0, rel=1e-6)


def test_step_jump_takeoff_uses_the_step_additive_branch_for_both_retail_paths(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoff(2, 0, ctypes.c_float(700.0)) == pytest.approx(
		323.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoff(2, 1, ctypes.c_float(700.0)) == pytest.approx(
		323.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoff(2, 0, ctypes.c_float(300.0)) == pytest.approx(
		300.0,
		rel=1e-6,
	)


def test_step_jump_takeoff_covers_scale_and_aircontrol_profile_edges(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoffAtTime(1, 0, 0, 100, ctypes.c_float(700.0)) == pytest.approx(
		363.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoffAtTime(1, 1, 0, 100, ctypes.c_float(700.0)) == pytest.approx(
		363.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoffAtTime(0, 0, 1, 100, ctypes.c_float(700.0)) == pytest.approx(
		323.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoffAtTime(2, 1, 1, 400, ctypes.c_float(700.0)) == pytest.approx(
		299.0,
		rel=1e-6,
	)
	assert pmove_fixture_harness.QLR_RunStepJumpModeTakeoffAtTime(2, 0, 1, 500, ctypes.c_float(700.0)) == pytest.approx(
		275.0,
		rel=1e-6,
	)


def test_recovered_jump_release_flag_overrides_autohop_profile(pmove_fixture_harness: ctypes.CDLL) -> None:
	pmf_require_jump_release = 262144

	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, 0, 0) == 1
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, pmf_require_jump_release, 0) == 0
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(0, 0, 0, 0) == 0
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(0, 1, 0, 0) == 0
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, 0, 1) == 1
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, pmf_require_jump_release, 1) == 0


def test_jumppad_launch_latch_blocks_jump_gates_from_replacing_push_velocity(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	velocity_z = ctypes.c_float(0.0)
	upmove = ctypes.c_int(0)

	results = pmove_fixture_harness.QLR_RunJumpPadLaunchJumpProbe(
		ctypes.byref(velocity_z),
		ctypes.byref(upmove),
	)

	assert results == 0
	assert velocity_z.value == pytest.approx(800.0, rel=1e-6)
	assert upmove.value == 0


def test_jumppad_launch_latch_blocks_grounded_jump_from_replacing_push_velocity(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	velocity_z = ctypes.c_float(0.0)
	upmove = ctypes.c_int(0)

	accepted = pmove_fixture_harness.QLR_RunJumpPadLaunchGroundedJumpProbe(
		ctypes.byref(velocity_z),
		ctypes.byref(upmove),
	)

	assert accepted == 0
	assert velocity_z.value == pytest.approx(0.0, abs=1e-6)
	assert upmove.value == 0


def test_jumppad_launch_latch_blocks_air_step_ledge_grab(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	origin_z = ctypes.c_float(0.0)
	step_up = ctypes.c_float(0.0)
	velocity_z = ctypes.c_float(0.0)

	trace_calls = pmove_fixture_harness.QLR_RunJumpPadLaunchAirStep(
		ctypes.byref(origin_z),
		ctypes.byref(step_up),
		ctypes.byref(velocity_z),
	)

	assert trace_calls == 1
	assert origin_z.value == pytest.approx(0.0, rel=1e-6)
	assert step_up.value == pytest.approx(0.0, rel=1e-6)


def test_jumppad_launch_latch_blocks_generic_ground_plane_step_retry(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	origin_z = ctypes.c_float(0.0)
	step_up = ctypes.c_float(0.0)
	velocity_z = ctypes.c_float(0.0)

	trace_calls = pmove_fixture_harness.QLR_RunJumpPadLaunchGroundPlaneStep(
		ctypes.byref(origin_z),
		ctypes.byref(step_up),
		ctypes.byref(velocity_z),
	)

	assert trace_calls == 2
	assert step_up.value == pytest.approx(0.0, rel=1e-6)
	assert velocity_z.value > 0.0


def test_jumppad_launch_pmove_suppresses_held_jump_across_split_slices(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	pmf_jump_held = 2
	velocity_z = ctypes.c_float(0.0)
	upmove = ctypes.c_int(0)
	pm_flags = ctypes.c_int(0)

	double_jumped = pmove_fixture_harness.QLR_RunJumpPadLaunchPmoveHeldJump(
		ctypes.byref(velocity_z),
		ctypes.byref(upmove),
		ctypes.byref(pm_flags),
	)

	assert double_jumped == 0
	assert upmove.value == 0
	assert not (pm_flags.value & pmf_jump_held)
	assert velocity_z.value > 700.0


def test_unsupported_air_step_returns_before_the_step_up_probe(pmove_fixture_harness: ctypes.CDLL) -> None:
	origin_z = ctypes.c_float(0.0)
	step_up = ctypes.c_float(0.0)
	velocity_z = ctypes.c_float(0.0)

	trace_calls = pmove_fixture_harness.QLR_RunUnsupportedAirStep(
		ctypes.byref(origin_z),
		ctypes.byref(step_up),
		ctypes.byref(velocity_z),
	)

	assert trace_calls == 3
	assert origin_z.value == pytest.approx(0.0, rel=1e-6)
	assert step_up.value == pytest.approx(0.0, rel=1e-6)
	assert velocity_z.value == pytest.approx(0.0, rel=1e-6)


def test_ladder_probe_uses_the_retail_player_solid_trace_and_surface_flag(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	surf_ladder = 0x8
	mask_playersolid = 0x2010001
	content_mask = ctypes.c_int(0)

	assert pmove_fixture_harness.QLR_RunCheckLadderProbe(
		surf_ladder, ctypes.c_float(0.5), ctypes.byref(content_mask)
	) == 1
	assert content_mask.value == mask_playersolid
	assert pmove_fixture_harness.QLR_RunCheckLadderProbe(
		0, ctypes.c_float(0.5), ctypes.byref(content_mask)
	) == 0
	assert pmove_fixture_harness.QLR_RunCheckLadderProbe(
		surf_ladder, ctypes.c_float(1.0), ctypes.byref(content_mask)
	) == 0


def test_ladder_move_caps_explicit_vertical_input_to_retail_two_thirds_speed(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunLadderMoveVerticalVelocity(127) == pytest.approx(211.2, rel=1e-5)
	assert pmove_fixture_harness.QLR_RunLadderMoveVerticalVelocity(-127) == pytest.approx(-211.2, rel=1e-5)
	assert pmove_fixture_harness.QLR_RunLadderMoveVerticalVelocity(0) == pytest.approx(0.0, abs=1e-6)


def test_water_jump_probe_requires_two_deep_water_solid_lip_and_clearance(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	contents_solid = 1
	pmf_time_waterjump = 128
	velocity_x = ctypes.c_float(0.0)
	velocity_z = ctypes.c_float(0.0)
	pm_time = ctypes.c_int(0)
	pm_flags = ctypes.c_int(0)
	point_calls = ctypes.c_int(0)

	assert pmove_fixture_harness.QLR_RunWaterJumpProbe(
		2,
		contents_solid,
		0,
		ctypes.byref(velocity_x),
		ctypes.byref(velocity_z),
		ctypes.byref(pm_time),
		ctypes.byref(pm_flags),
		ctypes.byref(point_calls),
	) == 1
	assert velocity_x.value == pytest.approx(200.0, rel=1e-6)
	assert velocity_z.value == pytest.approx(350.0, rel=1e-6)
	assert pm_time.value == 2000
	assert pm_flags.value & pmf_time_waterjump
	assert point_calls.value == 2

	assert pmove_fixture_harness.QLR_RunWaterJumpProbe(
		1,
		contents_solid,
		0,
		ctypes.byref(velocity_x),
		ctypes.byref(velocity_z),
		ctypes.byref(pm_time),
		ctypes.byref(pm_flags),
		ctypes.byref(point_calls),
	) == 0
	assert point_calls.value == 0
	assert pmove_fixture_harness.QLR_RunWaterJumpProbe(
		2,
		0,
		0,
		ctypes.byref(velocity_x),
		ctypes.byref(velocity_z),
		ctypes.byref(pm_time),
		ctypes.byref(pm_flags),
		ctypes.byref(point_calls),
	) == 0
	assert point_calls.value == 1
	assert pmove_fixture_harness.QLR_RunWaterJumpProbe(
		2,
		contents_solid,
		contents_solid,
		ctypes.byref(velocity_x),
		ctypes.byref(velocity_z),
		ctypes.byref(pm_time),
		ctypes.byref(pm_flags),
		ctypes.byref(point_calls),
	) == 0
	assert point_calls.value == 2


def test_watermove_idle_path_uses_the_retail_sixty_unit_sink_vector(
	pmove_fixture_harness: ctypes.CDLL,
) -> None:
	assert pmove_fixture_harness.QLR_RunWaterMoveIdleSink() == pytest.approx(-24.0, rel=1e-6)


def test_active_crouch_slide_keeps_footsteps_on_the_retail_movement_branch(pmove_fixture_harness: ctypes.CDLL) -> None:
	active = pmove_fixture_harness.QLR_RunCrouchSlideFootstepFrame(200)
	inactive = pmove_fixture_harness.QLR_RunCrouchSlideFootstepFrame(0)

	assert (active >> 8) == 50
	assert (active & 1) == 1
	assert inactive == 0


def test_checkduck_clears_standing_crouch_slide_timer_with_retail_ground_plane_gate(pmove_fixture_harness: ctypes.CDLL) -> None:
	pmf_ducked = 1
	pmf_crouch_slide = 1048576
	slide_flags = pmf_ducked | pmf_crouch_slide

	assert pmove_fixture_harness.QLR_RunCheckDuckCrouchSlideStandClear(
		slide_flags, 250, 1, 0
	) == 0
	assert pmove_fixture_harness.QLR_RunCheckDuckCrouchSlideStandClear(
		slide_flags, 250, 0, 1
	) == 250
	assert pmove_fixture_harness.QLR_RunCheckDuckCrouchSlideStandClear(
		pmf_ducked, 250, 1, 1
	) == 250


def test_dead_players_keep_foot_water_events_but_suppress_head_water_events(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	pm_dead = 3

	assert pmove_fixture_harness.QLR_RunWaterEventsFrame(pm_normal, 0, 3, 0) == 0x020B0D
	assert pmove_fixture_harness.QLR_RunWaterEventsFrame(pm_dead, 0, 3, 0) == 0x010B00
	assert pmove_fixture_harness.QLR_RunWaterEventsFrame(pm_normal, 3, 0, 0) == 0x020C0E
	assert pmove_fixture_harness.QLR_RunWaterEventsFrame(pm_dead, 3, 0, 0) == 0x010C00
	assert pmove_fixture_harness.QLR_RunWaterEventsFrame(pm_normal, 3, 0, 1) == 0x010C00
	assert pmove_fixture_harness.QLR_RunWaterEventsFrame(pm_normal, 3, 2, 0) == 0x010E00
	assert pmove_fixture_harness.QLR_RunWaterEventsFrame(pm_normal, 3, 2, 1) == 0x000000


def test_no_footsteps_is_owned_by_the_retail_surface_selector(pmove_fixture_harness: ctypes.CDLL) -> None:
	surf_metalsteps = 0x1000
	surf_snowsteps = 0x80000
	surf_woodsteps = 0x100000

	assert pmove_fixture_harness.QLR_RunFootstepSurfaceEvent(0, 0) == 1
	assert pmove_fixture_harness.QLR_RunFootstepSurfaceEvent(0, surf_metalsteps) == 2
	assert pmove_fixture_harness.QLR_RunFootstepSurfaceEvent(0, surf_snowsteps) == 81
	assert pmove_fixture_harness.QLR_RunFootstepSurfaceEvent(0, surf_woodsteps) == 82
	assert pmove_fixture_harness.QLR_RunFootstepSurfaceEvent(1, 0) == 0
	assert pmove_fixture_harness.QLR_RunFootstepSurfaceEvent(1, surf_woodsteps) == 0
	assert pmove_fixture_harness.QLR_RunNoFootstepsCycleFrame(0) == 0x101
	assert pmove_fixture_harness.QLR_RunNoFootstepsCycleFrame(1) == 0x100


def test_non_walking_footsteps_need_retail_axis_velocity_threshold(pmove_fixture_harness: ctypes.CDLL) -> None:
	bob_shift = 24
	event_sequence_shift = 16
	event_shift = 8

	slow_diagonal = pmove_fixture_harness.QLR_RunFootstepVelocityGateFrame(31.0, 31.0, 0)
	run_x = pmove_fixture_harness.QLR_RunFootstepVelocityGateFrame(32.0, 0.0, 0)
	run_y = pmove_fixture_harness.QLR_RunFootstepVelocityGateFrame(0.0, -32.0, 0)
	back_slow = pmove_fixture_harness.QLR_RunFootstepVelocityGateFrame(-31.0, 0.0, 1)
	back_run = pmove_fixture_harness.QLR_RunFootstepVelocityGateFrame(-32.0, 0.0, 1)

	assert (slow_diagonal >> bob_shift) == 70
	assert (slow_diagonal >> event_sequence_shift) & 0xff == 0
	assert (slow_diagonal >> event_shift) & 0xff == 0
	assert (slow_diagonal & 0xff) == 2
	assert (run_x >> bob_shift) == 80
	assert (run_x >> event_sequence_shift) & 0xff == 1
	assert (run_x >> event_shift) & 0xff == 1
	assert (run_x & 0xff) == 1
	assert (run_y >> event_sequence_shift) & 0xff == 1
	assert (run_y & 0xff) == 1
	assert (back_slow >> bob_shift) == 70
	assert (back_slow >> event_sequence_shift) & 0xff == 0
	assert (back_slow & 0xff) == 4
	assert (back_run >> event_sequence_shift) & 0xff == 1
	assert (back_run & 0xff) == 3


def test_crash_land_suppresses_events_at_the_retail_gib_health_boundary(pmove_fixture_harness: ctypes.CDLL) -> None:
	event_sequence_shift = 24
	event_shift = 16
	legs_timer_shift = 8

	alive_enough = pmove_fixture_harness.QLR_RunCrashLandHealthGate(-39)
	gib_limited = pmove_fixture_harness.QLR_RunCrashLandHealthGate(-40)

	assert (alive_enough >> event_sequence_shift) & 0xff == 1
	assert (alive_enough >> event_shift) & 0xff == 6
	assert (alive_enough >> legs_timer_shift) & 0xff == 130
	assert alive_enough & 0xff == 0
	assert (gib_limited >> event_sequence_shift) & 0xff == 0
	assert (gib_limited >> event_shift) & 0xff == 0
	assert (gib_limited >> legs_timer_shift) & 0xff == 130
	assert gib_limited & 0xff == 0


def test_crash_land_clears_double_jump_latch_only_on_the_retail_landing_path(pmove_fixture_harness: ctypes.CDLL) -> None:
	pmf_double_jump = 131072

	assert pmove_fixture_harness.QLR_RunCrashLandDoubleJumpLatch(
		pmf_double_jump, 1, -300.0
	) == 0
	assert pmove_fixture_harness.QLR_RunCrashLandDoubleJumpLatch(
		0, 1, -300.0
	) == 1
	assert pmove_fixture_harness.QLR_RunCrashLandDoubleJumpLatch(
		pmf_double_jump, 1, -50.0
	) == 1


def test_drop_timers_sanitizes_nonzero_crouch_slide_timer_under_retail_gate(pmove_fixture_harness: ctypes.CDLL) -> None:
	pmf_crouch_slide = 1048576

	assert pmove_fixture_harness.QLR_RunDropTimersCrouchSlide(
		pmf_crouch_slide, 1, 250, 100
	) == 150
	assert pmove_fixture_harness.QLR_RunDropTimersCrouchSlide(
		pmf_crouch_slide, 1, 75, 100
	) == 0
	assert pmove_fixture_harness.QLR_RunDropTimersCrouchSlide(
		pmf_crouch_slide, 1, -25, 100
	) == 0
	assert pmove_fixture_harness.QLR_RunDropTimersCrouchSlide(
		pmf_crouch_slide, 0, -25, 100
	) == -25
	assert pmove_fixture_harness.QLR_RunDropTimersCrouchSlide(
		0, 1, -25, 100
	) == -25


def _run_drop_timers_frame(
	pmove_fixture_harness: ctypes.CDLL,
	pm_flags: int,
	pm_time: int,
	legs_timer: int,
	torso_timer: int,
	crouch_slide_time: int,
	ground_plane: int,
	msec: int,
) -> tuple[int, int, int, int, int]:
	out_flags = ctypes.c_int(0)
	out_pm_time = ctypes.c_int(0)
	out_legs_timer = ctypes.c_int(0)
	out_torso_timer = ctypes.c_int(0)
	out_crouch_slide_time = ctypes.c_int(0)

	assert pmove_fixture_harness.QLR_RunDropTimersFrame(
		pm_flags,
		pm_time,
		legs_timer,
		torso_timer,
		crouch_slide_time,
		ground_plane,
		msec,
		ctypes.byref(out_flags),
		ctypes.byref(out_pm_time),
		ctypes.byref(out_legs_timer),
		ctypes.byref(out_torso_timer),
		ctypes.byref(out_crouch_slide_time),
	) == 0
	return (
		out_flags.value,
		out_pm_time.value,
		out_legs_timer.value,
		out_torso_timer.value,
		out_crouch_slide_time.value,
	)


def test_drop_timers_clears_time_flags_only_when_misc_timer_expires(pmove_fixture_harness: ctypes.CDLL) -> None:
	pmf_all_times = 32 | 64 | 128
	pmf_respawned = 512
	flags = pmf_all_times | pmf_respawned

	assert _run_drop_timers_frame(
		pmove_fixture_harness, flags, 250, 0, 0, 0, 0, 100
	) == (flags, 150, 0, 0, 0)
	assert _run_drop_timers_frame(
		pmove_fixture_harness, flags, 100, 0, 0, 0, 0, 100
	) == (pmf_respawned, 0, 0, 0, 0)
	assert _run_drop_timers_frame(
		pmove_fixture_harness, flags, 50, 0, 0, 0, 0, 100
	) == (pmf_respawned, 0, 0, 0, 0)


def test_drop_timers_clamps_animation_timers_independently(pmove_fixture_harness: ctypes.CDLL) -> None:
	pmf_respawned = 512

	assert _run_drop_timers_frame(
		pmove_fixture_harness, pmf_respawned, 0, 150, 250, 0, 0, 100
	) == (pmf_respawned, 0, 50, 150, 0)
	assert _run_drop_timers_frame(
		pmove_fixture_harness, pmf_respawned, 0, 40, 60, 0, 0, 100
	) == (pmf_respawned, 0, 0, 0, 0)


def test_freeze_view_angles_follow_the_retail_update_gate(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	pm_spectator = 2
	pm_freeze = 4
	pm_intermission = 5

	assert pmove_fixture_harness.QLR_RunUpdateViewAnglesGate(pm_normal, 0) == 0
	assert pmove_fixture_harness.QLR_RunUpdateViewAnglesGate(pm_normal, 100) == 1
	assert pmove_fixture_harness.QLR_RunUpdateViewAnglesGate(pm_spectator, 0) == 1
	assert pmove_fixture_harness.QLR_RunUpdateViewAnglesGate(pm_freeze, 0) == 1
	assert pmove_fixture_harness.QLR_RunUpdateViewAnglesGate(pm_intermission, 100) == 0
	assert pmove_fixture_harness.QLR_RunFreezePmoveViewAngles() == 0x7


def test_invulnerability_walk_handoff_bypasses_the_regular_jump_gate(pmove_fixture_harness: ctypes.CDLL) -> None:
	assert pmove_fixture_harness.QLR_RunInvulnerabilityWalkFrame() == 0x7


def test_invulnerability_timer_gate_uses_retail_zero_exactness(pmove_fixture_harness: ctypes.CDLL) -> None:
	assert pmove_fixture_harness.QLR_RunInvulnerabilityTimerGateFrame(0, 10000) == 0x2
	assert pmove_fixture_harness.QLR_RunInvulnerabilityTimerGateFrame(-5, 10000) == 0x7
	assert pmove_fixture_harness.QLR_RunInvulnerabilityTimerGateFrame(0, 0) == 0x5


def test_firing_flag_is_cleared_before_retail_early_returns(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	pm_spectator = 2
	wp_machinegun = 2
	button_attack = 1
	pmf_respawned = 512

	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_spectator, 100, wp_machinegun, 10, button_attack, 0
	) == 0
	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_normal, 0, wp_machinegun, 10, button_attack, 0
	) == 0
	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_normal, 100, wp_machinegun, 10, button_attack, pmf_respawned
	) == 0


def test_pm_weapon_re_latches_firing_only_after_alive_attack_ammo_gates(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	wp_machinegun = 2
	button_attack = 1
	pmf_attack_lockout = 4
	pmf_weapon_reset = 32768

	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_normal, 100, wp_machinegun, 10, button_attack, 0
	) == 0x100
	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_normal, 100, wp_machinegun, 10, button_attack, pmf_attack_lockout
	) == 0
	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_normal, 100, wp_machinegun, 10, button_attack, pmf_weapon_reset
	) == 0
	assert pmove_fixture_harness.QLR_RunWeaponResetFrame() == 0
	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_normal, 100, wp_machinegun, 0, button_attack, 0
	) == 0
	assert pmove_fixture_harness.QLR_RunFiringFlagFrame(
		pm_normal, 100, wp_machinegun, 10, 0, 0
	) == 0


def test_dead_player_body_tracemask_respects_the_retail_invulnerability_gate(pmove_fixture_harness: ctypes.CDLL) -> None:
	assert pmove_fixture_harness.QLR_RunDeadTraceMaskFrame(0) == 0
	assert pmove_fixture_harness.QLR_RunDeadTraceMaskFrame(1) == 1


def _run_animate_frame(
	pmove_fixture_harness: ctypes.CDLL, buttons: int, initial_torso_timer: int = 0
) -> tuple[int, int, int, int]:
	torso_anim = ctypes.c_int(0)
	torso_timer = ctypes.c_int(0)
	event_sequence = ctypes.c_int(0)
	event_id = ctypes.c_int(0)

	assert pmove_fixture_harness.QLR_RunAnimateButtonFrame(
		buttons,
		initial_torso_timer,
		ctypes.byref(torso_anim),
		ctypes.byref(torso_timer),
		ctypes.byref(event_sequence),
		ctypes.byref(event_id),
	) == 0
	return torso_anim.value, torso_timer.value, event_sequence.value, event_id.value


def test_animate_gesture_has_retail_priority_and_queues_taunt(pmove_fixture_harness: ctypes.CDLL) -> None:
	button_gesture = 8
	button_getflag = 128
	button_negative = 64
	torso_gesture = 6
	timer_gesture = 34 * 66 + 50
	ev_taunt = 74

	assert _run_animate_frame(
		pmove_fixture_harness, button_gesture | button_getflag | button_negative
	) == (torso_gesture, timer_gesture, 1, ev_taunt)


def test_animate_voice_buttons_use_retail_order_and_short_timer(pmove_fixture_harness: ctypes.CDLL) -> None:
	button_getflag = 128
	button_guardbase = 256
	button_patrol = 512
	button_followme = 1024
	button_affirmative = 32
	button_negative = 64

	assert _run_animate_frame(
		pmove_fixture_harness,
		button_getflag | button_guardbase | button_patrol | button_followme | button_affirmative | button_negative,
	) == (25, 600, 0, 0)

	for buttons, torso_anim in (
		(button_getflag, 25),
		(button_guardbase, 26),
		(button_patrol, 27),
		(button_followme, 28),
		(button_affirmative, 29),
		(button_negative, 30),
	):
		assert _run_animate_frame(pmove_fixture_harness, buttons) == (torso_anim, 600, 0, 0)


def test_animate_torso_timer_blocks_gesture_and_voice_buttons(pmove_fixture_harness: ctypes.CDLL) -> None:
	button_gesture = 8
	button_getflag = 128
	torso_stand = 11

	assert _run_animate_frame(pmove_fixture_harness, button_gesture | button_getflag, 25) == (
		torso_stand,
		25,
		0,
		0,
	)


def _run_torso_animation_frame(
	pmove_fixture_harness: ctypes.CDLL,
	pm_type: int,
	weapon_state: int,
	weapon: int,
	initial_torso_anim: int,
	initial_torso_timer: int = 0,
) -> tuple[int, int]:
	torso_anim = ctypes.c_int(0)
	torso_timer = ctypes.c_int(0)

	assert pmove_fixture_harness.QLR_RunTorsoAnimationFrame(
		pm_type,
		weapon_state,
		weapon,
		initial_torso_anim,
		initial_torso_timer,
		ctypes.byref(torso_anim),
		ctypes.byref(torso_timer),
	) == 0
	return torso_anim.value, torso_timer.value


def test_torso_animation_restores_ready_idle_by_weapon(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	weapon_ready = 0
	wp_gauntlet = 1
	wp_machinegun = 2
	torso_attack = 7
	torso_stand = 11
	torso_stand2 = 12

	assert _run_torso_animation_frame(
		pmove_fixture_harness, pm_normal, weapon_ready, wp_gauntlet, torso_attack
	) == (torso_stand2, 0)
	assert _run_torso_animation_frame(
		pmove_fixture_harness, pm_normal, weapon_ready, wp_machinegun, torso_attack
	) == (torso_stand, 0)


def test_torso_animation_respects_timer_state_and_player_life_gate(pmove_fixture_harness: ctypes.CDLL) -> None:
	pm_normal = 0
	pm_dead = 3
	weapon_ready = 0
	weapon_firing = 3
	wp_machinegun = 2
	torso_attack = 7

	assert _run_torso_animation_frame(
		pmove_fixture_harness, pm_normal, weapon_ready, wp_machinegun, torso_attack, 75
	) == (torso_attack, 75)
	assert _run_torso_animation_frame(
		pmove_fixture_harness, pm_normal, weapon_firing, wp_machinegun, torso_attack
	) == (torso_attack, 0)
	assert _run_torso_animation_frame(
		pmove_fixture_harness, pm_dead, weapon_ready, wp_machinegun, torso_attack
	) == (torso_attack, 0)


def test_weapon_change_accepts_the_retail_no_weapon_sentinel(pmove_fixture_harness: ctypes.CDLL) -> None:
	assert pmove_fixture_harness.QLR_RunWeaponSentinelChangeFrame() == 0x1F


def test_weapon_reload_scaling_keeps_the_retail_scout_refire_ratio(pmove_fixture_harness: ctypes.CDLL) -> None:
	pw_none = 0
	pw_haste = 3
	pw_scout = 10
	pw_ammoregen = 13

	assert pmove_fixture_harness.QLR_RunWeaponReloadScaleFrame(pw_none, 0) == 800
	assert pmove_fixture_harness.QLR_RunWeaponReloadScaleFrame(pw_scout, 0) == 640
	assert pmove_fixture_harness.QLR_RunWeaponReloadScaleFrame(pw_ammoregen, 0) == 615
	assert pmove_fixture_harness.QLR_RunWeaponReloadScaleFrame(pw_none, 1) == 615
	assert pmove_fixture_harness.QLR_RunWeaponReloadScaleFrame(pw_scout, 1) == 640


def test_weapon_chaingun_spinup_matches_retail_timer_paths(pmove_fixture_harness: ctypes.CDLL) -> None:
	def unpack(value: int) -> tuple[int, int]:
		return (value >> 16) & 0xffff, value & 0xffff

	assert unpack(pmove_fixture_harness.QLR_RunChaingunSpinFrame(0, 1, 0)) == (100, 100)
	assert unpack(pmove_fixture_harness.QLR_RunChaingunSpinFrame(1000, 1, 0)) == (50, 1000)
	assert unpack(pmove_fixture_harness.QLR_RunChaingunSpinFrame(950, 1, 0)) == (100, 1000)
	assert unpack(pmove_fixture_harness.QLR_RunChaingunSpinFrame(250, 0, 0)) == (0, 150)
	assert unpack(pmove_fixture_harness.QLR_RunChaingunSpinFrame(250, 1, 1)) == (0, 150)
