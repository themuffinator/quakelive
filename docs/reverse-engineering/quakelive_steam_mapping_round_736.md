# Quake Live Steam Mapping Round 736: ZMQ Socket Close-Slot Clear Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ socket close-slot clear boundary in SRP's retained
server-owned `idZMQ` shutdown wiring. Retail Quake Live compiled libzmq/CZMQ
code into `quakelive_steam.exe`, but SRP keeps libzmq as an external runtime
dependency and reconstructs only the Quake Live-owned integration code.

This is the ZMQ socket close-slot clear boundary for the SRP dynamic zmq_close adaptation.

Focused parity estimate: **before 94% -> after 99%** for focused socket
close-slot clear source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.86% -> 99.88%**. Repo-wide parity
remains **99%** because this pass names a local SRP dynamic `zmq_close`
adaptation boundary without changing the strict-retail Windows replacement
score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4012F0` | `zmq_close` | High | Lower embedded libzmq socket close wrapper. |
| `sub_4F5190` | `zsock_destroy_checked` | High | CZMQ checked zsock destructor that owns the pointer slot. |
| `sub_4F6AA0` | `zsys_close` | High | CZMQ socket close owner that dispatches to `zmq_close`. |

Observed Binary Ninja HLIL anchors:

- `004f5190` starts the promoted `zsock_destroy_checked` helper.
- `004f5198` reads the caller-owned zsock pointer slot.
- `004f519c` skips destruction when the slot is already empty.
- `004f51ab` stamps the wrapper with `0xdeadbeef`.
- `004f51b1` calls `zsys_close`.
- `004f51ce` clears the caller-owned slot with `*arg1 = 0`.
- `004f6aa0` starts the promoted `zsys_close` helper.
- `004f6b09` dispatches to the embedded `zmq_close` wrapper.

Observed fact: retail's CZMQ checked destructor owns both the close operation
and the caller-slot clear. SRP does not carry the CZMQ helper source; it closes
dynamic sockets through `idZMQ_CloseSocket`, then clears the caller-owned
socket pointer.

Inference: SRP's direct socket close helper should name the empty socket-slot
state at the retained `idZMQ` integration boundary instead of spelling raw
`NULL` at the pointer-slot clear site.

## Source Reconstruction

`QL_ZMQ_SOCKET_SLOT_EMPTY` now names the local empty state used by SRP's
direct `zmq_close` dispatch path.

`idZMQ_CloseSocket` keeps the dynamic close ordering intact:

- If the slot and dynamic `zmq_close` export are present, close the socket.
- Clear the caller-owned slot to `QL_ZMQ_SOCKET_SLOT_EMPTY`.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_socket_close_slot_clear_round_736 --tb=short`
  - Result: `1 passed, 274 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - Result: `98 passed, 177 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - Result: `2 passed, 1 skipped`; generated report includes
    `socket_close_slot_clear_present: true`.
- `rg --files src/libs/libzmq`
  - Result: only `src/libs/libzmq\README.md`; no reconstructed libzmq/CZMQ
    source is present in the repo.
- `git diff --check`
  - Result: passed; Git reported only the existing LF-to-CRLF working-copy
    warnings.

No game launch was needed; this was a static mapping/source-boundary pass
covered by corpus anchors and source parity gates.
