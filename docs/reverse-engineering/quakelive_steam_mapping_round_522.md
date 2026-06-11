# Quake Live Steam Mapping Round 522: Cgame Weapon Fire/Impact/Tracer Sounds

## Scope

This pass tightens the cgame weapon sound path that spans weapon attachment
loops, fire-event sounds, impact sounds, damage-through impact fallthrough, and
machinegun tracer playback.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x10052250` | `FUN_10052250` / `sub_10052250` | `CG_MachinegunSpinAngle` | High |
| `0x10052420` | `FUN_10052420` / `sub_10052420` | `CG_AddPlayerWeapon` | High |
| `0x10053DE0` | `FUN_10053de0` / `sub_10053de0` | `CG_FireWeapon` | High |
| `0x10053EF0` | `FUN_10053ef0` / `sub_10053ef0` | `CG_MissileHitWall` | High |
| `0x10054DB0` | `FUN_10054db0` / `sub_10054db0` | `CG_MissileHitWallDmgThrough` | High |
| `0x10055C00` | `FUN_10055c00` / `sub_10055c00` | `CG_Tracer` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` lists the
  helper sizes as `242`, `2231`, `266`, `3471`, `1657`, and `951` bytes.
- `references/symbol-maps/cgame.json` already identifies the same retail
  starts with the promoted cgame weapon helper names.
- Binary Ninja HLIL for `sub_10052250` preserves the `SPIN_SPEED` /
  `COAST_TIME` barrel math and calls the cgame start-sound import at offset
  `0x94` on channel `2` for the chaingun wind-down sound.
- HLIL for `sub_10052420` registers the weapon, uses import offset `0xac` for
  held-fire and ready looping sounds, and calls `sub_10052250` when attaching
  the spinning barrel.
- HLIL for `sub_10053de0` validates the weapon number, records
  `muzzleFlashTime`, starts a random flash sound on channel `2`, starts the
  quad sound on channel `4`, and preserves the brass-ejection callback gate.
- HLIL for `sub_10053ef0` selects impact sounds by weapon/surface class and
  starts them through import offset `0x94` at `ENTITYNUM_WORLD`.
- HLIL for `sub_10054db0` falls through to `sub_10053ef0` after its
  damage-through backside mark/spark work.
- HLIL for `sub_10055c00` keeps the short-line guard, adds the tracer quad
  through the renderer import, and starts `tracerSound` at the midpoint.

Inferred meaning:

- The source-side `trap_S_StartSound` and `trap_S_AddLoopingSound` calls in
  `cg_weapons.c` are retail-aligned for the weapon sound path. The test pins
  call order and import-slot evidence rather than relying only on symbol names.
- The `sub_...` aliases are stable enough to promote because the symbol map,
  Ghidra rows, HLIL callsites, media paths, and reconstructed source behavior
  all agree.

## Reconstruction

- Promoted missing `sub_...` aliases for the six weapon sound helpers in
  `references/analysis/quakelive_symbol_aliases.json`.
- Extended `tests/test_cgame_sound_wiring_parity.py` so the helper table now
  checks both alias families and Ghidra function sizes for this weapon band.
- Added a dedicated sound wiring parity test that pins:
  - chaingun barrel coast math and wind-down sound;
  - world-model held-fire and ready looping sounds;
  - fire-event muzzle flash timing, flash sound randomization, quad playback,
    and brass-ejection gating;
  - impact sound selection for nailgun, lightning, explosives, grapple,
    shotgun, chaingun, and machinegun branches;
  - damage-through fallthrough into normal wall-impact handling;
  - tracer line length guard, render submission, midpoint sound playback, and
    tracer/wind-down media registration.

No C source changes were needed.

## Remaining Boundary

The `CG_MissileHitWall` HLIL body has unresolved stack-usage annotations and
some compressed switch artifacts. The source-level branch names are therefore
treated as reconstructed meaning, while the committed guard anchors the retail
entry point, import slot, size, callsite, and observable sound-selection
surface.

## Validation

- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_weapon_fire_impact_and_tracer_sounds_match_retail_wiring -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_impact_effect_parity.py::test_cgame_normal_impact_switch_and_media_registration_stay_wired tests\test_cgame_impact_effect_parity.py::test_cgame_damage_through_impact_sparks_match_retail_surfacepuff_path -q --tb=short`
- `python -m pytest tests\test_game_weapon_parity.py::test_chaingun_full_server_and_cgame_wiring_matches_retail -q --tb=short`

## Parity Estimate

- Focused cgame weapon fire/impact/tracer sound mapping confidence:
  **before 83% -> after 97%**.
- Focused weapon-sound helper alias/function-size coverage:
  **before 78% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.1% -> after 93.2%**.
