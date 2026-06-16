# Quake Live Steam Mapping Round 728: ZMQ Frame-Read Failure Threshold Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ frame-read failure threshold in SRP's retained
server-owned `idZMQ` wiring. Retail Quake Live compiled libzmq/CZMQ code into
`quakelive_steam.exe`, but SRP keeps libzmq as an external runtime dependency
and reconstructs only the Quake Live-owned integration code.

This is the ZMQ frame-read failure threshold boundary for the SRP dynamic zmq_recv adaptation and stack-buffer receive path.

Focused parity estimate: **before 94% -> after 99%** for focused ZMQ
frame-read failure threshold source-boundary confidence. Focused ZMQ
wiring/source reconstruction confidence moves from **99.7% -> 99.75%**.
Repo-wide parity remains **99%** because this pass reuses the named SRP
dynamic `zmq_recv` adaptation boundary without changing the strict-retail
Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Receives RCON identity and command frames after poll readiness. |
| `sub_4F5CB0` | `zstr_recv` | High | CZMQ string receive helper embedded in the retail executable. |
| `sub_4F5E10` | `zstr_free` | High | CZMQ string release helper used after RCON frame processing. |
| `sub_401520` | `zmq_msg_recv` | High | Lower message receive wrapper used by retail `zstr_recv`. |

Observed Binary Ninja HLIL anchors:

- `004f4f23` receives the first RCON frame through `zstr_recv`.
- `004f4f2f` receives the second RCON frame through `zstr_recv`.
- `004f4f91` releases the second received string through `zstr_free` on the
  new-peer path.
- `004f4fab` and `004f4fb7` release both received strings on the command
  dispatch path.
- `004f5ce6` treats a negative `zmq_msg_recv` result as a receive failure
  inside the embedded retail CZMQ helper.

Observed fact: retail frame receive failure is represented by a negative
receive result in the embedded CZMQ receive path. SRP does not carry that CZMQ
source; it calls the dynamic libzmq `zmq_recv` export directly and preserves
the same signed failure boundary in the retained `idZMQ` integration.

Inference: all SRP stack-buffer frame-read failure checks should route through
the existing `QL_ZMQ_FRAME_READ_SUCCESS_MIN` boundary instead of spelling raw
negative receive checks at each call site.

## Source Reconstruction

`QL_ZMQ_FRAME_READ_SUCCESS_MIN` now gates all retained SRP frame-read failure
paths:

- `idZMQ_ReadFrameString` checks the direct `zmq_recv` result against the
  named success minimum.
- `idZMQ_DrainRemainingFrames` stops draining when a stack-buffer frame read
  falls below the same boundary.
- `idZMQ_PumpAuthSocket` uses the same boundary for each manual ZAP frame read.
- `idZMQ_ReadRconCommand` already used the boundary for the command-frame
  drain decision and remains unchanged.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_frame_read_failure_threshold_round_728 --tb=short`
  - `1 passed, 267 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - `93 passed, 174 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - `2 passed, 1 skipped`.
- `rg --files src/libs/libzmq`
  - only `src/libs/libzmq\README.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
