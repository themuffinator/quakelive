from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_DIR = REPO_ROOT / "src" / "code" / "game"

C_SOURCE = r"""
#include <stdarg.h>
#include <string.h>

#define PM_StepSlideMove QLR_PM_StepSlideMove_Stub
#define PM_SlideMove QLR_PM_SlideMove_Stub

#include "q_shared.h"
#include "bg_public.h"

#ifdef WIN32
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

/*
=============
Com_Printf

Test stub that discards movement diagnostics.
=============
*/
void Com_Printf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
trap_SnapVector

Stubbed trap call used by the movement helpers.
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
QLR_PM_StepSlideMove_Stub

Suppresses slide-move side effects so the air-control fixtures isolate the
retail tuning branches inside bg_pmove.c.
=============
*/
void QLR_PM_StepSlideMove_Stub( qboolean gravity ) {
	(void)gravity;
}

/*
=============
QLR_PM_SlideMove_Stub

Suppresses the adjacent water or ladder move dependency when the shared pmove
translation unit is compiled directly into the harness.
=============
*/
qboolean QLR_PM_SlideMove_Stub( qboolean gravity ) {
	(void)gravity;
	return qfalse;
}

#include "bg_pmove.c"

/*
=============
QLR_LoadAirControlTuning

Loads the retail pmove tuning globals from one synthetic settings block and
returns the resolved values to the Python harness.
=============
*/
QLR_EXPORT void QLR_LoadAirControlTuning(
	float airControlValue,
	float airAccelValue,
	float airStopAccelValue,
	float strafeAccelValue,
	float wishSpeedValue,
	float walkAccelValue,
	int airStepsValue,
	float *outValues
) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;

	memset( &localPM, 0, sizeof( localPM ) );
	memset( &localPS, 0, sizeof( localPS ) );
	memset( &localSettings, 0, sizeof( localSettings ) );
	memset( &pml, 0, sizeof( pml ) );

	localPM.ps = &localPS;
	localPM.pmoveSettings = &localSettings;
	pm = &localPM;

	localSettings = *PM_GetDefaultSettings();
	localSettings.airControl = airControlValue;
	localSettings.airAccel = airAccelValue;
	localSettings.airStopAccel = airStopAccelValue;
	localSettings.strafeAccel = strafeAccelValue;
	localSettings.wishSpeed = wishSpeedValue;
	localSettings.walkAccel = walkAccelValue;
	localSettings.airSteps = airStepsValue;

	PM_LoadMoveTuningConstants();

	outValues[0] = pm_accelerate;
	outValues[1] = pm_airaccelerate;
	outValues[2] = pm_aircontrol;
	outValues[3] = (float)pm_airsteps;
	outValues[4] = pm_airstopaccelerate;
	outValues[5] = pm_strafeaccelerate;
	outValues[6] = pm_wishspeed;
}

/*
=============
QLR_RunAirMove

Runs the retail PM_AirMove body with a controlled command and returns the
resolved velocity plus the jump-side effects used by the parity fixtures.
=============
*/
QLR_EXPORT void QLR_RunAirMove(
	float airControlValue,
	int doubleJumpEnabled,
	float velocityX,
	float velocityY,
	float velocityZ,
	int forwardMove,
	int rightMove,
	int upMove,
	float frameTime,
	int alreadyDoubleJumped,
	int jumpHeld,
	float *outVelocity,
	int *outDoubleJumped,
	int *outJumpTime
) {
	static pmove_t localPM;
	static playerState_t localPS;
	static pmove_settings_t localSettings;

	memset( &localPM, 0, sizeof( localPM ) );
	memset( &localPS, 0, sizeof( localPS ) );
	memset( &localSettings, 0, sizeof( localSettings ) );
	memset( &pml, 0, sizeof( pml ) );

	localPM.ps = &localPS;
	localPM.pmoveSettings = &localSettings;
	localPM.cmd.serverTime = 1000;
	localPM.cmd.forwardmove = (signed char)forwardMove;
	localPM.cmd.rightmove = (signed char)rightMove;
	localPM.cmd.upmove = (signed char)upMove;
	pm = &localPM;

	localSettings = *PM_GetDefaultSettings();
	localSettings.airControl = airControlValue;
	localSettings.doubleJump = doubleJumpEnabled ? qtrue : qfalse;
	localSettings.autoHop = qfalse;
	localSettings.bunnyHop = qfalse;

	localPS.speed = 320;
	localPS.velocity[0] = velocityX;
	localPS.velocity[1] = velocityY;
	localPS.velocity[2] = velocityZ;
	localPS.doubleJumped = alreadyDoubleJumped ? qtrue : qfalse;
	if ( jumpHeld ) {
		localPS.pm_flags |= PMF_JUMP_HELD;
	}

	pml.frametime = frameTime;
	pml.forward[0] = 1.0f;
	pml.right[1] = 1.0f;

	PM_LoadMoveTuningConstants();
	PM_AirMove();

	outVelocity[0] = localPS.velocity[0];
	outVelocity[1] = localPS.velocity[1];
	outVelocity[2] = localPS.velocity[2];
	*outDoubleJumped = localPS.doubleJumped ? 1 : 0;
	*outJumpTime = localPS.jumpTime;
}
"""


def _build_test_library(tmp_path: Path) -> Path:
	src_path = tmp_path / "pmove_air_control_runtime_test.c"
	src_path.write_text(C_SOURCE, encoding="utf-8")

	if os.name == "nt":
		clang = shutil.which("clang")
		if clang is None:
			pytest.skip("clang is required to build the pmove air-control harness on Windows")

		lib_path = tmp_path / "pmove_air_control_runtime_test.dll"
		compile_cmd = [
			clang,
			"-DWIN32",
			"-D_CRT_SECURE_NO_WARNINGS",
			"-std=c99",
			"-shared",
			"-fuse-ld=lld",
			"-Wno-return-type",
			"-Wno-deprecated-declarations",
			"-I",
			str(GAME_DIR),
			"-o",
			str(lib_path),
			str(src_path),
			str(GAME_DIR / "bg_misc.c"),
			str(GAME_DIR / "bg_lib.c"),
			str(GAME_DIR / "q_math.c"),
			str(GAME_DIR / "q_shared.c"),
		]
	elif sys.platform == "darwin":
		cc = shutil.which("cc")
		if cc is None:
			pytest.skip("cc is required to build the pmove air-control harness")

		lib_path = tmp_path / "libpmove_air_control_runtime_test.dylib"
		compile_cmd = [
			cc,
			"-std=c99",
			"-dynamiclib",
			"-I",
			str(GAME_DIR),
			"-o",
			str(lib_path),
			str(src_path),
			str(GAME_DIR / "bg_misc.c"),
			str(GAME_DIR / "bg_lib.c"),
			str(GAME_DIR / "q_math.c"),
			str(GAME_DIR / "q_shared.c"),
		]
	else:
		cc = shutil.which("cc")
		if cc is None:
			pytest.skip("cc is required to build the pmove air-control harness")

		lib_path = tmp_path / "libpmove_air_control_runtime_test.so"
		compile_cmd = [
			cc,
			"-std=c99",
			"-shared",
			"-fPIC",
			"-I",
			str(GAME_DIR),
			"-o",
			str(lib_path),
			str(src_path),
			str(GAME_DIR / "bg_misc.c"),
			str(GAME_DIR / "bg_lib.c"),
			str(GAME_DIR / "q_math.c"),
			str(GAME_DIR / "q_shared.c"),
		]

	subprocess.run(compile_cmd, check=True)
	return lib_path


@pytest.fixture(scope="module")
def air_control_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	lib_path = _build_test_library(tmp_path_factory.mktemp("pmove_air_control_runtime"))
	library = ctypes.CDLL(str(lib_path))

	library.QLR_LoadAirControlTuning.argtypes = [
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_float),
	]
	library.QLR_LoadAirControlTuning.restype = None

	library.QLR_RunAirMove.argtypes = [
		ctypes.c_float,
		ctypes.c_int,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_float,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	library.QLR_RunAirMove.restype = None

	return library


def test_air_control_bundle_promotes_stock_values_to_the_retail_profile( air_control_library: ctypes.CDLL ) -> None:
	default_values = ( ctypes.c_float * 7 )()
	air_control_library.QLR_LoadAirControlTuning(
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 1.0 ),
		ctypes.c_float( 1.0 ),
		ctypes.c_float( 1.0 ),
		ctypes.c_float( 400.0 ),
		ctypes.c_float( 10.0 ),
		ctypes.c_int( 1 ),
		default_values,
	)

	assert default_values[0] == pytest.approx( 10.0, rel=1e-6 )
	assert default_values[1] == pytest.approx( 1.0, rel=1e-6 )
	assert default_values[2] == pytest.approx( 0.0, rel=1e-6 )
	assert default_values[3] == pytest.approx( 1.0, rel=1e-6 )
	assert default_values[4] == pytest.approx( 1.0, rel=1e-6 )
	assert default_values[5] == pytest.approx( 1.0, rel=1e-6 )
	assert default_values[6] == pytest.approx( 400.0, rel=1e-6 )

	air_control_values = ( ctypes.c_float * 7 )()
	air_control_library.QLR_LoadAirControlTuning(
		ctypes.c_float( 150.0 ),
		ctypes.c_float( 1.0 ),
		ctypes.c_float( 1.0 ),
		ctypes.c_float( 1.0 ),
		ctypes.c_float( 400.0 ),
		ctypes.c_float( 10.0 ),
		ctypes.c_int( 1 ),
		air_control_values,
	)

	assert air_control_values[0] == pytest.approx( 15.0, rel=1e-6 )
	assert air_control_values[1] == pytest.approx( 1.1, rel=1e-6 )
	assert air_control_values[2] == pytest.approx( 150.0, rel=1e-6 )
	assert air_control_values[3] == pytest.approx( 3.0, rel=1e-6 )
	assert air_control_values[4] == pytest.approx( 2.5, rel=1e-6 )
	assert air_control_values[5] == pytest.approx( 70.0, rel=1e-6 )
	assert air_control_values[6] == pytest.approx( 35.0, rel=1e-6 )


def test_air_control_bundle_keeps_non_stock_overrides_when_the_profile_switch_is_enabled( air_control_library: ctypes.CDLL ) -> None:
	custom_values = ( ctypes.c_float * 7 )()
	air_control_library.QLR_LoadAirControlTuning(
		ctypes.c_float( 150.0 ),
		ctypes.c_float( 2.0 ),
		ctypes.c_float( 3.0 ),
		ctypes.c_float( 80.0 ),
		ctypes.c_float( 40.0 ),
		ctypes.c_float( 17.0 ),
		ctypes.c_int( 4 ),
		custom_values,
	)

	assert custom_values[0] == pytest.approx( 17.0, rel=1e-6 )
	assert custom_values[1] == pytest.approx( 2.0, rel=1e-6 )
	assert custom_values[2] == pytest.approx( 150.0, rel=1e-6 )
	assert custom_values[3] == pytest.approx( 4.0, rel=1e-6 )
	assert custom_values[4] == pytest.approx( 3.0, rel=1e-6 )
	assert custom_values[5] == pytest.approx( 80.0, rel=1e-6 )
	assert custom_values[6] == pytest.approx( 40.0, rel=1e-6 )


def test_air_move_preserves_reverse_speed_while_using_retail_air_stop_accel( air_control_library: ctypes.CDLL ) -> None:
	velocity = ( ctypes.c_float * 3 )()
	double_jumped = ctypes.c_int()
	jump_time = ctypes.c_int()

	air_control_library.QLR_RunAirMove(
		ctypes.c_float( 150.0 ),
		ctypes.c_int( 0 ),
		ctypes.c_float( -100.0 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_int( 127 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 0 ),
		ctypes.c_float( 0.01 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 0 ),
		velocity,
		ctypes.byref( double_jumped ),
		ctypes.byref( jump_time ),
	)

	assert velocity[0] == pytest.approx( -92.0, rel=1e-6 )
	assert velocity[1] == pytest.approx( 0.0, abs=1e-6 )
	assert velocity[2] == pytest.approx( 0.0, abs=1e-6 )
	assert double_jumped.value == 0
	assert jump_time.value == 0


def test_air_move_uses_retail_strafe_accel_and_wishspeed_clamp( air_control_library: ctypes.CDLL ) -> None:
	velocity = ( ctypes.c_float * 3 )()
	double_jumped = ctypes.c_int()
	jump_time = ctypes.c_int()

	air_control_library.QLR_RunAirMove(
		ctypes.c_float( 150.0 ),
		ctypes.c_int( 0 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 127 ),
		ctypes.c_int( 0 ),
		ctypes.c_float( 0.02 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 0 ),
		velocity,
		ctypes.byref( double_jumped ),
		ctypes.byref( jump_time ),
	)

	assert velocity[0] == pytest.approx( 0.0, abs=1e-6 )
	assert velocity[1] == pytest.approx( 35.0, rel=1e-6 )
	assert velocity[2] == pytest.approx( 0.0, abs=1e-6 )
	assert double_jumped.value == 0
	assert jump_time.value == 0


def test_air_move_allows_one_retail_double_jump_and_rejects_reuse( air_control_library: ctypes.CDLL ) -> None:
	accepted_velocity = ( ctypes.c_float * 3 )()
	accepted_double_jumped = ctypes.c_int()
	accepted_jump_time = ctypes.c_int()

	air_control_library.QLR_RunAirMove(
		ctypes.c_float( 0.0 ),
		ctypes.c_int( 1 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 24.0 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 20 ),
		ctypes.c_float( 0.01 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 0 ),
		accepted_velocity,
		ctypes.byref( accepted_double_jumped ),
		ctypes.byref( accepted_jump_time ),
	)

	assert accepted_velocity[2] == pytest.approx( 275.0, rel=1e-6 )
	assert accepted_double_jumped.value == 1
	assert accepted_jump_time.value == 1000

	reused_velocity = ( ctypes.c_float * 3 )()
	reused_double_jumped = ctypes.c_int()
	reused_jump_time = ctypes.c_int()

	air_control_library.QLR_RunAirMove(
		ctypes.c_float( 0.0 ),
		ctypes.c_int( 1 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 0.0 ),
		ctypes.c_float( 24.0 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 0 ),
		ctypes.c_int( 20 ),
		ctypes.c_float( 0.01 ),
		ctypes.c_int( 1 ),
		ctypes.c_int( 0 ),
		reused_velocity,
		ctypes.byref( reused_double_jumped ),
		ctypes.byref( reused_jump_time ),
	)

	assert reused_velocity[2] == pytest.approx( 24.0, rel=1e-6 )
	assert reused_double_jumped.value == 1
	assert reused_jump_time.value == 0
