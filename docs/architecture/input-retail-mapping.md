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

Mouse deltas pass through the CPI-aware scaling observed in the retail cvar
initialisation block. The HLIL snapshot seeds `cl_mouseAccel*`, `cl_mouseSensCap`,
and the CPI conversion toggle via `m_cpi`, matching the existing client-side
scaling path.【F:references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt†L18290-L18339】
UI and cgame consumers now receive the CPI-adjusted deltas so menu motion and
native overlays observe the same scaling as the retail binary, while gameplay
accumulation continues to capture the raw device deltas for later acceleration
and sensitivity processing.

### Captured retail samples

The translation helpers are validated against representative samples derived
from the HLIL traces and manual probes:

| Sample | Raw input | Translated output | Rationale |
| --- | --- | --- | --- |
| Uppercase printable | `key='A' (0x41)` | `dispatchKey='a'`, `charCode=0x41` | Retail UI paths consume lowercase key codes for bindings while WM_CHAR preserves the shifted character. |
| Unicode text | `key=0x20AC` (€) | `dispatchKey=0x20AC`, `charCode=0x20AC` | The Win32 pump emits Unicode payloads; the helper keeps the codepoint intact for UTF-8 UI consumers. |
| CPI scaling | `dx=1`, `m_cpi=500` | `translatedDx=2` | Retail mouse deltas are multiplied by `1000 / m_cpi` before reaching menu handlers, mirroring the HLIL CPI conversion block. |

These examples are exercised in `tests/test_input_translation.py` to ensure
future changes preserve the retail mappings.
