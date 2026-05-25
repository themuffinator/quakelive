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

#ifndef GL_RGBA16
#define GL_RGBA16 0x805B
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
static image_t *RB_UploadBloomScratch( int scratchIndex, int width, int height );
static void RB_DrawBloomSpread( float xOffset, float yOffset, int width, int height );
void RB_SetGL2D( void );
static void RBPP_Init( void );
static void RBPP_Shutdown( void );
static void RBPP_BindSceneRenderTarget( void );
static void RBPP_ReleaseSceneRenderTarget( void );
static void RBPP_ResetIfNeeded( void );
static void RBPP_Submit( void );


/*
=============
RB_InitRenderTargets

Initialize framebuffer storage for post-process rendering.
=============
*/
void RB_InitRenderTargets( void ) {
	RBPP_Init();
}


/*
=============
RB_ShutdownRenderTargets

Release framebuffer storage used for post-process rendering.
=============
*/
void RB_ShutdownRenderTargets( void ) {
	RBPP_Shutdown();
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
	RBPP_BindSceneRenderTarget();
}


/*
=============
RB_ReleaseOffscreenRenderTarget

Restore rendering to the default framebuffer.
=============
*/
static void RB_ReleaseOffscreenRenderTarget( void ) {
	RBPP_ReleaseSceneRenderTarget();
}

/*
=============
RB_ResetPostProcessState

Rebuild post-process render targets when toggles change and clear the reset flag once handled.
=============
*/
static void RB_ResetPostProcessState( void ) {
	RBPP_ResetIfNeeded();
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

Legacy compatibility hook kept until the shader-backed post-process path fully retires the old helper family.
=============
*/
static void RB_ApplyColorCorrection( void ) {
	return;
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

Set texture environment controls for the legacy scratch bloom stage.
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

Render a textured quad with offsets for the legacy scratch bloom stage.
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
	RBPP_Submit();
}

#ifndef GL_TEXTURE_RECTANGLE_ARB
#define GL_TEXTURE_RECTANGLE_ARB 0x84F5
#endif

#ifndef GL_MAX_RECTANGLE_TEXTURE_SIZE_ARB
#define GL_MAX_RECTANGLE_TEXTURE_SIZE_ARB 0x84F8
#endif

#ifndef GL_FRAGMENT_SHADER_ARB
#define GL_FRAGMENT_SHADER_ARB 0x8B30
#endif

#ifndef GL_VERTEX_SHADER_ARB
#define GL_VERTEX_SHADER_ARB 0x8B31
#endif

#ifndef GL_OBJECT_COMPILE_STATUS_ARB
#define GL_OBJECT_COMPILE_STATUS_ARB 0x8B81
#endif

#ifndef GL_OBJECT_LINK_STATUS_ARB
#define GL_OBJECT_LINK_STATUS_ARB 0x8B82
#endif

#ifndef GL_OBJECT_INFO_LOG_LENGTH_ARB
#define GL_OBJECT_INFO_LOG_LENGTH_ARB 0x8B84
#endif

#ifndef GL_STENCIL_ATTACHMENT_EXT
#define GL_STENCIL_ATTACHMENT_EXT 0x8D20
#endif

#ifndef GL_DEPTH24_STENCIL8_EXT
#define GL_DEPTH24_STENCIL8_EXT 0x88F0
#endif

#ifndef GLcharARB
typedef char GLcharARB;
#endif

#ifndef GLhandleARB
typedef unsigned int GLhandleARB;
#endif

#ifndef PFNGLCREATESHADEROBJECTARBPROC
typedef GLhandleARB (APIENTRY * PFNGLCREATESHADEROBJECTARBPROC) (GLenum);
typedef void (APIENTRY * PFNGLSHADERSOURCEARBPROC) (GLhandleARB, GLsizei, const GLcharARB **, const GLint *);
typedef void (APIENTRY * PFNGLCOMPILESHADERARBPROC) (GLhandleARB);
typedef void (APIENTRY * PFNGLGETOBJECTPARAMETERIVARBPROC) (GLhandleARB, GLenum, GLint *);
typedef void (APIENTRY * PFNGLGETINFOLOGARBPROC) (GLhandleARB, GLsizei, GLsizei *, GLcharARB *);
typedef void (APIENTRY * PFNGLDELETEOBJECTARBPROC) (GLhandleARB);
typedef GLhandleARB (APIENTRY * PFNGLCREATEPROGRAMOBJECTARBPROC) (void);
typedef void (APIENTRY * PFNGLATTACHOBJECTARBPROC) (GLhandleARB, GLhandleARB);
typedef void (APIENTRY * PFNGLLINKPROGRAMARBPROC) (GLhandleARB);
typedef void (APIENTRY * PFNGLUSEPROGRAMOBJECTARBPROC) (GLhandleARB);
typedef GLint (APIENTRY * PFNGLGETUNIFORMLOCATIONARBPROC) (GLhandleARB, const GLcharARB *);
typedef void (APIENTRY * PFNGLUNIFORM1IARBPROC) (GLint, GLint);
typedef void (APIENTRY * PFNGLUNIFORM1FARBPROC) (GLint, GLfloat);
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
	PFNGLCREATESHADEROBJECTARBPROC qglCreateShaderObjectARBFunc;
	PFNGLSHADERSOURCEARBPROC qglShaderSourceARBFunc;
	PFNGLCOMPILESHADERARBPROC qglCompileShaderARBFunc;
	PFNGLGETOBJECTPARAMETERIVARBPROC qglGetObjectParameterivARBFunc;
	PFNGLGETINFOLOGARBPROC qglGetInfoLogARBFunc;
	PFNGLDELETEOBJECTARBPROC qglDeleteObjectARBFunc;
	PFNGLCREATEPROGRAMOBJECTARBPROC qglCreateProgramObjectARBFunc;
	PFNGLATTACHOBJECTARBPROC qglAttachObjectARBFunc;
	PFNGLLINKPROGRAMARBPROC qglLinkProgramARBFunc;
	PFNGLUSEPROGRAMOBJECTARBPROC qglUseProgramObjectARBFunc;
	PFNGLGETUNIFORMLOCATIONARBPROC qglGetUniformLocationARBFunc;
	PFNGLUNIFORM1IARBPROC qglUniform1iARBFunc;
	PFNGLUNIFORM1FARBPROC qglUniform1fARBFunc;
} ppProcs_t;

typedef struct {
	GLuint framebuffer;
	GLuint texture;
	GLuint depthBuffer;
	int width;
	int height;
	qboolean initialized;
} ppRenderTarget_t;

typedef struct {
	const char *name;
	const char *fragmentPath;
	const char *vertexPath;
	GLhandleARB fragmentObject;
	GLhandleARB vertexObject;
	GLhandleARB programObject;
	GLint backBufferTexUniform;
	GLint bloomTexUniform;
	GLint brightThresholdUniform;
	GLint bloomSaturationUniform;
	GLint bloomIntensityUniform;
	GLint sceneIntensityUniform;
	GLint sceneSaturationUniform;
	GLint gammaRecipUniform;
	GLint overbrightUniform;
	GLint contrastUniform;
	GLint blurStepUniform;
	GLint blurFalloffUniform;
} ppProgram_t;

typedef struct {
	ppProcs_t procs;
	qboolean procsLoaded;
	qboolean supported;
	int maxRectangleTextureSize;
	ppRenderTarget_t sceneTarget;
	ppRenderTarget_t bloomDownsampleTarget;
	ppRenderTarget_t bloomBrightTarget;
	ppRenderTarget_t bloomBlurVerticalTarget;
	ppRenderTarget_t bloomBlurHorizontalTarget;
	ppRenderTarget_t bloomQuarterDownsampleTarget;
	ppRenderTarget_t bloomQuarterVerticalTarget;
	ppRenderTarget_t bloomQuarterHorizontalTarget;
	GLuint colorCorrectTexture;
	int colorCorrectWidth;
	int colorCorrectHeight;
	ppProgram_t brightPassProgram;
	ppProgram_t downsampleProgram;
	ppProgram_t blurVerticalProgram;
	ppProgram_t blurHorizontalProgram;
	ppProgram_t combineProgram;
	ppProgram_t colorCorrectProgram;
} ppState_t;

static const GLcharARB *s_postEffectVertexShaderSource =
	"#extension GL_ARB_texture_rectangle : enable\n"
	"void main(void)\n"
	"{\n"
	"	gl_Position = ftransform();\n"
	"	gl_TexCoord[0] = gl_MultiTexCoord0;\n"
	"	gl_TexCoord[1] = gl_MultiTexCoord1;\n"
	"}\n";

static const GLcharARB *s_brightPassFragmentShaderSource =
	"#extension GL_ARB_texture_rectangle : enable\n"
	"uniform sampler2DRect backBufferTex;\n"
	"uniform float p_brightthreshold;\n"
	"void main(void)\n"
	"{\n"
	"	vec3 color = texture2DRect(backBufferTex, gl_TexCoord[0].st).rgb;\n"
	"	float brightness = max(max(color.r, color.g), color.b);\n"
	"	float scale = max(brightness - p_brightthreshold, 0.0);\n"
	"	if (brightness > 0.0)\n"
	"	{\n"
	"		scale /= brightness;\n"
	"	}\n"
	"	gl_FragColor = vec4(color * scale, 1.0);\n"
	"}\n";

static const GLcharARB *s_downsampleFragmentShaderSource =
	"#extension GL_ARB_texture_rectangle : enable\n"
	"uniform sampler2DRect backBufferTex;\n"
	"void main(void)\n"
	"{\n"
	"	vec2 coord = gl_TexCoord[0].st;\n"
	"	vec4 color = texture2DRect(backBufferTex, coord);\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(1.0, 0.0));\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(0.0, 1.0));\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(1.0, 1.0));\n"
	"	gl_FragColor = color * 0.25;\n"
	"}\n";

static const GLcharARB *s_blurVerticalFragmentShaderSource =
	"#extension GL_ARB_texture_rectangle : enable\n"
	"uniform sampler2DRect backBufferTex;\n"
	"void main(void)\n"
	"{\n"
	"	vec2 coord = gl_TexCoord[0].st;\n"
	"	float stepSize = 1.25;\n"
	"	float falloff = 0.75;\n"
	"	float centerWeight = 0.40 + (falloff * 0.20);\n"
	"	float nearWeight = 0.22 * falloff;\n"
	"	float midWeight = 0.10 * falloff;\n"
	"	float farWeight = 0.04 * falloff;\n"
	"	vec4 color = texture2DRect(backBufferTex, coord) * centerWeight;\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(0.0, stepSize)) * nearWeight;\n"
	"	color += texture2DRect(backBufferTex, coord - vec2(0.0, stepSize)) * nearWeight;\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(0.0, stepSize * 2.0)) * midWeight;\n"
	"	color += texture2DRect(backBufferTex, coord - vec2(0.0, stepSize * 2.0)) * midWeight;\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(0.0, stepSize * 3.0)) * farWeight;\n"
	"	color += texture2DRect(backBufferTex, coord - vec2(0.0, stepSize * 3.0)) * farWeight;\n"
	"	gl_FragColor = color / (centerWeight + (2.0 * (nearWeight + midWeight + farWeight)));\n"
	"}\n";

static const GLcharARB *s_blurHorizontalFragmentShaderSource =
	"#extension GL_ARB_texture_rectangle : enable\n"
	"uniform sampler2DRect backBufferTex;\n"
	"void main(void)\n"
	"{\n"
	"	vec2 coord = gl_TexCoord[0].st;\n"
	"	float stepSize = 1.25;\n"
	"	float falloff = 0.75;\n"
	"	float centerWeight = 0.40 + (falloff * 0.20);\n"
	"	float nearWeight = 0.22 * falloff;\n"
	"	float midWeight = 0.10 * falloff;\n"
	"	float farWeight = 0.04 * falloff;\n"
	"	vec4 color = texture2DRect(backBufferTex, coord) * centerWeight;\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(stepSize, 0.0)) * nearWeight;\n"
	"	color += texture2DRect(backBufferTex, coord - vec2(stepSize, 0.0)) * nearWeight;\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(stepSize * 2.0, 0.0)) * midWeight;\n"
	"	color += texture2DRect(backBufferTex, coord - vec2(stepSize * 2.0, 0.0)) * midWeight;\n"
	"	color += texture2DRect(backBufferTex, coord + vec2(stepSize * 3.0, 0.0)) * farWeight;\n"
	"	color += texture2DRect(backBufferTex, coord - vec2(stepSize * 3.0, 0.0)) * farWeight;\n"
	"	gl_FragColor = color / (centerWeight + (2.0 * (nearWeight + midWeight + farWeight)));\n"
	"}\n";

static const GLcharARB *s_combineFragmentShaderSource =
	"#extension GL_ARB_texture_rectangle : enable\n"
	"uniform sampler2DRect backBufferTex;\n"
	"uniform sampler2DRect bloomTex;\n"
	"uniform float p_bloomsaturation;\n"
	"uniform float p_bloomintensity;\n"
	"uniform float p_sceneintensity;\n"
	"uniform float p_scenesaturation;\n"
	"vec3 Saturate(vec3 color, float saturation)\n"
	"{\n"
	"	float grey = dot(color, vec3(0.2126, 0.7152, 0.0722));\n"
	"	return mix(vec3(grey), color, saturation);\n"
	"}\n"
	"void main(void)\n"
	"{\n"
	"	vec3 sceneColor = texture2DRect(backBufferTex, gl_TexCoord[0].st).rgb;\n"
	"	vec3 bloomColor = texture2DRect(bloomTex, gl_TexCoord[1].st).rgb;\n"
	"	sceneColor = Saturate(sceneColor, p_scenesaturation) * p_sceneintensity;\n"
	"	bloomColor = Saturate(bloomColor, p_bloomsaturation) * p_bloomintensity;\n"
	"	gl_FragColor = vec4(clamp(sceneColor + bloomColor, 0.0, 1.0), 1.0);\n"
	"}\n";

static const GLcharARB *s_colorCorrectFragmentShaderSource =
	"#extension GL_ARB_texture_rectangle : enable\n"
	"uniform sampler2DRect backBufferTex;\n"
	"uniform float p_gammaRecip;\n"
	"uniform float p_overbright;\n"
	"uniform float p_contrast;\n"
	"void main(void)\n"
	"{\n"
	"	vec3 color = texture2DRect(backBufferTex, gl_TexCoord[0].st).rgb;\n"
	"	color = pow(max(color, vec3(0.0)), vec3(p_gammaRecip));\n"
	"	color *= p_overbright;\n"
	"	color = ((color - 0.5) * max(p_contrast, 0.0)) + 0.5;\n"
	"	gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);\n"
	"}\n";

static ppState_t s_postProcess;

static qboolean RBPP_LoadProcs( void );
static void RBPP_DestroyRenderTarget( ppRenderTarget_t *target );
static qboolean RBPP_CreateRenderTarget( ppRenderTarget_t *target, int width, int height, qboolean linearFilter );
static void RBPP_BindRenderTarget( ppRenderTarget_t *target );
static void RBPP_Set2DState( int width, int height );
static void RBPP_BindRectangleTexture( int unit, GLuint texture );
static void RBPP_DrawQuad( int width, int height, float s0Max, float t0Max, float s1Max, float t1Max );
static const GLcharARB *RBPP_GetShaderSource( const char *sourcePath );
static void RBPP_PrintInfoLog( GLhandleARB objectHandle );
static qboolean RBPP_CompileShader( GLenum shaderType, const char *sourcePath, GLhandleARB *shaderObject );
static void RBPP_DestroyProgram( ppProgram_t *program );
static qboolean RBPP_LoadProgram( ppProgram_t *program, const char *name, const char *fragmentPath, const char *vertexPath );
static qboolean RBPP_LoadBloomPrograms( void );
static void RBPP_DestroyBloomPrograms( void );
static qboolean RBPP_LoadColorCorrectProgram( void );
static void RBPP_DestroyColorCorrectProgram( void );
static qboolean RBPP_CreateColorCorrectTexture( void );
static void RBPP_DestroyColorCorrectTexture( void );
static qboolean RBPP_InitBloomResources( void );
static void RBPP_ShutdownBloomResources( void );
static qboolean RBPP_InitColorCorrectResources( void );
static void RBPP_ShutdownColorCorrectResources( void );
static void RBPP_MirrorState( void );
static void RBPP_RebuildState( void );
static void RBPP_BlitSceneTarget( void );
static qboolean RBPP_ApplyBloom( void );
static void RBPP_ApplyColorCorrectPass( void );

/*
=============
RBPP_LoadProcs

Load the rectangle-texture, framebuffer, and shader-object entry points used by the retail post-process pipeline.
=============
*/
static qboolean RBPP_LoadProcs( void ) {
	if ( s_postProcess.procsLoaded ) {
		return s_postProcess.supported;
	}

	Com_Memset( &s_postProcess.procs, 0, sizeof( s_postProcess.procs ) );
	s_postProcess.procsLoaded = qtrue;
	s_postProcess.supported = qfalse;

	if ( !glConfig.extensions_string ) {
		return qfalse;
	}

	if ( !strstr( glConfig.extensions_string, "GL_EXT_framebuffer_object" ) ) {
		return qfalse;
	}

	if ( !strstr( glConfig.extensions_string, "GL_ARB_texture_rectangle" ) ) {
		return qfalse;
	}

	if ( !strstr( glConfig.extensions_string, "GL_ARB_shader_objects" ) ||
		!strstr( glConfig.extensions_string, "GL_ARB_vertex_shader" ) ||
		!strstr( glConfig.extensions_string, "GL_ARB_fragment_shader" ) ) {
		return qfalse;
	}

	s_postProcess.procs.qglGenFramebuffersEXTFunc = (PFNGLGENFRAMEBUFFERSEXTPROC)RB_GetFramebufferProc( "glGenFramebuffersEXT" );
	s_postProcess.procs.qglDeleteFramebuffersEXTFunc = (PFNGLDELETEFRAMEBUFFERSEXTPROC)RB_GetFramebufferProc( "glDeleteFramebuffersEXT" );
	s_postProcess.procs.qglBindFramebufferEXTFunc = (PFNGLBINDFRAMEBUFFEREXTPROC)RB_GetFramebufferProc( "glBindFramebufferEXT" );
	s_postProcess.procs.qglFramebufferTexture2DEXTFunc = (PFNGLFRAMEBUFFERTEXTURE2DEXTPROC)RB_GetFramebufferProc( "glFramebufferTexture2DEXT" );
	s_postProcess.procs.qglCheckFramebufferStatusEXTFunc = (PFNGLCHECKFRAMEBUFFERSTATUSEXTPROC)RB_GetFramebufferProc( "glCheckFramebufferStatusEXT" );
	s_postProcess.procs.qglGenRenderbuffersEXTFunc = (PFNGLGENRENDERBUFFERSEXTPROC)RB_GetFramebufferProc( "glGenRenderbuffersEXT" );
	s_postProcess.procs.qglBindRenderbufferEXTFunc = (PFNGLBINDRENDERBUFFEREXTPROC)RB_GetFramebufferProc( "glBindRenderbufferEXT" );
	s_postProcess.procs.qglRenderbufferStorageEXTFunc = (PFNGLRENDERBUFFERSTORAGEEXTPROC)RB_GetFramebufferProc( "glRenderbufferStorageEXT" );
	s_postProcess.procs.qglFramebufferRenderbufferEXTFunc = (PFNGLFRAMEBUFFERRENDERBUFFEREXTPROC)RB_GetFramebufferProc( "glFramebufferRenderbufferEXT" );
	s_postProcess.procs.qglDeleteRenderbuffersEXTFunc = (PFNGLDELETERENDERBUFFERSEXTPROC)RB_GetFramebufferProc( "glDeleteRenderbuffersEXT" );
	s_postProcess.procs.qglCreateShaderObjectARBFunc = (PFNGLCREATESHADEROBJECTARBPROC)RB_GetFramebufferProc( "glCreateShaderObjectARB" );
	s_postProcess.procs.qglShaderSourceARBFunc = (PFNGLSHADERSOURCEARBPROC)RB_GetFramebufferProc( "glShaderSourceARB" );
	s_postProcess.procs.qglCompileShaderARBFunc = (PFNGLCOMPILESHADERARBPROC)RB_GetFramebufferProc( "glCompileShaderARB" );
	s_postProcess.procs.qglGetObjectParameterivARBFunc = (PFNGLGETOBJECTPARAMETERIVARBPROC)RB_GetFramebufferProc( "glGetObjectParameterivARB" );
	s_postProcess.procs.qglGetInfoLogARBFunc = (PFNGLGETINFOLOGARBPROC)RB_GetFramebufferProc( "glGetInfoLogARB" );
	s_postProcess.procs.qglDeleteObjectARBFunc = (PFNGLDELETEOBJECTARBPROC)RB_GetFramebufferProc( "glDeleteObjectARB" );
	s_postProcess.procs.qglCreateProgramObjectARBFunc = (PFNGLCREATEPROGRAMOBJECTARBPROC)RB_GetFramebufferProc( "glCreateProgramObjectARB" );
	s_postProcess.procs.qglAttachObjectARBFunc = (PFNGLATTACHOBJECTARBPROC)RB_GetFramebufferProc( "glAttachObjectARB" );
	s_postProcess.procs.qglLinkProgramARBFunc = (PFNGLLINKPROGRAMARBPROC)RB_GetFramebufferProc( "glLinkProgramARB" );
	s_postProcess.procs.qglUseProgramObjectARBFunc = (PFNGLUSEPROGRAMOBJECTARBPROC)RB_GetFramebufferProc( "glUseProgramObjectARB" );
	s_postProcess.procs.qglGetUniformLocationARBFunc = (PFNGLGETUNIFORMLOCATIONARBPROC)RB_GetFramebufferProc( "glGetUniformLocationARB" );
	s_postProcess.procs.qglUniform1iARBFunc = (PFNGLUNIFORM1IARBPROC)RB_GetFramebufferProc( "glUniform1iARB" );
	s_postProcess.procs.qglUniform1fARBFunc = (PFNGLUNIFORM1FARBPROC)RB_GetFramebufferProc( "glUniform1fARB" );

	if ( !s_postProcess.procs.qglGenFramebuffersEXTFunc || !s_postProcess.procs.qglDeleteFramebuffersEXTFunc ||
		!s_postProcess.procs.qglBindFramebufferEXTFunc || !s_postProcess.procs.qglFramebufferTexture2DEXTFunc ||
		!s_postProcess.procs.qglCheckFramebufferStatusEXTFunc || !s_postProcess.procs.qglGenRenderbuffersEXTFunc ||
		!s_postProcess.procs.qglBindRenderbufferEXTFunc || !s_postProcess.procs.qglRenderbufferStorageEXTFunc ||
		!s_postProcess.procs.qglFramebufferRenderbufferEXTFunc || !s_postProcess.procs.qglDeleteRenderbuffersEXTFunc ||
		!s_postProcess.procs.qglCreateShaderObjectARBFunc || !s_postProcess.procs.qglShaderSourceARBFunc ||
		!s_postProcess.procs.qglCompileShaderARBFunc || !s_postProcess.procs.qglGetObjectParameterivARBFunc ||
		!s_postProcess.procs.qglGetInfoLogARBFunc || !s_postProcess.procs.qglDeleteObjectARBFunc ||
		!s_postProcess.procs.qglCreateProgramObjectARBFunc || !s_postProcess.procs.qglAttachObjectARBFunc ||
		!s_postProcess.procs.qglLinkProgramARBFunc || !s_postProcess.procs.qglUseProgramObjectARBFunc ||
		!s_postProcess.procs.qglGetUniformLocationARBFunc || !s_postProcess.procs.qglUniform1iARBFunc ||
		!s_postProcess.procs.qglUniform1fARBFunc ) {
		return qfalse;
	}

	qglGetIntegerv( GL_MAX_RECTANGLE_TEXTURE_SIZE_ARB, &s_postProcess.maxRectangleTextureSize );
	if ( s_postProcess.maxRectangleTextureSize <= 0 ) {
		return qfalse;
	}

	s_postProcess.supported = qtrue;
	return qtrue;
}


/*
=============
RBPP_DestroyRenderTarget

Release one rectangle-texture render target and any attached depth-stencil storage.
=============
*/
static void RBPP_DestroyRenderTarget( ppRenderTarget_t *target ) {
	if ( !target ) {
		return;
	}

	if ( target->framebuffer && s_postProcess.procs.qglDeleteFramebuffersEXTFunc ) {
		s_postProcess.procs.qglDeleteFramebuffersEXTFunc( 1, &target->framebuffer );
	}

	if ( target->depthBuffer && s_postProcess.procs.qglDeleteRenderbuffersEXTFunc ) {
		s_postProcess.procs.qglDeleteRenderbuffersEXTFunc( 1, &target->depthBuffer );
	}

	if ( target->texture ) {
		qglDeleteTextures( 1, &target->texture );
	}

	Com_Memset( target, 0, sizeof( *target ) );
}


/*
=============
RBPP_CreateRenderTarget

Allocate one retail-style rectangle-texture render target with depth-stencil storage.
=============
*/
static qboolean RBPP_CreateRenderTarget( ppRenderTarget_t *target, int width, int height, qboolean linearFilter ) {
	GLenum status;
	GLenum errorCode;
	GLint internalFormat;
	GLenum pixelType;

	if ( !target || width <= 0 || height <= 0 || !RBPP_LoadProcs() ) {
		return qfalse;
	}

	if ( width > s_postProcess.maxRectangleTextureSize || height > s_postProcess.maxRectangleTextureSize ) {
		return qfalse;
	}

	RBPP_DestroyRenderTarget( target );
	target->width = width;
	target->height = height;

	internalFormat = GL_RGBA8;
	pixelType = GL_UNSIGNED_BYTE;
	if ( r_floatingPointFBOs && r_floatingPointFBOs->integer ) {
		internalFormat = GL_RGBA16;
		pixelType = GL_FLOAT;
	}

	s_postProcess.procs.qglGenFramebuffersEXTFunc( 1, &target->framebuffer );
	s_postProcess.procs.qglGenRenderbuffersEXTFunc( 1, &target->depthBuffer );
	qglGenTextures( 1, &target->texture );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, target->texture );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MIN_FILTER, linearFilter ? GL_LINEAR : GL_NEAREST );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MAG_FILTER, linearFilter ? GL_LINEAR : GL_NEAREST );
	qglTexImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, internalFormat, width, height, 0, GL_RGBA, pixelType, NULL );

	errorCode = qglGetError();
	if ( errorCode != GL_NO_ERROR ) {
		RBPP_DestroyRenderTarget( target );
		return qfalse;
	}

	s_postProcess.procs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, target->framebuffer );
	s_postProcess.procs.qglFramebufferTexture2DEXTFunc( GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_RECTANGLE_ARB, target->texture, 0 );
	s_postProcess.procs.qglBindRenderbufferEXTFunc( GL_RENDERBUFFER_EXT, target->depthBuffer );
	s_postProcess.procs.qglRenderbufferStorageEXTFunc( GL_RENDERBUFFER_EXT, GL_DEPTH24_STENCIL8_EXT, width, height );
	s_postProcess.procs.qglFramebufferRenderbufferEXTFunc( GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, target->depthBuffer );
	s_postProcess.procs.qglFramebufferRenderbufferEXTFunc( GL_FRAMEBUFFER_EXT, GL_STENCIL_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, target->depthBuffer );

	status = s_postProcess.procs.qglCheckFramebufferStatusEXTFunc( GL_FRAMEBUFFER_EXT );
	s_postProcess.procs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, 0 );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );

	if ( status != GL_FRAMEBUFFER_COMPLETE_EXT ) {
		ri.Printf( PRINT_WARNING, "Post Process Failure - unable to create FBO : %d (%x)\n", status, status );
		RBPP_DestroyRenderTarget( target );
		return qfalse;
	}

	errorCode = qglGetError();
	if ( errorCode != GL_NO_ERROR ) {
		RBPP_DestroyRenderTarget( target );
		return qfalse;
	}

	target->initialized = qtrue;
	return qtrue;
}


/*
=============
RBPP_BindRenderTarget

Bind one post-process framebuffer for the next rectangle-texture draw.
=============
*/
static void RBPP_BindRenderTarget( ppRenderTarget_t *target ) {
	if ( !target || !target->initialized || !s_postProcess.procs.qglBindFramebufferEXTFunc ) {
		return;
	}

	s_postProcess.procs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, target->framebuffer );
}


/*
=============
RBPP_Set2DState

Set the 2D state block used by the shader-backed rectangle-texture passes.
=============
*/
static void RBPP_Set2DState( int width, int height ) {
	backEnd.projection2D = qtrue;

	qglViewport( 0, 0, width, height );
	qglScissor( 0, 0, width, height );
	qglMatrixMode( GL_PROJECTION );
	qglLoadIdentity();
	qglOrtho( 0, width, height, 0, 0, 1 );
	qglMatrixMode( GL_MODELVIEW );
	qglLoadIdentity();

	GL_State( GLS_DEPTHTEST_DISABLE |
		GLS_SRCBLEND_SRC_ALPHA |
		GLS_DSTBLEND_ONE_MINUS_SRC_ALPHA );

	qglDisable( GL_CULL_FACE );
	qglDisable( GL_CLIP_PLANE0 );
	qglDisable( GL_SCISSOR_TEST );

	qglColor4f( 1.0f, 1.0f, 1.0f, 1.0f );
	qglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE );

	backEnd.refdef.time = ri.Milliseconds();
	backEnd.refdef.floatTime = backEnd.refdef.time * 0.001f;
}


/*
=============
RBPP_BindRectangleTexture

Bind one rectangle-texture source on the requested multitexture unit.
=============
*/
static void RBPP_BindRectangleTexture( int unit, GLuint texture ) {
	if ( qglActiveTextureARB ) {
		qglActiveTextureARB( GL_TEXTURE0_ARB + unit );
	}

	qglDisable( GL_TEXTURE_2D );
	qglEnable( GL_TEXTURE_RECTANGLE_ARB );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, texture );
}


/*
=============
RBPP_DrawQuad

Draw a fullscreen quad with explicit rectangle-texture coordinates for both multitexture units.
=============
*/
static void RBPP_DrawQuad( int width, int height, float s0Max, float t0Max, float s1Max, float t1Max ) {
	qglBegin( GL_QUADS );

	if ( qglMultiTexCoord2fARB ) {
		qglMultiTexCoord2fARB( GL_TEXTURE0_ARB, 0.0f, 0.0f );
		qglMultiTexCoord2fARB( GL_TEXTURE1_ARB, 0.0f, 0.0f );
	}
	qglTexCoord2f( 0.0f, 0.0f );
	qglVertex2f( 0.0f, 0.0f );

	if ( qglMultiTexCoord2fARB ) {
		qglMultiTexCoord2fARB( GL_TEXTURE0_ARB, s0Max, 0.0f );
		qglMultiTexCoord2fARB( GL_TEXTURE1_ARB, s1Max, 0.0f );
	}
	qglTexCoord2f( s0Max, 0.0f );
	qglVertex2f( width, 0.0f );

	if ( qglMultiTexCoord2fARB ) {
		qglMultiTexCoord2fARB( GL_TEXTURE0_ARB, s0Max, t0Max );
		qglMultiTexCoord2fARB( GL_TEXTURE1_ARB, s1Max, t1Max );
	}
	qglTexCoord2f( s0Max, t0Max );
	qglVertex2f( width, height );

	if ( qglMultiTexCoord2fARB ) {
		qglMultiTexCoord2fARB( GL_TEXTURE0_ARB, 0.0f, t0Max );
		qglMultiTexCoord2fARB( GL_TEXTURE1_ARB, 0.0f, t1Max );
	}
	qglTexCoord2f( 0.0f, t0Max );
	qglVertex2f( 0.0f, height );

	qglEnd();
}


/*
=============
RBPP_GetShaderSource

Return the embedded GLSL source that corresponds to the recovered retail script path.
=============
*/
static const GLcharARB *RBPP_GetShaderSource( const char *sourcePath ) {
	if ( !sourcePath ) {
		return NULL;
	}

	if ( !Q_stricmp( sourcePath, "scripts/posteffect.vs" ) ) {
		return s_postEffectVertexShaderSource;
	}

	if ( !Q_stricmp( sourcePath, "scripts/brightpass.fs" ) ) {
		return s_brightPassFragmentShaderSource;
	}

	if ( !Q_stricmp( sourcePath, "scripts/downsample1.fs" ) ) {
		return s_downsampleFragmentShaderSource;
	}

	if ( !Q_stricmp( sourcePath, "scripts/blurvertical.fs" ) ) {
		return s_blurVerticalFragmentShaderSource;
	}

	if ( !Q_stricmp( sourcePath, "scripts/blurhoriz.fs" ) ) {
		return s_blurHorizontalFragmentShaderSource;
	}

	if ( !Q_stricmp( sourcePath, "scripts/combine.fs" ) ) {
		return s_combineFragmentShaderSource;
	}

	if ( !Q_stricmp( sourcePath, "scripts/colorcorrect.fs" ) ) {
		return s_colorCorrectFragmentShaderSource;
	}

	return NULL;
}


/*
=============
RBPP_PrintInfoLog

Emit the GL info log for one shader or program object.
=============
*/
static void RBPP_PrintInfoLog( GLhandleARB objectHandle ) {
	GLint logLength;
	GLsizei actualLength;
	char *logBuffer;

	if ( !objectHandle ) {
		return;
	}

	logLength = 0;
	s_postProcess.procs.qglGetObjectParameterivARBFunc( objectHandle, GL_OBJECT_INFO_LOG_LENGTH_ARB, &logLength );
	if ( logLength <= 1 ) {
		return;
	}

	logBuffer = ri.Hunk_AllocateTempMemory( logLength );
	if ( !logBuffer ) {
		return;
	}

	actualLength = 0;
	s_postProcess.procs.qglGetInfoLogARBFunc( objectHandle, logLength, &actualLength, logBuffer );
	if ( actualLength > 0 ) {
		ri.Printf( PRINT_WARNING, "%s", logBuffer );
	}

	ri.Hunk_FreeTempMemory( logBuffer );
}


/*
=============
RBPP_CompileShader

Compile one embedded post-process shader and emit the recovered retail failure strings on error.
=============
*/
static qboolean RBPP_CompileShader( GLenum shaderType, const char *sourcePath, GLhandleARB *shaderObject ) {
	const GLcharARB *shaderSource;
	GLint compileStatus;

	if ( shaderObject ) {
		*shaderObject = 0;
	}

	shaderSource = RBPP_GetShaderSource( sourcePath );
	if ( !shaderSource ) {
		if ( shaderType == GL_FRAGMENT_SHADER_ARB ) {
			ri.Printf( PRINT_WARNING, "Unable to load post effect fragment shader source: %s\n", sourcePath );
		} else {
			ri.Printf( PRINT_WARNING, "Unable to load post effect vertex shader source: %s\n", sourcePath );
		}
		return qfalse;
	}

	if ( !shaderObject ) {
		return qfalse;
	}

	*shaderObject = s_postProcess.procs.qglCreateShaderObjectARBFunc( shaderType );
	s_postProcess.procs.qglShaderSourceARBFunc( *shaderObject, 1, &shaderSource, NULL );
	s_postProcess.procs.qglCompileShaderARBFunc( *shaderObject );

	compileStatus = 0;
	s_postProcess.procs.qglGetObjectParameterivARBFunc( *shaderObject, GL_OBJECT_COMPILE_STATUS_ARB, &compileStatus );
	if ( !compileStatus ) {
		if ( shaderType == GL_FRAGMENT_SHADER_ARB ) {
			ri.Printf( PRINT_WARNING, "Compilation of post effect fragment shader (%s) failed. Shader log follows:\n\n", sourcePath );
		} else {
			ri.Printf( PRINT_WARNING, "Compilation of post effect vertex shader (%s) failed. Shader log follows:\n\n", sourcePath );
		}
		RBPP_PrintInfoLog( *shaderObject );
		ri.Printf( PRINT_WARNING, "\nPost effects disabled.\n" );
		s_postProcess.procs.qglDeleteObjectARBFunc( *shaderObject );
		*shaderObject = 0;
		return qfalse;
	}

	return qtrue;
}


/*
=============
RBPP_DestroyProgram

Release the fragment shader, vertex shader, and linked program backing one post effect.
=============
*/
static void RBPP_DestroyProgram( ppProgram_t *program ) {
	if ( !program ) {
		return;
	}

	if ( program->programObject && s_postProcess.procs.qglDeleteObjectARBFunc ) {
		s_postProcess.procs.qglDeleteObjectARBFunc( program->programObject );
	}

	if ( program->fragmentObject && s_postProcess.procs.qglDeleteObjectARBFunc ) {
		s_postProcess.procs.qglDeleteObjectARBFunc( program->fragmentObject );
	}

	if ( program->vertexObject && s_postProcess.procs.qglDeleteObjectARBFunc ) {
		s_postProcess.procs.qglDeleteObjectARBFunc( program->vertexObject );
	}

	Com_Memset( program, 0, sizeof( *program ) );
}


/*
=============
RBPP_LoadProgram

Compile and link one recovered retail post effect program pair.
=============
*/
static qboolean RBPP_LoadProgram( ppProgram_t *program, const char *name, const char *fragmentPath, const char *vertexPath ) {
	GLint linkStatus;

	if ( !program || !RBPP_LoadProcs() ) {
		return qfalse;
	}

	Com_Memset( program, 0, sizeof( *program ) );
	program->name = name;
	program->fragmentPath = fragmentPath;
	program->vertexPath = vertexPath;
	program->backBufferTexUniform = -1;
	program->bloomTexUniform = -1;
	program->brightThresholdUniform = -1;
	program->bloomSaturationUniform = -1;
	program->bloomIntensityUniform = -1;
	program->sceneIntensityUniform = -1;
	program->sceneSaturationUniform = -1;
	program->gammaRecipUniform = -1;
	program->overbrightUniform = -1;
	program->contrastUniform = -1;
	program->blurStepUniform = -1;
	program->blurFalloffUniform = -1;

	if ( !RBPP_CompileShader( GL_FRAGMENT_SHADER_ARB, fragmentPath, &program->fragmentObject ) ||
		!RBPP_CompileShader( GL_VERTEX_SHADER_ARB, vertexPath, &program->vertexObject ) ) {
		RBPP_DestroyProgram( program );
		return qfalse;
	}

	program->programObject = s_postProcess.procs.qglCreateProgramObjectARBFunc();
	s_postProcess.procs.qglAttachObjectARBFunc( program->programObject, program->fragmentObject );
	s_postProcess.procs.qglAttachObjectARBFunc( program->programObject, program->vertexObject );
	s_postProcess.procs.qglLinkProgramARBFunc( program->programObject );

	linkStatus = 0;
	s_postProcess.procs.qglGetObjectParameterivARBFunc( program->programObject, GL_OBJECT_LINK_STATUS_ARB, &linkStatus );
	if ( !linkStatus ) {
		RBPP_PrintInfoLog( program->programObject );
		ri.Printf( PRINT_WARNING, "\nPost effects disabled.\n" );
		RBPP_DestroyProgram( program );
		return qfalse;
	}

	s_postProcess.procs.qglUseProgramObjectARBFunc( program->programObject );
	program->backBufferTexUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "backBufferTex" );
	program->bloomTexUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "bloomTex" );
	program->brightThresholdUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_brightthreshold" );
	program->bloomSaturationUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_bloomsaturation" );
	program->bloomIntensityUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_bloomintensity" );
	program->sceneIntensityUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_sceneintensity" );
	program->sceneSaturationUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_scenesaturation" );
	program->gammaRecipUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_gammaRecip" );
	program->overbrightUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_overbright" );
	program->contrastUniform = s_postProcess.procs.qglGetUniformLocationARBFunc( program->programObject, "p_contrast" );

	if ( program->backBufferTexUniform >= 0 ) {
		s_postProcess.procs.qglUniform1iARBFunc( program->backBufferTexUniform, 0 );
	}

	if ( program->bloomTexUniform >= 0 ) {
		s_postProcess.procs.qglUniform1iARBFunc( program->bloomTexUniform, 1 );
	}

	s_postProcess.procs.qglUseProgramObjectARBFunc( 0 );
	return qtrue;
}


/*
=============
RBPP_LoadBloomPrograms

Compile the recovered bloom program family.
=============
*/
static qboolean RBPP_LoadBloomPrograms( void ) {
	if ( !RBPP_LoadProgram( &s_postProcess.brightPassProgram, "brightpass", "scripts/brightpass.fs", "scripts/posteffect.vs" ) ) {
		return qfalse;
	}

	if ( !RBPP_LoadProgram( &s_postProcess.downsampleProgram, "downsample", "scripts/downsample1.fs", "scripts/posteffect.vs" ) ) {
		return qfalse;
	}

	if ( !RBPP_LoadProgram( &s_postProcess.blurVerticalProgram, "blurvertical", "scripts/blurvertical.fs", "scripts/posteffect.vs" ) ) {
		return qfalse;
	}

	if ( !RBPP_LoadProgram( &s_postProcess.blurHorizontalProgram, "blurhoriz", "scripts/blurhoriz.fs", "scripts/posteffect.vs" ) ) {
		return qfalse;
	}

	if ( !RBPP_LoadProgram( &s_postProcess.combineProgram, "combine", "scripts/combine.fs", "scripts/posteffect.vs" ) ) {
		return qfalse;
	}

	return qtrue;
}


/*
=============
RBPP_DestroyBloomPrograms

Release every bloom shader program.
=============
*/
static void RBPP_DestroyBloomPrograms( void ) {
	RBPP_DestroyProgram( &s_postProcess.combineProgram );
	RBPP_DestroyProgram( &s_postProcess.blurHorizontalProgram );
	RBPP_DestroyProgram( &s_postProcess.blurVerticalProgram );
	RBPP_DestroyProgram( &s_postProcess.downsampleProgram );
	RBPP_DestroyProgram( &s_postProcess.brightPassProgram );
}


/*
=============
RBPP_LoadColorCorrectProgram

Compile the recovered retail color-correct program pair.
=============
*/
static qboolean RBPP_LoadColorCorrectProgram( void ) {
	return RBPP_LoadProgram( &s_postProcess.colorCorrectProgram, "colorCorrect", "scripts/colorcorrect.fs", "scripts/posteffect.vs" );
}


/*
=============
RBPP_DestroyColorCorrectProgram

Release the linked retail color-correct program.
=============
*/
static void RBPP_DestroyColorCorrectProgram( void ) {
	RBPP_DestroyProgram( &s_postProcess.colorCorrectProgram );
}


/*
=============
RBPP_CreateColorCorrectTexture

Allocate the retail color-correct rectangle texture that caches the final backbuffer copy.
=============
*/
static qboolean RBPP_CreateColorCorrectTexture( void ) {
	GLenum errorCode;
	int width;
	int height;

	RBPP_DestroyColorCorrectTexture();

	if ( !RBPP_LoadProcs() ) {
		return qfalse;
	}

	width = glConfig.vidWidth;
	height = glConfig.vidHeight;
	if ( width > s_postProcess.maxRectangleTextureSize || height > s_postProcess.maxRectangleTextureSize ) {
		ri.Printf( PRINT_WARNING, "Color Correct Failure - unable to create backbuffer texture. Color Correct effect disabled\n" );
		return qfalse;
	}

	qglGenTextures( 1, &s_postProcess.colorCorrectTexture );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, s_postProcess.colorCorrectTexture );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MIN_FILTER, GL_NEAREST );
	qglTexParameteri( GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MAG_FILTER, GL_NEAREST );
	qglTexImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );

	errorCode = qglGetError();
	if ( errorCode != GL_NO_ERROR ) {
		ri.Printf( PRINT_WARNING, "Color Correct Failure - unable to create backbuffer texture. Color Correct effect disabled\n" );
		RBPP_DestroyColorCorrectTexture();
		return qfalse;
	}

	s_postProcess.colorCorrectWidth = width;
	s_postProcess.colorCorrectHeight = height;
	return qtrue;
}


/*
=============
RBPP_DestroyColorCorrectTexture

Release the cached color-correct rectangle texture.
=============
*/
static void RBPP_DestroyColorCorrectTexture( void ) {
	if ( s_postProcess.colorCorrectTexture ) {
		qglDeleteTextures( 1, &s_postProcess.colorCorrectTexture );
	}

	s_postProcess.colorCorrectTexture = 0;
	s_postProcess.colorCorrectWidth = 0;
	s_postProcess.colorCorrectHeight = 0;
}


/*
=============
RBPP_GetBloomMode

Retail Quake Live treats r_enableBloom as a mode selector:
0 disables bloom, 1 keeps the half-resolution chain, and 2 enables the
additional quarter-resolution stage.
=============
*/
static int RBPP_GetBloomMode( void ) {
	if ( !r_enableBloom || r_enableBloom->integer <= 0 ) {
		return 0;
	}

	if ( r_enableBloom->integer == 1 ) {
		return 1;
	}

	return 2;
}

/*
=============
RBPP_InitBloomResources

Allocate the retail bloom render-target chain and compile the recovered bloom programs.
=============
*/
static qboolean RBPP_InitBloomResources( void ) {
	int bloomMode;
	int width;
	int height;
	int halfWidth;
	int halfHeight;
	int quarterWidth;
	int quarterHeight;

	bloomMode = RBPP_GetBloomMode();
	if ( bloomMode <= 0 ) {
		return qfalse;
	}

	width = glConfig.vidWidth;
	height = glConfig.vidHeight;
	if ( width > s_postProcess.maxRectangleTextureSize || height > s_postProcess.maxRectangleTextureSize ) {
		ri.Printf( PRINT_WARNING, "Bloom Failure - unable to create backbuffer texture. Bloom effect disabled\n" );
		return qfalse;
	}

	halfWidth = width >> 1;
	halfHeight = height >> 1;
	if ( halfWidth < 1 ) {
		halfWidth = 1;
	}

	if ( halfHeight < 1 ) {
		halfHeight = 1;
	}

	quarterWidth = width >> 2;
	quarterHeight = height >> 2;
	if ( quarterWidth < 1 ) {
		quarterWidth = 1;
	}

	if ( quarterHeight < 1 ) {
		quarterHeight = 1;
	}

	if ( !RBPP_CreateRenderTarget( &s_postProcess.bloomDownsampleTarget, halfWidth, halfHeight, qtrue ) ||
		!RBPP_CreateRenderTarget( &s_postProcess.bloomBrightTarget, halfWidth, halfHeight, qtrue ) ||
		!RBPP_CreateRenderTarget( &s_postProcess.bloomBlurVerticalTarget, halfWidth, halfHeight, qtrue ) ||
		!RBPP_CreateRenderTarget( &s_postProcess.bloomBlurHorizontalTarget, halfWidth, halfHeight, qtrue ) ) {
		ri.Printf( PRINT_WARNING, "Bloom Failure - unable to create FBO. Bloom effect disabled\n" );
		RBPP_ShutdownBloomResources();
		return qfalse;
	}

	if ( bloomMode == 2 &&
		( !RBPP_CreateRenderTarget( &s_postProcess.bloomQuarterDownsampleTarget, quarterWidth, quarterHeight, qtrue ) ||
		!RBPP_CreateRenderTarget( &s_postProcess.bloomQuarterVerticalTarget, quarterWidth, quarterHeight, qtrue ) ||
		!RBPP_CreateRenderTarget( &s_postProcess.bloomQuarterHorizontalTarget, quarterWidth, quarterHeight, qtrue ) ) ) {
		ri.Printf( PRINT_WARNING, "Bloom Failure - unable to create FBO. Bloom effect disabled\n" );
		RBPP_ShutdownBloomResources();
		return qfalse;
	}

	if ( !RBPP_LoadBloomPrograms() ) {
		RBPP_ShutdownBloomResources();
		return qfalse;
	}

	return qtrue;
}


/*
=============
RBPP_ShutdownBloomResources

Release the bloom targets and shader programs.
=============
*/
static void RBPP_ShutdownBloomResources( void ) {
	RBPP_DestroyBloomPrograms();
	RBPP_DestroyRenderTarget( &s_postProcess.bloomQuarterHorizontalTarget );
	RBPP_DestroyRenderTarget( &s_postProcess.bloomQuarterVerticalTarget );
	RBPP_DestroyRenderTarget( &s_postProcess.bloomQuarterDownsampleTarget );
	RBPP_DestroyRenderTarget( &s_postProcess.bloomBlurHorizontalTarget );
	RBPP_DestroyRenderTarget( &s_postProcess.bloomBlurVerticalTarget );
	RBPP_DestroyRenderTarget( &s_postProcess.bloomBrightTarget );
	RBPP_DestroyRenderTarget( &s_postProcess.bloomDownsampleTarget );
}


/*
=============
RBPP_InitColorCorrectResources

Allocate the retail color-correct texture and load its shader program.
=============
*/
static qboolean RBPP_InitColorCorrectResources( void ) {
	if ( !RBPP_LoadColorCorrectProgram() ) {
		RBPP_ShutdownColorCorrectResources();
		return qfalse;
	}

	if ( !RBPP_CreateColorCorrectTexture() ) {
		RBPP_ShutdownColorCorrectResources();
		return qfalse;
	}

	return qtrue;
}


/*
=============
RBPP_ShutdownColorCorrectResources

Release the retail color-correct texture and linked shader program.
=============
*/
static void RBPP_ShutdownColorCorrectResources( void ) {
	RBPP_DestroyColorCorrectTexture();
	RBPP_DestroyColorCorrectProgram();
}


/*
=============
RBPP_MirrorState

Publish the backend-validated post-process active flags back to the renderer globals and ROM mirrors.
=============
*/
static void RBPP_MirrorState( void ) {
	tr.postProcessActive = backEnd.postProcessActive;
	tr.bloomActive = backEnd.bloomActive;
	tr.colorCorrectActive = backEnd.colorCorrectActive;

	if ( r_postProcessActive ) {
		ri.Cvar_Set( "r_postProcessActive", backEnd.postProcessActive ? "1" : "0" );
	}

	if ( r_bloomActive ) {
		ri.Cvar_Set( "r_bloomActive", backEnd.bloomActive ? "1" : "0" );
	}

	if ( r_colorCorrectActive ) {
		ri.Cvar_Set( "r_colorCorrectActive", backEnd.colorCorrectActive ? "1" : "0" );
	}
}


/*
=============
RBPP_RebuildState

Evaluate the post-process enable cvars, rebuild the retail resource/program set, and update the active mirrors.
=============
*/
static void RBPP_RebuildState( void ) {
	qboolean wantPostProcess;
	qboolean wantBloom;
	qboolean wantColorCorrect;

	RBPP_ShutdownColorCorrectResources();
	RBPP_ShutdownBloomResources();
	RBPP_DestroyRenderTarget( &s_postProcess.sceneTarget );

	backEnd.postProcessActive = qfalse;
	backEnd.bloomActive = qfalse;
	backEnd.colorCorrectActive = qfalse;

	wantPostProcess = (qboolean)(r_enablePostProcess && r_enablePostProcess->integer);
	wantBloom = (qboolean)(wantPostProcess && r_enableBloom && r_enableBloom->integer);
	wantColorCorrect = (qboolean)(wantPostProcess && r_enableColorCorrect && r_enableColorCorrect->integer);

	if ( !wantPostProcess ) {
		RBPP_MirrorState();
		return;
	}

	if ( !qglActiveTextureARB || !qglMultiTexCoord2fARB ) {
		ri.Printf( PRINT_WARNING, "GL_ARB_Multitexture is either not supported, or is disabled by r_ext_multiTexture. Post processing is disabled.\n" );
		RBPP_MirrorState();
		return;
	}

	if ( !RBPP_LoadProcs() ) {
		RBPP_MirrorState();
		return;
	}

	if ( !RBPP_CreateRenderTarget( &s_postProcess.sceneTarget, glConfig.vidWidth, glConfig.vidHeight, qfalse ) ) {
		RBPP_MirrorState();
		return;
	}

	backEnd.postProcessActive = qtrue;

	if ( wantBloom ) {
		backEnd.bloomActive = RBPP_InitBloomResources();
	}

	if ( wantColorCorrect ) {
		backEnd.colorCorrectActive = RBPP_InitColorCorrectResources();
	}

	RBPP_MirrorState();
}


/*
=============
RBPP_Init

Initialize the shared retail post-process state at renderer startup.
=============
*/
static void RBPP_Init( void ) {
	Com_Memset( &s_postProcess, 0, sizeof( s_postProcess ) );
	RBPP_RebuildState();
	backEnd.postProcessNeedsReset = qfalse;
}


/*
=============
RBPP_Shutdown

Release the full post-process resource set.
=============
*/
static void RBPP_Shutdown( void ) {
	RBPP_ShutdownColorCorrectResources();
	RBPP_ShutdownBloomResources();
	RBPP_DestroyRenderTarget( &s_postProcess.sceneTarget );
	backEnd.postProcessActive = qfalse;
	backEnd.bloomActive = qfalse;
	backEnd.colorCorrectActive = qfalse;
	backEnd.postProcessNeedsReset = qfalse;
	RBPP_MirrorState();
}


/*
=============
RBPP_BindSceneRenderTarget

Route scene rendering into the rectangle-texture scene target whenever post-processing is active.
=============
*/
static void RBPP_BindSceneRenderTarget( void ) {
	if ( !RB_PostProcessEnabled() || !s_postProcess.sceneTarget.initialized ) {
		RBPP_ReleaseSceneRenderTarget();
		return;
	}

	RBPP_BindRenderTarget( &s_postProcess.sceneTarget );
}


/*
=============
RBPP_ReleaseSceneRenderTarget

Restore rendering to the default framebuffer.
=============
*/
static void RBPP_ReleaseSceneRenderTarget( void ) {
	if ( s_postProcess.procs.qglBindFramebufferEXTFunc ) {
		s_postProcess.procs.qglBindFramebufferEXTFunc( GL_FRAMEBUFFER_EXT, 0 );
	}
}


/*
=============
RB_BeginScreenshotReadback

Restore the default framebuffer before screenshot readback, matching the
retail screenshot helpers' release of the post-process scene target.
=============
*/
void RB_BeginScreenshotReadback( void ) {
	if ( !RB_PostProcessEnabled() || !s_postProcess.sceneTarget.initialized ) {
		return;
	}

	RBPP_ReleaseSceneRenderTarget();
}


/*
=============
RB_EndScreenshotReadback

Rebind the scene target after screenshot readback when the frame is still being
rendered through the post-process path.
=============
*/
void RB_EndScreenshotReadback( void ) {
	if ( !RB_PostProcessEnabled() || !s_postProcess.sceneTarget.initialized ) {
		return;
	}

	RBPP_BindSceneRenderTarget();
}


/*
=============
RBPP_ResetIfNeeded

Apply any queued post-process restart request after the current frame has been presented.
=============
*/
static void RBPP_ResetIfNeeded( void ) {
	if ( !backEnd.postProcessNeedsReset ) {
		return;
	}

	RBPP_RebuildState();
	backEnd.postProcessNeedsReset = qfalse;
	tr.postProcessNeedsReset = qfalse;
}


/*
=============
RBPP_BlitSceneTarget

Present the scene rectangle texture directly to the default framebuffer.
=============
*/
static void RBPP_BlitSceneTarget( void ) {
	if ( !s_postProcess.sceneTarget.initialized ) {
		return;
	}

	RBPP_Set2DState( glConfig.vidWidth, glConfig.vidHeight );
	s_postProcess.procs.qglUseProgramObjectARBFunc( 0 );
	RBPP_BindRectangleTexture( 0, s_postProcess.sceneTarget.texture );
	RBPP_DrawQuad( glConfig.vidWidth, glConfig.vidHeight, (float)s_postProcess.sceneTarget.width, (float)s_postProcess.sceneTarget.height, (float)s_postProcess.sceneTarget.width, (float)s_postProcess.sceneTarget.height );

	if ( qglActiveTextureARB ) {
		qglActiveTextureARB( GL_TEXTURE1_ARB );
		qglDisable( GL_TEXTURE_RECTANGLE_ARB );
		qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );
		qglActiveTextureARB( GL_TEXTURE0_ARB );
	}

	qglDisable( GL_TEXTURE_RECTANGLE_ARB );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );
	qglEnable( GL_TEXTURE_2D );
}


/*
=============
RBPP_ApplyBloom

Run the retail downsample, bright-pass, blur, and combine chain on rectangle textures.
=============
*/
static qboolean RBPP_ApplyBloom( void ) {
	int bloomMode;
	float brightThreshold;
	float bloomIntensity;
	float bloomSaturation;
	float sceneIntensity;
	float sceneSaturation;
	ppRenderTarget_t *finalBloom;

	if ( !backEnd.bloomActive || !s_postProcess.sceneTarget.initialized ||
		!s_postProcess.bloomDownsampleTarget.initialized || !s_postProcess.bloomBrightTarget.initialized ||
		!s_postProcess.bloomBlurVerticalTarget.initialized || !s_postProcess.bloomBlurHorizontalTarget.initialized ) {
		return qfalse;
	}

	bloomMode = RBPP_GetBloomMode();
	if ( bloomMode <= 0 ) {
		return qfalse;
	}

	if ( bloomMode == 2 &&
		( !s_postProcess.bloomQuarterDownsampleTarget.initialized ||
		!s_postProcess.bloomQuarterVerticalTarget.initialized ||
		!s_postProcess.bloomQuarterHorizontalTarget.initialized ) ) {
		return qfalse;
	}

	brightThreshold = r_bloomBrightThreshold ? r_bloomBrightThreshold->value : 0.25f;
	bloomIntensity = r_bloomIntensity ? r_bloomIntensity->value : 0.5f;
	bloomSaturation = r_bloomSaturation ? r_bloomSaturation->value : 0.8f;
	sceneIntensity = r_bloomSceneIntensity ? r_bloomSceneIntensity->value : 1.0f;
	sceneSaturation = r_bloomSceneSaturation ? r_bloomSceneSaturation->value : 1.0f;

	RBPP_BindRenderTarget( &s_postProcess.bloomDownsampleTarget );
	RBPP_Set2DState( s_postProcess.bloomDownsampleTarget.width, s_postProcess.bloomDownsampleTarget.height );
	s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.downsampleProgram.programObject );
	RBPP_BindRectangleTexture( 0, s_postProcess.sceneTarget.texture );
	RBPP_DrawQuad( s_postProcess.bloomDownsampleTarget.width, s_postProcess.bloomDownsampleTarget.height, (float)s_postProcess.sceneTarget.width, (float)s_postProcess.sceneTarget.height, (float)s_postProcess.sceneTarget.width, (float)s_postProcess.sceneTarget.height );

	RBPP_BindRenderTarget( &s_postProcess.bloomBrightTarget );
	RBPP_Set2DState( s_postProcess.bloomBrightTarget.width, s_postProcess.bloomBrightTarget.height );
	s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.brightPassProgram.programObject );
	if ( s_postProcess.brightPassProgram.brightThresholdUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.brightPassProgram.brightThresholdUniform, brightThreshold );
	}
	RBPP_BindRectangleTexture( 0, s_postProcess.bloomDownsampleTarget.texture );
	RBPP_DrawQuad( s_postProcess.bloomBrightTarget.width, s_postProcess.bloomBrightTarget.height, (float)s_postProcess.bloomDownsampleTarget.width, (float)s_postProcess.bloomDownsampleTarget.height, (float)s_postProcess.bloomDownsampleTarget.width, (float)s_postProcess.bloomDownsampleTarget.height );

	RBPP_BindRenderTarget( &s_postProcess.bloomBlurVerticalTarget );
	RBPP_Set2DState( s_postProcess.bloomBlurVerticalTarget.width, s_postProcess.bloomBlurVerticalTarget.height );
	s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.blurVerticalProgram.programObject );
	RBPP_BindRectangleTexture( 0, s_postProcess.bloomBrightTarget.texture );
	RBPP_DrawQuad( s_postProcess.bloomBlurVerticalTarget.width, s_postProcess.bloomBlurVerticalTarget.height, (float)s_postProcess.bloomBrightTarget.width, (float)s_postProcess.bloomBrightTarget.height, (float)s_postProcess.bloomBrightTarget.width, (float)s_postProcess.bloomBrightTarget.height );

	RBPP_BindRenderTarget( &s_postProcess.bloomBlurHorizontalTarget );
	RBPP_Set2DState( s_postProcess.bloomBlurHorizontalTarget.width, s_postProcess.bloomBlurHorizontalTarget.height );
	s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.blurHorizontalProgram.programObject );
	RBPP_BindRectangleTexture( 0, s_postProcess.bloomBlurVerticalTarget.texture );
	RBPP_DrawQuad( s_postProcess.bloomBlurHorizontalTarget.width, s_postProcess.bloomBlurHorizontalTarget.height, (float)s_postProcess.bloomBlurVerticalTarget.width, (float)s_postProcess.bloomBlurVerticalTarget.height, (float)s_postProcess.bloomBlurVerticalTarget.width, (float)s_postProcess.bloomBlurVerticalTarget.height );

	finalBloom = &s_postProcess.bloomBlurHorizontalTarget;

	if ( bloomMode == 2 ) {
		RBPP_BindRenderTarget( &s_postProcess.bloomQuarterDownsampleTarget );
		RBPP_Set2DState( s_postProcess.bloomQuarterDownsampleTarget.width, s_postProcess.bloomQuarterDownsampleTarget.height );
		s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.downsampleProgram.programObject );
		RBPP_BindRectangleTexture( 0, finalBloom->texture );
		RBPP_DrawQuad( s_postProcess.bloomQuarterDownsampleTarget.width, s_postProcess.bloomQuarterDownsampleTarget.height, (float)finalBloom->width, (float)finalBloom->height, (float)finalBloom->width, (float)finalBloom->height );

		RBPP_BindRenderTarget( &s_postProcess.bloomQuarterVerticalTarget );
		RBPP_Set2DState( s_postProcess.bloomQuarterVerticalTarget.width, s_postProcess.bloomQuarterVerticalTarget.height );
		s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.blurVerticalProgram.programObject );
		RBPP_BindRectangleTexture( 0, s_postProcess.bloomQuarterDownsampleTarget.texture );
		RBPP_DrawQuad( s_postProcess.bloomQuarterVerticalTarget.width, s_postProcess.bloomQuarterVerticalTarget.height, (float)s_postProcess.bloomQuarterDownsampleTarget.width, (float)s_postProcess.bloomQuarterDownsampleTarget.height, (float)s_postProcess.bloomQuarterDownsampleTarget.width, (float)s_postProcess.bloomQuarterDownsampleTarget.height );

		RBPP_BindRenderTarget( &s_postProcess.bloomQuarterHorizontalTarget );
		RBPP_Set2DState( s_postProcess.bloomQuarterHorizontalTarget.width, s_postProcess.bloomQuarterHorizontalTarget.height );
		s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.blurHorizontalProgram.programObject );
		RBPP_BindRectangleTexture( 0, s_postProcess.bloomQuarterVerticalTarget.texture );
		RBPP_DrawQuad( s_postProcess.bloomQuarterHorizontalTarget.width, s_postProcess.bloomQuarterHorizontalTarget.height, (float)s_postProcess.bloomQuarterVerticalTarget.width, (float)s_postProcess.bloomQuarterVerticalTarget.height, (float)s_postProcess.bloomQuarterVerticalTarget.width, (float)s_postProcess.bloomQuarterVerticalTarget.height );
		finalBloom = &s_postProcess.bloomQuarterHorizontalTarget;
	}

	RBPP_ReleaseSceneRenderTarget();
	RBPP_Set2DState( glConfig.vidWidth, glConfig.vidHeight );
	s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.combineProgram.programObject );
	if ( s_postProcess.combineProgram.bloomSaturationUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.bloomSaturationUniform, bloomSaturation );
	}
	if ( s_postProcess.combineProgram.bloomIntensityUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.bloomIntensityUniform, bloomIntensity );
	}
	if ( s_postProcess.combineProgram.sceneIntensityUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.sceneIntensityUniform, sceneIntensity );
	}
	if ( s_postProcess.combineProgram.sceneSaturationUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.sceneSaturationUniform, sceneSaturation );
	}
	RBPP_BindRectangleTexture( 0, s_postProcess.sceneTarget.texture );
	RBPP_BindRectangleTexture( 1, finalBloom->texture );
	RBPP_DrawQuad( glConfig.vidWidth, glConfig.vidHeight, (float)s_postProcess.sceneTarget.width, (float)s_postProcess.sceneTarget.height, (float)finalBloom->width, (float)finalBloom->height );

	s_postProcess.procs.qglUseProgramObjectARBFunc( 0 );
	if ( qglActiveTextureARB ) {
		qglActiveTextureARB( GL_TEXTURE1_ARB );
		qglDisable( GL_TEXTURE_RECTANGLE_ARB );
		qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );
		qglActiveTextureARB( GL_TEXTURE0_ARB );
	}

	qglDisable( GL_TEXTURE_RECTANGLE_ARB );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );
	qglEnable( GL_TEXTURE_2D );
	return qtrue;
}


/*
=============
RBPP_ApplyColorCorrectPass

Copy the current default framebuffer into the retail color-correct texture and run the shader-backed correction pass.
=============
*/
static void RBPP_ApplyColorCorrectPass( void ) {
	float gammaRecip;
	float overbright;
	float contrast;

	if ( !backEnd.colorCorrectActive || !s_postProcess.colorCorrectTexture || !s_postProcess.colorCorrectProgram.programObject ) {
		return;
	}

	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, s_postProcess.colorCorrectTexture );
	qglCopyTexSubImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, 0, 0, 0, 0, glConfig.vidWidth, glConfig.vidHeight );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );

	gammaRecip = 1.0f;
	if ( ( !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {
		gammaRecip = 1.0f / r_gamma->value;
	}

	overbright = 1.0f;
	if ( r_overBrightBits ) {
		overbright = 2.0f * r_overBrightBits->integer;
		if ( overbright <= 1.0f ) {
			overbright = 1.0f;
		}
	}

	contrast = 1.0f;
	if ( ( !web_browserActive || !web_browserActive->integer ) && r_contrast ) {
		contrast = r_contrast->value;
	}

	RBPP_Set2DState( glConfig.vidWidth, glConfig.vidHeight );
	s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.colorCorrectProgram.programObject );
	if ( s_postProcess.colorCorrectProgram.gammaRecipUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.gammaRecipUniform, gammaRecip );
	}
	if ( s_postProcess.colorCorrectProgram.overbrightUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.overbrightUniform, overbright );
	}
	if ( s_postProcess.colorCorrectProgram.contrastUniform >= 0 ) {
		s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.contrastUniform, contrast );
	}
	RBPP_BindRectangleTexture( 0, s_postProcess.colorCorrectTexture );
	RBPP_DrawQuad( glConfig.vidWidth, glConfig.vidHeight, (float)s_postProcess.colorCorrectWidth, (float)s_postProcess.colorCorrectHeight, (float)s_postProcess.colorCorrectWidth, (float)s_postProcess.colorCorrectHeight );
	s_postProcess.procs.qglUseProgramObjectARBFunc( 0 );

	if ( qglActiveTextureARB ) {
		qglActiveTextureARB( GL_TEXTURE1_ARB );
		qglDisable( GL_TEXTURE_RECTANGLE_ARB );
		qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );
		qglActiveTextureARB( GL_TEXTURE0_ARB );
	}

	qglDisable( GL_TEXTURE_RECTANGLE_ARB );
	qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );
	qglEnable( GL_TEXTURE_2D );
}


/*
=============
RBPP_Submit

Present the offscreen scene target through the recovered retail bloom and color-correct pipeline.
=============
*/
static void RBPP_Submit( void ) {
	qboolean wasActive;

	wasActive = backEnd.postProcessActive;
	if ( backEnd.postProcessNeedsReset && !wasActive ) {
		RBPP_ResetIfNeeded();
		return;
	}

	if ( !RB_PostProcessEnabled() || !s_postProcess.sceneTarget.initialized ) {
		return;
	}

	if ( backEnd.bloomActive ) {
		if ( !RBPP_ApplyBloom() ) {
			RBPP_ReleaseSceneRenderTarget();
			RBPP_BlitSceneTarget();
		}
	} else {
		RBPP_ReleaseSceneRenderTarget();
		RBPP_BlitSceneTarget();
	}

	if ( backEnd.colorCorrectActive ) {
		RBPP_ApplyColorCorrectPass();
	}

	if ( backEnd.postProcessNeedsReset ) {
		RBPP_ResetIfNeeded();
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
=============
RB_GetFastSkyClearColor
=============
*/
static void RB_GetFastSkyClearColor( vec3_t color ) {
	const char		*string;
	char			*end;
	unsigned long	rgb;

	rgb = 0;
	string = r_fastSkyColor ? r_fastSkyColor->string : NULL;
	if ( string && string[0] ) {
		rgb = strtoul( string, &end, 0 );
		if ( end == string ) {
			rgb = (unsigned long)r_fastSkyColor->integer;
		}
	}

	color[0] = ( ( rgb >> 16 ) & 0xff ) / 255.0f;
	color[1] = ( ( rgb >> 8 ) & 0xff ) / 255.0f;
	color[2] = ( rgb & 0xff ) / 255.0f;
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
	vec3_t fastSkyColor;

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
		RB_GetFastSkyClearColor( fastSkyColor );
		qglClearColor( fastSkyColor[0], fastSkyColor[1], fastSkyColor[2], 1.0f );
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
	unsigned int	oldSort;
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
	oldSort = ~0u;
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
			|| ( entityNum != oldEntityNum && !r_forceMergeEntities->integer && !shader->entityMergable ) ) {
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
==============================
RB_DrawAdvertisementQueryQuad
==============================
*/
static void RB_DrawAdvertisementQueryQuad( const vec3_t points[4] ) {
	int		i;

	qglColor3f( 1.0f, 1.0f, 1.0f );
	qglBegin( GL_QUADS );
	for ( i = 0 ; i < 4 ; i++ ) {
		qglVertex3fv( points[i] );
	}
	qglEnd();
}

/*
==========================
RB_DrawAdvertisementQueries
==========================
*/
const void *RB_DrawAdvertisementQueries( const void *data ) {
	const advertisementQueryCommand_t	*cmd;
	GLboolean							depthMaskEnabled;
	GLint								depthFunc;
	qboolean							blendEnabled;
	qboolean							depthTestEnabled;
	int									i;

	cmd = (const advertisementQueryCommand_t *)data;
	if ( !qglBeginQueryARB || !qglEndQueryARB || cmd->numEntries <= 0 ) {
		return (const void *)(cmd + 1);
	}

	qglGetBooleanv( GL_DEPTH_WRITEMASK, &depthMaskEnabled );
	depthTestEnabled = qglIsEnabled( GL_DEPTH_TEST );
	blendEnabled = qglIsEnabled( GL_BLEND );
	qglGetIntegerv( GL_DEPTH_FUNC, &depthFunc );

	GL_Bind( tr.whiteImage );
	GL_Cull( CT_TWO_SIDED );
	qglDisable( GL_BLEND );
	qglDepthMask( GL_FALSE );
	qglColorMask( GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE );

	if ( !depthTestEnabled ) {
		qglEnable( GL_DEPTH_TEST );
	}

	for ( i = 0 ; i < cmd->numEntries ; i++ ) {
		qglDepthFunc( GL_EQUAL );
		qglBeginQueryARB( GL_SAMPLES_PASSED_ARB, cmd->entries[i].occlusionQueryIds[0] );
		RB_DrawAdvertisementQueryQuad( cmd->entries[i].points );
		qglEndQueryARB( GL_SAMPLES_PASSED_ARB );

		qglDepthFunc( GL_LEQUAL );
		qglBeginQueryARB( GL_SAMPLES_PASSED_ARB, cmd->entries[i].occlusionQueryIds[1] );
		RB_DrawAdvertisementQueryQuad( cmd->entries[i].points );
		qglEndQueryARB( GL_SAMPLES_PASSED_ARB );
	}

	GL_Cull( CT_BACK_SIDED );
	qglColorMask( GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE );

	if ( blendEnabled ) {
		qglEnable( GL_BLEND );
	}
	if ( depthMaskEnabled ) {
		qglDepthMask( GL_TRUE );
	}
	if ( !depthTestEnabled ) {
		qglDisable( GL_DEPTH_TEST );
	}
	if ( depthFunc != GL_LEQUAL ) {
		qglDepthFunc( depthFunc );
	}

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
===============
RB_ShowFontAtlas
===============
*/
static void RB_ShowFontAtlas( void ) {
	image_t	*image;
	float	x;
	float	y;
	float	w;
	float	h;
	float	scale;
	float	maxWidth;
	float	maxHeight;
	int		atlasWidth;
	int		atlasHeight;

	if ( !R_GetFontStashDebugInfo( &image, &atlasWidth, &atlasHeight ) || !image ) {
		return;
	}

	if ( !backEnd.projection2D ) {
		RB_SetGL2D();
	}

	maxWidth = glConfig.vidWidth - 32.0f;
	maxHeight = glConfig.vidHeight - 32.0f;
	scale = 1.0f;
	if ( atlasWidth > 0 && atlasWidth > maxWidth ) {
		scale = maxWidth / atlasWidth;
	}
	if ( atlasHeight > 0 && atlasHeight * scale > maxHeight ) {
		scale = maxHeight / atlasHeight;
	}

	x = 16.0f;
	y = 16.0f;
	w = atlasWidth * scale;
	h = atlasHeight * scale;

	GL_Bind( image );
	qglColor4f( 1.0f, 1.0f, 1.0f, 1.0f );
	qglBegin( GL_QUADS );
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
	if ( r_debugFontAtlas->integer ) {
		RB_ShowFontAtlas();
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
		case RC_ADVERTISEMENT_QUERIES:
			data = RB_DrawAdvertisementQueries( data );
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

