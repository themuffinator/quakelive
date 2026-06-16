# Quake Live Steam Mapping Round 691: ZMQ Endpoint Empty-Clear Boundary

Date: 2026-06-16

## Scope

This pass rechecked the retained ZMQ endpoint-buffer clear points in SRP's
server-owned `idZMQ` wiring. This ZMQ endpoint empty-clear boundary sits where
retail Quake Live separates stats PUB shutdown from RCON/runtime shutdown, and
SRP mirrors that split while also clearing the portable endpoint strings used
by its external-libzmq accommodation.

Focused parity estimate: **before 92% -> after 98%** for endpoint empty-clear
source-boundary confidence. Focused ZMQ wiring/source reconstruction confidence
moves from **99.25% -> 99.3%**. Repo-wide parity remains **99%** because this
pass names a local retained endpoint-buffer reset boundary without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3DD0` | `Zmq_ShutdownStatsPublisher` | High | Stats PUB shutdown owner. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | High | RCON/runtime shutdown owner. |
| `sub_4F5080` | `idZMQ_Destroy` | High | Retained object destructor analogue used by SRP's disabled-RCON cleanup. |
| `sub_4F5190` | `zsock_destroy_checked` | High | Retail checked CZMQ socket destroy helper; source body remains external evidence. |

Observed Binary Ninja HLIL anchors:

- `004f3dd0` begins the stats publisher shutdown wrapper.
- `004f3dd7` checks the retained stats PUB slot.
- `004f3de5` destroys the stats socket with `zsock_destroy_checked` and retail
  source line `0x73`.
- `004f3df0` begins the runtime shutdown wrapper.
- `004f3df7` checks the retained RCON socket slot.
- `004f3e08` clears the resolved RCON poll slot.
- `004f3e12` destroys the RCON socket with `zsock_destroy_checked` and retail
  source line `0xe2`.

Observed fact: retail owns distinct stats and RCON shutdown lanes. SRP keeps
the same owner split and additionally clears its retained endpoint buffers when
those lanes are disabled or shut down.

Inference: endpoint-buffer emptying is SRP's portable source boundary for the
retained endpoint strings around the retail socket lifetime split. Naming the
terminator makes that boundary auditable without reconstructing
`zsock_destroy_checked`, `zsock_destroy`, or other CZMQ/libzmq helpers.

## Source Reconstruction

The endpoint empty-clear boundary is now named in source:

- `QL_ZMQ_ENDPOINT_EMPTY`

The retained source boundary is:

- Disabled RCON cleanup clears `s_zmq.rconEndpoint` through
  `QL_ZMQ_ENDPOINT_EMPTY` after closing the RCON socket and resolved poll slot.
- Disabled stats cleanup clears `s_zmq.statsEndpoint` through
  `QL_ZMQ_ENDPOINT_EMPTY` after closing the transcript and PUB socket.
- `Zmq_ShutdownStatsPublisher` clears only the stats endpoint.
- `Zmq_ShutdownRuntime` clears only the RCON endpoint and keeps stats shutdown
  separate.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zsock_destroy_checked`, `zsock_destroy`, or lower libzmq source bodies to the
repository.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq_endpoint_empty_clear_boundary_round_691 --tb=short` - 1 passed, 231 deselected.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short` - 84 passed, 148 deselected.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short` - 2 passed, 1 skipped.
- `rg --files src/libs/libzmq` - only `src/libs/libzmq\README.md`.
- `git diff --check` - passed.
