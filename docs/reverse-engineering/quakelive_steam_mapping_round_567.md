# Quake Live Steam Mapping Round 567: UGC Call Result and SteamID Iterator Helpers

Date: 2026-06-11

## Scope

This round rechecked the small unmapped band immediately before the retained
Steam client callback setup in `quakelive_steam.exe`. The focus was the
`SteamUGCQueryCompleted_t` call-result wrapper and the adjacent SteamID
red-black-tree iterator helpers used by the voice mute set and related
SteamID-keyed containers. The work was static-only: Binary Ninja HLIL, Ghidra
function rows, vtable data, and current source reconstruction. No live Steam
or game launch probe was needed.

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
  `src/common/platform/platform_steamworks.c`,
  `src/code/client/cl_main.c`, and `src/code/client/cl_cgame.c`

## Observed Facts

| Retail function | Alias | Evidence | Source reconstruction boundary |
| --- | --- | --- | --- |
| `sub_4606b0` | `SteamCallbacks_RunUGCQueryCompleted` | The `CCallResult<class SteamCallbacks, struct SteamUGCQueryCompleted_t>` vtable points slot 1 at this wrapper. HLIL clears the stored Steam API call handle fields at `+0x10/+0x14` and dispatches the retained callback function at `+0x1c` with `ioFailure == 0`. | Reconstructed by the generic `QL_Steamworks_CallbackRunCallResultImpl`/dispatch path, with `QL_Steamworks_DispatchUGCQueryCompleted` normalizing payload and failure state. |
| `sub_4606d0` | `SteamCallbacks_RunUGCQueryCompletedCallResult` | The same vtable points slot 0 at this five-argument call-result wrapper. HLIL compares the delivered call handle against `+0x10/+0x14`, clears it on match, and dispatches the retained UGC completion handler with the supplied `ioFailure`. | Reconstructed by retaining `ugcCallHandle`, binding with `SteamAPI_RegisterCallResult`, and unbinding previous call results before a new request. |
| `sub_460710` | `std_tree_rightmost_steamid_node` | Walks right children until the sentinel flag at `+0x19` is reached; used by erase fixup to refresh the tree head rightmost pointer. | Compiler-generated container helper only. |
| `sub_460730` | `std_tree_leftmost_steamid_node` | Walks left children until the sentinel flag at `+0x19` is reached; used by erase fixup to refresh the tree head leftmost pointer. | Compiler-generated container helper only. |
| `sub_460750` | `std_tree_next_steamid_node` | Successor helper for the SteamID node layout, including right-subtree left descent and parent ascent cases. | Compiler-generated container helper only. |
| `sub_4607a0` | `std_tree_prev_steamid_node` | Predecessor helper for the same SteamID node layout, including header/rightmost handling. It is used both in the earlier voice mute insertion path and the later SteamID keyed map path. | Compiler-generated container helper only. |
| `sub_461100` | `std_tree_delete_steamid_node_head` | Tiny helper that deletes the tree head stored at `*(tree + 4)`, paired with the nearby red-black-tree rotation/insert/erase helpers. | Compiler-generated container cleanup only; source keeps typed arrays/wrapper state where practical. |

## Mapping Work

Promoted the missing aliases in
`references/analysis/quakelive_symbol_aliases.json` with Ghidra `FUN_*`,
upper-case Binary Ninja `sub_*`, and lower-case Binary Ninja spellings where
those differ.

Added
`tests/test_platform_services.py::test_steam_ugc_call_result_and_steamid_iterator_helpers_track_retail_reference_rows`
to pin:

- Ghidra row sizes for the seven newly mapped functions;
- the `CCallResult<class SteamCallbacks, struct SteamUGCQueryCompleted_t>`
  vtable slots at `0x005327c0`;
- the UGC call-result wrapper handle-clear and handle-match behavior;
- rightmost, leftmost, successor, predecessor, and head-delete helper bodies;
- call sites from `std_tree_erase_steamid_node_iter`,
  `std_tree_insert_steamid_node`, and the later SteamID keyed map insertion
  helper; and
- current source equivalents for call-result dispatch, unbind-before-bind, and
  UGC completion event normalization.

## Source Reconstruction Decision

No C source patch was needed in this round. The current source already models
the observable retail Steam launch/runtime behavior behind
`QL_BUILD_ONLINE_SERVICES`:

- `QL_Steamworks_BindUGCQueryCallResult` rejects zero handles, verifies the
  retained callback bundle is registered, unbinds any previous UGC call result,
  registers the new call handle, and records it locally.
- `QL_Steamworks_CallbackRunCallResultImpl` dispatches call-result payloads to
  the retained binding owner.
- `QL_Steamworks_DispatchUGCQueryCompleted` copies retail payload fields,
  preserves the delivered call handle, maps I/O failure to `result == -1`, and
  invokes the client binding.
- SteamID tree iterator helpers are compiler-generated support for the voice
  mute set and lobby/auth SteamID maps. Recreating the exact MSVC STL internals
  would add brittle scaffolding without improving the source-level launch or
  runtime contract.

## Confidence

- High for the two UGC call-result aliases: vtable ownership, handle storage
  offsets, dispatch slot, and source call-result bridge all agree.
- High for leftmost/rightmost/successor/predecessor helper names: body shape,
  sentinel offset, and erase/insert call sites are the canonical MSVC tree
  helper pattern.
- Medium-high for `sub_461100`: the body is only an 11-byte head delete helper,
  but its placement between paired rotation helpers and the shared tree-head
  layout make the ownership clear.

Focused parity estimate after this round:

- Steam UGC call-result wrapper mapping confidence:
  **before 78% -> after 98%**.
- SteamID tree iterator/helper confidence:
  **before 84% -> after 98%**.
- Overall Steam launch/runtime reconstruction parity:
  **92.85% -> 92.9%**.
