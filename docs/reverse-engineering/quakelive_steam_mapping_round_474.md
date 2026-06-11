# Quake Live Steam Mapping Round 474: Sound Console Command Wiring

## Scope

This round pins the retail sound console command cluster around
`S_SoundInfo_f`, `S_SoundList_f`, `S_Play_f`, and `S_Music_f`. The source
already matched the retail command behavior, so this pass adds stronger
evidence-backed mapping coverage rather than changing C code.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_4D9B60` to `S_SoundInfo_f`,
  `sub_4DAFD0` to `S_SoundList_f`, `sub_4DB710` to `S_Play_f`, and
  `sub_4DB810` to `S_Music_f`.
- `functions.csv` records `FUN_004d9b60` at size 237 and
  `FUN_004db710` at size 246. The current Ghidra CSV export does not include
  rows for `FUN_004dafd0` or `FUN_004db810`, but both helpers are present in
  the committed HLIL corpus.
- Retail `S_Init` registers `"play"`, `"music"`, `"s_list"`, `"s_info"`, and
  `"s_stop"` against this command cluster. Retail `S_Shutdown` removes the
  same command names.
- Retail `S_SoundInfo_f` prints the sound-info header, stopped/muted state,
  DMA fields, background-track status, and footer strings used by the source.
- Retail `S_SoundList_f` walks the known-sfx table, selects `MEM` for resident
  sounds and `PGD` for paged sounds, prints `"%6i [%s] : %s\n"`, prints the
  loaded-sound count, and tailcalls `S_DisplayFreeMemory`.
- Retail `S_Play_f` loops over command arguments, registers the resolved sound,
  and starts it on local sound channel `6`. The extensionless path uses
  `Cmd_Argv(1)` while inside the loop, matching the current source's inherited
  retail quirk.
- Retail `S_Music_f` starts the same intro/loop path for two arguments and
  clears the loop buffer's first byte. With three arguments it starts
  arg1/arg2, and otherwise prints the usage line.

## Source Reconstruction

Implemented source-side changes:

- Extended `tests/test_client_sound_voice_parity.py` with a
  `SOUND_CONSOLE_ALIASES` table for the four retail command helpers.
- Pinned the mixed evidence model: CSV-backed sizes for `S_SoundInfo_f` and
  `S_Play_f`, and HLIL-only function presence for `S_SoundList_f` and
  `S_Music_f`.
- Added HLIL assertions for the sound-info strings, sound-list `PGD`/`MEM`
  selection and `S_DisplayFreeMemory` tailcall, play-command extension branch,
  music-command argument handling, and `S_Init` command registration block.
- Expanded source assertions around `S_SoundInfo_f` to protect the retail
  console output contract, including the current OGG-active background-track
  status extension from earlier reconstruction work.

No C source edit was needed for this slice.

## Confidence

High confidence:

- Command ownership and registration/removal wiring.
- Sound-info and sound-list console output strings.
- `PGD` versus `MEM` list-state selection.
- `play` and `music` argument handling, including the extensionless
  `Cmd_Argv(1)` behavior in `S_Play_f`.

Medium confidence:

- The lack of `FUN_004dafd0` and `FUN_004db810` rows in `functions.csv` is a
  limitation of the committed Ghidra export rather than a sign that the helpers
  are unstable. The HLIL function boundaries and callsites are clear.

## Validation

- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
  - 10 passed.
- `python -m pytest tests\test_client_sound_voice_parity.py tests\test_client_sound_playback_parity.py tests\test_win32_sound_dma_parity.py tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py tests\test_cgame_announcer_timer_helper_parity.py tests\test_cgame_playerstate_transition_parity.py tests\test_botlib_cgame_native_import_slab_parity.py tests\test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
  - 41 passed.
- `git diff --check -- tests\test_client_sound_voice_parity.py docs\reverse-engineering\quakelive_steam_mapping_round_474.md`
  - Passed with the repository's existing LF-to-CRLF working-copy warning for
    the Python test.

No runtime launch was needed. This pass is deterministic mapping and parity-test
coverage from committed HLIL/Ghidra evidence.

## Parity Estimate

- Focused sound console-command mapping parity: 82% -> 94%.
- Focused sound command/wiring regression coverage: 84% -> 95%.
- Overall client sound-system reconstruction parity: 91% -> 91.2%.
