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
} qlr_trace_mode_t;

#ifdef _WIN32
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

static qlr_trace_mode_t qlr_trace_mode;
static int qlr_trace_call_count;

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
	(void)contentMask;

	memset( trace, 0, sizeof( *trace ) );
	trace->fraction = 1.0f;
	VectorCopy( end, trace->endpos );
	VectorSet( trace->plane.normal, 0.0f, 0.0f, 1.0f );

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
	localPS.playerItemTime = 10000;
	localPS.playerItemTimeMax = 10000;
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
	library.QLR_RunHeldJumpGate.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunHeldJumpGate.restype = ctypes.c_int
	library.QLR_RunUnsupportedAirStep.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	library.QLR_RunUnsupportedAirStep.restype = ctypes.c_int
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
	library.QLR_RunUpdateViewAnglesGate.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunUpdateViewAnglesGate.restype = ctypes.c_int
	library.QLR_RunFreezePmoveViewAngles.argtypes = []
	library.QLR_RunFreezePmoveViewAngles.restype = ctypes.c_int
	library.QLR_RunInvulnerabilityWalkFrame.argtypes = []
	library.QLR_RunInvulnerabilityWalkFrame.restype = ctypes.c_int
	library.QLR_RunFiringFlagFrame.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_RunFiringFlagFrame.restype = ctypes.c_int
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


def test_recovered_jump_release_flag_overrides_autohop_profile(pmove_fixture_harness: ctypes.CDLL) -> None:
	pmf_require_jump_release = 262144

	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, 0, 0) == 1
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, pmf_require_jump_release, 0) == 0
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(0, 0, 0, 0) == 0
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, 0, 1) == 1
	assert pmove_fixture_harness.QLR_RunHeldJumpGate(1, 0, pmf_require_jump_release, 1) == 0


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
