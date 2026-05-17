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
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/shm.h>
#include <sys/wait.h>
#ifdef __linux__ // rb0101023 - guard this
#include <linux/soundcard.h>
#endif
#ifdef __FreeBSD__ // rb0101023 - added
#include <sys/soundcard.h>
#endif
#include <stdio.h>

#include "../game/q_shared.h"
#include "../client/snd_local.h"

int audio_fd = -1;
int snd_inited=0;

cvar_t *sndbits;
cvar_t *sndspeed;
cvar_t *sndchannels;

cvar_t *snddevice;

/* Some devices may work only with 48000 */
static int tryrates[] = { 22050, 11025, 44100, 48000, 8000 };

static qboolean use_custom_memset = qfalse;
static size_t snd_mmapSize;

#define SND_NULL_DEVICE_NAME "null"
#define SND_NONE_DEVICE_NAME "none"
#define SND_SILENT_DEVICE_NAME "silent"
#define SND_NULL_SAMPLEBITS 16
#define SND_NULL_SPEED 22050
#define SND_NULL_CHANNELS 2
#define SND_NULL_BUFFER_SAMPLES 0x8000

static byte snd_nullBuffer[SND_NULL_BUFFER_SAMPLES * ( SND_NULL_SAMPLEBITS / 8 )];
static qboolean snd_nullInited;
static int snd_nullDmaPosition;
static int snd_nullLastMilliseconds;

/*
================
Snd_Memset
================
*/
// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=371
void Snd_Memset (void* dest, const int val, const size_t count) {
	int *pDest;
	int i, iterate;

	if ( !use_custom_memset ) {
		Com_Memset( dest, val, count );
		return;
	}
	iterate = count / sizeof( int );
	pDest = (int*)dest;
	for ( i = 0; i < iterate; i++ ) {
		pDest[i] = val;
	}
}

/*
================
SNDDMA_InitCvars
================
*/
static void SNDDMA_InitCvars( void ) {
	if ( snddevice ) {
		return;
	}

	sndbits = Cvar_Get( "sndbits", "16", CVAR_ARCHIVE );
	sndspeed = Cvar_Get( "sndspeed", "0", CVAR_ARCHIVE );
	sndchannels = Cvar_Get( "sndchannels", "2", CVAR_ARCHIVE );
	snddevice = Cvar_Get( "snddevice", "/dev/dsp", CVAR_ARCHIVE );
}

/*
================
SNDDMA_IsNullDevice
================
*/
static qboolean SNDDMA_IsNullDevice( const char *deviceName ) {
	if ( !deviceName || !deviceName[0] ) {
		return qfalse;
	}

	return ( !Q_stricmp( deviceName, SND_NULL_DEVICE_NAME )
		|| !Q_stricmp( deviceName, SND_NONE_DEVICE_NAME )
		|| !Q_stricmp( deviceName, SND_SILENT_DEVICE_NAME ) ) ? qtrue : qfalse;
}

/*
================
SNDDMA_InitNull
================
*/
static qboolean SNDDMA_InitNull( void ) {
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
	snd_inited = 1;

	Com_Printf( "Using silent Linux sound DMA sink for snddevice %s\n", snddevice->string );
	return qtrue;
}

/*
================
SNDDMA_Shutdown
================
*/
void SNDDMA_Shutdown( void ) {
	if ( snd_nullInited ) {
		snd_nullInited = qfalse;
		snd_nullDmaPosition = 0;
		snd_nullLastMilliseconds = 0;
	} else if ( dma.buffer && dma.buffer != (byte *)MAP_FAILED && snd_mmapSize > 0 ) {
		munmap( dma.buffer, snd_mmapSize );
	}

	if ( audio_fd >= 0 ) {
		close( audio_fd );
		audio_fd = -1;
	}

	snd_mmapSize = 0;
	use_custom_memset = qfalse;
	snd_inited = 0;
	Com_Memset( &dma, 0, sizeof( dma ) );
}

/*
================
SNDDMA_Init
================
*/
qboolean SNDDMA_Init( void ) {
	int rc;
	int fmt;
	int tmp;
	int i;
	struct audio_buf_info info;
	int caps;
	extern uid_t saved_euid;

	if ( snd_inited ) {
		return 1;
	}

	SNDDMA_InitCvars();

	if ( SNDDMA_IsNullDevice( snddevice->string ) ) {
		return SNDDMA_InitNull();
	}

	// open /dev/dsp, confirm capability to mmap, and get size of dma buffer
	if ( audio_fd < 0 ) {
		seteuid( saved_euid );

		audio_fd = open( snddevice->string, O_RDWR );

		seteuid( getuid() );

		if ( audio_fd < 0 ) {
			perror( snddevice->string );
			Com_Printf( "Could not open %s\n", snddevice->string );
			return 0;
		}
	}

	if ( ioctl( audio_fd, SNDCTL_DSP_GETCAPS, &caps ) == -1 ) {
		perror( snddevice->string );
		Com_Printf( "Sound driver too old\n" );
		SNDDMA_Shutdown();
		return 0;
	}

	if ( !( caps & DSP_CAP_TRIGGER ) || !( caps & DSP_CAP_MMAP ) ) {
		Com_Printf( "Sorry but your soundcard can't do this\n" );
		SNDDMA_Shutdown();
		return 0;
	}


	/* SNDCTL_DSP_GETOSPACE moved to be called later */

	// set sample bits & speed
	dma.samplebits = (int)sndbits->value;
	if ( dma.samplebits != 16 && dma.samplebits != 8 ) {
		ioctl( audio_fd, SNDCTL_DSP_GETFMTS, &fmt );
		if ( fmt & AFMT_S16_LE ) {
			dma.samplebits = 16;
		} else if ( fmt & AFMT_U8 ) {
			dma.samplebits = 8;
		}
	}

	dma.speed = (int)sndspeed->value;
	if ( !dma.speed ) {
		for ( i = 0 ; i < sizeof( tryrates ) / sizeof( tryrates[0] ) ; i++ ) {
			if ( !ioctl( audio_fd, SNDCTL_DSP_SPEED, &tryrates[i] ) ) {
				break;
			}
		}
		if ( i == sizeof( tryrates ) / sizeof( tryrates[0] ) ) {
			i = 0;
		}
		dma.speed = tryrates[i];
	}

	dma.channels = (int)sndchannels->value;
	if ( dma.channels < 1 || dma.channels > 2 ) {
		dma.channels = 2;
	}

/*  mmap() call moved forward */

	tmp = 0;
	if ( dma.channels == 2 ) {
		tmp = 1;
	}
	rc = ioctl( audio_fd, SNDCTL_DSP_STEREO, &tmp );
	if ( rc < 0 ) {
		perror( snddevice->string );
		Com_Printf( "Could not set %s to stereo=%d", snddevice->string, dma.channels );
		SNDDMA_Shutdown();
		return 0;
	}

	if ( tmp ) {
		dma.channels = 2;
	} else {
		dma.channels = 1;
	}

	rc = ioctl( audio_fd, SNDCTL_DSP_SPEED, &dma.speed );
	if ( rc < 0 ) {
		perror( snddevice->string );
		Com_Printf( "Could not set %s speed to %d", snddevice->string, dma.speed );
		SNDDMA_Shutdown();
		return 0;
	}

	if ( dma.samplebits == 16 ) {
		rc = AFMT_S16_LE;
		rc = ioctl( audio_fd, SNDCTL_DSP_SETFMT, &rc );
		if ( rc < 0 ) {
			perror( snddevice->string );
			Com_Printf( "Could not support 16-bit data.  Try 8-bit.\n" );
			SNDDMA_Shutdown();
			return 0;
		}
	} else if ( dma.samplebits == 8 ) {
		rc = AFMT_U8;
		rc = ioctl( audio_fd, SNDCTL_DSP_SETFMT, &rc );
		if ( rc < 0 ) {
			perror( snddevice->string );
			Com_Printf( "Could not support 8-bit data.\n" );
			SNDDMA_Shutdown();
			return 0;
		}
	} else {
		perror( snddevice->string );
		Com_Printf( "%d-bit sound not supported.", dma.samplebits );
		SNDDMA_Shutdown();
		return 0;
	}

	if ( ioctl( audio_fd, SNDCTL_DSP_GETOSPACE, &info ) == -1 ) {
		perror( "GETOSPACE" );
		Com_Printf( "Um, can't do GETOSPACE?\n" );
		SNDDMA_Shutdown();
		return 0;
	}

	snd_mmapSize = info.fragstotal * info.fragsize;
	dma.samples = snd_mmapSize / ( dma.samplebits / 8 );
	dma.submission_chunk = 1;

	// memory map the dma buffer

  // TTimo 2001/10/08 added PROT_READ to the mmap
  // https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=371
  // checking Alsa bug, doesn't allow dma alloc with PROT_READ?

	if ( !dma.buffer ) {
		dma.buffer = (unsigned char *) mmap( NULL, snd_mmapSize, PROT_WRITE|PROT_READ, MAP_FILE|MAP_SHARED, audio_fd, 0 );
	}

	if ( dma.buffer == MAP_FAILED ) {
		Com_Printf( "Could not mmap dma buffer PROT_WRITE|PROT_READ\n" );
		Com_Printf( "trying mmap PROT_WRITE (with associated better compatibility / less performance code)\n" );
		dma.buffer = (unsigned char *) mmap( NULL, snd_mmapSize, PROT_WRITE, MAP_FILE|MAP_SHARED, audio_fd, 0 );
		// NOTE TTimo could add a variable to force using regular memset on systems that are known to be safe
		use_custom_memset = qtrue;
	}

	if ( dma.buffer == MAP_FAILED ) {
		perror( snddevice->string );
		Com_Printf( "Could not mmap %s\n", snddevice->string );
		SNDDMA_Shutdown();
		return 0;
	}

	// toggle the trigger & start her up

	tmp = 0;
	rc  = ioctl( audio_fd, SNDCTL_DSP_SETTRIGGER, &tmp );
	if ( rc < 0 ) {
		perror( snddevice->string );
		Com_Printf( "Could not toggle.\n" );
		SNDDMA_Shutdown();
		return 0;
	}

	tmp = PCM_ENABLE_OUTPUT;
	rc = ioctl( audio_fd, SNDCTL_DSP_SETTRIGGER, &tmp );
	if ( rc < 0 ) {
		perror( snddevice->string );
		Com_Printf( "Could not toggle.\n" );
		SNDDMA_Shutdown();
		return 0;
	}

	snd_inited = 1;
	return 1;
}

/*
================
SNDDMA_GetDMAPos
================
*/
int SNDDMA_GetDMAPos( void ) {
	struct count_info count;
	int currentMilliseconds;
	int elapsedMilliseconds;
	int sampleDelta;

	if ( !snd_inited ) {
		return 0;
	}

	if ( snd_nullInited ) {
		currentMilliseconds = Sys_Milliseconds();
		elapsedMilliseconds = currentMilliseconds - snd_nullLastMilliseconds;
		if ( elapsedMilliseconds > 0 && dma.samples > 0 ) {
			sampleDelta = ( elapsedMilliseconds * dma.speed * dma.channels ) / 1000;
			snd_nullDmaPosition = ( snd_nullDmaPosition + sampleDelta ) % dma.samples;
			snd_nullLastMilliseconds = currentMilliseconds;
		}
		return snd_nullDmaPosition;
	}

	if ( ioctl( audio_fd, SNDCTL_DSP_GETOPTR, &count ) == -1 ) {
		perror( snddevice->string );
		Com_Printf( "Uh, sound dead.\n" );
		SNDDMA_Shutdown();
		return 0;
	}
	return count.ptr / ( dma.samplebits / 8 );
}

/*
==============
SNDDMA_Submit

Send sound to device if buffer isn't really the dma buffer
===============
*/
void SNDDMA_Submit( void ) {
}

/*
================
SNDDMA_BeginPainting
================
*/
void SNDDMA_BeginPainting( void ) {
	if ( snd_nullInited ) {
		Snd_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );
	}
}
