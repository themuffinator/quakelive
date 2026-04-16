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
// cg_event.c -- handle entity events at snapshot or playerstate transitions

#include "cg_local.h"

// for the voice chats
#include "../../ui/menudef.h"
//==========================================================================

enum {
	QL_EV_OVERTIME = 0x54,
	QL_EV_GAMEOVER = 0x55,
	QL_EV_LIGHTNING_DISCHARGE = 0x5c,
	QL_EV_RACE_START = 0x5d,
	QL_EV_RACE_CHECKPOINT = 0x5e,
	QL_EV_RACE_FINISH = 0x5f,
	QL_EV_AWARD = 0x61,
	QL_EV_INFECTED = 0x62,
	QL_EV_NEW_HIGH_SCORE = 99
};

/*
=============
CG_DamagePlumsEnabled

Returns qtrue when any damage plums should be displayed.
=============
*/
qboolean CG_DamagePlumsEnabled( void ) {
	return ( cg.damagePlumWeaponBits != 0u );
}

/*
=============
CG_ShouldRenderDamagePlumForWeapon

Determines if a specific weapon should show damage plums.
=============
*/
qboolean CG_ShouldRenderDamagePlumForWeapon( weapon_t weapon ) {
	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return qfalse;
	}

	return ( ( cg.damagePlumWeaponBits & ( 1u << weapon ) ) != 0u );
}

/*
=============
CG_GetDamagePlumColorStyle

Returns the cached damage plum color style.
=============
*/
damagePlumColorStyle_t CG_GetDamagePlumColorStyle( void ) {
	return cg.damagePlumColorStyle;
}

/*
=============
CG_GetDamagePlumColor

Approximates the retail color-style selector for source-side damage-plum
reconstruction.
=============
*/
static void CG_GetDamagePlumColor( int damage, weapon_t weapon, vec4_t color ) {
	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = 1.0f;

	switch ( CG_GetDamagePlumColorStyle() ) {
	case DAMAGE_PLUM_COLOR_STYLE_DAMAGE:
		if ( damage >= 100 ) {
			color[0] = 1.0f;
			color[1] = 0.2f;
			color[2] = 0.2f;
		}
		else if ( damage >= 75 ) {
			color[0] = 1.0f;
			color[1] = 0.45f;
			color[2] = 0.15f;
		}
		else if ( damage >= 50 ) {
			color[0] = 1.0f;
			color[1] = 0.8f;
			color[2] = 0.15f;
		}
		else if ( damage >= 25 ) {
			color[0] = 0.6f;
			color[1] = 1.0f;
			color[2] = 0.2f;
		}
		else {
			color[0] = 0.25f;
			color[1] = 1.0f;
			color[2] = 0.25f;
		}
		break;

	case DAMAGE_PLUM_COLOR_STYLE_WEAPON:
		switch ( weapon ) {
		case WP_GAUNTLET:
			color[0] = 1.0f;
			color[1] = 0.3f;
			color[2] = 0.3f;
			break;
		case WP_MACHINEGUN:
			color[0] = 1.0f;
			color[1] = 0.95f;
			color[2] = 0.35f;
			break;
		case WP_SHOTGUN:
			color[0] = 1.0f;
			color[1] = 1.0f;
			color[2] = 1.0f;
			break;
		case WP_GRENADE_LAUNCHER:
			color[0] = 0.55f;
			color[1] = 0.9f;
			color[2] = 0.2f;
			break;
		case WP_ROCKET_LAUNCHER:
			color[0] = 1.0f;
			color[1] = 0.45f;
			color[2] = 0.1f;
			break;
		case WP_LIGHTNING:
			color[0] = 0.35f;
			color[1] = 0.7f;
			color[2] = 1.0f;
			break;
		case WP_RAILGUN:
			color[0] = 0.2f;
			color[1] = 1.0f;
			color[2] = 1.0f;
			break;
		case WP_PLASMAGUN:
			color[0] = 1.0f;
			color[1] = 0.2f;
			color[2] = 1.0f;
			break;
		case WP_BFG:
			color[0] = 0.45f;
			color[1] = 1.0f;
			color[2] = 0.35f;
			break;
		case WP_GRAPPLING_HOOK:
			color[0] = 0.25f;
			color[1] = 0.9f;
			color[2] = 0.8f;
			break;
		case WP_NAILGUN:
			color[0] = 0.6f;
			color[1] = 0.85f;
			color[2] = 0.25f;
			break;
		case WP_PROX_LAUNCHER:
			color[0] = 1.0f;
			color[1] = 0.8f;
			color[2] = 0.2f;
			break;
		case WP_CHAINGUN:
			color[0] = 1.0f;
			color[1] = 0.7f;
			color[2] = 0.15f;
			break;
		default:
			break;
		}
		break;

	default:
		break;
	}
}

/*
=============
CG_DamagePlum

Stages the mapped retail damage-plum producer through the queued world-marker
path instead of the older local-entity score plum.
=============
*/
static void CG_DamagePlum( vec3_t org, int damage, weapon_t weapon ) {
	cgQueuedWorldMarker_t	*marker;
	vec4_t			color;

	if ( damage <= 0 || !CG_DamagePlumsEnabled() ) {
		return;
	}
	if ( !CG_ShouldRenderDamagePlumForWeapon( weapon ) ) {
		return;
	}

	CG_GetDamagePlumColor( damage, weapon, color );

	marker = CG_AllocQueuedWorldMarker();
	if ( !marker ) {
		return;
	}

	VectorCopy( org, marker->origin );
	marker->origin[0] += crandom() * 10.0f;
	marker->origin[1] += crandom() * 10.0f;
	marker->origin[2] += crandom() * 10.0f;
	marker->duration = 2000;
	marker->fadeDelay = 1000;
	marker->rise = 100.0f;
	marker->textScale = 0.18f;
	Vector4Copy( color, marker->color );
	Com_sprintf( marker->text, sizeof( marker->text ), "%d", damage );
}

/*
=============
CG_POIEvent

Stages the retail EV_POI seam through the shared queued world-marker path.
=============
*/
static void CG_POIEvent( centity_t *cent, const entityState_t *es ) {
	cgQueuedWorldMarker_t	*marker;
	qhandle_t		shader;
	vec4_t			color;
	float			size;
	float			rise;
	float			zOffset;

	if ( !cent || !es ) {
		return;
	}

	shader = 0;
	size = ( es->eventParm > 0 ) ? (float)es->eventParm : 64.0f;
	rise = size * 0.25f;
	zOffset = 48.0f;
	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = 1.0f;

	if ( cg_pmoveSettings.quadHogEnabled ) {
		shader = cgs.media.poiQuadHogShader;
		color[0] = 1.0f;
		color[1] = 0.75f;
		color[2] = 0.0f;
	} else if ( cgs.customSettingsMask & CUSTOM_SETTING_INFECTED ) {
		shader = cgs.media.poiInfectedShader;
	} else {
		shader = cgs.media.poiNeutralFlagCarrierShader;
		size *= 0.75f;
		zOffset = 64.0f;
	}
	if ( !shader ) {
		shader = cgs.media.poiUnavailableShader;
	}
	if ( !shader ) {
		return;
	}

	marker = CG_AllocQueuedWorldMarker();
	if ( !marker ) {
		return;
	}

	marker->kind = CG_QUEUED_MARKER_KIND_EVENT_POI;
	VectorCopy( cent->lerpOrigin, marker->origin );
	marker->origin[2] += zOffset;
	marker->duration = 2000;
	marker->fadeDelay = 1000;
	marker->rise = rise;
	marker->size = size;
	Vector4Copy( color, marker->color );
	marker->shader = shader;
}

/*
===============================
CG_ShouldSuppressPredictedRailEvent

Retail skips the local EV_RAILTRAIL entirely when the same shot was already
spawned from prediction.
===============================
*/
static qboolean CG_ShouldSuppressPredictedRailEvent( const entityState_t *es ) {
	if ( !es ) {
		return qfalse;
	}
	if ( !cg.predictLocalRailshots ) {
		return qfalse;
	}
	if ( cg.demoPlayback || cg_nopredict.integer || cg_synchronousClients.integer ) {
		return qfalse;
	}
	if ( !cg.snap || ( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		return qfalse;
	}
	if ( cg.snap->ps.pm_type == PM_SPECTATOR ) {
		return qfalse;
	}
	if ( !cg.predictedLocalRailValid ) {
		return qfalse;
	}
	if ( cg.time - cg.predictedLocalRailTime > 200 ) {
		return qfalse;
	}
	if ( es->clientNum != cg.predictedPlayerState.clientNum ) {
		return qfalse;
	}
	if ( cg.predictedLocalRailHit != ( es->eventParm != 255 ) ) {
		return qfalse;
	}
	if ( DistanceSquared( cg.predictedLocalRailEnd, es->pos.trBase ) > Square( 8.0f ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
===================
CG_PlaceString

Also called by scoreboard drawing
===================
*/
const char	*CG_PlaceString( int rank ) {
	static char	str[64];
	char	*s, *t;

	if ( rank & RANK_TIED_FLAG ) {
		rank &= ~RANK_TIED_FLAG;
		t = "Tied for ";
	} else {
		t = "";
	}

	if ( rank == 1 ) {
		s = S_COLOR_BLUE "1st" S_COLOR_WHITE;		// draw in blue
	} else if ( rank == 2 ) {
		s = S_COLOR_RED "2nd" S_COLOR_WHITE;		// draw in red
	} else if ( rank == 3 ) {
		s = S_COLOR_YELLOW "3rd" S_COLOR_WHITE;		// draw in yellow
	} else if ( rank == 11 ) {
		s = "11th";
	} else if ( rank == 12 ) {
		s = "12th";
	} else if ( rank == 13 ) {
		s = "13th";
	} else if ( rank % 10 == 1 ) {
		s = va("%ist", rank);
	} else if ( rank % 10 == 2 ) {
		s = va("%ind", rank);
	} else if ( rank % 10 == 3 ) {
		s = va("%ird", rank);
	} else {
		s = va("%ith", rank);
	}

	Com_sprintf( str, sizeof( str ), "%s%s", t, s );
	return str;
}


/*
=============
CG_MatchClockMilliseconds

Returns the current match clock in milliseconds, clamping for timeouts,
overtime, and sudden-death end caps.
=============
*/
static int CG_MatchClockMilliseconds( void ) {
	int		anchor;
	int		now;
	int		overtimeEnd;
	int		suddenMax;
	int		timeoutStart;

	anchor = cgs.levelStartTime;
	if ( anchor <= 0 ) {
		return 0;
	}

	timeoutStart = CG_GetMatchTimeoutStartTime();
	if ( cgs.matchTimeoutActive ) {
		if ( cgs.matchTimeoutExpireTime > 0 ) {
			now = cgs.matchTimeoutExpireTime;
		} else if ( timeoutStart > 0 ) {
			now = timeoutStart;
		} else {
			now = cg.time;
		}
	} else {
		now = cg.time;
	}

	overtimeEnd = cgs.matchOvertimeEndTime;
	if ( cgs.matchOvertimeActive && !overtimeEnd && cgs.matchOvertimeStartTime > 0 && cgs.matchOvertimeLengthSeconds > 0 ) {
		overtimeEnd = cgs.matchOvertimeStartTime + ( cgs.matchOvertimeLengthSeconds * 1000 );
	}
	if ( overtimeEnd > 0 && now > overtimeEnd ) {
		now = overtimeEnd;
	}

	suddenMax = 0;
	if ( cgs.matchSuddenDeathStartSeconds > 0 && cgs.matchSuddenDeathMaxSeconds > 0 ) {
		suddenMax = cgs.levelStartTime + ( ( cgs.matchSuddenDeathStartSeconds + cgs.matchSuddenDeathMaxSeconds ) * 1000 );
	}
	if ( suddenMax > 0 && now > suddenMax ) {
		now = suddenMax;
	}

	if ( now < anchor ) {
		return 0;
	}

	return now - anchor;
}

/*
=============
CG_StartScoreboardTimer

Begins tracking the scoreboard stopwatch so draw calls can format timer fields.
=============
*/
void CG_StartScoreboardTimer( int startTime ) {
	(void)startTime;

	cg.scoreboardTimerRunning = qtrue;
	cg.scoreboardTimerStartTime = CG_MatchClockMilliseconds();
	cg.scoreboardTimerStopTime = cg.scoreboardTimerStartTime;
}

/*
=============
CG_StopScoreboardTimer

Stops the scoreboard stopwatch and records the most recent checkpoint.
=============
*/
void CG_StopScoreboardTimer( int stopTime ) {
	int		anchor;

	(void)stopTime;

	if ( !cg.scoreboardTimerRunning ) {
		return;
	}

	anchor = CG_MatchClockMilliseconds();
	cg.scoreboardTimerStopTime = anchor;
	cg.scoreboardTimerRunning = qfalse;
}

/*
=============
CG_GetScoreboardTimerSeconds

Returns the stopwatch value in seconds for scoreboard formatting hooks.
=============
*/
int CG_GetScoreboardTimerSeconds( void ) {
	int		elapsed;

	elapsed = CG_MatchClockMilliseconds();
	if ( elapsed < 0 ) {
		return 0;
	}

	return ( elapsed + 500 ) / 1000;
}

/*
=============
CG_IsRetailLocalEventClient

Determines whether a retail event targets the live local client or the
currently followed player.
=============
*/
static qboolean CG_IsRetailLocalEventClient( int clientNum ) {
	if ( !cg.snap ) {
		return qfalse;
	}
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return qfalse;
	}
	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return qfalse;
	}
	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return ( qboolean )( clientNum == cg.spectatorFollowClient );
	}

	return ( qboolean )( clientNum == cg.clientNum );
}

/*
=============
CG_IsLocalPlayerWinner

Retail endgame predicate for local winner handling.
=============
*/
static qboolean CG_IsLocalPlayerWinner( void ) {
	int		rank;
	team_t	localTeam;

	if ( !cg.snap ) {
		return qfalse;
	}

	localTeam = cg.snap->ps.persistant[PERS_TEAM];
	if ( localTeam == TEAM_SPECTATOR ) {
		return qfalse;
	}

	if ( !CG_IsTeamWinnerGametype( cgs.gametype ) ) {
		rank = cg.snap->ps.persistant[PERS_RANK];
		if ( rank & RANK_TIED_FLAG ) {
			return qfalse;
		}
		return ( qboolean )( rank == 0 );
	}

	if ( cg.teamScores[0] == cg.teamScores[1] ) {
		return qfalse;
	}
	if ( localTeam == TEAM_RED ) {
		return ( qboolean )( cg.teamScores[0] > cg.teamScores[1] );
	}
	if ( localTeam == TEAM_BLUE ) {
		return ( qboolean )( cg.teamScores[1] > cg.teamScores[0] );
	}

	return qfalse;
}

/*
=============
CG_GetOvertimeCount

Returns the current overtime round count, falling back to the elapsed retail
match-state seam when the cached count has not landed yet.
=============
*/
int CG_GetOvertimeCount( void ) {
	int		anchor;
	int		regulationEnd;
	int		elapsed;
	int		overtimeWindow;

	if ( cgs.matchOvertimeCount > 0 ) {
		return cgs.matchOvertimeCount;
	}
	if ( cgs.timelimit <= 0 || cgs.matchOvertimeLengthSeconds <= 0 || cgs.levelStartTime <= 0 ) {
		return 0;
	}

	anchor = cgs.matchOvertimeStartTime;
	if ( anchor <= 0 ) {
		anchor = cgs.matchOvertimeEndTime;
	}
	if ( anchor <= 0 ) {
		anchor = cg.time;
	}

	regulationEnd = cgs.levelStartTime + ( cgs.timelimit * 60000 );
	elapsed = anchor - regulationEnd;
	if ( elapsed <= 0 ) {
		return 0;
	}

	overtimeWindow = cgs.matchOvertimeLengthSeconds * 1000;
	if ( overtimeWindow <= 0 ) {
		return 0;
	}

	return elapsed / overtimeWindow;
}

/*
=============
CG_GetRetailEventClientNum

Returns the recovered retail recipient slot used by Quake Live temp entities.
=============
*/
static int CG_GetRetailEventClientNum( const entityState_t *es ) {
	if ( !es ) {
		return -1;
	}
	if ( es->solid >= 0 && es->solid < MAX_CLIENTS ) {
		return es->solid;
	}
	if ( es->number >= 0 && es->number < MAX_CLIENTS ) {
		return es->number;
	}

	return -1;
}

/*
=============
CG_GetRetailEventIntPayload

Returns the recovered retail integer payload stored in the temp-entity origin
slot.
=============
*/
static int CG_GetRetailEventIntPayload( const entityState_t *es ) {
	int	value;

	if ( !es ) {
		return 0;
	}

	memcpy( &value, &es->origin[0], sizeof( value ) );
	return value;
}

/*
=============
CG_GetRaceEventCheckpointCount

Returns the recovered retail checkpoint-count payload for Race temp entities.
=============
*/
static int CG_GetRaceEventCheckpointCount( const entityState_t *es ) {
	if ( !es ) {
		return 0;
	}
	if ( es->groundEntityNum < 0 ) {
		return 0;
	}

	return es->groundEntityNum;
}

/*
=============
CG_GetRaceEventCurrentCheckpointEntityNum

Returns the recovered retail current-target entity number for Race temp
entities.
=============
*/
static int CG_GetRaceEventCurrentCheckpointEntityNum( const entityState_t *es ) {
	if ( !es ) {
		return -1;
	}

	return es->constantLight;
}

/*
=============
CG_GetRaceEventNextCheckpointEntityNum

Returns the recovered retail next-target entity number for Race temp entities.
=============
*/
static int CG_GetRaceEventNextCheckpointEntityNum( const entityState_t *es ) {
	if ( !es ) {
		return -1;
	}

	return es->legsAnim;
}

/*
=============
CG_GetGlobalTeamSound

Returns the recovered retail global-team-sound code.
=============
*/
static int CG_GetGlobalTeamSound( const entityState_t *es ) {
	if ( !es ) {
		return -1;
	}
	if ( es->weapon < GTS_RED_CAPTURE || es->weapon > GTS_SURVIVOR_WARNING ) {
		return -1;
	}

	return es->weapon;
}

/*
=============
CG_GetGlobalTeamSoundTrackedClientNum

Returns the recovered retail global-team-sound tracked-client payload.
=============
*/
static int CG_GetGlobalTeamSoundTrackedClientNum( const entityState_t *es ) {
	if ( !es ) {
		return -1;
	}
	if ( es->groundEntityNum >= 0 && es->groundEntityNum < MAX_CLIENTS ) {
		return es->groundEntityNum;
	}

	return -1;
}

/*
=============
CG_GetGlobalTeamSoundTeam

Returns the recovered retail global-team-sound team payload.
=============
*/
static team_t CG_GetGlobalTeamSoundTeam( const entityState_t *es ) {
	if ( !es ) {
		return TEAM_FREE;
	}
	if ( es->frame >= TEAM_FREE && es->frame < TEAM_NUM_TEAMS ) {
		return (team_t)es->frame;
	}

	return TEAM_FREE;
}

/*
=============
CG_GetGlobalTeamSoundIndex

Returns the staged retail global-team-sound point/index payload.
=============
*/
static int CG_GetGlobalTeamSoundIndex( const entityState_t *es ) {
	if ( !es ) {
		return 0;
	}

	return es->legsAnim;
}

/*
=============
CG_PlayDominationPointAnnouncement

Routes the recovered retail Domination point announcer family through the
current source point payload bridge.
=============
*/
static void CG_PlayDominationPointAnnouncement( const entityState_t *es ) {
	team_t		announcedTeam;
	team_t		localTeam;
	int			pointIndex;
	sfxHandle_t	sound;

	if ( !es ) {
		return;
	}

	announcedTeam = CG_GetGlobalTeamSoundTeam( es );
	if ( announcedTeam == TEAM_FREE ) {
		CG_AddBufferedSound( cgs.media.returnOpponentSound );
		return;
	}

	localTeam = cgs.clientinfo[cg.clientNum].team;
	if ( localTeam != TEAM_RED && localTeam != TEAM_BLUE ) {
		return;
	}

	pointIndex = CG_GetGlobalTeamSoundIndex( es ) - 1;
	sound = 0;
	if ( pointIndex >= 0 && pointIndex < QL_DOMINATION_ANNOUNCER_POINTS ) {
		sound = ( localTeam == announcedTeam )
			? cgs.media.dominationCapturedSounds[pointIndex]
			: cgs.media.dominationLostSounds[pointIndex];
	}
	if ( !sound ) {
		sound = ( localTeam == announcedTeam )
			? cgs.media.captureYourTeamSound
			: cgs.media.captureOpponentSound;
	}

	CG_AddBufferedSound( sound );
}

/*
=============
CG_GetRetailDamagePlumDamage

Returns the staged retail damage-plum damage payload.
=============
*/
static int CG_GetRetailDamagePlumDamage( const entityState_t *es ) {
	int	damage;

	if ( !es ) {
		return 0;
	}

	memcpy( &damage, &es->origin[0], sizeof( damage ) );
	return damage;
}

/* Legacy transport note preserved for parity documentation: return es->eventParm; */

/*
=============
CG_GetRetailDamagePlumWeapon

Returns the staged retail damage-plum weapon payload.
=============
*/
static weapon_t CG_GetRetailDamagePlumWeapon( const entityState_t *es ) {
	weapon_t	weapon;

	if ( !es ) {
		return WP_NONE;
	}

	weapon = (weapon_t)es->retailEventData;
	if ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
		return weapon;
	}

	return WP_NONE;
}

/*
=============
CG_GetRetailAwardType

Returns the staged retail award identifier for EV_AWARD.
=============
*/
static int CG_GetRetailAwardType( const entityState_t *es ) {
	if ( !es ) {
		return -1;
	}
	if ( es->retailEventData >= 0 && es->retailEventData <= 9 ) {
		return es->retailEventData;
	}

	return -1;
}

/*
=============
CG_GetRetailAwardCount

Returns the staged retail award count for EV_AWARD.
=============
*/
static int CG_GetRetailAwardCount( const entityState_t *es ) {
	if ( !es || es->frame <= 0 ) {
		return 1;
	}

	return es->frame;
}

/*
=============
CG_HandleRetailAwardEvent

Routes the recovered retail EV_AWARD taxonomy through the existing reward stack.
=============
*/
static void CG_HandleRetailAwardEvent( const entityState_t *es ) {
	int			clientNum;
	int			rewardCount;
	int			variant;
	sfxHandle_t	sfx;
	qhandle_t	shader;

	if ( !es ) {
		return;
	}

	clientNum = CG_GetRetailEventClientNum( es );
	if ( !CG_IsRetailLocalEventClient( clientNum ) ) {
		return;
	}

	rewardCount = CG_GetRetailAwardCount( es );
	sfx = 0;
	shader = 0;
	variant = rand() % 3;

	switch ( CG_GetRetailAwardType( es ) ) {
	case 0:
		sfx = ( variant == 0 ) ? cgs.media.comboKillSound :
			( ( variant == 1 ) ? cgs.media.comboKillSound2 : cgs.media.comboKillSound3 );
		shader = cgs.media.medalComboKill;
		break;
	case 1:
		sfx = ( variant == 0 ) ? cgs.media.rampageSound :
			( ( variant == 1 ) ? cgs.media.rampageSound2 : cgs.media.rampageSound3 );
		shader = cgs.media.medalRampage;
		break;
	case 2:
		sfx = ( variant == 0 ) ? cgs.media.midairSound :
			( ( variant == 1 ) ? cgs.media.midairSound2 : cgs.media.midairSound3 );
		shader = cgs.media.medalMidair;
		break;
	case 3:
		sfx = ( variant == 0 ) ? cgs.media.revengeSound :
			( ( variant == 1 ) ? cgs.media.revengeSound2 : cgs.media.revengeSound3 );
		shader = cgs.media.medalRevenge;
		break;
	case 4:
		sfx = cgs.media.perforatedSound;
		shader = cgs.media.medalPerforated;
		break;
	case 5:
		sfx = cgs.media.headshotSound;
		shader = cgs.media.medalHeadshot;
		break;
	case 6:
		sfx = cgs.media.accuracySound;
		shader = cgs.media.medalAccuracy;
		break;
	case 7:
		sfx = cgs.media.quadGodSound;
		shader = cgs.media.medalQuadGod;
		break;
	case 8:
		sfx = cgs.media.firstFragSound;
		shader = cgs.media.medalFirstFrag;
		rewardCount = 1;
		break;
	case 9:
		sfx = cgs.media.perfectSound;
		shader = cgs.media.medalPerfect;
		break;
	default:
		return;
	}

	if ( !sfx && !shader ) {
		return;
	}

	pushReward( sfx, shader, rewardCount );
}

/*
=============
CG_TryFollowKiller

Queues the retail delayed follow-killer command when the spectator was viewing
the victim.
=============
*/
static void CG_TryFollowKiller( int target, int attacker ) {
	if ( cg_followKiller.integer <= 0 ) {
		return;
	}
	if ( cg.demoPlayback ) {
		return;
	}
	if ( attacker < 0 || attacker >= cgs.maxclients ) {
		return;
	}
	if ( attacker == target ) {
		return;
	}
	if ( !CG_IsSpectatorCamera() ) {
		return;
	}
	if ( !cg.snap || !( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		return;
	}
	if ( cg.snap->ps.clientNum != target ) {
		return;
	}

	cg.pendingFollowKillerClient = attacker;
	cg.pendingFollowKillerTime = cg.time + 400;
}

/*
=============
CG_UseItemCenterPrintScale

Maps the retail use-item cvar modes onto the cached centerprint scale.
=============
*/
static float CG_UseItemCenterPrintScale( int mode ) {
	if ( mode == 2 ) {
		return 0.25f;
	}

	return 0.5f;
}

/*
=============
CG_TrackFlagCarrierByPowerup

Notifies the spectator tracker when the requested flag powerup is held.
=============
*/
static void CG_TrackFlagCarrierByPowerup( powerup_t powerup ) {
	int clientNum;

	if ( powerup <= PW_NONE || powerup >= PW_NUM_POWERUPS ) {
		return;
	}

	for ( clientNum = 0; clientNum < cgs.maxclients; clientNum++ ) {
		const clientInfo_t *ci = &cgs.clientinfo[clientNum];

		if ( !ci->infoValid ) {
			continue;
		}
		if ( ( ci->powerups & ( 1 << powerup ) ) == 0 ) {
			continue;
		}

		CG_SpectatorTrackEvent( clientNum, CG_SPECTATOR_TRACK_FLAG );
		break;
	}
}

/*
=============
CG_TrackFlagCarrierForEvent

Evaluates global team sound events to follow the current flag carrier.
=============
*/
static void CG_TrackFlagCarrierForEvent( const entityState_t *es ) {
	int			clientNum;
	powerup_t powerup = PW_NUM_POWERUPS;

	if ( !es ) {
		return;
	}

	clientNum = CG_GetGlobalTeamSoundTrackedClientNum( es );
	if ( clientNum >= 0 && clientNum < cgs.maxclients ) {
		CG_SpectatorTrackEvent( clientNum, CG_SPECTATOR_TRACK_FLAG );
		return;
	}

	switch ( CG_GetGlobalTeamSound( es ) ) {
		case GTS_RED_TAKEN:
			powerup = ( cgs.gametype == GT_1FCTF ) ? PW_NEUTRALFLAG : PW_BLUEFLAG;
			break;
		case GTS_BLUE_TAKEN:
			powerup = ( cgs.gametype == GT_1FCTF ) ? PW_NEUTRALFLAG : PW_REDFLAG;
			break;
		default:
			return;
	}

	CG_TrackFlagCarrierByPowerup( powerup );
}

/*
=============
CG_ObituaryFeedLimit

Returns the active obituary row cap, clamped to the retail feed bounds.
=============
*/
static int CG_ObituaryFeedLimit( void ) {
	int		limit;

	limit = cg_obituaryRowSize.integer;
	if ( limit < 1 ) {
		return 1;
	}
	if ( limit > MAX_OBITUARIES ) {
		return MAX_OBITUARIES;
	}

	return limit;
}

/*
=============
CG_ObituaryColorIndexForClient

Maps a client slot to the compact obituary color palette used by retail.
=============
*/
static int CG_ObituaryColorIndexForClient( int clientNum ) {
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return 3;
	}

	switch ( cgs.clientinfo[clientNum].team ) {
	case TEAM_RED:
		return 1;
	case TEAM_BLUE:
		return 2;
	case TEAM_SPECTATOR:
		return 3;
	default:
		return 0;
	}
}

/*
=============
CG_SanitizeObituaryText

Retail strips color escapes and low ASCII from obituary names in team games.
=============
*/
static void CG_SanitizeObituaryText( char *text ) {
	const char	*src;
	char		*dst;

	if ( !text || cgs.gametype < GT_TEAM ) {
		return;
	}

	src = text;
	dst = text;
	while ( *src ) {
		if ( Q_IsColorString( src ) ) {
			src += 2;
			continue;
		}
		if ( (unsigned char)*src >= 0x20 ) {
			*dst++ = *src;
		}
		src++;
	}
	*dst = '\0';
}

/*
=============
CG_SetObituaryName

Copies a player configstring name into the cached obituary payload.
=============
*/
static void CG_SetObituaryName( char *buffer, int bufferSize, const char *playerInfo ) {
	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !playerInfo || !playerInfo[0] ) {
		return;
	}

	Q_strncpyz( buffer, Info_ValueForKey( playerInfo, "n" ), bufferSize );
	Q_strcat( buffer, bufferSize, S_COLOR_WHITE );
	CG_SanitizeObituaryText( buffer );
}

/*
=============
CG_ClearObituaryEntry

Resets one cached obituary slot.
=============
*/
static void CG_ClearObituaryEntry( cgObituary_t *entry ) {
	memset( entry, 0, sizeof( *entry ) );
}

/*
=============
CG_ShiftObituaryFeedLeft

Compacts the cached obituary feed after expiry or row-cap trimming.
=============
*/
static void CG_ShiftObituaryFeedLeft( int firstIndex ) {
	int		i;

	if ( firstIndex < 0 || firstIndex >= MAX_OBITUARIES ) {
		return;
	}

	for ( i = firstIndex; i < MAX_OBITUARIES - 1; i++ ) {
		cg.obituaries[i] = cg.obituaries[i + 1];
	}

	CG_ClearObituaryEntry( &cg.obituaries[MAX_OBITUARIES - 1] );
}

/*
=============
CG_CompactObituaryFeed

Prunes expired obituary rows and keeps the live feed densely packed.
=============
*/
static int CG_CompactObituaryFeed( void ) {
	int		readIndex;
	int		writeIndex;
	int		activeCount;

	writeIndex = 0;
	for ( readIndex = 0; readIndex < MAX_OBITUARIES; readIndex++ ) {
		cgObituary_t	*entry;

		entry = &cg.obituaries[readIndex];
		if ( !entry->active ) {
			continue;
		}
		if ( cg.time - entry->time >= OBITUARY_TIME ) {
			continue;
		}

		if ( writeIndex != readIndex ) {
			cg.obituaries[writeIndex] = *entry;
		}
		writeIndex++;
	}

	activeCount = writeIndex;
	while ( writeIndex < MAX_OBITUARIES ) {
		CG_ClearObituaryEntry( &cg.obituaries[writeIndex] );
		writeIndex++;
	}

	return activeCount;
}

/*
=============
CG_PruneObituaryFeed

Applies expiry and visible-row capping to the cached obituary feed.
=============
*/
void CG_PruneObituaryFeed( void ) {
	int		activeCount;
	int		limit;

	activeCount = CG_CompactObituaryFeed();
	limit = CG_ObituaryFeedLimit();

	while ( activeCount > limit ) {
		CG_ShiftObituaryFeedLeft( 0 );
		activeCount--;
	}
}

/*
=============
CG_RecordObituaryFeedEntry

Stores the retail-style cached obituary row consumed by the draw path.
=============
*/
static void CG_RecordObituaryFeedEntry( const char *targetName, int targetColorIndex,
		const char *attackerName, int attackerColorIndex, qboolean hasAttacker,
		qhandle_t icon, int attacker, int target, int mod ) {
	cgObituary_t	*entry;
	int			activeCount;
	int			limit;

	activeCount = CG_CompactObituaryFeed();
	limit = CG_ObituaryFeedLimit();
	while ( activeCount >= limit ) {
		CG_ShiftObituaryFeedLeft( 0 );
		activeCount--;
	}

	entry = &cg.obituaries[activeCount];
	CG_ClearObituaryEntry( entry );
	entry->active = qtrue;
	entry->time = cg.time;
	entry->targetColorIndex = targetColorIndex;
	entry->attackerColorIndex = attackerColorIndex;
	entry->hasAttacker = ( qboolean )( hasAttacker && attackerName && attackerName[0] );
	entry->icon = icon;
	entry->attacker = attacker;
	entry->target = target;
	entry->mod = mod;

	Q_strncpyz( entry->targetName, targetName ? targetName : "", sizeof( entry->targetName ) );
	Q_strncpyz( entry->attackerName, attackerName ? attackerName : "", sizeof( entry->attackerName ) );
	CG_SanitizeObituaryText( entry->targetName );
	CG_SanitizeObituaryText( entry->attackerName );
}

/*
=============
CG_Obituary
=============
*/
static void CG_Obituary( entityState_t *ent ) {
	int			mod;
	int			target, attacker;
	int			targetColorIndex;
	int			attackerColorIndex;
	char		*message;
	char		*message2;
	const char	*targetInfo;
	const char	*attackerInfo;
	char		targetName[CG_OBITUARY_NAME_SIZE];
	char		attackerName[CG_OBITUARY_NAME_SIZE];
	gender_t	gender;
	qhandle_t	icon;
	clientInfo_t	*ci;

	target = ent->otherEntityNum;
	attacker = ent->otherEntityNum2;
	mod = ent->eventParm;

	if ( target < 0 || target >= MAX_CLIENTS ) {
		CG_Error( "CG_Obituary: target out of range" );
	}
	if ( cg.snap && target == cg.snap->ps.clientNum ) {
		cg.killerName[0] = '\0';
	}
	ci = &cgs.clientinfo[target];

	if ( attacker < 0 || attacker >= MAX_CLIENTS ) {
		attacker = ENTITYNUM_WORLD;
		attackerInfo = NULL;
	} else {
		attackerInfo = CG_ConfigString( CS_PLAYERS + attacker );
	}

	targetInfo = CG_ConfigString( CS_PLAYERS + target );
	if ( !targetInfo ) {
		return;
	}
	CG_SetObituaryName( targetName, sizeof( targetName ), targetInfo );
	targetColorIndex = CG_ObituaryColorIndexForClient( target );
	attackerColorIndex = CG_ObituaryColorIndexForClient( attacker );
	icon = CG_GetObituaryIcon( mod );

	message2 = "";

	// check for single client messages

	switch( mod ) {
	case MOD_SUICIDE:
		message = "suicides";
		break;
	case MOD_FALLING:
		message = "cratered";
		break;
	case MOD_CRUSH:
		message = "was squished";
		break;
	case MOD_WATER:
		message = "sank like a rock";
		break;
	case MOD_SLIME:
		message = "melted";
		break;
	case MOD_LAVA:
		message = "does a back flip into the lava";
		break;
	case MOD_TARGET_LASER:
		message = "saw the light";
		break;
	case MOD_TRIGGER_HURT:
		message = "was in the wrong place";
		break;
	default:
		message = NULL;
		break;
	}

	if ( attacker == target ) {
		gender = ci->gender;
		switch (mod) {
		case MOD_KAMIKAZE:
			message = "goes out with a bang";
			break;
		case MOD_GRENADE_SPLASH:
			if ( gender == GENDER_FEMALE )
				message = "tripped on her own grenade";
			else if ( gender == GENDER_NEUTER )
				message = "tripped on its own grenade";
			else
				message = "tripped on his own grenade";
			break;
		case MOD_ROCKET_SPLASH:
			if ( gender == GENDER_FEMALE )
				message = "blew herself up";
			else if ( gender == GENDER_NEUTER )
				message = "blew itself up";
			else
				message = "blew himself up";
			break;
		case MOD_PLASMA_SPLASH:
			if ( gender == GENDER_FEMALE )
				message = "melted herself";
			else if ( gender == GENDER_NEUTER )
				message = "melted itself";
			else
				message = "melted himself";
			break;
		case MOD_BFG_SPLASH:
			message = "should have used a smaller gun";
			break;
		case MOD_PROXIMITY_MINE:
			if( gender == GENDER_FEMALE ) {
				message = "found her prox mine";
			} else if ( gender == GENDER_NEUTER ) {
				message = "found it's prox mine";
			} else {
				message = "found his prox mine";
			}
			break;
		default:
			if ( gender == GENDER_FEMALE )
				message = "killed herself";
			else if ( gender == GENDER_NEUTER )
				message = "killed itself";
			else
				message = "killed himself";
			break;
		}
	}

	CG_TryFollowKiller( target, attacker );

	if (message) {
		CG_RecordObituaryFeedEntry( targetName, targetColorIndex, "", attackerColorIndex,
			qfalse, icon, attacker, target, mod );
		CG_Printf( "%s %s.\n", targetName, message);
		return;
	}


	// check for kill messages from the current clientNum
	if ( attacker == cg.snap->ps.clientNum ) {
		char	*s;

		if ( cgs.gametype < GT_TEAM ) {
			s = va("You fragged %s\n%s place with %i", targetName, 
				CG_PlaceString( cg.snap->ps.persistant[PERS_RANK] + 1 ),
				cg.snap->ps.persistant[PERS_SCORE] );
		} else {
			s = va("You fragged %s", targetName );
		}
		if (!(cg_singlePlayerActive.integer && cg_cameraOrbit.integer)) {
			CG_CenterPrint( s, SCREEN_HEIGHT * 0.30f, 0.3f );
		} 

		// print the text message as well
	}

	// check for double client messages
	if ( !attackerInfo ) {
		attacker = ENTITYNUM_WORLD;
		attackerName[0] = '\0';
	} else {
		CG_SetObituaryName( attackerName, sizeof( attackerName ), attackerInfo );
		// check for kill messages about the current clientNum
		if ( target == cg.snap->ps.clientNum ) {
			Q_strncpyz( cg.killerName, attackerName, sizeof( cg.killerName ) );
		}
	}

	if ( attacker != ENTITYNUM_WORLD ) {
		switch (mod) {
		case MOD_GRAPPLE:
			message = "was caught by";
			break;
		case MOD_GAUNTLET:
			message = "was pummeled by";
			break;
		case MOD_MACHINEGUN:
			message = "was machinegunned by";
			break;
		case MOD_SHOTGUN:
			message = "was gunned down by";
			break;
		case MOD_GRENADE:
			message = "ate";
			message2 = "'s grenade";
			break;
		case MOD_GRENADE_SPLASH:
			message = "was shredded by";
			message2 = "'s shrapnel";
			break;
		case MOD_ROCKET:
			message = "ate";
			message2 = "'s rocket";
			break;
		case MOD_ROCKET_SPLASH:
			message = "almost dodged";
			message2 = "'s rocket";
			break;
		case MOD_PLASMA:
			message = "was melted by";
			message2 = "'s plasmagun";
			break;
		case MOD_PLASMA_SPLASH:
			message = "was melted by";
			message2 = "'s plasmagun";
			break;
		case MOD_RAILGUN:
			message = "was railed by";
			break;
		case MOD_LIGHTNING:
			message = "was electrocuted by";
			break;
		case MOD_BFG:
		case MOD_BFG_SPLASH:
			message = "was blasted by";
			message2 = "'s BFG";
			break;
		case MOD_NAIL:
			message = "was nailed by";
			break;
		case MOD_CHAINGUN:
			message = "got lead poisoning from";
			message2 = "'s Chaingun";
			break;
		case MOD_PROXIMITY_MINE:
			message = "was too close to";
			message2 = "'s Prox Mine";
			break;
		case MOD_KAMIKAZE:
			message = "falls to";
			message2 = "'s Kamikaze blast";
			break;
		case MOD_JUICED:
			message = "was juiced by";
			break;
		case MOD_TELEFRAG:
			message = "tried to invade";
			message2 = "'s personal space";
			break;
		default:
			message = "was killed by";
			break;
		}

		if (message) {
			CG_RecordObituaryFeedEntry( targetName, targetColorIndex,
				attackerName, attackerColorIndex, qtrue, icon, attacker, target, mod );
			CG_Printf( "%s %s %s%s\n", 
				targetName, message, attackerName, message2);
			return;
		}
	}

	// we don't know what it was
	CG_RecordObituaryFeedEntry( targetName, targetColorIndex, "", attackerColorIndex,
		qfalse, icon, attacker, target, mod );
	CG_Printf( "%s died.\n", targetName );
}

//==========================================================================

/*
===============
CG_UseItem
===============
*/
static void CG_UseItem( centity_t *cent ) {
	clientInfo_t *ci;
	int			itemNum, clientNum;
	gitem_t		*item;
	entityState_t *es;

	es = &cent->currentState;
	
	itemNum = (es->event & ~EV_EVENT_BITS) - EV_USE_ITEM0;
	if ( itemNum < 0 || itemNum > HI_NUM_HOLDABLE ) {
		itemNum = 0;
	}

	// print a message if the local player
	if ( es->number == cg.snap->ps.clientNum ) {
		if ( !itemNum ) {
			if ( cg_useItemWarning.integer ) {
				CG_CenterPrint( "No item to use", SCREEN_HEIGHT * 0.30f,
					CG_UseItemCenterPrintScale( cg_useItemWarning.integer ) );
			}
		} else if ( cg_useItemMessage.integer ) {
			item = BG_FindItemForHoldable( itemNum );
			CG_CenterPrint( va( "Use %s", item->pickup_name ), SCREEN_HEIGHT * 0.30f,
				CG_UseItemCenterPrintScale( cg_useItemMessage.integer ) );
		}
	}

	switch ( itemNum ) {
	default:
	case HI_NONE:
		trap_S_StartSound (NULL, es->number, CHAN_BODY, cgs.media.useNothingSound );
		break;

	case HI_TELEPORTER:
		break;

	case HI_MEDKIT:
		clientNum = cent->currentState.clientNum;
		if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
			ci = &cgs.clientinfo[ clientNum ];
			ci->medkitUsageTime = cg.time;
		}
		trap_S_StartSound (NULL, es->number, CHAN_BODY, cgs.media.medkitSound );
		break;

	case HI_KAMIKAZE:
		break;

	case HI_PORTAL:
		break;
	case HI_INVULNERABILITY:
		trap_S_StartSound (NULL, es->number, CHAN_BODY, cgs.media.useInvulnerabilitySound );
		break;
	}

}

/*
================
CG_ItemPickup

A new item was picked up this frame
================
*/
static void CG_ItemPickup( int itemNum ) {
	cg.itemPickup = itemNum;
	cg.itemPickupTime = cg.time;
	cg.itemPickupBlendTime = cg.time;
	// see if it should be the grabbed weapon
	if ( bg_itemlist[itemNum].giType == IT_WEAPON ) {
		weapon_t weapon;

		weapon = BG_WeaponForItemTag( bg_itemlist[itemNum].giTag );

		// select it immediately
		if ( cg_autoswitch.integer && weapon != WP_MACHINEGUN ) {
			cg.weaponSelectTime = cg.time;
			CG_SetWeaponSelect( weapon );
		}
	}

}


/*
================
CG_PainEvent

Also called by playerstate transition
================
*/
void CG_PainEvent( centity_t *cent, int health ) {
	char	*snd;

	// don't do more than two pain sounds a second
	if ( cg.time - cent->pe.painTime < 500 ) {
		return;
	}

	if ( health < 25 ) {
		snd = "*pain25_1.wav";
	} else if ( health < 50 ) {
		snd = "*pain50_1.wav";
	} else if ( health < 75 ) {
		snd = "*pain75_1.wav";
	} else {
		snd = "*pain100_1.wav";
	}
	trap_S_StartSound( NULL, cent->currentState.number, CHAN_VOICE, 
		CG_CustomSound( cent->currentState.number, snd ) );

	// save pain time for programitic twitch animation
	cent->pe.painTime = cg.time;
	cent->pe.painDirection ^= 1;
}

/*
=============
CG_IsSpectatorItemPickupEvent

Detects the synthetic retail spectator pickup event that shares the GPL
taunt value in the public enum path.
=============
*/
static qboolean CG_IsSpectatorItemPickupEvent( const entityState_t *es ) {
	if ( !es || es->eType <= ET_EVENTS ) {
		return qfalse;
	}

	if ( es->groundEntityNum <= 0 || es->groundEntityNum > MAX_CLIENTS ) {
		return qfalse;
	}

	if ( es->clientNum <= 0 || es->clientNum >= bg_numItems ) {
		return qfalse;
	}

	switch ( bg_itemlist[es->clientNum].giType ) {
	case IT_POWERUP:
		return qtrue;
	case IT_HEALTH:
		return ( qboolean )( bg_itemlist[es->clientNum].quantity >= 100 );
	case IT_ARMOR:
		return ( qboolean )( bg_itemlist[es->clientNum].quantity >= 50 );
	default:
		break;
	}

	return qfalse;
}

/*
=============
CG_HandleRetailOvertimeEvent

Processes the retail overtime temp-entity event outside the GPL taunt switch
value overlap.
=============
*/
static void CG_HandleRetailOvertimeEvent( void ) {
	if ( cg.snap ) {
		trap_S_StartSound( NULL, cg.snap->ps.clientNum, CHAN_AUTO,
			trap_S_RegisterSound( "sound/world/klaxon2.ogg", qfalse ) );
	}
	{
		int secondsAdded = ( cgs.matchOvertimeLengthSeconds > 0 ) ? cgs.matchOvertimeLengthSeconds : 90;

		CG_CenterPrint( va( "Overtime! %d seconds added", secondsAdded ), 90, 0.5f );
	}
	if ( CG_GetOvertimeCount() == 0 && cgs.media.overtimeSound ) {
		CG_AddBufferedSound( cgs.media.overtimeSound );
	}
}



/*
==============
CG_EntityEvent

An entity has an event value
also called by CG_CheckPlayerstateEvents
==============
*/
#define	DEBUGNAME(x) if(cg_debugEvents.integer){CG_Printf(x"\n");}
void CG_EntityEvent( centity_t *cent, vec3_t position ) {
	entityState_t	*es;
	int				event;
	vec3_t			dir;
	const char		*s;
	int				clientNum;
	clientInfo_t	*ci;

	es = &cent->currentState;
	event = es->event & ~EV_EVENT_BITS;

	if ( cg_debugEvents.integer ) {
		CG_Printf( "ent:%3i  event:%3i ", es->number, event );
	}

	if ( !event ) {
		DEBUGNAME("ZEROEVENT");
		return;
	}

	if ( event == EV_ITEM_PICKUP_SPEC && CG_IsSpectatorItemPickupEvent( es ) ) {
		DEBUGNAME("EV_ITEM_PICKUP_SPEC");
		CG_RecordSpectatorItemPickup( es );
		return;
	}

	clientNum = es->clientNum;
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		clientNum = 0;
	}
	ci = &cgs.clientinfo[ clientNum ];

	switch ( event ) {
	//
	// movement generated events
	//
	case QL_EV_OVERTIME:
		DEBUGNAME("QL_EV_OVERTIME");
		/*
		trap_S_RegisterSound( "sound/world/klaxon2.ogg", qfalse )
		CG_CenterPrint( va( "Overtime! %d seconds added", secondsAdded ), 90, BIGCHAR_WIDTH );
		CG_AddBufferedSound( cgs.media.overtimeSound );
		*/
		CG_HandleRetailOvertimeEvent();
		break;

	case EV_FOOTSTEP:
		DEBUGNAME("EV_FOOTSTEP");
		if (cg_footsteps.integer) {
			trap_S_StartSound (NULL, es->number, CHAN_BODY, 
				cgs.media.footsteps[ ci->footsteps ][rand()&3] );
		}
		break;
	case EV_FOOTSTEP_METAL:
		DEBUGNAME("EV_FOOTSTEP_METAL");
		if (cg_footsteps.integer) {
			trap_S_StartSound (NULL, es->number, CHAN_BODY, 
				cgs.media.footsteps[ FOOTSTEP_METAL ][rand()&3] );
		}
		break;
	case EV_FOOTSTEP_SNOW:
		DEBUGNAME("EV_FOOTSTEP_SNOW");
		if ( cg_footsteps.integer ) {
			trap_S_StartSound( NULL, es->number, CHAN_BODY,
				cgs.media.footsteps[ FOOTSTEP_SNOW ][rand()&3] );
		}
		break;
	case EV_FOOTSTEP_WOOD:
		DEBUGNAME("EV_FOOTSTEP_WOOD");
		if ( cg_footsteps.integer ) {
			trap_S_StartSound( NULL, es->number, CHAN_BODY,
				cgs.media.footsteps[ FOOTSTEP_WOOD ][rand()&3] );
		}
		break;
	case EV_FOOTSPLASH:
		DEBUGNAME("EV_FOOTSPLASH");
		if (cg_footsteps.integer) {
			trap_S_StartSound (NULL, es->number, CHAN_BODY, 
				cgs.media.footsteps[ FOOTSTEP_SPLASH ][rand()&3] );
		}
		break;
	case EV_FOOTWADE:
		DEBUGNAME("EV_FOOTWADE");
		if (cg_footsteps.integer) {
			trap_S_StartSound (NULL, es->number, CHAN_BODY, 
				cgs.media.footsteps[ FOOTSTEP_SPLASH ][rand()&3] );
		}
		break;
	case EV_SWIM:
		DEBUGNAME("EV_SWIM");
		if (cg_footsteps.integer) {
			trap_S_StartSound (NULL, es->number, CHAN_BODY, 
				cgs.media.footsteps[ FOOTSTEP_SPLASH ][rand()&3] );
		}
		break;


	case EV_FALL_SHORT:
		DEBUGNAME("EV_FALL_SHORT");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.landSound );
		if ( clientNum == cg.predictedPlayerState.clientNum ) {
			// smooth landing z changes
			cg.landChange = -8 * cg.kickScale;
			cg.landTime = cg.time;
		}
		break;
	case EV_FALL_MEDIUM:
		DEBUGNAME("EV_FALL_MEDIUM");
		// use normal pain sound
		trap_S_StartSound( NULL, es->number, CHAN_VOICE, CG_CustomSound( es->number, "*pain100_1.wav" ) );
		if ( clientNum == cg.predictedPlayerState.clientNum ) {
			// smooth landing z changes
			cg.landChange = -16 * cg.kickScale;
			cg.landTime = cg.time;
		}
		break;
	case EV_FALL_FAR:
		DEBUGNAME("EV_FALL_FAR");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, CG_CustomSound( es->number, "*fall1.wav" ) );
		cent->pe.painTime = cg.time;	// don't play a pain sound right after this
		if ( clientNum == cg.predictedPlayerState.clientNum ) {
			// smooth landing z changes
			cg.landChange = -24 * cg.kickScale;
			cg.landTime = cg.time;
		}
		break;

	case EV_JUMP_PAD:
		DEBUGNAME("EV_JUMP_PAD");
//		CG_Printf( "EV_JUMP_PAD w/effect #%i\n", es->eventParm );
		{
			localEntity_t	*smoke;
			vec3_t			up = {0, 0, 1};


			smoke = CG_SmokePuff( cent->lerpOrigin, up, 
						  32, 
						  1, 1, 1, 0.33f,
						  1000, 
						  cg.time, 0,
						  LEF_PUFF_DONT_SCALE, 
						  cgs.media.smokePuffShader );
		}

		// boing sound at origin, jump sound on player
		trap_S_StartSound ( cent->lerpOrigin, -1, CHAN_VOICE, cgs.media.jumpPadSound );
		trap_S_StartSound (NULL, es->number, CHAN_VOICE, CG_CustomSound( es->number, "*jump1.wav" ) );
		break;

	case EV_JUMP:
		DEBUGNAME("EV_JUMP");
		trap_S_StartSound (NULL, es->number, CHAN_VOICE, CG_CustomSound( es->number, "*jump1.wav" ) );
		break;
	case EV_TAUNT:
		DEBUGNAME("EV_TAUNT");
		if ( !cg_allowTaunt.integer ) {
			break;
		}
		trap_S_StartSound (NULL, es->number, CHAN_VOICE, CG_CustomSound( es->number, "*taunt.wav" ) );
		break;
	case EV_TAUNT_YES:
		DEBUGNAME("EV_TAUNT_YES");
		if ( !cg_allowTaunt.integer ) {
			break;
		}
		CG_VoiceChatLocal(SAY_TEAM, qfalse, es->number, COLOR_CYAN, VOICECHAT_YES);
		break;
	case EV_TAUNT_NO:
		DEBUGNAME("EV_TAUNT_NO");
		if ( !cg_allowTaunt.integer ) {
			break;
		}
		CG_VoiceChatLocal(SAY_TEAM, qfalse, es->number, COLOR_CYAN, VOICECHAT_NO);
		break;
	case EV_TAUNT_FOLLOWME:
		DEBUGNAME("EV_TAUNT_FOLLOWME");
		if ( !cg_allowTaunt.integer ) {
			break;
		}
		CG_VoiceChatLocal(SAY_TEAM, qfalse, es->number, COLOR_CYAN, VOICECHAT_FOLLOWME);
		break;
	case EV_TAUNT_GETFLAG:
		DEBUGNAME("EV_TAUNT_GETFLAG");
		if ( !cg_allowTaunt.integer ) {
			break;
		}
		CG_VoiceChatLocal(SAY_TEAM, qfalse, es->number, COLOR_CYAN, VOICECHAT_ONGETFLAG);
		break;
	case EV_TAUNT_GUARDBASE:
		DEBUGNAME("EV_TAUNT_GUARDBASE");
		if ( !cg_allowTaunt.integer ) {
			break;
		}
		CG_VoiceChatLocal(SAY_TEAM, qfalse, es->number, COLOR_CYAN, VOICECHAT_ONDEFENSE);
		break;
	case EV_TAUNT_PATROL:
		DEBUGNAME("EV_TAUNT_PATROL");
		if ( !cg_allowTaunt.integer ) {
			break;
		}
		CG_VoiceChatLocal(SAY_TEAM, qfalse, es->number, COLOR_CYAN, VOICECHAT_ONPATROL);
		break;
	case EV_WATER_TOUCH:
		DEBUGNAME("EV_WATER_TOUCH");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.watrInSound );
		break;
	case EV_WATER_LEAVE:
		DEBUGNAME("EV_WATER_LEAVE");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.watrOutSound );
		break;
	case EV_WATER_UNDER:
		DEBUGNAME("EV_WATER_UNDER");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.watrUnSound );
		break;
	case EV_WATER_CLEAR:
		DEBUGNAME("EV_WATER_CLEAR");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, CG_CustomSound( es->number, "*gasp.wav" ) );
		break;

	case EV_ITEM_PICKUP:
		DEBUGNAME("EV_ITEM_PICKUP");
		{
			gitem_t	*item;
			int		index;

			index = es->eventParm;		// player predicted

			if ( index < 1 || index >= bg_numItems ) {
				break;
			}
			item = &bg_itemlist[ index ];

			// powerups and team items will have a separate global sound, this one
			// will be played at prediction time
			if ( item->giType == IT_POWERUP || item->giType == IT_TEAM) {
				trap_S_StartSound (NULL, es->number, CHAN_AUTO,	cgs.media.n_healthSound );
			} else if (item->giType == IT_PERSISTANT_POWERUP) {
				switch (item->giTag ) {
					case PW_SCOUT:
						trap_S_StartSound (NULL, es->number, CHAN_AUTO,	cgs.media.scoutSound );
					break;
					case PW_GUARD:
						trap_S_StartSound (NULL, es->number, CHAN_AUTO,	cgs.media.guardSound );
					break;
					case PW_DOUBLER:
						trap_S_StartSound (NULL, es->number, CHAN_AUTO,	cgs.media.doublerSound );
					break;
					case PW_AMMOREGEN:
						trap_S_StartSound (NULL, es->number, CHAN_AUTO,	cgs.media.ammoregenSound );
					break;
				}
			} else {
				trap_S_StartSound (NULL, es->number, CHAN_AUTO,	trap_S_RegisterSound( item->pickup_sound, qfalse ) );
			}

			// show icon and name on status bar
			if ( es->number == cg.snap->ps.clientNum ) {
				CG_ItemPickup( index );
			}
		}
		break;

	case EV_GLOBAL_ITEM_PICKUP:
		DEBUGNAME("EV_GLOBAL_ITEM_PICKUP");
		{
			gitem_t	*item;
			int		index;

			index = es->eventParm;		// player predicted

			if ( index < 1 || index >= bg_numItems ) {
				break;
			}
			item = &bg_itemlist[ index ];
			// powerup pickups are global
			if( item->pickup_sound ) {
				trap_S_StartSound (NULL, cg.snap->ps.clientNum, CHAN_AUTO, trap_S_RegisterSound( item->pickup_sound, qfalse ) );
			}

			// show icon and name on status bar
			if ( es->number == cg.snap->ps.clientNum ) {
				CG_ItemPickup( index );
			}
		}
		break;

	//
	// weapon events
	//
	case EV_NOAMMO:
		DEBUGNAME("EV_NOAMMO");
//		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.noAmmoSound );
		if ( es->number == cg.snap->ps.clientNum && cg_switchOnEmpty.integer ) {
			CG_OutOfAmmoChange();
		}
		break;
	case EV_CHANGE_WEAPON:
		DEBUGNAME("EV_CHANGE_WEAPON");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.selectSound );
		break;
	case EV_DROP_WEAPON:
		DEBUGNAME("EV_DROP_WEAPON");
		if ( CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) ) ) {
			weapon_t	excludedWeapon;

			excludedWeapon = ( es->weapon > WP_NONE && es->weapon < WP_NUM_WEAPONS )
				? (weapon_t)es->weapon
				: ( cg.snap ? (weapon_t)cg.snap->ps.weapon : WP_NONE );
			CG_SelectHighestWeaponExcluding( excludedWeapon );
		}
		break;
	case EV_FIRE_WEAPON:
		DEBUGNAME("EV_FIRE_WEAPON");
		CG_FireWeapon( cent );
		break;

	case EV_USE_ITEM0:
		DEBUGNAME("EV_USE_ITEM0");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM1:
		DEBUGNAME("EV_USE_ITEM1");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM2:
		DEBUGNAME("EV_USE_ITEM2");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM3:
		DEBUGNAME("EV_USE_ITEM3");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM4:
		DEBUGNAME("EV_USE_ITEM4");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM5:
		DEBUGNAME("EV_USE_ITEM5");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM6:
		DEBUGNAME("EV_USE_ITEM6");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM7:
		DEBUGNAME("EV_USE_ITEM7");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM8:
		DEBUGNAME("EV_USE_ITEM8");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM9:
		DEBUGNAME("EV_USE_ITEM9");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM10:
		DEBUGNAME("EV_USE_ITEM10");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM11:
		DEBUGNAME("EV_USE_ITEM11");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM12:
		DEBUGNAME("EV_USE_ITEM12");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM13:
		DEBUGNAME("EV_USE_ITEM13");
		CG_UseItem( cent );
		break;
	case EV_USE_ITEM14:
		DEBUGNAME("EV_USE_ITEM14");
		CG_UseItem( cent );
		break;

	//=================================================================

	//
	// other events
	//
	case EV_PLAYER_TELEPORT_IN:
		DEBUGNAME("EV_PLAYER_TELEPORT_IN");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.teleInSound );
		CG_SpawnEffect( position);
		break;

	case EV_PLAYER_TELEPORT_OUT:
		DEBUGNAME("EV_PLAYER_TELEPORT_OUT");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.teleOutSound );
		CG_SpawnEffect(  position);
		break;

	case EV_ITEM_POP:
		DEBUGNAME("EV_ITEM_POP");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.respawnSound );
		break;
	case EV_ITEM_RESPAWN:
		DEBUGNAME("EV_ITEM_RESPAWN");
		cent->miscTime = cg.time;	// scale up from this
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.respawnSound );
		break;

	case EV_GRENADE_BOUNCE:
		DEBUGNAME("EV_GRENADE_BOUNCE");
		if ( rand() & 1 ) {
			trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.hgrenb1aSound );
		} else {
			trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.hgrenb2aSound );
		}
		break;

	case EV_PROXIMITY_MINE_STICK:
		DEBUGNAME("EV_PROXIMITY_MINE_STICK");
		if( es->eventParm & SURF_FLESH ) {
			trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbimplSound );
		} else 	if( es->eventParm & SURF_METALSTEPS ) {
			trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbimpmSound );
		} else {
			trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbimpdSound );
		}
		break;

	case EV_PROXIMITY_MINE_TRIGGER:
		DEBUGNAME("EV_PROXIMITY_MINE_TRIGGER");
		trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbactvSound );
		break;
	case EV_KAMIKAZE:
		DEBUGNAME("EV_KAMIKAZE");
		CG_KamikazeEffect( cent->lerpOrigin );
		break;
	case EV_OBELISKEXPLODE:
		DEBUGNAME("EV_OBELISKEXPLODE");
		CG_ObeliskExplode( cent->lerpOrigin, es->eventParm );
		break;
	case EV_OBELISKPAIN:
		DEBUGNAME("EV_OBELISKPAIN");
		CG_ObeliskPain( cent->lerpOrigin );
		break;
	case EV_INVUL_IMPACT:
		DEBUGNAME("EV_INVUL_IMPACT");
		CG_InvulnerabilityImpact( cent->lerpOrigin, cent->currentState.angles );
		break;
	case EV_JUICED:
		DEBUGNAME("EV_JUICED");
		CG_InvulnerabilityJuiced( cent->lerpOrigin );
		break;
	case EV_LIGHTNINGBOLT:
		DEBUGNAME("EV_LIGHTNINGBOLT");
		CG_LightningBoltBeam(es->origin2, es->pos.trBase);
		break;
	case EV_SCOREPLUM:
		DEBUGNAME("EV_SCOREPLUM");
		CG_ScorePlum( cent->currentState.otherEntityNum, cent->lerpOrigin, cent->currentState.time );
		break;
	case EV_DAMAGEPLUM:
		DEBUGNAME("EV_DAMAGEPLUM");
		if ( CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) ) ) {
			CG_DamagePlum( cent->lerpOrigin, CG_GetRetailDamagePlumDamage( es ), CG_GetRetailDamagePlumWeapon( es ) );
		}
		break;
	case EV_POI:
		DEBUGNAME("EV_POI");
		CG_POIEvent( cent, es );
		break;
	case EV_THAW_PLAYER:
		DEBUGNAME("EV_THAW_PLAYER");
		CG_ThawPlayer( position );
		break;
	case EV_THAW_TICK:
		DEBUGNAME("EV_THAW_TICK");
		if ( cgs.media.thawTickSound ) {
			trap_S_StartSound( NULL, es->number, CHAN_BODY, cgs.media.thawTickSound );
		}
		break;

	//
	// missile impacts
	//
	case EV_MISSILE_MISS_DMGTHROUGH:
		DEBUGNAME("EV_MISSILE_MISS_DMGTHROUGH");
		ByteToDir( es->eventParm, dir );
		CG_MissileHitWallDmgThrough( position, dir, es->weapon );
		break;

	case EV_MISSILE_HIT:
		DEBUGNAME("EV_MISSILE_HIT");
		ByteToDir( es->eventParm, dir );
		CG_MissileHitPlayer( es->weapon, position, dir, es->otherEntityNum );
		break;

	case EV_MISSILE_MISS:
		DEBUGNAME("EV_MISSILE_MISS");
		ByteToDir( es->eventParm, dir );
		CG_MissileHitWall( es->weapon, 0, position, dir, IMPACTSOUND_DEFAULT );
		break;

	case EV_MISSILE_MISS_METAL:
		DEBUGNAME("EV_MISSILE_MISS_METAL");
		ByteToDir( es->eventParm, dir );
		CG_MissileHitWall( es->weapon, 0, position, dir, IMPACTSOUND_METAL );
		break;

	case EV_RAILTRAIL:
		DEBUGNAME("EV_RAILTRAIL");
		cent->currentState.weapon = WP_RAILGUN;
		if ( CG_ShouldSuppressPredictedRailEvent( es ) ) {
			cg.predictedLocalRailValid = qfalse;
			break;
		}
		// if the end was on a nomark surface, don't make an explosion
		CG_RailTrail( ci, es->origin2, es->pos.trBase );
		if ( es->eventParm != 255 ) {
			ByteToDir( es->eventParm, dir );
			CG_MissileHitWall( es->weapon, es->clientNum, position, dir, IMPACTSOUND_DEFAULT );
		}
		break;

	case EV_BULLET_HIT_WALL:
		DEBUGNAME("EV_BULLET_HIT_WALL");
		ByteToDir( es->eventParm, dir );
		CG_Bullet( es->pos.trBase, es->otherEntityNum, dir, qfalse, ENTITYNUM_WORLD );
		break;

	case EV_BULLET_HIT_FLESH:
		DEBUGNAME("EV_BULLET_HIT_FLESH");
		CG_Bullet( es->pos.trBase, es->otherEntityNum, dir, qtrue, es->eventParm );
		break;

	case EV_SHOTGUN:
		DEBUGNAME("EV_SHOTGUN");
		CG_ShotgunFire( es );
		break;

	case EV_SHOTGUN_KILL:
		DEBUGNAME("EV_SHOTGUN_KILL");
		CG_ShotgunKillEffect( cent, es );
		break;

	case EV_GENERAL_SOUND:
		DEBUGNAME("EV_GENERAL_SOUND");
		if ( cgs.gameSounds[ es->eventParm ] ) {
			trap_S_StartSound (NULL, es->number, CHAN_VOICE, cgs.gameSounds[ es->eventParm ] );
		} else {
			s = CG_ConfigString( CS_SOUNDS + es->eventParm );
			trap_S_StartSound (NULL, es->number, CHAN_VOICE, CG_CustomSound( es->number, s ) );
		}
		break;

	case EV_GLOBAL_SOUND:	// play from the player's head so it never diminishes
		DEBUGNAME("EV_GLOBAL_SOUND");
		if ( cgs.gameSounds[ es->eventParm ] ) {
			trap_S_StartSound (NULL, cg.snap->ps.clientNum, CHAN_AUTO, cgs.gameSounds[ es->eventParm ] );
		} else {
			s = CG_ConfigString( CS_SOUNDS + es->eventParm );
			trap_S_StartSound (NULL, cg.snap->ps.clientNum, CHAN_AUTO, CG_CustomSound( es->number, s ) );
		}
		break;

	case EV_GLOBAL_TEAM_SOUND:	// play from the player's head so it never diminishes
		{
			int	globalTeamSound;

			DEBUGNAME("EV_GLOBAL_TEAM_SOUND");
			globalTeamSound = CG_GetGlobalTeamSound( es );
			switch( globalTeamSound ) {
				case GTS_RED_CAPTURE: // CTF: red team captured the blue flag, 1FCTF: red team captured the neutral flag
					if ( cgs.clientinfo[cg.clientNum].team == TEAM_RED )
						CG_AddBufferedSound( cgs.media.captureYourTeamSound );
					else
						CG_AddBufferedSound( cgs.media.captureOpponentSound );
					break;
				case GTS_BLUE_CAPTURE: // CTF: blue team captured the red flag, 1FCTF: blue team captured the neutral flag
					if ( cgs.clientinfo[cg.clientNum].team == TEAM_BLUE )
						CG_AddBufferedSound( cgs.media.captureYourTeamSound );
					else
						CG_AddBufferedSound( cgs.media.captureOpponentSound );
					break;
				case GTS_RED_RETURN: // CTF: blue flag returned, 1FCTF: never used
					if ( cgs.clientinfo[cg.clientNum].team == TEAM_RED )
						CG_AddBufferedSound( cgs.media.returnYourTeamSound );
					else
						CG_AddBufferedSound( cgs.media.returnOpponentSound );
					//
					CG_AddBufferedSound( cgs.media.blueFlagReturnedSound );
					break;
			case GTS_BLUE_RETURN: // CTF red flag returned, 1FCTF: neutral flag returned
				if ( cgs.clientinfo[cg.clientNum].team == TEAM_BLUE )
					CG_AddBufferedSound( cgs.media.returnYourTeamSound );
				else
					CG_AddBufferedSound( cgs.media.returnOpponentSound );
				//
				CG_AddBufferedSound( cgs.media.redFlagReturnedSound );
				break;

			case GTS_RED_TAKEN: // CTF: red team took blue flag, 1FCTF: blue team took the neutral flag
				// if this player picked up the flag then a sound is played in CG_CheckLocalSounds
				if (cg.snap->ps.powerups[PW_BLUEFLAG] || cg.snap->ps.powerups[PW_NEUTRALFLAG]) {
				}
				else {
					if (cgs.clientinfo[cg.clientNum].team == TEAM_BLUE) {
						if (cgs.gametype == GT_1FCTF) {
							CG_AddBufferedSound( cgs.media.yourTeamTookTheFlagSound );
						} else {
							CG_AddBufferedSound( cgs.media.enemyTookYourFlagSound );
						}
					}
					else if (cgs.clientinfo[cg.clientNum].team == TEAM_RED) {
						if (cgs.gametype == GT_1FCTF) {
							CG_AddBufferedSound( cgs.media.enemyTookTheFlagSound );
						} else {
							CG_AddBufferedSound( cgs.media.yourTeamTookEnemyFlagSound );
						}
					}
				}
				CG_TrackFlagCarrierForEvent( es );
				break;
			case GTS_BLUE_TAKEN: // CTF: blue team took the red flag, 1FCTF red team took the neutral flag
				// if this player picked up the flag then a sound is played in CG_CheckLocalSounds
				if (cg.snap->ps.powerups[PW_REDFLAG] || cg.snap->ps.powerups[PW_NEUTRALFLAG]) {
				}
				else {
					if (cgs.clientinfo[cg.clientNum].team == TEAM_RED) {
						if (cgs.gametype == GT_1FCTF) {
							CG_AddBufferedSound( cgs.media.yourTeamTookTheFlagSound );
						} else {
							CG_AddBufferedSound( cgs.media.enemyTookYourFlagSound );
						}
					}
					else if (cgs.clientinfo[cg.clientNum].team == TEAM_BLUE) {
						if (cgs.gametype == GT_1FCTF) {
							CG_AddBufferedSound( cgs.media.enemyTookTheFlagSound );
						} else {
							CG_AddBufferedSound( cgs.media.yourTeamTookEnemyFlagSound );
						}
					}
				}
				CG_TrackFlagCarrierForEvent( es );
				break;
				case GTS_REDOBELISK_ATTACKED: // Overload: red obelisk is being attacked
					if (cgs.clientinfo[cg.clientNum].team == TEAM_RED) {
						CG_AddBufferedSound( cgs.media.yourBaseIsUnderAttackSound );
					}
					break;
				case GTS_BLUEOBELISK_ATTACKED: // Overload: blue obelisk is being attacked
					if (cgs.clientinfo[cg.clientNum].team == TEAM_BLUE) {
						CG_AddBufferedSound( cgs.media.yourBaseIsUnderAttackSound );
					}
					break;

				case GTS_REDTEAM_SCORED:
					CG_AddBufferedSound(cgs.media.redScoredSound);
					break;
				case GTS_BLUETEAM_SCORED:
					CG_AddBufferedSound(cgs.media.blueScoredSound);
					break;
				case GTS_REDTEAM_TOOK_LEAD:
					CG_AddBufferedSound(cgs.media.redLeadsSound);
					break;
				case GTS_BLUETEAM_TOOK_LEAD:
					CG_AddBufferedSound(cgs.media.blueLeadsSound);
					break;
				case GTS_TEAMS_ARE_TIED:
					CG_AddBufferedSound( cgs.media.teamsTiedSound );
					break;
				case GTS_KAMIKAZE:
					trap_S_StartLocalSound(cgs.media.kamikazeFarSound, CHAN_ANNOUNCER);
					break;
				case GTS_REDTEAM_WINS:
					CG_ClearBufferedAnnouncements();
					trap_S_StartLocalSound( trap_S_RegisterSound( "sound/world/buzzer.ogg", qfalse ), CHAN_LOCAL_SOUND );
					if ( cgs.clientinfo[cg.clientNum].team == TEAM_RED ) {
						trap_S_StartBackgroundTrack( "music/win", "" );
					} else if ( cgs.clientinfo[cg.clientNum].team == TEAM_BLUE ) {
						trap_S_StartBackgroundTrack( "music/loss", "" );
					}
					CG_AddBufferedSound( cgs.media.redWinsSound );
					break;
				case GTS_BLUETEAM_WINS:
					CG_ClearBufferedAnnouncements();
					trap_S_StartLocalSound( trap_S_RegisterSound( "sound/world/buzzer.ogg", qfalse ), CHAN_LOCAL_SOUND );
					if ( cgs.clientinfo[cg.clientNum].team == TEAM_BLUE ) {
						trap_S_StartBackgroundTrack( "music/win", "" );
					} else if ( cgs.clientinfo[cg.clientNum].team == TEAM_RED ) {
						trap_S_StartBackgroundTrack( "music/loss", "" );
					}
					CG_AddBufferedSound( cgs.media.blueWinsSound );
					break;
				case GTS_REDTEAM_WINS_ROUND:
					CG_AddBufferedSound( cgs.media.redWinsRoundSound );
					break;
				case GTS_BLUETEAM_WINS_ROUND:
					CG_AddBufferedSound( cgs.media.blueWinsRoundSound );
					break;
				case GTS_ROUND_DRAW:
					CG_ClearBufferedAnnouncements();
					CG_AddBufferedSound( cgs.media.roundDrawSound );
					break;
				case GTS_LAST_STANDING:
					if ( CG_GetGlobalTeamSoundTeam( es ) == cgs.clientinfo[cg.clientNum].team ) {
						CG_AddBufferedSound( cgs.media.lastStandingSound );
					}
					break;
				case GTS_ROUND_OVER:
					CG_AddBufferedSound( cgs.media.roundOverSound );
					break;
				case GTS_DOMINATION_POINT_EVENT:
					CG_PlayDominationPointAnnouncement( es );
					break;
				case GTS_SURVIVOR_WARNING:
					if ( CG_GetGlobalTeamSoundTeam( es ) == cgs.clientinfo[cg.clientNum].team ) {
						CG_AddBufferedSound( cgs.media.survivorWarningSound );
					}
					break;
				default:
					break;
			}
			break;
		}

	case EV_PAIN:
		// local player sounds are triggered in CG_CheckLocalSounds,
		// so ignore events on the player
		DEBUGNAME("EV_PAIN");
		if ( cent->currentState.number != cg.snap->ps.clientNum ) {
			CG_PainEvent( cent, es->eventParm );
		}
		break;

	case EV_DEATH1:
	case EV_DEATH2:
	case EV_DEATH3:
		DEBUGNAME("EV_DEATHx");
		trap_S_StartSound( NULL, es->number, CHAN_VOICE, 
				CG_CustomSound( es->number, va("*death%i.wav", event - EV_DEATH1 + 1) ) );
		break;
	case EV_DROWN:
		DEBUGNAME("EV_DROWN");
		trap_S_StartSound( NULL, es->number, CHAN_VOICE, CG_CustomSound( es->number, "*drown.wav" ) );
		break;


	case EV_OBITUARY:
		DEBUGNAME("EV_OBITUARY");
		CG_Obituary( es );
		break;

	//
	// powerup events
	//
	case EV_POWERUP_QUAD:
		DEBUGNAME("EV_POWERUP_QUAD");
		if ( es->number == cg.snap->ps.clientNum ) {
			cg.powerupActive = PW_QUAD;
			cg.powerupTime = cg.time;
		}
		trap_S_StartSound (NULL, es->number, CHAN_ITEM, cgs.media.quadSound );
		CG_SpectatorTrackEvent( es->number, CG_SPECTATOR_TRACK_POWERUP );
		break;
	case EV_POWERUP_BATTLESUIT:
		DEBUGNAME("EV_POWERUP_BATTLESUIT");
		if ( es->number == cg.snap->ps.clientNum ) {
			cg.powerupActive = PW_BATTLESUIT;
			cg.powerupTime = cg.time;
		}
		trap_S_StartSound (NULL, es->number, CHAN_ITEM, cgs.media.protectSound );
		CG_SpectatorTrackEvent( es->number, CG_SPECTATOR_TRACK_POWERUP );
		break;
	case EV_POWERUP_REGEN:
		DEBUGNAME("EV_POWERUP_REGEN");
		if ( es->number == cg.snap->ps.clientNum ) {
			cg.powerupActive = PW_REGEN;
			cg.powerupTime = cg.time;
		}
		trap_S_StartSound (NULL, es->number, CHAN_ITEM, cgs.media.regenSound );
		CG_SpectatorTrackEvent( es->number, CG_SPECTATOR_TRACK_POWERUP );
		break;
	case EV_POWERUP_ARMORREGEN:
		DEBUGNAME("EV_POWERUP_ARMORREGEN");
		if ( es->number == cg.snap->ps.clientNum ) {
			cg.powerupActive = PW_AMMOREGEN;
			cg.powerupTime = cg.time;
		}
		trap_S_StartSound( NULL, es->number, CHAN_ITEM, cgs.media.armorregenSound );
		CG_SpectatorTrackEvent( es->number, CG_SPECTATOR_TRACK_POWERUP );
		break;

	case EV_GIB_PLAYER:
		DEBUGNAME("EV_GIB_PLAYER");
		// don't play gib sound when using the kamikaze because it interferes
		// with the kamikaze sound, downside is that the gib sound will also
		// not be played when someone is gibbed while just carrying the kamikaze
		if ( !(es->eFlags & EF_KAMIKAZE) ) {
			trap_S_StartSound( NULL, es->number, CHAN_BODY, cgs.media.gibSound );
		}
		CG_GibPlayer( cent->lerpOrigin );
		break;

	case EV_DEBUG_LINE:
		DEBUGNAME("EV_DEBUG_LINE");
		CG_Beam( cent );
		break;

	case QL_EV_GAMEOVER:
		DEBUGNAME("QL_EV_GAMEOVER");
		CG_ClearBufferedAnnouncements();
		trap_S_StartLocalSound( trap_S_RegisterSound( "sound/world/buzzer.ogg", qfalse ), CHAN_LOCAL_SOUND );
		if ( CG_IsLocalPlayerWinner() ) {
			if ( cgs.media.winnerSound ) {
				CG_AddBufferedSound( cgs.media.winnerSound );
			}
			trap_S_StartBackgroundTrack( "music/win", "" );
		} else if ( cg.snap && cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
			trap_S_StartBackgroundTrack( "music/win", "" );
		} else {
			if ( cgs.media.loserSound ) {
				CG_AddBufferedSound( cgs.media.loserSound );
			}
			trap_S_StartBackgroundTrack( "music/loss", "" );
		}
		break;

	case QL_EV_LIGHTNING_DISCHARGE:
		DEBUGNAME("QL_EV_LIGHTNING_DISCHARGE");
		CG_LightningDischargeEffect( cent->lerpOrigin, es->eventParm );
		break;

	case QL_EV_RACE_START:
		DEBUGNAME("QL_EV_RACE_START");
		if ( CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) ) ) {
			CG_RaceResetRunState( qfalse );
			cgs.raceInfoActive = qtrue;
			cgs.raceInfoStartTime = CG_GetRetailEventIntPayload( es );
			cgs.raceInfoCheckpointCount = CG_GetRaceEventCheckpointCount( es );
			cgs.raceInfoCurrentCheckpointEntityNum = CG_GetRaceEventCurrentCheckpointEntityNum( es );
			cgs.raceInfoNextCheckpointEntityNum = CG_GetRaceEventNextCheckpointEntityNum( es );
			CG_RacePlayCue( CG_RACE_CUE_START );
		}
		break;

	case QL_EV_RACE_CHECKPOINT:
		DEBUGNAME("QL_EV_RACE_CHECKPOINT");
		if ( CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) ) ) {
			cgs.raceInfoActive = qtrue;
			cgs.raceInfoCheckpointCount = CG_GetRaceEventCheckpointCount( es );
			cgs.raceInfoCurrentCheckpointEntityNum = CG_GetRaceEventCurrentCheckpointEntityNum( es );
			cgs.raceInfoNextCheckpointEntityNum = CG_GetRaceEventNextCheckpointEntityNum( es );
			CG_RacePlayCue( CG_RACE_CUE_CHECKPOINT );
		}
		break;

	case QL_EV_RACE_FINISH:
		DEBUGNAME("QL_EV_RACE_FINISH");
		if ( CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) ) ) {
			CG_RaceResetRunState( qfalse );
			cgs.raceInfoLastTime = CG_GetRetailEventIntPayload( es );
			CG_RacePlayCue( CG_RACE_CUE_FINISH );
		}
		break;

	case QL_EV_AWARD:
		DEBUGNAME("QL_EV_AWARD");
		CG_HandleRetailAwardEvent( es );
		break;

	case QL_EV_INFECTED:
		DEBUGNAME("QL_EV_INFECTED");
		if ( CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) ) && cgs.media.infectedSound ) {
			CG_AddBufferedSound( cgs.media.infectedSound );
		}
		break;

	case QL_EV_NEW_HIGH_SCORE:
		DEBUGNAME("QL_EV_NEW_HIGH_SCORE");
		if ( CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) ) && cgs.media.newHighScoreSound ) {
			CG_AddBufferedSound( cgs.media.newHighScoreSound );
		}
		break;

	default:
		DEBUGNAME("UNKNOWN");
		CG_Error( "Unknown event: %i", event );
		break;
	}

}


/*
==============
CG_CheckEvents

==============
*/
void CG_CheckEvents( centity_t *cent ) {
	// check for event-only entities
	if ( cent->currentState.eType > ET_EVENTS ) {
		if ( cent->previousEvent ) {
			return;	// already fired
		}
		// if this is a player event set the entity number of the client entity number
		if ( cent->currentState.eFlags & EF_PLAYER_EVENT ) {
			cent->currentState.number = cent->currentState.otherEntityNum;
		}

		cent->previousEvent = 1;

		cent->currentState.event = cent->currentState.eType - ET_EVENTS;
	} else {
		// check for events riding with another entity
		if ( cent->currentState.event == cent->previousEvent ) {
			return;
		}
		cent->previousEvent = cent->currentState.event;
		if ( ( cent->currentState.event & ~EV_EVENT_BITS ) == 0 ) {
			return;
		}
	}

	// calculate the position at exactly the frame time
	BG_EvaluateTrajectory( &cent->currentState.pos, cg.snap->serverTime, cent->lerpOrigin );
	CG_SetEntitySoundPosition( cent );

	CG_EntityEvent( cent, cent->lerpOrigin );
}

