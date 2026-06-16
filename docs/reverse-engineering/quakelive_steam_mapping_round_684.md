# Quake Live Steam Mapping Round 684: ZMQ Receive String-Terminator Boundary

Date: 2026-06-16

## Scope

This pass rechecked SRP's bounded stack-buffer replacement for retail
`zstr_recv`. Retail CZMQ receives a message, allocates `message_size + 1`, copies
the payload, and writes a trailing NUL byte. SRP intentionally keeps the CZMQ
helper body out of the repository, so `idZMQ_ReadFrameString` performs the same
string-termination ownership with caller-owned buffers.

Focused parity estimate: **before 92% -> after 98%** for receive
string-terminator source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.1% -> 99.15%**. Repo-wide parity
remains **99%** because this pass names a local bounded-string receive boundary
without changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F5CB0` | `zstr_recv` | High | CZMQ string receive helper used by the retained RCON pump. |
| `sub_401520` | `zmq_msg_recv` | High | Lower libzmq message receive helper used by `zstr_recv`. |
| `sub_4015E0` | `zmq_msg_data` | High | Supplies the received message payload copied by `zstr_recv`. |
| `sub_4015F0` | `zmq_msg_size` | High | Supplies the payload length used for the `size + 1` allocation. |

Observed Binary Ninja HLIL anchors:

- `004f5cfe` reads the received message size.
- `004f5d09` performs the `malloc(size + 1)` allocation.
- `004f5d27` copies exactly `size` payload bytes from message data.
- `004f5d2f` writes the trailing `0` terminator at `result + size`.

Observed fact: the string-termination contract is part of the Quake Live
`idZMQ` receive boundary in SRP. The `zstr_recv`, `zmq_msg_recv`,
`zmq_msg_data`, and `zmq_msg_size` helper bodies belong to embedded retail
CZMQ/libzmq dependency evidence and are not reconstructed in SRP.

## Source Reconstruction

This receive string-terminator boundary is now named in source:

- `QL_ZMQ_STRING_TERMINATOR_LENGTH`
- `QL_ZMQ_STRING_TERMINATOR`
- `QL_ZMQ_RCVMORE_NONE`

The retained source boundary is:

- `idZMQ_ReadFrameString` reserves `QL_ZMQ_STRING_TERMINATOR_LENGTH` bytes when
  receiving into caller-owned buffers.
- The first byte and final clamped byte use `QL_ZMQ_STRING_TERMINATOR`.
- The optional multipart probe initializes its local `RCVMORE` state through
  `QL_ZMQ_RCVMORE_NONE`.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zstr_recv`, `zstr_free`, `zmq_msg_recv`, `zmq_msg_data`, or `zmq_msg_size`
source bodies to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_receive_string_terminator_boundary_round_684`
  - `1 passed, 227 deselected in 4.54s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `81 passed, 147 deselected in 1.82s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.21s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
