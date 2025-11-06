# Online Authentication Lifecycle

This document describes how the client dispatches external authentication requests and how to observe the resulting lifecycle logs.

## Request Routing

`QL_RequestExternalAuth` clears the response container and invokes `QL_Auth_ExecuteRequest`, which consults the platform service table to discover the active authentication backend.【F:src/common/auth_credentials.c†L120-L154】【F:src/code/client/ql_auth.c†L200-L273】 The descriptor published by `QL_GetPlatformServices` provides the human-readable provider name (for example, “Steamworks”, “Open Steam Adapter”, or “Hybrid”), and the dispatcher derives the request endpoint from the credential kind:

- **Steam** – `/steam/session/validate`
- **Standalone launcher** – `/launcher/auth/verify`

The build definitions `QL_BUILD_STEAMWORKS` and `QL_BUILD_OPEN_STEAM` funnel through `platform_config.h`, which exposes the normalised capability flags consumed by `QL_GetPlatformServices`. The table below maps the supported flag permutations to the advertised provider label and dispatch endpoints surfaced by the runtime. Regression probes compile the dispatcher with each flag combination to confirm the descriptors match the configuration.【F:src/common/platform/platform_config.h†L1-L34】【F:src/common/platform/platform_services.c†L16-L75】【F:tests/test_platform_services.py†L11-L132】

| Build macro preset | Provider label reported by `QL_GetPlatformServices` | Dispatch endpoints |
| --- | --- | --- |
| `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=0` | `Steamworks` | `/steam/session/validate` |
| `QL_BUILD_STEAMWORKS=0`, `QL_BUILD_OPEN_STEAM=1` | `Open Steam Adapter` | `/launcher/auth/verify` |
| `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1` | `Hybrid` (Steam primary, open fallback) | Steam: `/steam/session/validate`<br>Fallback: `/launcher/auth/verify` |

Each dispatch prints a log entry with the provider label, summarizes the credential using a masked preview, and writes the final outcome to the shared response object.【F:src/code/client/ql_auth.c†L44-L273】 The service table ensures that builds compiled without a given backend still advertise accurate capabilities.【F:src/common/platform/platform_services.c†L16-L75】

## Structured Outcomes

Handlers normalise their decisions into three high-level outcomes so callers can distinguish fatal errors from transient hiccups. The heuristics live inside the platform backends so each build flavour (Steamworks, open adapter, or hybrid) shares consistent responses.【F:src/common/platform/backends/platform_backend_steamworks.c†L1-L29】【F:src/common/platform/backends/platform_backend_open_steam.c†L1-L47】 Hybrid builds automatically replay Steam credentials through the open adapter whenever the Steamworks backend reports `QL_AUTH_RESULT_PENDING`, preserving the fallback response when it accepts the credential so downtime still produces a `success` outcome.【F:src/code/client/ql_auth.c†L139-L212】【F:tests/test_platform_services.py†L134-L177】

- `success` – the credential was accepted and the legacy code path may continue.
- `retry` – the backend asked for another attempt (for example, a Steam ticket marked with `retry` or a standalone token containing `refresh`).【F:src/common/platform/backends/platform_backend_steamworks.c†L12-L23】【F:src/common/platform/backends/platform_backend_open_steam.c†L25-L33】
- `failure` – the credential was denied or malformed.

The helper `QL_DescribeAuthOutcome` maps enum values to these human-readable strings, which appear in every lifecycle log.【F:src/code/client/ql_auth.c†L26-L83】

## Integration Trace

Run the simulation script to capture an end-to-end trace for both providers:

```bash
python3 tools/integration/auth_flow_trace.py
```

The script drives representative credentials through the same heuristics used in the C implementation and prints the dispatch/result logs.【F:tools/integration/auth_flow_trace.py†L1-L113】 Example output:

```text
== Auth Flow Lifecycle ==
Provider/token combinations demonstrate success, retry, and failure paths.

-- Scenario 1: Steamworks --
[auth] Steamworks dispatch (/steam/session/validate): submitting credential
[auth] Steamworks payload summary: ticket=TICKET-…cdef (len=23)
[auth] Steamworks result -> outcome=success, message="Steam session established (ticket=TICKET-…cdef)"
```

Use the remaining scenarios from the script to validate retry and failure paths for Steamworks, hybrid fallback, and the standalone launcher. Each log line corresponds to the callbacks issued by the client dispatcher when `QL_RequestExternalAuth` runs during a real handshake.【F:src/code/client/ql_auth.c†L26-L273】【F:tools/integration/auth_flow_trace.py†L1-L113】
