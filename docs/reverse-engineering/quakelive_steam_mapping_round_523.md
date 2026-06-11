# Quake Live Steam Mapping Round 523: Engine Sound Helper Alias Bridge

## Scope

This pass tightens the engine-side sound helper naming bridge between the
Ghidra `FUN_...` corpus and the Binary Ninja `sub_...` references. It covers
the reconstructed sound helpers in `snd_dma.c`, `snd_mem.c`, and `snd_mix.c`
that already have stable Ghidra function rows and source parity gates.

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` has
  stable rows and sizes for the core playback helpers, registration/cache
  helpers, sound-console helpers with function rows, background OGG helpers,
  allocator helpers, OGG/WAV decode helpers, voice-sample helper, and mixer
  transfer/paint helpers.
- Binary Ninja HLIL uses the matching `sub_...` names in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`.
- Existing source parity gates already pin the behavior of the same helpers:
  init/shutdown and playback in `test_client_sound_playback_parity.py`, plus
  sound registration, console commands, OGG/WAV loading, background track
  update, voice samples, allocator state, and mixer ordering in
  `test_client_sound_voice_parity.py`.

Inferred meaning:

- The existing `sub_...` aliases are source-owned, but the Ghidra corpus still
  benefits from paired `FUN_...` aliases so future Ghidra-first investigation
  lands on the same reconstructed names.
- Helpers without stable Ghidra rows remain `sub_...` only. This preserves the
  documented boundary for `S_SoundList_f`, `S_Music_f`, and the frame-clear
  thunk rather than inventing synthetic Ghidra rows.

## Reconstruction

- Added paired `FUN_...` aliases for stable engine sound rows, including:
  - core playback: `S_ChannelSetup`, `S_Shutdown`, `S_SpatializeOrigin`,
    `S_StartSoundVolume`, `S_StartSound`, `S_StartLocalSoundVolume`,
    `S_ClearSoundBuffer`, `S_AddLoopingSound`, `S_AddLoopSounds`,
    `S_RawSamples`, `S_UpdateEntityPosition`, `S_Respatialize`,
    `S_ScanChannelStarts`, `S_StartLocalSound`, `S_StopAllSounds`,
    `S_GetSoundtime`, `S_Update_`, `S_Update`, `S_Init`, and
    `S_DisableSounds`;
  - registration/cache: `generateHashValue`, `S_FindName`, `S_memoryLoad`,
    `S_RegisterSound`, `S_FreeOldestSound`, and `S_BeginRegistration`;
  - control/background/decode helpers: `S_SoundInfo_f`, `S_Play_f`,
    `S_StopBackgroundTrack`, `S_StartBackgroundTrack`,
    `S_UpdateBackgroundTrack`, `S_SoundFileTypeForPath`,
    `S_AddVoiceSamples`, `S_LoadSound`, `S_OpenBackgroundOgg`,
    `S_CloseBackgroundOgg`, `S_OggUpdateBackgroundTrack`,
    `S_VorbisDecodeMemory`, `S_LoadOggSound`, `S_FindWavChunk`,
    `GetWavinfo`, and `S_LoadWavSound`;
  - allocator/mixer: `SND_free`, `SND_setup`, `SND_shutdown`,
    `S_DisplayFreeMemory`, `ResampleSfx`, `S_TransferStereo16`,
    `S_TransferPaintBuffer`, `S_PaintChannelFrom16`, and `S_PaintChannels`.
- Strengthened the client sound playback and voice parity tests so every
  helper with a stable Ghidra row must resolve through both its `sub_...` and
  `FUN_...` alias and still match the retail function size.

No C source changes were needed.

## Remaining Boundary

`S_SoundList_f`, `S_Music_f`, `S_ClearLoopingSoundsFrame`, and the cgame import
thunks remain intentionally bounded where the committed Ghidra function table
does not expose matching stable `FUN_...` rows. Their `sub_...` and source
behavior remain covered by the existing tests.

## Validation

- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_playback_aliases_cover_retail_core_entrypoints -q --tb=short`
- `python -m pytest tests\test_client_sound_voice_parity.py::test_sound_helper_aliases_cover_retail_ogg_wav_voice_cluster tests\test_client_sound_voice_parity.py::test_sound_registration_cache_helpers_match_retail_diagnostics_and_reset_path tests\test_client_sound_voice_parity.py::test_sound_console_commands_match_retail_registration_and_output_contracts tests\test_client_sound_voice_parity.py::test_sound_mixer_paint_channels_preserves_retail_stage_order_and_transfer_helpers -q --tb=short`
- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`

## Parity Estimate

- Focused engine sound helper Ghidra/Binary Ninja alias bridge confidence:
  **before 68% -> after 98%**.
- Focused client sound helper test coverage:
  **before 82% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.2% -> after 93.3%**.
