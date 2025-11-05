#include "platform_services.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "platform_config.h"

static void QL_FormatCredentialPreview( const ql_auth_credential_t *credential, char *buffer, size_t bufferSize ) {
    if ( !buffer || bufferSize == 0 ) {
        return;
    }

    buffer[0] = '\0';

    if ( !credential || credential->length == 0 ) {
        Q_strncpyz( buffer, "<empty>", bufferSize );
        return;
    }

    if ( credential->length <= 12 ) {
        Q_strncpyz( buffer, credential->value, bufferSize );
        return;
    }

    char head[8];
    char tail[8];

    Q_strncpyz( head, credential->value, sizeof( head ) );

    if ( credential->length >= 4 ) {
        Q_strncpyz( tail, credential->value + credential->length - 4, sizeof( tail ) );
    } else {
        Q_strncpyz( tail, credential->value, sizeof( tail ) );
    }

    Com_sprintf( buffer, bufferSize, "%s…%s", head, tail );
}

static qlAuthOutcome QL_MapOutcomeFromResult( qlAuthResult result ) {
    switch ( result ) {
        case QL_AUTH_RESULT_ACCEPTED:
            return QL_AUTH_OUTCOME_SUCCESS;
        case QL_AUTH_RESULT_PENDING:
            return QL_AUTH_OUTCOME_RETRY;
        default:
            return QL_AUTH_OUTCOME_FAILURE;
    }
}

static void QL_SetAuthResponse( ql_auth_response_t *response, qlAuthResult result, const char *format, ... ) {
    if ( !response ) {
        return;
    }

    response->result = result;
    response->outcome = QL_MapOutcomeFromResult( result );

    if ( !format ) {
        response->message[0] = '\0';
        return;
    }

    va_list args;
    va_start( args, format );
    vsnprintf( response->message, sizeof( response->message ), format, args );
    va_end( args );
}

static qboolean QL_Steamworks_AuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
#if QL_PLATFORM_HAS_STEAMWORKS
    if ( !credential || credential->kind != QL_AUTH_CREDENTIAL_STEAM ) {
        return qfalse;
    }

    char preview[32];
    QL_FormatCredentialPreview( credential, preview, sizeof( preview ) );

    if ( credential->length < 16 ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket rejected: payload too short" );
        return qtrue;
    }

    if ( strstr( credential->value, "retry" ) ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_PENDING, "Steam service busy, retry with refreshed ticket" );
        return qtrue;
    }

    if ( strstr( credential->value, "denied" ) || strstr( credential->value, "invalid" ) ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam backend denied the ticket" );
        return qtrue;
    }

    QL_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "Steam session established (ticket=%s)", preview );
    return qtrue;
#else
    (void)credential;
    (void)response;
    return qfalse;
#endif
}

static qboolean QL_OpenAuth_AuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
#if QL_PLATFORM_HAS_OPEN_STEAM
    if ( !credential ) {
        return qfalse;
    }

    qboolean isStandalone = credential->kind == QL_AUTH_CREDENTIAL_STANDALONE_TOKEN;
    qboolean isSteamFallback = credential->kind == QL_AUTH_CREDENTIAL_STEAM;

    if ( !isStandalone && !isSteamFallback ) {
        return qfalse;
    }

    char preview[32];
    QL_FormatCredentialPreview( credential, preview, sizeof( preview ) );

    if ( credential->length == 0 ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Open adapter rejected credential: payload missing" );
        return qtrue;
    }

    if ( isStandalone ) {
        if ( credential->length < 12 ) {
            QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
                "Standalone token rejected: payload too short" );
            return qtrue;
        }

        if ( strstr( credential->value, "refresh" ) ) {
            QL_SetAuthResponse( response, QL_AUTH_RESULT_PENDING,
                "Launcher token expired, request a refresh" );
            return qtrue;
        }

        if ( strstr( credential->value, "revoke" ) || strstr( credential->value, "denied" ) ) {
            QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
                "Launcher revoked the token" );
            return qtrue;
        }

        QL_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
            "Standalone token accepted (token=%s)", preview );
        return qtrue;
    }

    if ( credential->length < 16 ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Open adapter rejected Steam credential: payload too short" );
        return qtrue;
    }

    if ( strstr( credential->value, "denied" ) || strstr( credential->value, "invalid" ) ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED,
            "Open adapter respected Steam denial" );
        return qtrue;
    }

    QL_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "Open adapter accepted Steam ticket (ticket=%s)", preview );
    return qtrue;
#else
    (void)credential;
    (void)response;
    return qfalse;
#endif
}

static qboolean QL_HybridAuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    qboolean handled = qfalse;

#if QL_PLATFORM_HAS_STEAMWORKS
    if ( QL_Steamworks_AuthFlow( credential, response ) ) {
        handled = qtrue;

        if ( response->result == QL_AUTH_RESULT_ACCEPTED ) {
            return qtrue;
        }
    }
#endif

#if QL_PLATFORM_HAS_OPEN_STEAM
    if ( QL_OpenAuth_AuthFlow( credential, response ) ) {
        if ( handled && response->result == QL_AUTH_RESULT_ACCEPTED ) {
            char preview[32];
            QL_FormatCredentialPreview( credential, preview, sizeof( preview ) );

            QL_SetAuthResponse( response, response->result,
                "Hybrid fallback accepted credential via open adapter (token=%s)", preview );
        }

        return response->result == QL_AUTH_RESULT_ACCEPTED ? qtrue : qfalse;
    }
#endif

    return handled;
}

static void QL_FinaliseDescriptor( ql_platform_feature_descriptor *descriptor, const char *fallbackLabel ) {
    if ( !descriptor ) {
        return;
    }

    if ( !descriptor->provider && fallbackLabel ) {
        descriptor->provider = fallbackLabel;
    }
}

static ql_platform_service_table QL_BuildServiceTable( void ) {
    ql_platform_service_table table;
    memset( &table, 0, sizeof( table ) );

#if QL_PLATFORM_BUILD_HYBRID
    table.auth.descriptor.supported = qtrue;
    table.auth.descriptor.provider = "Hybrid";
    table.auth.request = QL_HybridAuthFlow;
#elif QL_PLATFORM_HAS_STEAMWORKS
    table.auth.descriptor.supported = qtrue;
    table.auth.descriptor.provider = "Steamworks";
    table.auth.request = QL_Steamworks_AuthFlow;
#elif QL_PLATFORM_HAS_OPEN_STEAM
    table.auth.descriptor.supported = qtrue;
    table.auth.descriptor.provider = "Open Steam Adapter";
    table.auth.request = QL_OpenAuth_AuthFlow;
#endif

#if QL_PLATFORM_HAS_STEAMWORKS
    table.matchmaking.supported = qtrue;
    table.matchmaking.provider = "Steamworks";
    table.workshop.supported = qtrue;
    table.workshop.provider = "Steam UGC";
    table.overlay.supported = qtrue;
    table.overlay.provider = "Steam Overlay";
    table.stats.supported = qtrue;
    table.stats.provider = "Steam Stats";
#endif

#if QL_PLATFORM_HAS_OPEN_STEAM
    table.matchmaking.supported = qtrue;
    table.matchmaking.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steamworks + GameNetworkingSockets" : "GameNetworkingSockets";
    table.workshop.supported = qtrue;
    table.workshop.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam UGC + REST Mirror" : "REST UGC Service";
    table.overlay.supported = qtrue;
    table.overlay.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Overlay + In-Process UI" : "In-Process UI Overlay";
    table.stats.supported = qtrue;
    table.stats.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Stats + Metrics REST" : "Metrics REST Adapter";
#endif

    QL_FinaliseDescriptor( &table.matchmaking, "Unavailable" );
    QL_FinaliseDescriptor( &table.workshop, "Unavailable" );
    QL_FinaliseDescriptor( &table.overlay, "Unavailable" );
    QL_FinaliseDescriptor( &table.stats, "Unavailable" );

    if ( !table.auth.request ) {
        table.auth.descriptor.supported = qfalse;
        table.auth.descriptor.provider = "Unavailable";
    }

    return table;
}

const ql_platform_service_table *QL_GetPlatformServices( void ) {
    static ql_platform_service_table table;
    static qboolean initialised = qfalse;

    if ( !initialised ) {
        table = QL_BuildServiceTable();
        initialised = qtrue;
    }

    return &table;
}

qboolean QL_Platform_RunMockAuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !response ) {
        return qfalse;
    }

    QL_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, NULL );

    if ( !credential ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "No credential provided." );
        return qfalse;
    }

    const ql_platform_service_table *services = QL_GetPlatformServices();

    if ( !services->auth.descriptor.supported || !services->auth.request ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "No authentication backend is compiled in." );
        return qfalse;
    }

    if ( !services->auth.request( credential, response ) ) {
        if ( response->message[0] == '\0' ) {
            QL_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "No provider accepted credential kind %d.", credential->kind );
        }

        return qfalse;
    }

    return response->result == QL_AUTH_RESULT_ACCEPTED ? qtrue : qfalse;
}
