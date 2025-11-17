# Quake Live Configstring Ledger

This ledger captures the Quake Live–specific configstrings recovered from the
Binary Ninja HLIL exports. Each entry lists the canonical index, its purpose,
and the HLIL excerpt that demonstrates where the shipping `qagamex86.dll`
published the payload. Use this table when auditing parity or when adding new
consumers under `src/code/` so the indices stay aligned with the retail DLL.

| Index | Macro / Usage | Purpose | HLIL reference |
| --- | --- | --- | --- |
| `0x295` | `CS_MATCH_STATE` | Timeout/overtime info string seeded with `\time`, `\round`, `\turn`, and `\state` keys whenever the round controller advances. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L36873-L36974` |
| `0x2A2` | `CS_FACTORY_TITLE` | Plain-text title for the active match factory, updated when factory CVars change. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L8368-L8384` |
| `0x2A3` | `CS_FACTORY_FLAGS` | Decimal bitmask exposing which factory knobs diverge from defaults. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L8160-L8170` |
| `0x2A5` | `CS_SPAWN_HINTS` | Info string with `toCount`, `sdStart`, `sdTick`, etc., so clients mirror factory respawn metadata. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L8167-L8175` |
| `0x2B3` | `CS_FORCED_COSMETICS` | Broadcasts server-forced cosmetic toggles (`sb`, `hud`, `dmg`, `atm`). | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L8023-L8050` |
| `0x2B4` | `CS_TUTORIAL_NAME` | Tutorial headline text used by the HUD tutorials. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L11895-L11903` |
| `0x2B5` | `CS_TUTORIAL_TEXT` | Tutorial body string pushed alongside the headline. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L11889-L11897` |
| `0x2B6` | `CS_FREEZE_TIP_OBJECTIVE` | Freeze Tag objective hint, refreshed when round states change. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L7202-L7210` |
| `0x2B7` | `CS_FREEZE_TIP_THAW` | Freeze Tag thawing hint string. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L7207-L7215` |
| `0x2B8` | `CS_FREEZE_TIP_FREEZE` | Freeze Tag freezing mechanic tipline. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L11906-L11914` |
| `0x2B9` | `CS_FREEZE_TIP_SHOOT` | Freeze Tag shooting hint broadcast to clients. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L11920-L11928` |
| `0x2BA` | `CS_FREEZE_TIP_SUMMARY` | Freeze Tag summary string shown after the tutorial sequence. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L11926-L11934` |
| `0x2BC` | `CS_RACE_SCORES` | Race scoreboard payload that tracks checkpoint counts and elapsed times. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L3598-L3604` |
| `0x2BD` | `CS_RACE_INFO` | Race HUD info string paired with `race_init` to keep clients in sync. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L3598-L3604` |

Add additional entries here as more Quake Live configstrings are recovered or
when future HLIL exports expose new payloads.
