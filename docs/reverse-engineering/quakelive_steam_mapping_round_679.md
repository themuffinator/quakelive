# Quake Live Steam Mapping Round 679: ZMQ Single-Poll-Item Boundary

Date: 2026-06-16

## Scope

This pass rechecked the retained ZMQ poll vector used by the RCON pump. Retail
Quake Live builds one `zmq_pollitem_t` on the stack, sets the input event bit,
and calls `zmq_poll` with an item count of `1`. SRP already matched that
behavior for the RCON pump and for the external-runtime auth pump; this round
names the single-poll-item boundary instead of leaving the count as an inline
integer argument.

Focused parity estimate: **before 92% -> after 98%** for single-poll-item
source-boundary confidence. Focused ZMQ wiring/source reconstruction confidence
moves from **98.9% -> 99.0%**. Repo-wide parity remains **99%** because this
pass closes a local poll-vector source-shape gap without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401600` | `zmq_poll` | High | Lower libzmq poll entry reached by the retained RCON pump. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Owns the retained RCON poll item, one-item count, identity read, command read, and peer dispatch path. |

Observed Binary Ninja HLIL anchors:

- `004f4ed0` starts the retained RCON pump owner.
- `004f4f09` sets the poll item events word to `1`, matching `ZMQ_POLLIN`.
- `004f4f0d` calls `zmq_poll` as `sub_401600(xmm0, &var_20, 1)`.

Observed fact: the one-item poll vector is Quake Live `idZMQ` integration
wiring. The `zmq_poll` implementation body belongs to the embedded retail
libzmq/CZMQ dependency evidence and is not reconstructed in SRP.

## Source Reconstruction

This single-poll-item boundary is now named in source:

- `QL_ZMQ_SINGLE_POLL_ITEM`

The retained source boundary is:

- `idZMQ_PumpRcon` polls exactly one retained RCON poll item with
  `QL_ZMQ_SINGLE_POLL_ITEM` and `QL_ZMQ_POLL_TIMEOUT_IMMEDIATE`.
- `idZMQ_PumpAuthSocket` uses the same named one-item poll count for SRP's
  external-libzmq ZAP endpoint pump, keeping the runtime replacement shape
  explicit without reconstructing CZMQ's `zactor` helper.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zmq_poll`, `zstr_recv`, `zstr_send`, `zstr_sendm`, or `zactor` source bodies
to the repository.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k zmq_single_poll_item_boundary_round_679`
  - `1 passed, 222 deselected in 7.95s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `78 passed, 145 deselected in 2.37s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.21s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
