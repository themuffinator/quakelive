#include "../platform_backend_auth.h"

#if QL_BUILD_OPEN_STEAM

qboolean QL_PlatformBackendOpenSteam_Authenticate( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !credential ) {
        return qfalse;
    }

    qboolean isStandalone = credential->kind == QL_AUTH_CREDENTIAL_STANDALONE_TOKEN;
    qboolean isSteamFallback = credential->kind == QL_AUTH_CREDENTIAL_STEAM;

    if ( !isStandalone && !isSteamFallback ) {
        return qfalse;
    }

    char preview[32];
    QL_Backend_FormatCredentialPreview( credential, preview, sizeof( preview ) );

    if ( credential->length == 0 ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Open adapter heuristic compatibility backend rejected credential: payload missing" );
        return qtrue;
    }

    if ( isStandalone ) {
        if ( credential->length < 12 ) {
            QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
                "Open adapter heuristic compatibility backend rejected standalone token: payload too short" );
            return qtrue;
        }

        if ( strstr( credential->value, "refresh" ) ) {
            QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_PENDING,
                "Open adapter heuristic compatibility backend requested launcher token refresh" );
            return qtrue;
        }

        if ( strstr( credential->value, "revoke" ) || strstr( credential->value, "denied" ) ) {
            QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
                "Open adapter heuristic compatibility backend treated token as revoked" );
            return qtrue;
        }

        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
            "Open adapter heuristic compatibility backend accepted standalone token (token=%s)", preview );
        return qtrue;
    }

    if ( credential->length < 16 ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Open adapter heuristic compatibility backend rejected Steam credential: payload too short" );
        return qtrue;
    }

    if ( strstr( credential->value, "denied" ) || strstr( credential->value, "invalid" ) ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Open adapter heuristic compatibility backend respected Steam denial" );
        return qtrue;
    }

    QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "Open adapter heuristic compatibility backend accepted Steam ticket (ticket=%s)", preview );
    return qtrue;
}

#endif
