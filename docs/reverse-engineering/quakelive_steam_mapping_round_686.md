# Quake Live Steam Mapping Round 686: ZMQ RCON Broadcast Send-Flag Boundary

Date: 2026-06-16

## Scope

This pass rechecked the retained RCON broadcast path where retail Quake Live
uses CZMQ string send helpers for ROUTER replies. Retail sends each peer
identity with `zstr_sendm` and the console payload with `zstr_send`. SRP keeps
CZMQ out of writable source, so `idZMQ_BroadcastRconOutput` expresses that
same boundary through explicit `zmq_send` flags.

Focused parity estimate: **before 92% -> after 98%** for RCON broadcast
send-flag source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **99.15% -> 99.2%**. Repo-wide parity remains **99%**
because this pass names a local send-flag boundary without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Walks retained RCON peers, sends identity and payload frames, and erases peers when the identity send fails. |
| `sub_4F5C10` | `s_send_string` | High | Lower CZMQ string send helper that receives the final `more` argument. |
| `sub_4F5D60` | `zstr_send` | High | Calls `s_send_string` with final-send/no-more semantics. |
| `sub_4F5D90` | `zstr_sendm` | High | Calls `s_send_string` with multipart/more semantics. |

Observed Binary Ninja HLIL anchors:

- `004f4d78` sends the RCON peer identity frame through `zstr_sendm`.
- `004f4daa` sends the RCON payload frame through `zstr_send`.
- `004f5d80` routes `zstr_send` into the lower helper with the final-send
  argument.
- `004f5da7` routes `zstr_sendm` into the lower helper with the multipart
  argument.

Observed fact: the multipart/final frame split is Quake Live-owned RCON wiring
behavior, but the helper implementations are embedded CZMQ/libzmq dependency
evidence. SRP should preserve the split through the existing dynamic
`zmq_send` runtime path instead of reconstructing helper source.

Inference: the identity frame send should stay nonblocking and multipart, while
the payload frame send should stay nonblocking and final. Naming those
composite flags makes the retained ROUTER source shape auditable without
vendoring `zstr_sendm`, `zstr_send`, or `s_send_string`.

## Source Reconstruction

This RCON broadcast send-flag boundary is now named in source:

- `QL_ZMQ_SEND_DONTWAIT`
- `QL_ZMQ_SEND_MORE_DONTWAIT`

The retained source boundary is:

- `idZMQ_BroadcastRconOutput` sends the peer identity with
  `QL_ZMQ_SEND_MORE_DONTWAIT`, matching the retail `zstr_sendm`
  multipart identity-frame send.
- `idZMQ_BroadcastRconOutput` sends the console payload with
  `QL_ZMQ_SEND_DONTWAIT`, matching the retail `zstr_send` final payload-frame
  send.
- The disconnect/erase branch remains tied only to identity-send failure; the
  payload send stays after the successful multipart identity frame.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zstr_send`, `zstr_sendm`, `s_send_string`, or lower libzmq source bodies to
the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_broadcast_send_flag_boundary_round_686 --tb=short`
  - `1 passed, 228 deselected in 0.23s`
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - `82 passed, 147 deselected in 2.10s`
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - `2 passed, 1 skipped in 0.22s`
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
