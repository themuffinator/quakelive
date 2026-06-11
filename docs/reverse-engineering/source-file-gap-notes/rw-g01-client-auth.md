# `src/code/client/ql_auth.c` Divergence Note

Last updated: 2026-05-24

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Permanent bounded divergence for default builds; this dispatcher intentionally routes into bounded compatibility backends unless a documented open replacement path is adopted.

## Why this file remains a documented divergence

The client auth owner cleanly reconstructs the dispatcher and ticket lifetime, but the actual online-service lane it drives is still bounded by build/runtime policy and heuristic Steam or open-adapter backends.

## Observed facts

- Steam auth requests are blocked entirely when `CL_SteamServicesEnabled()` is false.
- Standalone launcher auth is blocked when `CL_OnlineServicesEnabled()` is false.
- `QL_Auth_ExecuteRequest` requests a fresh retained Steam ticket before dispatch
  through the retail-style `SteamClient_GetAuthSessionTicket` wrapper.
- Hybrid dispatch falls back to the open adapter only when Steamworks is
  unavailable or returns `QL_AUTH_RESULT_PENDING`.
- The surrounding platform-service cvar surface now publishes the same permanent bounded divergence through `cl_onlineServicesParityScope` and `cl_onlineServicesParityReason`.

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
| `QL_ClientAuth_HandleHybridSteam` | `divergence owner` | Explicitly encodes the hybrid compatibility fallback from Steamworks to the open adapter for unavailable or pending results while preserving Steamworks denials. |
| `QL_ClientAuth_DispatchSteam` | `divergence owner` | Selects between Steamworks, open-adapter, and hybrid compatibility providers. |
| `QL_Auth_ExecuteRequest` | `divergence owner` | Top-level auth request path remains gated by build/runtime policy and bounded providers. |

## Maintenance expectations

- Keep the dispatcher aligned with the bounded provider set while this lane remains a permanent bounded divergence.
- If the providers beneath it change, refresh `platform_services.c`, the backend files, and the runtime evidence/docs together so the auth story stays consistent end-to-end.
