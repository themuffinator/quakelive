#include "client.h"

#include <limits.h>
#include <stdlib.h>

#include "../../common/platform/platform_steamworks.h"

#define MAX_STEAM_RESOURCES 64
#define STEAM_URL_PREFIX "steam://"

typedef struct {
	char		url[MAX_QPATH];
	char		rendererName[MAX_QPATH];
	qhandle_t	shader;
} clSteamResource_t;

static clSteamResource_t cl_steamResources[MAX_STEAM_RESOURCES];
static unsigned int cl_steamResourceGeneration = 1;

qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize );
void Sys_Steam_FreeRequestBuffer( byte *buffer );

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
CL_SteamResources_IsURIResource

Returns qtrue when the provided resource uses a URI scheme and should route
through the launcher/Steam live-resource bridge instead of the normal shader
loader.
=============
*/
static qboolean CL_SteamResources_IsURIResource( const char *url ) {
	if ( !url ) {
		return qfalse;
	}

	return ( strstr( url, "://" ) != NULL ) ? qtrue : qfalse;
}

/*
=============
CL_SteamResources_IsAvatarURL

Returns qtrue when the provided Steam URL targets the avatar data source.
=============
*/
static qboolean CL_SteamResources_IsAvatarURL( const char *url ) {
	static const char *avatarPrefix = STEAM_URL_PREFIX "avatar/";

	if ( !url ) {
		return qfalse;
	}

	return ( Q_strnicmp( url, avatarPrefix, strlen( avatarPrefix ) ) == 0 );
}

/*
=============
CL_SteamResources_ParseAvatarSizeToken

Maps a Steam avatar size token to the matching Steamworks selector.
=============
*/
static qboolean CL_SteamResources_ParseAvatarSizeToken( const char *token, ql_steam_avatar_size_t *outSize ) {
	if ( !token || !token[0] || !outSize ) {
		return qfalse;
	}

	if ( !Q_stricmp( token, "small" ) ) {
		*outSize = QL_STEAM_AVATAR_SMALL;
		return qtrue;
	}

	if ( !Q_stricmp( token, "medium" ) ) {
		*outSize = QL_STEAM_AVATAR_MEDIUM;
		return qtrue;
	}

	if ( !Q_stricmp( token, "large" ) ) {
		*outSize = QL_STEAM_AVATAR_LARGE;
		return qtrue;
	}

	return qfalse;
}

/*
=============
CL_SteamResources_ParseAvatarURL

Extracts a SteamID and optional size token from a steam://avatar URL.
=============
*/
static qboolean CL_SteamResources_ParseAvatarURL( const char *url, ql_steam_avatar_size_t *outSize, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	static const char *avatarPrefix = STEAM_URL_PREFIX "avatar/";
	char token[MAX_QPATH];
	size_t prefixLength;
	const char *cursor;
	const char *slash;
	char *end;
	unsigned long long steamIdValue;

	if ( outSize ) {
		*outSize = QL_STEAM_AVATAR_LARGE;
	}
	if ( outIdLow ) {
		*outIdLow = 0;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0;
	}

	if ( !url || !outSize || !outIdLow || !outIdHigh ) {
		return qfalse;
	}

	prefixLength = strlen( avatarPrefix );
	if ( Q_strnicmp( url, avatarPrefix, prefixLength ) != 0 ) {
		return qfalse;
	}

	cursor = url + prefixLength;
	if ( !cursor[0] ) {
		return qfalse;
	}

	slash = strchr( cursor, '/' );
	if ( slash ) {
		size_t tokenLength = (size_t)( slash - cursor );

		if ( tokenLength == 0 || tokenLength >= sizeof( token ) ) {
			return qfalse;
		}

		memcpy( token, cursor, tokenLength );
		token[tokenLength] = '\0';
		if ( !CL_SteamResources_ParseAvatarSizeToken( token, outSize ) ) {
			return qfalse;
		}

		cursor = slash + 1;
	}

	if ( !cursor[0] ) {
		return qfalse;
	}

	steamIdValue = strtoull( cursor, &end, 10 );
	if ( end == cursor || *end != '\0' ) {
		return qfalse;
	}

	*outIdLow = (uint32_t)steamIdValue;
	*outIdHigh = (uint32_t)( steamIdValue >> 32 );
	return qtrue;
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

Stores the resolved shader and renderer-owned resource name for a Steam
resource.
=============
*/
static void CL_SteamResources_AssignSlot( clSteamResource_t *slot, const char *url, const char *rendererName, qhandle_t shader ) {
	if ( !slot ) {
		return;
	}

	Q_strncpyz( slot->url, url, sizeof( slot->url ) );
	Q_strncpyz( slot->rendererName, rendererName, sizeof( slot->rendererName ) );
	slot->shader = shader;
}

/*
=============
CL_SteamResources_BuildRendererName

Builds a short, renderer-owned name for one retained live resource slot. The
generation counter keeps reloads from silently reusing stale renderer images
after the client-side resource table is cleared.
=============
*/
static void CL_SteamResources_BuildRendererName( const char *url, const clSteamResource_t *slot, char *rendererName, size_t rendererNameSize ) {
	unsigned checksum;
	int slotIndex;

	if ( !rendererName || rendererNameSize == 0 || !url ) {
		return;
	}

	slotIndex = 0;
	if ( slot ) {
		slotIndex = (int)( slot - cl_steamResources );
	}

	checksum = Com_BlockChecksum( url, strlen( url ) );
	Com_sprintf( rendererName, rendererNameSize, "*steamres/%u/%02d/%08x", cl_steamResourceGeneration, slotIndex, checksum );
}

/*
=============
CL_SteamResources_ClearSlot

Drops one cached live-resource slot.
=============
*/
static void CL_SteamResources_ClearSlot( clSteamResource_t *slot, qboolean clearPersisted ) {
	(void)clearPersisted;

	if ( !slot ) {
		return;
	}

	Com_Memset( slot, 0, sizeof( *slot ) );
}

/*
=============
CL_SteamResources_RequestAvatarRGBA

Resolves a steam://avatar URL through the Steamworks avatar APIs and returns
the live RGBA payload directly for renderer-owned image creation.
=============
*/
static qboolean CL_SteamResources_RequestAvatarRGBA( const char *url, byte **outPixels, int *outWidth, int *outHeight ) {
	ql_steam_avatar_size_t size;
	uint32_t idLow;
	uint32_t idHigh;
	uint8_t *rgbaPixels;
	uint32_t width;
	uint32_t height;

	if ( outPixels ) {
		*outPixels = NULL;
	}
	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}

	if ( !CL_SteamResources_ParseAvatarURL( url, &size, &idLow, &idHigh ) ) {
		return qfalse;
	}

	rgbaPixels = NULL;
	width = 0;
	height = 0;
	if ( !QL_Steamworks_LoadAvatarRGBA( idLow, idHigh, size, &rgbaPixels, &width, &height ) || !rgbaPixels ) {
		return qfalse;
	}

	if ( width == 0 || height == 0 || width > INT_MAX || height > INT_MAX ) {
		QL_Steamworks_FreeBuffer( rgbaPixels );
		return qfalse;
	}

	if ( outPixels ) {
		*outPixels = rgbaPixels;
	}
	if ( outWidth ) {
		*outWidth = (int)width;
	}
	if ( outHeight ) {
		*outHeight = (int)height;
	}

	return qtrue;
}

/*
=============
CL_Steam_RegisterShader

Resolves a live Steam- or launcher-backed image resource into a renderer
handle compatible with the menu image cache.
=============
*/
qhandle_t CL_Steam_RegisterShader( const char *url ) {
	clSteamResource_t *slot;
	char rendererName[MAX_QPATH];
	byte *buffer;
	int bufferLength;
	byte *rgbaPixels;
	int width;
	int height;
	qhandle_t shader = 0;

	if ( !CL_SteamResources_IsURIResource( url ) ) {
		return re.RegisterShaderNoMip( url );
	}

	if ( CL_SteamResources_IsSteamURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			Com_DPrintf( "UI: Steam resource request stubbed for %s\n", url ? url : "<null>" );
			return 0;
		}
	}

	slot = CL_SteamResources_FindSlot( url );
	if ( !slot ) {
		Com_Printf( "UI: unable to allocate live resource slot for %s\n", url );
		return 0;
	}

	if ( slot->shader ) {
		return slot->shader;
	}

	CL_SteamResources_BuildRendererName( url, slot, rendererName, sizeof( rendererName ) );

	if ( CL_SteamResources_IsAvatarURL( url ) ) {
		rgbaPixels = NULL;
		width = 0;
		height = 0;

		if ( !CL_SteamResources_RequestAvatarRGBA( url, &rgbaPixels, &width, &height ) ) {
			Com_Printf( "UI: unable to satisfy in-memory avatar request for %s\n", url );
			return 0;
		}

		shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );
		QL_Steamworks_FreeBuffer( rgbaPixels );
	} else {
		buffer = NULL;
		bufferLength = 0;

		if ( !Sys_Steam_RequestURL( url, &buffer, &bufferLength ) || !buffer || bufferLength <= 0 ) {
			Com_Printf( "UI: unable to satisfy in-memory resource request for %s\n", url );
			return 0;
		}

		shader = CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );
		Sys_Steam_FreeRequestBuffer( buffer );
	}

	if ( !shader ) {
		Com_Printf( "UI: unable to register live resource image for %s\n", url );
		return 0;
	}

	CL_SteamResources_AssignSlot( slot, url, rendererName, shader );
	return shader;
}


/*
=============
CL_ClearSteamResourceCache

Clears the retained live-resource bookkeeping and forces future registrations
onto fresh renderer-owned names.
=============
*/
void CL_ClearSteamResourceCache( qboolean clearPersisted ) {
	int i;

	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		CL_SteamResources_ClearSlot( &cl_steamResources[i], clearPersisted );
	}

	cl_steamResourceGeneration++;
	if ( cl_steamResourceGeneration == 0 ) {
		cl_steamResourceGeneration = 1;
	}
}

/*
=============
CL_InitSteamResources

Initialises the Steam resource bridge and related configuration.
=============
*/
void CL_InitSteamResources( void ) {
	Com_Memset( cl_steamResources, 0, sizeof( cl_steamResources ) );
	cl_steamResourceGeneration = 1;

	if ( !CL_SteamServicesEnabled() ) {
		Com_Printf( "Steam resource bridge disabled by build/runtime policy\n" );
	}
}

/*
=============
CL_ShutdownSteamResources

Clears any retained Steam resource bookkeeping.
=============
*/
void CL_ShutdownSteamResources( void ) {
	CL_ClearSteamResourceCache( qfalse );
}

/*
=============
Sys_Steam_RequestURL

Retrieves an encoded Steam-backed or launcher-backed URL payload for the live
renderer image bridge.
=============
*/
qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {
	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( outSize ) {
		*outSize = 0;
	}

	if ( CL_LauncherRequestData( url, (void **)outBuffer, outSize ) ) {
		return qtrue;
	}

	if ( CL_SteamResources_IsSteamURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			Com_Printf( "Steam backend disabled by build/runtime policy for %s\n", url ? url : "<null>" );
		} else {
			Com_Printf( "Steam backend unavailable for %s\n", url ? url : "<null>" );
		}
	} else {
		Com_Printf( "Launcher resource backend unavailable for %s\n", url ? url : "<null>" );
	}

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

