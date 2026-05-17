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
#include "../client/client.h"

static cvar_t	*in_mouse;
static cvar_t	*in_nograb;
static cvar_t	*in_joystick;
static cvar_t	*in_debugJoystick;
static cvar_t	*joy_threshold;
static qboolean	in_nullInputInitialized;

/*
================
IN_NullTouchCompatibilityCvars
================
*/
static void IN_NullTouchCompatibilityCvars( void ) {
	(void)in_mouse;
	(void)in_nograb;
	(void)in_joystick;
	(void)in_debugJoystick;
	(void)joy_threshold;
}

/*
================
IN_NullRefreshCompatibilityState
================
*/
static void IN_NullRefreshCompatibilityState( void ) {
	if ( in_joystick ) {
		in_joystick->modified = qfalse;
	}

	Cvar_Set( "ui_joyavail", "0" );
	IN_NullTouchCompatibilityCvars();
}

/*
================
IN_Init
================
*/
void IN_Init( void ) {
	in_mouse = Cvar_Get( "in_mouse", "0", CVAR_ARCHIVE );
	in_nograb = Cvar_Get( "in_nograb", "0", CVAR_TEMP );
	in_joystick = Cvar_Get( "in_joystick", "0", CVAR_ARCHIVE|CVAR_LATCH );
	in_debugJoystick = Cvar_Get( "in_debugjoystick", "0", CVAR_TEMP );
	joy_threshold = Cvar_Get( "joy_threshold", "0.15", CVAR_ARCHIVE );

	in_nullInputInitialized = qtrue;
	IN_NullRefreshCompatibilityState();
}

/*
================
IN_Frame
================
*/
void IN_Frame( void ) {
	IN_NullRefreshCompatibilityState();
}

/*
================
IN_Shutdown
================
*/
void IN_Shutdown( void ) {
	IN_NullRefreshCompatibilityState();
	in_nullInputInitialized = qfalse;
}

/*
================
Sys_SendKeyEvents
================
*/
void Sys_SendKeyEvents( void ) {
	if ( in_nullInputInitialized ) {
		IN_NullRefreshCompatibilityState();
	}
}
