# quakelive_steam.exe Mapping Round 656

Date: 2026-06-15

Scope: focused ZMQ public-wrapper to retained `idZMQ` method-owner source
reconstruction. This round is limited to Quake Live-owned wiring and does not reconstruct libzmq/CZMQ internals.

## Summary

Retail exposes small public ZMQ entrypoints that forward to methods on the
retained global `idZMQ` object at `data_5756fc`. Examples include
`sub_4F4140 -> sub_4F3F80(&data_5756fc)` for registration,
`sub_4F43A0 -> sub_4F4210(&data_5756fc)` for stats publisher init, and
`sub_4F4FD0 -> sub_4F4ED0(&data_5756fc)` for the RCON pump.

SRP previously kept several method bodies directly in the exported `Zmq_*`
functions. This round reconstructs the retail wrapper/method split in portable
C: public `Zmq_*` functions now delegate to static `idZMQ_*` method owners,
while existing callers keep the stable `server.h` API.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3F20` | `idZMQ_UpdatePasswords` | High | Method owner for password refresh and actor password-file apply. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Method owner for ZMQ cvar registration and initial RCON ensure. |
| `sub_4F4130` | `Zmq_UpdatePasswords` | High | Public wrapper tailcalls `sub_4F3F20(&data_5756fc)`. |
| `sub_4F4140` | `Zmq_RegisterCvarsAndInitRcon` | High | Public wrapper tailcalls `sub_4F3F80(&data_5756fc)`. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Method owner for stats PUB setup. |
| `sub_4F43A0` | `Zmq_InitStatsPublisher` | High | Public wrapper tailcalls `sub_4F4210(&data_5756fc)`. |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | High | Method owner for player-event publication. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | High | Method owner for match-report publication. |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Method owner for broadcasting console output to retained RCON peers. |
| `sub_4F4E10` | `Zmq_ReportPlayerEvent` | High | Public wrapper forwards to `sub_4F4B20(&data_5756fc, ...)`. |
| `sub_4F4E40` | `Zmq_SubmitMatchReport` | High | Public wrapper forwards to `sub_4F4C30(&data_5756fc, ...)`. |
| `sub_4F4E60` | `Zmq_BroadcastRconOutput` | High | Public wrapper forwards to `sub_4F4D40(&data_5756fc)`. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Method owner for auth pump, ROUTER polling, peer tracking, and command dispatch. |
| `sub_4F4FD0` | `Zmq_PumpRcon` | High | Public wrapper tailcalls `sub_4F4ED0(&data_5756fc)`. |

## Observed Facts

- `sub_4F4130`, `sub_4F4140`, `sub_4F43A0`, and `sub_4F4FD0` are tailcall
  wrappers over the retained global `idZMQ` object.
- `sub_4F4E10`, `sub_4F4E40`, and `sub_4F4E60` preserve public argument
  forwarding while injecting `&data_5756fc` as the method receiver.
- The method owners retain the actual ZMQ behavior: cvar registration,
  password apply, stats PUB setup/publication, RCON broadcast, and RCON pump.
- These wrappers are Quake Live-owned API wiring. They are not a request to
  reconstruct or vendor libzmq/CZMQ.

## Source Reconstruction

- Added static `idZMQ_RegisterCvarsAndInitRcon`,
  `idZMQ_UpdatePasswords`, `idZMQ_InitStatsPublisher`,
  `idZMQ_SubmitMatchReport`, `idZMQ_ReportPlayerEvent`,
  `idZMQ_BroadcastRconOutput`, and `idZMQ_PumpRcon` method owners.
- Converted public `Zmq_RegisterCvarsAndInitRcon`, `Zmq_UpdatePasswords`,
  `Zmq_InitStatsPublisher`, `Zmq_SubmitMatchReport`,
  `Zmq_ReportPlayerEvent`, `Zmq_BroadcastRconOutput`, and `Zmq_PumpRcon` into
  thin wrappers over those method owners; each public wrapper tailcalls the retained idZMQ method owner in the retail evidence.
- Left `Zmq_ShutdownStatsPublisher` and `Zmq_ShutdownRuntime` as their already
  mapped shutdown owners from earlier rounds.
- Preserved the external libzmq runtime boundary: no `zmq.h`, `libzmq.lib`,
  libzmq/CZMQ source, or binary dependency was added to source.

## Validation

- `python -m pytest -q tests/test_platform_services.py -k zmq_public_wrapper_tailcalls_round_656`
  - `1 passed, 201 deselected in 0.11s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `60 passed, 142 deselected in 1.08s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.25s`
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`

## Parity Estimate

- Focused ZMQ public-wrapper/method-owner source-shape confidence:
  **before 88% -> after 97%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 97.0% -> after 97.2%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ source-shape gap without changing the strict-retail Windows replacement
  score.
