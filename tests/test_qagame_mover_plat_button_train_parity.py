from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_MOVER = REPO_ROOT / "src" / "code" / "game" / "g_mover.c"
GAME_SPAWN = REPO_ROOT / "src" / "code" / "game" / "g_spawn.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)


MOVER_PLAT_BUTTON_TRAIN_FUNCTIONS = (
	{
		"address": "0x1005FD60",
		"aliases": ("FUN_1005fd60", "sub_1005fd60"),
		"normalized": "Touch_Plat",
		"signature": "void Touch_Plat(gentity_t *ent, gentity_t *other, trace_t *trace)",
		"ghidra": None,
	},
	{
		"address": "0x1005FDA0",
		"aliases": ("FUN_1005fda0", "sub_1005fda0"),
		"normalized": "Touch_PlatCenterTrigger",
		"signature": "void Touch_PlatCenterTrigger(gentity_t *ent, gentity_t *other, trace_t *trace)",
		"ghidra": None,
	},
	{
		"address": "0x1005FDD0",
		"aliases": ("FUN_1005fdd0", "sub_1005fdd0"),
		"normalized": "SpawnPlatTrigger",
		"signature": "void SpawnPlatTrigger(gentity_t *ent)",
		"ghidra": ("1005fdd0", "FUN_1005fdd0", 448),
	},
	{
		"address": "0x1005FF90",
		"aliases": ("FUN_1005ff90", "sub_1005ff90"),
		"normalized": "SP_func_plat",
		"signature": "void SP_func_plat(gentity_t *ent)",
		"ghidra": None,
	},
	{
		"address": "0x10060160",
		"aliases": ("FUN_10060160", "sub_10060160"),
		"normalized": "Touch_ButtonKeyed",
		"signature": "void Touch_ButtonKeyed(gentity_t *ent, gentity_t *other, trace_t *trace)",
		"ghidra": ("10060160", "FUN_10060160", 82),
	},
	{
		"address": "0x100601C0",
		"aliases": ("FUN_100601c0", "sub_100601c0"),
		"normalized": "Touch_Button",
		"signature": "void Touch_Button(gentity_t *ent, gentity_t *other, trace_t *trace)",
		"ghidra": None,
	},
	{
		"address": "0x100601F0",
		"aliases": ("FUN_100601f0", "sub_100601f0"),
		"normalized": "SP_func_button",
		"signature": "void SP_func_button(gentity_t *ent)",
		"ghidra": ("100601f0", "FUN_100601f0", 513),
	},
	{
		"address": "0x10060400",
		"aliases": ("FUN_10060400", "sub_10060400"),
		"normalized": "Think_BeginMoving",
		"signature": "void Think_BeginMoving(gentity_t *ent)",
		"ghidra": None,
	},
	{
		"address": "0x10060420",
		"aliases": ("FUN_10060420", "sub_10060420"),
		"normalized": "Reached_Train",
		"signature": "void Reached_Train(gentity_t *ent)",
		"ghidra": ("10060420", "FUN_10060420", 603),
	},
	{
		"address": "0x10060680",
		"aliases": ("FUN_10060680", "sub_10060680"),
		"normalized": "Think_SetupTrainTargets",
		"signature": "void Think_SetupTrainTargets(gentity_t *ent)",
		"ghidra": ("10060680", "FUN_10060680", 452),
	},
	{
		"address": "0x10060850",
		"aliases": ("FUN_10060850", "sub_10060850"),
		"normalized": "SP_path_corner",
		"signature": "void SP_path_corner(gentity_t *ent)",
		"ghidra": ("10060850", "FUN_10060850", 179),
	},
	{
		"address": "0x10060910",
		"aliases": ("FUN_10060910", "sub_10060910"),
		"normalized": "SP_func_train",
		"signature": "void SP_func_train(gentity_t *ent)",
		"ghidra": ("10060910", "FUN_10060910", 393),
	},
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str) -> str:
	scan_text = "\n".join(line.split("//", 1)[0] for line in text.splitlines())
	start = scan_text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = scan_text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(scan_text)):
		char = scan_text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return scan_text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _function_rows_by_entry(path: Path) -> dict[str, dict[str, str]]:
	with path.open(newline="", encoding="utf-8") as file:
		return {row["entry"].lower(): row for row in csv.DictReader(file)}


def test_qagame_mover_aliases_metadata_and_hlil_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	hlil = _read(QAGAME_HLIL_PART02)

	for function in MOVER_PLAT_BUTTON_TRAIN_FUNCTIONS:
		for raw_name in function["aliases"]:
			assert aliases[raw_name] == function["normalized"]

		symbol = symbol_map[function["address"].lower()]
		assert symbol["normalized_name"] == function["normalized"]
		assert symbol["signature"] == function["signature"]
		assert symbol["status"] == "matched"

		if function["ghidra"]:
			entry, raw_name, size = function["ghidra"]
			row = function_rows[entry]
			assert row["name"] == raw_name
			assert int(row["size"]) == size
			assert row["thunk"] == "0"

	for expected in (
		"1005fd60    int32_t sub_1005fd60(void* arg1, void* arg2)",
		"1005fd83  if (result != 0 && *(result + 0xc0) s> 0 && *(arg1 + 0x278) == 1)",
		"1005fd96      *(arg1 + 0x2f4) = result",
		"1005fda0    void sub_1005fda0(void* arg1, void* arg2)",
		"1005fdbe      if (*(eax + 0x278) == 0)",
		"1005fdc3          st0_1, eax = sub_1005ec00(eax, arg1)",
		"1005fdd0    int32_t sub_1005fdd0(void* arg1 @ esi)",
		"1005fdda  *(eax + 0x244) = \"plat_trigger\"",
		"1005fde4  *(eax + 0x308) = sub_1005fda0",
		"1005fdee  *(eax + 0x204) = 0x40000000",
		"1005fe1e  long double x87_r4_1 = fconvert.t(33.0)",
		"1005feb8  float var_4 = fconvert.s(x87_r1_1 + fconvert.t(*(arg1 + 0x200)) + fconvert.t(8.0))",
		"1005ff8f  return (*(eax_1 + 0x9c))(eax, var_20_1, var_1c_4, var_18, var_14, var_10, var_c, var_8,",
		"1005ff90    int32_t sub_1005ff90(long double arg1 @ st0, long double arg2 @ st1)",
		"1005ff9e  int32_t eax = sub_1006be90(\"sound/movers/plats/pt1_strt.wav\")",
		"1005ffb8  int32_t eax_1 = sub_1006be90(\"sound/movers/plats/pt1_end.wav\")",
		"10060013  sub_10065c00(\"speed\", &data_1007dfe0, &arg_4)",
		"10060038  sub_10065c00(&data_10088260, &data_1007d53c, &arg_4)",
		"100600a2  int32_t eax_5 = sub_10065c00(\"height\", &data_1007d0a8, &arg_4)",
		"1006012d  *(esi i+ 0x308) = sub_1005fd60",
		"10060149  return sub_1005fdd0(esi)",
		"10060160    void sub_10060160(void* arg1, void* arg2)",
		"1006018d          if ((*(arg1 + 0x248) & 0x10) != 0 && (*(ecx + 0xfc) & 5) != 0)",
		"1006018d          else if (eax == 0 && (*(arg1 + 0x248) & 0x20) != 0 && (*(ecx + 0xfc) & 6) != 0)",
		"100601c0    void* sub_100601c0(void* arg1, void* arg2)",
		"100601d8  if (*(result + 0x23c) != 0 && *(arg1 + 0x278) == 0)",
		"100601f0    int32_t sub_100601f0(long double arg1 @ st0, void* arg2)",
		"10060206  int32_t eax = sub_1006be90(\"sound/movers/switches/butn2.wav\")",
		"10060273  *(arg2 + 0x370) = fconvert.s(fconvert.t(*(arg2 + 0x370)) * fconvert.t(1000.0))",
		"100602c8  sub_1006c1a0(arg2 + 0x2e8, atof(var_28), arg2 + 0x7c)",
		"100603db      *(arg2 + 0x308) = sub_10060160",
		"100603c5  *(arg2 + 0x308) = sub_100601c0",
		"10060400    void* sub_10060400(void* arg1)",
		"1006040a  *(arg1 + 0x10) = data_105dce5c",
		"1006040d  *(arg1 + 0xc) = 3",
		"10060420    void sub_10060420(float arg1)",
		"10060440  if (ebp != 0 && *(ebp + 0x294) != 0)",
		"10060449      sub_1006c0d0(ebp, 0)",
		"10060593      *(ebx i+ 0x14) = eax_3",
		"100605a6      *(ebx i+ 0xa4) = *(ebp + 0x28c)",
		"10060663          *(ebx i+ 0x2f8) = sub_10060400",
		"10060680    int32_t sub_10060680(void* arg1)",
		"1006070c      return sub_10053140(\"func_train at %s with an unfound…\")",
		"1006074a          char const* const edx_1 = \"path_corner\"",
		"1006078b  st0, result = sub_10060420()",
		"100607ee          return sub_10053140(\"Train corner at %s without a tar…\")",
		"10060843              return sub_10053140(\"Train corner at %s without a tar…\")",
		"10060850    void sub_10060850(void* arg1)",
		"100608a9      char const* const var_ac_1 = \"path_corner with no targetname a…\"",
		"100608ae      sub_10053140(\"path_corner with no targetname a…\")",
		"100608da          *(arg1 + 0x244) = \"freed\"",
		"10060910    int32_t sub_10060910(void* arg1)",
		"1006094f      *(arg1 + 0x2e4) = 0x42c80000",
		"100609ab      char const* const var_ac_1 = \"func_train without a target at %…\"",
		"100609b0      sub_10053140(\"func_train without a target at %…\")",
		"10060a60      *(arg1 + 0x300) = sub_10060420",
		"10060a89      *(arg1 + 0x2f8) = sub_10060680",
		"10080590  char const (* data_10080590)[0xa] = data_10089750 {\"func_plat\"}",
		"10080594  void* data_10080594 = sub_1005ff90",
		"10080598  char const (* data_10080598)[0xc] = data_1007d7e8 {\"func_button\"}",
		"1008059c  void* data_1008059c = sub_100601f0",
		"100805c8  char const (* data_100805c8)[0xb] = data_10088108 {\"func_train\"}",
		"100805cc  void* data_100805cc = sub_10060910",
		"10080688  char const (* data_10080688)[0xc] = data_1008836c {\"path_corner\"}",
		"1008068c  void* data_1008068c = sub_10060850",
	):
		assert expected in hlil


def test_qagame_plat_source_paths_match_retail() -> None:
	g_mover = _read(GAME_MOVER)
	touch_body = _extract_function_block(g_mover, "void Touch_Plat( gentity_t *ent, gentity_t *other, trace_t *trace )")
	center_body = _extract_function_block(g_mover, "void Touch_PlatCenterTrigger(gentity_t *ent, gentity_t *other, trace_t *trace )")
	trigger_body = _extract_function_block(g_mover, "void SpawnPlatTrigger( gentity_t *ent )")
	spawn_body = _extract_function_block(g_mover, "void SP_func_plat (gentity_t *ent)")

	for expected in (
		"if ( !other->client || other->client->ps.stats[STAT_HEALTH] <= 0 )",
		"if ( ent->moverState == MOVER_POS2 )",
		"ent->nextthink = level.time + 1000;",
	):
		assert expected in touch_body

	for expected in (
		"if ( !other->client )",
		"if ( ent->parent->moverState == MOVER_POS1 )",
		"Use_BinaryMover( ent->parent, ent, other );",
	):
		assert expected in center_body

	for expected in (
		"trigger = G_Spawn();",
		'trigger->classname = "plat_trigger";',
		"trigger->touch = Touch_PlatCenterTrigger;",
		"trigger->r.contents = CONTENTS_TRIGGER;",
		"trigger->parent = ent;",
		"tmin[0] = ent->pos1[0] + ent->r.mins[0] + 33;",
		"tmin[1] = ent->pos1[1] + ent->r.mins[1] + 33;",
		"tmin[2] = ent->pos1[2] + ent->r.mins[2];",
		"tmax[0] = ent->pos1[0] + ent->r.maxs[0] - 33;",
		"tmax[1] = ent->pos1[1] + ent->r.maxs[1] - 33;",
		"tmax[2] = ent->pos1[2] + ent->r.maxs[2] + 8;",
		"tmin[0] = ent->pos1[0] + (ent->r.mins[0] + ent->r.maxs[0]) *0.5;",
		"tmax[0] = tmin[0] + 1;",
		"tmin[1] = ent->pos1[1] + (ent->r.mins[1] + ent->r.maxs[1]) *0.5;",
		"tmax[1] = tmin[1] + 1;",
		"VectorCopy (tmin, trigger->r.mins);",
		"VectorCopy (tmax, trigger->r.maxs);",
		"trap_LinkEntity (trigger);",
	):
		assert expected in trigger_body

	for expected in (
		'ent->sound1to2 = ent->sound2to1 = G_SoundIndex("sound/movers/plats/pt1_strt.wav");',
		'ent->soundPos1 = ent->soundPos2 = G_SoundIndex("sound/movers/plats/pt1_end.wav");',
		"VectorClear (ent->s.angles);",
		'G_SpawnFloat( "speed", "200", &ent->speed );',
		'G_SpawnInt( "dmg", "2", &ent->damage );',
		'G_SpawnFloat( "wait", "1", &ent->wait );',
		'G_SpawnFloat( "lip", "8", &lip );',
		"ent->wait = 1000;",
		"trap_SetBrushModel( ent, ent->model );",
		'if ( !G_SpawnFloat( "height", "0", &height ) )',
		"height = (ent->r.maxs[2] - ent->r.mins[2]) - lip;",
		"VectorCopy( ent->s.origin, ent->pos2 );",
		"VectorCopy( ent->pos2, ent->pos1 );",
		"ent->pos1[2] -= height;",
		"InitMover( ent );",
		"ent->touch = Touch_Plat;",
		"ent->blocked = Blocked_Door;",
		"ent->parent = ent;",
		"if ( !ent->targetname )",
		"SpawnPlatTrigger(ent);",
	):
		assert expected in spawn_body


def test_qagame_button_source_paths_match_retail() -> None:
	g_mover = _read(GAME_MOVER)
	touch_body = _extract_function_block(g_mover, "void Touch_Button(gentity_t *ent, gentity_t *other, trace_t *trace )")
	keyed_body = _extract_function_block(g_mover, "static void Touch_ButtonKeyed( gentity_t *ent, gentity_t *other, trace_t *trace )")
	spawn_body = _extract_function_block(g_mover, "void SP_func_button( gentity_t *ent )")

	for expected in (
		"if ( !other->client )",
		"if ( ent->moverState == MOVER_POS1 )",
		"Use_BinaryMover( ent, other, other );",
	):
		assert expected in touch_body

	for expected in (
		"if ( !other->client )",
		"if ( ent->moverState != MOVER_POS1 )",
		"if ( ( ent->spawnflags & 16 ) && ( other->keyMask & ( KEY_FLAG_SILVER | KEY_FLAG_MASTER ) ) )",
		"Use_BinaryMover( ent, other, other );",
		"else if ( ( ent->spawnflags & 32 ) && ( other->keyMask & ( KEY_FLAG_GOLD | KEY_FLAG_MASTER ) ) )",
	):
		assert expected in keyed_body

	for expected in (
		'ent->sound1to2 = G_SoundIndex("sound/movers/switches/butn2.wav");',
		"ent->speed = 40;",
		"ent->wait = 1;",
		"ent->wait *= 1000;",
		"VectorCopy( ent->s.origin, ent->pos1 );",
		"trap_SetBrushModel( ent, ent->model );",
		'G_SpawnFloat( "lip", "4", &lip );',
		"G_SetMovedir( ent->s.angles, ent->movedir );",
		"abs_movedir[0] = fabs(ent->movedir[0]);",
		"VectorSubtract( ent->r.maxs, ent->r.mins, size );",
		"distance = abs_movedir[0] * size[0] + abs_movedir[1] * size[1] + abs_movedir[2] * size[2] - lip;",
		"VectorMA (ent->pos1, distance, ent->movedir, ent->pos2);",
		"if ( ent->spawnflags & ( 16 | 32 ) )",
		"ent->touch = Touch_ButtonKeyed;",
		"ent->takedamage = qtrue;",
		"ent->touch = Touch_Button;",
		"InitMover( ent );",
	):
		assert expected in spawn_body


def test_qagame_train_source_paths_and_spawn_order_match_retail() -> None:
	g_mover = _read(GAME_MOVER)
	g_spawn = _read(GAME_SPAWN)
	begin_body = _extract_function_block(g_mover, "void Think_BeginMoving( gentity_t *ent )")
	reached_body = _extract_function_block(g_mover, "void Reached_Train( gentity_t *ent )")
	setup_body = _extract_function_block(g_mover, "void Think_SetupTrainTargets( gentity_t *ent )")
	corner_body = _extract_function_block(g_mover, "void SP_path_corner( gentity_t *self )")
	train_body = _extract_function_block(g_mover, "void SP_func_train (gentity_t *self)")

	for expected in (
		"ent->s.pos.trTime = level.time;",
		"ent->s.pos.trType = TR_LINEAR_STOP;",
	):
		assert expected in begin_body

	for expected in (
		"next = ent->nextTrain;",
		"if ( !next || !next->nextTrain )",
		"G_UseTargets( next, NULL );",
		"ent->nextTrain = next->nextTrain;",
		"VectorCopy( next->s.origin, ent->pos1 );",
		"VectorCopy( next->nextTrain->s.origin, ent->pos2 );",
		"if ( next->speed )",
		"speed = next->speed;",
		"speed = ent->speed;",
		"if ( speed < 1 )",
		"speed = 1;",
		"VectorSubtract( ent->pos2, ent->pos1, move );",
		"length = VectorLength( move );",
		"ent->s.pos.trDuration = length * 1000 / speed;",
		"ent->s.loopSound = next->soundLoop;",
		"SetMoverState( ent, MOVER_1TO2, level.time );",
		"ent->nextthink = level.time + next->wait * 1000;",
		"ent->think = Think_BeginMoving;",
		"ent->s.pos.trType = TR_STATIONARY;",
	):
		assert expected in reached_body

	for expected in (
		"ent->nextTrain = G_Find( NULL, FOFS(targetname), ent->target );",
		'G_Printf( "func_train at %s with an unfound target\\n",',
		"start = NULL;",
		"for ( path = ent->nextTrain ; path != start ; path = next )",
		"start = path;",
		"if ( !path->target )",
		'G_Printf( "Train corner at %s without a target\\n",',
		"next = G_Find( next, FOFS(targetname), path->target );",
		'G_Printf( "Train corner at %s without a target path_corner\\n",',
		'while ( strcmp( next->classname, "path_corner" ) );',
		"path->nextTrain = next;",
		"Reached_Train( ent );",
	):
		assert expected in setup_body

	for expected in (
		"if ( !self->targetname )",
		'G_Printf ("path_corner with no targetname at %s\\n", vtos(self->s.origin));',
		"G_FreeEntity( self );",
	):
		assert expected in corner_body

	for expected in (
		"VectorClear (self->s.angles);",
		"if (self->spawnflags & TRAIN_BLOCK_STOPS)",
		"self->damage = 0;",
		"self->damage = 2;",
		"self->speed = 100;",
		"if ( !self->target )",
		'G_Printf ("func_train without a target at %s\\n", vtos(self->r.absmin));',
		"G_FreeEntity( self );",
		"trap_SetBrushModel( self, self->model );",
		"InitMover( self );",
		"self->reached = Reached_Train;",
		"self->nextthink = level.time + FRAMETIME;",
		"self->think = Think_SetupTrainTargets;",
	):
		assert expected in train_body

	expected_spawn_order = [
		'{"info_tour_point", SP_info_tour_point}',
		'{"func_plat", SP_func_plat}',
		'{"func_button", SP_func_button}',
		'{"func_door", SP_func_door}',
		'{"func_static", SP_func_static}',
		'{"func_rotating", SP_func_rotating}',
		'{"func_bobbing", SP_func_bobbing}',
		'{"func_pendulum", SP_func_pendulum}',
		'{"func_train", SP_func_train}',
		'{"func_group", SP_info_null}',
		'{"func_timer", SP_func_timer}',
		'{"path_corner", SP_path_corner}',
		'{"misc_teleporter_dest", SP_misc_teleporter_dest}',
	]
	positions = [g_spawn.index(entry) for entry in expected_spawn_order]
	assert positions == sorted(positions)
