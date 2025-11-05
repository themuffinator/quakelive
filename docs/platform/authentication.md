# Online Authentication Lifecycle

This document describes how the client dispatches external authentication requests and how to observe the resulting lifecycle logs.

## Request Routing

`QL_RequestExternalAuth` clears the response container and invokes `QL_Auth_ExecuteRequest`, which chooses the appropriate handler based on the credential kind.【F:src/common/auth_credentials.c†L119-L151】 The dispatcher lives in `src/code/client/ql_auth.c` and registers two transports:

- **Steam** – `/steam/session/validate`
- **Standalone launcher** – `/launcher/auth/verify`

Each transport prints a dispatch log, summarizes the credential using a masked preview, and writes the final outcome to the shared response object.【F:src/code/client/ql_auth.c†L33-L147】

## Structured Outcomes

Handlers normalise their decisions into three high-level outcomes so callers can distinguish fatal errors from transient hiccups:

- `success` – the credential was accepted and the legacy code path may continue.
- `retry` – the backend asked for another attempt (for example, a Steam ticket marked with `retry` or a standalone token containing `refresh`).【F:src/code/client/ql_auth.c†L63-L107】【F:src/code/client/ql_auth.c†L109-L147】
- `failure` – the credential was denied or malformed.

The helper `QL_DescribeAuthOutcome` maps enum values to these human-readable strings, which appear in every lifecycle log.【F:src/code/client/ql_auth.c†L45-L74】

## Integration Trace

Run the simulation script to capture an end-to-end trace for both providers:

```bash
python3 tools/integration/auth_flow_trace.py
```

The script drives representative credentials through the same heuristics used in the C implementation and prints the dispatch/result logs.【F:tools/integration/auth_flow_trace.py†L1-L77】 Example output:

```text
== Auth Flow Lifecycle ==
Provider/token combinations demonstrate success, retry, and failure paths.

-- Scenario 1: steam --
[auth] steam dispatch (/steam/session/validate): submitting credential
[auth] steam payload summary: ticket=TICKET-…cdef (len=23)
[auth] steam result -> outcome=success, message="Steam session established (ticket=TICKET-…cdef)"
```

Use the remaining scenarios from the script to validate retry and failure paths for Steam and the standalone launcher. Each log line corresponds to the callbacks issued by the client dispatcher when `QL_RequestExternalAuth` runs during a real handshake.【F:src/code/client/ql_auth.c†L56-L147】
