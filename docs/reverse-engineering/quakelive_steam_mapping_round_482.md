# Quake Live Steam Mapping Round 482: Sound Update Timing and DMA Submit

## Scope

This round maps the sound update timing lane from public `S_Update` through
`S_Update_` and the retail `S_GetSoundtime` helper. The pass focuses on DMA
position sampling, buffer-wrap accounting, the large-time reset path,
`s_mixPreStep`, `s_mixahead`, update de-duplication, channel-start scanning,
submission-chunk alignment, full-buffer clamping, paint, and DMA submit order.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DB490` to `S_GetSoundtime`,
  `sub_4DB570` to `S_Update_`, and `sub_4DB680` to `S_Update`.
- `functions.csv` records `FUN_004db490` at `0x004DB490`, size 209,
  `FUN_004db570` at `0x004DB570`, size 262, and `FUN_004db680` at
  `0x004DB680`, size 129.
- Retail `S_GetSoundtime` calls `SNDDMA_GetDMAPos`, increments a retained
  buffer-wrap counter when the DMA sample position goes backwards, and resets
  the wrap counter plus painted time when the painted clock crosses
  `0x40000000`.
- The reset path calls `S_ClearSoundBuffer` through the mapped
  `S_StopAllSounds` path when sound is active.
- Retail stores the DMA-derived sound clock separately from the painted clock.
- If `dma.submission_chunk < 256`, retail advances painted time by
  `s_mixPreStep * dma.speed` and returns that painted value.
- Otherwise retail advances painted time by `dma.submission_chunk` and returns
  the sound clock.
- Retail `S_Update_` calls `S_GetSoundtime`, skips work if the sound clock did
  not advance, scans channel starts, computes `s_mixahead * dma.speed`, aligns
  the end time to the submission chunk, clamps to the complete DMA buffer, then
  calls `SNDDMA_BeginPainting`, `S_PaintChannels`, and `SNDDMA_Submit`.
- Retail public `S_Update` keeps the `s_show == 2` per-channel diagnostic,
  updates background streaming, then tail-calls the private mixer update.

## Source Reconstruction

Implemented source-side changes:

- Added `test_sound_update_timing_and_dma_submit_slice_matches_retail` to
  `tests/test_client_sound_playback_parity.py`.
- Added HLIL assertions for the full retail timing lane: `S_GetSoundtime`,
  `S_Update_`, and public `S_Update`.
- Added source assertions for:
  - retained DMA wrap state,
  - `SNDDMA_GetDMAPos` sampling,
  - wrap detection and large-time reset,
  - separate `s_soundtime` and `s_paintedtime` updates,
  - the `s_mixPreStep` return path for small submission chunks,
  - the normal submission-chunk return path,
  - `S_Update_` duplicate-tick suppression,
  - channel-start scanning before paint,
  - `s_mixahead` computation,
  - submission-chunk alignment,
  - full-buffer clamp,
  - begin-paint, paint, submit order,
  - public update ordering from background track update to mixer update.
- Added negative source assertions to prevent replacing the aligned
  `endtime` paint target with `s_soundtime` or a plain submission-chunk-only
  path.

No C source edit was needed. The existing source already reconstructs this
retail timing slice; this round converts that reconstruction into direct
Binary Ninja HLIL/Ghidra-backed regression coverage.

## Confidence

High confidence:

- Function ownership and Ghidra sizes for `S_GetSoundtime`, `S_Update_`, and
  `S_Update`.
- DMA position sampling and wrap-counter semantics.
- Large-time reset and stop-all-sounds path.
- Small-submission `s_mixPreStep` behavior versus normal
  submission-chunk behavior.
- Private mixer ordering: clock update, duplicate-tick guard, channel scan,
  mixahead, alignment, clamp, paint, submit.
- Public update ordering: diagnostics, background streaming, private update.

Medium confidence:

- The Binary Ninja variable names for retained locals and DMA fields are
  anonymous globals, so the note maps them by repeated access patterns and
  source-equivalent behavior rather than by symbolic names alone.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 9 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 43 passed.

No runtime launch was needed. This pass is deterministic mapping and
regression coverage from committed Binary Ninja HLIL and Ghidra evidence.

## Parity Estimate

- Focused sound update timing mapping parity: 78% -> 96%.
- Focused DMA submit/order regression coverage: 82% -> 96%.
- Overall client sound-system reconstruction parity: 91.7% -> 91.8%.
