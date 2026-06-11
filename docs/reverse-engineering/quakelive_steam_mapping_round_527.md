# Quake Live Steam Mapping Round 527: Common Frame GameServer Runtime Pump

## Scope

This pass closes the remaining caller-placement boundary for the Steam
GameServer runtime pump. Round 525 rebuilt the local
`SteamServer_Frame -> SteamServer_UpdatePublishedState(false)` ordering; this
round maps the retail host-frame owner that calls `SteamServer_Frame`
(`sub_466850`) from `Com_Frame` (`sub_4CC6C0` / `FUN_004cc6c0`) before the
broader server simulation frame.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x004cc6c0` | `FUN_004cc6c0` / `sub_4CC6C0` | `Com_Frame` | High |
| `0x00466850` | `FUN_00466850` / `sub_466850` | `SteamServer_Frame` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_004cc6c0` at `0x004cc6c0`, size `1465`, and
  `FUN_00466850` at `0x00466850`, size `827`.
- Ghidra's `FUN_004cc6c0` decompile calls `FUN_00466850()` immediately after
  the optional first `Sys_Milliseconds()` timing sample and before the
  dedicated/client frame pacing branch.
- Binary Ninja HLIL for `sub_4CC6C0` shows the same ordering:
  `var_8_1 = 1`, `sub_466850()`, then the branch on the dedicated/server cvar
  used to compute frame pacing.
- Binary Ninja HLIL for `sub_466850` gates on the retained GameServer
  initialized flag, calls `SteamGameServer_RunCallbacks()`, calls
  `sub_466260(0)`, then performs keepalive, P2P relay, and outgoing packet
  drain work.

Inferred meaning:

- Retail treats the Steam GameServer callback/published-state/P2P pump as a
  host-frame service, not as part of the `SV_Frame` simulation step.
- The source-level `SV_SteamServerNetworkingFrame()` remains the correct body
  counterpart for retail `SteamServer_Frame`, but its caller belongs in
  `Com_Frame` before the normal server frame branch.
- Keeping the helper guarded by `QL_Steamworks_ServerIsInitialised()` preserves
  the repository policy that online Steam services stay behind the existing
  platform-service gates and default-disabled `QL_BUILD_ONLINE_SERVICES`.

## Reconstruction

- Promoted `FUN_004cc6c0 -> Com_Frame` beside the existing Binary Ninja-style
  `sub_4CC6C0 -> Com_Frame` alias.
- Exposed `SV_SteamServerNetworkingFrame()` through the qcommon/server
  interface so the host frame can call the reconstructed Steam server frame
  body directly.
- Moved the `SV_SteamServerNetworkingFrame()` call from `SV_Frame()` into
  `Com_Frame()`, immediately after the first optional frame timing sample and
  before frame pacing, event-loop sleep, and the later `SV_Frame( msec )`.
- Left ZMQ password/RCON pumping and the normal server-info publication work
  in `SV_Frame()`, matching their reconstructed server-side ownership while
  removing the Steam callback pump from that simulation frame.
- Strengthened platform and netcode parity gates so they pin:
  - Ghidra and Binary Ninja aliases for `Com_Frame` and `SteamServer_Frame`;
  - HLIL caller ordering around `sub_4CC6C0 -> sub_466850`;
  - source ordering from `Com_Frame -> SV_SteamServerNetworkingFrame -> SV_Frame`;
  - absence of the Steam server frame call from `SV_Frame()`.

## Remaining Boundary

No runtime launch was needed for this mapping pass. The source change follows
static retail evidence and preserves the default offline-service behavior. The
remaining Steam launch/runtime work is now outside this caller-placement slice:
startup parameter/version edge cases, modern SteamNetworkingMessages parity
gaps, and broader live-service replacement policy.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
- `python -m pytest tests\test_platform_services.py::test_server_frame_reconstructs_retail_steam_server_owner tests\test_platform_services.py::test_server_published_state_reconstructs_retail_steam_server_owner tests\test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners -q --tb=short`
- `python -m pytest tests\test_platform_services.py -q --tb=short`
- `python -m pytest tests\test_netcode_parity_manifest.py::test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck -q --tb=short`
- `python -m pytest tests\test_netcode_parity_manifest.py -q --tb=short`
- `python -m pytest tests\test_client_run_loop_mapping.py -q --tb=short`
- `python -m pytest tests\test_server_full_parity_gate.py -q --tb=short`
- `git diff --check -- src\code\qcommon\common.c src\code\qcommon\qcommon.h src\code\server\sv_main.c src\code\server\server.h references\analysis\quakelive_symbol_aliases.json tests\test_platform_services.py tests\test_netcode_parity_manifest.py tests\test_client_run_loop_mapping.py docs\reverse-engineering\quakelive_steam_mapping_round_527.md IMPLEMENTATION_PLAN.md`

## Parity Estimate

- Focused `Com_Frame -> SteamServer_Frame` caller-placement confidence:
  **before 55% -> after 98%**.
- Focused host-frame Ghidra/Binary Ninja alias bridge confidence:
  **before 50% -> after 98%**.
- Overall Steam launch/runtime integration confidence:
  **before 91.6% -> after 91.7%**.
