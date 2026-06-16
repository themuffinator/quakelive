# Quake Live ZMQ Mapping Round 638: RCON Peer Helper Source Shape

Date: 2026-06-15

## Scope

This round tightens the retained `idZMQ` RCON peer-table reconstruction in
`src/code/server/sv_zmq.c`. Earlier rounds had mapped the retail helpers, but
the writable source still inlined peer allocation inside insertion and used a
single full-clear helper. This pass adds a portable source analogue for `sub_4F4640`
and makes the range-erasure seam from `sub_4F4FE0` explicit.

No live ZMQ transport is enabled by this pass. The runtime remains behind
`QL_BUILD_ONLINE_SERVICES` through the existing `QL_PLATFORM_HAS_ONLINE_SERVICES`
policy guard.

## Retail Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  identifies the owning binary as `quakelive_steam.exe` with 5,473 functions,
  351 imports, and 2 exports.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records the peer-table helper rows:

| symbol | alias | size | evidence |
|---|---|---:|---|
| `sub_4F4640` | `std_tree_create_zmq_rcon_peer_node` | 104 | Allocates a 0x14-byte MSVC tree node, links it to the header sentinel, and stores the peer key pointer. |
| `sub_4F46B0` | `idZMQ_EraseRconPeer` | 592 | Single-node erasure helper used by failed RCON-output sends and narrowed range erasure. |
| `sub_4F4910` | `idZMQ_FindRconPeer` | 112 | Exact-match lookup for received RCON peer identities. |
| `sub_4F4980` | `idZMQ_FreeRconPeerSubtree` | 56 | Recursive subtree free used by the full clear path. |
| `sub_4F49C0` | `idZMQ_InsertRconPeer` | 341 | Inserts a new peer node after lookup has identified an absent key. |
| `sub_4F4E80` | `idZMQ_ClearRconPeers` | 77 | Full table clear that frees descendants and resets header/count state. |
| `sub_4F4FE0` | `idZMQ_EraseRconPeerRange` | 158 | Uses the retail full-range fast path or loops node-by-node through single erase. |

- `references/analysis/quakelive_symbol_aliases.json` already carries these
  promoted names, including the support-library `sub_4F4640` alias from Round
  362 and the retained object helpers re-pinned by Round 420.
- Binary Ninja HLIL in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
  shows:
  - `sub_4F4640` calls `operator new(0x14)`, writes the header pointer into
    node link fields, clears the state byte/word at `+0x10`, and stores the
    peer-key pointer at `+0x0c`.
  - `sub_4F4FE0` checks `i == *eax && arg4 == eax`, calls
    `sub_4F4E80(arg1)` for full-range erasure, otherwise iterates until
    `arg4` and calls `sub_4F46B0(arg1, &var_8, i_2)`.
  - `idZMQ_PumpRcon` still reaches insertion through
    `sub_4F49C0(..., sub_4F4640(...), nullptr)`, and broadcast failure still
    reaches single-node erase through `sub_4F46B0`.

Observed fact: retail separates peer node creation, single erase, full clear,
and range erase even though several helpers are mostly MSVC tree scaffolding.

Inferred source boundary: SRP should preserve the helper split at the
Quake Live-owned `idZMQ` level while retaining its portable tree/list
representation instead of recreating the embedded C++ container ABI.

## Source Reconstruction

`src/code/server/sv_zmq.c` now carries the helper split explicitly:

- `idZMQ_AllocRconPeer` owns peer allocation, zeroing, identity/label copying,
  and cached identity length setup. This is the portable source analogue for
  the retail `sub_4F4640` node creation seam.
- `idZMQ_InsertRconPeer` now calls `idZMQ_AllocRconPeer` after the duplicate
  lookup walk and before linking the peer into the retained tree/list.
- `idZMQ_EraseRconPeerRange` owns the retail full-range fast path by freeing
  the whole subtree and resetting the root, list head/tail, and count when
  clearing `s_zmq.rconPeers` through `NULL`.
- The same range helper owns narrowed erasure by walking `first` to `last` and
  forwarding each peer through `idZMQ_EraseRconPeer`.
- `idZMQ_ClearRconPeers` is now a thin wrapper over
  `idZMQ_EraseRconPeerRange( s_zmq.rconPeers, NULL )`.

Behavior is intentionally unchanged for the peer helpers themselves: failed
console-output sends still erase a single peer, explicit disabled-RCON cleanup
still clears the full table, and default builds still keep live ZMQ disabled
with the transcript fallback intact.

## Wiring

The retained wiring remains:

- `Zmq_PumpRcon` receives identity/command frames, looks up or inserts the peer,
  logs connect and command markers, and executes the command.
- `Zmq_BroadcastRconOutput` sends console output to retained peers and erases
  peers whose send path fails.
- Disabled RCON cleanup and the portable object-destroy analogue call through
  `idZMQ_ClearRconPeers`, now reaching the explicit range-erasure helper. A
  later shutdown-owner pass keeps that peer-table clear out of
  `Zmq_ShutdownRuntime`.

## Validation

Added `test_zmq_peer_table_source_shape_round_638_is_pinned`, covering:

- alias-map entries and Ghidra function rows for the seven peer-table helpers;
- HLIL anchors for `sub_4F4640` allocation/header-key storage and
  `sub_4F4FE0` full-range versus narrowed range behavior;
- source reconstruction of `idZMQ_AllocRconPeer`,
  `idZMQ_EraseRconPeerRange`, and the updated `idZMQ_InsertRconPeer` /
  `idZMQ_ClearRconPeers` call chain; and
- this mapping note's explicit source-boundary language.

No runtime launch was needed. This was a static reconstruction pass over
committed Ghidra/Binary Ninja evidence and source-shape tests.

## Parity Estimate

- Focused `idZMQ` RCON peer helper source-shape confidence:
  **before 95% -> after 97%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 94.2% -> after 94.4%**.
- Overall repo-wide parity remains **99%** because this closes a local
  source-shape freshness gap without changing the strict-retail Windows
  replacement score.
