#include "client.h"

#include <string.h>

#include "../../common/ql_auth_service.h"
#include "../../common/platform/platform_services.h"

typedef struct {
    ql_auth_request_descriptor_t descriptor;
    const char *logPrefix;
} ql_client_auth_transport_t;

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

qboolean QL_Auth_ExecuteRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !credential || !response ) {
        return qfalse;
    }

    const ql_platform_service_table *services = QL_GetPlatformServices();
    const char *provider = services && services->auth.descriptor.provider ? services->auth.descriptor.provider : "dispatcher";
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

    if ( !services || !services->auth.descriptor.supported || !services->auth.request ) {
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

    if ( !services || !services->auth.request ) {
        response->result = QL_AUTH_RESULT_ERROR;
        response->outcome = QL_AUTH_OUTCOME_FAILURE;
        Q_strncpyz( response->message, sizeof( response->message ),
            "No authentication backend is compiled in." );
        QL_ClientAuth_LogResponse( &transport, response );
        return qfalse;
    }

    if ( !QL_Platform_RunMockAuthFlow( credential, response ) ) {
        if ( response->message[0] == '\0' ) {
            Com_sprintf( response->message, sizeof( response->message ),
                "No transport for credential kind %s", QL_GetCredentialLabel( credential ) );
            response->result = QL_AUTH_RESULT_ERROR;
            response->outcome = QL_AUTH_OUTCOME_FAILURE;
        }

        QL_ClientAuth_LogResponse( &transport, response );
        return qfalse;
    }

    QL_ClientAuth_LogResponse( &transport, response );
    return qtrue;
}
