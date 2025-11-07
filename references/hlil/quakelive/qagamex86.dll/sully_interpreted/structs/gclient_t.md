# gclient_t layout (Quake Live `qagamex86.dll`)

The Quake Live client block lives at `data_105dce40` with a stride of `0xBD8`
bytes, substantially larger than Quake III Arena’s `gclient_t` due to the added
stats, persistence, and authentication fields.  The HLIL around
`ClientConnect`/`ClientBegin` exposes how this layout maps back to the GPL
structure.

| Offset | Field | Notes |
| ------ | ----- | ----- |
| `0x000` | `playerState_t ps` | `ClientBegin` clears the leading `0x250` bytes (which cover `ps` and the legacy entity linkage) before applying the respawn template, matching Quake III’s rule that `ps` is the first member (`memset(edi_2, 0, 0x250)` at `0x1003B0E6`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41217】 |
| `0x250` | `clientPersistant_t pers.connected` | Immediately after allocating the slot, the HLIL seeds `*(client + 0x250) = 1` (connected) or `2` (intermission) before the zero fill, preserving the state expected by `ClientSpawn` once the handshake completes (`0x1003ADB3`, `0x1003B0C2`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41117-L41213】 |
| `0x2C0` | Steam ID (low 32 bits) | The engine callback at `data_104b13ac + 0x320` returns a 64-bit identifier that lands at offsets `0x2C0`/`0x2C4`, reflecting Quake Live’s Steam authentication data that replaces the Quake III CD-Key hash (`0x1003ADC4`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41120-L41123】 |
| `0x2C8` | `pers.maxHealth` | The handicap scaling path writes the computed health cap here before mirroring it into `ps.stats[STAT_HEALTH]` (`*(edi + 0x2C8) = eax_36` followed by `*(edi + 0xDC) = *(edi + 0x2C8)` at `0x1003A878`–`0x1003A89E`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L40982-L41003】 |
| `0x2D8` / `0x2DC` | Session restart bookmarks | Reconnects initialise these slots to `-1`, a Quake Live extension used when re-queuing players during warmup or match transitions (`0x1003B100`–`0x1003B112`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41219-L41224】 |
| `0x32C` | Timeout / vote throttle | The handshake zeroes this word alongside the Steam slot timers, feeding the logic that tracks private client invite cooldowns (`0x1003B0E0`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41212-L41216】 |
| `0x348` | Session team | The reconnect helper inspects `*(client + 0x348)` to decide whether to preserve team assignments across map restarts, matching Quake Live’s session persistence (`0x1003B0F0`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41156-L41182】 |
| `0x368` | Ban timestamp / queue slot | When localhost connections bypass Steam, the HLIL stores the `_time64` ban expiry here, mirroring the GPL `sess.sessionTeam`-style field repurposed for Quake Live’s backend bans (`0x1003ACFA`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41068-L41156】 |
| `0x568` | Command time seed | The connect path reinitialises the command time used by bot AI and warmup logic (`*(client + 0x568) = data_105dce5c + rand() + ...` at `0x1003AE03`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41123-L41133】 |

The remaining space up to `0xBD8` holds the expanded award trackers, weapon
statistics, and private match metadata that Quake Live layered on top of Quake
III’s base `gclient_t`.  Those regions surface in other HLIL snippets (for
example the `g_startingAmmo_*` loader at `0x1003B2A0`) and can be cross-referenced
with the Quake III sources when more precise field names are required.
