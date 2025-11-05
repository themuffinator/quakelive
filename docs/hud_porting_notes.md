# Quake Live HUD Porting Notes

## Widescreen and Timer Enhancements
- **Widescreen scoreboxes** are rendered by `CG_DrawScoreboard`, which uses the `SB_*` layout helpers and `CG_DrawPic`. The scoreboard shaders (`cgs.media.scoreboard*`) are registered in `CG_RegisterGraphics`, and the on-screen positions are scaled through `CG_AdjustFrom640` to stay centered on widescreen resolutions.
- **Overtime announcer states** depend on `cg.timelimitWarnings` and the logic inside `CG_CheckPlayerstateEvents`. The sudden-death announcer sounds are registered alongside other announcer media in `CG_RegisterSounds`.
- **Power-up/status timers** are handled by `CG_DrawStatusBarHeadTimer` (classic) and `CG_DrawStatusBarHeadTimerMP` (missionpack). They sort active items, draw icons, and place countdown numbers, reusing the missionpack HUD logic for spectator overlays and scripted HUD menus.

## Owner-Draw Expansion Requirements
- The classic UI currently defines owner-draw IDs only through `CG_CAPTURES` (69), with rendering handled in `cg_newdraw.c` via helpers like `CG_DrawRedScore` and `CG_DrawBlueScore` that only expose base scores.
- Quake Live HUD scripts reference extended owner-draw IDs such as `CG_1ST_PLACE_SCORE` (84), `CG_RED_SCORE` (284), and `CG_BLUE_SCORE` (312). The listboxes expect detailed columns (SCORE, K/D, DMG, WEAP, TIME, PING) that `CG_DrawScoreboard` and its data structures do not yet supply.
- Supporting these widgets will require expanding the owner-draw enum in `src/ui/menudef.h`, adding render handlers in `cg_newdraw.c`, and enriching the scoreboard data in `cg_scoreboard.c` so the listbox feeders can surface the extra statistics.

## Spectator Overlay Replacement Tasks
- Replace the legacy `CG_DrawTeamSpectators` marquee by exposing two tracked clients (primary/secondary) that feed the dual-player follow overlay defined in `ui/comp_spectator_follow.menu`.
- Extend `menudef.h` with the Quake Live spectator owner-draw IDs (dual player scores, armor tiers, item stacks) and implement matching draw helpers in `cg_newdraw.c`. Update `CG_DrawActive` to dispatch these new cases.
- Hook spectator input transitions in `CG_KeyEvent`/`CG_MouseEvent` so the dual-follow state machine supports menu actions like `nextTeamMember` and `prevTeamMember`.
- Refresh the spectator HUD scripts to drop the legacy marquee, point to the new owner-draw IDs, and align widescreen positioning with the revised renderer.

:::task-stub{title="Adopt the dual-player spectator follow HUD"}
1. Expand `src/ui/menudef.h` with the Quake Live spectator owner-draw IDs (`CG_1ST_PLYR_SCORE`, `CG_2ND_PLYR_SCORE`, tiered armor widgets, etc.) referenced by `ui/comp_spectator_follow.menu` so the scripting system can request the correct draw handlers.
2. Implement the missing draw helpers in `src/code/cgame/cg_newdraw.c` (dual player names, scores, health/armor bars, dual item stacks) and update `CG_DrawActive`’s owner-draw switch to call them.
3. Replace the legacy spectator marquee logic in `CG_DrawTeamSpectators` with routines that pull two tracked clients (primary/secondary) and expose their data for the new owner-draw widgets, matching the layout used by `comp_spectator_follow.menu`.
4. Hook spectator input transitions: update `CG_KeyEvent`/`CG_MouseEvent` to respect the new dual-follow state machine and expose menu actions (`nextTeamMember`, `prevTeamMember`, etc.) needed by the spectator follow menus.
5. Update the Quake Live spectator HUD scripts (e.g., `references/original-assets/quakelive/baseq3/ui/comp_spectator_follow.menu`) to remove legacy marquee elements, point to the new owner-draw IDs, and ensure widescreen positioning lines up with the revised renderer.
:::
