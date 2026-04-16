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

PW_QUAD = 1
PW_REDFLAG = 7
PW_BLUEFLAG = 8
PW_NEUTRALFLAG = 9
PW_SCOUT = 10
PW_GUARD = 11
PW_DOUBLER = 12
PW_AMMOREGEN = 13
PW_INVULNERABILITY = 14

C_SOURCE = r"""
#include <stdarg.h>
#include <string.h>

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

Test stub that discards diagnostics from the shared bg_misc helpers.
=============
*/
void Com_Printf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
trap_SnapVector

Stubbed trap call used by the shared trajectory helpers.
=============
*/
void trap_SnapVector( float *v ) {
	(void)v;
}

/*
=============
Com_Error

Minimal error stub for bg_misc runtime fixtures.
=============
*/
void Com_Error( int level, const char *fmt, ... ) {
	(void)level;
	(void)fmt;
}

/*
=============
QLR_FindItemIndexByClassname

Resolves one bg_itemlist row by classname and returns its retail item index.
=============
*/
QLR_EXPORT int QLR_FindItemIndexByClassname( const char *classname ) {
	gitem_t	*item;

	item = BG_FindItemByClassname( classname );
	if ( !item ) {
		return -1;
	}

	return ITEM_INDEX( item );
}

/*
=============
QLR_FindItemIndexForPowerup

Returns the retail bg_itemlist row used by one powerup lookup request.
=============
*/
QLR_EXPORT int QLR_FindItemIndexForPowerup( int powerup ) {
	gitem_t	*item;

	item = BG_FindItemForPowerup( (powerup_t)powerup );
	if ( !item ) {
		return -1;
	}

	return ITEM_INDEX( item );
}

/*
=============
QLR_PlayerTouchesItemAt

Runs BG_PlayerTouchesItem against a stationary item positioned at the origin.
=============
*/
QLR_EXPORT int QLR_PlayerTouchesItemAt( int itemIndex, float playerX, float playerY, float playerZ ) {
	playerState_t	ps;
	entityState_t	item;

	memset( &ps, 0, sizeof( ps ) );
	memset( &item, 0, sizeof( item ) );

	ps.origin[0] = playerX;
	ps.origin[1] = playerY;
	ps.origin[2] = playerZ;

	item.modelindex = itemIndex;
	item.pos.trType = TR_STATIONARY;

	return BG_PlayerTouchesItem( &ps, &item, 0 ) ? 1 : 0;
}

/*
=============
QLR_CanGrabRocketLauncherCase

Exercises representative BG_CanItemBeGrabbed weapon gates for one rocket item.
=============
*/
QLR_EXPORT int QLR_CanGrabRocketLauncherCase(
	int ownsWeapon,
	int ammoCount,
	int ironsights,
	int dropped,
	int sameClient,
	int currentTime,
	int dropTime
) {
	playerState_t	ps;
	entityState_t	ent;
	int		itemIndex;

	memset( &ps, 0, sizeof( ps ) );
	memset( &ent, 0, sizeof( ent ) );

	itemIndex = QLR_FindItemIndexByClassname( "weapon_rocketlauncher" );
	if ( itemIndex < 0 ) {
		return -1;
	}

	ps.clientNum = 3;
	if ( ownsWeapon ) {
		ps.stats[STAT_WEAPONS] |= ( 1 << WP_ROCKET_LAUNCHER );
	}
	ps.ammo[WP_ROCKET_LAUNCHER] = ammoCount;
	if ( ironsights ) {
		ps.pm_flags |= PMF_IRONSIGHTS;
	}

	ent.modelindex = itemIndex;
	ent.modelindex2 = dropped ? 1 : 0;
	ent.otherEntityNum = sameClient ? ps.clientNum : ( ps.clientNum + 1 );
	ent.time2 = dropTime;

	return BG_CanItemBeGrabbed( GT_FFA, currentTime, &ent, &ps ) ? 1 : 0;
}

/*
=============
QLR_CanGrabHealthCase

Runs the shared health pickup gate for the supplied item and player state.
=============
*/
QLR_EXPORT int QLR_CanGrabHealthCase( int itemIndex, int health, int maxHealth ) {
	playerState_t	ps;
	entityState_t	ent;

	memset( &ps, 0, sizeof( ps ) );
	memset( &ent, 0, sizeof( ent ) );

	ps.stats[STAT_HEALTH] = health;
	ps.stats[STAT_MAX_HEALTH] = maxHealth;
	ent.modelindex = itemIndex;

	return BG_CanItemBeGrabbed( GT_FFA, 0, &ent, &ps ) ? 1 : 0;
}
"""


def _build_test_library(tmp_path: Path) -> Path:
	src_path = tmp_path / "bg_misc_runtime_test.c"
	src_path.write_text(C_SOURCE, encoding="utf-8")

	if os.name == "nt":
		clang = shutil.which("clang")
		if clang is None:
			pytest.skip("clang is required to build the bg_misc runtime harness on Windows")

		lib_path = tmp_path / "bg_misc_runtime_test.dll"
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
			pytest.skip("cc is required to build the bg_misc runtime harness")

		lib_path = tmp_path / "libbg_misc_runtime_test.dylib"
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
			pytest.skip("cc is required to build the bg_misc runtime harness")

		lib_path = tmp_path / "libbg_misc_runtime_test.so"
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
def bg_misc_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	lib_path = _build_test_library(tmp_path_factory.mktemp("bg_misc_runtime"))
	library = ctypes.CDLL(str(lib_path))

	library.QLR_FindItemIndexByClassname.argtypes = [ctypes.c_char_p]
	library.QLR_FindItemIndexByClassname.restype = ctypes.c_int

	library.QLR_FindItemIndexForPowerup.argtypes = [ctypes.c_int]
	library.QLR_FindItemIndexForPowerup.restype = ctypes.c_int

	library.QLR_PlayerTouchesItemAt.argtypes = [
		ctypes.c_int,
		ctypes.c_float,
		ctypes.c_float,
		ctypes.c_float,
	]
	library.QLR_PlayerTouchesItemAt.restype = ctypes.c_int

	library.QLR_CanGrabRocketLauncherCase.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_CanGrabRocketLauncherCase.restype = ctypes.c_int

	library.QLR_CanGrabHealthCase.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_CanGrabHealthCase.restype = ctypes.c_int

	return library


def _item_index(bg_misc_library: ctypes.CDLL, classname: str) -> int:
	return bg_misc_library.QLR_FindItemIndexByClassname(classname.encode("ascii"))


def test_find_item_for_powerup_keeps_the_retail_special_case_routes(bg_misc_library: ctypes.CDLL) -> None:
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_INVULNERABILITY) == _item_index(
		bg_misc_library, "holdable_invulnerability"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_QUAD) == _item_index(
		bg_misc_library, "item_quad"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_SCOUT) == _item_index(
		bg_misc_library, "item_scout"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_GUARD) == _item_index(
		bg_misc_library, "item_guard"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_DOUBLER) == _item_index(
		bg_misc_library, "item_doubler"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_AMMOREGEN) == _item_index(
		bg_misc_library, "item_armorregen"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_REDFLAG) == _item_index(
		bg_misc_library, "team_CTF_redflag"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_BLUEFLAG) == _item_index(
		bg_misc_library, "team_CTF_blueflag"
	)
	assert bg_misc_library.QLR_FindItemIndexForPowerup(PW_NEUTRALFLAG) == _item_index(
		bg_misc_library, "team_CTF_neutralflag"
	)


def test_player_touches_item_matches_retail_vertical_pickup_bounds(bg_misc_library: ctypes.CDLL) -> None:
	health_index = _item_index(bg_misc_library, "item_health")
	flag_index = _item_index(bg_misc_library, "team_CTF_redflag")

	assert bg_misc_library.QLR_PlayerTouchesItemAt(health_index, 36.0, 0.0, 29.0) == 1
	assert bg_misc_library.QLR_PlayerTouchesItemAt(health_index, 37.0, 0.0, 0.0) == 0
	assert bg_misc_library.QLR_PlayerTouchesItemAt(health_index, 0.0, 0.0, -50.0) == 1
	assert bg_misc_library.QLR_PlayerTouchesItemAt(health_index, 0.0, 0.0, -51.0) == 0
	assert bg_misc_library.QLR_PlayerTouchesItemAt(flag_index, 0.0, 0.0, 64.0) == 1
	assert bg_misc_library.QLR_PlayerTouchesItemAt(flag_index, 0.0, 0.0, 65.0) == 0


def test_can_item_be_grabbed_keeps_the_normal_weapon_and_health_gates(
	bg_misc_library: ctypes.CDLL,
) -> None:
	mega_index = _item_index(bg_misc_library, "item_health_mega")
	health_index = _item_index(bg_misc_library, "item_health")
	small_health_index = _item_index(bg_misc_library, "item_health_small")

	assert bg_misc_library.QLR_CanGrabRocketLauncherCase(1, 10, 0, 0, 0, 0, 0) == 1
	assert bg_misc_library.QLR_CanGrabRocketLauncherCase(1, 0, 0, 0, 0, 0, 0) == 1
	assert bg_misc_library.QLR_CanGrabRocketLauncherCase(0, 0, 1, 0, 0, 0, 0) == 0
	assert bg_misc_library.QLR_CanGrabRocketLauncherCase(0, 0, 0, 1, 1, 1500, 1000) == 0
	assert bg_misc_library.QLR_CanGrabRocketLauncherCase(0, 0, 0, 1, 1, 2000, 1000) == 1

	assert bg_misc_library.QLR_CanGrabHealthCase(health_index, 99, 100) == 1
	assert bg_misc_library.QLR_CanGrabHealthCase(health_index, 100, 100) == 0
	assert bg_misc_library.QLR_CanGrabHealthCase(small_health_index, 199, 100) == 1
	assert bg_misc_library.QLR_CanGrabHealthCase(small_health_index, 200, 100) == 0
	assert bg_misc_library.QLR_CanGrabHealthCase(mega_index, 150, 100) == 1
	assert bg_misc_library.QLR_CanGrabHealthCase(mega_index, 200, 100) == 0
