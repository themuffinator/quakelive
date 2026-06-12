# Attack and Defend Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Attack and Defend (`GT_ATTACK_DEFEND`) path across the
qagame round controller, match-state configstrings, hidden round-start side
channel, `scores_ad` round-history transport, objective flag wiring, cgame
score parser, warmup banner, round-score panel, POI media, and shared
CTF-family scoreboard feeders. The concrete reconstruction is the retail
compact A/D match-state payload plus cgame sparse-payload parsing.

## Evidence Used

- qagame Binary Ninja HLIL:
  - `0x10035780` resolves expired deferred `AD_RoundStateTransition` work and
    returns the current A/D round-state latch.
  - `0x10035B70` is the `AD_RoundStateTransition` body. It writes configstring
    `0x295` as `\time\-1\round\0\turn\0\state\0`,
    `\time\%d\round\%d\turn\%d\state\1`, or `\turn\%d\state\2`.
  - The active transition writes configstring `0x296` with the round start
    time. The complete transition later writes `0x296` as `-1` and leaves the
    active `0x295` turn/state payload visible while the next warmup is pending.
  - The same body preserves the
    `AD_RoundStateTransition: invalid state` diagnostic.
  - `0x100364A0`, `0x100365F0`, and `0x10036710` clear, update, and publish the
    20-entry `scores_ad` history window.
- qagame Ghidra `decompile_top_functions.c`:
  - The decompile mirrors the compact `0x295` writes and the A/D exit-rule
    branch around timelimit, scorelimit, and mercylimit.
- qagame symbol map:
  - Promoted A/D owners include `G_ADResolveRoundState`,
    `AD_RoundStateTransition`, `G_ADResolveAttackingTeam`,
    `G_ADResolveDefendingTeam`, `G_ADResetScoreHistory`, and
    `G_ADUpdateScoreHistory`.
- cgame evidence:
  - The cgame symbol map pins `CG_ParseADScores` to the `scores_ad` transport.
  - cgame HLIL preserves `ATTACK THE FLAG!`, `DEFEND THE FLAG!`,
    `ATTACK THE FLAG`, and `DEFEND THE FLAG` in the warmup/start banner paths.
  - Existing cgame mapping pins shared CTF-family team-list/stat feeders,
    `CG_DrawADRoundScoreboard`, `CG_DrawDominationOwnedFlags`, POI sprites, and
    match-end condition drawing for `GT_ATTACK_DEFEND`.

## Observed Wiring

| Surface | Retail-backed mapping | Source state after this pass |
| --- | --- | --- |
| Gametype id | `GT_ATTACK_DEFEND` is the raw retail `0xb` branch in qagame/cgame and shares CTF flag objects. | Factory aliases, map item validation, flag status, team spawn selection, and CTF-style scoreboard rows already route through A/D. |
| Inactive payload | Retail qagame publishes `\time\-1\round\0\turn\0\state\0` to `CS_MATCH_STATE`. | `G_BuildAttackDefendMatchStateInfo` now emits the same inactive payload. |
| Warmup payload | Retail qagame publishes `time`, `round`, `turn`, and `state=1`. | A/D warmup now publishes only those fields, using `level.roundTransitionTime`, `level.roundNumber`, and `level.adTurnIndex`. |
| Active payload | Retail qagame publishes `\turn\%d\state\2` and separately writes the active round start to slot `0x296`. | A/D active now emits the compact turn/state payload and preserves the hidden round-start side channel. |
| Complete payload | Retail qagame clears slot `0x296` to `-1` and leaves the previous active turn/state payload visible while transition delay runs. | A/D complete/exit now clear the round-start side channel and publish the completed turn with `state=2`, matching the retained retail client view. |
| cgame parser | Retail clients must tolerate sparse round payloads where A/D active omits `time` and `round`. | `CG_ParseMatchState` now treats A/D as a sparse round payload, preserves previous round fields when keys are absent, and re-parses `CS_ROUND_START_TIME` after resetting cached fields. |
| Score history | Retail qagame sends `scores_ad` with 20 history entries plus red/blue totals. | Existing `G_ADResetScoreHistory`, `G_ADUpdateScoreHistory`, `CG_ParseADScores`, and `CG_DrawADRoundScoreboard` mappings were revalidated. |
| Objective routing | Retail A/D uses CTF flag status, flag map warnings, team spawn points, offensive flag touch bonuses, and defender awards. | Existing A/D objective, damage bonus, flag touch, POI, and spawn routes remain aligned with the promoted retail owners. |
| HUD and feeders | Retail cgame shares CTF-family team-list/stat feeders and adds A/D round-panel and attack/defend banners. | Existing cgame HUD, feeder, owned-objective, POI, and match-end wiring was revalidated against symbol-map and HLIL evidence. |

## Source Reconstruction

- Added `G_BuildAttackDefendMatchStateInfo` and
  `G_AttackDefendPublishedTurn` in `src/code/game/g_match_state.c`.
- Changed `G_UpdateMatchStateConfigString` so A/D uses the compact retail
  configstring `0x295` payload instead of the richer SRP match-state payload.
- Changed `G_UpdateRoundStartConfigString` so A/D complete and exit states
  clear `CS_ROUND_START_TIME` to `-1`, matching retail slot `0x296`.
- Added `CG_UsesSparseRoundPayload` in `src/code/cgame/cg_servercmds.c`.
- Changed `CG_ParseMatchState` to preserve previous `time`, `round`, `turn`,
  and `state` values for sparse round payloads and to re-read
  `CS_ROUND_START_TIME` after clearing cached fields.
- Strengthened the AD, match-state, and helper-seam parity tests to pin the
  compact payloads, side-channel clear, `scores_ad` evidence, and sparse cgame
  parser behavior.

## Open Questions

- This pass did not fully rename every retail helper below the A/D award tail.
  The controller, objective, score-history, and HUD surfaces are mapped, but
  some lower award helpers remain inherited from earlier CA/Freeze/A/D work.
- The complete/exit `0x295` source publisher writes the retained active
  turn/state payload explicitly. Retail appears to leave the slot unchanged;
  publishing the same visible value keeps the client contract aligned while
  fitting the current source-side centralized configstring updater.
- Freeze and Red Rover still carry related compact-payload behavior in the
  qagame corpus. The cgame sparse/compact parsing change supports them, but
  this pass reconstructs qagame publishing only for A/D.

## Parity Estimate

Focused Attack and Defend qagame/cgame round-state, configstring, score-history,
objective, HUD, and feeder wiring moves approximately **92% -> 98%**. The
remaining gap is mostly confidence around the lower award tail and exact
unchanged-slot semantics during the complete-to-warmup delay. Broader
gametype/source parity remains approximately **99%**.
