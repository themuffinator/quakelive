#include <dirent.h>
#include <errno.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#include "../src/code/game/q_shared.h"
#include "../src/code/qcommon/qcommon.h"

/*
=============
Cbuf_AddText
=============
*/
void Cbuf_AddText( const char *text ) {
	(void)text;
}

/*
=============
Cmd_AddCommand
=============
*/
void Cmd_AddCommand( const char *cmd_name, xcommand_t function ) {
	(void)cmd_name;
	(void)function;
}

/*
=============
Cmd_RemoveCommand
=============
*/
void Cmd_RemoveCommand( const char *cmd_name ) {
	(void)cmd_name;
}

/*
=============
Cmd_Argc
=============
*/
int Cmd_Argc( void ) {
	return 0;
}

/*
=============
Cmd_Argv
=============
*/
char *Cmd_Argv( int arg ) {
	(void)arg;
	return "";
}

/*
=============
Cmd_TokenizeString
=============
*/
void Cmd_TokenizeString( const char *text_in ) {
	(void)text_in;
}

/*
=============
Com_Error
=============
*/
void Com_Error( int level, const char *error, ... ) {
	va_list args;
	(void)level;
	va_start( args, error );
	vfprintf( stderr, error, args );
	fprintf( stderr, "\n" );
	va_end( args );
	exit( 1 );
}

/*
=============
Com_Printf
=============
*/
void Com_Printf( const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	vfprintf( stdout, fmt, args );
	va_end( args );
}

/*
=============
Com_DPrintf
=============
*/
void Com_DPrintf( const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	vfprintf( stdout, fmt, args );
	va_end( args );
}

/*
=============
Com_sprintf
=============
*/
void Com_sprintf( char *dest, int size, const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	vsnprintf( dest, size, fmt, args );
	va_end( args );
}

/*
=============
Com_SafeMode
=============
*/
qboolean Com_SafeMode( void ) {
	return qfalse;
}

/*
=============
Com_StartupVariable
=============
*/
void Com_StartupVariable( const char *match ) {
	(void)match;
}

/*
=============
Com_BlockChecksum
=============
*/
unsigned int Com_BlockChecksum( const void *buffer, int length ) {
	unsigned int checksum = 0;
	const unsigned char *bytes = buffer;
	for ( int i = 0; i < length; i++ ) {
		checksum += bytes[i];
	}
	return checksum;
}

/*
=============
Com_BlockChecksumKey
=============
*/
unsigned int Com_BlockChecksumKey( void *buffer, int length, int key ) {
	return Com_BlockChecksum( buffer, length ) ^ (unsigned int)key;
}

/*
=============
Q_stricmp
=============
*/
/*
=============
Com_FilterPath
=============
*/
int Com_FilterPath( char *filter, char *name, int casesensitive ) {
	(void)filter;
	(void)name;
	(void)casesensitive;
	return 0;
}

int Q_stricmp( const char *s1, const char *s2 ) {
	return strcasecmp( s1, s2 );
}

/*
=============
Q_stricmpn
=============
*/
int Q_stricmpn( const char *s1, const char *s2, int n ) {
	return strncasecmp( s1, s2, n );
}

/*
=============
Q_strncpyz
=============
*/
void Q_strncpyz( char *dest, const char *src, int destsize ) {
	if ( destsize <= 0 ) {
		return;
	}
	strncpy( dest, src, destsize - 1 );
	dest[destsize - 1] = '\0';
}

/*
=============
Q_strcat
=============
*/
void Q_strcat( char *dest, int size, const char *src ) {
	int len = strlen( dest );
	Q_strncpyz( dest + len, src, size - len );
}

/*
=============
Q_strlwr
=============
*/
char *Q_strlwr( char *s1 ) {
	for ( char *c = s1; *c; c++ ) {
		*c = (char)tolower( *c );
	}
	return s1;
}

/*
=============
Com_Memset
=============
*/
void Com_Memset( void *dest, const int fill, const size_t count ) {
	memset( dest, fill, count );
}

/*
=============
Com_Memcpy
=============
*/
void Com_Memcpy( void *dest, const void *src, const size_t count ) {
	memcpy( dest, src, count );
}

/*
=============
Sys_DefaultHomePath
=============
*/
char *Sys_DefaultHomePath( void ) {
	return getenv( "HOME" );
}

/*
=============
Sys_DefaultInstallPath
=============
*/
char *Sys_DefaultInstallPath( void ) {
	return ".";
}

/*
=============
Sys_DefaultCDPath
=============
*/
char *Sys_DefaultCDPath( void ) {
	return ".";
}

/*
=============
Sys_Mkdir
=============
*/
void Sys_Mkdir( const char *path ) {
	mkdir( path, 0755 );
}

/*
=============
Sys_ListFiles
=============
*/
char **Sys_ListFiles( const char *directory, const char *extension, char *filter, int *numfiles, qboolean wantsubs ) {
	(void)filter;
	(void)wantsubs;
	DIR *dir = opendir( directory );
	if ( !dir ) {
		*numfiles = 0;
		return NULL;
	}

	size_t allocated = 16;
	size_t count = 0;
	char **result = malloc( allocated * sizeof( char * ) );
	struct dirent *entry;

	while ( ( entry = readdir( dir ) ) != NULL ) {
		if ( entry->d_name[0] == '.' ) {
			continue;
		}
		if ( extension ) {
			size_t name_len = strlen( entry->d_name );
			size_t ext_len = strlen( extension );
			if ( name_len < ext_len || strcmp( entry->d_name + name_len - ext_len, extension ) != 0 ) {
				continue;
			}
		}
		if ( count == allocated ) {
			allocated *= 2;
			result = realloc( result, allocated * sizeof( char * ) );
		}
		result[count] = strdup( entry->d_name );
		count++;
	}

	result = realloc( result, (count + 1) * sizeof( char * ) );
	result[count] = NULL;
	closedir( dir );
	*numfiles = (int)count;
	return result;
}

/*
=============
Sys_FreeFileList
=============
*/
void Sys_FreeFileList( char **list ) {
	if ( !list ) {
		return;
	}
	for ( char **cursor = list; *cursor; cursor++ ) {
		free( *cursor );
	}
	free( list );
}

/*
=============
Sys_BeginStreamedFile
=============
*/
void Sys_BeginStreamedFile( fileHandle_t f, int readahead ) {
	(void)f;
	(void)readahead;
}

/*
=============
Sys_EndStreamedFile
=============
*/
void Sys_EndStreamedFile( fileHandle_t f ) {
	(void)f;
}

/*
=============
Z_Malloc
=============
*/
void *Z_Malloc( int size ) {
	return calloc( 1, (size_t)size );
}

/*
=============
Z_Free
=============
*/
void Z_Free( void *ptr ) {
	free( ptr );
}

/*
=============
CopyString
=============
*/
char *CopyString( const char *in ) {
	return strdup( in );
}

/*
=============
Hunk_AllocateTempMemory
=============
*/
void *Hunk_AllocateTempMemory( int size ) {
	return malloc( (size_t)size );
}

/*
=============
Hunk_FreeTempMemory
=============
*/
void Hunk_FreeTempMemory( void *buf ) {
	free( buf );
}

/*
=============
S_ClearSoundBuffer
=============
*/
/*
=============
Hunk_ClearTempMemory
=============
*/
void Hunk_ClearTempMemory( void ) {
}

void S_ClearSoundBuffer( void ) {
}

/*
=============
va
=============
*/
char *va( char *format, ... ) {
	static char buffer[4096];
	va_list args;
	va_start( args, format );
	vsnprintf( buffer, sizeof( buffer ), format, args );
	va_end( args );
	return buffer;
}

/*
=============
Cvar_Set
=============
*/
void Cvar_Set( const char *var_name, const char *value ) {
	(void)var_name;
	(void)value;
}

/*
=============
Cvar_Get
=============
*/
cvar_t *Cvar_Get( const char *var_name, const char *value, int flags ) {
	cvar_t *var = calloc( 1, sizeof( cvar_t ) );
	var->name = strdup( var_name );
	var->string = strdup( value );
	var->resetString = strdup( value );
	var->flags = flags;
	var->value = (float)atof( value );
	var->integer = atoi( value );
	return var;
}

/*
=============
Com_ReadCDKey
=============
*/
void Com_ReadCDKey( const char *filename ) {
	(void)filename;
}

/*
=============
Com_AppendCDKey
=============
*/
void Com_AppendCDKey( const char *filename ) {
	(void)filename;
}

/*
=============
File system harness helpers
=============
*/
#include "../src/code/qcommon/files.c"

static cvar_t fs_stub_debug = { .name = "fs_debug", .string = "0", .resetString = "0", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_basepath = { .name = "fs_basepath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_homepath = { .name = "fs_homepath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_cdpath = { .name = "fs_cdpath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_basegame = { .name = "fs_basegame", .string = "baseq3", .resetString = "baseq3", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_copyfiles = { .name = "fs_copyfiles", .string = "0", .resetString = "0", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_gamedirvar = { .name = "fs_game", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_restrict = { .name = "fs_restrict", .string = "0", .resetString = "0", .flags = 0, .value = 0.0f, .integer = 0 };

qboolean com_fullyInitialized = qfalse;
cvar_t *com_journal = NULL;
fileHandle_t com_journalDataFile = 0;

/*
=============
Sys_StreamedRead
=============
*/
int Sys_StreamedRead( void *buffer, int size, int count, fileHandle_t f ) {
	return (int)fread( buffer, (size_t)size, (size_t)count, fsh[f].handleFiles.file.o );
}

/*
=============
Sys_StreamSeek
=============
*/
void Sys_StreamSeek( fileHandle_t f, int offset, int origin ) {
	fseek( fsh[f].handleFiles.file.o, offset, origin );
}

/*
=============
QLR_FS_TestInitCvars
=============
*/
void QLR_FS_TestInitCvars( const char *basepath, const char *homepath ) {
	fs_debug = &fs_stub_debug;
	fs_debug->string = strdup( "0" );
	fs_basepath = &fs_stub_basepath;
	fs_basepath->string = strdup( basepath );
	fs_homepath = &fs_stub_homepath;
	fs_homepath->string = strdup( homepath );
	fs_cdpath = &fs_stub_cdpath;
	fs_cdpath->string = strdup( basepath );
	fs_basegame = &fs_stub_basegame;
	fs_basegame->string = strdup( fs_stub_basegame.string );
	fs_copyfiles = &fs_stub_copyfiles;
	fs_copyfiles->string = strdup( "0" );
	fs_gamedirvar = &fs_stub_gamedirvar;
	fs_restrict = &fs_stub_restrict;
	fs_restrict->string = strdup( "0" );
}

/*
=============
QLR_FS_TestShutdown
=============
*/
void QLR_FS_TestShutdown( void ) {
	FS_Shutdown( qtrue );
}

/*
=============
QLR_FS_TestSetRestrict
=============
*/
void QLR_FS_TestSetRestrict( int restrictValue ) {
	char buffer[16];
	fs_stub_restrict.integer = restrictValue;
	fs_stub_restrict.value = (float)restrictValue;
	snprintf( buffer, sizeof( buffer ), "%d", restrictValue );
	free( fs_stub_restrict.string );
	fs_stub_restrict.string = strdup( buffer );
}

/*
=============
QLR_FS_TestAddGameDirectory
=============
*/
void QLR_FS_TestAddGameDirectory( const char *path, const char *gamedir ) {
	FS_AddGameDirectory( path, gamedir );
}

/*
=============
QLR_FS_TestReadFile
=============
*/
int QLR_FS_TestReadFile( const char *filename, qboolean uniqueFILE, char *buffer, size_t bufferSize, uintptr_t *handlePtr ) {
	fileHandle_t file = 0;
	int length = FS_FOpenFileRead( filename, &file, uniqueFILE );
	if ( length <= 0 ) {
		return length;
	}
	if ( (size_t)length >= bufferSize ) {
		length = (int)bufferSize - 1;
	}
	FS_Read( buffer, length, file );
	buffer[length] = '\0';
	if ( fsh[file].zipFile ) {
		*handlePtr = (uintptr_t)fsh[file].handleFiles.file.z;
	} else {
		*handlePtr = (uintptr_t)fsh[file].handleFiles.file.o;
	}
	FS_FCloseFile( file );
	return length;
}

