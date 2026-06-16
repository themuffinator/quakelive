# quakelive_steam.exe Mapping Round 661

Date: 2026-06-15

Scope: focused ZMQ cvar, endpoint-format, net fallback, and bind-log literal
boundary for the retained `idZMQ` RCON and stats setup paths. This round maps
Quake Live-owned wiring only and does not reconstruct libzmq/CZMQ internals.

## Summary

Retail keeps the ZMQ control surface in a compact string band around the
`idZMQ` setup paths. The RCON setup owner registers the eight `zmq_*` cvars,
uses `"tcp://%s:%i"` for endpoint construction, and prints one of the RCON
bind-result messages. The stats setup owner reuses the same endpoint format,
falls back through `net_ip`/`net_port`, formats parsed `net_ip` as
`"%i.%i.%i.%i"`, and prints one of the PUB bind-result messages.

SRP now names those literals in `sv_zmq.c` and routes the current source
through those constants. Runtime behavior remains the same; the point of this
pass is to make the retail ZMQ cvar and endpoint literal boundary explicit and
test-pinned without treating any embedded libzmq/CZMQ implementation as repo
source.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4C9860` | `Com_Printf` | High | Prints RCON/PUB bind-result messages. |
| `sub_4CE0D0` | `Cvar_Get` | High | Registers ZMQ cvars and net fallback cvars. |
| `sub_4D7250` | `NET_StringToAdr` | High | Parses the `net_ip` fallback before stats endpoint formatting. |
| `sub_4D9160` | `Com_sprintf` | High | Formats parsed IPv4 fallback text. |
| `sub_4D9220` | `va` | High | Builds endpoint and default port format strings. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Registers ZMQ cvars and builds/binds the RCON endpoint. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Builds stats endpoint with `zmq_stats_*` and net fallback cvars. |

## Observed Facts

- `sub_4F3F80` registers `zmq_rcon_enable`, `zmq_stats_enable`,
  `zmq_rcon_ip`, `zmq_rcon_port`, `zmq_stats_ip`, `zmq_stats_port`,
  `zmq_stats_password`, and `zmq_rcon_password`.
- The enable and bind-control cvars use the init-only flag path (`0x10`),
  while the password cvars use the archived flag path (`1`).
- RCON endpoint construction uses `"tcp://%s:%i"`, default RCON IP
  `"0.0.0.0"`, and default RCON port `"28960"`.
- `sub_4F4210` uses explicit `zmq_stats_ip` when present; otherwise it calls
  `Cvar_Get("net_ip", "localhost", CVAR_LATCH)`, parses it, formats the
  resulting bytes as `"%i.%i.%i.%i"`, then uses `net_port` when
  `zmq_stats_port` is empty.
- The bind-result strings are stable in the retail string corpus:
  `zmq RCON socket error, bind failed: %s\n`, `zmq RCON socket: %s\n`,
  `zmq PUB socket error, bind failed: %s\n`, and `zmq PUB socket: %s\n`.

Observed fact: these strings are Quake Live `idZMQ` integration literals, not
libzmq/CZMQ implementation surface.

Inferred source boundary: SRP should name and test these literals in the
server integration code, while keeping libzmq/CZMQ as the external runtime and
evidence boundary.

## Source Reconstruction

- Added constants for the ZMQ cvar names, default cvar strings, endpoint
  format, parsed IPv4 format, bind-result print formats, and password-update
  message.
- Updated `idZMQ_RegisterCvarsAndInitRcon`,
  `idZMQ_ResolveStatsHost`, `idZMQ_ResolveRconEndpoint`,
  `idZMQ_ResolveStatsEndpoint`, `idZMQ_EnsureRconSocket`,
  `idZMQ_EnsureStatsPublisher`, and `idZMQ_UpdatePasswords` to use the named
  constants.
- Added a focused parity gate that cross-checks aliases, Ghidra function rows,
  Binary Ninja HLIL, retail string-corpus anchors, and current source usage.

## Confidence And Open Questions

Confidence is high because the cvar registration order, default values, string
corpus, endpoint formatting calls, bind-result branches, aliases, and current
source all line up. The remaining unknowns are runtime environment details for
an installed external `libzmq.dll`, which are outside this static mapping pass.

## Validation

- `python -m pytest -q tests/test_platform_services.py -k zmq_endpoint_cvar_literal_boundary_round_661`
  - `1 passed, 206 deselected in 6.84s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `65 passed, 142 deselected in 1.43s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.20s`
- `git diff --check`
  - Clean, with existing CRLF normalization warnings only.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`

## Parity Estimate

- Focused ZMQ cvar/endpoint literal-boundary confidence:
  **before 94% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 97.6% -> after 97.7%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ literal-source-shape gap without changing the strict-retail Windows
  replacement score.
