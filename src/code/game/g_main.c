/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
//

#include "g_local.h"
#include "g_config.h"
#include "g_match_config.h"
#include <limits.h>
#include "../../../src-re/include/ql_types.h"
#include <time.h>

level_locals_t	level;
weaponConfig_t	g_weaponConfig;


typedef struct {
	vmCvar_t	*vmCvar;
	char		*cvarName;
	char		*defaultString;
	int			cvarFlags;
	int			modificationCount;  // for tracking changes
	qboolean	trackChange;	    // track this variable, and announce if changed
	qboolean	teamShader;	    // track and if changed, update shader state
	const char	*helpString; // optional help text advertised alongside the cvar
} cvarTable_t;

gentity_t		g_entities[MAX_GENTITIES];
gclient_t		g_clients[MAX_CLIENTS];

static qlr_game_frame_context_t *g_qlr_frame_ctx = NULL;
static int	s_itemTimersModCount = 0;
static int	s_itemHeightModCount = 0;
static int	s_lastItemTimerEnabled = -1;
static int	s_lastItemTimerHeight = -1;
static int	s_forceSmallScoreboardMessageModCount = -1;
static int	s_forceSendConfigstringModCount = -1;
static int	s_forceAtmosphericEffectsModCount = -1;
static int	s_forceDmgThroughSurfaceModCount = -1;
static int	s_forcedAtmosphereModCount = -1;
static char	s_worldspawnAtmosphere[MAX_QPATH];
static char	s_lastForcedCosmeticsPayload[MAX_INFO_STRING];

static qlr_game_frame_context_t *G_GetFrameContext( void );
static void G_DispatchScheduledThinks( qlr_game_frame_context_t *ctx, int msec );
static void G_StepEntities( qlr_game_frame_context_t *ctx );
static void G_DispatchEvents( qlr_game_frame_context_t *ctx );
static void G_FinishClientFrames( qlr_game_frame_context_t *ctx );
static void G_CheckLevelTimers( qlr_game_frame_context_t *ctx, int previousWarmupTime, int previousIntermissionQueued );
static void G_UpdateTrainingState( void );
static void G_UpdateGametypeTutorialText( void );

/*
=============
G_SelectForcedAtmosphere

Selects the highest priority forced atmosphere token to publish to clients.
=============
*/
static const char *G_SelectForcedAtmosphere( void ) {
	if ( g_forceAtmosphericEffects.string[0] ) {
		return g_forceAtmosphericEffects.string;
	}

	if ( s_worldspawnAtmosphere[0] ) {
		return s_worldspawnAtmosphere;
	}

	if ( g_forcedAtmosphere.string[0] ) {
		return g_forcedAtmosphere.string;
	}

	return "";
}

/*
=============
G_UpdateForcedCosmeticsConfigstring

Rebuilds the forced cosmetics payload and broadcasts it to all clients when requested.
=============
*/
void G_UpdateForcedCosmeticsConfigstring( qboolean forceBroadcast ) {
	char		info[MAX_INFO_STRING];
	const char	*atmosphere;
	qboolean	shouldBroadcast;

	info[0] = '\0';

	Info_SetValueForKey( info, "sb", g_forceSmallScoreboardMessage.integer ? "1" : "0" );
	Info_SetValueForKey( info, "hud", g_forceSendConfigstring.integer ? "1" : "0" );
	Info_SetValueForKey( info, "dmg", g_forceDmgThroughSurface.integer ? "1" : "0" );

	atmosphere = G_SelectForcedAtmosphere();
	if ( atmosphere && atmosphere[0] ) {
		Info_SetValueForKey( info, "atm", atmosphere );
	}

	shouldBroadcast = forceBroadcast;
	if ( !shouldBroadcast && Q_stricmp( info, s_lastForcedCosmeticsPayload ) ) {
		shouldBroadcast = qtrue;
	}

	if ( !shouldBroadcast ) {
		return;
	}

	trap_SetConfigstring( CS_FORCED_COSMETICS, info );
	Q_strncpyz( s_lastForcedCosmeticsPayload, info, sizeof( s_lastForcedCosmeticsPayload ) );
}

/*
=============
G_SetWorldspawnAtmosphere

Caches the worldspawn-provided atmosphere token and refreshes the broadcast payload.
=============
*/
void G_SetWorldspawnAtmosphere( const char *atmosphere ) {
	if ( atmosphere && atmosphere[0] ) {
		Q_strncpyz( s_worldspawnAtmosphere, atmosphere, sizeof( s_worldspawnAtmosphere ) );
	} else {
		s_worldspawnAtmosphere[0] = '\0';
	}

	G_UpdateForcedCosmeticsConfigstring( qtrue );
}

void QLR_Game_BindFrameContext( qlr_game_frame_context_t *ctx ) {
	g_qlr_frame_ctx = ctx;

	if ( g_qlr_frame_ctx ) {
		g_qlr_frame_ctx->level = ( qlr_level_locals_t * )&level;
		g_qlr_frame_ctx->entities = ( qlr_gentity_t * )g_entities;
		g_qlr_frame_ctx->entity_count = level.num_entities;
	}
}

void QLR_Game_UnbindFrameContext( void ) {
	g_qlr_frame_ctx = NULL;
}

vmCvar_t	g_gametype;
vmCvar_t	g_dmflags;
vmCvar_t	g_fraglimit;
vmCvar_t	g_timelimit;
vmCvar_t	mercylimit;
vmCvar_t	g_mercytime;
vmCvar_t	g_capturelimit;
vmCvar_t	g_domCapTime;
vmCvar_t	g_domTeammateCapScale;
vmCvar_t	g_domDistressThreshold;
vmCvar_t	g_domEnableContention;
vmCvar_t	g_domNeutralFlag;
vmCvar_t	g_domScoreRate;
vmCvar_t	g_friendlyFire;
vmCvar_t	g_password;
vmCvar_t	g_needpass;
vmCvar_t	g_allTalk;
vmCvar_t	g_maxclients;
vmCvar_t	g_maxGameClients;
vmCvar_t	g_dedicated;
vmCvar_t	g_speed;
vmCvar_t	g_gravity;
vmCvar_t	g_cheats;
vmCvar_t	g_knockback;
vmCvar_t	g_quadfactor;
vmCvar_t	g_forcerespawn;
vmCvar_t	g_inactivity;
vmCvar_t	g_debugMove;
vmCvar_t	g_debugDamage;
vmCvar_t	g_debugAlloc;
vmCvar_t	g_weaponRespawn;
vmCvar_t	g_weaponTeamRespawn;
vmCvar_t	g_motd;
vmCvar_t	g_synchronousClients;
vmCvar_t	g_warmup;
vmCvar_t	g_doWarmup;
vmCvar_t	g_restarted;
vmCvar_t	g_log;
vmCvar_t	g_logSync;
vmCvar_t	g_blood;
vmCvar_t	g_podiumDist;
vmCvar_t	g_podiumDrop;
vmCvar_t	g_allowSpecVote;
vmCvar_t	g_allowVote;
vmCvar_t	g_allowVoteMidGame;
vmCvar_t	g_allowForfeit;
vmCvar_t	g_allowKill;
vmCvar_t	g_allowForfeit;
vmCvar_t	g_complaintLimit;
vmCvar_t	g_complaintDamageThreshold;
vmCvar_t	g_voteFlags;
vmCvar_t	g_voteDelay;
vmCvar_t	g_voteLimit;
vmCvar_t	g_complaintDamageThreshold;
vmCvar_t	g_complaintLimit;
vmCvar_t	g_teamAutoJoin;
vmCvar_t	g_teamForceBalance;
vmCvar_t	g_banIPs;
vmCvar_t	g_filterBan;
vmCvar_t	g_instaGib;
vmCvar_t	g_itemTimers;
vmCvar_t	g_itemHeight;
vmCvar_t	g_forceSmallScoreboardMessage;
vmCvar_t	g_forceSendConfigstring;
vmCvar_t	g_forceAtmosphericEffects;
vmCvar_t	g_forceDmgThroughSurface;
vmCvar_t	g_grantItemOnSpawn;
vmCvar_t	g_maxDeferredSpawns;
vmCvar_t	g_teamSpawnAsSpec;
vmCvar_t	g_teamSpecFreeCam;
vmCvar_t	g_teamSpecSayEnable;
vmCvar_t	g_playermodelOverride;
vmCvar_t	g_playerheadmodelOverride;
vmCvar_t	g_training;
vmCvar_t	g_botsFile;
vmCvar_t	g_botSpawnList;
vmCvar_t	g_accessFile;
vmCvar_t	g_factoryTitle;
vmCvar_t	g_dropInactive;
vmCvar_t	g_smoothClients;
vmCvar_t	pmove_fixed;
vmCvar_t	pmove_msec;
vmCvar_t	g_rankings;
vmCvar_t	g_listEntity;
vmCvar_t	g_overtime;
vmCvar_t	g_timeoutLen;
vmCvar_t	g_timeoutCount;
vmCvar_t        g_factoryRespawnDelay;
vmCvar_t        g_factoryWarmupSpawnDelay;
vmCvar_t        g_factoryAllowItemDrops;
vmCvar_t        g_factoryAllowItemBounce;
vmCvar_t        g_itemTimers;
vmCvar_t        g_itemHeight;
vmCvar_t        g_vampiricDamage;
vmCvar_t	g_suddenDeathRespawn;
vmCvar_t	g_suddenDeathRespawnStart;
vmCvar_t	g_suddenDeathRespawnTick;
vmCvar_t	g_suddenDeathRespawnMax;
vmCvar_t	g_suddenDeathRespawnIncrement;
vmCvar_t	g_suddenDeathRespawnPrint;
vmCvar_t	g_damage_gauntlet;
vmCvar_t	g_damage_mg;
vmCvar_t	g_damage_mg_team;
vmCvar_t	g_damage_hmg;
vmCvar_t	g_damage_sg;
vmCvar_t	g_damage_gl;
vmCvar_t	g_splashDamage_gl;
vmCvar_t	g_splashRadius_gl;
vmCvar_t	g_damage_rl;
vmCvar_t	g_splashDamage_rl;
vmCvar_t	g_splashRadius_rl;
vmCvar_t	g_damage_pg;
vmCvar_t	g_splashDamage_pg;
vmCvar_t	g_splashRadius_pg;
vmCvar_t	g_damage_lg;
vmCvar_t	g_damage_rg;
vmCvar_t	g_damage_bfg;
vmCvar_t	g_splashDamage_bfg;
vmCvar_t	g_splashRadius_bfg;
vmCvar_t	g_velocity_gl;
vmCvar_t	g_velocity_rl;
vmCvar_t	g_velocity_pg;
vmCvar_t	g_velocity_bfg;
vmCvar_t	g_velocity_gh;
vmCvar_t	g_guidedRocket;
vmCvar_t	g_rocketsplashOffset;
vmCvar_t	g_quadHog;
vmCvar_t	g_quadHogIdle;
vmCvar_t	g_quadHogTime;
vmCvar_t	g_quadHogPingRate;
vmCvar_t	g_training;
vmCvar_t	g_forcedAtmosphere;
vmCvar_t	g_adTouchScoreBonus;
vmCvar_t	g_adElimScoreBonus;
vmCvar_t	g_adCaptureScoreBonus;
vmCvar_t	g_roundWarmupDelay;
vmCvar_t	g_roundDrawLivingCount;
vmCvar_t	g_roundDrawHealthCount;
vmCvar_t	g_freezeThawWinningTeam;
vmCvar_t	g_freezeThawThroughSurface;
vmCvar_t	g_freezeThawTime;
vmCvar_t	g_freezeThawTick;
vmCvar_t	g_freezeThawRadius;
vmCvar_t	g_freezeRoundDelay;
vmCvar_t	g_freezeResetWeaponsOnRound;
vmCvar_t	g_freezeResetHealthOnRound;
vmCvar_t	g_freezeResetArmorOnRound;
vmCvar_t	g_freezeRemovePowerupsOnRound;
vmCvar_t	g_freezeProtectedSpawnTime;
vmCvar_t	g_freezeEnvironmentalRespawnDelay;
vmCvar_t	g_freezeAutoThawTime;
static matchFactoryConfig_t matchFlow_lastConfig;
vmCvar_t	g_obeliskHealth;
vmCvar_t	g_obeliskRegenPeriod;
vmCvar_t	g_obeliskRegenAmount;
vmCvar_t	g_obeliskRespawnDelay;
vmCvar_t	g_cubeTimeout;
vmCvar_t	g_redteam;
vmCvar_t	g_blueteam;
vmCvar_t	g_singlePlayer;
vmCvar_t	g_enableDust;
vmCvar_t	g_enableBreath;
vmCvar_t	g_proxMineTimeout;
vmCvar_t	g_rrRoundScoreBonus;
vmCvar_t	g_rrInfectedZombieSpeed;
vmCvar_t	g_rrInfectedSurvivorScoreMethod;
vmCvar_t	g_rrInfectedSurvivorScoreBonus;
vmCvar_t	g_rrInfectedSurvivorScoreRate;
vmCvar_t	g_rrInfectedSurvivorMinSpeed;
vmCvar_t	g_rrInfectedSurvivorPingRate;
vmCvar_t	g_rrInfectedSpreadWarningTime;
vmCvar_t	g_rrInfectedSpreadTime;
vmCvar_t	g_rrInfected;
vmCvar_t	g_rrDamageScoreBonus;
vmCvar_t	g_rrAllowNegativeScores;
vmCvar_t	roundlimit;
vmCvar_t	roundtimelimit;

// bk001129 - made static to avoid aliasing
static cvarTable_t		gameCvarTable[] = {
	// don't override the cheat state set by the system
	{ &g_cheats, "sv_cheats", "", 0, 0, qfalse },

	// noset vars
	{ NULL, "gamename", GAMEVERSION , CVAR_SERVERINFO | CVAR_ROM, 0, qfalse  },
	{ NULL, "gamedate", __DATE__ , CVAR_ROM, 0, qfalse  },
	{ &g_restarted, "g_restarted", "0", CVAR_ROM, 0, qfalse  },
	{ NULL, "sv_mapname", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse  },

	// latched vars
	{ &g_gametype, "g_gametype", "0", CVAR_SERVERINFO | CVAR_USERINFO | CVAR_LATCH, 0, qfalse  },

	{ &g_maxclients, "sv_maxclients", "8", CVAR_SERVERINFO | CVAR_LATCH | CVAR_ARCHIVE, 0, qfalse  },
	{ &g_maxGameClients, "g_maxGameClients", "0", CVAR_SERVERINFO | CVAR_LATCH | CVAR_ARCHIVE, 0, qfalse  },

	// change anytime vars
	{ &g_dmflags, "dmflags", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qtrue  },
	{ &g_fraglimit, "fraglimit", "20", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
{ &g_timelimit, "timelimit", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
{ &mercylimit, "mercylimit", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue, qfalse, "Score differential that triggers the mercy rule once the grace window expires; 0 disables mercy checks." },
{ &g_mercytime, "g_mercytime", "10", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Minutes after match start before the server evaluates mercylimit." },
	{ &g_capturelimit, "capturelimit", "8", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
	{ &g_domCapTime, "g_domCapTime", "5", CVAR_ARCHIVE, 0, qfalse, qfalse, "Seconds required to capture a Domination point with a single attacker." },
	{ &g_domTeammateCapScale, "g_domTeammateCapScale", "0.5", CVAR_ARCHIVE, 0, qfalse, qfalse, "Additional capture speed gained per extra teammate assisting." },
	{ &g_domDistressThreshold, "g_domDistressThreshold", "75", CVAR_ARCHIVE, 0, qfalse, qfalse, "Percent progress when defenders receive a distress warning." },
	{ &g_domEnableContention, "g_domEnableContention", "1", CVAR_ARCHIVE, 0, qfalse, qfalse, "Allow Domination progress to continue when both teams contest a point." },
	{ &g_domNeutralFlag, "g_domNeutralFlag", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Require Domination points to be neutralized before capture completes when non-zero." },
	{ &g_domScoreRate, "g_domScoreRate", "5", CVAR_ARCHIVE, 0, qfalse, qfalse, "Seconds between Domination score ticks per owned point." },
	{ &roundlimit, "roundlimit", "10", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue, qfalse, "Maximum number of rounds to play before the match ends." },
	{ &roundtimelimit, "roundtimelimit", "180", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue, qfalse, "Seconds allowed per active round before it times out." },
	{ &g_roundWarmupDelay, "g_roundWarmupDelay", "10000", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Milliseconds of warmup that separate freeze-style rounds." },
	{ &g_roundDrawLivingCount, "g_roundDrawLivingCount", "1", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Print remaining living player counts when freeze rounds end." },
	{ &g_roundDrawHealthCount, "g_roundDrawHealthCount", "1", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Print aggregate team health when freeze rounds finish." },
	{ &g_freezeThawWinningTeam, "g_freezeThawWinningTeam", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Award thaw credit to the winning team before the next round when non-zero." },
	{ &g_freezeThawThroughSurface, "g_freezeThawThroughSurface", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Allow thaw traces to pass through solid world geometry when enabled." },
	{ &g_freezeThawTime, "g_freezeThawTime", "2000", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Milliseconds teammates must remain nearby before a frozen player thaws." },
	{ &g_freezeThawTick, "g_freezeThawTick", "250", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Milliseconds added to thaw progress each time an ally stays in range." },
	{ &g_freezeThawRadius, "g_freezeThawRadius", "96", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Radius in units required for thaw assistance to register." },
	{ &g_freezeRoundDelay, "g_freezeRoundDelay", "4000", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Delay in milliseconds between a freeze round ending and the next warmup." },
	{ &g_freezeResetWeaponsOnRound, "g_freezeResetWeaponsOnRound", "1", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Respawn players with the factory loadout each time a freeze round restarts." },
	{ &g_freezeResetHealthOnRound, "g_freezeResetHealthOnRound", "1", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Restore players to full health whenever a freeze round resets or they thaw." },
	{ &g_freezeResetArmorOnRound, "g_freezeResetArmorOnRound", "1", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Restore armor to the factory amount on round reset or thaw." },
	{ &g_freezeRemovePowerupsOnRound, "g_freezeRemovePowerupsOnRound", "1", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Strip carried powerups whenever a freeze round begins anew." },
	{ &g_freezeProtectedSpawnTime, "g_freezeProtectedSpawnTime", "5000", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Milliseconds of post-thaw spawn protection applied to players." },
	{ &g_freezeEnvironmentalRespawnDelay, "g_freezeEnvironmentalRespawnDelay", "120000", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Milliseconds frozen players wait before auto-respawning when killed by the environment." },
	{ &g_freezeAutoThawTime, "g_freezeAutoThawTime", "45000", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Milliseconds after which frozen players automatically thaw even without help." },
	{ &g_rrRoundScoreBonus, "g_rrRoundScoreBonus", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Score bonus granted to the team that wins a Red Rover round." },
	{ &g_rrInfectedZombieSpeed, "g_rrInfectedZombieSpeed", "1.15", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Speed multiplier applied to infected players." },
	{ &g_rrInfectedSurvivorScoreMethod, "g_rrInfectedSurvivorScoreMethod", "2", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Selects the survivor scoring mode: thresholds or direct damage scaling." },
	{ &g_rrInfectedSurvivorScoreBonus, "g_rrInfectedSurvivorScoreBonus", "1", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Base score bonus awarded to survivors when the configured method triggers." },
	{ &g_rrInfectedSurvivorScoreRate, "g_rrInfectedSurvivorScoreRate", "30", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Damage threshold required before issuing survivor score bonuses when using the threshold method." },
	{ &g_rrInfectedSurvivorMinSpeed, "g_rrInfectedSurvivorMinSpeed", "500", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Minimum planar speed survivors must maintain before receiving penalty pings." },
	{ &g_rrInfectedSurvivorPingRate, "g_rrInfectedSurvivorPingRate", "2000", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Milliseconds between survivor warning pings when moving too slowly." },
	{ &g_rrInfectedSpreadWarningTime, "g_rrInfectedSpreadWarningTime", "10", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Seconds before forced infection that survivors begin receiving warning cues." },
	{ &g_rrInfectedSpreadTime, "g_rrInfectedSpreadTime", "40", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Seconds a survivor can avoid infection before the virus automatically spreads." },
	{ &g_rrInfected, "g_rrInfected", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Enable the infection ruleset inside Red Rover." },
	{ &g_rrDamageScoreBonus, "g_rrDamageScoreBonus", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Multiplier applied to survivor damage when using damage-based scoring." },
	{ &g_rrAllowNegativeScores, "g_rrAllowNegativeScores", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Allow Red Rover scoring adjustments to drive a player's score below zero." },

	{ &g_synchronousClients, "g_synchronousClients", "0", CVAR_SYSTEMINFO, 0, qfalse  },

	{ &g_friendlyFire, "g_friendlyFire", "0", CVAR_ARCHIVE, 0, qtrue  },

        { &g_teamAutoJoin, "g_teamAutoJoin", "0", CVAR_ARCHIVE  },
        { &g_teamForceBalance, "g_teamForceBalance", "0", CVAR_ARCHIVE  },
        { &g_teamSpawnAsSpec, "g_teamSpawnAsSpec", "0", 0, 0, qfalse, qfalse, "Force all join attempts into spectator slots until administrators clear the flag." },
        { &g_teamSpecFreeCam, "g_teamSpecFreeCam", "0", 0, 0, qfalse, qfalse, "Allow spectators to use free-flying cameras when non-zero; otherwise they stay in follow or scoreboard views." },
        { &g_teamSpecSayEnable, "g_teamSpecSayEnable", "1", 0, 0, qfalse, qfalse, "Permit spectators to chat while observing when enabled." },

	{ &g_log, "g_log", "games.log", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_logSync, "g_logSync", "0", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_accessFile, "g_accessFile", "access.txt", 0, 0, qfalse, qfalse, "Relative path to the access permission file evaluated for admin commands." },

	{ &g_password, "g_password", "", CVAR_USERINFO, 0, qfalse  },

	{ &g_banIPs, "g_banIPs", "", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_filterBan, "g_filterBan", "1", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_instaGib, "g_instaGib", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse },
	{ &g_itemTimers, "g_itemTimers", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qfalse, "Force server-controlled item timers to display for all clients when non-zero." },
	{ &g_itemHeight, "g_itemHeight", "35", CVAR_ARCHIVE, 0, qfalse, qfalse, "Vertical offset in units applied to enforced item timer indicators." },
        { &g_forceSmallScoreboardMessage, "g_forceSmallScoreboardMessage", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Prefer the compact scoreboard centerprint even with small player counts." },
        { &g_forceSendConfigstring, "g_forceSendConfigstring", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Resend all configstrings to clients on map load when enabled to debug sync issues." },
        { &g_forceAtmosphericEffects, "g_forceAtmosphericEffects", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Enable atmospheric map effects such as snow or rain regardless of client preference." },
        { &g_forceDmgThroughSurface, "g_forceDmgThroughSurface", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Allow splash damage to pass through non-solid surfaces for testing when set." },
        { &g_grantItemOnSpawn, "g_grantItemOnSpawn", "", CVAR_ARCHIVE, 0, qfalse, qfalse, "Whitespace or comma separated list of `give` tokens handed to every spawn, mirroring Quake Live's server-only spawn grants." },
	{ &g_playermodelOverride, "g_playermodelOverride", "", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qfalse, "Optional model path used to override every player's model selection server-wide." },
	{ &g_playerheadmodelOverride, "g_playerheadmodelOverride", "", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qfalse, "Optional head model override applied to all players for consistent visuals." },
	{ &g_botsFile, "g_botsFile", "", CVAR_INIT | CVAR_ROM, 0, qfalse, qfalse, "Override bot definition list with a custom script when specified." },
	{ &g_botSpawnList, "g_botSpawnList", "", 0, 0, qfalse, qfalse, "Space-separated bot names automatically spawned on map start when set." },
	{ &g_training, "g_training", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Enable the training progression gate so players must complete tutorials." },
	{ &g_adTouchScoreBonus, "g_adTouchScoreBonus", "1", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qfalse, "Attack & Defend touch bonus added to the scoring totals whenever an attacker grabs the flag." },
	{ &g_adElimScoreBonus, "g_adElimScoreBonus", "2", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qfalse, "Attack & Defend elimination bonus granted to teams and players for each enemy frag." },
	{ &g_adCaptureScoreBonus, "g_adCaptureScoreBonus", "3", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qfalse, "Attack & Defend capture bonus layered on top of the base team point whenever the flag is secured." },

	{ &g_needpass, "g_needpass", "0", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse },

	{ &g_allTalk, "g_allTalk", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qfalse, "Allow players, spectators, and opposing teams to share chat when enabled." },

	{ &g_dedicated, "dedicated", "0", 0, 0, qfalse  },

	{ &g_speed, "g_speed", "320", 0, 0, qtrue  },
	{ &g_gravity, "g_gravity", "800", 0, 0, qtrue  },
	{ &g_knockback, "g_knockback", "1000", 0, 0, qtrue  },	{ &g_max_knockback, "g_max_knockback", "200", 0, 0, qfalse, qfalse, "Upper clamp applied to computed knockback force." },	{ &g_quadfactor, "g_quadfactor", "3", 0, 0, qtrue  },
	{ &g_weaponRespawn, "g_weaponrespawn", "5", 0, 0, qtrue  },
	{ &g_weaponTeamRespawn, "g_weaponTeamRespawn", "30", 0, 0, qtrue },
	{ &g_forcerespawn, "g_forcerespawn", "20", 0, 0, qtrue },
	{ &g_inactivity, "g_inactivity", "0", 0, 0, qtrue },
	{ &g_dropInactive, "g_dropInactive", "1", 0, 0, qfalse, qfalse, "Automatically remove clients marked inactive when enabled." },
	{ &g_debugMove, "g_debugMove", "0", 0, 0, qfalse },
	{ &g_debugDamage, "g_debugDamage", "0", 0, 0, qfalse },
	{ &g_debugAlloc, "g_debugAlloc", "0", 0, 0, qfalse },
	{ &g_motd, "g_motd", "", 0, 0, qfalse },
	{ &g_blood, "com_blood", "1", 0, 0, qfalse },

	{ &g_podiumDist, "g_podiumDist", "80", 0, 0, qfalse },
	{ &g_podiumDrop, "g_podiumDrop", "70", 0, 0, qfalse },

	{ &g_allowSpecVote, "g_allowSpecVote", "0", 0, 0, qfalse },
	{ &g_allowVote, "g_allowVote", "1", CVAR_ARCHIVE, 0, qfalse },
	{ &g_allowVoteMidGame, "g_allowVoteMidGame", "0", 0, 0, qfalse },
	{ &g_allowForfeit, "g_allowForfeit", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Enables the forfeit console command when non-zero so duel and CA leagues can permit early surrenders." },
	{ &g_allowKill, "g_allowKill", "1000", CVAR_ARCHIVE, 0, qfalse, qfalse, "Minimum milliseconds between kill commands; 0 restores instant suicides." },
	{ &g_allowForfeit, "g_allowForfeit", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Enables the forfeit console command when non-zero so early concessions can be honored." },
	{ &g_complaintLimit, "g_complaintLimit", "1", CVAR_ARCHIVE, 0, qfalse, qfalse, "Maximum complaints before a player is automatically kicked; 0 disables kicking." },
	{ &g_complaintDamageThreshold, "g_complaintDamageThreshold", "1", CVAR_ARCHIVE, 0, qfalse, qfalse, "Minimum damage from a teammate required to present the complaint prompt." },
	{ &g_voteFlags, "g_voteFlags", "0", CVAR_ARCHIVE | CVAR_SERVERINFO, 0, qfalse },
	{ &g_voteDelay, "g_voteDelay", "0", 0, 0, qfalse },
	{ &g_voteLimit, "g_voteLimit", "0", 0, 0, qfalse },
	{ &g_complaintDamageThreshold, "g_complaintDamageThreshold", "1", CVAR_ARCHIVE, 0, qfalse, qfalse, "Minimum team damage required before a complaint prompt is issued." },
	{ &g_complaintLimit, "g_complaintLimit", "1", CVAR_ARCHIVE, 0, qfalse, qfalse, "Friendly-fire complaints recorded against a player before they are kicked." },
	{ &g_warmup, "g_warmup", "20", CVAR_ARCHIVE, 0, qtrue  },
	{ &g_doWarmup, "g_doWarmup", "0", 0, 0, qtrue  },
	{ &g_training, "g_training", "0", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse, qfalse, "Marks training sessions and disables competitive match flow when set." },
	{ &g_forcedAtmosphere, "g_forcedAtmosphere", "", CVAR_ARCHIVE, 0, qfalse, qfalse, "Optional atmosphere effect applied when a map lacks an atmosphere worldspawn key." },
	{ &g_listEntity, "g_listEntity", "0", 0, 0, qfalse },
	{ &g_overtime, "g_overtime", "120", CVAR_SERVERINFO | CVAR_NORESTART, 0, qfalse, qfalse, "Overtime period length in seconds once regulation ends tied; 0 keeps sudden death active until the tie is broken." },
	{ &g_suddenDeathRespawn, "g_suddenDeathRespawn", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Allow ammo to continue respawning during sudden death when set to 1." },
	{ &g_timeoutLen, "g_timeoutLen", "60", CVAR_NORESTART, 0, qfalse, qfalse, "Timeout duration in seconds for each team pause." },
	{ &g_timeoutCount, "g_timeoutCount", "0", CVAR_SERVERINFO | CVAR_NORESTART, 0, qfalse, qfalse, "Number of timeouts each team may call per match." },
	{ &g_factoryTitle, "g_factoryTitle", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse, qfalse, "Short factory title pushed via serverinfo for display on connected clients." },
	{ &g_factoryRespawnDelay, "g_factoryRespawnDelay", "0", CVAR_NORESTART, 0, qfalse, qfalse, "Delay in milliseconds before a defeated player respawns when factories schedule queues." },
	{ &g_factoryWarmupSpawnDelay, "g_factoryWarmupSpawnDelay", "0", CVAR_NORESTART, 0, qfalse, qfalse, "Delay in milliseconds applied to warmup spawns when factories request staggered starts." },
	{ &g_factoryAllowItemDrops, "g_factoryAllowItemDrops", "1", CVAR_NORESTART, 0, qfalse, qfalse, "Controls whether item drop logic fires for weapons and powerups spawned from players." },
	{ &g_factoryAllowItemBounce, "g_factoryAllowItemBounce", "1", CVAR_NORESTART, 0, qfalse, qfalse, "Controls whether dropped items bounce before coming to rest when factories disable the behaviour." },
	{ &g_maxDeferredSpawns, "g_maxDeferredSpawns", "4", 0, 0, qfalse, qfalse, "Maximum simultaneous delayed spawns the queue may hold before new respawns execute immediately." },
	{ &g_itemTimers, "g_itemTimers", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Toggles broadcast of server-side item timer training aids when non-zero." },
	{ &g_itemHeight, "g_itemHeight", "20", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Adjusts the vertical spacing clients apply to item timer widgets in the HUD." },
	{ &g_vampiricDamage, "g_vampiricDamage", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Fraction of dealt health damage returned to the attacker as healing." },
	{ &g_suddenDeathRespawnStart, "g_suddenDeathRespawnStart", "3", CVAR_NORESTART, 0, qfalse, qfalse, "Initial sudden-death respawn delay in seconds when respawns are enabled." },
	{ &g_suddenDeathRespawnTick, "g_suddenDeathRespawnTick", "60", CVAR_NORESTART, 0, qfalse, qfalse, "Interval in seconds after which sudden-death respawn delays are increased." },
	{ &g_suddenDeathRespawnMax, "g_suddenDeathRespawnMax", "10", CVAR_NORESTART, 0, qfalse, qfalse, "Maximum sudden-death respawn delay in seconds." },
	{ &g_suddenDeathRespawnIncrement, "g_suddenDeathRespawnIncrement", "1", CVAR_NORESTART, 0, qfalse, qfalse, "Seconds added to the sudden-death respawn delay at each tick." },
	{ &g_suddenDeathRespawnPrint, "g_suddenDeathRespawnPrint", "1", CVAR_NORESTART, 0, qfalse, qfalse, "Print announcements when sudden-death respawn delays change." },
	{ &g_damage_gauntlet, "g_damage_gauntlet", "50", 0, 0, qtrue },
	{ &g_damage_mg, "g_damage_mg", "7", 0, 0, qtrue },
	{ &g_damage_mg_team, "g_damage_mg_team", "5", 0, 0, qtrue },
	{ &g_damage_hmg, "g_damage_hmg", "10", 0, 0, qtrue },
	{ &g_damage_sg, "g_damage_sg", "10", 0, 0, qtrue },
	{ &g_damage_gl, "g_damage_gl", "100", 0, 0, qtrue },
	{ &g_splashDamage_gl, "g_splashDamage_gl", "100", 0, 0, qtrue },
	{ &g_splashRadius_gl, "g_splashRadius_gl", "150", 0, 0, qtrue },
	{ &g_damage_rl, "g_damage_rl", "100", 0, 0, qtrue },
	{ &g_splashDamage_rl, "g_splashDamage_rl", "100", 0, 0, qtrue },
	{ &g_splashRadius_rl, "g_splashRadius_rl", "120", 0, 0, qtrue },
	{ &g_damage_pg, "g_damage_pg", "20", 0, 0, qtrue },
	{ &g_splashDamage_pg, "g_splashDamage_pg", "15", 0, 0, qtrue },
	{ &g_splashRadius_pg, "g_splashRadius_pg", "20", 0, 0, qtrue },
	{ &g_damage_lg, "g_damage_lg", "8", 0, 0, qtrue },
	{ &g_damage_rg, "g_damage_rg", "100", 0, 0, qtrue },
	{ &g_damage_bfg, "g_damage_bfg", "100", 0, 0, qtrue },
	{ &g_splashDamage_bfg, "g_splashDamage_bfg", "100", 0, 0, qtrue },
	{ &g_splashRadius_bfg, "g_splashRadius_bfg", "120", 0, 0, qtrue },
	{ &g_velocity_gl, "g_velocity_gl", "700", 0, 0, qtrue, qfalse, "Grenade Launcher projectile speed in ups; mirrors the compiled 700 default and feeds both server and client prediction." },
	{ &g_velocity_rl, "g_velocity_rl", "900", 0, 0, qtrue, qfalse, "Rocket Launcher projectile speed in ups, defaulting to the baked-in 900 ups behaviour." },
	{ &g_velocity_pg, "g_velocity_pg", "2000", 0, 0, qtrue, qfalse, "Plasmagun bolt speed in ups; aligns with the legacy 2000 ups firing velocity." },
	{ &g_velocity_bfg, "g_velocity_bfg", "2000", 0, 0, qtrue, qfalse, "BFG projectile speed in ups pulled from the retail DLL defaults." },
	{ &g_velocity_gh, "g_velocity_gh", "800", 0, 0, qtrue, qfalse, "Grappling Hook projectile speed in ups; 800 preserves the vanilla behaviour." },
	{ &g_guidedRocket, "g_guidedRocket", "0", 0, 0, qtrue, qfalse, "Enable Quake Live style guided rockets when non-zero." },
	{ &g_rocketsplashOffset, "g_rocketsplashOffset", "0", 0, 0, qtrue, qfalse, "Offset in ups applied along the impact normal before evaluating rocket splash damage; 0 retains classic explosions." },
	{ &g_quadHog, "g_quadHog", "0", 0, 0, qtrue, qfalse, "Toggle Quad Hog survival mode that forces the carrier to fight the arena when enabled." },
	{ &g_quadHogIdle, "g_quadHogIdle", "0", 0, 0, qtrue, qfalse, "Seconds of inactivity allowed for the Quad Hog carrier before the powerup is revoked; 0 disables the idle check." },
	{ &g_quadHogTime, "g_quadHogTime", "0", 0, 0, qtrue, qfalse, "Maximum time in seconds a player may hold Quad during Quad Hog events before it auto-expires; 0 removes the cap." },
	{ &g_quadHogPingRate, "g_quadHogPingRate", "0", 0, 0, qtrue, qfalse, "Seconds between Quad Hog reminder pings while the timer is active; 0 silences the announcements." },
	{ &g_obeliskHealth, "g_obeliskHealth", "2500", 0, 0, qfalse },
	{ &g_obeliskRegenPeriod, "g_obeliskRegenPeriod", "1", 0, 0, qfalse },
	{ &g_obeliskRegenAmount, "g_obeliskRegenAmount", "15", 0, 0, qfalse },
	{ &g_obeliskRespawnDelay, "g_obeliskRespawnDelay", "10", CVAR_SERVERINFO, 0, qfalse },

	{ &g_cubeTimeout, "g_cubeTimeout", "30", 0, 0, qfalse },
	{ &g_redteam, "g_redteam", "Stroggs", CVAR_ARCHIVE | CVAR_SERVERINFO | CVAR_USERINFO , 0, qtrue, qtrue },
	{ &g_blueteam, "g_blueteam", "Pagans", CVAR_ARCHIVE | CVAR_SERVERINFO | CVAR_USERINFO , 0, qtrue, qtrue  },
	{ &g_singlePlayer, "ui_singlePlayerActive", "", 0, 0, qfalse, qfalse  },

	{ &g_enableDust, "g_enableDust", "0", CVAR_SERVERINFO, 0, qtrue, qfalse },
	{ &g_enableBreath, "g_enableBreath", "0", CVAR_SERVERINFO, 0, qtrue, qfalse },
	{ &g_proxMineTimeout, "g_proxMineTimeout", "20000", 0, 0, qfalse },
	{ &g_smoothClients, "g_smoothClients", "1", 0, 0, qfalse},
	{ &pmove_fixed, "pmove_fixed", "0", CVAR_SYSTEMINFO, 0, qfalse},
	{ &pmove_msec, "pmove_msec", "8", CVAR_SYSTEMINFO, 0, qfalse},

	{ &g_rankings, "g_rankings", "0", 0, 0, qfalse}

};

// bk001129 - made static to avoid aliasing
static int gameCvarTableSize = sizeof( gameCvarTable ) / sizeof( gameCvarTable[0] );

static void G_RegisterCvarHelp( const cvarTable_t *cv ) {
	char helpName[MAX_CVAR_VALUE_STRING];

	if ( !cv->helpString || !cv->helpString[0] || !cv->cvarName ) {
		return;
	}

	Com_sprintf( helpName, sizeof( helpName ), "helptext_%s", cv->cvarName );
	trap_Cvar_Register( NULL, helpName, cv->helpString, CVAR_ROM );
}

static void G_ReportMissingCvar( const char *cvarName ) {
        if ( !cvarName || !cvarName[0] ) {
                return;
        }

        G_Printf( "WARNING: gameplay config cvar %s is unavailable; using fallback value\n", cvarName );
}

static int G_ReadWeaponCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_ReportMissingCvar( cvarName );
		return fallback;
	}

	if ( cvar->integer <= 0 ) {
		return fallback;
	}

	return cvar->integer;
}

static int G_ReadWeaponCvarRaw( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_ReportMissingCvar( cvarName );
		return fallback;
	}

	return cvar->integer;
}

static int G_ReadWeaponCvarAtLeast( const vmCvar_t *cvar, int fallback, const char *cvarName, int minValue ) {
	int		value;

	value = G_ReadWeaponCvar( cvar, fallback, cvarName );
	if ( value < minValue ) {
		return minValue;
	}

	return value;
}

static qboolean G_ReadWeaponBoolCvar( const vmCvar_t *cvar, qboolean fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_ReportMissingCvar( cvarName );
		return fallback;
	}

	return ( cvar->integer != 0 ) ? qtrue : qfalse;
}

void G_InitWeaponConfig( void ) {
	g_weaponConfig.gauntletDamage = G_ReadWeaponCvar( &g_damage_gauntlet, 50, "g_damage_gauntlet" );
	g_weaponConfig.machinegunDamage = G_ReadWeaponCvar( &g_damage_mg, 7, "g_damage_mg" );
	g_weaponConfig.machinegunTeamDamage = G_ReadWeaponCvar( &g_damage_mg_team, 5, "g_damage_mg_team" );
	g_weaponConfig.heavyMachinegunDamage = G_ReadWeaponCvar( &g_damage_hmg, 10, "g_damage_hmg" );
	g_weaponConfig.shotgunDamage = G_ReadWeaponCvar( &g_damage_sg, 10, "g_damage_sg" );
	g_weaponConfig.grenadeDamage = G_ReadWeaponCvar( &g_damage_gl, 100, "g_damage_gl" );
	g_weaponConfig.grenadeSplashDamage = G_ReadWeaponCvar( &g_splashDamage_gl, 100, "g_splashDamage_gl" );
	g_weaponConfig.grenadeSplashRadius = G_ReadWeaponCvar( &g_splashRadius_gl, 150, "g_splashRadius_gl" );
	g_weaponConfig.grenadeSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gl, 700, "g_velocity_gl", 1 );
	g_weaponConfig.rocketDamage = G_ReadWeaponCvar( &g_damage_rl, 100, "g_damage_rl" );
	g_weaponConfig.rocketSplashDamage = G_ReadWeaponCvar( &g_splashDamage_rl, 100, "g_splashDamage_rl" );
	g_weaponConfig.rocketSplashRadius = G_ReadWeaponCvar( &g_splashRadius_rl, 120, "g_splashRadius_rl" );
	g_weaponConfig.rocketSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_rl, 900, "g_velocity_rl", 1 );
	g_weaponConfig.rocketSplashOffset = G_ReadWeaponCvarRaw( &g_rocketsplashOffset, 0, "g_rocketsplashOffset" );
	g_weaponConfig.plasmaDamage = G_ReadWeaponCvar( &g_damage_pg, 20, "g_damage_pg" );
	g_weaponConfig.plasmaSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pg, 15, "g_splashDamage_pg" );
	g_weaponConfig.plasmaSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pg, 20, "g_splashRadius_pg" );
	g_weaponConfig.plasmaSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_pg, 2000, "g_velocity_pg", 1 );
	g_weaponConfig.lightningDamage = G_ReadWeaponCvar( &g_damage_lg, 8, "g_damage_lg" );
	g_weaponConfig.railgunDamage = G_ReadWeaponCvar( &g_damage_rg, 100, "g_damage_rg" );
	g_weaponConfig.bfgDamage = G_ReadWeaponCvar( &g_damage_bfg, 100, "g_damage_bfg" );
	g_weaponConfig.bfgSplashDamage = G_ReadWeaponCvar( &g_splashDamage_bfg, 100, "g_splashDamage_bfg" );
	g_weaponConfig.bfgSplashRadius = G_ReadWeaponCvar( &g_splashRadius_bfg, 120, "g_splashRadius_bfg" );
	g_weaponConfig.bfgSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_bfg, 2000, "g_velocity_bfg", 1 );
	g_weaponConfig.grappleSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gh, 800, "g_velocity_gh", 1 );
	g_weaponConfig.guidedRocketEnabled = G_ReadWeaponBoolCvar( &g_guidedRocket, qfalse, "g_guidedRocket" );
	g_weaponConfig.quadHogEnabled = G_ReadWeaponBoolCvar( &g_quadHog, qfalse, "g_quadHog" );
	g_weaponConfig.quadHogIdleSeconds = G_ReadWeaponCvarRaw( &g_quadHogIdle, 0, "g_quadHogIdle" );
	if ( g_weaponConfig.quadHogIdleSeconds < 0 ) {
		g_weaponConfig.quadHogIdleSeconds = 0;
	}
	g_weaponConfig.quadHogTimeSeconds = G_ReadWeaponCvarRaw( &g_quadHogTime, 0, "g_quadHogTime" );
	if ( g_weaponConfig.quadHogTimeSeconds < 0 ) {
		g_weaponConfig.quadHogTimeSeconds = 0;
	}
	g_weaponConfig.quadHogPingRateSeconds = G_ReadWeaponCvarRaw( &g_quadHogPingRate, 0, "g_quadHogPingRate" );
	if ( g_weaponConfig.quadHogPingRateSeconds < 0 ) {
		g_weaponConfig.quadHogPingRateSeconds = 0;
	}
}

void G_UpdateWeaponConfig( void ) {
	G_InitWeaponConfig();
}

/*
=============
G_UpdateItemTimerConfig

Synchronises the item timer configuration cvars with all clients.
=============
*/
static void G_UpdateItemTimerConfig( qboolean forceBroadcast ) {
	int	enabled;
	int	height;

	enabled = g_itemTimers.integer ? 1 : 0;
	height = g_itemHeight.integer;
	if ( height <= 0 ) {
		height = ITEM_TIMER_DEFAULT_HEIGHT;
	} else if ( height > ITEM_TIMER_MAX_HEIGHT ) {
		height = ITEM_TIMER_MAX_HEIGHT;
	}

	if ( !forceBroadcast && enabled == s_lastItemTimerEnabled && height == s_lastItemTimerHeight ) {
		return;
	}

	s_lastItemTimerEnabled = enabled;
	s_lastItemTimerHeight = height;

	G_BroadcastItemTimerState( enabled, height );
}

static void LevelCheckTimers( void );
void G_UpdateMatchStateConfigString( void );
static void G_StartOrExtendOvertime( void );
static void G_StopOvertime( void );
static void G_TrackSuddenDeathAnnouncements( void );
void G_InitGame( int levelTime, int randomSeed, int restart );
void G_RunFrame( int levelTime );
void G_ShutdownGame( int restart );
void CheckExitRules( void );


/*
================
vmMain

This is the only way control passes into the module.
This must be the very first function compiled into the .q3vm file
================
*/
int vmMain( int command, int arg0, int arg1, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8, int arg9, int arg10, int arg11  ) {
	switch ( command ) {
	case GAME_INIT:
		G_InitGame( arg0, arg1, arg2 );
		return 0;
	case GAME_SHUTDOWN:
		G_ShutdownGame( arg0 );
		return 0;
	case GAME_CLIENT_CONNECT:
		return (int)ClientConnect( arg0, arg1, arg2 );
	case GAME_CLIENT_THINK:
		ClientThink( arg0 );
		return 0;
	case GAME_CLIENT_USERINFO_CHANGED:
		ClientUserinfoChanged( arg0 );
		return 0;
	case GAME_CLIENT_DISCONNECT:
		ClientDisconnect( arg0 );
		return 0;
	case GAME_CLIENT_BEGIN:
		ClientBegin( arg0 );
		return 0;
	case GAME_CLIENT_COMMAND:
		ClientCommand( arg0 );
		return 0;
	case GAME_RUN_FRAME:
		G_RunFrame( arg0 );
		return 0;
	case GAME_CONSOLE_COMMAND:
		return ConsoleCommand();
	case BOTAI_START_FRAME:
		return BotAIStartFrame( arg0 );
	}

	return -1;
}


void QDECL G_Printf( const char *fmt, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, fmt);
	vsprintf (text, fmt, argptr);
	va_end (argptr);

	trap_Printf( text );
}

void QDECL G_Error( const char *fmt, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, fmt);
	vsprintf (text, fmt, argptr);
	va_end (argptr);

	trap_Error( text );
}

/*
================
G_FindTeams

Chain together all entities with a matching team field.
Entity teams are used for item groups and multi-entity mover groups.

All but the first will have the FL_TEAMSLAVE flag set and teammaster field set
All but the last will have the teamchain field set to the next one
================
*/
void G_FindTeams( void ) {
	gentity_t	*e, *e2;
	int		i, j;
	int		c, c2;

	c = 0;
	c2 = 0;
	for ( i=1, e=g_entities+i ; i < level.num_entities ; i++,e++ ){
		if (!e->inuse)
			continue;
		if (!e->team)
			continue;
		if (e->flags & FL_TEAMSLAVE)
			continue;
		e->teammaster = e;
		c++;
		c2++;
		for (j=i+1, e2=e+1 ; j < level.num_entities ; j++,e2++)
		{
			if (!e2->inuse)
				continue;
			if (!e2->team)
				continue;
			if (e2->flags & FL_TEAMSLAVE)
				continue;
			if (!strcmp(e->team, e2->team))
			{
				c2++;
				e2->teamchain = e->teamchain;
				e->teamchain = e2;
				e2->teammaster = e;
				e2->flags |= FL_TEAMSLAVE;

				// make sure that targets only point at the master
				if ( e2->targetname ) {
					e->targetname = e2->targetname;
					e2->targetname = NULL;
				}
			}
		}
	}

	G_Printf ("%i teams with %i entities\n", c, c2);
}

void G_RemapTeamShaders() {
	char string[1024];
	float f = level.time * 0.001;
	Com_sprintf( string, sizeof(string), "team_icon/%s_red", g_redteam.string );
	AddRemap("textures/ctf2/redteam01", string, f); 
	AddRemap("textures/ctf2/redteam02", string, f); 
	Com_sprintf( string, sizeof(string), "team_icon/%s_blue", g_blueteam.string );
	AddRemap("textures/ctf2/blueteam01", string, f); 
	AddRemap("textures/ctf2/blueteam02", string, f); 
	trap_SetConfigstring(CS_SHADERSTATE, BuildShaderStateConfig());
}


/*
=================
G_RegisterCvars
=================
*/
void G_RegisterCvars( void ) {
	int                     i;
	cvarTable_t     *cv;
	qboolean remapped = qfalse;

	for ( i = 0, cv = gameCvarTable ; i < gameCvarTableSize ; i++, cv++ ) {
		trap_Cvar_Register( cv->vmCvar, cv->cvarName,
		        cv->defaultString, cv->cvarFlags );
		G_RegisterCvarHelp( cv );
		if ( cv->vmCvar ) {
		        cv->modificationCount = cv->vmCvar->modificationCount;
		}

		if (cv->teamShader) {
		        remapped = qtrue;
		}
	}

        if (remapped) {
                	G_RemapTeamShaders();
        }

        G_Config_RegisterCvars();
        G_Config_UpdateCvars();
	G_RegisterPmoveCvars();
	G_RefreshPmoveSettings();

        // check some things
        if ( g_gametype.integer < 0 || g_gametype.integer >= GT_MAX_GAME_TYPE ) {
                G_Printf( "g_gametype %i is out of range, defaulting to 0\n", g_gametype.integer );
                trap_Cvar_Set( "g_gametype", "0" );
        }

	level.warmupModificationCount = g_warmup.modificationCount;
	s_itemTimersModCount = g_itemTimers.modificationCount;
	s_itemHeightModCount = g_itemHeight.modificationCount;
	s_forceSmallScoreboardMessageModCount = g_forceSmallScoreboardMessage.modificationCount;
	s_forceSendConfigstringModCount = g_forceSendConfigstring.modificationCount;
	s_forceAtmosphericEffectsModCount = g_forceAtmosphericEffects.modificationCount;
	s_forceDmgThroughSurfaceModCount = g_forceDmgThroughSurface.modificationCount;
s_forcedAtmosphereModCount = g_forcedAtmosphere.modificationCount;
s_worldspawnAtmosphere[0] = '\0';
s_lastForcedCosmeticsPayload[0] = '\0';
G_UpdateItemTimerConfig( qtrue );
G_UpdateForcedCosmeticsConfigstring( qtrue );
G_UpdateGametypeTutorialText();
G_InitWeaponConfig();
        G_InitWeaponReloadConfig();
        G_InitKnockbackConfig();
        G_InitStartingAmmoConfig();
        G_InitAmmoPackConfig();
        G_InitFactoryCvarConfig();
        G_InitMatchFactoryConfig();
	G_SyncMatchFactoryConfigToLevel();
	level.quadHogEnabled = ( g_weaponConfig.quadHogEnabled != 0 );
	level.quadHogOwner = ENTITYNUM_NONE;
	level.quadHogExpireTime = 0;
	level.quadHogLastActiveTime = 0;
	level.quadHogNextPingTime = 0;

	G_RefreshPmoveSettings();
}

void G_UpdateCvars( void ) {
        int                     i;
        cvarTable_t     *cv;
        qboolean remapped = qfalse;

        for ( i = 0, cv = gameCvarTable ; i < gameCvarTableSize ; i++, cv++ ) {
                if ( cv->vmCvar ) {
                        trap_Cvar_Update( cv->vmCvar );

                        if ( cv->modificationCount != cv->vmCvar->modificationCount ) {
                                cv->modificationCount = cv->vmCvar->modificationCount;

                                if ( cv->trackChange ) {
                                        trap_SendServerCommand( -1, va("print \"Server: %s changed to %s\n\"",
                                                cv->cvarName, cv->vmCvar->string ) );
                                }

                                if (cv->teamShader) {
                                        remapped = qtrue;
                                }
                        }
                }
        }

        if (remapped) {
                G_RemapTeamShaders();
        }

        G_Config_UpdateCvars();

        G_UpdateWeaponConfig();
        G_UpdateWeaponReloadConfig();
        G_UpdateKnockbackConfig();
        G_UpdateStartingAmmoConfig();
        G_UpdateAmmoPackConfig();
        G_UpdateFactoryCvarConfig();
        G_UpdateMatchFactoryConfig();
	G_SyncMatchFactoryConfigToLevel();
	if ( g_itemTimers.modificationCount != s_itemTimersModCount || g_itemHeight.modificationCount != s_itemHeightModCount ) {
		s_itemTimersModCount = g_itemTimers.modificationCount;
		s_itemHeightModCount = g_itemHeight.modificationCount;
		G_UpdateItemTimerConfig( qfalse );
	}
	if ( g_forceSmallScoreboardMessage.modificationCount != s_forceSmallScoreboardMessageModCount ||
		 g_forceSendConfigstring.modificationCount != s_forceSendConfigstringModCount ||
		 g_forceAtmosphericEffects.modificationCount != s_forceAtmosphericEffectsModCount ||
		 g_forceDmgThroughSurface.modificationCount != s_forceDmgThroughSurfaceModCount ||
		 g_forcedAtmosphere.modificationCount != s_forcedAtmosphereModCount ) {
		s_forceSmallScoreboardMessageModCount = g_forceSmallScoreboardMessage.modificationCount;
		s_forceSendConfigstringModCount = g_forceSendConfigstring.modificationCount;
		s_forceAtmosphericEffectsModCount = g_forceAtmosphericEffects.modificationCount;
		s_forceDmgThroughSurfaceModCount = g_forceDmgThroughSurface.modificationCount;
		s_forcedAtmosphereModCount = g_forcedAtmosphere.modificationCount;
		G_UpdateForcedCosmeticsConfigstring( qtrue );
	}
	level.quadHogEnabled = ( g_weaponConfig.quadHogEnabled != 0 );

G_UpdateTrainingState();
G_UpdateGametypeTutorialText();
G_RefreshPmoveSettings();
}

/*
=============
G_UpdateTrainingState

Synchronises the latched g_training cvar with the level training flag.
=============
*/
static void G_UpdateTrainingState( void ) {
trap_Cvar_Update( &g_training );
level.trainingMapActive = ( g_training.integer != 0 ) ? qtrue : qfalse;
}

typedef enum {
	GAMETYPE_LIFECYCLE_INIT,
	GAMETYPE_LIFECYCLE_CLIENT_BEGIN,
	GAMETYPE_LIFECYCLE_CLIENT_SPAWN
} gametypeLifecycleStage_t;

/*
=============
G_GametypeHandleDefault

No-op placeholder used when a gametype does not require custom
lifecycle handling.
=============
*/
static void G_GametypeHandleDefault( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	(void)stage;
	(void)ent;
}

/*
=============
G_GametypeHandleDuel

Hook invoked whenever a Duel lifecycle stage fires.  The Quake Live
binary applies custom loadouts here; the GPL drop simply preserves the
dispatch point for parity with the HLIL notes.
=============
*/
static void G_GametypeHandleDuel( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	(void)stage;
	(void)ent;
}

/*
=============
G_GametypeHandleRoundBased

Ensures round-based matches start in the warmup state so the round
controller can manage respawns.
=============
*/
static void G_GametypeHandleRoundBased( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	if ( stage == GAMETYPE_LIFECYCLE_INIT ) {
		G_Frame_BeginRoundWarmup();
	}

	(void)ent;
}

/*
=============
G_GametypeHandleRace

Routes the race-specific lifecycle hooks.
=============
*/
static void G_GametypeHandleRace( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	switch ( stage ) {
	case GAMETYPE_LIFECYCLE_CLIENT_BEGIN:
		if ( ent ) {
			G_RaceClientBegin( ent );
		}
		break;

	case GAMETYPE_LIFECYCLE_CLIENT_SPAWN:
		if ( ent ) {
			G_RaceClientSpawn( ent );
		}
		break;

	default:
		break;
	}

	G_GametypeHandleDefault( stage, ent );
}

/*
=============
G_RunGametypeLifecycle

Routes the current lifecycle stage through any gametype-specific helper
that needs to mirror the Quake Live dispatch table.
=============
*/
static void G_RunGametypeLifecycle( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	switch ( g_gametype.integer ) {
	case GT_TOURNAMENT:
		G_GametypeHandleDuel( stage, ent );
		break;
	case GT_RACE:
		G_GametypeHandleRace( stage, ent );
		break;

	case GT_CLAN_ARENA:
	case GT_RED_ROVER:
		G_GametypeHandleRoundBased( stage, ent );
		break;

	default:
		G_GametypeHandleDefault( stage, ent );
		break;
	}
}

/*
=============
G_GametypeInit

Executes the init-stage lifecycle hook for the current gametype.
=============
*/
void G_GametypeInit( void ) {
	G_RunGametypeLifecycle( GAMETYPE_LIFECYCLE_INIT, NULL );
}

/*
=============
G_GametypeClientBegin

Executes the ClientBegin-stage lifecycle hook for the current gametype.
=============
*/
void G_GametypeClientBegin( gentity_t *ent ) {
	G_RunGametypeLifecycle( GAMETYPE_LIFECYCLE_CLIENT_BEGIN, ent );
}

/*
=============
G_GametypeClientSpawn

Executes the ClientSpawn-stage lifecycle hook for the current gametype.
=============
*/
void G_GametypeClientSpawn( gentity_t *ent ) {
	G_RunGametypeLifecycle( GAMETYPE_LIFECYCLE_CLIENT_SPAWN, ent );
}


/*
============
G_InitGame

============
*/
void G_InitGame( int levelTime, int randomSeed, int restart ) {
	int					i;

	G_Printf ("------- Game Initialization -------\n");
	G_Printf ("gamename: %s\n", GAMEVERSION);
	G_Printf ("gamedate: %s\n", __DATE__);

	srand( randomSeed );
	{
		time_t levelStart = time( NULL );
		char startTimeBuffer[32];
		Com_sprintf( startTimeBuffer, sizeof( startTimeBuffer ), "%u", (unsigned int)levelStart );
		trap_Cvar_Set( "g_levelStartTime", startTimeBuffer );
	}


G_RegisterCvars();
trap_Cvar_Update( &mercylimit );
trap_Cvar_Update( &g_mercytime );

trap_Cvar_Set( "g_training", "0" );
G_UpdateTrainingState();

	G_ProcessIPBans();

	G_InitMemory();

// set some level globals
	memset( &level, 0, sizeof( level ) );
	if ( g_gametype.integer == GT_RACE ) {
		G_RaceInitLevel();
	}
	G_InitSpawnQueue();
	G_FreezeSyncCvars();
	level.time = levelTime;
	level.startTime = levelTime;
	level.roundState = ROUNDSTATE_INACTIVE;
	level.roundTransitionTime = ROUND_TRANSITION_NONE;

	level.timeoutOwner = -1;
	level.timeoutTeam = TEAM_FREE;
	level.timeoutActive = qfalse;
	level.timeoutStartTime = 0;
	level.timeoutExpireTime = 0;
	level.overtimeActive = qfalse;
	level.overtimeStartTime = 0;
	level.overtimeEndTime = 0;
	level.overtimeCount = 0;
	level.suddenDeathActive = qfalse;
	level.suddenDeathLastDelay = -1;
	level.suddenDeathNoRespawnLogged = qfalse;
	level.matchForfeited = qfalse;
        {
                int team;
                for ( team = TEAM_FREE; team < TEAM_NUM_TEAMS; team++ ) {
                        level.timeoutRemaining[team] = g_matchFactoryConfig.timeoutCountPerTeam;
                }
        }
        matchFlow_lastConfig = g_matchFactoryConfig;

	level.snd_fry = G_SoundIndex("sound/player/fry.wav");	// FIXME standing in lava / slime

	if ( g_gametype.integer != GT_SINGLE_PLAYER && g_log.string[0] ) {
		if ( g_logSync.integer ) {
			trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND_SYNC );
		} else {
			trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND );
		}
		if ( !level.logFile ) {
			G_Printf( "WARNING: Couldn't open logfile: %s\n", g_log.string );
		} else {
			char	serverinfo[MAX_INFO_STRING];

			trap_GetServerinfo( serverinfo, sizeof( serverinfo ) );

			G_LogPrintf("------------------------------------------------------------\n" );
			G_LogPrintf("InitGame: %s\n", serverinfo );
		}
	} else {
		G_Printf( "Not logging to disk.\n" );
	}

	G_InitWorldSession();

	// initialize all entities for this game
	memset( g_entities, 0, MAX_GENTITIES * sizeof(g_entities[0]) );
	level.gentities = g_entities;

	// initialize all clients for this game
	level.maxclients = g_maxclients.integer;
	memset( g_clients, 0, MAX_CLIENTS * sizeof(g_clients[0]) );
	level.clients = g_clients;

	// set client fields on player ents
	for ( i=0 ; i<level.maxclients ; i++ ) {
		g_entities[i].client = level.clients + i;
		G_InitClientVoteThrottle( level.clients + i );
	}

	// always leave room for the max number of clients,
	// even if they aren't all used, so numbers inside that
	// range are NEVER anything but clients
	level.num_entities = MAX_CLIENTS;

	// let the server system know where the entites are
	trap_LocateGameData( level.gentities, level.num_entities, sizeof( gentity_t ), 
		&level.clients[0].ps, sizeof( level.clients[0] ) );

	// reserve some spots for dead player bodies
	InitBodyQue();

	ClearRegisteredItems();

	// parse the key/value pairs and spawn gentities
	G_SpawnEntitiesFromString();
	G_UpdateTrainingState();
	if ( level.trainingMapActive ) {
		int team;
		for ( team = TEAM_FREE; team < TEAM_NUM_TEAMS; team++ ) {
			level.timeoutRemaining[team] = 0;
		}
		level.timeoutActive = qfalse;
		level.timeoutOwner = -1;
		level.timeoutTeam = TEAM_FREE;
		level.timeoutExpireTime = 0;
		level.timeoutStartTime = 0;
	}

	// general initialization
	G_FindTeams();

	// make sure we have flags for CTF, etc
	if( g_gametype.integer >= GT_TEAM ) {
		G_CheckTeamItems();
	}

	G_GametypeInit();

	SaveRegisteredItems();

	G_Printf ("-----------------------------------\n");

	if( g_gametype.integer == GT_SINGLE_PLAYER || trap_Cvar_VariableIntegerValue( "com_buildScript" ) ) {
		G_ModelIndex( SP_PODIUM_MODEL );
		G_SoundIndex( "sound/player/gurp1.wav" );
		G_SoundIndex( "sound/player/gurp2.wav" );
	}

	if ( trap_Cvar_VariableIntegerValue( "bot_enable" ) ) {
		BotAISetup( restart );
		BotAILoadMap( restart );
		G_InitBots( restart );
	}

	G_RemapTeamShaders();

	LevelCheckTimers();
	G_UpdateMatchStateConfigString();
	G_MatchConfig_UpdateConfigstrings();

}



/*
=================
G_ShutdownGame
=================
*/
void G_ShutdownGame( int restart ) {
	G_Printf ("==== ShutdownGame ====\n");

	if ( level.logFile ) {
		G_LogPrintf("ShutdownGame:\n" );
		G_LogPrintf("------------------------------------------------------------\n" );
		trap_FS_FCloseFile( level.logFile );
	}

	// write all the client session data so we can get it back
	G_WriteSessionData();

	if ( trap_Cvar_VariableIntegerValue( "bot_enable" ) ) {
		BotAIShutdown( restart );
	}
}



//===================================================================

#ifndef GAME_HARD_LINKED
// this is only here so the functions in q_shared.c and bg_*.c can link

void QDECL Com_Error ( int level, const char *error, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, error);
	vsprintf (text, error, argptr);
	va_end (argptr);

	G_Error( "%s", text);
}

void QDECL Com_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, msg);
	vsprintf (text, msg, argptr);
	va_end (argptr);

	G_Printf ("%s", text);
}

#endif

/*
========================================================================

PLAYER COUNTING / SCORE SORTING

========================================================================
*/

/*
=============
AddTournamentPlayer

If there are less than two tournament players, put a
spectator in the game and restart
=============
*/
void AddTournamentPlayer( void ) {
	int			i;
	gclient_t	*client;
	gclient_t	*nextInLine;

	if ( level.numPlayingClients >= 2 ) {
		return;
	}

	// never change during intermission
	if ( level.intermissiontime ) {
		return;
	}

	nextInLine = NULL;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != TEAM_SPECTATOR ) {
			continue;
		}
		// never select the dedicated follow or scoreboard clients
		if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD || 
			client->sess.spectatorClient < 0  ) {
			continue;
		}

		if ( !nextInLine || client->sess.spectatorTime < nextInLine->sess.spectatorTime ) {
			nextInLine = client;
		}
	}

	if ( !nextInLine ) {
		return;
	}

	level.warmupTime = -1;

	// set them to free-for-all team
	SetTeam( &g_entities[ nextInLine - level.clients ], "f" );
}

/*
=======================
RemoveTournamentLoser

Make the loser a spectator at the back of the line
=======================
*/
void RemoveTournamentLoser( void ) {
	int			clientNum;

	if ( level.numPlayingClients != 2 ) {
		return;
	}

	clientNum = level.sortedClients[1];

	if ( level.clients[ clientNum ].pers.connected != CON_CONNECTED ) {
		return;
	}

	// make them a spectator
	SetTeam( &g_entities[ clientNum ], "s" );
}

/*
=======================
RemoveTournamentWinner
=======================
*/
void RemoveTournamentWinner( void ) {
	int			clientNum;

	if ( level.numPlayingClients != 2 ) {
		return;
	}

	clientNum = level.sortedClients[0];

	if ( level.clients[ clientNum ].pers.connected != CON_CONNECTED ) {
		return;
	}

	// make them a spectator
	SetTeam( &g_entities[ clientNum ], "s" );
}

/*
=======================
AdjustTournamentScores
=======================
*/
void AdjustTournamentScores( void ) {
	int			clientNum;

	clientNum = level.sortedClients[0];
	if ( level.clients[ clientNum ].pers.connected == CON_CONNECTED ) {
		level.clients[ clientNum ].sess.wins++;
		ClientUserinfoChanged( clientNum );
	}

	clientNum = level.sortedClients[1];
	if ( level.clients[ clientNum ].pers.connected == CON_CONNECTED ) {
		level.clients[ clientNum ].sess.losses++;
		ClientUserinfoChanged( clientNum );
	}

}

/*
=============
SortRanks

=============
*/
int QDECL SortRanks( const void *a, const void *b ) {
	gclient_t	*ca, *cb;

	ca = &level.clients[*(int *)a];
	cb = &level.clients[*(int *)b];

	// sort special clients last
	if ( ca->sess.spectatorState == SPECTATOR_SCOREBOARD || ca->sess.spectatorClient < 0 ) {
		return 1;
	}
	if ( cb->sess.spectatorState == SPECTATOR_SCOREBOARD || cb->sess.spectatorClient < 0  ) {
		return -1;
	}

	// then connecting clients
	if ( ca->pers.connected == CON_CONNECTING ) {
		return 1;
	}
	if ( cb->pers.connected == CON_CONNECTING ) {
		return -1;
	}


	// then spectators
	if ( ca->sess.sessionTeam == TEAM_SPECTATOR && cb->sess.sessionTeam == TEAM_SPECTATOR ) {
		if ( ca->sess.spectatorTime < cb->sess.spectatorTime ) {
			return -1;
		}
		if ( ca->sess.spectatorTime > cb->sess.spectatorTime ) {
			return 1;
		}
		return 0;
	}
	if ( ca->sess.sessionTeam == TEAM_SPECTATOR ) {
		return 1;
	}
	if ( cb->sess.sessionTeam == TEAM_SPECTATOR ) {
		return -1;
	}

	// then sort by score
	if ( ca->ps.persistant[PERS_SCORE]
		> cb->ps.persistant[PERS_SCORE] ) {
		return -1;
	}
	if ( ca->ps.persistant[PERS_SCORE]
		< cb->ps.persistant[PERS_SCORE] ) {
		return 1;
	}
	return 0;
}

/*
============
CalculateRanks

Recalculates the score ranks of all players
This will be called on every client connect, begin, disconnect, death,
and team change.
============
*/
void CalculateRanks( void ) {
	int		i;
	int		rank;
	int		score;
	int		newScore;
	gclient_t	*cl;

	level.follow1 = -1;
	level.follow2 = -1;
	level.numConnectedClients = 0;
	level.numNonSpectatorClients = 0;
	level.numPlayingClients = 0;
	level.numVotingClients = 0;		// don't count bots
	for ( i = 0; i < TEAM_NUM_TEAMS; i++ ) {
		level.numteamVotingClients[i] = 0;
	}
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].pers.connected != CON_DISCONNECTED ) {
			level.sortedClients[level.numConnectedClients] = i;
			level.numConnectedClients++;

			if ( level.clients[i].sess.sessionTeam != TEAM_SPECTATOR ) {
				level.numNonSpectatorClients++;
			
				// decide if this should be auto-followed
				if ( level.clients[i].pers.connected == CON_CONNECTED ) {
					level.numPlayingClients++;
					if ( !(g_entities[i].r.svFlags & SVF_BOT) ) {
						level.numVotingClients++;
						if ( level.clients[i].sess.sessionTeam == TEAM_RED )
							level.numteamVotingClients[0]++;
						else if ( level.clients[i].sess.sessionTeam == TEAM_BLUE )
							level.numteamVotingClients[1]++;
					}
					if ( level.follow1 == -1 ) {
						level.follow1 = i;
					} else if ( level.follow2 == -1 ) {
						level.follow2 = i;
					}
				}
			}
		}
	}

	qsort( level.sortedClients, level.numConnectedClients, 
		sizeof(level.sortedClients[0]), SortRanks );

	// set the rank value for all clients that are connected and not spectators
	if ( g_gametype.integer >= GT_TEAM ) {
		// in team games, rank is just the order of the teams, 0=red, 1=blue, 2=tied
		for ( i = 0;  i < level.numConnectedClients; i++ ) {
			cl = &level.clients[ level.sortedClients[i] ];
			if ( level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE] ) {
				cl->ps.persistant[PERS_RANK] = 2;
			} else if ( level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE] ) {
				cl->ps.persistant[PERS_RANK] = 0;
			} else {
				cl->ps.persistant[PERS_RANK] = 1;
			}
		}
	} else {	
		rank = -1;
		score = 0;
		for ( i = 0;  i < level.numPlayingClients; i++ ) {
			cl = &level.clients[ level.sortedClients[i] ];
			newScore = cl->ps.persistant[PERS_SCORE];
			if ( i == 0 || newScore != score ) {
				rank = i;
				// assume we aren't tied until the next client is checked
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank;
			} else {
				// we are tied with the previous client
				level.clients[ level.sortedClients[i-1] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
			}
			score = newScore;
			if ( g_gametype.integer == GT_SINGLE_PLAYER && level.numPlayingClients == 1 ) {
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
			}
		}
	}

	// set the CS_SCORES1/2 configstrings, which will be visible to everyone
	if ( g_gametype.integer >= GT_TEAM ) {
		trap_SetConfigstring( CS_SCORES1, va("%i", level.teamScores[TEAM_RED] ) );
		trap_SetConfigstring( CS_SCORES2, va("%i", level.teamScores[TEAM_BLUE] ) );
	} else {
		if ( level.numConnectedClients == 0 ) {
			trap_SetConfigstring( CS_SCORES1, va("%i", SCORE_NOT_PRESENT) );
			trap_SetConfigstring( CS_SCORES2, va("%i", SCORE_NOT_PRESENT) );
		} else if ( level.numConnectedClients == 1 ) {
			trap_SetConfigstring( CS_SCORES1, va("%i", level.clients[ level.sortedClients[0] ].ps.persistant[PERS_SCORE] ) );
			trap_SetConfigstring( CS_SCORES2, va("%i", SCORE_NOT_PRESENT) );
		} else {
			trap_SetConfigstring( CS_SCORES1, va("%i", level.clients[ level.sortedClients[0] ].ps.persistant[PERS_SCORE] ) );
			trap_SetConfigstring( CS_SCORES2, va("%i", level.clients[ level.sortedClients[1] ].ps.persistant[PERS_SCORE] ) );
		}
	}

	// see if it is time to end the level
	CheckExitRules();

	// if we are at the intermission, send the new info to everyone
	if ( level.intermissiontime ) {
		SendScoreboardMessageToAllClients();
	}
}


/*
========================================================================

MAP CHANGING

========================================================================
*/

/*
========================
SendScoreboardMessageToAllClients

Do this at BeginIntermission time and whenever ranks are recalculated
due to enters/exits/forced team changes
========================
*/
void SendScoreboardMessageToAllClients( void ) {
	int		i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[ i ].pers.connected == CON_CONNECTED ) {
			DeathmatchScoreboardMessage( g_entities + i );
		}
	}
}

/*
========================
MoveClientToIntermission

When the intermission starts, this will be called for all players.
If a new client connects, this will be called after the spawn function.
========================
*/
void MoveClientToIntermission( gentity_t *ent ) {
	// take out of follow mode if needed
	if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
		StopFollowing( ent );
	}


	// move to the spot
	VectorCopy( level.intermission_origin, ent->s.origin );
	VectorCopy( level.intermission_origin, ent->client->ps.origin );
	VectorCopy (level.intermission_angle, ent->client->ps.viewangles);
	ent->client->ps.pm_type = PM_INTERMISSION;

	// clean up powerup info
	memset( ent->client->ps.powerups, 0, sizeof(ent->client->ps.powerups) );

	ent->client->ps.eFlags = 0;
	ent->s.eFlags = 0;
	ent->s.eType = ET_GENERAL;
	ent->s.modelindex = 0;
	ent->s.loopSound = 0;
	ent->s.event = 0;
	ent->r.contents = 0;
}

/*
==================
FindIntermissionPoint

This is also used for spectator spawns
==================
*/
void FindIntermissionPoint( void ) {
	gentity_t	*ent, *target;
	vec3_t		dir;

	// find the intermission spot
	ent = G_Find (NULL, FOFS(classname), "info_player_intermission");
	if ( !ent ) {	// the map creator forgot to put in an intermission point...
		SelectSpawnPoint ( vec3_origin, level.intermission_origin, level.intermission_angle );
	} else {
		VectorCopy (ent->s.origin, level.intermission_origin);
		VectorCopy (ent->s.angles, level.intermission_angle);
		// if it has a target, look towards it
		if ( ent->target ) {
			target = G_PickTarget( ent->target );
			if ( target ) {
				VectorSubtract( target->s.origin, level.intermission_origin, dir );
				vectoangles( dir, level.intermission_angle );
			}
		}
	}

}

/*
==================
BeginIntermission
==================
*/
void BeginIntermission( void ) {
	int			i;
	gentity_t	*client;

	if ( level.intermissiontime ) {
		return;		// already active
	}

	// if in tournement mode, change the wins / losses
	if ( g_gametype.integer == GT_TOURNAMENT ) {
		AdjustTournamentScores();
	}

	level.intermissiontime = level.time;
	FindIntermissionPoint();

	if (g_singlePlayer.integer) {
		trap_Cvar_Set("ui_singlePlayerActive", "0");
		UpdateTournamentInfo();
	}

	// move all clients to the intermission point
	for (i=0 ; i< level.maxclients ; i++) {
		client = g_entities + i;
		if (!client->inuse)
			continue;
		// respawn if dead
		if (client->health <= 0) {
			respawn(client);
		}
		MoveClientToIntermission( client );
	}

	// send the current scoring to all clients
	SendScoreboardMessageToAllClients();

}


/*
=============
ExitLevel

When the intermission has been exited, the server is either killed
or moved to a new level based on the "nextmap" cvar 

=============
*/
void ExitLevel (void) {
	int		i;
	gclient_t *cl;

	//bot interbreeding
	BotInterbreedEndMatch();

	// if we are running a tournement map, kick the loser to spectator status,
	// which will automatically grab the next spectator and restart
	if ( g_gametype.integer == GT_TOURNAMENT  ) {
		if ( !level.restarted ) {
			RemoveTournamentLoser();
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			level.restarted = qtrue;
			level.changemap = NULL;
			level.intermissiontime = 0;
		}
		return;	
	}


	trap_SendConsoleCommand( EXEC_APPEND, "vstr nextmap\n" );
	level.changemap = NULL;
	level.intermissiontime = 0;

	// reset all the scores so we don't enter the intermission again
	level.teamScores[TEAM_RED] = 0;
	level.teamScores[TEAM_BLUE] = 0;
	for ( i=0 ; i< g_maxclients.integer ; i++ ) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		cl->ps.persistant[PERS_SCORE] = 0;
	}

	// we need to do this here before chaning to CON_CONNECTING
	G_WriteSessionData();

	// change all client states to connecting, so the early players into the
	// next level will know the others aren't done reconnecting
	for (i=0 ; i< g_maxclients.integer ; i++) {
		if ( level.clients[i].pers.connected == CON_CONNECTED ) {
			level.clients[i].pers.connected = CON_CONNECTING;
		}
	}

}

/*
=================
G_LogPrintf

Print to the logfile with a time stamp if it is open
=================
*/
void QDECL G_LogPrintf( const char *fmt, ... ) {
	va_list		argptr;
	char		string[1024];
	int			min, tens, sec;

	sec = level.time / 1000;

	min = sec / 60;
	sec -= min * 60;
	tens = sec / 10;
	sec -= tens * 10;

	Com_sprintf( string, sizeof(string), "%3i:%i%i ", min, tens, sec );

	va_start( argptr, fmt );
	vsprintf( string +7 , fmt,argptr );
	va_end( argptr );

	if ( g_dedicated.integer ) {
		G_Printf( "%s", string + 7 );
	}

	if ( !level.logFile ) {
		return;
	}

	trap_FS_Write( string, strlen( string ), level.logFile );
}

/*
================
LogExit

Append information about this game to the log file
================
*/
void LogExit( const char *string ) {
	int				i, numSorted;
	gclient_t		*cl;
	qboolean won = qtrue;
	G_LogPrintf( "Exit: %s\n", string );

	level.intermissionQueued = level.time;

	// this will keep the clients from playing any voice sounds
	// that will get cut off when the queued intermission starts
	trap_SetConfigstring( CS_INTERMISSION, "1" );

	// don't send more than 32 scores (FIXME?)
	numSorted = level.numConnectedClients;
	if ( numSorted > 32 ) {
		numSorted = 32;
	}

	if ( g_gametype.integer >= GT_TEAM ) {
		G_LogPrintf( "red:%i  blue:%i\n",
			level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE] );
	}

	for (i=0 ; i < numSorted ; i++) {
		int		ping;

		cl = &level.clients[level.sortedClients[i]];

		if ( cl->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}
		if ( cl->pers.connected == CON_CONNECTING ) {
			continue;
		}

		ping = cl->ps.ping < 999 ? cl->ps.ping : 999;

		G_LogPrintf( "score: %i  ping: %i  client: %i %s\n", cl->ps.persistant[PERS_SCORE], ping, level.sortedClients[i],	cl->pers.netname );
		if (g_singlePlayer.integer && g_gametype.integer == GT_TOURNAMENT) {
			if (g_entities[cl - level.clients].r.svFlags & SVF_BOT && cl->ps.persistant[PERS_RANK] == 0) {
				won = qfalse;
			}
		}

	}

	if (g_singlePlayer.integer) {
		if (g_gametype.integer >= GT_CTF) {
			won = level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE];
		}
		trap_SendConsoleCommand( EXEC_APPEND, (won) ? "spWin\n" : "spLose\n" );
	}


}

/*
=============
G_ApplyForfeit

Ends the current match because a player forfeited.
=============
*/
void G_ApplyForfeit( gentity_t *ent ) {
	if ( level.matchForfeited ) {
		return;
	}

	level.matchForfeited = qtrue;

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		if ( ent && ent->client && ent->health > 0 ) {
			ent->flags &= ~FL_GODMODE;
			ent->client->ps.stats[STAT_HEALTH] = ent->health = -999;
			player_die( ent, ent, ent, 100000, MOD_SUICIDE );
		}
	}

	trap_SendServerCommand( -1, "print \"Game has been forfeited.\\n\"" );
	LogExit( "Players have forfeited." );
}

/*
=================
CheckIntermissionExit

The level will stay at the intermission for a minimum of 5 seconds
If all players wish to continue, the level will then exit.
If one or more players have not acknowledged the continue, the game will
wait 10 seconds before going on.
=================
*/
void CheckIntermissionExit( void ) {
	int			ready, notReady;
	int			i;
	gclient_t	*cl;
	int			readyMask;

	if ( g_gametype.integer == GT_SINGLE_PLAYER ) {
		return;
	}

	// see which players are ready
	ready = 0;
	notReady = 0;
	readyMask = 0;
	for (i=0 ; i< g_maxclients.integer ; i++) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( g_entities[cl->ps.clientNum].r.svFlags & SVF_BOT ) {
			continue;
		}

		if ( cl->readyToExit ) {
			ready++;
			if ( i < 16 ) {
				readyMask |= 1 << i;
			}
		} else {
			notReady++;
		}
	}

	// copy the readyMask to each player's stats so
	// it can be displayed on the scoreboard
	for (i=0 ; i< g_maxclients.integer ; i++) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		cl->ps.stats[STAT_CLIENTS_READY] = readyMask;
	}

	// never exit in less than five seconds
	if ( level.time < level.intermissiontime + 5000 ) {
		return;
	}

	// if nobody wants to go, clear timer
	if ( !ready ) {
		level.readyToExit = qfalse;
		return;
	}

	// if everyone wants to go, go now
	if ( !notReady ) {
		ExitLevel();
		return;
	}

	// the first person to ready starts the ten second timeout
	if ( !level.readyToExit ) {
		level.readyToExit = qtrue;
		level.exitTime = level.time;
	}

	// if we have waited ten seconds since at least one player
	// wanted to exit, go ahead
	if ( level.time < level.exitTime + 10000 ) {
		return;
	}

	ExitLevel();
}

/*
=============
ScoreIsTied
=============
*/
qboolean ScoreIsTied( void ) {
	int		a, b;

	if ( level.numPlayingClients < 2 ) {
		return qfalse;
	}
	
	if ( g_gametype.integer >= GT_TEAM ) {
		return level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE];
	}

	a = level.clients[level.sortedClients[0]].ps.persistant[PERS_SCORE];
	b = level.clients[level.sortedClients[1]].ps.persistant[PERS_SCORE];

	return a == b;
}

/*
=================
CheckExitRules

There will be a delay between the time the exit is qualified for
and the time everyone is moved to the intermission spot, so you
can see the last frag.
=================
*/
void CheckExitRules( void ) {
 	int			i;
	gclient_t	*cl;
	if ( level.timeoutActive ) {
		return;
	}
	// if at the intermission, wait for all non-bots to
	// signal ready, then go to next level
	if ( level.intermissiontime ) {
		CheckIntermissionExit ();
		return;
	}

	if ( level.intermissionQueued ) {
		int time = (g_singlePlayer.integer) ? SP_INTERMISSION_DELAY_TIME : INTERMISSION_DELAY_TIME;
		if ( level.time - level.intermissionQueued >= time ) {
			level.intermissionQueued = 0;
			BeginIntermission();
		}
		return;
	}

	// check for sudden death
	{
		qboolean suddenDeath = ScoreIsTied();

		if ( level.suddenDeathActive != suddenDeath ) {
			level.suddenDeathActive = suddenDeath;

			if ( suddenDeath ) {
				G_Printf( "Sudden death engaged (ammo respawn %s).\n", g_factoryCvarConfig.suddenDeathRespawn ? "active" : "paused" );
			} else {
				G_Printf( "Sudden death cleared; ammo respawn resumes.\n" );
			}
		}

		if ( suddenDeath ) {
			return;
		}
	}

        if ( g_timelimit.integer && !level.warmupTime ) {
                if ( level.time - level.startTime >= g_timelimit.integer*60000 ) {
                        trap_SendServerCommand( -1, "print \"Timelimit hit.\n\"");
                        LogExit( "Timelimit hit." );
                        return;
                }
        }

        if ( g_gametype.integer >= GT_TEAM && g_gametype.integer != GT_ATTACK_DEFEND && mercylimit.integer > 0 && !level.warmupTime ) {
                int mercyWindowMinutes = g_mercytime.integer;
                int mercyWindowMsec;
                int scoreDelta;
                int scoreSpread;
                const char *leadingTeam;

                if ( mercyWindowMinutes < 0 ) {
                        mercyWindowMinutes = 0;
                }

                if ( mercyWindowMinutes > 0 && mercyWindowMinutes > INT_MAX / 60000 ) {
                        mercyWindowMsec = INT_MAX;
                } else {
                        mercyWindowMsec = mercyWindowMinutes * 60000;
                }

                if ( level.time - level.startTime >= mercyWindowMsec ) {
                        scoreDelta = level.teamScores[TEAM_RED] - level.teamScores[TEAM_BLUE];
                        scoreSpread = ( scoreDelta >= 0 ) ? scoreDelta : -scoreDelta;
                        if ( scoreSpread > mercylimit.integer ) {
                                leadingTeam = ( scoreDelta > 0 ) ? "Red" : "Blue";
                                trap_SendServerCommand( -1, va( "print \"%s hit the mercylimit.\n\"", leadingTeam ) );
                                LogExit( "Mercylimit hit." );
                                return;
                        }
                }
        }

        if ( level.numPlayingClients < 2 ) {
                return;
        }

	if ( g_gametype.integer < GT_CTF && g_fraglimit.integer ) {
		if ( level.teamScores[TEAM_RED] >= g_fraglimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the fraglimit.\n\"" );
			LogExit( "Fraglimit hit." );
			return;
		}

		if ( level.teamScores[TEAM_BLUE] >= g_fraglimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the fraglimit.\n\"" );
			LogExit( "Fraglimit hit." );
			return;
		}

		for ( i=0 ; i< g_maxclients.integer ; i++ ) {
			cl = level.clients + i;
			if ( cl->pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( cl->sess.sessionTeam != TEAM_FREE ) {
				continue;
			}

			if ( cl->ps.persistant[PERS_SCORE] >= g_fraglimit.integer ) {
				LogExit( "Fraglimit hit." );
				trap_SendServerCommand( -1, va("print \"%s" S_COLOR_WHITE " hit the fraglimit.\n\"",
					cl->pers.netname ) );
				return;
			}
		}
	}

	if ( g_gametype.integer >= GT_CTF && g_capturelimit.integer ) {

		if ( level.teamScores[TEAM_RED] >= g_capturelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the capturelimit.\n\"" );
			LogExit( "Capturelimit hit." );
			return;
		}

		if ( level.teamScores[TEAM_BLUE] >= g_capturelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the capturelimit.\n\"" );
			LogExit( "Capturelimit hit." );
			return;
		}
	}
}




void G_UpdateMatchStateConfigString( void ) {
	int red = level.timeoutRemaining[TEAM_RED];
	int blue = level.timeoutRemaining[TEAM_BLUE];

	if ( g_gametype.integer < GT_TEAM ) {
		int duel = level.timeoutRemaining[TEAM_FREE];
		if ( duel < 0 ) {
			duel = 0;
		}
		red = duel;
		blue = duel;
	}

	if ( red < 0 ) {
		red = 0;
	}
	if ( blue < 0 ) {
		blue = 0;
	}

	trap_SetConfigstring( CS_MATCH_STATE, va("%i %i %i %i %i %i %i %i %i %i",
		level.overtimeActive ? 1 : 0,
		level.overtimeStartTime,
		level.overtimeEndTime,
		level.overtimeCount,
		level.timeoutActive ? 1 : 0,
		level.timeoutTeam,
		level.timeoutExpireTime,
		level.timeoutOwner,
		red,
		blue ) );
}

/*
=============
G_ResetTimeoutState

Clears the timeout bookkeeping so matches can resume immediately.
=============
*/
void G_ResetTimeoutState( void ) {
	level.timeoutActive = qfalse;
	level.timeoutOwner = -1;
	level.timeoutTeam = TEAM_FREE;
	level.timeoutExpireTime = 0;
	level.timeoutStartTime = 0;
}

void G_ApplyTimeoutPauseDelta( int msec ) {
	if ( msec <= 0 ) {
		return;
	}

	if ( level.warmupTime > 0 ) {
		level.warmupTime += msec;
		trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
	}

	if ( level.intermissionQueued ) {
		level.intermissionQueued += msec;
	}

	if ( level.readyToExit ) {
		level.exitTime += msec;
	}
}

int G_GetSuddenDeathRespawnDelay( void ) {
	const matchFactoryConfig_t *config = &g_matchFactoryConfig;

	if ( !level.overtimeActive ) {
		return 0;
	}
	if ( !config->suddenDeathRespawnsEnabled ) {
		return -1;
	}
	int baseDelay = config->suddenDeathStartSeconds;
	int tick = config->suddenDeathTickSeconds;
	int increment = config->suddenDeathIncrementSeconds;
	int maxDelay = config->suddenDeathMaxSeconds;
	int elapsed = ( level.time - level.overtimeStartTime ) / 1000;
	if ( elapsed < 0 ) {
		elapsed = 0;
	}
	int steps = elapsed / tick;
	int delaySeconds = baseDelay + steps * increment;
	if ( delaySeconds > maxDelay ) {
		delaySeconds = maxDelay;
	}
	return delaySeconds * 1000;
}

static void G_StartOrExtendOvertime( void ) {
        const int lengthSeconds = g_matchFactoryConfig.overtimeLengthSeconds;
	const int overtimeMillis = ( lengthSeconds > 0 ) ? lengthSeconds * 1000 : 0;
	if ( !level.overtimeActive ) {
		level.overtimeActive = qtrue;
		level.overtimeStartTime = level.time;
		level.overtimeEndTime = overtimeMillis > 0 ? level.time + overtimeMillis : 0;
		level.overtimeCount = 1;
		level.suddenDeathActive = qtrue;
		level.suddenDeathLastDelay = -1;
		level.suddenDeathNoRespawnLogged = qfalse;
		G_LogPrintf( "match: overtime period %i started (%i second window)\n", level.overtimeCount, lengthSeconds );
		G_UpdateMatchStateConfigString();
	} else if ( overtimeMillis > 0 && ( level.overtimeEndTime == 0 || level.time >= level.overtimeEndTime ) ) {
		level.overtimeCount++;
		level.overtimeStartTime = level.time;
		level.overtimeEndTime = level.time + overtimeMillis;
		level.suddenDeathLastDelay = -1;
		level.suddenDeathNoRespawnLogged = qfalse;
		G_LogPrintf( "match: overtime period %i started (%i second window)\n", level.overtimeCount, lengthSeconds );
		G_UpdateMatchStateConfigString();
	}
}

static void G_StopOvertime( void ) {
	if ( !level.overtimeActive ) {
		return;
	}
	level.overtimeActive = qfalse;
	level.overtimeEndTime = 0;
	level.overtimeStartTime = 0;
	level.suddenDeathActive = qfalse;
	level.suddenDeathLastDelay = -1;
	level.suddenDeathNoRespawnLogged = qfalse;
	G_LogPrintf( "match: overtime cleared\n" );
	G_UpdateMatchStateConfigString();


/*
=============
G_HandleForfeit

Transitions the current match into a forfeited state and synchronises timers, scores, and logs.
=============
*/
void G_HandleForfeit( gentity_t *caller ) {
	int pausedDuration;

	if ( level.matchForfeited ) {
		return;
	}

	level.matchForfeited = qtrue;

	pausedDuration = 0;
	if ( level.timeoutActive ) {
		if ( level.timeoutStartTime > 0 && level.time > level.timeoutStartTime ) {
			pausedDuration = level.time - level.timeoutStartTime;
		}
		if ( pausedDuration > 0 ) {
			G_ApplyTimeoutPauseDelta( pausedDuration );
		}
	}

	G_ResetTimeoutState();
	G_StopOvertime();
	G_UpdateMatchStateConfigString();

	if ( g_gametype.integer >= GT_TEAM ) {
		level.teamScores[TEAM_RED] = -999;
		level.teamScores[TEAM_BLUE] = -999;
		trap_SetConfigstring( CS_SCORES1, va( "%i", level.teamScores[TEAM_RED] ) );
		trap_SetConfigstring( CS_SCORES2, va( "%i", level.teamScores[TEAM_BLUE] ) );
	} else if ( g_gametype.integer == GT_TOURNAMENT && caller && caller->client ) {
		if ( caller->health > 0 ) {
			caller->flags &= ~FL_GODMODE;
			caller->client->ps.stats[STAT_HEALTH] = caller->health = -999;
			caller->client->pers.killCommandTime = level.time;
			player_die( caller, caller, caller, 100000, MOD_SUICIDE );
		}
	}

	trap_SendServerCommand( -1, "print \"Game has been forfeited.\n\"" );
	LogExit( "Players have forfeited." );
	CalculateRanks();
}

/*
=============
G_TrackSuddenDeathAnnouncements

Ensure sudden-death respawn messaging is delivered via center-print prompts.
=============
*/
static void G_TrackSuddenDeathAnnouncements( void ) {
	const matchFactoryConfig_t *config = &g_matchFactoryConfig;

	if ( !level.overtimeActive ) {
		return;
	}
	if ( g_suddenDeathRespawn.integer <= 0 || !config->suddenDeathRespawnsEnabled ) {
		if ( !level.suddenDeathNoRespawnLogged ) {
			level.suddenDeathNoRespawnLogged = qtrue;
			level.suddenDeathLastDelay = -1;
			G_LogPrintf( "match: sudden-death respawns disabled\n" );
			if ( config->suddenDeathPrintAnnouncements ) {
				trap_SendServerCommand( -1, "cp \"Sudden-death respawns disabled\n\"" );
			}
		}
		return;
	}
	int delay = G_GetSuddenDeathRespawnDelay();
	if ( delay < 0 ) {
		delay = 0;
	}
	if ( level.suddenDeathLastDelay != delay ) {
		level.suddenDeathLastDelay = delay;
		level.suddenDeathNoRespawnLogged = qfalse;
		G_LogPrintf( "match: sudden-death respawn delay %i ms\n", delay );
		if ( config->suddenDeathPrintAnnouncements ) {
			if ( delay > 0 ) {
				trap_SendServerCommand( -1, va( "cp \"Sudden-death respawns available in %i seconds\n\"", delay / 1000 ) );
			} else {
				trap_SendServerCommand( -1, "cp \"Sudden-death respawns available now\n\"" );
			}
		}
	}
}


static void LevelCheckTimers( void ) {
	int team;
	matchFactoryConfig_t previousConfig = matchFlow_lastConfig;
	const matchFactoryConfig_t *config = &g_matchFactoryConfig;

	if ( previousConfig.timeoutCountPerTeam != config->timeoutCountPerTeam ) {
		for ( team = TEAM_FREE; team < TEAM_NUM_TEAMS; team++ ) {
			level.timeoutRemaining[team] = config->timeoutCountPerTeam;
		}
		G_UpdateMatchStateConfigString();
	}
	if ( previousConfig.overtimeLengthSeconds != config->overtimeLengthSeconds ) {
		if ( level.overtimeActive ) {
			if ( config->overtimeLengthSeconds > 0 ) {
				level.overtimeEndTime = level.time + config->overtimeLengthSeconds * 1000;
			} else {
				level.overtimeEndTime = 0;
			}
			G_UpdateMatchStateConfigString();
		}
	}
	if ( previousConfig.suddenDeathRespawnsEnabled != config->suddenDeathRespawnsEnabled ||
		previousConfig.suddenDeathStartSeconds != config->suddenDeathStartSeconds ||
		previousConfig.suddenDeathTickSeconds != config->suddenDeathTickSeconds ||
		previousConfig.suddenDeathMaxSeconds != config->suddenDeathMaxSeconds ||
		previousConfig.suddenDeathIncrementSeconds != config->suddenDeathIncrementSeconds ) {
		level.suddenDeathLastDelay = -1;
		level.suddenDeathNoRespawnLogged = qfalse;
	}

	matchFlow_lastConfig = *config;

	G_AutoShuffleCountdown_Frame();

	if ( level.timeoutActive ) {
		if ( level.timeoutExpireTime && level.time >= level.timeoutExpireTime ) {
			int pausedDuration = 0;
			team_t team = level.timeoutTeam;
			int owner = level.timeoutOwner;

			if ( level.timeoutStartTime > 0 && level.time > level.timeoutStartTime ) {
				pausedDuration = level.time - level.timeoutStartTime;
			}

			G_ApplyTimeoutPauseDelta( pausedDuration );

			trap_SendServerCommand( -1, "print \"Timeout expired; match resuming.\\n\"" );
			G_LogPrintf( "match: timeout expired team %i owner %i\n", team, owner );

			level.timeoutActive = qfalse;
			level.timeoutOwner = -1;
			level.timeoutTeam = TEAM_FREE;
			level.timeoutExpireTime = 0;
			level.timeoutStartTime = 0;

			G_UpdateMatchStateConfigString();
		}
		return;
	}
	if ( g_timelimit.integer && !level.warmupTime ) {
		const int limitMillis = g_timelimit.integer * 60000;
		if ( level.time - level.startTime >= limitMillis ) {
			if ( ScoreIsTied() ) {
				G_StartOrExtendOvertime();
			} else if ( level.overtimeActive ) {
				G_StopOvertime();
			}
		}
	}
	if ( level.overtimeActive ) {
		if ( level.overtimeEndTime > 0 && level.time >= level.overtimeEndTime && ScoreIsTied() ) {
			G_StartOrExtendOvertime();
		}
		if ( !ScoreIsTied() && ( level.overtimeEndTime == 0 || level.time >= level.overtimeStartTime ) ) {
			G_StopOvertime();
		}
		G_TrackSuddenDeathAnnouncements();
	} else {
		level.suddenDeathLastDelay = -1;
		level.suddenDeathNoRespawnLogged = qfalse;
	}
}

/*
========================================================================

FUNCTIONS CALLED EVERY FRAME

========================================================================
*/


/*
=============
CheckTournament

Once a frame, check for changes in tournement player state
=============
*/
void CheckTournament( void ) {
	// check because we run 3 game frames before calling Connect and/or ClientBegin
	// for clients on a map_restart
	if ( level.numPlayingClients == 0 ) {
		return;
	}

	if ( level.trainingMapActive ) {
		if ( level.warmupTime != 0 ) {
			level.warmupTime = 0;
			trap_SetConfigstring( CS_WARMUP, "" );
		}
		return;
	}

	if ( level.timeoutActive ) {
		return;
	}

	if ( g_gametype.integer == GT_TOURNAMENT ) {

		// pull in a spectator if needed
		if ( level.numPlayingClients < 2 ) {
			AddTournamentPlayer();
		}

		// if we don't have two players, go back to "waiting for players"
		if ( level.numPlayingClients != 2 ) {
			if ( level.warmupTime != -1 ) {
				level.warmupTime = -1;
				trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
				G_LogPrintf( "Warmup:\n" );
			}
			return;
		}

		if ( level.warmupTime == 0 ) {
			return;
		}

		// if the warmup is changed at the console, restart it
		if ( g_warmup.modificationCount != level.warmupModificationCount ) {
			level.warmupModificationCount = g_warmup.modificationCount;
			level.warmupTime = -1;
			G_InitWeaponConfig();
		}

		// if all players have arrived, start the countdown
		if ( level.warmupTime < 0 ) {
			if ( level.numPlayingClients == 2 ) {
				// fudge by -1 to account for extra delays
				level.warmupTime = level.time + ( g_warmup.integer - 1 ) * 1000;
				trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
			}
			return;
		}

		// if the warmup time has counted down, restart
		if ( level.time > level.warmupTime ) {
			level.warmupTime += 10000;
			trap_Cvar_Set( "g_restarted", "1" );
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			level.restarted = qtrue;
			return;
		}
	} else if ( g_gametype.integer != GT_SINGLE_PLAYER && level.warmupTime != 0 ) {
		int		counts[TEAM_NUM_TEAMS];
		qboolean	notEnough = qfalse;

		if ( g_gametype.integer > GT_TEAM ) {
			counts[TEAM_BLUE] = TeamCount( -1, TEAM_BLUE );
			counts[TEAM_RED] = TeamCount( -1, TEAM_RED );

			if (counts[TEAM_RED] < 1 || counts[TEAM_BLUE] < 1) {
				notEnough = qtrue;
			}
		} else if ( level.numPlayingClients < 2 ) {
			notEnough = qtrue;
		}

		if ( notEnough ) {
			if ( level.warmupTime != -1 ) {
				level.warmupTime = -1;
				trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
				G_LogPrintf( "Warmup:\n" );
			}
			return; // still waiting for team members
		}

		if ( level.warmupTime == 0 ) {
			return;
		}

		// if the warmup is changed at the console, restart it
		if ( g_warmup.modificationCount != level.warmupModificationCount ) {
			level.warmupModificationCount = g_warmup.modificationCount;
			level.warmupTime = -1;
			G_InitWeaponConfig();
		}

		// if all players have arrived, start the countdown
		if ( level.warmupTime < 0 ) {
			// fudge by -1 to account for extra delays
			level.warmupTime = level.time + ( g_warmup.integer - 1 ) * 1000;
			trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
			return;
		}

		// if the warmup time has counted down, restart
		if ( level.time > level.warmupTime ) {
			level.warmupTime += 10000;
			trap_Cvar_Set( "g_restarted", "1" );
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			level.restarted = qtrue;
			return;
		}
	}
}


/*
==================
CheckVote
==================
*/
void CheckVote( void ) {
	if ( level.voteExecuteTime && level.voteExecuteTime < level.time ) {
		level.voteExecuteTime = 0;
		trap_SendConsoleCommand( EXEC_APPEND, va("%s\n", level.voteString ) );
	}
	if ( !level.voteTime ) {
		return;
	}
	if ( level.time - level.voteTime >= VOTE_TIME ) {
		trap_SendServerCommand( -1, "print \"Vote failed.\n\"" );
	} else {
		// ATVI Q3 1.32 Patch #9, WNF
		if ( level.voteYes > level.numVotingClients/2 ) {
			// execute the command, then remove the vote
			trap_SendServerCommand( -1, "print \"Vote passed.\n\"" );
			level.voteExecuteTime = level.time + 3000;
		} else if ( level.voteNo >= level.numVotingClients/2 ) {
			// same behavior as a timeout
			trap_SendServerCommand( -1, "print \"Vote failed.\n\"" );
		} else {
			// still waiting for a majority
			return;
		}
	}
	level.voteTime = 0;
	trap_SetConfigstring( CS_VOTE_TIME, "" );

}

/*
==================
PrintTeam
==================
*/
void PrintTeam(int team, char *message) {
	int i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		trap_SendServerCommand( i, message );
	}
}

/*
==================
SetLeader
==================
*/
void SetLeader(int team, int client) {
	int i;

	if ( level.clients[client].pers.connected == CON_DISCONNECTED ) {
		PrintTeam(team, va("print \"%s is not connected\n\"", level.clients[client].pers.netname) );
		return;
	}
	if (level.clients[client].sess.sessionTeam != team) {
		PrintTeam(team, va("print \"%s is not on the team anymore\n\"", level.clients[client].pers.netname) );
		return;
	}
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		if (level.clients[i].sess.teamLeader) {
			level.clients[i].sess.teamLeader = qfalse;
			ClientUserinfoChanged(i);
		}
	}
	level.clients[client].sess.teamLeader = qtrue;
	ClientUserinfoChanged( client );
	PrintTeam(team, va("print \"%s is the new team leader\n\"", level.clients[client].pers.netname) );
}

/*
==================
CheckTeamLeader
==================
*/
void CheckTeamLeader( int team ) {
	int i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		if (level.clients[i].sess.teamLeader)
			break;
	}
	if (i >= level.maxclients) {
		for ( i = 0 ; i < level.maxclients ; i++ ) {
			if (level.clients[i].sess.sessionTeam != team)
				continue;
			if (!(g_entities[i].r.svFlags & SVF_BOT)) {
				level.clients[i].sess.teamLeader = qtrue;
				break;
			}
		}
		for ( i = 0 ; i < level.maxclients ; i++ ) {
			if (level.clients[i].sess.sessionTeam != team)
				continue;
			level.clients[i].sess.teamLeader = qtrue;
			break;
		}
	}
}

/*
==================
CheckTeamVote
==================
*/
void CheckTeamVote( int team ) {
	int cs_offset;

	if ( team == TEAM_RED )
		cs_offset = 0;
	else if ( team == TEAM_BLUE )
		cs_offset = 1;
	else
		return;

	if ( !level.teamVoteTime[cs_offset] ) {
		return;
	}
	if ( level.time - level.teamVoteTime[cs_offset] >= VOTE_TIME ) {
		trap_SendServerCommand( -1, "print \"Team vote failed.\n\"" );
	} else {
		if ( level.teamVoteYes[cs_offset] > level.numteamVotingClients[cs_offset]/2 ) {
			// execute the command, then remove the vote
			trap_SendServerCommand( -1, "print \"Team vote passed.\n\"" );
			//
			if ( !Q_strncmp( "leader", level.teamVoteString[cs_offset], 6) ) {
				//set the team leader
				SetLeader(team, atoi(level.teamVoteString[cs_offset] + 7));
			}
			else {
				trap_SendConsoleCommand( EXEC_APPEND, va("%s\n", level.teamVoteString[cs_offset] ) );
			}
		} else if ( level.teamVoteNo[cs_offset] >= level.numteamVotingClients[cs_offset]/2 ) {
			// same behavior as a timeout
			trap_SendServerCommand( -1, "print \"Team vote failed.\n\"" );
		} else {
			// still waiting for a majority
			return;
		}
	}
	level.teamVoteTime[cs_offset] = 0;
	trap_SetConfigstring( CS_TEAMVOTE_TIME + cs_offset, "" );

}


/*
==================
CheckCvars
==================
*/
void CheckCvars( void ) {
	static int lastMod = -1;

	if ( g_password.modificationCount != lastMod ) {
		lastMod = g_password.modificationCount;
		if ( *g_password.string && Q_stricmp( g_password.string, "none" ) ) {
			trap_Cvar_Set( "g_needpass", "1" );
		} else {
			trap_Cvar_Set( "g_needpass", "0" );
		}
	}
}

static qlr_game_frame_context_t *G_GetFrameContext( void ) {
	if ( !g_qlr_frame_ctx ) {
		return NULL;
	}

	g_qlr_frame_ctx->level = ( qlr_level_locals_t * )&level;
	g_qlr_frame_ctx->entities = ( qlr_gentity_t * )g_entities;
	g_qlr_frame_ctx->entity_count = level.num_entities;

	return g_qlr_frame_ctx;
}

static void G_DispatchScheduledThinks( qlr_game_frame_context_t *ctx, int msec ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.num_entities; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		if ( ent->freeAfterEvent ) {
			continue;
		}

		if ( !ent->r.linked && ent->neverFree ) {
			continue;
		}

	// get any cvar changes
	G_UpdateCvars();
	LevelCheckTimers();
		if ( i < MAX_CLIENTS ) {
			continue;
		}

		if ( ent->s.eType == ET_MISSILE ) {
			continue;
		}

		if ( ent->s.eType == ET_ITEM || ent->physicsObject ) {
			continue;
		}

		if ( ent->s.eType == ET_MOVER ) {
			continue;
		}

		G_RunThink( ent );
	}

	if ( ctx && ctx->hooks.run_scheduled_thinks ) {
		ctx->hooks.run_scheduled_thinks( msec );
	}
}

static void G_StepEntities( qlr_game_frame_context_t *ctx ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.num_entities; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		if ( ent->freeAfterEvent ) {
			continue;
		}

		if ( !ent->r.linked && ent->neverFree ) {
			continue;
		}

		if ( ent->s.eType == ET_MISSILE ) {
			G_RunMissile( ent );

			if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
				ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
			}
			continue;
		}

		if ( ent->s.eType == ET_ITEM || ent->physicsObject ) {
			G_RunItem( ent );

			if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
				ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
			}
			continue;
		}

		if ( ent->s.eType == ET_MOVER ) {
			G_RunMover( ent );

			if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
				ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
			}
			continue;
		}

		if ( i < MAX_CLIENTS ) {
			G_RunClient( ent );

			if ( ctx ) {
				if ( ctx->hooks.physics_step && ent->inuse ) {
					ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
				}

				if ( ctx->hooks.client_think && ent->inuse && ent->client ) {
					ctx->hooks.client_think( ( qlr_gentity_t * )ent );
				}
			}
			continue;
		}

		if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
			ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
		}
	}
}

static void G_DispatchEvents( qlr_game_frame_context_t *ctx ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.num_entities; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		if ( ctx && ctx->hooks.fire_event && ent->s.event &&
			ent->eventTime > level.previousTime && ent->eventTime <= level.time ) {
			ctx->hooks.fire_event( ( qlr_gentity_t * )ent );
		}

		if ( level.time - ent->eventTime > EVENT_VALID_MSEC ) {
			if ( ent->s.event ) {
				ent->s.event = 0;       // &= EV_EVENT_BITS;
				if ( ent->client ) {
					ent->client->ps.externalEvent = 0;
					// predicted events should never be set to zero
					//ent->client->ps.events[0] = 0;
					//ent->client->ps.events[1] = 0;
				}
			}

			if ( ent->freeAfterEvent ) {
				G_FreeEntity( ent );
				continue;
			} else if ( ent->unlinkAfterEvent ) {
				ent->unlinkAfterEvent = qfalse;
				trap_UnlinkEntity( ent );
			}
		}
	}
}

static void G_FinishClientFrames( qlr_game_frame_context_t *ctx ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.maxclients; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		ClientEndFrame( ent );

		if ( ctx && ctx->hooks.client_end_frame && ent->client ) {
			ctx->hooks.client_end_frame( ( qlr_gentity_t * )ent );
		}
	}
}

static void G_CheckLevelTimers( qlr_game_frame_context_t *ctx, int previousWarmupTime, int previousIntermissionQueued ) {
        CheckTournament();
        CheckExitRules();
        CheckTeamStatus();
        CheckVote();
        CheckTeamVote( TEAM_RED );
        CheckTeamVote( TEAM_BLUE );
        CheckCvars();

        if ( !ctx ) {
                return;
        }

        if ( ctx->hooks.begin_match && previousWarmupTime > 0 && level.warmupTime <= 0 ) {
                ctx->hooks.begin_match();
        }

        if ( ctx->hooks.begin_intermission && previousIntermissionQueued == 0 && level.intermissionQueued != 0 ) {
                ctx->hooks.begin_intermission();
        }
}

/*
=============
G_RunThink

Runs thinking code for this frame if necessary
=============
*/
void G_RunThink (gentity_t *ent) {
	float	thinktime;

	thinktime = ent->nextthink;
	if (thinktime <= 0) {
		return;
	}
	if (thinktime > level.time) {
		return;
	}
	
	ent->nextthink = 0;
	if (!ent->think) {
		G_Error ( "NULL ent->think");
	}
	ent->think (ent);
}

/*
=============
G_QuadHogReset

Clears the Quad Hog tracking state on the server.
=============
*/
static void G_QuadHogReset( void ) {
	level.quadHogOwner = ENTITYNUM_NONE;
	level.quadHogExpireTime = 0;
	level.quadHogLastActiveTime = 0;
	level.quadHogNextPingTime = 0;
}

/*
=============
G_QuadHogRemove

Revokes the Quad powerup from the current Quad Hog carrier.
=============
*/
static void G_QuadHogRemove( gentity_t *owner, const char *reason ) {
	if ( owner && owner->client ) {
		owner->client->ps.powerups[PW_QUAD] = 0;
		if ( reason && reason[0] ) {
			trap_SendServerCommand( owner->s.number, va( "print \"%s\n\"", reason ) );
		}
	}

	G_QuadHogReset();
}

/*
=============
G_QuadHogOnPickup

Initialises Quad Hog timers when a player claims the Quad.
=============
*/
void G_QuadHogOnPickup( gentity_t *player ) {
	if ( !level.quadHogEnabled ) {
		G_QuadHogReset();
		return;
	}

	if ( !player || !player->client ) {
		G_QuadHogReset();
		return;
	}

	level.quadHogOwner = player->s.number;
	level.quadHogLastActiveTime = level.time;
	if ( g_weaponConfig.quadHogTimeSeconds > 0 ) {
		level.quadHogExpireTime = level.time + g_weaponConfig.quadHogTimeSeconds * 1000;
	} else {
		level.quadHogExpireTime = 0;
	}
	if ( g_weaponConfig.quadHogPingRateSeconds > 0 ) {
		level.quadHogNextPingTime = level.time + g_weaponConfig.quadHogPingRateSeconds * 1000;
	} else {
		level.quadHogNextPingTime = 0;
	}
}

/*
=============
G_QuadHogFrame

Processes Quad Hog timers each server frame.
=============
*/
void G_QuadHogFrame( void ) {
	gentity_t	*owner;
	qboolean	active = qfalse;

	if ( !level.quadHogEnabled ) {
		G_QuadHogReset();
		return;
	}

	if ( level.quadHogOwner < 0 || level.quadHogOwner >= level.maxclients ) {
		G_QuadHogReset();
		return;
	}

	owner = &g_entities[level.quadHogOwner];
	if ( !owner->inuse || !owner->client ) {
		G_QuadHogReset();
		return;
	}

	if ( owner->client->ps.powerups[PW_QUAD] <= level.time ) {
		G_QuadHogReset();
		return;
	}

	if ( g_weaponConfig.quadHogTimeSeconds > 0 && level.quadHogExpireTime > 0 && level.time >= level.quadHogExpireTime ) {
		G_QuadHogRemove( owner, "Quad Hog: timer expired!" );
		return;
	}

	if ( owner->client->pers.cmd.forwardmove || owner->client->pers.cmd.rightmove || owner->client->pers.cmd.upmove ) {
		active = qtrue;
	}
	if ( owner->client->pers.cmd.buttons & BUTTON_ATTACK ) {
		active = qtrue;
	}
	if ( !active ) {
		vec3_t	velocity;

		VectorCopy( owner->client->ps.velocity, velocity );
		if ( VectorLengthSquared( velocity ) > 1.0f ) {
			active = qtrue;
		}
	}

	if ( active ) {
		level.quadHogLastActiveTime = level.time;
	} else if ( g_weaponConfig.quadHogIdleSeconds > 0 ) {
		int	idleLimit = g_weaponConfig.quadHogIdleSeconds * 1000;
		if ( level.time - level.quadHogLastActiveTime >= idleLimit ) {
			G_QuadHogRemove( owner, "Quad Hog: idle penalty!" );
			return;
		}
	}

	if ( g_weaponConfig.quadHogPingRateSeconds > 0 ) {
		if ( level.quadHogNextPingTime == 0 ) {
			level.quadHogNextPingTime = level.time + g_weaponConfig.quadHogPingRateSeconds * 1000;
		} else if ( level.time >= level.quadHogNextPingTime ) {
			int	remainingMs = 0;

			if ( g_weaponConfig.quadHogTimeSeconds > 0 && level.quadHogExpireTime > 0 ) {
				remainingMs = level.quadHogExpireTime - level.time;
				if ( remainingMs < 0 ) {
					remainingMs = 0;
				}
			}

			trap_SendServerCommand( owner->s.number, va( "print \"Quad Hog: %d seconds remaining\\n\"", remainingMs / 1000 ) );
			level.quadHogNextPingTime = level.time + g_weaponConfig.quadHogPingRateSeconds * 1000;
		}
	}
}

/*
=============
G_RunFrame

Advance the game simulation by one frame.
=============
*/
void G_RunFrame( int levelTime ) {
	int		msec;
	int		previousWarmupTime;
	int		previousIntermissionQueued;
	qlr_game_frame_context_t	*ctx;

	if ( level.restarted ) {
		return;
	}

	msec = levelTime - level.time;
	if ( msec < 0 ) {
		msec = 0;
	}

	previousWarmupTime = level.warmupTime;
	previousIntermissionQueued = level.intermissionQueued;

	level.previousTime = level.time;
	level.time = levelTime;
	level.msec = msec;
	level.framenum++;

	ctx = G_GetFrameContext();

	G_UpdateCvars();
	G_RefreshPmoveSettings();

	G_DispatchScheduledThinks( ctx, msec );
	G_StepEntities( ctx );
	G_DispatchEvents( ctx );
	Team_RunDomination();
	G_QuadHogFrame();
	G_FinishClientFrames( ctx );
	G_UpdateVoteThrottle();
	G_Frame_UpdateRoundController();
	G_CheckLevelTimers( ctx, previousWarmupTime, previousIntermissionQueued );

	if ( g_listEntity.integer ) {
		int		i;

		for ( i = 0; i < MAX_GENTITIES; i++ ) {
			G_Printf( "%4i: %s\n", i, g_entities[i].classname );
		}
		trap_Cvar_Set( "g_listEntity", "0" );
	}
}


/*
=============
G_UpdateGametypeTutorialText

Publishes Domination and Freeze Tag tutorial strings so clients see coaching tips.
=============
*/
static void G_UpdateGametypeTutorialText( void ) {
	trap_SetConfigstring( CS_FREEZE_TIP_OBJECTIVE, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_THAW, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_FREEZE, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_SHOOT, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_SUMMARY, "" );

	if ( g_gametype.integer == GT_DOMINATION ) {
		trap_SetConfigstring( CS_TUTORIAL_NAME, "Domination" );
		trap_SetConfigstring( CS_TUTORIAL_TEXT, "Capture domination points to earn points for your team." );
		return;
	}

	if ( g_gametype.integer == GT_FREEZE ) {
		trap_SetConfigstring( CS_TUTORIAL_NAME, "Freeze Tag" );
		trap_SetConfigstring( CS_TUTORIAL_TEXT, "Freeze all enemy team members to score a team point." );
		trap_SetConfigstring( CS_FREEZE_TIP_OBJECTIVE, "Freeze all enemy team members to score a team point." );
		trap_SetConfigstring( CS_FREEZE_TIP_THAW, "Stand by frozen teammates for 3 seconds to thaw them." );
		trap_SetConfigstring( CS_FREEZE_TIP_FREEZE, "Fragging another player freezes them." );
		trap_SetConfigstring( CS_FREEZE_TIP_SHOOT, "Shoot everyone on the other team!" );
		trap_SetConfigstring( CS_FREEZE_TIP_SUMMARY, "This is a Freeze Tag game" );
		return;
	}

	trap_SetConfigstring( CS_TUTORIAL_NAME, "" );
	trap_SetConfigstring( CS_TUTORIAL_TEXT, "" );
}
