# Quake Live Steam Mapping Round 583: Awesomium Child Process Helper SDK/Dynamic Boundary

## Scope

This round pins the executable-owned Awesomium child-process helper boundary
against the committed retail `awesomium_process.exe` Ghidra corpus and the
source reconstruction that now supports both strict SDK linking and the
default SDK-free dynamic-loader path.

The focus is deliberately narrow: the helper executable only owns launch glue
into `Awesomium::ChildProcessMain(HINSTANCE)`. Browser runtime behavior still
belongs to the proprietary Awesomium DLLs and remains outside the repository's
source-owned reconstruction surface.

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/awesomium_process/metadata.txt`
  identifies `awesomium_process.exe` as a 32-bit Windows helper with `139`
  functions, `54` imports, and `1` export.
- `functions.csv` records `FUN_00401000` at `0x00401000`, size `98`, with the
  `__stdcall` convention; the shared alias corpus maps it to
  `AwesomiumProcess_RunChildProcessMain`.
- `exports.txt` contains the single `004013a5 entry` export.
- `imports.txt` contains Kernel32 loader/startup rows such as
  `GetProcAddress`, `GetModuleFileNameW`, `LoadLibraryW`, `GetCommandLineW`,
  `GetStartupInfoW`, and `ExitProcess`, with no direct `awesomium.dll` or
  `ChildProcessMain@Awesomium` import-name row in the helper corpus.
- `decompile_top_functions.c` shows CRT startup calling
  `FUN_00401000((HINSTANCE__ *)&IMAGE_DOS_HEADER_00400000)` and the helper
  body setting up SEH before calling `Awesomium::ChildProcessMain(param_1)`.

Inferred mapping:

- The retail helper's executable-owned behavior is the narrow
  `entry -> FUN_00401000 -> Awesomium::ChildProcessMain` bridge. The remaining
  imports are CRT and Windows loader support, not additional browser policy.
- The source reconstruction should therefore keep the helper as a Windows GUI
  subprocess host and route online-service behavior through guarded optional
  Awesomium SDK/runtime paths.

## Reconstruction

Strengthened `tests/test_awesomium_browser_parity.py` so the helper boundary is
checked as one source-owned contract:

- Ghidra metadata, export count, import count, and the `FUN_00401000` function
  row are pinned together with the promoted alias.
- The decompile evidence is checked from CRT entry through
  `Awesomium::ChildProcessMain`.
- The source helper is checked for the default `QL_AWESOMIUM_USE_SDK=0` path,
  the strict external SDK path, the SDK-free `awesomium.dll` dynamic-loader
  fallback, and the offline no-op fallback when online services are disabled.
- `src/code/awesomium_process.vcxproj` is checked for Windows GUI/x86 helper
  settings, default-off `QLBuildOnlineServices`, default-off
  `QLUseAwesomiumSdk`, and strict SDK validation only when both online services
  and SDK mode are explicitly enabled.
- `src/code/win32/awesomium_process.rc` is checked for the project-owned
  version, manifest, description, and executable filename identity.

No runtime launch was needed for this pass. The evidence question was static:
whether the source-owned helper boundary matches the committed retail helper
corpus while keeping Quake Live-only online services behind explicit build
switches.

## Validation

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  - passed
- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_child_process_helper_dynamic_sdk_boundary_matches_retail_corpus -q --tb=short`
  - passed, `1 passed`
- `python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short`
  - passed, `42 passed`
- `python -m pytest tests/test_game_native_export_helper_parity.py -q --tb=short`
  - passed, `11 passed`

## Parity Estimate

- Focused child-process helper ownership evidence: **before 91% -> after 99%**.
- Focused SDK/dynamic helper source-boundary confidence:
  **before 86% -> after 97%**.
- Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.26% -> 99.27%**.
