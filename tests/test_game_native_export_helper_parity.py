from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


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
	assert "static qboolean G_IsObjectiveFlagItemEntity( const gentity_t *ent, qboolean allowNeutralFlag ) {" in team_c
	assert "static qboolean G_IsOverloadObjectiveEntity( const gentity_t *ent ) {" in team_c
	assert "qboolean G_IsObjectiveEntity( int entNum ) {" in team_c
	assert "case GT_CTF:" in team_c
	assert "case GT_ATTACK_DEFEND:" in team_c
	assert "case GT_1FCTF:" in team_c
	assert "case GT_OBELISK:" in team_c
	assert "if ( ent->client && ent->target_ent && G_IsObjectiveFlagItemEntity( ent->target_ent, qtrue ) ) {" in team_c
	assert 'return G_IsOverloadObjectiveEntity( ent );' in team_c


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
