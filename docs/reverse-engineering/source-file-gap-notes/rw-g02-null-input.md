# `src/code/null/null_input.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; the file exposes bootstrap cvars but still resolves to a no-device input shim.

## Why this file is still open

The file now touches the modern input cvar surface and keeps `ui_joyavail` honest, but it still represents a no-device compatibility path rather than a real input host.

## Observed facts

- The current null input path seeds `in_mouse`, `in_nograb`, `in_joystick`, `in_debugjoystick`, and `joy_threshold` cvars.
- `IN_Frame()` only refreshes the compatibility state; it does not drive a real input backend.
- `Sys_SendKeyEvents()` remains empty.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `IN_NullTouchCompatibilityCvars` | `bounded compatibility` | Null-input compatibility shim. |
| `IN_NullRefreshCompatibilityState` | `open portability owner` | Maintains the explicit no-device input state. |
| `IN_Init` | `open portability owner` | Initialises only the null input compatibility cvars. |
| `IN_Frame` | `open portability owner` | No real input pump; only refreshes null compatibility state. |
| `IN_Shutdown` | `bounded compatibility` | Null-input shutdown shim. |
| `Sys_SendKeyEvents` | `open portability owner` | Still empty, so the null runtime has no real key-event pump. |

## Closure target

- Either keep the null input layer explicitly no-op or promote it to a better-defined host target; do not blur the current boundary.
