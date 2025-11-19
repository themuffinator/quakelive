# Follow-up Issues for Quake Live UI Parity

## Issue: Port Quake Live HUD and scoreboards
- **Problem**: The active HUD uses Quake III definitions and the legacy `cg_scoreboard.c` renderer, so none of the Quake Live scoreboxes, round timers, or overtime cues appear.【F:src/ui/hud.txt†L1-L7】【F:src/code/cgame/cg_scoreboard.c†L266-L352】
- **Scope**: Introduce the Quake Live HUD menus (`comp_hud.menu`, `hud3.menu`, and gametype-specific end scoreboards), add missing owner-draw enums, and update cgame drawing code to populate the new widgets.【F:assets/quakelive/baseq3/ui/comp_hud.menu†L24-L118】【F:src/ui/menudef.h†L137-L212】
- **Assets**: Requires registering the score shaders found under `assets/quakelive/baseq3/ui/assets/score/` (e.g., `scorebox_spec.tga`, `ink_fade_left.tga`).【F:assets/quakelive/baseq3/ui/comp_hud.menu†L32-L92】
- **Notes**: Capture before/after screenshots once the HUD renders correctly to validate widescreen alignment.

## Issue: Implement spectator follow overlays
- **Problem**: Spectator HUD logic still exposes Quake III team-order features instead of Quake Live’s dual-player follow view, and the required owner-draw IDs are undefined.【F:src/code/cgame/cg_newdraw.c†L41-L104】【F:src/ui/menudef.h†L137-L212】
- **Scope**: Port `comp_spectator.menu` and `comp_spectator_follow.menu`, implement drawing paths for `CG_HEALTH_COLORIZED`, `CG_1ST_PLYR_*`, and follow-state flags, and wire up spectator input to swap targets as scripted by the menus.【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L24-L308】
- **Assets**: Ensure the follow highlight textures and ink fades referenced by the menus are packaged (`scorebox_follow.tga`, `ink_fade_right.tga`).【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L32-L251】
- **Notes**: Provide captured footage or screenshots demonstrating the follow HUD (first vs. second place cards) once implemented.

## Issue: Align lobby and in-game menus with Quake Live flow
- **Problem**: `menus.txt` and `ingame.txt` still boot the Quake III menu stack, conflicting with Quake Live’s Awesomium-driven front end and streamlined in-game options.【F:src/ui/menus.txt†L1-L39】【F:src/ui/ingame.txt†L1-L16】
- **Scope**: Replace the menu loader lists with Quake Live’s definitions, port `main.menu`/`main_options.menu`, and integrate web overlay hooks (`exec web_showBrowser`, `uiScript stopRefresh`).【F:assets/quakelive/baseq3/ui/menus.txt†L4-L12】【F:assets/quakelive/baseq3/ui/main.menu†L17-L134】
- **Assets**: Reuse the `ui/assets/backscreen_smoke` background and any additional textures referenced by the new menus.【F:assets/quakelive/baseq3/ui/main.menu†L19-L134】
- **Notes**: Document any engine-level work needed to substitute Awesomium calls; include screenshots of the updated main menu flow.

