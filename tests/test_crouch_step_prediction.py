from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_DIR = REPO_ROOT / "src" / "code" / "game"
CGAME_DIR = REPO_ROOT / "src" / "code" / "cgame"

C_SOURCE = """#include <string.h>\n#include \"q_shared.h\"\n#include \"bg_public.h\"\n#include \"bg_local.h\"\n\nqboolean pm_test_doubleJumpActive;\n\n/*\n=============\nCom_Printf\n\nTest stub that discards log messages during crouch step tests.\n=============\n*/\nvoid Com_Printf( const char *fmt, ... ) {\n\t(void)fmt;\n}\n\n/*\n=============\ntrap_SnapVector\n\nStubbed trap call used by movement helpers.\n=============\n*/\nvoid trap_SnapVector( float *v ) {\n\t(void)v;\n}\n\n/*\n=============\nCom_Error\n
Minimal error stub for movement harness builds.\n=============\n*/\nvoid Com_Error( int level, const char *fmt, ... ) {\n\t(void)level;\n\t(void)fmt;\n}\n\n/*\n=============\nQLR_ApplyCrouchStep\n\nApplies the step jump helper with configurable crouch slide flags and returns the resulting vertical velocity.\n=============\n*/\nfloat QLR_ApplyCrouchStep( int crouchSlideActive, int settingsCrouchSlide, int settingsCrouchStepJump, float stepDelta, float initialVelocity, float stepJumpVelocity, int fromCrouchSlideFlag ) {\n\tstatic pmove_t localPM;\n\tstatic playerState_t localPS;\n\tstatic pmove_settings_t localSettings;\n\tpmove_t *previousPM;\n\tfloat resultingVelocity;\n\n\tmemset( &localPM, 0, sizeof( localPM ) );\n\tmemset( &localPS, 0, sizeof( localPS ) );\n\tmemset( &localSettings, 0, sizeof( localSettings ) );\n\n\tlocalPM.ps = &localPS;\n\tlocalPM.pmoveSettings = &localSettings;\n\n\tpreviousPM = pm;\n\tpm = &localPM;\n\n\tlocalPS.velocity[2] = initialVelocity;\n\n\tif ( crouchSlideActive ) {\n\t\tlocalPS.pm_flags |= PMF_CROUCH_SLIDE;\n\t}\n\n\tlocalSettings.stepJump = qtrue;\n\tlocalSettings.stepJumpVelocity = stepJumpVelocity;\n\tlocalSettings.crouchSlide = settingsCrouchSlide ? qtrue : qfalse;\n\tlocalSettings.crouchStepJump = settingsCrouchStepJump ? qtrue : qfalse;\n\n\tPM_ApplyStepJump( stepDelta, fromCrouchSlideFlag ? qtrue : qfalse );\n\n\tresultingVelocity = localPS.velocity[2];\n\tpm = previousPM;\n\n\treturn resultingVelocity;\n}\n"""

SOURCES = [
    GAME_DIR / "bg_pmove.c",
    GAME_DIR / "bg_slidemove.c",
    GAME_DIR / "bg_lib.c",
    GAME_DIR / "bg_misc.c",
    GAME_DIR / "q_math.c",
    GAME_DIR / "q_shared.c",
]


def _build_test_library(tmp_path: Path) -> Path:
    src_path = tmp_path / "crouch_step_test.c"
    shim_path = tmp_path / "crouch_step_shim.h"
    src_path.write_text(C_SOURCE, encoding="utf-8")
    shim_path.write_text(
        '\n'.join(
            (
                '#include "q_shared.h"',
                'extern qboolean pm_test_doubleJumpActive;',
                '#define doubleJumpActive pm_test_doubleJumpActive',
            )
        )
        + '\n',
        encoding="utf-8",
    )

    if sys.platform == "darwin":
        lib_path = tmp_path / "libcrouch_step_test.dylib"
        compile_cmd = [
            "cc",
            "-std=c99",
            "-dynamiclib",
            "-include",
            str(shim_path),
            "-I",
            str(GAME_DIR),
            "-I",
            str(CGAME_DIR),
            "-o",
            str(lib_path),
            str(src_path),
            *[str(source) for source in SOURCES],
        ]
    elif os.name == "nt":
        lib_path = tmp_path / "crouch_step_test.dll"
        compile_cmd = [
            "cl",
            "/LD",
            f"/FI{shim_path}",
            str(src_path),
            *[str(source) for source in SOURCES],
            f"/I{GAME_DIR}",
            f"/I{CGAME_DIR}",
            f"/Fe:{lib_path}",
        ]
    else:
        lib_path = tmp_path / "libcrouch_step_test.so"
        compile_cmd = [
            "cc",
            "-std=c99",
            "-shared",
            "-fPIC",
            "-include",
            str(shim_path),
            "-I",
            str(GAME_DIR),
            "-I",
            str(CGAME_DIR),
            "-o",
            str(lib_path),
            str(src_path),
            *[str(source) for source in SOURCES],
        ]

    subprocess.run(compile_cmd, check=True)
    return lib_path


def _load_library(lib_path: Path) -> ctypes.CDLL:
    library = ctypes.CDLL(str(lib_path))
    library.QLR_ApplyCrouchStep.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_int,
    ]
    library.QLR_ApplyCrouchStep.restype = ctypes.c_float
    return library


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_crouch_slide_step_boost_matches_server(tmp_path: Path) -> None:
    lib_path = _build_test_library(tmp_path)
    library = _load_library(lib_path)

    initial_velocity = ctypes.c_float(160.0)
    step_jump_velocity = ctypes.c_float(320.0)

    boosted_velocity = library.QLR_ApplyCrouchStep(
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_float(12.0),
        initial_velocity,
        step_jump_velocity,
        ctypes.c_int(1),
    )
    assert boosted_velocity == pytest.approx(step_jump_velocity.value, rel=1e-6)

    no_slide_velocity = library.QLR_ApplyCrouchStep(
        ctypes.c_int(0),
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_float(12.0),
        initial_velocity,
        step_jump_velocity,
        ctypes.c_int(1),
    )
    assert no_slide_velocity == pytest.approx(initial_velocity.value, rel=1e-6)

    disabled_cvar_velocity = library.QLR_ApplyCrouchStep(
        ctypes.c_int(1),
        ctypes.c_int(0),
        ctypes.c_int(1),
        ctypes.c_float(12.0),
        initial_velocity,
        step_jump_velocity,
        ctypes.c_int(1),
    )
    assert disabled_cvar_velocity == pytest.approx(initial_velocity.value, rel=1e-6)

    disabled_step_velocity = library.QLR_ApplyCrouchStep(
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_int(0),
        ctypes.c_float(12.0),
        initial_velocity,
        step_jump_velocity,
        ctypes.c_int(1),
    )
    assert disabled_step_velocity == pytest.approx(initial_velocity.value, rel=1e-6)

    non_crouch_call_velocity = library.QLR_ApplyCrouchStep(
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_float(12.0),
        initial_velocity,
        step_jump_velocity,
        ctypes.c_int(0),
    )
    assert non_crouch_call_velocity == pytest.approx(step_jump_velocity.value, rel=1e-6)

    negative_step_velocity = library.QLR_ApplyCrouchStep(
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_int(1),
        ctypes.c_float(-8.0),
        initial_velocity,
        step_jump_velocity,
        ctypes.c_int(1),
    )
    assert negative_step_velocity == pytest.approx(initial_velocity.value, rel=1e-6)
