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
	assert "static ql_import_f ql_game_imports[GAME_NATIVE_IMPORT_COUNT];" in sv_game
	assert "Com_Memset( ql_game_imports, 0, sizeof( ql_game_imports ) );" in sv_game
	assert "Com_Memcpy( &ql_game_imports[G_QL_IMPORT_COMPAT_BASE], ql_game_compat_imports, sizeof( ql_game_compat_imports ) );" in sv_game
