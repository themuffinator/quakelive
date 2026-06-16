# Quake Live Steam Mapping Round 672: ZMQ RCON Empty Payload Constant Boundary

Date: 2026-06-16

## Scope

This pass rechecked the RCON broadcast null-payload boundary in the retained
ZMQ integration. Retail Quake Live forwards console output through
`idZMQ_BroadcastRconOutput` and then through embedded CZMQ `zstr_send`. The
retail helper substitutes shared empty-string storage when the payload pointer
is null. SRP already preserved that behavior; this round names the retained
RCON empty payload fallback in source.

Focused parity estimate: **before 92% -> after 98%** for RCON empty payload
source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **98.6% -> 98.7%**. Repo-wide parity remains **99%**
because this pass closes a local RCON broadcast source-shape gap without
changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Iterates retained RCON peers and sends the message body after the identity frame succeeds. |
| `sub_4F4E60` | `Zmq_BroadcastRconOutput` | High | Public wrapper into the retained broadcast owner. |
| `sub_4F5C10` | `s_send_string` | High | Lower CZMQ string-send helper called by `zstr_send`. |
| `sub_4F5D60` | `zstr_send` | High | Normalizes a null payload pointer to shared empty-string storage before sending. |

Observed Binary Ninja HLIL anchors:

- `004f4d40` starts the retained RCON broadcast method.
- `004f4d78` sends the identity frame first through `zstr_sendm`.
- `004f4daa` sends the message body through `zstr_send`.
- `004f4e60` and `004f4e72` are the public wrapper path into the retained
  broadcaster.
- `004f5d69` checks whether the `zstr_send` payload pointer is null.
- `004f5d6b` substitutes `data_54f9da`.
- `004f5d80` enters the lower string-send helper with that normalized pointer.

Observed string/table anchors:

- `0054f9da`: shared empty-string storage (`00 00`)

Observed fact: the null-to-empty behavior belongs to embedded CZMQ helper code,
but the SRP source needs an explicit retained wiring equivalent for the
fallback payload used by the RCON broadcast method.

## Source Reconstruction

This RCON empty payload constant boundary is now named in source instead of
leaving the broadcast fallback as an inline empty string literal.

SRP now names the RCON empty payload fallback:

- `QL_ZMQ_RCON_EMPTY_PAYLOAD`

The constant aliases `QL_ZMQ_DEFAULT_EMPTY`, matching the retail use of shared
empty-string storage rather than introducing a separate payload buffer.

`idZMQ_BroadcastRconOutput` now uses:

- `payload = message ? message : QL_ZMQ_RCON_EMPTY_PAYLOAD`

The send path still emits `payload` through the dynamically resolved
`zmq_send` symbol and uses `strlen( payload )`. This pass does not reconstruct libzmq/CZMQ internals and does not add `zstr_send` or lower CZMQ helper source
to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_empty_payload_constant_boundary_round_672`
  - `1 passed, 217 deselected in 0.12s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `75 passed, 143 deselected in 1.49s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.12s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
