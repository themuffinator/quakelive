# Quake Live Steam Mapping Round 577: Background OGG Close Owner

## Scope

This round tightens the client sound background-music wiring around the retail
`S_CloseBackgroundOgg` helper:

- `sub_4DCA40` / `FUN_004dca40`, size `12`: `S_CloseBackgroundOgg`
- callers from `S_StopBackgroundTrack`, `S_StartBackgroundTrack`,
  `S_OpenBackgroundOgg`, and `S_OggUpdateBackgroundTrack`

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  keeps `FUN_004dca40` as a stable `12` byte function row.
- `references/analysis/quakelive_symbol_aliases.json` maps both
  `sub_4DCA40` and `FUN_004dca40` to `S_CloseBackgroundOgg`.
- Binary Ninja HLIL shows `S_StopBackgroundTrack` calling `sub_4dca40()`
  before clearing the active background state and raw-stream tail.
- The same background update HLIL routes an exhausted or failed OGG stream
  through `sub_4dca40()` before either restarting the loop track through
  `S_StartBackgroundTrack` or falling back to the normal stop path.
- The tiny `sub_4dca40` body calls the Vorbis clear helper on the retained
  background decoder object, matching a standalone close owner rather than a
  large policy-bearing function.

Inferred mapping:

- The reconstructed source keeps generic stream lifetime mechanics in
  `snd_ogg_stream.c`, but `snd_dma.c` should still expose the retail local
  close boundary. That keeps the retail call graph visible while preserving
  the source split used for the reusable OGG stream abstraction.

## Reconstruction

Implemented in `src/code/client/snd_dma.c`:

- Added `static void S_CloseBackgroundOgg( void )` as the local background
  decoder close owner.
- Routed invalid background OGG metadata, update/decode errors, explicit stop,
  and restart replacement through `S_CloseBackgroundOgg()`.
- Left `s_backgroundIsOgg` and `s_rawend` ownership in the surrounding
  high-level functions, matching the retail split where the close helper clears
  decoder state while the caller clears track/raw-stream policy state.

Strengthened `tests/test_client_sound_voice_parity.py`:

- The background-track gate now checks the `sub_4DCA40` body anchor, the source
  wrapper body, and the callsites in open, stop, start/restart, and update
  error paths.
- The test continues to guard against reintroducing legacy WAV background
  music helpers or generic source-only close ownership in this path.

## Validation

- `python -m pytest tests/test_client_sound_voice_parity.py::test_background_track_ogg_update_matches_retail_restart_path -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_client_sound_voice_parity.py tests/test_client_sound_playback_parity.py tests/test_win32_sound_dma_parity.py tests/test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
  - `30 passed`
- `python -m pytest tests/test_cgame_sound_wiring_parity.py tests/test_ui_menu_files.py::test_ui_native_import_table_matches_recovered_retail_slots tests/test_ui_menu_files.py::test_ui_sound_import_wiring_matches_retail_native_and_vm_paths -q --tb=short`
  - `17 passed`
- `git diff --check -- src/code/client/snd_dma.c tests/test_client_sound_voice_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_577.md IMPLEMENTATION_PLAN.md`
  - passed with only repository line-ending normalization warnings
- `powershell -NoProfile -ExecutionPolicy Bypass -File .vscode\build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - build succeeded with `0` warnings and `0` errors

## Parity Estimate

- Focused `S_CloseBackgroundOgg` source-boundary confidence:
  **before 78% -> after 98%**.
- Focused background OGG close/restart wiring confidence:
  **before 95% -> after 97%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.3% -> after 93.35%**.
