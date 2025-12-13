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
#include "tr_local.h"

backEndData_t	*backEndData[SMP_FRAMES];
backEndState_t	backEnd;


static float	s_flipMatrix[16] = {
		// convert from our coordinate system (looking down X)
		// to OpenGL's coordinate system (looking down -Z)
		0, 0, -1, 0,
		-1, 0, 0, 0,
		0, 1, 0, 0,
		0, 0, 0, 1
};

#ifndef GL_FRAMEBUFFER_EXT
#define GL_FRAMEBUFFER_EXT 0x8D40
#define GL_COLOR_ATTACHMENT0_EXT 0x8CE0
#define GL_DEPTH_ATTACHMENT_EXT 0x8D00
#define GL_RENDERBUFFER_EXT 0x8D41
#define GL_FRAMEBUFFER_COMPLETE_EXT 0x8CD5
#endif

#ifndef GL_DEPTH_COMPONENT24
#define GL_DEPTH_COMPONENT24 0x81A6
#endif

#ifndef GL_RGBA8
#define GL_RGBA8 0x8058
#endif

#ifndef GL_CLAMP_TO_EDGE
#define GL_CLAMP_TO_EDGE 0x812F
#endif

#ifndef PFNGLGENFRAMEBUFFERSEXTPROC
typedef void (APIENTRY * PFNGLGENFRAMEBUFFERSEXTPROC) (GLsizei, GLuint *);
typedef void (APIENTRY * PFNGLDELETEFRAMEBUFFERSEXTPROC) (GLsizei, const GLuint *);
typedef void (APIENTRY * PFNGLBINDFRAMEBUFFEREXTPROC) (GLenum, GLuint);
typedef void (APIENTRY * PFNGLFRAMEBUFFERTEXTURE2DEXTPROC) (GLenum, GLenum, GLenum, GLuint, GLint);
typedef GLenum (APIENTRY * PFNGLCHECKFRAMEBUFFERSTATUSEXTPROC) (GLenum);
typedef void (APIENTRY * PFNGLGENRENDERBUFFERSEXTPROC) (GLsizei, GLuint *);
typedef void (APIENTRY * PFNGLBINDRENDERBUFFEREXTPROC) (GLenum, GLuint);
typedef void (APIENTRY * PFNGLRENDERBUFFERSTORAGEEXTPROC) (GLenum, GLenum, GLsizei, GLsizei);
typedef void (APIENTRY * PFNGLFRAMEBUFFERRENDERBUFFEREXTPROC) (GLenum, GLenum, GLenum, GLuint);
typedef void (APIENTRY * PFNGLDELETERENDERBUFFERSEXTPROC) (GLsizei, const GLuint *);
#endif

typedef struct {
	PFNGLGENFRAMEBUFFERSEXTPROC qglGenFramebuffersEXTFunc;
	PFNGLDELETEFRAMEBUFFERSEXTPROC qglDeleteFramebuffersEXTFunc;
	PFNGLBINDFRAMEBUFFEREXTPROC qglBindFramebufferEXTFunc;
	PFNGLFRAMEBUFFERTEXTURE2DEXTPROC qglFramebufferTexture2DEXTFunc;
	PFNGLCHECKFRAMEBUFFERSTATUSEXTPROC qglCheckFramebufferStatusEXTFunc;
	PFNGLGENRENDERBUFFERSEXTPROC qglGenRenderbuffersEXTFunc;
	PFNGLBINDRENDERBUFFEREXTPROC qglBindRenderbufferEXTFunc;
	PFNGLRENDERBUFFERSTORAGEEXTPROC qglRenderbufferStorageEXTFunc;
	PFNGLFRAMEBUFFERRENDERBUFFEREXTPROC qglFramebufferRenderbufferEXTFunc;
	PFNGLDELETERENDERBUFFERSEXTPROC qglDeleteRenderbuffersEXTFunc;
} glFramebufferProcs_t;

typedef struct {
	GLuint framebuffer;
	GLuint color;
	GLuint depth;
	int width;
	int height;
	qboolean loaded;
	qboolean initialized;
	qboolean bound;
} renderTarget_t;

static glFramebufferProcs_t s_fboProcs;
static renderTarget_t s_sceneRenderTarget;
static int s_lastTeleporterFlashLogTime = -1;

/*
=============
RB_PostProcessEnabled

Return qtrue when post-processing is allowed by the cvar toggle and backend state.
=============
*/
static qboolean RB_PostProcessEnabled( void ) {
	if ( !r_enablePostProcess || !r_enablePostProcess->integer ) {
		return qfalse;
	}

	return backEnd.postProcessActive;
}

static void *RB_GetFramebufferProc( const char *procName );
static qboolean RB_LoadFramebufferProcs( void );
static qboolean RB_CreateRenderTarget( void );
static void RB_DestroyRenderTarget( void );
static void RB_BindOffscreenRenderTarget( void );
static void RB_ReleaseOffscreenRenderTarget( void );
static byte RB_ClampColorComponent( float value );
static void RB_ApplyColorCorrection( void );


/*
=============
RB_InitRenderTargets

Initialize framebuffer storage for post-process rendering.
=============
*/
void RB_InitRenderTargets( void ) {
	Com_Memset( &s_sceneRenderTarget, 0, sizeof( s_sceneRenderTarget ) );

	if ( !r_enablePostProcess || !r_enablePostProcess->integer ) {
		return;
	}

	if ( !RB_CreateRenderTarget() ) {
		ri.Printf( PRINT_WARNING, "WARNING: failed to create offscreen render target\n" );
	}
}


/*
=============
RB_ShutdownRenderTargets

Release framebuffer storage used for post-process rendering.
=============
*/
void RB_ShutdownRenderTargets( void ) {
	RB_DestroyRenderTarget();
}


/*
=============
RB_GetFramebufferProc

Resolve framebuffer extension entry points using the platform API.
=============
*/
static void *RB_GetFramebufferProc( const char *procName ) {
#if defined( _WIN32 )
	if ( !qwglGetProcAddress ) {
		return NULL;
	}

	return (void *)qwglGetProcAddress( procName );
#elif defined( __linux__ ) || defined( __FreeBSD__ )
	return (void *)glXGetProcAddressARB( (const GLubyte *)procName );
#else
	return NULL;
#endif
}


/*
=============
RB_LoadFramebufferProcs

Cache framebuffer extension entry points for later use.
=============
*/
static qboolean RB_LoadFramebufferProcs( void ) {
	Com_Memset( &s_fboProcs, 0, sizeof( s_fboProcs ) );

	s_fboProcs.qglGenFramebuffersEXTFunc = (PFNGLGENFRAMEBUFFERSEXTPROC)RB_GetFramebufferProc( "glGenFramebuffersEXT" );
	s_fboProcs.qglDeleteFramebuffersEXTFunc = (PFNGLDELETEFRAMEBUFFERSEXTPROC)RB_GetFramebufferProc( "glDeleteFramebuffersEXT" );
	s_fboProcs.qglBindFramebufferEXTFunc = (PFNGLBINDFRAMEBUFFEREXTPROC)RB_GetFramebufferProc( "glBindFramebufferEXT" );
	s_fboProcs.qglFramebufferTexture2DEXTFunc = (PFNGLFRAMEBUFFERTEXTURE2DEXTPROC)RB_GetFramebufferProc( "glFramebufferTexture2DEXT" );
	s_fboProcs.qglCheckFramebufferStatusEXTFunc = (PFNGLCHECKFRAMEBUFFERSTATUSEXTPROC)RB_GetFramebufferProc( "glCheckFramebufferStatusEXT" );
	s_fboProcs.qglGenRenderbuffersEXTFunc = (PFNGLGENRENDERBUFFERSEXTPROC)RB_GetFramebufferProc( "glGenRenderbuffersEXT" );
	s_fboProcs.qglBindRenderbufferEXTFunc = (PFNGLBINDRENDERBUFFEREXTPROC)RB_GetFramebufferProc( "glBindRenderbufferEXT" );
	s_fboProcs.qglRenderbufferStorageEXTFunc = (PFNGLRENDERBUFFERSTORAGEEXTPROC)RB_GetFramebufferProc( "glRenderbufferStorageEXT" );
	s_fboProcs.qglFramebufferRenderbufferEXTFunc = (PFNGLFRAMEBUFFERRENDERBUFFEREXTPROC)RB_GetFramebufferProc( "glFramebufferRenderbufferEXT" );
	s_fboProcs.qglDeleteRenderbuffersEXTFunc = (PFNGLDELETERENDERBUFFERSEXTPROC)RB_GetFramebufferProc( "glDeleteRenderbuffersEXT" );

	s_sceneRenderTarget.loaded = (qboolean)(s_fboProcs.qglGenFramebuffersEXTFunc && s_fboProcs.qglDeleteFramebuffersEXTFunc &&
		s_fboProcs.qglBindFramebufferEXTFunc && s_fboProcs.qglFramebufferTexture2DEXTFunc && s_fboProcs.qglCheckFramebufferStatusEXTFunc &&
		s_fboProcs.qglGenRenderbuffersEXTFunc && s_fboProcs.qglBindRenderbufferEXTFunc && s_fboProcs.qglRenderbufferStorageEXTFunc &&
		s_fboProcs.qglFramebufferRenderbufferEXTFunc && s_fboProcs.qglDeleteRenderbuffersEXTFunc);

	return s_sceneRenderTarget.loaded;
}


/*
=============
RB_CreateRenderTarget

Allocate a color texture and depth renderbuffer for offscreen scene rendering.
=============
*/
static qboolean RB_CreateRenderTarget( void ) {
	GLenum status;
	int width;
	int height;

	RB_DestroyRenderTarget();

	if ( !r_enablePostProcess || !r_enablePostProcess->integer ) {
		return qfalse;
	}

	if ( !s_sceneRenderTarget.loaded && !RB_LoadFramebufferProcs() ) {
		return qfalse;
	}

	width = glConfig.vidWidth;
	height = glConfig.vidHeight;

	s_sceneRenderTarget.width = width;
	s_sceneRenderTarget.height = height;

	s_fboProcs.qglGenFramebuffersEXTFunc( 1, &s_sceneRenderTarget.framebuffer );
	s_fboProcs.qglGenRenderbuffersEXTFunc( 1, &s_sceneRenderTarget.depth );

	qglGenTextures( 1, &s_sceneRenderTarget.color );
	qglBindTexture( GL_TEXTURE_2D, s_sceneRenderTarget.color );
	qglTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
	qglTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
	qglTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE );
	qglTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE );
	qglTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL );

	s_fboProcs.qglBindRenderbufferEXTFunc( GL_RENDERBUFFER_EXT, s_sceneRenderTarget.depth );
	s_fboProcs.qglRenderbufferStorageEXTFunc( GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT24, width, height );

	s_fboProcs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, s_sceneRenderTarget.framebuffer );
	s_fboProcs.qglFramebufferTexture2DEXTFunc( GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, s_sceneRenderTarget.color, 0 );
	s_fboProcs.qglFramebufferRenderbufferEXTFunc( GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, s_sceneRenderTarget.depth );

	status = s_fboProcs.qglCheckFramebufferStatusEXTFunc( GL_FRAMEBUFFER_EXT );
	if ( status != GL_FRAMEBUFFER_COMPLETE_EXT ) {
		RB_DestroyRenderTarget();
		return qfalse;
	}

	s_sceneRenderTarget.initialized = qtrue;
	s_sceneRenderTarget.bound = qfalse;

	s_fboProcs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, 0 );
	qglBindTexture( GL_TEXTURE_2D, 0 );

	return qtrue;
}


/*
=============
RB_DestroyRenderTarget

Release framebuffer resources allocated for post-processing.
=============
*/
static void RB_DestroyRenderTarget( void ) {
	if ( s_sceneRenderTarget.bound && s_sceneRenderTarget.loaded ) {
		s_fboProcs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, 0 );
	}

	if ( s_sceneRenderTarget.framebuffer && s_sceneRenderTarget.loaded ) {
		s_fboProcs.qglDeleteFramebuffersEXTFunc( 1, &s_sceneRenderTarget.framebuffer );
	}

	if ( s_sceneRenderTarget.depth && s_sceneRenderTarget.loaded ) {
		s_fboProcs.qglDeleteRenderbuffersEXTFunc( 1, &s_sceneRenderTarget.depth );
	}

	if ( s_sceneRenderTarget.color ) {
		qglDeleteTextures( 1, &s_sceneRenderTarget.color );
	}

	Com_Memset( &s_sceneRenderTarget, 0, sizeof( s_sceneRenderTarget ) );
}


/*
=============
RB_BindOffscreenRenderTarget

Make the offscreen framebuffer active for scene rendering when post-processing is enabled.
=============
*/
static void RB_BindOffscreenRenderTarget( void ) {
	if ( !RB_PostProcessEnabled() || !s_sceneRenderTarget.initialized || !s_sceneRenderTarget.loaded ) {
		RB_ReleaseOffscreenRenderTarget();
		return;
	}

	if ( s_sceneRenderTarget.bound ) {
		return;
	}

	s_fboProcs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, s_sceneRenderTarget.framebuffer );
	s_sceneRenderTarget.bound = qtrue;
}


/*
=============
RB_ReleaseOffscreenRenderTarget

Restore rendering to the default framebuffer.
=============
*/
static void RB_ReleaseOffscreenRenderTarget( void ) {
	if ( !s_sceneRenderTarget.bound || !s_sceneRenderTarget.loaded ) {
		return;
	}

	s_fboProcs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, 0 );
	s_sceneRenderTarget.bound = qfalse;
}

/*
=============
RB_ResetPostProcessState

Rebuild post-process render targets when toggles change and clear the reset flag once handled.
=============
*/
static void RB_ResetPostProcessState( void ) {
	if ( !backEnd.postProcessNeedsReset ) {
		return;
	}

	if ( backEnd.postProcessActive ) {
		RB_DestroyRenderTarget();

		if ( !RB_CreateRenderTarget() ) {
			backEnd.postProcessActive = qfalse;
			backEnd.bloomActive = qfalse;
			backEnd.colorCorrectActive = qfalse;
			return;
		}
	} else {
		RB_DestroyRenderTarget();
	}

	backEnd.postProcessNeedsReset = qfalse;
}


/*
=============
RB_ClampColorComponent

Clamp a floating point color component to the 0-255 range.
=============
*/
static byte RB_ClampColorComponent( float value ) {
	if ( value < 0.0f ) {
		value = 0.0f;
	} else if ( value > 255.0f ) {
		value = 255.0f;
	}

	return (byte)(value + 0.5f);
}


/*
=============
RB_ApplyColorCorrection

Apply a color-correction matrix to the current framebuffer contents.
=============
*/
static void RB_ApplyColorCorrection( void ) {
	int			width;
	int			height;
	image_t		*sceneImage;
	byte			*pixelData;
	int			pixelCount;
	int			pixelIndex;
	const float	*matrix;

	if ( !backEnd.colorCorrectActive || !tr.colorCorrectReady ) {
		return;
	}

	width = glConfig.vidWidth;
	height = glConfig.vidHeight;
	sceneImage = RB_UploadBloomScratch( 1, width, height );

	GL_Bind( sceneImage );

	pixelData = ri.Hunk_AllocateTempMemory( width * height * 4 );

	qglGetTexImage( GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixelData );

	matrix = tr.colorCorrectMatrix;
	pixelCount = width * height;

	for ( pixelIndex = 0; pixelIndex < pixelCount; pixelIndex++ ) {
		byte	*rgba;
		float	r;
		float	g;
		float	b;
		float	correctedR;
		float	correctedG;
		float	correctedB;

		rgba = pixelData + ( pixelIndex * 4 );
		r = rgba[0];
		g = rgba[1];
		b = rgba[2];

		correctedR = ( matrix[0] * r ) + ( matrix[4] * g ) + ( matrix[8] * b ) + ( matrix[12] * 255.0f );
		correctedG = ( matrix[1] * r ) + ( matrix[5] * g ) + ( matrix[9] * b ) + ( matrix[13] * 255.0f );
		correctedB = ( matrix[2] * r ) + ( matrix[6] * g ) + ( matrix[10] * b ) + ( matrix[14] * 255.0f );

		rgba[0] = RB_ClampColorComponent( correctedR );
		rgba[1] = RB_ClampColorComponent( correctedG );
		rgba[2] = RB_ClampColorComponent( correctedB );
	}

	qglTexSubImage2D( GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixelData );

	ri.Hunk_FreeTempMemory( pixelData );

	qglDisable( GL_DEPTH_TEST );
	qglDisable( GL_CULL_FACE );
	qglDisable( GL_SCISSOR_TEST );

	qglViewport( 0, 0, width, height );
	RB_SetGL2D();

	qglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE );
	qglColor4f( 1.0f, 1.0f, 1.0f, 1.0f );

	RB_DrawBloomSpread( 0.0f, 0.0f, width, height );
}
/*
=============
RB_UploadBloomScratch

Make sure a scratch texture matches the current viewport and contains a copy of the scene.
=============
*/
static image_t *RB_UploadBloomScratch( int scratchIndex, int width, int height ) {
	image_t		*image;

	image = tr.scratchImage[scratchIndex];

	GL_Bind( image );

	if ( image->width != width || image->height != height ) {
		image->width = image->uploadWidth = width;
		image->height = image->uploadHeight = height;
		qglTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP );
	}

	qglCopyTexSubImage2D( GL_TEXTURE_2D, 0, 0, 0, 0, 0, width, height );

	return image;
}


/*
=============
RB_ConfigureBloomStage

Set texture environment to approximate Quake Live's bright-pass, saturation, and intensity controls.
=============
*/
static void RB_ConfigureBloomStage( float threshold, float saturation, float intensity ) {
	GLfloat	constColor[4];
	GLfloat	lerp;

	constColor[0] = threshold;
	constColor[1] = threshold;
	constColor[2] = threshold;
	constColor[3] = 1.0f;
	qglTexEnvfv( GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, constColor );

	qglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE );
	qglTexEnvi( GL_TEXTURE_ENV, GL_COMBINE_RGB, GL_SUBTRACT );
	qglTexEnvi( GL_TEXTURE_ENV, GL_SOURCE0_RGB, GL_TEXTURE );
	qglTexEnvi( GL_TEXTURE_ENV, GL_SOURCE1_RGB, GL_CONSTANT );

	lerp = saturation;
	if ( lerp < 0.0f ) {
		lerp = 0.0f;
	}

	if ( lerp > 2.0f ) {
		lerp = 2.0f;
	}

	qglTexEnvi( GL_TEXTURE_ENV, GL_COMBINE_ALPHA, GL_INTERPOLATE );
	qglTexEnvi( GL_TEXTURE_ENV, GL_SOURCE0_ALPHA, GL_TEXTURE );
	qglTexEnvi( GL_TEXTURE_ENV, GL_SOURCE1_ALPHA, GL_CONSTANT );
	qglTexEnvi( GL_TEXTURE_ENV, GL_SOURCE2_ALPHA, GL_CONSTANT );
	constColor[0] = constColor[1] = constColor[2] = constColor[3] = lerp * 0.5f;
	qglTexEnvfv( GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, constColor );

	qglColor4f( intensity, intensity, intensity, 1.0f );
}


/*
=============
RB_DrawBloomSpread

Render a textured quad with offsets to approximate the separable blur used by Quake Live.
=============
*/
static void RB_DrawBloomSpread( float xOffset, float yOffset, int width, int height ) {
	float	s0, t0, s1, t1;

	s0 = 0.0f + xOffset;
	t0 = 0.0f + yOffset;
	s1 = 1.0f + xOffset;
	t1 = 1.0f + yOffset;

	qglBegin( GL_QUADS );
	qglTexCoord2f( s0, t0 );
	qglVertex2f( 0.0f, 0.0f );
	qglTexCoord2f( s1, t0 );
	qglVertex2f( width, 0.0f );
	qglTexCoord2f( s1, t1 );
	qglVertex2f( width, height );
	qglTexCoord2f( s0, t1 );
	qglVertex2f( 0.0f, height );
	qglEnd();
}


/*
=============
RB_DrawBloomPass

Issue one bloom blur pass using configurable radius and scale.
=============
*/
static void RB_DrawBloomPass( int width, int height, int radius, float scale, float saturation, float intensity, float threshold ) {
	int		offset;
	float	xStep;
	float	yStep;

	RB_ConfigureBloomStage( threshold, saturation, intensity );
	qglEnable( GL_BLEND );
	qglBlendFunc( GL_ONE, GL_ONE );

	xStep = (float)radius / (float)width;
	yStep = (float)radius / (float)height;

	xStep *= scale;
	yStep *= scale;

	RB_DrawBloomSpread( 0.0f, 0.0f, width, height );

	for ( offset = 1; offset <= radius; offset++ ) {
		float	spread;

		spread = offset * scale;
		RB_DrawBloomSpread( xStep * spread, 0.0f, width, height );
		RB_DrawBloomSpread( -xStep * spread, 0.0f, width, height );
		RB_DrawBloomSpread( 0.0f, yStep * spread, width, height );
		RB_DrawBloomSpread( 0.0f, -yStep * spread, width, height );
	}
}
/*
=============
RB_SubmitPostProcess

Run any post-process work gated by the current enable flags.
=============
*/
static void RB_SubmitPostProcess( void ) {
	if ( !RB_PostProcessEnabled() ) {
		return;
	}

	RB_ResetPostProcessState();

	if ( backEnd.bloomActive && r_bloomIntensity && r_bloomBrightThreshold && r_bloomPasses ) {
		int		width, height;
		int		passes;
		float	bloomIntensity;
		float	brightThreshold;
		float	blurScale;
		int		blurRadius;
		float	bloomSaturation;
		float	sceneIntensity;
		float	sceneSaturation;
		image_t	*sceneImage;

		width = glConfig.vidWidth;
		height = glConfig.vidHeight;

		brightThreshold = r_bloomBrightThreshold->value;
		bloomIntensity = r_bloomIntensity->value;
		passes = r_bloomPasses->integer;
		blurScale = ( r_bloomBlurScale && r_bloomBlurScale->value > 0.0f ) ? r_bloomBlurScale->value : 1.0f;
		blurRadius = ( r_bloomBlurRadius && r_bloomBlurRadius->integer > 0 ) ? r_bloomBlurRadius->integer : 1;
		bloomSaturation = ( r_bloomSaturation ? r_bloomSaturation->value : 1.0f );
		sceneIntensity = ( r_bloomSceneIntensity ? r_bloomSceneIntensity->value : 1.0f );
		sceneSaturation = ( r_bloomSceneSaturation ? r_bloomSceneSaturation->value : 1.0f );

		if ( passes < 1 ) {
			passes = 1;
		} else if ( passes > 2 ) {
			passes = 2;
		}

		qglDisable( GL_DEPTH_TEST );
		qglDisable( GL_CULL_FACE );
		qglDisable( GL_SCISSOR_TEST );

		qglViewport( 0, 0, width, height );
		RB_SetGL2D();

		sceneImage = RB_UploadBloomScratch( 0, width, height );
		GL_Bind( sceneImage );

		qglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );
		qglColor4f( sceneIntensity, sceneIntensity, sceneIntensity, 1.0f );
		RB_DrawBloomSpread( 0.0f, 0.0f, width, height );

		qglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE );
		qglTexEnvi( GL_TEXTURE_ENV, GL_COMBINE_RGB, GL_MODULATE );
		qglTexEnvi( GL_TEXTURE_ENV, GL_SOURCE0_RGB, GL_TEXTURE );
		qglTexEnvi( GL_TEXTURE_ENV, GL_SOURCE1_RGB, GL_PRIMARY_COLOR );
		qglColor4f( sceneSaturation, sceneSaturation, sceneSaturation, 1.0f );
		RB_DrawBloomSpread( 0.0f, 0.0f, width, height );

		while ( passes-- ) {
			RB_DrawBloomPass( width, height, blurRadius, blurScale, bloomSaturation, bloomIntensity, brightThreshold );
		}

		qglDisable( GL_BLEND );
		qglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE );
	}

	if ( backEnd.colorCorrectActive ) {
		RB_ApplyColorCorrection();
	}
}

/*
** GL_Bind
*/
void GL_Bind( image_t *image ) {
	int texnum;

	if ( !image ) {
		ri.Printf( PRINT_WARNING, "GL_Bind: NULL image\n" );
		texnum = tr.defaultImage->texnum;
	} else {
		texnum = image->texnum;
	}

	if ( r_nobind->integer && tr.dlightImage ) {		// performance evaluation option
		texnum = tr.dlightImage->texnum;
	}

	if ( glState.currenttextures[glState.currenttmu] != texnum ) {
		image->frameUsed = tr.frameCount;
		glState.currenttextures[glState.currenttmu] = texnum;
		qglBindTexture (GL_TEXTURE_2D, texnum);
	}
}

/*
** GL_SelectTexture
*/
void GL_SelectTexture( int unit )
{
	if ( glState.currenttmu == unit )
	{
		return;
	}

	if ( unit == 0 )
	{
		qglActiveTextureARB( GL_TEXTURE0_ARB );
		GLimp_LogComment( "glActiveTextureARB( GL_TEXTURE0_ARB )\n" );
		qglClientActiveTextureARB( GL_TEXTURE0_ARB );
		GLimp_LogComment( "glClientActiveTextureARB( GL_TEXTURE0_ARB )\n" );
	}
	else if ( unit == 1 )
	{
		qglActiveTextureARB( GL_TEXTURE1_ARB );
		GLimp_LogComment( "glActiveTextureARB( GL_TEXTURE1_ARB )\n" );
		qglClientActiveTextureARB( GL_TEXTURE1_ARB );
		GLimp_LogComment( "glClientActiveTextureARB( GL_TEXTURE1_ARB )\n" );
	} else {
		ri.Error( ERR_DROP, "GL_SelectTexture: unit = %i", unit );
	}

	glState.currenttmu = unit;
}


/*
** GL_BindMultitexture
*/
void GL_BindMultitexture( image_t *image0, GLuint env0, image_t *image1, GLuint env1 ) {
	int		texnum0, texnum1;

	texnum0 = image0->texnum;
	texnum1 = image1->texnum;

	if ( r_nobind->integer && tr.dlightImage ) {		// performance evaluation option
		texnum0 = texnum1 = tr.dlightImage->texnum;
	}

	if ( glState.currenttextures[1] != texnum1 ) {
		GL_SelectTexture( 1 );
		image1->frameUsed = tr.frameCount;
		glState.currenttextures[1] = texnum1;
		qglBindTexture( GL_TEXTURE_2D, texnum1 );
	}
	if ( glState.currenttextures[0] != texnum0 ) {
		GL_SelectTexture( 0 );
		image0->frameUsed = tr.frameCount;
		glState.currenttextures[0] = texnum0;
		qglBindTexture( GL_TEXTURE_2D, texnum0 );
	}
}


/*
** GL_Cull
*/
void GL_Cull( int cullType ) {
	if ( glState.faceCulling == cullType ) {
		return;
	}

	glState.faceCulling = cullType;

	if ( cullType == CT_TWO_SIDED ) 
	{
		qglDisable( GL_CULL_FACE );
	} 
	else 
	{
		qglEnable( GL_CULL_FACE );

		if ( cullType == CT_BACK_SIDED )
		{
			if ( backEnd.viewParms.isMirror )
			{
				qglCullFace( GL_FRONT );
			}
			else
			{
				qglCullFace( GL_BACK );
			}
		}
		else
		{
			if ( backEnd.viewParms.isMirror )
			{
				qglCullFace( GL_BACK );
			}
			else
			{
				qglCullFace( GL_FRONT );
			}
		}
	}
}

/*
** GL_TexEnv
*/
void GL_TexEnv( int env )
{
	if ( env == glState.texEnv[glState.currenttmu] )
	{
		return;
	}

	glState.texEnv[glState.currenttmu] = env;


	switch ( env )
	{
	case GL_MODULATE:
		qglTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );
		break;
	case GL_REPLACE:
		qglTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE );
		break;
	case GL_DECAL:
		qglTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL );
		break;
	case GL_ADD:
		qglTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_ADD );
		break;
	default:
		ri.Error( ERR_DROP, "GL_TexEnv: invalid env '%d' passed\n", env );
		break;
	}
}

/*
** GL_State
**
** This routine is responsible for setting the most commonly changed state
** in Q3.
*/
void GL_State( unsigned long stateBits )
{
	unsigned long diff = stateBits ^ glState.glStateBits;

	if ( !diff )
	{
		return;
	}

	//
	// check depthFunc bits
	//
	if ( diff & GLS_DEPTHFUNC_EQUAL )
	{
		if ( stateBits & GLS_DEPTHFUNC_EQUAL )
		{
			qglDepthFunc( GL_EQUAL );
		}
		else
		{
			qglDepthFunc( GL_LEQUAL );
		}
	}

	//
	// check blend bits
	//
	if ( diff & ( GLS_SRCBLEND_BITS | GLS_DSTBLEND_BITS ) )
	{
		GLenum srcFactor, dstFactor;

		if ( stateBits & ( GLS_SRCBLEND_BITS | GLS_DSTBLEND_BITS ) )
		{
			switch ( stateBits & GLS_SRCBLEND_BITS )
			{
			case GLS_SRCBLEND_ZERO:
				srcFactor = GL_ZERO;
				break;
			case GLS_SRCBLEND_ONE:
				srcFactor = GL_ONE;
				break;
			case GLS_SRCBLEND_DST_COLOR:
				srcFactor = GL_DST_COLOR;
				break;
			case GLS_SRCBLEND_ONE_MINUS_DST_COLOR:
				srcFactor = GL_ONE_MINUS_DST_COLOR;
				break;
			case GLS_SRCBLEND_SRC_ALPHA:
				srcFactor = GL_SRC_ALPHA;
				break;
			case GLS_SRCBLEND_ONE_MINUS_SRC_ALPHA:
				srcFactor = GL_ONE_MINUS_SRC_ALPHA;
				break;
			case GLS_SRCBLEND_DST_ALPHA:
				srcFactor = GL_DST_ALPHA;
				break;
			case GLS_SRCBLEND_ONE_MINUS_DST_ALPHA:
				srcFactor = GL_ONE_MINUS_DST_ALPHA;
				break;
			case GLS_SRCBLEND_ALPHA_SATURATE:
				srcFactor = GL_SRC_ALPHA_SATURATE;
				break;
			default:
				srcFactor = GL_ONE;		// to get warning to shut up
				ri.Error( ERR_DROP, "GL_State: invalid src blend state bits\n" );
				break;
			}

			switch ( stateBits & GLS_DSTBLEND_BITS )
			{
			case GLS_DSTBLEND_ZERO:
				dstFactor = GL_ZERO;
				break;
			case GLS_DSTBLEND_ONE:
				dstFactor = GL_ONE;
				break;
			case GLS_DSTBLEND_SRC_COLOR:
				dstFactor = GL_SRC_COLOR;
				break;
			case GLS_DSTBLEND_ONE_MINUS_SRC_COLOR:
				dstFactor = GL_ONE_MINUS_SRC_COLOR;
				break;
			case GLS_DSTBLEND_SRC_ALPHA:
				dstFactor = GL_SRC_ALPHA;
				break;
			case GLS_DSTBLEND_ONE_MINUS_SRC_ALPHA:
				dstFactor = GL_ONE_MINUS_SRC_ALPHA;
				break;
			case GLS_DSTBLEND_DST_ALPHA:
				dstFactor = GL_DST_ALPHA;
				break;
			case GLS_DSTBLEND_ONE_MINUS_DST_ALPHA:
				dstFactor = GL_ONE_MINUS_DST_ALPHA;
				break;
			default:
				dstFactor = GL_ONE;		// to get warning to shut up
				ri.Error( ERR_DROP, "GL_State: invalid dst blend state bits\n" );
				break;
			}

			qglEnable( GL_BLEND );
			qglBlendFunc( srcFactor, dstFactor );
		}
		else
		{
			qglDisable( GL_BLEND );
		}
	}

	//
	// check depthmask
	//
	if ( diff & GLS_DEPTHMASK_TRUE )
	{
		if ( stateBits & GLS_DEPTHMASK_TRUE )
		{
			qglDepthMask( GL_TRUE );
		}
		else
		{
			qglDepthMask( GL_FALSE );
		}
	}

	//
	// fill/line mode
	//
	if ( diff & GLS_POLYMODE_LINE )
	{
		if ( stateBits & GLS_POLYMODE_LINE )
		{
			qglPolygonMode( GL_FRONT_AND_BACK, GL_LINE );
		}
		else
		{
			qglPolygonMode( GL_FRONT_AND_BACK, GL_FILL );
		}
	}

	//
	// depthtest
	//
	if ( diff & GLS_DEPTHTEST_DISABLE )
	{
		if ( stateBits & GLS_DEPTHTEST_DISABLE )
		{
			qglDisable( GL_DEPTH_TEST );
		}
		else
		{
			qglEnable( GL_DEPTH_TEST );
		}
	}

	//
	// alpha test
	//
	if ( diff & GLS_ATEST_BITS )
	{
		switch ( stateBits & GLS_ATEST_BITS )
		{
		case 0:
			qglDisable( GL_ALPHA_TEST );
			break;
		case GLS_ATEST_GT_0:
			qglEnable( GL_ALPHA_TEST );
			qglAlphaFunc( GL_GREATER, 0.0f );
			break;
		case GLS_ATEST_LT_80:
			qglEnable( GL_ALPHA_TEST );
			qglAlphaFunc( GL_LESS, 0.5f );
			break;
		case GLS_ATEST_GE_80:
			qglEnable( GL_ALPHA_TEST );
			qglAlphaFunc( GL_GEQUAL, 0.5f );
			break;
		default:
			assert( 0 );
			break;
		}
	}

	glState.glStateBits = stateBits;
}



/*
================
RB_Hyperspace

A player has predicted a teleport, but hasn't arrived yet
================
*/
static void RB_Hyperspace( void ) {
	float		c;

	if ( !backEnd.isHyperspace ) {
		// do initialization shit
	}

	c = ( backEnd.refdef.time & 255 ) / 255.0f;
	qglClearColor( c, c, c, 1 );
	qglClear( GL_COLOR_BUFFER_BIT );

	backEnd.isHyperspace = qtrue;
}


/*
=============
RB_DrawTeleporterFlash

Render the teleport flash overlay when enabled.
=============
*/
static void RB_DrawTeleporterFlash( void ) {
	if ( !r_teleporterFlash || !r_teleporterFlash->integer ) {
		return;
	}

	if ( !( backEnd.refdef.rdflags & RDF_HYPERSPACE ) ) {
		return;
	}

	if ( !backEnd.projection2D ) {
		RB_SetGL2D();
	}

	GL_State( GLS_DEPTHTEST_DISABLE | GLS_SRCBLEND_ONE | GLS_DSTBLEND_ONE );
	qglColor4f( 1.0f, 0.2f, 0.2f, 0.35f );

	qglBegin( GL_QUADS );
	qglVertex2f( 0, 0 );
	qglVertex2f( glConfig.vidWidth, 0 );
	qglVertex2f( glConfig.vidWidth, glConfig.vidHeight );
	qglVertex2f( 0, glConfig.vidHeight );
	qglEnd();

	qglColor4f( 1.0f, 1.0f, 1.0f, 1.0f );

	if ( backEnd.refdef.time != s_lastTeleporterFlashLogTime ) {
		ri.Printf( PRINT_DEVELOPER, "QA: r_teleporterFlash overlay active\n" );
		s_lastTeleporterFlashLogTime = backEnd.refdef.time;
	}
}

static void SetViewportAndScissor( void ) {
	qglMatrixMode(GL_PROJECTION);
	qglLoadMatrixf( backEnd.viewParms.projectionMatrix );
	qglMatrixMode(GL_MODELVIEW);

	// set the window clipping
	qglViewport( backEnd.viewParms.viewportX, backEnd.viewParms.viewportY, 
		backEnd.viewParms.viewportWidth, backEnd.viewParms.viewportHeight );
	qglScissor( backEnd.viewParms.viewportX, backEnd.viewParms.viewportY, 
		backEnd.viewParms.viewportWidth, backEnd.viewParms.viewportHeight );
}

/*
=================
RB_BeginDrawingView

Any mirrored or portaled views have already been drawn, so prepare
to actually render the visible surfaces for this view
=================
*/
void RB_BeginDrawingView (void) {
	int clearBits = 0;

	// sync with gl if needed
	if ( r_finish->integer == 1 && !glState.finishCalled ) {
		qglFinish ();
		glState.finishCalled = qtrue;
	}
	if ( r_finish->integer == 0 ) {
		glState.finishCalled = qtrue;
	}

	// we will need to change the projection matrix before drawing
	// 2D images again
	backEnd.projection2D = qfalse;

	//
	// set the modelview matrix for the viewer
	//
	SetViewportAndScissor();

	// ensures that depth writes are enabled for the depth clear
	GL_State( GLS_DEFAULT );
	// clear relevant buffers
	clearBits = GL_DEPTH_BUFFER_BIT;

	if ( r_measureOverdraw->integer || r_shadows->integer == 2 )
	{
		clearBits |= GL_STENCIL_BUFFER_BIT;
	}
	if ( r_fastsky->integer && !( backEnd.refdef.rdflags & RDF_NOWORLDMODEL ) )
	{
		clearBits |= GL_COLOR_BUFFER_BIT;	// FIXME: only if sky shaders have been used
#ifdef _DEBUG
		qglClearColor( 0.8f, 0.7f, 0.4f, 1.0f );	// FIXME: get color of sky
#else
		qglClearColor( 0.0f, 0.0f, 0.0f, 1.0f );	// FIXME: get color of sky
#endif
	}
	qglClear( clearBits );

	if ( ( backEnd.refdef.rdflags & RDF_HYPERSPACE ) )
	{
		RB_Hyperspace();
		return;
	}
	else
	{
		backEnd.isHyperspace = qfalse;
	}

	glState.faceCulling = -1;		// force face culling to set next time

	// we will only draw a sun if there was sky rendered in this view
	backEnd.skyRenderedThisView = qfalse;

	// clip to the plane of the portal
	if ( backEnd.viewParms.isPortal ) {
		float	plane[4];
		double	plane2[4];

		plane[0] = backEnd.viewParms.portalPlane.normal[0];
		plane[1] = backEnd.viewParms.portalPlane.normal[1];
		plane[2] = backEnd.viewParms.portalPlane.normal[2];
		plane[3] = backEnd.viewParms.portalPlane.dist;

		plane2[0] = DotProduct (backEnd.viewParms.or.axis[0], plane);
		plane2[1] = DotProduct (backEnd.viewParms.or.axis[1], plane);
		plane2[2] = DotProduct (backEnd.viewParms.or.axis[2], plane);
		plane2[3] = DotProduct (plane, backEnd.viewParms.or.origin) - plane[3];

		qglLoadMatrixf( s_flipMatrix );
		qglClipPlane (GL_CLIP_PLANE0, plane2);
		qglEnable (GL_CLIP_PLANE0);
	} else {
		qglDisable (GL_CLIP_PLANE0);
	}
}


#define	MAC_EVENT_PUMP_MSEC		5

/*
==================
RB_RenderDrawSurfList
==================
*/
void RB_RenderDrawSurfList( drawSurf_t *drawSurfs, int numDrawSurfs ) {
	shader_t		*shader, *oldShader;
	int				fogNum, oldFogNum;
	int				entityNum, oldEntityNum;
	int				dlighted, oldDlighted;
	qboolean		depthRange, oldDepthRange;
	int				i;
	drawSurf_t		*drawSurf;
	int				oldSort;
	float			originalTime;
#ifdef __MACOS__
	int				macEventTime;

	Sys_PumpEvents();		// crutch up the mac's limited buffer queue size

	// we don't want to pump the event loop too often and waste time, so
	// we are going to check every shader change
	macEventTime = ri.Milliseconds() + MAC_EVENT_PUMP_MSEC;
#endif

	// save original time for entity shader offsets
	originalTime = backEnd.refdef.floatTime;

	// clear the z buffer, set the modelview, etc
	RB_BindOffscreenRenderTarget();
	RB_BeginDrawingView ();

	// draw everything
	oldEntityNum = -1;
	backEnd.currentEntity = &tr.worldEntity;
	oldShader = NULL;
	oldFogNum = -1;
	oldDepthRange = qfalse;
	oldDlighted = qfalse;
	oldSort = -1;
	depthRange = qfalse;

	backEnd.pc.c_surfaces += numDrawSurfs;

	for (i = 0, drawSurf = drawSurfs ; i < numDrawSurfs ; i++, drawSurf++) {
		if ( drawSurf->sort == oldSort ) {
			// fast path, same as previous sort
			rb_surfaceTable[ *drawSurf->surface ]( drawSurf->surface );
			continue;
		}
		oldSort = drawSurf->sort;
		R_DecomposeSort( drawSurf->sort, &entityNum, &shader, &fogNum, &dlighted );

		//
		// change the tess parameters if needed
		// a "entityMergable" shader is a shader that can have surfaces from seperate
		// entities merged into a single batch, like smoke and blood puff sprites
		if (shader != oldShader || fogNum != oldFogNum || dlighted != oldDlighted 
			|| ( entityNum != oldEntityNum && !shader->entityMergable ) ) {
			if (oldShader != NULL) {
#ifdef __MACOS__	// crutch up the mac's limited buffer queue size
				int		t;

				t = ri.Milliseconds();
				if ( t > macEventTime ) {
					macEventTime = t + MAC_EVENT_PUMP_MSEC;
					Sys_PumpEvents();
				}
#endif
				RB_EndSurface();
			}
			RB_BeginSurface( shader, fogNum );
			oldShader = shader;
			oldFogNum = fogNum;
			oldDlighted = dlighted;
		}

		//
		// change the modelview matrix if needed
		//
		if ( entityNum != oldEntityNum ) {
			depthRange = qfalse;

			if ( entityNum != ENTITYNUM_WORLD ) {
				backEnd.currentEntity = &backEnd.refdef.entities[entityNum];
				backEnd.refdef.floatTime = originalTime - backEnd.currentEntity->e.shaderTime;
				// we have to reset the shaderTime as well otherwise image animations start
				// from the wrong frame
				tess.shaderTime = backEnd.refdef.floatTime - tess.shader->timeOffset;

				// set up the transformation matrix
				R_RotateForEntity( backEnd.currentEntity, &backEnd.viewParms, &backEnd.or );

				// set up the dynamic lighting if needed
				if ( backEnd.currentEntity->needDlights ) {
					R_TransformDlights( backEnd.refdef.num_dlights, backEnd.refdef.dlights, &backEnd.or );
				}

				if ( backEnd.currentEntity->e.renderfx & RF_DEPTHHACK ) {
					// hack the depth range to prevent view model from poking into walls
					depthRange = qtrue;
				}
			} else {
				backEnd.currentEntity = &tr.worldEntity;
				backEnd.refdef.floatTime = originalTime;
				backEnd.or = backEnd.viewParms.world;
				// we have to reset the shaderTime as well otherwise image animations on
				// the world (like water) continue with the wrong frame
				tess.shaderTime = backEnd.refdef.floatTime - tess.shader->timeOffset;
				R_TransformDlights( backEnd.refdef.num_dlights, backEnd.refdef.dlights, &backEnd.or );
			}

			qglLoadMatrixf( backEnd.or.modelMatrix );

			//
			// change depthrange if needed
			//
			if ( oldDepthRange != depthRange ) {
				if ( depthRange ) {
					qglDepthRange (0, 0.3);
				} else {
					qglDepthRange (0, 1);
				}
				oldDepthRange = depthRange;
			}

			oldEntityNum = entityNum;
		}

		// add the triangles for this surface
		rb_surfaceTable[ *drawSurf->surface ]( drawSurf->surface );
	}

	backEnd.refdef.floatTime = originalTime;

	// draw the contents of the last shader batch
	if (oldShader != NULL) {
		RB_EndSurface();
	}

	// go back to the world modelview matrix
	qglLoadMatrixf( backEnd.viewParms.world.modelMatrix );
	if ( depthRange ) {
		qglDepthRange (0, 1);
	}

#if 0
	RB_DrawSun();
#endif
	// darken down any stencil shadows
	RB_ShadowFinish();

	// add light flares on lights that aren't obscured
	RB_RenderFlares();

	RB_DrawTeleporterFlash();

#ifdef __MACOS__
	Sys_PumpEvents();		// crutch up the mac's limited buffer queue size
#endif
}


/*
============================================================================

RENDER BACK END THREAD FUNCTIONS

============================================================================
*/

/*
================
RB_SetGL2D

================
*/
void	RB_SetGL2D (void) {
	backEnd.projection2D = qtrue;

	// set 2D virtual screen size
	qglViewport( 0, 0, glConfig.vidWidth, glConfig.vidHeight );
	qglScissor( 0, 0, glConfig.vidWidth, glConfig.vidHeight );
	qglMatrixMode(GL_PROJECTION);
    qglLoadIdentity ();
	qglOrtho (0, glConfig.vidWidth, glConfig.vidHeight, 0, 0, 1);
	qglMatrixMode(GL_MODELVIEW);
    qglLoadIdentity ();

	GL_State( GLS_DEPTHTEST_DISABLE |
			  GLS_SRCBLEND_SRC_ALPHA |
			  GLS_DSTBLEND_ONE_MINUS_SRC_ALPHA );

	qglDisable( GL_CULL_FACE );
	qglDisable( GL_CLIP_PLANE0 );

	// set time for 2D shaders
	backEnd.refdef.time = ri.Milliseconds();
	backEnd.refdef.floatTime = backEnd.refdef.time * 0.001f;
}


/*
=============
RE_StretchRaw

FIXME: not exactly backend
Stretches a raw 32 bit power of 2 bitmap image over the given screen rectangle.
Used for cinematics.
=============
*/
void RE_StretchRaw (int x, int y, int w, int h, int cols, int rows, const byte *data, int client, qboolean dirty) {
	int			i, j;
	int			start, end;

	if ( !tr.registered ) {
		return;
	}
	R_SyncRenderThread();

	// we definately want to sync every frame for the cinematics
	qglFinish();

	start = end = 0;
	if ( r_speeds->integer ) {
		start = ri.Milliseconds();
	}

	// make sure rows and cols are powers of 2
	for ( i = 0 ; ( 1 << i ) < cols ; i++ ) {
	}
	for ( j = 0 ; ( 1 << j ) < rows ; j++ ) {
	}
	if ( ( 1 << i ) != cols || ( 1 << j ) != rows) {
		ri.Error (ERR_DROP, "Draw_StretchRaw: size not a power of 2: %i by %i", cols, rows);
	}

	GL_Bind( tr.scratchImage[client] );

	// if the scratchImage isn't in the format we want, specify it as a new texture
	if ( cols != tr.scratchImage[client]->width || rows != tr.scratchImage[client]->height ) {
		tr.scratchImage[client]->width = tr.scratchImage[client]->uploadWidth = cols;
		tr.scratchImage[client]->height = tr.scratchImage[client]->uploadHeight = rows;
		qglTexImage2D( GL_TEXTURE_2D, 0, GL_RGB8, cols, rows, 0, GL_RGBA, GL_UNSIGNED_BYTE, data );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP );	
	} else {
		if (dirty) {
			// otherwise, just subimage upload it so that drivers can tell we are going to be changing
			// it and don't try and do a texture compression
			qglTexSubImage2D( GL_TEXTURE_2D, 0, 0, 0, cols, rows, GL_RGBA, GL_UNSIGNED_BYTE, data );
		}
	}

	if ( r_speeds->integer ) {
		end = ri.Milliseconds();
		ri.Printf( PRINT_ALL, "qglTexSubImage2D %i, %i: %i msec\n", cols, rows, end - start );
	}

	RB_SetGL2D();

	qglColor3f( tr.identityLight, tr.identityLight, tr.identityLight );

	qglBegin (GL_QUADS);
	qglTexCoord2f ( 0.5f / cols,  0.5f / rows );
	qglVertex2f (x, y);
	qglTexCoord2f ( ( cols - 0.5f ) / cols ,  0.5f / rows );
	qglVertex2f (x+w, y);
	qglTexCoord2f ( ( cols - 0.5f ) / cols, ( rows - 0.5f ) / rows );
	qglVertex2f (x+w, y+h);
	qglTexCoord2f ( 0.5f / cols, ( rows - 0.5f ) / rows );
	qglVertex2f (x, y+h);
	qglEnd ();
}

void RE_UploadCinematic (int w, int h, int cols, int rows, const byte *data, int client, qboolean dirty) {

	GL_Bind( tr.scratchImage[client] );

	// if the scratchImage isn't in the format we want, specify it as a new texture
	if ( cols != tr.scratchImage[client]->width || rows != tr.scratchImage[client]->height ) {
		tr.scratchImage[client]->width = tr.scratchImage[client]->uploadWidth = cols;
		tr.scratchImage[client]->height = tr.scratchImage[client]->uploadHeight = rows;
		qglTexImage2D( GL_TEXTURE_2D, 0, GL_RGB8, cols, rows, 0, GL_RGBA, GL_UNSIGNED_BYTE, data );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP );
		qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP );	
	} else {
		if (dirty) {
			// otherwise, just subimage upload it so that drivers can tell we are going to be changing
			// it and don't try and do a texture compression
			qglTexSubImage2D( GL_TEXTURE_2D, 0, 0, 0, cols, rows, GL_RGBA, GL_UNSIGNED_BYTE, data );
		}
	}
}


/*
=============
RB_SetColor

=============
*/
const void	*RB_SetColor( const void *data ) {
	const setColorCommand_t	*cmd;

	cmd = (const setColorCommand_t *)data;

	backEnd.color2D[0] = cmd->color[0] * 255;
	backEnd.color2D[1] = cmd->color[1] * 255;
	backEnd.color2D[2] = cmd->color[2] * 255;
	backEnd.color2D[3] = cmd->color[3] * 255;

	return (const void *)(cmd + 1);
}

/*
=============
RB_StretchPic
=============
*/
const void *RB_StretchPic ( const void *data ) {
	const stretchPicCommand_t	*cmd;
	shader_t *shader;
	int		numVerts, numIndexes;

	cmd = (const stretchPicCommand_t *)data;

	if ( !backEnd.projection2D ) {
		RB_SetGL2D();
	}

	shader = cmd->shader;
	if ( shader != tess.shader ) {
		if ( tess.numIndexes ) {
			RB_EndSurface();
		}
		backEnd.currentEntity = &backEnd.entity2D;
		RB_BeginSurface( shader, 0 );
	}

	RB_CHECKOVERFLOW( 4, 6 );
	numVerts = tess.numVertexes;
	numIndexes = tess.numIndexes;

	tess.numVertexes += 4;
	tess.numIndexes += 6;

	tess.indexes[ numIndexes ] = numVerts + 3;
	tess.indexes[ numIndexes + 1 ] = numVerts + 0;
	tess.indexes[ numIndexes + 2 ] = numVerts + 2;
	tess.indexes[ numIndexes + 3 ] = numVerts + 2;
	tess.indexes[ numIndexes + 4 ] = numVerts + 0;
	tess.indexes[ numIndexes + 5 ] = numVerts + 1;

	*(int *)tess.vertexColors[ numVerts ] =
		*(int *)tess.vertexColors[ numVerts + 1 ] =
		*(int *)tess.vertexColors[ numVerts + 2 ] =
		*(int *)tess.vertexColors[ numVerts + 3 ] = *(int *)backEnd.color2D;

	tess.xyz[ numVerts ][0] = cmd->x;
	tess.xyz[ numVerts ][1] = cmd->y;
	tess.xyz[ numVerts ][2] = 0;

	tess.texCoords[ numVerts ][0][0] = cmd->s1;
	tess.texCoords[ numVerts ][0][1] = cmd->t1;

	tess.xyz[ numVerts + 1 ][0] = cmd->x + cmd->w;
	tess.xyz[ numVerts + 1 ][1] = cmd->y;
	tess.xyz[ numVerts + 1 ][2] = 0;

	tess.texCoords[ numVerts + 1 ][0][0] = cmd->s2;
	tess.texCoords[ numVerts + 1 ][0][1] = cmd->t1;

	tess.xyz[ numVerts + 2 ][0] = cmd->x + cmd->w;
	tess.xyz[ numVerts + 2 ][1] = cmd->y + cmd->h;
	tess.xyz[ numVerts + 2 ][2] = 0;

	tess.texCoords[ numVerts + 2 ][0][0] = cmd->s2;
	tess.texCoords[ numVerts + 2 ][0][1] = cmd->t2;

	tess.xyz[ numVerts + 3 ][0] = cmd->x;
	tess.xyz[ numVerts + 3 ][1] = cmd->y + cmd->h;
	tess.xyz[ numVerts + 3 ][2] = 0;

	tess.texCoords[ numVerts + 3 ][0][0] = cmd->s1;
	tess.texCoords[ numVerts + 3 ][0][1] = cmd->t2;

	return (const void *)(cmd + 1);
}


/*
=============
RB_DrawSurfs

=============
*/
const void	*RB_DrawSurfs( const void *data ) {
	const drawSurfsCommand_t	*cmd;

	// finish any 2D drawing if needed
	if ( tess.numIndexes ) {
		RB_EndSurface();
	}

	cmd = (const drawSurfsCommand_t *)data;

	backEnd.refdef = cmd->refdef;
	backEnd.viewParms = cmd->viewParms;

	RB_RenderDrawSurfList( cmd->drawSurfs, cmd->numDrawSurfs );

	return (const void *)(cmd + 1);
}


/*
=============
RB_DrawBuffer

=============
*/
const void	*RB_DrawBuffer( const void *data ) {
	const drawBufferCommand_t	*cmd;

	cmd = (const drawBufferCommand_t *)data;

	qglDrawBuffer( cmd->buffer );

	// clear screen for debugging
	if ( r_clear->integer ) {
		qglClearColor( 1, 0, 0.5, 1 );
		qglClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
	}

	return (const void *)(cmd + 1);
}

/*
===============
RB_ShowImages

Draw all the images to the screen, on top of whatever
was there.  This is used to test for texture thrashing.

Also called by RE_EndRegistration
===============
*/
void RB_ShowImages( void ) {
	int		i;
	image_t	*image;
	float	x, y, w, h;
	int		start, end;

	if ( !backEnd.projection2D ) {
		RB_SetGL2D();
	}

	qglClear( GL_COLOR_BUFFER_BIT );

	qglFinish();

	start = ri.Milliseconds();

	for ( i=0 ; i<tr.numImages ; i++ ) {
		image = tr.images[i];

		w = glConfig.vidWidth / 20;
		h = glConfig.vidHeight / 15;
		x = i % 20 * w;
		y = i / 20 * h;

		// show in proportional size in mode 2
		if ( r_showImages->integer == 2 ) {
			w *= image->uploadWidth / 512.0f;
			h *= image->uploadHeight / 512.0f;
		}

		GL_Bind( image );
		qglBegin (GL_QUADS);
		qglTexCoord2f( 0, 0 );
		qglVertex2f( x, y );
		qglTexCoord2f( 1, 0 );
		qglVertex2f( x + w, y );
		qglTexCoord2f( 1, 1 );
		qglVertex2f( x + w, y + h );
		qglTexCoord2f( 0, 1 );
		qglVertex2f( x, y + h );
		qglEnd();
	}

	qglFinish();

	end = ri.Milliseconds();
	ri.Printf( PRINT_ALL, "%i msec to draw all images\n", end - start );

}


/*
=============
RB_SwapBuffers

=============
*/
const void	*RB_SwapBuffers( const void *data ) {
	const swapBuffersCommand_t	*cmd;

	// finish any 2D drawing if needed
	if ( tess.numIndexes ) {
		RB_EndSurface();
	}

	RB_ReleaseOffscreenRenderTarget();

	// texture swapping test
	if ( r_showImages->integer ) {
		RB_ShowImages();
	}

	cmd = (const swapBuffersCommand_t *)data;

	// we measure overdraw by reading back the stencil buffer and
	// counting up the number of increments that have happened
	if ( r_measureOverdraw->integer ) {
		int i;
		long sum = 0;
		unsigned char *stencilReadback;

		stencilReadback = ri.Hunk_AllocateTempMemory( glConfig.vidWidth * glConfig.vidHeight );
		qglReadPixels( 0, 0, glConfig.vidWidth, glConfig.vidHeight, GL_STENCIL_INDEX, GL_UNSIGNED_BYTE, stencilReadback );

		for ( i = 0; i < glConfig.vidWidth * glConfig.vidHeight; i++ ) {
			sum += stencilReadback[i];
		}

		backEnd.pc.c_overDraw += sum;
		ri.Hunk_FreeTempMemory( stencilReadback );
	}


	RB_SubmitPostProcess();

	if ( !glState.finishCalled ) {
		qglFinish();
	}

	GLimp_LogComment( "***************** RB_SwapBuffers *****************\n\n\n" );

	GLimp_EndFrame();

	backEnd.projection2D = qfalse;

	return (const void *)(cmd + 1);
}

/*
====================
RB_ExecuteRenderCommands

This function will be called synchronously if running without
smp extensions, or asynchronously by another thread.
====================
*/
void RB_ExecuteRenderCommands( const void *data ) {
	int		t1, t2;

	t1 = ri.Milliseconds ();

	if ( !r_smp->integer || data == backEndData[0]->commands.cmds ) {
		backEnd.smpFrame = 0;
	} else {
		backEnd.smpFrame = 1;
	}

	RB_ResetPostProcessState();

	while ( 1 ) {
		switch ( *(const int *)data ) {
		case RC_SET_COLOR:
			data = RB_SetColor( data );
			break;
		case RC_STRETCH_PIC:
			data = RB_StretchPic( data );
			break;
		case RC_DRAW_SURFS:
			data = RB_DrawSurfs( data );
			break;
		case RC_DRAW_BUFFER:
			data = RB_DrawBuffer( data );
			break;
		case RC_SWAP_BUFFERS:
			data = RB_SwapBuffers( data );
			break;
		case RC_SCREENSHOT:
			data = RB_TakeScreenshotCmd( data );
			break;

		case RC_END_OF_LIST:
		default:
			// stop rendering on this thread
			t2 = ri.Milliseconds ();
			backEnd.pc.msec = t2 - t1;
			return;
		}
	}

}


/*
================
RB_RenderThread
================
*/
void RB_RenderThread( void ) {
	const void	*data;

	// wait for either a rendering command or a quit command
	while ( 1 ) {
		// sleep until we have work to do
		data = GLimp_RendererSleep();

		if ( !data ) {
			return;	// all done, renderer is shutting down
		}

		renderThreadActive = qtrue;

		RB_ExecuteRenderCommands( data );

		renderThreadActive = qfalse;
	}
}

