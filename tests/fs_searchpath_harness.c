#include <ctype.h>
#include <errno.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>

#ifdef _WIN32
#include <direct.h>
#include <windows.h>
#else
#include <dirent.h>
#include <strings.h>
#include <unistd.h>
#endif

#include "../src/code/game/q_shared.h"
#include "../src/code/qcommon/qcommon.h"

#ifdef _WIN32
#define QLR_TEST_EXPORT __declspec(dllexport)
#define QLR_STRICMP _stricmp
#define QLR_STRNICMP _strnicmp
#else
#define QLR_TEST_EXPORT
#define QLR_STRICMP strcasecmp
#define QLR_STRNICMP strncasecmp
#endif

void Sys_FreeFileList( char **list );
static char qlr_captured_log[16384];
static size_t qlr_captured_log_len = 0;

/*
=============
QLR_StrDup
=============
*/
static char *QLR_StrDup( const char *in ) {
	size_t length;
	char *copy;

	if ( !in ) {
		in = "";
	}

	length = strlen( in ) + 1;
	copy = malloc( length );
	if ( !copy ) {
		return NULL;
	}

	memcpy( copy, in, length );
	return copy;
}

/*
=============
QLR_PathIsDirectory
=============
*/
static qboolean QLR_PathIsDirectory( const char *path ) {
#ifdef _WIN32
	DWORD attributes = GetFileAttributesA( path );
	return attributes != INVALID_FILE_ATTRIBUTES && ( attributes & FILE_ATTRIBUTE_DIRECTORY ) != 0;
#else
	struct stat pathInfo;
	if ( stat( path, &pathInfo ) != 0 ) {
		return qfalse;
	}
	return S_ISDIR( pathInfo.st_mode ) ? qtrue : qfalse;
#endif
}

/*
=============
QLR_ClearCapturedLog
=============
*/
static void QLR_ClearCapturedLog( void ) {
	qlr_captured_log[0] = '\0';
	qlr_captured_log_len = 0;
}

/*
=============
QLR_AppendCapturedLog
=============
*/
static void QLR_AppendCapturedLog( const char *text ) {
	size_t available;
	size_t textLength;

	if ( !text || !*text || qlr_captured_log_len >= sizeof( qlr_captured_log ) - 1 ) {
		return;
	}

	available = sizeof( qlr_captured_log ) - qlr_captured_log_len - 1;
	textLength = strlen( text );
	if ( textLength > available ) {
		textLength = available;
	}

	memcpy( qlr_captured_log + qlr_captured_log_len, text, textLength );
	qlr_captured_log_len += textLength;
	qlr_captured_log[qlr_captured_log_len] = '\0';
}

/*
=============
QLR_WriteCapturedLog
=============
*/
static void QLR_WriteCapturedLog( FILE *stream, const char *fmt, va_list args ) {
	char message[2048];
	va_list copy;

	va_copy( copy, args );
	vsnprintf( message, sizeof( message ), fmt, copy );
	va_end( copy );

	fputs( message, stream );
	QLR_AppendCapturedLog( message );
}

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
void QDECL Com_Error( int level, const char *error, ... ) {
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
void QDECL Com_Printf( const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	QLR_WriteCapturedLog( stdout, fmt, args );
	va_end( args );
}

/*
=============
Com_DPrintf
=============
*/
void QDECL Com_DPrintf( const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	QLR_WriteCapturedLog( stdout, fmt, args );
	va_end( args );
}

/*
=============
Com_sprintf
=============
*/
int QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
	va_list args;
	int written;
	va_start( args, fmt );
	written = vsnprintf( dest, size, fmt, args );
	va_end( args );
	return written;
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
	return QLR_STRICMP( s1, s2 );
}

/*
=============
Q_stricmpn
=============
*/
int Q_stricmpn( const char *s1, const char *s2, int n ) {
	return QLR_STRNICMP( s1, s2, n );
}

/*
=============
Q_strnicmp
=============
*/
int Q_strnicmp( const char *s1, const char *s2, int n ) {
	return Q_stricmpn( s1, s2, n );
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
#ifdef _WIN32
	_mkdir( path );
#else
	mkdir( path, 0755 );
#endif
}

/*
=============
Sys_ListFiles
=============
*/
char **Sys_ListFiles( const char *directory, const char *extension, char *filter, int *numfiles, qboolean wantsubs ) {
	(void)filter;
#ifdef _WIN32
	WIN32_FIND_DATAA findData;
	HANDLE findHandle;
	char searchPattern[MAX_OSPATH];
	size_t allocated = 16;
	size_t count = 0;
	char **result = malloc( allocated * sizeof( char * ) );

	Com_sprintf( searchPattern, sizeof( searchPattern ), "%s\\*", directory );
	findHandle = FindFirstFileA( searchPattern, &findData );
	if ( !result ) {
		*numfiles = 0;
		return NULL;
	}
	if ( findHandle == INVALID_HANDLE_VALUE ) {
		free( result );
		*numfiles = 0;
		return NULL;
	}

	do {
		char fullPath[MAX_OSPATH];
		qboolean isDirectory = ( findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY ) != 0;

		if ( findData.cFileName[0] == '.' ) {
			continue;
		}
		if ( wantsubs && !isDirectory ) {
			continue;
		}
		if ( extension && extension[0] ) {
			size_t name_len = strlen( findData.cFileName );
			size_t ext_len = strlen( extension );
			if ( name_len < ext_len || strcmp( findData.cFileName + name_len - ext_len, extension ) != 0 ) {
				continue;
			}
		}
		if ( count == allocated ) {
			char **grown;
			allocated *= 2;
			grown = realloc( result, allocated * sizeof( char * ) );
			if ( !grown ) {
				FindClose( findHandle );
				Sys_FreeFileList( result );
				*numfiles = 0;
				return NULL;
			}
			result = grown;
		}
		Com_sprintf( fullPath, sizeof( fullPath ), "%s\\%s", directory, findData.cFileName );
		if ( wantsubs && !QLR_PathIsDirectory( fullPath ) ) {
			continue;
		}
		result[count] = QLR_StrDup( findData.cFileName );
		if ( !result[count] ) {
			FindClose( findHandle );
			Sys_FreeFileList( result );
			*numfiles = 0;
			return NULL;
		}
		count++;
	} while ( FindNextFileA( findHandle, &findData ) );

	FindClose( findHandle );
#else
	DIR *dir = opendir( directory );
	size_t allocated = 16;
	size_t count = 0;
	char **result = malloc( allocated * sizeof( char * ) );
	struct dirent *entry;

	if ( !result ) {
		*numfiles = 0;
		return NULL;
	}

	if ( !dir ) {
		free( result );
		*numfiles = 0;
		return NULL;
	}

	while ( ( entry = readdir( dir ) ) != NULL ) {
		char fullPath[MAX_OSPATH];

		if ( entry->d_name[0] == '.' ) {
			continue;
		}
		Com_sprintf( fullPath, sizeof( fullPath ), "%s/%s", directory, entry->d_name );
		if ( wantsubs && !QLR_PathIsDirectory( fullPath ) ) {
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
			char **grown;
			allocated *= 2;
			grown = realloc( result, allocated * sizeof( char * ) );
			if ( !grown ) {
				closedir( dir );
				Sys_FreeFileList( result );
				*numfiles = 0;
				return NULL;
			}
			result = grown;
		}
		result[count] = QLR_StrDup( entry->d_name );
		if ( !result[count] ) {
			closedir( dir );
			Sys_FreeFileList( result );
			*numfiles = 0;
			return NULL;
		}
		count++;
	}
	closedir( dir );
#endif

	{
		char **grown = realloc( result, ( count + 1 ) * sizeof( char * ) );
		if ( !grown ) {
			Sys_FreeFileList( result );
			*numfiles = 0;
			return NULL;
		}
		result = grown;
	}
	result[count] = NULL;
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
	return QLR_StrDup( in );
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
char *va( const char *format, ... ) {
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
	var->name = QLR_StrDup( var_name );
	var->string = QLR_StrDup( value );
	var->resetString = QLR_StrDup( value );
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
COM_SkipPath
=============
*/
char *COM_SkipPath( char *pathname ) {
	char *last = pathname;

	if ( !pathname ) {
		return NULL;
	}

	for ( ; *pathname; pathname++ ) {
		if ( *pathname == '/' || *pathname == '\\' ) {
			last = pathname + 1;
		}
	}

	return last;
}

/*
=============
NET_DemoProtocol
=============
*/
int NET_DemoProtocol( void ) {
	return QL_RETAIL_PROTOCOL_VERSION;
}

/*
=============
File system harness helpers
=============
*/
#include "../src/code/qcommon/files.c"

static qboolean qlr_test_steam_user_available = qfalse;
static uint32_t qlr_test_steam_id_low = 0u;
static uint32_t qlr_test_steam_id_high = 0u;

/*
=============
QL_Steamworks_GetNumSubscribedItems
=============
*/
uint32_t QL_Steamworks_GetNumSubscribedItems( void ) {
	return 0u;
}

/*
=============
QL_Steamworks_HasUGCInterface
=============
*/
qboolean QL_Steamworks_HasUGCInterface( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_GetSubscribedItems
=============
*/
uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems ) {
	(void)outItemIds;
	(void)maxItems;
	return 0u;
}

/*
=============
QL_Steamworks_GetItemInstallInfo
=============
*/
qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp ) {
	(void)idLow;
	(void)idHigh;

	if ( outSizeOnDisk ) {
		*outSizeOnDisk = 0u;
	}
	if ( folder && folderSize > 0 ) {
		folder[0] = '\0';
	}
	if ( outTimestamp ) {
		*outTimestamp = 0u;
	}

	return qfalse;
}

/*
=============
QL_Steamworks_GetUserSteamID
=============
*/
qboolean QL_Steamworks_GetUserSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	if ( !qlr_test_steam_user_available ) {
		return qfalse;
	}

	if ( outIdLow ) {
		*outIdLow = qlr_test_steam_id_low;
	}
	if ( outIdHigh ) {
		*outIdHigh = qlr_test_steam_id_high;
	}

	return qtrue;
}

static cvar_t fs_stub_debug = { .name = "fs_debug", .string = "0", .resetString = "0", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_basepath = { .name = "fs_basepath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_homepath = { .name = "fs_homepath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_cdpath = { .name = "fs_cdpath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_webpath = { .name = "fs_webpath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_webMappings = { .name = "fs_webMappings", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_basegame = { .name = "fs_basegame", .string = "baseq3", .resetString = "baseq3", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_copyfiles = { .name = "fs_copyfiles", .string = "0", .resetString = "0", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_copypath = { .name = "fs_copypath", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_gamedirvar = { .name = "fs_game", .string = "", .resetString = "", .flags = 0, .value = 0.0f, .integer = 0 };
static cvar_t fs_stub_restrict = { .name = "fs_restrict", .string = "0", .resetString = "0", .flags = 0, .value = 0.0f, .integer = 0 };

qboolean com_fullyInitialized = qfalse;
cvar_t *com_buildScript = NULL;
cvar_t *com_journal = NULL;
fileHandle_t com_journalDataFile = 0;
vm_t *currentVM = NULL;

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
QLR_TEST_EXPORT void QLR_FS_TestInitCvars( const char *basepath, const char *homepath ) {
	QLR_ClearCapturedLog();
	qlr_test_steam_user_available = qfalse;
	qlr_test_steam_id_low = 0u;
	qlr_test_steam_id_high = 0u;
	fs_debug = &fs_stub_debug;
	fs_debug->string = QLR_StrDup( "0" );
	fs_basepath = &fs_stub_basepath;
	fs_basepath->string = QLR_StrDup( basepath );
	fs_homepath = &fs_stub_homepath;
	fs_homepath->string = QLR_StrDup( homepath );
	fs_cdpath = &fs_stub_cdpath;
	fs_cdpath->string = QLR_StrDup( basepath );
	fs_webpath = &fs_stub_webpath;
	fs_webpath->string = QLR_StrDup( basepath );
	fs_webMappings = &fs_stub_webMappings;
	fs_webMappings->string = QLR_StrDup( fs_defaultFallbackMappings );
	fs_basegame = &fs_stub_basegame;
	fs_basegame->string = QLR_StrDup( fs_stub_basegame.string );
	fs_copyfiles = &fs_stub_copyfiles;
	fs_copyfiles->string = QLR_StrDup( "0" );
	fs_copypath = &fs_stub_copypath;
	fs_copypath->string = QLR_StrDup( "" );
	fs_gamedirvar = &fs_stub_gamedirvar;
	fs_restrict = &fs_stub_restrict;
	fs_restrict->string = QLR_StrDup( "0" );
	Q_strncpyz( fs_gamedir, "baseq3", sizeof( fs_gamedir ) );
	FS_ParseFallbackMappings( fs_webMappings->string );
}

/*
=============
QLR_FS_TestShutdown
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestShutdown( void ) {
	FS_Shutdown( qtrue );
}

/*
=============
QLR_FS_TestClearCapturedLog
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestClearCapturedLog( void ) {
	QLR_ClearCapturedLog();
}

/*
=============
QLR_FS_TestCapturedLog
=============
*/
QLR_TEST_EXPORT const char *QLR_FS_TestCapturedLog( void ) {
	return qlr_captured_log;
}

/*
=============
QLR_FS_TestSetRestrict
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestSetRestrict( int restrictValue ) {
	char buffer[16];
	fs_stub_restrict.integer = restrictValue;
	fs_stub_restrict.value = (float)restrictValue;
	snprintf( buffer, sizeof( buffer ), "%d", restrictValue );
	free( fs_stub_restrict.string );
	fs_stub_restrict.string = QLR_StrDup( buffer );
}

/*
=============
QLR_FS_TestSetDebug
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestSetDebug( int debugValue ) {
	char buffer[16];

	fs_stub_debug.integer = debugValue;
	fs_stub_debug.value = (float)debugValue;
	snprintf( buffer, sizeof( buffer ), "%d", debugValue );
	free( fs_stub_debug.string );
	fs_stub_debug.string = QLR_StrDup( buffer );
}

/*
=============
QLR_FS_TestSetSteamUserId
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestSetSteamUserId( int available, uint32_t steamIdLow, uint32_t steamIdHigh ) {
	qlr_test_steam_user_available = available ? qtrue : qfalse;
	qlr_test_steam_id_low = steamIdLow;
	qlr_test_steam_id_high = steamIdHigh;
}

/*
=============
QLR_FS_TestResolveHomePath
=============
*/
QLR_TEST_EXPORT const char *QLR_FS_TestResolveHomePath( const char *basepath ) {
	return FS_ResolveHomePath( basepath );
}

/*
=============
QLR_FS_TestSetWebPath
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestSetWebPath( const char *webpath ) {
	free( fs_stub_webpath.string );
	fs_stub_webpath.string = QLR_StrDup( webpath );
}

/*
=============
QLR_FS_TestSetFallbackMappings
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestSetFallbackMappings( const char *rawMappings ) {
	free( fs_stub_webMappings.string );
	fs_stub_webMappings.string = QLR_StrDup( rawMappings );
	FS_ParseFallbackMappings( fs_stub_webMappings.string );
}

/*
=============
QLR_FS_TestRewriteWebPath
=============
*/
QLR_TEST_EXPORT int QLR_FS_TestRewriteWebPath( const char *uri, char *outPath, size_t outSize ) {
	return FS_RewriteWebPath( uri, outPath, (int)outSize );
}

/*
=============
QLR_FS_TestOpenWebFileRead
=============
*/
QLR_TEST_EXPORT int QLR_FS_TestOpenWebFileRead( const char *request, char *resolvedPath, size_t resolvedSize, char *buffer, size_t bufferSize ) {
	fileHandle_t file;
	int length;

	file = 0;
	if ( !FS_FOpenWebFileRead( request, &file, resolvedPath, resolvedSize ) ) {
		return -1;
	}

	length = FS_filelength( file );
	if ( buffer && bufferSize > 0 ) {
		int readLength;

		readLength = length;
		if ( readLength >= (int)bufferSize ) {
			readLength = (int)bufferSize - 1;
		}

		if ( readLength > 0 ) {
			FS_Read( buffer, readLength, file );
		}
		buffer[readLength > 0 ? readLength : 0] = '\0';
	}

	FS_FCloseFile( file );
	return length;
}

/*
=============
QLR_FS_TestAddGameDirectory
=============
*/
QLR_TEST_EXPORT void QLR_FS_TestAddGameDirectory( const char *path, const char *gamedir ) {
	FS_AddGameDirectory( path, gamedir );
}

/*
=============
QLR_FS_TestLoadedPakNames
=============
*/
QLR_TEST_EXPORT const char *QLR_FS_TestLoadedPakNames( void ) {
	return FS_LoadedPakNames();
}

/*
=============
QLR_FS_TestReferencedPakChecksums
=============
*/
QLR_TEST_EXPORT const char *QLR_FS_TestReferencedPakChecksums( void ) {
	return FS_ReferencedPakChecksums();
}

/*
=============
QLR_FS_TestReferencedPakNames
=============
*/
QLR_TEST_EXPORT const char *QLR_FS_TestReferencedPakNames( void ) {
	return FS_ReferencedPakNames();
}

/*
=============
QLR_FS_TestSetPakReferences
=============
*/
QLR_TEST_EXPORT int QLR_FS_TestSetPakReferences( const char *pakBasename, int flags ) {
	searchpath_t *search;
	int matched;

	matched = 0;

	for ( search = fs_searchpaths; search; search = search->next ) {
		if ( !search->pack ) {
			continue;
		}

		if ( Q_stricmp( search->pack->pakBasename, pakBasename ) ) {
			continue;
		}

		search->pack->referenced = flags;
		matched++;
	}

	return matched;
}

/*
=============
QLR_FS_TestReadFile
=============
*/
QLR_TEST_EXPORT int QLR_FS_TestReadFile( const char *filename, qboolean uniqueFILE, char *buffer, size_t bufferSize, uintptr_t *handlePtr ) {
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

