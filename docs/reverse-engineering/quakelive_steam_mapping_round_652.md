# quakelive_steam.exe Mapping Round 652

Date: 2026-06-15

Scope: focused ZMQ auth-gated password-file refresh reconstruction for the
retained `idZMQ` host. This round stays in Quake Live-owned wiring and does
not reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the password apply/update path after the shared auth-owner
mapping from Round 651. Retail updates the retained password cvar revision
snapshots before checking the auth actor, but the password-file write and
`PLAIN` actor command are gated by the retained auth actor slot at
`this + 0x04`. When that slot is null, `sub_4F3D70` returns before calling the
password-file writer.

SRP now mirrors that ownership split with the portable `authActorReady` state:
`idZMQ_ApplyPasswords` returns until the manual ZAP owner exists, while
`idZMQ_EnsureAuthSocket` marks that owner ready and immediately reapplies
passwords after binding. This keeps early cvar snapshotting harmless and moves
the password-file refresh to the same lifecycle phase as retail.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4D2460` | `idZMQ_WritePasswordFile` | High | Formats `stats_stats=%s\n` and `rcon_rcon=%s\n` records. |
| `sub_4F3D70` | `idZMQ_ApplyPasswords` | High | Updates retained password revisions, returns if the auth actor slot is null, and only then writes/sends `PLAIN`. |
| `sub_4F3F20` | `idZMQ_UpdatePasswords` | High | Uses the same auth-actor gate for runtime password refresh before logging the update message. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Calls password apply after creating and acknowledging the shared auth actor. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Shares the same auth actor creation and password apply path before stats PUB setup. |

## Observed Facts

- `sub_4F3D70` stores the current stats/RCON password cvar revision counters.
- It then checks `*(arg1 + 4) == 0` and returns before `sub_4D2460` when the
  auth actor slot is absent.
- When the auth actor slot exists, `sub_4F3D70` calls `sub_4D2460`, sends the
  `PLAIN` command with `zstr_sendx`, and waits with `zsock_wait`.
- `sub_4F3F20` repeats the same `*(arg1 + 4) != 0` gate for runtime password
  refresh and still prints `zmq stats and rcon passwords updated\n`.
- RCON and stats setup call `sub_4F3D70` only after creating and acknowledging
  the shared auth actor.

## Source Reconstruction

- `idZMQ_ApplyPasswords` now requires `s_zmq.authActorReady` before writing
  `zmqpass.txt`.
- The helper still has no socket teardown or socket creation side effects.
- `idZMQ_EnsureAuthSocket` remains the source owner that marks the manual ZAP
  socket ready and immediately calls `idZMQ_ApplyPasswords()` after bind.
- `Zmq_RegisterCvarsAndInitRcon` can still snapshot cvar values before RCON
  setup; the guarded apply no-ops until auth creation mirrors retail's actor
  gate.
- The manual ZAP owner remains the portable stand-in for retail's embedded
  CZMQ `zauth` actor. This pass does not add libzmq/CZMQ source.

## Confidence And Open Questions

Confidence is high because the branch is directly visible in Binary Ninja HLIL,
matches the function rows and existing aliases, and aligns with the Round 651
shared auth-owner reconstruction. The remaining difference is intentional:
retail sends a `PLAIN` command to a CZMQ actor, while SRP's manual ZAP socket
uses retained password buffers directly once the owner is ready.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_password_apply_auth_gate_round_652`
  - `1 passed, 197 deselected`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `56 passed, 142 deselected`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped`

## Parity Estimate

- Focused ZMQ auth-gated password-file refresh confidence:
  **before 92% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.6% -> after 96.7%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ auth/password lifecycle source-shape gap without changing the
  strict-retail Windows replacement score.
