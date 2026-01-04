# Implementation Plan

This plan outlines the steps required to close the parity gaps identified in `AUDIT.md`.

## Task 1: Physics Parity (PQL Air Control)
**Priority:** Critical
**File:** `src/code/game/bg_pmove.c`

The current `pm_aircontrol` implementation in `PM_Accelerate` is a simplified approximation. To support PQL (Turbo) and CPMA movement correctly, we must implement the standard `PM_AirControl` function.

### Subtasks:
1.  **Define `PM_AirControl`**: Create a new static function `PM_AirControl` in `bg_pmove.c`.
    *   Logic should calculate the dot product of velocity and wish direction.
    *   Apply velocity redirection based on `pm_aircontrol` magnitude and `pml.frametime`.
    *   Ensure it only applies when a strafe input is present (optional, but typical for CPMA) or matches QL behavior (always active if `pm_aircontrol > 0`).
2.  **Integrate into `PM_AirMove`**:
    *   Modify `PM_AirMove` to call `PM_AirControl` *instead* of `PM_Accelerate` when `pm_aircontrol > 0`.
    *   Alternatively, call it alongside `PM_Accelerate` if that matches QL's specific "Turbo" flavor (needs verification, but replacement is standard for CPMA).
3.  **Clean up `PM_Accelerate`**: Remove the partial "soft" air control logic from `PM_Accelerate` to avoid double application or interference.

## Task 2: UI & UX State
**Priority:** Medium
**File:** `src/code/ui/ui_quakelive_bridge.c`

With the removal of legacy menus, we must ensure the bridge handles basic navigation commands or provides feedback.

### Subtasks:
1.  **Console Helpers**: Ensure `Cmd_Map_f` provides clear feedback when factories are missing.
2.  **Bridge Verification**: Review `ui_quakelive_bridge.c` to confirm it doesn't hard-crash when web UI is missing.

## Task 3: Final Verification
**Priority:** Low

1.  **Damage Timelines**: Run `tests/test_damage_timelines.py` to ensure weapon config changes didn't regress damage events.
2.  **Race Logic**: Verify `g_race.c` compiles and links correctly with the `bg_pmove.c` changes.
