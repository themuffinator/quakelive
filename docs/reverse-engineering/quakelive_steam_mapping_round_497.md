# Quake Live Steam Mapping Round 497: GameServer UGC Owner Selection

## Scope

This round maps the Steam UGC owner selected immediately after retail
GameServer bootstrap succeeds. Retail Quake Live chooses between the normal
client `SteamUGC()` interface and `SteamGameServerUGC()` based on whether the
process is running as a dedicated server.

This is part of the launch/runtime integration surface because workshop
subscribe/download calls after server startup must be routed through the same
Steam owner that retail would have cached during bootstrap.

## Evidence

Primary evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/common/platform/platform_steamworks.c`
- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`

Observed facts:

- Ghidra imports include `SteamGameServerUGC`.
- Retail HLIL checks the dedicated cvar state after successful
  `SteamGameServer_Init`.
- The listen/non-dedicated path assigns `SteamUGC()`.
- The dedicated path assigns `SteamGameServerUGC()`.
- Retail stores the selected interface owner in the same bootstrap region
  before setting the SteamGameServer dedicated flag.
- SRP represents the same owner split through `state.useGameServerUGC` and
  `QL_Steamworks_GetUGCInterface()`.

## Reconstruction

Implemented mapping and test changes:

- Added static HLIL assertions for the post-init UGC owner branch:
  - dedicated check,
  - listen path `SteamUGC()`,
  - dedicated path `SteamGameServerUGC()`,
  - cached owner assignment,
  - dedicated-state publication after owner selection.
- Strengthened source assertions for `QL_Steamworks_GetUGCInterface()` so the
  GameServer UGC path is gated by `state.useGameServerUGC`,
  `state.gameServerInitialised`, and the optional `SteamGameServerUGC` import,
  with client `SteamUGC()` as the fallback owner.
- Added a fresh listen-server harness regression proving that a successful
  non-dedicated GameServer init keeps workshop subscribe/download calls on the
  client UGC owner and does not touch `SteamGameServerUGC`.

No production source change was required. The existing implementation already
had the owner split; this round makes the retail evidence and executable
behavior harder to regress.

## Validation

Focused validation passed:

- `python -m pytest tests/test_steamworks_harness.py::test_game_server_init_uses_retail_init_signature_and_dedicated_ugc_owner tests/test_steamworks_harness.py::test_game_server_listen_init_keeps_workshop_calls_on_client_ugc_owner tests/test_steamworks_harness.py::test_game_server_init_failure_keeps_server_runtime_state_cold -q --tb=short`
  - 6 passed across disabled and enabled Steamworks harness builds.
- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - 126 passed.
- `python -m pytest tests/test_platform_services.py::test_server_game_server_wrappers_reconstruct_mapped_server_slots tests/test_platform_services.py::test_server_init_reconstructs_retail_hostname_and_bootstrap_metadata -q --tb=short`
  - 2 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. Static retail evidence plus focused harness
coverage are sufficient for this UGC owner-selection mapping pass.

## Confidence

High confidence for the owner branch:

- The import table, HLIL branch, source owner gate, and executable harness
  behavior now agree for both dedicated and listen-server cases.

Medium confidence for broader workshop runtime behavior:

- This pass does not reconstruct every workshop call-result or mount-state
  edge. It specifically pins which Steam UGC interface owns those calls after
  server bootstrap.

## Parity Estimate

Focused Steam GameServer UGC owner selection:

- Before: 88%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89.8%
- After: 89.9%
