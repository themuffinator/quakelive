# gentity_t layout (Quake Live `qagamex86.dll`)

The HLIL shows the runtime `gentity_t` array rooted at `data_104b3fa0`, with a
stride of `0x384` bytes per entity.  That stride aligns with the Quake III Arena
`gentity_t` structure once the Quake Live additions (persistent power-up
bookkeeping, Steam session pointers, and scoreboard extensions) are accounted
for.  Selected offsets that are visible in the HLIL are summarised below.

| Offset | Field | Evidence |
| ------ | ----- | -------- |
| `0x000` | `entityState_t s` | `ClientBegin` zeros the first `0x250` bytes before rebuilding persistent state, matching the Quake III contract that the server snapshot (`s`) lives at the head of the struct (`memset(edi_2, 0, 0x250)` at `0x1003B0E6`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41217】 |
| `0x068` | `int svFlags` (inside `entityShared_t r`) | The reconnect path preserves the flag word while wiping the rest of the entity (`*(edi_2 + 0x68) = ebx` at `0x1003B0F7`), mirroring `gentity_t::r.svFlags` in Quake III where bots, spectators, and private clients toggle bits in this slot.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41219】 |
| `0x1E0` | `int svFlagsExt` | Steam-authenticated connects set `*(g_ent + 0x1E0) |= 8` when the `isBot` flag is true, matching the Quake Live-only mask used for bot slots (`0x1003AE4D`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41136-L41139】 |
| `0x23C` | `gclient_t *client` | Both `ClientConnect` and `ClientBegin` store the address of the owning client structure through this pointer (`*(ebx_6 + 0x23C) = esi_8` at `0x1003AD9F`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41112-L41122】 |
| `0x240` | `qboolean connected` | The connect handshake toggles this flag when the Steam backend reports success (`*(ebx_6 + 0x240) = 1` at `0x1003AE59`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41136-L41139】 |
| `0x27C` | `playerState_t::commandTime` mirror | When bots reconnect or the server restarts, Quake Live seeds `*(client + 0x568)` with `serverTime + rand()` and mirrors it through the owning entity at `entity + 0x27C`, matching the `s.clientNum`-synchronised command timer from `g_active.c` (`0x1003AE03`–`0x1003AE3C`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41123-L41133】 |
| `0x32C` | Warmup and timeout bookkeeping | The reconnection path clears `*(client + 0x32C)` during handoff (`0x1003B0E0`), aligning with Quake Live’s extra timeout counters layered on top of the Quake III `entityEvent_t` bookkeeping.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41212-L41216】 |

The array that backs `g_entities` is initialised in the Sully interpretation of
`G_InitGame`, where the HLIL seeds both the entity block (`data_104b3fa0`) and
the client pointer cache (`data_104b41dc`) before the map entities are spawned.
