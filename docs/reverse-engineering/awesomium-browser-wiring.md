# Awesomium browser wiring map

This note records the current retail mapping for the Quake Live Awesomium browser host and the source reconstruction seams that correspond to it. It is intentionally scoped to evidence already committed in this repository.

## Evidence anchors

- `references/hlil/quakelive_steam.exe/00_12d640/part05.txt:11025` shows retail opening `asset://ql/index.html` when the online browser path is allowed.
- `references/hlil/quakelive_steam.exe/00_12d640/part05.txt:15880` maps the browser bootstrap function that initializes WebCore, WebSession, data sources, WebView, handlers, URL load, resume, focus, and `web_browserActive`.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:22491` maps `QLResourceInterceptor` request behavior.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:35571` maps the Awesomium-facing vtables for `QLResourceInterceptor`, dialog/view/load handlers, `QLJSHandler`, `DataPakSource`, and `SteamDataSource`.
- `references/hlil/quakelive_steam.exe/00_12d640/part06.txt:49745` lists the Awesomium imports used by the retail executable, including JS object/value helpers, WebCore initialization, WebView calls, BitmapSurface copy, DataSource send response, and Steam API symbols.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:36881` is the structured companion decompile for the WebCore/WebView bootstrap.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45532` is the structured companion decompile for the resource interceptor.

## Retail bootstrap sequence

| Order | Retail behavior | Current source owner |
| --- | --- | --- |
| 1 | Gate browser startup on platform/service state, then request `asset://ql/index.html`. | `src/code/client/cl_main.c`, `src/code/client/cl_awesomium_win32.cpp` |
| 2 | Construct `Awesomium::WebConfig` and call `Awesomium::WebCore::Initialize`. | `CL_Awesomium_Startup` |
| 3 | Construct `Awesomium::WebPreferences`. Retail sets two observed local preference bytes before WebSession creation. | Partially reconstructed in `CL_Awesomium_Startup`; exact preference field names remain open. |
| 4 | Create a WebSession using `fs_homepath`. | `CL_Awesomium_CreateSession` |
| 5 | Construct `DataPakSource("web.pak")` and add it under source host `QL`. | `CL_Awesomium_CreateSession`, `src/code/client/cl_webpak.c` |
| 6 | Construct `SteamDataSource` and add it under source host `steam`. | Offline-safe avatar/resource bridge in `src/code/client/cl_steam_resources.c`; not yet attached as a native live Awesomium data source. |
| 7 | Construct `QLResourceInterceptor` and set it on WebCore. | Request behavior reconstructed in `src/code/client/cl_steam_resources.c`; live native interceptor object is still a compatibility seam. |
| 8 | Create WebView with current video dimensions and the session. | `CL_Awesomium_Startup` |
| 9 | Construct `QLJSHandler` and install it on WebView vtable slot `0x12c`. | JS bridge currently reconstructed with startup script injection and `FakeClient`/`qz_instance` compatibility. Native JSValue marshalling is still open. |
| 10 | Wait up to ten 100 ms helper iterations for browser helper initialization. | `CL_Awesomium_Startup` has equivalent polling around view initialization. |
| 11 | Install dialog, view, and load handlers on WebView slots `0x34`, `0x24`, and `0x28`. | Handler vtables are mapped; source currently uses direct host state and surface polling rather than native objects. |
| 12 | Call WebView slot `0xa0` with `1`, then load the URL through slot `0x64`. | URL load reconstructed. Slot `0xa0` is mapped as an unresolved WebView paint/transparent-state seam. |
| 13 | Resume rendering through slot `0xac`, focus through slot `0xb0`, update activation/cursor state, set `web_browserActive` to `1`, and enable key catcher. | `CL_Awesomium_OpenURL`, `CL_Awesomium_Startup`, and client-side browser host drawing/input paths. |

## Awesomium vtable and import mapping

| Retail object/API | Evidence | Source reconstruction status |
| --- | --- | --- |
| `WebView::LoadURL` slot `0x64` | HLIL bootstrap and Awesomium import list | Reconstructed through `_Awe_WebView_LoadURL@8` and retail vtable fallback. |
| `WebView::Stop` slot `0x74` | HLIL/import surface | Reconstructed through retail vtable fallback. |
| `WebView::surface` slot `0x84` | BitmapSurface copy path | Reconstructed and used by `CL_Awesomium_CopySurface`. |
| `WebView::Resize` slot `0x9c` | Video size integration | Reconstructed through `_Awe_WebView_Resize@12` and fallback. |
| `WebView::ExecuteJavascript` slot `0x124` | Awesomium import list and retail WebView ABI layout | Reconstructed in this pass as `CL_Awesomium_ExecuteJavascript`. |
| `WebView::set_js_method_handler` slot `0x12c` | HLIL bootstrap | Mapped, but native handler object is not yet source-reconstructed. |
| `WebView::ResumeRendering` slot `0xac` | HLIL bootstrap | Reconstructed through fallback. |
| `WebView::Focus` slot `0xb0` | HLIL bootstrap | Reconstructed through fallback. |
| Mouse input slots `0xd0` to `0xdc` | Input path reconstruction | Reconstructed through fallback. |
| `BitmapSurface::CopyTo` and dirty flag | Import list | Reconstructed in surface copy/upload path. |
| `Awesomium::DataPakSource` | Retail vtable and bootstrap | Reconstructed enough to load `web.pak`; source additionally searches deterministic filesystem roots. |
| `Awesomium::DataSource::SendResponse` | Import list | Mapped; source fallback request path is implemented in `cl_webpak.c` and `cl_steam_resources.c`. |

## Handler and data source wiring

| Retail class | Retail vtable evidence | Observed purpose | Current source equivalent |
| --- | --- | --- | --- |
| `QLResourceInterceptor` | vtable at `0x00547f94` | Intercepts `asset://ql/...`; maps screenshot URLs under `<fs_homepath>/<fs_game>/screenshots/`; maps other `asset://ql/...` paths through `fs_webpath` when set; navigation filter never blocks. | `QLResourceInterceptor_RequestRetailHost`, `QLResourceInterceptor_MapRetailPath`, and `QLResourceInterceptor_OnFilterNavigation` in `src/code/client/cl_steam_resources.c`. |
| `QLDialogHandler` | vtable at `0x00547fa8` | Dialog callback surface for WebView. | Mapped only; no live native object yet. |
| `QLViewHandler` | vtable at `0x00547fc0` | View lifecycle/paint-facing notifications. | Replaced by host polling of view/surface state. |
| `QLLoadHandler` | vtable at `0x00547fe8` | Load lifecycle callbacks. | Mapped only; startup script and direct state checks cover the currently required behavior. |
| `QLJSHandler` | vtable at `0x00548010` | Handles JS method calls and query responses for the menu. | Reconstructed with a deterministic injected `qz_instance`/`FakeClient` bridge. Full native JSValue/JSObject marshalling remains open. |
| `DataPakSource` | vtable at `0x00548070` | Serves browser assets from `web.pak` under `asset://ql/`. | Reconstructed in Awesomium session setup and `cl_webpak.c`. |
| `SteamDataSource` | vtable at `0x00532b80` | Serves Steam-backed resources, especially avatar-like data. | Offline-safe source-side bridge in `cl_steam_resources.c`; live Awesomium source attachment remains intentionally bounded by `QL_BUILD_ONLINE_SERVICES`. |

## Current parity assessment for the browser host

Implemented or source-reconstructed:

- WebCore initialization and shutdown behind `QL_BUILD_ONLINE_SERVICES`.
- WebSession creation rooted in `fs_homepath`.
- `web.pak` mounting and deterministic package-path behavior for `asset://ql/index.html`.
- WebView creation, resize, URL load, render resume, focus, surface copy, dirty tracking, and dynamic texture upload.
- Retail vtable fallback for the core WebView calls needed by the menu path.
- Startup JS bridge for `qz_instance` and `FakeClient.qz_instance` compatibility.
- `ExecuteJavascript` wrapper/fallback reconstructed at the retail WebView ABI seam.
- Retail-shaped resource request mapping for `asset://ql/screenshot/...` and `fs_webpath` overrides.
- Offline-safe Steam resource/avatar compatibility functions.

Mapped but not yet fully reconstructed:

- Native `QLJSHandler` with Awesomium `JSValue`, `JSArray`, and `JSObject` marshalling.
- Native `QLResourceInterceptor` object installation on the live WebCore instance.
- Native `SteamDataSource` installation into the live WebSession.
- Native dialog, view, and load handler objects.
- Exact names and semantics for the observed WebPreferences bytes and WebView slot `0xa0`.

Confidence notes:

- High confidence: bootstrap ordering, `asset://ql/index.html`, `QL` and `steam` source names, `web_browserActive`, WebView load/resume/focus slots, resource interceptor screenshot/fs_webpath mapping.
- Medium confidence: `ExecuteJavascript` slot `0x124` and raw wide-string wrapper shape, because it is aligned with the import surface and adjacent WebView ABI pattern but still needs a retail call-site-specific cross-check before using it for more complex script injection.
- Low confidence: exact semantic label for WebView slot `0xa0`; keep it mapped by slot until a second signal names it.

## Recommended next reconstruction cuts

1. Reconstruct the native `QLJSHandler` method table and map each JS method name to source-owned C helpers.
2. Add a source-side native resource interceptor object only if live Awesomium still needs it after the `web.pak` and startup script path are stable.
3. Cross-check WebPreferences field writes against Awesomium SDK headers or a focused retail object-layout pass before naming the fields.
4. Keep Steam-backed data source behavior offline-first unless a documented open replacement path is chosen.