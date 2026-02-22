#include "client.h"

static pack_t *cl_webPak = NULL;

/*
=============
CL_WebPak_NormalizePath

Normalise virtual paths for web.pak lookups.
=============
*/
static qboolean CL_WebPak_NormalizePath( const char *virtualPath, char *normalized, size_t normalizedSize ) {
	if ( !virtualPath || !virtualPath[0] || !normalized || normalizedSize < 1 ) {
		return qfalse;
	}

	while ( virtualPath[0] == '/' || virtualPath[0] == '\\' ) {
		virtualPath++;
	}

	if ( strstr( virtualPath, ".." ) || strstr( virtualPath, "::" ) ) {
		return qfalse;
	}

	Q_strncpyz( normalized, virtualPath, normalizedSize );
	Q_strlwr( normalized );
	return qtrue;
}

/*
=============
CL_WebPak_ReadInternal

Read a normalised path out of web.pak if the archive is mounted.
=============
*/
static qboolean CL_WebPak_ReadInternal( const char *normalizedPath, void **outBuffer, int *outLength ) {
	int			length;

	if ( !cl_webPak || !normalizedPath || !outBuffer ) {
		return qfalse;
	}

	length = FS_ReadFileFromPak( cl_webPak, normalizedPath, outBuffer );
	if ( length < 0 ) {
		return qfalse;
	}

	if ( outLength ) {
		*outLength = length;
	}
	return qtrue;
}

/*
=============
CL_WebPak_Init

Mount web.pak from fs_homepath for launcher and menu assets.
=============
*/
void CL_WebPak_Init( void ) {
	char			homePath[MAX_OSPATH];
	char			basePath[MAX_OSPATH];
	char			pakPath[MAX_OSPATH];
	char			*osPath;
	FILE			*fp;
	unsigned char		header[4];

	if ( cl_webPak ) {
		FS_FreePak( cl_webPak );
		cl_webPak = NULL;
	}

	Cvar_VariableStringBuffer( "fs_homepath", homePath, sizeof( homePath ) );
	osPath = FS_BuildOSPath( homePath, "", "web.pak" );
	Q_strncpyz( pakPath, osPath, sizeof( pakPath ) );

	cl_webPak = FS_LoadPackExplicit( pakPath );
	if ( cl_webPak ) {
		Com_Printf( "web.pak mounted from %s\n", pakPath );
		return;
	}

	// Retail Quake Live ships web.pak alongside the main executable under fs_basepath.
	Cvar_VariableStringBuffer( "fs_basepath", basePath, sizeof( basePath ) );
	osPath = FS_BuildOSPath( basePath, "", "web.pak" );
	Q_strncpyz( pakPath, osPath, sizeof( pakPath ) );

	cl_webPak = FS_LoadPackExplicit( pakPath );
	if ( cl_webPak ) {
		Com_Printf( "web.pak mounted from %s\n", pakPath );
		return;
	}

	// Help debug incorrect assumptions: web.pak is not always a pk3/zip container.
	fp = fopen( pakPath, "rb" );
	if ( fp ) {
		Com_Memset( header, 0, sizeof( header ) );
		fread( header, 1, sizeof( header ), fp );
		fclose( fp );

		if ( header[0] != 'P' || header[1] != 'K' ) {
			Com_DPrintf( "web.pak present at %s but is not a pk3/zip (header %02x %02x %02x %02x)\n",
				pakPath, header[0], header[1], header[2], header[3] );
		}
	}
}

/*
=============
CL_WebPak_Shutdown

Release the cached web.pak handle.
=============
*/
void CL_WebPak_Shutdown( void ) {
	if ( cl_webPak ) {
		FS_FreePak( cl_webPak );
		cl_webPak = NULL;
	}
}

/*
=============
CL_WebPak_Available
=============
*/
qboolean CL_WebPak_Available( void ) {
	return ( cl_webPak != NULL );
}

/*
=============
CL_WebPak_Fetch

Read a virtual path from web.pak if present. The returned buffer should be
freed with Z_Free.
=============
*/
qboolean CL_WebPak_Fetch( const char *virtualPath, void **outBuffer, int *outLength ) {
	char			normalized[MAX_QPATH];

	if ( !CL_WebPak_NormalizePath( virtualPath, normalized, sizeof( normalized ) ) ) {
		return qfalse;
	}

	return CL_WebPak_ReadInternal( normalized, outBuffer, outLength );
}

/*
=============
CL_WebRequestResolve

Resolve launcher/UI requests using web.pak first and fall back to the
regular filesystem search order. The returned buffer should be freed with
Z_Free.
=============
*/
qboolean CL_WebRequestResolve( const char *virtualPath, void **outBuffer, int *outLength ) {
	char			normalized[MAX_QPATH];
	void			*fsBuffer;
	int			length;

	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( !CL_WebPak_NormalizePath( virtualPath, normalized, sizeof( normalized ) ) ) {
		return qfalse;
	}

	if ( CL_WebPak_ReadInternal( normalized, outBuffer, outLength ) ) {
		return qtrue;
	}

	length = FS_ReadFile( normalized, &fsBuffer );
	if ( length < 0 ) {
		return qfalse;
	}

	*outBuffer = Z_Malloc( length + 1 );
	if ( fsBuffer && length > 0 ) {
		Com_Memcpy( *outBuffer, fsBuffer, length );
	}
	((byte *)*outBuffer)[length] = 0;

	FS_FreeFile( fsBuffer );

	if ( outLength ) {
		*outLength = length;
	}

	return qtrue;
}

/*
=============
CL_LauncherRequestData

Bridge HTTP/UI requests through web.pak before falling back to other sources.
=============
*/
qboolean CL_LauncherRequestData( const char *virtualPath, void **outBuffer, int *outLength ) {
	return CL_WebRequestResolve( virtualPath, outBuffer, outLength );
}
