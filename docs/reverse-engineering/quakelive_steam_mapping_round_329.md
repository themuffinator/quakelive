# Quake Live Steam Host Mapping Round 329

Date: 2026-05-27

## Scope

Investigated Win32 mouse capture and sensitivity state after toggling
fullscreen/windowed mode through `vid_restart fast`.

## Evidence

Primary owner: retail `quakelive_steam.exe`.

Committed corpus signals:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  identifies the Windows retail host with `5473` functions and the expected
  DirectInput/User32 imports.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  shows `CL_Vid_Restart_f @ 0x004BB7E0` calling the mouse deactivation owner
  `sub_4EBE40` immediately before `GLW_ChangeWindowMode @ 0x0046BC70`.
- The same fast-restart branch does not call `IN_Activate @ 0x004EC470`; that
  matters because `IN_Activate` writes the app-active latch before tail-calling
  `sub_4EBE40`.
- `IN_Frame @ 0x004EC4F0` releases relative mouse capture whenever
  `cls.keyCatchers & ~0x14` is non-zero, when `in_nograb` is set, or when the
  app-active latch is false, then falls through to the relative activation path
  only for gameplay-relative mouse movement.
- `IN_MouseMove @ 0x004EC030` posts absolute client coordinates while a
  non-gameplay catcher owns the mouse, matching the retained source
  `IN_WindowMouse` lane.

## Source Reconstruction

- `WIN_FastVidRestart` now calls `IN_DeactivateMouse()` directly instead of
  `IN_Activate( qfalse )`, preserving `in_appactive` across the mode switch.
- `IN_Activate` now mirrors retail by writing `in_appactive` and always forcing
  a capture reset through `IN_DeactivateMouse()`.
- `IN_Frame` now uses the retail keycatcher mask
  `KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS` to decide whether relative
  mouse capture is allowed, instead of the old windowed-console/3Dfx special
  case.

## Validation

- `python -m pytest tests/test_win32_raw_input_parity.py tests/test_renderer_win32_host_glue_parity.py tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentysecond_renderer_startup_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyseventh_renderer_extension_startup_tranche_matches_retail_contracts -q --tb=short`
  - Result: `25 passed`.
- No runtime launch was performed. Static HLIL/Ghidra evidence directly
  resolves this ownership path, and fullscreen launches are prohibited.

## Parity Estimate

- Focused Win32 fullscreen-toggle mouse lane: **94% -> 99%**.
- Repo-wide parity remains **98% -> 98%** because this closes a narrow host
  input/state divergence without changing the broader open compatibility lanes.
