# HUD/Menu Scripting Guide

## Introduction
This guide explains how to stage Quake Live HUD and menu assets inside the GPL tree, script layout updates, and incorporate accessibility safeguards so contributors can iterate without regressing parity.

## Asset Workflow Overview
1. **Mirror the reference hierarchy.** Copy `baseq3/ui/*.menu` and supporting text files (`country.txt`, `teaminfo.txt`, etc.) into a staging area that preserves path semantics expected by the UI VM.【672aa6†L21-L28】
2. **Bundle art dependencies.** Stage `ui/assets/` folders (HUD chrome, scoreboxes, menu chrome, flags) plus fonts and shader scripts before packaging so the renderer resolves every `assetGlobalDef` entry that Quake Live menus reference.【5d67f4†L1-L10】【ddcdc5†L9-L20】
3. **Generate distributable PK3s.** After copying scripts and assets, archive them into a PK3 alongside regenerated font atlases and the updated `default.cfg` bindings, ensuring engine bootstrap paths stay intact.【672aa6†L21-L33】
4. **Automate regeneration.** Capture the copy, conversion, and packaging commands in repeatable scripts so asset updates remain traceable and can be re-run across platforms.【672aa6†L23-L28】

## Scripting Conventions
- **Use Quake Live owner-draw IDs and flags.** Menus such as `comp_hud.menu` rely on owner-draw flags like `CG_SHOW_IF_RED_IS_FIRST_PLACE` and `CG_HEALTH_COLORIZED`; ensure `menudef.h` and cgame drawing code expose these IDs before scripting new widgets.【F:src/ui/menudef.h†L137-L212】【ddcdc5†L31-L152】
- **Respect widescreen directives.** Many HUD definitions set `widescreen WIDESCREEN_RIGHT` to anchor panels; maintain or extend these directives so elements scale cleanly across aspect ratios.【ddcdc5†L25-L123】
- **Centralize shared assets via `assetGlobalDef`.** Reference fonts, gradients, and cursors through the global asset block so future theme adjustments require minimal file edits.【ddcdc5†L9-L21】
- **Isolate gametype logic with `ownerdrawflag`.** Instead of branching in code, use menu flags such as `CG_SHOW_ANYTEAMGAME` or `CG_SHOW_IF_PLYR_IS_FIRST_PLACE` to handle permutations directly in script, keeping HUD logic declarative.【ddcdc5†L23-L152】

## Accessibility Considerations
- **Color contrast & duplication.** Scoreboxes tint red/blue backgrounds via `backcolor` while also presenting numeric owner-draw values, providing dual encoding that benefits colorblind players; preserve both signals when updating palettes.【ddcdc5†L31-L153】
- **Readable typography.** Quake Live defines separate font sizes (`font`, `smallFont`, `bigFont`) for HUD elements—ensure regenerated atlases match these sizes to maintain legibility at high resolutions.【ddcdc5†L9-L21】
- **State clarity.** Use owner-draw gates to show or hide overtime, follow-state, or gametype badges so the HUD avoids clutter while still surfacing critical state transitions, aiding cognitive accessibility.【ddcdc5†L23-L152】【366a0d†L65-L116】
- **Scalability hooks.** Keep layout rectangles grouped (for example, the TeamScoreboxes menus) so future scaling logic can adjust positions/sizes programmatically when implementing resolution or UI scale sliders.【ddcdc5†L23-L152】

## Review Checklist
- [ ] All referenced asset paths exist in the packaged PK3 and match case-sensitive expectations.
- [ ] Menu scripts compile without missing owner-draw IDs or shader references.
- [ ] Accessibility cues (color tint + text, readable fonts, conditional visibility) remain intact after modifications.
- [ ] Automated scripts regenerate assets/fonts so future contributors can reproduce the HUD package.
