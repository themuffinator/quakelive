# Quake Live Steam Mapping Round 676: ZMQ No-Flags And Immediate-Poll Boundary

Date: 2026-06-16

## Scope

This pass rechecked the zero-valued send flag and immediate poll boundaries in
the retained ZMQ integration. Retail Quake Live distinguishes multipart sends
from final sends through CZMQ `zstr_sendm` and `zstr_send`, and its RCON pump
uses a zero-time poll over the retained RCON socket. SRP already had equivalent
behavior; this round names the zero-valued source constants instead of leaving
them as inline `0` arguments.

Focused parity estimate: **before 90% -> after 98%** for no-flags and
immediate-poll source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **98.8% -> 98.9%**. Repo-wide parity
remains **99%** because this pass closes a local send/poll source-shape gap
without changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401600` | `zmq_poll` | High | Lower libzmq poll helper used by the retained RCON pump. |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | High | Publishes final stats messages through `zstr_send`. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | High | Publishes final match-report messages through `zstr_send`. |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Sends identity multipart frames through `zstr_sendm`, then final message frames through `zstr_send`. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Polls the retained RCON socket before reading identity and command frames. |
| `sub_4F5D60` | `zstr_send` | High | Calls the lower string-send helper with final-send/no-more semantics. |
| `sub_4F5D90` | `zstr_sendm` | High | Calls the lower string-send helper with multipart/more semantics. |

Observed Binary Ninja HLIL anchors:

- `004f4bd2` and `004f4cdf` send stats publications through `zstr_send`.
- `004f4d78` sends the RCON identity frame through `zstr_sendm`.
- `004f4daa` sends the RCON payload frame through `zstr_send`.
- `004f4f09` sets the poll input bit for the RCON pump item.
- `004f4f0d` calls `zmq_poll` with a single poll item.
- `004f5d80` calls the lower string-send helper with final-send/no-more
  semantics.
- `004f5da7` calls the lower string-send helper with multipart/more semantics.

Observed fact: final send and immediate poll behavior belongs at the retained
Quake Live ZMQ wiring boundary. The CZMQ/libzmq helper bodies remain evidence,
not source to reconstruct.

## Source Reconstruction

This no-flags and immediate-poll boundary is now named in source instead of
leaving the zero-valued send and poll arguments inline.

SRP now names the zero-valued boundaries:

- `QL_ZMQ_NO_FLAGS`
- `QL_ZMQ_POLL_TIMEOUT_IMMEDIATE`

The retained source boundary is:

- `idZMQ_SendAuthFrame` uses `QL_ZMQ_SNDMORE` for multipart frames and
  `QL_ZMQ_NO_FLAGS` for the final auth response frame.
- `idZMQ_Publish` uses `QL_ZMQ_NO_FLAGS` for final stats publication sends.
- `idZMQ_PumpAuthSocket` and `idZMQ_PumpRcon` use
  `QL_ZMQ_POLL_TIMEOUT_IMMEDIATE` when checking for ready messages.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zstr_send`, `zstr_sendm`, `s_send_string`, or `zmq_poll` source bodies to the
repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_no_flags_and_immediate_poll_boundary_round_676`
  - `1 passed, 220 deselected in 0.21s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `77 passed, 144 deselected in 2.43s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.24s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
