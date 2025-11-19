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

#include "g_local.h"
#include "g_match_config.h"

qboolean	G_SpawnString( const char *key, const char *defaultString, char **out ) {
	int		i;

	if ( !level.spawning ) {
		*out = (char *)defaultString;
//		G_Error( "G_SpawnString() called while not spawning" );
	}

	for ( i = 0 ; i < level.numSpawnVars ; i++ ) {
		if ( !Q_stricmp( key, level.spawnVars[i][0] ) ) {
			*out = level.spawnVars[i][1];
			return qtrue;
		}
	}

	*out = (char *)defaultString;
	return qfalse;
}

qboolean	G_SpawnFloat( const char *key, const char *defaultString, float *out ) {
	char		*s;
	qboolean	present;

	present = G_SpawnString( key, defaultString, &s );
	*out = atof( s );
	return present;
}

qboolean	G_SpawnInt( const char *key, const char *defaultString, int *out ) {
	char		*s;
	qboolean	present;

	present = G_SpawnString( key, defaultString, &s );
	*out = atoi( s );
	return present;
}

qboolean	G_SpawnVector( const char *key, const char *defaultString, float *out ) {
	char		*s;
	qboolean	present;

	present = G_SpawnString( key, defaultString, &s );
	sscanf( s, "%f %f %f", &out[0], &out[1], &out[2] );
	return present;
}



//
// fields are needed for spawning from the entity string
//
typedef enum {
	F_INT, 
	F_FLOAT,
	F_LSTRING,			// string on disk, pointer in memory, TAG_LEVEL
	F_GSTRING,			// string on disk, pointer in memory, TAG_GAME
	F_VECTOR,
	F_ANGLEHACK,
	F_ENTITY,			// index on disk, pointer in memory
	F_ITEM,				// index on disk, pointer in memory
	F_CLIENT,			// index on disk, pointer in memory
	F_IGNORE
} fieldtype_t;

typedef struct
{
	char	*name;
	int		ofs;
	fieldtype_t	type;
	int		flags;
} field_t;

field_t fields[] = {
	{"classname", FOFS(classname), F_LSTRING},
	{"origin", FOFS(s.origin), F_VECTOR},
	{"model", FOFS(model), F_LSTRING},
	{"model2", FOFS(model2), F_LSTRING},
	{"spawnflags", FOFS(spawnflags), F_INT},
	{"speed", FOFS(speed), F_FLOAT},
	{"target", FOFS(target), F_LSTRING},
	{"targetname", FOFS(targetname), F_LSTRING},
	{"message", FOFS(message), F_LSTRING},
	{"team", FOFS(team), F_LSTRING},
	{"wait", FOFS(wait), F_FLOAT},
	{"random", FOFS(random), F_FLOAT},
	{"count", FOFS(count), F_INT},
	{"health", FOFS(health), F_INT},
	{"light", 0, F_IGNORE},
	{"dmg", FOFS(damage), F_INT},
	{"angles", FOFS(s.angles), F_VECTOR},
	{"angle", FOFS(s.angles), F_ANGLEHACK},
	{"targetShaderName", FOFS(targetShaderName), F_LSTRING},
	{"targetShaderNewName", FOFS(targetShaderNewName), F_LSTRING},

	{NULL}
};


typedef struct {
	char	*name;
	void	(*spawn)(gentity_t *ent);
} spawn_t;

void SP_info_player_start (gentity_t *ent);
void SP_info_player_deathmatch (gentity_t *ent);
void SP_info_player_intermission (gentity_t *ent);
void SP_info_firstplace(gentity_t *ent);
void SP_info_secondplace(gentity_t *ent);
void SP_info_thirdplace(gentity_t *ent);
void SP_info_podium(gentity_t *ent);

void SP_func_plat (gentity_t *ent);
void SP_func_static (gentity_t *ent);
void SP_func_rotating (gentity_t *ent);
void SP_func_bobbing (gentity_t *ent);
void SP_func_pendulum( gentity_t *ent );
void SP_func_button (gentity_t *ent);
void SP_func_door (gentity_t *ent);
void SP_func_train (gentity_t *ent);
void SP_func_timer (gentity_t *self);

void SP_trigger_always (gentity_t *ent);
void SP_trigger_multiple (gentity_t *ent);
void SP_trigger_push (gentity_t *ent);
void SP_trigger_teleport (gentity_t *ent);
void SP_trigger_hurt (gentity_t *ent);
void SP_trigger_capturezone( gentity_t *ent );

void SP_target_remove_powerups( gentity_t *ent );
void SP_target_remove_keys( gentity_t *ent );
void SP_target_give (gentity_t *ent);
void SP_target_delay (gentity_t *ent);
void SP_target_speaker (gentity_t *ent);
void SP_target_print (gentity_t *ent);
void SP_target_laser (gentity_t *self);
void SP_target_character (gentity_t *ent);
void SP_target_score( gentity_t *ent );
void SP_target_teleporter( gentity_t *ent );
void SP_target_relay (gentity_t *ent);
void SP_target_kill (gentity_t *ent);
void SP_target_position (gentity_t *ent);
void SP_target_location (gentity_t *ent);
void SP_target_push (gentity_t *ent);
void SP_target_cvar( gentity_t *ent );
void SP_target_achievement( gentity_t *ent );

void SP_light (gentity_t *self);
void SP_info_null (gentity_t *self);
void SP_info_notnull (gentity_t *self);
void SP_info_camp (gentity_t *self);
void SP_path_corner (gentity_t *self);

void SP_misc_teleporter_dest (gentity_t *self);
void SP_misc_model(gentity_t *ent);
void SP_misc_portal_camera(gentity_t *ent);
void SP_misc_portal_surface(gentity_t *ent);

void SP_shooter_rocket( gentity_t *ent );
void SP_shooter_plasma( gentity_t *ent );
void SP_shooter_grenade( gentity_t *ent );

void SP_team_CTF_redplayer( gentity_t *ent );
void SP_team_CTF_blueplayer( gentity_t *ent );

void SP_team_CTF_redspawn( gentity_t *ent );
void SP_team_CTF_bluespawn( gentity_t *ent );

void SP_team_blueobelisk( gentity_t *ent );
void SP_team_redobelisk( gentity_t *ent );
void SP_team_neutralobelisk( gentity_t *ent );
void SP_team_dom_point( gentity_t *ent );
void SP_item_botroam( gentity_t *ent ) {};
void SP_race_point( gentity_t *ent );

spawn_t	spawns[] = {
	// info entities don't do anything at all, but provide positional
	// information for things controlled by other processes
	{"info_player_start", SP_info_player_start},
	{"info_player_deathmatch", SP_info_player_deathmatch},
	{"info_player_intermission", SP_info_player_intermission},
	{"info_null", SP_info_null},
	{"info_notnull", SP_info_notnull},		// use target_position instead
	{"info_camp", SP_info_camp},

	{"func_plat", SP_func_plat},
	{"func_button", SP_func_button},
	{"func_door", SP_func_door},
	{"func_static", SP_func_static},
	{"func_rotating", SP_func_rotating},
	{"func_bobbing", SP_func_bobbing},
	{"func_pendulum", SP_func_pendulum},
	{"func_train", SP_func_train},
	{"func_group", SP_info_null},
	{"func_timer", SP_func_timer},			// rename trigger_timer?

	// Triggers are brush objects that cause an effect when contacted
	// by a living player, usually involving firing targets.
	// While almost everything could be done with
	// a single trigger class and different targets, triggered effects
	// could not be client side predicted (push and teleport).
	{"trigger_always", SP_trigger_always},
	{"trigger_multiple", SP_trigger_multiple},
	{"trigger_push", SP_trigger_push},
	{"trigger_teleport", SP_trigger_teleport},
	{"trigger_hurt", SP_trigger_hurt},
	{"trigger_capturezone", SP_trigger_capturezone},

	// targets perform no action by themselves, but must be triggered
	// by another entity
	{"target_give", SP_target_give},
	{"target_remove_keys", SP_target_remove_keys},
	{"target_remove_powerups", SP_target_remove_powerups},
	{"target_delay", SP_target_delay},
	{"target_speaker", SP_target_speaker},
	{"target_print", SP_target_print},
	{"target_laser", SP_target_laser},
	{"target_score", SP_target_score},
	{"target_teleporter", SP_target_teleporter},
	{"target_relay", SP_target_relay},
	{"target_kill", SP_target_kill},
	{"target_position", SP_target_position},
	{"target_location", SP_target_location},
	{"target_push", SP_target_push},
	{"target_cvar", SP_target_cvar},
	{"target_achievement", SP_target_achievement},

	{"light", SP_light},
	{"path_corner", SP_path_corner},

	{"misc_teleporter_dest", SP_misc_teleporter_dest},
	{"misc_model", SP_misc_model},
	{"misc_portal_surface", SP_misc_portal_surface},
	{"misc_portal_camera", SP_misc_portal_camera},
	{"race_point", SP_race_point},

	{"shooter_rocket", SP_shooter_rocket},
	{"shooter_grenade", SP_shooter_grenade},
	{"shooter_plasma", SP_shooter_plasma},

	{"team_CTF_redplayer", SP_team_CTF_redplayer},
	{"team_CTF_blueplayer", SP_team_CTF_blueplayer},

	{"team_CTF_redspawn", SP_team_CTF_redspawn},
	{"team_CTF_bluespawn", SP_team_CTF_bluespawn},

	{"team_redobelisk", SP_team_redobelisk},
	{"team_blueobelisk", SP_team_blueobelisk},
	{"team_neutralobelisk", SP_team_neutralobelisk},
	{"team_dom_point", SP_team_dom_point},
	{"item_botroam", SP_item_botroam},

	{0, 0}
};

/*
===============
G_CallSpawn

Finds the spawn function for the entity and calls it,
returning qfalse if not found
===============
*/
qboolean G_CallSpawn( gentity_t *ent ) {
	spawn_t	*s;
	gitem_t	*item;

	if ( !ent->classname ) {
		G_Printf ("G_CallSpawn: NULL classname\n");
		return qfalse;
	}

	// check item spawn functions
	for ( item=bg_itemlist+1 ; item->classname ; item++ ) {
		if ( !strcmp(item->classname, ent->classname) ) {
			G_SpawnItem( ent, item );
			return qtrue;
		}
	}

	// check normal spawn functions
	for ( s=spawns ; s->name ; s++ ) {
		if ( !strcmp(s->name, ent->classname) ) {
			// found it
			s->spawn(ent);
			return qtrue;
		}
	}
	G_Printf ("%s doesn't have a spawn function\n", ent->classname);
	return qfalse;
}

/*
=============
G_NewString

Builds a copy of the string, translating \n to real linefeeds
so message texts can be multi-line
=============
*/
char *G_NewString( const char *string ) {
	char	*newb, *new_p;
	int		i,l;
	
	l = strlen(string) + 1;

	newb = G_Alloc( l );

	new_p = newb;

	// turn \n into a real linefeed
	for ( i=0 ; i< l ; i++ ) {
		if (string[i] == '\\' && i < l-1) {
			i++;
			if (string[i] == 'n') {
				*new_p++ = '\n';
			} else {
				*new_p++ = '\\';
			}
		} else {
			*new_p++ = string[i];
		}
	}
	
	return newb;
}




/*
===============
G_ParseField

Takes a key/value pair and sets the binary values
in a gentity
===============
*/
void G_ParseField( const char *key, const char *value, gentity_t *ent ) {
	field_t	*f;
	byte	*b;
	float	v;
	vec3_t	vec;

	for ( f=fields ; f->name ; f++ ) {
		if ( !Q_stricmp(f->name, key) ) {
			// found it
			b = (byte *)ent;

			switch( f->type ) {
			case F_LSTRING:
				*(char **)(b+f->ofs) = G_NewString (value);
				break;
			case F_VECTOR:
				sscanf (value, "%f %f %f", &vec[0], &vec[1], &vec[2]);
				((float *)(b+f->ofs))[0] = vec[0];
				((float *)(b+f->ofs))[1] = vec[1];
				((float *)(b+f->ofs))[2] = vec[2];
				break;
			case F_INT:
				*(int *)(b+f->ofs) = atoi(value);
				break;
			case F_FLOAT:
				*(float *)(b+f->ofs) = atof(value);
				break;
			case F_ANGLEHACK:
				v = atof(value);
				((float *)(b+f->ofs))[0] = 0;
				((float *)(b+f->ofs))[1] = v;
				((float *)(b+f->ofs))[2] = 0;
				break;
			default:
			case F_IGNORE:
				break;
			}
			return;
		}
	}
}




/*
=================
G_SpawnGametypeAliases

Mapping of gametype enum values to the spawn string tokens used by
worldspawn "gametype" filters.
=================
*/
#define MAX_GAMETYPE_NAME_ALIASES 3

static const char *const s_gametypeSpawnNames[GT_MAX_GAME_TYPE][MAX_GAMETYPE_NAME_ALIASES] = {
	[GT_FFA] = { "ffa", NULL, NULL },
	[GT_TOURNAMENT] = { "tournament", "duel", NULL },
	[GT_SINGLE_PLAYER] = { "single", "race", NULL },
	[GT_TEAM] = { "team", "tdm", NULL },
	[GT_CLAN_ARENA] = { "clanarena", "ca", NULL },
	[GT_CTF] = { "ctf", NULL, NULL },
	[GT_1FCTF] = { "oneflag", "1fctf", NULL },
	[GT_OBELISK] = { "obelisk", "overload", NULL },
	[GT_HARVESTER] = { "harvester", NULL, NULL },
	[GT_FREEZE] = { "freeze", "freezetag", NULL },
	[GT_DOMINATION] = { "domination", "dom", NULL },
	[GT_ATTACK_DEFEND] = { "attackdefend", "ad", NULL },
	[GT_RED_ROVER] = { "redrover", "rr", NULL }
};

/*
===================
G_SpawnGametypeMatchesFilter

Returns qtrue when the current gametype is permitted by the entity's
"gametype" spawn value, or when no filter is defined.
===================
*/
static qboolean G_SpawnGametypeMatchesFilter( const char *value ) {
	int				aliasIndex;

	if ( !value || !*value ) {
		return qtrue;
	}

	if ( g_gametype.integer < GT_FFA || g_gametype.integer >= GT_MAX_GAME_TYPE ) {
		return qtrue;
	}

	for ( aliasIndex = 0; aliasIndex < MAX_GAMETYPE_NAME_ALIASES; aliasIndex++ ) {
		const char *token = s_gametypeSpawnNames[g_gametype.integer][aliasIndex];

		if ( token && strstr( value, token ) ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
===================
G_SpawnGEntityFromSpawnVars

Spawn an entity and fill in all of the level fields from
level.spawnVars[], then call the class specfic spawn function
===================
*/
void G_SpawnGEntityFromSpawnVars( void ) {
	int			i;
	gentity_t	*ent;
	char		*s, *value;

	// get the next free entity
	ent = G_Spawn();

	for ( i = 0 ; i < level.numSpawnVars ; i++ ) {
		G_ParseField( level.spawnVars[i][0], level.spawnVars[i][1], ent );
	}

	// check for "notsingle" flag
	if ( g_gametype.integer == GT_SINGLE_PLAYER ) {
		G_SpawnInt( "notsingle", "0", &i );
		if ( i ) {
			G_FreeEntity( ent );
			return;
		}
	}
	// check for "notteam" flag (GT_FFA, GT_TOURNAMENT, GT_SINGLE_PLAYER)
	if ( g_gametype.integer >= GT_TEAM ) {
		G_SpawnInt( "notteam", "0", &i );
		if ( i ) {
			G_FreeEntity( ent );
			return;
		}
	} else {
		G_SpawnInt( "notfree", "0", &i );
		if ( i ) {
			G_FreeEntity( ent );
			return;
		}
	}

	G_SpawnInt( "notta", "0", &i );
	if ( i ) {
		G_FreeEntity( ent );
		return;
	}

	if ( G_SpawnString( "gametype", NULL, &value ) ) {
		if ( !G_SpawnGametypeMatchesFilter( value ) ) {
			G_FreeEntity( ent );
			return;
		}
	}

	// move editor origin to pos
	VectorCopy( ent->s.origin, ent->s.pos.trBase );
	VectorCopy( ent->s.origin, ent->r.currentOrigin );

	// if we didn't get a classname, don't bother spawning anything
	if ( !G_CallSpawn( ent ) ) {
		G_FreeEntity( ent );
	}
}



/*
====================
G_AddSpawnVarToken
====================
*/
char *G_AddSpawnVarToken( const char *string ) {
	int		l;
	char	*dest;

	l = strlen( string );
	if ( level.numSpawnVarChars + l + 1 > MAX_SPAWN_VARS_CHARS ) {
		G_Error( "G_AddSpawnVarToken: MAX_SPAWN_CHARS" );
	}

	dest = level.spawnVarChars + level.numSpawnVarChars;
	memcpy( dest, string, l+1 );

	level.numSpawnVarChars += l + 1;

	return dest;
}

/*
====================
G_ParseSpawnVars

Parses a brace bounded set of key / value pairs out of the
level's entity strings into level.spawnVars[]

This does not actually spawn an entity.
====================
*/
qboolean G_ParseSpawnVars( void ) {
	char		keyname[MAX_TOKEN_CHARS];
	char		com_token[MAX_TOKEN_CHARS];

	level.numSpawnVars = 0;
	level.numSpawnVarChars = 0;

	// parse the opening brace
	if ( !trap_GetEntityToken( com_token, sizeof( com_token ) ) ) {
		// end of spawn string
		return qfalse;
	}
	if ( com_token[0] != '{' ) {
		G_Error( "G_ParseSpawnVars: found %s when expecting {",com_token );
	}

	// go through all the key / value pairs
	while ( 1 ) {	
		// parse key
		if ( !trap_GetEntityToken( keyname, sizeof( keyname ) ) ) {
			G_Error( "G_ParseSpawnVars: EOF without closing brace" );
		}

		if ( keyname[0] == '}' ) {
			break;
		}
		
		// parse value	
		if ( !trap_GetEntityToken( com_token, sizeof( com_token ) ) ) {
			G_Error( "G_ParseSpawnVars: EOF without closing brace" );
		}

		if ( com_token[0] == '}' ) {
			G_Error( "G_ParseSpawnVars: closing brace without data" );
		}
		if ( level.numSpawnVars == MAX_SPAWN_VARS ) {
			G_Error( "G_ParseSpawnVars: MAX_SPAWN_VARS" );
		}
		level.spawnVars[ level.numSpawnVars ][0] = G_AddSpawnVarToken( keyname );
		level.spawnVars[ level.numSpawnVars ][1] = G_AddSpawnVarToken( com_token );
		level.numSpawnVars++;
	}

	return qtrue;
}



/*QUAKED worldspawn (0 0 0) ?

Every map should have exactly one worldspawn.
"music"		music wav file
"gravity"	800 is default gravity
"message"	Text to print during connection process
*/
void SP_worldspawn( void ) {
	char		*s;
	char		*atmosphere;
	int		trainingFlag;
	qboolean	trainingActive;

	G_SpawnString( "classname", "", &s );
	if ( Q_stricmp( s, "worldspawn" ) ) {
		G_Error( "SP_worldspawn: The first entity isn't 'worldspawn'" );
	}

	trainingFlag = 0;
	if ( G_SpawnInt( "trainingMap", "0", &trainingFlag ) && trainingFlag ) {
		trap_Cvar_Set( "g_training", "1" );
	}
	trap_Cvar_Update( &g_training );
	trainingActive = ( g_training.integer != 0 ) ? qtrue : qfalse;
	level.trainingMapActive = trainingActive;

	// make some data visible to connecting client
	trap_SetConfigstring( CS_GAME_VERSION, GAME_VERSION );

	trap_SetConfigstring( CS_LEVEL_START_TIME, va("%i", level.startTime ) );

	G_SpawnString( "music", "", &s );
	trap_SetConfigstring( CS_MUSIC, s );

	G_SpawnString( "message", "", &s );
	trap_SetConfigstring( CS_MESSAGE, s );				// map specific message

	trap_SetConfigstring( CS_MOTD, g_motd.string );	// message of the day

	G_SpawnString( "gravity", "800", &s );
	trap_Cvar_Set( "g_gravity", s );

	G_SpawnString( "enableDust", "0", &s );
	trap_Cvar_Set( "g_enableDust", s );

	G_SpawnString( "enableBreath", "0", &s );
	trap_Cvar_Set( "g_enableBreath", s );

	G_SpawnString( "atmosphere", "", &atmosphere );
	if ( atmosphere && atmosphere[0] ) {
		G_SetWorldspawnAtmosphere( atmosphere );
	} else {
		trap_Cvar_Update( &g_forcedAtmosphere );
		G_SetWorldspawnAtmosphere( g_forcedAtmosphere.string );
	}

	g_entities[ENTITYNUM_WORLD].s.number = ENTITYNUM_WORLD;
	g_entities[ENTITYNUM_WORLD].classname = "worldspawn";

	// see if we want a warmup time
	trap_SetConfigstring( CS_WARMUP, "" );
	trap_SetConfigstring( CS_MATCH_STATE, "" );
	if ( trainingActive ) {
		level.warmupTime = 0;
	} else if ( g_restarted.integer ) {
		trap_Cvar_Set( "g_restarted", "0" );
		level.warmupTime = 0;
	} else if ( g_doWarmup.integer ) { // Turn it on
		level.warmupTime = -1;
		trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
		G_LogPrintf( "Warmup:\n" );
	}

}



/*
=============
G_UpdateSpawnQueueFlag

Recomputes whether any clients are currently queued for delayed spawns.
=============
*/
static void G_UpdateSpawnQueueFlag( void ) {
	int             i;

	level.spawnQueueActive = qfalse;

	for ( i = 0; i < level.maxclients; ++i ) {
		if ( level.clientSpawnQueued[i] ) {
		        level.spawnQueueActive = qtrue;
		        break;
		}
	}
}

/*
=============
G_CountQueuedSpawns

Returns the number of clients currently waiting on delayed spawn slots.
=============
*/
static int G_CountQueuedSpawns( void ) {
	int		i;
	int		queued;

	queued = 0;
	for ( i = 0; i < level.maxclients; ++i ) {
		if ( level.clientSpawnQueued[i] ) {
			++queued;
		}
	}

	return queued;
}

/*
=============
G_FactoryRespawnWindowActive

Returns qtrue when an active factory configures staggered respawn delays.
=============
*/
static qboolean G_FactoryRespawnWindowActive( void ) {
	if ( !g_factory.string[0] ) {
		return qfalse;
	}

	if ( g_factoryCvarConfig.respawnDelayMinMilliseconds <= 0
		&& g_factoryCvarConfig.respawnDelayMaxMilliseconds <= 0 ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_FactoryComputeRespawnDelay

Maps a queue slot to a millisecond delay inside the configured min/max window.
=============
*/
static int G_FactoryComputeRespawnDelay( int slotIndex ) {
	int		minDelay;
	int		maxDelay;
	int		slotCount;
	int		span;
	int		offset;

	minDelay = g_factoryCvarConfig.respawnDelayMinMilliseconds;
	maxDelay = g_factoryCvarConfig.respawnDelayMaxMilliseconds;
	if ( minDelay < 0 ) {
		minDelay = 0;
	}
	if ( maxDelay < minDelay ) {
		maxDelay = minDelay;
	}

	slotCount = g_maxDeferredSpawns.integer;
	if ( slotCount <= 0 ) {
		slotCount = 1;
	}

	if ( slotCount == 1 || maxDelay == minDelay ) {
		return maxDelay;
	}

	if ( slotIndex < 0 ) {
		slotIndex = 0;
	}
	if ( slotIndex > slotCount - 1 ) {
		slotIndex = slotCount - 1;
	}

	span = maxDelay - minDelay;
	offset = ( span * slotIndex ) / ( slotCount - 1 );
	return minDelay + offset;
}

/*
=============
G_ClearQueuedSpawnState

Resets the queue bookkeeping for a particular client number.
=============
*/
static void G_ClearQueuedSpawnState( int clientNum ) {
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}

	level.clientSpawnQueued[clientNum] = qfalse;
	level.clientSpawnInitial[clientNum] = qfalse;
	level.clientSpawnNeedsEffect[clientNum] = qfalse;
	level.clientFactoryLoadoutQueued[clientNum] = qfalse;
	level.clientSpawnRequestTime[clientNum] = 0;
}

/*
=============
G_InitSpawnQueue

Initialises the spawn delay bookkeeping used to mimic Quake Live's factory scheduling.
=============
*/
void G_InitSpawnQueue( void ) {
	int             i;

	level.nextWarmupSpawnTime = 0;
	level.spawnQueueActive = qfalse;

	for ( i = 0; i < MAX_CLIENTS; ++i ) {
		level.clientSpawnRequestTime[i] = 0;
		level.clientSpawnQueued[i] = qfalse;
		level.clientSpawnInitial[i] = qfalse;
		level.clientSpawnNeedsEffect[i] = qfalse;
		level.clientFactoryLoadoutQueued[i] = qfalse;
	}
}

/*
=============
G_SyncMatchFactoryConfigToLevel

Copies the active match factory toggle values into level state for quick access.
=============
*/
void G_SyncMatchFactoryConfigToLevel( void ) {
	level.matchAllowItemDrops = g_matchFactoryConfig.factoryAllowItemDrops;
	level.matchAllowItemBounce = g_matchFactoryConfig.factoryAllowItemBounce;
}

/*
=============
G_ExecuteQueuedClientSpawn

Think callback that finalises delayed spawn requests.
=============
*/
static void G_ExecuteQueuedClientSpawn( gentity_t *ent ) {
	int             clientNum;
	qboolean        initialSpawn;
	qboolean        needsEffect;
	qboolean        announceEntry;

	if ( !ent || !ent->client ) {
		return;
	}

	clientNum = ent - g_entities;
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}

	if ( !level.clientSpawnQueued[clientNum] ) {
		return;
	}

	initialSpawn = level.clientSpawnInitial[clientNum];
	needsEffect = level.clientSpawnNeedsEffect[clientNum];
	announceEntry = ( initialSpawn && needsEffect && ent->client->sess.sessionTeam != TEAM_SPECTATOR && g_gametype.integer != GT_TOURNAMENT ) ? qtrue : qfalse;

	ent->think = NULL;
	ent->nextthink = 0;

	G_ClearQueuedSpawnState( clientNum );

	ClientSpawn( ent );

	if ( needsEffect && ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		gentity_t       *tent;

		tent = G_TempEntity( ent->client->ps.origin, EV_PLAYER_TELEPORT_IN );
		tent->s.clientNum = ent->s.clientNum;
	}

	if ( announceEntry ) {
		trap_SendServerCommand( -1, va( "print \"%s" S_COLOR_WHITE " entered the game\n\"", ent->client->pers.netname ) );
	}

	G_UpdateSpawnQueueFlag();
}

/*
=============
G_RequestClientSpawn

Queues or executes spawn requests, applying Quake Live factory delays where appropriate.
=============
*/
qboolean G_RequestClientSpawn( gentity_t *ent, qboolean warmupSpawn, qboolean initialSpawn ) {
	int             clientNum;
	int             delayMs;
	int             scheduledTime;
	int             baseTime;
	qboolean        needsEffect;
	int		queuedCount;

	if ( !ent || !ent->client ) {
		return qfalse;
	}

	clientNum = ent - g_entities;
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return qfalse;
	}

	queuedCount = 0;
	if ( warmupSpawn ) {
		delayMs = g_matchFactoryConfig.factoryWarmupSpawnDelayMilliseconds;
		if ( delayMs > 0 && g_maxDeferredSpawns.integer > 0 ) {
			queuedCount = G_CountQueuedSpawns();
			if ( queuedCount >= g_maxDeferredSpawns.integer ) {
				delayMs = 0;
			}
		}
	} else if ( G_FactoryRespawnWindowActive() ) {
		queuedCount = G_CountQueuedSpawns();
		if ( g_maxDeferredSpawns.integer > 0 && queuedCount >= g_maxDeferredSpawns.integer ) {
			delayMs = 0;
		} else {
			delayMs = G_FactoryComputeRespawnDelay( queuedCount );
		}
	} else {
		delayMs = g_matchFactoryConfig.factoryRespawnDelayMilliseconds;
		if ( delayMs > 0 && g_maxDeferredSpawns.integer > 0 ) {
			queuedCount = G_CountQueuedSpawns();
			if ( queuedCount >= g_maxDeferredSpawns.integer ) {
				delayMs = 0;
			}
		}
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		delayMs = 0;
	}

	if ( delayMs <= 0 ) {
		ent->think = NULL;
		ent->nextthink = 0;
		G_ClearQueuedSpawnState( clientNum );
		ClientSpawn( ent );
		return qtrue;
	}

	baseTime = level.time;
	if ( warmupSpawn && g_matchFactoryConfig.factoryWarmupSpawnDelayMilliseconds > 0 ) {
		if ( level.nextWarmupSpawnTime > baseTime ) {
		        baseTime = level.nextWarmupSpawnTime;
		}
		scheduledTime = baseTime + delayMs;
		level.nextWarmupSpawnTime = scheduledTime;
	} else {
		scheduledTime = baseTime + delayMs;
	}

	needsEffect = ( ent->client->sess.sessionTeam != TEAM_SPECTATOR ) ? qtrue : qfalse;

	level.clientSpawnRequestTime[clientNum] = scheduledTime;
	level.clientSpawnQueued[clientNum] = qtrue;
	level.clientSpawnInitial[clientNum] = initialSpawn ? qtrue : qfalse;
	level.clientSpawnNeedsEffect[clientNum] = needsEffect;
	level.clientFactoryLoadoutQueued[clientNum] = qtrue;
	level.spawnQueueActive = qtrue;

	ent->think = G_ExecuteQueuedClientSpawn;
	ent->nextthink = scheduledTime;

	return qfalse;
}

/*
==============
G_SpawnEntitiesFromString

Parses textual entity definitions out of an entstring and spawns gentities.
==============
*/
void G_SpawnEntitiesFromString( void ) {
	// allow calls to G_Spawn*()
	level.spawning = qtrue;
	level.numSpawnVars = 0;

	// the worldspawn is not an actual entity, but it still
	// has a "spawn" function to perform any global setup
	// needed by a level (setting configstrings or cvars, etc)
	if ( !G_ParseSpawnVars() ) {
		G_Error( "SpawnEntities: no entities" );
	}
	SP_worldspawn();

	// parse ents
	while( G_ParseSpawnVars() ) {
		G_SpawnGEntityFromSpawnVars();
	}	

	level.spawning = qfalse;			// any future calls to G_Spawn*() will be errors
	G_MatchConfig_UpdateConfigstrings();
}

