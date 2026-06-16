# quakelive_steam.exe Mapping Round 641

Date: 2026-06-15

Scope: focused ZMQ player-event publication wrapper pass for the retained
`idZMQ` host. This round stays in Quake Live server-owned wiring and does not
reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the retail `SV_ReportPlayerEvent -> Zmq_ReportPlayerEvent
-> idZMQ_ReportPlayerEvent` chain against the current portable source. Retail
`sub_4F4E10` forwards `arg1` directly as the ZMQ `TYPE` and `arg2` as `DATA`
into `sub_4F4B20`; there is no observed fallback event-type literal in the
retail wrapper. SRP now mirrors that source shape by forwarding `eventName`
directly to the common publisher and removing the synthetic `"UNKNOWN_EVENT"`
substitution.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4E2640` | `SV_ReportPlayerEvent` | High | Calls the Steam stats side effect first, then forwards the same arguments to ZMQ. |
| `sub_4F4E10` | `Zmq_ReportPlayerEvent` | High | Public wrapper forwards `arg1`/`arg2` into the retained `idZMQ` instance. |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | High | Builds the JSON-like object using wrapper `arg2` as `TYPE` and `arg3` as `DATA`. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | High | Companion publisher with the hardcoded `MATCH_REPORT` type. |
| `sub_4F4E40` | `Zmq_SubmitMatchReport` | High | Public match-report wrapper into the retained `idZMQ` instance. |

## Observed Facts

- `sub_4E2640` calls `sub_468030(arg1, arg2, arg3)` before returning through
  `sub_4F4E10(arg1, arg2, arg3, arg4, arg5)`, preserving the Steam-stats
  side effect before ZMQ publication.
- `sub_4F4E10` spills the trailing arguments but returns
  `sub_4F4B20(&data_5756fc, arg1, arg2)`, so the ZMQ wrapper uses the first two
  event arguments directly.
- `sub_4F4B20` only publishes when the stats PUB socket at `this + 8` exists.
  When it does publish, the JSON builder inserts `arg2` under `TYPE` and
  `arg3` under `DATA`.
- The adjacent `sub_4F4C30` match-report publisher hardcodes `MATCH_REPORT`,
  confirming that dynamic player-event names and the fixed match-report type
  are separate source shapes.
- The retail string table contains `TYPE`, `DATA`, and `MATCH_REPORT`, but no
  `UNKNOWN_EVENT` fallback literal in this publication band.

## Source Reconstruction

- Updated `Zmq_ReportPlayerEvent` to pass `eventName` directly into
  `idZMQ_Publish`.
- Removed the source-level `"UNKNOWN_EVENT"` substitution from the retained ZMQ
  publication lane.
- Added a guard in `idZMQ_Publish` so missing event types safely no-op in the C
  reconstruction instead of formatting a null `%s`. This preserves the retail
  direct-forwarding shape while keeping SRP's portable path robust.
- Kept `Zmq_SubmitMatchReport` hardcoded to `MATCH_REPORT`, matching the
  companion retail publisher.

## Confidence And Open Questions

Confidence is high for the source-shape change because the wrapper chain is
cross-checked against Binary Ninja HLIL, Ghidra function rows, existing aliases,
and retail string evidence. The only intentional portability guard is the
missing-type no-op in `idZMQ_Publish`; retail appears to rely on valid event
names from callers.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_player_event_type_forwarding_round_641`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ player-event wrapper source-shape confidence:
  **before 93% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 94.9% -> after 95.1%**.
- Repo-wide parity remains **99%** because this closes a local publication
  wrapper gap without changing the strict-retail Windows replacement score.
