# Red Rover Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Red Rover (`GT_RED_ROVER`) path across the qagame
round controller, qagame-to-cgame match-state configstrings, hidden round-start
side channel, infection-role controller helpers, `scores_rr` scoreboard
transport, cgame score parser, infected player presentation, survivor-warning
sound, and HUD round-state consumers. The concrete source reconstruction is the
retail compact Red Rover round-state payload plus the recovered invalid-state
fatal in the RR controller.

## Evidence Used

- qagame Binary Ninja HLIL:
  - `0x10064280` resolves expired deferred `RR_RoundStateTransition` work and
    returns the current RR round-state latch.
  - `0x100649F0` is the `RR_RoundStateTransition` body. It writes
    configstring `0x295` as `\time\-1\round\0`, `\time\%d\round\%d`, or
    `\round\%d` depending on controller state.
  - The active transition writes configstring `0x296` with the active round
    start time. The complete transition later writes `0x296` as `-1` before
    scheduling either the next seed/warmup phase or the exit state.
  - The same body preserves the
    `RR_RoundStateTransition: invalid state` diagnostic.
- qagame Ghidra `decompile_top_functions.c`:
  - The decompile mirrors the compact `0x295` writes, active `0x296` start
    write, complete `0x296 = -1` clear, round-score awards, and exit-delay
    branch.
- qagame symbol map:
  - Promoted RR owners include `G_RRResolveRoundState`,
    `RR_RoundStateTransition`, `G_RRHandleDamageScore`,
    `G_RRResetClientForRound`, `G_RRInitClient`,
    `G_RRCheckRoundCompletion`, `G_RRCheckExitRules`,
    `G_RRResolveAutoJoinTeam`, `G_RRSeedInfectionTeams`,
    `G_RRApplySurvivalBonus`, `G_RRCheckInfectionSpread`,
    `G_RRTrackRoundActivity`, `G_RRInitRoundController`, and
    `G_RRHandlePlayerDeath`.
- cgame evidence:
  - The cgame symbol map pins `CG_ParseRedRoverScores` to the `scores_rr`
    transport.
  - Existing cgame source and parity gates preserve the RR infected POI shader,
    local infected sound, persistent infected loop, survivor-warning global
    team sound, RR placement/status HUD branches, and compact round-state
    parser support.

## Observed Wiring

| Surface | Retail-backed mapping | Source state after this pass |
| --- | --- | --- |
| Gametype id | `GT_RED_ROVER` owns the RR round controller and shares round-controller client-side HUD inference with CA and Freeze. | Existing factory, warmup, scoreboard, infected, and HUD routes already branch on RR. |
| Inactive payload | Retail qagame publishes `\time\-1\round\0` to `CS_MATCH_STATE`. | `G_BuildRedRoverMatchStateInfo` now emits the same inactive payload. |
| Warmup payload | Retail qagame publishes `time` and `round`, using the pending warmup release time and next round ordinal. | RR warmup now publishes only those fields through the compact builder. |
| Active payload | Retail qagame publishes `\round\%d` to `CS_MATCH_STATE` and separately writes the active round start to slot `0x296`. | RR active now emits the compact round payload and preserves the hidden round-start side channel. |
| Complete/exit payload | Retail qagame clears slot `0x296` to `-1` while the visible match-state payload remains the completed round number. | RR complete/exit now clear the round-start side channel and keep the compact round payload. |
| Invalid controller state | Retail calls the fatal error path with `RR_RoundStateTransition: invalid state`. | The RR controller now calls `G_Error` for unexpected round-state values. |
| Infection seed | Retail routes the pending state machine through a seed/warmup split before active release. | The compact publisher derives a fallback round ordinal from team scores when the current centralized update path is reached before `level.roundNumber` is latched. |
| Scoreboard transport | Retail qagame emits `scores_rr`; retail cgame parses a wider per-client RR row block. | Existing `G_BuildRedRoverScoreboardMessage` and `CG_ParseRedRoverScores` mappings were revalidated. |
| Infection helpers | Retail RR mutates teams/roles through seed, autojoin, damage-score, death, spread, survival-bonus, and completion helpers. | Existing helper boundaries and caller wiring were revalidated against symbol-map evidence and focused static tests. |
| Client presentation | Retail cgame has RR-specific infected marker, sound, loop, survivor warning, and non-team placement/status branches. | Existing cgame marker, event, media, and HUD tests passed after the server-side RR reconstruction. |

## Source Reconstruction

- Added `G_RedRoverPublishedRoundNumber` and
  `G_BuildRedRoverMatchStateInfo` in `src/code/game/g_match_state.c`.
- Changed `G_UpdateMatchStateConfigString` so RR uses the compact retail
  configstring `0x295` payload instead of the richer SRP match-state payload.
- Changed `G_UpdateRoundStartConfigString` so RR complete and exit states clear
  `CS_ROUND_START_TIME` to `-1`, matching retail slot `0x296`.
- Replaced the silent RR controller default case in
  `src/code/game/g_active.c` with the retail fatal diagnostic.
- Strengthened match-state harness tests and static parity tests for RR compact
  payloads, side-channel clearing, cgame compact/sparse parser registration,
  and controller invalid-state handling.

## Verification

- `python -m pytest tests/test_match_state_configstring.py tests/test_game_team_count_parity.py tests/test_game_helper_seam_parity.py tests/test_game_round_controller_helper_parity.py::test_red_rover_controller_readback_helpers_match_retail_mapping_surface -q --tb=short`
  - `42 passed, 8 skipped`
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -k red_rover -q --tb=short`
  - `2 passed, 32 deselected`
- `python -m pytest tests/test_cgame_player_marker_parity.py tests/test_cgame_event_transport_parity.py -q --tb=short`
  - `17 passed`
- `python -m pytest tests/test_game_exit_rules_parity.py::test_score_is_tied_keeps_red_rover_on_retail_non_team_leader_path tests/test_game_round_controller_helper_parity.py::test_red_rover_autojoin_helper_routes_team_selection -q --tb=short`
  - `2 passed`

## Open Questions

- The lower award and medal tail after RR round completion remains inherited
  from earlier reconstruction. This pass revalidated the surrounding helper
  ownership and event/scoreboard edges, but did not exhaustively rename every
  award helper below the complete-state branch.
- Retail zero-delay warmup publication has subtle recursive controller
  ordering. The current source centralizes publishing and now matches the
  visible compact payload contract, but a future single-step trace could
  tighten the exact ordering of no-delay warmup versus active publication.
- The infection-seed state is source-side explicit for readability. Retail
  exposes the same seed/warmup/active split through controller state values,
  but its seed-state configstring write is less direct than the source helper
  call path.

## Parity Estimate

Focused Red Rover qagame/cgame round-state, configstring, infection-role,
scoreboard, marker, sound, and HUD wiring moves approximately **93% -> 98%**.
The remaining gap is mostly lower award-tail confidence and exact zero-delay
publication ordering. Broader gametype/source parity remains approximately
**99%**.
