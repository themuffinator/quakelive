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
// cg_screen.c -- handle screen feedback events

#include "cg_local.h"

static qhandle_t	cg_screenDamageBlendShader;
static qboolean		cg_joinGameMenuCaptureActive;

/*
================
CG_OpenJoinGameMenu

Ensures the shared retail `joingame_menu` root is visible and interactive.
================
*/
static menuDef_t *CG_OpenJoinGameMenu( void ) {
	menuDef_t	*menu;
	int		catcher;

	menu = CG_FindBrowserOverlayByName( "joingame_menu" );
	if ( !menu ) {
		return NULL;
	}

	if ( !( menu->window.flags & WINDOW_VISIBLE ) ) {
		catcher = trap_Key_GetCatcher();
		if ( !( catcher & KEYCATCH_CGAME ) ) {
			trap_Key_SetCatcher( catcher | KEYCATCH_CGAME );
		}
		menu = CG_OpenBrowserOverlayByName( "joingame_menu" );
	}

	return menu;
}

/*
================
CG_GetScreenDamageBlendShader

Lazily resolves the retail no-blood damage blend shader.
================
*/
static qhandle_t CG_GetScreenDamageBlendShader( void ) {
	if ( !cg_screenDamageBlendShader ) {
		cg_screenDamageBlendShader = trap_R_RegisterShader( "viewDamageBlend" );
	}

	return cg_screenDamageBlendShader;
}

/*
================
CG_GetScreenDamageColor

Selects the retail screen-damage tint variant for the current attacker.
================
*/
static qboolean CG_GetScreenDamageColor( vec4_t color, float *alphaScale ) {
	int				attackerClientNum;
	team_t			playerTeam;
	clientInfo_t	*attackerInfo;

	Vector4Copy( cg.screenDamageColor, color );
	*alphaScale = cg.screenDamageAlpha;

	if ( !cg.snap ) {
		return qfalse;
	}

	attackerClientNum = cg.snap->ps.persistant[PERS_ATTACKER];
	if ( attackerClientNum == cg.snap->ps.clientNum ) {
		Vector4Copy( cg.screenDamageSelfColor, color );
		return qtrue;
	}

	if ( cgs.gametype < GT_TEAM ) {
		return qfalse;
	}

	playerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	if ( playerTeam != TEAM_RED && playerTeam != TEAM_BLUE ) {
		return qfalse;
	}

	if ( attackerClientNum < 0 || attackerClientNum >= cgs.maxclients ) {
		return qfalse;
	}

	attackerInfo = &cgs.clientinfo[attackerClientNum];
	if ( !attackerInfo->infoValid || attackerInfo->team != playerTeam ) {
		return qfalse;
	}

	Vector4Copy( cg.screenDamageTeamColor, color );
	*alphaScale = cg.screenDamageAlphaTeam;
	return qfalse;
}

/*
================
CG_SetScreenDamageEntityColor

Applies the retail screen-damage tint to a sprite entity.
================
*/
static void CG_SetScreenDamageEntityColor( refEntity_t *ent, const vec4_t color, float alphaScale, float fade, qboolean useColorAlpha ) {
	float	alphaByte;

	ent->shaderRGBA[0] = (byte)( Com_Clamp( 0.0f, 1.0f, color[0] ) * 255.0f );
	ent->shaderRGBA[1] = (byte)( Com_Clamp( 0.0f, 1.0f, color[1] ) * 255.0f );
	ent->shaderRGBA[2] = (byte)( Com_Clamp( 0.0f, 1.0f, color[2] ) * 255.0f );

	if ( useColorAlpha ) {
		alphaByte = Com_Clamp( 0.0f, 1.0f, color[3] ) * 255.0f;
	} else {
		alphaByte = Com_Clamp( 0.0f, 255.0f, alphaScale );
	}

	ent->shaderRGBA[3] = (byte)Com_Clamp( 0.0f, 255.0f, alphaByte * fade );
}

/*
================
CG_DamageBlendBlob

First person view damage feedback (red blob)
================
*/
void CG_DamageBlendBlob( void ) {
	int			t;
	int			maxTime;
	float		fade;
	float		alphaScale;
	qboolean	useColorAlpha;
	vec4_t		color;
	refEntity_t		ent;

	if ( !cg.damageValue ) {
		return;
	}

	// rage pro systems can't fade blends, so don't obscure the screen
	if ( cgs.glconfig.hardwareType == GLHW_RAGEPRO ) {
		return;
	}

	maxTime = DAMAGE_TIME;
	t = cg.time - cg.damageTime;
	if ( t <= 0 || t >= maxTime ) {
		return;
	}

	fade = 1.0f - (float)t / maxTime;

	memset( &ent, 0, sizeof( ent ) );
	ent.reType = RT_SPRITE;
	ent.renderfx = RF_FIRST_PERSON;

	VectorMA( cg.refdef.vieworg, 8, cg.refdef.viewaxis[0], ent.origin );
	VectorMA( ent.origin, cg.damageX * -8, cg.refdef.viewaxis[1], ent.origin );
	VectorMA( ent.origin, cg.damageY * 8, cg.refdef.viewaxis[2], ent.origin );

	ent.radius = cg.damageValue * 2.0f;

	useColorAlpha = CG_GetScreenDamageColor( color, &alphaScale );
	CG_SetScreenDamageEntityColor( &ent, color, alphaScale, fade, useColorAlpha );

	if ( cgs.media.viewBloodShader ) {
		ent.customShader = cgs.media.viewBloodShader;
	} else {
		ent.customShader = CG_GetScreenDamageBlendShader();
	}
	trap_R_AddRefEntityToScene( &ent );
}

/*
================
CG_IsJoinGameMenuCaptureActive

Returns whether the retail spectator join-game capture latch is still armed.
================
*/
qboolean CG_IsJoinGameMenuCaptureActive( void ) {
	return cg_joinGameMenuCaptureActive;
}

/*
================
CG_ResetJoinGameMenuCaptureState

Re-arms the retail spectator join-game capture latch during cgame resets.
================
*/
void CG_ResetJoinGameMenuCaptureState( void ) {
	cg_joinGameMenuCaptureActive = qtrue;
}

/*
================
CG_ClearJoinGameMenuCaptureState

Drops the retail spectator join-game capture latch after the overlay closes.
================
*/
static void CG_ClearJoinGameMenuCaptureState( void ) {
	cg_joinGameMenuCaptureActive = qfalse;
}

/*
================
CG_ShouldDrawJoinGameMenu

Returns qtrue when the retail spectator-only `joingame_menu` overlay should
be painted through the old screen-damage slot.
================
*/
static qboolean CG_ShouldDrawJoinGameMenu( void ) {
	if ( !cg.snap ) {
		return qfalse;
	}

	if ( !CG_IsJoinGameMenuCaptureActive() ) {
		return qfalse;
	}

	if ( cg.scoreBoardShowing ) {
		return qfalse;
	}

	return ( qboolean )( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR );
}

/*
================
CG_CloseJoinGameMenu

Closes the retail spectator-only `joingame_menu` root and clears its capture
latch.
================
*/
void CG_CloseJoinGameMenu( void ) {
	int		catcher;

	CG_CloseBrowserOverlayByName( "joingame_menu" );

	CG_ClearJoinGameMenuCaptureState();
	cgs.capturedItem = NULL;
	cgs.activeCursor = 0;

	catcher = trap_Key_GetCatcher();
	if ( catcher & KEYCATCH_CGAME ) {
		trap_Key_SetCatcher( catcher & ~KEYCATCH_CGAME );
	}
}

/*
================
CG_DrawPregameJoinGameMenu

Paints the retail intro/placement overlay through the shared `joingame_menu`
root during SP intermission.
================
*/
void CG_DrawPregameJoinGameMenu( void ) {
	menuDef_t	*menu;

	menu = CG_OpenJoinGameMenu();
	if ( !menu ) {
		return;
	}

	menu->window.flags &= ~WINDOW_FORCED;
	CG_DrawBrowserOverlayTree( menu, qtrue );
}

/*
================
CG_DrawJoinGameMenu

Paints the retail spectator-only `joingame_menu` root and dismisses its
capture state once the local client stops spectating.
================
*/
void CG_DrawJoinGameMenu( void ) {
	menuDef_t	*menu;

	if ( !CG_ShouldDrawJoinGameMenu() ) {
		CG_CloseJoinGameMenu();
		return;
	}

	menu = CG_OpenJoinGameMenu();
	if ( !menu ) {
		return;
	}

	menu->window.flags &= ~WINDOW_FORCED;
	CG_DrawBrowserOverlayTree( menu, qtrue );
}
