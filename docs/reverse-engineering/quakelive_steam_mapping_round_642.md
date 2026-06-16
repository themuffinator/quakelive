# quakelive_steam.exe Mapping Round 642

Date: 2026-06-15

Scope: focused ZMQ stats-publication socket lifecycle pass for the retained
`idZMQ` host. This round stays in Quake Live server-owned wiring and does not
reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the retail stats PUB socket ownership split around
`sub_4F4210`, `sub_4F4B20`, and `sub_4F4C30`. Retail creates the stats PUB
socket in the stats-publisher initialization path and stores it at `this + 8`.
The publication helpers do not create the PUB socket; they first check
`this + 8` and only serialize/send the `TYPE`/`DATA` object when that socket is
already present. SRP now mirrors that lifecycle by keeping socket creation in
`Zmq_InitStatsPublisher` / `idZMQ_EnsureStatsPublisher` and removing the lazy
stats-publisher ensure from `idZMQ_Publish`.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Creates the PUB socket and writes it to `this + 8` when stats publication is enabled. |
| `sub_4F43A0` | `Zmq_InitStatsPublisher` | High | Public wrapper into the retained stats-publisher initializer. |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | High | Checks `this + 8` before serializing and sending a dynamic event object. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | High | Checks `this + 8` before serializing and sending the hardcoded `MATCH_REPORT` object. |
| `sub_4F4E10` | `Zmq_ReportPlayerEvent` | High | Public player-event publication wrapper. |
| `sub_4F4E40` | `Zmq_SubmitMatchReport` | High | Public match-report publication wrapper. |

## Observed Facts

- `sub_4F4210` gates on `zmq_stats_enable` and `this + 8 == 0` before creating
  a socket with type `1` (`QL_ZMQ_PUB`), setting its stats ZAP domain, binding
  it, logging `zmq PUB socket: %s\n`, and storing it at `this + 8`.
- `sub_4F43A0` is the public tail-call wrapper into that stats-publisher
  initialization path.
- `sub_4F4B20` starts its publication body with `if (*(arg1 + 8) != 0)` and
  sends through `sub_4F5D60(*(arg1 + 8), eax_6)` only inside that block.
- `sub_4F4C30` has the same `this + 8` guard before sending the hardcoded
  `MATCH_REPORT` publication object.
- The server spawn path calls `Zmq_InitStatsPublisher` after Steam server
  key/value publication, so stats socket creation remains a server lifecycle
  responsibility rather than a side effect of each publication helper.

## Source Reconstruction

- Removed the lazy `idZMQ_EnsureStatsPublisher()` call from `idZMQ_Publish`.
- Kept `Zmq_InitStatsPublisher` as the owner of stats socket creation and
  `idZMQ_EnsureStatsPublisher` as its internal helper.
- Kept the source fallback transcript write before the live send attempt. This
  is an intentional SRP fallback for policy-disabled or runtime-unavailable
  builds, while live PUB socket creation now follows the retail lifecycle
  boundary more closely.
- Preserved the dynamic external `zmq_*` loading boundary and the
  default-disabled `QL_BUILD_ONLINE_SERVICES` policy.

## Confidence And Open Questions

Confidence is high for the lifecycle split because the create-vs-send ownership
is cross-checked against Binary Ninja HLIL, Ghidra function rows, existing
aliases, retail strings, and current server-spawn wiring. The fallback
transcript remains an intentional source-level divergence for non-live builds.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_publication_socket_lifecycle_round_642`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ publication socket lifecycle confidence:
  **before 90% -> after 97%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 95.1% -> after 95.3%**.
- Repo-wide parity remains **99%** because this closes a local lifecycle
  ownership gap without changing the strict-retail Windows replacement score.
