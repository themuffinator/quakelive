# Quake Live Steam Mapping Round 667: ZMQ Manual ZAP Auth Response Frame Boundary

Date: 2026-06-16

## Scope

This pass rechecked the manual ZAP auth response frame boundary in SRP's
retained ZMQ wiring. Retail Quake Live uses embedded CZMQ `zauth` code for the
actor loop and ZAP response handling; SRP keeps that dependency outside the
source tree and owns a compact manual ZAP responder in `sv_zmq.c`.

Focused parity estimate: **before 92% -> after 98%** for the manual ZAP auth
response/source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **98.2% -> 98.3%**. Repo-wide parity remains **99%**
because this pass closes a local auth-response source-shape gap without
changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F5F10` | `zauth_self_new` | High | Creates the CZMQ auth self object and binds `inproc://zeromq.zap.01`. |
| `sub_4F5FC0` | `zauth_self_handle_pipe` | High | Handles actor pipe commands while the auth actor loop is running. |
| `sub_4F6630` | `s_authenticate_plain` | High | Authenticates PLAIN requests through the `%s_%s` password-table lookup. |
| `sub_4F69F0` | `zauth` | High | Actor body that starts auth self, signals readiness, and dispatches pipe/ZAP traffic. |

Observed Binary Ninja HLIL anchors:

- `004f5f9c` binds `inproc://zeromq.zap.01` while constructing the auth self.
- `004f65fd` logs the ZAP reply status-code/status-text pair.
- `004f6653` formats the PLAIN lookup key as `%s_%s`.
- `004f66a9` logs allowed PLAIN credentials.
- `004f66fd` logs denied PLAIN auth when no password file exists.
- `004f68dc` logs allowed NULL mechanism auth.
- `004f69fb` constructs the auth self from the `zauth` actor body.
- `004f6a28` dispatches actor pipe commands through `zauth_self_handle_pipe`.

Observed retail string anchors:

- `005485f8`: `zauth: - ZAP reply status_code=%s status_text=%s`
- `00548660`: `zauth: - denied (PLAIN) username=%s password=%s`
- `00548690`: `zauth: - allowed (PLAIN) username=%s password=%s`
- `005486c4`: `%s_%s`
- `0054878c`: `zauth: - allowed (NULL)`
- `005487fc`: `No access`
- `00550cd0`: `inproc://zeromq.zap.01`

Observed fact: the full `zauth` implementation is embedded CZMQ/libzmq support
code in retail `quakelive_steam.exe`, not SRP source to reconstruct. The
Quake Live integration requirement is the auth endpoint, NULL/PLAIN behavior,
status defaults, credential validation, and response frame order.

## Source Reconstruction

SRP now names the empty fields used by its SRP-owned manual ZAP responder:

- `QL_ZMQ_AUTH_EMPTY_FRAME`
- `QL_ZMQ_AUTH_EMPTY_USER_ID`
- `QL_ZMQ_AUTH_EMPTY_CREDENTIAL`

Those constants route the following response/credential boundary:

- `idZMQ_SendAuthFrame` sends an empty frame when a nullable frame value is
  absent.
- `idZMQ_SendAuthResponse` emits the ZAP response frames in order: version,
  request id, status code, status text, user id, then an empty metadata frame.
- `idZMQ_GetPlainCredentials` and `idZMQ_ValidatePlainCredentials` use named
  empty credential/user-id fallbacks before resolving `rcon` or `stats`.
- `idZMQ_PumpAuthSocket` starts each request with `400` / `BAD REQUEST`,
  permits `NULL` as `200` / `OK`, and upgrades valid PLAIN credentials to
  `200` / `OK` while keeping failures at `No access`.

This round does not reconstruct libzmq/CZMQ internals. The embedded retail
`zauth`, `zauth_self_*`, and `s_authenticate_plain` helpers remain evidence for
SRP's integration contract, while SRP keeps the implementation boundary at the
manual ZAP frame pump over external libzmq symbols.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_manual_zap_auth_response_boundary_round_667`
  - `1 passed, 212 deselected in 6.39s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `71 passed, 142 deselected in 9.37s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.10s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
