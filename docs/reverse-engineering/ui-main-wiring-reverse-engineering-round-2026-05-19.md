# `ui/ui_main.c` Wiring Reverse-Engineering Round (2026-05-19)

## Scope

This round audited `src/code/ui/ui_main.c` and the adjacent engine/UI native
wiring without editing `src/ui/` or `assets/`, which remain read-only by repo
policy. The goal was to refresh the evidence trail around the retail
`uix86.dll` UI module, identify which source paths are literal retail
reconstruction, and keep the Quake Live-only browser/advert/workshop lanes
explicitly bounded.

## Evidence Read

- Retail binary metadata: `references/reverse-engineering/ghidra/uix86/metadata.txt`
  reports `uix86.dll`, 348 Ghidra functions, 50 imports, 2 exports
  (`dllEntry`, `entry`), and 180 decompiled functions.
- Retail symbol map: `references/symbol-maps/ui.json` now tracks 444 mapped UI
  corpus anchors: 348 Ghidra functions plus 96 HLIL-only anchors.
- Ghidra source hints: `references/reverse-engineering/ghidra/uix86/decompile_annotated.c`
  anchors the large runtime owners:
  - `UI_RunMenuScript @ 0x1000B0E0`, size 8704
  - `UI_FeederSelection @ 0x1000EBA0`, size 1425
  - `_UI_Init @ 0x1000FAB0`, size 1156
  - `UI_RegisterCvars @ 0x10011730`, size 345
  - `UI_RefreshDisplayContextScale @ 0x1000F9F0`, size 191
  - `Menu_RefreshAdvertCellShaders @ 0x100155A0`, size 267
- HLIL cross-check: `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
  still carries `web_browserActive` at retail string address `0x10029140` and
  runtime references through the display context.
- Source wiring inspected:
  - `src/code/ui/ui_main.c`
  - `src/code/ui/ui_public.h`
  - `src/code/client/cl_ui.c`
  - `src/code/qcommon/vm.c`

## Current Source Shape

The production source keeps two UI call surfaces active:

1. Legacy `vmMain` dispatch in `src/code/ui/ui_main.c`, used by classic
   QVM/DLL call numbering.
2. Recovered Quake Live native export table in the same file, declared through
   `uiNativeExport_t` in `src/code/ui/ui_public.h` and called from
   `VM_CallNativeExports` in `src/code/qcommon/vm.c`.

The native side has 14 recovered export slots:

| Slot | Source owner | Retail role |
| --- | --- | --- |
| 0 | `_UI_Init` | Boot UI cvars, `uiDC`, menus, assets, scores, bots |
| 1 | `_UI_Shutdown` | Save cached LAN servers |
| 2 | `_UI_KeyEvent` | Focused menu key dispatch |
| 3 | `_UI_MouseEvent` | Cursor projection and menu mouse movement |
| 4 | `_UI_Refresh` | Cvar update, menu paint, cursor draw |
| 5 | `_UI_IsFullscreen` | Any fullscreen menu visible predicate |
| 6 | `_UI_SetActiveMenu` | Main/ingame/team/error menu activation |
| 7 | `UI_ConsoleCommand` | UI console command dispatcher |
| 8 | `UI_DrawConnectScreen` | Connect/download status rendering |
| 9 | `UI_HasUniqueCDKey` | CD-key uniqueness shim |
| 10 | `UI_RefreshDisplayContext` | Refresh glconfig and 640x480 scale state |
| 11 | `Menus_AnyVisible` | Any visible menu predicate |
| 12 | `UI_ForEachArenaName` | Arena-name iterator callback |
| 13 | `UI_DrawAdvertisementWaitScreen` | Advert wait-screen rendering helper |

The host import slab in `src/code/client/cl_ui.c` is the matching recovered
Quake Live side. The most UI-specific imports are:

- `UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER` -> `QL_UI_trap_SetupAdvertCellShader`
- `UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER` -> `QL_UI_trap_RefreshAdvertCellShader`
- `UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE` -> `QL_UI_trap_InitAdvertisementBridge`
- `UI_QL_IMPORT_UNUSED_83` -> `QL_UI_trap_UpdateAdvert`
- `UI_QL_IMPORT_ACTIVATE_ADVERT` -> `QL_UI_trap_ActivateAdvert`
- `UI_QL_IMPORT_IS_SUBSCRIBED_APP` -> `QL_UI_trap_IsSubscribedApp`
- `UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO` -> `QL_UI_trap_GetItemDownloadInfo`

## High-Confidence Matches

`_UI_Init` is structurally aligned with retail. Retail assigns the same core
display-context callbacks in `decompile_annotated.c`: `UI_OwnerDraw`,
`UI_OwnerDrawVisible`, `UI_RunMenuScript`, `UI_OwnerDrawHandleKey`, and
`UI_FeederSelection`. Source mirrors that in `uiInfo.uiDC` and also calls
`UI_InitAdvertisementBridge` before wiring the advert callbacks, matching the
retail import at offset `0x148`.

`UI_RefreshDisplayContextScale` is bounded by Ghidra and source. Retail calls
the glconfig import and computes widescreen bias/scale from the renderer size;
source refreshes `uiInfo.uiDC.glconfig`, computes 4:3-preserving `xscale`,
`yscale`, and `bias`, and feeds those values into mouse projection and drawing.

`UI_RunMenuScript` remains the biggest owner. The symbol map and annotated
decompile both tie it to callvote map preview/submission, CD-key cvar staging,
server refresh commands, web/browser commands, admin/vote paths, model color
sync, and the fallback unknown-command log. Source keeps the same retail-owned
branches and adds explicit browser-disabled routing rather than silently
executing inert `web_*` commands.

`UI_FeederSelection`, `UI_CVMapCountByGameType`, and `UI_SelectedMap` are
stable as the callvote map chain. The retail evidence proves
`FEEDER_CVMAPS -> UI_CVMapCountByGameType -> UI_SelectedMap -> ui_currentNetMap`.
Source carries the same `ui_cvGameType` reset in `_UI_Init` and
`_UI_SetActiveMenu(UIMENU_INGAME)`, preserving the retail default filter state.

`UI_DisplayDownloadInfo` and `QL_UI_trap_GetItemDownloadInfo` are the connect
screen's workshop progress pair. Retail UI reads `cl_downloadItem`, parses the
64-bit item id with `sscanf("%llu")`, calls import slot 96 with the low/high
words and downloaded/total outputs, then reads `cl_downloadTime`. Source now
keeps formatting in `ui_main.c`, sends the native path through
`trap_QL_GetItemDownloadInfo`, and leaves the older `cl_downloadCount` /
`cl_downloadSize` path as a VM fallback rather than the recovered native path.

## Bounded Compatibility Lanes

The following paths are intentionally not literal live-service parity in the
default build:

- Browser overlay flow: `UI_BrowserOverlayAvailable`,
  `UI_ResolveMenuFlowInternal`, `UI_SetBrowserActive`, and
  `UI_HandleDeferredScriptExec` keep retail `web_browserActive` semantics visible
  while keeping the retail menu root active when the Awesomium-style overlay is absent.
- Advertisement bridge: UI script and ownerdraw plumbing is mapped, but the host
  default path falls back to registered default shaders and null/compatibility
  bridge behavior unless online services are explicitly enabled.
- Subscription/workshop imports: `QL_UI_trap_IsSubscribedApp` and
  `QL_UI_trap_GetItemDownloadInfo` are correctly isolated in the client bridge,
  but live Steam-backed results remain governed by the repo-wide online-service
  policy.
- Menu data: `src/ui/` remains read-only. Runtime panel parity is handled by the
  current UI bundle/overlay pipeline rather than direct source-menu edits.

These lanes comply with the repository policy to keep Quake Live-only online
services behind `QL_BUILD_ONLINE_SERVICES` or equivalent disabled/default
fallbacks.

## Native Slot Follow-Up

This follow-up pass resolved the two next-work items from the first pass:
refreshing the Quake Live UI import slot ledger and checking the qmenu advert
leaves that feed `ui_main.c` through the display context.

The export side remains the recovered 14-slot native table:

| Export slot | Source table entry | Notes |
| --- | --- | --- |
| `UI_NATIVE_EXPORT_INIT` | `UI_NativeInit` | Wrapper around `_UI_Init` so the native path accepts a strict `qboolean`. |
| `UI_NATIVE_EXPORT_SHUTDOWN` | `_UI_Shutdown` | Shared legacy/native shutdown owner. |
| `UI_NATIVE_EXPORT_KEY_EVENT` | `UI_NativeKeyEvent` | Drops the extra native `time` argument before calling `_UI_KeyEvent`. |
| `UI_NATIVE_EXPORT_MOUSE_EVENT` | `_UI_MouseEvent` | Uses the source-side screen-to-virtual cursor projection. |
| `UI_NATIVE_EXPORT_REFRESH` | `_UI_Refresh` | Shared refresh owner. |
| `UI_NATIVE_EXPORT_IS_FULLSCREEN` | `_UI_IsFullscreen` | Shared fullscreen predicate. |
| `UI_NATIVE_EXPORT_SET_ACTIVE_MENU` | `_UI_SetActiveMenu` | Shared active-menu owner. |
| `UI_NATIVE_EXPORT_CONSOLE_COMMAND` | `UI_ConsoleCommand` | Shared console command dispatcher. |
| `UI_NATIVE_EXPORT_DRAW_CONNECT_SCREEN` | `UI_NativeDrawConnectScreen` | Thin native wrapper around `UI_DrawConnectScreen`. |
| `UI_NATIVE_EXPORT_HAS_UNIQUE_CD_KEY` | `UI_NativeHasUniqueCDKey` | Native wrapper preserving the source-side `qtrue` result. |
| `UI_NATIVE_EXPORT_REFRESH_DISPLAY_CONTEXT` | `UI_RefreshDisplayContext` | Calls `UI_RefreshDisplayContextScale` then republishes `uiDC` through `Init_Display`. |
| `UI_NATIVE_EXPORT_MENUS_ANY_VISIBLE` | `Menus_AnyVisible` | Extended retail-visible menu predicate. |
| `UI_NATIVE_EXPORT_FOR_EACH_ARENA_NAME` | `UI_ForEachArenaName` | Host callback iterator over loaded arena display names. |
| `UI_NATIVE_EXPORT_DRAW_ADVERTISEMENT_WAIT_SCREEN` | `UI_DrawAdvertisementWaitScreen` | Optional named-menu paint plus the retail wait/cancel prompts. |

The import side from slots 80-96 is fully assigned in `CL_InitUIImports`:

| Import slot | Enum | Client owner | Retail/bounded role |
| --- | --- | --- | --- |
| 80 | `UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER` | `QL_UI_trap_SetupAdvertCellShader` | Initial advert cell shader setup, falling back to default content. |
| 81 | `UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER` | `QL_UI_trap_RefreshAdvertCellShader` | Runtime advert cell refresh, falling back to default content. |
| 82 | `UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE` | `QL_UI_trap_InitAdvertisementBridge` | Mirrors retail UI advert bridge initialization into the client bridge. |
| 83 | `UI_QL_IMPORT_UNUSED_83` | `QL_UI_trap_UpdateAdvert` | Retail UI advert ownerdraw post-draw callback; current host side is intentionally inert. |
| 84 | `UI_QL_IMPORT_ACTIVATE_ADVERT` | `QL_UI_trap_ActivateAdvert` | Forwards `activateAdvert` menu scripts to the client advert bridge. |
| 85 | `UI_QL_IMPORT_UNUSED_85` | `QL_UI_trap_Unused85` | Retail no-op placeholder. |
| 86 | `UI_QL_IMPORT_SET_CURSOR_POS` | `QL_UI_trap_SetCursorPos` | Native cursor setter; Win32-only behavior, portable no-op elsewhere. |
| 87 | `UI_QL_IMPORT_GET_CURSOR_POS` | `QL_UI_trap_GetCursorPos` | Native cursor getter; Win32-only behavior, portable zero result elsewhere. |
| 88 | `UI_QL_IMPORT_PC_ADD_GLOBAL_DEFINE` | `QL_UI_trap_PC_AddGlobalDefine` | Parser import slab begins. |
| 89 | `UI_QL_IMPORT_PC_LOAD_SOURCE` | `QL_UI_trap_PC_LoadSource` | Parser source load. |
| 90 | `UI_QL_IMPORT_PC_FREE_SOURCE` | `QL_UI_trap_PC_FreeSource` | Parser source free. |
| 91 | `UI_QL_IMPORT_PC_READ_TOKEN` | `QL_UI_trap_PC_ReadToken` | Parser token read. |
| 92 | `UI_QL_IMPORT_PC_SOURCE_FILE_AND_LINE` | `QL_UI_trap_PC_SourceFileAndLine` | Parser source location. |
| 93 | `UI_QL_IMPORT_IS_SUBSCRIBED_APP` | `QL_UI_trap_IsSubscribedApp` | Steam subscription probe, bounded by the online-services policy. |
| 94 | `UI_QL_IMPORT_DRAW_SCALED_TEXT` | `QL_UI_trap_DrawScaledText` | Retail scaled text draw bridge used by text helpers such as `Text_Paint_Limit`. |
| 95 | `UI_QL_IMPORT_MEASURE_TEXT` | `QL_UI_trap_MeasureText` | Retail packed width/height measurement bridge. |
| 96 | `UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO` | `QL_UI_trap_GetItemDownloadInfo` | Workshop progress bridge, retained client state first, Steam fallback second. |

## Native Import Reference Header Audit (2026-06-12)

A follow-up audit found that `scripts/ghidra/build_ui_ghidra_reference.py`, the
generated `ui_ghidra_reference.h` snapshots, and `src-re/ui/include/ui_local.h`
still carried an older "syscall table" ledger that placed `Cvar_Register` at
slot 0. That contradicted the committed HLIL and the current `uiQlImport_t`
native table.

Observed HLIL facts:

- `dllEntry @ 0x10003970` stores the engine import table in
  `data_106b40a8` and returns API version 8.
- `data_106b40a8 + 0x10` calls `Cvar_Register`, so the native slot is 4.
- `data_106b40a8 + 0x1c` calls `Cvar_Set`, so the native slot is 7.
- `data_106b40a8 + 0x24` calls `Cvar_VariableStringBuffer`, so the native slot
  is 9.
- `data_106b40a8 + 0xb8`, `+ 0xbc`, and `+ 0xc0` anchor
  `GetClientState`, `GetGlconfig`, and `GetConfigString` at slots 46-48.
- `data_106b40a8 + 0x148`, `+ 0x14c`, and `+ 0x154` anchor the advert bridge
  init/update/no-op region at slots 82, 83, and 85.
- `data_106b40a8 + 0x164` through `+ 0x180` anchor parser, Steam/subscription,
  scaled-text, measurement, and item-download imports at slots 89-96.

The generator and checked-in snapshots now publish the full recovered retail
native import slab from slots 0-96. Source-only bridge extensions such as
`UI_QL_IMPORT_CVAR_RESET`, `UI_QL_IMPORT_CVAR_INFOSTRINGBUFFER`,
`UI_QL_IMPORT_CM_LOADMODEL`, `UI_QL_IMPORT_SET_PBCLSTATUS`, and
`UI_QL_IMPORT_LAUNCHER_READSCREENSHOT` remain intentionally absent from these
retail reference headers because they are not observed retail native slots.

Regression coverage:
`test_ui_native_import_reference_headers_match_recovered_hlil_slots` compares
the generator, both checked-in Ghidra reference headers, and
`src-re/ui/include/ui_local.h` against `uiQlImport_t`, then ties representative
slots back to concrete `data_106b40a8 + offset` HLIL evidence.

## Qmenu Leaf Follow-Up

The advert leaf chain under `src/code/ui/ui_shared.c` is now bounded well enough
to treat it as a stable `ui_main.c` dependency rather than an open widget-core
unknown:

- `Menu_PostParse` calls `Menu_SetupAdvertCellShaders` after final menu
  positioning, matching the retail `Menu_SetupAdvertCellShaders @ 0x100154E0`
  role from the symbol map.
- `Menus_CloseByName`, `Menus_CloseAll`, and `Menus_Activate` call
  `Menu_RefreshAdvertCellShaders`, matching the retail
  `Menu_RefreshAdvertCellShaders @ 0x100155A0` refresh role.
- `Item_UpdateAdvertShader` is a source-side factoring of the retail setup and
  refresh loops. It filters `UI_ADVERT` items, computes the current rect, sends
  hidden/non-forced refreshes through the zero-rect sentinel path, and falls back
  to `registerShaderNoMip(defaultContent)` when the host bridge returns no
  shader.
- `Script_ActivateAdvert` matches the mapped `Script_ActivateAdvert @
  0x10016AD0`: parse one integer token, call `DC->activateAdvert`, and clear the
  current item's focus bit.
- `Script_Exec` now calls `UI_HandleDeferredScriptExec` before dispatching
  `exec` text. That is a policy compatibility wrapper around retail browser
  verbs, not a new retail native branch.

Two observations matter for future source work:

1. The retail `Menu_Paint @ 0x1001D7B0` and `Menu_PaintAll @ 0x100203A0`
   paths refresh advert cells from the paint path itself. Hidden, non-forced
   menus clear the forced bit and call `Menu_RefreshAdvertCellShaders`; visible
   menus pass the ownerdraw-visible gate, require `web_browserActive == 0`, then
   refresh advert cells before preset-list update and item paint.
2. The slot-83 advert update callback remains opaque by design. Source sends
   `(shader, pixelArea)` as the closest local proxy for the retail opaque token
   and area pair, while the host side documents the provider as an inert retail
   stub in the default build.

## Paint-Path Follow-Up

The third pass closed the remaining advert-paint question rather than keeping a
transition-only refresh contract:

- `src/code/ui/ui_shared.c` now has a bounded `Menu_WebBrowserActive` helper
  that reads the same `web_browserActive` cvar observed in the retail decompile.
- `Menu_Paint` now mirrors retail hidden-menu behavior by clearing
  `WINDOW_FORCED`, calling `Menu_RefreshAdvertCellShaders`, and returning when a
  menu is neither visible nor force-painted.
- Visible paint now checks the browser-active gate before force-painting,
  advert refresh, `Menu_UpdatePresetLists`, and the existing draw path.
- Source `Menu_PaintAll` delegates through `Menu_Paint`, so the recovered
  retail `Menu_PaintAll` refresh behavior is covered without duplicating the
  loop body.

## Browser-Active Latch Follow-Up

The fourth pass tightened the `ui_main.c` side of the same paint gate. Retail
uses `web_browserActive` as a live browser-host state signal: when it is set,
`Menu_Paint`/`Menu_PaintAll` suppress native menu paint because an Awesomium
surface is expected to be present.

Current source now preserves that meaning in compatibility builds:

- `UI_MenuFlowUsesBrowserOverlay` returns true only when the selected flow is
  Quake Live and `UI_BrowserOverlayAvailable` confirms a real overlay provider.
- `UI_SetActiveMenuFlow`, `UI_LoadMenus`, and the `UIMENU_MAIN` activation path
  now publish `web_browserActive 1` only through that helper.
- The no-overlay/no-bridge fallback can still load Quake Live menu files, but it
  no longer tells `Menu_Paint` to hide the native menu surface.
- Direct `web_showBrowser` script handling still raises the active latch only
  after the overlay-available check succeeds.

## Centered Text Follow-Up

The fifth pass compared the retail `Text_PaintCenter @ 0x100105F0` helper and
the final advertisement/connect-screen export tail against the current source.
Retail measures the string width, subtracts half of it from the caller-supplied
center point, and calls `Text_Paint` with style `0`.

Current source now mirrors that smaller helper exactly:

- `Text_PaintCenter` ignores the legacy `adjust` parameter, calls
  `Text_Width(text, scale, 0)`, and paints with style `0` instead of forcing
  `ITEM_TEXTSTYLE_SHADOWEDMORE`.
- The `UI_DrawConnectScreen` startup/connecting lines now pass `0` through the
  centered helper, matching the retail helper call shape recovered from
  `UI_DrawConnectScreen @ 0x10010E30`.
- `UI_DrawAdvertisementWaitScreen` already matched the retail direct centered
  layout: optional forced menu paint, then `"Waiting on Advertisement"` at
  `y=178` and `"Press ESC to cancel"` at `y=440`.

## Download Progress Follow-Up

The sixth pass revisited the connect/download helper cluster:

- `UI_ReadableSize @ 0x100103F0` already matched the retail decimal MB/GB
  formatter: whole bytes and KB, plus `.%02d MB` or `.%02d GB` suffixes for
  larger values.
- `UI_PrintTime @ 0x10010540` already matched the retail thresholds: values
  above 3600 seconds use hours/minutes, values above 60 seconds use
  minutes/seconds, and the rest use seconds.
- `UI_DisplayDownloadInfo @ 0x100108D0` was the remaining drift. The source was
  still taking the native connect-screen byte counts directly from
  `cl_downloadCount` and `cl_downloadSize`, while retail reads
  `cl_downloadItem`, parses it as a 64-bit item id, calls import slot 96, and
  formats the returned downloaded/total values.

Current source now mirrors the native retail handoff:

- The native branch reads `cl_downloadItem`, uses the same loose `%llu` parse,
  splits the id into low/high words, and calls `trap_QL_GetItemDownloadInfo`.
- The transfer-rate and ETA math now carries the downloaded/total values as
  `unsigned long long`, matching the recovered `__allmul` / `__aulldiv` shape.
- The older `cl_downloadCount` / `cl_downloadSize` cvar path remains only under
  `Q3_VM`, where the native Quake Live import slab is not available.

## Connect Cancel Prompt Follow-Up

The seventh pass revisited the final `UI_DrawConnectScreen @ 0x10010E30`
status tail. Retail reaches the final centered text call for the non-download
`CA_CONNECTING`, `CA_CHALLENGING`, and no-download `CA_CONNECTED` states:

- It draws the current wait status at `y=210` for non-localhost servers.
- It then draws the literal `"Press ESC to cancel"` at `y=440` with the same
  center point and `0.5` scale.
- The prompt is not reached for the download-info early return, `CA_LOADING`,
  `CA_PRIMED`, other default returns, or overlay calls, matching the existing
  source control-flow exits.

Current source now restores that prompt in `UI_DrawConnectScreen`, closing the
old placeholder-only comment at the end of the connection status path.

## Keybind Prompt Follow-Up

The eighth pass moved one layer up into the display-context ownerdraw helpers
that `ui_main.c` installs during `_UI_Init`:

- `UI_OwnerDrawWidth @ 0x10006950` handles `UI_KEYBINDSTATUS` by choosing
  between the normal keybind help string and the pending-bind prompt before
  measuring width.
- `UI_DrawKeyBindStatus @ 0x100092F0` uses the same pending-bind predicate and
  paints the chosen string through the normal `Text_Paint` path.
- Both retail paths reference the same string-table literal:
  `"Waiting for new key... Press ESCAPE to cancel"`.

Current source now uses that exact retail pending-bind prompt in both the width
helper and the paint helper. This keeps menu layout measurement and rendered
text aligned instead of preserving the shorter GPL-era `"Press ESC..."` text.

## Crosshair Color Handle-Key Follow-Up

The ninth pass stayed in the display-context ownerdraw key bridge and compared
`UI_OwnerDrawHandleKey @ 0x1000A820` against the retail HLIL/Ghidra body:

- The `UI_REDBLUE`, `UI_CROSSHAIR`, and `UI_SELECTEDPLAYER` lanes call their
  helpers and return `0`, matching the current source's ignored helper return.
- Retail case `0x226` (`UI_CROSSHAIR_COLOR`) first reads
  `cg_crosshairHealth` through the display-context cvar-value import.
- It only delegates to `UI_CrosshairColor_HandleKey` when that value is `0`;
  otherwise it falls through to the default `0` return without changing
  `cg_crosshairColor`.

Current source now preserves that health-color gate before advancing the
numbered crosshair color palette. This keeps manual color cycling disabled
while crosshair health coloring owns the active color, matching the recovered
native callback behavior.

## Verification

Focused UI parity and menu tests were run without launching the game:

```text
pytest tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_menu_files.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py -q --tb=short
56 passed, 2 skipped
```

The native-slot/qmenu follow-up then reran the UI suite plus the workshop
progress bridge coverage:

```text
pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py -q --tb=short
60 passed, 2 skipped
```

The paint-path correction was then verified with the menu parity file and the
existing widescreen `Menu_Paint` guard:

```text
pytest tests/test_ui_menu_files.py tests/test_cgame_displaycontext_parity.py::test_ui_shared_widescreen_rect_flow_retargets_centered_ui_scale -q --tb=short
46 passed
```

The full focused UI gate was rerun after the correction:

```text
pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py -q --tb=short
61 passed, 2 skipped
```

The browser-active latch correction was then covered through the menu and
platform-service lanes:

```text
pytest tests/test_ui_menu_files.py tests/test_platform_services.py -q --tb=short
121 passed
```

The final run for this pass included the focused UI gate, platform-service
coverage, and the browser host parity tests:

```text
pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
149 passed, 2 skipped
```

The centered text helper correction was then checked through the menu parity
file and the focused UI/browser/platform suite:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
46 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
150 passed, 2 skipped
```

The download progress correction was then covered by the menu parity file,
client workshop bootstrap assertions, platform-service bridge assertions, and
the focused UI/browser parity suite:

```text
pytest tests/test_ui_menu_files.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py -q --tb=short
127 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
151 passed, 2 skipped
```

The connect cancel prompt correction was then covered through the menu parity
file and the broader focused UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
47 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
151 passed, 2 skipped
```

The keybind prompt correction was then covered through the menu parity file and
the broader focused UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
48 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
152 passed, 2 skipped
```

The crosshair color handle-key correction was then covered through the menu
parity file and the same broader focused UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
49 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
153 passed, 2 skipped
```

No runtime/game launch was needed for this round because the question was static
wiring and parity-gate evidence.

## Findings And Next Work

1. The current source wiring is consistent with the recovered native retail
   table and import slab. The applied source corrections cover advert paint
   refresh, browser-active latching, centered connect text, and native download
   progress ownership, connect/keybind prompt literals, and the crosshair-color
   handle-key health-color gate.
2. The live-service UI lanes should continue to be documented as bounded
   compatibility, not closed retail live-service parity, unless a future task
   replaces the default-disabled Awesomium/Steam behavior with a documented open
   equivalent.
3. The previously suggested qmenu advert-leaf pass is now closed for the
   `Menu_SetupAdvertCellShaders`, `Menu_RefreshAdvertCellShaders`, and
   `Script_ActivateAdvert` chain. The remaining qmenu risk is broader widget
   behavior outside this advert path.
4. The previously suggested `UI_QL_IMPORT_*` 80-96 ledger is now refreshed. The
   only slot still intentionally opaque is slot 83, where both source and host
   keep the advert-update token bounded instead of inventing a false live-service
   meaning.
5. A useful next reverse-engineering slice would move outside this advert path
   into broader qmenu widget paint behavior, where several helpers are still
   mapped only at a role level.
6. The menu-flow/browser-active interaction is now bounded: Quake Live menu
   flow alone does not imply an active browser surface in default-disabled
   compatibility builds.
7. The native export-tail text helpers now keep the recovered retail plain-text
   style instead of forcing shadowed centered text from the compatibility
   source.
8. The connect-screen download progress path now uses the recovered native
   `cl_downloadItem` -> import 96 handoff instead of sourcing the native path
   from legacy byte-count cvars.
9. The connect-screen non-download status tail now restores the retail
   `"Press ESC to cancel"` prompt at `y=440`.
10. The keybind pending-state ownerdraw width and paint helpers now share the
    recovered retail `"Waiting for new key... Press ESCAPE to cancel"` prompt.
11. The `UI_CROSSHAIR_COLOR` key handler now respects retail's
    `cg_crosshairHealth == 0` guard before advancing `cg_crosshairColor`.

## Parity Estimate

Before this round: **99% UI source/wiring parity confidence**. The module was
already marked closed by prior ledgers, but this round still had open audit risk
around whether later compatibility glue drifted away from recovered retail
ownership.

After this round: **99.5% UI source/wiring parity confidence**. The focused gate
is green, the native export/import wiring still matches the committed retail
corpus, and the remaining uncertainty is bounded to live-service policy lanes
and future qmenu/widget leaf promotion rather than current `ui_main.c` behavior.

After the native-slot/qmenu follow-up: **99.6% UI source/wiring parity
confidence**. The remaining uncertainty is no longer the slot table or advert
leaf ownership; it is limited to the intentionally bounded live-service
providers and the choice to refresh advert shaders on menu state transitions
rather than every paint pass in the default compatibility source.

After the paint-path follow-up: **99.7% UI source/wiring parity confidence**.
The remaining uncertainty is no longer the advert paint refresh cadence; it is
limited to the default-disabled live-service provider behavior and broader qmenu
widget leaves outside the audited `ui_main.c` dependency chain.

After the browser-active latch follow-up: **99.8% UI source/wiring parity
confidence**. The remaining uncertainty is limited to intentionally
default-disabled live-service behavior and qmenu/widget leaves outside the
audited `ui_main.c` bridge.

After the centered text follow-up: **99.85% UI source/wiring parity
confidence**. Remaining uncertainty is now concentrated in deliberately bounded
online-service behavior and lower-priority qmenu/widget leaves, not in the
audited `ui_main.c` native export tail.

After the download progress follow-up: **99.9% UI source/wiring parity
confidence**. The remaining uncertainty is concentrated in intentionally
bounded online-service provider behavior and lower-priority qmenu/widget leaves,
not in the audited `ui_main.c` connect/export/native-import handoff.

After the connect cancel prompt follow-up: **99.92% UI source/wiring parity
confidence**. Remaining uncertainty is now mostly outside the audited native
connect/export tail, in default-disabled online-service behavior and broader
qmenu/widget leaves.

After the keybind prompt follow-up: **99.94% UI source/wiring parity
confidence**. Remaining uncertainty is concentrated in lower-priority qmenu
widget leaves and intentionally bounded live-service providers, not in the
audited `ui_main.c` display-context callback strings.

After the crosshair color handle-key follow-up: **99.96% UI source/wiring
parity confidence**. Remaining uncertainty is concentrated in lower-priority
qmenu widget leaves and intentionally bounded live-service providers, not in
the audited `ui_main.c` display-context callback routing.
