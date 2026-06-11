# Quake Live mapping round 605: Win32 keyboard and character-input bridge

Date: 2026-06-11

## Scope

This pass closes the remaining mapping gap around keyboard and character input
after the mouse, raw input, joystick, and MIDI passes. The reviewed path is:

1. Win32 scancode mapping in `MapKey` / `sub_4f15c0`.
2. `MainWndProc` key, system-key, and character message queueing.
3. `Sys_QueEvent` / `Sys_GetEvent` timestamp and queue ownership.
4. `Com_EventLoop` dispatch into client key and char handlers.
5. `CL_KeyEvent` / `CL_CharEvent` routing into browser, UI, cgame, console,
   message, and binding consumers.
6. UI and cgame native key-event export wrappers.

## Retail evidence

Primary Binary Ninja HLIL anchors:

- `quakelive_steam.exe` part 05:
  - `004f15c0` is the static `MapKey` owner.
  - `004ed050` is `Sys_QueEvent`.
  - `004ed0e0` is `Sys_GetEvent`; it assigns the Win32 message timestamp before
    `TranslateMessage` and `DispatchMessageA`.
  - `004f1750` is `MainWndProc`, including the Alt+Enter
    `vid_restart fast\n` branch.
- `quakelive_steam.exe` part 04:
  - `004b71c0` is `CL_CharEvent`, with UTF-16 to UTF-8 conversion and
    console/UI/message routing.
  - `004b7b00` is `CL_KeyEvent`, with key-state tracking, demo-playback
    shortcuts, browser, UI, cgame, console, message, and binding routing.
- `uix86.dll` part 01:
  - `1000ff40` is `_UI_KeyEvent`.
  - `1002aeac` exports that handler through the UI native slot table.
- `cgamex86.dll`:
  - `1003c6f0` is `CG_KeyEvent`.
  - `100769c4` exports that handler through the cgame native slot table.

Ghidra confirms `FUN_004b6890`, `FUN_004b71c0`, `FUN_004b7b00`,
`FUN_004ed050`, `FUN_004f1750`, and `FUN_1003c6f0` rows. `MapKey` and the UI
`_UI_KeyEvent` name are HLIL/symbol-map anchored static owners rather than
Ghidra-promoted function rows.

## Mapping updates

`references/analysis/quakelive_symbol_aliases.json` now includes the missing
`FUN_*`, uppercase `sub_*`, and lowercase `sub_*` spellings for:

- `Field_CharEvent`
- `CL_CharEvent`
- `CL_KeyEvent`
- `Sys_QueEvent`
- `MapKey`
- `_UI_KeyEvent`
- `CG_KeyEvent`

The UI and cgame aliases stay module-scoped because the same virtual addresses
can name unrelated owners in different retail DLLs.

## Source reconstruction status

No runtime source patch was required for this slice. The current source already
matches the recovered retail wiring:

- `win_wndproc.c` extracts scan code and extended-key state in `MapKey`,
  preserves keypad remaps, queues `SE_KEY` for key up/down, queues `SE_CHAR`
  for `WM_CHAR`, and handles Alt+Enter as the retail fullscreen restart path.
- `win_main.c` stores event queue entries with overflow cleanup and stamps
  Win32 messages into `g_wv.sysMsgTime` before dispatch.
- `common.c` sends `SE_KEY`, `SE_CHAR`, `SE_MOUSE`, and `SE_JOYSTICK_AXIS` to
  the recovered client owners.
- `cl_keys.c` keeps key-state accounting, demo-playback shortcuts, browser/UI
  and cgame routing, binding execution, and UTF-8 character fanout.
- `ui_main.c` and `cg_main.c` provide native key-event wrappers matching the
  retained legacy VM command entries.

## Validation

Added `test_win32_keyboard_character_event_and_vm_key_wiring_match_retail_evidence`
to `tests/test_win32_raw_input_parity.py`. The test cross-checks:

- alias spellings;
- Ghidra function rows;
- HLIL anchors for the host, UI, and cgame modules;
- source-level queue, dispatch, routing, and native-wrapper calls.

Focused validation:

```text
python -m pytest tests/test_win32_raw_input_parity.py::test_win32_keyboard_character_event_and_vm_key_wiring_match_retail_evidence -q --tb=short
1 passed
```

## Parity estimate

- Focused Win32 keyboard/character evidence coverage: before 88% -> after 99%.
- Focused key/char alias coverage: before 45% -> after 99%.
- Focused VM key-consumer bridge confidence: before 94% -> after 99%.
- Repo-wide parity estimate remains 99% -> 99%; this pass improves evidence
  coverage and regression protection rather than changing runtime behavior.
