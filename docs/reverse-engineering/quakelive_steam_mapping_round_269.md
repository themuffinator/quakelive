# Quake Live Steam Host Mapping Round 269

## Scope

This pass tightened the `cg_main.c` HUD menu-file loader wrapper beneath the
retail parser corridor.

The directly checked helper was:

- `0x10025CA0 -> CG_LoadMenus`

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows
  `0x10025CA0` timing the load through the millisecond import, opening the
  requested menu file through `data_1074cccc + 0x38`, warning and falling back
  to `ui/hud.txt` when the selected file is missing, and using the error trap
  only for the missing default and oversize paths.
- The same HLIL block reads into the static menu buffer through import slot
  `+0x3C`, nul-terminates it, closes the handle through `+0x44`, compresses the
  script, resets the menu runtime, walks `loadmenu` tokens, and prints the final
  `UI menu load time` diagnostic.
- `references/analysis/quakelive_symbol_aliases.json` and
  `references/symbol-maps/cgame.json` both carry `0x10025CA0` as
  `CG_LoadMenus`.

## Source Updates

- Aligned the missing selected-HUD path with retail behavior:
  - Before: the warning path called `trap_Error`, making the intended fallback
    effectively fatal.
  - After: it calls `CG_Printf` and continues into the legacy `ui/hud.txt`
    fallback.
- Preserved the existing fatal handling for a missing default HUD file and for
  oversized menu files.
- Preserved the current cgame-owned `CG_ResetBrowserOverlayState` wrapper in
  place of directly calling the shared UI reset helper.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the source-side
  loader wrapper, the warning/fatal split, the file read/close path, script
  compression, cgame overlay reset, supplemental menu parsing, `loadmenu`
  dispatch, load-time print, and the committed HLIL evidence for
  `0x10025CA0`.

## Parity Estimate

- Before: HUD menu loader behavior and evidence parity was about 96%.
- After: about 98%.
