# `src/code/null/null_main.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; this is a compatibility-only null host, not a retail-equivalent runtime.

## Why this file is still open

The file now carries more of the current host contract than the old stale null runtime did, but it is still explicitly a null compatibility host rather than a real runtime replacement path.

## Observed facts

- The file now preserves executable-name, path, wall-clock, directory, and stream helpers that match current host expectations more closely.
- `Sys_GetGameAPI()` still returns `NULL`, and `Sys_GetClipboardData()` still returns `NULL`.
- The repo-wide audit still classifies the null runtime as compatibility-only rather than part of the closed Windows replacement target.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `Sys_CurrentWallClockMilliseconds` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_CopyDirectoryName` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_BeginStreamedFile` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_EndStreamedFile` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_StreamedRead` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_StreamSeek` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_Error` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_Quit` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_UnloadGame` | `bounded compatibility` | No-op null-host lifecycle stub. |
| `Sys_GetGameAPI` | `open portability owner` | Returns `NULL`, so the null runtime still cannot stand in for a real module host. |
| `Sys_GetClipboardData` | `open portability owner` | Returns `NULL`; clipboard remains absent in the null host. |
| `Sys_Print` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_DisplaySystemConsole` | `bounded compatibility` | No-op null-host console shim. |
| `Sys_SetErrorText` | `bounded compatibility` | No-op null-host error-text shim. |
| `Sys_ExecutableBaseName` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_Milliseconds` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_Mkdir` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_Cwd` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_SetDefaultCDPath` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_DefaultCDPath` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_SetDefaultInstallPath` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_DefaultInstallPath` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_SetDefaultHomePath` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_DefaultHomePath` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_GetCurrentUser` | `bounded compatibility` | Compatibility-only null-host helper. |
| `Sys_Init` | `bounded compatibility` | Initialises the null host path but does not close the portability lane. |
| `Sys_EarlyOutput` | `bounded compatibility` | Compatibility-only null-host helper. |
| `main` | `open portability owner` | Top-level null runtime entry remains part of the unresolved compatibility-only host lane. |

## Closure target

- Either keep the null host as a permanent compatibility shim or raise it to a better-defined portability target with explicit non-null host contracts.
- Until then, treat the file as evidence that the repo-wide score still excludes non-Windows/null host equivalence.
