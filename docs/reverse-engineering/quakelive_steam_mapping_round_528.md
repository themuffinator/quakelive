# Quake Live Steam Mapping Round 528: Cgame Item Pickup And Powerup Sound Wiring

## Scope

This pass maps and tightens the cgame item-use, item-pickup, and powerup event
sound wiring around `CG_UseItem`, `CG_ItemPickup`, and the item/powerup
branches inside `CG_EntityEvent`. The target is the retail `cgamex86.dll`
path that dispatches holdable-use sounds, predicted/global pickup sounds,
powerup announcer voice clips, and local powerup activation cues.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x10019af0` | `FUN_10019af0` / `sub_10019af0` | `CG_UseItem` | High |
| `0x10019c40` | `FUN_10019c40` / `sub_10019c40` | `CG_ItemPickup` | High |
| `0x10019eb0` | `FUN_10019eb0` / `sub_10019eb0` | `CG_EntityEvent` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` lists
  `FUN_10019af0` as a 325-byte helper and `FUN_10019c40` as a 94-byte helper.
- `references/symbol-maps/cgame.json` identifies `0x10019af0` as
  `CG_UseItem` and `0x10019c40` as `CG_ItemPickup`.
- Binary Ninja HLIL for `sub_10019af0` raises
  `CG_UseItem: invalid item %d` for out-of-range use-item events, prints the
  local `No item to use` / `Use %s` center messages, updates the medkit usage
  timestamp, and plays the use-nothing, medkit, and invulnerability activation
  sounds through the cgame start-sound import at `+0x94`.
- The `EV_ITEM_PICKUP` HLIL branch plays `n_healthSound` for powerup/team
  pickups, otherwise registers and plays the item pickup sound directly, then
  queues persistant-powerup announcer clips and updates local pickup HUD state.
- The `EV_GLOBAL_ITEM_PICKUP` branch plays the global pickup sound from the
  local client, skips announcer handling behind the Quad Hog custom setting,
  queues powerup announcer clips, triggers spectator powerup tracking, and
  updates local pickup HUD state.
- The `EV_POWERUP_QUAD`, `EV_POWERUP_BATTLESUIT`, `EV_POWERUP_REGEN`, and
  `EV_POWERUP_ARMORREGEN` HLIL cases set the local active-powerup state when
  the event belongs to the local player, then play the matching item-channel
  sound handles.
- Retail `CG_RegisterSounds` HLIL registers the matching direct event sounds:
  `use_nothing.ogg`, `invul_activate.ogg`, `use_medkit.ogg`, `damage3.ogg`,
  `regen.ogg`, `ar1_pkup.ogg`, `protect3.ogg`, and `n_health.ogg`.
- Retail powerup announcer registration builds the active profile paths for
  `battlesuit.ogg`, `haste.ogg`, `invisibility.ogg`, `quad_damage.ogg`,
  `regeneration.ogg`, `armor_regen.ogg`, `damage.ogg`, `guard.ogg`, and
  `scout.ogg`.

Inferred meaning:

- The source-level pickup announcer helpers are a clean reconstruction of the
  inlined retail switch behavior in `CG_EntityEvent`.
- The missing `sub_10019af0` alias is stable enough to promote beside the
  existing Ghidra-style `FUN_10019af0` alias.
- The previous silent invalid-item clamp in `CG_UseItem` was a source-only
  divergence from retail's explicit fatal diagnostic.

## Reconstruction

- Promoted `sub_10019af0 -> CG_UseItem` in
  `references/analysis/quakelive_symbol_aliases.json`.
- Reconstructed the invalid use-item guard in `src/code/cgame/cg_event.c` so
  it calls `CG_Error( "CG_UseItem: invalid item %d", itemNum )` instead of
  silently treating the event as `HI_NONE`.
- Split the `CG_UseItem` switch default away from `HI_NONE`, preserving the
  explicit retail no-item sound case without making future unhandled valid
  use-item slots fall through to `useNothingSound`.
- Extended `tests/test_cgame_sound_wiring_parity.py` so the cgame helper
  alias/function-size gate covers `CG_UseItem` and `CG_ItemPickup`.
- Added a dedicated parity test that pins:
  - retail HLIL for holdable-use diagnostics and sound dispatch;
  - predicted/global pickup sound and announcer ordering;
  - Quad Hog announcer suppression in global pickup handling;
  - powerup activation sounds and local active-powerup state updates;
  - direct event sound registration and powerup announcer media registration.

## Remaining Boundary

Retail HLIL exposes the pickup announcer selection as inline table/switch
logic inside `CG_EntityEvent`, while the source keeps it in small helper
functions for readability. This round treats that helper split as source
structure only; the observed behavior is pinned by HLIL strings, media handle
globals, and source call ordering.

## Validation

- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_item_pickup_use_and_powerup_sounds_match_retail_wiring -q --tb=short`
- `python -c "import json; json.load(open('references/analysis/quakelive_symbol_aliases.json', encoding='utf-8')); print('ok')"`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_event_transport_parity.py tests\test_spectator_client_state_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_displaycontext_parity.py::test_cgame_event_reconstruction_keeps_retail_overtime_gameover_and_race_handlers -q --tb=short`
- `python -m pytest tests\test_cgame_impact_effect_parity.py::test_cgame_event_dispatch_keeps_retail_impact_effect_wiring -q --tb=short`

## Parity Estimate

- Focused cgame item-use/pickup/powerup sound wiring confidence:
  **before 80% -> after 97%**.
- Focused `CG_UseItem` alias/source-behavior coverage:
  **before 70% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.5% -> after 93.6%**.
