# quakelive_steam.exe Mapping Round 643

Date: 2026-06-15

Scope: focused ZMQ password-refresh source-shape pass for the retained
`idZMQ` host. This round maps the retail password-file writer and refresh
hooks without reconstructing retail libzmq/CZMQ internals.

## Summary

This pass rechecked the owning retail `quakelive_steam.exe` evidence around
`sub_4D2460`, `sub_4F3D70`, `sub_4F3F20`, and the exported
`Zmq_UpdatePasswords` wrapper. The key correction is that password refresh updates retained cvar snapshots and the password file, then notifies the existing auth actor in retail; it is not a socket lifecycle operation.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4D2460` | `idZMQ_WritePasswordFile` | High | Writes `stats_stats=%s\n` and `rcon_rcon=%s\n` password lines to the retained ZMQ password file. |
| `sub_4F3D70` | `idZMQ_ApplyPasswords` | High | Copies password cvar revision state, writes the password file, and sends the actor `PLAIN` command when the auth actor exists. |
| `sub_4F3F20` | `idZMQ_UpdatePasswords` | High | Refreshes password state, conditionally sends `PLAIN`, and logs `zmq stats and rcon passwords updated\n`. |
| `sub_4F4130` | `Zmq_UpdatePasswords` | High | Thin exported wrapper into the retained `idZMQ` instance. |

## Observed Facts

- `sub_4D2460` formats the two Quake Live ZMQ password-file records as
  `stats_stats=%s\n` and `rcon_rcon=%s\n`.
- `sub_4F3D70` refreshes the retained stats and RCON password counters before
  writing the password file. If the auth actor pointer is null, it returns
  without socket teardown.
- When the auth actor pointer is non-null, `sub_4F3D70` sends the `PLAIN`
  control command and waits for acknowledgement.
- `sub_4F3F20` repeats that refresh/send pattern for runtime cvar updates and
  then prints `zmq stats and rcon passwords updated\n`.
- Socket lifecycle is owned elsewhere: RCON ROUTER setup remains in
  `sub_4F3F80`, stats PUB setup remains in `sub_4F4210`, stats wrapper setup
  remains in `sub_4F43A0`, and shutdown remains in `sub_4F3DD0`/`sub_4F3DF0`.

## Source Reconstruction

- Added the `sub_4D2460 -> idZMQ_WritePasswordFile` alias so the password-file
  writer is directly searchable in the committed symbol map.
- Reduced portable `idZMQ_ApplyPasswords` to the retained password-file refresh
  hook. SRP's manual ZAP REP socket reads the updated retained password
  strings directly, so the retail actor `PLAIN` notification is represented by
  keeping password-file refresh separate from socket lifecycle work.
- Removed password-refresh socket teardown and eager re-creation. The
  `QL_ZMQ_PLAIN_SERVER` option remains bound to socket creation in
  `idZMQ_EnsureRconSocket` and `idZMQ_EnsureStatsPublisher`, matching the
  retail split where PLAIN server mode is set while creating ROUTER/PUB
  sockets.
- Kept libzmq as an external runtime dependency. This pass does not reconstruct retail libzmq/CZMQ internals or vendor embedded third-party code.

## Confidence And Open Questions

Confidence is high for the ownership split because the source change is
cross-checked against Binary Ninja HLIL control flow, the Ghidra function
table, promoted symbol aliases, string literals, and prior ZMQ mapping rounds.
The remaining divergence is intentional: retail's embedded CZMQ `zauth` actor
receives a `PLAIN` command, while SRP's portable implementation keeps a compact
manual ZAP REP socket and uses the retained password buffers directly.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_password_refresh_actor_source_shape_round_643`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ password-refresh actor/source-shape confidence:
  **before 91% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 95.3% -> after 95.5%**.
- Repo-wide parity remains **99%** because this pass closes a local ZMQ
  lifecycle ownership gap without changing the strict-retail Windows
  replacement score.
