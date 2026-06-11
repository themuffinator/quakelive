# Quake Live Steam Host Mapping Round 603

Date: 2026-06-11

## Scope

Rechecked the VM mouse consumer bridge after the Win32 and client mouse-input
passes. This round covers the retail UI and cgame mouse consumers that receive
`CL_MouseEvent` payloads through `UI_MOUSE_EVENT`, `CG_MOUSE_EVENT`, and native
export tables.

## Evidence

Primary retail binaries:

- `uix86.dll` for `_UI_MouseEvent`, `Display_MouseMove`, and
  `Menu_HandleMouseMove`.
- `cgamex86.dll` for the `CG_MOUSE_EVENT` native slot and
  `CG_BrowserDisplayMouseMove`.

Committed corpus signals:

- UI Binary Ninja HLIL part 01 maps `sub_10010000` as `_UI_MouseEvent`: it
  projects host X/Y into the 640x480 virtual UI space, stores the display
  context cursor, rejects out-of-bounds virtual coordinates, and calls
  `sub_10020740` (`Display_MouseMove`) when menus are active.
- UI HLIL maps `sub_10020740` as the retail null-menu `Display_MouseMove`
  router. It prioritizes the focused popup root and otherwise walks all active
  menus through `sub_1001d600` (`Menu_HandleMouseMove`).
- UI Ghidra rows retain the consumer helpers:
  `FUN_1001d600` size `426`, `FUN_10020740` size `173`, and
  `FUN_100208f0` size `249`.
- Cgame Binary Ninja HLIL maps `sub_10063830` as the browser-display mouse
  motion fanout and the native export table slot at `data_100769c8` as
  `0x100208f0`.
- Cgame Ghidra carries `FUN_10063830` size `173`, matching the browser-display
  mouse fanout helper.

## Mapping Updates

The source and alias maps already separated the two module-local meanings of
`0x100208f0`, but this round makes that split explicit:

| Retail module | Raw symbol | Normalized owner | Evidence summary |
| --- | --- | --- | --- |
| `uix86.dll` | `FUN_100208f0` | `Menu_OverActiveItem` | UI menu hover hit-test helper. |
| `cgamex86.dll` | `sub_100208f0` | `CG_MouseEvent` | Cgame native mouse-event table entry. |
| `uix86.dll` | `sub_10010000` | `_UI_MouseEvent` | Absolute host coordinate projection into UI 640x480 space. |
| `cgamex86.dll` | `FUN_10063830` | `CG_BrowserDisplayMouseMove` | Browser-overlay mouse motion fanout. |

Updated the UI symbol-map comment for `_UI_MouseEvent` from the older inferred
delta-accumulator wording to the observed absolute coordinate projection. Also
updated the cgame `CG_MouseEvent` signature wording from `dx, dy` to `x, y` so
the map matches the reconstructed source and the host absolute-coordinate lane.

## Source Reconstruction

No C source change was needed in this round. The current source already matches
the retail consumer split:

- `src/code/ui/ui_main.c::_UI_MouseEvent` projects host screen coordinates with
  `UI_ConvertScreenCursorXToVirtual` and
  `UI_ConvertScreenCursorYToVirtual`, then forwards valid virtual cursor
  positions to `Display_MouseMove`.
- `src/code/ui/ui_shared.c::Display_MouseMove` stays on the retail null-menu
  route: focused popup first, otherwise all menus, with no GPL drag-path
  mutation.
- `src/code/cgame/cg_main.c` seeds `cgDC` from `cgs` in both the legacy
  `CG_MOUSE_EVENT` vmMain case and the native export wrapper.
- `src/code/cgame/cg_newdraw.c::CG_MouseEvent` applies the
  `cg_ignoreMouseInput` gate, spectator UI ownership, absolute host coordinate
  projection, 640x480 clamp, cursor-shape update, and
  `CG_BrowserDisplayMouseMove` dispatch.

## Validation

Added `tests/test_ui_menu_files.py` coverage that pins:

- UI and cgame alias-map separation for the colliding `0x100208f0` address.
- UI and cgame symbol-map comments/signatures for absolute mouse coordinates.
- UI and cgame Ghidra rows for the mapped consumer helpers.
- UI HLIL anchors for `_UI_MouseEvent`, `Display_MouseMove`, and the UI native
  export table.
- Cgame HLIL anchors for `CG_BrowserDisplayMouseMove` and the mouse native
  export-table slot.
- Source-side UI, cgame, and `VM_CallNativeExports` dispatch behavior.

No runtime launch was performed because this was a static mapping and source
reconstruction pass with direct HLIL, Ghidra, symbol-map, and source evidence.

## Parity Estimate

- Focused VM mouse consumer bridge evidence coverage: **92% -> 99%**.
- Focused UI/cgame mouse alias collision confidence: **70% -> 99%**.
- Repo-wide parity remains **99% -> 99%** because this closes a narrow mapping
  and validation gap without broadening the whole-codebase score.
