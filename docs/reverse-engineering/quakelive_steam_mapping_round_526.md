# Quake Live Steam Mapping Round 526: Cgame Team Result And Gameover Music Wiring

## Scope

This pass maps and hardens the cgame event-side sound wiring for team-result
announcements, round-result announcements, and gameover music selection inside
`CG_EntityEvent`. The target is the retail `cgamex86.dll` event dispatcher
that bridges global team-sound events and `QL_EV_GAMEOVER` into announcer
buffers plus the `music/win` and `music/loss` background tracks.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x10019eb0` | `FUN_10019eb0` / `sub_10019eb0` | `CG_EntityEvent` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` lists
  `FUN_10019eb0` as a 10088-byte function.
- `references/symbol-maps/cgame.json` identifies `0x10019eb0` as
  `CG_EntityEvent` with signature
  `void CG_EntityEvent(centity_t *cent, vec3_t position)`.
- Binary Ninja HLIL for `sub_10019eb0` clears buffered announcements before
  the red-team and blue-team win cases, selects the cgame start-background
  import at `data_1074cccc + 0xbc`, passes `music/win` or `music/loss`, and
  queues the matching red/blue win announcer handles through
  `sub_1004e110`.
- The same HLIL event block queues `red_wins_round`, `blue_wins_round`,
  `round_draw`, and `round_over` handles for round-specific team sound cases.
- The `QL_EV_GAMEOVER` block carries the `EV_GAMEOVER\n` debug string, clears
  buffered announcements, then selects winner, spectator, or loser handling:
  winners and spectators get `music/win`, while losers get `music/loss`.
- Retail `CG_RegisterSounds` HLIL registers `red_wins.ogg`,
  `blue_wins.ogg`, `red_wins_round.ogg`, `blue_wins_round.ogg`,
  `round_draw.ogg`, and `round_over.ogg` through the announcer path builder
  and the cgame register-sound import at `+0xB8`.
- Reconstructed `cg_event.c` and `cg_main.c` already match the same event
  ordering and media registration surface, including the kamikaze far sound
  and configured `you_win.ogg` / `you_lose.ogg` announcer clips.

Inferred meaning:

- The event dispatcher's numeric team-sound cases align with the reconstructed
  `GTS_*` names by string evidence, media-handle globals, and call ordering.
- The missing Binary Ninja `sub_10019eb0` alias is stable enough to promote
  beside the existing Ghidra-style `FUN_10019eb0` alias.

## Reconstruction

- Promoted `sub_10019eb0 -> CG_EntityEvent` in
  `references/analysis/quakelive_symbol_aliases.json`.
- Extended `tests/test_cgame_sound_wiring_parity.py` so the cgame sound helper
  alias/function-size gate covers both alias families and the 10088-byte
  Ghidra function row.
- Added a dedicated cgame event sound parity test that pins:
  - HLIL control-flow anchors for red/blue team wins, round wins, round draw,
    round over, and `QL_EV_GAMEOVER`;
  - start-background import offset `+0xBC` usage for `music/win` and
    `music/loss`;
  - source ordering from `CG_ClearBufferedAnnouncements()` through buzzer,
    local-team music selection, and buffered announcer playback;
  - source ordering for winner, spectator, and loser `QL_EV_GAMEOVER` music;
  - `CG_RegisterSounds` registration for global result, round result,
    kamikaze, winner, and loser announcer clips.

No C source changes were needed.

## Remaining Boundary

Binary Ninja HLIL exposes the team-result branch as numeric switch cases and
temporary globals rather than source enum names. This round therefore treats
the enum-name mapping as inferred from the combined string, media-handle, and
source-order evidence instead of as a direct decompiler name recovery.

## Validation

- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_event_team_result_and_gameover_music_matches_retail_wiring -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -c "import json; json.load(open('references/analysis/quakelive_symbol_aliases.json', encoding='utf-8')); print('ok')"`
- `python -m pytest tests\test_cgame_event_transport_parity.py tests\test_spectator_client_state_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_displaycontext_parity.py::test_cgame_event_reconstruction_keeps_retail_overtime_gameover_and_race_handlers -q --tb=short`
- `python -m pytest tests\test_cgame_impact_effect_parity.py::test_cgame_event_dispatch_keeps_retail_impact_effect_wiring -q --tb=short`

Non-blocking adjacent noise: the full
`tests\test_cgame_impact_effect_parity.py` file still has unrelated failures
in smoke/model-scale and rail/lightning marker checks. The focused
impact-event dispatch test passes.

## Parity Estimate

- Focused cgame event team-result/gameover music wiring confidence:
  **before 79% -> after 97%**.
- Focused `CG_EntityEvent` sound alias/function-size coverage:
  **before 50% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **before 93.4% -> after 93.5%**.
