# quakelive_steam.exe Mapping Round 640

Date: 2026-06-15

Scope: focused ZMQ RCON first-message handling pass for the retained `idZMQ`
host. This round stays inside the Quake Live-owned `id_zmq.cpp` wiring and does
not reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the retail `idZMQ_PumpRcon` branch at `sub_4F4ED0` against
the current portable `src/code/server/sv_zmq.c` implementation. Retail polls one
ROUTER socket, receives identity and command strings, and then splits on whether
the identity is already in the RCON peer table. The first message from a
previously unseen ROUTER identity is treated as a connection event: retail logs
the connection, inserts the peer, releases the command string, and returns
before command execution. SRP now mirrors that source shape by returning after a
new peer is inserted.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Owns the RCON poll/read/find/insert/execute branch. |
| `sub_4F4910` | `idZMQ_FindRconPeer` | High | Peer lookup before the connection-vs-command split. |
| `sub_4F49C0` | `idZMQ_InsertRconPeer` | High | Inserted only on the unseen identity path. |
| `sub_4F4640` | `std_tree_create_zmq_rcon_peer_node` | High | Allocates the peer node passed into insert. |
| `sub_4F4FD0` | `Zmq_PumpRcon` | High | Public tail-call wrapper used by the server frame. |

## Observed Facts

- `sub_4F4ED0` polls the RCON socket with `zmq_poll` and a single-item poll
  vector before receiving frames.
- The function calls `sub_4F5CB0` twice after a ready poll event, matching
  identity-frame and command-frame reads.
- It calls `sub_4F4910` against the peer table at `arg1 + 0x14` before deciding
  whether the identity is already known.
- On the unseen-peer path, the HLIL logs
  `zmq RCON client connected: %s\n`, calls `sub_4F49C0` with a newly created
  node from `sub_4F4640`, and returns via `sub_4F5E10(&var_c)`.
- This pins the first message from a previously unseen ROUTER identity as a
  connection event, not a command execution event.
- On the known-peer path, the HLIL logs
  `zmq RCON command from %s: %s\n` and then calls `sub_4C7CF0(var_c)`, which is
  the retained command execution lane.

## Source Reconstruction

- Updated `Zmq_PumpRcon` so an unseen RCON identity is registered and announced,
  then returns without executing the just-read command payload.
- Kept known-peer behavior unchanged: existing peers still log the command and
  call `Cmd_ExecuteString`.
- Preserved the current dynamic external `zmq_*` boundary and the
  default-disabled `QL_BUILD_ONLINE_SERVICES` policy.

## Confidence And Open Questions

Confidence is high for this local behavior change because the branch is
cross-checked against Binary Ninja HLIL, Ghidra function rows, existing aliases,
retail strings, and the current source. The portable source still differs from
retail's exact C++/CZMQ object ownership because SRP intentionally keeps libzmq
external and reconstructs only the Quake Live-owned server integration layer.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_first_message_connection_gate_round_640`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused RCON first-message source-shape confidence:
  **before 92% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 94.7% -> after 94.9%**.
- Repo-wide parity remains **99%** because this closes a local ZMQ behavior gap
  without changing the strict-retail Windows replacement score.
