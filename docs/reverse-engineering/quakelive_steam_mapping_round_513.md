# Quake Live Steam Mapping Round 513: Background Raw-Tail Stop Ownership

## Scope

This round tightens the client sound background-track reconstruction around
retail `S_StopBackgroundTrack` (`sub_4DB030`), `S_StartBackgroundTrack`
(`sub_4DB060`), and `S_UpdateBackgroundTrack` (`sub_4DB1C0`).

The source change is intentionally small: preserve raw-stream continuity unless
the background track stop path actually closed an active background stream.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part12.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The promoted alias map identifies `sub_4DB030` as `S_StopBackgroundTrack`,
  `sub_4DB060` as `S_StartBackgroundTrack`, `sub_4DB1C0` as
  `S_UpdateBackgroundTrack`, `sub_4DCA40` as `S_CloseBackgroundOgg`, and
  `sub_4DCA50` as `S_OggUpdateBackgroundTrack`.
- Ghidra `functions.csv` sizes match the active retail cluster:
  `FUN_004db030` size `35`, `FUN_004db060` size `351`, `FUN_004db1c0` size
  `347`, `FUN_004dca40` size `12`, and `FUN_004dca50` size `114`.
- Binary Ninja HLIL for `sub_4DB030` shows the stop path first checking
  `data_12c5b74 != 0`, then calling `sub_4dca40()`, clearing
  `data_12c5b74`, and clearing `data_13e1850`.
- The same HLIL block has no unconditional raw-tail clear outside the
  active-background branch.
- Binary Ninja HLIL for `sub_4DB060` closes existing background OGG state
  before opening the new track, but does not clear `data_13e1850` as part of
  start/restart setup.
- Binary Ninja HLIL for `sub_4DB1C0` routes exhausted OGG streams through the
  update helper, closes the OGG stream, and restarts through
  `sub_4DB060` when a loop path is available.

Inferred mapping:

- Retail stores background ownership in a single active OGG handle flag,
  while the reconstructed source supports both the retained legacy
  `s_backgroundFile` path and the Quake Live OGG stream path. A local source
  sentinel is therefore the closest faithful reconstruction of retail's
  "only clear raw tail after an active background close" behavior.

## Reconstruction

Implemented changes:

- Updated `S_StopBackgroundTrack()` in `src/code/client/snd_dma.c` to track
  whether a legacy background file or OGG stream was actually closed.
- Kept `s_backgroundIsOgg` reset on stop entry, but gated `s_rawend = 0` behind
  the new `stopped` sentinel.
- Strengthened `tests/test_client_sound_voice_parity.py` so the background
  track parity gate now pins:
  - retail stop HLIL anchors for the conditional close and raw-tail reset;
  - source ordering of both legacy-file and OGG close paths into the sentinel;
  - absence of `s_rawend = 0` from the start/restart block.

## Remaining Gaps

- The legacy `s_backgroundFile` path is retained from the GPL source and does
  not appear as the primary retail Quake Live OGG ownership shape. Its reset
  behavior is mapped by source compatibility inference rather than a separate
  retail legacy-file branch.
- This pass does not rename the retail globals behind `data_12c5b74` or
  `data_13e1850` beyond their already promoted source aliases.
- Runtime playback was not launched; static HLIL/Ghidra evidence and focused
  parity/build validation were sufficient for this wiring correction.

## Validation

Validation passed:

- `python -m pytest tests\test_client_sound_voice_parity.py::test_background_track_ogg_update_matches_retail_restart_path -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 10 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
  - 11 passed.
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
  - 7 passed.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .vscode\build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

## Parity Estimate

- Focused `S_StopBackgroundTrack` raw-tail reset ownership confidence:
  **70% -> 96%**.
- Focused background/raw-stream continuity wiring confidence: **88% -> 95%**.
- Overall sound-system wiring reconstruction parity: **92.5% -> 92.6%**.
