import ctypes
import json
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = REPO_ROOT / "src" / "code"
GAME_DIR = CODE_DIR / "game"
QCOMMON_DIR = CODE_DIR / "qcommon"
CG_SYSCALLS_PATH = CODE_DIR / "cgame" / "cg_syscalls.c"
CL_CGAME_PATH = CODE_DIR / "client" / "cl_cgame.c"
CL_PARSE_PATH = CODE_DIR / "client" / "cl_parse.c"
MSG_PATH = QCOMMON_DIR / "msg.c"
SV_SNAPSHOT_PATH = CODE_DIR / "server" / "sv_snapshot.c"
ALIASES_PATH = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
MAPPING_ROUND_17 = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_17.md"
MAPPING_ROUND_57 = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_57.md"
MAPPING_ROUND_65 = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_65.md"
MAPPING_ROUND_127 = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_127.md"
PLAYERSTATE_FIELDS_SPEC_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "network-playerstate-fields-parity-2026-06-05.json"
)

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

typedef struct qlr_ps_array_values_s {
	int		statHealth;
	int		statWeapons;
	int		statPlayerItemTime;
	int		persistantScore;
	int		persistantTeam;
	int		persistantHits;
	int		ammoRocket;
	int		ammoRail;
	int		powerupQuad;
	int		powerupBattleSuit;
	int		unchangedStatArmor;
	int		unchangedPersistantRank;
	int		unchangedAmmoMachinegun;
	int		unchangedPowerupHaste;
} qlr_ps_array_values_t;

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

/*
=============
QLR_ReplicatePlayerStateArrays

Generates a playerstate delta with all four retail array masks and captures changed plus unchanged slots.
=============
*/
QLR_TEST_EXPORT void QLR_ReplicatePlayerStateArrays( qlr_ps_array_values_t *values ) {
	playerState_t from;
	playerState_t server;
	playerState_t client;

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	from.stats[STAT_ARMOR] = 150;
	from.persistant[PERS_RANK] = 4;
	from.ammo[WP_MACHINEGUN] = 80;
	from.powerups[PW_HASTE] = 2222;

	server = from;
	server.stats[STAT_HEALTH] = 125;
	server.stats[STAT_WEAPONS] = ( 1 << WP_ROCKET_LAUNCHER ) | ( 1 << WP_RAILGUN );
	server.stats[STAT_PLAYER_ITEM_TIME] = 2222;
	server.persistant[PERS_SCORE] = 17;
	server.persistant[PERS_TEAM] = TEAM_RED;
	server.persistant[PERS_HITS] = 3;
	server.ammo[WP_ROCKET_LAUNCHER] = 9;
	server.ammo[WP_RAILGUN] = 4;
	server.powerups[PW_QUAD] = 12000;
	server.powerups[PW_BATTLESUIT] = 14000;

	QLR_WriteAndReadPlayerState( &from, &server, &client );

	values->statHealth = client.stats[STAT_HEALTH];
	values->statWeapons = client.stats[STAT_WEAPONS];
	values->statPlayerItemTime = client.stats[STAT_PLAYER_ITEM_TIME];
	values->persistantScore = client.persistant[PERS_SCORE];
	values->persistantTeam = client.persistant[PERS_TEAM];
	values->persistantHits = client.persistant[PERS_HITS];
	values->ammoRocket = client.ammo[WP_ROCKET_LAUNCHER];
	values->ammoRail = client.ammo[WP_RAILGUN];
	values->powerupQuad = client.powerups[PW_QUAD];
	values->powerupBattleSuit = client.powerups[PW_BATTLESUIT];
	values->unchangedStatArmor = client.stats[STAT_ARMOR];
	values->unchangedPersistantRank = client.persistant[PERS_RANK];
	values->unchangedAmmoMachinegun = client.ammo[WP_MACHINEGUN];
	values->unchangedPowerupHaste = client.powerups[PW_HASTE];
}
"""


def _block_from_marker(source: str, marker: str) -> str:
	start = source.index(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


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


class PlayerStateArrayReplication(ctypes.Structure):
	_fields_ = [
		("statHealth", ctypes.c_int),
		("statWeapons", ctypes.c_int),
		("statPlayerItemTime", ctypes.c_int),
		("persistantScore", ctypes.c_int),
		("persistantTeam", ctypes.c_int),
		("persistantHits", ctypes.c_int),
		("ammoRocket", ctypes.c_int),
		("ammoRail", ctypes.c_int),
		("powerupQuad", ctypes.c_int),
		("powerupBattleSuit", ctypes.c_int),
		("unchangedStatArmor", ctypes.c_int),
		("unchangedPersistantRank", ctypes.c_int),
		("unchangedAmmoMachinegun", ctypes.c_int),
		("unchangedPowerupHaste", ctypes.c_int),
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
	library.QLR_ReplicatePlayerStateArrays.argtypes = [ctypes.POINTER(PlayerStateArrayReplication)]
	library.QLR_ReplicatePlayerStateArrays.restype = None
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


def test_playerstate_array_masks_round_trip_changed_and_unchanged_slots(
	playerstate_library: ctypes.CDLL,
) -> None:
	values = PlayerStateArrayReplication()
	playerstate_library.QLR_ReplicatePlayerStateArrays(ctypes.byref(values))

	assert values.statHealth == 125
	assert values.statWeapons == (1 << 5) | (1 << 7)
	assert values.statPlayerItemTime == 2222
	assert values.persistantScore == 17
	assert values.persistantTeam == 1
	assert values.persistantHits == 3
	assert values.ammoRocket == 9
	assert values.ammoRail == 4
	assert values.powerupQuad == 12000
	assert values.powerupBattleSuit == 14000
	assert values.unchangedStatArmor == 150
	assert values.unchangedPersistantRank == 4
	assert values.unchangedAmmoMachinegun == 80
	assert values.unchangedPowerupHaste == 2222


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


def test_playerstate_netfield_table_matches_retail_quake_live_scalar_order() -> None:
	source = MSG_PATH.read_text(encoding="utf-8")
	spec = json.loads(PLAYERSTATE_FIELDS_SPEC_PATH.read_text(encoding="utf-8"))
	table_start = source.index("netField_t\tplayerStateFields[]")
	table_end = source.index("};", table_start) + len("};")
	table = source[table_start:table_end]
	entries = spec["source_of_truth"]["entries"]
	expected_entries = tuple(
		f"{{ PSF({entry['field']}), {entry['source_bits']} }}"
		for entry in entries
	)

	cursor = 0
	for entry in expected_entries:
		index = table.index(entry, cursor)
		cursor = index + len(entry)

	assert table.count("{ PSF(") == len(expected_entries)
	assert len(expected_entries) == spec["retail_table"]["field_count"] == 58
	assert entries[49]["field"] == "jumpTime"
	assert entries[50]["field"] == "doubleJumped"


def test_playerstate_delta_codec_preserves_retail_signed_byte_and_array_mask_wiring() -> None:
	source = MSG_PATH.read_text(encoding="utf-8")
	signed_byte_block = _block_from_marker(source, "static qboolean MSG_PlayerStateFieldIsSignedByte")
	network_value_block = _block_from_marker(source, "static int MSG_PlayerStateFieldNetworkValue")
	set_value_block = _block_from_marker(source, "static void MSG_SetPlayerStateFieldValue")
	write_block = _block_from_marker(source, "void MSG_WriteDeltaPlayerstate")
	read_block = _block_from_marker(source, "void MSG_ReadDeltaPlayerstate")

	for expected in (
		"field->offset == PSF_OFFSET(forwardmove)",
		"field->offset == PSF_OFFSET(rightmove)",
		"field->offset == PSF_OFFSET(upmove)",
	):
		assert expected in signed_byte_block

	assert "return (unsigned char)value;" in network_value_block
	assert "*(signed char *)( (byte *)ps + field->offset ) = (signed char)value;" in set_value_block
	assert "MSG_PlayerStateFieldNetworkValue( to, field )" in write_block
	assert "MSG_SetPlayerStateFieldValue( to, field, value );" in read_block
	assert "MSG_SetPlayerStateFieldValue( to, field, MSG_PlayerStateFieldValue( from, field ) );" in read_block

	for expected in (
		"statsbits = 0;",
		"persistantbits = 0;",
		"ammobits = 0;",
		"powerupbits = 0;",
		"MSG_WriteShort( msg, statsbits );",
		"MSG_WriteShort( msg, persistantbits );",
		"MSG_WriteShort( msg, ammobits );",
		"MSG_WriteShort( msg, powerupbits );",
		"MSG_WriteShort (msg, to->stats[i]);",
		"MSG_WriteShort (msg, to->persistant[i]);",
		"MSG_WriteShort (msg, to->ammo[i]);",
		"MSG_WriteLong( msg, to->powerups[i] );",
	):
		assert expected in write_block

	for expected in (
		'LOG("PS_STATS");',
		'LOG("PS_PERSISTANT");',
		'LOG("PS_AMMO");',
		'LOG("PS_POWERUPS");',
		"to->stats[i] = MSG_ReadShort(msg);",
		"to->persistant[i] = MSG_ReadShort(msg);",
		"to->ammo[i] = MSG_ReadShort(msg);",
		"to->powerups[i] = MSG_ReadLong(msg);",
	):
		assert expected in read_block


def test_playerstate_delta_codec_is_backed_by_committed_retail_mapping_evidence() -> None:
	aliases = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
	mapping_round = MAPPING_ROUND_57.read_text(encoding="utf-8")

	assert aliases["quakelive_steam_srp"]["sub_4D5D50"] == "MSG_WriteDeltaPlayerstate"
	assert aliases["quakelive_steam_srp"]["sub_4D66C0"] == "MSG_ReadDeltaPlayerstate"

	for expected in (
		"`sub_4D5D50 -> MSG_WriteDeltaPlayerstate`",
		"`sub_4D66C0 -> MSG_ReadDeltaPlayerstate`",
		"Quake Live's expanded `playerState_t`",
		"`PS_STATS`",
		"`PS_PERSISTANT`",
		"`PS_AMMO`",
		"`PS_POWERUPS`",
	):
		assert expected in mapping_round


def test_server_snapshot_writes_built_playerstate_before_packet_entities() -> None:
	source = SV_SNAPSHOT_PATH.read_text(encoding="utf-8")
	build_block = _block_from_marker(source, "static void SV_BuildClientSnapshot")
	write_block = _block_from_marker(source, "static void SV_WriteSnapshotToClient")
	send_block = _block_from_marker(source, "void SV_SendClientSnapshot")

	for expected in (
		"ps = SV_GameClientNum( client - svs.clients );",
		"frame->ps = *ps;",
		"clientNum = frame->ps.clientNum;",
		"svEnt->snapshotCounter = sv.snapshotCounter;",
		"VectorCopy( ps->origin, org );",
		"org[2] += ps->viewheight;",
		"SV_AddEntitiesVisibleFromPoint( org, frame, &entityNumbers, qfalse );",
		"frame->first_entity = svs.nextSnapshotEntities;",
	):
		assert expected in build_block

	assert build_block.index("ps = SV_GameClientNum( client - svs.clients );") < build_block.index("frame->ps = *ps;")
	assert build_block.index("frame->ps = *ps;") < build_block.index("clientNum = frame->ps.clientNum;")
	assert build_block.index("VectorCopy( ps->origin, org );") < build_block.index(
		"SV_AddEntitiesVisibleFromPoint( org, frame, &entityNumbers, qfalse );"
	)

	for expected in (
		"frame = &client->frames[ client->netchan.outgoingSequence & PACKET_MASK ];",
		"MSG_WriteByte (msg, svc_snapshot);",
		"MSG_WriteLong (msg, svs.time);",
		"MSG_WriteByte (msg, lastframe);",
		"MSG_WriteByte (msg, snapFlags);",
		"MSG_WriteByte (msg, frame->areabytes);",
		"MSG_WriteData (msg, frame->areabits, frame->areabytes);",
		"MSG_WriteDeltaPlayerstate( msg, &oldframe->ps, &frame->ps );",
		"MSG_WriteDeltaPlayerstate( msg, NULL, &frame->ps );",
		"SV_EmitPacketEntities (oldframe, frame, msg);",
	):
		assert expected in write_block

	assert write_block.index("MSG_WriteByte (msg, svc_snapshot);") < write_block.index("MSG_WriteLong (msg, svs.time);")
	assert write_block.index("MSG_WriteLong (msg, svs.time);") < write_block.index("MSG_WriteByte (msg, lastframe);")
	assert write_block.index("MSG_WriteByte (msg, snapFlags);") < write_block.index("MSG_WriteByte (msg, frame->areabytes);")
	assert write_block.index("MSG_WriteData (msg, frame->areabits, frame->areabytes);") < write_block.index(
		"MSG_WriteDeltaPlayerstate( msg,"
	)
	assert write_block.index("MSG_WriteDeltaPlayerstate( msg,") < write_block.index(
		"SV_EmitPacketEntities (oldframe, frame, msg);"
	)

	assert send_block.index("SV_BuildClientSnapshot( client );") < send_block.index(
		"if ( client->gentity && client->gentity->r.svFlags & SVF_BOT ) {"
	)
	assert send_block.index("SV_UpdateServerCommandsToClient( client, &msg );") < send_block.index(
		"SV_WriteSnapshotToClient( client, &msg );"
	)


def test_client_snapshot_parse_preserves_retail_playerstate_handoff_to_snapshot_ring() -> None:
	source = CL_PARSE_PATH.read_text(encoding="utf-8")
	parse_block = _block_from_marker(source, "void CL_ParseSnapshot")

	for expected in (
		"Com_Memset (&newSnap, 0, sizeof(newSnap));",
		"newSnap.serverCommandNum = clc.serverCommandSequence;",
		"newSnap.serverTime = MSG_ReadLong( msg );",
		"newSnap.messageNum = clc.serverMessageSequence;",
		"deltaNum = MSG_ReadByte( msg );",
		"newSnap.snapFlags = MSG_ReadByte( msg );",
		"len = MSG_ReadByte( msg );",
		"MSG_ReadData( msg, &newSnap.areamask, len);",
		'SHOWNET( msg, "playerstate" );',
		"MSG_ReadDeltaPlayerstate( msg, &old->ps, &newSnap.ps );",
		"MSG_ReadDeltaPlayerstate( msg, NULL, &newSnap.ps );",
		'SHOWNET( msg, "packet entities" );',
		"CL_ParsePacketEntities( msg, old, &newSnap );",
		"if ( !newSnap.valid ) {",
		"cl.snap = newSnap;",
		"cl.snap.ping = 999;",
		"if ( cl.snap.ps.commandTime >= cl.outPackets[ packetNum ].p_serverTime ) {",
		"cl.snapshots[cl.snap.messageNum & PACKET_MASK] = cl.snap;",
		"cl.newSnapshots = qtrue;",
	):
		assert expected in parse_block

	assert parse_block.index("newSnap.serverCommandNum = clc.serverCommandSequence;") < parse_block.index(
		"newSnap.serverTime = MSG_ReadLong( msg );"
	)
	assert parse_block.index("MSG_ReadData( msg, &newSnap.areamask, len);") < parse_block.index(
		'SHOWNET( msg, "playerstate" );'
	)
	assert parse_block.index('SHOWNET( msg, "playerstate" );') < parse_block.index(
		'SHOWNET( msg, "packet entities" );'
	)
	assert parse_block.index("CL_ParsePacketEntities( msg, old, &newSnap );") < parse_block.index(
		"if ( !newSnap.valid ) {"
	)
	assert parse_block.index("if ( !newSnap.valid ) {") < parse_block.index("cl.snap = newSnap;")
	assert parse_block.index("cl.snap = newSnap;") < parse_block.index("cl.snap.ping = 999;")
	assert parse_block.index("cl.snap.ping = 999;") < parse_block.index(
		"if ( cl.snap.ps.commandTime >= cl.outPackets[ packetNum ].p_serverTime ) {"
	)
	assert parse_block.index("if ( cl.snap.ps.commandTime >= cl.outPackets[ packetNum ].p_serverTime ) {") < parse_block.index(
		"cl.snapshots[cl.snap.messageNum & PACKET_MASK] = cl.snap;"
	)
	assert parse_block.index("cl.snapshots[cl.snap.messageNum & PACKET_MASK] = cl.snap;") < parse_block.index(
		"cl.newSnapshots = qtrue;"
	)


def test_cgame_snapshot_import_exposes_client_snapshot_playerstate_to_prediction() -> None:
	cl_cgame_source = CL_CGAME_PATH.read_text(encoding="utf-8")
	cg_syscalls_source = CG_SYSCALLS_PATH.read_text(encoding="utf-8")
	current_number_block = _block_from_marker(cl_cgame_source, "void\tCL_GetCurrentSnapshotNumber")
	get_snapshot_block = _block_from_marker(cl_cgame_source, "qboolean\tCL_GetSnapshot")
	syscall_block = _block_from_marker(cl_cgame_source, "static int CL_CgameSystemCallsImpl")
	map_native_block = _block_from_marker(cg_syscalls_source, "static int CG_MapNativeImport")
	trap_block = _block_from_marker(cg_syscalls_source, "qboolean\ttrap_GetSnapshot")

	for expected in (
		"*snapshotNumber = cl.snap.messageNum;",
		"*serverTime = cl.snap.serverTime;",
	):
		assert expected in current_number_block

	for expected in (
		"if ( snapshotNumber > cl.snap.messageNum ) {",
		"if ( cl.snap.messageNum - snapshotNumber >= PACKET_BACKUP ) {",
		"clSnap = &cl.snapshots[snapshotNumber & PACKET_MASK];",
		"if ( !clSnap->valid ) {",
		"if ( cl.parseEntitiesNum - clSnap->parseEntitiesNum >= MAX_PARSE_ENTITIES ) {",
		"snapshot->snapFlags = clSnap->snapFlags;",
		"snapshot->serverCommandSequence = clSnap->serverCommandNum;",
		"snapshot->ping = clSnap->ping;",
		"snapshot->serverTime = clSnap->serverTime;",
		"Com_Memcpy( snapshot->areamask, clSnap->areamask, sizeof( snapshot->areamask ) );",
		"snapshot->ps = clSnap->ps;",
		"if ( count > MAX_ENTITIES_IN_SNAPSHOT ) {",
		"snapshot->numEntities = count;",
	):
		assert expected in get_snapshot_block

	assert get_snapshot_block.index("Com_Memcpy( snapshot->areamask") < get_snapshot_block.index("snapshot->ps = clSnap->ps;")
	assert get_snapshot_block.index("snapshot->ps = clSnap->ps;") < get_snapshot_block.index("count = clSnap->numEntities;")
	assert get_snapshot_block.index("if ( count > MAX_ENTITIES_IN_SNAPSHOT ) {") < get_snapshot_block.index(
		"snapshot->numEntities = count;"
	)

	assert "case CG_GETCURRENTSNAPSHOTNUMBER:" in syscall_block
	assert "CL_GetCurrentSnapshotNumber( VMA(1), VMA(2) );" in syscall_block
	assert "case CG_GETSNAPSHOT:" in syscall_block
	assert "return CL_GetSnapshot( args[1], VMA(2) ) ? qtrue : qfalse;" in syscall_block
	assert syscall_block.index("case CG_GETCURRENTSNAPSHOTNUMBER:") < syscall_block.index("case CG_GETSNAPSHOT:")
	assert "case CG_GETSNAPSHOT: return CG_QL_IMPORT_GETSNAPSHOT;" in map_native_block
	assert "return syscall( CG_GETSNAPSHOT, snapshotNumber, snapshot ) ? qtrue : qfalse;" in trap_block


def test_snapshot_playerstate_transport_is_backed_by_committed_retail_mapping_evidence() -> None:
	aliases = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	round_17 = MAPPING_ROUND_17.read_text(encoding="utf-8")
	round_65 = MAPPING_ROUND_65.read_text(encoding="utf-8")
	round_127 = MAPPING_ROUND_127.read_text(encoding="utf-8")

	expected_aliases = {
		"sub_4B0130": "QLCGImport_GetCurrentSnapshotNumber",
		"sub_4B0150": "QLCGImport_GetSnapshot",
		"sub_4BD350": "CL_ParseSnapshot",
		"sub_4E50E0": "SV_WriteSnapshotToClient",
		"sub_4E5680": "SV_BuildClientSnapshot",
		"sub_4E5AC0": "SV_SendClientSnapshot",
	}

	for address, normalized_name in expected_aliases.items():
		assert aliases[address] == normalized_name

	for expected in (
		"matches `CL_GetSnapshot`",
		"copies the playerstate/areamask/entity list",
		"Retail cgame calls `(*(data_1074CCCC + 0x15C))(snapshotNumber, snapshotOut)`",
	):
		assert expected in round_17

	for expected in (
		"`sub_4E50E0 -> SV_WriteSnapshotToClient`",
		"`sub_4E5680 -> SV_BuildClientSnapshot`",
		"`sub_4E5AC0 -> SV_SendClientSnapshot`",
		"areabits, playerstate, and packet entities in the retained order",
	):
		assert expected in round_65

	assert "`sub_4BD350` -> `CL_ParseSnapshot`" in round_127
