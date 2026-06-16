# Quake Live Steam Mapping Round 726: ZMQ Send Success-Threshold Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ send success-threshold boundary in SRP's retained
server-owned `idZMQ` wiring. Retail Quake Live compiled libzmq/CZMQ code into
`quakelive_steam.exe`, but SRP intentionally keeps libzmq as an external
runtime dependency and reconstructs only the Quake Live-owned integration code.

Focused parity estimate: **before 94% -> after 99%** for focused ZMQ send
success-threshold source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.6% -> 99.65%**. Repo-wide parity
remains **99%** because this pass names a local SRP dynamic `zmq_send`
adaptation boundary without changing the strict-retail Windows replacement
score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Broadcasts RCON output to retained ROUTER peers. |
| `sub_4F5C10` | `s_send_string` | High | CZMQ string-send helper body retained inside the retail executable. |
| `sub_4F5D60` | `zstr_send` | High | CZMQ single-frame string send wrapper. |
| `sub_4F5D90` | `zstr_sendm` | High | CZMQ multipart string send wrapper. |

Observed Binary Ninja HLIL anchors:

- `004f4d40` starts the retail RCON broadcast helper.
- `004f4d78` branches on `zstr_sendm` success using a signed non-negative
  comparison.
- `004f4daa` sends the payload frame through `zstr_send` only after the
  identity-frame success branch.
- `004f5d80` routes `zstr_send` to the lower string-send helper with a final
  frame flag.
- `004f5da7` routes `zstr_sendm` to the lower string-send helper with a
  multipart frame flag.

Observed fact: retail's CZMQ helper layer treats negative send results as
failure and non-negative results as success. SRP does not carry that helper
source; it calls the dynamic libzmq `zmq_send` export directly through the
retained `idZMQ` server integration.

Inference: the SRP dynamic zmq_send adaptation should name the same
non-negative success threshold at the integration boundary, while keeping the
embedded retail CZMQ helper bodies as evidence only.

## Source Reconstruction

`QL_ZMQ_SEND_SUCCESS_MIN` now names the local send-success threshold used by
SRP's direct `zmq_send` dispatch path.

`idZMQ_SendAuthResponse` uses this constant for each manual ZAP response frame
gate before emitting the final empty frame. `idZMQ_BroadcastRconOutput` uses
the same constant for the ROUTER identity-frame send before deciding whether a
peer disconnected or should receive the payload frame.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_send_success_threshold_round_726 --tb=short`
  - `1 passed, 264 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - `91 passed, 174 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - `2 passed, 1 skipped`.
- `rg --files src/libs/libzmq`
  - only `src/libs/libzmq\README.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
