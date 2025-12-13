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

#include "server.h"

#define SV_FACTORY_MAX_JSON_STRING        4096
#define SV_FACTORY_FILE_LIST_BUFFER       4096

#define SV_MAX_MAP_GAMETYPE_ALIASES       3

typedef struct svFactoryParseState_s {
	const char *cursor;
	const char *end;
	const char *filename;
	int line;
} svFactoryParseState_t;

typedef struct svFactoryDefinition_s {
	char *id;
	gametype_t baseGametype;
	char *sourceFile;
	struct svFactoryDefinition_s *next;
} svFactoryDefinition_t;

static qboolean s_svFactoryRegistryLoaded = qfalse;
static svFactoryDefinition_t *s_svFactoryList = NULL;
static qboolean s_svArenaRegistryLoaded = qfalse;
static int s_svNumArenaInfos = 0;
static char *s_svArenaInfos[MAX_ARENAS];

/*
=============
SV_FactoryCopyString

Allocates a persistent copy of the supplied string using the zone allocator.
=============
*/
static char *SV_FactoryCopyString( const char *value ) {
	size_t length;
	char *copy;

	if ( !value ) {
		return NULL;
	}

	length = strlen( value ) + 1u;
	copy = ( char * )Z_Malloc( length );
	if ( copy ) {
		memcpy( copy, value, length );
	}

	return copy;
}

/*
=============
SV_FactoryReportParseError

Logs a descriptive parse error so administrators can diagnose malformed JSON.
=============
*/
static void SV_FactoryReportParseError( const svFactoryParseState_t *state, const char *message ) {
	const char *filename = ( state && state->filename ) ? state->filename : "<unknown>";
	int line = state ? state->line : 0;

	if ( !message ) {
		message = "unknown parse error";
	}

	Com_Printf( "factories: parse error in %s at line %i: %s\n", filename, line, message );
}

/*
=============
SV_FactorySkipWhitespace

Advances the parse cursor beyond any whitespace, updating the current line.
=============
*/
static void SV_FactorySkipWhitespace( svFactoryParseState_t *state ) {
	if ( !state || !state->cursor || state->cursor >= state->end ) {
		return;
	}

	while ( state->cursor < state->end ) {
		char ch = *state->cursor;

		if ( ch == '\n' ) {
			state->line++;
		}

		if ( ch != ' ' && ch != '\t' && ch != '\r' && ch != '\n' ) {
			return;
		}

		state->cursor++;
	}
}

/*
=============
SV_FactoryParseExpectedChar

Ensures the next non-whitespace character matches *ch*.
=============
*/
static qboolean SV_FactoryParseExpectedChar( svFactoryParseState_t *state, char ch ) {
	SV_FactorySkipWhitespace( state );
	if ( !state || !state->cursor || state->cursor >= state->end ) {
		SV_FactoryReportParseError( state, va( "expected '%c'", ch ) );
		return qfalse;
	}
	if ( *state->cursor != ch ) {
		SV_FactoryReportParseError( state, va( "expected '%c'", ch ) );
		return qfalse;
	}
	state->cursor++;
	return qtrue;
}

/*
=============
SV_FactorySkipJsonString

Skips over a JSON string literal, handling escapes.
=============
*/
static qboolean SV_FactorySkipJsonString( svFactoryParseState_t *state ) {
	if ( !state || !state->cursor || state->cursor >= state->end || *state->cursor != '"' ) {
		SV_FactoryReportParseError( state, "expected string" );
		return qfalse;
	}

	state->cursor++;
	while ( state->cursor < state->end ) {
		char ch = *state->cursor++;

		if ( ch == '"' ) {
			return qtrue;
		}

		if ( ch == '\\' && state->cursor < state->end ) {
			state->cursor++;
		}
	}

	SV_FactoryReportParseError( state, "unterminated string" );
	return qfalse;
}

/*
=============
SV_FactoryParseJsonString

Parses a JSON string literal and returns a heap-allocated copy.
=============
*/
static char *SV_FactoryParseJsonString( svFactoryParseState_t *state ) {
	char buffer[SV_FACTORY_MAX_JSON_STRING];
	int length;

	SV_FactorySkipWhitespace( state );
	if ( !state || !state->cursor || state->cursor >= state->end || *state->cursor != '"' ) {
		SV_FactoryReportParseError( state, "expected string" );
		return NULL;
	}

	state->cursor++;
	length = 0;
	while ( state->cursor < state->end ) {
		char ch = *state->cursor++;

		if ( ch == '"' ) {
			buffer[length] = '\0';
			return SV_FactoryCopyString( buffer );
		}

		if ( ch == '\\' && state->cursor < state->end ) {
			char escaped = *state->cursor++;

			switch ( escaped ) {
			case '\"':
				case '\\':
					case '/':
							ch = escaped;
							break;
						case 'b':
								ch = '\b';
								break;
							case 'f':
									ch = '\f';
									break;
								case 'n':
										ch = '\n';
										break;
									case 'r':
											ch = '\r';
											break;
										case 't':
												ch = '\t';
												break;
											default:
													SV_FactoryReportParseError( state, "invalid escape" );
													return NULL;
												}
											}

											if ( length + 1 >= SV_FACTORY_MAX_JSON_STRING ) {
												SV_FactoryReportParseError( state, "string literal too long" );
												return NULL;
											}

											buffer[length++] = ch;
										}

										SV_FactoryReportParseError( state, "unterminated string" );
										return NULL;
									}

									/*
									=============
									SV_FactoryParseLiteralString

									Parses a literal token (numbers, booleans) int o a new string.
									=============
									*/
									static char *SV_FactoryParseLiteralString( svFactoryParseState_t *state ) {
										char buffer[SV_FACTORY_MAX_JSON_STRING];
										int length;

										SV_FactorySkipWhitespace( state );
										if ( !state || !state->cursor || state->cursor >= state->end ) {
											SV_FactoryReportParseError( state, "expected literal" );
											return NULL;
										}

										length = 0;
										while ( state->cursor < state->end ) {
											char ch = *state->cursor;

											if ( ch == ',' || ch == '}' || ch == ']' || ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n' ) {
												break;
											}

											if ( length + 1 >= SV_FACTORY_MAX_JSON_STRING ) {
												SV_FactoryReportParseError( state, "literal too long" );
												return NULL;
											}

											buffer[length++] = ch;
											state->cursor++;
										}

										buffer[length] = '\0';
										return SV_FactoryCopyString( buffer );
									}

									/*
									=============
									SV_FactorySkipValue

									Skips an arbitrary JSON value (objects, arrays, strings, literals).
									=============
									*/
									static qboolean SV_FactorySkipValue( svFactoryParseState_t *state ) {
										SV_FactorySkipWhitespace( state );
										if ( !state || !state->cursor || state->cursor >= state->end ) {
											SV_FactoryReportParseError( state, "unexpected end of data" );
											return qfalse;
										}

										switch ( *state->cursor ) {
										case '{':
												state->cursor++;
												while ( state->cursor < state->end ) {
													if ( !SV_FactorySkipJsonString( state ) ) {
														return qfalse;
													}
													if ( !SV_FactoryParseExpectedChar( state, ':' ) ) {
														return qfalse;
													}
													if ( !SV_FactorySkipValue( state ) ) {
														return qfalse;
													}
													SV_FactorySkipWhitespace( state );
													if ( state->cursor >= state->end ) {
														break;
													}
													if ( *state->cursor == '}' ) {
														state->cursor++;
														return qtrue;
													}
													if ( *state->cursor != ',' ) {
														SV_FactoryReportParseError( state, "expected ',' or '}'" );
														return qfalse;
													}
													state->cursor++;
												}
												SV_FactoryReportParseError( state, "unterminated object" );
												return qfalse;
											case '[':
													state->cursor++;
													while ( state->cursor < state->end ) {
														if ( !SV_FactorySkipValue( state ) ) {
															return qfalse;
														}
														SV_FactorySkipWhitespace( state );
														if ( state->cursor >= state->end ) {
															break;
														}
														if ( *state->cursor == ']' ) {
															state->cursor++;
															return qtrue;
														}
														if ( *state->cursor != ',' ) {
															SV_FactoryReportParseError( state, "expected ',' or ']'" );
															return qfalse;
														}
														state->cursor++;
													}
													SV_FactoryReportParseError( state, "unterminated array" );
													return qfalse;
												case '"':
														return SV_FactorySkipJsonString( state );
													default:
															( void )SV_FactoryParseLiteralString( state );
															return qtrue;
														}
													}

													/*
													=============
													SV_FactoryMapBaseGametype

													Translates textual base gametype tokens int o gametype_t values.
													=============
													*/
													static qboolean SV_FactoryMapBaseGametype( const char *token, gametype_t *outType ) {
														static const struct {
															const char *name;
															gametype_t type;
														} s_gametypeMap[] = {
															{ "ffa", GT_FFA },
															{ "duel", GT_TOURNAMENT },
															{ "race", GT_RACE },
															{ "tdm", GT_TEAM },
															{ "ca", GT_CLAN_ARENA },
															{ "ctf", GT_CTF },
															{ "oneflag", GT_1FCTF },
															{ "dom", GT_DOMINATION },
															{ "ad", GT_ATTACK_DEFEND },
															{ "ft", GT_FREEZE },
															{ "har", GT_HARVESTER },
															{ "rr", GT_RED_ROVER }
														};
														int i;

														if ( !token || !*token ) {
															return qfalse;
														}

														for ( i = 0; i < (int)( sizeof( s_gametypeMap ) / sizeof( s_gametypeMap[0] ) ); i++ ) {
															if ( !Q_stricmp( token, s_gametypeMap[i].name ) ) {
																if ( outType ) {
																	*outType = s_gametypeMap[i].type;
																}
																return qtrue;
															}
														}

														return qfalse;
													}

													/*
													=============
													SV_FactoryParseDefinition

													Parses a single factory definition object.
													=============
													*/
													static svFactoryDefinition_t *SV_FactoryParseDefinition( svFactoryParseState_t *state, const char *sourceFile ) {
														svFactoryDefinition_t *definition;
														char *id;
														char *basegt;

														if ( !SV_FactoryParseExpectedChar( state, '{' ) ) {
															return NULL;
														}

														definition = ( svFactoryDefinition_t * )Z_Malloc( sizeof( svFactoryDefinition_t ) );
														if ( !definition ) {
															return NULL;
														}

														definition->sourceFile = sourceFile ? SV_FactoryCopyString( sourceFile ) : NULL;
														definition->id = NULL;
														definition->baseGametype = GT_FFA;
														definition->next = NULL;

														id = NULL;
														basegt = NULL;

														while ( state && state->cursor < state->end ) {
															char *key;

															SV_FactorySkipWhitespace( state );
															if ( state->cursor >= state->end ) {
																SV_FactoryReportParseError( state, "unterminated factory object" );
																goto fail;
															}
															if ( *state->cursor == '}' ) {
																state->cursor++;
																break;
															}

															key = SV_FactoryParseJsonString( state );
															if ( !key ) {
																goto fail;
															}
															if ( !SV_FactoryParseExpectedChar( state, ':' ) ) {
																Z_Free( key );
																goto fail;
															}

															if ( !Q_stricmp( key, "id" ) ) {
																if ( id ) {
																	Z_Free( id );
																}
																id = SV_FactoryParseJsonString( state );
															} else if ( !Q_stricmp( key, "basegt" ) ) {
																if ( basegt ) {
																	Z_Free( basegt );
																}
																basegt = SV_FactoryParseJsonString( state );
															} else {
																if ( !SV_FactorySkipValue( state ) ) {
																	Z_Free( key );
																	goto fail;
																}
															}

															Z_Free( key );

															SV_FactorySkipWhitespace( state );
															if ( state->cursor >= state->end ) {
																SV_FactoryReportParseError( state, "unterminated factory object" );
																goto fail;
															}
															if ( *state->cursor == '}' ) {
																state->cursor++;
																break;
															}
															if ( *state->cursor != ',' ) {
																SV_FactoryReportParseError( state, "expected ',' or '}'" );
																goto fail;
															}
															state->cursor++;
														}

														if ( !id ) {
															SV_FactoryReportParseError( state, "factory missing id" );
															goto fail;
														}
														if ( !basegt || !SV_FactoryMapBaseGametype( basegt, &definition->baseGametype ) ) {
															SV_FactoryReportParseError( state, va( "factory %s missing valid basegt", id ) );
															goto fail;
														}

														definition->id = id;
														Z_Free( basegt );
														return definition;

														fail:
														if ( id ) {
															Z_Free( id );
														}
														if ( basegt ) {
															Z_Free( basegt );
														}
														if ( definition ) {
															if ( definition->sourceFile ) {
																Z_Free( definition->sourceFile );
															}
															Z_Free( definition );
														}
														return NULL;
													}

													/*
													=============
													SV_FactoryRegisterDefinition

													Adds a parsed definition to the registry when the id is unique.
													=============
													*/
													static qboolean SV_FactoryRegisterDefinition( svFactoryDefinition_t *definition ) {
														svFactoryDefinition_t *iter;

														if ( !definition || !definition->id ) {
															return qfalse;
														}

														for ( iter = s_svFactoryList; iter; iter = iter->next ) {
															if ( !Q_stricmp( iter->id, definition->id ) ) {
																Com_Printf( "factories: duplicate id %s from %s ignored (already provided by %s)\n",
																definition->id,
																definition->sourceFile ? definition->sourceFile : "<unknown>",
																iter->sourceFile ? iter->sourceFile : "<unknown>" );
																return qfalse;
															}
														}

														definition->next = s_svFactoryList;
														s_svFactoryList = definition;
														return qtrue;
													}

													/*
													=============
													SV_FactoryParseFactoriesBuffer

													Reads a JSON array of factory definitions from memory.
													=============
													*/
													static int SV_FactoryParseFactoriesBuffer( const char *filename, const char *buffer, int length ) {
														svFactoryParseState_t state;
														int count;

														if ( !buffer || length <= 0 ) {
															return 0;
														}

														state.cursor = buffer;
														state.end = buffer + length;
														state.filename = filename;
														state.line = 1;

														SV_FactorySkipWhitespace( &state );
														if ( !SV_FactoryParseExpectedChar( &state, '[' ) ) {
															return 0;
														}

														count = 0;
														while ( state.cursor < state.end ) {
															svFactoryDefinition_t *definition = SV_FactoryParseDefinition( &state, filename );
															if ( !definition ) {
																break;
															}
															if ( SV_FactoryRegisterDefinition( definition ) ) {
																count++;
															}

															SV_FactorySkipWhitespace( &state );
															if ( state.cursor >= state.end ) {
																break;
															}
															if ( *state.cursor == ']' ) {
																state.cursor++;
																return count;
															}
															if ( *state.cursor != ',' ) {
																SV_FactoryReportParseError( &state, "expected ',' or ']'" );
																return count;
															}
															state.cursor++;
														}

														SV_FactoryReportParseError( &state, "unterminated factory array" );
														return count;
													}

													/*
													=============
													SV_FactoryLoadFile

													Reads and parses a factories file.
													=============
													*/
													static qboolean SV_FactoryLoadFile( const char *filename ) {
														fileHandle_t file;
														int length;
														char *data;

														length = FS_FOpenFileRead( filename, &file, qfalse );
														if ( length <= 0 ) {
															return qfalse;
														}
														if ( length >= SV_FACTORY_MAX_JSON_STRING * 64 ) {
															Com_Printf( "factories: file %s too large (%i bytes)\n", filename, length );
															FS_FCloseFile( file );
															return qfalse;
														}

														data = ( char * )Z_Malloc( length + 1 );
														if ( !data ) {
															FS_FCloseFile( file );
															return qfalse;
														}

														FS_Read( data, length, file );
														data[length] = '\0';
														FS_FCloseFile( file );

														SV_FactoryParseFactoriesBuffer( filename, data, length );
														Z_Free( data );
														return qtrue;
													}

													/*
													=============
													SV_FactoryLoadSupplementalFiles

													Loads optional *.factories files from the scripts directory.
													=============
													*/
													static void SV_FactoryLoadSupplementalFiles( void ) {
														char fileList[SV_FACTORY_FILE_LIST_BUFFER];
														char *cursor;
														int count;
														int index;

														count = FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );
														cursor = fileList;
														for ( index = 0; index < count; index++ ) {
															int length = strlen( cursor );
															char path[MAX_QPATH];

															if ( length <= 0 ) {
																cursor++;
																continue;
															}

															Com_sprint f( path, sizeof( path ), "scripts/%s", cursor );
															SV_FactoryLoadFile( path );
															cursor += length + 1;
														}
													}

													/*
													=============
													SV_FactoryEnsureRegistryLoaded

													Initialises the factory registry on demand.
													=============
													*/
													static void SV_FactoryEnsureRegistryLoaded( void ) {
														if ( s_svFactoryRegistryLoaded ) {
															return;
														}

														SV_FactoryLoadFile( "scripts/factories.txt" );
														SV_FactoryLoadSupplementalFiles();
														s_svFactoryRegistryLoaded = qtrue;
													}

													/*
													=============
													SV_FactoryFindById

													Looks up a previously parsed factory definition by id.
													=============
													*/
													static const svFactoryDefinition_t *SV_FactoryFindById( const char *id ) {
														const svFactoryDefinition_t *factory;

														SV_FactoryEnsureRegistryLoaded();
														if ( !id || !*id ) {
															return NULL;
														}

														for ( factory = s_svFactoryList; factory; factory = factory->next ) {
															if ( !Q_stricmp( factory->id, id ) ) {
																return factory;
															}
														}

														return NULL;
													}

													/*
													=============
													SV_ParseInfos

													Parses info blocks from arena definition files.
													=============
													*/
													static int SV_ParseInfos( char *buf, int max, char *infos[] ) {
														char *token;
														int count;
														char key[MAX_TOKEN_CHARS];
														char info[MAX_INFO_STRING];

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
																	Q_strncpyz( token, "<NULL>", MAX_TOKEN_CHARS );
																}
																Info_SetValueForKey( info, key, token );
															}

															infos[count] = ( char * )Z_Malloc( strlen( info ) + strlen( "\\num\\" ) + strlen( va( "%d", MAX_ARENAS ) ) + 1 );
															if ( infos[count] ) {
																strcpy( infos[count], info );
																count++;
															}
														}

														return count;
													}

													/*
													=============
													SV_LoadArenasFromFile

													Loads arena definitions from the given file.
													=============
													*/
													static void SV_LoadArenasFromFile( const char *filename ) {
														fileHandle_t file;
														int length;
														char buffer[MAX_ARENAS_TEXT];

														length = FS_FOpenFileRead( filename, &file, qfalse );
														if ( length <= 0 ) {
															return;
														}
														if ( length >= MAX_ARENAS_TEXT ) {
															Com_Printf( "arenas: file %s too large (%i bytes)\n", filename, length );
															FS_FCloseFile( file );
															return;
														}

														FS_Read( buffer, length, file );
														buffer[length] = '\0';
														FS_FCloseFile( file );

														s_svNumArenaInfos += SV_ParseInfos( buffer, MAX_ARENAS - s_svNumArenaInfos, &s_svArenaInfos[s_svNumArenaInfos] );
													}

													/*
													=============
													SV_LoadArenaRegistry

													Initialises the cached arena metadata used for gametype validation.
													=============
													*/
													static void SV_LoadArenaRegistry( void ) {
														char fileList[MAX_ARENAS_TEXT];
														char *cursor;
														int count;
														int index;

														if ( s_svArenaRegistryLoaded ) {
															return;
														}

														s_svNumArenaInfos = 0;
														SV_LoadArenasFromFile( "scripts/arenas.txt" );

														count = FS_GetFileList( "scripts", ".arena", fileList, sizeof( fileList ) );
														cursor = fileList;
														for ( index = 0; index < count; index++ ) {
															int length = strlen( cursor );
															char path[MAX_QPATH];

															if ( length <= 0 ) {
																cursor++;
																continue;
															}

															Com_sprint f( path, sizeof( path ), "scripts/%s", cursor );
															SV_LoadArenasFromFile( path );
															cursor += length + 1;
														}

														s_svArenaRegistryLoaded = qtrue;
													}

													/*
													=============
													SV_GetArenaInfoByMap

													Returns arena metadata for the supplied map name when available.
													=============
													*/
													static const char *SV_GetArenaInfoByMap( const char *map ) {
														int index;

														if ( !map || !*map ) {
															return NULL;
														}

														SV_LoadArenaRegistry();
														for ( index = 0; index < s_svNumArenaInfos; index++ ) {
															if ( !Q_stricmp( Info_ValueForKey( s_svArenaInfos[index], "map" ), map ) ) {
																return s_svArenaInfos[index];
															}
														}

														return NULL;
													}

													/*
													=============
													SV_MapTypesContainToken

													Returns qtrue when the arena type list includes the supplied token.
													=============
													*/
													static qboolean SV_MapTypesContainToken( const char *typeList, const char *token ) {
														const char *scan;
														size_t tokenLength;

														if ( !typeList || !*typeList || !token || !*token ) {
															return qfalse;
														}

														tokenLength = strlen( token );
														scan = typeList;
														while ( *scan ) {
															const char *start;
															size_t length;

															while ( *scan && *scan <= ' ' ) {
																scan++;
															}
															if ( !*scan ) {
																break;
															}

															start = scan;
															while ( *scan && *scan > ' ' ) {
																scan++;
															}
															length = scan - start;

															if ( length == tokenLength && !Q_strnicmp( start, token, tokenLength ) ) {
																return qtrue;
															}
														}

														return qfalse;
													}

													/*
													=============
													SV_MapSupportsGametype

													Determines whether the supplied map exposes entities for the requested gametype.
													=============
													*/
													static qboolean SV_MapSupportsGametype( const char *mapName, gametype_t gametype ) {
														static const char *const s_gametypeTokens[GT_MAX_GAME_TYPE][SV_MAX_MAP_GAMETYPE_ALIASES] = {
															[GT_FFA] = { "ffa", NULL, NULL },
															[GT_TOURNAMENT] = { "duel", "tourney", NULL },
															[GT_SINGLE_PLAYER] = { "single", NULL, NULL },
															[GT_TEAM] = { "tdm", "team", NULL },
															[GT_CLAN_ARENA] = { "ca", "clanarena", NULL },
															[GT_CTF] = { "ctf", NULL, NULL },
															[GT_1FCTF] = { "oneflag", "1fctf", NULL },
															[GT_OBELISK] = { "overload", "obelisk", NULL },
															[GT_HARVESTER] = { "har", "harvester", NULL },
															[GT_FREEZE] = { "ft", "freeze", NULL },
															[GT_DOMINATION] = { "dom", "domination", NULL },
															[GT_ATTACK_DEFEND] = { "ad", "attackdefend", NULL },
															[GT_RED_ROVER] = { "rr", "redrover", NULL },
															[GT_RACE] = { "race", NULL, NULL }
														};
														const char *info;
														const char *types;
														const char *const*aliases;
														int aliasIndex;

														if ( !mapName || !*mapName || mapName[0] == '_' ) {
															return qtrue;
														}

														if ( gametype < GT_FFA || gametype >= GT_MAX_GAME_TYPE ) {
															return qtrue;
														}

														info = SV_GetArenaInfoByMap( mapName );
														if ( !info ) {
															return qtrue;
														}

														types = Info_ValueForKey( info, "type" );
														if ( !types || !*types ) {
															return qtrue;
														}

														aliases = s_gametypeTokens[gametype];
														for ( aliasIndex = 0; aliasIndex < SV_MAX_MAP_GAMETYPE_ALIASES; aliasIndex++ ) {
															const char *token = aliases[aliasIndex];

															if ( token && SV_MapTypesContainToken( types, token ) ) {
																return qtrue;
															}
														}

														return qfalse;
													}


/*
===============================================================================

OPERATOR CONSOLE ONLY COMMANDS

These commands can only be entered from stdin or by a remote operator datagram
===============================================================================
*/


/*
==================
SV_GetPlayerByName

Returns the player with name from Cmd_Argv(1)
==================
*/
static client_t *SV_GetPlayerByName( void ) {
	client_t	*cl;
	int			i;
	char		*s;
	char		cleanName[64];

	// make sure server is running
	if ( !com_sv_running->integer ) {
		return NULL;
	}

	if ( Cmd_Argc() < 2 ) {
		Com_Printf( "No player specified.\n" );
		return NULL;
	}

	s = Cmd_Argv(1);

	// check for a name match
	for ( i=0, cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++ ) {
		if ( !cl->state ) {
			continue;
		}
		if ( !Q_stricmp( cl->name, s ) ) {
			return cl;
		}

		Q_strncpyz( cleanName, cl->name, sizeof(cleanName) );
		Q_CleanStr( cleanName );
		if ( !Q_stricmp( cleanName, s ) ) {
			return cl;
		}
	}

	Com_Printf( "Player %s is not on the server\n", s );

	return NULL;
}

/*
==================
SV_GetPlayerByNum

Returns the player with idnum from Cmd_Argv(1)
==================
*/
static client_t *SV_GetPlayerByNum( void ) {
	client_t	*cl;
	int			i;
	int			idnum;
	char		*s;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		return NULL;
	}

	if ( Cmd_Argc() < 2 ) {
		Com_Printf( "No player specified.\n" );
		return NULL;
	}

	s = Cmd_Argv(1);

	for (i = 0; s[i]; i++) {
		if (s[i] < '0' || s[i] > '9') {
			Com_Printf( "Bad slot number: %s\n", s);
			return NULL;
		}
	}
	idnum = atoi( s );
	if ( idnum < 0 || idnum >= sv_maxclients->integer ) {
		Com_Printf( "Bad client slot: %i\n", idnum );
		return NULL;
	}

	cl = &svs.clients[idnum];
	if ( !cl->state ) {
		Com_Printf( "Client %i is not active\n", idnum );
		return NULL;
	}
	return cl;

	return NULL;
}

//=========================================================


/*
==================
SV_Map_f

Restart the server on a different map
==================
*/
static void SV_Map_f( void ) {
	char		*cmd;
	char		*map;
	qboolean	killBots, cheat;
	char		expanded[MAX_QPATH];
	char		mapname[MAX_QPATH];
	const svFactoryDefinition_t	*factoryOverride;
	const char		*factoryId;

	map = Cmd_Argv(1);
	if ( !map ) {
		return;
	}

	// make sure the level exists before trying to change, so that
	// a typo at the server console won't end the game
	Com_sprintf (expanded, sizeof(expanded), "maps/%s.bsp", map);
	if ( FS_ReadFile (expanded, NULL) == -1 ) {
		Com_Printf ("Can't find map %s\n", expanded);
		return;
	}

	if ( SV_HandleQuitOnExitLevel( map ) ) {
		return;
	}

	// force latched values to get set
	Cvar_Get ("g_gametype", "0", CVAR_SERVERINFO | CVAR_USERINFO | CVAR_LATCH );

	factoryOverride = NULL;
	factoryId = NULL;

	cmd = Cmd_Argv(0);
	if( Q_stricmpn( cmd, "sp", 2 ) == 0 ) {
		Cvar_SetValue( "g_gametype", GT_SINGLE_PLAYER );
		Cvar_SetValue( "g_doWarmup", 0 );
		// may not set sv_maxclients directly, always set latched
		Cvar_SetLatched( "sv_maxclients", "8" );
		cmd += 2;
		cheat = qfalse;
		killBots = qtrue;
	}
	else {
		if ( !Q_stricmp( cmd, "devmap" ) || !Q_stricmp( cmd, "spdevmap" ) ) {
			cheat = qtrue;
			killBots = qtrue;
		} else {
			cheat = qfalse;
			killBots = qfalse;
		}
		if( sv_gametype->integer == GT_SINGLE_PLAYER ) {
			Cvar_SetValue( "g_gametype", GT_FFA );
		}
	}

	if ( Cmd_Argc() > 2 ) {
		factoryId = Cmd_Argv( 2 );
		if ( factoryId && *factoryId ) {
			factoryOverride = SV_FactoryFindById( factoryId );
			if ( !factoryOverride ) {
				Com_Printf( "Invalid factory specified.\n" );
				return;
			}
			if ( !cheat && !SV_MapSupportsGametype( map, factoryOverride->baseGametype ) ) {
				Com_Printf( "Map not supported for this gametype.\n" );
				return;
			}
		}
	}

	// save the map name here cause on a map restart we reload the q3config.cfg
	// and thus nuke the arguments of the map command
	Q_strncpyz(mapname, map, sizeof(mapname));

	if ( factoryOverride ) {
		Cvar_Set( "g_factory", factoryOverride->id );
	}

	// start up the map
	SV_SpawnServer( mapname, killBots );

	// set the cheat value
	// if the level was started with "map <levelname>", then
	// cheats will not be allowed.  If started with "devmap <levelname>"
	// then cheats will be allowed
	if ( cheat ) {
		Cvar_Set( "sv_cheats", "1" );
	} else {
		Cvar_Set( "sv_cheats", "0" );
	}
}

/*
================
SV_MapRestart_f

Completely restarts a level, but doesn't send a new gamestate to the clients.
This allows fair starts with variable load times.
================
*/
static void SV_MapRestart_f( void ) {
	int			i;
	client_t	*client;
	char		*denied;
	qboolean	isBot;
	int			delay;

	// make sure we aren't restarting twice in the same frame
	if ( com_frameTime == sv.serverId ) {
		return;
	}

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( sv.restartTime ) {
		return;
	}

	if ( SV_HandleQuitOnExitLevel( "map_restart" ) ) {
		return;
	}

	if (Cmd_Argc() > 1 ) {
		delay = atoi( Cmd_Argv(1) );
	}
	else {
		delay = 5;
	}
	if( delay && !Cvar_VariableValue("g_doWarmup") ) {
		sv.restartTime = svs.time + delay * 1000;
		SV_SetConfigstring( CS_WARMUP, va("%i", sv.restartTime) );
		return;
	}

	if ( !SV_CheckWarmupReadiness( qtrue ) ) {
		sv.restartTime = svs.time + 1000;
		return;
	}

	// check for changes in variables that can't just be restarted
	// check for maxclients change
	if ( sv_maxclients->modified || sv_gametype->modified ) {
		char	mapname[MAX_QPATH];

		Com_Printf( "variable change -- restarting.\n" );
		// restart the map the slow way
		Q_strncpyz( mapname, Cvar_VariableString( "mapname" ), sizeof( mapname ) );

		SV_SpawnServer( mapname, qfalse );
		return;
	}

	// toggle the server bit so clients can detect that a
	// map_restart has happened
	svs.snapFlagServerBit ^= SNAPFLAG_SERVERCOUNT;

	// generate a new serverid	
	// TTimo - don't update restartedserverId there, otherwise we won't deal correctly with multiple map_restart
	sv.serverId = com_frameTime;
	Cvar_Set( "sv_serverid", va("%i", sv.serverId ) );

	// reset all the vm data in place without changing memory allocation
	// note that we do NOT set sv.state = SS_LOADING, so configstrings that
	// had been changed from their default values will generate broadcast updates
	sv.state = SS_LOADING;
	sv.restarting = qtrue;

	SV_RestartGameProgs();

	// run a few frames to allow everything to settle
	for ( i = 0 ;i < 3 ; i++ ) {
		VM_Call( gvm, GAME_RUN_FRAME, svs.time );
		svs.time += 100;
	}

	sv.state = SS_GAME;
	sv.restarting = qfalse;

	// connect and begin all the clients
	for (i=0 ; i<sv_maxclients->integer ; i++) {
		client = &svs.clients[i];

		// send the new gamestate to all connected clients
		if ( client->state < CS_CONNECTED) {
			continue;
		}

		isBot = SV_ClientIsBot( client );

		// add the map_restart command
		SV_AddServerCommand( client, "map_restart\n" );

		// connect the client again, without the firstTime flag
		denied = VM_ExplicitArgPtr( gvm, VM_Call( gvm, GAME_CLIENT_CONNECT, i, qfalse, isBot ) );
		if ( denied ) {
			// this generally shouldn't happen, because the client
			// was connected before the level change
			SV_DropClient( client, denied );
			Com_Printf( "SV_MapRestart_f(%d): dropped client %i - denied!\n", delay, i ); // bk010125
			continue;
		}

		client->state = CS_ACTIVE;

		SV_ClientEnterWorld( client, &client->lastUsercmd );
	}	

	// run another frame to allow things to look at all the players
	VM_Call( gvm, GAME_RUN_FRAME, svs.time );
	svs.time += 100;
}

//===============================================================

/*
==================
SV_Kick_f

Kick a user off of the server  FIXME: move to game
==================
*/
static void SV_Kick_f( void ) {
	client_t	*cl;
	int			i;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( Cmd_Argc() != 2 ) {
		Com_Printf ("Usage: kick <player name>\nkick all = kick everyone\nkick allbots = kick all bots\n");
		return;
	}

	cl = SV_GetPlayerByName();
	if ( !cl ) {
		if ( !Q_stricmp(Cmd_Argv(1), "all") ) {
			for ( i=0, cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++ ) {
				if ( !cl->state ) {
					continue;
				}
				if( cl->netchan.remoteAddress.type == NA_LOOPBACK ) {
					continue;
				}
				SV_DropClient( cl, "was kicked" );
				cl->lastPacketTime = svs.time;	// in case there is a funny zombie
			}
		}
		else if ( !Q_stricmp(Cmd_Argv(1), "allbots") ) {
			for ( i=0, cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++ ) {
				if ( !cl->state ) {
					continue;
				}
				if( cl->netchan.remoteAddress.type != NA_BOT ) {
					continue;
				}
				SV_DropClient( cl, "was kicked" );
				cl->lastPacketTime = svs.time;	// in case there is a funny zombie
			}
		}
		return;
	}
	if( cl->netchan.remoteAddress.type == NA_LOOPBACK ) {
		SV_SendServerCommand(NULL, "print \"%s\"", "Cannot kick host player\n");
		return;
	}

	SV_DropClient( cl, "was kicked" );
	cl->lastPacketTime = svs.time;	// in case there is a funny zombie
}

/*
==================
SV_Ban_f

Ban a user from being able to play on this server through the auth
server
==================
*/
static void SV_Ban_f( void ) {
	client_t	*cl;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( Cmd_Argc() != 2 ) {
		Com_Printf ("Usage: banUser <player name>\n");
		return;
	}

	cl = SV_GetPlayerByName();

	if (!cl) {
		return;
	}

	if( cl->netchan.remoteAddress.type == NA_LOOPBACK ) {
		SV_SendServerCommand(NULL, "print \"%s\"", "Cannot kick host player\n");
		return;
	}

	// look up the authorize server's IP
	if ( !svs.authorizeAddress.ip[0] && svs.authorizeAddress.type != NA_BAD ) {
		Com_Printf( "Resolving %s\n", AUTHORIZE_SERVER_NAME );
		if ( !NET_StringToAdr( AUTHORIZE_SERVER_NAME, &svs.authorizeAddress ) ) {
			Com_Printf( "Couldn't resolve address\n" );
			return;
		}
		svs.authorizeAddress.port = BigShort( PORT_AUTHORIZE );
		Com_Printf( "%s resolved to %i.%i.%i.%i:%i\n", AUTHORIZE_SERVER_NAME,
			svs.authorizeAddress.ip[0], svs.authorizeAddress.ip[1],
			svs.authorizeAddress.ip[2], svs.authorizeAddress.ip[3],
			BigShort( svs.authorizeAddress.port ) );
	}

	// otherwise send their ip to the authorize server
	if ( svs.authorizeAddress.type != NA_BAD ) {
		NET_OutOfBandPrint( NS_SERVER, svs.authorizeAddress,
			"banUser %i.%i.%i.%i", cl->netchan.remoteAddress.ip[0], cl->netchan.remoteAddress.ip[1], 
								   cl->netchan.remoteAddress.ip[2], cl->netchan.remoteAddress.ip[3] );
		Com_Printf("%s was banned from coming back\n", cl->name);
	}
}

/*
==================
SV_BanNum_f

Ban a user from being able to play on this server through the auth
server
==================
*/
static void SV_BanNum_f( void ) {
	client_t	*cl;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( Cmd_Argc() != 2 ) {
		Com_Printf ("Usage: banClient <client number>\n");
		return;
	}

	cl = SV_GetPlayerByNum();
	if ( !cl ) {
		return;
	}
	if( cl->netchan.remoteAddress.type == NA_LOOPBACK ) {
		SV_SendServerCommand(NULL, "print \"%s\"", "Cannot kick host player\n");
		return;
	}

	// look up the authorize server's IP
	if ( !svs.authorizeAddress.ip[0] && svs.authorizeAddress.type != NA_BAD ) {
		Com_Printf( "Resolving %s\n", AUTHORIZE_SERVER_NAME );
		if ( !NET_StringToAdr( AUTHORIZE_SERVER_NAME, &svs.authorizeAddress ) ) {
			Com_Printf( "Couldn't resolve address\n" );
			return;
		}
		svs.authorizeAddress.port = BigShort( PORT_AUTHORIZE );
		Com_Printf( "%s resolved to %i.%i.%i.%i:%i\n", AUTHORIZE_SERVER_NAME,
			svs.authorizeAddress.ip[0], svs.authorizeAddress.ip[1],
			svs.authorizeAddress.ip[2], svs.authorizeAddress.ip[3],
			BigShort( svs.authorizeAddress.port ) );
	}

	// otherwise send their ip to the authorize server
	if ( svs.authorizeAddress.type != NA_BAD ) {
		NET_OutOfBandPrint( NS_SERVER, svs.authorizeAddress,
			"banUser %i.%i.%i.%i", cl->netchan.remoteAddress.ip[0], cl->netchan.remoteAddress.ip[1], 
								   cl->netchan.remoteAddress.ip[2], cl->netchan.remoteAddress.ip[3] );
		Com_Printf("%s was banned from coming back\n", cl->name);
	}
}

/*
==================
SV_KickNum_f

Kick a user off of the server  FIXME: move to game
==================
*/
static void SV_KickNum_f( void ) {
	client_t	*cl;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( Cmd_Argc() != 2 ) {
		Com_Printf ("Usage: kicknum <client number>\n");
		return;
	}

	cl = SV_GetPlayerByNum();
	if ( !cl ) {
		return;
	}
	if( cl->netchan.remoteAddress.type == NA_LOOPBACK ) {
		SV_SendServerCommand(NULL, "print \"%s\"", "Cannot kick host player\n");
		return;
	}

	SV_DropClient( cl, "was kicked" );
	cl->lastPacketTime = svs.time;	// in case there is a funny zombie
}

/*
================
SV_Status_f
================
*/
static void SV_Status_f( void ) {
	int			i, j, l;
	client_t	*cl;
	playerState_t	*ps;
	const char		*s;
	int			ping;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	Com_Printf ("map: %s\n", sv_mapname->string );

	Com_Printf ("num score ping name            lastmsg address               qport rate\n");
	Com_Printf ("--- ----- ---- --------------- ------- --------------------- ----- -----\n");
	for (i=0,cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++)
	{
		if (!cl->state)
			continue;
		Com_Printf ("%3i ", i);
		ps = SV_GameClientNum( i );
		Com_Printf ("%5i ", ps->persistant[PERS_SCORE]);

		if (cl->state == CS_CONNECTED)
			Com_Printf ("CNCT ");
		else if (cl->state == CS_ZOMBIE)
			Com_Printf ("ZMBI ");
		else
		{
			ping = cl->ping < 9999 ? cl->ping : 9999;
			Com_Printf ("%4i ", ping);
		}

		Com_Printf ("%s", cl->name);
    // TTimo adding a ^7 to reset the color
    // NOTE: colored names in status breaks the padding (WONTFIX)
    Com_Printf ("^7");
		l = 16 - strlen(cl->name);
		for (j=0 ; j<l ; j++)
			Com_Printf (" ");

		Com_Printf ("%7i ", svs.time - cl->lastPacketTime );

		s = NET_AdrToString( cl->netchan.remoteAddress );
		Com_Printf ("%s", s);
		l = 22 - strlen(s);
		for (j=0 ; j<l ; j++)
			Com_Printf (" ");
		
		Com_Printf ("%5i", cl->netchan.qport);

		Com_Printf (" %5i", cl->rate);

		Com_Printf ("\n");
	}
	Com_Printf ("\n");
}

/*
==================
SV_ConSay_f
==================
*/
static void SV_ConSay_f(void) {
	char	*p;
	char	text[1024];

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( Cmd_Argc () < 2 ) {
		return;
	}

	strcpy (text, "console: ");
	p = Cmd_Args();

	if ( *p == '"' ) {
		p++;
		p[strlen(p)-1] = 0;
	}

	strcat(text, p);

	SV_SendServerCommand(NULL, "chat \"%s\n\"", text);
}


/*
==================
SV_Heartbeat_f

Also called by SV_DropClient, SV_DirectConnect, and SV_SpawnServer
==================
*/
void SV_Heartbeat_f( void ) {
	svs.nextHeartbeatTime = -9999999;
}


/*
===========
SV_Serverinfo_f

Examine the serverinfo string
===========
*/
static void SV_Serverinfo_f( void ) {
	Com_Printf ("Server info settings:\n");
	Info_Print ( Cvar_InfoString( CVAR_SERVERINFO ) );
}


/*
===========
SV_Systeminfo_f

Examine or change the serverinfo string
===========
*/
static void SV_Systeminfo_f( void ) {
	Com_Printf ("System info settings:\n");
	Info_Print ( Cvar_InfoString( CVAR_SYSTEMINFO ) );
}


/*
===========
SV_DumpUser_f

Examine all a users info strings FIXME: move to game
===========
*/
static void SV_DumpUser_f( void ) {
	client_t	*cl;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( Cmd_Argc() != 2 ) {
		Com_Printf ("Usage: info <userid>\n");
		return;
	}

	cl = SV_GetPlayerByName();
	if ( !cl ) {
		return;
	}

	Com_Printf( "userinfo\n" );
	Com_Printf( "--------\n" );
	Info_Print( cl->userinfo );
}


/*
=================
SV_KillServer
=================
*/
static void SV_KillServer_f( void ) {
	SV_Shutdown( "killserver" );
}

//===========================================================

/*
==================
SV_AddOperatorCommands
==================
*/
void SV_AddOperatorCommands( void ) {
	static qboolean	initialized;

	if ( initialized ) {
		return;
	}
	initialized = qtrue;

	Cmd_AddCommand ("heartbeat", SV_Heartbeat_f);
	Cmd_AddCommand ("kick", SV_Kick_f);
	Cmd_AddCommand ("banUser", SV_Ban_f);
	Cmd_AddCommand ("banClient", SV_BanNum_f);
	Cmd_AddCommand ("clientkick", SV_KickNum_f);
	Cmd_AddCommand ("status", SV_Status_f);
	Cmd_AddCommand ("serverinfo", SV_Serverinfo_f);
	Cmd_AddCommand ("systeminfo", SV_Systeminfo_f);
	Cmd_AddCommand ("dumpuser", SV_DumpUser_f);
	Cmd_AddCommand ("map_restart", SV_MapRestart_f);
	Cmd_AddCommand ("sectorlist", SV_SectorList_f);
	Cmd_AddCommand ("map", SV_Map_f);
#ifndef PRE_RELEASE_DEMO
	Cmd_AddCommand ("devmap", SV_Map_f);
	Cmd_AddCommand ("spmap", SV_Map_f);
	Cmd_AddCommand ("spdevmap", SV_Map_f);
#endif
	Cmd_AddCommand ("killserver", SV_KillServer_f);
	if( com_dedicated->integer ) {
		Cmd_AddCommand ("say", SV_ConSay_f);
	}
}

/*
==================
SV_RemoveOperatorCommands
==================
*/
void SV_RemoveOperatorCommands( void ) {
#if 0
	// removing these won't let the server start again
	Cmd_RemoveCommand ("heartbeat");
	Cmd_RemoveCommand ("kick");
	Cmd_RemoveCommand ("banUser");
	Cmd_RemoveCommand ("banClient");
	Cmd_RemoveCommand ("status");
	Cmd_RemoveCommand ("serverinfo");
	Cmd_RemoveCommand ("systeminfo");
	Cmd_RemoveCommand ("dumpuser");
	Cmd_RemoveCommand ("map_restart");
	Cmd_RemoveCommand ("sectorlist");
	Cmd_RemoveCommand ("say");
#endif
}

