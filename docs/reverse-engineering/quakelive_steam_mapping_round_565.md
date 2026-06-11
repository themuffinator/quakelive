# Quake Live Steam Mapping Round 565: Server-Browser Detail and SteamDataSource Helper Kernels

Date: 2026-06-11

## Scope

This round rechecked the remaining unmapped helper band in
`quakelive_steam.exe` around the WebUI Steam server-browser detail path and the
adjacent `SteamDataSource` request maps. The focus was static evidence only:
Binary Ninja HLIL, Ghidra function rows, vtable/RTTI symbols, and the existing
source reconstruction. No live Steam, Awesomium, or game launch probe was
needed.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- Binary Ninja vtable data:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Symbol/name support:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  and `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/common/platform/platform_steamworks.c` and `src/code/client/cl_main.c`

## Observed Facts

| Retail function | Alias | Evidence | Source reconstruction boundary |
| --- | --- | --- | --- |
| `sub_461f10` | `SteamBrowser_FormatServerListFallbackName` | Formats a ring-buffered `"%u.%u.%u.%u:%i"` address string from the `gameserveritem_t` IP and port when the server name is empty. `JSBrowserDetails_OnServerResponded` calls it immediately before publishing `name`. | Reconstructed by `QL_Steamworks_FormatServerListFallbackName` and used by `QL_Steamworks_CopyServerListDisplayName`. |
| `sub_462340` | `JSBrowserDetails_OnServerFailedToRespond` | The `ISteamMatchmakingPingResponse` vtable at `0x00532b0c` pairs `sub_461fe0` with `sub_462340`; the body increments the shared completion counter and deletes the owning `JSBrowserDetails` object after the third terminal callback. | Reconstructed by `CL_SteamBrowser_NativePingFailedImpl` and `QL_Steamworks_CompleteServerBrowserDetailRequestCallback`. |
| `sub_4632a0` | `std_tree_rotate_right_steamid_value_node` | Right-rotation kernel used by `std_tree_erase_steamid_value_node_iter` during erase fixup on the small SteamID value-node layout. | Container helper only; source keeps the observable request ownership in typed wrapper state instead of recreating MSVC STL internals. |
| `sub_463300` | `std_tree_rightmost_steamid_value_node` | Walks right children until the sentinel flag at `+0x15` is reached. | Container helper only. |
| `sub_463320` | `std_tree_leftmost_steamid_value_node` | Walks left children until the sentinel flag at `+0x15` is reached. | Container helper only. |
| `sub_463340` | `std_tree_next_steamid_map_node` | Successor helper for the larger SteamID map-node layout using the sentinel flag at `+0x21`. | Container helper only. |
| `sub_463390` | `std_tree_next_steamid_value_node` | Successor helper for the smaller SteamID value-node layout using the sentinel flag at `+0x15`. | Container helper only. |
| `sub_4633e0` | `std_tree_prev_steamid_map_node` | Predecessor helper for the larger SteamID map-node layout, including the header/rightmost case. | Container helper only. |
| `sub_463610` | `std_tree_rotate_left_steamid_value_node` | Left-rotation kernel paired with `sub_4632a0` in the value-node erase fixup path. | Container helper only. |
| `sub_464060` | `std_tree_destroy_steamid_map` | Destroys a SteamID map by erasing the full `[begin,end)` range through `sub_463f20` and deleting the tree head node. | Represented by guarded SteamDataSource/resource lifecycle cleanup in source. |

## Mapping Work

Promoted the remaining helper aliases in
`references/analysis/quakelive_symbol_aliases.json` with Ghidra `FUN_*`,
upper-case Binary Ninja `sub_*`, and lower-case Binary Ninja spellings where
those differ.

Added
`tests/test_platform_services.py::test_steam_browser_detail_datasource_helper_aliases_track_retail_reference_rows`
to pin:

- Ghidra row sizes for the ten helper functions above;
- the `sub_461f10` fallback-name call from `JSBrowserDetails_OnServerResponded`;
- the `ISteamMatchmakingPingResponse` vtable pair
  `sub_461fe0` / `sub_462340`;
- value-node and map-node iterator/rotation helper signatures and call anchors;
- the `sub_464060` full-range map destructor call into `sub_463f20`; and
- source equivalents for fallback display names and the three-callback
  `JSBrowserDetails` release lifecycle.

## Source Reconstruction Decision

No C source patch was needed in this round. The current source already models
the user-visible retail behavior behind the default-offline service policy:

- empty Steam server names fall back to the retail-formatted address string;
- `RequestServerDetails` owns a ping/rules/players callback bundle;
- the ping-failure leg advances the same three-terminal-callback lifecycle as
  success, rules terminal events, and players terminal events; and
- `SteamDataSource` avatar/resource behavior remains guarded and narrower than
  retail live service usage, as required by `QL_BUILD_ONLINE_SERVICES`.

The promoted tree helpers are retained as binary mapping evidence. Recreating
MSVC STL red-black-tree internals in source would reduce clarity without
improving the observable launch/runtime contract.

## Confidence

- High for `sub_461f10`: call site, format string, raw IP/port accesses, and
  source fallback-name helper agree.
- High for `sub_462340`: the HLIL body and vtable ownership identify it as the
  missing `ISteamMatchmakingPingResponse::ServerFailedToRespond` callback.
- Medium-high for the tree helper aliases: rotation, leftmost/rightmost,
  successor/predecessor, erase-fixup call sites, and sibling node-layout offsets
  agree, but these remain generic compiler-library helpers rather than
  hand-authored gameplay logic.
- Medium-high for `sub_464060`: the destructor body and SteamDataSource
  shutdown call pattern agree; source intentionally uses wrapper lifecycle
  cleanup instead of a literal STL tree destructor.

Focused parity estimate after this round:

- Steam server-browser detail helper alias confidence:
  **before 82% -> after 98%**.
- SteamDataSource map-helper confidence:
  **before 76% -> after 94%**.
- Overall Steam launch/runtime reconstruction parity:
  **92.8% -> 92.85%**.
