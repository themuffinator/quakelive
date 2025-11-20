#include "client.h"

#define CL_SCREENSHOT_SUBDIR "screenshots/"

/*
=============
CL_ScreenshotPathIsAllowed

Validate that the requested screenshot path stays within the screenshots directory.
=============
*/
static qboolean CL_ScreenshotPathIsAllowed( const char *requestedName ) {
	const char *trimmedName;

	if ( !requestedName || !requestedName[0] ) {
		return qfalse;
	}

	if ( requestedName[0] == '/' || requestedName[0] == '\\' ) {
		return qfalse;
	}

	if ( strstr( requestedName, ".." ) || strchr( requestedName, ':' ) || strchr( requestedName, '\\' ) ) {
		return qfalse;
	}

	if ( !Q_stricmpn( requestedName, CL_SCREENSHOT_SUBDIR, strlen( CL_SCREENSHOT_SUBDIR ) ) ) {
		trimmedName = requestedName + strlen( CL_SCREENSHOT_SUBDIR );
	} else {
		trimmedName = requestedName;
	}

	if ( trimmedName[0] == 0 ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_ScreenshotBuildQPath

Compose the qpath for a screenshot, ensuring it is rooted in the screenshots directory.
=============
*/
static void CL_ScreenshotBuildQPath( const char *requestedName, char *qpath, int qpathLen ) {
	if ( !Q_stricmpn( requestedName, CL_SCREENSHOT_SUBDIR, strlen( CL_SCREENSHOT_SUBDIR ) ) ) {
		Com_sprintf( qpath, qpathLen, "%s", requestedName );
	} else {
		Com_sprintf( qpath, qpathLen, "%s%s", CL_SCREENSHOT_SUBDIR, requestedName );
	}
}

/*
=============
CL_MenuReadScreenshot

Stream a screenshot file into the provided buffer for UI consumption.
=============
*/
int CL_MenuReadScreenshot( const char *requestedName, byte *buffer, int bufferSize ) {
	fileHandle_t file;
	char qpath[MAX_QPATH];
	int fileSize;
	int bytesToRead;

	if ( !buffer || bufferSize <= 0 ) {
		return -1;
	}

	if ( !CL_ScreenshotPathIsAllowed( requestedName ) ) {
		return -1;
	}

	CL_ScreenshotBuildQPath( requestedName, qpath, sizeof( qpath ) );

	fileSize = FS_FOpenFileRead( qpath, &file, qtrue );
	if ( fileSize <= 0 ) {
		return fileSize;
	}

	bytesToRead = fileSize;
	if ( bytesToRead > bufferSize ) {
		bytesToRead = bufferSize;
	}

	FS_Read( buffer, bytesToRead, file );
	FS_FCloseFile( file );

	return bytesToRead;
}
