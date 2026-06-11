# Quake Live Steam Mapping Round 580: ResampleSfx Argument Shape

## Scope

This round tightens the client sound cache reconstruction around the retail
PCM resample helper:

- `sub_4DBC00` / `FUN_004dbc00`, size `245`: `ResampleSfx`
- WAV and OGG decoded PCM callers from `S_LoadWavSound` and `S_LoadOggSound`
- source wiring in `src/code/client/snd_mem.c`

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_004dbc00` at `0x004dbc00`, size `245`.
- `references/analysis/quakelive_symbol_aliases.json` maps both
  `sub_4DBC00` and `FUN_004dbc00` to `ResampleSfx`.
- Binary Ninja HLIL shows `sub_4dbc00` as a four-argument helper:
  `(sfx, inrate, inwidth, data)`.
- The helper computes the rate scale from `inrate / dma.speed`, rewrites the
  sound length to the output count, advances a fixed-point `samplefrac`, reads
  16-bit samples directly when `inwidth == 2`, expands unsigned 8-bit samples
  through the `-128 << 8` path otherwise, and writes into `SND_CHUNK_SIZE`
  cache chunks.
- The same HLIL body allocates a new `sndBuffer` at the `0x400` sample
  boundary and updates the retail allocator counters by `0x808`, matching the
  existing `SND_malloc` / `sndBuffer` reconstruction.
- Retail callsites pass four arguments from the decoded sound path:
  `sub_4dc8ad` for decoded OGG PCM and `sub_4dcd07` for WAV PCM.

Inferred mapping:

- The source helper should not carry the old unused GPL-era `compressed`
  parameter. Compression policy belongs to the caller-side `S_LoadPCMSound`
  branch, while `ResampleSfx` is the plain PCM-to-cache chunk writer.

## Reconstruction

Implemented in `src/code/client/snd_mem.c`:

- Changed `ResampleSfx` from five arguments to the retail four-argument shape:
  `sfx`, `inrate`, `inwidth`, and decoded PCM `data`.
- Updated the uncompressed `S_LoadPCMSound` callsite to pass only those four
  arguments.
- Corrected the nearby private helper comment header from `ResampleSfx` to
  `ResampleSfxRaw` so the local source boundary is no longer ambiguous.

Strengthened `tests/test_client_sound_voice_parity.py`:

- Added `sub_4DBC00` / `FUN_004dbc00` alias and Ghidra size coverage.
- Pinned the retail four-argument HLIL signature, fixed-point resampling path,
  8-bit and 16-bit sample conversions, chunk-boundary allocation, and WAV/OGG
  callsites.
- Added source assertions that reject the stale `qboolean compressed`
  parameter and the old five-argument callsite.

## Validation

- `python -m pytest tests/test_client_sound_voice_parity.py::test_sound_cache_and_shutdown_match_retail_allocator_contracts -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_client_sound_voice_parity.py tests/test_client_sound_playback_parity.py tests/test_win32_sound_dma_parity.py tests/test_cgame_sound_wiring_parity.py tests/test_cgame_sound_registration_parity.py -q --tb=short`
  - `41 passed`
- `git diff --check -- src/code/client/snd_mem.c tests/test_client_sound_voice_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_580.md IMPLEMENTATION_PLAN.md`
  - passed with only repository line-ending normalization warnings
- `powershell -NoProfile -ExecutionPolicy Bypass -File .vscode\build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - build succeeded with `0` warnings and `0` errors

## Parity Estimate

- Focused `ResampleSfx` argument-shape/source-boundary confidence:
  **before 86% -> after 99%**.
- Focused sound cache load/resample wiring confidence:
  **before 93% -> after 95%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.35% -> after 93.4%**.
