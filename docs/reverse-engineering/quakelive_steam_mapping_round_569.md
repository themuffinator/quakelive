# Quake Live Steam Mapping Round 569: Awesomium String and No-Engine Helper Bridge

Date: 2026-06-11

## Scope

This round rechecked the remaining unmapped helper pocket in the retail
`quakelive_steam.exe` WebUI/Awesomium bridge around `0x00431660..0x00431d60`.
The focus was the small listener no-engine callback stubs and the string
helpers used by `QLJSHandler`, resource interception, and browser URL handling.
The work was static-only: Binary Ninja HLIL, Ghidra function rows, vtable data,
and current source reconstruction. No live Awesomium, Steam, or game launch
probe was needed.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- Binary Ninja vtable data:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Symbol/name support:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  and `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_cgame.c` and
  `src/code/client/cl_awesomium_win32.cpp`

## Observed Facts

| Retail function | Alias | Evidence | Source reconstruction boundary |
| --- | --- | --- | --- |
| `sub_431660` | `AwesomiumListener_NoEngineCallback` | Three-byte pure/no-engine body shared by `QLDialogHandler` slots `0`, `1`, and `3`, plus multiple `QLViewHandler` base slots in the vtable data. | Source records the listener-slot ownership in `cl_webListenerCallbackMappings[]` rather than inventing behavior for empty base callbacks. |
| `sub_4317b0` | `QLViewHandler_NoEngineCallback` | Three-byte pure/no-engine body used by `QLViewHandler` vtable slot `7` at `0x00547fdc`. | Source maps it as a no-engine callback row. |
| `sub_4317c0` | `QLResourceInterceptor_NoEngineCallback` | Three-byte pure/no-engine body used by `QLResourceInterceptor` vtable slot `2` at `0x00547f9c`. | Source maps it as a no-engine callback row. |
| `sub_431cc0` | `std_string_find_last_of_char_set` | Implements the MSVC `std::string` find-last-of pattern: clamps the starting index, scans backward, tests each byte with `memchr`, and returns `0xffffffff` for `npos`. `QLResourceInterceptor_OnRequest` uses it to split the WebURL path on `/`. | Compiler/string-library helper only. Source keeps path handling in explicit C helpers rather than cloning MSVC string internals. |
| `sub_431d60` | `AwesomiumWebString_ToStdStringUTF8` | Checks `Awesomium::WebString::IsEmpty`, calls `WebString::ToUTF8` once for byte count and once for payload copy, builds a temporary `std::string`, and returns the output string. It feeds `QLJSHandler` logging/argument handling and resource path extraction. | Retail string conversion helpers are mapped as ABI evidence; source keeps the public WebUI contract on the injected qz_instance bridge. Native `JSValue` string marshalling remains intentionally bounded. |

## Mapping Work

Promoted the five helper aliases in
`references/analysis/quakelive_symbol_aliases.json` with Ghidra `FUN_*`,
upper-case Binary Ninja `sub_*`, and lower-case Binary Ninja spellings where
those differ.

Added
`tests/test_awesomium_browser_parity.py::test_awesomium_string_and_no_engine_helper_aliases_track_retail_reference_rows`
to pin:

- Ghidra row sizes for the five newly mapped helper functions;
- the three no-engine callback stubs and their listener vtable slots;
- the `std::string::find_last_of` byte-scan body and resource-path split call;
- the `Awesomium::WebString::ToUTF8` two-pass conversion helper;
- the source listener mapping rows for resource, dialog, and view no-engine
  slots; and
- the source boundary that avoids direct retail `JSValue` string marshalling in
  favor of the injected `qz_instance` request bridge.

## Source Reconstruction Decision

No C/C++ source patch was needed in this round. The current source already
captures the retail-observable behavior that matters under the default-offline
online-services policy:

- no-engine Awesomium listener slots are explicitly represented in
  `cl_webListenerCallbackMappings[]`;
- source-visible QLJS methods are routed through `QLJSHandler_OnMethodCall` and
  `QLJSHandler_OnMethodCallWithReturnValue`;
- live Awesomium builds use the C-export adapter and injected JavaScript bridge
  instead of recreating the retail C++ `JSValue`/`WebString` ABI; and
- UTF-8 input to the adapter is still handled deliberately through
  `CL_Awesomium_AllocWideString` and the C-export call surface.

Reconstructing the exact MSVC `std::string` helper or native Awesomium
`WebString` object conversion in source would make the guarded online-services
path more brittle without improving the browser-visible launch/runtime
contract.

## Confidence

- High for the no-engine callback aliases: bodies are empty/pure stubs and the
  vtable rows identify their listener owners directly.
- High for `sub_431cc0`: the HLIL control flow is a canonical
  `find_last_of`/`npos` implementation, and the `/` path-split call provides a
  concrete use site.
- High for `sub_431d60`: the two `Awesomium::WebString::ToUTF8` calls,
  temporary byte buffer, and `std::string` assignment pattern are direct.

Focused parity estimate after this round:

- Awesomium listener no-engine helper alias confidence:
  **before 88% -> after 99%**.
- WebUI string conversion/helper mapping confidence:
  **before 72% -> after 96%**.
- Overall Steam/WebUI launch/runtime integration mapping confidence:
  **92.9% -> 92.95%**.
