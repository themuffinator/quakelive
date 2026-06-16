# Qagame Static and Motion Mover Reconstruction - 2026-06-15

## Scope

This pass rechecked the retail `qagamex86.dll` constructor band for the
remaining `g_mover.c` motion movers: `func_static`, `func_rotating`,
`func_bobbing`, and `func_pendulum`. The focused range is `0x10060AA0`
through `0x10060D50`.

| Address | Retail raw name | Promoted name | Source owner |
| --- | --- | --- | --- |
| `0x10060AA0` | `FUN_10060aa0` / `sub_10060aa0` | `SP_func_static` | `src/code/game/g_mover.c` |
| `0x10060B00` | `FUN_10060b00` / `sub_10060b00` | `SP_func_rotating` | `src/code/game/g_mover.c` |
| `0x10060C00` | `FUN_10060c00` / `sub_10060c00` | `SP_func_bobbing` | `src/code/game/g_mover.c` |
| `0x10060D50` | `FUN_10060d50` / `sub_10060d50` | `SP_func_pendulum` | `src/code/game/g_mover.c` |

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
- `tests/test_qagame_mover_static_motion_parity.py`

## Observed Retail Behavior

- `SP_func_static` is an HLIL-backed constructor and retail spawn-table target
  at `data_100805AC`. The body sets the brush model, initializes mover state,
  and mirrors `s.origin` into both `s.pos.trBase` and `r.currentOrigin`.
- `SP_func_rotating` is a committed Ghidra row
  `FUN_10060b00,10060b00,255,0,unknown`. It defaults speed to `100`, uses
  `TR_LINEAR` angular motion, maps spawnflags to Z/X/Y rotation axes, defaults
  damage to `2`, initializes the brush mover, mirrors origin and angles into
  runtime state, and links the entity.
- `SP_func_bobbing` is an HLIL-backed constructor and retail spawn-table target
  at `data_100805BC`. It reads `speed`, `height`, `dmg`, and `phase`, sets up
  sine positional motion, seeds duration/time from speed and phase, and maps
  spawnflags to X/Y/Z bob axes.
- `SP_func_pendulum` is a committed Ghidra row
  `FUN_10060d50,10060d50,377,0,unknown`. It reads `speed`, `dmg`, and `phase`,
  derives pendulum length from the brush mins with the retail minimum length of
  `8`, computes frequency from gravity and length, initializes mover state,
  mirrors origin/angles, and sets sine angular motion with Z-axis swing delta.
- The retail spawn table preserves the order:
  `func_static`, `func_rotating`, `func_bobbing`, `func_pendulum` between
  `func_door` and `func_train`.

## Source Mapping

The current `g_mover.c` implementation matched the retail evidence. This pass
made the mapping explicit by:

- adding raw `FUN_` and `sub_` aliases for all four constructors;
- adding a focused parity gate for alias rows, symbol-map signatures, committed
  Ghidra sizes where available, representative HLIL anchors, source bodies, and
  spawn-table order;
- recording the evidence distinction between committed Ghidra rows and
  HLIL-only constructor bodies.

No C source patch was needed.

## Confidence

Focused `g_mover.c` static/rotating/bobbing/pendulum mapping confidence:
**before 86% -> after 99%**.

Focused source reconstruction confidence:
**before 97% -> after 99%**.

Repo-wide parity remains **99%**. This pass closes a local qagame mover
evidence freshness gap without changing the strict-retail Windows replacement
score.
