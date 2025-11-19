#ifndef G_LEGACY_CVARS_H
#define G_LEGACY_CVARS_H

#include <stddef.h>
#include "q_shared.h"

typedef struct legacyCvarAlias_s {
	vmCvar_t	*primary;
	const char	*primaryName;
	vmCvar_t	*alias;
	const char	*aliasName;
	const char	*defaultString;
	int		cvarFlags;
	int		primaryModCount;
	int		aliasModCount;
} legacyCvarAlias_t;

/*
=============
LegacyCvar_RegisterAliases

Registers legacy alias CVars and synchronises their initial values with the primary handles.
=============
*/
static ID_INLINE void LegacyCvar_RegisterAliases( legacyCvarAlias_t *aliases, size_t aliasCount ) {
	if ( !aliases || aliasCount == 0 ) {
		return;
	}

	for ( size_t i = 0; i < aliasCount; ++i ) {
		legacyCvarAlias_t *binding = &aliases[i];
		const char *defaultValue;

		if ( !binding->primary || !binding->alias || !binding->primaryName || !binding->aliasName ) {
			continue;
		}

		defaultValue = binding->defaultString ? binding->defaultString : "";
		trap_Cvar_Register( binding->alias, binding->aliasName, defaultValue, binding->cvarFlags );
		trap_Cvar_Update( binding->alias );
		trap_Cvar_Update( binding->primary );

		binding->aliasModCount = binding->alias->modificationCount;
		binding->primaryModCount = binding->primary->modificationCount;

		if ( binding->defaultString && Q_stricmp( binding->alias->string, binding->defaultString ) != 0 &&
				Q_stricmp( binding->alias->string, binding->primary->string ) != 0 ) {
			trap_Cvar_Set( binding->primaryName, binding->alias->string );
			trap_Cvar_Update( binding->primary );
			binding->primaryModCount = binding->primary->modificationCount;
		} else if ( Q_stricmp( binding->alias->string, binding->primary->string ) != 0 ) {
			trap_Cvar_Set( binding->aliasName, binding->primary->string );
			trap_Cvar_Update( binding->alias );
			binding->aliasModCount = binding->alias->modificationCount;
		}
	}
}

/*
=============
LegacyCvar_UpdateAliases

Keeps the legacy alias CVars mirrored with their primary counterparts.
=============
*/
static ID_INLINE void LegacyCvar_UpdateAliases( legacyCvarAlias_t *aliases, size_t aliasCount ) {
	if ( !aliases || aliasCount == 0 ) {
		return;
	}

	for ( size_t i = 0; i < aliasCount; ++i ) {
		legacyCvarAlias_t *binding = &aliases[i];
		qboolean aliasChanged;
		qboolean primaryChanged;

		if ( !binding->primary || !binding->alias || !binding->primaryName || !binding->aliasName ) {
			continue;
		}

		trap_Cvar_Update( binding->alias );

		aliasChanged = ( binding->aliasModCount != binding->alias->modificationCount );
		primaryChanged = ( binding->primaryModCount != binding->primary->modificationCount );

		if ( aliasChanged ) {
			binding->aliasModCount = binding->alias->modificationCount;
			if ( Q_stricmp( binding->alias->string, binding->primary->string ) != 0 ) {
				trap_Cvar_Set( binding->primaryName, binding->alias->string );
				trap_Cvar_Update( binding->primary );
				binding->primaryModCount = binding->primary->modificationCount;
				continue;
			}
		}

		if ( primaryChanged ) {
			binding->primaryModCount = binding->primary->modificationCount;
			if ( Q_stricmp( binding->alias->string, binding->primary->string ) != 0 ) {
				trap_Cvar_Set( binding->aliasName, binding->primary->string );
				trap_Cvar_Update( binding->alias );
				binding->aliasModCount = binding->alias->modificationCount;
			}
		}
	}
}

#endif // G_LEGACY_CVARS_H
