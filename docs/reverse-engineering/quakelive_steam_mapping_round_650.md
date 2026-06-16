# quakelive_steam.exe Mapping Round 650

Date: 2026-06-15

Scope: focused ZMQ RCON resolved-poll-slot reconstruction for the retained
`idZMQ` host. This round stays in Quake Live server-owned wiring and does not
reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the retail RCON setup and pump split after the bind-result
logging path. Retail keeps the RCON `zsock` wrapper at `this + 0x0c`, resolves
that wrapper with `zsock_resolve`, stores the resolved raw socket at
`this + 0x10`, and then has the RCON pump poll `this + 0x10` while receiving
message frames from the retained wrapper. SRP now mirrors that local source
shape with a dedicated resolved RCON poll slot that is populated after bind
logging and used only for the RCON poll gate/item.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401600` | `zmq_poll` | High | Polls the resolved socket stored at the retained RCON poll slot. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Stores the RCON wrapper, logs bind result, resolves it, and stores the poll socket. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Requires both the wrapper and resolved poll slot before polling/receiving. |
| `sub_4F4FD0` | `Zmq_PumpRcon` | High | Tail-call wrapper into the retained RCON pump. |
| `sub_4F56B0` | `zsock_resolve` | High | Resolves a CZMQ wrapper to the underlying socket handle. |

## Observed Facts

- `sub_4F3F80` stores the RCON wrapper at `arg1 + 0x0c`, selects and prints the
  bind-result log string, then calls `sub_4F56B0(*(arg1 + 0x0c))`.
- The resolved `sub_4F56B0` result is stored at `arg1 + 0x10`.
- `sub_4F4ED0` first checks that `arg1 + 0x0c` is non-null, then reads
  `arg1 + 0x10` and requires it to be non-null before building the poll item.
- The pump passes the resolved slot into `zmq_poll`, but still receives the
  identity and command frames through calls rooted at the retained RCON wrapper.

## Source Reconstruction

- Added `rconPollSocket` to the retained portable `idZMQ_t` state.
- Populated `s_zmq.rconPollSocket` after the RCON bind-result log in
  `idZMQ_EnsureRconSocket`, mirroring the retail post-log `zsock_resolve`
  store at `this + 0x10`.
- Updated `Zmq_PumpRcon` to require `rconPollSocket` and use it for the
  `zmq_poll` item, while continuing to read command frames from `rconSocket`.
- Cleared `rconPollSocket` alongside RCON socket shutdown/disabled handling.
- Preserved the external libzmq runtime boundary; this pass does not
  reconstruct embedded CZMQ/libzmq internals.

## Confidence And Open Questions

Confidence is high because the split is supported by Binary Ninja HLIL, Ghidra
function rows, aliases, retail strings, and the existing RCON setup/pump
source. In SRP's external-C-API implementation the wrapper and resolved socket
are the same pointer value, but the retained state split is valuable because it
matches retail ownership and keeps future mapping of `this + 0x10` explicit.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_resolved_poll_slot_round_650`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ RCON resolved-poll-slot confidence:
  **before 90% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.4% -> after 96.5%**.
- Repo-wide parity remains **99%** because this pass closes a local RCON pump
  source-shape gap without changing the strict-retail Windows replacement
  score.
