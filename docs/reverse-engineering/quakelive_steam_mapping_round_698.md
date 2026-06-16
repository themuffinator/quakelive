# Quake Live Steam Mapping Round 698: ZMQ RCON Positive-Frame Gate

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ RCON positive-frame gate in the retained server-owned
`idZMQ` wiring. Retail Quake Live reads multipart RCON identities and commands
through CZMQ string helpers, then only proceeds to peer lookup, insertion,
logging, and command execution when the identity and command frames contain
payload bytes.

Focused parity estimate: **before 94% -> after 99%** for RCON positive-frame
gate source-boundary confidence. Focused ZMQ wiring/source reconstruction
confidence moves from **99.4% -> 99.45%**. Repo-wide parity remains **99%**
because this pass names a local server integration receive gate without
changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Retail RCON pump owner. |
| `sub_4F4910` | `idZMQ_FindRconPeer` | High | Finds the peer record for a received identity. |
| `sub_4F49C0` | `idZMQ_InsertRconPeer` | High | Inserts a peer when a new identity connects. |
| `sub_4F5CB0` | `zstr_recv` | High | Retail CZMQ string receive helper. |
| `sub_4F5E10` | `zstr_free` | High | Retail CZMQ string free helper. |
| `sub_401600` | `zmq_poll` | High | Retail embedded libzmq poll wrapper. |

Observed Binary Ninja HLIL anchors:

- `004f4ed0` is the retained RCON pump.
- `004f4f0d` polls one RCON item.
- `004f4f23` receives the identity frame through `zstr_recv`.
- `004f4f2f` receives the command frame through `zstr_recv`.
- `004f4f4c` looks up the peer after both receive steps.
- `004f4f7a` inserts a missing peer.
- `004f4fa2` executes the command string after the positive-frame path.
- `004f4fab` and `004f4fb7` release received string frames.

Observed fact: these branches belong to Quake Live's `idZMQ` integration. The
CZMQ/libzmq helpers are embedded dependency evidence, not SRP source to
reconstruct.

Inference: SRP's stack-buffer adaptation should keep multipart drain behavior
for non-negative read lengths, while treating empty identity or command frames
as non-actionable RCON messages.

## Source Reconstruction

The positive-frame gate is now named in source:

- `QL_ZMQ_FRAME_READ_SUCCESS_MIN`
- `QL_ZMQ_RCON_MIN_IDENTITY_LENGTH`
- `QL_ZMQ_RCON_MIN_COMMAND_LENGTH`

`idZMQ_ReadRconCommand` treats non-negative frame reads as successful enough to
preserve the multipart drain path. `idZMQ_PumpRcon` requires positive identity
and command lengths before peer lookup, insertion, logging, or command
execution.

This is an SRP stack-buffer adaptation of the retail CZMQ string receive shape.
It does not reconstruct libzmq/CZMQ internals and does not add `zstr_recv`,
`zstr_free`, `zsock_*`, `zauth`, or lower `zmq::*` source bodies to the
repository.

## Validation

Restored evidence companion for the existing Round 698 parity gate. Covered by
the current ZMQ validation pass:

- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short` - 88 passed, 172 deselected.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short` - 2 passed, 1 skipped.
- `rg --files src/libs/libzmq` - only `src/libs/libzmq\README.md`.
- `git diff --check` - passed with pre-existing LF-to-CRLF warnings.
