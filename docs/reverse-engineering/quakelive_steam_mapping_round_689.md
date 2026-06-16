# Quake Live Steam Mapping Round 689: ZMQ ZAP Request Frame-Buffer Boundary

Date: 2026-06-16

## Scope

This pass rechecked SRP's manual ZAP request pump, which stands in for retail
Quake Live's embedded CZMQ `zauth` actor. Earlier rounds named the ZAP endpoint,
mechanisms, status texts, response frames, and credential domains. This round
names the caller-owned request frame buffers used by `idZMQ_PumpAuthSocket` so
the manual REP socket has an auditable source shape without importing CZMQ
request-parser code.

Focused parity estimate: **before 92% -> after 98%** for ZAP request
frame-buffer source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.2% -> 99.25%**. Repo-wide parity
remains **99%** because this pass names a local bounded-frame receive boundary
without changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F63D0` | `s_zap_request_new` | High | Receives and decodes ZAP request frames before authentication dispatch. |
| `sub_4F65F0` | `s_zap_request_reply` | High | Emits the six-frame ZAP response. |
| `sub_4F6630` | `s_authenticate_plain` | High | Authenticates PLAIN credentials against the password table. |
| `sub_4F67A0` | `s_self_authenticate` | High | Dispatches NULL/PLAIN request handling and returns `No access` on denial. |
| `sub_4F69F0` | `zauth` | High | Owns the actor loop that polls pipe/ZAP traffic in retail. |

Observed Binary Ninja HLIL anchors:

- `004f63d0` begins `s_zap_request_new`.
- `004f65ce` logs the request mechanism and address.
- `004f65f0` begins `s_zap_request_reply`.
- `004f6630` begins `s_authenticate_plain`.
- `004f6894` selects the `NULL` mechanism.
- `004f68f3` selects the `PLAIN` mechanism.
- `004f69f0` begins the `zauth` actor body.

Observed string anchors:

- `005485c8`: `zauth: ZAP request mechanism=%s ipaddress=%s`
- `005485f8`: `zauth: - ZAP reply status_code=%s status_text=%s`
- `005487fc`: `No access`
- `00550cd0`: `inproc://zeromq.zap.01`

Observed fact: the request parsing helper belongs to embedded CZMQ/libzmq
support code in retail `quakelive_steam.exe`. SRP's owned boundary is the
manual ZAP frame pump and the caller-owned buffers it uses to receive version,
request id, domain, address, identity, mechanism, username, and password
frames.

Inference: naming these capacities in SRP source records the request frame
contract while preserving the intentionally external `zauth`/CZMQ
implementation boundary.

## Source Reconstruction

The ZAP request frame-buffer boundary is now named in source:

- `QL_ZMQ_ZAP_VERSION_BUFFER_SIZE`
- `QL_ZMQ_ZAP_REQUEST_ID_BUFFER_SIZE`
- `QL_ZMQ_ZAP_DOMAIN_BUFFER_SIZE`
- `QL_ZMQ_ZAP_ADDRESS_BUFFER_SIZE`
- `QL_ZMQ_ZAP_IDENTITY_BUFFER_SIZE`
- `QL_ZMQ_ZAP_MECHANISM_BUFFER_SIZE`
- `QL_ZMQ_ZAP_USERNAME_BUFFER_SIZE`
- `QL_ZMQ_ZAP_PASSWORD_BUFFER_SIZE`
- `QL_ZMQ_ZAP_EMPTY_FIELD`

`idZMQ_PumpAuthSocket` now declares its caller-owned frame buffers through
those constants, initializes the version buffer from `QL_ZMQ_ZAP_VERSION`, and
resets optional fields through `QL_ZMQ_ZAP_EMPTY_FIELD`.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zauth`, `s_zap_request_new`, `s_zap_request_reply`, `s_authenticate_plain`, or
lower libzmq source bodies to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_zap_request_buffer_boundary_round_689 --tb=short`
  - `1 passed, 230 deselected in 8.99s`
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short`
  - `83 passed, 148 deselected in 4.14s`
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short`
  - `2 passed, 1 skipped in 0.27s`
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
