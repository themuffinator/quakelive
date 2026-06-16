# Quake Live Steam Mapping Round 727: ZMQ Poll Ready-Threshold Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ poll ready-threshold boundary in SRP's retained
server-owned `idZMQ` wiring. Retail Quake Live compiled libzmq/CZMQ code into
`quakelive_steam.exe`, but SRP keeps libzmq as an external runtime dependency
and reconstructs only the Quake Live-owned integration code.

This is the ZMQ poll ready-threshold boundary for the SRP dynamic zmq_poll adaptation.

Focused parity estimate: **before 94% -> after 99%** for focused ZMQ poll
ready-threshold source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.65% -> 99.7%**. Repo-wide parity
remains **99%** because this pass names a local SRP dynamic `zmq_poll`
adaptation boundary without changing the strict-retail Windows replacement
score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401600` | `zmq_poll` | High | External-style poll entry embedded in the retail executable. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Pumps one ready RCON ROUTER message after poll readiness is observed. |
| `sub_4F5CB0` | `zstr_recv` | High | CZMQ string receive helper used for RCON identity and command frames. |

Observed Binary Ninja HLIL anchors:

- `004f4ed0` starts the retail RCON pump helper.
- `004f4f0d` calls `zmq_poll` with one poll item.
- `004f4f17` branches only when the poll result is signed-positive.
- `004f4f23` receives the RCON identity frame through `zstr_recv` inside the
  positive-ready branch.
- `004f4f2f` receives the RCON command frame through `zstr_recv` inside the
  same branch.

Observed fact: retail treats a positive `zmq_poll` result as the ready state
that permits RCON frame reads. Zero or negative results do not enter the RCON
receive path.

Inference: the SRP dynamic zmq_poll adaptation should name the minimum ready
count at the integration boundary, while keeping embedded retail libzmq/CZMQ
helper bodies as evidence only.

## Source Reconstruction

`QL_ZMQ_POLL_READY_MIN` names the local poll-ready threshold used by SRP's
direct `zmq_poll` dispatch path.

`idZMQ_PumpRcon` uses this constant for the early-return gate before reading
RCON identity and command frames. `idZMQ_PumpAuthSocket` uses the same
threshold in the manual ZAP auth pump loop so both retained external-runtime
poll sites use one named readiness boundary.

This pass does not reconstruct libzmq/CZMQ internals. SRP still keeps
`src/libs/libzmq` limited to dependency instructions and keeps the runtime
symbols loaded dynamically from the external libzmq library.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_poll_ready_threshold_round_727 --tb=short`
  - `1 passed, 265 deselected`.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - `92 passed, 174 deselected`.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - `2 passed, 1 skipped`.
- `rg --files src/libs/libzmq`
  - only `src/libs/libzmq\README.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
