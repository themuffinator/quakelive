# Quake Live Steam Mapping Round 724: ZMQ RCON Peer-Count Floor Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ RCON peer-count floor boundary in SRP's retained
server-owned `idZMQ` wiring. Retail Quake Live keeps a count field inside the
RCON peer tree container, increments it on insert, decrements it only when the
count is non-zero during single-node erase, and resets it to zero on full peer
table clear.

Focused parity estimate: **before 94% -> after 99%** for RCON peer-count floor
source-boundary confidence. Focused ZMQ wiring/source reconstruction confidence
moves from **99.55% -> 99.6%**. Repo-wide parity remains **99%** because this
pass names a local portable peer-table count boundary without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F46B0` | `idZMQ_EraseRconPeer` | High | Single-node peer erase; decrements the retained count only when non-zero. |
| `sub_4F49C0` | `idZMQ_InsertRconPeer` | High | Inserts a newly observed RCON peer identity. |
| `sub_4F4E80` | `idZMQ_ClearRconPeers` | High | Full peer-table clear that resets the retained count. |
| `sub_4F4FE0` | `idZMQ_EraseRconPeerRange` | High | Range erase helper that delegates full-range erasure to the clear helper. |

Observed Binary Ninja HLIL anchors:

- `004f46b0` starts the single-node RCON peer erase helper.
- `004f48e7` reads the peer-table count from `arg1 + 8` after deleting the
  selected node.
- `004f48f2` checks that the count is non-zero.
- `004f48f5` writes `count - 1` only through that non-zero branch.
- `004f4e80` starts the full peer-table clear helper.
- `004f4ec2` resets the retained count field to zero.
- `004f4fe0` starts the range erase helper.
- `004f4ff6` detects the full-range erase case.
- `004f4ffa` delegates that full-range case to the clear helper.

Observed fact: these count transitions are part of the Quake Live `idZMQ`
RCON peer container behavior. The retail implementation uses MSVC tree support
helpers around this container, but those helpers are evidence and not source to
reconstruct in SRP.

Inference: SRP's portable peer-table count floor should be named separately
from both the embedded CZMQ/libzmq runtime and the retail MSVC `std::tree`
container internals.

## Source Reconstruction

`QL_ZMQ_RCON_PEER_COUNT_EMPTY` now names the SRP portable peer-table count floor.

`idZMQ_EraseRconPeer` uses that constant for the non-empty decrement guard, and
`idZMQ_EraseRconPeerRange` uses it when resetting the count during full-range
clear. The existing insert/decrement operations remain unchanged:

- `idZMQ_InsertRconPeer` still increments `s_zmq.rconPeerCount` after linking a
  newly allocated peer.
- `idZMQ_EraseRconPeer` still decrements exactly one peer after unlinking and
  transplanting the erased node.
- `idZMQ_ClearRconPeers` still routes through
  `idZMQ_EraseRconPeerRange( s_zmq.rconPeers, NULL )`.

This pass does not reconstruct libzmq/CZMQ internals and does not reconstruct MSVC std::tree internals. SRP keeps the portable tree/list implementation while
pinning the observed Quake Live-owned peer-count behavior.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_peer_count_floor_round_724 --tb=short` - 1 passed, 262 deselected.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short` - 90 passed, 173 deselected.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short` - 2 passed, 1 skipped.
- `rg --files src/libs/libzmq` - only `src/libs/libzmq\README.md`.
- `git diff --check` - passed with pre-existing LF-to-CRLF warnings.
