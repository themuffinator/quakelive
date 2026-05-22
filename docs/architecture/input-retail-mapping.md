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
`sub_4B54E0` first gates on `cg_ignoreMouseInput`, then checks the recovered
browser keycatcher bit (`0x20`), `KEYCATCH_UI`, and `KEYCATCH_CGAME` before
falling through to gameplay accumulation when no catcher is active except the
retail `0x10` pass-through bit. `CL_MouseEvent` passes the queued payloads
directly to those browser/UI/cgame routes; the previous client-side retained
absolute-cursor accumulator was an inferred compatibility layer and is no
longer treated as retail behavior. The Windows host still chooses which payload
shape to queue: while capture is active and the catcher mask is clear except
for message/pass-through bits, it queues relative deltas; when browser/UI/cgame
capture, `in_nograb`, inactive focus, or the windowed console releases capture,
it queues `ScreenToClient` client-area coordinates for the absolute cursor lane.
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

The gameplay side of `CL_MouseMove` uses the more specific retail movement
formula recovered from `sub_4B5800`: raw counts are first scaled by
`2.5399999618530273 / m_cpi` when CPI is enabled, rate calculation then
multiplies by `1000`, CPI-enabled yaw/pitch application uses the retail
`45.45454545454546` axis multiplier, and signed `cl_mouseAccel` either adds to
or subtracts from sensitivity before the cap check. The retained `m_filter`
cvar is also a view-angle history filter, not a two-frame raw-delta average.

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
