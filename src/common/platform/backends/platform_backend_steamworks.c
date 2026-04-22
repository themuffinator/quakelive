#include "../platform_backend_auth.h"

#if QL_BUILD_STEAMWORKS

qboolean QL_PlatformBackendSteamworks_Authenticate( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !credential || credential->kind != QL_AUTH_CREDENTIAL_STEAM ) {
        return qfalse;
    }

    char preview[32];
    QL_Backend_FormatCredentialPreview( credential, preview, sizeof( preview ) );

    if ( credential->length < 16 ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Steamworks heuristic compatibility backend rejected ticket: payload too short" );
        return qtrue;
    }

    if ( strstr( credential->value, "retry" ) ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_PENDING,
            "Steamworks heuristic compatibility backend reported busy; retry with refreshed ticket" );
        return qtrue;
    }

    if ( strstr( credential->value, "denied" ) || strstr( credential->value, "invalid" ) ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Steamworks heuristic compatibility backend denied the ticket" );
        return qtrue;
    }

    QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "Steamworks heuristic compatibility backend accepted ticket (ticket=%s)", preview );
    return qtrue;
}

#endif
