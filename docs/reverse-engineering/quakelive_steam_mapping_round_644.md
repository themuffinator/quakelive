# quakelive_steam.exe Mapping Round 644

Date: 2026-06-15

Scope: focused ZMQ stats-publisher init wrapper pass for the retained `idZMQ`
host. This round stays in Quake Live server-owned wiring and keeps libzmq as
an external runtime dependency.

## Summary

This pass rechecked the retail stats PUB lifecycle around `sub_4F4210`,
`sub_4F43A0`, and `sub_4F3DD0`. Retail `Zmq_InitStatsPublisher` is a thin
tail-call wrapper into `idZMQ_InitStatsPublisher`; the initializer creates the
PUB socket only when stats are enabled and the retained socket slot is empty.
Shutdown, not init, owns PUB socket destruction.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3DD0` | `Zmq_ShutdownStatsPublisher` | High | Destroys the retained stats socket when it exists. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Creates the PUB socket only when `zmq_stats_enable > 0` and `this + 8 == 0`. |
| `sub_4F43A0` | `Zmq_InitStatsPublisher` | High | Tail-call wrapper into the retained stats-publisher initializer. |

## Observed Facts

- `sub_4F43A0` tailcalls `sub_4F4210(&data_5756fc)` and does not perform a
  socket destroy first.
- `sub_4F4210` gates creation with `zmq_stats_enable` and `this + 8 == 0`,
  then stores the new PUB socket at `this + 8`.
- `sub_4F3DD0` is the stats shutdown owner and calls the checked zsock destroy
  helper when the retained stats socket is non-null.
- The server spawn path still calls `Zmq_InitStatsPublisher` after Steam
  server key/value publication, so spawn-time stats setup is an idempotent
  ensure step rather than a forced rebind.

## Source Reconstruction

- Updated portable `Zmq_InitStatsPublisher` to call only
  `idZMQ_EnsureStatsPublisher()`.
- Removed the non-retail forced `idZMQ_CloseStatsTranscript()` and
  `idZMQ_CloseSocket( &s_zmq.pubSocket )` calls from the init wrapper. The
  wrapper now does not close and recreate an existing PUB socket.
- Left socket closure in the disabled-path helper and
  `Zmq_ShutdownStatsPublisher`, preserving SRP's default-disabled fallback
  transcript boundary without turning init into teardown.
- Did not reconstruct retail libzmq/CZMQ internals; this is retained
  Quake Live `idZMQ` wiring only.

## Confidence And Open Questions

Confidence is high for the wrapper ownership correction because it is
cross-checked against Binary Ninja HLIL, Ghidra function rows, aliases, retail
strings, current server-spawn wiring, and the existing Round 642 publication
lifecycle mapping. The source transcript fallback remains an intentional SRP
divergence for non-live builds.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_stats_init_idempotent_wrapper_round_644`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ stats init wrapper/source-shape confidence:
  **before 93% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 95.5% -> after 95.7%**.
- Repo-wide parity remains **99%** because this pass closes a local ZMQ
  lifecycle ownership gap without changing the strict-retail Windows
  replacement score.
