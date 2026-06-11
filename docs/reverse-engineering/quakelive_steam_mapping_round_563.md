# Quake Live Steam Mapping Round 563: Voice Mute SteamID Tree Helpers

Date: 2026-06-11

## Scope

This round rechecked the retail Steam client voice mute-set helper corridor in
`quakelive_steam.exe`, covering the MSVC red-black-tree helpers around
`0x004610a0..0x00461ca0` and their public consumers in the retail voice
receive/mute path.

No live Steam behavior was enabled. Voice transport remains behind
`QL_BUILD_ONLINE_SERVICES`, default disabled, with local speaking-state and mute
fallbacks preserved for offline-safe builds.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- Binary Ninja HLIL string anchors:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_main.c`, `src/code/client/cl_cgame.c`, and
  `src/code/client/client.h`

## Observed Facts

| Retail helper | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_4610a0` | `std_tree_rotate_right_steamid_node` | Rotates a SteamID tree node through the left-child/right-subtree pattern used by MSVC tree rebalance and erase repair. | Alias-only STL helper; source does not clone the tree. |
| `sub_461110` | `std_tree_rotate_left_steamid_node` | Rotates a SteamID tree node through the right-child/left-subtree pattern. | Alias-only STL helper; source does not clone the tree. |
| `sub_461170` | `std_tree_insert_steamid_node_rebalance` | Inserts a new SteamID node, checks `map/set<T> too long`, increments the tree count, and rebalances the root black. | Alias-only STL helper used by the retail muted-SteamID set. |
| `sub_4615e0` | `std_tree_erase_steamid_node_iter` | Validates the iterator, repairs red-black colors/rotations, deletes the removed node, and decrements the tree count. | Alias-only STL helper used by retail mute removal and range erase. |
| `sub_461840` | `std_tree_destroy_steamid_node_subtree` | Recursively destroys right subtrees, walks left links, and deletes SteamID tree nodes. | Alias-only STL helper. |
| `sub_461880` | `std_tree_insert_steamid_node` | Walks low/high SteamID ordering and inserts through `sub_461170`, deleting the candidate node on duplicate. | Source-backed by bounded mute identity insertion in `QL_CG_trap_ToggleClientMute`. |
| `sub_461a10` | `std_tree_clear_steamid_node_set` | Clears all nodes, resets sentinel left/right/parent links, and zeroes the count. | Source-backed by bounded mute identity storage reset/overwrite semantics, not literal STL. |
| `sub_461ca0` | `std_tree_erase_steamid_node` | Erases a SteamID range through repeated iterator erase, with a fast full-clear path. | Source-backed by bounded mute identity removal in `QL_CG_trap_ToggleClientMute`. |
| `sub_461990` | `SteamVoice_IsClientMuted` | Searches the muted SteamID tree for a low/high SteamID pair. | Source-backed by `CL_IsVoiceSenderMuted` and `CL_IsSteamIdentityMuted`. |
| `sub_461c00` | `SteamVoice_ToggleClientMute` | Removes an existing SteamID from the set or allocates/inserts a new one, returning the new mute state. | Source-backed by `QL_CG_trap_ToggleClientMute`. |

## Mapping Work

Promoted function spellings:

- `FUN_004610a0`, `sub_4610A0`, `sub_4610a0` -> `std_tree_rotate_right_steamid_node`
- `FUN_00461110`, `sub_461110` -> `std_tree_rotate_left_steamid_node`
- `FUN_00461170`, `sub_461170` -> `std_tree_insert_steamid_node_rebalance`
- `FUN_004615e0`, `sub_4615E0`, `sub_4615e0` -> `std_tree_erase_steamid_node_iter`
- `FUN_00461840`, `sub_461840` -> `std_tree_destroy_steamid_node_subtree`
- `FUN_00461880`, `sub_461880` -> `std_tree_insert_steamid_node`
- `FUN_00461a10`, `sub_461A10`, `sub_461a10` -> `std_tree_clear_steamid_node_set`
- `FUN_00461ca0`, `sub_461CA0`, `sub_461ca0` -> `std_tree_erase_steamid_node`

Added
`tests/test_platform_services.py::test_steam_voice_mute_tree_helpers_track_retail_reference_rows`
to pin:

1. Ghidra rows and sizes for the newly promoted helper functions.
2. HLIL rotate-left, rotate-right, insert/rebalance, iterator erase, subtree
   destroy, set clear, range erase, and public voice mute/toggle anchors.
3. Retail string anchors for `invalid map/set<T> iterator` and
   `map/set<T> too long`.
4. Source equivalents in `CL_IsVoiceSenderMuted`,
   `CL_Steam_ProcessVoicePackets`, `CL_IsSteamIdentityMuted`, and
   `QL_CG_trap_ToggleClientMute`.

## Source Reconstruction Decision

No C source patch was required. The retail binary stores muted Steam identities
in an MSVC `std::set<CSteamID>`-style tree. The reconstructed source uses a
bounded `ql_cgame_mutedIdentitySet[MAX_CLIENTS]` array in `cl_cgame.c`.

That source model preserves the observable runtime contract:

1. a zero Steam identity is never treated as muted;
2. incoming voice packets resolve the sender identity before mixing audio;
3. muted senders are filtered before `S_AddVoiceSamples`;
4. toggling an existing identity removes it and returns unmuted state; and
5. toggling a new identity inserts it when bounded storage is available.

The STL helper names are therefore retained as binary-evidence aliases rather
than source data-structure requirements.

## Confidence

- High for the rotation helper identities: child movement and parent repair
  match MSVC tree left/right rotations.
- High for insert/erase ownership: the helpers are directly called from
  `SteamVoice_ToggleClientMute`, use SteamID low/high ordering, and share the
  retail `map/set<T>` failure strings.
- High for source behavioral equivalence at the user-facing mute contract.
- Medium-high for exact container parity: the source intentionally avoids a
  literal STL tree and uses bounded storage.

## Inference Boundary

Observed facts:

1. Retail `SteamVoice_ProcessIncomingPackets` checks `SteamVoice_IsClientMuted`
   before delivering decompressed voice samples.
2. Retail `SteamVoice_ToggleClientMute` erases an existing SteamID node or
   creates/inserts a new one.
3. The helper band uses the same sentinel-byte, color-byte, count, and
   `map/set<T>` guard patterns as MSVC red-black-tree code.

Inferences:

1. The tree key is the two-word SteamID pair because comparisons use offsets
   `+0x10` and `+0x14`, and both public voice owners pass low/high identity
   words.
2. The source bounded array is behaviorally equivalent for Quake Live client
   slots because the mute surface is limited to resolved player identities.

Open questions:

1. A future live-Steam voice pass could compare remote speaking-state timing
   and packet-channel behavior with real P2P traffic, but that requires online
   services and is outside the default build policy.
2. If later evidence finds another owner for the same node-type helper family,
   the aliases should stay generic rather than become voice-only names.

## Validation

- `python -m pytest tests/test_platform_services.py::test_steam_voice_mute_tree_helpers_track_retail_reference_rows -q`

## Parity Estimate

- Focused Steam voice mute tree helper alias confidence:
  **before 57% -> after 98%**.
- Focused Steam voice mute source-equivalence confidence:
  **before 90% -> after 94%**.
- Overall Steam launch/runtime reconstruction parity:
  **92.75% -> 92.8%**.
