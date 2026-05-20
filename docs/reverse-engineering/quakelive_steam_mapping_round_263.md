# Quake Live Steam Host Mapping Round 263

## Scope

This pass stayed in the `cgame/cg_main.c` HUD parser corridor immediately
above the previously checked HUD bootstrap path.  The target helpers were:

- `0x10025AC0 -> CG_ParseMenu`
- `0x10025C40 -> CG_Load_Menu`
- `0x10025CA0 -> CG_LoadMenus`

## Evidence

- `references/reverse-engineering/ghidra/cgamex86/functions.csv` still carries
  function boundaries for `FUN_10025ac0` and `FUN_10025c40`.
- `references/analysis/quakelive_symbol_aliases.json` maps those starts to
  `CG_ParseMenu` and `CG_Load_Menu`.
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows
  `0x10025AC0` loading the requested pc source through the display context
  callback slot at `+0x1B0`, falling back to `ui/testhud.menu`, reading tokens
  through `+0x1B8`, and freeing the source through `+0x1B4`.
- The same HLIL block contains the stable parser strings `assetGlobalDef` and
  `menudef`.
- `0x10025C40` parses a `loadmenu { ... }` block and calls back into
  `0x10025AC0` for each nested menu token.
- `0x10025CA0` retains the outer HUD-script load loop and the retail
  `UI menu load time = %d milli seconds\n` print.

## Source Updates

- Added the required function headers above `CG_ParseMenu`, `CG_Load_Menu`, and
  `CG_LoadMenus`.
- Normalized the three helper declarations and nearby parser call formatting to
  repository style:
  - `void CG_ParseMenu( const char *menuFile )`
  - `qboolean CG_Load_Menu( char **p )`
  - `void CG_LoadMenus( const char *menuFile )`
- Preserved the existing shared-runtime reconstruction: `CG_ParseMenu` still
  initializes menu roots through `CG_InitBrowserOverlay`, parses through
  `CG_ParseBrowserMenu`, and avoids cloning shared UI parser bodies.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the normalized parser
  declarations, the source-side wrapper calls, and the committed HLIL anchors
  for the pc-source callback slots and parser strings.

## Parity Estimate

- Before: `CG_ParseMenu` / `CG_Load_Menu` / `CG_LoadMenus` source declaration
  and evidence-lock parity was about 96%.
- After: about 97%.

This pass was intentionally behavior-neutral; the gain is source compliance and
stronger drift protection around the retail parser seam.
