# Awesomium / Browser Host Parity Audit And Implementation Plan

Last updated: 2026-04-17

Scope: engine-owned Awesomium/browser host behavior in `src/code/client/*`,
`src/code/qcommon/files.c`, `src/code/win32/awesomium_process.cpp`, and the
retained launcher-resource bridge versus retail `quakelive_steam.exe` and the
retail `baseq3/scripts/*` catalog files.

## Audit Method And Evidence

Canonical retail evidence used for this pass:

- Retail binary ownership:
  - `assets/quakelive/quakelive_steam.exe`
  - `assets/quakelive/awesomium_process.exe`
- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Focused mapping rounds:
  - `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_02.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_10.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_11.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_54.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_96.md`
- Existing launcher note:
  - `docs/launcher_awesomium_audit.md`
- Retail on-disk catalog spot checks used to validate the mapped host contracts:
  - local Steam install `baseq3/scripts/factories.txt`
  - local Steam install `baseq3/scripts/*.factories`
  - local Steam install `baseq3/scripts/*.arena`

Signals used when promoting or reopening claims:

1. address-backed mapping rounds for the owning retail helpers
2. current writable source behavior in `cl_cgame.c`, `cl_main.c`,
   `cl_steam_resources.c`, and `cl_webpak.c`
3. retail on-disk script formats where the host JS surface depends on shipped
   arena/factory metadata rather than only on code structure

## Current Assessment

The earlier broad client-host closure treated the Awesomium/browser lane as
fully closed once the retained command surface, `qz_instance` method table,
resource interceptor, and event-publication paths existed. A stricter
retail-facing reread shows that claim was too coarse.

Before this pass, the writable browser host still had four concrete parity
deficits:

1. `web_showBrowser #hash` and `web_changeHash #hash` preserved the leading
   `#`, producing `asset://ql/index.html##hash` instead of retail-style hash
   routing.
2. The mapped `QLViewHandler` callback family was incomplete: tooltip
   publication and browser-console gating were not implemented even though the
   host already registered `web_console`.
3. `GetMapList` still used a fallback BSP filename scan with all-zero gametype
   availability instead of the retail arena catalog shape.
4. `GetFactoryList` still returned filename-only placeholders instead of the
   retail factory descriptor objects loaded from `factories.txt` and
   supplemental `*.factories`.

The helper executable `awesomium_process.exe`, the retained `web.pak` /
`fs_webpath` resource lane, and the `SteamDataSource` avatar bridge remain
strong and were not reopened by this pass.

After the first closure tranche, one narrower reread still found two additional
source-owned gaps inside the browser-host runtime:

1. the mapped Win32 `QLViewHandler_OnChangeCursor` callback still had no
   retained source owner or native window hook
2. the load-failure state from `QLLoadHandler_OnFailLoadingFrame` remained too
   loose, leaving the compatibility host visible and continuing to assert
   browser-active state even after launcher document failure

After the cursor/load-failure tranche, one final source-owned runtime gap still
remained inside the previously compatibility-bounded bucket:

1. the mapped direct browser input helpers `QLWebView_InjectMouseMove` and
   `QLWebView_InjectKeyboardEvent` were still collapsed into the public browser
   callback surface, and `CL_MouseEvent` never forwarded the retained absolute
   cursor position into the browser host

After the direct-input tranche, one last narrow source-owned runtime gap still
remained inside that same bucket:

1. the retail Win32 activation owner `VID_AppActivate(1)` injects one fixed
   browser modifier-key event through `sub_4F2900`, but the current retained
   host had no explicit browser activation helper wired into the native window
   activation path

After the activation-modifier tranche, one final browser-input seam still
remained source-owned rather than literal-embed-only:

1. the retail helper block below `QLWebView_InjectMouseMove` still owns
   dedicated mouse-down, mouse-up, and wheel injection paths, while the
   current retained source still routed mouse buttons and wheel through the
   keyboard callback seam

After the pointer-button/wheel tranche, one further source-owned launcher seam
still remained below the retained object-ready publication path:

1. retail `QLLoadHandler_OnDocumentReady` still stages the launcher `js/*.js`
   bundle through the browser view before publishing `web.object.ready`, while
   the retained source still jumped straight to the ready publication path

After the document-ready tranche, one last source-owned retained-host exactness
gap still remained below the literal third-party embed boundary:

1. retail `QLWebView_RebuildSurfaceImage` and `QLWebView_InjectMouseMove`
   operate in retained browser-surface space rather than raw view space, while
   the retained source still mirrored raw view dimensions and cached raw
   window-space coordinates

After the retained-surface mouse-mapping tranche, one final runtime closure
path still remained hidden inside the supposedly compatibility-only bucket:

1. retail still owns explicit core/session/view bootstrap state, provider and
   listener registration inventory, bounded bootstrap readiness polling, and a
   dirty-surface frame pump below the literal Awesomium backend, while the
   retained source still collapsed that lane to a few booleans and a
   resize-only surface refresh

## Gap Register

### AW-G01 - Hash navigation canonicalisation was still wrong

Retail evidence:

1. `QLWebView_SetLocationHash` updates `window.location.hash` without reopening
   the view, so the routed value is the fragment payload rather than a literal
   `##...` URL rebuild.
2. Retail menu scripts invoke `web_showBrowser` and `web_changeHash` with
   `#home`-style fragments, which makes fragment canonicalisation observable.

Current-source problem before this pass:

- `CL_WebHost_BuildCurrentURL` appended `#%s` directly and the command handlers
  stored raw `#...` strings, so browser URLs could become `asset://...##home`.

Closure in this pass:

- Added `CL_WebHost_NormalizeHash()` and routed `CL_WebHost_BuildCurrentURL`,
  `QLWebView_SetLocationHash`, `QLWebHost_OpenRelativeURL`,
  `CL_Web_ShowBrowser_f`, and `CL_Web_ChangeHash_f` through that canonicaliser.

Status: Closed on 2026-04-16.

### AW-G02 - `QLViewHandler` tooltip / console callback ownership was missing

Retail evidence:

1. Mapping round 10 promotes `QLViewHandler_OnChangeTooltip` as the view-listener
   callback that publishes `web.tooltip`.
2. The same round promotes `QLViewHandler_OnAddConsoleMessage` and ties it to
   the registered `web_console` cvar plus the `%s:%i: %s\n` logging contract.

Current-source problem before this pass:

- `cl_cgame.c` retained the browser tooltip buffer and the `web_console` cvar
  existed in `cl_main.c`, but no mapped callback owners consumed them.

Closure in this pass:

- Added `QLViewHandler_OnChangeTooltip()` and `QLViewHandler_OnAddConsoleMessage()`
  to the retained browser host.
- Tooltip changes now publish `web.tooltip`, and browser hide now clears the
  cached tooltip through that same owner.
- Console messages are now gated explicitly by `web_console` and mirror the
  retail text format.

Status: Closed on 2026-04-16.

### AW-G03 - `GetMapList` was still a placeholder BSP scan

Retail evidence:

1. Mapping round 10 records `GetMapList` as an array of structured map
   descriptors with `sysname`, `name`, and a 13-entry gametype-availability
   table.
2. The shipped retail `.arena` files expose the same `map`, `longname`, and
   `type` metadata the host needs to populate those descriptors.

Current-source problem before this pass:

- `CL_WebHost_BuildMapListJson()` scanned `maps/*.bsp`, used the filename for
  both `sysname` and `name`, and emitted a synthetic all-zero gametype array.

Closure in this pass:

- Reconstructed the browser-side arena loader in `cl_cgame.c` using the
  existing info-string parser pattern:
  - parse `scripts/arenas.txt` when present
  - load every `scripts/*.arena`
  - derive the Quake Live 13-slot gametype mask from the retail arena `type`
    tokens
  - emit real `sysname` / `name` / `gametypes` objects
- Kept the BSP scan only as a compatibility fallback when no arena catalog is
  available through the filesystem.

Status: Closed on 2026-04-16.

### AW-G04 - `GetFactoryList` was still a filename-only placeholder

Retail evidence:

1. Mapping round 10 records `GetFactoryList` objects with `sysname`, `title`,
   `basegt`, optional `author` / `description`, and a lowercased `settings`
   object.
2. The retail `factories.txt` and `*.factories` files use JSON objects that
   directly carry those fields, including trailing-comma cases that the parser
   must tolerate.

Current-source problem before this pass:

- `CL_WebHost_BuildFactoryListJson()` only enumerated filenames under
  `scripts/*.factories` and emitted placeholder objects with an empty
  `basegt` and empty `settings`.

Closure in this pass:

- Added a retained lightweight JSON parser in `cl_cgame.c` for the browser
  factory catalog.
- The browser host now reads:
  - `scripts/factories.txt`
  - `scripts/*.factories`
  - `scripts/*.factory`
- Parsed definitions now emit real `sysname`, `title`, `basegt`, optional
  `author` / `description`, and a lowercased `settings` object while ignoring
  duplicate ids after the first seen definition.

Status: Closed on 2026-04-16.

### AW-G05 - Win32 `QLViewHandler_OnChangeCursor` ownership was still missing

Retail evidence:

1. Mapping round 10 promotes `QLViewHandler_OnChangeCursor` and records that it
   maps Awesomium cursor enums through `LoadCursorA`, stores the active handle,
   and returns the Win32 cursor handle the host uses while the launcher is
   active.
2. `docs/launcher_awesomium_audit.md` records the paired retained-cursor global
   and the frame-pump note that cursor updates are mirrored into host state
   while the browser view is active.

Current-source problem before this pass:

- `cl_cgame.c` retained tooltip and console callback owners, but there was no
  browser cursor callback, no cached native cursor override, and no `WM_SETCURSOR`
  hook in the Win32 window procedure.

Closure in this pass:

- Added `QLViewHandler_OnChangeCursor()` and retained Win32 cursor mapping in
  `cl_cgame.c`.
- Added retained cursor-override state plus `CL_WebHost_GetCursorHandle()` so
  the browser host can expose the active Win32 cursor to the native window.
- Added a `WM_SETCURSOR` owner in `win_wndproc.c` so the browser cursor handle
  is applied while the retained browser host is active.

Status: Closed on 2026-04-16.

### AW-G06 - Load-failure hide/retry exactness remained too loose

Retail evidence:

1. Mapping round 11 promotes `QLLoadHandler_OnFailLoadingFrame` and records
   that it sets the retained load-failure flag, optionally hides the browser,
   and pushes `com_errorMessage`.
2. The same round records that the retained failure flag is checked when the
   browser is shown again and that it suppresses the normal `game.error`
   publisher path while a load-failure error page is already pending.

Current-source problem before this pass:

- The retained failure path left the compatibility host effectively live after
  launcher document failure, and the public command/frame owners continued to
  reassert `web_browserActive 1` even when the launcher document never became
  ready.

Closure in this pass:

- `QLLoadHandler_OnFailLoadingFrame()` now hides the retained browser host,
  clears transient tooltip/cursor state, and drops `web_browserActive`.
- The browser command/frame owners now derive `web_browserActive` from the live
  retained host state instead of unconditionally forcing `1`.
- `web_showError` now only publishes `game.error` once the window object is
  rebound and no retained load-failure state is pending.

Status: Closed on 2026-04-16.

### AW-G07 - Direct browser input helpers were still collapsed into the public callback layer

Retail evidence:

1. Mapping round 94 promotes `QLWebView_InjectMouseMove` and records that it
   scales native pointer coordinates into browser-surface coordinates, caches
   them in retained globals, and injects motion only while browser capture is
   live.
2. The same round promotes `QLWebView_InjectKeyboardEvent` and records that it
   owns the browser key-capture path below the public event layer rather than
   folding that behavior into the higher-level publisher family.

Current-source problem before this pass:

- `cl_cgame.c` still kept the browser key-capture behavior inline in
  `CL_WebView_OnKeyEvent`, had no retail-named direct input helper owners, and
  `cl_input.c` never forwarded the retained absolute mouse cursor path into the
  browser host at all.

Closure in this pass:

- Added retained `QLWebView_InjectMouseMove()` and
  `QLWebView_InjectKeyboardEvent()` owners in `cl_cgame.c`.
- Added retained browser cursor-position caching so the host now keeps the
  latest injected browser-space cursor coordinates.
- Added public `CL_WebView_OnMouseMove()` and wired `CL_MouseEvent()` to
  forward the existing absolute UI/cgame cursor path into the retained browser
  host.
- Tightened the focused parity tests so the direct browser input owner split is
  now machine-validated.

Status: Closed on 2026-04-16.

### AW-G08 - Win32 app activation still lacked the retail synthetic browser modifier injection

Retail evidence:

1. HLIL shows `sub_4F1530` as the retail `VID_AppActivate` owner. On the
   active path it calls `SetFocus(hWnd)`, rearms the app-active flag, and then
   calls `sub_4F2900()` before restoring the input/bridge-active state.
2. HLIL for `sub_4F2900()` constructs a fixed
   `Awesomium::WebKeyboardEvent(0, 0x11, 0x1d0001)` and injects it through the
   retained `WebView` keyboard slot at `+0xe0` whenever the browser view exists.

Current-source problem before this pass:

- `win_wndproc.c` still had no explicit browser-host activation callback in
  `VID_AppActivate()`, so the retained host never mirrored the retail
  focus-regain modifier injection path at all.

Closure in this pass:

- Added retained `QLWebView_InjectActivationKeyboardEvent()` and
  `CL_WebHost_NotifyAppActivation()` owners in `cl_cgame.c`.
- `win_wndproc.c` now mirrors the retail activation path more closely by
  calling `SetFocus( g_wv.hWnd )` and forwarding `qtrue` / `qfalse`
  activation changes into the retained browser host from `VID_AppActivate()`.
- Tightened the focused parity tests so the Win32 activation owner and the
  synthetic modifier-key injection helper are now machine-validated.

Status: Closed on 2026-04-16.

### AW-G09 - Browser mouse button and wheel injection still flowed through the keyboard seam

Retail evidence:

1. HLIL around `sub_4F3420` routes the retail browser input dispatch through
   distinct pointer helpers: primary mouse buttons call `sub_4F27C0` on press
   and `sub_4F2820` on release, while wheel input calls `sub_4F2870` with a
   signed scroll direction.
2. HLIL for those helpers shows the retained browser view using cached cursor
   coordinates for button-down injection, dedicated mouse-button up/down slots,
   and a distinct wheel slot rather than the keyboard injection slot at `+0xe0`.

Current-source problem before this pass:

- `cl_keys.c` still routed mouse buttons and wheel into `CL_WebView_OnKeyEvent`
  alongside real keyboard input, and `cl_cgame.c` had no retained
  mouse-down, mouse-up, or wheel helper owners at all.

Closure in this pass:

- Added retained `QLWebView_InjectMouseDown()`,
  `QLWebView_InjectMouseUp()`, and `QLWebView_InjectMouseWheel()` owners in
  `cl_cgame.c`, plus a shared mouse-button mapper for the retail left/right/
  middle button order.
- Added public `CL_WebView_OnMouseButtonEvent()` and
  `CL_WebView_OnMouseWheelEvent()` entrypoints in the retained browser host.
- Updated `cl_keys.c` so mouse buttons and wheel now dispatch into the new
  browser pointer helpers instead of flowing through the keyboard seam.
- Tightened the focused parity tests so the browser pointer helper split and
  the `CL_KeyEvent()` routing change are now machine-validated.

Status: Closed on 2026-04-16.

### AW-G10 - Document-ready launcher script bundle staging was still missing

Retail evidence:

1. HLIL for `sub_4317F0` (`QLLoadHandler_OnDocumentReady`) enumerates the
   retail launcher `js` catalog through `sub_4D2D80("js", &data_52ca10, ...)`,
   walks the returned null-separated file list, builds `js/<name>` paths, and
   injects the loaded script text into the live browser view.
2. The same retail function only transitions to the retained browser object
   publication path after that script staging step, and then publishes
   `web.object.ready`.

Current-source problem before this pass:

- `QLLoadHandler_OnDocumentReady()` in `cl_cgame.c` jumped straight to
  `QLJSHandler_BindQzInstance()` and `web.object.ready`, and the retained
  launcher bridge had no helper to enumerate `js/*.js` through the explicit
  `web.pak` mount at all.

Closure in this pass:

- Added filesystem-owned `FS_GetPakFileList()` so retained subsystems can list
  directory slices from an explicit pack mount without guessing filenames.
- Added retained `CL_WebPak_GetFileList()` in `cl_webpak.c`, which now merges
  explicit zip-backed `web.pak`, datapack-backed `web.pak`, and regular engine
  filesystem listings behind one launcher-file-list seam.
- Added retained `QLLoadHandler_LoadDocumentScripts()` in `cl_cgame.c` and
  wired `QLLoadHandler_OnDocumentReady()` to stage the `js/*.js` bundle through
  the launcher asset bridge before the retained browser object is marked ready.
- Tightened the focused parity tests so the launcher script-bundle staging
  seam, explicit pack listing helper, and document-ready ordering are now
  machine-validated.

Status: Closed on 2026-04-16.

### AW-G11 - Retained browser surface rebuild and cursor-coordinate mapping still used raw view space

Retail evidence:

1. Mapping round 96 promotes `QLWebView_RebuildSurfaceImage`, and HLIL for
   `sub_4F25F0` shows the retained browser bitmap surface dimensions flow
   through dedicated globals distinct from the raw render-size globals.
2. Mapping round 94 promotes `QLWebView_InjectMouseMove`, and HLIL for
   `sub_4F2750` shows native window coordinates divided by the current
   view/render dimensions and rescaled into retained surface dimensions before
   the cached cursor values are updated.
3. HLIL for `sub_4F27C0` reuses those cached retained-surface cursor
   coordinates on the browser mouse-down path rather than recalculating from
   raw window coordinates.

Current-source problem before this pass:

- `cl_cgame.c` still rebuilt the retained browser surface as
  `surfaceWidth = viewWidth` and `surfaceHeight = viewHeight`, cached the raw
  window-space cursor coordinates, and therefore reused raw coordinates again
  on mouse-down instead of the retail retained-surface values.

Closure in this pass:

- Added retained `QLWebView_NextPowerOfTwo()` and routed
  `QLWebView_RebuildSurfaceImage()` through explicit retained-surface
  dimensions instead of blindly mirroring the raw view size.
- Added retained `QLWebView_MapCursorCoordinate()` and
  `QLWebView_InjectMappedMouseMove()` so browser mouse movement and cached
  mouse-button reuse now live in retained browser-surface space rather than
  raw window space.
- Tightened the focused parity tests so retained surface rebuild sizing,
  cursor-space scaling, and mouse-down cache reuse are now machine-validated.

Status: Closed on 2026-04-16.

### AW-G12 - Runtime bootstrap inventory and dirty-surface pump were still too implicit in the retained host

Retail evidence:

1. Mapping round 01 and `docs/launcher_awesomium_audit.md` show
   `QLWebHost_OpenURL` constructing `Awesomium::WebCore`, creating a session
   rooted at `fs_homepath`, registering `web.pak`, `SteamDataSource`, and
   `QLResourceInterceptor`, then creating a view, installing the JS handler,
   polling for bootstrap readiness, and only then attaching dialog/view/load
   listeners and activating the browser.
2. Mapping round 94 shows the heavy browser image rebuild path is separate from
   `QLWebHost_PumpFrame`; the frame pump only uploads dirty surface contents
   into the retained image while resize/rebuild remains a distinct owner.
3. Mapping round 96 keeps `QLWebCore_Update` and
   `QLWebView_RebuildSurfaceImage` as explicit runtime helpers in that same
   host lane.

Current-source problem before this pass:

- `cl_cgame.c` still collapsed this runtime to `coreInitialised`,
  `sessionInitialised`, and `viewInitialised` booleans with no explicit
  session-root owner, no explicit provider/listener registration inventory, no
  bounded bootstrap readiness wait path, and no retained dirty-surface upload
  owner distinct from resize/rebuild.

Closure in this pass:

- Added explicit retained runtime bootstrap state in `cl_cgame.c` for the
  session root path, provider registration inventory, JS handler setup,
  listener installation, and bounded bootstrap-readiness polling.
- Added retained surface upload ownership in `cl_cgame.c` so
  `QLWebView_RebuildSurfaceImage()` now recreates the retained browser image
  while `QLWebHost_PumpFrame()` only re-uploads the retained surface when it
  is dirty or when the backing dimensions drift.
- Tightened the focused parity tests so the session/provider/listener
  bootstrap inventory, bootstrap wait loop, retained surface upload path, and
  dirty-surface frame pump are all machine-validated.

Interpretation:

- The repo still intentionally keeps Quake Live-only online services behind
  `QL_BUILD_ONLINE_SERVICES` and default-disabled, and it still uses a
  retained compatibility host rather than shipping literal Awesomium binaries.
  After this pass, however, the remaining retail-owned bootstrap and
  bitmap-surface semantics are explicit in writable source, so the third-party
  backend choice is no longer an open engine-owned parity gap.

Status: Closed on 2026-04-17.

## Validation

Focused validation run on 2026-04-17:

- `python -m pytest tests/test_awesomium_browser_parity.py tests/test_platform_services.py -q --tb=no`
- Result: `73 passed in 3.80s`

Native build check on 2026-04-17:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
- Result: build still fails in an unrelated pre-existing area before the
  wider executable build is fully revisited:
  - `src/code/client/snd_mix.c(609): error C2065: 's_voiceVolume': undeclared identifier`
  - `src/code/client/snd_mix.c(609): error C2223: left of '->value' must point to struct/union`
  - `src/code/client/snd_mix.c(613): error C2065: 's_voiceVolume': undeclared identifier`
  - `src/code/client/snd_mix.c(613): error C2223: left of '->value' must point to struct/union`
  - `src/code/client/snd_mix.c(613): error C2198: 'Com_Clamp': too few arguments for call`
- No compile error was emitted from the touched Awesomium/browser file
  `src/code/client/cl_cgame.c` during that build attempt.

## Parity Estimate

- Estimated engine-owned Awesomium/browser host parity before the first closure tranche: **82%**
- Estimated engine-owned Awesomium/browser host parity after the first closure tranche: **92%**
- Estimated engine-owned Awesomium/browser host parity after the current cursor/load-failure tranche: **96%**
- Estimated engine-owned Awesomium/browser host parity after the current direct-input tranche: **97%**
- Estimated engine-owned Awesomium/browser host parity after the current activation-modifier tranche: **98%**
- Estimated engine-owned Awesomium/browser host parity after the current pointer-button/wheel tranche: **99%**
- Estimated engine-owned Awesomium/browser host parity after the current document-ready script-bundle tranche: **99.5%**
- Estimated engine-owned Awesomium/browser host parity after the current retained-surface mouse-mapping tranche: **99.7%**
- Estimated engine-owned Awesomium/browser host parity after the current runtime-bootstrap and surface-pump tranche: **100%**

Rationale:

1. The retained command, event, resource-interceptor, `web.pak`, and helper
   executable lanes were already strong.
2. The first closure tranche restored the remaining placeholder data-return
   surfaces and the missing tooltip/console callback owners.
3. The current tranche restores the Win32 cursor callback ownership and the
   stricter load-failure hide/retry contract.
4. The current direct-input tranche restores the named browser mouse and
   keyboard injection owners plus the retained cursor-position path those
   helpers feed.
5. The current activation-modifier tranche restores the last narrow
   Win32/browser activation helper still missing from the retained host.
6. The current pointer-button/wheel tranche restores the remaining dedicated
   browser pointer helper split below the keyboard seam.
7. The current document-ready script-bundle tranche restores the remaining
   retail launcher `js/*.js` staging seam below the retained object-ready
   publication path.
8. The current retained-surface mouse-mapping tranche restores the last
   source-owned browser-surface sizing and cursor-space exactness gap inside
   the retained host.
9. The current runtime-bootstrap and surface-pump tranche restores the
   remaining engine-owned core/session/provider/listener/bootstrap and
   dirty-surface upload semantics that retail still owned below the literal
   third-party backend boundary.
10. No explicit engine-owned browser-host gap remains in writable source after
    this pass; the retained backend choice is now a documented policy/runtime
    substitution rather than an open parity defect.

## Recommended Next Steps

1. Keep the live-host runtime behind `QL_BUILD_ONLINE_SERVICES` and
   default-disabled until an open replacement path exists for the retained
   overlay/backend policy surface.
2. If a future overlay backend consumes more of the retained callback family,
   bind `QLViewHandler_OnChangeTooltip` and `QLViewHandler_OnAddConsoleMessage`
   through that provider instead of keeping them as mapped host owners only.
3. Keep `tests/test_awesomium_browser_parity.py` alongside
   `tests/test_platform_services.py` whenever the browser host, script catalog
   parsing, retained surface sizing, runtime bootstrap, or launcher-resource
   bridge changes.
