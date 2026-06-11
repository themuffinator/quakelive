# Quake Live Steam Mapping Round 552: Awesomium Document-Ready and Resource Flow

Date: 2026-06-11

## Scope

This round rechecked the retail Awesomium/WebUI launch/runtime flow around
document readiness, `qz_instance` binding, resource interception, screenshot
resource mapping, and load-failure handling in retail `quakelive_steam.exe`.

No live WebUI behavior was enabled and no runtime source behavior was changed.
The current source already keeps live Awesomium service use behind
`QL_BUILD_ONLINE_SERVICES` and leaves default builds on the source-owned
fallback paths.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_cgame.c` and
  `src/code/client/cl_steam_resources.c`

## Observed Facts

- Retail `QLLoadHandler_OnDocumentReady` starts by enumerating `js/*.js` via
  the launcher file-list helper, builds `js/<name>` paths, and executes each
  script through the WebView `ExecuteJavascript` vtable slot before resolving
  the global `window` object.
- The same retail flow publishes `web.object.ready` only after the script loop
  and window-object acquisition.
- Retail `QLJSHandler_BindQzInstance` fetches `qz_instance`, verifies that it is
  a JavaScript object, installs the method table with `SetCustomMethod`, and
  then publishes asynchronous bootstrap properties for `version`, `steamId`,
  `playerName`, and `appId`.
- Retail `QLResourceInterceptor_OnRequest` reads `fs_webpath`, extracts URL
  host/path through Awesomium `WebURL`, compares the host against the retail
  `ql` host, special-cases `/screenshot`, and returns
  `Awesomium::ResourceResponse::Create` for mapped screenshot and web resources.
- Retail `QLLoadHandler_OnFailLoadingFrame` clears the loading state, formats
  the `Failed to load QUAKE LIVE site.` message, marks the load-failed state,
  hides the browser, and writes `com_errorMessage`.

## Mapping Work

- Added
  `tests/test_awesomium_browser_parity.py::test_awesomium_document_ready_resource_and_failure_retail_hlil_flow_is_pinned`
  to pin the retail HLIL order for:
  - `QLLoadHandler_OnDocumentReady`
  - `QLJSHandler_BindQzInstance`
  - `QLResourceInterceptor_OnRequest`
  - `QLLoadHandler_OnFailLoadingFrame`
- The same test cross-checks the committed Ghidra row names and alias owners for
  the four functions above.
- The test also verifies source-side ordering for:
  - launcher `js/*.js` enumeration and script execution;
  - qz binding and bootstrap-property refresh;
  - document-ready publication after script/qz setup;
  - retail-host mapped resource loading before the generic launcher fallback;
  - load-failure state clearing, browser hiding, and error-cvar publication; and
  - retained fallback constants for `ql`, `/screenshot`, CDN web resources, and
    screenshot resource requests.

## Source Reconstruction Decision

No source reconstruction patch was needed in this round. The source already
models the retail ordering closely enough for the mapped default-disabled
online-services lane:

- `QLLoadHandler_LoadDocumentScripts` stages `js/*.js` resources through the
  launcher data path and executes live JavaScript only when online services and
  the live Awesomium adapter are enabled.
- `QLLoadHandler_OnDocumentReady` runs the script loader, binds `qz_instance`,
  updates document state, clears the cursor override, and publishes
  `web.object.ready` in retail order.
- `QLResourceInterceptor_OnRequest` keeps SteamDataSource ownership, mapped
  retail `ql` host requests, and launcher fallback behavior separated.
- `QLLoadHandler_OnFailLoadingFrame` follows the retail visible-result path
  without enabling the live service dependency in default builds.

## Confidence

- High for document-ready ordering: HLIL call order, source order, and the
  existing launcher-script reconstruction agree.
- High for qz binding shape: HLIL object lookup, method-table loop, and
  bootstrap-property names agree with the source owner.
- High for resource-response routing: HLIL host/path extraction, screenshot
  branch, `fs_webpath` branch, and source fallback constants agree.
- Medium-high for exact load-failure UI side effects: the retail call to
  `QLWebHost_HideBrowser` is represented by source-owned browser state clearing
  and cvar publication rather than a live Awesomium call in default builds.

## Validation

Validation run:

```text
python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_document_ready_resource_and_failure_retail_hlil_flow_is_pinned -q --tb=short
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Parity Estimate

- Focused Awesomium/WebUI document-ready, qz binding, resource-response, and
  load-failure HLIL-flow confidence: **before 78% -> after 98%**.
- Focused Awesomium/WebUI launch/runtime integration mapping confidence:
  **before 97% -> after 97.5%**.
- Overall strict Windows Awesomium/WebUI source behavior remains effectively
  closed; this pass improves executable evidence coverage rather than changing
  runtime behavior.
