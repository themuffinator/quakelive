#include "client.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "../../common/ql_auth_service.h"

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
    Q_vsnprintf( response->message, sizeof( response->message ), format, args );
    va_end( args );
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

static qboolean QL_ClientAuth_SteamRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response,
    const ql_client_auth_transport_t *transport ) {
    if ( !credential || credential->kind != QL_AUTH_CREDENTIAL_STEAM ) {
        return qfalse;
    }

    char preview[32];
    QL_ClientAuth_TokenPreview( credential, preview, sizeof( preview ) );

    Com_Printf( "[auth] steam payload summary: ticket=%s (len=%zu)\n", preview, credential->length );

    if ( credential->length < 16 ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_DENIED,
            "Steam ticket rejected: payload too short" );
        QL_ClientAuth_LogResponse( transport, response );
        return qfalse;
    }

    if ( strstr( credential->value, "retry" ) ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_PENDING,
            "Steam service busy, retry with refreshed ticket" );
        QL_ClientAuth_LogResponse( transport, response );
        return qfalse;
    }

    if ( strstr( credential->value, "denied" ) || strstr( credential->value, "invalid" ) ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_DENIED,
            "Steam backend denied the ticket" );
        QL_ClientAuth_LogResponse( transport, response );
        return qfalse;
    }

    QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "Steam session established (ticket=%s)", preview );
    QL_ClientAuth_LogResponse( transport, response );
    return qtrue;
}

static qboolean QL_ClientAuth_StandaloneRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response,
    const ql_client_auth_transport_t *transport ) {
    if ( !credential || credential->kind != QL_AUTH_CREDENTIAL_STANDALONE_TOKEN ) {
        return qfalse;
    }

    char preview[32];
    QL_ClientAuth_TokenPreview( credential, preview, sizeof( preview ) );

    Com_Printf( "[auth] standalone payload summary: token=%s (len=%zu)\n", preview, credential->length );

    if ( credential->length < 12 ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_DENIED,
            "Standalone token rejected: payload too short" );
        QL_ClientAuth_LogResponse( transport, response );
        return qfalse;
    }

    if ( strstr( credential->value, "refresh" ) ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_PENDING,
            "Launcher token expired, request a refresh" );
        QL_ClientAuth_LogResponse( transport, response );
        return qfalse;
    }

    if ( strstr( credential->value, "revoke" ) || strstr( credential->value, "denied" ) ) {
        QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_DENIED,
            "Launcher revoked the token" );
        QL_ClientAuth_LogResponse( transport, response );
        return qfalse;
    }

    QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ACCEPTED,
        "Standalone token accepted (token=%s)", preview );
    QL_ClientAuth_LogResponse( transport, response );
    return qtrue;
}

qboolean QL_Auth_ExecuteRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !credential || !response ) {
        return qfalse;
    }

    const ql_client_auth_transport_t steamTransport = {
        { "steam", "/steam/session/validate" },
        "steam"
    };

    const ql_client_auth_transport_t standaloneTransport = {
        { "standalone", "/launcher/auth/verify" },
        "standalone"
    };

    const ql_client_auth_transport_t unknownTransport = {
        { "unknown", "<unroutable>" },
        "dispatcher"
    };

    switch ( credential->kind ) {
        case QL_AUTH_CREDENTIAL_STEAM:
            QL_ClientAuth_LogStage( &steamTransport, "dispatch", "submitting credential" );
            return QL_ClientAuth_SteamRequest( credential, response, &steamTransport );
        case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
            QL_ClientAuth_LogStage( &standaloneTransport, "dispatch", "submitting credential" );
            return QL_ClientAuth_StandaloneRequest( credential, response, &standaloneTransport );
        default:
            QL_ClientAuth_LogStage( &unknownTransport, "dispatch", "credential kind not routed" );
            QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
                "No transport for credential kind %s", QL_GetCredentialLabel( credential ) );
            QL_ClientAuth_LogResponse( &unknownTransport, response );
            return qfalse;
    }
}
