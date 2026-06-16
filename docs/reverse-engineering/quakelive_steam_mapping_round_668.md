# Quake Live Steam Mapping Round 668: ZMQ Receive Frame Drain Boundary

Date: 2026-06-16

## Scope

This pass rechecked the receive frame drain boundary used by SRP's retained ZMQ
auth and RCON pumps. Retail Quake Live uses embedded CZMQ `zstr_recv` and
lower `zmq_msg_*` helpers. SRP keeps those helpers outside the source tree and
uses a stack-buffer receive/drain equivalent over dynamically resolved
external libzmq symbols.

Focused parity estimate: **before 91% -> after 98%** for receive frame
drain/source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **98.3% -> 98.4%**. Repo-wide parity remains **99%**
because this pass closes a local frame-drain source-shape gap without changing
the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F5CB0` | `zstr_recv` | High | Receives a ZMQ message, allocates a string, copies message bytes, appends a terminator, and closes the message. |
| `sub_4F5E10` | `zstr_free` | High | Frees strings returned by `zstr_recv`. |
| `sub_401520` | `zmq_msg_recv` | High | Lower libzmq message receive wrapper used by `zstr_recv`. |
| `sub_401570` | `zmq_msg_init` | High | Initializes the temporary message object. |
| `sub_4015B0` | `zmq_msg_close` | High | Closes the temporary message object. |
| `sub_4015E0` | `zmq_msg_data` | High | Reads the received message data pointer. |
| `sub_4015F0` | `zmq_msg_size` | High | Reads the received message byte count. |

Observed Binary Ninja HLIL anchors:

- `004f5cb0` starts `zstr_recv`.
- `004f5cd0` initializes the temporary message object.
- `004f5ce6` receives into that message object.
- `004f5cfe` reads the message size.
- `004f5d09` allocates `size + 1` bytes for a C string.
- `004f5d27` copies the received bytes from message data.
- `004f5d2f` writes the trailing NUL terminator.
- `004f5d37` closes the temporary message object.

Observed fact: retail's allocation/free mechanics are embedded CZMQ/libzmq
support code. SRP does not reconstruct libzmq/CZMQ internals and should not add
`zstr_recv`, `zstr_free`, or `zmq_msg_*` source bodies.

## Source Reconstruction

SRP now names the receive drain scratch buffer size:

- `QL_ZMQ_DRAIN_SCRATCH_SIZE`

The source boundary is:

- `idZMQ_ReadFrameString` clears output state before receiving.
- It uses nonblocking `zmq_recv` through `QL_ZMQ_DONTWAIT`.
- It reserves one byte for a trailing NUL, clamps overlong frames, and always
  terminates the destination buffer when the caller provides storage.
- It queries `QL_ZMQ_RCVMORE` through optional `zmq_getsockopt` to tell callers
  whether more multipart frames remain.
- `idZMQ_DrainRemainingFrames` uses the named scratch buffer and repeatedly
  reads until `RCVMORE` is false or the runtime reports a read failure.
- The auth pump and RCON command paths drain surplus frames so malformed or
  overlong multipart messages do not bleed into later commands.

This is the SRP stack-buffer receive/drain equivalent of the retail `zstr_recv`
contract. The retail helper bodies remain mapped evidence only; SRP continues
to use the external libzmq runtime boundary.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_receive_frame_drain_boundary_round_668`
  - `1 passed, 213 deselected in 0.08s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `72 passed, 142 deselected in 1.45s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.12s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
