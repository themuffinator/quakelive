# Retail input translation audit

The retail Windows client drives keyboard and mouse dispatch through the Win32
message pump (`TranslateMessage`/`DispatchMessageA`) before forwarding input to
UI or client game consumers. The HLIL export confirms the pipeline stays inside
the default Win32 loop and therefore expects character messages to arrive as
Unicode payloads produced by the OS rather than the raw key codes emitted by
the platform layer.【F:references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt†L10101-L10108】

Key and character translation follows the same rules exposed by the retail loop
and retains the ASCII/Unicode payload used by Quake Live. The new translation
helper keeps printable keys intact (covering both ASCII and higher-plane
codepoints) while normalising uppercase ASCII to lowercase when dispatching
virtual keys into UI or client game handlers. Printable keys are also surfaced
as character payloads and gated behind `K_CHAR_FLAG` to mirror the retail menu
stack, which expects already-shifted characters when handling WM_CHAR events.

Mouse movement splits into two retail paths. The event dispatcher recovered as
`sub_4B54E0` first gates on `AdvertisementBridge_IsDelayElapsed`, then checks
`cg_ignoreMouseInput`, the recovered browser keycatcher bit (`0x20`),
`KEYCATCH_UI`, and `KEYCATCH_CGAME` before
falling through to gameplay accumulation when no catcher is active except the
retail `0x10` pass-through bit. `CL_MouseEvent` passes the queued payloads
directly to those browser/UI/cgame routes; the previous client-side retained
absolute-cursor accumulator was an inferred compatibility layer and is no
longer treated as retail behavior. The Windows host still chooses which payload
shape to queue: while capture is active and the catcher mask is clear except
for message/pass-through bits, it queues relative deltas; when browser/UI/cgame
capture, `in_nograb`, inactive focus, or the windowed console releases capture,
it queues `ScreenToClient` client-area coordinates for the absolute cursor lane.
The absolute lane keeps cursor ownership split the same way: the browser host may
publish a native Win32 cursor while its `0x20` catcher is active, but UI/cgame
catchers use the renderer-drawn game cursor and force the OS cursor to `NULL`
over the client area until that game cursor owner clears.
The cgame-owned join-game overlay projects those host coordinates back into
the shared 640x480 cursor space and preserves any existing console catcher bit
when it arms `KEYCATCH_CGAME`, so toggling the console does not immediately
drop back into the join-menu-only state.
Mouse buttons follow the same split: raw-input button samples are only retained
for the relative gameplay lane, while browser/UI/cgame catcher states use the
Win32 button-state messages to synthesize `K_MOUSE*` key events. That keeps the
cgame join-game overlay on the same click path as ordinary menus instead of
dropping clicks whenever raw input is the active mouse backend.
The retained browser host now produces the same browser catcher bit from the
frame/hide/reset owners: active browser frames arm `0x20`, and hide/reset paths
clear it.

Mouse button numbering now follows the recovered retail key-name table through
`MOUSE9`, so `MOUSE6` through `MOUSE9` occupy the range before `MWHEELDOWN`,
`MWHEELUP`, and `JOY1`. The Win32 fallback path maps `MK_XBUTTON1` and
`MK_XBUTTON2` into the same contiguous key range, and the DirectInput buffered
path accepts button offsets through `DIMOFS_BUTTON7`.

Keyboard dispatch follows the same recovered catcher ownership. `CL_KeyEvent`
no longer feeds browser pointer/key events as an unconditional side channel;
console capture wins first, browser capture owns the next route, then UI,
message, cgame, disconnected-console, and finally normal bindings. ESC closes
the retained browser host while `KEYCATCH_BROWSER` is active, matching the
retail `sub_4B7B00` browser-hide branch instead of opening the normal menu.
The same owner now applies the recovered demo-playback shortcuts while
`clc.demoplaying` is active and the catcher mask is clear except for the retail
`0x10` pass-through bit: space toggles `cl_freezeDemo`, down or mouse3 resets
`timescale`, left/wheel-down decrements timescale, right/wheel-up increments or
single-steps a frozen demo, and delete toggles `cg_drawDemoHUD`.

The host keyboard and character-input bridge is pinned from the Win32 message
layer through the VM consumers. `MapKey` extracts the scan code and extended-key
bit from `lParam`, keeps the retail keypad remaps, and feeds `MainWndProc`
`SE_KEY` events for key up/down while `WM_CHAR` queues `SE_CHAR` with the
OS-produced character payload. `Sys_GetEvent` records the Win32 message
timestamp before `TranslateMessage` and dispatch, `Sys_QueEvent` owns queue
overflow cleanup and timestamp fallback, and `Com_EventLoop` dispatches the
result into `CL_KeyEvent` or `CL_CharEvent`. The client handlers then route
browser, UI, cgame, console, message, disconnected-console, and binding paths in
the retail priority order; the UI and cgame DLLs expose matching native
key-event wrappers around `_UI_KeyEvent` and `CG_KeyEvent`.

The gameplay side of `CL_MouseMove` uses the more specific retail movement
formula recovered from `sub_4B5800`: raw counts are first scaled by
`2.5399999618530273 / m_cpi` when CPI is enabled, rate calculation then
multiplies by `1000`, CPI-enabled yaw/pitch application uses the retail
`45.45454545454546` axis multiplier, and signed `cl_mouseAccel` either adds to
or subtracts from sensitivity before the cap check. The retained `m_filter`
cvar is also a view-angle history filter, not a two-frame raw-delta average.
The client owner band is pinned as `CL_MouseEvent` (`0x004B54E0`),
`CL_BeginMouseFilter` (`0x004B5640`), `CL_EndMouseFilter` (`0x004B5710`), and
`CL_MouseMove` (`0x004B5800`), with Ghidra `FUN_*`, uppercase Binary Ninja
`sub_*`, and lowercase Binary Ninja `sub_*` aliases all present in the shared
symbol ledger.

The VM consumer bridge is pinned on both DLL sides. UI `_UI_MouseEvent`
projects host screen coordinates into 640x480 virtual cursor space, bounds
checks that virtual cursor, and forwards valid motion into `Display_MouseMove`.
Cgame seeds `cgDC` from the retained `cgs` cursor in both the `CG_MOUSE_EVENT`
vmMain case and the native export wrapper, then `CG_MouseEvent` projects,
clamps, updates cursor-shape state, and routes motion through
`CG_BrowserDisplayMouseMove`. The shared alias ledger deliberately keeps
`uix86.dll` `FUN_100208f0` as `Menu_OverActiveItem` while
`cgamex86.dll` `sub_100208f0` remains `CG_MouseEvent`; the same virtual address
belongs to different retail modules and must not be merged by address alone.
The cgame browser-widget consumer band is now pinned as the next input layer:
`CG_BrowserDisplayMouseMove` and `CG_BrowserHandleMouseMove` feed overlay roots,
while focus, hover, listbox, slider, text-field, bind, multi, preset-list,
out-of-bounds click, and overlay key handlers retain their cgame-scoped wrapper
owners. This keeps browser overlay motion and key dispatch tied to the retail
`0x1005a1a0..0x100638e0` owner band instead of collapsing it into generic UI
item helpers.

The Windows backend ownership is now mapped across the retail host band around
`0x004EA390..0x004EC4F0`. Raw input remains the default (`in_mouse 2`), the
DirectInput fallback uses the retail `DINPUT8.DLL!DirectInput8Create` interface
and a `0x200` buffered event stream, and the classic Win32 lane is retained as
the final fallback for center-relative gameplay deltas or absolute client
coordinates when a UI/browser/cgame catcher owns the cursor.
The raw-message handoff is pinned at `MainWndProc` / `sub_4f1750`: retail reads
the `in_mouse` cvar pointer defensively, handles `WM_INPUT` with
`GetRawInputData`, uses a `0x400` stack buffer before heap fallback, and then
forwards mouse packets into the retained raw-sample appender. The source keeps
that packet parsing in `IN_RawInputEvent`, but the routing and guard semantics
now match the retail owner.

The remaining Win32 device input lane is mapped through the same owner band.
`IN_StartupJoystick` probes WinMM joystick devices with `joyGetNumDevs`,
`joyGetPosEx`, and `joyGetDevCapsA`, publishes `ui_joyavail`, and
`IN_JoyMove` translates buttons into `K_JOY*`, hat/secondary axes into
direction keys, side/forward analog motion into `SE_JOYSTICK_AXIS`, and R/U
look axes into ordinary `SE_MOUSE` events. `Com_EventLoop` then dispatches
`SE_JOYSTICK_AXIS` into `CL_JoystickEvent`, and `CL_CreateCmd` applies stored
axis state after mouse movement through `CL_JoystickMove`. The adjacent MIDI
bridge is also pinned: `MidiInProc` gates note messages by `in_midichannel`,
maps notes from middle C into the `K_AUX*` key range, and opens WinMM through
`IN_StartupMIDI` only when `in_midi` is enabled.

### Captured retail samples

The translation helpers are validated against representative samples derived
from the HLIL traces and manual probes:

| Sample | Raw input | Translated output | Rationale |
| --- | --- | --- | --- |
| Uppercase printable | `key='A' (0x41)` | `dispatchKey='a'`, `charCode=0x41` | Retail UI paths consume lowercase key codes for bindings while WM_CHAR preserves the shifted character. |
| Unicode text | `key=0x20AC` (€) | `dispatchKey=0x20AC`, `charCode=0x20AC` | The Win32 pump emits Unicode payloads; the helper keeps the codepoint intact for UTF-8 UI consumers. |
| CPI helper scaling | `dx=1`, `m_cpi=500` | `translatedDx=2` | The standalone conversion helper preserves the recovered `1000 / m_cpi` sample for harness coverage; `CL_MouseEvent` itself passes the host-queued payload without client-side cursor translation. |

These examples are exercised in `tests/test_input_translation.py` to ensure
future changes preserve the retail mappings.
