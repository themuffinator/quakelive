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

	if ( strstr( virtualPath, ".." ) || strstr( virtualPath, "::" ) || strchr( virtualPath, ':' ) ) {
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
CL_WebRequestReadMappedFile

Reads a launcher request through the retail-style fs_webpath / screenshots
fallback mappings owned by the engine filesystem.
=============
*/
static qboolean CL_WebRequestReadMappedFile( const char *request, void **outBuffer, int *outLength ) {
	fileHandle_t	file;
	char		resolvedPath[MAX_QPATH];
	int		length;
	byte		*buffer;

	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( outLength ) {
		*outLength = 0;
	}

	if ( !request || !outBuffer ) {
		return qfalse;
	}

	if ( !FS_FOpenWebFileRead( request, &file, resolvedPath, sizeof( resolvedPath ) ) ) {
		return qfalse;
	}

	length = FS_filelength( file );
	if ( length < 0 ) {
		FS_FCloseFile( file );
		return qfalse;
	}

	buffer = Z_Malloc( length + 1 );
	if ( !buffer ) {
		FS_FCloseFile( file );
		return qfalse;
	}

	if ( length > 0 && FS_Read( buffer, length, file ) != length ) {
		Z_Free( buffer );
		FS_FCloseFile( file );
		return qfalse;
	}

	buffer[length] = 0;
	FS_FCloseFile( file );

	*outBuffer = buffer;
	if ( outLength ) {
		*outLength = length;
	}

	return qtrue;
}

/*
=============
CL_WebPak_Init

Mount web.pak from fs_homepath for launcher and menu assets. Local launcher
fallback assets remain valid even when live online services are disabled.
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

Resolve launcher/UI requests using web.pak first, then the retail-style mapped
filesystem interceptor path, and finally the regular filesystem search order.
The returned buffer should be freed with Z_Free.
=============
*/
qboolean CL_WebRequestResolve( const char *virtualPath, void **outBuffer, int *outLength ) {
	char			normalized[MAX_QPATH];
	qboolean		normalizedValid;
	void			*fsBuffer;
	int			length;

	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	normalizedValid = CL_WebPak_NormalizePath( virtualPath, normalized, sizeof( normalized ) );

	if ( normalizedValid && CL_WebPak_ReadInternal( normalized, outBuffer, outLength ) ) {
		return qtrue;
	}

	if ( CL_WebRequestReadMappedFile( virtualPath, outBuffer, outLength ) ) {
		return qtrue;
	}

	if ( !normalizedValid ) {
		return qfalse;
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

Bridges launcher/UI requests through web.pak before falling back to the
retail-style mapped filesystem interceptor path.
=============
*/
qboolean CL_LauncherRequestData( const char *virtualPath, void **outBuffer, int *outLength ) {
	return CL_WebRequestResolve( virtualPath, outBuffer, outLength );
}
