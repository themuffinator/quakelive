#ifndef PLATFORM_SERVICES_H
#define PLATFORM_SERVICES_H

#include "../auth_credentials.h"

typedef struct {
qboolean compiled;
qboolean initialised;
const char *provider;
} ql_platform_feature_descriptor;

typedef struct {
    ql_platform_feature_descriptor auth;
    ql_platform_feature_descriptor matchmaking;
    ql_platform_feature_descriptor workshop;
    ql_platform_feature_descriptor overlay;
    ql_platform_feature_descriptor stats;
} ql_platform_service_table;

const ql_platform_service_table *QL_GetPlatformServices( void );
const char *QL_DescribePlatformFeaturePolicy( const ql_platform_feature_descriptor *descriptor );

#endif // PLATFORM_SERVICES_H
