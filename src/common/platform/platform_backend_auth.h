#ifndef PLATFORM_BACKEND_AUTH_H
#define PLATFORM_BACKEND_AUTH_H

#include "platform_config.h"
#include "platform_backend_shared.h"

#if QL_BUILD_STEAMWORKS
qboolean QL_PlatformBackendSteamworks_Authenticate( const ql_auth_credential_t *credential, ql_auth_response_t *response );
#else
static inline qboolean QL_PlatformBackendSteamworks_Authenticate( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    (void)credential;
    (void)response;
    return qfalse;
}
#endif

#if QL_BUILD_OPEN_STEAM
qboolean QL_PlatformBackendOpenSteam_Authenticate( const ql_auth_credential_t *credential, ql_auth_response_t *response );
#else
static inline qboolean QL_PlatformBackendOpenSteam_Authenticate( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    (void)credential;
    (void)response;
    return qfalse;
}
#endif

#endif // PLATFORM_BACKEND_AUTH_H
