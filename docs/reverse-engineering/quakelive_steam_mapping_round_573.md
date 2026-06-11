# Quake Live Steam Mapping Round 573: Awesomium DLL Import Name Table and C Export Adapter

Date: 2026-06-11

## Scope

This round maps the retail `quakelive_steam.exe` Awesomium import-name table
that starts in Binary Ninja HLIL part 07 and ties it to the reconstructed
Win32 Awesomium backend. The source decision remains intentional: live
Awesomium usage stays behind `QL_BUILD_ONLINE_SERVICES`, and the retail C++
ABI is documented as evidence while runtime calls are routed through the SDK C
exports resolved from `awesomium.dll`.

## Evidence Inputs

- Binary Ninja HLIL part 07 import-name table:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- Ghidra symbol support:
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Source reconstruction:
  `src/code/client/cl_awesomium_win32.cpp`

## Observed Facts

The retail import-name table covers the span `0x00558b98..0x0055913e`.
It includes decorated C++ Awesomium symbols for `JSArray`, `JSObject`,
`JSValue`, `ResourceResponse`, `WebURL`, `DataSource`, listener vtables,
`BitmapSurface`, `WebKeyboardEvent`, `WebCore`, `WebPreferences`,
`DataPakSource`, and `WebConfig`.

The table terminates at `0x0055913e`: import DLL name literal `awesomium.dll`.
That gives a direct retail dependency signal, but not a requirement that source
default builds recreate the C++ import ABI.

## Adapter Mapping

The current source maps the retail C++ evidence to guarded SDK C exports:

| Retail evidence | Source adapter |
| --- | --- |
| `WebCore::Initialize` -> `_Awe_WebCore_Initialize@4` |
| `WebCore::Shutdown` -> `_Awe_WebCore_Shutdown@0` |
| `WebConfig::WebConfig` -> `_Awe_new_WebConfig@0` |
| `WebPreferences::WebPreferences` -> `_Awe_new_WebPreferences@0` |
| `DataPakSource::DataPakSource` -> `_Awe_new_DataPakSource@4` |
| `WebView::LoadURL` -> `_Awe_WebView_LoadURL@8` |
| `WebView::ExecuteJavascript` -> `_Awe_WebView_ExecuteJavascript@12` |
| `WebView::InjectKeyboardEvent` -> `_Awe_new_WebKeyboardEvent_1@12` plus `_Awe_WebView_InjectKeyboardEvent@8` |
| `BitmapSurface::CopyTo` -> `_Awe_BitmapSurface_CopyTo@24` |

The Ghidra symbol corpus also keeps the listener/data-source vtable owners
visible: `QLResourceInterceptor`, `QLDialogHandler`, `QLViewHandler`,
`QLLoadHandler`, `QLJSHandler`, and `Awesomium::DataPakSource`.

## Source Decision

No source patch was needed for this mapping note. `CL_Awesomium_LoadImports`
already resolves `awesomium.dll` through guarded candidate paths, then imports
the `_Awe_*` C-export surface used by the Win32 backend. The source deliberately
does not name or link the retail decorated `__thiscall` C++ import symbols.

That keeps live browser runtime usage behind `QL_BUILD_ONLINE_SERVICES` and
avoids turning evidence-only C++ ABI names into default-build dependencies.

## Confidence

- High for import-name table ownership: the ordered HLIL rows and final DLL
  name literal identify the retail dependency directly.
- High for the C-export substitution boundary: the source import loader,
  bootstrap mapping table, and ABI equivalence table all point to `_Awe_*`
  exports instead of decorated C++ names.
- Medium-high for strict ABI equivalence: source matches the observable browser
  contract through the C-export adapter, while literal retail C++ object ABI
  identity remains deliberately out of scope.

Focused parity estimate after this round:

- Retail Awesomium import-name evidence confidence:
  **before 68% -> after 97%**.
- Source C-export adapter substitution confidence:
  **before 88% -> after 98%**.
- Overall Awesomium/WebUI launch/runtime integration mapping confidence:
  **99.15% -> 99.20%**.
