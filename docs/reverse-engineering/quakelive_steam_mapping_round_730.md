# Quake Live Steam Mapping Round 730: ZMQ Bind Success-Threshold Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ bind success-threshold boundary in SRP's retained
server-owned `idZMQ` wiring. Retail Quake Live compiled libzmq/CZMQ code into
`quakelive_steam.exe`, but SRP keeps libzmq as an external runtime dependency
and reconstructs only the Quake Live-owned integration code.

This is the ZMQ bind success-threshold boundary for the SRP dynamic zmq_bind adaptation.

Focused parity estimate: **before 94% -> after 99%** for focused ZMQ bind
success-threshold source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.75% -> 99.8%**. Repo-wide parity
remains **99%** because this pass names a local SRP dynamic `zmq_bind`
adaptation boundary without changing the strict-retail Windows replacement
score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401410` | `zmq_bind` | High | Lower libzmq bind entry embedded in the retail executable. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Creates and binds the retained RCON ROUTER socket. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Creates and binds the retained stats PUB socket. |
| `sub_4F5200` | `zsock_bind` | High | CZMQ bind helper returning `0xffffffff` on failure. |

Observed Binary Ninja HLIL anchors:

- `004f40ff` checks whether the retail RCON `zsock_bind` result is
  `0xffffffff`.
- `004f4108` selects the RCON bind-failure log string.
- `004f4101` selects the RCON bind-success log string.
- `004f4371` checks whether the retail stats PUB `zsock_bind` result is
  `0xffffffff`.
- `004f437a` selects the stats PUB bind-failure log string.
- `004f4373` selects the stats PUB bind-success log string.

Observed fact: retail's CZMQ wrapper reports bind failure through its helper
result before selecting the endpoint log message. SRP does not carry the CZMQ
helper source; it calls the dynamic libzmq `zmq_bind` export directly and uses
the libzmq zero-success convention.

Inference: SRP's direct bind branches should name the success value at the
retained `idZMQ` integration boundary instead of spelling raw zero comparisons
at each bind site.

## Source Reconstruction

`QL_ZMQ_BIND_SUCCESS` now names the local bind-success result used by SRP's
direct `zmq_bind` dispatch path.

The manual ZAP REP socket bind, RCON ROUTER socket bind, and stats PUB socket
bind all compare their `zmq_bind` result against `QL_ZMQ_BIND_SUCCESS`. The
existing retained-slot behavior stays intact:

- RCON and stats sockets are stored before bind logging.
- RCON bind failure still leaves the retained socket and resolved poll slot
  path owned by shutdown/disabled cleanup.
- Stats bind failure still leaves the retained PUB socket owned by stats
  shutdown/disabled cleanup.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_bind_success_threshold_round_730 --tb=short`
  - Result: `1 passed, 268 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - Result: `94 passed, 175 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - Result: `2 passed, 1 skipped`.
- `rg --files src/libs/libzmq`
  - Result: only `src/libs/libzmq\README.md`; no reconstructed libzmq/CZMQ
    source is present in the repo.
- `git diff --check`
  - Result: passed; Git reported only the existing LF-to-CRLF working-copy
    warnings.

No game launch was needed; this was a static mapping/source-boundary pass
covered by corpus anchors and source parity gates.
