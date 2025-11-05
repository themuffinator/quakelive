# Credential Validation Matrix

This matrix captures the expected authentication behaviour across Steam-only, open-only, and hybrid builds, along with validation steps and sample logs from the scripted auth flow trace.

## Build Targets and Active Providers

| Build flag preset | `QL_PLATFORM_HAS_STEAMWORKS` | `QL_PLATFORM_HAS_OPEN_STEAM` | Effective provider | Dispatch endpoint |
| --- | --- | --- | --- | --- |
| Steam-only (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=0`) | `1` | `0` | Steamworks | `/steam/session/validate` |
| Open-only (`QL_BUILD_STEAMWORKS=0`, `QL_BUILD_OPEN_STEAM=1`) | `0` | `1` | Open Steam Adapter | `/launcher/auth/verify` |
| Hybrid (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1`) | `1` | `1` | Hybrid dispatcher (Steam primary, open fallback) | Steam: `/steam/session/validate`<br>Fallback: `/launcher/auth/verify` |

The `platform_config.h` macros turn the `QL_BUILD_*` definitions into capability flags, and `platform_services.c` exposes the matching provider names and handlers via `QL_GetPlatformServices`.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L200-L281】

## Test Plan: Steam-only Build

1. Configure the build with `QL_BUILD_STEAMWORKS=1` and `QL_BUILD_OPEN_STEAM=0` so the service table exposes only the Steamworks handler.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L200-L236】
2. Launch a client session and acquire a Steam ticket (use `steam:<token>` when invoking `QL_ParseCredentialString`).【F:src/common/auth_credentials.c†L62-L105】
3. Trigger `QL_RequestExternalAuth` and confirm the dispatcher routes the request to the Steam endpoint, logging the ticket preview and outcome via `QL_ClientAuth_LogStage` and `QL_ClientAuth_LogResponse`.【F:src/code/client/ql_auth.c†L38-L126】
4. Validate outcomes:
   - Short tickets (`len < 16`) produce `failure` with "payload too short".
   - Tickets containing `retry` return `retry`, prompting the caller to refresh the Steam ticket.
   - Tickets with `denied` or `invalid` return `failure` describing the backend denial.
   - Otherwise expect `success` and proceed with the legacy authorize path.【F:src/common/platform/platform_services.c†L40-L106】

## Test Plan: Open-only Build

1. Compile with `QL_BUILD_STEAMWORKS=0` and `QL_BUILD_OPEN_STEAM=1` so only the open adapter is registered as the auth provider.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L200-L236】
2. Acquire a launcher credential (use `standalone:<token>`).【F:src/common/auth_credentials.c†L69-L105】
3. Execute `QL_RequestExternalAuth` and confirm the dispatcher logs the `/launcher/auth/verify` endpoint with the token preview before invoking the adapter.【F:src/code/client/ql_auth.c†L86-L126】
4. Validate responses:
   - Short tokens (`len < 12`) are denied.
   - Tokens containing `refresh` request a retry.
   - Tokens containing `revoke` or `denied` are rejected.
   - Valid tokens return `success` and the message `Standalone token accepted …`.【F:src/common/platform/platform_services.c†L108-L175】

## Test Plan: Hybrid Build

1. Enable both providers (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1`) so the service table registers the hybrid dispatcher that first queries Steamworks and then falls back to the open adapter.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L176-L236】
2. Submit a Steam credential via `QL_RequestExternalAuth`. Observe the Steam dispatch logs and ensure the request initially targets `/steam/session/validate`.【F:src/code/client/ql_auth.c†L86-L126】
3. Induce a fallback by supplying a ticket that contains the substring `retry`. The Steamworks handler returns `QL_AUTH_RESULT_PENDING`, prompting the hybrid flow to retry the credential through the open adapter.【F:src/common/platform/platform_services.c†L40-L149】【F:src/common/platform/platform_services.c†L152-L209】
4. Confirm the fallback request logs both the original Steam stage and the open adapter result message `Hybrid fallback accepted credential via open adapter …`.【F:src/common/platform/platform_services.c†L152-L209】

### Validation Session Logs

Execute the scripted lifecycle trace to capture reference logs:

```bash
python3 tools/integration/auth_flow_trace.py
```

Sample output for the hybrid fallback scenario:

```text
-- Scenario 2: Hybrid --
[auth] Hybrid dispatch (/steam/session/validate): submitting credential
[auth] Hybrid payload summary: ticket=retry:T…FFFF (len=21)
[auth] Hybrid result -> outcome=success, message="Hybrid fallback accepted credential via open adapter (token=retry:T…FFFF)"
```

The script mirrors the dispatcher logging by chaining the hybrid Steam and open-adapter handlers, demonstrating the fallback path described above.【14b840†L1-L19】【F:tools/integration/auth_flow_trace.py†L48-L98】

## Summary of Findings

- Steam-only builds route exclusively through Steamworks and surface retry semantics when tickets contain `retry` markers.【F:src/common/platform/platform_services.c†L40-L106】
- Open-only builds rely on the launcher adapter and surface retry semantics for `refresh` tokens while rejecting revoked credentials.【F:src/common/platform/platform_services.c†L108-L175】
- Hybrid builds honour the Steam result first but convert pending responses into successful open-adapter fallbacks, logging the acceptance message shown in the validation trace.【F:src/common/platform/platform_services.c†L152-L209】【14b840†L9-L13】
