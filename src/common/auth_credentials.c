#include "auth_credentials.h"

#include <ctype.h>
#include <string.h>

#include "../code/qcommon/qcommon.h"
#include "ql_auth_service.h"

static void QL_CopyString( char *dst, size_t dstSize, const char *src ) {
    size_t i;

    if ( !dst || dstSize == 0 ) {
        return;
    }

    if ( !src ) {
        dst[0] = '\0';
        return;
    }

    for ( i = 0; i + 1 < dstSize && src[i]; ++i ) {
        dst[i] = src[i];
    }

    dst[i] = '\0';
}

void QL_InitAuthCredential( ql_auth_credential_t *credential ) {
    if ( !credential ) {
        return;
    }

    credential->kind = QL_AUTH_CREDENTIAL_EMPTY;
    credential->value[0] = '\0';
    credential->length = 0;
}

static qboolean QL_ParseLegacyKeyInternal( const char *value, ql_auth_credential_t *out ) {
    size_t i;

    if ( !value || !out ) {
        return qfalse;
    }

    QL_InitAuthCredential( out );
    out->kind = QL_AUTH_CREDENTIAL_LEGACY_CDKEY;

    for ( i = 0; value[i] && out->length + 1 < QL_AUTH_MAX_CREDENTIAL_LENGTH; ++i ) {
        const unsigned char ch = (unsigned char)value[i];

        if ( isalnum( ch ) ) {
            out->value[out->length++] = (char)ch;
        }
    }

    out->value[out->length] = '\0';

    return out->length > 0 ? qtrue : qfalse;
}

qboolean QL_ParseLegacyCDKey( const char *cdkey, ql_auth_credential_t *out ) {
    if ( !cdkey || !out ) {
        return qfalse;
    }

    return QL_ParseLegacyKeyInternal( cdkey, out );
}

qboolean QL_ParseCredentialString( const char *value, ql_auth_credential_t *out ) {
    if ( !value || !out ) {
        return qfalse;
    }

    if ( !Q_stricmpn( value, "steam:", 6 ) ) {
        return QL_ParsePlatformToken( value + 6, QL_AUTH_CREDENTIAL_STEAM, out );
    }

    if ( !Q_stricmpn( value, "standalone:", 11 ) ) {
        return QL_ParsePlatformToken( value + 11, QL_AUTH_CREDENTIAL_STANDALONE_TOKEN, out );
    }

    return QL_ParseLegacyCDKey( value, out );
}

qboolean QL_ParsePlatformToken( const char *token, qlAuthCredentialKind kind, ql_auth_credential_t *out ) {
    if ( !token || !out ) {
        return qfalse;
    }

    QL_InitAuthCredential( out );

    if ( kind == QL_AUTH_CREDENTIAL_EMPTY ) {
        return qfalse;
    }

    out->kind = kind;
    QL_CopyString( out->value, sizeof( out->value ), token );
    out->length = strlen( out->value );

    return out->length > 0 ? qtrue : qfalse;
}

const char *QL_GetCredentialLabel( const ql_auth_credential_t *credential ) {
    if ( !credential ) {
        return "unknown";
    }

    switch ( credential->kind ) {
        case QL_AUTH_CREDENTIAL_LEGACY_CDKEY:
            return "legacy_cdkey";
        case QL_AUTH_CREDENTIAL_STEAM:
            return "steam";
        case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
            return "standalone";
        default:
            return "unknown";
    }
}

qboolean QL_FormatCredentialForStorage( const ql_auth_credential_t *credential,
    char *kindBuffer, size_t kindBufferSize,
    char *valueBuffer, size_t valueBufferSize )
{
    const char *label;

    if ( !kindBuffer || kindBufferSize == 0 || !valueBuffer || valueBufferSize == 0 ) {
        return qfalse;
    }

    kindBuffer[0] = '\0';
    valueBuffer[0] = '\0';

    if ( !credential || credential->kind == QL_AUTH_CREDENTIAL_EMPTY || credential->length == 0 ) {
        return qfalse;
    }

    label = QL_GetCredentialLabel( credential );
    if ( !label || !label[0] || !Q_stricmp( label, "unknown" ) ) {
        return qfalse;
    }

    QL_CopyString( kindBuffer, kindBufferSize, label );
    QL_CopyString( valueBuffer, valueBufferSize, credential->value );

    if ( kindBuffer[0] == '\0' || valueBuffer[0] == '\0' ) {
        return qfalse;
    }

    return qtrue;
}

qboolean QL_RequestExternalAuth( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !response ) {
        return qfalse;
    }

    QL_CopyString( response->message, sizeof( response->message ), "" );
    response->result = QL_AUTH_RESULT_ERROR;
    response->outcome = QL_AUTH_OUTCOME_FAILURE;

    if ( !credential ) {
        QL_CopyString( response->message, sizeof( response->message ),
            "No credential provided for external auth." );
        return qfalse;
    }

    if ( credential->kind == QL_AUTH_CREDENTIAL_LEGACY_CDKEY ) {
        QL_CopyString( response->message, sizeof( response->message ),
            "Legacy CD keys are validated locally; no external auth required." );
        response->result = QL_AUTH_RESULT_ACCEPTED;
        response->outcome = QL_AUTH_OUTCOME_SUCCESS;
        return qtrue;
    }

    if ( !QL_Auth_ExecuteRequest( credential, response ) ) {
        if ( response->message[0] == '\0' ) {
            Com_sprintf( response->message, sizeof( response->message ),
                "No external auth backend for %s credentials.", QL_GetCredentialLabel( credential ) );
        }

        response->result = QL_AUTH_RESULT_ERROR;
        response->outcome = QL_AUTH_OUTCOME_FAILURE;
        return qfalse;
    }

    return response->result == QL_AUTH_RESULT_ACCEPTED ? qtrue : qfalse;
}

char *QL_FormatCredentialForAuthorize( const ql_auth_credential_t *credential, char *buffer, size_t bufferSize ) {
    if ( !buffer || bufferSize == 0 ) {
        return NULL;
    }

    buffer[0] = '\0';

    if ( !credential || credential->length == 0 ) {
        return buffer;
    }

    switch ( credential->kind ) {
        case QL_AUTH_CREDENTIAL_LEGACY_CDKEY:
            QL_CopyString( buffer, bufferSize, credential->value );
            break;
        case QL_AUTH_CREDENTIAL_STEAM:
            Com_sprintf( buffer, bufferSize, "steam:%s", credential->value );
            break;
        case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
            Com_sprintf( buffer, bufferSize, "standalone:%s", credential->value );
            break;
        default:
            QL_CopyString( buffer, bufferSize, credential->value );
            break;
    }

    return buffer;
}
