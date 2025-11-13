#include "../code/game/g_local.h"
#include "g_match_config.h"

#define DEFAULT_TIMEOUT_LENGTH_SECONDS			60
#define DEFAULT_TIMEOUT_COUNT_PER_TEAM			0
#define DEFAULT_OVERTIME_LENGTH_SECONDS		120
#define DEFAULT_SUDDEN_DEATH_RESPAWN			0
#define DEFAULT_SUDDEN_DEATH_START_SECONDS		3
#define DEFAULT_SUDDEN_DEATH_TICK_SECONDS		60
#define DEFAULT_SUDDEN_DEATH_MAX_SECONDS		10
#define DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS	1
#define DEFAULT_SUDDEN_DEATH_PRINT			1

matchFactoryConfig_t g_matchFactoryConfig;

static matchFactoryConfig_t s_reportedMatchFactoryConfig;

/*
=============
G_MatchConfig_ReportMissingCvar

Logs when a match factory CVar is unavailable so administrators can diagnose config issues.
=============
*/
static void G_MatchConfig_ReportMissingCvar( const char *cvarName ) {
	if ( !cvarName || !cvarName[0] ) {
		return;
	}

	G_Printf( "WARNING: match config cvar %s is unavailable; using fallback value\n", cvarName );
}

/*
=============
G_MatchConfig_ReadIntCvar

Reads a match factory integer CVar, falling back when it is missing.
=============
*/
static int G_MatchConfig_ReadIntCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_MatchConfig_ReportMissingCvar( cvarName );
		return fallback;
	}

	return cvar->integer;
}

/*
=============
G_MatchConfig_ReadNonNegativeCvar

Clamps match factory CVars that must remain non-negative.
=============
*/
static int G_MatchConfig_ReadNonNegativeCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	int value = G_MatchConfig_ReadIntCvar( cvar, fallback, cvarName );

	if ( value < 0 ) {
		G_Printf( "WARNING: match config cvar %s must be non-negative; using fallback value %i\n", cvarName, fallback );
		return fallback;
	}

	return value;
}

/*
=============
G_MatchConfig_ReadPositiveCvar

Clamps match factory CVars that must stay positive.
=============
*/
static int G_MatchConfig_ReadPositiveCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	int value = G_MatchConfig_ReadIntCvar( cvar, fallback, cvarName );

	if ( value <= 0 ) {
		G_Printf( "WARNING: match config cvar %s must be positive; using fallback value %i\n", cvarName, fallback );
		return fallback;
	}

	return value;
}

/*
=============
G_MatchConfig_ReadBoolCvar

Converts match factory CVars to qboolean flags.
=============
*/
static qboolean G_MatchConfig_ReadBoolCvar( const vmCvar_t *cvar, qboolean fallback, const char *cvarName ) {
	int value = G_MatchConfig_ReadIntCvar( cvar, fallback ? 1 : 0, cvarName );

	return value ? qtrue : qfalse;
}

/*
=============
G_MatchConfig_Load

Collects the active match factory CVars into a cached snapshot for gameplay use.
=============
*/
static matchFactoryConfig_t G_MatchConfig_Load( void ) {
	matchFactoryConfig_t config;

	config.timeoutLengthSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_timeoutLen, DEFAULT_TIMEOUT_LENGTH_SECONDS, "g_timeoutLen" );
	config.timeoutCountPerTeam = G_MatchConfig_ReadNonNegativeCvar( &g_timeoutCount, DEFAULT_TIMEOUT_COUNT_PER_TEAM, "g_timeoutCount" );
	config.overtimeLengthSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_overtime, DEFAULT_OVERTIME_LENGTH_SECONDS, "g_overtime" );
	config.suddenDeathRespawnsEnabled = G_MatchConfig_ReadBoolCvar( &g_suddenDeathRespawn, DEFAULT_SUDDEN_DEATH_RESPAWN ? qtrue : qfalse, "g_suddenDeathRespawn" );
	config.suddenDeathStartSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_suddenDeathRespawnStart, DEFAULT_SUDDEN_DEATH_START_SECONDS, "g_suddenDeathRespawnStart" );
	config.suddenDeathTickSeconds = G_MatchConfig_ReadPositiveCvar( &g_suddenDeathRespawnTick, DEFAULT_SUDDEN_DEATH_TICK_SECONDS, "g_suddenDeathRespawnTick" );
	config.suddenDeathMaxSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_suddenDeathRespawnMax, DEFAULT_SUDDEN_DEATH_MAX_SECONDS, "g_suddenDeathRespawnMax" );
	if ( config.suddenDeathMaxSeconds < config.suddenDeathStartSeconds ) {
		config.suddenDeathMaxSeconds = config.suddenDeathStartSeconds;
	}
	config.suddenDeathIncrementSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_suddenDeathRespawnIncrement, DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS, "g_suddenDeathRespawnIncrement" );
	config.suddenDeathPrintAnnouncements = G_MatchConfig_ReadBoolCvar( &g_suddenDeathRespawnPrint, DEFAULT_SUDDEN_DEATH_PRINT ? qtrue : qfalse, "g_suddenDeathRespawnPrint" );
	config.suddenDeathSpawnDelayActive = ( config.suddenDeathRespawnsEnabled && ( config.suddenDeathStartSeconds > 0 || config.suddenDeathIncrementSeconds > 0 ) ) ? qtrue : qfalse;

	return config;
}

/*
=============
G_LogMatchFactoryConfig

Logs the active match factory snapshot for admin visibility.
=============
*/
static void G_LogMatchFactoryConfig( const char *reason, const matchFactoryConfig_t *config ) {
	if ( !reason || !config ) {
		return;
	}

	G_Printf( "Match factory config (%s): timeoutLen=%i timeoutCount=%i overtime=%i suddenRespawn=%i start=%i tick=%i max=%i increment=%i print=%i delay=%i\n",
		reason,
		config->timeoutLengthSeconds,
		config->timeoutCountPerTeam,
		config->overtimeLengthSeconds,
		config->suddenDeathRespawnsEnabled ? 1 : 0,
		config->suddenDeathStartSeconds,
		config->suddenDeathTickSeconds,
		config->suddenDeathMaxSeconds,
		config->suddenDeathIncrementSeconds,
		config->suddenDeathPrintAnnouncements ? 1 : 0,
		config->suddenDeathSpawnDelayActive ? 1 : 0 );
}

/*
=============
G_InitMatchFactoryConfig

Initialises the cached match factory configuration during VM startup.
=============
*/
void G_InitMatchFactoryConfig( void ) {
	g_matchFactoryConfig = G_MatchConfig_Load();
	s_reportedMatchFactoryConfig = g_matchFactoryConfig;
	G_LogMatchFactoryConfig( "init", &g_matchFactoryConfig );
}

/*
=============
G_UpdateMatchFactoryConfig

Refreshes the cached match factory configuration and emits transition logs when CVars change.
=============
*/
void G_UpdateMatchFactoryConfig( void ) {
	matchFactoryConfig_t config = G_MatchConfig_Load();

	if ( config.timeoutLengthSeconds != s_reportedMatchFactoryConfig.timeoutLengthSeconds
		|| config.timeoutCountPerTeam != s_reportedMatchFactoryConfig.timeoutCountPerTeam
		|| config.overtimeLengthSeconds != s_reportedMatchFactoryConfig.overtimeLengthSeconds
		|| config.suddenDeathRespawnsEnabled != s_reportedMatchFactoryConfig.suddenDeathRespawnsEnabled
		|| config.suddenDeathStartSeconds != s_reportedMatchFactoryConfig.suddenDeathStartSeconds
		|| config.suddenDeathTickSeconds != s_reportedMatchFactoryConfig.suddenDeathTickSeconds
		|| config.suddenDeathMaxSeconds != s_reportedMatchFactoryConfig.suddenDeathMaxSeconds
		|| config.suddenDeathIncrementSeconds != s_reportedMatchFactoryConfig.suddenDeathIncrementSeconds
		|| config.suddenDeathPrintAnnouncements != s_reportedMatchFactoryConfig.suddenDeathPrintAnnouncements
		|| config.suddenDeathSpawnDelayActive != s_reportedMatchFactoryConfig.suddenDeathSpawnDelayActive ) {
		G_LogMatchFactoryConfig( "update", &config );
		s_reportedMatchFactoryConfig = config;
	}

	g_matchFactoryConfig = config;
}
