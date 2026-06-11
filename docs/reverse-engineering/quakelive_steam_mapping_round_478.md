# Quake Live Steam Mapping Round 478: Sound Name Hash Lookup Wiring

## Scope

This round tightens the sound registration lookup lane around
`S_FindName` and the retail shared filename hash helper. Round 314 correctly
renamed `sub_4D8990` as shared `generateHashValue`; this pass pins how the
sound system uses that helper with the `0x80` sound hash table and verifies the
source-local `S_HashSFXName` implementation remains semantically equivalent.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_314.md`

Observed facts:

- The alias map promotes `sub_4D8990` to `generateHashValue`, not to a
  sound-only helper name.
- `functions.csv` records `FUN_004d8990` at `0x004D8990`, size 75.
- Retail `generateHashValue` lowercases each filename byte, stops hashing at
  `.`, normalizes `\` to `/`, accumulates the character value with the
  `(index + 119)` weighting, and returns `hash & (size - 1)`.
- Retail `S_FindName` calls `sub_4D8990(arg1, 0x80)`, matching the source
  `LOOP_HASH == 128` sound hash table.
- Retail `S_FindName` then walks the selected bucket chain, allocates or reuses
  an `sfx_t`, and inserts new entries at the bucket head.

## Source Reconstruction

Implemented source-side changes:

- Added a shared-hash alias/size check for `sub_4D8990 -> generateHashValue` to
  `tests/test_client_sound_voice_parity.py`.
- Added HLIL assertions for the retail helper body and the sound caller's
  `0x80` table-size argument.
- Added source assertions for `S_HashSFXName`:
  - starts with zero hash and index,
  - lowercases each byte,
  - stops at `.` before the extension,
  - normalizes backslashes to forward slashes,
  - applies `(i + 119)` weighting,
  - masks with `LOOP_HASH - 1`.
- Added source assertions for `S_FindName` bucket walk and head insertion via
  `sfxHash[hash]`.

No C source edit was needed. The current source keeps the GPL-era local helper
boundary while matching the retail shared helper's sound-call semantics.

## Confidence

High confidence:

- `generateHashValue` ownership and function size.
- Sound caller table size `0x80`.
- Hash algorithm details: lowercase, extension stop, slash normalization,
  `(index + 119)` weighting, and final mask.
- Source `S_HashSFXName` equivalence for the sound hash table.

Medium confidence:

- Retail folds this algorithm into one shared helper used by renderer, shader,
  cvar, and sound callers. The source still has local helper boundaries; this
  round deliberately maps equivalence rather than forcing a cross-module helper
  refactor.

## Validation

- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
  - 10 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 42 passed.

No runtime launch was needed. This pass is deterministic mapping and parity-test
coverage from committed HLIL/Ghidra evidence.

## Parity Estimate

- Focused sound name-hash lookup mapping parity: 82% -> 96%.
- Focused sound registration hash regression coverage: 84% -> 96%.
- Overall client sound-system reconstruction parity: 91.5% -> 91.6%.
