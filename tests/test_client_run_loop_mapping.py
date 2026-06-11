from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		if text[index] == "{":
			depth += 1
		elif text[index] == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"closing brace not found for: {signature}")


def test_client_run_loop_round_292_maps_host_and_client_frame_wiring() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(
			encoding="utf-8"
		)
	)
	functions_csv = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	hlil = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	common = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")
	qcommon = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
	q_shared = (REPO_ROOT / "src/code/game/q_shared.h").read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	null_client = (REPO_ROOT / "src/code/null/null_client.c").read_text(encoding="utf-8")
	null_main = (REPO_ROOT / "src/code/null/null_main.c").read_text(encoding="utf-8")
	win_main = (REPO_ROOT / "src/code/win32/win_main.c").read_text(encoding="utf-8")
	ql_types = (REPO_ROOT / "src-re/include/ql_types.h").read_text(encoding="utf-8")
	clean_frame_header = (REPO_ROOT / "src-re/clean/include/qlr_client_frame.h").read_text(
		encoding="utf-8"
	)
	proto_frame = (REPO_ROOT / "src-re/prototypes/c_client/cl_frame.c").read_text(
		encoding="utf-8"
	)
	mapping = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_292.md"
	).read_text(encoding="utf-8")

	steam_aliases = aliases["quakelive_steam_srp"]
	expected_aliases = {
		"sub_4CC6C0": "Com_Frame",
		"FUN_004cc6c0": "Com_Frame",
		"sub_4BC3E0": "CL_Frame",
		"sub_4F2590": "QLWebCore_Update",
		"sub_461D40": "SteamClient_Frame",
		"sub_4BC320": "CL_Workshop_Frame",
		"sub_4B62A0": "CL_SendCmd",
		"sub_4B9150": "CL_CheckForResend",
		"sub_4B07C0": "CL_SetCGameTime",
		"sub_4BE3A0": "SCR_UpdateScreen",
		"sub_4DB680": "S_Update",
		"sub_4B3510": "SCR_RunCinematic",
		"sub_4B4800": "Con_RunConsole",
	}
	for raw_name, reconstructed_name in expected_aliases.items():
		assert steam_aliases[raw_name] == reconstructed_name

	for row in [
		"FUN_004cc6c0,004cc6c0,1465",
		"FUN_004bc3e0,004bc3e0,674",
		"FUN_00461d40,00461d40,442",
		"FUN_004bc320,004bc320,187",
		"FUN_004f2590,004f2590,46",
	]:
		assert row in functions_csv

	com_start = hlil.index("004cc986          sub_4cbc90()")
	com_end = hlil.index("004cc9be          if (*(data_145c9e0 + 0x30) != 0)", com_start)
	com_window = hlil[com_start:com_end]
	assert com_window.index("sub_4f2590()") < com_window.index("sub_461d40()")
	assert com_window.index("sub_461d40()") < com_window.index("sub_4bc3e0")

	cl_start = hlil.index('004bc3e0    void __convention("regparm") sub_4bc3e0')
	cl_end = hlil.index("004bc682", cl_start)
	cl_window = hlil[cl_start:cl_end]
	for snippet in [
		"sub_4cd250(\"cl_avidemo\"",
		"data_1528ba0 == 8",
		"sub_4c8900(ecx_2, \"screenshot silent\\n\")",
		"if (sub_4ec640() != 0 && data_1528cc0 == 0)",
		"sub_4b8250()",
		"data_1528ccc = esi_1",
		"if (not(cond:1_1) && *(data_1627c50 + 0x30) != 0)",
		"esi_1 = 0",
		"data_1528cc8 += esi_1",
		"data_1528cc4 = esi_1",
		"sub_4be040(",
		"sub_4b9960()",
		"sub_4bc320()",
		"sub_4b62a0()",
		"sub_4b07c0(sub_4b9150(esi_1))",
		"sub_4be3a0()",
		"sub_4db680()",
		"sub_4b3510()",
		"sub_4b4800()",
		"data_1528cc0.d += 1",
	]:
		assert snippet in cl_window
	assert "else if (data_1528ba0 == 1" in cl_window
	assert "if (data_1528ba0 s>= 4" in cl_window
	assert cl_window.index("sub_4ec640()") < cl_window.index("sub_4b8250()")
	assert cl_window.index("sub_4b8250()") < cl_window.index("data_1528ccc = esi_1")
	assert cl_window.index("data_1528ccc = esi_1") < cl_window.index(
		"if (not(cond:1_1) && *(data_1627c50 + 0x30) != 0)"
	)
	assert cl_window.index("esi_1 = 0") < cl_window.index("data_1528cc8 += esi_1")
	assert cl_window.index("data_1528cc8 += esi_1") < cl_window.index("data_1528cc4 = esi_1")
	assert cl_window.index("data_1528cc4 = esi_1") < cl_window.index("sub_4be040(")
	assert cl_window.index("sub_4b9960()") < cl_window.index("sub_4bc320()")
	assert cl_window.index("sub_4bc320()") < cl_window.index("sub_4b62a0()")
	assert cl_window.index("sub_4b62a0()") < cl_window.index("sub_4b07c0")
	assert cl_window.index("sub_4be3a0()") < cl_window.index("sub_4db680()")
	assert cl_window.index("sub_4db680()") < cl_window.index("sub_4b3510()")
	assert cl_window.index("sub_4b3510()") < cl_window.index("sub_4b4800()")

	common_frame = _extract_function_block(common, "void Com_Frame( void )")
	assert "void SteamClient_Frame( void );" in qcommon
	assert "void CL_WebHost_Frame( void );" in qcommon
	assert "void SteamClient_Frame( void ) {" in cl_main
	assert "void SteamClient_Frame( void ) {" in null_client
	second_event_loop = common_frame.index("// run event loop a second time")
	assert common_frame.index("Com_EventLoop();", second_event_loop) < common_frame.index(
		"CL_WebHost_Frame();"
	)
	assert common_frame.index("CL_WebHost_Frame();") < common_frame.index(
		"SteamClient_Frame();"
	)
	assert common_frame.index("SteamClient_Frame();") < common_frame.index("CL_Frame( msec );")

	cl_frame = _extract_function_block(cl_main, "void CL_Frame ( int msec ) {")
	assert "SteamClient_Frame();" not in cl_frame
	assert "CL_WebHost_Frame();" not in cl_frame
	assert "if ( clc.demoplaying && cl_freezeDemo->integer ) {" in cl_frame
	assert "if ( Sys_MonkeyShouldBeSpanked() && cls.framecount == 0 ) {" in cl_frame
	assert "CL_ChangeReliableCommand();" in cl_frame
	assert cl_frame.index("Sys_MonkeyShouldBeSpanked()") < cl_frame.index("CL_ChangeReliableCommand();")
	assert cl_frame.index("CL_ChangeReliableCommand();") < cl_frame.index("cls.realFrametime = msec;")
	assert cl_frame.index("cls.realFrametime = msec;") < cl_frame.index(
		"if ( clc.demoplaying && cl_freezeDemo->integer ) {"
	)
	assert cl_frame.index("msec = 0;") < cl_frame.index("cls.frametime = msec;")
	assert cl_frame.index("cls.frametime = msec;") < cl_frame.index(
		"cls.realtime += cls.frametime;"
	)
	assert cl_frame.index("cls.realtime += cls.frametime;") < cl_frame.index(
		"SCR_DebugGraph"
	)
	assert cl_frame.index("CL_CheckUserinfo();") < cl_frame.index("CL_CheckTimeout();")
	assert cl_frame.index("CL_CheckTimeout();") < cl_frame.index("CL_Workshop_Frame();")
	assert cl_frame.index("CL_Workshop_Frame();") < cl_frame.index("CL_SendCmd();")
	assert cl_frame.index("CL_SendCmd();") < cl_frame.index("CL_SteamBrowser_Frame();")
	assert cl_frame.index("CL_SteamBrowser_Frame();") < cl_frame.index("CL_CheckForResend();")
	assert cl_frame.index("CL_CheckForResend();") < cl_frame.index("CL_SetCGameTime();")
	assert cl_frame.index("SCR_UpdateScreen();") < cl_frame.index("S_Update();")
	assert cl_frame.index("S_Update();") < cl_frame.index("SCR_RunCinematic();")
	assert cl_frame.index("SCR_RunCinematic();") < cl_frame.index("Con_RunConsole();")
	assert cl_frame.index("Con_RunConsole();") < cl_frame.index("cls.framecount++;")

	assert "int framecount;" in ql_types
	for state_line in [
		"QLR_CA_UNINITIALIZED = 0,",
		"QLR_CA_DISCONNECTED = 1,",
		"QLR_CA_AUTHORIZING = 2,",
		"QLR_CA_CONNECTING = 3,",
		"QLR_CA_CHALLENGING = 4,",
		"QLR_CA_CONNECTED = 5,",
		"QLR_CA_LOADING = 6,",
		"QLR_CA_PRIMED = 7,",
		"QLR_CA_ACTIVE = 8,",
		"QLR_CA_CINEMATIC = 9,",
	]:
		assert state_line in ql_types
	for state_line in [
		"QLR_CLIENT_STATE_AUTHORIZING = 2,",
		"QLR_CLIENT_STATE_LOADING = 6,",
		"QLR_CLIENT_STATE_ACTIVE = 8,",
		"QLR_CLIENT_STATE_CINEMATIC = 9",
	]:
		assert state_line in clean_frame_header
	assert "CA_AUTHORIZING," in q_shared
	assert "CA_LOADING," in q_shared
	assert "qlr_cvar_shadow_t *cl_avidemo_latch;" in ql_types
	assert "void (*workshopFrame)(void);" in ql_types
	assert "void (*steamBrowserFrame)(void);" in ql_types
	assert "int (*monkeyShouldBeSpanked)(void);" in ql_types
	assert "float (*randomFloat)(void);" in ql_types
	assert "void (*changeReliableCommand)(void);" in ql_types
	assert "int Sys_MonkeyShouldBeSpanked( void ) {" in win_main
	assert 'Sys_PathHasReleaseMarker( Sys_Cwd(), "q3monkeyid" )' in win_main
	assert 'Sys_PathHasReleaseMarker( Sys_DefaultInstallPath(), "q3monkeyid" )' in win_main
	assert "int Sys_MonkeyShouldBeSpanked( void ) {" in null_main
	assert "return qfalse;" in _extract_function_block(
		null_main, "int Sys_MonkeyShouldBeSpanked( void ) {"
	)
	assert "void (*readPackets)(void);" not in ql_types
	assert "void (*predictMovement)(void);" not in ql_types
	assert 'qlr_client_call_hook("workshopFrame", ctx->hooks.workshopFrame);' in proto_frame
	assert (
		'qlr_client_call_hook("steamBrowserFrame", ctx->hooks.steamBrowserFrame);'
		in proto_frame
	)
	assert (
		"ctx->clc && ctx->clc->demoplaying && "
		"qlr_client_cvar_integer(ctx->cvars.cl_freezeDemo)"
		in proto_frame
	)
	assert "ctx->hooks.monkeyShouldBeSpanked" in proto_frame
	assert 'qlr_client_call_hook("changeReliableCommand", ctx->hooks.changeReliableCommand);' in proto_frame
	assert "ctx->cls->framecount++;" in proto_frame

	assert "Scope: client run-loop ownership" in mapping
	assert "`src/code/qcommon/common.c` now owns" in mapping
	assert "After this round, the focused lane is about `97%`" in mapping


def test_client_run_loop_round_294_documents_freeze_demo_frame_delta() -> None:
	mapping = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_294.md"
	).read_text(encoding="utf-8")

	assert "Scope: `CL_Frame` demo-freeze frame-delta ownership" in mapping
	assert "`data_1528ccc = esi_1` captures the pre-freeze frame sample" in mapping
	assert "`clc.demoplaying && cl_freezeDemo->integer`" in mapping
	assert "After this round, the focused lane is about `98%`" in mapping


def test_client_run_loop_round_295_documents_retail_state_ids() -> None:
	mapping = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_295.md"
	).read_text(encoding="utf-8")

	assert "Scope: client run-loop state enum identity" in mapping
	assert "`CA_DISCONNECTED == 1`" in mapping
	assert "`CA_CHALLENGING == 4`" in mapping
	assert "`CA_ACTIVE == 8`" in mapping
	assert "After this round, the focused lane remains about `98%`" in mapping


def test_client_run_loop_round_296_documents_release_marker_branch() -> None:
	mapping = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_296.md"
	).read_text(encoding="utf-8")

	assert "Scope: `CL_Frame` release-marker reliable-command mutation" in mapping
	assert "`sub_4EC640 -> Sys_MonkeyShouldBeSpanked`" in mapping
	assert "`sub_4B8250 -> CL_ChangeReliableCommand`" in mapping
	assert "`cls.framecount == 0`" in mapping
	assert "After this round, the focused lane remains about `98%`" in mapping
