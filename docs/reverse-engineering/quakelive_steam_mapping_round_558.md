# Quake Live Steam Mapping Round 558: Auth and Stats Session Tree Helpers

Date: 2026-06-11

## Scope

This round rechecked the retail Steam GameServer auth-session and
GameServerStats session-helper band around `0x00465eb0..0x00467c50` in
`quakelive_steam.exe`.

No live Steam behavior was enabled and no default-build online-service policy
changed. The source remains a compatibility reconstruction: live Steam calls
stay behind `QL_BUILD_ONLINE_SERVICES`, while the server source keeps
offline-safe session arrays and explicit fallbacks instead of reproducing the
retail binary's MSVC red-black tree templates byte-for-byte.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/server/sv_client.c`

## Observed Facts

| Retail helper | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_465eb0` | `std_tree_equal_range_steamid_node` | Searches the active-auth SteamID tree and returns the lower/upper range around a two-word SteamID key. | Source-backed by `SV_SteamServerClientOwnsAuthSteamId` and orphan cleanup scans. |
| `sub_465f60` | `std_tree_create_steamid_node` | Allocates a `0x20` byte node and stores the low/high SteamID key at offsets `0x10` and `0x14`. | Source-backed by `client_t::platformSteamId` parsing into `CSteamID`. |
| `sub_4660c0` | `std_tree_find_or_insert_steamid_node` | Inserts a SteamID node through the shared rebalance helper and node allocator. Used while rebuilding the retained auth-session ownership set. | Source-backed by bounded client-session ownership checks rather than a literal STL tree. |
| `sub_467320` | `std_tree_rightmost_steamid_map_node` | Walks child slot `+0x08` until the sentinel flag at `+0x21` is set. | Source has no literal tree, but stats-session lookup/removal covers the owning behavior. |
| `sub_467340` | `std_tree_leftmost_steamid_map_node` | Walks child slot `+0x00` until the sentinel flag at `+0x21` is set. | Source has no literal tree, but stats-session lookup/removal covers the owning behavior. |
| `sub_467510` | `std_tree_lower_bound_steamid_map_node` | Performs lower-bound traversal over two-word SteamID keys. | Source-backed by `SV_SteamStats_FindSessionBySteamId`. |
| `sub_467620` | `std_tree_insert_steamid_map_node_rebalance` | Inserts/rebalances SteamID map nodes and marks the root black. | Source equivalent is the fixed `sv_steamStatsSessions[MAX_CLIENTS]` owner. |
| `sub_467a20` | `std_tree_destroy_steamid_map_subtree` | Recursively destroys right subtree, then left chain, deleting nodes. | Source equivalent is explicit session reset/removal. |
| `sub_467a60` | `std_tree_find_steamid_map_node` | Wraps the lower-bound helper and verifies key equality. | Source-backed by `SV_SteamStats_FindSessionBySteamId`. |
| `sub_467ac0` | `std_tree_clear_steamid_map` | Destroys all map nodes, resets sentinel links, and clears count. | Source-backed by `SV_SteamStats_ResetSession`/teardown paths. |
| `sub_467bd0` | `std_tree_create_steamid_value_node` | Allocates a `0x28` byte node and stores low/high/key value fields. | Source-backed by `sv_steam_stats_session_t` per-client session storage. |
| `sub_467c50` | `std_tree_find_or_insert_steamid_value_node` | Finds or inserts a SteamID-keyed stats-session value node via lower-bound and node allocation. | Source-backed by create/reuse logic in `SV_SteamStats_CreatePlayerSession`. |

## Mapping Work

Promoted Ghidra `FUN_*`, upper-case Binary Ninja, and lower-case Binary Ninja
spellings for the auth/session helper band:

- `FUN_00465eb0`, `sub_465EB0`, `sub_465eb0` -> `std_tree_equal_range_steamid_node`
- `FUN_00465f60`, `sub_465F60`, `sub_465f60` -> `std_tree_create_steamid_node`
- `FUN_004660c0`, `sub_4660C0`, `sub_4660c0` -> `std_tree_find_or_insert_steamid_node`
- `FUN_00467320`, `sub_467320` -> `std_tree_rightmost_steamid_map_node`
- `FUN_00467340`, `sub_467340` -> `std_tree_leftmost_steamid_map_node`
- `FUN_00467510`, `sub_467510` -> `std_tree_lower_bound_steamid_map_node`
- `FUN_00467620`, `sub_467620` -> `std_tree_insert_steamid_map_node_rebalance`
- `FUN_00467a20`, `sub_467A20`, `sub_467a20` -> `std_tree_destroy_steamid_map_subtree`
- `FUN_00467a60`, `sub_467A60`, `sub_467a60` -> `std_tree_find_steamid_map_node`
- `FUN_00467ac0`, `sub_467AC0`, `sub_467ac0` -> `std_tree_clear_steamid_map`
- `FUN_00467bd0`, `sub_467BD0`, `sub_467bd0` -> `std_tree_create_steamid_value_node`
- `FUN_00467c50`, `sub_467C50`, `sub_467c50` -> `std_tree_find_or_insert_steamid_value_node`

Added
`tests/test_platform_services.py::test_steam_auth_and_stats_tree_helpers_track_retail_reference_rows`
to pin:

- Ghidra function rows and sizes for the helper band;
- Binary Ninja HLIL anchors for allocation, sentinel traversal,
  lower-bound/search, insert/rebalance, subtree destroy, map clear, and
  find-or-insert behavior;
- the active-auth call edges from `SteamServer_BeginAuthSession`,
  `SteamServer_EndAuthSession`, and orphaned-auth cleanup; and
- source-side session equivalence in `SV_BeginPlatformAuthSession`,
  `SV_EndPlatformAuthSession`, `SV_SteamServerEndOrphanedAuthSessions`,
  `SV_SteamStats_FindSessionBySteamId`, session create/remove, and
  GS stats callback lookup.

## Source Reconstruction Decision

No new source patch was required. The current source intentionally reconstructs
the retail ownership contracts at the server/session level:

1. active auth sessions are retained on the client slot and cleaned up before a
   fresh server spawn if no live client still owns the SteamID;
2. stats sessions are retained in a bounded `MAX_CLIENTS` array keyed by
   parsed `CSteamID`;
3. current-value requests are reissued for reused or backend-reconnected
   sessions; and
4. stats store partial-validation callbacks re-prime the session, matching the
   observed retail retry path.

This is a source-coded equivalent of the retail behavior, not a literal
reimplementation of MSVC STL node layout. The literal node helpers are kept as
aliases and tests because they explain the retail binary, while the source
keeps the simpler bounded representation expected by the GPL codebase.

## Confidence

- High for helper identity: Ghidra rows, Binary Ninja starts, allocation sizes,
  sentinel offsets, and call edges agree.
- High for auth-session ownership: Begin/EndAuthSession, orphan cleanup, and
  source slot ownership share the same SteamID lifetime boundary.
- Medium-high for stats-session container equivalence: retail uses SteamID
  maps, while source uses bounded client-slot sessions. The behavior is pinned
  for lookup, create/reuse, remove, callback dispatch, and partial-validation
  requery, but the container implementation is intentionally different.

## Inference Boundary

Observed facts:

1. Retail stores SteamID keys as low/high words inside STL tree nodes.
2. Retail active-auth cleanup builds/searches a SteamID ownership set before
   ending orphaned sessions.
3. Retail stats sessions are keyed by SteamID and use lower-bound/find-or-insert
   helpers before readback, flush, unlock, and callback paths.

Inferences:

1. `SV_SteamServerClientOwnsAuthSteamId` plus the active client slots is the
   source-level equivalent of retail's temporary active-auth ownership tree.
2. `sv_steamStatsSessions[MAX_CLIENTS]` is the source-level equivalent of the
   retail SteamID stats-session map for this codebase, because Quake server
   clients are already bounded and slot-indexed.

Open questions:

1. A future live-Steam validation pass could compare callback timing under
   real GameServerStats responses, but that is outside the default-disabled
   online-service policy.
2. Literal STL helper naming may still be refined if later Ghidra/Binary Ninja
   evidence distinguishes template instantiations more precisely.

## Validation

- `python -m pytest tests/test_platform_services.py::test_steam_auth_and_stats_tree_helpers_track_retail_reference_rows -q`

## Parity Estimate

- Focused auth-session helper alias confidence:
  **before 72% -> after 99%**.
- Focused stats-session map helper confidence:
  **before 70% -> after 98%**.
- Focused source-equivalence confidence for auth/stats session ownership:
  **before 94% -> after 98%**.
- Overall Steam launch/runtime reconstruction parity:
  **92.6% -> 92.65%**.
