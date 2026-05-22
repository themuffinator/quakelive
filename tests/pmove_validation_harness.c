#include <math.h>
#include <string.h>

#include "q_shared.h"
#include "bg_public.h"
#include "bg_local.h"

#if defined(_WIN32)
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

typedef enum {
	QLR_TRACE_FLAT_GROUND = 1,
	QLR_TRACE_FREE_AIR,
	QLR_TRACE_STEP_UNSUPPORTED,
	QLR_TRACE_STEP_SUPPORTED,
	QLR_TRACE_CROUCH_STEP_FALLBACK
} qlr_trace_mode_t;

typedef struct {
	float	originZ;
	float	stepUp;
} qlr_step_result_t;

typedef struct {
	float	velocityZ;
	float	originZ;
	float	stepUp;
	int	jumpTime;
	int	upmove;
	int	pmFlags;
	int	traceCalls;
} qlr_crouch_step_result_t;

typedef struct {
	float	firstJumpVelocity;
	float	reuseJumpVelocity;
	int	doubleJumped;
	int	eventSequence;
} qlr_double_jump_result_t;

typedef struct {
	int	weaponPrimary;
	int	fov;
	int	forwardmove;
	int	rightmove;
	int	upmove;
} qlr_command_mirror_result_t;

static qlr_trace_mode_t	qlr_traceMode;
static int		qlr_traceCallCount;

void PmoveSingle( pmove_t *pmove );

/*
=============
Com_Printf

Test stub that discards log messages during pmove fixture runs.
=============
*/
void Com_Printf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
trap_SnapVector

Stubbed trap call used by movement helpers.
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
QLR_SetTraceResult

Seeds one synthetic trace result for the pmove harness.
=============
*/
static void QLR_SetTraceResult( trace_t *results, float fraction, const vec3_t endpos, const vec3_t normal, int surfaceFlags, int contents, int entityNum ) {
	memset( results, 0, sizeof( *results ) );
	results->fraction = fraction;
	VectorCopy( endpos, results->endpos );
	VectorCopy( normal, results->plane.normal );
	results->plane.type = PlaneTypeForNormal( results->plane.normal );
	results->surfaceFlags = surfaceFlags;
	results->contents = contents;
	results->entityNum = entityNum;
}

/*
=============
QLR_ResetTraceMode

Resets the synthetic trace dispatcher for a new fixture scenario.
=============
*/
static void QLR_ResetTraceMode( qlr_trace_mode_t mode ) {
	qlr_traceMode = mode;
	qlr_traceCallCount = 0;
}

/*
=============
QLR_TestTrace

Provides deterministic trace responses for the focused pmove fixtures.
=============
*/
static void QLR_TestTrace( trace_t *results, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, int passEntityNum, int contentMask ) {
	vec3_t	upNormal;
	vec3_t	wallNormal;
	vec3_t	traceEnd;
	int	callIndex;

	(void)maxs;
	(void)passEntityNum;
	(void)contentMask;

	VectorSet( upNormal, 0.0f, 0.0f, 1.0f );
	VectorSet( wallNormal, 1.0f, 0.0f, 0.0f );
	callIndex = ++qlr_traceCallCount;

	if ( qlr_traceMode == QLR_TRACE_CROUCH_STEP_FALLBACK && callIndex >= 5 ) {
		if ( mins[0] > -15.0f ) {
			VectorCopy( end, traceEnd );
			QLR_SetTraceResult( results, 1.0f, traceEnd, upNormal, 0, 0, ENTITYNUM_NONE );
		} else {
			VectorSet( traceEnd, 5.0f, 0.0f, 10.0f );
			QLR_SetTraceResult( results, 0.5f, traceEnd, upNormal, 0, CONTENTS_SOLID, ENTITYNUM_WORLD );
		}
		return;
	}

	switch ( qlr_traceMode ) {
	case QLR_TRACE_FLAT_GROUND:
		if ( end[2] < start[2] && start[2] <= 0.0f ) {
			VectorCopy( start, traceEnd );
			QLR_SetTraceResult( results, 0.0f, traceEnd, upNormal, 0, CONTENTS_SOLID, ENTITYNUM_WORLD );
			return;
		}

		QLR_SetTraceResult( results, 1.0f, end, upNormal, 0, 0, ENTITYNUM_NONE );
		return;

	case QLR_TRACE_FREE_AIR:
		QLR_SetTraceResult( results, 1.0f, end, upNormal, 0, 0, ENTITYNUM_NONE );
		return;

	case QLR_TRACE_STEP_UNSUPPORTED:
	case QLR_TRACE_STEP_SUPPORTED:
	case QLR_TRACE_CROUCH_STEP_FALLBACK:
		switch ( callIndex ) {
		case 1:
			VectorSet( traceEnd, 5.0f, 0.0f, 5.0f );
			QLR_SetTraceResult( results, 0.5f, traceEnd, wallNormal, 0, CONTENTS_SOLID, ENTITYNUM_WORLD );
			return;

		case 2:
			VectorCopy( end, traceEnd );
			QLR_SetTraceResult( results, 1.0f, traceEnd, upNormal, 0, 0, ENTITYNUM_NONE );
			return;

		case 3:
			if ( qlr_traceMode == QLR_TRACE_CROUCH_STEP_FALLBACK ) {
				VectorSet( traceEnd, 10.0f, 0.0f, 10.0f );
			} else {
				VectorSet( traceEnd, 5.0f, 0.0f, 5.0f );
			}
			QLR_SetTraceResult( results, 0.5f, traceEnd, wallNormal, 0, CONTENTS_SOLID, ENTITYNUM_WORLD );
			return;

		case 4:
			if ( qlr_traceMode == QLR_TRACE_STEP_SUPPORTED ) {
				VectorSet( traceEnd, 5.0f, 0.0f, -6.0f );
				QLR_SetTraceResult( results, 0.5f, traceEnd, upNormal, 0, CONTENTS_SOLID, ENTITYNUM_WORLD );
			} else if ( qlr_traceMode == QLR_TRACE_CROUCH_STEP_FALLBACK ) {
				VectorSet( traceEnd, 10.0f, 0.0f, 10.0f );
				QLR_SetTraceResult( results, 0.5f, traceEnd, upNormal, 0, CONTENTS_SOLID, ENTITYNUM_WORLD );
			} else {
				VectorCopy( end, traceEnd );
				QLR_SetTraceResult( results, 1.0f, traceEnd, upNormal, 0, 0, ENTITYNUM_NONE );
			}
			return;

		case 5:
			if ( qlr_traceMode == QLR_TRACE_CROUCH_STEP_FALLBACK ) {
				VectorSet( traceEnd, 5.0f, 0.0f, 10.0f );
				QLR_SetTraceResult( results, 0.5f, traceEnd, upNormal, 0, CONTENTS_SOLID, ENTITYNUM_WORLD );
			} else {
				VectorCopy( end, traceEnd );
				QLR_SetTraceResult( results, 1.0f, traceEnd, upNormal, 0, 0, ENTITYNUM_NONE );
			}
			return;

		case 6:
			VectorCopy( end, traceEnd );
			QLR_SetTraceResult( results, 1.0f, traceEnd, upNormal, 0, 0, ENTITYNUM_NONE );
			return;

		case 7:
			VectorSet( traceEnd, 10.0f, 0.0f, 10.0f );
			QLR_SetTraceResult( results, 1.0f, traceEnd, upNormal, 0, 0, ENTITYNUM_NONE );
			return;

		default:
			VectorCopy( end, traceEnd );
			QLR_SetTraceResult( results, 1.0f, traceEnd, upNormal, 0, 0, ENTITYNUM_NONE );
			return;
		}

	default:
		QLR_SetTraceResult( results, 1.0f, end, upNormal, 0, 0, ENTITYNUM_NONE );
		return;
	}
}

/*
=============
QLR_TestPointContents

Reports an empty pointcontents result for the focused pmove fixtures.
=============
*/
static int QLR_TestPointContents( const vec3_t point, int passEntityNum ) {
	(void)point;
	(void)passEntityNum;
	return 0;
}

/*
=============
QLR_ResetPmove

Initialises one local pmove state block with retail defaults.
=============
*/
static void QLR_ResetPmove( pmove_t *localPM, playerState_t *localPS, pmove_settings_t *localSettings ) {
	memset( localPM, 0, sizeof( *localPM ) );
	memset( localPS, 0, sizeof( *localPS ) );
	memset( localSettings, 0, sizeof( *localSettings ) );
	memset( &pml, 0, sizeof( pml ) );

	*localSettings = *PM_GetDefaultSettings();

	localPM->ps = localPS;
	localPM->pmoveSettings = localSettings;
	localPM->trace = QLR_TestTrace;
	localPM->pointcontents = QLR_TestPointContents;
	localPM->tracemask = MASK_PLAYERSOLID;

	localPS->pm_type = PM_NORMAL;
	localPS->clientNum = 0;
	localPS->gravity = 800;
	localPS->speed = 320;
}

/*
=============
QLR_RunCircleStrafeFrictionScenario

Runs one grounded pmove frame and returns the resulting planar speed.
=============
*/
QLR_EXPORT float QLR_RunCircleStrafeFrictionScenario( int diagonalInput ) {
	pmove_t		localPM;
	playerState_t	localPS;
	pmove_settings_t	localSettings;

	QLR_ResetPmove( &localPM, &localPS, &localSettings );
	QLR_ResetTraceMode( QLR_TRACE_FLAT_GROUND );

	localPS.origin[2] = 0.0f;
	localPS.velocity[0] = 500.0f;
	localPS.velocity[1] = 0.0f;
	localPS.velocity[2] = 0.0f;

	localSettings.airControl = 150.0f;
	localSettings.walkAccel = 0.0f;
	localSettings.walkFriction = 6.0f;
	localSettings.circleStrafeFriction = 5.5f;
	localPS.pm_flags |= PMF_AIR_CONTROL;

	localPM.cmd.serverTime = 16;
	localPM.cmd.forwardmove = 127;
	localPM.cmd.rightmove = diagonalInput ? 127 : 0;
	localPM.cmd.upmove = 0;

	PmoveSingle( &localPM );

	return sqrtf( localPS.velocity[0] * localPS.velocity[0] + localPS.velocity[1] * localPS.velocity[1] );
}

/*
=============
QLR_RunAirStepScenario

Runs the public PM_StepSlideMove entry point under the air-step support probe.
=============
*/
QLR_EXPORT void QLR_RunAirStepScenario( int supported, qlr_step_result_t *outResult ) {
	pmove_t		localPM;
	playerState_t	localPS;
	pmove_settings_t	localSettings;
	pmove_t		*previousPM;
	int		previousAirSteps;
	float		previousStepHeight;

	if ( !outResult ) {
		return;
	}

	QLR_ResetPmove( &localPM, &localPS, &localSettings );
	QLR_ResetTraceMode( supported ? QLR_TRACE_STEP_SUPPORTED : QLR_TRACE_STEP_UNSUPPORTED );

	VectorSet( localPM.mins, -15.0f, -15.0f, MINS_Z );
	VectorSet( localPM.maxs, 15.0f, 15.0f, 32.0f );

	localPS.origin[0] = 0.0f;
	localPS.origin[1] = 0.0f;
	localPS.origin[2] = 0.0f;
	localPS.velocity[0] = 100.0f;
	localPS.velocity[1] = 0.0f;
	localPS.velocity[2] = 100.0f;

	localPM.cmd.serverTime = 100;
	localPM.cmd.upmove = 0;

	pml.frametime = 0.1f;
	pml.msec = 100;
	pml.groundPlane = qfalse;
	pml.walking = qfalse;

	previousPM = pm;
	pm = &localPM;
	previousAirSteps = pm_airsteps;
	previousStepHeight = pm_stepHeight;
	pm_airsteps = 0;
	pm_stepHeight = localSettings.stepHeight;

	PM_StepSlideMove( qfalse );

	pm = previousPM;
	pm_airsteps = previousAirSteps;
	pm_stepHeight = previousStepHeight;

	outResult->originZ = localPS.origin[2];
	outResult->stepUp = pml.stepUp;
}

/*
=============
QLR_RunCrouchStepFallbackScenario

Runs the retail crouch-step fallback after the general step-jump gate clears
queued upmove and returns the resulting takeoff state.
=============
*/
QLR_EXPORT void QLR_RunCrouchStepFallbackScenario( qlr_crouch_step_result_t *outResult ) {
	pmove_t		localPM;
	playerState_t	localPS;
	pmove_settings_t	localSettings;
	pmove_t		*previousPM;
	int		previousAirSteps;
	float		previousStepHeight;

	if ( !outResult ) {
		return;
	}

	memset( outResult, 0, sizeof( *outResult ) );
	QLR_ResetPmove( &localPM, &localPS, &localSettings );
	QLR_ResetTraceMode( QLR_TRACE_CROUCH_STEP_FALLBACK );

	VectorSet( localPM.mins, -15.0f, -15.0f, MINS_Z );
	VectorSet( localPM.maxs, 15.0f, 15.0f, 32.0f );

	localPS.origin[0] = 0.0f;
	localPS.origin[1] = 0.0f;
	localPS.origin[2] = 0.0f;
	localPS.velocity[0] = 100.0f;
	localPS.velocity[1] = 0.0f;
	localPS.velocity[2] = 100.0f;
	localPS.pm_flags = PMF_DUCKED | PMF_JUMP_HELD;
	localPS.jumpTime = 0;

	localSettings.stepJump = qtrue;
	localSettings.crouchStepJump = qtrue;
	localSettings.jumpTimeDeltaMin = 100.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localSettings.stepJumpVelocity = 48.0f;

	localPM.cmd.serverTime = 100;
	localPM.cmd.upmove = 0;

	pml.frametime = 0.1f;
	pml.msec = 100;
	pml.groundPlane = qfalse;
	pml.walking = qfalse;

	previousPM = pm;
	pm = &localPM;
	previousAirSteps = pm_airsteps;
	previousStepHeight = pm_stepHeight;
	pm_airsteps = 1;
	pm_stepHeight = localSettings.stepHeight;

	PM_StepSlideMove( qfalse );

	outResult->velocityZ = localPS.velocity[2];
	outResult->originZ = localPS.origin[2];
	outResult->stepUp = pml.stepUp;
	outResult->jumpTime = localPS.jumpTime;
	outResult->upmove = localPM.cmd.upmove;
	outResult->pmFlags = localPS.pm_flags;
	outResult->traceCalls = qlr_traceCallCount;

	pm = previousPM;
	pm_airsteps = previousAirSteps;
	pm_stepHeight = previousStepHeight;
}

/*
=============
QLR_RunAirDoubleJumpSequence

Runs a jump, release, and reuse probe entirely in free air to validate the
retail double-jump latch.
=============
*/
QLR_EXPORT void QLR_RunAirDoubleJumpSequence( qlr_double_jump_result_t *outResult ) {
	pmove_t		localPM;
	playerState_t	localPS;
	pmove_settings_t	localSettings;

	if ( !outResult ) {
		return;
	}

	memset( outResult, 0, sizeof( *outResult ) );
	QLR_ResetPmove( &localPM, &localPS, &localSettings );
	QLR_ResetTraceMode( QLR_TRACE_FREE_AIR );

	localPS.origin[2] = 128.0f;
	localPS.velocity[2] = 0.0f;
	localPS.commandTime = 984;

	localSettings.doubleJump = qtrue;
	localSettings.jumpTimeDeltaMin = 0.0f;
	localSettings.jumpVelocity = 275.0f;
	localSettings.jumpVelocityMax = 700.0f;
	localPS.pm_flags |= PMF_DOUBLE_JUMP;

	localPM.cmd.forwardmove = 0;
	localPM.cmd.rightmove = 0;
	localPM.cmd.upmove = 20;
	localPM.cmd.serverTime = 1000;
	PmoveSingle( &localPM );

	outResult->firstJumpVelocity = localPS.velocity[2];

	localPM.cmd.upmove = 0;
	localPM.cmd.serverTime = 1016;
	PmoveSingle( &localPM );

	localPM.cmd.upmove = 20;
	localPM.cmd.serverTime = 1032;
	PmoveSingle( &localPM );

	outResult->reuseJumpVelocity = localPS.velocity[2];
	outResult->doubleJumped = localPS.doubleJumped;
	outResult->eventSequence = localPS.eventSequence;
}

/*
=============
QLR_RunCommandMirrorScenario

Runs one pmove frame and captures the retail playerstate command-axis mirrors.
=============
*/
QLR_EXPORT void QLR_RunCommandMirrorScenario( qlr_command_mirror_result_t *outResult ) {
	pmove_t		localPM;
	playerState_t	localPS;
	pmove_settings_t	localSettings;

	if ( !outResult ) {
		return;
	}

	memset( outResult, 0, sizeof( *outResult ) );
	QLR_ResetPmove( &localPM, &localPS, &localSettings );
	QLR_ResetTraceMode( QLR_TRACE_FREE_AIR );

	localPM.cmd.weaponPrimary = 14;
	localPM.cmd.fov = 110;
	localPM.cmd.forwardmove = -127;
	localPM.cmd.rightmove = 64;
	localPM.cmd.upmove = -12;
	localPM.cmd.serverTime = 16;

	PmoveSingle( &localPM );

	outResult->weaponPrimary = localPS.weaponPrimary;
	outResult->fov = localPS.fov;
	outResult->forwardmove = localPS.forwardmove;
	outResult->rightmove = localPS.rightmove;
	outResult->upmove = localPS.upmove;
}
