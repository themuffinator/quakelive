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

	assert "GAME_NATIVE_EXPORT_COUNT" in public_h
	assert "static void *g_nativeExports[GAME_NATIVE_EXPORT_COUNT]" in game_main
	assert "return GAME_NATIVE_EXPORT_COUNT;" in vm_c
	assert "VM_NormalizeQbooleanArg( args[2] )" in vm_block
	assert "VM_NormalizeQbooleanResult" in vm_block


def test_native_loader_api_version_wiring_matches_retail_dllentry_contracts() -> None:
	sv_game = _read("src/code/server/sv_game.c")
	cl_cgame = _read("src/code/client/cl_cgame.c")
	game_public = _read("src/code/game/g_public.h")
	cgame_public = _read("src/code/cgame/cg_public.h")
	qagame_mapping = _read("docs/reverse-engineering/qagame-mapping.md")
	cgame_mapping = _read("docs/reverse-engineering/cgame-mapping.md")
	qvm_fallback_note = _read("docs/reverse-engineering/qcommon-vm-fallback-ownership-2026-04-10.md")

	assert "#define\tGAME_API_VERSION\t8" in game_public
	assert "#define\tGAME_NATIVE_API_VERSION\t10" in game_public
	assert "#define\tCGAME_IMPORT_API_VERSION\t4" in cgame_public
	assert "#define\tCGAME_NATIVE_API_VERSION\t8" in cgame_public
	assert 'VM_Create( "qagame", SV_GameSystemCalls, VMI_NATIVE, ql_game_imports, GAME_NATIVE_API_VERSION );' in sv_game
	assert 'return VM_Create( "qagame", SV_GameSystemCalls, interpret, ql_game_imports, GAME_API_VERSION );' in sv_game
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
	sv_game = _read("src/code/server/sv_game.c")

	assert "#define GAME_LEGACY_IMPORT_COUNT\t(G_RANK_REPORT_STR + 1)" in public_h
	assert "#define GAME_NATIVE_IMPORT_COUNT\tG_QL_IMPORT_TOTAL_COUNT" in public_h
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
	assert "G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL = 79," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_SWIMMING = 81," in public_h
	assert "G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE = 82," in public_h
	assert "G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS = 158," in public_h
	assert "static ql_import_f ql_game_imports[GAME_NATIVE_IMPORT_COUNT];" in sv_game
	assert "Com_Memset( ql_game_imports, 0, sizeof( ql_game_imports ) );" in sv_game
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
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL] = (ql_import_f)QL_G_trap_AAS_AlternativeRouteGoals;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_SWIMMING] = (ql_import_f)QL_G_trap_AAS_Swimming;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE] = (ql_import_f)QL_G_trap_AAS_PredictRoute;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS] = (ql_import_f)QL_G_trap_BotUpdateEntityItems;" in sv_game
	assert "Com_Memcpy( &ql_game_imports[G_QL_IMPORT_COMPAT_BASE], ql_game_compat_imports, sizeof( ql_game_compat_imports ) );" in sv_game
