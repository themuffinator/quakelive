# Quake Live Steam Mapping Round 339: Awesomium C API Native Handler Route

Date: 2026-05-29

Scope: remaining Awesomium native object gaps and whether they can be
reconstructed through SDK-owned C API exports instead of local SDK layout
replication.

## Evidence Checked

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45597-45643`
  shows retail installing:
  - `QLResourceInterceptor` on WebCore slot `0x10`
  - `QLJSHandler` on WebView slot `0x12c`
  - `QLDialogHandler` on WebView slot `0x34`
  - `QLViewHandler` on WebView slot `0x24`
  - `QLLoadHandler` on WebView slot `0x28`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt:3363-3370`
  names the `QLResourceInterceptor`, `QLDialogHandler`, `QLViewHandler`, and
  `QLLoadHandler` vtables.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt:3372`
  names the `QLJSHandler` vtable.
- `dumpbin /exports E:\Games\QuakeLive\awesomium.dll` shows generated C API
  exports for the same seams:
  `_Awe_WebCore_set_resource_interceptor@8`,
  `_Awe_WebView_set_js_method_handler@8`,
  `_Awe_WebView_set_dialog_listener@8`,
  `_Awe_WebView_set_load_listener@8`,
  `_Awe_WebView_set_view_listener@8`,
  `_Awe_ResourceInterceptor_director_connect@16`,
  `_Awe_JSMethodHandler_director_connect@12`,
  `_Awe_DataSource_director_connect@8`,
  `_Awe_Load_director_connect@20`,
  `_Awe_View_director_connect@36`, and
  `_Awe_Dialog_director_connect@20`.

## Mapping Result

- The remaining native Awesomium object gaps have a clean SDK/API route. Source
  code should import the generated C API setters and director-connect helpers,
  allocate SDK-owned objects with `_Awe_new_*`, and connect small source-owned
  callbacks.
- We should not reconstruct Awesomium object layout, duplicate SDK vtables, or
  add decorated C++ ABI thunks. The SDK already exports the required object and
  callback boundary.
- The best next native-object target is `QLLoadHandler`: its callback signatures
  are strongly constrained by the exported byte counts and the source already
  has recovered begin/fail/finish/document-ready helpers.
- `QLJSHandler` remains a later target because its callbacks also need exact
  `JSValue`/`JSArray`/`JSObject` argument and return marshalling.

## Parity Movement

This round does not claim new executable native-object parity. It raises the
mapping confidence for the remaining native Awesomium object lane from about
`70%` to `88%` by proving the SDK C API exports exist for the retail install
points, while keeping source reconstruction on the safe side of the proprietary
SDK boundary.
