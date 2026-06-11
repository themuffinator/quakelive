# Quake Live Steam Mapping Round 480: Sound PVS Spatial Culling

## Scope

This round maps the Quake Live sound spatial-culling gate inside
`S_Respatialize` and ties the source `S_OriginInPVS` helper to the retail
`s_pvs` wiring. The pass covers listener/head storage, channel-origin choice,
the optional PVS visibility test, zero-volume behavior for inaudible channels,
and the follow-on loop-sound accumulation call.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DACD0` to `S_Respatialize`.
- `functions.csv` records `FUN_004dacd0` at `0x004DACD0`, size 351.
- Retail `S_Init` registers `s_pvs` with bounded defaults `"0"`, `"0"`, and
  `"1"` plus flags `0x81801`.
- Retail `S_Respatialize` checks the integer value at `data_13e1858 + 0x30`
  before applying the PVS gate.
- When `s_pvs` is enabled, retail calls the visibility function pointer stored
  at `data_146ccd4` with the listener origin and candidate sound origin.
- If the visibility callback reports false, retail writes zero into both
  channel volume slots and skips the spatialize call for that channel.
- If the PVS gate is disabled or visibility succeeds, retail calls
  `sub_4d9ef0`, already mapped to `S_SpatializeOrigin`, with master volume
  `0x7f`.
- The retail function then calls `sub_4da6f0`, already mapped to
  `S_AddLoopSounds`.

## Source Reconstruction

Implemented source-side changes:

- Added HLIL assertions for the retail `s_pvs` registration, the
  `S_Respatialize` PVS branch, the zero-volume branch, and the loop-sound tail
  call to `tests/test_client_sound_playback_parity.py`.
- Added source assertions for `S_OriginInPVS`:
  - listener and origin leaf lookup through `CM_PointLeafnum`,
  - cluster lookup through `CM_LeafCluster`,
  - negative-cluster rejection,
  - PVS mask lookup through `CM_ClusterPVS`,
  - null-mask rejection,
  - bit test against `originCluster`.
- Extended `S_Respatialize` source assertions to require the `s_pvs` gate,
  zeroing of `leftvol` and `rightvol`, `continue`, `S_SpatializeOrigin`, and
  `S_AddLoopSounds`.
- Added a guard against accidentally reversing the listener/origin argument
  order in the source PVS call.

No C source edit was needed. The current source already reconstructs the retail
behavior with a named `S_OriginInPVS` helper instead of exposing the raw engine
visibility callback slot from the binary.

## Confidence

High confidence:

- `S_Respatialize` ownership and function size.
- Retail `s_pvs` cvar registration and bounded default.
- Conditional PVS branch location inside dynamic channel spatialization.
- Zeroing both channel volume outputs when PVS visibility fails.
- Source listener/origin argument order for `S_OriginInPVS`.
- Loop-sound accumulation remains the tail behavior after channel
  respatialization.

Medium confidence:

- The retail `data_146ccd4` slot is interpreted as the engine visibility/PVS
  callback based on call shape, arguments, and source equivalence. The source
  decomposes that callback through `CM_PointLeafnum`, `CM_LeafCluster`, and
  `CM_ClusterPVS`, which is behaviorally equivalent for this gate.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
  - 8 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 42 passed.

No runtime launch was needed. This pass is deterministic mapping and
regression coverage from committed Binary Ninja HLIL and Ghidra evidence.

## Parity Estimate

- Focused `S_Respatialize` PVS culling mapping parity: 80% -> 95%.
- Focused spatial sound culling regression coverage: 84% -> 96%.
- Overall client sound-system reconstruction parity: 91.6% -> 91.7%.
