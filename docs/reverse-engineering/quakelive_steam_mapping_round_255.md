# quakelive_steam.exe Mapping Round 255

Date: 2026-05-18

Scope: a focused reread of the engine-owned client input owner
`sub_4B5800` / `CL_MouseMove`, plus adjacent client cvar-registration wiring
in `CL_Init`.

## Summary

This round did not add new aliases. It tightened an already-mapped client
owner where the source still carried a source-only `cl_mouseAccelStyle` cvar
and a console-print placeholder for `cl_mouseAccelDebug`, while the committed
retail corpus exposes a file-backed mouse acceleration diagnostic path.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The source-parity wins are:

- [`cl_input.c`](../../src/code/client/cl_input.c) now mirrors the retained
  `cl_mouseAccelDebug` file lifecycle: open `fs_homepath/mouse.log` on enable,
  write the retail header and per-frame numeric rows, and close the file when
  the cvar is disabled.
- [`cl_main.c`](../../src/code/client/cl_main.c) and
  [`client.h`](../../src/code/client/client.h) no longer declare or register
  the source-only `cl_mouseAccelStyle` cvar, which has no matching retail
  string or cvar-table entry.

## Evidence Notes

Observed facts from the committed retail corpus:

- Round 123 already mapped `sub_4B5800` to `CL_MouseMove` with high
  confidence.
- The alias ledger still maps `sub_4B5800 -> CL_MouseMove`.
- The `quakelive_steam` Ghidra function corpus records
  `FUN_004b5800,004b5800,968`, matching the large retained input owner.
- HLIL for `sub_4B5800` reads the retained `cl_mouseAccelDebug` cvar before
  mouse movement processing.
- When `cl_mouseAccelDebug` is enabled and the retained file pointer is null,
  the retail owner builds `fs_homepath` + empty game dir + `mouse.log`, opens
  it with mode `w`, and writes `mx my frame_msec rate power\n`.
- When `cl_mouseAccelDebug` is disabled and the retained file pointer is
  non-null, the retail owner closes the file and clears the pointer.
- During debug frames, the retail owner writes `%g %g %d ` for mouse deltas
  and `frame_msec`, conditionally writes `%g %g ` for the acceleration rate
  and power-style values, then writes a trailing newline.
- The retained `CL_Init` cvar table registers `cl_mouseAccel`,
  `cl_mouseAccelDebug`, `cl_mouseAccelOffset`, `cl_mouseAccelPower`, and
  `cl_mouseSensCap`.
- No committed HLIL, Ghidra decompile, string table, or cvar-registration
  search found `cl_mouseAccelStyle`.

Source-side inference used this round:

- `FS_BuildOSPath( homepath, "", "mouse.log" )` is the appropriate source
  reconstruction for the recovered retail path builder call, because the
  companion Ghidra decompile passes `"fs_homepath"`, the empty string, and
  `"mouse.log"` into the same filesystem path-building lane.
- The broader retail acceleration formula still deserves a separate pass.
  This round intentionally limits behavior changes to the directly evidenced
  debug-file lifecycle and cvar-table cleanup.

## Source Reconstruction

- [`cl_input.c`](../../src/code/client/cl_input.c) adds
  `cl_mouseAccelDebugLog` plus small open/close/write helpers for the retained
  mouse diagnostic file.
- [`cl_input.c`](../../src/code/client/cl_input.c) routes `CL_MouseMove`
  through the debug-file updater and row writer instead of printing a
  source-only console diagnostic.
- [`cl_input.c`](../../src/code/client/cl_input.c) removes the stale
  `cl_mouseAccelStyle` TODO block from the movement path.
- [`cl_main.c`](../../src/code/client/cl_main.c) removes the source-only
  `cl_mouseAccelStyle` cvar storage and `Cvar_Get` registration.
- [`client.h`](../../src/code/client/client.h) removes the corresponding
  extern declaration.
- [`tests/test_engine_cvar_retail_parity.py`](../../tests/test_engine_cvar_retail_parity.py)
  now pins the file-backed debug path and absence of `cl_mouseAccelStyle`.
- [`docs/client_cvars.md`](../client_cvars.md) and the client parity audit now
  document the debug-file contract and cvar-table cleanup.

## Verification

Static/source validation:

- `python -m pytest tests/test_engine_cvar_retail_parity.py tests/test_engine_client_command_parity.py -q --tb=short`
  passed with `51 passed`
- `python -m pytest tests/test_client_full_parity_gate.py tests/test_client_config_parity.py tests/test_engine_netcode_parity.py tests/test_platform_services.py -q --tb=short`
  passed with `88 passed, 1 skipped`
- `git diff --check` reported only the repository's existing LF -> CRLF
  normalization warnings
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
  compiled the touched client source batch including `cl_input.c`, then failed
  in the unrelated existing `win_net.c` `WSAEVENT` / `ip_socket_event`
  declarations before link

No runtime launch was performed. This patch is bounded to statically
recoverable cvar and file-diagnostic wiring, and the committed HLIL/Ghidra
evidence was sufficient.

Alias accounting after this pass:

- current `quakelive_steam` aliases: `2238` raw entries, `2231`
  strict address-backed aliases
- strict Ghidra address-backed coverage: `40.764%` of `5473` committed
  functions

Parity estimate after this pass:

- strict `client` parity: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

The score stays flat because the client parity gate was already closed, but
the classic input lane now has stronger source-level fidelity and less
source-only cvar drift.

## Next Queue Head

The next useful client-owned pass is to finish a deeper `CL_MouseMove`
algorithm comparison for the CPI scaling and positive/negative mouse
acceleration formula, because this round only changed the directly evidenced
debug-file lifecycle and unsupported cvar registration.
