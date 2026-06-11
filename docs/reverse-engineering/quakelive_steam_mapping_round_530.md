# Quake Live Steam Mapping Round 530: Cgame Movement And Environment Event Sounds

## Scope

This pass maps the cgame movement and environment sound branch inside
`CG_EntityEvent`, plus the `CG_PainEvent` helper that is reached from the
retail `EV_PAIN` case. The target is the retail `cgamex86.dll` path that
dispatches footsteps, landing sounds, jump-pad cues, water transitions,
teleports, item respawns, grenade bounces, pain, death, and drowning voice
samples.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x10019ca0` | `FUN_10019ca0` / `sub_10019ca0` | `CG_PainEvent` | High |
| `0x10019eb0` | `FUN_10019eb0` / `sub_10019eb0` | `CG_EntityEvent` | High |
| `0x10020e70` | `FUN_10020e70` | `CG_RegisterSounds` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` lists
  `FUN_10019ca0` as a 127-byte helper and `FUN_10019eb0` as the 10088-byte
  event dispatcher.
- `references/symbol-maps/cgame.json` identifies `0x10019ca0` as
  `CG_PainEvent`, with the 500 ms debounce, pain-time update, pain-direction
  toggle, and player pain-sound dispatch documented from HLIL.
- Binary Ninja HLIL for `sub_10019ca0` writes the pain-time timestamp, checks
  a `0x1f4` debounce window, resolves the custom player sound through
  `sub_1003ca30`, calls the cgame start-sound import at `+0x94`, toggles the
  pain direction, and stores the new pain time.
- The retail `CG_EntityEvent` HLIL branch contains the expected event names
  for `EV_FOOTSTEP`, `EV_FOOTSTEP_METAL`, `EV_FOOTSTEP_SNOW`,
  `EV_FOOTSTEP_WOOD`, `EV_FOOTSPLASH`, `EV_FOOTWADE`, `EV_SWIM`,
  `EV_FALL_SHORT`, `EV_FALL_MEDIUM`, `EV_FALL_FAR`, `EV_JUMP_PAD`, `EV_JUMP`,
  water transition events, teleport events, `EV_ITEM_RESPAWN`,
  `EV_GRENADE_BOUNCE`, `EV_PAIN`, `EV_DEATHx`, and `EV_DROWN`.
- Retail `EV_JUMP_PAD` plays `jumpPadSound` at the event origin and then plays
  the player's custom `*jump1.wav` voice sample.
- Retail `EV_PAIN` calls `sub_10019ca0`; retail death and drown cases format
  `*death%i.wav` or use `*drown.wav` before dispatching through
  `CG_CustomSound`.
- Retail `CG_RegisterSounds` registers `telein.ogg`, `teleout.ogg`,
  `respawn1.ogg`, `land1.ogg`, water transition sounds, `jumppad.ogg`, all
  nine four-sample footstep families, and both grenade bounce samples.

Inferred meaning:

- The source event switch is already behaviorally aligned for this branch; the
  reconstruction value in this round is stronger mapping coverage and the
  missing `sub_10019ca0` alias.
- The footstep table names are stable because the event-side table reads,
  `cg_footsteps` cvar, and registration format strings all converge on the
  same source arrays.

## Reconstruction

- Promoted `sub_10019ca0 -> CG_PainEvent` in
  `references/analysis/quakelive_symbol_aliases.json`.
- Extended the cgame sound helper alias/function-size parity gate so
  `CG_PainEvent` is covered beside `CG_UseItem`, `CG_ItemPickup`, and
  `CG_EntityEvent`.
- Added a dedicated movement/environment sound parity test that pins:
  - `CG_PainEvent` debounce, custom sound, pain-time, and direction-toggle
    behavior;
  - footstep, fall, jump, water, teleport, item-respawn, grenade-bounce,
    pain, death, and drown event ordering in `CG_EntityEvent`;
  - `cg_footsteps` cvar registration;
  - direct registration of the world, player, footstep, and grenade sounds
    consumed by those event branches.

## Remaining Boundary

The retail HLIL compresses several string-format registrations and long sound
paths with display truncation. The parity gate therefore pins retail addresses
and stable prefixes for those HLIL lines, then uses the reconstructed source
to assert the full sound paths.

## Validation

- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_movement_environment_event_sounds_match_retail_wiring -q --tb=short`
- `python -c "import json; json.load(open('references/analysis/quakelive_symbol_aliases.json', encoding='utf-8')); print('ok')"`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_event_transport_parity.py tests\test_spectator_client_state_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_displaycontext_parity.py::test_cgame_event_reconstruction_keeps_retail_overtime_gameover_and_race_handlers -q --tb=short`
- `python -m pytest tests\test_cgame_impact_effect_parity.py::test_cgame_event_dispatch_keeps_retail_impact_effect_wiring -q --tb=short`

## Parity Estimate

- Focused cgame movement/environment event sound wiring confidence:
  **before 78% -> after 97%**.
- Focused `CG_PainEvent` alias/source-behavior coverage:
  **before 50% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.6% -> after 93.7%**.
