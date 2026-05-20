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
// cg_draw.c -- draw all of the graphical elements during
// active (after loading) gameplay

#include "cg_local.h"

#include "../ui/ui_shared.h"

// used for scoreboard
extern displayContextDef_t cgDC;
extern menuDef_t Menus[MAX_MENUS];
menuDef_t *menuScoreboard = NULL;
menuDef_t *menuStats = NULL;
static menuDef_t	*cgSpectatorMenu;
static menuDef_t	*cgSpectatorFollowMenu;
static menuDef_t	*cgSpectatorRedTopMenu;
static menuDef_t	*cgSpectatorRedBottomMenu;
static menuDef_t	*cgSpectatorBlueTopMenu;
static menuDef_t	*cgSpectatorBlueBottomMenu;

int sortedTeamPlayers[TEAM_MAXOVERLAY];
int	numSortedTeamPlayers;

char systemChat[256];
char teamChat1[256];
char teamChat2[256];

#define CG_SPEEDOMETER_HISTORY_SAMPLES	128
#define CG_SPEEDOMETER_RANGE			960.0f

static float	cg_speedometerHistory[CG_SPEEDOMETER_HISTORY_SAMPLES];
static int	cg_speedometerHistoryCount;
static int	cg_speedometerHistoryHead = -1;
static int	cg_speedometerHistoryTime;
static float	cg_spectatorItemPickupBaseY;
static int	cg_drawActiveMilliseconds;

static float CG_DrawSnapshot( float y );
static void CG_DrawCrosshair( void );
static void CG_DrawCrosshairNames( void );
static const char *CG_GetBindKeyName( const char *cmd, char *buf, int len );


/*
=============
CG_ShouldDrawSpriteSelf

Helper predicate so sprite rendering can consult cg_drawSpriteSelf.
=============
*/
qboolean CG_ShouldDrawSpriteSelf( void ) {
	return ( qboolean )( cg_drawSpriteSelf.integer != 0 );
}

/*
=============
CG_ShouldDrawTieredArmor

Determines if tiered armor prompts should render.
=============
*/
qboolean CG_ShouldDrawTieredArmor( void ) {
	return ( qboolean )( cg_drawTieredArmorAvailability.integer != 0 );
}

/*
=============
CG_ShouldDrawSpeedometer

Decides whether the HUD speedometer should be visible.
=============
*/
qboolean CG_ShouldDrawSpeedometer( void ) {
	return ( qboolean )( cg_speedometer.integer != 0 );
}

/*
=============
CG_SampleLegacySpeedometer

Samples the current horizontal movement speed for the classic HUD renderer.
=============
*/
static float CG_SampleLegacySpeedometer( void ) {
	vec3_t	horizontalVelocity;

	if ( !cg.snap ) {
		return 0.0f;
	}

	VectorCopy( cg.snap->ps.velocity, horizontalVelocity );
	horizontalVelocity[2] = 0.0f;
	return VectorLength( horizontalVelocity );
}

/*
=============
CG_RecordSpeedometerSample

Maintains the retail-style 128-sample history ring used by the classic HUD
speedometer graph.
=============
*/
static void CG_RecordSpeedometerSample( void ) {
	if ( !cg.snap ) {
		cg_speedometerHistoryCount = 0;
		cg_speedometerHistoryHead = -1;
		cg_speedometerHistoryTime = cg.time;
		return;
	}

	if ( cg_speedometerHistoryTime == cg.time ) {
		return;
	}

	if ( cg_speedometerHistoryTime > cg.time ) {
		cg_speedometerHistoryCount = 0;
		cg_speedometerHistoryHead = -1;
	}

	cg_speedometerHistoryHead = ( cg_speedometerHistoryHead + 1 ) & ( CG_SPEEDOMETER_HISTORY_SAMPLES - 1 );
	cg_speedometerHistory[cg_speedometerHistoryHead] = CG_SampleLegacySpeedometer();
	if ( cg_speedometerHistoryCount < CG_SPEEDOMETER_HISTORY_SAMPLES ) {
		cg_speedometerHistoryCount++;
	}
	cg_speedometerHistoryTime = cg.time;
}

/*
=============
CG_RegisterInputCmdShaders

Ensures the retail race command-arrow icons used by the classic HUD are cached
in the shared cgame media table.
=============
*/
static void CG_RegisterInputCmdShaders( void ) {
	if ( !cgs.media.raceCommandUpShader ) {
		cgs.media.raceCommandUpShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_up" );
	}
	if ( !cgs.media.raceCommandDownShader ) {
		cgs.media.raceCommandDownShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_down" );
	}
	if ( !cgs.media.raceCommandRightShader ) {
		cgs.media.raceCommandRightShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_right" );
	}
	if ( !cgs.media.raceCommandLeftShader ) {
		cgs.media.raceCommandLeftShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_left" );
	}
}

/*
=============
CG_DrawInputCmds

Restores the retail classic-HUD command arrow slab, using live usercmd bytes
for the local player and mirrored playerstate bytes for follow/demo playback.
=============
*/
static void CG_DrawInputCmds( void ) {
	usercmd_t	cmd;
	float		x;
	float		y;
	float		size;
	int		cmdNum;
	int		forwardMove;
	int		rightMove;
	int		upMove;
	qhandle_t	upShader;
	qhandle_t	downShader;
	qhandle_t	rightShader;
	qhandle_t	leftShader;

	if ( !cg.snap || cg_drawInputCmds.integer == 0 ) {
		return;
	}

	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return;
	}

	if ( cg.snap->ps.pm_type == PM_SPECTATOR && !( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		return;
	}

	if ( cg_drawInputCmds.integer == 2 && !( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		return;
	}

	if ( ( cg.snap->ps.pm_flags & PMF_FOLLOW ) || cg.demoPlayback ) {
		forwardMove = cg.snap->ps.forwardmove;
		rightMove = cg.snap->ps.rightmove;
		upMove = cg.snap->ps.upmove;
	} else {
		cmdNum = trap_GetCurrentCmdNumber();
		if ( !trap_GetUserCmd( cmdNum, &cmd ) ) {
			return;
		}

		forwardMove = cmd.forwardmove;
		rightMove = cmd.rightmove;
		upMove = cmd.upmove;
	}

	CG_RegisterInputCmdShaders();
	upShader = cgs.media.raceCommandUpShader;
	downShader = cgs.media.raceCommandDownShader;
	rightShader = cgs.media.raceCommandRightShader;
	leftShader = cgs.media.raceCommandLeftShader;
	if ( !upShader || !downShader || !rightShader || !leftShader ) {
		return;
	}

	x = cg_drawInputCmdsX.value;
	y = cg_drawInputCmdsY.value;
	size = cg_drawInputCmdsSize.value;

	if ( forwardMove > 0 ) {
		CG_DrawPic( x - 8.0f, y - size - 16.0f, 16.0f, 16.0f, upShader );
	}
	if ( forwardMove < 0 ) {
		CG_DrawPic( x - 8.0f, y + size, 16.0f, 16.0f, downShader );
	}
	if ( rightMove > 0 ) {
		CG_DrawPic( x + size, y - 8.0f, 16.0f, 16.0f, rightShader );
	}
	if ( rightMove < 0 ) {
		CG_DrawPic( x - size - 16.0f, y - 8.0f, 16.0f, 16.0f, leftShader );
	}
	if ( upMove > 0 ) {
		CG_DrawPic( x + size + 16.0f, y - size - 16.0f, 16.0f, 16.0f, upShader );
	}
	if ( upMove < 0 ) {
		CG_DrawPic( x + size + 16.0f, y + size, 16.0f, 16.0f, downShader );
	}
}

/*
=============
CG_IsMenuHudActive

Reports if the Quake Live HUD menus should be drawn.
=============
*/
static qboolean CG_IsMenuHudActive( void ) {
	return cg.hudMenusLoaded;
}

/*
=============
CG_FloatFromBits
=============
*/
static float CG_FloatFromBits( unsigned int value ) {
	float result;

	*(unsigned int *)&result = value;
	return result;
}

/*
=============
CG_UnpackFloatBits64
=============
*/
static void CG_UnpackFloatBits64( unsigned long long packed, float *lo, float *hi ) {
	if ( lo ) {
		*lo = CG_FloatFromBits( (unsigned int)( packed & 0xffffffffULL ) );
	}
	if ( hi ) {
		*hi = CG_FloatFromBits( (unsigned int)( packed >> 32 ) );
	}
}

/*
=============
CG_SelectTextFontHandle

Maps the retail per-item font bucket onto the renderer host-text face table.
=============
*/
int CG_SelectTextFontHandle( float scale, int fontIndex ) {
	if ( fontIndex != ITEM_FONT_INHERIT ) {
		switch ( fontIndex ) {
			case FONT_SANS:
				return FONT_SANS;

			case FONT_MONO:
				return FONT_MONO;

			case FONT_DEFAULT:
			default:
				return FONT_DEFAULT;
		}
	}

	if ( scale <= cg_smallFont.value ) {
		return FONT_SANS;
	}

	return FONT_DEFAULT;
}

/*
=============
CG_GetTextLimitEnd

Returns the byte position after the requested number of visible characters.
=============
*/
static const char *CG_GetTextLimitEnd( const char *text, int limit ) {
	const char *s;
	int visibleCount;

	if ( text == NULL ) {
		return NULL;
	}

	if ( limit <= 0 ) {
		return text + strlen( text );
	}

	visibleCount = 0;
	for ( s = text; *s; ) {
		if ( Q_IsColorString( s ) ) {
			s += 2;
			continue;
		}

		if ( visibleCount >= limit ) {
			break;
		}

		s++;
		visibleCount++;
	}

	return s;
}

/*
=============
CG_CopyTextSpan

Copies a byte span so host text rendering can honor retail visible-character
limits.
=============
*/
static void CG_CopyTextSpan( const char *text, const char *end, char *buffer, int bufferSize ) {
	int copyLength;

	if ( buffer == NULL || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( text == NULL ) {
		return;
	}

	if ( end == NULL || end < text ) {
		end = text + strlen( text );
	}

	copyLength = (int)( end - text );
	if ( copyLength >= bufferSize ) {
		copyLength = bufferSize - 1;
	}

	if ( copyLength > 0 ) {
		memcpy( buffer, text, copyLength );
	}
	buffer[copyLength] = '\0';
}

/*
=============
CG_GetHostTextMetrics

Measures retail host text in screen space, then converts the result back into
virtual 640-space bounds for caller-side layout.
=============
*/
static void CG_GetHostTextMetrics( const char *text, float scale, int limit, int fontIndex, int *outWidth, int *outHeight ) {
	const char *limitEnd;
	unsigned long long packed;
	float width;
	float height;
	float xScale;
	float yScale;

	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}

	if ( text == NULL || text[0] == '\0' ) {
		return;
	}

	xScale = 1.0f;
	yScale = 1.0f;
	CG_AdjustFrom640( NULL, NULL, &xScale, &yScale );
	limitEnd = CG_GetTextLimitEnd( text, limit );
	packed = trap_QL_MeasureText(
		text,
		limitEnd,
		CG_SelectTextFontHandle( scale, fontIndex ),
		scale * QL_FONT_HOST_POINT_SIZE * yScale,
		0,
		NULL );
	CG_UnpackFloatBits64( packed, &width, &height );

	if ( outWidth && yScale > 0.0f ) {
		*outWidth = (int)( width / yScale );
	}
	if ( outHeight && yScale > 0.0f ) {
		*outHeight = (int)( height / yScale );
	}
}

/*
=============
CG_DrawHostTextSpan

Projects 640-space HUD coordinates into screen space and routes through the
renderer-owned host text painter that retail cgame uses.
=============
*/
static void CG_DrawHostTextSpan( float x, float y, float scale, const vec4_t color, const char *text, int fontIndex, int style, qboolean forceColor ) {
	float screenX;
	float screenY;
	float hostScale;
	float yScale;
	int fontHandle;

	if ( text == NULL || text[0] == '\0' ) {
		return;
	}

	screenX = x;
	screenY = y;
	yScale = 1.0f;
	CG_AdjustFrom640( &screenX, &screenY, NULL, &yScale );
	hostScale = scale * QL_FONT_HOST_POINT_SIZE * yScale;
	fontHandle = CG_SelectTextFontHandle( scale, fontIndex );

	if ( style == ITEM_TEXTSTYLE_SHADOWED || style == ITEM_TEXTSTYLE_SHADOWEDMORE ) {
		float shadowOffset;
		float shadowX;
		float shadowY;

		shadowOffset = ( style == ITEM_TEXTSTYLE_SHADOWED ) ? 1.0f : 2.0f;
		shadowX = x + shadowOffset;
		shadowY = y + shadowOffset;
		CG_AdjustFrom640( &shadowX, &shadowY, NULL, NULL );
		colorBlack[3] = color[3];
		trap_R_SetColor( colorBlack );
		trap_QL_DrawScaledText( (int)shadowX, (int)shadowY, text, fontHandle, hostScale, 0, NULL, qtrue );
		colorBlack[3] = 1.0f;
	}

	trap_R_SetColor( color );
	trap_QL_DrawScaledText( (int)screenX, (int)screenY, text, fontHandle, hostScale, 0, NULL, forceColor );
	trap_R_SetColor( NULL );
}

/*
=============
CG_Text_WidthExt

Measures retail host text with an explicit cgame font bucket override.
=============
*/
int CG_Text_WidthExt( const char *text, float scale, int limit, int fontIndex ) {
	int width;

	CG_GetHostTextMetrics( text, scale, limit, fontIndex, &width, NULL );
	return width;
}

/*
=============
CG_Text_Width
=============
*/
int CG_Text_Width(const char *text, float scale, int limit) {
	return CG_Text_WidthExt( text, scale, limit, ITEM_FONT_INHERIT );
}

/*
=============
CG_Text_HeightExt

Measures retail host text height with an explicit cgame font bucket override.
=============
*/
int CG_Text_HeightExt( const char *text, float scale, int limit, int fontIndex ) {
	int height;

	CG_GetHostTextMetrics( text, scale, limit, fontIndex, NULL, &height );
	return height;
}

/*
=============
CG_Text_Height
=============
*/
int CG_Text_Height(const char *text, float scale, int limit) {
	return CG_Text_HeightExt( text, scale, limit, ITEM_FONT_INHERIT );
}

/*
=============
CG_Text_GetExtents

Measures the rendered text bounds through the shared width and height helpers.
=============
*/
static void CG_Text_GetExtents( const char *text, float scale, int limit, int style, int *outWidth, int *outHeight ) {
	(void)style;

	CG_GetHostTextMetrics( text, scale, limit, ITEM_FONT_INHERIT, outWidth, outHeight );
}

void CG_Text_PaintChar(float x, float y, float width, float height, float scale, float s, float t, float s2, float t2, qhandle_t hShader) {
  float w, h;
  w = width * scale;
  h = height * scale;
  CG_AdjustFrom640( &x, &y, &w, &h );
  trap_R_DrawStretchPic( x, y, w, h, s, t, s2, t2, hShader );
}

/*
=============
CG_Text_PaintExt

Routes cgame text painting through the retail host-text lane with an explicit
font bucket override.
=============
*/
void CG_Text_PaintExt( float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style, int fontIndex ) {
	char limitedText[1024];
	const char *drawText;
	const char *limitEnd;

	(void)adjust;

	if ( text == NULL || text[0] == '\0' ) {
		return;
	}

	limitEnd = CG_GetTextLimitEnd( text, limit );
	if ( *limitEnd == '\0' ) {
		drawText = text;
	} else {
		CG_CopyTextSpan( text, limitEnd, limitedText, sizeof( limitedText ) );
		drawText = limitedText;
	}

	CG_DrawHostTextSpan( x, y, scale, color, drawText, fontIndex, style, qfalse );
}

/*
=============
CG_Text_Paint
=============
*/
void CG_Text_Paint(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style) {
	CG_Text_PaintExt( x, y, scale, color, text, adjust, limit, style, ITEM_FONT_INHERIT );
}

/*
=============
CG_Text_PaintNoAdjust

Forwards to the shared text painter with zero glyph adjustment.
=============
*/
static void CG_Text_PaintNoAdjust( float x, float y, float scale, vec4_t color, const char *text, int limit, int style ) {
	CG_Text_Paint( x, y, scale, color, text, 0.0f, limit, style );
}


/*
=============
CG_WorldCoordToScreenCoord

Projects a world position into the 640x480 virtual screen space.
=============
*/
static qboolean CG_WorldCoordToScreenCoord( const vec3_t world, float *x, float *y ) {
	vec3_t	transformed;
	float	tanHalfFovX;
	float	tanHalfFovY;
	float	ndcX;
	float	ndcY;
	float	pixelX;
	float	pixelY;
	float	widthScale;
	float	heightScale;
	float	forward;
	float	right;
	float	up;

	if ( cgs.glconfig.vidWidth <= 0 || cgs.glconfig.vidHeight <= 0 || cg.refdef.width <= 0 || cg.refdef.height <= 0 ) {
		return qfalse;
	}

	VectorSubtract( world, cg.refdef.vieworg, transformed );
	right = DotProduct( transformed, cg.refdef.viewaxis[1] );
	up = DotProduct( transformed, cg.refdef.viewaxis[2] );
	forward = DotProduct( transformed, cg.refdef.viewaxis[0] );
	if ( forward <= 0.001f ) {
		return qfalse;
	}

	tanHalfFovX = tan( DEG2RAD( cg.refdef.fov_x * 0.5f ) );
	tanHalfFovY = tan( DEG2RAD( cg.refdef.fov_y * 0.5f ) );
	if ( tanHalfFovX == 0.0f || tanHalfFovY == 0.0f ) {
		return qfalse;
	}

	ndcX = right / ( forward * tanHalfFovX );
	ndcY = up / ( forward * tanHalfFovY );
	pixelX = cg.refdef.x + ( 1.0f + ndcX ) * cg.refdef.width * 0.5f;
	pixelY = cg.refdef.y + ( 1.0f - ndcY ) * cg.refdef.height * 0.5f;
	if ( pixelX < 0.0f || pixelX > cgs.glconfig.vidWidth || pixelY < 0.0f || pixelY > cgs.glconfig.vidHeight ) {
		return qfalse;
	}

	widthScale = (float)SCREEN_WIDTH / (float)cgs.glconfig.vidWidth;
	heightScale = (float)SCREEN_HEIGHT / (float)cgs.glconfig.vidHeight;
	if ( x ) {
		*x = pixelX * widthScale;
	}
	if ( y ) {
		*y = pixelY * heightScale;
	}
	return qtrue;
}

static cgQueuedWorldMarker_t	cg_queuedWorldMarkers[CG_MAX_QUEUED_WORLD_MARKERS];

/*
===============================
CG_ResetQueuedWorldMarkerDefaults

Seeds the shared queued world-marker record with the retail defaults.
===============================
*/
static void CG_ResetQueuedWorldMarkerDefaults( cgQueuedWorldMarker_t *marker ) {
	if ( !marker ) {
		return;
	}

	memset( marker, 0, sizeof( *marker ) );
	marker->active = qtrue;
	marker->startTime = cg.time;
	marker->duration = 2000;
	marker->alpha = 1.0f;
	marker->size = 24.0f;
	marker->textScale = 0.18f;
	marker->color[0] = 1.0f;
	marker->color[1] = 1.0f;
	marker->color[2] = 1.0f;
	marker->color[3] = 1.0f;
}

/*
=========================
CG_ClearQueuedWorldMarkers

Clears the retail queued world-marker slab.
=========================
*/
void CG_ClearQueuedWorldMarkers( void ) {
	memset( cg_queuedWorldMarkers, 0, sizeof( cg_queuedWorldMarkers ) );
}

/*
=======================
CG_AllocQueuedWorldMarker

Allocates a queued world-marker slot from the retail-sized slab.
=======================
*/
cgQueuedWorldMarker_t *CG_AllocQueuedWorldMarker( void ) {
	cgQueuedWorldMarker_t	*marker;
	int				i;

	for ( i = 0; i < ARRAY_LEN( cg_queuedWorldMarkers ); i++ ) {
		marker = &cg_queuedWorldMarkers[i];
		if ( marker->active ) {
			continue;
		}

		CG_ResetQueuedWorldMarkerDefaults( marker );
		return marker;
	}

	return NULL;
}

/*
=============================
CG_AllocQueuedWorldMarkerForKey

Reuses a keyed queued world-marker slot when the same producer refreshes it.
=============================
*/
cgQueuedWorldMarker_t *CG_AllocQueuedWorldMarkerForKey( int kind, int key ) {
	cgQueuedWorldMarker_t	*marker;
	int				i;

	for ( i = 0; i < ARRAY_LEN( cg_queuedWorldMarkers ); i++ ) {
		marker = &cg_queuedWorldMarkers[i];
		if ( !marker->active || marker->kind != kind || marker->key != key ) {
			continue;
		}

		CG_ResetQueuedWorldMarkerDefaults( marker );
		marker->kind = kind;
		marker->key = key;
		return marker;
	}

	marker = CG_AllocQueuedWorldMarker();
	if ( !marker ) {
		return NULL;
	}

	marker->kind = kind;
	marker->key = key;
	return marker;
}

/*
====================
CG_POIMarkerSizeForOrigin

Applies the retail POI width clamp from the hidden cg_poi* cvars.
====================
*/
float CG_POIMarkerSizeForOrigin( const vec3_t origin ) {
	float	minWidth;
	float	maxWidth;
	float	distance;
	float	frac;

	maxWidth = ( cg_poiMaxWidth.value > 0.0f ) ? cg_poiMaxWidth.value : 32.0f;
	minWidth = ( cg_poiMinWidth.value > 0.0f ) ? cg_poiMinWidth.value : 16.0f;
	if ( minWidth > maxWidth ) {
		minWidth = maxWidth;
	}
	if ( !cg.snap ) {
		return maxWidth;
	}

	distance = Distance( cg.refdef.vieworg, origin );
	if ( distance <= 256.0f ) {
		return maxWidth;
	}
	if ( distance >= 768.0f ) {
		return minWidth;
	}

	frac = ( distance - 256.0f ) / ( 768.0f - 256.0f );
	return maxWidth + ( minWidth - maxWidth ) * frac;
}

/*
=========================
CG_ShouldDrawPOIMarkerMode

Applies the retail cg_powerupPOIs mode split before queuing a persistent POI.
=========================
*/
qboolean CG_ShouldDrawPOIMarkerMode( int mode, const vec3_t origin ) {
	trace_t	trace;
	int		skipNum;

	if ( mode <= 0 ) {
		return qfalse;
	}
	if ( mode >= 2 ) {
		return qtrue;
	}
	if ( !cg.snap ) {
		return qfalse;
	}

	skipNum = cg.predictedPlayerState.clientNum;
	if ( skipNum < 0 ) {
		skipNum = cg.snap->ps.clientNum;
	}

	CG_Trace( &trace, cg.refdef.vieworg, vec3_origin, vec3_origin, origin, skipNum, MASK_OPAQUE );
	return (qboolean)( trace.fraction < 1.0f );
}

/*
==========================
CG_UpdateQueuedWorldMarkers

Updates queued world-marker lifetimes and fade alpha ahead of the frame build.
==========================
*/
void CG_UpdateQueuedWorldMarkers( void ) {
	cgQueuedWorldMarker_t	*marker;
	int				elapsed;
	int				i;

	for ( i = 0; i < ARRAY_LEN( cg_queuedWorldMarkers ); i++ ) {
		marker = &cg_queuedWorldMarkers[i];
		if ( !marker->active ) {
			continue;
		}

		elapsed = cg.time - marker->startTime;
		if ( elapsed < 0 ) {
			elapsed = 0;
		}

		if ( marker->duration > 0 && elapsed >= marker->duration ) {
			memset( marker, 0, sizeof( *marker ) );
			continue;
		}

		marker->alpha = 1.0f;
		if ( marker->duration > 0 && marker->fadeDelay > 0 &&
				elapsed > marker->fadeDelay && marker->fadeDelay < marker->duration ) {
			float fadeFrac;

			fadeFrac = (float)( elapsed - marker->fadeDelay ) /
				(float)( marker->duration - marker->fadeDelay );
			marker->alpha = 1.0f - fadeFrac;
			if ( marker->alpha < 0.0f ) {
				marker->alpha = 0.0f;
			} else if ( marker->alpha > 1.0f ) {
				marker->alpha = 1.0f;
			}
		}
	}
}

/*
========================
CG_DrawQueuedWorldMarkers

Projects and draws the active queued world-marker records.
========================
*/
void CG_DrawQueuedWorldMarkers( void ) {
	cgQueuedWorldMarker_t	*marker;
	vec3_t			markerOrigin;
	vec4_t			color;
	float			screenX;
	float			screenY;
	float			textWidth;
	float			textHeight;
	float			elapsedFrac;
	float			drawY;
	int				i;

	for ( i = 0; i < ARRAY_LEN( cg_queuedWorldMarkers ); i++ ) {
		marker = &cg_queuedWorldMarkers[i];
		if ( !marker->active || marker->alpha <= 0.0f ) {
			continue;
		}

		VectorCopy( marker->origin, markerOrigin );
		elapsedFrac = 0.0f;
		if ( marker->duration > 0 ) {
			elapsedFrac = (float)( cg.time - marker->startTime ) / (float)marker->duration;
			if ( elapsedFrac < 0.0f ) {
				elapsedFrac = 0.0f;
			} else if ( elapsedFrac > 1.0f ) {
				elapsedFrac = 1.0f;
			}
		}
		markerOrigin[2] += marker->rise * elapsedFrac;

		if ( !CG_WorldCoordToScreenCoord( markerOrigin, &screenX, &screenY ) ) {
			continue;
		}

		Vector4Copy( marker->color, color );
		color[3] *= marker->alpha;

		drawY = screenY;
		if ( marker->shader ) {
			trap_R_SetColor( color );
			CG_DrawPic( screenX - ( marker->size * 0.5f ), drawY - ( marker->size * 0.5f ),
				marker->size, marker->size, marker->shader );
			trap_R_SetColor( NULL );
		}

		if ( !marker->text[0] ) {
			continue;
		}

		textWidth = (float)CG_Text_Width( marker->text, marker->textScale, 0 );
		textHeight = (float)CG_Text_Height( marker->text, marker->textScale, 0 );
		CG_Text_Paint( screenX - ( textWidth * 0.5f ), drawY + ( textHeight * 0.5f ),
			marker->textScale, color, marker->text, 0.0f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	}
}

#define CG_TEAMMATE_POI_LABEL_SCALE			0.22f
#define CG_TEAMMATE_POI_ICON_SIZE			10.0f
#define CG_TEAMMATE_POI_BAR_HEIGHT			3.0f
#define CG_TEAMMATE_POI_PADDING_X			3.0f
#define CG_TEAMMATE_POI_PADDING_Y			2.0f
#define CG_TEAMMATE_POI_WORLD_Z_OFFSET		48.0f
#define CG_TEAMMATE_POI_MAX_LABEL_CHARS		40
#define CG_TEAMMATE_POI_MAX_ICONS			4

/*
=============
CG_ShouldDrawTeammatePOIs

Applies the retail-style teammate POI gates before the projected pass runs.
=============
*/
static qboolean CG_ShouldDrawTeammatePOIs( void ) {
	team_t	myTeam;

	if ( !cg.snap || cgs.gametype < GT_TEAM ) {
		return qfalse;
	}

	myTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	if ( myTeam != TEAM_RED && myTeam != TEAM_BLUE ) {
		return qfalse;
	}

	if ( cg.predictedPlayerState.stats[STAT_HEALTH] <= 0 ) {
		return qfalse;
	}

	if ( cg_teammateNames.integer == 0 && cg_teammatePOIs.integer == 0 ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CG_GetTeammatePOIArmorColor

Matches the retail armor tier colors used by the HUD bar paths.
=============
*/
static void CG_GetTeammatePOIArmorColor( int armor, vec4_t color ) {
	if ( armor >= 150 ) {
		color[0] = 0.9f;
		color[1] = 0.15f;
		color[2] = 0.15f;
		color[3] = 1.0f;
	} else if ( armor >= 100 ) {
		color[0] = 0.95f;
		color[1] = 0.75f;
		color[2] = 0.2f;
		color[3] = 1.0f;
	} else if ( armor > 0 ) {
		color[0] = 0.2f;
		color[1] = 0.8f;
		color[2] = 0.2f;
		color[3] = 1.0f;
	} else {
		color[0] = 0.4f;
		color[1] = 0.4f;
		color[2] = 0.4f;
		color[3] = 0.6f;
	}
}

/*
=============
CG_TeammatePOILocation

Returns the location string used by the projected teammate label.
=============
*/
static const char *CG_TeammatePOILocation( const clientInfo_t *ci ) {
	const char	*location;

	if ( !ci || ci->location <= 0 ) {
		return "";
	}

	location = CG_ConfigString( CS_LOCATIONS + ci->location );
	if ( !location || !location[0] ) {
		return "";
	}

	return location;
}

/*
=============
CG_TrimTeammatePOILabelToWidth

Applies the retail-style ".." prefix when the projected label would overrun its width budget.
=============
*/
static void CG_TrimTeammatePOILabelToWidth( const char *source, char *buffer, size_t bufferSize, float scale, float maxWidth ) {
	const char	*trimmed;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	if ( !source || !source[0] ) {
		buffer[0] = '\0';
		return;
	}

	Q_strncpyz( buffer, source, bufferSize );
	if ( maxWidth <= 0.0f || CG_Text_Width( buffer, scale, 0 ) <= maxWidth ) {
		return;
	}

	trimmed = source;
	while ( *trimmed ) {
		Com_sprintf( buffer, bufferSize, "..%s", trimmed );
		if ( CG_Text_Width( buffer, scale, 0 ) <= maxWidth ) {
			return;
		}
		trimmed++;
	}

	Q_strncpyz( buffer, "..", bufferSize );
}

/*
=============
CG_BuildTeammatePOILabel

Builds the retail-style name/location slab used above projected teammates.
=============
*/
static void CG_BuildTeammatePOILabel( const clientInfo_t *ci, char *buffer, size_t bufferSize ) {
	char		baseLabel[128];
	const char	*location;
	float		maxWidth;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !ci || !ci->infoValid ) {
		return;
	}

	location = CG_TeammatePOILocation( ci );
	if ( cg_teammateNames.integer ) {
		if ( location[0] ) {
			Com_sprintf( baseLabel, sizeof( baseLabel ), "%s [%s]", ci->name, location );
		} else {
			Q_strncpyz( baseLabel, ci->name, sizeof( baseLabel ) );
		}
	} else if ( location[0] ) {
		Q_strncpyz( baseLabel, location, sizeof( baseLabel ) );
	} else {
		return;
	}

	maxWidth = cg_teammatePOIsMaxWidth.value * SMALLCHAR_WIDTH;
	if ( maxWidth < 0.0f ) {
		maxWidth = 0.0f;
	}

	CG_TrimTeammatePOILabelToWidth( baseLabel, buffer, bufferSize, CG_TEAMMATE_POI_LABEL_SCALE, maxWidth );
}

/*
=============
CG_ItemBackedPowerupIcon

Resolves the classic HUD/item-table icon for a powerup.
=============
*/
static qhandle_t CG_ItemBackedPowerupIcon( int powerup ) {
	gitem_t	*item;

	item = BG_FindItemForPowerup( powerup );
	if ( item ) {
		return cg_items[ITEM_INDEX( item )].icon;
	}

	switch ( powerup ) {
	case PW_QUAD:
		return cgs.media.quadShader;
	case PW_BATTLESUIT:
		return cgs.media.battleSuitShader;
	case PW_REGEN:
		return cgs.media.regenShader;
	case PW_INVIS:
		return cgs.media.invisShader;
	default:
		return 0;
	}
}

/*
=============
CG_TeammatePOIPowerupIcon

Resolves the icon used for projected teammate markers.
=============
*/
static qhandle_t CG_TeammatePOIPowerupIcon( int powerup ) {
	switch ( powerup ) {
	case PW_QUAD:
		if ( cgs.media.poiPowerupQuadShader ) {
			return cgs.media.poiPowerupQuadShader;
		}
		break;
	case PW_BATTLESUIT:
		if ( cgs.media.poiPowerupBattleSuitShader ) {
			return cgs.media.poiPowerupBattleSuitShader;
		}
		break;
	case PW_HASTE:
		if ( cgs.media.poiPowerupHasteShader ) {
			return cgs.media.poiPowerupHasteShader;
		}
		break;
	case PW_INVIS:
		if ( cgs.media.poiPowerupInvisShader ) {
			return cgs.media.poiPowerupInvisShader;
		}
		break;
	case PW_REGEN:
		if ( cgs.media.poiPowerupRegenShader ) {
			return cgs.media.poiPowerupRegenShader;
		}
		break;
	default:
		break;
	}

	return CG_ItemBackedPowerupIcon( powerup );
}

/*
=============
CG_TeammatePOIIconCount

Counts the status markers that will be appended to a teammate POI slab.
=============
*/
static int CG_TeammatePOIIconCount( const clientInfo_t *ci ) {
	static const int powerups[] = {
		PW_REDFLAG,
		PW_BLUEFLAG,
		PW_NEUTRALFLAG,
		PW_QUAD,
		PW_BATTLESUIT,
		PW_REGEN,
		PW_HASTE,
		PW_INVIS
	};
	int	i;
	int	count;

	if ( !ci || !ci->infoValid || cg_teammatePOIs.integer == 0 ) {
		return 0;
	}

	count = ( ci->teamTask != TEAMTASK_NONE ) ? 1 : 0;
	for ( i = 0; i < ARRAY_LEN( powerups ) && count < CG_TEAMMATE_POI_MAX_ICONS; i++ ) {
		if ( ci->powerups & ( 1 << powerups[i] ) ) {
			count++;
		}
	}

	return count;
}

/*
=============
CG_DrawTeammatePOIBar

Draws a compact retail-style teammate health or armor bar.
=============
*/
static void CG_DrawTeammatePOIBar( float x, float y, float width, qhandle_t shader, float fraction, const vec4_t color ) {
	vec4_t	backgroundColor = { 0.0f, 0.0f, 0.0f, 0.35f };
	float	drawX;
	float	drawY;
	float	drawW;
	float	drawH;

	CG_FillRect( x, y, width, CG_TEAMMATE_POI_BAR_HEIGHT, backgroundColor );
	if ( fraction <= 0.0f ) {
		return;
	}

	if ( !shader ) {
		cgs.media.healthSegmentShader = trap_R_RegisterShader( "gfx/2d/health_segment.tga" );
		shader = cgs.media.healthSegmentShader;
	}

	fraction = Com_Clamp( 0.0f, 1.0f, fraction );
	drawX = x;
	drawY = y;
	drawW = width * fraction;
	drawH = CG_TEAMMATE_POI_BAR_HEIGHT;
	CG_AdjustFrom640( &drawX, &drawY, &drawW, &drawH );

	trap_R_SetColor( color );
	trap_R_DrawStretchPic( drawX, drawY, drawW, drawH, 0.0f, 0.0f, fraction, 1.0f, shader ? shader : cgs.media.whiteShader );
	trap_R_SetColor( NULL );
}

/*
=============
CG_DrawTeammatePOIIcons

Appends task, flag, and powerup markers beside the projected teammate slab.
=============
*/
static void CG_DrawTeammatePOIIcons( const clientInfo_t *ci, float x, float y ) {
	static const int powerups[] = {
		PW_REDFLAG,
		PW_BLUEFLAG,
		PW_NEUTRALFLAG,
		PW_QUAD,
		PW_BATTLESUIT,
		PW_REGEN,
		PW_HASTE,
		PW_INVIS
	};
	int			i;
	int			drawn;
	qhandle_t	icon;

	if ( !ci || !ci->infoValid || cg_teammatePOIs.integer == 0 ) {
		return;
	}

	drawn = 0;
	if ( ci->teamTask != TEAMTASK_NONE ) {
		icon = CG_StatusHandle( ci->teamTask );
		if ( icon ) {
			CG_DrawPic( x, y, CG_TEAMMATE_POI_ICON_SIZE, CG_TEAMMATE_POI_ICON_SIZE, icon );
			x += CG_TEAMMATE_POI_ICON_SIZE + 1.0f;
			drawn++;
		}
	}

	for ( i = 0; i < ARRAY_LEN( powerups ) && drawn < CG_TEAMMATE_POI_MAX_ICONS; i++ ) {
		if ( !( ci->powerups & ( 1 << powerups[i] ) ) ) {
			continue;
		}

		icon = CG_TeammatePOIPowerupIcon( powerups[i] );
		if ( !icon ) {
			continue;
		}

		CG_DrawPic( x, y, CG_TEAMMATE_POI_ICON_SIZE, CG_TEAMMATE_POI_ICON_SIZE, icon );
		x += CG_TEAMMATE_POI_ICON_SIZE + 1.0f;
		drawn++;
	}
}

/*
=============
CG_DrawTeammatePOIs

Projects retail-style teammate POI slabs above visible teammates.
=============
*/
static void CG_DrawTeammatePOIs( void ) {
	vec4_t			backgroundColor;
	vec4_t			textColor = { 1.0f, 1.0f, 1.0f, 1.0f };
	vec4_t			healthColor;
	vec4_t			armorColor;
	team_t			myTeam;
	int				i;

	if ( !CG_ShouldDrawTeammatePOIs() ) {
		return;
	}

	myTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	for ( i = 0; i < cgs.maxclients; i++ ) {
		centity_t		*cent;
		clientInfo_t	*ci;
		vec3_t			poiOrigin;
		char			label[CG_TEAMMATE_POI_MAX_LABEL_CHARS];
		float			screenX;
		float			screenY;
		float			minWidth;
		float			labelWidth;
		float			boxWidth;
		float			boxHeight;
		float			boxX;
		float			boxY;
		float			textBaseline;
		float			barWidth;
		float			iconOffset;
		int				iconCount;

		if ( i == cg.snap->ps.clientNum ) {
			continue;
		}

		ci = &cgs.clientinfo[i];
		cent = &cg_entities[i];
		if ( !ci->infoValid || ci->team != myTeam || !cent->currentValid ) {
			continue;
		}
		if ( cent->currentState.eFlags & EF_DEAD ) {
			continue;
		}
		if ( ci->health <= 0 ) {
			continue;
		}

		VectorCopy( cent->lerpOrigin, poiOrigin );
		poiOrigin[2] += CG_TEAMMATE_POI_WORLD_Z_OFFSET;
		if ( !trap_R_inPVS( cg.refdef.vieworg, poiOrigin ) ) {
			continue;
		}
		if ( !CG_WorldCoordToScreenCoord( poiOrigin, &screenX, &screenY ) ) {
			continue;
		}

		CG_BuildTeammatePOILabel( ci, label, sizeof( label ) );
		iconCount = CG_TeammatePOIIconCount( ci );
		if ( label[0] == '\0' && iconCount == 0 ) {
			continue;
		}

		labelWidth = label[0] ? (float)CG_Text_Width( label, CG_TEAMMATE_POI_LABEL_SCALE, 0 ) : 0.0f;
		minWidth = cg_teammatePOIsMinWidth.value * SMALLCHAR_WIDTH;
		boxWidth = labelWidth;
		if ( boxWidth < minWidth ) {
			boxWidth = minWidth;
		}

		if ( cg_teammatePOIs.integer ) {
			if ( boxWidth < 40.0f ) {
				boxWidth = 40.0f;
			}
		}

		boxHeight = 12.0f;
		if ( label[0] ) {
			boxHeight += CG_Text_Height( label, CG_TEAMMATE_POI_LABEL_SCALE, 0 );
		}
		if ( cg_teammatePOIs.integer ) {
			boxHeight += ( CG_TEAMMATE_POI_BAR_HEIGHT * 2.0f ) + 3.0f;
		}
		boxHeight += CG_TEAMMATE_POI_PADDING_Y * 2.0f;

		boxX = screenX - ( boxWidth * 0.5f ) - CG_TEAMMATE_POI_PADDING_X;
		boxY = screenY - boxHeight - 18.0f;
		iconOffset = iconCount > 0 ? (float)iconCount * ( CG_TEAMMATE_POI_ICON_SIZE + 1.0f ) + 2.0f : 0.0f;

		Vector4Copy( CG_TeamColor( ci->team ), backgroundColor );
		backgroundColor[3] = ( ci->powerups & ( ( 1 << PW_REDFLAG ) | ( 1 << PW_BLUEFLAG ) | ( 1 << PW_NEUTRALFLAG ) ) ) ? 0.40f : 0.28f;
		CG_FillRect( boxX, boxY, boxWidth + ( CG_TEAMMATE_POI_PADDING_X * 2.0f ) + iconOffset, boxHeight, backgroundColor );

		textBaseline = boxY + CG_TEAMMATE_POI_PADDING_Y;
		if ( label[0] ) {
			textBaseline += CG_Text_Height( label, CG_TEAMMATE_POI_LABEL_SCALE, 0 );
			CG_Text_Paint( boxX + CG_TEAMMATE_POI_PADDING_X, textBaseline, CG_TEAMMATE_POI_LABEL_SCALE, textColor, label, 0, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
		}

		if ( cg_teammatePOIs.integer ) {
			barWidth = boxWidth;
			textBaseline += 2.0f;
			CG_GetColorForHealth( ci->health, ci->armor, healthColor );
			healthColor[3] = 1.0f;
			CG_DrawTeammatePOIBar(
				boxX + CG_TEAMMATE_POI_PADDING_X,
				textBaseline,
				barWidth,
				cgs.media.healthSegmentShader,
				Com_Clamp( 0.0f, 200.0f, (float)ci->health ) / 200.0f,
				healthColor
			);

			textBaseline += CG_TEAMMATE_POI_BAR_HEIGHT + 1.0f;
			CG_GetTeammatePOIArmorColor( ci->armor, armorColor );
			CG_DrawTeammatePOIBar(
				boxX + CG_TEAMMATE_POI_PADDING_X,
				textBaseline,
				barWidth,
				cgs.media.healthSegmentShader,
				Com_Clamp( 0.0f, 200.0f, (float)ci->armor ) / 200.0f,
				armorColor
			);

			CG_DrawTeammatePOIIcons( ci, boxX + boxWidth + ( CG_TEAMMATE_POI_PADDING_X * 2.0f ), boxY + CG_TEAMMATE_POI_PADDING_Y );
		}
	}
}

/*
=============
CG_DrawRacePoints

Renders projected race checkpoint icons and their distance labels.
=============
*/
static void CG_DrawRacePoints( void ) {
	int	slotCount;
	int	i;
	float	screenX;
	float	screenY;
	vec3_t	delta;
	float	distance;
	char	distanceText[16];
	int	textWidth;
	int	textX;
	int	textY;
	qhandle_t	shader;
	const float	iconSize = 32.0f;
	cgRacePointInfo_t	*info;

	if ( cgs.gametype != GT_RACE || !cg.snap || cgs.racePointCount <= 0 ) {
		return;
	}

	slotCount = cgs.racePointCount;
	if ( cgs.raceLeaderSplitCount > slotCount ) {
		slotCount = cgs.raceLeaderSplitCount;
	}
	if ( slotCount > MAX_RACE_POINTS ) {
		slotCount = MAX_RACE_POINTS;
	}

	for ( i = 0; i < slotCount; i++ ) {
		info = &cgs.racePoints[i];
		if ( !info->active ) {
			continue;
		}
		if ( !CG_WorldCoordToScreenCoord( info->origin, &screenX, &screenY ) ) {
			continue;
		}

		VectorSubtract( info->origin, cg.predictedPlayerState.origin, delta );
		distance = VectorLength( delta );
		shader = cgs.media.raceCheckpointShader;
		if ( i == 0 && cgs.media.raceStartShader ) {
			shader = cgs.media.raceStartShader;
		} else if ( i == cgs.racePointCount - 1 && cgs.media.raceFinishShader ) {
			shader = cgs.media.raceFinishShader;
		} else if ( !shader ) {
			continue;
		}

		CG_DrawPic( screenX - ( iconSize * 0.5f ), screenY - ( iconSize * 0.5f ), iconSize, iconSize, shader );
		if ( distance >= 1000.0f ) {
			Com_sprintf( distanceText, sizeof( distanceText ), "%.1fk", distance / 1000.0f );
		} else {
			Com_sprintf( distanceText, sizeof( distanceText ), "%.0f", distance );
		}
		textWidth = CG_DrawStrlen( distanceText ) * SMALLCHAR_WIDTH;
		textX = (int)( screenX - ( textWidth / 2 ) );
		textY = (int)( screenY + ( iconSize * 0.5f ) + 2.0f );
		CG_DrawStringExt( textX, textY, distanceText, colorWhite, qfalse, qtrue, SMALLCHAR_WIDTH, SMALLCHAR_HEIGHT, 0 );
	}
}



/*
==============
CG_DrawField

Draws large numbers for status bar and powerups
==============
*/

/*
================
CG_Draw3DModel

================
*/
void CG_Draw3DModel( float x, float y, float w, float h, qhandle_t model, qhandle_t skin, vec3_t origin, vec3_t angles ) {
	refdef_t		refdef;
	refEntity_t		ent;

	if ( !cg_draw3dIcons.integer || !cg_drawIcons.integer ) {
		return;
	}

	CG_AdjustFrom640( &x, &y, &w, &h );

	memset( &refdef, 0, sizeof( refdef ) );

	memset( &ent, 0, sizeof( ent ) );
	AnglesToAxis( angles, ent.axis );
	VectorCopy( origin, ent.origin );
	ent.hModel = model;
	ent.customSkin = skin;
	ent.renderfx = RF_NOSHADOW;		// no stencil shadows

	refdef.rdflags = RDF_NOWORLDMODEL;

	AxisClear( refdef.viewaxis );

	refdef.fov_x = 30;
	refdef.fov_y = 30;

	refdef.x = x;
	refdef.y = y;
	refdef.width = w;
	refdef.height = h;

	refdef.time = cg.time;

	trap_R_ClearScene();
	trap_R_AddRefEntityToScene( &ent );
	trap_R_RenderScene( &refdef );
}

/*
================
CG_DrawHead

Used for both the status bar and the scoreboard
================
*/
void CG_DrawHead( float x, float y, float w, float h, int clientNum, vec3_t headAngles ) {
	clipHandle_t	cm;
	clientInfo_t	*ci;
	float			len;
	vec3_t			origin;
	vec3_t			mins, maxs;

	ci = &cgs.clientinfo[ clientNum ];

	if ( cg_draw3dIcons.integer ) {
		cm = ci->headModel;
		if ( !cm ) {
			return;
		}

		// offset the origin y and z to center the head
		trap_R_ModelBounds( cm, mins, maxs );

		origin[2] = -0.5 * ( mins[2] + maxs[2] );
		origin[1] = 0.5 * ( mins[1] + maxs[1] );

		// calculate distance so the head nearly fills the box
		// assume heads are taller than wide
		len = 0.7 * ( maxs[2] - mins[2] );
		if ( cgs.playerModelScale > 0.0f ) {
			len *= cgs.playerModelScale;
		}
		origin[0] = len / 0.268;	// len / tan( fov/2 )

		// allow per-model tweaking
		VectorAdd( origin, ci->headOffset, origin );

		CG_Draw3DModel( x, y, w, h, ci->headModel, ci->headSkin, origin, headAngles );
	} else if ( cg_drawIcons.integer ) {
		CG_DrawPic( x, y, w, h, ci->modelIcon );
	}

	// if they are deferred, draw a cross out
	if ( ci->deferred ) {
		CG_DrawPic( x, y, w, h, cgs.media.deferShader );
	}
}

/*
================
CG_DrawFlagModel

Used for both the status bar and the scoreboard
================
*/
void CG_DrawFlagModel( float x, float y, float w, float h, int team, qboolean force2D ) {
	qhandle_t		cm;
	float			len;
	vec3_t			origin, angles;
	vec3_t			mins, maxs;
	qhandle_t		handle;

	if ( !force2D && cg_draw3dIcons.integer ) {

		VectorClear( angles );

		cm = cgs.media.redFlagModel;

		// offset the origin y and z to center the flag
		trap_R_ModelBounds( cm, mins, maxs );

		origin[2] = -0.5 * ( mins[2] + maxs[2] );
		origin[1] = 0.5 * ( mins[1] + maxs[1] );

		// calculate distance so the flag nearly fills the box
		// assume heads are taller than wide
		len = 0.5 * ( maxs[2] - mins[2] );		
		origin[0] = len / 0.268;	// len / tan( fov/2 )

		angles[YAW] = 60 * sin( cg.time / 2000.0 );;

		if( team == TEAM_RED ) {
			handle = cgs.media.redFlagModel;
		} else if( team == TEAM_BLUE ) {
			handle = cgs.media.blueFlagModel;
		} else if( team == TEAM_FREE ) {
			handle = cgs.media.neutralFlagModel;
		} else {
			return;
		}
		CG_Draw3DModel( x, y, w, h, handle, 0, origin, angles );
	} else if ( cg_drawIcons.integer ) {
		gitem_t *item;

		if( team == TEAM_RED ) {
			item = BG_FindItemForPowerup( PW_REDFLAG );
		} else if( team == TEAM_BLUE ) {
			item = BG_FindItemForPowerup( PW_BLUEFLAG );
		} else if( team == TEAM_FREE ) {
			item = BG_FindItemForPowerup( PW_NEUTRALFLAG );
		} else {
			return;
		}
		if (item) {
		  CG_DrawPic( x, y, w, h, cg_items[ ITEM_INDEX(item) ].icon );
		}
	}
}

/*
================
CG_DrawStatusBarHead

================
*/

/*
================
CG_DrawStatusBarFlag

================
*/

/*
================
CG_DrawTeamBackground

================
*/
void CG_DrawTeamBackground( int x, int y, int w, int h, float alpha, int team )
{
	vec4_t		hcolor;

	hcolor[3] = alpha;
	if ( team == TEAM_RED ) {
		hcolor[0] = 1;
		hcolor[1] = 0;
		hcolor[2] = 0;
	} else if ( team == TEAM_BLUE ) {
		hcolor[0] = 0;
		hcolor[1] = 0;
		hcolor[2] = 1;
	} else {
		return;
	}
	trap_R_SetColor( hcolor );
	CG_DrawPic( x, y, w, h, cgs.media.teamStatusBar );
	trap_R_SetColor( NULL );
}

/*
================
CG_DrawStatusBar

================
*/

/*
===========================================================================================

  UPPER RIGHT CORNER

===========================================================================================
*/

/*
================
CG_GetObituaryIcon
================
*/
qhandle_t CG_GetObituaryIcon( int mod ) {
	switch ( mod ) {
	case MOD_SHOTGUN:
		return cg_weapons[WP_SHOTGUN].weaponIcon;
	case MOD_GAUNTLET:
		return cg_weapons[WP_GAUNTLET].weaponIcon;
	case MOD_MACHINEGUN:
		return cg_weapons[WP_MACHINEGUN].weaponIcon;
	case MOD_HMG:
		return cg_weapons[WP_HEAVY_MACHINEGUN].weaponIcon;
	case MOD_GRENADE:
	case MOD_GRENADE_SPLASH:
		return cg_weapons[WP_GRENADE_LAUNCHER].weaponIcon;
	case MOD_ROCKET:
	case MOD_ROCKET_SPLASH:
		return cg_weapons[WP_ROCKET_LAUNCHER].weaponIcon;
	case MOD_PLASMA:
	case MOD_PLASMA_SPLASH:
		return cg_weapons[WP_PLASMAGUN].weaponIcon;
	case MOD_RAILGUN:
	case MOD_RAILGUN_HEADSHOT:
		return cg_weapons[WP_RAILGUN].weaponIcon;
	case MOD_LIGHTNING:
	case MOD_LIGHTNING_DISCHARGE:
		return cg_weapons[WP_LIGHTNING].weaponIcon;
	case MOD_BFG:
	case MOD_BFG_SPLASH:
		return cg_weapons[WP_BFG].weaponIcon;
	case MOD_NAIL:
		return cg_weapons[WP_NAILGUN].weaponIcon;
	case MOD_CHAINGUN:
		return cg_weapons[WP_CHAINGUN].weaponIcon;
	case MOD_PROXIMITY_MINE:
		return cg_weapons[WP_PROX_LAUNCHER].weaponIcon;
	case MOD_GRAPPLE:
		return cg_weapons[WP_GRAPPLING_HOOK].weaponIcon;
	case MOD_THAW:
		return cg_weapons[WP_LIGHTNING].weaponIcon; // Use LG icon for thaw? Or a specific one? QL might use standard gauntlet or LG.
	case MOD_KAMIKAZE:
		return cgs.media.kamikazeIcon;
	case MOD_JUICED:
		return cgs.media.juicedIcon;
	case MOD_WATER:
		return cgs.media.waterIcon;
	case MOD_SLIME:
		return cgs.media.slimeIcon;
	case MOD_LAVA:
		return cgs.media.lavaIcon;
	case MOD_CRUSH:
		return cgs.media.crushIcon;
	case MOD_TELEFRAG:
		return cgs.media.telefragIcon;
	case MOD_FALLING:
		return cgs.media.fallingIcon;
	case MOD_SUICIDE:
	case MOD_SWITCHTEAM:
		return cgs.media.suicideIcon;
	case MOD_TARGET_LASER:
	case MOD_TRIGGER_HURT:
	case MOD_UNKNOWN:
	default:
		return cgs.media.suicideIcon;
	}
}

/*
=============
CG_ObituaryColorForIndex

Maps the retail obituary palette index to the draw color for one name column.
=============
*/
void CG_ObituaryColorForIndex( int colorIndex, float alpha, vec4_t color ) {
	switch ( colorIndex ) {
	case 1:
		color[0] = 1.0f;
		color[1] = 0.5f;
		color[2] = 0.5f;
		break;
	case 2:
		color[0] = 0.5f;
		color[1] = 0.75f;
		color[2] = 1.0f;
		break;
	case 3:
		color[0] = 0.85f;
		color[1] = 0.85f;
		color[2] = 0.85f;
		break;
	default:
		color[0] = 1.0f;
		color[1] = 1.0f;
		color[2] = 1.0f;
		break;
	}

	color[3] = alpha;
}

/*
================
CG_DrawObituaries
================
*/
static float CG_DrawObituaries( float y ) {
	int		i;
	float		alpha;
	vec4_t	targetColor;
	vec4_t	attackerColor;
	int		w;
	int		h;
	int		time;
	float		x;

	CG_PruneObituaryFeed();

	if ( cg_drawFragMessages.integer == 0 ) {
		return y;
	}

	for ( i = 0; i < MAX_OBITUARIES; i++ ) {
		const cgObituary_t	*entry;

		entry = &cg.obituaries[i];
		if ( !entry->active ) {
			break;
		}

		time = cg.time - entry->time;
		if ( time > OBITUARY_TIME - FADE_TIME ) {
			alpha = (float)( OBITUARY_TIME - time ) / FADE_TIME;
		} else {
			alpha = 1.0f;
		}

		h = SMALLCHAR_HEIGHT;
		w = SMALLCHAR_WIDTH;
		x = 640 - 2;

		if ( entry->targetName[0] ) {
			int nameWidth;

			CG_ObituaryColorForIndex( entry->targetColorIndex, alpha, targetColor );
			nameWidth = CG_DrawStrlen( entry->targetName ) * w;
			x = 640 - nameWidth - 2;
			CG_DrawStringExt( x, y, entry->targetName, targetColor, qfalse, qtrue, w, h, 0 );
			x -= ( w + 2 );
		}

		if ( entry->icon ) {
			trap_R_SetColor( colorWhite );
			x -= 20;
			CG_DrawPic( x, y - 2, 20, 20, entry->icon );
			trap_R_SetColor( NULL );
			x -= 4;
		}

		if ( entry->hasAttacker && entry->attackerName[0] ) {
			int nameWidth;

			CG_ObituaryColorForIndex( entry->attackerColorIndex, alpha, attackerColor );
			nameWidth = CG_DrawStrlen( entry->attackerName ) * w;
			x -= nameWidth;
			CG_DrawStringExt( x, y, entry->attackerName, attackerColor, qfalse, qtrue, w, h, 0 );
		}

		y += h + 4;
	}

	return y;
}

/*
================
CG_DrawAttacker

================
*/
static float CG_DrawAttacker( float y ) {
	int			t;
	float		size;
	vec3_t		angles;
	const char	*info;
	const char	*name;
	int			clientNum;

	if ( cg.predictedPlayerState.stats[STAT_HEALTH] <= 0 ) {
		return y;
	}

	if ( !cg.attackerTime ) {
		return y;
	}

	clientNum = cg.predictedPlayerState.persistant[PERS_ATTACKER];
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS || clientNum == cg.snap->ps.clientNum ) {
		return y;
	}

	t = cg.time - cg.attackerTime;
	if ( t > ATTACKER_HEAD_TIME ) {
		cg.attackerTime = 0;
		return y;
	}

	size = ICON_SIZE * 1.25;

	angles[PITCH] = 0;
	angles[YAW] = 180;
	angles[ROLL] = 0;
	CG_DrawHead( 640 - size, y, size, size, clientNum, angles );

	info = CG_ConfigString( CS_PLAYERS + clientNum );
	name = Info_ValueForKey(  info, "n" );
	y += size;
	CG_DrawBigString( 640 - ( Q_PrintStrlen( name ) * BIGCHAR_WIDTH), y, name, 0.5 );

	return y + BIGCHAR_HEIGHT + 2;
}

/*
==================
CG_DrawSnapshot
==================
*/
static float CG_DrawSnapshot( float y ) {
	char		*s;
	int			w;
	float		drawY;

	s = va( "time:%i snap:%i cmd:%i", cg.snap->serverTime, 
		cg.latestSnapshotNum, cgs.serverCommandSequence );
	w = CG_Text_WidthExt( s, 0.25f, 0, FONT_DEFAULT );
	drawY = (float)(int)( y + 2.0f ) + 16.0f;

	CG_Text_PaintExt( 635.0f - w, drawY, 0.25f, colorWhite, s, 0.0f, 0, ITEM_TEXTSTYLE_NORMAL, FONT_DEFAULT );

	return y + 16.0f + 4.0f;
}

/*
==================
CG_DrawFPS
==================
*/
#define	FPS_FRAMES	4
static float CG_DrawFPS( float y ) {
	char		*s;
	int			w;
	int			h;
	static int	previousTimes[FPS_FRAMES];
	static int	index;
	int		i, total;
	int		fps;
	static	int	previous;
	int		t, frameTime;

	// don't use serverTime, because that will be drifting to
	// correct for internet lag changes, timescales, timedemos, etc
	t = trap_Milliseconds();
	frameTime = t - previous;
	previous = t;

	previousTimes[index % FPS_FRAMES] = frameTime;
	index++;
	if ( index > FPS_FRAMES ) {
		// average multiple frames together to smooth changes out a bit
		total = 0;
		for ( i = 0 ; i < FPS_FRAMES ; i++ ) {
			total += previousTimes[i];
		}
		if ( !total ) {
			total = 1;
		}
		fps = 1000 * FPS_FRAMES / total;

		s = va( "%ifps", fps );
		w = CG_Text_WidthExt( s, 0.25f, 0, FONT_MONO );
		h = CG_Text_HeightExt( s, 0.25f, 0, FONT_MONO );

		CG_Text_PaintExt( 635.0f - w, y + h, 0.25f, colorWhite, s, 0.0f, 0, ITEM_TEXTSTYLE_NORMAL, FONT_MONO );
		return y + h;
	}

	return y;
}

/*
=================
CG_DrawTimer
=================
*/
static float CG_DrawTimer( float y ) {
	int			lineHeight;
	int			drawY;
	char			*s;
	int			w;
	int			mins, seconds, tens;
	int			msec;
	qboolean	countDown;
	int			remaining;

	if ( !cgs.itemTimersEnabled && !cgs.forceHudHints ) {
		return y;
	}

	lineHeight = cgs.itemTimerHeight;
	if ( lineHeight <= 0 ) {
		lineHeight = ITEM_TIMER_DEFAULT_HEIGHT;
	} else if ( lineHeight > ITEM_TIMER_MAX_HEIGHT ) {
		lineHeight = ITEM_TIMER_MAX_HEIGHT;
	}

	countDown = ( qboolean )( cgs.timelimit > 0 && !Q_stricmp( cg_levelTimerDirection.string, "down" ) );
	msec = cg.time - cgs.levelStartTime;
	remaining = 0;

	if ( countDown ) {
		remaining = cgs.timelimit * 60000 - msec;
		if ( remaining <= 0 ) {
			s = "OT";
		} else {
			seconds = remaining / 1000;
			mins = seconds / 60;
			seconds -= mins * 60;
			tens = seconds / 10;
			seconds -= tens * 10;
			s = va( "%i:%i%i", mins, tens, seconds );
		}
	} else {
		seconds = msec / 1000;
		mins = seconds / 60;
		seconds -= mins * 60;
		tens = seconds / 10;
		seconds -= tens * 10;
		s = va( "%i:%i%i", mins, tens, seconds );
	}
	w = CG_DrawStrlen( s ) * BIGCHAR_WIDTH;

	drawY = y + ( lineHeight - BIGCHAR_HEIGHT ) / 2;
	if ( drawY < y + 2 ) {
		drawY = y + 2;
	}
	if ( drawY + BIGCHAR_HEIGHT > y + lineHeight ) {
		drawY = y + lineHeight - BIGCHAR_HEIGHT;
	}

	CG_DrawBigString( 635 - w, drawY, s, 1.0F);

	return y + lineHeight;
}


/*
=================
CG_DrawTeamOverlay
=================
*/

static float CG_DrawTeamOverlay( float y, qboolean right, qboolean upper ) {
	int x, w, h, xx;
	int i, j, len;
	const char *p;
	vec4_t		hcolor;
	int pwidth, lwidth;
	int plyrs;
	char st[16];
	clientInfo_t *ci;
	gitem_t	*item;
	int ret_y, count;

	if ( !cg_drawTeamOverlay.integer ) {
		return y;
	}

	if ( cg.snap->ps.persistant[PERS_TEAM] != TEAM_RED && cg.snap->ps.persistant[PERS_TEAM] != TEAM_BLUE ) {
		return y; // Not on any team
	}

	plyrs = 0;

	// max player name width
	pwidth = 0;
	count = (numSortedTeamPlayers > 8) ? 8 : numSortedTeamPlayers;
	for (i = 0; i < count; i++) {
		ci = cgs.clientinfo + sortedTeamPlayers[i];
		if ( ci->infoValid && ci->team == cg.snap->ps.persistant[PERS_TEAM]) {
			plyrs++;
			len = CG_DrawStrlen(ci->name);
			if (len > pwidth)
				pwidth = len;
		}
	}

	if (!plyrs)
		return y;

	if (pwidth > TEAM_OVERLAY_MAXNAME_WIDTH)
		pwidth = TEAM_OVERLAY_MAXNAME_WIDTH;

	// max location name width
	lwidth = 0;
	for (i = 1; i < MAX_LOCATIONS; i++) {
		p = CG_ConfigString(CS_LOCATIONS + i);
		if (p && *p) {
			len = CG_DrawStrlen(p);
			if (len > lwidth)
				lwidth = len;
		}
	}

	if (lwidth > TEAM_OVERLAY_MAXLOCATION_WIDTH)
		lwidth = TEAM_OVERLAY_MAXLOCATION_WIDTH;

	w = (pwidth + lwidth + 4 + 7) * TINYCHAR_WIDTH;

	if ( right )
		x = 640 - w;
	else
		x = 0;

	h = plyrs * TINYCHAR_HEIGHT;

	if ( upper ) {
		ret_y = y + h;
	} else {
		y -= h;
		ret_y = y;
	}

	if ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_RED ) {
		hcolor[0] = 1.0f;
		hcolor[1] = 0.0f;
		hcolor[2] = 0.0f;
		hcolor[3] = 0.33f;
	} else { // if ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_BLUE )
		hcolor[0] = 0.0f;
		hcolor[1] = 0.0f;
		hcolor[2] = 1.0f;
		hcolor[3] = 0.33f;
	}
	trap_R_SetColor( hcolor );
	CG_DrawPic( x, y, w, h, cgs.media.teamStatusBar );
	trap_R_SetColor( NULL );

	for (i = 0; i < count; i++) {
		ci = cgs.clientinfo + sortedTeamPlayers[i];
		if ( ci->infoValid && ci->team == cg.snap->ps.persistant[PERS_TEAM]) {

			hcolor[0] = hcolor[1] = hcolor[2] = hcolor[3] = 1.0;

			xx = x + TINYCHAR_WIDTH;

			CG_DrawStringExt( xx, y,
				ci->name, hcolor, qfalse, qfalse,
				TINYCHAR_WIDTH, TINYCHAR_HEIGHT, TEAM_OVERLAY_MAXNAME_WIDTH);

			if (lwidth) {
				p = CG_ConfigString(CS_LOCATIONS + ci->location);
				if (!p || !*p)
					p = "unknown";
				len = CG_DrawStrlen(p);
				if (len > lwidth)
					len = lwidth;

//				xx = x + TINYCHAR_WIDTH * 2 + TINYCHAR_WIDTH * pwidth + 
//					((lwidth/2 - len/2) * TINYCHAR_WIDTH);
				xx = x + TINYCHAR_WIDTH * 2 + TINYCHAR_WIDTH * pwidth;
				CG_DrawStringExt( xx, y,
					p, hcolor, qfalse, qfalse, TINYCHAR_WIDTH, TINYCHAR_HEIGHT,
					TEAM_OVERLAY_MAXLOCATION_WIDTH);
			}

			CG_GetColorForHealth( ci->health, ci->armor, hcolor );

			Com_sprintf (st, sizeof(st), "%3i %3i", ci->health,	ci->armor);

			xx = x + TINYCHAR_WIDTH * 3 + 
				TINYCHAR_WIDTH * pwidth + TINYCHAR_WIDTH * lwidth;

			CG_DrawStringExt( xx, y,
				st, hcolor, qfalse, qfalse,
				TINYCHAR_WIDTH, TINYCHAR_HEIGHT, 0 );

			// draw weapon icon
			xx += TINYCHAR_WIDTH * 3;

			if ( cg_weapons[ci->curWeapon].weaponIcon ) {
				CG_DrawPic( xx, y, TINYCHAR_WIDTH, TINYCHAR_HEIGHT, 
					cg_weapons[ci->curWeapon].weaponIcon );
			} else {
				CG_DrawPic( xx, y, TINYCHAR_WIDTH, TINYCHAR_HEIGHT, 
					cgs.media.deferShader );
			}

			// Draw powerup icons
			if (right) {
				xx = x;
			} else {
				xx = x + w - TINYCHAR_WIDTH;
			}
			for (j = 0; j <= PW_NUM_POWERUPS; j++) {
				if (ci->powerups & (1 << j)) {

					item = BG_FindItemForPowerup( j );

					if (item) {
						CG_DrawPic( xx, y, TINYCHAR_WIDTH, TINYCHAR_HEIGHT, 
						trap_R_RegisterShader( item->icon ) );
						if (right) {
							xx -= TINYCHAR_WIDTH;
						} else {
							xx += TINYCHAR_WIDTH;
						}
					}
				}
			}

			y += TINYCHAR_HEIGHT;
		}
	}

	return ret_y;
//#endif
}

/*
=============
CG_GetSpectatorItemPickupMask

Maps an item definition onto the retail spectator-item filter mask.
=============
*/
static int CG_GetSpectatorItemPickupMask( const gitem_t *item ) {
	if ( !item ) {
		return 0;
	}

	if ( item->giType == IT_POWERUP ) {
		return 1;
	}

	if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {
		return 2;
	}

	if ( item->giType == IT_ARMOR ) {
		if ( item->quantity >= 100 ) {
			return 4;
		}

		if ( item->quantity >= 50 ) {
			return 8;
		}
	}

	return 0;
}

/*
=============
CG_IsSpectatorItemPickupModeActive

Returns qtrue when the retail spectator pickup overlay should stay live.
=============
*/
static qboolean CG_IsSpectatorItemPickupModeActive( void ) {
	if ( !cg.snap ) {
		return qfalse;
	}

	if ( cg.demoPlayback ) {
		return qtrue;
	}

	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return qtrue;
	}

	return ( qboolean )( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR );
}

/*
=============
CG_IsSpectatorItemPickupVisible

Applies the spectator timer cvar mask to a cached retail pickup row.
=============
*/
static qboolean CG_IsSpectatorItemPickupVisible( const cgSpectatorItemPickup_t *pickup ) {
	const gitem_t	*item;
	int		mask;

	if ( !pickup || pickup->clientNum < 0 || pickup->remainingTime <= 0 ) {
		return qfalse;
	}

	if ( pickup->itemNum <= 0 || pickup->itemNum >= bg_numItems ) {
		return qfalse;
	}

	item = &bg_itemlist[pickup->itemNum];
	mask = CG_GetSpectatorItemPickupMask( item );
	if ( mask == 0 ) {
		return qfalse;
	}

	return ( ( cg_specItemTimers.integer & mask ) != 0 );
}

/*
=============
CG_GetSpectatorItemPickupPaletteColor

Resolves the compact retail tint used by the duel-side item timer overlay.
=============
*/
static void CG_GetSpectatorItemPickupPaletteColor( int palette, vec4_t color ) {
	switch ( palette ) {
	case 1:
		color[0] = 1.0f;
		color[1] = 0.2f;
		color[2] = 0.1f;
		color[3] = 1.0f;
		break;
	case 2:
		color[0] = 0.2f;
		color[1] = 0.4f;
		color[2] = 1.0f;
		color[3] = 1.0f;
		break;
	default:
		Vector4Copy( colorWhite, color );
		break;
	}
}

/*
=============
CG_CompareSpectatorItemPickups

Orders the cached spectator pickup rows for the classic HUD drawer.
=============
*/
static int QDECL CG_CompareSpectatorItemPickups( const void *a, const void *b ) {
	const cgSpectatorItemPickup_t	*pickupA;
	const cgSpectatorItemPickup_t	*pickupB;
	int			result;

	pickupA = (const cgSpectatorItemPickup_t *)a;
	pickupB = (const cgSpectatorItemPickup_t *)b;

	if ( cgs.gametype == GT_TOURNAMENT ) {
		result = pickupB->palette - pickupA->palette;
		if ( result != 0 ) {
			return result;
		}

		result = pickupA->duelLayout - pickupB->duelLayout;
		if ( result != 0 ) {
			return result;
		}

		if ( pickupA->layoutOrder != 0 && pickupB->layoutOrder != 0 ) {
			result = pickupB->layoutOrder - pickupA->layoutOrder;
			if ( result != 0 ) {
				return result;
			}
		}
	}

	result = (int)pickupB->origin[2] - (int)pickupA->origin[2];
	if ( result != 0 ) {
		return result;
	}

	result = (int)pickupB->origin[1] - (int)pickupA->origin[1];
	if ( result != 0 ) {
		return result;
	}

	result = (int)pickupB->origin[0] - (int)pickupA->origin[0];
	if ( result != 0 ) {
		return result;
	}

	return pickupB->clientNum - pickupA->clientNum;
}

/*
=============
CG_ClearSpectatorItemPickups

Resets the retail spectator pickup overlay cache.
=============
*/
void CG_ClearSpectatorItemPickups( void ) {
	int	i;

	memset( cg.spectatorItemPickups, 0, sizeof( cg.spectatorItemPickups ) );
	for ( i = 0; i < CG_SPECTATOR_ITEM_PICKUP_COUNT; i++ ) {
		cg.spectatorItemPickups[i].clientNum = -1;
	}

	cg.spectatorItemPickupCount = 0;
}

/*
=============
CG_RecordSpectatorItemPickup

Caches a retail-style spectator item timer row keyed by the pickup owner.
=============
*/
void CG_RecordSpectatorItemPickup( const entityState_t *es ) {
	cgSpectatorItemPickup_t	*pickup;
	int			clientNum;
	int			itemNum;
	int			freeSlot;
	int			i;

	if ( !es ) {
		return;
	}

	clientNum = es->groundEntityNum - 1;
	itemNum = es->clientNum;
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return;
	}

	if ( itemNum <= 0 || itemNum >= bg_numItems ) {
		return;
	}

	if ( CG_GetSpectatorItemPickupMask( &bg_itemlist[itemNum] ) == 0 ) {
		return;
	}

	pickup = NULL;
	freeSlot = -1;
	for ( i = 0; i < CG_SPECTATOR_ITEM_PICKUP_COUNT; i++ ) {
		if ( cg.spectatorItemPickups[i].clientNum == clientNum ) {
			pickup = &cg.spectatorItemPickups[i];
			break;
		}

		if ( freeSlot < 0 && cg.spectatorItemPickups[i].clientNum < 0 ) {
			freeSlot = i;
		}
	}

	if ( !pickup ) {
		if ( freeSlot < 0 ) {
			return;
		}

		pickup = &cg.spectatorItemPickups[freeSlot];
		cg.spectatorItemPickupCount++;
	}

	pickup->clientNum = clientNum;
	pickup->palette = es->constantLight;
	pickup->itemNum = itemNum;
	pickup->remainingTime = (int)es->origin[0] - cg.time;
	pickup->duelLayout = (int)es->origin[1];
	pickup->layoutOrder = es->frame * ( ( es->loopSound > 0 ) ? 2 : 1 );
	VectorCopy( es->pos.trBase, pickup->origin );
	if ( pickup->remainingTime < 0 ) {
		pickup->remainingTime = 0;
	}
}

/*
=============
CG_UpdateSpectatorItemPickups

Maintains and sorts the cached spectator pickup rows once per frame.
=============
*/
void CG_UpdateSpectatorItemPickups( void ) {
	int			i;
	int			liveCount;
	cgSpectatorItemPickup_t	activePickups[CG_SPECTATOR_ITEM_PICKUP_COUNT];

	if ( !CG_IsSpectatorItemPickupModeActive() ) {
		CG_ClearSpectatorItemPickups();
		return;
	}

	liveCount = 0;
	for ( i = 0; i < CG_SPECTATOR_ITEM_PICKUP_COUNT; i++ ) {
		cgSpectatorItemPickup_t	pickup;

		if ( cg.spectatorItemPickups[i].clientNum < 0 ) {
			continue;
		}

		pickup = cg.spectatorItemPickups[i];
		if ( !cg_paused.integer ) {
			pickup.remainingTime -= cg.frametime;
		}

		if ( pickup.remainingTime <= 0 ) {
			continue;
		}

		activePickups[liveCount++] = pickup;
	}

	CG_ClearSpectatorItemPickups();
	if ( liveCount == 0 ) {
		return;
	}

	if ( liveCount > 1 ) {
		qsort( activePickups, liveCount, sizeof( activePickups[0] ), CG_CompareSpectatorItemPickups );
	}

	memcpy( cg.spectatorItemPickups, activePickups, sizeof( activePickups[0] ) * liveCount );
	cg.spectatorItemPickupCount = liveCount;
	for ( i = liveCount; i < CG_SPECTATOR_ITEM_PICKUP_COUNT; i++ ) {
		cg.spectatorItemPickups[i].clientNum = -1;
	}
}

/*
=============
CG_DrawSpectatorItemPickups

Draws the retail spectator major-item timer overlay beneath the upper-right slab.
=============
*/
static void CG_DrawSpectatorItemPickups( void ) {
	int			i;
	int			leftIndex;
	int			rightIndex;
	float		x;
	float		y;
	float		size;
	float		scale;
	char		timerText[16];

	if ( cg_specItemTimers.integer <= 0 || cg.spectatorItemPickupCount <= 0 ) {
		return;
	}

	if ( !CG_IsSpectatorItemPickupModeActive() ) {
		return;
	}

	size = cg_specItemTimersSize.value * 100.0f;
	if ( size < 1.0f ) {
		size = 1.0f;
	}

	scale = cg_specItemTimersSize.value;
	if ( scale <= 0.0f ) {
		scale = 0.24f;
	}

	x = cg_specItemTimersX.value;
	if ( x == 0.0f ) {
		x = 640.0f - size - 4.0f;
	}

	y = cg_specItemTimersY.value;
	if ( y == 0.0f ) {
		y = cg_spectatorItemPickupBaseY;
	}

	leftIndex = 0;
	rightIndex = 0;
	for ( i = 0; i < cg.spectatorItemPickupCount; i++ ) {
		const cgSpectatorItemPickup_t	*pickup;
		const gitem_t			*item;
		qhandle_t			icon;
		float				drawX;
		float				drawY;
		int				seconds;

		pickup = &cg.spectatorItemPickups[i];
		if ( !CG_IsSpectatorItemPickupVisible( pickup ) ) {
			continue;
		}

		item = &bg_itemlist[pickup->itemNum];
		icon = item->icon ? trap_R_RegisterShader( item->icon ) : 0;
		if ( !icon ) {
			icon = cgs.media.deferShader;
		}

		drawX = x;
		drawY = y;
		if ( pickup->duelLayout && ( pickup->palette == 1 || pickup->palette == 2 ) ) {
			vec4_t	color;
			int	columnIndex;

			columnIndex = ( pickup->palette == 1 ) ? leftIndex++ : rightIndex++;
			drawX = ( pickup->palette == 1 ) ? ( x - size * 1.2f ) : x;
			drawY = y + columnIndex * ( size * 1.1f );
			CG_GetSpectatorItemPickupPaletteColor( pickup->palette, color );
			CG_FillRect( drawX, drawY, size, size, color );
		} else {
			y += size + 4.0f;
		}

		CG_DrawPic( drawX, drawY, size, size, icon );

		seconds = ( pickup->remainingTime + 999 ) / 1000;
		if ( seconds > 0 ) {
			Com_sprintf( timerText, sizeof( timerText ), "%d", seconds );
			CG_Text_PaintNoAdjust( drawX + size + 4.0f, drawY + size - 5.0f, scale, colorWhite,
				timerText, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
		}
	}
}


/*
=====================
CG_DrawUpperRightStack

=====================
*/
static float CG_DrawUpperRightStack( float y ) {
	if ( cgs.gametype >= GT_TEAM && cg_drawTeamOverlay.integer == 1 ) {
		y = CG_DrawTeamOverlay( y, qtrue, qtrue );
	}
	if ( cg_drawSnapshot.integer ) {
		y = CG_DrawSnapshot( y );
	}
	if ( cg_drawFPS.integer ) {
		y = CG_DrawFPS( y );
	}
	if ( cg_drawAttacker.integer ) {
		y = CG_DrawAttacker( y );
	}

	return y;
}

/*
=====================
CG_DrawUpperRight

=====================
*/
static void CG_DrawUpperRight( void ) {
	cg_spectatorItemPickupBaseY = CG_DrawUpperRightStack( 0.0f );
}

/*
===========================================================================================

  LOWER RIGHT CORNER

===========================================================================================
*/

/*
=================
CG_DrawScores

Draw the small two score display
=================
*/

/*
================
CG_DrawPowerups
================
*/
/*
=============
CG_CountActiveTimedPowerups

Counts the active timed powerups on the current playerstate for the lower-right
stack count popup.
=============
*/
static int CG_CountActiveTimedPowerups( const playerState_t *ps ) {
	int	i;
	int	count;

	if ( !ps ) {
		return 0;
	}

	count = 0;
	for ( i = 0; i < MAX_POWERUPS; i++ ) {
		if ( ps->powerups[i] <= cg.time || ps->powerups[i] >= 999000 ) {
			continue;
		}

		if ( !BG_FindItemForPowerup( i ) ) {
			continue;
		}

		count++;
	}

	return count;
}

/*
=============
CG_DrawPowerups

Restores the retail lower-right powerup popup around the mirrored
`cg.powerupActive` / `cg.powerupTime` seam.
=============
*/
static float CG_DrawPowerups( float y ) {
	playerState_t	*ps;
	gitem_t		*item;
	char		powerupTimeText[16];
	char		stackText[16];
	float		*color;
	float		scale;
	float		textY;
	float		x;
	int		msec;
	int		seconds;
	int		mins;
	int		tens;
	int		textWidth;
	int		activeCount;
	qhandle_t	icon;

	y -= 48.0f;

	if ( !cg.snap ) {
		return y;
	}

	ps = &cg.snap->ps;
	if ( cg.showScores || cg.warmup || ps->stats[STAT_HEALTH] < 1 ) {
		return y;
	}

	if ( cg.powerupActive <= PW_NONE || cg.powerupActive >= PW_NUM_POWERUPS ) {
		return y;
	}

	if ( ps->powerups[cg.powerupActive] <= cg.time || ps->powerups[cg.powerupActive] >= 999000 ) {
		return y;
	}

	color = CG_FadeColor( cg.powerupTime, 3000 );
	if ( !color ) {
		cg.powerupActive = PW_NONE;
		return y;
	}

	item = BG_FindItemForPowerup( cg.powerupActive );
	if ( !item ) {
		return y;
	}

	msec = ps->powerups[cg.powerupActive] - cg.time;
	seconds = msec / 1000;
	mins = seconds / 60;
	seconds -= mins * 60;
	tens = seconds / 10;
	seconds -= tens * 10;
	Com_sprintf( powerupTimeText, sizeof( powerupTimeText ), "%i:%i%i", mins, tens, seconds );

	scale = 0.28f;
	textY = y + (float)CG_Text_Height( powerupTimeText, scale, 0 );
	CG_Text_Paint( 5.0f, textY, scale, color, powerupTimeText, 0, 0, ITEM_TEXTSTYLE_SHADOWED );

	textWidth = CG_Text_Width( powerupTimeText, scale, 0 );
	x = (float)textWidth + 13.0f;

	icon = CG_ItemBackedPowerupIcon( cg.powerupActive );
	if ( !icon ) {
		icon = trap_R_RegisterShader( item->icon );
	}
	if ( icon ) {
		CG_DrawPic( x, y, 16.0f, 16.0f, icon );
		x += 24.0f;
	}

	CG_Text_Paint( x, y + (float)CG_Text_Height( item->pickup_name, scale, 0 ), scale, color, item->pickup_name, 0, 0, ITEM_TEXTSTYLE_SHADOWED );
	x += (float)CG_Text_Width( item->pickup_name, scale, 0 ) + 8.0f;

	activeCount = CG_CountActiveTimedPowerups( ps );
	if ( activeCount > 1 ) {
		Com_sprintf( stackText, sizeof( stackText ), "x%i", activeCount );
		CG_Text_Paint( x, y + (float)CG_Text_Height( stackText, scale, 0 ), scale, color, stackText, 0, 0, ITEM_TEXTSTYLE_SHADOWED );
	}

	return y;
}

/*
=============
CG_DrawSpeedometer

Rebuilds the retail classic-HUD speedometer graph and label ahead of the
legacy corner stacks.
=============
*/
static void CG_DrawSpeedometer( void ) {
	static const vec4_t speedFillColor = { 0.2f, 0.85f, 0.2f, 0.75f };
	static const vec4_t speedOverflowColor = { 1.0f, 0.82f, 0.2f, 0.85f };
	static const vec4_t speedBackColor = { 0.0f, 0.0f, 0.0f, 0.35f };
	char		speedText[16];
	float		graphX;
	float		graphY;
	float		graphWidth;
	float		graphHeight;
	float		barWidth;
	float		barScale;
	float		halfHeight;
	float		barHeight;
	float		fullHeight;
	float		overflowHeight;
	float		textScale;
	float		textX;
	float		textY;
	float		currentSpeed;
	int		mode;
	int		sampleCount;
	int		sampleIndex;
	int		i;

	if ( !CG_ShouldDrawSpeedometer() || !cg.snap ) {
		return;
	}

	if ( cg.showScores || cg.warmup || cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return;
	}

	mode = cg_speedometer.integer;
	if ( mode <= 0 ) {
		return;
	}

	CG_RecordSpeedometerSample();
	if ( cg_speedometerHistoryCount <= 0 || cg_speedometerHistoryHead < 0 ) {
		return;
	}

	if ( mode < 2 ) {
		graphX = 592.0f;
		graphY = 384.0f;
		graphWidth = 48.0f;
		graphHeight = 48.0f;
		textScale = 0.25f;
		CG_FillRect( graphX, graphY, graphWidth, graphHeight, speedBackColor );
	} else {
		graphX = 256.0f;
		graphY = 241.0f;
		graphWidth = 128.0f;
		graphHeight = 32.0f;
		textScale = 0.15f;
	}

	barWidth = graphWidth * ( 1.0f / (float)CG_SPEEDOMETER_HISTORY_SAMPLES );
	barScale = ( graphHeight - 5.0f ) / CG_SPEEDOMETER_RANGE;
	halfHeight = graphHeight * 0.5f;
	sampleCount = cg_speedometerHistoryCount;
	if ( sampleCount > CG_SPEEDOMETER_HISTORY_SAMPLES ) {
		sampleCount = CG_SPEEDOMETER_HISTORY_SAMPLES;
	}

	if ( mode < 3 ) {
		for ( i = 0; i < sampleCount; i++ ) {
			sampleIndex = ( cg_speedometerHistoryHead - sampleCount + 1 + i + CG_SPEEDOMETER_HISTORY_SAMPLES ) & ( CG_SPEEDOMETER_HISTORY_SAMPLES - 1 );
			currentSpeed = cg_speedometerHistory[sampleIndex];
			if ( currentSpeed <= 0.0f ) {
				continue;
			}

			fullHeight = currentSpeed * barScale;
			barHeight = fullHeight;
			if ( barHeight > halfHeight ) {
				barHeight = halfHeight;
			}

			CG_FillRect(
				graphX + barWidth * (float)i,
				graphY + graphHeight - barHeight,
				barWidth,
				barHeight,
				speedFillColor
			);

			if ( fullHeight > halfHeight ) {
				overflowHeight = fullHeight - barHeight;
				if ( overflowHeight > halfHeight ) {
					overflowHeight = halfHeight;
				}

				CG_FillRect(
					graphX + barWidth * (float)i,
					graphY + graphHeight - barHeight - overflowHeight,
					barWidth,
					overflowHeight,
					speedOverflowColor
				);
			}
		}
	}

	currentSpeed = cg_speedometerHistory[cg_speedometerHistoryHead];
	Com_sprintf( speedText, sizeof( speedText ), "%i", (int)currentSpeed );
	textX = graphX + ( graphWidth - CG_Text_Width( speedText, textScale, 0 ) ) * 0.5f;
	textY = graphY + graphHeight + ( mode < 2 ? 14.0f : 8.0f );
	CG_Text_Paint( textX, textY, textScale, colorWhite, speedText, 0, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
}

/*
=====================
CG_DrawLowerRight

=====================
*/
/*
=====================
CG_DrawLowerRight

Rebuilds the retail lower-right wrapper around the existing team overlay seam
and the restored powerup popup helper.
=====================
*/
static void CG_DrawLowerRight( void ) {
	float	y;

	y = 408.0f;
	if ( cgs.gametype >= GT_TEAM && cg_drawTeamOverlay.integer == 3 ) {
		y = CG_DrawTeamOverlay( y, qtrue, qfalse );
	}

	CG_DrawPowerups( y );
}

/*
===================
CG_DrawPickupItem
===================
*/
/*
=============
CG_FormatPickupTimestamp

Formats the timestamped pickup prefix as the retail notify/chat `m:ss.mmm`
clock wrapped in brackets.
=============
*/
static void CG_FormatPickupTimestamp( int milliseconds, char *buffer, size_t bufferSize ) {
	int	minutes;
	int	seconds;
	int	ms;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	if ( milliseconds < 0 ) {
		milliseconds = 0;
	}

	minutes = milliseconds / 60000;
	seconds = ( milliseconds % 60000 ) / 1000;
	ms = milliseconds % 1000;
	Com_sprintf( buffer, bufferSize, "[%i:%02i.%03i]", minutes, seconds, ms );
}

/*
=============
CG_DrawPickupItem

Restores the Quake Live pickup notification bitmask controlled by
`cg_drawItemPickups`: icon, text, and optional timestamp prefix.
=============
*/
static int CG_DrawPickupItem( int y ) {
	int			value;
	float		*fadeColor;
	const gitem_t	*item;
	qboolean		drawIcon;
	qboolean		drawText;
	qboolean		drawTimestamp;
	int			x;
	char			timestampText[32];

	if ( cg.snap->ps.stats[STAT_HEALTH] <= 0 ) {
		return y;
	}

	if ( cg_drawItemPickups.integer <= 0 ) {
		return y;
	}

	value = cg.itemPickup;
	if ( value <= 0 || value >= bg_numItems ) {
		return y;
	}

	item = &bg_itemlist[value];
	if ( !item->pickup_name || !item->pickup_name[0] ) {
		return y;
	}

	fadeColor = CG_FadeColor( cg.itemPickupTime, 3000 );
	if ( !fadeColor ) {
		return y;
	}

	drawIcon = (qboolean)( ( cg_drawItemPickups.integer & 1 ) != 0 );
	drawText = (qboolean)( ( cg_drawItemPickups.integer & 2 ) != 0 );
	drawTimestamp = (qboolean)( ( cg_drawItemPickups.integer & 4 ) != 0 );
	if ( !drawIcon && !drawText && !drawTimestamp ) {
		return y;
	}

	y -= ICON_SIZE;
	x = 8;

	if ( drawTimestamp ) {
		CG_FormatPickupTimestamp( cg.itemPickupTime, timestampText, sizeof( timestampText ) );
		CG_DrawSmallStringColor( x, y + ( ICON_SIZE - SMALLCHAR_HEIGHT ) / 2, timestampText, fadeColor );
		x += CG_DrawStrlen( timestampText ) * SMALLCHAR_WIDTH + 8;
	}

	if ( drawIcon ) {
		CG_RegisterItemVisuals( value );
		if ( cg_items[value].icon ) {
			trap_R_SetColor( fadeColor );
			CG_DrawPic( x, y, ICON_SIZE, ICON_SIZE, cg_items[value].icon );
			trap_R_SetColor( NULL );
		}
		x += ICON_SIZE + 8;
	}

	if ( drawText ) {
		CG_DrawBigStringColor( x, y + ( ICON_SIZE / 2 - BIGCHAR_HEIGHT / 2 ), item->pickup_name, fadeColor );
	}

	return y;
}

/*
=====================
CG_DrawLowerLeft

=====================
*/
/*
=============
CG_DrawLowerLeft

Draws the retail pickup notification stack in the lower-left corner when the
classic HUD path is active.
=============
*/
static void CG_DrawLowerLeft( void ) {
	int	y;

	y = 480 - ICON_SIZE;
	CG_DrawPickupItem( y );
}


//===========================================================================================

/*
=================
CG_DrawTeamInfo
=================
*/
/*
=============
CG_GetTeamInfoArmorColor

Returns the armor color tier for the fixed team info bars.
=============
*/
static void CG_GetTeamInfoArmorColor( int armor, vec4_t color ) {
	if ( armor >= 150 ) {
		color[0] = 0.9f;
		color[1] = 0.15f;
		color[2] = 0.15f;
		color[3] = 1.0f;
	} else if ( armor >= 100 ) {
		color[0] = 0.95f;
		color[1] = 0.75f;
		color[2] = 0.2f;
		color[3] = 1.0f;
	} else if ( armor > 0 ) {
		color[0] = 0.2f;
		color[1] = 0.8f;
		color[2] = 0.2f;
		color[3] = 1.0f;
	} else {
		color[0] = 0.4f;
		color[1] = 0.4f;
		color[2] = 0.4f;
		color[3] = 0.6f;
	}
}

/*
=============
CG_TeamInfoBarFraction

Normalizes a team-info stat value into the retail 0-200 bar range.
=============
*/
static float CG_TeamInfoBarFraction( int value ) {
	return Com_Clamp( 0.0f, 200.0f, (float)value ) * ( 1.0f / 200.0f );
}

/*
=============
CG_DrawTeamInfoBar

Draws one retail-style team info stat bar, falling back to a solid fill if
the Quake Live HUD shader isn't available.
=============
*/
static void CG_DrawTeamInfoBar( float x, float y, float width, float height, float fraction, qhandle_t shader, const vec4_t color ) {
	float	drawX;
	float	drawY;
	float	drawW;
	float	drawH;

	if ( width <= 0.0f || height <= 0.0f || fraction <= 0.0f ) {
		return;
	}

	if ( fraction > 1.0f ) {
		fraction = 1.0f;
	}

	if ( shader ) {
		drawX = x;
		drawY = y;
		drawW = width * fraction;
		drawH = height;
		CG_AdjustFrom640( &drawX, &drawY, &drawW, &drawH );
		trap_R_SetColor( color );
		trap_R_DrawStretchPic( drawX, drawY, drawW, drawH, 0.0f, 0.0f, fraction, 1.0f, shader );
		trap_R_SetColor( NULL );
	} else {
		CG_FillRect( x, y, width * fraction, height, color );
	}
}

/*
=============
CG_TeamInfoLocation

Returns the team info location text, mirroring the retail "unknown" fallback.
=============
*/
static const char *CG_TeamInfoLocation( const clientInfo_t *ci ) {
	const char	*location;

	if ( !ci || ci->location <= 0 ) {
		return "unknown";
	}

	location = CG_ConfigString( CS_LOCATIONS + ci->location );
	if ( !location || !location[0] ) {
		return "unknown";
	}

	return location;
}

/*
=============
CG_TeamInfoCarryIcon

Returns the leading carry or powerup icon used by the fixed team info slab.
=============
*/
static qhandle_t CG_TeamInfoCarryIcon( const clientInfo_t *ci ) {
	static const int powerups[] = {
		PW_REDFLAG,
		PW_BLUEFLAG,
		PW_NEUTRALFLAG,
		PW_QUAD,
		PW_BATTLESUIT,
		PW_REGEN,
		PW_HASTE,
		PW_INVIS
	};
	int	i;

	if ( !ci ) {
		return 0;
	}

	for ( i = 0; i < ARRAY_LEN( powerups ); i++ ) {
		if ( ci->powerups & ( 1 << powerups[i] ) ) {
			return CG_ItemBackedPowerupIcon( powerups[i] );
		}
	}

	return 0;
}

/*
=============
CG_HasActiveTeamScoreRows

Returns true when the mirrored score list still carries usable team rows for
the fixed overlay fallback path.
=============
*/
static qboolean CG_HasActiveTeamScoreRows( void ) {
	int				i;
	const score_t	*score;

	for ( i = 0; i < cg.numScores; i++ ) {
		score = &cg.scores[i];
		if ( score->client < 0 || score->client >= MAX_CLIENTS ) {
			continue;
		}
		if ( !cgs.clientinfo[score->client].infoValid ) {
			continue;
		}
		if ( score->team == TEAM_RED || score->team == TEAM_BLUE ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CG_ShouldDrawTeamInfo

Gates the fixed retail team info slab on the reconstructed cvar and team-mode
transport surfaces.
=============
*/
static qboolean CG_ShouldDrawTeamInfo( void ) {
	if ( !cg.snap ) {
		return qfalse;
	}

	if ( cg_drawTeamOverlay.integer <= 0 || cgs.gametype < GT_TEAM ) {
		return qfalse;
	}

	if ( numSortedTeamPlayers > 0 ) {
		return qtrue;
	}

	return CG_HasActiveTeamScoreRows();
}

/*
=============
CG_DrawTeamInfoRow

Paints one fixed-position retail team-info row, mirroring the recovered 16px
icon cadence, stat bars, and clipped name/location text layout.
=============
*/
static void CG_DrawTeamInfoRow( const clientInfo_t *ci, team_t team, float y ) {
	char		nameText[MAX_NAME_LENGTH];
	char		locationText[MAX_QPATH];
	vec4_t		healthColor;
	vec4_t		armorColor;
	vec4_t		backColor;
	vec4_t		textColor;
	qhandle_t	carryIcon;
	qhandle_t	taskIcon;
	float		nameWidth;
	float		locationWidth;
	float		panelLeft;
	float		panelRight;
	float		iconX;
	float		taskX;
	float		barX;
	float		textStartX;
	float		textRight;
	float		textAvailable;
	float		locationX;
	float		nameX;

	if ( !ci || !ci->infoValid ) {
		return;
	}

	panelLeft = ( team == TEAM_RED ) ? 5.0f : 320.0f;
	panelRight = ( team == TEAM_RED ) ? 315.0f : 635.0f;
	backColor[0] = 0.0f;
	backColor[1] = 0.0f;
	backColor[2] = 0.0f;
	backColor[3] = 0.35f;
	textColor[0] = 1.0f;
	textColor[1] = 1.0f;
	textColor[2] = 1.0f;
	textColor[3] = 1.0f;

	CG_GetColorForHealth( ci->health, ci->armor, healthColor );
	healthColor[3] = 1.0f;
	CG_GetTeamInfoArmorColor( ci->armor, armorColor );
	armorColor[3] = 1.0f;

	if ( team == TEAM_RED ) {
		iconX = panelLeft;
		taskX = iconX + 18.0f;
		barX = taskX + 18.0f;
		textStartX = barX + 70.0f;
		textRight = panelRight;
	} else {
		iconX = panelRight - 16.0f;
		taskX = iconX - 18.0f;
		barX = taskX - 66.0f;
		textStartX = panelLeft;
		textRight = barX - 4.0f;
	}

	textAvailable = textRight - textStartX;
	if ( textAvailable < 32.0f ) {
		textAvailable = 32.0f;
	}

	CG_TrimTeammatePOILabelToWidth( ci->name, nameText, sizeof( nameText ), 0.18f, textAvailable * 0.55f );
	CG_TrimTeammatePOILabelToWidth( CG_TeamInfoLocation( ci ), locationText, sizeof( locationText ), 0.18f, textAvailable * 0.40f );
	nameWidth = (float)CG_Text_Width( nameText, 0.18f, 0 );
	locationWidth = (float)CG_Text_Width( locationText, 0.18f, 0 );

	if ( team == TEAM_RED ) {
		nameX = textStartX;
		locationX = textRight - locationWidth;
		if ( locationX < nameX + nameWidth + 4.0f ) {
			locationX = nameX + nameWidth + 4.0f;
		}
	} else {
		locationX = textRight - locationWidth;
		nameX = locationX - nameWidth - 4.0f;
		if ( nameX < textStartX ) {
			nameX = textStartX;
		}
	}

	CG_FillRect( barX, y + 3.0f, 64.0f, 6.0f, backColor );
	CG_FillRect( barX, y + 11.0f, 64.0f, 6.0f, backColor );
	CG_DrawTeamInfoBar( barX, y + 3.0f, 64.0f, 6.0f, CG_TeamInfoBarFraction( ci->health ), cgs.media.healthBar200, healthColor );
	CG_DrawTeamInfoBar( barX, y + 11.0f, 64.0f, 6.0f, CG_TeamInfoBarFraction( ci->armor ), cgs.media.armorBar200, armorColor );

	carryIcon = CG_TeamInfoCarryIcon( ci );
	if ( carryIcon ) {
		CG_DrawPic( iconX, y, 16.0f, 16.0f, carryIcon );
	}

	taskIcon = CG_StatusHandle( ci->teamTask );
	if ( taskIcon ) {
		CG_DrawPic( taskX, y, 16.0f, 16.0f, taskIcon );
	}

	if ( cg.snap && ci == &cgs.clientinfo[cg.snap->ps.clientNum] ) {
		CG_DrawRect( iconX - 1.0f, y - 1.0f, 18.0f, 18.0f, 1.0f, colorWhite );
	}

	CG_Text_PaintNoAdjust( nameX, y + 18.0f, 0.18f, textColor, nameText, 0, ITEM_TEXTSTYLE_SHADOWED );
	CG_Text_PaintNoAdjust( locationX, y + 18.0f, 0.18f, textColor, locationText, 0, ITEM_TEXTSTYLE_SHADOWED );
}

/*
=================
CG_DrawTeamInfo
=================
*/
static void CG_DrawTeamInfo( void ) {
	float			teamY[TEAM_NUM_TEAMS];
	int				i;
	const score_t	*score;
	const clientInfo_t	*ci;

	if ( !CG_ShouldDrawTeamInfo() ) {
		return;
	}

	memset( teamY, 0, sizeof( teamY ) );

	if ( numSortedTeamPlayers > 0 ) {
		for ( i = 0; i < numSortedTeamPlayers; i++ ) {
			ci = &cgs.clientinfo[sortedTeamPlayers[i]];
			if ( !ci->infoValid ) {
				continue;
			}
			if ( ci->team != TEAM_RED && ci->team != TEAM_BLUE ) {
				continue;
			}

			CG_DrawTeamInfoRow( ci, ci->team, teamY[ci->team] );
			teamY[ci->team] += 22.0f;
		}
		return;
	}

	for ( i = 0; i < cg.numScores; i++ ) {
		score = &cg.scores[i];
		if ( score->client < 0 || score->client >= MAX_CLIENTS ) {
			continue;
		}
		if ( score->team != TEAM_RED && score->team != TEAM_BLUE ) {
			continue;
		}

		ci = &cgs.clientinfo[score->client];
		if ( !ci->infoValid ) {
			continue;
		}

		CG_DrawTeamInfoRow( ci, score->team, teamY[score->team] );
		teamY[score->team] += 22.0f;
	}
}

/*
===================
CG_DrawHoldableItem
===================
*/

/*
===================
CG_DrawPersistantPowerup
===================
*/
#if 0 // sos001208 - DEAD
static void CG_DrawPersistantPowerup( void ) { 
	int		value;

	value = cg.snap->ps.stats[STAT_PERSISTANT_POWERUP];
	if ( value ) {
		CG_RegisterItemVisuals( value );
		CG_DrawPic( 640-ICON_SIZE, (SCREEN_HEIGHT-ICON_SIZE)/2 - ICON_SIZE, ICON_SIZE, ICON_SIZE, cg_items[ value ].icon );
	}
}
#endif


/*
===================
CG_DrawReward
===================
*/
static void CG_DrawReward( void ) { 
	float	*color;
	int		i, count;
	float	x, y;
	char	buf[32];

	if ( !cg_drawRewards.integer ) {
		return;
	}

	color = CG_FadeColor( cg.rewardTime, REWARD_TIME );
	if ( !color ) {
		if (cg.rewardStack > 0) {
			for(i = 0; i < cg.rewardStack; i++) {
				cg.rewardSound[i] = cg.rewardSound[i+1];
				cg.rewardShader[i] = cg.rewardShader[i+1];
				cg.rewardCount[i] = cg.rewardCount[i+1];
			}
			cg.rewardTime = cg.time;
			cg.rewardStack--;
			color = CG_FadeColor( cg.rewardTime, REWARD_TIME );
			if ( cg.rewardSound[0] ) {
				trap_S_StartLocalSound( cg.rewardSound[0], CHAN_ANNOUNCER );
			}
		} else {
			return;
		}
	}

	trap_R_SetColor( color );

	/*
	count = cg.rewardCount[0]/10;				// number of big rewards to draw

	if (count) {
		y = 4;
		x = 320 - count * ICON_SIZE;
		for ( i = 0 ; i < count ; i++ ) {
			CG_DrawPic( x, y, (ICON_SIZE*2)-4, (ICON_SIZE*2)-4, cg.rewardShader[0] );
			x += (ICON_SIZE*2);
		}
	}

	count = cg.rewardCount[0] - count*10;		// number of small rewards to draw
	*/

	count = cg.rewardCount[0];
	if (count > 0) {
		int rowSize = cg_drawRewardsRowSize.integer;
		float iconSize = ICON_SIZE - 4.0f;
		float padding = ICON_SIZE;
		rowSize = Com_Clamp(1, MAX_REWARDSTACK, rowSize);

		y = 56;
		{
			int fullRows = (count + rowSize - 1) / rowSize;
			for (i = 0; i < count; i++) {
				int row = i / rowSize;
				int col = i % rowSize;
				int rowColumns = (row == fullRows - 1 && (count % rowSize)) ? (count % rowSize) : rowSize;
				float totalWidth = rowColumns * padding;
				float baseX = 320.0f - totalWidth * 0.5f;
				x = baseX + col * padding;
				CG_DrawPic( x, y + row * padding, iconSize, iconSize, cg.rewardShader[0] );
			}
		}

		if ( count >= 10 ) {
			Com_sprintf(buf, sizeof(buf), "%d", count);
			x = ( SCREEN_WIDTH - SMALLCHAR_WIDTH * CG_DrawStrlen( buf ) ) / 2;
			CG_DrawStringExt( x, y + iconSize + SMALLCHAR_HEIGHT, buf, color, qfalse, qtrue,
				SMALLCHAR_WIDTH, SMALLCHAR_HEIGHT, 0 );
		}
	}
	trap_R_SetColor( NULL );
}


/*
===============================================================================

LAGOMETER

===============================================================================
*/

#define	LAG_SAMPLES		128


typedef struct {
	int		frameSamples[LAG_SAMPLES];
	int		frameCount;
	int		snapshotFlags[LAG_SAMPLES];
	int		snapshotSamples[LAG_SAMPLES];
	int		snapshotCount;
} lagometer_t;

lagometer_t		lagometer;

/*
==============
CG_AddLagometerFrameInfo

Adds the current interpolate / extrapolate bar for this frame
==============
*/
void CG_AddLagometerFrameInfo( void ) {
	int			offset;

	offset = cg.time - cg.latestSnapshotTime;
	lagometer.frameSamples[ lagometer.frameCount & ( LAG_SAMPLES - 1) ] = offset;
	lagometer.frameCount++;
}

/*
==============
CG_AddLagometerSnapshotInfo

Each time a snapshot is received, log its ping time and
the number of snapshots that were dropped before it.

Pass NULL for a dropped packet.
==============
*/
void CG_AddLagometerSnapshotInfo( snapshot_t *snap ) {
	// dropped packet
	if ( !snap ) {
		lagometer.snapshotSamples[ lagometer.snapshotCount & ( LAG_SAMPLES - 1) ] = -1;
		lagometer.snapshotCount++;
		return;
	}

	// add this snapshot's info
	lagometer.snapshotSamples[ lagometer.snapshotCount & ( LAG_SAMPLES - 1) ] = snap->ping;
	lagometer.snapshotFlags[ lagometer.snapshotCount & ( LAG_SAMPLES - 1) ] = snap->snapFlags;
	lagometer.snapshotCount++;
}

/*
==============
CG_DrawDisconnect

Should we draw something differnet for long lag vs no packets?
==============
*/
static void CG_DrawDisconnect( void ) {
	float		x, y;
	int			cmdNum;
	usercmd_t	cmd;
	const char		*s;
	int			w;  // bk010215 - FIXME char message[1024];
	qhandle_t	netShader;

	// draw the phone jack if we are completely past our buffers
	cmdNum = trap_GetCurrentCmdNumber() - CMD_BACKUP + 1;
	trap_GetUserCmd( cmdNum, &cmd );
	if ( cmd.serverTime <= cg.snap->ps.commandTime
		|| cmd.serverTime > cg.time ) {	// special check for map_restart // bk 0102165 - FIXME
		return;
	}

	// also add text in center of screen
	s = "Connection Interrupted"; // bk 010215 - FIXME
	w = CG_DrawStrlen( s ) * BIGCHAR_WIDTH;
	CG_DrawBigString( 320 - w/2, 100, s, 1.0F);

	// blink the icon
	if ( ( cg.time >> 9 ) & 1 ) {
		return;
	}

	x = 640 - 48;
	y = 480 - 48;
	netShader = trap_R_RegisterShader( "gfx/2d/net.tga" );
	CG_DrawPic( x, y, 48, 48, netShader );
}


#define	MAX_LAGOMETER_PING	900
#define	MAX_LAGOMETER_RANGE	300

/*
==============
CG_DrawLagometer
==============
*/
static void CG_DrawLagometer( void ) {
	int		a, x, y, i;
	float	v;
	float	ax, ay, aw, ah, mid, range;
	int		color;
	float	vscale;

	if ( !cg_lagometer.integer || cgs.localServer || cg.renderingThirdPerson ) {
		return;
	}

	//
	// draw the graph
	//
	x = 640 - 48;
	y = 480 - 144;

	trap_R_SetColor( NULL );
	CG_DrawPic( x, y, 48, 48, cgs.media.lagometerShader );

	ax = x;
	ay = y;
	aw = 48;
	ah = 48;
	CG_AdjustFrom640( &ax, &ay, &aw, &ah );

	color = -1;
	range = ah / 3;
	mid = ay + range;

	vscale = range / MAX_LAGOMETER_RANGE;

	// draw the frame interpoalte / extrapolate graph
	for ( a = 0 ; a < aw ; a++ ) {
		i = ( lagometer.frameCount - 1 - a ) & (LAG_SAMPLES - 1);
		v = lagometer.frameSamples[i];
		v *= vscale;
		if ( v > 0 ) {
			if ( color != 1 ) {
				color = 1;
				trap_R_SetColor( g_color_table[ColorIndex(COLOR_YELLOW)] );
			}
			if ( v > range ) {
				v = range;
			}
			trap_R_DrawStretchPic ( ax + aw - a, mid - v, 1, v, 0, 0, 0, 0, cgs.media.whiteShader );
		} else if ( v < 0 ) {
			if ( color != 2 ) {
				color = 2;
				trap_R_SetColor( g_color_table[ColorIndex(COLOR_BLUE)] );
			}
			v = -v;
			if ( v > range ) {
				v = range;
			}
			trap_R_DrawStretchPic( ax + aw - a, mid, 1, v, 0, 0, 0, 0, cgs.media.whiteShader );
		}
	}

	// draw the snapshot latency / drop graph
	range = ah / 2;
	vscale = range / MAX_LAGOMETER_PING;

	for ( a = 0 ; a < aw ; a++ ) {
		i = ( lagometer.snapshotCount - 1 - a ) & (LAG_SAMPLES - 1);
		v = lagometer.snapshotSamples[i];
		if ( v > 0 ) {
			if ( lagometer.snapshotFlags[i] & SNAPFLAG_RATE_DELAYED ) {
				if ( color != 5 ) {
					color = 5;	// YELLOW for rate delay
					trap_R_SetColor( g_color_table[ColorIndex(COLOR_YELLOW)] );
				}
			} else {
				if ( color != 3 ) {
					color = 3;
					trap_R_SetColor( g_color_table[ColorIndex(COLOR_GREEN)] );
				}
			}
			v = v * vscale;
			if ( v > range ) {
				v = range;
			}
			trap_R_DrawStretchPic( ax + aw - a, ay + ah - v, 1, v, 0, 0, 0, 0, cgs.media.whiteShader );
		} else if ( v < 0 ) {
			if ( color != 4 ) {
				color = 4;		// RED for dropped snapshots
				trap_R_SetColor( g_color_table[ColorIndex(COLOR_RED)] );
			}
			trap_R_DrawStretchPic( ax + aw - a, ay + ah - range, 1, range, 0, 0, 0, 0, cgs.media.whiteShader );
		}
	}

	trap_R_SetColor( NULL );

	if ( cg_nopredict.integer || cg_synchronousClients.integer ) {
		CG_DrawBigString( ax, ay, "snc", 1.0 );
	}
}



/*
===============================================================================

CENTER PRINTING

===============================================================================
*/


/*
==============
CG_CenterPrint

Called for important messages that should stay in the center of the screen
for a few moments.
==============
*/
void CG_CenterPrint( const char *str, int y, float scale ) {
	char	*s;

	Q_strncpyz( cg.centerPrint, str, sizeof(cg.centerPrint) );

	cg.centerPrintTime = cg.time;
	if ( cgs.gametype == GT_RACE ) {
		cg.centerPrintY = y + 10;
	} else {
		cg.centerPrintY = y;
	}
	cg.centerPrintScale = scale;

	// count the number of lines for centering
	cg.centerPrintLines = 1;
	s = cg.centerPrint;
	while( *s ) {
		if (*s == '\n')
			cg.centerPrintLines++;
		s++;
	}
}


/*
===================
CG_DrawCenterString
===================
*/
static void CG_DrawCenterString( void ) {
	char	*start;
	int		l;
	int		x, y, w;
	int		h;
	float		scale;
	float	*color;

	if ( !cg.centerPrintTime ) {
		return;
	}

	color = CG_FadeColor( cg.centerPrintTime, 1000 * cg_centertime.value );
	if ( !color ) {
		return;
	}

	trap_R_SetColor( color );

	start = cg.centerPrint;
	scale = cg.centerPrintScale;
	if ( scale <= 0.0f ) {
		scale = 0.5f;
	}

	y = cg.centerPrintY - (int)( (float)( cg.centerPrintLines * BIGCHAR_HEIGHT ) * scale );

	while ( 1 ) {
		char linebuffer[1024];

		for ( l = 0; l < 50; l++ ) {
			if ( !start[l] || start[l] == '\n' ) {
				break;
			}
			linebuffer[l] = start[l];
		}
		linebuffer[l] = 0;

		w = CG_Text_Width( linebuffer, scale, 0 );
		h = CG_Text_Height( linebuffer, scale, 0 );
		x = (SCREEN_WIDTH - w) / 2;
		CG_Text_Paint( x, y + h, scale, color, linebuffer, 0, 0, 0 );
		y += h + 6;
		while ( *start && ( *start != '\n' ) ) {
			start++;
		}
		if ( !*start ) {
			break;
		}
		start++;
	}

	trap_R_SetColor( NULL );
}



/*
================================================================================

CROSSHAIR

================================================================================
*/


/*
=================
CG_DrawScreenVignette

Draws the retail fullscreen vignette overlay when the cached cvar allows it.
=================
*/
static void CG_DrawScreenVignette( void ) {
	vec4_t vignetteColor = { 1.0f, 1.0f, 1.0f, 0.35f };

	if ( !cg.vignetteEnabled ) {
		return;
	}

	if ( !cgs.media.vignetteShader ) {
		cgs.media.vignetteShader = trap_R_RegisterShader( "gfx/misc/vignette" );
	}

	if ( !cgs.media.vignetteShader ) {
		return;
	}

	trap_R_SetColor( vignetteColor );
	CG_DrawPic( 0.0f, 0.0f, 640.0f, 480.0f, cgs.media.vignetteShader );
	trap_R_SetColor( NULL );
}

/*
=================
CG_ApplyCrosshairHitFeedback

Applies the retail hit-window scale and color override to the active crosshair.
=================
*/
static void CG_ApplyCrosshairHitFeedback( float *width, float *height ) {
	static const vec4_t builtInColors[4] = {
		{ 0.25f, 0.50f, 1.00f, 1.00f },
		{ 1.00f, 1.00f, 1.00f, 1.00f },
		{ 1.00f, 0.50f, 1.00f, 1.00f },
		{ 1.00f, 0.00f, 1.00f, 1.00f }
	};
	float		elapsed;
	float		fraction;
	float		scaleAmount;
	float		scaleFactor;
	vec4_t		color;
	int			style;
	int			hitValue;
	qboolean	useColor;
	qboolean	useScale;
	qboolean	useCustomColor;
	qboolean	useConstantScale;

	if ( !width || !height ) {
		return;
	}

	style = cg.crosshairHitStyle;
	if ( style < 1 || style > 8 || cg.crosshairHitTime <= 0 ) {
		return;
	}

	elapsed = (float)( cg.time - cg_crosshairHitFeedbackTime );
	if ( elapsed <= 0.0f || elapsed >= (float)cg.crosshairHitTime ) {
		return;
	}

	useColor = qfalse;
	useScale = qfalse;
	useCustomColor = qfalse;
	useConstantScale = qfalse;

	switch ( style ) {
	case 1:
		useColor = qtrue;
		break;
	case 2:
		useColor = qtrue;
		useCustomColor = qtrue;
		break;
	case 3:
		useScale = qtrue;
		break;
	case 4:
		useColor = qtrue;
		useScale = qtrue;
		break;
	case 5:
		useColor = qtrue;
		useScale = qtrue;
		useCustomColor = qtrue;
		break;
	case 6:
		useScale = qtrue;
		useConstantScale = qtrue;
		break;
	case 7:
		useColor = qtrue;
		useScale = qtrue;
		useConstantScale = qtrue;
		break;
	case 8:
		useColor = qtrue;
		useScale = qtrue;
		useCustomColor = qtrue;
		useConstantScale = qtrue;
		break;
	default:
		return;
	}

	fraction = elapsed / (float)cg.crosshairHitTime;
	hitValue = cg_crosshairHitFeedbackValue;
	if ( hitValue < 1 || hitValue > 4 ) {
		hitValue = 1;
	}

	if ( useScale ) {
		scaleAmount = useConstantScale ? 1.0f : (float)hitValue;
		scaleFactor = 1.0f + scaleAmount * fraction;
		*width *= scaleFactor;
		*height *= scaleFactor;
	}

	if ( !useColor ) {
		return;
	}

	if ( useCustomColor ) {
		Vector4Copy( cg.crosshairHitColor, color );
		color[3] = 1.0f;
	} else {
		Vector4Copy( builtInColors[hitValue - 1], color );
	}

	trap_R_SetColor( color );
}

/*
=================
CG_DrawCrosshair
=================
*/
static void CG_DrawCrosshair(void) {
	float		w, h;
	qhandle_t	hShader;
	float		f;
	float		x, y;
	int			ca;

	if ( !cg_drawCrosshair.integer ) {
		return;
	}

	if ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR) {
		return;
	}

	if ( cg.renderingThirdPerson ) {
		return;
	}

	// set color based on health
	if ( cg_crosshairHealth.integer ) {
		vec4_t		hcolor;

		CG_ColorForHealth( hcolor );
		trap_R_SetColor( hcolor );
	} else {
		trap_R_SetColor( cg.crosshairColor );
	}

	w = h = cg_crosshairSize.value;

	if ( cg.crosshairPulseEnabled ) {
		// pulse the size of the crosshair when picking up items
		f = cg.time - cg.itemPickupBlendTime;
		if ( f > 0 && f < ITEM_BLOB_TIME ) {
			f /= ITEM_BLOB_TIME;
			w *= ( 1 + f );
			h *= ( 1 + f );
		}
	}

	CG_ApplyCrosshairHitFeedback( &w, &h );

	x = cg_crosshairX.integer;
	y = cg_crosshairY.integer;
	// Retail scales crosshair size and offsets from the vertical 480-space axis
	// so the shader stays square regardless of widescreen HUD mode state.
	x *= cgs.screenYScale;
	y *= cgs.screenYScale;
	w *= cgs.screenYScale;
	h *= cgs.screenYScale;

	ca = cg_drawCrosshair.integer;
	if ( ca <= 0 || ( ca % NUM_CROSSHAIRS ) == 0 ) {
		return;
	}
	hShader = cgs.media.crosshairShader[ ca % NUM_CROSSHAIRS ];

	trap_R_DrawStretchPic( x + cg.refdef.x + 0.5 * (cg.refdef.width - w), 
		y + cg.refdef.y + 0.5 * (cg.refdef.height - h), 
		w, h, 0, 0, 1, 1, hShader );
	trap_R_SetColor( NULL );
}



/*
=================
CG_ScanForCrosshairEntity
=================
*/
static void CG_ScanForCrosshairEntity( void ) {
	trace_t		trace;
	vec3_t		start, end;
	int			content;

	VectorCopy( cg.refdef.vieworg, start );
	VectorMA( start, 131072, cg.refdef.viewaxis[0], end );

	CG_Trace( &trace, start, vec3_origin, vec3_origin, end, 
		cg.snap->ps.clientNum, CONTENTS_SOLID|CONTENTS_BODY );
	if ( trace.entityNum >= MAX_CLIENTS ) {
		return;
	}

	// if the player is in fog, don't show it
	content = trap_CM_PointContents( trace.endpos, 0 );
	if ( content & CONTENTS_FOG ) {
		return;
	}

	// if the player is invisible, don't show it
	if ( cg_entities[ trace.entityNum ].currentState.powerups & ( 1 << PW_INVIS ) ) {
		return;
	}

	// update the fade timer
	cg.crosshairClientNum = trace.entityNum;
	cg.crosshairClientTime = cg.time;
}


/*
=============
CG_ShouldDrawCrosshairTeamVitals

Applies the retail same-team gate for the health/armor readout beneath the
crosshair name.
=============
*/
static qboolean CG_ShouldDrawCrosshairTeamVitals( const clientInfo_t *ci ) {
	team_t	myTeam;
	team_t	targetTeam;

	if ( !cg.snap || !ci || !ci->infoValid ) {
		return qfalse;
	}

	if ( cg_drawCrosshairTeamHealth.integer <= 0 || cgs.gametype < GT_TEAM ) {
		return qfalse;
	}

	myTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	targetTeam = ci->team;

	if ( myTeam != targetTeam ) {
		return qfalse;
	}

	return ( qboolean )( myTeam != TEAM_FREE && myTeam != TEAM_SPECTATOR );
}

/*
=============
CG_GetCrosshairTeamVitalColor

Rebuilds the retail 0-2 mode color ramp for teammate crosshair health and
armor strings.
=============
*/
static void CG_GetCrosshairTeamVitalColor( int value, int maxValue, float alpha, vec4_t color ) {
	float	lowComponent;
	float	highComponent;

	if ( maxValue <= 0 ) {
		maxValue = 100;
	}

	if ( value < maxValue ) {
		lowComponent = (float)value / (float)maxValue;
		if ( lowComponent <= 0.0f ) {
			lowComponent = 0.0f;
		}
		highComponent = 0.0f;
	} else {
		lowComponent = 1.0f;
		highComponent = (float)value / (float)( maxValue + maxValue );
		if ( highComponent > 1.0f ) {
			highComponent = 1.0f;
		}
	}

	color[0] = 1.0f;
	color[1] = lowComponent;
	color[2] = highComponent;
	color[3] = alpha;
}

/*
=============
CG_DrawCrosshairTeamVitals

Renders the retail teammate health/armor readout centered beneath the
crosshair target name.
=============
*/
static void CG_DrawCrosshairTeamVitals( const clientInfo_t *ci, const vec4_t baseColor ) {
	char	healthText[16];
	char	armorText[16];
	float	textScale;
	float	textY;
	float	healthWidth;
	int		maxHealth;
	vec4_t	healthColor;
	vec4_t	slashColor;
	vec4_t	armorColor;

	if ( !CG_ShouldDrawCrosshairTeamVitals( ci ) ) {
		return;
	}

	textScale = cg_drawCrosshairTeamHealthSize.value;
	if ( textScale <= 0.0f ) {
		return;
	}

	maxHealth = cg.snap->ps.stats[STAT_MAX_HEALTH];
	Com_sprintf( healthText, sizeof( healthText ), "%i ", ci->health );
	Com_sprintf( armorText, sizeof( armorText ), " %i", ci->armor );

	Vector4Copy( baseColor, healthColor );
	Vector4Copy( baseColor, slashColor );
	Vector4Copy( baseColor, armorColor );

	if ( cg_drawCrosshairTeamHealth.integer == 2 ) {
		CG_GetCrosshairTeamVitalColor( ci->health, maxHealth, baseColor[3], healthColor );
		slashColor[0] = 1.0f;
		slashColor[1] = 1.0f;
		slashColor[2] = 1.0f;
		slashColor[3] = baseColor[3];
		CG_GetCrosshairTeamVitalColor( ci->armor, maxHealth, baseColor[3], armorColor );
	}

	healthWidth = CG_Text_Width( healthText, textScale, 0 );
	textY = 198.0f + textScale * 16.0f;

	CG_Text_Paint( 320.0f - healthWidth, textY, textScale, healthColor, healthText, 0, 0, ITEM_TEXTSTYLE_SHADOWED );
	CG_Text_Paint( 320.0f, textY, textScale, slashColor, "/", 0, 0, ITEM_TEXTSTYLE_SHADOWED );
	CG_Text_Paint( 325.0f, textY, textScale, armorColor, armorText, 0, 0, ITEM_TEXTSTYLE_SHADOWED );
}

/*
=============
CG_ShouldRenderCrosshairName

Determines if the current crosshair target should have their name displayed.
=============
*/
static qboolean CG_ShouldRenderCrosshairName( const clientInfo_t *ci, float *opacityScale ) {
	team_t	myTeam;
	team_t	targetTeam;
	qboolean	teamGame;
	float		alpha;

	if ( !ci || !ci->infoValid ) {
		return qfalse;
	}

	alpha = 1.0f;
	teamGame = ( qboolean )( cgs.gametype >= GT_TEAM );
	myTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	targetTeam = ci->team;

	if ( teamGame && targetTeam != TEAM_FREE && targetTeam != TEAM_SPECTATOR && myTeam == targetTeam ) {
		if ( !cg_teammateCrosshairNames.integer ) {
			return qfalse;
		}
		alpha *= Com_Clamp( 0.0f, 1.0f, cg_teammateCrosshairNamesOpacity.value );
	} else {
		if ( !cg_enemyCrosshairNames.integer ) {
			return qfalse;
		}
		alpha *= Com_Clamp( 0.0f, 1.0f, cg_enemyCrosshairNamesOpacity.value );
	}

	if ( opacityScale ) {
		*opacityScale = alpha;
	}

	return qtrue;
}

/*
=====================
CG_DrawCrosshairNames
=====================
*/
static void CG_DrawCrosshairNames( void ) {
	float		*color;
	const char	*name;
	float		w;
	float		nameScale;
	float		opacityScale;
	const clientInfo_t	*ci;

	if ( !cg_drawCrosshair.integer ) {
		return;
	}
	if ( !cg_drawCrosshairNames.integer ) {
		return;
	}
	if ( cg.renderingThirdPerson ) {
		return;
	}

	// scan the known entities to see if the crosshair is sighted on one
	CG_ScanForCrosshairEntity();

	// draw the name of the player being looked at
	color = CG_FadeColor( cg.crosshairClientTime, 1000 );
	if ( !color ) {
		trap_R_SetColor( NULL );
		return;
	}

	ci = &cgs.clientinfo[ cg.crosshairClientNum ];
	opacityScale = 1.0f;
	if ( !CG_ShouldRenderCrosshairName( ci, &opacityScale ) ) {
		trap_R_SetColor( NULL );
		return;
	}

	name = ci->name;
	color[3] *= ( 0.5f * opacityScale );

	nameScale = 0.26f;
	w = CG_Text_Width( name, nameScale, 0 );
	if ( cg_overheadNamesWidth.value > 0.0f && w > cg_overheadNamesWidth.value ) {
		float clampedScale = cg_overheadNamesWidth.value / w;
		if ( clampedScale < 0.1f ) {
			clampedScale = 0.1f;
		}
		nameScale *= clampedScale;
		w = CG_Text_Width( name, nameScale, 0 );
	}

	CG_Text_Paint( 320 - w / 2, 190, nameScale, color, name, 0, 0, ITEM_TEXTSTYLE_SHADOWED);
	CG_DrawCrosshairTeamVitals( ci, color );
	trap_R_SetColor( NULL );
}


//==============================================================================

/*
=============
CG_ResetDraw2DMenuCache

Clears the cached retail 2D overlay roots rebuilt when HUD menus reload.
=============
*/
void CG_ResetDraw2DMenuCache( void ) {
	menuScoreboard = NULL;
	menuStats = NULL;
	cgSpectatorMenu = NULL;
	cgSpectatorFollowMenu = NULL;
	cgSpectatorRedTopMenu = NULL;
	cgSpectatorRedBottomMenu = NULL;
	cgSpectatorBlueTopMenu = NULL;
	cgSpectatorBlueBottomMenu = NULL;
}

/*
=============
CG_CacheDraw2DMenuCache

Resolves the retail 2D overlay roots that `CG_Draw2D()` reuses each frame.
=============
*/
void CG_CacheDraw2DMenuCache( void ) {
	menuStats = Menus_FindByName( "stats_menu" );
	cgSpectatorMenu = Menus_FindByName( "comp_spechud_menu" );
	cgSpectatorFollowMenu = Menus_FindByName( "comp_specfollowhud_menu" );
	cgSpectatorRedTopMenu = Menus_FindByName( "comp_specred_top" );
	cgSpectatorRedBottomMenu = Menus_FindByName( "comp_specred_bottom" );
	cgSpectatorBlueTopMenu = Menus_FindByName( "comp_specblue_top" );
	cgSpectatorBlueBottomMenu = Menus_FindByName( "comp_specblue_bottom" );
}

/*
=============
CG_DrawCachedOverlayMenu

Paints one cached retail browser/menu root when it exists.
=============
*/
static qboolean CG_DrawCachedOverlayMenu( menuDef_t *menu ) {
	if ( !menu ) {
		return qfalse;
	}

	menu->window.flags &= ~WINDOW_FORCED;
	CG_DrawBrowserOverlayTree( menu, qtrue );
	return qtrue;
}

/*
=============
CG_DrawSpectatorFallback

Preserves the source-side spectator text when retail menu roots are absent.
=============
*/
static void CG_DrawSpectatorFallback( void ) {
	CG_DrawBigString(320 - 9 * 8, 440, "SPECTATOR", 1.0F);
	if ( cgs.gametype == GT_TOURNAMENT ) {
		CG_DrawBigString(320 - 15 * 8, 460, "waiting to play", 1.0F);
	}
	else if ( cgs.gametype >= GT_TEAM ) {
		CG_DrawBigString(320 - 39 * 8, 460, "press ESC and use the JOIN menu to play", 1.0F);
	}
}

/*
=================
CG_DrawSpectator
=================
*/
static void CG_DrawSpectator( void ) {
	menuDef_t	*menu;
	qboolean	drewOverlay;

	if ( cg.scoreBoardShowing ) {
		return;
	}

	drewOverlay = qfalse;
	menu = cgSpectatorMenu;
	if ( cg.snap && ( cg.snap->ps.pm_flags & PMF_FOLLOW ) && cgSpectatorFollowMenu ) {
		menu = cgSpectatorFollowMenu;
	}

	drewOverlay = (qboolean)( CG_DrawCachedOverlayMenu( menu ) || drewOverlay );
	drewOverlay = (qboolean)( CG_DrawCachedOverlayMenu( cgSpectatorRedTopMenu ) || drewOverlay );
	drewOverlay = (qboolean)( CG_DrawCachedOverlayMenu( cgSpectatorRedBottomMenu ) || drewOverlay );
	drewOverlay = (qboolean)( CG_DrawCachedOverlayMenu( cgSpectatorBlueTopMenu ) || drewOverlay );
	drewOverlay = (qboolean)( CG_DrawCachedOverlayMenu( cgSpectatorBlueBottomMenu ) || drewOverlay );

	if ( !drewOverlay ) {
		CG_DrawSpectatorFallback();
	}
}

/*
=================
CG_DrawVote
=================
*/
static void CG_DrawVote(void) {
	static vec4_t	voteColor = { 1.0f, 1.0f, 0.0f, 1.0f };
	const char	*s;
	char		yesKey[32];
	char		noKey[32];
	int		sec;

	CG_GetBindKeyName( "vote yes", yesKey, sizeof( yesKey ) );
	CG_GetBindKeyName( "vote no", noKey, sizeof( noKey ) );

	if ( cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER ) {
		if ( cg_complaintWarning.integer && cg.complaintClient >= 0 &&
				cg.complaintEndTime > cg.time && !cg.renderingThirdPerson ) {
			sec = ( cg.complaintEndTime - cg.time ) / 1000;
			if ( sec < 0 ) {
				sec = 0;
			}

			s = va( "File complaint against %s for team-killing?", cgs.clientinfo[cg.complaintClient].name );
			CG_Text_Paint( 4.0f, 300.0f, 0.22f, voteColor, s, 0, 0, 0 );
			s = va( "Press '%s' for Yes, or '%s' for No (%is)", yesKey, noKey, sec );
			CG_Text_Paint( 8.0f, 312.0f, 0.22f, colorWhite, s, 0, 0, 0 );
			return;
		}

		if ( cg.complaintEndTime > cg.time && !cg.renderingThirdPerson &&
				cg_complaintWarning.integer > 0 && cg.complaintClient < 0 ) {
			s = NULL;
			switch ( cg.complaintClient ) {
			case -1:
				s = "Your complaint has been filed.";
				break;
			case -2:
				s = "Your complaint has been dismissed.";
				break;
			case -3:
				s = "Comlaints cannot be filed against server admins.";
				break;
			case -4:
				s = "You received friendly fire from a server admin.";
				break;
			}

			if ( s ) {
				CG_Text_PaintNoAdjust( 3.0f, 300.0f, 0.22f, colorWhite, s, 0, 0 );
				return;
			}
		}
	}

	if ( !cgs.voteTime ) {
		return;
	}

	// play a talk beep whenever it is modified
	if ( cgs.voteModified ) {
		cgs.voteModified = qfalse;
		trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );
	}

	sec = ( VOTE_TIME - ( cg.time - cgs.voteTime ) ) / 1000;
	if ( sec < 0 ) {
		sec = 0;
	}

	s = va( "VOTE(%is):%s Yes(%s):%i No(%s):%i", sec, cgs.voteString, yesKey, cgs.voteYes, noKey, cgs.voteNo );
	CG_Text_PaintNoAdjust( 4.0f, 300.0f, 0.22f, voteColor, s, 0, 0 );
	CG_Text_PaintNoAdjust( 8.0f, 312.0f, 0.22f, colorWhite, "or press ESC then click Vote", 0, 0 );
}

/*
=============
CG_GetGametypeScoreboardName

Resolves the Quake Live menu name used for the current gametype.
=============
*/
static const char *CG_GetGametypeScoreboardName( void ) {
	switch ( cgs.gametype ) {
	case GT_FFA:
		return "score_menu_ffa";
	case GT_TOURNAMENT:
		return "score_menu_duel";
	case GT_SINGLE_PLAYER:
#if GT_RACE != GT_SINGLE_PLAYER
	case GT_RACE:
#endif
		return "score_menu_race";
	case GT_RED_ROVER:
		return "score_menu_rr";
	case GT_TEAM:
		return "teamscore_menu_tdm";
	case GT_CLAN_ARENA:
		return "teamscore_menu_ca";
	case GT_CTF:
		return "teamscore_menu_ctf";
	case GT_1FCTF:
		return "teamscore_menu_1fctf";
	case GT_OBELISK:
		return "teamscore_menu";
	case GT_HARVESTER:
		return "teamscore_menu_har";
	case GT_FREEZE:
		return "teamscore_menu_ft";
	case GT_DOMINATION:
		return "teamscore_menu_dom";
	case GT_ATTACK_DEFEND:
		return "teamscore_menu_ad";
	default:
		break;
	}

	if ( cgs.gametype >= GT_TEAM ) {
		return "teamscore_menu";
	}

	return "score_menu";
}

/*
=============
CG_DrawScoreboard

Paints the Quake Live scoreboard menu for the active gametype.
=============
*/
static qboolean CG_DrawScoreboard( void ) {
	static qboolean firstTime = qtrue;
	float fade, *fadeColor;
	const char *menuName;

	if ( menuScoreboard ) {
		menuScoreboard->window.flags &= ~WINDOW_FORCED;
	}
	if ( cg_paused.integer ) {
		cg.deferredPlayerLoading = 0;
		firstTime = qtrue;
		return qfalse;
	}

	// should never happen in Team Arena
	if ( cgs.gametype == GT_SINGLE_PLAYER && cg.predictedPlayerState.pm_type == PM_INTERMISSION ) {
		cg.deferredPlayerLoading = 0;
		firstTime = qtrue;
		return qfalse;
	}

	// don't draw scoreboard during death while warmup up
	if ( cg.warmup && !cg.showScores ) {
		return qfalse;
	}

	if ( cg.showScores || cg.predictedPlayerState.pm_type == PM_DEAD || cg.predictedPlayerState.pm_type == PM_INTERMISSION ) {
		fade = 1.0f;
		fadeColor = colorWhite;
	} else {
		fadeColor = CG_FadeColor( cg.scoreFadeTime, FADE_TIME );
		if ( !fadeColor ) {
			// next time scoreboard comes up, don't print killer
			cg.deferredPlayerLoading = 0;
			cg.killerName[0] = 0;
			firstTime = qtrue;
			return qfalse;
		}
		fade = *fadeColor;
	}

	menuName = CG_GetGametypeScoreboardName();
	if ( menuScoreboard && menuName && Q_stricmp( menuScoreboard->window.name, menuName ) ) {
		menuScoreboard = NULL;
		firstTime = qtrue;
	}

	if ( !menuScoreboard && menuName ) {
		menuScoreboard = CG_FindBrowserOverlayByName( menuName );
	}

	if ( !menuScoreboard ) {
		const char *fallback = ( cgs.gametype >= GT_TEAM ) ? "teamscore_menu" : "score_menu";
		menuScoreboard = CG_FindBrowserOverlayByName( fallback );
	}

	if ( !menuScoreboard ) {
		return qfalse;
	}

	if ( firstTime ) {
		CG_SetScoreSelection( menuScoreboard );
		firstTime = qfalse;
	}

	CG_DrawBrowserOverlayTree( menuScoreboard, qtrue );

	// load any models that have been deferred
	if ( ++cg.deferredPlayerLoading > 10 ) {
		CG_LoadDeferredPlayers();
	}

	return qtrue;
}

/*
=============
CG_DrawActiveScoreboard

Selects the appropriate scoreboard implementation for the current HUD mode.
=============
*/
static qboolean CG_DrawActiveScoreboard( qboolean menuHudActive, qboolean forceDisplay ) {
	qboolean	requested;
	qboolean	drawn;

	requested = forceDisplay;
	if ( !requested ) {
		requested = (qboolean)( ( cg.showScores != 0 ) || ( ( cg.snap->ps.pm_flags & PMF_SCOREBOARD ) != 0 ) );
		if ( menuHudActive ) {
			requested = (qboolean)( cg.showScores != 0 );
		}
	}

	if ( !requested ) {
		CG_StopScoreboardTimer( cg.time );
		return qfalse;
	}

	CG_StartScoreboardTimer( cg.time );
	CG_BuildHudScoreboard();

	drawn = CG_DrawScoreboard();
	if ( !drawn ) {
		drawn = CG_DrawOldScoreboard();
	}

	if ( !drawn ) {
		CG_StopScoreboardTimer( cg.time );
	}

	return drawn;
}

/*
=================
CG_DrawIntermission
=================
*/
static void CG_DrawIntermission( void ) {
//	int key;
	//if (cg_singlePlayer.integer) {
	//	CG_DrawCenterString();
	//	return;
	//}
	cg.scoreFadeTime = cg.time;
	cg.scoreBoardShowing = CG_DrawActiveScoreboard( qfalse, qtrue );
}

/*
=================
CG_DrawFollow
=================
*/
static qboolean CG_DrawFollow( void ) {
	float		x;
	vec4_t		color;
	const char	*name;

	if ( !(cg.snap->ps.pm_flags & PMF_FOLLOW) ) {
		return qfalse;
	}
	color[0] = 1;
	color[1] = 1;
	color[2] = 1;
	color[3] = 1;


	CG_DrawBigString( 320 - 9 * 8, 24, "following", 1.0F );

	name = cgs.clientinfo[ cg.snap->ps.clientNum ].name;

	x = 0.5 * ( 640 - GIANT_WIDTH * CG_DrawStrlen( name ) );

	CG_DrawStringExt( x, 40, name, color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );

	return qtrue;
}



/*
=================
CG_DrawAmmoWarning
=================
*/
static void CG_DrawAmmoWarning( void ) {
	const char	*s;
	float		scale;
	float		y;
	int			w;

	if ( cg_drawAmmoWarning.integer == 0 ) {
		return;
	}

	if ( !cg.lowAmmoWarning ) {
		return;
	}

	if ( cg.lowAmmoWarning == 2 ) {
		s = "OUT OF AMMO";
	} else {
		s = "LOW AMMO WARNING";
	}

	if ( cg_drawAmmoWarning.integer == 1 ) {
		scale = 0.35f;
		y = 55.0f;
	} else {
		scale = 0.24f;
		y = 52.0f;
	}

	w = CG_Text_Width( s, scale, 0 );
	CG_Text_Paint( 320.0f - (float)w * 0.5f, y, scale, colorWhite, s, 0.0f, 0, 0 );
}


/*
=================
CG_DrawProxWarning
=================
*/
static void CG_DrawProxWarning( void ) {
	char		s[32];
	int			w;
	static int	proxTime;
	static int	proxCounter;
	static int	proxTick;

	if ( !( cg.snap->ps.eFlags & EF_TICKING ) ) {
		proxTime = 0;
		return;
	}

	if ( proxTime == 0 ) {
		proxTime = cg.time + 5000;
		proxCounter = 5;
		proxTick = 0;
	}

	if ( cg.time > proxTime ) {
		proxTick = proxCounter--;
		proxTime = cg.time + 1000;
	}

	if ( proxTick != 0 ) {
		Com_sprintf( s, sizeof( s ), "INTERNAL COMBUSTION IN: %i", proxTick );
	} else {
		Com_sprintf( s, sizeof( s ), "YOU HAVE BEEN MINED" );
	}

	CG_Text_GetExtents( s, 0.25f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
	CG_Text_PaintNoAdjust( 320 - w / 2, 112.0f, 0.25f, g_color_table[ColorIndex(COLOR_RED)], s, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
}


/*
=================
CG_GetBindKeyName
=================
*/
static const char *CG_GetBindKeyName( const char *cmd, char *buf, int len ) {
	int key;

	key = trap_Key_GetKey( cmd );
	trap_Key_KeynumToStringBuf( key, buf, len );
	return buf;
}

/*
=================
CG_DrawWarmupStartBanner
=================
*/
static void CG_DrawWarmupStartBanner( void ) {
	const char	*text;
	team_t		localTeam;
	team_t		attackingTeam;
	sfxHandle_t	sound;

	text = "FIGHT!";
	sound = cgs.media.countFightSound;

	if ( cgs.gametype == GT_ATTACK_DEFEND ) {
		attackingTeam = ( cgs.matchRoundTurn != 0 ) ? TEAM_BLUE : TEAM_RED;
		localTeam = TEAM_SPECTATOR;
		if ( cg.snap ) {
			localTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
		}

		if ( localTeam == TEAM_RED || localTeam == TEAM_BLUE ) {
			if ( localTeam == attackingTeam ) {
				text = "ATTACK THE FLAG!";
				if ( cgs.media.attackTheFlagSound ) {
					sound = cgs.media.attackTheFlagSound;
				}
			} else {
				text = "DEFEND THE FLAG!";
				if ( cgs.media.defendTheFlagSound ) {
					sound = cgs.media.defendTheFlagSound;
				}
			}
		}
	} else if ( cgs.gametype == GT_RED_ROVER ) {
		if ( cgs.matchRoundNumber > 0 && cgs.media.kamikazeRespawnSound ) {
			trap_S_StartLocalSound( cgs.media.kamikazeRespawnSound, CHAN_LOCAL_SOUND );
		}
		if ( ( cgs.customSettingsMask & CUSTOM_SETTING_INFECTED )
			&& cg.snap && cg.snap->ps.generic1 == 2 ) {
			text = "BITE!";
			if ( cgs.media.biteSound ) {
				sound = cgs.media.biteSound;
			}
		}
	}

	CG_ClearBufferedAnnouncements();

	if ( sound ) {
		trap_S_StartLocalSound( sound, CHAN_ANNOUNCER );
	}

	CG_CenterPrint( text, 120, 0.5f );
}

/*
=================
CG_PlayWarmupCountSound
=================
*/
static void CG_PlayWarmupCountSound( int countdown ) {
	switch ( countdown ) {
	case 3:
		if ( cgs.media.count3Sound ) {
			trap_S_StartLocalSound( cgs.media.count3Sound, CHAN_ANNOUNCER );
		}
		break;

	case 2:
		if ( cgs.media.count2Sound ) {
			trap_S_StartLocalSound( cgs.media.count2Sound, CHAN_ANNOUNCER );
		}
		break;

	case 1:
		if ( cgs.media.count1Sound ) {
			trap_S_StartLocalSound( cgs.media.count1Sound, CHAN_ANNOUNCER );
		}
		break;

	case 0:
		if ( CG_IsRoundStartGametype( cgs.gametype ) ) {
			CG_DrawWarmupStartBanner();
		}
		break;

	case 5:
		if ( cgs.matchTimeoutActive ) {
			if ( cgs.media.countPrepareSound ) {
				trap_S_StartLocalSound( cgs.media.countPrepareSound, CHAN_ANNOUNCER );
			}
		} else if ( CG_IsRoundStartGametype( cgs.gametype )
			&& ( cgs.gametype != GT_FREEZE || countdown >= 5 ) ) {
			if ( cgs.media.roundBeginsInSound ) {
				trap_S_StartLocalSound( cgs.media.roundBeginsInSound, CHAN_ANNOUNCER );
			}
		}
		break;

	default:
		break;
	}
}

/*
=================
CG_ADRoundScoreboardStatusText

Builds the retail Attack and Defend round-panel status banner from the
available scorelimit and roundlimit transport.
=================
*/
static const char *CG_ADRoundScoreboardStatusText( void ) {
	const char	*info;
	const char	*value;
	int		scorelimit;
	int		roundlimit;
	int		redScore;
	int		blueScore;

	info = CG_ConfigString( CS_SERVERINFO );
	scorelimit = 0;
	roundlimit = 0;
	if ( info && info[0] ) {
		value = Info_ValueForKey( info, "g_scorelimit" );
		scorelimit = value[0] ? atoi( value ) : 0;

		value = Info_ValueForKey( info, "roundlimit" );
		roundlimit = value[0] ? atoi( value ) : 0;
	}

	redScore = cg.teamScores[0];
	blueScore = cg.teamScores[1];

	if ( cgs.matchRoundTurn != 0 ) {
		if ( scorelimit > 0 && redScore >= scorelimit && redScore > blueScore ) {
			return "Red Wins! Good Game";
		}

		if ( ( scorelimit > 0 && redScore > blueScore && redScore + 1 >= scorelimit )
			|| ( roundlimit > 0 && cgs.matchRoundNumber >= roundlimit && redScore > blueScore ) ) {
			return "Last Chance";
		}
	}

	if ( ( scorelimit > 0
			&& ( ( cgs.matchRoundTurn != 0 ) ? blueScore : redScore ) + 1 >= scorelimit )
		|| ( roundlimit > 0 && cgs.matchRoundNumber >= roundlimit ) ) {
		return "Match Point";
	}

	return NULL;
}

/*
=================
CG_DrawADRoundScoreboard

Mirrors the retail Attack and Defend round-score panel drawn beneath the
warmup banner.
=================
*/
static void CG_DrawADRoundScoreboard( void ) {
	static const vec4_t panelColor = { 0.0f, 0.0f, 0.0f, 0.25f };
	static const vec4_t activeTeamRedFillColor = { 0.5f, 0.1f, 0.1f, 0.5f };
	static const vec4_t activeTeamBlueFillColor = { 0.1f, 0.1f, 0.5f, 0.5f };
	static const vec4_t activeRoundRedFillColor = { 1.0f, 0.0f, 0.0f, 0.5f };
	static const vec4_t activeRoundBlueFillColor = { 0.0f, 0.0f, 1.0f, 0.5f };
	static vec4_t	redColor = { 1.0f, 0.0f, 0.0f, 1.0f };
	static vec4_t	blueColor = { 0.0f, 0.0f, 1.0f, 1.0f };
	const vec4_t	*activeTeamFillColor;
	const vec4_t	*activeRoundFillColor;
	const char	*statusText;
	float		activeRowY;
	float		cellX;
	int		column;
	int		activeColumn;
	int		roundWindowStart;

	if ( cgs.matchRoundNumber <= 0 ) {
		return;
	}

	CG_FillRect( 196.0f, 150.0f, 252.0f, 60.0f, panelColor );
	/*
	CG_FillRect( 200.0f, 150.0f, 240.0f, 48.0f, panelColor );
	CG_Text_PaintNoAdjust( 204.0f, 178.0f, 0.25f, colorRed, "Red", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	CG_Text_PaintNoAdjust( 204.0f, 194.0f, 0.25f, colorBlue, "Blue", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	CG_Text_PaintNoAdjust( 404.0f, 162.0f, 0.25f, colorWhite, "Score", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	*/

	roundWindowStart = ( cgs.matchRoundNumber > ( CG_AD_SCORE_HISTORY_LENGTH / 2 ) ) ?
		( cgs.matchRoundNumber - ( CG_AD_SCORE_HISTORY_LENGTH / 2 ) + 1 ) : 1;
	activeColumn = cgs.matchRoundNumber - roundWindowStart;
	if ( activeColumn < 0 ) {
		activeColumn = 0;
	} else if ( activeColumn >= ( CG_AD_SCORE_HISTORY_LENGTH / 2 ) ) {
		activeColumn = ( CG_AD_SCORE_HISTORY_LENGTH / 2 ) - 1;
	}

	if ( cgs.matchRoundTurn != 0 ) {
		activeRowY = 182.0f;
		activeTeamFillColor = &activeTeamBlueFillColor;
		activeRoundFillColor = &activeRoundBlueFillColor;
	} else {
		activeRowY = 166.0f;
		activeTeamFillColor = &activeTeamRedFillColor;
		activeRoundFillColor = &activeRoundRedFillColor;
	}

	CG_FillRect( 200.0f, activeRowY, 40.0f, 16.0f, *activeTeamFillColor );
	CG_FillRect( 240.0f + activeColumn * 16.0f, activeRowY, 16.0f, 16.0f, *activeRoundFillColor );

	CG_Text_PaintNoAdjust( 204.0f, 162.0f, 0.20f, colorWhite, "Round", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	CG_Text_PaintNoAdjust( 204.0f, 178.0f, 0.25f, redColor, "Red", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	CG_Text_PaintNoAdjust( 204.0f, 194.0f, 0.25f, blueColor, "Blue", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );

	for ( column = 0; column < ( CG_AD_SCORE_HISTORY_LENGTH / 2 ); column++ ) {
		char	buffer[16];
		int		historyIndex;
		int		roundNumber;
		int		textWidth;

		cellX = 240.0f + column * 16.0f;
		roundNumber = roundWindowStart + column;
		Com_sprintf( buffer, sizeof( buffer ), "%i", roundNumber );
		textWidth = CG_Text_Width( buffer, 0.20f, 0 );
		CG_Text_PaintNoAdjust( cellX + ( 16.0f - (float)textWidth ) * 0.5f, 162.0f, 0.20f,
			colorWhite, buffer, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );

		historyIndex = column * 2;
		if ( cg.adScoreHistory[historyIndex] >= 0 ) {
			Com_sprintf( buffer, sizeof( buffer ), "%i", cg.adScoreHistory[historyIndex] );
			textWidth = CG_Text_Width( buffer, 0.25f, 0 );
			CG_Text_PaintNoAdjust( cellX + ( 16.0f - (float)textWidth ) * 0.5f, 178.0f, 0.25f,
				redColor, buffer, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
		}

		if ( cg.adScoreHistory[historyIndex + 1] >= 0 ) {
			Com_sprintf( buffer, sizeof( buffer ), "%i", cg.adScoreHistory[historyIndex + 1] );
			textWidth = CG_Text_Width( buffer, 0.25f, 0 );
			CG_Text_PaintNoAdjust( cellX + ( 16.0f - (float)textWidth ) * 0.5f, 194.0f, 0.25f,
				blueColor, buffer, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
		}
	}

	CG_Text_PaintNoAdjust( 416.0f, 162.0f, 0.25f, colorWhite, "Score", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	{
		char	buffer[16];
		int		textWidth;

		Com_sprintf( buffer, sizeof( buffer ), "%i", cg.teamScores[0] );
		textWidth = CG_Text_Width( buffer, 0.25f, 0 );
		CG_Text_PaintNoAdjust( 416.0f + ( 16.0f - (float)textWidth ) * 0.5f, 178.0f, 0.25f,
			redColor, buffer, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );

		Com_sprintf( buffer, sizeof( buffer ), "%i", cg.teamScores[1] );
		textWidth = CG_Text_Width( buffer, 0.25f, 0 );
		CG_Text_PaintNoAdjust( 416.0f + ( 16.0f - (float)textWidth ) * 0.5f, 194.0f, 0.25f,
			blueColor, buffer, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	}

	statusText = CG_ADRoundScoreboardStatusText();
	if ( statusText && statusText[0] ) {
		int		textWidth;
		vec4_t	*statusColor;

		statusColor = &colorWhite;
		if ( !Q_stricmp( statusText, "Red Wins! Good Game" ) ) {
			statusColor = &redColor;
		}

		textWidth = CG_Text_Width( statusText, 0.30f, 0 );
		CG_Text_PaintNoAdjust( 320.0f - (float)textWidth * 0.5f, 214.0f, 0.30f, *statusColor,
			statusText, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	}
}

/*
=================
CG_DrawWarmupStatusText
=================
*/
static void CG_DrawWarmupStatusText( int gametype ) {
	int				i;
	int				w;
	int				countdown;
	float			titleY;
	float			countdownY;
	float			countdownScale;
	float			verticalOffset;
	qboolean			shortCountdown;
	clientInfo_t		*ci1;
	clientInfo_t		*ci2;
	team_t			localTeam;
	team_t			attackingTeam;
	const char		*title;
	const char		*countdownText;

	title = "";
	titleY = 90.0f;
	countdownY = 125.0f;
	verticalOffset = ( gametype == GT_RACE ) ? 30.0f : 0.0f;
	shortCountdown = qfalse;

	if ( gametype == GT_TOURNAMENT ) {
		ci1 = NULL;
		ci2 = NULL;
		for ( i = 0; i < cgs.maxclients; i++ ) {
			if ( cgs.clientinfo[i].infoValid && cgs.clientinfo[i].team == TEAM_FREE ) {
				if ( !ci1 ) {
					ci1 = &cgs.clientinfo[i];
				} else {
					ci2 = &cgs.clientinfo[i];
				}
			}
		}

		if ( ci1 && ci2 ) {
			title = va( "%s vs %s", ci1->name, ci2->name );
		}
	} else if ( gametype == GT_FFA && ( cgs.customSettingsMask & CUSTOM_SETTING_QUAD_HOG ) ) {
		title = "Quad Hog";
	} else if ( gametype == GT_RED_ROVER &&
		( cgs.customSettingsMask & CUSTOM_SETTING_INFECTED ) &&
		cgs.matchRoundNumber <= 0 ) {
		title = "Infected";
	} else if ( gametype == GT_ATTACK_DEFEND && cgs.matchRoundState == ROUNDSTATE_WARMUP ) {
		CG_DrawADRoundScoreboard();
		attackingTeam = ( cgs.matchRoundTurn != 0 ) ? TEAM_BLUE : TEAM_RED;
		localTeam = TEAM_SPECTATOR;
		if ( cg.snap ) {
			localTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
		}

		if ( localTeam == TEAM_RED || localTeam == TEAM_BLUE ) {
			title = ( localTeam == attackingTeam ) ? "ATTACK THE FLAG" : "DEFEND THE FLAG";
		} else {
			title = ( attackingTeam == TEAM_RED ) ? "Red is on offense" : "Blue is on offense";
		}
		shortCountdown = qtrue;
	} else {
		switch ( gametype ) {
		case GT_CLAN_ARENA:
		case GT_FREEZE:
		case GT_ATTACK_DEFEND:
		case GT_RED_ROVER:
			if ( cgs.matchRoundNumber > 0 ) {
				title = cgs.matchSuddenDeathActive ? "Sudden Death" : "Round Begins in";
				shortCountdown = qtrue;
				break;
			}
			break;

		default:
			break;
		}

		if ( !title[0] ) {
			title = CG_GameTypeString();
		}
	}

	if ( title[0] ) {
		CG_Text_GetExtents( title, 0.6f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
		CG_Text_PaintNoAdjust( 320 - w / 2, titleY + verticalOffset, 0.6f, colorWhite,
			title, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	}

	countdown = cg.warmupCount;
	if ( countdown <= 0 ) {
		return;
	}

	countdownText = va( shortCountdown ? "%i" : "Starts in: %i", countdown );
	countdownScale = 0.45f;
	CG_Text_GetExtents( countdownText, countdownScale, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
	CG_Text_PaintNoAdjust( 320 - w / 2, countdownY + verticalOffset, countdownScale, colorWhite,
		countdownText, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
}

/*
=================
CG_DrawMatchPauseStatus
=================
*/
static void CG_DrawMatchPauseStatus( void ) {
	int			remaining;
	int			w;
	const char		*text;

	if ( !cgs.matchTimeoutActive ) {
		return;
	}

	text = "Match Paused";
	if ( cgs.matchTimeoutExpireTime > 0 ) {
		remaining = ( cgs.matchTimeoutExpireTime - cg.time ) / 1000;
		if ( remaining < 0 ) {
			remaining = 0;
		}

		if ( remaining <= 5 ) {
			if ( remaining != cg.warmupCount ) {
				cg.warmupCount = remaining;
				CG_PlayWarmupCountSound( remaining );
			}

			if ( remaining <= 0 ) {
				return;
			}

			text = va( "Match resuming in ^5%d^7 seconds", remaining );
		} else {
			cg.warmupCount = -1;
		}
	} else {
		cg.warmupCount = -1;
	}

	CG_Text_GetExtents( text, 0.5f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
	CG_Text_PaintNoAdjust( 320 - w / 2, 128.0f, 0.5f, colorWhite, text, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
}

/*
=================
CG_DominationPointLabel
=================
*/
static const char *CG_DominationPointLabel( int pointIndex ) {
	switch ( pointIndex ) {
	case 1:
		return "A";
	case 2:
		return "B";
	case 3:
		return "C";
	case 4:
		return "D";
	case 5:
		return "E";
	default:
		return "?";
	}
}

/*
=================
CG_DrawDominationPointStatus
=================
*/
static void CG_DrawDominationPointStatus( void ) {
	centity_t	*cent;
	team_t		viewerTeam;
	team_t		owner;
	team_t		capturing;
	team_t		activeTeam;
	vec3_t		delta;
	vec4_t		barColor;
	const char	*text;
	const char	*pointLabel;
	float		progress;
	float		radius;
	int			i;
	int			textWidth;
	int			captureCount;

	if ( cgs.gametype != GT_DOMINATION || !cg.snap || cg.showScores ) {
		return;
	}

	if ( cg.snap->ps.stats[STAT_HEALTH] <= 0 || cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return;
	}

	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return;
	}

	viewerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	if ( viewerTeam != TEAM_RED && viewerTeam != TEAM_BLUE ) {
		return;
	}

	for ( i = 0; i < ENTITYNUM_NONE; i++ ) {
		cent = &cg_entities[i];
		if ( !cent->currentValid || cent->currentState.eType != ET_TEAM ) {
			continue;
		}

		radius = (float)cent->currentState.otherEntityNum;
		if ( radius <= 0.0f ) {
			continue;
		}

		owner = ( cent->currentState.modelindex == TEAM_RED || cent->currentState.modelindex == TEAM_BLUE ) ?
			(team_t)cent->currentState.modelindex : TEAM_FREE;
		capturing = ( cent->currentState.modelindex2 == TEAM_RED || cent->currentState.modelindex2 == TEAM_BLUE ) ?
			(team_t)cent->currentState.modelindex2 : TEAM_FREE;
		if ( owner == TEAM_FREE && capturing == TEAM_FREE && cent->currentState.frame <= 0 &&
				cent->currentState.constantLight <= 0 && cent->currentState.generic1 != 2 ) {
			continue;
		}

		VectorSubtract( cg.refdef.vieworg, cent->lerpOrigin, delta );
		if ( DotProduct( delta, delta ) > radius * radius ) {
			continue;
		}

		pointLabel = CG_DominationPointLabel( cent->currentState.clientNum );
		captureCount = cent->currentState.constantLight;
		if ( captureCount < 0 ) {
			captureCount = 0;
		}

		if ( cent->currentState.generic1 == 2 ) {
			text = va( "Contesting %s", pointLabel );
		} else if ( owner == viewerTeam ) {
			text = va( "Defending %s", pointLabel );
		} else if ( captureCount >= 2 ) {
			text = va( "Capturing %s (%dx)", pointLabel, captureCount );
		} else {
			text = va( "Capturing %s", pointLabel );
		}

		progress = Com_Clamp( 0.0f, 1.0f, (float)cent->currentState.frame / 255.0f );
		activeTeam = ( capturing != TEAM_FREE ) ? capturing : owner;
		if ( activeTeam == TEAM_RED ) {
			barColor[0] = 1.0f;
			barColor[1] = 0.0f;
			barColor[2] = 0.0f;
			barColor[3] = 1.0f;
		} else {
			barColor[0] = 0.0f;
			barColor[1] = 0.5f;
			barColor[2] = 1.0f;
			barColor[3] = 1.0f;
		}

		CG_Text_GetExtents( text, 0.25f, 0, 0, &textWidth, NULL );
		CG_Text_PaintNoAdjust( 320.0f - textWidth / 2.0f, 360.0f, 0.25f, colorWhite, text, 0, 0 );
		CG_FillRect( 258.0f, 365.0f, 125.0f, 12.0f, colorBlack );
		if ( progress > 0.0f ) {
			CG_FillRect( 258.0f, 365.0f, 125.0f * progress, 12.0f, barColor );
		}
		return;
	}
}

/*
=================
CG_WarmupPlayerCountTeamSize
=================
*/
static int CG_WarmupPlayerCountTeamSize( void ) {
	if ( cgs.playerCountTeamSize > 0 ) {
		return cgs.playerCountTeamSize;
	}

	return 1;
}

/*
=================
CG_CountWarmupPlayersByTeam
=================
*/
static void CG_CountWarmupPlayersByTeam( int teamCounts[TEAM_NUM_TEAMS] ) {
	int		i;
	int		team;

	for ( i = 0; i < TEAM_NUM_TEAMS; i++ ) {
		teamCounts[i] = 0;
	}

	for ( i = 0; i < cgs.maxclients; i++ ) {
		if ( !cgs.clientinfo[i].infoValid ) {
			continue;
		}

		team = cgs.clientinfo[i].team;
		if ( team >= TEAM_FREE && team < TEAM_NUM_TEAMS ) {
			teamCounts[team]++;
		}
	}
}

/*
=================
CG_WarmupReadyDeadlineSeconds
=================
*/
static int CG_WarmupReadyDeadlineSeconds( void ) {
	int		remaining;

	if ( cgs.matchReadyUpDeadline <= 0 ) {
		return 0;
	}

	remaining = ( cgs.matchReadyUpDeadline - cg.time ) / 1000 + 1;
	if ( remaining < 0 ) {
		remaining = 0;
	}
	return remaining;
}

/*
=================
CG_WarmupPluralSuffix
=================
*/
static const char *CG_WarmupPluralSuffix( int count ) {
	return ( count == 1 ) ? "" : "s";
}

/*
=================
CG_WarmupTeamsBalanced
=================
*/
static qboolean CG_WarmupTeamsBalanced( const int teamCounts[TEAM_NUM_TEAMS] ) {
	if ( teamCounts[TEAM_RED] > teamCounts[TEAM_BLUE] + 1 ) {
		return qfalse;
	}
	if ( teamCounts[TEAM_BLUE] > teamCounts[TEAM_RED] + 1 ) {
		return qfalse;
	}
	return qtrue;
}

/*
=================
CG_BuildWarmupWaitingStatus

Builds the retail two-line pregame waiting prompt from player counts.
=================
*/
static void CG_BuildWarmupWaitingStatus( int gametype, const int teamCounts[TEAM_NUM_TEAMS],
	char *line1, int line1Size, char *line2, int line2Size ) {
	int		requiredPlayers;
	int		readySeconds;
	int		missingPlayers;

	requiredPlayers = CG_WarmupPlayerCountTeamSize();
	Q_strncpyz( line1, "The wanking will begin", line1Size );
	Q_strncpyz( line2, "when more players are ready.", line2Size );

	if ( gametype == GT_RED_ROVER ) {
		if ( cgs.customSettingsMask & CUSTOM_SETTING_INFECTED ) {
			if ( teamCounts[TEAM_RED] + teamCounts[TEAM_BLUE] < requiredPlayers ) {
				Q_strncpyz( line2, "when more players join.", line2Size );
			}
			return;
		}

		if ( teamCounts[TEAM_RED] < requiredPlayers || teamCounts[TEAM_BLUE] < requiredPlayers ) {
			Q_strncpyz( line2, "when more players join.", line2Size );
		}
		return;
	}

	if ( gametype < GT_TEAM ) {
		if ( gametype == GT_TOURNAMENT && teamCounts[TEAM_FREE] > 2 ) {
			Q_strncpyz( line1, "The wanking will begin when", line1Size );
			Q_strncpyz( line2, "fewer players are in the match.", line2Size );
		} else if ( teamCounts[TEAM_FREE] < 2 ) {
			Q_strncpyz( line2, "when more players join.", line2Size );
		} else {
			readySeconds = CG_WarmupReadyDeadlineSeconds();
			if ( readySeconds > 0 ) {
				Q_strncpyz( line1, "Players must ready", line1Size );
				Com_sprintf( line2, line2Size, "within %i second%s.",
					readySeconds, CG_WarmupPluralSuffix( readySeconds ) );
			}
		}
		return;
	}

	if ( teamCounts[TEAM_RED] < requiredPlayers ) {
		if ( teamCounts[TEAM_BLUE] < requiredPlayers ) {
			Q_strncpyz( line1, "Waiting for more players.", line1Size );
			Com_sprintf( line2, line2Size, "The match requires %i player%s per team.",
				requiredPlayers, CG_WarmupPluralSuffix( requiredPlayers ) );
		} else {
			missingPlayers = requiredPlayers - teamCounts[TEAM_RED];
			Com_sprintf( line1, line1Size, "Waiting for %i more player%s",
				missingPlayers, CG_WarmupPluralSuffix( missingPlayers ) );
			Q_strncpyz( line2, "to join the Red Team.", line2Size );
		}
		return;
	}

	if ( teamCounts[TEAM_BLUE] < requiredPlayers ) {
		missingPlayers = requiredPlayers - teamCounts[TEAM_BLUE];
		Com_sprintf( line1, line1Size, "Waiting for %i more player%s",
			missingPlayers, CG_WarmupPluralSuffix( missingPlayers ) );
		Q_strncpyz( line2, "to join the Blue Team.", line2Size );
		return;
	}

	if ( !CG_WarmupTeamsBalanced( teamCounts ) ) {
		Q_strncpyz( line1, "The teams must be balanced", line1Size );
		Q_strncpyz( line2, "before the match can begin.", line2Size );
	}
}

/*
=================
CG_DrawWarmupTextLine
=================
*/
static void CG_DrawWarmupTextLine( const char *text, float y, float scale ) {
	int		w;

	CG_Text_GetExtents( text, scale, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
	CG_Text_PaintNoAdjust( 320 - w / 2, y, scale, colorWhite, text, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
}

/*
=================
CG_DrawWarmupWaitingStatus
=================
*/
static void CG_DrawWarmupWaitingStatus( int gametype, const int teamCounts[TEAM_NUM_TEAMS],
	float verticalOffset ) {
	char	line1[128];
	char	line2[128];

	if ( !cg_drawPregameMessages.integer ) {
		return;
	}

	CG_BuildWarmupWaitingStatus( gametype, teamCounts, line1, sizeof( line1 ), line2, sizeof( line2 ) );
	CG_DrawWarmupTextLine( line1, 88.0f + verticalOffset, 0.35f );
	CG_DrawWarmupTextLine( line2, 108.0f + verticalOffset, 0.35f );
}

/*
=================
CG_ShouldDrawWarmupReadyPrompt
=================
*/
static qboolean CG_ShouldDrawWarmupReadyPrompt( int gametype, const int teamCounts[TEAM_NUM_TEAMS] ) {
	int		requiredPlayers;
	team_t	localTeam;

	if ( !cg.snap ) {
		return qfalse;
	}

	localTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	if ( localTeam == TEAM_SPECTATOR ) {
		return qfalse;
	}

	requiredPlayers = CG_WarmupPlayerCountTeamSize();
	if ( gametype < GT_TEAM ) {
		return (qboolean)( teamCounts[TEAM_FREE] >= 2 );
	}

	if ( gametype == GT_RED_ROVER && ( cgs.customSettingsMask & CUSTOM_SETTING_INFECTED ) ) {
		return (qboolean)( teamCounts[TEAM_RED] + teamCounts[TEAM_BLUE] >= requiredPlayers );
	}

	return (qboolean)( teamCounts[TEAM_RED] >= requiredPlayers && teamCounts[TEAM_BLUE] >= requiredPlayers );
}

/*
=================
CG_DrawWarmupReadyPrompt
=================
*/
static void CG_DrawWarmupReadyPrompt( int gametype, const int teamCounts[TEAM_NUM_TEAMS],
	float verticalOffset ) {
	char		keyBuf[32];
	const char	*keyName;
	const char	*prompt;

	if ( !CG_ShouldDrawWarmupReadyPrompt( gametype, teamCounts ) ) {
		return;
	}

	keyName = CG_GetBindKeyName( "readyup", keyBuf, sizeof( keyBuf ) );
	if ( cg.snap->ps.eFlags & EF_READY ) {
		prompt = va( "Press %s to unready yourself", keyName );
	} else {
		prompt = va( "Press %s to ready yourself", keyName );
	}

	CG_DrawWarmupTextLine( prompt, 124.0f + verticalOffset, 0.25f );
}

/*
=================
CG_ShouldPlayWarmupCountSound
=================
*/
static qboolean CG_ShouldPlayWarmupCountSound( int gametype ) {
	if ( !CG_IsRoundStartGametype( (gametype_t)gametype ) ) {
		return qtrue;
	}

	if ( gametype == GT_FREEZE && cgs.matchRoundNumber == 0 ) {
		return qtrue;
	}

	return (qboolean)( cgs.matchRoundNumber > 0 );
}

/*
=================
CG_DrawWarmup
=================
*/
static void CG_DrawWarmup( void ) {
	int		sec;

	if ( CG_IsJoinGameMenuCaptureActive() && !cg.scoreBoardShowing ) {
		return;
	}
	if ( cg.showScores || !cg.snap ) {
		return;
	}

	sec = cg.warmup;
	if ( sec == 0 && cgs.matchReadyUpDeadline > 0 ) {
		sec = cgs.matchReadyUpDeadline;
	}
	if ( !sec ) {
		return;
	}

	if ( sec < 0 ) {
		int		teamCounts[TEAM_NUM_TEAMS];
		float	verticalOffset;

		verticalOffset = ( cgs.gametype == GT_RACE ) ? 30.0f : 0.0f;
		CG_CountWarmupPlayersByTeam( teamCounts );
		cg.warmupCount = -1;
		CG_DrawWarmupWaitingStatus( cgs.gametype, teamCounts, verticalOffset );
		CG_DrawWarmupReadyPrompt( cgs.gametype, teamCounts, verticalOffset );
		return;
	}

	sec = ( ( sec - cg.time ) + 1000 ) / 1000;
	if ( sec < 0 ) {
		cg.warmup = 0;
		sec = 0;
	}

	if ( sec != cg.warmupCount ) {
		cg.warmupCount = sec;
		if ( CG_ShouldPlayWarmupCountSound( cgs.gametype ) ) {
			CG_PlayWarmupCountSound( sec );
		}
	}

	if ( sec <= 0 ) {
		return;
	}

	CG_DrawWarmupStatusText( cgs.gametype );
}

//==================================================================================
/* 
=================
CG_DrawTimedMenus
=================
*/
void CG_DrawTimedMenus() {
	if ( cg.voiceMenuTime ) {
		int t = cg.time - cg.voiceMenuTime;

		if ( t > 2500 ) {
			Menus_CloseByName( "voiceMenu" );
			cg.voiceMenuTime = 0;
		}
	}
}

/*
=============
CG_FormatSignedMilliseconds

Formats the retail signed millisecond delta as `[-]m:ss.mmm`.
=============
*/
static const char *CG_FormatSignedMilliseconds( int milliseconds ) {
	unsigned int	absoluteMilliseconds;
	const char		*signPrefix;
	const char		*secondPrefix;
	int			minutes;
	float			seconds;

	signPrefix = "";
	absoluteMilliseconds = (unsigned int)milliseconds;
	if ( milliseconds < 0 ) {
		signPrefix = "-";
		absoluteMilliseconds = (unsigned int)( -( milliseconds + 1 ) ) + 1u;
	}

	minutes = absoluteMilliseconds / 60000u;
	seconds = ( absoluteMilliseconds % 60000u ) / 1000.0f;
	secondPrefix = ( seconds < 10.0f ) ? "0" : "";

	return va( "%s%d:%s%.03f", signPrefix, minutes, secondPrefix, seconds );
}

/*
=============
CG_IsTrainingTutorialSession

Returns qtrue when the current pregame prompt should use the retail training
or tutorial wording.
=============
*/
static qboolean CG_IsTrainingTutorialSession( void ) {
	const char	*info;
	const char	*trainingValue;
	const char	*tutorialName;
	const char	*tutorialText;

	info = CG_ConfigString( CS_SERVERINFO );
	if ( info && info[0] ) {
		trainingValue = Info_ValueForKey( info, "g_training" );
		if ( trainingValue && trainingValue[0] && atoi( trainingValue ) ) {
			return qtrue;
		}
	}

	tutorialName = CG_ConfigString( CS_TUTORIAL_NAME );
	if ( tutorialName && tutorialName[0] ) {
		return qtrue;
	}

	tutorialText = CG_ConfigString( CS_TUTORIAL_TEXT );
	return ( tutorialText && tutorialText[0] ) ? qtrue : qfalse;
}

/*
=============
CG_DrawDemoControlPair

Paints one retail demo-HUD label/key pair centered on the supplied x column.
=============
*/
static void CG_DrawDemoControlPair( float centerX, const char *label, const char *key ) {
	static vec4_t	demoKeyColor = { 1.0f, 1.0f, 0.0f, 1.0f };
	int	labelWidth;
	int	keyWidth;

	if ( label && label[0] ) {
		labelWidth = CG_Text_Width( label, 0.25f, 0 );
		CG_Text_PaintNoAdjust( centerX - labelWidth * 0.5f, 395.0f, 0.25f, colorWhite,
			label, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	}

	if ( key && key[0] ) {
		keyWidth = CG_Text_Width( key, 0.15f, 0 );
		CG_Text_PaintNoAdjust( centerX - keyWidth * 0.5f, 405.0f, 0.15f, demoKeyColor,
			key, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
	}
}

/*
=============
CG_SetIgnoreMouseInput

Keeps the cached `cg_ignoreMouseInput` cvar aligned with the retail overlay
ownership logic.
=============
*/
static void CG_SetIgnoreMouseInput( qboolean ignoreMouseInput ) {
	if ( cg_ignoreMouseInput.integer == (int)ignoreMouseInput ) {
		return;
	}

	trap_Cvar_Set( "cg_ignoreMouseInput", ignoreMouseInput ? "1" : "0" );
}

/*
=============
CG_UpdateTimeoutMouseInput

Mirrors the retail timeout path that suppresses classic-HUD mouse handling
while leaving menu-HUD overlays interactive.
=============
*/
static void CG_UpdateTimeoutMouseInput( qboolean menuHudActive ) {
	if ( CG_GetMatchTimeoutStartTime() != 0 ) {
		if ( cg_ignoreMouseInput.integer == (int)menuHudActive ) {
			CG_SetIgnoreMouseInput( (qboolean)!menuHudActive );
		}
		return;
	}

	if ( cg_ignoreMouseInput.integer != 0 ) {
		CG_SetIgnoreMouseInput( qfalse );
	}
}

/*
=============
CG_HasVisibleMenu

Reports whether any retail browser/menu root is currently visible.
=============
*/
static qboolean CG_HasVisibleMenu( void ) {
	int	i;

	for ( i = 0; i < Menu_Count(); ++i ) {
		if ( Menus[i].window.flags & WINDOW_VISIBLE ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CG_DrawBrowserCursor

Draws the cgame-owned menu cursor while Win32 keeps the system cursor hidden
and captured for raw input.
=============
*/
static void CG_DrawBrowserCursor( void ) {
	qhandle_t	cursor;

	if ( !( trap_Key_GetCatcher() & KEYCATCH_CGAME ) ) {
		return;
	}

	if ( !CG_HasVisibleMenu() ) {
		return;
	}

	cursor = cgs.activeCursor;
	if ( !cursor ) {
		cursor = cgs.media.cursor;
	}
	if ( !cursor ) {
		cursor = cgs.media.selectCursor;
	}
	if ( !cursor ) {
		return;
	}

	trap_R_SetColor( NULL );
	CG_DrawPic( (float)cgs.cursorX - 16.0f, (float)cgs.cursorY - 16.0f, 32.0f, 32.0f, cursor );
}

/*
=============
CG_UpdateSpIntermissionMouseInput

Matches the retail SP intermission path that only re-enables mouse movement
when a visible browser/menu root owns the interaction.
=============
*/
static void CG_UpdateSpIntermissionMouseInput( void ) {
	if ( cg_ignoreMouseInput.integer == 1 ) {
		return;
	}

	if ( CG_HasVisibleMenu() ) {
		CG_SetIgnoreMouseInput( qfalse );
	} else {
		CG_SetIgnoreMouseInput( qtrue );
	}
}

/*
=============
CG_DrawReduced2D

Runs the retail reduced 2D path used while the classic HUD is disabled or the
client is paused.
=============
*/
static void CG_DrawReduced2D( void ) {
	CG_DrawCrosshair();
	CG_DrawCrosshairNames();

	if ( cg_drawSnapshot.integer == 2 ) {
		CG_DrawSnapshot( 0.0f );
	}
}

/*
=============
CG_DrawPregamePlacementPrompt

Draws the retail placement/tutorial prompt shown during the single-player
pregame intermission path.
=============
*/
static void CG_DrawPregamePlacementPrompt( void ) {
	const char	*prompt;
	const char	*keyName;
	float		y;
	char		keyBuf[32];
	int			w;

	if ( !cg.snap || cg.snap->ps.pm_type != PM_SPINTERMISSION ) {
		return;
	}

	keyName = CG_GetBindKeyName( "readyup", keyBuf, sizeof( keyBuf ) );
	if ( CG_IsTrainingTutorialSession() ) {
		prompt = va( "Press %s to skip the tutorial", keyName );
		y = 30.0f;
	} else {
		if ( cg.intermissionStarted != 1 ) {
			return;
		}

		CG_Text_GetExtents( "This match will determine", 0.35f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
		CG_Text_PaintNoAdjust( 320.0f - w * 0.5f, 35.0f, 0.35f, colorWhite,
			"This match will determine", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );

		CG_Text_GetExtents( "your skill placement", 0.35f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
		CG_Text_PaintNoAdjust( 320.0f - w * 0.5f, 55.0f, 0.35f, colorWhite,
			"your skill placement", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );

		prompt = va( "Press %s to start the match", keyName );
		y = 85.0f;
	}

	CG_Text_GetExtents( prompt, 0.25f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );
	CG_Text_PaintNoAdjust( 320.0f - w * 0.5f, y, 0.25f, colorWhite, prompt, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
}

/*
=============
CG_DrawDemoPlaybackControls

Draws the retail playback key legend beneath the classic 2D HUD during demo
playback.
=============
*/
static void CG_DrawDemoPlaybackControls( int panelWidth ) {
	static int	playbackStateDelayFrames;
	const char	*deltaText;
	const char	*stateLabel;
	const char	*speedText;
	float		freezeDemo;
	float		columnOffset;
	vec4_t		panelColor;
	qboolean	showPlaybackControls;

	freezeDemo = trap_Cvar_VariableValue( "cl_freezeDemo" );
	if ( freezeDemo <= 0.0f ) {
		playbackStateDelayFrames++;
		if ( playbackStateDelayFrames >= 4 ) {
			showPlaybackControls = qtrue;
			stateLabel = "Pause";
		} else {
			showPlaybackControls = qfalse;
			stateLabel = "Play";
		}
	} else {
		playbackStateDelayFrames = 0;
		showPlaybackControls = qfalse;
		stateLabel = "Play";
	}

	panelColor[0] = 0.0f;
	panelColor[1] = 0.0f;
	panelColor[2] = 0.0f;
	panelColor[3] = 0.5f;
	CG_FillRect( 210.0f, 355.0f, 220.0f, 60.0f, panelColor );

	columnOffset = panelWidth * 0.5f;

	deltaText = CG_FormatSignedMilliseconds( cg.time - cgs.levelStartTime );
	CG_Text_PaintNoAdjust( 288.0f, 375.0f, 0.30f, colorWhite, deltaText, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );

	CG_DrawDemoControlPair( 235.0f - columnOffset, stateLabel, "[SPACE]" );

	if ( showPlaybackControls ) {
		CG_DrawDemoControlPair( 275.0f - columnOffset, "-", "[LEFT]" );

		speedText = va( "%0.1fx", cg_timescale.value );
		CG_Text_PaintNoAdjust( 290.0f, 395.0f, 0.25f, colorWhite, speedText, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );
		CG_DrawDemoControlPair( 330.0f - columnOffset, "+", "[RIGHT]" );
		CG_DrawDemoControlPair( 370.0f - columnOffset, "1.0x", "[DOWN]" );
	} else {
		CG_DrawDemoControlPair( 320.0f - columnOffset, "Advance", "[RIGHT]" );
	}

	CG_DrawDemoControlPair( 410.0f - columnOffset, "Hide", "[DEL]" );
}

/*
=============
CG_DrawStatsMenu

Paints the retail `stats_menu` overlay that backs the `+acc` HUD request.
=============
*/
static qboolean CG_DrawStatsMenu( void ) {
	if ( !menuStats ) {
		menuStats = CG_FindBrowserOverlayByName( "stats_menu" );
	}

	if ( menuStats ) {
		menuStats->window.flags &= ~WINDOW_FORCED;
	}

	if ( !CG_ShouldDrawAccOverlay() || !menuStats ) {
		return qfalse;
	}

	CG_DrawBrowserOverlayTree( menuStats, qtrue );
	return qtrue;
}

/*
=============================
CG_ComputeIntermissionLetterboxHeight

Evaluates the current retail intermission letterbox height from the cached
transition state.
=============================
*/
static float CG_ComputeIntermissionLetterboxHeight( void ) {
	int		elapsed;
	float	fraction;

	if ( cg.intermissionLetterboxDuration <= 0 ||
		 cg.intermissionLetterboxStartHeight == cg.intermissionLetterboxTargetHeight ) {
		cg.intermissionLetterboxStartHeight = cg.intermissionLetterboxTargetHeight;
		cg.intermissionLetterboxDuration = 0;
		return cg.intermissionLetterboxTargetHeight;
	}

	elapsed = cg.time - cg.intermissionLetterboxChangeTime;
	if ( elapsed <= 0 ) {
		return cg.intermissionLetterboxStartHeight;
	}
	if ( elapsed >= cg.intermissionLetterboxDuration ) {
		cg.intermissionLetterboxStartHeight = cg.intermissionLetterboxTargetHeight;
		cg.intermissionLetterboxDuration = 0;
		return cg.intermissionLetterboxTargetHeight;
	}

	fraction = (float)elapsed / (float)cg.intermissionLetterboxDuration;
	return cg.intermissionLetterboxStartHeight +
		( cg.intermissionLetterboxTargetHeight - cg.intermissionLetterboxStartHeight ) * fraction;
}

/*
============================
CG_DrawIntermissionLetterbox

Draws the retail top/bottom intermission letterbox transition beneath CG_Draw2D.
============================
*/
static void CG_DrawIntermissionLetterbox( void ) {
	qboolean	intermissionLatched;
	float		targetHeight;
	float		height;

	intermissionLatched = qfalse;
	if ( cg.intermissionStarted ) {
		intermissionLatched = qtrue;
	}
	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		intermissionLatched = qtrue;
	}

	targetHeight = intermissionLatched ? 84.0f : 0.0f;
	if ( targetHeight != cg.intermissionLetterboxTargetHeight ) {
		cg.intermissionLetterboxStartHeight = CG_ComputeIntermissionLetterboxHeight();
		cg.intermissionLetterboxTargetHeight = targetHeight;
		cg.intermissionLetterboxChangeTime = cg.time;
		cg.intermissionLetterboxDuration = 1000;
	}

	height = CG_ComputeIntermissionLetterboxHeight();
	if ( height > 0.0f && height < 1.0f ) {
		height = 1.0f;
	}
	if ( height <= 0.0f ) {
		return;
	}

	CG_FillRect( 0, 0, 640, height, colorBlack );
	CG_FillRect( 0, 480 - height, 640, height, colorBlack );
}
/*
=================
CG_Draw2D
=================
*/
static void CG_Draw2D( void ) {
	int			freezeDemo;
	qboolean		spectator;
	qboolean		menuHudActive;
	qboolean		canShowStatus;
	qboolean		menuScoreboardHandled;
	qboolean		joinGameCaptureActive;

	if (cgs.orderPending && cg.time > cgs.orderTime) {
		CG_CheckOrderPending();
	}

	freezeDemo = (int)trap_Cvar_VariableValue( "cl_freezeDemo" );

	// if we are taking a levelshot for the menu, don't draw anything
	if ( cg.levelShot ) {
		return;
	}

	menuHudActive = CG_IsMenuHudActive();
	if ( cg.demoPlayback && !cg_drawDemoHUD.integer ) {
		menuHudActive = qfalse;
	}

	CG_UpdateTimeoutMouseInput( menuHudActive );

	if ( cg_draw2D.integer == 0 || cg_paused.integer ) {
		CG_DrawReduced2D();
		return;
	}

	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		if ( CG_IsJoinGameMenuCaptureActive() ) {
			CG_CloseJoinGameMenu();
		}
		if ( cg_ignoreMouseInput.integer != 0 ) {
			CG_SetIgnoreMouseInput( qfalse );
		}
		CG_DrawIntermissionLetterbox();
		CG_DrawIntermission();
		return;
	}

	if ( cg.snap->ps.pm_type == PM_SPINTERMISSION ) {
		CG_DrawIntermissionLetterbox();
		CG_DrawPregameJoinGameMenu();
		CG_DrawCenterString();
		CG_DrawPregamePlacementPrompt();
		CG_UpdateSpIntermissionMouseInput();
		CG_DrawBrowserCursor();
		return;
	}

	CG_DrawIntermissionLetterbox();

	spectator = ( qboolean )( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR );
	canShowStatus = ( qboolean )( !cg.showScores && cg.snap->ps.stats[STAT_HEALTH] > 0 );
	menuScoreboardHandled = qfalse;
	joinGameCaptureActive = (qboolean)( CG_IsJoinGameMenuCaptureActive() && !cg.scoreBoardShowing );
	cg_spectatorItemPickupBaseY = 0.0f;

	if ( menuHudActive && cg_drawStatus.integer && ( spectator || canShowStatus ) ) {
		CG_DrawBrowserOverlays();
		CG_DrawTimedMenus();
	}

	if ( !cg.demoPlayback || freezeDemo == 0 ) {
		CG_DrawQueuedWorldMarkers();
	}

	if ( joinGameCaptureActive ) {
		CG_DrawJoinGameMenu();
	} else if ( spectator ) {
		if ( !menuHudActive ) {
			CG_DrawSpectator();
		}
		CG_DrawCrosshair();
		CG_DrawCrosshairNames();
	} else {
		if ( canShowStatus ) {
			if ( !menuHudActive ) {
				CG_DrawAmmoWarning();
				CG_DrawProxWarning();
				CG_DrawReward();
			}
			CG_DrawWeaponSelect();
			CG_DrawCrosshair();
			CG_DrawCrosshairNames();
		}

		if ( cgs.gametype >= GT_TEAM ) {
			CG_DrawTeammatePOIs();
		}
	}

	if ( menuHudActive ) {
		if ( cg.showScores ) {
			cg.scoreBoardShowing = CG_DrawActiveScoreboard( qtrue, qfalse );
			if ( !cg.scoreBoardShowing && !CG_IsJoinGameMenuCaptureActive() ) {
				CG_DrawCenterString();
			}
		} else {
			cg.scoreBoardShowing = qfalse;
			if ( !CG_IsJoinGameMenuCaptureActive() ) {
				CG_DrawCenterString();
			}
		}
		menuScoreboardHandled = qtrue;
	}

	CG_DrawLagometer();
	if ( !cg.renderingThirdPerson ) {
		CG_DrawDisconnect();
	}

	if (!cg_paused.integer) {
		if ( !menuHudActive ) {
			CG_DrawInputCmds();
			CG_DrawSpeedometer();
		}

		CG_DrawVote();
		CG_DrawUpperRight();
		CG_DrawSpectatorItemPickups();
		if ( cgs.gametype >= GT_TEAM && cg_drawTeamOverlay.integer == 2 ) {
			CG_DrawTeamOverlay( 408.0f, qtrue, qfalse );
		}

		if ( !menuHudActive ) {
			CG_DrawLowerRight();
			CG_DrawLowerLeft();
		}
	}


	if ( !CG_DrawFollow() ) {
		CG_DrawDominationPointStatus();
		CG_DrawMatchPauseStatus();
		CG_DrawWarmup();
	}
	CG_DrawTeamInfo();

	if ( cgs.gametype == GT_RACE ) {
		CG_DrawRacePoints();
	}

	// don't draw center string if scoreboard is up
	if ( !menuScoreboardHandled ) {
		cg.scoreBoardShowing = CG_DrawActiveScoreboard( qfalse, qfalse );
		if ( !cg.scoreBoardShowing && !CG_IsJoinGameMenuCaptureActive() ) {
			CG_DrawCenterString();
		}
	}

	CG_DrawStatsMenu();
	CG_DrawObituaries( 150.0f );

	if ( cg.demoPlayback && cg_drawDemoHUD.integer ) {
		CG_DrawDemoPlaybackControls( 0 );
	}

	CG_DrawBrowserCursor();
}

/*
=====================
CG_DrawActive

Perform all drawing needed to completely fill the screen
=====================
*/
void CG_DrawActive( stereoFrame_t stereoView ) {
	float		separation;
	int		pmType;
	vec3_t		baseOrg;
	float		browserActive;

	cg_drawActiveMilliseconds = trap_Milliseconds();

	// optionally draw the info screen instead
	if ( !cg.snap ) {
		CG_DrawInformation();
		return;
	}

	switch ( stereoView ) {
	case STEREO_CENTER:
		separation = 0;
		break;
	case STEREO_LEFT:
		separation = -cg_stereoSeparation.value / 2;
		break;
	case STEREO_RIGHT:
		separation = cg_stereoSeparation.value / 2;
		break;
	default:
		separation = 0;
		CG_Error( "CG_DrawActive: Undefined stereoView" );
	}


	// clear around the rendered view if sized down
	CG_TileClear();

	pmType = cg.predictedPlayerState.pm_type;
	if ( ( ( pmType == PM_DEAD || pmType == PM_FREEZE ) && cg.renderingThirdPerson )
		|| pmType == PM_INTERMISSION ) {
		cg.zoomed = qfalse;
	}

	// offset vieworg appropriately if we're doing stereo separation
	VectorCopy( cg.refdef.vieworg, baseOrg );
	if ( separation != 0 ) {
		VectorMA( cg.refdef.vieworg, -separation, cg.refdef.viewaxis[1], cg.refdef.vieworg );
	}

	// draw 3D view
	trap_QL_AdvertisementBridge_UpdateViewParameters();
	trap_R_RenderScene( &cg.refdef );
	trap_QL_AdvertisementBridge_ClearDelay();

	// restore original viewpoint if running stereo
	if ( separation != 0 ) {
		VectorCopy( baseOrg, cg.refdef.vieworg );
	}

	// draw status bar and other floating elements
	browserActive = trap_Cvar_VariableValue( "web_browserActive" );
	if ( browserActive == 0.0f ) {
		if ( !cg.renderingThirdPerson ) {
			CG_DrawScreenVignette();
		}
		CG_Draw2D();
	}
}



