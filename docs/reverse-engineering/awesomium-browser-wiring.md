# Awesomium browser wiring map

This note records the current retail mapping for the Quake Live Awesomium browser host and the source reconstruction seams that correspond to it. It is intentionally scoped to evidence already committed in this repository.

## Evidence anchors

- `references/hlil/quakelive_steam.exe/00_12d640/part05.txt:11025` shows retail opening `asset://ql/index.html` when the online browser path is allowed.
- `references/hlil/quakelive_steam.exe/00_12d640/part05.txt:15880` maps the browser bootstrap function that initializes WebCore, WebSession, data sources, WebView, handlers, URL load, resume, focus, and `web_browserActive`.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:22491` maps `QLResourceInterceptor` request behavior.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:35571` maps the Awesomium-facing vtables for `QLResourceInterceptor`, dialog/view/load handlers, `QLJSHandler`, `DataPakSource`, and `SteamDataSource`.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:49745` lists the Awesomium imports used by the retail executable, including JS object/value helpers, WebCore initialization, WebView calls, BitmapSurface copy, DataSource send response, and Steam API symbols.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15728` maps `web_clearCache` to WebSession slot `0x1c`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15739` maps `web_reload` to WebSession slot `0x1c` followed by WebView slot `0x78`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15747` maps shutdown to WebView destroy plus `WebCore::Shutdown`, with no WebSession slot `0x1c` call.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:36881` is the structured companion decompile for the WebCore/WebView bootstrap.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45532` is the structured companion decompile for the resource interceptor.

## Retail bootstrap sequence

| Order | Retail behavior | Current source owner |
| --- | --- | --- |
| 1 | Gate browser startup on platform/service state, then request `asset://ql/index.html`. | `src/code/client/cl_main.c`, `src/code/client/cl_awesomium_win32.cpp` |
| 2 | Construct `Awesomium::WebConfig` and call `Awesomium::WebCore::Initialize`. | `CL_Awesomium_Startup` |
| 3 | Construct `Awesomium::WebPreferences`. Retail sets two observed local preference bytes before WebSession creation. | Reconstructed in `CL_Awesomium_PreparePreferences` as `enable_plugins = true` and `enable_web_security = false`, using SDK C API setters. |
| 4 | Create a WebSession using `fs_homepath`, then call WebSession slot `0x18`. | `CL_Awesomium_CreateSession` |
| 5 | Construct `DataPakSource("web.pak")` and add it under source host `QL`. | `CL_Awesomium_CreateSession`, `src/code/client/cl_webpak.c` |
| 6 | Construct `SteamDataSource` and add it under source host `steam`. | Offline-safe avatar/resource bridge in `src/code/client/cl_steam_resources.c`; not yet attached as a native live Awesomium data source. |
| 7 | Construct `QLResourceInterceptor` and set it on WebCore. | Request behavior reconstructed in `src/code/client/cl_steam_resources.c`; live native interceptor object is still a compatibility seam. |
| 8 | Create WebView with current video dimensions and the session. | `CL_Awesomium_Startup` |
| 9 | Construct `QLJSHandler` and install it on WebView vtable slot `0x12c`. | Source bridge reconstructs the browser-visible `qz_instance` method-name surface through startup script injection, deterministic `FakeClient.qz_instance` replacement, and a queued command/cvar native bridge. Native JSValue marshalling is still open. |
| 10 | Wait up to ten 100 ms helper iterations for browser helper initialization. | `CL_Awesomium_Startup` has equivalent polling around view initialization. |
| 11 | Install dialog, view, and load handlers on WebView slots `0x34`, `0x24`, and `0x28`. | Handler vtables are mapped; source currently uses direct host state and surface polling rather than native objects. `QLLoadHandler` document-ready script execution is projected through the live frame pump. |
| 12 | Call WebView slot `0xa0` with `1`, then load the URL through slot `0x64`. | URL load and transparent-state setup are reconstructed. |
| 13 | Resume rendering through slot `0xac`, focus through slot `0xb0`, update activation/cursor state, set `web_browserActive` to `1`, and enable key catcher. | `CL_Awesomium_OpenURL`, `CL_Awesomium_Startup`, and client-side browser host drawing/input paths. |

## Awesomium vtable and import mapping

| Retail object/API | Evidence | Source reconstruction status |
| --- | --- | --- |
| `WebSession` bootstrap slot `0x18` | HLIL bootstrap calls slot `0x18` immediately after `WebCore::CreateWebSession`. | Reconstructed only when the external SDK C API exposes optional `_Awe_WebSession_Initialize@4`; no local vtable fallback is retained. |
| `WebSession` cache-clear slot `0x1c` | HLIL `web_clearCache` calls slot `0x1c`; `web_reload` calls the same slot before WebView reload; staged and retail `awesomium.dll` export `_Awe_WebSession_ClearCache@4`. | Reconstructed through optional `_Awe_WebSession_ClearCache@4`; `_Awe_WebSession_Release@4` remains shutdown-only, and reload still follows with the SDK WebView ignore-cache flag. |
| `WebView::LoadURL` slot `0x64` | HLIL bootstrap and Awesomium import list | Reconstructed through `_Awe_WebView_LoadURL@8`. |
| `WebView::Stop` slot `0x74` | HLIL/import surface | Reconstructed through `_Awe_WebView_Stop@4`. |
| `WebView::surface` slot `0x84` | BitmapSurface copy path | Reconstructed and used by `CL_Awesomium_CopySurface`. |
| `WebView::Resize` slot `0x9c` | Video size integration | Reconstructed through `_Awe_WebView_Resize@12`. |
| `WebView::SetTransparent` slot `0xa0` | HLIL bootstrap calls slot `0xa0` with `1` before URL presentation | Reconstructed through the SDK C API export `_Awe_WebView_SetTransparent@8`. |
| `WebView::PauseRendering` slot `0xa8` | HLIL hide-browser path calls slot `0xa8` before deactivating `web_browserActive` | Reconstructed through `_Awe_WebView_PauseRendering@4`. |
| `WebView::ExecuteJavascript` slot `0x124` | Awesomium import list and retail WebView ABI layout | Reconstructed in this pass as `CL_Awesomium_ExecuteJavascript`. |
| `WebView::set_js_method_handler` slot `0x12c` | HLIL bootstrap constructs `QLJSHandler` and calls slot `0x12c`; `data_55c008` stores the 34-entry `qz_instance` method table. | Native handler object remains mapped, while the source-visible browser contract is reconstructed through the injected `qz_instance`/`FakeClient.qz_instance` bridge and native command/cvar request pump. |
| `WebView::ResumeRendering` slot `0xac` | HLIL bootstrap | Reconstructed through `_Awe_WebView_ResumeRendering@4`. |
| `WebView::Focus` slot `0xb0` | HLIL bootstrap | Reconstructed through `_Awe_WebView_Focus@4`. |
| `WebView::Unfocus` slot `0xb4` | HLIL hide-browser path calls slot `0xb4` after pause rendering | Reconstructed through `_Awe_WebView_Unfocus@4`. |
| `WebView::SetZoom` slot `0xc4` | HLIL bootstrap passes the `web_zoom` cvar integer to slot `0xc4` before rebuilding the surface | Kept as an optional SDK C API import `_Awe_WebView_SetZoom@8`; no local vtable fallback is retained. |
| Mouse input slots `0xd0` to `0xdc` | Input path reconstruction | Reconstructed through SDK C API exports. |
| `WebKeyboardEvent` / `WebView::InjectKeyboardEvent` slot `0xe0` | HLIL `sub_4f28a0` constructs `Awesomium::WebKeyboardEvent(eventType, virtualKeyCode, nativeKeyCode)` and dispatches it through WebView slot `0xe0`; the import list names `??0WebKeyboardEvent@Awesomium@@QAE@IIJ@Z`. | Reconstructed through the SDK event-object path: `_Awe_new_WebKeyboardEvent_1@12`, `_Awe_WebView_InjectKeyboardEvent@8`, and `_Awe_delete_WebKeyboardEvent@4`. |
| `BitmapSurface::CopyTo` and dirty flag | Import list | Reconstructed in surface copy/upload path. |
| `Awesomium::DataPakSource` | Retail vtable and bootstrap | Reconstructed enough to load `web.pak`; source additionally searches deterministic filesystem roots. |
| `Awesomium::DataSource::SendResponse` | Import list | Mapped; source fallback request path is implemented in `cl_webpak.c` and `cl_steam_resources.c`. |

## Handler and data source wiring

| Retail class | Retail vtable evidence | Observed purpose | Current source equivalent |
| --- | --- | --- | --- |
| `QLResourceInterceptor` | vtable at `0x00547f94` | Intercepts `asset://ql/...`; maps screenshot URLs under `<fs_homepath>/<fs_game>/screenshots/`; maps other `asset://ql/...` paths through `fs_webpath` when set; navigation filter never blocks. | `QLResourceInterceptor_RequestRetailHost`, `QLResourceInterceptor_MapRetailPath`, and `QLResourceInterceptor_OnFilterNavigation` in `src/code/client/cl_steam_resources.c`. |
| `QLDialogHandler` | vtable at `0x00547fa8` | Dialog callback surface for WebView. | Mapped only; no live native object yet. |
| `QLViewHandler` | vtable at `0x00547fc0` | View lifecycle/paint-facing notifications. | Replaced by host polling of view/surface state. |
| `QLLoadHandler` | vtable at `0x00547fe8` | Load lifecycle callbacks. | Native object remains mapped; source now projects begin/finish/document-ready state, executes recovered `js/*.js` scripts through WebView slot `0x124`, and publishes `web.object.ready`. |
| `QLJSHandler` | vtable at `0x00548010` | Handles JS method calls and query responses for the menu. | Reconstructed with a deterministic injected `qz_instance`/`FakeClient` bridge plus native command/cvar dispatch. Full native JSValue/JSObject marshalling remains open. |
| `DataPakSource` | vtable at `0x00548070` | Serves browser assets from `web.pak` under `asset://ql/`. | Reconstructed in Awesomium session setup and `cl_webpak.c`. |
| `SteamDataSource` | vtable at `0x00532b80` | Serves Steam-backed resources, especially avatar-like data. | Offline-safe source-side bridge in `cl_steam_resources.c`; live Awesomium source attachment remains intentionally bounded by `QL_BUILD_ONLINE_SERVICES`. |

## Current parity assessment for the browser host

Implemented or source-reconstructed:

- WebCore initialization and shutdown behind `QL_BUILD_ONLINE_SERVICES`.
- WebSession creation rooted in `fs_homepath`, including the post-create slot `0x18` initialization call.
- WebSession cache-clear ownership is reconstructed through the confirmed `_Awe_WebSession_ClearCache@4` export; reload clears the session cache and then uses SDK reload ignore-cache.
- `web.pak` mounting and deterministic package-path behavior for `asset://ql/index.html`.
- WebView creation, resize, URL load, render resume, focus, surface copy, dirty tracking, visible-surface gating, and dynamic texture upload.
- External SDK C API imports for the core WebView calls needed by the menu path.
- SDK-owned `WebKeyboardEvent` construction and WebView slot-`0xe0` keyboard event injection for modeled browser activation events.
- Retail WebPreferences byte writes mapped to SDK fields and reconstructed through `enable_plugins` and `enable_web_security` setters.
- Startup JS bridge for the 34-entry `qz_instance` method-name surface, deterministic `FakeClient.qz_instance` replacement, queued command/cvar dispatch, and bounded helper-readiness retries.
- `ExecuteJavascript` wrapper/fallback reconstructed at the retail WebView ABI seam.
- `QLLoadHandler_OnDocumentReady` observable behavior: recovered launcher `js/*.js` enumeration, live `ExecuteJavascript` dispatch, `qz_instance` bind, cursor reset, and `web.object.ready` publication.
- Retail-shaped resource request mapping for `asset://ql/screenshot/...` and `fs_webpath` overrides.
- Offline-safe Steam resource/avatar compatibility functions.

Mapped but not yet fully reconstructed:

- Native `QLJSHandler` with Awesomium `JSValue`, `JSArray`, and `JSObject` marshalling.
- Native `QLResourceInterceptor` object installation on the live WebCore instance.
- Native `SteamDataSource` installation into the live WebSession.
- Native dialog, view, and load handler objects; `QLLoadHandler` behavior is source-projected, but the SDK listener object is not reconstructed.
- Native hidden-view lifecycle state around the retail guard that suppresses pause/unfocus during some shutdown paths.

SDK/API export audit:

- The retail `awesomium.dll` C API exposes generated director-connect exports for
  `DataSource`, `JSMethodHandler`, `ResourceInterceptor`, `Load`, `View`, and
  `Dialog`, plus WebCore/WebView setter exports for the resource interceptor
  and view/listener slots.
- That makes native-object reconstruction a matter of wiring SDK-owned C API
  objects and callback signatures. It does not require local source to recreate
  Awesomium object layout, vtables, or decorated C++ ABI thunks.
- Source should keep using the SDK C API boundary for this lane. Any future
  native listener/data-source pass should import and verify those exports first,
  then connect small source-owned callbacks that call the already recovered
  `QL*Handler_*` and resource bridge helpers.

Confidence notes:

- High confidence: bootstrap ordering, `asset://ql/index.html`, `QL` and `steam` source names, `web_browserActive`, WebView load/resume/focus slots, resource interceptor screenshot/fs_webpath mapping.
- Medium confidence: `ExecuteJavascript` slot `0x124` and raw wide-string wrapper shape, because it is aligned with the import surface and adjacent WebView ABI pattern but still needs a retail call-site-specific cross-check before using it for more complex script injection.
- Medium confidence: slot `0xa0` as `set_transparent`, because retail passes a boolean-like `1` immediately after listener installation and before page presentation, matching the old Awesomium WebView API shape.
- High confidence: slot `0xc4` as `SetZoom`, because retail passes `web_zoom->integer` to this slot both during page open and when the cvar modified latch is set.
- High confidence: slots `0xa8` and `0xb4` as pause/unfocus, because they are paired in the hide-browser path and mirror the complementary bootstrap calls to resume/focus.

## Recommended next reconstruction cuts

1. Reconstruct the native `QLJSHandler` object and Awesomium `JSValue` / `JSArray` / `JSObject` marshalling after the source-visible method-name surface is stable.
2. Add a source-side native resource interceptor object only if live Awesomium still needs it after the `web.pak` and startup script path are stable.
3. Prioritize native `QLLoadHandler` SDK C API/director wiring before attempting the higher-risk `QLJSHandler` value-marshalling lane.
4. Keep Steam-backed data source behavior offline-first unless a documented open replacement path is chosen.

## 2026-05-28 WebSession lifecycle and cache correction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15728` shows `sub_4f2a10` loading `data_12d3044` and tail-calling WebSession slot `0x1c`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15739` shows `sub_4f2a30` calling WebSession slot `0x1c` before WebView slot `0x78` with `1`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15747` shows shutdown destroying the WebView and then calling `Awesomium::WebCore::Shutdown`; it does not call the WebSession `0x1c` slot.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15868` shows the WebSession created from `fs_homepath` and then immediately dispatched through slot `0x18`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16532` shows `web_showError` forwarding `sub_4c7ee0(1)`, the full command tail after the command name.

Source divergence found:

- The source adapter named WebSession slot `0x1c` as a release path and called it during shutdown.
- Live `web_clearCache`/reload cleared only source-side resource caches and did not dispatch to the live Awesomium WebSession cache slot.
- The post-create WebSession slot `0x18` call was documented as an object-lifetime boundary rather than reconstructed.
- `web_showError` consumed only the first token after the command name.
- Live navigation ignored an `CL_Awesomium_OpenURL` failure return, so the host could remain marked active after a failed URL dispatch.

Fix implemented:

- Added optional `_Awe_WebSession_Initialize@4` binding for WebSession slot `0x18`.
- Removed the incorrect `_Awe_WebSession_Release@4` cache-clear classification. That SDK export is now used only as session release during shutdown.
- Confirmed `_Awe_WebSession_ClearCache@4` in both the staged rebuilt runtime and the retail Steam Awesomium runtime, then wired `CL_Awesomium_ClearCache` to call it when a live WebSession exists.
- Routed `CL_Web_ClearSessionState` through `CL_Awesomium_ClearCache` before source-side resource cache clearing when live Awesomium is active.
- Switched `web_showError` to `Cmd_ArgsFrom( 1 )` and made live navigation failure publish the load-failure path.

## 2026-05-28 WebUI launch/cache/image correction

Retail evidence:

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2A10` to `CL_Web_ClearCache_f`, `sub_4F2A30` to `CL_Web_Reload_f`, `sub_4F2590` to `QLWebCore_Update`, `sub_445910` to `R_CreateImage`, `sub_458A40` to `R_GetShaderByHandle`, and `sub_4586D0` to `RE_RegisterShaderFromImage`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15587` shows the browser bitmap upload calling `R_CreateImage("browser", ...)`, retrieving the retained shader handle, and writing the new image pointer into the shader stage.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt` shows the retained browser shader registration using the literal `browserShader`.
- `dumpbin /exports` on both `build/win32/Debug/bin/awesomium.dll` and the Steam Quake Live `awesomium.dll` shows `_Awe_WebSession_ClearCache@4`, `_Awe_WebSession_Release@4`, and `_Awe_WebView_Reload@8`.

Source reconstruction:

- `ui_browserAwesomium 0` launch profiles stay authoritative through the source-side runtime request gate, so a map launch such as `campgrounds` does not bring up the WebUI runtime unless explicitly requested.
- The browser upload path now separates the retained shader handle name from the backing renderer image name. Retail uses `browserShader` plus `browser`; source uses the retail shader handle `browserShader` and the private image `*ql_web_browser` to avoid collisions with unrelated renderer image cache entries.
- `CL_RegisterShaderFromRGBAWithImageName` mirrors the retail distinction without changing existing Steam/avatar resource callers, which still use the one-name `CL_RegisterShaderFromRGBA` wrapper.
- `CL_Awesomium_ClearCache` now dispatches to `_Awe_WebSession_ClearCache@4` when a live session and export are present; `_Awe_WebSession_Release@4` is kept solely in shutdown.

## 2026-05-28 WebUI hash-navigation and overlay ownership correction

Retail/runtime evidence:

- Retail WebUI menu changes use the existing document and change only the hash;
  they do not reload `asset://ql/index.html` for every menu transition.
- A live runtime pass reproduced the source failure: navigating to Settings and
  pressing Escape hid the retained browser host, leaving only the dark
  background/copyright shell. Retail comparison shows browser-owned Escape is
  consumed as a no-op.

Source reconstruction:

- `web_changeHash` on a live Awesomium view now executes JavaScript to assign
  `window.location.hash` and rerun the bridge hook, instead of reloading the
  current URL.
- The startup script's `SendGameCommand` shim recognizes `web_changeHash`, but
  no longer installs a JavaScript Escape handler.
- `CL_KeyEvent` now returns immediately for Escape while `KEYCATCH_BROWSER` is
  set, matching the observed retail no-op.
- Overlay drawing, `KEYCATCH_BROWSER`, and `web_browserActive` publication are
  now tied to a contentful browser surface, so shell-only paints do not take over
  the native menu or game view.

## 2026-05-29 qz_instance command/cvar bridge correction

Retail/runtime evidence:

- The WebUI power button calls `qz_instance.SendGameCommand("quit")`; the local
  bundle's non-Awesomium `FakeClient` implementation only logs that call.
- `data_55c008` maps `SendGameCommand`, `GetCvar`, `SetCvar`, and `ResetCvar`
  onto `QLJSHandler`; the recovered source handlers execute commands through
  `Cbuf_ExecuteText` and cvars through `Cvar_VariableStringBuffer`, `Cvar_Set`,
  and `Cvar_Reset`.
- The startup script previously filled only missing `FakeClient.qz_instance`
  methods, so the bundle's existing fake `SendGameCommand` survived on live
  Awesomium pages and swallowed commands such as `quit`.

Source reconstruction:

- The injected `main_hook_v2` now replaces `FakeClient.qz_instance` methods with
  the source-owned qz bridge and keeps `window.qz_instance` pointed at the same
  object.
- `SendGameCommand`, `GetCvar`, `SetCvar`, and `ResetCvar` now enqueue native
  requests that the live Awesomium frame pump drains and routes through the same
  command-buffer and cvar APIs as the recovered `QLJSHandler` methods.
- The bridge uses `_Awe_WebView_ExecuteJavascriptWithResult@12` plus integer
  `JSValue` conversion to pop queued request text without claiming full native
  `JSMethodHandler` marshalling parity.
- The browser-side config/cvar cache is synchronized from native cvars and binds
  so WebUI `GetConfig` and `GetCvar` reads observe engine state instead of a
  detached JavaScript-only object.

Settings-menu parity evidence:

- The retail Settings screenshot shows native state in the first render:
  populated binds such as `w`, `SPACE`, and `CTRL, MOUSE1`, plus live cvar
  values such as `sensitivity 1.00`. The source screenshot showed fallback
  state instead: `Default`, `0.00`, and `None` for every bind.
- The shipped WebUI bundle reads `qz_instance.GetConfig()` during
  `componentWillMount`, iterates `cfg.cvars` as a name-to-value object, and
  reads each bind through `bind.key` plus `bind.value`. It subscribes to
  `cvar.*` and `bind.changed` afterward for live updates.
- The retail `GetConfig` HLIL bind loop builds bind objects with `id`, `key`,
  and `value`; `sub_4B6570(index)` supplies the same printable key name exposed
  by the source `Key_KeynumToString` helper.

Source reconstruction:

- The live Awesomium startup now receives an initial native config JSON blob
  before the injected `qz_instance` bridge exposes `GetConfig`, so the Settings
  mount path sees engine cvars and key bindings instead of the fallback object.
- The config snapshot now emits `cvars` as a JSON object and `binds` entries as
  `{ "id", "key", "value" }`, matching the WebUI bundle and the retail bind
  object literals.
- `cvar.*` and `bind.changed` events are dispatched into the live page through
  `EnginePublish`, keeping React state synchronized after WebUI cvar edits and
  bind/unbind commands.

Startup performance correction:

- A runtime pass showed the source bridge could hitch during the black
  Awesomium startup frame because the compatibility layer was reparsing the full
  native-config startup script during helper retries and polling
  `ExecuteJavascriptWithResult` every frame while the page was still settling.
- The full startup script is now used for the initial config-bearing bridge only;
  helper retries execute a tiny `main_hook_v2` script.
- The request pump is deferred after live-view creation, skipped while Awesomium
  reports the page loading, and reduced to one request per poll with idle/busy
  pacing. Initial config sync is treated as satisfied by the startup script, so
  the first frame no longer sends a second large config blob.
- Live `EnginePublish` dispatch is gated on a drawable browser surface, avoiding
  a startup event storm before the WebUI has a document ready to receive it.

## 2026-06-02 Awesomium child-process command-line correction

Runtime evidence:

- A `cdb` breakpoint on `KernelBase!CreateProcessW` during the failing WebUI
  launch showed Awesomium trying to spawn `awesomium_process.exe` with
  `--awesomium-user-script=<startup bridge...>` appended to the child command
  line.
- `CreateProcessW` returned `0` and `LastErrorValue` was Win32 `0xce` (`206`),
  "The filename or extension is too long." The failed launch was therefore not
  caused by aspect ratio; the child renderer process command line was over the
  Windows limit.

Source reconstruction:

- The startup bridge is still constructed from native player, Steam/app, cvar,
  and bind state, but it is no longer assigned to `WebConfig.user_script`.
- The bridge is injected through the existing WebView `ExecuteJavascript` retry
  path after WebView creation and URL load. This keeps the large script out of
  Awesomium's renderer child-process command line while preserving the recovered
  source-visible `qz_instance` bridge behavior.
- The child-process WebConfig path remains the retail filename
  `awesomium_process.exe` after validating that the staged helper imports
  `ChildProcessMain@Awesomium`.

## 2026-05-25 update/pump parity audit

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:27537` shows `Com_Frame` running the second event loop, executing pending commands, then calling `FUN_004f2590` before Steam callbacks and the client frame.
- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2590` to `QLWebCore_Update`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15501` shows `sub_4f2590` calling WebCore slot `0x18` and maintaining the browser keycatcher bit while `data_15ee390` is active.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15804` shows the draw/update helper rebuilding the browser surface when dimensions change, updating the GL texture when the `BitmapSurface` dirty flag is set, then clearing the dirty flag.
- Retail command registration at `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16540` includes `web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`, `web_clearCache`, and `web_reload`; it does not show a retail `web_stopRefresh` browser command.

Source divergence found:

- The source UI bridge forwards the legacy `uiScript stopRefresh` action from `src/ui/main.menu` through `web_stopRefresh` when a browser overlay is available.
- `src/ui/main.menu` runs `uiScript stopRefresh` in the main menu `onOpen` block, so the command can fire immediately after the Awesomium menu is requested.
- The previous source-side `web_stopRefresh` handler called `CL_Awesomium_Stop()` for a live Awesomium view and set `refreshStopped`.
- The previous `QLWebCore_Update` treated `refreshStopped` as a hard gate and stopped calling `CL_Awesomium_Update()`, freezing the WebCore paint/update loop.

Fix implemented:

- `QLWebCore_Update` now continues pumping WebCore once the core is initialized, matching the retail frame-pump contract.
- `CL_Web_StopRefresh_f` now treats `web_stopRefresh` as a non-destructive legacy UI/server-list stop signal for live Awesomium. It does not call `WebView::Stop`, does not latch `refreshStopped`, and marks the surface dirty so the next frame can upload the live paint.

Expected effect:

- The main menu's inherited `stopRefresh` action no longer aborts the initial `asset://ql/index.html` load.
- Awesomium can continue running JavaScript, receiving paints, and producing dirty `BitmapSurface` updates across frames instead of showing a black or stale canvas until shutdown timing changes.

## 2026-05-27 browser keycatcher activation correction

Retail evidence:

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2590` to `QLWebCore_Update`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15501` shows `sub_4f2590` checking the active browser byte and setting keycatcher bit `0x20` before dispatching WebCore slot `0x18`.
- The same HLIL block does not gate the keycatcher write on the drawable browser surface or paint-presentation state.

Source divergence found:

- The reconstructed `QLWebCore_Update` armed `KEYCATCH_BROWSER` only when `browserActive` and `surfacePresented` were both true.
- The frame loop also republished `web_browserActive` from the same surface-presented condition even after the browser was opened.
- If live Awesomium was active but the first valid paint had not reached `CL_WebHost_DrawBrowserSurface`, keyboard capture could remain disabled even though retail would already route input to the WebUI.

Fix implemented:

- `QLWebCore_Update` now arms `KEYCATCH_BROWSER` from browser-active state alone, matching the retail `sub_4f2590` condition.
- The frame loop now republishes `web_browserActive` from browser-active state alone, but the publisher first checks the existing cvar value so repeated compatibility refreshes do not re-enter `Cvar_Set2`.
- Fullscreen browser drawing still remains protected by the existing visible-surface checks, so blank-surface presentation behavior is unchanged.

## 2026-05-28 no-op bridge cvar publish guard

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` identifies `FUN_004cce90` as the 959-byte cvar setter body and `references/analysis/quakelive_symbol_aliases.json` promotes it to `Cvar_Set2`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:33429` shows the retail `Cvar_Set2: %s (%s)\n` debug print before cvar lookup and same-value filtering.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15483` and `:15927` show retail `web_browserActive` publication on hide/open transitions, not as a generic advert-bridge telemetry stream.

Source divergence found:

- The retained compatibility advert/browser bridge refreshed provider, policy, parity, and active cvars from renderer/UI bridge callbacks that can run every frame.
- Because reconstructed `Cvar_Set2` correctly prints before detecting an unchanged value, default offline builds could flood the developer console with unchanged bridge cvar writes while falling back to the main menu.

Fix implemented:

- Added `CL_SetCvarIfChanged()` for bridge telemetry publishers that mirror long-lived compatibility state.
- Routed repeated browser/advert bridge telemetry and frame-loop `web_browserActive` mirrors through that helper while keeping the retail event-style open/hide cvar writes intact.
- Added an Awesomium launch guard that refuses `-EnableAwesomium` launches when the latest build stamp says `QLBuildOnlineServices=0`, preventing accidental testing of the default offline build.

## 2026-05-28 web_* cvar cached-owner reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:32923` registers `web_browserActive` into `data_145ca50` with default `0` and flags `0x40`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16547` registers `web_zoom` into `data_12d3060` with default `100` and flags `1`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16550` registers `web_console` into `data_12d3064` with default `0` and flags `1`.
- The live WebView path checks the `web_zoom` modified byte before calling WebView slot `0xc4`, then clears that modified latch.

Source reconstruction:

- `common.c` now keeps `com_webBrowserActive` as the cached core cvar pointer and uses it in the frame idle-sleep decision.
- `cl_cgame.c` now keeps `cl_webZoom`, `cl_webConsole`, and `cl_webBrowserActive` pointers from `QLWebHost_RegisterCommands()`.
- The browser host exposes `cl_webCvarRetailMappings[]` with the recovered retail globals/defaults/flags, and live Awesomium zoom handling now consumes the cached `web_zoom` modified latch.

## 2026-05-25 WebView bootstrap slot reconstruction

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45644` shows the bootstrap calling WebView slot `0xa0` with `1` after installing dialog/view/load handlers.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45665` shows the bootstrap calling WebView slot `0xc4` with `web_zoom->integer`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15811` shows the browser draw/update path applying the same slot `0xc4` when the `web_zoom` modified bit is set.

Source reconstruction:

- Added the SDK C API export `_Awe_WebView_SetTransparent@8` for the retail slot `0xa0` behavior.
- Kept `_Awe_WebView_SetZoom@8` optional. The retail slot remains mapped, but the source no longer reconstructs a local vtable fallback when the SDK C API export is absent.
- `CL_Awesomium_Startup` now applies transparent mode immediately after WebView creation, matching the retail bootstrap position.
- `CL_Awesomium_OpenURL` applies default zoom before resume/focus.
- `QLWebCore_Update` now watches `web_zoom` and pushes changes to live Awesomium before the WebCore update tick, matching the retail cvar-modified behavior.
- Navigation and reload paths now reapply `web_zoom` after URL/reload commands.

## 2026-05-25 WebView hide/deactivation reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15474` maps the browser hide path.
- In that path, retail checks that WebCore and WebView exist, then calls WebView slot `0xa8` when the shutdown guard is clear.
- Retail then calls WebView slot `0xb4`, clears the active browser flag, sets `web_browserActive` to `0`, clears the browser keycatcher bit, and restores the cursor.

Source reconstruction:

- Added `CL_AWE_WEBVIEW_PAUSE_RENDERING_SLOT` and `CL_AWE_WEBVIEW_UNFOCUS_SLOT` wrappers to the Win32 adapter.
- Added `_Awe_WebView_PauseRendering@4` and `_Awe_WebView_Unfocus@4` dynamic import seams.
- Added public `CL_Awesomium_PauseRendering` and `CL_Awesomium_Unfocus` APIs plus disabled-build stubs.
- `QLWebHost_HideBrowser` now invokes pause/unfocus for live Awesomium before clearing source-side active/visible state, matching the retail lifecycle ordering.

Remaining caveat:

- Retail suppresses the pause-rendering call when its shutdown guard byte is set. The current source path calls pause/unfocus only through normal browser hide, while full shutdown still releases the runtime separately. That preserves the important behavioral distinction without naming the retail guard until more evidence is mapped.

## 2026-05-25 WebKeyboardEvent injection reconstruction

Retail evidence:

- `references/hlil/quakelive_steam.exe/hlil_by_address/part05.txt:15659-15671` maps `sub_4f28a0` to construction of `Awesomium::WebKeyboardEvent(eventType, virtualKeyCode, nativeKeyCode)` followed by a WebView vtable call at slot `0xe0`.
- `references/hlil/quakelive_steam.exe/hlil_by_address/part05.txt:15685-15688` shows the activation event using the retail triplet `(0, 0x11, 0x1d0001)`.
- `references/hlil/quakelive_steam.exe/hlil_by_address/part06.txt:18384` names the imported constructor as `??0WebKeyboardEvent@Awesomium@@QAE@IIJ@Z`.

Source reconstruction:

- Replaced the old four-argument pseudo export with the SDK event-object path: `_Awe_new_WebKeyboardEvent_1@12`, `_Awe_WebView_InjectKeyboardEvent@8`, and `_Awe_delete_WebKeyboardEvent@4`.
- Removed the local object-storage constructor/vtable fallback so `WebKeyboardEvent` lifetime remains owned by the external SDK.
- Added `CL_Awesomium_InjectKeyboardEvent` and wired `QLWebView_InjectKeyboardEventFields` to forward the preserved `{ eventType, virtualKeyCode, nativeKeyCode }` triplet when live Awesomium is active.

Remaining caveat:

- The current source-side key path still only models the retail activation event at full field fidelity. General per-key browser input should be reconstructed from the broader key-event caller before expanding beyond the observed triplet.

## 2026-05-25 QLJSHandler and qz_instance bootstrap reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16009-16011` shows retail constructing a four-byte `QLJSHandler` object and installing it through WebView slot `0x12c`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:285623-285629` maps the `QLJSHandler` vtable to `OnMethodCall`, `OnMethodCallWithReturnValue`, and destroy callbacks.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:301553-301690` maps the `data_55c008` table, including `IsPakFilePresent`, `IsGameRunning`, `SendGameCommand`, `WriteTextFile`, cvar helpers, map/factory/demo list helpers, Steam/lobby helpers, `GetConfig`, `GetCursorPosition`, `GetAllUGC`, `GetNextKeyDown`, and `SetFavoriteServer`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:268623-268624` anchors the browser object name `qz_instance` and the retail fallback log string for unimplemented plugin calls.

Source reconstruction:

- The native slot-`0x12c` object remains mapped rather than claimed as ABI-reconstructed; `Awesomium::JSValue` and `Awesomium::JSArray` marshalling are still a separate evidence pass.
- The startup script now deterministically creates `window.FakeClient.qz_instance` when absent, exposes `window.qz_instance`, replaces browser-visible methods from the retail 34-entry method-name surface, and invokes `main_hook_v2` immediately instead of waiting for page code to call it.
- Default implementations are deliberately offline-safe: catalog getters return bounded placeholder data, return-value helpers return stable empty/false values, and Steam/lobby/UGC methods no-op rather than attempting live services outside the source-owned service gates.

Expected effect:

- Browser payloads that assume `FakeClient.qz_instance` exists at startup should no longer trip a JavaScript exception before first paint.
- Missing qz method names should no longer leave the menu in a black or loader-only state solely because the native Awesomium `QLJSHandler` object is still mapped rather than fully reconstructed, and pre-existing fake qz methods no longer swallow command/cvar calls.

## 2026-05-25 browser-helper readiness reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:216003-216017` shows retail installing `QLJSHandler` on WebView slot `0x12c`, then calling `QLJSHandler_BindQzInstance` in a helper loop.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:216008-216019` bounds that readiness loop to ten iterations with a 100 ms sleep before failing with `Could not initialize browser helpers. Please try restarting the game.`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:44555-44564` shows `QLJSHandler_BindQzInstance` probing the page for `qz_instance` object state rather than treating the native object install alone as sufficient.

Source reconstruction:

- The startup bridge now advertises `window.__qlr_browser_helpers_ready` once the source-owned `qz_instance` surface is installed.
- It dispatches a `qz_instance.ready` DOM event for page scripts that wait on an explicit readiness signal.
- It re-runs `main_hook_v2` for forty 250 ms intervals, preserving the retail idea of a bounded helper-readiness window while allowing source-side page code to create or replace `FakeClient.qz_instance` after the injected script first runs.

Remaining caveat:

- The retry loop is intentionally source-owned and JavaScript-level. It reconstructs the observable browser-helper readiness contract, not the native Awesomium `JSMethodHandler` return-value ABI.

## 2026-05-25 startup script compactness and truncation guard

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:216003-216017` keeps the native helper install and readiness loop separate from page script parsing, so a failed helper bind is surfaced through the explicit browser-helper failure path.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:301553-301690` bounds the browser-visible method-name table to a fixed method surface rather than a page-owned ad hoc object shape.

Source reconstruction:

- The injected `qz_instance` bridge now builds the fixed retail method-name surface from compact method groups instead of a long sequence of individual `bind(...)` calls.
- The script sets `window.__qlr_qz_instance_script_complete` only at the end of the injected payload, giving future diagnostics a stable marker for successful parse-through.
- `CL_Awesomium_BuildStartupScript` now logs a debug diagnostic if `_snprintf` truncates the injected helper script before WebConfig receives it.

Expected effect:

- Source-owned additions to the bridge are less likely to silently truncate the injected script and leave live Awesomium with a black page before the menu JavaScript can attach to `qz_instance`.
- If truncation does occur, the failure becomes visible in developer logging instead of looking like an unrelated paint/surface problem.

## 2026-05-25 live-surface renderer containment

- Dirty-state parity: the retail `BitmapSurface::IsDirty` fallback now reads the same reconstructed dirty byte used by `SetIsDirty`, rather than treating every non-empty surface as permanently dirty. This keeps the client from re-uploading the last bad browser frame every renderer frame after Awesomium has already acknowledged the paint.

Observed source failure mode:

- The live Awesomium path copied `BitmapSurface` pixels into the browser surface buffer and treated a successful copy as drawable even when all sampled RGB channels were zero.
- When the live surface was black or empty, the fallback path synthesized a full-screen diagnostic texture and `CL_WebHost_DrawBrowserSurface` still drew it while `browserActive` was set.
- Because the browser surface is drawn as a full-screen overlay, promoting an empty/black live surface could make the UI appear black, hide the console, or make the world look incorrectly bright or washed depending on draw order and the current 2D state.

Source reconstruction at the time:

- `QLWebView_WriteSurfacePixels` now returns whether a drawable surface was produced.
- Live Awesomium surfaces are drawable only after `CL_Awesomium_CopySurface` succeeds and `QLWebView_SurfaceHasVisiblePixels` finds non-zero RGB data.
- Empty or all-black live surfaces no longer fall through to the diagnostic fallback surface and no longer upload a browser shader.
- `CL_WebHost_DrawBrowserSurface` now requires `browserVisible`, `browserActive`, a valid shader, and `surfaceHasVisiblePixels` before issuing the full-screen draw.

Expected effect:

- Awesomium can continue updating in the background while black/empty paints are ignored, rather than corrupting or covering the rest of the renderer.
- If the browser page still fails to paint, the normal Quake UI, console, and world render should remain visible instead of being replaced by the browser overlay.

## 2026-05-31 disconnected WebUI startup and DataPak path correction

Runtime evidence:

- A VS Code launch with `cwd` set to the repository root no longer matched the retail process working directory beside `web.pak`.
- `awesomium.log` reported `Unable to load DataPak with path: web.pak`, then repeated `Failed to launch child process`; the client log showed `Awesomium surface not visible: copy=0 ... lastError=4`.
- While the browser was pending, `SCR_DrawScreenField` still reopened `UIMENU_MAIN` every disconnected frame, repeatedly invoking the native menu `onOpen` path and its `web_stopRefresh`/music actions.

Source reconstruction:

- Disconnected WebUI requests now claim fullscreen ownership as soon as `KEYCATCH_BROWSER`, `web_browserActive`, or `ui_browserAwesomiumPending` is set. Native `UI_REFRESH` is suppressed for the same requested-browser window so `main.menu` is not reopened underneath a live Awesomium startup.
- The live Awesomium adapter now resolves `awesomium_process.exe` and `web.pak` from `fs_homepath` first, falling back to `fs_basepath`, and passes the resolved `web.pak` path into `DataPakSource`. Retail still uses the literal package member name under the retail install cwd; the source adapter must be deterministic under the repository cwd used by VS Code launches.
- `WebConfig::child_process_path` now receives the retail `awesomium_process.exe` filename only after the staged helper beside the executable is validated. Runtime evidence from the direct VS Code launch showed the runtime-bin helper could be a source-built online-services stub with no `awesomium.dll` / `Awesomium::ChildProcessMain` import, while the retail helper retained that import. A follow-up launch showed absolute helper paths still make Chromium's legacy child launcher fail, so the adapter now rejects invalid staged helpers instead of letting WebCore spin on a dead child path; the default build task is responsible for staging the retail helper beside the executable.
- The adapter sets Awesomium `additional_options` to `--no-sandbox`. The earlier `--single-process` workaround did not prevent Chromium from trying to launch a child process, and retail parity is better served by requiring the child helper to be the real `Awesomium::ChildProcessMain` bootstrap.
- The live WebPreferences path explicitly disables Awesomium GPU acceleration when the setter is available. Retail's offscreen menu expects a software `BitmapSurface`; keeping the reconstructed host out of GPU compositing avoids handing the first successful WebUI paint to the same broken post-process/render-cache path that had been corrupting map loading and in-game frames.
- Dynamic browser surface upload stays in the WebUI pump, not inside `CL_WebHost_DrawBrowserSurface`, matching the retail update/draw split and avoiding texture registration from the draw path.
- A live Awesomium startup that never produces a contentful `BitmapSurface` is now bounded. After 180 missing-surface frames, the host logs the last Awesomium state, shuts down the live WebCore path, clears browser keycatch/cvars, latches `loadFailed`, and refreshes the bridge so the native menu can regain control instead of freezing behind a permanently pending WebUI owner.
- Follow-up runtime evidence showed the renderer post-process gate was still being resurrected from archived config state (`r_enablePostProcess 1`), which turned the post-fallback capture into a white frame even after the dead browser owner was cleared. `r_enablePostProcess` is now ROM default `0` and force-reset during renderer registration as a documented stability divergence until the reconstructed post-process FBO/cache path is fixed.

## 2026-05-28 runtime/update parity correction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15969` shows `DataPakSource::DataPakSource` receiving the literal `"web.pak"` before the source is added under `"QL"`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15804` maps the browser draw/update helper: it recreates the browser image when dimensions change, uploads the Awesomium `BitmapSurface` only when dirty, clears the dirty bit, then draws the browser shader without an RGB-visibility gate.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:33128` shows `QLWebCore_Update` called from the main frame loop before Steam callbacks and the client frame; surface upload/draw remains in the renderer-facing helper.

Source divergence found:

- `CL_Awesomium_CreateSession` verified `web.pak` under the selected runtime/base root, but then passed the absolute path into `DataPakSource` instead of the retail `"web.pak"` package member name. With `WebConfig::package_path` already pointing at the root, this could prevent `asset://ql/...` loads from resolving.
- The live surface path treated all-black copied surfaces as non-drawable. Retail treats a copied `BitmapSurface` as the drawable browser texture and lets page content, including dark startup frames, present normally.
- `QLWebCore_Update` still forced the live browser surface dirty every active frame. Retail dirty handling is driven by `BitmapSurface::IsDirty` plus dimension changes.

Fix implemented:

- `CL_Awesomium_CreateSession` was initially reconstructed to construct the data source with `DataPakSource("web.pak")` after verifying the file exists in the selected root. The 2026-05-31 VS Code launch correction above supersedes that runtime detail for the reconstructed dynamic-loader host: it now passes the resolved `web.pak` path while keeping `WebConfig::package_path` pointed at the selected root.
- A successful live `BitmapSurface` copy now produces an uploadable browser shader even when sampled RGB values are zero; the visible-pixel check is retained only as a diagnostic.
- Live Awesomium no longer forces `surfaceDirty` every active frame after `WebCore::Update`; dirty uploads now follow `BitmapSurface::IsDirty` and size rebuilds, matching the retail update cadence.

## 2026-05-28 qz_instance return-flag correction

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv:366`, `:1121`, `:1308`, and `:1549` retain the owning retail functions at `0x00431A10`, `0x004328B0`, `0x00431E50`, and `0x00431570`.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt:3372` identifies the `QLJSHandler::vftable` at `0x00548010`, while `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45616` shows retail installing that handler on the WebView before the ten-try browser-helper bind loop.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44299` shows `QLJSHandler_LookupMethodId` walking `data_55c008` to `0x55c1a0` in 12-byte rows.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44571-44577` shows `QLJSHandler_BindQzInstance` passing the third table field to `Awesomium::JSObject::SetCustomMethod`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt:1559-1698` maps the 34-entry qz method table. The `SetCvar` row at `0x0055C044` and `ResetCvar` row at `0x0055C050` both have return flag `1`; the final `NoOp` row is at `0x0055C194`, after `SetFavoriteServer`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:45282` maps `QLJSHandler_OnMethodCallWithReturnValue`, and the adjacent switch cases reconstruct return-valued cvar set/reset behavior.

Source divergence found:

- The source-visible qz method binding table did not preserve the retail data-table address for each row, making row-order regressions hard to catch.
- `SetCvar` and `ResetCvar` were treated like void/no-op browser helpers in the injected startup bridge even though retail registers them as return-valued custom methods.
- The compact startup method group placed `NoOp` before the late UGC/key/favorite rows, which did not match the retail table's final-row ordering.

Fix implemented:

- Added retail qz table bounds and per-row table addresses to `cl_webMethodBindings`.
- Marked `SetCvar` and `ResetCvar` as return-valued rows, routed them through `QLJSHandler_OnMethodCallWithReturnValue`, and made them return boolean success/failure strings to Awesomium.
- Updated the injected `qz_instance` bridge so local `SetCvar` and `ResetCvar` helpers normalize cvar names and return `true`, matching the browser-visible return contract.
- Reordered the startup no-op method group so `NoOp` remains the last retail method row after `GetAllUGC`, `GetNextKeyDown`, and `SetFavoriteServer`.

Expected effect:

- Menu JavaScript that checks the result of `qz_instance.SetCvar(...)` or `qz_instance.ResetCvar(...)` should now see the same truthy return behavior retail exposes.
- Future reconstruction work has source-visible anchors for the exact `data_55c008` table span and row addresses, reducing the chance of silently drifting from the retail qz method surface.

## 2026-05-28 SDK dependency hygiene correction

Audit finding:

- The Win32 backend had accumulated SDK-like C++ ABI fallback code: local object storage, `__thiscall` typedefs, vtable-slot dispatch helpers, decorated constructor lookups, and raw `BitmapSurface` field-offset reads.
- The helper project generated an Awesomium import library from `src/code/win32/awesomium.def`, and `awesomium_process.cpp` locally redeclared `Awesomium::ChildProcessMain`.
- `awesomium_process.rc` presented the rebuilt helper as an Awesomium Technologies binary instead of project-owned source.

Fix implemented:

- Removed the C++ ABI fallback layer. Runtime calls now stay on the external Awesomium SDK C API exports loaded from `awesomium.dll`; if an export is absent, the adapter reports the missing SDK export or treats documented optional exports as no-op/optional.
- Corrected SDK export names for live paths that matter at startup/input: `_Awe_WebView_SetTransparent@8` and the SDK-owned keyboard event-object sequence `_Awe_new_WebKeyboardEvent_1@12`, `_Awe_WebView_InjectKeyboardEvent@8`, `_Awe_delete_WebKeyboardEvent@4`.
- Deleted `src/code/win32/awesomium.def`; `awesomium_process.vcxproj` now requires an external Awesomium SDK path and links `awesomium.lib` when `QLBuildOnlineServices=1`.
- `quakelive_steam.vcxproj` now declares the external SDK/runtime dependency for online builds through `AwesomiumSdkDir` or `AWESOMIUM_SDK_DIR`, while default builds remain offline-safe.
- `awesomium_process.cpp` includes `<Awesomium/ChildProcess.h>` instead of redeclaring SDK symbols, and the helper version resource now uses project-owned metadata.

Expected effect:

- The repository no longer contains a local reconstruction of Awesomium SDK object layout or C++ ABI behavior.
- Live WebUI startup should fail with a precise missing-SDK/missing-export diagnostic instead of falling into an inaccurate local ABI imitation.

## 2026-05-29 external Awesomium SDK/runtime payload correction

Audit finding:

- A live startup pass could initialize the main window and load `awesomium.dll`,
  but `awesomium.log` reported child-process launch failures. Static project
  review showed why: `quakelive_steam.vcxproj` only copied `awesomium.dll`,
  leaving the helper and Chromium/Awesomium sidecar DLL contract to whatever
  happened to be staged beside the executable.
- Retail metadata in `docs/reverse-engineering/build-recapture.md` shows the
  Awesomium payload is a set, not one DLL: `awesomium.dll`,
  `awesomium_process.exe`, `avcodec-53.dll`, `avformat-53.dll`,
  `avutil-51.dll`, `icudt.dll`, `libEGL.dll`, and `libGLESv2.dll`.
- The Quake Live `web.pak` remains game UI data, not SDK code. It is still
  resolved through the engine/runtime asset roots and passed to
  `DataPakSource("web.pak")`.

Source reconstruction:

- Online client builds now project-reference `awesomium_process.vcxproj` when an
  external `AwesomiumSdkDir` is supplied, so the helper is built from the SDK
  header/import library boundary instead of depending on a stale staged binary.
- The client project validates the retail-observed Awesomium runtime sidecar DLLs
  under the external runtime folder and copies that payload into `$(OutDir)`.
  Optional `locales` files are copied if the SDK/runtime package provides them.
- The source tree still does not vendor the proprietary SDK, generate an import
  library from a local `.def`, redeclare `ChildProcessMain`, or reconstruct
  Awesomium C++ object layout. The only source-owned helper call remains
  `Awesomium::ChildProcessMain` through `<Awesomium/ChildProcess.h>`.

Expected effect:

- A correctly installed external SDK/runtime now produces a self-contained
  online-enabled output directory with the SDK-backed helper and required
  Awesomium sidecars.
- If the runtime payload is incomplete, the build fails with the missing sidecar
  name instead of producing a black Awesomium window that can only report child
  launch failure at runtime.

## 2026-05-29 QLLoadHandler document-ready execution reconstruction

Retail evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44449`
  maps `sub_4317f0` as the `QLLoadHandler_OnDocumentReady` callback.
- Lines `44463-44525` enumerate the `js` directory for `.js` entries, build
  `js/<filename>`, read each script, and call the WebView `ExecuteJavascript`
  slot `0x124`.
- Lines `44527-44538` refresh the retained `window` object, then publish
  `web.object.ready` through the same `EnginePublish` bridge used by later
  browser events.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt:35617`
  identifies the `QLLoadHandler` vtable at `0x00547fe8`, with `OnBegin`,
  `OnFail`, `OnFinish`, and `OnDocumentReady` callbacks.

Source reconstruction:

- `QLLoadHandler_LoadDocumentScripts` now preserves the retail order:
  enumerate `js/*.js`, resolve each script through `CL_LauncherRequestData`,
  execute it in live Awesomium with `CL_Awesomium_ExecuteJavascript`, then free
  the source buffer.
- `QLLoadHandler_PollLiveDocumentReady` projects the native load callback onto
  the source frame pump: after `CL_Awesomium_Update`, if the host is waiting on
  a document and `CL_Awesomium_IsLoading()` is false, it runs
  `QLLoadHandler_OnFinishLoadingFrame` followed by
  `QLLoadHandler_OnDocumentReady`.
- Live `QLWebHost_OpenURL` and reload now mark the document as loading and let
  the frame pump publish readiness, instead of immediately declaring the
  document ready after `LoadURL`/reload dispatch.

Expected effect:

- The live WebUI gets the same launcher helper script staging before
  `web.object.ready` that retail performs through the native load handler.
- Events and native request polling are less likely to race the document load,
  because the source bridge waits for Awesomium's loading state to clear before
  publishing readiness.

## 2026-05-29 Awesomium C API native-handler route mapping

Retail/API evidence:

- Local retail Awesomium export inspection identifies SDK C exports for the
  remaining native object seams:
  `_Awe_WebCore_set_resource_interceptor@8`,
  `_Awe_WebView_set_js_method_handler@8`,
  `_Awe_WebView_set_dialog_listener@8`,
  `_Awe_WebView_set_load_listener@8`, and
  `_Awe_WebView_set_view_listener@8`.
- The same export table exposes constructor/director helpers:
  `_Awe_new_ResourceInterceptor@0`,
  `_Awe_ResourceInterceptor_director_connect@16`,
  `_Awe_new_JSMethodHandler@0`,
  `_Awe_JSMethodHandler_director_connect@12`,
  `_Awe_new_DataSource@0`, `_Awe_DataSource_director_connect@8`,
  `_Awe_new_Load@0`, `_Awe_Load_director_connect@20`,
  `_Awe_new_View@0`, `_Awe_View_director_connect@36`,
  `_Awe_new_Dialog@0`, and `_Awe_Dialog_director_connect@20`.
- The committed HLIL already maps the corresponding retail install points:
  resource interceptor on WebCore slot `0x10`, JS method handler on WebView slot
  `0x12c`, dialog handler on `0x34`, view handler on `0x24`, and load handler on
  `0x28`.

Mapping result:

- The remaining native listener/interceptor/data-source parity work has a
  verified SDK-owned route. We should not reconstruct SDK class storage or
  retail vtable objects in repository source.
- The next implementation pass can replace source polling/projection for the
  native object seams incrementally by importing these C exports and connecting
  callbacks to the already recovered source helpers.
- The JS method handler remains the riskiest lane because it also requires
  precise `JSValue`, `JSArray`, and `JSObject` marshalling. Load/view/dialog
  listener projection is a better first native-object target.

## 2026-05-29 WebPreferences byte-field reconstruction

Retail evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45557-45560`
  shows retail constructing a local `Awesomium::WebPreferences`, then writing
  byte offsets `+0x02 = 1` and `+0x08 = 0` before `WebCore::CreateWebSession`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15948-15950`
  captures the same constructor-plus-two-byte-write sequence.
- A focused x86 probe against the staged retail `E:\Games\QuakeLive\awesomium.dll`
  mapped SDK C setters onto the WebPreferences byte layout:
  `_Awe_WebPreferences_enable_plugins_set@8` toggles byte `+0x02`, and
  `_Awe_WebPreferences_enable_web_security_set@8` toggles byte `+0x08`.

Source reconstruction:

- `CL_Awesomium_PreparePreferences` now imports and calls only the two
  retail-observed setters: `enable_plugins = true` and
  `enable_web_security = false`.
- The previous broader compatibility setup no longer forces JavaScript, local
  storage, databases, file-access, or universal file-access preferences. Those
  SDK defaults are left to the constructed `WebPreferences`, matching the
  recovered retail write surface.

Expected effect:

- Online-enabled WebUI startup now follows the retail WebPreferences mutation
  contract instead of over-configuring the session.
- The exact field-name gap for the two observed preference bytes is closed
  without copying SDK headers, object layout, or proprietary implementation
  code into repository source.
