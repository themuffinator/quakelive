#ifndef PLATFORM_BACKEND_SHARED_H
#define PLATFORM_BACKEND_SHARED_H

#include "../auth_credentials.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

static inline void QL_Backend_FormatCredentialPreview( const ql_auth_credential_t *credential, char *buffer, size_t bufferSize ) {
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

static inline qlAuthOutcome QL_Backend_MapOutcomeFromResult( qlAuthResult result ) {
    switch ( result ) {
        case QL_AUTH_RESULT_ACCEPTED:
            return QL_AUTH_OUTCOME_SUCCESS;
        case QL_AUTH_RESULT_PENDING:
            return QL_AUTH_OUTCOME_RETRY;
        default:
            return QL_AUTH_OUTCOME_FAILURE;
    }
}

static inline void QL_Backend_SetAuthResponse( ql_auth_response_t *response, qlAuthResult result, const char *format, ... ) {
    if ( !response ) {
        return;
    }

    response->result = result;
    response->outcome = QL_Backend_MapOutcomeFromResult( result );

    if ( !format ) {
        response->message[0] = '\0';
        return;
    }

    va_list args;
    va_start( args, format );
    vsnprintf( response->message, sizeof( response->message ), format, args );
    va_end( args );
}

#endif // PLATFORM_BACKEND_SHARED_H
