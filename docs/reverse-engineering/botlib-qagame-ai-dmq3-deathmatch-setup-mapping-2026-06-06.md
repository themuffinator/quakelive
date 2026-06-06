# Botlib Qagame AI DMQ3 Deathmatch Setup Mapping - 2026-06-06

## Scope

This pass extends the qagame-side botlib mapping past the activate/obstacle
slice into the deathmatch think loop, deathmatch setup bootstrap, entity-goal
binding helper, adjacent `ai_main.c` wrappers, and tutorial support helpers.
The owning retail binary is `qagamex86.dll`; the primary mapped ranges are
`0x1001F050..0x1001FEC0` and `0x10020980..0x10020EC0`.

No C behavior was changed. One analysis correction was made: the
`BotSetEntityNumForGoal` symbol-map comment now reflects the retail-preserved
classname guard actually present in both HLIL and source, where exact classname
matches are skipped and absent or non-matching classnames fall through to the
distance check.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_dmq3.c`
- `src/code/game/ai_main.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py`

## Mapped Rows

### Source-Owned Rows

| Address | Promoted name | Source owner | Function size |
| --- | --- | --- | ---: |
| `0x1001F050` | `BotDeathmatchAI` | `ai_dmq3.c` | 1129 |
| `0x1001F4C0` | `BotSetEntityNumForGoal` | `ai_dmq3.c` | 185 |
| `0x1001F580` | `BotSetupDeathmatchAI` | `ai_dmq3.c` | 1079 |
| `0x10020980` | `BotAI_Print` | `ai_main.c` | 298 |
| `0x10020AC0` | `BotAI_Trace` | `ai_main.c` | 219 |
| `0x10020BA0` | `BotAI_GetClientState` | `ai_main.c` | 54 |
| `0x10020BE0` | `BotClientHasNoTargetFlag` | `ai_dmq3.c` | 46 |
| `0x10020D70` | `BotAI_GetEntityState` | `ai_main.c` | 79 |
| `0x10020DC0` | `BotAI_BotInitialChat` | `ai_main.c` | 255 |

### Mapped-Only Retail Helpers

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x1001F9C0` | `BotSelectTormentTarget` | 1262 |
| `0x1001FEC0` | `BotResolveTourPoint` | 825 |
| `0x10020C10` | `BotAcceptOffscreenEnemyCandidate` | 341 |
| `0x10020EC0` | `BotCanSpawnTourPoint` | 61 |

These four helpers have strong HLIL, size, and symbol-map evidence, but their
retail-only bodies have not been reconstructed into source in this pass. The
test intentionally treats them as mapped-only rows.

## Source Mapping Notes

Observed source anchors now pinned by tests:

- `BotDeathmatchAI` preserves setup-count staging, gender/userinfo updates,
  team command emission, chat gender/name setup, alternate-route setup,
  intermission-gated teleport/inventory/snapshot/air checks, console-message
  polling, team AI, no-node fallback, enter-game chat, node dispatch, and
  goal/avoid stack dump diagnostics.
- `BotSetEntityNumForGoal` preserves the retail/GPL classname guard as-is:
  exact classname matches continue past the candidate, while absent or
  non-matching classnames fall through to the distance-based entity binding.
  This looks counter-intuitive, but the HLIL control flow matches the current
  C source, so it is documented rather than rewritten.
- `BotSetupDeathmatchAI` preserves gametype and maxclient reads, the bot cvar
  registration cluster, CTF/1FCTF/obelisk/harvester objective goal lookup and
  warning strings, obelisk entity binding, BSP model-index scan, and waypoint
  heap initialization.
- `BotAI_Print`, `BotAI_Trace`, `BotAI_GetClientState`,
  `BotAI_GetEntityState`, and `BotAI_BotInitialChat` preserve the expected
  ai_main wrapper behavior around game printing, trace-to-BSP trace copying,
  client/player-state copying, entity-state filtering, and initial chat
  vararg packing.
- `BotClientHasNoTargetFlag` preserves the Quake Live enemy-filter guard for
  live client entities carrying `FL_NOTARGET`.

Observed retail-only helper anchors:

- `BotSelectTormentTarget` is called by `AINode_Torment_Human`, revalidates a
  cached target with 360-degree visibility, and scans client/entity candidates
  by distance and AAS reachability.
- `BotResolveTourPoint` resolves `info_tour_point` to a floor-traced origin
  and linked `info_notnull` target origin.
- `BotAcceptOffscreenEnemyCandidate` is a retail-only sidecar for hidden enemy
  candidate acceptance.
- `BotCanSpawnTourPoint` scans the tutorial marker entity slab for a free or
  expired slot and is called from the retail-expanded AAS debug/tour-point
  path.

## Botlib Wiring

The new regression pins wrapper and import-table wiring used by this band:

- Engine/game imports: cvar integer reads, cvar registration, get/set userinfo,
  and trace.
- AAS/BSP imports: next BSP entity and BSP epair key lookup.
- Botlib EA and AI imports: command emission, characteristic string lookup,
  chat gender/name setup, goal/avoid stack dumping, and level item goal lookup.
- Direct `sv_game.c` import-table entries and `ql_game_imports.inc` wrappers
  for the same calls.

## Tests

- `python -m pytest tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py -q --tb=short`

## Parity Estimate

- Focused qagame deathmatch/setup and adjacent ai_main alias coverage:
  **before 0% -> after 100%** for the newly guarded rows in this pass.
- Focused source-owned deathmatch/setup/wrapper parity confidence:
  **before 91% -> after 98%** after pinning source bodies to HLIL and
  symbol-map metadata.
- Focused retail-only tutorial helper mapping confidence:
  **before 45% -> after 82%**. These names are now pinned, but source
  reconstruction remains a separate task.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 96.7% -> after 97.1%**. Remaining uncertainty is concentrated in
  retail-only tutorial helper bodies and broader live validation, not this
  source-owned deathmatch setup slice.
