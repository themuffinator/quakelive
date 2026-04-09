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
#include "g_match_config.h"

#include "../../ui/menudef.h"			// for the voice chats

#define SCORESTAT_PLACEMENT_SLOTS			2
#define SCORESTAT_FRAG_WEAPON_COUNT		13
#define SCORESTAT_ACCURACY_WEAPON_COUNT	12
#define SCORESTAT_DMG_WEAPON_COUNT		13
#define CASTAT_WEAPON_COUNT				( WP_NUM_WEAPONS - 1 )
#define TDMSTAT_FIELD_COUNT				11
#define CTFSTAT_FIELD_COUNT				12
#define RETAIL_TDM_TEAMSTAT_COUNT		14
#define RETAIL_CTF_TEAMSTAT_COUNT		17
#define RETAIL_TDM_SCORE_ROW_FIELDS		15
#define RETAIL_CTF_SCORE_ROW_FIELDS		17
#define RETAIL_FREEZE_SCORE_ROW_FIELDS	17

static const weapon_t scorestatFragWeapons[SCORESTAT_FRAG_WEAPON_COUNT] = {
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_CHAINGUN,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_HEAVY_MACHINEGUN
};

static const weapon_t scorestatAccuracyWeapons[SCORESTAT_ACCURACY_WEAPON_COUNT] = {
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_CHAINGUN,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_HEAVY_MACHINEGUN
};

static const weapon_t retailAccuracyCommandOrder[] = {
	WP_NONE,
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_GRAPPLING_HOOK,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_CHAINGUN,
	WP_HEAVY_MACHINEGUN
};

static const weapon_t castatWeapons[CASTAT_WEAPON_COUNT] = {
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_HEAVY_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_GRAPPLING_HOOK,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_CHAINGUN
};

static const teamScoreStatIndex_t scorestatPlacementPickupTeamStats[SCORESTAT_PICKUP_COUNT] = {
	TEAMSTAT_PICKUPS_RA,
	TEAMSTAT_PICKUPS_YA,
	TEAMSTAT_PICKUPS_GA,
	TEAMSTAT_PICKUPS_MH
};

static const teamScoreStatIndex_t retailTdmTeamStatOrder[RETAIL_TDM_TEAMSTAT_COUNT] = {
	TEAMSTAT_MAP_PICKUPS,
	TEAMSTAT_PICKUPS_RA,
	TEAMSTAT_PICKUPS_YA,
	TEAMSTAT_PICKUPS_GA,
	TEAMSTAT_PICKUPS_MH,
	TEAMSTAT_PICKUPS_QUAD,
	TEAMSTAT_PICKUPS_BS,
	TEAMSTAT_TIMEHELD_QUAD,
	TEAMSTAT_TIMEHELD_BS,
	TEAMSTAT_PICKUPS_FLAG,
	TEAMSTAT_PICKUPS_MEDKIT,
	TEAMSTAT_PICKUPS_REGEN,
	TEAMSTAT_PICKUPS_HASTE,
	TEAMSTAT_PICKUPS_INVIS
};

static const teamScoreStatIndex_t retailCtfTeamStatOrder[RETAIL_CTF_TEAMSTAT_COUNT] = {
	TEAMSTAT_PICKUPS_RA,
	TEAMSTAT_PICKUPS_YA,
	TEAMSTAT_PICKUPS_GA,
	TEAMSTAT_PICKUPS_MH,
	TEAMSTAT_PICKUPS_QUAD,
	TEAMSTAT_PICKUPS_BS,
	TEAMSTAT_TIMEHELD_QUAD,
	TEAMSTAT_TIMEHELD_BS,
	TEAMSTAT_PICKUPS_FLAG,
	TEAMSTAT_PICKUPS_MEDKIT,
	TEAMSTAT_PICKUPS_REGEN,
	TEAMSTAT_PICKUPS_HASTE,
	TEAMSTAT_PICKUPS_INVIS,
	TEAMSTAT_TIMEHELD_FLAG,
	TEAMSTAT_TIMEHELD_REGEN,
	TEAMSTAT_TIMEHELD_HASTE,
	TEAMSTAT_TIMEHELD_INVIS
};

static qboolean G_BuildRichScoreboardMessage( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildObeliskScoreboardMessage( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildFFAScoreboardMessage( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildDuelScoreboardMessage( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildClanArenaScoreboardMessage( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildRedRoverScoreboardMessage( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildTdmScoreboardRows( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildCtfScoreboardRows( char *payload, int payloadSize, int *emittedCount );
static qboolean G_BuildFreezeScoreboardRows( char *payload, int payloadSize, int *emittedCount );

static const gentity_t	*g_duelScoreboardViewer;

/*
==================
G_IsCTFStyleScoreboardGametype

Returns qtrue when the retail shared CTF-family intermission stats should be
published for the active gametype.
==================
*/
static qboolean G_IsCTFStyleScoreboardGametype( void ) {
	switch ( g_gametype.integer ) {
	case GT_CTF:
	case GT_1FCTF:
	case GT_HARVESTER:
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
==================
G_SendClientKeyMask

Pushes the current key mask for a specific subject client to one receiver.
==================
*/
void G_SendClientKeyMask( int targetClientNum, int subjectClientNum ) {
	int keyMask;

	if ( targetClientNum < 0 || targetClientNum >= level.maxclients ) {
		return;
	}
	if ( subjectClientNum < 0 || subjectClientNum >= level.maxclients ) {
		return;
	}
	if ( level.clients[targetClientNum].pers.connected != CON_CONNECTED ) {
		return;
	}

	keyMask = g_entities[subjectClientNum].keyMask;
	if ( keyMask < 0 ) {
		keyMask = 0;
	}

	trap_SendServerCommand( targetClientNum, va( "keymask %i %i", subjectClientNum, keyMask ) );
}

/*
==================
G_BroadcastClientKeyMask

Broadcasts the latest key mask for one client to all connected clients.
==================
*/
void G_BroadcastClientKeyMask( int subjectClientNum ) {
	int i;

	if ( subjectClientNum < 0 || subjectClientNum >= level.maxclients ) {
		return;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		if ( level.clients[i].pers.connected != CON_CONNECTED ) {
			continue;
		}
		G_SendClientKeyMask( i, subjectClientNum );
	}
}

/*
==================
G_SendAllClientKeyMasks

Sends the complete connected-client key mask table to one receiver.
==================
*/
void G_SendAllClientKeyMasks( int targetClientNum ) {
	char	payload[1024];
	char	entry[32];
	int		count;
	int		i;

	if ( targetClientNum < 0 || targetClientNum >= level.maxclients ) {
		return;
	}
	if ( level.clients[targetClientNum].pers.connected != CON_CONNECTED ) {
		return;
	}

	payload[0] = '\0';
	count = 0;
	for ( i = 0; i < level.maxclients; i++ ) {
		int keyMask;

		if ( level.clients[i].pers.connected != CON_CONNECTED ) {
			continue;
		}

		keyMask = g_entities[i].keyMask;
		if ( keyMask < 0 ) {
			keyMask = 0;
		}

		Com_sprintf( entry, sizeof( entry ), " %i %i", i, keyMask );
		if ( strlen( payload ) + strlen( entry ) + 1 >= sizeof( payload ) ) {
			break;
		}
		Q_strcat( payload, sizeof( payload ), entry );
		count++;
	}

	trap_SendServerCommand( targetClientNum, va( "keymasks %i%s", count, payload ) );
}

/*
==================
G_IsTeamHoldStatIndex

Reports whether a team stat index tracks a time-held duration.
==================
*/
static qboolean G_IsTeamHoldStatIndex( teamScoreStatIndex_t statIndex ) {
	switch ( statIndex ) {
	case TEAMSTAT_TIMEHELD_QUAD:
	case TEAMSTAT_TIMEHELD_BS:
	case TEAMSTAT_TIMEHELD_FLAG:
	case TEAMSTAT_TIMEHELD_REGEN:
	case TEAMSTAT_TIMEHELD_HASTE:
	case TEAMSTAT_TIMEHELD_INVIS:
		return qtrue;
	default:
		return qfalse;
	}
}

static const teamScoreStatIndex_t g_teamHoldStatOrder[] = {
	TEAMSTAT_TIMEHELD_QUAD,
	TEAMSTAT_TIMEHELD_BS,
	TEAMSTAT_TIMEHELD_FLAG,
	TEAMSTAT_TIMEHELD_REGEN,
	TEAMSTAT_TIMEHELD_HASTE,
	TEAMSTAT_TIMEHELD_INVIS
};

/*
==================
G_TeamHoldPowerupForStat

Maps a time-held stat bucket to the underlying powerup slot.
==================
*/
static int G_TeamHoldPowerupForStat( teamScoreStatIndex_t statIndex ) {
	switch ( statIndex ) {
	case TEAMSTAT_TIMEHELD_QUAD:
		return PW_QUAD;
	case TEAMSTAT_TIMEHELD_BS:
		return PW_BATTLESUIT;
	case TEAMSTAT_TIMEHELD_FLAG:
		return PW_NEUTRALFLAG;
	case TEAMSTAT_TIMEHELD_REGEN:
		return PW_REGEN;
	case TEAMSTAT_TIMEHELD_HASTE:
		return PW_HASTE;
	case TEAMSTAT_TIMEHELD_INVIS:
		return PW_INVIS;
	default:
		return -1;
	}
}

/*
==================
G_TeamHoldStatForPowerup

Resolves which time-held stat bucket should track a given powerup.
==================
*/
teamScoreStatIndex_t G_TeamHoldStatForPowerup( int powerup ) {
	switch ( powerup ) {
	case PW_QUAD:
		return TEAMSTAT_TIMEHELD_QUAD;
	case PW_BATTLESUIT:
		return TEAMSTAT_TIMEHELD_BS;
	case PW_REGEN:
		return TEAMSTAT_TIMEHELD_REGEN;
	case PW_HASTE:
		return TEAMSTAT_TIMEHELD_HASTE;
	case PW_INVIS:
		return TEAMSTAT_TIMEHELD_INVIS;
	case PW_REDFLAG:
	case PW_BLUEFLAG:
	case PW_NEUTRALFLAG:
		return TEAMSTAT_TIMEHELD_FLAG;
	default:
		return TEAMSTAT_COUNT;
	}
}

/*
==================
G_BeginClientTeamHoldStat

Starts accumulating elapsed time for a tracked hold-stat slot.
==================
*/
void G_BeginClientTeamHoldStat( gclient_t *client, teamScoreStatIndex_t statIndex ) {
	if ( !client ) {
		return;
	}

	if ( statIndex < 0 || statIndex >= TEAMSTAT_COUNT ) {
		return;
	}
	if ( !G_IsTeamHoldStatIndex( statIndex ) ) {
		return;
	}

	if ( client->pers.teamHoldStartTime[statIndex] <= 0 ) {
		client->pers.teamHoldStartTime[statIndex] = level.time;
	}
}

/*
==================
G_EndClientTeamHoldStat

Finalizes a tracked hold-stat slot and folds elapsed time into scoreboard stats.
==================
*/
void G_EndClientTeamHoldStat( gclient_t *client, teamScoreStatIndex_t statIndex, int endTime ) {
	int	startTime;
	int	duration;
	int	seconds;

	if ( !client ) {
		return;
	}

	if ( statIndex < 0 || statIndex >= TEAMSTAT_COUNT ) {
		return;
	}
	if ( !G_IsTeamHoldStatIndex( statIndex ) ) {
		return;
	}

	startTime = client->pers.teamHoldStartTime[statIndex];
	if ( startTime <= 0 ) {
		return;
	}

	if ( endTime <= 0 ) {
		endTime = level.time;
	}
	if ( endTime < startTime ) {
		endTime = startTime;
	}

	duration = endTime - startTime;
	seconds = ( duration + 500 ) / 1000;
	client->pers.teamScoreStats[statIndex] += seconds;
	client->pers.teamHoldStartTime[statIndex] = 0;
}

/*
==================
G_IsTeamHoldPowerupActive

Evaluates whether the mapped powerup for a stat index is currently active.
==================
*/
static qboolean G_IsTeamHoldPowerupActive( const gclient_t *client, teamScoreStatIndex_t statIndex, int now, int *expiryTime ) {
	int powerup;
	int value;

	if ( !client ) {
		return qfalse;
	}

	powerup = G_TeamHoldPowerupForStat( statIndex );
	if ( powerup < PW_NONE || powerup >= MAX_POWERUPS ) {
		return qfalse;
	}

	if ( statIndex == TEAMSTAT_TIMEHELD_FLAG ) {
		value = client->ps.powerups[PW_REDFLAG];
		if ( value > 0 ) {
			if ( expiryTime ) {
				*expiryTime = value;
			}
			return qtrue;
		}

		value = client->ps.powerups[PW_BLUEFLAG];
		if ( value > 0 ) {
			if ( expiryTime ) {
				*expiryTime = value;
			}
			return qtrue;
		}

		value = client->ps.powerups[PW_NEUTRALFLAG];
		if ( value > 0 ) {
			if ( expiryTime ) {
				*expiryTime = value;
			}
			return qtrue;
		}

		if ( expiryTime ) {
			*expiryTime = 0;
		}
		return qfalse;
	}

	value = client->ps.powerups[powerup];
	if ( expiryTime ) {
		*expiryTime = value;
	}
	return ( value > now ) ? qtrue : qfalse;
}

/*
==================
G_FlushExpiredClientTeamHoldStats

Closes any tracked hold slots that are no longer active.
==================
*/
void G_FlushExpiredClientTeamHoldStats( gclient_t *client, int now ) {
	int i;

	if ( !client ) {
		return;
	}

	for ( i = 0; i < sizeof( g_teamHoldStatOrder ) / sizeof( g_teamHoldStatOrder[0] ); i++ ) {
		teamScoreStatIndex_t statIndex;
		int	startTime;
		int	expiryTime;

		statIndex = g_teamHoldStatOrder[i];
		startTime = client->pers.teamHoldStartTime[statIndex];
		if ( startTime <= 0 ) {
			continue;
		}

		if ( G_IsTeamHoldPowerupActive( client, statIndex, now, &expiryTime ) ) {
			continue;
		}

		if ( statIndex != TEAMSTAT_TIMEHELD_FLAG && expiryTime > 0 && expiryTime < now ) {
			G_EndClientTeamHoldStat( client, statIndex, expiryTime );
		} else {
			G_EndClientTeamHoldStat( client, statIndex, now );
		}
	}
}

/*
==================
G_GetClientTeamHoldStatSeconds

Returns the current hold-time total including any active segment in progress.
==================
*/
int G_GetClientTeamHoldStatSeconds( gclient_t *client, teamScoreStatIndex_t statIndex, int now ) {
	int	value;
	int	startTime;
	int	expiryTime;

	if ( !client ) {
		return 0;
	}

	if ( statIndex < 0 || statIndex >= TEAMSTAT_COUNT ) {
		return 0;
	}
	if ( !G_IsTeamHoldStatIndex( statIndex ) ) {
		return client->pers.teamScoreStats[statIndex];
	}

	G_FlushExpiredClientTeamHoldStats( client, now );

	value = client->pers.teamScoreStats[statIndex];
	startTime = client->pers.teamHoldStartTime[statIndex];
	if ( startTime <= 0 ) {
		return value;
	}

	if ( !G_IsTeamHoldPowerupActive( client, statIndex, now, &expiryTime ) ) {
		return value;
	}

	if ( now > startTime ) {
		value += ( now - startTime + 500 ) / 1000;
	}

	return value;
}

/*
==================
G_TeamMapPickupProxyTotal

Builds a team aggregate pickup proxy from objective score counters.
==================
*/
static int G_TeamMapPickupProxyTotal( team_t team ) {
	int	total;
	int	i;

	total = 0;
	for ( i = 0; i < level.maxclients; i++ ) {
		const gclient_t	*cl;

		cl = &level.clients[i];
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( cl->sess.sessionTeam != team ) {
			continue;
		}

		total += cl->ps.persistant[PERS_CAPTURES];
		total += cl->ps.persistant[PERS_ASSIST_COUNT];
		total += cl->ps.persistant[PERS_DEFEND_COUNT];
	}

	return total;
}

/*
==================
G_BuildTeamScoreStatsFields

Builds team pickup/time-held aggregates for scorestats_team serialization.
==================
*/
static void G_BuildTeamScoreStatsFields( team_t team, int *fields, int fieldCount ) {
	int	i;

	if ( !fields || fieldCount <= 0 ) {
		return;
	}

	memset( fields, 0, sizeof( fields[0] ) * fieldCount );

	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t	*cl;
		int			fieldIndex;

		cl = &level.clients[i];
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( cl->sess.sessionTeam != team ) {
			continue;
		}

		for ( fieldIndex = TEAMSTAT_PICKUPS_RA; fieldIndex < TEAMSTAT_COUNT && fieldIndex < fieldCount; fieldIndex++ ) {
			if ( G_IsTeamHoldStatIndex( (teamScoreStatIndex_t)fieldIndex ) ) {
				fields[fieldIndex] += G_GetClientTeamHoldStatSeconds( cl, (teamScoreStatIndex_t)fieldIndex, level.time );
			} else {
				fields[fieldIndex] += cl->pers.teamScoreStats[fieldIndex];
			}
		}
	}

	if ( fieldCount > TEAMSTAT_MAP_PICKUPS ) {
		int mapPickups;
		int sourceIndex;
		static const teamScoreStatIndex_t mapPickupSources[] = {
			TEAMSTAT_PICKUPS_RA,
			TEAMSTAT_PICKUPS_YA,
			TEAMSTAT_PICKUPS_GA,
			TEAMSTAT_PICKUPS_MH,
			TEAMSTAT_PICKUPS_QUAD,
			TEAMSTAT_PICKUPS_BS,
			TEAMSTAT_PICKUPS_FLAG,
			TEAMSTAT_PICKUPS_MEDKIT,
			TEAMSTAT_PICKUPS_REGEN,
			TEAMSTAT_PICKUPS_HASTE,
			TEAMSTAT_PICKUPS_INVIS
		};

		mapPickups = 0;
		for ( sourceIndex = 0; sourceIndex < sizeof( mapPickupSources ) / sizeof( mapPickupSources[0] ); sourceIndex++ ) {
			int fieldIndex;

			fieldIndex = mapPickupSources[sourceIndex];
			if ( fieldIndex < fieldCount ) {
				mapPickups += fields[fieldIndex];
			}
		}

		if ( mapPickups > 0 ) {
			fields[TEAMSTAT_MAP_PICKUPS] = mapPickups;
		} else {
			fields[TEAMSTAT_MAP_PICKUPS] = G_TeamMapPickupProxyTotal( team );
		}
	}
}

/*
==================
G_SendTeamScoreStatsMessage

Sends team pickup/time-held aggregates used by team ownerdraw panels.
==================
*/
static void G_SendTeamScoreStatsMessage( gentity_t *ent ) {
	char	payload[1024];
	char	entry[32];
	int		teamFields[2][TEAMSTAT_COUNT];
	int		teamIndex;
	int		fieldIndex;
	qboolean	truncated;

	if ( !ent ) {
		return;
	}

	G_BuildTeamScoreStatsFields( TEAM_RED, teamFields[0], TEAMSTAT_COUNT );
	G_BuildTeamScoreStatsFields( TEAM_BLUE, teamFields[1], TEAMSTAT_COUNT );

	payload[0] = '\0';
	truncated = qfalse;
	for ( teamIndex = 0; teamIndex < 2; teamIndex++ ) {
		for ( fieldIndex = 0; fieldIndex < TEAMSTAT_COUNT; fieldIndex++ ) {
			Com_sprintf( entry, sizeof( entry ), " %i", teamFields[teamIndex][fieldIndex] );
			if ( strlen( payload ) + strlen( entry ) + 1 >= sizeof( payload ) ) {
				truncated = qtrue;
				break;
			}
			Q_strcat( payload, sizeof( payload ), entry );
		}
		if ( truncated ) {
			break;
		}
	}

	trap_SendServerCommand( ent - g_entities, va( "scorestats_team %i%s", TEAMSTAT_COUNT, payload ) );
}

/*
==================
G_FindNextActivePlacementClient

Returns the next connected non-spectator client index from level.sortedClients.
==================
*/
static int G_FindNextActivePlacementClient( int startIndex ) {
	int	i;

	for ( i = startIndex; i < level.numConnectedClients; i++ ) {
		int			clientNum;
		const gclient_t	*cl;

		clientNum = level.sortedClients[i];
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			continue;
		}

		cl = &level.clients[clientNum];
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( cl->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}

		return i;
	}

	return -1;
}

/*
==================
G_AppendScoreStatsWeaponValues

Serializes per-weapon values using the supplied weapon order table.
==================
*/
static void G_AppendScoreStatsWeaponValues( char *buffer, size_t bufferSize, const int *values, const weapon_t *weaponOrder, int weaponCount ) {
	int		i;
	char	entry[32];

	if ( !buffer || !values || !weaponOrder || weaponCount <= 0 ) {
		return;
	}

	for ( i = 0; i < weaponCount; i++ ) {
		int weapon = weaponOrder[i];

		if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
			continue;
		}

		Com_sprintf( entry, sizeof( entry ), " %i", values[weapon] );
		Q_strcat( buffer, bufferSize, entry );
	}
}

/*
==================
G_GetPlacementPickupAverageSeconds

Returns the retail pickup-average interval in seconds between matching pickup
events.
==================
*/
static float G_GetPlacementPickupAverageSeconds( const gclient_t *cl, scorestatPickupIndex_t pickupIndex ) {
	int intervalCount;
	int totalIntervalMs;

	if ( !cl ) {
		return 0.0f;
	}

	if ( pickupIndex < 0 || pickupIndex >= SCORESTAT_PICKUP_COUNT ) {
		return 0.0f;
	}

	intervalCount = cl->pers.pickupIntervalCount[pickupIndex];
	if ( intervalCount <= 0 ) {
		return 0.0f;
	}

	totalIntervalMs = cl->pers.pickupIntervalTotalMs[pickupIndex];
	if ( totalIntervalMs <= 0 ) {
		return 0.0f;
	}

	return ( (float)totalIntervalMs / 1000.0f ) / (float)intervalCount;
}

/*
==================
G_GetPlacementProgressionPr

Resolves placement PR value from session skill metadata.
==================
*/
static int G_GetPlacementProgressionPr( const gclient_t *cl ) {
	int progressionPr;

	if ( !cl ) {
		return 0;
	}

	progressionPr = cl->sess.skill1;
	if ( progressionPr < 0 ) {
		progressionPr = 0;
	}

	return progressionPr;
}

/*
==================
G_GetPlacementProgressionTier

Resolves placement tier value from session skill metadata.
==================
*/
static int G_GetPlacementProgressionTier( const gclient_t *cl ) {
	int progressionTier;

	if ( !cl ) {
		return 0;
	}

	progressionTier = cl->sess.skill2;
	if ( progressionTier < 0 ) {
		progressionTier = 0;
	}

	return progressionTier;
}

/*
==================
G_SendScoreStatsMessage

Sends a compact placement stat payload (weapons + pickups) for top rows.
==================
*/
static void G_SendScoreStatsMessage( gentity_t *ent ) {
	char	payload[1024];
	char	entry[32];
	int		slot;
	int		sortedIndex;
	int		emitted;

	if ( !ent ) {
		return;
	}

	payload[0] = '\0';
	sortedIndex = 0;
	emitted = 0;

	for ( slot = 0; slot < SCORESTAT_PLACEMENT_SLOTS; slot++ ) {
		int			clientNum;
		const gclient_t	*cl;

		sortedIndex = G_FindNextActivePlacementClient( sortedIndex );
		if ( sortedIndex < 0 ) {
			break;
		}

		clientNum = level.sortedClients[sortedIndex];
		sortedIndex++;
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			continue;
		}

		cl = &level.clients[clientNum];
		Com_sprintf( entry, sizeof( entry ), " %i", clientNum );
		Q_strcat( payload, sizeof( payload ), entry );

		G_AppendScoreStatsWeaponValues( payload, sizeof( payload ), cl->pers.weaponFrags, scorestatFragWeapons, SCORESTAT_FRAG_WEAPON_COUNT );
		G_AppendScoreStatsWeaponValues( payload, sizeof( payload ), cl->pers.accuracy_hits, scorestatAccuracyWeapons, SCORESTAT_ACCURACY_WEAPON_COUNT );
		G_AppendScoreStatsWeaponValues( payload, sizeof( payload ), cl->pers.accuracy_shots, scorestatAccuracyWeapons, SCORESTAT_ACCURACY_WEAPON_COUNT );
		G_AppendScoreStatsWeaponValues( payload, sizeof( payload ), cl->pers.weaponDamage, scorestatFragWeapons, SCORESTAT_DMG_WEAPON_COUNT );
		{
			int pickupIndex;

			for ( pickupIndex = 0; pickupIndex < SCORESTAT_PICKUP_COUNT; pickupIndex++ ) {
				int countValue;
				char valueEntry[32];
				teamScoreStatIndex_t teamStatIndex;

				teamStatIndex = scorestatPlacementPickupTeamStats[pickupIndex];
				countValue = cl->pers.teamScoreStats[teamStatIndex];
				Com_sprintf( valueEntry, sizeof( valueEntry ), " %i", countValue );
				Q_strcat( payload, sizeof( payload ), valueEntry );
			}

			for ( pickupIndex = 0; pickupIndex < SCORESTAT_PICKUP_COUNT; pickupIndex++ ) {
				float avgSeconds;
				char valueEntry[32];

				avgSeconds = G_GetPlacementPickupAverageSeconds( cl, (scorestatPickupIndex_t)pickupIndex );
				Com_sprintf( valueEntry, sizeof( valueEntry ), " %3.2f", avgSeconds );
				Q_strcat( payload, sizeof( payload ), valueEntry );
			}

			{
				int progressionPr;
				int progressionTier;
				char valueEntry[32];

				progressionPr = G_GetPlacementProgressionPr( cl );
				progressionTier = G_GetPlacementProgressionTier( cl );

				Com_sprintf( valueEntry, sizeof( valueEntry ), " %i", progressionPr );
				Q_strcat( payload, sizeof( payload ), valueEntry );
				Com_sprintf( valueEntry, sizeof( valueEntry ), " %i", progressionTier );
				Q_strcat( payload, sizeof( payload ), valueEntry );
			}
		}
		emitted++;
	}

	trap_SendServerCommand( ent - g_entities, va( "scorestats %i%s", emitted, payload ) );
}

/*
==================
G_GetCAWeaponAccuracy

Returns the retail-style per-weapon accuracy percentage used by castats rows.
==================
*/
static int G_GetCAWeaponAccuracy( const gclient_t *cl, weapon_t weapon ) {
	int shots;
	int hits;

	if ( !cl ) {
		return 0;
	}
	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return 0;
	}

	shots = cl->pers.accuracy_shots[weapon];
	if ( shots <= 0 ) {
		return 0;
	}

	hits = cl->pers.accuracy_hits[weapon];
	if ( hits <= 0 ) {
		return 0;
	}

	return hits * 100 / shots;
}

/*
==================
G_SendCAStatsMessage

Publishes the retail intermission-only castats rows for Clan Arena.
==================
*/
static void G_SendCAStatsMessage( gentity_t *ent ) {
	int i;

	if ( !ent ) {
		return;
	}

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		char		payload[1024];
		char		entry[32];
		int		clientNum;
		gclient_t	*cl;
		int		weaponIndex;

		clientNum = level.sortedClients[i];
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			continue;
		}

		cl = &level.clients[clientNum];
		payload[0] = '\0';

		Com_sprintf( entry, sizeof( entry ), " %i %i", cl->pers.damageGiven, cl->pers.damageReceived );
		Q_strcat( payload, sizeof( payload ), entry );

		for ( weaponIndex = 0; weaponIndex < CASTAT_WEAPON_COUNT; weaponIndex++ ) {
			weapon_t weapon;
			int accuracy;

			weapon = castatWeapons[weaponIndex];
			accuracy = G_GetCAWeaponAccuracy( cl, weapon );

			Com_sprintf( entry, sizeof( entry ), " %i %i", cl->pers.weaponFrags[weapon], accuracy );
			Q_strcat( payload, sizeof( payload ), entry );
		}

		trap_SendServerCommand( ent - g_entities, va( "castats %i%s", i, payload ) );
	}
}

/*
==================
G_SendTDMStatsMessage

Publishes the retail intermission-only tdmstats rows for TDM-family scoreboards.
Retail uses pickup, damage, team-damage, and world-death counters here rather
than the older source-side hold/objective mix.
==================
*/
static void G_SendTDMStatsMessage( gentity_t *ent ) {
	int i;

	if ( !ent ) {
		return;
	}

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		char		payload[1024];
		char		entry[32];
		int		clientNum;
		gclient_t	*cl;
		int		values[TDMSTAT_FIELD_COUNT];
		int		fieldIndex;

		clientNum = level.sortedClients[i];
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			continue;
		}

		cl = &level.clients[clientNum];
		payload[0] = '\0';

		values[0] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_BS];
		values[1] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_QUAD];
		values[2] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_MH];
		values[3] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_GA];
		values[4] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_YA];
		values[5] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_RA];
		values[6] = cl->pers.damageReceived;
		values[7] = cl->pers.damageGiven;
		values[8] = cl->teamDamageEventsReceived;
		values[9] = cl->teamDamageEventsGiven;
		values[10] = cl->environmentalDeaths;

		for ( fieldIndex = 0; fieldIndex < TDMSTAT_FIELD_COUNT; fieldIndex++ ) {
			Com_sprintf( entry, sizeof( entry ), " %i", values[fieldIndex] );
			Q_strcat( payload, sizeof( payload ), entry );
		}

		trap_SendServerCommand( ent - g_entities, va( "tdmstats %i%s", i, payload ) );
	}
}

/*
==================
G_SendCTFStatsMessage

Publishes the retail intermission-only ctfstats rows for shared CTF-family
scoreboards. Retail reuses a pickup and damage row here instead of the classic
teamState objective counters.
==================
*/
static void G_SendCTFStatsMessage( gentity_t *ent ) {
	int i;

	if ( !ent ) {
		return;
	}

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		char		payload[1024];
		char		entry[32];
		int		clientNum;
		gclient_t	*cl;
		int		values[CTFSTAT_FIELD_COUNT];
		int		fieldIndex;

		clientNum = level.sortedClients[i];
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			continue;
		}

		cl = &level.clients[clientNum];
		payload[0] = '\0';

		values[0] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_INVIS];
		values[1] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_HASTE];
		values[2] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_REGEN];
		values[3] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_BS];
		values[4] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_QUAD];
		values[5] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_MH];
		values[6] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_GA];
		values[7] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_YA];
		values[8] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_RA];
		values[9] = cl->pers.damageReceived;
		values[10] = cl->pers.damageGiven;
		values[11] = cl->environmentalDeaths;

		for ( fieldIndex = 0; fieldIndex < CTFSTAT_FIELD_COUNT; fieldIndex++ ) {
			Com_sprintf( entry, sizeof( entry ), " %i", values[fieldIndex] );
			Q_strcat( payload, sizeof( payload ), entry );
		}

		trap_SendServerCommand( ent - g_entities, va( "ctfstats %i%s", i, payload ) );
	}
}

/*
==================
G_CopyRetailTeamScoreboardHeaderValues

Builds the retail-style team aggregate header block used by team-family rich
scoreboard payloads from the existing per-team ownerdraw stat cache.
==================
*/
static void G_CopyRetailTeamScoreboardHeaderValues( team_t team, const teamScoreStatIndex_t *statOrder, int statCount, int *values ) {
	int teamFields[TEAMSTAT_COUNT];
	int i;

	if ( !statOrder || !values || statCount <= 0 ) {
		return;
	}

	G_BuildTeamScoreStatsFields( team, teamFields, TEAMSTAT_COUNT );
	for ( i = 0; i < statCount; i++ ) {
		values[i] = teamFields[statOrder[i]];
	}
}

/*
==================
G_AppendPreparedRetailTeamScoreboardHeader

Appends a prebuilt red/blue retail team aggregate header block to a scoreboard
payload, returning qfalse when the combined message would overflow.
==================
*/
static qboolean G_AppendPreparedRetailTeamScoreboardHeader( char *payload, int payloadSize, int teamValues[2][RETAIL_CTF_TEAMSTAT_COUNT], int statCount ) {
	char entry[32];
	int teamIndex;
	int statIndex;

	if ( !payload || payloadSize <= 0 ) {
		return qfalse;
	}
	if ( !teamValues || statCount <= 0 || statCount > RETAIL_CTF_TEAMSTAT_COUNT ) {
		return qfalse;
	}

	for ( teamIndex = 0; teamIndex < 2; teamIndex++ ) {
		for ( statIndex = 0; statIndex < statCount; statIndex++ ) {
			Com_sprintf( entry, sizeof( entry ), " %i", teamValues[teamIndex][statIndex] );
			if ( strlen( payload ) + strlen( entry ) + 1 >= payloadSize ) {
				return qfalse;
			}
			Q_strcat( payload, payloadSize, entry );
		}
	}

	return qtrue;
}

/*
==================
G_AppendRetailTeamScoreboardHeader

Appends a retail-style red/blue team aggregate header block to a scoreboard
payload, returning qfalse when the combined message would overflow.
==================
*/
static qboolean G_AppendRetailTeamScoreboardHeader( char *payload, int payloadSize, const teamScoreStatIndex_t *statOrder, int statCount ) {
	int teamValues[2][RETAIL_CTF_TEAMSTAT_COUNT];
	int teamIndex;

	if ( !payload || payloadSize <= 0 ) {
		return qfalse;
	}
	if ( !statOrder || statCount <= 0 || statCount > RETAIL_CTF_TEAMSTAT_COUNT ) {
		return qfalse;
	}

	for ( teamIndex = 0; teamIndex < 2; teamIndex++ ) {
		G_CopyRetailTeamScoreboardHeaderValues(
			( teamIndex == 0 ) ? TEAM_RED : TEAM_BLUE,
			statOrder,
			statCount,
			teamValues[teamIndex] );
	}

	return G_AppendPreparedRetailTeamScoreboardHeader( payload, payloadSize, teamValues, statCount );
}

/*
==================
G_ApplyRetailCTFEnemyHeaderSuppression

Retail scores_ctf hides most opposing-team aggregate header fields for live
red/blue viewers, while preserving three specific slots and restoring the full
header during intermission or spectator views.
==================
*/
static void G_ApplyRetailCTFEnemyHeaderSuppression( const gentity_t *viewer, int teamValues[2][RETAIL_CTF_TEAMSTAT_COUNT] ) {
	int enemyTeamIndex;
	int statIndex;
	team_t viewerTeam;

	if ( !viewer || !viewer->client || level.intermissiontime ) {
		return;
	}

	viewerTeam = viewer->client->sess.sessionTeam;
	if ( viewerTeam != TEAM_RED && viewerTeam != TEAM_BLUE ) {
		return;
	}

	enemyTeamIndex = ( viewerTeam == TEAM_RED ) ? 1 : 0;
	for ( statIndex = 0; statIndex < RETAIL_CTF_TEAMSTAT_COUNT; statIndex++ ) {
		if ( statIndex == 8 || statIndex == 10 || statIndex == 16 ) {
			continue;
		}

		teamValues[enemyTeamIndex][statIndex] = 0;
	}
}

/*
==================
G_BuildTeamScoreboardMessage

Builds the retail-style TDM rich scoreboard header block and appends the
current GPL-shaped per-client row payload.
==================
*/
static qboolean G_BuildTeamScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	char rowPayload[MAX_STRING_CHARS];
	char counts[64];
	int count;

	if ( !payload || payloadSize <= 0 ) {
		return qfalse;
	}

	if ( !G_BuildTdmScoreboardRows( rowPayload, sizeof( rowPayload ), &count ) ) {
		return qfalse;
	}

	payload[0] = '\0';
	if ( !G_AppendRetailTeamScoreboardHeader( payload, payloadSize, retailTdmTeamStatOrder, RETAIL_TDM_TEAMSTAT_COUNT ) ) {
		return qfalse;
	}

	Com_sprintf( counts, sizeof( counts ), " %i %i %i", count, level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE] );
	if ( strlen( payload ) + strlen( counts ) + strlen( rowPayload ) + 1 >= payloadSize ) {
		return qfalse;
	}

	Q_strcat( payload, payloadSize, counts );
	Q_strcat( payload, payloadSize, rowPayload );

	if ( emittedCount ) {
		*emittedCount = count;
	}

	return qtrue;
}

/*
==================
G_BuildCTFStyleScoreboardMessage

Builds the retail-style shared CTF-family rich scoreboard header block and
appends the current GPL-shaped per-client row payload.
==================
*/
static qboolean G_BuildCTFStyleScoreboardMessage( gentity_t *viewer, char *payload, int payloadSize, int *emittedCount ) {
	char rowPayload[MAX_STRING_CHARS];
	char counts[64];
	int teamValues[2][RETAIL_CTF_TEAMSTAT_COUNT];
	int count;

	if ( !payload || payloadSize <= 0 ) {
		return qfalse;
	}

	if ( !G_BuildCtfScoreboardRows( rowPayload, sizeof( rowPayload ), &count ) ) {
		return qfalse;
	}

	payload[0] = '\0';
	G_CopyRetailTeamScoreboardHeaderValues( TEAM_RED, retailCtfTeamStatOrder, RETAIL_CTF_TEAMSTAT_COUNT, teamValues[0] );
	G_CopyRetailTeamScoreboardHeaderValues( TEAM_BLUE, retailCtfTeamStatOrder, RETAIL_CTF_TEAMSTAT_COUNT, teamValues[1] );
	G_ApplyRetailCTFEnemyHeaderSuppression( viewer, teamValues );
	if ( !G_AppendPreparedRetailTeamScoreboardHeader( payload, payloadSize, teamValues, RETAIL_CTF_TEAMSTAT_COUNT ) ) {
		return qfalse;
	}

	Com_sprintf( counts, sizeof( counts ), " %i %i %i", count, level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE] );
	if ( strlen( payload ) + strlen( counts ) + strlen( rowPayload ) + 1 >= payloadSize ) {
		return qfalse;
	}

	Q_strcat( payload, payloadSize, counts );
	Q_strcat( payload, payloadSize, rowPayload );

	if ( emittedCount ) {
		*emittedCount = count;
	}

	return qtrue;
}

/*
==================
G_BuildFreezeScoreboardMessage

Retail Freeze reuses the same red/blue team aggregate header shape as the TDM
family before appending its per-client row block.
==================
*/
static qboolean G_BuildFreezeScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	char rowPayload[MAX_STRING_CHARS];
	char counts[64];
	int count;

	if ( !payload || payloadSize <= 0 ) {
		return qfalse;
	}

	if ( !G_BuildFreezeScoreboardRows( rowPayload, sizeof( rowPayload ), &count ) ) {
		return qfalse;
	}

	payload[0] = '\0';
	if ( !G_AppendRetailTeamScoreboardHeader( payload, payloadSize, retailTdmTeamStatOrder, RETAIL_TDM_TEAMSTAT_COUNT ) ) {
		return qfalse;
	}

	Com_sprintf( counts, sizeof( counts ), " %i %i %i", count, level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE] );
	if ( strlen( payload ) + strlen( counts ) + strlen( rowPayload ) + 1 >= payloadSize ) {
		return qfalse;
	}

	Q_strcat( payload, payloadSize, counts );
	Q_strcat( payload, payloadSize, rowPayload );

	if ( emittedCount ) {
		*emittedCount = count;
	}

	return qtrue;
}

/*
==================
G_GetScoreboardPing

Clamps scoreboard ping values to the retail-visible range.
==================
*/
static int G_GetScoreboardPing( const gclient_t *cl ) {
	if ( cl->pers.connected == CON_CONNECTING ) {
		return -1;
	}

	if ( cl->ps.ping >= 999 ) {
		return 999;
	}

	return cl->ps.ping;
}

/*
==================
G_GetScoreboardFallbackWeapon

Returns the retail-style fallback weapon used by team-family scoreboard rows
when a client has no recorded frag leader yet.
==================
*/
static weapon_t G_GetScoreboardFallbackWeapon( const gclient_t *cl ) {
	unsigned int	weaponMask;
	weapon_t	weapon;

	weaponMask = cl ? (unsigned int)cl->ps.stats[STAT_WEAPONS] : 0u;
	if ( !weaponMask ) {
		if ( g_startingWeapons.integer > 0 ) {
			weaponMask = (unsigned int)g_startingWeapons.integer;
		} else {
			weaponMask = g_factoryCvarConfig.startingWeaponsStatMask;
		}
	}
	if ( !weaponMask ) {
		weaponMask = ( 1u << WP_MACHINEGUN ) | ( 1u << WP_GAUNTLET );
	}

	if ( weaponMask & ( 1u << WP_MACHINEGUN ) ) {
		return WP_MACHINEGUN;
	}

	for ( weapon = WP_NUM_WEAPONS - 1; weapon > WP_NONE; --weapon ) {
		if ( weapon == WP_MACHINEGUN ) {
			continue;
		}

		if ( weaponMask & ( 1u << weapon ) ) {
			return weapon;
		}
	}

	if ( weaponMask & ( 1u << WP_GAUNTLET ) ) {
		return WP_GAUNTLET;
	}

	return WP_MACHINEGUN;
}

/*
==================
G_GetClientScoreboardWeapon

Mirrors the retail best-weapon selector used by the team-family scoreboard
rows: highest frag count wins, otherwise the current loadout fallback is used.
==================
*/
static weapon_t G_GetClientScoreboardWeapon( const gclient_t *cl ) {
	int		bestCount;
	weapon_t	bestWeapon;
	weapon_t	weapon;

	if ( !cl ) {
		return WP_MACHINEGUN;
	}

	bestCount = 0;
	bestWeapon = WP_NONE;
	for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; ++weapon ) {
		if ( cl->pers.weaponFrags[weapon] > bestCount ) {
			bestCount = cl->pers.weaponFrags[weapon];
			bestWeapon = weapon;
		}
	}

	if ( bestWeapon != WP_NONE ) {
		return bestWeapon;
	}

	return G_GetScoreboardFallbackWeapon( cl );
}

/*
==================
G_GetClientScoreboardAccuracy

Returns the retail-style scoreboard accuracy percentage for the current match.
==================
*/
static int G_GetClientScoreboardAccuracy( const gclient_t *cl ) {
	if ( !cl || !cl->accuracy_shots ) {
		return 0;
	}

	return cl->accuracy_hits * 100 / cl->accuracy_shots;
}

/*
==================
G_GetDuelScoreboardPickupCount

Returns the retail duel scoreboard pickup-count field for the requested item.
==================
*/
static int G_GetDuelScoreboardPickupCount( const gclient_t *cl, scorestatPickupIndex_t pickupIndex ) {
	if ( !cl || pickupIndex < 0 || pickupIndex >= SCORESTAT_PICKUP_COUNT ) {
		return 0;
	}

	return cl->pers.pickupIntervalCount[pickupIndex];
}

/*
==================
G_GetDuelScoreboardPickupAverageSeconds

Returns the retail duel scoreboard pickup-average field in seconds.
==================
*/
static float G_GetDuelScoreboardPickupAverageSeconds( const gclient_t *cl, scorestatPickupIndex_t pickupIndex ) {
	int	count;
	int	totalMs;

	if ( !cl || pickupIndex < 0 || pickupIndex >= SCORESTAT_PICKUP_COUNT ) {
		return 0.0f;
	}

	count = cl->pers.pickupIntervalCount[pickupIndex];
	totalMs = cl->pers.pickupIntervalTotalMs[pickupIndex];
	if ( count <= 0 || totalMs <= 0 ) {
		return 0.0f;
	}

	return ( (float)totalMs / 1000.0f ) / (float)count;
}

/*
==================
G_AppendDuelWeaponScoreboardStats

Builds the retail per-weapon duel stat tail appended to each scores_duel row.
==================
*/
static void G_AppendDuelWeaponScoreboardStats( char *payload, int payloadSize, const gclient_t *cl ) {
	char		entry[64];
	weapon_t	weapon;

	if ( !payload || payloadSize <= 0 ) {
		return;
	}

	for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; ++weapon ) {
		int	shots;
		int	hits;
		int	accuracy;
		int	frags;
		int	damage;

		shots = cl ? cl->pers.accuracy_shots[weapon] : 0;
		hits = cl ? cl->pers.accuracy_hits[weapon] : 0;
		accuracy = 0;
		if ( shots > 0 ) {
			accuracy = hits * 100 / shots;
		}

		frags = cl ? cl->pers.weaponFrags[weapon] : 0;
		damage = cl ? cl->pers.weaponDamage[weapon] : 0;

		Com_sprintf( entry, sizeof( entry ), " %i %i %i %i %i",
			frags,
			damage,
			accuracy,
			shots,
			hits );
		Q_strcat( payload, payloadSize, entry );
	}
}

/*
==================
G_ShouldRevealDuelScoreboardDetails

Mirrors the retail duel item-timing visibility split for the local player and
spectators while leaving the public row redacted for active opponents.
==================
*/
static qboolean G_ShouldRevealDuelScoreboardDetails( const gentity_t *viewer, int clientNum ) {
	if ( level.intermissiontime ) {
		return qtrue;
	}

	if ( !viewer || !viewer->client ) {
		return qfalse;
	}

	if ( viewer->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return qtrue;
	}

	return ( ( viewer - g_entities ) == clientNum ) ? qtrue : qfalse;
}

/*
==================
G_BuildDuelScoreboardRow

Builds one retail scores_duel row for the selected player.
==================
*/
static void G_BuildDuelScoreboardRow( char *payload, int payloadSize, int clientNum, qboolean revealPickupTiming ) {
	gclient_t		*cl;
	int			kills;
	int			deaths;
	int			accuracy;
	int			bestWeapon;
	int			damage;
	int			impressiveCount;
	int			excellentCount;
	int			gauntletCount;
	int			activePlayer;
	int			redArmorCount;
	float			redArmorAverage;
	int			yellowArmorCount;
	float			yellowArmorAverage;
	int			greenArmorCount;
	float			greenArmorAverage;
	int			megaHealthCount;
	float			megaHealthAverage;

	payload[0] = '\0';
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return;
	}

	cl = &level.clients[clientNum];
	kills = cl->killCount;
	deaths = cl->deathCount;
	accuracy = G_GetClientScoreboardAccuracy( cl );
	bestWeapon = G_GetClientScoreboardWeapon( cl );
	damage = cl->pers.damageGiven;
	impressiveCount = cl->ps.persistant[PERS_IMPRESSIVE_COUNT];
	excellentCount = cl->ps.persistant[PERS_EXCELLENT_COUNT];
	gauntletCount = cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT];
	activePlayer = ( cl->sess.sessionTeam != TEAM_SPECTATOR && cl->ps.pm_type == PM_NORMAL ) ? 1 : 0;

	redArmorCount = 0;
	redArmorAverage = 0.0f;
	yellowArmorCount = 0;
	yellowArmorAverage = 0.0f;
	greenArmorCount = 0;
	greenArmorAverage = 0.0f;
	megaHealthCount = 0;
	megaHealthAverage = 0.0f;
	if ( revealPickupTiming ) {
		redArmorCount = G_GetDuelScoreboardPickupCount( cl, SCORESTAT_PICKUP_RA );
		redArmorAverage = G_GetDuelScoreboardPickupAverageSeconds( cl, SCORESTAT_PICKUP_RA );
		yellowArmorCount = G_GetDuelScoreboardPickupCount( cl, SCORESTAT_PICKUP_YA );
		yellowArmorAverage = G_GetDuelScoreboardPickupAverageSeconds( cl, SCORESTAT_PICKUP_YA );
		greenArmorCount = G_GetDuelScoreboardPickupCount( cl, SCORESTAT_PICKUP_GA );
		greenArmorAverage = G_GetDuelScoreboardPickupAverageSeconds( cl, SCORESTAT_PICKUP_GA );
		megaHealthCount = G_GetDuelScoreboardPickupCount( cl, SCORESTAT_PICKUP_MH );
		megaHealthAverage = G_GetDuelScoreboardPickupAverageSeconds( cl, SCORESTAT_PICKUP_MH );
	}

	Com_sprintf( payload, payloadSize,
		"%i %i %i %i %i %i %i %i %i %i %i %i %i %i %3.2f %i %3.2f %i %3.2f %i %3.2f",
		clientNum,
		cl->ps.persistant[PERS_SCORE],
		G_GetScoreboardPing( cl ),
		(level.time - cl->pers.enterTime) / 60000,
		kills,
		deaths,
		accuracy,
		bestWeapon,
		damage,
		impressiveCount,
		excellentCount,
		gauntletCount,
		activePlayer,
		redArmorCount,
		redArmorAverage,
		yellowArmorCount,
		yellowArmorAverage,
		greenArmorCount,
		greenArmorAverage,
		megaHealthCount,
		megaHealthAverage );

	G_AppendDuelWeaponScoreboardStats( payload, payloadSize, cl );
}

/*
==================
G_BuildTdmScoreboardRows

Builds the retail GT_TEAM per-client scoreboard row block.
==================
*/
static qboolean G_BuildTdmScoreboardRows( char *payload, int payloadSize, int *emittedCount ) {
	char		entry[1024];
	int		stringlength;
	int		i;
	int		emitted;

	payload[0] = '\0';
	stringlength = 0;
	emitted = 0;

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		const int	clientNum = level.sortedClients[i];
		gclient_t	*cl;
		int		j;

		cl = &level.clients[clientNum];
		Com_sprintf( entry, sizeof( entry ),
			" %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i",
			clientNum,
			cl->sess.sessionTeam,
			cl->ps.persistant[PERS_SCORE],
			G_GetScoreboardPing( cl ),
			(level.time - cl->pers.enterTime) / 60000,
			cl->killCount,
			cl->deathCount,
			G_GetClientScoreboardAccuracy( cl ),
			G_GetClientScoreboardWeapon( cl ),
			cl->ps.persistant[PERS_IMPRESSIVE_COUNT],
			cl->ps.persistant[PERS_EXCELLENT_COUNT],
			cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT],
			cl->teamDamageEventsGiven,
			cl->teamDamageEventsReceived,
			cl->pers.damageGiven );

		j = strlen( entry );
		if ( stringlength + j + 32 >= payloadSize ) {
			if ( emittedCount ) {
				*emittedCount = emitted;
			}
			return qfalse;
		}

		Q_strcat( payload, payloadSize, entry );
		stringlength += j;
		emitted++;
	}

	if ( emittedCount ) {
		*emittedCount = emitted;
	}

	return qtrue;
}

/*
==================
G_BuildCtfScoreboardRows

Builds the retail shared CTF-family per-client scoreboard row block.
==================
*/
static qboolean G_BuildCtfScoreboardRows( char *payload, int payloadSize, int *emittedCount ) {
	char		entry[1024];
	int		stringlength;
	int		i;
	int		emitted;

	payload[0] = '\0';
	stringlength = 0;
	emitted = 0;

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		const int	clientNum = level.sortedClients[i];
		gclient_t	*cl;
		int		perfect;
		int		j;

		cl = &level.clients[clientNum];
		perfect = ( cl->ps.persistant[PERS_RANK] == 0 && cl->ps.persistant[PERS_KILLED] == 0 ) ? 1 : 0;

		Com_sprintf( entry, sizeof( entry ),
			" %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i",
			clientNum,
			cl->sess.sessionTeam,
			cl->ps.persistant[PERS_SCORE],
			G_GetScoreboardPing( cl ),
			(level.time - cl->pers.enterTime) / 60000,
			cl->killCount,
			cl->deathCount,
			G_GetClientScoreboardAccuracy( cl ),
			G_GetClientScoreboardWeapon( cl ),
			cl->ps.persistant[PERS_IMPRESSIVE_COUNT],
			cl->ps.persistant[PERS_EXCELLENT_COUNT],
			cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT],
			cl->ps.persistant[PERS_DEFEND_COUNT],
			cl->ps.persistant[PERS_ASSIST_COUNT],
			cl->ps.persistant[PERS_CAPTURES],
			perfect,
			(cl->ps.pm_type == PM_NORMAL) ? 1 : 0 );

		j = strlen( entry );
		if ( stringlength + j + 32 >= payloadSize ) {
			if ( emittedCount ) {
				*emittedCount = emitted;
			}
			return qfalse;
		}

		Q_strcat( payload, payloadSize, entry );
		stringlength += j;
		emitted++;
	}

	if ( emittedCount ) {
		*emittedCount = emitted;
	}

	return qtrue;
}

/*
==================
G_BuildFreezeScoreboardRows

Builds the retail Freeze per-client scoreboard row block.
==================
*/
static qboolean G_BuildFreezeScoreboardRows( char *payload, int payloadSize, int *emittedCount ) {
	char		entry[1024];
	int		stringlength;
	int		i;
	int		emitted;

	payload[0] = '\0';
	stringlength = 0;
	emitted = 0;

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		const int	clientNum = level.sortedClients[i];
		gclient_t	*cl;
		int		j;

		cl = &level.clients[clientNum];
		Com_sprintf( entry, sizeof( entry ),
			" %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i",
			clientNum,
			cl->sess.sessionTeam,
			cl->ps.persistant[PERS_SCORE],
			G_GetScoreboardPing( cl ),
			(level.time - cl->pers.enterTime) / 60000,
			cl->killCount,
			cl->deathCount,
			G_GetClientScoreboardAccuracy( cl ),
			G_GetClientScoreboardWeapon( cl ),
			cl->ps.persistant[PERS_IMPRESSIVE_COUNT],
			cl->ps.persistant[PERS_EXCELLENT_COUNT],
			cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT],
			cl->ps.persistant[PERS_ASSIST_COUNT],
			cl->teamDamageEventsGiven,
			cl->teamDamageEventsReceived,
			cl->pers.damageGiven,
			(cl->ps.pm_type == PM_NORMAL) ? 1 : 0 );

		j = strlen( entry );
		if ( stringlength + j + 32 >= payloadSize ) {
			if ( emittedCount ) {
				*emittedCount = emitted;
			}
			return qfalse;
		}

		Q_strcat( payload, payloadSize, entry );
		stringlength += j;
		emitted++;
	}

	if ( emittedCount ) {
		*emittedCount = emitted;
	}

	return qtrue;
}

/*
==================
G_BuildRichScoreboardMessage

Builds the current full scoreboard payload and reports whether all rows fit
within the retail-sized server command budget.
==================
*/
static qboolean G_BuildRichScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	char		entry[1024];
	int			stringlength;
	int			i;
	int			emitted;

	payload[0] = '\0';
	stringlength = 0;
	emitted = 0;

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		gclient_t	*cl;
		int			accuracy;
		int			perfect;
		int			ping;
		int			j;

		cl = &level.clients[level.sortedClients[i]];
		ping = G_GetScoreboardPing( cl );

		if ( cl->accuracy_shots ) {
			accuracy = cl->accuracy_hits * 100 / cl->accuracy_shots;
		} else {
			accuracy = 0;
		}

		perfect = ( cl->ps.persistant[PERS_RANK] == 0 && cl->ps.persistant[PERS_KILLED] == 0 ) ? 1 : 0;

		Com_sprintf( entry, sizeof( entry ),
			" %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i",
			level.sortedClients[i],
			cl->ps.persistant[PERS_SCORE],
			ping,
			(level.time - cl->pers.enterTime) / 60000,
			0,
			g_entities[level.sortedClients[i]].s.powerups,
			accuracy,
			cl->ps.persistant[PERS_IMPRESSIVE_COUNT],
			cl->ps.persistant[PERS_EXCELLENT_COUNT],
			cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT],
			cl->ps.persistant[PERS_DEFEND_COUNT],
			cl->ps.persistant[PERS_ASSIST_COUNT],
			perfect,
			cl->ps.persistant[PERS_CAPTURES],
			cl->pers.damageGiven,
			cl->ps.persistant[PERS_KILLED] );

		j = strlen( entry );
		if ( stringlength + j + 32 >= payloadSize ) {
			if ( emittedCount ) {
				*emittedCount = emitted;
			}
			return qfalse;
		}

		Q_strcat( payload, payloadSize, entry );
		stringlength += j;
		emitted++;
	}

	if ( emittedCount ) {
		*emittedCount = emitted;
	}

	return qtrue;
}

/*
==================
G_BuildObeliskScoreboardMessage

Builds the retail generic/default scoreboard payload used by Overload and the
legacy fallback command path.
==================
*/
static qboolean G_BuildObeliskScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	return G_BuildRichScoreboardMessage( payload, payloadSize, emittedCount );
}

/*
==================
G_BuildFFAScoreboardMessage

Builds the retail FFA rich scoreboard payload.
==================
*/
static qboolean G_BuildFFAScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	return G_BuildRichScoreboardMessage( payload, payloadSize, emittedCount );
}

/*
==================
G_BuildDuelScoreboardMessage

Caches the retail low/high duel client pair, applies the per-viewer pickup
timing visibility split, and builds the retail scores_duel payload.
==================
*/
static qboolean G_BuildDuelScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	int		numRows;
	int		firstClientNum;
	int		secondClientNum;
	char		lowPublic[MAX_STRING_CHARS];
	char		lowPrivate[MAX_STRING_CHARS];
	char		highPublic[MAX_STRING_CHARS];
	char		highPrivate[MAX_STRING_CHARS];
	const char	*lowRow;
	const char	*highRow;

	level.duelScoreboardLowClientNum = -1;
	level.duelScoreboardHighClientNum = -1;
	if ( emittedCount ) {
		*emittedCount = 0;
	}
	if ( !payload || payloadSize <= 0 ) {
		return qfalse;
	}

	numRows = level.numPlayingClients;
	if ( numRows > 2 ) {
		numRows = 2;
	}
	payload[0] = '\0';
	if ( numRows <= 0 ) {
		return qtrue;
	}

	firstClientNum = level.sortedClients[0];
	secondClientNum = firstClientNum;
	if ( level.numPlayingClients > 1 ) {
		secondClientNum = level.sortedClients[1];
	}

	if ( firstClientNum > secondClientNum ) {
		int swapClientNum;

		swapClientNum = firstClientNum;
		firstClientNum = secondClientNum;
		secondClientNum = swapClientNum;
	}

	level.duelScoreboardLowClientNum = firstClientNum;
	level.duelScoreboardHighClientNum = secondClientNum;

	G_BuildDuelScoreboardRow( lowPublic, sizeof( lowPublic ), level.duelScoreboardLowClientNum, qfalse );
	G_BuildDuelScoreboardRow( lowPrivate, sizeof( lowPrivate ), level.duelScoreboardLowClientNum, qtrue );
	lowRow = G_ShouldRevealDuelScoreboardDetails( g_duelScoreboardViewer, level.duelScoreboardLowClientNum ) ? lowPrivate : lowPublic;

	if ( numRows <= 1 ) {
		if ( strlen( lowRow ) + 2 >= payloadSize ) {
			return qfalse;
		}
		Com_sprintf( payload, payloadSize, " %s", lowRow );
		if ( emittedCount ) {
			*emittedCount = 1;
		}
		return qtrue;
	}

	G_BuildDuelScoreboardRow( highPublic, sizeof( highPublic ), level.duelScoreboardHighClientNum, qfalse );
	G_BuildDuelScoreboardRow( highPrivate, sizeof( highPrivate ), level.duelScoreboardHighClientNum, qtrue );
	highRow = G_ShouldRevealDuelScoreboardDetails( g_duelScoreboardViewer, level.duelScoreboardHighClientNum ) ? highPrivate : highPublic;

	if ( strlen( lowRow ) + strlen( highRow ) + 3 >= payloadSize ) {
		return qfalse;
	}
	Com_sprintf( payload, payloadSize, " %s %s", lowRow, highRow );
	if ( emittedCount ) {
		*emittedCount = 2;
	}

	return qtrue;
}

/*
==================
G_BuildClanArenaScoreboardMessage

Builds the retail Clan Arena scoreboard payload.
==================
*/
static qboolean G_BuildClanArenaScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	char		entry[1024];
	int		stringlength;
	int		i;
	int		emitted;

	payload[0] = '\0';
	stringlength = 0;
	emitted = 0;

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		const int	clientNum = level.sortedClients[i];
		gclient_t	*cl;
		int		perfect;
		int		activePlayer;
		int		j;

		cl = &level.clients[clientNum];
		perfect = ( cl->ps.persistant[PERS_RANK] == 0 && cl->ps.persistant[PERS_KILLED] == 0 ) ? 1 : 0;
		activePlayer = ( cl->sess.sessionTeam != TEAM_SPECTATOR && cl->ps.pm_type == PM_NORMAL ) ? 1 : 0;

		Com_sprintf( entry, sizeof( entry ),
			" %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i",
			clientNum,
			cl->sess.sessionTeam,
			cl->ps.persistant[PERS_SCORE],
			G_GetScoreboardPing( cl ),
			(level.time - cl->pers.enterTime) / 60000,
			cl->killCount,
			cl->deathCount,
			G_GetClientScoreboardAccuracy( cl ),
			G_GetClientScoreboardWeapon( cl ),
			0,
			cl->pers.damageGiven,
			cl->ps.persistant[PERS_IMPRESSIVE_COUNT],
			cl->ps.persistant[PERS_EXCELLENT_COUNT],
			cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT],
			perfect,
			activePlayer );

		j = strlen( entry );
		if ( stringlength + j + 32 >= payloadSize ) {
			if ( emittedCount ) {
				*emittedCount = emitted;
			}
			return qfalse;
		}

		Q_strcat( payload, payloadSize, entry );
		stringlength += j;
		emitted++;
	}

	if ( emittedCount ) {
		*emittedCount = emitted;
	}

	return qtrue;
}

/*
==================
G_BuildRedRoverScoreboardMessage

Builds the retail Red Rover scoreboard payload.
==================
*/
static qboolean G_BuildRedRoverScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	char		entry[1024];
	int		stringlength;
	int		i;
	int		emitted;

	payload[0] = '\0';
	stringlength = 0;
	emitted = 0;

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		const int	clientNum = level.sortedClients[i];
		gclient_t	*cl;
		int		activePlayer;
		int		j;

		cl = &level.clients[clientNum];
		activePlayer = ( cl->sess.sessionTeam != TEAM_SPECTATOR && cl->ps.pm_type == PM_NORMAL ) ? 1 : 0;

		Com_sprintf( entry, sizeof( entry ),
			" %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i %i",
			clientNum,
			cl->ps.persistant[PERS_SCORE],
			0,
			G_GetScoreboardPing( cl ),
			(level.time - cl->pers.enterTime) / 60000,
			cl->killCount,
			cl->deathCount,
			G_GetClientScoreboardAccuracy( cl ),
			G_GetClientScoreboardWeapon( cl ),
			0,
			cl->pers.damageGiven,
			cl->ps.persistant[PERS_IMPRESSIVE_COUNT],
			cl->ps.persistant[PERS_EXCELLENT_COUNT],
			cl->ps.persistant[PERS_GAUNTLET_FRAG_COUNT],
			cl->ps.persistant[PERS_DEFEND_COUNT],
			cl->ps.persistant[PERS_ASSIST_COUNT],
			activePlayer,
			cl->ps.persistant[PERS_CAPTURES],
			0 );

		j = strlen( entry );
		if ( stringlength + j + 32 >= payloadSize ) {
			if ( emittedCount ) {
				*emittedCount = emitted;
			}
			return qfalse;
		}

		Q_strcat( payload, payloadSize, entry );
		stringlength += j;
		emitted++;
	}

	if ( emittedCount ) {
		*emittedCount = emitted;
	}

	return qtrue;
}

/*
==================
G_BuildCompactScoreboardMessage

Builds the retail compact smscores payload used when the full scoreboard would
overflow or the server forces the compact path.
==================
*/
static qboolean G_BuildCompactScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {
	char		entry[256];
	int			stringlength;
	int			i;
	int			emitted;

	payload[0] = '\0';
	stringlength = 0;
	emitted = 0;

	for ( i = 0; i < level.numConnectedClients; i++ ) {
		gclient_t	*cl;
		int			ping;
		int			j;

		cl = &level.clients[level.sortedClients[i]];
		ping = G_GetScoreboardPing( cl );

		Com_sprintf( entry, sizeof( entry ),
			" %i %i %i %i %i %i %i %i",
			level.sortedClients[i],
			cl->ps.persistant[PERS_SCORE],
			ping,
			(level.time - cl->pers.enterTime) / 60000,
			g_entities[level.sortedClients[i]].s.powerups,
			(cl->ps.pm_type == PM_NORMAL) ? 1 : 0,
			cl->pers.damageGiven,
			cl->ps.persistant[PERS_KILLED] );

		j = strlen( entry );
		if ( stringlength + j + 32 >= payloadSize ) {
			if ( emittedCount ) {
				*emittedCount = emitted;
			}
			return qfalse;
		}

		Q_strcat( payload, payloadSize, entry );
		stringlength += j;
		emitted++;
	}

	if ( emittedCount ) {
		*emittedCount = emitted;
	}

	return qtrue;
}

/*
==================
DeathmatchScoreboardMessage

==================
*/
void DeathmatchScoreboardMessage( gentity_t *ent ) {
	char		string[MAX_STRING_CHARS];
	int			emittedCount = 0;
	qboolean	useCompact;
	const char	*cmd;

	if ( g_gametype.integer == GT_RACE ) {
		G_BuildRaceScoreboardMessage( ent );
		return;
	}

	g_duelScoreboardViewer = ent;

	switch ( g_gametype.integer ) {
	case GT_FFA:
		cmd = "scores_ffa";
		break;
	case GT_TOURNAMENT:
		cmd = "scores_duel";
		break;
	case GT_OBELISK:
		cmd = "scores";
		break;
	case GT_TEAM:
		cmd = "scores_tdm";
		break;
	case GT_CLAN_ARENA:
		cmd = "scores_ca";
		break;
	case GT_CTF:
	case GT_1FCTF:
	case GT_HARVESTER:
	case GT_DOMINATION:
		cmd = "scores_ctf";
		break;
	case GT_ATTACK_DEFEND:
		cmd = "scores_ad";
		break;
	case GT_FREEZE:
		cmd = "scores_ft";
		break;
	case GT_RED_ROVER:
		cmd = "scores_rr";
		break;
	default:
		cmd = "scores";
		break;
	}

	useCompact = g_forceSmallScoreboardMessage.integer ? qtrue : qfalse;
	if ( !useCompact ) {
		switch ( g_gametype.integer ) {
		case GT_FFA:
			useCompact = G_BuildFFAScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		case GT_TOURNAMENT:
			useCompact = G_BuildDuelScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		case GT_OBELISK:
			useCompact = G_BuildObeliskScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		case GT_TEAM:
			useCompact = G_BuildTeamScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		case GT_CLAN_ARENA:
			useCompact = G_BuildClanArenaScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		case GT_CTF:
		case GT_1FCTF:
		case GT_HARVESTER:
		case GT_DOMINATION:
		case GT_ATTACK_DEFEND:
			useCompact = G_BuildCTFStyleScoreboardMessage( ent, string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		case GT_FREEZE:
			useCompact = G_BuildFreezeScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		case GT_RED_ROVER:
			useCompact = G_BuildRedRoverScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		default:
			useCompact = G_BuildRichScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;
			break;
		}
	}

	if ( useCompact ) {
		G_BuildCompactScoreboardMessage( string, sizeof( string ), &emittedCount );
		trap_SendServerCommand( ent-g_entities, va( "smscores %i %i %i%s",
			emittedCount,
			level.teamScores[TEAM_RED],
			level.teamScores[TEAM_BLUE],
			string ) );
	} else {
		if ( g_gametype.integer == GT_TEAM || g_gametype.integer == GT_FREEZE || G_IsCTFStyleScoreboardGametype() ) {
			trap_SendServerCommand( ent-g_entities, va( "%s%s", cmd, string ) );
		} else if ( g_gametype.integer == GT_TOURNAMENT ) {
			trap_SendServerCommand( ent-g_entities, va( "%s %i%s", cmd, emittedCount, string ) );
		} else {
			trap_SendServerCommand( ent-g_entities, va( "%s %i %i %i%s",
				cmd,
				emittedCount,
				level.teamScores[TEAM_RED],
				level.teamScores[TEAM_BLUE],
				string ) );
		}
	}

	G_SendScoreStatsMessage( ent );
	G_SendTeamScoreStatsMessage( ent );
	if ( level.intermissiontime ) {
		if ( g_gametype.integer == GT_TEAM || g_gametype.integer == GT_FREEZE ) {
			G_SendTDMStatsMessage( ent );
		}
		if ( g_gametype.integer == GT_CLAN_ARENA ) {
			G_SendCAStatsMessage( ent );
		}
		if ( G_IsCTFStyleScoreboardGametype() ) {
			G_SendCTFStatsMessage( ent );
		}
	}
	G_SendAllClientKeyMasks( ent - g_entities );
	g_duelScoreboardViewer = NULL;
}


/*
==================
Cmd_Score_f

Request current scoreboard information
==================
*/
void Cmd_Score_f( gentity_t *ent ) {
	if ( g_gametype.integer == GT_RACE ) {
		G_RaceSendScoreboard( ent );
		return;
	}

	DeathmatchScoreboardMessage( ent );
}

/*
==================
Team_CountsBalanced

Returns qtrue when the red/blue roster spread is no greater than one player.
==================
*/
static qboolean Team_CountsBalanced( int redCount, int blueCount ) {
	int		delta;

	delta = redCount - blueCount;
	if ( delta < 0 ) {
		delta = -delta;
	}

	return ( delta <= 1 ) ? qtrue : qfalse;
}

/*
==================
G_GametypeRequiresBothTeamsPresent

Returns qtrue for retail warmup modes that deny ready-up until both teams exist.
==================
*/
static qboolean G_GametypeRequiresBothTeamsPresent( void ) {
	switch ( g_gametype.integer ) {
	case GT_TEAM:
	case GT_CLAN_ARENA:
	case GT_CTF:
	case GT_1FCTF:
	case GT_OBELISK:
	case GT_HARVESTER:
	case GT_FREEZE:
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
==================
G_RRResolveAutoJoinTeam

Selects the retail Red Rover auto-join target while ensuring both infection teams can seed.
==================
*/
static team_t G_RRResolveAutoJoinTeam( int clientNum ) {
	if ( g_gametype.integer != GT_RED_ROVER || !g_rrInfected.integer ) {
		return PickTeam( clientNum );
	}

	G_RRResolveRoundState();
	if ( clientNum == level.rrSelectedInfectedClientNum
		|| clientNum == level.rrCarryoverInfectedClientNum ) {
		return TEAM_RED;
	}

	return TEAM_BLUE;
}

/*
==================
G_ResetTrainingSession

Restores the retail tutorial reset path that hangs off `readyup`.
==================
*/
static void G_ResetTrainingSession( gentity_t *ent ) {
	int			i;
	gentity_t	*player;
	gclient_t	*client;

	trap_Cvar_Set( "g_training", "1" );
	trap_Cvar_Set( "bot_training", "0" );
	trap_Cvar_Set( "bot_dynamicSkill", "1" );
	trap_Cvar_Set( "bot_followMe", "0" );
	trap_Cvar_Set( "bot_gauntlet", "0" );
	trap_Cvar_Set( "g_skipTrainingEnable", "0" );
	trap_Cvar_Update( &g_training );
	level.trainingMapActive = ( g_training.integer != 0 ) ? qtrue : qfalse;

	for ( i = 0; i < level.maxclients; i++ ) {
		player = &g_entities[i];
		client = player->client;
		if ( !client || client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		G_SetClientReadyState( client, qfalse );
		client->ps.eFlags &= ~( EF_PLAYER_EVENT | EF_AWARD_ASSIST );
		if ( player->r.svFlags & SVF_BOT ) {
			client->ps.eFlags &= ~EF_AWARD_DEFEND;
		}

		ClientSpawn( player );
	}

	trap_SendServerCommand( ent - g_entities, "clearChat" );
	trap_SendServerCommand( ent - g_entities, "clearSounds" );
}

/*
==================
G_GetReadyUpBlockedMessage

Returns a retail-aligned denial string when warmup cannot accept ready-up state.
==================
*/
static const char *G_GetReadyUpBlockedMessage( void ) {
	int redCount;
	int blueCount;
	int required;

	if ( level.warmupTime == 0 ) {
		return "print \"The match has already started.\n\"";
	}

	if ( Team_HasMinimumPlayersForWarmup() ) {
		return NULL;
	}

	if ( !G_GametypeRequiresBothTeamsPresent() ) {
		return "print \"Cannot ready up until more players are present.\n\"";
	}

	redCount = TeamCount( -1, TEAM_RED );
	blueCount = TeamCount( -1, TEAM_BLUE );
	if ( redCount < 1 || blueCount < 1 ) {
		return "print \"Players cannot ready up until both teams are present.\n\"";
	}

	if ( g_teamForceBalance.integer && !Team_CountsBalanced( redCount, blueCount ) ) {
		return "print \"Cannot ready up until more players are present.\n\"";
	}

	required = g_teamSizeMin.integer;
	if ( required < 0 ) {
		required = 0;
	}

	if ( required > 1 && g_teamForcePresent.integer && ( redCount < required || blueCount < required ) ) {
		return "print \"Players cannot ready up until both teams are fully present.\n\"";
	}

	return "print \"Cannot ready up until more players are present.\n\"";
}

/*
==================
Cmd_Ready_f
==================
*/
void Cmd_Ready_f( gentity_t *ent ) {
	const char *blockedMessage;

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot ready up.\n\"" );
		return;
	}

	blockedMessage = G_GetReadyUpBlockedMessage();
	if ( blockedMessage ) {
		trap_SendServerCommand( ent-g_entities, blockedMessage );
		return;
	}

	if ( G_ClientIsReady( ent->client ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"You are already ready.\n\"" );
		return;
	}

	G_SetClientReadyState( ent->client, qtrue );
	G_WarmupReadyToStart();
	trap_SendServerCommand( ent-g_entities, "print \"You are now ready.\n\"" );
}

/*
==================
Cmd_ReadyUp_f
==================
*/
void Cmd_ReadyUp_f( gentity_t *ent ) {
	const char *blockedMessage;
	qboolean	ready;

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot ready up.\n\"" );
		return;
	}

	if ( ( level.warmupTime < 0 || level.intermissiontime != 0 ) &&
		g_training.integer != 0 && ent->client->pers.localClient ) {
		G_ResetTrainingSession( ent );
	}

	if ( level.warmupTime < 0 && !Team_HasMinimumPlayersForWarmup() && G_ClientIsReady( ent->client ) ) {
		G_SetClientReadyState( ent->client, qfalse );
		ClientUserinfoChanged( ent - g_entities );
		return;
	}

	blockedMessage = G_GetReadyUpBlockedMessage();
	if ( blockedMessage ) {
		trap_SendServerCommand( ent-g_entities, blockedMessage );
		return;
	}

	if ( level.intermissiontime != 0 && G_ClientIsReady( ent->client ) ) {
		return;
	}

	ready = G_ClientIsReady( ent->client ) ? qfalse : qtrue;
	G_SetClientReadyState( ent->client, ready );
	ClientUserinfoChanged( ent - g_entities );
	G_WarmupReadyToStart();

	if ( level.warmupTime < 0 ) {
		trap_SendServerCommand( -1, va( "cp \"%s ^7is ^7%s\n\"",
			ent->client->pers.netname, ready ? "Ready" : "Not Ready" ) );
		return;
	}

	if ( ready ) {
		trap_SendServerCommand( ent-g_entities, "print \"You are now ^2READY^7.\n\"" );
	} else {
		trap_SendServerCommand( ent-g_entities, "print \"You are now ^1NOT ^7ready.\n\"" );
	}
}

/*
==================
Cmd_NotReady_f
==================
*/
void Cmd_NotReady_f( gentity_t *ent ) {
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot ready up.\n\"" );
		return;
	}

	if ( level.warmupTime <= 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"The match has already started.\n\"" );
		return;
	}

	if ( !G_ClientIsReady( ent->client ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"You are already not ready.\n\"" );
		return;
	}

	G_SetClientReadyState( ent->client, qfalse );
	G_WarmupReadyToStart();
	trap_SendServerCommand( ent-g_entities, "print \"You are now not ready.\n\"" );
}

/*
==================
Cmd_Players_f
==================
*/
void Cmd_Players_f( gentity_t *ent ) {
	int		i;
	gclient_t	*cl;
	int		score;
	int		ping;
	char	*s;
	char	cleanName[MAX_NETNAME];

	trap_SendServerCommand( ent-g_entities, "print \"  ID Score Ping Name            \n\"" );
	trap_SendServerCommand( ent-g_entities, "print \"------------------------------\n\"" );

	for ( i=0 ; i < level.maxclients ; i++ ) {
		cl = &level.clients[i];
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}

		score = cl->ps.persistant[PERS_SCORE];
		ping = cl->ps.ping < 999 ? cl->ps.ping : 999;

		// QL style output
		s = cl->pers.netname;
		// sanitize name for display if needed
		Q_strncpyz( cleanName, s, sizeof(cleanName) );
		Q_CleanStr( cleanName );

		trap_SendServerCommand( ent-g_entities, va("print \"  %2i %5i %4i %s\n\"",
			i, score, ping, cleanName) );
	}
}

/*
==================
Cmd_Teams_f
==================
*/
void Cmd_Teams_f( gentity_t *ent ) {
	if ( g_gametype.integer < GT_TEAM ) {
		trap_SendServerCommand( ent-g_entities, "print \"Teams are not enabled in this gametype.\n\"" );
		return;
	}

	trap_SendServerCommand( ent-g_entities, va("print \"Red Team: %i\n\"", level.teamScores[TEAM_RED] ) );
	trap_SendServerCommand( ent-g_entities, va("print \"Blue Team: %i\n\"", level.teamScores[TEAM_BLUE] ) );
}

/*
=================
G_RetailAccuracySourceClient

Resolves the retail accuracy source, following the chased client when a
spectator requests `acc` or `pstats`.
=================
*/
static gclient_t *G_RetailAccuracySourceClient( gentity_t *ent ) {
	int clientNum;

	if ( !ent || !ent->client ) {
		return NULL;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR &&
			ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
		clientNum = ent->client->sess.spectatorClient;
		if ( clientNum >= 0 && clientNum < level.maxclients &&
				level.clients[clientNum].pers.connected == CON_CONNECTED ) {
			return &level.clients[clientNum];
		}
	}

	return ent->client;
}

/*
=================
G_SendRetailAccuracyPayloadCommand

Builds the retail compact `acc` / `pstats` payload across the fixed
weapon-order slab.
=================
*/
static void G_SendRetailAccuracyPayloadCommand( gentity_t *ent, const char *command ) {
	gclient_t	*client;
	char		payload[256];
	char		entry[16];
	int		accuracy;
	int		hits;
	int		i;
	int		shots;
	weapon_t	weapon;

	if ( !ent ) {
		return;
	}

	client = G_RetailAccuracySourceClient( ent );
	if ( !client ) {
		return;
	}

	payload[0] = '\0';
	for ( i = 0; i < ARRAY_LEN( retailAccuracyCommandOrder ); i++ ) {
		weapon = retailAccuracyCommandOrder[i];
		accuracy = 0;

		if ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
			hits = client->pers.accuracy_hits[weapon];
			shots = client->pers.accuracy_shots[weapon];
			if ( hits > 0 && shots > 0 ) {
				accuracy = hits * 100 / shots;
			}
		}

		Com_sprintf( entry, sizeof( entry ), " %i", accuracy );
		Q_strcat( payload, sizeof( payload ), entry );
	}

	trap_SendServerCommand( ent-g_entities, va( "%s %s", command, payload ) );
}

/*
=================
G_SendRetailAccuracyCommand
=================
*/
static void G_SendRetailAccuracyCommand( gentity_t *ent ) {
	G_SendRetailAccuracyPayloadCommand( ent, "acc" );
}

/*
=================
G_SendRetailPStatsCommand
=================
*/
static void G_SendRetailPStatsCommand( gentity_t *ent ) {
	G_SendRetailAccuracyPayloadCommand( ent, "pstats" );
}

/*
=================
Cmd_Acc_f
=================
*/
void Cmd_Acc_f( gentity_t *ent ) {
	G_SendRetailAccuracyCommand( ent );
}

/*
=================
Cmd_PStats_f
=================
*/
void Cmd_PStats_f( gentity_t *ent ) {
	G_SendRetailPStatsCommand( ent );
}

/*
=================
Cmd_Cvar_f
=================
*/
void Cmd_Cvar_f( gentity_t *ent ) {
	char	arg[MAX_TOKEN_CHARS];
	char	val[MAX_TOKEN_CHARS];

	if ( trap_Argc() != 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: cvar <cvarname>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );

	// only allow checking safe cvars
	if ( Q_stricmp( arg, "g_gametype" ) &&
		 Q_stricmp( arg, "timelimit" ) &&
		 Q_stricmp( arg, "fraglimit" ) &&
		 Q_stricmp( arg, "capturelimit" ) &&
		 Q_stricmp( arg, "g_friendlyFire" ) &&
		 Q_stricmp( arg, "g_gravity" ) &&
		 Q_stricmp( arg, "g_speed" ) &&
		 Q_stricmp( arg, "g_knockback" ) &&
		 Q_stricmp( arg, "g_quadfactor" ) &&
		 Q_stricmp( arg, "g_weaponRespawn" ) &&
		 Q_stricmp( arg, "g_forcerespawn" ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Cvar is not public.\n\"" );
		return;
	}

	trap_Cvar_VariableStringBuffer( arg, val, sizeof( val ) );
	trap_SendServerCommand( ent-g_entities, va("print \"Cvar %s = %s\n\"", arg, val) );
}


/*
==================
CheatsOk
==================
*/
qboolean	CheatsOk( gentity_t *ent ) {
	if ( !g_cheats.integer ) {
		trap_SendServerCommand( ent-g_entities, va("print \"Cheats are not enabled on this server.\n\""));
		return qfalse;
	}
	if ( ent->health <= 0 ) {
		trap_SendServerCommand( ent-g_entities, va("print \"You must be alive to use this command.\n\""));
		return qfalse;
	}
	return qtrue;
}


/*
==================
ConcatArgs
==================
*/
char	*ConcatArgs( int start ) {
	int		i, c, tlen;
	static char	line[MAX_STRING_CHARS];
	int		len;
	char	arg[MAX_STRING_CHARS];

	len = 0;
	c = trap_Argc();
	for ( i = start ; i < c ; i++ ) {
		trap_Argv( i, arg, sizeof( arg ) );
		tlen = strlen( arg );
		if ( len + tlen >= MAX_STRING_CHARS - 1 ) {
			break;
		}
		memcpy( line + len, arg, tlen );
		len += tlen;
		if ( i != c - 1 ) {
			line[len] = ' ';
			len++;
		}
	}

	line[len] = 0;

	return line;
}

/*
============
G_FloodLimited

Tracks command flood usage against the retail shared counter. Active-client
code performs the actual drop once the count exceeds the limit.
============
*/
static qboolean G_FloodLimited( gentity_t *ent, const char *action, qboolean recordUsage ) {
	gclient_t		*client;
	const char	*label;
	int		maxCount;
	int		decay;

	if ( !ent || !ent->client ) {
		return qfalse;
	}

	maxCount = g_floodprot_maxcount.integer;
	decay = g_floodprot_decay.integer;
	if ( maxCount <= 0 || decay <= 0 ) {
		return qfalse;
	}

	client = ent->client;
	label = ( action && action[0] ) ? action : "issuing commands";
	client->floodPenaltyTime = 0;

	if ( client->floodCount > maxCount ) {
		G_LogPrintf( "floodprot: client %i (%s) pending drop via %s\n",
			ent - g_entities, client->pers.netname, label );
		return qtrue;
	}

	if ( !recordUsage ) {
		return qfalse;
	}

	client->floodLastTime = level.time;
	client->floodCount++;
	if ( client->floodCount > maxCount ) {
		G_LogPrintf( "floodprot: client %i (%s) exceeded limit via %s\n",
			ent - g_entities, client->pers.netname, label );
		return qtrue;
	}

	return qfalse;
}
/*
=============
G_ClampItemTimerHeight

Ensures the timer height sent to clients always uses a sensible fallback and sane upper bound.
=============
*/
static int G_ClampItemTimerHeight( int rawHeight ) {
	if ( rawHeight <= 0 ) {
		return ITEM_TIMER_DEFAULT_HEIGHT;
	}

	if ( rawHeight > ITEM_TIMER_MAX_HEIGHT ) {
		return ITEM_TIMER_MAX_HEIGHT;
	}

	return rawHeight;
}


/*
=============
G_SendItemTimerState

Sends the current item timer configuration to a single client.
=============
*/
void G_SendItemTimerState( int clientNum, int enabled, int height ) {
	int	clampedHeight;

	clampedHeight = G_ClampItemTimerHeight( height );
	trap_SendServerCommand( clientNum, va( "itemcfg %i %i", enabled ? 1 : 0, clampedHeight ) );
}

/*
=============
G_BroadcastItemTimerState

Broadcasts the current item timer configuration to every connected client.
=============
*/
void G_BroadcastItemTimerState( int enabled, int height ) {
	G_SendItemTimerState( -1, enabled, height );
}


/*
==================
SanitizeString

Remove case and control characters
==================
*/
void SanitizeString( char *in, char *out ) {
	while ( *in ) {
		if ( *in == 27 ) {
			in += 2;		// skip color code
			continue;
		}
		if ( *in < 32 ) {
			in++;
			continue;
		}
		*out++ = tolower( *in++ );
	}

	*out = 0;
}

/*
==================
ClientNumberFromString

Returns a player number for either a number or name string
Returns -1 if invalid
==================
*/
int ClientNumberFromString( gentity_t *to, char *s ) {
	gclient_t	*cl;
	int			idnum;
	char		s2[MAX_STRING_CHARS];
	char		n2[MAX_STRING_CHARS];

	// numeric values are just slot numbers
	if (s[0] >= '0' && s[0] <= '9') {
		idnum = atoi( s );
		if ( idnum < 0 || idnum >= level.maxclients ) {
			trap_SendServerCommand( to-g_entities, va("print \"Bad client slot: %i\n\"", idnum));
			return -1;
		}

		cl = &level.clients[idnum];
		if ( cl->pers.connected != CON_CONNECTED ) {
			trap_SendServerCommand( to-g_entities, va("print \"Client %i is not active\n\"", idnum));
			return -1;
		}
		return idnum;
	}

	// check for a name match
	SanitizeString( s, s2 );
	for ( idnum=0,cl=level.clients ; idnum < level.maxclients ; idnum++,cl++ ) {
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		SanitizeString( cl->pers.netname, n2 );
		if ( !strcmp( n2, s2 ) ) {
			return idnum;
		}
	}

	trap_SendServerCommand( to-g_entities, va("print \"User %s is not on the server\n\"", s));
	return -1;
}


/*
=============
G_GiveItemByName

Grants inventory matching the `give` command tokens so non-cheat code paths can reuse the logic.
=============
*/
qboolean G_GiveItemByName( gentity_t *ent, const char *name ) {
	gitem_t		*it;
	gentity_t	*it_ent;
	trace_t	trace;
	int			 i;

	if ( !ent || !ent->client || !name || !name[0] ) {
		return qfalse;
	}

	if ( Q_stricmp( name, "health" ) == 0 ) {
		ent->health = ent->client->ps.stats[STAT_MAX_HEALTH];
		return qtrue;
	}

	if ( Q_stricmp( name, "weapons" ) == 0 ) {
		ent->client->ps.stats[STAT_WEAPONS] = ( 1 << WP_NUM_WEAPONS ) - 1 - ( 1 << WP_GRAPPLING_HOOK ) - ( 1 << WP_NONE );
		return qtrue;
	}

	if ( Q_stricmp( name, "ammo" ) == 0 ) {
		for ( i = 0 ; i < MAX_WEAPONS ; i++ ) {
			ent->client->ps.ammo[i] = 999;
		}
		return qtrue;
	}

	if ( Q_stricmp( name, "armor" ) == 0 ) {
		ent->client->ps.stats[STAT_ARMOR] = 200;
		BG_UpdateArmorTierFromCurrentArmor( &ent->client->ps, g_armorTiered.integer ? qtrue : qfalse );
		return qtrue;
	}

	if ( Q_stricmp( name, "excellent" ) == 0 ) {
		ent->client->ps.persistant[PERS_EXCELLENT_COUNT]++;
		G_RankSendPlayerMedal( ent, "EXCELLENT" );
		return qtrue;
	}
	if ( Q_stricmp( name, "impressive" ) == 0 ) {
		ent->client->ps.persistant[PERS_IMPRESSIVE_COUNT]++;
		G_RankSendPlayerMedal( ent, "IMPRESSIVE" );
		return qtrue;
	}
	if ( Q_stricmp( name, "gauntletaward" ) == 0 ) {
		ent->client->ps.persistant[PERS_GAUNTLET_FRAG_COUNT]++;
		G_RankSendPlayerMedal( ent, "GAUNTLET" );
		return qtrue;
	}
	if ( Q_stricmp( name, "defend" ) == 0 ) {
		ent->client->ps.persistant[PERS_DEFEND_COUNT]++;
		G_RankSendPlayerMedal( ent, "DEFENDS" );
		return qtrue;
	}
	if ( Q_stricmp( name, "assist" ) == 0 ) {
		ent->client->ps.persistant[PERS_ASSIST_COUNT]++;
		G_RankSendPlayerMedal( ent, "ASSISTS" );
		return qtrue;
	}

	it = BG_FindItem( name );
	if ( !it ) {
		return qfalse;
	}

	it_ent = G_Spawn();
	VectorCopy( ent->r.currentOrigin, it_ent->s.origin );
	it_ent->classname = it->classname;
	G_SpawnItem( it_ent, it );
	FinishSpawningItem( it_ent );
	memset( &trace, 0, sizeof( trace ) );
	Touch_Item( it_ent, ent, &trace );
	if ( it_ent->inuse ) {
		G_FreeEntity( it_ent );
	}

	return qtrue;
}

/*
==================
Cmd_Give_f

Give items to a client
==================
*/
void Cmd_Give_f (gentity_t *ent)
{
	char			*name;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	name = ConcatArgs( 1 );
	if ( !name[0] ) {
		return;
	}

	if ( Q_stricmp( name, "all" ) == 0 ) {
		G_GiveItemByName( ent, "health" );
		G_GiveItemByName( ent, "weapons" );
		G_GiveItemByName( ent, "ammo" );
		G_GiveItemByName( ent, "armor" );
		return;
	}

	G_GiveItemByName( ent, name );
}


/*
==================
Cmd_God_f

Sets client to godmode

argv(0) god
==================
*/
void Cmd_God_f (gentity_t *ent)
{
	char	*msg;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	ent->flags ^= FL_GODMODE;
	if (!(ent->flags & FL_GODMODE) )
		msg = "godmode OFF\n";
	else
		msg = "godmode ON\n";

	trap_SendServerCommand( ent-g_entities, va("print \"%s\"", msg));
}

/*
==================
Cmd_Notarget_f

Sets client to notarget

argv(0) notarget
==================
*/
void Cmd_Notarget_f( gentity_t *ent ) {
	char	*msg;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	ent->flags ^= FL_NOTARGET;
	if (!(ent->flags & FL_NOTARGET) )
		msg = "notarget OFF\n";
	else
		msg = "notarget ON\n";

	trap_SendServerCommand( ent-g_entities, va("print \"%s\"", msg));
}


/*
==================
Cmd_Noclip_f

argv(0) noclip
==================
*/
void Cmd_Noclip_f( gentity_t *ent ) {
	char	*msg;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	if ( ent->client->noclip ) {
		msg = "noclip OFF\n";
	} else {
		msg = "noclip ON\n";
	}
	ent->client->noclip = !ent->client->noclip;

	trap_SendServerCommand( ent-g_entities, va("print \"%s\"", msg));
}


/*
============
Cmd_ThawTarget_f

Cheat helper that lets developers thaw a frozen teammate directly by slot.
============
*/
static void Cmd_ThawTarget_f( gentity_t *ent ) {
	char	arg[MAX_TOKEN_CHARS];
	int		targetNum;
	gentity_t	*target;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( !G_FreezeGametypeEnabled() ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_FREEZE_ONLY "\"" );
		G_LogPrintf( "cmd: thawtarget denied outside Freeze for client %i\n", ent->client->ps.clientNum );
		return;
	}

	if ( !CheatsOk( ent ) ) {
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget missing argument from client %i\n", ent->client->ps.clientNum );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	targetNum = atoi( arg );
	if ( targetNum < 0 || targetNum >= level.maxclients ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget invalid slot %s from client %i\n", arg, ent->client->ps.clientNum );
		return;
	}

	target = &g_entities[targetNum];
	if ( !target->inuse || !target->client || target->client->pers.connected != CON_CONNECTED ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget unavailable client %i requested by %i\n", targetNum, ent->client->ps.clientNum );
		return;
	}

	if ( target->client->sess.sessionTeam != TEAM_RED && target->client->sess.sessionTeam != TEAM_BLUE ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget non-team target %i requested by %i\n", targetNum, ent->client->ps.clientNum );
		return;
	}

	if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR && ent->client->sess.sessionTeam != target->client->sess.sessionTeam ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget team mismatch client %i target %i\n", ent->client->ps.clientNum, targetNum );
		return;
	}

	if ( !target->client->freezeFrozen ) {
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_THAW_INVALID_TARGET "\"" );
		G_LogPrintf( "cmd: thawtarget requested for non-frozen client %i by %i\n", targetNum, ent->client->ps.clientNum );
		return;
	}

	G_FreezeThawClient( target, qfalse, ent - g_entities );
	G_LogPrintf( "cmd: thawtarget thawed client %i via client %i\n", targetNum, ent->client->ps.clientNum );
}

/*
==================
Cmd_LevelShot_f

This is just to help generate the level pictures
for the menus.  It goes to the intermission immediately
and sends over a command to the client to resize the view,
hide the scoreboard, and take a special screenshot
==================
*/
void Cmd_LevelShot_f( gentity_t *ent ) {
	if ( !CheatsOk( ent ) ) {
		return;
	}

	// doesn't work in single player
	if ( g_gametype.integer != 0 ) {
		trap_SendServerCommand( ent-g_entities, 
			"print \"Must be in g_gametype 0 for levelshot\n\"" );
		return;
	}

	BeginIntermission();
	trap_SendServerCommand( ent-g_entities, "clientLevelShot" );
}


void Cmd_TeamTask_f( gentity_t *ent ) {
	char userinfo[MAX_INFO_STRING];
	char		arg[MAX_TOKEN_CHARS];
	int task;
	int client = ent->client - level.clients;

	if ( trap_Argc() != 2 ) {
		return;
	}
	trap_Argv( 1, arg, sizeof( arg ) );
	task = atoi( arg );

	trap_GetUserinfo(client, userinfo, sizeof(userinfo));
	Info_SetValueForKey(userinfo, "teamtask", va("%d", task));
	trap_SetUserinfo(client, userinfo);
	ClientUserinfoChanged(client);
}



/*
=============
G_IsRoundCountdownActive
=============
*/
static qboolean G_IsRoundCountdownActive( void ) {
	if ( level.roundTransitionTime != ROUND_TRANSITION_NONE
		&& level.roundTransitionTime > level.time ) {
		return qtrue;
	}

	return qfalse;
}


/*
=============
G_ForfeitGametypeName
=============
*/
static const char *G_ForfeitGametypeName( int gametype ) {
	static const char *const s_forfeitGametypeNames[] = {
		"Free For All",
		"Duel",
		"Race",
		"Team Deathmatch",
		"Clan Arena",
		"Capture the Flag",
		"One Flag CTF",
		"Overload",
		"Harvester",
		"Freeze Tag",
		"Domination",
		"Attack and Defend",
		"Red Rover"
	};

	if ( gametype >= 0 && gametype < (int)( sizeof( s_forfeitGametypeNames ) / sizeof( s_forfeitGametypeNames[0] ) ) ) {
		return s_forfeitGametypeNames[gametype];
	}

	return "Unknown Gametype";
}


/*
=============
G_CanForfeit

Mirrors the retail shared forfeit gate used by both the client command path
and the automatic exit-rule checks.
=============
*/
qboolean G_CanForfeit( gentity_t *ent, qboolean fromCommand ) {
	int			gametype;
	const char	*gametypeName;
	team_t		team;
	int			redScore;
	int			blueScore;
	int			redPlayerCount;
	int			bluePlayerCount;
	gclient_t		*opponent;
	int			opponentScore;
	int			i;

	gametype = g_gametype.integer;
	gametypeName = G_ForfeitGametypeName( gametype );

	if ( !fromCommand ) {
		if ( level.time - level.startTime <= 60000 ) {
			return qfalse;
		}

		if ( level.warmupTime != 0 || level.intermissionQueued != 0 || level.intermissiontime != 0 ) {
			return qfalse;
		}

		if ( G_IsRoundCountdownActive() ) {
			return qfalse;
		}

		if ( gametype == GT_TOURNAMENT || gametype == GT_RED_ROVER ) {
			return ( level.numPlayingClients < 2 ) ? qtrue : qfalse;
		}

		if ( gametype < GT_TEAM ) {
			return qfalse;
		}

		redPlayerCount = TeamCount( -1, TEAM_RED );
		bluePlayerCount = TeamCount( -1, TEAM_BLUE );
		return ( redPlayerCount < 1 || bluePlayerCount < 1 ) ? qtrue : qfalse;
	}

	if ( !ent || !ent->client ) {
		return qfalse;
	}

	if ( g_allowForfeit.integer <= 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeits are not enabled on this server.\\n\"" );
		return qfalse;
	}

	if ( level.warmupTime != 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is not available in warmup.\\n\"" );
		return qfalse;
	}

	if ( gametype == GT_FFA || gametype == GT_RACE || gametype == GT_RED_ROVER ) {
		trap_SendServerCommand( ent-g_entities, va( "print \"Forfeit is not available in %s.\\n\"", gametypeName ) );
		return qfalse;
	}

	if ( gametype >= GT_TEAM ) {
		team = ent->client->sess.sessionTeam;
		if ( team != TEAM_RED && team != TEAM_BLUE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to members of the losing team.\\n\"" );
			return qfalse;
		}

		redScore = level.teamScores[TEAM_RED];
		blueScore = level.teamScores[TEAM_BLUE];

		if ( redScore < blueScore ) {
			if ( team != TEAM_RED ) {
				trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to members of the losing team.\\n\"" );
				return qfalse;
			}

			if ( TeamCount( ent->client->ps.clientNum, TEAM_RED ) > 0 ) {
				trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to the last remaining player on the losing team.\\n\"" );
				return qfalse;
			}

			return qtrue;
		}

		if ( blueScore < redScore ) {
			if ( team != TEAM_BLUE ) {
				trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to members of the losing team.\\n\"" );
				return qfalse;
			}

			if ( TeamCount( ent->client->ps.clientNum, TEAM_BLUE ) > 0 ) {
				trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to the last remaining player on the losing team.\\n\"" );
				return qfalse;
			}

			return qtrue;
		}

		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to members of the losing team.\\n\"" );
		return qfalse;
	}

	if ( gametype == GT_TOURNAMENT ) {
		opponent = NULL;
		opponentScore = 0;

		for ( i = 0; i < level.maxclients; i++ ) {
			gclient_t *client;

			if ( i == ent->client->ps.clientNum ) {
				continue;
			}

			client = &level.clients[i];
			if ( client->pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {
				continue;
			}

			opponent = client;
			opponentScore = client->ps.persistant[PERS_SCORE];
			break;
		}

		if ( !opponent ) {
			return qfalse;
		}

		if ( ent->client->ps.persistant[PERS_SCORE] >= opponentScore
			|| ent->client->ps.pm_type != PM_NORMAL
			|| ent->health <= 0 ) {
			trap_SendServerCommand( ent-g_entities, "print \"Forfeit is only available to the losing player.\\n\"" );
			return qfalse;
		}

		return qtrue;
	}

	trap_SendServerCommand( ent-g_entities, va( "print \"Forfeit is not available in %s.\\n\"", gametypeName ) );
	return qfalse;
}


/*
=============
Cmd_Kill_f

Executes the self-kill command while honouring the g_allowKill cooldown.
=============
*/
void Cmd_Kill_f( gentity_t *ent ) {
	int	cooldown;

	if ( !ent || !ent->client ) {
		return;
	}
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}
	if ( ent->health <= 0 ) {
		return;
	}

	cooldown = g_allowKill.integer;
	if ( cooldown < 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Kill is not enabled on this server.\n\"" );
		return;
	}

	if ( cooldown > 0 ) {
		int	spawnElapsed;
		int	killElapsed;

		spawnElapsed = level.time - ent->client->respawnTime;
		if ( spawnElapsed < cooldown ) {
			return;
		}

		if ( ent->client->pers.killCommandTime >= 0 ) {
			killElapsed = level.time - ent->client->pers.killCommandTime;
			if ( killElapsed < cooldown ) {
				return;
			}
		}
	}

	ent->flags &= ~FL_GODMODE;
	ent->client->ps.stats[STAT_HEALTH] = ent->health = -999;
	ent->client->pers.killCommandTime = level.time;
	player_die( ent, ent, ent, 100000, MOD_SUICIDE );
}

/*
=============
Cmd_Forfeit_f

Processes the player forfeit command.
=============
*/
void Cmd_Forfeit_f( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	if ( ent->health <= 0 ) {
		return;
	}

	if ( level.timeoutActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is not available during a pause or timeout.\\n\"" );
		return;
	}

	if ( G_IsRoundCountdownActive() ) {
		trap_SendServerCommand( ent-g_entities, "print \"Forfeit is not available during a round countdown.\\n\"" );
		return;
	}

	if ( G_CanForfeit( ent, qtrue ) ) {
		G_ApplyForfeit();
	}
}

/*
=================
BroadCastTeamChange

Let everyone know about a team change
=================
*/
void BroadcastTeamChange( gclient_t *client, int oldTeam )
{
	if ( client->sess.sessionTeam == TEAM_RED ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the red team.\n\"",
			client->pers.netname) );
	} else if ( client->sess.sessionTeam == TEAM_BLUE ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the blue team.\n\"",
		client->pers.netname));
	} else if ( client->sess.sessionTeam == TEAM_SPECTATOR && oldTeam != TEAM_SPECTATOR ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the spectators.\n\"",
		client->pers.netname));
	} else if ( client->sess.sessionTeam == TEAM_FREE ) {
		trap_SendServerCommand( -1, va("cp \"%s" S_COLOR_WHITE " joined the battle.\n\"",
		client->pers.netname));
	}
}

/*
=================
SetTeam
=================
*/
void SetTeam( gentity_t *ent, char *s ) {
	int					team, oldTeam;
	gclient_t			*client;
	int					clientNum;
	spectatorState_t	specState;
	int					specClient;
	int					teamLeader;
	qboolean			requestedSpectator;
	qboolean			wasSpectateOnly;
	qboolean			sendQueueMessage;
	qboolean			sendSpectateOnlyMessage;

	//
	// see what change is requested
	//
	client = ent->client;
	requestedSpectator = qfalse;
	sendQueueMessage = qfalse;
	sendSpectateOnlyMessage = qfalse;
	wasSpectateOnly = client->sess.spectateOnly;

	clientNum = client - level.clients;
	specClient = 0;
	specState = SPECTATOR_NOT;
	if ( !Q_stricmp( s, "scoreboard" ) || !Q_stricmp( s, "score" )  ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_SCOREBOARD;
		requestedSpectator = qtrue;
	} else if ( !Q_stricmp( s, "follow1" ) ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_FOLLOW;
		specClient = -1;
		requestedSpectator = qtrue;
	} else if ( !Q_stricmp( s, "follow2" ) ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_FOLLOW;
		specClient = -2;
		requestedSpectator = qtrue;
	} else if ( !Q_stricmp( s, "spectator" ) || !Q_stricmp( s, "s" ) ) {
		team = TEAM_SPECTATOR;
		specState = SPECTATOR_FREE;
		requestedSpectator = qtrue;
	} else if ( g_gametype.integer >= GT_TEAM ) {
		// if running a team game, assign player to one of the teams
		specState = SPECTATOR_NOT;
		if ( !Q_stricmp( s, "red" ) || !Q_stricmp( s, "r" ) ) {
			team = TEAM_RED;
		} else if ( !Q_stricmp( s, "blue" ) || !Q_stricmp( s, "b" ) ) {
			team = TEAM_BLUE;
		} else if ( !Q_stricmp( s, "auto" ) ) {
			team = G_RRResolveAutoJoinTeam( clientNum );
		} else {
			team = G_RRResolveAutoJoinTeam( clientNum );
		}

		if ( g_teamForceBalance.integer  ) {
			int		counts[TEAM_NUM_TEAMS];
			int		nextRedCount;
			int		nextBlueCount;

			counts[TEAM_BLUE] = TeamCount( ent->client->ps.clientNum, TEAM_BLUE );
			counts[TEAM_RED] = TeamCount( ent->client->ps.clientNum, TEAM_RED );
			nextRedCount = counts[TEAM_RED] + ( team == TEAM_RED ? 1 : 0 );
			nextBlueCount = counts[TEAM_BLUE] + ( team == TEAM_BLUE ? 1 : 0 );

			if ( !Team_CountsBalanced( nextRedCount, nextBlueCount ) ) {
				if ( team == TEAM_RED ) {
					trap_SendServerCommand( ent->client->ps.clientNum, 
						"cp \"Red team has too many players.\n\"" );
				}
				else {
					trap_SendServerCommand( ent->client->ps.clientNum, 
						"cp \"Blue team has too many players.\n\"" );
				}
				return; // ignore the request
			}
		}

	} else {
		// force them to spectators if there aren't any spots free
		team = TEAM_FREE;
	}

	if ( g_teamSpawnAsSpec.integer && g_gametype.integer >= GT_TEAM && team != TEAM_SPECTATOR ) {
		team = TEAM_SPECTATOR;
		specState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;
	}

	if ( team == TEAM_SPECTATOR && specState == SPECTATOR_FREE && !g_teamSpecFreeCam.integer ) {
		specState = SPECTATOR_SCOREBOARD;
	}

	// override decision if limiting the players
	if ( (g_gametype.integer == GT_TOURNAMENT)
		&& level.numNonSpectatorClients >= 2 ) {
		team = TEAM_SPECTATOR;
	} else if ( g_maxGameClients.integer > 0 && 
		level.numNonSpectatorClients >= g_maxGameClients.integer ) {
		team = TEAM_SPECTATOR;
	}

	//
	// decide if we will allow the change
	//
	oldTeam = client->sess.sessionTeam;
	if ( team == oldTeam && team != TEAM_SPECTATOR ) {
		return;
	}

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		client->sess.spectatorQueuePosition = 0;
		client->sess.spectatorQueuePositionDirty = qfalse;
		if ( requestedSpectator ) {
			client->sess.spectateOnly = qtrue;
			if ( oldTeam != TEAM_SPECTATOR || !wasSpectateOnly ) {
				sendSpectateOnlyMessage = qtrue;
			}
		} else {
			client->sess.spectateOnly = qfalse;
			if ( team == TEAM_SPECTATOR && ( oldTeam != TEAM_SPECTATOR || wasSpectateOnly ) ) {
				sendQueueMessage = qtrue;
			}
		}
	} else {
		client->sess.spectateOnly = qfalse;
		client->sess.spectatorQueuePosition = 0;
		client->sess.spectatorQueuePositionDirty = qfalse;
	}

	//
	// execute the team change
	//

	// if the player was dead leave the body
	if ( client->ps.stats[STAT_HEALTH] <= 0 ) {
		CopyToBodyQue(ent);
	}

	// he starts at 'base'
	client->pers.teamState.state = TEAM_BEGIN;
	G_SetClientReadyState( client, qfalse );
	if ( oldTeam != TEAM_SPECTATOR ) {
		G_RankSendPlayerStats( ent, qtrue );

		// Kill him (makes sure he loses flags, etc)
		ent->flags &= ~FL_GODMODE;
		ent->client->ps.stats[STAT_HEALTH] = ent->health = 0;
		player_die (ent, ent, ent, 100000, MOD_SUICIDE);

	}
	// they go to the end of the line for tournements
	if ( team == TEAM_SPECTATOR ) {
		client->sess.spectatorTime = level.time;
	}

	client->sess.sessionTeam = team;
	client->sess.spectatorState = specState;
	client->sess.spectatorClient = specClient;
	client->pers.teamJoinStartTime = ( team == TEAM_SPECTATOR ) ? 0 : level.time;
	if ( oldTeam != team ) {
		G_RankSendPlayerSwitchTeam( ent, oldTeam, team );
	}

	client->lastKillCommandTime = 0;
	client->killCommandCooldownExpires = 0;
	client->friendlyFireComplaints = 0;
	client->friendlyFireComplaintEndTime = 0;
	client->teammateDamageGiven = 0;
	client->teammateDamageThisLife = 0;
	client->teamDamageEventsGiven = 0;
	client->teamDamageEventsReceived = 0;

	client->sess.teamLeader = qfalse;
	if ( team == TEAM_RED || team == TEAM_BLUE ) {
		teamLeader = TeamLeader( team );
		// if there is no team leader or the team leader is a bot and this client is not a bot
		if ( teamLeader == -1 || ( !(g_entities[clientNum].r.svFlags & SVF_BOT) && (g_entities[teamLeader].r.svFlags & SVF_BOT) ) ) {
			SetLeader( team, clientNum );
		}
	}
	// make sure there is a team leader on the team the player came from
	if ( oldTeam == TEAM_RED || oldTeam == TEAM_BLUE ) {
		CheckTeamLeader( oldTeam );
	}

	BroadcastTeamChange( client, oldTeam );

	if ( sendQueueMessage ) {
		trap_SendServerCommand( ent - g_entities, "cp \"You are in the queue to play\n\"" );
	}
	if ( sendSpectateOnlyMessage ) {
		trap_SendServerCommand( ent - g_entities, "cp \"You are set to spectate only\n\"" );
	}

	// get and distribute relevent paramters
	ClientUserinfoChanged( clientNum );

	ClientBegin( clientNum );
}

/*
=================
StopFollowing

If the client being followed leaves the game, or you just want to drop
to free floating spectator mode
=================
*/
void StopFollowing( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	ent->client->ps.persistant[ PERS_TEAM ] = TEAM_SPECTATOR;
	ent->client->sess.sessionTeam = TEAM_SPECTATOR;
	ent->client->sess.spectatorState = g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;
	ent->client->sess.spectatorClient = -1;
	ent->client->lastKillCommandTime = 0;
	ent->client->killCommandCooldownExpires = 0;
	ent->client->friendlyFireComplaints = 0;
	ent->client->friendlyFireComplaintEndTime = 0;
	ent->client->teammateDamageGiven = 0;
	ent->client->teammateDamageThisLife = 0;
	ent->client->teamDamageEventsGiven = 0;
	ent->client->teamDamageEventsReceived = 0;
	ent->client->ps.pm_flags &= ~PMF_FOLLOW;
	ent->r.svFlags &= ~SVF_BOT;
	ent->client->ps.clientNum = ent - g_entities;
}

/*
=================
Cmd_Team_f
=================
*/
void Cmd_Team_f( gentity_t *ent ) {
	int			oldTeam;
	char		s[MAX_TOKEN_CHARS];

	if ( trap_Argc() != 2 ) {
		oldTeam = ent->client->sess.sessionTeam;
		switch ( oldTeam ) {
		case TEAM_BLUE:
			trap_SendServerCommand( ent-g_entities, "print \"Blue team\n\"" );
			break;
		case TEAM_RED:
			trap_SendServerCommand( ent-g_entities, "print \"Red team\n\"" );
			break;
		case TEAM_FREE:
			trap_SendServerCommand( ent-g_entities, "print \"Free team\n\"" );
			break;
		case TEAM_SPECTATOR:
			trap_SendServerCommand( ent-g_entities, "print \"Spectator team\n\"" );
			break;
		}
		return;
	}

	if ( ent->client->switchTeamTime > level.time ) {
		trap_SendServerCommand( ent-g_entities, "print \"May not switch teams more than once per 5 seconds.\n\"" );
		return;
	}

	// if they are playing a tournement game, count as a loss
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& ent->client->sess.sessionTeam == TEAM_FREE ) {
		ent->client->sess.losses++;
	}

	trap_Argv( 1, s, sizeof( s ) );

	SetTeam( ent, s );

	ent->client->switchTeamTime = level.time + 5000;
}


/*
=================
Cmd_Follow_f
=================
*/
void Cmd_Follow_f( gentity_t *ent ) {
	int			i;
	char	arg[MAX_TOKEN_CHARS];

	if ( !ent || !ent->client ) {
		return;
	}

	if ( level.trainingMapActive ) {
		if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
			StopFollowing( ent );
		}
		trap_SendServerCommand( ent-g_entities, "print \"Following is disabled in training.\n\"" );
		return;
	}

	if ( trap_Argc() != 2 ) {
		if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
			if ( g_teamSpecFreeCam.integer ) {
				StopFollowing( ent );
			} else {
				trap_SendServerCommand( ent-g_entities, "print \"Free-flying spectators are disabled while g_teamSpecFreeCam is 0.\n\"" );
			}
		}
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	i = ClientNumberFromString( ent, arg );
	if ( i == -1 ) {
		return;
	}

	// can't follow self
	if ( &level.clients[ i ] == ent->client ) {
		return;
	}

	// can't follow another spectator
	if ( level.clients[ i ].sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	// if they are playing a tournement game, count as a loss
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& ent->client->sess.sessionTeam == TEAM_FREE ) {
		ent->client->sess.losses++;
	}

	// first set them to spectator
	if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		SetTeam( ent, "spectator" );
	}

	ent->client->sess.spectatorState = SPECTATOR_FOLLOW;
	ent->client->sess.spectatorClient = i;

}

/*
=================
Cmd_FollowCycle_f
=================
*/
void Cmd_FollowCycle_f( gentity_t *ent, int dir ) {
	int		clientnum;
	int		original;
	int		curr;
	int		max;

	if ( level.trainingMapActive ) {
		if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
			StopFollowing( ent );
		}
		trap_SendServerCommand( ent-g_entities, "print \"Following is disabled in training.\n\"" );
		return;
	}

	// if they are playing a tournement game, count as a loss
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& ent->client->sess.sessionTeam == TEAM_FREE ) {
		ent->client->sess.losses++;
	}
	// first set them to spectator
	if ( ent->client->sess.spectatorState == SPECTATOR_NOT ) {
		SetTeam( ent, "spectator" );
	}

	if ( dir != 1 && dir != -1 ) {
		G_Error( "Cmd_FollowCycle_f: bad dir %i", dir );
	}

	clientnum = ent->client->sess.spectatorClient;
	max = level.maxclients + level.numPois;

	// Map spectatorClient to linear index 0..max-1
	if ( clientnum >= 0 && clientnum < level.maxclients ) {
		curr = clientnum;
	} else if ( clientnum <= -10 ) {
		curr = level.maxclients + (-(clientnum + 10));
	} else {
		curr = 0; // Fallback
	}

	original = curr;

	do {
		curr += dir;
		if ( curr >= max ) {
			curr = 0;
		} else if ( curr < 0 ) {
			curr = max - 1;
		}

		if ( curr < level.maxclients ) {
			// Client logic
			if ( level.clients[ curr ].pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( level.clients[ curr ].sess.sessionTeam == TEAM_SPECTATOR ) {
				continue;
			}

			ent->client->sess.spectatorClient = curr;
			ent->client->sess.spectatorState = SPECTATOR_FOLLOW;
			return;
		} else {
			// POI logic
			int poiIndex = curr - level.maxclients;
			if ( poiIndex >= 0 && poiIndex < level.numPois && level.pois[poiIndex].inuse ) {
				ent->client->sess.spectatorClient = -(poiIndex + 10);
				ent->client->sess.spectatorState = SPECTATOR_FOLLOW;
				return;
			}
		}

	} while ( curr != original );

	// leave it where it was
}


/*
=============
G_SayTo

Sends a chat message to a single recipient when chat permissions allow it.
=============
*/
static void G_SayTo( gentity_t *ent, gentity_t *other, int mode, int color, const char *name, const char *message ) {
	if ( !other ) {
		return;
	}
	if ( !other->inuse ) {
		return;
	}
	if ( !other->client ) {
		return;
	}
	if ( other->client->pers.connected != CON_CONNECTED ) {
		return;
	}
	if ( mode == SAY_TEAM && !OnSameTeam( ent, other ) ) {
		return;
	}

	if ( ent && ent->client && other->client ) {
		if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR && !g_teamSpecSayEnable.integer ) {
			if ( ent == other ) {
				trap_SendServerCommand( ent - g_entities, "print \"Spectator chat is disabled while g_teamSpecSayEnable is 0.\n\"" );
			}
			return;
		}

		const team_t		entTeam = ent->client->sess.sessionTeam;
		const team_t		otherTeam = other->client->sess.sessionTeam;
		const qboolean	isTeamGame = ( g_gametype.integer >= GT_TEAM );
		const qboolean	sameClient = ( ent == other );

		if ( entTeam == TEAM_SPECTATOR && otherTeam != TEAM_SPECTATOR && !sameClient && !g_allTalk.integer ) {
			if ( mode == SAY_TELL ) {
				trap_SendServerCommand( ent - g_entities, "print \"Spectators may only chat with other spectators unless g_allTalk is enabled.\n\"" );
			}
			return;
		}

		if ( isTeamGame && mode != SAY_TEAM && !g_allTalk.integer && entTeam != TEAM_SPECTATOR && otherTeam != TEAM_SPECTATOR && entTeam != otherTeam ) {
			if ( mode == SAY_TELL && !sameClient ) {
				trap_SendServerCommand( ent - g_entities, "print \"Cross-team tells are disabled while g_allTalk is 0.\n\"" );
			}
			return;
		}
	}

	// no chatting to players in tournements
	if ( (g_gametype.integer == GT_TOURNAMENT )
		&& other->client->sess.sessionTeam == TEAM_FREE
		&& ent->client->sess.sessionTeam != TEAM_FREE ) {
		return;
	}

	trap_SendServerCommand( other-g_entities, va( "%s %d \"%s%c%c%s\"",
		mode == SAY_TEAM ? "tchat" : "chat",
		ent->s.number,
		name, Q_COLOR_ESCAPE, color, message));
}

#define EC		"\x19"

/*
=============
G_Say

Routes chat text according to chat mode and talk permissions.
=============
*/
void G_Say( gentity_t *ent, gentity_t *target, int mode, const char *chatText ) {
	int			j;
	gentity_t	*other;
	int			color;
	char		name[64];
	// don't let text be too long for malicious reasons
	char		text[MAX_SAY_TEXT];
	char		location[64];

	if ( ent->client && ent->client->sess.muted ) {
		trap_SendServerCommand( ent-g_entities, "print \"You are muted.\n\"" );
		return;
	}

	if ( g_gametype.integer < GT_TEAM && mode == SAY_TEAM ) {
		mode = SAY_ALL;
	}

	switch ( mode ) {
	default:
	case SAY_ALL:
		G_LogPrintf( "say: %s: %s\n", ent->client->pers.netname, chatText );
		Com_sprintf (name, sizeof(name), "%s%c%c"EC": ", ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE );
		color = COLOR_GREEN;
		break;
	case SAY_TEAM:
		G_LogPrintf( "sayteam: %s: %s\n", ent->client->pers.netname, chatText );
		if (Team_GetLocationMsg(ent, location, sizeof(location)))
			Com_sprintf (name, sizeof(name), EC"(%s%c%c"EC") (%s)"EC": ", 
				ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE, location);
		else
			Com_sprintf (name, sizeof(name), EC"(%s%c%c"EC")"EC": ", 
				ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE );
		color = COLOR_CYAN;
		break;
	case SAY_TELL:
		if (target && g_gametype.integer >= GT_TEAM &&
			target->client->sess.sessionTeam == ent->client->sess.sessionTeam &&
			Team_GetLocationMsg(ent, location, sizeof(location)))
			Com_sprintf (name, sizeof(name), EC"[%s%c%c"EC"] (%s)"EC": ", ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE, location );
		else
			Com_sprintf (name, sizeof(name), EC"[%s%c%c"EC"]"EC": ", ent->client->pers.netname, Q_COLOR_ESCAPE, COLOR_WHITE );
		color = COLOR_MAGENTA;
		break;
	}

	Q_strncpyz( text, chatText, sizeof(text) );

	if ( target ) {
		G_SayTo( ent, target, mode, color, name, text );
		return;
	}

	// echo the text to the console
	if ( g_dedicated.integer ) {
		G_Printf( "%s%s\n", name, text);
	}

	// send it to all the apropriate clients
	for (j = 0; j < level.maxclients; j++) {
		other = &g_entities[j];
		G_SayTo( ent, other, mode, color, name, text );
	}
}


/*
==================
Cmd_Say_f
==================
*/
static void Cmd_Say_f( gentity_t *ent, int mode, qboolean arg0 ) {
	char		*p;

	if ( trap_Argc () < 2 && !arg0 ) {
		return;
	}

	if (arg0)
	{
		p = ConcatArgs( 0 );
	}
	else
	{
		p = ConcatArgs( 1 );
	}

	if ( G_FloodLimited( ent, ( mode == SAY_TEAM ) ? "using team chat" : "chatting", qtrue ) ) {
		return;
	}

	G_Say( ent, NULL, mode, p );
}

/*
==================
Cmd_Tell_f
==================
*/
static void Cmd_Tell_f( gentity_t *ent ) {
	int			targetNum;
	gentity_t	*target;
	char		*p;
	char		arg[MAX_TOKEN_CHARS];

	if ( trap_Argc () < 2 ) {
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	targetNum = atoi( arg );
	if ( targetNum < 0 || targetNum >= level.maxclients ) {
		return;
	}

	target = &g_entities[targetNum];
	if ( !target || !target->inuse || !target->client ) {
		return;
	}

	p = ConcatArgs( 2 );

	if ( G_FloodLimited( ent, "sending tells", qtrue ) ) {
		return;
	}

	G_LogPrintf( "tell: %s to %s: %s\n", ent->client->pers.netname, target->client->pers.netname, p );
	G_Say( ent, target, SAY_TELL, p );
	// don't tell to the player self if it was already directed to this player
	// also don't send the chat back to a bot
	if ( ent != target && !(ent->r.svFlags & SVF_BOT)) {
		G_Say( ent, ent, SAY_TELL, p );
	}
}


static void G_VoiceTo( gentity_t *ent, gentity_t *other, int mode, const char *id, qboolean voiceonly ) {
	int color;
	char *cmd;

	if (!other) {
		return;
	}
	if (!other->inuse) {
		return;
	}
	if (!other->client) {
		return;
	}
	if ( mode == SAY_TEAM && !OnSameTeam(ent, other) ) {
		return;
	}
	// no chatting to players in tournements
	if ( (g_gametype.integer == GT_TOURNAMENT )) {
		return;
	}

	if (mode == SAY_TEAM) {
		color = COLOR_CYAN;
		cmd = "vtchat";
	}
	else if (mode == SAY_TELL) {
		color = COLOR_MAGENTA;
		cmd = "vtell";
	}
	else {
		color = COLOR_GREEN;
		cmd = "vchat";
	}

	trap_SendServerCommand( other-g_entities, va("%s %d %d %d %s", cmd, voiceonly, ent->s.number, color, id));
}

void G_Voice( gentity_t *ent, gentity_t *target, int mode, const char *id, qboolean voiceonly ) {
	int			j;
	gentity_t	*other;

	if ( ent->client && ent->client->sess.muted ) {
		trap_SendServerCommand( ent-g_entities, "print \"You are muted.\n\"" );
		return;
	}

	if ( g_gametype.integer < GT_TEAM && mode == SAY_TEAM ) {
		mode = SAY_ALL;
	}

	if ( target ) {
		G_VoiceTo( ent, target, mode, id, voiceonly );
		return;
	}

	// echo the text to the console
	if ( g_dedicated.integer ) {
		G_Printf( "voice: %s %s\n", ent->client->pers.netname, id);
	}

	// send it to all the apropriate clients
	for (j = 0; j < level.maxclients; j++) {
		other = &g_entities[j];
		G_VoiceTo( ent, other, mode, id, voiceonly );
	}
}

/*
==================
Cmd_Voice_f
==================
*/
static void Cmd_Voice_f( gentity_t *ent, int mode, qboolean arg0, qboolean voiceonly ) {
	char		*p;
	const char		*action;

	if ( trap_Argc () < 2 && !arg0 ) {
		return;
	}

	if (arg0)
	{
		p = ConcatArgs( 0 );
	}
	else
	{
		p = ConcatArgs( 1 );
	}

	if ( mode == SAY_TEAM ) {
		action = voiceonly ? "using team voice commands" : "using team voice chat";
	} else {
		action = voiceonly ? "using voice commands" : "using voice chat";
	}

	if ( G_FloodLimited( ent, action, qtrue ) ) {
		return;
	}

	G_Voice( ent, NULL, mode, p, voiceonly );
}

/*
==================
Cmd_VoiceTell_f
==================
*/
static void Cmd_VoiceTell_f( gentity_t *ent, qboolean voiceonly ) {
	int			targetNum;
	gentity_t	*target;
	char		*id;
	char		arg[MAX_TOKEN_CHARS];

	if ( trap_Argc () < 2 ) {
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	targetNum = atoi( arg );
	if ( targetNum < 0 || targetNum >= level.maxclients ) {
		return;
	}

	target = &g_entities[targetNum];
	if ( !target || !target->inuse || !target->client ) {
		return;
	}

	id = ConcatArgs( 2 );

	if ( G_FloodLimited( ent, voiceonly ? "sending private voice commands" : "sending private voice chats", qtrue ) ) {
		return;
	}

	G_LogPrintf( "vtell: %s to %s: %s\n", ent->client->pers.netname, target->client->pers.netname, id );
	G_Voice( ent, target, SAY_TELL, id, voiceonly );
	// don't tell to the player self if it was already directed to this player
	// also don't send the chat back to a bot
	if ( ent != target && !(ent->r.svFlags & SVF_BOT)) {
		G_Voice( ent, ent, SAY_TELL, id, voiceonly );
	}
}


/*
==================
Cmd_VoiceTaunt_f
==================
*/
static void Cmd_VoiceTaunt_f( gentity_t *ent ) {
	gentity_t *who;
	int i;

	if (!ent->client) {
		return;
	}

	if ( G_FloodLimited( ent, "sending voice taunts", qtrue ) ) {
		return;
	}

	// insult someone who just killed you
	if (ent->enemy && ent->enemy->client && ent->enemy->client->lastkilled_client == ent->s.number) {
		// i am a dead corpse
		if (!(ent->enemy->r.svFlags & SVF_BOT)) {
			G_Voice( ent, ent->enemy, SAY_TELL, VOICECHAT_DEATHINSULT, qfalse );
		}
		if (!(ent->r.svFlags & SVF_BOT)) {
			G_Voice( ent, ent,        SAY_TELL, VOICECHAT_DEATHINSULT, qfalse );
		}
		ent->enemy = NULL;
		return;
	}
	// insult someone you just killed
	if (ent->client->lastkilled_client >= 0 && ent->client->lastkilled_client != ent->s.number) {
		who = g_entities + ent->client->lastkilled_client;
		if (who->client) {
			// who is the person I just killed
			if (who->client->lasthurt_mod == MOD_GAUNTLET) {
				if (!(who->r.svFlags & SVF_BOT)) {
					G_Voice( ent, who, SAY_TELL, VOICECHAT_KILLGAUNTLET, qfalse );	// and I killed them with a gauntlet
				}
				if (!(ent->r.svFlags & SVF_BOT)) {
					G_Voice( ent, ent, SAY_TELL, VOICECHAT_KILLGAUNTLET, qfalse );
				}
			} else {
				if (!(who->r.svFlags & SVF_BOT)) {
					G_Voice( ent, who, SAY_TELL, VOICECHAT_KILLINSULT, qfalse );	// and I killed them with something else
				}
				if (!(ent->r.svFlags & SVF_BOT)) {
					G_Voice( ent, ent, SAY_TELL, VOICECHAT_KILLINSULT, qfalse );
				}
			}
			ent->client->lastkilled_client = -1;
			return;
		}
	}

	if (g_gametype.integer >= GT_TEAM) {
		// praise a team mate who just got a reward
		for(i = 0; i < MAX_CLIENTS; i++) {
			who = g_entities + i;
			if (who->client && who != ent && who->client->sess.sessionTeam == ent->client->sess.sessionTeam) {
				if (who->client->rewardTime > level.time) {
					if (!(who->r.svFlags & SVF_BOT)) {
						G_Voice( ent, who, SAY_TELL, VOICECHAT_PRAISE, qfalse );
					}
					if (!(ent->r.svFlags & SVF_BOT)) {
						G_Voice( ent, ent, SAY_TELL, VOICECHAT_PRAISE, qfalse );
					}
					return;
				}
			}
		}
	}

	// just say something
	G_Voice( ent, NULL, SAY_ALL, VOICECHAT_TAUNT, qfalse );
}



static char	*gc_orders[] = {
	"hold your position",
	"hold this position",
	"come here",
	"cover me",
	"guard location",
	"search and destroy",
	"report"
};

void Cmd_GameCommand_f( gentity_t *ent ) {
	int		player;
	int		order;
	char	str[MAX_TOKEN_CHARS];

	trap_Argv( 1, str, sizeof( str ) );
	player = atoi( str );
	trap_Argv( 2, str, sizeof( str ) );
	order = atoi( str );

	if ( player < 0 || player >= MAX_CLIENTS ) {
		return;
	}
	if ( order < 0 || order > sizeof(gc_orders)/sizeof(char *) ) {
		return;
	}
	if ( G_FloodLimited( ent, "issuing team commands", qtrue ) ) {
		return;
	}
	G_Say( ent, &g_entities[player], SAY_TELL, gc_orders[order] );
	G_Say( ent, ent, SAY_TELL, gc_orders[order] );
}

/*
==================
Cmd_Where_f
==================
*/
void Cmd_Where_f( gentity_t *ent ) {
	trap_SendServerCommand( ent-g_entities, va("print \"%s\n\"", vtos( ent->s.origin ) ) );
}

#define VF_NO_MAP				0x0001
#define VF_NO_MAP_RESTART		0x0002
#define VF_NO_NEXTMAP			0x0004
#define VF_NO_GAMETYPE			0x0008
#define VF_NO_KICK			0x0010
#define VF_NO_TIME_LIMIT		0x0020
#define VF_NO_FRAG_LIMIT		0x0040
#define VF_NO_SHUFFLE			0x0080
#define VF_NO_TEAMSIZE			0x0100
#define VF_NO_RANDOM			0x0200
#define VF_NO_LOADOUTS			0x0400
#define VF_NO_AMMO			0x1000
#define VF_NO_TIMERS			0x2000
#define VF_NO_WEAPRESPAWN		0x4000
#define VF_NO_BOTS			0x8000

static const char *gameNames[] = {
"Free For All",
"Duel",
"Race",
"Team Deathmatch",
"Clan Arena",
"Capture the Flag",
"One Flag CTF",
"Overload",
"Harvester",
"Freeze Tag",
"Domination",
"Attack and Defend",
"Red Rover"
};

/*
=============
G_VoteSelectionKey

Generate a stable hash so repeated vote attempts can be detected.
=============
*/
static int G_VoteSelectionKey( const char *command, const char *option ) {
	int		hash;
	const char	*scan;

	if ( !command || !*command ) {
		return -1;
	}

	hash = 5381;
	for ( scan = command ; *scan ; scan++ ) {
		hash = ( ( hash << 5 ) + hash ) ^ tolower( *scan );
	}

	if ( option && *option ) {
		for ( scan = option ; *scan ; scan++ ) {
			hash = ( ( hash << 5 ) + hash ) ^ tolower( *scan );
		}
	}

	return hash;
}

/*
=============
G_VoteArgumentIsUnsignedInteger

Reports whether a callvote argument is a non-empty unsigned integer token.
=============
*/
static qboolean G_VoteArgumentIsUnsignedInteger( const char *text ) {
	const unsigned char	*scan;

	if ( !text || !text[0] ) {
		return qfalse;
	}

	for ( scan = (const unsigned char *)text; *scan; scan++ ) {
		if ( *scan < '0' || *scan > '9' ) {
			return qfalse;
		}
	}

	return qtrue;
}

/*
=============
G_ClientBypassesCallVoteRestrictions

Retail allows moderators and above to bypass the public-vote, vote-limit,
spectator, and vote-flag disable gates in Cmd_CallVote_f.
=============
*/
static qboolean G_ClientBypassesCallVoteRestrictions( const gclient_t *client ) {
	if ( !client ) {
		return qfalse;
	}

	return ( client->sess.privilege >= PRIV_MOD ) ? qtrue : qfalse;
}

/*
=============
G_CallVoteHelpColor

Retail colors disabled callvote commands red and available ones green.
=============
*/
static int G_CallVoteHelpColor( int voteFlagMask ) {
	if ( g_voteFlags.integer & voteFlagMask ) {
		return 1;
	}

	return 5;
}

/*
==================
Cmd_CallVote_f
==================
*/
void Cmd_CallVote_f( gentity_t *ent ) {
	gclient_t       *client;
	char            arg1[MAX_STRING_TOKENS];
	char            arg2[MAX_STRING_TOKENS];
	char            arg3[MAX_STRING_TOKENS];
	char            buffer[MAX_STRING_CHARS];
	int             voteSelection;
	int             delayMsec;
	int             remaining;
	qboolean        isSpectator;
	qboolean        privilegedCallVote;
	qboolean        midGame;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;

	trap_Argv( 1, arg1, sizeof( arg1 ) );
	trap_Argv( 2, arg2, sizeof( arg2 ) );
	trap_Argv( 3, arg3, sizeof( arg3 ) );

	if ( strchr( arg1, ';' ) || strchr( arg2, ';' ) || strchr( arg3, ';' ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid vote string.\\n\"" );
		return;
	}

	delayMsec = g_voteDelay.integer > 0 ? g_voteDelay.integer * 1000 : 0;
	isSpectator = ( client->sess.sessionTeam == TEAM_SPECTATOR );
	privilegedCallVote = G_ClientBypassesCallVoteRestrictions( client );
	midGame = G_WarmupReadyToStart();

	if ( delayMsec > 0 ) {
		int             startWindow;

		startWindow = level.startTime + delayMsec;
		if ( level.time < startWindow ) {
			remaining = startWindow - level.time;
			trap_SendServerCommand( ent-g_entities,
				va( "print \"Voting will be allowed in %.1f seconds.\\n\"", remaining / 1000.0f ) );
			return;
		}

		if ( level.voteEligibleTime > level.time ) {
			remaining = level.voteEligibleTime - level.time;
			trap_SendServerCommand( ent-g_entities,
				va( "print \"Voting will be allowed in %.1f seconds.\\n\"", remaining / 1000.0f ) );
			return;
		}
	}

	if ( !g_allowVote.integer && !privilegedCallVote ) {
		trap_SendServerCommand( ent-g_entities, "print \"Public voting is not allowed here.\\n\"" );
		return;
	}

	if ( level.trainingMapActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"Voting is not allowed in training.\\n\"" );
		return;
	}

	if ( g_voteLimit.integer > 0 && client->pers.voteCount >= g_voteLimit.integer && !privilegedCallVote ) {
		trap_SendServerCommand( ent-g_entities, "print \"You have called the maximum number of votes.\\n\"" );
		return;
	}

	if ( isSpectator && !g_allowSpecVote.integer && !privilegedCallVote ) {
		trap_SendServerCommand( ent-g_entities, "print \"Not allowed to call a vote as spectator.\\n\"" );
		return;
	}

	if ( !g_allowVoteMidGame.integer && midGame && !privilegedCallVote ) {
		trap_SendServerCommand( ent-g_entities, "print \"Voting is only allowed during the warm up period.\\n\"" );
		return;
	}

	if ( level.voteTime ) {
		trap_SendServerCommand( ent-g_entities, "print \"A vote is already in progress.\\n\"" );
		return;
	}

	if ( level.voteExecuteTime && level.voteExecuteTime > level.time ) {
		trap_SendServerCommand( ent-g_entities, "print \"A vote is being executed.\\n\"" );
		return;
	}

	voteSelection = -1;

	if ( !Q_stricmp( arg1, "map_restart" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_MAP_RESTART ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting on a map restart is disabled on this server.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "map_restart" );
		Q_strncpyz( level.voteDisplayString, level.voteString, sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, NULL );
	} else if ( !Q_stricmp( arg1, "nextmap" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_NEXTMAP ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to move to the next map is disabled on this server.\\n\"" );
			return;
		}
		trap_Cvar_VariableStringBuffer( "nextmap", buffer, sizeof( buffer ) );
		if ( !buffer[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"nextmap not set.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "vstr nextmap" );
		Q_strncpyz( level.voteDisplayString, "nextmap", sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, buffer );
	} else if ( !Q_stricmp( arg1, "map" ) ) {
		int			len;
		fileHandle_t	f;
		const factoryDefinition_t *factoryOverride;
		char		voteOptionBuffer[MAX_STRING_TOKENS];
		const char	*voteOption;

		if ( ( g_voteFlags.integer & VF_NO_MAP ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the map being played is disabled on this server.\\n\"" );
			return;
		}
		if ( !arg2[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"Missing map name.\\n\"" );
			return;
		}
		Com_sprintf( buffer, sizeof( buffer ), "maps/%s.bsp", arg2 );
		len = trap_FS_FOpenFile( buffer, &f, FS_READ );
		if ( len <= 0 ) {
			trap_SendServerCommand( ent-g_entities, "print \"Map does not exist.\\n\"" );
			return;
		}
		trap_FS_FCloseFile( f );

		factoryOverride = NULL;
		voteOption = arg2;
		if ( arg3[0] ) {
			factoryOverride = Factory_FindById( arg3 );
			if ( !factoryOverride ) {
				trap_SendServerCommand( ent-g_entities, "print \"Invalid factory specified.\\n\"" );
				return;
			}
			if ( !G_MapSupportsGametype( arg2, factoryOverride->baseGametype ) ) {
				trap_SendServerCommand( ent-g_entities, "print \"Map not supported for this gametype.\\n\"" );
				return;
			}
			Com_sprintf( voteOptionBuffer, sizeof( voteOptionBuffer ), "%s %s", arg2, arg3 );
			voteOption = voteOptionBuffer;
		}

		trap_Cvar_VariableStringBuffer( "nextmap", buffer, sizeof( buffer ) );
		if ( buffer[0] ) {
			if ( factoryOverride ) {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s %s; set nextmap \"%s\"", arg2, arg3, buffer );
			} else {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s; set nextmap \"%s\"", arg2, buffer );
			}
		} else {
			if ( factoryOverride ) {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s %s", arg2, arg3 );
			} else {
				Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s", arg2 );
			}
		}
		if ( factoryOverride ) {
			Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "map %s %s", arg2, arg3 );
		} else {
			Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "map %s", arg2 );
		}
		voteSelection = G_VoteSelectionKey( arg1, voteOption );
	} else if ( !Q_stricmp( arg1, "g_gametype" ) ) {
		int             gametype;

		if ( ( g_voteFlags.integer & VF_NO_GAMETYPE ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the gametype being played is disabled on this server.\\n\"" );
			return;
		}

		gametype = atoi( arg2 );
		if ( gametype == GT_SINGLE_PLAYER || gametype < GT_FFA || gametype >= GT_MAX_GAME_TYPE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid gametype.\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_gametype %d", gametype );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_gametype %s", gameNames[gametype] );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "shuffle" ) ) {
		if ( g_gametype.integer < GT_TEAM ) {
			trap_SendServerCommand( ent-g_entities, "print \"Shuffle is only available in team games.\\n\"" );
			return;
		}
		if ( ( g_voteFlags.integer & VF_NO_SHUFFLE ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to shuffle the teams is disabled on this server.\\n\"" );
			return;
		}
		if ( midGame ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to shuffle the teams is only permitted during warmup.\\n\"" );
			return;
		}
		if ( arg2[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"Too many parameters called for a shuffle.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "shuffle_teams" );
		Q_strncpyz( level.voteDisplayString, "Shuffle Teams", sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, NULL );
	} else if ( !Q_stricmp( arg1, "teamsize" ) ) {
		int desiredSize;
		int activeCounts[TEAM_NUM_TEAMS];
		int totalActivePlayers;
		int maxSize;

		if ( g_gametype.integer == GT_TOURNAMENT ) {
			trap_SendServerCommand( ent-g_entities, "print \"Teamsize is not available in Duel.\\n\"" );
			return;
		}
		if ( ( g_voteFlags.integer & VF_NO_TEAMSIZE ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change team size is disabled on this server.\\n\"" );
			return;
		}
		if ( !arg2[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"Missing desired teamsize.\\n\"" );
			return;
		}
		if ( !G_VoteArgumentIsUnsignedInteger( arg2 ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid desired teamsize, parameter must be an integer.\\n\"" );
			return;
		}

		desiredSize = atoi( arg2 );
		if ( desiredSize > 0 ) {
			G_CountActivePlayersByTeam( activeCounts );
			totalActivePlayers = activeCounts[TEAM_FREE] + activeCounts[TEAM_RED] + activeCounts[TEAM_BLUE];
			if ( desiredSize < totalActivePlayers ) {
				trap_SendServerCommand( ent-g_entities,
					va( "print \"^1The arena has more than %d players. Players must leave before this teamsize can be set.^7\"", desiredSize ) );
				return;
			}
			if ( activeCounts[TEAM_RED] > desiredSize ) {
				trap_SendServerCommand( ent-g_entities,
					va( "print \"^1%s has more than %d players. Players must leave the team before this teamsize can be set.^7\"",
						"Red Team", desiredSize ) );
				return;
			}
			if ( activeCounts[TEAM_BLUE] > desiredSize ) {
				trap_SendServerCommand( ent-g_entities,
					va( "print \"^1%s has more than %d players. Players must leave the team before this teamsize can be set.^7\"",
						"Blue Team", desiredSize ) );
				return;
			}

			if ( g_gametype.integer >= GT_TEAM ) {
				maxSize = level.maxclients / 2;
			} else {
				maxSize = level.maxclients;
			}
			if ( desiredSize < 0 || desiredSize > maxSize ) {
				trap_SendServerCommand( ent-g_entities,
					va( "print \"Invalid team size. (Valid Range: %d - %d)\\n\"", 0, maxSize ) );
				return;
			}
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "teamsize %d", desiredSize );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "teamsize %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "kickbot" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_KICK ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to kick bots is disabled on this server.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "kick %s", arg2[0] ? arg2 : "allbots" );
		if ( arg2[0] ) {
			Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "kickbot %s", arg2 );
		} else {
			Q_strncpyz( level.voteDisplayString, "kickbot (all)", sizeof( level.voteDisplayString ) );
		}
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "addbot" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_BOTS ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to add bots is disabled on this server.\\n\"" );
			return;
		}
		// addbot <name> <skill> <team> <delay>
		Com_sprintf( level.voteString, sizeof( level.voteString ), "addbot %s %s", arg2, arg3 ); // simplify for now, maybe parse better
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "addbot %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "kick" ) ) {
		int             clientNum;

		if ( ( g_voteFlags.integer & VF_NO_KICK ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to kick a player is disabled on this server.\\n\"" );
			return;
		}

		if ( !arg2[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"Missing player name.\\n\"" );
			return;
		}

		if ( !Q_stricmp( arg2, "all" ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to kick all players is not allowed.\\n\"" );
			return;
		}

		clientNum = ClientNumberFromString( ent, arg2 );
		if ( clientNum == -1 ) {
			return;
		}

		if ( level.clients[clientNum].pers.localClient ) {
			trap_SendServerCommand( ent-g_entities, "print \"Cannot call a vote on the server host.\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "clientkick %d", clientNum );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "kick %s", level.clients[clientNum].pers.netname );
		voteSelection = G_VoteSelectionKey( arg1, level.clients[clientNum].pers.netname );
	} else if ( !Q_stricmp( arg1, "clientkick" ) ) {
		int             clientNum;

		if ( ( g_voteFlags.integer & VF_NO_KICK ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to kick a player is disabled on this server.\\n\"" );
			return;
		}

		clientNum = atoi( arg2 );
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid client slot.\n\"" );
			return;
		}

		if ( !g_entities[clientNum].inuse ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid player id.\n\"" );
			return;
		}

		if ( level.clients[clientNum].pers.localClient ) {
			trap_SendServerCommand( ent-g_entities, "print \"Cannot call a vote on the server host.\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "clientkick %d", clientNum );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "clientkick %d", clientNum );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "timelimit" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_TIME_LIMIT ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the games time limit is disabled on this server.\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "timelimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "timelimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "fraglimit" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_FRAG_LIMIT ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the games frag limit is disabled on this server.\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "fraglimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "fraglimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "scorelimit" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "scorelimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "scorelimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "roundlimit" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "roundlimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "roundlimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "cointoss" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_RANDOM ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to coin toss is disabled on this server.\\n\"" );
			return;
		}
		if ( arg2[0] ) {
			if ( Q_stricmp( arg2, "heads" ) && Q_stricmp( arg2, "h" )
					&& Q_stricmp( arg2, "tails" ) && Q_stricmp( arg2, "t" ) ) {
				trap_SendServerCommand( ent-g_entities, "print \"Valid cointoss parameters are:    ^5heads    ^5tails ^7\\n\"" );
				return;
			}
			Com_sprintf( level.voteString, sizeof( level.voteString ), "cointoss %s", arg2 );
			Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "cointoss %s", arg2 );
			voteSelection = G_VoteSelectionKey( arg1, arg2 );
		} else {
			Com_sprintf( level.voteString, sizeof( level.voteString ), "cointoss" );
			Q_strncpyz( level.voteDisplayString, "Coin Toss", sizeof( level.voteDisplayString ) );
			voteSelection = G_VoteSelectionKey( arg1, NULL );
		}
	} else if ( !Q_stricmp( arg1, "random" ) ) {
		int upperLimit;

		if ( ( g_voteFlags.integer & VF_NO_RANDOM ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Random number generation is disabled on this server.\\n\"" );
			return;
		}
		if ( !G_VoteArgumentIsUnsignedInteger( arg2 ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid upper limit, parameter must be an integer.\\n\"" );
			return;
		}

		upperLimit = atoi( arg2 );
		if ( upperLimit < 2 || upperLimit > 100 ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid upper limit. (Valid Range: 2 - 100)\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "random %d", upperLimit );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "random %d", upperLimit );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "loadouts" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_LOADOUTS ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to alter loadouts is disabled on this server.\\n\"" );
			return;
		}
		if ( midGame ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to alter loadouts is only allowed during the warm up period.\\n\"" );
			return;
		}
		if ( Q_stricmp( arg2, "on" ) && Q_stricmp( arg2, "off" ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"^3Valid loadout options are:    ^5ON    ^5OFF^7\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "loadouts %s", arg2 );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "loadouts %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "ammo" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_AMMO ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to alter the ammo system is disabled on this server.\\n\"" );
			return;
		}
		if ( midGame ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to alter the ammo system is only allowed during the warm up period.\\n\"" );
			return;
		}
		if ( Q_stricmp( arg2, "global" ) && Q_stricmp( arg2, "weap" ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"^3Valid ammo options are:    ^5GLOBAL    ^5WEAP^7\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "ammo %s", arg2 );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "ammo %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "timers" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_TIMERS ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to alter the item timers is disabled on this server.\\n\"" );
			return;
		}
		if ( midGame ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to alter the item timers is only allowed during the warm up period.\\n\"" );
			return;
		}
		if ( Q_stricmp( arg2, "on" ) && Q_stricmp( arg2, "off" ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"^3Valid item timer options are:    ^5ON    ^5OFF^7\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "timers %s", arg2 );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "timers %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "weaprespawn" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_WEAPRESPAWN ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the weapon respawn time is disabled on this server.\\n\"" );
			return;
		}
		if ( !arg2[0] ) {
			trap_SendServerCommand( ent-g_entities, "print \"Missing desired weapon respawn time.\\n\"" );
			return;
		}
		if ( !G_VoteArgumentIsUnsignedInteger( arg2 ) ) {
			trap_SendServerCommand( ent-g_entities, "print \"Invalid desired weapon respawn time, parameter must be an integer.\\n\"" );
			return;
		}

		Com_sprintf( level.voteString, sizeof( level.voteString ), "weaprespawn %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "weaprespawn %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "randommap" ) ) {
		if ( ( g_voteFlags.integer & VF_NO_MAP ) && !privilegedCallVote ) {
			trap_SendServerCommand( ent-g_entities, "print \"Voting to change the map being played is disabled on this server.\\n\"" );
			return;
		}
		Com_sprintf( level.voteString, sizeof( level.voteString ), "randommap" );
		Q_strncpyz( level.voteDisplayString, "Random Map", sizeof( level.voteDisplayString ) );
		voteSelection = G_VoteSelectionKey( arg1, NULL );
	} else if ( !Q_stricmp( arg1, "ruleset" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "ruleset %s", arg2 );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "ruleset %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "mercylimit" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "mercylimit %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "mercylimit %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "floodprot" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_floodprot_maxcount %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "floodprot %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_friendlyFire" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_friendlyFire %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_friendlyFire %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_gravity" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_gravity %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_gravity %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_speed" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_speed %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_speed %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else if ( !Q_stricmp( arg1, "g_doWarmup" ) ) {
		Com_sprintf( level.voteString, sizeof( level.voteString ), "g_doWarmup %d", atoi( arg2 ) );
		Com_sprintf( level.voteDisplayString, sizeof( level.voteDisplayString ), "g_doWarmup %s", arg2 );
		voteSelection = G_VoteSelectionKey( arg1, arg2 );
	} else {
		trap_SendServerCommand( ent-g_entities, "print \"^3Callvote commands:\\n\"" );
		trap_SendServerCommand( ent-g_entities,
			va( "print \"^%imap           ^%inextmap        ^%imap_restart   ^7\\n\"",
				G_CallVoteHelpColor( VF_NO_MAP ),
				G_CallVoteHelpColor( VF_NO_NEXTMAP ),
				G_CallVoteHelpColor( VF_NO_MAP_RESTART ) ) );
		trap_SendServerCommand( ent-g_entities,
			va( "print \"^%ikick          ^%iclientkick                      ^7\\n\"",
				G_CallVoteHelpColor( VF_NO_KICK ),
				G_CallVoteHelpColor( VF_NO_KICK ) ) );
		trap_SendServerCommand( ent-g_entities,
			va( "print \"^%ishuffle       ^%iteamsize       ^%icointoss      ^7\\n\"",
				G_CallVoteHelpColor( VF_NO_SHUFFLE ),
				G_CallVoteHelpColor( VF_NO_TEAMSIZE ),
				G_CallVoteHelpColor( VF_NO_RANDOM ) ) );
		trap_SendServerCommand( ent-g_entities,
			va( "print \"^%itimelimit     ^%ifraglimit      ^%iweaprespawn   ^7\\n\"",
				G_CallVoteHelpColor( VF_NO_TIME_LIMIT ),
				G_CallVoteHelpColor( VF_NO_FRAG_LIMIT ),
				G_CallVoteHelpColor( VF_NO_WEAPRESPAWN ) ) );
		trap_SendServerCommand( ent-g_entities,
			va( "print \"^%iloadouts      ^%iammo           ^%itimers        ^7\\n\"",
				G_CallVoteHelpColor( VF_NO_LOADOUTS ),
				G_CallVoteHelpColor( VF_NO_AMMO ),
				G_CallVoteHelpColor( VF_NO_TIMERS ) ) );
		trap_SendServerCommand( ent-g_entities, "print \"Usage: ^3\\\\callvote <command> <params>^7\\n\"" );
		return;
	}

	if ( voteSelection != -1 && client->pers.voteDelayTime > 0
			&& client->pers.voteLastSelection == voteSelection
			&& level.time - client->pers.voteDelayTime < VOTE_THROTTLE_MSEC ) {
		trap_SendServerCommand( ent-g_entities, "print \"You already voted for this option.\\n\"" );
		return;
	}

	client->pers.voteCount++;
	G_RegisterVoteCall( client, ent-g_entities, voteSelection );
	trap_SendServerCommand( -1, va( "print \"%s called a vote.\\n\"", client->pers.netname ) );

	level.voteTime = level.time;
	level.voteYes = 1;
	level.voteNo = 0;

	if ( delayMsec > 0 ) {
		level.voteEligibleTime = level.time + delayMsec;
	}

	for ( voteSelection = 0 ; voteSelection < level.maxclients ; voteSelection++ ) {
		if ( level.clients[voteSelection].pers.connected != CON_CONNECTED || ( g_entities[voteSelection].r.svFlags & SVF_BOT ) ) {
			level.clients[voteSelection].pers.voteState = VOTE_STATE_NONE;
		} else if ( level.clients[voteSelection].sess.sessionTeam == TEAM_SPECTATOR && !g_allowSpecVote.integer ) {
			level.clients[voteSelection].pers.voteState = VOTE_STATE_NONE;
		} else {
			level.clients[voteSelection].pers.voteState = VOTE_STATE_ELIGIBLE;
		}
		level.clients[voteSelection].ps.eFlags &= ~EF_VOTED;
	}
	client->pers.voteState = VOTE_STATE_YES;
	client->ps.eFlags |= EF_VOTED;

	trap_SetConfigstring( CS_VOTE_TIME, va( "%i", level.voteTime ) );
	trap_SetConfigstring( CS_VOTE_STRING, level.voteDisplayString );
	G_UpdateVoteCounts();
}


/*
=============
Cmd_Vote_f

Process a client's ballot during an active vote, applying spectator and throttle rules.
=============
*/
void Cmd_Vote_f( gentity_t *ent ) {
	char		msg[64];
	voteState_t	voteState;
	gclient_t	*client;

	if ( !level.voteTime ) {
		trap_SendServerCommand( ent-g_entities, "print \"No vote in progress.\n\"" );
		return;
	}

	client = ent->client;
	if ( !client ) {
		return;
	}

	trap_Argv( 1, msg, sizeof( msg ) );
	if ( client->sess.sessionTeam == TEAM_SPECTATOR && !g_allowSpecVote.integer ) {
		trap_SendServerCommand( ent-g_entities, "print \"You may not participate in this vote.\n\"" );
		return;
	}
	if ( client->pers.voteState == VOTE_STATE_NONE ) {
		trap_SendServerCommand( ent-g_entities, "print \"You may not participate in this vote.\n\"" );
		return;
	}

	if ( client->ps.eFlags & EF_VOTED ) {
		trap_SendServerCommand( ent-g_entities, "print \"Vote already cast.\n\"" );
		return;
	}

	if ( client->pers.voteDelayTime > 0 && level.time - client->pers.voteDelayTime < VOTE_THROTTLE_MSEC ) {
		trap_SendServerCommand( ent-g_entities, "print \"You may only vote once every 2 seconds.\n\"" );
		return;
	}

	voteState = VOTE_STATE_NONE;
	if ( client->sess.privilege >= PRIV_MOD ) {
		if ( !Q_stricmp( msg, "pass" ) ) {
			voteState = VOTE_STATE_FORCE_PASS;
		} else if ( !Q_stricmp( msg, "veto" ) ) {
			voteState = VOTE_STATE_FORCE_VETO;
		}
	}

	if ( voteState == VOTE_STATE_NONE ) {
		int voteSelection;

		voteSelection = atoi( msg );
		if ( voteSelection <= 0 ) {
			if ( msg[0] == 'y' || msg[0] == 'Y' ) {
				voteSelection = 1;
			} else if ( msg[0] == 'n' || msg[0] == 'N' ) {
				voteSelection = 2;
			}
		}

		if ( msg[0] == 'y' || msg[0] == 'Y' || msg[0] == '1' ) {
			voteState = VOTE_STATE_YES;
		} else {
			voteState = VOTE_STATE_NO;
		}
	}

	if ( client->pers.voteLastSelection == voteState ) {
		trap_SendServerCommand( ent-g_entities, "print \"You already voted for this arena.\n\"" );
		return;
	}

	trap_SendServerCommand( ent-g_entities, "print \"Vote cast.\n\"" );

	client->ps.eFlags |= EF_VOTED;
	client->pers.voteState = voteState;
	client->pers.voteDelayTime = level.time;
	client->pers.voteLastSelection = voteState;
	client->pers.voteLastEnableFrame = -1;

	trap_SendServerCommand( ent-g_entities, "disable_vote_ui" );
	G_UpdateVoteCounts();

	// a majority will be determined in CheckVote, which will also account
	// for players entering or leaving
}

/*
==================
Cmd_CallTeamVote_f
==================
*/
void Cmd_CallTeamVote_f( gentity_t *ent ) {
	int		i, team, cs_offset;
	char	arg1[MAX_STRING_TOKENS];
	char	arg2[MAX_STRING_TOKENS];
	int		voteSelection;

	team = ent->client->sess.sessionTeam;
	voteSelection = -1;
	if ( team == TEAM_RED )
		cs_offset = 0;
	else if ( team == TEAM_BLUE )
		cs_offset = 1;
	else
		return;

	if ( !g_allowVote.integer ) {
		trap_SendServerCommand( ent-g_entities, "print \"Voting not allowed here.\n\"" );
		return;
	}

	if ( level.teamVoteTime[cs_offset] ) {
		trap_SendServerCommand( ent-g_entities, "print \"A team vote is already in progress.\n\"" );
		return;
	}
	if ( ent->client->pers.teamVoteCount >= MAX_VOTE_COUNT ) {
		trap_SendServerCommand( ent-g_entities, "print \"You have called the maximum number of team votes.\n\"" );
		return;
	}
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Not allowed to call a vote as spectator.\n\"" );
		return;
	}

	// make sure it is a valid command to vote on
	trap_Argv( 1, arg1, sizeof( arg1 ) );
	arg2[0] = '\0';
	for ( i = 2; i < trap_Argc(); i++ ) {
		if (i > 2)
			strcat(arg2, " ");
		trap_Argv( i, &arg2[strlen(arg2)], sizeof( arg2 ) - strlen(arg2) );
	}

	if( strchr( arg1, ';' ) || strchr( arg2, ';' ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid vote string.\n\"" );
		return;
	}

	if ( !Q_stricmp( arg1, "leader" ) ) {
		char netname[MAX_NETNAME], leader[MAX_NETNAME];

		if ( !arg2[0] ) {
			i = ent->client->ps.clientNum;
			voteSelection = i;
		}
		else {
			// numeric values are just slot numbers
			for (i = 0; i < 3; i++) {
				if ( !arg2[i] || arg2[i] < '0' || arg2[i] > '9' )
					break;
			}
			if ( i >= 3 || !arg2[i]) {
				i = atoi( arg2 );
				voteSelection = i;
				if ( i < 0 || i >= level.maxclients ) {
					trap_SendServerCommand( ent-g_entities, va("print \"Bad client slot: %i\n\"", i) );
					return;
				}

				if ( !g_entities[i].inuse ) {
					trap_SendServerCommand( ent-g_entities, va("print \"Client %i is not active\n\"", i) );
					return;
				}
			}
			else {
				Q_strncpyz(leader, arg2, sizeof(leader));
				Q_CleanStr(leader);
				for ( i = 0 ; i < level.maxclients ; i++ ) {
					if ( level.clients[i].pers.connected == CON_DISCONNECTED )
						continue;
					if (level.clients[i].sess.sessionTeam != team)
						continue;
					Q_strncpyz(netname, level.clients[i].pers.netname, sizeof(netname));
					Q_CleanStr(netname);
					if ( !Q_stricmp(netname, leader) ) {
						break;
					}
				}
				if ( i >= level.maxclients ) {
					trap_SendServerCommand( ent-g_entities, va("print \"%s is not a valid player on your team.\n\"", arg2) );
					return;
				}
			}
		}
		voteSelection = i;
		Com_sprintf(arg2, sizeof(arg2), "%d", i);
	} else {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid vote string.\n\"" );
		trap_SendServerCommand( ent-g_entities, "print \"Team vote commands are: leader <player>.\n\"" );
		return;
	}

	Com_sprintf( level.teamVoteString[cs_offset], sizeof( level.teamVoteString[cs_offset] ), "%s %s", arg1, arg2 );
	G_RegisterVoteCall( ent->client, ent - g_entities, voteSelection );

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].pers.connected == CON_DISCONNECTED )
			continue;
		if (level.clients[i].sess.sessionTeam == team)
			trap_SendServerCommand( i, va("print \"%s called a team vote.\n\"", ent->client->pers.netname ) );
	}

	// start the voting, the caller autoamtically votes yes
	level.teamVoteTime[cs_offset] = level.time;
	level.teamVoteYes[cs_offset] = 1;
	level.teamVoteNo[cs_offset] = 0;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam == team)
			level.clients[i].ps.eFlags &= ~EF_TEAMVOTED;
	}
	ent->client->ps.eFlags |= EF_TEAMVOTED;

	trap_SetConfigstring( CS_TEAMVOTE_TIME + cs_offset, va("%i", level.teamVoteTime[cs_offset] ) );
	trap_SetConfigstring( CS_TEAMVOTE_STRING + cs_offset, level.teamVoteString[cs_offset] );
	trap_SetConfigstring( CS_TEAMVOTE_YES + cs_offset, va("%i", level.teamVoteYes[cs_offset] ) );
	trap_SetConfigstring( CS_TEAMVOTE_NO + cs_offset, va("%i", level.teamVoteNo[cs_offset] ) );
}

/*
==================
Cmd_TeamVote_f
==================
*/
void Cmd_TeamVote_f( gentity_t *ent ) {
	int			team, cs_offset;
	char		msg[64];

	team = ent->client->sess.sessionTeam;
	if ( team == TEAM_RED )
		cs_offset = 0;
	else if ( team == TEAM_BLUE )
		cs_offset = 1;
	else
		return;

	if ( !level.teamVoteTime[cs_offset] ) {
		trap_SendServerCommand( ent-g_entities, "print \"No team vote in progress.\n\"" );
		return;
	}
	if ( ent->client->ps.eFlags & EF_TEAMVOTED ) {
		trap_SendServerCommand( ent-g_entities, "print \"Team vote already cast.\n\"" );
		return;
	}
	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Not allowed to vote as spectator.\n\"" );
		return;
	}

	trap_SendServerCommand( ent-g_entities, "print \"Team vote cast.\n\"" );

	ent->client->ps.eFlags |= EF_TEAMVOTED;

	trap_Argv( 1, msg, sizeof( msg ) );

	if ( msg[0] == 'y' || msg[1] == 'Y' || msg[1] == '1' ) {
		level.teamVoteYes[cs_offset]++;
		trap_SetConfigstring( CS_TEAMVOTE_YES + cs_offset, va("%i", level.teamVoteYes[cs_offset] ) );
	} else {
		level.teamVoteNo[cs_offset]++;
		trap_SetConfigstring( CS_TEAMVOTE_NO + cs_offset, va("%i", level.teamVoteNo[cs_offset] ) );	
	}

	// a majority will be determined in TeamCheckVote, which will also account
	// for players entering or leaving
}


/*
=================
Cmd_SetViewpos_f
=================
*/
void Cmd_SetViewpos_f( gentity_t *ent ) {
	vec3_t		origin, angles;
	char		buffer[MAX_TOKEN_CHARS];
	int			i;

	if ( !g_cheats.integer ) {
		trap_SendServerCommand( ent-g_entities, va("print \"Cheats are not enabled on this server.\n\""));
		return;
	}
	if ( trap_Argc() != 5 ) {
		trap_SendServerCommand( ent-g_entities, va("print \"usage: setviewpos x y z yaw\n\""));
		return;
	}

	VectorClear( angles );
	for ( i = 0 ; i < 3 ; i++ ) {
		trap_Argv( i + 1, buffer, sizeof( buffer ) );
		origin[i] = atof( buffer );
	}

	trap_Argv( 4, buffer, sizeof( buffer ) );
	angles[YAW] = atof( buffer );

	TeleportPlayer( ent, origin, angles );
}



/*
==================
Cmd_Elo_f
==================
*/
void Cmd_Elo_f( gentity_t *ent ) {
	int clientNum;
	char arg[MAX_TOKEN_CHARS];
	gclient_t *target;

	if ( trap_Argc() < 2 ) {
		clientNum = ent->s.number;
	} else {
		trap_Argv( 1, arg, sizeof( arg ) );
		clientNum = ClientNumberFromString( ent, arg );
	}

	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}

	target = &level.clients[clientNum];
	if ( target->pers.connected != CON_CONNECTED ) {
		return;
	}

	trap_SendServerCommand( ent-g_entities, va( "print \"^7Elo for %s^7: %i (Skill1: %i, Skill2: %i)\n\"",
		target->pers.netname,
		target->sess.skill1,
		target->sess.skill1,
		target->sess.skill2 ) );
}

/*
=================
Cmd_Stats_f
=================
*/
void Cmd_Stats_f( gentity_t *ent ) {
	int i, shots, hits, accuracy;
	int totalShots = 0, totalHits = 0;
	gclient_t *client = ent->client;
	char *weaponNames[] = {
		"Gauntlet", "Machinegun", "HMG", "Shotgun", "Grenade", "Rocket",
		"Lightning", "Railgun", "Plasma", "BFG", "Grapple", "Nailgun",
		"Prox Mine", "Chaingun"
	};
	int weaponIndices[] = {
		WP_GAUNTLET, WP_MACHINEGUN, WP_HEAVY_MACHINEGUN, WP_SHOTGUN, WP_GRENADE_LAUNCHER, WP_ROCKET_LAUNCHER,
		WP_LIGHTNING, WP_RAILGUN, WP_PLASMAGUN, WP_BFG, WP_GRAPPLING_HOOK, WP_NAILGUN,
		WP_PROX_LAUNCHER, WP_CHAINGUN
	};

	if ( !client ) {
		return;
	}

	trap_SendServerCommand( ent-g_entities, va("print \"\nWeapon Stats for %s\n\"", client->pers.netname) );
	trap_SendServerCommand( ent-g_entities, "print \"Weapon     Accuracy   Hits   Shots\n\"" );
	trap_SendServerCommand( ent-g_entities, "print \"----------------------------------\n\"" );

	for ( i = 0; i < sizeof(weaponIndices) / sizeof(weaponIndices[0]); i++ ) {
		int w = weaponIndices[i];
		shots = client->pers.accuracy_shots[w];
		hits = client->pers.accuracy_hits[w];
		if ( shots > 0 ) {
			accuracy = hits * 100 / shots;
		} else {
			accuracy = 0;
		}

		if ( shots > 0 ) {
			trap_SendServerCommand( ent-g_entities, va("print \"%-10s %5i%% %6i %7i\n\"",
				weaponNames[i], accuracy, hits, shots) );
			totalShots += shots;
			totalHits += hits;
		}
	}

	if ( totalShots > 0 ) {
		accuracy = totalHits * 100 / totalShots;
	} else {
		accuracy = 0;
	}

	trap_SendServerCommand( ent-g_entities, "print \"----------------------------------\n\"" );
	trap_SendServerCommand( ent-g_entities, va("print \"Total      %5i%% %6i %7i\n\"",
		accuracy, totalHits, totalShots) );
	trap_SendServerCommand( ent-g_entities, va("print \"\nDamage Given: %i  Damage Received: %i\n\"",
		client->pers.damageGiven, client->pers.damageReceived) );
}

static qboolean G_ClientCanControlTimeouts( gentity_t *ent, team_t *teamOut ) {
	team_t team;

	if ( !ent->client ) {
		return qfalse;
	}

	if ( level.trainingMapActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"Timeouts are disabled in training.\n\"" );
		return qfalse;
	}

	team = ent->client->sess.sessionTeam;
	if ( team == TEAM_SPECTATOR ) {
		trap_SendServerCommand( ent-g_entities, "print \"Spectators cannot control timeouts.\\n\"" );
		return qfalse;
	}

	if ( g_gametype.integer != GT_TOURNAMENT && g_gametype.integer < GT_TEAM ) {
		trap_SendServerCommand( ent-g_entities, "print \"Timeouts are disabled in this gametype.\\n\"" );
		return qfalse;
	}

	if ( g_gametype.integer >= GT_TEAM ) {
		if ( team != TEAM_RED && team != TEAM_BLUE ) {
			trap_SendServerCommand( ent-g_entities, "print \"Join a team before calling a timeout.\\n\"" );
			return qfalse;
		}
		*teamOut = team;
	} else {
		*teamOut = TEAM_FREE;
	}

	return qtrue;
}

/*
=============
G_TimeoutCallerName

Returns the retail-facing timeout caller label for player and server-owned pauses.
=============
*/
static const char *G_TimeoutCallerName( gentity_t *ent ) {
	if ( ent && ent->client ) {
		return ent->client->pers.netname;
	}

	return "The server";
}

/*
=============
G_StartTimeout

Starts a timed timeout or indefinite pause and publishes the updated timeout state.
=============
*/
static qboolean G_StartTimeout( gentity_t *ent, int durationSeconds ) {
	team_t	team;

	if ( level.timeoutActive ) {
		return qfalse;
	}

	team = TEAM_FREE;
	if ( ent && ent->client ) {
		if ( g_gametype.integer >= GT_TEAM ) {
			team = ent->client->sess.sessionTeam;
			if ( team != TEAM_RED && team != TEAM_BLUE ) {
				team = TEAM_FREE;
			}
		}
		level.timeoutOwner = ent->client->ps.clientNum;
	} else {
		level.timeoutOwner = -1;
	}

	level.timeoutActive = qtrue;
	level.timeoutTeam = team;
	level.timeoutStartTime = level.time;
	if ( durationSeconds > 0 ) {
		level.timeoutExpireTime = level.time + durationSeconds * 1000;
	} else {
		level.timeoutExpireTime = 0;
	}

	if ( durationSeconds > 0 ) {
		trap_SendServerCommand( -1,
			va( "print \"%s has called timeout (%ds)\\n\"", G_TimeoutCallerName( ent ), durationSeconds ) );
	} else {
		trap_SendServerCommand( -1,
			va( "print \"%s has paused the match\\n\"", G_TimeoutCallerName( ent ) ) );
	}

	G_UpdateMatchStateConfigString();
	return qtrue;
}

/*
=============
G_BeginTimein

Arms the retail-style five-second resume countdown for the active timeout.
=============
*/
static qboolean G_BeginTimein( gentity_t *ent ) {
	if ( !level.timeoutActive ) {
		return qfalse;
	}

	if ( ent && ent->client && level.timeoutOwner != ent->client->ps.clientNum ) {
		trap_SendServerCommand( ent-g_entities, "print \"You did not call the current timeout\n\"" );
		return qfalse;
	}

	level.timeoutExpireTime = level.time + 5000;
	trap_SendServerCommand( -1,
		va( "print \"%s has called timein\\n\"", G_TimeoutCallerName( ent ) ) );
	G_UpdateMatchStateConfigString();
	return qtrue;
}

void Cmd_Timeout_f( gentity_t *ent ) {
	team_t team;
	int remaining;
	int timeoutLength;

	if ( level.timeoutActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"A timeout is already active.\\n\"" );
		return;
	}

	if ( !G_ClientCanControlTimeouts( ent, &team ) ) {
		return;
	}

	timeoutLength = g_matchFactoryConfig.timeoutLengthSeconds;
	if ( timeoutLength <= 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Timeouts are not enabled on this server.\n\"" );
		return;
	}

	remaining = level.timeoutRemaining[team];
	if ( remaining <= 0 ) {
		if ( g_gametype.integer >= GT_TEAM ) {
			trap_SendServerCommand( ent-g_entities, "print \"Your team has no timeouts left to call\n\"" );
		} else {
			trap_SendServerCommand( ent-g_entities, "print \"You have no timeouts left to call\n\"" );
		}
		return;
	}

	level.timeoutRemaining[team] = remaining - 1;
	if ( level.timeoutRemaining[team] < 0 ) {
		level.timeoutRemaining[team] = 0;
	}

	if ( !G_StartTimeout( ent, timeoutLength ) ) {
		level.timeoutRemaining[team] = remaining;
	}
}

/*
=============
Cmd_Pause_f

Starts an indefinite pause without consuming the timeout pool, or lets a player claim a server-owned pause.
=============
*/
void Cmd_Pause_f( gentity_t *ent ) {
	team_t team;

	if ( !G_ClientCanControlTimeouts( ent, &team ) ) {
		return;
	}

	if ( !level.timeoutActive ) {
		G_StartTimeout( ent, 0 );
		return;
	}

	if ( level.timeoutOwner < 0 ) {
		level.timeoutOwner = ent->client->ps.clientNum;
		if ( g_gametype.integer >= GT_TEAM && team >= TEAM_RED && team < TEAM_NUM_TEAMS ) {
			level.timeoutTeam = team;
		}
		trap_SendServerCommand( ent-g_entities, "print \"You have taken ownership of the current timeout\n\"" );
		G_UpdateMatchStateConfigString();
		return;
	}

	trap_SendServerCommand( ent-g_entities, "print \"A timeout is already active.\n\"" );
}

void Cmd_Timein_f( gentity_t *ent ) {
	if ( level.trainingMapActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"Training matches do not support timeouts.\n\"" );
		return;
	}

	if ( !level.timeoutActive ) {
		trap_SendServerCommand( ent-g_entities, "print \"No timeout in progress.\\n\"" );
		return;
	}

	G_BeginTimein( ent );
}

/*
=================
Cmd_Complaint_f

Processes friendly-fire complaint responses from the victim.
=================
*/
static void Cmd_Complaint_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	gclient_t *client;
	int attackerNum;
	gentity_t *attacker;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;

	if ( client->complaintClient < 0 ) {
		client->complaintClient = -1;
		client->complaintEndTime = 0;
		return;
	}

	if ( client->complaintEndTime > 0 && client->complaintEndTime <= level.time ) {
		G_ComplaintResolve( ent, qfalse );
		return;
	}

	attackerNum = client->complaintClient;

	if ( attackerNum < 0 || attackerNum >= level.maxclients ) {
		client->complaintClient = -1;
		client->complaintEndTime = 0;
		trap_SendServerCommand( ent - g_entities, "complaint -3" );
		return;
	}

	attacker = &g_entities[attackerNum];

	if ( !attacker->client || attacker->client->pers.connected != CON_CONNECTED ) {
		client->complaintClient = -1;
		client->complaintEndTime = 0;
		trap_SendServerCommand( ent - g_entities, "complaint -3" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );

	if ( arg[0] == 'y' || arg[0] == 'Y' || arg[0] == '1' ) {
		G_ComplaintResolve( ent, qtrue );
		return;
	}

	G_ComplaintResolve( ent, qfalse );
}

/*
==================
Cmd_Ruleset_f
==================
*/
void Cmd_Ruleset_f( gentity_t *ent ) {
	trap_SendServerCommand( ent - g_entities, va( "print \"Current ruleset: %s\n\"", g_ruleset.string ) );
}

/*
==================
Cmd_Invite_f
==================
*/
void Cmd_Invite_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	int clientNum;
	gentity_t *target;
	unsigned int steamIdLow;
	unsigned int steamIdHigh;
	unsigned long long steamIdValue;
	char steamIdString[MAX_ADMIN_STEAMID_LENGTH];
	int priv;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( !trap_VerifySteamAuth( ent->s.number ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Failed to verify Steam auth token\n\"" );
		return;
	}

	if ( !trap_GetSteamId( ent->s.number, &steamIdLow, &steamIdHigh ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Failed to verify Steam auth token\n\"" );
		return;
	}

	steamIdValue = ( (unsigned long long)steamIdHigh << 32 ) | steamIdLow;
	Com_sprintf( steamIdString, sizeof( steamIdString ), "%llu", steamIdValue );
	priv = G_AdminAccessForSteamID( steamIdString );
	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: invite <client>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	clientNum = ClientNumberFromString( ent, arg );
	if ( clientNum < 0 ) {
		return;
	}

	target = &g_entities[clientNum];
	trap_SendServerCommand( ent-g_entities, va("print \"Invitation sent to %s.\n\"", target->client->pers.netname) );
	trap_SendServerCommand( target-g_entities, va("cp \"You have been invited by %s.\n\"", ent->client->pers.netname) );
}

/*
==================
Cmd_Revoke_f
==================
*/
void Cmd_Revoke_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	int clientNum;
	gentity_t *target;
	unsigned int steamIdLow;
	unsigned int steamIdHigh;
	unsigned long long steamIdValue;
	char steamIdString[MAX_ADMIN_STEAMID_LENGTH];
	int priv;

	if ( !ent || !ent->client ) return;

	if ( !trap_VerifySteamAuth( ent->s.number ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Failed to verify Steam auth token\n\"" );
		return;
	}

	if ( !trap_GetSteamId( ent->s.number, &steamIdLow, &steamIdHigh ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Failed to verify Steam auth token\n\"" );
		return;
	}

	steamIdValue = ( (unsigned long long)steamIdHigh << 32 ) | steamIdLow;
	Com_sprintf( steamIdString, sizeof( steamIdString ), "%llu", steamIdValue );
	priv = G_AdminAccessForSteamID( steamIdString );
	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: revoke <client>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	clientNum = ClientNumberFromString( ent, arg );
	if ( clientNum < 0 ) {
		return;
	}

	target = &g_entities[clientNum];
	// In a full implementation, this would remove the client from an invitation list or similar.
	// For now, we simulate it.
	trap_SendServerCommand( ent-g_entities, va("print \"Invitation revoked for %s.\n\"", target->client->pers.netname) );
}

/*
==================
Cmd_Whois_f
==================
*/
void Cmd_Whois_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	int clientNum;
	gentity_t *target;
	char userinfo[MAX_INFO_STRING];
	const char *ip;
	const char *steamid;

	if ( !ent || !ent->client ) return;

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: whois <client>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	clientNum = ClientNumberFromString( ent, arg );
	if ( clientNum < 0 ) return;

	target = &g_entities[clientNum];
	trap_GetUserinfo( clientNum, userinfo, sizeof(userinfo) );
	ip = Info_ValueForKey( userinfo, "ip" );
	steamid = Info_ValueForKey( userinfo, "steamid" );

	trap_SendServerCommand( ent-g_entities, va("print \"name: %s\nclient: %i\nIP: %s\nSteamID: %s\n\"",
		target->client->pers.netname, clientNum, ip, steamid ) );
}

/*
==================
Cmd_Mute_f
==================
*/
void Cmd_Mute_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	int clientNum;
	gentity_t *target;
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: mute <client>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	clientNum = ClientNumberFromString( ent, arg );
	if ( clientNum < 0 ) return;

	target = &g_entities[clientNum];
	target->client->sess.muted = qtrue;
	trap_SendServerCommand( ent-g_entities, va("print \"%s muted.\n\"", target->client->pers.netname) );
	trap_SendServerCommand( target-g_entities, "print \"You have been muted.\n\"" );
}

/*
==================
Cmd_Unmute_f
==================
*/
void Cmd_Unmute_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	int clientNum;
	gentity_t *target;
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: unmute <client>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	clientNum = ClientNumberFromString( ent, arg );
	if ( clientNum < 0 ) return;

	target = &g_entities[clientNum];
	target->client->sess.muted = qfalse;
	trap_SendServerCommand( ent-g_entities, va("print \"%s unmuted.\n\"", target->client->pers.netname) );
	trap_SendServerCommand( target-g_entities, "print \"You have been unmuted.\n\"" );
}

/*
==================
Cmd_Lock_f
==================
*/
void Cmd_Lock_f( gentity_t *ent ) {
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	trap_Cvar_Set( "g_teamSpawnAsSpec", "1" );
	trap_SendServerCommand( -1, "print \"Teams locked by admin.\n\"" );
}

/*
==================
Cmd_Unlock_f
==================
*/
void Cmd_Unlock_f( gentity_t *ent ) {
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	trap_Cvar_Set( "g_teamSpawnAsSpec", "0" );
	trap_SendServerCommand( -1, "print \"Teams unlocked by admin.\n\"" );
}

/*
==================
Cmd_PutTeam_f
==================
*/
void Cmd_PutTeam_f( gentity_t *ent ) {
	char arg1[MAX_TOKEN_CHARS];
	char arg2[MAX_TOKEN_CHARS];
	int clientNum;
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 3 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: putteam <client> <team>\n\"" );
		return;
	}

	trap_Argv( 1, arg1, sizeof( arg1 ) );
	trap_Argv( 2, arg2, sizeof( arg2 ) );

	clientNum = ClientNumberFromString( ent, arg1 );
	if ( clientNum < 0 ) return;

	SetTeam( &g_entities[clientNum], arg2 );
}

/*
==================
Cmd_AllReady_f
==================
*/
void Cmd_AllReady_f( gentity_t *ent ) {
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	const char *blockedMessage;
	int priv;
	int i;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	blockedMessage = G_GetReadyUpBlockedMessage();
	if ( blockedMessage ) {
		trap_SendServerCommand( ent-g_entities, blockedMessage );
		return;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		if ( level.clients[i].pers.connected == CON_CONNECTED && level.clients[i].sess.sessionTeam != TEAM_SPECTATOR ) {
			G_SetClientReadyState( &level.clients[i], qtrue );
		}
	}
	trap_SendServerCommand( -1, "print \"All players set to ready by admin.\n\"" );
}

/*
==================
Cmd_Map_f
==================
*/
void Cmd_Map_f( gentity_t *ent ) {
	char map[MAX_TOKEN_CHARS];
	char factory[MAX_TOKEN_CHARS];
	char expandedMap[MAX_QPATH];
	fileHandle_t mapFile;
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	const factoryDefinition_t *factoryOverride;
	int priv;
	int mapLen;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_ADMIN ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: map <mapname> [factory]\n\"" );
		return;
	}

	trap_Argv( 1, map, sizeof( map ) );
	trap_Argv( 2, factory, sizeof( factory ) );

	// Sanitize map name to prevent command injection
	if ( strchr( map, ';' ) || strchr( map, '\n' ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid characters in map name.\n\"" );
		return;
	}
	if ( factory[0] && ( strchr( factory, ';' ) || strchr( factory, '\n' ) ) ) {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid characters in factory name.\n\"" );
		return;
	}

	Com_sprintf( expandedMap, sizeof( expandedMap ), "maps/%s.bsp", map );
	mapLen = trap_FS_FOpenFile( expandedMap, &mapFile, FS_READ );
	if ( mapLen < 0 ) {
		trap_SendServerCommand( ent-g_entities, "print \"Map does not exist.\n\"" );
		return;
	}
	trap_FS_FCloseFile( mapFile );

	factoryOverride = NULL;
	if ( factory[0] ) {
		factoryOverride = Factory_FindById( factory );
		if ( !factoryOverride ) {
			if ( ent ) {
				trap_SendServerCommand( ent - g_entities, "print \"Invalid factory specified.\\n\"" );
			} else {
				G_Printf( "Invalid factory specified.\n" );
			}
			return;
		}
		if ( !G_MapSupportsGametype( map, factoryOverride->baseGametype ) ) {
			trap_SendServerCommand( ent - g_entities, "print \"Map not supported for this gametype.\n\"" );
			return;
		}
		trap_SendConsoleCommand( EXEC_APPEND, va("map %s %s\n", map, factory) );
	} else {
		trap_SendConsoleCommand( EXEC_APPEND, va("map %s\n", map) );
	}
}

/*
==================
Cmd_Restart_f
==================
*/
void Cmd_Restart_f( gentity_t *ent ) {
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
}

/*
==================
Cmd_ShuffleTeams_f
==================
*/
void Cmd_ShuffleTeams_f( void ) {
	if ( !Team_IsAutoShuffleArmed() ) {
		G_AutoShuffleCountdown_Arm( 5000 );
		Team_ClampWarmupToShuffleCountdown();
		trap_SendServerCommand( -1, "print \"Teams will be shuffled in 5 seconds.\n\"" );
	}
}

/*
==================
Cmd_Shuffle_f
==================
*/
void Cmd_Shuffle_f( gentity_t *ent ) {
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	Cmd_ShuffleTeams_f();
}

/*
==================
Cmd_Teamsize_f
==================
*/
void Cmd_Teamsize_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: teamsize <size>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	trap_Cvar_Set( "g_teamSizeMin", arg );
	trap_SendServerCommand( -1, va("print \"Teamsize set to %s by admin.\n\"", arg) );
}

/*
==================
Cmd_Clan_f
==================
*/
void Cmd_Clan_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];

	// QL uses this to set clan tag. In Q3 base we usually use userinfo "clan" or "team".
	// Implementing as userinfo setter.
	if ( !ent || !ent->client ) return;

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: clan <tag>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	// Just print for now as full clan system requires more userinfo handling
	trap_SendServerCommand( ent-g_entities, "print \"Clan tag updated (simulated).\n\"" );
}

/*
==================
G_KickOrBanClient
==================
*/
static int G_KickOrBanClient( gentity_t *ent, char *targetToken, qboolean banTarget ) {
	int		clientNum;
	gentity_t	*target;

	if ( !targetToken || !targetToken[0] ) {
		return -1;
	}

	clientNum = ClientNumberFromString( ent, targetToken );
	if ( clientNum < 0 ) {
		return -1;
	}

	target = &g_entities[clientNum];
	if ( target->client && target->client->sess.privilege >= PRIV_ADMIN ) {
		if ( ent && ent->client ) {
			trap_SendServerCommand( ent-g_entities, "print \"Can not kick admins.\n\"" );
		}
		return -1;
	}

	if ( banTarget ) {
		char	targetUserinfo[MAX_INFO_STRING];
		char	*ip;

		trap_GetUserinfo( clientNum, targetUserinfo, sizeof( targetUserinfo ) );
		ip = Info_ValueForKey( targetUserinfo, "ip" );
		if ( ip && ip[0] ) {
			trap_SendConsoleCommand( EXEC_APPEND, va( "addip %s\n", ip ) );
		}
	}

	trap_SendConsoleCommand( EXEC_APPEND, va( "clientkick %d\n", clientNum ) );
	return clientNum;
}

/*
==================
Cmd_Kick_f
==================
*/
void Cmd_Kick_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: kick <player>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	G_KickOrBanClient( ent, arg, qfalse );
}

/*
==================
Cmd_Ban_f
==================
*/
void Cmd_Ban_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_ADMIN ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: ban <player>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	G_KickOrBanClient( ent, arg, qtrue );
}

/*
==================
Cmd_ClientKick_f
==================
*/
void Cmd_ClientKick_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	int clientNum;
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: clientkick <clientnum>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	clientNum = atoi( arg );
	if ( clientNum >= 0 && clientNum < level.maxclients ) {
		trap_SendConsoleCommand( EXEC_APPEND, va("clientkick %d\n", clientNum) );
	}
}

/*
==================
Cmd_Cointoss_f
==================
*/
void Cmd_Cointoss_f( gentity_t *ent ) {
	char	*msg;

	if ( rand() & 1 ) {
		msg = "Heads";
	} else {
		msg = "Tails";
	}

	trap_SendServerCommand( -1, va( "print \"%s throws a coin... ^3%s!^7\n\"", ent->client->pers.netname, msg ) );
}

/*
==================
Cmd_TimeLimit_f
==================
*/
void Cmd_TimeLimit_f( gentity_t *ent ) {
	char arg[MAX_TOKEN_CHARS];
	char userinfo[MAX_INFO_STRING];
	const char *steamId;
	int priv;

	if ( !ent || !ent->client ) return;

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_ADMIN ) {
		trap_SendServerCommand( ent-g_entities, "print \"Insufficient privileges.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: timelimit <limit>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	trap_Cvar_Set( "timelimit", arg );
	trap_SendServerCommand( -1, va("print \"Timelimit set to %s by admin.\n\"", arg) );
}

/*
==================
Cmd_Admin_f
==================
*/
void Cmd_Admin_f( gentity_t *ent ) {
	char        arg[MAX_TOKEN_CHARS];
	char        val[MAX_TOKEN_CHARS];
	int         priv;
	char        userinfo[MAX_INFO_STRING];
	const char  *steamId;

	if ( !ent || !ent->client ) {
		return;
	}

	trap_GetUserinfo( ent->s.number, userinfo, sizeof(userinfo) );
	steamId = Info_ValueForKey( userinfo, "steamid" );
	priv = G_AdminAccessForSteamID( steamId );

	if ( priv < PRIV_MOD ) {
		trap_SendServerCommand( ent - g_entities, "print \"You do not have access to admin commands.\n\"" );
		return;
	}

	if ( trap_Argc() < 2 ) {
		trap_SendServerCommand( ent - g_entities, "print \"usage: admin <command> [args]\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );

	if ( !Q_stricmp( arg, "kick" ) ) {
		int clientNum;

		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Argv( 2, val, sizeof( val ) );
		if ( !val[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin kick <client>\n\"" );
			return;
		}

		clientNum = G_KickOrBanClient( ent, val, qfalse );
		if ( clientNum >= 0 ) {
			G_LogPrintf( "Admin %s kicked %s\n", ent->client->pers.netname, level.clients[clientNum].pers.netname );
		}
		return;
	}

	if ( !Q_stricmp( arg, "ban" ) ) {
		int clientNum;

		if ( priv < PRIV_ADMIN ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Argv( 2, val, sizeof( val ) );
		if ( !val[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin ban <client>\n\"" );
			return;
		}
		clientNum = G_KickOrBanClient( ent, val, qtrue );
		if ( clientNum >= 0 ) {
			G_LogPrintf( "Admin %s banned %s\n", ent->client->pers.netname, level.clients[clientNum].pers.netname );
		}
		return;
	}

	if ( !Q_stricmp( arg, "map" ) ) {
		char factory[MAX_TOKEN_CHARS];
		const factoryDefinition_t	*factoryOverride;

		if ( priv < PRIV_ADMIN ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Argv( 2, val, sizeof( val ) ); // mapname
		if ( !val[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin map <mapname> [factory]\n\"" );
			return;
		}
		trap_Argv( 3, factory, sizeof( factory ) );
		if ( factory[0] ) {
			if ( strchr( factory, ';' ) || strchr( factory, '\n' ) ) {
				trap_SendServerCommand( ent - g_entities, "print \"Invalid characters in factory name.\n\"" );
				return;
			}

			factoryOverride = Factory_FindById( factory );
			if ( !factoryOverride ) {
				trap_SendServerCommand( ent - g_entities, "print \"Invalid factory specified.\n\"" );
				return;
			}
			if ( !G_MapSupportsGametype( val, factoryOverride->baseGametype ) ) {
				trap_SendServerCommand( ent - g_entities, "print \"Map not supported for this gametype.\n\"" );
				return;
			}

			trap_SendConsoleCommand( EXEC_APPEND, va("map %s %s\n", val, factory) );
		} else {
			trap_SendConsoleCommand( EXEC_APPEND, va("map %s\n", val) );
		}
		G_LogPrintf( "Admin %s changed map to %s\n", ent->client->pers.netname, val );
		return;
	}

	if ( !Q_stricmp( arg, "restart" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
		G_LogPrintf( "Admin %s restarted match\n", ent->client->pers.netname );
		return;
	}

	if ( !Q_stricmp( arg, "pass" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		if ( level.voteTime ) {
			ent->client->pers.voteState = VOTE_STATE_FORCE_PASS;
			ent->client->ps.eFlags |= EF_VOTED;
			G_UpdateVoteCounts();
			G_LogPrintf( "Admin %s passed vote\n", ent->client->pers.netname );
		}
		return;
	}

	if ( !Q_stricmp( arg, "cancel" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		if ( level.voteTime ) {
			G_ClearVoteState();
			trap_SendServerCommand( -1, "print \"Vote cancelled by admin.\n\"" );
			G_LogPrintf( "Admin %s cancelled vote\n", ent->client->pers.netname );
		}
		return;
	}

	if ( !Q_stricmp( arg, "shuffle" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		Cmd_ShuffleTeams_f();
		G_LogPrintf( "Admin %s shuffled teams\n", ent->client->pers.netname );
		return;
	}

	if ( !Q_stricmp( arg, "teamsize" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Argv( 2, val, sizeof( val ) );
		if ( !val[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin teamsize <size>\n\"" );
			return;
		}
		trap_Cvar_Set( "g_teamSizeMin", val );
		trap_SendServerCommand( -1, va("print \"Teamsize set to %s by admin.\n\"", val) );
		return;
	}

	if ( !Q_stricmp( arg, "addbot" ) ) {
		char botName[MAX_TOKEN_CHARS];
		char skill[MAX_TOKEN_CHARS];
		char team[MAX_TOKEN_CHARS];
		char delay[MAX_TOKEN_CHARS];

		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		// admin addbot <name> <skill> <team> <delay>

		trap_Argv( 2, botName, sizeof( botName ) );
		trap_Argv( 3, skill, sizeof( skill ) );
		trap_Argv( 4, team, sizeof( team ) );
		trap_Argv( 5, delay, sizeof( delay ) );

		if ( !botName[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin addbot <name> [skill] [team] [delay]\n\"" );
			return;
		}

		trap_SendConsoleCommand( EXEC_APPEND, va("addbot %s %s %s %s\n", botName, skill, team, delay) );
		G_LogPrintf( "Admin %s added bot %s\n", ent->client->pers.netname, botName );
		return;
	}

	if ( !Q_stricmp( arg, "kickbot" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Argv( 2, val, sizeof( val ) );
		trap_SendConsoleCommand( EXEC_APPEND, va("kick %s\n", val[0] ? val : "allbots") );
		return;
	}

	if ( !Q_stricmp( arg, "move" ) ) {
		char targetStr[MAX_TOKEN_CHARS];
		char teamStr[MAX_TOKEN_CHARS];
		int clientNum;

		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Argv( 2, targetStr, sizeof( targetStr ) );
		trap_Argv( 3, teamStr, sizeof( teamStr ) );

		if ( !targetStr[0] || !teamStr[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin move <client> <team>\n\"" );
			return;
		}

		clientNum = ClientNumberFromString( ent, targetStr );
		if ( clientNum >= 0 ) {
			SetTeam( &g_entities[clientNum], teamStr );
			G_LogPrintf( "Admin %s moved %s to %s\n", ent->client->pers.netname, level.clients[clientNum].pers.netname, teamStr );
		}
		return;
	}

	if ( !Q_stricmp( arg, "timeout" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		if ( level.timeoutActive ) {
			trap_SendServerCommand( ent - g_entities, "print \"Timeout already active.\n\"" );
			return;
		}
		G_StartTimeout( NULL, g_matchFactoryConfig.timeoutLengthSeconds );
		return;
	}

	if ( !Q_stricmp( arg, "timein" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		if ( !level.timeoutActive ) {
			trap_SendServerCommand( ent - g_entities, "print \"No timeout active.\n\"" );
			return;
		}
		G_BeginTimein( NULL );
		return;
	}

	if ( !Q_stricmp( arg, "lock" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Cvar_Set( "g_teamSpawnAsSpec", "1" );
		trap_SendServerCommand( -1, "print \"Teams locked by admin.\n\"" );
		return;
	}

	if ( !Q_stricmp( arg, "unlock" ) ) {
		if ( priv < PRIV_MOD ) {
			trap_SendServerCommand( ent - g_entities, "print \"Insufficient privileges.\n\"" );
			return;
		}
		trap_Cvar_Set( "g_teamSpawnAsSpec", "0" );
		trap_SendServerCommand( -1, "print \"Teams unlocked by admin.\n\"" );
		return;
	}

	if ( !Q_stricmp( arg, "mute" ) ) {
		char targetStr[MAX_TOKEN_CHARS];
		int clientNum;
		if ( priv < PRIV_MOD ) { return; }

		trap_Argv( 2, targetStr, sizeof( targetStr ) );
		if ( !targetStr[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin mute <client>\n\"" );
			return;
		}
		clientNum = ClientNumberFromString( ent, targetStr );
		if ( clientNum >= 0 ) {
			g_entities[clientNum].client->sess.muted = qtrue;
			trap_SendServerCommand( ent-g_entities, va("print \"%s muted.\n\"", level.clients[clientNum].pers.netname) );
			trap_SendServerCommand( clientNum, "print \"You have been muted.\n\"" );
		}
		return;
	}

	if ( !Q_stricmp( arg, "unmute" ) ) {
		char targetStr[MAX_TOKEN_CHARS];
		int clientNum;
		if ( priv < PRIV_MOD ) { return; }

		trap_Argv( 2, targetStr, sizeof( targetStr ) );
		if ( !targetStr[0] ) {
			trap_SendServerCommand( ent - g_entities, "print \"usage: admin unmute <client>\n\"" );
			return;
		}
		clientNum = ClientNumberFromString( ent, targetStr );
		if ( clientNum >= 0 ) {
			g_entities[clientNum].client->sess.muted = qfalse;
			trap_SendServerCommand( ent-g_entities, va("print \"%s unmuted.\n\"", level.clients[clientNum].pers.netname) );
			trap_SendServerCommand( clientNum, "print \"You have been unmuted.\n\"" );
		}
		return;
	}

	trap_SendServerCommand( ent - g_entities, "print \"Unknown admin command.\n\"" );
}

/*
=================
ClientCommand
=================
*/
void ClientCommand( int clientNum ) {
	gentity_t *ent;
	char	cmd[MAX_TOKEN_CHARS];

	ent = g_entities + clientNum;
	if ( !ent->client ) {
		return;		// not fully in game yet
	}

	if ( G_FloodLimited( ent, "issuing commands", qfalse ) ) {
		return;
	}

	trap_Argv( 0, cmd, sizeof( cmd ) );

	if (Q_stricmp (cmd, "say") == 0) {
		Cmd_Say_f (ent, SAY_ALL, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "say_team") == 0) {
		Cmd_Say_f (ent, SAY_TEAM, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "tell") == 0) {
		Cmd_Tell_f ( ent );
		return;
	}
	if (Q_stricmp (cmd, "complaint") == 0) {
		Cmd_Complaint_f( ent );
		return;
	}
	if (Q_stricmp (cmd, "vsay") == 0) {
		Cmd_Voice_f (ent, SAY_ALL, qfalse, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "vsay_team") == 0) {
		Cmd_Voice_f (ent, SAY_TEAM, qfalse, qfalse);
		return;
	}
	if (Q_stricmp (cmd, "vtell") == 0) {
		Cmd_VoiceTell_f ( ent, qfalse );
		return;
	}
	if (Q_stricmp (cmd, "vosay") == 0) {
		Cmd_Voice_f (ent, SAY_ALL, qfalse, qtrue);
		return;
	}
	if (Q_stricmp (cmd, "vosay_team") == 0) {
		Cmd_Voice_f (ent, SAY_TEAM, qfalse, qtrue);
		return;
	}
	if (Q_stricmp (cmd, "votell") == 0) {
		Cmd_VoiceTell_f ( ent, qtrue );
		return;
	}
	if (Q_stricmp (cmd, "vtaunt") == 0) {
		Cmd_VoiceTaunt_f ( ent );
		return;
	}
	if (Q_stricmp (cmd, "score") == 0) {
		Cmd_Score_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "ready") == 0) {
		Cmd_Ready_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "readyup") == 0) {
		Cmd_ReadyUp_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "notready") == 0 || Q_stricmp (cmd, "unready") == 0 ) {
		Cmd_NotReady_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "players") == 0) {
		Cmd_Players_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "teams") == 0) {
		Cmd_Teams_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "acc") == 0) {
		Cmd_Acc_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "pstats") == 0) {
		Cmd_PStats_f (ent);
		return;
	}
	else if (Q_stricmp (cmd, "cvar") == 0) {
		Cmd_Cvar_f (ent);
		return;
	}

	// ignore all other commands when at intermission
	if (level.intermissiontime) {
		Cmd_Say_f (ent, qfalse, qtrue);
		return;
	}

	if (Q_stricmp (cmd, "give") == 0)
		Cmd_Give_f (ent);
	else if (Q_stricmp (cmd, "god") == 0)
		Cmd_God_f (ent);
	else if (Q_stricmp (cmd, "notarget") == 0)
		Cmd_Notarget_f (ent);
	else if (Q_stricmp (cmd, "noclip") == 0)
		Cmd_Noclip_f (ent);
	else if (Q_stricmp (cmd, "thawtarget") == 0)
		Cmd_ThawTarget_f( ent );
	else if (Q_stricmp (cmd, "kill") == 0)
		Cmd_Kill_f (ent);
	else if (Q_stricmp (cmd, "forfeit") == 0)
		Cmd_Forfeit_f( ent );
	else if (Q_stricmp (cmd, "teamtask") == 0)
		Cmd_TeamTask_f (ent);
	else if (Q_stricmp (cmd, "levelshot") == 0)
		Cmd_LevelShot_f (ent);
	else if (Q_stricmp (cmd, "follow") == 0)
		Cmd_Follow_f (ent);
	else if (Q_stricmp (cmd, "follownext") == 0)
		Cmd_FollowCycle_f (ent, 1);
	else if (Q_stricmp (cmd, "followprev") == 0)
		Cmd_FollowCycle_f (ent, -1);
	else if (Q_stricmp (cmd, "team") == 0)
		Cmd_Team_f (ent);
	else if (Q_stricmp (cmd, "where") == 0)
		Cmd_Where_f (ent);
	else if (Q_stricmp (cmd, "callvote") == 0)
		Cmd_CallVote_f (ent);
	else if (Q_stricmp (cmd, "vote") == 0)
		Cmd_Vote_f (ent);
	else if (Q_stricmp (cmd, "callteamvote") == 0)
		Cmd_CallTeamVote_f (ent);
	else if (Q_stricmp (cmd, "teamvote") == 0)
		Cmd_TeamVote_f (ent);
	else if (Q_stricmp (cmd, "gc") == 0)
		Cmd_GameCommand_f( ent );
	else if ( !Q_stricmp( cmd, "pause" ) )
		Cmd_Pause_f( ent );
	else if ( !Q_stricmp( cmd, "timeout" ) )
		Cmd_Timeout_f( ent );
	else if ( !Q_stricmp( cmd, "timein" ) || !Q_stricmp( cmd, "resume" ) || !Q_stricmp( cmd, "unpause" ) )
		Cmd_Timein_f( ent );
	else if ( !Q_stricmp( cmd, "forfeit" ) )
		Cmd_Forfeit_f( ent );
	else if ( !Q_stricmp( cmd, "specresp" ) )
		G_SyncSpectatorItemStatesForClient( clientNum );
	else if ( !Q_stricmp( cmd, "racepoint" ) )
		G_RaceAdminCommand( ent );
	else if ( !Q_stricmp( cmd, "raceinit" ) || !Q_stricmp( cmd, "race_init" ) ) {
		if ( g_gametype.integer == GT_RACE ) {
			G_RaceBroadcastInitCommand( ent - g_entities );
		} else {
			trap_SendServerCommand( clientNum, "print \"" GAMEPRINT_RACEPOINT_RACE_ONLY "\"" );
			G_LogPrintf( "cmd: %s denied outside Race for client %i\n", cmd, clientNum );
		}
	}
	else if ( !Q_stricmp( cmd, "race_info" ) ) {
		if ( g_gametype.integer == GT_RACE ) {
			G_RaceSendInfoCommand( ent - g_entities );
		} else {
			trap_SendServerCommand( clientNum, "print \"" GAMEPRINT_RACEPOINT_RACE_ONLY "\"" );
			G_LogPrintf( "cmd: %s denied outside Race for client %i\n", cmd, clientNum );
		}
	}
	else if ( !Q_stricmpn( cmd, "admin_race_point_", 17 ) ) {
		if ( g_gametype.integer == GT_RACE ) {
			int index = atoi( cmd + 17 );
			if ( !G_RaceSendPointMetadataCommand( ent - g_entities, index ) ) {
				trap_SendServerCommand( clientNum, va( "print \"" GAMEPRINT_RACEPOINT_INVALID_INDEX "\"", index ) );
				G_LogPrintf( "cmd: %s invalid index %i from client %i\n", cmd, index, clientNum );
			}
		} else {
			trap_SendServerCommand( clientNum, "print \"" GAMEPRINT_RACEPOINT_RACE_ONLY "\"" );
			G_LogPrintf( "cmd: %s denied outside Race for client %i\n", cmd, clientNum );
		}
	}
	else if (Q_stricmp (cmd, "setviewpos") == 0)
		Cmd_SetViewpos_f( ent );
	else if (Q_stricmp (cmd, "stats") == 0)
		Cmd_Stats_f( ent );
	else if (Q_stricmp (cmd, "elo") == 0)
		Cmd_Elo_f( ent );
	else if (Q_stricmp (cmd, "admin") == 0)
		Cmd_Admin_f( ent );
	else if (Q_stricmp (cmd, "ruleset") == 0)
		Cmd_Ruleset_f( ent );
	else if (Q_stricmp (cmd, "invite") == 0)
		Cmd_Invite_f( ent );
	else if (Q_stricmp (cmd, "revoke") == 0)
		Cmd_Revoke_f( ent );
	else if (Q_stricmp (cmd, "whois") == 0)
		Cmd_Whois_f( ent );
	else if (Q_stricmp (cmd, "mute") == 0)
		Cmd_Mute_f( ent );
	else if (Q_stricmp (cmd, "unmute") == 0)
		Cmd_Unmute_f( ent );
	else if (Q_stricmp (cmd, "lock") == 0)
		Cmd_Lock_f( ent );
	else if (Q_stricmp (cmd, "unlock") == 0)
		Cmd_Unlock_f( ent );
	else if (Q_stricmp (cmd, "putteam") == 0)
		Cmd_PutTeam_f( ent );
	else if (Q_stricmp (cmd, "allready") == 0)
		Cmd_AllReady_f( ent );
	else if (Q_stricmp (cmd, "map") == 0)
		Cmd_Map_f( ent );
	else if (Q_stricmp (cmd, "restart") == 0)
		Cmd_Restart_f( ent );
	else if (Q_stricmp (cmd, "shuffle") == 0)
		Cmd_Shuffle_f( ent );
	else if (Q_stricmp (cmd, "teamsize") == 0)
		Cmd_Teamsize_f( ent );
	else if (Q_stricmp (cmd, "clan") == 0)
		Cmd_Clan_f( ent );
	else if (Q_stricmp (cmd, "kick") == 0)
		Cmd_Kick_f( ent );
	else if (Q_stricmp (cmd, "ban") == 0)
		Cmd_Ban_f( ent );
	else if (Q_stricmp (cmd, "clientkick") == 0)
		Cmd_ClientKick_f( ent );
	else if (Q_stricmp (cmd, "timelimit") == 0)
		Cmd_TimeLimit_f( ent );
	else if (Q_stricmp (cmd, "addpoi") == 0)
		Cmd_AddPOI_f( ent );
	else if (Q_stricmp (cmd, "delpoi") == 0)
		Cmd_DelPOI_f( ent );
	else if (Q_stricmp (cmd, "pois") == 0)
		Cmd_POIs_f( ent );
	else
		trap_SendServerCommand( clientNum, va("print \"unknown cmd %s\n\"", cmd ) );
}

/*
==================
Cmd_AddPOI_f
==================
*/
void Cmd_AddPOI_f( gentity_t *ent ) {
	char	arg[MAX_TOKEN_CHARS];
	vec3_t	origin, angles;
	int		i;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	if ( level.numPois >= MAX_POIS ) {
		trap_SendServerCommand( ent-g_entities, "print \"Max POIs reached.\n\"" );
		return;
	}

	if ( trap_Argc() > 1 ) {
		// x y z yaw pitch roll name
		if ( trap_Argc() < 5 ) {
			trap_SendServerCommand( ent-g_entities, "print \"usage: addpoi [x y z [yaw pitch roll]] [name]\n\"" );
			return;
		}
		for ( i=0 ; i<3 ; i++ ) {
			trap_Argv( i+1, arg, sizeof( arg ) );
			origin[i] = atof( arg );
		}
		if ( trap_Argc() >= 7 ) {
			for ( i=0 ; i<3 ; i++ ) {
				trap_Argv( i+4, arg, sizeof( arg ) );
				angles[i] = atof( arg );
			}
		} else {
			VectorClear( angles );
		}
		if ( trap_Argc() >= 8 ) {
			trap_Argv( 7, level.pois[level.numPois].name, sizeof( level.pois[level.numPois].name ) );
		} else {
			Com_sprintf( level.pois[level.numPois].name, sizeof( level.pois[level.numPois].name ), "POI %d", level.numPois );
		}
	} else {
		VectorCopy( ent->r.currentOrigin, origin );
		VectorCopy( ent->client->ps.viewangles, angles );
		Com_sprintf( level.pois[level.numPois].name, sizeof( level.pois[level.numPois].name ), "POI %d", level.numPois );
	}

	VectorCopy( origin, level.pois[level.numPois].origin );
	VectorCopy( angles, level.pois[level.numPois].angles );
	level.pois[level.numPois].inuse = qtrue;
	level.numPois++;

	trap_SendServerCommand( ent-g_entities, va("print \"Added POI %d at %s\n\"", level.numPois-1, vtos(origin) ) );
}

/*
==================
Cmd_DelPOI_f
==================
*/
void Cmd_DelPOI_f( gentity_t *ent ) {
	char	arg[MAX_TOKEN_CHARS];
	int		index;

	if ( !CheatsOk( ent ) ) {
		return;
	}

	if ( trap_Argc() != 2 ) {
		trap_SendServerCommand( ent-g_entities, "print \"usage: delpoi <index>\n\"" );
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	index = atoi( arg );

	if ( index < 0 || index >= level.numPois || !level.pois[index].inuse ) {
		trap_SendServerCommand( ent-g_entities, "print \"Invalid POI index.\n\"" );
		return;
	}

	// Remove by shifting
	level.numPois--;
	for ( ; index < level.numPois ; index++ ) {
		level.pois[index] = level.pois[index+1];
	}

	trap_SendServerCommand( ent-g_entities, "print \"POI deleted.\n\"" );
}

/*
==================
Cmd_POIs_f
==================
*/
void Cmd_POIs_f( gentity_t *ent ) {
	int		i;

	trap_SendServerCommand( ent-g_entities, "print \"Index Name                 Origin\n\"" );
	trap_SendServerCommand( ent-g_entities, "print \"--------------------------------------------------\n\"" );

	for ( i=0 ; i<level.numPois ; i++ ) {
		if ( !level.pois[i].inuse ) {
			continue;
		}
		trap_SendServerCommand( ent-g_entities, va("print \"  %3d %-20s %s\n\"", i, level.pois[i].name, vtos(level.pois[i].origin) ) );
	}
}
