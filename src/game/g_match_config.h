#ifndef G_MATCH_CONFIG_H
#define G_MATCH_CONFIG_H

#include "g_config.h"

extern matchFactoryConfig_t g_matchFactoryConfig;

void G_InitMatchFactoryConfig( void );
void G_UpdateMatchFactoryConfig( void );
void G_MatchConfig_UpdateConfigstrings( void );

#endif // G_MATCH_CONFIG_H
