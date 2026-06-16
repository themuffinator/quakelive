# Qagame Mover Plat, Button, and Train Reconstruction - 2026-06-15

## Scope

This pass rechecked the retail `qagamex86.dll` mover band covering platforms,
buttons, path corners, and trains from `0x1005FD60` through `0x10060910`.
The current source already matched the observed behavior, so the work focused
on alias promotion and executable evidence coverage tying the Binary Ninja
HLIL, Ghidra rows, symbol map, spawn table, and `src/code/game/g_mover.c`
source together.

| Address | Retail raw name | Promoted name | Source owner |
| --- | --- | --- | --- |
| `0x1005FD60` | `FUN_1005fd60` / `sub_1005fd60` | `Touch_Plat` | `src/code/game/g_mover.c` |
| `0x1005FDA0` | `FUN_1005fda0` / `sub_1005fda0` | `Touch_PlatCenterTrigger` | `src/code/game/g_mover.c` |
| `0x1005FDD0` | `FUN_1005fdd0` / `sub_1005fdd0` | `SpawnPlatTrigger` | `src/code/game/g_mover.c` |
| `0x1005FF90` | `FUN_1005ff90` / `sub_1005ff90` | `SP_func_plat` | `src/code/game/g_mover.c` |
| `0x10060160` | `FUN_10060160` / `sub_10060160` | `Touch_ButtonKeyed` | `src/code/game/g_mover.c` |
| `0x100601C0` | `FUN_100601c0` / `sub_100601c0` | `Touch_Button` | `src/code/game/g_mover.c` |
| `0x100601F0` | `FUN_100601f0` / `sub_100601f0` | `SP_func_button` | `src/code/game/g_mover.c` |
| `0x10060400` | `FUN_10060400` / `sub_10060400` | `Think_BeginMoving` | `src/code/game/g_mover.c` |
| `0x10060420` | `FUN_10060420` / `sub_10060420` | `Reached_Train` | `src/code/game/g_mover.c` |
| `0x10060680` | `FUN_10060680` / `sub_10060680` | `Think_SetupTrainTargets` | `src/code/game/g_mover.c` |
| `0x10060850` | `FUN_10060850` / `sub_10060850` | `SP_path_corner` | `src/code/game/g_mover.c` |
| `0x10060910` | `FUN_10060910` / `sub_10060910` | `SP_func_train` | `src/code/game/g_mover.c` |

## Evidence

- `references/reverse-engineering/ghidra/qagamex86/metadata.txt`
- `references/reverse-engineering/ghidra/qagamex86/imports.txt`
- `references/reverse-engineering/ghidra/qagamex86/exports.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `src/code/game/g_mover.c`
- `src/code/game/g_spawn.c`
- `tests/test_qagame_mover_plat_button_train_parity.py`

## Observed Retail Behavior

- `Touch_Plat` and `Touch_PlatCenterTrigger` are HLIL-backed touch helpers.
  The plat touch path rejects dead or non-client entities and delays descent
  while a living client stands on a raised platform. The center trigger only
  starts its parent mover when the platform is at `MOVER_POS1`.
- `SpawnPlatTrigger` is a committed Ghidra row
  `FUN_1005fdd0,1005fdd0,448,0,unknown`. It spawns a `plat_trigger`, wires
  `Touch_PlatCenterTrigger`, sets trigger contents, parents it to the platform,
  builds the inset 33-unit XY trigger with the +8 Z cap, applies the 1-unit
  fallback for narrow platforms, and links the trigger.
- `SP_func_plat` is an HLIL-backed spawn constructor and retail spawn-table
  target at `data_10080594`. It assigns platform sounds, reads speed/damage/
  wait/lip/height spawnvars, computes bottom/top positions, initializes the
  binary mover, wires the top touch and blocked handlers, and auto-spawns the
  center trigger for untargeted plats.
- `Touch_ButtonKeyed` is a committed Ghidra row
  `FUN_10060160,10060160,82,0,unknown`. It gates on a client touch, requires
  the button to be at rest, then accepts silver/master or gold/master key masks
  according to the keyed spawnflags before forwarding to `Use_BinaryMover`.
- `Touch_Button` is an HLIL-backed helper that forwards client touches to the
  binary mover only when the button is at `MOVER_POS1`.
- `SP_func_button` is a committed Ghidra row
  `FUN_100601f0,100601f0,513,0,unknown`. It assigns the switch sound, defaults
  speed and wait, computes `pos1`/`pos2` from angle, size, and lip, then selects
  keyed touch, shootable, or normal touch behavior before `InitMover`.
- `Think_BeginMoving` is an HLIL-backed wait-complete helper that restores
  `TR_LINEAR_STOP` and stamps the train trajectory time after a path-corner
  wait expires.
- `Reached_Train` is a committed Ghidra row
  `FUN_10060420,10060420,603,0,unknown`. It advances to the next corner, fires
  corner targets, copies the next path pair into `pos1`/`pos2`, clamps speed,
  computes duration, copies corner loop sound, starts the mover, and schedules
  `Think_BeginMoving` when the corner has a wait.
- `Think_SetupTrainTargets` is a committed Ghidra row
  `FUN_10060680,10060680,452,0,unknown`. It resolves the first corner, preserves
  the missing-target diagnostics, searches only `path_corner` targets, links
  the circular `nextTrain` chain, and calls `Reached_Train`.
- `SP_path_corner` and `SP_func_train` are committed Ghidra rows at
  `0x10060850` and `0x10060910`. The path-corner spawn frees unnamed corners.
  The train spawn clears angles, applies `TRAIN_BLOCK_STOPS`, defaults damage
  and speed, requires a target, initializes the mover, wires `Reached_Train`,
  and defers path setup by one frame.

## Source Mapping

This pass made the mapping explicit by:

- adding aliases for every raw `FUN_` and `sub_` name in the selected mover
  range;
- adding a focused parity gate that checks alias rows, symbol-map signatures,
  committed Ghidra sizes where available, representative HLIL anchors,
  source bodies, and retail spawn-table ordering;
- distinguishing the committed Ghidra rows from smaller HLIL-only helpers.

No C source patch was needed.

## Confidence

Focused `g_mover.c` plat/button/train mapping confidence:
**before 83% -> after 99%**.

Focused source reconstruction confidence:
**before 97% -> after 99%**.

Repo-wide parity remains **99%**. This pass closes a local qagame mover
evidence freshness gap without changing the strict-retail Windows replacement
score.
