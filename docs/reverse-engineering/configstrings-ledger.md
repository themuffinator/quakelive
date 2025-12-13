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
| `0x2A6` | `CS_MAP_AUTHOR` | Human-readable map author mirrored from the worldspawn `author` key. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L23205-L23215` |
| `0x2A7` | `CS_MAP_AUTHOR_ALT` | Secondary author credit sourced from the optional `author2` key. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L23210-L23234` |
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
| `0x2BF` | `CS_MATCH_AWARDS` | Serialized feed of medal/award info (accuracy, perfect, etc.) built before the award temp-entity is spawned. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L22080-L22166` |
| `0x2C0` | `CS_CUSTOM_SETTINGS` | Info string of custom factory settings (loadout toggles, overrides) pushed when the match controller initializes. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L10997-L11005` |
| `0x2C1` | `CS_ROTATION_TITLES` | Rotation preview payload that concatenates `map_%i`, `title_%i`, and `gt_%i` slots for the next-map UI. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12692-L12745` |
| `0x2C2` | `CS_ROTATION_CONFIGS` | Companion info string containing the queued `cfg_%i` data used to reconstruct the rotation presets client-side. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12692-L12745` |
| `0x2C3` | `CS_SUDDENDEATH_STATUS` | Single-character flag flipped when the sudden-death timer fires and cleared when the controller resets votes. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L13372-L13378,L14283-L14290` |
| `0x2C4` | `CS_READYUP_STATUS` | Ready-up manager payload broadcast when the server drops back to `PRE_GAME` and clears stale toggles. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L11678-L11707` |
| `0x2C5` | `CS_SPAWN_HINTS_ALT` | Float-formatted spawn metadata updated alongside `CS_SPAWN_HINTS` for HUDs that need decimal precision. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L8498-L8509` |
| `0x2C6` | `CS_RACE_RECORDS` | Race best-time cache that resets during `race_init` before announcing fresh lap records. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L21058-L21064` |
| `0x2C7` | `CS_LOADOUT_FLAGS` | Decimal bitmask describing which loadout toggles (`g_disableLoadout`, etc.) are currently forced server-side. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L23218-L23234` |
| `0x2C9` | `CS_LOADOUT_MASK` | Per-item mask used with `CS_LOADOUT_FLAGS` so clients can hide the disabled inventory slots. | `F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L10997-L11005` |

Add additional entries here as more Quake Live configstrings are recovered or
when future HLIL exports expose new payloads.

## Rotation and loadout payload formats

- **Rotation previews:** The HLIL builder walks the `nextmaps` info string and
  writes `map_%i`, `title_%i`, and `gt_%i` keys into the `CS_ROTATION_TITLES`
  info string while mirroring the `cfg_%i` payloads into `CS_ROTATION_CONFIGS`.
  Both configstrings are flushed together after the loop finishes, mirroring
  the retail DLL’s queue preview semantics.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12692-L12747】
- **Loadout flags/masks:** `CS_LOADOUT_FLAGS` and `CS_LOADOUT_MASK` start as
  empty strings when the server boots, then `SP_worldspawn` parses the optional
  `disable_loadout` key. The parsed bitmask is formatted with `va("%i")` and
  pushed into `CS_LOADOUT_FLAGS` before mirroring the same string into the
  `g_disableLoadout` CVar. No map-specific mask is published separately in the
  HLIL traces, leaving `CS_LOADOUT_MASK` blank unless other codepaths are
  discovered.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L10992-L11009】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L23190-L23239】
- **Timing expectations:** The rotation payloads and loadout flag updates are
  emitted via `trap_SetConfigstring` immediately after their builders finish;
  the HLIL does not defer publication to later frames. Any reconstruction
  should ensure the configstrings update atomically alongside rotation changes
  or `disable_loadout` edits.

## Current gaps to close

- The game module never populates `CS_ROTATION_TITLES` or
  `CS_ROTATION_CONFIGS`; the HLIL shows both being emitted once the rotation
  queue is parsed, so a server-side publisher is still needed.
- `G_UpdateDisableLoadoutConfigstrings` currently merges the worldspawn mask
  with the `g_disableLoadout` CVar and publishes the merged value plus a map
  mask in `CS_LOADOUT_MASK`, which diverges from the HLIL’s single-mask
  broadcast.【F:src/code/game/g_spawn.c†L171-L207】【F:src/code/game/g_spawn.c†L958-L962】
- Client rotation feeders only parse UI CVars/files (`ui_mapRotation`,
  `sv_mapRotation`, etc.) and have no consumer for the server-advertised
  rotation preview fields.【F:src/code/ui/ui_gameinfo.c†L377-L660】
- HUD/loadout gating is driven solely by `g_loadout` in the serverinfo string
  and ignores the loadout configstrings that the HLIL publishes, so clients
  cannot mirror per-slot disables today.【F:src/code/cgame/cg_newdraw.c†L5045-L5064】

## HLIL-derived gametype strings

The Domination/Freeze tutorial payloads and the HUD gametype hints both reuse
strings lifted from the Binary Ninja HLIL dumps for `qagamex86.dll` and
`cgamex86.dll`. These values live in
`src/code/game/generated/ql_gametype_strings.h`, which is generated from the
`tools/hlil/gametype_strings.json` metadata via:

```
python tools/hlil/generate_gametype_strings.py
```

Re-run the script whenever the JSON is updated with new HLIL findings so the
game and client modules stay aligned.
