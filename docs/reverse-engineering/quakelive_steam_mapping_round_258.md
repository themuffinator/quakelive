# Quake Live Steam Host Mapping Round 258

## Scope

This round follows the `CL_MouseEvent` reconstruction from round 257 and
revisits the sibling key dispatcher at `sub_4B7B00` / `CL_KeyEvent`.

The specific question was whether browser key, mouse-button, and wheel routing
should run as an unconditional retained side channel, or only when the recovered
browser keycatcher bit (`0x20`) owns input.

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_101.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_257.md`

## `sub_4B7B00`: Browser-Aware `CL_KeyEvent`

Observed corpus facts:

1. Round 101 already promoted `sub_4B7B00` as `CL_KeyEvent`, and the Ghidra
   body still exposes the same owner at `FUN_004b7b00`.
2. The retail owner updates the key down/repeat counters before dispatch, then
   handles the hard-coded console key and ESC branch.
3. On ESC down, retail checks `data_1528ba4 & 0x20` before the normal menu path.
   When the browser state is live, it calls `sub_4F24D0`, already promoted as
   `QLWebHost_HideBrowser`.
4. For key-up events, retail first runs `CL_AddKeyUpCommands`, then routes
   browser-owned input through `sub_4F3420` only when `(keyCatchers & 0x20) != 0`
   and the console catcher is not active. UI and cgame key-up dispatch remain
   after that branch.
5. For key-down events, the recovered order is:
   - console
   - browser `0x20`
   - UI
   - message
   - cgame
   - disconnected console
   - normal binding execution
6. `sub_4F3420` is already promoted as `QLWebView_PublishGameKey`, but its HLIL
   is broader than that name suggests: it also forwards browser-owned mouse
   button presses/releases to `sub_4F27C0` / `sub_4F2820` and wheel motion to
   `sub_4F2870`.
7. The current source had been calling the retained browser key/button/wheel
   entrypoints before normal key routing, even when `KEYCATCH_BROWSER` was not
   set. No matching unconditional side channel appears in the retail owner.

## Source Reconstruction

Implemented source changes:

1. `src/code/client/cl_keys.c` now centralizes browser-owned key routing in
   `CL_DispatchBrowserKeyEvent()`. That helper preserves the retained split
   between:
   - `CL_WebView_OnMouseButtonEvent`
   - `CL_WebView_OnMouseWheelEvent`
   - `CL_WebView_OnKeyEvent`
2. `CL_KeyEvent` no longer calls those browser entrypoints unconditionally.
3. Key-up dispatch now follows the recovered browser-before-UI/cgame path while
   preserving the console-catcher exclusion.
4. Key-down dispatch now follows the recovered console -> browser -> UI ->
   message -> cgame -> disconnected-console -> binding order.
5. ESC while `KEYCATCH_BROWSER` is active now calls the public
   `CL_WebHost_HideBrowser()` wrapper and returns before normal menu toggling.
6. `src/code/client/cl_cgame.c` keeps the retail-named `QLWebHost_HideBrowser`
   helper private and exposes only the narrow wrapper needed by `cl_keys.c`.

## What Stays Open

The same retail owner also contains demo-playback key controls guarded by
`clc.demoplaying` and `(keyCatchers & ~0x10) == 0`: pause, timescale reset,
timescale step down/up, and demo HUD toggle. Round 259 closes that key-event
sublane while recording the remaining whole-engine key-number reconciliation as
a separate source/UI boundary question.

## Validation

Commands run:

- `python -m pytest tests/test_awesomium_browser_parity.py tests/test_platform_services.py tests/test_input_translation.py tests/test_engine_client_command_parity.py -q --tb=short`
  - Result: `114 passed in 6.07s`
- `python -m pytest tests/test_client_full_parity_gate.py tests/test_client_config_parity.py tests/test_engine_netcode_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `88 passed, 1 skipped in 5.60s`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json > $null`
  - Result: alias JSON parsed successfully.
- `git diff --check`
  - Result: no whitespace errors; Git reported existing LF-to-CRLF conversion
    warnings for dirty text files.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
  - Result: the touched client batch compiled, including `cl_cgame.c`,
    `cl_input.c`, `cl_keys.c`, and `cl_main.c`; the project then stopped in
    the known unrelated `src/code/win32/win_net.c` `WSAEVENT` /
    `ip_socket_event` errors.

No runtime launch was performed. The HLIL/Ghidra evidence and focused tests
were sufficient for this key-routing reconstruction.

## Parity Estimate

Strict engine `client` parity remains **100% -> 100%**. This round removes a
source-only browser input side channel from a high-traffic dispatcher and makes
the browser catcher semantics consistent across mouse and key routing.

Repo-wide retail parity remains **98% -> 98%** because the remaining gaps are
outside this focused engine-client key/browser route.
