# quakelive_steam.exe Mapping Round 653

Date: 2026-06-15

Scope: focused ZMQ shutdown-owner split reconstruction for the retained
`idZMQ` host. This round is limited to Quake Live-owned server wiring and does
not reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

Retail keeps stats publisher shutdown and runtime RCON/auth shutdown in two
separate functions. `sub_4F3DD0` owns only the stats PUB socket slot, while
`sub_4F3DF0` owns the RCON socket slot, resolved RCON poll slot, and shared
auth actor. SRP previously let `Zmq_ShutdownRuntime` call
`Zmq_ShutdownStatsPublisher`, blending those two owners.

This round restores the retail source shape: stats PUB shutdown remains separate from runtime RCON/auth shutdown in
`Zmq_ShutdownStatsPublisher`, and `Zmq_ShutdownRuntime` now handles only the
runtime RCON/auth/context side. `SV_Shutdown` still calls the stats shutdown
owner, and `Com_Shutdown` still calls the runtime shutdown owner.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3DD0` | `Zmq_ShutdownStatsPublisher` | High | Checks the stats PUB slot and destroys only that socket wrapper. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | High | Clears the resolved RCON poll slot, destroys the RCON socket, and destroys the shared auth actor. |
| `sub_4F5190` | `zsock_destroy_checked` | High | Destroys retained CZMQ socket wrappers in the stats/RCON shutdown paths. |
| `sub_4F5B50` | `zactor_destroy` | High | Destroys the retained auth actor from runtime shutdown. |

## Observed Facts

- `sub_4F3DD0` checks `data_575704` and calls
  `zsock_destroy_checked(&data_575704, "zmq\\id_zmq.cpp", 0x73)`.
- `sub_4F3DF0` checks `data_575708`, clears `data_57570c`, and calls
  `zsock_destroy_checked(&data_575708, "zmq\\id_zmq.cpp", 0xe2)`.
- `sub_4F3DF0` then checks `data_575700` and calls
  `zactor_destroy(&data_575700)`.
- There is no call from `sub_4F3DF0` back into `sub_4F3DD0`.

## Source Reconstruction

- Removed the internal `Zmq_ShutdownStatsPublisher()` call from
  `Zmq_ShutdownRuntime`.
- Kept `Zmq_ShutdownStatsPublisher` as the stats transcript/PUB socket close
  owner.
- Kept `Zmq_ShutdownRuntime` focused on RCON socket close, resolved poll slot
  clear, auth owner shutdown, context termination, and dynamic library unload.
  A later peer-destructor pass keeps retained peer-table cleanup out of this
  runtime shutdown owner.
- Preserved caller wiring: `SV_Shutdown` calls `Zmq_ShutdownStatsPublisher`,
  while `Com_Shutdown` calls `Zmq_ShutdownRuntime`.
- Preserved the external libzmq runtime boundary. This pass does not add
  libzmq or CZMQ source.

## Confidence And Open Questions

Confidence is high because the retail functions are adjacent, small, and
directly visible in Binary Ninja HLIL, and the aliases/Ghidra function rows
match the existing source owners. The portable runtime still keeps a local
stats transcript fallback and explicit context/library cleanup, which are SRP
adaptations around the external-runtime boundary rather than reconstructed
libzmq internals.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_shutdown_owner_split_round_653`
  - `1 passed, 198 deselected`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `57 passed, 142 deselected`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped`

## Parity Estimate

- Focused ZMQ shutdown-owner split confidence:
  **before 91% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.7% -> after 96.8%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ shutdown ownership source-shape gap without changing the strict-retail
  Windows replacement score.
