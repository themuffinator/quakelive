# `src/code/null/null_input.c` Gap Note

Last updated: 2026-05-17

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; the file exposes bootstrap cvars but still resolves to a no-device input shim.

## Why this file is still open

The file now touches the modern input cvar surface and keeps `ui_joyavail` plus the joystick modified latch honest, but it still represents a no-device compatibility path rather than a real input host.

## Observed facts

- The current null input path seeds `in_mouse`, `in_nograb`, `in_joystick`, `in_debugjoystick`, and `joy_threshold` cvars.
- `IN_NullRefreshCompatibilityState()` clears `in_joystick->modified` and pins `ui_joyavail` to `0`, making the no-device joystick state explicit across init, frames, shutdown, and key-event polling.
- `Sys_SendKeyEvents()` now refreshes the no-device compatibility state when null input is initialized, but still emits no real key events.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `IN_NullTouchCompatibilityCvars` | `bounded compatibility` | Null-input compatibility shim. |
| `IN_NullRefreshCompatibilityState` | `bounded compatibility` | Maintains the explicit no-device input state and clears the retained joystick modified latch. |
| `IN_Init` | `open portability owner` | Initialises only the null input compatibility cvars and no-device state. |
| `IN_Frame` | `open portability owner` | No real input pump; only refreshes null compatibility state. |
| `IN_Shutdown` | `bounded compatibility` | Null-input shutdown shim. |
| `Sys_SendKeyEvents` | `open portability owner` | Refreshes the no-device state but still emits no real key events. |

## Closure target

- Either keep the null input layer explicitly no-op or promote it to a better-defined host target; do not blur the current boundary.
