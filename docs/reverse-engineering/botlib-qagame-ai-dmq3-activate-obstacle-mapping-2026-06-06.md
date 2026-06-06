# Botlib Qagame AI DMQ3 Activate/Obstacle Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_dmq3.c` activate-goal stack, obstacle
prediction bridge, console-message scanner, event/snapshot sweep, and
alternate-route setup helpers. The owning retail binary is `qagamex86.dll`;
the mapped range is `0x1001BCD0..0x1001EE30`.

No C behavior was changed in this pass. The source bodies already matched the
retail evidence closely enough for this slice; the reconstruction work was to
promote the remaining names and add parity guards that bind source, HLIL,
Ghidra sizes, symbol-map signatures, and botlib import wiring together.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_dmq3.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_dmq3_activate_obstacle_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x1001BCD0` | `BotFuncButtonActivateGoal` | 2257 |
| `0x1001C5B0` | `BotFuncDoorActivateGoal` | 364 |
| `0x1001C720` | `BotTriggerMultipleActivateGoal` | 531 |
| `0x1001C940` | `BotPopFromActivateGoalStack` | 151 |
| `0x1001C9E0` | `BotPushOntoActivateGoalStack` | 463 |
| `0x1001CBB0` | `BotClearActivateGoalStack` | 166 |
| `0x1001CC60` | `BotEnableActivateGoalAreas` | 88 |
| `0x1001CCC0` | `BotIsGoingToActivateEntity` | 110 |
| `0x1001CD40` | `BotGetActivateGoal` | 2422 |
| `0x1001D6D0` | `BotGoForActivateGoal` | 310 |
| `0x1001D810` | `BotRandomMove` | 323 |
| `0x1001D960` | `BotAIBlocked` | 897 |
| `0x1001DCF0` | `BotAIPredictObstacles` | 434 |
| `0x1001DEB0` | `BotCheckConsoleMessages` | 1357 |
| `0x1001E400` | `BotCheckForProxMines` | 183 |
| `0x1001E4C0` | `BotCheckEvents` | 1421 |
| `0x1001EAF0` | `BotCheckSnapshot` | 446 |
| `0x1001ECB0` | `BotAlternateRoute` | 123 |
| `0x1001ED30` | `BotGetAlternateRouteGoal` | 245 |
| `0x1001EE30` | `BotSetupAlternativeRouteGoals` | 541 |

`BotCheckConsoleMessages`, `BotAlternateRoute`, `BotGetAlternateRouteGoal`,
and `BotSetupAlternativeRouteGoals` now have both `FUN_...` and `sub_...`
aliases in `references/analysis/quakelive_symbol_aliases.json`. The other
rows in this band were already promoted and are now guarded as a contiguous
evidence slice.

## Source Mapping Notes

Observed source anchors now pinned by tests:

- The activate-goal builders preserve BSP model epair lookup, mover and
  trigger bounds resolution through `BotModelMinsMaxs`, crouch presence bbox
  probes, trace-area reachability scans, door/button shoot target setup, and
  trigger goal area selection.
- The activate stack preserves pop/push/clear behavior, routing-area disable
  toggles through `trap_AAS_EnableRoutingArea`, recent-use gating, and the
  `MAX_ACTIVATESTACK` heap scan used to recycle entries.
- `BotGetActivateGoal` preserves the scan over BSP entities and the
  `func_door`, `func_button`, `trigger_multiple`, `func_timer`,
  `target_relay`, and `target_delay` target chain used to discover a bot
  activation goal for a blocking model.
- `BotAIBlocked` and `BotAIPredictObstacles` preserve the random escape move,
  activate-goal handoff, sidestep fallback, six-second goal-area obstacle
  throttle, `trap_AAS_PredictRoute` call, mover-content model extraction, and
  `BotGoForActivateGoal` bridge.
- `BotCheckConsoleMessages` preserves console-message polling, flood-speed
  handling, chat match extraction, synonym replacement, reply-chat testing,
  bot-self filtering, reply probability, and stand-node handoff after a
  successful reply.
- `BotCheckEvents` and `BotCheckSnapshot` preserve obituary bookkeeping, CTF
  and 1FCTF flag status updates, kamikaze and powerup respawn reactions,
  falling-teleporter use, grenade/prox-mine avoidance, kamikaze-body tracking,
  and player-state external event copying.
- `BotAlternateRoute`, `BotGetAlternateRouteGoal`, and
  `BotSetupAlternativeRouteGoals` preserve alternate route reach detection,
  random red/blue route goal selection, CTF/1FCTF/obelisk/harvester setup, and
  `trap_AAS_AlternativeRouteGoals` population for both teams.

Inferred meaning: this band is the bridge between low-level botlib navigation
services and the qagame AI state machine when movement is blocked or when team
objective routes need alternate pathing. Confidence is high because the same
function identities are supported by symbol-map signatures, Ghidra function
sizes, HLIL call relationships, strings/constants, and source-level wiring.

## Botlib Wiring

The new regression pins the retail import numbers and wrapper paths used by
this band:

- AAS route and BSP helpers: bbox/area info, presence bbox, trace areas, BSP
  epair key readers, area reachability, area travel time, routing-area enable,
  route prediction, and alternate-route goals.
- Bot AI chat and movement helpers: console-message polling/removal, reply
  chat, match parsing, synonym replacement, level item goal lookup,
  `trap_BotMoveInDirection`, and `trap_BotAddAvoidSpot`.
- Server-side direct import-table wiring in `sv_game.c` and VM-compatible
  wrappers in `ql_game_imports.inc`.

## Tests

- `python -m pytest tests/test_botlib_qagame_ai_dmq3_activate_obstacle_parity.py -q --tb=short`

## Parity Estimate

- Focused qagame `ai_dmq3.c` activate/obstacle/alternate-route alias coverage:
  **before 80% -> after 100%** for the mapped `0x1001BCD0..0x1001EE30`
  retail band.
- Focused source-owned activate/obstacle/event parity confidence:
  **before 92% -> after 98%** after pinning source anchors against HLIL and
  symbol-map signatures.
- Focused botlib activation, route, movement, avoid, and chat import wiring
  confidence: **before 91% -> after 98%**.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 96.0% -> after 96.7%**. Remaining uncertainty is concentrated in
  later `ai_dmq3.c` goal/entity setup helpers and broader live behavior
  validation, not in this mapped slice.
