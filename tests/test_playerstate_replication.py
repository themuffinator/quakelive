import ctypes
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = REPO_ROOT / "src" / "code"
GAME_DIR = CODE_DIR / "game"
QCOMMON_DIR = CODE_DIR / "qcommon"

C_SOURCE = r"""
#include <stdarg.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "q_shared.h"
#include "qcommon.h"
#include "bg_public.h"

typedef struct qlr_ps_values_s {
	int		jumpTime;
	int		doubleJumped;
	int		crouchTime;
	int		crouchSlideTime;
	int		weaponPrimary;
	int		fov;
	int		forwardmove;
	int		rightmove;
	int		upmove;
	int		playerItemTimeMax;
	int		playerItemTime;
	int		playerItemRecharge;
} qlr_ps_values_t;

typedef struct qlr_usercmd_values_s {
	int		weapon;
	int		weaponPrimary;
	int		fov;
	int		forwardmove;
	int		rightmove;
	int		upmove;
	int		buttons;
} qlr_usercmd_values_t;

typedef struct qlr_ps_offsets_s {
	int		externalEvent;
	int		externalEventParm;
	int		clientNum;
	int		location;
	int		weapon;
	int		weaponPrimary;
	int		weaponstate;
	int		fov;
	int		generic1;
	int		loopSound;
	int		jumppad_ent;
	int		jumpTime;
	int		doubleJumped;
	int		crouchTime;
	int		crouchSlideTime;
	int		forwardmove;
	int		rightmove;
	int		upmove;
} qlr_ps_offsets_t;

#ifdef _WIN32
#define QLR_TEST_EXPORT __declspec(dllexport)
#else
#define QLR_TEST_EXPORT
#endif

static cvar_t qlr_localShownet;
cvar_t *cl_shownet = &qlr_localShownet;

/*
=============
Com_Printf

Stubbed logger for network serialization tests.
=============
*/
void QDECL Com_Printf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
Com_Error

Aborts the test harness if the message code fails.
=============
*/
void QDECL Com_Error( int level, const char *fmt, ... ) {
	(void)level;
	(void)fmt;
	abort();
}

/*
=============
Com_Memcpy

Test-friendly memcpy shim.
=============
*/
void Com_Memcpy( void *dest, const void *src, size_t count ) {
	memcpy( dest, src, count );
}

/*
=============
Com_Memset

Test-friendly memset shim.
=============
*/
void Com_Memset( void *dest, int c, size_t count ) {
	memset( dest, c, count );
}

/*
=============
QLR_WriteAndReadPlayerState

Encodes the server playerstate delta and immediately decodes it to produce the client result.
=============
*/
static void QLR_WriteAndReadPlayerState( const playerState_t *from, const playerState_t *to, playerState_t *out ) {
	msg_t msg;
	byte buffer[2048];

	MSG_Init( &msg, buffer, sizeof( buffer ) );
	MSG_WriteDeltaPlayerstate( &msg, (playerState_t *)from, (playerState_t *)to );
	MSG_BeginReading( &msg );
	MSG_ReadDeltaPlayerstate( &msg, (playerState_t *)from, out );
}

/*
=============
QLR_ReplicateJumpState

Generates a jump timing delta and captures the replicated fields for verification.
=============
*/
QLR_TEST_EXPORT void QLR_ReplicateJumpState( qlr_ps_values_t *values ) {
	playerState_t from;
	playerState_t server;
	playerState_t client;

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	server.jumpTime = 1337331;
	server.doubleJumped = 1;

	QLR_WriteAndReadPlayerState( &from, &server, &client );

	values->jumpTime = client.jumpTime;
	values->doubleJumped = client.doubleJumped;
}

/*
=============
QLR_ReplicateCrouchSlide

Generates a crouch slide delta and captures the replicated timers for verification.
=============
*/
QLR_TEST_EXPORT void QLR_ReplicateCrouchSlide( qlr_ps_values_t *values ) {
	playerState_t from;
	playerState_t server;
	playerState_t client;

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	server.crouchTime = 777;
	server.crouchSlideTime = 1600;

	QLR_WriteAndReadPlayerState( &from, &server, &client );

	values->crouchTime = client.crouchTime;
	values->crouchSlideTime = client.crouchSlideTime;
}

/*
=============
QLR_ReplicateCommandMirrors

Generates signed command-axis deltas and captures their replicated values.
=============
*/
QLR_TEST_EXPORT void QLR_ReplicateCommandMirrors( qlr_ps_values_t *values ) {
	playerState_t from;
	playerState_t server;
	playerState_t client;

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	server.forwardmove = -127;
	server.rightmove = 64;
	server.upmove = -12;
	server.weaponPrimary = 14;
	server.fov = 110;

	QLR_WriteAndReadPlayerState( &from, &server, &client );

	values->weaponPrimary = client.weaponPrimary;
	values->fov = client.fov;
	values->forwardmove = client.forwardmove;
	values->rightmove = client.rightmove;
	values->upmove = client.upmove;
}

/*
=============
QLR_ReplicatePlayerItemStats

Generates the retail progress-backed holdable stat triplet and captures the replicated values.
=============
*/
QLR_TEST_EXPORT void QLR_ReplicatePlayerItemStats( qlr_ps_values_t *values ) {
	playerState_t from;
	playerState_t server;
	playerState_t client;

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	server.stats[STAT_PLAYER_ITEM_TIME_MAX] = 10000;
	server.stats[STAT_PLAYER_ITEM_TIME] = 7500;
	server.stats[STAT_PLAYER_ITEM_RECHARGE] = 500;

	QLR_WriteAndReadPlayerState( &from, &server, &client );

	values->playerItemTimeMax = client.stats[STAT_PLAYER_ITEM_TIME_MAX];
	values->playerItemTime = client.stats[STAT_PLAYER_ITEM_TIME];
	values->playerItemRecharge = client.stats[STAT_PLAYER_ITEM_RECHARGE];
}

/*
=============
QLR_GetPlayerStateOffsets

Returns the retail playerState offsets recovered from the engine netfield table and shared pmove writes.
=============
*/
QLR_TEST_EXPORT void QLR_GetPlayerStateOffsets( qlr_ps_offsets_t *offsets ) {
	Com_Memset( offsets, 0, sizeof( *offsets ) );

	offsets->externalEvent = (int)offsetof( playerState_t, externalEvent );
	offsets->externalEventParm = (int)offsetof( playerState_t, externalEventParm );
	offsets->clientNum = (int)offsetof( playerState_t, clientNum );
	offsets->location = (int)offsetof( playerState_t, location );
	offsets->weapon = (int)offsetof( playerState_t, weapon );
	offsets->weaponPrimary = (int)offsetof( playerState_t, weaponPrimary );
	offsets->weaponstate = (int)offsetof( playerState_t, weaponstate );
	offsets->fov = (int)offsetof( playerState_t, fov );
	offsets->generic1 = (int)offsetof( playerState_t, generic1 );
	offsets->loopSound = (int)offsetof( playerState_t, loopSound );
	offsets->jumppad_ent = (int)offsetof( playerState_t, jumppad_ent );
	offsets->jumpTime = (int)offsetof( playerState_t, jumpTime );
	offsets->doubleJumped = (int)offsetof( playerState_t, doubleJumped );
	offsets->crouchTime = (int)offsetof( playerState_t, crouchTime );
	offsets->crouchSlideTime = (int)offsetof( playerState_t, crouchSlideTime );
	offsets->forwardmove = (int)offsetof( playerState_t, forwardmove );
	offsets->rightmove = (int)offsetof( playerState_t, rightmove );
	offsets->upmove = (int)offsetof( playerState_t, upmove );
}

/*
=============
QLR_RoundTripUsercmd

Encodes a keyed usercmd delta and captures the decoded retail command bytes.
=============
*/
QLR_TEST_EXPORT void QLR_RoundTripUsercmd( qlr_usercmd_values_t *values ) {
	usercmd_t from;
	usercmd_t server;
	usercmd_t client;
	msg_t msg;
	byte buffer[512];

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	server.serverTime = 64;
	server.weapon = 5;
	server.weaponPrimary = 14;
	server.fov = 110;
	server.forwardmove = -127;
	server.rightmove = 64;
	server.upmove = -12;
	server.buttons = BUTTON_ATTACK | BUTTON_USE_HOLDABLE;

	MSG_Init( &msg, buffer, sizeof( buffer ) );
	MSG_WriteDeltaUsercmdKey( &msg, 0x12345678, &from, &server );
	MSG_BeginReading( &msg );
	MSG_ReadDeltaUsercmdKey( &msg, 0x12345678, &from, &client );

	values->weapon = client.weapon;
	values->weaponPrimary = client.weaponPrimary;
	values->fov = client.fov;
	values->forwardmove = client.forwardmove;
	values->rightmove = client.rightmove;
	values->upmove = client.upmove;
	values->buttons = client.buttons;
}
"""

class PlayerStateReplication(ctypes.Structure):
	_fields_ = [
		("jumpTime", ctypes.c_int),
		("doubleJumped", ctypes.c_int),
		("crouchTime", ctypes.c_int),
		("crouchSlideTime", ctypes.c_int),
		("weaponPrimary", ctypes.c_int),
		("fov", ctypes.c_int),
		("forwardmove", ctypes.c_int),
		("rightmove", ctypes.c_int),
		("upmove", ctypes.c_int),
		("playerItemTimeMax", ctypes.c_int),
		("playerItemTime", ctypes.c_int),
		("playerItemRecharge", ctypes.c_int),
	]


class UsercmdReplication(ctypes.Structure):
	_fields_ = [
		("weapon", ctypes.c_int),
		("weaponPrimary", ctypes.c_int),
		("fov", ctypes.c_int),
		("forwardmove", ctypes.c_int),
		("rightmove", ctypes.c_int),
		("upmove", ctypes.c_int),
		("buttons", ctypes.c_int),
	]


class PlayerStateOffsets(ctypes.Structure):
	_fields_ = [
		("externalEvent", ctypes.c_int),
		("externalEventParm", ctypes.c_int),
		("clientNum", ctypes.c_int),
		("location", ctypes.c_int),
		("weapon", ctypes.c_int),
		("weaponPrimary", ctypes.c_int),
		("weaponstate", ctypes.c_int),
		("fov", ctypes.c_int),
		("generic1", ctypes.c_int),
		("loopSound", ctypes.c_int),
		("jumppad_ent", ctypes.c_int),
		("jumpTime", ctypes.c_int),
		("doubleJumped", ctypes.c_int),
		("crouchTime", ctypes.c_int),
		("crouchSlideTime", ctypes.c_int),
		("forwardmove", ctypes.c_int),
		("rightmove", ctypes.c_int),
		("upmove", ctypes.c_int),
	]


def _build_test_library(tmp_path: Path) -> Path:
	src_path = tmp_path / "playerstate_replication_test.c"
	src_path.write_text(C_SOURCE, encoding="utf-8")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the playerstate replication harness")

	lib_path = tmp_path / shared_library_name("playerstate_replication_test")
	compile_c_binary(
		compiler,
		[
			src_path,
			QCOMMON_DIR / "huffman.c",
			QCOMMON_DIR / "msg.c",
			GAME_DIR / "q_shared.c",
		],
		lib_path,
		include_dirs=[CODE_DIR, GAME_DIR, QCOMMON_DIR],
		shared=True,
		workdir=REPO_ROOT,
	)
	return lib_path


def _load_library(lib_path: Path) -> ctypes.CDLL:
	library = ctypes.CDLL(str(lib_path))
	library.QLR_ReplicateJumpState.argtypes = [ctypes.POINTER(PlayerStateReplication)]
	library.QLR_ReplicateJumpState.restype = None
	library.QLR_ReplicateCrouchSlide.argtypes = [ctypes.POINTER(PlayerStateReplication)]
	library.QLR_ReplicateCrouchSlide.restype = None
	library.QLR_ReplicateCommandMirrors.argtypes = [ctypes.POINTER(PlayerStateReplication)]
	library.QLR_ReplicateCommandMirrors.restype = None
	library.QLR_ReplicatePlayerItemStats.argtypes = [ctypes.POINTER(PlayerStateReplication)]
	library.QLR_ReplicatePlayerItemStats.restype = None
	library.QLR_GetPlayerStateOffsets.argtypes = [ctypes.POINTER(PlayerStateOffsets)]
	library.QLR_GetPlayerStateOffsets.restype = None
	library.QLR_RoundTripUsercmd.argtypes = [ctypes.POINTER(UsercmdReplication)]
	library.QLR_RoundTripUsercmd.restype = None
	return library


@pytest.fixture(scope="module")
def playerstate_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	tmp_path = tmp_path_factory.mktemp("playerstate_replication")
	lib_path = _build_test_library(tmp_path)
	return _load_library(lib_path)


def test_jump_state_round_trip(playerstate_library: ctypes.CDLL) -> None:
	values = PlayerStateReplication()
	playerstate_library.QLR_ReplicateJumpState(ctypes.byref(values))

	assert values.jumpTime == 1337331
	assert values.doubleJumped == 1


def test_crouch_slide_timers_round_trip(playerstate_library: ctypes.CDLL) -> None:
	values = PlayerStateReplication()
	playerstate_library.QLR_ReplicateCrouchSlide(ctypes.byref(values))

	assert values.crouchTime == 777
	assert values.crouchSlideTime == 1600


def test_command_axis_mirrors_round_trip_as_signed_bytes(playerstate_library: ctypes.CDLL) -> None:
	values = PlayerStateReplication()
	playerstate_library.QLR_ReplicateCommandMirrors(ctypes.byref(values))

	assert values.weaponPrimary == 14
	assert values.fov == 110
	assert values.forwardmove == -127
	assert values.rightmove == 64
	assert values.upmove == -12


def test_player_item_timer_stats_round_trip(playerstate_library: ctypes.CDLL) -> None:
	values = PlayerStateReplication()
	playerstate_library.QLR_ReplicatePlayerItemStats(ctypes.byref(values))

	assert values.playerItemTimeMax == 10000
	assert values.playerItemTime == 7500
	assert values.playerItemRecharge == 500


def test_playerstate_retail_offsets_match_netfield_and_pmove_evidence(
	playerstate_library: ctypes.CDLL,
) -> None:
	offsets = PlayerStateOffsets()
	playerstate_library.QLR_GetPlayerStateOffsets(ctypes.byref(offsets))

	assert offsets.externalEvent == 0x80
	assert offsets.externalEventParm == 0x84
	assert offsets.clientNum == 0x88
	assert offsets.location == 0x8C
	assert offsets.weapon == 0x90
	assert offsets.weaponPrimary == 0x94
	assert offsets.weaponstate == 0x98
	assert offsets.fov == 0x9C
	assert offsets.generic1 == 0x1C0
	assert offsets.loopSound == 0x1C4
	assert offsets.jumppad_ent == 0x1C8
	assert offsets.jumpTime == 0x1CC
	assert offsets.doubleJumped == 0x1D0
	assert offsets.crouchTime == 0x1D4
	assert offsets.crouchSlideTime == 0x1D8
	assert offsets.forwardmove == 0x1DC
	assert offsets.rightmove == 0x1DD
	assert offsets.upmove == 0x1DE


def test_keyed_usercmd_delta_round_trips_ql_weapon_primary_fov_and_signed_axes(
	playerstate_library: ctypes.CDLL,
) -> None:
	values = UsercmdReplication()
	playerstate_library.QLR_RoundTripUsercmd(ctypes.byref(values))

	assert values.weapon == 5
	assert values.weaponPrimary == 14
	assert values.fov == 110
	assert values.forwardmove == -127
	assert values.rightmove == 64
	assert values.upmove == -12
	assert values.buttons == 5
