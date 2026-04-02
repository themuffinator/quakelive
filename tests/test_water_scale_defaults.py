from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

import pytest

C_SOURCE = """#include <string.h>

typedef int qboolean;
#define qtrue 1
#define qfalse 0

typedef struct pmove_settings_s {
	float	waterSwimScale;
	float	waterWadeScale;
	float	stepHeight;
} pmove_settings_t;

typedef struct pmove_s {
	pmove_settings_t	*pmoveSettings;
} pmove_t;

pmove_t	*pm;
float	pm_swimScale = 0.60f;
float	pm_wadeScale = 0.80f;
float	pm_stepHeight = 22.0f;

static const pmove_settings_t pm_defaultSettings = {
	.waterSwimScale = 0.60f,
	.waterWadeScale = 0.80f,
	.stepHeight = 22.0f,
};

/*
=============
PM_GetActiveSettings

Returns the current movement tuning block, falling back to defaults.
=============
*/
const pmove_settings_t *PM_GetActiveSettings( void ) {
	if ( pm && pm->pmoveSettings ) {
		return pm->pmoveSettings;
	}

	return &pm_defaultSettings;
}

/*
=============
PM_LoadMoveSettings

Synchronises extended Quake Live movement settings with legacy globals.
=============
*/
static void PM_LoadMoveSettings( void ) {
	const pmove_settings_t	*settings;
	float	swimScale;
	float	wadeScale;
	float	stepHeight;

	settings = PM_GetActiveSettings();

	swimScale = settings->waterSwimScale;
	if ( swimScale <= 0.0f ) {
		swimScale = pm_defaultSettings.waterSwimScale;
	}
	pm_swimScale = swimScale;

	wadeScale = settings->waterWadeScale;
	if ( wadeScale <= 0.0f ) {
		wadeScale = pm_defaultSettings.waterWadeScale;
	}
	pm_wadeScale = wadeScale;

	stepHeight = settings->stepHeight;
	if ( stepHeight <= 0.0f ) {
		stepHeight = pm_defaultSettings.stepHeight;
	}
	pm_stepHeight = stepHeight;
}

/*
=============
qlr_load_water_scales_for_test

Applies PM_LoadMoveSettings to test-provided overrides.
=============
*/
void qlr_load_water_scales_for_test( float swimScale, float wadeScale, float *outSwim, float *outWade ) {
	pmove_settings_t	settings;
	pmove_t	localPmove;

	memset( &settings, 0, sizeof( settings ) );
	memset( &localPmove, 0, sizeof( localPmove ) );

	settings.waterSwimScale = swimScale;
	settings.waterWadeScale = wadeScale;
	localPmove.pmoveSettings = &settings;

	pm = &localPmove;
	PM_LoadMoveSettings();

	if ( outSwim ) {
		*outSwim = pm_swimScale;
	}

	if ( outWade ) {
		*outWade = pm_wadeScale;
	}

	pm = NULL;
}
"""


def _build_test_library(tmp_path: Path) -> Path:
    src_path = tmp_path / "pmove_water_scale_test.c"
    src_path.write_text(C_SOURCE, encoding="utf-8")

    if sys.platform == "darwin":
        lib_path = tmp_path / "libpmove_water_scale_test.dylib"
        compile_cmd = [
            "cc",
            "-std=c99",
            "-dynamiclib",
            "-o",
            str(lib_path),
            str(src_path),
        ]
    elif os.name == "nt":
        lib_path = tmp_path / "pmove_water_scale_test.dll"
        compile_cmd = [
            "cl",
            "/LD",
            str(src_path),
            "/Fe:" + str(lib_path),
        ]
    else:
        lib_path = tmp_path / "libpmove_water_scale_test.so"
        compile_cmd = [
            "cc",
            "-std=c99",
            "-shared",
            "-fPIC",
            "-o",
            str(lib_path),
            str(src_path),
        ]

    subprocess.run(compile_cmd, check=True)
    return lib_path


def _load_library(lib_path: Path) -> ctypes.CDLL:
    library = ctypes.CDLL(str(lib_path))
    library.qlr_load_water_scales_for_test.argtypes = [
        ctypes.c_float,
        ctypes.c_float,
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float),
    ]
    library.qlr_load_water_scales_for_test.restype = None
    return library


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_water_scale_defaults(tmp_path: Path) -> None:
    lib_path = _build_test_library(tmp_path)
    library = _load_library(lib_path)

    swim = ctypes.c_float(-1.0)
    wade = ctypes.c_float(-1.0)

    library.qlr_load_water_scales_for_test(
        ctypes.c_float(0.0),
        ctypes.c_float(0.0),
        ctypes.byref(swim),
        ctypes.byref(wade),
    )

    assert swim.value == pytest.approx(0.60, rel=1e-6)
    assert wade.value == pytest.approx(0.80, rel=1e-6)

    library.qlr_load_water_scales_for_test(
        ctypes.c_float(0.5),
        ctypes.c_float(0.7),
        ctypes.byref(swim),
        ctypes.byref(wade),
    )

    assert swim.value == pytest.approx(0.5, rel=1e-6)
    assert wade.value == pytest.approx(0.7, rel=1e-6)

    library.qlr_load_water_scales_for_test(
        ctypes.c_float(-0.5),
        ctypes.c_float(-0.7),
        ctypes.byref(swim),
        ctypes.byref(wade),
    )

    assert swim.value == pytest.approx(0.60, rel=1e-6)
    assert wade.value == pytest.approx(0.80, rel=1e-6)
