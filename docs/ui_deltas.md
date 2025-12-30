# UI and Gameplay HUD Delta Report

This report compares the repository's current cgame and UI implementations with the Quake Live reverse-engineering references. It highlights visual/behavioral gaps and identifies the updates required to reach feature parity.

## HUD Elements

### Current implementation
- The shipped HUD configuration only loads the legacy Quake III `hud.menu`, `score.menu`, and `teamscore.menu` definitions, offering none of Quake Live's widescreen-aware scoreboxes or round information overlays.【F:src/ui/hud.txt†L1-L7】【F:src/ui/hud2.txt†L1-L7】
- Runtime drawing logic still relies on the pre-Quake Live scoreboard path in `cg_scoreboard.c`, which renders narrow fixed-width columns and omits sudden-death, overtime, and round timer states that Quake Live surfaces in menus.【F:src/code/cgame/cg_scoreboard.c†L266-L352】
- `menudef.h` enumerates owner-draw IDs only up to the Quake III missionpack set (for example `CG_CAPTURES`), so values used by Quake Live such as `CG_ROUNDTIMER`, `CG_OVERTIME`, `CG_1ST_PLYR_HEALTH_ARMOR`, and `CG_HEALTH_COLORIZED` are undefined and cannot be rendered.【F:src/ui/menudef.h†L137-L212】
- Match-state parsing now triggers the overtime announcer cue (`overtime.ogg`) and drives overtime owner-draw visibility off the server-provided overtime flag, matching HLIL cue strings for overtime transitions.【F:src/code/cgame/cg_servercmds.c†L1043-L1150】【F:src/code/cgame/cg_newdraw.c†L3920-L3995】【F:references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt†L23117-L23140】

### Quake Live reference behavior
- `comp_hud.menu` drives first/second place panels, overtime notices, and gametype-aware scoreboxes using new owner-draw IDs and widescreen layout helpers that are absent from the current HUD path.【F:assets/quakelive/baseq3/ui/comp_hud.menu†L24-L118】
- High-level cgame logic references overtime and round-state cvars (`g_overtime`, `g_timeoutCount`, etc.), showing that the Quake Live client integrates match flow concepts that our build does not surface.【F:references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt†L25940-L25985】【F:references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt†L28860-L28904】

### Required updates
- Extend `menudef.h` and the associated owner-draw switch in cgame to cover Quake Live HUD elements (round timer, overtime banner, multi-player health/armor rows, etc.).【F:src/ui/menudef.h†L137-L212】【F:assets/quakelive/baseq3/ui/comp_hud.menu†L24-L118】
- Replace or augment `cg_scoreboard.c` with logic that feeds the menu-driven HUD, including widescreen scaling, per-gametype end-game scoreboards, and sudden-death messaging expected by the Quake Live menus.【F:src/code/cgame/cg_scoreboard.c†L266-L352】【F:assets/quakelive/baseq3/ui/comp_hud.menu†L24-L118】
- Port the Quake Live HUD menu set (`comp_hud.menu`, `hud3.menu`, end-of-game menus) and ensure referenced shaders such as `ui/assets/score/scorebox_spec.tga` and `ui/assets/score/ink_fade_left.tga` are available from the extracted assets.【F:assets/quakelive/baseq3/ui/comp_hud.menu†L32-L92】【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L168-L207】

### HUD gating behavior
- The HUD loader now inspects `cg_hudFiles` scripts for `comp_*.menu` references and records whether the Quake Live competitive HUD assets are available, exposing a fallback via the new `cg_useLegacyHud` cvar for debugging legacy overlays.【F:src/code/cgame/cg_main.c†L1829-L1876】【F:src/code/cgame/cg_main.c†L169-L212】
- `cg_draw.c` short-circuits most legacy drawing calls whenever those competitive menus are active so that owner-draw/menu code remains the single source of HUD elements during gameplay and spectator modes.【F:src/code/cgame/cg_draw.c†L1937-L2005】【F:src/code/cgame/cg_draw.c†L70-L89】

## Spectator Controls and Overlays

### Current implementation
- The Quake III missionpack spectator overlay logic persists in `cg_newdraw.c`, focusing on team orders and voice chats rather than the follow-camera overlays Quake Live expects.【F:src/code/cgame/cg_newdraw.c†L1-L104】
- No owner-draw IDs or menu entries exist for the Quake Live spectator widgets such as follow-state badges, dual-player comparison bars, or health-colorized overlays.【F:src/ui/menudef.h†L137-L212】【F:src/ui/hud.txt†L1-L7】

### Quake Live reference behavior
- `comp_spectator.menu` and `comp_spectator_follow.menu` render detailed HUDs: dual player cards, follow indicators, overtime timers, and conditional gametype banners, all driven through new owner-draw flags (`CG_HEALTH_COLORIZED`, `CG_SHOW_IF_1ST_PLYR_FOLLOWED`, etc.).【F:assets/quakelive/baseq3/ui/comp_spectator.menu†L24-L145】【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L24-L268】
- Spectator menus reference assets for score fades and follow highlights (`ui/assets/score/ink_fade_right.tga`, `ui/assets/score/scorebox_follow.tga`), implying shader/material dependencies that must be registered at runtime.【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L32-L251】

### Required updates
- Introduce the spectator-specific owner-draw definitions and backing cgame draw routines for follow target comparison, player obituaries, and gametype-specific team panels.【F:src/ui/menudef.h†L137-L212】【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L151-L308】
- Port the spectator HUD menus and ensure the renderer registers the referenced scorebox and ink-fade assets from `assets/quakelive/baseq3/ui/assets/score`.【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L32-L251】
- Update spectator input handling to match Quake Live’s follow-state expectations (e.g., next/previous target, camera lock) surfaced by the HLIL strings and menu scripts, replacing the Quake III order system in `cg_newdraw.c`.【F:src/code/cgame/cg_newdraw.c†L41-L104】【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L216-L308】

## Lobby and Menu Flow

### Current implementation
- Startup menus still load the entire Quake III Arena suite (join server, skirmish, mod configuration, etc.), which does not align with Quake Live’s streamlined web-integrated front end.【F:src/ui/menus.txt†L1-L39】
- In-game menu loading includes legacy vote, system, and order menus absent from the Quake Live asset set (e.g., `ingame_orders.menu`).【F:src/ui/ingame.txt†L1-L16】
- The `ui_menuFiles` default previously pointed at `ui/menus_quakelive.txt`, a file that does not ship in this repo, causing every boot to log the fallback path before loading `ui/menus.txt`—the HLIL shows Quake Live defaulting directly to `ui/menus.txt` instead.【F:src/code/ui/ui_main.c†L241-L275】【F:references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt†L11070-L11102】

### Quake Live reference behavior
- Quake Live’s `menus.txt` only loads a minimal stack (default, main, main options, connect, quit, demo, ingame lower-nav, error), delegating server browsing to the embedded web/Awesomium layer and deferring other flows to new menus such as `main.menu` and `main_options.menu`.【F:assets/quakelive/baseq3/ui/menus.txt†L4-L12】
- `main.menu` introduces widescreen backgrounds, scripted transitions, and actions that interact with the browser overlay (e.g., `exec web_showBrowser`), none of which exist in the current legacy menu definitions.【F:assets/quakelive/baseq3/ui/main.menu†L17-L134】
- `ingame.txt` in Quake Live loads admin and vote submenus tailored to the new rulesets, omitting the Quake III “leave” and “orders” menus.【F:assets/quakelive/baseq3/ui/ingame.txt†L1-L12】

### Required updates
- Replace the root menu loader with the Quake Live set (`default.menu`, `main.menu`, `main_options.menu`, etc.) and integrate browser-dependent scripts referenced by the menus.【F:assets/quakelive/baseq3/ui/menus.txt†L4-L12】【F:assets/quakelive/baseq3/ui/main.menu†L17-L134】
- Port the Quake Live in-game submenus and remove Quake III-only flows (orders, mod menu) so the UI surfaces admin, vote, and join controls expected by modern rulesets.【F:src/ui/ingame.txt†L4-L15】【F:assets/quakelive/baseq3/ui/ingame.txt†L1-L12】
- Audit Awesomium/browser integration points needed by menu scripts (`exec web_showBrowser`, `uiScript stopRefresh`) and ensure the client VM exposes equivalent functionality or substitutes.【F:assets/quakelive/baseq3/ui/main.menu†L27-L132】

## Asset dependency summary

| Feature area | Referenced assets/cvars | Notes |
| --- | --- | --- |
| HUD scoreboxes | `ui/assets/score/ink_fade_left.tga`, `ui/assets/score/scorebox_spec.tga`, `ui/assets/score/scorebox_follow.tga` | Required for widescreen score panels and follow highlights.【F:assets/quakelive/baseq3/ui/comp_hud.menu†L32-L92】【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L168-L251】 |
| Timers & overtime | `g_overtime`, `g_timeoutCount`, `overtime.ogg` | Overtime cue audio and HUD state now key off match-state overtime data, aligning with the HLIL string set for overtime transitions.【F:src/code/cgame/cg_servercmds.c†L1043-L1150】【F:src/code/cgame/cg_newdraw.c†L3920-L3995】【F:references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt†L25940-L25985】【F:references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt†L28860-L28904】 |
| Spectator comparison | `CG_HEALTH_COLORIZED`, `CG_1ST_PLYR_SCORE`, `CG_2ND_PLYR_SCORE` owner-draw IDs | Need new drawing code plus menu definitions.【F:assets/quakelive/baseq3/ui/comp_spectator_follow.menu†L216-L308】 |
| Lobby background | `ui/assets/backscreen_smoke` | Used by `main.menu` for animated background; ensure shader registration.【F:assets/quakelive/baseq3/ui/main.menu†L19-L134】 |
