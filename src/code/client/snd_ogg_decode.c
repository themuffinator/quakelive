#include "snd_local.h"

#if QL_ENABLE_OGG
#include <vorbis/vorbisfile.h>
#include <limits.h>

#if defined(Q3_BIG_ENDIAN) || defined(__BIG_ENDIAN__)
#define SND_OGG_BIG_ENDIAN_OUTPUT 1
#else
#define SND_OGG_BIG_ENDIAN_OUTPUT 0
#endif

#define SND_OGG_DECODE_CHUNK	4096

typedef struct snd_vorbis_buffer_s {
	const byte	*data;
	int			length;
	int			position;
} snd_vorbis_buffer_t;

/*
=============
S_VorbisBufferRead

Feeds libvorbis from a memory buffer.
=============
*/
static size_t S_VorbisBufferRead( void *ptr, size_t size, size_t nmemb, void *datasource ) {
	snd_vorbis_buffer_t	*buffer;
	size_t					requested;
	size_t					available;
	size_t					count;

	buffer = (snd_vorbis_buffer_t *)datasource;
	if ( !buffer || !ptr || size == 0 ) {
		return 0;
	}

	requested = size * nmemb;
	if ( requested <= 0 ) {
		return 0;
	}

	available = buffer->length - buffer->position;
	if ( available <= 0 ) {
		return 0;
	}

	count = requested;
	if ( count > available ) {
		count = available;
	}

	Com_Memcpy( ptr, buffer->data + buffer->position, count );
	buffer->position += (int)count;

	return count / size;
}

/*
=============
S_VorbisBufferSeek

Supports absolute, relative, and end-relative seeks for the decoder.
=============
*/
static int S_VorbisBufferSeek( void *datasource, ogg_int64_t offset, int whence ) {
	snd_vorbis_buffer_t *buffer;
	int target;

	buffer = (snd_vorbis_buffer_t *)datasource;
	if ( !buffer ) {
		return -1;
	}

	switch ( whence ) {
	case SEEK_SET:
		target = (int)offset;
		break;
	case SEEK_CUR:
		target = buffer->position + (int)offset;
		break;
	case SEEK_END:
		target = buffer->length + (int)offset;
		break;
	default:
		return -1;
	}

	if ( target < 0 || target > buffer->length ) {
		return -1;
	}

	buffer->position = target;
	return 0;
}

/*
=============
S_VorbisBufferClose

Provided for the callback table even though there is no resource to free.
=============
*/
static int S_VorbisBufferClose( void *datasource ) {
	return 0;
}

/*
=============
S_VorbisBufferTell

Reports the decoder's current position inside the memory buffer.
=============
*/
static long S_VorbisBufferTell( void *datasource ) {
	snd_vorbis_buffer_t	*buffer;

	buffer = (snd_vorbis_buffer_t *)datasource;
	if ( !buffer ) {
		return -1;
	}

	return buffer->position;
}

/*
=============
S_VorbisDecodeMemory

Loads an entire Vorbis stream into a temporary PCM buffer.
=============
*/
qboolean S_VorbisDecodeMemory( const char *name, const byte *data, int length, wavinfo_t *info, short **outPcm ) {
	snd_vorbis_buffer_t		stream;
	ov_callbacks			callbacks;
	OggVorbis_File			vorbisFile;
	vorbis_info				*vorbisInfo;
	short					*pcm;
	short					*writePtr;
	byte					decodeChunk[SND_OGG_DECODE_CHUNK];
	int					bitstream;
	long					bytesRead;
	ogg_int64_t			totalSamples;
	int					channels;
	int					rate;
	int					i;
	int					samplePairs;
	short					*chunkSamples;

	if ( !info || !outPcm ) {
		return qfalse;
	}

	*outPcm = NULL;
	Com_Memset( info, 0, sizeof( *info ) );

	if ( !data || length <= 0 ) {
		return qfalse;
	}

	Com_Memset( &stream, 0, sizeof( stream ) );
	stream.data = data;
	stream.length = length;
	stream.position = 0;

	Com_Memset( &callbacks, 0, sizeof( callbacks ) );
	callbacks.read_func = S_VorbisBufferRead;
	callbacks.seek_func = S_VorbisBufferSeek;
	callbacks.close_func = S_VorbisBufferClose;
	callbacks.tell_func = S_VorbisBufferTell;

	if ( ov_open_callbacks( &stream, &vorbisFile, NULL, 0, callbacks ) < 0 ) {
		return qfalse;
	}

	vorbisInfo = ov_info( &vorbisFile, -1 );
	if ( !vorbisInfo ) {
		ov_clear( &vorbisFile );
		return qfalse;
	}

	channels = vorbisInfo->channels;
	rate = vorbisInfo->rate;
	if ( channels <= 0 || rate <= 0 ) {
		ov_clear( &vorbisFile );
		return qfalse;
	}

	if ( channels > 2 ) {
		Com_Printf( S_COLOR_YELLOW "WARNING: %s has %d channels and cannot be decoded\n", name ? name : "<unnamed>", channels );
		ov_clear( &vorbisFile );
		return qfalse;
	}

	totalSamples = ov_pcm_total( &vorbisFile, -1 );
	if ( totalSamples <= 0 || totalSamples > INT_MAX ) {
		ov_clear( &vorbisFile );
		return qfalse;
	}

	pcm = Hunk_AllocateTempMemory( (int)totalSamples * sizeof( short ) );
	if ( !pcm ) {
		ov_clear( &vorbisFile );
		return qfalse;
	}

	writePtr = pcm;
	info->samples = 0;
	bitstream = 0;

	while ( qtrue ) {
		bytesRead = ov_read( &vorbisFile, (char *)decodeChunk, sizeof( decodeChunk ), SND_OGG_BIG_ENDIAN_OUTPUT, 2, 1, &bitstream );
		if ( bytesRead == 0 ) {
			break;
		}
		if ( bytesRead < 0 ) {
			Hunk_FreeTempMemory( pcm );
			ov_clear( &vorbisFile );
			return qfalse;
		}

		samplePairs = bytesRead / ( channels * sizeof( short ) );
		chunkSamples = (short *)decodeChunk;

		for ( i = 0; i < samplePairs; i++ ) {
			if ( channels == 2 ) {
				*writePtr = (short)( ( (int)chunkSamples[i * 2] + (int)chunkSamples[i * 2 + 1] ) / 2 );
			} else {
				*writePtr = chunkSamples[i];
			}
			writePtr++;
			info->samples++;
		}
	}

	ov_clear( &vorbisFile );

	if ( info->samples <= 0 ) {
		Hunk_FreeTempMemory( pcm );
		return qfalse;
	}

	if ( channels == 2 ) {
		Com_DPrintf( S_COLOR_YELLOW "WARNING: %s is a stereo Vorbis file and was downmixed to mono\n", name ? name : "<unnamed>" );
	}

	info->format = WAV_FORMAT_PCM;
	info->channels = 1;
	info->width = 2;
	info->rate = rate;
	info->dataofs = 0;

	*outPcm = pcm;
	return qtrue;
}

#else

/*
=============
S_VorbisDecodeMemory

Vorbis decoding is disabled when QL_ENABLE_OGG is 0.
=============
*/
qboolean S_VorbisDecodeMemory( const char *name, const byte *data, int length, wavinfo_t *info, short **outPcm ) {
	return qfalse;
}

#endif
