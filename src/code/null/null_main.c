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
// sys_null.h -- null system driver to aid porting efforts

#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined( _WIN32 )
	#include <direct.h>
	#include <sys/timeb.h>
#else
	#include <sys/stat.h>
	#include <sys/time.h>
	#include <unistd.h>
#endif

#include "../game/q_shared.h"
#include "../qcommon/qcommon.h"

static unsigned long	sys_timeBase;
static char				sys_executablePath[MAX_OSPATH];
static char				sys_cdPath[MAX_OSPATH];
static char				sys_installPath[MAX_OSPATH];
static char				sys_homePath[MAX_OSPATH];

/*
==================
Sys_CurrentWallClockMilliseconds
==================
*/
static unsigned long Sys_CurrentWallClockMilliseconds( void ) {
#if defined( _WIN32 )
	struct _timeb	timeBuffer;

	_ftime( &timeBuffer );
	return (unsigned long)timeBuffer.time * 1000ul + (unsigned long)timeBuffer.millitm;
#else
	struct timeval	timeBuffer;

	gettimeofday( &timeBuffer, NULL );
	return (unsigned long)timeBuffer.tv_sec * 1000ul + (unsigned long)( timeBuffer.tv_usec / 1000 );
#endif
}

/*
==================
Sys_CopyDirectoryName
==================
*/
static void Sys_CopyDirectoryName( const char *path, char *buffer, size_t bufferSize ) {
	char	*separator;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !path || !path[0] ) {
		Q_strncpyz( buffer, Sys_Cwd(), bufferSize );
		return;
	}

	Q_strncpyz( buffer, path, bufferSize );
	separator = strrchr( buffer, '/' );
	if ( !separator ) {
		separator = strrchr( buffer, '\\' );
	}

	if ( separator ) {
		*separator = '\0';
		if ( buffer[0] ) {
			return;
		}
	}

	Q_strncpyz( buffer, Sys_Cwd(), bufferSize );
}

/*
==================
Sys_BeginStreamedFile
==================
*/
void Sys_BeginStreamedFile( fileHandle_t f, int readAhead ) {
	(void)f;
	(void)readAhead;
}

/*
==================
Sys_EndStreamedFile
==================
*/
void Sys_EndStreamedFile( fileHandle_t f ) {
	(void)f;
}

/*
==================
Sys_StreamedRead
==================
*/
int Sys_StreamedRead( void *buffer, int size, int count, fileHandle_t f ) {
	return FS_Read( buffer, size * count, f );
}

/*
==================
Sys_StreamSeek
==================
*/
void Sys_StreamSeek( fileHandle_t f, int offset, int origin ) {
	FS_Seek( f, offset, origin );
}

/*
==================
Sys_Error
==================
*/
void QDECL Sys_Error( const char *error, ... ) {
	va_list	argptr;

	fprintf( stderr, "Sys_Error: " );
	va_start( argptr, error );
	vfprintf( stderr, error, argptr );
	va_end( argptr );
	fprintf( stderr, "\n" );

	exit( 1 );
}

/*
==================
Sys_Quit
==================
*/
void Sys_Quit( void ) {
	exit( 0 );
}

/*
==================
Sys_UnloadGame
==================
*/
void Sys_UnloadGame( void ) {
}

/*
==================
Sys_GetGameAPI
==================
*/
void *Sys_GetGameAPI( void *parms ) {
	(void)parms;
	return NULL;
}

/*
==================
Sys_GetClipboardData
==================
*/
char *Sys_GetClipboardData( void ) {
	return NULL;
}

/*
==================
Sys_Print
==================
*/
void Sys_Print( const char *msg ) {
	if ( !msg ) {
		return;
	}

	fputs( msg, stderr );
}

/*
==================
Sys_DisplaySystemConsole
==================
*/
void Sys_DisplaySystemConsole( qboolean show ) {
	(void)show;
}

/*
==================
Sys_SetErrorText
==================
*/
void Sys_SetErrorText( const char *text ) {
	(void)text;
}

/*
==================
Sys_ExecutableBaseName
==================
*/
char *Sys_ExecutableBaseName( void ) {
	char	*separator;

	separator = strrchr( sys_executablePath, '/' );
	if ( !separator ) {
		separator = strrchr( sys_executablePath, '\\' );
	}

	return separator ? separator + 1 : sys_executablePath;
}

/*
==================
Sys_Milliseconds
==================
*/
int Sys_Milliseconds( void ) {
	unsigned long	currentMilliseconds;

	currentMilliseconds = Sys_CurrentWallClockMilliseconds();
	if ( !sys_timeBase ) {
		sys_timeBase = currentMilliseconds;
		return 0;
	}

	return (int)( currentMilliseconds - sys_timeBase );
}

/*
==================
Sys_Mkdir
==================
*/
void Sys_Mkdir( const char *path ) {
	if ( !path || !path[0] ) {
		return;
	}

#if defined( _WIN32 )
	_mkdir( path );
#else
	mkdir( path, 0777 );
#endif
}

/*
==================
Sys_Cwd
==================
*/
char *Sys_Cwd( void ) {
	static char	cwd[MAX_OSPATH];

#if defined( _WIN32 )
	if ( !_getcwd( cwd, sizeof( cwd ) - 1 ) ) {
		cwd[0] = '\0';
	}
#else
	if ( !getcwd( cwd, sizeof( cwd ) - 1 ) ) {
		cwd[0] = '\0';
	}
#endif

	cwd[MAX_OSPATH - 1] = '\0';
	return cwd;
}

/*
==================
Sys_SetDefaultCDPath
==================
*/
void Sys_SetDefaultCDPath( const char *path ) {
	Q_strncpyz( sys_cdPath, path ? path : "", sizeof( sys_cdPath ) );
}

/*
==================
Sys_DefaultCDPath
==================
*/
char *Sys_DefaultCDPath( void ) {
	return sys_cdPath;
}

/*
==================
Sys_SetDefaultInstallPath
==================
*/
void Sys_SetDefaultInstallPath( const char *path ) {
	Q_strncpyz( sys_installPath, path ? path : "", sizeof( sys_installPath ) );
}

/*
==================
Sys_DefaultInstallPath
==================
*/
char *Sys_DefaultInstallPath( void ) {
	if ( sys_installPath[0] ) {
		return sys_installPath;
	}

	return Sys_Cwd();
}

/*
==================
Sys_SetDefaultHomePath
==================
*/
void Sys_SetDefaultHomePath( const char *path ) {
	Q_strncpyz( sys_homePath, path ? path : "", sizeof( sys_homePath ) );
}

/*
==================
Sys_DefaultHomePath
==================
*/
char *Sys_DefaultHomePath( void ) {
	const char	*environmentValue;

	if ( sys_homePath[0] ) {
		return sys_homePath;
	}

	environmentValue = getenv( "HOME" );
	if ( !environmentValue || !environmentValue[0] ) {
		environmentValue = getenv( "USERPROFILE" );
	}

	if ( environmentValue && environmentValue[0] ) {
		Q_strncpyz( sys_homePath, environmentValue, sizeof( sys_homePath ) );
		Q_strcat( sys_homePath, sizeof( sys_homePath ), "/.q3a" );
		Sys_Mkdir( sys_homePath );
		return sys_homePath;
	}

	return Sys_Cwd();
}

/*
==================
Sys_GetCurrentUser
==================
*/
char *Sys_GetCurrentUser( void ) {
	static char	userName[128];
	const char	*environmentValue;

	environmentValue = getenv( "USER" );
	if ( !environmentValue || !environmentValue[0] ) {
		environmentValue = getenv( "USERNAME" );
	}

	if ( environmentValue && environmentValue[0] ) {
		Q_strncpyz( userName, environmentValue, sizeof( userName ) );
	} else {
		Q_strncpyz( userName, "player", sizeof( userName ) );
	}

	return userName;
}

/*
==================
Sys_Init
==================
*/
void Sys_Init( void ) {
}

/*
==================
Sys_EarlyOutput
==================
*/
void Sys_EarlyOutput( char *string ) {
	if ( string ) {
		printf( "%s", string );
	}
}

/*
==================
main
==================
*/
int main( int argc, char **argv ) {
	int		cmdlineLength;
	int		i;
	char	*cmdline;
	char	executableDirectory[MAX_OSPATH];

	if ( argc > 0 && argv && argv[0] ) {
		Q_strncpyz( sys_executablePath, argv[0], sizeof( sys_executablePath ) );
		Sys_CopyDirectoryName( argv[0], executableDirectory, sizeof( executableDirectory ) );
		Sys_SetDefaultCDPath( executableDirectory );
		Sys_SetDefaultInstallPath( executableDirectory );
	}

	cmdlineLength = 1;
	for ( i = 1; i < argc; i++ ) {
		cmdlineLength += (int)strlen( argv[i] ) + 1;
	}

	cmdline = malloc( cmdlineLength );
	if ( !cmdline ) {
		Sys_Error( "null_main: unable to allocate command line buffer" );
		return 1;
	}

	*cmdline = '\0';
	for ( i = 1; i < argc; i++ ) {
		if ( i > 1 ) {
			strcat( cmdline, " " );
		}
		strcat( cmdline, argv[i] );
	}

	Com_Init( cmdline );
	NET_Init();

	while ( 1 ) {
		Com_Frame();
	}
}
