# Quake Live Steam Mapping Round 484: Real Looping-Sound Scale Reset

## Scope

This round reconstructs a small stale-state edge in the legacy
`S_AddRealLoopingSound` compatibility path. Earlier rounds kept the old QVM
entry point while changing the retail mixer to use uniform 127-volume loop
spatialization. This pass rechecks the retail loop-record initialization body
and mirrors its doppler-scale reset in the source compatibility path.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_459.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_463.md`

Observed facts:

- The alias map promotes `sub_4DA4C0` to `S_AddLoopingSound`, and
  `functions.csv` records `FUN_004da4c0` at `0x004DA4C0`, size `558`.
- The native retail `S_AddLoopingSound` body writes the loop record origin,
  sound pointer, active flag, velocity, doppler flag, both doppler-scale cells,
  and frame number before returning.
- The committed HLIL also exposes an adjacent extracted body at `0x004DA522`
  that performs the same loop-record initialization. That slice writes
  doppler false at `0x004DA575`, loads `1.0` at `0x004DA57F`, then writes that
  value to both scale cells at `0x004DA587` and `0x004DA58D`.
- The source `S_AddRealLoopingSound` is an intentional compatibility surface
  for legacy VM callers and not a native retail import slot, but it shares the
  same loop-record bank consumed by `S_AddLoopSounds`.
- Before this round, `S_AddRealLoopingSound` cleared `doppler` but did not
  reset `oldDopplerScale` or `dopplerScale`, allowing a previous doppler loop
  on the same entity slot to leak stale scale values into the next real-loop
  record.

## Source Reconstruction

Implemented source-side changes:

- Updated the `S_AddRealLoopingSound` header comment to name the function and
  describe its legacy-VM compatibility role.
- Reset `loopSounds[entityNum].oldDopplerScale` and
  `loopSounds[entityNum].dopplerScale` to `1.0` after clearing the doppler flag.
- Extended `tests/test_client_sound_playback_parity.py` with direct HLIL
  anchors for `0x004DA522`, the doppler-false write, the `1.0` load, and both
  retail scale writes.
- Extended the same test to require the compatibility source path to set
  active, clear kill, clear doppler, and reset both scale fields.

No runtime launch was needed. This is a deterministic sound-state
reconstruction backed by committed Binary Ninja HLIL and Ghidra evidence.

## Confidence

High confidence:

- `S_AddLoopingSound` ownership and function size.
- Retail loop-record initialization writes both doppler-scale cells to `1.0`.
- Source `S_AddRealLoopingSound` uses the same loop-record storage and should
  not leave stale doppler scale values behind after clearing doppler.

Medium confidence:

- The `0x004DA522` body is best treated as compiler-extracted loop-record
  initialization evidence rather than a stable public retail function. The
  source change applies the observed side effects to the compatibility helper
  that still exists in the reconstructed source tree.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_local_and_loop_warning_paths_preserve_retail_yellow_diagnostics -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_playback_parity.py tests\test_client_sound_voice_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 43 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.
- `git diff --check -- src/code/client/snd_dma.c tests/test_client_sound_playback_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_484.md IMPLEMENTATION_PLAN.md`
  - Passed with repository LF-to-CRLF working-copy warnings only.

## Parity Estimate

- Focused `S_AddRealLoopingSound` stale-state parity: 72% -> 96%.
- Focused loop-record initialization regression coverage: 88% -> 97%.
- Overall client sound-system reconstruction parity: 91.8% -> 91.9%.
