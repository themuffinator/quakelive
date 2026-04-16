# Platform-Specific Engine Parity Audit And Implementation Plan

Last updated: 2026-04-16

Scope: platform-specific engine code in `src/code/win32/*`,
`src/code/unix/*`, `src/code/macosx/*`, and `src/code/null/*` against the
retail Windows Quake Live executable, with compatibility-only ports tracked
explicitly instead of being silently counted as retail debt.

Purpose: perform a fresh parity audit of the platform-specific engine surface,
identify any remaining strict-retail Windows gaps, and record the closure work
completed in this task.

## Audit Method And Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Canonical committed evidence used for this audit:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Existing platform-focused audits and mapping notes:
  - `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
  - `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_98.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_100.md`
- Writable source under audit:
  - `src/code/win32/*`
  - `src/code/unix/*`
  - `src/code/macosx/*`
  - `src/code/null/*`
- Focused validation surface:
  - `tests/test_renderer_win32_host_glue_parity.py`
  - `tests/test_engine_cvar_retail_parity.py`
  - `tests/test_engine_host_support_full_parity_gate.py`
  - `tests/test_platform_services.py`

Method:

1. Treat the retail Windows executable as the only strict-parity owner.
2. Reuse the committed subsystem audits for already-closed Win32 bootstrap,
   clipboard, raw-input, loading-window, and Steamworks wrapper lanes instead
   of rescoring them blindly.
3. Re-check `win_glimp.c` and other renderer-facing Win32 host helpers against
   direct retail HLIL/decompile evidence because the earlier remaining-host
   audit intentionally excluded renderer-owned platform code.
4. Keep `unix`, `macosx`, and `null` explicitly classified as compatibility
   ports unless retail Windows evidence proves otherwise.

## Scope Boundary

Strict-retail Windows target:

- `src/code/win32/win_main.c`
- `src/code/win32/win_syscon.c`
- `src/code/win32/win_wndproc.c`
- `src/code/win32/win_input.c`
- `src/code/win32/win_net.c`
- `src/code/win32/win_glimp.c`
- `src/code/win32/win_gamma.c`
- `src/code/win32/win_qgl.c`
- `src/code/win32/win_shared.c`
- `src/code/win32/awesomium_process.cpp`

Compatibility-only or non-retail ports:

- `src/code/unix/*`
- `src/code/macosx/*`
- `src/code/null/*`

Interpretation:

- The strict parity score below tracks the Windows platform-specific engine
  surface that exists in retail `quakelive_steam.exe`.
- Unix, macOS, and null remain useful portability lanes, but they are not
  part of the retail Windows replacement target.

## Current Verified State

Already-closed Windows platform lanes reaffirmed during this audit:

1. `win_main.c`, `win_syscon.c`, and `win_wndproc.c` remain strongly bounded
   by mapping round `98` and the host/support audit. The loading-window,
   console, quit, error, and windowed resize/restart paths still match the
   committed retail evidence.
2. `win_input.c` and the adjacent `win_wndproc.c` raw-input dispatch remain
   source-backed and test-backed through the focused raw-input harness and the
   host/support gate.
3. `win_main.c` keeps the Unicode-first clipboard path that was already closed
   in the remaining host/support audit.
4. `win_glimp.c` keeps the previously recovered maximized-window restart
   behavior and aspect-ratio preset publication path that the renderer host
   glue tests already cover.

Compatibility-only lanes reaffirmed:

1. `src/code/unix/*`, `src/code/macosx/*`, and `src/code/null/*` are still
   valuable for portability, tooling, and cross-platform builds.
2. None of those trees are owned by the retail Windows executable, so they do
   not count against the strict Windows parity score in this audit.

## Newly Confirmed Strict-Retail Gap

### PS-G01 - `win_glimp.c` pixel-format auto-selection drifted away from retail

**Status before this task:** Open  
**Status after this task:** Closed

Retail evidence anchors:

- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
  around `FUN_00469e40`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
  for the imported GDI and WGL pixel-format owners

Observed retail behavior:

1. The retail helper logs `"...GLW_AutoSelectPFD( %d, %d, %d )\n"` before the
   fallback enumeration path.
2. When `glConfig.driverType == GLDRV_ICD`, retail uses the GDI
   `ChoosePixelFormat` path for auto-selection and `DescribePixelFormat` for
   enumeration.
3. When `glConfig.driverType > GLDRV_ICD`, retail switches to
   `wglChoosePixelFormat` and `wglDescribePixelFormat`.

Observed pre-patch source divergence:

1. The current source only attempted auto-selection for
   `glConfig.driverType > GLDRV_ICD`, so the normal ICD path skipped the retail
   `ChoosePixelFormat` stage entirely.
2. The current source hardwired the enumeration/query path to
   `DescribePixelFormat`, even when retail switches to the WGL owner for
   standalone/minidriver drivers.

Why this mattered:

- The pre-patch code was still functional, but it changed the strict-retail
  PFD selection and query owner split in the most common Windows ICD path.
- That made the old broad “renderer host glue is fully closed” claim slightly
  overstated for this narrow helper band.

Closure implemented in this task:

1. Restored the retail `GLW_AutoSelectPFD` stage in `src/code/win32/win_glimp.c`.
2. Re-enabled the GDI `ChoosePixelFormat` branch for ICD drivers.
3. Switched the `DescribePixelFormat` helper to preserve the retail GDI-vs-WGL
   split while still guarding both paths with exception handling.
4. Updated the focused renderer host-glue test so the recovered ICD/WGL owner
   split is now regression-tested.

## Remaining Observations

No other high-confidence strict-retail Windows platform gap was confirmed in
this pass.

Notes:

1. The Win32 SMP/render-thread helper band still contains generic thread and
   event helpers in the retail binary, but this audit did not find enough
   direct two-signal evidence to tie those helper bodies back to a concrete
   `win_glimp.c` behavioral gap beyond the already-closed active runtime path.
2. Unix/macOS/null remain intentionally non-retail and should stay classified
   that way unless a future audit changes the target definition itself.

## Parity Estimate

- Strict platform-specific Windows engine parity before this task: **99%**
- Strict platform-specific Windows engine parity after this task: **100%**

Interpretation:

- The remaining unscored platform trees are compatibility-only ports, not open
  retail Windows debt.
- After restoring the retail PFD auto-selection owner split, this audited
  platform-specific Windows surface no longer has an open strict-retail gap.
