# Quake Live Steam Mapping Round 521: Cgame Low-Ammo Sound Warning

## Scope

This pass tightens the cgame low/no-ammo sound-warning reconstruction around
`CG_CheckAmmo`. It links the retail helper to the cvar/media/HUD wiring that
uses the same warning state.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x10042E50` | `FUN_10042e50` / `sub_10042e50` | `CG_CheckAmmo` | High |

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` lists
  `FUN_10042e50` as a 183-byte helper.
- `references/analysis/quakelive_symbol_aliases.json` already promotes both
  `FUN_10042e50` and `sub_10042e50` to `CG_CheckAmmo`.
- `references/symbol-maps/cgame.json` identifies `0x10042E50` as the retail
  low-ammo warning helper.
- Binary Ninja HLIL for `sub_10042e50` reads the active weapon from the current
  playerstate, reads that weapon's ammo, multiplies the per-weapon max-ammo
  table by the cached low-ammo percentile, writes the warning state, and calls
  the cgame local-sound import on channel `6`.
- Binary Ninja HLIL for `sub_10043b60` calls `sub_10042e50` after local
  playerstate sound handling and before playerstate event replay.

Inference:

- The local `CHAN_LOCAL_SOUND` warning playback in `cg_playerstate.c` is the
  source-level counterpart to the retail import call at `data_1074cccc + 0x9c`.
  The surrounding `cg_lowAmmoWarningSound` selector maps the level-1 warning to
  either low-ammo or no-ammo media while level 2 always plays no-ammo.

## Reconstruction

- Added `CG_CheckAmmo` to the focused cgame sound helper alias/function-size
  parity table.
- Added a dedicated cgame sound parity gate that pins:
  - active weapon and per-weapon ammo lookup;
  - per-weapon threshold calculation from cached
    `cg.lowAmmoWarningPercentile`;
  - warning state values `0`, `1`, and `2`;
  - no-repeat behavior when the warning state has not changed;
  - level-2 direct `noAmmoSound` playback on `CHAN_LOCAL_SOUND`;
  - level-1 `cg_lowAmmoWarningSound` selection between `lowAmmoSound`,
    `noAmmoSound`, and silence;
  - cvar registration bounds, cached percentile update, and media paths;
  - HUD and weapon-bar consumers of the same warning state;
  - transition ordering through `CG_CheckAmmo`.

No C source changes were needed.

## Remaining Boundary

The HLIL call signature for the `+0x9c` cgame import carries a decompiler
artifact third value in this helper. Other sound bridge evidence identifies
the slot as the standard local-sound import; the source-level channel and media
behavior are therefore pinned, while the extra HLIL argument is treated as an
artifact rather than a source contract.

## Validation

- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_low_ammo_sound_warning_matches_retail_threshold_contract -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_displaycontext_parity.py::test_cgame_true_useitem_view_vignette_voice_water_and_zoom_cvars_match_retail_table_and_wiring tests\test_cgame_displaycontext_parity.py::test_cgame_early_audio_effect_cvars_match_retail_table_and_wiring tests\test_cgame_displaycontext_parity.py::test_cgame_remaining_retail_cvars_match_table_and_wiring -q --tb=short`
- `python -m pytest tests\test_cgame_playerstate_transition_parity.py tests\test_cgame_snapshot_parity.py::test_transition_player_state_keeps_retail_follow_reset_and_intermission_flow -q --tb=short`

## Parity Estimate

- Focused cgame low-ammo sound warning mapping:
  **before 84% -> after 98%**.
- Focused low-ammo cvar/media/HUD sound-state coupling:
  **before 86% -> after 97%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.0% -> after 93.1%**.
