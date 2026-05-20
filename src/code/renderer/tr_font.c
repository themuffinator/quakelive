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
// tr_font.c
// 
//
// The font system uses FreeType 2.x to render TrueType fonts for use within the game.
// As of this writing ( Nov, 2000 ) Team Arena uses these fonts for all of the ui and 
// about 90% of the cgame presentation. A few areas of the CGAME were left uses the old 
// fonts since the code is shared with standard Q3A.
//
// If you include this font rendering code in a commercial product you MUST include the
// following somewhere with your product, see www.freetype.org for specifics or changes.
// The Freetype code also uses some hinting techniques that MIGHT infringe on patents 
// held by apple so be aware of that also.
//
// As of Q3A 1.25+ and Team Arena, we are shipping the game with the font rendering code
// disabled. This removes any potential patent issues and it keeps us from having to 
// distribute an actual TrueTrype font which is 1. expensive to do and 2. seems to require
// an act of god to accomplish. 
//
// What we did was pre-render the fonts using FreeType ( which is why we leave the FreeType
// credit in the credits ) and then saved off the glyph data and then hand touched up the 
// font bitmaps so they scale a bit better in GL.
//
// There are limitations in the way fonts are saved and reloaded in that it is based on 
// point size and not name. So if you pre-render Helvetica in 18 point and Impact in 18 point
// you will end up with a single 18 point data file and image set. Typically you will want to 
// choose 3 sizes to best approximate the scaling you will be doing in the ui scripting system
// 
// In the UI Scripting code, a scale of 1.0 is equal to a 48 point font. In Team Arena, we
// use three or four scales, most of them exactly equaling the specific rendered size. We 
// rendered three sizes in Team Arena, 12, 16, and 20. 
//
// To generate new font data you need to go through the following steps.
// 1. delete the fontImage_x_xx.tga files and fontImage_xx.dat files from the fonts path.
// 2. in a ui script, specificy a font, smallFont, and bigFont keyword with font name and 
//    point size. the original TrueType fonts must exist in fonts at this point.
// 3. run the game, you should see things normally.
// 4. Exit the game and there will be three dat files and at least three tga files. The 
//    tga's are in 256x256 pages so if it takes three images to render a 24 point font you 
//    will end up with fontImage_0_24.tga through fontImage_2_24.tga
// 5. You will need to flip the tga's in Photoshop as the tga output code writes them upside
//    down.
// 6. In future runs of the game, the system looks for these images and data files when a s
//    specific point sized font is rendered and loads them for use. 
// 7. Because of the original beta nature of the FreeType code you will probably want to hand
//    touch the font bitmaps.
// 
// Currently a define in the project turns on or off the FreeType code which is currently
// defined out. To pre-render new fonts you need to enable the repo-managed FreeType lane
// so BUILD_FREETYPE is defined for the renderer build.


#include "tr_local.h"
#include "../qcommon/qcommon.h"
#include <stdio.h>

#if defined( _WIN32 )
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

#ifdef BUILD_FREETYPE
#include <ft2build.h>
/*
 * Reference SDK headers kept here to document the intended external FreeType lane:
 * #include FT_ERRORS_H
 * #include FT_SYSTEM_H
 * #include FT_IMAGE_H
 */
#include FT_FREETYPE_H
#include FT_OUTLINE_H

#define _FLOOR(x)  ((x) & -64)
#define _CEIL(x)   (((x)+63) & -64)
#define _TRUNC(x)  ((x) >> 6)

FT_Library ftLibrary = NULL;  
#endif

#define MAX_FONTS 16
#define R_FONT_ATLAS_SIZE 256
#define R_FONT_ATLAS_PIXEL_COUNT ( R_FONT_ATLAS_SIZE * R_FONT_ATLAS_SIZE )
#define R_COMPAT_FONT_CELL_SIZE 16
#define R_COMPAT_FONT_GRID_SIZE 16
#define R_COMPAT_FONT_TOP 12
#define R_COMPAT_FONT_BOTTOM -4
#define R_FONTSTASH_TEXTURE_NAME "*fontstash"
#define R_FONTSTASH_INITIAL_WIDTH 512
#define R_FONTSTASH_INITIAL_HEIGHT 512
#define R_FONTSTASH_MAX_WIDTH 2048
#define R_FONTSTASH_MAX_HEIGHT 1024
#define R_FONTSTASH_ERROR_ATLAS_FULL 1
#define R_FONTSTASH_FACE_NAME_MAX 32
#define R_FONTSTASH_POINT_SIZE 48
#define R_FONTSTASH_PADDING 1
#define R_FONTSTASH_GLYPH_CACHE_GROW 64
static int registeredFontCount = 0;
static fontInfo_t registeredFont[MAX_FONTS];

typedef enum {
	R_FONTSTASH_FACE_NORMAL = 0,
	R_FONTSTASH_FACE_SANS,
	R_FONTSTASH_FACE_MONO,
	R_FONTSTASH_FACE_SANS_FALLBACK,
	R_FONTSTASH_FACE_SANS_WINDOWS_FALLBACK,
	R_FONTSTASH_FACE_COUNT
} rFontStashFaceId_t;

typedef struct {
	int	left;
	int	right;
	int	top;
	int	bottom;
	int	xAdvance;
} rFontStashHostGlyph_t;

typedef struct {
	unsigned int	codepoint;
	short		scaleTenths;
	short		reserved;
	glyphInfo_t	glyph;
	rFontStashHostGlyph_t	hostGlyph;
} rFontStashGlyph_t;

typedef struct {
	int	ascent;
	int	descent;
	int	lineHeight;
} rFontStashFaceMetrics_t;

typedef struct {
	glyphInfo_t			*glyph;
	const rFontStashHostGlyph_t	*hostGlyph;
	float				scaleFactor;
} rFontStashResolvedGlyph_t;

typedef struct {
	char		name[R_FONTSTASH_FACE_NAME_MAX];
	char		resolvedPath[MAX_OSPATH];
	void		*fontData;
	int		fontDataLength;
	int		handle;
	qboolean	loaded;
#ifdef BUILD_FREETYPE
	FT_Face		ftFace;
#endif
	rFontStashGlyph_t	*hostGlyphs;
	int		hostGlyphCount;
	int		hostGlyphCapacity;
	fontInfo_t	compatFont;
	qboolean	compatFontLoaded;
} rFontStashFace_t;

typedef struct rFontStashState_s rFontStashState_t;

struct rFontStashState_s {
	int		texnum;
	int		width;
	int		height;
	byte		*buffer;
	image_t		*image;
	qhandle_t	shader;
	qboolean	initialized;
	int		nextX;
	int		nextY;
	int		rowHeight;
	void		(*errorCallback)( struct rFontStashState_s *fontStash, int error, int val );
	rFontStashFace_t	faces[R_FONTSTASH_FACE_COUNT];
	rFontStashFace_t	*primarySansFace;
	rFontStashFace_t	*fallbackSansFace;
	rFontStashFace_t	*windowsFallbackFace;
};

static rFontStashState_t r_fontStash;

#ifdef BUILD_FREETYPE
void R_GetGlyphInfo(FT_GlyphSlot glyph, int *left, int *right, int *width, int *top, int *bottom, int *height, int *pitch) {

  *left  = _FLOOR( glyph->metrics.horiBearingX );
  *right = _CEIL( glyph->metrics.horiBearingX + glyph->metrics.width );
  *width = _TRUNC(*right - *left);
    
  *top    = _CEIL( glyph->metrics.horiBearingY );
  *bottom = _FLOOR( glyph->metrics.horiBearingY - glyph->metrics.height );
  *height = _TRUNC( *top - *bottom );
  *pitch  = ( qtrue ? (*width+3) & -4 : (*width+7) >> 3 );
}


FT_Bitmap *R_RenderGlyph(FT_GlyphSlot glyph, glyphInfo_t* glyphOut) {

  FT_Bitmap  *bit2;
  int row;
  int pitch;
  int size;

  if ( glyph->format == FT_GLYPH_FORMAT_OUTLINE ) {
    if ( FT_Render_Glyph( glyph, FT_RENDER_MODE_NORMAL ) != 0 ) {
      return NULL;
    }
  } else if ( glyph->format != FT_GLYPH_FORMAT_BITMAP ) {
    ri.Printf( PRINT_ALL, "Non-outline fonts are not supported\n" );
    return NULL;
  }

  pitch = glyph->bitmap.pitch < 0 ? -glyph->bitmap.pitch : glyph->bitmap.pitch;
  size = pitch * glyph->bitmap.rows;

  bit2 = Z_Malloc( sizeof( FT_Bitmap ) );
  Com_Memset( bit2, 0, sizeof( FT_Bitmap ) );

  bit2->width = glyph->bitmap.width;
  bit2->rows = glyph->bitmap.rows;
  bit2->pitch = pitch;
  bit2->pixel_mode = glyph->bitmap.pixel_mode;
  bit2->num_grays = glyph->bitmap.num_grays;
  bit2->buffer = Z_Malloc( size > 0 ? size : 1 );
  Com_Memset( bit2->buffer, 0, size > 0 ? size : 1 );

  if ( glyph->bitmap.buffer && size > 0 ) {
    for ( row = 0; row < glyph->bitmap.rows; row++ ) {
      const byte *src;

      if ( glyph->bitmap.pitch < 0 ) {
        src = glyph->bitmap.buffer + ( ( glyph->bitmap.rows - 1 - row ) * pitch );
      } else {
        src = glyph->bitmap.buffer + ( row * glyph->bitmap.pitch );
      }
      Com_Memcpy( bit2->buffer + ( row * pitch ), src, pitch );
    }
  }

  glyphOut->height = glyph->bitmap.rows;
  glyphOut->pitch = pitch;
  glyphOut->top = glyph->bitmap_top;
  glyphOut->bottom = glyph->bitmap_top - glyph->bitmap.rows;

  return bit2;

  return NULL;
}

void WriteTGA (char *filename, byte *data, int width, int height) {
	byte	*buffer;
	int		i, c;

	buffer = Z_Malloc(width*height*4 + 18);
	Com_Memset (buffer, 0, 18);
	buffer[2] = 2;		// uncompressed type
	buffer[12] = width&255;
	buffer[13] = width>>8;
	buffer[14] = height&255;
	buffer[15] = height>>8;
	buffer[16] = 32;	// pixel size

	// swap rgb to bgr
	c = 18 + width * height * 4;
	for (i=18 ; i<c ; i+=4)
	{
		buffer[i] = data[i-18+2];		// blue
		buffer[i+1] = data[i-18+1];		// green
		buffer[i+2] = data[i-18+0];		// red
		buffer[i+3] = data[i-18+3];		// alpha
	}

	ri.FS_WriteFile(filename, buffer, c);

	//f = fopen (filename, "wb");
	//fwrite (buffer, 1, c, f);
	//fclose (f);

	Z_Free (buffer);
}

static glyphInfo_t *RE_ConstructGlyphInfo(unsigned char *imageOut, int *xOut, int *yOut, int *maxHeight, FT_Face face, const unsigned char c, qboolean calcHeight) {
  int i;
  static glyphInfo_t glyph;
  unsigned char *src, *dst;
  float scaled_width, scaled_height;
  FT_Bitmap *bitmap = NULL;

  Com_Memset(&glyph, 0, sizeof(glyphInfo_t));
  // make sure everything is here
  if (face != NULL) {
    FT_Load_Glyph(face, FT_Get_Char_Index( face, c), FT_LOAD_DEFAULT );
    bitmap = R_RenderGlyph(face->glyph, &glyph);
    if (bitmap) {
      glyph.xSkip = (face->glyph->metrics.horiAdvance >> 6) + 1;
    } else {
      return &glyph;
    }

    if (glyph.height > *maxHeight) {
      *maxHeight = glyph.height;
    }

    if (calcHeight) {
      Z_Free(bitmap->buffer);
      Z_Free(bitmap);
      return &glyph;
    }

/*
    // need to convert to power of 2 sizes so we do not get 
    // any scaling from the gl upload
  	for (scaled_width = 1 ; scaled_width < glyph.pitch ; scaled_width<<=1)
	  	;
  	for (scaled_height = 1 ; scaled_height < glyph.height ; scaled_height<<=1)
	  	;
*/

    scaled_width = glyph.pitch;
    scaled_height = glyph.height;

    // we need to make sure we fit
    if (*xOut + scaled_width + 1 >= 255) {
      if (*yOut + *maxHeight + 1 >= 255) {
        *yOut = -1;
        *xOut = -1;
        Z_Free(bitmap->buffer);
        Z_Free(bitmap);
        return &glyph;
      } else {
        *xOut = 0;
        *yOut += *maxHeight + 1;
      }
    } else if (*yOut + *maxHeight + 1 >= 255) {
      *yOut = -1;
      *xOut = -1;
      Z_Free(bitmap->buffer);
      Z_Free(bitmap);
      return &glyph;
    }


    if ( *xOut < 0 || *yOut < 0 ||
      *xOut + glyph.pitch > R_FONT_ATLAS_SIZE ||
      *yOut + glyph.height > R_FONT_ATLAS_SIZE ) {
      *yOut = -1;
      *xOut = -1;
      Z_Free(bitmap->buffer);
      Z_Free(bitmap);
      return &glyph;
    }

    src = bitmap->buffer;
    dst = imageOut + (*yOut * R_FONT_ATLAS_SIZE) + *xOut;

		if (bitmap->pixel_mode == FT_PIXEL_MODE_MONO) {
			for (i = 0; i < glyph.height; i++) {
				int j;
				unsigned char *_src = src;
				unsigned char *_dst = dst;
				unsigned char mask = 0x80;
				unsigned char val = *_src;
				for (j = 0; j < glyph.pitch; j++) {
					if (mask == 0x80) {
						val = *_src++;
					}
					if (val & mask) {
						*_dst = 0xff;
					}
					mask >>= 1;
        
					if ( mask == 0 ) {
						mask = 0x80;
					}
					_dst++;
				}

				src += glyph.pitch;
				dst += R_FONT_ATLAS_SIZE;

			}
		} else {
	    for (i = 0; i < glyph.height; i++) {
		    Com_Memcpy(dst, src, glyph.pitch);
			  src += glyph.pitch;
				dst += R_FONT_ATLAS_SIZE;
	    }
		}

    // we now have an 8 bit per pixel grey scale bitmap 
    // that is width wide and pf->ftSize->metrics.y_ppem tall

    glyph.imageHeight = scaled_height;
    glyph.imageWidth = scaled_width;
    glyph.s = (float)*xOut / R_FONT_ATLAS_SIZE;
    glyph.t = (float)*yOut / R_FONT_ATLAS_SIZE;
    glyph.s2 = glyph.s + (float)scaled_width / R_FONT_ATLAS_SIZE;
    glyph.t2 = glyph.t + (float)scaled_height / R_FONT_ATLAS_SIZE;

    *xOut += scaled_width + 1;
  }

  Z_Free(bitmap->buffer);
  Z_Free(bitmap);

  return &glyph;
}
#endif

static int fdOffset;
static byte	*fdFile;

int readInt() {
	int i = fdFile[fdOffset]+(fdFile[fdOffset+1]<<8)+(fdFile[fdOffset+2]<<16)+(fdFile[fdOffset+3]<<24);
	fdOffset += 4;
	return i;
}

typedef union {
	byte	fred[4];
	float	ffred;
} poor;

float readFloat() {
	poor	me;
#if idppc
	me.fred[0] = fdFile[fdOffset+3];
	me.fred[1] = fdFile[fdOffset+2];
	me.fred[2] = fdFile[fdOffset+1];
	me.fred[3] = fdFile[fdOffset+0];
#else
	me.fred[0] = fdFile[fdOffset+0];
	me.fred[1] = fdFile[fdOffset+1];
	me.fred[2] = fdFile[fdOffset+2];
	me.fred[3] = fdFile[fdOffset+3];
#endif
	fdOffset += 4;
	return me.ffred;
}

/*
=================
R_FontPathIsAbsolute
=================
*/
static qboolean R_FontPathIsAbsolute( const char *path ) {
	if ( !path || !path[0] ) {
		return qfalse;
	}

	if ( path[0] == '\\' || path[0] == '/' ) {
		return qtrue;
	}

	if ( path[1] == ':' && ( ( path[0] >= 'A' && path[0] <= 'Z' ) || ( path[0] >= 'a' && path[0] <= 'z' ) ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=================
R_NormalizeFontSourcePath
=================
*/
static void R_NormalizeFontSourcePath( const char *fontName, char *resolvedPath, int resolvedPathSize ) {
	if ( !resolvedPath || resolvedPathSize <= 0 ) {
		return;
	}

	if ( !fontName || !fontName[0] ) {
		Q_strncpyz( resolvedPath, "fonts/handelgothic.ttf", resolvedPathSize );
		return;
	}

	if ( !Q_stricmp( fontName, "fonts/font" )
		|| !Q_stricmp( fontName, "fonts/bigfont" )
		|| !Q_stricmp( fontName, "normal" ) ) {
		Q_strncpyz( resolvedPath, "fonts/handelgothic.ttf", resolvedPathSize );
		return;
	}

	if ( !Q_stricmp( fontName, "fonts/smallfont" )
		|| !Q_stricmp( fontName, "sans" ) ) {
		Q_strncpyz( resolvedPath, "fonts/notosans-regular.ttf", resolvedPathSize );
		return;
	}

	if ( !Q_stricmp( fontName, "fonts/monofont" )
		|| !Q_stricmp( fontName, "mono" ) ) {
		Q_strncpyz( resolvedPath, "fonts/droidsansmono.ttf", resolvedPathSize );
		return;
	}

	if ( !Q_stricmp( fontName, "sans-fallback" )
		|| !Q_stricmp( fontName, "sans-windows-fallback" ) ) {
		Q_strncpyz( resolvedPath, "fonts/droidsansfallbackfull.ttf", resolvedPathSize );
		return;
	}

	Q_strncpyz( resolvedPath, fontName, resolvedPathSize );
}

/*
=================
R_BuildFontCacheStem

Retail-backed helper that maps Quake Live font aliases and normalized source
paths onto the lowercase cache/page stem used by the classic renderer font
atlases.
=================
*/
static void R_BuildFontCacheStem( const char *fontName, char *cacheStem, int cacheStemSize ) {
	char resolvedPath[MAX_QPATH];
	char strippedName[MAX_QPATH];
	const char *baseName;
	int i;
	int outIndex;

	if ( !cacheStem || cacheStemSize <= 0 ) {
		return;
	}

	R_NormalizeFontSourcePath( fontName, resolvedPath, sizeof( resolvedPath ) );
	baseName = COM_SkipPath( resolvedPath );
	COM_StripExtension( baseName, strippedName );
	Q_strlwr( strippedName );

	if ( !strippedName[0] ) {
		cacheStem[0] = '\0';
		return;
	}

	for ( i = 0, outIndex = 0; strippedName[i] && outIndex < cacheStemSize - 1; i++ ) {
		char c = strippedName[i];

		if ( ( c >= 'a' && c <= 'z' ) || ( c >= '0' && c <= '9' ) ) {
			cacheStem[outIndex++] = c;
		} else {
			cacheStem[outIndex++] = '_';
		}
	}
	cacheStem[outIndex] = '\0';
}

/*
=================
R_BuildLegacyFontCacheName

Compatibility-only point-size cache name preserved for older pre-Quake Live
font bakes.
=================
*/
static void R_BuildLegacyFontCacheName( int pointSize, char *cacheName, int cacheNameSize ) {
	if ( !cacheName || cacheNameSize <= 0 ) {
		return;
	}

	Com_sprintf( cacheName, cacheNameSize, "fonts/fontImage_%i.dat", pointSize );
}

/*
=================
R_BuildFontCacheName
=================
*/
static void R_BuildFontCacheName( const char *fontName, int pointSize, char *cacheName, int cacheNameSize ) {
	char cacheStem[MAX_QPATH];

	if ( !cacheName || cacheNameSize <= 0 ) {
		return;
	}

	R_BuildFontCacheStem( fontName, cacheStem, sizeof( cacheStem ) );
	if ( !cacheStem[0] ) {
		R_BuildLegacyFontCacheName( pointSize, cacheName, cacheNameSize );
		return;
	}

	Com_sprintf( cacheName, cacheNameSize, "fonts/fontImage_%s_%i.dat", cacheStem, pointSize );
}

/*
=================
R_BuildFontPageName
=================
*/
static void R_BuildFontPageName( const char *fontName, int pointSize, int imageNumber, char *pageName, int pageNameSize ) {
	char cacheStem[MAX_QPATH];

	if ( !pageName || pageNameSize <= 0 ) {
		return;
	}

	R_BuildFontCacheStem( fontName, cacheStem, sizeof( cacheStem ) );
	if ( !cacheStem[0] ) {
		Com_sprintf( pageName, pageNameSize, "fonts/fontImage_%i_%i.tga", imageNumber, pointSize );
		return;
	}

	Com_sprintf( pageName, pageNameSize, "fonts/fontImage_%s_%i_%i.tga", cacheStem, imageNumber, pointSize );
}

/*
=================
R_FindRegisteredFont
=================
*/
static int R_FindRegisteredFont( const char *cacheName ) {
	int i;

	for ( i = 0; i < registeredFontCount; i++ ) {
		if ( !Q_stricmp( cacheName, registeredFont[i].name ) ) {
			return i;
		}
	}

	return -1;
}

/*
=================
R_FindCachedFontDataName

Retail-backed face-specific cache probe with an explicit point-size-only
compatibility fallback for older baked font data.
=================
*/
static const char *R_FindCachedFontDataName( const char *cacheName, const char *legacyCacheName ) {
	int len;

	len = ri.FS_ReadFile( cacheName, NULL );
	if ( len == sizeof( fontInfo_t ) ) {
		return cacheName;
	}

	len = ri.FS_ReadFile( legacyCacheName, NULL );
	if ( len == sizeof( fontInfo_t ) ) {
		return legacyCacheName;
	}

	return NULL;
}

/*
=================
R_RegisterCachedFontShaders

Cached-font reload helper: every serialized glyph page name is rebound through
the renderer so all 256 glyph slots share the correct atlas shader handles.
=================
*/
static void R_RegisterCachedFontShaders( fontInfo_t *font ) {
	int i;

	for ( i = GLYPH_START; i <= GLYPH_END; i++ ) {
		font->glyphs[i].glyph = RE_RegisterShaderNoMip( font->glyphs[i].shaderName );
	}
}

/*
=================
R_ReadAbsoluteFontFile

Compatibility bridge for resolved host font paths that do not live inside the
Quake filesystem.
=================
*/
static int R_ReadAbsoluteFontFile( const char *fontName, void **buffer ) {
	FILE *stream;
	long fileSize;
	byte *data;

	if ( !buffer || !R_FontPathIsAbsolute( fontName ) ) {
		return -1;
	}

	stream = fopen( fontName, "rb" );
	if ( !stream ) {
		return -1;
	}

	if ( fseek( stream, 0, SEEK_END ) != 0 ) {
		fclose( stream );
		return -1;
	}

	fileSize = ftell( stream );
	if ( fileSize <= 0 || fseek( stream, 0, SEEK_SET ) != 0 ) {
		fclose( stream );
		return -1;
	}

	data = Z_Malloc( fileSize );
	if ( fread( data, 1, fileSize, stream ) != (size_t)fileSize ) {
		Z_Free( data );
		fclose( stream );
		return -1;
	}

	fclose( stream );
	*buffer = data;
	return (int)fileSize;
}

/*
=================
R_ReadFontFile

Prefer the Quake filesystem first, then fall back to explicit host paths when a
compatibility caller resolved one.
=================
*/
static int R_ReadFontFile( const char *fontName, void **buffer, qboolean *fromFileSystem ) {
	int len;

	if ( fromFileSystem ) {
		*fromFileSystem = qfalse;
	}

	len = ri.FS_ReadFile( fontName, buffer );
	if ( len > 0 ) {
		if ( fromFileSystem ) {
			*fromFileSystem = qtrue;
		}
		return len;
	}

	return R_ReadAbsoluteFontFile( fontName, buffer );
}

/*
=================
R_FreeFontFileBuffer
=================
*/
static void R_FreeFontFileBuffer( void *buffer, qboolean fromFileSystem ) {
	if ( !buffer ) {
		return;
	}

	if ( fromFileSystem ) {
		ri.FS_FreeFile( buffer );
	} else {
		Z_Free( buffer );
	}
}

/*
=================
R_CopyOwnedFontFileBuffer

Retail host text initialization keeps per-face font payloads alive for the
retained fontstash core instead of reading them on demand for every call.
=================
*/
static int R_CopyOwnedFontFileBuffer( const char *fontName, void **ownedBuffer ) {
	void *fileData = NULL;
	qboolean fromFileSystem = qfalse;
	byte *copiedData;
	int len;

	if ( ownedBuffer ) {
		*ownedBuffer = NULL;
	}

	len = R_ReadFontFile( fontName, &fileData, &fromFileSystem );
	if ( len <= 0 || !fileData ) {
		return -1;
	}

	copiedData = Z_Malloc( len );
	Com_Memcpy( copiedData, fileData, len );
	R_FreeFontFileBuffer( fileData, fromFileSystem );

	if ( ownedBuffer ) {
		*ownedBuffer = copiedData;
	}

	return len;
}

/*
=================
R_GetFontStashFace
=================
*/
static rFontStashFace_t *R_GetFontStashFace( rFontStashFaceId_t faceId ) {
	if ( faceId < R_FONTSTASH_FACE_NORMAL || faceId >= R_FONTSTASH_FACE_COUNT ) {
		return NULL;
	}

	return &r_fontStash.faces[faceId];
}

/*
=================
R_ResetFontStashFaceGlyphCache
=================
*/
static void R_ResetFontStashFaceGlyphCache( rFontStashFace_t *face ) {
	if ( !face ) {
		return;
	}

	if ( face->hostGlyphs ) {
		Z_Free( face->hostGlyphs );
	}

	face->hostGlyphs = NULL;
	face->hostGlyphCount = 0;
	face->hostGlyphCapacity = 0;
}

/*
=================
R_GetFontStashScaleTenths

Retail host text rounds the requested face size to tenths before probing the
retained glyph cache.
=================
*/
static int R_GetFontStashScaleTenths( float scale ) {
	int scaleTenths;

	if ( scale <= 0.0f ) {
		scale = R_FONTSTASH_POINT_SIZE;
	}

	scaleTenths = (int)( scale * 10.0f + 0.5f );
	if ( scaleTenths < 2 ) {
		scaleTenths = 2;
	} else if ( scaleTenths > 0x7fff ) {
		scaleTenths = 0x7fff;
	}

	return scaleTenths;
}

/*
=================
R_DecodeFontStashCodepoint

Retail host DrawScaledText/MeasureText walk UTF-8 text instead of indexing raw
bytes. This reconstruction keeps the same byte-stream contract and advances a
single byte on malformed input so callers never get stuck.
=================
*/
static const char *R_DecodeFontStashCodepoint( const char *text, const char *end, unsigned int *outCodepoint ) {
	const unsigned char *cursor;
	int available;
	unsigned int codepoint;
	int length;

	if ( outCodepoint ) {
		*outCodepoint = 0;
	}

	if ( !text || ( end && text >= end ) || !*text ) {
		return text;
	}

	cursor = (const unsigned char *)text;
	available = end ? (int)( end - text ) : 4;

	if ( cursor[0] < 0x80 ) {
		if ( outCodepoint ) {
			*outCodepoint = cursor[0];
		}
		return text + 1;
	}

	if ( ( cursor[0] & 0xE0 ) == 0xC0 ) {
		codepoint = cursor[0] & 0x1F;
		length = 2;
	} else if ( ( cursor[0] & 0xF0 ) == 0xE0 ) {
		codepoint = cursor[0] & 0x0F;
		length = 3;
	} else if ( ( cursor[0] & 0xF8 ) == 0xF0 ) {
		codepoint = cursor[0] & 0x07;
		length = 4;
	} else {
		if ( outCodepoint ) {
			*outCodepoint = cursor[0];
		}
		return text + 1;
	}

	if ( end && available < length ) {
		if ( outCodepoint ) {
			*outCodepoint = cursor[0];
		}
		return text + 1;
	}

	{
		int i;

		for ( i = 1; i < length; i++ ) {
			if ( !cursor[i] || ( cursor[i] & 0xC0 ) != 0x80 ) {
				if ( outCodepoint ) {
					*outCodepoint = cursor[0];
				}
				return text + 1;
			}

			codepoint = ( codepoint << 6 ) | ( cursor[i] & 0x3F );
		}
	}

	if ( ( length == 2 && codepoint < 0x80 ) ||
		( length == 3 && codepoint < 0x800 ) ||
		( length == 4 && codepoint < 0x10000 ) ||
		( codepoint >= 0xD800 && codepoint <= 0xDFFF ) ||
		codepoint > 0x10FFFF ) {
		if ( outCodepoint ) {
			*outCodepoint = cursor[0];
		}
		return text + 1;
	}

	if ( outCodepoint ) {
		*outCodepoint = codepoint;
	}

	return text + length;
}

/*
=================
R_ParseHostTextColorEscape

Retail host text consumes only `^0`..`^7` color escapes. Other caret sequences
stay in the glyph stream.
=================
*/
static qboolean R_ParseHostTextColorEscape( const char *text, const char *end, int *outColorIndex, const char **outNext ) {
	unsigned int codepoint;
	const char *next;

	if ( outColorIndex ) {
		*outColorIndex = -1;
	}
	if ( outNext ) {
		*outNext = text;
	}

	if ( !text || *text != Q_COLOR_ESCAPE ) {
		return qfalse;
	}

	next = R_DecodeFontStashCodepoint( text + 1, end, &codepoint );
	if ( next <= text + 1 || codepoint < '0' || codepoint > '7' ) {
		return qfalse;
	}

	if ( outColorIndex ) {
		*outColorIndex = (int)( codepoint - '0' );
	}
	if ( outNext ) {
		*outNext = next;
	}

	return qtrue;
}

/*
=================
R_AppendFontStashFaceChain
=================
*/
static void R_AppendFontStashFaceChain( rFontStashFace_t **faces, int *faceCount, int maxFaces, rFontStashFace_t *face ) {
	int i;

	if ( !faces || !faceCount || !face || !face->loaded || *faceCount >= maxFaces ) {
		return;
	}

	for ( i = 0; i < *faceCount; i++ ) {
		if ( faces[i] == face ) {
			return;
		}
	}

	faces[*faceCount] = face;
	( *faceCount )++;
}

/*
=================
R_BuildFontStashFaceChain

Retail glyph lookup probes the requested face first, then walks the retained
host fallback-face slots before dropping to the compatibility font lane.
=================
*/
static int R_BuildFontStashFaceChain( rFontStashFace_t *face, rFontStashFace_t **faces, int maxFaces ) {
	int faceCount;

	faceCount = 0;
	R_AppendFontStashFaceChain( faces, &faceCount, maxFaces, face );
	R_AppendFontStashFaceChain( faces, &faceCount, maxFaces, r_fontStash.primarySansFace );
	R_AppendFontStashFaceChain( faces, &faceCount, maxFaces, r_fontStash.fallbackSansFace );
	R_AppendFontStashFaceChain( faces, &faceCount, maxFaces, r_fontStash.windowsFallbackFace );

	return faceCount;
}

/*
=================
R_FindFontStashGlyph
=================
*/
static rFontStashGlyph_t *R_FindFontStashGlyph( rFontStashFace_t *face, unsigned int codepoint, int scaleTenths ) {
	int i;

	if ( !face || !face->hostGlyphs ) {
		return NULL;
	}

	for ( i = 0; i < face->hostGlyphCount; i++ ) {
		rFontStashGlyph_t *glyph;

		glyph = &face->hostGlyphs[i];
		if ( glyph->codepoint == codepoint && glyph->scaleTenths == scaleTenths ) {
			return glyph;
		}
	}

	return NULL;
}

/*
=================
R_EnsureFontStashGlyphCapacity
=================
*/
static qboolean R_EnsureFontStashGlyphCapacity( rFontStashFace_t *face, int requiredCapacity ) {
	rFontStashGlyph_t *glyphs;
	int newCapacity;

	if ( !face ) {
		return qfalse;
	}

	if ( requiredCapacity <= face->hostGlyphCapacity ) {
		return qtrue;
	}

	newCapacity = face->hostGlyphCapacity;
	if ( newCapacity <= 0 ) {
		newCapacity = R_FONTSTASH_GLYPH_CACHE_GROW;
	}

	while ( newCapacity < requiredCapacity ) {
		newCapacity += R_FONTSTASH_GLYPH_CACHE_GROW;
	}

	glyphs = Z_Malloc( newCapacity * sizeof( *glyphs ) );
	Com_Memset( glyphs, 0, newCapacity * sizeof( *glyphs ) );

	if ( face->hostGlyphs && face->hostGlyphCount > 0 ) {
		Com_Memcpy( glyphs, face->hostGlyphs, face->hostGlyphCount * sizeof( *glyphs ) );
	}

	if ( face->hostGlyphs ) {
		Z_Free( face->hostGlyphs );
	}

	face->hostGlyphs = glyphs;
	face->hostGlyphCapacity = newCapacity;
	return qtrue;
}

/*
=================
R_ResetFontStashFace
=================
*/
static void R_ResetFontStashFace( rFontStashFace_t *face ) {
	if ( !face ) {
		return;
	}

#ifdef BUILD_FREETYPE
	if ( face->ftFace ) {
		FT_Done_Face( face->ftFace );
	}
#endif

	if ( face->fontData ) {
		Z_Free( face->fontData );
	}

	R_ResetFontStashFaceGlyphCache( face );
	Com_Memset( face, 0, sizeof( *face ) );
	face->handle = -1;
}

/*
=================
R_ResetFontStashLayout
=================
*/
static void R_ResetFontStashLayout( void ) {
	r_fontStash.nextX = 0;
	r_fontStash.nextY = 0;
	r_fontStash.rowHeight = 0;
}

/*
=================
R_ClearFontStashFaceGlyphState
=================
*/
static void R_ClearFontStashFaceGlyphState( void ) {
	int i;

	for ( i = 0; i < R_FONTSTASH_FACE_COUNT; i++ ) {
		R_ResetFontStashFaceGlyphCache( &r_fontStash.faces[i] );
	}
}

/*
=================
R_ClearFontStashAtlasBuffer
=================
*/
static void R_ClearFontStashAtlasBuffer( void ) {
	if ( !r_fontStash.buffer || r_fontStash.width <= 0 || r_fontStash.height <= 0 ) {
		return;
	}

	Com_Memset( r_fontStash.buffer, 0, r_fontStash.width * r_fontStash.height );
	R_ResetFontStashLayout();
	R_ClearFontStashFaceGlyphState();
}

/*
=================
R_RescaleFontStashGlyphUVs

When the retained atlas grows, keep existing glyph cache entries valid by
rebasing their normalized coordinates onto the new texture dimensions.
=================
*/
static void R_RescaleFontStashGlyphUVs( int oldWidth, int oldHeight, int newWidth, int newHeight ) {
	int faceIndex;

	if ( oldWidth <= 0 || oldHeight <= 0 || newWidth <= 0 || newHeight <= 0 ) {
		return;
	}

	for ( faceIndex = 0; faceIndex < R_FONTSTASH_FACE_COUNT; faceIndex++ ) {
		rFontStashFace_t *face;
		int glyphIndex;

		face = &r_fontStash.faces[faceIndex];
		for ( glyphIndex = 0; glyphIndex < face->hostGlyphCount; glyphIndex++ ) {
			rFontStashGlyph_t *cachedGlyph;
			int x;
			int y;

			cachedGlyph = &face->hostGlyphs[glyphIndex];
			x = (int)( cachedGlyph->glyph.s * oldWidth + 0.5f );
			y = (int)( cachedGlyph->glyph.t * oldHeight + 0.5f );

			cachedGlyph->glyph.s = (float)x / newWidth;
			cachedGlyph->glyph.t = (float)y / newHeight;
			cachedGlyph->glyph.s2 = (float)( x + cachedGlyph->glyph.imageWidth ) / newWidth;
			cachedGlyph->glyph.t2 = (float)( y + cachedGlyph->glyph.imageHeight ) / newHeight;
		}
	}
}

/*
=================
R_BuildFontStashSeedImage

Create a temporary RGBA seed image so the renderer owns *fontstash through the
normal image/shader path before the retained atlas is rebound as an alpha
texture, matching the retail host ownership split.
=================
*/
static byte *R_BuildFontStashSeedImage( const byte *alphaBuffer, int width, int height ) {
	byte *rgbaBuffer;
	int pixelCount;
	int i;

	pixelCount = width * height;
	rgbaBuffer = Z_Malloc( pixelCount * 4 );

	for ( i = 0; i < pixelCount; i++ ) {
		int base = i * 4;
		byte alpha = alphaBuffer ? alphaBuffer[i] : 0;

		rgbaBuffer[base + 0] = 255;
		rgbaBuffer[base + 1] = 255;
		rgbaBuffer[base + 2] = 255;
		rgbaBuffer[base + 3] = alpha;
	}

	return rgbaBuffer;
}

/*
=================
R_UploadFontStashAtlas

Retail host text uses a retained alpha atlas behind the *fontstash image or
shader handle.
=================
*/
static void R_UploadFontStashAtlas( void ) {
	if ( !r_fontStash.image || !r_fontStash.buffer ) {
		return;
	}

	r_fontStash.image->width = r_fontStash.width;
	r_fontStash.image->height = r_fontStash.height;
	r_fontStash.image->uploadWidth = r_fontStash.width;
	r_fontStash.image->uploadHeight = r_fontStash.height;
	r_fontStash.image->internalFormat = GL_ALPHA;
	r_fontStash.image->mipmap = qfalse;
	r_fontStash.image->allowPicmip = qfalse;
	r_fontStash.image->wrapClampMode = GL_CLAMP;
	r_fontStash.texnum = r_fontStash.image->texnum;

	GL_Bind( r_fontStash.image );
	qglTexImage2D( GL_TEXTURE_2D, 0, GL_ALPHA, r_fontStash.width, r_fontStash.height, 0, GL_ALPHA, GL_UNSIGNED_BYTE, r_fontStash.buffer );
	qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP );
	qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP );
	qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
	qglTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
	qglBindTexture( GL_TEXTURE_2D, 0 );
}

/*
=================
R_EnsureFontStashImage

Create or refresh the renderer-owned *fontstash image and shader so later host
text work shares the same retained object lifetime as retail.
=================
*/
static qboolean R_EnsureFontStashImage( void ) {
	byte *seedImage;

	if ( !r_fontStash.buffer || r_fontStash.width <= 0 || r_fontStash.height <= 0 ) {
		return qfalse;
	}

	if ( !r_fontStash.image ) {
		seedImage = R_BuildFontStashSeedImage( r_fontStash.buffer, r_fontStash.width, r_fontStash.height );
		r_fontStash.image = R_CreateImage( R_FONTSTASH_TEXTURE_NAME, seedImage, r_fontStash.width, r_fontStash.height, qfalse, qfalse, GL_CLAMP );
		Z_Free( seedImage );
		if ( !r_fontStash.image ) {
			return qfalse;
		}

		r_fontStash.shader = RE_RegisterShaderFromImage( R_FONTSTASH_TEXTURE_NAME, LIGHTMAP_2D, r_fontStash.image, qfalse );
	}

	if ( !r_fontStash.shader ) {
		r_fontStash.shader = RE_RegisterShaderFromImage( R_FONTSTASH_TEXTURE_NAME, LIGHTMAP_2D, r_fontStash.image, qfalse );
	}

	if ( !r_fontStash.shader ) {
		return qfalse;
	}

	r_fontStash.initialized = qtrue;
	R_UploadFontStashAtlas();
	return qtrue;
}

/*
=================
R_ClearFontStashAtlas
=================
*/
static void R_ClearFontStashAtlas( void ) {
	if ( !r_fontStash.buffer || r_fontStash.width <= 0 || r_fontStash.height <= 0 ) {
		return;
	}

	R_ClearFontStashAtlasBuffer();
	if ( r_fontStash.image ) {
		R_UploadFontStashAtlas();
	}
}

/*
=================
R_ResizeFontStashAtlas
=================
*/
static qboolean R_ResizeFontStashAtlas( int width, int height ) {
	byte *newBuffer;
	byte *oldBuffer;
	int oldWidth;
	int oldHeight;
	int row;

	if ( width <= 0 || height <= 0 ) {
		return qfalse;
	}

	oldBuffer = r_fontStash.buffer;
	oldWidth = r_fontStash.width;
	oldHeight = r_fontStash.height;

	newBuffer = Z_Malloc( width * height );
	Com_Memset( newBuffer, 0, width * height );

	if ( oldBuffer ) {
		if ( oldWidth > 0 && oldHeight > 0 ) {
			int copyWidth = oldWidth < width ? oldWidth : width;
			int copyHeight = oldHeight < height ? oldHeight : height;

			for ( row = 0; row < copyHeight; row++ ) {
				Com_Memcpy( newBuffer + row * width, oldBuffer + row * oldWidth, copyWidth );
			}
		}

		Z_Free( oldBuffer );
	}

	r_fontStash.buffer = newBuffer;
	r_fontStash.width = width;
	r_fontStash.height = height;
	R_RescaleFontStashGlyphUVs( oldWidth, oldHeight, width, height );

	return R_EnsureFontStashImage();
}

/*
=================
R_fonsErrorCallback

Retail host text expands the retained atlas on overflow, then flushes once the
maximum size is reached.
=================
*/
static void R_fonsErrorCallback( rFontStashState_t *fontStash, int error, int val ) {
	int width;
	int height;

	ri.Printf( PRINT_ALL, "R_fonsErrorCallback: error %d val %d\n", error, val );

	if ( !fontStash || error != R_FONTSTASH_ERROR_ATLAS_FULL ) {
		return;
	}

	width = fontStash->width * 2;
	height = fontStash->height * 2;

	if ( width > R_FONTSTASH_MAX_WIDTH ) {
		width = R_FONTSTASH_MAX_WIDTH;
	}

	if ( height > R_FONTSTASH_MAX_HEIGHT ) {
		height = R_FONTSTASH_MAX_HEIGHT;
	}

	if ( width != fontStash->width || height != fontStash->height ) {
		ri.Printf( PRINT_ALL, "Expand font atlas to %dx%d\n", width, height );
		R_ResizeFontStashAtlas( width, height );
		return;
	}

	ri.Printf( PRINT_ALL, "Max font atlas size, flushing\n" );
	R_ClearFontStashAtlas();
}

/*
=================
R_FontStashPathExists
=================
*/
static qboolean R_FontStashPathExists( const char *path ) {
	FILE *stream;

	if ( !path || !path[0] ) {
		return qfalse;
	}

	stream = fopen( path, "rb" );
	if ( !stream ) {
		return qfalse;
	}

	fclose( stream );
	return qtrue;
}

/*
=================
R_ResolveFontStashWindowsFallbackPath

Mirror the retail host fallback search order for the dedicated Windows Unicode
fallback face.
=================
*/
static const char *R_ResolveFontStashWindowsFallbackPath( char *fontPath, int fontPathSize ) {
#if defined( _WIN32 )
	char windowsDirectory[MAX_OSPATH];

	if ( GetWindowsDirectoryA( windowsDirectory, sizeof( windowsDirectory ) ) > 0 ) {
		Com_sprintf( fontPath, fontPathSize, "%s\\fonts\\ARIALUNI.TTF", windowsDirectory );
		if ( R_FontStashPathExists( fontPath ) ) {
			ri.Printf( PRINT_ALL, "Using font fallback from the Windows host: arialuni.ttf\n" );
			return fontPath;
		}

		Com_sprintf( fontPath, fontPathSize, "%s\\fonts\\segoeui.TTF", windowsDirectory );
		if ( R_FontStashPathExists( fontPath ) ) {
			ri.Printf( PRINT_ALL, "Using font fallback from the Windows host: segoeui.ttf\n" );
			Com_sprintf( fontPath, fontPathSize, "%s\\fonts\\segoeui.ttf", windowsDirectory );
			return fontPath;
		}

		ri.Printf( PRINT_ALL, "Using font fallback from the Windows host: l_10646.ttf\n" );
		Com_sprintf( fontPath, fontPathSize, "%s\\fonts\\l_10646.ttf", windowsDirectory );
		return fontPath;
	}
#endif

	Q_strncpyz( fontPath, "fonts/droidsansfallbackfull.ttf", fontPathSize );
	return fontPath;
}

/*
=================
R_LoadFontStashFace
=================
*/
static void R_LoadFontStashFace( rFontStashFaceId_t faceId, const char *faceName, const char *fontPath ) {
	rFontStashFace_t *face;
	void *fontData = NULL;
	int fontDataLength;

	face = R_GetFontStashFace( faceId );
	if ( !face || !faceName || !fontPath ) {
		return;
	}

	R_ResetFontStashFace( face );
	Q_strncpyz( face->name, faceName, sizeof( face->name ) );
	Q_strncpyz( face->resolvedPath, fontPath, sizeof( face->resolvedPath ) );
	face->handle = -1;

	fontDataLength = R_CopyOwnedFontFileBuffer( fontPath, &fontData );
	if ( fontDataLength <= 0 || !fontData ) {
		ri.Printf( PRINT_ALL, "R_InitFontStash: unable to load '%s' from '%s'\n", faceName, fontPath );
		return;
	}

	face->fontData = fontData;
	face->fontDataLength = fontDataLength;
	face->handle = faceId;
	face->loaded = qtrue;

#ifdef BUILD_FREETYPE
	if ( ftLibrary && FT_New_Memory_Face( ftLibrary, face->fontData, face->fontDataLength, 0, &face->ftFace ) == 0 ) {
		if ( FT_Set_Char_Size( face->ftFace, R_FONTSTASH_POINT_SIZE << 6, R_FONTSTASH_POINT_SIZE << 6, 72, 72 ) != 0 ) {
			FT_Done_Face( face->ftFace );
			face->ftFace = NULL;
		}
	}
#endif
}

/*
=================
R_InitFontStashFaces
=================
*/
static void R_InitFontStashFaces( void ) {
	char windowsFallbackPath[MAX_OSPATH];

	R_LoadFontStashFace( R_FONTSTASH_FACE_NORMAL, "normal", "fonts/handelgothic.ttf" );
	R_LoadFontStashFace( R_FONTSTASH_FACE_SANS, "sans", "fonts/notosans-regular.ttf" );
	R_LoadFontStashFace( R_FONTSTASH_FACE_MONO, "mono", "fonts/droidsansmono.ttf" );
	R_LoadFontStashFace( R_FONTSTASH_FACE_SANS_FALLBACK, "sans-fallback", "fonts/droidsansfallbackfull.ttf" );
	R_LoadFontStashFace( R_FONTSTASH_FACE_SANS_WINDOWS_FALLBACK, "sans-windows-fallback", R_ResolveFontStashWindowsFallbackPath( windowsFallbackPath, sizeof( windowsFallbackPath ) ) );

	r_fontStash.primarySansFace = R_GetFontStashFace( R_FONTSTASH_FACE_SANS );
	r_fontStash.fallbackSansFace = R_GetFontStashFace( R_FONTSTASH_FACE_SANS_FALLBACK );
	r_fontStash.windowsFallbackFace = R_GetFontStashFace( R_FONTSTASH_FACE_SANS_WINDOWS_FALLBACK );

	if ( r_fontStash.windowsFallbackFace && !r_fontStash.windowsFallbackFace->loaded ) {
		r_fontStash.windowsFallbackFace = r_fontStash.fallbackSansFace;
	}
}

/*
=================
R_GetFontStashFaceForHandle
=================
*/
static rFontStashFace_t *R_GetFontStashFaceForHandle( int fontHandle ) {
	rFontStashFace_t *face = NULL;

	switch ( fontHandle ) {
		case R_FONTSTASH_FACE_SANS:
			face = r_fontStash.primarySansFace;
			break;

		case R_FONTSTASH_FACE_MONO:
			face = R_GetFontStashFace( R_FONTSTASH_FACE_MONO );
			break;

		case R_FONTSTASH_FACE_SANS_FALLBACK:
			face = r_fontStash.fallbackSansFace;
			break;

		case R_FONTSTASH_FACE_SANS_WINDOWS_FALLBACK:
			face = r_fontStash.windowsFallbackFace;
			break;

		case R_FONTSTASH_FACE_NORMAL:
		default:
			face = R_GetFontStashFace( R_FONTSTASH_FACE_NORMAL );
			break;
	}

	if ( !face || !face->loaded ) {
		face = R_GetFontStashFace( R_FONTSTASH_FACE_NORMAL );
	}

	if ( ( !face || !face->loaded ) && r_fontStash.primarySansFace && r_fontStash.primarySansFace->loaded ) {
		face = r_fontStash.primarySansFace;
	}

	return face;
}

/*
=================
R_EnsureFontStashCompatibilityFont
=================
*/
static qboolean R_EnsureFontStashCompatibilityFont( rFontStashFace_t *face ) {
	if ( !face || !face->loaded ) {
		return qfalse;
	}

	if ( face->compatFontLoaded ) {
		return qtrue;
	}

	Com_Memset( &face->compatFont, 0, sizeof( face->compatFont ) );
	RE_RegisterFont( face->resolvedPath, R_FONTSTASH_POINT_SIZE, &face->compatFont );
	if ( !face->compatFont.name[0] ) {
		return qfalse;
	}

	face->compatFontLoaded = qtrue;
	return qtrue;
}

#ifdef BUILD_FREETYPE
/*
=================
R_AllocateFontStashGlyphRect
=================
*/
static qboolean R_AllocateFontStashGlyphRect( int width, int height, int *x, int *y ) {
	if ( width <= 0 || height <= 0 ) {
		if ( x ) {
			*x = 0;
		}
		if ( y ) {
			*y = 0;
		}
		return qtrue;
	}

	if ( width + R_FONTSTASH_PADDING > r_fontStash.width || height + R_FONTSTASH_PADDING > r_fontStash.height ) {
		if ( r_fontStash.errorCallback ) {
			r_fontStash.errorCallback( &r_fontStash, R_FONTSTASH_ERROR_ATLAS_FULL, 0 );
		}
		return qfalse;
	}

	if ( r_fontStash.nextX + width + R_FONTSTASH_PADDING > r_fontStash.width ) {
		r_fontStash.nextX = 0;
		r_fontStash.nextY += r_fontStash.rowHeight + R_FONTSTASH_PADDING;
		r_fontStash.rowHeight = 0;
	}

	if ( r_fontStash.nextY + height + R_FONTSTASH_PADDING > r_fontStash.height ) {
		if ( r_fontStash.errorCallback ) {
			r_fontStash.errorCallback( &r_fontStash, R_FONTSTASH_ERROR_ATLAS_FULL, 0 );
		}
		return qfalse;
	}

	if ( x ) {
		*x = r_fontStash.nextX;
	}
	if ( y ) {
		*y = r_fontStash.nextY;
	}

	r_fontStash.nextX += width + R_FONTSTASH_PADDING;
	if ( height > r_fontStash.rowHeight ) {
		r_fontStash.rowHeight = height;
	}

	return qtrue;
}

/*
=================
R_CopyFontStashBitmap
=================
*/
static void R_CopyFontStashBitmap( const FT_Bitmap *bitmap, int x, int y ) {
	int copyWidth;
	int sourcePitch;
	int row;

	if ( !bitmap || !bitmap->buffer || !r_fontStash.buffer ) {
		return;
	}

	copyWidth = bitmap->width;
	sourcePitch = ( bitmap->pitch < 0 ) ? -bitmap->pitch : bitmap->pitch;
	if ( copyWidth <= 0 || sourcePitch <= 0 ) {
		return;
	}
	if ( copyWidth > sourcePitch ) {
		copyWidth = sourcePitch;
	}

	for ( row = 0; row < bitmap->rows; row++ ) {
		Com_Memcpy(
			r_fontStash.buffer + ( ( y + row ) * r_fontStash.width ) + x,
			bitmap->buffer + ( row * sourcePitch ),
			copyWidth );
	}
}

/*
=================
R_FontStashFaceSupportsCodepoint
=================
*/
static qboolean R_FontStashFaceSupportsCodepoint( rFontStashFace_t *face, unsigned int codepoint ) {
	if ( !face || !face->ftFace ) {
		return qfalse;
	}

	return ( FT_Get_Char_Index( face->ftFace, codepoint ) != 0 );
}

/*
=================
R_SetFontStashFaceSize
=================
*/
static qboolean R_SetFontStashFaceSize( rFontStashFace_t *face, int scaleTenths ) {
	FT_F26Dot6 charSize;

	if ( !face || !face->ftFace ) {
		return qfalse;
	}

	charSize = ( scaleTenths * 64 + 5 ) / 10;
	if ( charSize <= 0 ) {
		charSize = 1;
	}

	return ( FT_Set_Char_Size( face->ftFace, 0, charSize, 72, 72 ) == 0 );
}

/*
=================
R_RoundFontStashMetric
=================
*/
static int R_RoundFontStashMetric( FT_Pos value ) {
	if ( value >= 0 ) {
		return (int)( ( value + 32 ) >> 6 );
	}

	return -(int)( ( ( -value ) + 32 ) >> 6 );
}

/*
=================
R_GetFontStashFaceMetrics
=================
*/
static qboolean R_GetFontStashFaceMetrics( rFontStashFace_t *face, int scaleTenths, rFontStashFaceMetrics_t *outMetrics ) {
	if ( outMetrics ) {
		Com_Memset( outMetrics, 0, sizeof( *outMetrics ) );
	}

	if ( !face || !face->ftFace || !face->ftFace->size || !outMetrics ) {
		return qfalse;
	}

	if ( !R_SetFontStashFaceSize( face, scaleTenths ) ) {
		return qfalse;
	}

	outMetrics->ascent = R_RoundFontStashMetric( face->ftFace->size->metrics.ascender );
	outMetrics->descent = R_RoundFontStashMetric( face->ftFace->size->metrics.descender );
	outMetrics->lineHeight = R_RoundFontStashMetric( face->ftFace->size->metrics.height );
	if ( outMetrics->lineHeight <= 0 ) {
		outMetrics->lineHeight = outMetrics->ascent - outMetrics->descent;
	}

	return qtrue;
}

/*
=================
R_CacheFontStashGlyph
=================
*/
static qboolean R_CacheFontStashGlyph( rFontStashFace_t *face, unsigned int codepoint, int scaleTenths, qboolean uploadAtlas, rFontStashGlyph_t **outGlyph ) {
	rFontStashGlyph_t *cachedGlyph;
	FT_Bitmap *bitmap;
	FT_GlyphSlot slot;
	FT_UInt glyphIndex;
	glyphInfo_t glyph;
	int x;
	int y;
	int attempt;

	if ( outGlyph ) {
		*outGlyph = NULL;
	}

	if ( !face || !face->ftFace || !r_fontStash.shader ) {
		return qfalse;
	}

	cachedGlyph = R_FindFontStashGlyph( face, codepoint, scaleTenths );
	if ( cachedGlyph ) {
		if ( outGlyph ) {
			*outGlyph = cachedGlyph;
		}
		return qtrue;
	}

	if ( !R_SetFontStashFaceSize( face, scaleTenths ) ) {
		return qfalse;
	}

	glyphIndex = FT_Get_Char_Index( face->ftFace, codepoint );
	if ( glyphIndex == 0 ) {
		return qfalse;
	}

	if ( FT_Load_Glyph( face->ftFace, glyphIndex, FT_LOAD_DEFAULT ) != 0 ) {
		return qfalse;
	}

	slot = face->ftFace->glyph;
	Com_Memset( &glyph, 0, sizeof( glyph ) );
	bitmap = R_RenderGlyph( slot, &glyph );
	if ( !bitmap ) {
		return qfalse;
	}

	glyph.xSkip = R_RoundFontStashMetric( slot->metrics.horiAdvance );
	if ( glyph.xSkip < 0 ) {
		glyph.xSkip = 0;
	}
	glyph.imageWidth = bitmap->width;
	glyph.imageHeight = bitmap->rows;

	x = 0;
	y = 0;
	for ( attempt = 0; attempt < 2; attempt++ ) {
		if ( R_AllocateFontStashGlyphRect( glyph.imageWidth, glyph.imageHeight, &x, &y ) ) {
			break;
		}
	}

	if ( attempt == 2 ) {
		Z_Free( bitmap->buffer );
		Z_Free( bitmap );
		return qfalse;
	}

	if ( !R_EnsureFontStashGlyphCapacity( face, face->hostGlyphCount + 1 ) ) {
		Z_Free( bitmap->buffer );
		Z_Free( bitmap );
		return qfalse;
	}

	cachedGlyph = &face->hostGlyphs[face->hostGlyphCount];
	Com_Memset( cachedGlyph, 0, sizeof( *cachedGlyph ) );
	cachedGlyph->glyph = glyph;
	cachedGlyph->hostGlyph.left = slot->bitmap_left;
	cachedGlyph->hostGlyph.right = slot->bitmap_left + bitmap->width;
	cachedGlyph->hostGlyph.top = slot->bitmap_top;
	cachedGlyph->hostGlyph.bottom = slot->bitmap_top - bitmap->rows;
	cachedGlyph->hostGlyph.xAdvance = glyph.xSkip;

	if ( glyph.imageWidth > 0 && glyph.imageHeight > 0 ) {
		R_CopyFontStashBitmap( bitmap, x, y );
		cachedGlyph->glyph.s = (float)x / r_fontStash.width;
		cachedGlyph->glyph.t = (float)y / r_fontStash.height;
		cachedGlyph->glyph.s2 = (float)( x + glyph.imageWidth ) / r_fontStash.width;
		cachedGlyph->glyph.t2 = (float)( y + glyph.imageHeight ) / r_fontStash.height;
	}

	cachedGlyph->codepoint = codepoint;
	cachedGlyph->scaleTenths = (short)scaleTenths;
	cachedGlyph->glyph.glyph = r_fontStash.shader;
	face->hostGlyphCount++;

	Z_Free( bitmap->buffer );
	Z_Free( bitmap );

	if ( uploadAtlas && r_fontStash.image ) {
		R_UploadFontStashAtlas();
	}

	if ( outGlyph ) {
		*outGlyph = cachedGlyph;
	}

	return qtrue;
}

#endif

/*
=================
R_GetResolvedGlyphBounds
=================
*/
static void R_GetResolvedGlyphBounds( glyphInfo_t *glyph, const rFontStashResolvedGlyph_t *resolvedGlyph, float *outLeft, float *outRight, float *outTop, float *outBottom, float *outAdvance ) {
	const rFontStashHostGlyph_t *hostGlyph;
	float scaleFactor;

	hostGlyph = resolvedGlyph ? resolvedGlyph->hostGlyph : NULL;
	scaleFactor = resolvedGlyph ? resolvedGlyph->scaleFactor : 1.0f;

	if ( outLeft ) {
		*outLeft = 0.0f;
	}
	if ( outRight ) {
		*outRight = 0.0f;
	}
	if ( outTop ) {
		*outTop = 0.0f;
	}
	if ( outBottom ) {
		*outBottom = 0.0f;
	}
	if ( outAdvance ) {
		*outAdvance = 0.0f;
	}

	if ( !glyph ) {
		return;
	}

	if ( hostGlyph ) {
		if ( outLeft ) {
			*outLeft = hostGlyph->left * scaleFactor;
		}
		if ( outRight ) {
			*outRight = hostGlyph->right * scaleFactor;
		}
		if ( outTop ) {
			*outTop = hostGlyph->top * scaleFactor;
		}
		if ( outBottom ) {
			*outBottom = hostGlyph->bottom * scaleFactor;
		}
		if ( outAdvance ) {
			*outAdvance = hostGlyph->xAdvance * scaleFactor;
		}
		return;
	}

	if ( outRight ) {
		*outRight = glyph->imageWidth * scaleFactor;
	}
	if ( outTop ) {
		*outTop = glyph->top * scaleFactor;
	}
	if ( outBottom ) {
		*outBottom = glyph->bottom * scaleFactor;
	}
	if ( outAdvance ) {
		*outAdvance = glyph->xSkip * scaleFactor;
	}
}

/*
=================
R_GetFontStashGlyph
=================
*/
static glyphInfo_t *R_GetFontStashGlyph( rFontStashFace_t *face, unsigned int codepoint, int scaleTenths, rFontStashResolvedGlyph_t *resolvedGlyph ) {
	rFontStashResolvedGlyph_t localResolvedGlyph;

	if ( !resolvedGlyph ) {
		resolvedGlyph = &localResolvedGlyph;
	}

	resolvedGlyph->glyph = NULL;
	resolvedGlyph->hostGlyph = NULL;
	resolvedGlyph->scaleFactor = 1.0f;

	if ( !face ) {
		return NULL;
	}

#ifdef BUILD_FREETYPE
	if ( r_fontStash.shader ) {
		rFontStashFace_t *faceChain[4];
		int faceCount;
		int i;

		faceCount = R_BuildFontStashFaceChain( face, faceChain, ARRAY_LEN( faceChain ) );
		for ( i = 0; i < faceCount; i++ ) {
			rFontStashFace_t *candidateFace;
			rFontStashGlyph_t *cachedGlyph;

			candidateFace = faceChain[i];
			if ( !candidateFace || !candidateFace->ftFace ) {
				continue;
			}

			cachedGlyph = R_FindFontStashGlyph( candidateFace, codepoint, scaleTenths );
			if ( cachedGlyph ) {
				resolvedGlyph->glyph = &cachedGlyph->glyph;
				resolvedGlyph->hostGlyph = &cachedGlyph->hostGlyph;
				return resolvedGlyph->glyph;
			}

			if ( !R_FontStashFaceSupportsCodepoint( candidateFace, codepoint ) ) {
				continue;
			}

			if ( R_CacheFontStashGlyph( candidateFace, codepoint, scaleTenths, qtrue, &cachedGlyph ) ) {
				resolvedGlyph->glyph = &cachedGlyph->glyph;
				resolvedGlyph->hostGlyph = &cachedGlyph->hostGlyph;
				return resolvedGlyph->glyph;
			}
		}
	}
#endif

	/*
	 * Retail host DrawScaledText/MeasureText resolve glyphs from the retained
	 * *fontstash face table first and only fall back to the classic cached-font
	 * lane when the retained atlas path is unavailable for the requested face.
	 */
	if ( codepoint <= GLYPH_END && R_EnsureFontStashCompatibilityFont( face ) ) {
		resolvedGlyph->glyph = &face->compatFont.glyphs[codepoint];
		resolvedGlyph->scaleFactor = ( (float)scaleTenths / 10.0f ) / R_FONTSTASH_POINT_SIZE;
		return resolvedGlyph->glyph;
	}

	return NULL;
}

/*
=================
R_GetFontStashDebugInfo
=================
*/
qboolean R_GetFontStashDebugInfo( image_t **image, int *width, int *height ) {
	if ( image ) {
		*image = r_fontStash.image;
	}
	if ( width ) {
		*width = r_fontStash.width;
	}
	if ( height ) {
		*height = r_fontStash.height;
	}

	return ( r_fontStash.image != NULL && r_fontStash.shader != 0 );
}

/*
=================
RE_GetScaledFontMetrics
=================
*/
qboolean RE_GetScaledFontMetrics( int fontHandle, float scale, float *outAscent, float *outDescent, float *outLineHeight ) {
	rFontStashFace_t *face;
	int scaleTenths;

	if ( outAscent ) {
		*outAscent = 0.0f;
	}
	if ( outDescent ) {
		*outDescent = 0.0f;
	}
	if ( outLineHeight ) {
		*outLineHeight = 0.0f;
	}

	face = R_GetFontStashFaceForHandle( fontHandle );
	scaleTenths = R_GetFontStashScaleTenths( scale );

#ifdef BUILD_FREETYPE
	if ( face && face->ftFace ) {
		rFontStashFaceMetrics_t metrics;

		if ( R_GetFontStashFaceMetrics( face, scaleTenths, &metrics ) ) {
			if ( outAscent ) {
				*outAscent = (float)metrics.ascent;
			}
			if ( outDescent ) {
				*outDescent = (float)metrics.descent;
			}
			if ( outLineHeight ) {
				*outLineHeight = (float)metrics.lineHeight;
			}
			return qtrue;
		}
	}
#endif

	if ( face && R_EnsureFontStashCompatibilityFont( face ) ) {
		const glyphInfo_t *compatGlyph;
		float scaleFactor;

		compatGlyph = &face->compatFont.glyphs['A'];
		scaleFactor = ( (float)scaleTenths / 10.0f ) / R_FONTSTASH_POINT_SIZE;

		if ( outAscent ) {
			*outAscent = compatGlyph->top * scaleFactor;
		}
		if ( outDescent ) {
			*outDescent = compatGlyph->bottom * scaleFactor;
		}
		if ( outLineHeight ) {
			*outLineHeight = ( compatGlyph->top - compatGlyph->bottom ) * scaleFactor;
		}
		return qtrue;
	}

	return qfalse;
}

/*
=================
RE_DrawScaledText
=================
*/
void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor ) {
	rFontStashFace_t *face;
	const char *s;
	const char *end;
	vec4_t currentColor;
	float penX;
	int scaleTenths;
	qboolean hasMaxX;
	float maxXf;

	if ( outMaxX ) {
		*outMaxX = (float)x;
	}

	if ( !text || !text[0] ) {
		return;
	}

	if ( baseColor ) {
		Com_Memcpy( currentColor, baseColor, sizeof( currentColor ) );
	} else {
		currentColor[0] = 1.0f;
		currentColor[1] = 1.0f;
		currentColor[2] = 1.0f;
		currentColor[3] = 1.0f;
	}

	face = R_GetFontStashFaceForHandle( fontHandle );
	scaleTenths = R_GetFontStashScaleTenths( scale );
	penX = (float)x;
	hasMaxX = ( maxX > 0 );
	maxXf = (float)maxX;
	end = text + strlen( text );

	RE_SetColor( currentColor );

	for ( s = text; s < end && *s; ) {
		rFontStashResolvedGlyph_t resolvedGlyph;
		unsigned int codepoint;
		const char *next;
		glyphInfo_t *glyph;
		float advance;
		float drawBottom;
		float drawLeft;
		float drawRight;
		float drawTop;
		float glyphMaxX;
		float quadHeight;
		float quadWidth;
		vec4_t newColor;
		int colorIndex;
		const char *colorNext;

		if ( R_ParseHostTextColorEscape( s, end, &colorIndex, &colorNext ) ) {
			if ( !forceColor ) {
				Com_Memcpy( newColor, g_color_table[colorIndex], sizeof( newColor ) );
				newColor[3] = currentColor[3];
				RE_SetColor( newColor );
			}
			s = colorNext;
			continue;
		}

		next = R_DecodeFontStashCodepoint( s, end, &codepoint );
		if ( next <= s ) {
			break;
		}

		glyph = R_GetFontStashGlyph( face, codepoint, scaleTenths, &resolvedGlyph );
		if ( !glyph ) {
			s = next;
			continue;
		}

		R_GetResolvedGlyphBounds( glyph, &resolvedGlyph, &drawLeft, &drawRight, &drawTop, &drawBottom, &advance );
		glyphMaxX = penX + advance;
		if ( penX + drawRight > glyphMaxX ) {
			glyphMaxX = penX + drawRight;
		}
		if ( hasMaxX && glyphMaxX > maxXf ) {
			if ( outMaxX ) {
				*outMaxX = 0.0f;
			}
			break;
		}

		quadWidth = drawRight - drawLeft;
		quadHeight = drawTop - drawBottom;
		if ( glyph->imageWidth > 0 && glyph->imageHeight > 0 && quadWidth > 0.0f && quadHeight > 0.0f ) {
			RE_StretchPic(
				penX + drawLeft,
				(float)y - drawTop,
				quadWidth,
				quadHeight,
				glyph->s,
				glyph->t,
				glyph->s2,
				glyph->t2,
				glyph->glyph );
		}

		penX += advance;
		s = next;
		if ( outMaxX ) {
			*outMaxX = glyphMaxX;
		}
	}

	RE_SetColor( currentColor );
}

/*
=================
RE_MeasureScaledText
=================
*/
void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft ) {
	rFontStashFace_t *face;
	const char *s;
	qboolean hasBounds;
	float width;
	float height;
	float maxBottom;
	float maxRight;
	float minLeft;
	float minTop;
	float penX;
	int scaleTenths;
	qboolean hasMaxX;
	float maxXf;

	if ( outWidth ) {
		*outWidth = 0.0f;
	}
	if ( outHeight ) {
		*outHeight = 0.0f;
	}
	if ( outLeft ) {
		*outLeft = 0.0f;
	}

	if ( !text ) {
		return;
	}

	face = R_GetFontStashFaceForHandle( fontHandle );
	scaleTenths = R_GetFontStashScaleTenths( scale );
	width = 0.0f;
	height = 0.0f;
	penX = 0.0f;
	hasBounds = qfalse;
	minLeft = 0.0f;
	maxRight = 0.0f;
	minTop = 0.0f;
	maxBottom = 0.0f;
	hasMaxX = ( maxX > 0 );
	maxXf = (float)maxX;

	for ( s = text; *s && ( !end || s < end ); ) {
		rFontStashResolvedGlyph_t resolvedGlyph;
		unsigned int codepoint;
		const char *next;
		glyphInfo_t *glyph;
		float advance;
		float drawBottom;
		float drawLeft;
		float drawRight;
		float drawTop;
		float glyphLeft;
		float glyphMaxX;
		float glyphRight;
		int colorIndex;
		const char *colorNext;

		if ( R_ParseHostTextColorEscape( s, end, &colorIndex, &colorNext ) ) {
			s = colorNext;
			continue;
		}

		next = R_DecodeFontStashCodepoint( s, end, &codepoint );
		if ( next <= s ) {
			break;
		}

		glyph = R_GetFontStashGlyph( face, codepoint, scaleTenths, &resolvedGlyph );
		if ( !glyph ) {
			s = next;
			continue;
		}

		R_GetResolvedGlyphBounds( glyph, &resolvedGlyph, &drawLeft, &drawRight, &drawTop, &drawBottom, &advance );
		glyphRight = penX + drawRight;
		glyphMaxX = penX + advance;
		if ( glyphRight > glyphMaxX ) {
			glyphMaxX = glyphRight;
		}
		if ( hasMaxX && glyphMaxX > maxXf ) {
			break;
		}

		glyphLeft = penX + drawLeft;
		if ( glyph->imageWidth > 0 && glyph->imageHeight > 0 ) {
			if ( !hasBounds ) {
				hasBounds = qtrue;
				minLeft = glyphLeft;
				maxRight = glyphRight;
				minTop = -drawTop;
				maxBottom = -drawBottom;
			} else {
				if ( glyphLeft < minLeft ) {
					minLeft = glyphLeft;
				}
				if ( glyphRight > maxRight ) {
					maxRight = glyphRight;
				}
				if ( -drawTop < minTop ) {
					minTop = -drawTop;
				}
				if ( -drawBottom > maxBottom ) {
					maxBottom = -drawBottom;
				}
			}
		}

		penX += advance;
		width = penX;
		if ( maxRight > width ) {
			width = maxRight;
		}
		if ( hasBounds ) {
			height = maxBottom - minTop;
		}
		s = next;
	}

	if ( outWidth ) {
		*outWidth = width;
	}
	if ( outHeight ) {
		*outHeight = height;
	}
	if ( outLeft ) {
		*outLeft = hasBounds ? minLeft : 0.0f;
	}
}

/*
=================
RE_RegisterFontFallback

Source-compatibility fallback used when cached or FreeType-backed font data is unavailable.
=================
*/
static qboolean RE_RegisterFontFallback( const char *cacheName, float glyphScale, fontInfo_t *font ) {
	const char *shaderName;
	qhandle_t glyphShader;
	float cell;
	int i;

	glyphShader = RE_RegisterShaderNoMip( "gfx/2d/bigchars" );
	shaderName = "gfx/2d/bigchars";
	if ( !glyphShader ) {
		glyphShader = RE_RegisterShaderNoMip( "white" );
		shaderName = "white";
	}

	if ( !glyphShader ) {
		return qfalse;
	}

	Com_Memset( font, 0, sizeof( *font ) );
	cell = 1.0f / R_COMPAT_FONT_GRID_SIZE;

	for ( i = GLYPH_START; i <= GLYPH_END; i++ ) {
		glyphInfo_t *glyph;
		int row;
		int col;

		glyph = &font->glyphs[i];
		row = ( i >> 4 ) & ( R_COMPAT_FONT_GRID_SIZE - 1 );
		col = i & ( R_COMPAT_FONT_GRID_SIZE - 1 );

		glyph->height = R_COMPAT_FONT_CELL_SIZE;
		glyph->top = R_COMPAT_FONT_TOP;
		glyph->bottom = R_COMPAT_FONT_BOTTOM;
		glyph->pitch = R_COMPAT_FONT_CELL_SIZE;
		glyph->xSkip = R_COMPAT_FONT_CELL_SIZE;
		glyph->imageWidth = R_COMPAT_FONT_CELL_SIZE;
		glyph->imageHeight = R_COMPAT_FONT_CELL_SIZE;
		glyph->s = col * cell;
		glyph->t = row * cell;
		glyph->s2 = glyph->s + cell;
		glyph->t2 = glyph->t + cell;
		glyph->glyph = glyphShader;
		Q_strncpyz( glyph->shaderName, shaderName, sizeof( glyph->shaderName ) );
	}

	font->glyphScale = glyphScale;
	Q_strncpyz( font->name, cacheName, sizeof( font->name ) );
	Com_Memcpy( &registeredFont[registeredFontCount++], font, sizeof( fontInfo_t ) );
	ri.Printf( PRINT_ALL, "RE_RegisterFont: using built-in glyph fallback via '%s'\n", shaderName );
	return qtrue;
}

#ifdef BUILD_FREETYPE
/*
=================
R_FlushFontAtlasPage

Retail-backed classic font atlas flush: one 256x256 page becomes one shader
handle shared by the glyphs emitted onto that page.
=================
*/
static void R_FlushFontAtlasPage( const char *fontName, int pointSize, int imageNumber, fontInfo_t *font, int firstGlyph, int lastGlyph, byte *out ) {
	int j;
	int k;
	int left;
	float max;
	byte *imageBuff;
	image_t *image;
	qhandle_t h;
	char pageName[MAX_QPATH];

	if ( firstGlyph > lastGlyph ) {
		return;
	}

	imageBuff = Z_Malloc( R_FONT_ATLAS_PIXEL_COUNT * 4 );
	left = 0;
	max = 0;
	for ( k = 0; k < R_FONT_ATLAS_PIXEL_COUNT; k++ ) {
		if ( max < out[k] ) {
			max = out[k];
		}
	}

	if ( max > 0 ) {
		max = 255 / max;
	}

	for ( k = 0; k < R_FONT_ATLAS_PIXEL_COUNT; k++ ) {
		imageBuff[left++] = 255;
		imageBuff[left++] = 255;
		imageBuff[left++] = 255;
		imageBuff[left++] = (byte)( (float)out[k] * max );
	}

	R_BuildFontPageName( fontName, pointSize, imageNumber, pageName, sizeof( pageName ) );
	if ( r_saveFontData->integer ) {
		WriteTGA( pageName, imageBuff, R_FONT_ATLAS_SIZE, R_FONT_ATLAS_SIZE );
	}

	image = R_CreateImage( pageName, imageBuff, R_FONT_ATLAS_SIZE, R_FONT_ATLAS_SIZE, qfalse, qfalse, GL_CLAMP );
	h = RE_RegisterShaderFromImage( pageName, LIGHTMAP_2D, image, qfalse );
	for ( j = firstGlyph; j <= lastGlyph; j++ ) {
		font->glyphs[j].glyph = h;
		Q_strncpyz( font->glyphs[j].shaderName, pageName, sizeof( font->glyphs[j].shaderName ) );
	}

	Z_Free( imageBuff );
}
#endif

/*
=================
RE_RegisterFont

Renderer font registration implementation used by the UI/cgame import lanes.
Retail Quake Live no longer proves this function as part of the GetRefAPI export tail.
=================
*/
void RE_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {
#ifdef BUILD_FREETYPE
	FT_Face face;
	int xOut, yOut, lastStart, imageNumber;
	int maxHeight;
	int len;
	unsigned char *out;
	glyphInfo_t *glyph;
	char resolvedFontName[MAX_QPATH];
	qboolean faceDataFromFileSystem = qfalse;
#endif
	void *faceData = NULL;
	int i;
	int registeredIndex;
	const char *loadName = NULL;
	char cacheName[MAX_QPATH];
	char legacyCacheName[MAX_QPATH];
	float dpi = 72;
	float glyphScale = 72.0f / dpi;

	if ( !fontName || !fontName[0] ) {
		fontName = "fonts/font";
	}

	if ( pointSize <= 0 ) {
		pointSize = 12;
	}

	glyphScale *= 48.0f / pointSize;

	R_SyncRenderThread();

	if ( registeredFontCount >= MAX_FONTS ) {
		ri.Printf( PRINT_ALL, "RE_RegisterFont: Too many fonts registered already.\n" );
		return;
	}

	R_BuildFontCacheName( fontName, pointSize, cacheName, sizeof( cacheName ) );
	R_BuildLegacyFontCacheName( pointSize, legacyCacheName, sizeof( legacyCacheName ) );

	registeredIndex = R_FindRegisteredFont( cacheName );
	if ( registeredIndex < 0 && Q_stricmp( cacheName, legacyCacheName ) ) {
		// Preserve the point-size-only cache probe as explicit compatibility scaffolding until the retail cache helpers are fully mapped.
		registeredIndex = R_FindRegisteredFont( legacyCacheName );
	}

	if ( registeredIndex >= 0 ) {
		Com_Memcpy( font, &registeredFont[registeredIndex], sizeof( fontInfo_t ) );
		Q_strncpyz( font->name, cacheName, sizeof( font->name ) );
		return;
	}

	loadName = R_FindCachedFontDataName( cacheName, legacyCacheName );
	if ( loadName != NULL ) {
		ri.FS_ReadFile( loadName, &faceData );
		fdOffset = 0;
		fdFile = faceData;
		for ( i = 0; i < GLYPHS_PER_FONT; i++ ) {
			font->glyphs[i].height = readInt();
			font->glyphs[i].top = readInt();
			font->glyphs[i].bottom = readInt();
			font->glyphs[i].pitch = readInt();
			font->glyphs[i].xSkip = readInt();
			font->glyphs[i].imageWidth = readInt();
			font->glyphs[i].imageHeight = readInt();
			font->glyphs[i].s = readFloat();
			font->glyphs[i].t = readFloat();
			font->glyphs[i].s2 = readFloat();
			font->glyphs[i].t2 = readFloat();
			font->glyphs[i].glyph = readInt();
			Com_Memcpy( font->glyphs[i].shaderName, &fdFile[fdOffset], 32 );
			fdOffset += 32;
		}
		font->glyphScale = readFloat();
		Com_Memcpy( font->name, &fdFile[fdOffset], MAX_QPATH );
		Q_strncpyz( font->name, cacheName, sizeof( font->name ) );
		R_RegisterCachedFontShaders( font );
		Com_Memcpy( &registeredFont[registeredFontCount++], font, sizeof( fontInfo_t ) );
		ri.FS_FreeFile( faceData );
		return;
	}

#ifndef BUILD_FREETYPE
	ri.Printf( PRINT_ALL, "RE_RegisterFont: FreeType code not available for %s (%i)\n", fontName, pointSize );
	if ( RE_RegisterFontFallback( cacheName, glyphScale, font ) ) {
		return;
	}
	ri.Printf( PRINT_ALL, "RE_RegisterFont: built-in glyph fallback failed\n" );
#else
	if ( ftLibrary == NULL ) {
		ri.Printf( PRINT_ALL, "RE_RegisterFont: FreeType not initialized.\n" );
		return;
	}

	R_NormalizeFontSourcePath( fontName, resolvedFontName, sizeof( resolvedFontName ) );
	len = R_ReadFontFile( resolvedFontName, &faceData, &faceDataFromFileSystem );
	if ( len <= 0 ) {
		ri.Printf( PRINT_ALL, "RE_RegisterFont: Unable to read font file '%s'\n", resolvedFontName );
		return;
	}

	if ( FT_New_Memory_Face( ftLibrary, faceData, len, 0, &face ) ) {
		ri.Printf( PRINT_ALL, "RE_RegisterFont: FreeType2, unable to allocate new face.\n" );
		R_FreeFontFileBuffer( faceData, faceDataFromFileSystem );
		return;
	}

	if ( FT_Set_Char_Size( face, pointSize << 6, pointSize << 6, dpi, dpi ) ) {
		ri.Printf( PRINT_ALL, "RE_RegisterFont: FreeType2, Unable to set face char size.\n" );
		FT_Done_Face( face );
		R_FreeFontFileBuffer( faceData, faceDataFromFileSystem );
		return;
	}

	out = Z_Malloc( R_FONT_ATLAS_PIXEL_COUNT );
	if ( out == NULL ) {
		ri.Printf( PRINT_ALL, "RE_RegisterFont: Z_Malloc failure during output image creation.\n" );
		FT_Done_Face( face );
		R_FreeFontFileBuffer( faceData, faceDataFromFileSystem );
		return;
	}
	Com_Memset( out, 0, R_FONT_ATLAS_PIXEL_COUNT );

	maxHeight = 0;
	xOut = 0;
	yOut = 0;

	for ( i = GLYPH_START; i <= GLYPH_END; i++ ) {
		glyph = RE_ConstructGlyphInfo( out, &xOut, &yOut, &maxHeight, face, (unsigned char)i, qtrue );
	}

	xOut = 0;
	yOut = 0;
	i = GLYPH_START;
	lastStart = i;
	imageNumber = 0;

	while ( i <= GLYPH_END ) {
		glyph = RE_ConstructGlyphInfo( out, &xOut, &yOut, &maxHeight, face, (unsigned char)i, qfalse );

		if ( xOut == -1 || yOut == -1 ) {
			R_FlushFontAtlasPage( fontName, pointSize, imageNumber++, font, lastStart, i - 1, out );
			lastStart = i;
			Com_Memset( out, 0, R_FONT_ATLAS_PIXEL_COUNT );
			xOut = 0;
			yOut = 0;
			continue;
		}

		Com_Memcpy( &font->glyphs[i], glyph, sizeof( glyphInfo_t ) );
		if ( i == GLYPH_END ) {
			R_FlushFontAtlasPage( fontName, pointSize, imageNumber++, font, lastStart, i, out );
		}

		i++;
	}

	font->glyphScale = glyphScale;
	Q_strncpyz( font->name, cacheName, sizeof( font->name ) );
	Com_Memcpy( &registeredFont[registeredFontCount++], font, sizeof( fontInfo_t ) );

	if ( r_saveFontData->integer ) {
		ri.FS_WriteFile( cacheName, font, sizeof( fontInfo_t ) );
	}

	Z_Free( out );
	FT_Done_Face( face );
	R_FreeFontFileBuffer( faceData, faceDataFromFileSystem );
#endif
}



/*
=================
R_InitFreeType
=================
*/
void R_InitFreeType() {
#ifdef BUILD_FREETYPE
	if ( FT_Init_FreeType( &ftLibrary ) ) {
		ri.Printf( PRINT_ALL, "R_InitFreeType: Unable to initialize FreeType.\n" );
	}
#endif
	registeredFontCount = 0;
}

/*
=================
R_InitFontStash
=================
*/
void R_InitFontStash( void ) {
	Com_Memset( &r_fontStash, 0, sizeof( r_fontStash ) );
	r_fontStash.errorCallback = R_fonsErrorCallback;
	r_fontStash.width = R_FONTSTASH_INITIAL_WIDTH;
	r_fontStash.height = R_FONTSTASH_INITIAL_HEIGHT;
	r_fontStash.buffer = Z_Malloc( r_fontStash.width * r_fontStash.height );
	R_ClearFontStashAtlasBuffer();

	if ( !R_EnsureFontStashImage() ) {
		ri.Printf( PRINT_ALL, "R_InitFontStash: unable to create retained %s image\n", R_FONTSTASH_TEXTURE_NAME );
	}

	R_InitFontStashFaces();
}

/*
=================
R_DoneFontStash
=================
*/
void R_DoneFontStash( void ) {
	int i;

	for ( i = 0; i < R_FONTSTASH_FACE_COUNT; i++ ) {
		R_ResetFontStashFace( &r_fontStash.faces[i] );
	}

	if ( r_fontStash.buffer ) {
		Z_Free( r_fontStash.buffer );
	}

	Com_Memset( &r_fontStash, 0, sizeof( r_fontStash ) );
}

/*
=================
R_DoneFreeType
=================
*/
void R_DoneFreeType() {
#ifdef BUILD_FREETYPE
	if ( ftLibrary ) {
		FT_Done_FreeType( ftLibrary );
		ftLibrary = NULL;
	}
#endif
	registeredFontCount = 0;
}
