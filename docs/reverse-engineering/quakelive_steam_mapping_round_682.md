# Quake Live Steam Mapping Round 682: ZMQ RCON Receive-Buffer Boundary

Date: 2026-06-16

## Scope

This pass rechecked the retained RCON receive path in `idZMQ_PumpRcon`.
Retail Quake Live receives exactly two string frames from the RCON ROUTER
socket: the peer identity and the command payload. SRP intentionally keeps
CZMQ out of the repository, so the writable source uses bounded stack buffers
and external `zmq_recv` instead of reconstructing `zstr_recv`.

Focused parity estimate: **before 92% -> after 98%** for RCON receive-buffer
source-boundary confidence. Focused ZMQ wiring/source reconstruction confidence
moves from **99.05% -> 99.1%**. Repo-wide parity remains **99%** because this
pass names a local receive-buffer source boundary without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Polls the retained RCON socket, receives identity and command frames, then dispatches or registers the peer. |
| `sub_4F5CB0` | `zstr_recv` | High | CZMQ helper used twice by retail RCON pump for identity and command strings. |
| `sub_4F5E10` | `zstr_free` | High | CZMQ helper used by retail RCON pump to release received strings. |

Observed Binary Ninja HLIL anchors:

- `004f4f23` calls `zstr_recv` for the first RCON frame.
- `004f4f2f` calls `zstr_recv` for the second RCON frame.
- `004f4f91` frees the command frame after a new peer is registered.
- `004f4fab` frees the identity frame after command dispatch.
- `004f4fb7` frees the command frame after command dispatch.

Observed fact: the two retail `zstr_recv` calls and the two-frame receive
ownership belong to the Quake Live `idZMQ` RCON pump. The `zstr_recv` and
`zstr_free` helper bodies belong to the embedded retail CZMQ/libzmq dependency
evidence and are not reconstructed in SRP.

## Source Reconstruction

This RCON receive-buffer boundary is now named in source:

- `QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE`
- `QL_ZMQ_RCON_COMMAND_BUFFER_SIZE`

The retained source boundary is:

- `idZMQ_PumpRcon` uses `QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE` for the peer
  identity frame that corresponds to the first retail `zstr_recv`.
- `idZMQ_PumpRcon` uses `QL_ZMQ_RCON_COMMAND_BUFFER_SIZE` for the command
  frame that corresponds to the second retail `zstr_recv`.
- `idZMQ_ReadRconCommand` remains the bounded stack-buffer equivalent of the
  second retail receive and drains surplus multipart frames through the
  previously pinned receive/drain boundary.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zstr_recv`, `zstr_free`, `zmq_msg_recv`, or related helper bodies to the
repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_receive_buffer_boundary_round_682`
  - `1 passed, 225 deselected in 0.17s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `80 passed, 146 deselected in 2.15s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.25s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
