# HUD & Menu Asset Audit

## Scope
This audit compares the Quake Live reference snapshot under `references/original-assets/quakelive/baseq3` against the GPL tree to identify HUD/menu scripts, supporting assets, and metadata required for feature parity.

## Summary of Findings
- **Menu scripts largely ported, with a few metadata gaps.** The GPL tree carries 65 menu/HUD files versus 66 in the snapshot, omitting `country.txt`, `hud3.txt`, and `teaminfo.txt` while adding `ingame_quakelive.txt` and `menus_quakelive.txt` for migration tracing.【1c6e30†L13-L16】 These missing scripts provide locale and team configuration data that the Quake Live UI expects when populating dropdowns and spectator panels.
- **Art asset directories are absent from the active tree.** The reference dump includes `ui/assets` folders for HUD elements, scoreboards, menu chrome, and flag art, but no equivalent directory exists under `src/ui/` today, indicating the GPL build cannot render the Quake Live-specific imagery without repackaging the PNG/TGA set.【14ce7a†L7-L15】
- **Broader UI asset families remain outside source control.** Fonts, icons, levelshots, and shader definitions reside exclusively under the reference snapshot, so parity requires staging these resources into the build pipeline alongside the menu scripts.【5d67f4†L1-L10】

## Detailed Gap Analysis
| Area | Reference Coverage | GPL Tree Status | Recommended Follow-Up |
| --- | --- | --- | --- |
| Menu & HUD scripts | 66 `.menu`/`.txt` files governing competitive HUDs, scoreboards, and flow menus under `baseq3/ui/`. | 65 ported scripts in `src/ui/`, missing `country.txt`, `hud3.txt`, and `teaminfo.txt` metadata required for nationalities and team overlays.【1c6e30†L13-L16】 | Import the missing text definitions; confirm script loader handles locale/team tables before UI regression testing. |
| HUD/menu art | `ui/assets/` subfolders for `hud`, `statusbar`, `score`, `flags`, `menu`, and `main_menu` imagery.【5d67f4†L1-L6】 | No `src/ui/assets/` directory exists, so builds fall back to Quake III art or placeholders.【14ce7a†L7-L15】 | Stage the PNG/TGA set inside a new asset package (e.g., `pak_uiql.pk3`) and update the data build scripts to bundle it. |
| Fonts | `baseq3/fonts/` holds Quake Live font TTFs and generated image atlases.【5d67f4†L1-L10】 | Fonts absent from GPL tree, leaving legacy Quake III atlas generation in place. | Introduce a reproducible font bake step that outputs Quake Live-aligned sizes, then update menu definitions to reference the new assets. |
| Shader definitions | UI shaders captured under `baseq3/scripts/` in the reference dump.【5d67f4†L1-L10】 | No Quake Live-specific shader scripts shipped in source; renderer uses legacy set. | Copy `ui*.shader` files into the build and regenerate lightmaps/material caches so the HUD art renders with intended blending. |
| Locale data | `country.txt` enumerates country codes, and `teaminfo.txt` drives spectator overlays in the snapshot. | Entries missing from GPL tree, so UI cannot populate those selectors.【1c6e30†L13-L16】 | Import files, verify encoding, and hook into the spectator/team HUD widgets during QA passes. |

## Next Steps
1. **Asset Staging:** Mirror the `ui/assets` folder hierarchy inside the build output and ensure the packaging step includes flags, HUD chrome, and scoreboard art.
2. **Script Synchronisation:** Bring across `country.txt`, `teaminfo.txt`, and `hud3.txt`, then diff menu scripts against the reference to confirm no additional drift.
3. **Font/Shader Integration:** Automate font atlas generation from the Quake Live TTFs and deploy the matching shader scripts to preserve intended rendering.
4. **Verification:** Establish UI regression tests that load competitive HUD presets, spectator views, and vote dialogs to confirm assets resolve without fallback art.
