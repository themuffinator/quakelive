#include "client.h"

#include <limits.h>
#include <stdlib.h>

#include "../../common/platform/platform_services.h"
#include "../../common/platform/platform_steamworks.h"

#define MAX_STEAM_RESOURCES 64
#define STEAM_URL_PREFIX "steam://"

typedef struct {
	char		url[MAX_QPATH];
	char		rendererName[MAX_QPATH];
	qhandle_t	shader;
} clSteamResource_t;

typedef struct {
	byte		*buffer;
	int			bufferLength;
	byte		*rgbaPixels;
	int			width;
	int			height;
	char		mimeType[64];
	qboolean	fromSteamDataSource;
} clSteamDataSourceResponse_t;

static clSteamResource_t cl_steamResources[MAX_STEAM_RESOURCES];
static unsigned int cl_steamResourceGeneration = 1;

qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize );
void Sys_Steam_FreeRequestBuffer( byte *buffer );

/*
=============
CL_GetSteamResourceServiceDescriptor

Returns the retained platform-service descriptor that owns the browser/live
resource bridge compatibility boundary.
=============
*/
static const ql_platform_feature_descriptor *CL_GetSteamResourceServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->overlay;
}

/*
=============
CL_GetSteamResourceServiceProviderLabel

Returns the human-readable provider label for the browser/live resource bridge.
=============
*/
static const char *CL_GetSteamResourceServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetSteamResourceServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetSteamResourceServicePolicyLabel

Returns the short compatibility policy label for the browser/live resource
bridge.
=============
*/
static const char *CL_GetSteamResourceServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetSteamResourceServiceDescriptor() );
}

/*
=============
CL_LogSteamResourceBridgeUnavailable

Publishes provider-aware diagnostics whenever the retained Steam resource
bridge cannot satisfy a request.
=============
*/
static void CL_LogSteamResourceBridgeUnavailable( const char *url, const char *reason ) {
	Com_Printf( "Steam resource bridge unavailable for %s via %s [%s]; %s\n",
		url ? url : "<null>",
		CL_GetSteamResourceServiceProviderLabel(),
		CL_GetSteamResourceServicePolicyLabel(),
		reason ? reason : "request could not be satisfied" );
}

/*
=============
CL_LogLauncherResourceFallbackUnavailable

Publishes provider-aware diagnostics when the retained launcher/web fallback
owner cannot satisfy a live resource request.
=============
*/
static void CL_LogLauncherResourceFallbackUnavailable( const char *url, const char *reason ) {
	Com_Printf( "Launcher/web fallback unavailable for %s via %s [%s]; %s\n",
		url ? url : "<null>",
		CL_GetSteamResourceServiceProviderLabel(),
		CL_GetSteamResourceServicePolicyLabel(),
		reason ? reason : "no launcher/web resource owner is available" );
}

/*
=============
CL_LogSteamResourceRequestStubbed

Publishes provider-aware diagnostics when the UI-side Steam resource request is
stubbed by the current compatibility policy.
=============
*/
static void CL_LogSteamResourceRequestStubbed( const char *url ) {
	Com_DPrintf( "UI: Steam resource request stubbed for %s via %s [%s]\n",
		url ? url : "<null>",
		CL_GetSteamResourceServiceProviderLabel(),
		CL_GetSteamResourceServicePolicyLabel() );
}

/*
=============
CL_RefreshSteamResourceBridgeCvars

Mirrors the retained live-resource bridge provider/policy labels through ROM
cvars for diagnostics and bounded compatibility reporting.
=============
*/
static void CL_RefreshSteamResourceBridgeCvars( void ) {
	Cvar_Set( "ui_resourceBridgeProvider", CL_GetSteamResourceServiceProviderLabel() );
	Cvar_Set( "ui_resourceBridgePolicy", CL_GetSteamResourceServicePolicyLabel() );
}

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
CL_SteamDataSource_ClearResponse
=============
*/
static void CL_SteamDataSource_ClearResponse( clSteamDataSourceResponse_t *response ) {
	if ( !response ) {
		return;
	}

	Com_Memset( response, 0, sizeof( *response ) );
}

/*
=============
CL_SteamDataSource_GuessMimeType
=============
*/
static const char *CL_SteamDataSource_GuessMimeType( const char *url ) {
	const char *extension;

	if ( !url ) {
		return "application/octet-stream";
	}

	extension = strrchr( url, '.' );
	if ( !extension ) {
		return "application/octet-stream";
	}

	if ( !Q_stricmp( extension, ".jpg" ) || !Q_stricmp( extension, ".jpeg" ) ) {
		return "image/jpeg";
	}

	if ( !Q_stricmp( extension, ".png" ) ) {
		return "image/png";
	}

	if ( !Q_stricmp( extension, ".gif" ) ) {
		return "image/gif";
	}

	if ( !Q_stricmp( extension, ".html" ) || !Q_stricmp( extension, ".htm" ) ) {
		return "text/html";
	}

	if ( !Q_stricmp( extension, ".js" ) ) {
		return "application/javascript";
	}

	if ( !Q_stricmp( extension, ".css" ) ) {
		return "text/css";
	}

	if ( !Q_stricmp( extension, ".json" ) ) {
		return "application/json";
	}

	return "application/octet-stream";
}

/*
=============
CL_SteamDataSource_Request

Reconstructs the retail SteamDataSource owner by servicing `steam://` resource
requests through the retained avatar/image bridge and launcher-compatible URL
loader surface.
=============
*/
static qboolean CL_SteamDataSource_Request( const char *url, clSteamDataSourceResponse_t *response ) {
	if ( !url || !response || !CL_SteamResources_IsSteamURL( url ) ) {
		return qfalse;
	}

	CL_SteamDataSource_ClearResponse( response );
	response->fromSteamDataSource = qtrue;

	if ( CL_SteamResources_IsAvatarURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			CL_LogSteamResourceBridgeUnavailable( url, "keeping launcher/web fallback resource bridge" );
			return qfalse;
		}

		if ( !CL_SteamResources_RequestAvatarRGBA( url, &response->rgbaPixels, &response->width, &response->height ) ) {
			CL_LogSteamResourceBridgeUnavailable( url, "avatar request could not be satisfied" );
			return qfalse;
		}

		Q_strncpyz( response->mimeType, "image/rgba", sizeof( response->mimeType ) );
		return qtrue;
	}

	if ( !CL_SteamServicesEnabled() ) {
		CL_LogSteamResourceBridgeUnavailable( url, "keeping launcher/web fallback resource bridge" );
		return qfalse;
	}

	CL_LogSteamResourceBridgeUnavailable( url, "no live SteamDataSource owner is available" );
	return qfalse;
}

/*
=============
QLResourceInterceptor_OnRequest

Reconstructs the retained browser-resource interceptor by routing `steam://`
requests through SteamDataSource and every other URI through the launcher/web
filesystem fallback owner.
=============
*/
static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {
	if ( !url || !response ) {
		return qfalse;
	}

	if ( CL_SteamDataSource_Request( url, response ) ) {
		return qtrue;
	}

	CL_SteamDataSource_ClearResponse( response );
	if ( CL_LauncherRequestData( url, (void **)&response->buffer, &response->bufferLength ) ) {
		Q_strncpyz( response->mimeType, CL_SteamDataSource_GuessMimeType( url ), sizeof( response->mimeType ) );
		return qtrue;
	}

	CL_LogLauncherResourceFallbackUnavailable( url, "no launcher/web resource owner is available" );
	return qfalse;
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
			CL_LogSteamResourceRequestStubbed( url );
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
		if ( !CL_SteamResources_RequestAvatarRGBA( url, &rgbaPixels, &width, &height ) ) {
			Com_Printf( "UI: unable to satisfy avatar resource request for %s via %s [%s]\n",
				url,
				CL_GetSteamResourceServiceProviderLabel(),
				CL_GetSteamResourceServicePolicyLabel() );
			return 0;
		}

		shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );
		QL_Steamworks_FreeBuffer( rgbaPixels );
	} else {
		clSteamDataSourceResponse_t response;

		CL_SteamDataSource_ClearResponse( &response );
		if ( !QLResourceInterceptor_OnRequest( url, &response ) ) {
			Com_Printf( "UI: unable to satisfy in-memory resource request for %s via %s [%s]\n",
				url,
				CL_GetSteamResourceServiceProviderLabel(),
				CL_GetSteamResourceServicePolicyLabel() );
			return 0;
		}

		rgbaPixels = response.rgbaPixels;
		width = response.width;
		height = response.height;
		buffer = response.buffer;
		bufferLength = response.bufferLength;

		if ( buffer && bufferLength > 0 ) {
			shader = CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );
			Sys_Steam_FreeRequestBuffer( buffer );
		} else if ( rgbaPixels ) {
			shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );
			QL_Steamworks_FreeBuffer( rgbaPixels );
		} else {
			return 0;
		}
	}

	if ( !shader ) {
		Com_Printf( "UI: unable to register live resource image for %s via %s [%s]\n",
			url,
			CL_GetSteamResourceServiceProviderLabel(),
			CL_GetSteamResourceServicePolicyLabel() );
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
	CL_RefreshSteamResourceBridgeCvars();

	if ( !CL_SteamServicesEnabled() ) {
		Com_Printf( "Steam resource bridge disabled for %s [%s]; keeping launcher/web fallback resource bridge.\n",
			CL_GetSteamResourceServiceProviderLabel(),
			CL_GetSteamResourceServicePolicyLabel() );
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
	clSteamDataSourceResponse_t response;

	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( outSize ) {
		*outSize = 0;
	}

	CL_SteamDataSource_ClearResponse( &response );
	if ( !QLResourceInterceptor_OnRequest( url, &response ) ) {
		CL_LogLauncherResourceFallbackUnavailable( url, "request could not be resolved" );
		return qfalse;
	}

	if ( !response.buffer || response.bufferLength <= 0 ) {
		if ( response.rgbaPixels ) {
			QL_Steamworks_FreeBuffer( response.rgbaPixels );
		}
		CL_LogLauncherResourceFallbackUnavailable( url, "no binary buffer was produced" );
		return qfalse;
	}

	if ( outBuffer ) {
		*outBuffer = response.buffer;
	}
	if ( outSize ) {
		*outSize = response.bufferLength;
	}

	return qtrue;
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

