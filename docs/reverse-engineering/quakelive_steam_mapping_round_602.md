# Quake Live Steam Host Mapping Round 602

Date: 2026-06-11

## Scope

Rechecked the client-owned mouse input corridor after the Win32 acquisition and
raw-message passes. This round covers `CL_MouseEvent`, the retained mouse
filter helpers, and `CL_MouseMove` against the retail
`quakelive_steam.exe` Binary Ninja HLIL and Ghidra function rows.

## Evidence

Primary owner: retail `quakelive_steam.exe`.

Committed corpus signals:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains the client mouse owner rows:
  `FUN_004b54e0` size `141`, `FUN_004b5640` size `197`,
  `FUN_004b5710` size `236`, and `FUN_004b5800` size `968`.
- Binary Ninja HLIL part 04 maps `sub_4b54e0` as the mouse event router:
  advertisement-delay gate, `cg_ignoreMouseInput`, browser catcher `0x20`, UI
  catcher `0x2`, cgame catcher `0x8`, then gameplay accumulation only when the
  catcher mask is clear except for the retail mouse-pass bit.
- The adjacent HLIL owners `sub_4b5640` and `sub_4b5710` are the retained
  `m_filter` begin/end helpers: clamp `m_filter` to `0..31`, reset history on
  modified cvar state, restore the base yaw/pitch before movement, then store
  and average view-angle history.
- `sub_4b5800` owns the gameplay mouse movement math: file-backed
  `cl_mouseAccelDebug`, `m_cpi / 2.5399999618530273` CPI scaling,
  CPI-enabled rate multiplier `1000.0`, signed `cl_mouseAccel`, power
  `cl_mouseAccelPower - 1.0`, `cl_mouseSensCap`, and the filter begin/end calls.

## Mapping Updates

Promoted the remaining client mouse aliases:

| Retail address | Alias | Evidence summary |
| --- | --- | --- |
| `0x004B54E0` | `CL_MouseEvent` | Routes queued mouse payloads through browser, UI, cgame, or gameplay accumulation. |
| `0x004B5640` | `CL_BeginMouseFilter` | Clamps/reset-retains `m_filter` state and restores base view angles before movement. |
| `0x004B5710` | `CL_EndMouseFilter` | Records and averages retained yaw/pitch history after movement. |
| `0x004B5800` | `CL_MouseMove` | Applies CPI, acceleration, sensitivity, FOV scale, command movement, and view-angle deltas. |

The alias ledger now carries Ghidra `FUN_*`, uppercase Binary Ninja `sub_*`,
and lowercase Binary Ninja `sub_*` spellings for those four owners.

## Source Reconstruction

No source code change was needed in this round. The current source already
matches the retail owner split:

- `CL_MouseEvent` does not perform CPI translation or absolute cursor
  accumulation before UI/cgame/browser dispatch.
- `CL_MouseMove` owns CPI, acceleration, sensitivity cap, cgame sensitivity,
  mlook/freelook pitch routing, and `m_filter` begin/end calls.
- The `cl_viewAccel` multiplier remains absent from `CL_MouseMove`, matching
  the retained retail body.

## Validation

Added `tests/test_engine_client_command_parity.py` coverage that pins:

- the widened `CL_MouseEvent` / `CL_BeginMouseFilter` / `CL_EndMouseFilter` /
  `CL_MouseMove` aliases;
- the Ghidra rows and HLIL anchors for the four owners;
- source routing order for advertisement delay, ignore cvar, browser, UI,
  cgame, and gameplay accumulation;
- `m_filter` clamp/reset/average behavior;
- CPI, acceleration, sensitivity cap, and yaw/pitch/command movement source
  wiring.

No runtime launch was performed because the pass was static client input
mapping with direct source and corpus evidence.

## Parity Estimate

- Focused client mouse routing/filter/math evidence coverage: **96% -> 99%**.
- Focused client mouse alias coverage: **70% -> 99%**.
- Repo-wide parity remains **99% -> 99%** because this closes a narrow mapping
  and validation gap without broadening the whole-codebase score.
