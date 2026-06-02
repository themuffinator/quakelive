# Quake Live Steam Host Mapping Round 342

Scope: Win32 OpenGL startup and ICD fallback wiring.

## Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- `sub_46A2A0` owns the `SetPixelFormat`/`wglCreateContext`/`wglMakeCurrent`
  context attempt and matches `GLW_MakeContext`.
- `sub_46A9F0` owns the Win32 bridge around `R_GetModeInfo`, including the
  Quake Live native-desktop `-2` scan, and matches `GLW_GetModeInfo`.
- `sub_46B7A0` owns the OS version probe and `GetVersionEx failed` diagnostic,
  matching `GLW_CheckOSVersion`.
- `sub_46C020` wraps `GLW_SetMode` return values into the two startup warning
  messages and a boolean result, matching `GLW_StartDriverAndSetMode`.
- `sub_46C060` lowercases the driver name, classifies ICD/standalone/3dfx
  drivers, calls `QGL_Init`, starts the requested mode, then retries ICD
  startup through the two retail safe-mode constants `5` and `12`.
- `sub_46C1E0` calls the loader for the requested `r_glDriver`, then falls
  through the retail `3dfxvgl` and `opengl32` fallback order before issuing
  `GLW_StartOpenGL() - could not load OpenGL subsystem`.
- `sub_46C2E0` calls `sub_46C1E0` before directly copying the four
  `glGetString` results with `Q_strncpyz`, matching `GLimp_Init`.

Inference:

- The HLIL represents the retry mode constants as denormal float literals
  because the helper uses register-shaped arguments. Interpreted as integer
  mode IDs, the constants are `5` and `12`, which map through the committed
  retail mode table to `640x480` and `1024x768`.
- The local startup failure reported by users was caused by the old GPL-era
  single retry at mode `3`, which is `640x360` in Quake Live, not the retail
  QL safe-mode pair.

## Source Update

- `GLW_LoadOpenGL` now keeps the requested-mode first attempt, then retries ICD
  startup through mode `5`/`16-bit`/fullscreen and mode `12`/`16-bit`/fullscreen.
- `GLimp_Init` remains retail-shaped: `GLW_StartOpenGL` is the fatal boundary,
  and the GL strings are copied directly afterward.
- The alias ledger now promotes the adjacent startup helpers:
  `GLW_MakeContext`, `GLW_GetModeInfo`, `GLW_CheckOSVersion`,
  `GLW_StartDriverAndSetMode`, `GLW_LoadOpenGL`, and `GLW_StartOpenGL`.

## Parity Estimate

- Win32 OpenGL startup/fallback wiring lane: before 96%, after 100%.
- Strict renderer/Win32 host-glue estimate remains 100% for this audited lane.
- Repo-wide estimate remains 98% until unrelated portability, packaging,
  online-service, and source-legacy surfaces are closed.

## Verification

- `python -m pytest tests/test_renderer_win32_host_glue_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentysecond_renderer_startup_tranche_matches_retail_contracts -q --tb=short`
  - Result: `42 passed`.
- `msbuild src\code\quakelive.sln /p:Configuration=Debug /p:Platform=x86 /m /nologo`
  - Result: `Build succeeded`, `0 warnings`, `0 errors`.
