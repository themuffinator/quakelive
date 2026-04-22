# Online Authentication Lifecycle

This document describes how the client dispatches external authentication requests and how to observe the resulting lifecycle logs.

## Strict-Retail Classification

This authentication surface is a compatibility-only provider lane for the
remaining engine host/support audit, not a claim that retail Quake Live online
services have been reconstructed in source. In the strict retail Windows engine-host/support score,
only the policy boundary and caller ownership are counted here: the
open-adapter and hybrid labels exist so the repo can expose bounded fallback
behavior without misreporting those backends as retail code.

`QL_BUILD_ONLINE_SERVICES` defaults to `0`, which keeps Quake Live-only online
service traffic disabled unless a contributor deliberately opts into a non-default
compatibility build. Even in opted-in builds, the open/hybrid backends remain a
documented divergence until a documented open replacement path exists for the
retail-only service dependency.

## Request Routing

`QL_RequestExternalAuth` clears the response container and invokes `QL_Auth_ExecuteRequest`, which consults the platform service table to discover the active authentication backend.【F:src/common/auth_credentials.c†L120-L154】【F:src/code/client/ql_auth.c†L200-L273】 The descriptor published by `QL_GetPlatformServices` provides the human-readable provider name (for example, “Steamworks”, “Open Steam Adapter”, or “Hybrid”), while `QL_DescribePlatformFeaturePolicy(...)` publishes the short compatibility policy label paired with that provider (for example, `compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)`, `compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)`, `compatibility-only provider unavailable`, or `compatibility-only`). The dispatcher carries both labels into the auth logs and still derives the request endpoint from the credential kind:

- **Steam** – `/steam/session/validate`
- **Standalone launcher** – `/launcher/auth/verify`

The build definitions `QL_BUILD_ONLINE_SERVICES`, `QL_BUILD_STEAMWORKS`, and `QL_BUILD_OPEN_STEAM` funnel through `platform_config.h`, which exposes the normalised capability flags consumed by `QL_GetPlatformServices`. The table below maps the supported flag permutations to the advertised provider label and dispatch endpoints surfaced by the runtime. Regression probes compile the dispatcher with each flag combination to confirm the descriptors match the configuration, including the default build-disabled policy path.【F:src/common/platform/platform_config.h†L1-L40】【F:src/common/platform/platform_services.c†L16-L89】【F:tests/test_platform_services.py†L11-L154】

When a build does enable those compatibility lanes, `QL_GetPlatformServices`
can still hard-disable them at runtime through
`QL_DISABLE_EXTERNAL_ECOSYSTEMS` or `QL_DISABLE_STEAMWORKS`, publishing
`Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS` instead of silently pretending the
non-retail providers are part of the strict-retail path.

| Build macro preset | Provider label reported by `QL_GetPlatformServices` | Dispatch endpoints |
| --- | --- | --- |
| `QL_BUILD_ONLINE_SERVICES=0` | `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)` | none; policy stubs reject live-service auth attempts |
| `QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=0` | `Steamworks` | `/steam/session/validate` |
| `QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=0`, `QL_BUILD_OPEN_STEAM=1` | `Open Steam Adapter` | `/launcher/auth/verify` |
| `QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1` | `Hybrid` (Steam primary, open fallback) | Steam: `/steam/session/validate`<br>Fallback: `/launcher/auth/verify` |

Each dispatch now prints both the provider label and the compatibility policy label, summarizes the credential using a masked preview, and writes the final outcome to the shared response object.【F:src/code/client/ql_auth.c†L44-L273】 This keeps default-disabled or provider-unavailable builds explicit in the client logs instead of collapsing them into a generic dispatcher-only message. The service table ensures that builds compiled without a given backend still advertise accurate capabilities.【F:src/common/platform/platform_services.c†L16-L110】

The same common layer now also exposes an overall online-service mode/policy
summary through `QL_GetOnlineServicesModeLabel()` and
`QL_GetOnlineServicesPolicyLabel()`. Those helpers collapse the cached service
table into a single compatibility-lane label such as
`Build-disabled default (QL_BUILD_ONLINE_SERVICES=0)`,
`Steamworks compatibility lane`, `Open-adapter compatibility lane`, or
`Hybrid compatibility lane`, paired with a policy label that stays explicit
about whether the current lane is default-disabled, runtime-disabled, or an
opted-in heuristic compatibility path. The client mirrors those labels through
the ROM cvars `cl_onlineServicesMode` and `cl_onlineServicesPolicy`, while the
server mirrors them through `sv_onlineServicesMode` and
`sv_onlineServicesPolicy`, which keeps the structural `RW-G01` boundary visible
outside the per-feature provider cvars too.

Those overall labels now also drive the dispatcher's early failure paths.
Steam and standalone requests that never reach a backend emit an explicit
`policy-blocked` lifecycle stage naming the active overall mode/policy pair
before dispatch, and Steam ticket-acquisition failures similarly report a
`ticket-request-failed` stage plus a response tied to the same structural lane
instead of the older generic build/runtime wording.

The retained server auth owner now mirrors that same compatibility story instead
of hiding it behind generic Steam-only wording. `SV_LogPlatformAuth` preserves
the legacy `credential=steam` telemetry field for downstream log consumers, but
it now appends `provider=<...> policy=<...>` to the message payload so the
current auth lane remains explicit in server-side telemetry too. The dedicated
server bootstrap and callback logs likewise reuse the matchmaking descriptor’s
provider/policy labels, which keeps connect, disconnect, callback-registration,
and bootstrap-unavailable diagnostics aligned with the documented
compatibility-only boundary rather than reading like strict-retail service
ownership.

## Structured Outcomes

Handlers normalise their decisions into three high-level outcomes so callers can distinguish fatal errors from transient hiccups. The heuristics live inside the platform backends so each build flavour (Steamworks, open adapter, or hybrid) shares consistent responses, and those response payloads now explicitly identify the heuristic compatibility backend that produced them instead of reading like a retail live-service verdict.【F:src/common/platform/backends/platform_backend_steamworks.c†L1-L31】【F:src/common/platform/backends/platform_backend_open_steam.c†L1-L47】 Hybrid builds automatically replay Steam credentials through the open adapter whenever the Steamworks backend reports `QL_AUTH_RESULT_PENDING`, and the dispatcher now emits an explicit `hybrid-fallback` stage before the open-adapter dispatch so the compatibility-only handoff stays visible in lifecycle traces too.【F:src/code/client/ql_auth.c†L139-L225】【F:tests/test_platform_services.py†L134-L177】

- `success` – the credential was accepted and the legacy code path may continue.
- `retry` – the backend asked for another attempt (for example, a Steam ticket marked with `retry` or a standalone token containing `refresh`).【F:src/common/platform/backends/platform_backend_steamworks.c†L12-L23】【F:src/common/platform/backends/platform_backend_open_steam.c†L25-L33】
- `failure` – the credential was denied or malformed.

The helper `QL_DescribeAuthOutcome` maps enum values to these human-readable strings, which appear in every lifecycle log.【F:src/code/client/ql_auth.c†L26-L83】

## Integration Trace

Run the simulation script to capture an end-to-end trace for both providers:

```bash
python3 tools/integration/auth_flow_trace.py
```

The script drives representative credentials through the same heuristics used in the C implementation and prints the dispatch/result logs.【F:tools/integration/auth_flow_trace.py†L1-L137】 Example output:

```text
== Auth Flow Lifecycle ==
Provider/token combinations demonstrate success, retry, and failure paths.

-- Scenario 1: Steamworks success --
[auth] Steamworks [compatibility-only] dispatch (/steam/session/validate): submitting credential
[auth] Steamworks [compatibility-only] payload summary: ticket=TICKET-…cdef (len=23)
[auth] Steamworks [compatibility-only] result -> outcome=success, message="Steamworks heuristic compatibility backend accepted ticket (ticket=TICKET-…cdef)"
```

Use the remaining scenarios from the script to validate malformed, denied, retry, hybrid-fallback, revoked-token, and accepted-token paths for the retained compatibility backends. Each log line corresponds to the callbacks issued by the client dispatcher when `QL_RequestExternalAuth` runs during a real handshake, including the explicit hybrid fallback handoff into the open adapter when Steamworks returns a retry-eligible result.【F:src/code/client/ql_auth.c†L26-L273】【F:tools/integration/auth_flow_trace.py†L1-L137】
