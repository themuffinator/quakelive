# Quake Live Steam Host Mapping Round 262

## Scope

This round stays in `cgame/cg_main.c`, but shifts from the display-context
callback slab to the HUD bootstrap corridor around `CG_LoadHudMenu`,
`CG_LoadMenus`, and `CG_AssetCache`.

Primary evidence:

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`
- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/symbol-maps/cgame.json`
- `src/code/cgame/cg_main.c`
- `src/code/cgame/cg_local.h`
- `tests/test_cgame_displaycontext_parity.py`

## HUD Bootstrap Evidence

Observed corpus facts:

1. `0x10025CA0 -> CG_LoadMenus` owns the menu-file read, default HUD fallback,
   `COM_Compress`, supplemental menu load path, `loadmenu` token handling, and
   menu load-time print.
2. `0x10029120 -> CG_LoadHudMenu` reads `cg_hudFiles`, falls back to the retail
   HUD default, and calls `CG_LoadMenus`.
3. Current source intentionally extends the loader with cgame-owned HUD script
   scanning (`CG_HudScriptHasMenuLoads`, `CG_HudScriptHasCompetitiveMenus`),
   draw2D cache refresh, and scoreboard selection menu caching. Those
   extensions are already documented in the cgame mapping notes as source
   reconstruction on top of the retail loader seam.
4. `0x10029420 -> CG_AssetCache` registers the shared gradient, fx, scrollbar,
   and slider assets used by the HUD/menu path.
5. `CG_Init` still preserves the recovered ordering: display-context init and
   HUD font registration before collision-map load, then asset cache and HUD
   menu load after graphics/clients registration.

## Source Reconstruction

No behavior changed in this pass. The source updates are declaration hygiene for
already-mapped helpers:

- `CG_LoadMenus` now uses the repository's spaced prototype style in both
  `cg_main.c` and `cg_local.h`.
- `CG_LoadHudMenu` now has an explicit `( void )` parameter list and the
  required reconstruction function header.
- `CG_LoadHudMenu` now uses tabbed, spaced call formatting for
  `trap_Cvar_VariableStringBuffer`, the empty-string fallback check, and
  `CG_LoadMenus`.
- `CG_AssetCache` now has an explicit `( void )` parameter list.
- The display-context parity tests now locate these helpers through the updated
  declarations while keeping the existing retail behavior assertions intact.

## Validation

Commands run:

```text
python -m pytest tests/test_cgame_displaycontext_parity.py tests/test_cgame_console_surface_parity.py -q
```

Result:

- `103 passed in 1.02s`

No runtime launch was performed. This was a static source-shape and evidence
guarding pass on already-recovered HUD bootstrap helpers.

## Parity Estimate

Estimated `cg_main.c` HUD bootstrap parity remains **98% -> 98%**. This round
does not add new runtime behavior; it improves source compliance and keeps the
tests aligned with the recovered loader/asset-cache helper declarations.
