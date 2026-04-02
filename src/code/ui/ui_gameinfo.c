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
//
//
// gameinfo.c
//

#include "ui_local.h"


//
// arena and bot info
//


int				ui_numBots;
static char		*ui_botInfos[MAX_BOTS];

static int		ui_numArenas;
static char		*ui_arenaInfos[MAX_ARENAS];


/*
===============
UI_ParseInfos
===============
*/
int UI_ParseInfos( char *buf, int max, char *infos[] ) {
	char	*token;
	int		count;
	char	key[MAX_TOKEN_CHARS];
	char	info[MAX_INFO_STRING];

	count = 0;

	while ( 1 ) {
		token = COM_Parse( &buf );
		if ( !token[0] ) {
			break;
		}
		if ( strcmp( token, "{" ) ) {
			Com_Printf( "Missing { in info file\n" );
			break;
		}

		if ( count == max ) {
			Com_Printf( "Max infos exceeded\n" );
			break;
		}

		info[0] = '\0';
		while ( 1 ) {
			token = COM_ParseExt( &buf, qtrue );
			if ( !token[0] ) {
				Com_Printf( "Unexpected end of info file\n" );
				break;
			}
			if ( !strcmp( token, "}" ) ) {
				break;
			}
			Q_strncpyz( key, token, sizeof( key ) );

			token = COM_ParseExt( &buf, qfalse );
			if ( !token[0] ) {
				strcpy( token, "<NULL>" );
			}
			Info_SetValueForKey( info, key, token );
		}
		//NOTE: extra space for arena number
		infos[count] = UI_Alloc(strlen(info) + strlen("\\num\\") + strlen(va("%d", MAX_ARENAS)) + 1);
		if (infos[count]) {
			strcpy(infos[count], info);
			count++;
		}
	}
	return count;
}

/*
===============
UI_LoadArenasFromFile
===============
*/
static void UI_LoadArenasFromFile( char *filename ) {
	int				len;
	fileHandle_t	f;
	char			buf[MAX_ARENAS_TEXT];

	len = trap_FS_FOpenFile( filename, &f, FS_READ );
	if ( !f ) {
		trap_Print( va( S_COLOR_RED "file not found: %s\n", filename ) );
		return;
	}
	if ( len >= MAX_ARENAS_TEXT ) {
		trap_Print( va( S_COLOR_RED "file too large: %s is %i, max allowed is %i", filename, len, MAX_ARENAS_TEXT ) );
		trap_FS_FCloseFile( f );
		return;
	}

	trap_FS_Read( buf, len, f );
	buf[len] = 0;
	trap_FS_FCloseFile( f );

	ui_numArenas += UI_ParseInfos( buf, MAX_ARENAS - ui_numArenas, &ui_arenaInfos[ui_numArenas] );
}

/*
===============
UI_LoadArenas
===============
*/
void UI_LoadArenas( void ) {
	int			numdirs;
	vmCvar_t	arenasFile;
	char		filename[128];
	char		dirlist[1024];
	char*		dirptr;
	int			i, n;
	int			dirlen;
	char		*type;

	ui_numArenas = 0;
	uiInfo.mapCount = 0;

	trap_Cvar_Register( &arenasFile, "g_arenasFile", "", CVAR_INIT|CVAR_ROM );
	if( *arenasFile.string ) {
		UI_LoadArenasFromFile(arenasFile.string);
	}
	else {
		UI_LoadArenasFromFile("scripts/arenas.txt");
	}

	// get all arenas from .arena files
	numdirs = trap_FS_GetFileList("scripts", ".arena", dirlist, 1024 );
	dirptr  = dirlist;
	for (i = 0; i < numdirs; i++, dirptr += dirlen+1) {
		dirlen = strlen(dirptr);
		strcpy(filename, "scripts/");
		strcat(filename, dirptr);
		UI_LoadArenasFromFile(filename);
	}
	trap_Print( va( "%i arenas parsed\n", ui_numArenas ) );
	if (UI_OutOfMemory()) {
		trap_Print(S_COLOR_YELLOW"WARNING: not anough memory in pool to load all arenas\n");
	}

	for( n = 0; n < ui_numArenas; n++ ) {
		// determine type

		uiInfo.mapList[uiInfo.mapCount].cinematic = -1;
		uiInfo.mapList[uiInfo.mapCount].mapLoadName = String_Alloc(Info_ValueForKey(ui_arenaInfos[n], "map"));
		uiInfo.mapList[uiInfo.mapCount].mapName = String_Alloc(Info_ValueForKey(ui_arenaInfos[n], "longname"));
		uiInfo.mapList[uiInfo.mapCount].levelShot = -1;
		uiInfo.mapList[uiInfo.mapCount].imageName = String_Alloc(va("levelshots/%s", uiInfo.mapList[uiInfo.mapCount].mapLoadName));
		uiInfo.mapList[uiInfo.mapCount].typeBits = 0;

		type = Info_ValueForKey( ui_arenaInfos[n], "type" );
		// if no type specified, it will be treated as "ffa"
		if( *type ) {
			if( strstr( type, "ffa" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_FFA);
			}
			if( strstr( type, "tourney" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_TOURNAMENT);
			}
			if( strstr( type, "single" ) || strstr( type, "race" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_SINGLE_PLAYER);
			}
			if( strstr( type, "team" ) || strstr( type, "tdm" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_TEAM);
			}
			if( strstr( type, "clanarena" ) || strstr( type, "ca" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_CLAN_ARENA);
			}
			if( strstr( type, "ctf" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_CTF);
			}
			if( strstr( type, "oneflag" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_1FCTF);
			}
			if( strstr( type, "overload" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_OBELISK);
			}
			if( strstr( type, "harvester" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_HARVESTER);
			}
			if( strstr( type, "freeze" ) || strstr( type, "freezetag" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_FREEZE);
			}
			if( strstr( type, "domination" ) || strstr( type, "dom" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_DOMINATION);
			}
			if( strstr( type, "attackdefend" ) || strstr( type, "ad" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_ATTACK_DEFEND);
			}
			if( strstr( type, "redrover" ) || strstr( type, "rr" ) ) {
				uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_RED_ROVER);
			}
		} else {
			uiInfo.mapList[uiInfo.mapCount].typeBits |= (1 << GT_FFA);
		}

		uiInfo.mapCount++;
		if (uiInfo.mapCount >= MAX_MAPS) {
			break;
		}
	}
}


/*
===============
UI_LoadBotsFromFile
===============
*/
static void UI_LoadBotsFromFile( char *filename ) {
	int				len;
	fileHandle_t	f;
	char			buf[MAX_BOTS_TEXT];

	len = trap_FS_FOpenFile( filename, &f, FS_READ );
	if ( !f ) {
		trap_Print( va( S_COLOR_RED "file not found: %s\n", filename ) );
		return;
	}
	if ( len >= MAX_BOTS_TEXT ) {
		trap_Print( va( S_COLOR_RED "file too large: %s is %i, max allowed is %i", filename, len, MAX_BOTS_TEXT ) );
		trap_FS_FCloseFile( f );
		return;
	}

	trap_FS_Read( buf, len, f );
	buf[len] = 0;
	trap_FS_FCloseFile( f );

	COM_Compress(buf);

	ui_numBots += UI_ParseInfos( buf, MAX_BOTS - ui_numBots, &ui_botInfos[ui_numBots] );
}

/*
===============
UI_LoadBots
===============
*/
void UI_LoadBots( void ) {
	vmCvar_t	botsFile;
	int			numdirs;
	char		filename[128];
	char		dirlist[1024];
	char*		dirptr;
	int			i;
	int			dirlen;

	ui_numBots = 0;

	trap_Cvar_Register( &botsFile, "g_botsFile", "", CVAR_INIT|CVAR_ROM );
	if( *botsFile.string ) {
		UI_LoadBotsFromFile(botsFile.string);
	}
	else {
		UI_LoadBotsFromFile("scripts/bots.txt");
	}

	// get all bots from .bot files
	numdirs = trap_FS_GetFileList("scripts", ".bot", dirlist, 1024 );
	dirptr  = dirlist;
	for (i = 0; i < numdirs; i++, dirptr += dirlen+1) {
		dirlen = strlen(dirptr);
		strcpy(filename, "scripts/");
		strcat(filename, dirptr);
		UI_LoadBotsFromFile(filename);
	}
	trap_Print( va( "%i bots parsed\n", ui_numBots ) );
}

/*
=============
UI_ClearMapRotations

Resets the cached list of map rotation entries so subsequent loads start fresh.
=============
*/
static void UI_ClearMapRotations( void ) {
	Com_Memset( uiInfo.mapRotations, 0, sizeof( uiInfo.mapRotations ) );
	uiInfo.mapRotationCount = 0;
}

/*
=============
UI_TrimRotationToken

Strips leading and trailing whitespace from a rotation token in-place.
=============
*/
static void UI_TrimRotationToken( char *token ) {
	char	*start;
	char	*end;
	size_t	length;

	if ( token == NULL ) {
		return;
	}

	start = token;
	while ( *start == ' ' || *start == '\t' ) {
		start++;
	}

	length = strlen( start );
	end = start + length;
	while ( end > start && ( end[-1] == ' ' || end[-1] == '\t' ) ) {
		end--;
	}
	*end = '\0';

	if ( start != token ) {
		memmove( token, start, ( end - start ) + 1 );
	}
}

/*
=============
UI_MapIndexForRotationToken

Finds the arena index for a given map token, matching either load or display names.
=============
*/
static int UI_MapIndexForRotationToken( const char *token ) {
	int i;

	if ( token == NULL || token[0] == '\0' ) {
		return -1;
	}

	for ( i = 0; i < uiInfo.mapCount; i++ ) {
		if ( !Q_stricmp( uiInfo.mapList[i].mapLoadName, token )
			|| !Q_stricmp( uiInfo.mapList[i].mapName, token ) ) {
			return i;
		}
	}

	return -1;
}

/*
=============
UI_PopulateRotationMetadata

Copies friendly metadata into the rotation entry after resolving the arena index.
=============
*/
static void UI_PopulateRotationMetadata( mapRotationInfo_t *entry, int mapIndex ) {
	if ( entry == NULL ) {
		return;
	}

	entry->mapIndex = mapIndex;

	if ( mapIndex >= 0 && mapIndex < uiInfo.mapCount ) {
		const mapInfo *map = &uiInfo.mapList[mapIndex];
		Q_strncpyz( entry->mapTitle, map->mapName, sizeof( entry->mapTitle ) );
	} else if ( entry->mapTitle[0] == '\0' ) {
		Q_strncpyz( entry->mapTitle, entry->mapName, sizeof( entry->mapTitle ) );
	}
}

/*
=============
UI_AddMapRotationFromLine

Parses a single rotation definition and appends it to the cache when valid.
=============
*/
static void UI_AddMapRotationFromLine( const char *line, const char *sourceTag ) {
	char			buffer[MAX_MAP_ROTATION_TOKEN * 2];
	char			*cursor;
	char			*factorySeparator;
	char			*configSeparator;
	char			*comment;
	mapRotationInfo_t	rotation;
	const char		*sourceName = ( sourceTag && sourceTag[0] ) ? sourceTag : "map rotation source";
	int			mapIndex;
	const char		*mapToken;
	const char		*factoryToken;
	const char		*configToken;
	const char		*factoryGameTypeToken;
	int				gameType;

	if ( line == NULL ) {
		return;
	}

	Q_strncpyz( buffer, line, sizeof( buffer ) );
	cursor = buffer;
	while ( *cursor == ' ' || *cursor == '\t' ) {
		cursor++;
	}
	if ( *cursor == '\0' || *cursor == '#' ) {
		return;
	}

	comment = strchr( cursor, '#' );
	if ( comment ) {
		*comment = '\0';
	}

	factorySeparator = strchr( cursor, '|' );
	if ( factorySeparator == NULL ) {
		Com_Printf( S_COLOR_RED "^1map rotation item missing map or factory name, skipping: %s\n", cursor );
		return;
	}

	*factorySeparator = '\0';
	mapToken = cursor;
	factoryToken = factorySeparator + 1;
	UI_TrimRotationToken( ( char * )mapToken );
	UI_TrimRotationToken( ( char * )factoryToken );

	if ( mapToken[0] == '\0' || factoryToken[0] == '\0' ) {
		Com_Printf( S_COLOR_RED "^1map rotation item missing map or factory name, skipping: %s\n", line );
		return;
	}

	if ( factoryToken[0] == '_' ) {
		Com_Printf( S_COLOR_RED "^1invalid factory found in rotation, skipping: %s\n", line );
		return;
	}

	configToken = NULL;
	factoryGameTypeToken = NULL;
	configSeparator = strchr( (char *)factoryToken, '|' );
	if ( configSeparator ) {
		*configSeparator = '\0';
		configToken = configSeparator + 1;
		UI_TrimRotationToken( ( char * )configToken );

		factorySeparator = strchr( (char *)configToken, '|' );
		if ( factorySeparator ) {
			*factorySeparator = '\0';
			factoryGameTypeToken = factorySeparator + 1;
			UI_TrimRotationToken( ( char * )factoryGameTypeToken );
		}
	}

	if ( configToken && !configToken[0] ) {
		configToken = NULL;
	}
	if ( factoryGameTypeToken && !factoryGameTypeToken[0] ) {
		factoryGameTypeToken = NULL;
	}

	if ( uiInfo.mapRotationCount >= MAX_MAP_ROTATIONS ) {
		Com_Printf( S_COLOR_RED "^1map rotation cache full (%i entries), skipping remainder from %s\n",
			MAX_MAP_ROTATIONS, sourceName );
		return;
	}

	mapIndex = UI_MapIndexForRotationToken( mapToken );
	if ( mapIndex < 0 ) {
		Com_Printf( S_COLOR_RED "^1map doesn't exist, skipping: %s\n", mapToken );
		return;
	}

	if ( factoryGameTypeToken && factoryGameTypeToken[0] ) {
		gameType = UI_ParseCallvoteGametypeToken( factoryGameTypeToken );
		if ( gameType >= GT_FFA && gameType < GT_MAX_GAME_TYPE ) {
			const mapInfo *map = &uiInfo.mapList[mapIndex];
			if ( ( map->typeBits & ( 1 << gameType ) ) == 0 ) {
				Com_Printf( S_COLOR_RED "^1map isn't valid for factory gametype, skipping: %s\n", line );
				return;
			}
		}
	}

	Com_Memset( &rotation, 0, sizeof( rotation ) );
	Q_strncpyz( rotation.mapName, mapToken, sizeof( rotation.mapName ) );
	Q_strncpyz( rotation.factoryId, factoryToken, sizeof( rotation.factoryId ) );
	if ( configToken ) {
		Q_strncpyz( rotation.factoryConfig, configToken, sizeof( rotation.factoryConfig ) );
	}
	if ( factoryGameTypeToken ) {
		Q_strncpyz( rotation.factoryGameType, factoryGameTypeToken, sizeof( rotation.factoryGameType ) );
	}
	Q_strncpyz( rotation.mapTitle, mapToken, sizeof( rotation.mapTitle ) );
	UI_PopulateRotationMetadata( &rotation, mapIndex );

	uiInfo.mapRotations[uiInfo.mapRotationCount++] = rotation;
}

/*
=============
UI_ParseMapRotationText

Tokenizes rotation definitions from a buffer and forwards them to the line parser.
=============
*/
static void UI_ParseMapRotationText( const char *text, const char *sourceTag ) {
	const char	*cursor;
	char		line[MAX_MAP_ROTATION_TOKEN * 2];
	size_t	length;

	if ( text == NULL ) {
		return;
	}

	cursor = text;
	while ( *cursor ) {
		length = 0;
		while ( cursor[length] && cursor[length] != '\n' && cursor[length] != '\r'
			&& length < sizeof( line ) - 1 ) {
			line[length] = cursor[length];
			length++;
		}
		line[length] = '\0';
		UI_AddMapRotationFromLine( line, sourceTag );

		cursor += length;
		while ( *cursor == '\n' || *cursor == '\r' ) {
			cursor++;
		}
	}
}

/*
=============
UI_LoadMapRotationsFromInlineCvar

Attempts to load rotation definitions embedded in a CVar string.
=============
*/
static qboolean UI_LoadMapRotationsFromInlineCvar( const char *cvarName ) {
	char buffer[MAX_CVAR_VALUE_STRING];

	if ( cvarName == NULL ) {
		return qfalse;
	}

	trap_Cvar_VariableStringBuffer( cvarName, buffer, sizeof( buffer ) );
	if ( buffer[0] == '\0' ) {
		return qfalse;
	}

	UI_ParseMapRotationText( buffer, cvarName );
	return ( uiInfo.mapRotationCount > 0 );
}

/*
=============
UI_LoadMapRotationsFromFile

Loads rotation definitions from disk, mirroring the HLIL file size guardrails.
=============
*/
static qboolean UI_LoadMapRotationsFromFile( const char *path ) {
	fileHandle_t file;
	int		length;
	static char buffer[MAX_MAP_ROTATION_FILE_BYTES];

	if ( path == NULL || path[0] == '\0' ) {
		return qfalse;
	}

	length = trap_FS_FOpenFile( path, &file, FS_READ );
	if ( length <= 0 || !file ) {
		Com_Printf( S_COLOR_RED "^1rotation file not found: %s\n", path );
		return qfalse;
	}
	if ( length >= MAX_MAP_ROTATION_FILE_BYTES ) {
		Com_Printf( S_COLOR_RED "^1rotations file too large: %s is %i, max allowed is %i^7\n",
			path, length, MAX_MAP_ROTATION_FILE_BYTES - 1 );
		trap_FS_FCloseFile( file );
		return qfalse;
	}

	trap_FS_Read( buffer, length, file );
	buffer[length] = '\0';
	trap_FS_FCloseFile( file );

	UI_ParseMapRotationText( buffer, path );
	return ( uiInfo.mapRotationCount > 0 );
}

/*
=============
UI_LoadMapRotations

Builds the UI map rotation cache from inline CVars, user-selected files, or defaults.
=============
*/
void UI_LoadMapRotations( void ) {
	static const char *inlineCvars[] = { "ui_mapRotation", "sv_mapRotation", "g_mapRotation", NULL };
	static const char *fileCvars[] = { "ui_mapPoolFile", "sv_mapPoolFile", NULL };
	char		path[MAX_QPATH];
	int		index;

	UI_ClearMapRotations();

	for ( index = 0; inlineCvars[index] != NULL && uiInfo.mapRotationCount == 0; index++ ) {
		UI_LoadMapRotationsFromInlineCvar( inlineCvars[index] );
	}

	if ( uiInfo.mapRotationCount == 0 ) {
		for ( index = 0; fileCvars[index] != NULL && uiInfo.mapRotationCount == 0; index++ ) {
			trap_Cvar_VariableStringBuffer( fileCvars[index], path, sizeof( path ) );
			if ( path[0] != '\0' ) {
				UI_LoadMapRotationsFromFile( path );
			}
		}
	}

	if ( uiInfo.mapRotationCount == 0 ) {
		UI_LoadMapRotationsFromFile( "mappool.txt" );
	}

	Com_Printf( "loaded %i maps into the map rotation cache\n", uiInfo.mapRotationCount );
}

/*
===============
UI_GetBotInfoByNumber
===============
*/
char *UI_GetBotInfoByNumber( int num ) {
	if( num < 0 || num >= ui_numBots ) {
		trap_Print( va( S_COLOR_RED "Invalid bot number: %i\n", num ) );
		return NULL;
	}
	return ui_botInfos[num];
}


/*
===============
UI_GetBotInfoByName
===============
*/
char *UI_GetBotInfoByName( const char *name ) {
	int		n;
	char	*value;

	for ( n = 0; n < ui_numBots ; n++ ) {
		value = Info_ValueForKey( ui_botInfos[n], "name" );
		if ( !Q_stricmp( value, name ) ) {
			return ui_botInfos[n];
		}
	}

	return NULL;
}

int UI_GetNumBots() {
	return ui_numBots;
}


char *UI_GetBotNameByNumber( int num ) {
	char *info = UI_GetBotInfoByNumber(num);
	if (info) {
		return Info_ValueForKey( info, "name" );
	}
	return "Sarge";
}
