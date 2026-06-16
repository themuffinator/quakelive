# Quake Live Steam Mapping Round 671: ZMQ Stats Default Port Format Boundary

Date: 2026-06-16

## Scope

This pass rechecked the stats PUB endpoint default-port path in the retained
ZMQ integration. Retail Quake Live uses the explicit `zmq_stats_port` cvar when
it is non-zero; otherwise it falls back to the latched `net_port` cvar with a
default string produced from `PORT_SERVER`. SRP already matched the behavior,
and this round names the `%i` default-port format used by the fallback.

Focused parity estimate: **before 91% -> after 98%** for stats default port
format/source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **98.5% -> 98.6%**. Repo-wide parity remains **99%**
because this pass closes a local endpoint-format source-shape gap without
changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4CE0D0` | `Cvar_Get` | High | Reads `net_port` with the latched flag when `zmq_stats_port` has no integer value. |
| `sub_4D9160` | `Com_sprintf` | High | Formats the final endpoint through the retained `tcp://%s:%i` endpoint string. |
| `sub_4D9220` | `va` | High | Produces the default string from the `%i` format storage before `Cvar_Get`. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Owns the stats PUB endpoint construction and socket bind. |
| `sub_4F43A0` | `Zmq_InitStatsPublisher` | High | Public wrapper into the retained stats-publisher initializer. |

Observed Binary Ninja HLIL anchors:

- `004f42e4` reads the `zmq_stats_port` integer slot.
- `004f42e9` branches into the fallback path when that value is zero.
- `004f42ed` materializes `0x6d38`, matching `PORT_SERVER` (`27960`).
- `004f430a` calls `Cvar_Get("net_port", va(&data_52e930), 0x20)`.
- `004f4317` formats the endpoint with `tcp://%s:%i`.
- `004f43a0` is the public wrapper into the stats initializer.

Observed string/table anchors:

- `0052ca8c`: `net_port`
- `0052e930`: `%i`
- `005482a8`: `zmq_stats_port`
- `00548274`: `tcp://%s:%i`

Observed fact: the fallback default string is a Quake Live/server endpoint
wiring detail. It does not require reconstructing the embedded libzmq/CZMQ
implementation.

## Source Reconstruction

This stats default port format boundary is now named in source instead of
leaving the fallback `va` format literal inline.

SRP now names the stats default-port format:

- `QL_ZMQ_DEFAULT_NET_PORT_FORMAT`

The retained source boundary is:

- `idZMQ_ResolveStatsEndpoint` still uses `s_zmqStatsPort->integer` when
  `zmq_stats_port` is present.
- Empty `zmq_stats_port` falls back to
  `Cvar_Get( QL_ZMQ_CVAR_NET_PORT, va( QL_ZMQ_DEFAULT_NET_PORT_FORMAT, PORT_SERVER ), CVAR_LATCH )`.
- The final endpoint still uses `QL_ZMQ_ENDPOINT_FORMAT`.

This pass does not reconstruct libzmq/CZMQ internals and does not add libzmq
source to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_stats_default_port_format_boundary_round_671`
  - `1 passed, 216 deselected in 0.12s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `74 passed, 143 deselected in 1.64s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.20s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
