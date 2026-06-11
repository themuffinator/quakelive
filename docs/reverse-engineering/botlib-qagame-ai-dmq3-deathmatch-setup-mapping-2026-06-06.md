# Botlib Qagame AI DMQ3 Deathmatch Setup Mapping - 2026-06-06

## Scope

This pass extends the qagame-side botlib mapping past the activate/obstacle
slice into the deathmatch think loop, deathmatch setup bootstrap, entity-goal
binding helper, adjacent `ai_main.c` wrappers, and tutorial support helpers.
The owning retail binary is `qagamex86.dll`; the primary mapped ranges are
`0x1001F050..0x1001FEC0` and `0x10020980..0x10020EC0`.

Update 2026-06-11: `BotAcceptOffscreenEnemyCandidate` is no longer a
mapped-only retail helper. It is reconstructed in source and wired through
`BotFindEnemy`, `BotCheckEvents`, and selected-bot telemetry. One analysis
correction from the original pass remains: the `BotSetEntityNumForGoal`
symbol-map comment reflects the retail-preserved classname guard actually
present in both HLIL and source, where exact classname matches are skipped and
absent or non-matching classnames fall through to the distance check.

Second update 2026-06-11: `BotResolveTourPoint` and `BotCanSpawnTourPoint` are
also source-backed. The resolver preserves the retail current-tour-point and
fallback-start-point branches, the 8192-unit floor trace, the 16-unit origin
lift, and linked `info_notnull` target-origin resolution. The spawn gate
preserves the retail raw entity-slab scan for free slots whose `freetime + 2000`
has expired against `level.time`.

Third update 2026-06-11: `BotSelectTormentTarget` is now source-backed. The
reconstruction preserves the cached enemy revalidation, the first human-only
`PM_NORMAL` reachability scan, the trace-assisted reachability fallback, and
the nearest-human final fallback used by the retail tutorial torment node.

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
| `0x1001F9C0` | `BotSelectTormentTarget` | `ai_dmq3.c` | 1262 |
| `0x1001FEC0` | `BotResolveTourPoint` | `ai_dmq3.c` | 825 |
| `0x10020980` | `BotAI_Print` | `ai_main.c` | 298 |
| `0x10020AC0` | `BotAI_Trace` | `ai_main.c` | 219 |
| `0x10020BA0` | `BotAI_GetClientState` | `ai_main.c` | 54 |
| `0x10020BE0` | `BotClientHasNoTargetFlag` | `ai_dmq3.c` | 46 |
| `0x10020C10` | `BotAcceptOffscreenEnemyCandidate` | `ai_dmq3.c` | 341 |
| `0x10020D70` | `BotAI_GetEntityState` | `ai_main.c` | 79 |
| `0x10020DC0` | `BotAI_BotInitialChat` | `ai_main.c` | 255 |
| `0x10020EC0` | `BotCanSpawnTourPoint` | `ai_dmq3.c` | 61 |

There are no mapped-only helpers left in this focused deathmatch/setup helper
band. The larger tutorial nodes that call into these helpers are still tracked
in the adjacent `ai_dmnet.c` tutorial-tail mapping.

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
- `BotAcceptOffscreenEnemyCandidate` preserves the retail offscreen enemy
  side path reached only after `BotFindEnemy` receives a non-positive
  `BotEntityVisible` score. The reconstructed helper requires no current
  enemy, no retreat decision, a positive chase decision, no blocking top or
  second goal-stack entity, skill at least `4.0`, and a matching heard-client
  event bit before accepting the unseen candidate.
- `BotSelectTormentTarget` preserves the retail torment-human target selector:
  revalidate `bs->enemy` only when it remains 360-degree visible and reachable
  inside the caller's `maxDist`, scan all 64 client slots for non-bot
  `PM_NORMAL` humans reachable through `BotPointAreaNum`, fall back to
  `trap_AAS_PointReachabilityAreaIndex` plus a 24-unit `trap_AAS_TraceAreas`
  probe, then choose the nearest valid non-bot human when no reachable target
  was found. All travel checks use the retail `0x011C0FBE` mask.
- `BotResolveTourPoint` preserves the retail tutorial tour-point resolver:
  valid current entities search by the current entity's `target` into
  `info_tour_point` `targetname`s, invalid/currentless calls select the first
  spawnflag-1 `info_tour_point`, the chosen point is traced down 8192 units and
  lifted 16 units, and the optional target vector comes from the linked
  `info_notnull` entity.
- `BotCanSpawnTourPoint` preserves the retail tutorial marker spawn gate:
  scan non-client entity slots from `MAX_CLIENTS` to `ENTITYNUM_MAX_NORMAL`,
  require `!ent->inuse`, and accept only once `ent->freetime + 2000 <=
  level.time`.

Retail-only coverage that still remains outside this file is concentrated in
the larger `AINode_Torment_Human` caller and neighboring tutorial nodes.

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

```text
python -m pytest tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py -q --tb=short
5 passed in 0.20s

python -m pytest tests -k botlib -q --tb=short
205 passed, 1861 deselected in 20.79s
```

## Parity Estimate

- Focused qagame deathmatch/setup and adjacent ai_main alias coverage:
  **before 0% -> after 100%** for the newly guarded rows in this pass.
- Focused source-owned deathmatch/setup/wrapper parity confidence:
  **before 91% -> after 99%** after pinning source bodies to HLIL and
  symbol-map metadata.
- Focused torment target selector source reconstruction confidence:
  **before 0% -> after 89%**. Remaining uncertainty is limited to exact retail
  stack-local artifacts and live training-node behavior, not the documented
  branch structure.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 97.1% -> after 97.4%**. Remaining uncertainty is concentrated in
  retail-only tutorial node bodies and broader live validation, not this
  source-owned deathmatch setup slice.
