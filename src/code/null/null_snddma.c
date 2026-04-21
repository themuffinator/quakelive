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

// snddma_null.c
// all other sound mixing is portable

#include "../client/client.h"

/*
================
SNDDMA_Init
================
*/
qboolean SNDDMA_Init( void ) {
	return qfalse;
}

/*
================
SNDDMA_GetDMAPos
================
*/
int	SNDDMA_GetDMAPos( void ) {
	return 0;
}

/*
================
SNDDMA_Shutdown
================
*/
void SNDDMA_Shutdown( void ) {
}

/*
================
SNDDMA_BeginPainting
================
*/
void SNDDMA_BeginPainting( void ) {
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
