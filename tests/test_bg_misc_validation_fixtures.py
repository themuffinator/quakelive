from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_DIR = REPO_ROOT / "src" / "code" / "game"
HARNESS_PATH = REPO_ROOT / "tests" / "bg_misc_validation_harness.c"

SOURCES = [
	HARNESS_PATH,
	GAME_DIR / "bg_misc.c",
	GAME_DIR / "bg_lib.c",
	GAME_DIR / "q_math.c",
	GAME_DIR / "q_shared.c",
]

PW_NONE = 0
PW_REDFLAG = 7
PW_BLUEFLAG = 8
PW_NEUTRALFLAG = 9
PW_SCOUT = 10
PW_GUARD = 11
PW_DOUBLER = 12
PW_AMMOREGEN = 13
PW_INVULNERABILITY = 14


def _find_c_compiler() -> str:
	compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
	if not compiler:
		pytest.skip("No C compiler found for bg_misc validation fixtures")

	return compiler


@pytest.fixture(scope="session")
def bg_misc_validation_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("bg_misc_validation_harness")
	lib_path = build_dir / ("bg_misc_validation_harness.dll" if os.name == "nt" else "libbg_misc_validation_harness.so")
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
	library.QLR_GetPowerupItemClassname.argtypes = [ctypes.c_int]
	library.QLR_GetPowerupItemClassname.restype = ctypes.c_char_p
	library.QLR_PlayerTouchesItemByClassname.argtypes = [
		ctypes.c_char_p,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
	]
	library.QLR_PlayerTouchesItemByClassname.restype = ctypes.c_int
	library.QLR_CanGrabDroppedSelfWeaponAfterDelay.argtypes = [ctypes.c_int]
	library.QLR_CanGrabDroppedSelfWeaponAfterDelay.restype = ctypes.c_int
	library.QLR_CanGrabOwnedWeaponWithAmmo.argtypes = [ctypes.c_int]
	library.QLR_CanGrabOwnedWeaponWithAmmo.restype = ctypes.c_int
	library.QLR_CanGrabAmmoPack.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_CanGrabAmmoPack.restype = ctypes.c_int
	library.QLR_CanGrabHealthItem.argtypes = [ctypes.c_char_p, ctypes.c_int]
	library.QLR_CanGrabHealthItem.restype = ctypes.c_int
	library.QLR_CanGrabCtfFlag.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_CanGrabCtfFlag.restype = ctypes.c_int
	return library


def test_powerup_lookup_fixture_keeps_retail_remaps(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_INVULNERABILITY) == b"holdable_invulnerability"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_SCOUT) == b"item_scout"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_GUARD) == b"item_guard"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_DOUBLER) == b"item_doubler"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_AMMOREGEN) == b"item_armorregen"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_REDFLAG) == b"team_CTF_redflag"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_BLUEFLAG) == b"team_CTF_blueflag"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_NEUTRALFLAG) == b"team_CTF_neutralflag"
	assert bg_misc_validation_harness.QLR_GetPowerupItemClassname(PW_NONE) is None


def test_player_touch_fixture_preserves_regular_and_flag_vertical_bounds(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_PlayerTouchesItemByClassname(b"item_health", 36.0, 0.0, 29.0) == 1
	assert bg_misc_validation_harness.QLR_PlayerTouchesItemByClassname(b"item_health", 37.0, 0.0, 29.0) == 0
	assert bg_misc_validation_harness.QLR_PlayerTouchesItemByClassname(b"item_health", 0.0, 0.0, 30.0) == 0
	assert bg_misc_validation_harness.QLR_PlayerTouchesItemByClassname(b"team_CTF_redflag", 0.0, 0.0, 64.0) == 1
	assert bg_misc_validation_harness.QLR_PlayerTouchesItemByClassname(b"team_CTF_redflag", 0.0, 0.0, 65.0) == 0
	assert bg_misc_validation_harness.QLR_PlayerTouchesItemByClassname(b"item_health", 0.0, 0.0, -50.0) == 1
	assert bg_misc_validation_harness.QLR_PlayerTouchesItemByClassname(b"item_health", 0.0, 0.0, -51.0) == 0


def test_dropped_self_weapon_fixture_keeps_the_retail_grace_window(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_CanGrabDroppedSelfWeaponAfterDelay(999) == 0
	assert bg_misc_validation_harness.QLR_CanGrabDroppedSelfWeaponAfterDelay(1000) == 1


def test_weapon_and_ammo_pickup_fixtures_preserve_retail_gates(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_CanGrabOwnedWeaponWithAmmo(5) == 0
	assert bg_misc_validation_harness.QLR_CanGrabOwnedWeaponWithAmmo(0) == 1
	assert bg_misc_validation_harness.QLR_CanGrabAmmoPack(1, 200, 1, 19) == 1
	assert bg_misc_validation_harness.QLR_CanGrabAmmoPack(1, 200, 1, 20) == 0


def test_health_and_team_item_fixtures_cover_shared_pickup_switch_cases(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_CanGrabHealthItem(b"item_health", 99) == 1
	assert bg_misc_validation_harness.QLR_CanGrabHealthItem(b"item_health", 100) == 0
	assert bg_misc_validation_harness.QLR_CanGrabHealthItem(b"item_health_small", 199) == 1
	assert bg_misc_validation_harness.QLR_CanGrabHealthItem(b"item_health_small", 200) == 0
	assert bg_misc_validation_harness.QLR_CanGrabHealthItem(b"item_health_mega", 199) == 1
	assert bg_misc_validation_harness.QLR_CanGrabHealthItem(b"item_health_mega", 200) == 0
	assert bg_misc_validation_harness.QLR_CanGrabCtfFlag(1, PW_NONE, PW_BLUEFLAG, 0) == 1
	assert bg_misc_validation_harness.QLR_CanGrabCtfFlag(1, PW_NONE, PW_REDFLAG, 0) == 0
	assert bg_misc_validation_harness.QLR_CanGrabCtfFlag(1, PW_BLUEFLAG, PW_REDFLAG, 0) == 1
	assert bg_misc_validation_harness.QLR_CanGrabCtfFlag(1, PW_NONE, PW_REDFLAG, 1) == 1
