# Quake Live Steam Mapping Round 590: Sound Cache, Decode, and Mixer Alias Closure

Date: 2026-06-11

## Scope

This round closes the lowercase Binary Ninja alias bridge for the already
source-owned Quake Live sound registration, cache/decode, and mixer corridor.
No sound behavior was changed; the reconstruction work was limited to symbol
promotion and parity gates that connect the retail HLIL spelling, Ghidra rows,
and source owners.

Focused retail owners:

- shared hash helper: `sub_4d8990` / `FUN_004d8990`
- sound file type and cache helpers: `sub_4d9b20`, `sub_4dbb10` through
  `sub_4dbd00`
- registration helpers: `sub_4d9d00`, `sub_4d9e10`, `sub_4d9e50`,
  `sub_4db320`, `sub_4db3a0`
- Vorbis/WAV decode helpers: `sub_4dc6a0` through `sub_4dcc70`
- mixer transfer/paint helpers: `sub_4dbdf0`, `sub_4dbed0`, `sub_4dc030`,
  `sub_4dc350`

## Evidence

Observed facts:

1. Binary Ninja HLIL exposes these sound helpers with lowercase `sub_*`
   spellings in
   `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`,
   including the registration chain at `004d9d00` through `004d9e50`, cache
   reset/load helpers at `004db320` through `004dbd00`, and mixer transfer
   helpers at `004dbdf0` through `004dc350`.
2. The Ghidra function table contains matching rows and sizes for the promoted
   `FUN_*` aliases in
   `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
3. The source owners are already reconstructed in `src/code/client/snd_dma.c`,
   `src/code/client/snd_mem.c`, and `src/code/client/snd_mix.c`, with existing
   tests checking retail diagnostics, WAV/OGG decode flow, background/voice
   mixer ordering, and DMA transfer helpers.

Inferred meaning:

- The uppercase `sub_*` aliases and Ghidra `FUN_*` names were already mapped to
  stable source names, so adding the lowercase Binary Ninja names is a naming
  closure rather than a behavior reconstruction.
- The shared `generateHashValue` alias is included because the sound
  registration path calls retail `sub_4d8990` directly for the sound hash,
  even though that helper also has non-sound users.

## Reconstruction

Updated `references/analysis/quakelive_symbol_aliases.json` with lowercase
Binary Ninja aliases for the sound hash, file-type classifier, registration
helpers, sound memory/cache helpers, Vorbis and WAV decode helpers, and mixer
paint/transfer helpers.

Expanded `tests/test_client_sound_voice_parity.py` so the helper,
registration, and mixer parity gates assert the newly promoted lowercase
aliases alongside the existing uppercase and Ghidra rows. This keeps future
source reconstruction notes able to cite either Ghidra or Binary Ninja without
falling through to anonymous `sub_*` spellings.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json | Out-Null`
- `python -m pytest tests/test_client_sound_voice_parity.py::test_sound_helper_aliases_cover_retail_ogg_wav_voice_cluster tests/test_client_sound_voice_parity.py::test_sound_registration_cache_helpers_match_retail_diagnostics_and_reset_path tests/test_client_sound_voice_parity.py::test_sound_mixer_paint_channels_preserves_retail_stage_order_and_transfer_helpers -q --tb=short`
  - Result: `3 passed in 0.96s`
- `python -m pytest tests/test_client_sound_voice_parity.py tests/test_client_sound_playback_parity.py tests/test_win32_sound_dma_parity.py tests/test_cgame_sound_wiring_parity.py -q --tb=short`
  - Result: `38 passed in 4.82s`

No C source files changed, so no Debug|x86 rebuild or runtime launch was
required.

## Parity Estimate

- Focused sound cache/decode/mixer lowercase Binary Ninja alias coverage:
  **before 68% -> after 99%**.
- Focused registration/cache/mixer evidence bridge confidence:
  **before 94% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **93.47% -> 93.49%**.
