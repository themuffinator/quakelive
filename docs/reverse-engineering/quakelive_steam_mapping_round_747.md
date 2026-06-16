# Quake Live Steam Mapping Round 747: ZMQ RCON peer-table slot-clear boundary

Date: 2026-06-16

## Scope

This round pins the retained RCON peer-table slot-clear boundary in SRP's
external ZMQ runtime adaptation. Retail Quake Live embeds libzmq/CZMQ and uses
MSVC `std::tree` internals around the `idZMQ` RCON peer table. SRP keeps the
Quake Live-owned `idZMQ` behavior but represents the peer table with portable
source-owned structures. This pass names the empty peer-table slots and pins
the full-range clear path.

Focused RCON peer-table slot-clear confidence: **before 94% -> after 99%**.

Focused ZMQ wiring/source reconstruction confidence: **99.96% -> 99.97%**.

Repo-wide parity remains **99%** because this pass documents an SRP portable
peer-table slot adaptation without reconstructing libzmq/CZMQ internals, MSVC
`std::tree` internals, or changing the strict-retail Windows replacement score.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_4F46B0` | `idZMQ_EraseRconPeer` | Retail peer erase path that decrements the retained peer count. |
| `sub_4F49C0` | `idZMQ_InsertRconPeer` | Retail peer insert path that grows the retained peer table. |
| `sub_4F4E80` | `idZMQ_ClearRconPeers` | Retail peer-table clear helper. |
| `sub_4F4FE0` | `idZMQ_EraseRconPeerRange` | Retail range erase path that delegates full-range clears. |
| `sub_4F5080` | `idZMQ_Destroy` | Retail destroy path that clears retained RCON peers. |

Primary HLIL anchors:

```text
004f46b0    int32_t* __thiscall sub_4f46b0(void* arg1, int32_t* arg2, int32_t* arg3)
004f48e7  int32_t eax_13 = *(arg1 + 8)
004f48f2  if (eax_13 != 0)
004f48f5      *(arg1 + 8) = eax_13 - 1
004f4e80    void* __fastcall sub_4f4e80(void* arg1)
004f4ec2  *(arg1 + 8) = 0
004f4fe0    int32_t* __thiscall sub_4f4fe0(void* arg1, int32_t* arg2, int32_t* arg3, int32_t arg4)
004f4ff6  if (i == *eax && arg4 == eax)
004f4ffa      sub_4f4e80(arg1)
004f5080    struct idZMQ::VTable** __thiscall sub_4f5080
004f50c9  sub_4f4fe0(&arg1[5], &var_18, *eax_3, eax_3)
```

Observed facts:

- Retail decrements the peer count when erasing one RCON peer.
- Retail clears the peer count to zero in the full table clear helper.
- Retail range erase delegates to the clear helper when the requested range
  covers the container endpoints.
- Retail `idZMQ_Destroy` clears the retained RCON peer table.

Inference:

- SRP's portable peer table should name its empty list, root, last, and count
  slots explicitly at the retained `idZMQ` boundary.
- SRP should not reconstruct MSVC `std::tree` internals or embed libzmq/CZMQ
  source to represent this retained peer-table lifecycle.

## Reconstruction

`sv_zmq.c` names the retained peer-table empty slots with
`QL_ZMQ_RCON_PEER_SLOT_EMPTY` and `QL_ZMQ_RCON_PEER_COUNT_EMPTY`. The full
range clear path frees the retained subtree, clears `s_zmq.rconPeers`,
`s_zmq.rconPeerRoot`, and `s_zmq.rconPeerLast`, then resets
`s_zmq.rconPeerCount`.

The retained destroy path continues to call `idZMQ_ClearRconPeers`, while
runtime shutdown does not duplicate that peer-table clear. Single peer insert
and erase still adjust the retained peer count through the portable table.

This is an SRP portable peer-table slot adaptation. It does not reconstruct
libzmq/CZMQ internals and does not reconstruct MSVC std::tree internals.

This pass does not reconstruct libzmq/CZMQ internals.
This pass does not reconstruct MSVC std::tree internals.

## Validation

Completed validation:

- `python -m pytest -q tests/test_platform_services.py -k "steam_browser_ping_response_filtered_completion_round_748 or zmq_rcon_peer_table_slot_clear_round_747" --tb=short`
  - `2 passed, 284 deselected in 0.18s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `286 passed in 16.68s`
- `git diff --check`
  - Passed; Git reported existing LF-to-CRLF working-copy warnings only.
