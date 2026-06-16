# Quake Live Steam Mapping Round 669: ZMQ Stats Transcript Line Boundary

Date: 2026-06-16

## Scope

This pass rechecked the stats transcript line boundary in SRP's retained ZMQ
publication lane. Retail Quake Live publishes serialized stats objects through
the embedded CZMQ `zstr_send` helper after the Quake Live-owned publication
wrappers build the `TYPE`/`DATA` payload. SRP keeps a local newline-delimited
fallback transcript for policy-disabled or runtime-unavailable builds, so this
round names the transcript record terminator without treating the fallback as a
retail libzmq/CZMQ implementation.

Focused parity estimate: **before 90% -> after 98%** for stats transcript
line/source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **98.4% -> 98.5%**. Repo-wide parity remains **99%**
because this pass closes a local fallback source-shape gap without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | High | Checks the retained stats PUB socket before serializing and sending the caller-provided player-event payload. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | High | Checks the retained stats PUB socket before serializing and sending the fixed `MATCH_REPORT` payload. |
| `sub_4F4E10` | `Zmq_ReportPlayerEvent` | High | Public wrapper forwarding player-event publication requests to the retained owner. |
| `sub_4F4E40` | `Zmq_SubmitMatchReport` | High | Public wrapper forwarding match-report publication requests to the retained owner. |
| `sub_4F5D60` | `zstr_send` | High | Retail CZMQ send helper for the serialized publication string; SRP source does not reconstruct it. |

Observed Binary Ninja HLIL anchors:

- `004f4b57` gates `idZMQ_ReportPlayerEvent` on the retained stats PUB socket
  at `this + 8`.
- `004f4bd2` sends the serialized player-event object through `zstr_send`.
- `004f4c65` gates `idZMQ_SubmitMatchReport` on the retained stats PUB socket.
- `004f4cdf` sends the serialized match-report object through `zstr_send`.
- `004f4e32` and `004f4e52` are the public wrapper calls into those retained
  publication owners.

Observed fact: retail publication is socket-gated and uses compiled-in
CZMQ/libzmq helpers. The SRP fallback transcript is an accommodation for
offline/default builds and records the same serialized publication message in a
local newline-delimited file when the source path is exercised.

## Source Reconstruction

SRP now names the fallback transcript line boundary:

- `QL_ZMQ_STATS_TRANSCRIPT`
- `QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR`
- `QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR_LENGTH`

`idZMQ_OpenStatsTranscript` remains the only opener for
`zmq_stats.ndjson`. `idZMQ_WriteStatsTranscript` still exits when stats
publication is disabled, the message is empty, or the transcript file cannot be
opened. When it does write, it writes the serialized publication message and
then writes the named record terminator.

`idZMQ_Publish` still builds the publication message first, writes the SRP
fallback transcript before the live send attempt, and then uses the dynamically
resolved external `zmq_send` symbol when a live PUB socket exists. Retail
`zstr_send` remains mapped evidence only. This round does not reconstruct libzmq/CZMQ internals and does not add libzmq source to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_stats_transcript_line_boundary_round_669`
  - `1 passed, 214 deselected in 0.11s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `73 passed, 142 deselected in 1.51s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.16s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
