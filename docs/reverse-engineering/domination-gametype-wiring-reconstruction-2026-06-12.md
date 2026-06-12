# Domination Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Domination (`GT_DOMINATION`) path across qagame point
entities, capture triggers, linked point respawns, per-frame capture and score
updates, owned-point configstrings, qagame-to-cgame point state, cgame point
HUD, announcer/event presentation, owned-count ownerdraws, and shared
CTF-family scoreboard feeders. The concrete reconstruction outcome is a
high-confidence wiring map plus parity tests that pin the already-recovered
source implementation to retail HLIL/Ghidra evidence.

## Evidence Used

- qagame Binary Ninja HLIL:
  - `0x10038B60` selects Domination respawns by scanning `team_dom_point`
    owners, collecting linked `info_player_deathmatch` nodes, limiting point
    spawn candidates to `0x19`, and ranking them against enemy players.
  - `0x1004AA80` awards Domination capture and assist credit, using `25` for
    `CAPTURE` and `15` for `ASSIST`.
  - `0x1004ABF0` stabilizes the primary-capturer pointer for the point capture
    controller.
  - `0x1004B720` is the delayed point activation leaf that traces the point to
    the floor and links the live entity.
  - `0x1004B900` recounts red-owned and blue-owned points and publishes them
    through configstrings `0x2BC` and `0x2BD`.
  - `0x1004B980` awards the Domination defense bonus within the 500-unit/PVS
    protection envelope of an owned point.
  - `0x1004BB10` is `SP_team_dom_point`; it frees the entity outside
    `GT_DOMINATION`, initializes the ET_TEAM metadata path when active, queues
    the activation think, and stores up to five point entities.
- qagame Ghidra `decompile_top_functions.c`:
  - The frame hook includes `case 10: FUN_1004b900();`, matching the late-frame
    owned-count refresh for Domination.
  - The entity spawn dispatcher registers `team_dom_point` and
    `trigger_capturezone` ownership paths.
- qagame symbol map:
  - Promoted Domination owners include `Team_SelectDominationSpawnPoint`,
    `G_DominationRewardCaptureParticipants`,
    `G_DominationSelectPrimaryCapturer`, `G_DominationPointActivate`,
    `G_UpdateDominationPointCountConfigstrings`, and
    `G_DominationCheckDefenseBonus`.
- cgame evidence:
  - The symbol map pins `CG_DominationPointLabel`,
    `CG_DrawDominationPointStatus`, `CG_QueueDominationPointBillboard`, and
    `CG_DrawDominationOwnedFlags`.
  - Shared CTF-family team-list/stat feeders explicitly cover
    `GT_DOMINATION`, and the objective strip/match-end condition paths include
    Domination branches.

## Observed Wiring

| Surface | Retail-backed mapping | Source state after this pass |
| --- | --- | --- |
| Gametype id | Retail raw gametype `10` owns Domination point entities, capture triggers, point respawns, owned-count configstrings, and score-limit end conditions. | Existing enum, factories, map entity gates, scoreboards, HUD, and cgame ownerdraws route through `GT_DOMINATION`. |
| Point entity spawn | `SP_team_dom_point` frees outside Domination, initializes ET_TEAM-style network fields, queues delayed activation, and stores at most five points. | `SP_team_dom_point` matches the non-Dom free path, point registration, ET_TEAM state, activation think, and five-point cap. |
| Point activation | Retail activation traces down from the point, retries from a raised fallback probe, settles origin, links the entity, then arms point thinking. | `G_DominationPointActivate` preserves the trace/fallback/link path and rebuilds linked point spawns after settlement. |
| Linked point respawns | Retail scans owned `team_dom_point` entities and their `info_player_deathmatch` targets, capped at 25 spawn candidates per point, before ranked selection. | `Team_DominationBuildSpawnList`, `Team_SelectDominationSpawnPoint`, and `G_SelectClientSpawnPoint` now have explicit parity tests against this path. |
| Capture trigger | Retail `trigger_capturezone` binds to point metadata and drives occupant/participant accumulation. | `Team_RegisterDominationTrigger` and `Team_DominationPointTouch` preserve the metadata binding and participant capture lists. |
| Capture controller | Retail handles contested capture, neutralization, capture progress, primary capturer stability, and point event publication in the `0x1004ACE0` family. | `Team_DominationUpdatePointState` and helpers already reconstruct the capture progression and event/publication surfaces. |
| Capture rewards | Retail grants `CAPTURE` to the primary capturer and `ASSIST` to other participants, with 25/15 scores and the preserved award eFlags. | `G_DominationRewardCaptureParticipants` is pinned by HLIL constants, medal strings, and static tests. |
| Defense bonus | Retail reaches the Domination defense helper from `Team_FragBonuses`, requiring owned point team, 500-unit radius, and PVS. | `G_DominationCheckDefenseBonus` and the `Team_FragBonuses` route are covered by focused parity tests. |
| Per-frame capture/scoring | Retail advances capture state in the active frame path and periodically awards team score by owned point count. | `G_RunFrame` calls `Team_RunDomination` before finishing client frames when not paused; `Team_RunDomination` updates points and awards red/blue score ticks. |
| Owned-point counts | Retail writes red and blue owned counts into configstrings `0x2BC` and `0x2BD`. | `G_UpdateDominationPointCountConfigstrings` writes `CS_RACE_SCORES` and `CS_RACE_INFO`; cgame reads `CS_RACE_STATUS`/`CS_RACE_INFO` into `dominationOwnedPointCount`. |
| Capture-time transport | Retail uses configstring `0x2A5` for a numeric Domination mode side channel. | `G_UpdateDominationCaptureTimeConfigstring` publishes `g_domCapTime` to `CS_DOMINATION_CAPTURE_TIME`; cgame has the matching shared slot constant. |
| Cgame presentation | Retail cgame labels points, draws the point-status strip, queues world billboards, shows owned point counts, and shares CTF-family scoreboard rows. | Existing cgame source and tests preserve point labels/status, owned flags, announcements, billboard media, match-end text, and shared feeders. |

## Source Reconstruction

- No risky gameplay-code rewrite was needed in this round. The current source
  already contains the recovered Domination entity lifecycle, trigger binding,
  linked point respawn selection, capture controller, reward fan-out, defense
  bonus, periodic score award, and owned-count configstring bridge.
- Strengthened `tests/test_game_domination_parity.py` so it now pins:
  - the non-Domination free path and ET_TEAM metadata initialization in
    `SP_team_dom_point`;
  - delayed point activation evidence at `0x1004B720`/`0x1004BB10`;
  - retail linked spawn selection evidence at `0x10038B60`;
  - active-team Domination respawn routing in `G_SelectClientSpawnPoint`;
  - per-frame `Team_RunDomination` score updates;
  - owned-count publication through `CS_RACE_SCORES`/`CS_RACE_INFO` and cgame
    parsing through `CS_RACE_STATUS`/`CS_RACE_INFO`.
- Strengthened `tests/test_game_runframe_parity.py` so the generic runframe
  parity gate also asserts that `Team_RunDomination()` remains in the active
  non-timeout frame path before client-frame finishing.

## Verification

- `python -m pytest tests/test_game_domination_parity.py tests/test_cgame_domination_count_parity.py tests/test_game_runframe_parity.py`
  - `12 passed`

No runtime launch was needed; this was a static evidence and regression-gate
pass over committed HLIL/Ghidra/source/test artifacts.

## Open Questions

- The capture controller body is high-confidence through HLIL constants, point
  state fields, and existing tests, but a future single-function decompilation
  cleanup could still tighten exact field names inside the point metadata slab.
- Cgame objective-strip graphics for the shared `CG_FLAG_STATUS` ownerdraw are
  documented elsewhere as partially reconstructed. Domination is included in
  that ownerdraw family, but this pass did not attempt to finish the full strip
  art/layout path.
- The `0x2A5` side channel is now named for Domination capture time in source.
  Retail cgame also reuses the numeric slot in a damage-through probe helper;
  current comments preserve that ambiguity pending a broader configstring-slot
  audit.

## Parity Estimate

Focused Domination qagame/cgame point entity, trigger, respawn, capture,
reward, defense, scoring, configstring, HUD, and feeder wiring moves
approximately **95% -> 98%**. The remaining gap is mostly exact naming inside
the point metadata slab and the broader shared objective-strip presentation
tail. Broader repo-wide parity remains approximately **99%**.
