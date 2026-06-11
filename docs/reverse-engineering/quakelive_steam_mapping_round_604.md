# Quake Live Steam Host Mapping Round 604

Date: 2026-06-11

## Scope

Rechecked the non-mouse Win32 device-input wiring after the mouse acquisition,
client mouse, and VM mouse-consumer passes. This round covers joystick and MIDI
input owners in the retail `quakelive_steam.exe` host, plus the common event
loop and client command-builder wiring that consumes joystick axis events.

## Evidence

Primary owner: retail `quakelive_steam.exe`.

Committed corpus signals:

- Ghidra imports include the WinMM joystick APIs `joyGetNumDevs`,
  `joyGetPosEx`, and `joyGetDevCapsA`, and the MIDI APIs `midiInOpen`,
  `midiInStart`, `midiInClose`, `midiInGetNumDevs`, and
  `midiInGetDevCapsA`.
- Ghidra function rows pin the joystick owners:
  `FUN_004eacd0` size `444` (`IN_StartupJoystick`), `FUN_004eae90` size `81`
  (`JoyToF`), and `FUN_004eaef0` size `1536` (`IN_JoyMove`).
- Ghidra function rows pin the MIDI owners:
  `FUN_004eb520` size `41` (`MIDI_NoteOff`), `FUN_004eb550` size `93`
  (`MIDI_NoteOn`), `FUN_004eb5b0` size `131` (`MidiInProc`),
  `FUN_004eb640` size `282` (`MidiInfo_f`), and `FUN_004eb770` size `189`
  (`IN_StartupMIDI`).
- Binary Ninja HLIL part 05 shows joystick startup clearing `ui_joyavail`,
  probing devices with `JOY_RETURNCENTERED`, reading capabilities, and setting
  `ui_joyavail` on success. The same part maps `IN_JoyMove` as the
  `JOY_RETURNALL` poller that emits `K_JOY*`, direction-key, `SE_JOYSTICK_AXIS`,
  and `SE_MOUSE` events.
- Binary Ninja HLIL part 05 also shows `MIDI_NoteOff`, `MIDI_NoteOn`,
  `MidiInProc`, `MidiInfo_f`, and `IN_StartupMIDI`: note events are remapped
  to the `K_AUX*` range, the callback gates by channel, and startup opens WinMM
  with `CALLBACK_FUNCTION`.
- Binary Ninja HLIL part 04 anchors the client consumers
  `CL_JoystickEvent` (`0x004B5570`) and `CL_JoystickMove` (`0x004B55B0`).

## Mapping Updates

Promoted the missing raw-name spellings into the shared alias ledger:

| Retail address | Alias | Evidence summary |
| --- | --- | --- |
| `0x004B5570` | `CL_JoystickEvent` | Stores joystick axis events and preserves the retail bad-axis error string. |
| `0x004B55B0` | `CL_JoystickMove` | Applies retained axis state during usercmd construction. |
| `0x004EACD0` | `IN_StartupJoystick` | WinMM joystick probe and `ui_joyavail` publication. |
| `0x004EAE90` | `JoyToF` | Centers and clamps WinMM axis values to `-1..1`. |
| `0x004EAEF0` | `IN_JoyMove` | Polls joystick state and emits key, joystick-axis, and mouse-look events. |
| `0x004EB520` | `MIDI_NoteOff` | Releases the mapped `K_AUX*` key for a MIDI note. |
| `0x004EB550` | `MIDI_NoteOn` | Presses the mapped `K_AUX*` key for a MIDI note, with zero velocity as note-off. |
| `0x004EB5B0` | `MidiInProc` | WinMM callback that gates note messages by configured channel. |
| `0x004EB640` | `MidiInfo_f` | Console info command for MIDI state and device capabilities. |
| `0x004EB770` | `IN_StartupMIDI` | Enumerates MIDI input devices and opens the selected callback device. |

Each promoted owner now carries the Ghidra `FUN_*`, uppercase Binary Ninja
`sub_*`, and lowercase Binary Ninja `sub_*` spellings.

## Source Reconstruction

No C source change was needed in this round. The current source already keeps
the device-input split aligned with the retail evidence:

- `IN_Init` registers the joystick cvars, MIDI cvars, and `midiinfo` command.
- `IN_Startup` runs mouse, joystick, then MIDI startup and clears the mouse and
  joystick modified latches.
- `IN_StartupJoystick` probes WinMM joystick devices, clears/publishes
  `ui_joyavail`, and records the selected joystick capabilities.
- `IN_JoyMove` emits joystick button key events, direction-key events, analog
  movement as `SE_JOYSTICK_AXIS`, and R/U look axes as `SE_MOUSE`.
- `Com_EventLoop` routes `SE_JOYSTICK_AXIS` to `CL_JoystickEvent`.
- `CL_CreateCmd` applies `CL_MouseMove` first and `CL_JoystickMove` afterward.
- `MidiInProc` converts MIDI note-on/off messages into `K_AUX*` key events and
  `IN_StartupMIDI` keeps MIDI disabled unless `in_midi` is enabled.

## Validation

Added `tests/test_win32_raw_input_parity.py` coverage that pins:

- joystick and MIDI alias spellings;
- WinMM import evidence;
- Ghidra function rows for joystick, MIDI, input init/frame, and client
  joystick consumers;
- Binary Ninja HLIL anchors for joystick startup, axis normalization, joystick
  polling, MIDI note mapping, MIDI callback/startup, cvar registration, and
  client joystick consumers;
- source-side cvar registration, joystick startup/polling, MIDI startup and
  shutdown, common event-loop dispatch, and client command-builder ordering.

Updated the existing client-command mapping gate so the widened
`CL_JoystickEvent` and `CL_JoystickMove` aliases are checked alongside the
older client input owners.

No runtime launch was performed because this was static mapping and
source-reconstruction validation with direct committed HLIL, Ghidra, import,
alias, and source evidence.

## Parity Estimate

- Focused non-mouse Win32 device-input evidence coverage: **86% -> 98%**.
- Focused joystick/MIDI alias coverage: **40% -> 99%**.
- Focused input event-loop wiring confidence: **94% -> 99%**.
- Repo-wide parity remains **99% -> 99%** because this closes a narrow mapping
  and validation gap without broadening the whole-codebase score.
