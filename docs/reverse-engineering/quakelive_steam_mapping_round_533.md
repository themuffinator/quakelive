# Quake Live Steam Mapping Round 533: Native Cgame Sound Import Alias Bridge

## Scope

This pass tightens the retail alias bridge for the native cgame sound import
slab in `quakelive_steam.exe`. The behavior and slot ordering were already
reconstructed; this round promotes the matching Ghidra `FUN_*` names for the
stable sound wrapper rows so the shared alias corpus covers both Binary Ninja
and Ghidra spellings.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x004afe10` | `FUN_004afe10` / `sub_4AFE10` | `QLCGImport_S_StartSound` | High |
| `0x004afe20` | `FUN_004afe20` / `sub_4AFE20` | `QLCGImport_S_StartSoundVolume` | High |
| `0x004afe50` | `FUN_004afe50` / `sub_4AFE50` | `QLCGImport_S_StartLocalSoundVolume` | High |
| `0x004afe90` | `FUN_004afe90` / `sub_4AFE90` | `QLCGImport_S_AddLoopingSound` | High |
| `0x004afea0` | `FUN_004afea0` / `sub_4AFEA0` | `QLCGImport_S_UpdateEntityPosition` | High |
| `0x004afeb0` | `FUN_004afeb0` / `sub_4AFEB0` | `QLCGImport_S_Respatialize` | High |
| `0x004afec0` | `FUN_004afec0` / `sub_4AFEC0` | `QLCGImport_S_RegisterSound` | High |
| `0x004afed0` | `FUN_004afed0` / `sub_4AFED0` | `QLCGImport_S_StartBackgroundTrack` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` lists
  these sound import wrappers with stable sizes: 9 bytes for the simple
  tail-call wrappers, 36 bytes for `S_StartSoundVolume`, and 28 bytes for
  `S_StartLocalSoundVolume`.
- Binary Ninja HLIL shows `sub_4AFE10` tail-calling `S_StartSound`,
  `sub_4AFE20` converting the float volume and calling `S_StartSoundVolume`,
  `sub_4AFE50` calling `S_StartLocalSoundVolume`, and the remaining sound
  wrappers tail-calling the expected engine helpers.
- The retail native import table stores this band consecutively at
  `data_5659ec..data_565a14`, followed by the raw stop-background-track slot
  at `data_565a18 = 0x4b02f0`.
- The reconstructed source keeps the same slot split: native volume-aware
  imports are direct host calls, legacy QVM start-sound slots remain fixed
  volume, frame/killall loop clears are distinct imports, and no synthetic
  `QLCGImport_S_StopBackgroundTrack` alias is introduced.

Inferred meaning:

- The Ghidra `FUN_*` names are safe to promote because each row has a stable
  function-size entry and the paired HLIL/table evidence already identifies the
  owner.
- The existing decision to keep stop-background-track as a raw table slot
  remains correct; this round intentionally avoids inventing a missing wrapper.

## Reconstruction

- Promoted the eight Ghidra-style native cgame sound wrapper aliases in
  `references/analysis/quakelive_symbol_aliases.json`.
- Extended `tests/test_botlib_cgame_native_import_slab_parity.py` so the native
  import slab gate checks both `sub_*` and `FUN_*` spellings for the sound
  wrapper band and reuses the same Ghidra function-size rows.

## Remaining Boundary

This is an alias/evidence bridge only. The retail stop-background-track table
entry at `0x004b02f0` still has no stable function row and remains deliberately
unpromoted.

## Validation

- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_import_slab_aliases_and_rows_are_pinned -q --tb=short`
- `python -c "import json; json.load(open('references/analysis/quakelive_symbol_aliases.json', encoding='utf-8')); print('ok')"`
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py tests\test_cgame_sound_registration_parity.py -q --tb=short`
- `python -m pytest tests\test_client_sound_playback_parity.py tests\test_client_sound_voice_parity.py -q --tb=short`

## Parity Estimate

- Focused native cgame sound import alias coverage:
  **before 88% -> after 99%**.
- Focused cgame sound import Ghidra/Binary Ninja bridge coverage:
  **before 82% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.8% -> after 93.85%**.
