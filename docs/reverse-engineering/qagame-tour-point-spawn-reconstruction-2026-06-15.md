# Qagame Tour Point Spawn Reconstruction - 2026-06-15

## Scope

This pass rechecked the Quake Live tutorial `info_tour_point` spawn band in the
retail `qagamex86.dll` corpus and promoted the existing source reconstruction
from source-shaped confidence to pinned source-backed mapping. The focused
range is `0x10059FD0` and `0x1005A1F0`:

| Address | Retail raw name | Promoted name | Source owner |
| --- | --- | --- | --- |
| `0x10059FD0` | `FUN_10059fd0` / `sub_10059fd0` | `FinishSpawningTourPoint` | `src/code/game/g_misc.c` |
| `0x1005A1F0` | `sub_1005a1f0` | `SP_info_tour_point` | `src/code/game/g_misc.c` |

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
- `tests/test_qagame_tour_point_spawn_parity.py`

## Observed Retail Behavior

- `FinishSpawningTourPoint` is a committed Ghidra row
  `FUN_10059fd0,10059fd0,541,0,unknown` and a Binary Ninja HLIL function
  beginning at `0x10059FD0`.
- When spawnflag `0x80` is set, the finisher builds the entity bounds from
  current origin plus mins/maxs, calls the qagame `EntitiesInBox` import, and
  hides overlapping `ET_ITEM` entities except item types `7` and `8`, matching
  source `IT_PERSISTANT_POWERUP` and `IT_TEAM`.
- The same finisher walks entities sharing the tour point `targetname` and
  hides linked tutorial entities that already have `target_ent`.
- The finisher resolves `tourPointTarget` through the targetname search helper
  and preserves the missing target diagnostic before linking the point.
- `SP_info_tour_point` is an HLIL-only row at `0x1005A1F0` and the qagame
  spawn table entry at `data_10080714`.
- `SP_info_tour_point` frees a non-start point with no
  `tourPointTargetName`, reads `radius`, `cvarValue`, `printChatTextTime`,
  `ignorePlayerLocation`, and `noise`, initializes the general entity bounds
  `(-16, -16, -24)..(16, 16, 32)`, and defers linkage to
  `FinishSpawningTourPoint`.

## Source Mapping

The existing `g_misc.c` implementation already carried the reconstructed
behavior. This pass makes that evidence explicit by:

- adding `FUN_10059fd0`, `sub_10059fd0`, and `sub_1005a1f0` aliases;
- updating the qagame symbol-map comments and string references for both
  functions;
- adding a focused parity gate that checks alias rows, the committed Ghidra
  size for `FinishSpawningTourPoint`, HLIL anchors for the hide/resolve/defer
  paths, source bodies for the helper, finisher, and spawn constructor, and the
  `g_spawn.c` `info_tour_point` dispatch slot.

## Confidence

Focused `info_tour_point` spawn/finish mapping confidence:
**before 88% -> after 99%**.

Focused source reconstruction confidence:
**before 96% -> after 99%**. No C source patch was needed because the body was
already reconstructed; the improvement is from alias promotion, string-ref
correction, and executable source/evidence coverage.

Repo-wide parity remains **99%**. The strict-retail Windows target remains
closed; this pass reduces a local evidence freshness gap in qagame tutorial
entity spawning.
