# Quake Live Steam Mapping Round 524: Cgame Configstring Music Bridge

## Scope

This pass maps and hardens the cgame background-music bridge around
`CG_StartMusic`. The target is the retail `cgamex86.dll` helper that parses
`CS_MUSIC`, starts the paired intro/loop track, and is reached from init,
configstring updates, and map restarts.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x10025320` | `FUN_10025320` / `sub_10025320` | `CG_StartMusic` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` lists
  `FUN_10025320` as a 196-byte helper.
- `references/symbol-maps/cgame.json` identifies `0x10025320` as
  `CG_StartMusic` with signature `void CG_StartMusic(void)`.
- Binary Ninja HLIL for `sub_10025320` reads the `CS_MUSIC` configstring
  storage, parses two tokens with the cgame token parser, copies each token
  into bounded `MAX_QPATH`-sized buffers, and calls the cgame
  start-background-track import at `data_1074cccc + 0xbc`.
- HLIL callsites invoke `sub_10025320` from the cgame init tail, from the
  `CG_ConfigStringModified` switch case for configstring index `2`, and from
  the map-restart path after buffered announcements are cleared.
- The server-command dispatcher still recognizes `playMusic` and `stopMusic`;
  the retail `stopMusic` branch calls import offset `0xc0`.

Inferred meaning:

- The reconstructed source-side `CG_StartMusic()` body is the exact bridge
  between `CS_MUSIC` and `trap_S_StartBackgroundTrack()`. The import offset,
  callsites, source ordering, and symbol-map name all agree.
- The missing `sub_10025320` alias is stable enough to promote beside the
  existing `FUN_10025320` alias.

## Reconstruction

- Promoted `sub_10025320 -> CG_StartMusic` in
  `references/analysis/quakelive_symbol_aliases.json`.
- Extended `tests/test_cgame_sound_wiring_parity.py` so the cgame sound helper
  table verifies both alias families and the 196-byte Ghidra function row.
- Added a dedicated cgame music bridge parity test that pins:
  - retail HLIL token parsing and start-background import slot `+0xBC`;
  - init ordering from `CG_SetConfigValues()` to `CG_StartMusic()`;
  - configstring update handling for `CS_MUSIC`;
  - map-restart ordering from `CG_ClearBufferedAnnouncements()` through
    `CG_StartMusic()` to `trap_S_ClearLoopingSounds(qtrue)`;
  - direct `playMusic` / `stopMusic` server-command handlers;
  - cgame syscall declarations and `CG_S_STARTBACKGROUNDTRACK` /
    `CG_S_STOPBACKGROUNDTRACK` bridge wrappers.

No C source changes were needed.

## Remaining Boundary

The retail command dispatcher HLIL compresses the direct `playMusic` call
through surrounding command-parse control flow, so this round treats the
source-level `CG_ParsePlayMusic()` body as the stable behavior owner while the
HLIL anchors the dispatcher strings and the `stopMusic` import slot directly.

## Validation

- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_music_configstring_and_server_command_bridge_matches_retail_wiring -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_sound_import_wiring_reconstructs_retail_clear_slots tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_sound_slab_keeps_volume_slots_direct_and_legacy_slots_fixed_volume tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_import_table_source_matches_reconstructed_slot_surface -q --tb=short`

## Parity Estimate

- Focused cgame configstring/background-music bridge confidence:
  **before 82% -> after 98%**.
- Focused `CG_StartMusic` alias coverage:
  **before 50% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.3% -> after 93.4%**.
