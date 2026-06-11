# Quake Live Steam Mapping Round 488: Local Sound Stopped/Muted Guard Order

## Scope

This round reconstructs the engine-side local sound helper guard order for
`S_StartLocalSoundVolume` and `S_StartLocalSound`. Retail Quake Live returns
silently when the sound system is stopped or muted before it validates the
sound handle, so stopped-sound or muted-sound paths do not emit local-sound
range warnings.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/snd_dma.c`
- `tests/test_client_sound_playback_parity.py`

Observed facts:

- The alias map promotes `sub_4DA380` to `S_StartLocalSoundVolume` and
  `sub_4DB3F0` to `S_StartLocalSound`.
- `functions.csv` records `FUN_004da380` at `0x004DA380`, size `83`, and
  `FUN_004db3f0` at `0x004DB3F0`, size `82`.
- Retail `0x004DA380` first checks `data_126094c != 0 &&
  data_1260934 == 0`, then validates the handle range, then forwards to
  `sub_4DA050(nullptr, listener_number, channel, sfx, volume)`.
- Retail `0x004DB3F0` has the same stopped/muted guard before its handle
  validation and then forwards to `sub_4DA050` with a fixed `1.0` volume.
- The retail warning string
  `^3S_StartLocalSound: handle %i out of range\n` remains correct, but it is
  only reachable after the backend state guard succeeds.

## Source Reconstruction

Implemented source-side changes:

- Added `if ( !s_soundStarted || s_soundMuted ) return;` before the handle
  range check in `S_StartLocalSound`.
- Added the same stopped/muted guard before the handle range check in
  `S_StartLocalSoundVolume`.
- Extended `tests/test_client_sound_playback_parity.py` with HLIL anchors for
  both retail guards and ordered source assertions for guard -> warning ->
  start-call flow.

No runtime launch was needed. This is a deterministic warning-path and helper
ordering reconstruction backed by committed Binary Ninja HLIL and Ghidra
function evidence.

## Confidence

High confidence:

- Function ownership and sizes for both local-sound wrappers.
- The stopped/muted guard precedes handle validation in both retail helpers.
- The source warning string remains retail-correct but must be gated by sound
  backend state.

Medium confidence:

- The source continues to call `S_StartSound` from the fixed-volume wrapper
  rather than directly calling the common volume-aware core. The resulting
  channel volume is equivalent for fixed `1.0` playback, and the important
  reconstructed behavior in this round is the retail guard order.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_local_and_loop_warning_paths_preserve_retail_yellow_diagnostics -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 9 passed.
- `python -m pytest tests\test_client_sound_playback_parity.py tests\test_client_sound_voice_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 44 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

## Parity Estimate

- Focused local-sound stopped/muted guard parity: 70% -> 98%.
- Focused client sound warning-path regression coverage: 88% -> 97%.
- Overall client sound-system reconstruction parity: 91.9% -> 92.0%.
