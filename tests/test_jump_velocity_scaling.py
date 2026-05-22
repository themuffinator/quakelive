from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INCLUDE_DIR = REPO_ROOT / "src" / "code" / "game"

C_SOURCE = r"""
#include <string.h>
#include "q_shared.h"
#include "bg_public.h"
#include "bg_local.h"
#include "bg_pmove_jump.h"

float qlr_jump_scale(int jump_time, int command_time, float threshold, float offset, float scale_add, int *out_delta) {
        playerState_t ps;
        pmove_settings_t settings;
        int delta;
        float scale;

        memset(&ps, 0, sizeof(ps));
        memset(&settings, 0, sizeof(settings));

        ps.jumpTime = jump_time;

        settings.jumpVelocityTimeThreshold = threshold;
        settings.jumpVelocityTimeThresholdOffset = offset;
        settings.jumpVelocityScaleAdd = scale_add;

        scale = PM_EvaluateJumpVelocityScale(&ps, &settings, command_time, &delta);

        if (out_delta) {
                *out_delta = delta;
        }

        return scale;
}
"""


def _build_test_library(tmp_path: Path) -> Path:
        src_path = tmp_path / "pmove_jump_test.c"
        src_path.write_text(C_SOURCE, encoding="utf-8")

        if sys.platform == "darwin":
                lib_path = tmp_path / "libpmove_jump_test.dylib"
                compile_cmd = [
                        "cc",
                        "-std=c99",
                        "-dynamiclib",
                        "-I",
                        str(INCLUDE_DIR),
                        "-o",
                        str(lib_path),
                        str(src_path),
                ]
        elif os.name == "nt":
                lib_path = tmp_path / "pmove_jump_test.dll"
                compile_cmd = [
                        "cl",
                        "/LD",
                        str(src_path),
                        f"/I{INCLUDE_DIR}",
                        f"/Fe:{lib_path}",
                ]
        else:
                lib_path = tmp_path / "libpmove_jump_test.so"
                compile_cmd = [
                        "cc",
                        "-std=c99",
                        "-shared",
                        "-fPIC",
                        "-I",
                        str(INCLUDE_DIR),
                        "-o",
                        str(lib_path),
                        str(src_path),
                ]

        subprocess.run(compile_cmd, check=True)
        return lib_path


def _load_library(lib_path: Path) -> ctypes.CDLL:
        library = ctypes.CDLL(str(lib_path))
        library.qlr_jump_scale.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_float,
                ctypes.c_float,
                ctypes.c_float,
                ctypes.POINTER(ctypes.c_int),
        ]
        library.qlr_jump_scale.restype = ctypes.c_float
        return library


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_jump_velocity_scaling_threshold(tmp_path: Path) -> None:
        lib_path = _build_test_library(tmp_path)
        library = _load_library(lib_path)

        inside_delta = ctypes.c_int(-1)
        inside_scale = library.qlr_jump_scale(
                1000,
                1100,
                ctypes.c_float(500.0),
                ctypes.c_float(0.6),
                ctypes.c_float(0.4),
                ctypes.byref(inside_delta),
        )

        assert inside_delta.value == 100
        assert inside_scale == pytest.approx(1.32, rel=1e-6)

        outside_delta = ctypes.c_int(-1)
        outside_scale = library.qlr_jump_scale(
                1000,
                1500,
                ctypes.c_float(500.0),
                ctypes.c_float(0.6),
                ctypes.c_float(0.4),
                ctypes.byref(outside_delta),
        )

        assert outside_delta.value == 500
        assert outside_scale == pytest.approx(1.0, rel=1e-6)
