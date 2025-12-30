# UI Strings & Assets Parity Audit (Quake Live)

## Scope
This report cross-references UI strings/assets tracked in documentation with Quake Live asset drops and the UI HLIL dump to highlight gaps that require updates in `src/code/ui/` and `src/ui/`.

## Sources Reviewed
- `docs/documentation-backlog.md`
- `docs/ui/localization/credential-menu_strings.md`
- `assets/quakelive/baseq3/ui/`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `src/code/ui/`
- `src/ui/`

## Outstanding UI Strings
### Credential menu localization set not implemented in code or menus
The localization table for credential menus lists runtime strings that should live in a dedicated UI implementation, but there is no corresponding menu script or C implementation in the current tree:
- `docs/ui/localization/credential-menu_strings.md` references `src/code/ui/ui_cdkey.c`, which does not exist.
- `src/code/ui/ui_local.h` declares `UI_CDKeyMenu`, `UI_CDKeyMenu_Cache`, and `UI_CDKeyMenu_f`, and `src/code/ui/ui_main.c` calls `UI_CDKeyMenu()` via the `openCredentials` script action.
- No credential/`cdkey` menu definitions exist in `src/ui/` or `assets/quakelive/baseq3/ui/` (searching for “credential” yields no menu scripts).

**Required change:** implement the credential menu UI (menu script in `src/ui/` and matching C implementation in `src/code/ui/`, e.g., a new `ui_cdkey.c`) and wire the localization strings into the menu or a string table to match the documented identifiers.

### CD key waiting prompt mismatch
The HLIL dump includes a CD key prompt string that does not match the current UI text:
- HLIL string: “Waiting for new key... Press ESC…”
- `src/code/ui/ui_main.c` uses “Waiting for new key... Press ESCAPE to cancel”.

**Required change:** align the prompt string with the HLIL wording (or capture the HLIL text in localization so menu text matches the retail UI).

## Outstanding UI Assets
### `menu/art/*` references missing from asset drop
The HLIL dump references a small set of Quake Live menu art paths that do not exist under `assets/quakelive/baseq3/`:
- `menu/art/3_cursor2`
- `menu/art/fx_base`
- `menu/art/fx_blue`
- `menu/art/fx_cyan`
- `menu/art/fx_grn`
- `menu/art/fx_red`
- `menu/art/fx_teal`
- `menu/art/fx_white`
- `menu/art/fx_yel`
- `menu/art/unknownmap`

**Required change:** add the referenced art assets (or remap the UI to available art) so `src/ui/` has parity with the HLIL-referenced menu art.

### UI asset directory not mirrored into `src/ui/`
`assets/quakelive/baseq3/ui/assets/` contains the Quake Live UI artwork (cursor, buttons, HUD art, etc.), but there is no `src/ui/assets/` directory.

**Required change:** stage the UI art hierarchy under `src/ui/assets/` (or update the build tooling to pull from the Quake Live asset drop) so the script-driven menus can reference the artwork in-tree.

## Notes on Backlog Items
`docs/documentation-backlog.md` highlights missing metadata text tables (`country.txt`, `teaminfo.txt`, `hud3.txt`). These files already exist in both `assets/quakelive/baseq3/ui/` and `src/ui/` with matching content, so the backlog entry appears to be satisfied and should be updated once verified against additional HLIL/UI behaviour.
