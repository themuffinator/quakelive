# quakelive_steam.exe Mapping Round 647

Date: 2026-06-15

Scope: focused ZMQ RCON broadcast payload-normalization pass for the retained
`idZMQ` host. This round stays in Quake Live server-owned wiring and does not
reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked the retail `Zmq_BroadcastRconOutput` wrapper and
`zstr_send` helper behavior. Retail forwards the console-print payload through
the retained broadcast method and then through `zstr_send`. The embedded
`zstr_send` helper maps a null payload pointer to the empty-string storage
before sending. SRP now mirrors that local source shape: null broadcast payloads are normalized to an empty string and empty payloads are no longer suppressed before the retained RCON socket/peer checks.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Broadcasts the wrapper-provided console payload to retained RCON peers. |
| `sub_4F4E60` | `Zmq_BroadcastRconOutput` | High | Public console-print wrapper that preserves the payload argument before entering the retained broadcast method. |
| `sub_4F5D60` | `zstr_send` | High | Sends the message body and substitutes the empty string when its payload pointer is null. |

## Observed Facts

- `sub_4F4E60` stores its incoming argument before entering
  `sub_4F4D40(&data_5756fc)`, matching a wrapper that forwards a console
  message payload into the retained object method.
- `sub_4F4D40` passes that payload to `sub_4F5D60` on the successful
  identity-prefix send path.
- `sub_4F5D60` checks whether its payload argument is null and substitutes
  `data_54f9da`, the retail empty-string storage, before calling the send
  helper.
- No retail guard was observed that rejects an empty message before reaching
  the retained RCON broadcast loop.

## Source Reconstruction

- Added a local `payload` pointer in `Zmq_BroadcastRconOutput` and normalized
  null messages with `payload = message ? message : ""`.
- Removed the non-retail `!message || !message[0]` early return from the
  broadcast path. Socket, peer, send-symbol, and recursion guards remain.
- Sent the message body with `payload` and `strlen( payload )`, preserving the
  retail null-to-empty behavior while staying on public dynamically resolved
  `zmq_send`.
- Preserved the external libzmq runtime boundary; this pass does not
  reconstruct embedded CZMQ/libzmq internals.

## Confidence And Open Questions

Confidence is high for this source-shape correction because it is cross-checked
against Binary Ninja HLIL, Ghidra function rows, aliases, current console-print
wiring, and the previous RCON broadcast branch mapping. The exact CZMQ helper
implementation remains evidence only; SRP continues to reconstruct only the
Quake Live-owned server wiring.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_broadcast_null_payload_round_647`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ RCON broadcast payload-normalization confidence:
  **before 93% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 96.1% -> after 96.2%**.
- Repo-wide parity remains **99%** because this pass closes a local RCON
  broadcast source-shape gap without changing the strict-retail Windows
  replacement score.
