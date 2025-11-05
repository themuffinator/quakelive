# Client/Server Handshake State Transitions

This note captures how the Quake Live/Quake III style handshake flows between the client and server, focusing on the `Netchan_Process` path and the challenge/authorization responses involved in establishing a `netchan_t` session.

## Connstate lifecycle on the client

| State | Entered When | Outbound Handler | Expected Response | Transition |
| --- | --- | --- | --- | --- |
| `CA_DISCONNECTED` | Default after `CL_Disconnect` | – | – | `CL_Connect_f` resolves address, jumps to `CA_CONNECTING`/`CA_CHALLENGING`. |
| `CA_CONNECTING` | Remote server not on LAN (`CL_Connect_f`) | `CL_CheckForResend` sends `getchallenge` OOB; may also trigger `CL_RequestAuthorization`. 【F:src/code/client/cl_main.c†L1067-L1100】【F:src/code/client/cl_main.c†L1489-L1525】 | Server sends `challengeResponse` with nonce. | On receipt via `CL_ConnectionlessPacket`, state → `CA_CHALLENGING`. 【F:src/code/client/cl_main.c†L1776-L1804】 |
| `CA_CHALLENGING` | LAN connect path or post-challenge response | `CL_CheckForResend` packs `connect "userinfo"` payload with qport + challenge. 【F:src/code/client/cl_main.c†L1507-L1526】 | Server replies with `connectResponse` once slot allocated. | `CL_ConnectionlessPacket` instantiates `clc.netchan` and state → `CA_CONNECTED`. 【F:src/code/client/cl_main.c†L1816-L1836】 |
| `CA_CONNECTED` | `netchan_t` created | Client now expects sequenced traffic. `CL_Netchan_Process` decodes messages gated by `Netchan_Process`. 【F:src/code/client/cl_net_chan.c†L69-L112】【F:src/code/qcommon/net_chan.c†L304-L411】 | Snapshot / gamestate frames begin. | Later transitions (`CA_LOADING`, etc.) handled in `CL_ParseServerMessage`. |

Additional transitions: `CA_CHALLENGING` can revert to `CA_CONNECTING` when `CL_Disconnect` resets handshake counters; repeated challenge requests reuse `clc.connectPacketCount` to track timeouts.

## Server-side flow

1. `SV_GetChallenge` stores/refreshes per-IP challenge slots and answers LAN clients immediately, otherwise forwards to authorize backend. 【F:src/code/server/sv_client.c†L134-L220】
2. `SV_AuthorizeIpPacket` converts authorize-server callbacks into `challengeResponse` or rejection messages, clearing `svs.challenges` entries afterward. 【F:src/code/server/sv_client.c†L240-L333】
3. `SV_DirectConnect` validates the `challenge`, ensures qport/IP uniqueness, and seeds `client_t.challenge` before `Netchan_Setup`. 【F:src/code/server/sv_client.c†L335-L472】
4. Upon success, `SV_ConnectionlessPacket` emits `connectResponse` that the client accepts to create `netchan_t`. 【F:src/code/server/sv_main.c†L523-L590】

## `Netchan_Process` gating

Once a `netchan_t` exists on either side:

- Incoming packets are validated by `Netchan_Process`, which rejects out-of-order sequences, assembles fragments, and only returns `qtrue` for complete payloads. 【F:src/code/qcommon/net_chan.c†L304-L411】
- The client wraps this in `CL_Netchan_Process`, decoding the reliable stream using a key derived from the challenge, `serverId`, and acknowledgement counters. 【F:src/code/client/cl_net_chan.c†L25-L112】
- The server mirrors this by calling `SV_Netchan_Process` to decode with its own challenge/XOR stream and to schedule queued fragments. 【F:src/code/server/sv_net_chan.c†L25-L205】

### State gating via acknowledgements

`Netchan_Process` increments `chan->incomingSequence` after the last fragment of a message, enabling `CL_ParseServerMessage` / `SV_ReadClientMessage` to consume reliable commands. Because `clc.challenge` participates in the XOR key, losing the challenge or acknowledgement state desynchronises the cipher, so both sides reset the channel (transition back to `CA_CONNECTING`) on repeated decode failures.

## Stage 3 tracing focus

- `clc.connectPacketCount` and `clc.connectTime` govern retransmit thresholds; watch these when fuzzing handshake timings.
- `client_t.challenge` persists across reconnect logic in `SV_DirectConnect`, affecting the XOR seed until the client is dropped; we may need instrumentation to ensure stale challenges do not leak.

For deeper per-packet walkthroughs, refer to `docs/reverse-engineering/network-handshake.md` for serialized layout diagrams.
