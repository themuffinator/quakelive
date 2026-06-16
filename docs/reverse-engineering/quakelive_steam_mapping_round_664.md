# Quake Live Steam Mapping Round 664: ZMQ Stats Publication Envelope Boundary

Date: 2026-06-15

## Scope

This pass rechecked the retail stats publication envelope boundary in
`quakelive_steam.exe`. The mapped owner functions are the Quake Live-owned
`idZMQ_ReportPlayerEvent` and `idZMQ_SubmitMatchReport` paths. The adjacent
retail serializer and `zstr_send` helper are evidence for the envelope and send
boundary; SRP source keeps a portable JSON envelope and does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 98%** for the retail stats
publication envelope boundary. Focused ZMQ wiring/source reconstruction
confidence moves from **97.9% -> 98.0%**. Repo-wide parity remains **99%**
because this pass closes a local retained ZMQ source-shape gap without changing
the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | High | Checks the retained PUB socket, stores wrapper-provided event type under `TYPE`, stores the payload under `DATA`, serializes, and sends. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | High | Checks the retained PUB socket, stores fixed `MATCH_REPORT` under `TYPE`, stores the report payload under `DATA`, serializes, and sends. |
| `sub_4F4E10` | `Zmq_ReportPlayerEvent` | High | Public wrapper forwarding to the retained player-event publisher. |
| `sub_4F4E40` | `Zmq_SubmitMatchReport` | High | Public wrapper forwarding to the retained match-report publisher. |
| `sub_4F5D60` | `zstr_send` | High | Retail CZMQ send helper for the serialized publication string; SRP source does not reconstruct it. |

Observed Binary Ninja HLIL anchors:

- `004f4b57` gates `idZMQ_ReportPlayerEvent` on the retained stats PUB socket
  at `this + 8`.
- `004f4b72` builds the dynamic event type string from the wrapper argument.
- `004f4b8b` stores the dynamic type under `TYPE`.
- `004f4bac` stores the event payload under `DATA`.
- `004f4bd2` sends the serialized player-event object through `zstr_send`.
- `004f4c65` gates `idZMQ_SubmitMatchReport` on the retained stats PUB socket.
- `004f4c80` builds the fixed `MATCH_REPORT` type string.
- `004f4c99` stores that fixed type under `TYPE`.
- `004f4cb9` stores the match report under `DATA`.
- `004f4cdf` sends the serialized match-report object through `zstr_send`.
- `004f4e32` and `004f4e52` are the public wrapper calls into those retained
  method owners.

Observed retail string anchors:

- `00548368`: `DATA`
- `00548370`: `TYPE`
- `00548378`: `MATCH_REPORT`

## Source Reconstruction

TYPE/DATA/MATCH_REPORT constants define the Quake Live-owned envelope:

- `QL_ZMQ_PUBLICATION_TYPE_KEY`
- `QL_ZMQ_PUBLICATION_DATA_KEY`
- `QL_ZMQ_MATCH_REPORT_TYPE`

SRP also now names the portable JSON envelope formats used by the C
reconstruction:

- `QL_ZMQ_PUBLICATION_PAYLOAD_FORMAT`
- `QL_ZMQ_PUBLICATION_NULL_PAYLOAD_FORMAT`

`idZMQ_BuildPublication` now routes both payload-present and null-payload JSON
serialization through those format constants. `idZMQ_SubmitMatchReport` now
uses `QL_ZMQ_MATCH_REPORT_TYPE`, while `idZMQ_ReportPlayerEvent` continues to
forward the caller-provided event name directly. The live send remains the
existing dynamic `zmq_send` runtime path; retail `zstr_send` remains mapped
evidence and not implementation source.

## Validation

Completed 2026-06-15:

- `python -m pytest -q tests/test_platform_services.py -k zmq_stats_publication_envelope_boundary_round_664`
  - `1 passed, 209 deselected in 0.12s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `68 passed, 142 deselected in 1.41s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.16s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
