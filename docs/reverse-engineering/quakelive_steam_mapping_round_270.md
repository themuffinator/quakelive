# Quake Live Steam Host Mapping Round 270

## Scope

This pass tightened the `cg_main.c` HUD bootstrap split immediately after the
menu-file loader round.

The directly checked helpers were:

- `0x10029120 -> CG_LoadHudMenu`
- `0x10029420 -> CG_AssetCache`

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows
  `0x10029120` resetting the menu count, reading `cg_hudFiles` through the
  cvar-string import, falling back to `ui/hud.txt`, calling `CG_LoadMenus`, and
  then calling the scoreboard-selection menu cache helper.
- The same HLIL file shows `0x10029420` registering the shared HUD art bank
  through the shader-no-mip import slot: `gradientbar2`, `fx_*`, scrollbar
  pieces, and slider art.
- `references/analysis/quakelive_symbol_aliases.json` and
  `references/symbol-maps/cgame.json` carry both recovered helper names.

## Source Updates

- No behavior changes were needed in this pass.
- The new guard documents the current intentional source split:
  - `CG_Init` calls `CG_InitDisplayContext` before `CG_LoadHudMenu`.
  - `CG_LoadHudMenu` owns the `cg_hudFiles` read, `ui/hud.txt` fallback,
    `CG_LoadMenus` call, and scoreboard menu cache refresh.
  - `CG_AssetCache` owns the shared HUD art bank registration and the local
    score texture cache.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the source-side HUD
  bootstrap split, the committed HLIL evidence for `0x10029120`, the asset bank
  token family at `0x10029420`, and the symbol-map/alias evidence for both
  helpers.

## Parity Estimate

- Before: HUD bootstrap split and asset-cache evidence parity was about 98%.
- After: about 98.5%.

This round was behavior-neutral.
