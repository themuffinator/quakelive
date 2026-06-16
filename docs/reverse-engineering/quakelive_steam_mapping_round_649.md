# quakelive_steam.exe Mapping Round 649

Date: 2026-06-15

Scope: focused ZMQ RCON/PUB bind-failure retained-slot reconstruction for the
retained `idZMQ` host. This round stays in Quake Live server-owned wiring and
does not reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the retail RCON and stats socket setup paths after socket
creation but before the public endpoint log. Retail stores the created RCON
socket at the retained `idZMQ` RCON slot and the created PUB socket at the
retained stats slot before calling `zsock_bind`. If bind fails, retail selects
the error log string, prints it, and leaves the created socket in the retained
slot. SRP now mirrors that source shape: bind failures retain the created socket slot instead of closing the socket inside the bind-error branch.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Creates the RCON ROUTER socket, stores it at `this + 0x0c`, then attempts bind. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Creates the stats PUB socket, stores it at `this + 0x08`, then attempts bind. |
| `sub_4F5100` | `zsock_new_checked` | High | Allocates the CZMQ `zsock` wrapper used by both retained setup paths. |
| `sub_4F5200` | `zsock_bind` | High | Endpoint bind helper returning `0xffffffff` on failure. |
| `sub_4F56B0` | `zsock_resolve` | High | Resolves the wrapped socket after RCON bind logging and feeds the retained poll slot. |

## Observed Facts

- `sub_4F3F80` stores the new RCON socket at `arg1 + 0x0c` before the
  `sub_4F5200` bind result branch.
- The RCON bind branch selects either `zmq RCON socket error, bind failed: %s\n`
  or `zmq RCON socket: %s\n`, prints the selected string, then resolves the
  retained socket and stores that result at `arg1 + 0x10`.
- `sub_4F4210` stores the new stats PUB socket at `arg1 + 0x08` before the
  `sub_4F5200` bind result branch.
- The stats bind branch selects either `zmq PUB socket error, bind failed: %s\n`
  or `zmq PUB socket: %s\n`, then prints the selected string.
- No retail destroy call is observed in either bind-error branch; socket
  destruction remains with the shutdown/disabled paths.

## Source Reconstruction

- Moved `s_zmq.rconSocket = socket` before the RCON `zmq_bind` call in
  `idZMQ_EnsureRconSocket`.
- Moved `s_zmq.pubSocket = socket` before the stats `zmq_bind` call in
  `idZMQ_EnsureStatsPublisher`.
- Removed the non-retail `s_zmq.zmq_close( socket )` calls from both bind-error
  branches; those branches now log and return with the retained socket slot
  populated.
- Kept explicit close ownership in disabled-mode handling,
  `Zmq_ShutdownStatsPublisher`, and `Zmq_ShutdownRuntime`.
- Preserved the external libzmq runtime boundary; this pass does not
  reconstruct embedded CZMQ/libzmq internals.

## Confidence And Open Questions

Confidence is high for the retained-slot ordering because it is cross-checked
against Binary Ninja HLIL, Ghidra function rows, aliases, retail strings,
CZMQ helper aliases, and the current source setup paths. The RCON resolved poll
slot at `this + 0x10` remains represented by SRP's portable per-frame
`zmq_pollitem_t`; this round only reconstructs the socket-retention semantics
around bind failure.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_socket_bind_failure_retention_round_649`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ bind-failure retained-slot confidence:
  **before 89% -> after 97%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.3% -> after 96.4%**.
- Repo-wide parity remains **99%** because this pass closes a local setup
  source-shape gap without changing the strict-retail Windows replacement
  score.
