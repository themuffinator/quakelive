from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_VCMD = REPO_ROOT / "src" / "code" / "game" / "ai_vcmd.c"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_BOT = REPO_ROOT / "src" / "code" / "game" / "g_bot.c"
GAME_LOCAL = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
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


VOICE_COMMAND_FUNCTIONS = (
	("1002b9b0", "FUN_1002b9b0", "BotVoiceChat_GetFlag", "void BotVoiceChat_GetFlag(bot_state_t *bs, int client, int mode)", 238, ("FUN_1002b9b0", "sub_1002b9b0")),
	("1002baa0", "sub_1002baa0", "BotVoiceChat_Offense", "void BotVoiceChat_Offense(bot_state_t *bs, int client, int mode)", None, ("FUN_1002baa0", "sub_1002baa0")),
	("1002bbc0", "FUN_1002bbc0", "BotVoiceChat_Defend", "void BotVoiceChat_Defend(bot_state_t *bs, int client, int mode)", 318, ("FUN_1002bbc0", "sub_1002bbc0")),
	("1002bd00", "j_sub_1002bbc0", "BotVoiceChat_DefendFlag", "void BotVoiceChat_DefendFlag(bot_state_t *bs, int client, int mode)", None, ("j_sub_1002bbc0", "sub_1002bd00")),
	("1002bd10", "sub_1002bd10", "BotVoiceChat_Patrol", "void BotVoiceChat_Patrol(bot_state_t *bs, int client, int mode)", None, ("FUN_1002bd10", "sub_1002bd10")),
	("1002be10", "sub_1002be10", "BotVoiceChat_Camp", "void BotVoiceChat_Camp(bot_state_t *bs, int client, int mode)", None, ("FUN_1002be10", "sub_1002be10")),
	("1002c010", "FUN_1002c010", "BotVoiceChat_FollowMe", "void BotVoiceChat_FollowMe(bot_state_t *bs, int client, int mode)", 566, ("FUN_1002c010", "sub_1002c010")),
	("1002c250", "sub_1002c250", "BotVoiceChat_FollowFlagCarrier", "void BotVoiceChat_FollowFlagCarrier(bot_state_t *bs, int client, int mode)", None, ("FUN_1002c250", "sub_1002c250")),
	("1002c310", "FUN_1002c310", "BotVoiceChat_ReturnFlag", "void BotVoiceChat_ReturnFlag(bot_state_t *bs, int client, int mode)", 164, ("FUN_1002c310", "sub_1002c310")),
	("1002c3c0", "sub_1002c3c0", "BotVoiceChat_StartLeader", "void BotVoiceChat_StartLeader(bot_state_t *bs, int client, int mode)", None, ("FUN_1002c3c0", "sub_1002c3c0")),
	("1002c3f0", "sub_1002c3f0", "BotVoiceChat_StopLeader", "void BotVoiceChat_StopLeader(bot_state_t *bs, int client, int mode)", None, ("FUN_1002c3f0", "sub_1002c3f0")),
	("1002c470", "sub_1002c470", "BotVoiceChat_WhoIsLeader", "void BotVoiceChat_WhoIsLeader(bot_state_t *bs, int client, int mode)", None, ("FUN_1002c470", "sub_1002c470")),
	("1002c530", "FUN_1002c530", "BotVoiceChat_WantOnDefense", "void BotVoiceChat_WantOnDefense(bot_state_t *bs, int client, int mode)", 329, ("FUN_1002c530", "sub_1002c530")),
	("1002c680", "FUN_1002c680", "BotVoiceChat_WantOnOffense", "void BotVoiceChat_WantOnOffense(bot_state_t *bs, int client, int mode)", 329, ("FUN_1002c680", "sub_1002c680")),
	("1002c7d0", "FUN_1002c7d0", "BotVoiceChatCommand", "int BotVoiceChatCommand(bot_state_t *bs, int mode, char *voiceChat)", 379, ("FUN_1002c7d0", "sub_1002c7d0")),
)


BOT_SPAWN_FUNCTIONS = (
	("100367c0", "FUN_100367c0", "G_ParseInfos", "int G_ParseInfos(char *buf, int max, char *infos[])", 602, ("FUN_100367c0", "sub_100367c0")),
	("10036a20", "FUN_10036a20", "G_AddRandomBot", "void G_AddRandomBot(int team)", 636, ("FUN_10036a20", "sub_10036a20")),
	("10036cb0", "FUN_10036cb0", "G_RemoveRandomBot", "int G_RemoveRandomBot(int team)", 190, ("FUN_10036cb0", "sub_10036cb0")),
	("10036d80", "FUN_10036d80", "G_CountHumanPlayers", "int G_CountHumanPlayers(int team)", 82, ("FUN_10036d80", "sub_10036d80")),
	("10036de0", "FUN_10036de0", "G_CountBotPlayers", "int G_CountBotPlayers(int team)", 156, ("FUN_10036de0", "sub_10036de0")),
	("10036e80", "FUN_10036e80", "G_CheckMinimumPlayers", "void G_CheckMinimumPlayers(void)", 681, ("FUN_10036e80", "sub_10036e80")),
	("10037130", "FUN_10037130", "G_CheckBotSpawn", "void G_CheckBotSpawn(void)", 58, ("FUN_10037130", "sub_10037130")),
	("10037170", "FUN_10037170", "AddBotToSpawnQueue", "void AddBotToSpawnQueue(int clientNum, int delay)", 540, ("FUN_10037170", "sub_10037170")),
	("100373b0", "FUN_100373b0", "G_BotConnect", "qboolean G_BotConnect(int clientNum, qboolean restart)", 288, ("FUN_100373b0", "sub_100373b0")),
	("100374d0", "FUN_100374d0", "G_GetBotInfoByName", "char *G_GetBotInfoByName(const char *name)", 78, ("FUN_100374d0", "sub_100374d0")),
	("10037520", "FUN_10037520", "G_AddBot", "void G_AddBot(const char *name, float skill, const char *team, int delay, char *altname)", 948, ("FUN_10037520", "sub_10037520")),
	("100378e0", "FUN_100378e0", "G_AddTrainerBot", "int G_AddTrainerBot(void)", 46, ("FUN_100378e0", "sub_100378e0")),
	("10037910", "FUN_10037910", "Svcmd_AddBot_f", "void Svcmd_AddBot_f(void)", 512, ("FUN_10037910", "sub_10037910")),
	("10037b10", "FUN_10037b10", "Svcmd_BotList_f", "void Svcmd_BotList_f(void)", 479, ("FUN_10037b10", "sub_10037b10")),
	("10037d00", "FUN_10037d00", "G_LoadBotsFromFile", "void G_LoadBotsFromFile(char *filename)", 271, ("FUN_10037d00", "sub_10037d00")),
	("10037e10", "FUN_10037e10", "G_LoadBots", "void G_LoadBots(void)", 354, ("FUN_10037e10", "sub_10037e10")),
)


VOICE_SOURCE_ANCHORS = {
	"BotVoiceChat_GetFlag": (
		"if (gametype == GT_CTF)",
		"else if (gametype == GT_1FCTF)",
		"bs->ltgtype = LTG_GETFLAG;",
		"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
		"BotRememberLastOrderedTask(bs);",
	),
	"BotVoiceChat_Offense": (
		"BotVoiceChat_GetFlag(bs, client, mode);",
		"bs->ltgtype = LTG_HARVEST;",
		"bs->harvestaway_time = 0;",
		"bs->ltgtype = LTG_ATTACKENEMYBASE;",
		"bs->attackaway_time = 0;",
	),
	"BotVoiceChat_Defend": (
		"case TEAM_RED: memcpy(&bs->teamgoal, &redobelisk, sizeof(bot_goal_t)); break;",
		"case TEAM_BLUE: memcpy(&bs->teamgoal, &blueobelisk, sizeof(bot_goal_t)); break;",
		"case TEAM_RED: memcpy(&bs->teamgoal, &ctf_redflag, sizeof(bot_goal_t)); break;",
		"case TEAM_BLUE: memcpy(&bs->teamgoal, &ctf_blueflag, sizeof(bot_goal_t)); break;",
		"bs->ltgtype = LTG_DEFENDKEYAREA;",
		"bs->defendaway_time = 0;",
	),
	"BotVoiceChat_DefendFlag": (
		"BotVoiceChat_Defend(bs, client, mode);",
	),
	"BotVoiceChat_Patrol": (
		"bs->decisionmaker = client;",
		"bs->ltgtype = 0;",
		"bs->lead_time = 0;",
		"BotAI_BotInitialChat(bs, \"dismissed\", NULL);",
		"BotVoiceChatOnly(bs, -1, VOICECHAT_ONPATROL);",
	),
	"BotVoiceChat_Camp": (
		"BotEntityInfo(client, &entinfo);",
		"areanum = BotPointAreaNum(entinfo.origin);",
		"BotAI_BotInitialChat(bs, \"whereareyou\", EasyClientName(client, netname, sizeof(netname)), NULL);",
		"bs->ltgtype = LTG_CAMPORDER;",
		"bs->teammate = client;",
		"bs->arrive_time = 0;",
	),
	"BotVoiceChat_FollowMe": (
		"BotEntityInfo(client, &entinfo);",
		"areanum = BotPointAreaNum(entinfo.origin);",
		"BotAI_BotInitialChat(bs, \"whereareyou\", EasyClientName(client, netname, sizeof(netname)), NULL);",
		"bs->ltgtype = LTG_TEAMACCOMPANY;",
		"bs->formation_dist = 3.5 * 32;",
		"bs->arrive_time = 0;",
	),
	"BotVoiceChat_FollowFlagCarrier": (
		"carrier = BotTeamFlagCarrier(bs);",
		"BotVoiceChat_FollowMe(bs, carrier, mode);",
	),
	"BotVoiceChat_ReturnFlag": (
		"gametype != GT_CTF",
		"gametype != GT_1FCTF",
		"bs->ltgtype = LTG_RETURNFLAG;",
		"bs->teamgoal_time = FloatTime() + CTF_RETURNFLAG_TIME;",
		"bs->rushbaseaway_time = 0;",
	),
	"BotVoiceChat_StartLeader": (
		"ClientName(client, bs->teamleader, sizeof(bs->teamleader));",
	),
	"BotVoiceChat_StopLeader": (
		"if (!Q_stricmp(bs->teamleader, ClientName(client, netname, sizeof(netname))))",
		"bs->teamleader[0] = '\\0';",
		"notleader[client] = qtrue;",
	),
	"BotVoiceChat_WhoIsLeader": (
		"if (!TeamPlayIsOn()) return;",
		"if (!Q_stricmp(netname, bs->teamleader))",
		"BotAI_BotInitialChat(bs, \"iamteamleader\", NULL);",
		"BotVoiceChatOnly(bs, -1, VOICECHAT_STARTLEADER);",
	),
	"BotVoiceChat_WantOnDefense": (
		"preference &= ~TEAMTP_ATTACKER;",
		"preference |= TEAMTP_DEFENDER;",
		"BotSetTeamMateTaskPreference(bs, client, preference);",
		"BotAI_BotInitialChat(bs, \"keepinmind\", netname, NULL);",
		"trap_EA_Action(bs->client, ACTION_AFFIRMATIVE);",
	),
	"BotVoiceChat_WantOnOffense": (
		"preference &= ~TEAMTP_DEFENDER;",
		"preference |= TEAMTP_ATTACKER;",
		"BotSetTeamMateTaskPreference(bs, client, preference);",
		"BotAI_BotInitialChat(bs, \"keepinmind\", netname, NULL);",
		"trap_EA_Action(bs->client, ACTION_AFFIRMATIVE);",
	),
	"BotVoiceChatCommand": (
		"if (!TeamPlayIsOn())",
		"if ( mode == SAY_ALL )",
		"Q_strncpyz(buf, voiceChat, sizeof(buf));",
		"voiceOnly = atoi(ptr);",
		"clientNum = atoi(ptr);",
		"color = atoi(ptr);",
		"if (!BotSameTeam(bs, clientNum))",
		"if (!Q_stricmp(cmd, voiceCommands[i].cmd))",
		"voiceCommands[i].func(bs, clientNum, mode);",
	),
}


BOT_SPAWN_SOURCE_ANCHORS = {
	"G_ParseInfos": (
		"Com_Printf( \"Missing { in info file\\n\" );",
		"Com_Printf( \"Max infos exceeded\\n\" );",
		"Com_Printf( \"Unexpected end of info file\\n\" );",
		"infos[count] = G_Alloc(strlen(info) + strlen(\"\\\\num\\\\\") + strlen(va(\"%d\", MAX_ARENAS)) + 1);",
	),
	"G_AddRandomBot": (
		"if ( !(g_entities[cl->ps.clientNum].r.svFlags & SVF_BOT) )",
		"skill = trap_Cvar_VariableValue( \"g_spSkill\" );",
		"Q_CleanStr(netname);",
		"trap_SendConsoleCommand( EXEC_INSERT, va(\"addbot %s %f %s %i\\n\", netname, skill, teamstr, 0) );",
	),
	"G_RemoveRandomBot": (
		"if ( !(g_entities[cl->ps.clientNum].r.svFlags & SVF_BOT) )",
		"trap_SendConsoleCommand( EXEC_INSERT, va( \"clientkick %d\\n\", i ) );",
		"return qtrue;",
	),
	"G_CountHumanPlayers": (
		"if ( g_entities[cl->ps.clientNum].r.svFlags & SVF_BOT )",
		"if ( team >= 0 && cl->sess.sessionTeam != team )",
		"num++;",
	),
	"G_CountBotPlayers": (
		"if ( !(g_entities[cl->ps.clientNum].r.svFlags & SVF_BOT) )",
		"for( n = 0; n < BOT_SPAWN_QUEUE_DEPTH; n++ )",
		"if ( botSpawnQueue[n].spawnTime > level.time )",
		"num++;",
	),
	"G_CheckMinimumPlayers": (
		"if (checkminimumplayers_time > level.time - 1000)",
		"if (G_ConsumeBotSpawnList()) return;",
		"G_AddRandomBot( TEAM_RED );",
		"G_RemoveRandomBot( TEAM_BLUE );",
		"G_RemoveRandomBot( TEAM_SPECTATOR )",
		"G_AddRandomBot( TEAM_FREE );",
	),
	"G_CheckBotSpawn": (
		"G_CheckMinimumPlayers();",
		"ClientBegin( botSpawnQueue[n].clientNum );",
		"botSpawnQueue[n].spawnTime = 0;",
		"PlayerIntroSound( Info_ValueForKey (userinfo, \"model\") );",
	),
	"AddBotToSpawnQueue": (
		"if( !botSpawnQueue[n].spawnTime )",
		"botSpawnQueue[n].spawnTime = level.time + delay;",
		"botSpawnQueue[n].clientNum = clientNum;",
		"G_Printf( S_COLOR_YELLOW \"Unable to delay spawn\\n\" );",
		"ClientBegin( clientNum );",
	),
	"G_BotConnect": (
		"trap_GetUserinfo( clientNum, userinfo, sizeof(userinfo) );",
		"Q_strncpyz( settings.characterfile, Info_ValueForKey( userinfo, \"characterfile\" ), sizeof(settings.characterfile) );",
		"settings.skill = atof( Info_ValueForKey( userinfo, \"skill\" ) );",
		"Q_strncpyz( settings.team, Info_ValueForKey( userinfo, \"team\" ), sizeof(settings.team) );",
		"trap_DropClient( clientNum, \"BotAISetupClient failed\" );",
	),
	"G_GetBotInfoByName": (
		"for ( n = 0; n < g_numBots ; n++ )",
		"if ( !Q_stricmp( value, name ) )",
		"return g_botInfos[n];",
	),
	"G_AddBot": (
		"G_GetBotInfoByName( name );",
		"G_Printf( S_COLOR_RED \"Error: Bot '%s' not defined\\n\", name );",
		"Info_SetValueForKey( userinfo, \"rate\", \"25000\" );",
		"Info_SetValueForKey( userinfo, \"snaps\", \"20\" );",
		"trap_BotAllocateClient();",
		"if( PickTeam(clientNum) == TEAM_RED)",
		"bot->r.svFlags |= SVF_BOT;",
		"trap_SetUserinfo( clientNum, userinfo );",
		"ClientBegin( clientNum );",
		"AddBotToSpawnQueue( clientNum, delay );",
	),
	"G_AddTrainerBot": (
		"skill = trap_Cvar_VariableValue( \"g_spSkill\" );",
		"trap_Cvar_Set( \"g_spSkill\", \"1\" );",
		"trap_Cvar_Set( \"g_spSkill\", \"5\" );",
		"G_AddBot( \"Trainer\", skill, \"\", 5000, \"\" );",
		"trap_SendServerCommand( -1, \"loaddeferred\\n\" );",
	),
	"Svcmd_AddBot_f": (
		"if ( !trap_Cvar_VariableIntegerValue( \"bot_enable\" ) )",
		"if ( level.trainingMapActive )",
		"trap_Printf( \"Usage: Addbot <botname> [skill 1-5] [team] [msec delay] [altname]\\n\" );",
		"trap_Argv( 5, altname, sizeof( altname ) );",
		"G_AddBot( name, skill, team, delay, altname );",
		"trap_Cvar_VariableIntegerValue( \"cl_running\" )",
		"trap_SendServerCommand( -1, \"loaddeferred\\n\" );",
	),
	"Svcmd_BotList_f": (
		"trap_Printf(\"^1name             model            aifile              funname\\n\");",
		"strcpy(name, \"UnnamedPlayer\");",
		"strcpy(model, \"visor/default\");",
		"strcpy(aifile, \"bots/default_c.c\");",
		"trap_Printf(va(\"%-16s %-16s %-20s %-20s\\n\", name, model, aifile, funname));",
	),
	"G_LoadBotsFromFile": (
		"len = trap_FS_FOpenFile( filename, &f, FS_READ );",
		"trap_Printf( va( S_COLOR_RED \"file not found: %s\\n\", filename ) );",
		"trap_Printf( va( S_COLOR_RED \"file too large: %s is %i, max allowed is %i\", filename, len, MAX_BOTS_TEXT ) );",
		"trap_FS_Read( buf, len, f );",
		"g_numBots += G_ParseInfos( buf, MAX_BOTS - g_numBots, &g_botInfos[g_numBots] );",
	),
	"G_LoadBots": (
		"if ( !trap_Cvar_VariableIntegerValue( \"bot_enable\" ) )",
		"G_LoadBotsFromFile( g_botsFile.string );",
		"G_LoadBotsFromFile( \"scripts/bots.txt\" );",
		"numdirs = trap_FS_GetFileList(\"scripts\", \".bot\", dirlist, 1024 );",
		"trap_Printf( va( \"%i bots parsed\\n\", g_numBots ) );",
	),
}


SOURCE_SIGNATURES = {
	"BotVoiceChat_GetFlag": "void BotVoiceChat_GetFlag(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_Offense": "void BotVoiceChat_Offense(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_Defend": "void BotVoiceChat_Defend(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_DefendFlag": "void BotVoiceChat_DefendFlag(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_Patrol": "void BotVoiceChat_Patrol(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_Camp": "void BotVoiceChat_Camp(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_FollowMe": "void BotVoiceChat_FollowMe(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_FollowFlagCarrier": "void BotVoiceChat_FollowFlagCarrier(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_ReturnFlag": "void BotVoiceChat_ReturnFlag(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_StartLeader": "void BotVoiceChat_StartLeader(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_StopLeader": "void BotVoiceChat_StopLeader(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_WhoIsLeader": "void BotVoiceChat_WhoIsLeader(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_WantOnDefense": "void BotVoiceChat_WantOnDefense(bot_state_t *bs, int client, int mode)",
	"BotVoiceChat_WantOnOffense": "void BotVoiceChat_WantOnOffense(bot_state_t *bs, int client, int mode)",
	"BotVoiceChatCommand": "int BotVoiceChatCommand(bot_state_t *bs, int mode, char *voiceChat)",
	"G_ParseInfos": "int G_ParseInfos( char *buf, int max, char *infos[] )",
	"G_AddRandomBot": "void G_AddRandomBot( int team )",
	"G_RemoveRandomBot": "int G_RemoveRandomBot( int team )",
	"G_CountHumanPlayers": "int G_CountHumanPlayers( int team )",
	"G_CountBotPlayers": "int G_CountBotPlayers( int team )",
	"G_CheckMinimumPlayers": "void G_CheckMinimumPlayers( void )",
	"G_CheckBotSpawn": "void G_CheckBotSpawn( void )",
	"AddBotToSpawnQueue": "static void AddBotToSpawnQueue( int clientNum, int delay )",
	"G_BotConnect": "qboolean G_BotConnect( int clientNum, qboolean restart )",
	"G_GetBotInfoByName": "char *G_GetBotInfoByName( const char *name )",
	"G_AddBot": "static void G_AddBot( const char *name, float skill, const char *team, int delay, char *altname)",
	"G_AddTrainerBot": "void G_AddTrainerBot( void )",
	"Svcmd_AddBot_f": "void Svcmd_AddBot_f( void )",
	"Svcmd_BotList_f": "void Svcmd_BotList_f( void )",
	"G_LoadBotsFromFile": "static void G_LoadBotsFromFile( char *filename )",
	"G_LoadBots": "static void G_LoadBots( void )",
}


VOICE_HLIL_ANCHORS = (
	"1002b9b0    int32_t sub_1002b9b0(void* arg1, int32_t arg2)",
	"1002baa0    int32_t sub_1002baa0(void* arg1, int32_t arg2)",
	"1002bbc0    int32_t sub_1002bbc0(void* arg1, int32_t arg2)",
	"1002bd00    int32_t j_sub_1002bbc0(void* arg1, int32_t arg2)",
	"1002bd00  return sub_1002bbc0(arg1, arg2) __tailcall",
	"1002bd10    int32_t sub_1002bd10(void* arg1, int32_t arg2)",
	'1002bd5a  sub_10020dc0(arg1, "dismissed", 0)',
	'1002bd87  int32_t eax_3 = sub_10070cb0("vosay_team %s")',
	"1002be10    int32_t sub_1002be10(void* arg1, int32_t arg2)",
	'1002bf0d      sub_10020dc0(arg1, "whereareyou", sub_10015df0(arg2, 0x28))',
	"1002c010    int32_t sub_1002c010(void* arg1, int32_t arg2)",
	'1002c109      sub_10020dc0(arg1, "whereareyou", sub_10015df0(arg2, 0x28))',
	"1002c250    int32_t sub_1002c250(void* arg1, int32_t arg2)",
	"1002c2e6                          result = sub_1002c010(arg1, i)",
	"1002c310    int32_t sub_1002c310(void* arg1, int32_t arg2)",
	"1002c3c0    char* sub_1002c3c0(void* arg1, int32_t arg2)",
	"1002c3e0  return sub_10015ad0(arg1 + 0x1af4, 0x20, arg2)",
	"1002c3f0    char* sub_1002c3f0(void* arg1, int32_t arg2)",
	"1002c443          *((arg2 << 2) + &data_105e9de0) = 1",
	"1002c470    void* sub_1002c470(void* arg1)",
	'1002c4c8              sub_10020dc0(arg1, "iamteamleader", result)',
	'1002c4f6              int32_t eax_3 = sub_10070cb0("vosay_team %s")',
	"1002c530    int32_t sub_1002c530(void* arg1, int32_t arg2)",
	"1002c5a6  *(ebx_3 + &data_105e20a4) = (eax_3 & 0xfffffffd) | 1",
	'1002c5e5  sub_10020dc0(esi_3, "keepinmind", &var_2c)',
	"1002c680    int32_t sub_1002c680(void* arg1, int32_t arg2)",
	"1002c6f6  *(ebx_3 + &data_105e20a4) = (eax_3 & 0xfffffffe) | 2",
	'1002c735  sub_10020dc0(esi_3, "keepinmind", &var_2c)',
	'1002c787      int32_t eax_12 = sub_10070cb0("votell %d %s")',
	"1002c7d0    int32_t __convention(\"regparm\") sub_1002c7d0(int32_t arg1, int32_t arg2, int32_t arg3, void* arg4, int32_t arg5)",
	"1002c819  if (data_105e4ae8 s< 3 || arg5 == 0)",
	"1002c8e5  eax_5, edx_1 = sub_10018900(eax_4, edx, ebx, arg4)",
	"1002c8f1      eax_6 = data_10090200",
	"1002c93f              (&data_10090204)[edi_1 * 2](arg4, ebx, arg5)",
)


BOT_SPAWN_HLIL_ANCHORS = (
	'100367c0    int32_t __convention("regparm") sub_100367c0(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, int32_t arg5)',
	"10036a20    int32_t sub_10036a20(int32_t arg1)",
	'10036c8a      result = (*data_104b13ac)(sub_10070cb0("addbot %s %f %s %i\\n"))',
	"10036cb0    int32_t __fastcall sub_10036cb0(int32_t arg1, int32_t arg2)",
	'10036d59              (*data_104b13ac)(sub_10070cb0("clientkick %i\\n"))',
	"10036d80    int32_t sub_10036d80(int32_t arg1 @ esi)",
	'10036de0    int32_t __convention("regparm") sub_10036de0(int32_t arg1)',
	"10036e80    int32_t sub_10036e80(long double arg1 @ st0)",
	"10037035                          int32_t eax_17 = sub_10036a20(1)",
	"100370c5                          eax_1, ecx_15 = sub_10036cb0(ecx_16, 3)",
	"10037130    int32_t sub_10037130()",
	"10037131  sub_10036e80(x87_r0)",
	"10037170    int32_t sub_10037170(int32_t arg1, int32_t arg2)",
	'10037198  sub_10053140("^3Unable to delay spawn\\n")',
	"100373b0    int32_t sub_100373b0(long double arg1 @ st0, int32_t arg2, int32_t arg3)",
	'100374a9      (*(data_104b13ac + 0x5c))(arg2, "BotAISetupClient failed")',
	"100374d0    int32_t sub_100374d0(char* arg1 @ edi)",
	'10037520    int32_t __convention("regparm") sub_10037520(int32_t arg1, char* arg2, char* arg3, float arg4 @ xmm0, char* arg5, int32_t arg6)',
	"10037559  if (sub_100374d0(arg3) == 0)",
	"1003778a  void* eax_18 = (*(data_104b13ac + 0xac))()",
	"100378b7      eax_29 = sub_10037170(eax_18, arg6)",
	"100378e0    int32_t sub_100378e0()",
	'100378f4  sub_10037520(eax, &data_1007c414, "Trainer", xmm0, &data_1007c414, 0x1388)',
	'1003790d  return (*(data_104b13ac + 0x60))(0xffffffff, "loaddeferred\\n")',
	"10037910    int32_t __stdcall sub_10037910(long double arg1 @ st0, long double arg2 @ st2, char const* const arg3)",
	"10037b10    int32_t sub_10037b10()",
	"10037d00    int32_t sub_10037d00()",
	"10037e10    int32_t sub_10037e10(long double arg1 @ st0)",
	"10037f53      result = sub_10053140(sub_10070cb0(\"%i bots parsed\\n\"))",
)


BOT_SPAWN_GHIDRA_ANCHORS = (
	"/* FUN_10036a20 @ 10036a20 size 636 */",
	'void FUN_10036a20(int param_1)',
	'uVar8 = FUN_10070cb0("addbot %s %f %s %i\\n",abStack_28,(double)local_30,puVar12,0);',
	"/* FUN_10036e80 @ 10036e80 size 681 */",
	"void FUN_10036e80(void)",
	'uVar4 = FUN_10070cb0("addbot %s %f %s %i\\n",pcVar2,(double)fStack_1c,&DAT_1007c414,0);',
	"FUN_10036a20(0);",
	"FUN_10036a20(2);",
	"FUN_10036a20(1);",
	"/* FUN_10037520 @ 10037520 size 948 */",
	"void __thiscall FUN_10037520(undefined4 param_1,char *param_2,int param_3)",
	"FUN_10037170(iVar1,param_3);",
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
	in_string = False
	in_char = False
	escaped = False
	for index in range(brace_start, len(scan_text)):
		char = scan_text[index]
		if escaped:
			escaped = False
			continue
		if in_string:
			if char == "\\":
				escaped = True
			elif char == '"':
				in_string = False
			continue
		if in_char:
			if char == "\\":
				escaped = True
			elif char == "'":
				in_char = False
			continue
		if char == '"':
			in_string = True
		elif char == "'":
			in_char = True
		elif char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return scan_text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _function_rows_by_entry(path: Path) -> dict[str, dict[str, str]]:
	with path.open(newline="", encoding="utf-8") as file:
		return {row["entry"].lower(): row for row in csv.DictReader(file)}


def _assert_mapping_rows(entries: tuple[tuple[str, str, str, str, int | None, tuple[str, ...]], ...]) -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)

	for address, raw_name, normalized_name, signature, size, alias_keys in entries:
		for alias_key in alias_keys:
			assert aliases[alias_key] == normalized_name

		symbol = symbol_map[f"0x{address}"]
		assert symbol["raw_name"] == raw_name
		assert symbol["normalized_name"] == normalized_name
		assert symbol["status"] == "matched"
		assert symbol["signature"] == signature

		if size is not None:
			row = function_rows[address]
			assert row["name"] == raw_name
			assert int(row["size"]) == size
			assert row["thunk"] == "0"


def test_qagame_voice_command_aliases_metadata_and_source_are_pinned() -> None:
	ai_vcmd = _read(GAME_AI_VCMD)

	_assert_mapping_rows(VOICE_COMMAND_FUNCTIONS)

	for _, _, normalized_name, _, _, _ in VOICE_COMMAND_FUNCTIONS:
		block = _extract_function_block(ai_vcmd, SOURCE_SIGNATURES[normalized_name])
		for anchor in VOICE_SOURCE_ANCHORS[normalized_name]:
			assert anchor in block, normalized_name

	voice_table = _read(GAME_AI_VCMD)
	for token, handler in (
		("VOICECHAT_GETFLAG", "BotVoiceChat_GetFlag"),
		("VOICECHAT_OFFENSE", "BotVoiceChat_Offense"),
		("VOICECHAT_DEFEND", "BotVoiceChat_Defend"),
		("VOICECHAT_DEFENDFLAG", "BotVoiceChat_DefendFlag"),
		("VOICECHAT_PATROL", "BotVoiceChat_Patrol"),
		("VOICECHAT_CAMP", "BotVoiceChat_Camp"),
		("VOICECHAT_FOLLOWME", "BotVoiceChat_FollowMe"),
		("VOICECHAT_FOLLOWFLAGCARRIER", "BotVoiceChat_FollowFlagCarrier"),
		("VOICECHAT_RETURNFLAG", "BotVoiceChat_ReturnFlag"),
		("VOICECHAT_STARTLEADER", "BotVoiceChat_StartLeader"),
		("VOICECHAT_STOPLEADER", "BotVoiceChat_StopLeader"),
		("VOICECHAT_WHOISLEADER", "BotVoiceChat_WhoIsLeader"),
		("VOICECHAT_WANTONDEFENSE", "BotVoiceChat_WantOnDefense"),
		("VOICECHAT_WANTONOFFENSE", "BotVoiceChat_WantOnOffense"),
	):
		assert f"{{{token}, {handler}" in voice_table


def test_qagame_voice_command_hlil_dispatch_and_botlib_import_wiring_are_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	g_syscalls = _read(GAME_SYSCALLS)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	ai_main = _read(GAME_AI_MAIN)

	for expected in VOICE_HLIL_ANCHORS:
		assert expected in hlil

	for expected in (
		"void trap_BotEnterChat(int chatstate, int client, int sendto)",
		"void trap_EA_Action(int client, int action)",
		"int trap_BotGetLevelItemGoal(int index, char *classname, void /* struct bot_goal_s */ *goal)",
		"void trap_BotUserCommand(int clientNum, usercmd_t *ucmd)",
	):
		assert expected in g_syscalls

	for expected in (
		"QL_G_trap_BotEnterChat",
		"QL_G_trap_EA_Action",
		"QL_G_trap_BotGetLevelItemGoal",
		"QL_G_trap_BotUserCommand",
	):
		assert expected in ql_game_imports

	assert "BotVoiceChatCommand(bs, SAY_TEAM, args);" in ai_main
	assert "trap_BotUserCommand(botstates[i]->client, &botstates[i]->lastucmd);" in ai_main


def test_qagame_bot_spawn_aliases_metadata_and_source_are_pinned() -> None:
	g_bot = _read(GAME_BOT)

	_assert_mapping_rows(BOT_SPAWN_FUNCTIONS)

	for _, _, normalized_name, _, _, _ in BOT_SPAWN_FUNCTIONS:
		block = _extract_function_block(g_bot, SOURCE_SIGNATURES[normalized_name])
		for anchor in BOT_SPAWN_SOURCE_ANCHORS[normalized_name]:
			assert anchor in block, normalized_name

	assert "void G_AddTrainerBot( void );" in _read(GAME_LOCAL)
	assert "G_CheckBotSpawn();" in _extract_function_block(_read(GAME_AI_MAIN), "int BotAIStartFrame(int time)")


def test_qagame_bot_spawn_hlil_ghidra_and_botlib_bridge_wiring_are_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	decompile_top = _read(QAGAME_DECOMPILE_TOP)
	g_syscalls = _read(GAME_SYSCALLS)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in BOT_SPAWN_HLIL_ANCHORS:
		assert expected in hlil

	for expected in BOT_SPAWN_GHIDRA_ANCHORS:
		assert expected in decompile_top

	for expected in (
		"int trap_BotLibStartFrame(float time)",
		"int trap_BotLibUpdateEntity(int ent, void /* struct bot_updateentity_s */ *bue)",
		"int trap_BotLibLoadMap(const char *mapname)",
		"int trap_BotLibSetup( void )",
		"int trap_BotLibShutdown( void )",
	):
		assert expected in g_syscalls

	for expected in (
		"QL_G_trap_BotLibStartFrame",
		"QL_G_trap_BotLibUpdateEntity",
		"QL_G_trap_BotLibLoadMap",
		"QL_G_trap_BotLibSetup",
		"QL_G_trap_BotLibShutdown",
		"QL_G_trap_BotAllocateClient",
		"QL_G_trap_BotFreeClient",
	):
		assert expected in ql_game_imports
