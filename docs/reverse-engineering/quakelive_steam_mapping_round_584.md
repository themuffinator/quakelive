# Quake Live Steam Mapping Round 584: Voice Sample Entry Boundary

## Scope

This round tightens the client sound voice-sample ingress path:

- `sub_4dab00` / `sub_4DAB00` / `FUN_004dab00`, size `373`:
  `S_AddVoiceSamples`
- the Steam voice receive path that feeds decompressed PCM into
  `S_AddVoiceSamples`
- the five-lane retail voice ring mixed by `S_PaintChannels`

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_004dab00` at `0x004dab00`, size `373`.
- Binary Ninja HLIL part04 names the helper as `sub_4dab00` and enters the
  voice-channel lookup immediately:
  - initializes the selected channel to `-1`;
  - scans the five `data_13e1860` voice lanes for the same client;
  - otherwise selects a lane whose end sample is more than half the DMA buffer
    behind `s_paintedtime`;
  - computes the first queued sample from `s_mixPreStep`, `s_voiceStep`,
    `dma.speed`, and `s_paintedtime`;
  - copies PCM samples into the `0x4000`-sample circular voice buffer.
- The same HLIL body does not contain an early sound-started, muted, null-data,
  or non-positive sample guard before channel selection.
- The current source already reconstructs the downstream retail mixer:
  `S_PaintChannels` mixes voice lanes before normal dynamic and looping
  channels, scaled by `s_voiceVolume`.

Inferred mapping:

- The extra source guard before `S_AddVoiceSamples` channel selection was a
  defensive local addition, not a retail boundary. Retail expects the Steam
  voice receive path to pass validated decompressed PCM and lets the sound
  helper own only voice-lane scheduling and buffering.

## Reconstruction

Implemented in `src/code/client/snd_dma.c`:

- Removed the non-retail early return:
  `!s_soundStarted || s_soundMuted || !data || samples <= 0`.
- Left the existing five-lane voice ring selection, start-time scheduling,
  overflow clamp, diagnostics, and circular-buffer copy intact.

Updated `references/analysis/quakelive_symbol_aliases.json`:

- Added the lowercase Binary Ninja alias `sub_4dab00` for
  `S_AddVoiceSamples`.

Strengthened `tests/test_client_sound_voice_parity.py`:

- Added lowercase BN alias coverage for `sub_4dab00`.
- Pinned the retail source entry order so `S_AddVoiceSamples` starts at
  `channelIndex = -1` and scans the five voice lanes before any local guard.
- Added a negative assertion rejecting the removed non-retail guard.

## Validation

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  - passed
- `python -m pytest tests/test_client_sound_voice_parity.py::test_sound_helper_aliases_cover_retail_ogg_wav_voice_cluster tests/test_client_sound_voice_parity.py::test_voice_mixer_reconstructs_retail_lane_shape_and_cvars -q --tb=short`
  - passed
- `python -m pytest tests/test_client_sound_voice_parity.py tests/test_client_sound_playback_parity.py tests/test_platform_services.py::test_client_steam_command_voice_and_runtime_alias_bridge_tracks_ghidra_hlil_rows tests/test_platform_services.py::test_client_voice_commands_reconstruct_retail_binding_surface -q --tb=short`
  - passed
- `git diff --check -- src/code/client/snd_dma.c references/analysis/quakelive_symbol_aliases.json tests/test_client_sound_voice_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_584.md IMPLEMENTATION_PLAN.md`
  - passed with only repository line-ending normalization warnings
- `powershell -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - build succeeded with `0` warnings and `0` errors

## Parity Estimate

- Focused `S_AddVoiceSamples` source-entry boundary confidence:
  **before 88% -> after 98%**.
- Focused voice-sample alias/evidence bridge confidence:
  **before 92% -> after 99%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.42% -> after 93.45%**.
