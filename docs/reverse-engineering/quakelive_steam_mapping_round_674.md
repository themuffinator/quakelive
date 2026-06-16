# Quake Live Steam Mapping Round 674: ZMQ Socket Option Boolean Boundary

Date: 2026-06-16

## Scope

This pass rechecked the socket option boolean boundary in the retained ZMQ
RCON and stats socket setup paths. Retail Quake Live uses embedded CZMQ helpers
to set ZAP domain, PLAIN server mode, and RCON-only ROUTER mandatory delivery.
SRP keeps the helper bodies external and dynamically calls libzmq option
setting through the reconstructed server-owned wiring.

Focused parity estimate: **before 91% -> after 98%** for socket option boolean
source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **98.7% -> 98.8%**. Repo-wide parity remains **99%**
because this pass closes a local socket-option source-shape gap without
changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401390` | `zmq_setsockopt` | High | Lower libzmq option setter used by the CZMQ wrappers. |
| `sub_4F5750` | `zsock_set_zap_domain` | High | Sets the RCON or stats ZAP domain before bind. |
| `sub_4F5790` | `zsock_set_plain_server` | High | Receives the password-present boolean for RCON and stats sockets. |
| `sub_4F5980` | `zsock_set_router_mandatory` | High | Enables ROUTER mandatory delivery for the RCON ROUTER socket. |

Observed Binary Ninja HLIL anchors:

- `004f40b8` sets the RCON ZAP domain to `rcon`.
- `004f40cb` branches on the RCON password string.
- `004f40d8` materializes disabled PLAIN server mode as `0`.
- `004f40d0` materializes enabled PLAIN server mode as `1`.
- `004f40db` calls the PLAIN server setter.
- `004f40e6` materializes ROUTER mandatory delivery as `1`.
- `004f40e9` calls the ROUTER mandatory setter.
- `004f4335` sets the stats ZAP domain to `stats`.
- `004f4348` branches on the stats password string.
- `004f4355` materializes disabled stats PLAIN server mode as `0`.
- `004f434d` materializes enabled stats PLAIN server mode as `1`.
- `004f4358` calls the stats PLAIN server setter.
- `004f57b1` maps PLAIN server mode to `zmq_setsockopt(..., 0x2c, ..., 4)`.
- `004f59cc` maps ROUTER mandatory delivery to
  `zmq_setsockopt(..., 0x21, ..., 4)`.

Observed fact: the retained Quake Live owner decides when those booleans are
enabled or disabled. The CZMQ/libzmq helper bodies remain dependency evidence,
not source to reconstruct.

## Source Reconstruction

SRP now names the socket option booleans:

- `QL_ZMQ_SOCKET_OPTION_DISABLED`
- `QL_ZMQ_SOCKET_OPTION_ENABLED`

The retained source boundary is:

- RCON always enables `QL_ZMQ_ROUTER_MANDATORY`.
- RCON enables `QL_ZMQ_PLAIN_SERVER` only when the retained RCON password
  buffer is non-empty.
- Stats enables `QL_ZMQ_PLAIN_SERVER` only when the retained stats password
  buffer is non-empty.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zsock_set_plain_server`, `zsock_set_router_mandatory`, or `zmq_setsockopt`
source bodies to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_socket_option_boolean_boundary_round_674`
  - `1 passed, 219 deselected in 7.51s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `76 passed, 143 deselected in 1.71s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.23s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
