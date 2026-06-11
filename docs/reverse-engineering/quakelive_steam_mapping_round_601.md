# Quake Live Steam Host Mapping Round 601

Date: 2026-06-11

## Scope

Extended the Windows mouse-input mapping from the backend acquisition owners
into the `MainWndProc` raw-message bridge. This pass focused on the
`WM_INPUT` / `GetRawInputData` handoff, the DirectInput/raw helper aliases that
were still missing Ghidra or lowercase Binary Ninja names, and the startup-safe
`in_mouse` read visible at the head of retail `MainWndProc`.

## Evidence

Primary owner: retail `quakelive_steam.exe`.

Committed corpus signals:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  identifies `FUN_004f1750` at `0x004F1750`, size `404`, matching the retail
  Win32 window procedure body.
- Binary Ninja HLIL part 05 starts `sub_4f1750` by reading the retained
  `in_mouse` pointer and substituting mode `0` when the pointer is null.
- The same HLIL owner handles `case 0xff` (`WM_INPUT`) by calling
  `GetRawInputData` once for size, using a 0x400 stack buffer when possible,
  allocating a heap buffer for larger packets, checking the returned byte
  count, and forwarding mouse packets into `sub_4ebaa0`.
- The retail import table includes `USER32.DLL!GetRawInputData`, and the
  adjacent backend owners remain `sub_4EBAA0`, `sub_4EB830`, and
  `sub_4EBBA0`.

## Mapping Updates

Promoted the remaining mouse-related symbols:

| Retail address | Alias | Evidence summary |
| --- | --- | --- |
| `0x004EA690` | `IN_DIMouse` | Buffered DirectInput mouse event drain, including X/Y axes, wheel key pairs, and `K_MOUSE1..K_MOUSE8`. |
| `0x004EB830` | `IN_RawInputMouse` | Drains retained raw samples into relative deltas, queues raw button/wheel events, clears the sample buffer, and recenters the host cursor. |
| `0x004EBBA0` | `IN_InitDIMouse` | Creates the DirectInput8 root/device, installs the mouse data format, sets exclusive foreground cooperation, and configures the 0x200 event buffer. |
| `0x004F1750` | `MainWndProc` | Owns Win32 window-message dispatch, including the retail `WM_INPUT` raw-data bridge into `IN_RawInputAppendSample`. |

For the `0x004EA390..0x004EC4F0` mouse owner band, the alias ledger now carries
the Ghidra `FUN_*` spellings and lowercase Binary Ninja `sub_*` spellings in
addition to the existing uppercase names.

## Source Reconstruction

- Added a small `WIN_GetMouseInputMode` helper in `win_wndproc.c` so early
  window messages follow retail behavior when `in_mouse` has not been
  registered yet: missing cvar pointer means mode `0`.
- Updated the `MSH_MOUSEWHEEL` and `WM_MOUSEWHEEL` gates to use that snapshot
  instead of dereferencing `in_mouse` directly.
- Kept the current source split where `MainWndProc` delegates `WM_INPUT` to
  `IN_RawInputEvent`; that helper mirrors the retail stack/heap raw packet
  path and forwards extracted mouse samples into the bounded raw queue.

## Validation

Added parity coverage in `tests/test_win32_raw_input_parity.py` for:

- `MainWndProc` aliases and Ghidra row;
- HLIL `WM_INPUT` anchors, including the 0x400 stack-buffer boundary and
  `sub_4ebaa0` sample-forwarding call;
- the source `WIN_GetMouseInputMode` null guard;
- the source `WM_INPUT` dispatch into `IN_RawInputEvent`;
- the remaining DirectInput/raw mouse helper `FUN_*` and lowercase aliases.

No runtime launch was performed. The change is a static host-input
reconstruction backed by HLIL/Ghidra evidence and parity tests.

## Parity Estimate

- Focused Win32 mouse message/raw dispatch parity: **95% -> 99%**.
- Focused Win32 mouse backend alias coverage: **88% -> 99%**.
- Repo-wide parity remains **99% -> 99%** because this closes a narrow host
  input exactness gap without broadening the project-wide score.
