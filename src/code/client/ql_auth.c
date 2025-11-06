#include "client.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "../../common/ql_auth_service.h"
#include "../../common/platform/platform_backend_auth.h"
#include "../../common/platform/platform_services.h"

typedef struct {
    ql_auth_request_descriptor_t descriptor;
    const char *logPrefix;
} ql_client_auth_transport_t;

static qlAuthOutcome QL_ClientAuth_MapOutcome( qlAuthResult result ) {
    switch ( result ) {
        case QL_AUTH_RESULT_ACCEPTED:
            return QL_AUTH_OUTCOME_SUCCESS;
        case QL_AUTH_RESULT_PENDING:
            return QL_AUTH_OUTCOME_RETRY;
        default:
            return QL_AUTH_OUTCOME_FAILURE;
    }
}

const char *QL_DescribeAuthOutcome( const ql_auth_response_t *response ) {
    if ( !response ) {
        return "unknown";
    }

    switch ( response->outcome ) {
        case QL_AUTH_OUTCOME_SUCCESS:
            return "success";
        case QL_AUTH_OUTCOME_RETRY:
            return "retry";
        case QL_AUTH_OUTCOME_FAILURE:
            return "failure";
        default:
            return "unknown";
    }
}

static void QL_ClientAuth_SetResponse( ql_auth_response_t *response, qlAuthResult result, const char *format, ... ) {
    if ( !response ) {
        return;
    }

    response->result = result;
    response->outcome = QL_ClientAuth_MapOutcome( result );

    if ( !format ) {
        response->message[0] = '\0';
        return;
    }

    va_list args;
    va_start( args, format );
    vsnprintf( response->message, sizeof( response->message ), format, args );
    va_end( args );
}

static void QL_ClientAuth_LogStage( const ql_client_auth_transport_t *transport, const char *stage, const char *detail ) {
    if ( !transport || !stage || !detail ) {
        return;
    }

    Com_Printf( "[auth] %s %s (%s): %s\n",
        transport->logPrefix,
        stage,
        transport->descriptor.endpoint ? transport->descriptor.endpoint : "<none>",
        detail );
}

static void QL_ClientAuth_LogResponse( const ql_client_auth_transport_t *transport, const ql_auth_response_t *response ) {
    if ( !transport || !response ) {
        return;
    }

    Com_Printf( "[auth] %s result -> outcome=%s, message=\"%s\"\n",
        transport->logPrefix,
        QL_DescribeAuthOutcome( response ),
        response->message );
}

static void QL_ClientAuth_TokenPreview( const ql_auth_credential_t *credential, char *buffer, size_t bufferSize ) {
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
    Q_strncpyz( tail, credential->value + credential->length - 4, sizeof( tail ) );

    Com_sprintf( buffer, bufferSize, "%s…%s", head, tail );
}

static qboolean QL_ClientAuth_InvokeBackend( qboolean (*backend)( const ql_auth_credential_t *, ql_auth_response_t * ), const ql_auth_credential_t *credential, ql_auth_response_t *response, const char *label ) {
    if ( !backend || !credential ) {
        return qfalse;
    }

    qboolean handled = backend( credential, response );

    if ( handled ) {
        return qtrue;
    }

    if ( response && label ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
            "%s backend unavailable in this build", label );
    }

    return qfalse;
}

static qboolean QL_ClientAuth_HandleSteamworksTicket( const ql_client_auth_transport_t *transport, const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    (void)transport;

    return QL_ClientAuth_InvokeBackend( QL_PlatformBackendSteamworks_Authenticate,
        credential, response, "Steamworks" );
}

static qboolean QL_ClientAuth_HandleOpenSteamTicket( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    return QL_ClientAuth_InvokeBackend( QL_PlatformBackendOpenSteam_Authenticate,
        credential, response, "Open Steam Adapter" );
}

static qboolean QL_ClientAuth_HandleStandaloneToken( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !credential || credential->kind != QL_AUTH_CREDENTIAL_STANDALONE_TOKEN ) {
        return qfalse;
    }

    return QL_ClientAuth_InvokeBackend( QL_PlatformBackendOpenSteam_Authenticate,
        credential, response, "Open Steam Adapter" );
}

static qboolean QL_ClientAuth_HandleHybridSteam( const ql_client_auth_transport_t *transport, const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    ql_auth_response_t steamResponse;
    memset( &steamResponse, 0, sizeof( steamResponse ) );

    qboolean handled = QL_ClientAuth_HandleSteamworksTicket( transport, credential, &steamResponse );

    if ( handled && steamResponse.result == QL_AUTH_RESULT_ACCEPTED ) {
        *response = steamResponse;
        return qtrue;
    }

    qboolean fallbackEligible = !handled || steamResponse.result == QL_AUTH_RESULT_PENDING;
    if ( fallbackEligible ) {
        qboolean fallbackHandled = QL_ClientAuth_HandleOpenSteamTicket( credential, response );

        if ( fallbackHandled ) {
            if ( response->result == QL_AUTH_RESULT_ACCEPTED ) {
                char preview[32];
                QL_ClientAuth_TokenPreview( credential, preview, sizeof( preview ) );

                QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ACCEPTED,
                    "Hybrid fallback accepted credential via open adapter (token=%s)", preview );
            }

            return qtrue;
        }
    }

    if ( handled ) {
        *response = steamResponse;
        return qtrue;
    }

    return qfalse;
}

static qboolean QL_ClientAuth_DispatchSteam( const ql_client_auth_transport_t *transport, const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !transport || !credential ) {
        return qfalse;
    }

    const char *provider = transport->descriptor.provider ? transport->descriptor.provider : "";

    if ( !Q_stricmp( provider, "Hybrid" ) ) {
        return QL_ClientAuth_HandleHybridSteam( transport, credential, response );
    }

    if ( !Q_stricmp( provider, "Open Steam Adapter" ) ) {
        return QL_ClientAuth_HandleOpenSteamTicket( credential, response );
    }

    return QL_ClientAuth_HandleSteamworksTicket( transport, credential, response );
}

qboolean QL_Auth_ExecuteRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !credential || !response ) {
        return qfalse;
    }

    const ql_platform_service_table *services = QL_GetPlatformServices();
    const char *provider = services && services->auth.provider ? services->auth.provider : "dispatcher";
    const char *endpoint = "<unroutable>";

    switch ( credential->kind ) {
        case QL_AUTH_CREDENTIAL_STEAM:
            endpoint = "/steam/session/validate";
            break;
        case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
            endpoint = "/launcher/auth/verify";
            break;
        default:
            break;
    }

    ql_client_auth_transport_t transport = {
        { provider, endpoint },
        provider
    };

    if ( !services || !services->auth.supported ) {
        transport.logPrefix = "dispatcher";
    }

    QL_ClientAuth_LogStage( &transport, "dispatch", "submitting credential" );

    char preview[32];
    QL_ClientAuth_TokenPreview( credential, preview, sizeof( preview ) );

    switch ( credential->kind ) {
        case QL_AUTH_CREDENTIAL_STEAM:
            Com_Printf( "[auth] %s payload summary: ticket=%s (len=%zu)\n",
                transport.logPrefix, preview, credential->length );
            break;
        case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
            Com_Printf( "[auth] %s payload summary: token=%s (len=%zu)\n",
                transport.logPrefix, preview, credential->length );
            break;
        default:
            Com_Printf( "[auth] %s payload summary: credential=%s (len=%zu)\n",
                transport.logPrefix, preview, credential->length );
            break;
    }

    if ( !services || !services->auth.supported ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
            "No authentication backend is compiled in." );
        QL_ClientAuth_LogResponse( &transport, response );
        return qfalse;
    }

    qboolean handled = qfalse;

    switch ( credential->kind ) {
        case QL_AUTH_CREDENTIAL_STEAM:
            handled = QL_ClientAuth_DispatchSteam( &transport, credential, response );
            break;
        case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
            handled = QL_ClientAuth_HandleStandaloneToken( credential, response );
            break;
        default:
            QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
                "No transport for credential kind %s", QL_GetCredentialLabel( credential ) );
            handled = qfalse;
            break;
    }

    QL_ClientAuth_LogResponse( &transport, response );
    return handled;
}
