# Credential Validation Matrix

This matrix captures the expected authentication behaviour across Steam-only, open-only, and hybrid builds following the unified dispatcher that now fronts the Steamworks and open-adapter authentication flows. The goal of this document is to outline coverage expectations, provide reproducible validation sessions, and archive the logs collected while exercising the new hybrid fallback path.

## Build Targets and Active Providers

| Build flag preset | `QL_PLATFORM_HAS_STEAMWORKS` | `QL_PLATFORM_HAS_OPEN_STEAM` | Effective provider | Dispatch endpoint |
| --- | --- | --- | --- | --- |
| Steam-only (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=0`) | `1` | `0` | Steamworks | `/steam/session/validate` |
| Open-only (`QL_BUILD_STEAMWORKS=0`, `QL_BUILD_OPEN_STEAM=1`) | `0` | `1` | Open Steam Adapter | `/launcher/auth/verify` |
| Hybrid (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1`) | `1` | `1` | Hybrid dispatcher (Steam primary, open fallback) | Steam: `/steam/session/validate`<br>Fallback: `/launcher/auth/verify` |

The `platform_config.h` macros turn the `QL_BUILD_*` definitions into capability flags, and `platform_services.c` exposes the matching provider names via `QL_GetPlatformServices`.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L1-L54】

## Test Plan: Steam-only Build

**Objective:** Validate that the Steamworks handler is the sole authentication provider and that the client surfaces retry guidance for transient Steam errors.

**Preconditions**

- Build with `QL_BUILD_STEAMWORKS=1` and `QL_BUILD_OPEN_STEAM=0`, allowing only the Steamworks capability flags to resolve in `QL_GetPlatformServices`.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L1-L54】
- Prepare a Steam credential (e.g., `steam:<token>`) for `QL_ParseCredentialString`.【F:src/common/auth_credentials.c†L62-L105】

**Procedure**

1. Launch the client and call `QL_RequestExternalAuth` with the prepared Steam ticket.
2. Observe the dispatcher logs (`QL_ClientAuth_LogStage`/`QL_ClientAuth_LogResponse`) to confirm traffic is routed to `/steam/session/validate` and no fallback providers are enumerated.【F:src/code/client/ql_auth.c†L62-L83】【F:src/code/client/ql_auth.c†L274-L318】
3. Exercise ticket classifications:
   - Supply a ticket shorter than 16 characters to trigger the "payload too short" failure.
   - Include `retry` to provoke the Steam retry response and verify the client surfaces the refresh guidance.
   - Include `denied`/`invalid` to verify denial propagation.
   - Use a valid ticket to confirm the success path hands off to the legacy authorize step.【F:src/code/client/ql_auth.c†L111-L163】

**Expected Results**

- Only Steamworks endpoints are logged.
- Retry and denial semantics mirror the heuristics defined in `QL_ClientAuth_HandleSteamResult`.

## Test Plan: Open-only Build

**Objective:** Validate the open launcher adapter as the exclusive provider and ensure retry/denial semantics reflect the new credential parser.

**Preconditions**

- Build with `QL_BUILD_STEAMWORKS=0` and `QL_BUILD_OPEN_STEAM=1`, restricting the capability flags to the open adapter.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L1-L54】
- Prepare launcher credentials (e.g., `standalone:<token>`).【F:src/common/auth_credentials.c†L69-L105】

**Procedure**

1. Trigger `QL_RequestExternalAuth` and confirm the dispatcher logs `/launcher/auth/verify` before invoking the adapter implementation.【F:src/code/client/ql_auth.c†L274-L318】
2. Validate token classifications:
   - Tokens shorter than 12 characters are rejected.
   - Tokens containing `refresh` emit a retry result.
   - Tokens containing `revoke`/`denied` produce failures.
   - Valid tokens complete successfully with the acceptance message.【F:src/code/client/ql_auth.c†L166-L195】

**Expected Results**

- No Steamworks stages are logged.
- Retry and failure messaging follows `QL_ClientAuth_HandleStandaloneResult`.

## Test Plan: Hybrid Build

**Objective:** Exercise the dual-provider dispatcher, demonstrating Steam-first authentication with a verified fallback into the open adapter when Steam reports a pending status.

**Preconditions**

- Enable both providers (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1`). This configuration exposes the hybrid dispatcher that wraps both handlers.【F:src/common/platform/platform_config.h†L1-L37】【F:src/common/platform/platform_services.c†L1-L54】
- Prepare a Steam credential containing the substring `retry` so the Steamworks result returns `QL_AUTH_RESULT_PENDING`.【F:src/code/client/ql_auth.c†L111-L163】

**Procedure**

1. Invoke `QL_RequestExternalAuth` with the prepared credential and confirm the first dispatch targets `/steam/session/validate`.
2. Observe that the pending result automatically feeds the credential into the open adapter, generating a second dispatch to `/launcher/auth/verify` without caller intervention.【F:src/code/client/ql_auth.c†L197-L225】【F:src/code/client/ql_auth.c†L274-L318】
3. Verify the hybrid result log reports `Hybrid fallback accepted credential via open adapter …` and the final outcome is `success`.

**Expected Results**

- Steam stage logs precede the fallback stage.
- The fallback completes successfully even though the initial Steam invocation reported a pending state, validating the new hybrid control flow.

## Validation Sessions and Log Capture

To capture canonical logs for each scenario and to archive proof of the hybrid fallback behaviour, run the scripted lifecycle trace and persist the output:

```bash
python3 tools/integration/auth_flow_trace.py | tee docs/qa/logs/auth_flow_trace.log
```

The script reflects the same classification rules implemented by the client dispatcher, making it suitable for regression validation.【F:tools/integration/auth_flow_trace.py†L48-L98】 Each scenario slice of the captured transcript is archived for direct linkage from this matrix:

| Scenario | Log archive |
| --- | --- |
| Steam-only | [`steam_only_auth_flow.log`](logs/steam_only_auth_flow.log) |
| Hybrid | [`hybrid_auth_flow.log`](logs/hybrid_auth_flow.log) |
| Open-only | [`open_only_auth_flow.log`](logs/open_only_auth_flow.log) |
| Full trace | [`auth_flow_trace.log`](logs/auth_flow_trace.log) |

These artefacts sit alongside the original hybrid validation log for historical comparison.【F:docs/qa/logs/auth_flow_trace.log†L1-L18】【F:docs/qa/logs/steam_only_auth_flow.log†L1-L5】【F:docs/qa/logs/hybrid_auth_flow.log†L1-L5】【F:docs/qa/logs/open_only_auth_flow.log†L1-L9】【F:docs/qa/logs/hybrid_auth_flow_validation.log†L1-L19】

## Summary of Findings

- Steam-only builds route exclusively through Steamworks, yielding the expected success message when presented with a valid ticket and no evidence of fallback providers in the lifecycle trace.【F:docs/qa/logs/steam_only_auth_flow.log†L1-L5】
- Open-only builds exercise both the retry guidance for expired launcher tokens and the success path for valid credentials, matching the open adapter heuristics and confirming that no Steam stages are emitted.【F:docs/qa/logs/open_only_auth_flow.log†L1-L9】
- Hybrid builds report the Steam dispatch followed by a successful hybrid verdict, demonstrating the fallback acceptance messaging while highlighting that only the Steam dispatch is currently logged in the scripted trace.【F:docs/qa/logs/hybrid_auth_flow.log†L1-L5】

## Open Issues

- The scripted hybrid trace does not emit a second dispatch entry for the open adapter fallback, making it difficult to prove the dual-provider routing from the log alone. Extend `auth_flow_trace.py` to log the open adapter stage after a Steam pending result.【F:docs/qa/logs/hybrid_auth_flow.log†L1-L5】【F:tools/integration/auth_flow_trace.py†L57-L93】
- Steam-only coverage lacks the negative ticket classifications (`payload too short`, `denied/invalid`) described in the plan; add scripted samples so the archived logs capture those outcomes for regression tracking.【F:docs/qa/logs/steam_only_auth_flow.log†L1-L5】【F:docs/qa/credential-matrix.md†L31-L54】
- The open-only archive omits a revoked-token failure sample, leaving the matrix without trace evidence for that branch. Add a `revoke` token sample to the integration script and log catalogue.【F:docs/qa/logs/open_only_auth_flow.log†L1-L9】【F:docs/qa/credential-matrix.md†L67-L81】
