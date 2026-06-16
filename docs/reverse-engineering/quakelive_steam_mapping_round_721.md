# Quake Live Steam Mapping Round 721: ZMQ Endpoint IP Scratch-Buffer Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ endpoint IP scratch-buffer boundary in SRP's retained
server-owned `idZMQ` wiring. Retail Quake Live builds RCON and stats endpoints
around `va("tcp://%s:%i")`; the SRP dynamic-runtime path uses bounded local
buffers while copying direct cvar strings, defaults, and the stats `net_ip`
fallback into the final endpoint format.

Focused parity estimate: **before 94% -> after 99%** for endpoint IP
scratch-buffer source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.45% -> 99.5%**. Repo-wide parity
remains **99%** because this pass names an SRP portability buffer without
changing the strict-retail Windows replacement score.

## Evidence

ZMQ endpoint IP scratch-buffer boundary alias cross-check:

| Symbol | Alias |
| --- | --- |
| `sub_4D9160` | `Com_sprintf` |
| `sub_4D9220` | `va` |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` |

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4D9160` | `Com_sprintf` | High | Retail bounded string formatting helper. |
| `sub_4D9220` | `va` | High | Retail temporary formatted-string helper used for endpoints. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Registers ZMQ cvars and initializes RCON. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Resolves stats host and endpoint before binding the PUB socket. |

Observed Binary Ninja HLIL anchors:

- `004f4090` reads the RCON port cvar integer.
- `004f4091` reads the RCON IP cvar string.
- `004f4097` formats the RCON endpoint with `va("tcp://%s:%i")`.
- `004f42af` reads the `net_ip` fallback with flag `0x20`.
- `004f42d3` formats the parsed IPv4 fallback with `Com_sprintf(..., 0x10,
  "%i.%i.%i.%i")`.
- `004f4317` formats the stats endpoint with `va("tcp://%s:%i")`.

Observed fact: retail's endpoint strings and cvar fallbacks are Quake Live
`idZMQ` integration behavior. Retail's embedded libzmq/CZMQ implementation is
evidence for socket behavior, not source to reconstruct in SRP.

Inference: the SRP portable endpoint buffer is a local adaptation for the
dynamic runtime implementation. It should be named and pinned separately from
the retail embedded CZMQ/libzmq bodies.

## Source Reconstruction

`QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE` now names the 64-byte local endpoint IP
workspace used by `idZMQ_ResolveRconEndpoint` and
`idZMQ_ResolveStatsEndpoint`.

RCON endpoint resolution copies either the `zmq_rcon_ip` cvar or the
`0.0.0.0` default into that workspace before final endpoint formatting. Stats
endpoint resolution routes the same SRP portable endpoint buffer through
`idZMQ_ResolveStatsHost`, which preserves the retail cvar/fallback behavior
and IPv4 formatting evidence before final endpoint formatting.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zsock_new_checked`, `zsock_bind`, `zstr_*`, `zauth`, or lower `zmq::*` source
bodies to the repository.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_endpoint_ip_scratch_buffer_round_721 --tb=short` - 1 passed, 259 deselected.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short` - 88 passed, 172 deselected.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short` - 2 passed, 1 skipped.
- `rg --files src/libs/libzmq` - only `src/libs/libzmq\README.md`.
- `git diff --check` - passed with pre-existing LF-to-CRLF warnings.
