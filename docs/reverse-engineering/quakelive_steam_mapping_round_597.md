# Quake Live Steam Mapping Round 597: Cgame Browser Script Sound Verb Closure

Date: 2026-06-11

## Scope

This round closes the retail evidence bridge for cgame browser script sound
verbs. The previous sound-parser pass pinned authored `focusSound` and
`soundLoop` tokens; this pass pins runtime script actions that play sound:
`play` for one-shot local sound playback and `playlooped` for menu background
track restart.

No C source behavior was changed. The current source already routes these
browser script verbs through the shared UI script helpers and display-context
sound callbacks.

## Retail Evidence

Primary owner: `assets/quakelive/cgamex86.dll`

Evidence checked:

- Binary Ninja HLIL:
  - `sub_10059eb0`: cgame browser `play` script verb wrapper.
  - `sub_10059f00`: cgame browser `playlooped` script verb wrapper.
  - `sub_10059f50`: cgame browser script dispatcher.
  - script command table rows at `0x100750b0..0x100750bc`.
- Ghidra `functions.csv`:
  - `FUN_10059f50,10059f50,246,0,unknown`
- Symbol alias map:
  - cgame aliases: `sub_10059eb0` to `CG_BrowserScriptPlay`
  - cgame aliases: `sub_10059f00` to `CG_BrowserScriptPlayLooped`
  - cgame aliases: `FUN_10059f50` / `sub_10059f50` to
    `CG_RunBrowserScript`
  - UI-owner helper aliases: `sub_10016cd0` to `Script_Play` and
    `sub_10016d20` to `Script_playLooped`

Observed HLIL signals:

- `sub_10059eb0` parses one script token, then calls the display-context sound
  registration callback and the local-sound callback.
- `sub_10059f00` parses one script token, calls the stop-background callback,
  then restarts the background track using the same token for intro and loop.
- `sub_10059f50` copies a script buffer, walks the cgame browser script command
  table, calls matched handlers through `data_1007501c`, and falls back to the
  display-context `runScript` callback for unmatched verbs.
- The retail command table binds `"play"` to `sub_10059eb0` and
  `"playlooped"` to `sub_10059f00`.

## Source Reconstruction

Source owners:

- `src/code/cgame/cg_newdraw.c` for cgame browser script dispatch wrappers.
- `src/code/ui/ui_shared.c` for shared `Script_Play` and `Script_playLooped`
  behavior.
- `src/code/cgame/cg_main.c` for display-context sound callback wiring.

Pinned source contracts:

- `CG_RunBrowserScript` owns a cgame-local command table and dispatches
  `"play"` and `"playlooped"` through `CG_BrowserScriptPlay` and
  `CG_BrowserScriptPlayLooped`.
- The cgame browser wrappers call the shared helpers:
  - `Script_Play((itemDef_t *)widget, args)`
  - `Script_playLooped((itemDef_t *)widget, args)`
- `Script_Play` registers the parsed sound with `qfalse` compression and starts
  it on `CHAN_LOCAL_SOUND`.
- `Script_playLooped` stops the current background track and starts a new
  background track with the same token for intro and loop.
- `CG_InitDisplayContext` wires the callback targets used by this path:
  `trap_S_StartLocalSound`, `trap_S_StartBackgroundTrack`,
  `trap_S_StopBackgroundTrack`, and `CG_RunMenuScript`.

## Tests

Expanded `tests/test_cgame_sound_wiring_parity.py`:

- `test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets`
  now covers `CG_BrowserScriptPlay`, `CG_BrowserScriptPlayLooped`, and
  `CG_RunBrowserScript`.
- Added
  `test_cgame_browser_script_sound_verbs_pin_local_and_looped_playback_wiring`
  to tie the UI helper aliases, cgame aliases, Ghidra dispatcher row, BN HLIL
  command table, cgame wrappers, shared sound helpers, and display-context
  sound callbacks together.

## Validation

- `python -m pytest tests/test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets tests/test_cgame_sound_wiring_parity.py::test_cgame_browser_script_sound_verbs_pin_local_and_looped_playback_wiring -q --tb=short`

## Confidence

Observed facts:

- BN HLIL supplies the `play` and `playlooped` command strings, table pointers,
  wrapper bodies, and dispatcher fallback behavior.
- Ghidra confirms the dispatcher function row and size.
- The source path uses the same display-context sound callbacks as the retail
  wrappers and keeps unmatched script verbs on the `runScript` fallback.

Inference:

- The cgame browser wrappers are intentionally thin source-side adapters around
  shared UI script helpers. Keeping the UI helper aliases and cgame wrapper
  aliases separate is the most faithful ownership model for the reconstructed
  source.

Parity estimates:

- Focused cgame browser script sound verb wiring confidence:
  **before 68% -> after 98%**.
- Focused cgame sound script alias/table confidence:
  **before 84% -> after 98%**.
- Overall sound-system wiring reconstruction parity: **93.56% -> 93.58%**.
