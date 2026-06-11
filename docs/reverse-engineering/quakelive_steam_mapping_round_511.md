# Quake Live Steam Mapping Round 511: Looping Sound State Wiring

## Scope

This round reconstructs and pins the sound-system looping-state boundary around
native Quake Live clear helpers, legacy cgame loop syscalls, and the
`S_AddLoopSounds` merge pass.

The source change is intentionally small: the legacy compatibility
`S_AddRealLoopingSound` path now stamps the loop sound with `cls.framecount`,
matching the retail loop-state setup path's final frame-counter write.

## Evidence

Primary evidence:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/snd_dma.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/cgame/cg_public.h`
- `src/code/cgame/cg_syscalls.c`
- `tests/test_client_sound_playback_parity.py`

Observed facts:

- Retail aliases and Ghidra rows bind the relevant helper island:
  - `sub_4DA3E0` -> `S_ClearSoundBuffer`, Ghidra `FUN_004da3e0`, size `163`.
  - `sub_4DA490` -> `S_ClearLoopingSoundsFrame`.
  - `j_sub_4DA490` -> `QLCGImport_S_ClearLoopingSoundsFrame`.
  - `j_sub_4DA3E0` -> `QLCGImport_S_ClearLoopingSoundsKillAll`.
  - `sub_4DA4C0` -> `S_AddLoopingSound`, Ghidra `FUN_004da4c0`, size `558`.
  - `sub_4DA6F0` -> `S_AddLoopSounds`, Ghidra `FUN_004da6f0`, size `328`.
- Retail `S_ClearSoundBuffer` clears the loop-state slab, loop-channel slab,
  loop-channel count, raw-stream end, voice lanes, and DMA buffer.
- Retail `S_ClearLoopingSoundsFrame` only clears the active flag for each
  loop-sound entry and resets the loop-channel count.
- The retail loop-state setup region writes origin, velocity, sfx pointer,
  active state, doppler state/scales, and finally writes the client frame
  counter from `data_1528cc0` into the loop entry.
- Binary Ninja exposes the compatibility-shaped setup block at `004da522`, but
  the committed Ghidra function table does not promote a separate
  `FUN_004da522` row. This round therefore treats it as evidence for the
  loop-state setup contract, not as a stable public alias.
- Retail `S_AddLoopSounds` clears `numLoopChannels`, increments a merge-frame
  marker, skips inactive/already-merged entries, spatializes active loops at
  master volume `0x7f`, merges duplicate non-doppler loops with the same sfx,
  clamps left/right totals to `0xff`, writes `loop_channels`, and stops when
  `MAX_CHANNELS` is reached.
- Source host wiring keeps the native and legacy paths separated:
  - Native `QL_CG_trap_S_ClearLoopingSoundsFrame` calls
    `S_ClearLoopingSoundsFrame()`.
  - Native `QL_CG_trap_S_ClearLoopingSoundsKillAll` calls
    `S_ClearSoundBuffer()`.
  - Legacy `CG_S_CLEARLOOPINGSOUNDS` calls
    `S_ClearLoopingSounds( args[1] ? qtrue : qfalse )`.
  - Legacy `CG_S_ADDREALLOOPINGSOUND` calls `S_AddRealLoopingSound(...)`.
  - QVM compatibility still exposes `CG_S_ADDREALLOOPINGSOUND` through
    `ql_cgame_imports.inc`.

## Reconstruction

Implemented changes:

- Updated `S_AddRealLoopingSound()` in `src/code/client/snd_dma.c` so the
  compatibility loop path writes
  `loopSounds[entityNum].framenum = cls.framecount;` after initializing the
  loop state.
- Extended `tests/test_client_sound_playback_parity.py` with
  `test_looping_sound_state_paths_preserve_retail_clear_merge_and_compat_frame_contract`.
- Strengthened the existing local/loop diagnostic test so the compatibility
  real-loop path must carry the frame-counter stamp.

The new focused guard binds:

- Native frame-clear and kill-all aliases.
- Absence of a promoted `FUN_004da522` row, avoiding an unstable rename.
- HLIL anchors for loop-state clear, frame clear, setup, frame-counter write,
  and merge aggregation.
- Source frame-clear versus legacy kill-all behavior.
- Source `S_AddLoopingSound`, `S_AddRealLoopingSound`, and `S_AddLoopSounds`
  ordering.
- Legacy and native cgame host import wiring for clear/add-loop paths.

## Confidence

High confidence:

- The frame-counter write is directly visible at the tail of the retail
  loop-state setup path and now exists in both source loop entry paths.
- Native frame-clear and kill-all helpers are pinned by promoted aliases,
  source wrappers, and import-table wiring.
- The loop merge pass is pinned by retail HLIL data roots, source order, and
  static tests.

Medium confidence:

- `004da522` is intentionally not promoted as a standalone source name because
  the Ghidra function table does not expose `FUN_004da522`; its evidence is
  used only to support the shared loop-state setup contract.
- The source still carries the legacy `kill` field for compatibility
  `S_ClearLoopingSounds()` behavior. This round keeps that path bounded rather
  than claiming the field layout is byte-for-byte identical to the retail
  native-only loop slab.

## Validation

Validation passed:

- `python -m pytest tests\test_client_sound_playback_parity.py::test_looping_sound_state_paths_preserve_retail_clear_merge_and_compat_frame_contract -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 10 passed.
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
  - 7 passed.
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_sound_slab_keeps_volume_slots_direct_and_legacy_slots_fixed_volume -q --tb=short`
  - 1 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. This was a static retail-mapping and
source-reconstruction pass, and the committed Binary Ninja/Ghidra evidence plus
focused source tests were sufficient.

## Parity Estimate

Focused compatibility real-loop frame-state reconstruction:

- Before: 65%
- After: 95%

Focused native/legacy loop clear and merge wiring:

- Before: 88%
- After: 98%

Overall sound-system wiring reconstruction parity:

- Before: 92.3%
- After: 92.4%
