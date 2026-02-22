#include "client.h"

#include <stdio.h>

#define MAX_STEAM_RESOURCES 64
#define STEAM_URL_PREFIX "steam://"

typedef struct {
	char		url[MAX_QPATH];
	char		cachePath[MAX_QPATH];
	qhandle_t	shader;
	qboolean	persisted;
} clSteamResource_t;

static clSteamResource_t cl_steamResources[MAX_STEAM_RESOURCES];
static cvar_t *cl_steamCachePersist;
static cvar_t *cl_steamCachePath;

qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize );
void Sys_Steam_FreeRequestBuffer( byte *buffer );
char *FS_BuildOSPath( const char *base, const char *game, const char *qpath );

/*
=============
CL_SteamResources_IsSteamURL

Returns qtrue when the provided resource begins with the Steam URL scheme.
=============
*/
static qboolean CL_SteamResources_IsSteamURL( const char *url ) {
	if ( !url ) {
		return qfalse;
	}

	return ( Q_strnicmp( url, STEAM_URL_PREFIX, strlen( STEAM_URL_PREFIX ) ) == 0 );
}

/*
=============
CL_SteamResources_FindSlot

Returns an existing slot for the URL or the first available free slot.
=============
*/
static clSteamResource_t *CL_SteamResources_FindSlot( const char *url ) {
	int i;
	clSteamResource_t *freeSlot = NULL;

	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		clSteamResource_t *entry = &cl_steamResources[i];

		if ( entry->url[0] && !Q_stricmp( entry->url, url ) ) {
			return entry;
		}

		if ( !entry->url[0] && !freeSlot ) {
			freeSlot = entry;
		}
	}

	return freeSlot;
}

/*
=============
CL_SteamResources_AssignSlot

Stores the resolved shader and cache path for a Steam resource.
=============
*/
static void CL_SteamResources_AssignSlot( clSteamResource_t *slot, const char *url, const char *cachePath, qhandle_t shader, qboolean persisted ) {
	if ( !slot ) {
		return;
	}

	Q_strncpyz( slot->url, url, sizeof( slot->url ) );
	Q_strncpyz( slot->cachePath, cachePath, sizeof( slot->cachePath ) );
	slot->shader = shader;
	slot->persisted = persisted;
}

/*
=============
CL_SteamResources_SanitizeCacheName

Builds a cache file path under fs_homepath for the provided Steam URL.
=============
*/
static void CL_SteamResources_SanitizeCacheName( const char *url, char *cachePath, size_t cachePathSize ) {
	const char *payload;
	char sanitized[MAX_QPATH];
	unsigned checksum;
	int i;
	const char *cacheFolder;

	if ( !cachePath || cachePathSize == 0 || !url ) {
		return;
	}

	payload = url;
	if ( CL_SteamResources_IsSteamURL( url ) ) {
		payload = url + strlen( STEAM_URL_PREFIX );
	}

	Q_strncpyz( sanitized, payload, sizeof( sanitized ) );
	for ( i = 0; sanitized[i]; i++ ) {
		char ch = sanitized[i];
		if ( !( ( ch >= 'a' && ch <= 'z' ) || ( ch >= 'A' && ch <= 'Z' ) || ( ch >= '0' && ch <= '9' ) || ch == '.' || ch == '-' || ch == '_' ) ) {
			sanitized[i] = '_';
		}
	}

	cacheFolder = ( cl_steamCachePath && cl_steamCachePath->string[0] ) ? cl_steamCachePath->string : "steamcache";
	checksum = Com_BlockChecksum( url, strlen( url ) );
	Com_sprintf( cachePath, cachePathSize, "%s/%08x_%s", cacheFolder, checksum, sanitized );
}


/*
=============
CL_SteamResources_RegisterCachedShader

Registers a shader from an existing cache file if one is present.
=============
*/
static qboolean CL_SteamResources_RegisterCachedShader( const char *cachePath, qhandle_t *shader ) {
	if ( !cachePath || !cachePath[0] || !shader ) {
		return qfalse;
	}

	if ( !FS_FileExists( cachePath ) ) {
		return qfalse;
	}

	*shader = re.RegisterShaderNoMip( cachePath );
	return ( *shader != 0 );
}

/*
=============
CL_SteamResources_WriteCacheFile

Writes downloaded image bytes to a cache file under fs_homepath.
=============
*/
static qboolean CL_SteamResources_WriteCacheFile( const char *cachePath, const byte *buffer, int length ) {
	fileHandle_t handle;

	if ( !cachePath || !cachePath[0] || !buffer || length <= 0 ) {
		return qfalse;
	}

	handle = FS_FOpenFileWrite( cachePath );
	if ( !handle ) {
		return qfalse;
	}

	FS_Write( buffer, length, handle );
	FS_FCloseFile( handle );
	return qtrue;
}

/*
=============
CL_SteamResources_CleanupTransient

Removes a transient cache file when persistence is disabled.
=============
*/
static void CL_SteamResources_CleanupTransient( const char *cachePath ) {
	const char *homePath;
	const char *gameDir;
	char *ospath;

	if ( !cachePath || !cachePath[0] ) {
		return;
	}

	homePath = Cvar_VariableString( "fs_homepath" );
	gameDir = Cvar_VariableString( "fs_gamedirvar" );
	if ( !gameDir || !gameDir[0] ) {
		gameDir = Cvar_VariableString( "fs_game" );
	}
	if ( !gameDir || !gameDir[0] ) {
		gameDir = BASEGAME;
	}

	ospath = FS_BuildOSPath( homePath, gameDir, cachePath );
	remove( ospath );
}

/*
=============
CL_SteamResources_RequestAndCache

Downloads a Steam resource, stores it to disk when requested, and registers a shader for UI use.
=============
*/
static qboolean CL_SteamResources_RequestAndCache( const char *url, const char *cachePath, qboolean persist, qhandle_t *shader ) {
	byte *buffer = NULL;
	int length = 0;
	qboolean wroteCache;

	if ( !shader ) {
		return qfalse;
	}

	if ( !Sys_Steam_RequestURL( url, &buffer, &length ) || !buffer || length <= 0 ) {
		return qfalse;
	}

	wroteCache = CL_SteamResources_WriteCacheFile( cachePath, buffer, length );
	Sys_Steam_FreeRequestBuffer( buffer );

	if ( !wroteCache ) {
		return qfalse;
	}

	*shader = re.RegisterShaderNoMip( cachePath );
	if ( *shader && !persist ) {
		CL_SteamResources_CleanupTransient( cachePath );
	}

	return ( *shader != 0 );
}

/*
=============
CL_Steam_RegisterShader

Resolves a Steam-backed resource into a renderer handle compatible with the menu image cache.
=============
*/
qhandle_t CL_Steam_RegisterShader( const char *url ) {
	clSteamResource_t *slot;
	char cachePath[MAX_QPATH];
	qhandle_t shader = 0;
	qboolean persist;

	if ( !CL_SteamResources_IsSteamURL( url ) ) {
		return re.RegisterShaderNoMip( url );
	}

	slot = CL_SteamResources_FindSlot( url );
	persist = ( cl_steamCachePersist && cl_steamCachePersist->integer );
	CL_SteamResources_SanitizeCacheName( url, cachePath, sizeof( cachePath ) );

	if ( slot && slot->shader ) {
		return slot->shader;
	}

	if ( CL_SteamResources_RegisterCachedShader( cachePath, &shader ) ) {
		CL_SteamResources_AssignSlot( slot, url, cachePath, shader, qtrue );
		return shader;
	}

	if ( CL_SteamResources_RequestAndCache( url, cachePath, persist, &shader ) ) {
		CL_SteamResources_AssignSlot( slot, url, cachePath, shader, persist );
		return shader;
	}

	Com_Printf( "UI: unable to satisfy Steam resource request for %s\n", url );
	return 0;
}


/*
=============
CL_InitSteamResources

Initialises the Steam resource bridge and related configuration.
=============
*/
void CL_InitSteamResources( void ) {
	Com_Memset( cl_steamResources, 0, sizeof( cl_steamResources ) );
	cl_steamCachePersist = Cvar_Get( "cl_steamCachePersist", "1", CVAR_ARCHIVE );
	cl_steamCachePath = Cvar_Get( "cl_steamCachePath", "steamcache", CVAR_ARCHIVE );
}

/*
=============
CL_ShutdownSteamResources

Clears any cached Steam resource bookkeeping.
=============
*/
void CL_ShutdownSteamResources( void ) {
	Com_Memset( cl_steamResources, 0, sizeof( cl_steamResources ) );
}

/*
=============
Sys_Steam_RequestURL

Stubbed Steam syscall to retrieve a URL payload.
=============
*/
qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {
	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( outSize ) {
		*outSize = 0;
	}

	Com_Printf( "Steam backend unavailable for %s\n", url ? url : "<null>" );
	return qfalse;
}

/*
=============
Sys_Steam_FreeRequestBuffer

Releases buffers allocated by Sys_Steam_RequestURL.
=============
*/
void Sys_Steam_FreeRequestBuffer( byte *buffer ) {
	if ( buffer ) {
		Z_Free( buffer );
	}
}

