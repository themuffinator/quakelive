#include "platform_services.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "platform_config.h"

static void QL_SetAuthResponse( ql_auth_response_t *response, qlAuthResult result, const char *format, ... ) {
    if ( !response ) {
        return;
    }

    response->result = result;

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

    if ( credential->length == 0 ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "steamworks_ticket:{\"error\":\"empty\"}" );
        return qtrue;
    }

    QL_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "steamworks_ticket:{\"steam_id\":\"%s\",\"callbacks\":true}", credential->value );
    return qtrue;
#else
    (void)credential;
    (void)response;
    return qfalse;
#endif
}

static qboolean QL_OpenAuth_AuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
#if QL_PLATFORM_HAS_OPEN_STEAM
    if ( !credential || credential->length == 0 ) {
        QL_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "{\"provider\":\"open-auth\",\"error\":\"missing_token\"}" );
        return qtrue;
    }

    const char *ns = "standalone";

    if ( credential->kind == QL_AUTH_CREDENTIAL_STEAM ) {
        ns = "steam";
    }

    QL_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "{\"provider\":\"open-auth\",\"namespace\":\"%s\",\"token\":\"%s\"}", ns, credential->value );
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
            QL_SetAuthResponse( response, response->result,
                "{\"provider\":\"hybrid\",\"delegated_to\":\"open-auth\",\"token\":\"%s\"}", credential->value );
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
