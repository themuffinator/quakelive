# Quake Live Steam Mapping Round 697: ZMQ Cvar Flag Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ cvar flag boundary in the retained server-owned
`idZMQ` wiring. Retail Quake Live registers the six non-password `zmq_*`
control cvars with the init-only flag value `0x10`, registers the two password
cvars with archived flag value `1`, and uses the latched `net_*` fallback flag
value `0x20` while building the stats endpoint.

Focused parity estimate: **before 94% -> after 99%** for cvar flag
source-boundary confidence. Focused ZMQ wiring/source reconstruction confidence
moves from **99.35% -> 99.4%**. Repo-wide parity remains **99%** because this
pass names a local server integration flag boundary without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4CE0D0` | `Cvar_Get` | High | Retail cvar registration/fallback helper. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Registers the `zmq_*` cvars and initializes RCON. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Uses net fallback cvars while resolving the stats endpoint. |

Observed Binary Ninja HLIL anchors:

- `004f3fa0` registers `zmq_rcon_enable` with flag `0x10`.
- `004f3fb6` registers `zmq_stats_enable` with flag `0x10`.
- `004f3fcc` registers `zmq_rcon_ip` with flag `0x10`.
- `004f3fe2` registers `zmq_rcon_port` with flag `0x10`.
- `004f3ff8` registers `zmq_stats_ip` with flag `0x10`.
- `004f4011` registers `zmq_stats_port` with flag `0x10`.
- `004f4027` registers `zmq_stats_password` with flag `1`.
- `004f4031` registers `zmq_rcon_password` with flag `1`.
- `004f42af` reads `net_ip` with flag `0x20`.
- `004f430a` reads `net_port` with flag `0x20`.

Observed fact: these are Quake Live `idZMQ` integration cvar flags, not
libzmq/CZMQ implementation details.

Inference: SRP should keep the engine macro values (`CVAR_INIT`,
`CVAR_ARCHIVE`, and `CVAR_LATCH`) but name their ZMQ call-site roles so the
retail `0x10`/`1`/`0x20` split remains reviewable.

## Source Reconstruction

The cvar flag boundary is now named in source:

- `QL_ZMQ_CVAR_INIT_FLAGS`
- `QL_ZMQ_CVAR_PASSWORD_FLAGS`
- `QL_ZMQ_CVAR_NET_FALLBACK_FLAGS`

`idZMQ_RegisterCvarsAndInitRcon` routes all six non-password `zmq_*` cvars
through `QL_ZMQ_CVAR_INIT_FLAGS` and both password cvars through
`QL_ZMQ_CVAR_PASSWORD_FLAGS`. The stats endpoint fallback reads `net_ip` and
`net_port` through `QL_ZMQ_CVAR_NET_FALLBACK_FLAGS`.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zsock_new_checked`, `zsock_bind`, or other lower helper bodies to the
repository.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_cvar_flag_boundary_round_697 --tb=short` - 1 passed, 235 deselected.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short` - 86 passed, 150 deselected.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short` - 2 passed, 1 skipped.
- `rg --files src/libs/libzmq` - only `src/libs/libzmq\README.md`.
- `git diff --check` - passed.
