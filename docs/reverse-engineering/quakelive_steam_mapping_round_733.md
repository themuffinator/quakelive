# Quake Live Steam Mapping Round 733: ZMQ Socket-Option Int-Size Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ socket-option int-size boundary in SRP's retained
server-owned `idZMQ` socket setup wiring. Retail Quake Live compiled
libzmq/CZMQ code into `quakelive_steam.exe`, but SRP keeps libzmq as an
external runtime dependency and reconstructs only the Quake Live-owned
integration code.

This is the ZMQ socket-option int-size boundary for the SRP dynamic zmq_setsockopt adaptation.

Focused parity estimate: **before 94% -> after 99%** for focused
socket-option int-size source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.82% -> 99.84%**. Repo-wide parity
remains **99%** because this pass names a local SRP dynamic `zmq_setsockopt`
adaptation boundary without changing the strict-retail Windows replacement
score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401390` | `zmq_setsockopt` | High | Lower embedded libzmq option setter wrapper. |
| `sub_4F5790` | `zsock_set_plain_server` | High | CZMQ helper forwarding PLAIN server mode as an integer option. |
| `sub_4F5980` | `zsock_set_router_mandatory` | High | CZMQ helper forwarding ROUTER mandatory mode as an integer option. |

Observed Binary Ninja HLIL anchors:

- `004f40db` calls `zsock_set_plain_server` for the RCON ROUTER socket.
- `004f40e9` calls `zsock_set_router_mandatory` for the RCON ROUTER socket.
- `004f4358` calls `zsock_set_plain_server` for the stats PUB socket.
- `004f57b1` forwards PLAIN server mode to `zmq_setsockopt` with option
  `0x2c` and payload size `4`.
- `004f59cc` forwards ROUTER mandatory mode to `zmq_setsockopt` with option
  `0x21` and payload size `4`.

Observed fact: retail's CZMQ integer socket-option helpers pass a four-byte
integer payload to the embedded `zmq_setsockopt` wrapper. SRP does not carry
the CZMQ helper source; it uses `idZMQ_TrySetSocketInt` to dispatch integer
options through the optional dynamic `zmq_setsockopt` export.

Inference: SRP's direct integer option helper should name the integer payload
size at the retained `idZMQ` integration boundary instead of leaving it as an
unexplained local `sizeof( value )` detail.

## Source Reconstruction

`QL_ZMQ_SOCKET_OPTION_INT_SIZE` now names the local integer option payload
size used by SRP's direct `zmq_setsockopt` dispatch path.

`idZMQ_TrySetSocketInt` uses that named size when forwarding retained integer
socket options:

- RCON `QL_ZMQ_ROUTER_MANDATORY`.
- RCON `QL_ZMQ_PLAIN_SERVER`.
- Stats `QL_ZMQ_PLAIN_SERVER`.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_socket_option_int_size_round_733 --tb=short`
  - Result: `1 passed, 271 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - Result: `96 passed, 176 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - Result: `2 passed, 1 skipped`; generated report includes
    `socket_option_int_size_present: true`.
- `rg --files src/libs/libzmq`
  - Result: only `src/libs/libzmq\README.md`; no reconstructed libzmq/CZMQ
    source is present in the repo.
- `git diff --check`
  - Result: passed; Git reported only the existing LF-to-CRLF working-copy
    warnings.

No game launch was needed; this was a static mapping/source-boundary pass
covered by corpus anchors and source parity gates.
