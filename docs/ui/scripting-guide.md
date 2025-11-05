# HUD/Menu Scripting Guide

## Purpose
This guide documents how to stage Quake Live HUD and menu assets inside the GPL tree, automate regeneration, and uphold accessibility guarantees while iterating on scripts.

## Updated Asset Workflow
1. **Sync menu & metadata files.** Mirror every `.menu`/`.txt` definition from `references/original-assets/quakelive/baseq3/ui` so the GPL tree retains Quake Live’s locale tables, HUD presets, and configuration flows alongside new staging helpers such as `ingame_quakelive.txt` and `menus_quakelive.txt`. Use the diff in the HUD audit to track stragglers (`country.txt`, `hud3.txt`, `teaminfo.txt`).【f8903d†L3-L8】
2. **Stage UI art packages.** Copy the `ui/assets` subdirectories (`hud`, `score`, `menu`, `flags`, `main_menu`, `statusbar`) into a dedicated build asset bundle so scripted backgrounds, cursors, and gradients resolve without falling back to Quake III art.【c79cbb†L3-L9】
3. **Bake Quake Live fonts.** Import the Droid Sans/Noto Sans/Handel Gothic TTFs and generate the `fonts/font`, `fonts/smallfont`, and `fonts/bigfont` atlases referenced by `assetGlobalDef` blocks, keeping the scripted point sizes intact.【60b9f9†L1-L5】【77ce0a†L9-L22】
4. **Include shader/material scripts.** Copy the Quake Live `ui*.shader` files and related material definitions flagged by the global asset audit so menu gradients and ink overlays compile correctly during render init.【273dcd†L5-L28】
5. **Package consistently.** Follow the packaging flow captured in the global asset audit to archive menus, art, fonts, shaders, and configuration defaults into reproducible PK3s that the engine loads at startup.【273dcd†L21-L37】

## Automation Tips
- **Script the copy pipeline.** Capture the file sync, font generation, and packaging commands inside a reproducible Bash/PowerShell script so HUD updates can be rebuilt across platforms without manual effort.【273dcd†L23-L28】
- **Validate ownership flags.** Run automated checks that parse menu files to confirm `ownerdrawflag` and `showCvar` directives reference supported enums before distributing updated PK3s, preventing runtime HUD failures.【143912†L53-L124】
- **Smoke-test packaging.** Launch the game with a clean homepath after each rebuild to ensure the packaged menus, fonts, and shaders load without falling back to Quake III defaults.【273dcd†L23-L37】

## Scripting Conventions
- **Use Quake Live owner-draw IDs and flags.** HUD scripts depend on enums such as `CG_SHOW_IF_RED_IS_FIRST_PLACE`, `CG_SHOW_ANYTEAMGAME`, and `CG_RED_SCORE` defined in `menudef.h`; keep scripts aligned with these identifiers when introducing new widgets.【143912†L53-L132】
- **Respect widescreen layout directives.** Competitive HUDs anchor elements with `widescreen WIDESCREEN_RIGHT/LEFT/CENTER` and rely on consistent rectangles for scaling; retain or extend these directives when reshaping panels.【77ce0a†L23-L93】【ba2fd2†L31-L83】
- **Centralise shared assets via `assetGlobalDef`.** Update cursor, gradient, and font references inside the global asset block so theme swaps and accessibility tweaks remain declarative.【77ce0a†L9-L33】【ba2fd2†L7-L23】
- **Isolate gametype logic with `ownerdrawflag`.** Leverage flags such as `CG_SHOW_ANYTEAMGAME`, `CG_SHOW_IF_PLYR_IS_FIRST_PLACE`, and `CG_SHOW_IF_BLUE_IS_FIRST_PLACE` to handle state permutations without hard-coding branching logic in C, keeping HUD behaviour data-driven.【77ce0a†L35-L91】

## Accessibility Guardrails
- **Provide dual-encoded feedback.** Preserve combinations of color fills and numeric/textual owner-draws for score widgets so colorblind users retain redundant cues when art assets are refreshed.【77ce0a†L27-L93】
- **Expose spectator state transitions.** Spectator HUD elements should pair ink-fade textures with text overlays indicating placement, timers, or overtime state to aid screen readers and low-vision players.【ba2fd2†L35-L87】
- **Match typography to scripts.** Ensure regenerated fonts honour the scripted `textscale` values across HUD menus to maintain legibility at tournament resolutions.【77ce0a†L17-L60】
- **Document asset swaps.** When replacing cursors or gradients in `assetGlobalDef`, log the rationale and contrast checks so reviewers can verify the changes preserve accessibility expectations before landing.【77ce0a†L9-L33】

## Review Checklist
- [ ] All referenced asset paths exist in the packaged PK3 and match case-sensitive expectations across platforms.【c79cbb†L3-L9】【273dcd†L21-L37】
- [ ] Menu scripts compile without missing owner-draw IDs or shader references, and automation verifies enum usage before distribution.【143912†L53-L132】
- [ ] Accessibility cues (color tint + text, readable fonts, conditional visibility) remain intact after modifications.【77ce0a†L27-L93】【ba2fd2†L35-L87】
- [ ] Regeneration scripts reproduce fonts and asset bundles so future contributors can rebuild the HUD package on demand.【273dcd†L23-L37】
