# Quake Live Steam Mapping Round 547: Awesomium/WebUI Ghidra Bridge

Date: 2026-06-11

## Scope

This round rechecked the Awesomium/WebUI launcher and runtime integration band in
retail `quakelive_steam.exe` and the committed helper-process corpus, then
promoted the missing Ghidra-style aliases for source-owned WebUI owners that
already had stable Binary Ninja `sub_*` names.

Primary writable areas:

- `references/analysis/quakelive_symbol_aliases.json`
- `tests/test_awesomium_browser_parity.py`

Reference evidence:

- `references/reverse-engineering/ghidra/awesomium_process/metadata.txt`
- `references/reverse-engineering/ghidra/awesomium_process/imports.txt`
- `references/reverse-engineering/ghidra/awesomium_process/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_awesomium_win32.cpp`
- `src/code/win32/awesomium_process.cpp`

## Observed Facts

- `awesomium_process.exe` remains a thin helper: the Ghidra metadata reports
  139 functions, 54 imports, and a single entry export, while the committed
  import table is Kernel32-only. The source-owned behavior is still the helper
  launch wrapper and SDK entry boundary, not the browser runtime itself.
- Retail `quakelive_steam.exe` has committed Ghidra rows for the mapped WebUI
  listener, resource-interceptor, advertisement bridge, WebCore/WebView,
  input-injection, event-publication, and command-registration owners.
- The existing alias map already carried stable Binary Ninja names for those
  owners, but most of this WebUI band did not yet carry matching `FUN_*` rows or
  lower-case `sub_*` spellings.
- Three adjacent bridge wrappers remain Binary Ninja-only in the committed
  corpus: `0x004F2000`, `0x004F2020`, and `0x004F20C0`. They are still retained
  as `sub_*` aliases only because `functions.csv` does not contain matching
  Ghidra rows.
- The historically weak `0x004F1FC0` one-argument advertisement bridge wrapper
  now has a conservative source-visible name: `AdvertisementBridge_Reserved1FC0`.
  This records the observed vtable slot `+0x1c` without inventing a higher-level
  behavior.

## Mapping Work

- Promoted the `0x00431510..0x00434AE0` WebUI listener/resource band to matching
  `FUN_*` aliases where Ghidra rows exist:
  - `CGameID_IsValid`
  - `QLJSHandler_LookupMethodId`
  - `QLDialogHandler_OnShowFileChooser`
  - `QLViewHandler_OnChangeCursor`
  - `QLLoadHandler_OnBeginLoadingFrame`
  - `QLLoadHandler_OnFinishLoadingFrame`
  - `QLLoadHandler_OnDocumentReady`
  - `QLJSHandler_BindQzInstance`
  - `QLJSHandler_OnMethodCall`
  - `QLJSHandler_OnMethodCallWithReturnValue`
  - `QLViewHandler_OnChangeTooltip`
  - `QLViewHandler_OnAddConsoleMessage`
  - `QLResourceInterceptor_OnFilterNavigation`
  - `QLResourceInterceptor_OnRequest`
  - `QLLoadHandler_OnFailLoadingFrame`
- Promoted the `0x004F1EF0..0x004F3CD0` WebUI runtime band to matching `FUN_*`
  aliases where Ghidra rows exist:
  - advertisement bridge set/get/setup/refresh wrappers
  - reserved slot `0x1c`
  - WebView hash, hide, update, resize, surface, mouse, wheel, keyboard, and
    activation-key owners
  - WebUI event-publication owners
  - WebHost shutdown, listener destructors, frame pump, URL open/navigation, and
    command registration
- Added lower-case `sub_*` spellings beside the existing Binary Ninja names for
  the same stable owners.
- Added `test_awesomium_webui_ghidra_and_binary_ninja_alias_bridge_is_pinned`
  so the alias set is now checked against:
  - Ghidra row names and sizes
  - Binary Ninja `sub_*` and lower-case spellings
  - no-row boundaries for `0x004F2000`, `0x004F2020`, and `0x004F20C0`
  - HLIL anchors for document-ready, resource interception, reserved bridge
    slot dispatch, WebCore initialization, and event publication
  - source anchors for the retained `QL_WEB_BRIDGE_SLOT_RESERVED_1FC0` slot

## Source Reconstruction Decision

No runtime source patch was made in this round. The current source already
models the WebUI/Awesomium launch and runtime contract as a default-disabled
online-services lane, with live Awesomium usage behind `QL_BUILD_ONLINE_SERVICES`
and a source-owned fallback bridge for default builds. The remaining improvement
available from this evidence pass was mapping confidence, not new behavior.

## Confidence

- High for Ghidra/Binary Ninja alias equivalence where `functions.csv` rows,
  HLIL function starts, and existing source owners all agree.
- Medium for `AdvertisementBridge_Reserved1FC0`: the vtable offset and source
  slot are concrete, but the public behavior remains intentionally unnamed.
- Low for the no-row wrappers `0x004F2000`, `0x004F2020`, and `0x004F20C0`
  beyond their existing Binary Ninja/source slot names, so this round did not
  create `FUN_*` aliases for them.

## Validation

Validation run:

```text
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short
```

## Parity Estimate

- Focused Awesomium/WebUI Ghidra/Binary Ninja alias bridge confidence:
  **before 70% -> after 98%**.
- Focused Awesomium/WebUI launch/runtime integration mapping confidence:
  **before 93% -> after 96%**.
- Overall Awesomium/WebUI source reconstruction parity remains effectively
  closed for the strict Windows replacement target; this pass improves evidence
  traceability rather than changing runtime behavior.
