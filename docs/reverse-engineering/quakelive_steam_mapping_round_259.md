# Quake Live Steam Host Mapping Round 259

## Scope

This round continues the `sub_4B7B00` / `CL_KeyEvent` reconstruction after the
browser-catcher pass in round 258. The focused target is the demo-playback
shortcut block that sits between the ESC branch and normal key routing in the
retail owner.

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_101.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_258.md`

## `sub_4B7B00`: Demo-Playback Shortcuts

Observed corpus facts:

1. Round 101 already promoted `sub_4B7B00` as `CL_KeyEvent`; the Ghidra owner
   remains `FUN_004b7b00` at `0x004B7B00`.
2. After the hard-coded console and ESC branches, retail enters a
   demo-playback-only block when `clc.demoplaying` is nonzero and the event is a
   key-down event.
3. The demo shortcut block is additionally guarded by
   `(keyCatchers & ~0x10) == 0`, so console, UI, message, cgame, and browser
   capture all suppress these playback controls while the recovered `0x10`
   pass-through bit is allowed.
4. The recovered commands are:
   - space: `toggle cl_freezeDemo`
   - down arrow or mouse3: `timescale 1`
   - left arrow or wheel down: `cvarAdd timescale -0.1`
   - right arrow or wheel up: `cvarAdd timescale 0.1`
   - right arrow or wheel up while frozen: `timescale 1; cl_freezeDemo 0; wait; wait; cl_freezeDemo 1`
   - delete: `toggle cg_drawDemoHUD`
5. Retail appends each command through `Cbuf_ExecuteText(EXEC_APPEND, ...)`.
6. The older GPL client behavior that mapped arbitrary demo-playback keys to
   ESC is not present in this recovered retail block.

## Key-Number Boundary

The committed retail key-name table shows Quake Live added `MOUSE6` through
`MOUSE9`, shifting wheel and joystick numbers relative to the older GPL enum.
The table maps `MWHEELDOWN` to `0xBB`, `MWHEELUP` to `0xBC`, and `JOY1` to
`0xBD`.

Follow-up input parity work resolved this boundary in `src/code/ui/keycodes.h`
by inserting `K_MOUSE6` through `K_MOUSE9` before the wheel and joystick ranges.
That path is distinct from the repository's read-only `src/ui/` tree, so the
retail key-number reconciliation no longer remains open.

## Source Reconstruction

Implemented source changes:

1. `src/code/client/cl_keys.c` now has `CL_HandleDemoPlaybackKeyEvent()` with
   the recovered demo guard:
   `clc.demoplaying && (cls.keyCatchers & ~KEYCATCH_RETAIL_MOUSEPASS) == 0`.
2. The helper appends the recovered `cl_freezeDemo`, `timescale`, and
   `cg_drawDemoHUD` command strings with `EXEC_APPEND`.
3. Right-arrow or wheel-up on a frozen demo now queues the retail single-frame
   advance sequence before refreezing.
4. `CL_KeyEvent` calls the helper after ESC special handling and before normal
   key-up/key-down dispatch.
5. The source-only demo-playback half of the old
   `clc.demoplaying || cls.state == CA_CINEMATIC` any-key-to-ESC branch was
   removed; the cinematic branch remains in place.

## Validation

Commands run:

- `python -m pytest tests/test_engine_client_command_parity.py tests/test_input_translation.py tests/test_awesomium_browser_parity.py tests/test_engine_cvar_retail_parity.py -q --tb=short`
  - Result: `75 passed in 0.68s`
- `python -m pytest tests/test_client_full_parity_gate.py tests/test_client_config_parity.py tests/test_engine_netcode_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `88 passed, 1 skipped in 6.19s`
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json > $null`
  - Result: alias JSON parsed successfully.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
  - Result: `cl_keys.c` compiled cleanly; the project then stopped in the
    known unrelated `src/code/win32/win_net.c` `WSAEVENT` /
    `ip_socket_event` errors.

No runtime launch was performed. The committed HLIL/Ghidra evidence is
sufficient for this static key-routing reconstruction.

## Parity Estimate

Strict engine `client` parity remains **100% -> 100%**. This closes another
source-only behavior difference inside the high-traffic key dispatcher.

Repo-wide retail parity remained **98% -> 98%** for this historical round. A
later input parity pass closed the key-number enum boundary described above.
