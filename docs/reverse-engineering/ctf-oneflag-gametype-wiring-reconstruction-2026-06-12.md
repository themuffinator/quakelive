# Capture The Flag And One Flag Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked Capture the Flag and One Flag CTF across the retail
qagame, cgame, shared bg item rules, bot goal state, local command surface, and
legacy trigger wiring. The goal was to confirm that the reconstructed source
keeps red/blue CTF flags and the One Flag neutral objective separate all the
way from server item touches through cgame HUD/status parsing.

## Primary Evidence

- Retail qagame HLIL and symbol map:
  - `0x10068770 -> Team_SetFlagStatus`
  - `0x10068930 -> Team_CheckDroppedItem`
  - `0x100692B0 -> Team_ReturnFlagIfMissing`
  - `0x10069380 -> Team_ResetFlag`
  - `0x100695B0 -> Team_ReturnFlag`
  - `0x10069780 -> Team_DroppedFlagThink`
  - `0x10069800 -> Team_TouchOurFlag`
  - `0x10069E30 -> Team_TouchEnemyFlag`
  - `0x1006A040 -> Pickup_Team`
  - `0x1006BDA0 -> G_DroppedPowerupTouchCaptureZone`
  - `0x10046F80 -> CheckAlmostCapture`
  - `0x1003E6D0 -> G_BuildCTFStyleScoreboardMessage`
  - `0x1003EC40 -> G_SendCTFStatsMessage`
- Retail cgame HLIL and symbol map:
  - `0x10001000 -> CG_IsRedBlueFlagItem`
  - `0x100076B0 -> CG_DropFlag_f`
  - `0x10030A80 -> CG_DrawTeamFlagOrBaseStatus`
  - `0x10030FF0 -> CG_OneFlagStatus`
  - `0x100316B0 -> CG_OtherTeamHasFlag`
  - `0x10031720 -> CG_YourTeamHasFlag`
  - `0x10031CD0 -> CG_DrawPlayerHasFlag`
  - `0x10046BF0 -> CG_ParseCtfScores`
  - `0x10047400 -> CG_ParseCTFStats`
  - `0x10049420 -> CG_SetConfigValues`
  - `0x10049980 -> CG_ConfigStringModified`
- Shared source evidence:
  - `bg_misc.c::BG_CanItemBeGrabbed` preserves CTF red/blue flag ownership,
    dropped own-flag recovery, One Flag neutral pickup, and enemy-base capture
    rules.
  - `g_combat.c::TossClientItems` and the nodrop death path route
    `PW_NEUTRALFLAG`, `PW_REDFLAG`, and `PW_BLUEFLAG` through `G_TossFlag`.
  - `g_active.c`, `g_misc.c::PortalTouch`, and
    `g_target.c::Use_target_remove_powerups` all use the same flag drop/return
    helper path instead of duplicating flag state changes.

## Retail Wiring Map

| Area | Retail behavior | Reconstructed source state |
| --- | --- | --- |
| Flag status publication | CTF stores red/blue status in `CS_FLAGSTATUS` using `0/1/*/*/2`; One Flag stores a single neutral status using `0/1/2/3/4`. | `Team_SetFlagStatus` keeps `ctfFlagStatusRemap` and `oneFlagStatusRemap`, then cgame parses the compact status with `CG_ParseFlagStatusConfigString`. |
| Team item pickup dispatch | CTF routes own flag touches to return/capture and enemy flag touches to pickup. One Flag routes neutral flag touches to pickup and enemy-base red/blue flag touches to capture. | `Pickup_Team`, `Team_TouchEnemyFlag`, and `Team_TouchOurFlag` preserve that split, including `FLAG_TAKEN_RED` / `FLAG_TAKEN_BLUE` for neutral carriers. |
| Flag drop and forced return | Death, nodrop, teleport/scripted drops, portals, and target_remove_powerups all clear carried flags through the same red/blue/neutral helper path. | `G_TossFlag` owns carried flag removal, drop metadata, status publication, and forced return. `TossClientItems`, `player_die`, `ClientEvents`, `PortalTouch`, and `Use_target_remove_powerups` all call it. |
| Missing CTF flag sanity | Retail only runs the missing-flag sanity scan in the `GT_CTF` frame branch, returning a flag only when neither a visible/dropped world entity nor a live enemy carrier exists. | `G_RunFrameGametypeHooks` calls `Team_ReturnFlagIfMissing( TEAM_RED/TEAM_BLUE )` only for `GT_CTF`. |
| Near-capture award | Retail checks carried CTF/One Flag state, selects the correct red/blue base classname, skips dropped/hidden flag entities, and toggles the holyshit event within 200 units. | `CheckAlmostCapture` matches the GT_CTF versus One Flag base selection and records the holyshit count on carrier/attacker. |
| Client prediction | Retail cgame suppresses predictable pickup for red/blue CTF flags via a narrow flag-item predicate, while One Flag only predicts neutral-flag pickup. | `CG_TouchItem` keeps the One Flag neutral-only branch and the CTF red/blue same-team suppression through `BG_IsRedBlueFlagItem`. |
| HUD and visibility | Retail CTF consumes red/blue status, while One Flag consumes `cgs.flagStatus` and keeps red-carrier and blue-carrier neutral states distinct. | `CG_SetConfigValues`, `CG_ConfigStringModified`, `CG_OneFlagStatus`, `CG_DrawTeamFlagOrBaseStatus`, `CG_OtherTeamHasFlag`, and `CG_YourTeamHasFlag` preserve the split. |
| Scoreboard transport | Retail CTF-family modes share `scores_ctf` and intermission `ctfstats`. | `DeathmatchScoreboardMessage`, `G_BuildCTFStyleScoreboardMessage`, `G_SendCTFStatsMessage`, `CG_ParseCtfScores`, `CG_ParseCTFStats`, and the cgame CTF-family feeders cover CTF and One Flag. |
| Bot goals and orders | Retail bot AI tracks CTF red/blue flag inventories separately from One Flag neutral flag inventory and dispatches distinct CTF/1FCTF team orders. | `BotCTFCarryingFlag`, `Bot1FCTFCarryingFlag`, `BotCTFOrders`, `Bot1FCTFOrders`, `BotTeamGoals`, and setup warnings all preserve that split. |
| Legacy capturezone bridge | Retail retains a `trigger_capturezone` bridge that resolves a red/blue base flag and routes into `Team_TouchOurFlag`. | The symbol map records `G_DroppedPowerupTouchCaptureZone`; no source rewrite was needed in this pass. |

## Source Reconstruction

- Added `CG_ParseFlagStatusConfigString` in `cg_servercmds.c` so initial
  configstring bootstrap and live `CS_FLAGSTATUS` updates share the same
  compact CTF/One Flag parser.
- Corrected and filled the qagame function headers around the flag-status,
  reset, return, pickup-status, and touch handlers in `g_team.c`; this keeps
  the reconstructed source names aligned with the promoted retail owners.
- Strengthened `tests/test_ctf_oneflag_retail_parity.py` to cover flag
  drop/forced-return paths, cgame prediction suppression, local `dropflag`
  forwarding, and the shared flag-status parser.
- Updated qagame and cgame symbol-map comments for the compact status remaps,
  One Flag neutral carrier statuses, legacy capturezone routing, and CTF-family
  score transport ownership.

## Notes And Open Questions

- `Team_DroppedFlagThink` is still intentionally documented as not fully exact:
  the current source has a newer neutral-flag ping scheduling branch layered on
  top of the compact retail timeout/reset body. This pass did not remove it
  because that branch needs its own focused evidence pass against factory/cvar
  behavior.
- The legacy `trigger_capturezone` path is mapped but not source-expanded here;
  current gameplay routes through item touch and `Team_TouchOurFlag`.
- Runtime launch was not needed. The mapping was resolved from committed HLIL,
  Ghidra decompile snippets, symbol maps, and targeted static parity tests.

## Parity Estimate

- Focused CTF/One Flag gametype and wiring parity: **97% -> 98%**.
- Broader gameplay/gametype parity remains **99%**. Remaining uncertainty is
  mainly the dropped neutral-flag ping/timer extension and live visual
  confirmation of the objective-status strip, not the server/client transport
  contract.
