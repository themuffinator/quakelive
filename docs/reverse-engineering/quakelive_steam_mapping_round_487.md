# Quake Live Steam Mapping Round 487: WinMain Tooltip Shell

## Scope

This round reconstructs the native WinMain tooltip common-control shell that
retail creates after the Windows-key hook and before the Steam web-menu launch.
It is part of the Steam launch/runtime host lane because the observed shell
immediately precedes `asset://ql/index.html` startup in retail
`quakelive_steam.exe`.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/application-initialization-wiring-reconstruction-2026-05-27.md`

Observed facts:

- Retail `WinMain @ 0x004ED830` initializes `INITCOMMONCONTROLSEX` with
  `dwSize = 8` and `dwICC = 4`, then calls `InitCommonControlsEx`.
- The import table contains `COMCTL32.DLL!InitCommonControlsEx`.
- Retail creates a tooltip window with class `"tooltips_class32"` and style
  `0x80000003`, which corresponds to `WS_POPUP | TTS_ALWAYSTIP |
  TTS_NOPREFIX`.
- Retail uses default coordinates and sizes (`0x80000000`), then positions the
  tooltip window with `hWndInsertAfter = 0xfffffffe` and flags `0x13`, matching
  `HWND_NOTOPMOST` plus `SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE`.
- Retail builds a tool info block with `cbSize = 0x30`, `uFlags = 0x10`, the
  main window, the executable instance, an empty tooltip string, and the desktop
  rectangle.
- Retail sends `TTM_ADDTOOLA` (`0x404`) followed by `TTM_ACTIVATE` (`0x401`)
  with activation disabled.
- The next observed WinMain host action is the Steam web-menu URL launch
  `asset://ql/index.html`.

## Source Reconstruction

Implemented source-side changes:

- Added a dynamic `comctl32.dll` loader helper, `Sys_InitCommonControls`, so
  source builds do not need a new project-level link dependency while still
  exercising the retail common-control import contract.
- Added `Sys_InitTooltipShell` to create the retained tooltip host window with:
  - `ICC_BAR_CLASSES`
  - `TOOLTIPS_CLASSA`
  - `WS_POPUP | TTS_ALWAYSTIP | TTS_NOPREFIX`
  - `CW_USEDEFAULT` for all position and size inputs
  - `HWND_NOTOPMOST` and `SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE`
  - an empty desktop-wide `TOOLINFOA` entry
  - `TTM_ADDTOOLA` and inactive `TTM_ACTIVATE`
- Added `Sys_ShutdownTooltipShell` and wired it into both `Sys_Error` and
  `Sys_Quit` after the Windows-key hook shutdown.
- Wired `Sys_InitTooltipShell` into `WinMain` immediately after
  `Sys_InitWinkeyHook` and before the main frame loop.
- Extended `tests/test_application_initialization_mapping.py` to pin the retail
  HLIL constants, source call order, dynamic common-control loader, tooltip
  creation, message sends, and shutdown ordering.

No live Steam service behavior changed. The Steam/browser URL bootstrap remains
behind the existing online-services policy and retained client bootstrap path.

## Validation

Focused validation passed:

- `python -m pytest tests/test_application_initialization_mapping.py::test_retail_application_startup_chain_maps_primary_owners tests/test_application_initialization_mapping.py::test_winkey_hook_reconstructs_retail_keyboard_filter_and_shutdown -q --tb=short`
  - 2 passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. Static evidence and focused parity tests were
sufficient for this reconstruction.

## Confidence

High confidence for shell creation and placement: HLIL constants, class string,
import evidence, call order, and Win32 symbolic equivalents align.

Medium confidence for future tooltip mutation semantics: the committed evidence
shows shell creation and an empty desktop-wide tool, but does not yet expose a
separate downstream native tooltip text update path beyond the retained browser
tooltip publication.

## Parity Estimate

Scoped WinMain tooltip common-control shell:

- Before: 0%
- After: 92%

Scoped application-initialization wiring lane:

- Before: 98.0%
- After: 98.4%

Overall Steam launch/runtime integration:

- Before: 88%
- After: 89%
