# `src/code/unix/unix_main.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; several helpers are now bounded, but the broader Unix host still remains compatibility-only rather than retail-equivalent.

## Why this file is still open

This file has absorbed a lot of restoration work, yet its current state is still explicitly bounded: profiling is optional, clipboard access depends on host tools, `Sys_CheckCD()` is only a coarse data-root probe, and the surrounding Unix runtime is not claimed as a retail-equivalent client host.

## Observed facts

- `Sys_LowPhysicalMemory()`, `Sys_FunctionCmp()`, `Sys_FunctionCheckSum()`, `Sys_MonkeyShouldBeSpanked()`, bounded `gprof` hooks, clipboard retrieval, and `Sys_CheckCD()` are all restored in scoped form.
- The file still underpins a broader Unix runtime that the repo-wide audit explicitly classifies as compatibility-only rather than a closed retail replacement target.
- Optional profiling and environment-dependent clipboard helpers remain bounded host shims, not broad portability closure proof.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `Sys_QueryPhysicalMemoryBytes` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_LowPhysicalMemory` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_QueryFunctionBytes` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_FunctionCmp` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_FunctionCheckSum` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_PathHasReleaseMarker` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_MonkeyShouldBeSpanked` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ResolveProfilingHooks` | `bounded compatibility` | Optional `moncontrol` / `_mcleanup` path only exists when the host build enables profiling. |
| `Sys_SetProfilingEnabled` | `bounded compatibility` | Only meaningful inside the bounded optional profiling lane. |
| `Sys_BeginProfiling` | `bounded compatibility` | Restored, but still intentionally scoped to `QL_ENABLE_GPROF=1` hosts. |
| `Sys_EndProfiling` | `bounded compatibility` | Restored, but still intentionally scoped to `QL_ENABLE_GPROF=1` hosts. |
| `Sys_In_Restart_f` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `tty_FlushIn` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `tty_Back` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `tty_Hide` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `tty_Show` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ConsoleInputShutdown` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Hist_Add` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Hist_Prev` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Hist_Next` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_Printf` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_Exit` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_Quit` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_Init` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_Error` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_Warn` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_FileTime` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `floating_point_exception_handler` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ConsoleInputInit` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ConsoleInput` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_UnloadDll` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_LoadDll` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_InitStreamThread` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ShutdownStreamThread` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_BeginStreamedFile` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_EndStreamedFile` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_StreamedRead` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_StreamSeek` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_StreamThread` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_InitStreamThread` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ShutdownStreamThread` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_BeginStreamedFile` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_EndStreamedFile` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_StreamedRead` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_StreamSeek` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_QueEvent` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_GetEvent` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_PathHasBaseq3Asset` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_CheckCD` | `bounded compatibility` | Now a coarse data-root probe rather than an unconditional success stub, but still not a full portability closure claim. |
| `Sys_AppActivate` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_TrimClipboardText` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_IsExecutableOnPath` | `bounded compatibility` | Supports the bounded clipboard helper chain rather than a broad host-API abstraction. |
| `Sys_ReadClipboardCommand` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_GetClipboardData` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_Print` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ConfigureFPU` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_PrintBinVersion` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `Sys_ParseArgs` | `not currently implicated` | Recovered or retained helper not currently singled out as the active remaining portability blocker. |
| `main` | `compatibility host owner` | Top-level Unix host entry remains part of the broader still-open portability lane. |

## Closure target

- Finish deciding whether the Unix runtime is meant to reach client/runtime parity or remain a compatibility-only boundary.
- When that decision is made, rerun the full Unix file walk and split the still-bounded helpers from any truly closed retail-equivalent host functions.
