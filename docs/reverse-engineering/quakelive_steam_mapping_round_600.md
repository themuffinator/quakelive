# Quake Live Steam Host Mapping Round 600

Date: 2026-06-11

## Scope

Rechecked the retail Windows mouse-input stack from platform acquisition
through client mouse dispatch, focusing on `quakelive_steam.exe` ownership and
the already-reconstructed Win32/source paths.

## Evidence

Primary owner: retail `quakelive_steam.exe`.

Committed corpus signals:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  identifies the Windows retail host (`function_count=5473`) and the Win32
  compiler/language target.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt` includes
  `DINPUT8.DLL!DirectInput8Create`, `USER32.DLL!RegisterRawInputDevices`,
  `USER32.DLL!GetRawInputData`, `USER32.DLL!GetRawInputDeviceList`,
  `USER32.DLL!GetRawInputDeviceInfoA`, `USER32.DLL!ClipCursor`,
  `USER32.DLL!SetCapture`, `USER32.DLL!ScreenToClient`, and
  `USER32.DLL!SetCursorPos`.
- Binary Ninja HLIL part 05 maps the platform mouse owners:
  `sub_4EBB20` registers the raw mouse device (`usagePage=1`, `usage=2`) and
  sets `in_mouseMode` to `win32(Raw)`;
  `sub_4EBAA0` appends bounded raw samples while clearing the queue outside the
  relative gameplay lane;
  `sub_4EB830` drains samples into relative deltas and queues mouse button and
  wheel keys;
  `sub_4EBBA0` calls `DirectInput8Create(..., 0x800, ...)` and configures the
  0x200-entry buffered DirectInput mouse stream;
  `sub_4EC030` either queues absolute client coordinates through
  `ScreenToClient` or relative deltas through raw/DirectInput/Win32 backends;
  and `sub_4EC4F0` owns the per-frame activation/deactivation policy.
- The client-side owner remains `sub_4B54E0` / `CL_MouseEvent` for routing and
  `sub_4B5800` / `CL_MouseMove` for CPI, acceleration, sensitivity cap, and
  view-angle filtering.

## Mapping Updates

Added aliases for the contiguous Win32 mouse owner band:

| Retail address | Alias | Evidence summary |
| --- | --- | --- |
| `0x004EA390` | `IN_UpdateWin32MouseClip` | Clamps the window rectangle, recenters the cursor, conditionally clips, and writes `vid_xpos`/`vid_ypos`. |
| `0x004EA480` | `IN_ActivateWin32Mouse` | Hides the OS cursor, refreshes the clip/center state, and calls `SetCapture`. |
| `0x004EA4B0` | `IN_Win32Mouse` | Reads `GetCursorPos`, optionally recenters, and returns center-relative deltas. |
| `0x004EA540` | `IN_ShutdownDIMouse` | Releases DirectInput mouse/root interfaces and resets `in_mouseMode` to `win32`. |
| `0x004EA590` | `IN_ActivateDIMouse` | Rebinds DirectInput cooperative level, acquires the device, and sets `DirectInput` mode. |
| `0x004EAA80` | `IN_MouseEvent` | Converts the retained 8-bit Win32 button mask into `K_MOUSE1..K_MOUSE8` key events. |
| `0x004EBAA0` | `IN_RawInputAppendSample` | Stores up to `0x1ff` raw samples and reports debug overflow. |
| `0x004EBB20` | `IN_InitRawInput` | Registers the raw mouse device and updates `in_mouseMode`. |
| `0x004EBE40` | `IN_DeactivateMouse` | Releases relative capture, shows cursor, unregisters raw input, and unacquires DirectInput. |
| `0x004EBEE0` | `IN_StartupMouse` | Selects raw input, DirectInput, or Win32 fallback and handles delayed startup. |
| `0x004EC030` | `IN_MouseMove` | Queues absolute or relative `SE_MOUSE` payloads depending on catcher/capture state. |
| `0x004EC160` | `IN_Startup` | Runs mouse, joystick, and MIDI startup. |
| `0x004EC1D0` | `IN_Shutdown` | Shuts down mouse, DirectInput, raw input, MIDI, and input commands. |
| `0x004EC2A0` | `IN_Init` | Registers input cvars and commands, including `in_mouse 2` and `in_raw_useWindowHandle`. |
| `0x004EC470` | `IN_Activate` | Writes the app-active latch and deactivates mouse capture. |
| `0x004EC490` | `IN_ActivateMouse` | Activates the selected relative mouse backend and Win32 capture. |
| `0x004EC4F0` | `IN_Frame` | Pumps joystick input, delayed mouse startup, capture policy, and mouse movement. |

## Source Reconstruction

- Updated the Win32 DirectInput path from the old Quake III
  `dinput.dll` / `DirectInputCreateA` loader to `dinput8.dll` /
  `DirectInput8Create` with `DIRECTINPUT_VERSION 0x0800`.
- Switched the source handles and calls to the DirectInput8 interface macros
  while preserving the reconstructed 0x200 buffered mouse event stream,
  `DIDEVICEOBJECTDATA` processing, eight mouse buttons, and wheel translation.
- Kept raw input as the default backend (`in_mouse 2`) and retained the Win32
  cursor warp path as the documented fallback.

## Validation

- Added `tests/test_win32_raw_input_parity.py` coverage for the DirectInput8
  initialization path, old loader removal, and the new retail owner aliases.
- No runtime launch was performed. The change is static mouse acquisition
  reconstruction, and the HLIL/Ghidra evidence directly resolves the backend
  selection and function ownership.

## Parity Estimate

- Focused Win32 mouse acquisition/dispatch parity: **97% -> 99%**.
- Repo-wide parity remains **99% -> 99%** because this closes a narrow host
  input exactness gap without changing the broader validation-freshness score.
