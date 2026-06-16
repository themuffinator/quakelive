# Quake Live Steam Mapping Round 680: ZMQ Poll-Item Zero-State Boundary

Date: 2026-06-16

## Scope

This pass rechecked the retained ZMQ poll-item setup used by the RCON pump.
Retail Quake Live prepares a stack `zmq_pollitem_t`-shaped object by assigning
the socket pointer, zeroing the side fields, then setting the input-event word
before calling `zmq_poll`. SRP already matched the behavior; this round names
the socket-fd-none and revents-none boundaries instead of leaving poll-item
zero state as raw `0` assignments.

Focused parity estimate: **before 93% -> after 98%** for poll-item zero-state
source-boundary confidence. Focused ZMQ wiring/source reconstruction confidence
moves from **99.0% -> 99.05%**. Repo-wide parity remains **99%** because this
pass closes a local poll-item source-shape gap without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401600` | `zmq_poll` | High | Lower libzmq poll entry reached by the retained RCON pump. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Builds the one-item RCON poll vector before reading identity and command frames. |

Observed Binary Ninja HLIL anchors:

- `004f4ed0` starts the retained RCON pump owner.
- `004f4ef7` zeroes one poll-item side field before the poll call.
- `004f4efc` zeroes the events/revents storage before setting the events word.
- `004f4f00` zeroes the adjacent stack state before the poll call.
- `004f4f09` sets the poll item events word to `1`, matching `ZMQ_POLLIN`.
- `004f4f0d` calls `zmq_poll` as `sub_401600(xmm0, &var_20, 1)`.

Observed fact: the zero-state poll-item setup is Quake Live `idZMQ`
integration wiring. The `zmq_poll` implementation body belongs to the embedded
retail libzmq/CZMQ dependency evidence and is not reconstructed in SRP.

## Source Reconstruction

This poll-item zero-state boundary is now named in source:

- `QL_ZMQ_POLL_FD_NONE`
- `QL_ZMQ_POLL_REVENTS_NONE`

The retained source boundary is:

- `idZMQ_PumpRcon` assigns `QL_ZMQ_POLL_FD_NONE`, `QL_ZMQ_POLLIN`, and
  `QL_ZMQ_POLL_REVENTS_NONE` before polling the retained RCON socket.
- `idZMQ_PumpAuthSocket` uses the same named zero-state fields for SRP's
  external-libzmq ZAP endpoint pump and resets `revents` through
  `QL_ZMQ_POLL_REVENTS_NONE` after handled auth replies.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zmq_poll`, `zpoller`, `zstr_recv`, `zstr_send`, `zstr_sendm`, or `zactor`
source bodies to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_poll_item_zero_state_boundary_round_680`
  - `1 passed, 223 deselected in 9.79s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `79 passed, 145 deselected in 2.40s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.24s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
