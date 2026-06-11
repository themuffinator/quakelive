# Quake Live Steam Mapping Round 592: Core Sound Playback and Import Wiring Alias Closure

Date: 2026-06-11

## Scope

This round closes the lowercase Binary Ninja alias bridge for the core client
sound playback/update corridor and its native cgame/UI sound import wiring.
No source behavior was changed; the work promotes stable retail names and pins
them with tests that cross-reference Binary Ninja HLIL, Ghidra function rows,
and the reconstructed source owners.

Focused retail owners:

- lifecycle/update helpers: `sub_4d9c50`, `sub_4d9ca0`, `sub_4db450`,
  `sub_4db490`, `sub_4db570`, `sub_4db680`, `sub_4db870`, `sub_4dbad0`
- playback/spatial/loop helpers: `sub_4d9ef0`, `sub_4da350`, `sub_4da3e0`,
  `sub_4da490`, `sub_4da4c0`, `sub_4da6f0`, `sub_4da840`, `sub_4dac80`,
  `sub_4dacd0`, `sub_4dae30`, `sub_4db3f0`
- native cgame sound thunks: `sub_4afe10`, `sub_4afe90`, `sub_4afea0`,
  `sub_4afeb0`, `sub_4afec0`, plus lowercase `j_sub_4da490` and
  `j_sub_4da3e0`
- UI/native local-sound thunk: `sub_4befb0` / `FUN_004befb0`

## Evidence

Observed facts:

1. Binary Ninja HLIL exposes the core playback lane with lowercase names from
   `004d9c50` through `004dbad0`, including the update tail
   `S_Update -> S_UpdateBackgroundTrack -> S_Update_`.
2. Ghidra `functions.csv` has matching `FUN_*` rows for the core playback
   helpers except the known `004da490` frame-clear helper, which the committed
   corpus does not expose as a stable function row.
3. HLIL shows native sound import thunks at `004afe10`, `004afe20`,
   `004afe50`, `004afe70`, `004afe80`, `004afe90`, `004afea0`, `004afeb0`,
   `004afec0`, and `004afed0`; the `004afe70` and `004afe80` labels are
   lowercase `j_sub_4da490` and `j_sub_4da3e0` tailcalls rather than ordinary
   `sub_4afe*` names.
4. HLIL and Ghidra both expose `004befb0` / `FUN_004befb0` for the UI/native
   local sound thunk that tailcalls `S_StartLocalSound`.

Inferred meaning:

- The source behavior was already reconstructed in `src/code/client/snd_dma.c`
  and the cgame/UI import bridge files; this pass closes naming and evidence
  drift between the retail decompiler spellings and the shared symbol corpus.
- `sub_4da490` is safe to promote as a Binary Ninja alias for
  `S_ClearLoopingSoundsFrame`, but the absence of `FUN_004da490` in Ghidra
  remains deliberate evidence, not a gap to paper over.

## Reconstruction

Updated `references/analysis/quakelive_symbol_aliases.json` with lowercase
Binary Ninja aliases for the core sound lifecycle, playback, spatialization,
looping, raw-sample, entity-position, respatialization, scan, stop, timing,
update, init, and disable helpers.

Promoted lowercase native cgame sound import aliases and lowercase `j_sub_*`
loop-clear thunk aliases, then promoted `FUN_004befb0` and lowercase
`sub_4befb0` for the UI/native local-sound thunk.

Strengthened the client playback, native cgame import slab, and UI sound import
parity tests so the new aliases remain tied to retail HLIL text, Ghidra rows
where they exist, and the documented no-row boundary for `S_ClearLoopingSoundsFrame`.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json | Out-Null`
- `python -m pytest tests/test_client_sound_playback_parity.py::test_sound_playback_aliases_cover_retail_core_entrypoints tests/test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_import_slab_aliases_and_rows_are_pinned tests/test_ui_menu_files.py::test_ui_native_import_table_matches_recovered_retail_slots tests/test_ui_menu_files.py::test_ui_sound_import_wiring_matches_retail_native_and_vm_paths -q --tb=short`
  - Result: `4 passed in 0.14s`
- `python -m pytest tests/test_client_sound_playback_parity.py tests/test_client_sound_voice_parity.py tests/test_cgame_sound_wiring_parity.py tests/test_win32_sound_dma_parity.py tests/test_botlib_cgame_native_import_slab_parity.py tests/test_ui_menu_files.py -q --tb=short`
  - Result: `128 passed, 1 skipped in 27.53s`

No C source files changed, so no Debug|x86 rebuild or runtime launch was
required.

## Parity Estimate

- Focused core sound playback/update lowercase Binary Ninja alias coverage:
  **before 58% -> after 99%**.
- Focused native cgame/UI sound import wiring evidence bridge confidence:
  **before 72% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **93.49% -> 93.52%**.
