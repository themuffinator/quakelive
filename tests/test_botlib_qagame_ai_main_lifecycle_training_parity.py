from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
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
QAGAME_DECOMPILE_TOP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
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


AI_MAIN_LIFECYCLE_FUNCTIONS = (
	("10020f00", "FUN_10020f00", "BotTestAAS", "void BotTestAAS(vec3_t origin)", 580),
	("10021150", "FUN_10021150", "BotInterbreedBots", "void BotInterbreedBots(void)", 390),
	("100212e0", "FUN_100212e0", "BotWriteInterbreeded", "void BotWriteInterbreeded(char *filename)", 363),
	("10021450", "FUN_10021450", "BotInterbreedEndMatch", "void BotInterbreedEndMatch(void)", 115),
	("100214d0", "FUN_100214d0", "BotInterbreeding", "void BotInterbreeding(void)", 265),
	("100215e0", "FUN_100215e0", "BotTeamLeader", "int BotTeamLeader(bot_state_t *bs)", 43),
	("10021610", "FUN_10021610", "BotChangeViewAngle", "float BotChangeViewAngle(float angle, float ideal_angle, float speed)", 293),
	("10021740", "FUN_10021740", "BotChangeViewAngles", "void BotChangeViewAngles(bot_state_t *bs, float thinktime)", 980),
	("10021b20", "FUN_10021b20", "BotInputToUserCommand", "void BotInputToUserCommand(bot_input_t *bi, usercmd_t *ucmd, int delta_angles[3], int time)", 741),
	("10021e10", "FUN_10021e10", "BotUpdateInput", "void BotUpdateInput(bot_state_t *bs, int time, int elapsed_time)", 372),
	("10021f90", "FUN_10021f90", "RemoveColorEscapeSequences", "void RemoveColorEscapeSequences(char *text)", 70),
	("10021fe0", "FUN_10021fe0", "BotAI", "int BotAI(int client, float thinktime)", 1187),
	("10022490", "FUN_10022490", "BotScheduleBotThink", "void BotScheduleBotThink(void)", 138),
	("10022520", "FUN_10022520", "BotWriteSessionData", "void BotWriteSessionData(bot_state_t *bs)", 207),
	("100225f0", "FUN_100225f0", "BotReadSessionData", "void BotReadSessionData(bot_state_t *bs)", 219),
	("100226d0", "FUN_100226d0", "BotAISetupClient", "int BotAISetupClient(int client, bot_settings_t *settings, qboolean restart)", 1154),
	("10022b60", "FUN_10022b60", "BotAIShutdownClient", "int BotAIShutdownClient(int client, qboolean restart)", 242),
	("10022c60", "FUN_10022c60", "BotResetState", "void BotResetState(bot_state_t *bs)", 465),
	("10022e40", "FUN_10022e40", "BotAILoadMap", "int BotAILoadMap(int restart)", 157),
	("10022ee0", "FUN_10022ee0", "BotPublishDebugInfoString", "int BotPublishDebugInfoString(bot_state_t *bs)", 1228),
	("10023400", "FUN_10023400", "BotAIStartFrame", "int BotAIStartFrame(int time)", 2038),
	("10023c00", "FUN_10023c00", "BotInitLibrary", "int BotInitLibrary(void)", 1469),
	("100241c0", "FUN_100241c0", "BotAISetup", "int BotAISetup(int restart)", 436),
	("10024380", "FUN_10024380", "BotAIShutdown", "int BotAIShutdown(int restart)", 76),
)


AI_MAIN_RETAIL_TRAINING_FUNCTIONS = (
	("100243d0", "FUN_100243d0", "BotEntityBoundsGap", "float BotEntityBoundsGap(int ent1, int ent2)", 350),
	("10024530", "FUN_10024530", "BotSetIdealViewAnglesToPoint", "void BotSetIdealViewAnglesToPoint(bot_state_t *bs, vec3_t target)", 82),
	("10024590", "FUN_10024590", "BotSetPredictItemPickupDisabled", "void BotSetPredictItemPickupDisabled(int client, qboolean disabled)", 40),
	("100245c0", "FUN_100245c0", "BotSetTrainingBotState", "void BotSetTrainingBotState(bot_state_t *bs, qboolean enabled)", 124),
	("10024640", "FUN_10024640", "BotUpdateItemDelayTime", "void BotUpdateItemDelayTime(int time)", 183),
	("10024700", "FUN_10024700", "BotAppendDynamicSkillSample", "void BotAppendDynamicSkillSample(bot_state_t *bs, int delta, float skill, int time)", 177),
	("100247c0", "FUN_100247c0", "BotUpdateDynamicSkill", "void BotUpdateDynamicSkill(int time)", 1596),
	("10024e10", "FUN_10024e10", "BotApplyBeyondRealityTravelFlags", "void BotApplyBeyondRealityTravelFlags(int *travelFlags)", 136),
	("10024ea0", "FUN_10024ea0", "BotGetLocalClient", "int BotGetLocalClient(void)", 56),
	("10024ee0", "FUN_10024ee0", "BotGetFirstBotClient", "int BotGetFirstBotClient(void)", 59),
	("10024f20", "FUN_10024f20", "BotSetTrainingCvarIfChanged", "qboolean BotSetTrainingCvarIfChanged(const char *name, const char *value)", 127),
	("10024fa0", "FUN_10024fa0", "BotUpdateTrainingState", "void BotUpdateTrainingState(void)", 993),
)


SOURCE_HELPERS = {
	"BotTestAAS": (
		"void BotTestAAS(vec3_t origin)",
		(
			"trap_Cvar_Update(&bot_testsolid);",
			"trap_BotDrawDebugAreas(origin, bot_showAreas.integer, bot_showAreaNumber.integer);",
			"trap_BotDrawAvoidSpots(bs->ms);",
			"areanum = BotPointAreaNum(origin);",
			'BotAI_Print(PRT_MESSAGE, "\\rarea %d, cluster %d       ", areanum, info.cluster);',
		),
	),
	"BotInterbreedBots": (
		"void BotInterbreedBots(void)",
		(
			"ranks[i] = botstates[i]->num_kills * 2 - botstates[i]->num_deaths;",
			"trap_GeneticParentsAndChildSelection(MAX_CLIENTS, ranks, &parent1, &parent2, &child)",
			"trap_BotInterbreedGoalFuzzyLogic(botstates[parent1]->gs, botstates[parent2]->gs, botstates[child]->gs);",
			"trap_BotMutateGoalFuzzyLogic(botstates[child]->gs, 1);",
		),
	),
	"BotWriteInterbreeded": (
		"void BotWriteInterbreeded(char *filename)",
		(
			"rank = botstates[i]->num_kills * 2 - botstates[i]->num_deaths;",
			"trap_BotSaveGoalFuzzyLogic(botstates[bestbot]->gs, filename);",
		),
	),
	"BotInterbreedEndMatch": (
		"void BotInterbreedEndMatch(void)",
		(
			"if (!bot_interbreed) return;",
			"bot_interbreedmatchcount++;",
			"BotWriteInterbreeded(bot_interbreedwrite.string);",
			"BotInterbreedBots();",
		),
	),
	"BotInterbreeding": (
		"void BotInterbreeding(void)",
		(
			"trap_Cvar_Update(&bot_interbreedchar);",
			"if (gametype != GT_TOURNAMENT)",
			"BotAIShutdownClient(botstates[i]->client, qfalse);",
			'trap_BotLibVarSet("bot_reloadcharacters", "1");',
			'trap_SendConsoleCommand( EXEC_INSERT, va("addbot %s 4 free %i %s%d\\n",',
		),
	),
	"BotTeamLeader": (
		"int BotTeamLeader(bot_state_t *bs)",
		(
			"leader = ClientFromName(bs->teamleader);",
			"if (!botstates[leader] || !botstates[leader]->inuse) return qfalse;",
		),
	),
	"BotChangeViewAngle": (
		"float BotChangeViewAngle(float angle, float ideal_angle, float speed)",
		(
			"angle = AngleMod(angle);",
			"ideal_angle = AngleMod(ideal_angle);",
			"if (move > speed) move = speed;",
			"return AngleMod(angle + move);",
		),
	),
	"BotChangeViewAngles": (
		"void BotChangeViewAngles(bot_state_t *bs, float thinktime)",
		(
			"CHARACTERISTIC_VIEW_FACTOR",
			"CHARACTERISTIC_VIEW_MAXCHANGE",
			"if (bot_challenge.integer)",
			"BotChangeViewAngle(bs->viewangles[i],",
			"trap_EA_View(bs->client, bs->viewangles);",
		),
	),
	"BotInputToUserCommand": (
		"void BotInputToUserCommand(bot_input_t *bi, usercmd_t *ucmd, int delta_angles[3], int time)",
		(
			"memset(ucmd, 0, sizeof(usercmd_t));",
			"if (bi->actionflags & ACTION_DELAYEDJUMP)",
			"ucmd->buttons |= BUTTON_FOLLOWME;",
			"ucmd->weapon = bi->weapon;",
			"ucmd->angles[PITCH] = ANGLE2SHORT(bi->viewangles[PITCH]);",
			"bi->speed = bi->speed * 127 / 400;",
			"if (bi->actionflags & ACTION_CROUCH) ucmd->upmove -= 127;",
		),
	),
	"BotUpdateInput": (
		"void BotUpdateInput(bot_state_t *bs, int time, int elapsed_time)",
		(
			"BotChangeViewAngles(bs, (float) elapsed_time / 1000);",
			"trap_EA_GetInput(bs->client, (float) time / 1000, &bi);",
			"if (bs->lastucmd.buttons & BUTTON_ATTACK) bi.actionflags &= ~(ACTION_RESPAWN|ACTION_ATTACK);",
			"BotInputToUserCommand(&bi, &bs->lastucmd, bs->cur_ps.delta_angles, time);",
		),
	),
	"RemoveColorEscapeSequences": (
		"void RemoveColorEscapeSequences( char *text )",
		(
			"if (Q_IsColorString(&text[i]))",
			"if (text[i] > 0x7E)",
			"text[l++] = text[i];",
			"text[l] = '\\0';",
		),
	),
	"BotAI": (
		"int BotAI(int client, float thinktime)",
		(
			"trap_EA_ResetInput(client);",
			'BotAI_Print(PRT_FATAL, "BotAI: client %d is not setup\\n", client);',
			"BotAI_GetClientState( client, &bs->cur_ps );",
			"while( trap_BotGetServerCommand(client, buf, sizeof(buf)) )",
			"RemoveColorEscapeSequences( args );",
			"trap_BotQueueConsoleMessage(bs->cs, CMS_NORMAL, args);",
			"BotVoiceChatCommand(bs, SAY_TEAM, args);",
			"BotDeathmatchAI(bs, thinktime);",
			"trap_EA_SelectWeapon(bs->client, bs->weaponnum);",
		),
	),
	"BotScheduleBotThink": (
		"void BotScheduleBotThink(void)",
		(
			"botstates[i]->botthink_residual = bot_thinktime.integer * botnum / numbots;",
			"botnum++;",
		),
	),
	"BotWriteSessionData": (
		"void BotWriteSessionData(bot_state_t *bs)",
		(
			'var = va( "botsession%i", bs->client );',
			"trap_Cvar_Set( var, s );",
			"bs->lastgoal_teamgoal.maxs[2]",
		),
	),
	"BotReadSessionData": (
		"void BotReadSessionData(bot_state_t *bs)",
		(
			'var = va( "botsession%i", bs->client );',
			"trap_Cvar_VariableStringBuffer( var, s, sizeof(s) );",
			"sscanf(s,",
			"&bs->lastgoal_teamgoal.maxs[2]",
		),
	),
	"BotAISetupClient": (
		"int BotAISetupClient(int client, struct bot_settings_s *settings, qboolean restart)",
		(
			'BotAI_Print(PRT_FATAL, "BotAISetupClient: client %d already setup\\n", client);',
			"bs->character = trap_BotLoadCharacter(settings->characterfile, settings->skill);",
			"bs->gs = trap_BotAllocGoalState(client);",
			"errnum = trap_BotLoadItemWeights(bs->gs, filename);",
			"bs->ws = trap_BotAllocWeaponState();",
			"bs->cs = trap_BotAllocChatState();",
			"errnum = trap_BotLoadChatFile(bs->cs, filename, name);",
			"trap_BotSetChatGender(bs->cs, CHAT_GENDERFEMALE);",
			"BotScheduleBotThink();",
			"BotReadSessionData(bs);",
		),
	),
	"BotAIShutdownClient": (
		"int BotAIShutdownClient(int client, qboolean restart)",
		(
			"BotWriteSessionData(bs);",
			"BotChat_ExitGame(bs)",
			"trap_BotFreeMoveState(bs->ms);",
			"trap_BotFreeGoalState(bs->gs);",
			"trap_BotFreeChatState(bs->cs);",
			"trap_BotFreeWeaponState(bs->ws);",
			"trap_BotFreeCharacter(bs->character);",
			"BotClearActivateGoalStack(bs);",
			"numbots--;",
		),
	),
	"BotResetState": (
		"void BotResetState(bot_state_t *bs)",
		(
			"memcpy(&settings, &bs->settings, sizeof(bot_settings_t));",
			"memcpy(&ps, &bs->cur_ps, sizeof(playerState_t));",
			"BotFreeWaypoints(bs->checkpoints);",
			"memset(bs, 0, sizeof(bot_state_t));",
			"trap_BotResetMoveState(bs->ms);",
			"trap_BotResetGoalState(bs->gs);",
			"trap_BotResetWeaponState(bs->ws);",
			"trap_BotResetAvoidReach(bs->ms);",
		),
	),
	"BotAILoadMap": (
		"int BotAILoadMap( int restart )",
		(
			'trap_Cvar_Register( &mapname, "mapname", "", CVAR_SERVERINFO | CVAR_ROM );',
			"trap_BotLibLoadMap( mapname.string );",
			"BotResetState( botstates[i] );",
			"botstates[i]->setupcount = 4;",
			"BotSetupDeathmatchAI();",
		),
	),
	"BotAIStartFrame": (
		"int BotAIStartFrame(int time)",
		(
			"G_CheckBotSpawn();",
			"trap_BotLibStartFrame((float) time / 1000);",
			"trap_BotLibUpdateEntity(i, NULL);",
			"state.qlTimeSeconds = (float)( ent->s.time / 1000 );",
			"BotAIRegularUpdate();",
			"BotAI(i, (float) thinktime / 1000);",
			"BotUpdateInput(botstates[i], time, elapsed_time);",
			"trap_BotUserCommand(botstates[i]->client, &botstates[i]->lastucmd);",
			"BotUpdateTrainingState();",
		),
	),
	"BotInitLibrary": (
		"int BotInitLibrary(void)",
		(
			'trap_BotLibVarSet("maxclients", buf);',
			'trap_BotLibVarSet("maxentities", buf);',
			'trap_BotLibVarSet("bot_showPath", "0");',
			'trap_BotLibVarSet("aasoptimize", buf);',
			'trap_BotLibVarSet("saveroutingcache", buf);',
			'trap_BotLibVarSet("basedir", buf);',
			'trap_BotLibDefine("MISSIONPACK");',
			"return trap_BotLibSetup();",
		),
	),
	"BotAISetup": (
		"int BotAISetup( int restart )",
		(
			'trap_Cvar_Register(&bot_log, "bot_log", "0", 0);',
			'trap_Cvar_Register(&bot_thinktime, "bot_thinktime", "100", 0);',
			'trap_Cvar_Register(&bot_report, "bot_report", "0", CVAR_CHEAT);',
			'trap_Cvar_Register(&bot_interbreedwrite, "bot_interbreedwrite", "", 0);',
			"BotResetTrainingRuntimeFlags();",
			"memset( botstates, 0, sizeof(botstates) );",
			"errnum = BotInitLibrary();",
		),
	),
	"BotAIShutdown": (
		"int BotAIShutdown( int restart )",
		(
			"BotAIShutdownClient(botstates[i]->client, restart);",
			"trap_BotLibShutdown();",
			"return qtrue;",
		),
	),
	"BotGetLocalClient": (
		"int BotGetLocalClient( void )",
		(
			"level.clients[i].pers.connected != CON_CONNECTED",
			"level.clients[i].pers.localClient",
			"return i;",
		),
	),
	"BotGetFirstBotClient": (
		"int BotGetFirstBotClient( void )",
		(
			"level.clients[i].pers.connected != CON_CONNECTED",
			"g_entities[i].r.svFlags & SVF_BOT",
			"return i;",
		),
	),
	"BotSetTrainingCvarIfChanged": (
		"qboolean BotSetTrainingCvarIfChanged( const char *name, const char *value )",
		(
			"trap_Cvar_VariableStringBuffer( name, current, sizeof( current ) );",
			"if ( !Q_stricmp( current, value ) )",
			"trap_Cvar_Set( name, value );",
		),
	),
	"BotSetPredictItemPickupDisabled": (
		"static void BotSetPredictItemPickupDisabled( int clientNum, qboolean disabled )",
		(
			"level.clients[clientNum].ps.eFlags |= EF_AWARD_DENIED;",
			"level.clients[clientNum].ps.eFlags &= ~EF_AWARD_DENIED;",
		),
	),
	"BotUpdateItemDelayTime": (
		"static void BotUpdateItemDelayTime( void )",
		(
			'delayValue = "0";',
			'skill = trap_Cvar_VariableValue( "g_spSkill" );',
			"elapsedSeconds = ( level.time - level.startTime ) / 1000;",
			'BotSetTrainingCvarIfChanged( "bot_itemDelayTime", delayValue );',
		),
	),
	"BotUpdateTrainingState": (
		"static void BotUpdateTrainingState( void )",
		(
			"localClient = BotGetLocalClient();",
			"botClient = BotGetFirstBotClient();",
			'trap_Cvar_Set( "g_spSkill", BotFormatTrainingSkill( bootstrapSkill ) );',
			"G_AddTrainerBot();",
			'BotSetTrainingCvarIfChanged( "g_training", "1" );',
			"BotSetPredictItemPickupDisabled( botClient, qtrue );",
			"BotUpdateItemDelayTime();",
			"BotUpdateTrainingMusic( localClient );",
		),
	),
}


RETAIL_ONLY_NAMES = {
	"BotEntityBoundsGap",
	"BotSetIdealViewAnglesToPoint",
	"BotSetTrainingBotState",
	"BotAppendDynamicSkillSample",
	"BotUpdateDynamicSkill",
	"BotApplyBeyondRealityTravelFlags",
}


HLIL_ENTRY_ANCHORS = (
	"10020f00    void __fastcall sub_10020f00(int32_t* arg1)",
	"10021150    void* sub_10021150()",
	"100212e0    long double sub_100212e0(int32_t arg1)",
	"10021450    void sub_10021450()",
	"100214d0    void* sub_100214d0()",
	'100215e0    int32_t __convention("regparm") sub_100215e0(void* arg1)',
	"10021610    long double sub_10021610(float arg1, float arg2, float arg3)",
	"10021740    int32_t sub_10021740(long double arg1 @ st0, long double arg2 @ st1)",
	'10021b20    int32_t __convention("regparm") sub_10021b20(int16_t* arg1, int32_t arg2, int32_t* arg3, int32_t arg4, int32_t arg5, int32_t arg6)',
	'10021e10    uint32_t __convention("regparm") sub_10021e10(int32_t arg1, int32_t arg2, void* arg3, int32_t arg4, int32_t arg5)',
	"10021f90    void sub_10021f90(char* arg1 @ esi)",
	'10021fe0    void __convention("regparm") sub_10021fe0(int32_t arg1, int32_t arg2, int32_t arg3, float arg4)',
	"10022490    void sub_10022490()",
	"10022520    int32_t sub_10022520(void* arg1 @ esi)",
	"100225f0    int32_t __fastcall sub_100225f0(void* arg1)",
	'100226d0    int32_t __convention("regparm") sub_100226d0(int32_t arg1, void* arg2, int32_t arg3, long double arg4 @ st0, long double arg5 @ st1, int32_t arg6)',
	'10022b60    int32_t __convention("regparm") sub_10022b60(int32_t arg1, int32_t arg2)',
	'10022c60    int32_t __convention("regparm") sub_10022c60(int32_t* arg1)',
	"10022e40    int32_t sub_10022e40(int32_t arg1)",
	"10022ee0    int32_t sub_10022ee0(void* arg1)",
	"10023400    int32_t sub_10023400(long double arg1 @ st0, int32_t arg2)",
	"10023c00    int32_t sub_10023c00()",
	"100241c0    int32_t sub_100241c0(int32_t arg1)",
	"10024380    int32_t sub_10024380(int32_t arg1 @ edi)",
	'100243d0    long double __convention("regparm") sub_100243d0(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4)',
	'10024530    int32_t __convention("regparm") sub_10024530(float* arg1)',
	'10024590    void* __convention("regparm") sub_10024590(int32_t arg1, int32_t arg2)',
	'100245c0    void* __convention("regparm") sub_100245c0(void* arg1, int32_t arg2)',
	"10024640    void __fastcall sub_10024640(float arg1 @ ecx, int32_t arg2 @ esi, long double arg3 @ st0)",
	'10024700    void* __convention("regparm") sub_10024700(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, int32_t arg5, int32_t arg6)',
	"100247c0    int32_t __fastcall sub_100247c0(int32_t arg1, long double arg2 @ st0)",
	"10024e10    int32_t sub_10024e10(int32_t* arg1 @ esi)",
	"10024ea0    int32_t sub_10024ea0()",
	"10024ee0    int32_t sub_10024ee0()",
	"10024f20    int32_t sub_10024f20(char* arg1 @ edi)",
	"10024fa0    void sub_10024fa0(long double arg1 @ st0)",
)


HLIL_FLOW_ANCHORS = (
	"10020f5a  (*(data_104b13ac + 0x14c))(arg1, data_1059cdac, data_105a27ac)",
	"100211d6  if ((*(data_104b13ac + 0x2e0))(0x40, &var_104, &var_108, &var_10c, &var_110) != 0)",
	"100214bd          return sub_10021150() __tailcall",
	"10021547              edx = sub_10022b60(eax_4[2], edx)",
	"10021f21  sub_10021b20(arg3 + 0x48, arg4, ecx_4, &var_30, arg3 + 0x264, arg4)",
	'1002202b      (*(data_104b13ac + 0x3c))("bot_breakPoint", &data_1007d0a8)',
	'10022460      sub_10020980(4, "BotAI: client %d is not setup\\n")',
	'100225dc  var_88.d = sub_10070cb0("botsession%i")',
	'10022629  (*(data_104b13ac + 0x34))(sub_10070cb0("botsession%i"), &var_404, 0x400)',
	'1002278e              sub_10020980(4, "couldn\'t load skill %f from %s\\n")',
	"10022b80      sub_10022520(esi)",
	'10022e78      (*(data_104b13ac + 0x44))(&var_118, "mapname", &data_1007c414, 0x44)',
	"10022ea1          sub_10022c60(eax_2)",
	"10023bd3      sub_10024640(ecx_38, arg2, st0)",
	"10023bda      sub_100247c0(arg2, st0)",
	"10023bdf      sub_10024fa0(st0)",
	'10023c61  (*(data_104b13ac + 0xcc))("maxclients", &var_94)',
	"10024369  int32_t eax_9 = sub_10023c00()",
	"10024578  *(ebx + 0x1998) = fconvert.s(fconvert.t(*(ebx + 0x1998)) * fconvert.t(0.5))",
	'10024674      (*(data_104b13ac + 0x3c))("bot_itemDelayTime", &data_1007d0a8)',
	"1002470f  if (*(*((arg3 << 2) + &data_105e2f00) + 0x2694) s>= 0x20)",
	'10024e73      sub_10070a40("beyondreality", strncpy(&var_484, sub_10070cf0(), 0x7f), &var_484)',
	'10025018          sub_10024f20("125")',
	'10025168          (*(data_104b13ac + 0x60))(eax_2, "playMusic music/fla22k_01_loop")',
)


GHIDRA_DECOMPILE_ANCHORS = (
	"/* FUN_10021fe0 @ 10021fe0 size 1187 */",
	'FUN_10020980(4,"BotAI: client %d is not setup\\n",param_1);',
	"FUN_10021f90();",
	"/* FUN_100226d0 @ 100226d0 size 1154 */",
	'FUN_10020980(4,"BotAISetupClient: client %d already setup\\n",param_1);',
	"FUN_10022490();",
	"/* FUN_100247c0 @ 100247c0 size 1596 */",
	"FUN_10024590(uVar6);",
	"FUN_10024ea0();",
	"/* FUN_10024fa0 @ 10024fa0 size 993 */",
	"playMusic music/fla22k_01_loop",
	"bot_dynamicSkill",
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


def test_qagame_ai_main_lifecycle_aliases_metadata_and_source_are_pinned() -> None:
	ai_main = _read(GAME_AI_MAIN)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_MAIN_LIFECYCLE_FUNCTIONS + AI_MAIN_RETAIL_TRAINING_FUNCTIONS:
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

	for normalized_name in RETAIL_ONLY_NAMES:
		symbol = next(
			entry
			for entry in symbol_map.values()
			if entry["normalized_name"] == normalized_name
		)
		assert "retail-only" in symbol["comment"]

	for normalized_name, (source_signature, source_anchors) in SOURCE_HELPERS.items():
		block = _extract_function_block(ai_main, source_signature)
		for anchor in source_anchors:
			assert anchor in block, normalized_name


def test_qagame_ai_main_lifecycle_hlil_and_ghidra_are_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	decompile_top = _read(QAGAME_DECOMPILE_TOP)

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_FLOW_ANCHORS:
		assert expected in hlil

	for expected in GHIDRA_DECOMPILE_ANCHORS:
		assert expected in decompile_top


def test_qagame_ai_main_lifecycle_botlib_import_wiring_is_pinned() -> None:
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		"G_QL_IMPORT_BOTLIB_SETUP = 49,",
		"G_QL_IMPORT_BOTLIB_SHUTDOWN = 50,",
		"G_QL_IMPORT_BOTLIB_LIBVAR_SET = 51,",
		"G_QL_IMPORT_BOTLIB_START_FRAME = 54,",
		"G_QL_IMPORT_BOTLIB_LOAD_MAP = 55,",
		"G_QL_IMPORT_BOTLIB_UPDATE_ENTITY = 56,",
		"G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE = 59,",
		"G_QL_IMPORT_BOTLIB_USER_COMMAND = 60,",
		"G_QL_IMPORT_BOTLIB_EA_VIEW = 106,",
		"G_QL_IMPORT_BOTLIB_EA_GET_INPUT = 108,",
		"G_QL_IMPORT_BOTLIB_EA_RESET_INPUT = 109,",
		"G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER = 110,",
		"G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE = 119,",
		"G_QL_IMPORT_BOTLIB_AI_LOAD_CHAT_FILE = 134,",
		"G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE = 137,",
		"G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS = 158,",
		"G_QL_IMPORT_BOTLIB_AI_ALLOC_GOAL_STATE = 164,",
		"G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE = 166,",
		"G_QL_IMPORT_BOTLIB_AI_ALLOC_MOVE_STATE = 174,",
		"G_QL_IMPORT_BOTLIB_AI_LOAD_WEAPON_WEIGHTS = 180,",
		"G_QL_IMPORT_BOTLIB_AI_ALLOC_WEAPON_STATE = 181,",
		"G_QL_IMPORT_BOTLIB_AI_RESET_WEAPON_STATE = 183,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_SETUP: return G_QL_IMPORT_BOTLIB_SETUP;",
		"case BOTLIB_SHUTDOWN: return G_QL_IMPORT_BOTLIB_SHUTDOWN;",
		"case BOTLIB_LIBVAR_SET: return G_QL_IMPORT_BOTLIB_LIBVAR_SET;",
		"case BOTLIB_START_FRAME: return G_QL_IMPORT_BOTLIB_START_FRAME;",
		"case BOTLIB_LOAD_MAP: return G_QL_IMPORT_BOTLIB_LOAD_MAP;",
		"case BOTLIB_UPDATENTITY: return G_QL_IMPORT_BOTLIB_UPDATE_ENTITY;",
		"case BOTLIB_GET_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE;",
		"case BOTLIB_USER_COMMAND: return G_QL_IMPORT_BOTLIB_USER_COMMAND;",
		"case BOTLIB_EA_VIEW: return G_QL_IMPORT_BOTLIB_EA_VIEW;",
		"case BOTLIB_EA_GET_INPUT: return G_QL_IMPORT_BOTLIB_EA_GET_INPUT;",
		"case BOTLIB_EA_RESET_INPUT: return G_QL_IMPORT_BOTLIB_EA_RESET_INPUT;",
		"case BOTLIB_AI_LOAD_CHARACTER: return G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER;",
		"case BOTLIB_AI_QUEUE_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE;",
		"case BOTLIB_AI_LOAD_CHAT_FILE: return G_QL_IMPORT_BOTLIB_AI_LOAD_CHAT_FILE;",
		"case BOTLIB_AI_RESET_GOAL_STATE: return G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE;",
		"case BOTLIB_AI_UPDATE_ENTITY_ITEMS: return G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS;",
		"case BOTLIB_AI_ALLOC_GOAL_STATE: return G_QL_IMPORT_BOTLIB_AI_ALLOC_GOAL_STATE;",
		"case BOTLIB_AI_RESET_MOVE_STATE: return G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE;",
		"case BOTLIB_AI_ALLOC_MOVE_STATE: return G_QL_IMPORT_BOTLIB_AI_ALLOC_MOVE_STATE;",
		"case BOTLIB_AI_LOAD_WEAPON_WEIGHTS: return G_QL_IMPORT_BOTLIB_AI_LOAD_WEAPON_WEIGHTS;",
		"case BOTLIB_AI_ALLOC_WEAPON_STATE: return G_QL_IMPORT_BOTLIB_AI_ALLOC_WEAPON_STATE;",
		"case BOTLIB_AI_RESET_WEAPON_STATE: return G_QL_IMPORT_BOTLIB_AI_RESET_WEAPON_STATE;",
		"return syscall( BOTLIB_SETUP );",
		"return syscall( BOTLIB_SHUTDOWN );",
		"return syscall( BOTLIB_LIBVAR_SET, var_name, value );",
		"return syscall( BOTLIB_START_FRAME, PASSFLOAT( time ) );",
		"return syscall( BOTLIB_LOAD_MAP, mapname );",
		"return syscall( BOTLIB_UPDATENTITY, ent, bue );",
		"return syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );",
		"syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );",
		"syscall( BOTLIB_EA_VIEW, client, viewangles );",
		"syscall( BOTLIB_EA_GET_INPUT, client, PASSFLOAT(thinktime), input );",
		"syscall( BOTLIB_EA_RESET_INPUT, client );",
		"return syscall( BOTLIB_AI_LOAD_CHARACTER, charfile, PASSFLOAT(skill));",
		"syscall( BOTLIB_AI_QUEUE_CONSOLE_MESSAGE, chatstate, type, message );",
		"return syscall( BOTLIB_AI_LOAD_CHAT_FILE, chatstate, chatfile, chatname );",
		"syscall( BOTLIB_AI_RESET_GOAL_STATE, goalstate );",
		"syscall( BOTLIB_AI_UPDATE_ENTITY_ITEMS );",
		"return syscall( BOTLIB_AI_ALLOC_GOAL_STATE, state );",
		"syscall( BOTLIB_AI_RESET_MOVE_STATE, movestate );",
		"return syscall( BOTLIB_AI_ALLOC_MOVE_STATE );",
		"return syscall( BOTLIB_AI_LOAD_WEAPON_WEIGHTS, weaponstate, filename );",
		"return syscall( BOTLIB_AI_ALLOC_WEAPON_STATE );",
		"syscall( BOTLIB_AI_RESET_WEAPON_STATE, weaponstate );",
	):
		assert expected in game_syscalls

	for expected in (
		"[BOTLIB_SETUP] = (ql_import_f)QL_G_trap_BotLibSetup,",
		"[BOTLIB_SHUTDOWN] = (ql_import_f)QL_G_trap_BotLibShutdown,",
		"[BOTLIB_LIBVAR_SET] = (ql_import_f)QL_G_trap_BotLibVarSet,",
		"[BOTLIB_START_FRAME] = (ql_import_f)QL_G_trap_BotLibStartFrame,",
		"[BOTLIB_LOAD_MAP] = (ql_import_f)QL_G_trap_BotLibLoadMap,",
		"[BOTLIB_UPDATENTITY] = (ql_import_f)QL_G_trap_BotLibUpdateEntity,",
		"[BOTLIB_GET_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotGetServerCommand,",
		"[BOTLIB_USER_COMMAND] = (ql_import_f)QL_G_trap_BotUserCommand,",
		"[BOTLIB_EA_VIEW] = (ql_import_f)QL_G_trap_EA_View,",
		"[BOTLIB_EA_GET_INPUT] = (ql_import_f)QL_G_trap_EA_GetInput,",
		"[BOTLIB_EA_RESET_INPUT] = (ql_import_f)QL_G_trap_EA_ResetInput,",
		"[BOTLIB_AI_LOAD_CHARACTER] = (ql_import_f)QL_G_trap_BotLoadCharacter,",
		"[BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage,",
		"[BOTLIB_AI_LOAD_CHAT_FILE] = (ql_import_f)QL_G_trap_BotLoadChatFile,",
		"[BOTLIB_AI_RESET_GOAL_STATE] = (ql_import_f)QL_G_trap_BotResetGoalState,",
		"[BOTLIB_AI_UPDATE_ENTITY_ITEMS] = (ql_import_f)QL_G_trap_BotUpdateEntityItems,",
		"[BOTLIB_AI_ALLOC_GOAL_STATE] = (ql_import_f)QL_G_trap_BotAllocGoalState,",
		"[BOTLIB_AI_RESET_MOVE_STATE] = (ql_import_f)QL_G_trap_BotResetMoveState,",
		"[BOTLIB_AI_ALLOC_MOVE_STATE] = (ql_import_f)QL_G_trap_BotAllocMoveState,",
		"[BOTLIB_AI_LOAD_WEAPON_WEIGHTS] = (ql_import_f)QL_G_trap_BotLoadWeaponWeights,",
		"[BOTLIB_AI_ALLOC_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotAllocWeaponState,",
		"[BOTLIB_AI_RESET_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotResetWeaponState,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_SETUP] = (ql_import_f)QL_G_trap_BotLibSetup;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_SHUTDOWN] = (ql_import_f)QL_G_trap_BotLibShutdown;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_LIBVAR_SET] = (ql_import_f)QL_G_trap_BotLibVarSet;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_START_FRAME] = (ql_import_f)QL_G_trap_BotLibStartFrame;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_LOAD_MAP] = (ql_import_f)QL_G_trap_BotLibLoadMap;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_UPDATE_ENTITY] = (ql_import_f)QL_G_trap_BotLibUpdateEntity;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotGetServerCommand;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_USER_COMMAND] = (ql_import_f)QL_G_trap_BotUserCommand;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER] = (ql_import_f)QL_G_trap_BotLoadCharacter;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_CHAT_FILE] = (ql_import_f)QL_G_trap_BotLoadChatFile;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE] = (ql_import_f)QL_G_trap_BotResetGoalState;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS] = (ql_import_f)QL_G_trap_BotUpdateEntityItems;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_GOAL_STATE] = (ql_import_f)QL_G_trap_BotAllocGoalState;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE] = (ql_import_f)QL_G_trap_BotResetMoveState;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_MOVE_STATE] = (ql_import_f)QL_G_trap_BotAllocMoveState;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_WEAPON_WEIGHTS] = (ql_import_f)QL_G_trap_BotLoadWeaponWeights;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ALLOC_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotAllocWeaponState;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_WEAPON_STATE] = (ql_import_f)QL_G_trap_BotResetWeaponState;",
	):
		assert expected in server_game

	for expected in (
		"return G_Import_Syscall( BOTLIB_SETUP );",
		"return G_Import_Syscall( BOTLIB_SHUTDOWN );",
		"return G_Import_Syscall( BOTLIB_LIBVAR_SET, var_name, value );",
		"return G_Import_Syscall( BOTLIB_START_FRAME, QL_G_PASSFLOAT( time ) );",
		"return G_Import_Syscall( BOTLIB_LOAD_MAP, mapname );",
		"return G_Import_Syscall( BOTLIB_UPDATENTITY, ent, bue );",
		"return G_Import_Syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );",
		"G_Import_Syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );",
		"G_Import_Syscall( BOTLIB_EA_VIEW, client, viewangles );",
		"G_Import_Syscall( BOTLIB_EA_GET_INPUT, client, QL_G_PASSFLOAT(thinktime), input );",
		"G_Import_Syscall( BOTLIB_EA_RESET_INPUT, client );",
		"return G_Import_Syscall( BOTLIB_AI_LOAD_CHARACTER, charfile, QL_G_PASSFLOAT(skill));",
		"G_Import_Syscall( BOTLIB_AI_QUEUE_CONSOLE_MESSAGE, chatstate, type, message );",
		"return G_Import_Syscall( BOTLIB_AI_LOAD_CHAT_FILE, chatstate, chatfile, chatname );",
		"G_Import_Syscall( BOTLIB_AI_RESET_GOAL_STATE, goalstate );",
		"G_Import_Syscall( BOTLIB_AI_UPDATE_ENTITY_ITEMS );",
		"return G_Import_Syscall( BOTLIB_AI_ALLOC_GOAL_STATE, state );",
		"G_Import_Syscall( BOTLIB_AI_RESET_MOVE_STATE, movestate );",
		"return G_Import_Syscall( BOTLIB_AI_ALLOC_MOVE_STATE );",
		"return G_Import_Syscall( BOTLIB_AI_LOAD_WEAPON_WEIGHTS, weaponstate, filename );",
		"return G_Import_Syscall( BOTLIB_AI_ALLOC_WEAPON_STATE );",
		"G_Import_Syscall( BOTLIB_AI_RESET_WEAPON_STATE, weaponstate );",
	):
		assert expected in ql_game_imports
