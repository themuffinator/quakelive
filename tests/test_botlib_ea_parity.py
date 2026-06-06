from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_EA = REPO_ROOT / "src" / "code" / "botlib" / "be_ea.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
GAME_SYSCALLS_ASM = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.asm"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
QL_STEAM_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
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
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_DECOMPILE_TOP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


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


def test_botlib_ea_retail_function_map_and_export_slots_are_pinned() -> None:
	functions_csv = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]

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
		("4A7C80", "EA_Setup"),
		("4A7CA0", "EA_Shutdown"),
		("4A8060", "Init_EA_Export"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_004a78c0,004a78c0,33,0,unknown",
		"FUN_004a78f0,004a78f0,33,0,unknown",
		"FUN_004a7920,004a7920,28,0,unknown",
		"FUN_004a7940,004a7940,10,0,unknown",
		"FUN_004a7950,004a7950,24,0,unknown",
		"FUN_004a7970,004a7970,25,0,unknown",
		"FUN_004a7990,004a7990,28,0,unknown",
		"FUN_004a79b0,004a79b0,25,0,unknown",
		"FUN_004a79d0,004a79d0,25,0,unknown",
		"FUN_004a79f0,004a79f0,44,0,unknown",
		"FUN_004a7a20,004a7a20,48,0,unknown",
		"FUN_004a7a50,004a7a50,28,0,unknown",
		"FUN_004a7a70,004a7a70,28,0,unknown",
		"FUN_004a7a90,004a7a90,27,0,unknown",
		"FUN_004a7ab0,004a7ab0,25,0,unknown",
		"FUN_004a7ad0,004a7ad0,28,0,unknown",
		"FUN_004a7af0,004a7af0,28,0,unknown",
		"FUN_004a7b10,004a7b10,28,0,unknown",
		"FUN_004a7b30,004a7b30,28,0,unknown",
		"FUN_004a7b50,004a7b50,28,0,unknown",
		"FUN_004a7b70,004a7b70,105,0,unknown",
		"FUN_004a7be0,004a7be0,40,0,unknown",
		"FUN_004a7c10,004a7c10,40,0,unknown",
		"FUN_004a7c40,004a7c40,61,0,unknown",
		"FUN_004a7c80,004a7c80,31,0,unknown",
		"FUN_004a7ca0,004a7ca0,25,0,unknown",
		"FUN_004a8060,004a8060,175,0,unknown",
		"FUN_004d7980,004d7980,1,0,unknown",
	):
		assert row in functions_csv

	for expected in (
		"004a8060    void __convention(\"regparm\") sub_4a8060(int32_t (** arg1)())",
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
	):
		assert expected in hlil


def test_botlib_ea_input_source_shape_matches_retail_hlil() -> None:
	ea_source = _read(BOTLIB_EA)
	hlil = _read(QL_STEAM_HLIL_PART03)

	assert "#define MAX_USERMOVE\t\t\t\t400" in ea_source
	assert "#define ACTION_JUMPEDLASTFRAME\t\t0x10000000" in ea_source
	assert "bot_input_t *botinputs;" in ea_source

	assert 'botimport.BotClientCommand(client, va("say %s", str) );' in _extract_function_block(
		ea_source, "void EA_Say(int client, char *str)"
	)
	assert 'botimport.BotClientCommand(client, va("say_team %s", str));' in _extract_function_block(
		ea_source, "void EA_SayTeam(int client, char *str)"
	)
	assert "botimport.BotClientCommand(client, command);" in _extract_function_block(
		ea_source, "void EA_Command(int client, char *command)"
	)

	for signature, action in (
		("void EA_Gesture(int client)", "ACTION_GESTURE"),
		("void EA_Attack(int client)", "ACTION_ATTACK"),
		("void EA_Talk(int client)", "ACTION_TALK"),
		("void EA_Use(int client)", "ACTION_USE"),
		("void EA_Respawn(int client)", "ACTION_RESPAWN"),
		("void EA_Crouch(int client)", "ACTION_CROUCH"),
		("void EA_Walk(int client)", "ACTION_WALK"),
		("void EA_MoveUp(int client)", "ACTION_MOVEUP"),
		("void EA_MoveDown(int client)", "ACTION_MOVEDOWN"),
		("void EA_MoveForward(int client)", "ACTION_MOVEFORWARD"),
		("void EA_MoveBack(int client)", "ACTION_MOVEBACK"),
		("void EA_MoveLeft(int client)", "ACTION_MOVELEFT"),
		("void EA_MoveRight(int client)", "ACTION_MOVERIGHT"),
	):
		block = _extract_function_block(ea_source, signature)
		assert "bi = &botinputs[client];" in block
		assert f"bi->actionflags |= {action};" in block

	select_weapon = _extract_function_block(ea_source, "void EA_SelectWeapon(int client, int weapon)")
	assert "bi->weapon = weapon;" in select_weapon

	jump = _extract_function_block(ea_source, "void EA_Jump(int client)")
	assert "if (bi->actionflags & ACTION_JUMPEDLASTFRAME)" in jump
	assert "bi->actionflags &= ~ACTION_JUMP;" in jump
	assert "bi->actionflags |= ACTION_JUMP;" in jump

	delayed_jump = _extract_function_block(ea_source, "void EA_DelayedJump(int client)")
	assert "bi->actionflags &= ~ACTION_DELAYEDJUMP;" in delayed_jump
	assert "bi->actionflags |= ACTION_DELAYEDJUMP;" in delayed_jump

	move = _extract_function_block(ea_source, "void EA_Move(int client, vec3_t dir, float speed)")
	assert "VectorCopy(dir, bi->dir);" in move
	assert "if (speed > MAX_USERMOVE) speed = MAX_USERMOVE;" in move
	assert "else if (speed < -MAX_USERMOVE) speed = -MAX_USERMOVE;" in move
	assert "bi->speed = speed;" in move

	view = _extract_function_block(ea_source, "void EA_View(int client, vec3_t viewangles)")
	assert "VectorCopy(viewangles, bi->viewangles);" in view

	get_input = _extract_function_block(ea_source, "void EA_GetInput(int client, float thinktime, bot_input_t *input)")
	assert "bi->thinktime = thinktime;" in get_input
	assert "Com_Memcpy(input, bi, sizeof(bot_input_t));" in get_input

	reset = _extract_function_block(ea_source, "void EA_ResetInput(int client)")
	assert "bi->actionflags &= ~ACTION_JUMPEDLASTFRAME;" in reset
	assert "bi->thinktime = 0;" in reset
	assert "VectorClear(bi->dir);" in reset
	assert "bi->speed = 0;" in reset
	assert "jumped = bi->actionflags & ACTION_JUMP;" in reset
	assert "bi->actionflags = 0;" in reset
	assert "if (jumped) bi->actionflags |= ACTION_JUMPEDLASTFRAME;" in reset

	setup = _extract_function_block(ea_source, "int EA_Setup(void)")
	assert "botlibglobals.maxclients * sizeof(bot_input_t)" in setup
	assert "return BLERR_NOERROR;" in setup

	shutdown = _extract_function_block(ea_source, "void EA_Shutdown(void)")
	assert "FreeMemory(botinputs);" in shutdown
	assert "botinputs = NULL;" in shutdown

	for expected in (
		'004a78e0  return data_16dd81c(arg1, sub_4d9220("say %s"))',
		'004a7910  return data_16dd81c(arg1, sub_4d9220("say_team %s"))',
		"004a7944  jump(data_16dd81c)",
		"004a792f  *(ecx + (eax_1 << 3) + 0x20) |= 0x20000",
		"004a7962  *(data_16ddaa4 + (result << 3) + 0x24) = arg2",
		"004a797f  *(ecx + (eax_1 << 3) + 0x20) |= 1",
		"004a799f  *(ecx + (eax_1 << 3) + 0x20) |= 0x10000",
		"004a79bf  *(ecx + (eax_1 << 3) + 0x20) |= 2",
		"004a79df  *(ecx + (eax_1 << 3) + 0x20) |= 8",
		"004a7a0a  if ((eax_2 & 0x10000000) != 0)",
		"004a7a14  int32_t eax_4 = eax_2 | 0x10",
		"004a7a3a  if ((eax_2 & 0x10000000) != 0)",
		"004a7a46  int32_t eax_4 = eax_2 | 0x8000",
		"004a7a5f  *(ecx + (eax_1 << 3) + 0x20) |= 0x80",
		"004a7a7f  *(ecx + (eax_1 << 3) + 0x20) |= 0x80000",
		"004a7aa2  *(ecx + (eax_1 << 3) + 0x20) |= arg2",
		"004a7abf  *(ecx + (eax_1 << 3) + 0x20) |= 0x20",
		"004a7adf  *(ecx + (eax_1 << 3) + 0x20) |= 0x100",
		"004a7aff  *(ecx + (eax_1 << 3) + 0x20) |= 0x200",
		"004a7b1f  *(ecx + (eax_1 << 3) + 0x20) |= 0x800",
		"004a7b3f  *(ecx + (eax_1 << 3) + 0x20) |= 0x1000",
		"004a7b5f  *(ecx + (eax_1 << 3) + 0x20) |= 0x2000",
		"004a7b7f  void* ecx_1 = data_16ddaa4 + arg1 * 0x28",
		"004a7bb4      *(ecx_1 + 0x10) = fconvert.s(fconvert.t(fconvert.s(fconvert.t(400f))))",
		"004a7bd1      x87_r7_3 = fconvert.t(fconvert.s(fconvert.t(-400f)))",
		"004a7bf7  *(result + 0x14) = fconvert.s(fconvert.t(*arg2))",
		"004a7c2a  *eax_2 = fconvert.s(fconvert.t(arg2))",
		"004a7c37  return sub_4cb7d0(arg3, eax_2, 0x28)",
		"004a7c51  int32_t edx = *(ecx + (eax_1 << 3) + 0x20)",
		"004a7c65  *(result + 0x20) = 0",
		"004a7c72  if ((edx & 0x10) != 0)",
		"004a7c74      *(result + 0x20) = 0x10000000",
		"004a7c94  data_16ddaa4 = sub_4a8a50(data_16dda98 * 0x28)",
		"004a7ca6  int32_t* result = sub_4a8aa0(data_16ddaa4)",
		"004a7cae  data_16ddaa4 = 0",
	):
		assert expected in hlil


def test_botlib_ea_struct_and_engine_wiring_match_public_call_surface() -> None:
	interface_source = _read(BOTLIB_INTERFACE)
	botlib_public = _read(BOTLIB_PUBLIC)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	game_syscalls_asm = _read(GAME_SYSCALLS_ASM)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(SERVER_QL_GAME_IMPORTS)
	ai_main = _read(GAME_AI_MAIN)

	init_ea = _extract_function_block(interface_source, "static void Init_EA_Export( ea_export_t *ea )")
	for assignment in (
		"ea->EA_Command = EA_Command;",
		"ea->EA_Say = EA_Say;",
		"ea->EA_SayTeam = EA_SayTeam;",
		"ea->EA_Action = EA_Action;",
		"ea->EA_Walk = EA_Walk;",
		"ea->EA_Gesture = EA_Gesture;",
		"ea->EA_Talk = EA_Talk;",
		"ea->EA_Attack = EA_Attack;",
		"ea->EA_Use = EA_Use;",
		"ea->EA_Respawn = EA_Respawn;",
		"ea->EA_Crouch = EA_Crouch;",
		"ea->EA_MoveUp = EA_MoveUp;",
		"ea->EA_MoveDown = EA_MoveDown;",
		"ea->EA_MoveForward = EA_MoveForward;",
		"ea->EA_MoveBack = EA_MoveBack;",
		"ea->EA_MoveLeft = EA_MoveLeft;",
		"ea->EA_MoveRight = EA_MoveRight;",
		"ea->EA_SelectWeapon = EA_SelectWeapon;",
		"ea->EA_Jump = EA_Jump;",
		"ea->EA_DelayedJump = EA_DelayedJump;",
		"ea->EA_Move = EA_Move;",
		"ea->EA_View = EA_View;",
		"ea->EA_EndRegular = EA_EndRegular;",
		"ea->EA_GetInput = EA_GetInput;",
		"ea->EA_ResetInput = EA_ResetInput;",
	):
		assert assignment in init_ea

	bot_input = botlib_public[
		botlib_public.index("typedef struct bot_input_s") : botlib_public.index("} bot_input_t;") + len("} bot_input_t;")
	]
	for field in (
		"float thinktime;",
		"vec3_t dir;",
		"float speed;",
		"vec3_t viewangles;",
		"int actionflags;",
		"int weapon;",
	):
		assert field in bot_input

	ea_export = botlib_public[
		botlib_public.index("typedef struct ea_export_s") : botlib_public.index("} ea_export_t;") + len("} ea_export_t;")
	]
	for prototype in (
		"void\t(*EA_Command)(int client, char *command );",
		"void\t(*EA_Say)(int client, char *str);",
		"void\t(*EA_SayTeam)(int client, char *str);",
		"void\t(*EA_Action)(int client, int action);",
		"void\t(*EA_Crouch)(int client);",
		"void\t(*EA_SelectWeapon)(int client, int weapon);",
		"void\t(*EA_Jump)(int client);",
		"void\t(*EA_DelayedJump)(int client);",
		"void\t(*EA_Move)(int client, vec3_t dir, float speed);",
		"void\t(*EA_View)(int client, vec3_t viewangles);",
		"void\t(*EA_EndRegular)(int client, float thinktime);",
		"void\t(*EA_GetInput)(int client, float thinktime, bot_input_t *input);",
		"void\t(*EA_ResetInput)(int client);",
	):
		assert prototype in ea_export

	for syscall_id in (
		"BOTLIB_EA_SAY = 400,",
		"BOTLIB_EA_END_REGULAR,",
		"BOTLIB_EA_GET_INPUT,",
		"BOTLIB_EA_RESET_INPUT,",
		"G_QL_IMPORT_BOTLIB_EA_SAY = 85,",
		"G_QL_IMPORT_BOTLIB_EA_END_REGULAR = 107,",
		"G_QL_IMPORT_BOTLIB_EA_GET_INPUT = 108,",
		"G_QL_IMPORT_BOTLIB_EA_RESET_INPUT = 109,",
	):
		assert syscall_id in game_public

	for mapped_import in (
		"case BOTLIB_EA_SAY: return G_QL_IMPORT_BOTLIB_EA_SAY;",
		"case BOTLIB_EA_END_REGULAR: return G_QL_IMPORT_BOTLIB_EA_END_REGULAR;",
		"case BOTLIB_EA_GET_INPUT: return G_QL_IMPORT_BOTLIB_EA_GET_INPUT;",
		"case BOTLIB_EA_RESET_INPUT: return G_QL_IMPORT_BOTLIB_EA_RESET_INPUT;",
	):
		assert mapped_import in game_syscalls

	for vm_asm_id in (
		"equ trap_EA_Say\t\t\t\t\t\t\t-401",
		"equ trap_EA_Command\t\t\t\t\t\t-403",
		"equ trap_EA_Move\t\t\t\t\t\t-420",
		"equ trap_EA_View\t\t\t\t\t\t-421",
		"equ trap_EA_EndRegular\t\t\t\t\t-422",
		"equ trap_EA_GetInput\t\t\t\t\t-423",
		"equ trap_EA_ResetInput\t\t\t\t\t-424",
	):
		assert vm_asm_id in game_syscalls_asm

	for server_dispatch in (
		"botlib_export->ea.EA_Say( args[1], VMA(2) );",
		"botlib_export->ea.EA_EndRegular( args[1], VMF(2) );",
		"botlib_export->ea.EA_GetInput( args[1], VMF(2), VMA(3) );",
		"botlib_export->ea.EA_ResetInput( args[1] );",
		"[BOTLIB_EA_END_REGULAR] = (ql_import_f)QL_G_trap_EA_EndRegular,",
		"[BOTLIB_EA_GET_INPUT] = (ql_import_f)QL_G_trap_EA_GetInput,",
		"[BOTLIB_EA_RESET_INPUT] = (ql_import_f)QL_G_trap_EA_ResetInput,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_END_REGULAR] = (ql_import_f)QL_G_trap_EA_EndRegular;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_GET_INPUT] = (ql_import_f)QL_G_trap_EA_GetInput;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_RESET_INPUT] = (ql_import_f)QL_G_trap_EA_ResetInput;",
	):
		assert server_dispatch in server_game

	for native_trap in (
		"G_Import_Syscall( BOTLIB_EA_SAY, client, str );",
		"G_Import_Syscall( BOTLIB_EA_MOVE, client, dir, QL_G_PASSFLOAT(speed) );",
		"G_Import_Syscall( BOTLIB_EA_END_REGULAR, client, QL_G_PASSFLOAT(thinktime) );",
		"G_Import_Syscall( BOTLIB_EA_GET_INPUT, client, QL_G_PASSFLOAT(thinktime), input );",
		"G_Import_Syscall( BOTLIB_EA_RESET_INPUT, client );",
	):
		assert native_trap in ql_game_imports

	input_to_cmd = _extract_function_block(
		ai_main, "void BotInputToUserCommand(bot_input_t *bi, usercmd_t *ucmd, int delta_angles[3], int time)"
	)
	assert "if (bi->actionflags & ACTION_DELAYEDJUMP)" in input_to_cmd
	assert "ucmd->weapon = bi->weapon;" in input_to_cmd
	assert "ucmd->angles[PITCH] = ANGLE2SHORT(bi->viewangles[PITCH]);" in input_to_cmd
	assert "bi->speed = bi->speed * 127 / 400;" in input_to_cmd
	assert "if (bi->actionflags & ACTION_JUMP) ucmd->upmove += 127;" in input_to_cmd
	assert "if (bi->actionflags & ACTION_CROUCH) ucmd->upmove -= 127;" in input_to_cmd

	update_input = _extract_function_block(ai_main, "void BotUpdateInput(bot_state_t *bs, int time, int elapsed_time)")
	assert "trap_EA_GetInput(bs->client, (float) time / 1000, &bi);" in update_input
	assert "BotInputToUserCommand(&bi, &bs->lastucmd, bs->cur_ps.delta_angles, time);" in update_input


def test_botlib_ea_qagame_consumer_reference_shape_is_mapped() -> None:
	qagame_symbols = json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	qagame_functions = _read(QAGAME_FUNCTIONS)
	qagame_decomp = _read(QAGAME_DECOMPILE_TOP)

	qagame_by_name = {
		entry["normalized_name"]: entry
		for entry in qagame_symbols
		if entry.get("normalized_name") in {"BotChangeViewAngles", "BotInputToUserCommand", "BotUpdateInput"}
	}

	assert qagame_by_name["BotChangeViewAngles"]["address"] == "0x10021740"
	assert qagame_by_name["BotChangeViewAngles"]["status"] == "matched"
	assert "trap_EA_View" in qagame_by_name["BotChangeViewAngles"]["comment"]

	assert qagame_by_name["BotInputToUserCommand"]["address"] == "0x10021B20"
	assert qagame_by_name["BotInputToUserCommand"]["signature"] == (
		"void BotInputToUserCommand(bot_input_t *bi, usercmd_t *ucmd, int delta_angles[3], int time)"
	)
	assert "ACTION_*" in qagame_by_name["BotInputToUserCommand"]["comment"]
	assert "weapon-selection handoff" in qagame_by_name["BotInputToUserCommand"]["comment"]

	assert qagame_by_name["BotUpdateInput"]["address"] == "0x10021E10"
	assert qagame_by_name["BotUpdateInput"]["status"] == "matched"
	assert "trap_EA_GetInput" in qagame_by_name["BotUpdateInput"]["comment"]

	for row in (
		"FUN_10021740,10021740,980,0,unknown",
		"FUN_10021b20,10021b20,741,0,unknown",
		"FUN_10021e10,10021e10,372,0,unknown",
	):
		assert row in qagame_functions

	for evidence in (
		"/* FUN_10021b20 @ 10021b20 size 741 */",
		"void FUN_10021b20(int param_1,undefined4 *param_2,undefined4 param_3,float param_4,int param_5)",
		"param_2[1] = 0;",
		"*param_2 = param_3;",
		"if ((*(uint *)(param_1 + 0x20) & 0x8000) != 0) {",
		"*(uint *)(param_1 + 0x20) = *(uint *)(param_1 + 0x20) & 0xffff7fff | 0x10;",
		"if ((*(byte *)(param_1 + 0x20) & 8) != 0) {",
		"param_2[4] = 1;",
		"if ((*(uint *)(param_1 + 0x20) & 0x20000) != 0) {",
		"param_2[4] = param_2[4] | 8;",
		"if ((*(uint *)(param_1 + 0x20) & 0x80000) != 0) {",
		"param_2[4] = param_2[4] | 0x10;",
		"*(undefined1 *)(param_2 + 5) = *(undefined1 *)(param_1 + 0x24);",
		"*(float *)(param_1 + 0x10) =",
		"(*(float *)(param_1 + 0x10) * (float)_DAT_1008b1b8) / (float)_DAT_1008b170;",
		"if ((*(uint *)(param_1 + 0x20) & 0x200) != 0) {",
		"*(char *)((int)param_2 + 0x17) = *(char *)((int)param_2 + 0x17) + '\\x7f';",
		"if (((*(byte *)(param_1 + 0x20) & 0x80) != 0) && (param_5 != 0x3ff)) {",
		"*(char *)((int)param_2 + 0x19) = *(char *)((int)param_2 + 0x19) + -0x7f;",
		"FUN_10021e10(param_1,iStack_e4);",
	):
		assert evidence in qagame_decomp
