# Quake Live Steam Mapping Round 722: ZMQ Passfile Record-Buffer Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ passfile record-buffer boundary in SRP's retained
server-owned `idZMQ` wiring. Retail Quake Live formats the `stats_stats=%s\n`
and `rcon_rcon=%s\n` password records into a bounded local record buffer before
writing them to `zmqpass.txt`. SRP keeps the same Quake Live-owned passfile
shape while using wider engine-sized password buffers in the portable
dynamic-runtime adaptation.

Focused parity estimate: **before 94% -> after 99%** for passfile
record-buffer source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.5% -> 99.55%**. Repo-wide parity
remains **99%** because this pass names an SRP passfile record line buffer
without changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4D2460` | `idZMQ_WritePasswordFile` | High | Opens `zmqpass.txt`, formats stats/RCON password records, writes them, and closes the file. |
| `sub_4CF3E0` | `FS_FOpenFileWrite` | High | Opens the retained passfile path. |
| `sub_4D00F0` | `FS_Write` | High | Writes each formatted password record. |
| `sub_4CF320` | `FS_FCloseFile` | High | Closes the passfile after record emission. |

Observed Binary Ninja HLIL anchors:

- `004d2460` starts `sub_4d2460`, the retained password-file writer.
- `004d24ac` opens the retained `zmqpass.txt` path through
  `FS_FOpenFileWrite`.
- `004d24fc` formats `stats_stats=%s\n` into a `0x80` record buffer when the
  stats password is non-empty.
- `004d2522` writes the formatted stats record through `FS_Write`.
- `004d2545` formats `rcon_rcon=%s\n` into the same `0x80` record buffer when
  the RCON password is non-empty.
- `004d2568` writes the formatted RCON record through `FS_Write`.
- `004d2571` closes the opened passfile through `FS_FCloseFile`.
- `004f3d9e` and `004f3f4e` call the writer from the apply/update paths.

Observed fact: the passfile path, record formats, write order, and close path
are Quake Live `idZMQ` integration behavior. The adjacent CZMQ actor
notification calls remain retail dependency evidence.

Inference: SRP's wider `MAX_STRING_CHARS` password storage makes a wider
passfile record buffer appropriate for the portable dynamic-runtime path, but
that adaptation should still be named so reviewers do not mistake it for a
reconstructed libzmq/CZMQ detail.

## Source Reconstruction

The SRP passfile record line buffer is now named in source:

- `QL_ZMQ_PASSFILE_RECORD_SLACK`
- `QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE`

`idZMQ_WritePasswordFile` now declares
`char line[QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE]` before formatting the stats and
RCON password records with the retained Quake Live formats. The raw
`MAX_STRING_CHARS + 32` expression has been removed from the writer.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zstr_sendx`, `zsock_wait`, `zsock_*`, `zauth`, or lower `zmq::*` source bodies
to the repository.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_passfile_record_buffer_round_722 --tb=short` - 1 passed, 261 deselected.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short` - 89 passed, 173 deselected.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short` - 2 passed, 1 skipped.
- `rg --files src/libs/libzmq` - only `src/libs/libzmq\README.md`.
- `git diff --check` - passed with pre-existing LF-to-CRLF warnings.
