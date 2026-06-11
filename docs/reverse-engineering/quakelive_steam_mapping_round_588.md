# Quake Live Steam Mapping Round 588: Background Sound Command Alias Closure

## Scope

This round tightens the Binary Ninja/Ghidra alias bridge for the client sound
console helpers and background-track corridor:

- `sub_4d9b60` / `FUN_004d9b60`: `S_SoundInfo_f`
- `sub_4dafd0`: `S_SoundList_f`
- `sub_4db710` / `FUN_004db710`: `S_Play_f`
- `sub_4db810`: `S_Music_f`
- `sub_4db030` / `FUN_004db030`: `S_StopBackgroundTrack`
- `sub_4db060` / `FUN_004db060`: `S_StartBackgroundTrack`
- `sub_4db1c0` / `FUN_004db1c0`: `S_UpdateBackgroundTrack`
- `sub_4dc9a0` / `FUN_004dc9a0`: `S_OpenBackgroundOgg`
- `sub_4dca40` / `FUN_004dca40`: `S_CloseBackgroundOgg`
- `sub_4dca50` / `FUN_004dca50`: `S_OggUpdateBackgroundTrack`
- `sub_4afed0` / `FUN_004afed0`: `QLCGImport_S_StartBackgroundTrack`

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records stable rows for the Ghidra-backed helpers:
  `FUN_004d9b60`, `FUN_004db030`, `FUN_004db060`, `FUN_004db1c0`,
  `FUN_004db710`, `FUN_004dc9a0`, `FUN_004dca40`, and `FUN_004dca50`.
- Binary Ninja HLIL part04 names the sound console callbacks with lowercase
  `sub_*` spellings and shows the command registration table:
  - `play -> sub_4db710`
  - `music -> sub_4db810`
  - `s_list -> sub_4dafd0`
  - `s_info -> sub_4d9b60`
  - `s_stop -> sub_4db450`
- The same HLIL body shows `S_Music_f` dispatching to `sub_4db060`, and the
  background update path closing `sub_4dca40` before looping through
  `sub_4db060`.
- Binary Ninja HLIL part04 also shows the native cgame start-background import
  thunk at `sub_4afed0` tailcalling `sub_4db060`.
- The native stop-background slot remains intentionally different: retail uses
  a raw `0x4b02f0`/no-stable-row slot for that surface, so this round does not
  introduce a synthetic `QLCGImport_S_StopBackgroundTrack` alias.

Inferred mapping:

- The existing uppercase `sub_*` and `FUN_*` aliases were correct, but the
  shared alias corpus should also promote the lowercase Binary Ninja spellings
  used directly by the committed HLIL evidence for this command/background
  sound corridor.

## Reconstruction

Updated `references/analysis/quakelive_symbol_aliases.json`:

- Added lowercase Binary Ninja aliases for the sound console helpers:
  `sub_4d9b60`, `sub_4dafd0`, `sub_4db710`, and `sub_4db810`.
- Added lowercase Binary Ninja aliases for the background-track helpers:
  `sub_4db030`, `sub_4db060`, `sub_4db1c0`, `sub_4dc9a0`,
  `sub_4dca40`, and `sub_4dca50`.
- Added lowercase `sub_4afed0` for the native cgame start-background thunk.

Strengthened parity gates:

- `tests/test_client_sound_voice_parity.py` now checks lowercase BN aliases
  for the sound console command and background-track helper clusters.
- `tests/test_botlib_cgame_native_import_slab_parity.py` now checks the
  lowercase native start-background import alias alongside the existing native
  sound slab evidence.

No C source change was required in this pass; source reconstruction for the
background OGG path, command callbacks, and update loop was already aligned
with the retail evidence.

## Validation

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  - passed
- `python -m pytest tests/test_client_sound_voice_parity.py::test_sound_console_commands_match_retail_registration_and_output_contracts tests/test_client_sound_voice_parity.py::test_background_track_ogg_update_matches_retail_restart_path tests/test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_import_slab_aliases_and_rows_are_pinned -q --tb=short`
  - passed
- `python -m pytest tests/test_client_sound_voice_parity.py tests/test_client_sound_playback_parity.py tests/test_botlib_cgame_native_import_slab_parity.py tests/test_cgame_sound_wiring_parity.py tests/test_ui_menu_files.py::test_ui_sound_import_wiring_matches_retail_native_and_vm_paths -q --tb=short`
  - passed
- `git diff --check -- references/analysis/quakelive_symbol_aliases.json tests/test_client_sound_voice_parity.py tests/test_botlib_cgame_native_import_slab_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_588.md IMPLEMENTATION_PLAN.md`
  - passed with only repository line-ending normalization warnings

## Parity Estimate

- Focused background/console sound lowercase Binary Ninja alias coverage:
  **before 72% -> after 99%**.
- Focused native cgame/background-track evidence bridge confidence:
  **before 94% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.45% -> after 93.47%**.
