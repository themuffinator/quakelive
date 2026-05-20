# Quake Live Steam Host Mapping Round 268

## Scope

This pass tightened the `cg_main.c` HUD asset parser leaf beneath the retail
menu parser corridor.

The directly checked helper was:

- `0x10025590 -> CG_Asset_Parse`

Adjacent source hygiene also added the required function header and repository
prototype spacing for `CG_GetMenuBuffer`, which is local menu-file wiring next
to the recovered parser leaf.

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows
  `0x10025590` reading parser tokens through the pc-source import slot
  `data_1074cccc + 0x1B8`, accepting the opening asset block, and returning
  success only on the closing brace.
- The same HLIL block walks the same asset-token family as the current source:
  `font`, `smallFont`, `bigfont`, `gradientbar`, `menuEnterSound`,
  `menuExitSound`, `itemFocusSound`, `menuBuzzSound`, `cursor`, `fadeClamp`,
  `fadeCycle`, `fadeAmount`, `shadowX`, `shadowY`, and `shadowColor`.
- `references/analysis/quakelive_symbol_aliases.json` and
  `references/symbol-maps/cgame.json` both carry `0x10025590` as
  `CG_Asset_Parse`.
- The caller evidence stays in the already-mapped `CG_ParseMenu` leaf:
  `assetGlobalDef` dispatches into `CG_Asset_Parse` before `menudef` dispatches
  into the browser/menu parser.

## Source Updates

- Added the required source header above `CG_Asset_Parse`.
- Normalized `CG_Asset_Parse` to repository-style declaration spacing.
- Added the required source header above the adjacent `CG_GetMenuBuffer` helper
  and normalized its declaration spacing.
- Preserved behavior in both helpers.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the source-side
  `CG_Asset_Parse` token handling, the `CG_ParseMenu -> CG_Asset_Parse`
  caller edge, the committed HLIL token chain at `0x10025590`, and the
  symbol-map/alias evidence for the recovered name.

## Parity Estimate

- Before: HUD asset-parser source-compliance and evidence parity was about
  97%.
- After: about 98%.

This round was intentionally behavior-neutral.
