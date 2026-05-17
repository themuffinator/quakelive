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
/*
** linux_joystick.c
**
** This file contains ALL Linux specific stuff having to do with the
** Joystick input.  When a port is being made the following functions
** must be implemented by the port:
**
** Authors: mkv, bk
**
*/

#include <linux/joystick.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>  // bk001204

#include "../client/client.h"
#include "linux_local.h"

#define LINUX_JOYSTICK_MAX_DEVICES 4
#define LINUX_JOYSTICK_MAX_BUTTONS 32
#define LINUX_JOYSTICK_MAX_AXES 8
#define LINUX_JOYSTICK_AXIS_KEY_BITS ( LINUX_JOYSTICK_MAX_AXES * 2 )

/* We translate axes movement into keypresses. */
static int joy_keys[LINUX_JOYSTICK_AXIS_KEY_BITS] = {
	K_LEFTARROW, K_RIGHTARROW,
	K_UPARROW, K_DOWNARROW,
	K_JOY16, K_JOY17,
	K_JOY18, K_JOY19,
	K_JOY20, K_JOY21,
	K_JOY22, K_JOY23,

	K_JOY24, K_JOY25,
	K_JOY26, K_JOY27
};

/* Our file descriptor for the joystick device. */
static int joy_fd = -1;
static int joy_axes_state[LINUX_JOYSTICK_MAX_AXES];
static unsigned int joy_old_axes;
static unsigned int joy_button_state;

// bk001130 - from linux_glimp.c
extern cvar_t *in_joystick;
extern cvar_t *in_joystickDebug;
extern cvar_t *joy_threshold;

void IN_ShutdownJoystick( void );

/*
================
IN_ClearJoystickState
================
*/
static void IN_ClearJoystickState( void ) {
	Com_Memset( joy_axes_state, 0, sizeof( joy_axes_state ) );
	joy_old_axes = 0;
	joy_button_state = 0;
}

/*
================
IN_ReleaseJoystickKeys
================
*/
static void IN_ReleaseJoystickKeys( void ) {
	int i;

	for ( i = 0; i < LINUX_JOYSTICK_MAX_BUTTONS; i++ ) {
		if ( joy_button_state & ( 1u << i ) ) {
			Sys_QueEvent( 0, SE_KEY, K_JOY1 + i, qfalse, 0, NULL );
		}
	}

	for ( i = 0; i < LINUX_JOYSTICK_AXIS_KEY_BITS; i++ ) {
		if ( joy_old_axes & ( 1u << i ) ) {
			Sys_QueEvent( 0, SE_KEY, joy_keys[i], qfalse, 0, NULL );
		}
	}
}

/*
================
IN_TryOpenJoystick
================
*/
static qboolean IN_TryOpenJoystick( const char *filename ) {
	struct js_event event;
	char axes;
	char buttons;
	char name[128];
	int n;

	joy_fd = open( filename, O_RDONLY | O_NONBLOCK );
	if ( joy_fd == -1 ) {
		return qfalse;
	}

	Com_Printf( "Joystick %s found\n", filename );

	/* Get rid of initialization messages. */
	while ( 1 ) {
		n = read( joy_fd, &event, sizeof( event ) );
		if ( n != sizeof( event ) ) {
			break;
		}

		if ( !( event.type & JS_EVENT_INIT ) ) {
			break;
		}
	}

	axes = 0;
	buttons = 0;
	name[0] = '\0';

	ioctl( joy_fd, JSIOCGAXES, &axes );
	ioctl( joy_fd, JSIOCGBUTTONS, &buttons );

	if ( ioctl( joy_fd, JSIOCGNAME( sizeof( name ) ), name ) < 0 ) {
		Q_strncpyz( name, "Unknown", sizeof( name ) );
	} else {
		name[sizeof( name ) - 1] = '\0';
	}

	Com_Printf( "Name:    %s\n", name );
	Com_Printf( "Axes:    %d\n", axes );
	Com_Printf( "Buttons: %d\n", buttons );

	Cvar_Set( "ui_joyavail", "1" );
	return qtrue;
}

/**********************************************/
/* Joystick routines.                         */
/**********************************************/

/*
================
IN_StartupJoystick
================
*/
// bk001130 - from cvs1.17 (mkv), removed from linux_glimp.c
void IN_StartupJoystick( void ) {
	const char *deviceFormats[] = {
		"/dev/input/js%d",
		"/dev/js%d"
	};
	char filename[PATH_MAX];
	int formatIndex;
	int deviceIndex;

	IN_ShutdownJoystick();
	Cvar_Set( "ui_joyavail", "0" );

	if ( !in_joystick->integer ) {
		Com_Printf( "Joystick is not active.\n" );
		return;
	}

	for ( formatIndex = 0; formatIndex < ARRAY_LEN( deviceFormats ); formatIndex++ ) {
		for ( deviceIndex = 0; deviceIndex < LINUX_JOYSTICK_MAX_DEVICES; deviceIndex++ ) {
			Com_sprintf( filename, sizeof( filename ), deviceFormats[formatIndex], deviceIndex );
			if ( IN_TryOpenJoystick( filename ) ) {
				return;
			}
		}
	}

	Com_Printf( "No joystick found.\n" );
}

/*
================
IN_ShutdownJoystick
================
*/
void IN_ShutdownJoystick( void ) {
	IN_ReleaseJoystickKeys();
	IN_ClearJoystickState();

	if ( joy_fd != -1 ) {
		close( joy_fd );
		joy_fd = -1;
	}

	Cvar_Set( "ui_joyavail", "0" );
}

/*
================
IN_JoyMove
================
*/
void IN_JoyMove( void ) {
	unsigned int axes;
	int i;

	if ( joy_fd == -1 ) {
		return;
	}

	/* Empty the queue, dispatching button presses immediately
	 * and updating the instantaneous state for the axes.
	 */
	while ( 1 ) {
		struct js_event event;
		int n;
		unsigned char eventType;

		n = read( joy_fd, &event, sizeof( event ) );
		if ( n == -1 ) {
			break;
		}
		if ( n != sizeof( event ) ) {
			break;
		}

		eventType = event.type & ~JS_EVENT_INIT;
		if ( eventType == JS_EVENT_BUTTON ) {
			unsigned int buttonMask;

			if ( event.number >= LINUX_JOYSTICK_MAX_BUTTONS ) {
				continue;
			}

			buttonMask = 1u << event.number;
			if ( event.value ) {
				if ( !( joy_button_state & buttonMask ) ) {
					Sys_QueEvent( 0, SE_KEY, K_JOY1 + event.number, qtrue, 0, NULL );
				}
				joy_button_state |= buttonMask;
			} else {
				if ( joy_button_state & buttonMask ) {
					Sys_QueEvent( 0, SE_KEY, K_JOY1 + event.number, qfalse, 0, NULL );
				}
				joy_button_state &= ~buttonMask;
			}
		} else if ( eventType == JS_EVENT_AXIS ) {
			if ( event.number >= LINUX_JOYSTICK_MAX_AXES ) {
				continue;
			}

			joy_axes_state[event.number] = event.value;
		} else if ( in_joystickDebug && in_joystickDebug->integer ) {
			Com_Printf( "Unknown joystick event type %d\n", event.type );
		}
	}

	/* Translate our instantaneous state to bits. */
	axes = 0;
	for ( i = 0; i < LINUX_JOYSTICK_MAX_AXES; i++ ) {
		float f = ( (float)joy_axes_state[i] ) / 32767.0f;

		if ( f < -joy_threshold->value ) {
			axes |= ( 1u << ( i * 2 ) );
		} else if ( f > joy_threshold->value ) {
			axes |= ( 1u << ( ( i * 2 ) + 1 ) );
		}
	}

	/* Time to update axes state based on old vs. new. */
	for ( i = 0; i < LINUX_JOYSTICK_AXIS_KEY_BITS; i++ ) {
		if ( ( axes & ( 1u << i ) ) && !( joy_old_axes & ( 1u << i ) ) ) {
			Sys_QueEvent( 0, SE_KEY, joy_keys[i], qtrue, 0, NULL );
		}

		if ( !( axes & ( 1u << i ) ) && ( joy_old_axes & ( 1u << i ) ) ) {
			Sys_QueEvent( 0, SE_KEY, joy_keys[i], qfalse, 0, NULL );
		}
	}

	/* Save for future generations. */
	joy_old_axes = axes;
}
