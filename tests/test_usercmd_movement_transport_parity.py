from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

ALIASES_PATH = REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json"
HLIL_PART04_PATH = (
	REPO_ROOT
	/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt"
)
CL_INPUT_PATH = REPO_ROOT / "src/code/client/cl_input.c"
CL_CGAME_PATH = REPO_ROOT / "src/code/client/cl_cgame.c"
CG_SYSCALLS_PATH = REPO_ROOT / "src/code/cgame/cg_syscalls.c"
CG_PREDICT_PATH = REPO_ROOT / "src/code/cgame/cg_predict.c"
QL_CGAME_IMPORTS_PATH = REPO_ROOT / "src/code/client/ql_cgame_imports.inc"
MSG_PATH = REPO_ROOT / "src/code/qcommon/msg.c"
Q_SHARED_PATH = REPO_ROOT / "src/code/game/q_shared.h"
SV_CLIENT_PATH = REPO_ROOT / "src/code/server/sv_client.c"
SV_GAME_PATH = REPO_ROOT / "src/code/server/sv_game.c"
ROUND_17_PATH = REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_17.md"
ROUND_57_PATH = REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_57.md"
ROUND_62_PATH = REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_62.md"
ROUND_126_PATH = REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_126.md"
ROUND_277_PATH = REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_277.md"


def _function_block(source: str, signature: str) -> str:
	start = source.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = source.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	in_string = False
	escaped = False

	for index in range(brace_start, len(source)):
		char = source[index]

		if in_string:
			if escaped:
				escaped = False
			elif char == "\\":
				escaped = True
			elif char == '"':
				in_string = False
			continue

		if char == '"':
			in_string = True
		elif char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _assert_order(block: str, *needles: str) -> None:
	cursor = 0
	for needle in needles:
		index = block.find(needle, cursor)
		if index == -1:
			raise AssertionError(f"expected ordered snippet not found after {cursor}: {needle}")
		cursor = index + len(needle)


def test_client_creates_and_packs_retail_usercmd_stream_for_server_pmove() -> None:
	source = CL_INPUT_PATH.read_text(encoding="utf-8")
	finish_block = _function_block(source, "void CL_FinishMove( usercmd_t *cmd )")
	create_block = _function_block(source, "usercmd_t CL_CreateCmd( void )")
	create_new_block = _function_block(source, "void CL_CreateNewCommands( void )")
	ready_block = _function_block(source, "qboolean CL_ReadyToSendPacket( void )")
	write_block = _function_block(source, "void CL_WritePacket( void )")
	send_block = _function_block(source, "void CL_SendCmd( void )")

	_assert_order(
		finish_block,
		"cmd->weapon = cl.cgameUserCmdValue;",
		"cmd->weaponPrimary = cl.cgameUserCmdPrimary;",
		"cmd->fov = cl.cgameUserCmdFov;",
		"cmd->serverTime = cl.serverTime;",
		"cmd->angles[i] = ANGLE2SHORT(cl.viewangles[i]);",
	)

	_assert_order(
		create_block,
		"VectorCopy( cl.viewangles, oldAngles );",
		"CL_AdjustAngles ();",
		"Com_Memset( &cmd, 0, sizeof( cmd ) );",
		"CL_CmdButtons( &cmd );",
		"CL_KeyMove( &cmd );",
		"CL_MouseMove( &cmd );",
		"CL_JoystickMove( &cmd );",
		"CL_FinishMove( &cmd );",
		"return cmd;",
	)
	assert "cl.viewangles[PITCH] = oldAngles[PITCH] + 90;" in create_block
	assert "cl.viewangles[PITCH] = oldAngles[PITCH] - 90;" in create_block

	_assert_order(
		create_new_block,
		"if ( cls.state < CA_PRIMED ) {",
		"frame_msec = com_frameTime - old_com_frameTime;",
		"if ( frame_msec > 200 ) {",
		"old_com_frameTime = com_frameTime;",
		"cl.cmdNumber++;",
		"cmdNum = cl.cmdNumber & CMD_MASK;",
		"cl.cmds[cmdNum] = CL_CreateCmd ();",
	)

	for expected in (
		"if ( clc.demoplaying || cls.state == CA_CINEMATIC ) {",
		"cls.realtime - clc.lastPacketSentTime < 50",
		"cls.realtime - clc.lastPacketSentTime < 1000",
		"clc.netchan.remoteAddress.type == NA_LOOPBACK",
		"Sys_IsLANAddress( clc.netchan.remoteAddress )",
		'Cvar_Set( "cl_maxpackets", "15" );',
		'Cvar_Set( "cl_maxpackets", "125" );',
		"delta = cls.realtime -  cl.outPackets[ oldPacketNum ].p_realtime;",
		"delta < 1000 / cl_maxpackets->integer",
	):
		assert expected in ready_block

	_assert_order(
		write_block,
		"MSG_Bitstream( &buf );",
		"MSG_WriteLong( &buf, cl.serverId );",
		"MSG_WriteLong( &buf, clc.serverMessageSequence );",
		"MSG_WriteLong( &buf, clc.serverCommandSequence );",
		"for ( i = clc.reliableAcknowledge + 1 ; i <= clc.reliableSequence ; i++ ) {",
		"oldPacketNum = (clc.netchan.outgoingSequence - 1 - cl_packetdup->integer) & PACKET_MASK;",
		"count = cl.cmdNumber - cl.outPackets[ oldPacketNum ].p_cmdNumber;",
		"if ( count > MAX_PACKET_USERCMDS ) {",
		"if ( count >= 1 ) {",
	)
	_assert_order(
		write_block,
		"if ( cl_nodelta->integer || !cl.snap.valid || clc.demowaiting",
		"MSG_WriteByte (&buf, clc_moveNoDelta);",
		"MSG_WriteByte( &buf, count );",
		"key = clc.checksumFeed;",
		"key ^= clc.serverMessageSequence;",
		"key ^= Com_HashKey(clc.serverCommands[ clc.serverCommandSequence & (MAX_RELIABLE_COMMANDS-1) ], 32);",
		"for ( i = 0 ; i < count ; i++ ) {",
		"j = (cl.cmdNumber - count + i + 1) & CMD_MASK;",
		"MSG_WriteDeltaUsercmdKey (&buf, key, oldcmd, cmd);",
		"oldcmd = cmd;",
	)
	_assert_order(
		write_block,
		"packetNum = clc.netchan.outgoingSequence & PACKET_MASK;",
		"cl.outPackets[ packetNum ].p_realtime = cls.realtime;",
		"cl.outPackets[ packetNum ].p_serverTime = oldcmd->serverTime;",
		"cl.outPackets[ packetNum ].p_cmdNumber = cl.cmdNumber;",
		"CL_Netchan_Transmit (&clc.netchan, &buf);",
	)

	_assert_order(
		send_block,
		"if ( cls.state < CA_CONNECTED ) {",
		"if ( com_sv_running->integer && sv_paused->integer && cl_paused->integer ) {",
		"CL_CreateNewCommands();",
		"if ( !CL_ReadyToSendPacket() ) {",
		"CL_WritePacket();",
	)


def test_server_decodes_usercmd_stream_and_replays_new_commands_into_qagame() -> None:
	sv_client = SV_CLIENT_PATH.read_text(encoding="utf-8")
	sv_game = SV_GAME_PATH.read_text(encoding="utf-8")
	client_think_block = _function_block(sv_client, "void SV_ClientThink (client_t *cl, usercmd_t *cmd)")
	user_move_block = _function_block(sv_client, "static void SV_UserMove( client_t *cl, msg_t *msg, qboolean delta )")
	execute_block = _function_block(sv_client, "void SV_ExecuteClientMessage( client_t *cl, msg_t *msg )")
	get_usercmd_block = _function_block(sv_game, "void SV_GetUsercmd( int clientNum, usercmd_t *cmd )")
	game_syscall_block = _function_block(sv_game, "static int SV_GameSystemCallsImpl( int *args, qboolean logContract )")

	_assert_order(
		client_think_block,
		"cl->lastUsercmd = *cmd;",
		"if ( cl->state != CS_ACTIVE ) {",
		"VM_Call( gvm, GAME_CLIENT_THINK, cl - svs.clients );",
	)

	_assert_order(
		user_move_block,
		"if ( delta ) {",
		"cl->deltaMessage = cl->messageAcknowledge;",
		"cmdCount = MSG_ReadByte( msg );",
		"if ( cmdCount < 1 ) {",
		"if ( cmdCount > MAX_PACKET_USERCMDS ) {",
		"key = sv.checksumFeed;",
		"key ^= cl->messageAcknowledge;",
		"key ^= Com_HashKey(cl->reliableCommands[ cl->reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ], 32);",
		"Com_Memset( &nullcmd, 0, sizeof(nullcmd) );",
		"oldcmd = &nullcmd;",
		"MSG_ReadDeltaUsercmdKey( msg, key, oldcmd, cmd );",
		"oldcmd = cmd;",
		"cl->frames[ cl->messageAcknowledge & PACKET_MASK ].messageAcked = svs.time;",
	)
	_assert_order(
		user_move_block,
		"if ( cl->state == CS_PRIMED ) {",
		"SV_ClientEnterWorld( cl, &cmds[0] );",
		"if ( cl->state != CS_ACTIVE ) {",
		"for ( i =  0 ; i < cmdCount ; i++ ) {",
		"if ( cmds[i].serverTime > cmds[cmdCount-1].serverTime ) {",
		"if ( cmds[i].serverTime <= cl->lastUsercmd.serverTime ) {",
		"SV_ClientThink (cl, &cmds[ i ]);",
	)
	assert "cl->deltaMessage = -1;" in user_move_block
	assert 'SV_DropClient( cl, "Cannot validate pure client!");' in user_move_block

	_assert_order(
		execute_block,
		"MSG_Bitstream(msg);",
		"serverId = MSG_ReadLong( msg );",
		"cl->messageAcknowledge = MSG_ReadLong( msg );",
		"cl->reliableAcknowledge = MSG_ReadLong( msg );",
		"do {",
		"c = MSG_ReadByte( msg );",
		"if ( c != clc_clientCommand ) {",
		"if ( !SV_ClientCommand( cl, msg ) ) {",
		"if ( c == clc_move ) {",
		"SV_UserMove( cl, msg, qtrue );",
		"} else if ( c == clc_moveNoDelta ) {",
		"SV_UserMove( cl, msg, qfalse );",
	)
	assert 'Com_Printf( "WARNING: bad command byte for client %i\\n", cl - svs.clients );' in execute_block

	assert 'Com_Error( ERR_DROP, "SV_GetUsercmd: bad clientNum:%i", clientNum );' in get_usercmd_block
	assert "*cmd = svs.clients[clientNum].lastUsercmd;" in get_usercmd_block
	assert "case G_GET_USERCMD:" in game_syscall_block
	assert "SV_GetUsercmd( args[1], VMA(2) );" in game_syscall_block
	assert "case BOTLIB_USER_COMMAND:" in game_syscall_block
	assert "SV_ClientThink( &svs.clients[args[1]], VMA(2) );" in game_syscall_block


def test_keyed_usercmd_delta_keeps_quake_live_tail_fields_and_signed_axes() -> None:
	msg_source = MSG_PATH.read_text(encoding="utf-8")
	q_shared = Q_SHARED_PATH.read_text(encoding="utf-8")
	write_block = _function_block(msg_source, "void MSG_WriteDeltaUsercmdKey( msg_t *msg, int key, usercmd_t *from, usercmd_t *to )")
	read_block = _function_block(msg_source, "void MSG_ReadDeltaUsercmdKey( msg_t *msg, int key, usercmd_t *from, usercmd_t *to )")
	usercmd_decl = q_shared[q_shared.index("typedef struct usercmd_s {") : q_shared.index("} usercmd_t;")]

	_assert_order(
		usercmd_decl,
		"int\t\t\t\tserverTime;",
		"int\t\t\t\tangles[3];",
		"int \t\t\tbuttons;",
		"byte\t\t\tweapon;",
		"byte\t\t\tweaponPrimary;",
		"byte\t\t\tfov;",
		"signed char\tforwardmove, rightmove, upmove;",
	)

	for expected in (
		"from->weaponPrimary == to->weaponPrimary",
		"from->fov == to->fov",
		"key ^= to->serverTime;",
		"MSG_WriteDeltaKey( msg, key, from->forwardmove, to->forwardmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->rightmove, to->rightmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->upmove, to->upmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->weaponPrimary, to->weaponPrimary, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->fov, to->fov, 8 );",
	):
		assert expected in write_block

	_assert_order(
		write_block,
		"MSG_WriteDeltaKey( msg, key, from->angles[0], to->angles[0], 16 );",
		"MSG_WriteDeltaKey( msg, key, from->angles[1], to->angles[1], 16 );",
		"MSG_WriteDeltaKey( msg, key, from->angles[2], to->angles[2], 16 );",
		"MSG_WriteDeltaKey( msg, key, from->forwardmove, to->forwardmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->rightmove, to->rightmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->upmove, to->upmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->buttons, to->buttons, 16 );",
		"MSG_WriteDeltaKey( msg, key, from->weapon, to->weapon, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->weaponPrimary, to->weaponPrimary, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->fov, to->fov, 8 );",
	)
	_assert_order(
		read_block,
		"key ^= to->serverTime;",
		"to->angles[0] = MSG_ReadDeltaKey( msg, key, from->angles[0], 16);",
		"to->angles[1] = MSG_ReadDeltaKey( msg, key, from->angles[1], 16);",
		"to->angles[2] = MSG_ReadDeltaKey( msg, key, from->angles[2], 16);",
		"to->forwardmove = MSG_ReadDeltaKey( msg, key, from->forwardmove, 8);",
		"to->rightmove = MSG_ReadDeltaKey( msg, key, from->rightmove, 8);",
		"to->upmove = MSG_ReadDeltaKey( msg, key, from->upmove, 8);",
		"to->buttons = MSG_ReadDeltaKey( msg, key, from->buttons, 16);",
		"to->weapon = MSG_ReadDeltaKey( msg, key, from->weapon, 8);",
		"to->weaponPrimary = MSG_ReadDeltaKey( msg, key, from->weaponPrimary, 8);",
		"to->fov = MSG_ReadDeltaKey( msg, key, from->fov, 8);",
		"to->angles[0] = from->angles[0];",
	)
	for expected in (
		"to->forwardmove = from->forwardmove;",
		"to->rightmove = from->rightmove;",
		"to->upmove = from->upmove;",
		"to->weaponPrimary = from->weaponPrimary;",
		"to->fov = from->fov;",
	):
		assert expected in read_block


def test_cgame_prediction_imports_host_usercmd_ring_without_bypassing_bounds() -> None:
	cl_cgame = CL_CGAME_PATH.read_text(encoding="utf-8")
	cg_syscalls = CG_SYSCALLS_PATH.read_text(encoding="utf-8")
	cg_predict = CG_PREDICT_PATH.read_text(encoding="utf-8")
	ql_imports = QL_CGAME_IMPORTS_PATH.read_text(encoding="utf-8")
	get_usercmd_block = _function_block(cl_cgame, "qboolean CL_GetUserCmd( int cmdNumber, usercmd_t *ucmd )")
	get_current_block = _function_block(cl_cgame, "int CL_GetCurrentCmdNumber( void )")
	syscall_block = _function_block(cl_cgame, "static int CL_CgameSystemCallsImpl( int *args, qboolean logContract )")
	predict_block = _function_block(cg_predict, "void CG_PredictPlayerState( void )")

	_assert_order(
		get_usercmd_block,
		"if ( cmdNumber > cl.cmdNumber ) {",
		'Com_Error( ERR_DROP, "CL_GetUserCmd: %i >= %i", cmdNumber, cl.cmdNumber );',
		"if ( cmdNumber <= cl.cmdNumber - CMD_BACKUP ) {",
		"return qfalse;",
		"*ucmd = cl.cmds[ cmdNumber & CMD_MASK ];",
		"return qtrue;",
	)
	assert "return cl.cmdNumber;" in get_current_block

	assert "case CG_GETCURRENTCMDNUMBER:" in syscall_block
	assert "return CL_GetCurrentCmdNumber();" in syscall_block
	assert "case CG_GETUSERCMD:" in syscall_block
	assert "return CL_GetUserCmd( args[1], VMA(2) ) ? qtrue : qfalse;" in syscall_block
	assert "case CG_GETCURRENTCMDNUMBER: return CG_QL_IMPORT_GETCURRENTCMDNUMBER;" in cg_syscalls
	assert "case CG_GETUSERCMD: return CG_QL_IMPORT_GETUSERCMD;" in cg_syscalls
	assert "return syscall( CG_GETCURRENTCMDNUMBER );" in cg_syscalls
	assert "return syscall( CG_GETUSERCMD, cmdNumber, ucmd ) ? qtrue : qfalse;" in cg_syscalls
	assert "return CG_Import_Syscall( CG_GETCURRENTCMDNUMBER );" in ql_imports
	assert "return CG_Import_Syscall( CG_GETUSERCMD, cmdNumber, ucmd );" in ql_imports

	_assert_order(
		predict_block,
		"current = trap_GetCurrentCmdNumber();",
		"cmdNum = current - CMD_BACKUP + 1;",
		"trap_GetUserCmd( cmdNum, &oldestCmd );",
		"trap_GetUserCmd( current, &latestCmd );",
		"CG_UpdatePredictedRailFire( &latestCmd );",
		"for ( cmdNum = current - CMD_BACKUP + 1 ; cmdNum <= current ; cmdNum++ ) {",
		"trap_GetUserCmd( cmdNum, &cg_pmove.cmd );",
		"if ( cg_pmove.cmd.serverTime <= cg.predictedPlayerState.commandTime ) {",
		"if ( cg_pmove.cmd.serverTime > latestCmd.serverTime ) {",
		"Pmove (&cg_pmove);",
	)


def test_usercmd_movement_transport_is_backed_by_committed_retail_evidence() -> None:
	aliases = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	hlil = HLIL_PART04_PATH.read_text(encoding="utf-8")
	round_17 = ROUND_17_PATH.read_text(encoding="utf-8")
	round_57 = ROUND_57_PATH.read_text(encoding="utf-8")
	round_62 = ROUND_62_PATH.read_text(encoding="utf-8")
	round_126 = ROUND_126_PATH.read_text(encoding="utf-8")
	round_277 = ROUND_277_PATH.read_text(encoding="utf-8")
	round_57_compact = " ".join(round_57.split())
	round_62_compact = " ".join(round_62.split())
	round_277_compact = " ".join(round_277.split())

	expected_aliases = {
		"sub_4B0170": "QLCGImport_GetCurrentCmdNumber",
		"sub_4B0180": "QLCGImport_GetUserCmd",
		"sub_4B5C70": "CL_CreateCmd",
		"sub_4B5DE0": "CL_CreateNewCommands",
		"sub_4B5E60": "CL_ReadyToSendPacket",
		"sub_4B5F70": "CL_WritePacket",
		"sub_4B62A0": "CL_SendCmd",
		"sub_4D51A0": "MSG_WriteDeltaUsercmdKey",
		"sub_4D54A0": "MSG_ReadDeltaUsercmdKey",
		"sub_4E02D0": "SV_ClientThink",
		"sub_4E0320": "SV_UserMove",
		"sub_4E05C0": "SV_ExecuteClientMessage",
	}
	for address, normalized_name in expected_aliases.items():
		assert aliases[address] == normalized_name

	for expected in (
		"004d51a0    int32_t* sub_4d51a0",
		"004d54a0    int32_t sub_4d54a0",
		"*(arg3 + 0x15)",
		"*(arg3 + 0x16)",
		"004b61d6                  sub_4d51a0",
		"004e0411          sub_4d54a0",
		"004e02d0    int32_t sub_4e02d0",
		"004e0320    int32_t sub_4e0320",
	):
		assert expected in hlil

	assert "Native cgame import wrapper returning the latest generated usercmd number." in round_17
	assert "Native cgame import wrapper copying one `usercmd_t` from the host circular buffer." in round_17
	assert "`sub_4D51A0 -> MSG_WriteDeltaUsercmdKey`" in round_57
	assert "Quake Live extends the keyed usercmd tail with `weaponPrimary` and `fov`" in round_57_compact
	assert "`sub_4E02D0 -> SV_ClientThink`" in round_62
	assert "`sub_4E0320 -> SV_UserMove`" in round_62
	assert "server-side source now pins the same command replay shape" in round_62_compact
	assert "`sub_4B5F70 -> CL_WritePacket`" in round_126
	assert "| `sub_4B5C70` | `CL_CreateCmd` |" in round_277
	assert "| `sub_4B62A0` | `CL_SendCmd` |" in round_277
	assert "client-side source now pins that command stream through `CL_WritePacket`" in round_277_compact
