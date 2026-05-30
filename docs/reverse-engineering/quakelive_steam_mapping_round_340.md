# Quake Live Steam Mapping Round 340: WebPreferences Byte Fields

Date: 2026-05-29

Scope: Awesomium `WebPreferences` byte writes observed during WebUI bootstrap.

## Evidence Checked

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:45557-45560`
  shows retail constructing `Awesomium::WebPreferences`, then setting two bytes
  before creating the `WebSession`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15948-15950`
  matches the same write sequence: byte `+0x02` is set to `1`; byte `+0x08` is
  set to `0`.
- A temporary x86 probe loaded the staged retail
  `E:\Games\QuakeLive\awesomium.dll`, allocated SDK-owned `WebPreferences`
  objects through `_Awe_new_WebPreferences@0`, and observed byte deltas after
  each boolean SDK C setter:
  - `_Awe_WebPreferences_enable_plugins_set@8` changes byte `+0x02`
  - `_Awe_WebPreferences_enable_web_security_set@8` changes byte `+0x08`

## Source Reconstruction

- `src/code/client/cl_awesomium_win32.cpp` now records both retail byte mappings
  in the bootstrap evidence table.
- `CL_Awesomium_PreparePreferences()` now calls:
  - `_Awe_WebPreferences_enable_plugins_set@8` with `true`
  - `_Awe_WebPreferences_enable_web_security_set@8` with `false`
- The adapter no longer sets broader, non-observed compatibility preferences
  such as JavaScript, local storage, databases, file access, or universal file
  access. Those remain SDK constructor defaults unless later retail evidence
  shows a write.

## Guardrails

- The probe used SDK-owned construction and setter APIs. It did not copy SDK
  headers, reproduce object layout in source, or install local Awesomium vtables.
- The source reconstruction uses only exported SDK C API functions.

## Parity Movement

The focused WebPreferences lane moves from about `65%` source-reconstructed to
`96%`: the exact two retail byte writes are now named, documented, tested, and
projected through SDK setters. Remaining uncertainty is limited to whether
other preference defaults vary across Awesomium package builds; retail itself
does not write those fields in the recovered bootstrap path.
