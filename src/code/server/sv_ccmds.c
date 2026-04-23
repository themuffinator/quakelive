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
#include "../../common/platform/platform_steamworks.h"

#define SV_FACTORY_MAX_JSON_STRING        4096
#define SV_FACTORY_FILE_LIST_BUFFER       4096

#define SV_MAX_MAP_GAMETYPE_ALIASES       3
#define SV_MAP_POOL_FILE_BYTES            0x8000
#define SV_MAX_MAP_POOL_ENTRIES           1024

typedef struct svFactoryParseState_s {
	const char *cursor;
	const char *end;
	const char *filename;
	int line;
} svFactoryParseState_t;

typedef struct svFactoryOverride_s {
	char *name;
	char *value;
	struct svFactoryOverride_s *next;
} svFactoryOverride_t;

typedef struct svFactoryDefinition_s {
	char *id;
	char *title;
	gametype_t baseGametype;
	char *sourceFile;
	svFactoryOverride_t *overrides;
	int overrideCount;
	struct svFactoryDefinition_s *next;
} svFactoryDefinition_t;

typedef struct svMapPoolEntry_s {
	char mapName[MAX_QPATH];
	char mapTitle[MAX_INFO_VALUE];
	char factoryId[MAX_QPATH];
	char factoryTitle[MAX_INFO_VALUE];
} svMapPoolEntry_t;

static qboolean s_svFactoryRegistryLoaded = qfalse;
static svFactoryDefinition_t *s_svFactoryList = NULL;
static const svFactoryDefinition_t *s_svCurrentFactory = NULL;
static svFactoryDefinition_t *s_svDetachedCurrentFactory = NULL;
static qboolean s_svArenaRegistryLoaded = qfalse;
static int s_svNumArenaInfos = 0;
static char *s_svArenaInfos[MAX_ARENAS];
static int s_svMapPoolCount = 0;
static svMapPoolEntry_t s_svMapPool[SV_MAX_MAP_POOL_ENTRIES];

static void SV_FactoryLoadSupplementalFiles( void );

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
SV_FactoryFreeOverrides

Releases a linked list of parsed factory CVar overrides.
=============
*/
static void SV_FactoryFreeOverrides( svFactoryOverride_t *override ) {
	svFactoryOverride_t *next;

	while ( override ) {
		next = override->next;
		if ( override->name ) {
			Z_Free( override->name );
		}
		if ( override->value ) {
			Z_Free( override->value );
		}
		Z_Free( override );
		override = next;
	}
}

/*
=============
SV_FactoryFreeDefinition

Releases a parsed factory definition that is not retained by the registry.
=============
*/
static void SV_FactoryFreeDefinition( svFactoryDefinition_t *definition ) {
	if ( !definition ) {
		return;
	}

	if ( definition->id ) {
		Z_Free( definition->id );
	}
	if ( definition->title ) {
		Z_Free( definition->title );
	}
	if ( definition->sourceFile ) {
		Z_Free( definition->sourceFile );
	}

	SV_FactoryFreeOverrides( definition->overrides );
	Z_Free( definition );
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
	if ( !state || !state->cursor || state->cursor >= state->end ) {
		return qfalse;
	}

	SV_FactorySkipWhitespace( state );
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
															SV_FactorySkipWhitespace( state );
															if ( state->cursor < state->end && *state->cursor == '}' ) {
																state->cursor++;
																return qtrue;
															}
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
															SV_FactorySkipWhitespace( state );
															if ( state->cursor < state->end && *state->cursor == ']' ) {
																state->cursor++;
																return qtrue;
															}
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
													SV_FactoryParseCvarOverrides

													Parses the "cvars" object for a factory definition.
													=============
													*/
													static qboolean SV_FactoryParseCvarOverrides( svFactoryParseState_t *state, svFactoryDefinition_t *definition ) {
														svFactoryOverride_t *tail = NULL;

														if ( !definition || !SV_FactoryParseExpectedChar( state, '{' ) ) {
															return qfalse;
														}

														SV_FactorySkipWhitespace( state );
														if ( state->cursor < state->end && *state->cursor == '}' ) {
															state->cursor++;
															return qtrue;
														}

														while ( state->cursor < state->end ) {
															char *name = SV_FactoryParseJsonString( state );
															char *value;
															svFactoryOverride_t *override;

															if ( !name ) {
																return qfalse;
															}

															if ( !SV_FactoryParseExpectedChar( state, ':' ) ) {
																Z_Free( name );
																return qfalse;
															}

															SV_FactorySkipWhitespace( state );
															if ( state->cursor >= state->end ) {
																Z_Free( name );
																SV_FactoryReportParseError( state, "unexpected end of cvars" );
																return qfalse;
															}

															if ( *state->cursor == '"' ) {
																value = SV_FactoryParseJsonString( state );
															} else {
																value = SV_FactoryParseLiteralString( state );
															}

															if ( !value ) {
																Z_Free( name );
																return qfalse;
															}

															override = ( svFactoryOverride_t * )Z_Malloc( sizeof( svFactoryOverride_t ) );
															if ( !override ) {
																Z_Free( name );
																Z_Free( value );
																return qfalse;
															}

															override->name = name;
															override->value = value;
															override->next = NULL;

															if ( tail ) {
																tail->next = override;
															} else {
																definition->overrides = override;
															}

															tail = override;
															definition->overrideCount++;

															SV_FactorySkipWhitespace( state );
															if ( state->cursor >= state->end ) {
																SV_FactoryReportParseError( state, "unterminated cvars object" );
																return qfalse;
															}

															if ( *state->cursor == ',' ) {
																state->cursor++;
																SV_FactorySkipWhitespace( state );
																if ( state->cursor < state->end && *state->cursor == '}' ) {
																	state->cursor++;
																	return qtrue;
																}
																continue;
															}

															if ( *state->cursor == '}' ) {
																state->cursor++;
																return qtrue;
															}

															SV_FactoryReportParseError( state, "expected ',' or '}'" );
															return qfalse;
														}

														SV_FactoryReportParseError( state, "unterminated cvars object" );
														return qfalse;
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
		{ "obelisk", GT_OBELISK },
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
														char *title;
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
														definition->title = NULL;
														definition->baseGametype = GT_FFA;
														definition->overrides = NULL;
														definition->overrideCount = 0;
														definition->next = NULL;

														id = NULL;
														title = NULL;
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
															} else if ( !Q_stricmp( key, "title" ) ) {
																if ( title ) {
																	Z_Free( title );
																}
																title = SV_FactoryParseJsonString( state );
															} else if ( !Q_stricmp( key, "basegt" ) ) {
																if ( basegt ) {
																	Z_Free( basegt );
																}
																basegt = SV_FactoryParseJsonString( state );
															} else if ( !Q_stricmp( key, "cvars" ) ) {
																if ( !SV_FactoryParseCvarOverrides( state, definition ) ) {
																	Z_Free( key );
																	goto fail;
																}
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
															SV_FactorySkipWhitespace( state );
															if ( state->cursor < state->end && *state->cursor == '}' ) {
																state->cursor++;
																break;
															}
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
														definition->title = title;
														Z_Free( basegt );
														return definition;

														fail:
														if ( id ) {
															Z_Free( id );
														}
														if ( title ) {
															Z_Free( title );
														}
														if ( basegt ) {
															Z_Free( basegt );
														}
														SV_FactoryFreeDefinition( definition );
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
																SV_FactoryFreeDefinition( definition );
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

													Reads factory definitions from a JSON document (array or singleton object).
													=============
													*/
													static int SV_FactoryParseFactoriesBuffer( const char *filename, const char *buffer, int length ) {
														svFactoryParseState_t state;
														int count;
														svFactoryDefinition_t *definition;

														if ( !buffer || length <= 0 ) {
															return 0;
														}

														state.cursor = buffer;
														state.end = buffer + length;
														state.filename = filename;
														state.line = 1;

														SV_FactorySkipWhitespace( &state );
														if ( state.cursor >= state.end || *state.cursor == '\0' ) {
															return 0;
														}

														count = 0;
														if ( *state.cursor == '{' ) {
															definition = SV_FactoryParseDefinition( &state, filename );
															if ( !definition ) {
																return 0;
															}
															if ( SV_FactoryRegisterDefinition( definition ) ) {
																count++;
															}
															SV_FactorySkipWhitespace( &state );
															if ( state.cursor < state.end ) {
																SV_FactorySkipWhitespace( &state );
																if ( state.cursor < state.end && *state.cursor == ',' ) {
																	state.cursor++;
																	SV_FactorySkipWhitespace( &state );
																}
																SV_FactoryReportParseError( &state, "trailing data after factory object" );
															}
															return count;
														}

														if ( !SV_FactoryParseExpectedChar( &state, '[' ) ) {
															SV_FactoryReportParseError( &state, "expected '[' or '{'" );
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
															SV_FactorySkipWhitespace( &state );
															if ( state.cursor < state.end && *state.cursor == ']' ) {
																state.cursor++;
																return count;
															}
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
	int totalCount = 0;
	const svFactoryDefinition_t *factory;

	length = FS_FOpenFileRead( filename, &file, qfalse );
	if ( length <= 0 ) {
		Com_Printf( "^1file not found: %s\n^7", filename );
		return qfalse;
	}
	if ( length >= SV_FACTORY_MAX_JSON_STRING * 64 ) {
		Com_Printf( "^1file too large: %s is %i, max allowed is %i^7", filename, length, SV_FACTORY_MAX_JSON_STRING * 64 );
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

	for ( factory = s_svFactoryList; factory; factory = factory->next ) {
		totalCount++;
	}

	Com_Printf( "loaded factories from %s, total %i\n", filename, totalCount );
	return qtrue;
}

/*
=============
SV_FactoryLoadAllDefinitions

Loads the retail base factories file plus any supplemental `*.factories`
definitions shipped alongside it.
=============
*/
static void SV_FactoryLoadAllDefinitions( void ) {
	SV_FactoryLoadFile( "scripts/factories.txt" );
	SV_FactoryLoadSupplementalFiles();
}

/*
=============
SV_FactoryLoadSupplementalFiles

Loads optional `*.factories` files from the scripts directory, falling back to
the singular `*.factory` suffix when no plural supplements are present.
=============
*/
static void SV_FactoryLoadSupplementalFiles( void ) {
														char fileList[SV_FACTORY_FILE_LIST_BUFFER];
														char *cursor;
	int count;
	int index;

	count = FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );
	if ( count <= 0 ) {
		count = FS_GetFileList( "scripts", ".factory", fileList, sizeof( fileList ) );
	}
	cursor = fileList;
	for ( index = 0; index < count; index++ ) {
		int length = strlen( cursor );
		char path[MAX_QPATH];

															if ( length <= 0 ) {
																cursor++;
																continue;
															}

															Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
															SV_FactoryLoadFile( path );
															cursor += length + 1;
	}
}

/*
=============
SV_FactoryCloneOverrides

Creates a deep copy of a factory override list so the active selection can
survive retail registry reloads.
=============
*/
static svFactoryOverride_t *SV_FactoryCloneOverrides( const svFactoryOverride_t *source ) {
	svFactoryOverride_t *head = NULL;
	svFactoryOverride_t *tail = NULL;

	while ( source ) {
		svFactoryOverride_t *copy = ( svFactoryOverride_t * )Z_Malloc( sizeof( *copy ) );

		if ( !copy ) {
			SV_FactoryFreeOverrides( head );
			return NULL;
		}

		copy->name = SV_FactoryCopyString( source->name );
		copy->value = SV_FactoryCopyString( source->value );
		copy->next = NULL;

		if ( tail ) {
			tail->next = copy;
		} else {
			head = copy;
		}

		tail = copy;
		source = source->next;
	}

	return head;
}

/*
=============
SV_FactoryCloneDefinition

Duplicates a parsed factory definition so the current selection can outlive a
registry rebuild.
=============
*/
static svFactoryDefinition_t *SV_FactoryCloneDefinition( const svFactoryDefinition_t *source ) {
	svFactoryDefinition_t *copy;

	if ( !source ) {
		return NULL;
	}

	copy = ( svFactoryDefinition_t * )Z_Malloc( sizeof( *copy ) );
	if ( !copy ) {
		return NULL;
	}

	Com_Memset( copy, 0, sizeof( *copy ) );
	copy->id = SV_FactoryCopyString( source->id );
	copy->title = SV_FactoryCopyString( source->title );
	copy->baseGametype = source->baseGametype;
	copy->sourceFile = SV_FactoryCopyString( source->sourceFile );
	copy->overrideCount = source->overrideCount;
	copy->overrides = SV_FactoryCloneOverrides( source->overrides );
	return copy;
}

/*
=============
SV_FactoryReleaseDetachedCurrentSelection

Frees the preserved current-factory copy created during a retail reload once
its overrides are no longer needed.
=============
*/
static void SV_FactoryReleaseDetachedCurrentSelection( void ) {
	if ( !s_svDetachedCurrentFactory ) {
		return;
	}

	if ( s_svCurrentFactory == s_svDetachedCurrentFactory ) {
		s_svCurrentFactory = NULL;
	}

	SV_FactoryFreeDefinition( s_svDetachedCurrentFactory );
	s_svDetachedCurrentFactory = NULL;
}

/*
=============
SV_FactoryResetRegistry

Clears the loaded factory registry, optionally preserving the active selection
so running servers keep the retail-applied ruleset until the next map change.
=============
*/
static void SV_FactoryResetRegistry( qboolean preserveCurrent ) {
	svFactoryDefinition_t *definition = s_svFactoryList;
	const svFactoryDefinition_t *currentFactory = s_svCurrentFactory;
	svFactoryDefinition_t *preservedFactory = NULL;

	if ( preserveCurrent && currentFactory && currentFactory->id ) {
		preservedFactory = SV_FactoryCloneDefinition( currentFactory );
		if ( preservedFactory ) {
			Com_Printf( "not clearing currently loaded factory id %s, continuing\n", currentFactory->id );
		}
	}

	SV_FactoryReleaseDetachedCurrentSelection();
	s_svFactoryList = NULL;
	s_svFactoryRegistryLoaded = qfalse;
	s_svDetachedCurrentFactory = preservedFactory;

	while ( definition ) {
		svFactoryDefinition_t *next = definition->next;

		SV_FactoryFreeDefinition( definition );
		definition = next;
	}

	s_svCurrentFactory = s_svDetachedCurrentFactory;
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

	SV_FactoryLoadAllDefinitions();
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
													SV_FactoryPrintValidList

													Prints the retail host factory list used by the map usage path.
													=============
													*/
													static void SV_FactoryPrintValidList( void ) {
														const svFactoryDefinition_t *factory;

														SV_FactoryEnsureRegistryLoaded();

														Com_Printf( "Valid factories: " );
														for ( factory = s_svFactoryList; factory; factory = factory->next ) {
															if ( factory->id && factory->id[0] && factory->id[0] != '_' ) {
																Com_Printf( "%s ", factory->id );
															}
														}
														Com_Printf( "\n" );
													}

													/*
													=============
													SV_FactoryResetOverrides

													Resets every override contributed by the supplied host-side factory selection.
													=============
													*/
													static void SV_FactoryResetOverrides( const svFactoryDefinition_t *factory ) {
														const svFactoryOverride_t *override;

														if ( !factory ) {
															return;
														}

														for ( override = factory->overrides; override; override = override->next ) {
															if ( override->name && override->name[0] ) {
																Cvar_Reset( override->name );
															}
														}
													}

													/*
													=============
													SV_FactoryApplySelection

													Applies the selected host-side factory before the next map bootstraps qagame.
													=============
													*/
static void SV_FactoryApplySelection( const svFactoryDefinition_t *factory ) {
	const svFactoryOverride_t *override;
	char gametypeBuffer[8];
	const svFactoryDefinition_t *previousFactory;

	if ( s_svCurrentFactory == factory ) {
		return;
	}

	previousFactory = s_svCurrentFactory;
	SV_FactoryResetOverrides( previousFactory );
	if ( previousFactory == s_svDetachedCurrentFactory ) {
		SV_FactoryReleaseDetachedCurrentSelection();
	}

	for ( override = factory ? factory->overrides : NULL; override; override = override->next ) {
		if ( override->name && override->value ) {
			Cvar_Set( override->name, override->value );
															}
														}

														if ( factory ) {
															Com_sprintf( gametypeBuffer, sizeof( gametypeBuffer ), "%i", factory->baseGametype );
															Cvar_Set( "g_gametype", gametypeBuffer );
															Cvar_Set( "g_factory", factory->id ? factory->id : "" );
															Cvar_Set( "g_factoryTitle", factory->title ? factory->title : "" );
														} else {
															Cvar_Set( "g_factory", "" );
															Cvar_Set( "g_factoryTitle", "" );
														}

														s_svCurrentFactory = factory;
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
SV_ClearArenaRegistry

Releases the cached host arena metadata so it can be rebuilt from disk.
=============
*/
static void SV_ClearArenaRegistry( void ) {
	int index;

	for ( index = 0; index < s_svNumArenaInfos; index++ ) {
		if ( s_svArenaInfos[index] ) {
			Z_Free( s_svArenaInfos[index] );
			s_svArenaInfos[index] = NULL;
		}
	}

	s_svNumArenaInfos = 0;
	s_svArenaRegistryLoaded = qfalse;
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
		Com_Printf( "^1file not found: %s\n", filename );
		return;
	}
	if ( length >= MAX_ARENAS_TEXT ) {
		Com_Printf( "^1file too large: %s is %i, max allowed is %i^7", filename, length, MAX_ARENAS_TEXT );
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
SV_LoadArenas

Initialises the cached arena metadata used for retail map validation.
=============
*/
static void SV_LoadArenas( void ) {
	char fileList[MAX_ARENAS_TEXT];
	char *cursor;
	int count;
	int index;

	SV_ClearArenaRegistry();
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

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		SV_LoadArenasFromFile( path );
		cursor += length + 1;
	}

	s_svArenaRegistryLoaded = qtrue;
	Com_Printf( "%i arenas parsed\n", s_svNumArenaInfos );
}

/*
=============
SV_EnsureArenaRegistryLoaded

Initialises the cached arena metadata used for gametype validation.
=============
*/
static void SV_EnsureArenaRegistryLoaded( void ) {
	if ( s_svArenaRegistryLoaded ) {
		return;
	}

	SV_LoadArenas();
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

	SV_EnsureArenaRegistryLoaded();
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
=============
SV_GetArenaDisplayTitle

Returns the host-visible long title for the supplied map, falling back to the
raw map token when the arena catalog does not expose one.
=============
*/
static void SV_GetArenaDisplayTitle( const char *mapName, char *buffer, int bufferSize ) {
	const char *arenaInfo;
	const char *longName;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !mapName || !*mapName ) {
		return;
	}

	arenaInfo = SV_GetArenaInfoByMap( mapName );
	if ( arenaInfo ) {
		longName = Info_ValueForKey( arenaInfo, "longname" );
		if ( longName && *longName ) {
			Q_strncpyz( buffer, longName, bufferSize );
			return;
		}
	}

	Q_strncpyz( buffer, mapName, bufferSize );
}

/*
=============
SV_MapPoolTrimToken

Strips leading and trailing whitespace from a parsed map-pool token.
=============
*/
static void SV_MapPoolTrimToken( char *token ) {
	char *start;
	char *end;

	if ( !token ) {
		return;
	}

	start = token;
	while ( *start == ' ' || *start == '\t' ) {
		start++;
	}

	end = start + strlen( start );
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
SV_MapPoolClear

Resets the loaded retail map-pool cache.
=============
*/
static void SV_MapPoolClear( void ) {
	Com_Memset( s_svMapPool, 0, sizeof( s_svMapPool ) );
	s_svMapPoolCount = 0;
}

/*
=============
SV_MapPoolAppendEntry

Appends one validated retail map-pool entry to the host cache.
=============
*/
static void SV_MapPoolAppendEntry( const char *mapName, const char *mapTitle, const svFactoryDefinition_t *factory ) {
	svMapPoolEntry_t *entry;

	if ( s_svMapPoolCount >= SV_MAX_MAP_POOL_ENTRIES || !mapName || !*mapName || !factory ) {
		return;
	}

	entry = &s_svMapPool[s_svMapPoolCount++];
	Com_Memset( entry, 0, sizeof( *entry ) );
	Q_strncpyz( entry->mapName, mapName, sizeof( entry->mapName ) );
	Q_strncpyz( entry->mapTitle, ( mapTitle && *mapTitle ) ? mapTitle : mapName, sizeof( entry->mapTitle ) );
	Q_strncpyz( entry->factoryId, factory->id ? factory->id : "", sizeof( entry->factoryId ) );
	Q_strncpyz( entry->factoryTitle, factory->title ? factory->title : "", sizeof( entry->factoryTitle ) );
}

/*
=============
SV_MapPoolLoadLine

Parses and validates one retail map-pool definition line.
=============
*/
static void SV_MapPoolLoadLine( const char *line ) {
	char lineBuffer[MAX_STRING_CHARS * 2];
	char *mapSeparator;
	char *comment;
	char *mapToken;
	char *factoryToken;
	char mapPath[MAX_QPATH];
	char mapTitle[MAX_INFO_VALUE];
	const svFactoryDefinition_t *factory;

	if ( !line ) {
		return;
	}

	Q_strncpyz( lineBuffer, line, sizeof( lineBuffer ) );
	mapToken = lineBuffer;
	while ( *mapToken == ' ' || *mapToken == '\t' ) {
		mapToken++;
	}

	if ( !*mapToken || *mapToken == '#' ) {
		return;
	}

	comment = strchr( mapToken, '#' );
	if ( comment ) {
		*comment = '\0';
	}

	mapSeparator = strchr( mapToken, '|' );
	if ( !mapSeparator ) {
		Com_Printf( "^1map rotation item missing map or factory name, skipping: %s\n^7", line );
		return;
	}

	*mapSeparator = '\0';
	factoryToken = mapSeparator + 1;

	SV_MapPoolTrimToken( mapToken );
	SV_MapPoolTrimToken( factoryToken );
	if ( !mapToken[0] || !factoryToken[0] ) {
		Com_Printf( "^1map rotation item missing map or factory name, skipping: %s\n^7", line );
		return;
	}

	factory = SV_FactoryFindById( factoryToken );
	if ( !factory || factoryToken[0] == '_' ) {
		Com_Printf( "^1invalid factory found in rotation, skipping: %s\n^7", line );
		return;
	}

	Com_sprintf( mapPath, sizeof( mapPath ), "maps/%s.bsp", mapToken );
	if ( FS_ReadFile( mapPath, NULL ) == -1 ) {
		Com_Printf( "^1map doesn't exist, skipping: %s\n^7", mapToken );
		return;
	}

	if ( !SV_MapSupportsGametype( mapToken, factory->baseGametype ) ) {
		Com_Printf( "^1map isn't valid for factory gametype, skipping: %s\n^7", line );
		return;
	}

	SV_GetArenaDisplayTitle( mapToken, mapTitle, sizeof( mapTitle ) );
	SV_MapPoolAppendEntry( mapToken, mapTitle, factory );
}

/*
=============
SV_MapPoolLoadFromFile

Loads and validates the retail host map-pool file.
=============
*/
static qboolean SV_MapPoolLoadFromFile( const char *path ) {
	fileHandle_t file;
	int length;
	static char buffer[SV_MAP_POOL_FILE_BYTES];
	char *cursor;

	if ( !path || !*path ) {
		path = "mappool.txt";
	}

	length = FS_FOpenFileRead( path, &file, qfalse );
	if ( length <= 0 ) {
		Com_Printf( "^1rotation file not found: %s\n^7", path );
		return qfalse;
	}
	if ( length >= SV_MAP_POOL_FILE_BYTES ) {
		Com_Printf( "^1rotations file too large: %s is %i, max allowed is %i^7", path, length, SV_MAP_POOL_FILE_BYTES );
		FS_FCloseFile( file );
		return qfalse;
	}

	FS_Read( buffer, length, file );
	buffer[length] = '\0';
	FS_FCloseFile( file );

	SV_EnsureArenaRegistryLoaded();
	SV_FactoryEnsureRegistryLoaded();

	cursor = buffer;
	while ( *cursor && s_svMapPoolCount < SV_MAX_MAP_POOL_ENTRIES ) {
		char lineBuffer[MAX_STRING_CHARS * 2];
		int lineLength = 0;

		while ( cursor[lineLength] && cursor[lineLength] != '\n' && cursor[lineLength] != '\r'
			&& lineLength < sizeof( lineBuffer ) - 1 ) {
			lineBuffer[lineLength] = cursor[lineLength];
			lineLength++;
		}
		lineBuffer[lineLength] = '\0';
		SV_MapPoolLoadLine( lineBuffer );

		cursor += lineLength;
		while ( *cursor == '\n' || *cursor == '\r' ) {
			cursor++;
		}
	}

	Com_Printf( "loaded %i maps into the map pool\n", s_svMapPoolCount );
	return ( s_svMapPoolCount > 0 );
}

/*
=============
SV_MapPoolSelectRandomEntry

Returns a retail-style random entry from the loaded map pool, falling back to
`campgrounds` when the pool is empty.
=============
*/
static const svMapPoolEntry_t *SV_MapPoolSelectRandomEntry( void ) {
	static svMapPoolEntry_t fallbackEntry;
	int index;

	if ( s_svMapPoolCount <= 0 ) {
		Com_Memset( &fallbackEntry, 0, sizeof( fallbackEntry ) );
		Q_strncpyz( fallbackEntry.mapName, "campgrounds", sizeof( fallbackEntry.mapName ) );
		Q_strncpyz( fallbackEntry.mapTitle, "campgrounds", sizeof( fallbackEntry.mapTitle ) );
		if ( s_svCurrentFactory ) {
			Q_strncpyz( fallbackEntry.factoryId, s_svCurrentFactory->id ? s_svCurrentFactory->id : "", sizeof( fallbackEntry.factoryId ) );
			Q_strncpyz( fallbackEntry.factoryTitle, s_svCurrentFactory->title ? s_svCurrentFactory->title : "", sizeof( fallbackEntry.factoryTitle ) );
		}
		return &fallbackEntry;
	}

	index = ( rand() ^ Com_Milliseconds() ) % s_svMapPoolCount;
	if ( index < 0 ) {
		index = 0;
	}

	return &s_svMapPool[index];
}

/*
=============
SV_MapPoolUpdateNextMap

Refreshes the retail `nextmap` command from the loaded map-pool state.
=============
*/
static void SV_MapPoolUpdateNextMap( void ) {
	const svMapPoolEntry_t *entry;

	if ( s_svMapPoolCount <= 0 ) {
		Cvar_Set( "nextmap", "map_restart 0" );
		return;
	}

	entry = SV_MapPoolSelectRandomEntry();
	Cvar_Set( "nextmap", va( "map %s %s", entry->mapName, entry->factoryId ) );
}

/*
=============
SV_MapPoolBuildNextMapsCvar

Builds the retail `nextmaps` preview payload consumed by the downstream
intermission vote UI.
=============
*/
static void SV_MapPoolBuildNextMapsCvar( void ) {
	char nextmaps[MAX_STRING_CHARS];
	int slot = 0;
	int index;

	nextmaps[0] = '\0';

	if ( sv_includeCurrentMapInVote && sv_includeCurrentMapInVote->integer && s_svCurrentFactory ) {
		char currentMap[MAX_QPATH];
		char currentTitle[MAX_INFO_VALUE];

		Q_strncpyz( currentMap, Cvar_VariableString( "mapname" ), sizeof( currentMap ) );
		if ( currentMap[0] ) {
			SV_GetArenaDisplayTitle( currentMap, currentTitle, sizeof( currentTitle ) );
			Info_SetValueForKey( nextmaps, va( "map_%i", slot ), currentMap );
			Info_SetValueForKey( nextmaps, va( "title_%i", slot ), currentTitle );
			Info_SetValueForKey( nextmaps, va( "cfg_%i", slot ), s_svCurrentFactory->id ? s_svCurrentFactory->id : "" );
			Info_SetValueForKey( nextmaps, va( "gt_%i", slot ), s_svCurrentFactory->title ? s_svCurrentFactory->title : "" );
			slot++;
		}
	}

	if ( s_svMapPoolCount >= 4 ) {
		qboolean used[SV_MAX_MAP_POOL_ENTRIES];

		Com_Memset( used, 0, sizeof( used ) );
		while ( slot < 3 ) {
			const svMapPoolEntry_t *entry;

			index = ( rand() ^ Com_Milliseconds() ) % s_svMapPoolCount;
			if ( index < 0 ) {
				index = 0;
			}
			if ( used[index] ) {
				continue;
			}

			used[index] = qtrue;
			entry = &s_svMapPool[index];
			Info_SetValueForKey( nextmaps, va( "map_%i", slot ), entry->mapName );
			Info_SetValueForKey( nextmaps, va( "title_%i", slot ), entry->mapTitle );
			Info_SetValueForKey( nextmaps, va( "cfg_%i", slot ), entry->factoryId );
			Info_SetValueForKey( nextmaps, va( "gt_%i", slot ), entry->factoryTitle );
			slot++;
		}
	} else {
		for ( index = 0; index < s_svMapPoolCount && slot < 3; index++ ) {
			const svMapPoolEntry_t *entry = &s_svMapPool[index];

			Info_SetValueForKey( nextmaps, va( "map_%i", slot ), entry->mapName );
			Info_SetValueForKey( nextmaps, va( "title_%i", slot ), entry->mapTitle );
			Info_SetValueForKey( nextmaps, va( "cfg_%i", slot ), entry->factoryId );
			Info_SetValueForKey( nextmaps, va( "gt_%i", slot ), entry->factoryTitle );
			slot++;
		}
	}

	Cvar_Set( "nextmaps", nextmaps );
}

/*
=============
ReloadArenaDefinitions_f

Reloads the host-side arena catalog from retail assets.
=============
*/
static void ReloadArenaDefinitions_f( void ) {
	Com_Printf( "reloading arena definitions...\n" );
	SV_LoadArenas();
}

/*
=============
MapPool_Reload_f

Reloads the retail host map pool from the current `sv_mapPoolFile` path.
=============
*/
static void MapPool_Reload_f( void ) {
	Com_Printf( "reloading map pool...\n" );
	SV_MapPoolClear();
	SV_MapPoolLoadFromFile( sv_mapPoolFile ? sv_mapPoolFile->string : "mappool.txt" );
}

/*
=============
StartRandomMap_f

Queues the retail random map-pool starter command.
=============
*/
static void StartRandomMap_f( void ) {
	const svMapPoolEntry_t *entry = SV_MapPoolSelectRandomEntry();

	Cbuf_AddText( va( "map %s %s\n", entry->mapName, entry->factoryId ) );
}

/*
=============
Factory_Reload_f

Rebuilds the host-side factory registry while preserving the currently loaded
selection until the next map change.
=============
*/
static void Factory_Reload_f( void ) {
	SV_FactoryResetRegistry( qtrue );
	SV_FactoryEnsureRegistryLoaded();
}

/*
=============
SV_InitRetailOperatorData

Preloads the retail arena, factory, and map-pool data owned by the server
operator command surface.
=============
*/
void SV_InitRetailOperatorData( void ) {
	if ( !s_svArenaRegistryLoaded ) {
		SV_LoadArenas();
	}

	SV_FactoryEnsureRegistryLoaded();

	SV_MapPoolClear();
	SV_MapPoolLoadFromFile( sv_mapPoolFile ? sv_mapPoolFile->string : "mappool.txt" );
}

/*
=============
SV_UpdateMapPoolRotationCvars

Refreshes the retail `nextmap` and `nextmaps` cvars after map boots and
restart-style command paths.
=============
*/
void SV_UpdateMapPoolRotationCvars( void ) {
	SV_MapPoolUpdateNextMap();
	SV_MapPoolBuildNextMapsCvar();
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
	int		requiredArgs;

	cmd = Cmd_Argv(0);
	requiredArgs = s_svCurrentFactory ? 2 : 3;
	if ( Cmd_Argc() < requiredArgs ) {
		Com_Printf( "%s (map) (factory)\n", cmd );
		SV_FactoryPrintValidList();
		return;
	}

	map = Cmd_Argv(1);
	if ( !map || !*map ) {
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

	factoryOverride = s_svCurrentFactory;
	if ( Cmd_Argc() > 2 ) {
		factoryId = Cmd_Argv( 2 );
		if ( !factoryId || !*factoryId ) {
			factoryOverride = NULL;
		} else {
			factoryOverride = SV_FactoryFindById( factoryId );
		}
	}

	if ( !factoryOverride ) {
		Com_Printf( "Invalid factory specified.\n" );
		return;
	}

	if ( !cheat && !SV_MapSupportsGametype( map, factoryOverride->baseGametype ) ) {
		Com_Printf( "Map not supported for this gametype.\n" );
		return;
	}

	// save the map name here cause on a map restart we reload the q3config.cfg
	// and thus nuke the arguments of the map command
	Q_strncpyz(mapname, map, sizeof(mapname));

	SV_FactoryApplySelection( factoryOverride );

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

	if ( !com_dedicated->integer ) {
		Cvar_Set( "ui_singlePlayerActive", "1" );
		Cvar_Set( "ui_priv", "3" );
	}
}

/*
==================
SV_Arena_f

Launches a retail single-player arena descriptor from `scripts/*.sp_arena`.
==================
*/
static void SV_Arena_f( void ) {
	const char	*arenaName;
	fileHandle_t	file;
	int		length;
	char		path[MAX_QPATH];
	char		buffer[1024];
	char		*cursor;
	char		*token;
	int		fragLimit;
	int		timeLimit;
	int		botSkill;
	char		mapName[MAX_QPATH];
	char		mapPath[MAX_QPATH];
	char		botList[MAX_INFO_VALUE];
	qboolean	valid;

	arenaName = Cmd_Argv( 1 );
	if ( !arenaName || !arenaName[0] ) {
		Com_Printf( "No arena name passed\n" );
		return;
	}

	fragLimit = 20;
	timeLimit = 0;
	botSkill = (int)Cvar_VariableValue( "g_spSkill" );
	mapName[0] = '\0';
	botList[0] = '\0';

	Com_sprintf( path, sizeof( path ), "scripts/%s.sp_arena", arenaName );
	length = FS_FOpenFileRead( path, &file, qfalse );
	if ( length <= 0 ) {
		Com_Printf( "^1file not found: %s\n", path );
		return;
	}
	if ( length >= sizeof( buffer ) ) {
		Com_Printf( "^1file too large: %s is %i, max allowed is %i", path, length, sizeof( buffer ) );
		FS_FCloseFile( file );
		return;
	}

	FS_Read( buffer, length, file );
	buffer[length] = '\0';
	FS_FCloseFile( file );

	cursor = buffer;
	token = COM_Parse( &cursor );
	if ( !token[0] ) {
		Com_Printf( "%s is empty!\n", path );
		return;
	}
	if ( strcmp( token, "{" ) ) {
		Com_Printf( "Missing initial \"{\" in %s!\n", path );
		return;
	}

	valid = qtrue;
	while ( valid ) {
		token = COM_ParseExt( &cursor, qtrue );
		if ( !token[0] ) {
			Com_Printf( "Unexpected end of info file!\n" );
			return;
		}
		if ( !strcmp( token, "}" ) ) {
			break;
		}

		if ( !Q_stricmp( token, "fraglimit" ) ) {
			token = COM_ParseExt( &cursor, qfalse );
			if ( !token[0] ) {
				Com_Printf( "No matching value given for fraglimit!\n" );
				return;
			}

			fragLimit = atoi( token );
			if ( fragLimit < 1 ) {
				Com_Printf( "Fraglimit was an invalid value! Valid values are 1 or greater. Setting to 20.\n" );
				fragLimit = 20;
			}
		} else if ( !Q_stricmp( token, "timelimit" ) ) {
			token = COM_ParseExt( &cursor, qfalse );
			if ( !token[0] ) {
				Com_Printf( "No matching value given for timelimit!\n" );
				return;
			}

			timeLimit = atoi( token );
			if ( timeLimit < 0 ) {
				Com_Printf( "timelimit was an invalid value! Valid values are 0 or greater. Setting to 0.\n" );
				timeLimit = 0;
			}
		} else if ( !Q_stricmp( token, "bot_skill" ) ) {
			token = COM_ParseExt( &cursor, qfalse );
			if ( !token[0] ) {
				Com_Printf( "No matching value given for botSkill!\n" );
				return;
			}

			botSkill = atoi( token );
			if ( botSkill < 1 || botSkill > 5 ) {
				Com_Printf( "bot_skill was an invalid value! Valid values are 1 - 5. Setting to 4.\n" );
				botSkill = 4;
			}
		} else if ( !Q_stricmp( token, "map" ) ) {
			token = COM_ParseExt( &cursor, qfalse );
			if ( !token[0] ) {
				Com_Printf( "No map name given!\n" );
				return;
			}

			Q_strncpyz( mapName, token, sizeof( mapName ) );
			Com_sprintf( mapPath, sizeof( mapPath ), "maps/%s.bsp", mapName );
			if ( FS_ReadFile( mapPath, NULL ) == -1 ) {
				Com_Printf( "Can't find map %s!\n", mapPath );
				return;
			}
		} else if ( !Q_stricmp( token, "bots" ) ) {
			token = COM_ParseExt( &cursor, qfalse );
			if ( !token[0] ) {
				Com_Printf( "No bot names given for bots!\n" );
				return;
			}

			Q_strncpyz( botList, token, sizeof( botList ) );
		} else {
			Com_Printf( "Unknown value in %s\n", path );
			valid = qfalse;
		}
	}

	if ( !valid ) {
		return;
	}
	if ( !mapName[0] ) {
		Com_Printf( "No map name given!\n" );
		return;
	}

	Cvar_SetValue( "g_gametype", GT_FFA );
	Cvar_SetValue( "g_spSkill", botSkill );
	Cvar_SetValue( "fraglimit", fragLimit );
	Cvar_SetValue( "timelimit", timeLimit );
	if ( botList[0] ) {
		Cvar_Set( "g_botSpawnList", botList );
	}

	SV_SpawnServer( mapName, qtrue );
	Cvar_Set( "sv_cheats", "0" );
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
	const char	*denied;
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
	if ( sv_maxclients->modified || sv_gametype->modified || ( sv_ammoPack && sv_ammoPack->modified ) ) {
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
		denied = SV_GameClientConnect( i, qfalse, isBot );
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

	SV_UpdateMapPoolRotationCvars();
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
	const char	*reason;
	const char	*dropReason;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	if ( Cmd_Argc() == 1 ) {
		Com_Printf ("Usage: kick <player name>\nkick all = kick everyone\nkick allbots = kick all bots\n");
		return;
	}

	reason = ( Cmd_Argc() > 2 ) ? Cmd_Argv( 2 ) : NULL;
	if ( reason && reason[0] && strlen( reason ) < 0x80 ) {
		dropReason = va( "was kicked: %s", reason );
	} else {
		dropReason = "was kicked";
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
				SV_DropClient( cl, dropReason );
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
				SV_DropClient( cl, dropReason );
				cl->lastPacketTime = svs.time;	// in case there is a funny zombie
			}
		}
		return;
	}
	if( cl->netchan.remoteAddress.type == NA_LOOPBACK ) {
		SV_SendServerCommand(NULL, "print \"%s\"", "Cannot kick host player.\n");
		return;
	}

	SV_DropClient( cl, dropReason );
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
SV_StatusClientSteamId
================
*/
static unsigned long long SV_StatusClientSteamId( const client_t *cl ) {
	const char			*steamId;
	const char			*cursor;
	unsigned long long	value;

	if ( !cl ) {
		return 0ull;
	}

#if SV_HAS_PLATFORM_AUTH
	if ( cl->platformSteamId[0] ) {
		steamId = cl->platformSteamId;
	} else
#endif
	{
		steamId = Info_ValueForKey( cl->userinfo, "steamid" );
	}

	if ( !steamId || !steamId[0] ) {
		return 0ull;
	}

	value = 0ull;
	for ( cursor = steamId; *cursor; cursor++ ) {
		if ( *cursor < '0' || *cursor > '9' ) {
			return 0ull;
		}

		value = value * 10ull + (unsigned long long)( *cursor - '0' );
	}

	return value;
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
	unsigned long long	steamIdValue;

	// make sure server is running
	if ( !com_sv_running->integer ) {
		Com_Printf( "Server is not running.\n" );
		return;
	}

	Com_Printf ("map: %s\n", sv_mapname->string );

	Com_Printf ("num score ping name            lastmsg address               qport rate  steamid\n");
	Com_Printf ("--- ----- ---- --------------- ------- --------------------- ----- ----- -----------------\n");
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
		steamIdValue = SV_StatusClientSteamId( cl );
		Com_Printf (" %llu", steamIdValue);

		Com_Printf ("\n");
	}
	Com_Printf ("\n");
}

/*
==================
SV_ConSay_f
==================
*/
static void SV_ConSay_f( void ) {
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

	Q_strncpyz( text, Cmd_Args(), sizeof( text ) );
	p = text;

	if ( *p == '"' ) {
		p++;
		p[strlen(p)-1] = 0;
	}

	SV_SendServerCommand( NULL, "chat %d \"Server: %s\n\"", MAX_CLIENTS - 1, p );
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

/*
=============
SV_SteamWorkshop_SplitItemId

Splits a decimal workshop item ID into the low/high 32-bit pair used by the
SteamUGC wrappers.
=============
*/
static qboolean SV_SteamWorkshop_SplitItemId( unsigned long long itemId, uint32_t *itemIdLow, uint32_t *itemIdHigh ) {
	if ( itemIdLow ) {
		*itemIdLow = (uint32_t)( itemId & 0xffffffffull );
	}
	if ( itemIdHigh ) {
		*itemIdHigh = (uint32_t)( ( itemId >> 32 ) & 0xffffffffull );
	}

	return itemIdLow != NULL && itemIdHigh != NULL;
}

/*
=============
SV_LogWorkshopOperatorLifecycle

Publishes provider-aware diagnostics for the retained dedicated-server manual
Steam workshop command surface.
=============
*/
static void SV_LogWorkshopOperatorLifecycle( const char *commandName, unsigned long long itemId, const char *detail ) {
	Com_Printf( "Workshop operator %s for %llu via %s [%s]: %s\n",
		commandName ? commandName : "unknown",
		itemId,
		SV_GetWorkshopProviderLabel(),
		SV_GetWorkshopPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=============
SV_WorkshopServiceSupportsSteamCommands

Returns qtrue when the retained workshop descriptor still owns the manual
Steam UGC operator command lane.
=============
*/
static qboolean SV_WorkshopServiceSupportsSteamCommands( void ) {
	const char *provider = SV_GetWorkshopProviderLabel();

	return ( strstr( provider, "Steam UGC" ) != NULL );
}

/*
=============
SV_SteamCmd_DownloadUGC_f

Mirrors the retail manual workshop download command surface.
=============
*/
static void SV_SteamCmd_DownloadUGC_f( void ) {
	unsigned long long itemId = 0;
	uint32_t itemIdLow;
	uint32_t itemIdHigh;

	if ( Cmd_Argc() != 2 ) {
		Com_Printf( "Usage: steam_downloadugc <itemid>\n" );
		return;
	}

	sscanf( Cmd_Argv( 1 ), "%llu", &itemId );
	if ( !SV_SteamWorkshop_SplitItemId( itemId, &itemIdLow, &itemIdHigh ) ) {
		return;
	}

	if ( !SV_WorkshopServiceSupportsSteamCommands() ) {
		SV_LogWorkshopOperatorLifecycle( "steam_downloadugc", itemId,
			"Steam UGC operator unavailable for current compatibility lane" );
		return;
	}

	if ( QL_Steamworks_GetItemState( itemIdLow, itemIdHigh ) & 4u ) {
		SV_LogWorkshopOperatorLifecycle( "steam_downloadugc", itemId, "item already in cache" );
		return;
	}

	SV_LogWorkshopOperatorLifecycle( "steam_downloadugc", itemId, "download requested" );
	if ( !QL_Steamworks_DownloadItem( itemIdLow, itemIdHigh, qtrue ) ) {
		SV_LogWorkshopOperatorLifecycle( "steam_downloadugc", itemId, "download request failed" );
	}
}

/*
=============
SV_SteamCmd_SubscribeUGC_f

Mirrors the retail manual workshop subscribe command surface.
=============
*/
static void SV_SteamCmd_SubscribeUGC_f( void ) {
	unsigned long long itemId = 0;
	uint32_t itemIdLow;
	uint32_t itemIdHigh;

	if ( Cmd_Argc() != 2 ) {
		Com_Printf( "Usage: steam_subscribeugc <itemid>\n" );
		return;
	}

	sscanf( Cmd_Argv( 1 ), "%llu", &itemId );
	if ( !SV_SteamWorkshop_SplitItemId( itemId, &itemIdLow, &itemIdHigh ) ) {
		return;
	}

	if ( !SV_WorkshopServiceSupportsSteamCommands() ) {
		SV_LogWorkshopOperatorLifecycle( "steam_subscribeugc", itemId,
			"Steam UGC operator unavailable for current compatibility lane" );
		return;
	}

	SV_LogWorkshopOperatorLifecycle( "steam_subscribeugc", itemId, "subscribe requested" );
	if ( !QL_Steamworks_SubscribeItem( itemIdLow, itemIdHigh ) ) {
		SV_LogWorkshopOperatorLifecycle( "steam_subscribeugc", itemId, "subscribe request failed" );
	}
}

/*
=============
SV_SteamCmd_UnsubscribeUGC_f

Mirrors the retail manual workshop unsubscribe command surface.
=============
*/
static void SV_SteamCmd_UnsubscribeUGC_f( void ) {
	unsigned long long itemId = 0;
	uint32_t itemIdLow;
	uint32_t itemIdHigh;

	if ( Cmd_Argc() != 2 ) {
		Com_Printf( "Usage: steam_unsubscribeugc <itemid>\n" );
		return;
	}

	sscanf( Cmd_Argv( 1 ), "%llu", &itemId );
	if ( !SV_SteamWorkshop_SplitItemId( itemId, &itemIdLow, &itemIdHigh ) ) {
		return;
	}

	if ( !SV_WorkshopServiceSupportsSteamCommands() ) {
		SV_LogWorkshopOperatorLifecycle( "steam_unsubscribeugc", itemId,
			"Steam UGC operator unavailable for current compatibility lane" );
		return;
	}

	SV_LogWorkshopOperatorLifecycle( "steam_unsubscribeugc", itemId, "unsubscribe requested" );
	if ( !QL_Steamworks_UnsubscribeItem( itemIdLow, itemIdHigh ) ) {
		SV_LogWorkshopOperatorLifecycle( "steam_unsubscribeugc", itemId, "unsubscribe request failed" );
	}
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

	Cmd_AddCommand ("kick", SV_Kick_f);
	Cmd_AddCommand ("clientkick", SV_KickNum_f);
	Cmd_AddCommand ("status", SV_Status_f);
	Cmd_AddCommand ("serverinfo", SV_Serverinfo_f);
	Cmd_AddCommand ("dumpuser", SV_DumpUser_f);
	Cmd_AddCommand ("map_restart", SV_MapRestart_f);
	Cmd_AddCommand ("sectorlist", SV_SectorList_f);
	Cmd_AddCommand ("map", SV_Map_f);
	Cmd_AddCommand ("arena", SV_Arena_f);
#ifndef PRE_RELEASE_DEMO
	Cmd_AddCommand ("devmap", SV_Map_f);
#endif
	Cmd_AddCommand ("killserver", SV_KillServer_f);
	Cmd_AddCommand ("steam_downloadugc", SV_SteamCmd_DownloadUGC_f);
	Cmd_AddCommand ("steam_subscribeugc", SV_SteamCmd_SubscribeUGC_f);
	Cmd_AddCommand ("steam_unsubscribeugc", SV_SteamCmd_UnsubscribeUGC_f);
	Cmd_AddCommand ("startRandomMap", StartRandomMap_f);
	Cmd_AddCommand ("reload_mappool", MapPool_Reload_f);
	Cmd_AddCommand ("reload_arenas", ReloadArenaDefinitions_f);
	Cmd_AddCommand ("reload_factories", Factory_Reload_f);
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

