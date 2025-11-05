#ifndef QL_AUTH_SERVICE_H
#define QL_AUTH_SERVICE_H

#include "auth_credentials.h"

typedef struct {
    const char *provider;
    const char *endpoint;
} ql_auth_request_descriptor_t;

typedef struct {
    ql_auth_request_descriptor_t request;
    ql_auth_response_t *response;
} ql_auth_exchange_context_t;

qboolean QL_Auth_ExecuteRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response );

const char *QL_DescribeAuthOutcome( const ql_auth_response_t *response );

#endif // QL_AUTH_SERVICE_H
