from __future__ import annotations

import ctypes
import json
import math
import re
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_INTERNAL_HARNESS = REPO_ROOT / "tests" / "botlib_internal_harness.c"
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
BOTLIB_BE_AAS_H = REPO_ROOT / "src" / "code" / "game" / "be_aas.h"
BOTLIB_AAS_ENTITY = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_entity.c"
BOTLIB_AAS_SAMPLE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_sample.c"
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"
BOTLIB_AAS_REACH = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_reach.c"
BOTLIB_AAS_ROUTE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_route.c"
BOTLIB_AI_CHAT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_chat.c"
BOTLIB_AI_CHAR = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_char.c"
BOTLIB_AI_GOAL = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_goal.c"
BOTLIB_AI_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c"
BOTLIB_AI_WEAP = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weap.c"
BOTLIB_AI_WEIGHT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weight.c"
BOTLIB_EA = REPO_ROOT / "src" / "code" / "botlib" / "be_ea.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_INTERFACE_H = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.h"
BOTLIB_L_PRECOMP = REPO_ROOT / "src" / "code" / "botlib" / "l_precomp.c"
BOTLIB_L_STRUCT = REPO_ROOT / "src" / "code" / "botlib" / "l_struct.c"
SERVER_BOT = REPO_ROOT / "src" / "code" / "server" / "sv_bot.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
GAME_BE_AI_GOAL_H = REPO_ROOT / "src" / "code" / "game" / "be_ai_goal.h"
GAME_MEM = REPO_ROOT / "src" / "code" / "game" / "g_mem.c"
GAME_PUBLIC_H = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
QAGAME_GHIDRA_TOP = REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "qagamex86" / "decompile_top_functions.c"
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QAGAME_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part01.txt"
)
QAGAME_HLIL_TYPE_00078 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "split"
	/ "types"
	/ "qagamex86.dll.bndb_hlil_type_00078_block.txt"
)
QAGAME_HLIL_TYPE_00085 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "split"
	/ "types"
	/ "qagamex86.dll.bndb_hlil_type_00085_block.txt"
)
QL_STEAM_GHIDRA_DECOMP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "decompile_top_functions.c"
)
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
QL_STEAM_HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_GHIDRA_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)

PRESENCE_NORMAL = 2
PRESENCE_CROUCH = 4
PRT_FATAL = 4
TRAVELFLAG_NOTTEAM1 = 1 << 24
TRAVELFLAG_NOTTEAM2 = 2 << 24
MFL_ONGROUND = 2
MFL_SWIMMING = 4
MFL_WATERJUMP = 16
MFL_TELEPORTED = 32
MFL_GRAPPLEPULL = 64
MFL_WALK = 512

BOTLIB_EXPORT_CORE_TAIL = (
	("BotLibSetup", "Export_BotLibSetup", "4A7CE0", "data_16dda50", "004a8427", None),
	("BotLibShutdown", "Export_BotLibShutdown", "4A7DC0", "data_16dda54", "004a8431", None),
	("BotLibVarSet", "Export_BotLibVarSet", "4A7E40", "data_16dda58", "004a843b", 23),
	("BotLibVarGet", "Export_BotLibVarGet", "4A7E60", "data_16dda5c", "004a8445", 46),
	("PC_AddGlobalDefine", "PC_AddGlobalDefine", "4AD200", "data_16dda60", "004a844f", 42),
	("PC_LoadSourceHandle", "PC_LoadSourceHandle", "4AC260", "data_16dda64", "004a8459", 230),
	("PC_FreeSourceHandle", "PC_FreeSourceHandle", "4AC350", "data_16dda68", "004a8463", 59),
	("PC_ReadTokenHandle", "PC_ReadTokenHandle", "4ACB10", "data_16dda6c", "004a846d", 163),
	("PC_SourceFileAndLine", "PC_SourceFileAndLine", "4AC390", "data_16dda70", "004a8477", 100),
	("BotLibStartFrame", "Export_BotLibStartFrame", "4A7E90", "data_16dda74", "004a8481", 57),
	("BotLibLoadMap", "Export_BotLibLoadMap", "4A7ED0", "data_16dda78", "004a848b", 99),
	("BotLibUpdateEntity", "Export_BotLibUpdateEntity", "4A7F40", "data_16dda7c", "004a8495", 102),
	("Test", "BotExportTest", "4D7970", "data_16dda80", "004a849f", 3),
)


class BotGoal(ctypes.Structure):
	_fields_ = [
		("origin", ctypes.c_float * 3),
		("areanum", ctypes.c_int),
		("mins", ctypes.c_float * 3),
		("maxs", ctypes.c_float * 3),
		("entitynum", ctypes.c_int),
		("number", ctypes.c_int),
		("flags", ctypes.c_int),
		("iteminfo", ctypes.c_int),
		("qlGoalExtra", ctypes.c_int * 2),
	]


class BotInitMove(ctypes.Structure):
	_fields_ = [
		("origin", ctypes.c_float * 3),
		("velocity", ctypes.c_float * 3),
		("viewoffset", ctypes.c_float * 3),
		("entitynum", ctypes.c_int),
		("client", ctypes.c_int),
		("thinktime", ctypes.c_float),
		("presencetype", ctypes.c_int),
		("viewangles", ctypes.c_float * 3),
		("or_moveflags", ctypes.c_int),
	]


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _vec3(*values: float) -> ctypes.Array[ctypes.c_float]:
	assert len(values) == 3
	return (ctypes.c_float * 3)(*values)


def _goal(number: int, origin: tuple[float, float, float]) -> BotGoal:
	goal = BotGoal()
	goal.origin[:] = origin
	goal.areanum = number + 100
	goal.mins[:] = (-15.0, -15.0, -24.0)
	goal.maxs[:] = (15.0, 15.0, 32.0)
	goal.entitynum = number + 200
	goal.number = number
	goal.flags = 1
	goal.iteminfo = number + 300
	return goal


def test_qagame_activate_goal_layout_and_setup_lifecycle_match_retail_references() -> None:
	ai_main = GAME_AI_MAIN.read_text(encoding="utf-8")
	be_ai_goal_h = GAME_BE_AI_GOAL_H.read_text(encoding="utf-8")
	g_mem = GAME_MEM.read_text(encoding="utf-8")
	harness = BOTLIB_INTERNAL_HARNESS.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART01.read_text(encoding="utf-8")
	qagame_type78 = QAGAME_HLIL_TYPE_00078.read_text(encoding="utf-8")
	qagame_type85 = QAGAME_HLIL_TYPE_00085.read_text(encoding="utf-8")
	qagame_ghidra = QAGAME_GHIDRA_TOP.read_text(encoding="utf-8")
	setup_block = _extract_function_block(
		ai_main,
		"int BotAISetupClient(int client, struct bot_settings_s *settings, qboolean restart)",
	)

	assert ctypes.sizeof(BotGoal) == 0x40
	assert "int qlGoalExtra[2];" in be_ai_goal_h
	assert "int qlGoalExtra[ 2 ];" in harness
	assert "#define POOLSIZE\t(4 * 1024 * 1024)" in g_mem

	assert "if (!botstates[client]) {" in setup_block
	assert "botstates[client] = G_Alloc(sizeof(bot_state_t));" in setup_block
	assert "memset(botstates[client], 0, sizeof(bot_state_t));" in setup_block
	assert setup_block.index("if (bs->inuse)") < setup_block.index("memset(bs, 0, sizeof(bot_state_t));")
	assert setup_block.index("memset(bs, 0, sizeof(bot_state_t));") < setup_block.index("if (!trap_AAS_Initialized())")
	assert "goto setup_failed_goal;" in setup_block
	assert "goto setup_failed_weapon;" in setup_block
	assert "goto setup_failed_chat;" in setup_block
	assert "setup_failed_chat:" in setup_block
	assert "setup_failed_weapon:" in setup_block
	assert "setup_failed_goal:" in setup_block
	assert "setup_failed_character:" in setup_block
	assert "if (bs->cs) trap_BotFreeChatState(bs->cs);" in setup_block
	assert "if (bs->ws) trap_BotFreeWeaponState(bs->ws);" in setup_block
	assert "if (bs->gs) trap_BotFreeGoalState(bs->gs);" in setup_block
	assert "if (bs->character) trap_BotFreeCharacter(bs->character);" in setup_block
	assert setup_block.index("setup_failed_character:") < setup_block.rindex("memset(bs, 0, sizeof(bot_state_t));")

	assert "sub_10059e70(0x2698)" in qagame_type85
	assert "10022c26  sub_1001cbb0(esi)" in qagame_type85
	assert "10022c33  memset(esi, 0, 0x2698)" in qagame_type85
	assert "piVar1[0x656] = iVar4;" in qagame_ghidra
	assert "piVar1[0x658] = iVar5;" in qagame_ghidra
	assert "piVar1[0x65a] = iVar4;" in qagame_ghidra
	assert "piVar1[0x659] = iVar5;" in qagame_ghidra

	for expected in (
		"1001c946  void* esi = *(arg1 + 0x1bd4)",
		"1001c95c  if (*(esi + 0xf4) != 0)",
		"1001c967      if (*(esi + 0xf0) s> 0)",
		"1001c96a          void* ebx_1 = esi + 0x70",
		"1001c9c9  *(arg1 + 0x1bd4) = *(*(arg1 + 0x1bd4) + 0xf8)",
		"1001cb6d  void* ebx = ecx * 0xfc + arg2",
		"1001cb83  __builtin_memcpy(dest: ebx + 0x1bd8, src: arg3, n: 0xfc)",
		"1001cb92  *(ebx + 0x1cd0) = *(arg2 + 0x1bd4)",
		"1001cb99  *(arg2 + 0x1bd4) = ebx + 0x1bd8",
		"1001cbbc  while (*(arg1 + 0x1bd4) != 0)",
	):
		assert expected in qagame_type78

	assert "1001cc60    int32_t sub_1001cc60(int32_t arg1)" in qagame_hlil
	assert "if (*(ebx + 0xf4) != result)" in qagame_hlil
	assert "if (*(ebx + 0xf0) s> 0)" in qagame_hlil
	assert "void* edi_1 = ebx + 0x70" in qagame_hlil
	assert "*(ebx + 0xf4) = result" in qagame_hlil


@pytest.fixture(scope="session")
def botlib_internal_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("botlib_internal_harness_build")
	lib_path = build_dir / shared_library_name("botlib_internal_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the botlib internal harness")

	libraries = [] if compiler.is_msvc or lib_path.suffix == ".dll" else ["m"]

	compile_c_binary(
		compiler,
		[ BOTLIB_INTERNAL_HARNESS ],
		lib_path,
		libraries=libraries,
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_BotlibResetState.argtypes = []
	lib.QLR_BotlibResetState.restype = None
	lib.QLR_BotlibSetTime.argtypes = [ctypes.c_float]
	lib.QLR_BotlibSetTime.restype = None
	lib.QLR_BotlibSetReachabilitySettings.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
	lib.QLR_BotlibSetReachabilitySettings.restype = None
	lib.QLR_BotlibSetTravelFlagsForTeamValue.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibSetTravelFlagsForTeamValue.restype = None
	lib.QLR_BotlibPresenceTypeBoundingBoxFromArrays.argtypes = [
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_BotlibPresenceTypeBoundingBoxFromArrays.restype = None
	lib.QLR_BotlibProjectPointOntoVector.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_BotlibProjectPointOntoVector.restype = None
	lib.QLR_BotlibFallDamageDistance.argtypes = []
	lib.QLR_BotlibFallDamageDistance.restype = ctypes.c_int
	lib.QLR_BotlibFallDelta.argtypes = [ctypes.c_float]
	lib.QLR_BotlibFallDelta.restype = ctypes.c_float
	lib.QLR_BotlibMaxJumpHeight.argtypes = [ctypes.c_float]
	lib.QLR_BotlibMaxJumpHeight.restype = ctypes.c_float
	lib.QLR_BotlibMaxJumpDistance.argtypes = [ctypes.c_float]
	lib.QLR_BotlibMaxJumpDistance.restype = ctypes.c_float
	lib.QLR_BotlibTravelFlagsForTeam.argtypes = [ctypes.c_int]
	lib.QLR_BotlibTravelFlagsForTeam.restype = ctypes.c_int
	lib.QLR_BotlibAllocMoveState.argtypes = []
	lib.QLR_BotlibAllocMoveState.restype = ctypes.c_int
	lib.QLR_BotlibFreeMoveState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibFreeMoveState.restype = None
	lib.QLR_BotlibMoveStateExists.argtypes = [ctypes.c_int]
	lib.QLR_BotlibMoveStateExists.restype = ctypes.c_int
	lib.QLR_BotlibInitMoveState.argtypes = [ctypes.c_int, ctypes.POINTER(BotInitMove)]
	lib.QLR_BotlibInitMoveState.restype = None
	lib.QLR_BotlibSetMoveFlags.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibSetMoveFlags.restype = None
	lib.QLR_BotlibMoveFlags.argtypes = [ctypes.c_int]
	lib.QLR_BotlibMoveFlags.restype = ctypes.c_int
	lib.QLR_BotlibSeedAvoidReach.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_int]
	lib.QLR_BotlibSeedAvoidReach.restype = None
	lib.QLR_BotlibSetAvoidReachGateWord.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibSetAvoidReachGateWord.restype = None
	lib.QLR_BotlibAvoidReach.argtypes = [ctypes.c_int]
	lib.QLR_BotlibAvoidReach.restype = ctypes.c_int
	lib.QLR_BotlibAvoidReachTime.argtypes = [ctypes.c_int]
	lib.QLR_BotlibAvoidReachTime.restype = ctypes.c_float
	lib.QLR_BotlibAvoidReachTries.argtypes = [ctypes.c_int]
	lib.QLR_BotlibAvoidReachTries.restype = ctypes.c_int
	lib.QLR_BotlibResetAvoidReach.argtypes = [ctypes.c_int]
	lib.QLR_BotlibResetAvoidReach.restype = None
	lib.QLR_BotlibResetLastAvoidReach.argtypes = [ctypes.c_int]
	lib.QLR_BotlibResetLastAvoidReach.restype = None
	lib.QLR_BotlibResetMoveState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibResetMoveState.restype = None
	lib.QLR_BotlibAllocGoalState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibAllocGoalState.restype = ctypes.c_int
	lib.QLR_BotlibFreeGoalState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibFreeGoalState.restype = None
	lib.QLR_BotlibResetGoalState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibResetGoalState.restype = None
	lib.QLR_BotlibPushGoal.argtypes = [ctypes.c_int, ctypes.POINTER(BotGoal)]
	lib.QLR_BotlibPushGoal.restype = None
	lib.QLR_BotlibPopGoal.argtypes = [ctypes.c_int]
	lib.QLR_BotlibPopGoal.restype = None
	lib.QLR_BotlibEmptyGoalStack.argtypes = [ctypes.c_int]
	lib.QLR_BotlibEmptyGoalStack.restype = None
	lib.QLR_BotlibGetTopGoal.argtypes = [ctypes.c_int, ctypes.POINTER(BotGoal)]
	lib.QLR_BotlibGetTopGoal.restype = ctypes.c_int
	lib.QLR_BotlibGetSecondGoal.argtypes = [ctypes.c_int, ctypes.POINTER(BotGoal)]
	lib.QLR_BotlibGetSecondGoal.restype = ctypes.c_int
	lib.QLR_BotlibSetAvoidGoalTime.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float]
	lib.QLR_BotlibSetAvoidGoalTime.restype = None
	lib.QLR_BotlibAvoidGoalTime.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibAvoidGoalTime.restype = ctypes.c_float
	lib.QLR_BotlibRemoveFromAvoidGoals.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibRemoveFromAvoidGoals.restype = None
	lib.QLR_BotlibLastPrintType.argtypes = []
	lib.QLR_BotlibLastPrintType.restype = ctypes.c_int
	lib.QLR_BotlibLastPrintMessage.argtypes = []
	lib.QLR_BotlibLastPrintMessage.restype = ctypes.c_char_p
	lib.QLR_BotlibResetState()
	return lib


def test_botlib_presence_type_bounding_box_matches_retail_boxes(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	botlib_internal_harness.QLR_BotlibResetState()
	mins = _vec3(0.0, 0.0, 0.0)
	maxs = _vec3(0.0, 0.0, 0.0)

	botlib_internal_harness.QLR_BotlibPresenceTypeBoundingBoxFromArrays(
		PRESENCE_NORMAL,
		mins,
		maxs,
	)
	assert tuple(mins) == pytest.approx((-15.0, -15.0, -24.0))
	assert tuple(maxs) == pytest.approx((15.0, 15.0, 32.0))

	botlib_internal_harness.QLR_BotlibPresenceTypeBoundingBoxFromArrays(
		PRESENCE_CROUCH,
		mins,
		maxs,
	)
	assert tuple(mins) == pytest.approx((-15.0, -15.0, -24.0))
	assert tuple(maxs) == pytest.approx((15.0, 15.0, 8.0))


def test_botlib_project_point_onto_vector_projects_orthogonally(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	botlib_internal_harness.QLR_BotlibResetState()
	projected = _vec3(0.0, 0.0, 0.0)

	botlib_internal_harness.QLR_BotlibProjectPointOntoVector(
		_vec3(5.0, 5.0, 0.0),
		_vec3(0.0, 0.0, 0.0),
		_vec3(10.0, 0.0, 0.0),
		projected,
	)

	assert tuple(projected) == pytest.approx((5.0, 0.0, 0.0))


def test_botlib_reachability_formula_helpers_match_expected_q3_physics(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	gravity = 800.0
	maxvelocity = 320.0
	maxjumpfallheight = 64.0
	jumpvel = 270.0

	botlib_internal_harness.QLR_BotlibResetState()
	botlib_internal_harness.QLR_BotlibSetReachabilitySettings(gravity, maxvelocity, maxjumpfallheight)

	expected_fall_distance = int(0.5 * gravity * ((math.sqrt(30 * 10000) / gravity) ** 2))
	expected_fall_delta = ((math.sqrt(abs(128.0) * 2 / gravity) * gravity) ** 2) * 0.0001
	expected_jump_height = 0.5 * gravity * ((jumpvel / gravity) ** 2)
	expected_jump_distance = maxvelocity * (math.sqrt(maxjumpfallheight / (0.5 * gravity)) + jumpvel / gravity)

	assert botlib_internal_harness.QLR_BotlibFallDamageDistance() == expected_fall_distance
	assert botlib_internal_harness.QLR_BotlibFallDelta(128.0) == pytest.approx(expected_fall_delta, rel=1e-6)
	assert botlib_internal_harness.QLR_BotlibMaxJumpHeight(jumpvel) == pytest.approx(expected_jump_height, rel=1e-6)
	assert botlib_internal_harness.QLR_BotlibMaxJumpDistance(jumpvel) == pytest.approx(expected_jump_distance, rel=1e-6)


def test_botlib_travel_flags_for_team_use_notteam_epair_convention(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	botlib_internal_harness.QLR_BotlibResetState()
	botlib_internal_harness.QLR_BotlibSetTravelFlagsForTeamValue(0, 0)
	assert botlib_internal_harness.QLR_BotlibTravelFlagsForTeam(7) == 0

	botlib_internal_harness.QLR_BotlibSetTravelFlagsForTeamValue(1, 1)
	assert botlib_internal_harness.QLR_BotlibTravelFlagsForTeam(7) == TRAVELFLAG_NOTTEAM1

	botlib_internal_harness.QLR_BotlibSetTravelFlagsForTeamValue(1, 2)
	assert botlib_internal_harness.QLR_BotlibTravelFlagsForTeam(7) == TRAVELFLAG_NOTTEAM2


def test_botlib_move_state_reset_lifecycle_preserves_retail_avoidreach_gate(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	botlib_internal_harness.QLR_BotlibResetState()
	handle = botlib_internal_harness.QLR_BotlibAllocMoveState()
	assert handle > 0
	assert botlib_internal_harness.QLR_BotlibMoveStateExists(handle) == 1

	initmove = BotInitMove()
	initmove.origin[:] = (10.0, 20.0, 30.0)
	initmove.velocity[:] = (1.0, 2.0, 3.0)
	initmove.viewoffset[:] = (0.0, 0.0, 24.0)
	initmove.entitynum = 9
	initmove.client = 4
	initmove.thinktime = 0.05
	initmove.presencetype = PRESENCE_NORMAL
	initmove.viewangles[:] = (45.0, 90.0, 0.0)
	initmove.or_moveflags = MFL_WATERJUMP | MFL_WALK

	botlib_internal_harness.QLR_BotlibSetMoveFlags(
		handle,
		MFL_SWIMMING | MFL_ONGROUND | MFL_TELEPORTED | MFL_GRAPPLEPULL,
	)
	botlib_internal_harness.QLR_BotlibInitMoveState(handle, ctypes.byref(initmove))
	assert botlib_internal_harness.QLR_BotlibMoveFlags(handle) == (
		MFL_SWIMMING | MFL_WATERJUMP | MFL_WALK
	)

	botlib_internal_harness.QLR_BotlibSeedAvoidReach(handle, 77, 8.0, 4)
	botlib_internal_harness.QLR_BotlibSetAvoidReachGateWord(handle, 0)
	botlib_internal_harness.QLR_BotlibResetLastAvoidReach(handle)
	assert botlib_internal_harness.QLR_BotlibAvoidReachTime(handle) == pytest.approx(0.0)
	assert botlib_internal_harness.QLR_BotlibAvoidReachTries(handle) == 4

	botlib_internal_harness.QLR_BotlibSeedAvoidReach(handle, 88, 9.0, 4)
	botlib_internal_harness.QLR_BotlibSetAvoidReachGateWord(handle, 1)
	botlib_internal_harness.QLR_BotlibResetLastAvoidReach(handle)
	assert botlib_internal_harness.QLR_BotlibAvoidReachTime(handle) == pytest.approx(0.0)
	assert botlib_internal_harness.QLR_BotlibAvoidReachTries(handle) == 3

	botlib_internal_harness.QLR_BotlibSeedAvoidReach(handle, 99, 5.0, 2)
	botlib_internal_harness.QLR_BotlibResetAvoidReach(handle)
	assert botlib_internal_harness.QLR_BotlibAvoidReach(handle) == 0
	assert botlib_internal_harness.QLR_BotlibAvoidReachTime(handle) == pytest.approx(0.0)
	assert botlib_internal_harness.QLR_BotlibAvoidReachTries(handle) == 0

	botlib_internal_harness.QLR_BotlibSetMoveFlags(handle, MFL_WALK)
	botlib_internal_harness.QLR_BotlibSeedAvoidReach(handle, 101, 7.0, 1)
	botlib_internal_harness.QLR_BotlibResetMoveState(handle)
	assert botlib_internal_harness.QLR_BotlibMoveFlags(handle) == 0
	assert botlib_internal_harness.QLR_BotlibAvoidReach(handle) == 0
	assert botlib_internal_harness.QLR_BotlibAvoidReachTime(handle) == pytest.approx(0.0)
	assert botlib_internal_harness.QLR_BotlibAvoidReachTries(handle) == 0

	botlib_internal_harness.QLR_BotlibFreeMoveState(handle)
	assert botlib_internal_harness.QLR_BotlibMoveStateExists(handle) == 0


def test_botlib_goal_state_stack_and_avoid_timer_lifecycle(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	top = BotGoal()
	second = BotGoal()

	botlib_internal_harness.QLR_BotlibResetState()
	handle = botlib_internal_harness.QLR_BotlibAllocGoalState(3)
	assert handle > 0

	first_goal = _goal(11, (100.0, 200.0, 300.0))
	second_goal = _goal(22, (-10.0, 40.0, 90.0))

	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0
	assert botlib_internal_harness.QLR_BotlibGetSecondGoal(handle, ctypes.byref(second)) == 0

	botlib_internal_harness.QLR_BotlibPushGoal(handle, ctypes.byref(first_goal))
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 1
	assert top.number == 11
	assert tuple(top.origin) == pytest.approx((100.0, 200.0, 300.0))
	assert botlib_internal_harness.QLR_BotlibGetSecondGoal(handle, ctypes.byref(second)) == 0

	botlib_internal_harness.QLR_BotlibPushGoal(handle, ctypes.byref(second_goal))
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 1
	assert top.number == 22
	assert botlib_internal_harness.QLR_BotlibGetSecondGoal(handle, ctypes.byref(second)) == 1
	assert second.number == 11

	botlib_internal_harness.QLR_BotlibSetTime(10.0)
	botlib_internal_harness.QLR_BotlibSetAvoidGoalTime(handle, 77, 3.5)
	assert botlib_internal_harness.QLR_BotlibAvoidGoalTime(handle, 77) == pytest.approx(3.5, rel=1e-6)

	botlib_internal_harness.QLR_BotlibSetTime(11.25)
	assert botlib_internal_harness.QLR_BotlibAvoidGoalTime(handle, 77) == pytest.approx(2.25, rel=1e-6)

	botlib_internal_harness.QLR_BotlibRemoveFromAvoidGoals(handle, 77)
	assert botlib_internal_harness.QLR_BotlibAvoidGoalTime(handle, 77) == pytest.approx(0.0)

	botlib_internal_harness.QLR_BotlibPopGoal(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 1
	assert top.number == 11

	botlib_internal_harness.QLR_BotlibEmptyGoalStack(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0

	botlib_internal_harness.QLR_BotlibPushGoal(handle, ctypes.byref(first_goal))
	botlib_internal_harness.QLR_BotlibResetGoalState(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0

	botlib_internal_harness.QLR_BotlibFreeGoalState(handle)


def test_botlib_goal_state_invalid_handle_messages_match_retail_strings(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	top = BotGoal()

	botlib_internal_harness.QLR_BotlibResetState()
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(0, ctypes.byref(top)) == 0
	assert botlib_internal_harness.QLR_BotlibLastPrintType() == PRT_FATAL
	assert botlib_internal_harness.QLR_BotlibLastPrintMessage().decode("utf-8") == "goal state handle 0 out of range\n"

	handle = botlib_internal_harness.QLR_BotlibAllocGoalState(9)
	assert handle > 0
	botlib_internal_harness.QLR_BotlibFreeGoalState(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0
	assert botlib_internal_harness.QLR_BotlibLastPrintType() == PRT_FATAL
	assert botlib_internal_harness.QLR_BotlibLastPrintMessage().decode("utf-8") == f"invalid goal state {handle}\n"

	botlib_internal_harness.QLR_BotlibFreeGoalState(handle)
	assert botlib_internal_harness.QLR_BotlibLastPrintMessage().decode("utf-8") == f"invalid goal state handle {handle}\n"


def test_botlib_source_keeps_presence_bbox_and_jump_formula_helpers() -> None:
	aas_sample = BOTLIB_AAS_SAMPLE.read_text(encoding="utf-8")
	aas_main = BOTLIB_AAS_MAIN.read_text(encoding="utf-8")
	aas_reach = BOTLIB_AAS_REACH.read_text(encoding="utf-8")

	presence_block = _extract_function_block(
		aas_sample,
		"void AAS_PresenceTypeBoundingBox(int presencetype, vec3_t mins, vec3_t maxs)",
	)
	project_block = _extract_function_block(
		aas_main,
		"void AAS_ProjectPointOntoVector( vec3_t point, vec3_t vStart, vec3_t vEnd, vec3_t vProj )",
	)
	fall_distance_block = _extract_function_block(aas_reach, "int AAS_FallDamageDistance(void)")
	fall_delta_block = _extract_function_block(aas_reach, "float AAS_FallDelta(float distance)")
	max_jump_height_block = _extract_function_block(aas_reach, "float AAS_MaxJumpHeight(float phys_jumpvel)")
	max_jump_distance_block = _extract_function_block(aas_reach, "float AAS_MaxJumpDistance(float phys_jumpvel)")
	travel_flags_block = _extract_function_block(aas_reach, "int AAS_TravelFlagsForTeam(int ent)")

	assert "vec3_t boxmins[3] = {{0, 0, 0}, {-15, -15, -24}, {-15, -15, -24}};" in presence_block
	assert 'botimport.Print(PRT_FATAL, "AAS_PresenceTypeBoundingBox: unknown presence type\\n");' in presence_block
	assert "VectorNormalize( vec );" in project_block
	assert "VectorMA( vStart, DotProduct( pVec, vec ), vec, vProj );" in project_block
	assert "maxzvelocity = sqrt(30 * 10000);" in fall_distance_block
	assert "return 0.5 * gravity * t * t;" in fall_distance_block
	assert "t = sqrt(fabs(distance) * 2 / gravity);" in fall_delta_block
	assert "return delta * delta * 0.0001;" in fall_delta_block
	assert "return 0.5 * phys_gravity * (phys_jumpvel / phys_gravity) * (phys_jumpvel / phys_gravity);" in max_jump_height_block
	assert "t = sqrt(aassettings.rs_maxjumpfallheight / (0.5 * phys_gravity));" in max_jump_distance_block
	assert "return phys_maxvelocity * (t + phys_jumpvel / phys_gravity);" in max_jump_distance_block
	assert 'if (!AAS_IntForBSPEpairKey(ent, "bot_notteam", &notteam))' in travel_flags_block
	assert "return TRAVELFLAG_NOTTEAM1;" in travel_flags_block
	assert "return TRAVELFLAG_NOTTEAM2;" in travel_flags_block


def test_botlib_ql_entity_state_tail_matches_retail_layout_references() -> None:
	botlib_h = BOTLIB_H.read_text(encoding="utf-8")
	be_aas_h = BOTLIB_BE_AAS_H.read_text(encoding="utf-8")
	aas_entity_source = BOTLIB_AAS_ENTITY.read_text(encoding="utf-8")
	ai_main_source = GAME_AI_MAIN.read_text(encoding="utf-8")
	qagame_ghidra = QAGAME_GHIDRA_TOP.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART01.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")

	assert "#define BOTLIB_QL_POWERUP_ACTIVE_COUNT\t16" in botlib_h
	assert "#define BOTLIB_QL_POWERUP_ACTIVE_COUNT\t16" in be_aas_h
	assert "float\tqlTimeSeconds;" in botlib_h
	assert "int\t\tqlPlayerGravity;" in botlib_h
	assert "int\t\tqlPlayerSpeed;" in botlib_h
	assert "int\t\tqlPlayerDeltaAngle0;" in botlib_h
	assert "int\t\tqlEntityHealth;" in botlib_h
	assert "int\t\tqlClientMaxHealth;" in botlib_h
	assert "int\t\tqlPowerupsActive[BOTLIB_QL_POWERUP_ACTIVE_COUNT];" in botlib_h
	assert "int\t\tqlFlagsBit18Clear;" in botlib_h
	assert "int\t\tqlRedBlueFlagCarrier;" in botlib_h
	assert "float\tqlTimeSeconds;" in be_aas_h
	assert "int\t\tqlEntityHealth;" in be_aas_h
	assert "int\t\tqlClientMaxHealth;" in be_aas_h
	assert "int\t\tqlPowerupsActive[BOTLIB_QL_POWERUP_ACTIVE_COUNT];" in be_aas_h
	assert "int\t\tqlFlagsBit18Clear;" in be_aas_h
	assert "int\t\tqlRedBlueFlagCarrier;" in be_aas_h
	assert "qlRetailExtra" not in botlib_h
	assert "qlRetailExtra" not in be_aas_h
	assert "ent->i.qlEntityHealth = state->qlEntityHealth;" in aas_entity_source
	assert "ent->i.qlClientMaxHealth = state->qlClientMaxHealth;" in aas_entity_source
	assert "Com_Memcpy(ent->i.qlPowerupsActive, state->qlPowerupsActive, sizeof(ent->i.qlPowerupsActive));" in aas_entity_source
	assert "ent->i.qlFlagsBit18Clear = state->qlFlagsBit18Clear;" in aas_entity_source
	assert "ent->i.qlRedBlueFlagCarrier = state->qlRedBlueFlagCarrier;" in aas_entity_source
	assert "#define RETAIL_BOTLIB_GENTITY_FLAG_BIT18\t0x00040000" in ai_main_source
	assert "state.qlTimeSeconds = (float)( ent->s.time / 1000 );" in ai_main_source
	assert "state.qlPlayerGravity = ent->client->ps.gravity;" in ai_main_source
	assert "state.qlPlayerSpeed = ent->client->ps.speed;" in ai_main_source
	assert "state.qlPlayerDeltaAngle0 = ent->client->ps.delta_angles[0];" in ai_main_source
	assert "state.qlEntityHealth = ent->health;" in ai_main_source
	assert "state.qlClientMaxHealth = ent->client->ps.stats[STAT_MAX_HEALTH];" in ai_main_source
	assert "state.qlRedBlueFlagCarrier = ( ent->client->ps.powerups[PW_REDFLAG]" in ai_main_source
	assert "powerupTime = ent->client->ps.powerups[powerup];" in ai_main_source
	assert "powerupTime >= level.time || powerupTime == INT_MAX" in ai_main_source

	assert "memset(&iStack_e0,0,0xd0);" in qagame_ghidra
	assert "fStack_70 = (float)(piVar4[0x47] / 1000);" in qagame_ghidra
	assert "uStack_6c = *(undefined4 *)(iVar3 + 0x30);" in qagame_ghidra
	assert "iStack_60 = piVar4[0x52];" in qagame_ghidra
	assert "uStack_5c = *(undefined4 *)(iVar3 + 0xdc);" in qagame_ghidra
	assert "if ((*(int *)(iVar3 + 0x144) != 0) || (uStack_14 = 0, *(int *)(iVar3 + 0x148) != 0))" in qagame_ghidra
	assert "piVar5 = (int *)(iVar3 + 0x180);" in qagame_ghidra
	assert "memset(auStack_58,0,0x40);" in qagame_ghidra
	assert "*(esp_14 + 0x88) = float.s" in qagame_hlil
	assert "*(esp_14 + 0x98) = *(i + 0x148)" in qagame_hlil
	assert "*(esp_14 + 0x9c) = *(edx_30 + 0xdc)" in qagame_hlil
	assert "if (*(edx_30 + 0x144) == 0)" in qagame_hlil
	assert "void* esi_4 = edx_30 + 0x180" in qagame_hlil
	assert "if (edx_31 s>= *j || edx_31 == 0xffffffff)" in qagame_hlil
	assert "00484e6b  int32_t* ebx_2 = arg1 * 0xf4 + data_16de9a8" in ql_steam_hlil
	assert "004851dd      return sub_4c95e0(arg2, 0, 0xec)" in ql_steam_hlil
	assert "__builtin_memcpy(dest: &ebx_2[0x29], src: &arg2[0x22], n: 0x40)" in ql_steam_hlil
	assert "return sub_4cb7d0(arg2, arg1 * 0xf4 + data_16de9a8, 0xec)" in ql_steam_hlil


def test_botlib_show_path_cache_and_move_debug_path_match_retail_references() -> None:
	be_interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	be_interface_h = BOTLIB_INTERFACE_H.read_text(encoding="utf-8")
	aas_main = BOTLIB_AAS_MAIN.read_text(encoding="utf-8")
	ai_move = BOTLIB_AI_MOVE.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	move_to_goal_block = _extract_function_block(
		ai_move,
		"void BotMoveToGoal(bot_moveresult_t *result, int movestate, bot_goal_t *goal, int travelflags)",
	)
	blocked_index = move_to_goal_block.find("if (result->blocked)")
	show_path_index = move_to_goal_block.find("if (bot_showPath)")
	last_origin_index = move_to_goal_block.find("VectorCopy(ms->origin, ms->lastorigin);")
	show_path_block = move_to_goal_block[show_path_index:last_origin_index]

	assert "int bot_showPath;" in be_interface
	assert "extern int bot_showPath;" in be_interface_h
	assert 'bot_showPath = LibVarGetValue("bot_showPath");' in be_interface
	assert 'bot_showPath = LibVarGetValue("bot_showPath");' in aas_main
	assert "AAS_ReachabilityFromNum(ms->lastreachnum, &reach);" in move_to_goal_block
	assert "AAS_DebugLine(ms->origin, ms->lastorigin, LINECOLOR_YELLOW);" in move_to_goal_block
	assert "AAS_DrawArrow(reach.start, reach.end, LINECOLOR_BLUE, LINECOLOR_YELLOW);" in show_path_block
	assert "AAS_ShowReachability(&reach);" not in show_path_block
	assert blocked_index != -1
	assert show_path_index != -1
	assert last_origin_index != -1
	assert blocked_index < show_path_index < last_origin_index
	assert aliases["sub_4844E0"] == "AAS_DebugLine"
	assert aliases["sub_484A80"] == "AAS_DrawArrow"

	assert 'data_16dd7ec = sub_526000(sub_4a8680("bot_showPath"))' in ql_steam_hlil
	assert '004863bb  data_16dd7ec = sub_526000(sub_4a8680("bot_showPath"))' in ql_steam_hlil
	assert '004a7d03  data_16dd7ec = sub_526000(sub_4a8680("bot_showPath"))' in ql_steam_hlil
	assert "004a573e  if (data_16dd7ec != 0)" in ql_steam_hlil
	assert "004a5757      sub_4844e0()" in ql_steam_hlil
	assert "004a576e      eax_40 = sub_484a80()" in ql_steam_hlil


def test_botlib_move_state_lifecycle_and_avoidreach_reset_match_retail_references() -> None:
	botlib_h = BOTLIB_H.read_text(encoding="utf-8")
	ai_move_h = (REPO_ROOT / "src" / "code" / "game" / "be_ai_move.h").read_text(encoding="utf-8")
	ai_move = BOTLIB_AI_MOVE.read_text(encoding="utf-8")
	be_interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	move_state_struct = _extract_function_block(ai_move, "typedef struct bot_movestate_s")
	alloc_move_state = _extract_function_block(ai_move, "int BotAllocMoveState(void)")
	free_move_state = _extract_function_block(ai_move, "void BotFreeMoveState(int handle)")
	move_state_from_handle = _extract_function_block(ai_move, "bot_movestate_t *BotMoveStateFromHandle(int handle)")
	init_move_state = _extract_function_block(ai_move, "void BotInitMoveState(int handle, bot_initmove_t *initmove)")
	reset_avoid_reach = _extract_function_block(ai_move, "void BotResetAvoidReach(int movestate)")
	reset_last_avoid_reach = _extract_function_block(ai_move, "void BotResetLastAvoidReach(int movestate)")
	reset_move_state = _extract_function_block(ai_move, "void BotResetMoveState(int movestate)")
	ai_export = _extract_function_block(botlib_h, "typedef struct ai_export_s")
	init_ai = _extract_function_block(be_interface, "static void Init_AI_Export( ai_export_t *ai )")

	assert "#define MAX_AVOIDREACH\t\t\t\t\t1" in ai_move_h
	assert "int avoidreach[MAX_AVOIDREACH];" in move_state_struct
	assert "float avoidreachtimes[MAX_AVOIDREACH];" in move_state_struct
	assert "int avoidreachtries[MAX_AVOIDREACH];" in move_state_struct
	assert "bot_avoidspot_t avoidspots[MAX_AVOIDSPOTS];" in move_state_struct
	assert move_state_struct.index("avoidreach[MAX_AVOIDREACH]") < move_state_struct.index("avoidreachtimes[MAX_AVOIDREACH]")
	assert move_state_struct.index("avoidreachtimes[MAX_AVOIDREACH]") < move_state_struct.index("avoidreachtries[MAX_AVOIDREACH]")
	assert move_state_struct.index("avoidreachtries[MAX_AVOIDREACH]") < move_state_struct.index("avoidspots[MAX_AVOIDSPOTS]")

	assert "botmovestates[i] = GetClearedMemory(sizeof(bot_movestate_t));" in alloc_move_state
	assert 'botimport.Print(PRT_FATAL, "move state handle %d out of range\\n", handle);' in free_move_state
	assert 'botimport.Print(PRT_FATAL, "invalid move state %d\\n", handle);' in move_state_from_handle
	assert "VectorCopy(initmove->origin, ms->origin);" in init_move_state
	assert "ms->moveflags &= ~MFL_ONGROUND;" in init_move_state
	assert "ms->moveflags &= ~MFL_TELEPORTED;" in init_move_state
	assert "ms->moveflags &= ~MFL_WATERJUMP;" in init_move_state
	assert "ms->moveflags &= ~MFL_WALK;" in init_move_state
	assert "ms->moveflags &= ~MFL_GRAPPLEPULL;" in init_move_state
	assert "Com_Memset(ms->avoidreach, 0, MAX_AVOIDREACH * sizeof(int));" in reset_avoid_reach
	assert "Com_Memset(ms->avoidreachtimes, 0, MAX_AVOIDREACH * sizeof(float));" in reset_avoid_reach
	assert "Com_Memset(ms->avoidreachtries, 0, MAX_AVOIDREACH * sizeof(int));" in reset_avoid_reach
	assert "for (i = 0; i < MAX_AVOIDREACH; i++)" in reset_last_avoid_reach
	assert "ms->avoidreachtimes[latest] = 0;" in reset_last_avoid_reach
	assert "if (ms->avoidreachtries[i] > 0) ms->avoidreachtries[latest]--;" in reset_last_avoid_reach
	assert "Com_Memset(ms, 0, sizeof(bot_movestate_t));" in reset_move_state

	assert ai_export.index("(*BotResetMoveState)") < ai_export.index("(*BotMoveToGoal)")
	assert ai_export.index("(*BotResetAvoidReach)") < ai_export.index("(*BotResetLastAvoidReach)")
	assert ai_export.index("(*BotAllocMoveState)") < ai_export.index("(*BotFreeMoveState)")
	assert ai_export.index("(*BotFreeMoveState)") < ai_export.index("(*BotInitMoveState)")
	assert init_ai.index("ai->BotResetMoveState = BotResetMoveState;") < init_ai.index(
		"ai->BotMoveToGoal = BotMoveToGoal;"
	)
	assert init_ai.index("ai->BotResetAvoidReach = BotResetAvoidReach;") < init_ai.index(
		"ai->BotResetLastAvoidReach = BotResetLastAvoidReach;"
	)
	assert init_ai.index("ai->BotAllocMoveState = BotAllocMoveState;") < init_ai.index(
		"ai->BotFreeMoveState = BotFreeMoveState;"
	)
	assert init_ai.index("ai->BotFreeMoveState = BotFreeMoveState;") < init_ai.index(
		"ai->BotInitMoveState = BotInitMoveState;"
	)
	assert ai_export.index("(*BotResetLastAvoidReach)") < ai_export.index("(*BotReachabilityArea)")
	assert ai_export.index("(*BotReachabilityArea)") < ai_export.index("(*BotMovementViewTarget)")
	assert ai_export.index("(*BotMovementViewTarget)") < ai_export.index("(*BotPredictVisiblePosition)")
	assert init_ai.index("ai->BotResetLastAvoidReach = BotResetLastAvoidReach;") < init_ai.index(
		"ai->BotReachabilityArea = BotReachabilityArea;"
	)
	assert init_ai.index("ai->BotReachabilityArea = BotReachabilityArea;") < init_ai.index(
		"ai->BotMovementViewTarget = BotMovementViewTarget;"
	)
	assert init_ai.index("ai->BotMovementViewTarget = BotMovementViewTarget;") < init_ai.index(
		"ai->BotPredictVisiblePosition = BotPredictVisiblePosition;"
	)

	for address, name in (
		("49F9C0", "BotAllocMoveState"),
		("49FA00", "BotFreeMoveState"),
		("49FA60", "BotMoveStateFromHandle"),
		("49FAB0", "BotInitMoveState"),
		("49FC30", "BotFuzzyPointReachabilityArea"),
		("49FED0", "BotReachabilityArea"),
		("4A0F70", "BotPredictVisiblePosition"),
		("4A17F0", "BotMoveInDirection"),
		("4A5830", "BotResetAvoidReach"),
		("4A58A0", "BotResetLastAvoidReach"),
		("4A5920", "BotResetMoveState"),
	):
		assert aliases[f"sub_{address}"] == name

	assert "0049f9c0    int32_t sub_49f9c0()" in ql_steam_hlil
	assert "*((i << 2) + &data_16de100) = sub_4a89d0(0x304)" in ql_steam_hlil
	assert "0049fa00    int32_t* sub_49fa00(int32_t arg1)" in ql_steam_hlil
	assert 'data_16dd800(4, "move state handle %d out of rang' in ql_steam_hlil
	assert 'data_16dd800(4, "invalid move state %d\\n", arg1)' in ql_steam_hlil
	assert "0049fa60    int32_t sub_49fa60(int32_t arg1)" in ql_steam_hlil
	assert "0049fab0    float* sub_49fab0(int32_t arg1, float* arg2)" in ql_steam_hlil
	assert "004a5830    int32_t sub_4a5830(int32_t arg1)" in ql_steam_hlil
	assert "sub_4c95e0(esi + 0x74, 0, 4)" in ql_steam_hlil
	assert "sub_4c95e0(esi + 0x78, 0, 4)" in ql_steam_hlil
	assert "sub_4c95e0(esi + 0x7c, 0, 4)" in ql_steam_hlil
	assert "004a58a0    void sub_4a58a0(float arg1)" in ql_steam_hlil
	assert "if (*(ecx_1 + 0x80) s> 0)" in ql_steam_hlil
	assert "*(ecx_1 + 0x7c) -= 1" in ql_steam_hlil
	assert "004a5920    int32_t sub_4a5920(int32_t arg1)" in ql_steam_hlil
	assert "return sub_4c95e0(eax_1, 0, 0x304)" in ql_steam_hlil
	assert "arg1[0x38] = sub_4a5920" in ql_steam_hlil
	assert "004a82e9  arg1[0x39] = sub_4a4a50" in ql_steam_hlil
	assert "004a82f3  arg1[0x3a] = sub_4a17f0" in ql_steam_hlil
	assert "arg1[0x3b] = sub_4a5830" in ql_steam_hlil
	assert "arg1[0x3c] = sub_4a58a0" in ql_steam_hlil
	assert "004a8311  arg1[0x3d] = sub_49fed0" in ql_steam_hlil
	assert "004a831b  arg1[0x3e] = sub_4a0cd0" in ql_steam_hlil
	assert "004a8325  arg1[0x3f] = sub_4a0f70" in ql_steam_hlil
	assert "arg1[0x40] = sub_49f9c0" in ql_steam_hlil
	assert "arg1[0x41] = sub_49fa00" in ql_steam_hlil
	assert "arg1[0x42] = sub_49fab0" in ql_steam_hlil


def test_botlib_export_table_retail_layout_includes_ea_walk_slot() -> None:
	botlib_h = BOTLIB_H.read_text(encoding="utf-8")
	be_interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	ai_move = BOTLIB_AI_MOVE.read_text(encoding="utf-8")
	be_ea = BOTLIB_EA.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	aas_export = _extract_function_block(botlib_h, "typedef struct aas_export_s")
	ea_export = _extract_function_block(botlib_h, "typedef struct ea_export_s")
	ai_export = _extract_function_block(botlib_h, "typedef struct ai_export_s")
	botlib_export = _extract_function_block(botlib_h, "typedef struct botlib_export_s")
	init_aas = _extract_function_block(be_interface, "static void Init_AAS_Export( aas_export_t *aas )")
	init_ea = _extract_function_block(be_interface, "static void Init_EA_Export( ea_export_t *ea )")
	init_ai = _extract_function_block(be_interface, "static void Init_AI_Export( ai_export_t *ai )")
	get_api = _extract_function_block(be_interface, "botlib_export_t *GetBotLibAPI(int apiVersion, botlib_import_t *import)")
	draw_debug_areas = _extract_function_block(be_interface, "void BotDrawDebugAreas(vec3_t origin, int enable, int areanum)")
	draw_avoid_spots = _extract_function_block(ai_move, "void BotDrawAvoidSpots(int movestate)")
	ea_walk = _extract_function_block(be_ea, "void EA_Walk(int client)")
	ea_crouch = _extract_function_block(be_ea, "void EA_Crouch(int client)")

	assert botlib_export.index("aas_export_t aas;") < botlib_export.index("ea_export_t ea;")
	assert botlib_export.index("ea_export_t ea;") < botlib_export.index("ai_export_t ai;")
	assert botlib_export.index("ai_export_t ai;") < botlib_export.index("int (*BotLibSetup)(void);")

	assert ea_export.index("(*EA_Action)") < ea_export.index("(*EA_Walk)")
	assert ea_export.index("(*EA_Walk)") < ea_export.index("(*EA_Gesture)")
	assert ea_export.index("(*EA_Respawn)") < ea_export.index("(*EA_MoveUp)")
	assert ea_export.index("(*EA_MoveRight)") < ea_export.index("(*EA_Crouch)")
	assert ea_export.index("(*EA_Crouch)") < ea_export.index("(*EA_SelectWeapon)")
	assert ea_export.index("(*EA_View)") < ea_export.index("(*EA_EndRegular)")
	assert ea_export.index("(*EA_EndRegular)") < ea_export.index("(*EA_GetInput)")
	assert ea_export.index("(*EA_GetInput)") < ea_export.index("(*EA_ResetInput)")
	assert ai_export.index("(*GeneticParentsAndChildSelection)") < ai_export.index("(*BotDrawDebugAreas)")
	assert ai_export.index("(*BotDrawDebugAreas)") < ai_export.index("(*BotDrawAvoidSpots)")
	assert "bi->actionflags |= ACTION_WALK;" in ea_walk
	assert "bi->actionflags |= ACTION_CROUCH;" in ea_crouch

	assert init_ea.index("ea->EA_Action = EA_Action;") < init_ea.index("ea->EA_Walk = EA_Walk;")
	assert init_ea.index("ea->EA_Walk = EA_Walk;") < init_ea.index("ea->EA_Gesture = EA_Gesture;")
	assert "ea->EA_EndRegular = EA_EndRegular;" in init_ea
	assert "ea->EA_GetInput = EA_GetInput;" in init_ea
	assert "ea->EA_ResetInput = EA_ResetInput;" in init_ea
	assert init_ai.index("ai->GeneticParentsAndChildSelection = GeneticParentsAndChildSelection;") < init_ai.index(
		"ai->BotDrawDebugAreas = BotDrawDebugAreas;"
	)
	assert init_ai.index("ai->BotDrawDebugAreas = BotDrawDebugAreas;") < init_ai.index(
		"ai->BotDrawAvoidSpots = BotDrawAvoidSpots;"
	)
	assert "RETAIL_BOT_DEBUG_AREA_REFRESH\t0.1f" in be_interface
	assert "RETAIL_BOT_DEBUG_AREA_RADIUS\t512" in be_interface
	assert "AAS_ClearShownDebugLines();" in draw_debug_areas
	assert "AAS_ClearShownPolygons();" in draw_debug_areas
	assert "VectorLength(dir) > RETAIL_BOT_DEBUG_AREA_RADIUS" in draw_debug_areas
	assert "AAS_inPVS(aasworld.areas[area].center, origin)" in draw_debug_areas
	assert "AAS_ShowAreaPolygons(area, LINECOLOR_ORANGE, qtrue);" in draw_debug_areas
	assert "AAS_NextAreaReachability(area, 0)" in draw_debug_areas
	assert "AAS_ReachabilityFromNum(reachnum, &reach);" in draw_debug_areas
	assert "traveltype = reach.traveltype & TRAVELTYPE_MASK;" in draw_debug_areas
	assert "traveltype == TRAVEL_JUMP || traveltype == TRAVEL_WALKOFFLEDGE" in draw_debug_areas
	assert "traveltype == TRAVEL_ROCKETJUMP" in draw_debug_areas
	assert "AAS_DrawArrow(reach.start, reach.end, linecolor, LINECOLOR_YELLOW);" in draw_debug_areas
	assert "ms = BotMoveStateFromHandle(movestate);" in draw_avoid_spots
	assert "AAS_ClearShownDebugLines();" in draw_avoid_spots
	assert "i < ms->numavoidspots" in draw_avoid_spots
	assert "AAS_DrawCross(ms->avoidspots[i].origin, ms->avoidspots[i].radius, LINECOLOR_RED);" in draw_avoid_spots

	assert aas_export.index("(*AAS_PredictRoute)") < aas_export.index("(*AAS_AlternativeRouteGoals)")
	assert aas_export.index("(*AAS_AlternativeRouteGoals)") < aas_export.index("(*AAS_Swimming)")
	assert aas_export.index("(*AAS_Swimming)") < aas_export.index("(*AAS_PredictClientMovement)")
	assert init_aas.index("aas->AAS_PredictRoute = AAS_PredictRoute;") < init_aas.index(
		"aas->AAS_AlternativeRouteGoals = AAS_AlternativeRouteGoals;"
	)
	assert init_aas.index("aas->AAS_AlternativeRouteGoals = AAS_AlternativeRouteGoals;") < init_aas.index(
		"aas->AAS_Swimming = AAS_Swimming;"
	)
	assert init_aas.index("aas->AAS_Swimming = AAS_Swimming;") < init_aas.index(
		"aas->AAS_PredictClientMovement = AAS_PredictClientMovement;"
	)

	assert "Com_Memset( &be_botlib_export, 0, sizeof( be_botlib_export ) );" in get_api
	assert "Init_AAS_Export(&be_botlib_export.aas);" in get_api
	assert "Init_EA_Export(&be_botlib_export.ea);" in get_api
	assert "Init_AI_Export(&be_botlib_export.ai);" in get_api
	assert "be_botlib_export.BotLibSetup = Export_BotLibSetup;" in get_api
	assert "be_botlib_export.BotLibStartFrame = Export_BotLibStartFrame;" in get_api

	assert "004a7fc0    void __convention(\"regparm\") sub_4a7fc0" in ql_steam_hlil
	assert "004a803d  arg1[0x12] = sub_494870" in ql_steam_hlil
	assert "004a8044  arg1[0x13] = sub_494db0" in ql_steam_hlil
	assert "004a804b  arg1[0x14] = sub_486cf0" in ql_steam_hlil
	assert "004a8052  arg1[0x15] = sub_488190" in ql_steam_hlil
	assert "004a8060    void __convention(\"regparm\") sub_4a8060" in ql_steam_hlil
	assert "004a8074  arg1[3] = sub_4a7a90" in ql_steam_hlil
	assert "004a807b  arg1[4] = sub_4a7a70" in ql_steam_hlil
	assert "004a8082  arg1[5] = sub_4a7920" in ql_steam_hlil
	assert "004a80a5  arg1[0x10] = sub_4a7a50" in ql_steam_hlil
	assert "004a80f2  arg1[0x15] = sub_4a7be0" in ql_steam_hlil
	assert "004a8100  arg1[0x16] = sub_4d7980" in ql_steam_hlil
	assert "004a80f9  arg1[0x17] = sub_4a7c10" in ql_steam_hlil
	assert "004a8107  arg1[0x18] = sub_4a7c40" in ql_steam_hlil
	assert "00484bf0    float* sub_484bf0(float* arg1, int32_t arg2, float* arg3)" in ql_steam_hlil
	assert aliases["sub_484BF0"] == "BotDrawDebugAreas"
	assert "if (arg2 != 0)" in ql_steam_hlil
	assert "sub_4844a0()" in ql_steam_hlil
	assert "sub_484470()" in ql_steam_hlil
	assert "data_e41f28 = fconvert.s(x87_r7_3)" in ql_steam_hlil
	assert "x87_r7_14 - temp2_1" in ql_steam_hlil
	assert "sub_482a90(ebx_2 + edx_1 + 0x24, arg1)" in ql_steam_hlil
	assert "sub_4848e0(i_3, 5, 1)" in ql_steam_hlil
	assert "sub_484a80(&var_28, &var_1c, ecx_3, 4)" in ql_steam_hlil
	assert "00484dc0    void* sub_484dc0(int32_t arg1)" in ql_steam_hlil
	assert aliases["sub_484DC0"] == "BotDrawAvoidSpots"
	assert "void* result = sub_49fa60(arg1)" in ql_steam_hlil
	assert "if (*(result_1 + 0x300) s> 0)" in ql_steam_hlil
	assert "void* esi_1 = result_1 + 0x80" in ql_steam_hlil
	assert "sub_4849a0(esi_1, fconvert.s(fconvert.t(*(esi_1 + 0xc))), 1)" in ql_steam_hlil
	assert "004a83c0    int32_t sub_4a83c0" in ql_steam_hlil

	for address, name in (
		("496A80", "BotFreeCharacter"),
		("497590", "BotLoadCharacter"),
		("497780", "Characteristic_Float"),
		("497810", "Characteristic_BFloat"),
		("4978C0", "Characteristic_Integer"),
		("497950", "Characteristic_BInteger"),
		("4979E0", "Characteristic_String"),
		("497CB0", "BotQueueConsoleMessage"),
		("497BD0", "BotRemoveConsoleMessage"),
		("497DE0", "BotNextConsoleMessage"),
		("497E60", "BotNumConsoleMessages"),
		("497F00", "UnifyWhiteSpaces"),
		("498710", "BotReplaceSynonyms"),
		("498020", "StringContains"),
		("4999C0", "BotFindMatch"),
		("499BF0", "BotMatchVariable"),
		("49AFB0", "BotLoadChatFile"),
		("49BAE0", "BotReplyChat"),
		("49C1B0", "BotChatLength"),
		("49C210", "BotEnterChat"),
		("49C300", "BotGetChatMessage"),
		("49C370", "BotSetChatGender"),
		("49C3D0", "BotSetChatName"),
		("49F680", "BotResetGoalState"),
		("49D9B0", "BotResetAvoidGoals"),
		("49DBA0", "BotRemoveFromAvoidGoals"),
		("49E650", "BotPushGoal"),
		("49E6E0", "BotPopGoal"),
		("49E740", "BotEmptyGoalStack"),
		("49DA20", "BotDumpAvoidGoals"),
		("49E590", "BotDumpGoalStack"),
		("49D940", "BotGoalName"),
		("49E790", "BotGetTopGoal"),
		("49E800", "BotGetSecondGoal"),
		("49F3C0", "BotTouchingGoal"),
		("49F560", "BotItemGoalInVisButNotVisible"),
		("49DDF0", "BotGetLevelItemGoal"),
		("49E000", "BotGetNextCampSpotGoal"),
		("49DF80", "BotGetMapLocationGoal"),
		("49DC40", "BotAvoidGoalTime"),
		("49DD00", "BotSetAvoidGoalTime"),
		("49F6F0", "BotLoadItemWeights"),
		("49F780", "BotFreeItemWeights"),
		("49CC30", "BotInterbreedGoalFuzzyLogic"),
		("49CCF0", "BotSaveGoalFuzzyLogic"),
		("49CD30", "BotMutateGoalFuzzyLogic"),
		("49F7F0", "BotAllocGoalState"),
		("49F840", "BotFreeGoalState"),
		("4A0990", "BotAddAvoidSpot"),
		("4A5FA0", "WeaponWeightIndex"),
		("4A5FF0", "BotFreeWeaponWeights"),
		("4A6190", "BotChooseBestFightWeapon"),
		("4A6100", "BotGetWeaponInfo"),
		("4A6060", "BotLoadWeaponWeights"),
		("4A62A0", "BotAllocWeaponState"),
		("4A62D0", "BotFreeWeaponState"),
		("4A6260", "BotResetWeaponState"),
		("4A6340", "BotSetupWeaponAI"),
		("4A6380", "BotShutdownWeaponAI"),
	):
		assert aliases[f"sub_{address}"] == name

	assert "004a8110    void __convention(\"regparm\") sub_4a8110" in ql_steam_hlil
	assert "004a8110  *arg1 = sub_497590" in ql_steam_hlil
	assert "004a8116  arg1[1] = sub_496a80" in ql_steam_hlil
	assert "004a814e  arg1[9] = sub_497cb0" in ql_steam_hlil
	assert "004a8155  arg1[0xa] = sub_497bd0" in ql_steam_hlil
	assert "004a815c  arg1[0xb] = sub_497de0" in ql_steam_hlil
	assert "004a8163  arg1[0xc] = sub_497e60" in ql_steam_hlil
	assert "004a8178  arg1[0xf] = sub_49bae0" in ql_steam_hlil
	assert "004a817f  arg1[0x10] = sub_49c1b0" in ql_steam_hlil
	assert "004a8186  arg1[0x11] = sub_49c210" in ql_steam_hlil
	assert "004a818d  arg1[0x12] = sub_49c300" in ql_steam_hlil
	assert "004a8194  arg1[0x13] = sub_498020" in ql_steam_hlil
	assert "004a819b  arg1[0x14] = sub_4999c0" in ql_steam_hlil
	assert "004a81a2  arg1[0x15] = sub_499bf0" in ql_steam_hlil
	assert "004a81a9  arg1[0x16] = sub_497f00" in ql_steam_hlil
	assert "004a81b0  arg1[0x17] = sub_498710" in ql_steam_hlil
	assert "004a81b7  arg1[0x18] = sub_49afb0" in ql_steam_hlil
	assert "004a81be  arg1[0x19] = sub_49c370" in ql_steam_hlil
	assert "004a81c5  arg1[0x1a] = sub_49c3d0" in ql_steam_hlil
	assert "004a81cc  arg1[0x1b] = sub_49f680" in ql_steam_hlil
	assert "004a820d  arg1[0x23] = sub_49d940" in ql_steam_hlil
	assert "004a8271  arg1[0x2d] = sub_49dc40" in ql_steam_hlil
	assert "004a82cb  arg1[0x36] = sub_49f7f0" in ql_steam_hlil
	assert "004a82d5  arg1[0x37] = sub_49f840" in ql_steam_hlil
	assert "004a834d  arg1[0x43] = sub_4a0990" in ql_steam_hlil
	assert "004a8357  arg1[0x44] = sub_4a6190" in ql_steam_hlil
	assert "004a8361  arg1[0x45] = sub_4a6100" in ql_steam_hlil
	assert "004a836b  arg1[0x46] = sub_4a6060" in ql_steam_hlil
	assert "004a8375  arg1[0x47] = sub_4a62a0" in ql_steam_hlil
	assert "004a837f  arg1[0x48] = sub_4a62d0" in ql_steam_hlil
	assert "004a8389  arg1[0x49] = sub_4a6260" in ql_steam_hlil
	assert "004a8393  arg1[0x4a] = sub_49c810" in ql_steam_hlil
	assert "004a839d  arg1[0x4b] = sub_484bf0" in ql_steam_hlil
	assert "004a83a7  arg1[0x4c] = sub_484dc0" in ql_steam_hlil
	assert "004a83e0  sub_4c95e0(&data_16dd860, 0, 0x224)" in ql_steam_hlil
	assert "004a840e  sub_4a7fc0(&data_16dd860)" in ql_steam_hlil
	assert "004a8418  sub_4a8060(&data_16dd8b8)" in ql_steam_hlil
	assert "004a8422  sub_4a8110(&data_16dd91c)" in ql_steam_hlil
	assert "004a8427  data_16dda50 = sub_4a7ce0" in ql_steam_hlil
	assert "004a8481  data_16dda74 = sub_4a7e90" in ql_steam_hlil


def test_botlib_export_table_aliases_cover_aas_ea_and_top_level_helpers() -> None:
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	for address, name in (
		("4829F0", "AAS_PointContents"),
		("482AB0", "AAS_NextBSPEntity"),
		("482AD0", "AAS_ValueForBSPEpairKey"),
		("482B70", "AAS_VectorForBSPEpairKey"),
		("482C30", "AAS_FloatForBSPEpairKey"),
		("482CA0", "AAS_IntForBSPEpairKey"),
		("4851B0", "AAS_EntityInfo"),
		("486200", "AAS_Initialized"),
		("486400", "AAS_Time"),
		("488190", "AAS_PredictClientMovement"),
		("488B50", "AAS_AreaReachability"),
		("492990", "AAS_EnableRoutingArea"),
		("495270", "AAS_PresenceTypeBoundingBox"),
		("4954B0", "AAS_PointAreaNum"),
		("495540", "AAS_PointReachabilityAreaIndex"),
		("4967E0", "AAS_BBoxAreas"),
		("496830", "AAS_AreaInfo"),
	):
		assert aliases[f"sub_{address}"] == name

	for address, name in (
		("4A78C0", "EA_Say"),
		("4A78F0", "EA_SayTeam"),
		("4A7920", "EA_Gesture"),
		("4A7940", "EA_Command"),
		("4A7950", "EA_SelectWeapon"),
		("4A7970", "EA_Attack"),
		("4A7990", "EA_Talk"),
		("4A79B0", "EA_Use"),
		("4A79D0", "EA_Respawn"),
		("4A79F0", "EA_Jump"),
		("4A7A20", "EA_DelayedJump"),
		("4A7A50", "EA_Crouch"),
		("4A7A70", "EA_Walk"),
		("4A7A90", "EA_Action"),
		("4A7AB0", "EA_MoveUp"),
		("4A7AD0", "EA_MoveDown"),
		("4A7AF0", "EA_MoveForward"),
		("4A7B10", "EA_MoveBack"),
		("4A7B30", "EA_MoveLeft"),
		("4A7B50", "EA_MoveRight"),
		("4A7B70", "EA_Move"),
		("4A7BE0", "EA_View"),
		("4A7C10", "EA_GetInput"),
		("4A7C40", "EA_ResetInput"),
	):
		assert aliases[f"sub_{address}"] == name

	for address, name in (
		("4A7CE0", "Export_BotLibSetup"),
		("4A7DC0", "Export_BotLibShutdown"),
		("4A7E40", "Export_BotLibVarSet"),
		("4A7E60", "Export_BotLibVarGet"),
		("4A7E90", "Export_BotLibStartFrame"),
		("4A7ED0", "Export_BotLibLoadMap"),
		("4A7F40", "Export_BotLibUpdateEntity"),
		("4A7FC0", "Init_AAS_Export"),
		("4A8060", "Init_EA_Export"),
		("4A83C0", "GetBotLibAPI"),
		("4AC260", "PC_LoadSourceHandle"),
		("4AC350", "PC_FreeSourceHandle"),
		("4AD200", "PC_AddGlobalDefine"),
	):
		assert aliases[f"sub_{address}"] == name

	assert "sub_4D7980" not in aliases
	assert "sub_4D7970" not in aliases

	for assignment in (
		"004a7fc0  *arg1 = sub_4851b0",
		"004a7fc6  arg1[1] = sub_486200",
		"004a7fcd  arg1[2] = sub_495270",
		"004a7fd4  arg1[3] = sub_486400",
		"004a7fdb  arg1[4] = sub_4954b0",
		"004a7fe2  arg1[5] = sub_495540",
		"004a7ff0  arg1[7] = sub_4967e0",
		"004a7ff7  arg1[8] = sub_496830",
		"004a7ffe  arg1[9] = sub_4829f0",
		"004a8005  arg1[0xa] = sub_482ab0",
		"004a800c  arg1[0xb] = sub_482ad0",
		"004a8013  arg1[0xc] = sub_482b70",
		"004a801a  arg1[0xd] = sub_482c30",
		"004a8021  arg1[0xe] = sub_482ca0",
		"004a8028  arg1[0xf] = sub_488b50",
		"004a8036  arg1[0x11] = sub_492990",
		"004a8052  arg1[0x15] = sub_488190",
		"004a8060  *arg1 = sub_4a7940",
		"004a8066  arg1[1] = sub_4a78c0",
		"004a806d  arg1[2] = sub_4a78f0",
		"004a8074  arg1[3] = sub_4a7a90",
		"004a807b  arg1[4] = sub_4a7a70",
		"004a8082  arg1[5] = sub_4a7920",
		"004a8089  arg1[6] = sub_4a7990",
		"004a8090  arg1[7] = sub_4a7970",
		"004a8097  arg1[8] = sub_4a79b0",
		"004a809e  arg1[9] = sub_4a79d0",
		"004a80a5  arg1[0x10] = sub_4a7a50",
		"004a80ac  arg1[0xa] = sub_4a7ab0",
		"004a80b3  arg1[0xb] = sub_4a7ad0",
		"004a80ba  arg1[0xc] = sub_4a7af0",
		"004a80c1  arg1[0xd] = sub_4a7b10",
		"004a80c8  arg1[0xe] = sub_4a7b30",
		"004a80cf  arg1[0xf] = sub_4a7b50",
		"004a80d6  arg1[0x11] = sub_4a7950",
		"004a80dd  arg1[0x12] = sub_4a79f0",
		"004a80e4  arg1[0x13] = sub_4a7a20",
		"004a80eb  arg1[0x14] = sub_4a7b70",
		"004a80f2  arg1[0x15] = sub_4a7be0",
		"004a80f9  arg1[0x17] = sub_4a7c10",
		"004a8100  arg1[0x16] = sub_4d7980",
		"004a8107  arg1[0x18] = sub_4a7c40",
		"004a83c0    int32_t sub_4a83c0(int32_t arg1, int32_t arg2)",
		"004a83de  __builtin_memcpy(dest: &data_16dd800, src: arg2, n: 0x58)",
		"004a840e  sub_4a7fc0(&data_16dd860)",
		"004a8418  sub_4a8060(&data_16dd8b8)",
		"004a8422  sub_4a8110(&data_16dd91c)",
		"004a8427  data_16dda50 = sub_4a7ce0",
		"004a8431  data_16dda54 = sub_4a7dc0",
		"004a843b  data_16dda58 = sub_4a7e40",
		"004a8445  data_16dda5c = sub_4a7e60",
		"004a844f  data_16dda60 = sub_4ad200",
		"004a8459  data_16dda64 = sub_4ac260",
		"004a8463  data_16dda68 = sub_4ac350",
		"004a846d  data_16dda6c = sub_4acb10",
		"004a8477  data_16dda70 = sub_4ac390",
		"004a8481  data_16dda74 = sub_4a7e90",
		"004a848b  data_16dda78 = sub_4a7ed0",
		"004a8495  data_16dda7c = sub_4a7f40",
		"004a849f  data_16dda80 = sub_4d7970",
	):
		assert assignment in ql_steam_hlil


def test_get_botlib_api_core_export_tail_matches_retail_table_order() -> None:
	botlib_h = BOTLIB_H.read_text(encoding="utf-8")
	be_interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	botlib_export = _extract_function_block(botlib_h, "typedef struct botlib_export_s")
	get_api = _extract_function_block(be_interface, "botlib_export_t *GetBotLibAPI(int apiVersion, botlib_import_t *import)")

	for source_anchor in (
		"#define\tBOTLIB_API_VERSION\t\t2",
		"typedef struct botlib_export_s",
		"aas_export_t aas;",
		"ea_export_t ea;",
		"ai_export_t ai;",
	):
		assert source_anchor in botlib_h

	for source_anchor in (
		"assert(import);",
		"botimport = *import;",
		"assert(botimport.Print);",
		"Com_Memset( &be_botlib_export, 0, sizeof( be_botlib_export ) );",
		"if ( apiVersion != BOTLIB_API_VERSION )",
		'Mismatched BOTLIB_API_VERSION: expected %i, got %i\\n',
		"return NULL;",
		"Init_AAS_Export(&be_botlib_export.aas);",
		"Init_EA_Export(&be_botlib_export.ea);",
		"Init_AI_Export(&be_botlib_export.ai);",
		"return &be_botlib_export;",
	):
		assert source_anchor in get_api

	previous_source_index = -1
	for source_anchor in (
		"Com_Memset( &be_botlib_export, 0, sizeof( be_botlib_export ) );",
		"if ( apiVersion != BOTLIB_API_VERSION )",
		"Init_AAS_Export(&be_botlib_export.aas);",
		"Init_EA_Export(&be_botlib_export.ea);",
		"Init_AI_Export(&be_botlib_export.ai);",
	):
		source_index = get_api.index(source_anchor)
		assert previous_source_index < source_index
		previous_source_index = source_index

	for evidence in (
		"004a83c0    int32_t sub_4a83c0(int32_t arg1, int32_t arg2)",
		"004a83de  __builtin_memcpy(dest: &data_16dd800, src: arg2, n: 0x58)",
		"004a83e0  sub_4c95e0(&data_16dd860, 0, 0x224)",
		"004a83f0  if (arg1 != 2)",
		'004a83fc      data_16dd800(3, "Mismatched BOTLIB_API_VERSION: e',
		"004a8408      return 0",
		"004a840e  sub_4a7fc0(&data_16dd860)",
		"004a8418  sub_4a8060(&data_16dd8b8)",
		"004a8422  sub_4a8110(&data_16dd91c)",
		"004a84af  return &data_16dd860",
	):
		assert evidence in ql_steam_hlil

	assert aliases["sub_4A83C0"] == "GetBotLibAPI"
	assert "FUN_004a83c0,004a83c0,240,0,unknown" in ghidra_functions

	previous_field_index = botlib_export.index("ai_export_t ai;")
	previous_assignment_index = get_api.index("Init_AI_Export(&be_botlib_export.ai);")
	previous_hlil_index = ql_steam_hlil.index("004a8422  sub_4a8110(&data_16dd91c)")
	for field_name, source_name, address, table_slot, hlil_address, ghidra_size in BOTLIB_EXPORT_CORE_TAIL:
		field_index = botlib_export.index(f"(*{field_name})")
		assert previous_field_index < field_index
		previous_field_index = field_index

		assignment = f"be_botlib_export.{field_name} = {source_name};"
		assignment_index = get_api.index(assignment)
		assert previous_assignment_index < assignment_index
		previous_assignment_index = assignment_index

		hlil_assignment = f"{hlil_address}  {table_slot} = sub_{address.lower()}"
		hlil_index = ql_steam_hlil.index(hlil_assignment)
		assert previous_hlil_index < hlil_index
		previous_hlil_index = hlil_index

		if field_name == "Test":
			assert f"sub_{address}" not in aliases
		else:
			assert aliases[f"sub_{address}"] == source_name

		if ghidra_size is not None:
			assert f"FUN_00{address.lower()},00{address.lower()},{ghidra_size},0,unknown" in ghidra_functions


def test_botlib_lifecycle_parser_and_aas_internal_aliases_match_retail_references() -> None:
	be_interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	aas_main = BOTLIB_AAS_MAIN.read_text(encoding="utf-8")
	ai_move = BOTLIB_AI_MOVE.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	setup = _extract_function_block(be_interface, "int Export_BotLibSetup(void)")
	shutdown = _extract_function_block(be_interface, "int Export_BotLibShutdown(void)")
	load_map = _extract_function_block(be_interface, "int Export_BotLibLoadMap(const char *mapname)")
	start_frame = _extract_function_block(aas_main, "int AAS_StartFrame(float time)")
	load_files = _extract_function_block(aas_main, "int AAS_LoadFiles(const char *mapname)")
	set_brush_model_types = _extract_function_block(ai_move, "void BotSetBrushModelTypes(void)")

	assert setup.index("errnum = AAS_Setup();") < setup.index("errnum = EA_Setup();")
	assert setup.index("errnum = EA_Setup();") < setup.index("errnum = BotSetupWeaponAI();")
	assert setup.index("errnum = BotSetupWeaponAI();") < setup.index("errnum = BotSetupGoalAI();")
	assert setup.index("errnum = BotSetupGoalAI();") < setup.index("errnum = BotSetupChatAI();")
	assert setup.index("errnum = BotSetupChatAI();") < setup.index("errnum = BotSetupMoveAI();")
	assert shutdown.index("BotShutdownChatAI();") < shutdown.index("BotShutdownMoveAI();")
	assert shutdown.index("BotShutdownMoveAI();") < shutdown.index("BotShutdownGoalAI();")
	assert shutdown.index("BotShutdownGoalAI();") < shutdown.index("BotShutdownWeaponAI();")
	assert shutdown.index("BotShutdownWeaponAI();") < shutdown.index("BotShutdownWeights();")
	assert shutdown.index("BotShutdownWeights();") < shutdown.index("BotShutdownCharacters();")
	assert shutdown.index("AAS_Shutdown();") < shutdown.index("EA_Shutdown();")
	assert shutdown.index("LibVarDeAllocAll();") < shutdown.index("PC_RemoveAllGlobalDefines();")
	assert shutdown.index("Log_Shutdown();") < shutdown.index("PC_CheckOpenSourceHandles();")
	assert load_map.index("errnum = AAS_LoadMap(mapname);") < load_map.index("BotInitLevelItems();")
	assert load_map.index("BotInitLevelItems();") < load_map.index("BotSetBrushModelTypes();")
	assert "AAS_UnlinkInvalidEntities();" in start_frame
	assert "AAS_InvalidateEntities();" in start_frame
	assert "AAS_ContinueInit(time);" in start_frame
	assert "AAS_WriteRouteCache();" in start_frame
	assert "AAS_ResetEntityLinks();" in load_files
	assert "AAS_LoadBSPFile();" in load_files
	assert "errnum = AAS_LoadAASFile(aasfile);" in load_files
	assert 'AAS_ValueForBSPEpairKey(ent, "classname", classname, MAX_EPAIRKEY)' in set_brush_model_types
	assert 'AAS_ValueForBSPEpairKey(ent, "model", model, MAX_EPAIRKEY)' in set_brush_model_types

	for address, name in (
		("4830C0", "AAS_DumpBSPData"),
		("483110", "AAS_LoadBSPFile"),
		("485370", "AAS_ResetEntityLinks"),
		("4853B0", "AAS_InvalidateEntities"),
		("4853F0", "AAS_UnlinkInvalidEntities"),
		("485600", "AAS_DumpAASData"),
		("486210", "AAS_ContinueInit"),
		("4862E0", "AAS_StartFrame"),
		("4864C0", "AAS_LoadFiles"),
		("486550", "AAS_LoadMap"),
		("4865B0", "AAS_Setup"),
		("492570", "AAS_InitReachability"),
		("493A50", "AAS_InitRouting"),
		("493AD0", "AAS_FreeRoutingCaches"),
		("4951D0", "AAS_InitAlternativeRouting"),
		("495230", "AAS_ShutdownAlternativeRouting"),
		("495350", "AAS_InitAASLinkHeap"),
		("495420", "AAS_FreeAASLinkHeap"),
		("495450", "AAS_InitAASLinkedEntities"),
		("495490", "AAS_FreeAASLinkedEntities"),
		("497A80", "BotShutdownCharacters"),
		("49F8B0", "BotSetupGoalAI"),
		("49F920", "BotShutdownGoalAI"),
		("4A0310", "BotSetBrushModelTypes"),
		("4A5980", "BotSetupMoveAI"),
		("4A5A60", "BotShutdownMoveAI"),
		("4A7820", "BotShutdownWeights"),
		("4A7C80", "EA_Setup"),
		("4A7CA0", "EA_Shutdown"),
		("4A7CC0", "Sys_MilliSeconds"),
		("4AA070", "PC_RemoveAllGlobalDefines"),
		("4AC050", "LoadSourceFile"),
		("4AC0E0", "FreeSource"),
		("4AD0E0", "PC_DefineFromString"),
	):
		assert aliases[f"sub_{address}"] == name

	for evidence in (
		"004a7d6a  sub_4865b0()",
		"004a7d73  sub_4a7c80()",
		"004a7d7c  int32_t result = sub_4a6340()",
		"004a7d85      result = sub_49f8b0()",
		"004a7d8e          sub_49c560()",
		"004a7d97          result = sub_4a5980()",
		"004a7de4  sub_49c5f0()",
		"004a7de9  sub_4a5a60()",
		"004a7dee  sub_49f920()",
		"004a7df3  sub_4a6380()",
		"004a7df8  sub_4a7820()",
		"004a7dfd  sub_497a80()",
		"004a7e02  sub_486640()",
		"004a7e07  sub_4a7ca0()",
		"004a7e11  sub_4aa070()",
		"004a7e16  sub_4a8960()",
		"004a7e2f  sub_4ac410()",
		"004a7f09  int32_t result = sub_486550(arg1)",
		"004a7f15  sub_49d3c0()",
		"004a7f1a  sub_4a0310()",
	):
		assert evidence in ql_steam_hlil


def test_botlib_aas_cluster_and_debug_internal_aliases_match_retail_references() -> None:
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	for address, name in (
		("4831B0", "AAS_UpdatePortal"),
		("4832C0", "AAS_FloodClusterAreas_r"),
		("483440", "AAS_FloodClusterAreasUsingReachabilities"),
		("483610", "AAS_NumberClusterAreas"),
		("4837C0", "AAS_FindClusters"),
		("4838D0", "AAS_CreatePortals"),
		("483950", "AAS_ConnectedAreas_r"),
		("483A00", "AAS_ConnectedAreas"),
		("483AA0", "AAS_GetAdjacentAreasWithLessPresenceTypes_r"),
		("484020", "AAS_FindPossiblePortals"),
		("484060", "AAS_TestPortals"),
		("4840F0", "AAS_CountForcedClusterPortals"),
		("484150", "AAS_CreateViewPortals"),
		("484190", "AAS_SetViewPortalsAsClusterPortals"),
		("484470", "AAS_ClearShownPolygons"),
		("4844A0", "AAS_ClearShownDebugLines"),
		("484550", "AAS_PermanentLine"),
		("4848E0", "AAS_ShowAreaPolygons"),
		("4849A0", "AAS_DrawCross"),
		("4861A0", "AAS_Error"),
		("4861F0", "AAS_Loaded"),
		("486410", "AAS_ProjectPointOntoVector"),
	):
		assert aliases[f"sub_{address}"] == name

	for evidence in (
		"004831b0    int32_t sub_4831b0(int32_t arg1, int32_t arg2)",
		'00483230              sub_4861a0("AAS_MAX_PORTALINDEXSIZE")',
		"004832c0    int32_t sub_4832c0(int32_t arg1, int32_t arg2)",
		'0048342d  sub_4861a0("AAS_FloodClusterAreas_r: areanum',
		"004837c0    int32_t sub_4837c0()",
		"004838d0    void sub_4838d0()",
		'00483b7f      sub_4861a0("MAX_PORTALAREAS")',
		"00484020    int32_t sub_484020()",
		"00484470    int32_t sub_484470()",
		"004844a0    int32_t sub_4844a0()",
		"004848e0    int32_t sub_4848e0(int32_t arg1, int32_t arg2, int32_t arg3)",
		"004861a0    int32_t sub_4861a0(int32_t arg1)",
		"004861f0    int32_t sub_4861f0()",
		"00486410    int32_t sub_486410(float* arg1, float* arg2, float* arg3, float* arg4)",
	):
		assert evidence in ql_steam_hlil

	for row in (
		"FUN_004831b0,004831b0,257,0,unknown",
		"FUN_00486410,00486410,164,0,unknown",
		"FUN_004861a0,004861a0,72,0,unknown",
	):
		assert row in ghidra_functions


def test_botlib_precompiler_and_script_internal_aliases_match_retail_references() -> None:
	ql_steam_hlil_part03 = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ql_steam_hlil_part04 = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	for address, name in (
		("4A8AD0", "SourceError"),
		("4A8B30", "SourceWarning"),
		("4A8B90", "PC_PushIndent"),
		("4A8BD0", "PC_PushScript"),
		("4A8C30", "PC_CopyToken"),
		("4A8C90", "PC_ReadSourceToken"),
		("4A8DB0", "PC_UnreadSourceToken"),
		("4A9230", "PC_StringizeTokens"),
		("4A92D0", "PC_MergeTokens"),
		("4A9370", "PC_NameHash"),
		("4A93B0", "PC_AddDefineToHash"),
		("4A9410", "PC_FindHashedDefine"),
		("4A94A0", "PC_FindDefineParm"),
		("4A9500", "PC_FreeDefine"),
		("4A9B70", "PC_ExpandDefineIntoSource"),
		("4A9BD0", "PC_ConvertPath"),
		("4A9EA0", "PC_ReadLine"),
		("4A9F20", "PC_Directive_undef"),
		("4AA0F0", "PC_CopyDefine"),
		("4AA250", "PC_AddGlobalDefinesToSource"),
		("4AA2E0", "PC_Directive_if_def"),
		("4AA3E0", "PC_Directive_ifdef"),
		("4AA400", "PC_Directive_ifndef"),
		("4AA420", "PC_Directive_else"),
		("4AA4E0", "PC_Directive_endif"),
		("4AA540", "PC_OperatorPriority"),
		("4AB780", "PC_Directive_elif"),
		("4AB810", "PC_Directive_if"),
		("4AB880", "PC_Directive_line"),
		("4AB8A0", "PC_Directive_error"),
		("4AB900", "PC_Directive_pragma"),
		("4AB9F0", "UnreadSignToken"),
		("4ABA70", "PC_Directive_eval"),
		("4ABB40", "PC_Directive_evalfloat"),
		("4ABC10", "PC_ReadDirective"),
		("4ABD20", "PC_DollarDirective_evalint"),
		("4ABE00", "PC_DollarDirective_evalfloat"),
		("4ABF10", "PC_ReadDollarDirective"),
		("4AC030", "PC_UnreadLastToken"),
		("4AD230", "PS_CreatePunctuationTable"),
		("4AD320", "ScriptError"),
		("4AD390", "ScriptWarning"),
		("4AD400", "PS_ReadWhiteSpace"),
		("4AD7B0", "PS_ReadString"),
		("4AD920", "PS_ReadName"),
		("4AD9C0", "NumberValue"),
		("4ADE70", "PS_ReadPunctuation"),
		("4ADF30", "PS_ReadPrimitive"),
		("4ADFC0", "PS_ReadToken"),
		("4AE4C0", "StripDoubleQuotes"),
		("4AE520", "StripSingleQuotes"),
		("4AE580", "SetScriptFlags"),
		("4AE5A0", "EndOfScript"),
		("4AE5C0", "LoadScriptFile"),
		("4AE720", "LoadScriptMemory"),
		("4AE7E0", "FreeScript"),
		("4AE810", "PS_SetBaseFolder"),
		("4AE830", "FindField"),
		("4AE8A0", "ReadNumber"),
		("4AECD0", "ReadStructure"),
	):
		assert aliases[f"sub_{address}"] == name

	for evidence in (
		"004a8ad0    int32_t sub_4a8ad0(void* arg1, int32_t arg2)",
		"004a8c90    int32_t sub_4a8c90(void* arg1, int32_t* arg2)",
		"004a9230    int32_t sub_4a9230(void* arg1, char* arg2)",
		"004aa2e0    int32_t sub_4aa2e0(void* arg1, int32_t arg2)",
		"004ab780    int32_t sub_4ab780(int32_t arg1)",
		"004abc10    int32_t sub_4abc10(void* arg1)",
		"004ac030    int32_t sub_4ac030(void* arg1)",
		"004ad230    int32_t sub_4ad230(void* arg1, int32_t* arg2)",
		"004adfc0    int32_t sub_4adfc0(int32_t* arg1, int32_t* arg2)",
		"004ae830    void* sub_4ae830(int32_t* arg1, char* arg2)",
		"004ae8a0    void sub_4ae8a0(int32_t arg1, void* arg2, float* arg3)",
		"004aecd0    int32_t sub_4aecd0(int32_t arg1, void* arg2, int32_t arg3)",
	):
		assert evidence in ql_steam_hlil_part03 or evidence in ql_steam_hlil_part04

	for row in (
		"FUN_004a8ad0,004a8ad0,96,0,unknown",
		"FUN_004adfc0,004adfc0,414,0,unknown",
		"FUN_004ae830,004ae830,104,0,unknown",
		"FUN_004ae8a0,004ae8a0,1062,0,unknown",
		"FUN_004aecd0,004aecd0,851,0,unknown",
	):
		assert row in ghidra_functions


def test_botlib_structure_resource_reader_source_shape_matches_retail_references() -> None:
	l_struct = BOTLIB_L_STRUCT.read_text(encoding="utf-8")
	ai_goal = BOTLIB_AI_GOAL.read_text(encoding="utf-8")
	ai_weap = BOTLIB_AI_WEAP.read_text(encoding="utf-8")
	ql_steam_hlil_part03 = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ql_steam_hlil_part04 = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
	ql_steam_ghidra = (
		REPO_ROOT
		/ "references"
		/ "reverse-engineering"
		/ "ghidra"
		/ "quakelive_steam"
		/ "decompile_top_functions.c"
	).read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	find_field = _extract_function_block(l_struct, "fielddef_t *FindField(fielddef_t *defs, char *name)")
	read_number = _extract_function_block(l_struct, "qboolean ReadNumber(source_t *source, fielddef_t *fd, void *p)")
	read_char = _extract_function_block(l_struct, "qboolean ReadChar(source_t *source, fielddef_t *fd, void *p)")
	read_string = _extract_function_block(l_struct, "int ReadString(source_t *source, fielddef_t *fd, void *p)")
	read_structure = _extract_function_block(l_struct, "int ReadStructure(source_t *source, structdef_t *def, char *structure)")

	assert "for (i = 0; defs[i].name; i++)" in find_field
	assert "if (!strcmp(defs[i].name, name)) return &defs[i];" in find_field
	assert "return NULL;" in find_field

	assert "if (!PC_ExpectAnyToken(source, &token)) return 0;" in read_number
	assert "if (token.type == TT_PUNCTUATION)" in read_number
	assert "if (fd->type & FT_UNSIGNED)" in read_number
	assert 'SourceError(source, "expected unsigned value, found %s", token.string);' in read_number
	assert 'if (strcmp(token.string, "-"))' in read_number
	assert 'SourceError(source, "unexpected punctuation %s", token.string);' in read_number
	assert "negative = qtrue;" in read_number
	assert 'SourceError(source, "expected number, found %s", token.string);' in read_number
	assert "if (token.subtype & TT_FLOAT)" in read_number
	assert "if ((fd->type & FT_TYPE) != FT_FLOAT)" in read_number
	assert 'SourceError(source, "unexpected float");' in read_number
	assert "floatval = token.floatvalue;" in read_number
	assert "if (negative) floatval = -floatval;" in read_number
	assert "if (floatval < fd->floatmin || floatval > fd->floatmax)" in read_number
	assert 'SourceError(source, "float out of range [%f, %f]", fd->floatmin, fd->floatmax);' in read_number
	assert "*(float *) p = (float) floatval;" in read_number
	assert "if (fd->type & FT_UNSIGNED) {intmin = 0; intmax = 255;}" in read_number
	assert "else {intmin = -128; intmax = 127;}" in read_number
	assert "if (fd->type & FT_UNSIGNED) {intmin = 0; intmax = 65535;}" in read_number
	assert "else {intmin = -32768; intmax = 32767;}" in read_number
	assert "intmin = Maximum(intmin, fd->floatmin);" in read_number
	assert "intmax = Minimum(intmax, fd->floatmax);" in read_number
	assert 'SourceError(source, "value %d out of range [%d, %d]", intval, intmin, intmax);' in read_number
	assert 'SourceError(source, "value %d out of range [%f, %f]", intval, fd->floatmin, fd->floatmax);' in read_number
	assert "if (fd->type & FT_UNSIGNED) *(unsigned char *) p = (unsigned char) intval;" in read_number
	assert "if (fd->type & FT_UNSIGNED) *(unsigned int *) p = (unsigned int) intval;" in read_number
	assert "*(float *) p = (float) intval;" in read_number
	assert aliases["sub_4AE8A0"] == "ReadNumber"

	assert "if (token.type == TT_LITERAL)" in read_char
	assert "StripSingleQuotes(token.string);" in read_char
	assert "*(char *) p = token.string[0];" in read_char
	assert "PC_UnreadLastToken(source);" in read_char
	assert "if (!ReadNumber(source, fd, p)) return 0;" in read_char
	assert "if (!PC_ExpectTokenType(source, TT_STRING, 0, &token)) return 0;" in read_string
	assert "StripDoubleQuotes(token.string);" in read_string
	assert "strncpy((char *) p, token.string, MAX_STRINGFIELD);" in read_string
	assert "((char *)p)[MAX_STRINGFIELD-1] = '\\0';" in read_string

	assert "if (!PC_ExpectTokenString(source, \"{\")) return 0;" in read_structure
	assert "fd = FindField(def->fields, token.string);" in read_structure
	assert 'SourceError(source, "unknown structure field %s", token.string);' in read_structure
	assert "if (fd->type & FT_ARRAY)" in read_structure
	assert "num = fd->maxarray;" in read_structure
	assert "if (!PC_ExpectTokenString(source, \"{\")) return qfalse;" in read_structure
	assert "p = (void *)(structure + fd->offset);" in read_structure
	assert "if (PC_CheckTokenString(source, \"}\")) break;" in read_structure
	assert "case FT_CHAR:" in read_structure
	assert "if (!ReadChar(source, fd, p)) return qfalse;" in read_structure
	assert "case FT_INT:" in read_structure
	assert "if (!ReadNumber(source, fd, p)) return qfalse;" in read_structure
	assert "case FT_FLOAT:" in read_structure
	assert "case FT_STRING:" in read_structure
	assert "if (!ReadString(source, fd, p)) return qfalse;" in read_structure
	assert "case FT_STRUCT:" in read_structure
	assert 'SourceError(source, "BUG: no sub structure defined");' in read_structure
	assert "ReadStructure(source, fd->substruct, (char *) p);" in read_structure
	assert "if (!ReadStructure(source, fd->substruct" not in read_structure
	assert 'SourceError(source, "expected a comma, found %s", token.string);' in read_structure
	assert aliases["sub_4AECD0"] == "ReadStructure"

	assert "if (!ReadStructure(source, &iteminfo_struct, (char *) ii))" in ai_goal
	assert "if (!ReadStructure(source, &weaponinfo_struct, (char *) &weaponinfo))" in ai_weap
	assert "if (!ReadStructure(source, &projectileinfo_struct, (char *) &wc->projectileinfo[wc->numprojectiles]))" in ai_weap

	for evidence in (
		"004ae830    void* sub_4ae830(int32_t* arg1, char* arg2)",
		"004ae897              return &arg1[esi * 7]",
		"004ae8a0    void sub_4ae8a0(int32_t arg1, void* arg2, float* arg3)",
		'004ae9ed                  sub_4a8ad0(arg1, "unexpected float")',
		'004aea50                      sub_4a8ad0(arg1, "float out of range [%f, %f]")',
		'004aeb84                      sub_4a8ad0(arg1, "value %d out of range [%f, %f]")',
		'004aecab          sub_4a8ad0(arg1, "value %d out of range [%d, %d]")',
		"004aecd0    int32_t sub_4aecd0(int32_t arg1, void* arg2, int32_t arg3)",
		"004aed8e          void* eax_8 = sub_4ae830(*(arg2 + 4), &var_438)",
		"004aee75                              int32_t eax_17 = sub_4ae8a0(arg1, eax_8, esi_2)",
		"004aee8b                          int32_t eax_18 = sub_4ae8a0(arg1, eax_8, esi_2)",
		"004aeec3                          sub_4ae4c0(&var_868)",
		"004aeed2                          strncpy(esi_2, &var_868, 0x50)",
		"004aeef2                          sub_4aecd0(arg1, eax_20, esi_2)",
		'004aefed                              sub_4a8ad0(arg1, "BUG: no sub structure defined")',
		'004af00f                          var_888_10 = "expected a comma, found %s"',
	):
		assert evidence in ql_steam_hlil_part04

	assert "0049cf5d                  if (sub_4aecd0(eax_3, &data_563f9c, eax_15) == 0)" in ql_steam_hlil_part03
	assert "004a5c42              if (sub_4aecd0(eax_4, &data_5643d4, &var_6a0) == 0)" in ql_steam_hlil_part03
	assert "004a5d13              if (sub_4aecd0(eax_4, &data_5643dc, result[1] * 0xd0 + result[2]) == 0)" in ql_steam_hlil_part03
	assert "iVar4 = FUN_004aecd0(iVar2,&DAT_005643d4,local_6a0);" in ql_steam_ghidra
	assert "iVar4 = FUN_004aecd0(iVar2,&DAT_005643dc,piVar3[1] * 0xd0 + piVar3[2]);" in ql_steam_ghidra


def test_botlib_structure_reader_consumers_match_retail_resource_tables() -> None:
	ai_goal = BOTLIB_AI_GOAL.read_text(encoding="utf-8")
	ai_weap = BOTLIB_AI_WEAP.read_text(encoding="utf-8")
	ql_steam_hlil_part03 = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ql_steam_ghidra = (
		REPO_ROOT
		/ "references"
		/ "reverse-engineering"
		/ "ghidra"
		/ "quakelive_steam"
		/ "decompile_top_functions.c"
	).read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	load_item_config = _extract_function_block(ai_goal, "itemconfig_t *LoadItemConfig(char *filename)")
	load_weapon_config = _extract_function_block(ai_weap, "weaponconfig_t *LoadWeaponConfig(char *filename)")

	for source_anchor in (
		'{"name", ITEMINFO_OFS(name), FT_STRING}',
		'{"model", ITEMINFO_OFS(model), FT_STRING}',
		'{"modelindex", ITEMINFO_OFS(modelindex), FT_INT}',
		'{"type", ITEMINFO_OFS(type), FT_INT}',
		'{"index", ITEMINFO_OFS(index), FT_INT}',
		'{"respawntime", ITEMINFO_OFS(respawntime), FT_FLOAT}',
		'{"mins", ITEMINFO_OFS(mins), FT_FLOAT|FT_ARRAY, 3}',
		'{"maxs", ITEMINFO_OFS(maxs), FT_FLOAT|FT_ARRAY, 3}',
		"sizeof(iteminfo_t), iteminfo_fields",
	):
		assert source_anchor in ai_goal

	for source_anchor in (
		'{"number", WEAPON_OFS(number), FT_INT}',
		'{"name", WEAPON_OFS(name), FT_STRING}',
		'{"level", WEAPON_OFS(level), FT_INT}',
		'{"projectile", WEAPON_OFS(projectile), FT_STRING}',
		'{"numprojectiles", WEAPON_OFS(numprojectiles), FT_INT}',
		'{"recoil", WEAPON_OFS(recoil), FT_FLOAT|FT_ARRAY, 3}',
		'{"offset", WEAPON_OFS(offset), FT_FLOAT|FT_ARRAY, 3}',
		'{"angleoffset", WEAPON_OFS(angleoffset), FT_FLOAT|FT_ARRAY, 3}',
		'{"spinup", WEAPON_OFS(spinup), FT_FLOAT}',
		'{"spindown", WEAPON_OFS(spindown), FT_FLOAT}',
		"sizeof(weaponinfo_t), weaponinfo_fields",
	):
		assert source_anchor in ai_weap

	for source_anchor in (
		'{"name", PROJECTILE_OFS(name), FT_STRING}',
		'{"model", WEAPON_OFS(model), FT_STRING}',
		'{"flags", PROJECTILE_OFS(flags), FT_INT}',
		'{"gravity", PROJECTILE_OFS(gravity), FT_FLOAT}',
		'{"damage", PROJECTILE_OFS(damage), FT_INT}',
		'{"radius", PROJECTILE_OFS(radius), FT_FLOAT}',
		'{"visdamage", PROJECTILE_OFS(visdamage), FT_INT}',
		'{"damagetype", PROJECTILE_OFS(damagetype), FT_INT}',
		'{"healthinc", PROJECTILE_OFS(healthinc), FT_INT}',
		'{"push", PROJECTILE_OFS(push), FT_FLOAT}',
		'{"detonation", PROJECTILE_OFS(detonation), FT_FLOAT}',
		'{"bounce", PROJECTILE_OFS(bounce), FT_FLOAT}',
		'{"bouncefric", PROJECTILE_OFS(bouncefric), FT_FLOAT}',
		'{"bouncestop", PROJECTILE_OFS(bouncestop), FT_FLOAT}',
		"sizeof(projectileinfo_t), projectileinfo_fields",
	):
		assert source_anchor in ai_weap

	assert 'max_iteminfo = (int) LibVarValue("max_iteminfo", "256");' in load_item_config
	assert 'LibVarSet( "max_iteminfo", "256" );' in load_item_config
	assert 'if (!strcmp(token.string, "iteminfo"))' in load_item_config
	assert 'SourceError(source, "more than %d item info defined\\n", max_iteminfo);' in load_item_config
	assert "ii = &ic->iteminfo[ic->numiteminfo];" in load_item_config
	assert "if (!PC_ExpectTokenType(source, TT_STRING, 0, &token))" in load_item_config
	assert "StripDoubleQuotes(token.string);" in load_item_config
	assert "strncpy(ii->classname, token.string, sizeof(ii->classname)-1);" in load_item_config
	assert "if (!ReadStructure(source, &iteminfo_struct, (char *) ii))" in load_item_config
	assert "ii->number = ic->numiteminfo;" in load_item_config
	assert "ic->numiteminfo++;" in load_item_config
	assert 'SourceError(source, "unknown definition %s\\n", token.string);' in load_item_config
	assert 'botimport.Print(PRT_WARNING, "no item info loaded\\n");' in load_item_config

	assert 'max_weaponinfo = (int) LibVarValue("max_weaponinfo", "32");' in load_weapon_config
	assert 'max_projectileinfo = (int) LibVarValue("max_projectileinfo", "32");' in load_weapon_config
	assert 'if (!strcmp(token.string, "weaponinfo"))' in load_weapon_config
	assert "Com_Memset(&weaponinfo, 0, sizeof(weaponinfo_t));" in load_weapon_config
	assert "if (!ReadStructure(source, &weaponinfo_struct, (char *) &weaponinfo))" in load_weapon_config
	assert 'botimport.Print(PRT_ERROR, "weapon info number %d out of range in %s\\n", weaponinfo.number, path);' in load_weapon_config
	assert "Com_Memcpy(&wc->weaponinfo[weaponinfo.number], &weaponinfo, sizeof(weaponinfo_t));" in load_weapon_config
	assert "wc->weaponinfo[weaponinfo.number].valid = qtrue;" in load_weapon_config
	assert 'else if (!strcmp(token.string, "projectileinfo"))' in load_weapon_config
	assert 'botimport.Print(PRT_ERROR, "more than %d projectiles defined in %s\\n", max_projectileinfo, path);' in load_weapon_config
	assert "Com_Memset(&wc->projectileinfo[wc->numprojectiles], 0, sizeof(projectileinfo_t));" in load_weapon_config
	assert "if (!ReadStructure(source, &projectileinfo_struct, (char *) &wc->projectileinfo[wc->numprojectiles]))" in load_weapon_config
	assert "wc->numprojectiles++;" in load_weapon_config
	assert 'botimport.Print(PRT_ERROR, "unknown definition %s in %s\\n", token.string, path);' in load_weapon_config
	assert 'botimport.Print(PRT_ERROR, "weapon %s uses undefined projectile in %s\\n", wc->weaponinfo[i].name, path);' in load_weapon_config

	dump_weapon_index = ai_weap.index("#ifdef DEBUG_AI_WEAP")
	dump_writer_index = ai_weap.index("WriteStructure(fp, &projectileinfo_struct")
	dump_end_index = ai_weap.index("#endif //DEBUG_AI_WEAP")
	load_weapon_index = ai_weap.index("weaponconfig_t *LoadWeaponConfig")
	assert dump_weapon_index < dump_writer_index < dump_end_index < load_weapon_index

	assert aliases["sub_49CD80"] == "BotLoadItemConfig"
	assert aliases["sub_4A5A90"] == "LoadWeaponConfig"
	assert "FUN_0049cd80,0049cd80,646,0,unknown" in ghidra_functions
	assert "FUN_004a5a90,004a5a90,1273,0,unknown" in ghidra_functions

	for evidence in (
		'0049cdb0  int32_t esi = sub_526000(sub_4a8770("max_iteminfo", "256"))',
		'0049ceba          char const* const ecx_5 = "iteminfo"',
		"0049ce48  char* result = sub_4a8a50(esi * 0xec + 8)",
		"0049cf46                  strncpy(eax_15, &var_478, 0x1f)",
		"0049cf5d                  if (sub_4aecd0(eax_3, &data_563f9c, eax_15) == 0)",
		"0049cf68                  *(eax_15 + 0xe8) = *result",
		'0049cf87                  var_490_3 = "more than %d item info defined\\n"',
		'0049ce84      data_16dd800(2, "no item info loaded\\n")',
		'004a5ac0  int32_t edi = sub_526000(sub_4a8770("max_weaponinfo", "32"))',
		'004a5b0b  int32_t eax_3 = sub_526000(sub_4a8770("max_projectileinfo", "32"))',
		"004a5bac  int32_t* result = sub_4a8a50(var_6a8 * 0xd0 + edi * 0x228 + 0x10)",
		'004a5be0          char const* const ecx_3 = "weaponinfo"',
		"004a5c42              if (sub_4aecd0(eax_4, &data_5643d4, &var_6a0) == 0)",
		"004a5c74              sub_4cb7d0(var_69c * 0x228 + result[3], &var_6a0, 0x228)",
		"004a5c8b              *(var_69c * 0x228 + result[3]) = 1",
		'004a5c97              char const* const ecx_5 = "projectileinfo"',
		"004a5cf1              sub_4c95e0(eax_24 * 0xd0 + result[2], 0, 0xd0)",
		"004a5d13              if (sub_4aecd0(eax_4, &data_5643dc, result[1] * 0xd0 + result[2]) == 0)",
		"004a5d19              result[1] += 1",
		'004a5e33                  data_16dd800(3, "unknown definition %s in %s\\n", &var_478, &var_48)',
	):
		assert evidence in ql_steam_hlil_part03

	for evidence in (
		'FUN_004a8770("max_weaponinfo",&DAT_0052f574);',
		'FUN_004a8770("max_projectileinfo",&DAT_0052f574);',
		"piVar3 = (int *)FUN_004a8a50(local_6a8 * 0xd0 + 0x10 + local_6a4 * 0x228);",
		'pcVar8 = "weaponinfo";',
		"iVar4 = FUN_004aecd0(iVar2,&DAT_005643d4,local_6a0);",
		'pcVar8 = "projectileinfo";',
		"FUN_004c95e0(piVar3[1] * 0xd0 + piVar3[2],0,0xd0);",
		"iVar4 = FUN_004aecd0(iVar2,&DAT_005643dc,piVar3[1] * 0xd0 + piVar3[2]);",
		'pcVar8 = "weapon %s uses undefined projectile in %s\\n";',
		'(*DAT_016dd800)(2,"no weapon info loaded\\n");',
	):
		assert evidence in ql_steam_ghidra


def test_botlib_character_resource_parser_matches_retail_references() -> None:
	ai_char = BOTLIB_AI_CHAR.read_text(encoding="utf-8")
	ql_steam_hlil_part03 = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ql_steam_ghidra = (
		REPO_ROOT
		/ "references"
		/ "reverse-engineering"
		/ "ghidra"
		/ "quakelive_steam"
		/ "decompile_top_functions.c"
	).read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	load_from_file = _extract_function_block(ai_char, "bot_character_t *BotLoadCharacterFromFile(char *charfile, int skill)")
	load_cached = _extract_function_block(ai_char, "int BotLoadCachedCharacter(char *charfile, float skill, int reload)")
	load_skill = _extract_function_block(ai_char, "int BotLoadCharacterSkill(char *charfile, float skill)")

	assert "#define MAX_CHARACTERISTICS\t\t80" in ai_char
	assert "#define CT_INTEGER\t\t\t\t1" in ai_char
	assert "#define CT_FLOAT\t\t\t\t2" in ai_char
	assert "#define CT_STRING\t\t\t\t3" in ai_char
	assert '#define DEFAULT_CHARACTER\t\t"bots/default_c.c"' in ai_char
	assert "char filename[MAX_QPATH];" in ai_char
	assert "float skill;" in ai_char
	assert "bot_characteristic_t c[1];" in ai_char

	assert "PC_SetBaseFolder(BOTFILESBASEFOLDER);" in load_from_file
	assert "source = LoadSourceFile(charfile);" in load_from_file
	assert 'botimport.Print(PRT_ERROR, "counldn\'t load %s\\n", charfile);' in load_from_file
	assert "ch = (bot_character_t *) GetClearedMemory(sizeof(bot_character_t) +" in load_from_file
	assert "MAX_CHARACTERISTICS * sizeof(bot_characteristic_t));" in load_from_file
	assert "strcpy(ch->filename, charfile);" in load_from_file
	assert 'if (!strcmp(token.string, "skill"))' in load_from_file
	assert "if (!PC_ExpectTokenType(source, TT_NUMBER, 0, &token))" in load_from_file
	assert 'if (!PC_ExpectTokenString(source, "{"))' in load_from_file
	assert "if (skill < 0 || (int)token.intvalue == skill)" in load_from_file
	assert "foundcharacter = qtrue;" in load_from_file
	assert "ch->skill = token.intvalue;" in load_from_file
	assert "if (token.type != TT_NUMBER || !(token.subtype & TT_INTEGER))" in load_from_file
	assert 'SourceError(source, "expected integer index, found %s\\n", token.string);' in load_from_file
	assert "if (index < 0 || index > MAX_CHARACTERISTICS)" in load_from_file
	assert 'SourceError(source, "characteristic index out of range [0, %d]\\n", MAX_CHARACTERISTICS);' in load_from_file
	assert 'SourceError(source, "characteristic %d already initialized\\n", index);' in load_from_file
	assert "if (token.subtype & TT_FLOAT)" in load_from_file
	assert "ch->c[index].type = CT_FLOAT;" in load_from_file
	assert "ch->c[index].type = CT_INTEGER;" in load_from_file
	assert "StripDoubleQuotes(token.string);" in load_from_file
	assert "ch->c[index].value.string = GetMemory(strlen(token.string)+1);" in load_from_file
	assert "ch->c[index].type = CT_STRING;" in load_from_file
	assert 'SourceError(source, "expected integer, float or string, found %s\\n", token.string);' in load_from_file
	assert "indent = 1;" in load_from_file
	assert 'if (!strcmp(token.string, "{")) indent++;' in load_from_file
	assert 'else if (!strcmp(token.string, "}")) indent--;' in load_from_file
	assert 'SourceError(source, "unknown definition %s\\n", token.string);' in load_from_file
	assert "if (!foundcharacter)" in load_from_file

	assert "cachedhandle = BotFindCachedCharacter(charfile, skill);" in load_cached
	assert 'botimport.Print(PRT_MESSAGE, "loaded cached skill %f from %s\\n", skill, charfile);' in load_cached
	assert "intskill = (int) (skill + 0.5);" in load_cached
	assert "ch = BotLoadCharacterFromFile(charfile, intskill);" in load_cached
	assert "ch = BotLoadCharacterFromFile(DEFAULT_CHARACTER, intskill);" in load_cached
	assert "cachedhandle = BotFindCachedCharacter(charfile, -1);" in load_cached
	assert "ch = BotLoadCharacterFromFile(DEFAULT_CHARACTER, -1);" in load_cached
	assert 'botimport.Print(PRT_WARNING, "couldn\'t load any skill from %s\\n", charfile);' in load_cached
	assert "defaultch = BotLoadCachedCharacter(DEFAULT_CHARACTER, skill, qfalse);" in load_skill
	assert 'ch = BotLoadCachedCharacter(charfile, skill, LibVarGetValue("bot_reloadcharacters"));' in load_skill
	assert "BotDefaultCharacteristics(botcharacters[ch], botcharacters[defaultch]);" in load_skill

	for address, name in (
		("496B40", "BotLoadCharacterFromFile"),
		("4970E0", "BotLoadCachedCharacter"),
		("497360", "BotLoadCharacterSkill"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_00496b40,00496b40,1271,0,unknown",
		"FUN_004970e0,004970e0,627,0,unknown",
		"FUN_00497360,00497360,104,0,unknown",
	):
		assert row in ghidra_functions

	for evidence in (
		"00496b40    char* sub_496b40(char* arg1, int32_t arg2)",
		'00496b58  char const* const __saved_ebx = "botfiles"',
		"00496baa  char* result = sub_4a89d0(0x2cc)",
		'00496be5          char const* const ecx_3 = "skill"',
		"00496e4e                  if (var_38 != 3 || (var_34 & 0x1000) == 0)",
		"00496e4e                  else if (var_30 s< 0 || var_30 s> 0x50)",
		"00496e7c                      if (*(edi + result + 0x44) != 0)",
		"00496eb6                                  *(edi + result + 0x44) = 2",
		"00496ec8                                  *(edi + result + 0x44) = 1",
		"00496edf                              sub_4ae4c0(&var_438)",
		"00496f25                              *(edi + result + 0x44) = 3",
		"00497040    int32_t sub_497040(char* arg1, float arg2)",
		"004970e0    int32_t sub_4970e0(char* arg1, float arg2, int32_t arg3)",
		'004971cf          int32_t eax_7 = sub_497040("bots/default_c.c", fconvert.s(fconvert.t(arg2)))',
		'00497200      eax_9, ecx_2 = sub_496b40("bots/default_c.c", eax_4)',
		'00497304          char* eax_18 = sub_496b40("bots/default_c.c", 0xffffffff)',
		"00497360    int32_t sub_497360(char* arg1, float arg2)",
		'00497373  int32_t eax = sub_4970e0("bots/default_c.c", fconvert.s(fconvert.t(arg2)), 0)',
	):
		assert evidence in ql_steam_hlil_part03

	for evidence in (
		"/* FUN_00496b40 @ 00496b40 size 1271 */",
		"iVar6 = FUN_004a89d0(0x2cc);",
		'pcVar9 = "skill";',
		'pcVar9 = "expected integer index, found %s\\n";',
		"if (((int)pbVar7 < 0) || (0x50 < (int)pbVar7)) {",
		'pcVar9 = "characteristic index out of range [0, %d]\\n";',
		'pcVar9 = "characteristic %d already initialized\\n";',
		'pcVar9 = "expected integer, float or string, found %s\\n";',
		"FUN_004ae4c0(local_438);",
		"/* FUN_004a6b40 @ 004a6b40 size 1524 */",
	):
		assert evidence in ql_steam_ghidra


def test_botlib_weight_resource_parser_matches_retail_references() -> None:
	ai_weight = BOTLIB_AI_WEIGHT.read_text(encoding="utf-8")
	ql_steam_hlil_part03 = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ql_steam_ghidra = (
		REPO_ROOT
		/ "references"
		/ "reverse-engineering"
		/ "ghidra"
		/ "quakelive_steam"
		/ "decompile_top_functions.c"
	).read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	read_value = _extract_function_block(ai_weight, "int ReadValue(source_t *source, float *value)")
	read_fuzzy_weight = _extract_function_block(ai_weight, "int ReadFuzzyWeight(source_t *source, fuzzyseperator_t *fs)")
	read_separators = _extract_function_block(ai_weight, "fuzzyseperator_t *ReadFuzzySeperators_r(source_t *source)")
	read_config = _extract_function_block(ai_weight, "weightconfig_t *ReadWeightConfig(char *filename)")

	assert "#define MAX_INVENTORYVALUE\t\t\t999999" in ai_weight
	assert "#define EVALUATERECURSIVELY" in ai_weight
	assert "#define MAX_WEIGHT_FILES\t\t\t128" in ai_weight
	assert "weightconfig_t\t*weightFileList[MAX_WEIGHT_FILES];" in ai_weight

	assert 'if (!strcmp(token.string, "-"))' in read_value
	assert 'SourceWarning(source, "negative value set to zero\\n");' in read_value
	assert "if (token.type != TT_NUMBER)" in read_value
	assert 'SourceError(source, "invalid return value %s\\n", token.string);' in read_value
	assert "*value = token.floatvalue;" in read_value

	assert 'if (PC_CheckTokenString(source, "balance"))' in read_fuzzy_weight
	assert "fs->type = WT_BALANCE;" in read_fuzzy_weight
	assert 'if (!PC_ExpectTokenString(source, "(")) return qfalse;' in read_fuzzy_weight
	assert "if (!ReadValue(source, &fs->weight)) return qfalse;" in read_fuzzy_weight
	assert "if (!ReadValue(source, &fs->minweight)) return qfalse;" in read_fuzzy_weight
	assert "if (!ReadValue(source, &fs->maxweight)) return qfalse;" in read_fuzzy_weight
	assert "fs->type = 0;" in read_fuzzy_weight
	assert "fs->minweight = fs->weight;" in read_fuzzy_weight
	assert "fs->maxweight = fs->weight;" in read_fuzzy_weight
	assert 'if (!PC_ExpectTokenString(source, ";")) return qfalse;' in read_fuzzy_weight

	assert "founddefault = qfalse;" in read_separators
	assert 'if (!PC_ExpectTokenString(source, "(")) return NULL;' in read_separators
	assert "if (!PC_ExpectTokenType(source, TT_NUMBER, TT_INTEGER, &token)) return NULL;" in read_separators
	assert 'if (!PC_ExpectTokenString(source, "{")) return NULL;' in read_separators
	assert 'def = !strcmp(token.string, "default");' in read_separators
	assert 'if (def || !strcmp(token.string, "case"))' in read_separators
	assert 'SourceError(source, "switch already has a default\\n");' in read_separators
	assert "fs->value = MAX_INVENTORYVALUE;" in read_separators
	assert "founddefault = qtrue;" in read_separators
	assert "fs->value = token.intvalue;" in read_separators
	assert "newindent = qfalse;" in read_separators
	assert 'if (!strcmp(token.string, "{"))' in read_separators
	assert 'if (!strcmp(token.string, "return"))' in read_separators
	assert "if (!ReadFuzzyWeight(source, fs))" in read_separators
	assert 'else if (!strcmp(token.string, "switch"))' in read_separators
	assert "fs->child = ReadFuzzySeperators_r(source);" in read_separators
	assert 'SourceError(source, "invalid name %s\\n", token.string);' in read_separators
	assert 'SourceWarning(source, "switch without default\\n");' in read_separators
	assert "fs->weight = 0;" in read_separators

	assert 'if (!LibVarGetValue("bot_reloadcharacters"))' in read_config
	assert "for( n = 0; n < MAX_WEIGHT_FILES; n++ )" in read_config
	assert "if( strcmp( filename, config->filename ) == 0 )" in read_config
	assert 'botimport.Print( PRT_ERROR, "weightFileList was full trying to load %s\\n", filename );' in read_config
	assert "PC_SetBaseFolder(BOTFILESBASEFOLDER);" in read_config
	assert "source = LoadSourceFile(filename);" in read_config
	assert "config = (weightconfig_t *) GetClearedMemory(sizeof(weightconfig_t));" in read_config
	assert "Q_strncpyz( config->filename, filename, sizeof(config->filename) );" in read_config
	assert 'if (!strcmp(token.string, "weight"))' in read_config
	assert 'SourceWarning(source, "too many fuzzy weights\\n");' in read_config
	assert "if (!PC_ExpectTokenType(source, TT_STRING, 0, &token))" in read_config
	assert "StripDoubleQuotes(token.string);" in read_config
	assert "config->weights[config->numweights].name = (char *) GetClearedMemory(strlen(token.string) + 1);" in read_config
	assert 'if (!strcmp(token.string, "switch"))' in read_config
	assert "fs = ReadFuzzySeperators_r(source);" in read_config
	assert 'else if (!strcmp(token.string, "return"))' in read_config
	assert "fs->value = MAX_INVENTORYVALUE;" in read_config
	assert "if (!ReadFuzzyWeight(source, fs))" in read_config
	assert 'SourceError(source, "invalid name %s\\n", token.string);' in read_config
	assert "weightFileList[avail] = config;" in read_config

	writer_block_index = ai_weight.index("#if 0")
	write_weight_index = ai_weight.index("qboolean WriteFuzzyWeight")
	write_config_index = ai_weight.index("qboolean WriteWeightConfig")
	find_weight_index = ai_weight.index("int FindFuzzyWeight")
	assert writer_block_index < write_weight_index < write_config_index < find_weight_index

	for address, name in (
		("4A63F0", "ReadValue"),
		("4A64D0", "ReadFuzzyWeight"),
		("4A65C0", "FreeFuzzySeperators_r"),
		("4A66A0", "ReadFuzzySeperators_r"),
		("4A6B40", "ReadWeightConfig"),
		("4A7140", "FindFuzzyWeight"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_004a63f0,004a63f0,211,0,unknown",
		"FUN_004a64d0,004a64d0,230,0,unknown",
		"FUN_004a66a0,004a66a0,1180,0,unknown",
		"FUN_004a6b40,004a6b40,1524,0,unknown",
	):
		assert row in ghidra_functions

	for evidence in (
		"004a63f0    int32_t sub_4a63f0(int32_t arg1, float* arg2)",
		'004a645f          sub_4a8b30(arg1, "negative value set to zero\\n")',
		'004a648f          sub_4a8ad0(arg1, "invalid return value %s\\n")',
		"004a64d0    int32_t sub_4a64d0(int32_t arg1, void* arg2)",
		"004a64ec  if (sub_4aca70(arg1, \"balance\") == 0)",
		"004a6509      if (sub_4ac650(arg1, U\"(\") != 0 && sub_4a63f0(arg1, arg2 + 0xc) != 0",
		"004a66a0    int32_t* sub_4a66a0(int32_t arg1)",
		"004a66e2  if (sub_4ac650(edi, U\"(\") != 0 && sub_4ac710(edi, 3, 0x1000, &var_438) != 0",
		'004a6753          char const* const ecx_4 = "default"',
		'004a679d              char const* const ecx_6 = "case"',
		'004a6a44              sub_4a8ad0(var_440, "switch already has a default\\n")',
		'004a6a85          sub_4a8b30(var_440, "switch without default\\n")',
		"004a6a8c          int32_t* result_3 = sub_4a89d0(0x20)",
		"004a6b40    char* sub_4a6b40(char* arg1)",
		'004a6b6c  st0, eax_2, ecx = sub_4a8680("bot_reloadcharacters")',
		"004a6bdd          edi += 1",
		"004a6be4          if (edi s>= 0x80)",
		"004a6c6e  char* eax_8 = sub_4a89d0(0x444)",
		"004a6c85  sub_4d8f40(&eax_8[0x404], arg1, 0x40)",
		'004a6ca7          void* eax_11 = &var_438',
		'004a6cad          char const* const ecx_9 = "weight"',
		'004a6f12              sub_4a8b30(esi_2, "too many fuzzy weights\\n")',
		"004a6d11          sub_4ae4c0(&var_438)",
		"004a6d34          *(eax_8 + (*eax_8 << 3) + 4) = sub_4a89d0(eax_15 - &var_437 + 1)",
		"004a6ece  data_16dd800(1, \"loaded %s\\n\", arg1)",
	):
		assert evidence in ql_steam_hlil_part03

	for evidence in (
		"/* FUN_004a6b40 @ 004a6b40 size 1524 */",
		'FUN_004a8680("bot_reloadcharacters");',
		'(*DAT_016dd800)(3,"weightFileList was full trying to load %s\\n",param_1);',
		"piVar2 = (int *)FUN_004a89d0(0x444);",
		"FUN_004d8f40(piVar2 + 0x101,param_1,0x40);",
		'pcVar6 = "weight";',
		'FUN_004a8b30(iVar8,"too many fuzzy weights\\n");',
		"iVar3 = FUN_004a66a0(iVar8);",
		"iVar3 = FUN_004a64d0(iVar8,puVar5);",
		'(*DAT_016dd800)(1,"loaded %s\\n",param_1);',
		"/* FUN_004a66a0 @ 004a66a0 size 1180 */",
		'FUN_004a8ad0(param_1,"switch already has a default\\n");',
		'FUN_004a8b30(param_1,"switch without default\\n");',
	):
		assert evidence in ql_steam_ghidra


def test_botlib_precompiler_source_handle_slice_matches_retail_references() -> None:
	l_precomp = BOTLIB_L_PRECOMP.read_text(encoding="utf-8")
	botlib_h = BOTLIB_H.read_text(encoding="utf-8")
	be_interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	server_game = SERVER_GAME.read_text(encoding="utf-8")
	server_ql_game_imports = SERVER_QL_GAME_IMPORTS.read_text(encoding="utf-8")
	game_public_h = GAME_PUBLIC_H.read_text(encoding="utf-8")
	game_syscalls = GAME_SYSCALLS.read_text(encoding="utf-8")
	ql_steam_hlil_part03 = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ql_steam_hlil_part04 = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	load_handle = _extract_function_block(l_precomp, "int PC_LoadSourceHandle(const char *filename)")
	free_handle = _extract_function_block(l_precomp, "int PC_FreeSourceHandle(int handle)")
	read_token = _extract_function_block(l_precomp, "int PC_ReadTokenHandle(int handle, pc_token_t *pc_token)")
	source_line = _extract_function_block(l_precomp, "int PC_SourceFileAndLine(int handle, char *filename, int *line)")
	set_base = _extract_function_block(l_precomp, "void PC_SetBaseFolder(char *path)")
	check_open = _extract_function_block(l_precomp, "void PC_CheckOpenSourceHandles(void)")
	get_api = _extract_function_block(be_interface, "botlib_export_t *GetBotLibAPI(int apiVersion, botlib_import_t *import)")
	syscall_impl = _extract_function_block(server_game, "static int SV_GameSystemCallsImpl( int *args, qboolean logContract )")
	load_wrapper = _extract_function_block(server_ql_game_imports, "static int QDECL QL_G_trap_PC_LoadSource( const char *filename )")
	free_wrapper = _extract_function_block(server_ql_game_imports, "static int QDECL QL_G_trap_PC_FreeSource( int handle )")
	read_wrapper = _extract_function_block(server_ql_game_imports, "static int QDECL QL_G_trap_PC_ReadToken( int handle, pc_token_t *pc_token )")
	line_wrapper = _extract_function_block(server_ql_game_imports, "static int QDECL QL_G_trap_PC_SourceFileAndLine( int handle, char *filename, int *line )")
	g_load = _extract_function_block(game_syscalls, "int trap_PC_LoadSource( const char *filename )")
	g_free = _extract_function_block(game_syscalls, "int trap_PC_FreeSource( int handle )")
	g_read = _extract_function_block(game_syscalls, "int trap_PC_ReadToken( int handle, pc_token_t *pc_token )")
	g_line = _extract_function_block(game_syscalls, "int trap_PC_SourceFileAndLine( int handle, char *filename, int *line )")

	assert "#define MAX_SOURCEFILES\t\t64" in l_precomp
	assert "source_t *sourceFiles[MAX_SOURCEFILES];" in l_precomp
	assert "for (i = 1; i < MAX_SOURCEFILES; i++)" in load_handle
	assert "if (!sourceFiles[i])" in load_handle
	assert "if (i >= MAX_SOURCEFILES)" in load_handle
	assert "PS_SetBaseFolder(\"\");" in load_handle
	assert "source = LoadSourceFile(filename);" in load_handle
	assert "if (!source)" in load_handle
	assert "sourceFiles[i] = source;" in load_handle
	assert "return i;" in load_handle

	assert "if (handle < 1 || handle >= MAX_SOURCEFILES)" in free_handle
	assert "if (!sourceFiles[handle])" in free_handle
	assert "FreeSource(sourceFiles[handle]);" in free_handle
	assert "sourceFiles[handle] = NULL;" in free_handle
	assert "return qtrue;" in free_handle

	assert "if (handle < 1 || handle >= MAX_SOURCEFILES)" in read_token
	assert "ret = PC_ReadToken(sourceFiles[handle], &token);" in read_token
	assert "strcpy(pc_token->string, token.string);" in read_token
	assert "pc_token->type = token.type;" in read_token
	assert "pc_token->subtype = token.subtype;" in read_token
	assert "pc_token->intvalue = token.intvalue;" in read_token
	assert "pc_token->floatvalue = token.floatvalue;" in read_token
	assert "if (pc_token->type == TT_STRING)" in read_token
	assert "StripDoubleQuotes(pc_token->string);" in read_token
	assert "return ret;" in read_token

	assert "strcpy(filename, sourceFiles[handle]->filename);" in source_line
	assert "if (sourceFiles[handle]->scriptstack)" in source_line
	assert "*line = sourceFiles[handle]->scriptstack->line;" in source_line
	assert "else" in source_line
	assert "*line = 0;" in source_line
	assert "PS_SetBaseFolder(path);" in set_base
	assert "for (i = 1; i < MAX_SOURCEFILES; i++)" in check_open
	assert 'botimport.Print(PRT_ERROR, "file %s still open in precompiler\\n", sourceFiles[i]->scriptstack->filename);' in check_open

	for source_anchor in (
		"int (*PC_AddGlobalDefine)(char *string);",
		"int (*PC_LoadSourceHandle)(const char *filename);",
		"int (*PC_FreeSourceHandle)(int handle);",
		"int (*PC_ReadTokenHandle)(int handle, pc_token_t *pc_token);",
		"int (*PC_SourceFileAndLine)(int handle, char *filename, int *line);",
	):
		assert source_anchor in botlib_h

	assert "be_botlib_export.PC_AddGlobalDefine = PC_AddGlobalDefine;" in get_api
	assert "be_botlib_export.PC_LoadSourceHandle = PC_LoadSourceHandle;" in get_api
	assert "be_botlib_export.PC_FreeSourceHandle = PC_FreeSourceHandle;" in get_api
	assert "be_botlib_export.PC_ReadTokenHandle = PC_ReadTokenHandle;" in get_api
	assert "be_botlib_export.PC_SourceFileAndLine = PC_SourceFileAndLine;" in get_api
	assert get_api.index("be_botlib_export.PC_AddGlobalDefine = PC_AddGlobalDefine;") < get_api.index(
		"be_botlib_export.PC_LoadSourceHandle = PC_LoadSourceHandle;"
	)
	assert get_api.index("be_botlib_export.PC_LoadSourceHandle = PC_LoadSourceHandle;") < get_api.index(
		"be_botlib_export.PC_FreeSourceHandle = PC_FreeSourceHandle;"
	)
	assert get_api.index("be_botlib_export.PC_FreeSourceHandle = PC_FreeSourceHandle;") < get_api.index(
		"be_botlib_export.PC_ReadTokenHandle = PC_ReadTokenHandle;"
	)
	assert get_api.index("be_botlib_export.PC_ReadTokenHandle = PC_ReadTokenHandle;") < get_api.index(
		"be_botlib_export.PC_SourceFileAndLine = PC_SourceFileAndLine;"
	)

	assert "case BOTLIB_PC_LOAD_SOURCE:" in syscall_impl
	assert "return botlib_export->PC_LoadSourceHandle( VMA(1) );" in syscall_impl
	assert "case BOTLIB_PC_FREE_SOURCE:" in syscall_impl
	assert "return botlib_export->PC_FreeSourceHandle( args[1] );" in syscall_impl
	assert "case BOTLIB_PC_READ_TOKEN:" in syscall_impl
	assert "return botlib_export->PC_ReadTokenHandle( args[1], VMA(2) );" in syscall_impl
	assert "case BOTLIB_PC_SOURCE_FILE_AND_LINE:" in syscall_impl
	assert "return botlib_export->PC_SourceFileAndLine( args[1], VMA(2), VMA(3) );" in syscall_impl

	assert "[BOTLIB_PC_LOAD_SOURCE] = (ql_import_f)QL_G_trap_PC_LoadSource," in server_game
	assert "[BOTLIB_PC_FREE_SOURCE] = (ql_import_f)QL_G_trap_PC_FreeSource," in server_game
	assert "[BOTLIB_PC_READ_TOKEN] = (ql_import_f)QL_G_trap_PC_ReadToken," in server_game
	assert "[BOTLIB_PC_SOURCE_FILE_AND_LINE] = (ql_import_f)QL_G_trap_PC_SourceFileAndLine," in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_G_trap_BotLibDefine;" in server_game
	assert "G_QL_IMPORT_BOTLIB_PC_LOAD_SOURCE" not in game_public_h
	assert "G_QL_IMPORT_BOTLIB_PC_FREE_SOURCE" not in game_public_h
	assert "G_QL_IMPORT_BOTLIB_PC_READ_TOKEN" not in game_public_h
	assert "G_QL_IMPORT_BOTLIB_PC_SOURCE_FILE_AND_LINE" not in game_public_h

	assert "return G_Import_Syscall( BOTLIB_PC_LOAD_SOURCE, filename );" in load_wrapper
	assert "return G_Import_Syscall( BOTLIB_PC_FREE_SOURCE, handle );" in free_wrapper
	assert "return G_Import_Syscall( BOTLIB_PC_READ_TOKEN, handle, pc_token );" in read_wrapper
	assert "return G_Import_Syscall( BOTLIB_PC_SOURCE_FILE_AND_LINE, handle, filename, line );" in line_wrapper
	assert "return syscall( BOTLIB_PC_LOAD_SOURCE, filename );" in g_load
	assert "return syscall( BOTLIB_PC_FREE_SOURCE, handle );" in g_free
	assert "return syscall( BOTLIB_PC_READ_TOKEN, handle, pc_token );" in g_read
	assert "return syscall( BOTLIB_PC_SOURCE_FILE_AND_LINE, handle, filename, line );" in g_line

	for address, name in (
		("4AC260", "PC_LoadSourceHandle"),
		("4AC350", "PC_FreeSourceHandle"),
		("4AC390", "PC_SourceFileAndLine"),
		("4AC400", "PC_SetBaseFolder"),
		("4AC410", "PC_CheckOpenSourceHandles"),
		("4ACB10", "PC_ReadTokenHandle"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_004ac260,004ac260,230,0,unknown",
		"FUN_004ac350,004ac350,59,0,unknown",
		"FUN_004ac390,004ac390,100,0,unknown",
		"FUN_004ac400,004ac400,9,0,unknown",
		"FUN_004ac410,004ac410,48,0,unknown",
		"FUN_004acb10,004acb10,163,0,unknown",
	):
		assert row in ghidra_functions

	for evidence in (
		"004a844f  data_16dda60 = sub_4ad200",
		"004a8459  data_16dda64 = sub_4ac260",
		"004a8463  data_16dda68 = sub_4ac350",
		"004a846d  data_16dda6c = sub_4acb10",
		"004a8477  data_16dda70 = sub_4ac390",
	):
		assert evidence in ql_steam_hlil_part03

	for evidence in (
		"004ac260    int32_t sub_4ac260(char* arg1)",
		"004ac278  while (*((result << 2) + &data_16dd6e0) != 0)",
		"004ac294      if (result s>= 0x40)",
		"004ac2b1  sub_4ae810(&data_54f9da)",
		"004ac2c6  if (eax_3 == 0)",
		"004ac2d8  void* eax_4 = sub_4a89a0(0xc50)",
		"004ac2f3  strncpy(eax_4, arg1, 0x40)",
		"004ac332  *((result << 2) + &data_16dd6e0) = eax_4",
		"004ac350    int32_t sub_4ac350(int32_t arg1)",
		"004ac35d  if (arg1 - 1 u<= 0x3e)",
		"004ac36b          sub_4ac0e0(eax_1)",
		"004ac373          *((arg1 << 2) + &data_16dd6e0) = 0",
		"004ac390    int32_t sub_4ac390(int32_t arg1, char* arg2, int32_t* arg3)",
		"004ac39d  if (arg1 - 1 u<= 0x3e)",
		"004ac3d4              *arg3 = *(eax_1 + 0x41c)",
		"004ac3e1          *arg3 = 0",
		"004ac400    int32_t sub_4ac400()",
		"004ac404  return sub_4ae810() __tailcall",
		"004ac410    void* sub_4ac410()",
		'004ac42a          result = data_16dd800(3, "file %s still open in precompile…", *(result + 0x804))',
		"004acb10    int32_t sub_4acb10(int32_t arg1, int32_t* arg2)",
		"004acb30  if (arg1 - 1 u<= 0x3e)",
		"004acb47          void var_438",
		"004acb73          arg2[3] = fconvert.s(fconvert.t(var_28))",
		"004acb79          *arg2 = var_38",
		"004acb7b          arg2[1] = var_34",
		"004acb7e          arg2[2] = var_30",
		"004acb84          if (var_38 == 1)",
		"004acb87              sub_4ae4c0(&arg2[4])",
	):
		assert evidence in ql_steam_hlil_part04


def test_botlib_server_import_table_keeps_retail_shared_assignments() -> None:
	sv_bot = SERVER_BOT.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	init_botlib = _extract_function_block(sv_bot, "void SV_BotInitBotLib(void)")
	debug_line_delete = _extract_function_block(sv_bot, "void BotImport_DebugLineDelete(int line)")

	assert "botlib_import.BSPEntityData = BotImport_BSPEntityData;" in init_botlib
	assert "botlib_import.DebugLineDelete = BotImport_DebugPolygonDelete;" in init_botlib
	assert "botlib_import.DebugPolygonDelete = BotImport_DebugPolygonDelete;" in init_botlib
	assert "BotImport_DebugPolygonDelete(line);" in debug_line_delete
	assert aliases["sub_4DD240"] == "BotImport_BSPEntityData"
	assert aliases["sub_4DD430"] == "BotImport_DebugPolygonDelete"

	assert "004dd940    int32_t sub_4dd940()" in ql_steam_hlil
	assert "004dd9bf  int32_t (* var_48)() = j_sub_4c0250" in ql_steam_hlil
	assert "004dda1a  int32_t (* var_14)(int32_t arg1) = sub_4dd430" in ql_steam_hlil
	assert "004dda2f  int32_t (* var_8)(int32_t arg1) = sub_4dd430" in ql_steam_hlil
	assert "004dda36  int32_t result = sub_4a83c0(2, &var_5c)" in ql_steam_hlil


def test_botlib_chat_console_message_source_shape_matches_retail_references() -> None:
	ai_chat = BOTLIB_AI_CHAT.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	remove_message = _extract_function_block(ai_chat, "void BotRemoveConsoleMessage(int chatstate, int handle)")
	queue_message = _extract_function_block(ai_chat, "void BotQueueConsoleMessage(int chatstate, int type, char *message)")
	next_message = _extract_function_block(ai_chat, "int BotNextConsoleMessage(int chatstate, bot_consolemessage_t *cm)")
	num_messages = _extract_function_block(ai_chat, "int BotNumConsoleMessages(int chatstate)")

	assert "if (m->next) m->next->prev = m->prev;" in remove_message
	assert "else cs->lastmessage = m->prev;" in remove_message
	assert "if (m->prev) m->prev->next = m->next;" in remove_message
	assert "else cs->firstmessage = m->next;" in remove_message
	assert "FreeConsoleMessage(m);" in remove_message
	assert "cs->numconsolemessages--;" in remove_message

	assert "m = AllocConsoleMessage();" in queue_message
	assert 'botimport.Print(PRT_ERROR, "empty console message heap\\n");' in queue_message
	assert "cs->handle++;" in queue_message
	assert "if (cs->handle <= 0 || cs->handle > 8192) cs->handle = 1;" in queue_message
	assert "m->handle = cs->handle;" in queue_message
	assert "m->time = AAS_Time();" in queue_message
	assert "m->type = type;" in queue_message
	assert "strncpy(m->message, message, MAX_MESSAGE_SIZE);" in queue_message
	assert "cs->lastmessage->next = m;" in queue_message
	assert "m->prev = cs->lastmessage;" in queue_message
	assert "cs->lastmessage = m;" in queue_message
	assert "cs->firstmessage = m;" in queue_message
	assert "cs->numconsolemessages++;" in queue_message

	assert "Com_Memcpy(cm, cs->firstmessage, sizeof(bot_consolemessage_t));" in next_message
	assert "cm->next = cm->prev = NULL;" in next_message
	assert "return cm->handle;" in next_message
	assert "return cs->numconsolemessages;" in num_messages

	for address, name in (
		("497BD0", "BotRemoveConsoleMessage"),
		("497CB0", "BotQueueConsoleMessage"),
		("497DE0", "BotNextConsoleMessage"),
		("497E60", "BotNumConsoleMessages"),
	):
		assert aliases[f"sub_{address}"] == name

	assert "00497bd0    int32_t* sub_497bd0(int32_t arg1, int32_t arg2)" in ql_steam_hlil
	assert "00497cb0    void* sub_497cb0(int32_t arg1, int32_t arg2, int32_t arg3)" in ql_steam_hlil
	assert "00497d72          strncpy(&edi[3], arg3, 0x100)" in ql_steam_hlil
	assert "00497dc7              *(esi + 0x134) += 1" in ql_steam_hlil
	assert "00497de0    int32_t sub_497de0(int32_t arg1, int32_t* arg2)" in ql_steam_hlil
	assert "00497e38          sub_4cb7d0(arg2, eax_4, 0x114)" in ql_steam_hlil
	assert "00497e42          arg2[0x43] = 0" in ql_steam_hlil
	assert "00497e4c          arg2[0x44] = 0" in ql_steam_hlil
	assert "00497e60    int32_t sub_497e60(int32_t arg1)" in ql_steam_hlil
	assert "00497eaa      return *(eax_1 + 0x134)" in ql_steam_hlil


def test_botlib_avoid_spots_source_shape_matches_retail_references() -> None:
	ai_move = BOTLIB_AI_MOVE.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	avoid_spots = _extract_function_block(
		ai_move,
		"int BotAvoidSpots(vec3_t origin, aas_reachability_t *reach, bot_avoidspot_t *avoidspots, int numavoidspots)",
	)

	assert "case TRAVEL_WALK: checkbetween = qtrue; break;" in avoid_spots
	assert "case TRAVEL_CROUCH: checkbetween = qtrue; break;" in avoid_spots
	assert "case TRAVEL_BARRIERJUMP: checkbetween = qtrue; break;" in avoid_spots
	assert "case TRAVEL_LADDER: checkbetween = qtrue; break;" in avoid_spots
	assert "case TRAVEL_SWIM: checkbetween = qtrue; break;" in avoid_spots
	assert "case TRAVEL_WATERJUMP: checkbetween = qtrue; break;" in avoid_spots
	assert "case TRAVEL_WALKOFFLEDGE: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_JUMP: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_TELEPORT: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_ELEVATOR: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_GRAPPLEHOOK: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_ROCKETJUMP: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_BFGJUMP: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_JUMPPAD: checkbetween = qfalse; break;" in avoid_spots
	assert "case TRAVEL_FUNCBOB: checkbetween = qfalse; break;" in avoid_spots
	assert "type = AVOID_CLEAR;" in avoid_spots
	assert "squareddist = DistanceFromLineSquared(avoidspots[i].origin, origin, reach->start);" in avoid_spots
	assert "VectorDistanceSquared(avoidspots[i].origin, origin) > squareddist" in avoid_spots
	assert "else if (checkbetween)" in avoid_spots
	assert "squareddist = DistanceFromLineSquared(avoidspots[i].origin, reach->start, reach->end);" in avoid_spots
	assert "VectorDistanceSquared(avoidspots[i].origin, reach->start) > squareddist" in avoid_spots
	assert "if (type == AVOID_ALWAYS)" in avoid_spots
	assert "return type;" in avoid_spots
	assert aliases["sub_4A0770"] == "BotAvoidSpots"

	assert "004a0770    void sub_4a0770(float* arg1, void* arg2, void* arg3, int32_t arg4)" in ql_steam_hlil
	assert "004a078c  switch ((*(arg2 + 0x24) & 0xffffff) - 2)" in ql_steam_hlil
	assert "004a0793      case 3, 5, 8, 9, 0xa, 0xb, 0xc, 0x10, 0x11" in ql_steam_hlil
	assert "004a0793          var_8 = 0" in ql_steam_hlil
	assert "004a079c          var_8 = 1" in ql_steam_hlil
	assert "004a07a5  int32_t var_c = 0" in ql_steam_hlil
	assert "004a083c          if (var_c == 1)" in ql_steam_hlil
	assert "004a0942              return " in ql_steam_hlil


def test_botlib_avoid_spot_source_shape_matches_retail_references() -> None:
	ai_move_h = (REPO_ROOT / "src" / "code" / "game" / "be_ai_move.h").read_text(encoding="utf-8")
	ai_move = BOTLIB_AI_MOVE.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	add_avoid_spot = _extract_function_block(ai_move, "void BotAddAvoidSpot(int movestate, vec3_t origin, float radius, int type)")

	assert "#define MAX_AVOIDSPOTS\t\t\t\t\t32" in ai_move_h
	assert "#define AVOID_CLEAR\t\t\t\t\t\t0" in ai_move_h
	assert "ms = BotMoveStateFromHandle(movestate);" in add_avoid_spot
	assert "if (!ms) return;" in add_avoid_spot
	assert "if (type == AVOID_CLEAR)" in add_avoid_spot
	assert "ms->numavoidspots = 0;" in add_avoid_spot
	assert "if (ms->numavoidspots >= MAX_AVOIDSPOTS)" in add_avoid_spot
	assert "return;" in add_avoid_spot
	assert "VectorCopy(origin, ms->avoidspots[ms->numavoidspots].origin);" in add_avoid_spot
	assert "ms->avoidspots[ms->numavoidspots].radius = radius;" in add_avoid_spot
	assert "ms->avoidspots[ms->numavoidspots].type = type;" in add_avoid_spot
	assert "ms->numavoidspots++;" in add_avoid_spot
	assert aliases["sub_4A0990"] == "BotAddAvoidSpot"

	assert "004a0990    void* sub_4a0990(int32_t arg1, float* arg2, float arg3, int32_t arg4)" in ql_steam_hlil
	assert "004a09d7      *(result + 0x300) = arg4" in ql_steam_hlil
	assert "004a09e0  int32_t ecx_1 = *(result + 0x300)" in ql_steam_hlil
	assert "004a09e9  if (ecx_1 s< 0x20)" in ql_steam_hlil
	assert "004a09f3      *(result + ecx_1 * 0x14 + 0x80) = fconvert.s(fconvert.t(*arg2))" in ql_steam_hlil
	assert "004a0a06      *(result + *(result + 0x300) * 0x14 + 0x84) = fconvert.s(fconvert.t(arg2[1]))" in ql_steam_hlil
	assert "004a0a19      *(result + *(result + 0x300) * 0x14 + 0x88) = fconvert.s(fconvert.t(arg2[2]))" in ql_steam_hlil
	assert "004a0a2d      *(result + ((*(result + 0x300) * 5 + 0x23) << 2)) = fconvert.s(fconvert.t(arg3))" in ql_steam_hlil
	assert "004a0a39      *(result + *(result + 0x300) * 0x14 + 0x90) = arg4" in ql_steam_hlil
	assert "004a0a40      *(result + 0x300) += 1" in ql_steam_hlil


def test_botlib_weapon_state_source_shape_matches_retail_references() -> None:
	ai_weap = BOTLIB_AI_WEAP.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")

	valid_weapon = _extract_function_block(ai_weap, "int BotValidWeaponNumber(int weaponnum)")
	get_info = _extract_function_block(ai_weap, "void BotGetWeaponInfo(int weaponstate, int weapon, weaponinfo_t *weaponinfo)")
	reset_weapon = _extract_function_block(ai_weap, "void BotResetWeaponState(int weaponstate)")

	assert 'botimport.Print(PRT_ERROR, "weapon number (%d) out of range\\n", weaponnum);' in valid_weapon
	assert 'botimport.Print(PRT_ERROR, "weapon number out of range\\n");' not in valid_weapon
	assert "if (!BotValidWeaponNumber(weapon)) return;" in get_info
	assert "ws = BotWeaponStateFromHandle(weaponstate);" in get_info
	assert get_info.index("if (!BotValidWeaponNumber(weapon)) return;") < get_info.index(
		"ws = BotWeaponStateFromHandle(weaponstate);"
	)
	assert "if (!weaponconfig) return;" not in get_info
	assert "Com_Memcpy(weaponinfo, &weaponconfig->weaponinfo[weapon], sizeof(weaponinfo_t));" in get_info
	assert "ws = BotWeaponStateFromHandle(weaponstate);" in reset_weapon
	assert "if (!ws) return;" in reset_weapon
	assert "struct weightconfig_s *weaponweightconfig;" not in reset_weapon
	assert "int *weaponweightindex;" not in reset_weapon
	assert "Com_Memset" not in reset_weapon
	assert "ws->weaponweightconfig =" not in reset_weapon
	assert "ws->weaponweightindex =" not in reset_weapon

	assert "004a5fa0    char* sub_4a5fa0(int32_t* arg1, char* arg2)" in ql_steam_hlil
	assert "004a5ff0    int32_t* sub_4a5ff0(int32_t arg1)" in ql_steam_hlil
	assert "004a6100    int32_t sub_4a6100(int32_t arg1, int32_t arg2, int32_t* arg3)" in ql_steam_hlil
	assert '004a6126  return data_16dd800(3, "weapon number (%d) out of range\\n", arg2)' in ql_steam_hlil
	assert "004a6180              return sub_4cb7d0(arg3, arg2 * 0x228 + edx_1[3], 0x228)" in ql_steam_hlil
	assert "004a6260    int32_t sub_4a6260(int32_t arg1)" in ql_steam_hlil
	assert '004a6293      return data_16dd800(4, "move state handle %d out of rang…", arg1)' in ql_steam_hlil
	assert "004a629d      return arg1" in ql_steam_hlil
	assert '004a628a  return data_16dd800(4, "invalid move state %d\\n", arg1)' in ql_steam_hlil
	assert "004a6340    int32_t sub_4a6340()" in ql_steam_hlil
	assert "004a6380    int32_t* sub_4a6380()" in ql_steam_hlil


def test_qagame_bot_obstacle_prediction_mapping_matches_retail_route_bridge() -> None:
	ai_dmq3 = GAME_AI_DMQ3.read_text(encoding="utf-8")
	aas_route = BOTLIB_AAS_ROUTE.read_text(encoding="utf-8")
	qagame_ghidra = QAGAME_GHIDRA_TOP.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART01.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	ql_steam_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	qagame_symbols = json.loads(QAGAME_SYMBOL_MAP.read_text(encoding="utf-8"))

	entry = next(function for function in qagame_symbols["functions"] if function["address"] == "0x1001DCF0")
	assert entry["raw_name"] == "FUN_1001dcf0"
	assert entry["normalized_name"] == "BotAIPredictObstacles"
	assert entry["signature"] == "int BotAIPredictObstacles(bot_state_t *bs, bot_goal_t *goal)"

	obstacle_block = _extract_function_block(
		ai_dmq3,
		"int BotAIPredictObstacles(bot_state_t *bs, bot_goal_t *goal)",
	)
	predict_route_block = _extract_function_block(
		aas_route,
		"int AAS_PredictRoute(struct aas_predictroute_s *route, int areanum, vec3_t origin",
	)

	assert "if (!bot_predictobstacles.integer)" in obstacle_block
	assert "bs->predictobstacles_goalareanum == goal->areanum" in obstacle_block
	assert "bs->predictobstacles_time > FloatTime() - 6" in obstacle_block
	assert "trap_AAS_PredictRoute(&route, bs->areanum, bs->origin," in obstacle_block
	assert "goal->areanum, bs->tfl, 100, 1000," in obstacle_block
	assert "RSE_USETRAVELTYPE|RSE_ENTERCONTENTS," in obstacle_block
	assert "AREACONTENTS_MOVER, TFL_BRIDGE, 0);" in obstacle_block
	assert "modelnum = (route.endcontents & AREACONTENTS_MODELNUM) >> AREACONTENTS_MODELNUMSHIFT;" in obstacle_block
	assert "entitynum = BotModelMinsMaxs(modelnum, ET_MOVER, 0, NULL, NULL);" in obstacle_block
	assert "bspent = BotGetActivateGoal(bs, entitynum, &activategoal);" in obstacle_block
	assert "BotGoForActivateGoal(bs, &activategoal);" in obstacle_block
	assert "BotEnableActivateGoalAreas(&activategoal, qtrue);" in obstacle_block

	assert "route->stopevent = RSE_NONE;" in predict_route_block
	assert "route->endarea = goalareanum;" in predict_route_block
	assert "route->endcontents = 0;" in predict_route_block
	assert "route->endtravelflags = 0;" in predict_route_block
	assert "route->time = 0;" in predict_route_block
	assert "route->numareas" not in predict_route_block

	assert "1001dcf0    void sub_1001dcf0(void* arg1, void* arg2)" in qagame_hlil
	assert "data_105e43cc != 0" in qagame_hlil
	assert "fconvert.t(6.0)" in qagame_hlil
	assert "(*(data_104b13ac + 0x13c))(&var_134" in qagame_hlil
	assert "0x64, 0x3e8, 6, 0x400, 0x4000000, 0)" in qagame_hlil
	assert "(var_124 & 4) != 0 && (var_120 & 0x400) != 0" in qagame_hlil
	assert "sub_1001cd40(eax_7, &var_110, arg1, ecx_2)" in qagame_hlil
	assert "sub_1001d6d0(arg1, &var_110)" in qagame_hlil
	assert "sub_1001cc60(1)" in qagame_hlil
	assert qagame_ghidra.count("FUN_1001dcf0(") >= 4

	assert "FUN_00494870,00494870,830,0,unknown" in ql_steam_functions
	assert "00494884  esi[3] = ecx" in ql_steam_hlil
	assert "0049488a  esi[4] = 0" in ql_steam_hlil
	assert "0049488d  esi[5] = 0" in ql_steam_hlil
	assert "00494890  esi[6] = 0" in ql_steam_hlil
	assert "004948a0  esi[8] = 0" in ql_steam_hlil


def test_qagame_bot_ai_aliases_cover_recent_botlib_mapping_round() -> None:
	ai_dmq3 = GAME_AI_DMQ3.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART01.read_text(encoding="utf-8")
	qagame_ghidra = QAGAME_GHIDRA_TOP.read_text(encoding="utf-8")
	qagame_symbols = json.loads(QAGAME_SYMBOL_MAP.read_text(encoding="utf-8"))
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))
	qagame_aliases = aliases["qagamex86"]

	expected_aliases = {
		"1000c6e0": "AINode_Seek_NBG",
		"1000cbe0": "AINode_Seek_LTG",
		"1000d2f0": "AINode_Battle_Fight",
		"1000d910": "AINode_Battle_Chase",
		"1000dfb0": "AINode_Battle_Retreat",
		"1000e700": "AINode_Battle_NBG",
		"1001bcd0": "BotFuncButtonActivateGoal",
		"1001c5b0": "BotFuncDoorActivateGoal",
		"1001c720": "BotTriggerMultipleActivateGoal",
		"1001c940": "BotPopFromActivateGoalStack",
		"1001c9e0": "BotPushOntoActivateGoalStack",
		"1001cbb0": "BotClearActivateGoalStack",
		"1001cc60": "BotEnableActivateGoalAreas",
		"1001ccc0": "BotIsGoingToActivateEntity",
		"1001cd40": "BotGetActivateGoal",
		"1001d6d0": "BotGoForActivateGoal",
		"1001d810": "BotRandomMove",
		"1001d960": "BotAIBlocked",
		"1001dcf0": "BotAIPredictObstacles",
		"1001e400": "BotCheckForProxMines",
		"1001e4c0": "BotCheckEvents",
		"1001eaf0": "BotCheckSnapshot",
		"10008460": "BotRecordNodeSwitch",
		"10022c60": "BotResetState",
		"10022ee0": "BotPublishDebugInfoString",
		"10023400": "BotAIStartFrame",
	}
	for address, name in expected_aliases.items():
		assert qagame_aliases[f"FUN_{address}"] == name
		assert qagame_aliases[f"sub_{address}"] == name

	normalized_names = {function["normalized_name"] for function in qagame_symbols["functions"]}
	assert "BotCheckForGrenades" not in normalized_names
	assert "BotPrintActivateGoalInfo" not in normalized_names

	activate_entry = next(function for function in qagame_symbols["functions"] if function["address"] == "0x1001CD40")
	assert activate_entry["normalized_name"] == "BotGetActivateGoal"
	assert "first-byte classname guard" in activate_entry["comment"]

	activate_block = _extract_function_block(
		ai_dmq3,
		"int BotGetActivateGoal(bot_state_t *bs, int entitynum, bot_activategoal_t *activategoal)",
	)
	assert 'trap_AAS_ValueForBSPEpairKey(ent, "classname", classname, sizeof(classname));' in activate_block
	assert "if (!*classname)" in activate_block
	assert "if (!classname)" not in activate_block
	assert 'if (!trap_AAS_ValueForBSPEpairKey(ent, "classname", classname, sizeof(classname)))' in activate_block

	random_entry = next(function for function in qagame_symbols["functions"] if function["address"] == "0x1001D810")
	assert random_entry["raw_name"] == "FUN_1001d810"
	assert random_entry["normalized_name"] == "BotRandomMove"
	assert random_entry["signature"] == "void BotRandomMove(bot_state_t *bs, bot_moveresult_t *moveresult)"
	assert "RESULTTYPE_INSOLIDAREA" in random_entry["comment"]
	assert "botlib import offset +0x2a0" in random_entry["comment"]
	assert "do not preserve the GPL debug activate-goal speech strings" in random_entry["comment"]

	random_block = _extract_function_block(ai_dmq3, "void BotRandomMove(bot_state_t *bs, bot_moveresult_t *moveresult)")
	blocked_block = _extract_function_block(ai_dmq3, "void BotAIBlocked(bot_state_t *bs, bot_moveresult_t *moveresult, int activate)")
	assert "angles[1] = random() * 360;" in random_block
	assert "AngleVectors(angles, dir, NULL, NULL);" in random_block
	assert "trap_BotMoveInDirection(bs->ms, dir, 400, MOVE_WALK);" in random_block
	assert "moveresult->failure = qfalse;" in random_block
	assert "VectorCopy(dir, moveresult->movedir);" in random_block
	assert "moveresult->type == RESULTTYPE_INSOLIDAREA" in blocked_block
	assert "BotRandomMove(bs, moveresult);" in blocked_block

	snapshot_entry = next(function for function in qagame_symbols["functions"] if function["normalized_name"] == "BotCheckSnapshot")
	assert "inlined grenade avoidance" in snapshot_entry["comment"]
	assert "BotCheckEvents" in snapshot_entry["comment"]
	assert "BotCheckForProxMines" in snapshot_entry["comment"]

	snapshot_block = _extract_function_block(ai_dmq3, "void BotCheckSnapshot(bot_state_t *bs)")
	assert "void BotCheckForGrenades(" not in ai_dmq3
	assert "BotCheckForGrenades(bs, &state);" not in snapshot_block
	assert "BotCheckEvents(bs, &state);" in snapshot_block
	assert "state.eType == ET_MISSILE && state.weapon == WP_GRENADE_LAUNCHER" in snapshot_block
	assert "trap_BotAddAvoidSpot(bs->ms, state.pos.trBase, 160, AVOID_ALWAYS);" in snapshot_block
	assert "BotCheckForProxMines(bs, &state);" in snapshot_block
	assert "BotCheckForKamikazeBody(bs, &state);" in snapshot_block
	assert snapshot_block.index("trap_BotAddAvoidSpot(bs->ms, vec3_origin, 0, AVOID_CLEAR);") < snapshot_block.index(
		"while( ( ent = BotAI_GetSnapshotEntity( bs->client, ent, &state ) ) != -1 ) {"
	)
	assert snapshot_block.index("while( ( ent = BotAI_GetSnapshotEntity( bs->client, ent, &state ) ) != -1 ) {") < snapshot_block.index(
		"BotCheckEvents(bs, &state);"
	)
	assert snapshot_block.index("BotCheckEvents(bs, &state);") < snapshot_block.index(
		"state.eType == ET_MISSILE && state.weapon == WP_GRENADE_LAUNCHER"
	)
	assert snapshot_block.index("trap_BotAddAvoidSpot(bs->ms, state.pos.trBase, 160, AVOID_ALWAYS);") < snapshot_block.index(
		"BotCheckForProxMines(bs, &state);"
	)
	assert snapshot_block.index("BotCheckForProxMines(bs, &state);") < snapshot_block.index(
		"BotCheckForKamikazeBody(bs, &state);"
	)
	assert snapshot_block.index("BotCheckForKamikazeBody(bs, &state);") < snapshot_block.index(
		"BotAI_GetEntityState(bs->client, &state);"
	)

	assert "1001eaf0    int32_t* sub_1001eaf0(void* arg1)" in qagame_hlil
	assert "sub_1001e4c0(arg1, &var_f8)" in qagame_hlil
	assert "if (var_f4 == 3 && var_28 == 4)" in qagame_hlil
	assert "(*(data_104b13ac + 0x2c4))(*(arg1 + 0x195c), &var_e0," in qagame_hlil
	assert "fconvert.s(fconvert.t(160f)), 1)" in qagame_hlil
	assert "sub_1001e400(arg1, &var_f8)" in qagame_hlil
	assert '(*(data_104b13ac + 0x120))(ebp, "classname", &var_a88, 0x80)' in qagame_hlil
	assert "if (var_a88 != 0)" in qagame_hlil
	assert '(**(code **)(DAT_104b13ac + 0x120))(iVar3,"classname",abStack_a88,0x80);' in qagame_ghidra
	assert "if (abStack_a88[0] != 0)" in qagame_ghidra
	assert 'BotGetActivateGoal: entity with model %s has no classname\\n' in qagame_ghidra
	assert "1001d810    int32_t sub_1001d810(int32_t* arg1 @ esi, void* arg2 @ edi)" in qagame_hlil
	assert "rand() & 0x7fff" in qagame_hlil
	assert "(*(edx + 0x2a0))(ecx_1, &var_18, fconvert.s(fconvert.t(data_1008fe58)), 1)" in qagame_hlil
	assert "arg1[7] = fconvert.s(fconvert.t(var_18))" in qagame_hlil
	assert "arg1[8] = fconvert.s(fconvert.t(var_14))" in qagame_hlil
	assert "*arg1 = 0" in qagame_hlil
	assert "arg1[9] = xmm0_1" in qagame_hlil
	assert "if (esi[1] == 8)" in qagame_hlil
	assert "sub_1001d810(esi, ebx)" in qagame_hlil
	assert "I have to shoot at a %s" not in qagame_hlil
	assert "I have to activate a %s" not in qagame_hlil
	assert "I have to shoot at a %s" not in qagame_ghidra
	assert "I have to activate a %s" not in qagame_ghidra


def test_qagame_bot_inventory_keeps_hmg_out_of_retail_inventory_snapshot() -> None:
	ai_dmq3 = GAME_AI_DMQ3.read_text(encoding="utf-8")
	qagame_hlil = QAGAME_HLIL_PART01.read_text(encoding="utf-8")
	qagame_symbols = json.loads(QAGAME_SYMBOL_MAP.read_text(encoding="utf-8"))

	normalize_entry = next(function for function in qagame_symbols["functions"] if function["normalized_name"] == "BotNormalizeAmmoInventory")
	update_entry = next(function for function in qagame_symbols["functions"] if function["normalized_name"] == "BotUpdateInventory")
	assert normalize_entry["address"] == "0x100162D0"
	assert update_entry["address"] == "0x10016380"
	assert "INVENTORY_SHELLS` through `INVENTORY_BELT" in normalize_entry["comment"]

	normalize_block = _extract_function_block(ai_dmq3, "static void BotNormalizeAmmoInventory( bot_state_t *bs )")
	update_block = _extract_function_block(ai_dmq3, "void BotUpdateInventory(bot_state_t *bs)")

	assert "INVENTORY_SHELLS" in normalize_block
	assert "INVENTORY_BELT" in normalize_block
	assert "INVENTORY_HEAVYBULLETS" not in normalize_block
	assert "INVENTORY_HEAVYMACHINEGUN" not in update_block
	assert "WP_HEAVY_MACHINEGUN" not in update_block
	assert "INVENTORY_BELT" in update_block
	assert "BotNormalizeAmmoInventory( bs );" in update_block

	assert "100162d0    void __convention(\"regparm\") sub_100162d0(void* arg1)" in qagame_hlil
	assert "100162de  if (*(arg1 + 0x1380) == 0xffffffff)" in qagame_hlil
	assert "1001636a  if (*(arg1 + 0x13a8) == 0xffffffff)" in qagame_hlil
	assert "1001636c      *(arg1 + 0x13a8) = 0x3e7" in qagame_hlil
	assert "10016380    void* sub_10016380()" in qagame_hlil
	assert "10016452  *(result + 0x137c) = eax_1 u>> 0xd & 1" in qagame_hlil
	assert "10016476  *(result + 0x1380) = eax_4" in qagame_hlil
	assert "100164ee  *(result + 0x13a8) = *(result + 0x1c4)" in qagame_hlil
	assert "10016660  sub_100162d0(result)" in qagame_hlil


def test_botlib_source_keeps_goal_state_stack_and_avoid_helpers() -> None:
	goal_source = BOTLIB_AI_GOAL.read_text(encoding="utf-8")

	state_from_handle_block = _extract_function_block(goal_source, "bot_goalstate_t *BotGoalStateFromHandle(int handle)")
	push_block = _extract_function_block(goal_source, "void BotPushGoal(int goalstate, bot_goal_t *goal)")
	top_block = _extract_function_block(goal_source, "int BotGetTopGoal(int goalstate, bot_goal_t *goal)")
	second_block = _extract_function_block(goal_source, "int BotGetSecondGoal(int goalstate, bot_goal_t *goal)")
	reset_block = _extract_function_block(goal_source, "void BotResetGoalState(int goalstate)")
	avoid_time_block = _extract_function_block(goal_source, "float BotAvoidGoalTime(int goalstate, int number)")
	set_avoid_time_block = _extract_function_block(goal_source, "void BotSetAvoidGoalTime(int goalstate, int number, float avoidtime)")
	alloc_block = _extract_function_block(goal_source, "int BotAllocGoalState(int client)")
	free_block = _extract_function_block(goal_source, "void BotFreeGoalState(int handle)")

	assert 'botimport.Print(PRT_FATAL, "goal state handle %d out of range\\n", handle);' in state_from_handle_block
	assert 'botimport.Print(PRT_FATAL, "invalid goal state %d\\n", handle);' in state_from_handle_block
	assert 'botimport.Print(PRT_ERROR, "goal heap overflow\\n");' in push_block
	assert "gs->goalstacktop++;" in push_block
	assert "Com_Memcpy(&gs->goalstack[gs->goalstacktop], goal, sizeof(bot_goal_t));" in push_block
	assert "if (!gs->goalstacktop) return qfalse;" in top_block
	assert "Com_Memcpy(goal, &gs->goalstack[gs->goalstacktop], sizeof(bot_goal_t));" in top_block
	assert "if (gs->goalstacktop <= 1) return qfalse;" in second_block
	assert "Com_Memset(gs->goalstack, 0, MAX_GOALSTACK * sizeof(bot_goal_t));" in reset_block
	assert "BotResetAvoidGoals(goalstate);" in reset_block
	assert "return gs->avoidgoaltimes[i] - AAS_Time();" in avoid_time_block
	assert "BotAddToAvoidGoals(gs, number, avoidtime);" in set_avoid_time_block
	assert "botgoalstates[i] = GetClearedMemory(sizeof(bot_goalstate_t));" in alloc_block
	assert "botgoalstates[i]->client = client;" in alloc_block
	assert 'botimport.Print(PRT_FATAL, "invalid goal state handle %d\\n", handle);' in free_block
	assert "BotFreeItemWeights(handle);" in free_block
	assert "botgoalstates[handle] = NULL;" in free_block


def test_botlib_interface_still_exports_aas_and_goal_owners() -> None:
	interface_source = BOTLIB_INTERFACE.read_text(encoding="utf-8")

	assert "aas->AAS_PresenceTypeBoundingBox = AAS_PresenceTypeBoundingBox;" in interface_source
	assert "aas->AAS_AreaTravelTimeToGoalArea = AAS_AreaTravelTimeToGoalArea;" in interface_source
	assert "ai->BotResetGoalState = BotResetGoalState;" in interface_source
	assert "ai->BotResetAvoidGoals = BotResetAvoidGoals;" in interface_source
	assert "ai->BotPushGoal = BotPushGoal;" in interface_source
	assert "ai->BotAllocGoalState = BotAllocGoalState;" in interface_source
	assert "ai->BotFreeGoalState = BotFreeGoalState;" in interface_source
