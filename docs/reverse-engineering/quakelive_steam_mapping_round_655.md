# quakelive_steam.exe Mapping Round 655

Date: 2026-06-15

Scope: focused ZMQ RCON peer-tree iterator and rebalance helper mapping. This
round documents the portable tree/list boundary in `src/code/server/sv_zmq.c`;
it does not reconstruct MSVC `std::tree` internals and does not reconstruct or
vendor libzmq/CZMQ implementation source.

## Summary

Retail stores retained RCON ROUTER identities in a C++ `std::tree`-shaped
container inside the `idZMQ` object. Around the Quake Live-owned peer helpers,
Binary Ninja HLIL shows a cluster of compiler/library helpers for rightmost,
leftmost, next, previous, rotate, lower-bound, and insert-rebalance behavior.

SRP intentionally keeps a portable tree/list representation instead of
recreating the retail MSVC container ABI. This round pins that boundary:
retail `std_tree_*_zmq_rcon_peer_node` aliases are evidence for source shape
and ownership, while the writable source remains at the Quake Live-owned
behavioral level with `idZMQ_FindRconPeer`, `idZMQ_InsertRconPeer`,
`idZMQ_EraseRconPeer`, and the in-order `prev`/`next` chain.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3E30` | `std_tree_rightmost_zmq_rcon_peer_node` | High | Walks right links until the header/sentinel marker is reached. |
| `sub_4F3E50` | `std_tree_leftmost_zmq_rcon_peer_node` | High | Walks left links until the header/sentinel marker is reached. |
| `sub_4F3E70` | `std_tree_next_zmq_rcon_peer_node` | High | Advances a tree iterator to the next in-order node. |
| `sub_4F3EC0` | `std_tree_prev_zmq_rcon_peer_node` | High | Moves a tree iterator to the previous in-order node. |
| `sub_4F4150` | `std_tree_rotate_right_zmq_rcon_peer_node` | High | Performs right rotation during tree erase/rebalance. |
| `sub_4F41B0` | `std_tree_lower_bound_zmq_rcon_peer_node` | High | Finds the first retained identity node that is not less than the requested key. |
| `sub_4F43B0` | `std_tree_rotate_left_zmq_rcon_peer_node` | High | Performs left rotation during tree erase/rebalance. |
| `sub_4F4410` | `std_tree_insert_zmq_rcon_peer_node_rebalance` | High | Inserts and rebalances a peer-node entry while updating tree count and extremal nodes. |

## Observed Facts

- `sub_4F3E30` and `sub_4F3E50` walk right/left child links until the sentinel
  byte at `+0x11` marks the end of the tree.
- `sub_4F3E70` and `sub_4F3EC0` are iterator next/previous helpers used by
  erase and insert paths.
- `sub_4F41B0` compares retained identity strings and returns the lower-bound
  node used by `sub_4F4910`.
- `sub_4F4410` increments the tree count, attaches the new node, and performs
  red/black-style rotation and recolor steps before returning the inserted
  node.
- `sub_4F46B0`, `sub_4F49C0`, and `sub_4F4FE0` call these helpers as
  container support; they are not libzmq or CZMQ implementation code.

Observed fact: these symbols are MSVC container scaffolding around the retained
Quake Live peer table, not independent networking/runtime behavior.

Inferred source boundary: SRP should preserve the behavioral peer-table owner
and iteration semantics without adding a vendored or ABI-faithful `std::tree`
implementation to source.

## Source Boundary

`src/code/server/sv_zmq.c` currently represents this boundary as:

- The portable tree/list boundary does not reconstruct MSVC std::tree internals.

- `idZMQ_FindRconPeer` performs exact identity lookup with `strcmp`.
- `idZMQ_InsertRconPeer` walks the portable tree, records predecessor and
  successor peers, and calls `idZMQ_LinkRconPeerInOrder`.
- `idZMQ_LinkRconPeerInOrder` keeps the in-order `prev`/`next` chain and
  updates `s_zmq.rconPeers` / `s_zmq.rconPeerLast`, replacing retail's
  header-sentinel extremal-node bookkeeping.
- `idZMQ_LeftmostRconPeer` provides the source-level successor helper used
  when erasing a node with two children.
- `idZMQ_EraseRconPeerRange` uses the portable in-order `next` chain for
  narrowed range erasure and keeps the retail full-range fast path separate.

This is a deliberate portable tree/list boundary. It does not reconstruct MSVC
std::tree internals, and it does not reconstruct embedded libzmq/CZMQ
internals.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_peer_tree_iterator_boundary_round_655`
  - `1 passed, 200 deselected`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `59 passed, 142 deselected`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped`

## Parity Estimate

- Focused ZMQ RCON peer iterator/container-boundary confidence:
  **before 93% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.9% -> after 97.0%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ mapping/source-boundary gap without changing the strict-retail Windows
  replacement score.
