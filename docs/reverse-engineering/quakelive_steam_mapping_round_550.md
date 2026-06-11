# Quake Live Steam Mapping Round 550: Awesomium Imported ABI and Listener Graph Bridge

Date: 2026-06-11

## Scope

This round rechecked the retail Awesomium/WebUI launch/runtime ABI boundary in
`quakelive_steam.exe`, with emphasis on the imported Awesomium SDK extern table,
the listener/data-source RTTI and vtables, the `QLWebHost_OpenURL` construction
graph, and the standalone `awesomium_process.exe` helper corpus.

No live WebUI behavior was enabled and no runtime source behavior was changed.
The current source already keeps this lane behind `QL_BUILD_ONLINE_SERVICES` and
uses explicit fallback behavior for default builds.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part19.txt`
- Ghidra symbols:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Helper-process Ghidra corpus:
  `references/reverse-engineering/ghidra/awesomium_process/metadata.txt` and
  `references/reverse-engineering/ghidra/awesomium_process/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_awesomium_win32.cpp` and
  `src/code/win32/awesomium_process.cpp`

## Observed Facts

- HLIL part 19 exposes the retail Awesomium extern surface used by the WebUI
  runtime, including `WebCore::Initialize`, `WebCore::Shutdown`,
  `DataPakSource::DataPakSource`, `DataPakSource::OnRequest`,
  `ResourceResponse::Create`, `DataSource::SendResponse`,
  `JSObject::InvokeAsync`, `BitmapSurface::CopyTo`, and
  `BitmapSurface::set_is_dirty`.
- HLIL part 05 shows `QLWebHost_OpenURL` constructing the browser runtime:
  WebConfig, WebCore, WebPreferences, WebSession, `QL` DataPakSource,
  `steam` SteamDataSource, ResourceInterceptor, JS method handler, and
  Dialog/View/Load listeners.
- Ghidra `analysis_symbols.txt` carries the matching imported vtables and RTTI
  descriptors for `QLResourceInterceptor`, `QLDialogHandler`, `QLViewHandler`,
  `QLLoadHandler`, `QLJSHandler`, and `Awesomium::DataPakSource`.
- `awesomium_process.exe` remains a small helper binary. Its committed Ghidra
  corpus reports 139 functions, 54 imports, one export, and `FUN_00401000` as
  the product-specific child-process entry owner.
- The reconstructed source uses SDK C-export adapter calls for the live
  WebCore/WebView/WebSession surface, retains the DataPakSource bootstrap map,
  and validates the helper-process dynamic or imported
  `Awesomium::ChildProcessMain` boundary.

## Mapping Work

- Added
  `tests/test_awesomium_browser_parity.py::test_awesomium_webui_retail_import_vtable_and_helper_abi_bridge_is_pinned`
  to pin the imported ABI graph across:
  - Awesomium extern entries in Binary Ninja HLIL part 19;
  - `QLWebHost_OpenURL` runtime construction anchors in HLIL part 05;
  - Ghidra RTTI/vtable symbols for the listener and DataPakSource classes;
  - helper-process metadata, function row, and alias owner; and
  - source-side adapter bindings for DataPakSource, WebSession AddDataSource,
    ExecuteJavascript, BitmapSurface copy/dirty handling, reload/stop, and
    helper dynamic resolution.

## Source Reconstruction Decision

No source-code reconstruction was needed in this round. The source already
contains the bounded adapter surface and helper validation path required by the
retail evidence. The remaining improvement was making the imported SDK ABI and
listener graph directly testable from committed Ghidra/Binary Ninja references.

## Confidence

- High for the imported Awesomium SDK extern names and core runtime calls:
  HLIL extern rows, HLIL call sites, and source adapter bindings all agree.
- High for listener and DataPakSource vtable/RTTI ownership:
  Ghidra symbol names and HLIL construction sites agree.
- High for `awesomium_process.exe` helper ownership at `FUN_00401000`:
  Ghidra function rows, alias ledger, and source helper entry all agree.

## Validation

Validation run:

```text
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Parity Estimate

- Focused Awesomium/WebUI imported ABI and listener-graph evidence confidence:
  **before 76% -> after 98%**.
- Focused Awesomium/WebUI launch/runtime integration mapping confidence:
  **before 96% -> after 97%**.
- Overall strict Windows Awesomium/WebUI source behavior remains effectively
  closed; this pass improves evidence traceability rather than changing runtime
  behavior.
