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
// win_input.c -- win32 mouse and joystick code
// 02/21/97 JCB Added extended DirectInput code to support external controllers.

#include "../client/client.h"
#include "win_local.h"
#include "win_rawinput_shared.h"
#include <math.h>
#include <stdlib.h>


typedef struct {
	int			oldButtonState;
	int			oldCursorX;
	int			oldCursorY;

	qboolean	mouseActive;
	qboolean	mouseInitialized;
	qboolean	mouseStartupDelayed; // delay mouse init to try again when we have a window
	qboolean	cursorCaptured;
} WinMouseVars_t;

static WinMouseVars_t s_wmv;
static qboolean s_systemCursorHiddenForGameCursor;

#define MAX_RAW_INPUT_SAMPLES 0x1ff

typedef struct {
	qboolean					registered;
	int							sampleCount;
	qlr_win32_raw_mouse_sample_t	samples[MAX_RAW_INPUT_SAMPLES];
} WinRawInputVars_t;

static WinRawInputVars_t s_wri;

static int	window_center_x, window_center_y;

//
// MIDI definitions
//
static void IN_StartupMIDI( void );
static void IN_ShutdownMIDI( void );

#define MAX_MIDIIN_DEVICES	8

typedef struct {
	int			numDevices;
	MIDIINCAPS	caps[MAX_MIDIIN_DEVICES];

	HMIDIIN		hMidiIn;
} MidiInfo_t;

static MidiInfo_t s_midiInfo;

//
// Joystick definitions
//
#define	JOY_MAX_AXES		6				// X, Y, Z, R, U, V

typedef struct {
	qboolean	avail;
	int			id;			// joystick number
	JOYCAPS		jc;

	int			oldbuttonstate;
	int			oldpovstate;
	int			oldmoveaxisstate[2];

	JOYINFOEX	ji;
} joystickInfo_t;

static	joystickInfo_t	joy;



cvar_t	*in_midi;
cvar_t	*in_midiport;
cvar_t	*in_midichannel;
cvar_t	*in_mididevice;

cvar_t	*in_debugMouse;
cvar_t	*in_mouse;
cvar_t	*in_mouseMode;
cvar_t  *in_logitechbug;
cvar_t	*in_nograb;
cvar_t	*in_raw_useWindowHandle;
cvar_t	*in_joystick;
cvar_t	*in_joystickInverted;
cvar_t	*in_joyBallScale;
cvar_t	*in_debugJoystick;
cvar_t	*joy_threshold;
cvar_t	*in_joyHorizViewSensitivity;
cvar_t	*in_joyVertViewSensitivity;
cvar_t	*in_joyHorizViewDeadzone;
cvar_t	*in_joyVertViewDeadzone;
cvar_t	*in_joyHorizMoveDeadzone;
cvar_t	*in_joyVertMoveDeadzone;

qboolean	in_appactive;

// forward-referenced functions
void IN_StartupJoystick (void);
void IN_JoyMove(void);

static void MidiInfo_f( void );
static void ListInputDevices_f( void );

/*
================
IN_GameCursorActive

Returns whether the renderer is drawing a Quake cursor instead of relying on
the host/browser cursor.
================
*/
qboolean IN_GameCursorActive( void ) {
	if ( !in_appactive ) {
		return qfalse;
	}

	if ( cls.keyCatchers & KEYCATCH_BROWSER ) {
		return qfalse;
	}

	return ( cls.keyCatchers & ( KEYCATCH_UI | KEYCATCH_CGAME ) ) ? qtrue : qfalse;
}

/*
================
IN_UpdateSystemCursor

Keeps the Win32 cursor hidden while UI or cgame owns the visible game cursor.
================
*/
void IN_UpdateSystemCursor( void ) {
	if ( IN_GameCursorActive() ) {
		SetCursor( NULL );
		s_systemCursorHiddenForGameCursor = qtrue;
		return;
	}

	if ( s_systemCursorHiddenForGameCursor ) {
		SetCursor( LoadCursor( NULL, IDC_ARROW ) );
		s_systemCursorHiddenForGameCursor = qfalse;
	}
}

/*
================
IN_GetClampedWindowRect

Returns the game window rect clipped to the same virtual-screen bounds used by
the retail Win32 mouse activation path.
================
*/
static qboolean IN_GetClampedWindowRect( RECT *window_rect ) {
	int	width, height;

	if ( !window_rect || !g_wv.hWnd ) {
		return qfalse;
	}

	width = GetSystemMetrics( SM_CXVIRTUALSCREEN );
	height = GetSystemMetrics( SM_CYVIRTUALSCREEN );

	GetWindowRect( g_wv.hWnd, window_rect );
	if ( window_rect->left < 0 ) {
		window_rect->left = 0;
	}
	if ( window_rect->top < 0 ) {
		window_rect->top = 0;
	}
	if ( window_rect->right >= width ) {
		window_rect->right = width - 1;
	}
	if ( window_rect->bottom >= height - 1 ) {
		window_rect->bottom = height - 1;
	}

	return qtrue;
}

/*
================
IN_CursorCaptureRequested

Returns qtrue for UI/browser/cgame cursor lanes that need the host cursor
confined to the game window without enabling relative gameplay mouse deltas.
================
*/
static qboolean IN_CursorCaptureRequested( void ) {
	if ( !in_appactive || !g_wv.hWnd ) {
		return qfalse;
	}

	if ( in_nograb && in_nograb->integer ) {
		return qfalse;
	}

	return ( cls.keyCatchers & ( KEYCATCH_UI | KEYCATCH_CGAME | KEYCATCH_BROWSER ) ) ? qtrue : qfalse;
}

/*
================
IN_ActivateCursorCapture
================
*/
static void IN_ActivateCursorCapture( void ) {
	RECT	window_rect;

	if ( !IN_GetClampedWindowRect( &window_rect ) ) {
		return;
	}

	SetCapture( g_wv.hWnd );
	ClipCursor( &window_rect );
	s_wmv.cursorCaptured = qtrue;
}

/*
================
IN_DeactivateCursorCapture
================
*/
static void IN_DeactivateCursorCapture( void ) {
	if ( !s_wmv.cursorCaptured ) {
		return;
	}

	ClipCursor( NULL );
	ReleaseCapture();
	s_wmv.cursorCaptured = qfalse;
}

/*
================
IN_UpdateCursorCapture
================
*/
static void IN_UpdateCursorCapture( void ) {
	if ( IN_CursorCaptureRequested() ) {
		IN_ActivateCursorCapture();
	} else {
		IN_DeactivateCursorCapture();
	}
}

/*
============================================================

WIN32 MOUSE CONTROL

============================================================
*/

/*
================
IN_InitWin32Mouse
================
*/
void IN_InitWin32Mouse( void ) 
{
}

/*
================
IN_ShutdownWin32Mouse
================
*/
void IN_ShutdownWin32Mouse( void ) {
}

/*
================
IN_ActivateWin32Mouse
================
*/
void IN_ActivateWin32Mouse( void ) {
	RECT		window_rect;

	if ( !IN_GetClampedWindowRect( &window_rect ) ) {
		return;
	}

	window_center_x = (window_rect.right + window_rect.left)/2;
	window_center_y = (window_rect.top + window_rect.bottom)/2;

	SetCursorPos (window_center_x, window_center_y);
	Cvar_SetValue( "vid_xpos", (float)window_rect.left );
	Cvar_SetValue( "vid_ypos", (float)window_rect.top );

	SetCapture ( g_wv.hWnd );
	ClipCursor (&window_rect);
	s_wmv.cursorCaptured = qtrue;
	while (ShowCursor (FALSE) >= 0)
		;
}

/*
================
IN_DeactivateWin32Mouse
================
*/
void IN_DeactivateWin32Mouse( void ) 
{
	IN_DeactivateCursorCapture();
	while (ShowCursor (TRUE) < 0)
		;
	IN_UpdateSystemCursor();
}

/*
================
IN_Win32Mouse
================
*/
void IN_Win32Mouse( int *mx, int *my ) {
	POINT		current_pos;

	// find mouse movement
	GetCursorPos (&current_pos);

	// force the mouse to the center, so there's room to move
	SetCursorPos (window_center_x, window_center_y);

	*mx = current_pos.x - window_center_x;
	*my = current_pos.y - window_center_y;
}

/*
================
IN_ShouldUseRelativeMouse
================
*/
static qboolean IN_ShouldUseRelativeMouse( void ) {
	if ( !s_wmv.mouseActive ) {
		return qfalse;
	}

	if ( cls.keyCatchers & ~( KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS ) ) {
		return qfalse;
	}

	if ( in_nograb && in_nograb->integer ) {
		return qfalse;
	}

	return qtrue;
}

/*
================
IN_WindowMouse
================
*/
static void IN_WindowMouse( void ) {
	POINT	current_pos;

	if ( !g_wv.hWnd ) {
		return;
	}

	GetCursorPos( &current_pos );
	ScreenToClient( g_wv.hWnd, &current_pos );

	if ( current_pos.x == s_wmv.oldCursorX && current_pos.y == s_wmv.oldCursorY ) {
		return;
	}

	s_wmv.oldCursorX = current_pos.x;
	s_wmv.oldCursorY = current_pos.y;
	Sys_QueEvent( 0, SE_MOUSE, current_pos.x, current_pos.y, 0, NULL );
}

/*
================
IN_SetMouseMode
================
*/
static void IN_SetMouseMode( const char *mode ) {
	if ( !mode ) {
		mode = "undefined";
	}

	if ( in_mouseMode ) {
		Cvar_Set( "in_mouseMode", mode );
	}
}

/*
================
IN_ClearRawInputSamples
================
*/
static void IN_ClearRawInputSamples( void ) {
	s_wri.sampleCount = 0;
}

/*
================
IN_RegisterRawInput
================
*/
static qboolean IN_RegisterRawInput( qboolean removeDevice ) {
	RAWINPUTDEVICE rawInputDevice;

	if ( !removeDevice && !g_wv.hWnd ) {
		return qfalse;
	}

	QLR_Win32RawInputBuildRegistration( &rawInputDevice,
		g_wv.hWnd,
		in_raw_useWindowHandle && in_raw_useWindowHandle->integer,
		removeDevice );

	if ( !RegisterRawInputDevices( &rawInputDevice, 1, sizeof( rawInputDevice ) ) ) {
		return qfalse;
	}

	s_wri.registered = removeDevice ? qfalse : qtrue;
	return qtrue;
}

/*
================
IN_InitRawInput
================
*/
static qboolean IN_InitRawInput( void ) {
	if ( !IN_RegisterRawInput( qfalse ) ) {
		Com_Printf( "RAW MOUSE INIT FAIL!" );
		return qfalse;
	}

	IN_SetMouseMode( "win32(Raw)" );
	return qtrue;
}

/*
================
IN_ShutdownRawInput
================
*/
static void IN_ShutdownRawInput( void ) {
	if ( !s_wri.registered ) {
		IN_ClearRawInputSamples();
		return;
	}

	if ( !IN_RegisterRawInput( qtrue ) ) {
		Com_Printf( "RAW MOUSE SHUTDOWN FAIL!" );
	}

	IN_ClearRawInputSamples();
}

/*
================
IN_RawInputAppendSample
================
*/
static void IN_RawInputAppendSample( const qlr_win32_raw_mouse_sample_t *sample ) {
	if ( !sample ) {
		return;
	}

	if ( cls.keyCatchers & ~KEYCATCH_RETAIL_MOUSEPASS ) {
		IN_ClearRawInputSamples();
		return;
	}

	if ( s_wri.sampleCount >= MAX_RAW_INPUT_SAMPLES ) {
		if ( in_debugMouse && in_debugMouse->integer ) {
			Com_Printf( "Raw Input buffer overflow!\n" );
		}
		return;
	}

	s_wri.samples[s_wri.sampleCount] = *sample;
	s_wri.sampleCount++;
}

/*
================
IN_QueueRawInputButtons
================
*/
static void IN_QueueRawInputButtons( const qlr_win32_raw_mouse_sample_t *sample ) {
	int		down[QLR_WIN32_RAW_INPUT_MAX_EVENTS];
	int		keys[QLR_WIN32_RAW_INPUT_MAX_EVENTS];
	int		eventCount;
	int		i;

	if ( !sample ) {
		return;
	}

	eventCount = QLR_Win32RawInputTranslateButtonFlags(
		sample->buttonFlags,
		sample->wheelDelta,
		keys,
		down,
		QLR_WIN32_RAW_INPUT_MAX_EVENTS );

	for ( i = 0; i < eventCount; i++ ) {
		Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, keys[i], down[i], 0, NULL );
	}
}

/*
================
IN_RawInputIsActive
================
*/
qboolean IN_RawInputIsActive( void ) {
	if ( !in_mouse ) {
		return qfalse;
	}

	return ( in_mouse->integer == 2 && s_wmv.mouseActive && s_wri.registered ) ? qtrue : qfalse;
}

/*
================
IN_ShouldProcessWin32MouseButtons

Returns qtrue when the Win32 button-state messages should synthesize mouse
key events. Retail skips them only for the raw relative gameplay lane, while
menu and cgame catchers still receive the Win32 button messages.
================
*/
qboolean IN_ShouldProcessWin32MouseButtons( void ) {
	if ( !IN_RawInputIsActive() ) {
		return qtrue;
	}

	if ( !IN_ShouldUseRelativeMouse() ) {
		return qtrue;
	}

	return qfalse;
}

/*
================
IN_RawInputEvent
================
*/
void IN_RawInputEvent( WPARAM wParam, LPARAM lParam ) {
	BYTE						stackBuffer[0x400];
	qlr_win32_raw_mouse_sample_t	sample;
	PRAWINPUT					rawInput;
	PRAWINPUT					rawInputHeap;
	UINT						rawInputSize;
	UINT						sizeResult;

	if ( !s_wmv.mouseInitialized || !in_mouse || in_mouse->integer != 2 || !s_wri.registered ) {
		return;
	}

	if ( GET_RAWINPUT_CODE_WPARAM( wParam ) != RIM_INPUT ) {
		return;
	}

	rawInput = (PRAWINPUT)stackBuffer;
	rawInputHeap = NULL;
	rawInputSize = 0;

	sizeResult = GetRawInputData(
		(HRAWINPUT)lParam,
		RID_INPUT,
		NULL,
		&rawInputSize,
		sizeof( RAWINPUTHEADER ) );
	if ( sizeResult == (UINT)-1 ) {
		Com_Printf( "GetRawInputData returned an error while getting size: %08x\n", GetLastError() );
		return;
	}

	if ( rawInputSize < 1 ) {
		return;
	}

	if ( rawInputSize > sizeof( stackBuffer ) ) {
		rawInputHeap = (PRAWINPUT)malloc( rawInputSize );
		if ( !rawInputHeap ) {
			return;
		}
		rawInput = rawInputHeap;
	}

	sizeResult = GetRawInputData(
		(HRAWINPUT)lParam,
		RID_INPUT,
		rawInput,
		&rawInputSize,
		sizeof( RAWINPUTHEADER ) );
	if ( sizeResult == (UINT)-1 ) {
		Com_Printf( "GetRawInputData returned an error: %08x\n", GetLastError() );
		if ( rawInputHeap ) {
			free( rawInputHeap );
		}
		return;
	}

	if ( sizeResult != rawInputSize ) {
		Com_Printf( "GetRawInputData doesn't return correct size ! (er = %08x)\n", GetLastError() );
	}

	if ( QLR_Win32RawInputExtractMouseSample( rawInput, &sample ) ) {
		IN_RawInputAppendSample( &sample );
	}

	if ( rawInputHeap ) {
		free( rawInputHeap );
	}
}

/*
================
IN_RawInputMouse
================
*/
static void IN_RawInputMouse( int *mx, int *my ) {
	int	i;

	*mx = 0;
	*my = 0;

	if ( !s_wri.sampleCount ) {
		if ( s_wmv.mouseActive && ( !in_nograb || !in_nograb->integer ) ) {
			SetCursorPos( window_center_x, window_center_y );
		}
		return;
	}

	for ( i = 0; i < s_wri.sampleCount; i++ ) {
		*mx += s_wri.samples[i].dx;
		*my += s_wri.samples[i].dy;
		IN_QueueRawInputButtons( &s_wri.samples[i] );
	}

	IN_ClearRawInputSamples();

	if ( s_wmv.mouseActive && ( !in_nograb || !in_nograb->integer ) ) {
		SetCursorPos( window_center_x, window_center_y );
	}
}


/*
============================================================

DIRECT INPUT MOUSE CONTROL

============================================================
*/

#undef DEFINE_GUID

#define DEFINE_GUID(name, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8) \
        EXTERN_C const GUID name \
                = { l, w1, w2, { b1, b2,  b3,  b4,  b5,  b6,  b7,  b8 } }

DEFINE_GUID(GUID_SysMouse,   0x6F1D2B60,0xD5A0,0x11CF,0xBF,0xC7,0x44,0x45,0x53,0x54,0x00,0x00);
DEFINE_GUID(GUID_XAxis,   0xA36D02E0,0xC9F3,0x11CF,0xBF,0xC7,0x44,0x45,0x53,0x54,0x00,0x00);
DEFINE_GUID(GUID_YAxis,   0xA36D02E1,0xC9F3,0x11CF,0xBF,0xC7,0x44,0x45,0x53,0x54,0x00,0x00);
DEFINE_GUID(GUID_ZAxis,   0xA36D02E2,0xC9F3,0x11CF,0xBF,0xC7,0x44,0x45,0x53,0x54,0x00,0x00);


#define DINPUT_BUFFERSIZE           0x200
#ifndef DIMOFS_BUTTON4
#define DIMOFS_BUTTON4              (DIMOFS_BUTTON0 + 4)
#endif
#ifndef DIMOFS_BUTTON5
#define DIMOFS_BUTTON5              (DIMOFS_BUTTON0 + 5)
#endif
#ifndef DIMOFS_BUTTON6
#define DIMOFS_BUTTON6              (DIMOFS_BUTTON0 + 6)
#endif
#ifndef DIMOFS_BUTTON7
#define DIMOFS_BUTTON7              (DIMOFS_BUTTON0 + 7)
#endif
#define iDirectInput8Create(a,b,c,d,e)	pDirectInput8Create(a,b,c,d,e)

typedef HRESULT (WINAPI *DirectInput8CreateProc_t)(HINSTANCE hinst, DWORD dwVersion,
	REFIID riidltf, LPVOID *ppvOut, LPUNKNOWN punkOuter);

static HINSTANCE hInstDI;
static DirectInput8CreateProc_t pDirectInput8Create;

typedef struct MYDATA {
	LONG  lX;                   // X axis goes here
	LONG  lY;                   // Y axis goes here
	LONG  lZ;                   // Z axis goes here
	BYTE  bButtonA;             // One button goes here
	BYTE  bButtonB;             // Another button goes here
	BYTE  bButtonC;             // Another button goes here
	BYTE  bButtonD;             // Another button goes here
	BYTE  bButtonE;             // Another button goes here
	BYTE  bButtonF;             // Another button goes here
	BYTE  bButtonG;             // Another button goes here
	BYTE  bButtonH;             // Another button goes here
} MYDATA;

static DIOBJECTDATAFORMAT rgodf[] = {
  { &GUID_XAxis,    FIELD_OFFSET(MYDATA, lX),       DIDFT_AXIS | DIDFT_ANYINSTANCE,   0,},
  { &GUID_YAxis,    FIELD_OFFSET(MYDATA, lY),       DIDFT_AXIS | DIDFT_ANYINSTANCE,   0,},
  { &GUID_ZAxis,    FIELD_OFFSET(MYDATA, lZ),       0x80000000 | DIDFT_AXIS | DIDFT_ANYINSTANCE,   0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonA), DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonB), DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonC), 0x80000000 | DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonD), 0x80000000 | DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonE), 0x80000000 | DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonF), 0x80000000 | DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonG), 0x80000000 | DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
  { 0,              FIELD_OFFSET(MYDATA, bButtonH), 0x80000000 | DIDFT_BUTTON | DIDFT_ANYINSTANCE, 0,},
};

#define NUM_OBJECTS (sizeof(rgodf) / sizeof(rgodf[0]))

// NOTE TTimo: would be easier using c_dfDIMouse or c_dfDIMouse2 
static DIDATAFORMAT	df = {
	sizeof(DIDATAFORMAT),       // this structure
	sizeof(DIOBJECTDATAFORMAT), // size of object data format
	DIDF_RELAXIS,               // absolute axis coordinates
	sizeof(MYDATA),             // device data size
	NUM_OBJECTS,                // number of objects
	rgodf,                      // and here they are
};

static LPDIRECTINPUT8		g_pdi;
static LPDIRECTINPUTDEVICE8	g_pMouse;

static const GUID ql_IID_IDirectInput8A = {
	0xBF798030, 0x483A, 0x4DA2, { 0xAA, 0x99, 0x5D, 0x64, 0xED, 0x36, 0x97, 0x00 }
};

void IN_DIMouse( int *mx, int *my );

/*
========================
IN_InitDIMouse
========================
*/
qboolean IN_InitDIMouse( void ) {
    HRESULT		hr;
	int			x, y;
	DIPROPDWORD	dipdw = {
		{
			sizeof(DIPROPDWORD),        // diph.dwSize
			sizeof(DIPROPHEADER),       // diph.dwHeaderSize
			0,                          // diph.dwObj
			DIPH_DEVICE,                // diph.dwHow
		},
		DINPUT_BUFFERSIZE,              // dwData
	};

	Com_Printf( "Initializing DirectInput...\n");

	if (!hInstDI) {
		hInstDI = LoadLibrary("dinput8.dll");
		
		if (hInstDI == NULL) {
			Com_Printf ("Couldn't load dinput8.dll\n");
			return qfalse;
		}
	}

	if (!pDirectInput8Create) {
		pDirectInput8Create = (DirectInput8CreateProc_t)GetProcAddress(hInstDI,"DirectInput8Create");

		if (!pDirectInput8Create) {
			Com_Printf ("Couldn't get DI8 proc addr\n");
			return qfalse;
		}
	}

	// register with DirectInput and get an IDirectInput to play with.
	hr = iDirectInput8Create( g_wv.hInstance, DIRECTINPUT_VERSION, &ql_IID_IDirectInput8A, (LPVOID *)&g_pdi, NULL);

	if (FAILED(hr)) {
		Com_Printf ("DirectInput8Create failed\n");
		return qfalse;
	}

	// obtain an interface to the system mouse device.
	hr = IDirectInput8_CreateDevice(g_pdi, &GUID_SysMouse, &g_pMouse, NULL);

	if (FAILED(hr)) {
		Com_Printf ("Couldn't open DI mouse device\n");
		return qfalse;
	}

	// set the data format to "mouse format".
	hr = IDirectInputDevice8_SetDataFormat(g_pMouse, &df);

	if (FAILED(hr)) 	{
		Com_Printf ("Couldn't set DI mouse format\n");
		return qfalse;
	}

	// set the cooperativity level.
	hr = IDirectInputDevice8_SetCooperativeLevel(g_pMouse, g_wv.hWnd,
			DISCL_EXCLUSIVE | DISCL_FOREGROUND);

	// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=50
	if (FAILED(hr)) {
		Com_Printf ("Couldn't set DI coop level\n");
		return qfalse;
	}


	// set the buffer size to DINPUT_BUFFERSIZE elements.
	// the buffer size is a DWORD property associated with the device
	hr = IDirectInputDevice8_SetProperty(g_pMouse, DIPROP_BUFFERSIZE, &dipdw.diph);

	if (FAILED(hr)) {
		Com_Printf ("Couldn't set DI buffersize\n");
		return qfalse;
	}

	// clear any pending samples
	IN_DIMouse( &x, &y );
	IN_DIMouse( &x, &y );

	IN_SetMouseMode( "DirectInput" );
	Com_Printf( "DirectInput initialized.\n");
	return qtrue;
}

/*
==========================
IN_ShutdownDIMouse
==========================
*/
void IN_ShutdownDIMouse( void ) {
    if (g_pMouse) {
		IDirectInputDevice8_Release(g_pMouse);
		g_pMouse = NULL;
	}

    if (g_pdi) {
		IDirectInput8_Release(g_pdi);
		g_pdi = NULL;
	}
}

/*
==========================
IN_ActivateDIMouse
==========================
*/
void IN_ActivateDIMouse( void ) {
	HRESULT		hr;

	if (!g_pMouse) {
		return;
	}

	// we may fail to reacquire if the window has been recreated
	hr = IDirectInputDevice8_Acquire( g_pMouse );
	if (FAILED(hr)) {
		if ( !IN_InitDIMouse() ) {
			Com_Printf( "Falling back on raw input...\n" );
			IN_ShutdownDIMouse();
			Cvar_Set( "in_mouse", "2" );
			if ( !IN_InitRawInput() ) {
				Com_Printf( "Falling back to Win32 mouse support...\n" );
				Cvar_Set( "in_mouse", "-1" );
				IN_SetMouseMode( "win32" );
			}
		}
	}
}

/*
==========================
IN_DeactivateDIMouse
==========================
*/
void IN_DeactivateDIMouse( void ) {
	if (!g_pMouse) {
		return;
	}
	IDirectInputDevice8_Unacquire( g_pMouse );
}


/*
===================
IN_DIMouse
===================
*/
void IN_DIMouse( int *mx, int *my ) {
	DIDEVICEOBJECTDATA	od[DINPUT_BUFFERSIZE];
	DWORD				dwElements;
	HRESULT				hr;
	int					i;
	int					key;
	int					value;

	*mx = *my = 0;

	if ( !g_pMouse ) {
		return;
	}

	// fetch new events
	for ( ;; ) {
		dwElements = DINPUT_BUFFERSIZE;

		hr = IDirectInputDevice8_GetDeviceData( g_pMouse, sizeof( DIDEVICEOBJECTDATA ), od, &dwElements, 0 );
		if ((hr == DIERR_INPUTLOST) || (hr == DIERR_NOTACQUIRED)) {
			IDirectInputDevice8_Acquire(g_pMouse);
			return;
		}

		/* Unable to read data or no data available */
		if ( FAILED(hr) ) {
			break;
		}

		if ( hr == DI_BUFFEROVERFLOW ) {
			Com_Printf( "IN_DIMouse: DI_BUFFEROVERFLOW\n" );
		}

		if ( dwElements == 0 ) {
			break;
		}

		for ( i = 0; i < (int)dwElements; i++ ) {
			switch ( od[i].dwOfs ) {
			case DIMOFS_X:
				*mx += (int)od[i].dwData;
				break;
			case DIMOFS_Y:
				*my += (int)od[i].dwData;
				break;
			case DIMOFS_Z:
				value = (int)od[i].dwData;
				if ( value < 0 ) {
					Sys_QueEvent( od[i].dwTimeStamp, SE_KEY, K_MWHEELDOWN, qtrue, 0, NULL );
					Sys_QueEvent( od[i].dwTimeStamp, SE_KEY, K_MWHEELDOWN, qfalse, 0, NULL );
				} else if ( value > 0 ) {
					Sys_QueEvent( od[i].dwTimeStamp, SE_KEY, K_MWHEELUP, qtrue, 0, NULL );
					Sys_QueEvent( od[i].dwTimeStamp, SE_KEY, K_MWHEELUP, qfalse, 0, NULL );
				}
				break;
			default:
				if ( od[i].dwOfs >= DIMOFS_BUTTON0 && od[i].dwOfs <= DIMOFS_BUTTON7 ) {
					key = K_MOUSE1 + (int)( od[i].dwOfs - DIMOFS_BUTTON0 );
					Sys_QueEvent( od[i].dwTimeStamp, SE_KEY, key, ( od[i].dwData & 0x80 ) ? qtrue : qfalse, 0, NULL );
				}
				break;
			}
		}
	}
}

/*
============================================================

  MOUSE CONTROL

============================================================
*/

/*
===========
IN_ActivateMouse

Called when the window gains focus or changes in some way
===========
*/
void IN_ActivateMouse( void ) 
{
	if (!s_wmv.mouseInitialized ) {
		return;
	}
	if ( !in_mouse->integer ) 
	{
		s_wmv.mouseActive = qfalse;
		return;
	}
	if ( s_wmv.mouseActive ) 
	{
		return;
	}

	s_wmv.mouseActive = qtrue;

	if ( in_mouse->integer == 2 && !s_wri.registered ) {
		if ( !IN_InitRawInput() ) {
			Com_Printf( "Falling back to Win32 mouse support...\n" );
			Cvar_Set( "in_mouse", "-1" );
			IN_SetMouseMode( "win32" );
		}
	}

	if ( in_mouse->integer == 1 ) {
		IN_ActivateDIMouse();
	}
	IN_ActivateWin32Mouse();
}


/*
===========
IN_DeactivateMouse

Called when the window loses focus
===========
*/
void IN_DeactivateMouse( void ) {
	if (!s_wmv.mouseInitialized ) {
		IN_DeactivateCursorCapture();
		return;
	}
	if (!s_wmv.mouseActive ) {
		IN_DeactivateCursorCapture();
		return;
	}
	s_wmv.mouseActive = qfalse;

	IN_DeactivateDIMouse();
	IN_ShutdownRawInput();
	IN_DeactivateWin32Mouse();
	s_wmv.oldButtonState = 0;
}



/*
===========
IN_StartupMouse
===========
*/
void IN_StartupMouse( void ) 
{
	s_wmv.mouseInitialized = qfalse;
	s_wmv.mouseStartupDelayed = qfalse;
	s_wri.registered = qfalse;
	IN_ClearRawInputSamples();
	IN_SetMouseMode( "win32" );

	if ( in_mouse->integer == 0 ) {
		Com_Printf ("Mouse control not active.\n");
		return;
	}

	// nt4.0 direct input is screwed up
	if ( ( g_wv.osversion.dwPlatformId == VER_PLATFORM_WIN32_NT ) &&
		 ( g_wv.osversion.dwMajorVersion == 4 ) )
	{
		Com_Printf ("Disallowing DirectInput on NT 4.0\n");
		Cvar_Set( "in_mouse", "-1" );
	}

	if ( in_mouse->integer == -1 ) {
		Com_Printf ("Skipping check for DirectInput\n");
		s_wmv.mouseInitialized = qtrue;
		IN_InitWin32Mouse();
		return;
	}

	if ( !g_wv.hWnd ) {
		if ( in_mouse->integer == 1 ) {
			Com_Printf( "No window for DirectInput mouse init, delaying\n" );
		} else {
			Com_Printf( "No window for Raw Input mouse init, delaying\n" );
		}
		s_wmv.mouseStartupDelayed = qtrue;
		return;
	}

	if ( in_mouse->integer == 2 ) {
		if ( IN_InitRawInput() ) {
			s_wmv.mouseInitialized = qtrue;
			return;
		}

		Com_Printf( "Falling back to Win32 mouse support...\n" );
		Cvar_Set( "in_mouse", "-1" );
		s_wmv.mouseInitialized = qtrue;
		IN_InitWin32Mouse();
		return;
	}

	if ( in_mouse->integer == 1 ) {
		if ( IN_InitDIMouse() ) {
			s_wmv.mouseInitialized = qtrue;
			return;
		}

		Com_Printf( "Falling back on raw input...\n" );
		IN_ShutdownDIMouse();
		Cvar_Set( "in_mouse", "2" );

		if ( IN_InitRawInput() ) {
			s_wmv.mouseInitialized = qtrue;
			return;
		}

		Com_Printf( "Falling back to Win32 mouse support...\n" );
		Cvar_Set( "in_mouse", "-1" );
	}

	s_wmv.mouseInitialized = qtrue;
	IN_InitWin32Mouse();
}

/*
===========
IN_MouseEvent
===========
*/
void IN_MouseEvent (int mstate)
{
	int		i;

	if ( !s_wmv.mouseInitialized )
		return;

// perform button actions
	for  (i = 0 ; i < 8 ; i++ )
	{
		if ( (mstate & (1<<i)) &&
			!(s_wmv.oldButtonState & (1<<i)) )
		{
			Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, K_MOUSE1 + i, qtrue, 0, NULL );
		}

		if ( !(mstate & (1<<i)) &&
			(s_wmv.oldButtonState & (1<<i)) )
		{
			Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, K_MOUSE1 + i, qfalse, 0, NULL );
		}
	}	

	s_wmv.oldButtonState = mstate;
}


/*
===========
IN_MouseMove
===========
*/
void IN_MouseMove ( void ) {
	int		mx, my;

	if ( !IN_ShouldUseRelativeMouse() ) {
		IN_WindowMouse();
		return;
	}

	if ( in_mouse && in_mouse->integer == 2 && s_wri.registered ) {
		IN_RawInputMouse( &mx, &my );
	} else if ( g_pMouse ) {
		IN_DIMouse( &mx, &my );
	} else {
		IN_Win32Mouse( &mx, &my );
	}

	if ( !mx && !my ) {
		return;
	}

	Sys_QueEvent( 0, SE_MOUSE, mx, my, 0, NULL );
}


/*
=========================================================================

=========================================================================
*/

/*
===========
IN_Startup
===========
*/
void IN_Startup( void ) {
	Com_Printf ("\n------- Input Initialization -------\n");
	IN_StartupMouse ();
	IN_StartupJoystick ();
	IN_StartupMIDI();
	Com_Printf ("------------------------------------\n");

	in_mouse->modified = qfalse;
	in_joystick->modified = qfalse;
}

/*
===========
IN_Shutdown
===========
*/
void IN_Shutdown( void ) {
	IN_DeactivateMouse();
	IN_ShutdownRawInput();
	IN_ShutdownDIMouse();
	IN_ShutdownMIDI();
	Cmd_RemoveCommand("midiinfo" );
	Cmd_RemoveCommand("ListInputDevices" );
}


/*
===========
IN_Init
===========
*/
void IN_Init( void ) {
	// MIDI input controler variables
	in_midi					= Cvar_Get ("in_midi",					"0",		CVAR_ARCHIVE);
	in_midiport				= Cvar_Get ("in_midiport",				"1",		CVAR_ARCHIVE);
	in_midichannel			= Cvar_Get ("in_midichannel",			"1",		CVAR_ARCHIVE);
	in_mididevice			= Cvar_Get ("in_mididevice",			"0",		CVAR_ARCHIVE);

	Cmd_AddCommand( "midiinfo", MidiInfo_f );
	Cmd_AddCommand( "ListInputDevices", ListInputDevices_f );

	// mouse variables
	in_mouse				= Cvar_Get ("in_mouse",					"2",		CVAR_ARCHIVE|CVAR_LATCH|CVAR_CLOUD);
	in_debugMouse			= Cvar_Get ("in_debugMouse",			"0",		CVAR_TEMP);
	in_mouseMode			= Cvar_Get ("in_mouseMode",				"undefined",	CVAR_ROM | CVAR_TEMP | CVAR_CLOUD);
	in_logitechbug  = Cvar_Get ("in_logitechbug", "0", CVAR_ARCHIVE);
	in_nograb				= Cvar_Get ("in_nograb",				"0",		CVAR_TEMP);
	in_raw_useWindowHandle	= Cvar_Get ("in_raw_useWindowHandle",	"0",		CVAR_ARCHIVE);

	// joystick variables
	in_joystick				= Cvar_Get ("in_joystick",				"1",		CVAR_ARCHIVE|CVAR_LATCH);
	in_joystickInverted		= Cvar_Get ("in_joystick_inverted",		"0",		CVAR_ARCHIVE);
	in_joyBallScale			= Cvar_Get ("in_joyBallScale",			"1.0",		CVAR_ARCHIVE);
	in_debugJoystick		= Cvar_Get ("in_debugjoystick",			"0",		CVAR_TEMP);
	joy_threshold			= Cvar_Get ("joy_threshold",			"0.15",		CVAR_ARCHIVE);
	in_joyHorizViewSensitivity = Cvar_Get ("in_joyHorizViewSensitivity",	"20.0",	CVAR_ARCHIVE);
	in_joyVertViewSensitivity = Cvar_Get ("in_joyVertViewSensitivity",	"15.0",	CVAR_ARCHIVE);
	in_joyHorizViewDeadzone	= Cvar_Get ("in_joyHorizViewDeadzone",	"0.15",	CVAR_ARCHIVE);
	in_joyVertViewDeadzone	= Cvar_Get ("in_joyVertViewDeadzone",	"0.15",	CVAR_ARCHIVE);
	in_joyHorizMoveDeadzone	= Cvar_Get ("in_joyHorizMoveDeadzone",	"0.50",	CVAR_ARCHIVE);
	in_joyVertMoveDeadzone	= Cvar_Get ("in_joyVertMoveDeadzone",	"0.15",	CVAR_ARCHIVE);

	IN_Startup();
}


/*
===========
IN_Activate

Called when the main window gains or loses focus.
The window may have been destroyed and recreated
between a deactivate and an activate.
===========
*/
void IN_Activate (qboolean active) {
	in_appactive = active;
	IN_DeactivateMouse();
}


/*
==================
IN_Frame

Called every frame, even if not generating commands
==================
*/
void IN_Frame (void) {
	// post joystick events
	IN_JoyMove();

	if ( !s_wmv.mouseInitialized ) {
		if ( g_wv.hWnd && ( s_wmv.mouseStartupDelayed || ( in_mouse && in_mouse->integer != 0 ) ) ) {
			if ( s_wmv.mouseStartupDelayed ) {
				Com_Printf( "Proceeding with delayed mouse init\n" );
			} else if ( in_debugMouse && in_debugMouse->integer ) {
				Com_Printf( "Retrying mouse init now that a window is available\n" );
			}
			IN_StartupMouse();
		}

		if ( !s_wmv.mouseInitialized ) {
			IN_UpdateCursorCapture();
			IN_UpdateSystemCursor();
			if ( cls.keyCatchers & ( KEYCATCH_UI | KEYCATCH_CGAME | KEYCATCH_BROWSER ) ) {
				IN_WindowMouse();
			}
			return;
		}
	}

	if ( cls.keyCatchers & ~( KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS ) ) {
		IN_DeactivateMouse();
		IN_UpdateCursorCapture();
		IN_UpdateSystemCursor();
		IN_MouseMove();
		return;
	}

	if ( in_nograb && in_nograb->integer ) {
		IN_DeactivateMouse();
		IN_DeactivateCursorCapture();
		IN_UpdateSystemCursor();
		IN_MouseMove();
		return;
	}

	if ( !in_appactive ) {
		IN_DeactivateMouse();
		IN_DeactivateCursorCapture();
		IN_UpdateSystemCursor();
		IN_MouseMove();
		return;
	}

	IN_ActivateMouse();
	IN_UpdateSystemCursor();

	// post events to the system que
	IN_MouseMove();

}


/*
===================
IN_ClearStates
===================
*/
void IN_ClearStates (void) 
{
	s_wmv.oldButtonState = 0;
	IN_ClearRawInputSamples();
}


/*
=========================================================================

JOYSTICK

=========================================================================
*/

/* 
=============== 
IN_StartupJoystick 
=============== 
*/  
void IN_StartupJoystick (void) { 
	int			numdevs;
	MMRESULT	mmr;

	// assume no joystick
	joy.avail = qfalse; 
	joy.oldbuttonstate = 0;
	joy.oldpovstate = 0;
	joy.oldmoveaxisstate[AXIS_SIDE] = 0;
	joy.oldmoveaxisstate[AXIS_FORWARD] = 0;
	Cvar_Set( "ui_joyavail", "0" );

	if (! in_joystick->integer ) {
		Com_Printf ("Joystick is not active.\n");
		return;
	}

	// verify joystick driver is present
	if ((numdevs = joyGetNumDevs ()) == 0)
	{
		Com_Printf ("joystick not found -- driver not present\n");
		return;
	}

	// cycle through the joystick ids for the first valid one
	mmr = 0;
	for (joy.id=0 ; joy.id<numdevs ; joy.id++)
	{
		Com_Memset (&joy.ji, 0, sizeof(joy.ji));
		joy.ji.dwSize = sizeof(joy.ji);
		joy.ji.dwFlags = JOY_RETURNCENTERED;

		if ((mmr = joyGetPosEx (joy.id, &joy.ji)) == JOYERR_NOERROR)
			break;
	} 

	// abort startup if we didn't find a valid joystick
	if (mmr != JOYERR_NOERROR)
	{
		Com_Printf ("joystick not found -- no valid joysticks (%x)\n", mmr);
		return;
	}

	// get the capabilities of the selected joystick
	// abort startup if command fails
	Com_Memset (&joy.jc, 0, sizeof(joy.jc));
	if ((mmr = joyGetDevCaps (joy.id, &joy.jc, sizeof(joy.jc))) != JOYERR_NOERROR)
	{
		Com_Printf ("joystick not found -- invalid joystick capabilities (%x)\n", mmr); 
		return;
	}

	Com_Printf( "Joystick found.\n" );
	Com_Printf( "Pname: %s\n", joy.jc.szPname );
	Com_Printf( "OemVxD: %s\n", joy.jc.szOEMVxD );
	Com_Printf( "RegKey: %s\n", joy.jc.szRegKey );

	Com_Printf( "Numbuttons: %i / %i\n", joy.jc.wNumButtons, joy.jc.wMaxButtons );
	Com_Printf( "Axis: %i / %i\n", joy.jc.wNumAxes, joy.jc.wMaxAxes );
	Com_Printf( "Caps: 0x%x\n", joy.jc.wCaps );
	if ( joy.jc.wCaps & JOYCAPS_HASPOV ) {
		Com_Printf( "HASPOV\n" );
	} else {
		Com_Printf( "no POV\n" );
	}

	// mark the joystick as available
	joy.avail = qtrue; 
	Cvar_Set( "ui_joyavail", "1" );
}

/*
===========
JoyToF
===========
*/
float JoyToF( int value ) {
	float	fValue;

	// move centerpoint to zero
	value -= 32768;

	// convert range from -32768..32767 to -1..1 
	fValue = (float)value / 32768.0;

	if ( fValue < -1 ) {
		fValue = -1;
	}
	if ( fValue > 1 ) {
		fValue = 1;
	}
	return fValue;
}

int JoyToI( int value ) {
	// move centerpoint to zero
	value -= 32768;

	return value;
}

/*
================
IN_JoyRoundToInt
================
*/
static int IN_JoyRoundToInt( float value ) {
	if ( value < 0.0f ) {
		return (int)( value - 0.5f );
	}

	return (int)( value + 0.5f );
}

/*
===================
IN_QueueJoystickAxis
===================
*/
static void IN_QueueJoystickAxis( int axis, int value ) {
	value = (int)Com_Clamp( -127.0f, 127.0f, (float)value );

	if ( joy.oldmoveaxisstate[axis] == value ) {
		return;
	}

	Sys_QueEvent( g_wv.sysMsgTime, SE_JOYSTICK_AXIS, axis, value, 0, NULL );
	joy.oldmoveaxisstate[axis] = value;
}

/*
===============
IN_JoyMouseMove
===============
*/
static int IN_JoyMouseMove( float axisValue, float deadzone, float sensitivity, qboolean invert ) {
	float	accel;
	float	move;
	float	sign;

	axisValue = Com_Clamp( -1.0f, 1.0f, axisValue );
	if ( fabsf( axisValue ) <= deadzone ) {
		return 0;
	}

	move = (float)IN_JoyRoundToInt( axisValue * sensitivity );
	if ( move == 0.0f ) {
		return 0;
	}

	sign = 1.0f;
	if ( move < 0.0f ) {
		sign = -1.0f;
	}

	accel = cl_viewAccel ? cl_viewAccel->value : 1.0f;
	move = powf( fabsf( move ), accel ) * sign;

	if ( invert ) {
		move = -move;
	}

	return IN_JoyRoundToInt( move );
}

int	joyDirectionKeys[16] = {
	K_LEFTARROW, K_RIGHTARROW,
	K_UPARROW, K_DOWNARROW,
	K_JOY16, K_JOY17,
	K_JOY18, K_JOY19,
	K_JOY20, K_JOY21,
	K_JOY22, K_JOY23,

	K_JOY24, K_JOY25,
	K_JOY26, K_JOY27
};

/*
===========
IN_JoyMove
===========
*/
void IN_JoyMove( void ) {
	float	fAxisValue;
	int		i;
	DWORD	buttonstate, povstate;
	int		forward;
	int		side;
	int		x, y;

	// verify joystick is available and that the user wants to use it
	if ( !joy.avail ) {
		return; 
	}

	// collect the joystick data, if possible
	Com_Memset (&joy.ji, 0, sizeof(joy.ji));
	joy.ji.dwSize = sizeof(joy.ji);
	joy.ji.dwFlags = JOY_RETURNALL;

	if ( joyGetPosEx (joy.id, &joy.ji) != JOYERR_NOERROR ) {
		// read error occurred
		// turning off the joystick seems too harsh for 1 read error,\
		// but what should be done?
		// Com_Printf ("IN_ReadJoystick: no response\n");
		// joy.avail = false;
		return;
	}

	if ( in_debugJoystick->integer ) {
		Com_Printf( "%8x %5i %5.2f %5.2f %5.2f %5.2f %6i %6i\n", 
			joy.ji.dwButtons,
			joy.ji.dwPOV,
			JoyToF( joy.ji.dwXpos ), JoyToF( joy.ji.dwYpos ),
			JoyToF( joy.ji.dwZpos ), JoyToF( joy.ji.dwRpos ),
			JoyToI( joy.ji.dwUpos ), JoyToI( joy.ji.dwVpos ) );
	}

	// loop through the joystick buttons
	// key a joystick event or auxillary event for higher number buttons for each state change
	buttonstate = joy.ji.dwButtons;
	for ( i=0 ; i < joy.jc.wNumButtons ; i++ ) {
		if ( (buttonstate & (1<<i)) && !(joy.oldbuttonstate & (1<<i)) ) {
			Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, K_JOY1 + i, qtrue, 0, NULL );
		}
		if ( !(buttonstate & (1<<i)) && (joy.oldbuttonstate & (1<<i)) ) {
			Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, K_JOY1 + i, qfalse, 0, NULL );
		}
	}
	joy.oldbuttonstate = buttonstate;

	povstate = 0;

	side = 0;
	if ( joy.jc.wNumAxes > 0 ) {
		fAxisValue = JoyToF( joy.ji.dwXpos );
		if ( fabsf( fAxisValue ) > in_joyHorizMoveDeadzone->value ) {
			side = IN_JoyRoundToInt( fAxisValue * in_joyBallScale->value * 127.0f );
		}
	}
	IN_QueueJoystickAxis( AXIS_SIDE, side );

	forward = 0;
	if ( joy.jc.wNumAxes > 1 ) {
		fAxisValue = JoyToF( joy.ji.dwYpos );
		if ( fabsf( fAxisValue ) > in_joyVertMoveDeadzone->value ) {
			forward = IN_JoyRoundToInt( fAxisValue * in_joyBallScale->value * 127.0f );
		}
	}
	IN_QueueJoystickAxis( AXIS_FORWARD, forward );

	// convert the remaining primary joystick axes into direction button bits
	for (i = 2; i < joy.jc.wNumAxes && i < 4 ; i++) {
		// get the floating point zero-centered, potentially-inverted data for the current axis
		fAxisValue = JoyToF( (&joy.ji.dwXpos)[i] );

		if ( fAxisValue < -joy_threshold->value ) {
			povstate |= (1<<(i*2));
		} else if ( fAxisValue > joy_threshold->value ) {
			povstate |= (1<<(i*2+1));
		}
	}

	// convert POV information from a direction into 4 button bits
	if ( joy.jc.wCaps & JOYCAPS_HASPOV ) {
		if ( joy.ji.dwPOV != JOY_POVCENTERED ) {
			if (joy.ji.dwPOV == JOY_POVFORWARD)
				povstate |= 1<<12;
			if (joy.ji.dwPOV == JOY_POVBACKWARD)
				povstate |= 1<<13;
			if (joy.ji.dwPOV == JOY_POVRIGHT)
				povstate |= 1<<14;
			if (joy.ji.dwPOV == JOY_POVLEFT)
				povstate |= 1<<15;
		}
	}

	// determine which bits have changed and key an auxillary event for each change
	for (i=0 ; i < 16 ; i++) {
		if ( (povstate & (1<<i)) && !(joy.oldpovstate & (1<<i)) ) {
			Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, joyDirectionKeys[i], qtrue, 0, NULL );
		}

		if ( !(povstate & (1<<i)) && (joy.oldpovstate & (1<<i)) ) {
			Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, joyDirectionKeys[i], qfalse, 0, NULL );
		}
	}
	joy.oldpovstate = povstate;

	// retail Quake Live treats the R/U axes as analog look input.
	if ( joy.jc.wNumAxes >= 5 ) {
		x = IN_JoyMouseMove( JoyToF( joy.ji.dwRpos ), in_joyHorizViewDeadzone->value, in_joyHorizViewSensitivity->value, qfalse );
		y = IN_JoyMouseMove( JoyToF( joy.ji.dwUpos ), in_joyVertViewDeadzone->value, in_joyVertViewSensitivity->value, in_joystickInverted && in_joystickInverted->integer );
		if ( x || y ) {
			Sys_QueEvent( g_wv.sysMsgTime, SE_MOUSE, x, y, 0, NULL );
		}
	}
}

/*
=========================================================================

MIDI

=========================================================================
*/

static void MIDI_NoteOff( int note )
{
	int qkey;

	qkey = note - 60 + K_AUX1;

	if ( qkey > 255 || qkey < K_AUX1 )
		return;

	Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, qkey, qfalse, 0, NULL );
}

static void MIDI_NoteOn( int note, int velocity )
{
	int qkey;

	if ( velocity == 0 )
		MIDI_NoteOff( note );

	qkey = note - 60 + K_AUX1;

	if ( qkey > 255 || qkey < K_AUX1 )
		return;

	Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, qkey, qtrue, 0, NULL );
}

static void CALLBACK MidiInProc( HMIDIIN hMidiIn, UINT uMsg, DWORD dwInstance, 
								 DWORD dwParam1, DWORD dwParam2 )
{
	int message;

	switch ( uMsg )
	{
	case MIM_OPEN:
		break;
	case MIM_CLOSE:
		break;
	case MIM_DATA:
		message = dwParam1 & 0xff;

		// note on
		if ( ( message & 0xf0 ) == 0x90 )
		{
			if ( ( ( message & 0x0f ) + 1 ) == in_midichannel->integer )
				MIDI_NoteOn( ( dwParam1 & 0xff00 ) >> 8, ( dwParam1 & 0xff0000 ) >> 16 );
		}
		else if ( ( message & 0xf0 ) == 0x80 )
		{
			if ( ( ( message & 0x0f ) + 1 ) == in_midichannel->integer )
				MIDI_NoteOff( ( dwParam1 & 0xff00 ) >> 8 );
		}
		break;
	case MIM_LONGDATA:
		break;
	case MIM_ERROR:
		break;
	case MIM_LONGERROR:
		break;
	}

//	Sys_QueEvent( sys_msg_time, SE_KEY, wMsg, qtrue, 0, NULL );
}

static void MidiInfo_f( void )
{
	int i;

	const char *enableStrings[] = { "disabled", "enabled" };

	Com_Printf( "\nMIDI control:       %s\n", enableStrings[in_midi->integer != 0] );
	Com_Printf( "port:               %d\n", in_midiport->integer );
	Com_Printf( "channel:            %d\n", in_midichannel->integer );
	Com_Printf( "current device:     %d\n", in_mididevice->integer );
	Com_Printf( "number of devices:  %d\n", s_midiInfo.numDevices );
	for ( i = 0; i < s_midiInfo.numDevices; i++ )
	{
		if ( i == Cvar_VariableValue( "in_mididevice" ) )
			Com_Printf( "***" );
		else
			Com_Printf( "..." );
		Com_Printf(    "device %2d:       %s\n", i, s_midiInfo.caps[i].szPname );
		Com_Printf( "...manufacturer ID: 0x%hx\n", s_midiInfo.caps[i].wMid );
		Com_Printf( "...product ID:      0x%hx\n", s_midiInfo.caps[i].wPid );

		Com_Printf( "\n" );
	}
}

/*
================
ListInputDevices_f
================
*/
static void ListInputDevices_f( void )
{
	RAWINPUTDEVICELIST	*deviceList;
	RID_DEVICE_INFO		deviceInfo;
	UINT				deviceCount;
	UINT				infoSize;
	int					i;

	if ( !in_mouse || in_mouse->integer != 2 )
	{
		Com_Printf( "ListInputDevices is only supported for Raw Input (in_mouse 2).\n" );
		return;
	}

	deviceCount = 0;
	if ( GetRawInputDeviceList( NULL, &deviceCount, sizeof( RAWINPUTDEVICELIST ) ) == ( UINT )-1 )
	{
		Com_Printf( "Failed to acquire device list size.\n" );
		return;
	}

	if ( !deviceCount )
	{
		Com_Printf( "Raw Input Mouse Devices: \n" );
		return;
	}

	deviceList = ( RAWINPUTDEVICELIST * )malloc( deviceCount * sizeof( RAWINPUTDEVICELIST ) );
	if ( !deviceList )
	{
		Com_Printf( "Failed to allocate memory for the device list.\n" );
		return;
	}

	if ( GetRawInputDeviceList( deviceList, &deviceCount, sizeof( RAWINPUTDEVICELIST ) ) == ( UINT )-1 )
	{
		Com_Printf( "Failed to acquire device list.\n" );
		free( deviceList );
		return;
	}

	Com_Printf( "Raw Input Mouse Devices: \n" );

	for ( i = 0; i < ( int )deviceCount; i++ )
	{
		if ( deviceList[i].dwType != RIM_TYPEMOUSE )
		{
			continue;
		}

		Com_Memset( &deviceInfo, 0, sizeof( deviceInfo ) );
		deviceInfo.cbSize = sizeof( deviceInfo );
		infoSize = sizeof( deviceInfo );

		if ( GetRawInputDeviceInfoA( deviceList[i].hDevice, RIDI_DEVICEINFO, &deviceInfo, &infoSize ) == ( UINT )-1 )
		{
			continue;
		}

		Com_Printf( "  Mouse Id: %d, Button count: %d, Sample rate: %d\n",
			deviceInfo.mouse.dwId,
			deviceInfo.mouse.dwNumberOfButtons,
			deviceInfo.mouse.dwSampleRate );
	}

	free( deviceList );
}

static void IN_StartupMIDI( void )
{
	int i;

	if ( !Cvar_VariableValue( "in_midi" ) )
		return;

	//
	// enumerate MIDI IN devices
	//
	s_midiInfo.numDevices = midiInGetNumDevs();

	for ( i = 0; i < s_midiInfo.numDevices; i++ )
	{
		midiInGetDevCaps( i, &s_midiInfo.caps[i], sizeof( s_midiInfo.caps[i] ) );
	}

	//
	// open the MIDI IN port
	//
	if ( midiInOpen( &s_midiInfo.hMidiIn, 
		             in_mididevice->integer,
					 ( unsigned long ) MidiInProc,
					 ( unsigned long ) NULL,
					 CALLBACK_FUNCTION ) != MMSYSERR_NOERROR )
	{
		Com_Printf( "WARNING: could not open MIDI device %d: '%s'\n", in_mididevice->integer , s_midiInfo.caps[( int ) in_mididevice->value] );
		return;
	}

	midiInStart( s_midiInfo.hMidiIn );
}

static void IN_ShutdownMIDI( void )
{
	if ( s_midiInfo.hMidiIn )
	{
		midiInClose( s_midiInfo.hMidiIn );
	}
	Com_Memset( &s_midiInfo, 0, sizeof( s_midiInfo ) );
}

