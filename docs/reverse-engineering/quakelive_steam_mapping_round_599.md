# Quake Live Steam Mapping Round 599: UI Script Sound Verb Closure

Date: 2026-06-11

## Scope

This round closes the UI-owner side of the menu script sound verb path. The
previous pass pinned the cgame browser wrappers that call into the shared script
helpers; this pass pins the retail `uix86.dll` helper bodies themselves:
`Script_Play`, `Script_playLooped`, and the `Item_RunScript` dispatcher that
reaches them from the UI script command table.

No C source behavior was changed. The source already matches the observed UI
sound wiring, and `src/ui/` remained read-only.

## Retail Evidence

Primary owner: `assets/quakelive/uix86.dll`

Evidence checked:

- Binary Ninja HLIL part 01:
  - `sub_10016cd0`: UI `Script_Play`.
  - `sub_10016d20`: UI `Script_playLooped`.
  - `sub_10016d70`: UI `Item_RunScript` dispatcher.
  - command table rows at `0x1002a0b0..0x1002a0bc`.
- Ghidra `functions.csv`:
  - `FUN_10016d70,10016d70,246,0,unknown`
  - no committed Ghidra function rows for the tiny `0x10016cd0` and
    `0x10016d20` wrapper bodies.
- Symbol alias map:
  - `sub_10016cd0` to `Script_Play`
  - `sub_10016d20` to `Script_playLooped`
  - `FUN_10016d70` to `Item_RunScript`

Observed HLIL signals:

- `sub_10016cd0` parses one script token, then calls the display-context
  register-sound callback at `+0xAC` and the local-sound callback at `+0x74`,
  passing channel `6`.
- `sub_10016d20` parses one script token, calls the stop-background callback at
  `+0xB4`, then calls the start-background callback at `+0xB0` with the same
  token for intro and loop.
- `sub_10016d70` owns the semicolon-delimited script loop, dispatches known
  commands through the command table rooted at `0x1002a018`, and falls back to
  the display-context `runScript` callback at `+0x50`.
- The table rows bind `"play"` to `sub_10016cd0` and `"playlooped"` to
  `sub_10016d20`.

## Source Reconstruction

Source owners:

- `src/code/ui/ui_shared.c` for the shared UI script helpers and command table.
- `src/code/ui/ui_main.c` for display-context callback wiring.

Pinned source contracts:

- `commandList` contains the retail `"play"` and `"playlooped"` verbs mapped to
  `Script_Play` and `Script_playLooped`.
- `Item_RunScript` copies the script into the 2048-byte UI script buffer,
  dispatches matched command handlers, and falls back to `DC->runScript(&p)`.
- `Script_Play` parses one token, registers it with `qfalse`, and starts it on
  `CHAN_LOCAL_SOUND`.
- `Script_playLooped` stops the active background track and restarts it with the
  same token for intro and loop.
- `_UI_Init` wires the display-context callbacks used by these helpers:
  `trap_S_RegisterSound`, `trap_S_StartLocalSound`,
  `trap_S_StartBackgroundTrack`, and `trap_S_StopBackgroundTrack`.

## Tests

Expanded `tests/test_ui_menu_files.py`:

- Added `UI_FUNCTIONS` so UI tests can read the committed Ghidra function rows.
- Added
  `test_ui_script_sound_verbs_match_retail_hlil_and_display_context_callbacks`
  to tie the UI aliases, Ghidra dispatcher row/no-row boundary, BN HLIL helper
  bodies and table rows, reconstructed `ui_shared.c` helpers, and `_UI_Init`
  display-context sound callback assignments together.

## Validation

- `python -m pytest tests/test_ui_menu_files.py::test_ui_sound_import_wiring_matches_retail_native_and_vm_paths tests/test_ui_menu_files.py::test_ui_script_sound_verbs_match_retail_hlil_and_display_context_callbacks -q --tb=short`

## Confidence

Observed facts:

- BN HLIL supplies the UI helper bodies, callback offsets, command strings, and
  command table pointers.
- Ghidra confirms the `Item_RunScript` dispatcher row and size.
- The source path uses the same display-context callbacks and preserves the
  same command-table shape.

Inference:

- `sub_10016cd0` and `sub_10016d20` should remain alias-backed tiny wrapper
  identities unless a future Ghidra export promotes stable rows for them. The
  source reconstruction is still high confidence because the HLIL body, command
  table, display-context offsets, and shared helper source all agree.

Parity estimates:

- Focused UI script sound verb wiring confidence: **before 72% -> after 98%**.
- Focused UI sound command-table and display-context callback confidence:
  **before 90% -> after 98%**.
- Overall sound-system wiring reconstruction parity: **93.58% -> 93.60%**.
