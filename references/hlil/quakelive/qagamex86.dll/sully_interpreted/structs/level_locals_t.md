# level_locals_t highlights

The global `level` structure is stored in the zero-initialised block beginning at
`data_105dce40`.  `G_InitGame` clears the first `0x4B9C` bytes before seeding key
fields, mirroring the Quake III Arena `level_locals_t` initialisation path.

| Offset | Field | HLIL evidence |
| ------ | ----- | ------------- |
| `0x0000` | `gclient_t *clients` | The init sequence writes the base address of the client array (`0x105AD180`) into both `data_105dce40` and the per-entity cache at `data_105dce44`, then fans out pointers for each entity slot (`0x10055312`–`0x1005535F`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61309-L61389】 |
| `0x0004` | `gentity_t *gentities` | `data_105dce44 = &data_104b3fa0` stores the base of the entity array alongside the client pointer fan-out, matching Quake III’s `level.gentities` pointer (`0x1005531D`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61363-L61385】 |
| `0x0008` | `int gentitySize` | The function pointer at `data_104b13ac + 0x58` receives `(0x384, 0xBD8)` before the configstring upload, reflecting the entity/client strides (`0x100553BD`–`0x100553D8`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61390-L61421】 |
| `0x0010` | `int maxclients` | The HLIL pulls `data_1059800c` (the compiled `sv_maxclients`) into `data_105dce58` immediately after clearing the level block (`0x10055309`–`0x10055327`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61363-L61373】 |
| `0x0014` | `int framenum` | `G_RunFrame` increments the word that mirrors `level.framenum`; the Sully interpretation of the frame loop references this offset directly when syncing the warmup timers.【F:references/hlil/quakelive/qagamex86.dll/sully_interpreted/functions/g_main/G_RunFrame.md†L9-L33】 |
| `0x0018` | `int time` | Both `G_InitGame` and `ClientConnect` read `data_105dce5c` when stamping session and command timers, aligning with Quake III’s `level.time` (`0x1005519C`, `0x1003AE0E`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61304-L61333】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41123-L41139】 |
| `0x001C` | `int previousTime` | `data_105dce64` shadows `level.previousTime`, seeded alongside `level.time` during initialisation (`0x100551A1`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61304-L61306】 |
| `0x0134` | `fileHandle_t logFile` | When logging is enabled, the pointer stored at `data_105dce54` is funneled through Quake III’s `level.logFile` usage (`0x1005521F`–`0x100552A5`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61321-L61348】 |
| `0x01C0` | Warmup/restart latch | The Quake Live-only `data_105dce7c` flag flips when the stored session gametype differs from the current latched value, matching the `level.newSession` semantics from the GPL code (`0x100552E4`–`0x100552F1`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61350-L61362】 |

Quake Live extends the tail of `level_locals_t` with additional tournament and
backend state (`data_105df58*`, `data_105e1e60`, etc.).  Those addresses surface
in the remainder of the `G_InitGame` HLIL and can be mapped to their Quake III
counterparts as reconstruction progresses.
