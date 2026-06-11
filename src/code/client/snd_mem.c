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

/*****************************************************************************
 * name:		snd_mem.c
 *
 * desc:		sound caching
 *
 * $Archive: /MissionPack/code/client/snd_mem.c $
 *
 *****************************************************************************/

#include "snd_local.h"

#define DEF_COMSOUNDMEGS "16"

/*
===============================================================================

memory management

===============================================================================
*/

static	sndBuffer	*buffer = NULL;
static	sndBuffer	*freelist = NULL;
static	int inUse = 0;
static	int totalInUse = 0;

short *sfxScratchBuffer = NULL;
sfx_t *sfxScratchPointer = NULL;
int	   sfxScratchIndex = 0;

void	SND_free(sndBuffer *v) {
	*(sndBuffer **)v = freelist;
	freelist = (sndBuffer*)v;
	inUse += sizeof(sndBuffer);
}

sndBuffer*	SND_malloc() {
	sndBuffer *v;
redo:
	if (freelist == NULL) {
		S_FreeOldestSound();
		goto redo;
	}

	inUse -= sizeof(sndBuffer);
	totalInUse += sizeof(sndBuffer);

	v = freelist;
	freelist = *(sndBuffer **)freelist;
	v->next = NULL;
	return v;
}

/*
=============
SND_shutdown
=============
*/
void SND_shutdown( void ) {
	if ( buffer ) {
		free( buffer );
		buffer = NULL;
	}

	if ( sfxScratchBuffer ) {
		free( sfxScratchBuffer );
		sfxScratchBuffer = NULL;
	}

	freelist = NULL;
	inUse = 0;
	totalInUse = 0;
	sfxScratchPointer = NULL;
	sfxScratchIndex = 0;
}

/*
=============
SND_setup
=============
*/
void SND_setup() {
	sndBuffer *p, *q;
	cvar_t	*cv;
	int scs;

	cv = Cvar_Get( "com_soundMegs", DEF_COMSOUNDMEGS, CVAR_LATCH | CVAR_ARCHIVE );

	scs = (cv->integer*1024);

	buffer = malloc(scs*sizeof(sndBuffer) );
	// allocate the stack based hunk allocator
	sfxScratchBuffer = malloc(SND_CHUNK_SIZE * sizeof(short) * 4);	//Hunk_Alloc(SND_CHUNK_SIZE * sizeof(short) * 4);
	sfxScratchPointer = NULL;
	sfxScratchIndex = 0;

	inUse = scs*sizeof(sndBuffer);
	totalInUse = 0;
	p = buffer;;
	q = p + scs;
	while (--q > p)
		*(sndBuffer **)q = q-1;
	
	*(sndBuffer **)q = NULL;
	freelist = p + scs - 1;

	Com_Printf("Sound memory manager started\n");
}

/*
===============================================================================

WAV loading

===============================================================================
*/

typedef enum {
	SFT_UNKNOWN = 0,
	SFT_WAV = 1,
	SFT_OGG = 2
} soundFileType_t;

/*
=============
S_ReadWavBytes

Reads from the open WAV handle using the retail FS_Read-based parsing contract.
=============
*/
static int S_ReadWavBytes( fileHandle_t file, void *dest, int count ) {
	if ( !file || !dest || count <= 0 ) {
		return 0;
	}

	return FS_Read( dest, count, file );
}

/*
=============
GetLittleShort
=============
*/
static short GetLittleShort( fileHandle_t file ) {
	short val = 0;

	if ( S_ReadWavBytes( file, &val, sizeof( val ) ) != sizeof( val ) ) {
		return 0;
	}

	return LittleShort( val );
}

/*
=============
GetLittleLong
=============
*/
static int GetLittleLong( fileHandle_t file ) {
	int val = 0;

	if ( S_ReadWavBytes( file, &val, sizeof( val ) ) != sizeof( val ) ) {
		return 0;
	}

	return LittleLong( val );
}

/*
=============
S_FindWavChunk

Returns the padded size of the next WAV chunk when its id matches `chunk`.
=============
*/
static int S_FindWavChunk( fileHandle_t file, const char *chunk ) {
	char	name[4];
	int		len;

	if ( S_ReadWavBytes( file, name, sizeof( name ) ) != sizeof( name ) ) {
		return 0;
	}

	len = GetLittleLong( file );
	if ( len < 0 ) {
		return 0;
	}

	if ( strncmp( name, chunk, sizeof( name ) ) ) {
		return 0;
	}

	return ( len + 1 ) & ~1;
}

/*
============
GetWavinfo
============
*/
static int GetWavinfo( fileHandle_t file, wavinfo_t *info ) {
	char		waveTag[4];
	int			dataLength;

	if ( !info ) {
		return 0;
	}

	Com_Memset( info, 0, sizeof( *info ) );

// find "RIFF" chunk
	if ( !S_FindWavChunk( file, "RIFF" ) || S_ReadWavBytes( file, waveTag, sizeof( waveTag ) ) != sizeof( waveTag )
		|| strncmp( waveTag, "WAVE", sizeof( waveTag ) ) )
	{
		return 0;
	}

// get "fmt " chunk
// DumpChunks ();

	if ( !S_FindWavChunk( file, "fmt " ) )
	{
		return 0;
	}
	info->format = GetLittleShort( file );
	info->channels = GetLittleShort( file );
	info->rate = GetLittleLong( file );
	GetLittleLong( file );
	GetLittleShort( file );
	info->width = GetLittleShort( file ) / 8;

	if (info->format != 1)
	{
		return 0;
	}


// find data chunk
	dataLength = S_FindWavChunk( file, "data" );
	if ( !dataLength )
	{
		return 0;
	}

	if ( info->width <= 0 ) {
		return 0;
	}

	info->samples = dataLength / info->width;

	return dataLength;
}

/*
=============
S_SoundFileTypeForPath

Classifies a sound path using the retail extension-only type mapping.
=============
*/
static soundFileType_t S_SoundFileTypeForPath( const char *name ) {
	const char	*dot;

	if ( !name ) {
		return SFT_UNKNOWN;
	}

	dot = Q_strrchr( name, '.' );
	if ( !dot || !*dot ) {
		return SFT_UNKNOWN;
	}

	if ( !Q_stricmp( dot, ".ogg" ) ) {
		return SFT_OGG;
	}

	if ( !Q_stricmp( dot, ".wav" ) ) {
		return SFT_WAV;
	}

	return SFT_UNKNOWN;
}

/*
=============
S_OpenSoundFile

Opens the requested sound path and retries with a default `.ogg` extension when
the original asset is missing, matching the retail sound-load path.
=============
*/
static qboolean S_OpenSoundFile( const char *name, char *resolvedName, int resolvedNameSize, fileHandle_t *file, int *outSize, soundFileType_t *fileType ) {
	if ( !name || !resolvedName || resolvedNameSize <= 0 || !file || !outSize || !fileType ) {
		return qfalse;
	}

	*file = 0;
	*outSize = 0;
	*fileType = S_SoundFileTypeForPath( name );

	Q_strncpyz( resolvedName, name, resolvedNameSize );
	*outSize = FS_FOpenFileRead( resolvedName, file, qtrue );
	if ( *file ) {
		return qtrue;
	}

	COM_DefaultExtension( resolvedName, resolvedNameSize, ".ogg" );
	if ( !Q_stricmp( resolvedName, name ) ) {
		return qfalse;
	}

	*fileType = SFT_OGG;
	*outSize = FS_FOpenFileRead( resolvedName, file, qtrue );
	return ( *file != 0 );
}

/*
================
ResampleSfx

resample / decimate to the current source rate
================
*/
static void ResampleSfx( sfx_t *sfx, int inrate, int inwidth, byte *data, qboolean compressed ) {
	int		outcount;
	int		srcsample;
	float	stepscale;
	int		i;
	int		sample, samplefrac, fracstep;
	int			part;
	sndBuffer	*chunk;
	
	stepscale = (float)inrate / dma.speed;	// this is usually 0.5, 1, or 2

	outcount = sfx->soundLength / stepscale;
	sfx->soundLength = outcount;

	samplefrac = 0;
	fracstep = stepscale * 256;
	chunk = sfx->soundData;

	for (i=0 ; i<outcount ; i++)
	{
		srcsample = samplefrac >> 8;
		samplefrac += fracstep;
		if( inwidth == 2 ) {
			sample = LittleShort ( ((short *)data)[srcsample] );
		} else {
			sample = (int)( (unsigned char)(data[srcsample]) - 128) << 8;
		}
		part  = (i&(SND_CHUNK_SIZE-1));
		if (part == 0) {
			sndBuffer	*newchunk;
			newchunk = SND_malloc();
			if (chunk == NULL) {
				sfx->soundData = newchunk;
			} else {
				chunk->next = newchunk;
			}
			chunk = newchunk;
		}

		chunk->sndChunk[part] = sample;
	}
}

/*
================
ResampleSfx

resample / decimate to the current source rate
================
*/
static int ResampleSfxRaw( short *sfx, int inrate, int inwidth, int samples, byte *data ) {
	int			outcount;
	int			srcsample;
	float		stepscale;
	int			i;
	int			sample, samplefrac, fracstep;
	
	stepscale = (float)inrate / dma.speed;	// this is usually 0.5, 1, or 2

	outcount = samples / stepscale;

	samplefrac = 0;
	fracstep = stepscale * 256;

	for (i=0 ; i<outcount ; i++)
	{
		srcsample = samplefrac >> 8;
		samplefrac += fracstep;
		if( inwidth == 2 ) {
			sample = LittleShort ( ((short *)data)[srcsample] );
		} else {
			sample = (int)( (unsigned char)(data[srcsample]) - 128) << 8;
		}
		sfx[i] = sample;
	}
	return outcount;
}

/*
================
S_LoadPCMSound

Stores decoded mono PCM data into the sound cache.
================
*/
static qboolean S_LoadPCMSound( sfx_t *sfx, const char *loadName, const wavinfo_t *info, byte *source ) {
	short	*samples;

	if ( info->width != 2 ) {
		Com_DPrintf( "WAV_Load: %s is not a 16-bit file\n", loadName );
	}

	if ( info->rate != 22050 ) {
		Com_DPrintf( "WAV_Load: %s is not a 22kHz file\n", loadName );
	}

	if ( info->samples <= 0 || info->width <= 0 || !source ) {
		return qfalse;
	}

	samples = Hunk_AllocateTempMemory(info->samples * sizeof(short) * 2);

	// each of these compression schemes works just fine
	// but the 16bit quality is much nicer and with a local
	// install assured we can rely upon the sound memory
	// manager to do the right thing for us and page
	// sound in as needed

	if( sfx->soundCompressed == qtrue) {
		sfx->soundCompressionMethod = 1;
		sfx->soundData = NULL;
		sfx->soundLength = ResampleSfxRaw( samples, info->rate, info->width, info->samples, source );
		S_AdpcmEncodeSound(sfx, samples);
#if 0
	} else if (info.samples>(SND_CHUNK_SIZE*16) && info.width >1) {
		sfx->soundCompressionMethod = 3;
		sfx->soundData = NULL;
		sfx->soundLength = ResampleSfxRaw( samples, info.rate, info.width, info.samples, source );
		encodeMuLaw( sfx, samples);
	} else if (info.samples>(SND_CHUNK_SIZE*6400) && info.width >1) {
		sfx->soundCompressionMethod = 2;
		sfx->soundData = NULL;
		sfx->soundLength = ResampleSfxRaw( samples, info.rate, info.width, info.samples, source );
		encodeWavelet( sfx, samples);
#endif
	} else {
		sfx->soundCompressionMethod = 0;
		sfx->soundLength = info->samples;
		sfx->soundData = NULL;
		ResampleSfx( sfx, info->rate, info->width, source, qfalse );
	}

	Hunk_FreeTempMemory(samples);
	return qtrue;
}

/*
================
S_LoadOggSound

Decodes a retail OGG sound effect and stores the resulting PCM.
================
*/
static qboolean S_LoadOggSound( sfx_t *sfx, const char *loadName, fileHandle_t file, int size ) {
	byte		*data;
	short		*oggPcm;
	wavinfo_t	info;
	qboolean	result;

	if ( size <= 0 ) {
		return qfalse;
	}

	data = Hunk_AllocateTempMemory( size );
	if ( !data ) {
		return qfalse;
	}

	if ( FS_Read( data, size, file ) != size ) {
		Hunk_FreeTempMemory( data );
		return qfalse;
	}

	oggPcm = NULL;
	if ( !S_VorbisDecodeMemory( loadName, data, size, &info, &oggPcm ) ) {
		Hunk_FreeTempMemory( data );
		return qfalse;
	}

	result = S_LoadPCMSound( sfx, loadName, &info, (byte *)oggPcm );
	Hunk_FreeTempMemory( oggPcm );
	Hunk_FreeTempMemory( data );
	return result;
}

/*
================
S_LoadWavSound

Parses a retail WAV sound effect and stores its PCM payload.
================
*/
static qboolean S_LoadWavSound( sfx_t *sfx, const char *loadName, fileHandle_t file ) {
	byte		*data;
	wavinfo_t	info;
	int			dataLength;
	qboolean	result;

	dataLength = GetWavinfo( file, &info );
	if ( info.channels != 1 ) {
		Com_Error( ERR_DROP, "%s is not a mono wav file", loadName );
		return qfalse;
	}

	if ( dataLength <= 0 ) {
		return qfalse;
	}

	data = Hunk_AllocateTempMemory( dataLength );
	if ( !data ) {
		return qfalse;
	}

	if ( FS_Read( data, dataLength, file ) != dataLength ) {
		Hunk_FreeTempMemory( data );
		return qfalse;
	}

	result = S_LoadPCMSound( sfx, loadName, &info, data );
	Hunk_FreeTempMemory( data );
	return result;
}

//=============================================================================

/*
==============
S_LoadSound

The filename may be different than sfx->name in the case
of a forced fallback of a player specific sound
==============
*/
qboolean S_LoadSound( sfx_t *sfx )
{
	fileHandle_t	file;
	int			 size;
	char		loadName[MAX_QPATH];
	soundFileType_t	fileType;
	qboolean	result;

	// player specific sounds are never directly loaded
	if ( sfx->soundName[0] == '*') {
		return qfalse;
	}

	// load it in
	if ( !S_OpenSoundFile( sfx->soundName, loadName, sizeof( loadName ), &file, &size, &fileType ) ) {
		return qfalse;
	}

	switch ( fileType ) {
	case SFT_WAV:
		result = S_LoadWavSound( sfx, loadName, file );
		break;
	case SFT_OGG:
		result = S_LoadOggSound( sfx, loadName, file, size );
		break;
	default:
		result = qfalse;
		break;
	}

	FS_FCloseFile( file );
	sfx->lastTimeUsed = Com_Milliseconds();

	return result;
}

void S_DisplayFreeMemory() {
	Com_Printf("%d bytes sound buffer memory in use, %d free \n", totalInUse, inUse);
}
