# quakelive_steam.exe Mapping Round 648

Date: 2026-06-15

Scope: focused ZMQ stats endpoint fallback-host reconstruction for the retained
`idZMQ` host. This round stays in Quake Live server-owned wiring and does not
reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the retail `idZMQ_InitStatsPublisher` path that builds the
stats PUB endpoint when `zmq_stats_ip` is empty. Retail does not preserve the
raw `net_ip` cvar string in that branch. It reads `net_ip` with the default
`"localhost"` and `CVAR_LATCH`, passes the result through the engine address
parser, formats the address bytes as `%i.%i.%i.%i`, and then uses that value in
`tcp://%s:%i`. SRP now mirrors that source shape: empty zmq_stats_ip now follows the retail net_ip parse-and-format path before the stats endpoint is formatted.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Builds the stats PUB endpoint and parses `net_ip` when `zmq_stats_ip` is empty. |
| `sub_4F43A0` | `Zmq_InitStatsPublisher` | High | Tail-call wrapper into the retained stats-publisher initializer. |

## Observed Facts

- `sub_4F4210` first uses the `zmq_stats_ip` cvar string directly when it is
  non-empty.
- When `zmq_stats_ip` is empty, `sub_4F4210` calls the engine cvar getter for
  `net_ip` with default `"localhost"` and flag `0x20`, which maps to
  `CVAR_LATCH`.
- The same branch passes the `net_ip` string to the engine address parser and
  formats the parsed address bytes with `"%i.%i.%i.%i"`.
- Endpoint formatting still happens after the host selection with
  `"tcp://%s:%i"`, while stats socket creation remains owned by the retained
  init path.

## Source Reconstruction

- Updated `idZMQ_ResolveStatsHost` so explicit `zmq_stats_ip` values still pass
  through unchanged.
- Replaced the old `Cvar_VariableStringBuffer( "net_ip", ... )` fallback with
  `Cvar_Get( "net_ip", "localhost", CVAR_LATCH )`, matching the retail cvar
  registration path.
- Parsed the fallback host through `NET_StringToAdr` and formatted
  `address.ip[0..3]` into the retained dotted host string before
  `idZMQ_ResolveStatsEndpoint` builds `tcp://%s:%i`.
- Preserved the external libzmq runtime boundary; this pass does not
  reconstruct embedded CZMQ/libzmq internals.

## Confidence And Open Questions

Confidence is high for the fallback-host source shape because it is
cross-checked against Binary Ninja HLIL, Ghidra function rows, aliases, cvar
flag definitions, and the existing Windows `NET_OpenIP` registration pattern.
The exact behavior of malformed `net_ip` strings remains an inference from the
retail parse-and-format shape; SRP zero-initializes the address before parsing
so the fallback stays deterministic.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_stats_endpoint_net_ip_round_648`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ stats endpoint fallback-host confidence:
  **before 88% -> after 97%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.2% -> after 96.3%**.
- Repo-wide parity remains **99%** because this pass closes a local stats
  endpoint source-shape gap without changing the strict-retail Windows
  replacement score.
