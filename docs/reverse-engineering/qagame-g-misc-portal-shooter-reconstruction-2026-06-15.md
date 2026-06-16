# Qagame Portal and Shooter Reconstruction - 2026-06-15

## Scope

This pass rechecked the contiguous `g_misc.c` portal camera/surface, map
shooter, and holdable Portal helper band in retail `qagamex86.dll`. The source
was already reconstructed; this pass promoted the raw retail names into the
alias corpus and added executable evidence coverage for the range
`0x1005A6C0` through `0x1005B190`.

| Address | Retail raw name | Promoted name | Source owner |
| --- | --- | --- | --- |
| `0x1005A6C0` | `FUN_1005a6c0` / `sub_1005a6c0` | `locateCamera` | `src/code/game/g_misc.c` |
| `0x1005A820` | `sub_1005a820` | `SP_misc_portal_surface` | `src/code/game/g_misc.c` |
| `0x1005A8C0` | `sub_1005a8c0` | `SP_misc_portal_camera` | `src/code/game/g_misc.c` |
| `0x1005A950` | `FUN_1005a950` / `sub_1005a950` | `Use_Shooter` | `src/code/game/g_misc.c` |
| `0x1005AC40` | `FUN_1005ac40` / `sub_1005ac40` | `InitShooter_Finish` | `src/code/game/g_misc.c` |
| `0x1005AC70` | `FUN_1005ac70` / `sub_1005ac70` | `InitShooter` | `src/code/game/g_misc.c` |
| `0x1005AD90` | `FUN_1005ad90` / `sub_1005ad90` | `SP_shooter_rocket` | `src/code/game/g_misc.c` |
| `0x1005ADB0` | `FUN_1005adb0` / `sub_1005adb0` | `SP_shooter_plasma` | `src/code/game/g_misc.c` |
| `0x1005ADD0` | `FUN_1005add0` / `sub_1005add0` | `SP_shooter_grenade` | `src/code/game/g_misc.c` |
| `0x1005ADF0` | `FUN_1005adf0` / `sub_1005adf0` | `DropPortalDestination` | `src/code/game/g_misc.c` |
| `0x1005AFE0` | `FUN_1005afe0` / `sub_1005afe0` | `PortalTouch` | `src/code/game/g_misc.c` |
| `0x1005B160` | `FUN_1005b160` / `sub_1005b160` | `PortalEnable` | `src/code/game/g_misc.c` |
| `0x1005B190` | `FUN_1005b190` / `sub_1005b190` | `DropPortalSource` | `src/code/game/g_misc.c` |

## Evidence

- `references/reverse-engineering/ghidra/qagamex86/metadata.txt`
- `references/reverse-engineering/ghidra/qagamex86/imports.txt`
- `references/reverse-engineering/ghidra/qagamex86/exports.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `src/code/game/g_misc.c`
- `src/code/game/g_spawn.c`
- `tests/test_qagame_misc_portal_shooter_parity.py`

## Observed Retail Behavior

- `locateCamera` is a committed Ghidra row
  `FUN_1005a6c0,1005a6c0,349,0,unknown` and a Binary Ninja HLIL function
  beginning at `0x1005A6C0`. It resolves the target camera, preserves the
  missing-target diagnostic string for `misc_partal_surface`, copies camera
  ownership and origin data into the portal surface entity state, maps camera
  spawnflags to the portal frame/powerup swing controls, and stores a
  `DirToByte` view direction.
- `SP_misc_portal_surface` and `SP_misc_portal_camera` are HLIL-backed spawn
  constructors at `0x1005A820` and `0x1005A8C0`. The retail spawn table maps
  `misc_portal_surface` to `sub_1005a820` and `misc_portal_camera` to
  `sub_1005a8c0`.
- `Use_Shooter` is a committed Ghidra row
  `FUN_1005a950,1005a950,748,0,unknown`. Its HLIL shows the enemy-or-movedir
  aim branch, two-axis random spread, weapon switch values for grenade
  launcher, rocket launcher, and plasma, and final weapon-fire event emission.
- `InitShooter_Finish` and `InitShooter` are committed Ghidra rows at
  `0x1005AC40` and `0x1005AC70`. The bootstrap helper wires `Use_Shooter`,
  stores the weapon id, registers the item, computes movedir from angles,
  normalizes random spread through sine of degrees, and schedules delayed
  target resolution when a target is present.
- The shooter spawn constructors are one-call wrappers: rocket passes weapon
  id `5`, plasma passes `8`, and grenade passes `4`. The retail spawn table
  maps `shooter_rocket`, `shooter_grenade`, and `shooter_plasma` to those
  constructors in that order.
- `DropPortalDestination` is a committed Ghidra row
  `FUN_1005adf0,1005adf0,481,0,unknown`. It creates the `hi_portal destination`
  entity, applies the teleporter exit model, copies player bounds and angles,
  schedules two-minute cleanup through `G_FreeEntity`, increments the global
  portal sequence, and returns the Portal holdable to the player.
- `PortalTouch` is a committed Ghidra row
  `FUN_1005afe0,1005afe0,384,0,unknown`. It rejects dead or non-client users,
  drops carried neutral/red/blue flags through scripted flag-drop context,
  finds a matching `hi_portal destination` by `count`, teleports to cached
  `pos1` when the destination is gone, then telefrags the user on the failed
  destination path.
- `PortalEnable` is an HLIL-backed helper at `0x1005B160`; it arms
  `PortalTouch`, swaps the think callback back to `G_FreeEntity`, and converts
  the one-second warmup into the normal two-minute cleanup timer.
- `DropPortalSource` is a committed Ghidra row
  `FUN_1005b190,1005b190,435,0,unknown`. It creates the `hi_portal source`
  entity, copies player bounds, combines corpse and trigger contents,
  transfers the player's saved portal sequence into `ent->count`, clears the
  player portal id, schedules `PortalEnable` after one second, and caches the
  paired destination origin into `pos1` when available.

## Source Mapping

The existing `g_misc.c` source matched the retail evidence. This pass makes the
mapping explicit by:

- adding aliases for all raw names in the portal/shooter range, including both
  `FUN_` and `sub_` variants where the companion corpora use both forms;
- adding a focused parity gate that checks alias rows, committed Ghidra sizes,
  HLIL function anchors, spawn table slots, and the source bodies for the
  portal surface/camera, shooter, and holdable Portal paths;
- recording the spawn-table order around `misc_portal_surface`,
  `misc_portal_camera`, `shooter_rocket`, `shooter_grenade`, and
  `shooter_plasma`.

No C source patch was needed. The reconstruction benefit comes from mapping
freshness, alias promotion, and executable evidence coverage.

## Confidence

Focused `g_misc.c` portal/shooter mapping confidence:
**before 82% -> after 99%**.

Focused source reconstruction confidence:
**before 96% -> after 99%**.

Repo-wide parity remains **99%**. This pass closes a local qagame evidence
freshness gap without changing the strict-retail Windows replacement score.
