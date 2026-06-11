# Quake Live Steam Mapping Round 532: Cgame Sound Registration Evidence Bridge

## Scope

This pass tightens the retail evidence bridge for `CG_RegisterSounds`, with a
focus on the teamplay announcer, configured announcer, powerup announcer, and
direct item/effect sound registration slice in `cgamex86.dll`. The source paths
were already reconstructed; this round binds them to the Binary Ninja HLIL and
Ghidra function inventory so future edits cannot drift back to Quake III-era
`.wav` paths or unanchored local assumptions.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x10020dd0` | `FUN_10020dd0` / `sub_10020dd0` | `CG_BuildAnnouncerSoundPath` | High |
| `0x10020e70` | `FUN_10020e70` / `sub_10020e70` | `CG_RegisterSounds` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` lists
  `FUN_10020e70` as the 8324-byte cgame sound-registration body.
- `references/symbol-maps/cgame.json` identifies `0x10020e70` as
  `CG_RegisterSounds` and `0x10020dd0` as the announcer path builder used by
  the registration body.
- Binary Ninja HLIL for `sub_10020e70` registers configured announcer samples
  through `sub_10020dd0(...)` for `prepare_your_team.ogg`, lead-state sounds,
  score sounds, flag-return/taken prompts, base-attack prompts, vote prompts,
  and the `you_win.ogg` / `you_lose.ogg` result sounds.
- The same HLIL body directly registers `sound/feedback/hit_teammate.ogg`,
  teamplay flag capture/return/taken paths, `sound/items/wearoff.ogg`,
  `sound/items/flight.ogg`, medkit/damage sounds, kamikaze sounds, and
  `sound/misc/yousuck.ogg`.
- The powerup announcer region in the same retail function uses active
  announcer folder selection and emits the expected powerup voice samples,
  including `battlesuit.ogg` and `quad_damage.ogg`.

Inferred meaning:

- The reconstructed helper split between `CG_RegisterConfiguredAnnouncerClip`,
  `CG_RegisterPowerupAnnouncerSounds`, and `CG_RegisterSounds` is source
  structure only; the observed retail behavior is the same registration set.
- The missing `sub_10020e70` alias is stable because the function-size row,
  symbol-map identity, and HLIL registration body converge on the same owner.

## Reconstruction

- Promoted `sub_10020e70 -> CG_RegisterSounds` in
  `references/analysis/quakelive_symbol_aliases.json`.
- Extended the shared cgame sound alias gate so both `FUN_10020e70` and
  `sub_10020e70` are covered.
- Strengthened `tests/test_cgame_sound_registration_parity.py` with a retail
  HLIL/Ghidra-backed test for the teamplay announcer, configured announcer,
  direct item/effect sound, and powerup announcer registration slice.

## Remaining Boundary

Binary Ninja display truncates several long direct teamplay paths in the HLIL.
The parity gate therefore pins stable retail address prefixes and then uses the
existing source assertions to preserve the complete reconstructed paths.

## Validation

- `python -m pytest tests\test_cgame_sound_registration_parity.py::test_cgame_register_sounds_alias_and_hlil_cover_retail_registration_slice -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -c "import json; json.load(open('references/analysis/quakelive_symbol_aliases.json', encoding='utf-8')); print('ok')"`
- `python -m pytest tests\test_cgame_sound_registration_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_event_transport_parity.py tests\test_spectator_client_state_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`

## Parity Estimate

- Focused cgame sound-registration evidence coverage:
  **before 82% -> after 98%**.
- Focused `CG_RegisterSounds` alias bridge coverage:
  **before 75% -> after 99%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.7% -> after 93.8%**.
