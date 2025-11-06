# Online Authentication Lifecycle

This document describes how the client dispatches external authentication requests and how to observe the resulting lifecycle logs.

## Request Routing

`QL_RequestExternalAuth` clears the response container and invokes `QL_Auth_ExecuteRequest`, which consults the platform service table to discover the active authentication backend.【F:src/common/auth_credentials.c†L120-L154】【F:src/code/client/ql_auth.c†L200-L273】 The descriptor published by `QL_GetPlatformServices` provides the human-readable provider name (for example, “Steamworks”, “Open Steam Adapter”, or “Hybrid”) and the dispatcher derives the request endpoint from the credential kind:

- **Steam** – `/steam/session/validate`
- **Standalone launcher** – `/launcher/auth/verify`

Each dispatch prints a log entry with the provider label, summarizes the credential using a masked preview, and then emits backend lifecycle logs that capture the invocation and result stages before writing the final outcome to the shared response object.【F:src/code/client/ql_auth.c†L44-L352】 The service table ensures that builds compiled without a given backend still advertise accurate capabilities.【F:src/common/platform/platform_services.c†L16-L75】

## Structured Outcomes

Handlers normalise their decisions into three high-level outcomes so callers can distinguish fatal errors from transient hiccups. The heuristics live inside the platform backends so each build flavour (Steamworks, open adapter, or hybrid) shares consistent responses, and the dispatcher logs the mapped outcome for every backend invocation.【F:src/common/platform/backends/platform_backend_steamworks.c†L1-L33】【F:src/common/platform/backends/platform_backend_open_steam.c†L1-L47】【F:src/code/client/ql_auth.c†L91-L229】

- `success` – the credential was accepted and the legacy code path may continue.
- `retry` – the backend asked for another attempt (for example, a Steam ticket marked with `retry` or a standalone token containing `refresh`).【F:src/common/platform/backends/platform_backend_steamworks.c†L12-L23】【F:src/common/platform/backends/platform_backend_open_steam.c†L25-L33】
- `failure` – the credential was denied or malformed.

The helper `QL_DescribeAuthOutcome` maps enum values to these human-readable strings, which appear in every lifecycle log.【F:src/code/client/ql_auth.c†L26-L83】

## Integration Trace

Run the simulation script to capture an end-to-end trace for both providers:

```bash
python3 tools/integration/auth_flow_trace.py
```

The script drives representative credentials through the same heuristics used in the C implementation and prints the dispatch/result logs.【F:tools/integration/auth_flow_trace.py†L1-L195】 Example output:

```text
== Auth Flow Lifecycle ==
Provider/token combinations demonstrate success, retry, and failure paths.

-- Scenario 1: Steamworks --
[auth] Steamworks dispatch (/steam/session/validate): submitting credential
[auth] Steamworks payload summary: ticket=TICKET-…cdef (len=23)
[auth] Steamworks steamworks.invoke (/steam/session/validate): invoking Steamworks backend
[auth] Steamworks steamworks.result (/steam/session/validate): handled=true, backend=Steamworks, outcome=success, message="Steam session established (ticket=TICKET-…cdef)"
[auth] Steamworks result -> outcome=success, message="Steam session established (ticket=TICKET-…cdef)"
```

Use the remaining scenarios from the script to validate retry and failure paths for Steamworks, hybrid fallback, and the standalone launcher. Each log line corresponds to the callbacks issued by the client dispatcher when `QL_RequestExternalAuth` runs during a real handshake.【F:src/code/client/ql_auth.c†L44-L352】【F:tools/integration/auth_flow_trace.py†L1-L195】
