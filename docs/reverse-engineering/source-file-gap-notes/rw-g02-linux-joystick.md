# `src/code/unix/linux_joystick.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; Linux joystick support remains part of the unresolved non-Windows input host lane.

## Why this file is still open

The file still owns `/dev/js*` probing and axis-to-key translation, but that input path is not currently claimed as a closed portability surface in the repo-wide audit.

## Observed facts

- The startup path walks `/dev/js0` through `/dev/js3` to find a joystick device.
- Axis values are still translated into Quake-style key events through threshold checks.
- The repo-wide audit still treats Linux input support as part of the broader unresolved portability lane.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `IN_StartupJoystick` | `open portability owner` | This function belongs to the still-open Linux joystick/input lane. |
| `IN_JoyMove` | `open portability owner` | This function belongs to the still-open Linux joystick/input lane. |

## Closure target

- Do not close this file until the broader Linux input story is either validated or explicitly bounded permanently.
