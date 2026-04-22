#include "client.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../../common/ql_auth_service.h"
#include "../../common/platform/platform_backend_auth.h"
#include "../../common/platform/platform_services.h"
#include "../../common/platform/platform_steamworks.h"

typedef struct {
	ql_auth_request_descriptor_t descriptor;
	const char *logPrefix;
	const char *policyLabel;
} ql_client_auth_transport_t;

static uint32_t cl_clientAuthSteamTicketHandle = 0;

/*
=============
QL_ClientAuth_MapOutcome

Maps a backend result code into the public-facing outcome enum.
=============
*/
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

/*
=============
QL_DescribeAuthOutcome

Converts an auth response outcome into a loggable string.
=============
*/
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

/*
=============
QL_ClientAuth_SetResponse

Populates a response container with a result, outcome, and formatted message.
=============
*/
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

/*
=============
QL_ClientAuth_LogStage

Emits a lifecycle log entry for an auth stage.
=============
*/
static void QL_ClientAuth_LogStage( const ql_client_auth_transport_t *transport, const char *stage, const char *detail ) {
	if ( !transport || !stage || !detail ) {
		return;
	}

	Com_Printf( "[auth] %s [%s] %s (%s): %s\n",
	transport->logPrefix,
	transport->policyLabel ? transport->policyLabel : "compatibility-unavailable",
	stage,
	transport->descriptor.endpoint ? transport->descriptor.endpoint : "<none>",
	detail );
}

/*
=============
QL_ClientAuth_LogResponse

Logs a completed response for diagnostics.
=============
*/
static void QL_ClientAuth_LogResponse( const ql_client_auth_transport_t *transport, const ql_auth_response_t *response ) {
	if ( !transport || !response ) {
		return;
	}

	Com_Printf( "[auth] %s [%s] result -> outcome=%s, message=\"%s\"\n",
	transport->logPrefix,
	transport->policyLabel ? transport->policyLabel : "compatibility-unavailable",
	QL_DescribeAuthOutcome( response ),
	response->message );
}

/*
=============
QL_ClientAuth_TokenPreview

Creates a short preview of a credential value for logging.
=============
*/
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

/*
=============
QL_ClientAuth_GetEndpoint

Returns the retained request endpoint label for one credential kind.
=============
*/
static const char *QL_ClientAuth_GetEndpoint( qlAuthCredentialKind kind ) {
	switch ( kind ) {
		case QL_AUTH_CREDENTIAL_STEAM:
		return "/steam/session/validate";
		case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
		return "/launcher/auth/verify";
		default:
		return "<unroutable>";
	}
}

/*
=============
QL_ClientAuth_ReportPolicyBlock

Publishes a policy-blocked auth result using the structural online-services
mode and policy labels.
=============
*/
static qboolean QL_ClientAuth_ReportPolicyBlock( const ql_client_auth_transport_t *transport, ql_auth_response_t *response, const char *requestLabel ) {
	char detail[256];
	const char *responseLabel = requestLabel ? requestLabel : "Authentication";
	const char *modeLabel = QL_GetOnlineServicesModeLabel();
	const char *policyLabel = QL_GetOnlineServicesPolicyLabel();

	if ( requestLabel ) {
		if ( !Q_stricmp( requestLabel, "Steam authentication" ) ) {
			responseLabel = "Steam";
		} else if ( !Q_stricmp( requestLabel, "Standalone launcher authentication" ) ) {
			responseLabel = "Standalone";
		}
	}

	Com_sprintf( detail, sizeof( detail ), "%s blocked by %s [%s] before dispatch",
		requestLabel ? requestLabel : "Authentication",
		modeLabel ? modeLabel : "Unavailable",
		policyLabel ? policyLabel : "compatibility-unavailable" );
	QL_ClientAuth_LogStage( transport, "policy-blocked", detail );

	QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
		"%s blocked: %s [%s]",
		responseLabel,
		modeLabel ? modeLabel : "Unavailable",
		policyLabel ? policyLabel : "compatibility-unavailable" );
	QL_ClientAuth_LogResponse( transport, response );
	return qfalse;
}

/*
=============
QL_ClientAuth_InvokeBackend

Invokes a backend authenticator if present, emitting an error otherwise.
=============
*/
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

/*
=============
QL_ClientAuth_SetSteamTicketHandle

Retains the most recent Steam auth-ticket handle so disconnect cleanup can
mirror the retail lifetime owner.
=============
*/
static void QL_ClientAuth_SetSteamTicketHandle( uint32_t ticketHandle ) {
	if ( cl_clientAuthSteamTicketHandle && cl_clientAuthSteamTicketHandle != ticketHandle ) {
		QL_Steamworks_CancelAuthTicket( cl_clientAuthSteamTicketHandle );
	}

	cl_clientAuthSteamTicketHandle = ticketHandle;
}

/*
=============
QL_ClientAuth_RequestSteamTicket

Fetches a Steam auth ticket via the Steamworks wrapper for dispatch.
=============
*/
static qboolean QL_ClientAuth_RequestSteamTicket( ql_auth_credential_t *credential, char *logBuffer, size_t logBufferSize ) {
	int ticketLength = 0;
	uint32_t ticketHandle = 0;

	if ( logBuffer && logBufferSize > 0 ) {
		logBuffer[0] = '\0';
	}

	if ( !credential || credential->kind != QL_AUTH_CREDENTIAL_STEAM ) {
		return qfalse;
	}

	if ( !CL_SteamServicesEnabled() ) {
		return qfalse;
	}

	QL_Steamworks_RunCallbacks();

	if ( !QL_Steamworks_RequestAuthTicket( credential->value, sizeof( credential->value ), &ticketLength, &ticketHandle ) ) {
		return qfalse;
	}

	QL_Steamworks_RunCallbacks();

	credential->length = (size_t)ticketLength;
	QL_ClientAuth_SetSteamTicketHandle( ticketHandle );

	if ( logBuffer && logBufferSize > 0 ) {
		Q_strncpyz( logBuffer, credential->value, logBufferSize );
	}

	return qtrue;
}

/*
=============
QL_ClientAuth_CancelSteamTicket

Cancels the retained Steam auth ticket during disconnect/error cleanup.
=============
*/
void QL_ClientAuth_CancelSteamTicket( void ) {
	if ( !cl_clientAuthSteamTicketHandle ) {
		return;
	}

	QL_Steamworks_CancelAuthTicket( cl_clientAuthSteamTicketHandle );
	cl_clientAuthSteamTicketHandle = 0;
}

/*
=============
QL_ClientAuth_HandleSteamworksTicket

Validates a Steam ticket using the native Steamworks APIs.
=============
*/
static qboolean QL_ClientAuth_HandleSteamworksTicket( const ql_client_auth_transport_t *transport, const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
	(void)transport;

	if ( !CL_SteamServicesEnabled() ) {
		return qfalse;
	}

	QL_Steamworks_RunCallbacks();

	if ( !QL_Steamworks_ValidateTicket( credential ? credential->value : NULL, response ) ) {
		return QL_ClientAuth_InvokeBackend( QL_PlatformBackendSteamworks_Authenticate,
		credential, response, "Steamworks" );
	}

	QL_Steamworks_RunCallbacks();

	return qtrue;
}

/*
=============
QL_ClientAuth_HandleOpenSteamTicket

Validates a Steam ticket using the open adapter backend.
=============
*/
static qboolean QL_ClientAuth_HandleOpenSteamTicket( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
	return QL_ClientAuth_InvokeBackend( QL_PlatformBackendOpenSteam_Authenticate,
	credential, response, "Open Steam Adapter" );
}

/*
=============
QL_ClientAuth_HandleStandaloneToken

Routes standalone launcher tokens to the Open Steam adapter backend.
=============
*/
static qboolean QL_ClientAuth_HandleStandaloneToken( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
	if ( !credential || credential->kind != QL_AUTH_CREDENTIAL_STANDALONE_TOKEN ) {
		return qfalse;
	}

	if ( !CL_OnlineServicesEnabled() ) {
		return qfalse;
	}

	return QL_ClientAuth_InvokeBackend( QL_PlatformBackendOpenSteam_Authenticate,
	credential, response, "Open Steam Adapter" );
}

/*
=============
QL_ClientAuth_HandleHybridSteam

Attempts Steamworks validation first, falling back to the open adapter on retry-eligible outcomes.
=============
*/
static qboolean QL_ClientAuth_HandleHybridSteam( const ql_client_auth_transport_t *transport, const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
	ql_auth_response_t steamResponse;
	ql_client_auth_transport_t fallbackTransport;
	qboolean handled;
	qboolean fallbackEligible;
	qboolean fallbackHandled;
	char preview[32];
	memset( &steamResponse, 0, sizeof( steamResponse ) );

	handled = QL_ClientAuth_HandleSteamworksTicket( transport, credential, &steamResponse );

	if ( handled && steamResponse.result == QL_AUTH_RESULT_ACCEPTED ) {
		*response = steamResponse;
		return qtrue;
	}

	fallbackEligible = !handled || steamResponse.result == QL_AUTH_RESULT_PENDING;
	if ( fallbackEligible ) {
		QL_ClientAuth_LogStage( transport,
			"hybrid-fallback",
			handled
				? "Steamworks heuristic compatibility backend returned retry; dispatching open adapter fallback"
				: "Steamworks compatibility path unavailable; dispatching open adapter fallback" );

		fallbackTransport.descriptor.provider = "Open Steam Adapter";
		fallbackTransport.descriptor.endpoint = "/launcher/auth/verify";
		fallbackTransport.logPrefix = "Open Steam Adapter";
		fallbackTransport.policyLabel = transport && transport->policyLabel ? transport->policyLabel : "compatibility-unavailable";
		QL_ClientAuth_LogStage( &fallbackTransport, "dispatch", "submitting fallback credential" );

		fallbackHandled = QL_ClientAuth_HandleOpenSteamTicket( credential, response );

		if ( fallbackHandled ) {
			if ( response->result == QL_AUTH_RESULT_ACCEPTED ) {
				QL_ClientAuth_TokenPreview( credential, preview, sizeof( preview ) );

				QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ACCEPTED,
				"Hybrid fallback accepted credential via heuristic open adapter (token=%s)", preview );
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

/*
=============
QL_ClientAuth_DispatchSteam

Selects the correct Steam validation path for the configured provider.
=============
*/
static qboolean QL_ClientAuth_DispatchSteam( const ql_client_auth_transport_t *transport, const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
	const char *provider;

	if ( !transport || !credential ) {
		return qfalse;
	}

	provider = transport->descriptor.provider ? transport->descriptor.provider : "";

	if ( !Q_stricmp( provider, "Hybrid" ) ) {
		return QL_ClientAuth_HandleHybridSteam( transport, credential, response );
	}

	if ( !Q_stricmp( provider, "Open Steam Adapter" ) ) {
		return QL_ClientAuth_HandleOpenSteamTicket( credential, response );
	}

	return QL_ClientAuth_HandleSteamworksTicket( transport, credential, response );
}

/*
=============
QL_Auth_ExecuteRequest

Dispatches a credential to the configured auth backend and reports the result.
=============
*/
qboolean QL_Auth_ExecuteRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
	const ql_auth_credential_t *activeCredential;
	const ql_platform_service_table *services;
	qboolean authCompiled;
	qboolean authInitialised;
	const char *provider;
	const char *policyLabel;
	const char *endpoint;
	ql_client_auth_transport_t transport;
	ql_auth_credential_t steamCredential;
	char steamHex[QL_AUTH_MAX_CREDENTIAL_STORAGE];
	char preview[32];
	qboolean handled;

	if ( !credential || !response ) {
		return qfalse;
	}

	activeCredential = credential;
	steamHex[0] = '\0';
	services = QL_GetPlatformServices();
	authCompiled = services && services->auth.compiled;
	authInitialised = services && services->auth.initialised;
	provider = services && services->auth.provider ? services->auth.provider : "dispatcher";
	policyLabel = services ? QL_DescribePlatformFeaturePolicy( &services->auth ) : "compatibility-unavailable";
	endpoint = QL_ClientAuth_GetEndpoint( credential->kind );

	transport.descriptor.provider = provider;
	transport.descriptor.endpoint = endpoint;
	transport.logPrefix = provider;
	transport.policyLabel = policyLabel;

	if ( credential->kind == QL_AUTH_CREDENTIAL_STEAM ) {
		if ( !CL_SteamServicesEnabled() ) {
			return QL_ClientAuth_ReportPolicyBlock( &transport, response, "Steam authentication" );
		}

		QL_InitAuthCredential( &steamCredential );
		steamCredential.kind = QL_AUTH_CREDENTIAL_STEAM;

		if ( !QL_ClientAuth_RequestSteamTicket( &steamCredential, steamHex, sizeof( steamHex ) ) ) {
			QL_ClientAuth_LogStage( &transport, "ticket-request-failed", "Steam auth ticket request failed before dispatch" );
			QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
			"Steam ticket failed: %s [%s]",
			QL_GetOnlineServicesModeLabel(),
			QL_GetOnlineServicesPolicyLabel() );
			QL_ClientAuth_LogResponse( &transport, response );
			return qfalse;
		}

		activeCredential = &steamCredential;
	}

	if ( credential->kind == QL_AUTH_CREDENTIAL_STANDALONE_TOKEN && !CL_OnlineServicesEnabled() ) {
		return QL_ClientAuth_ReportPolicyBlock( &transport, response, "Standalone launcher authentication" );
	}

	QL_ClientAuth_LogStage( &transport, "dispatch", "submitting credential" );

	QL_ClientAuth_TokenPreview( activeCredential, preview, sizeof( preview ) );

	switch ( activeCredential->kind ) {
		case QL_AUTH_CREDENTIAL_STEAM:
		Com_Printf( "[auth] %s [%s] payload summary: ticket=%s (len=%zu)\n",
		transport.logPrefix, transport.policyLabel, steamHex[0] ? steamHex : preview, activeCredential->length );
		break;
		case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
		Com_Printf( "[auth] %s [%s] payload summary: token=%s (len=%zu)\n",
		transport.logPrefix, transport.policyLabel, preview, activeCredential->length );
		break;
		default:
		Com_Printf( "[auth] %s [%s] payload summary: credential=%s (len=%zu)\n",
		transport.logPrefix, transport.policyLabel, preview, activeCredential->length );
		break;
	}

	if ( !authInitialised ) {
		QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
		authCompiled
			? "Auth init failed: %s [%s]"
			: "No auth backend: %s [%s]",
		QL_GetOnlineServicesModeLabel(),
		QL_GetOnlineServicesPolicyLabel() );
		QL_ClientAuth_LogResponse( &transport, response );
		return qfalse;
	}

	handled = qfalse;

	switch ( activeCredential->kind ) {
		case QL_AUTH_CREDENTIAL_STEAM:
		handled = QL_ClientAuth_DispatchSteam( &transport, activeCredential, response );
		break;
		case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
		handled = QL_ClientAuth_HandleStandaloneToken( activeCredential, response );
		break;
		default:
		QL_ClientAuth_SetResponse( response, QL_AUTH_RESULT_ERROR,
		"No transport for credential kind %s", QL_GetCredentialLabel( activeCredential ) );
		handled = qfalse;
		break;
	}

	QL_ClientAuth_LogResponse( &transport, response );
	return handled;
}
