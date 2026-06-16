# quakelive_steam.exe Mapping Round 654

Date: 2026-06-15

Scope: focused ZMQ runtime-shutdown versus peer-table destructor ownership
mapping for the retained `idZMQ` host. This round reconstructs Quake
Live-owned server wiring only; it does not reconstruct or vendor libzmq/CZMQ
implementation source.

## Summary

Retail keeps the runtime RCON/auth close path separate from the `idZMQ`
object/destructor peer-table cleanup. `sub_4F3DF0` clears the RCON socket slot,
clears the resolved RCON poll slot, and destroys the shared auth actor. The
peer table is instead cleared by the range-erasure/destructor path around
`sub_4F4E80`, `sub_4F4FE0`, and `sub_4F5080`.

This round updates SRP so runtime shutdown no longer clears the RCON peer
table. The portable `idZMQ_Destroy` analogue owns the peer-table clear through
the existing `idZMQ_ClearRconPeers` and `idZMQ_EraseRconPeerRange` helpers,
while `Zmq_ShutdownRuntime` stays aligned with the retail RCON/auth shutdown
owner.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | High | Checks the RCON socket slot, clears the resolved poll slot, destroys the RCON socket wrapper, then destroys the shared auth actor. |
| `sub_4F4E80` | `idZMQ_ClearRconPeers` | High | Full peer-table clear that frees the tree descendants and resets table/header state. |
| `sub_4F4FE0` | `idZMQ_EraseRconPeerRange` | High | Range erase helper; the full-range case delegates to `sub_4F4E80`. |
| `sub_4F5080` | `idZMQ_Destroy` | High | Destructor-shaped owner that resets the vtable, erases the peer table through `sub_4F4FE0`, and releases the backing tree header. |

## Observed Facts

- `sub_4F3DF0` checks `data_575708`, clears `data_57570c`, and calls
  `zsock_destroy_checked(&data_575708, "zmq\\id_zmq.cpp", 0xe2)`.
- `sub_4F3DF0` then checks `data_575700` and calls
  `zactor_destroy(&data_575700)`.
- There is no `sub_4F4E80` or `sub_4F4FE0` call inside `sub_4F3DF0`.
- `sub_4F4FE0` detects the full-range case and calls `sub_4F4E80`.
- `sub_4F5080` calls `sub_4F4FE0(&arg1[5], &var_18, *eax_3, eax_3)` from the
  destructor-shaped object cleanup path.

Observed fact: the retail peer-table clear is a destructor/range-erasure
concern, not a runtime socket/auth shutdown concern.

Inferred source boundary: SRP can represent that object cleanup with a portable
`idZMQ_Destroy` wrapper over the existing peer-clear helpers, but it should not
pull that peer-table clear back into `Zmq_ShutdownRuntime`. The missing C++
static object lifetime is a portability adaptation, not a reason to reconstruct
libzmq/CZMQ internals.

## Source Reconstruction

- Retail-aligned runtime shutdown no longer clears the RCON peer table; the
  destructor analogue owns the peer-table clear instead.
- Removed `idZMQ_ClearRconPeers()` from `Zmq_ShutdownRuntime`.
- Added a portable `idZMQ_Destroy()` analogue that owns the peer-table clear by
  calling `idZMQ_ClearRconPeers()`.
- Kept `idZMQ_ClearRconPeers()` as the thin full-table wrapper over
  `idZMQ_EraseRconPeerRange( s_zmq.rconPeers, NULL )`.
- Routed the disabled-RCON cleanup through `idZMQ_Destroy()` so local
  mode-disable cleanup still releases retained peer state without assigning it
  to the retail runtime shutdown owner.
- Preserved the external libzmq runtime boundary. `src/libs/libzmq/` remains a
  README-only runtime drop location; no libzmq/CZMQ source, import library, or
  header was added.

## Confidence And Open Questions

Confidence is high for the shutdown split because `sub_4F3DF0` is short and
adjacent to the already mapped stats shutdown helper, and the destructor path
has direct HLIL evidence through `sub_4F5080 -> sub_4F4FE0 -> sub_4F4E80`.
The only remaining adaptation is SRP's portable C representation: there is no
retail-style C++ global `idZMQ` object to destruct at process teardown, so the
portable `idZMQ_Destroy` helper is used only where SRP must explicitly clear
retained peer state.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_runtime_shutdown_skips_peer_clear_round_654`
  - `1 passed, 199 deselected`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `58 passed, 142 deselected`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped`

## Parity Estimate

- Focused ZMQ runtime-shutdown versus peer-table destructor confidence:
  **before 90% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.8% -> after 96.9%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ lifecycle source-shape gap without changing the strict-retail Windows
  replacement score.
