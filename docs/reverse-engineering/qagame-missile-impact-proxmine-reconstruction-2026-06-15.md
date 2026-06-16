# Qagame Missile Impact and Proxmine Reconstruction - 2026-06-15

## Scope

This pass rechecked the retail `qagamex86.dll` missile impact and proximity
mine core from `0x1005B350` through `0x1005BBE0`. The current source already
contained the reconstructed behavior; this pass promoted the missing raw
aliases and added executable coverage that ties the Binary Ninja HLIL, Ghidra
function rows, symbol map, and `src/code/game/g_missile.c` source together.

| Address | Retail raw name | Promoted name | Source owner |
| --- | --- | --- | --- |
| `0x1005B350` | `FUN_1005b350` / `sub_1005b350` | `G_BounceMissile` | `src/code/game/g_missile.c` |
| `0x1005B500` | `FUN_1005b500` / `sub_1005b500` | `G_ExplodeMissile` | `src/code/game/g_missile.c` |
| `0x1005B730` | `FUN_1005b730` / `sub_1005b730` | `ProximityMine_Explode` | `src/code/game/g_missile.c` |
| `0x1005B7A0` | `FUN_1005b7a0` / `sub_1005b7a0` | `ProximityMine_Die` | `src/code/game/g_missile.c` |
| `0x1005B7C0` | `FUN_1005b7c0` / `sub_1005b7c0` | `ProximityMine_Trigger` | `src/code/game/g_missile.c` |
| `0x1005B8A0` | `FUN_1005b8a0` / `sub_1005b8a0` | `ProximityMine_Activate` | `src/code/game/g_missile.c` |
| `0x1005B9D0` | `FUN_1005b9d0` / `sub_1005b9d0` | `ProximityMine_ExplodeOnPlayer` | `src/code/game/g_missile.c` |
| `0x1005BAB0` | `FUN_1005bab0` / `sub_1005bab0` | `ProximityMine_Player` | `src/code/game/g_missile.c` |
| `0x1005BBE0` | `FUN_1005bbe0` / `sub_1005bbe0` | `G_MissileImpact` | `src/code/game/g_missile.c` |

## Evidence

- `references/reverse-engineering/ghidra/qagamex86/metadata.txt`
- `references/reverse-engineering/ghidra/qagamex86/imports.txt`
- `references/reverse-engineering/ghidra/qagamex86/exports.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `src/code/game/g_missile.c`
- `tests/test_qagame_missile_impact_proxmine_parity.py`

## Observed Retail Behavior

- `G_BounceMissile` is a committed Ghidra row
  `FUN_1005b350,1005b350,423,0,unknown`. The HLIL reflects the trajectory
  delta at hit time, mirrors velocity across the impact plane, applies the
  `EF_BOUNCE_HALF` `0.65` scale, stops low-energy floor bounces, and rewrites
  the missile base/time from the updated current origin.
- `G_ExplodeMissile` is a committed Ghidra row
  `FUN_1005b500,1005b500,533,0,unknown`. Retail evaluates and snaps the
  missile origin, emits `EV_MISSILE_MISS` with an upward direction byte, marks
  the entity `freeAfterEvent`, applies splash damage, updates owner accuracy
  counters, and relinks the entity.
- `ProximityMine_Explode` and `ProximityMine_Die` are HLIL-backed wrappers.
  The explosion wrapper forwards into `G_ExplodeMissile` and frees the
  activator trigger. The die callback schedules `ProximityMine_Explode` on the
  next frame.
- `ProximityMine_Trigger` is a committed Ghidra row
  `FUN_1005b7c0,1005b7c0,221,0,unknown`. It rejects non-clients, checks the
  spherical radius inside the trigger cube, rejects same-team clients in team
  modes, gates through `CanDamage`, emits `EV_PROXIMITY_MINE_TRIGGER`, arms the
  parent mine for the short trigger delay, and frees the trigger.
- `ProximityMine_Activate` is an HLIL-backed helper. It converts the mine into
  a ticking damageable entity, sets the timeout, installs `ProximityMine_Die`,
  starts the ticking loop sound, spawns the `proxmine_trigger` child, sizes it
  from splash radius, and stores the child through `ent->activator`.
- `ProximityMine_ExplodeOnPlayer` is an HLIL-backed helper. It clears the
  victim ticking flag, handles the invulnerability juiced path with
  `DAMAGE_NO_KNOCKBACK` and `EV_JUICED`, otherwise makes the hidden mine
  visible again and tailcalls `G_ExplodeMissile`.
- `ProximityMine_Player` is a committed Ghidra row
  `FUN_1005bab0,1005bab0,292,0,unknown`. It handles already-hidden mines,
  stacks damage/radius onto an existing ticking player mine, otherwise hides
  the mine on the player, marks both sides with the ticking state, and schedules
  `ProximityMine_ExplodeOnPlayer` using the retail invulnerability-aware delay
  split.
- `G_MissileImpact` is a committed Ghidra row
  `FUN_1005bbe0,1005bbe0,3347,0,unknown`. The retail body preserves bounce,
  mover bounce, invulnerability reflection, direct damage and accuracy, proxmine
  player or surface stick, grapple hook conversion, hit/miss event selection,
  Quake Live damage-through-surface event selection, configurable splash origin
  offsets, and final splash damage/relink behavior.

## Source Mapping

The existing source matched the retail evidence. This pass made the mapping
explicit by:

- adding alias rows for the raw `FUN_` and `sub_` names in the missile impact
  and proxmine range;
- adding a focused parity test that checks alias rows, symbol-map signatures,
  committed Ghidra sizes where available, representative HLIL anchors, and the
  source bodies for bounce, explosion, proxmine lifecycle, and impact handling;
- recording the evidence distinction between committed Ghidra rows and
  HLIL-only helper bodies instead of forcing unstable claims.

No C source patch was needed.

## Confidence

Focused `g_missile.c` missile impact/proxmine mapping confidence:
**before 84% -> after 99%**.

Focused source reconstruction confidence:
**before 97% -> after 99%**.

Repo-wide parity remains **99%**. This pass closes a local qagame missile
evidence freshness gap without changing the strict-retail Windows replacement
score.
