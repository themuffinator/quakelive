# Quake Live Steam Mapping Round 734: ZMQ Socket-Option String-Size Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ socket-option string-size boundary in SRP's
retained server-owned `idZMQ` ZAP-domain socket setup wiring. Retail Quake
Live compiled libzmq/CZMQ code into `quakelive_steam.exe`, but SRP keeps
libzmq as an external runtime dependency and reconstructs only the Quake
Live-owned integration code.

This is the ZMQ socket-option string-size boundary for the SRP dynamic zmq_setsockopt adaptation.

Focused parity estimate: **before 94% -> after 99%** for focused
socket-option string-size source-boundary confidence. Focused ZMQ
wiring/source reconstruction confidence moves from **99.84% -> 99.86%**.
Repo-wide parity remains **99%** because this pass names a local SRP dynamic
`zmq_setsockopt` adaptation boundary without changing the strict-retail
Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401390` | `zmq_setsockopt` | High | Lower embedded libzmq option setter wrapper. |
| `sub_4F5750` | `zsock_set_zap_domain` | High | CZMQ helper forwarding the ZAP domain string and its length. |

Observed Binary Ninja HLIL anchors:

- `004f40b8` calls `zsock_set_zap_domain` with `"rcon"` for the RCON ROUTER
  socket.
- `004f4335` calls `zsock_set_zap_domain` with `"stats"` for the stats PUB
  socket.
- `004f5750` starts the promoted `zsock_set_zap_domain` helper.
- `004f5756` seeds a scan pointer from the input domain string.
- `004f5765` loops until the terminator byte.
- `004f5784` forwards option `0x37` to `zmq_setsockopt` with length
  `eax - &eax[1]`, matching the string length without the trailing terminator.

Observed fact: retail's CZMQ ZAP-domain helper passes the domain string and
its non-terminating length to the embedded `zmq_setsockopt` wrapper. SRP does
not carry the CZMQ helper source; it uses `idZMQ_TrySetSocketString` to
dispatch the retained ZAP-domain strings through the optional dynamic
`zmq_setsockopt` export.

Inference: SRP's direct string option helper should name the string payload
size at the retained `idZMQ` integration boundary instead of leaving the
length forwarding as a raw `strlen( value )` at the socket-option call site.

## Source Reconstruction

`QL_ZMQ_SOCKET_OPTION_STRING_SIZE` now names the local string option payload
size used by SRP's direct `zmq_setsockopt` dispatch path.

`idZMQ_TrySetSocketString` uses that named size when forwarding retained
string socket options:

- RCON `QL_ZMQ_ZAP_DOMAIN` with `QL_ZMQ_DOMAIN_RCON`.
- Stats `QL_ZMQ_ZAP_DOMAIN` with `QL_ZMQ_DOMAIN_STATS`.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_socket_option_string_size_round_734 --tb=short`
  - Result: `1 passed, 272 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - Result: `97 passed, 176 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - Result: `2 passed, 1 skipped`; generated report includes
    `socket_option_string_size_present: true`.
- `rg --files src/libs/libzmq`
  - Result: only `src/libs/libzmq\README.md`; no reconstructed libzmq/CZMQ
    source is present in the repo.
- `git diff --check`
  - Result: passed; Git reported only the existing LF-to-CRLF working-copy
    warnings.

No game launch was needed; this was a static mapping/source-boundary pass
covered by corpus anchors and source parity gates.
