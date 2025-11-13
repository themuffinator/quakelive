import ctypes
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

C_SOURCE = r"""
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define GUIDED_ROCKET_TURN_FRACTION 0.2f

typedef float vec3_t[3];

static void qlr_vec_copy( const vec3_t in, vec3_t out ) {
out[0] = in[0];
out[1] = in[1];
out[2] = in[2];
}

static float qlr_vec_length( const vec3_t v ) {
return sqrtf( ( v[0] * v[0] ) + ( v[1] * v[1] ) + ( v[2] * v[2] ) );
}

static float qlr_vec_normalize( vec3_t v ) {
float length = qlr_vec_length( v );

if ( length == 0.0f ) {
return 0.0f;
}

v[0] /= length;
v[1] /= length;
v[2] /= length;
return length;
}

static void qlr_vec_scale( vec3_t v, float scale ) {
v[0] *= scale;
v[1] *= scale;
v[2] *= scale;
}

static void qlr_vec_ma( const vec3_t start, float scale, const vec3_t direction, vec3_t out ) {
out[0] = start[0] + scale * direction[0];
out[1] = start[1] + scale * direction[1];
out[2] = start[2] + scale * direction[2];
}

static void qlr_vec_add( const vec3_t a, const vec3_t b, vec3_t out ) {
out[0] = a[0] + b[0];
out[1] = a[1] + b[1];
out[2] = a[2] + b[2];
}

static void AngleVectors( const vec3_t angles, vec3_t forward ) {
float pitch = angles[0] * (float)M_PI / 180.0f;
float yaw = angles[1] * (float)M_PI / 180.0f;
float cp = cosf( pitch );
float sp = sinf( pitch );
float cy = cosf( yaw );
float sy = sinf( yaw );

forward[0] = cp * cy;
forward[1] = cp * sy;
forward[2] = -sp;
}

int qlr_apply_guided_step( const vec3_t viewAngles, const vec3_t inDelta, float storedSpeed, int guidedFlag, int ownerActive, vec3_t outDelta ) {
vec3_t desiredDir;
vec3_t currentDir;
float speed;

if ( !guidedFlag || !ownerActive ) {
qlr_vec_copy( inDelta, outDelta );
return 0;
}

AngleVectors( viewAngles, desiredDir );
if ( qlr_vec_normalize( desiredDir ) == 0.0f ) {
desiredDir[0] = 1.0f;
desiredDir[1] = 0.0f;
desiredDir[2] = 0.0f;
}

qlr_vec_copy( inDelta, currentDir );
if ( qlr_vec_normalize( currentDir ) == 0.0f ) {
qlr_vec_copy( desiredDir, currentDir );
}

speed = storedSpeed;
if ( speed <= 0.0f ) {
vec3_t tmp;
qlr_vec_copy( inDelta, tmp );
speed = qlr_vec_length( tmp );
}
if ( speed <= 0.0f ) {
speed = storedSpeed;
}

qlr_vec_ma( currentDir, GUIDED_ROCKET_TURN_FRACTION, desiredDir, currentDir );
if ( qlr_vec_normalize( currentDir ) == 0.0f ) {
qlr_vec_copy( desiredDir, currentDir );
}

outDelta[0] = currentDir[0] * speed;
outDelta[1] = currentDir[1] * speed;
outDelta[2] = currentDir[2] * speed;
return 1;
}

void qlr_adjust_splash(vec3_t origin, const vec3_t planeNormal, const vec3_t velocity, int offset) {
vec3_t normal;

if ( offset == 0 ) {
return;
}

qlr_vec_copy( planeNormal, normal );
if ( qlr_vec_normalize( normal ) == 0.0f ) {
qlr_vec_copy( velocity, normal );
if ( qlr_vec_normalize( normal ) == 0.0f ) {
return;
}
}

qlr_vec_ma( origin, (float)offset, normal, origin );
}

float qlr_select_grapple_speed( int configSpeed, float cvarSpeed, float defaultSpeed ) {
float speed = (float)configSpeed;

if ( speed <= 0.0f ) {
speed = cvarSpeed;
if ( speed <= 0.0f ) {
speed = defaultSpeed;
}
}

return speed;
}

void qlr_scale_direction( const vec3_t dir, int speed, vec3_t outDelta ) {
vec3_t normal;

qlr_vec_copy( dir, normal );
if ( qlr_vec_normalize( normal ) == 0.0f ) {
outDelta[0] = outDelta[1] = outDelta[2] = 0.0f;
return;
}

outDelta[0] = normal[0] * (float)speed;
outDelta[1] = normal[1] * (float)speed;
outDelta[2] = normal[2] * (float)speed;
}
"""


def _build_test_library(tmp_path: Path) -> Path:
    src_path = tmp_path / "weapon_tuning_test.c"
    src_path.write_text(C_SOURCE, encoding="utf-8")

    if sys.platform == "darwin":
        lib_path = tmp_path / "libweapon_tuning_test.dylib"
        compile_cmd = [
            "cc",
            "-std=c99",
            "-dynamiclib",
            "-o",
            str(lib_path),
            str(src_path),
        ]
    elif os.name == "nt":
        lib_path = tmp_path / "weapon_tuning_test.dll"
        compile_cmd = [
            "cl",
            "/LD",
            str(src_path),
            "/Fe:" + str(lib_path),
        ]
    else:
        lib_path = tmp_path / "libweapon_tuning_test.so"
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
    vec3 = ctypes.c_float * 3
    library.qlr_apply_guided_step.argtypes = [
        vec3,
        vec3,
        ctypes.c_float,
        ctypes.c_int,
        ctypes.c_int,
        vec3,
    ]
    library.qlr_apply_guided_step.restype = ctypes.c_int
    library.qlr_adjust_splash.argtypes = [
        vec3,
        vec3,
        vec3,
        ctypes.c_int,
    ]
    library.qlr_adjust_splash.restype = None
    library.qlr_select_grapple_speed.argtypes = [
        ctypes.c_int,
        ctypes.c_float,
        ctypes.c_float,
    ]
    library.qlr_select_grapple_speed.restype = ctypes.c_float
    library.qlr_scale_direction.argtypes = [
        vec3,
        ctypes.c_int,
        vec3,
    ]
    library.qlr_scale_direction.restype = None
    return library


VEC3 = ctypes.c_float * 3


@pytest.fixture(scope="module")
def weapon_lib(tmp_path_factory):
    lib_path = _build_test_library(tmp_path_factory.mktemp("weapon_tuning"))
    return _load_library(lib_path)


def _length(vec) -> float:
    return math.sqrt(sum(component * component for component in vec))


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_guided_rocket_lerps_toward_owner(weapon_lib) -> None:
    view_angles = VEC3(0.0, 90.0, 0.0)
    initial_delta = VEC3(900.0, 0.0, 0.0)
    out_delta = VEC3(0.0, 0.0, 0.0)

    applied = weapon_lib.qlr_apply_guided_step(
        view_angles,
        initial_delta,
        ctypes.c_float(900.0),
        ctypes.c_int(1),
        ctypes.c_int(1),
        out_delta,
    )

    assert applied == 1
    assert _length(out_delta) == pytest.approx(900.0, rel=1e-6)
    assert out_delta[1] > 0.0
    assert out_delta[0] < 900.0


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_guided_rocket_inactive_owner(weapon_lib) -> None:
    view_angles = VEC3(0.0, 0.0, 0.0)
    initial_delta = VEC3(500.0, 0.0, 0.0)
    out_delta = VEC3(0.0, 0.0, 0.0)

    applied = weapon_lib.qlr_apply_guided_step(
        view_angles,
        initial_delta,
        ctypes.c_float(500.0),
        ctypes.c_int(1),
        ctypes.c_int(0),
        out_delta,
    )

    assert applied == 0
    assert tuple(out_delta) == tuple(initial_delta)


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_rocket_splash_offset_respects_normal(weapon_lib) -> None:
    origin = VEC3(0.0, 0.0, 0.0)
    plane_normal = VEC3(0.0, 0.0, 1.0)
    velocity = VEC3(0.0, 0.0, 0.0)

    weapon_lib.qlr_adjust_splash(origin, plane_normal, velocity, ctypes.c_int(32))
    assert origin[2] == pytest.approx(32.0, rel=1e-6)


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_rocket_splash_offset_uses_velocity_fallback(weapon_lib) -> None:
    origin = VEC3(0.0, 0.0, 0.0)
    plane_normal = VEC3(0.0, 0.0, 0.0)
    velocity = VEC3(1.0, 0.0, 0.0)

    weapon_lib.qlr_adjust_splash(origin, plane_normal, velocity, ctypes.c_int(-16))
    assert origin[0] == pytest.approx(-16.0, rel=1e-6)
    assert origin[1] == pytest.approx(0.0, rel=1e-6)
    assert origin[2] == pytest.approx(0.0, rel=1e-6)


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_grapple_speed_prefers_weapon_config(weapon_lib) -> None:
    direct = weapon_lib.qlr_select_grapple_speed(ctypes.c_int(1200), ctypes.c_float(600.0), ctypes.c_float(800.0))
    assert direct == pytest.approx(1200.0, rel=1e-6)

    fallback = weapon_lib.qlr_select_grapple_speed(ctypes.c_int(0), ctypes.c_float(600.0), ctypes.c_float(800.0))
    assert fallback == pytest.approx(600.0, rel=1e-6)

    defaulted = weapon_lib.qlr_select_grapple_speed(ctypes.c_int(0), ctypes.c_float(0.0), ctypes.c_float(800.0))
    assert defaulted == pytest.approx(800.0, rel=1e-6)


@pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")
def test_projectile_speed_scaling(weapon_lib) -> None:
    direction = VEC3(0.0, 0.0, 1.0)
    out_delta = VEC3(0.0, 0.0, 0.0)

    weapon_lib.qlr_scale_direction(direction, ctypes.c_int(2000), out_delta)
    assert _length(out_delta) == pytest.approx(2000.0, rel=1e-6)
    assert out_delta[2] == pytest.approx(2000.0, rel=1e-6)
