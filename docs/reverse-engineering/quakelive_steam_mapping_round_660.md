# quakelive_steam.exe Mapping Round 660

Date: 2026-06-15

Scope: focused ZMQ password-file record formats, `zauth` PLAIN credential key
construction, and the actor `PLAIN` notification boundary. This round maps
Quake Live-owned wiring and CZMQ evidence only; it does not reconstruct
libzmq/CZMQ internals.

## Summary

Retail's password refresh path has three distinct pieces:

- `idZMQ_WritePasswordFile` writes `stats_stats=%s\n` and `rcon_rcon=%s\n` to
  `zmqpass.txt`.
- `idZMQ_ApplyPasswords` and `idZMQ_UpdatePasswords` notify the existing auth
  actor with the `PLAIN` command and wait for the acknowledgement when the
  actor slot is non-null.
- CZMQ `zauth` authenticates PLAIN requests by building a `%s_%s` key from the
  ZAP domain and username, then looking it up in the password table.

SRP keeps the same source-surface boundary without embedding CZMQ: the manual ZAP path reads retained password buffers directly while validating the equivalent domain/username/password tuple. The new source constants make the retail record formats and `zauth` key shape explicit while preserving the external libzmq runtime boundary.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4D2460` | `idZMQ_WritePasswordFile` | High | Opens `zmqpass.txt`, emits stats/RCON password records, and closes the file. |
| `sub_4F3D70` | `idZMQ_ApplyPasswords` | High | Writes the password file and sends actor command `PLAIN` when the auth actor exists. |
| `sub_4F3F20` | `idZMQ_UpdatePasswords` | High | Runtime refresh path that repeats the actor `PLAIN` notification and logs success. |
| `sub_4F5630` | `zsock_wait` | High | Waits for actor acknowledgement after the PLAIN command. |
| `sub_4F5DB0` | `zstr_sendx` | High | Sends actor control commands. |
| `sub_4F6630` | `s_authenticate_plain` | High | CZMQ `zauth` PLAIN credential verifier. |
| `sub_4F7360` | `zsys_sprintf` | High | Formats the `zauth` password-table lookup key as `%s_%s`. |

## Observed Facts

- `sub_4D2460` guards against uninitialized filesystem access, opens
  `zmqpass.txt`, writes the stats record only when its password is non-empty,
  writes the RCON record only when its password is non-empty, then closes the
  file.
- The password-record literals are stable in the retail string corpus:
  `stats_stats=%s\n` and `rcon_rcon=%s\n`.
- `sub_4F3D70` and `sub_4F3F20` both send the `PLAIN` actor command through
  `zstr_sendx` and wait through `zsock_wait` when the retained auth actor slot
  exists.
- `sub_4F6630` formats `%s_%s`, performs the password-table lookup, compares
  the supplied password, and logs allowed/denied PLAIN outcomes.

Observed fact: the actor notification and `%s_%s` lookup are CZMQ `zauth`
implementation details compiled into retail `quakelive_steam.exe`; SRP does not reconstruct libzmq/CZMQ internals as source.

Inferred source boundary: SRP should name these constants and preserve the
auth-gated password refresh ordering, but it should not implement `zstr_sendx`,
`zsock_wait`, `s_authenticate_plain`, or CZMQ's password-table internals.

## Source Reconstruction

- Added `QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT` and
  `QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT`, and changed
  `idZMQ_WritePasswordFile` to emit password records through those named
  retail formats.
- Added `QL_ZMQ_AUTH_KEY_FORMAT` for the retail `zauth` `%s_%s` lookup key.
  SRP does not need to construct that key at runtime because the manual ZAP
  path validates the equivalent tuple directly.
- Documented `idZMQ_ApplyPasswords` as SRP's actor-`PLAIN` notification
  boundary: retail sends the command to the auth actor, while SRP's manual ZAP
  path reads retained password buffers directly.
- Added a focused parity gate that cross-checks aliases, Ghidra rows, Binary
  Ninja HLIL, string-corpus anchors, source constants, and the absence of CZMQ
  implementation calls in `sv_zmq.c`.

## Confidence And Open Questions

Confidence is high because the password writer, apply/update paths, ZAP PLAIN
authenticator, promoted aliases, string corpus, and current source shape all
agree. The only divergence is intentional and already documented: the repo
keeps libzmq/CZMQ as external runtime/library evidence and implements only the
Quake Live server integration surface.

Open question: a later runtime fixture with external `libzmq.dll` can validate
end-to-end authenticated RCON/stats behavior. Static evidence is sufficient
for this mapping/source-boundary pass.

## Validation

- `python -m pytest -q tests/test_platform_services.py -k zmq_password_plain_notification_boundary_round_660`
  - `1 passed, 205 deselected in 0.13s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `64 passed, 142 deselected in 2.87s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.17s`
- `git diff --check`
  - Clean, with existing CRLF normalization warnings only.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`

## Parity Estimate

- Focused password PLAIN notification/source-boundary confidence:
  **before 93% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 97.5% -> after 97.6%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ password/auth evidence gap without changing the strict-retail Windows
  replacement score.
