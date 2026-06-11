from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
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


AI_DMQ3_ACTIVATE_OBSTACLE_FUNCTIONS = (
	("1001bcd0", "FUN_1001bcd0", "BotFuncButtonActivateGoal", "qboolean BotFuncButtonActivateGoal(bot_state_t *bs, int bspent, bot_activategoal_t *activategoal)", 2257),
	("1001c5b0", "FUN_1001c5b0", "BotFuncDoorActivateGoal", "int BotFuncDoorActivateGoal(bot_state_t *bs, int bspent, bot_activategoal_t *activategoal)", 364),
	("1001c720", "FUN_1001c720", "BotTriggerMultipleActivateGoal", "int BotTriggerMultipleActivateGoal(bot_state_t *bs, int bspent, bot_activategoal_t *activategoal)", 531),
	("1001c940", "FUN_1001c940", "BotPopFromActivateGoalStack", "int BotPopFromActivateGoalStack(bot_state_t *bs)", 151),
	("1001c9e0", "FUN_1001c9e0", "BotPushOntoActivateGoalStack", "int BotPushOntoActivateGoalStack(bot_state_t *bs, bot_activategoal_t *activategoal)", 463),
	("1001cbb0", "FUN_1001cbb0", "BotClearActivateGoalStack", "void BotClearActivateGoalStack(bot_state_t *bs)", 166),
	("1001cc60", "FUN_1001cc60", "BotEnableActivateGoalAreas", "void BotEnableActivateGoalAreas(bot_activategoal_t *activategoal, int enable)", 88),
	("1001ccc0", "FUN_1001ccc0", "BotIsGoingToActivateEntity", "int BotIsGoingToActivateEntity(bot_state_t *bs, int entitynum)", 110),
	("1001cd40", "FUN_1001cd40", "BotGetActivateGoal", "int BotGetActivateGoal(bot_state_t *bs, int entitynum, bot_activategoal_t *activategoal)", 2422),
	("1001d6d0", "FUN_1001d6d0", "BotGoForActivateGoal", "int BotGoForActivateGoal(bot_state_t *bs, bot_activategoal_t *activategoal)", 310),
	("1001d810", "FUN_1001d810", "BotRandomMove", "void BotRandomMove(bot_state_t *bs, bot_moveresult_t *moveresult)", 323),
	("1001d960", "FUN_1001d960", "BotAIBlocked", "void BotAIBlocked(bot_state_t *bs, bot_moveresult_t *moveresult, int activate)", 897),
	("1001dcf0", "FUN_1001dcf0", "BotAIPredictObstacles", "int BotAIPredictObstacles(bot_state_t *bs, bot_goal_t *goal)", 434),
	("1001deb0", "FUN_1001deb0", "BotCheckConsoleMessages", "void BotCheckConsoleMessages(bot_state_t *bs)", 1357),
	("1001e400", "FUN_1001e400", "BotCheckForProxMines", "void BotCheckForProxMines(bot_state_t *bs, entityState_t *state)", 183),
	("1001e4c0", "FUN_1001e4c0", "BotCheckEvents", "void BotCheckEvents(bot_state_t *bs, entityState_t *state)", 1421),
	("1001eaf0", "FUN_1001eaf0", "BotCheckSnapshot", "void BotCheckSnapshot(bot_state_t *bs)", 446),
	("1001ecb0", "FUN_1001ecb0", "BotAlternateRoute", "bot_goal_t *BotAlternateRoute(bot_state_t *bs, bot_goal_t *goal)", 123),
	("1001ed30", "FUN_1001ed30", "BotGetAlternateRouteGoal", "int BotGetAlternateRouteGoal(bot_state_t *bs, int base)", 245),
	("1001ee30", "FUN_1001ee30", "BotSetupAlternativeRouteGoals", "void BotSetupAlternativeRouteGoals(void)", 541),
)


SOURCE_HELPERS = {
	"BotFuncButtonActivateGoal": (
		"int BotFuncButtonActivateGoal(bot_state_t *bs, int bspent, bot_activategoal_t *activategoal)",
		(
			'trap_AAS_ValueForBSPEpairKey(bspent, "model", model, sizeof(model));',
			'trap_AAS_FloatForBSPEpairKey(bspent, "lip", &lip);',
			'trap_AAS_FloatForBSPEpairKey(bspent, "angle", &angle);',
			"BotSetMovedir(angles, movedir);",
			'trap_AAS_FloatForBSPEpairKey(bspent, "health", &health);',
			"activategoal->shoot = qtrue;",
			"trap_AAS_PresenceTypeBoundingBox(PRESENCE_CROUCH, bboxmins, bboxmaxs);",
			"trap_AAS_TraceAreas(start, end, areas, points, 10);",
			"trap_AAS_AreaReachability(areas[i])",
		),
	),
	"BotFuncDoorActivateGoal": (
		"int BotFuncDoorActivateGoal(bot_state_t *bs, int bspent, bot_activategoal_t *activategoal)",
		(
			'trap_AAS_ValueForBSPEpairKey(bspent, "model", model, sizeof(model));',
			"BotModelMinsMaxs(modelindex, ET_MOVER, 0, mins, maxs);",
			"activategoal->shoot = qtrue;",
			"VectorCopy(bs->origin, activategoal->goal.origin);",
			"VectorSet(activategoal->goal.mins, -8, -8, -8);",
		),
	),
	"BotTriggerMultipleActivateGoal": (
		"int BotTriggerMultipleActivateGoal(bot_state_t *bs, int bspent, bot_activategoal_t *activategoal)",
		(
			'trap_AAS_ValueForBSPEpairKey(bspent, "model", model, sizeof(model));',
			"BotModelMinsMaxs(modelindex, 0, CONTENTS_TRIGGER, mins, maxs);",
			"trap_AAS_TraceAreas(start, end, areas, NULL, 10);",
			"trap_AAS_AreaReachability(areas[i])",
			"activategoal->shoot = qfalse;",
		),
	),
	"BotPopFromActivateGoalStack": (
		"int BotPopFromActivateGoalStack(bot_state_t *bs)",
		(
			"if (!bs->activatestack)",
			"BotEnableActivateGoalAreas(bs->activatestack, qtrue);",
			"bs->activatestack->inuse = qfalse;",
			"bs->activatestack->justused_time = FloatTime();",
			"bs->activatestack = bs->activatestack->next;",
		),
	),
	"BotPushOntoActivateGoalStack": (
		"int BotPushOntoActivateGoalStack(bot_state_t *bs, bot_activategoal_t *activategoal)",
		(
			"for (i = 0; i < MAX_ACTIVATESTACK; i++)",
			"besttime = bs->activategoalheap[i].justused_time;",
			"memcpy(&bs->activategoalheap[best], activategoal, sizeof(bot_activategoal_t));",
			"bs->activategoalheap[best].next = bs->activatestack;",
			"bs->activatestack = &bs->activategoalheap[best];",
		),
	),
	"BotClearActivateGoalStack": (
		"void BotClearActivateGoalStack(bot_state_t *bs)",
		(
			"while(bs->activatestack)",
			"BotPopFromActivateGoalStack(bs);",
		),
	),
	"BotEnableActivateGoalAreas": (
		"void BotEnableActivateGoalAreas(bot_activategoal_t *activategoal, int enable)",
		(
			"if (activategoal->areasdisabled == !enable)",
			"for (i = 0; i < activategoal->numareas; i++)",
			"trap_AAS_EnableRoutingArea( activategoal->areas[i], enable );",
			"activategoal->areasdisabled = !enable;",
		),
	),
	"BotIsGoingToActivateEntity": (
		"int BotIsGoingToActivateEntity(bot_state_t *bs, int entitynum)",
		(
			"for (a = bs->activatestack; a; a = a->next)",
			"a->goal.entitynum == entitynum",
			"for (i = 0; i < MAX_ACTIVATESTACK; i++)",
			"bs->activategoalheap[i].justused_time > FloatTime() - 2",
		),
	),
	"BotGetActivateGoal": (
		"int BotGetActivateGoal(bot_state_t *bs, int entitynum, bot_activategoal_t *activategoal)",
		(
			'Com_sprintf(model, sizeof( model ), "*%d", entinfo.modelindex);',
			"for (ent = trap_AAS_NextBSPEntity(0); ent; ent = trap_AAS_NextBSPEntity(ent))",
			'trap_AAS_ValueForBSPEpairKey(ent, "model", tmpmodel, sizeof(tmpmodel))',
			'"func_door"',
			'"func_button"',
			'"trigger_multiple"',
			'"func_timer"',
			'"target_relay"',
			'"target_delay"',
			"BotFuncDoorActivateGoal(bs, ent, activategoal);",
			"BotFuncButtonActivateGoal(bs, ent, activategoal)",
			"BotTriggerMultipleActivateGoal(bs, ent, activategoal)",
			"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, activategoal->goal.areanum, bs->tfl);",
		),
	),
	"BotGoForActivateGoal": (
		"int BotGoForActivateGoal(bot_state_t *bs, bot_activategoal_t *activategoal)",
		(
			"activategoal->inuse = qtrue;",
			"activategoal->start_time = FloatTime();",
			"BotEntityInfo(activategoal->goal.entitynum, &activateinfo);",
			"BotPushOntoActivateGoalStack(bs, activategoal)",
			'AIEnter_Seek_ActivateEntity(bs, "BotGoForActivateGoal");',
			"BotEnableActivateGoalAreas(activategoal, qtrue);",
		),
	),
	"BotRandomMove": (
		"void BotRandomMove(bot_state_t *bs, bot_moveresult_t *moveresult)",
		(
			"random() * 360",
			"AngleVectors(angles, dir, NULL, NULL);",
			"trap_BotMoveInDirection(bs->ms, dir, 400, MOVE_WALK);",
			"moveresult->failure = qfalse;",
			"VectorCopy(dir, moveresult->movedir);",
		),
	),
	"BotAIBlocked": (
		"void BotAIBlocked(bot_state_t *bs, bot_moveresult_t *moveresult, int activate)",
		(
			"moveresult->type == RESULTTYPE_INSOLIDAREA",
			"BotGetActivateGoal(bs, entinfo.number, &activategoal);",
			"BotGoForActivateGoal(bs, &activategoal);",
			"trap_AAS_AreaReachability(bs->areanum)",
			"trap_BotMoveInDirection(bs->ms, sideward, 400, movetype)",
			"bs->flags ^= BFL_AVOIDRIGHT;",
			"bs->ainode == AINode_Seek_NBG",
		),
	),
	"BotAIPredictObstacles": (
		"int BotAIPredictObstacles(bot_state_t *bs, bot_goal_t *goal)",
		(
			"if (!bot_predictobstacles.integer)",
			"trap_AAS_PredictRoute(&route, bs->areanum, bs->origin,",
			"RSE_USETRAVELTYPE|RSE_ENTERCONTENTS",
			"AREACONTENTS_MOVER",
			"TFL_BRIDGE",
			"BotGetActivateGoal(bs, entitynum, &activategoal);",
			"BotGoForActivateGoal(bs, &activategoal);",
			"BotEnableActivateGoalAreas(&activategoal, qtrue);",
		),
	),
	"BotCheckConsoleMessages": (
		"void BotCheckConsoleMessages(bot_state_t *bs)",
		(
			"ClientName(bs->client, botname, sizeof(botname));",
			"trap_BotNextConsoleMessage(bs->cs, &m)",
			"trap_BotNumConsoleMessages(bs->cs)",
			"trap_BotFindMatch(m.message, &match, MTCONTEXT_REPLYCHAT)",
			"trap_BotMatchVariable(&match, NETNAME, netname, sizeof(netname));",
			"trap_UnifyWhiteSpaces(ptr);",
			"trap_BotReplaceSynonyms(ptr, context);",
			"BotMatchMessage(bs, m.message)",
			"trap_BotReplyChat(bs->cs, message, context, CONTEXT_REPLY,",
			"trap_BotRemoveConsoleMessage(bs->cs, handle);",
		),
	),
	"BotCheckForProxMines": (
		"void BotCheckForProxMines(bot_state_t *bs, entityState_t *state)",
		(
			"state->eType != ET_MISSILE || state->weapon != WP_PROX_LAUNCHER",
			"state->generic1 == BotTeam(bs)",
			"bs->inventory[INVENTORY_PLASMAGUN] > 0 && bs->inventory[INVENTORY_CELLS] > 0",
			"trap_BotAddAvoidSpot(bs->ms, state->pos.trBase, 160, AVOID_ALWAYS);",
			"bs->proxmines[bs->numproxmines] = state->number;",
		),
	),
	"BotCheckEvents": (
		"void BotCheckEvents(bot_state_t *bs, entityState_t *state)",
		(
			"bs->entityeventTime[state->number] == g_entities[state->number].eventTime",
			"bs->heardClientMask = 0;",
			"event = (state->eType - ET_EVENTS) & ~EV_EVENT_BITS;",
			"case EV_OBITUARY:",
			"if (gametype == GT_1FCTF)",
			"case EV_GLOBAL_SOUND:",
			"BotDontAvoid(bs, \"Kamikaze\");",
			"BotGoForPowerups(bs);",
			"case EV_GLOBAL_TEAM_SOUND:",
			"case EV_PLAYER_TELEPORT_IN:",
			"lastteleport_time = FloatTime();",
			"case EV_GENERAL_SOUND:",
			"trap_EA_Use(bs->client);",
			"BotRememberHeardClient(bs, state);",
		),
	),
	"BotCheckSnapshot": (
		"void BotCheckSnapshot(bot_state_t *bs)",
		(
			"trap_BotAddAvoidSpot(bs->ms, vec3_origin, 0, AVOID_CLEAR);",
			"bs->kamikazebody = 0;",
			"bs->numproxmines = 0;",
			"BotAI_GetSnapshotEntity( bs->client, ent, &state )",
			"BotCheckEvents(bs, &state);",
			"state.eType == ET_MISSILE && state.weapon == WP_GRENADE_LAUNCHER",
			"BotCheckForProxMines(bs, &state);",
			"BotCheckForKamikazeBody(bs, &state);",
			"BotAI_GetEntityState(bs->client, &state);",
			"state.event = bs->cur_ps.externalEvent;",
		),
	),
	"BotAlternateRoute": (
		"bot_goal_t *BotAlternateRoute(bot_state_t *bs, bot_goal_t *goal)",
		(
			"if (bs->altroutegoal.areanum)",
			"if (bs->reachedaltroutegoal_time)",
			"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, bs->altroutegoal.areanum, bs->tfl);",
			"if (t && t < 20)",
			"bs->reachedaltroutegoal_time = FloatTime();",
			"memcpy(goal, &bs->altroutegoal, sizeof(bot_goal_t));",
		),
	),
	"BotGetAlternateRouteGoal": (
		"int BotGetAlternateRouteGoal(bot_state_t *bs, int base)",
		(
			"if (base == TEAM_RED)",
			"altroutegoals = red_altroutegoals;",
			"altroutegoals = blue_altroutegoals;",
			"rnd = (float) random() * numaltroutegoals;",
			"VectorCopy(altroutegoals[rnd].origin, goal->origin);",
			"VectorSet(goal->mins, -8, -8, -8);",
			"goal->flags = 0;",
			"bs->reachedaltroutegoal_time = 0;",
		),
	),
	"BotSetupAlternativeRouteGoals": (
		"void BotSetupAlternativeRouteGoals(void)",
		(
			"if (altroutegoals_setup)",
			"if (gametype == GT_CTF)",
			'trap_BotGetLevelItemGoal(-1, "Neutral Flag", &ctf_neutralflag)',
			"red_numaltroutegoals = trap_AAS_AlternativeRouteGoals(",
			"blue_numaltroutegoals = trap_AAS_AlternativeRouteGoals(",
			"else if (gametype == GT_1FCTF)",
			"else if (gametype == GT_OBELISK)",
			'trap_BotGetLevelItemGoal(-1, "Neutral Obelisk", &neutralobelisk)',
			"else if (gametype == GT_HARVESTER)",
			"altroutegoals_setup = qtrue;",
		),
	),
}


HLIL_ENTRY_ANCHORS = (
	"1001bcd0    int32_t sub_1001bcd0(void* arg1, int32_t arg2, void* arg3)",
	'1001c5b0    int32_t __convention("regparm") sub_1001c5b0(int32_t arg1, int32_t arg2, int32_t arg3, void* arg4, void* arg5)',
	'1001c720    int32_t __convention("regparm") sub_1001c720(int32_t arg1, int32_t arg2, int32_t arg3, void* arg4)',
	"1001c940    int32_t sub_1001c940(void* arg1)",
	'1001c9e0    void __convention("regparm") sub_1001c9e0(int32_t arg1, void* arg2, int32_t arg3)',
	"1001cbb0    void sub_1001cbb0(void* arg1)",
	"1001cc60    int32_t sub_1001cc60(int32_t arg1)",
	"1001ccc0    long double sub_1001ccc0(void* arg1 @ esi, int32_t arg2 @ edi)",
	'1001cd40    void __convention("regparm") sub_1001cd40(int32_t arg1, void* arg2, void* arg3, int32_t arg4)',
	"1001d6d0    int32_t __fastcall sub_1001d6d0(void* arg1, int32_t* arg2 @ esi)",
	"1001d810    int32_t sub_1001d810(int32_t* arg1 @ esi, void* arg2 @ edi)",
	"1001d960    void sub_1001d960(void* arg1, int32_t* arg2, int32_t arg3)",
	"1001dcf0    void sub_1001dcf0(void* arg1, void* arg2)",
	"1001deb0    int32_t sub_1001deb0()",
	"1001e400    void sub_1001e400(void* arg1 @ esi, int32_t* arg2 @ edi)",
	"1001e4c0    int32_t* sub_1001e4c0(void* arg1 @ esi, int32_t* arg2)",
	"1001eaf0    int32_t* sub_1001eaf0(void* arg1)",
	'1001ecb0    void __convention("regparm") sub_1001ecb0(void* arg1, int32_t arg2, void* arg3)',
	"1001ed30    int32_t sub_1001ed30(void* arg1 @ esi, int32_t arg2)",
	"1001ee30    void sub_1001ee30()",
)


HLIL_FLOW_ANCHORS = (
	'1001bd38  (*(eax_3 + 0x120))(arg2, "model", &var_88, 0x80)',
	"1001bd73          int32_t eax_5 = sub_1001bbe0(&var_1e0, 0, eax_4, &var_1ec)",
	"1001be02          sub_1001baf0(&var_170, edx_1, &var_200)",
	"1001c452              int32_t eax_24 = (*(edx_5 + 0x114))(&var_158, &var_134, &var_128, 0, 0xa)",
	"1001c477                  while ((*(data_104b13ac + 0x130))(var_128[esi_6]) == 0)",
	"1001c630          int32_t eax_5 = sub_1001bbe0(&var_410, 0, eax_4, &var_41c)",
	"1001c7bb          int32_t eax_5 = sub_1001bbe0(&var_dc, 0x40000000, eax_4, &var_d0)",
	"1001c981              (*(data_104b13ac + 0x138))(*ebx_1, 1)",
	"1001cb83  __builtin_memcpy(dest: ebx + 0x1bd8, src: arg3, n: 0xfc)",
	"1001ccaf          while (i s< *(ebx + 0xf0))",
	"1001cd00  while (true)",
	"1001cf2a                  sub_1001c5b0(eax_17, edx_5, ebp, arg3, arg2)",
	"1001d3b2                                              if (sub_1001bcd0(arg3, ebp_1, ebx_4) == 0)",
	"1001d50a                                              if (sub_1001c720(eax_63, edx_18, ebp_1, ebx_4)",
	"1001d757  st0, eax_4 = sub_1001c9e0(eax_3, arg1, ecx_1)",
	"1001d851  float var_2c = fconvert.s(fconvert.t(fconvert.s(float.t(rand() & 0x7fff)",
	"1001d920      (*(edx + 0x2a0))(ecx_1, &var_18, fconvert.s(fconvert.t(data_1008fe58)), 1)",
	"1001d9be      sub_1001d810(esi, ebx)",
	"1001da28  st0_1, eax_4 = sub_1001cd40(var_b0, &var_218, ebx, var_104)",
	"1001da53      st0_2, eax_6 = sub_1001ccc0(ebx, var_1ec)",
	"1001da62          sub_1001d6d0(ebx, &var_218)",
	"1001dda1      (*(data_104b13ac + 0x13c))(&var_134, eax_4, arg1 + 0x130c, *(arg2 + 0xc), eax_3,",
	"1001de24                      st0_1, eax_9 = sub_1001cd40(eax_7, &var_110, arg1, ecx_2)",
	"1001defe  int32_t eax_4 = (*(data_104b13ac + 0x1e4))(*(ebx + 0x1964), &var_278)",
	"1001e1ff                              *(esp_7 - 4) = \"**** no valid reply ****\\n\"",
	"1001e497              (*(data_104b13ac + 0x2c4))(*(arg1 + 0x195c), &arg2[6],",
	"1001e4f5  if (*(arg1 + (ecx << 2) + 0x280) != *(ecx * 0x384 + 0x104b4200))",
	"1001e684                  char const* const ecx_14 = \"sound/items/kamikazerespawn.wav\"",
	"1001e6dd                  char const* const ecx_17 = \"sound/items/poweruprespawn.wav\"",
	"1001e97c                      (*(data_104b13ac + 0x68))(eax_26 + 0x111, &var_88, 0x80)",
	"1001eb30  (*(data_104b13ac + 0x2c4))(*(arg1 + 0x195c), &data_104b1438, fconvert.s(float.t(0)), 0)",
	"1001eb51      int32_t eax_5 = (*(data_104b13ac + 0xe8))(*(arg1 + 8), ebx)",
	"1001ebb3      int32_t ecx_3 = sub_1001e4c0(arg1, &var_f8)",
	"1001ebf8      sub_1001e400(arg1, &var_f8)",
	"1001ec8d  int32_t* result = sub_1001e4c0(arg1, &var_f8)",
	"1001ecfb          (*(data_104b13ac + 0x134))(*(arg3 + 0x1334), arg3 + 0x130c, ecx, *(arg3 + 0x1738))",
	"1001ed26      __builtin_memcpy(dest: edi, src: arg3 + 0x1a00, n: 0x40)",
	"1001ed81      sub_1007b550(float.t(rand() & 0x7fff) / fconvert.t(32767.0) * float.t(edi))",
	"1001ee37  if (data_105e4394 == 0)",
	"1001efba          if ((*(data_104b13ac + 0x268))(0xffffffff, \"Neutral Flag\", &data_105e40c0) s< 0)",
	"1001eee7                  int32_t eax_5 = (*(data_104b13ac + 0x140))(&data_105e3e40, data_105e3e4c,",
	"1001f1d8          sub_1001ee30()",
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


def test_qagame_ai_dmq3_activate_obstacle_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_DMQ3)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_DMQ3_ACTIVATE_OBSTACLE_FUNCTIONS:
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

		source_signature, source_anchors = SOURCE_HELPERS[normalized_name]
		block = _extract_function_block(source, source_signature)
		for anchor in source_anchors:
			assert anchor in block

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_FLOW_ANCHORS:
		assert expected in hlil


def test_qagame_ai_dmq3_activate_obstacle_botlib_import_wiring_is_pinned() -> None:
	ai_dmq3 = _read(GAME_AI_DMQ3)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		"G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS = 61,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_INFO = 62,",
		"G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX = 65,",
		"G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS = 69,",
		"G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY = 71,",
		"G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY = 72,",
		"G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY = 73,",
		"G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY = 74,",
		"G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY = 75,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY = 76,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA = 77,",
		"G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA = 78,",
		"G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE = 79,",
		"G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL = 80,",
		"G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT = 113,",
		"G_QL_IMPORT_BOTLIB_AI_REMOVE_CONSOLE_MESSAGE = 120,",
		"G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE = 121,",
		"G_QL_IMPORT_BOTLIB_AI_NUM_CONSOLE_MESSAGE = 122,",
		"G_QL_IMPORT_BOTLIB_AI_REPLY_CHAT = 125,",
		"G_QL_IMPORT_BOTLIB_AI_FIND_MATCH = 130,",
		"G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE = 131,",
		"G_QL_IMPORT_BOTLIB_AI_UNIFY_WHITE_SPACES = 132,",
		"G_QL_IMPORT_BOTLIB_AI_REPLACE_SYNONYMS = 133,",
		"G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL = 154,",
		"G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION = 168,",
		"G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT = 177,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX: return G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX;",
		"case BOTLIB_AAS_TRACE_AREAS: return G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS;",
		"case BOTLIB_AAS_NEXT_BSP_ENTITY: return G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY;",
		"case BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY;",
		"case BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY;",
		"case BOTLIB_AAS_AREA_REACHABILITY: return G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY;",
		"case BOTLIB_AAS_ENABLE_ROUTING_AREA: return G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA;",
		"case BOTLIB_AAS_PREDICT_ROUTE: return G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE;",
		"case BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL: return G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL;",
		"case BOTLIB_AI_NEXT_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE;",
		"case BOTLIB_AI_REPLY_CHAT: return G_QL_IMPORT_BOTLIB_AI_REPLY_CHAT;",
		"case BOTLIB_AI_FIND_MATCH: return G_QL_IMPORT_BOTLIB_AI_FIND_MATCH;",
		"case BOTLIB_AI_REPLACE_SYNONYMS: return G_QL_IMPORT_BOTLIB_AI_REPLACE_SYNONYMS;",
		"case BOTLIB_AI_GET_LEVEL_ITEM_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL;",
		"case BOTLIB_AI_MOVE_IN_DIRECTION: return G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION;",
		"case BOTLIB_AI_ADD_AVOID_SPOT: return G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT;",
		"syscall( BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX, presencetype, mins, maxs );",
		"return syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );",
		"return syscall( BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY, ent, key, value, size );",
		"return syscall( BOTLIB_AAS_AREA_REACHABILITY, areanum );",
		"return syscall( BOTLIB_AAS_ENABLE_ROUTING_AREA, areanum, enable );",
		"return syscall( BOTLIB_AAS_PREDICT_ROUTE, route, areanum, origin, goalareanum, travelflags, maxareas, maxtime, stopevent, stopcontents, stoptfl, stopareanum );",
		"return syscall( BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL, start, startareanum, goal, goalareanum, travelflags, altroutegoals, maxaltroutegoals, type );",
		"return syscall( BOTLIB_AI_NEXT_CONSOLE_MESSAGE, chatstate, cm );",
		"return syscall( BOTLIB_AI_REPLY_CHAT, chatstate, message, mcontext, vcontext, var0, var1, var2, var3, var4, var5, var6, var7 );",
		"return syscall( BOTLIB_AI_FIND_MATCH, str, match, context );",
		"syscall( BOTLIB_AI_REPLACE_SYNONYMS, string, context );",
		"return syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );",
		"return syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, PASSFLOAT(speed), type );",
		"syscall( BOTLIB_AI_ADD_AVOID_SPOT, movestate, origin, PASSFLOAT(radius), type);",
	):
		assert expected in game_syscalls

	for expected in (
		"case BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX:",
		"case BOTLIB_AAS_TRACE_AREAS:",
		"case BOTLIB_AAS_ENABLE_ROUTING_AREA:",
		"case BOTLIB_AAS_PREDICT_ROUTE:",
		"case BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL:",
		"case BOTLIB_AI_NEXT_CONSOLE_MESSAGE:",
		"case BOTLIB_AI_REPLY_CHAT:",
		"case BOTLIB_AI_FIND_MATCH:",
		"case BOTLIB_AI_GET_LEVEL_ITEM_GOAL:",
		"case BOTLIB_AI_MOVE_IN_DIRECTION:",
		"case BOTLIB_AI_ADD_AVOID_SPOT:",
		"[BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX] = (ql_import_f)QL_G_trap_AAS_PresenceTypeBoundingBox,",
		"[BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas,",
		"[BOTLIB_AAS_ENABLE_ROUTING_AREA] = (ql_import_f)QL_G_trap_AAS_EnableRoutingArea,",
		"[BOTLIB_AAS_PREDICT_ROUTE] = (ql_import_f)QL_G_trap_AAS_PredictRoute,",
		"[BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL] = (ql_import_f)QL_G_trap_AAS_AlternativeRouteGoals,",
		"[BOTLIB_AI_NEXT_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNextConsoleMessage,",
		"[BOTLIB_AI_REPLY_CHAT] = (ql_import_f)QL_G_trap_BotReplyChat,",
		"[BOTLIB_AI_FIND_MATCH] = (ql_import_f)QL_G_trap_BotFindMatch,",
		"[BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal,",
		"[BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection,",
		"[BOTLIB_AI_ADD_AVOID_SPOT] = (ql_import_f)QL_G_trap_BotAddAvoidSpot,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX] = (ql_import_f)QL_G_trap_AAS_PresenceTypeBoundingBox;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA] = (ql_import_f)QL_G_trap_AAS_EnableRoutingArea;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE] = (ql_import_f)QL_G_trap_AAS_PredictRoute;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL] = (ql_import_f)QL_G_trap_AAS_AlternativeRouteGoals;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotNextConsoleMessage;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REPLY_CHAT] = (ql_import_f)QL_G_trap_BotReplyChat;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FIND_MATCH] = (ql_import_f)QL_G_trap_BotFindMatch;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT] = (ql_import_f)QL_G_trap_BotAddAvoidSpot;",
	):
		assert expected in server_game

	for expected in (
		"G_Import_Syscall( BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX, presencetype, mins, maxs );",
		"return G_Import_Syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );",
		"return G_Import_Syscall( BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY, ent, key, value, size );",
		"return G_Import_Syscall( BOTLIB_AAS_AREA_REACHABILITY, areanum );",
		"return G_Import_Syscall( BOTLIB_AAS_ENABLE_ROUTING_AREA, areanum, enable );",
		"return G_Import_Syscall( BOTLIB_AAS_PREDICT_ROUTE, route, areanum, origin, goalareanum, travelflags, maxareas, maxtime, stopevent, stopcontents, stoptfl, stopareanum );",
		"return G_Import_Syscall( BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL, start, startareanum, goal, goalareanum, travelflags, altroutegoals, maxaltroutegoals, type );",
		"return G_Import_Syscall( BOTLIB_AI_NEXT_CONSOLE_MESSAGE, chatstate, cm );",
		"return G_Import_Syscall( BOTLIB_AI_REPLY_CHAT, chatstate, message, mcontext, vcontext, var0, var1, var2, var3, var4, var5, var6, var7 );",
		"return G_Import_Syscall( BOTLIB_AI_FIND_MATCH, str, match, context );",
		"G_Import_Syscall( BOTLIB_AI_REPLACE_SYNONYMS, string, context );",
		"return G_Import_Syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );",
		"return G_Import_Syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, QL_G_PASSFLOAT(speed), type );",
		"G_Import_Syscall( BOTLIB_AI_ADD_AVOID_SPOT, movestate, origin, QL_G_PASSFLOAT(radius), type);",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_AAS_PresenceTypeBoundingBox(PRESENCE_CROUCH, bboxmins, bboxmaxs);",
		"trap_AAS_TraceAreas(start, end, areas, points, 10);",
		"trap_AAS_ValueForBSPEpairKey(ent, \"model\", tmpmodel, sizeof(tmpmodel))",
		"trap_AAS_FloatForBSPEpairKey(bspent, \"lip\", &lip);",
		"trap_AAS_AreaReachability(areas[i])",
		"trap_AAS_EnableRoutingArea( activategoal->areas[i], enable );",
		"trap_AAS_PredictRoute(&route, bs->areanum, bs->origin,",
		"trap_AAS_AlternativeRouteGoals(",
		"trap_BotNextConsoleMessage(bs->cs, &m)",
		"trap_BotReplyChat(bs->cs, message, context, CONTEXT_REPLY,",
		"trap_BotFindMatch(m.message, &match, MTCONTEXT_REPLYCHAT)",
		"trap_BotReplaceSynonyms(ptr, context);",
		"trap_BotGetLevelItemGoal(-1, \"Neutral Flag\", &ctf_neutralflag)",
		"trap_BotMoveInDirection(bs->ms, sideward, 400, movetype)",
		"trap_BotAddAvoidSpot(bs->ms, state->pos.trBase, 160, AVOID_ALWAYS);",
	):
		assert expected in ai_dmq3
