# Quake Live Steam Mapping Round 663: ZMQ RCON Peer Log-Format Boundary

Date: 2026-06-15

## Scope

This pass rechecked the retail RCON peer log-format boundary in
`quakelive_steam.exe`. The mapped owner functions are the Quake Live-owned
`idZMQ_BroadcastRconOutput` and `idZMQ_PumpRcon` paths. The adjacent CZMQ
helpers are evidence for retail behavior. The manual ROUTER send/recv path keeps CZMQ helpers out of source and does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 98%** for the retail RCON peer
log-format boundary. Focused ZMQ wiring/source reconstruction confidence moves
from **97.8% -> 97.9%**. Repo-wide parity remains **99%** because this pass
closes a local retained ZMQ source-shape gap without changing the strict-retail
Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Walks retained RCON peers, sends identity and payload frames, logs disconnects before erasing failed peers. |
| `sub_4F4E60` | `Zmq_BroadcastRconOutput` | High | Public wrapper into the retained broadcast owner. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Polls the retained ROUTER socket, reads identity and command frames, logs first-contact and command execution. |
| `sub_4F4910` | `idZMQ_FindRconPeer` | High | Looks up the retained RCON peer before deciding whether first contact should be inserted. |
| `sub_4F49C0` | `idZMQ_InsertRconPeer` | High | Inserts a newly observed ROUTER identity into the retained peer table. |
| `sub_4F5CB0` | `zstr_recv` | High | Retail CZMQ helper used by the embedded retail binary; SRP source does not reconstruct it. |
| `sub_4F5D60` | `zstr_send` | High | Retail CZMQ helper for body-frame sending; SRP uses explicit `zmq_send` calls. |
| `sub_4F5D90` | `zstr_sendm` | High | Retail CZMQ helper for multipart identity-frame sending; SRP uses explicit `zmq_send` calls. |
| `sub_4F5E10` | `zstr_free` | High | Retail CZMQ helper freeing strings returned by `zstr_recv`; SRP uses stack buffers. |

Observed Binary Ninja HLIL anchors:

- `004f4d40` starts `sub_4f4d40`, the broadcast method owner.
- `004f4d78` sends the RCON peer identity with `sub_4f5d90` before the body
  frame.
- `004f4d92` logs `zmq RCON client disconnected: %s...` before peer erase.
- `004f4daa` sends the console payload through `sub_4f5d60`.
- `004f4f23` and `004f4f2f` receive identity and command frames through
  `sub_4f5cb0`.
- `004f4f5c` logs `zmq RCON client connected: %s\n` for first contact.
- `004f4f91` frees the command frame through `sub_4f5e10` after first contact.
- `004f4f99` logs `zmq RCON command from %s: %s\n` before command execution.
- `004f4fa2` dispatches the command string.

Observed retail string anchors:

- `00548388`: `zmq RCON client disconnected: %s\n`
- `005483ac`: `zmq RCON command from %s: %s\n`
- `005483cc`: `zmq RCON client connected: %s\n`

## Source Reconstruction

SRP now names the retail log formats in `src/code/server/sv_zmq.c`:

- `QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT`
- `QL_ZMQ_RCON_CLIENT_CONNECT_FORMAT`
- `QL_ZMQ_RCON_COMMAND_FORMAT`

`idZMQ_BroadcastRconOutput` routes disconnect logging through the disconnect
format and still erases the peer only after the identity frame send fails.
`idZMQ_PumpRcon` routes first-contact and command logging through the connect
and command formats while preserving the existing first-message gate: an
unknown peer is inserted and logged, then the first command frame is freed or
discarded rather than executed. A known peer logs and executes the command.

The retail binary used embedded CZMQ helpers (`zstr_recv`, `zstr_send`,
`zstr_sendm`, and `zstr_free`). SRP intentionally keeps those out of writable
source and uses the existing external runtime boundary: libzmq/CZMQ-derived
behavior is a dependency concern, while the source reconstructs only the Quake
Live-owned `idZMQ` wiring.

## Validation

Completed 2026-06-15:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_peer_log_format_boundary_round_663`
  - `1 passed, 208 deselected in 0.12s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `67 passed, 142 deselected in 1.34s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.14s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
