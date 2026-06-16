# quakelive_steam.exe Mapping Round 651

Date: 2026-06-15

Scope: focused ZMQ auth actor ready state and runtime shutdown ordering for the
retained `idZMQ` host. This pass reconstructs Quake Live-owned wiring only and
does not reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

Retail keeps a shared auth actor at the retained `idZMQ` slot `this + 0x04`.
Both the RCON setup path and the stats publisher setup path create that actor
only when the slot is empty, send the actor a `VERBOSE` command, wait for the
acknowledgement, and then run the password apply path. Retail runtime shutdown
then destroys the RCON socket slot and clears the resolved RCON poll slot before
destroying the shared auth actor.

SRP still uses the portable manual ZAP REP socket in place of retail's embedded
CZMQ `zauth` actor. This round makes that intentional stand-in source-shaped
like the retained actor owner: the manual auth socket now has an explicit
`authActorReady` state, applies passwords immediately after first bind, gates
the auth pump on that state, and shuts down RCON before the shared auth owner.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3D70` | `idZMQ_ApplyPasswords` | High | Password-file apply hook called immediately after a newly created auth actor is made ready. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | High | Destroys the RCON socket slot, clears the resolved slot, then destroys the shared auth actor. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | RCON setup creates the shared auth actor only when `this + 0x04` is null. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Stats setup shares the same auth actor creation/apply path. |
| `sub_4F5630` | `zsock_wait` | High | Waits for the auth actor acknowledgement after `VERBOSE` and `PLAIN` control commands. |
| `sub_4F5A30` | `zactor_new` | High | Creates retail's embedded `zauth` actor. |
| `sub_4F5B50` | `zactor_destroy` | High | Destroys the retained auth actor during runtime shutdown. |
| `sub_4F5DB0` | `zstr_sendx` | High | Sends actor control commands such as `VERBOSE` and `PLAIN`. |

## Observed Facts

- `sub_4F3F80` checks `*(arg1 + 4) == 0` before creating the RCON/stat shared
  auth actor with `zactor_new(zauth, 0)`.
- The newly created actor receives `VERBOSE`, is acknowledged with
  `zsock_wait`, and is followed by `sub_4F3D70(arg1)`.
- `sub_4F4210` repeats the same actor-null check and creation path before
  creating the stats PUB socket.
- `sub_4F3DF0` first checks the retained RCON socket slot at `data_575708`,
  clears the resolved slot `data_57570c`, and destroys the RCON socket.
- The same shutdown function then checks `data_575700` and destroys the shared
  auth actor with `zactor_destroy`.

## Source Reconstruction

- Added `authActorReady` to portable `idZMQ_t` as the source-level stand-in for
  retail's non-null auth actor slot.
- `idZMQ_EnsureAuthSocket` now marks the retained auth owner ready only after
  the ZAP socket is bound, then calls `idZMQ_ApplyPasswords()` to mirror the
  retail post-`VERBOSE` password apply step.
- `idZMQ_PumpAuthSocket` now requires the auth actor ready state before polling
  the manual ZAP socket.
- `idZMQ_CloseAuthSocket` clears the ready state with the auth socket.
- `Zmq_ShutdownRuntime` now closes the RCON socket before the shared auth owner
  and clears the resolved poll slot before destroying that auth owner, matching the retail
  `sub_4F3DF0` ordering.
- The manual ZAP socket remains the portable replacement for retail's embedded
  CZMQ actor. This pass does not add `zactor`, `zauth`, or libzmq source to the
  repository.

## Confidence And Open Questions

Confidence is high because the actor-null gate, `VERBOSE` command, password
apply call, shutdown ordering, Ghidra function rows, promoted aliases, and
retail strings all agree. The remaining divergence is intentional: SRP's
runtime is still dynamically bound to an external libzmq and uses a compact
manual ZAP socket instead of reconstructing CZMQ's actor implementation.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_auth_actor_ready_shutdown_order_round_651`
  - `1 passed, 196 deselected`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `55 passed, 142 deselected`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped`

## Parity Estimate

- Focused ZMQ auth actor ready state and shutdown-order confidence:
  **before 90% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.5% -> after 96.6%**.
- Repo-wide parity remains **99%** because this pass closes a local ZMQ runtime
  ownership source-shape gap without changing the strict-retail Windows
  replacement score.
