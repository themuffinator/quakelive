#include <limits.h>
#include <stdint.h>
#include <stdlib.h>

#include "client.h"

static pack_t *cl_webPak = NULL;

#define CL_WEB_FILE_LIST_BUFFER 4096

typedef struct {
	uint16_t	resourceId;
	char		path[MAX_QPATH];
} clWebDataPakPath_t;

typedef struct {
	qboolean			loaded;
	uint32_t			version;
	uint32_t			resourceCount;
	uint16_t			aliasCount;
	int				headerLength;
	byte				*buffer;
	int				bufferLength;
	clWebDataPakPath_t	*paths;
	int				pathCount;
} clWebDataPak_t;

static clWebDataPak_t cl_webDataPak;

/*
=============
CL_WebPak_BuildStandalonePath

Builds an OS path rooted directly under the supplied directory without
injecting fs_gamedir. Retail web.pak sits beside the executable.
=============
*/
static void CL_WebPak_BuildStandalonePath( const char *rootPath, const char *filename, char *outPath, size_t outPathSize ) {
	size_t rootLength;

	if ( !outPath || outPathSize == 0 ) {
		return;
	}

	outPath[0] = '\0';
	if ( !rootPath || !rootPath[0] || !filename || !filename[0] ) {
		return;
	}

	rootLength = strlen( rootPath );
	if ( rootPath[rootLength - 1] == '/' || rootPath[rootLength - 1] == '\\' ) {
		Com_sprintf( outPath, outPathSize, "%s%s", rootPath, filename );
	} else {
		Com_sprintf( outPath, outPathSize, "%s%c%s", rootPath, PATH_SEP, filename );
	}
}

/*
=============
CL_WebDataPak_ReadUInt16
=============
*/
static uint16_t CL_WebDataPak_ReadUInt16( const byte *cursor ) {
	return (uint16_t)( cursor[0] | ( cursor[1] << 8 ) );
}

/*
=============
CL_WebDataPak_ReadUInt32
=============
*/
static uint32_t CL_WebDataPak_ReadUInt32( const byte *cursor ) {
	return (uint32_t)(
		cursor[0]
		| ( cursor[1] << 8 )
		| ( cursor[2] << 16 )
		| ( cursor[3] << 24 )
	);
}

/*
=============
CL_WebDataPak_Clear
=============
*/
static void CL_WebDataPak_Clear( clWebDataPak_t *dataPak ) {
	if ( !dataPak ) {
		return;
	}

	if ( dataPak->paths ) {
		Z_Free( dataPak->paths );
	}

	if ( dataPak->buffer ) {
		free( dataPak->buffer );
	}

	Com_Memset( dataPak, 0, sizeof( *dataPak ) );
}

/*
=============
CL_WebDataPak_EntryPointer
=============
*/
static const byte *CL_WebDataPak_EntryPointer( const clWebDataPak_t *dataPak, int entryIndex ) {
	if ( !dataPak || !dataPak->buffer || entryIndex < 0 || entryIndex > (int)dataPak->resourceCount ) {
		return NULL;
	}

	return dataPak->buffer + dataPak->headerLength + ( entryIndex * 6 );
}

/*
=============
CL_WebDataPak_AliasPointer
=============
*/
static const byte *CL_WebDataPak_AliasPointer( const clWebDataPak_t *dataPak, int aliasIndex ) {
	int aliasOffset;

	if ( !dataPak || !dataPak->buffer || aliasIndex < 0 || aliasIndex >= (int)dataPak->aliasCount ) {
		return NULL;
	}

	aliasOffset = dataPak->headerLength + ( (int)dataPak->resourceCount + 1 ) * 6;
	return dataPak->buffer + aliasOffset + ( aliasIndex * 4 );
}

/*
=============
CL_WebDataPak_FindEntryIndex
=============
*/
static int CL_WebDataPak_FindEntryIndex( const clWebDataPak_t *dataPak, uint16_t resourceId ) {
	int low;
	int high;

	if ( !dataPak || !dataPak->buffer || dataPak->resourceCount == 0 ) {
		return -1;
	}

	low = 0;
	high = (int)dataPak->resourceCount - 1;
	while ( low <= high ) {
		int mid;
		const byte *entry;
		uint16_t currentId;

		mid = low + ( high - low ) / 2;
		entry = CL_WebDataPak_EntryPointer( dataPak, mid );
		currentId = CL_WebDataPak_ReadUInt16( entry );

		if ( currentId == resourceId ) {
			return mid;
		}

		if ( currentId < resourceId ) {
			low = mid + 1;
		} else {
			high = mid - 1;
		}
	}

	low = 0;
	high = (int)dataPak->aliasCount - 1;
	while ( low <= high ) {
		int mid;
		const byte *alias;
		uint16_t currentId;

		mid = low + ( high - low ) / 2;
		alias = CL_WebDataPak_AliasPointer( dataPak, mid );
		currentId = CL_WebDataPak_ReadUInt16( alias );

		if ( currentId == resourceId ) {
			return (int)CL_WebDataPak_ReadUInt16( alias + 2 );
		}

		if ( currentId < resourceId ) {
			low = mid + 1;
		} else {
			high = mid - 1;
		}
	}

	return -1;
}

/*
=============
CL_WebDataPak_GetResourceView
=============
*/
static qboolean CL_WebDataPak_GetResourceView( const clWebDataPak_t *dataPak, uint16_t resourceId, const byte **outData, int *outLength ) {
	int entryIndex;
	const byte *entry;
	const byte *nextEntry;
	uint32_t startOffset;
	uint32_t endOffset;

	if ( outData ) {
		*outData = NULL;
	}

	if ( outLength ) {
		*outLength = 0;
	}

	if ( !dataPak || !dataPak->buffer || dataPak->resourceCount == 0 ) {
		return qfalse;
	}

	entryIndex = CL_WebDataPak_FindEntryIndex( dataPak, resourceId );
	if ( entryIndex < 0 ) {
		return qfalse;
	}

	entry = CL_WebDataPak_EntryPointer( dataPak, entryIndex );
	nextEntry = CL_WebDataPak_EntryPointer( dataPak, entryIndex + 1 );
	startOffset = CL_WebDataPak_ReadUInt32( entry + 2 );
	endOffset = CL_WebDataPak_ReadUInt32( nextEntry + 2 );

	if ( endOffset < startOffset || endOffset > (uint32_t)dataPak->bufferLength ) {
		return qfalse;
	}

	if ( outData ) {
		*outData = dataPak->buffer + startOffset;
	}

	if ( outLength ) {
		*outLength = (int)( endOffset - startOffset );
	}

	return qtrue;
}

/*
=============
CL_WebDataPak_ReadResource
=============
*/
static qboolean CL_WebDataPak_ReadResource( const clWebDataPak_t *dataPak, uint16_t resourceId, void **outBuffer, int *outLength ) {
	const byte	*view;
	int			length;
	byte		*copy;

	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( outLength ) {
		*outLength = 0;
	}

	if ( !outBuffer || !CL_WebDataPak_GetResourceView( dataPak, resourceId, &view, &length ) ) {
		return qfalse;
	}

	copy = Z_Malloc( length + 1 );
	if ( !copy ) {
		return qfalse;
	}

	if ( length > 0 ) {
		Com_Memcpy( copy, view, length );
	}
	copy[length] = 0;

	*outBuffer = copy;
	if ( outLength ) {
		*outLength = length;
	}

	return qtrue;
}

/*
=============
CL_WebDataPak_DecodePath
=============
*/
static qboolean CL_WebDataPak_DecodePath( const byte *utf16Data, uint32_t charCount, char *outPath, size_t outPathSize ) {
	uint32_t i;

	if ( !utf16Data || !outPath || outPathSize == 0 || charCount == 0 || charCount >= outPathSize ) {
		return qfalse;
	}

	for ( i = 0; i < charCount; i++ ) {
		byte low;
		byte high;

		low = utf16Data[i * 2];
		high = utf16Data[i * 2 + 1];
		if ( high != 0 ) {
			return qfalse;
		}

		outPath[i] = ( low == '\\' ) ? '/' : (char)low;
	}
	outPath[charCount] = '\0';

	if ( strstr( outPath, ".." ) || strstr( outPath, "::" ) || strchr( outPath, ':' ) ) {
		return qfalse;
	}

	Q_strlwr( outPath );
	return qtrue;
}

/*
=============
CL_WebDataPak_BuildPathTable
=============
*/
static qboolean CL_WebDataPak_BuildPathTable( clWebDataPak_t *dataPak ) {
	const byte	*manifestData;
	uint32_t	trailerResourceId;
	int			manifestLength;
	int			cursor;
	char		pendingPath[MAX_QPATH];
	qboolean	havePending;

	if ( !dataPak ) {
		return qfalse;
	}

	if ( !CL_WebDataPak_GetResourceView( dataPak, 0, &manifestData, &manifestLength ) ) {
		return qfalse;
	}

	if ( manifestLength < 16 ) {
		return qfalse;
	}

	if ( CL_WebDataPak_ReadUInt32( manifestData ) + 4u > (uint32_t)manifestLength ) {
		return qfalse;
	}

	trailerResourceId = CL_WebDataPak_ReadUInt32( manifestData + manifestLength - 4 );
	dataPak->paths = Z_Malloc( sizeof( *dataPak->paths ) * ( dataPak->resourceCount - 1 ) );
	if ( !dataPak->paths ) {
		return qfalse;
	}

	dataPak->pathCount = 0;
	cursor = 8;
	havePending = qfalse;
	pendingPath[0] = '\0';

	while ( cursor + 12 <= manifestLength - 8 ) {
		uint32_t nextResourceId;
		uint32_t pathLength;
		char decodedPath[MAX_QPATH];

		(void)CL_WebDataPak_ReadUInt32( manifestData + cursor );
		cursor += 4;
		nextResourceId = CL_WebDataPak_ReadUInt32( manifestData + cursor );
		cursor += 4;
		pathLength = CL_WebDataPak_ReadUInt32( manifestData + cursor );
		cursor += 4;

		if ( pathLength == 0 || cursor + (int)( pathLength * 2 ) > manifestLength - 8 ) {
			return qfalse;
		}

		if ( !CL_WebDataPak_DecodePath( manifestData + cursor, pathLength, decodedPath, sizeof( decodedPath ) ) ) {
			return qfalse;
		}
		cursor += (int)( pathLength * 2 );
		cursor = ( cursor + 3 ) & ~3;

		if ( havePending ) {
			dataPak->paths[dataPak->pathCount].resourceId = (uint16_t)nextResourceId;
			Q_strncpyz( dataPak->paths[dataPak->pathCount].path, pendingPath, sizeof( dataPak->paths[dataPak->pathCount].path ) );
			dataPak->pathCount++;
		}

		Q_strncpyz( pendingPath, decodedPath, sizeof( pendingPath ) );
		havePending = qtrue;
	}

	if ( havePending ) {
		dataPak->paths[dataPak->pathCount].resourceId = (uint16_t)trailerResourceId;
		Q_strncpyz( dataPak->paths[dataPak->pathCount].path, pendingPath, sizeof( dataPak->paths[dataPak->pathCount].path ) );
		dataPak->pathCount++;
	}

	return dataPak->pathCount > 0;
}

/*
=============
CL_WebDataPak_LoadFile
=============
*/
static qboolean CL_WebDataPak_LoadFile( const char *pakPath, clWebDataPak_t *outDataPak ) {
	clWebDataPak_t	dataPak;
	FILE			*fp;
	long			fileLength;
	uint32_t		version;
	int			tableLength;
	int			aliasLength;
	int			i;

	if ( !pakPath || !pakPath[0] || !outDataPak ) {
		return qfalse;
	}

	Com_Memset( &dataPak, 0, sizeof( dataPak ) );

	fp = fopen( pakPath, "rb" );
	if ( !fp ) {
		return qfalse;
	}

	fseek( fp, 0, SEEK_END );
	fileLength = ftell( fp );
	fseek( fp, 0, SEEK_SET );
	if ( fileLength <= 0 || fileLength > INT_MAX ) {
		fclose( fp );
		return qfalse;
	}

	dataPak.buffer = malloc( (size_t)fileLength );
	if ( !dataPak.buffer ) {
		fclose( fp );
		return qfalse;
	}

	if ( fread( dataPak.buffer, 1, (size_t)fileLength, fp ) != (size_t)fileLength ) {
		fclose( fp );
		CL_WebDataPak_Clear( &dataPak );
		return qfalse;
	}
	fclose( fp );

	dataPak.bufferLength = (int)fileLength;
	version = CL_WebDataPak_ReadUInt32( dataPak.buffer );
	if ( version == 4u ) {
		dataPak.version = version;
		dataPak.resourceCount = CL_WebDataPak_ReadUInt32( dataPak.buffer + 4 );
		dataPak.aliasCount = 0;
		dataPak.headerLength = 9;
	} else if ( version == 5u ) {
		dataPak.version = version;
		dataPak.resourceCount = CL_WebDataPak_ReadUInt16( dataPak.buffer + 8 );
		dataPak.aliasCount = CL_WebDataPak_ReadUInt16( dataPak.buffer + 10 );
		dataPak.headerLength = 12;
	} else {
		CL_WebDataPak_Clear( &dataPak );
		return qfalse;
	}

	tableLength = ( (int)dataPak.resourceCount + 1 ) * 6;
	aliasLength = (int)dataPak.aliasCount * 4;
	if ( dataPak.headerLength + tableLength + aliasLength > dataPak.bufferLength ) {
		CL_WebDataPak_Clear( &dataPak );
		return qfalse;
	}

	for ( i = 0; i <= (int)dataPak.resourceCount; i++ ) {
		const byte *entry;
		uint32_t offset;

		entry = CL_WebDataPak_EntryPointer( &dataPak, i );
		offset = CL_WebDataPak_ReadUInt32( entry + 2 );
		if ( offset > (uint32_t)dataPak.bufferLength ) {
			CL_WebDataPak_Clear( &dataPak );
			return qfalse;
		}

		if ( i > 0 ) {
			const byte *prevEntry;
			uint32_t previousOffset;

			prevEntry = CL_WebDataPak_EntryPointer( &dataPak, i - 1 );
			previousOffset = CL_WebDataPak_ReadUInt32( prevEntry + 2 );
			if ( offset < previousOffset ) {
				CL_WebDataPak_Clear( &dataPak );
				return qfalse;
			}
		}
	}

	if ( !CL_WebDataPak_BuildPathTable( &dataPak ) ) {
		CL_WebDataPak_Clear( &dataPak );
		return qfalse;
	}

	dataPak.loaded = qtrue;
	*outDataPak = dataPak;
	return qtrue;
}

/*
=============
CL_WebDataPak_Load
=============
*/
static qboolean CL_WebDataPak_Load( const char *pakPath ) {
	clWebDataPak_t dataPak;

	if ( !CL_WebDataPak_LoadFile( pakPath, &dataPak ) ) {
		return qfalse;
	}

	CL_WebDataPak_Clear( &cl_webDataPak );
	cl_webDataPak = dataPak;
	return qtrue;
}

/*
=============
CL_WebDataPak_Fetch
=============
*/
static qboolean CL_WebDataPak_Fetch( const char *normalizedPath, void **outBuffer, int *outLength ) {
	int i;

	if ( !cl_webDataPak.loaded || !normalizedPath || !normalizedPath[0] ) {
		return qfalse;
	}

	for ( i = 0; i < cl_webDataPak.pathCount; i++ ) {
		if ( !Q_stricmp( cl_webDataPak.paths[i].path, normalizedPath ) ) {
			return CL_WebDataPak_ReadResource( &cl_webDataPak, cl_webDataPak.paths[i].resourceId, outBuffer, outLength );
		}
	}

	return qfalse;
}

/*
=============
CL_WebPak_StripProtocol

Reduces launcher-style URIs to the local request path used by retained
web.pak and filesystem fallbacks.
=============
*/
static const char *CL_WebPak_StripProtocol( const char *virtualPath ) {
	const char	*pathStart;
	const char	*separator;

	if ( !virtualPath ) {
		return NULL;
	}

	pathStart = virtualPath;
	separator = strstr( virtualPath, "://" );
	if ( separator ) {
		pathStart = separator + 3;
		separator = strchr( pathStart, '/' );
		if ( separator ) {
			pathStart = separator + 1;
		}
	}

	while ( *pathStart == '/' || *pathStart == '\\' ) {
		pathStart++;
	}

	return pathStart;
}

/*
=============
CL_WebPak_NormalizePath

Normalise virtual paths for web.pak lookups.
=============
*/
static qboolean CL_WebPak_NormalizePath( const char *virtualPath, char *normalized, size_t normalizedSize ) {
	const char	*normalizedSource;
	size_t		index;

	if ( !virtualPath || !virtualPath[0] || !normalized || normalizedSize < 1 ) {
		return qfalse;
	}

	normalizedSource = CL_WebPak_StripProtocol( virtualPath );
	if ( !normalizedSource || !normalizedSource[0] ) {
		return qfalse;
	}

	for ( index = 0; normalizedSource[index] && normalizedSource[index] != '?' && normalizedSource[index] != '#'; index++ ) {
		char ch;

		if ( index >= normalizedSize - 1 ) {
			break;
		}

		ch = normalizedSource[index];
		normalized[index] = ( ch == '\\' ) ? '/' : ch;
	}
	normalized[index] = '\0';

	if ( !normalized[0] || strstr( normalized, ".." ) || strstr( normalized, "::" ) || strchr( normalized, ':' ) ) {
		return qfalse;
	}

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

	if ( !normalizedPath || !outBuffer ) {
		return qfalse;
	}

	if ( cl_webPak ) {
		length = FS_ReadFileFromPak( cl_webPak, normalizedPath, outBuffer );
		if ( length < 0 ) {
			return qfalse;
		}

		if ( outLength ) {
			*outLength = length;
		}
		return qtrue;
	}

	if ( cl_webDataPak.loaded ) {
		return CL_WebDataPak_Fetch( normalizedPath, outBuffer, outLength );
	}

	return qfalse;
}

/*
=============
CL_WebPak_AppendUniqueFile
=============
*/
static int CL_WebPak_AppendUniqueFile( const char *name, char *listbuf, int bufsize, int *outOffset, int count ) {
	char		*cursor;
	int		offset;
	int		length;

	if ( !name || !name[0] || !listbuf || !outOffset || bufsize <= 0 ) {
		return count;
	}

	cursor = listbuf;
	while ( *cursor ) {
		if ( !Q_stricmp( cursor, name ) ) {
			return count;
		}

		cursor += strlen( cursor ) + 1;
	}

	offset = *outOffset;
	length = strlen( name ) + 1;
	if ( offset + length + 1 >= bufsize ) {
		return count;
	}

	strcpy( listbuf + offset, name );
	offset += length;
	listbuf[offset] = '\0';
	*outOffset = offset;
	return count + 1;
}

/*
=============
CL_WebPak_AppendFileList
=============
*/
static int CL_WebPak_AppendFileList( const char *sourceList, int sourceCount, char *listbuf, int bufsize, int *outOffset, int count ) {
	const char	*cursor;
	int		i;

	if ( !sourceList || !listbuf || !outOffset || sourceCount <= 0 ) {
		return count;
	}

	cursor = sourceList;
	for ( i = 0; i < sourceCount && *cursor; i++ ) {
		count = CL_WebPak_AppendUniqueFile( cursor, listbuf, bufsize, outOffset, count );
		cursor += strlen( cursor ) + 1;
	}

	return count;
}

/*
=============
CL_WebDataPak_GetFileList
=============
*/
static int CL_WebDataPak_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {
	int		pathLength;
	int		extensionLength;
	int		offset;
	int		count;
	int		i;

	if ( !cl_webDataPak.loaded || !path || !extension || !listbuf || bufsize <= 0 ) {
		return 0;
	}

	pathLength = strlen( path );
	if ( pathLength > 0 && ( path[pathLength - 1] == '\\' || path[pathLength - 1] == '/' ) ) {
		pathLength--;
	}
	extensionLength = strlen( extension );

	listbuf[0] = '\0';
	offset = 0;
	count = 0;

	for ( i = 0; i < cl_webDataPak.pathCount; i++ ) {
		const char	*entryPath;
		const char	*name;
		int		length;

		entryPath = cl_webDataPak.paths[i].path;
		if ( pathLength > 0 ) {
			if ( Q_stricmpn( entryPath, path, pathLength ) || entryPath[pathLength] != '/' ) {
				continue;
			}
			name = entryPath + pathLength + 1;
		} else {
			name = entryPath;
		}

		if ( strchr( name, '/' ) || strchr( name, '\\' ) ) {
			continue;
		}

		length = strlen( entryPath );
		if ( length < extensionLength ) {
			continue;
		}

		if ( Q_stricmp( entryPath + length - extensionLength, extension ) ) {
			continue;
		}

		count = CL_WebPak_AppendUniqueFile( name, listbuf, bufsize, &offset, count );
	}

	return count;
}

/*
=============
CL_WebPak_GetFileList
=============
*/
int CL_WebPak_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {
	char		sourceList[CL_WEB_FILE_LIST_BUFFER];
	int		offset;
	int		count;
	int		sourceCount;

	if ( !path || !extension || !listbuf || bufsize <= 0 ) {
		return 0;
	}

	listbuf[0] = '\0';
	offset = 0;
	count = 0;

	if ( cl_webPak ) {
		sourceCount = FS_GetPakFileList( cl_webPak, path, extension, sourceList, sizeof( sourceList ) );
		count = CL_WebPak_AppendFileList( sourceList, sourceCount, listbuf, bufsize, &offset, count );
	}

	sourceCount = CL_WebDataPak_GetFileList( path, extension, sourceList, sizeof( sourceList ) );
	count = CL_WebPak_AppendFileList( sourceList, sourceCount, listbuf, bufsize, &offset, count );

	sourceCount = FS_GetFileList( path, extension, sourceList, sizeof( sourceList ) );
	count = CL_WebPak_AppendFileList( sourceList, sourceCount, listbuf, bufsize, &offset, count );

	return count;
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
	FILE			*fp;
	unsigned char		header[4];

	if ( cl_webPak ) {
		FS_FreePak( cl_webPak );
		cl_webPak = NULL;
	}
	CL_WebDataPak_Clear( &cl_webDataPak );

	Cvar_VariableStringBuffer( "fs_homepath", homePath, sizeof( homePath ) );
	CL_WebPak_BuildStandalonePath( homePath, "web.pak", pakPath, sizeof( pakPath ) );

	cl_webPak = FS_LoadPackExplicit( pakPath );
	if ( cl_webPak ) {
		Com_Printf( "web.pak mounted from %s\n", pakPath );
		return;
	}
	if ( CL_WebDataPak_Load( pakPath ) ) {
		Com_Printf( "web.pak datapack mounted from %s\n", pakPath );
		return;
	}

	// Retail Quake Live ships web.pak alongside the main executable under fs_basepath.
	Cvar_VariableStringBuffer( "fs_basepath", basePath, sizeof( basePath ) );
	CL_WebPak_BuildStandalonePath( basePath, "web.pak", pakPath, sizeof( pakPath ) );

	cl_webPak = FS_LoadPackExplicit( pakPath );
	if ( cl_webPak ) {
		Com_Printf( "web.pak mounted from %s\n", pakPath );
		return;
	}
	if ( CL_WebDataPak_Load( pakPath ) ) {
		Com_Printf( "web.pak datapack mounted from %s\n", pakPath );
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
	CL_WebDataPak_Clear( &cl_webDataPak );
}

/*
=============
CL_WebPak_Available
=============
*/
qboolean CL_WebPak_Available( void ) {
	return ( cl_webPak != NULL || cl_webDataPak.loaded );
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
