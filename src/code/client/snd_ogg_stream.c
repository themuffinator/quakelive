#include "snd_ogg_stream.h"

#if QL_ENABLE_OGG

#if defined(Q3_BIG_ENDIAN) || defined(__BIG_ENDIAN__)
#define SND_OGG_BIG_ENDIAN_OUTPUT 1
#else
#define SND_OGG_BIG_ENDIAN_OUTPUT 0
#endif

/*
=============
S_OggResetInfo

Clears the cached format information for a stream.
=============
*/
static void S_OggResetInfo( snd_ogg_stream_t *stream ) {
	if ( !stream ) {
		return;
	}
	stream->channels = 0;
	stream->rate = 0;
	stream->width = 0;
	stream->active = qfalse;
}

/*
=============
S_OggClearFileHandle

Closes any open filesystem handle owned by the stream.
=============
*/
static void S_OggClearFileHandle( snd_ogg_stream_t *stream ) {
	if ( !stream ) {
		return;
	}
	if ( stream->handle ) {
		FS_FCloseFile( stream->handle );
		stream->handle = 0;
	}
}

/*
=============
S_OggReadCallback

Feeds the Vorbis decoder from the virtual filesystem.
=============
*/
static size_t S_OggReadCallback( void *ptr, size_t size, size_t nmemb, void *datasource ) {
	snd_ogg_stream_t *stream;
	int requested;
	int bytesRead;

	stream = (snd_ogg_stream_t *)datasource;
	if ( !stream || !stream->handle || !size ) {
		return 0;
	}
	requested = (int)( size * nmemb );
	bytesRead = FS_Read( ptr, requested, stream->handle );
	if ( bytesRead <= 0 ) {
		return 0;
	}
	return (size_t)( bytesRead / (int)size );
}

/*
=============
S_OggCloseCallback

Shuts down the filesystem handle when libvorbis releases the datasource.
=============
*/
static int S_OggCloseCallback( void *datasource ) {
	snd_ogg_stream_t *stream;

	stream = (snd_ogg_stream_t *)datasource;
	S_OggClearFileHandle( stream );
	return 0;
}

/*
=============
S_OggStreamOpen

Opens a Vorbis bitstream and caches its audio format.
=============
*/
qboolean S_OggStreamOpen( snd_ogg_stream_t *stream, const char *path ) {
	vorbis_info *info;

	if ( !stream || !path || !path[0] ) {
		return qfalse;
	}

	S_OggStreamClose( stream );
	Q_strncpyz( stream->path, path, sizeof( stream->path ) );

	if ( FS_FOpenFileRead( path, &stream->handle, qtrue ) <= 0 || !stream->handle ) {
		stream->handle = 0;
		stream->path[0] = '\0';
		return qfalse;
	}

	stream->callbacks.read_func = S_OggReadCallback;
	stream->callbacks.seek_func = NULL;
	stream->callbacks.close_func = S_OggCloseCallback;
	stream->callbacks.tell_func = NULL;

	if ( ov_open_callbacks( stream, &stream->vorbisFile, NULL, 0, stream->callbacks ) < 0 ) {
		S_OggClearFileHandle( stream );
		Com_Memset( &stream->vorbisFile, 0, sizeof( stream->vorbisFile ) );
		stream->path[0] = '\0';
		return qfalse;
	}

	info = ov_info( &stream->vorbisFile, -1 );
	if ( !info ) {
		S_OggStreamClose( stream );
		return qfalse;
	}

	stream->channels = info->channels;
	stream->rate = info->rate;
	stream->width = 2;
	stream->active = qtrue;

	return qtrue;
}

/*
=============
S_OggStreamClose

Releases any decoder and filesystem state associated with the stream.
=============
*/
void S_OggStreamClose( snd_ogg_stream_t *stream ) {
	if ( !stream ) {
		return;
	}
	if ( stream->active ) {
		ov_clear( &stream->vorbisFile );
	}
	S_OggClearFileHandle( stream );
	S_OggResetInfo( stream );
}

/*
=============
S_OggStreamRead

Pulls decoded PCM data into the caller supplied buffer.
=============
*/
int S_OggStreamRead( snd_ogg_stream_t *stream, byte *buffer, int bytesToRead ) {
	int total;
	int bitstream;
	long result;

	if ( !stream || !stream->active || !buffer || bytesToRead <= 0 ) {
		return 0;
	}

	total = 0;
	bitstream = 0;
	while ( total < bytesToRead ) {
		result = ov_read( &stream->vorbisFile, (char *)buffer + total, bytesToRead - total, SND_OGG_BIG_ENDIAN_OUTPUT, 2, 1, &bitstream );
		if ( result == 0 ) {
			break;
		}
		if ( result < 0 ) {
			return (int)result;
		}
		total += (int)result;
	}

	return total;
}

/*
=============
S_OggStreamRestart

Reopens the previously cached path so decoding restarts from the beginning.
=============
*/
qboolean S_OggStreamRestart( snd_ogg_stream_t *stream ) {
	if ( !stream || !stream->path[0] ) {
		return qfalse;
	}
	return S_OggStreamOpen( stream, stream->path );
}

/*
=============
S_OggStreamActive

Reports whether the stream currently has an open decoder.
=============
*/
qboolean S_OggStreamActive( const snd_ogg_stream_t *stream ) {
	if ( !stream ) {
		return qfalse;
	}
	return stream->active;
}

/*
=============
S_OggStreamRate
=============
*/
int S_OggStreamRate( const snd_ogg_stream_t *stream ) {
	if ( !stream ) {
		return 0;
	}
	return stream->rate;
}

/*
=============
S_OggStreamChannels
=============
*/
int S_OggStreamChannels( const snd_ogg_stream_t *stream ) {
	if ( !stream ) {
		return 0;
	}
	return stream->channels;
}

/*
=============
S_OggStreamWidth
=============
*/
int S_OggStreamWidth( const snd_ogg_stream_t *stream ) {
	if ( !stream ) {
		return 0;
	}
	return stream->width;
}

#else

/*
=============
S_OggStreamOpen

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
qboolean S_OggStreamOpen( snd_ogg_stream_t *stream, const char *path ) {
	return qfalse;
}

/*
=============
S_OggStreamClose

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
void S_OggStreamClose( snd_ogg_stream_t *stream ) {
	(void)stream;
}

/*
=============
S_OggStreamRead

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
int S_OggStreamRead( snd_ogg_stream_t *stream, byte *buffer, int bytesToRead ) {
	(void)stream;
	(void)buffer;
	(void)bytesToRead;
	return 0;
}

/*
=============
S_OggStreamRestart

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
qboolean S_OggStreamRestart( snd_ogg_stream_t *stream ) {
	(void)stream;
	return qfalse;
}

/*
=============
S_OggStreamActive

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
qboolean S_OggStreamActive( const snd_ogg_stream_t *stream ) {
	(void)stream;
	return qfalse;
}

/*
=============
S_OggStreamRate

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
int S_OggStreamRate( const snd_ogg_stream_t *stream ) {
	(void)stream;
	return 0;
}

/*
=============
S_OggStreamChannels

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
int S_OggStreamChannels( const snd_ogg_stream_t *stream ) {
	(void)stream;
	return 0;
}

/*
=============
S_OggStreamWidth

Stubbed when QL_ENABLE_OGG is 0.
=============
*/
int S_OggStreamWidth( const snd_ogg_stream_t *stream ) {
	(void)stream;
	return 0;
}

#endif
