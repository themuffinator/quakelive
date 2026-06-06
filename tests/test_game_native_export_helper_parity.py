import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _extract_block(source: str, anchor: str) -> str:
	start = source.index(anchor)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start : index + 1]

	raise AssertionError(f"Unterminated block for {anchor}")


def test_qagame_native_export_table_matches_recovered_slot_order() -> None:
	public_h = _read("src/code/game/g_public.h")
	game_main = _read("src/code/game/g_main.c")
	vm_c = _read("src/code/qcommon/vm.c")
	export_block = _extract_block(game_main, "static void *g_nativeExports")
	vm_block = _extract_block(vm_c, "static int VM_CallNativeExports")
	register_block = _extract_block(vm_c, "qboolean VM_CallGameRegisterCvars")

	expected_slots = [
		("GAME_NATIVE_EXPORT_SHUTDOWN", "G_NativeShutdown"),
		("GAME_NATIVE_EXPORT_RUN_FRAME", "G_RunFrame"),
		("GAME_NATIVE_EXPORT_REGISTER_CVARS", "G_RegisterCvars"),
		("GAME_NATIVE_EXPORT_INIT", "G_NativeInit"),
		("GAME_NATIVE_EXPORT_CONSOLE_COMMAND", "ConsoleCommand"),
		("GAME_NATIVE_EXPORT_CLIENT_USERINFO_CHANGED", "ClientUserinfoChanged"),
		("GAME_NATIVE_EXPORT_CLIENT_THINK", "ClientThink"),
		("GAME_NATIVE_EXPORT_CLIENT_DISCONNECT", "ClientDisconnect"),
		("GAME_NATIVE_EXPORT_CLIENT_CONNECT", "G_NativeClientConnect"),
		("GAME_NATIVE_EXPORT_CLIENT_COMMAND", "ClientCommand"),
		("GAME_NATIVE_EXPORT_CLIENT_BEGIN", "ClientBegin"),
		("GAME_NATIVE_EXPORT_BOTAI_START_FRAME", "BotAIStartFrame"),
		("GAME_NATIVE_EXPORT_CAN_CLIENT_SEE_CLIENT", "G_CanClientSeeClient"),
		("GAME_NATIVE_EXPORT_FREEZE_CAN_SEE_THAW_PROGRESS_EVENT", "G_FreezeCanSeeThawProgressEvent"),
		("GAME_NATIVE_EXPORT_IS_OBJECTIVE_ENTITY", "G_IsObjectiveEntity"),
		("GAME_NATIVE_EXPORT_SHOULD_SUPPRESS_VOICE_TO_CLIENT", "G_ShouldSuppressVoiceToClient"),
		("GAME_NATIVE_EXPORT_IS_CLIENT_ADMIN", "G_IsClientAdmin"),
		("GAME_NATIVE_EXPORT_ARE_ENEMY_CLIENTS", "G_AreEnemyClients"),
		("GAME_NATIVE_EXPORT_GET_CLIENT_SCORE", "G_GetClientScore"),
	]

	for slot, target in expected_slots:
		assert slot in public_h
		assert f"[{slot}] = {target}" in export_block

	dispatched_slots = [
		slot
		for slot, _target in expected_slots
		if slot != "GAME_NATIVE_EXPORT_REGISTER_CVARS"
	]

	for slot in dispatched_slots:
		assert f"dllExports[{slot}]" in vm_block

	assert "dllExports[GAME_NATIVE_EXPORT_REGISTER_CVARS]" not in vm_block
	assert "dllExports[GAME_NATIVE_EXPORT_REGISTER_CVARS]" in register_block
	assert 'VM_LogTraceEvent( "call %s GAME_REGISTER_CVARS", vm->name );' in register_block
	assert "((void (QDECL *)( void ))exportFunc)();" in register_block

	assert "GAME_NATIVE_EXPORT_COUNT" in public_h
	assert "static void *g_nativeExports[GAME_NATIVE_EXPORT_COUNT]" in game_main
	assert "return GAME_NATIVE_EXPORT_COUNT;" in vm_c
	assert "VM_NormalizeQbooleanArg( args[2] )" in vm_block
	assert "VM_NormalizeQbooleanResult" in vm_block


def test_native_loader_api_version_wiring_matches_retail_dllentry_contracts() -> None:
	sv_game = _read("src/code/server/sv_game.c")
	server_h = _read("src/code/server/server.h")
	cl_cgame = _read("src/code/client/cl_cgame.c")
	qcommon_h = _read("src/code/qcommon/qcommon.h")
	game_public = _read("src/code/game/g_public.h")
	cgame_public = _read("src/code/cgame/cg_public.h")
	qagame_mapping = _read("docs/reverse-engineering/qagame-mapping.md")
	cgame_mapping = _read("docs/reverse-engineering/cgame-mapping.md")
	qvm_fallback_note = _read("docs/reverse-engineering/qcommon-vm-fallback-ownership-2026-04-10.md")
	register_game_block = _extract_block(sv_game, "void SV_RegisterGameCvars")

	assert "#define\tGAME_API_VERSION\t8" in game_public
	assert "#define\tGAME_NATIVE_API_VERSION\t10" in game_public
	assert "#define\tCGAME_IMPORT_API_VERSION\t4" in cgame_public
	assert "#define\tCGAME_NATIVE_API_VERSION\t8" in cgame_public
	assert 'VM_Create( "qagame", SV_GameSystemCalls, VMI_NATIVE, ql_game_imports, GAME_NATIVE_API_VERSION );' in sv_game
	assert 'return VM_Create( "qagame", SV_GameSystemCalls, interpret, ql_game_imports, GAME_API_VERSION );' in sv_game
	assert 'void\t\tSV_RegisterGameCvars( void );' in server_h
	assert "void SV_RegisterGameCvars( void );" in qcommon_h
	assert "qboolean VM_CallGameRegisterCvars( vm_t *vm );" in qcommon_h
	assert 'var = Cvar_Get( "bot_enable", "1", 0 );' in register_game_block
	assert 'interpret = Cvar_VariableValue( "vm_game" );' in register_game_block
	assert "gvm = SV_LoadGameModule( interpret );" in register_game_block
	assert 'Com_Error( ERR_FATAL, "Couldn\'t load game VM during cvar registration.\\n" );' in register_game_block
	assert "VM_CallGameRegisterCvars( gvm );" in register_game_block
	assert 'VM_Create( "cgame", CL_CgameSystemCalls, VMI_NATIVE, ql_cgame_imports, CGAME_NATIVE_API_VERSION );' in cl_cgame
	assert 'return VM_Create( "cgame", CL_CgameSystemCalls, interpret, ql_cgame_imports, CGAME_IMPORT_API_VERSION );' in cl_cgame
	assert "writes API version `10`" in qagame_mapping
	assert "writing native API version `8`" in cgame_mapping
	assert "Windows defaults to native modules" in qvm_fallback_note
	assert "fallback then opens `vm/<name>.qvm`" in qvm_fallback_note


def test_native_ui_and_cgame_receive_retail_packed_glconfig() -> None:
	client_h = _read("src/code/client/client.h")
	cl_cgame = _read("src/code/client/cl_cgame.c")
	cl_ui = _read("src/code/client/cl_ui.c")
	tr_types = _read("src/code/cgame/tr_types.h")
	win_glimp = _read("src/code/win32/win_glimp.c")
	helper_block = _extract_block(cl_cgame, "void CL_GetRetailGlconfig")
	cgame_import_block = _extract_block(cl_cgame, "static int QDECL CG_Import_Syscall")
	ui_import_block = _extract_block(cl_ui, "static int QDECL UI_Import_Syscall")

	assert "void CL_GetRetailGlconfig( void *glconfig );" in client_h
	assert "qboolean\t\t\t\ttextureEnvAddAvailable;" in tr_types
	assert "qboolean\t\t\t\tmultitextureAvailable;" in tr_types
	assert "int\t\t\t\t\t\tvidWidth, vidHeight;" in tr_types
	assert "#if !defined(CGAME) && !defined(UI_EXPORTS)" in tr_types
	assert tr_types.index("qboolean\t\t\t\ttextureEnvAddAvailable;") < tr_types.index("qboolean\t\t\t\tmultitextureAvailable;")
	assert tr_types.index("qboolean\t\t\t\tmultitextureAvailable;") < tr_types.index("int\t\t\t\t\t\tvidWidth, vidHeight;")
	assert tr_types.index("qboolean\t\t\t\tstereoEnabled;") < tr_types.index("#if !defined(CGAME) && !defined(UI_EXPORTS)")
	assert "glConfig.multitextureAvailable = qfalse;" in win_glimp
	assert "glConfig.multitextureAvailable = qtrue;" in win_glimp
	assert "qboolean\t\t\t\tmultitextureAvailable;" in cl_cgame
	assert "typedef char qlRetailGlconfigSizeCheck[( sizeof( qlRetailGlconfig_t ) == 0x2c44 ) ? 1 : -1 ];" in cl_cgame
	assert "retailConfig.textureEnvAddAvailable = cls.glconfig.textureEnvAddAvailable;" in helper_block
	assert "retailConfig.multitextureAvailable = cls.glconfig.multitextureAvailable;" in helper_block
	assert "retailConfig.vidWidth = cls.glconfig.vidWidth;" in helper_block
	assert "retailConfig.vidHeight = cls.glconfig.vidHeight;" in helper_block
	assert "retailConfig.windowAspect = cls.glconfig.windowAspect;" in helper_block
	assert "retailConfig.stereoEnabled = cls.glconfig.stereoEnabled;" in helper_block
	assert "retailConfig.smpActive" not in helper_block
	assert "Com_Memcpy( glconfig, &retailConfig, sizeof( retailConfig ) );" in helper_block

	for import_block, syscall_name in (
		(cgame_import_block, "CG_GETGLCONFIG"),
		(ui_import_block, "UI_GETGLCONFIG"),
	):
		assert f"if ( arg == {syscall_name} ) {{" in import_block
		assert "glconfig = va_arg(ap, void *);" in import_block
		assert "CL_GetRetailGlconfig( glconfig );" in import_block
		assert import_block.index(f"if ( arg == {syscall_name} ) {{") < import_block.index("args[0] = arg;")


def test_native_cgame_import_slot_54_preserves_retail_ad_bridge_callout() -> None:
	cgame_public = _read("src/code/cgame/cg_public.h")
	cl_cgame = _read("src/code/client/cl_cgame.c")
	engine_hlil = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt")
	cgame_hlil = _read("references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt")
	import_block = _extract_block(cl_cgame, "static void CL_InitCGameImports")
	wrapper_block = _extract_block(cl_cgame, "static void QDECL QL_CG_trap_AdvertisementBridge_Reserved21C0")

	assert "CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_21C0 = 54," in cgame_public
	assert "004f21c0    void sub_4f21c0()" in engine_hlil
	assert "jump(*(*ecx + 0x40))" in engine_hlil
	assert "10029139  int32_t ecx = *(data_1074cccc + 0xd8)" in cgame_hlil
	assert "10029149  ecx()" in cgame_hlil
	assert "cl_webBridge.vtbl->reserved21C0( &cl_webBridge );" in wrapper_block
	assert "CG_LoadHudMenu calls import[54]" in wrapper_block
	assert "ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_21C0] = (ql_import_f)QL_CG_trap_AdvertisementBridge_Reserved21C0;" in import_block
	assert import_block.index("CG_QL_IMPORT_R_REGISTERSHADERNOMIP") < import_block.index("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_21C0")
	assert import_block.index("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_21C0") < import_block.index("CG_QL_IMPORT_SETUP_ADVERT_CELL_SHADER")


def test_native_cgame_import_enum_covers_full_retail_slab() -> None:
	cgame_public = _read("src/code/cgame/cg_public.h")
	cgame_local = _read("src/code/cgame/cg_local.h")
	cg_syscalls = _read("src/code/cgame/cg_syscalls.c")
	cl_cgame = _read("src/code/client/cl_cgame.c")
	aliases = _read("references/analysis/quakelive_symbol_aliases.json")
	host_part04 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt")
	host_part05 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt")
	host_part07 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt")
	import_block = _extract_block(cl_cgame, "static void CL_InitCGameImports")
	set_value_block = _extract_block(cl_cgame, "static void QDECL QL_CG_trap_Cvar_SetValue")
	reserved_block = _extract_block(cl_cgame, "static int QDECL QL_CG_trap_RetailReservedImport")
	subscribed_block = _extract_block(cl_cgame, "static int QDECL QL_CG_trap_IsSubscribedApp")
	module_set_value_block = _extract_block(cg_syscalls, "void trap_QL_Cvar_SetValue")
	module_subscribed_block = _extract_block(cg_syscalls, "qboolean trap_QL_IsSubscribedApp")

	retail_slots = [
		(name, int(slot))
		for name, slot in re.findall(r"\b(CG_QL_IMPORT_[A-Z0-9_]+)\s*=\s*(\d+),", cgame_public)
		if int(slot) < 128
	]
	slot_names = {slot: name for name, slot in retail_slots}

	assert len(retail_slots) == 128
	assert set(slot_names) == set(range(128))

	for name, slot in (
		("CG_QL_IMPORT_CVAR_SET_VALUE", 8),
		("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_59", 59),
		("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_63", 63),
		("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_65", 65),
		("CG_QL_IMPORT_RETAIL_RESERVED_66", 66),
		("CG_QL_IMPORT_RETAIL_RESERVED_67", 67),
		("CG_QL_IMPORT_RETAIL_RESERVED_68", 68),
		("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_69", 69),
		("CG_QL_IMPORT_RETAIL_RESERVED_80", 80),
		("CG_QL_IMPORT_NULL_100", 100),
		("CG_QL_IMPORT_PC_ADD_GLOBAL_DEFINE", 107),
		("CG_QL_IMPORT_RETAIL_RESERVED_112", 112),
		("CG_QL_IMPORT_RETAIL_RESERVED_113", 113),
		("CG_QL_IMPORT_RETAIL_RESERVED_117", 117),
		("CG_QL_IMPORT_NULL_118", 118),
		("CG_QL_IMPORT_NULL_119", 119),
		("CG_QL_IMPORT_IS_SUBSCRIBED_APP", 122),
	):
		assert slot_names[slot] == name
		assert f"{name} = {slot}," in cgame_public

	for expected in (
		"00565958  void* data_565958 = __set_purecall_handler",
		"00565978  void* data_565978 = sub_4ea2b0",
		"00565a44  void* data_565a44 = sub_4aff40",
		"00565a54  void* data_565a54 = sub_4aff80",
		"00565a5c  void* data_565a5c = sub_4affe0",
		"00565a60  void* data_565a60 = sub_4d7980",
		"00565a64  void* data_565a64 = sub_4d7980",
		"00565a68  void* data_565a68 = sub_4d7980",
		"00565a6c  void* data_565a6c = sub_4affc0",
		"00565a98  void* data_565a98 = sub_4b00c0",
		"00565b04  void* data_565b04 = sub_4e1740",
		"00565b18  void* data_565b18 = sub_4b0340",
		"00565b1c  void* data_565b1c = sub_4bef20",
		"00565b2c  void* data_565b2c = sub_4b0370",
		"00565b40  void* data_565b40 = sub_4bf2e0",
	):
		assert expected in host_part07

	assert "00565ae8" in host_part07 and "00 00 00 00" in host_part07
	assert "00565b30" in host_part07 and "00 00 00 00 00 00 00 00" in host_part07
	assert 'sub_4e9ff0("cgame", &data_146cc38, &data_565958, &var_8)' in host_part04
	assert "004ea2b0    int32_t* sub_4ea2b0(int32_t arg1, float arg2)" in host_part05
	assert "return sub_4cd270(arg1, fconvert.s(fconvert.t(arg2)))" in host_part05
	assert '"sub_4E1740": "PC_AddGlobalDefine"' in aliases
	assert '"sub_4BF2E0": "QLUIImport_IsSubscribedApp"' in aliases

	assert "Cvar_SetValue( varName, value );" in set_value_block
	assert "return 0;" in reserved_block
	assert "if ( !CL_SteamServicesEnabled() ) {" in subscribed_block
	assert "return QL_Steamworks_IsSubscribedApp( (uint32_t)appId ) ? 1 : 0;" in subscribed_block
	assert "void\t\ttrap_QL_Cvar_SetValue( const char *varName, float value );" in cgame_local
	assert "qboolean\ttrap_QL_IsSubscribedApp( int appId );" in cgame_local
	assert "static ID_INLINE void trap_QL_Cvar_SetValue( const char *varName, float value )" in cgame_local
	assert "static ID_INLINE qboolean trap_QL_IsSubscribedApp( int appId )" in cgame_local
	assert "CG_GetNativeImportFunction( CG_QL_IMPORT_CVAR_SET_VALUE )" in module_set_value_block
	assert "trap_Cvar_Set( varName, valueString );" in module_set_value_block
	assert "CG_GetNativeImportFunction( CG_QL_IMPORT_IS_SUBSCRIBED_APP )" in module_subscribed_block
	assert "return ((int (QDECL *)( int ))import)( appId ) ? qtrue : qfalse;" in module_subscribed_block
	assert "case CG_PC_ADD_GLOBAL_DEFINE: return CG_QL_IMPORT_PC_ADD_GLOBAL_DEFINE;" in cg_syscalls
	assert "ql_cgame_imports[CG_QL_IMPORT_CVAR_SET_VALUE] = (ql_import_f)QL_CG_trap_Cvar_SetValue;" in import_block
	assert "ql_cgame_imports[CG_QL_IMPORT_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_CG_trap_PC_AddGlobalDefine;" in import_block
	assert "ql_cgame_imports[CG_QL_IMPORT_IS_SUBSCRIBED_APP] = (ql_import_f)QL_CG_trap_IsSubscribedApp;" in import_block
	for reserved_name in (
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_59",
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_63",
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_65",
		"CG_QL_IMPORT_RETAIL_RESERVED_66",
		"CG_QL_IMPORT_RETAIL_RESERVED_67",
		"CG_QL_IMPORT_RETAIL_RESERVED_68",
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_69",
		"CG_QL_IMPORT_RETAIL_RESERVED_80",
		"CG_QL_IMPORT_RETAIL_RESERVED_112",
		"CG_QL_IMPORT_RETAIL_RESERVED_113",
		"CG_QL_IMPORT_RETAIL_RESERVED_117",
	):
		assert f"ql_cgame_imports[{reserved_name}] = (ql_import_f)QL_CG_trap_RetailReservedImport;" in import_block
	for null_name in (
		"CG_QL_IMPORT_NULL_100",
		"CG_QL_IMPORT_NULL_118",
		"CG_QL_IMPORT_NULL_119",
	):
		assert f"ql_cgame_imports[{null_name}]" not in import_block
	assert "CG_QL_IMPORT_COMPAT_PC_ADD_GLOBAL_DEFINE" not in cg_syscalls


def test_voice_suppression_helper_matches_retail_export_policy() -> None:
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")

	assert "qboolean G_ShouldSuppressVoiceToClient( int senderClientNum, int recipientClientNum );" in local_h
	assert "qboolean G_ShouldSuppressVoiceToClient( int senderClientNum, int recipientClientNum ) {" in team_c
	assert "if ( recipientEnt->r.svFlags & SVF_BOT ) {" in team_c
	assert "if ( sender->sess.muted ) {" in team_c
	assert "if ( g_gametype.integer < GT_TEAM || g_allTalk.integer ) {" in team_c
	assert "if ( senderClientNum == recipientClientNum ) {" in team_c
	assert "return G_ClientNumsOnSameTeam( senderClientNum, recipientClientNum ) ? qfalse : qtrue;" in team_c


def test_objective_classifier_covers_retail_flag_and_obelisk_paths() -> None:
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")

	assert "qboolean G_IsObjectiveEntity( int entNum );" in local_h
	assert "qboolean G_ItemUsesRespawnTimer( const gitem_t *item );" in local_h
	assert "static qboolean G_IsObjectiveFlagItemEntity( const gentity_t *ent, qboolean allowNeutralFlag ) {" in team_c
	assert "static qboolean G_IsOverloadObjectiveEntity( const gentity_t *ent ) {" in team_c
	assert "static qboolean G_IsQuadHogObjectiveEntity( const gentity_t *ent ) {" in team_c
	assert "static qboolean G_IsItemTimerObjectiveEntity( const gentity_t *ent ) {" in team_c
	assert "qboolean G_IsObjectiveEntity( int entNum ) {" in team_c
	assert "case GT_FFA:" in team_c
	assert "case GT_CTF:" in team_c
	assert "case GT_ATTACK_DEFEND:" in team_c
	assert "case GT_1FCTF:" in team_c
	assert "case GT_OBELISK:" in team_c
	assert "if ( level.quadHogEnabled ) {" in team_c
	assert "ent->item->giType == IT_POWERUP && ent->item->giTag == PW_QUAD" in team_c
	assert "if ( g_itemTimers.integer == 0 ) {" in team_c
	assert "return G_ItemUsesRespawnTimer( ent->item );" in team_c
	assert "if ( ent->client && ent->target_ent && G_IsObjectiveFlagItemEntity( ent->target_ent, qtrue ) ) {" in team_c
	assert "if ( G_IsOverloadObjectiveEntity( ent ) ) {" in team_c
	assert "return G_IsItemTimerObjectiveEntity( ent );" in team_c


def test_server_snapshot_uses_retail_visibility_exports_before_pvs() -> None:
	snapshot_c = _read("src/code/server/sv_snapshot.c")
	helper_block = _extract_block(snapshot_c, "static qboolean SV_GameForcesSnapshotEntity")
	visible_block = _extract_block(snapshot_c, "static void SV_AddEntitiesVisibleFromPoint")

	for expected in (
		"VM_Call( gvm, GAME_CAN_CLIENT_SEE_CLIENT, viewerClientNum, entityNum )",
		"VM_Call( gvm, GAME_FREEZE_CAN_SEE_THAW_PROGRESS_EVENT, viewerClientNum, entityNum )",
		"VM_Call( gvm, GAME_IS_OBJECTIVE_ENTITY, entityNum )",
	):
		assert expected in helper_block

	assert visible_block.index("if ( ent->r.svFlags & SVF_BROADCAST ) {") < visible_block.index(
		"SV_GameForcesSnapshotEntity( frame->ps.clientNum, e )"
	)
	assert visible_block.index("SV_GameForcesSnapshotEntity( frame->ps.clientNum, e )") < visible_block.index(
		"if ( !CM_AreasConnected( clientarea, svEnt->areanum ) ) {"
	)


def test_freeze_visibility_helper_matches_retail_export_boundary() -> None:
	public_h = _read("src/code/game/bg_public.h")
	local_h = _read("src/code/game/g_local.h")
	freeze_c = _read("src/code/game/g_freeze.c")

	assert "qboolean\tG_FreezeCanSeeThawProgressEvent( int clientNum, int entNum );" in local_h
	assert "EV_DROWN = 57," in public_h
	assert "EV_OBITUARY = 58," in public_h
	assert "EV_THAW_PLAYER = 87," in public_h
	assert "EV_THAW_TICK = 88," in public_h
	assert "static int G_FreezeResolveThawProgressTarget( const gentity_t *ent ) {" in freeze_c
	assert "qboolean G_FreezeCanSeeThawProgressEvent( int clientNum, int entNum ) {" in freeze_c
	assert "if ( G_FreezeResolveRoundState() != ROUNDSTATE_ACTIVE ) {" in freeze_c
	assert "if ( ent->s.eType != ET_EVENTS + EV_THAW_TICK ) {" in freeze_c
	assert "targetClientNum = ent->s.otherEntityNum;" in freeze_c
	assert "targetClientNum = ent->s.clientNum;" in freeze_c
	assert "return G_ClientNumsOnSameTeam( clientNum, targetClientNum );" in freeze_c


def test_qagame_native_import_table_uses_public_header_count() -> None:
	public_h = _read("src/code/game/g_public.h")
	g_syscalls = _read("src/code/game/g_syscalls.c")
	ai_main = _read("src/code/game/ai_main.c")
	sv_game = _read("src/code/server/sv_game.c")
	ql_game_imports = _read("src/code/server/ql_game_imports.inc")
	qagame_ghidra = _read("references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c")
	qagame_hlil = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt"
	)
	qagame_hlil_cvars = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
	)
	syscall_map = _extract_block(g_syscalls, "static int G_MapNativeImport")
	native_syscall = _extract_block(g_syscalls, "static int QDECL G_NativeImportSyscall")
	bot_test_aas = _extract_block(ai_main, "void BotTestAAS")
	game_draw_debug_areas = _extract_block(g_syscalls, "void trap_BotDrawDebugAreas")
	game_draw_avoid_spots = _extract_block(g_syscalls, "void trap_BotDrawAvoidSpots")
	bot_ai_start_frame = _extract_block(ai_main, "int BotAIStartFrame(int time)")
	predict_client_movement = _extract_block(
		ql_game_imports,
		"static int QDECL QL_G_trap_AAS_PredictClientMovement",
	)
	server_draw_debug_areas = _extract_block(
		sv_game,
		"static void QDECL QL_G_trap_BotDrawDebugAreas",
	)
	server_draw_avoid_spots = _extract_block(
		sv_game,
		"static void QDECL QL_G_trap_BotDrawAvoidSpots",
	)
	ea_walk = _extract_block(
		ql_game_imports,
		"static void QDECL QL_G_trap_EA_Walk",
	)
	ea_end_regular = _extract_block(
		ql_game_imports,
		"static void QDECL QL_G_trap_EA_EndRegular",
	)
	bot_avoid_goal_time = _extract_block(
		ql_game_imports,
		"static float QDECL QL_G_trap_BotAvoidGoalTime",
	)
	send_console_block = _extract_block(sv_game, "static void SV_GameExecuteConsoleCommand")
	game_syscall_block = _extract_block(sv_game, "static int SV_GameSystemCallsImpl")
	retail_send_console = _extract_block(sv_game, "static void QDECL QL_G_trap_SendConsoleCommandText")

	assert "#define GAME_LEGACY_IMPORT_COUNT\t(G_RANK_REPORT_STR + 1)" in public_h
	assert "#define GAME_NATIVE_IMPORT_COUNT\tG_QL_IMPORT_TOTAL_COUNT" in public_h
	assert "G_QL_IMPORT_COMPAT_BASE = G_QL_IMPORT_COUNT," in public_h
	assert "G_QL_IMPORT_TOTAL_COUNT = G_QL_IMPORT_COMPAT_BASE + GAME_LEGACY_IMPORT_COUNT" in public_h
	assert "G_SEND_CONSOLE_COMMAND,\t// ( const char *text );" in public_h
	assert "G_QL_IMPORT_BOTLIB_LIBVAR_GET = 52," in public_h
	assert "G_QL_IMPORT_BOTLIB_START_FRAME = 54," in public_h
	assert "G_QL_IMPORT_BOTLIB_UPDATE_ENTITY = 56," in public_h
	assert "G_QL_IMPORT_BOTLIB_TEST = 57," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS = 61," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_AREA_INFO = 62," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO = 63," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_INITIALIZED = 64," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX = 65," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_TIME = 66," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM = 67," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX = 68," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS = 69," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS = 70," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY = 71," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY = 72," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY = 73," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY = 74," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY = 75," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY = 76," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA = 77," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA = 78," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE = 79," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL = 80," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_SWIMMING = 81," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT = 82," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS = 83," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS = 84," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_SAY = 85," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_SAY_TEAM = 86," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_COMMAND = 87," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_ACTION = 88," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_WALK = 89," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_GESTURE = 90," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_TALK = 91," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_ATTACK = 92," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_USE = 93," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_RESPAWN = 94," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_CROUCH = 95," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_MOVE_UP = 96," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_MOVE_DOWN = 97," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_MOVE_FORWARD = 98," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_MOVE_BACK = 99," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_MOVE_LEFT = 100," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_MOVE_RIGHT = 101," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_SELECT_WEAPON = 102," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_JUMP = 103," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_DELAYED_JUMP = 104," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_MOVE = 105," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_VIEW = 106," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_END_REGULAR = 107," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_GET_INPUT = 108," in public_h
	assert "G_QL_IMPORT_BOTLIB_EA_RESET_INPUT = 109," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER = 110," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_FREE_CHARACTER = 111," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_FLOAT = 112," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT = 113," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_INTEGER = 114," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BINTEGER = 115," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING = 116," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_ALLOC_CHAT_STATE = 117," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_FREE_CHAT_STATE = 118," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE = 119," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_REMOVE_CONSOLE_MESSAGE = 120," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE = 121," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_NUM_CONSOLE_MESSAGE = 122," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT = 123," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_NUM_INITIAL_CHATS = 124," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_REPLY_CHAT = 125," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT = 127," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE = 128," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS = 138," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS = 139," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_EMPTY_GOAL_STACK = 142," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_DUMP_AVOID_GOALS = 143," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_DUMP_GOAL_STACK = 144," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_GET_MAP_LOCATION_GOAL = 153," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_AVOID_GOAL_TIME = 155," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_INIT_LEVEL_ITEMS = 157," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS = 158," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_LOAD_ITEM_WEIGHTS = 159," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_FREE_ITEM_WEIGHTS = 160," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC = 161," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC = 162," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC = 163," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_ALLOC_GOAL_STATE = 164," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_FREE_GOAL_STATE = 165," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE = 166," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_REACHABILITY_AREA = 171," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION = 173," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_ALLOC_MOVE_STATE = 174," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_FREE_MOVE_STATE = 175," in public_h
	assert "BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT," in public_h
	assert "BOTLIB_EA_SAY = 400," in public_h
	assert "BOTLIB_EA_END_REGULAR," in public_h
	assert "BOTLIB_AI_LOAD_CHARACTER = 500," in public_h
	assert "BOTLIB_AI_EMPTY_GOAL_STACK," in public_h
	assert "BOTLIB_AI_AVOID_GOAL_TIME," in public_h
	assert "BOTLIB_AI_ALLOC_MOVE_STATE," in public_h
	assert "BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL," in public_h
	assert "BOTLIB_AAS_PREDICT_ROUTE," in public_h
	assert "BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX," in public_h
	assert "static ql_import_f ql_game_imports[GAME_NATIVE_IMPORT_COUNT];" in sv_game
	assert "Com_Memset( ql_game_imports, 0, sizeof( ql_game_imports ) );" in sv_game
	assert '(*(code *)*DAT_104b13ac)("map_restart 0\\n");' in qagame_ghidra
	assert '(*(code *)*DAT_104b13ac)("vstr nextmap\\n");' in qagame_ghidra
	assert "Cbuf_ExecuteText( exec_when, text );" in send_console_block
	assert "if ( args[1] >= EXEC_NOW && args[1] <= EXEC_APPEND ) {" in game_syscall_block
	assert "SV_GameExecuteConsoleCommand( args[1], VMA(2) );" in game_syscall_block
	assert "SV_GameExecuteConsoleCommand( EXEC_APPEND, VMA(1) );" in game_syscall_block
	assert "G_Import_Syscall( G_SEND_CONSOLE_COMMAND, text );" in retail_send_console
	assert "ql_game_imports[G_QL_IMPORT_SEND_CONSOLE_COMMAND] = (ql_import_f)QL_G_trap_SendConsoleCommandText;" in sv_game
	assert "[G_SEND_CONSOLE_COMMAND] = (ql_import_f)QL_G_trap_SendConsoleCommand," in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_LIBVAR_GET] = (ql_import_f)QL_G_trap_BotLibVarGet;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_START_FRAME] = (ql_import_f)QL_G_trap_BotLibStartFrame;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_UPDATE_ENTITY] = (ql_import_f)QL_G_trap_BotLibUpdateEntity;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_TEST] = (ql_import_f)QL_G_trap_BotLibTest;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS] = (ql_import_f)QL_G_trap_AAS_BBoxAreas;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_INFO] = (ql_import_f)QL_G_trap_AAS_AreaInfo;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO] = (ql_import_f)QL_G_trap_AAS_EntityInfo;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_INITIALIZED] = (ql_import_f)QL_G_trap_AAS_Initialized;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX] = (ql_import_f)QL_G_trap_AAS_PresenceTypeBoundingBox;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TIME] = (ql_import_f)QL_G_trap_AAS_Time;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX] = (ql_import_f)QL_G_trap_AAS_PointReachabilityAreaIndex;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY] = (ql_import_f)QL_G_trap_AAS_NextBSPEntity;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_ValueForBSPEpairKey;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_VectorForBSPEpairKey;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_FloatForBSPEpairKey;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_IntForBSPEpairKey;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY] = (ql_import_f)QL_G_trap_AAS_AreaReachability;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA] = (ql_import_f)QL_G_trap_AAS_EnableRoutingArea;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE] = (ql_import_f)QL_G_trap_AAS_PredictRoute;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL] = (ql_import_f)QL_G_trap_AAS_AlternativeRouteGoals;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_SWIMMING] = (ql_import_f)QL_G_trap_AAS_Swimming;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT] = (ql_import_f)QL_G_trap_AAS_PredictClientMovement;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS] = (ql_import_f)QL_G_trap_BotDrawDebugAreas;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS] = (ql_import_f)QL_G_trap_BotDrawAvoidSpots;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_SAY] = (ql_import_f)QL_G_trap_EA_Say;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_SAY_TEAM] = (ql_import_f)QL_G_trap_EA_SayTeam;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_ACTION] = (ql_import_f)QL_G_trap_EA_Action;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_WALK] = (ql_import_f)QL_G_trap_EA_Walk;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_GESTURE] = (ql_import_f)QL_G_trap_EA_Gesture;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_TALK] = (ql_import_f)QL_G_trap_EA_Talk;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_ATTACK] = (ql_import_f)QL_G_trap_EA_Attack;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_USE] = (ql_import_f)QL_G_trap_EA_Use;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_RESPAWN] = (ql_import_f)QL_G_trap_EA_Respawn;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_CROUCH] = (ql_import_f)QL_G_trap_EA_Crouch;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_MOVE_UP] = (ql_import_f)QL_G_trap_EA_MoveUp;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_MOVE_DOWN] = (ql_import_f)QL_G_trap_EA_MoveDown;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_MOVE_FORWARD] = (ql_import_f)QL_G_trap_EA_MoveForward;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_MOVE_BACK] = (ql_import_f)QL_G_trap_EA_MoveBack;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_MOVE_LEFT] = (ql_import_f)QL_G_trap_EA_MoveLeft;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_MOVE_RIGHT] = (ql_import_f)QL_G_trap_EA_MoveRight;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_SELECT_WEAPON] = (ql_import_f)QL_G_trap_EA_SelectWeapon;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_JUMP] = (ql_import_f)QL_G_trap_EA_Jump;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_DELAYED_JUMP] = (ql_import_f)QL_G_trap_EA_DelayedJump;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_MOVE] = (ql_import_f)QL_G_trap_EA_Move;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_VIEW] = (ql_import_f)QL_G_trap_EA_View;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_END_REGULAR] = (ql_import_f)QL_G_trap_EA_EndRegular;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_GET_INPUT] = (ql_import_f)QL_G_trap_EA_GetInput;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_EA_RESET_INPUT] = (ql_import_f)QL_G_trap_EA_ResetInput;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER] = (ql_import_f)QL_G_trap_BotLoadCharacter;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_CHARACTER] = (ql_import_f)QL_G_trap_BotFreeCharacter;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_FLOAT] = (ql_import_f)QL_G_trap_Characteristic_Float;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_INTEGER] = (ql_import_f)QL_G_trap_Characteristic_Integer;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BINTEGER] = (ql_import_f)QL_G_trap_Characteristic_BInteger;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING] = (ql_import_f)QL_G_trap_Characteristic_String;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_CHAT_STATE] = (ql_import_f)QL_G_trap_BotAllocChatState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_CHAT_STATE] = (ql_import_f)QL_G_trap_BotFreeChatState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REMOVE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotRemoveConsoleMessage;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNextConsoleMessage;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_NUM_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNumConsoleMessages;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_NUM_INITIAL_CHATS] = (ql_import_f)QL_G_trap_BotNumInitialChats;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REPLY_CHAT] = (ql_import_f)QL_G_trap_BotReplyChat;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE] = (ql_import_f)QL_G_trap_BotGetChatMessage;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS] = (ql_import_f)QL_G_trap_BotUpdateEntityItems;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotRemoveFromAvoidGoals;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotResetAvoidGoals;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_EMPTY_GOAL_STACK] = (ql_import_f)QL_G_trap_BotEmptyGoalStack;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_DUMP_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotDumpAvoidGoals;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_DUMP_GOAL_STACK] = (ql_import_f)QL_G_trap_BotDumpGoalStack;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_MAP_LOCATION_GOAL] = (ql_import_f)QL_G_trap_BotGetMapLocationGoal;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_AVOID_GOAL_TIME] = (ql_import_f)QL_G_trap_BotAvoidGoalTime;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INIT_LEVEL_ITEMS] = (ql_import_f)QL_G_trap_BotInitLevelItems;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_ITEM_WEIGHTS] = (ql_import_f)QL_G_trap_BotLoadItemWeights;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_ITEM_WEIGHTS] = (ql_import_f)QL_G_trap_BotFreeItemWeights;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC] = (ql_import_f)QL_G_trap_BotInterbreedGoalFuzzyLogic;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC] = (ql_import_f)QL_G_trap_BotSaveGoalFuzzyLogic;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC] = (ql_import_f)QL_G_trap_BotMutateGoalFuzzyLogic;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_GOAL_STATE] = (ql_import_f)QL_G_trap_BotAllocGoalState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_GOAL_STATE] = (ql_import_f)QL_G_trap_BotFreeGoalState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE] = (ql_import_f)QL_G_trap_BotResetMoveState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetAvoidReach;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetLastAvoidReach;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REACHABILITY_AREA] = (ql_import_f)QL_G_trap_BotReachabilityArea;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION] = (ql_import_f)QL_G_trap_BotPredictVisiblePosition;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_MOVE_STATE] = (ql_import_f)QL_G_trap_BotAllocMoveState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_MOVE_STATE] = (ql_import_f)QL_G_trap_BotFreeMoveState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE] = (ql_import_f)QL_G_trap_BotInitMoveState;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT] = (ql_import_f)QL_G_trap_BotAddAvoidSpot;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_GENERATE_MATCH_GUID] = (ql_import_f)QL_G_trap_GenerateMatchGuid;" in sv_game
	assert "Com_Memcpy( &ql_game_imports[G_QL_IMPORT_COMPAT_BASE], ql_game_compat_imports, sizeof( ql_game_compat_imports ) );" in sv_game
	assert "[BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT] = (ql_import_f)QL_G_trap_AAS_PredictClientMovement," in sv_game
	assert "[BOTLIB_EA_END_REGULAR] = (ql_import_f)QL_G_trap_EA_EndRegular," in sv_game
	assert "[BOTLIB_EA_GET_INPUT] = (ql_import_f)QL_G_trap_EA_GetInput," in sv_game
	assert "[BOTLIB_AI_EMPTY_GOAL_STACK] = (ql_import_f)QL_G_trap_BotEmptyGoalStack," in sv_game
	assert "[BOTLIB_AI_AVOID_GOAL_TIME] = (ql_import_f)QL_G_trap_BotAvoidGoalTime," in sv_game
	assert "[BOTLIB_AI_ALLOC_MOVE_STATE] = (ql_import_f)QL_G_trap_BotAllocMoveState," in sv_game
	assert "[BOTLIB_PC_LOAD_SOURCE] = (ql_import_f)QL_G_trap_PC_LoadSource," in sv_game

	for legacy_id, native_slot in (
		("BOTLIB_SETUP", "G_QL_IMPORT_BOTLIB_SETUP"),
		("BOTLIB_LIBVAR_SET", "G_QL_IMPORT_BOTLIB_LIBVAR_SET"),
		("BOTLIB_LIBVAR_GET", "G_QL_IMPORT_BOTLIB_LIBVAR_GET"),
		("BOTLIB_START_FRAME", "G_QL_IMPORT_BOTLIB_START_FRAME"),
		("BOTLIB_UPDATENTITY", "G_QL_IMPORT_BOTLIB_UPDATE_ENTITY"),
		("BOTLIB_TEST", "G_QL_IMPORT_BOTLIB_TEST"),
		("BOTLIB_AAS_TIME", "G_QL_IMPORT_BOTLIB_AAS_TIME"),
		("BOTLIB_AAS_PREDICT_ROUTE", "G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE"),
		("BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL", "G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL"),
		("BOTLIB_AAS_SWIMMING", "G_QL_IMPORT_BOTLIB_AAS_SWIMMING"),
		("BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT", "G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT"),
		("BOTLIB_EA_SAY", "G_QL_IMPORT_BOTLIB_EA_SAY"),
		("BOTLIB_EA_SAY_TEAM", "G_QL_IMPORT_BOTLIB_EA_SAY_TEAM"),
		("BOTLIB_EA_COMMAND", "G_QL_IMPORT_BOTLIB_EA_COMMAND"),
		("BOTLIB_EA_ACTION", "G_QL_IMPORT_BOTLIB_EA_ACTION"),
		("BOTLIB_EA_GESTURE", "G_QL_IMPORT_BOTLIB_EA_GESTURE"),
		("BOTLIB_EA_TALK", "G_QL_IMPORT_BOTLIB_EA_TALK"),
		("BOTLIB_EA_ATTACK", "G_QL_IMPORT_BOTLIB_EA_ATTACK"),
		("BOTLIB_EA_USE", "G_QL_IMPORT_BOTLIB_EA_USE"),
		("BOTLIB_EA_RESPAWN", "G_QL_IMPORT_BOTLIB_EA_RESPAWN"),
		("BOTLIB_EA_CROUCH", "G_QL_IMPORT_BOTLIB_EA_CROUCH"),
		("BOTLIB_EA_MOVE_UP", "G_QL_IMPORT_BOTLIB_EA_MOVE_UP"),
		("BOTLIB_EA_MOVE_DOWN", "G_QL_IMPORT_BOTLIB_EA_MOVE_DOWN"),
		("BOTLIB_EA_MOVE_FORWARD", "G_QL_IMPORT_BOTLIB_EA_MOVE_FORWARD"),
		("BOTLIB_EA_MOVE_BACK", "G_QL_IMPORT_BOTLIB_EA_MOVE_BACK"),
		("BOTLIB_EA_MOVE_LEFT", "G_QL_IMPORT_BOTLIB_EA_MOVE_LEFT"),
		("BOTLIB_EA_MOVE_RIGHT", "G_QL_IMPORT_BOTLIB_EA_MOVE_RIGHT"),
		("BOTLIB_EA_SELECT_WEAPON", "G_QL_IMPORT_BOTLIB_EA_SELECT_WEAPON"),
		("BOTLIB_EA_JUMP", "G_QL_IMPORT_BOTLIB_EA_JUMP"),
		("BOTLIB_EA_DELAYED_JUMP", "G_QL_IMPORT_BOTLIB_EA_DELAYED_JUMP"),
		("BOTLIB_EA_MOVE", "G_QL_IMPORT_BOTLIB_EA_MOVE"),
		("BOTLIB_EA_VIEW", "G_QL_IMPORT_BOTLIB_EA_VIEW"),
		("BOTLIB_EA_END_REGULAR", "G_QL_IMPORT_BOTLIB_EA_END_REGULAR"),
		("BOTLIB_EA_GET_INPUT", "G_QL_IMPORT_BOTLIB_EA_GET_INPUT"),
		("BOTLIB_EA_RESET_INPUT", "G_QL_IMPORT_BOTLIB_EA_RESET_INPUT"),
		("BOTLIB_AI_LOAD_CHARACTER", "G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER"),
		("BOTLIB_AI_FREE_CHARACTER", "G_QL_IMPORT_BOTLIB_AI_FREE_CHARACTER"),
		("BOTLIB_AI_CHARACTERISTIC_FLOAT", "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_FLOAT"),
		("BOTLIB_AI_CHARACTERISTIC_BFLOAT", "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT"),
		("BOTLIB_AI_CHARACTERISTIC_INTEGER", "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_INTEGER"),
		("BOTLIB_AI_CHARACTERISTIC_BINTEGER", "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BINTEGER"),
		("BOTLIB_AI_CHARACTERISTIC_STRING", "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING"),
		("BOTLIB_AI_ALLOC_CHAT_STATE", "G_QL_IMPORT_BOTLIB_AI_ALLOC_CHAT_STATE"),
		("BOTLIB_AI_FREE_CHAT_STATE", "G_QL_IMPORT_BOTLIB_AI_FREE_CHAT_STATE"),
		("BOTLIB_AI_QUEUE_CONSOLE_MESSAGE", "G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE"),
		("BOTLIB_AI_REMOVE_CONSOLE_MESSAGE", "G_QL_IMPORT_BOTLIB_AI_REMOVE_CONSOLE_MESSAGE"),
		("BOTLIB_AI_NEXT_CONSOLE_MESSAGE", "G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE"),
		("BOTLIB_AI_NUM_CONSOLE_MESSAGE", "G_QL_IMPORT_BOTLIB_AI_NUM_CONSOLE_MESSAGE"),
		("BOTLIB_AI_INITIAL_CHAT", "G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT"),
		("BOTLIB_AI_NUM_INITIAL_CHATS", "G_QL_IMPORT_BOTLIB_AI_NUM_INITIAL_CHATS"),
		("BOTLIB_AI_REPLY_CHAT", "G_QL_IMPORT_BOTLIB_AI_REPLY_CHAT"),
		("BOTLIB_AI_CHAT_LENGTH", "G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH"),
		("BOTLIB_AI_ENTER_CHAT", "G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT"),
		("BOTLIB_AI_GET_CHAT_MESSAGE", "G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE"),
		("BOTLIB_AI_STRING_CONTAINS", "G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS"),
		("BOTLIB_AI_REMOVE_FROM_AVOID_GOALS", "G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS"),
		("BOTLIB_AI_RESET_AVOID_GOALS", "G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS"),
		("BOTLIB_AI_EMPTY_GOAL_STACK", "G_QL_IMPORT_BOTLIB_AI_EMPTY_GOAL_STACK"),
		("BOTLIB_AI_DUMP_AVOID_GOALS", "G_QL_IMPORT_BOTLIB_AI_DUMP_AVOID_GOALS"),
		("BOTLIB_AI_DUMP_GOAL_STACK", "G_QL_IMPORT_BOTLIB_AI_DUMP_GOAL_STACK"),
		("BOTLIB_AI_GET_MAP_LOCATION_GOAL", "G_QL_IMPORT_BOTLIB_AI_GET_MAP_LOCATION_GOAL"),
		("BOTLIB_AI_AVOID_GOAL_TIME", "G_QL_IMPORT_BOTLIB_AI_AVOID_GOAL_TIME"),
		("BOTLIB_AI_INIT_LEVEL_ITEMS", "G_QL_IMPORT_BOTLIB_AI_INIT_LEVEL_ITEMS"),
		("BOTLIB_AI_UPDATE_ENTITY_ITEMS", "G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS"),
		("BOTLIB_AI_LOAD_ITEM_WEIGHTS", "G_QL_IMPORT_BOTLIB_AI_LOAD_ITEM_WEIGHTS"),
		("BOTLIB_AI_FREE_ITEM_WEIGHTS", "G_QL_IMPORT_BOTLIB_AI_FREE_ITEM_WEIGHTS"),
		("BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC", "G_QL_IMPORT_BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC"),
		("BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC", "G_QL_IMPORT_BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC"),
		("BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC", "G_QL_IMPORT_BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC"),
		("BOTLIB_AI_ALLOC_GOAL_STATE", "G_QL_IMPORT_BOTLIB_AI_ALLOC_GOAL_STATE"),
		("BOTLIB_AI_FREE_GOAL_STATE", "G_QL_IMPORT_BOTLIB_AI_FREE_GOAL_STATE"),
		("BOTLIB_AI_RESET_MOVE_STATE", "G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE"),
		("BOTLIB_AI_MOVE_TO_GOAL", "G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL"),
		("BOTLIB_AI_MOVE_IN_DIRECTION", "G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION"),
		("BOTLIB_AI_RESET_AVOID_REACH", "G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH"),
		("BOTLIB_AI_RESET_LAST_AVOID_REACH", "G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH"),
		("BOTLIB_AI_REACHABILITY_AREA", "G_QL_IMPORT_BOTLIB_AI_REACHABILITY_AREA"),
		("BOTLIB_AI_MOVEMENT_VIEW_TARGET", "G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET"),
		("BOTLIB_AI_PREDICT_VISIBLE_POSITION", "G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION"),
		("BOTLIB_AI_ALLOC_MOVE_STATE", "G_QL_IMPORT_BOTLIB_AI_ALLOC_MOVE_STATE"),
		("BOTLIB_AI_FREE_MOVE_STATE", "G_QL_IMPORT_BOTLIB_AI_FREE_MOVE_STATE"),
		("BOTLIB_AI_INIT_MOVE_STATE", "G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE"),
		("BOTLIB_AI_ADD_AVOID_SPOT", "G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT"),
	):
		assert f"case {legacy_id}: return {native_slot};" in syscall_map

	for compat_only_id in (
		"BOTLIB_PC_LOAD_SOURCE",
		"BOTLIB_PC_FREE_SOURCE",
		"BOTLIB_PC_READ_TOKEN",
		"BOTLIB_PC_SOURCE_FILE_AND_LINE",
	):
		assert f"case {compat_only_id}:" not in syscall_map

	assert "case BOTLIB_EA_WALK:" not in syscall_map
	assert "if ( arg >= 0 && arg < GAME_LEGACY_IMPORT_COUNT ) {" in syscall_map
	assert "return G_QL_IMPORT_COMPAT_BASE + arg;" in syscall_map
	assert "import = G_GetMappedImport( arg, stack );" in native_syscall
	assert "return G_InvokeImport( import, &stack[1] );" in native_syscall
	assert "G_GetDirectImport( G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS )" in game_draw_debug_areas
	assert "((void (QDECL *)( vec3_t, int, int ))import)( origin, enable, areanum );" in game_draw_debug_areas
	assert "G_GetDirectImport( G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS )" in game_draw_avoid_spots
	assert "((void (QDECL *)( int ))import)( movestate );" in game_draw_avoid_spots
	assert "botlib_export->ai.BotDrawDebugAreas( origin, enable, areanum );" in server_draw_debug_areas
	assert "botlib_export->ai.BotDrawAvoidSpots( movestate );" in server_draw_avoid_spots
	assert "botlib_export->ea.EA_Walk( client );" in ea_walk
	assert "(**(code **)(DAT_104b13ac + 0x13c))" in qagame_ghidra
	assert "(*(data_104b13ac + 0x140))(&data_105e3e40" in qagame_hlil
	assert "(**(code **)(DAT_104b13ac + 0x144))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x148))" in qagame_ghidra
	assert "(*(data_104b13ac + 0x14c))(arg1, data_1059cdac, data_105a27ac)" in qagame_hlil
	assert "(*(data_104b13ac + 0x150))(eax_7[0x657])" in qagame_hlil
	assert '(*(data_104b13ac + 0x158))(*(arg1 + 8), "what do you say?")' in qagame_hlil
	assert '(*(data_104b13ac + 0x15c))(*(arg1 + 8), "vtaunt")' in qagame_hlil
	assert "(*(data_104b13ac + 0x160))(*(arg4 + 8), 0x100000)" in qagame_hlil
	assert "(*(data_104b13ac + 0x164))(*(arg3 + 8))" in qagame_hlil
	assert "(*(data_104b13ac + 0x198))(*(arg1 + 8), *(arg1 + 0x1980))" in qagame_hlil
	assert "(*(data_104b13ac + 0x1a8))(*(ebx + 8), ebx + 0x1984)" in qagame_hlil
	assert "int32_t eax_3 = *(data_104b13ac + 0x1b0)" in qagame_hlil
	assert "(*(data_104b13ac + 0x1b4))(edi)" in qagame_hlil
	assert '(*(data_104b13ac + 0x3c))("bot_showAvoidSpots", &data_1007d0a8)' in qagame_hlil
	assert 'char const (* data_1008d9b4)[0x13] = data_100875ac {"bot_showAreaNumber"}' in qagame_hlil_cvars
	assert 'char const (* data_1008d9cc)[0xe] = data_1008759c {"bot_showAreas"}' in qagame_hlil_cvars
	assert 'char const (* data_1008d9e4)[0x13] = data_1007dc8c {"bot_showAvoidSpots"}' in qagame_hlil_cvars
	assert "(**(code **)(DAT_104b13ac + 0xd8))(fStack_ec);" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0xe0))(iVar1,0);" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x164))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x198))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1a8))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1b4))" in qagame_ghidra
	assert "(*(data_104b13ac + 0x1b8))(arg2, fconvert.s(fconvert.t(*(arg2 + 0x40))))" in qagame_hlil
	assert "(*(data_104b13ac + 0x1bc))(esi[0x656])" in qagame_hlil
	assert "(**(code **)(DAT_104b13ac + 0x1e0))(*(undefined4 *)(unaff_EBX + 0x1964),iStack_3d4)" in qagame_ghidra
	assert "int32_t eax_30 = *(edx_16 + 0x1f4)" in qagame_hlil
	assert "iVar2 = (**(code **)(DAT_104b13ac + 500))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1fc))(*(undefined4 *)(param_3 + 0x1964),0,1);" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x200))(*(undefined4 *)(unaff_EBX + 0x1964),local_10c,0x100);" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1f8))" not in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x204))" not in qagame_ghidra
	assert "(*(data_104b13ac + 0x1f8))" not in qagame_hlil
	assert "(*(data_104b13ac + 0x204))" not in qagame_hlil
	assert "(*(data_104b13ac + 0x1c4))(*(arg1 + 0x1958), 0x1b" in qagame_hlil
	assert "(*(data_104b13ac + 0x1cc))(*(arg1 + 0x1958), 0x17, 1, 0xfa0)" in qagame_hlil
	assert "(*(data_104b13ac + 0x1d0))(arg1[0x656], 1, &var_528, 0x90)" in qagame_hlil
	assert "(*(data_104b13ac + 0x228))(*(ebx + 0x1960), var_20)" in qagame_hlil
	assert "(*(data_104b13ac + 0x22c))(*(arg1 + 0x1960))" in qagame_hlil
	assert "(*(data_104b13ac + 0x238))(arg1[0x658])" in qagame_hlil
	assert "(*(data_104b13ac + 0x240))(arg1[0x658])" in qagame_hlil
	assert "(*(data_104b13ac + 0x27c))(ebp[0x658], &var_1b8)" in qagame_hlil
	assert "(*(data_104b13ac + 0x284))(*(*((var_108 << 2) + &data_105e2f00) + 0x1960)" in qagame_hlil
	assert "(*(data_104b13ac + 0x288))(*(*((esi << 2) + &data_105e2f00) + 0x1960), arg1)" in qagame_hlil
	assert "(*(data_104b13ac + 0x28c))(ebp[0x658], fconvert.s(float.t(1)))" in qagame_hlil
	assert "(*(data_104b13ac + 0x290))(arg3)" in qagame_hlil
	assert "(*(data_104b13ac + 0x294))(esi[0x658])" in qagame_hlil
	assert "(*(data_104b13ac + 0x298))(ecx_1)" in qagame_hlil
	assert "(*(eax_40 + 0x2b4))() != 0" in qagame_hlil
	assert "(*(ecx_17 + 0x2b8))()" in qagame_hlil
	assert "(*(data_104b13ac + 0x2bc))(esi[0x657])" in qagame_hlil
	assert "(*(data_104b13ac + 0x2c8))(*(arg1 + 0x1968), arg1 + 0x1338)" in qagame_hlil
	assert "(*(data_104b13ac + 0x2cc))(*(arg3 + 0x1968), *(arg3 + 0x1980), &var_2a8)" in qagame_hlil
	assert "(*(data_104b13ac + 0x2d0))(ebp[0x65a], &var_1b8)" in qagame_hlil
	assert "(*(data_104b13ac + 0x2d4))()" in qagame_hlil
	assert "(*(data_104b13ac + 0x2d8))(ebp[0x65a])" in qagame_hlil
	assert "(*(data_104b13ac + 0x2dc))(eax_8)" in qagame_hlil
	assert "(*(data_104b13ac + 0x2e0))(0x40, &var_104, &var_108, &var_10c, &var_110)" in qagame_hlil
	assert "(**(code **)(DAT_104b13ac + 0x1b8))()" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1c4))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1cc))(*(undefined4 *)(unaff_EBX + 0x1958),0x17,1,4000)" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1d0))(iVar5,0x28,auStack_49c,0x90)" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x290))(local_1bc)" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x27c))(piVar1[0x658],auStack_1b8)" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x2b4))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x2d0))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x2d4))()" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x2d8))" in qagame_ghidra
	assert "(**(code **)(iVar4 + 0x2b8))()" in qagame_ghidra
	assert "trap_BotLibStartFrame((float) time / 1000);" in bot_ai_start_frame
	assert "trap_BotLibUpdateEntity(i, NULL);" in bot_ai_start_frame
	assert 'trap_Cvar_Register(&bot_showAreaNumber, "bot_showAreaNumber", "0", CVAR_VM_CREATED);' in ai_main
	assert 'trap_Cvar_Register(&bot_showAreas, "bot_showAreas", "0", CVAR_VM_CREATED);' in ai_main
	assert 'trap_Cvar_Register(&bot_showAvoidSpots, "bot_showAvoidSpots", "0", CVAR_VM_CREATED);' in ai_main
	assert "trap_Cvar_Update(&bot_testsolid);" in bot_test_aas
	assert "trap_Cvar_Update(&bot_testclusters);" in bot_test_aas
	assert "trap_Cvar_Update(&bot_showAreas);" in bot_test_aas
	assert "trap_BotDrawDebugAreas(origin, bot_showAreas.integer, bot_showAreaNumber.integer);" in bot_test_aas
	assert "client = bot_showAvoidSpots.integer;" in bot_test_aas
	assert "if ( client >= 1 && client < MAX_CLIENTS ) {" in bot_test_aas
	assert "bs = botstates[client];" in bot_test_aas
	assert "trap_BotDrawAvoidSpots(bs->ms);" in bot_test_aas
	assert 'trap_Cvar_Set("bot_showAvoidSpots", "0");' in bot_test_aas
	assert bot_test_aas.index("trap_Cvar_Update(&bot_showAreas);") < bot_test_aas.index(
		"trap_BotDrawDebugAreas(origin, bot_showAreas.integer, bot_showAreaNumber.integer);"
	)
	assert bot_test_aas.index("trap_BotDrawDebugAreas") < bot_test_aas.index(
		"if (bot_testsolid.integer) {"
	)
	assert bot_test_aas.index("trap_BotDrawAvoidSpots(bs->ms);") < bot_test_aas.index(
		"if (bot_testsolid.integer) {"
	)
	assert "G_Import_Syscall( BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT" in predict_client_movement
	assert "QL_G_PASSFLOAT(frametime)" in predict_client_movement
	assert "G_Import_Syscall( BOTLIB_AI_GET_MAP_LOCATION_GOAL, name, goal );" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_AI_ENTER_CHAT, chatstate, client, sendto );" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_AI_GET_CHAT_MESSAGE, chatstate, buf, size);" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_AI_INIT_LEVEL_ITEMS );" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_AI_FREE_ITEM_WEIGHTS, goalstate );" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_AI_REACHABILITY_AREA, origin, testground );" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_AI_PREDICT_VISIBLE_POSITION, origin, areanum, goal, travelflags, target );" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_EA_END_REGULAR, client, QL_G_PASSFLOAT(thinktime) );" in ea_end_regular
	assert "temp = G_Import_Syscall( BOTLIB_AI_AVOID_GOAL_TIME, goalstate, number );" in bot_avoid_goal_time
	assert "return (*(float*)&temp);" in bot_avoid_goal_time


def test_qagame_factory_exists_native_tail_matches_retail_references() -> None:
	public_h = _read("src/code/game/g_public.h")
	bg_public = _read("src/code/game/bg_public.h")
	g_local = _read("src/code/game/g_local.h")
	g_main = _read("src/code/game/g_main.c")
	g_syscalls = _read("src/code/game/g_syscalls.c")
	g_cmds = _read("src/code/game/g_cmds.c")
	server_h = _read("src/code/server/server.h")
	sv_ccmds = _read("src/code/server/sv_ccmds.c")
	sv_game = _read("src/code/server/sv_game.c")
	ql_game_imports = _read("src/code/server/ql_game_imports.inc")
	aliases = _read("references/analysis/quakelive_symbol_aliases.json")
	qagame_hlil = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt"
	)
	qagame_ghidra = _read("references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c")
	engine_hlil_part05 = _read(
		"references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt"
	)
	engine_hlil_part07 = _read(
		"references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt"
	)

	factory_trap = _extract_block(g_syscalls, "qboolean trap_FactoryExists")
	guid_trap = _extract_block(g_syscalls, "void trap_GenerateMatchGuid")
	server_guid = _extract_block(sv_game, "static void SV_GenerateMatchGuid")
	server_guid_trap = _extract_block(sv_game, "static void QDECL QL_G_trap_GenerateMatchGuid")
	factory_vote = _extract_block(g_cmds, "static qboolean G_CallVoteFactoryExists")
	callvote = _extract_block(g_cmds, "void Cmd_CallVote_f")
	server_factory_exists = _extract_block(sv_ccmds, "qboolean SV_FactoryExists")
	server_trap = _extract_block(ql_game_imports, "static int QDECL QL_G_trap_FactoryExists")

	assert "#define\tGAME_MATCH_GUID_BUFFER_SIZE\t64" in public_h
	assert "G_QL_IMPORT_STEAM_AUTH_VALIDATE = 205," in public_h
	assert "G_QL_IMPORT_STEAM_STAT_ADD = 201," in public_h
	assert "G_QL_IMPORT_GENERATE_MATCH_GUID = 202," in public_h
	assert "G_QL_IMPORT_STEAM_UNLOCK_ACHIEVEMENT = 203," in public_h
	assert "G_QL_IMPORT_FACTORY_EXISTS = 206," in public_h
	assert "G_QL_IMPORT_COUNT = 207," in public_h
	assert "G_QL_IMPORT_COMPAT_BASE = G_QL_IMPORT_COUNT," in public_h
	assert "qboolean\ttrap_FactoryExists( const char *id );" in g_local
	assert "void\ttrap_GenerateMatchGuid( char *buffer, int bufferSize );" in g_local
	assert "char\t\t\trankMatchGuid[GAME_MATCH_GUID_BUFFER_SIZE];" in g_local
	assert "qboolean SV_FactoryExists( const char *id );" in server_h
	assert "return SV_FactoryFindById( id ) ? qtrue : qfalse;" in server_factory_exists
	assert "return SV_FactoryExists( id );" in server_trap
	assert "ql_game_imports[G_QL_IMPORT_FACTORY_EXISTS] = (ql_import_f)QL_G_trap_FactoryExists;" in sv_game

	assert "G_GetDirectImport( G_QL_IMPORT_FACTORY_EXISTS )" in factory_trap
	assert "return ((int (QDECL *)( const char * ))import)( id ) ? qtrue : qfalse;" in factory_trap
	assert "G_GetDirectImport( G_QL_IMPORT_GENERATE_MATCH_GUID )" in guid_trap
	assert "buffer[0] = '\\0';" in guid_trap
	assert "((void (QDECL *)( char *, int ))import)( buffer, bufferSize );" in guid_trap
	assert "SV_CreateSystemGuid( &guid )" in server_guid
	assert "SV_CreateFallbackGuid( &guid );" in server_guid
	assert '"CoCreateGuid"' in sv_game
	assert "SV_GenerateMatchGuid( buffer, bufferSize );" in server_guid_trap
	assert "bufferSize > GAME_MATCH_GUID_BUFFER_SIZE" in server_guid_trap
	assert "ql_game_imports[G_QL_IMPORT_GENERATE_MATCH_GUID] = (ql_import_f)QL_G_trap_GenerateMatchGuid;" in sv_game
	assert "trap_GetConfigstring( CS_MATCH_GUID, level.rankMatchGuid, sizeof( level.rankMatchGuid ) );" in g_main
	assert "trap_GenerateMatchGuid( level.rankMatchGuid, sizeof( level.rankMatchGuid ) );" in g_main
	assert "trap_SetConfigstring( CS_MATCH_GUID, matchGuidInfo );" in g_main
	assert "if ( !level.rankMatchGuid[0] ) {" in g_main
	assert "#ifdef Q3_VM" in factory_vote
	assert "return Factory_FindById( id ) ? qtrue : qfalse;" in factory_vote
	assert "#else" in factory_vote
	assert "return trap_FactoryExists( id );" in factory_vote
	assert callvote.index("if ( !G_CallVoteFactoryExists( arg3 ) ) {") < callvote.index(
		"factoryOverride = Factory_FindById( arg3 );"
	)

	assert "100429fe                              int32_t eax_79 = *(data_104b13ac + 0x338)" in qagame_hlil
	assert "10042a08                              var_898 = &var_850" in qagame_hlil
	assert "10042a09                              eax_80, edx_35 = eax_79(var_898)" in qagame_hlil
	assert "10042a16                              var_898 =" in qagame_hlil
	assert "Factory does not exist" in qagame_hlil
	assert "(iVar4 = (*(code *)DAT_104b13ac[0xce])(acStack_864), iVar4 != 0)" in qagame_ghidra
	assert 'uVar13 = CONCAT44(unaff_EDI,"print \\"Factory does not exist.\\n\\"");' in qagame_ghidra
	assert "004e2a20    int32_t sub_4e2a20(char* arg1)" in engine_hlil_part05
	assert "004e2a27  void* eax_1 = sub_45e760(arg1)" in engine_hlil_part05
	assert "0056d2b8  void* data_56d2b8 = sub_4e2a20" in engine_hlil_part07
	assert '"sub_45E760": "Factory_FindById"' in aliases
	assert '"sub_4E2A20": "SV_FactoryExists"' in aliases

	assert "004e27d0    int32_t sub_4e27d0(int32_t arg1)" in engine_hlil_part05
	assert "004e27e8  CoCreateGuid(&pguid)" in engine_hlil_part05
	assert "0056d2a8  void* data_56d2a8 = sub_4e27d0" in engine_hlil_part07
	assert '"sub_4E27D0": "SV_GenerateMatchGuid"' in aliases
	assert "(**(code **)(DAT_104b13ac + 0x328))(auStack_450,0x40);" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 100))(0x2c8,auStack_450);" in qagame_ghidra
	assert "#define CS_MATCH_GUID\t\t0x2C8" in bg_public
	assert "#define CS_WARMUP_READY\t\t0x2D1" in bg_public
	assert "trap_SetConfigstring( CS_MATCH_GUID, level.rankMatchGuid" not in g_main
	assert "trap_SetConfigstring( CS_WARMUP_READY, level.rankMatchGuid" not in g_main
