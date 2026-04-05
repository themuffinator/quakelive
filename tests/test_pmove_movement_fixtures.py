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
	library.QLR_RunUnsupportedAirStep.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	library.QLR_RunUnsupportedAirStep.restype = ctypes.c_int
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
