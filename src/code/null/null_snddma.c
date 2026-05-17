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

// null_snddma.c
// silent DMA sink for compatibility-only hosts

#include "../client/snd_local.h"

#define SND_NULL_SAMPLEBITS 16
#define SND_NULL_SPEED 22050
#define SND_NULL_CHANNELS 2
#define SND_NULL_BUFFER_SAMPLES 0x8000

#if defined( DEDICATED ) || defined( C_ONLY )
dma_t	dma;
#endif

static byte	snd_nullBuffer[SND_NULL_BUFFER_SAMPLES * ( SND_NULL_SAMPLEBITS / 8 )];
static qboolean	snd_nullInited;
static int	snd_nullDmaPosition;
static int	snd_nullLastMilliseconds;

/*
================
SNDDMA_ClearNullState
================
*/
static void SNDDMA_ClearNullState( void ) {
	snd_nullInited = qfalse;
	snd_nullDmaPosition = 0;
	snd_nullLastMilliseconds = 0;
	Com_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );
	Com_Memset( &dma, 0, sizeof( dma ) );
}

/*
================
SNDDMA_Init
================
*/
qboolean SNDDMA_Init( void ) {
	Com_Memset( &dma, 0, sizeof( dma ) );
	Com_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );

	dma.channels = SND_NULL_CHANNELS;
	dma.samplebits = SND_NULL_SAMPLEBITS;
	dma.speed = SND_NULL_SPEED;
	dma.samples = SND_NULL_BUFFER_SAMPLES;
	dma.submission_chunk = 1;
	dma.buffer = snd_nullBuffer;

	snd_nullDmaPosition = 0;
	snd_nullLastMilliseconds = Sys_Milliseconds();
	snd_nullInited = qtrue;

	return qtrue;
}

/*
================
SNDDMA_GetDMAPos
================
*/
int	SNDDMA_GetDMAPos( void ) {
	int	currentMilliseconds;
	int	elapsedMilliseconds;
	int	sampleDelta;

	if ( !snd_nullInited ) {
		return 0;
	}

	currentMilliseconds = Sys_Milliseconds();
	elapsedMilliseconds = currentMilliseconds - snd_nullLastMilliseconds;
	if ( elapsedMilliseconds > 0 && dma.samples > 0 ) {
		sampleDelta = ( elapsedMilliseconds * dma.speed * dma.channels ) / 1000;
		snd_nullDmaPosition = ( snd_nullDmaPosition + sampleDelta ) % dma.samples;
		snd_nullLastMilliseconds = currentMilliseconds;
	}

	return snd_nullDmaPosition;
}

/*
================
SNDDMA_Shutdown
================
*/
void SNDDMA_Shutdown( void ) {
	SNDDMA_ClearNullState();
}

/*
================
SNDDMA_BeginPainting
================
*/
void SNDDMA_BeginPainting( void ) {
	if ( snd_nullInited ) {
		Com_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );
	}
}

/*
================
SNDDMA_Submit
================
*/
void SNDDMA_Submit( void ) {
}

/*
================
SNDDMA_Activate
================
*/
void SNDDMA_Activate( void ) {
}

/*
================
S_RegisterSound
================
*/
sfxHandle_t S_RegisterSound( const char *name, qboolean compressed ) {
	(void)name;
	(void)compressed;
	return 0;
}

/*
================
S_StartLocalSound
================
*/
void S_StartLocalSound( sfxHandle_t sfxHandle, int channelNum ) {
	(void)sfxHandle;
	(void)channelNum;
}

/*
================
S_ClearSoundBuffer
================
*/
void S_ClearSoundBuffer( void ) {
	if ( snd_nullInited ) {
		snd_nullDmaPosition = 0;
		snd_nullLastMilliseconds = Sys_Milliseconds();
		Com_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );
	}
}

/*
================
S_AddVoiceSamples
================
*/
void S_AddVoiceSamples( int clientNum, int samples, const short *data ) {
	(void)clientNum;
	(void)samples;
	(void)data;
}
