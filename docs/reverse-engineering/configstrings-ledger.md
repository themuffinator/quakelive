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

## Forced cosmetics and tutorial broadcasts

- The HLIL routine that publishes `CS_FORCED_COSMETICS` builds an info string
  containing `sb`, `hud`, `dmg`, and optional `atm` keys; in the reimpl the
  same payload is assembled inside `G_UpdateForcedCosmeticsConfigstring()` and
  pushed whenever the tracked CVars (`g_forceSmallScoreboardMessage`,
  `g_forceSendConfigstring`, `g_forceDmgThroughSurface`, `g_forcedAtmosphere`)
  change or when the worldspawn `atmosphere` key is parsed through
  `G_SetWorldspawnAtmosphere()`.【F:src/code/game/g_main.c†L134-L166】【F:src/code/game/g_main.c†L1213-L1244】【F:src/code/game/g_main.c†L1324-L1345】【F:src/code/game/g_spawn.c†L930-L979】
- Clients react to the broadcast via `CG_ParseForcedCosmetics()` after
  `CG_ConfigStringModified()` sees a `CS_FORCED_COSMETICS` update, flipping the
  HUD coaching widgets, compact scoreboard notice, and damage-through-surface
  toggle while propagating any `atm` override to the local atmosphere state.
  The parser now tracks previous damage state so clearing the flag prints the
  correct restoration message.【F:src/code/cgame/cg_servercmds.c†L1092-L1155】【F:src/code/cgame/cg_servercmds.c†L1315-L1366】
- `G_UpdateGametypeTutorialText()` mirrors the HLIL tutorial routine by
  clearing all tutorial configstrings (`CS_TUTORIAL_NAME`, `CS_TUTORIAL_TEXT`,
  and the `CS_FREEZE_TIP_*` block) before repopulating them from the gametype
  tutorial table; it is run during level init and whenever CVars refresh in
  `G_UpdateCvars()`.【F:src/code/game/g_main.c†L3803-L3838】【F:src/code/game/g_main.c†L1324-L1345】
- The client draws the tutorial headline/body directly from
  `CS_TUTORIAL_NAME`/`CS_TUTORIAL_TEXT` inside `CG_DrawPregameCoach()`, but the
  Freeze Tag tip configstrings are not parsed anywhere yet, leaving those HLIL
  payloads unused client-side. Aligning with HLIL would require adding
  `CG_ConfigStringModified()` handlers for `CS_FREEZE_TIP_*` and plumbing the
  strings into the HUD widgets that expect them.【F:src/code/cgame/cg_newdraw.c†L3505-L3546】【F:src/code/cgame/cg_servercmds.c†L1315-L1366】

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
