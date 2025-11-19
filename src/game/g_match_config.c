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
#define DEFAULT_FACTORY_RESPAWN_DELAY_MILLISECONDS		0
#define DEFAULT_FACTORY_WARMUP_DELAY_MILLISECONDS	0
#define DEFAULT_FACTORY_ALLOW_ITEM_DROPS		1
#define DEFAULT_FACTORY_ALLOW_ITEM_BOUNCE		1

matchFactoryConfig_t g_matchFactoryConfig;

static matchFactoryConfig_t s_reportedMatchFactoryConfig;

/*
=============
G_MatchConfig_CopyTrimmedFactoryTitle

Copies the g_factoryTitle CVar into the provided buffer after trimming whitespace.
=============
*/
static qboolean G_MatchConfig_CopyTrimmedFactoryTitle( char *buffer, int bufferSize ) {
	const char	*source;
	int			start;
	int			end;
	int			length;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	trap_Cvar_Update( &g_factoryTitle );
	source = g_factoryTitle.string;
	if ( !source ) {
		buffer[0] = '\0';
		return qfalse;
	}

	start = 0;
	while ( source[start] && (unsigned char)source[start] <= ' ' ) {
		start++;
	}

	end = (int)strlen( source );
	while ( end > start && (unsigned char)source[end - 1] <= ' ' ) {
		end--;
	}

	length = end - start;
	if ( length <= 0 ) {
		buffer[0] = '\0';
		return qfalse;
	}

	if ( length >= bufferSize ) {
		length = bufferSize - 1;
	}

	memcpy( buffer, source + start, (size_t)length );
	buffer[length] = '\0';
return qtrue;
}

/*
=============
G_MatchConfig_BuildMetadataStrings

Prepares the human-readable factory metadata strings that are sent through configstrings.
=============
*/
static void G_MatchConfig_BuildMetadataStrings( char *title, int titleSize, char *flags, int flagsSize, char *spawnHints, int spawnHintsSize ) {
	const matchFactoryConfig_t	*config;
	unsigned int			mask;
	qboolean				defaultSpawnDelayActive;
	char				info[MAX_INFO_STRING];
	char				buffer[32];
	char				trimmedTitle[MAX_CVAR_VALUE_STRING];
	qboolean				customTitle;

	if ( !title || titleSize <= 0 || !flags || flagsSize <= 0 || !spawnHints || spawnHintsSize <= 0 ) {
		return;
	}

	config = &g_matchFactoryConfig;
	mask = 0u;

	if ( config->timeoutLengthSeconds != DEFAULT_TIMEOUT_LENGTH_SECONDS ) {
		mask |= FACTORY_FLAG_TIMEOUT_LENGTH;
	}
	if ( config->timeoutCountPerTeam != DEFAULT_TIMEOUT_COUNT_PER_TEAM ) {
		mask |= FACTORY_FLAG_TIMEOUT_COUNT;
	}
	if ( config->overtimeLengthSeconds != DEFAULT_OVERTIME_LENGTH_SECONDS ) {
		mask |= FACTORY_FLAG_OVERTIME_LENGTH;
	}
	if ( ( config->suddenDeathRespawnsEnabled ? qtrue : qfalse ) != ( DEFAULT_SUDDEN_DEATH_RESPAWN ? qtrue : qfalse ) ) {
		mask |= FACTORY_FLAG_SUDDEN_DEATH_ENABLED;
	}
	if ( config->suddenDeathStartSeconds != DEFAULT_SUDDEN_DEATH_START_SECONDS ) {
		mask |= FACTORY_FLAG_SUDDEN_DEATH_START;
	}
	if ( config->suddenDeathTickSeconds != DEFAULT_SUDDEN_DEATH_TICK_SECONDS ) {
		mask |= FACTORY_FLAG_SUDDEN_DEATH_TICK;
	}
	if ( config->suddenDeathMaxSeconds != DEFAULT_SUDDEN_DEATH_MAX_SECONDS ) {
		mask |= FACTORY_FLAG_SUDDEN_DEATH_MAX;
	}
	if ( config->suddenDeathIncrementSeconds != DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS ) {
		mask |= FACTORY_FLAG_SUDDEN_DEATH_INCREMENT;
	}
	if ( ( config->suddenDeathPrintAnnouncements ? qtrue : qfalse ) != ( DEFAULT_SUDDEN_DEATH_PRINT ? qtrue : qfalse ) ) {
		mask |= FACTORY_FLAG_SUDDEN_DEATH_PRINT;
	}
	defaultSpawnDelayActive = ( DEFAULT_SUDDEN_DEATH_RESPAWN && ( DEFAULT_SUDDEN_DEATH_START_SECONDS > 0 || DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS > 0 ) ) ? qtrue : qfalse;
	if ( config->suddenDeathSpawnDelayActive != defaultSpawnDelayActive ) {
		mask |= FACTORY_FLAG_SUDDEN_DEATH_DELAY;
	}

	customTitle = G_MatchConfig_CopyTrimmedFactoryTitle( trimmedTitle, sizeof( trimmedTitle ) );
	if ( customTitle ) {
		Q_strncpyz( title, trimmedTitle, titleSize );
	} else if ( mask == 0u ) {
		Q_strncpyz( title, "Standard Factory", titleSize );
	} else {
		Q_strncpyz( title, "Custom Factory", titleSize );
	}

	Com_sprintf( flags, flagsSize, "%u", mask );

	info[0] = '\0';

	Com_sprintf( buffer, sizeof( buffer ), "%i", config->timeoutCountPerTeam );
	Info_SetValueForKey( info, "toCount", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->timeoutLengthSeconds );
	Info_SetValueForKey( info, "toLength", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->overtimeLengthSeconds );
	Info_SetValueForKey( info, "otLength", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->suddenDeathRespawnsEnabled ? 1 : 0 );
	Info_SetValueForKey( info, "sd", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->suddenDeathStartSeconds );
	Info_SetValueForKey( info, "sdStart", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->suddenDeathTickSeconds );
	Info_SetValueForKey( info, "sdTick", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->suddenDeathMaxSeconds );
	Info_SetValueForKey( info, "sdMax", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->suddenDeathIncrementSeconds );
	Info_SetValueForKey( info, "sdInc", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->suddenDeathPrintAnnouncements ? 1 : 0 );
	Info_SetValueForKey( info, "sdPrint", buffer );
	Com_sprintf( buffer, sizeof( buffer ), "%i", config->suddenDeathSpawnDelayActive ? 1 : 0 );
	Info_SetValueForKey( info, "sdDelay", buffer );

	Q_strncpyz( spawnHints, info, spawnHintsSize );
}
/*
=============
G_MatchConfig_UpdateConfigstrings

Publishes the cached match factory metadata into configstrings for clients.
=============
*/
void G_MatchConfig_UpdateConfigstrings( void ) {
	char				title[MAX_STRING_CHARS];
	char				flags[32];
	char				spawnHints[MAX_INFO_STRING];

	G_MatchConfig_BuildMetadataStrings( title, sizeof( title ), flags, sizeof( flags ), spawnHints, sizeof( spawnHints ) );

	trap_SetConfigstring( CS_FACTORY_TITLE, title );
	trap_SetConfigstring( CS_FACTORY_FLAGS, flags );
	trap_SetConfigstring( CS_SPAWN_HINTS, spawnHints );
}
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
	config.factoryRespawnDelayMilliseconds = G_MatchConfig_ReadNonNegativeCvar( &g_factoryRespawnDelay, DEFAULT_FACTORY_RESPAWN_DELAY_MILLISECONDS, "g_factoryRespawnDelay" );
	config.factoryWarmupSpawnDelayMilliseconds = G_MatchConfig_ReadNonNegativeCvar( &g_factoryWarmupSpawnDelay, DEFAULT_FACTORY_WARMUP_DELAY_MILLISECONDS, "g_factoryWarmupSpawnDelay" );
	config.factoryAllowItemDrops = G_MatchConfig_ReadBoolCvar( &g_factoryAllowItemDrops, DEFAULT_FACTORY_ALLOW_ITEM_DROPS ? qtrue : qfalse, "g_factoryAllowItemDrops" );
	config.factoryAllowItemBounce = G_MatchConfig_ReadBoolCvar( &g_factoryAllowItemBounce, DEFAULT_FACTORY_ALLOW_ITEM_BOUNCE ? qtrue : qfalse, "g_factoryAllowItemBounce" );

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

        G_Printf( "Match factory config (%s): timeoutLen=%i timeoutCount=%i overtime=%i suddenRespawn=%i start=%i tick=%i max=%i increment=%i print=%i delay=%i respawnMs=%i warmupMs=%i drops=%i bounce=%i\n",
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
                config->suddenDeathSpawnDelayActive ? 1 : 0,
                config->factoryRespawnDelayMilliseconds,
                config->factoryWarmupSpawnDelayMilliseconds,
                config->factoryAllowItemDrops ? 1 : 0,
                config->factoryAllowItemBounce ? 1 : 0 );
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
	G_MatchConfig_UpdateConfigstrings();
}

/*
=============
G_UpdateMatchFactoryConfig

Refreshes the cached match factory configuration and emits transition logs when CVars change.
=============
*/
void G_UpdateMatchFactoryConfig( void ) {
	matchFactoryConfig_t config = G_MatchConfig_Load();
	qboolean changed = qfalse;

	if ( config.timeoutLengthSeconds != s_reportedMatchFactoryConfig.timeoutLengthSeconds
		|| config.timeoutCountPerTeam != s_reportedMatchFactoryConfig.timeoutCountPerTeam
		|| config.overtimeLengthSeconds != s_reportedMatchFactoryConfig.overtimeLengthSeconds
		|| config.suddenDeathRespawnsEnabled != s_reportedMatchFactoryConfig.suddenDeathRespawnsEnabled
		|| config.suddenDeathStartSeconds != s_reportedMatchFactoryConfig.suddenDeathStartSeconds
		|| config.suddenDeathTickSeconds != s_reportedMatchFactoryConfig.suddenDeathTickSeconds
		|| config.suddenDeathMaxSeconds != s_reportedMatchFactoryConfig.suddenDeathMaxSeconds
		|| config.suddenDeathIncrementSeconds != s_reportedMatchFactoryConfig.suddenDeathIncrementSeconds
		|| config.suddenDeathPrintAnnouncements != s_reportedMatchFactoryConfig.suddenDeathPrintAnnouncements
		|| config.suddenDeathSpawnDelayActive != s_reportedMatchFactoryConfig.suddenDeathSpawnDelayActive
		|| config.factoryRespawnDelayMilliseconds != s_reportedMatchFactoryConfig.factoryRespawnDelayMilliseconds
		|| config.factoryWarmupSpawnDelayMilliseconds != s_reportedMatchFactoryConfig.factoryWarmupSpawnDelayMilliseconds
		|| config.factoryAllowItemDrops != s_reportedMatchFactoryConfig.factoryAllowItemDrops
		|| config.factoryAllowItemBounce != s_reportedMatchFactoryConfig.factoryAllowItemBounce ) {
		G_LogMatchFactoryConfig( "update", &config );
		s_reportedMatchFactoryConfig = config;
		changed = qtrue;
	}

	g_matchFactoryConfig = config;
	G_MatchConfig_UpdateConfigstrings();
	if ( changed ) {
		G_UpdateMatchStateConfigString();
	}
}

