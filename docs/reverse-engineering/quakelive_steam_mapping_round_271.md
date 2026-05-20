# Quake Live Steam Host Mapping Round 271

## Scope

This pass tightened the `cg_main.c` init/shutdown lifecycle around the native
cgame export table and advertisement bridge.

The directly checked helpers were:

- `0x10029820 -> CG_Init`
- `0x10029FC0 -> CG_Shutdown`

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows the
  retail init tail calling the asset cache, HUD load, config-value bootstrap,
  music start, advertisement bridge init import at `data_1074cccc + 0xF4`,
  game-info cvar refresh, and country-flag cache.
- The same HLIL file shows `0x10029FC0` calling the shutdown-side advertisement
  bridge import at `data_1074cccc + 0xF8`, then restoring `ui_mainmenu` through
  the cvar-set import.
- The native export table rooted at `data_100769A8` maps the init slot to
  `sub_10029820` and the shutdown slot to `sub_10029FC0`.
- `references/analysis/quakelive_symbol_aliases.json` and
  `references/symbol-maps/cgame.json` carry the recovered `CG_Init` /
  `CG_Shutdown` names.

## Source Updates

- Clarified the function headers for `CG_Init` and `CG_Shutdown`.
- Preserved behavior:
  - `CG_Init` still calls the advertisement bridge init after shader-state
    refresh and before the final looping-sound clear.
  - `CG_Shutdown` still clears local reconstructed state, calls the host
    shutdown bridge, then restores `ui_mainmenu`.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the source lifecycle,
  source native export table entries, the committed HLIL init/shutdown import
  slots, the retail native table entries, and the symbol-map/alias evidence.

## Parity Estimate

- Before: init/shutdown lifecycle evidence parity was about 98%.
- After: about 98.5%.

This round was behavior-neutral.
