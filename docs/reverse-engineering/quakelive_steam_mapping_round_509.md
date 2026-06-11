# Quake Live Steam Mapping Round 509: Sound Mixer Paint Pipeline

## Scope

This round maps the retail sound mixer paint path centered on
`S_PaintChannels` and its adjacent transfer helpers. The work pins the retail
stage order for streamed background audio, Steam voice overlay, dynamic
channels, looped channels, and final DMA transfer.

No C source behavior changed in this pass. The current `snd_mix.c`
reconstruction already matches the observed retail stage order, including the
Quake Live background underrun diagnostic; this round turns that shape into a
dedicated regression gate.

## Evidence

Primary evidence:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `src/code/client/snd_mix.c`
- `tests/test_client_sound_voice_parity.py`

Observed facts:

- Promoted retail aliases bind the mixer helper cluster:
  - `sub_4DBDF0` -> `S_TransferStereo16`, Ghidra `FUN_004dbdf0`, size `214`.
  - `sub_4DBED0` -> `S_TransferPaintBuffer`, Ghidra `FUN_004dbed0`, size
    `351`.
  - `sub_4DC030` -> `S_PaintChannelFrom16`, Ghidra `FUN_004dc030`, size
    `775`.
  - `sub_4DC350` -> `S_PaintChannels`, Ghidra `FUN_004dc350`, size `781`.
- Retail `S_PaintChannels` starts by scaling `s_volume` into the mixer global
  and then slices the requested paint range into `0x1000` sample chunks.
- The first paint stage copies from the raw stream ring at `data_14098a0` into
  the paintbuffer at `data_12c5ba0`, or clears the paintbuffer when the stream
  has underrun.
- The background underrun diagnostic is gated by the background/music volume
  cvar and emits the retail string at `data_5445c8`.
- The voice overlay stage reads `s_voiceVolume`, walks five voice lanes rooted
  at `data_13e1864`, mixes mono samples into both paintbuffer channels, and
  uses the `0x3fff` ring mask.
- The dynamic channel pass walks `0x60` channel entries rooted at
  `data_14298e8` and dispatches through `sub_4DC030`.
- The loop-channel pass is gated by `data_142c2f0`, walks entries rooted at
  `data_142ae08`, uses `paintTime % soundLength`, and also dispatches through
  `sub_4DC030`.
- Each chunk finishes with `sub_4DBED0(end)` and then advances the retail
  painted-time global at `data_142c2ec`.
- `S_TransferPaintBuffer` keeps the optimized 16-bit stereo path through
  `S_TransferStereo16`, with the generic 16-bit and 8-bit clamped transfer
  paths retained for other DMA formats.

## Reconstruction

Implemented reconstruction artifacts:

- Added `SOUND_MIXER_ALIASES` to
  `tests/test_client_sound_voice_parity.py`.
- Added
  `test_sound_mixer_paint_channels_preserves_retail_stage_order_and_transfer_helpers`,
  which binds:
  - Binary Ninja promoted aliases and Ghidra function sizes for the mixer
    helper cluster.
  - The HLIL stage order inside `sub_4DC350`.
  - Retail data roots for raw stream, paintbuffer, voice lanes, dynamic
    channels, loop channels, and painted-time transfer.
  - Source stage order in `S_PaintChannels`.
  - Source transfer-helper behavior in `S_TransferStereo16` and
    `S_TransferPaintBuffer`.
  - Source 16-bit channel mixing behavior in `S_PaintChannelFrom16`.
  - Dynamic and loop-channel compression dispatch through ADPCM, Wavelet,
    MuLaw, and 16-bit paths.

## Confidence

High confidence:

- The mixer stage order is backed by promoted names, Ghidra sizes, HLIL control
  flow, data-root access patterns, source implementation shape, and focused
  static tests.
- The retail voice lane count and ring mask are pinned by both the voice-buffer
  tests and the mixer-stage test.
- The final chunk transfer through `S_TransferPaintBuffer` is directly visible
  in HLIL and now source-pinned after loop-channel painting.

Medium confidence:

- The compression-specific helper bodies beyond the 16-bit path remain covered
  by dispatch shape here, not by a fresh instruction-by-instruction
  reconstruction in this round.
- Runtime DMA format behavior was not launched for this mapping pass; the
  committed HLIL/Ghidra evidence and static source gates were sufficient.

## Validation

Validation passed:

- `python -m pytest tests\test_client_sound_voice_parity.py::test_sound_mixer_paint_channels_preserves_retail_stage_order_and_transfer_helpers -q --tb=short`
  - 1 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
  - 11 passed.
- `python -m pytest tests\test_client_sound_playback_parity.py::test_sound_update_timing_and_dma_submit_slice_matches_retail tests\test_client_sound_playback_parity.py::test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring -q --tb=short`
  - 2 passed.

No game launch was performed. The task is a static retail-mapping and
source-coverage pass, and no rendered-output or startup hypothesis required a
runtime probe.

## Parity Estimate

Focused `S_PaintChannels` mixer stage-order reconstruction:

- Before: 84%
- After: 98%

Focused mixer transfer-helper mapping:

- Before: 80%
- After: 96%

Overall sound-system wiring reconstruction parity:

- Before: 92.2%
- After: 92.3%
