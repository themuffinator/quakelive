#include "g_local.h"
#include "g_config.h"
#include "g_match_config.h"

#define FACTORY_MAX_JSON_STRING          4096
#define FACTORY_FILE_LIST_BUFFER         4096

typedef struct factoryParseState_s {
	const char      *cursor;
	const char      *end;
	const char      *filename;
	int             line;
} factoryParseState_t;

static factoryDefinition_t    *s_factoryList = NULL;
static const factoryDefinition_t      *s_activeFactory = NULL;
static int                     s_factoryCount = 0;

static const char *Factory_CopyString( const char *value );
static void Factory_ReportParseError( const factoryParseState_t *state, const char *message );
static void Factory_SkipWhitespace( factoryParseState_t *state );
static qboolean Factory_ParseExpectedChar( factoryParseState_t *state, char ch );
static qboolean Factory_SkipJsonString( factoryParseState_t *state );
static char *Factory_ParseJsonString( factoryParseState_t *state );
static char *Factory_ParseLiteralString( factoryParseState_t *state );
static qboolean Factory_SkipValue( factoryParseState_t *state );
static qboolean Factory_ParseCvarOverrides( factoryParseState_t *state, factoryDefinition_t *definition );
static factoryDefinition_t *Factory_ParseDefinition( factoryParseState_t *state, const char *sourceFile );
static int Factory_ParseFactoriesBuffer( const char *filename, const char *buffer, int length );
static qboolean Factory_LoadFile( const char *filename );
static void Factory_LoadSupplementalFiles( void );
static qboolean Factory_RegisterDefinition( factoryDefinition_t *definition );
static qboolean Factory_MapBaseGametype( const char *token, gametype_t *outType );
static void Factory_RefreshMatchConfig( void );
static void Factory_LogSelection( const factoryDefinition_t *factory );

/*
=============
Factory_CopyString

Allocates a persistent copy of the supplied string using the VM memory pool.
=============
*/
static const char *Factory_CopyString( const char *value ) {
	size_t  length;
	char    *copy;

	if ( !value ) {
		return "";
	}

	length = strlen( value ) + 1u;
	copy = ( char * )G_Alloc( length );
	if ( copy ) {
		memcpy( copy, value, length );
	}

	return copy ? copy : "";
}

/*
=============
Factory_ReportParseError

Logs a descriptive parse error so administrators can diagnose malformed JSON.
=============
*/
static void Factory_ReportParseError( const factoryParseState_t *state, const char *message ) {
	const char  *filename = state && state->filename ? state->filename : "<unknown>";
	int         line = state ? state->line : 0;

	if ( !message ) {
		message = "unknown parse error";
	}

	G_Printf( "factories: parse error in %s at line %i: %s\n", filename, line, message );
}

/*
=============
Factory_SkipWhitespace

Advances past whitespace characters in the JSON stream.
=============
*/
static void Factory_SkipWhitespace( factoryParseState_t *state ) {
	if ( !state ) {
		return;
	}

	while ( state->cursor < state->end ) {
		char ch = *state->cursor;

		if ( ch == '\n' ) {
			state->line++;
			state->cursor++;
			continue;
		}

		if ( ch == '\r' || ch == '\t' || ch == ' ' ) {
			state->cursor++;
			continue;
		}

		break;
	}
}

/*
=============
Factory_ParseExpectedChar

Consumes the expected delimiter or reports a parse error.
=============
*/
static qboolean Factory_ParseExpectedChar( factoryParseState_t *state, char ch ) {
	Factory_SkipWhitespace( state );

	if ( !state || state->cursor >= state->end || *state->cursor != ch ) {
		Factory_ReportParseError( state, va( "expected '%c'", ch ) );
		return qfalse;
	}

	state->cursor++;
	return qtrue;
}

/*
=============
Factory_SkipJsonString

Skips over a JSON string literal without allocating storage.
=============
*/
static qboolean Factory_SkipJsonString( factoryParseState_t *state ) {
	if ( !state ) {
		return qfalse;
	}

	Factory_SkipWhitespace( state );
	if ( state->cursor >= state->end || *state->cursor != '"' ) {
		Factory_ReportParseError( state, "expected string" );
		return qfalse;
	}

	state->cursor++;
	while ( state->cursor < state->end ) {
		char ch = *state->cursor++;

		if ( ch == '"' ) {
			return qtrue;
		}

		if ( ch == '\\' ) {
			if ( state->cursor >= state->end ) {
				break;
			}

			state->cursor++;
			continue;
		}

		if ( ch == '\n' ) {
			state->line++;
		}
	}

	Factory_ReportParseError( state, "unterminated string" );
	return qfalse;
}

/*
=============
Factory_ParseJsonString

Parses a JSON string literal into the VM memory pool.
=============
*/
static char *Factory_ParseJsonString( factoryParseState_t *state ) {
	char    buffer[FACTORY_MAX_JSON_STRING];
	size_t  length;

	if ( !state ) {
		return NULL;
	}

	Factory_SkipWhitespace( state );
	if ( state->cursor >= state->end || *state->cursor != '"' ) {
		Factory_ReportParseError( state, "expected string" );
		return NULL;
	}

	state->cursor++;
	length = 0u;
	while ( state->cursor < state->end ) {
		char ch = *state->cursor++;

		if ( ch == '"' ) {
			buffer[length] = '\0';
			return ( char * )Factory_CopyString( buffer );
		}

		if ( ch == '\\' ) {
			char escaped;

			if ( state->cursor >= state->end ) {
				break;
			}

			escaped = *state->cursor++;
			switch ( escaped ) {
				case '"': ch = '"'; break;
				case '\\': ch = '\\'; break;
				case '/': ch = '/'; break;
				case 'b': ch = '\b'; break;
				case 'f': ch = '\f'; break;
				case 'n': ch = '\n'; state->line++; break;
				case 'r': ch = '\r'; break;
				case 't': ch = '\t'; break;
				case 'u': {
					int i;
					int value = 0;

					for ( i = 0; i < 4 && state->cursor < state->end; i++ ) {
						char hex = *state->cursor++;
						value <<= 4;
						if ( hex >= '0' && hex <= '9' ) {
							value |= hex - '0';
						} else if ( hex >= 'a' && hex <= 'f' ) {
							value |= 10 + ( hex - 'a' );
						} else if ( hex >= 'A' && hex <= 'F' ) {
							value |= 10 + ( hex - 'A' );
						} else {
							Factory_ReportParseError( state, "invalid unicode escape" );
							return NULL;
						}
					}

					if ( value <= 0x7F ) {
						ch = ( char )value;
					} else {
						ch = '?';
					}
					break;
				}
				default:
					Factory_ReportParseError( state, "invalid escape" );
					return NULL;
			}
		}

		if ( length + 1u >= sizeof( buffer ) ) {
			Factory_ReportParseError( state, "string literal too long" );
			return NULL;
		}

		buffer[length++] = ch;
	}

	Factory_ReportParseError( state, "unterminated string" );
	return NULL;
}

/*
=============
Factory_ParseLiteralString

Consumes a JSON literal (number, true/false/null) as a string.
=============
*/
static char *Factory_ParseLiteralString( factoryParseState_t *state ) {
	char    buffer[64];
	size_t  length;

	if ( !state ) {
		return NULL;
	}

	Factory_SkipWhitespace( state );
	length = 0u;
	while ( state->cursor < state->end ) {
		char ch = *state->cursor;

		if ( ch == ',' || ch == '}' || ch == ']' || ch == '\n' || ch == '\r' || ch == '\t' || ch == ' ' ) {
			break;
		}

		if ( length + 1u >= sizeof( buffer ) ) {
			Factory_ReportParseError( state, "literal too long" );
			return NULL;
		}

		buffer[length++] = ch;
		state->cursor++;
	}

	buffer[length] = '\0';
	if ( length == 0u ) {
		Factory_ReportParseError( state, "expected literal" );
		return NULL;
	}

	return ( char * )Factory_CopyString( buffer );
}

/*
=============
Factory_SkipValue

Skips over any JSON value so optional keys may be ignored cleanly.
=============
*/
static qboolean Factory_SkipValue( factoryParseState_t *state ) {
	if ( !state ) {
		return qfalse;
	}

	Factory_SkipWhitespace( state );
	if ( state->cursor >= state->end ) {
		Factory_ReportParseError( state, "unexpected end of data" );
		return qfalse;
	}

	switch ( *state->cursor ) {
		case '{': {
			int depth = 0;
			do {
				char ch = *state->cursor++;
				if ( ch == '{' ) {
					depth++;
				} else if ( ch == '}' ) {
					depth--;
				} else if ( ch == '"' ) {
					if ( !Factory_SkipJsonString( state ) ) {
						return qfalse;
					}
				}
				if ( ch == '\n' ) {
					state->line++;
				}
			} while ( depth > 0 && state->cursor < state->end );
			if ( depth != 0 ) {
				Factory_ReportParseError( state, "unterminated object" );
				return qfalse;
			}
			return qtrue;
		}
		case '[': {
			int depth = 0;
			do {
				char ch = *state->cursor++;
				if ( ch == '[' ) {
					depth++;
				} else if ( ch == ']' ) {
					depth--;
				} else if ( ch == '"' ) {
					if ( !Factory_SkipJsonString( state ) ) {
						return qfalse;
					}
				}
				if ( ch == '\n' ) {
					state->line++;
				}
			} while ( depth > 0 && state->cursor < state->end );
			if ( depth != 0 ) {
				Factory_ReportParseError( state, "unterminated array" );
				return qfalse;
			}
			return qtrue;
		}
		case '"':
			return Factory_SkipJsonString( state );
		default:
			while ( state->cursor < state->end ) {
				char ch = *state->cursor;

				if ( ch == ',' || ch == '}' || ch == ']' || ch == '\n' ) {
					return qtrue;
				}

				state->cursor++;
			}
			return qtrue;
	}
}

/*
=============
Factory_ParseCvarOverrides

Parses the "cvars" object for a factory definition.
=============
*/
static qboolean Factory_ParseCvarOverrides( factoryParseState_t *state, factoryDefinition_t *definition ) {
	factoryOverride_t *tail = NULL;

	if ( !definition || !Factory_ParseExpectedChar( state, '{' ) ) {
		return qfalse;
	}

	Factory_SkipWhitespace( state );
	if ( state->cursor < state->end && *state->cursor == '}' ) {
		state->cursor++;
		return qtrue;
	}

	while ( state->cursor < state->end ) {
		char *name = Factory_ParseJsonString( state );
		char *value;
		factoryOverride_t *override;

		if ( !name ) {
			return qfalse;
		}

		if ( !Factory_ParseExpectedChar( state, ':' ) ) {
			return qfalse;
		}

		Factory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			Factory_ReportParseError( state, "unexpected end of cvars" );
			return qfalse;
		}

		if ( *state->cursor == '"' ) {
			value = Factory_ParseJsonString( state );
		} else {
			value = Factory_ParseLiteralString( state );
		}

		if ( !value ) {
			return qfalse;
		}

		override = ( factoryOverride_t * )G_Alloc( sizeof( factoryOverride_t ) );
		if ( !override ) {
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

		Factory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			Factory_ReportParseError( state, "unterminated cvars object" );
			return qfalse;
		}

		if ( *state->cursor == ',' ) {
			state->cursor++;
			continue;
		}

		if ( *state->cursor == '}' ) {
			state->cursor++;
			return qtrue;
		}

		Factory_ReportParseError( state, "expected ',' or '}'" );
		return qfalse;
	}

	Factory_ReportParseError( state, "unterminated cvars object" );
	return qfalse;
}

/*
=============
Factory_MapBaseGametype

Translates the textual base gametype token into a gametype_t value.
=============
*/
static qboolean Factory_MapBaseGametype( const char *token, gametype_t *outType ) {
	static const struct {
		const char      *name;
		gametype_t      type;
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

	if ( !token || !token[0] ) {
		return qfalse;
	}

	for ( i = 0; i < ARRAY_LEN( s_gametypeMap ); i++ ) {
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
Factory_ParseDefinition

Parses a single factory definition object.
=============
*/
static factoryDefinition_t *Factory_ParseDefinition( factoryParseState_t *state, const char *sourceFile ) {
	factoryDefinition_t *definition;
	char    *basegt = NULL;

	if ( !Factory_ParseExpectedChar( state, '{' ) ) {
		return NULL;
	}

	definition = ( factoryDefinition_t * )G_Alloc( sizeof( factoryDefinition_t ) );
	if ( !definition ) {
		return NULL;
	}

	definition->sourceFile = Factory_CopyString( sourceFile );

	while ( state->cursor < state->end ) {
		char *key;

		Factory_SkipWhitespace( state );
		if ( state->cursor < state->end && *state->cursor == '}' ) {
			state->cursor++;
			break;
		}

		key = Factory_ParseJsonString( state );
		if ( !key ) {
			return NULL;
		}

		if ( !Factory_ParseExpectedChar( state, ':' ) ) {
			return NULL;
		}

		if ( !Q_stricmp( key, "id" ) ) {
			definition->id = Factory_ParseJsonString( state );
		} else if ( !Q_stricmp( key, "title" ) ) {
			definition->title = Factory_ParseJsonString( state );
		} else if ( !Q_stricmp( key, "description" ) ) {
			definition->description = Factory_ParseJsonString( state );
		} else if ( !Q_stricmp( key, "basegt" ) ) {
			basegt = Factory_ParseJsonString( state );
		} else if ( !Q_stricmp( key, "cvars" ) ) {
			if ( !Factory_ParseCvarOverrides( state, definition ) ) {
				return NULL;
			}
		} else {
			if ( !Factory_SkipValue( state ) ) {
				return NULL;
			}
		}

		Factory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			Factory_ReportParseError( state, "unterminated factory object" );
			return NULL;
		}

		if ( *state->cursor == ',' ) {
			state->cursor++;
			continue;
		}

		if ( *state->cursor == '}' ) {
			state->cursor++;
			break;
		}

		Factory_ReportParseError( state, "expected ',' or '}'" );
		return NULL;
	}

	if ( !definition->id || !definition->id[0] ) {
		Factory_ReportParseError( state, "factory missing id" );
		return NULL;
	}

	if ( !definition->title ) {
		definition->title = "";
	}

	if ( !definition->description ) {
		definition->description = "";
	}

	if ( !basegt || !Factory_MapBaseGametype( basegt, &definition->baseGametype ) ) {
		Factory_ReportParseError( state, va( "factory %s missing valid basegt", definition->id ) );
		return NULL;
	}

	definition->baseGametypeName = Factory_CopyString( basegt );
	return definition;
}

/*
=============
Factory_ParseFactoriesBuffer

Reads a JSON array of factory definitions from memory.
=============
*/
static int Factory_ParseFactoriesBuffer( const char *filename, const char *buffer, int length ) {
	factoryParseState_t    state;
	int                   parsed = 0;

	if ( !buffer || length <= 0 ) {
		return 0;
	}

	state.cursor = buffer;
	state.end = buffer + length;
	state.filename = filename;
	state.line = 1;

	Factory_SkipWhitespace( &state );
	if ( !Factory_ParseExpectedChar( &state, '[' ) ) {
		return 0;
	}

	Factory_SkipWhitespace( &state );
	if ( state.cursor < state.end && *state.cursor == ']' ) {
		state.cursor++;
		return 0;
	}

	while ( state.cursor < state.end ) {
		factoryDefinition_t *definition = Factory_ParseDefinition( &state, filename );

		if ( !definition ) {
			return parsed;
		}

		if ( Factory_RegisterDefinition( definition ) ) {
			parsed++;
		}

		Factory_SkipWhitespace( &state );
		if ( state.cursor >= state.end ) {
			Factory_ReportParseError( &state, "unterminated factory array" );
			return parsed;
		}

		if ( *state.cursor == ',' ) {
			state.cursor++;
			continue;
		}

		if ( *state.cursor == ']' ) {
			state.cursor++;
			break;
		}

		Factory_ReportParseError( &state, "expected ',' or ']'" );
		break;
	}

	return parsed;
}

/*
=============
Factory_LoadFile

Reads and parses a single factories text file.
=============
*/
static qboolean Factory_LoadFile( const char *filename ) {
	fileHandle_t   handle;
	int            length;
	char           *data;
	int            parsed;

	length = trap_FS_FOpenFile( filename, &handle, FS_READ );
	if ( length <= 0 || !handle ) {
		G_Printf( "factories: unable to open %s\n", filename );
		return qfalse;
	}

	data = ( char * )G_Alloc( length + 1 );
	if ( !data ) {
		trap_FS_FCloseFile( handle );
		return qfalse;
	}

	trap_FS_Read( data, length, handle );
	data[length] = '\0';
	trap_FS_FCloseFile( handle );

	parsed = Factory_ParseFactoriesBuffer( filename, data, length );
	if ( parsed > 0 ) {
		G_Printf( "factories: parsed %i entries from %s\n", parsed, filename );
	}

	return parsed > 0 ? qtrue : qfalse;
}

/*
=============
Factory_LoadSupplementalFiles

Loads any *.factories supplements under scripts/.
=============
*/
static void Factory_LoadSupplementalFiles( void ) {
	char    fileList[FACTORY_FILE_LIST_BUFFER];
	char    *cursor;
	int     total;
	int     i;

	total = trap_FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( i = 0; i < total; i++ ) {
		int length = strlen( cursor );
		char path[MAX_QPATH];

		if ( length <= 0 ) {
			cursor++;
			continue;
		}

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		Factory_LoadFile( path );
		cursor += length + 1;
	}
}

/*
=============
Factory_RegisterDefinition

Adds a parsed definition to the registry if the id is unique.
=============
*/
static qboolean Factory_RegisterDefinition( factoryDefinition_t *definition ) {
	const factoryDefinition_t *existing;

	if ( !definition || !definition->id ) {
		return qfalse;
	}

	existing = Factory_FindById( definition->id );
	if ( existing ) {
		G_Printf( "factories: duplicate id %s from %s ignored (already provided by %s)\n",
			definition->id,
			definition->sourceFile ? definition->sourceFile : "<unknown>",
			existing->sourceFile ? existing->sourceFile : "<unknown>" );
		return qfalse;
	}

	definition->next = s_factoryList;
	s_factoryList = definition;
	s_factoryCount++;
	return qtrue;
}

/*
=============
Factory_RefreshMatchConfig

Refreshes cached factory configuration mirrors after a selection change.
=============
*/
static void Factory_RefreshMatchConfig( void ) {
	G_UpdateWeaponConfig();
	G_UpdateWeaponReloadConfig();
	G_UpdateKnockbackConfig();
	G_UpdateStartingAmmoConfig();
	G_UpdateAmmoPackConfig();
	G_UpdateFactoryCvarConfig();
	G_UpdateMatchFactoryConfig();
	G_SyncMatchFactoryConfigToLevel();
}

/*
=============
Factory_LogSelection

Describes the newly selected factory in server output for diagnostics.
=============
*/
static void Factory_LogSelection( const factoryDefinition_t *factory ) {
	if ( !factory ) {
		G_Printf( "factories: clearing active selection\n" );
		return;
	}

	G_Printf( "factories: applying %s (%s) from %s\n",
		factory->id,
		factory->title ? factory->title : "",
		factory->sourceFile ? factory->sourceFile : "<unknown>" );
}

/*
=============
G_FactoryRegistry_Init

Initialises the factory registry for the current map.
=============
*/
void G_FactoryRegistry_Init( void ) {
	s_factoryList = NULL;
	s_activeFactory = NULL;
	s_factoryCount = 0;

	Factory_LoadFile( "scripts/factories.txt" );
	Factory_LoadSupplementalFiles();

	G_Printf( "factories: %i definitions available\n", s_factoryCount );
}

/*
=============
Factory_FindById

Looks up a previously parsed factory definition by id.
=============
*/
const factoryDefinition_t *Factory_FindById( const char *id ) {
	const factoryDefinition_t *factory;

	if ( !id || !id[0] ) {
		return NULL;
	}

	for ( factory = s_factoryList; factory; factory = factory->next ) {
		if ( !Q_stricmp( factory->id, id ) ) {
			return factory;
		}
	}

	return NULL;
}

/*
=============
Factory_Apply

Applies a parsed factory definition by pushing its overrides into CVars.
=============
*/
qboolean Factory_Apply( const factoryDefinition_t *factory, qboolean forceReapply ) {
	const factoryOverride_t   *override;
	char                      gametypeBuffer[8];

	if ( !factory ) {
		s_activeFactory = NULL;
		trap_Cvar_Set( "g_factoryTitle", "" );
		trap_Cvar_Update( &g_factoryTitle );
		return qtrue;
	}

	if ( !forceReapply && s_activeFactory == factory ) {
		G_Printf( "factories: not clearing currently loaded factory id %s\n", factory->id );
		return qtrue;
	}

	s_activeFactory = factory;
	Factory_LogSelection( factory );

	for ( override = factory->overrides; override; override = override->next ) {
		if ( override->name && override->value ) {
			trap_Cvar_Set( override->name, override->value );
		}
	}

	Com_sprintf( gametypeBuffer, sizeof( gametypeBuffer ), "%i", factory->baseGametype );
	trap_Cvar_Set( "g_gametype", gametypeBuffer );
	trap_Cvar_Set( "g_factoryTitle", factory->title ? factory->title : "" );

	G_RefreshAllCvars();
	G_Config_UpdateCvars();
	Factory_RefreshMatchConfig();
	return qtrue;
}

/*
=============
Factory_ApplyCurrentSelection

Applies the factory referenced by the g_factory CVar.
=============
*/
void Factory_ApplyCurrentSelection( qboolean forceReapply ) {
	const factoryDefinition_t *factory;

	trap_Cvar_Update( &g_factory );
	if ( !g_factory.string[0] ) {
		Factory_Apply( NULL, qtrue );
		return;
	}

	factory = Factory_FindById( g_factory.string );
	if ( !factory ) {
		G_Printf( "factories: unknown id %s\n", g_factory.string );
		if ( s_activeFactory && s_activeFactory->id ) {
			trap_Cvar_Set( "g_factory", s_activeFactory->id );
		}
		return;
	}

	Factory_Apply( factory, forceReapply );
}
