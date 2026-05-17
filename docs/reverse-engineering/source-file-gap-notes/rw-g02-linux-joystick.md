# `src/code/unix/linux_joystick.c` Gap Note

Last updated: 2026-05-17

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; Linux joystick support remains part of the unresolved non-Windows input host lane.

## Why this file is still open

The file still owns Linux joystick device probing and axis-to-key translation, but that input path is not currently claimed as a closed portability surface in the repo-wide audit. The current source now bounds the retained Linux joystick host more tightly, but it is still not a modern SDL/input-stack replacement.

## Observed facts

- The startup path now prefers `/dev/input/js0` through `/dev/input/js3` before the historical `/dev/js0` through `/dev/js3` device nodes.
- Axis values are still translated into Quake-style key events through threshold checks, now capped to the 8 axis / 16 direction-key range represented by the retained `joy_keys` table.
- `IN_ShutdownJoystick()` releases queued joystick keys, closes `joy_fd`, clears the tracked axis/button state, and resets `ui_joyavail`; `linux_glimp.c` now calls that shutdown path when input shuts down or when the latched `in_joystick` cvar restarts the joystick lane.
- Button event translation is capped to `K_JOY1` through `K_JOY32`, matching the exposed Quake key range instead of trusting arbitrary Linux event numbers.
- The repo-wide audit still treats Linux input support as part of the broader unresolved portability lane.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `IN_ClearJoystickState` | `bounded compatibility` | Tracks bounded axis/button state reset for the retained Linux joystick lane. |
| `IN_ReleaseJoystickKeys` | `bounded compatibility` | Releases queued joystick key state on shutdown/restart so stale device state does not leak into later input frames. |
| `IN_TryOpenJoystick` | `bounded compatibility` | Opens one candidate Linux joystick device, reports its capability metadata, and sets `ui_joyavail` on success. |
| `IN_StartupJoystick` | `open portability owner` | Still owns the unresolved Linux joystick startup lane, now bounded to explicit modern and historical js device probes. |
| `IN_ShutdownJoystick` | `bounded compatibility` | Closes the retained Linux joystick descriptor and clears the UI availability bridge. |
| `IN_JoyMove` | `open portability owner` | Still owns Linux joystick event translation, with capped button and axis ranges but no modern input abstraction. |

## Closure target

- Do not close this file until the broader Linux input story is either validated or explicitly bounded permanently. The descriptor cleanup, `ui_joyavail` bridge, and event caps reduce compatibility debt but do not close Linux input parity.
