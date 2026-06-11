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
// win_main.c

#include "../client/client.h"
#include "../qcommon/qcommon.h"
#include "win_local.h"
#include "win_clipboard_shared.h"
#include "resource.h"
#include <errno.h>
#include <float.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <direct.h>
#include <io.h>
#include <conio.h>
#include <dbghelp.h>
#include <signal.h>
#include <tlhelp32.h>
#include <commctrl.h>

#define	CD_BASEDIR	"quake3"
#define	CD_EXE		"quake3.exe"
#define	CD_BASEDIR_LINUX	"bin\\x86\\glibc-2.1"
#define	CD_EXE_LINUX "quake3"
#define MEM_THRESHOLD 96*1024*1024

static char		sys_cmdline[MAX_STRING_CHARS];
static char		sys_dumpPath[MAX_OSPATH];
static LONG		sys_crashHandled;
static LPTOP_LEVEL_EXCEPTION_FILTER	sys_previousExceptionFilter;
static HHOOK	sys_winkeyHook;
static HWND		sys_tooltipWindow;
static HMODULE	sys_commonControlsLibrary;
static cvar_t	*sys_winkeyDisable;

#define SYS_CRASH_DIALOG_TITLE	QL_PRODUCT_NAME " Debug Crash"

#ifndef DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
#define DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2	((HANDLE)-4)
#endif

typedef BOOL (WINAPI *SetProcessDpiAwarenessContextProc)( HANDLE value );
typedef BOOL (WINAPI *SetProcessDPIAwareProc)( void );
typedef BOOL (WINAPI *Sys_InitCommonControlsExProc)( const INITCOMMONCONTROLSEX *picce );

/*
==================
Sys_EnableDpiAwareness
==================
*/
static void Sys_EnableDpiAwareness( void )
{
	HMODULE		user32;
	qboolean	loadedUser32;
	SetProcessDpiAwarenessContextProc	setDpiAwarenessContext;
	SetProcessDPIAwareProc				setDPIAware;

	user32 = GetModuleHandleA( "user32.dll" );
	loadedUser32 = qfalse;
	if ( !user32 )
	{
		user32 = LoadLibraryA( "user32.dll" );
		loadedUser32 = (qboolean)( user32 != NULL );
	}
	if ( !user32 )
	{
		return;
	}

	setDpiAwarenessContext = (SetProcessDpiAwarenessContextProc)GetProcAddress( user32, "SetProcessDpiAwarenessContext" );
	if ( setDpiAwarenessContext && setDpiAwarenessContext( DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 ) )
	{
		if ( loadedUser32 )
		{
			FreeLibrary( user32 );
		}
		return;
	}

	setDPIAware = (SetProcessDPIAwareProc)GetProcAddress( user32, "SetProcessDPIAware" );
	if ( setDPIAware )
	{
		setDPIAware();
	}

	if ( loadedUser32 )
	{
		FreeLibrary( user32 );
	}
}

/*
==================
Sys_WinkeyHookProc

Optionally swallows the Windows keys while the client is running.
==================
*/
static LRESULT CALLBACK Sys_WinkeyHookProc( int nCode, WPARAM wParam, LPARAM lParam ) {
	const KBDLLHOOKSTRUCT	*key;

	if ( nCode < 0 ) {
		return CallNextHookEx( sys_winkeyHook, nCode, wParam, lParam );
	}

	if ( nCode == HC_ACTION
		&& sys_winkeyDisable
		&& sys_winkeyDisable->integer
		&& ( wParam == WM_SYSKEYDOWN || wParam == WM_KEYDOWN ) ) {
		key = (const KBDLLHOOKSTRUCT *)lParam;
		if ( key->vkCode == VK_LWIN || key->vkCode == VK_RWIN ) {
			return 1;
		}
	}

	return CallNextHookEx( sys_winkeyHook, nCode, wParam, lParam );
}

/*
==================
Sys_InitWinkeyHook
==================
*/
static void Sys_InitWinkeyHook( void ) {
	sys_winkeyHook = SetWindowsHookExA( WH_KEYBOARD_LL, Sys_WinkeyHookProc, g_wv.hInstance, 0 );
	sys_winkeyDisable = Cvar_Get( "winkey_disable", "0", CVAR_CLOUD );
}

/*
==================
Sys_ShutdownWinkeyHook
==================
*/
static void Sys_ShutdownWinkeyHook( void ) {
	if ( sys_winkeyHook ) {
		UnhookWindowsHookEx( sys_winkeyHook );
		sys_winkeyHook = NULL;
	}
}

/*
==================
Sys_InitCommonControls
==================
*/
static qboolean Sys_InitCommonControls( INITCOMMONCONTROLSEX *controls ) {
	HMODULE							library;
	qboolean						loadedCommonControls;
	Sys_InitCommonControlsExProc	initCommonControlsEx;

	library = GetModuleHandleA( "comctl32.dll" );
	loadedCommonControls = qfalse;
	if ( !library ) {
		library = LoadLibraryA( "comctl32.dll" );
		loadedCommonControls = (qboolean)( library != NULL );
	}
	if ( !library ) {
		return qfalse;
	}

	initCommonControlsEx = (Sys_InitCommonControlsExProc)GetProcAddress( library, "InitCommonControlsEx" );
	if ( !initCommonControlsEx ) {
		if ( loadedCommonControls ) {
			FreeLibrary( library );
		}
		return qfalse;
	}

	if ( !initCommonControlsEx( controls ) ) {
		if ( loadedCommonControls ) {
			FreeLibrary( library );
		}
		return qfalse;
	}

	if ( loadedCommonControls ) {
		sys_commonControlsLibrary = library;
	}

	return qtrue;
}

/*
==================
Sys_ShutdownTooltipShell
==================
*/
static void Sys_ShutdownTooltipShell( void ) {
	if ( sys_tooltipWindow ) {
		DestroyWindow( sys_tooltipWindow );
		sys_tooltipWindow = NULL;
	}

	if ( sys_commonControlsLibrary ) {
		FreeLibrary( sys_commonControlsLibrary );
		sys_commonControlsLibrary = NULL;
	}
}

/*
==================
Sys_InitTooltipShell
==================
*/
static void Sys_InitTooltipShell( void ) {
	INITCOMMONCONTROLSEX	controls;
	TOOLINFOA			tool;
	RECT				desktopRect;

	Sys_ShutdownTooltipShell();

	if ( !g_wv.hWnd ) {
		return;
	}

	memset( &controls, 0, sizeof( controls ) );
	controls.dwSize = sizeof( controls );
	controls.dwICC = ICC_BAR_CLASSES;

	if ( !Sys_InitCommonControls( &controls ) ) {
		return;
	}

	sys_tooltipWindow = CreateWindowExA( 0, TOOLTIPS_CLASSA, NULL,
			WS_POPUP | TTS_ALWAYSTIP | TTS_NOPREFIX,
			CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,
			g_wv.hWnd, NULL, g_wv.hInstance, NULL );
	if ( !sys_tooltipWindow ) {
		Sys_ShutdownTooltipShell();
		return;
	}

	SetWindowPos( sys_tooltipWindow, HWND_NOTOPMOST, 0, 0, 0, 0,
			SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE );

	memset( &tool, 0, sizeof( tool ) );
	tool.cbSize = sizeof( tool );
	tool.uFlags = TTF_SUBCLASS;
	tool.hwnd = g_wv.hWnd;
	tool.hinst = g_wv.hInstance;
	tool.lpszText = "";

	GetWindowRect( GetDesktopWindow(), &desktopRect );
	tool.rect = desktopRect;

	SendMessageA( sys_tooltipWindow, TTM_ADDTOOLA, 0, (LPARAM)&tool );
	SendMessageA( sys_tooltipWindow, TTM_ACTIVATE, 0, 0 );
}

// define this to use alternate spanking method
// I found out that the regular way doesn't work on my box for some reason
// see the associated spank.sh script
#define ALT_SPANK
#ifdef ALT_SPANK
#include <stdio.h>
#include <sys\stat.h>

int fh = 0;

void Spk_Open(char *name)
{
  fh = open( name, O_TRUNC | O_CREAT | O_WRONLY, S_IREAD | S_IWRITE );
};

void Spk_Close()
{
  if (!fh)
    return;

  close( fh );
  fh = 0;
}

void Spk_Printf (const char *text, ...)
{
  va_list argptr;
  char buf[32768];

  if (!fh)
    return;

  va_start (argptr,text);
  vsprintf (buf, text, argptr);
  write(fh, buf, strlen(buf));
  _commit(fh);
  va_end (argptr);

};
#endif

/*
==================
Sys_LowPhysicalMemory()
==================
*/

qboolean Sys_LowPhysicalMemory() {
	MEMORYSTATUS stat;
  GlobalMemoryStatus (&stat);
	return (stat.dwTotalPhys <= MEM_THRESHOLD) ? qtrue : qfalse;
}

/*
==================
Sys_BeginProfiling
==================
*/
void Sys_BeginProfiling( void ) {
	// this is just used on the mac build
}

/*
=============
Sys_Error

Show the early console as an error dialog
=============
*/
void QDECL Sys_Error( const char *error, ... ) {
	va_list		argptr;
	char		text[4096];
    MSG        msg;

	va_start (argptr, error);
	vsprintf (text, error, argptr);
	va_end (argptr);

	Conbuf_AppendText( text );
	Conbuf_AppendText( "\n" );

	Sys_SetErrorText( text );
	Sys_ShowConsole( 1, qtrue );

	timeEndPeriod( 1 );

	IN_Shutdown();
	Sys_ShutdownWinkeyHook();
	Sys_ShutdownTooltipShell();

	// wait for the user to quit
	while ( 1 ) {
		if (!GetMessage (&msg, NULL, 0, 0))
			Com_Quit_f ();
		TranslateMessage (&msg);
      	DispatchMessage (&msg);
	}

	Sys_DestroyConsole();

	exit (1);
}

/*
==============
Sys_Quit
==============
*/
void Sys_Quit( void ) {
	timeEndPeriod( 1 );
	IN_Shutdown();
	Sys_ShutdownWinkeyHook();
	Sys_ShutdownTooltipShell();
	Sys_DestroyConsole();

	exit (0);
}

/*
==============
Sys_Print
==============
*/
void Sys_Print( const char *msg ) {
	Conbuf_AppendText( msg );
}


/*
==============
Sys_Mkdir
==============
*/
void Sys_Mkdir( const char *path ) {
	_mkdir (path);
}

/*
==============
Sys_Cwd
==============
*/
char *Sys_Cwd( void ) {
	static char cwd[MAX_OSPATH];

	_getcwd( cwd, sizeof( cwd ) - 1 );
	cwd[MAX_OSPATH-1] = 0;

	return cwd;
}

/*
==============
Sys_DefaultCDPath
==============
*/
char *Sys_DefaultCDPath( void ) {
	return "";
}

/*
==============
Sys_DefaultBasePath
==============
*/
char *Sys_DefaultBasePath( void ) {
	return Sys_Cwd();
}

/*
==============
Sys_PathHasReleaseMarker

Checks whether a release-marker file exists in a root path.
==============
*/
static qboolean Sys_PathHasReleaseMarker( const char *directory, const char *markerName ) {
	char		path[MAX_OSPATH];
	struct _stat	fileInfo;

	if ( !directory || !directory[0] || !markerName || !markerName[0] ) {
		return qfalse;
	}

	Com_sprintf( path, sizeof( path ), "%s\\%s", directory, markerName );
	return _stat( path, &fileInfo ) == 0 ? qtrue : qfalse;
}

/*
==============
Sys_MonkeyShouldBeSpanked
==============
*/
int Sys_MonkeyShouldBeSpanked( void ) {
	if ( Sys_PathHasReleaseMarker( Sys_Cwd(), "q3monkeyid" ) ) {
		return qtrue;
	}

	if ( Sys_PathHasReleaseMarker( Sys_DefaultInstallPath(), "q3monkeyid" ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
==============================================================

DIRECTORY SCANNING

==============================================================
*/

#define	MAX_FOUND_FILES	0x1000

void Sys_ListFilteredFiles( const char *basedir, char *subdirs, char *filter, char **list, int *numfiles ) {
	char		search[MAX_OSPATH], newsubdirs[MAX_OSPATH];
	char		filename[MAX_OSPATH];
	int			findhandle;
	struct _finddata_t findinfo;

	if ( *numfiles >= MAX_FOUND_FILES - 1 ) {
		return;
	}

	if (strlen(subdirs)) {
		Com_sprintf( search, sizeof(search), "%s\\%s\\*", basedir, subdirs );
	}
	else {
		Com_sprintf( search, sizeof(search), "%s\\*", basedir );
	}

	findhandle = _findfirst (search, &findinfo);
	if (findhandle == -1) {
		return;
	}

	do {
		if (findinfo.attrib & _A_SUBDIR) {
			if (Q_stricmp(findinfo.name, ".") && Q_stricmp(findinfo.name, "..")) {
				if (strlen(subdirs)) {
					Com_sprintf( newsubdirs, sizeof(newsubdirs), "%s\\%s", subdirs, findinfo.name);
				}
				else {
					Com_sprintf( newsubdirs, sizeof(newsubdirs), "%s", findinfo.name);
				}
				Sys_ListFilteredFiles( basedir, newsubdirs, filter, list, numfiles );
			}
		}
		if ( *numfiles >= MAX_FOUND_FILES - 1 ) {
			break;
		}
		Com_sprintf( filename, sizeof(filename), "%s\\%s", subdirs, findinfo.name );
		if (!Com_FilterPath( filter, filename, qfalse ))
			continue;
		list[ *numfiles ] = CopyString( filename );
		(*numfiles)++;
	} while ( _findnext (findhandle, &findinfo) != -1 );

	_findclose (findhandle);
}

static qboolean strgtr(const char *s0, const char *s1) {
	int l0, l1, i;

	l0 = strlen(s0);
	l1 = strlen(s1);

	if (l1<l0) {
		l0 = l1;
	}

	for(i=0;i<l0;i++) {
		if (s1[i] > s0[i]) {
			return qtrue;
		}
		if (s1[i] < s0[i]) {
			return qfalse;
		}
	}
	return qfalse;
}

char **Sys_ListFiles( const char *directory, const char *extension, char *filter, int *numfiles, qboolean wantsubs ) {
	char		search[MAX_OSPATH];
	int			nfiles;
	char		**listCopy;
	char		*list[MAX_FOUND_FILES];
	struct _finddata_t findinfo;
	int			findhandle;
	int			flag;
	int			i;

	if (filter) {

		nfiles = 0;
		Sys_ListFilteredFiles( directory, "", filter, list, &nfiles );

		list[ nfiles ] = 0;
		*numfiles = nfiles;

		if (!nfiles)
			return NULL;

		listCopy = Z_Malloc( ( nfiles + 1 ) * sizeof( *listCopy ) );
		for ( i = 0 ; i < nfiles ; i++ ) {
			listCopy[i] = list[i];
		}
		listCopy[i] = NULL;

		return listCopy;
	}

	if ( !extension) {
		extension = "";
	}

	// passing a slash as extension will find directories
	if ( extension[0] == '/' && extension[1] == 0 ) {
		extension = "";
		flag = 0;
	} else {
		flag = _A_SUBDIR;
	}

	Com_sprintf( search, sizeof(search), "%s\\*%s", directory, extension );

	// search
	nfiles = 0;

	findhandle = _findfirst (search, &findinfo);
	if (findhandle == -1) {
		*numfiles = 0;
		return NULL;
	}

	do {
		if ( (!wantsubs && flag ^ ( findinfo.attrib & _A_SUBDIR )) || (wantsubs && findinfo.attrib & _A_SUBDIR) ) {
			if ( nfiles == MAX_FOUND_FILES - 1 ) {
				break;
			}
			list[ nfiles ] = CopyString( findinfo.name );
			nfiles++;
		}
	} while ( _findnext (findhandle, &findinfo) != -1 );

	list[ nfiles ] = 0;

	_findclose (findhandle);

	// return a copy of the list
	*numfiles = nfiles;

	if ( !nfiles ) {
		return NULL;
	}

	listCopy = Z_Malloc( ( nfiles + 1 ) * sizeof( *listCopy ) );
	for ( i = 0 ; i < nfiles ; i++ ) {
		listCopy[i] = list[i];
	}
	listCopy[i] = NULL;

	do {
		flag = 0;
		for(i=1; i<nfiles; i++) {
			if (strgtr(listCopy[i-1], listCopy[i])) {
				char *temp = listCopy[i];
				listCopy[i] = listCopy[i-1];
				listCopy[i-1] = temp;
				flag = 1;
			}
		}
	} while(flag);

	return listCopy;
}

void	Sys_FreeFileList( char **list ) {
	int		i;

	if ( !list ) {
		return;
	}

	for ( i = 0 ; list[i] ; i++ ) {
		Z_Free( list[i] );
	}

	Z_Free( list );
}

//========================================================


/*
================
Sys_ScanForCD

Search all the drives to see if there is a valid CD to grab
the cddir from
================
*/
qboolean Sys_ScanForCD( void ) {
	static char	cddir[MAX_OSPATH];
	char		drive[4];
	FILE		*f;
	char		test[MAX_OSPATH];
#if 0
	// don't override a cdpath on the command line
	if ( strstr( sys_cmdline, "cdpath" ) ) {
		return;
	}
#endif

	drive[0] = 'c';
	drive[1] = ':';
	drive[2] = '\\';
	drive[3] = 0;

	// scan the drives
	for ( drive[0] = 'c' ; drive[0] <= 'z' ; drive[0]++ ) {
		if ( GetDriveType (drive) != DRIVE_CDROM ) {
			continue;
		}

		sprintf (cddir, "%s%s", drive, CD_BASEDIR);
		sprintf (test, "%s\\%s", cddir, CD_EXE);
		f = fopen( test, "r" );
		if ( f ) {
			fclose (f);
			return qtrue;
    } else {
      sprintf(cddir, "%s%s", drive, CD_BASEDIR_LINUX);
      sprintf(test, "%s\\%s", cddir, CD_EXE_LINUX);
  		f = fopen( test, "r" );
	  	if ( f ) {
		  	fclose (f);
			  return qtrue;
      }
    }
	}

	return qfalse;
}

/*
================
Sys_CheckCD

Return true if the proper CD is in the drive
================
*/
qboolean	Sys_CheckCD( void ) {
  // FIXME: mission pack
  return qtrue;
	//return Sys_ScanForCD();
}

/*
==================
Sys_CloneClipboardText
==================
*/
static char *Sys_CloneClipboardText( const char *cliptext ) {
	size_t dataBytes;
	char *data;

	if ( !cliptext ) {
		return NULL;
	}

	dataBytes = strlen( cliptext ) + 1;
	data = Z_Malloc( dataBytes );
	memcpy( data, cliptext, dataBytes );
	QLR_Win32ClipboardTrimText( data );

	return data;
}

/*
==================
Sys_CloneClipboardUnicodeText
==================
*/
static char *Sys_CloneClipboardUnicodeText( const WCHAR *cliptext ) {
	int utf8Bytes;
	char *data;

	utf8Bytes = QLR_Win32ClipboardWideToUtf8ByteCount( cliptext );
	if ( utf8Bytes <= 0 ) {
		return NULL;
	}

	data = Z_Malloc( utf8Bytes );
	if ( !QLR_Win32ClipboardWideToUtf8( cliptext, data, utf8Bytes ) ) {
		Z_Free( data );
		return NULL;
	}

	QLR_Win32ClipboardTrimText( data );
	return data;
}

/*
==================
Sys_SetClipboardData
==================
*/
void Sys_SetClipboardData( const char *text ) {
	HGLOBAL clipboardData;
	char *clipboardText;
	size_t textBytes;

	if ( !text ) {
		return;
	}

	if ( OpenClipboard( NULL ) == 0 ) {
		return;
	}

	EmptyClipboard();

	textBytes = strlen( text ) + 1;
	clipboardData = GlobalAlloc( GMEM_MOVEABLE, textBytes );
	if ( clipboardData != 0 ) {
		clipboardText = (char *)GlobalLock( clipboardData );
		if ( clipboardText != 0 ) {
			memcpy( clipboardText, text, textBytes );
			GlobalUnlock( clipboardData );
			SetClipboardData( CF_TEXT, clipboardData );
		} else {
			GlobalFree( clipboardData );
		}
	}

	CloseClipboard();
}

/*
==================
Sys_GetClipboardData
==================
*/
char *Sys_GetClipboardData( void ) {
	char *data = NULL;
	HANDLE hClipboardData;

	if ( OpenClipboard( NULL ) == 0 ) {
		return NULL;
	}

	if ( ( hClipboardData = GetClipboardData( CF_UNICODETEXT ) ) != 0 ) {
		const WCHAR *cliptext;

		if ( ( cliptext = (const WCHAR *)GlobalLock( hClipboardData ) ) != 0 ) {
			data = Sys_CloneClipboardUnicodeText( cliptext );
			GlobalUnlock( hClipboardData );
		}
	}

	if ( !data && ( hClipboardData = GetClipboardData( CF_TEXT ) ) != 0 ) {
		const char *cliptext;

		if ( ( cliptext = (const char *)GlobalLock( hClipboardData ) ) != 0 ) {
			data = Sys_CloneClipboardText( cliptext );
			GlobalUnlock( hClipboardData );
		}
	}

	CloseClipboard();
	return data;
}


/*
========================================================================

LOAD/UNLOAD DLL

========================================================================
*/

/*
=================
Sys_UnloadDll

=================
*/
void Sys_UnloadDll( void *dllHandle ) {
	if ( !dllHandle ) {
		return;
	}
	if ( !FreeLibrary( dllHandle ) ) {
		Com_Error (ERR_FATAL, "Sys_UnloadDll FreeLibrary failed");
	}
}

typedef int (QDECL *sysVmMain_t)( int, ... );
typedef void (QDECL *sysDllEntryVoid_t)( int (QDECL *syscallptr)(int, ...) );
typedef sysVmMain_t (QDECL *sysDllEntryRet_t)( int (QDECL *syscallptr)(int, ...) );
typedef void (QDECL *sysDllEntryQL_t)( void **exports, void *imports, int *apiVersion );

extern char		*FS_BuildOSPath( const char *base, const char *game, const char *qpath );

/*
=================
Sys_CreatePathForFile
=================
*/
static qboolean Sys_CreatePathForFile( char *osPath ) {
	char	*ofs;
	char	separator;

	if ( !osPath || !osPath[0] ) {
		return qfalse;
	}

	if ( strstr( osPath, ".." ) || strstr( osPath, "::" ) ) {
		Com_Printf( "WARNING: refusing to create relative path \"%s\"\n", osPath );
		return qfalse;
	}

	for ( ofs = osPath + 1 ; *ofs ; ofs++ ) {
		if ( *ofs == '/' || *ofs == '\\' ) {
			if ( ofs > osPath && ofs[-1] == ':' ) {
				continue;
			}

			separator = *ofs;
			*ofs = 0;
			Sys_Mkdir( osPath );
			*ofs = separator;
		}
	}

	return qtrue;
}

/*
=================
Sys_WriteFileToPath
=================
*/
static qboolean Sys_WriteFileToPath( const char *path, const void *buffer, int size ) {
	FILE	*file;
	char	createPath[MAX_OSPATH];
	size_t	written;

	if ( !path || !path[0] || !buffer || size <= 0 ) {
		return qfalse;
	}

	Q_strncpyz( createPath, path, sizeof( createPath ) );
	if ( !Sys_CreatePathForFile( createPath ) ) {
		return qfalse;
	}

	file = fopen( path, "wb" );
	if ( !file ) {
		Com_Printf( "Sys_LoadDll: failed to open native cache '%s'\n", path );
		return qfalse;
	}

	written = fwrite( buffer, 1, size, file );
	if ( written != (size_t)size ) {
		fclose( file );
		Com_Printf( "Sys_LoadDll: short write to native cache '%s'\n", path );
		return qfalse;
	}

	if ( fclose( file ) == EOF ) {
		Com_Printf( "Sys_LoadDll: failed to close native cache '%s'\n", path );
		return qfalse;
	}

	return qtrue;
}

/*
=================
Sys_FileIsReadable
=================
*/
static qboolean Sys_FileIsReadable( const char *path ) {
	FILE	*file;

	if ( !path || !path[0] ) {
		return qfalse;
	}

	file = fopen( path, "rb" );
	if ( !file ) {
		return qfalse;
	}

	fclose( file );
	return qtrue;
}

/*
=================
Sys_GetNativeDllCachePath
=================
*/
static qboolean Sys_GetNativeDllCachePath( const char *filename, const char *preferredRoot, const char *gamedir, char *outPath, int outPathSize ) {
	const char	*localAppData;
	char		tempPath[MAX_OSPATH];
	DWORD		tempPathLength;

	if ( !filename || !filename[0] || !outPath || outPathSize <= 0 ) {
		return qfalse;
	}

	if ( preferredRoot && preferredRoot[0] ) {
		Q_strncpyz( outPath, FS_BuildOSPath( preferredRoot, ( gamedir && gamedir[0] ) ? gamedir : BASEGAME, filename ), outPathSize );
		return qtrue;
	}

	localAppData = getenv( "LOCALAPPDATA" );
	if ( localAppData && localAppData[0] ) {
		Com_sprintf( outPath, outPathSize, "%s\\QuakeLive-SRP\\%s\\%s", localAppData, BASEGAME, filename );
		return qtrue;
	}

	tempPathLength = GetTempPathA( sizeof( tempPath ), tempPath );
	if ( tempPathLength == 0 || tempPathLength >= sizeof( tempPath ) ) {
		return qfalse;
	}

	while ( tempPathLength > 0 && ( tempPath[tempPathLength - 1] == '\\' || tempPath[tempPathLength - 1] == '/' ) ) {
		tempPath[--tempPathLength] = '\0';
	}
	if ( !tempPath[0] ) {
		return qfalse;
	}

	Com_sprintf( outPath, outPathSize, "%s\\QuakeLive-SRP\\%s\\%s", tempPath, BASEGAME, filename );
	return qtrue;
}

/*
=================
Sys_ShouldExtractNativeDllFromBinPak
=================
*/
static qboolean Sys_ShouldExtractNativeDllFromBinPak( const char *name, const char *filename, const char *gamedir ) {
	if ( gamedir && gamedir[0] && Q_stricmp( gamedir, BASEGAME ) ) {
		return qfalse;
	}

	if ( !Q_stricmp( name, "ui" ) && !Q_stricmp( filename, "uix86.dll" ) ) {
		return qtrue;
	}
	if ( !Q_stricmp( name, "cgame" ) && !Q_stricmp( filename, "cgamex86.dll" ) ) {
		return qtrue;
	}
	if ( !Q_stricmp( name, "qagame" ) && !Q_stricmp( filename, "qagamex86.dll" ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=================
Sys_MaterializeNativeDllFromBinPak
=================
*/
static qboolean Sys_MaterializeNativeDllFromBinPak( const char *name, const char *filename, char **roots, int rootCount,
	const char *gamedir, char *outPath, int outPathSize ) {
	char	pakPath[MAX_OSPATH];
	char	cachePath[MAX_OSPATH];
	void	*buffer;
	pack_t	*pack;
	int		i;
	int		length;

	if ( !Sys_ShouldExtractNativeDllFromBinPak( name, filename, gamedir ) ) {
		return qfalse;
	}
	if ( !Sys_GetNativeDllCachePath( filename, rootCount > 0 ? roots[0] : NULL, gamedir, cachePath, sizeof( cachePath ) ) ) {
		return qfalse;
	}

	for ( i = 0; i < rootCount; i++ ) {
		if ( !roots[i] || !roots[i][0] ) {
			continue;
		}

		Q_strncpyz( pakPath, FS_BuildOSPath( roots[i], BASEGAME, "bin.pk3" ), sizeof( pakPath ) );
		pack = FS_LoadPackExplicit( pakPath );
		if ( !pack ) {
			continue;
		}

		buffer = NULL;
		length = FS_ReadFileFromPak( pack, filename, &buffer );
		FS_FreePak( pack );
		if ( length <= 0 || !buffer ) {
			if ( buffer ) {
				Z_Free( buffer );
			}
			continue;
		}

		if ( Sys_WriteFileToPath( cachePath, buffer, length ) && Sys_FileIsReadable( cachePath ) ) {
			Z_Free( buffer );
			Q_strncpyz( outPath, cachePath, outPathSize );
			Com_Printf( "Sys_LoadDll: extracted %s from %s\n", filename, pakPath );
			return qtrue;
		}

		Z_Free( buffer );
	}

	return qfalse;
}

/*
=================
Sys_TryLoadDllFromPath
=================
*/
static void *Sys_TryLoadDllFromPath( const char *fn, char *fqpath, int (QDECL **entryPoint)(int, ...),
				  void **dllExports, void *imports, int *apiVersion,
				  int (QDECL *systemcalls)(int, ...) ) {
	HINSTANCE	libHandle;
	sysDllEntryVoid_t dllEntry;
	sysDllEntryQL_t dllEntryQL;
	sysVmMain_t vmMain;
	sysDllEntryRet_t dllEntryRet;

	libHandle = LoadLibrary( fn );
	if ( !libHandle ) {
		if ( Cvar_VariableIntegerValue( "developer" ) ) {
			Com_Printf( "Sys_LoadDll: LoadLibrary '%s' failed (err %lu)\n", fn, GetLastError() );
		}
		return NULL;
	}

	dllEntry = ( sysDllEntryVoid_t )GetProcAddress( libHandle, "dllEntry" );
	vmMain = ( sysVmMain_t )GetProcAddress( libHandle, "vmMain" );
	if ( !dllEntry ) {
		Com_Printf( "Sys_LoadDll: rejected '%s': missing dllEntry export\n", fn );
		FreeLibrary( libHandle );
		return NULL;
	}
	if ( dllExports && imports && apiVersion ) {
		dllEntryQL = ( sysDllEntryQL_t )dllEntry;
		dllEntryQL( dllExports, imports, apiVersion );
		if ( dllExports && *dllExports ) {
			Q_strncpyz( fqpath, fn, MAX_QPATH );
			Com_Printf( "Sys_LoadDll: loaded '%s'\n", fn );
			return libHandle;
		}
	}
	if ( vmMain ) {
		dllEntry( systemcalls );
		*entryPoint = vmMain;
		Q_strncpyz( fqpath, fn, MAX_QPATH );
		Com_Printf( "Sys_LoadDll: loaded '%s'\n", fn );
		return libHandle;
	}
	if ( systemcalls ) {
		dllEntryRet = ( sysDllEntryRet_t )dllEntry;
		*entryPoint = dllEntryRet( systemcalls );
		if ( *entryPoint ) {
			Q_strncpyz( fqpath, fn, MAX_QPATH );
			Com_Printf( "Sys_LoadDll: loaded '%s'\n", fn );
			return libHandle;
		}
	}

	Com_Printf( "Sys_LoadDll: rejected '%s': missing compatible VM exports\n", fn );
	if ( dllExports ) {
		*dllExports = NULL;
	}
	*entryPoint = NULL;
	FreeLibrary( libHandle );

	return NULL;
}

/*
=================
Sys_LoadDll

Used to load a development dll instead of a virtual machine

TTimo: added some verbosity in debug
=================
*/
// fqpath param added 7/20/02 by T.Ray - Sys_LoadDll is only called in vm.c at this time
// fqpath will be empty if dll not loaded, otherwise will hold fully qualified path of dll module loaded
// fqpath buffersize must be at least MAX_QPATH+1 bytes long
void * QDECL Sys_LoadDll( const char *name, char *fqpath, int (QDECL **entryPoint)(int, ...),
				  void **dllExports, void *imports, int *apiVersion,
				  int (QDECL *systemcalls)(int, ...) ) {
	HINSTANCE	libHandle;
	char	*basepath;
	char	*cdpath;
	char	*cwdpath;
	char	*homepath;
	char	*gamedir;
	const char *dllGamedir;
	char	*searchRoots[4];
	char	*binPakRoots[3];
	char	*fn;
	int		searchCount;
	int		binPakRootCount;
	int		i;
	char	filename[MAX_QPATH];
	char	extractedPath[MAX_OSPATH];

	*fqpath = 0 ;		// added 7/20/02 by T.Ray
	*entryPoint = NULL;
	if ( dllExports ) {
		*dllExports = NULL;
	}

	Com_sprintf( filename, sizeof( filename ), "%sx86.dll", name );

	basepath = Cvar_VariableString( "fs_basepath" );
	cdpath = Cvar_VariableString( "fs_cdpath" );
	homepath = Cvar_VariableString( "fs_homepath" );
	gamedir = Cvar_VariableString( "fs_game" );
	dllGamedir = ( gamedir && gamedir[0] ) ? gamedir : BASEGAME;
	cwdpath = Sys_Cwd();

	searchCount = 0;
	binPakRootCount = 0;
	/*
	 * Retail probes fs_basepath before fs_homepath. Keep the SteamID-scoped
	 * homepath first so replacement launches prefer fs_basepath/<steamid>
	 * native DLLs and extracted bin.pk3 modules over the immutable retail root.
	 */
	if ( homepath && homepath[0] ) {
		searchRoots[searchCount++] = homepath;
		binPakRoots[binPakRootCount++] = homepath;
	}
	if ( basepath && basepath[0] ) {
		searchRoots[searchCount++] = basepath;
		binPakRoots[binPakRootCount++] = basepath;
	}
	if ( cdpath && cdpath[0] ) {
		searchRoots[searchCount++] = cdpath;
		binPakRoots[binPakRootCount++] = cdpath;
	}
	if ( cwdpath && cwdpath[0] ) {
		searchRoots[searchCount++] = cwdpath;
	}

	Com_Printf( "Sys_LoadDll: %s search roots home='%s' base='%s' cd='%s' cwd='%s' game='%s'\n",
		filename,
		homepath ? homepath : "",
		basepath ? basepath : "",
		cdpath ? cdpath : "",
		cwdpath ? cwdpath : "",
		dllGamedir );

	for ( i = 0; i < searchCount; i++ ) {
		fn = FS_BuildOSPath( searchRoots[i], dllGamedir, filename );
		libHandle = Sys_TryLoadDllFromPath( fn, fqpath, entryPoint, dllExports, imports, apiVersion, systemcalls );
		if ( libHandle ) {
			return libHandle;
		}
	}

	if ( Sys_MaterializeNativeDllFromBinPak( name, filename, binPakRoots, binPakRootCount, dllGamedir,
		extractedPath, sizeof( extractedPath ) ) ) {
		libHandle = Sys_TryLoadDllFromPath( extractedPath, fqpath, entryPoint, dllExports, imports, apiVersion, systemcalls );
		if ( libHandle ) {
			return libHandle;
		}
	}

	return NULL;
}


/*
========================================================================

BACKGROUND FILE STREAMING

========================================================================
*/

#if 1

void Sys_InitStreamThread( void ) {
}

void Sys_ShutdownStreamThread( void ) {
}

void Sys_BeginStreamedFile( fileHandle_t f, int readAhead ) {
}

void Sys_EndStreamedFile( fileHandle_t f ) {
}

int Sys_StreamedRead( void *buffer, int size, int count, fileHandle_t f ) {
   return FS_Read( buffer, size * count, f );
}

void Sys_StreamSeek( fileHandle_t f, int offset, int origin ) {
   FS_Seek( f, offset, origin );
}


#else

typedef struct {
	fileHandle_t	file;
	byte	*buffer;
	qboolean	eof;
	qboolean	active;
	int		bufferSize;
	int		streamPosition;	// next byte to be returned by Sys_StreamRead
	int		threadPosition;	// next byte to be read from file
} streamsIO_t;

typedef struct {
	HANDLE				threadHandle;
	int					threadId;
	CRITICAL_SECTION	crit;
	streamsIO_t			sIO[MAX_FILE_HANDLES];
} streamState_t;

streamState_t	stream;

/*
===============
Sys_StreamThread

A thread will be sitting in this loop forever
================
*/
void Sys_StreamThread( void ) {
	int		buffer;
	int		count;
	int		readCount;
	int		bufferPoint;
	int		r, i;

	while (1) {
		Sleep( 10 );
//		EnterCriticalSection (&stream.crit);

		for (i=1;i<MAX_FILE_HANDLES;i++) {
			// if there is any space left in the buffer, fill it up
			if ( stream.sIO[i].active  && !stream.sIO[i].eof ) {
				count = stream.sIO[i].bufferSize - (stream.sIO[i].threadPosition - stream.sIO[i].streamPosition);
				if ( !count ) {
					continue;
				}

				bufferPoint = stream.sIO[i].threadPosition % stream.sIO[i].bufferSize;
				buffer = stream.sIO[i].bufferSize - bufferPoint;
				readCount = buffer < count ? buffer : count;

				r = FS_Read( stream.sIO[i].buffer + bufferPoint, readCount, stream.sIO[i].file );
				stream.sIO[i].threadPosition += r;

				if ( r != readCount ) {
					stream.sIO[i].eof = qtrue;
				}
			}
		}
//		LeaveCriticalSection (&stream.crit);
	}
}

/*
===============
Sys_InitStreamThread

================
*/
void Sys_InitStreamThread( void ) {
	int i;

	InitializeCriticalSection ( &stream.crit );

	// don't leave the critical section until there is a
	// valid file to stream, which will cause the StreamThread
	// to sleep without any overhead
//	EnterCriticalSection( &stream.crit );

	stream.threadHandle = CreateThread(
	   NULL,	// LPSECURITY_ATTRIBUTES lpsa,
	   0,		// DWORD cbStack,
	   (LPTHREAD_START_ROUTINE)Sys_StreamThread,	// LPTHREAD_START_ROUTINE lpStartAddr,
	   0,			// LPVOID lpvThreadParm,
	   0,			//   DWORD fdwCreate,
	   &stream.threadId);
	for(i=0;i<MAX_FILE_HANDLES;i++) {
		stream.sIO[i].active = qfalse;
	}
}

/*
===============
Sys_ShutdownStreamThread

================
*/
void Sys_ShutdownStreamThread( void ) {
}


/*
===============
Sys_BeginStreamedFile

================
*/
void Sys_BeginStreamedFile( fileHandle_t f, int readAhead ) {
	if ( stream.sIO[f].file ) {
		Sys_EndStreamedFile( stream.sIO[f].file );
	}

	stream.sIO[f].file = f;
	stream.sIO[f].buffer = Z_Malloc( readAhead );
	stream.sIO[f].bufferSize = readAhead;
	stream.sIO[f].streamPosition = 0;
	stream.sIO[f].threadPosition = 0;
	stream.sIO[f].eof = qfalse;
	stream.sIO[f].active = qtrue;

	// let the thread start running
//	LeaveCriticalSection( &stream.crit );
}

/*
===============
Sys_EndStreamedFile

================
*/
void Sys_EndStreamedFile( fileHandle_t f ) {
	if ( f != stream.sIO[f].file ) {
		Com_Error( ERR_FATAL, "Sys_EndStreamedFile: wrong file");
	}
	// don't leave critical section until another stream is started
	EnterCriticalSection( &stream.crit );

	stream.sIO[f].file = 0;
	stream.sIO[f].active = qfalse;

	Z_Free( stream.sIO[f].buffer );

	LeaveCriticalSection( &stream.crit );
}


/*
===============
Sys_StreamedRead

================
*/
int Sys_StreamedRead( void *buffer, int size, int count, fileHandle_t f ) {
	int		available;
	int		remaining;
	int		sleepCount;
	int		copy;
	int		bufferCount;
	int		bufferPoint;
	byte	*dest;

	if (stream.sIO[f].active == qfalse) {
		Com_Error( ERR_FATAL, "Streamed read with non-streaming file" );
	}

	dest = (byte *)buffer;
	remaining = size * count;

	if ( remaining <= 0 ) {
		Com_Error( ERR_FATAL, "Streamed read with non-positive size" );
	}

	sleepCount = 0;
	while ( remaining > 0 ) {
		available = stream.sIO[f].threadPosition - stream.sIO[f].streamPosition;
		if ( !available ) {
			if ( stream.sIO[f].eof ) {
				break;
			}
			if ( sleepCount == 1 ) {
				Com_DPrintf( "Sys_StreamedRead: waiting\n" );
			}
			if ( ++sleepCount > 100 ) {
				Com_Error( ERR_FATAL, "Sys_StreamedRead: thread has died");
			}
			Sleep( 10 );
			continue;
		}

		EnterCriticalSection( &stream.crit );

		bufferPoint = stream.sIO[f].streamPosition % stream.sIO[f].bufferSize;
		bufferCount = stream.sIO[f].bufferSize - bufferPoint;

		copy = available < bufferCount ? available : bufferCount;
		if ( copy > remaining ) {
			copy = remaining;
		}
		memcpy( dest, stream.sIO[f].buffer + bufferPoint, copy );
		stream.sIO[f].streamPosition += copy;
		dest += copy;
		remaining -= copy;

		LeaveCriticalSection( &stream.crit );
	}

	return (count * size - remaining) / size;
}

/*
===============
Sys_StreamSeek

================
*/
void Sys_StreamSeek( fileHandle_t f, int offset, int origin ) {

	// halt the thread
	EnterCriticalSection( &stream.crit );

	// clear to that point
	FS_Seek( f, offset, origin );
	stream.sIO[f].streamPosition = 0;
	stream.sIO[f].threadPosition = 0;
	stream.sIO[f].eof = qfalse;

	// let the thread start running at the new position
	LeaveCriticalSection( &stream.crit );
}

#endif

/*
========================================================================

EVENT LOOP

========================================================================
*/

#define	MAX_QUED_EVENTS		256
#define	MASK_QUED_EVENTS	( MAX_QUED_EVENTS - 1 )

sysEvent_t	eventQue[MAX_QUED_EVENTS];
int			eventHead, eventTail;
byte		sys_packetReceived[MAX_MSGLEN];

/*
================
Sys_QueEvent

A time of 0 will get the current time
Ptr should either be null, or point to a block of data that can
be freed by the game later.
================
*/
void Sys_QueEvent( int time, sysEventType_t type, int value, int value2, int ptrLength, void *ptr ) {
	sysEvent_t	*ev;

	ev = &eventQue[ eventHead & MASK_QUED_EVENTS ];
	if ( eventHead - eventTail >= MAX_QUED_EVENTS ) {
		Com_Printf("Sys_QueEvent: overflow\n");
		// we are discarding an event, but don't leak memory
		if ( ev->evPtr ) {
			Z_Free( ev->evPtr );
		}
		eventTail++;
	}

	eventHead++;

	if ( time == 0 ) {
		time = Sys_Milliseconds();
	}

	ev->evTime = time;
	ev->evType = type;
	ev->evValue = value;
	ev->evValue2 = value2;
	ev->evPtrLength = ptrLength;
	ev->evPtr = ptr;
}

/*
================
Sys_GetEvent

================
*/
sysEvent_t Sys_GetEvent( void ) {
    MSG			msg;
	sysEvent_t	ev;
	char		*s;
	msg_t		netmsg;
	netadr_t	adr;

	// return if we have data
	if ( eventHead > eventTail ) {
		eventTail++;
		return eventQue[ ( eventTail - 1 ) & MASK_QUED_EVENTS ];
	}

	// pump the message loop
	while (PeekMessage (&msg, NULL, 0, 0, PM_NOREMOVE)) {
		if ( !GetMessage (&msg, NULL, 0, 0) ) {
			Com_Quit_f();
		}

		// save the msg time, because wndprocs don't have access to the timestamp
		g_wv.sysMsgTime = msg.time;

		TranslateMessage (&msg);
      	DispatchMessage (&msg);
	}

	// check for console commands
	s = Sys_ConsoleInput();
	if ( s ) {
		char	*b;
		int		len;

		len = strlen( s ) + 1;
		b = Z_Malloc( len );
		Q_strncpyz( b, s, len-1 );
		Sys_QueEvent( 0, SE_CONSOLE, 0, 0, len, b );
	}

	// check for network packets
	MSG_Init( &netmsg, sys_packetReceived, sizeof( sys_packetReceived ) );
	if ( Sys_GetPacket ( &adr, &netmsg ) ) {
		netadr_t		*buf;
		int				len;

		// copy out to a seperate buffer for qeueing
		// the readcount stepahead is for SOCKS support
		len = sizeof( netadr_t ) + netmsg.cursize - netmsg.readcount;
		buf = Z_Malloc( len );
		*buf = adr;
		memcpy( buf+1, &netmsg.data[netmsg.readcount], netmsg.cursize - netmsg.readcount );
		Sys_QueEvent( 0, SE_PACKET, 0, 0, len, buf );
	}

	// return if we have data
	if ( eventHead > eventTail ) {
		eventTail++;
		return eventQue[ ( eventTail - 1 ) & MASK_QUED_EVENTS ];
	}

	// create an empty event to return

	memset( &ev, 0, sizeof( ev ) );
	ev.evTime = timeGetTime();

	return ev;
}

//================================================================

/*
=================
Sys_In_Restart_f

Restart the input subsystem
=================
*/
void Sys_In_Restart_f( void ) {
	IN_Shutdown();
	IN_Init();
}


/*
=================
Sys_Net_Restart_f

Restart the network subsystem
=================
*/
void Sys_Net_Restart_f( void ) {
	NET_Restart();
}

/*
==================
Sys_WriteCrashLogText
==================
*/
static void Sys_WriteCrashLogText( HANDLE logFile, const char *text ) {
	DWORD written;

	if ( logFile == INVALID_HANDLE_VALUE || !text || !text[0] ) {
		return;
	}

	WriteFile( logFile, text, (DWORD)strlen( text ), &written, NULL );
}

/*
==================
Sys_WriteCrashLogf
==================
*/
static void QDECL Sys_WriteCrashLogf( HANDLE logFile, const char *fmt, ... ) {
	va_list argptr;
	char message[2048];

	if ( logFile == INVALID_HANDLE_VALUE || !fmt ) {
		return;
	}

	va_start( argptr, fmt );
	Q_vsnprintf( message, sizeof( message ), fmt, argptr );
	va_end( argptr );
	message[sizeof( message ) - 1] = '\0';

	Sys_WriteCrashLogText( logFile, message );
}

/*
==================
Sys_ExceptionName
==================
*/
static const char *Sys_ExceptionName( DWORD exceptionCode ) {
	switch ( exceptionCode ) {
	case EXCEPTION_ACCESS_VIOLATION:
		return "EXCEPTION_ACCESS_VIOLATION";
	case EXCEPTION_ARRAY_BOUNDS_EXCEEDED:
		return "EXCEPTION_ARRAY_BOUNDS_EXCEEDED";
	case EXCEPTION_BREAKPOINT:
		return "EXCEPTION_BREAKPOINT";
	case EXCEPTION_DATATYPE_MISALIGNMENT:
		return "EXCEPTION_DATATYPE_MISALIGNMENT";
	case EXCEPTION_FLT_DENORMAL_OPERAND:
		return "EXCEPTION_FLT_DENORMAL_OPERAND";
	case EXCEPTION_FLT_DIVIDE_BY_ZERO:
		return "EXCEPTION_FLT_DIVIDE_BY_ZERO";
	case EXCEPTION_FLT_INEXACT_RESULT:
		return "EXCEPTION_FLT_INEXACT_RESULT";
	case EXCEPTION_FLT_INVALID_OPERATION:
		return "EXCEPTION_FLT_INVALID_OPERATION";
	case EXCEPTION_FLT_OVERFLOW:
		return "EXCEPTION_FLT_OVERFLOW";
	case EXCEPTION_FLT_STACK_CHECK:
		return "EXCEPTION_FLT_STACK_CHECK";
	case EXCEPTION_FLT_UNDERFLOW:
		return "EXCEPTION_FLT_UNDERFLOW";
	case EXCEPTION_ILLEGAL_INSTRUCTION:
		return "EXCEPTION_ILLEGAL_INSTRUCTION";
	case EXCEPTION_IN_PAGE_ERROR:
		return "EXCEPTION_IN_PAGE_ERROR";
	case EXCEPTION_INT_DIVIDE_BY_ZERO:
		return "EXCEPTION_INT_DIVIDE_BY_ZERO";
	case EXCEPTION_INT_OVERFLOW:
		return "EXCEPTION_INT_OVERFLOW";
	case EXCEPTION_INVALID_DISPOSITION:
		return "EXCEPTION_INVALID_DISPOSITION";
	case EXCEPTION_NONCONTINUABLE_EXCEPTION:
		return "EXCEPTION_NONCONTINUABLE_EXCEPTION";
	case EXCEPTION_PRIV_INSTRUCTION:
		return "EXCEPTION_PRIV_INSTRUCTION";
	case EXCEPTION_SINGLE_STEP:
		return "EXCEPTION_SINGLE_STEP";
	case EXCEPTION_STACK_OVERFLOW:
		return "EXCEPTION_STACK_OVERFLOW";
	case 0xE0000001:
		return "QL_INVALID_PARAMETER";
	case 0xE0000002:
		return "QL_PURECALL";
	case 0xE0000101:
		return "QL_SIGABRT";
	case 0xE0000105:
		return "QL_SIGTERM";
	case 0xE00001FF:
		return "QL_SIGNAL";
	default:
		return "UNKNOWN_EXCEPTION";
	}
}

/*
==================
Sys_GetCrashDumpType
==================
*/
static MINIDUMP_TYPE Sys_GetCrashDumpType( void ) {
	const char *fullDump;
	DWORD dumpType;

	dumpType = MiniDumpWithDataSegs
		| MiniDumpWithHandleData
		| MiniDumpWithIndirectlyReferencedMemory
		| MiniDumpScanMemory
		| MiniDumpWithProcessThreadData
		| MiniDumpWithThreadInfo
		| MiniDumpWithUnloadedModules;

	fullDump = getenv( "QLR_FULL_DUMP" );
	if ( fullDump && fullDump[0] && fullDump[0] != '0' ) {
		dumpType |= MiniDumpWithFullMemory;
	}

	return (MINIDUMP_TYPE)dumpType;
}

/*
==================
Sys_WriteCrashModuleList
==================
*/
static void Sys_WriteCrashModuleList( HANDLE logFile ) {
	HANDLE snapshot;
	MODULEENTRY32 moduleEntry;

	snapshot = CreateToolhelp32Snapshot( TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, GetCurrentProcessId() );
	if ( snapshot == INVALID_HANDLE_VALUE ) {
		Sys_WriteCrashLogf( logFile, "Loaded modules: unavailable (GetLastError=%lu)\r\n", GetLastError() );
		return;
	}

	memset( &moduleEntry, 0, sizeof( moduleEntry ) );
	moduleEntry.dwSize = sizeof( moduleEntry );

	Sys_WriteCrashLogText( logFile, "\r\nLoaded modules:\r\n" );
	if ( Module32First( snapshot, &moduleEntry ) ) {
		do {
			Sys_WriteCrashLogf( logFile, "  %p-%p %s (%s)\r\n",
				moduleEntry.modBaseAddr,
				moduleEntry.modBaseAddr + moduleEntry.modBaseSize,
				moduleEntry.szModule,
				moduleEntry.szExePath );
			moduleEntry.dwSize = sizeof( moduleEntry );
		} while ( Module32Next( snapshot, &moduleEntry ) );
	}

	CloseHandle( snapshot );
}

/*
==================
Sys_WriteCrashLog
==================
*/
static void Sys_WriteCrashLog( HANDLE logFile, const char *dumpName, MINIDUMP_TYPE dumpType,
	const EXCEPTION_POINTERS *exceptionInfo ) {
	SYSTEMTIME localTime;
	EXCEPTION_RECORD *exceptionRecord;
	CONTEXT *contextRecord;
	char exeName[MAX_OSPATH];
	DWORD exeNameLength;
	DWORD exceptionCode;
	int i;

	if ( logFile == INVALID_HANDLE_VALUE ) {
		return;
	}

	GetLocalTime( &localTime );
	exeName[0] = '\0';
	exeNameLength = GetModuleFileNameA( NULL, exeName, sizeof( exeName ) );
	if ( exeNameLength >= sizeof( exeName ) ) {
		exeName[sizeof( exeName ) - 1] = '\0';
	}

	exceptionRecord = exceptionInfo ? exceptionInfo->ExceptionRecord : NULL;
	contextRecord = exceptionInfo ? exceptionInfo->ContextRecord : NULL;
	exceptionCode = exceptionRecord ? exceptionRecord->ExceptionCode : 0;

	Sys_WriteCrashLogText( logFile, "QuakeLive-reverse crash report\r\n" );
	Sys_WriteCrashLogf( logFile, "Timestamp: %04d-%02d-%02d %02d:%02d:%02d.%03d\r\n",
		localTime.wYear, localTime.wMonth, localTime.wDay,
		localTime.wHour, localTime.wMinute, localTime.wSecond, localTime.wMilliseconds );
	Sys_WriteCrashLogf( logFile, "Executable: %s\r\n", exeName );
	Sys_WriteCrashLogf( logFile, "Process ID: %lu\r\n", GetCurrentProcessId() );
	Sys_WriteCrashLogf( logFile, "Thread ID: %lu\r\n", GetCurrentThreadId() );
	Sys_WriteCrashLogf( logFile, "Debugger attached: %s\r\n", IsDebuggerPresent() ? "yes" : "no" );
	Sys_WriteCrashLogf( logFile, "Dump path: %s\r\n", dumpName ? dumpName : "(none)" );
	Sys_WriteCrashLogf( logFile, "Dump type: 0x%08lx\r\n", (unsigned long)dumpType );
	Sys_WriteCrashLogf( logFile, "Exception: %s (0x%08lx)\r\n", Sys_ExceptionName( exceptionCode ), exceptionCode );

	if ( exceptionRecord ) {
		Sys_WriteCrashLogf( logFile, "Exception address: %p\r\n", exceptionRecord->ExceptionAddress );
		Sys_WriteCrashLogf( logFile, "Exception flags: 0x%08lx\r\n", exceptionRecord->ExceptionFlags );
		Sys_WriteCrashLogf( logFile, "Exception parameters: %lu\r\n", exceptionRecord->NumberParameters );
		for ( i = 0; i < (int)exceptionRecord->NumberParameters && i < EXCEPTION_MAXIMUM_PARAMETERS; i++ ) {
			Sys_WriteCrashLogf( logFile, "  Parameter[%d]: 0x%p\r\n", i, (void *)exceptionRecord->ExceptionInformation[i] );
		}
		if ( exceptionCode == EXCEPTION_ACCESS_VIOLATION && exceptionRecord->NumberParameters >= 2 ) {
			const char *operation;

			operation = "read";
			if ( exceptionRecord->ExceptionInformation[0] == 1 ) {
				operation = "write";
			} else if ( exceptionRecord->ExceptionInformation[0] == 8 ) {
				operation = "execute";
			}
			Sys_WriteCrashLogf( logFile, "Access violation: %s at 0x%p\r\n",
				operation, (void *)exceptionRecord->ExceptionInformation[1] );
		}
	}

	if ( contextRecord ) {
#if defined(_M_IX86)
		Sys_WriteCrashLogText( logFile, "\r\nRegisters:\r\n" );
		Sys_WriteCrashLogf( logFile, "  EAX=%08lx EBX=%08lx ECX=%08lx EDX=%08lx\r\n",
			contextRecord->Eax, contextRecord->Ebx, contextRecord->Ecx, contextRecord->Edx );
		Sys_WriteCrashLogf( logFile, "  ESI=%08lx EDI=%08lx EBP=%08lx ESP=%08lx\r\n",
			contextRecord->Esi, contextRecord->Edi, contextRecord->Ebp, contextRecord->Esp );
		Sys_WriteCrashLogf( logFile, "  EIP=%08lx EFlags=%08lx\r\n",
			contextRecord->Eip, contextRecord->EFlags );
#elif defined(_M_X64)
		Sys_WriteCrashLogText( logFile, "\r\nRegisters:\r\n" );
		Sys_WriteCrashLogf( logFile, "  RAX=%016llx RBX=%016llx RCX=%016llx RDX=%016llx\r\n",
			contextRecord->Rax, contextRecord->Rbx, contextRecord->Rcx, contextRecord->Rdx );
		Sys_WriteCrashLogf( logFile, "  RSI=%016llx RDI=%016llx RBP=%016llx RSP=%016llx\r\n",
			contextRecord->Rsi, contextRecord->Rdi, contextRecord->Rbp, contextRecord->Rsp );
		Sys_WriteCrashLogf( logFile, "  RIP=%016llx EFlags=%08lx\r\n",
			contextRecord->Rip, contextRecord->EFlags );
#endif
	}

	Sys_WriteCrashModuleList( logFile );
}

#ifdef _DEBUG
/*
==================
Sys_DebugCrashReportConfirmed
==================
*/
static qboolean Sys_DebugCrashReportConfirmed( const char *dumpName, const char *logName ) {
	char message[4096];
	int result;

	Com_sprintf( message, sizeof( message ),
		QL_PRODUCT_NAME " debug build detected an unhandled exception.\n\n"
		"Create a memory dump and crash log?\n\n"
		"Dump: %s\n"
		"Log: %s",
		dumpName, logName );

	result = MessageBoxA( NULL, message, SYS_CRASH_DIALOG_TITLE,
		MB_ICONERROR | MB_YESNO | MB_DEFBUTTON1 | MB_TASKMODAL | MB_SETFOREGROUND );

	return (qboolean)( result == IDYES );
}

/*
==================
Sys_ShowDebugCrashReportResult
==================
*/
static void Sys_ShowDebugCrashReportResult( qboolean dumpWritten, qboolean logWritten,
	const char *dumpName, const char *logName, DWORD dumpError ) {
	char message[4096];

	if ( dumpWritten && logWritten ) {
		Com_sprintf( message, sizeof( message ),
			"Crash dump and crash log written.\n\n"
			"Dump: %s\n"
			"Log: %s",
			dumpName, logName );
		MessageBoxA( NULL, message, SYS_CRASH_DIALOG_TITLE,
			MB_ICONERROR | MB_OK | MB_TASKMODAL | MB_SETFOREGROUND );
		return;
	}

	if ( dumpWritten ) {
		Com_sprintf( message, sizeof( message ),
			"Crash dump written, but crash log creation failed.\n\n"
			"Dump: %s\n"
			"Log: %s",
			dumpName, logName );
		MessageBoxA( NULL, message, SYS_CRASH_DIALOG_TITLE,
			MB_ICONERROR | MB_OK | MB_TASKMODAL | MB_SETFOREGROUND );
		return;
	}

	if ( logWritten ) {
		Com_sprintf( message, sizeof( message ),
			"Crash log written, but memory dump creation failed.\n\n"
			"Dump: %s\n"
			"Log: %s\n"
			"GetLastError: %lu",
			dumpName, logName, dumpError );
		MessageBoxA( NULL, message, SYS_CRASH_DIALOG_TITLE,
			MB_ICONERROR | MB_OK | MB_TASKMODAL | MB_SETFOREGROUND );
		return;
	}

	Com_sprintf( message, sizeof( message ),
		"Crash report creation failed.\n\n"
		"Dump: %s\n"
		"Log: %s\n"
		"GetLastError: %lu",
		dumpName, logName, dumpError );
	MessageBoxA( NULL, message, SYS_CRASH_DIALOG_TITLE,
		MB_ICONERROR | MB_OK | MB_TASKMODAL | MB_SETFOREGROUND );
}
#endif

/*
==================
Sys_UnhandledExceptionFilter
==================
*/
static LONG WINAPI Sys_UnhandledExceptionFilter( EXCEPTION_POINTERS *exceptionInfo ) {
	HANDLE dumpFile;
	HANDLE logFile;
	SYSTEMTIME localTime;
	MINIDUMP_EXCEPTION_INFORMATION dumpInfo;
	MINIDUMP_TYPE dumpType;
	char crashBaseName[MAX_OSPATH];
	char dumpName[MAX_OSPATH];
	char logName[MAX_OSPATH];
#ifdef _DEBUG
	qboolean logWritten;
#endif
	BOOL dumpWritten;
	DWORD dumpError;
#ifndef _DEBUG
	LONG previousAction;
#endif

	if ( !sys_dumpPath[0] ) {
		return EXCEPTION_CONTINUE_SEARCH;
	}

	if ( InterlockedCompareExchange( &sys_crashHandled, 1, 0 ) != 0 ) {
		return EXCEPTION_CONTINUE_SEARCH;
	}

	GetLocalTime( &localTime );
	Com_sprintf( crashBaseName, sizeof( crashBaseName ),
		"%s\\quakelive_steam_%04d%02d%02d_%02d%02d%02d_%03d",
		sys_dumpPath,
		localTime.wYear, localTime.wMonth, localTime.wDay,
		localTime.wHour, localTime.wMinute, localTime.wSecond, localTime.wMilliseconds );
	Com_sprintf( dumpName, sizeof( dumpName ), "%s.dmp", crashBaseName );
	Com_sprintf( logName, sizeof( logName ), "%s.log", crashBaseName );

	dumpType = Sys_GetCrashDumpType();

#ifdef _DEBUG
	if ( IsDebuggerPresent() ) {
		return EXCEPTION_CONTINUE_SEARCH;
	}

	if ( !Sys_DebugCrashReportConfirmed( dumpName, logName ) ) {
		return EXCEPTION_EXECUTE_HANDLER;
	}
#endif

	logFile = CreateFileA( logName, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL );
#ifdef _DEBUG
	logWritten = (qboolean)( logFile != INVALID_HANDLE_VALUE );
#endif
	Sys_WriteCrashLog( logFile, dumpName, dumpType, exceptionInfo );

	dumpFile = CreateFileA( dumpName, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL );
	if ( dumpFile == INVALID_HANDLE_VALUE ) {
		dumpError = GetLastError();
		Sys_WriteCrashLogf( logFile, "\r\nMiniDumpWriteDump: failed to create dump file (GetLastError=%lu)\r\n",
			dumpError );
		if ( logFile != INVALID_HANDLE_VALUE ) {
			CloseHandle( logFile );
		}
#ifdef _DEBUG
		Sys_ShowDebugCrashReportResult( qfalse, logWritten, dumpName, logName, dumpError );
		return EXCEPTION_EXECUTE_HANDLER;
#else
		if ( sys_previousExceptionFilter ) {
			previousAction = sys_previousExceptionFilter( exceptionInfo );
			if ( previousAction != EXCEPTION_CONTINUE_SEARCH ) {
				return previousAction;
			}
		}
		return EXCEPTION_CONTINUE_SEARCH;
#endif
	}

	dumpInfo.ThreadId = GetCurrentThreadId();
	dumpInfo.ExceptionPointers = exceptionInfo;
	dumpInfo.ClientPointers = FALSE;

	dumpWritten = MiniDumpWriteDump( GetCurrentProcess(), GetCurrentProcessId(), dumpFile, dumpType, &dumpInfo, NULL, NULL );
	dumpError = dumpWritten ? 0 : GetLastError();
	CloseHandle( dumpFile );

	Sys_WriteCrashLogf( logFile, "\r\nMiniDumpWriteDump: %s", dumpWritten ? "succeeded" : "failed" );
	if ( !dumpWritten ) {
		Sys_WriteCrashLogf( logFile, " (GetLastError=%lu)", dumpError );
	}
	Sys_WriteCrashLogText( logFile, "\r\n" );
	if ( logFile != INVALID_HANDLE_VALUE ) {
		CloseHandle( logFile );
	}

#ifdef _DEBUG
	Sys_ShowDebugCrashReportResult( (qboolean)dumpWritten, logWritten, dumpName, logName, dumpError );
	return EXCEPTION_EXECUTE_HANDLER;
#else
	if ( sys_previousExceptionFilter ) {
		previousAction = sys_previousExceptionFilter( exceptionInfo );
		if ( previousAction != EXCEPTION_CONTINUE_SEARCH ) {
			return previousAction;
		}
	}

	return EXCEPTION_CONTINUE_SEARCH;
#endif
}

/*
==================
Sys_RaiseCrashException
==================
*/
static void Sys_RaiseCrashException( DWORD code ) {
	if ( InterlockedCompareExchange( &sys_crashHandled, 1, 1 ) != 0 ) {
		TerminateProcess( GetCurrentProcess(), (UINT)code );
	}

	RaiseException( code, EXCEPTION_NONCONTINUABLE, 0, NULL );
	TerminateProcess( GetCurrentProcess(), (UINT)code );
}

/*
==================
Sys_InvalidParameterHandler
==================
*/
static void __cdecl Sys_InvalidParameterHandler( const wchar_t *expression, const wchar_t *function,
	const wchar_t *file, unsigned int line, uintptr_t reserved ) {
	Sys_RaiseCrashException( 0xE0000001 );
}

/*
==================
Sys_PureCallHandler
==================
*/
static void __cdecl Sys_PureCallHandler( void ) {
	Sys_RaiseCrashException( 0xE0000002 );
}

/*
==================
Sys_SignalHandler
==================
*/
static void __cdecl Sys_SignalHandler( int signalCode ) {
	DWORD exceptionCode;

	switch ( signalCode ) {
	case SIGABRT:
		exceptionCode = 0xE0000101;
		break;
	case SIGSEGV:
		exceptionCode = EXCEPTION_ACCESS_VIOLATION;
		break;
	case SIGILL:
		exceptionCode = EXCEPTION_ILLEGAL_INSTRUCTION;
		break;
	case SIGFPE:
		exceptionCode = EXCEPTION_FLT_INVALID_OPERATION;
		break;
	case SIGTERM:
		exceptionCode = 0xE0000105;
		break;
	default:
		exceptionCode = 0xE00001FF;
		break;
	}

	signal( signalCode, SIG_DFL );
	Sys_RaiseCrashException( exceptionCode );
}

/*
==================
Sys_InitCrashDumps
==================
*/
static void Sys_InitCrashDumps( void ) {
	const char *envPath;
	const char *homePath;
	const char *basePath;

	sys_dumpPath[0] = '\0';

	homePath = NULL;
	basePath = NULL;
	envPath = getenv( "QLR_DUMP_PATH" );
	if ( envPath && envPath[0] ) {
		Q_strncpyz( sys_dumpPath, envPath, sizeof( sys_dumpPath ) );
	} else {
		homePath = Cvar_VariableString( "fs_homepath" );
		if ( homePath && homePath[0] ) {
			Q_strncpyz( sys_dumpPath, FS_BuildOSPath( homePath, BASEGAME, "dumps" ), sizeof( sys_dumpPath ) );
		} else {
			basePath = Cvar_VariableString( "fs_basepath" );
			if ( basePath && basePath[0] ) {
				Q_strncpyz( sys_dumpPath, FS_BuildOSPath( basePath, BASEGAME, "dumps" ), sizeof( sys_dumpPath ) );
			}
		}
	}

	if ( sys_dumpPath[0] ) {
		if ( homePath && homePath[0] ) {
			Sys_Mkdir( FS_BuildOSPath( homePath, BASEGAME, "" ) );
		}
		Sys_Mkdir( sys_dumpPath );
		sys_crashHandled = 0;
		sys_previousExceptionFilter = SetUnhandledExceptionFilter( Sys_UnhandledExceptionFilter );
		_set_abort_behavior( 0, _CALL_REPORTFAULT | _WRITE_ABORT_MSG );
		_set_invalid_parameter_handler( Sys_InvalidParameterHandler );
		_set_purecall_handler( Sys_PureCallHandler );
		signal( SIGABRT, Sys_SignalHandler );
		signal( SIGSEGV, Sys_SignalHandler );
		signal( SIGILL, Sys_SignalHandler );
		signal( SIGFPE, Sys_SignalHandler );
		signal( SIGTERM, Sys_SignalHandler );
	}
}


/*
================
Sys_Init

Called after the common systems (cvars, files, etc)
are initialized
================
*/
#define OSR2_BUILD_NUMBER 1111
#define WIN98_BUILD_NUMBER 1998

void Sys_Init( void ) {
	int cpuid;

	// make sure the timer is high precision, otherwise
	// NT gets 18ms resolution
	timeBeginPeriod( 1 );

	Cmd_AddCommand ("in_restart", Sys_In_Restart_f);
	Cmd_AddCommand ("net_restart", Sys_Net_Restart_f);

	g_wv.osversion.dwOSVersionInfoSize = sizeof( g_wv.osversion );

	if (!GetVersionEx (&g_wv.osversion))
		Sys_Error ("Couldn't get OS info");

	if (g_wv.osversion.dwMajorVersion < 4)
		Sys_Error ("Quake3 requires Windows version 4 or greater");
	if (g_wv.osversion.dwPlatformId == VER_PLATFORM_WIN32s)
		Sys_Error ("Quake3 doesn't run on Win32s");

	if ( g_wv.osversion.dwPlatformId == VER_PLATFORM_WIN32_NT )
	{
		Cvar_Set( "arch", "winnt" );
	}
	else if ( g_wv.osversion.dwPlatformId == VER_PLATFORM_WIN32_WINDOWS )
	{
		if ( LOWORD( g_wv.osversion.dwBuildNumber ) >= WIN98_BUILD_NUMBER )
		{
			Cvar_Set( "arch", "win98" );
		}
		else if ( LOWORD( g_wv.osversion.dwBuildNumber ) >= OSR2_BUILD_NUMBER )
		{
			Cvar_Set( "arch", "win95 osr2.x" );
		}
		else
		{
			Cvar_Set( "arch", "win95" );
		}
	}
	else
	{
		Cvar_Set( "arch", "unknown Windows variant" );
	}

	// save out a couple things in rom cvars for the renderer to access
	Cvar_Get( "win_hinstance", va("%i", (int)g_wv.hInstance), CVAR_ROM );
	Cvar_Get( "win_wndproc", va("%i", (int)MainWndProc), CVAR_ROM );

	Sys_InitCrashDumps();

	//
	// figure out our CPU
	//
	Cvar_Get( "sys_cpustring", "detect", 0 );
	if ( !Q_stricmp( Cvar_VariableString( "sys_cpustring"), "detect" ) )
	{
		Com_Printf( "...detecting CPU, found " );

		cpuid = Sys_GetProcessorId();

		switch ( cpuid )
		{
		case CPUID_GENERIC:
			Cvar_Set( "sys_cpustring", "generic" );
			break;
		case CPUID_INTEL_UNSUPPORTED:
			Cvar_Set( "sys_cpustring", "x86 (pre-Pentium)" );
			break;
		case CPUID_INTEL_PENTIUM:
			Cvar_Set( "sys_cpustring", "x86 (P5/PPro, non-MMX)" );
			break;
		case CPUID_INTEL_MMX:
			Cvar_Set( "sys_cpustring", "x86 (P5/Pentium2, MMX)" );
			break;
		case CPUID_INTEL_KATMAI:
			Cvar_Set( "sys_cpustring", "Intel Pentium III" );
			break;
		case CPUID_AMD_3DNOW:
			Cvar_Set( "sys_cpustring", "AMD w/ 3DNow!" );
			break;
		case CPUID_AXP:
			Cvar_Set( "sys_cpustring", "Alpha AXP" );
			break;
		default:
			Com_Error( ERR_FATAL, "Unknown cpu type %d\n", cpuid );
			break;
		}
	}
	else
	{
		Com_Printf( "...forcing CPU type to " );
		if ( !Q_stricmp( Cvar_VariableString( "sys_cpustring" ), "generic" ) )
		{
			cpuid = CPUID_GENERIC;
		}
		else if ( !Q_stricmp( Cvar_VariableString( "sys_cpustring" ), "x87" ) )
		{
			cpuid = CPUID_INTEL_PENTIUM;
		}
		else if ( !Q_stricmp( Cvar_VariableString( "sys_cpustring" ), "mmx" ) )
		{
			cpuid = CPUID_INTEL_MMX;
		}
		else if ( !Q_stricmp( Cvar_VariableString( "sys_cpustring" ), "3dnow" ) )
		{
			cpuid = CPUID_AMD_3DNOW;
		}
		else if ( !Q_stricmp( Cvar_VariableString( "sys_cpustring" ), "PentiumIII" ) )
		{
			cpuid = CPUID_INTEL_KATMAI;
		}
		else if ( !Q_stricmp( Cvar_VariableString( "sys_cpustring" ), "axp" ) )
		{
			cpuid = CPUID_AXP;
		}
		else
		{
			Com_Printf( "WARNING: unknown sys_cpustring '%s'\n", Cvar_VariableString( "sys_cpustring" ) );
			cpuid = CPUID_GENERIC;
		}
	}
	Cvar_SetValue( "sys_cpuid", cpuid );
	Com_Printf( "%s\n", Cvar_VariableString( "sys_cpustring" ) );

	Cvar_Set( "username", Sys_GetCurrentUser() );

	IN_Init();		// FIXME: not in dedicated?
}


//=======================================================================

int	totalMsec, countMsec;

/*
==================
WinMain

==================
*/
int WINAPI WinMain (HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
	char		cwd[MAX_OSPATH];
	int			startTime, endTime;

	// should never get a previous instance in Win32
	if ( hPrevInstance ) {
		return 0;
	}

	Sys_EnableDpiAwareness();

	g_wv.hInstance = hInstance;
	Q_strncpyz( sys_cmdline, lpCmdLine, sizeof( sys_cmdline ) );

	Sys_CreateLoadingWindow();

	// done before Com/Sys_Init since we need this for error output
	Sys_CreateConsole();

	// no abort/retry/fail errors
	SetErrorMode( SEM_FAILCRITICALERRORS );

	Sys_DestroyLoadingWindow();

	// get the initial time base
	Sys_Milliseconds();
#if 0
	// if we find the CD, add a +set cddir xxx command line
	Sys_ScanForCD();
#endif

	Sys_InitStreamThread();

	Com_Init( sys_cmdline );
	NET_Init();

	_getcwd (cwd, sizeof(cwd));
	Com_Printf("Working directory: %s\n", cwd);

	// hide the early console since we've reached the point where we
	// have a working graphics subsystems
	if ( !com_dedicated->integer && !com_viewlog->integer ) {
		Sys_ShowConsole( 0, qfalse );
	}

	Sys_InitWinkeyHook();
	Sys_InitTooltipShell();

    // main game loop
	while( 1 ) {
		// if not running as a game client, sleep a bit
		if ( g_wv.isMinimized || ( com_dedicated && com_dedicated->integer ) ) {
			Sleep( 5 );
		}

		// set low precision every frame, because some system calls
		// reset it arbitrarily
//		_controlfp( _PC_24, _MCW_PC );
//    _controlfp( -1, _MCW_EM  ); // no exceptions, even if some crappy
                                // syscall turns them back on!

		startTime = Sys_Milliseconds();

		// make sure mouse and joystick are only called once a frame
		IN_Frame();

		// run the game
		Com_Frame();

		endTime = Sys_Milliseconds();
		totalMsec += endTime - startTime;
		countMsec++;
	}

	// never gets here
}
