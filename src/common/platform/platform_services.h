#ifndef PLATFORM_SERVICES_H
#define PLATFORM_SERVICES_H

#include "../auth_credentials.h"

typedef struct {
    qboolean supported;
    const char *provider;
} ql_platform_feature_descriptor;

typedef qboolean (*ql_platform_auth_request_fn)( const ql_auth_credential_t *credential, ql_auth_response_t *response );

typedef struct {
    ql_platform_feature_descriptor descriptor;
    ql_platform_auth_request_fn request;
} ql_platform_auth_feature;

typedef struct {
    ql_platform_auth_feature auth;
    ql_platform_feature_descriptor matchmaking;
    ql_platform_feature_descriptor workshop;
    ql_platform_feature_descriptor overlay;
    ql_platform_feature_descriptor stats;
} ql_platform_service_table;

const ql_platform_service_table *QL_GetPlatformServices( void );

qboolean QL_Platform_RunMockAuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response );

#endif // PLATFORM_SERVICES_H
