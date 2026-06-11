from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
GAME_AI_DMQ3_H = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.h"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
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
QAGAME_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part01.txt"
)


SOURCE_OWNED_FUNCTIONS = (
	("1001f050", "FUN_1001f050", "BotDeathmatchAI", "void BotDeathmatchAI(bot_state_t *bs, float thinktime)", 1129),
	("1001f4c0", "FUN_1001f4c0", "BotSetEntityNumForGoal", "void BotSetEntityNumForGoal(bot_goal_t *goal, char *classname)", 185),
	("1001f580", "FUN_1001f580", "BotSetupDeathmatchAI", "void BotSetupDeathmatchAI(void)", 1079),
	("1001f9c0", "FUN_1001f9c0", "BotSelectTormentTarget", "int BotSelectTormentTarget(bot_state_t *bs, float maxDist)", 1262),
	("1001fec0", "FUN_1001fec0", "BotResolveTourPoint", "int BotResolveTourPoint(int currentEntnum, vec3_t origin, vec3_t targetOrigin)", 825),
	("10020980", "FUN_10020980", "BotAI_Print", "void BotAI_Print(int type, char *fmt, ...)", 298),
	("10020ac0", "FUN_10020ac0", "BotAI_Trace", "void BotAI_Trace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int passent, int contentmask)", 219),
	("10020ba0", "FUN_10020ba0", "BotAI_GetClientState", "int BotAI_GetClientState(int clientNum, playerState_t *state)", 54),
	("10020be0", "FUN_10020be0", "BotClientHasNoTargetFlag", "qboolean BotClientHasNoTargetFlag(int clientNum)", 46),
	("10020c10", "FUN_10020c10", "BotAcceptOffscreenEnemyCandidate", "qboolean BotAcceptOffscreenEnemyCandidate(bot_state_t *bs, int clientNum)", 341),
	("10020d70", "FUN_10020d70", "BotAI_GetEntityState", "int BotAI_GetEntityState(int entityNum, entityState_t *state)", 79),
	("10020dc0", "FUN_10020dc0", "BotAI_BotInitialChat", "void BotAI_BotInitialChat(bot_state_t *bs, char *type, ...)", 255),
	("10020ec0", "FUN_10020ec0", "BotCanSpawnTourPoint", "int BotCanSpawnTourPoint(void)", 61),
)


MAPPED_ONLY_FUNCTIONS = ()


SOURCE_HELPERS = {
	"BotDeathmatchAI": (
		GAME_AI_DMQ3,
		"void BotDeathmatchAI(bot_state_t *bs, float thinktime)",
		(
			"trap_Characteristic_String(bs->character, CHARACTERISTIC_GENDER, gender, sizeof(gender));",
			"trap_GetUserinfo(bs->client, userinfo, sizeof(userinfo));",
			'Info_SetValueForKey(userinfo, "sex", gender);',
			"trap_SetUserinfo(bs->client, userinfo);",
			'Com_sprintf(buf, sizeof(buf), "team %s", bs->settings.team);',
			"trap_EA_Command(bs->client, buf);",
			"trap_BotSetChatGender(bs->cs, CHAT_GENDERMALE);",
			"trap_BotSetChatName(bs->cs, name, bs->client);",
			"BotSetupAlternativeRouteGoals();",
			"BotCheckSnapshot(bs);",
			"BotCheckConsoleMessages(bs);",
			"BotTeamAI(bs);",
			"g_instaGib.integer && bs->ltgtype != LTG_INSTAGIB",
			"!bs->ordered && bs->enemy == -1",
			"AIEnter_InstaGib(bs);",
			'AIEnter_Seek_LTG(bs, "BotDeathmatchAI: no ai node");',
			'AIEnter_Stand(bs, "BotDeathmatchAI: chat enter game");',
			"for (i = 0; i < MAX_NODESWITCHES; i++)",
			"trap_BotDumpGoalStack(bs->gs);",
			"trap_BotDumpAvoidGoals(bs->gs);",
		),
	),
	"BotSetEntityNumForGoal": (
		GAME_AI_DMQ3,
		"void BotSetEntityNumForGoal(bot_goal_t *goal, char *classname)",
		(
			"ent = &g_entities[0];",
			"for (i = 0; i < level.num_entities; i++, ent++)",
			"if ( ent->classname && classname )",
			"if ( !Q_stricmp(ent->classname, classname) )",
			"continue;",
			"VectorSubtract(goal->origin, ent->s.origin, dir);",
			"VectorLengthSquared(dir) < Square(10)",
			"goal->entitynum = i;",
		),
	),
	"BotSetupDeathmatchAI": (
		GAME_AI_DMQ3,
		"void BotSetupDeathmatchAI(void)",
		(
			'trap_Cvar_VariableIntegerValue("g_gametype");',
			'trap_Cvar_VariableIntegerValue("sv_maxclients");',
			'trap_Cvar_Register(&bot_rocketjump, "bot_rocketjump", "1", 0);',
			'trap_Cvar_Register(&bot_nochat, "bot_nochat", "0", CVAR_CLOUD);',
			'trap_Cvar_Register(&bot_challenge, "bot_challenge", "0", CVAR_CLOUD);',
			'trap_Cvar_Register(&bot_predictobstacles, "bot_predictobstacles", "1", 0);',
			'trap_BotGetLevelItemGoal(-1, "Red Flag", &ctf_redflag)',
			'BotAI_Print(PRT_WARNING, "One Flag CTF without Neutral Flag\\n");',
			'BotAI_Print(PRT_WARNING, "Harvester without neutral obelisk\\n");',
			'BotSetEntityNumForGoal(&redobelisk, "team_redobelisk");',
			'BotSetEntityNumForGoal(&neutralobelisk, "team_neutralobelisk");',
			"for (ent = trap_AAS_NextBSPEntity(0); ent; ent = trap_AAS_NextBSPEntity(ent))",
			'trap_AAS_ValueForBSPEpairKey(ent, "model", model, sizeof(model))',
			"max_bspmodelindex = modelnum;",
			"BotInitWaypoints();",
		),
	),
	"BotTormentCandidateClientActive": (
		GAME_AI_DMQ3,
		"static qboolean BotTormentCandidateClientActive( int clientNum )",
		(
			"BotAI_GetClientState( clientNum, &ps )",
			"return ps.pm_type == PM_NORMAL;",
		),
	),
	"BotTormentCandidateAllowed": (
		GAME_AI_DMQ3,
		"static qboolean BotTormentCandidateAllowed( bot_state_t *bs, int clientNum, aas_entityinfo_t *entinfo )",
		(
			"clientNum == bs->client",
			"BotEntityInfo( clientNum, entinfo );",
			"if ( !entinfo->valid )",
			"g_entities[clientNum].r.svFlags & SVF_BOT",
		),
	),
	"BotTormentCandidateDistance": (
		GAME_AI_DMQ3,
		"static float BotTormentCandidateDistance( bot_state_t *bs, vec3_t origin )",
		(
			"VectorSubtract( bs->origin, origin, dir );",
			"return VectorLength( dir );",
		),
	),
	"BotTormentCandidateReachableArea": (
		GAME_AI_DMQ3,
		"static qboolean BotTormentCandidateReachableArea( bot_state_t *bs, int areanum )",
		(
			"areanum <= 0",
			"trap_AAS_AreaTravelTimeToGoalArea( bs->areanum, bs->origin, areanum,",
			"BOT_TORMENT_TRAVEL_FLAGS",
		),
	),
	"BotTormentCandidateTraceArea": (
		GAME_AI_DMQ3,
		"static int BotTormentCandidateTraceArea( vec3_t origin )",
		(
			"trap_AAS_PointReachabilityAreaIndex( origin );",
			"end[2] += BOT_TORMENT_TARGET_TRACE_UP;",
			"trap_AAS_TraceAreas( origin, end, areas, NULL, BOT_TORMENT_TARGET_MAX_AREAS );",
			"numareas <= 0 || !areas[0]",
			"return areas[0];",
		),
	),
	"BotAcceptTormentCandidateWithArea": (
		GAME_AI_DMQ3,
		"static qboolean BotAcceptTormentCandidateWithArea( bot_state_t *bs, int target,",
		(
			"dist = BotTormentCandidateDistance( bs, origin );",
			"if ( dist >= maxDist )",
			"if ( dist >= *bestDist )",
			"BotTormentCandidateReachableArea( bs, areanum )",
			"*bestTarget = target;",
		),
	),
	"BotAcceptReachableTormentCandidate": (
		GAME_AI_DMQ3,
		"static qboolean BotAcceptReachableTormentCandidate( bot_state_t *bs, int target,",
		(
			"areanum = BotPointAreaNum( entinfo->origin );",
			"BotAcceptTormentCandidateWithArea( bs, target, entinfo->origin, areanum,",
		),
	),
	"BotAcceptTracedTormentCandidate": (
		GAME_AI_DMQ3,
		"static qboolean BotAcceptTracedTormentCandidate( bot_state_t *bs, int target,",
		(
			"areanum = BotTormentCandidateTraceArea( entinfo->origin );",
			"BotAcceptTormentCandidateWithArea( bs, target, entinfo->origin, areanum,",
		),
	),
	"BotAcceptNearestTormentCandidate": (
		GAME_AI_DMQ3,
		"static qboolean BotAcceptNearestTormentCandidate( bot_state_t *bs, int target,",
		(
			"dist = BotTormentCandidateDistance( bs, entinfo->origin );",
			"if ( dist >= maxDist )",
			"if ( dist >= *bestDist )",
			"*bestTarget = target;",
		),
	),
	"BotSelectTormentTarget": (
		GAME_AI_DMQ3,
		"int BotSelectTormentTarget( bot_state_t *bs, float maxDist )",
		(
			"bestTarget = -1;",
			"bestDist = BOT_TORMENT_TARGET_MAX_DISTANCE;",
			"BotEntityVisible( bs->entitynum, bs->eye, bs->viewangles, 360, bs->enemy ) > 0",
			"BotAcceptReachableTormentCandidate( bs, bs->enemy, &entinfo, maxDist,",
			"for ( i = 0; i < MAX_CLIENTS; i++ )",
			"BotTormentCandidateAllowed( bs, i, &entinfo )",
			"BotTormentCandidateClientActive( entinfo.number )",
			"BotAcceptReachableTormentCandidate( bs, i, &entinfo, bestDist,",
			"if ( bestTarget == -1 )",
			"BotAcceptTracedTormentCandidate( bs, i, &entinfo, bestDist,",
			"BotAcceptNearestTormentCandidate( bs, i, &entinfo, bestDist,",
			"return bestTarget;",
		),
	),
	"BotIsTourPointEntity": (
		GAME_AI_DMQ3,
		"static qboolean BotIsTourPointEntity( gentity_t *ent )",
		(
			'ent->classname, "info_tour_point"',
			"!Q_stricmp",
		),
	),
	"BotIsTourPointTargetEntity": (
		GAME_AI_DMQ3,
		"static qboolean BotIsTourPointTargetEntity( gentity_t *ent )",
		(
			'ent->classname, "info_notnull"',
			"!Q_stricmp",
		),
	),
	"BotSetTourPointFloorOrigin": (
		GAME_AI_DMQ3,
		"static void BotSetTourPointFloorOrigin( gentity_t *tourPoint, vec3_t origin )",
		(
			"end[2] -= BOT_TOUR_POINT_FLOOR_DROP;",
			"BotAI_Trace( &trace, tourPoint->s.origin, NULL, NULL, end, 0, CONTENTS_SOLID );",
			"VectorCopy( trace.endpos, origin );",
			"origin[2] += BOT_TOUR_POINT_ORIGIN_Z_OFFSET;",
		),
	),
	"BotSetTourPointTargetOrigin": (
		GAME_AI_DMQ3,
		"static void BotSetTourPointTargetOrigin( gentity_t *tourPoint, vec3_t targetOrigin )",
		(
			"G_Find( target, FOFS( targetname ), tourPoint->target )",
			"BotIsTourPointTargetEntity( target )",
			"VectorCopy( target->s.origin, targetOrigin );",
		),
	),
	"BotResolveTourPoint": (
		GAME_AI_DMQ3,
		"int BotResolveTourPoint( int currentEntnum, vec3_t origin, vec3_t targetOrigin )",
		(
			"VectorClear( targetOrigin );",
			"currentEntnum >= MAX_CLIENTS && currentEntnum < MAX_GENTITIES",
			"G_Find( tourPoint, FOFS( targetname ), current->target )",
			"BotIsTourPointEntity( tourPoint )",
			"tourPoint == current",
			"BotSetTourPointFloorOrigin( tourPoint, origin );",
			"BotSetTourPointTargetOrigin( tourPoint, targetOrigin );",
			"G_Find( tourPoint, FOFS( classname ), \"info_tour_point\" )",
			"tourPoint->spawnflags & BOT_TOUR_POINT_START_FLAG",
			"return tourPoint->s.number;",
		),
	),
	"BotCanSpawnTourPoint": (
		GAME_AI_DMQ3,
		"int BotCanSpawnTourPoint( void )",
		(
			"ent = &g_entities[MAX_CLIENTS];",
			"for ( i = MAX_CLIENTS; i < ENTITYNUM_MAX_NORMAL; i++, ent++ )",
			"if ( !ent->inuse && ent->freetime + BOT_TOUR_POINT_REUSE_DELAY <= level.time )",
			"return qtrue;",
			"return qfalse;",
		),
	),
	"BotAI_Print": (
		GAME_AI_MAIN,
		"void QDECL BotAI_Print(int type, char *fmt, ...)",
		(
			"vsprintf(str, fmt, ap);",
			"case PRT_MESSAGE:",
			'G_Printf("%s", str);',
			'G_Printf( S_COLOR_YELLOW "Warning: %s", str );',
			'G_Printf( S_COLOR_RED "Error: %s", str );',
			'G_Error( S_COLOR_RED "Exit: %s", str );',
			'G_Printf( "unknown print type\\n" );',
		),
	),
	"BotAI_Trace": (
		GAME_AI_MAIN,
		"void BotAI_Trace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int passent, int contentmask)",
		(
			"trap_Trace(&trace, start, mins, maxs, end, passent, contentmask);",
			"bsptrace->allsolid = trace.allsolid;",
			"VectorCopy(trace.endpos, bsptrace->endpos);",
			"bsptrace->surface.value = trace.surfaceFlags;",
			"bsptrace->ent = trace.entityNum;",
			"bsptrace->contents = 0;",
		),
	),
	"BotAI_GetClientState": (
		GAME_AI_MAIN,
		"int BotAI_GetClientState( int clientNum, playerState_t *state )",
		(
			"ent = &g_entities[clientNum];",
			"if ( !ent->inuse )",
			"if ( !ent->client )",
			"memcpy( state, &ent->client->ps, sizeof(playerState_t) );",
		),
	),
	"BotClientHasNoTargetFlag": (
		GAME_AI_DMQ3,
		"static qboolean BotClientHasNoTargetFlag( int clientNum )",
		(
			"if ( clientNum < 0 || clientNum >= MAX_CLIENTS )",
			"ent = &g_entities[clientNum];",
			"if ( !ent->inuse || !ent->client )",
			"return ( ent->flags & FL_NOTARGET ) != 0;",
		),
	),
	"BotAcceptOffscreenEnemyCandidate": (
		GAME_AI_DMQ3,
		"static qboolean BotAcceptOffscreenEnemyCandidate( bot_state_t *bs, int clientNum )",
		(
			"clientNum >= BOT_OFFSCREEN_CLIENT_MASK_BITS",
			"if ( bs->enemy != -1 )",
			"BotWantsToRetreat( bs )",
			"BotWantsToChase( bs )",
			"BotHasBlockingOffscreenGoal( bs )",
			"bs->settings.skill < BOT_OFFSCREEN_ENEMY_MIN_SKILL",
			"bs->heardClientMask & ( 1u << clientNum )",
		),
	),
	"BotGoalBlocksOffscreenEnemyCandidate": (
		GAME_AI_DMQ3,
		"static qboolean BotGoalBlocksOffscreenEnemyCandidate( bot_goal_t *goal )",
		(
			"BotEntityInfo( goal->entitynum, &entinfo );",
			"if ( entinfo.type == ET_BEAM )",
			"entinfo.type == ET_MISSILE || entinfo.type == ET_MOVER",
			"entinfo.modelindex >= BOT_OFFSCREEN_GOAL_MIN_MODEL",
		),
	),
	"BotHasBlockingOffscreenGoal": (
		GAME_AI_DMQ3,
		"static qboolean BotHasBlockingOffscreenGoal( bot_state_t *bs )",
		(
			"trap_BotGetTopGoal( bs->gs, &goal )",
			"BotGoalBlocksOffscreenEnemyCandidate( &goal )",
			"trap_BotGetSecondGoal( bs->gs, &goal )",
		),
	),
	"BotAI_GetEntityState": (
		GAME_AI_MAIN,
		"int BotAI_GetEntityState( int entityNum, entityState_t *state )",
		(
			"memset( state, 0, sizeof(entityState_t) );",
			"if (!ent->inuse) return qfalse;",
			"if (!ent->r.linked) return qfalse;",
			"if (ent->r.svFlags & SVF_NOCLIENT) return qfalse;",
			"memcpy( state, &ent->s, sizeof(entityState_t) );",
		),
	),
	"BotAI_BotInitialChat": (
		GAME_AI_MAIN,
		"void QDECL BotAI_BotInitialChat( bot_state_t *bs, char *type, ... )",
		(
			"memset(vars, 0, sizeof(vars));",
			"va_start(ap, type);",
			"for (i = 0; i < MAX_MATCHVARIABLES; i++)",
			"mcontext = BotSynonymContext(bs);",
			"trap_BotInitialChat( bs->cs, type, mcontext, vars[0], vars[1], vars[2], vars[3], vars[4], vars[5], vars[6], vars[7] );",
		),
	),
}


HLIL_ENTRY_ANCHORS = (
	"1001f050    int32_t sub_1001f050(int32_t* arg1)",
	"1001f4c0    void sub_1001f4c0(float* arg1, char* arg2)",
	"1001f580    void sub_1001f580(int32_t arg1 @ esi, int32_t arg2 @ edi)",
	"1001f9c0    int32_t sub_1001f9c0(void* arg1, float arg2)",
	'1001fec0    int32_t __convention("regparm") sub_1001fec0(int32_t arg1, int32_t arg2, int32_t* arg3, int32_t arg4, int32_t* arg5)',
	"10020980    int32_t sub_10020980(int32_t arg1, int32_t arg2)",
	'10020ac0    int32_t __convention("regparm") sub_10020ac0(int32_t arg1, int32_t arg2, int32_t arg3, int32_t* arg4 @ esi, int32_t arg5, int32_t arg6, int32_t arg7)',
	'10020ba0    int32_t __convention("regparm") sub_10020ba0(int32_t arg1, int32_t arg2)',
	'10020be0    uint32_t __convention("regparm") sub_10020be0(int32_t arg1)',
	'10020c10    void __convention("regparm") sub_10020c10(int32_t arg1, int32_t arg2, void* arg3, char arg4)',
	'10020d70    int32_t __convention("regparm") sub_10020d70(int32_t arg1, int32_t arg2, int32_t arg3)',
	"10020dc0    int32_t sub_10020dc0(void* arg1, int32_t arg2, int32_t arg3)",
	"10020ec0    int32_t sub_10020ec0()",
)


HLIL_FLOW_ANCHORS = (
	"1001f0e2          sub_10070f30((*(data_104b13ac + 0x70))(arg1[2], &var_408, 0x400), &var_408,",
	"1001f1d8          sub_1001ee30()",
	"1001f21c          sub_1001eaf0(arg1)",
	"1001f25a      sub_1001deb0()",
	"1001f30c                  sub_10011900(arg1)",
	"1001f359                  sub_100133c0(arg1)",
	'1001f36d          sub_1000cb30(arg1, "BotDeathmatchAI: no ai node")',
	'1001f3da                  sub_1000b5b0("BotDeathmatchAI: chat enter game", arg1)',
	"1001f42d              (*(data_104b13ac + 0x240))(arg1[0x658])",
	"1001f445              (*(data_104b13ac + 0x23c))(arg1[0x658])",
	'1001f480              sub_10020980(3, "%s at %1.1f switched more than %…")',
	"1001f4c0    void sub_1001f4c0(float* arg1, char* arg2)",
	"1001f4ff                  if (eax_2 != 0)",
	"1001f56c      arg1[0xa] = edi",
	'1001f5e1  edx_1(0x105e3fa0, "bot_rocketjump", &data_1007d1d8, 0)',
	'1001f637  (*(data_104b13ac + 0x44))(0x105e3d20, "bot_nochat", &data_1007d0a8, 0x80000)',
	'1001f674  (*(data_104b13ac + 0x44))(0x105e3e80, "bot_challenge", &data_1007d0a8, 0x80000)',
	'1001f8bb      if (ecx_12(0xffffffff, var_8c, var_88_19) s< 0)',
	'1001f783          char* var_88_9 = "team_redobelisk"',
	"1001f902  int32_t edx_13 = *(data_104b13ac + 0x11c)",
	'1001f946          *(esp_6 - 0xc) = "model"',
	"1001f9a3  data_105e4140 = i_2",
	"100119af  int32_t eax_2 = sub_1001f9c0(arg1, fconvert.s(fconvert.t(500f)))",
	"1001f9e5  int32_t eax_2 = *(arg1 + 0x196c)",
	"1001fa20          sub_10018b20(*(arg1 + 8), arg1 + 0x1984, fconvert.s(fconvert.t(360f)), eax_2)",
	"1001fad0              if (eax_6 s> 0 && (*(data_104b13ac + 0x134))(*(arg1 + 0x1334), arg1 + 0x130c,",
	"1001fb65                  if (*(var_118 * 0x384 + 0x104b41e0) != 0)",
	"1001fb83                  if (var_378 == 0)",
	"1001fb8d                  if ((*(i - 0x48) & 8) == 0)",
	"1001fd0c                      int32_t eax_21 = (*(data_104b13ac + 0x10c))(&var_114)",
	"1001fd7b                          if ((*(edx_5 + 0x114))(&var_114, &var_3c, var_3b8_4, eax_21,",
	"1001fda9                          if ((*(data_104b13ac + 0x134))(*(arg1 + 0x1334), arg1 + 0x130c,",
	"1001fe74                          float var_388_4 = var_398_4",
	"1001fead  return result",
	"1001fee7  *arg5 = data_104b1438",
	"1001ff37      if (*(arg4 * 0x384 + 0x104b41e0) == 0)",
	"1001ff5c          eax_7, edx = sub_1006bfa0(esi, edx, 0x2c0, edi)",
	'1001ff74          char const* const ecx_3 = "info_tour_point"',
	"10020007                  char const* const edx_1 = ecx_4(&var_50, esi + 0x220, 0, 0, &var_18, 0, 1)",
	'1002006a                      edx_1 = "info_notnull"',
	'100200dc          eax_18, edx = sub_1006bfa0(esi, edx, 0x244, "info_tour_point")',
	"100200f4          if ((*(esi + 0x248) & 1) != 0)",
	'100201a0                  char const* const ecx_12 = "info_notnull"',
	"100209a9  vsprintf(&var_804, arg2, &arg_c)",
	'10020a8d      int32_t eax_9 = sub_10053140("unknown print type\\n")',
	"10020af5  (*(data_104b13ac + 0x80))(&var_44, arg5, arg3, arg2)",
	"10020bcc          __builtin_memcpy(dest: arg2, src: eax_2, n: 0x250)",
	"10020bfe  if (*(arg1 * 0x384 + 0x104b41e0) != 0 && *(arg1 * 0x384 + &data_104b41dc) != 0)",
	"10019729                                              sub_10020c10(eax_17, edx_7, esi, i.b)",
	"10020c2e  if (*(arg3 + 0x196c) == 0xffffffff)",
	"10020c48      st0_1, eax_3 = sub_10017470(arg3)",
	"10020c51          st0_2, eax_4 = sub_10017620(arg3)",
	"10020c79              if ((*(data_104b13ac + 0x248))(*(arg3 + 0x1960), &var_138) == 0)",
	"10020cd8                  if ((*(data_104b13ac + 0x24c))(*(arg3 + 0x1960), &var_138) == 0)",
	"10020d2c                      if (not(4f f> *(arg3 + 0x12c0)))",
	"10020d89  memset(arg3, 0, 0xec)",
	"10020dba  __builtin_memcpy(dest: arg3, src: arg1 * 0x384 + &data_104b3fa0, n: 0xec)",
	"10020ebe  return (*(data_104b13ac + 0x1ec))(*(arg1 + 0x1964), arg2, eax_1, s_2, s, var_3c, var_38,",
	"10020eca  int32_t i = 0x40",
	"10020ee1      if (*(ecx - 0x1c) == 0 && *ecx + 0x7d0 s<= data_105dce5c)",
	"10020ef0  while (i s< 0x3fe)",
	"10021060      if (data_105a5ecc != 0 && sub_10020ec0() != 0)",
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


def test_qagame_ai_dmq3_deathmatch_setup_aliases_metadata_and_source_are_pinned() -> None:
	sources = {
		GAME_AI_DMQ3: _read(GAME_AI_DMQ3),
		GAME_AI_MAIN: _read(GAME_AI_MAIN),
	}
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in SOURCE_OWNED_FUNCTIONS + MAPPED_ONLY_FUNCTIONS:
		assert aliases[raw_name] == normalized_name
		assert aliases[f"sub_{address}"] == normalized_name

		row = function_rows[address]
		assert row["name"] == raw_name
		assert int(row["size"]) == size
		assert row["thunk"] == "0"

		symbol = symbol_map[f"0x{address}"]
		assert symbol["raw_name"] == raw_name
		assert symbol["normalized_name"] == normalized_name
		assert symbol["status"] == "matched"
		assert symbol["signature"] == signature

	for normalized_name in ("BotSetEntityNumForGoal",):
		symbol = symbol_map["0x1001f4c0"]
		assert "skips exact classname matches" in symbol["comment"]
		assert "absent or non-matching classnames" in symbol["comment"]

	for normalized_name, (path, source_signature, source_anchors) in SOURCE_HELPERS.items():
		block = _extract_function_block(sources[path], source_signature)
		for anchor in source_anchors:
			assert anchor in block, normalized_name

	assert "int BotResolveTourPoint(int currentEntnum, vec3_t origin, vec3_t targetOrigin);" in _read(GAME_AI_DMQ3_H)
	assert "int BotSelectTormentTarget(bot_state_t *bs, float maxDist);" in _read(GAME_AI_DMQ3_H)
	assert "int BotCanSpawnTourPoint(void);" in _read(GAME_AI_DMQ3_H)


def test_qagame_ai_dmq3_deathmatch_setup_hlil_and_import_wiring_are_pinned() -> None:
	ai_dmq3 = _read(GAME_AI_DMQ3)
	ai_main = _read(GAME_AI_MAIN)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	hlil = _read(QAGAME_HLIL_PART01)

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_FLOW_ANCHORS:
		assert expected in hlil

	for expected in (
		"G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE = 11,",
		"G_QL_IMPORT_CVAR_REGISTER = 17,",
		"G_QL_IMPORT_GET_USERINFO = 28,",
		"G_QL_IMPORT_SET_USERINFO = 29,",
		"G_QL_IMPORT_TRACE = 32,",
		"G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY = 71,",
		"G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY = 72,",
		"G_QL_IMPORT_BOTLIB_EA_COMMAND = 87,",
		"G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING = 116,",
		"G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER = 135,",
		"G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME = 136,",
		"G_QL_IMPORT_BOTLIB_AI_DUMP_AVOID_GOALS = 143,",
		"G_QL_IMPORT_BOTLIB_AI_DUMP_GOAL_STACK = 144,",
		"G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL = 146,",
		"G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL = 147,",
		"G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL = 154,",
	):
		assert expected in game_public

	for expected in (
		"case G_CVAR_VARIABLE_INTEGER_VALUE: return G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE;",
		"case G_CVAR_REGISTER: return G_QL_IMPORT_CVAR_REGISTER;",
		"case G_GET_USERINFO: return G_QL_IMPORT_GET_USERINFO;",
		"case G_SET_USERINFO: return G_QL_IMPORT_SET_USERINFO;",
		"case G_TRACE: return G_QL_IMPORT_TRACE;",
		"case BOTLIB_EA_COMMAND: return G_QL_IMPORT_BOTLIB_EA_COMMAND;",
		"case BOTLIB_AI_CHARACTERISTIC_STRING: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING;",
		"case BOTLIB_AI_SET_CHAT_GENDER: return G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER;",
		"case BOTLIB_AI_SET_CHAT_NAME: return G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME;",
		"case BOTLIB_AI_DUMP_AVOID_GOALS: return G_QL_IMPORT_BOTLIB_AI_DUMP_AVOID_GOALS;",
		"case BOTLIB_AI_DUMP_GOAL_STACK: return G_QL_IMPORT_BOTLIB_AI_DUMP_GOAL_STACK;",
		"case BOTLIB_AI_GET_TOP_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL;",
		"case BOTLIB_AI_GET_SECOND_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL;",
		"case BOTLIB_AI_GET_LEVEL_ITEM_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL;",
		"return syscall( G_CVAR_VARIABLE_INTEGER_VALUE, var_name );",
		"syscall( G_CVAR_REGISTER, cvar, var_name, value, flags );",
		"syscall( G_GET_USERINFO, num, buffer, bufferSize );",
		"syscall( G_SET_USERINFO, num, buffer );",
		"syscall( G_TRACE, results, start, mins, maxs, end, passEntityNum, contentmask );",
		"syscall( BOTLIB_EA_COMMAND, client, command );",
		"syscall( BOTLIB_AI_CHARACTERISTIC_STRING, character, index, buf, size );",
		"syscall( BOTLIB_AI_SET_CHAT_GENDER, chatstate, gender );",
		"syscall( BOTLIB_AI_SET_CHAT_NAME, chatstate, name, client );",
		"syscall( BOTLIB_AI_DUMP_AVOID_GOALS, goalstate );",
		"syscall( BOTLIB_AI_DUMP_GOAL_STACK, goalstate );",
		"return syscall( BOTLIB_AI_GET_TOP_GOAL, goalstate, goal );",
		"return syscall( BOTLIB_AI_GET_SECOND_GOAL, goalstate, goal );",
		"return syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );",
	):
		assert expected in game_syscalls

	for expected in (
		"[G_CVAR_REGISTER] = (ql_import_f)QL_G_trap_Cvar_Register,",
		"[G_CVAR_VARIABLE_INTEGER_VALUE] = (ql_import_f)QL_G_trap_Cvar_VariableIntegerValue,",
		"[G_GET_USERINFO] = (ql_import_f)QL_G_trap_GetUserinfo,",
		"[G_SET_USERINFO] = (ql_import_f)QL_G_trap_SetUserinfo,",
		"[G_TRACE] = (ql_import_f)QL_G_trap_Trace,",
		"[BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command,",
		"[BOTLIB_AI_CHARACTERISTIC_STRING] = (ql_import_f)QL_G_trap_Characteristic_String,",
		"[BOTLIB_AI_SET_CHAT_GENDER] = (ql_import_f)QL_G_trap_BotSetChatGender,",
		"[BOTLIB_AI_SET_CHAT_NAME] = (ql_import_f)QL_G_trap_BotSetChatName,",
		"[BOTLIB_AI_DUMP_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotDumpAvoidGoals,",
		"[BOTLIB_AI_DUMP_GOAL_STACK] = (ql_import_f)QL_G_trap_BotDumpGoalStack,",
		"[BOTLIB_AI_GET_TOP_GOAL] = (ql_import_f)QL_G_trap_BotGetTopGoal,",
		"[BOTLIB_AI_GET_SECOND_GOAL] = (ql_import_f)QL_G_trap_BotGetSecondGoal,",
		"[BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal,",
		"ql_game_imports[G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE] = (ql_import_f)QL_G_trap_Cvar_VariableIntegerValue;",
		"ql_game_imports[G_QL_IMPORT_CVAR_REGISTER] = (ql_import_f)QL_G_trap_Cvar_Register;",
		"ql_game_imports[G_QL_IMPORT_GET_USERINFO] = (ql_import_f)QL_G_trap_GetUserinfo;",
		"ql_game_imports[G_QL_IMPORT_SET_USERINFO] = (ql_import_f)QL_G_trap_SetUserinfo;",
		"ql_game_imports[G_QL_IMPORT_TRACE] = (ql_import_f)QL_G_trap_Trace;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING] = (ql_import_f)QL_G_trap_Characteristic_String;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER] = (ql_import_f)QL_G_trap_BotSetChatGender;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME] = (ql_import_f)QL_G_trap_BotSetChatName;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_DUMP_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotDumpAvoidGoals;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_DUMP_GOAL_STACK] = (ql_import_f)QL_G_trap_BotDumpGoalStack;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL] = (ql_import_f)QL_G_trap_BotGetTopGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL] = (ql_import_f)QL_G_trap_BotGetSecondGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal;",
	):
		assert expected in server_game

	for expected in (
		"return G_Import_Syscall( G_CVAR_VARIABLE_INTEGER_VALUE, var_name );",
		"G_Import_Syscall( G_CVAR_REGISTER, cvar, var_name, value, flags );",
		"G_Import_Syscall( G_GET_USERINFO, num, buffer, bufferSize );",
		"G_Import_Syscall( G_SET_USERINFO, num, buffer );",
		"G_Import_Syscall( G_TRACE, results, start, mins, maxs, end, passEntityNum, contentmask );",
		"G_Import_Syscall( BOTLIB_EA_COMMAND, client, command );",
		"G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_STRING, character, index, buf, size );",
		"G_Import_Syscall( BOTLIB_AI_SET_CHAT_GENDER, chatstate, gender );",
		"G_Import_Syscall( BOTLIB_AI_SET_CHAT_NAME, chatstate, name, client );",
		"G_Import_Syscall( BOTLIB_AI_DUMP_AVOID_GOALS, goalstate );",
		"G_Import_Syscall( BOTLIB_AI_DUMP_GOAL_STACK, goalstate );",
		"return G_Import_Syscall( BOTLIB_AI_GET_TOP_GOAL, goalstate, goal );",
		"return G_Import_Syscall( BOTLIB_AI_GET_SECOND_GOAL, goalstate, goal );",
		"return G_Import_Syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_Characteristic_String(bs->character, CHARACTERISTIC_GENDER, gender, sizeof(gender));",
		"trap_EA_Command(bs->client, buf);",
		"trap_BotSetChatGender(bs->cs, CHAT_GENDERMALE);",
		"trap_BotSetChatName(bs->cs, name, bs->client);",
		"trap_BotDumpGoalStack(bs->gs);",
		"trap_BotDumpAvoidGoals(bs->gs);",
		"trap_BotGetTopGoal( bs->gs, &goal )",
		"trap_BotGetSecondGoal( bs->gs, &goal )",
		"trap_BotGetLevelItemGoal(-1, \"Red Flag\", &ctf_redflag)",
		"trap_AAS_NextBSPEntity(ent)",
		"trap_AAS_ValueForBSPEpairKey(ent, \"model\", model, sizeof(model))",
	):
		assert expected in ai_dmq3

	for expected in (
		"trap_Trace(&trace, start, mins, maxs, end, passent, contentmask);",
		"trap_BotInitialChat( bs->cs, type, mcontext, vars[0], vars[1], vars[2], vars[3], vars[4], vars[5], vars[6], vars[7] );",
	):
		assert expected in ai_main
