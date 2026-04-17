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
// tr_init.c -- functions that are not called every frame

#include "tr_local.h"

glconfig_t	glConfig;
glstate_t	glState;

static void GfxInfo_f( void );

cvar_t	*r_flareSize;
cvar_t	*r_flareFade;

cvar_t	*r_railWidth;
cvar_t	*r_railCoreWidth;
cvar_t	*r_railSegmentLength;

cvar_t	*r_ignoreFastPath;

cvar_t	*r_verbose;
cvar_t	*r_ignore;

cvar_t	*r_displayRefresh;

cvar_t	*r_detailTextures;

cvar_t	*r_znear;

cvar_t	*r_smp;
cvar_t	*r_showSmp;
cvar_t	*r_skipBackEnd;

cvar_t	*r_ignorehwgamma;
cvar_t	*r_measureOverdraw;

cvar_t	*r_inGameVideo;
cvar_t	*r_fastsky;
cvar_t	*r_drawSun;
cvar_t	*r_dynamiclight;
cvar_t	*r_dlightBacks;

cvar_t	*r_lodbias;
cvar_t	*r_lodscale;

cvar_t	*r_norefresh;
cvar_t	*r_drawentities;
cvar_t	*r_drawworld;
cvar_t	*r_speeds;
cvar_t	*r_fullbright;
cvar_t	*r_novis;
cvar_t	*r_nocull;
cvar_t	*r_facePlaneCull;
cvar_t	*r_showcluster;
cvar_t	*r_nocurves;

cvar_t	*r_allowExtensions;

cvar_t	*r_ext_compressed_textures;
cvar_t	*r_ext_gamma_control;
cvar_t	*r_ext_multitexture;
cvar_t	*r_ext_compiled_vertex_array;
cvar_t	*r_ext_texture_env_add;

cvar_t	*r_ignoreGLErrors;
cvar_t	*r_logFile;

cvar_t	*r_stencilbits;
cvar_t	*r_depthbits;
cvar_t	*r_colorbits;
cvar_t	*r_stereo;
cvar_t	*r_primitives;
cvar_t	*r_texturebits;

cvar_t	*r_enablePostProcess;
cvar_t	*r_enableBloom;
cvar_t	*r_enableColorCorrect;
cvar_t	*r_postProcessActive;
cvar_t	*r_bloomActive;
cvar_t	*r_bloomPasses;
cvar_t	*r_bloomIntensity;
cvar_t	*r_bloomBrightThreshold;
cvar_t	*r_bloomBlurScale;
cvar_t	*r_bloomBlurRadius;
cvar_t	*r_bloomBlurFalloff;
cvar_t	*r_bloomSaturation;
cvar_t	*r_bloomSceneIntensity;
cvar_t	*r_bloomSceneSaturation;
cvar_t	*r_colorCorrectActive;

static void R_InitColorCorrection( void );
static void R_ShutdownColorCorrection( void );

cvar_t	*r_drawBuffer;
cvar_t  *r_glDriver;
cvar_t	*r_lightmap;
cvar_t	*r_vertexLight;
cvar_t	*r_uiFullScreen;
cvar_t	*r_shadows;
cvar_t	*r_flares;
cvar_t	*r_mode;
cvar_t	*r_nobind;
cvar_t	*r_singleShader;
cvar_t	*r_roundImagesDown;
cvar_t	*r_colorMipLevels;
cvar_t	*r_picmip;
cvar_t	*r_showtris;
cvar_t	*r_showsky;
cvar_t	*r_shownormals;
cvar_t	*r_finish;
cvar_t	*r_clear;
cvar_t	*r_swapInterval;
cvar_t	*r_textureMode;
cvar_t	*r_offsetFactor;
cvar_t	*r_offsetUnits;
cvar_t	*r_gamma;
cvar_t	*r_contrast;
cvar_t	*r_intensity;
cvar_t	*r_lockpvs;
cvar_t	*r_noportals;
cvar_t	*r_portalOnly;

cvar_t	*r_subdivisions;
cvar_t	*r_lodCurveError;

cvar_t	*r_fullscreen;

cvar_t	*r_customwidth;
cvar_t	*r_customheight;
cvar_t	*r_customaspect;

cvar_t	*r_overBrightBits;
cvar_t	*r_mapOverBrightBits;

cvar_t	*r_debugSurface;
cvar_t	*r_simpleMipMaps;

cvar_t	*r_showImages;

cvar_t	*r_ambientScale;
cvar_t	*r_aspectRatio;
cvar_t	*r_directedScale;
cvar_t	*r_debugLight;
cvar_t	*r_debugFontAtlas;
cvar_t	*r_debugSort;
cvar_t	*r_printShaders;
cvar_t	*r_saveFontData;

cvar_t	*r_drawSkyFloor;
cvar_t	*r_noFastRestart;
cvar_t	*r_skipLargeBatches;
cvar_t	*r_skipSmallBatches;
cvar_t	*r_teleporterFlash;
cvar_t	*r_windowedMode;
cvar_t	*r_windowedWidth;
cvar_t	*r_windowedHeight;

cvar_t	*r_maxpolys;
int		max_polys;
cvar_t	*r_maxpolyverts;
int		max_polyverts;

void ( APIENTRY * qglMultiTexCoord2fARB )( GLenum texture, GLfloat s, GLfloat t );
void ( APIENTRY * qglActiveTextureARB )( GLenum texture );
void ( APIENTRY * qglClientActiveTextureARB )( GLenum texture );

void ( APIENTRY * qglLockArraysEXT)( GLint, GLint);
void ( APIENTRY * qglUnlockArraysEXT) ( void );

/*
=============
R_InitColorCorrection

Initialize an identity color-correction matrix for post-process rendering.
=============
*/
static void R_InitColorCorrection( void ) {
	int		index;
	float	*matrix;

	matrix = tr.colorCorrectMatrix;

	for ( index = 0; index < 16; index++ ) {
		matrix[index] = 0.0f;
	}

	matrix[0] = 1.0f;
	matrix[5] = 1.0f;
	matrix[10] = 1.0f;
	matrix[15] = 1.0f;

	tr.colorCorrectReady = qtrue;
}


/*
=============
R_ShutdownColorCorrection

Reset color-correction resources tracked for post-process rendering.
=============
*/
static void R_ShutdownColorCorrection( void ) {
	Com_Memset( tr.colorCorrectMatrix, 0, sizeof( tr.colorCorrectMatrix ) );

	tr.colorCorrectReady = qfalse;
}

static void AssertCvarRange( cvar_t *cv, float minVal, float maxVal, qboolean shouldBeIntegral )
{
	if ( shouldBeIntegral )
	{
		if ( ( int ) cv->value != cv->integer )
		{
			ri.Printf( PRINT_WARNING, "WARNING: cvar '%s' must be integral (%f)\n", cv->name, cv->value );
			ri.Cvar_Set( cv->name, va( "%d", cv->integer ) );
		}
	}

	if ( cv->value < minVal )
	{
		ri.Printf( PRINT_WARNING, "WARNING: cvar '%s' out of range (%f < %f)\n", cv->name, cv->value, minVal );
		ri.Cvar_Set( cv->name, va( "%f", minVal ) );
	}
	else if ( cv->value > maxVal )
	{
		ri.Printf( PRINT_WARNING, "WARNING: cvar '%s' out of range (%f > %f)\n", cv->name, cv->value, maxVal );
		ri.Cvar_Set( cv->name, va( "%f", maxVal ) );
	}
}


/*
=============
R_ClampRendererCvars

Apply HLIL-observed Quake Live ranges to renderer CVars.
=============
*/
static void R_ClampRendererCvars( void )
{
	if ( r_picmip )
	{
		AssertCvarRange( r_picmip, 0, 16, qtrue );
	}

	if ( r_displayRefresh )
	{
		AssertCvarRange( r_displayRefresh, 0, 240, qtrue );
	}

	if ( r_znear )
	{
		AssertCvarRange( r_znear, 0.001f, 200, qtrue );
	}

	if ( r_ambientScale )
	{
		AssertCvarRange( r_ambientScale, 1, 100, qtrue );
	}

	if ( r_lodbias )
	{
		AssertCvarRange( r_lodbias, -2, 2, qtrue );
	}

	if ( r_lodscale )
	{
		AssertCvarRange( r_lodscale, 1, 50, qtrue );
	}

	if ( r_aspectRatio )
	{
		AssertCvarRange( r_aspectRatio, 0, 3, qtrue );
	}

	if ( r_bloomPasses )
	{
		AssertCvarRange( r_bloomPasses, 1, 2, qtrue );
	}

	if ( r_bloomIntensity )
	{
		AssertCvarRange( r_bloomIntensity, 0.0f, 10.0f, qfalse );
	}

	if ( r_bloomBrightThreshold )
	{
		AssertCvarRange( r_bloomBrightThreshold, 0.0f, 1.0f, qfalse );
	}

	if ( r_bloomBlurScale )
	{
		AssertCvarRange( r_bloomBlurScale, 1.0f, 2.0f, qfalse );
	}

	if ( r_bloomBlurRadius )
	{
		AssertCvarRange( r_bloomBlurRadius, 1, 12, qtrue );
	}

	if ( r_bloomBlurFalloff )
	{
		AssertCvarRange( r_bloomBlurFalloff, 0.75f, 1.0f, qfalse );
	}

	if ( r_bloomSaturation )
	{
		AssertCvarRange( r_bloomSaturation, 0.0f, 10.0f, qfalse );
	}

	if ( r_bloomSceneIntensity )
	{
		AssertCvarRange( r_bloomSceneIntensity, 0.0f, 10.0f, qfalse );
	}

	if ( r_bloomSceneSaturation )
	{
		AssertCvarRange( r_bloomSceneSaturation, 0.0f, 10.0f, qfalse );
	}

	if ( r_teleporterFlash )
	{
		AssertCvarRange( r_teleporterFlash, 0, 1, qtrue );
	}

	if ( r_skipLargeBatches )
	{
		AssertCvarRange( r_skipLargeBatches, 0, 1, qtrue );
	}

	if ( r_skipSmallBatches )
	{
		AssertCvarRange( r_skipSmallBatches, 0, 1, qtrue );
	}

	if ( r_noFastRestart )
	{
		AssertCvarRange( r_noFastRestart, 0, 1, qtrue );
	}

	if ( r_drawSkyFloor )
	{
		AssertCvarRange( r_drawSkyFloor, 0, 1, qtrue );
	}
}


/*
** InitOpenGL
**
** This function is responsible for initializing a valid OpenGL subsystem.  This
** is done by calling GLimp_Init (which gives us a working OGL subsystem) then
** setting variables, checking GL constants, and reporting the gfx system config
** to the user.
*/
static void InitOpenGL( void )
{
	char renderer_buffer[1024];

	//
	// initialize OS specific portions of the renderer
	//
	// GLimp_Init directly or indirectly references the following cvars:
	//		- r_fullscreen
	//		- r_glDriver
	//		- r_mode
	//		- r_(color|depth|stencil)bits
	//		- r_ignorehwgamma
	//		- r_gamma
	//
	
	if ( glConfig.vidWidth == 0 )
	{
		GLint		temp;
		
		GLimp_Init();

		strcpy( renderer_buffer, glConfig.renderer_string );
		Q_strlwr( renderer_buffer );

		// OpenGL driver constants
		qglGetIntegerv( GL_MAX_TEXTURE_SIZE, &temp );
		glConfig.maxTextureSize = temp;

		// stubbed or broken drivers may have reported 0...
		if ( glConfig.maxTextureSize <= 0 ) 
		{
			glConfig.maxTextureSize = 0;
		}
	}

	// init command buffers and SMP
	R_InitCommandBuffers();

	// print info
	GfxInfo_f();

	// set default state
	GL_SetDefaultState();
}

/*
==================
GL_CheckErrors
==================
*/
void GL_CheckErrors( void ) {
    int		err;
    char	s[64];

    err = qglGetError();
    if ( err == GL_NO_ERROR ) {
        return;
    }
    if ( r_ignoreGLErrors->integer ) {
        return;
    }
    switch( err ) {
        case GL_INVALID_ENUM:
            strcpy( s, "GL_INVALID_ENUM" );
            break;
        case GL_INVALID_VALUE:
            strcpy( s, "GL_INVALID_VALUE" );
            break;
        case GL_INVALID_OPERATION:
            strcpy( s, "GL_INVALID_OPERATION" );
            break;
        case GL_STACK_OVERFLOW:
            strcpy( s, "GL_STACK_OVERFLOW" );
            break;
        case GL_STACK_UNDERFLOW:
            strcpy( s, "GL_STACK_UNDERFLOW" );
            break;
        case GL_OUT_OF_MEMORY:
            strcpy( s, "GL_OUT_OF_MEMORY" );
            break;
        default:
            Com_sprintf( s, sizeof(s), "%i", err);
            break;
    }

    ri.Error( ERR_FATAL, "GL_CheckErrors: %s", s );
}


/*
** R_GetModeInfo
*/
typedef struct vidmode_s
{
    const char *description;
    int         width, height;
	float		pixelAspect;		// pixel width / height
} vidmode_t;

vidmode_t r_vidModes[] =
{
    { "Mode  0: 320x240",		320,	240,	1 },
    { "Mode  1: 400x300",		400,	300,	1 },
    { "Mode  2: 512x384",		512,	384,	1 },
    { "Mode  3: 640x360",		640,	360,	1 },
    { "Mode  4: 640x400",		640,	400,	1 },
    { "Mode  5: 640x480",		640,	480,	1 },
    { "Mode  6: 800x450",		800,	450,	1 },
    { "Mode  7: 852x480",		852,	480,	1 },
    { "Mode  8: 800x500",		800,	500,	1 },
    { "Mode  9: 800x600",		800,	600,	1 },
    { "Mode 10: 1024x640",		1024,	640,	1 },
    { "Mode 11: 1024x576",		1024,	576,	1 },
    { "Mode 12: 1024x768",		1024,	768,	1 },
    { "Mode 13: 1152x864",		1152,	864,	1 },
    { "Mode 14: 1280x720",		1280,	720,	1 },
    { "Mode 15: 1280x768",		1280,	768,	1 },
    { "Mode 16: 1280x800",		1280,	800,	1 },
    { "Mode 17: 1280x1024",		1280,	1024,	1 },
    { "Mode 18: 1440x900",		1440,	900,	1 },
    { "Mode 19: 1600x900",		1600,	900,	1 },
    { "Mode 20: 1600x1000",		1600,	1000,	1 },
    { "Mode 21: 1680x1050",		1680,	1050,	1 },
    { "Mode 22: 1600x1200",		1600,	1200,	1 },
    { "Mode 23: 1920x1080",		1920,	1080,	1 },
    { "Mode 24: 1920x1200",		1920,	1200,	1 },
    { "Mode 25: 1920x1440",		1920,	1440,	1 },
    { "Mode 26: 2048x1536",		2048,	1536,	1 },
    { "Mode 27: 2560x1600",		2560,	1600,	1 }
};
static int	s_numVidModes = ( sizeof( r_vidModes ) / sizeof( r_vidModes[0] ) );

/*
=============
R_IsValidMode
=============
*/
static qboolean R_IsValidMode( int mode )
{
	if ( mode < -1 ) {
		return qfalse;
	}

	if ( mode >= s_numVidModes ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
R_GetMode
=============
*/
int R_GetMode( void )
{
	if ( r_fullscreen && !r_fullscreen->integer && r_windowedMode ) {
		return r_windowedMode->integer;
	}

	if ( r_mode ) {
		return r_mode->integer;
	}

	return 3;
}

/*
=============
R_GetModeInfo
=============
*/
qboolean R_GetModeInfo( int *width, int *height, float *windowAspect, int mode, qboolean fullscreen ) {
	vidmode_t	*vm;

	if ( !R_IsValidMode( mode ) ) {
		return qfalse;
	}

	if ( mode == -1 ) {
		if ( fullscreen ) {
			*width = r_customwidth->integer;
			*height = r_customheight->integer;
		} else {
			*width = r_windowedWidth->integer;
			*height = r_windowedHeight->integer;
		}

		if ( *width <= 0 || *height <= 0 ) {
			return qfalse;
		}

		*windowAspect = (float)*width / (float)*height;
		return qtrue;
	}

	vm = &r_vidModes[mode];

    *width  = vm->width;
    *height = vm->height;
    *windowAspect = (float)vm->width / ( vm->height * vm->pixelAspect );

    return qtrue;
}

/*
====================
R_ValidateModeCvars
====================
*/
static void R_ValidateModeCvars( void )
{
	if ( r_mode && !R_IsValidMode( r_mode->integer ) ) {
		ri.Printf( PRINT_WARNING, "WARNING: invalid r_mode %d, resetting to 3\n", r_mode->integer );
		ri.Cvar_Set( "r_mode", "3" );
	}

	if ( r_windowedMode && !R_IsValidMode( r_windowedMode->integer ) ) {
		ri.Printf( PRINT_WARNING, "WARNING: invalid r_windowedMode %d, resetting to 12\n", r_windowedMode->integer );
		ri.Cvar_Set( "r_windowedMode", "12" );
	}

	if ( r_customwidth && r_customwidth->integer <= 0 ) {
		ri.Printf( PRINT_WARNING, "WARNING: invalid r_customwidth %d, resetting to 1600\n", r_customwidth->integer );
		ri.Cvar_Set( "r_customwidth", "1600" );
	}

	if ( r_customheight && r_customheight->integer <= 0 ) {
		ri.Printf( PRINT_WARNING, "WARNING: invalid r_customheight %d, resetting to 1024\n", r_customheight->integer );
		ri.Cvar_Set( "r_customheight", "1024" );
	}

	if ( r_windowedWidth && r_windowedWidth->integer <= 0 ) {
		ri.Printf( PRINT_WARNING, "WARNING: invalid r_windowedWidth %d, resetting to 1600\n", r_windowedWidth->integer );
		ri.Cvar_Set( "r_windowedWidth", "1600" );
	}

	if ( r_windowedHeight && r_windowedHeight->integer <= 0 ) {
		ri.Printf( PRINT_WARNING, "WARNING: invalid r_windowedHeight %d, resetting to 1024\n", r_windowedHeight->integer );
		ri.Cvar_Set( "r_windowedHeight", "1024" );
	}
}

/*
** R_ModeList_f
*/
static void R_ModeList_f( void )
{
	int i;

	ri.Printf( PRINT_ALL, "\n" );
	for ( i = 0; i < s_numVidModes; i++ )
	{
		ri.Printf( PRINT_ALL, "%s\n", r_vidModes[i].description );
	}
	ri.Printf( PRINT_ALL, "\n" );
}


/* 
============================================================================== 
 
						SCREEN SHOTS 

NOTE TTimo
some thoughts about the screenshots system:
screenshots get written in fs_homepath + fs_gamedir
vanilla q3 .. baseq3/screenshots/ *.tga
team arena .. missionpack/screenshots/ *.tga

two commands: "screenshot" and "screenshotJPEG"
we use statics to store a count and start writing the first screenshot/screenshot????.tga (.jpg) available
(with FS_FileExists / FS_FOpenFileWrite calls)
FIXME: the statics don't get a reinit between fs_game changes

============================================================================== 
*/ 

/* 
================== 
RB_TakeScreenshot
================== 
*/  
void RB_TakeScreenshot( int x, int y, int width, int height, char *fileName ) {
	byte		*buffer;
	int			i, c, temp;
	GLint		readBuffer;
		
	buffer = ri.Hunk_AllocateTempMemory(glConfig.vidWidth*glConfig.vidHeight*3+18);

	Com_Memset (buffer, 0, 18);
	buffer[2] = 2;		// uncompressed type
	buffer[12] = width & 255;
	buffer[13] = width >> 8;
	buffer[14] = height & 255;
	buffer[15] = height >> 8;
	buffer[16] = 24;	// pixel size

	qglGetIntegerv( GL_READ_BUFFER, &readBuffer );
	qglReadBuffer( GL_FRONT );
	qglReadPixels( x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE, buffer+18 ); 
	qglReadBuffer( readBuffer );

	// swap rgb to bgr
	c = 18 + width * height * 3;
	for (i=18 ; i<c ; i+=3) {
		temp = buffer[i];
		buffer[i] = buffer[i+2];
		buffer[i+2] = temp;
	}

	// gamma correct
	if ( ( tr.overbrightBits > 0 ) && glConfig.deviceSupportsGamma ) {
		R_GammaCorrect( buffer + 18, glConfig.vidWidth * glConfig.vidHeight * 3 );
	}

	ri.FS_WriteFile( fileName, buffer, c );

	ri.Hunk_FreeTempMemory( buffer );
}

/* 
================== 
RB_TakeScreenshotJPEG
================== 
*/  
void RB_TakeScreenshotJPEG( int x, int y, int width, int height, char *fileName ) {
	byte		*buffer;
	GLint		readBuffer;

	buffer = ri.Hunk_AllocateTempMemory(glConfig.vidWidth*glConfig.vidHeight*4);

	qglGetIntegerv( GL_READ_BUFFER, &readBuffer );
	qglReadBuffer( GL_FRONT );
	qglReadPixels( x, y, width, height, GL_RGBA, GL_UNSIGNED_BYTE, buffer ); 
	qglReadBuffer( readBuffer );

	// gamma correct
	if ( ( tr.overbrightBits > 0 ) && glConfig.deviceSupportsGamma ) {
		R_GammaCorrect( buffer, glConfig.vidWidth * glConfig.vidHeight * 4 );
	}

	ri.FS_WriteFile( fileName, buffer, 1 );		// create path
	SaveJPG( fileName, 95, glConfig.vidWidth, glConfig.vidHeight, buffer);

	ri.Hunk_FreeTempMemory( buffer );
}

/*
==================
RB_TakeScreenshotCmd
==================
*/
const void *RB_TakeScreenshotCmd( const void *data ) {
	const screenshotCommand_t	*cmd;
	
	cmd = (const screenshotCommand_t *)data;
	
	if (cmd->jpeg)
		RB_TakeScreenshotJPEG( cmd->x, cmd->y, cmd->width, cmd->height, cmd->fileName);
	else
		RB_TakeScreenshot( cmd->x, cmd->y, cmd->width, cmd->height, cmd->fileName);
	
	return (const void *)(cmd + 1);	
}

/*
==================
R_TakeScreenshot
==================
*/
void R_TakeScreenshot( int x, int y, int width, int height, char *name, qboolean jpeg ) {
	static char	fileName[MAX_OSPATH]; // bad things if two screenshots per frame?
	screenshotCommand_t	*cmd;

	cmd = R_GetCommandBuffer( sizeof( *cmd ) );
	if ( !cmd ) {
		return;
	}
	cmd->commandId = RC_SCREENSHOT;

	cmd->x = x;
	cmd->y = y;
	cmd->width = width;
	cmd->height = height;
	Q_strncpyz( fileName, name, sizeof(fileName) );
	cmd->fileName = fileName;
	cmd->jpeg = jpeg;
}

/* 
================== 
R_ScreenshotFilename
================== 
*/  
void R_ScreenshotFilename( int lastNumber, char *fileName ) {
	int		a,b,c,d;

	if ( lastNumber < 0 || lastNumber > 9999 ) {
		Com_sprintf( fileName, MAX_OSPATH, "screenshots/shot9999.tga" );
		return;
	}

	a = lastNumber / 1000;
	lastNumber -= a*1000;
	b = lastNumber / 100;
	lastNumber -= b*100;
	c = lastNumber / 10;
	lastNumber -= c*10;
	d = lastNumber;

	Com_sprintf( fileName, MAX_OSPATH, "screenshots/shot%i%i%i%i.tga"
		, a, b, c, d );
}

/* 
================== 
R_ScreenshotFilename
================== 
*/  
void R_ScreenshotFilenameJPEG( int lastNumber, char *fileName ) {
	int		a,b,c,d;

	if ( lastNumber < 0 || lastNumber > 9999 ) {
		Com_sprintf( fileName, MAX_OSPATH, "screenshots/shot9999.jpg" );
		return;
	}

	a = lastNumber / 1000;
	lastNumber -= a*1000;
	b = lastNumber / 100;
	lastNumber -= b*100;
	c = lastNumber / 10;
	lastNumber -= c*10;
	d = lastNumber;

	Com_sprintf( fileName, MAX_OSPATH, "screenshots/shot%i%i%i%i.jpg"
		, a, b, c, d );
}

/*
====================
R_LevelShot

levelshots are specialized 128*128 thumbnails for
the menu system, sampled down from full screen distorted images
====================
*/
void R_LevelShot( void ) {
	char		checkname[MAX_OSPATH];
	byte		*buffer;
	byte		*source;
	byte		*src, *dst;
	int			x, y;
	int			r, g, b;
	float		xScale, yScale;
	int			xx, yy;
	GLint		readBuffer;

	sprintf( checkname, "levelshots/%s.tga", tr.world->baseName );

	source = ri.Hunk_AllocateTempMemory( glConfig.vidWidth * glConfig.vidHeight * 3 );

	buffer = ri.Hunk_AllocateTempMemory( 128 * 128*3 + 18);
	Com_Memset (buffer, 0, 18);
	buffer[2] = 2;		// uncompressed type
	buffer[12] = 128;
	buffer[14] = 128;
	buffer[16] = 24;	// pixel size

	qglGetIntegerv( GL_READ_BUFFER, &readBuffer );
	qglReadBuffer( GL_FRONT );
	qglReadPixels( 0, 0, glConfig.vidWidth, glConfig.vidHeight, GL_RGB, GL_UNSIGNED_BYTE, source ); 
	qglReadBuffer( readBuffer );

	// resample from source
	xScale = glConfig.vidWidth / 512.0f;
	yScale = glConfig.vidHeight / 384.0f;
	for ( y = 0 ; y < 128 ; y++ ) {
		for ( x = 0 ; x < 128 ; x++ ) {
			r = g = b = 0;
			for ( yy = 0 ; yy < 3 ; yy++ ) {
				for ( xx = 0 ; xx < 4 ; xx++ ) {
					src = source + 3 * ( glConfig.vidWidth * (int)( (y*3+yy)*yScale ) + (int)( (x*4+xx)*xScale ) );
					r += src[0];
					g += src[1];
					b += src[2];
				}
			}
			dst = buffer + 18 + 3 * ( y * 128 + x );
			dst[0] = b / 12;
			dst[1] = g / 12;
			dst[2] = r / 12;
		}
	}

	// gamma correct
	if ( ( tr.overbrightBits > 0 ) && glConfig.deviceSupportsGamma ) {
		R_GammaCorrect( buffer + 18, 128 * 128 * 3 );
	}

	ri.FS_WriteFile( checkname, buffer, 128 * 128*3 + 18 );

	ri.Hunk_FreeTempMemory( buffer );
	ri.Hunk_FreeTempMemory( source );

	ri.Printf( PRINT_ALL, "Wrote %s\n", checkname );
}

/* 
================== 
R_ScreenShot_f

screenshot
screenshot [silent]
screenshot [levelshot]
screenshot [filename]

Doesn't print the pacifier message if there is a second arg
================== 
*/  
void R_ScreenShot_f (void) {
	char	checkname[MAX_OSPATH];
	static	int	lastNumber = -1;
	qboolean	silent;

	if ( !strcmp( ri.Cmd_Argv(1), "levelshot" ) ) {
		R_LevelShot();
		return;
	}

	if ( !strcmp( ri.Cmd_Argv(1), "silent" ) ) {
		silent = qtrue;
	} else {
		silent = qfalse;
	}

	if ( ri.Cmd_Argc() == 2 && !silent ) {
		// explicit filename
		Com_sprintf( checkname, MAX_OSPATH, "screenshots/%s.tga", ri.Cmd_Argv( 1 ) );
	} else {
		// scan for a free filename

		// if we have saved a previous screenshot, don't scan
		// again, because recording demo avis can involve
		// thousands of shots
		if ( lastNumber == -1 ) {
			lastNumber = 0;
		}
		// scan for a free number
		for ( ; lastNumber <= 9999 ; lastNumber++ ) {
			R_ScreenshotFilename( lastNumber, checkname );

      if (!ri.FS_FileExists( checkname ))
      {
        break; // file doesn't exist
      }
		}

		if ( lastNumber >= 9999 ) {
			ri.Printf (PRINT_ALL, "ScreenShot: Couldn't create a file\n"); 
			return;
 		}

		lastNumber++;
	}

	R_TakeScreenshot( 0, 0, glConfig.vidWidth, glConfig.vidHeight, checkname, qfalse );

	if ( !silent ) {
		ri.Printf (PRINT_ALL, "Wrote %s\n", checkname);
	}
} 

void R_ScreenShotJPEG_f (void) {
	char		checkname[MAX_OSPATH];
	static	int	lastNumber = -1;
	qboolean	silent;

	if ( !strcmp( ri.Cmd_Argv(1), "levelshot" ) ) {
		R_LevelShot();
		return;
	}

	if ( !strcmp( ri.Cmd_Argv(1), "silent" ) ) {
		silent = qtrue;
	} else {
		silent = qfalse;
	}

	if ( ri.Cmd_Argc() == 2 && !silent ) {
		// explicit filename
		Com_sprintf( checkname, MAX_OSPATH, "screenshots/%s.jpg", ri.Cmd_Argv( 1 ) );
	} else {
		// scan for a free filename

		// if we have saved a previous screenshot, don't scan
		// again, because recording demo avis can involve
		// thousands of shots
		if ( lastNumber == -1 ) {
			lastNumber = 0;
		}
		// scan for a free number
		for ( ; lastNumber <= 9999 ; lastNumber++ ) {
			R_ScreenshotFilenameJPEG( lastNumber, checkname );

      if (!ri.FS_FileExists( checkname ))
      {
        break; // file doesn't exist
      }
		}

		if ( lastNumber == 10000 ) {
			ri.Printf (PRINT_ALL, "ScreenShot: Couldn't create a file\n"); 
			return;
 		}

		lastNumber++;
	}

	R_TakeScreenshot( 0, 0, glConfig.vidWidth, glConfig.vidHeight, checkname, qtrue );

	if ( !silent ) {
		ri.Printf (PRINT_ALL, "Wrote %s\n", checkname);
	}
} 

//============================================================================

/*
** GL_SetDefaultState
*/
void GL_SetDefaultState( void )
{
	qglClearDepth( 1.0f );

	qglCullFace(GL_FRONT);

	qglColor4f (1,1,1,1);

	// initialize downstream texture unit if we're running
	// in a multitexture environment
	if ( qglActiveTextureARB ) {
		GL_SelectTexture( 1 );
		GL_TextureMode( r_textureMode->string );
		GL_TexEnv( GL_MODULATE );
		qglDisable( GL_TEXTURE_2D );
		GL_SelectTexture( 0 );
	}

	qglEnable(GL_TEXTURE_2D);
	GL_TextureMode( r_textureMode->string );
	GL_TexEnv( GL_MODULATE );

	qglShadeModel( GL_SMOOTH );
	qglDepthFunc( GL_LEQUAL );

	// the vertex array is always enabled, but the color and texture
	// arrays are enabled and disabled around the compiled vertex array call
	qglEnableClientState (GL_VERTEX_ARRAY);

	//
	// make sure our GL state vector is set correctly
	//
	glState.glStateBits = GLS_DEPTHTEST_DISABLE | GLS_DEPTHMASK_TRUE;

	qglPolygonMode (GL_FRONT_AND_BACK, GL_FILL);
	qglDepthMask( GL_TRUE );
	qglDisable( GL_DEPTH_TEST );
	qglEnable( GL_SCISSOR_TEST );
	qglDisable( GL_CULL_FACE );
	qglDisable( GL_BLEND );
}


/*
================
GfxInfo_f
================
*/
void GfxInfo_f( void ) 
{
	cvar_t *sys_cpustring = ri.Cvar_Get( "sys_cpustring", "", 0 );
	const char *enablestrings[] =
	{
		"disabled",
		"enabled"
	};
	const char *fsstrings[] =
	{
		"windowed",
		"fullscreen"
	};

	ri.Printf( PRINT_ALL, "\nGL_VENDOR: %s\n", glConfig.vendor_string );
	ri.Printf( PRINT_ALL, "GL_RENDERER: %s\n", glConfig.renderer_string );
	ri.Printf( PRINT_ALL, "GL_VERSION: %s\n", glConfig.version_string );
	ri.Printf( PRINT_ALL, "GL_EXTENSIONS: %s\n", glConfig.extensions_string );
	ri.Printf( PRINT_ALL, "GL_MAX_TEXTURE_SIZE: %d\n", glConfig.maxTextureSize );
	ri.Printf( PRINT_ALL, "GL_MAX_ACTIVE_TEXTURES_ARB: %d\n", glConfig.maxActiveTextures );
	ri.Printf( PRINT_ALL, "\nPIXELFORMAT: color(%d-bits) Z(%d-bit) stencil(%d-bits)\n", glConfig.colorBits, glConfig.depthBits, glConfig.stencilBits );
	ri.Printf( PRINT_ALL, "MODE: %d, %d x %d %s hz:", R_GetMode(), glConfig.vidWidth, glConfig.vidHeight, fsstrings[r_fullscreen->integer == 1] );
	if ( glConfig.displayFrequency )
	{
		ri.Printf( PRINT_ALL, "%d\n", glConfig.displayFrequency );
	}
	else
	{
		ri.Printf( PRINT_ALL, "N/A\n" );
	}
	if ( glConfig.deviceSupportsGamma )
	{
		ri.Printf( PRINT_ALL, "GAMMA: hardware w/ %d overbright bits\n", tr.overbrightBits );
	}
	else
	{
		ri.Printf( PRINT_ALL, "GAMMA: software w/ %d overbright bits\n", tr.overbrightBits );
	}
	ri.Printf( PRINT_ALL, "CPU: %s\n", sys_cpustring->string );

	// rendering primitives
	{
		int		primitives;

		// default is to use triangles if compiled vertex arrays are present
		ri.Printf( PRINT_ALL, "rendering primitives: " );
		primitives = r_primitives->integer;
		if ( primitives == 0 ) {
			if ( qglLockArraysEXT ) {
				primitives = 2;
			} else {
				primitives = 1;
			}
		}
		if ( primitives == -1 ) {
			ri.Printf( PRINT_ALL, "none\n" );
		} else if ( primitives == 2 ) {
			ri.Printf( PRINT_ALL, "single glDrawElements\n" );
		} else if ( primitives == 1 ) {
			ri.Printf( PRINT_ALL, "multiple glArrayElement\n" );
		} else if ( primitives == 3 ) {
			ri.Printf( PRINT_ALL, "multiple glColor4ubv + glTexCoord2fv + glVertex3fv\n" );
		}
	}

	ri.Printf( PRINT_ALL, "texturemode: %s\n", r_textureMode->string );
	ri.Printf( PRINT_ALL, "picmip: %d\n", r_picmip->integer );
	ri.Printf( PRINT_ALL, "texture bits: %d\n", r_texturebits->integer );
	ri.Printf( PRINT_ALL, "multitexture: %s\n", enablestrings[qglActiveTextureARB != 0] );
	ri.Printf( PRINT_ALL, "compiled vertex arrays: %s\n", enablestrings[qglLockArraysEXT != 0 ] );
	ri.Printf( PRINT_ALL, "texenv add: %s\n", enablestrings[glConfig.textureEnvAddAvailable != 0] );
	ri.Printf( PRINT_ALL, "compressed textures: %s\n", enablestrings[glConfig.textureCompression!=TC_NONE] );
	if ( r_vertexLight->integer || glConfig.hardwareType == GLHW_PERMEDIA2 )
	{
		ri.Printf( PRINT_ALL, "HACK: using vertex lightmap approximation\n" );
	}
	if ( glConfig.hardwareType == GLHW_RAGEPRO )
	{
		ri.Printf( PRINT_ALL, "HACK: ragePro approximations\n" );
	}
	if ( glConfig.hardwareType == GLHW_RIVA128 )
	{
		ri.Printf( PRINT_ALL, "HACK: riva128 approximations\n" );
	}
	if ( glConfig.smpActive ) {
		ri.Printf( PRINT_ALL, "Using dual processor acceleration\n" );
	}
	if ( r_finish->integer ) {
		ri.Printf( PRINT_ALL, "Forcing glFinish\n" );
	}
}

/*
=============
R_ClampPostProcessCvars

Clamp post-process toggles to the Quake Live ranges observed in HLIL.
=============
*/
static void R_ClampPostProcessCvars( void ) {
	if ( r_enablePostProcess ) {
		AssertCvarRange( r_enablePostProcess, 0, 1, qtrue );
	}

	if ( r_enableBloom ) {
		AssertCvarRange( r_enableBloom, 0, 2, qtrue );
	}

	if ( r_enableColorCorrect ) {
		AssertCvarRange( r_enableColorCorrect, 0, 1, qtrue );
	}
}

/*
=============
R_ClearLivePostProcessModifiedFlags

Retail Quake Live consumes the live color-correct and bloom combine controls
without forcing a full post-process restart.
=============
*/
static void R_ClearLivePostProcessModifiedFlags( void ) {
	if ( r_contrast && r_contrast->modified ) {
		r_contrast->modified = qfalse;
	}

	if ( r_bloomBrightThreshold && r_bloomBrightThreshold->modified ) {
		r_bloomBrightThreshold->modified = qfalse;
	}

	if ( r_bloomSaturation && r_bloomSaturation->modified ) {
		r_bloomSaturation->modified = qfalse;
	}

	if ( r_bloomSceneSaturation && r_bloomSceneSaturation->modified ) {
		r_bloomSceneSaturation->modified = qfalse;
	}

	if ( r_bloomIntensity && r_bloomIntensity->modified ) {
		r_bloomIntensity->modified = qfalse;
	}

	if ( r_bloomSceneIntensity && r_bloomSceneIntensity->modified ) {
		r_bloomSceneIntensity->modified = qfalse;
	}
}

/*
=============
R_UpdatePostProcessCvars

Synchronize post-process state mirrors with the enable toggles.
=============
*/
void R_UpdatePostProcessCvars( void ) {
	qboolean colorCorrectEnabled;
	qboolean triggerReset;

	R_ClampPostProcessCvars();
	R_ClampRendererCvars();

	colorCorrectEnabled = (qboolean)(r_enablePostProcess && r_enablePostProcess->integer &&
		r_enableColorCorrect && r_enableColorCorrect->integer);

	if ( colorCorrectEnabled && !tr.colorCorrectReady ) {
		R_InitColorCorrection();
	}

	triggerReset = (qboolean)(r_enablePostProcess && r_enablePostProcess->modified);
	triggerReset = (qboolean)(triggerReset || (r_enableBloom && r_enableBloom->modified));
	triggerReset = (qboolean)(triggerReset || (r_enableColorCorrect && r_enableColorCorrect->modified));

	if ( triggerReset ) {
		tr.postProcessNeedsReset = qtrue;
	}

	if ( r_enablePostProcess ) {
		r_enablePostProcess->modified = qfalse;
	}

	if ( r_enableBloom ) {
		r_enableBloom->modified = qfalse;
	}

	if ( r_enableColorCorrect ) {
		r_enableColorCorrect->modified = qfalse;
	}

	R_ClearLivePostProcessModifiedFlags();
}

/*
=============
R_PostProcessRestart
=============
*/
static void R_PostProcessRestart( void ) {
	R_UpdatePostProcessCvars();
	tr.postProcessNeedsReset = qtrue;
}


/*
===============
R_Register
===============
*/
void R_Register( void )
{
	//
	// latched and archived variables
	//
	r_glDriver = ri.Cvar_Get( "r_glDriver", OPENGL_DRIVER_NAME, CVAR_ARCHIVE | CVAR_LATCH );
	r_allowExtensions = ri.Cvar_Get( "r_allowExtensions", "1", CVAR_ARCHIVE | CVAR_LATCH );
	r_ext_compressed_textures = ri.Cvar_Get( "r_ext_compressed_textures", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_ext_gamma_control = ri.Cvar_Get( "r_ext_gamma_control", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_ext_multitexture = ri.Cvar_Get( "r_ext_multitexture", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_ext_compiled_vertex_array = ri.Cvar_Get( "r_ext_compiled_vertex_array", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
#ifdef __linux__ // broken on linux
	r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
#else
	r_ext_texture_env_add = ri.Cvar_Get( "r_ext_texture_env_add", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
#endif

	// HLIL: post-processing and color-correct are 0/1 gates; bloom keeps the retail 0/1/2 mode selection.
	r_enablePostProcess = ri.Cvar_Get( "r_enablePostProcess", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_enableBloom = ri.Cvar_Get( "r_enableBloom", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_enableColorCorrect = ri.Cvar_Get( "r_enableColorCorrect", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_postProcessActive = ri.Cvar_Get( "r_postProcessActive", "0", CVAR_TEMP | CVAR_ROM );
	r_bloomActive = ri.Cvar_Get( "r_bloomActive", "0", CVAR_TEMP | CVAR_ROM | CVAR_CLOUD );
	r_colorCorrectActive = ri.Cvar_Get( "r_colorCorrectActive", "0", CVAR_TEMP | CVAR_ROM );
	// HLIL: bloom tuning cvars are registered with the retail defaults even though the shader path only consumes the bright/combine subset.
	r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );
	r_bloomIntensity = ri.Cvar_GetBounded( "r_bloomIntensity", "0.5", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_bloomBrightThreshold = ri.Cvar_GetBounded( "r_bloomBrightThreshold", "0.25", "0.0", "1.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_bloomBlurScale = ri.Cvar_GetBounded( "r_bloomBlurScale", "0.0", "1.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_bloomBlurRadius = ri.Cvar_GetBounded( "r_bloomBlurRadius", "5", "1", "12", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_bloomBlurFalloff = ri.Cvar_GetBounded( "r_bloomBlurFalloff", "0.0", "0.75", "1.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_bloomSaturation = ri.Cvar_GetBounded( "r_bloomSaturation", "0.8", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_bloomSceneIntensity = ri.Cvar_GetBounded( "r_bloomSceneIntensity", "1.0", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_bloomSceneSaturation = ri.Cvar_GetBounded( "r_bloomSceneSaturation", "1.0", "0.0", "10.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );

	r_picmip = ri.Cvar_Get ("r_picmip", "0", CVAR_ARCHIVE | CVAR_LATCH );
	r_roundImagesDown = ri.Cvar_Get ("r_roundImagesDown", "1", CVAR_ARCHIVE | CVAR_LATCH );
	r_colorMipLevels = ri.Cvar_Get ("r_colorMipLevels", "0", CVAR_LATCH );
	r_detailTextures = ri.Cvar_Get( "r_detailtextures", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_texturebits = ri.Cvar_Get( "r_texturebits", "32", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_colorbits = ri.Cvar_Get( "r_colorbits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_stereo = ri.Cvar_Get( "r_stereo", "0", CVAR_ARCHIVE | CVAR_LATCH );
#ifdef __linux__
	r_stencilbits = ri.Cvar_Get( "r_stencilbits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
#else
	r_stencilbits = ri.Cvar_Get( "r_stencilbits", "8", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
#endif
	r_depthbits = ri.Cvar_Get( "r_depthbits", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_overBrightBits = ri.Cvar_Get ("r_overBrightBits", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_ignorehwgamma = ri.Cvar_Get( "r_ignoreHWGamma", "0", CVAR_ARCHIVE | CVAR_LATCH );
	r_mode = ri.Cvar_Get( "r_mode", "3", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_fullscreen = ri.Cvar_Get( "r_fullscreen", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_windowedMode = ri.Cvar_Get( "r_windowedMode", "12", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );
	r_windowedWidth = ri.Cvar_Get( "r_windowedWidth", "1600", CVAR_ARCHIVE | CVAR_LATCH );
	r_windowedHeight = ri.Cvar_Get( "r_windowedHeight", "1024", CVAR_ARCHIVE | CVAR_LATCH );
	r_customwidth = ri.Cvar_Get( "r_customwidth", "1600", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_customheight = ri.Cvar_Get( "r_customheight", "1024", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_customaspect = ri.Cvar_Get( "r_customaspect", "1", CVAR_ARCHIVE | CVAR_LATCH );
	r_aspectRatio = ri.Cvar_Get( "r_aspectRatio", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	R_ValidateModeCvars();
	r_simpleMipMaps = ri.Cvar_Get( "r_simpleMipMaps", "1", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_vertexLight = ri.Cvar_Get( "r_vertexLight", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );
	r_uiFullScreen = ri.Cvar_Get( "r_uiFullScreen", "0", 0);
	r_subdivisions = ri.Cvar_Get ("r_subdivisions", "4", CVAR_ROM);
	r_smp = ri.Cvar_Get( "r_smp", "0", CVAR_ROM );
	r_ignoreFastPath = ri.Cvar_Get( "r_ignoreFastPath", "1", CVAR_ARCHIVE | CVAR_LATCH );

	//
	// temporary latched variables that can only change over a restart
	//
	r_displayRefresh = ri.Cvar_Get( "r_displayRefresh", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_fullbright = ri.Cvar_Get ("r_fullbright", "0", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_CLOUD );
	r_mapOverBrightBits = ri.Cvar_Get ("r_mapOverBrightBits", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_CLOUD );
	r_intensity = ri.Cvar_Get ("r_intensity", "1", CVAR_ARCHIVE | CVAR_LATCH );
	r_singleShader = ri.Cvar_Get ("r_singleShader", "0", CVAR_CHEAT | CVAR_LATCH );

	//
	// archived variables that can change at any time
	r_noFastRestart = ri.Cvar_Get( "r_noFastRestart", "0", CVAR_ARCHIVE );
	//
	r_lodCurveError = ri.Cvar_Get( "r_lodCurveError", "250", CVAR_CHEAT );
	r_lodbias = ri.Cvar_Get( "r_lodBias", "-2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_flares = ri.Cvar_Get ("r_flares", "0", CVAR_ARCHIVE );
	r_znear = ri.Cvar_Get( "r_znear", "1", CVAR_CHEAT );
	r_ignoreGLErrors = ri.Cvar_Get( "r_ignoreGLErrors", "1", CVAR_ARCHIVE );
	r_fastsky = ri.Cvar_Get( "r_fastsky", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	r_drawSkyFloor = ri.Cvar_Get( "r_drawSkyFloor", "1", CVAR_ARCHIVE | CVAR_CLOUD );
	r_inGameVideo = ri.Cvar_Get( "r_inGameVideo", "1", CVAR_ARCHIVE );
	r_drawSun = ri.Cvar_Get( "r_drawSun", "0", CVAR_ARCHIVE );
	r_dynamiclight = ri.Cvar_Get( "r_dynamiclight", "1", CVAR_ARCHIVE | CVAR_CLOUD );
	r_teleporterFlash = ri.Cvar_Get( "r_teleporterFlash", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	r_dlightBacks = ri.Cvar_Get( "r_dlightBacks", "1", CVAR_ARCHIVE );
	r_finish = ri.Cvar_Get ("r_finish", "0", CVAR_ARCHIVE);
	r_textureMode = ri.Cvar_Get( "r_textureMode", "GL_LINEAR_MIPMAP_LINEAR", CVAR_ARCHIVE | CVAR_CLOUD );
	r_swapInterval = ri.Cvar_Get( "r_swapInterval", "0", CVAR_ARCHIVE | CVAR_CLOUD );
#ifdef __MACOS__
	r_gamma = ri.Cvar_Get( "r_gamma", "1.2", CVAR_ARCHIVE | CVAR_CLOUD );
#else
	r_gamma = ri.Cvar_Get( "r_gamma", "1", CVAR_ARCHIVE | CVAR_CLOUD );
#endif
	r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE | CVAR_CLOUD );
	r_facePlaneCull = ri.Cvar_Get ("r_facePlaneCull", "1", CVAR_ARCHIVE );

	r_railWidth = ri.Cvar_Get( "r_railWidth", "16", CVAR_ARCHIVE | CVAR_CLOUD );
	r_railCoreWidth = ri.Cvar_Get( "r_railCoreWidth", "6", CVAR_ARCHIVE | CVAR_CLOUD );
	r_railSegmentLength = ri.Cvar_Get( "r_railSegmentLength", "32", CVAR_ARCHIVE | CVAR_CLOUD );

	r_primitives = ri.Cvar_Get( "r_primitives", "0", CVAR_ARCHIVE );

	r_ambientScale = ri.Cvar_Get( "r_ambientScale", "10", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	r_directedScale = ri.Cvar_Get( "r_directedScale", "1", CVAR_CHEAT );

	//
	// temporary variables that can change at any time
	//
	r_showImages = ri.Cvar_Get( "r_showImages", "0", CVAR_TEMP );

	r_debugLight = ri.Cvar_Get( "r_debuglight", "0", CVAR_TEMP );
	r_debugFontAtlas = ri.Cvar_Get( "r_debugFontAtlas", "0", CVAR_TEMP );
	r_debugSort = ri.Cvar_Get( "r_debugSort", "0", CVAR_CHEAT );
	r_printShaders = ri.Cvar_Get( "r_printShaders", "0", 0 );
	r_saveFontData = ri.Cvar_Get( "r_saveFontData", "0", 0 );

	r_nocurves = ri.Cvar_Get ("r_nocurves", "0", CVAR_CHEAT );
	r_drawworld = ri.Cvar_Get ("r_drawworld", "1", CVAR_CHEAT );
	r_lightmap = ri.Cvar_Get ("r_lightmap", "0", 0 );
	r_portalOnly = ri.Cvar_Get ("r_portalOnly", "0", CVAR_CHEAT );

	r_flareSize = ri.Cvar_Get ("r_flareSize", "40", CVAR_CHEAT);
	r_flareFade = ri.Cvar_Get ("r_flareFade", "7", CVAR_CHEAT);

	r_showSmp = ri.Cvar_Get ("r_showSmp", "0", CVAR_CHEAT);
	r_skipBackEnd = ri.Cvar_Get ("r_skipBackEnd", "0", CVAR_CHEAT);
	r_skipLargeBatches = ri.Cvar_Get( "r_skipLargeBatches", "0", CVAR_CHEAT );
	r_skipSmallBatches = ri.Cvar_Get( "r_skipSmallBatches", "0", CVAR_CHEAT );

	r_measureOverdraw = ri.Cvar_Get( "r_measureOverdraw", "0", CVAR_CHEAT );
	r_lodscale = ri.Cvar_Get( "r_lodScale", "10", CVAR_VM_CREATED | CVAR_CLOUD );
	r_norefresh = ri.Cvar_Get ("r_norefresh", "0", CVAR_CHEAT);
	r_drawentities = ri.Cvar_Get ("r_drawentities", "1", CVAR_CHEAT );
	r_ignore = ri.Cvar_Get( "r_ignore", "1", CVAR_CHEAT );
	r_nocull = ri.Cvar_Get ("r_nocull", "0", CVAR_CHEAT);
	r_novis = ri.Cvar_Get ("r_novis", "0", CVAR_CHEAT);
	r_showcluster = ri.Cvar_Get ("r_showcluster", "0", CVAR_CHEAT);
	r_speeds = ri.Cvar_Get ("r_speeds", "0", CVAR_CHEAT);
	r_verbose = ri.Cvar_Get( "r_verbose", "0", CVAR_CHEAT );
	r_logFile = ri.Cvar_Get( "r_logFile", "0", CVAR_CHEAT );
	r_debugSurface = ri.Cvar_Get ("r_debugSurface", "0", CVAR_CHEAT);
	r_nobind = ri.Cvar_Get ("r_nobind", "0", CVAR_CHEAT);
	r_showtris = ri.Cvar_Get ("r_showtris", "0", CVAR_CHEAT);
	r_showsky = ri.Cvar_Get ("r_showsky", "0", CVAR_CHEAT);
	r_shownormals = ri.Cvar_Get ("r_shownormals", "0", CVAR_CHEAT);
	r_clear = ri.Cvar_Get ("r_clear", "0", CVAR_CHEAT);
	r_offsetFactor = ri.Cvar_Get( "r_offsetfactor", "-1", CVAR_CHEAT );
	r_offsetUnits = ri.Cvar_Get( "r_offsetunits", "-2", CVAR_CHEAT );
	r_drawBuffer = ri.Cvar_Get( "r_drawBuffer", "GL_BACK", CVAR_CHEAT );
	r_lockpvs = ri.Cvar_Get ("r_lockpvs", "0", CVAR_CHEAT);
	r_noportals = ri.Cvar_Get ("r_noportals", "0", CVAR_CHEAT);
	r_shadows = ri.Cvar_Get( "cg_shadows", "1", 0 );

	r_maxpolys = ri.Cvar_Get( "r_maxpolys", va("%d", MAX_POLYS), 0);
	r_maxpolyverts = ri.Cvar_Get( "r_maxpolyverts", va("%d", MAX_POLYVERTS), 0);

	R_UpdatePostProcessCvars();

	// make sure all the commands added here are also
	// removed in R_Shutdown
	ri.Cmd_AddCommand( "imagelist", R_ImageList_f );
	ri.Cmd_AddCommand( "shaderlist", R_ShaderList_f );
	ri.Cmd_AddCommand( "skinlist", R_SkinList_f );
	ri.Cmd_AddCommand( "modellist", R_Modellist_f );
	ri.Cmd_AddCommand( "advertlist", R_AdvertisementList_f );
	ri.Cmd_AddCommand( "modelist", R_ModeList_f );
	ri.Cmd_AddCommand( "screenshot", R_ScreenShot_f );
	ri.Cmd_AddCommand( "screenshotJPEG", R_ScreenShotJPEG_f );
	ri.Cmd_AddCommand( "gfxinfo", GfxInfo_f );
}

/*
===============
R_Init
===============
*/
void R_Init( void ) {	
	int	err;
	int i;
	byte *ptr;

	ri.Printf( PRINT_ALL, "----- R_Init -----\n" );

	// clear all our internal state
	Com_Memset( &tr, 0, sizeof( tr ) );
	Com_Memset( &backEnd, 0, sizeof( backEnd ) );
	Com_Memset( &tess, 0, sizeof( tess ) );

//	Swap_Init();

	if ( (int)tess.xyz & 15 ) {
		Com_Printf( "WARNING: tess.xyz not 16 byte aligned\n" );
	}
	Com_Memset( tess.constantColor255, 255, sizeof( tess.constantColor255 ) );

	//
	// init function tables
	//
	for ( i = 0; i < FUNCTABLE_SIZE; i++ )
	{
		tr.sinTable[i]		= sin( DEG2RAD( i * 360.0f / ( ( float ) ( FUNCTABLE_SIZE - 1 ) ) ) );
		tr.squareTable[i]	= ( i < FUNCTABLE_SIZE/2 ) ? 1.0f : -1.0f;
		tr.sawToothTable[i] = (float)i / FUNCTABLE_SIZE;
		tr.inverseSawToothTable[i] = 1.0f - tr.sawToothTable[i];

		if ( i < FUNCTABLE_SIZE / 2 )
		{
			if ( i < FUNCTABLE_SIZE / 4 )
			{
				tr.triangleTable[i] = ( float ) i / ( FUNCTABLE_SIZE / 4 );
			}
			else
			{
				tr.triangleTable[i] = 1.0f - tr.triangleTable[i-FUNCTABLE_SIZE / 4];
			}
		}
		else
		{
			tr.triangleTable[i] = -tr.triangleTable[i-FUNCTABLE_SIZE/2];
		}
	}

	R_InitFogTable();

	R_NoiseInit();

	R_Register();

	max_polys = r_maxpolys->integer;
	if (max_polys < MAX_POLYS)
		max_polys = MAX_POLYS;

	max_polyverts = r_maxpolyverts->integer;
	if (max_polyverts < MAX_POLYVERTS)
		max_polyverts = MAX_POLYVERTS;

	ptr = ri.Hunk_Alloc( sizeof( *backEndData[0] ) + sizeof(srfPoly_t) * max_polys + sizeof(polyVert_t) * max_polyverts, h_low);
	backEndData[0] = (backEndData_t *) ptr;
	backEndData[0]->polys = (srfPoly_t *) ((char *) ptr + sizeof( *backEndData[0] ));
	backEndData[0]->polyVerts = (polyVert_t *) ((char *) ptr + sizeof( *backEndData[0] ) + sizeof(srfPoly_t) * max_polys);
	if ( r_smp->integer ) {
		ptr = ri.Hunk_Alloc( sizeof( *backEndData[1] ) + sizeof(srfPoly_t) * max_polys + sizeof(polyVert_t) * max_polyverts, h_low);
		backEndData[1] = (backEndData_t *) ptr;
		backEndData[1]->polys = (srfPoly_t *) ((char *) ptr + sizeof( *backEndData[1] ));
		backEndData[1]->polyVerts = (polyVert_t *) ((char *) ptr + sizeof( *backEndData[1] ) + sizeof(srfPoly_t) * max_polys);
	} else {
		backEndData[1] = NULL;
	}
	R_ToggleSmpFrame();

	ri.Printf( PRINT_ALL, "R_Init: InitOpenGL\n" );
	InitOpenGL();

	ri.Printf( PRINT_ALL, "R_Init: InitRenderTargets\n" );
	RB_InitRenderTargets();

	ri.Printf( PRINT_ALL, "R_Init: InitColorCorrection\n" );
	R_InitColorCorrection();

	ri.Printf( PRINT_ALL, "R_Init: InitImages\n" );
	R_InitImages();

	ri.Printf( PRINT_ALL, "R_Init: InitShaders\n" );
	R_InitShaders();

	ri.Printf( PRINT_ALL, "R_Init: InitSkins\n" );
	R_InitSkins();

	ri.Printf( PRINT_ALL, "R_Init: ModelInit\n" );
	R_ModelInit();

	ri.Printf( PRINT_ALL, "R_Init: InitFreeType\n" );
	R_InitFreeType();

	ri.Printf( PRINT_ALL, "R_Init: InitFontStash\n" );
	R_InitFontStash();


	err = qglGetError();
	if ( err != GL_NO_ERROR )
		ri.Printf (PRINT_ALL, "glGetError() = 0x%x\n", err);

	ri.Printf( PRINT_ALL, "----- finished R_Init -----\n" );
}

/*
===============
RE_Shutdown
===============
*/
void RE_Shutdown( qboolean destroyWindow ) {	

	ri.Printf( PRINT_ALL, "RE_Shutdown( %i )\n", destroyWindow );

	ri.Cmd_RemoveCommand ("modellist");
	ri.Cmd_RemoveCommand( "advertlist" );
	ri.Cmd_RemoveCommand ("screenshotJPEG");
	ri.Cmd_RemoveCommand ("screenshot");
	ri.Cmd_RemoveCommand ("imagelist");
	ri.Cmd_RemoveCommand ("shaderlist");
	ri.Cmd_RemoveCommand ("skinlist");
	ri.Cmd_RemoveCommand ("gfxinfo");
	ri.Cmd_RemoveCommand( "modelist" );
	ri.Cmd_RemoveCommand( "shaderstate" );

	R_DoneFontStash();

	if ( tr.registered ) {
		R_SyncRenderThread();
		R_ShutdownCommandBuffers();
		R_ShutdownColorCorrection();
		RB_ShutdownRenderTargets();
		R_DeleteTextures();
	}

	R_DoneFreeType();

	// shut down platform specific OpenGL stuff
	if ( destroyWindow ) {
		GLimp_Shutdown();
	}

	tr.registered = qfalse;
}


/*
=============
RE_EndRegistration

Touch all images to make sure they are resident
=============
*/
void RE_EndRegistration( void ) {
	R_SyncRenderThread();
	if (!Sys_LowPhysicalMemory()) {
		RB_ShowImages();
	}
}


/*
@@@@@@@@@@@@@@@@@@@@@
GetRefAPI

@@@@@@@@@@@@@@@@@@@@@
*/
refexport_t *GetRefAPI ( int apiVersion, refimport_t *rimp ) {
	static refexport_t	re;

	ri = *rimp;

	Com_Memset( &re, 0, sizeof( re ) );

	if ( apiVersion != REF_API_VERSION ) {
		ri.Printf(PRINT_ALL, "Mismatched REF_API_VERSION: expected %i, got %i\n", 
			REF_API_VERSION, apiVersion );
		return NULL;
	}

	// the RE_ functions are Renderer Entry points

	re.Shutdown = RE_Shutdown;

	re.BeginRegistration = RE_BeginRegistration;
	re.RegisterModel = RE_RegisterModel;
	re.RegisterSkin = RE_RegisterSkin;
	re.RegisterShader = RE_RegisterShader;
	re.RegisterShaderNoMip = RE_RegisterShaderNoMip;
	re.LoadWorld = RE_LoadWorldMap;
	re.SetWorldVisData = RE_SetWorldVisData;
	re.EndRegistration = RE_EndRegistration;

	re.ClearScene = RE_ClearScene;
	re.AddRefEntityToScene = RE_AddRefEntityToScene;
	re.AddPolyToScene = RE_AddPolyToScene;
	re.LightForPoint = R_LightForPoint;
	re.AddLightToScene = RE_AddLightToScene;
	re.AddAdditiveLightToScene = RE_AddAdditiveLightToScene;
	re.RenderScene = RE_RenderScene;
	re.AdvertisementBridge_UpdateLoadingViewParameters = AdvertisementBridge_UpdateLoadingViewParameters;
	re.PostProcessRestart = R_PostProcessRestart;
	re.SetColor = RE_SetColor;
	re.DrawStretchPic = RE_StretchPic;
	re.DrawStretchRaw = RE_StretchRaw;
	re.UploadCinematic = RE_UploadCinematic;
	re.BeginFrame = RE_BeginFrame;
	re.EndFrame = RE_EndFrame;
	re.MarkFragments = R_MarkFragments;
	re.LerpTag = R_LerpTag;
	re.ModelBounds = R_ModelBounds;

	re.RemapShader = R_RemapShader;
	re.GetEntityToken = R_GetEntityToken;
	re.inPVS = R_inPVS;

	return &re;
}
