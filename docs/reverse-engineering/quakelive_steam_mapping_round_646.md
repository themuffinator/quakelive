# quakelive_steam.exe Mapping Round 646

Date: 2026-06-15

Scope: focused ZMQ RCON broadcast disconnect-branch pass for the retained
`idZMQ` host. This round stays in Quake Live server-owned wiring and does not
reconstruct or vendor libzmq/CZMQ implementation source.

## Summary

This pass rechecked retail `idZMQ_BroadcastRconOutput` at `sub_4F4D40`.
Retail walks the retained RCON peer table, sends each peer identity with
`zstr_sendm`, and only enters the disconnect/erase branch when that identity
prefix send fails. When the prefix send succeeds, retail sends the console
message body with `zstr_send`; the message frame send is not part of the disconnect branch.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Walks the retained RCON peer table and erases peers on multipart identity-send failure. |
| `sub_4F4E60` | `Zmq_BroadcastRconOutput` | High | Public console-print wrapper into the retained broadcast method. |
| `sub_4F46B0` | `idZMQ_EraseRconPeer` | High | Erases the current peer on the broadcast disconnect branch. |
| `sub_4F5D60` | `zstr_send` | High | Sends the console output body after the identity send succeeds. |
| `sub_4F5D90` | `zstr_sendm` | High | Sends the RCON peer identity as the multipart prefix and controls the disconnect branch. |

## Observed Facts

- `sub_4F4D40` first checks the retained RCON socket at `this + 0xc`.
- It iterates the peer table rooted from the retained sentinel at `this + 0x18`.
- The branch condition is `sub_4F5D90(*(arg1 + 0xc), peerIdentity) >= 0`.
- On that success path, retail calls `sub_4F5D60(*(arg1 + 0xc), message)`.
- On failure of the identity prefix send, retail calls `sub_4F46B0` to erase
  the current peer and logs `zmq RCON client disconnected: %s\n`.
- `sub_4F4E60` is the public wrapper used by the console print path.

## Source Reconstruction

- Updated portable `Zmq_BroadcastRconOutput` so peer disconnect/erase is tied
  only to the identity multipart-prefix send failure.
- Left the console-message body send as a follow-up operation after the prefix
  succeeds. Its return value no longer triggers the disconnect branch.
- Kept the portable implementation on public dynamically resolved `zmq_send`
  calls while preserving the retail `zstr_sendm`/`zstr_send` ownership split.
- Preserved the external libzmq runtime boundary; this pass does not
  reconstruct retail CZMQ/libzmq internals.

## Confidence And Open Questions

Confidence is high for this branch correction because it is cross-checked
against Binary Ninja HLIL, Ghidra function rows, aliases, retail strings, the
existing peer-table mapping, and the current console-print wrapper. The exact
CZMQ helper implementation remains evidence only; SRP continues to reconstruct
only the Quake Live-owned server wiring.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k zmq_rcon_broadcast_disconnect_branch_round_646`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
- `python -m pytest -q tests/test_server_full_parity_gate.py`

## Parity Estimate

- Focused ZMQ RCON broadcast branch confidence:
  **before 91% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 95.9% -> after 96.1%**.
- Repo-wide parity remains **99%** because this pass closes a local RCON
  broadcast ownership gap without changing the strict-retail Windows
  replacement score.
