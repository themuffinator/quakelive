# quakelive_steam.exe Mapping Round 659

Date: 2026-06-15

Scope: focused ZMQ auth actor `VERBOSE` handshake boundary for the retained
`idZMQ` RCON and stats initialization paths. This round documents Quake
Live-owned wiring only and does not reconstruct libzmq/CZMQ internals.

## Summary

Retail shares one auth actor between RCON and stats. Both setup paths check
the retained auth slot, create `zactor_new(zauth, 0)` when it is empty, send
the actor the `VERBOSE` control command with `zstr_sendx`, wait for the actor
pipe with `zsock_wait`, and then call the password apply owner.

SRP intentionally keeps that boundary at the Quake Live integration layer. The
manual ZAP REP socket remains the portable stand-in for retail's embedded CZMQ
`zauth` actor: it binds `inproc://zeromq.zap.01`, marks the retained auth owner
ready after bind, reapplies passwords, and pumps ZAP frames through the
external libzmq symbols that the build/runtime install lane provides.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | RCON setup creates the shared auth actor before constructing the ROUTER socket. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Stats setup shares the same auth actor creation and password-apply path. |
| `sub_4F5630` | `zsock_wait` | High | Waits for the actor acknowledgement after `VERBOSE`; also used by the actor constructor. |
| `sub_4F5A30` | `zactor_new` | High | CZMQ actor constructor that allocates the actor wrapper and starts the actor thread suspended. |
| `sub_4F5B50` | `zactor_destroy` | High | Destroys the retained auth actor during runtime shutdown. |
| `sub_4F5DB0` | `zstr_sendx` | High | Sends actor control commands such as `VERBOSE`. |
| `sub_4F69F0` | `zauth` | High | Actor body that owns the ZAP REP socket loop. |

## Observed Facts

- `sub_4F3F80` calls `sub_4F5A30(sub_4F69F0, 0)`, stores the returned actor
  at `arg1 + 4`, prepares the literal `VERBOSE`, calls `sub_4F5DB0`, waits via
  `sub_4F5630`, and then calls `sub_4F3D70(arg1)`.
- `sub_4F4210` repeats the same null-auth-slot guard and `VERBOSE` handshake
  before the stats PUB socket path.
- `sub_4F5A30` carries CZMQ `zactor.c` provenance: wrapper allocation failure
  reports line `0x66`, thread-args allocation failure reports line `0x6a`,
  the actor magic is `0x5cafe`, and the constructor waits on the actor pipe
  before returning.
- The actor thread shim destroys the pipe with checked source metadata from
  `..\..\..\..\src\zactor.c` line `0x58` before freeing the thread args.
- `sub_4F69F0` builds the `zauth` self object, signals readiness on the actor
  pipe, dispatches pipe or ZAP traffic, and finally destroys the auth state.

Observed fact: the retail actor machinery belongs to embedded CZMQ/libzmq
support code compiled into `quakelive_steam.exe`, while the RCON/stats setup
sites are Quake Live `idZMQ` integration owners.

Inferred source boundary: SRP should record the actor command/provenance shape
and preserve the ready/apply ordering, but it should not vendor or rewrite
`zactor`, `zauth`, `zsock_wait`, or `zstr_sendx`.

## Source Reconstruction

- Added source constants for the retail actor commands `VERBOSE` and `PLAIN`
  so future password/auth work has named anchors for the CZMQ control lane.
- Added source constants for the retail `zactor.c` provenance lines, including
  the `0x5cafe` actor magic and the thread-pipe destroy/allocation line
  numbers.
- Annotated `idZMQ_EnsureAuthSocket` with the intentional boundary: SRP binds a
  manual ZAP REP socket and then applies passwords instead of reconstructing
  the CZMQ `zauth` actor.
- Added a focused parity gate that cross-checks aliases, Ghidra function rows,
  Binary Ninja HLIL call sites, source constants, and the absence of direct
  CZMQ actor calls in `sv_zmq.c`.

## Confidence And Open Questions

Confidence is high because the two Quake Live setup paths, promoted aliases,
Ghidra function rows, HLIL literals, actor constructor internals, and current
source all agree on the same boundary. The remaining divergence is explicit
and policy-aligned: SRP uses the external libzmq runtime install and a compact
manual ZAP socket rather than reconstructing embedded CZMQ actor internals.

Open question: no further runtime probe is needed for this mapping pass. A
future live ZMQ test can validate authenticated RCON/stats behavior once the
external `libzmq.dll` test fixture is available in a controlled environment.

## Validation

- `python -m pytest -q tests/test_platform_services.py -k zmq_auth_actor_verbose_handshake_boundary_round_659`
  - `1 passed, 204 deselected in 6.34s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `63 passed, 142 deselected in 1.13s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.14s`
- `git diff --check`
  - Clean, with existing CRLF normalization warnings only.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`

## Parity Estimate

- Focused auth actor handshake/source-boundary confidence:
  **before 92% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 97.4% -> after 97.5%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ actor-handshake evidence gap without changing the strict-retail Windows
  replacement score.
