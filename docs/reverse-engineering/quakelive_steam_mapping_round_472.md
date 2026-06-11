# Quake Live Steam Mapping Round 472: Paint Mixer Background Underrun Wiring

## Scope

This round maps and reconstructs the raw/background-stream underrun branch in
`sub_4DC350 -> S_PaintChannels`. The source already had the retail diagnostic
as a commented-out line, but retail emits `"background sound underrun\n"` when
an existing raw stream falls behind the painted time while music volume remains
positive.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4DC350` to `S_PaintChannels`.
- `functions.csv` records `FUN_004dc350` at `0x004DC350`, size 781.
- HLIL at `0x004DC366` computes mixer master volume from `s_volume`.
- The raw-stream branch compares the raw-stream end cell with the current
  painted time. When raw end is behind painted time, retail clears the paint
  buffer.
- HLIL at `0x004DC3B3` checks that the old raw end is nonzero before considering
  the underrun diagnostic.
- HLIL at `0x004DC3BC` reads `data_13e1854 + 0x2c`, the value field of the
  `s_musicvolume` cvar initialized in `S_Init`.
- HLIL at `0x004DC3CB` emits `"background sound underrun\n"`.
- The string corpus contains `data_5445c8`, exactly
  `"background sound underrun\n"`.
- The same `S_PaintChannels` slice then clears the paintbuffer, mixes voice
  channels from `data_13e1860`, paints normal channels, paints loop channels,
  transfers the paint buffer, and advances painted time.

## Source Reconstruction

Implemented source changes:

- Exposed `s_musicVolume` through `snd_local.h` for mixer-side access.
- Restored the `S_PaintChannels` raw-stream underrun diagnostic as
  `Com_DPrintf( "background sound underrun\n" )`.
- Guarded the diagnostic with `s_musicVolume && s_musicVolume->value > 0.0f`,
  matching the retail cvar-value check while keeping the source safe before
  full sound cvar initialization.
- Extended `tests/test_client_sound_voice_parity.py` to pin the retail HLIL
  branch, `s_musicvolume` value access, string-corpus entry, header exposure,
  and source diagnostic call.

No runtime launch was needed. This pass reconstructs deterministic mixer
diagnostic behavior from committed HLIL/Ghidra evidence.

## Confidence

High confidence:

- `S_PaintChannels` ownership and function size.
- Raw/background underrun string and branch location.
- `s_musicvolume` as the cvar backing the retail value read at
  `data_13e1854 + 0x2c`.
- Restoring a diagnostic that already existed in source as a commented-out
  retail-era line.

Medium confidence:

- The source null guard around `s_musicVolume` is defensive; retail assumes the
  cvar pointer is initialized before this branch is reachable.

## Validation

- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
  - 10 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 41 passed.
- `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v143 /v:minimal`
  - Build completed successfully; `quakelive_steam.exe` rebuilt.
- `git diff --check -- src\code\client\snd_mix.c src\code\client\snd_local.h tests\test_client_sound_voice_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_472.md`
  - Passed with repository LF-to-CRLF working-copy warnings on touched text
    files.

## Parity Estimate

- Focused `S_PaintChannels` raw-stream underrun diagnostic parity: 82% -> 98%.
- Focused mixer/voice/raw pass mapping parity: 91% -> 94%.
- Overall client sound-system reconstruction parity: 90.5% -> 91%.
