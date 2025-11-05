#ifndef AUTH_CREDENTIALS_H
#define AUTH_CREDENTIALS_H

#include "../code/game/q_shared.h"
#include <stddef.h>

typedef enum {
    QL_AUTH_CREDENTIAL_EMPTY = 0,
    QL_AUTH_CREDENTIAL_LEGACY_CDKEY,
    QL_AUTH_CREDENTIAL_STEAM,
    QL_AUTH_CREDENTIAL_STANDALONE_TOKEN
} qlAuthCredentialKind;

#define QL_AUTH_MAX_CREDENTIAL_LENGTH 128
#define QL_AUTH_MAX_RESPONSE_MESSAGE 128
#define QL_AUTH_MAX_CREDENTIAL_STORAGE (QL_AUTH_MAX_CREDENTIAL_LENGTH + 32)

typedef struct {
    qlAuthCredentialKind kind;
    char value[QL_AUTH_MAX_CREDENTIAL_LENGTH];
    size_t length;
} ql_auth_credential_t;

typedef enum {
    QL_AUTH_RESULT_PENDING = 0,
    QL_AUTH_RESULT_ACCEPTED,
    QL_AUTH_RESULT_DENIED,
    QL_AUTH_RESULT_ERROR
} qlAuthResult;

typedef enum {
    QL_AUTH_OUTCOME_SUCCESS = 0,
    QL_AUTH_OUTCOME_RETRY,
    QL_AUTH_OUTCOME_FAILURE
} qlAuthOutcome;

typedef struct {
    qlAuthResult result;
    qlAuthOutcome outcome;
    char message[QL_AUTH_MAX_RESPONSE_MESSAGE];
} ql_auth_response_t;

void QL_InitAuthCredential( ql_auth_credential_t *credential );

qboolean QL_ParseLegacyCDKey( const char *cdkey, ql_auth_credential_t *out );

qboolean QL_ParseCredentialString( const char *value, ql_auth_credential_t *out );

qboolean QL_ParsePlatformToken( const char *token, qlAuthCredentialKind kind, ql_auth_credential_t *out );

const char *QL_GetCredentialLabel( const ql_auth_credential_t *credential );

qboolean QL_RequestExternalAuth( const ql_auth_credential_t *credential, ql_auth_response_t *response );

char *QL_FormatCredentialForAuthorize( const ql_auth_credential_t *credential, char *buffer, size_t bufferSize );

#endif // AUTH_CREDENTIALS_H
