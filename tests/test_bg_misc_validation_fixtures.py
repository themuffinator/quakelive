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
PW_QUAD = 1
PW_FLIGHT = 6
PW_REDFLAG = 7
PW_BLUEFLAG = 8
PW_NEUTRALFLAG = 9
PW_SCOUT = 10
PW_GUARD = 11
PW_DOUBLER = 12
PW_AMMOREGEN = 13
PW_INVULNERABILITY = 14
PM_NORMAL = 0
PM_SPECTATOR = 2
PM_INTERMISSION = 5
EV_JUMP_PAD = 9
EV_JUMP = 10
EV_FALL_FAR = 8
ET_PLAYER = 1
ET_INVISIBLE = 10
EF_DEAD = 1
HI_NONE = 0
HI_INVULNERABILITY = 5
IT_WEAPON = 1
IT_HOLDABLE = 6
WP_NONE = 0
WP_GAUNTLET = 1
WP_MACHINEGUN = 2
WP_HEAVY_MACHINEGUN = 3
WP_SHOTGUN = 4
WP_GRENADE_LAUNCHER = 5
WP_ROCKET_LAUNCHER = 6
WP_LIGHTNING = 7
WP_RAILGUN = 8
WP_PLASMAGUN = 9
WP_BFG = 10
WP_GRAPPLING_HOOK = 11
WP_NAILGUN = 12
WP_PROX_LAUNCHER = 13
WP_CHAINGUN = 14
WP_NUM_WEAPONS = 15
ITEMTAG_WEAPON_GAUNTLET = 1
ITEMTAG_WEAPON_MACHINEGUN = 2
ITEMTAG_WEAPON_SHOTGUN = 3
ITEMTAG_WEAPON_GRENADE_LAUNCHER = 4
ITEMTAG_WEAPON_ROCKET_LAUNCHER = 5
ITEMTAG_WEAPON_LIGHTNING = 6
ITEMTAG_WEAPON_RAILGUN = 7
ITEMTAG_WEAPON_PLASMAGUN = 8
ITEMTAG_WEAPON_BFG = 9
ITEMTAG_WEAPON_GRAPPLING_HOOK = 10
ITEMTAG_WEAPON_NAILGUN = 11
ITEMTAG_WEAPON_PROX_LAUNCHER = 12
ITEMTAG_WEAPON_CHAINGUN = 13
ITEMTAG_WEAPON_HEAVY_MACHINEGUN = 14
ITEMTAG_HOLDABLE_INVULNERABILITY = 6
HANDICAP_SCALAR_PICKUP = 0
HANDICAP_SCALAR_ARMOR = 1
HANDICAP_SCALAR_HEALTH = 2
HANDICAP_SCALAR_RESPAWN = 3
HANDICAP_SCALAR_MAX = 4

WEAPON_STAT_ROWS = [
	(WP_GAUNTLET, b"Gauntlet", ITEMTAG_WEAPON_GAUNTLET, 0, 0, -1, 0, 0, 847, 1000, 1000),
	(WP_MACHINEGUN, b"Machine Gun", ITEMTAG_WEAPON_MACHINEGUN, 200, 50, 200, 0, 1000, 1000, 0, 1000),
	(WP_HEAVY_MACHINEGUN, b"Heavy Machinegun", ITEMTAG_WEAPON_HEAVY_MACHINEGUN, 200, 50, 200, 1, 807, 647, 0, 1000),
	(WP_SHOTGUN, b"Shotgun", ITEMTAG_WEAPON_SHOTGUN, 40, 10, 40, 1, 1000, 490, 0, 1000),
	(WP_GRENADE_LAUNCHER, b"Grenade Launcher", ITEMTAG_WEAPON_GRENADE_LAUNCHER, 20, 5, 20, 0, 7, 564, 70, 1000),
	(WP_ROCKET_LAUNCHER, b"Rocket Launcher", ITEMTAG_WEAPON_ROCKET_LAUNCHER, 20, 5, 20, 1, 1000, 3, 3, 1000),
	(WP_LIGHTNING, b"Lightning Gun", ITEMTAG_WEAPON_LIGHTNING, 240, 60, 240, 1, 1000, 1000, 729, 1000),
	(WP_RAILGUN, b"Railgun", ITEMTAG_WEAPON_RAILGUN, 40, 10, 40, 1, 0, 1000, 0, 1000),
	(WP_PLASMAGUN, b"Plasma Gun", ITEMTAG_WEAPON_PLASMAGUN, 120, 30, 120, 1, 772, 0, 1000, 1000),
	(WP_BFG, b"BFG10K", ITEMTAG_WEAPON_BFG, 60, 15, 60, 0, 3, 352, 1000, 1000),
	(WP_GRAPPLING_HOOK, b"Grappling Hook", ITEMTAG_WEAPON_GRAPPLING_HOOK, 0, 0, -1, 0, 317, 666, 862, 1000),
	(WP_NAILGUN, b"Nailgun", ITEMTAG_WEAPON_NAILGUN, 80, 20, 80, 0, 0, 1000, 701, 1000),
	(WP_PROX_LAUNCHER, b"Prox Launcher", ITEMTAG_WEAPON_PROX_LAUNCHER, 40, 10, 40, 0, 1000, 0, 486, 1000),
	(WP_CHAINGUN, b"Chaingun", ITEMTAG_WEAPON_CHAINGUN, 400, 100, 400, 0, 721, 721, 721, 1000),
]


def _find_c_compiler() -> str:
	compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
	if not compiler:
		pytest.skip("No C compiler found for bg_misc validation fixtures")

	return compiler


@pytest.fixture(scope="session")
def bg_misc_validation_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("bg_misc_validation_harness")
	lib_path = build_dir / ("bg_misc_validation_harness.dll" if os.name == "nt" else "libbg_misc_validation_harness.so")
	compile_args = [_find_c_compiler(), "-std=c99", "-shared", "-DQAGAME"]

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
	library.QLR_GetWeaponName.argtypes = [ctypes.c_int]
	library.QLR_GetWeaponName.restype = ctypes.c_char_p
	library.QLR_ItemTagForWeapon.argtypes = [ctypes.c_int]
	library.QLR_ItemTagForWeapon.restype = ctypes.c_int
	library.QLR_WeaponForItemTag.argtypes = [ctypes.c_int]
	library.QLR_WeaponForItemTag.restype = ctypes.c_int
	library.QLR_ItemTagForHoldable.argtypes = [ctypes.c_int]
	library.QLR_ItemTagForHoldable.restype = ctypes.c_int
	library.QLR_HoldableForItemTag.argtypes = [ctypes.c_int]
	library.QLR_HoldableForItemTag.restype = ctypes.c_int
	library.QLR_GetWeaponMaxAmmo.argtypes = [ctypes.c_int]
	library.QLR_GetWeaponMaxAmmo.restype = ctypes.c_int
	library.QLR_GetWeaponAmmoPackSize.argtypes = [ctypes.c_int]
	library.QLR_GetWeaponAmmoPackSize.restype = ctypes.c_int
	library.QLR_GetWeaponAmmoPackMaxStack.argtypes = [ctypes.c_int]
	library.QLR_GetWeaponAmmoPackMaxStack.restype = ctypes.c_int
	library.QLR_GetWeaponStatsCount.argtypes = []
	library.QLR_GetWeaponStatsCount.restype = ctypes.c_int
	library.QLR_GetWeaponStatsFlags.argtypes = [ctypes.c_int]
	library.QLR_GetWeaponStatsFlags.restype = ctypes.c_int
	library.QLR_GetHandicapScalarPermille.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_GetHandicapScalarPermille.restype = ctypes.c_int
	library.QLR_FindItemIndexByPickupName.argtypes = [ctypes.c_char_p]
	library.QLR_FindItemIndexByPickupName.restype = ctypes.c_int
	library.QLR_FindItemIndexByClassname.argtypes = [ctypes.c_char_p]
	library.QLR_FindItemIndexByClassname.restype = ctypes.c_int
	library.QLR_FindItemIndexByTypeAndTag.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_FindItemIndexByTypeAndTag.restype = ctypes.c_int
	library.QLR_PlayerHasPersistantPowerupByClassname.argtypes = [
		ctypes.c_char_p,
		ctypes.c_int,
	]
	library.QLR_PlayerHasPersistantPowerupByClassname.restype = ctypes.c_int
	library.QLR_PlayerHasPersistantPowerupWithIndex.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_PlayerHasPersistantPowerupWithIndex.restype = ctypes.c_int
	library.QLR_GetHealthArmorBoundsSnapshot.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_GetHealthArmorBoundsSnapshot.restype = ctypes.c_int
	library.QLR_ClearArmorTierIfEmpty.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_ClearArmorTierIfEmpty.restype = ctypes.c_int
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
	library.QLR_CanGrabArmorItem.argtypes = [
		ctypes.c_char_p,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_CanGrabArmorItem.restype = ctypes.c_int
	library.QLR_ApplyArmorPickup.argtypes = [
		ctypes.c_char_p,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_ApplyArmorPickup.restype = ctypes.c_int
	library.QLR_UpdateArmorTier.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_UpdateArmorTier.restype = ctypes.c_int
	library.QLR_GetArmorRegenTarget.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_GetArmorRegenTarget.restype = ctypes.c_int
	library.QLR_CanGrabCtfFlag.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_CanGrabCtfFlag.restype = ctypes.c_int
	library.QLR_AddPredictableEventSnapshot.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_AddPredictableEventSnapshot.restype = ctypes.c_int
	library.QLR_TouchJumpPadSnapshot.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_TouchJumpPadSnapshot.restype = ctypes.c_int
	library.QLR_TouchJumpPadVelocityZ.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_TouchJumpPadVelocityZ.restype = ctypes.c_int
	library.QLR_ProjectPredictableEventSnapshot.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_ProjectPredictableEventSnapshot.restype = ctypes.c_int
	library.QLR_ProjectExternalEventSnapshot.argtypes = []
	library.QLR_ProjectExternalEventSnapshot.restype = ctypes.c_int
	library.QLR_ProjectPlayerStateVisibilitySnapshot.argtypes = [
		ctypes.c_int,
		ctypes.c_int,
		ctypes.c_int,
	]
	library.QLR_ProjectPlayerStateVisibilitySnapshot.restype = ctypes.c_int
	library.QLR_ProjectPlayerStateReplicationSnapshotA.argtypes = []
	library.QLR_ProjectPlayerStateReplicationSnapshotA.restype = ctypes.c_int
	library.QLR_ProjectPlayerStateReplicationSnapshotB.argtypes = []
	library.QLR_ProjectPlayerStateReplicationSnapshotB.restype = ctypes.c_int
	return library


def _packed_armor_state(value: int) -> tuple[int, int]:
	return value >> 8, value & 0xff


def _packed_event_snapshot(value: int) -> tuple[int, int, int, int]:
	return (value >> 24) & 0xff, (value >> 12) & 0x3ff, (value >> 4) & 0xff, value & 0xf


def _packed_bounds_snapshot(value: int) -> tuple[int, int]:
	return (value >> 16) & 0xffff, value & 0xffff


def _packed_visibility_snapshot(value: int) -> tuple[int, int, int, int]:
	return (value >> 28) & 0xf, (value >> 16) & 0xfff, (value >> 8) & 0xff, value & 0xff


def _packed_projection_snapshot_a(value: int) -> tuple[int, int, int, int]:
	return (value >> 24) & 0xff, (value >> 16) & 0xff, (value >> 8) & 0xff, value & 0xff


def _packed_projection_snapshot_b(value: int) -> tuple[int, int, int]:
	return (value >> 24) & 0xff, (value >> 16) & 0xff, value & 0xffff


def test_weapon_stat_and_tag_helper_fixtures_cover_top_level_bg_misc_bridges(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_GetWeaponName(WP_HEAVY_MACHINEGUN) == b"Heavy Machinegun"
	assert bg_misc_validation_harness.QLR_GetWeaponName(WP_SHOTGUN) == b"Shotgun"
	assert bg_misc_validation_harness.QLR_GetWeaponName(WP_NONE) == b"None"
	assert bg_misc_validation_harness.QLR_GetWeaponName(WP_NUM_WEAPONS) == b"None"

	assert bg_misc_validation_harness.QLR_ItemTagForWeapon(WP_HEAVY_MACHINEGUN) == ITEMTAG_WEAPON_HEAVY_MACHINEGUN
	assert bg_misc_validation_harness.QLR_ItemTagForWeapon(WP_SHOTGUN) == ITEMTAG_WEAPON_SHOTGUN
	assert bg_misc_validation_harness.QLR_ItemTagForWeapon(WP_NUM_WEAPONS) == WP_NUM_WEAPONS
	assert bg_misc_validation_harness.QLR_ItemTagForWeapon(-1) == WP_NONE
	assert bg_misc_validation_harness.QLR_WeaponForItemTag(ITEMTAG_WEAPON_HEAVY_MACHINEGUN) == WP_HEAVY_MACHINEGUN
	assert bg_misc_validation_harness.QLR_WeaponForItemTag(ITEMTAG_WEAPON_CHAINGUN) == WP_CHAINGUN
	assert bg_misc_validation_harness.QLR_WeaponForItemTag(WP_NUM_WEAPONS) == WP_NUM_WEAPONS
	assert bg_misc_validation_harness.QLR_WeaponForItemTag(99) == WP_NONE

	assert bg_misc_validation_harness.QLR_ItemTagForHoldable(HI_INVULNERABILITY) == ITEMTAG_HOLDABLE_INVULNERABILITY
	assert bg_misc_validation_harness.QLR_HoldableForItemTag(ITEMTAG_HOLDABLE_INVULNERABILITY) == HI_INVULNERABILITY
	assert bg_misc_validation_harness.QLR_HoldableForItemTag(5) == HI_NONE

	assert bg_misc_validation_harness.QLR_GetWeaponMaxAmmo(WP_HEAVY_MACHINEGUN) == 200
	assert bg_misc_validation_harness.QLR_GetWeaponMaxAmmo(WP_CHAINGUN) == 400
	assert bg_misc_validation_harness.QLR_GetWeaponMaxAmmo(WP_GAUNTLET) == 0
	assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackSize(WP_HEAVY_MACHINEGUN) == 50
	assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackSize(WP_CHAINGUN) == 100
	assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackMaxStack(WP_HEAVY_MACHINEGUN) == 200
	assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackMaxStack(WP_GAUNTLET) == -1

	assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_PICKUP, WP_HEAVY_MACHINEGUN) == 807
	assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_ARMOR, WP_SHOTGUN) == 490
	assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_HEALTH, WP_LIGHTNING) == 729
	assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_MAX, WP_RAILGUN) == 1000
	assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_PICKUP, WP_NUM_WEAPONS) == 1000


def test_full_weapon_stat_table_fixture_matches_recovered_retail_rows(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_GetWeaponStatsCount() == len(WEAPON_STAT_ROWS)

	for (
		weapon,
		name,
		item_tag,
		max_ammo,
		pack_size,
		max_stack,
		flags,
		pickup_scale,
		armor_scale,
		health_scale,
		respawn_scale,
	) in WEAPON_STAT_ROWS:
		assert bg_misc_validation_harness.QLR_GetWeaponName(weapon) == name
		assert bg_misc_validation_harness.QLR_ItemTagForWeapon(weapon) == item_tag
		assert bg_misc_validation_harness.QLR_WeaponForItemTag(item_tag) == weapon
		assert bg_misc_validation_harness.QLR_GetWeaponMaxAmmo(weapon) == max_ammo
		assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackSize(weapon) == pack_size
		assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackMaxStack(weapon) == max_stack
		assert bg_misc_validation_harness.QLR_GetWeaponStatsFlags(weapon) == flags
		assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_PICKUP, weapon) == pickup_scale
		assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_ARMOR, weapon) == armor_scale
		assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_HEALTH, weapon) == health_scale
		assert bg_misc_validation_harness.QLR_GetHandicapScalarPermille(HANDICAP_SCALAR_RESPAWN, weapon) == respawn_scale

	assert bg_misc_validation_harness.QLR_GetWeaponStatsFlags(WP_NONE) == -1
	assert bg_misc_validation_harness.QLR_GetWeaponMaxAmmo(WP_NUM_WEAPONS) == 0
	assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackSize(WP_NUM_WEAPONS) == 0
	assert bg_misc_validation_harness.QLR_GetWeaponAmmoPackMaxStack(WP_NUM_WEAPONS) == 0


def test_item_lookup_fixtures_cover_pickup_name_classname_and_type_tag_paths(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	hmg_index = bg_misc_validation_harness.QLR_FindItemIndexByClassname(b"weapon_hmg")
	invuln_index = bg_misc_validation_harness.QLR_FindItemIndexByClassname(b"holdable_invulnerability")

	assert hmg_index > 0
	assert invuln_index > 0
	assert bg_misc_validation_harness.QLR_FindItemIndexByClassname(b"WEAPON_HMG") == hmg_index
	assert bg_misc_validation_harness.QLR_FindItemIndexByClassname(b"") == 0
	assert bg_misc_validation_harness.QLR_FindItemIndexByClassname(None) == 0
	assert bg_misc_validation_harness.QLR_FindItemIndexByPickupName(b"Heavy Machinegun") == hmg_index
	assert bg_misc_validation_harness.QLR_FindItemIndexByPickupName(b"heavy machinegun") == hmg_index
	assert bg_misc_validation_harness.QLR_FindItemIndexByPickupName(b"weapon_hmg") == 0
	assert bg_misc_validation_harness.QLR_FindItemIndexByTypeAndTag(
		IT_WEAPON,
		ITEMTAG_WEAPON_HEAVY_MACHINEGUN,
	) == hmg_index
	assert bg_misc_validation_harness.QLR_FindItemIndexByTypeAndTag(
		IT_HOLDABLE,
		ITEMTAG_HOLDABLE_INVULNERABILITY,
	) == invuln_index
	assert bg_misc_validation_harness.QLR_FindItemIndexByTypeAndTag(IT_WEAPON, WP_NUM_WEAPONS) == 0


def test_small_policy_helper_fixtures_cover_bounds_and_powerup_guards(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_PlayerHasPersistantPowerupByClassname(b"item_scout", PW_SCOUT) == 1
	assert bg_misc_validation_harness.QLR_PlayerHasPersistantPowerupByClassname(b"item_scout", PW_GUARD) == 0
	assert bg_misc_validation_harness.QLR_PlayerHasPersistantPowerupByClassname(b"", PW_SCOUT) == 0
	assert bg_misc_validation_harness.QLR_PlayerHasPersistantPowerupWithIndex(0, PW_SCOUT) == 0
	assert bg_misc_validation_harness.QLR_PlayerHasPersistantPowerupWithIndex(9999, PW_SCOUT) == 0
	assert bg_misc_validation_harness.QLR_PlayerHasPersistantPowerupByClassname(b"item_scout", PW_NONE) == 0

	assert _packed_bounds_snapshot(
		bg_misc_validation_harness.QLR_GetHealthArmorBoundsSnapshot(125, 25)
	) == (250, 125)
	assert _packed_bounds_snapshot(
		bg_misc_validation_harness.QLR_GetHealthArmorBoundsSnapshot(125, 5)
	) == (250, 250)
	assert _packed_bounds_snapshot(
		bg_misc_validation_harness.QLR_GetHealthArmorBoundsSnapshot(125, 100)
	) == (250, 250)

	assert bg_misc_validation_harness.QLR_ClearArmorTierIfEmpty(0, 2, 1) == 0
	assert bg_misc_validation_harness.QLR_ClearArmorTierIfEmpty(1, 2, 1) == 2
	assert bg_misc_validation_harness.QLR_ClearArmorTierIfEmpty(1, 2, 0) == 0


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


def test_armor_pickup_fixture_preserves_classic_and_tiered_retail_gates(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_body", 199, 2, 100, 0, 1) == 1
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_body", 200, 2, 100, 0, 1) == 0
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_body", 199, 2, 100, 1, 1) == 1
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_body", 200, 2, 100, 1, 1) == 0
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_combat", 132, 2, 100, 1, 0) == 1
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_combat", 133, 2, 100, 1, 0) == 0
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_jacket", 75, 1, 100, 1, 0) == 1
	assert bg_misc_validation_harness.QLR_CanGrabArmorItem(b"item_armor_jacket", 76, 1, 100, 1, 0) == 0


def test_armor_application_fixture_preserves_retail_pickup_and_regen_helpers(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert _packed_armor_state(
		bg_misc_validation_harness.QLR_ApplyArmorPickup(b"item_armor_body", 175, 0, 100, 0)
	) == (200, 0)
	assert _packed_armor_state(
		bg_misc_validation_harness.QLR_ApplyArmorPickup(b"item_armor_body", 75, 0, 100, 1)
	) == (200, 2)
	assert _packed_armor_state(
		bg_misc_validation_harness.QLR_ApplyArmorPickup(b"item_armor_combat", 60, 0, 100, 1)
	) == (150, 1)
	assert _packed_armor_state(
		bg_misc_validation_harness.QLR_ApplyArmorPickup(b"item_armor_jacket", 60, 2, 100, 1)
	) == (100, 0)
	assert _packed_armor_state(
		bg_misc_validation_harness.QLR_ApplyArmorPickup(b"item_armor_shard", 20, 2, 100, 1)
	) == (22, 2)

	assert bg_misc_validation_harness.QLR_UpdateArmorTier(99, 1) == 0
	assert bg_misc_validation_harness.QLR_UpdateArmorTier(100, 1) == 1
	assert bg_misc_validation_harness.QLR_UpdateArmorTier(149, 1) == 1
	assert bg_misc_validation_harness.QLR_UpdateArmorTier(150, 1) == 2
	assert bg_misc_validation_harness.QLR_UpdateArmorTier(150, 0) == 0

	assert bg_misc_validation_harness.QLR_GetArmorRegenTarget(125, 0, 0) == 125
	assert bg_misc_validation_harness.QLR_GetArmorRegenTarget(125, 0, 1) == 50
	assert bg_misc_validation_harness.QLR_GetArmorRegenTarget(125, 1, 1) == 100
	assert bg_misc_validation_harness.QLR_GetArmorRegenTarget(125, 2, 1) == 150


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


def test_predictable_event_and_jump_pad_fixtures_cover_shared_event_transport(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert _packed_event_snapshot(
		bg_misc_validation_harness.QLR_AddPredictableEventSnapshot(3, EV_FALL_FAR, 22)
	) == (4, EV_FALL_FAR, 22, 1)

	assert _packed_event_snapshot(
		bg_misc_validation_harness.QLR_TouchJumpPadSnapshot(PM_NORMAL, 0, 0)
	) == (1, EV_JUMP_PAD, 0, 7)
	assert bg_misc_validation_harness.QLR_TouchJumpPadVelocityZ(PM_NORMAL, 0, 0) == 30
	assert _packed_event_snapshot(
		bg_misc_validation_harness.QLR_TouchJumpPadSnapshot(PM_NORMAL, 0, 7)
	) == (0, 0, 0, 7)
	assert bg_misc_validation_harness.QLR_TouchJumpPadVelocityZ(PM_SPECTATOR, 0, 0) == 0
	assert bg_misc_validation_harness.QLR_TouchJumpPadVelocityZ(PM_NORMAL, 1, 0) == 0

	assert _packed_event_snapshot(
		bg_misc_validation_harness.QLR_ProjectPredictableEventSnapshot(0, 1)
	) == (1, EV_JUMP, 11, ET_PLAYER)
	assert _packed_event_snapshot(
		bg_misc_validation_harness.QLR_ProjectPredictableEventSnapshot(0, 5)
	) == (4, EV_FALL_FAR | 0x300, 22, ET_PLAYER)
	assert _packed_event_snapshot(
		bg_misc_validation_harness.QLR_ProjectExternalEventSnapshot()
	) == (0, EV_FALL_FAR, 55, ET_PLAYER)


def test_playerstate_projection_fixture_covers_visibility_and_replication_fields(
	bg_misc_validation_harness: ctypes.CDLL,
) -> None:
	assert _packed_visibility_snapshot(
		bg_misc_validation_harness.QLR_ProjectPlayerStateVisibilitySnapshot(PM_NORMAL, 100, 0x20)
	) == (ET_PLAYER, 0x20, 17, 17)
	assert _packed_visibility_snapshot(
		bg_misc_validation_harness.QLR_ProjectPlayerStateVisibilitySnapshot(PM_SPECTATOR, 100, 0x20)
	) == (ET_INVISIBLE, 0x20, 17, 17)
	assert _packed_visibility_snapshot(
		bg_misc_validation_harness.QLR_ProjectPlayerStateVisibilitySnapshot(PM_INTERMISSION, 100, 0)
	) == (ET_INVISIBLE, 0, 17, 17)
	assert _packed_visibility_snapshot(
		bg_misc_validation_harness.QLR_ProjectPlayerStateVisibilitySnapshot(PM_NORMAL, 0, 0x20)
	) == (ET_PLAYER, 0x20 | EF_DEAD, 17, 17)
	assert _packed_visibility_snapshot(
		bg_misc_validation_harness.QLR_ProjectPlayerStateVisibilitySnapshot(PM_NORMAL, -40, 0)
	) == (ET_INVISIBLE, EF_DEAD, 17, 17)

	assert _packed_projection_snapshot_a(
		bg_misc_validation_harness.QLR_ProjectPlayerStateReplicationSnapshotA()
	) == (WP_ROCKET_LAUNCHER, 42, 7, 3)
	assert _packed_projection_snapshot_b(
		bg_misc_validation_harness.QLR_ProjectPlayerStateReplicationSnapshotB()
	) == (21, 22, (1 << PW_QUAD) | (1 << PW_FLIGHT) | (1 << PW_BLUEFLAG))
