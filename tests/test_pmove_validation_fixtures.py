from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_DIR = REPO_ROOT / "src" / "code" / "game"
HARNESS_PATH = REPO_ROOT / "tests" / "pmove_validation_harness.c"

SOURCES = [
	HARNESS_PATH,
	GAME_DIR / "bg_pmove.c",
	GAME_DIR / "bg_slidemove.c",
	GAME_DIR / "bg_lib.c",
	GAME_DIR / "bg_misc.c",
	GAME_DIR / "q_math.c",
	GAME_DIR / "q_shared.c",
]


class StepResult(ctypes.Structure):
	_fields_ = [
		("originZ", ctypes.c_float),
		("stepUp", ctypes.c_float),
	]


class DoubleJumpResult(ctypes.Structure):
	_fields_ = [
		("firstJumpVelocity", ctypes.c_float),
		("reuseJumpVelocity", ctypes.c_float),
		("doubleJumped", ctypes.c_int),
		("eventSequence", ctypes.c_int),
	]


def _find_c_compiler() -> str:
	compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
	if not compiler:
		pytest.skip("No C compiler found for pmove validation fixtures")

	return compiler


def _expected_ground_speed(speed: float, friction: float, frametime: float, stop_speed: float = 100.0) -> float:
	control = stop_speed if speed < stop_speed else speed
	newspeed = speed - control * friction * frametime
	return max(newspeed, 0.0)


@pytest.fixture(scope="session")
def pmove_validation_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("pmove_validation_harness")
	lib_path = build_dir / ("pmove_validation_harness.dll" if os.name == "nt" else "libpmove_validation_harness.so")
	compile_args = [_find_c_compiler(), "-std=c99", "-shared"]

	if os.name != "nt":
		compile_args.append("-fPIC")
	else:
		compile_args.extend(["-DWIN32", "-D_CRT_SECURE_NO_WARNINGS", "-Wno-return-type"])

	compile_cmd = [
		*compile_args,
		"-Isrc/common",
		"-Isrc/code",
		"-Isrc/code/game",
		"-Isrc/code/qcommon",
		*[str(source) for source in SOURCES],
		"-o",
		str(lib_path),
	]
	subprocess.check_call(compile_cmd, cwd=REPO_ROOT)

	library = ctypes.CDLL(str(lib_path))
	library.QLR_RunCircleStrafeFrictionScenario.argtypes = [ctypes.c_int]
	library.QLR_RunCircleStrafeFrictionScenario.restype = ctypes.c_float
	library.QLR_RunAirStepScenario.argtypes = [ctypes.c_int, ctypes.POINTER(StepResult)]
	library.QLR_RunAirStepScenario.restype = None
	library.QLR_RunAirDoubleJumpSequence.argtypes = [ctypes.POINTER(DoubleJumpResult)]
	library.QLR_RunAirDoubleJumpSequence.restype = None
	return library


def test_circle_strafe_friction_fixture_uses_the_retail_diagonal_branch(
	pmove_validation_harness: ctypes.CDLL,
) -> None:
	straight_speed = pmove_validation_harness.QLR_RunCircleStrafeFrictionScenario(0)
	circle_speed = pmove_validation_harness.QLR_RunCircleStrafeFrictionScenario(1)

	assert straight_speed == pytest.approx(_expected_ground_speed(500.0, 6.0, 0.016), rel=1e-5)
	assert circle_speed > straight_speed


def test_air_step_suppression_fixture_requires_projected_support(
	pmove_validation_harness: ctypes.CDLL,
) -> None:
	unsupported = StepResult()
	supported = StepResult()

	pmove_validation_harness.QLR_RunAirStepScenario(0, ctypes.byref(unsupported))
	pmove_validation_harness.QLR_RunAirStepScenario(1, ctypes.byref(supported))

	assert unsupported.stepUp == pytest.approx(0.0, abs=1e-6)
	assert supported.stepUp == pytest.approx(10.0, rel=1e-5)
	assert supported.stepUp > unsupported.stepUp


def test_air_double_jump_fixture_blocks_reuse_until_ground_contact(
	pmove_validation_harness: ctypes.CDLL,
) -> None:
	result = DoubleJumpResult()

	pmove_validation_harness.QLR_RunAirDoubleJumpSequence(ctypes.byref(result))

	assert result.firstJumpVelocity == pytest.approx(275.0, rel=1e-5)
	assert result.reuseJumpVelocity < result.firstJumpVelocity
	assert result.doubleJumped == 1
	assert result.eventSequence == 1
