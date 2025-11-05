# HUD & Menu Asset Audit

## Scope
This audit compares the Quake Live reference snapshot in `references/original-assets/quakelive/baseq3/ui` against the GPL tree under `src/ui` to identify the scripts, supporting art, and metadata required for UI parity.【4c71d3†L1-L10】【b8670f†L1-L11】 The counts below only consider menu/HUD definitions and text metadata located at the top level of each tree.

## Inventory Snapshot
### Menu & Metadata Coverage
Both trees contain 65 top-level `.menu`/`.txt` definitions, but the contents diverge: the reference snapshot still provides `country.txt`, `hud3.txt`, and `teaminfo.txt`, while the GPL tree introduces `credential.menu`, `ingame_quakelive.txt`, and `menus_quakelive.txt` to bootstrap the migration.【a0bfed†L1-L3】【0b75f8†L1-L3】【f8903d†L3-L8】 The missing locale/team tables block dropdown population, spectator overlays, and the legacy HUD preset shipped with Quake Live.

### Support Asset Families
- **HUD art packages.** The snapshot retains a nested `ui/assets` hierarchy that supplies HUD chrome, scoreboard overlays, menu chrome, and national flag textures (`hud`, `score`, `menu`, `flags`, `main_menu`, `statusbar`).【c79cbb†L3-L9】 No equivalent directory lives under `src/ui`, so the GPL build currently falls back to Quake III visuals for these references.【4d18d4†L1-L2】
- **Fonts.** Droid Sans, Noto Sans, and Handel Gothic TTFs reside exclusively under `baseq3/fonts`, reflecting Quake Live’s typography choices, but the GPL tree does not stage a font directory or regenerated atlases yet.【60b9f9†L1-L5】【4bab0c†L1-L2】
- **Broader art/shader dependencies.** Icons, levelshots, and UI shader scripts that back menu gradients and cursors remain in the reference tree and are called out in the global asset audit; none of these resources are tracked in `src/` today.【273dcd†L5-L28】

## Parity Gaps & Recommended Actions
| Area | Gap | Action |
| --- | --- | --- |
| Locale & team metadata | `country.txt` and `teaminfo.txt` are still only present in the reference snapshot, preventing the UI from rendering country pickers and spectator team callouts.【f8903d†L3-L8】 | Import the missing tables, validate encoding, and verify that dropdown owner-drawers resolve after packaging.
| Legacy HUD preset | `hud3.txt` has not been migrated, so the legacy preset referenced by configuration tools is unavailable.【f8903d†L3-L8】 | Copy the preset into `src/ui`, then surface it through the HUD selector to preserve user workflows.
| HUD/menu art | Quake Live’s HUD imagery (`ui/assets/*`) is absent from the GPL tree, leaving scoreboxes and menu chrome without the intended gradients and iconography.【c79cbb†L3-L9】【4d18d4†L1-L2】 | Stage the hierarchy inside a reproducible PK3 (e.g., `pak_uiql.pk3`) and update the data build scripts to package it.
| Fonts & readability | The Quake Live TTF set is not staged, risking fallback to Quake III bitmap fonts that do not match the scripted point sizes in competitive HUDs.【60b9f9†L1-L5】【77ce0a†L9-L22】 | Add a font bake step that emits `fonts/font`, `fonts/smallfont`, and `fonts/bigfont` atlases referenced by the menus before packaging.
| Shader/material coverage | UI shader scripts referenced by the audit are missing from source control, so gradients and ink overlays degrade when the renderer falls back to legacy definitions.【273dcd†L5-L28】 | Import `ui*.shader` definitions alongside the art bundle and trigger shader cache regeneration in the build pipeline.

## Accessibility Backlog
1. **Prioritise color-differentiated scoreboxes.** Score widgets currently rely on semi-transparent red/blue fills plus numeric owner-draw values; re-importing the Quake Live art bundle should preserve dual encoding while providing higher-contrast assets for colorblind users.【77ce0a†L27-L93】
2. **Add textual cues for spectator overlays.** Spectator HUD panels render ink-fade textures without explicit labels; pair reintroduced textures with brief text summaries or tooltips to support screen readers and low-vision players.【ba2fd2†L29-L87】
3. **Localise country and team lists.** Restoring `country.txt`/`teaminfo.txt` enables locale-aware dropdowns and team rosters, ensuring players relying on textual identification are not excluded.【f8903d†L3-L8】
4. **Document assetGlobalDef expectations.** The competitive HUD scripts hardcode font and cursor references inside `assetGlobalDef`; adding contributor guidance ensures replacements maintain sizing and contrast guarantees.【77ce0a†L9-L33】
