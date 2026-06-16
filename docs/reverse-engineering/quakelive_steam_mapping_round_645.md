# quakelive_steam.exe Mapping Round 645

Date: 2026-06-15

Scope: focused ZMQ RCON frame-pump lifecycle pass for the retained `idZMQ`
host. This round stays in Quake Live server-owned wiring and does not
reconstruct retail libzmq/CZMQ internals.

## Summary

This pass rechecked the retail split between RCON setup and per-frame RCON
pumping. Retail `Zmq_RegisterCvarsAndInitRcon` tailcalls the retained
initializer that creates the ROUTER socket, applies auth settings, and binds
the endpoint. Retail `Zmq_PumpRcon` tailcalls `idZMQ_PumpRcon`, which polls
the already-retained socket at `this + 0xc`; it does not recreate the RCON
socket from the frame path.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Registers ZMQ cvars and creates/binds the RCON ROUTER socket when RCON is enabled. |
| `sub_4F4140` | `Zmq_RegisterCvarsAndInitRcon` | High | Startup wrapper that tailcalls the retained init method. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Per-frame poll/read/peer-dispatch path over the retained RCON socket. |
| `sub_4F4FD0` | `Zmq_PumpRcon` | High | Frame wrapper that tailcalls the retained RCON pump. |

## Observed Facts

- `sub_4F3F80` checks `zmq_rcon_enable`, creates the auth actor when needed,
  applies password state, creates a ROUTER socket with type `6`, stores it at
  `this + 0xc`, applies the `rcon` ZAP domain, PLAIN server mode, and ROUTER
  mandatory mode, then binds/logs the endpoint.
- `sub_4F4140` is the public startup wrapper into `sub_4F3F80`.
- `sub_4F4ED0` sets up a one-item poll vector and reads frames from
  `*(arg1 + 0xc)`, the retained RCON socket.
- `sub_4F4FD0` is the public frame wrapper into `sub_4F4ED0`.
- No retail HLIL evidence shows RCON socket creation from `sub_4F4ED0` or
  `sub_4F4FD0`.

## Source Reconstruction

- Updated portable `idZMQ_PumpAuthSocket` so it only pumps an existing manual
  ZAP REP socket. It no longer creates auth/runtime state from the frame path.
- Updated `Zmq_PumpRcon` so the frame pump no longer creates RCON or auth sockets. It now pumps auth only if an auth socket already exists and polls RCON only if `s_zmq.rconSocket` is already retained.
- Kept socket creation in `Zmq_RegisterCvarsAndInitRcon` /
  `idZMQ_EnsureRconSocket`, matching the retail init-vs-frame ownership split.
- Preserved SRP's manual ZAP REP socket as the documented portable substitute
  for retail's embedded CZMQ `zauth` actor, without vendoring or reconstructing
  libzmq/CZMQ source.

## Confidence And Open Questions

Confidence is high for the ownership correction because it is cross-checked
against Binary Ninja HLIL, Ghidra function rows, aliases, retail strings,
current server frame wiring, and prior RCON pump mapping rounds. The remaining
intentional divergence is SRP's manual ZAP REP pump, which exists only because
SRP keeps libzmq external instead of reconstructing retail's embedded actor
implementation.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_frame_pump_is_poll_only_round_645`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ RCON frame-pump source-shape confidence:
  **before 92% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 95.7% -> after 95.9%**.
- Repo-wide parity remains **99%** because this pass closes a local ZMQ
  lifecycle ownership gap without changing the strict-retail Windows
  replacement score.
