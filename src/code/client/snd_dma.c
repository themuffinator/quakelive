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
 * name:		snd_dma.c
 *
 * desc:		main control for any streaming sound output device
 *
 * $Archive: /MissionPack/code/client/snd_dma.c $
 *
 *****************************************************************************/

#include "snd_local.h"
#include "client.h"
#include "snd_ogg_stream.h"

void S_Play_f(void);
void S_SoundList_f(void);
void S_Music_f(void);

void S_Update_();
void S_StopAllSounds(void);
void S_UpdateBackgroundTrack( void );

static fileHandle_t s_backgroundFile;
static wavinfo_t	s_backgroundInfo;
//int			s_nextWavChunk;
static char		s_backgroundLoop[MAX_QPATH];
static snd_ogg_stream_t	s_backgroundOgg;
static qboolean		s_backgroundIsOgg;
//static char		s_backgroundMusic[MAX_QPATH]; //TTimo: unused


// =======================================================================
// Internal sound data & structures
// =======================================================================

#define		SOUND_MAXDISTANCE	1250.0f
#define		SOUND_ATTENUATE		0.0008f
channel_t   s_channels[MAX_CHANNELS];
channel_t   loop_channels[MAX_CHANNELS];
voiceChannel_t	s_voiceChannels[MAX_VOICE_CHANNELS];
int			numLoopChannels;

static int	s_soundStarted;
static		qboolean	s_soundMuted;

dma_t		dma;

static int			listener_number;
static vec3_t		listener_origin;
static vec3_t		listener_axis[3];

int			s_soundtime;		// sample PAIRS
int   		s_paintedtime; 		// sample PAIRS

// MAX_SFX may be larger than MAX_SOUNDS because
// of custom player sounds
#define		MAX_SFX			4096
sfx_t		s_knownSfx[MAX_SFX];
int			s_numSfx = 0;

#define		LOOP_HASH		128
static	sfx_t		*sfxHash[LOOP_HASH];

cvar_t		*s_volume;
cvar_t		*s_testsound;
cvar_t		*s_show;
cvar_t		*s_mixahead;
cvar_t		*s_announcerVolume;
cvar_t		*s_mixPreStep;
cvar_t		*s_musicVolume;
cvar_t		*s_doppler;
cvar_t		*s_pvs;
cvar_t		*s_voiceStep;
cvar_t		*s_voiceVolume;

static loopSound_t		loopSounds[MAX_GENTITIES];
static	channel_t		*freelist = NULL;

int						s_rawend;
portable_samplepair_t	s_rawsamples[MAX_RAW_SAMPLES];


// ====================================================================
// User-setable variables
// ====================================================================


void S_SoundInfo_f(void) {
	Com_Printf("----- Sound Info -----\n" );
	if (!s_soundStarted) {
		Com_Printf ("sound system not started\n");
	} else {
		if ( s_soundMuted ) {
			Com_Printf ("sound system is muted\n");
		}

		Com_Printf("%5d stereo\n", dma.channels - 1);
		Com_Printf("%5d samples\n", dma.samples);
		Com_Printf("%5d samplebits\n", dma.samplebits);
		Com_Printf("%5d submission_chunk\n", dma.submission_chunk);
		Com_Printf("%5d speed\n", dma.speed);
		Com_Printf("0x%x dma buffer\n", dma.buffer);
		if ( s_backgroundFile || S_OggStreamActive( &s_backgroundOgg ) ) {
			Com_Printf("Background file: %s\n", s_backgroundLoop );
		} else {
			Com_Printf("No background file.\n" );
		}

	}
	Com_Printf("----------------------\n" );
}

/*
================
S_Init
================
*/
void S_Init( void ) {
	cvar_t	*cv;
	qboolean	r;

	Com_Printf("\n------- sound initialization -------\n");

	s_announcerVolume = Cvar_GetBounded( "s_announcerVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	s_doppler = Cvar_Get( "s_doppler", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	cv = Cvar_Get ("s_initsound", "1", 0);
	s_mixahead = Cvar_Get( "s_mixahead", "0.140", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	s_mixPreStep = Cvar_Get( "s_mixPreStep", "0.05", CVAR_ARCHIVE | CVAR_PROTECTED );
	s_musicVolume = Cvar_GetBounded( "s_musicvolume", "0.5", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	s_pvs = Cvar_GetBounded( "s_pvs", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	s_voiceVolume = Cvar_GetBounded( "s_voiceVolume", "1.0", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	s_voiceStep = Cvar_Get( "s_voiceStep", "0.02", CVAR_ARCHIVE | CVAR_PROTECTED );
	s_show = Cvar_Get ("s_show", "0", CVAR_CHEAT);
	s_testsound = Cvar_Get ("s_testsound", "0", CVAR_CHEAT);
	s_volume = Cvar_GetBounded( "s_volume", "0.8", "0.0", "2.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	if ( !cv->integer ) {
		Com_Printf ("not initializing.\n");
		Com_Printf("------------------------------------\n");
		return;
	}

	Cmd_AddCommand("play", S_Play_f);
	Cmd_AddCommand("music", S_Music_f);
	Cmd_AddCommand("s_list", S_SoundList_f);
	Cmd_AddCommand("s_info", S_SoundInfo_f);
	Cmd_AddCommand("s_stop", S_StopAllSounds);

	r = SNDDMA_Init();
	Com_Printf("------------------------------------\n");

	if ( r ) {
		s_soundStarted = 1;
		s_soundMuted = 1;
		s_numSfx = 0;

		Com_Memset(sfxHash, 0, sizeof(sfx_t *)*LOOP_HASH);

		s_soundtime = 0;
		s_paintedtime = 0;

		S_StopAllSounds ();

		S_SoundInfo_f();
	}

}


void S_ChannelFree(channel_t *v) {
	v->thesfx = NULL;
	*(channel_t **)v = freelist;
	freelist = (channel_t*)v;
}

channel_t*	S_ChannelMalloc() {
	channel_t *v;
	if (freelist == NULL) {
		return NULL;
	}
	v = freelist;
	freelist = *(channel_t **)freelist;
	v->allocTime = Com_Milliseconds();
	return v;
}

void S_ChannelSetup() {
	channel_t *p, *q;

	// clear all the sounds so they don't
	Com_Memset( s_channels, 0, sizeof( s_channels ) );

	p = s_channels;;
	q = p + MAX_CHANNELS;
	while (--q > p) {
		*(channel_t **)q = q-1;
	}
	
	*(channel_t **)q = NULL;
	freelist = p + MAX_CHANNELS - 1;
	Com_DPrintf("Channel memory manager started\n");
}

// =======================================================================
// Shutdown sound engine
// =======================================================================

void S_Shutdown( void ) {
	if ( !s_soundStarted ) {
		return;
	}

	SND_shutdown();
	SNDDMA_Shutdown();

	s_soundStarted = 0;

	Cmd_RemoveCommand("play");
	Cmd_RemoveCommand("music");
	Cmd_RemoveCommand("s_list");
	Cmd_RemoveCommand("s_info");
	Cmd_RemoveCommand("s_stop");
}


// =======================================================================
// Load a sound
// =======================================================================

/*
================
return a hash value for the sfx name
================
*/
static long S_HashSFXName(const char *name) {
	int		i;
	long	hash;
	char	letter;

	hash = 0;
	i = 0;
	while (name[i] != '\0') {
		letter = tolower(name[i]);
		if (letter =='.') break;				// don't include extension
		if (letter =='\\') letter = '/';		// damn path names
		hash+=(long)(letter)*(i+119);
		i++;
	}
	hash &= (LOOP_HASH-1);
	return hash;
}

/*
==================
S_FindName

Will allocate a new sfx if it isn't found
==================
*/
static sfx_t *S_FindName( const char *name ) {
	int		i;
	int		hash;

	sfx_t	*sfx;

	if (!name) {
		Com_Error (ERR_FATAL, "S_FindName: NULL");
	}
	if (!name[0]) {
		Com_Error (ERR_FATAL, "S_FindName: empty name");
	}

	if (strlen(name) >= MAX_QPATH) {
		Com_Error (ERR_FATAL, "S_FindName: name too long: %s", name);
	}

	hash = S_HashSFXName(name);

	sfx = sfxHash[hash];
	// see if already loaded
	while (sfx) {
		if (!Q_stricmp(sfx->soundName, name) ) {
			return sfx;
		}
		sfx = sfx->next;
	}

	// find a free sfx
	for (i=0 ; i < s_numSfx ; i++) {
		if (!s_knownSfx[i].soundName[0]) {
			break;
		}
	}

	if (i == s_numSfx) {
		if (s_numSfx == MAX_SFX) {
			Com_Error (ERR_FATAL, "S_FindName: out of sfx_t");
		}
		s_numSfx++;
	}
	
	sfx = &s_knownSfx[i];
	Com_Memset (sfx, 0, sizeof(*sfx));
	strcpy (sfx->soundName, name);

	sfx->next = sfxHash[hash];
	sfxHash[hash] = sfx;

	return sfx;
}

/*
=================
S_DefaultSound
=================
*/
void S_DefaultSound( sfx_t *sfx ) {
	
	int		i;

	sfx->soundLength = 512;
	sfx->soundData = SND_malloc();
	sfx->soundData->next = NULL;


	for ( i = 0 ; i < sfx->soundLength ; i++ ) {
		sfx->soundData->sndChunk[i] = i;
	}
}

/*
===================
S_DisableSounds

Disables sounds until the next S_BeginRegistration.
This is called when the hunk is cleared and the sounds
are no longer valid.
===================
*/
void S_DisableSounds( void ) {
	S_StopAllSounds();
	s_soundMuted = qtrue;
}

/*
=====================
S_BeginRegistration

=====================
*/
void S_BeginRegistration( void ) {
	s_soundMuted = qfalse;		// we can play again

	SND_shutdown();
	SND_setup();

	s_numSfx = 0;
	Com_Memset( s_knownSfx, 0, sizeof( s_knownSfx ) );
	Com_Memset(sfxHash, 0, sizeof(sfx_t *)*LOOP_HASH);

	S_RegisterSound("sound/feedback/hit.wav", qfalse);		// changed to a sound in baseq3
}


/*
==================
S_RegisterSound

Creates a default buzz sound if the file can't be loaded
==================
*/
sfxHandle_t	S_RegisterSound( const char *name, qboolean compressed ) {
	sfx_t	*sfx;

	compressed = qfalse;
	if (!s_soundStarted) {
		return 0;
	}

	if ( strlen( name ) >= MAX_QPATH ) {
		Com_Printf( "Sound name exceeds MAX_QPATH\n" );
		return 0;
	}

	sfx = S_FindName( name );
	if ( sfx->soundData ) {
		if ( sfx->defaultSound ) {
			Com_Printf( S_COLOR_YELLOW "WARNING: could not find %s - using default\n", sfx->soundName );
			return 0;
		}
		return sfx - s_knownSfx;
	}

	sfx->inMemory = qfalse;
	sfx->soundCompressed = compressed;

	S_memoryLoad(sfx);

	if ( sfx->defaultSound ) {
		Com_Printf( S_COLOR_YELLOW "WARNING: could not find %s - using default\n", sfx->soundName );
		return 0;
	}

	return sfx - s_knownSfx;
}

/*
==================
S_memoryLoad
==================
*/
void S_memoryLoad(sfx_t	*sfx) {
	// load the sound file
	if ( !S_LoadSound ( sfx ) ) {
		Com_Printf( S_COLOR_YELLOW "WARNING: couldn't load sound: %s\n", sfx->soundName );
		sfx->defaultSound = qtrue;
	}
	sfx->inMemory = qtrue;
}

//=============================================================================

/*
=================
S_SpatializeOrigin

Used for spatializing s_channels
=================
*/
void S_SpatializeOrigin (vec3_t origin, int master_vol, int *left_vol, int *right_vol)
{
    vec_t		dot;
    vec_t		dist;
    vec_t		lscale, rscale, scale;
    vec3_t		source_vec;
    vec3_t		vec;

	const float dist_mult = SOUND_ATTENUATE;
	
	// calculate stereo seperation and distance attenuation
	VectorSubtract(origin, listener_origin, source_vec);

	dist = VectorNormalize(source_vec);
	if ( dist >= SOUND_MAXDISTANCE ) {
		*left_vol = 0;
		*right_vol = 0;
		return;
	}
	dist *= dist_mult;		// different attenuation levels
	
	VectorRotate( source_vec, listener_axis, vec );

	dot = -vec[1];

	if (dma.channels == 1)
	{ // no attenuation = no spatialization
		rscale = 1.0;
		lscale = 1.0;
	}
	else
	{
		rscale = 0.5 * (1.0 + dot);
		lscale = 0.5 * (1.0 - dot);
		if ( rscale < 0 ) {
			rscale = 0;
		}
		if ( lscale < 0 ) {
			lscale = 0;
		}
	}

	// add in distance effect
	scale = (1.0 - dist) * rscale;
	*right_vol = (master_vol * scale);
	if (*right_vol < 0)
		*right_vol = 0;

	scale = (1.0 - dist) * lscale;
	*left_vol = (master_vol * scale);
	if (*left_vol < 0)
		*left_vol = 0;
}

// =======================================================================
// Start a sound effect
// =======================================================================

/*
====================
S_StartSoundInternal

Common channel-start path shared by the fixed-gain and retail volume-aware
entry points.
====================
*/
static void S_StartSoundInternal( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfxHandle, float volume ) {
	channel_t	*ch;
	sfx_t		*sfx;
	int			i;
	int			oldest;
	int			chosen;
	int			time;

	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	if ( !origin && ( entityNum < 0 || entityNum > MAX_GENTITIES ) ) {
		Com_Error( ERR_DROP, "S_StartSound: bad entitynum %i", entityNum );
	}

	if ( sfxHandle < 0 || sfxHandle >= s_numSfx ) {
		Com_Printf( S_COLOR_YELLOW "S_StartSound: handle %i out of range\n", sfxHandle );
		return;
	}

	sfx = &s_knownSfx[ sfxHandle ];

	if (sfx->inMemory == qfalse) {
		S_memoryLoad(sfx);
	}

	if ( s_show->integer == 1 ) {
		Com_Printf( "%i : %s\n", s_paintedtime, sfx->soundName );
	}

	time = Com_Milliseconds();

//	Com_Printf("playing %s\n", sfx->soundName);
	// pick a channel to play on

	if ( entityNum != ENTITYNUM_WORLD ) {
		ch = s_channels;
		for ( i = 0; i < MAX_CHANNELS ; i++, ch++ ) {
			if ( ch->entnum == entityNum && ch->thesfx == sfx ) {
				if ( time - ch->allocTime < 50 ) {
					Com_DPrintf( "double sound start: %d %s\n", entityNum, sfx->soundName );
					return;
				}
			}
		}
	}

	sfx->lastTimeUsed = time;

	ch = S_ChannelMalloc();	// entityNum, entchannel);
	if (!ch) {
		ch = s_channels;

		oldest = sfx->lastTimeUsed;
		chosen = -1;
		for ( i = 0 ; i < MAX_CHANNELS ; i++, ch++ ) {
			if (ch->entnum == entityNum && ch->allocTime<oldest && ch->entchannel != CHAN_ANNOUNCER) {
				oldest = ch->allocTime;
				chosen = i;
			}
		}
		if (chosen == -1) {
			ch = s_channels;
			for ( i = 0 ; i < MAX_CHANNELS ; i++, ch++ ) {
				if (ch->entnum == ENTITYNUM_WORLD && ch->allocTime<oldest) {
					oldest = ch->allocTime;
					chosen = i;
				}
			}
			if (chosen == -1) {
				return;
			}
		}
		ch = &s_channels[chosen];
		ch->allocTime = sfx->lastTimeUsed;
	}

	if (origin) {
		VectorCopy (origin, ch->origin);
		ch->fixed_origin = qtrue;
	} else {
		ch->fixed_origin = qfalse;
	}

	ch->master_vol = (int)( volume * 127.0f );
	ch->entnum = entityNum;
	ch->thesfx = sfx;
	ch->startSample = START_SAMPLE_IMMEDIATE;
	ch->entchannel = entchannel;
	ch->leftvol = ch->master_vol;		// these will get calced at next spatialize
	ch->rightvol = ch->master_vol;		// unless the game isn't running
	ch->doppler = qfalse;
}

/*
====================
S_StartSound

Validates the parms and ques the sound up
if pos is NULL, the sound will be dynamically sourced from the entity
Entchannel 0 will never override a playing sound
====================
*/
void S_StartSound( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfxHandle ) {
	S_StartSoundInternal( origin, entityNum, entchannel, sfxHandle, 1.0f );
}

/*
====================
S_StartSoundVolume

Reconstructs the retail sound-start helper with an explicit caller-controlled
volume scalar.
====================
*/
void S_StartSoundVolume( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfxHandle, float volume ) {
	S_StartSoundInternal( origin, entityNum, entchannel, sfxHandle, volume );
}

/*
==================
S_StartLocalSound
==================
*/
void S_StartLocalSound( sfxHandle_t sfxHandle, int channelNum ) {
	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	if ( sfxHandle < 0 || sfxHandle >= s_numSfx ) {
		Com_Printf( S_COLOR_YELLOW "S_StartLocalSound: handle %i out of range\n", sfxHandle );
		return;
	}

	S_StartSound( NULL, listener_number, channelNum, sfxHandle );
}

/*
========================
S_StartLocalSoundVolume
========================
*/
void S_StartLocalSoundVolume( sfxHandle_t sfxHandle, int channelNum, float volume ) {
	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	if ( sfxHandle < 0 || sfxHandle >= s_numSfx ) {
		Com_Printf( S_COLOR_YELLOW "S_StartLocalSound: handle %i out of range\n", sfxHandle );
		return;
	}

	S_StartSoundVolume( NULL, listener_number, channelNum, sfxHandle, volume );
}

/*
================
S_AddVoiceSamples

Queues decompressed voice PCM into the retail-style five-lane circular voice
buffer consumed from the top-level paint path.
================
*/
void S_AddVoiceSamples( int clientNum, int samples, const short *data ) {
	voiceChannel_t	*voice;
	int				i;
	int				channelIndex;
	int				queuedSamples;
	int				startSample;
	int				count;
	int				room;

	channelIndex = -1;
	for ( i = 0; i < MAX_VOICE_CHANNELS; ++i ) {
		if ( s_voiceChannels[i].clientNum == clientNum ) {
			channelIndex = i;
			break;
		}
	}

	if ( channelIndex < 0 ) {
		for ( i = 0; i < MAX_VOICE_CHANNELS; ++i ) {
			if ( s_paintedtime - s_voiceChannels[i].endSample > (int)( dma.samples * 0.5f ) ) {
				channelIndex = i;
				s_voiceChannels[i].clientNum = clientNum;
				Com_DPrintf( "client %d: using voice %d\n", clientNum, channelIndex );
				break;
			}
		}
	}

	if ( channelIndex < 0 ) {
		Com_DPrintf( "client %d silenced: no voices left\n", clientNum );
		return;
	}

	voice = &s_voiceChannels[channelIndex];
	voice->clientNum = clientNum;

	if ( voice->endSample <= voice->startSample ) {
		startSample = s_paintedtime + (int)( s_mixPreStep->value * dma.speed );
		if ( s_voiceStep ) {
			startSample += (int)( s_voiceStep->value * dma.speed );
		}

		voice->startSample = startSample;
		voice->endSample = startSample;
		Com_DPrintf( "voice channel %d: start samples at time %d\n", channelIndex, startSample );
	}

	queuedSamples = voice->endSample - voice->startSample;
	if ( queuedSamples < 0 ) {
		queuedSamples = 0;
	}
	if ( queuedSamples > 0 ) {
		Com_DPrintf( "voice channel %d: %d samples already in buffer\n", channelIndex, queuedSamples );
	}

	count = samples;
	room = VOICE_BUFFER_SAMPLES - queuedSamples;
	if ( count > room ) {
		Com_DPrintf( "voice channel %d: overflow %d voice samples with room for only %d\n", channelIndex, samples, room );
		count = room;
	}
	if ( count < 0 ) {
		count = 0;
	}
	Com_DPrintf( "voice channel %d: add %d samples to voice buffer\n", channelIndex, count );

	for ( i = 0; i < count; ++i ) {
		voice->samples[( voice->endSample + i ) & ( VOICE_BUFFER_SAMPLES - 1 )] = data[i];
	}

	voice->endSample += count;
}


/*
==================
S_ClearSoundBuffer

If we are about to perform file access, clear the buffer
so sound doesn't stutter.
==================
*/
void S_ClearSoundBuffer( void ) {
	int		clear;
		
	if (!s_soundStarted)
		return;

	// stop looping sounds
	Com_Memset(loopSounds, 0, MAX_GENTITIES*sizeof(loopSound_t));
	Com_Memset(loop_channels, 0, MAX_CHANNELS*sizeof(channel_t));
	numLoopChannels = 0;

	S_ChannelSetup();

	s_rawend = 0;
	Com_Memset( s_voiceChannels, 0, sizeof( s_voiceChannels ) );

	if (dma.samplebits == 8)
		clear = 0x80;
	else
		clear = 0;

	SNDDMA_BeginPainting ();
	if (dma.buffer)
    // TTimo: due to a particular bug workaround in linux sound code,
    //   have to optionally use a custom C implementation of Com_Memset
    //   not affecting win32, we have #define Snd_Memset Com_Memset
    // https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=371
		Snd_Memset(dma.buffer, clear, dma.samples * dma.samplebits/8);
	SNDDMA_Submit ();
}

/*
==================
S_StopAllSounds
==================
*/
void S_StopAllSounds(void) {
	if ( !s_soundStarted ) {
		return;
	}

	// stop the background music
	S_StopBackgroundTrack();

	S_ClearSoundBuffer ();
}

/*
==============================================================

continuous looping sounds are added each frame

==============================================================
*/

void S_StopLoopingSound(int entityNum) {
	loopSounds[entityNum].active = qfalse;
//	loopSounds[entityNum].sfx = 0;
	loopSounds[entityNum].kill = qfalse;
}

/*
==================
S_ClearLoopingSoundsFrame

Retail native-cgame frame clear for transient looping sounds.
==================
*/
void S_ClearLoopingSoundsFrame( void ) {
	int i;

	for ( i = 0 ; i < MAX_GENTITIES ; i++) {
		loopSounds[i].active = qfalse;
	}
	numLoopChannels = 0;
}

/*
==================
S_ClearLoopingSounds

==================
*/
void S_ClearLoopingSounds( qboolean killall ) {
	int i;
	for ( i = 0 ; i < MAX_GENTITIES ; i++) {
		if (killall || loopSounds[i].kill == qtrue || (loopSounds[i].sfx && loopSounds[i].sfx->soundLength == 0)) {
			loopSounds[i].kill = qfalse;
			S_StopLoopingSound(i);
		}
	}
	numLoopChannels = 0;
}

/*
==================
S_AddLoopingSound

Called during entity generation for a frame
Include velocity in case I get around to doing doppler...
==================
*/
void S_AddLoopingSound( int entityNum, const vec3_t origin, const vec3_t velocity, sfxHandle_t sfxHandle ) {
	sfx_t *sfx;

	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	if ( sfxHandle < 0 || sfxHandle >= s_numSfx ) {
		Com_Printf( S_COLOR_YELLOW "S_AddLoopingSound: handle %i out of range\n", sfxHandle );
		return;
	}

	sfx = &s_knownSfx[ sfxHandle ];

	if (sfx->inMemory == qfalse) {
		S_memoryLoad(sfx);
	}

	if ( !sfx->soundLength ) {
		Com_Error( ERR_DROP, "%s has length 0", sfx->soundName );
	}

	VectorCopy( origin, loopSounds[entityNum].origin );
	VectorCopy( velocity, loopSounds[entityNum].velocity );
	loopSounds[entityNum].active = qtrue;
	loopSounds[entityNum].kill = qtrue;
	loopSounds[entityNum].doppler = qfalse;
	loopSounds[entityNum].oldDopplerScale = 1.0;
	loopSounds[entityNum].dopplerScale = 1.0;
	loopSounds[entityNum].sfx = sfx;

	if (s_doppler->integer && VectorLengthSquared(velocity)>0.0) {
		vec3_t	out;
		float	lena, lenb;

		loopSounds[entityNum].doppler = qtrue;
		lena = DistanceSquared(loopSounds[listener_number].origin, loopSounds[entityNum].origin);
		VectorAdd(loopSounds[entityNum].origin, loopSounds[entityNum].velocity, out);
		lenb = DistanceSquared(loopSounds[listener_number].origin, out);
		if ((loopSounds[entityNum].framenum+1) != cls.framecount) {
			loopSounds[entityNum].oldDopplerScale = 1.0;
		} else {
			loopSounds[entityNum].oldDopplerScale = loopSounds[entityNum].dopplerScale;
		}
		loopSounds[entityNum].dopplerScale = lenb/(lena*100);
		if (loopSounds[entityNum].dopplerScale<=1.0) {
			loopSounds[entityNum].doppler = qfalse;			// don't bother doing the math
		}
	}

	loopSounds[entityNum].framenum = cls.framecount;
}

/*
==================
S_AddRealLoopingSound

Compatibility looping-sound path for legacy VM callers.
==================
*/
void S_AddRealLoopingSound( int entityNum, const vec3_t origin, const vec3_t velocity, sfxHandle_t sfxHandle ) {
	sfx_t *sfx;

	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	if ( sfxHandle < 0 || sfxHandle >= s_numSfx ) {
		Com_Printf( S_COLOR_YELLOW "S_AddRealLoopingSound: handle %i out of range\n", sfxHandle );
		return;
	}

	sfx = &s_knownSfx[ sfxHandle ];

	if (sfx->inMemory == qfalse) {
		S_memoryLoad(sfx);
	}

	if ( !sfx->soundLength ) {
		Com_Error( ERR_DROP, "%s has length 0", sfx->soundName );
	}
	VectorCopy( origin, loopSounds[entityNum].origin );
	VectorCopy( velocity, loopSounds[entityNum].velocity );
	loopSounds[entityNum].sfx = sfx;
	loopSounds[entityNum].active = qtrue;
	loopSounds[entityNum].kill = qfalse;
	loopSounds[entityNum].doppler = qfalse;
	loopSounds[entityNum].oldDopplerScale = 1.0;
	loopSounds[entityNum].dopplerScale = 1.0;
	loopSounds[entityNum].framenum = cls.framecount;
}



/*
==================
S_AddLoopSounds

Spatialize all of the looping sounds.
All sounds are on the same cycle, so any duplicates can just
sum up the channel multipliers.
==================
*/
void S_AddLoopSounds (void) {
	int			i, j, time;
	int			left_total, right_total, left, right;
	channel_t	*ch;
	loopSound_t	*loop, *loop2;
	static int	loopFrame;


	numLoopChannels = 0;

	time = Com_Milliseconds();

	loopFrame++;
	for ( i = 0 ; i < MAX_GENTITIES ; i++) {
		loop = &loopSounds[i];
		if ( !loop->active || loop->mergeFrame == loopFrame ) {
			continue;	// already merged into an earlier sound
		}

		S_SpatializeOrigin( loop->origin, 127, &left_total, &right_total);

		loop->sfx->lastTimeUsed = time;

		for (j=(i+1); j< MAX_GENTITIES ; j++) {
			loop2 = &loopSounds[j];
			if ( !loop2->active || loop2->doppler || loop2->sfx != loop->sfx) {
				continue;
			}
			loop2->mergeFrame = loopFrame;

			S_SpatializeOrigin( loop2->origin, 127, &left, &right);

			loop2->sfx->lastTimeUsed = time;
			left_total += left;
			right_total += right;
		}
		if (left_total == 0 && right_total == 0) {
			continue;		// not audible
		}

		// allocate a channel
		ch = &loop_channels[numLoopChannels];
		
		if (left_total > 255) {
			left_total = 255;
		}
		if (right_total > 255) {
			right_total = 255;
		}
		
		ch->master_vol = 127;
		ch->leftvol = left_total;
		ch->rightvol = right_total;
		ch->thesfx = loop->sfx;
		ch->doppler = loop->doppler;
		ch->dopplerScale = loop->dopplerScale;
		ch->oldDopplerScale = loop->oldDopplerScale;
		numLoopChannels++;
		if (numLoopChannels == MAX_CHANNELS) {
			return;
		}
	}
}

//=============================================================================

/*
=================
S_GetRawSamplePointer
=================
*/
portable_samplepair_t *S_GetRawSamplePointer() {
	return s_rawsamples;
}

/*
============
S_RawSamples

Music streaming
============
*/
void S_RawSamples( int samples, int rate, int width, int s_channels, const byte *data, float volume ) {
	int		i;
	int		src, dst;
	float	scale;
	int		intVolume;

	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	intVolume = 256 * volume * s_volume->value;

	if ( s_rawend < s_soundtime ) {
		Com_DPrintf( "S_RawSamples: resetting minimum: %i < %i\n", s_rawend, s_soundtime );
		s_rawend = s_soundtime;
	}

	scale = (float)rate / dma.speed;

//Com_Printf ("%i < %i < %i\n", s_soundtime, s_paintedtime, s_rawend);
	if (s_channels == 2 && width == 2)
	{
		if (scale == 1.0)
		{	// optimized case
			for (i=0 ; i<samples ; i++)
			{
				dst = s_rawend&(MAX_RAW_SAMPLES-1);
				s_rawend++;
				s_rawsamples[dst].left = ((short *)data)[i*2] * intVolume;
				s_rawsamples[dst].right = ((short *)data)[i*2+1] * intVolume;
			}
		}
		else
		{
			for (i=0 ; ; i++)
			{
				src = i*scale;
				if (src >= samples)
					break;
				dst = s_rawend&(MAX_RAW_SAMPLES-1);
				s_rawend++;
				s_rawsamples[dst].left = ((short *)data)[src*2] * intVolume;
				s_rawsamples[dst].right = ((short *)data)[src*2+1] * intVolume;
			}
		}
	}
	else if (s_channels == 1 && width == 2)
	{
		for (i=0 ; ; i++)
		{
			src = i*scale;
			if (src >= samples)
				break;
			dst = s_rawend&(MAX_RAW_SAMPLES-1);
			s_rawend++;
			s_rawsamples[dst].left = ((short *)data)[src] * intVolume;
			s_rawsamples[dst].right = ((short *)data)[src] * intVolume;
		}
	}
	else if (s_channels == 2 && width == 1)
	{
		intVolume *= 256;

		for (i=0 ; ; i++)
		{
			src = i*scale;
			if (src >= samples)
				break;
			dst = s_rawend&(MAX_RAW_SAMPLES-1);
			s_rawend++;
			s_rawsamples[dst].left = ((char *)data)[src*2] * intVolume;
			s_rawsamples[dst].right = ((char *)data)[src*2+1] * intVolume;
		}
	}
	else if (s_channels == 1 && width == 1)
	{
		intVolume *= 256;

		for (i=0 ; ; i++)
		{
			src = i*scale;
			if (src >= samples)
				break;
			dst = s_rawend&(MAX_RAW_SAMPLES-1);
			s_rawend++;
			s_rawsamples[dst].left = (((byte *)data)[src]-128) * intVolume;
			s_rawsamples[dst].right = (((byte *)data)[src]-128) * intVolume;
		}
	}

	if ( s_rawend > s_soundtime + MAX_RAW_SAMPLES ) {
		Com_DPrintf( "S_RawSamples: overflowed %i > %i\n", s_rawend, s_soundtime );
	}
}

//=============================================================================

/*
=====================
S_UpdateEntityPosition

let the sound system know where an entity currently is
======================
*/
void S_UpdateEntityPosition( int entityNum, const vec3_t origin ) {
	if ( entityNum < 0 || entityNum > MAX_GENTITIES ) {
		Com_Error( ERR_DROP, "S_UpdateEntityPosition: bad entitynum %i", entityNum );
	}
	VectorCopy( origin, loopSounds[entityNum].origin );
}

/*
================
S_OriginInPVS
================
*/
static qboolean S_OriginInPVS( const vec3_t listener, const vec3_t origin ) {
	int listenerLeaf;
	int listenerCluster;
	int originLeaf;
	int originCluster;
	byte *mask;

	listenerLeaf = CM_PointLeafnum( listener );
	originLeaf = CM_PointLeafnum( origin );
	listenerCluster = CM_LeafCluster( listenerLeaf );
	originCluster = CM_LeafCluster( originLeaf );
	if ( listenerCluster < 0 || originCluster < 0 ) {
		return qfalse;
	}

	mask = CM_ClusterPVS( listenerCluster );
	if ( !mask ) {
		return qfalse;
	}

	return ( mask[originCluster >> 3] & ( 1 << ( originCluster & 7 ) ) ) ? qtrue : qfalse;
}


/*
============
S_Respatialize

Change the volumes of all the playing sounds for changes in their positions
============
*/
void S_Respatialize( int entityNum, const vec3_t head, vec3_t axis[3], int inwater ) {
	int			i;
	channel_t	*ch;
	vec3_t		origin;

	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	listener_number = entityNum;
	VectorCopy(head, listener_origin);
	VectorCopy(axis[0], listener_axis[0]);
	VectorCopy(axis[1], listener_axis[1]);
	VectorCopy(axis[2], listener_axis[2]);

	// update spatialization for dynamic sounds	
	ch = s_channels;
	for ( i = 0 ; i < MAX_CHANNELS ; i++, ch++ ) {
		if ( !ch->thesfx ) {
			continue;
		}
		// anything coming from the view entity will always be full volume
		if (ch->entnum == listener_number) {
			ch->leftvol = ch->master_vol;
			ch->rightvol = ch->master_vol;
		} else {
			if (ch->fixed_origin) {
				VectorCopy( ch->origin, origin );
			} else {
				VectorCopy( loopSounds[ ch->entnum ].origin, origin );
			}

			if ( s_pvs && s_pvs->integer && !S_OriginInPVS( listener_origin, origin ) ) {
				ch->leftvol = 0;
				ch->rightvol = 0;
				continue;
			}

			S_SpatializeOrigin (origin, ch->master_vol, &ch->leftvol, &ch->rightvol);
		}
	}

	// add loopsounds
	S_AddLoopSounds ();
}


/*
========================
S_ScanChannelStarts

Returns qtrue if any new sounds were started since the last mix
========================
*/
qboolean S_ScanChannelStarts( void ) {
	channel_t		*ch;
	int				i;
	qboolean		newSamples;

	newSamples = qfalse;
	ch = s_channels;

	for (i=0; i<MAX_CHANNELS ; i++, ch++) {
		if ( !ch->thesfx ) {
			continue;
		}
		// if this channel was just started this frame,
		// set the sample count to it begins mixing
		// into the very first sample
		if ( ch->startSample == START_SAMPLE_IMMEDIATE ) {
			ch->startSample = s_paintedtime;
			newSamples = qtrue;
			continue;
		}

		// if it is completely finished by now, clear it
		if ( ch->startSample + (ch->thesfx->soundLength) <= s_paintedtime ) {
			S_ChannelFree(ch);
		}
	}

	return newSamples;
}

/*
============
S_Update

Called once each time through the main loop
============
*/
void S_Update( void ) {
	int			i;
	int			total;
	channel_t	*ch;

	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	//
	// debugging output
	//
	if ( s_show->integer == 2 ) {
		total = 0;
		ch = s_channels;
		for (i=0 ; i<MAX_CHANNELS; i++, ch++) {
			if (ch->thesfx && (ch->leftvol || ch->rightvol) ) {
				Com_Printf ("%3i %3i %s\n", ch->leftvol, ch->rightvol, ch->thesfx->soundName);
				total++;
			}
		}
		
		Com_Printf ("----(%i)---- painted: %i\n", total, s_paintedtime);
	}

	// add raw data from streamed samples
	S_UpdateBackgroundTrack();

	// mix some sound
	S_Update_();
}

/*
================
S_GetSoundtime

Updates the DMA-derived sound clock and returns the retail helper's ignored
status value.
================
*/
int S_GetSoundtime(void) {
	int		samplepos;
	static	int		buffers;
	static	int		oldsamplepos;
	int		fullsamples;
	
	fullsamples = dma.samples / dma.channels;

	// it is possible to miscount buffers if it has wrapped twice between
	// calls to S_Update.  Oh well.
	samplepos = SNDDMA_GetDMAPos();
	if (samplepos < oldsamplepos)
	{
		buffers++;					// buffer wrapped
		
		if (s_paintedtime > 0x40000000)
		{	// time to chop things off to avoid 32 bit limits
			buffers = 0;
			s_paintedtime = fullsamples;
			S_StopAllSounds ();
		}
	}
	oldsamplepos = samplepos;

	s_soundtime = buffers*fullsamples + samplepos/dma.channels;

#if 0
// check to make sure that we haven't overshot
	if (s_paintedtime < s_soundtime)
	{
		Com_DPrintf ("S_Update_ : overflow\n");
		s_paintedtime = s_soundtime;
	}
#endif

	if ( dma.submission_chunk < 256 ) {
		s_paintedtime = s_soundtime + s_mixPreStep->value * dma.speed;
		return s_paintedtime;
	} else {
		s_paintedtime = s_soundtime + dma.submission_chunk;
	}

	return s_soundtime;
}


void S_Update_(void) {
	unsigned        endtime;
	int				samps;
	float			ma;
	static			int ot = -1;

	if ( !s_soundStarted || s_soundMuted ) {
		return;
	}

	// Updates s_soundtime
	S_GetSoundtime();

	if (s_soundtime == ot) {
		return;
	}
	ot = s_soundtime;

	// clear any sound effects that end before the current time,
	// and start any new sounds
	S_ScanChannelStarts();

	ma = s_mixahead->value * dma.speed;

	// mix ahead of current position
	endtime = s_soundtime + ma;

	// mix to an even submission block size
	endtime = (endtime + dma.submission_chunk-1)
		& ~(dma.submission_chunk-1);

	// never mix more than the complete buffer
	samps = dma.samples >> (dma.channels-1);
	if (endtime - s_soundtime > samps)
		endtime = s_soundtime + samps;



	SNDDMA_BeginPainting ();

	S_PaintChannels (endtime);

	SNDDMA_Submit ();
}

/*
===============================================================================

console functions

===============================================================================
*/

void S_Play_f( void ) {
	int 		i;
	sfxHandle_t	h;
	char		name[256];
	
	i = 1;
	while ( i<Cmd_Argc() ) {
		if ( !Q_strrchr(Cmd_Argv(i), '.') ) {
			Com_sprintf( name, sizeof(name), "%s.wav", Cmd_Argv(1) );
		} else {
			Q_strncpyz( name, Cmd_Argv(i), sizeof(name) );
		}
		h = S_RegisterSound( name, qfalse );
		if( h ) {
			S_StartLocalSound( h, CHAN_LOCAL_SOUND );
		}
		i++;
	}
}

void S_Music_f( void ) {
	int		c;

	c = Cmd_Argc();

	if ( c == 2 ) {
		S_StartBackgroundTrack( Cmd_Argv(1), Cmd_Argv(1) );
		s_backgroundLoop[0] = 0;
	} else if ( c == 3 ) {
		S_StartBackgroundTrack( Cmd_Argv(1), Cmd_Argv(2) );
	} else {
		Com_Printf ("music <musicfile> [loopfile]\n");
		return;
	}

}

/*
=============
S_SoundList_f
=============
*/
void S_SoundList_f( void ) {
	int		i;
	sfx_t	*sfx;
	int		size;
	const char	*location;

	for ( sfx = s_knownSfx, i = 0 ; i < s_numSfx ; i++, sfx++ ) {
		size = sfx->soundLength;
		location = sfx->inMemory ? "MEM" : "PGD";
		Com_Printf( "%6i [%s] : %s\n", size, location, sfx->soundName );
	}
	Com_Printf( "%i sounds loaded\n", s_numSfx );
	S_DisplayFreeMemory();
}


/*
===============================================================================

background music functions

===============================================================================
*/

/*
============
S_BackgroundTrackHasOggExtension

Returns qtrue when the supplied music path already ends in .ogg.
============
*/
static qboolean S_BackgroundTrackHasOggExtension( const char *path ) {
	const char	*extension;

	if ( !path || !path[0] ) {
		return qfalse;
	}

	extension = Q_strrchr( path, '.' );
	return ( extension && !Q_stricmp( extension, ".ogg" ) );
}

/*
============
S_SetOggTrackPath

Normalizes the provided music path to the retail OGG background-track path.
============
*/
static void S_SetOggTrackPath( const char *source, char *dest, int destSize ) {
	char	stripped[MAX_QPATH];

	if ( !dest || destSize <= 0 ) {
		return;
	}

	dest[0] = '\0';
	if ( !source || !source[0] ) {
		return;
	}

	if ( S_BackgroundTrackHasOggExtension( source ) ) {
		Q_strncpyz( dest, source, destSize );
		return;
	}

	COM_StripExtension( source, stripped );
	Q_strncpyz( dest, stripped, destSize );
	COM_DefaultExtension( dest, destSize, ".ogg" );
}

/*
============
S_CloseBackgroundOgg

Releases the active background OGG decoder.
============
*/
static void S_CloseBackgroundOgg( void ) {
	S_OggStreamClose( &s_backgroundOgg );
}

/*
============
S_OpenBackgroundOgg

Initializes the Vorbis decoder for the requested music track.
============
*/
static qboolean S_OpenBackgroundOgg( const char *name ) {
	if ( !S_OggStreamOpen( &s_backgroundOgg, name ) ) {
		return qfalse;
	}

	s_backgroundIsOgg = qtrue;
	s_backgroundFile = 0;
	s_backgroundInfo.format = WAV_FORMAT_PCM;
	s_backgroundInfo.channels = S_OggStreamChannels( &s_backgroundOgg );
	s_backgroundInfo.rate = S_OggStreamRate( &s_backgroundOgg );
	s_backgroundInfo.width = S_OggStreamWidth( &s_backgroundOgg );
	s_backgroundInfo.samples = 0;

	if ( s_backgroundInfo.channels <= 0 || s_backgroundInfo.width <= 0 || s_backgroundInfo.rate <= 0 ) {
		S_CloseBackgroundOgg();
		s_backgroundIsOgg = qfalse;
		return qfalse;
	}

	return qtrue;
}

/*
============
S_BackgroundTrackLoop

Restarts playback using the configured loop track, if available.
============
*/
static qboolean S_BackgroundTrackLoop( void ) {
	if ( !s_backgroundLoop[0] ) {
		return qfalse;
	}

	S_StartBackgroundTrack( s_backgroundLoop, s_backgroundLoop );
	return S_OggStreamActive( &s_backgroundOgg );
}

/*
==========================
S_OggUpdateBackgroundTrack

Feeds decoded OGG music into the temporary buffer and mirrors the retail
helper's error handling by logging the decode status and closing the decoder on
failure.
==========================
*/
static int S_OggUpdateBackgroundTrack( byte *buffer, int bytesToRead ) {
	int	result;

	result = S_OggStreamRead( &s_backgroundOgg, buffer, bytesToRead );
	if ( result < 0 ) {
		Com_Printf( S_COLOR_YELLOW "OGG_UpdateBackgroundTrack: %i\n", result );
		S_CloseBackgroundOgg();
		return 0;
	}

	return result;
}

/*
======================
S_StopBackgroundTrack
======================
*/
void S_StopBackgroundTrack( void ) {
	qboolean	stopped;

	stopped = qfalse;
	if ( s_backgroundFile ) {
		Sys_EndStreamedFile( s_backgroundFile );
		FS_FCloseFile( s_backgroundFile );
		s_backgroundFile = 0;
		stopped = qtrue;
	}
	if ( S_OggStreamActive( &s_backgroundOgg ) ) {
		S_CloseBackgroundOgg();
		stopped = qtrue;
	}
	s_backgroundIsOgg = qfalse;
	if ( stopped ) {
		s_rawend = 0;
	}
}

/*
======================
S_StartBackgroundTrack
======================
*/
void S_StartBackgroundTrack( const char *intro, const char *loop ){
	char	introPath[MAX_QPATH];

	if ( !intro || !intro[0] ) {
		return;
	}
	if ( !loop || !loop[0] ) {
		loop = intro;
	}
	Com_DPrintf( "S_StartBackgroundTrack( %s, %s )\n", intro, loop );

	if ( !S_BackgroundTrackHasOggExtension( intro ) ) {
		Com_DPrintf( "S_StartBackgroundTrack: %s should have an OGG extension\n", intro );
	}
	S_SetOggTrackPath( loop, s_backgroundLoop, sizeof( s_backgroundLoop ) );
	S_SetOggTrackPath( intro, introPath, sizeof( introPath ) );

	// close the background track, but DON'T reset s_rawend
	// if restarting the same back ground track
	if ( s_backgroundFile ) {
		Sys_EndStreamedFile( s_backgroundFile );
		FS_FCloseFile( s_backgroundFile );
		s_backgroundFile = 0;
	}
	if ( S_OggStreamActive( &s_backgroundOgg ) ) {
		S_CloseBackgroundOgg();
	}
	s_backgroundIsOgg = qfalse;

	if ( !S_OpenBackgroundOgg( introPath ) ) {
		Com_Printf( S_COLOR_YELLOW "WARNING: couldn't open music file %s\n", introPath );
		return;
	}
}

/*
======================
S_UpdateBackgroundTrack
======================
*/
void S_UpdateBackgroundTrack( void ) {
	int		bufferSamples;
	int		fileSamples;
	byte	raw[30000];		// just enough to fit in a mac stack frame
	int		fileBytes;
	int		r;
	static	float	musicVolume = 0.5f;

	if ( !S_OggStreamActive( &s_backgroundOgg ) ) {
		return;
	}

	// graeme see if this is OK
	musicVolume = (musicVolume + (s_musicVolume->value * 2))/4.0f;

	// don't bother playing anything if musicvolume is 0
	if ( musicVolume <= 0 ) {
		return;
	}

	// see how many samples should be copied into the raw buffer
	if ( s_rawend < s_soundtime ) {
		s_rawend = s_soundtime;
	}

	while ( s_rawend < s_soundtime + MAX_RAW_SAMPLES ) {
		bufferSamples = MAX_RAW_SAMPLES - (s_rawend - s_soundtime);

		// decide how much data needs to be read from the file
		fileSamples = bufferSamples * s_backgroundInfo.rate / dma.speed;
		if ( fileSamples <= 0 ) {
			return;
		}

		// our max buffer size
		fileBytes = fileSamples * (s_backgroundInfo.width * s_backgroundInfo.channels);
		if ( fileBytes > sizeof( raw ) ) {
			fileBytes = sizeof( raw );
			fileSamples = fileBytes / (s_backgroundInfo.width * s_backgroundInfo.channels);
		}

		r = S_OggUpdateBackgroundTrack( raw, fileBytes );
		fileSamples = r / (s_backgroundInfo.width * s_backgroundInfo.channels);

		// add to raw buffer
		S_RawSamples( fileSamples, s_backgroundInfo.rate,
			s_backgroundInfo.width, s_backgroundInfo.channels, raw, musicVolume );

		if ( r < fileBytes || fileBytes == 0 ) {
			s_backgroundIsOgg = qfalse;
			if ( !S_BackgroundTrackLoop() ) {
				S_StopBackgroundTrack();
				return;
			}
		}
	}
}


/*
======================
S_FreeOldestSound
======================
*/

void S_FreeOldestSound() {
	int	i, oldest, used;
	sfx_t	*sfx;
	sndBuffer	*buffer, *nbuffer;

	oldest = Com_Milliseconds();
	used = 0;

	for (i=1 ; i < s_numSfx ; i++) {
		sfx = &s_knownSfx[i];
		if (sfx->inMemory && sfx->lastTimeUsed<oldest) {
			used = i;
			oldest = sfx->lastTimeUsed;
		}
	}

	sfx = &s_knownSfx[used];

	Com_DPrintf("S_FreeOldestSound: freeing sound %s\n", sfx->soundName);

	buffer = sfx->soundData;
	while(buffer != NULL) {
		nbuffer = buffer->next;
		SND_free(buffer);
		buffer = nbuffer;
	}
	sfx->inMemory = qfalse;
	sfx->soundData = NULL;
}
