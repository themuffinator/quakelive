# Quake Live Steam Mapping Round 665: ZMQ Password-File Failed-Open Boundary

Date: 2026-06-15

## Scope

This pass rechecked the retail password-file failed-open boundary in
`quakelive_steam.exe`. The mapped owner is the Quake Live-owned
`idZMQ_WritePasswordFile` helper that opens `zmqpass.txt`, logs failed opens,
writes password records, and returns to the retained auth apply/update paths.
The adjacent actor notification and wait helpers remain CZMQ evidence only;
SRP does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 98%** for the password-file
failed-open/source boundary. Focused ZMQ wiring/source reconstruction
confidence moves from **98.0% -> 98.1%**. Repo-wide parity remains **99%**
because this pass closes a local retained ZMQ source-shape gap without changing
the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4D2460` | `idZMQ_WritePasswordFile` | High | Opens `zmqpass.txt`, logs a failed open, writes stats/RCON password records, then closes the file. |
| `sub_4F3D70` | `idZMQ_ApplyPasswords` | High | Calls the password writer before the retail actor `PLAIN` notification when the auth actor slot exists. |
| `sub_4F3F20` | `idZMQ_UpdatePasswords` | High | Runtime password refresh path that repeats the password writer call and logs the update. |
| `sub_4F5630` | `zsock_wait` | High | Retail CZMQ actor acknowledgement wait; SRP source does not reconstruct it. |
| `sub_4F5DB0` | `zstr_sendx` | High | Retail CZMQ actor command sender for `PLAIN`; SRP source does not reconstruct it. |

Observed Binary Ninja HLIL anchors:

- `004d2460` starts `sub_4d2460`, the password-file writer.
- `004d2482` guards against filesystem calls before initialization.
- `004d24ac` opens the retained `zmqpass.txt` path through `data_5686b4`.
- `004d24b8` checks whether the open returned a null file handle.
- `004d24c6` logs `Failed to open %s\n`.
- `004d24e0` returns after the failed-open log.
- `004d24fc` formats `stats_stats=%s\n` when the stats password is non-empty.
- `004d2545` formats `rcon_rcon=%s\n` when the RCON password is non-empty.
- `004d2571` closes the opened file.
- `004f3d9e` and `004f3f4e` call `sub_4d2460` from the apply/update paths.

Observed retail string anchors:

- `005413dc`: `zmqpass.txt`
- `00541870`: `Failed to open %s\n`
- `00541ac4`: `rcon_rcon=%s\n`
- `00541ad4`: `stats_stats=%s\n`
- `005686b4`: retained pointer to the `zmqpass.txt` string

## Source Reconstruction

The failed-open log and password-record formats are Quake Live-owned. SRP now
names the failed-open format as `QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT` and routes
`idZMQ_WritePasswordFile` through it:

- `QL_ZMQ_PASSFILE`
- `QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT`
- `QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT`
- `QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT`

The source order remains the same: return if the filesystem is unavailable,
open `QL_ZMQ_PASSFILE`, log and return if the file cannot be opened, write the
stats record first when present, write the RCON record second when present, and
close the file.

The retail actor command and acknowledgement helpers (`zstr_sendx` and
`zsock_wait`) remain evidence for retail behavior. SRP keeps the manual ZAP
stand-in and external libzmq runtime boundary instead of reconstructing those
CZMQ implementation details.

## Validation

Completed 2026-06-15:

- `python -m pytest -q tests/test_platform_services.py -k zmq_passfile_failed_open_boundary_round_665`
  - `1 passed, 210 deselected in 4.10s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `69 passed, 142 deselected in 1.34s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.15s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
