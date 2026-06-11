# Quake Live Steam Mapping Round 561: idSteamStats Callback Lifecycle Helpers

Date: 2026-06-11

## Scope

This round rechecked the retail `idSteamStats` callback-object lifecycle and
the adjacent SteamID stats-session map rotations in `quakelive_steam.exe`.

No live Steam behavior was enabled. The source remains default-offline unless
`QL_BUILD_ONLINE_SERVICES` enables Steam-backed services.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- Binary Ninja HLIL vtable data:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/common/platform/platform_steamworks.c`

## Observed Facts

| Retail helper | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_467430` | `SteamStatsCallback_DestroyServersConnected` | Restores the `idSteamStats` `SteamServersConnected_t` callback vtable and unregisters when the registered flag is set. | Source-backed by `QL_Steamworks_UnregisterCallbackObject` on `serverCallbacks.serversConnected`. |
| `sub_467460` | `SteamStatsCallback_DestroyGSStatsReceived` | Restores the `GSStatsReceived_t` callback vtable and unregisters through `SteamAPI_UnregisterCallback`. | Source-backed by `serverCallbacks.gsStatsReceived` teardown. |
| `sub_467490` | `SteamStatsCallback_DestroyGSStatsStored` | Restores the `GSStatsStored_t` callback vtable and unregisters through `SteamAPI_UnregisterCallback`. | Source-backed by `serverCallbacks.gsStatsStored` teardown. |
| `sub_4674b0` | `std_tree_rotate_right_steamid_map_node` | Performs a right rotation around a SteamID stats-map node during red-black insertion. | Kept as an alias-only STL helper; source uses bounded client sessions. |
| `sub_4675c0` | `std_tree_rotate_left_steamid_map_node` | Performs a left rotation around a SteamID stats-map node during red-black insertion. | Kept as an alias-only STL helper; source uses bounded client sessions. |
| `sub_467560` | `SteamStats_Shutdown` | Deletes the stat descriptor array, then unregisters stored, received, and connected callback objects in reverse order. | Source-backed by `QL_Steamworks_UnregisterServerCallbacks`. |
| `sub_467850` | `SteamStats_Init` | Registers `idSteamStats` callbacks for event IDs `0x65`, `0x708`, and `0x709`, then requests stats if the game server is logged on. | Source-backed by server callback registration and `SV_SteamStats_RequerySessions`. |

## Mapping Work

Promoted function spellings:

- `FUN_00467430`, `sub_467430` -> `SteamStatsCallback_DestroyServersConnected`
- `FUN_00467460`, `sub_467460` -> `SteamStatsCallback_DestroyGSStatsReceived`
- `FUN_00467490`, `sub_467490` -> `SteamStatsCallback_DestroyGSStatsStored`
- `FUN_004674b0`, `sub_4674B0`, `sub_4674b0` -> `std_tree_rotate_right_steamid_map_node`
- `FUN_004675c0`, `sub_4675C0`, `sub_4675c0` -> `std_tree_rotate_left_steamid_map_node`

Added
`tests/test_platform_services.py::test_steam_stats_callback_lifecycle_helpers_track_retail_reference_rows`
to pin:

1. Ghidra rows and sizes for the newly named helper functions.
2. HLIL destructor thunk behavior and `SteamAPI_UnregisterCallback` edges.
3. HLIL `idSteamStats` vtable payload-size buckets in part 06.
4. `SteamStats_Init` registration offsets and event IDs:
   `SteamServersConnected_t` at `0x65`, `GSStatsReceived_t` at `0x708`, and
   `GSStatsStored_t` at `0x709`.
5. Source callback-state ownership, registration, reverse teardown order, and
   optional-unregister guard behavior.

## Source Reconstruction Decision

No C source patch was required. The retail binary owns three separate
`CCallback<class idSteamStats, ...>` subobjects inside the `idSteamStats`
instance. The reconstructed source intentionally uses one generic
`ql_steam_callback_base_t` representation with explicit callback IDs, payload
sizes, dispatch functions, and `QL_STEAM_CALLBACK_FLAG_REGISTERED`.

That source model is equivalent for the observable runtime contract:

1. callbacks are registered against the game-server callback pump;
2. registered server stats callbacks use the retail IDs `0x65`, `0x708`, and
   `0x709`;
3. teardown unregisters stats-stored, stats-received, and connected callback
   objects before clearing the callback state; and
4. the default build remains offline-safe when Steam services are not compiled
   or initialised.

The two tree rotation helpers remain alias-only evidence. The source keeps the
bounded `sv_steamStatsSessions[MAX_CLIENTS]` representation documented in round
558 rather than reconstructing MSVC STL node rotations.

## Confidence

- High for callback destructor identity: vtable writes, registered-flag tests,
  and unregister imports agree across HLIL and Ghidra.
- High for event-ID ownership: `SteamStats_Init` registers `0x65`, `0x708`,
  and `0x709` against the three `idSteamStats` callback subobjects, matching
  source callback constants.
- High for rotation helper identity: pointer movement matches right/left tree
  rotations and the helpers are adjacent to the mapped insert/rebalance path.
- Medium-high for source equivalence: retail uses C++ callback subobjects,
  while source uses one generic callback object layout. The ABI-visible
  behavior is pinned, but object layout is intentionally not cloned.

## Inference Boundary

Observed facts:

1. Retail `idSteamStats` uses three game-server callback subobjects and
   unregisters them through `SteamAPI_UnregisterCallback`.
2. Retail vtable data reports a one-byte payload for `SteamServersConnected_t`
   and 12-byte payloads for `GSStatsReceived_t` and `GSStatsStored_t`.
3. Retail stats-session map insertion uses adjacent left and right rotation
   helpers.

Inferences:

1. The source generic callback object is a faithful reconstruction of retail
   callback registration and teardown when callback ID, payload size, dispatch
   target, and game-server flag match.
2. The stats-session rotation helpers are STL implementation detail, not a
   source-level data-structure requirement for the GPL reconstruction.

Open questions:

1. A future live Steam validation pass could compare callback delivery timing
   under actual `SteamGameServerStats` responses, but that would require
   enabling online services and is outside the default build policy.
2. Later template analysis may refine the tree helper names if another
   SteamID-keyed map instantiation is separated by value layout.

## Validation

- `python -m pytest tests/test_platform_services.py::test_steam_stats_callback_lifecycle_helpers_track_retail_reference_rows -q`

## Parity Estimate

- Focused `idSteamStats` callback lifecycle helper confidence:
  **before 74% -> after 99%**.
- Focused stats-session map rotation helper confidence:
  **before 58% -> after 96%**.
- Focused source-equivalence confidence for server stats callback teardown:
  **before 96% -> after 98%**.
- Overall Steam launch/runtime reconstruction parity:
  **92.65% -> 92.7%**.
