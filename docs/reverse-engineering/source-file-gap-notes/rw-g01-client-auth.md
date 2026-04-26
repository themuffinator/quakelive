# `src/code/client/ql_auth.c` Divergence Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Documented repo-wide divergence; this dispatcher intentionally routes into bounded compatibility backends.

## Why this file remains a documented divergence

The client auth owner cleanly reconstructs the dispatcher and ticket lifetime, but the actual online-service lane it drives is still bounded by build/runtime policy and heuristic Steam or open-adapter backends.

## Observed facts

- Steam auth requests are blocked entirely when `CL_SteamServicesEnabled()` is false.
- Standalone launcher auth is blocked when `CL_OnlineServicesEnabled()` is false.
- Hybrid dispatch explicitly falls back to the open adapter whenever the Steamworks lane does not accept the credential.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `QL_ClientAuth_MapOutcome` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_DescribeAuthOutcome` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_SetResponse` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_LogStage` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_LogResponse` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_TokenPreview` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_GetEndpoint` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_ReportPolicyBlock` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_InvokeBackend` | `bounded compatibility` | Reports build-unavailable backend states instead of closing the live-service lane. |
| `QL_ClientAuth_SetSteamTicketHandle` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_RequestSteamTicket` | `bounded compatibility` | Still depends on the build/runtime Steam-service gate before any online auth path exists. |
| `QL_ClientAuth_CancelSteamTicket` | `helper closed` | Local helper or logging function; not the direct remaining parity blocker on its own. |
| `QL_ClientAuth_HandleSteamworksTicket` | `divergence owner` | Dispatches into the heuristic Steamworks backend. |
| `QL_ClientAuth_HandleOpenSteamTicket` | `divergence owner` | Dispatches into the heuristic open-adapter Steam fallback path. |
| `QL_ClientAuth_HandleStandaloneToken` | `divergence owner` | Dispatches standalone launcher tokens into the same bounded open-adapter lane. |
| `QL_ClientAuth_HandleHybridSteam` | `divergence owner` | Explicitly encodes the hybrid compatibility fallback from Steamworks to the open adapter. |
| `QL_ClientAuth_DispatchSteam` | `divergence owner` | Selects between Steamworks, open-adapter, and hybrid compatibility providers. |
| `QL_Auth_ExecuteRequest` | `divergence owner` | Top-level auth request path remains gated by build/runtime policy and bounded providers. |

## Maintenance expectations

- Keep the dispatcher aligned with the bounded provider set while this lane remains a documented divergence.
- If the providers beneath it change, refresh `platform_services.c`, the backend files, and the runtime evidence/docs together so the auth story stays consistent end-to-end.
