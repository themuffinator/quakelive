#ifndef SND_OGG_STREAM_H
#define SND_OGG_STREAM_H

#include "../game/q_shared.h"
#include "../qcommon/qcommon.h"
#if QL_ENABLE_OGG
#include <vorbis/vorbisfile.h>
#endif

typedef struct snd_ogg_stream_s {
	fileHandle_t		handle;
#if QL_ENABLE_OGG
	OggVorbis_File	vorbisFile;
	ov_callbacks	callbacks;
#endif
	qboolean		active;
	int			channels;
	int			rate;
	int			width;
	char			path[MAX_QPATH];
} snd_ogg_stream_t;

qboolean S_OggStreamOpen( snd_ogg_stream_t *stream, const char *path );
void S_OggStreamClose( snd_ogg_stream_t *stream );
int S_OggStreamRead( snd_ogg_stream_t *stream, byte *buffer, int bytesToRead );
qboolean S_OggStreamRestart( snd_ogg_stream_t *stream );
qboolean S_OggStreamActive( const snd_ogg_stream_t *stream );
int S_OggStreamRate( const snd_ogg_stream_t *stream );
int S_OggStreamChannels( const snd_ogg_stream_t *stream );
int S_OggStreamWidth( const snd_ogg_stream_t *stream );

#endif
