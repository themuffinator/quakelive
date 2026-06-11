# Quake Live Steam Mapping Round 476: Channel Start Scanner Wiring

## Scope

This round tightens the `S_ScanChannelStarts` slice feeding the retail
`S_Update_` mixer path. Earlier rounds mapped `S_Update`, `S_Update_`, and the
DirectSound timing edge; this pass pins the channel scanner that converts newly
allocated sound channels into paint-time starts and frees completed channels.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DAE30` to `S_ScanChannelStarts`.
- `functions.csv` records `FUN_004dae30` at `0x004DAE30`, size 413.
- Retail HLIL snapshots the current `s_paintedtime` value, initializes the
  scanner result to zero, walks the 96 sound channels as sixteen unrolled
  six-channel groups, and writes the updated channel freelist back before
  returning.
- For channels with a live `sfx`, retail tests `startSample` against
  `0x7fffffff`, the `START_SAMPLE_IMMEDIATE` sentinel. Those channels receive
  the current painted time and cause the helper to return a true result.
- For already-started channels, retail compares `sfx->soundLength + startSample`
  against the current painted time. Finished channels are unlinked from active
  playback and relinked through the channel freelist.
- Retail `S_Update_` calls this scanner after `S_GetSoundtime` and before the
  mix-ahead, begin-paint, `S_PaintChannels`, and submit sequence.

## Source Reconstruction

Implemented source-side changes:

- Expanded `tests/test_client_sound_playback_parity.py` to extract
  `S_ScanChannelStarts` directly from `snd_dma.c`.
- Added HLIL anchors for the retail scanner owner, `s_paintedtime` snapshot,
  `START_SAMPLE_IMMEDIATE` comparison, finished-channel free path, unrolled
  channel-walk stride, freelist writeback, and return value.
- Added source assertions for the reconstructed behavior:
  - skip empty channels,
  - convert `START_SAMPLE_IMMEDIATE` to `s_paintedtime`,
  - report `newSamples = qtrue` for immediate-start channels,
  - free channels whose `startSample + soundLength` is at or before
    `s_paintedtime`,
  - preserve the pointer-based `S_ChannelFree(ch)` source shape.

No C source edit was needed. The current source already matches the retail
scanner semantics at the source level.

## Confidence

High confidence:

- `S_ScanChannelStarts` ownership and function size.
- Immediate-start sentinel value and source mapping to
  `START_SAMPLE_IMMEDIATE`.
- Finished-channel cleanup predicate and freelist ownership.
- `S_Update_` call placement relative to soundtime update and painting.

Medium confidence:

- Retail's unrolled six-channel group shape is compiler output rather than a
  source-level requirement. The source loop over `MAX_CHANNELS` is the correct
  reconstruction target.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 7 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 41 passed.

No runtime launch was needed. This pass is deterministic mapping and parity-test
coverage from committed HLIL/Ghidra evidence.

## Parity Estimate

- Focused `S_ScanChannelStarts` mapping parity: 78% -> 94%.
- Focused channel-start/update wiring regression coverage: 86% -> 96%.
- Overall client sound-system reconstruction parity: 91.2% -> 91.4%.
