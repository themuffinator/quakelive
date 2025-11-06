# HUD & Menu Asset Audit

## Scope
This audit compares the Quake Live reference snapshot in `references/original-assets/quakelive/baseq3/ui` against the GPL tree under `src/ui`. It captures the state of script coverage, supporting assets, and build integration tasks required to reproduce Quake Live’s HUD and menu presentation inside the open-source build.

## Inventory Snapshot
### Definition Parity
| Category | Reference Count | GPL Count | Notes |
| --- | --- | --- | --- |
| `.menu` / `.txt` definitions | 65 | 65 | Definitions align numerically, but the GPL tree swaps in bootstrap helpers (`credential.menu`, `ingame_quakelive.txt`, `menus_quakelive.txt`) while omitting Quake Live’s `country.txt`, `hud3.txt`, and `teaminfo.txt` tables.
| `menudef.h` | 1 | 1 | The Quake Live enum definitions exist in both trees and remain the canonical owner-draw ID source.
| Accessory config (`hud*.txt`) | 3 | 2 | `hud.txt` and `hud2.txt` are staged, but the legacy `hud3.txt` preset is still absent from the GPL tree.

### GPL-Only Bootstrap Files
The GPL branch introduces the following convenience files to seed the port:
- `credential.menu` powers the Steam authentication prompt.
- `ingame_quakelive.txt` consolidates HUD owner-draw registration for testing.
- `menus_quakelive.txt` bootstraps menu loading order while the asset bundle is incomplete.

These files should remain, but their dependencies must be harmonised with the restored Quake Live assets to avoid diverging behaviour.

## Supporting Assets & Dependencies
| Area | Reference Location | GPL Status | Gap Summary |
| --- | --- | --- | --- |
| HUD & menu art | `ui/assets/{hud,score,menu,flags,main_menu,statusbar}` | Missing | Scoreboard state badges, menu chrome, and national flag textures are unavailable, forcing Quake III fallbacks and stripping visual cues from score widgets and navigation flows.
| Fonts | `baseq3/fonts/*.ttf` | Missing | Droid Sans, Noto Sans, and Handel Gothic TTFs are not staged or baked into atlases, so scripted point sizes fall back to Quake III bitmap fonts.
| Shader scripts | `baseq3/scripts/ui*.shader` (tracked in the global asset audit) | Missing | Gradient, cursor, and overlay materials referenced by menus do not compile without the Quake Live shader definitions.
| Packaging hooks | `pak/ui` structure in the reference PK3s | Missing | No reproducible PK3 exists in the GPL build to bundle menus, art, fonts, and shaders for distribution.

## Parity Gaps & Recommended Actions
| Area | Gap | Action |
| --- | --- | --- |
| Locale & team metadata | `country.txt` and `teaminfo.txt` remain exclusive to the reference snapshot, blocking country pickers and spectator team callouts. | Import both tables, validate UTF-8 encoding, and confirm dropdown population inside `ingame_join.menu` and scoreboard panels.
| Legacy HUD preset | `hud3.txt` is missing, preventing the legacy HUD preset from appearing in configuration utilities. | Stage `hud3.txt`, add it to the HUD selector list, and test preset rotation to ensure bindings persist.
| HUD/menu art | Quake Live’s art hierarchy is absent, so gradients, scoreboxes, and iconography degrade to Quake III defaults. | Stage `ui/assets/*` inside a dedicated PK3 (e.g., `pak_uiql.pk3`), then repoint menu scripts to the restored textures.
| Fonts & readability | The Quake Live TTFs are not baked, causing inconsistent typography and reduced legibility at scripted sizes. | Add a font-bake step that emits `fonts/font`, `fonts/smallfont`, and `fonts/bigfont` atlases before packaging.
| Shader/material coverage | UI shader scripts are missing, leading to placeholder gradients and cursors. | Import the `ui*.shader` definitions alongside the art bundle and trigger shader cache regeneration in the build pipeline.
| Build integration | There is no automated packaging flow for HUD assets. | Extend the data build to archive menus, art, fonts, and shaders into reproducible PK3s and document the process in the scripting guide.

## Follow-Up Validation Checklist
- [ ] Confirm all menu and metadata files referenced by Quake Live scripts exist in `src/ui` with identical casing.
- [ ] Verify that UI art directories resolve in-game by launching with a clean homepath and inspecting HUD, scoreboard, and menu screens.
- [ ] Run font bake tooling and compare generated atlas metrics against Quake Live defaults to ensure `textscale` directives remain accurate.
- [ ] Recompile shader caches with the imported `ui*.shader` files and validate gradients/cursors in the renderer.
- [ ] Exercise the packaging workflow to ensure PK3 generation is deterministic and platform-agnostic.

## Accessibility Backlog (Prioritised)
| Priority | Task | Rationale | Dependencies |
| --- | --- | --- | --- |
| P0 | Restore color-differentiated scoreboxes with redundant numeric/text cues. | Missing score textures eliminate dual-encoded feedback for colorblind users; reinstating art plus numeric overlays restores accessibility. | Requires `ui/assets/score` bundle.
| P0 | Reinstate locale-aware country/team dropdowns. | Dropdowns currently render empty states without `country.txt`/`teaminfo.txt`, blocking text-based identification. | Requires metadata import.
| P1 | Add textual overlays to spectator ink-fade panels. | Spectator HUD relies solely on texture gradients; adding captions/tooltips aids screen readers and low-vision players. | Depends on art bundle import for final layout.
| P1 | Document accessible font scaling expectations in `assetGlobalDef`. | Contributors need guidance to maintain legible `textscale` and contrast when swapping fonts. | Requires font bake workflow.
| P2 | Provide high-contrast cursor and highlight variants. | Cursor gradients lose contrast on bright backgrounds; shipping alternative themes allows users to select readable options. | Requires shader + art packaging.
| P2 | Automate checks for owner-draw visibility flags that gate accessibility cues. | Prevents regressions where visibility flags strip textual fallback elements in competitive HUDs. | Needs scripting QA harness.
