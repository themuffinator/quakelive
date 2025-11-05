# Stage 3 Dynamic Tracing Candidates

These hotspots either involve obfuscation, checksum seeding, or conditional paths that are difficult to reason about statically. Instrument them during Stage 3 capture/replay work.

| Area | Why It Matters | Suggested Instrumentation |
| --- | --- | --- |
| `CL_Netchan_Encode` / `CL_Netchan_Decode` | XOR stream combines `clc.challenge`, acknowledgement counters, and the most recent reliable command payload. Off-by-one desyncs silently corrupt subsequent packets. Trace key evolution per byte to validate documentation. 【F:src/code/client/cl_net_chan.c†L25-L112】 | Hook right before/after the loops to log derived `key`, `index`, and the referenced command string. |
| `SV_Netchan_Encode` / `SV_Netchan_Decode` | Server mirrors the XOR logic but seeds from `client->netchan.outgoingSequence`. Divergence between client/server views is hard to detect without capturing both sides. 【F:src/code/server/sv_net_chan.c†L25-L128】 | Record per-client key schedule and ensure queueing code (`netchan_buffer_t`) replays encoded payloads identically. |
| `Netchan_ScramblePacket` (disabled) | Although `#if 0` in current tree, some legacy builds flip this on, reordering/obfuscating payload bytes. Requires dynamic probes if resurrected by patches. 【F:src/code/qcommon/net_chan.c†L70-L126】 | Build-time guard detection; if enabled, capture before/after buffers to reverse the permutation. |
| Challenge authorization loop | `SV_GetChallenge` → `SV_AuthorizeIpPacket` clears or reuses `svs.challenges[i]` depending on multiple async callbacks; race conditions could leak stale `challenge` seeds that poison encryption. 【F:src/code/server/sv_client.c†L134-L333】 | Trace challenge slot lifecycle with timestamps, especially when backend times out or denies access. |
| Checksum feeds | `clc.checksumFeed` influences usercmd signing later in the connect flow; handshake packets include seeds for this mechanism. 【F:src/code/client/cl_input.c†L758-L768】【F:src/code/client/cl_main.c†L361-L405】 | Capture `checksumFeed` assignments from initial `gamestate` to ensure consistent command verification. |

Document findings in Stage 3 to refine packet layout notes.
