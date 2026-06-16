# Quake Live Steam Mapping Round 732: ZMQ RCVMORE Getsockopt Success Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ RCVMORE getsockopt success boundary in SRP's
retained server-owned `idZMQ` receive wiring. Retail Quake Live compiled
libzmq/CZMQ code into `quakelive_steam.exe`, but SRP keeps libzmq as an
external runtime dependency and reconstructs only the Quake Live-owned
integration code.

This is the ZMQ RCVMORE getsockopt success boundary for the SRP dynamic zmq_getsockopt adaptation.

Focused parity estimate: **before 94% -> after 99%** for focused RCVMORE
getsockopt source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.8% -> 99.82%**. Repo-wide parity
remains **99%** because this pass names a local SRP dynamic `zmq_getsockopt`
adaptation boundary without changing the strict-retail Windows replacement
score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4013D0` | `zmq_getsockopt` | High | Lower embedded libzmq option getter wrapper. |
| `sub_4F58F0` | `zsock_rcvmore` | High | CZMQ helper that queries `ZMQ_RCVMORE` and returns the resulting integer. |
| `sub_4F5CB0` | `zstr_recv` | High | Retail CZMQ string receive helper used by the retained receive path. |

Observed Binary Ninja HLIL anchors:

- `004f58f0` starts the promoted `zsock_rcvmore` helper.
- `004f5904` initializes the local option-length value to `4`.
- `004f5914` calls `zmq_getsockopt` through `sub_4013d0` with option `0xd`.
- `004f5922` returns the resulting multipart indicator.
- `004f5cb0` remains the adjacent CZMQ string receive helper boundary.

Observed fact: retail's CZMQ helper asks the embedded libzmq getter for
`ZMQ_RCVMORE` and returns the option value. SRP does not carry the CZMQ helper
source; it reads into stack buffers through dynamic `zmq_recv`, then probes
`ZMQ_RCVMORE` through the optional dynamic `zmq_getsockopt` export.

Inference: SRP's direct receive helper should name the `zmq_getsockopt`
success result and compare the returned multipart state against the existing
`QL_ZMQ_RCVMORE_NONE` boundary instead of spelling a raw zero-success plus
truthy-value check at the receive site.

## Source Reconstruction

`QL_ZMQ_GETSOCKOPT_SUCCESS` now names the local getter success result used by
SRP's direct `zmq_getsockopt` dispatch path.

`idZMQ_ReadFrameString` initializes the local multipart state to
`QL_ZMQ_RCVMORE_NONE`, probes `QL_ZMQ_RCVMORE`, and sets the caller's `more`
flag only when `zmq_getsockopt` returns `QL_ZMQ_GETSOCKOPT_SUCCESS` and the
option value differs from `QL_ZMQ_RCVMORE_NONE`.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcvmore_getsockopt_success_round_732 --tb=short`
  - Result: `1 passed, 270 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - Result: `95 passed, 176 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - Result: `2 passed, 1 skipped`; generated report includes
    `rcvmore_getsockopt_success_present: true`.
- `rg --files src/libs/libzmq`
  - Result: only `src/libs/libzmq\README.md`; no reconstructed libzmq/CZMQ
    source is present in the repo.
- `git diff --check`
  - Result: passed; Git reported only the existing LF-to-CRLF working-copy
    warnings.

No game launch was needed; this was a static mapping/source-boundary pass
covered by corpus anchors and source parity gates.
