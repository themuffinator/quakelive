# Botlib Goal Item Mapping - 2026-06-06

## Scope

This pass maps the `be_ai_goal.c` item configuration, level-item heap,
info-entity, avoid-goal, dynamic entity-item update, and LTG/NBG selection
corridor against the retail `quakelive_steam.exe` botlib image. The owning
retail binary is `quakelive_steam.exe`; the committed Binary Ninja HLIL and
Ghidra function table were sufficient, so no game launch was needed.

No C source rewrite is currently justified. The checked-in GPL-derived
implementation already matches the static retail shape in this corridor. The
work in this tranche is alias promotion, mapping documentation, and focused
parity coverage for botlib/game/server wiring.

## Evidence Inputs

- Canonical binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Source owners:
  `src/code/botlib/be_ai_goal.c`,
  `src/code/botlib/be_interface.c`,
  `src/code/game/botlib.h`,
  `src/code/game/g_local.h`,
  `src/code/game/g_public.h`,
  `src/code/game/g_syscalls.c`,
  `src/code/game/ai_dmq3.c`,
  `src/code/server/sv_game.c`,
  and `src/code/server/ql_game_imports.inc`

## Promoted Names

| Retail address | Promoted name | Evidence summary |
|---|---|---|
| `sub_49D010` | `ItemWeightIndex` | Allocates one `int` per iteminfo, calls `FindFuzzyWeight` for every item classname, and logs missing fuzzy weights. |
| `sub_49D080` | `InitLevelItemHeap` | Reads `max_levelitems`, allocates the `levelitem_t` heap, and links the free-list head through `freelevelitems`. |
| `sub_49D110` | `BotFreeInfoEntities` | Frees the map-location and camp-spot lists and clears their global heads before info-entity reinitialization. |
| `sub_49DB00` | `BotAddToAvoidGoals` | Updates matching avoid-goal slots first, then replaces expired slots using `AAS_Time() + avoidtime`. |

The existing aliases for `BotLoadItemConfig`, `BotInitInfoEntities`,
`BotInitLevelItems`, `BotGoalName`, avoid-goal public helpers,
`BotUpdateEntityItems`, `BotChooseLTGItem`, and `BotChooseNBGItem` were
rechecked in the same evidence band.

The 2026-06-11 goal/fuzzy bridge recheck promotes matching Ghidra `FUN_*`
aliases for every committed row in the surrounding `0x0049C6C0..0x0049F920`
goal band, including genetic selection, goal fuzzy-logic interbreed/save/mutate
helpers, goal-stack helpers, item weights, and goal-state lifecycle owners.

## Observed Retail Shape

Ghidra rows pin the main goal-item band:

- `FUN_0049cd80,0049cd80,646,0,unknown` -> `BotLoadItemConfig`
- `FUN_0049d010,0049d010,102,0,unknown` -> `ItemWeightIndex`
- `FUN_0049d080,0049d080,141,0,unknown` -> `InitLevelItemHeap`
- `FUN_0049d110,0049d110,91,0,unknown` -> `BotFreeInfoEntities`
- `FUN_0049d180,0049d180,568,0,unknown` -> `BotInitInfoEntities`
- `FUN_0049d3c0,0049d3c0,1395,0,unknown` -> `BotInitLevelItems`
- `FUN_0049db00,0049db00,147,0,unknown` -> `BotAddToAvoidGoals`
- `FUN_0049dd00,0049dd00,233,0,unknown` -> `BotSetAvoidGoalTime`
- `FUN_0049e070,0049e070,1292,0,unknown` -> `BotUpdateEntityItems`
- `FUN_0049e870,0049e870,1315,0,unknown` -> `BotChooseLTGItem`
- `FUN_0049eda0,0049eda0,1562,0,unknown` -> `BotChooseNBGItem`
- The bridge recheck additionally pins rows from
  `FUN_0049c6c0,0049c6c0,321,0,unknown` through
  `FUN_0049f920,0049f920,153,0,unknown`, with each `FUN_*` alias resolving to
  the same owner as the already-promoted Binary Ninja `sub_*` name.

Binary Ninja HLIL confirms the following ownership and ordering facts:

- `sub_49D010` walks the iteminfo array and calls the fuzzy-weight lookup
  helper on each item classname.
- `sub_49D080` frees any old heap, reads the `max_levelitems` libvar, allocates
  the cleared heap, and constructs the free-list chain.
- `sub_49D110` releases both `maplocations` and `campspots`.
- `sub_49D180` calls the info-entity cleanup path before enumerating BSP
  entities for `target_location` and `info_camp` records.
- `sub_49D3C0` calls `BotInitInfoEntities` and `InitLevelItemHeap` before the
  AAS-loaded check, then enumerates item entities and emits the retail
  `found %d level items` diagnostic.
- `sub_49DB00` computes avoid expiry through `AAS_Time` and writes the
  avoid-goal number/time pair.
- `sub_49E070` maps dynamic entity items back onto level items, retires stale
  dropped items, and links new dropped items with the retail timeout path.
- `sub_49E870` and `sub_49EDA0` share the expected selection pattern:
  item-weight evaluation, travel-time scaling, avoid-goal checks, and final
  goal-stack push.

## Source Reconstruction Notes

- `LoadItemConfig` still carries the retail parser shape: `max_iteminfo`,
  `PC_SetBaseFolder(BOTFILESBASEFOLDER)`, `iteminfo` structure parsing, and
  the original `counldn't load` diagnostic spelling.
- `InitLevelItemHeap` retains the `max_levelitems` libvar and free-list heap
  layout rather than replacing it with a growable container.
- `BotInitLevelItems` preserves model-index refresh, BSP item enumeration,
  spawnflag handling, `item_botroam`, floating/jumppad handling,
  `AAS_DropToFloor`, `AAS_BestReachableArea`, and list insertion.
- `BotSetAvoidGoalTime` preserves the retail negative-avoid-time path that
  derives the avoid duration from item respawn data, plus the minimum/default
  clamp behavior.
- `BotUpdateEntityItems` preserves dropped-item timeout, entity-number reuse
  detection, relinking for moved entity items, and area avoidance for jumppad
  items.
- The small source-visible helpers `AllocLevelItem`, `FreeLevelItem`,
  `AddLevelItemToList`, `RemoveLevelItemFromList`, and
  `BotFindEntityForLevelItem` were not promoted. Inference: the committed
  retail function rows represent those operations inside larger owners such as
  `BotInitLevelItems` and `BotUpdateEntityItems`, so separate aliases would
  overstate the evidence.

## Wiring

`Init_AI_Export` exposes the goal-item public API block in the same order as
`ai_export_t`. `Export_BotLibLoadMap` calls `BotInitLevelItems` before brush
model type setup. The qagame legacy syscall bridge, Quake Live native import
IDs `153..160`, server VM dispatch, and `ql_game_imports.inc` direct wrappers
all route the goal-item API back to the botlib export surface.

The HLIL export table anchors the relevant slots:

- `arg1[0x26] = sub_49E870` -> `BotChooseLTGItem`
- `arg1[0x27] = sub_49EDA0` -> `BotChooseNBGItem`
- `arg1[0x2a] = sub_49DDF0` -> `BotGetLevelItemGoal`
- `arg1[0x2b] = sub_49E000` -> `BotGetNextCampSpotGoal`
- `arg1[0x2c] = sub_49DF80` -> `BotGetMapLocationGoal`
- `arg1[0x2d] = sub_49DC40` -> `BotAvoidGoalTime`
- `arg1[0x2e] = sub_49DD00` -> `BotSetAvoidGoalTime`
- `arg1[0x2f] = sub_49D3C0` -> `BotInitLevelItems`
- `arg1[0x30] = sub_49E070` -> `BotUpdateEntityItems`

Qagame consumers were also pinned: `BotDontAvoid` iterates
`trap_BotGetLevelItemGoal` results and removes matching avoid goals, while the
camp-spot logic walks `trap_BotGetNextCampSpotGoal`.

## Validation

Added `tests/test_botlib_goal_item_parity.py` to pin:

1. Alias promotions, Ghidra function sizes, HLIL headers, helper call sites,
   and export-table slot assignments.
2. Source shape for item config loading, fuzzy-weight indexing, level-item
   heap setup, info-entity cleanup/enumeration, level-item initialization,
   avoid-goal mutation, dynamic entity-item updates, and LTG/NBG item
   selection.
3. Public AI export order, qagame legacy syscall mapping, Quake Live native
   import IDs, server VM dispatch, native import slab entries, and direct
   native wrappers.
4. Qagame consumer loops that use level-item and camp-spot goal APIs.

The 2026-06-11 bridge recheck extends the first parity gate to cover all 39
committed Ghidra rows in the goal/fuzzy/item band and requires both `sub_*` and
`FUN_*` aliases for each row.

Focused validation:

```text
python -m pytest tests/test_botlib_goal_item_parity.py -q
```

Observed result:

```text
4 passed in 0.41s
```

## Confidence

High for static ownership, helper naming, export order, and game/server
routing. Remaining uncertainty is live map-specific AAS item behavior, dynamic
dropped-item behavior, and tactical selection quality, not the static
ownership or API routing covered by this pass.

## Parity Estimate

- Focused goal item heap/info-entity/avoid-selection corridor:
  approximately `79% -> 95%`.
- Overall botlib plus goal-item export/import wiring:
  approximately `88% -> 89%`.
