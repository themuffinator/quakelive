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
// cg_consolecmds.c -- text commands typed in at the local console, or
// executed by a key binding

#include "cg_local.h"
#include "../ui/ui_shared.h"
extern menuDef_t *menuScoreboard;

static qboolean	cg_pstatsRequestActive;



void CG_TargetCommand_f( void ) {
	int		targetNum;
	char	test[4];

	targetNum = CG_CrosshairPlayer();
	if (!targetNum ) {
		return;
	}

	trap_Argv( 1, test, 4 );
	trap_SendConsoleCommand( va( "gc %i %i", targetNum, atoi( test ) ) );
}



/*
=================
CG_SizeUp_f

Keybinding command
=================
*/
static void CG_SizeUp_f (void) {
	trap_Cvar_Set("cg_viewsize", va("%i",(int)(cg_viewsize.integer+10)));
}


/*
=================
CG_SizeDown_f

Keybinding command
=================
*/
static void CG_SizeDown_f (void) {
	trap_Cvar_Set("cg_viewsize", va("%i",(int)(cg_viewsize.integer-10)));
}


/*
=============
CG_Viewpos_f

Debugging command to print the current position
=============
*/
static void CG_Viewpos_f (void) {
	CG_Printf ("(%i %i %i) : %i\n", (int)cg.refdef.vieworg[0],
		(int)cg.refdef.vieworg[1], (int)cg.refdef.vieworg[2], 
		(int)cg.refdefViewAngles[YAW]);
}


/*
=============
CG_ScoresDown_f

Retail `+scores` handler shared by the console-command table and the cgame HUD
binding intercept path.
=============
*/
void CG_ScoresDown_f( void ) {

		CG_BuildSpectatorString();
	if ( cg.scoresRequestTime + 2000 < cg.time ) {
		// the scores are more than two seconds out of data,
		// so request new ones
		cg.scoresRequestTime = cg.time;
		trap_SendClientCommand( "score" );

		// leave the current scores up if they were already
		// displayed, but if this is the first hit, clear them out
		if ( !cg.showScores ) {
			cg.showScores = qtrue;
			cg.numScores = 0;
		}
	} else {
		// show the cached contents even if they just pressed if it
		// is within two seconds
		cg.showScores = qtrue;
	}
}

static void CG_ScoresUp_f( void ) {
	if ( cg.showScores ) {
		cg.showScores = qfalse;
		cg.scoreFadeTime = cg.time;
	}
}

/*
=============
CG_AccDown_f

Mirrors the retail `+acc` command by arming the vertical accuracy overlay and
issuing an immediate request when the local client is not free-spectating.
=============
*/
static void CG_AccDown_f( void ) {
	if ( !cg.snap ) {
		return;
	}

	if ( cg.snap->ps.pm_type == PM_SPECTATOR &&
			!( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		return;
	}

	if ( cg.accRequestTime + 1000 < cg.time ) {
		cg.accRequestTime = cg.time;
		trap_SendClientCommand( "acc" );
	}

	cg.accRequestActive = qtrue;
}

/*
=============
CG_AccUp_f

Mirrors the retail `-acc` command by dismissing the vertical accuracy overlay.
=============
*/
static void CG_AccUp_f( void ) {
	if ( cg.accRequestActive ) {
		cg.accRequestActive = qfalse;
	}
}

/*
=============
CG_PStatsDown_f

Mirrors the retail `+pstats` command by issuing an immediate request when the
local client is not free-spectating.
=============
*/
static void CG_PStatsDown_f( void ) {
	if ( !cg.snap ) {
		return;
	}

	if ( cg.snap->ps.pm_type == PM_SPECTATOR &&
			!( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		return;
	}

	if ( cg.accRequestTime + 1000 < cg.time ) {
		cg.accRequestTime = cg.time;
		trap_SendClientCommand( "pstats" );
	}

	cg_pstatsRequestActive = qtrue;
}

/*
=============
CG_PStatsUp_f

Mirrors the retail `-pstats` command by dismissing the pstats request latch.
=============
*/
static void CG_PStatsUp_f( void ) {
	if ( cg_pstatsRequestActive ) {
		cg_pstatsRequestActive = qfalse;
	}
}

/*
=============
CG_LoadHud_f

Replays the retail HUD bootstrap on demand, including supplemental overlays and
scoreboard-menu caches.
=============
*/
static void CG_LoadHud_f( void ) {
	CG_InitBrowserRuntime();
	CG_LoadHudMenu();
}

static void CG_scrollScoresDown_f( void) {
	if (menuScoreboard && cg.scoreBoardShowing) {
		Menu_ScrollFeeder(menuScoreboard, FEEDER_SCOREBOARD, qtrue);
		Menu_ScrollFeeder(menuScoreboard, FEEDER_REDTEAM_LIST, qtrue);
		Menu_ScrollFeeder(menuScoreboard, FEEDER_BLUETEAM_LIST, qtrue);
	}
}


static void CG_scrollScoresUp_f( void) {
	if (menuScoreboard && cg.scoreBoardShowing) {
		Menu_ScrollFeeder(menuScoreboard, FEEDER_SCOREBOARD, qfalse);
		Menu_ScrollFeeder(menuScoreboard, FEEDER_REDTEAM_LIST, qfalse);
		Menu_ScrollFeeder(menuScoreboard, FEEDER_BLUETEAM_LIST, qfalse);
	}
}


static void CG_spWin_f( void) {
	trap_Cvar_Set("cg_cameraOrbit", "2");
	trap_Cvar_Set("cg_cameraOrbitDelay", "35");
	trap_Cvar_Set("cg_thirdPerson", "1");
	trap_Cvar_Set("cg_thirdPersonAngle", "0");
	trap_Cvar_Set("cg_thirdPersonRange", "100");
	CG_ClearBufferedAnnouncements();
	CG_AddBufferedSound(cgs.media.winnerSound);
	//trap_S_StartLocalSound(cgs.media.winnerSound, CHAN_ANNOUNCER);
	CG_CenterPrint( "YOU WIN!", SCREEN_HEIGHT * .30f, 0.5f );
}

static void CG_spLose_f( void) {
	trap_Cvar_Set("cg_cameraOrbit", "2");
	trap_Cvar_Set("cg_cameraOrbitDelay", "35");
	trap_Cvar_Set("cg_thirdPerson", "1");
	trap_Cvar_Set("cg_thirdPersonAngle", "0");
	trap_Cvar_Set("cg_thirdPersonRange", "100");
	CG_ClearBufferedAnnouncements();
	CG_AddBufferedSound(cgs.media.loserSound);
	//trap_S_StartLocalSound(cgs.media.loserSound, CHAN_ANNOUNCER);
	CG_CenterPrint( "YOU LOSE...", SCREEN_HEIGHT * .30f, 0.5f );
}


static void CG_TellTarget_f( void ) {
	int		clientNum;
	char	command[128];
	char	message[128];

	clientNum = CG_CrosshairPlayer();
	if ( clientNum == -1 ) {
		return;
	}

	trap_Args( message, 128 );
	Com_sprintf( command, 128, "tell %i %s", clientNum, message );
	trap_SendClientCommand( command );
}

static void CG_TellAttacker_f( void ) {
	int		clientNum;
	char	command[128];
	char	message[128];

	clientNum = CG_LastAttacker();
	if ( clientNum == -1 ) {
		return;
	}

	trap_Args( message, 128 );
	Com_sprintf( command, 128, "tell %i %s", clientNum, message );
	trap_SendClientCommand( command );
}

static void CG_VoiceTellTarget_f( void ) {
	int		clientNum;
	char	command[128];
	char	message[128];

	clientNum = CG_CrosshairPlayer();
	if ( clientNum == -1 ) {
		return;
	}

	trap_Args( message, 128 );
	Com_sprintf( command, 128, "vtell %i %s", clientNum, message );
	trap_SendClientCommand( command );
}

static void CG_VoiceTellAttacker_f( void ) {
	int		clientNum;
	char	command[128];
	char	message[128];

	clientNum = CG_LastAttacker();
	if ( clientNum == -1 ) {
		return;
	}

	trap_Args( message, 128 );
	Com_sprintf( command, 128, "vtell %i %s", clientNum, message );
	trap_SendClientCommand( command );
}

static void CG_NextTeamMember_f( void ) {
  if (cg.snap && (cg.snap->ps.pm_flags & PMF_FOLLOW)) {
    CG_SpectatorFollowCycle(1);
  } else {
    CG_SelectNextPlayer();
  }
}


static void CG_PrevTeamMember_f( void ) {
  if (cg.snap && (cg.snap->ps.pm_flags & PMF_FOLLOW)) {
    CG_SpectatorFollowCycle(-1);
  } else {
    CG_SelectPrevPlayer();
  }
}

/*
=============
CG_ClientMute_f

Mirrors the retail identity-backed clientmute wrapper.
=============
*/
static void CG_ClientMute_f( void ) {
	char				arg[16];
	int					clientNum;
	const clientInfo_t	*ci;

	if ( trap_Argc() < 2 ) {
		return;
	}

	trap_Argv( 1, arg, sizeof( arg ) );
	clientNum = atoi( arg );
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return;
	}

	ci = &cgs.clientinfo[clientNum];
	if ( ( ci->identityLow | ci->identityHigh ) == 0 ) {
		return;
	}

	trap_QL_ToggleClientMute( ci->identityLow, ci->identityHigh );
}

/*
=============
CG_IsInstaGibMode

Returns qtrue when the retail dmflags bit that blocks dropweapon and droppowerup is set.
=============
*/
static qboolean CG_IsInstaGibMode( void ) {
	return ( cgs.dmflags & 0x20000 ) != 0;
}

/*
=============
CG_DropFlag_f

Mirrors the retail local dropflag gate and only forwards in flag-objective modes.
=============
*/
static void CG_DropFlag_f( void ) {
	if ( cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF &&
			cgs.gametype != GT_ATTACK_DEFEND ) {
		Com_Printf( "DropFlag is not available in non-flag gametypes.\n" );
		return;
	}

	trap_SendClientCommand( "dropflag" );
}

/*
=============
CG_DropPowerup_f

Mirrors the retail local droppowerup gate across team-mode, mode-specific, and InstaGib checks.
=============
*/
static void CG_DropPowerup_f( void ) {
	if ( cgs.gametype < GT_TEAM ) {
		Com_Printf( "DropPowerup is not available in non-team gametypes.\n" );
		return;
	}

	if ( cgs.gametype == GT_CLAN_ARENA || cgs.gametype == GT_DOMINATION ||
			cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_RED_ROVER ) {
		Com_Printf( "DropPowerup is not available in %s.\n", CG_GameTypeString() );
		return;
	}

	if ( CG_IsInstaGibMode() ) {
		Com_Printf( "DropPowerup is not available in InstaGib.\n" );
		return;
	}

	trap_SendClientCommand( "droppowerup" );
}

/*
=============
CG_DropRune_f

Mirrors the retail local droprune gate, which only blocks the Race slot.
=============
*/
static void CG_DropRune_f( void ) {
	if ( cgs.gametype == GT_RACE ) {
		Com_Printf( "DropRune not available in %s.\n", CG_GameTypeString() );
		return;
	}

	trap_SendClientCommand( "droprune" );
}

/*
=============
CG_DropWeapon_f

Mirrors the retail local dropweapon gate across team-mode, mode-specific, and InstaGib checks.
=============
*/
static void CG_DropWeapon_f( void ) {
	if ( cgs.gametype < GT_TEAM ) {
		Com_Printf( "DropWeapon is not available in non-team gametypes.\n" );
		return;
	}

	if ( cgs.gametype == GT_CLAN_ARENA || cgs.gametype == GT_DOMINATION ||
			cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_RED_ROVER ) {
		Com_Printf( "DropWeapon is not available in %s.\n", CG_GameTypeString() );
		return;
	}

	if ( CG_IsInstaGibMode() ) {
		Com_Printf( "DropWeapon is not available in InstaGib.\n" );
		return;
	}

	trap_SendClientCommand( "dropweapon" );
}

/*
=============
CG_Forfeit_f

Mirrors the retail local forfeit gate and only forwards in supported match types.
=============
*/
static void CG_Forfeit_f( void ) {
	if ( cgs.gametype == GT_FFA || cgs.gametype == GT_RACE ||
			cgs.gametype == GT_RED_ROVER ) {
		Com_Printf( "Forfeit is not available in %s.\n", CG_GameTypeString() );
		return;
	}

	trap_SendClientCommand( "forfeit" );
}

/*
=============
CG_RageQuit_f

Mirrors the retail ragequit wrapper and arms the existing client-side quit latch.
=============
*/
static void CG_RageQuit_f( void ) {
	trap_SendClientCommand( "ragequit" );
	cg.rageQuitTime = 2;
}

/*
=============
CG_Kill_f

Reconstructs the retail local kill command entry point.
=============
*/
static void CG_Kill_f( void ) {
	cg.killRespawnHintSuppressed = qtrue;
	trap_SendClientCommand( "kill" );
}

/*
=============
CG_GetRetailReadyUpPmType

Returns the player movement mode that the retail readyup wrapper uses for its
intermission bypass, falling back to the predicted state when no live snapshot
is available.
=============
*/
static pmtype_t CG_GetRetailReadyUpPmType( void ) {
	if ( cg.snap ) {
		return (pmtype_t)cg.snap->ps.pm_type;
	}

	return (pmtype_t)cg.predictedPlayerState.pm_type;
}

/*
=============
CG_IsRetailReadyUpIntermissionBypassActive

Returns qtrue when the retail intermission-only readyup bypass is active.
=============
*/
static qboolean CG_IsRetailReadyUpIntermissionBypassActive( void ) {
	return ( qboolean )( CG_GetRetailReadyUpPmType() == PM_INTERMISSION );
}

/*
=============
CG_ReadyUp_f

Mirrors the retail local readyup wrapper by requiring an active warmup window
and only bypassing the spectator gate during intermission.
=============
*/
static void CG_ReadyUp_f( void ) {
	const playerState_t	*ps;
	qboolean		allowIntermissionBypass;

	ps = cg.snap ? &cg.snap->ps : NULL;
	allowIntermissionBypass = CG_IsRetailReadyUpIntermissionBypassActive();

	if ( cg.warmup == 0 && cgs.matchReadyUpDeadline <= 0 && !allowIntermissionBypass ) {
		return;
	}

	if ( !ps ) {
		if ( !allowIntermissionBypass ) {
			return;
		}
	} else if ( ps->persistant[PERS_TEAM] == TEAM_SPECTATOR && !allowIntermissionBypass ) {
		return;
	}

	trap_SendClientCommand( "readyup" );
}

/*
=============
CG_ClearRetailCommandCaptureState

Closes the cgame-owned capture paths that the retail team wrapper dismisses after forwarding.
=============
*/
static void CG_ClearRetailCommandCaptureState( void ) {
	int catcher;

	if ( cgs.eventHandling == CGAME_EVENT_TEAMMENU ||
			cgs.eventHandling == CGAME_EVENT_EDITHUD ) {
		CG_EventHandling( CGAME_EVENT_NONE );
	}

	catcher = trap_Key_GetCatcher();
	if ( catcher & KEYCATCH_CGAME ) {
		trap_Key_SetCatcher( catcher & ~KEYCATCH_CGAME );
	}
}

/*
=============
CG_Team_f

Mirrors the retail local team wrapper by forwarding the team command and dismissing any cgame-owned capture state.
=============
*/
static void CG_Team_f( void ) {
	char	teamArg[128];
	char	command[160];

	trap_Argv( 1, teamArg, sizeof( teamArg ) );
	Com_sprintf( command, sizeof( command ), "team %s", teamArg );
	trap_SendClientCommand( command );
	CG_ClearRetailCommandCaptureState();
}

static const unsigned int cg_retailCommandColorPalette[26] = {
	0x800000ffu,
	0x802300ffu,
	0x804000ffu,
	0x805e00ffu,
	0x808000ffu,
	0x5e8000ffu,
	0x408000ffu,
	0x238000ffu,
	0x008000ffu,
	0x008023ffu,
	0x008040ffu,
	0x00805effu,
	0x008080ffu,
	0x005e80ffu,
	0x004080ffu,
	0x002380ffu,
	0x000080ffu,
	0x230080ffu,
	0x400080ffu,
	0x5e0080ffu,
	0x800080ffu,
	0x80005effu,
	0x800040ffu,
	0x800023ffu,
	0x808080ffu,
	0x404040ffu
};

/*
=============
CG_ColorCommandCharToPaletteIndex

Maps a retail color-command letter into the observed 26-entry palette, defaulting invalid input to the first slot.
=============
*/
static int CG_ColorCommandCharToPaletteIndex( char ch ) {
	ch = (char)tolower( (unsigned char)ch );
	if ( ch < 'a' || ch > 'z' ) {
		return 0;
	}
	return ch - 'a';
}

/*
=============
CG_FormatRetailCommandColor

Formats one retail command-palette entry as the lowercase RGBA hex string used by the color wrappers.
=============
*/
static void CG_FormatRetailCommandColor( char ch, char *buffer, int bufferSize ) {
	int index;

	index = CG_ColorCommandCharToPaletteIndex( ch );
	Com_sprintf( buffer, bufferSize, "0x%08x", cg_retailCommandColorPalette[index] );
}

/*
=============
CG_ApplyCommandColorString

Applies the retail upper/lower/head command ordering to the source-side team or enemy color cvars.
=============
*/
static void CG_ApplyCommandColorString( qboolean useTeam, const char *colorArg ) {
	char upperColor[16];
	char lowerColor[16];
	char headColor[16];
	char upperChar;
	char lowerChar;
	char headChar;
	int len;

	if ( !colorArg || !colorArg[0] ) {
		return;
	}

	len = strlen( colorArg );
	if ( len < 1 ) {
		return;
	}

	upperChar = colorArg[0];
	lowerChar = colorArg[( len > 1 ) ? 1 : ( len - 1 )];
	headChar = colorArg[( len > 2 ) ? 2 : ( len - 1 )];

	CG_FormatRetailCommandColor( headChar, headColor, sizeof( headColor ) );
	CG_FormatRetailCommandColor( upperChar, upperColor, sizeof( upperColor ) );
	CG_FormatRetailCommandColor( lowerChar, lowerColor, sizeof( lowerColor ) );

	trap_Cvar_Set( useTeam ? "cg_teamHeadColor" : "cg_enemyHeadColor", headColor );
	trap_Cvar_Set( useTeam ? "cg_teamUpperColor" : "cg_enemyUpperColor", upperColor );
	trap_Cvar_Set( useTeam ? "cg_teamLowerColor" : "cg_enemyLowerColor", lowerColor );
}

/*
=============
CG_SetColorCommand_f

Mirrors the retail team and enemy color wrappers using the observed 26-entry palette and upper/lower/head token ordering.
=============
*/
static void CG_SetColorCommand_f( qboolean useTeam ) {
	char colorArg[128];
	char currentColor[128];
	int len;

	trap_Argv( 1, colorArg, sizeof( colorArg ) );
	if ( !colorArg[0] ) {
		trap_Cvar_VariableStringBuffer( useTeam ? "cg_teamColors" : "cg_enemyColors",
			currentColor, sizeof( currentColor ) );
		Com_Printf( "Current %s color: %s\n", useTeam ? "team" : "enemy", currentColor );
		return;
	}

	len = strlen( colorArg );
	if ( len > 3 ) {
		colorArg[3] = '\0';
	}

	trap_Cvar_Set( useTeam ? "cg_teamColors" : "cg_enemyColors", colorArg );
	CG_ApplyCommandColorString( useTeam, colorArg );
}

/*
=============
CG_SetTeamColor_f

Mirrors the retail local team-color wrapper.
=============
*/
static void CG_SetTeamColor_f( void ) {
	CG_SetColorCommand_f( qtrue );
}

/*
=============
CG_SetEnemyColor_f

Mirrors the retail local enemy-color wrapper.
=============
*/
static void CG_SetEnemyColor_f( void ) {
	CG_SetColorCommand_f( qfalse );
}

/*
=============
CG_ChatDown_f

Raises the buffered chat-history latch used by the retail HUD ownerdraw path.
=============
*/
static void CG_ChatDown_f( void ) {
	cg.chatHistoryVisible = qtrue;
}

/*
=============
CG_ChatUp_f

Clears the buffered chat-history latch used by the retail HUD ownerdraw path.
=============
*/
static void CG_ChatUp_f( void ) {
	cg.chatHistoryVisible = qfalse;
}

/*
=============
CG_ToggleChatHistory_f

Toggles the buffered chat-history latch used by the retail HUD ownerdraw path.
=============
*/
static void CG_ToggleChatHistory_f( void ) {
	cg.chatHistoryVisible = (qboolean)!cg.chatHistoryVisible;
}

/*
=============
CG_Print_f

Joins the command arguments into one line and forwards them into the buffered chat ring.
=============
*/
static void CG_Print_f( void ) {
	char	buffer[MAX_STRING_CHARS];
	char	arg[MAX_STRING_CHARS];
	int		i;
	int		argc;

	buffer[0] = '\0';
	argc = trap_Argc();
	for ( i = 1; i < argc; i++ ) {
		trap_Argv( i, arg, sizeof( arg ) );
		if ( i > 1 ) {
			Q_strcat( buffer, sizeof( buffer ), " " );
		}
		Q_strcat( buffer, sizeof( buffer ), arg );
	}

	CG_PushPrintString( buffer, SYSTEM_PRINT, 0 );
}

/*
=============
CG_IsSpectatorInput

Returns qtrue when the local client is spectating or following another player.
=============
*/
static qboolean CG_IsSpectatorInput( void ) {
	if ( !cg.snap ) {
		return qfalse;
	}
	return ( ( cg.snap->ps.pm_flags & PMF_FOLLOW ) || cg.snap->ps.pm_type == PM_SPECTATOR ||
			cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR );
}

// ASS U ME's enumeration order as far as task specific orders, OFFENSE is zero, CAMP is last
// ASS U ME's enumeration order as far as task specific orders, OFFENSE is zero, CAMP is last
//
static void CG_NextOrder_f( void ) {
	if ( CG_IsSpectatorInput() ) {
		cgs.orderPending = qfalse;
		return;
	}
	clientInfo_t *ci = cgs.clientinfo + cg.snap->ps.clientNum;
	if (ci) {
		if (!ci->teamLeader && sortedTeamPlayers[cg_currentSelectedPlayer.integer] != cg.snap->ps.clientNum) {
			return;
		}
	}
	if (cgs.currentOrder < TEAMTASK_CAMP) {
		cgs.currentOrder++;

		if (cgs.currentOrder == TEAMTASK_RETRIEVE) {
			if (!CG_OtherTeamHasFlag()) {
				cgs.currentOrder++;
			}
		}

		if (cgs.currentOrder == TEAMTASK_ESCORT) {
			if (!CG_YourTeamHasFlag()) {
				cgs.currentOrder++;
			}
		}

	} else {
		cgs.currentOrder = TEAMTASK_OFFENSE;
	}
	cgs.orderPending = qtrue;
	cgs.orderTime = cg.time + 3000;
}



static void CG_ConfirmOrder_f (void ) {
	if ( CG_IsSpectatorInput() ) {
		return;
	}
	trap_SendConsoleCommand( va( "cmd vtell %d %s\n", cgs.acceptLeader, VOICECHAT_YES ) );
	trap_SendConsoleCommand("+button5; wait; -button5");
	if (cg.time < cgs.acceptOrderTime) {
		trap_SendClientCommand( va( "teamtask %d\n", cgs.acceptTask ) );
		cgs.acceptOrderTime = 0;
	}
}

static void CG_DenyOrder_f (void ) {
	if ( CG_IsSpectatorInput() ) {
		return;
	}
	trap_SendConsoleCommand( va( "cmd vtell %d %s\n", cgs.acceptLeader, VOICECHAT_NO ) );
	trap_SendConsoleCommand("+button6; wait; -button6");
	if (cg.time < cgs.acceptOrderTime) {
		cgs.acceptOrderTime = 0;
	}
}

static void CG_TaskOffense_f (void ) {
	if (cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF) {
		trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONGETFLAG));
	} else {
		trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONOFFENSE));
	}
	trap_SendClientCommand(va("teamtask %d\n", TEAMTASK_OFFENSE));
}

static void CG_TaskDefense_f (void ) {
	trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONDEFENSE));
	trap_SendClientCommand(va("teamtask %d\n", TEAMTASK_DEFENSE));
}

static void CG_TaskPatrol_f (void ) {
	trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONPATROL));
	trap_SendClientCommand(va("teamtask %d\n", TEAMTASK_PATROL));
}

static void CG_TaskCamp_f (void ) {
	trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONCAMPING));
	trap_SendClientCommand(va("teamtask %d\n", TEAMTASK_CAMP));
}

static void CG_TaskFollow_f (void ) {
	trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONFOLLOW));
	trap_SendClientCommand(va("teamtask %d\n", TEAMTASK_FOLLOW));
}

static void CG_TaskRetrieve_f (void ) {
	trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONRETURNFLAG));
	trap_SendClientCommand(va("teamtask %d\n", TEAMTASK_RETRIEVE));
}

static void CG_TaskEscort_f (void ) {
	trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_ONFOLLOWCARRIER));
	trap_SendClientCommand(va("teamtask %d\n", TEAMTASK_ESCORT));
}

static void CG_TaskOwnFlag_f (void ) {
	trap_SendConsoleCommand(va("cmd vsay_team %s\n", VOICECHAT_IHAVEFLAG));
}

static void CG_TauntKillInsult_f (void ) {
	trap_SendConsoleCommand("cmd vsay kill_insult\n");
}

static void CG_TauntPraise_f (void ) {
	trap_SendConsoleCommand("cmd vsay praise\n");
}

static void CG_TauntTaunt_f (void ) {
	trap_SendConsoleCommand("cmd vtaunt\n");
}

static void CG_TauntDeathInsult_f (void ) {
	trap_SendConsoleCommand("cmd vsay death_insult\n");
}

static void CG_TauntGauntlet_f (void ) {
	trap_SendConsoleCommand("cmd vsay kill_gauntlet\n");
}

static void CG_TaskSuicide_f (void ) {
	int		clientNum;
	char	command[128];

	clientNum = CG_CrosshairPlayer();
	if ( clientNum == -1 ) {
		return;
	}

	Com_sprintf( command, 128, "tell %i suicide", clientNum );
	trap_SendClientCommand( command );
}



/*
==================
CG_TeamMenu_f
==================
*/
/*
static void CG_TeamMenu_f( void ) {
  if (trap_Key_GetCatcher() & KEYCATCH_CGAME) {
    CG_EventHandling(CGAME_EVENT_NONE);
    trap_Key_SetCatcher(0);
  } else {
    CG_EventHandling(CGAME_EVENT_TEAMMENU);
    //trap_Key_SetCatcher(KEYCATCH_CGAME);
  }
}
*/

/*
==================
CG_EditHud_f
==================
*/
/*
static void CG_EditHud_f( void ) {
  //cls.keyCatchers ^= KEYCATCH_CGAME;
  //VM_Call (cgvm, CG_EVENT_HANDLING, (cls.keyCatchers & KEYCATCH_CGAME) ? CGAME_EVENT_EDITHUD : CGAME_EVENT_NONE);
}
*/


/*
==================
CG_StartOrbit_f
==================
*/

static void CG_StartOrbit_f( void ) {
	char var[MAX_TOKEN_CHARS];

	trap_Cvar_VariableStringBuffer( "developer", var, sizeof( var ) );
	if ( !atoi(var) ) {
		return;
	}
	if (cg_cameraOrbit.value != 0) {
		trap_Cvar_Set ("cg_cameraOrbit", "0");
		trap_Cvar_Set("cg_thirdPerson", "0");
	} else {
		trap_Cvar_Set("cg_cameraOrbit", "5");
		trap_Cvar_Set("cg_thirdPerson", "1");
		trap_Cvar_Set("cg_thirdPersonAngle", "0");
		trap_Cvar_Set("cg_thirdPersonRange", "100");
	}
}

/*
static void CG_Camera_f( void ) {
	char name[1024];
	trap_Argv( 1, name, sizeof(name));
	if (trap_loadCamera(name)) {
		cg.cameraMode = qtrue;
		trap_startCamera(cg.time);
	} else {
		CG_Printf ("Unable to load camera %s\n",name);
	}
}
*/


typedef struct {
	char	*cmd;
	void	(*function)(void);
} consoleCommand_t;

static consoleCommand_t	commands[] = {
	{ "viewpos", CG_Viewpos_f },
	{ "+scores", CG_ScoresDown_f },
	{ "-scores", CG_ScoresUp_f },
	{ "+acc", CG_AccDown_f },
	{ "-acc", CG_AccUp_f },
	{ "+pstats", CG_PStatsDown_f },
	{ "-pstats", CG_PStatsUp_f },
	{ "+zoom", CG_ZoomDown_f },
	{ "-zoom", CG_ZoomUp_f },
	{ "sizeup", CG_SizeUp_f },
	{ "sizedown", CG_SizeDown_f },
	{ "weapnext", CG_NextWeapon_f },
	{ "weapprev", CG_PrevWeapon_f },
	{ "weapon", CG_Weapon_f },
	{ "tell_target", CG_TellTarget_f },
	{ "tell_attacker", CG_TellAttacker_f },
	{ "vtell_target", CG_VoiceTellTarget_f },
	{ "vtell_attacker", CG_VoiceTellAttacker_f },
	{ "tcmd", CG_TargetCommand_f },
	{ "loadhud", CG_LoadHud_f },
	{ "nextTeamMember", CG_NextTeamMember_f },
	{ "prevTeamMember", CG_PrevTeamMember_f },
	{ "nextOrder", CG_NextOrder_f },
	{ "confirmOrder", CG_ConfirmOrder_f },
	{ "denyOrder", CG_DenyOrder_f },
	{ "taskOffense", CG_TaskOffense_f },
	{ "taskDefense", CG_TaskDefense_f },
	{ "taskPatrol", CG_TaskPatrol_f },
	{ "taskCamp", CG_TaskCamp_f },
	{ "taskFollow", CG_TaskFollow_f },
	{ "taskRetrieve", CG_TaskRetrieve_f },
	{ "taskEscort", CG_TaskEscort_f },
	{ "taskSuicide", CG_TaskSuicide_f },
	{ "taskOwnFlag", CG_TaskOwnFlag_f },
	{ "tauntKillInsult", CG_TauntKillInsult_f },
	{ "tauntPraise", CG_TauntPraise_f },
	{ "tauntTaunt", CG_TauntTaunt_f },
	{ "tauntDeathInsult", CG_TauntDeathInsult_f },
	{ "tauntGauntlet", CG_TauntGauntlet_f },
	{ "startOrbit", CG_StartOrbit_f },
	{ "loaddeferred", CG_LoadDeferredPlayers },
	{ "dropflag", CG_DropFlag_f },
	{ "droppowerup", CG_DropPowerup_f },
	{ "droprune", CG_DropRune_f },
	{ "dropweapon", CG_DropWeapon_f },
	{ "+chat", CG_ChatDown_f },
	{ "-chat", CG_ChatUp_f },
	{ "readyup", CG_ReadyUp_f },
	{ "team", CG_Team_f },
	{ "togglechathistory", CG_ToggleChatHistory_f },
	{ "forfeit", CG_Forfeit_f },
	{ "ragequit", CG_RageQuit_f },
	{ "setteamcolor", CG_SetTeamColor_f },
	{ "setenemycolor", CG_SetEnemyColor_f },
	{ "print", CG_Print_f },
	{ "kill", CG_Kill_f },
	{ "clientmute", CG_ClientMute_f }
};

static consoleCommand_t compatCommands[] = {
	{ "testgun", CG_TestGun_f },
	{ "testmodel", CG_TestModel_f },
	{ "nextframe", CG_TestModelNextFrame_f },
	{ "prevframe", CG_TestModelPrevFrame_f },
	{ "nextskin", CG_TestModelNextSkin_f },
	{ "prevskin", CG_TestModelPrevSkin_f },
	{ "spWin", CG_spWin_f },
	{ "spLose", CG_spLose_f },
	{ "scoresDown", CG_scrollScoresDown_f },
	{ "scoresUp", CG_scrollScoresUp_f }
};


/*
=================
CG_ConsoleCommand

The string has been tokenized and can be retrieved with
Cmd_Argc() / Cmd_Argv()
=================
*/
qboolean CG_ConsoleCommand( void ) {
	const char	*cmd;
	int		i;

	cmd = CG_Argv(0);

	for ( i = 0 ; i < ARRAY_LEN( commands ) ; i++ ) {
		if ( !Q_stricmp( cmd, commands[i].cmd ) ) {
			commands[i].function();
			return qtrue;
		}
	}

	for ( i = 0 ; i < ARRAY_LEN( compatCommands ) ; i++ ) {
		if ( !Q_stricmp( cmd, compatCommands[i].cmd ) ) {
			compatCommands[i].function();
			return qtrue;
		}
	}

	return qfalse;
}


/*
=================
CG_InitConsoleCommands

Let the client system know about all of our commands
so it can perform tab completion
=================
*/
void CG_InitConsoleCommands( void ) {
	int		i;

	for ( i = 0 ; i < ARRAY_LEN( commands ) ; i++ ) {
		trap_AddCommand( commands[i].cmd );
	}

	//
	// the game server will interpret these commands, which will be automatically
	// forwarded to the server after they are not recognized locally
	//
	trap_AddCommand ("abort");
	trap_AddCommand ("addadmin");
	trap_AddCommand ("addbot");
	trap_AddCommand ("addmod");
	trap_AddCommand ("addscore");
	trap_AddCommand ("addteamscore");
	trap_AddCommand ("allready");
	trap_AddCommand ("ban");
	trap_AddCommand ("callvote");
	trap_AddCommand ("demote");
	trap_AddCommand ("dropflag");
	trap_AddCommand ("droppowerup");
	trap_AddCommand ("droprune");
	trap_AddCommand ("dropweapon");
	trap_AddCommand ("follow");
	trap_AddCommand ("forfeit");
	trap_AddCommand ("give");
	trap_AddCommand ("god");
	trap_AddCommand ("kill");
	trap_AddCommand ("levelshot");
	trap_AddCommand ("listaccess");
	trap_AddCommand ("loaddeferred");
	trap_AddCommand ("lock");
	trap_AddCommand ("mute");
	trap_AddCommand ("notarget");
	trap_AddCommand ("noclip");
	trap_AddCommand ("opsay");
	trap_AddCommand ("pause");
	trap_AddCommand ("players");
	trap_AddCommand ("put");
	trap_AddCommand ("ragequit");
	trap_AddCommand ("rcon");
	trap_AddCommand ("reload_access");
	trap_AddCommand ("say");
	trap_AddCommand ("say_team");
	trap_AddCommand ("setmatchtime");
	trap_AddCommand ("setviewpos");
	trap_AddCommand ("spec");
	trap_AddCommand ("team");
	trap_AddCommand ("tell");
	trap_AddCommand ("tempban");
	trap_AddCommand ("timein");
	trap_AddCommand ("timeout");
	trap_AddCommand ("unban");
	trap_AddCommand ("unlock");
	trap_AddCommand ("unmute");
	trap_AddCommand ("unpause");
	trap_AddCommand ("vote");
}
