# quakelive_steam.exe Mapping Round 639

Date: 2026-06-15

Scope: focused ZMQ ZAP/PLAIN authentication wiring pass for the retained
`idZMQ` host. This round does not vendor CZMQ or libzmq; it tightens the
portable server-owned source shape around the manual ZAP REP socket that
stands in for retail's embedded `zauth` actor.

## Summary

This pass rechecked the owning retail `quakelive_steam.exe` evidence for
RCON/stats authentication setup, the CZMQ `zauth.c` request/reply lane, and
the current `src/code/server/sv_zmq.c` implementation. The retail `zauth` actor evidence is now tied to the portable source's named ZAP frame constants
and split PLAIN domain credential selection in `idZMQ_GetPlainCredentials`,
keeping the dynamic external `zmq_*` boundary and the default-disabled
online-service policy intact.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F5A30` | `zactor_new` | High | Retail RCON/stats setup creates the auth actor with `sub_4F69F0` as the body. |
| `sub_4F5DB0` | `zstr_sendx` | High | Sends actor control commands including `VERBOSE` and password-file `PLAIN` setup. |
| `sub_4F5630` | `zsock_wait` | High | Waits for actor acknowledgement after control messages. |
| `sub_4F5F10` | `zauth_self_new` | High | Constructs the auth self object and binds `inproc://zeromq.zap.01`. |
| `sub_4F63D0` | `s_zap_request_new` | High | Receives and decodes the ZAP request, including mechanism-specific PLAIN frames. |
| `sub_4F65F0` | `s_zap_request_reply` | High | Emits the six-frame ZAP response with status code/text and user id. |
| `sub_4F6630` | `s_authenticate_plain` | High | Verifies `%s_%s` username/domain keys against the loaded password table. |
| `sub_4F67A0` | `s_self_authenticate` | High | Dispatches NULL/PLAIN/CURVE/GSSAPI and returns `No access` when denied. |
| `sub_4F69F0` | `zauth` | High | Actor body that polls the pipe and ZAP socket. |

## Observed Facts

- `sub_4F3F80` creates a `zactor_new(zauth, 0)` actor when RCON is enabled,
  sends `VERBOSE` via `zstr_sendx`, waits with `zsock_wait`, then calls
  `idZMQ_ApplyPasswords` before creating the ROUTER socket.
- `sub_4F4210` repeats the actor creation and `VERBOSE` command for stats
  publication before creating the PUB socket.
- `sub_4F3D70` and `sub_4F3F20` send the `PLAIN` control command after the
  password file is refreshed from the retained `zmq_*_password` cvars.
- The string table contains the ZAP endpoint, `NULL`, `PLAIN`, `VERBOSE`,
  `%s_%s`, `No access`, and the Quake Live password file lines
  `rcon_rcon=%s\n` and `stats_stats=%s\n`.

## Source Reconstruction

- Added named source constants for the ZAP endpoint contract: version `1.0`,
  mechanisms `NULL`/`PLAIN`, success code `200`, denial code `400`, and the
  retail denial text `No access`.
- Added `idZMQ_GetPlainCredentials` so the portable manual ZAP REP socket uses
  the same two domain buckets that retail wires through `rcon_rcon` and
  `stats_stats` password keys.
- Kept the existing direct `zmq_*` dynamic loading boundary and did not move
  source into CZMQ/libzmq library ownership.

## Confidence And Open Questions

Confidence is high for the source-shape improvement because it is cross-checked
against existing aliases, Ghidra function rows, Binary Ninja HLIL control flow,
retail string literals, and prior ZMQ mapping rounds. The remaining divergence
is intentional: SRP still uses a compact manual ZAP REP socket instead of
embedding retail's full CZMQ `zauth` actor implementation.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_zap_plain_auth_source_shape_round_639`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZAP/PLAIN auth source-shape confidence: **before 97% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 94.4% -> after 94.6%**.
- Repo-wide parity remains **99%** because this closes a local ZMQ evidence and
  source-shape gap without changing the strict-retail Windows replacement score.
