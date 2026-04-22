# `src/code/null/null_glimp.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; the file is a compatibility-only null renderer host rather than a real graphics runtime.

## Why this file is still open

The file now carries the corrected renderer-host signatures, but every GL entry point is still empty or returns a compatibility-safe default, so the null runtime still lacks a real graphics host.

## Observed facts

- `GLimp_Init()`, `GLimp_EndFrame()`, and `GLimp_Shutdown()` are empty.
- `QGL_Init()` returns `qtrue` without loading a renderer library or binding real GL entry points.
- The repo-wide audit still states that the null runtime does not implement a real live graphics/audio/input host.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `GLimp_EndFrame` | `open portability owner` | No-op swap/end-frame path inside the null compatibility host. |
| `GLimp_Init` | `open portability owner` | No-op renderer-host initialisation; the null runtime creates no graphics context. |
| `GLimp_Shutdown` | `open portability owner` | No-op renderer-host teardown inside the null compatibility lane. |
| `GLimp_EnableLogging` | `bounded compatibility` | Null renderer-host compatibility shim. |
| `GLimp_LogComment` | `bounded compatibility` | Null renderer-host compatibility shim. |
| `QGL_Init` | `open portability owner` | Returns `qtrue` without loading or validating a real GL backend. |
| `QGL_Shutdown` | `bounded compatibility` | Null renderer-host compatibility shim. |

## Closure target

- Either keep the null renderer host as an explicit compatibility shim or raise it to a better-defined non-Windows graphics target.
- Do not close the file while the null runtime still lacks a real graphics context, swap path, and GL loader contract.
