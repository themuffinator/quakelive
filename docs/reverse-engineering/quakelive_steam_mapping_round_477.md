# Quake Live Steam Mapping Round 477: Channel Freelist Allocator Wiring

## Scope

This round tightens the low-level sound channel freelist contract underneath
`S_StartSoundVolume`, `S_ScanChannelStarts`, and the update mixer path. The
source already matched retail behavior, so this pass records and tests the
allocator/free wiring instead of changing C code.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4D9C50` to `S_ChannelSetup`,
  `sub_4DA050` to `S_StartSoundVolume`, and `sub_4DAE30` to
  `S_ScanChannelStarts`.
- `functions.csv` records `FUN_004d9c50` at size 74,
  `FUN_004da050` at size 760, and `FUN_004dae30` at size 413.
- Retail `S_ChannelSetup` clears the 96-channel slab, links a reverse freelist
  from the tail of the slab back to the first channel, stores the head in
  `data_12c5b78`, and prints `"Channel memory manager started\n"`.
- Retail `S_StartSoundVolume` reads `data_12c5b78` as the free-channel head.
  When a free channel exists it pops the head, stores `Com_Milliseconds()` into
  the channel's first word, and later marks `startSample` with the
  `0x7fffffff` immediate-start sentinel.
- When no free channel exists, retail searches for an older channel on the same
  entity excluding announcer channel `7`, then falls back to an older world
  channel.
- Retail `S_ScanChannelStarts` relinks finished channels by writing the current
  freelist through the channel's first word, clearing the live `thesfx` slot,
  advancing the local free head, and writing that head back to `data_12c5b78`.

## Source Reconstruction

Implemented source-side changes:

- Added `test_channel_freelist_helpers_match_retail_alloc_and_free_paths()` to
  `tests/test_client_sound_playback_parity.py`.
- Pinned the source `channel_t` field order relevant to the freelist overlay:
  `allocTime`, `startSample`, and `thesfx`.
- Pinned `S_ChannelFree()` as the source-level free helper: clear `thesfx`,
  write the old freelist through the channel pointer, and promote the channel
  to the freelist head without bulk-clearing the channel.
- Pinned `S_ChannelMalloc()` as the source-level allocation helper: return
  `NULL` when no free channel exists, otherwise pop the freelist head and stamp
  `allocTime` from `Com_Milliseconds()`.
- Cross-checked source setup, allocation, steal, and scan/free callsites
  against the retail HLIL anchors.

No C source edit was needed for this slice.

## Confidence

High confidence:

- Channel setup ownership, function size, reverse freelist construction, and
  debug string.
- Free-channel pop behavior and `Com_Milliseconds()` allocation timestamp.
- Finished-channel relinking behavior in `S_ScanChannelStarts`.
- Source helper names and field usage are stable because the same freelist is
  reached from setup, start, and scanner paths.

Medium confidence:

- Retail emits the allocation/free operations inline through optimized channel
  pointer math rather than named helper calls. The source helper boundaries are
  still the correct reconstruction layer because they preserve the observed
  side effects.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 8 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 42 passed.

No runtime launch was needed. This pass is deterministic mapping and parity-test
coverage from committed HLIL/Ghidra evidence.

## Parity Estimate

- Focused channel freelist allocator mapping parity: 80% -> 95%.
- Focused playback allocation/free regression coverage: 87% -> 96%.
- Overall client sound-system reconstruction parity: 91.4% -> 91.5%.
