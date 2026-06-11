# Quake Live Steam Mapping Round 491: Native Cgame Sound Slab ABI Split

## Scope

This round hardens the native `cgamex86.dll` sound import slab around the retail
Quake Live volume-aware sound slots. The key distinction is that retail exposes
direct native volume helpers in the `data_565958` host import table without
adding matching legacy `CG_*` syscall IDs for QVM or classic syscall traffic.

No C source behavior changed in this pass. The current source already preserves
the ABI split; this round turns that reconstruction into a dedicated regression
guardrail.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/cgame/cg_public.h`
- `src/code/cgame/cg_syscalls.c`
- `src/code/cgame/cg_local.h`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`

Observed facts:

- Retail table rows `data_5659EC..data_565A18` are a contiguous sound band:
  - `data_5659EC = sub_4AFE10`, fixed-volume `S_StartSound`.
  - `data_5659F0 = sub_4AFE20`, direct native `S_StartSoundVolume`.
  - `data_5659F4 = sub_4BEFB0`, fixed-volume `S_StartLocalSound`.
  - `data_5659F8 = sub_4AFE50`, direct native `S_StartLocalSoundVolume`.
  - `data_5659FC = j_sub_4DA490`, frame looping-sound clear.
  - `data_565A00 = j_sub_4DA3E0`, full sound-buffer clear.
  - `data_565A04 = sub_4AFE90`, `S_AddLoopingSound`.
  - `data_565A08 = sub_4AFEA0`, `S_UpdateEntityPosition`.
  - `data_565A0C = sub_4AFEB0`, `S_Respatialize`.
  - `data_565A10 = sub_4AFEC0`, `S_RegisterSound`.
  - `data_565A14 = sub_4AFED0`, `S_StartBackgroundTrack`.
  - `data_565A18 = 0x4B02F0`, stop-background-track slot.
- The recovered native import enum keeps those rows at slots `37..48`.
- `CG_MapNativeImport` maps only legacy syscall names. It maps fixed-volume
  sound calls and clear/loop/spatialization calls, but it intentionally has no
  mapping for `CG_QL_IMPORT_S_STARTSOUND_VOLUME` or
  `CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME`.
- Native cgame code calls `trap_QL_S_StartSoundVolume` and
  `trap_QL_S_StartLocalSoundVolume` through `CG_GetNativeImportFunction` at
  slots `38` and `40`.
- QVM compatibility in `cg_local.h` discards the volume scalar and falls back to
  `trap_S_StartSound` / `trap_S_StartLocalSound`, matching the fact that the
  legacy syscall enum has no volume-aware sound entries.
- Host-side native import providers in `cl_cgame.c` call
  `S_StartSoundVolume` and `S_StartLocalSoundVolume` directly, while
  `ql_cgame_imports.inc` keeps fixed-volume sound wrappers on the legacy
  `CG_Import_Syscall` path.

## Source Reconstruction

Implemented reconstruction artifacts:

- Added
  `test_native_cgame_sound_slab_keeps_volume_slots_direct_and_legacy_slots_fixed_volume`
  to `tests/test_botlib_cgame_native_import_slab_parity.py`.
- The test now binds:
  - the retail HLIL table row order for `data_5659EC..data_565A18`
  - the recovered `CG_QL_IMPORT_S_*` slot order `37..48`
  - the absence of legacy `CG_S_*_VOLUME` syscall IDs
  - the native `trap_QL_*Volume` direct import calls
  - the QVM fixed-volume fallback boundary
  - host-side direct volume providers in `cl_cgame.c`
  - legacy fixed-volume wrappers in `ql_cgame_imports.inc`

## Confidence

High confidence:

- Direct native volume slots `38` and `40` are pinned by table position, wrapper
  bodies, source enum slots, and host provider functions.
- The fixed-volume legacy syscall path remains separate from the native
  volume-aware path.
- The clear-looping-sounds split remains stable: native `killall == false`
  maps to the frame clear helper and `killall == true` maps to the full
  sound-buffer clear helper.

Medium confidence:

- The stop-background-track table row is still represented as raw `0x4B02F0`
  in the committed HLIL table, so its row identity is supported by adjacency,
  source wiring, and the already-promoted engine helper rather than by a named
  wrapper row at that table location.

## Validation

- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_sound_slab_keeps_volume_slots_direct_and_legacy_slots_fixed_volume -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - 6 passed.
- `python -m pytest tests\test_cgame_sound_wiring_parity.py tests\test_client_sound_voice_parity.py::test_volume_aware_sound_imports_route_to_engine_helpers tests\test_client_sound_playback_parity.py::test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring -q --tb=short`
  - 9 passed.

## Parity Estimate

- Focused native cgame sound slab ABI mapping: 90% -> 98%.
- Focused direct-volume versus legacy fixed-volume sound coverage: 76% -> 98%.
- Overall sound-system wiring reconstruction parity: 92.1% -> 92.2%.
