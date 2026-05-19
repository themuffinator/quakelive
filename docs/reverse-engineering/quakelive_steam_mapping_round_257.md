# Quake Live Steam Host Mapping Round 257

## Scope

This round isolates the engine-client mouse event dispatcher recovered at
`sub_4B54E0` and compares it against the retained `CL_MouseEvent` wiring in
`src/code/client/cl_input.c`.

The goal was to decide whether the source-side absolute cursor accumulator and
CPI-scaled UI/cgame dispatch were retail behavior or a previous compatibility
inference.

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/quakelive_steam_mapping_round_29.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_256.md`

## `sub_4B54E0`: `CL_MouseEvent`

Observed corpus facts:

1. The Ghidra function table exposes the dispatcher row as
   `FUN_004b54e0,004b54e0,141,0,unknown`.
2. The HLIL body starts with `sub_4F22E0()`, already promoted in round 29 as
   `AdvertisementBridge_IsDelayElapsed`. The current source still does not have
   the advertisement-delay state modeled in the input dispatcher, so this gate
   remains documented rather than guessed.
3. The dispatcher then checks the engine-registered `cg_ignoreMouseInput` cvar
   pointer at `data_1627c54 + 0x30` and exits when it is non-zero.
4. The `CL_Init` cvar table registers `cg_ignoreMouseInput` with default `0`
   and flag `0x40` (`CVAR_ROM` in the retained source flag table).
5. The keycatcher checks are ordered:
   - `0x20` -> `sub_4F2750(arg1, arg2)`
   - `KEYCATCH_UI` (`0x2`) -> UI VM mouse event with the same two arguments
   - `KEYCATCH_CGAME` (`0x8`) -> cgame VM mouse event with the same two
     arguments
   - no catcher except `0x10` -> accumulate the same arguments into the gameplay
     mouse movement totals
6. `sub_4F2750` is already promoted as `QLWebView_InjectMouseMove`; its HLIL
   maps the incoming coordinates through the browser view/surface dimensions and
   avoids injection while the console catcher is active.
7. The adjacent browser host helpers wire the same bit: `QLWebHost_HideBrowser`
   clears `data_1528ba4 & 0x20`, while `QLWebCore_Update` sets `0x20` when the
   browser-active flag is live.
8. No HLIL branch in `sub_4B54E0` performs the retained source's previous
   `m_cpi` translation or absolute cursor accumulation before UI/cgame dispatch.

The dispatcher is now promoted in
`references/analysis/quakelive_symbol_aliases.json` as:

| Raw symbol | Alias | Confidence | Basis |
| --- | --- | --- | --- |
| `sub_4B54E0` (`0x004B54E0`) | `CL_MouseEvent` | High | Event-loop mouse payload owner with exact UI/cgame/browser/gameplay routing shape. |

## Source Reconstruction

Implemented source changes:

1. `src/code/client/cl_main.c` now registers
   `Cvar_Get( "cg_ignoreMouseInput", "0", CVAR_ROM );` beside the other
   engine-visible client state cvars.
2. `src/code/client/client.h` now defines the recovered local keycatcher bits:
   - `KEYCATCH_RETAIL_MOUSEPASS` = `0x0010`
   - `KEYCATCH_BROWSER` = `0x0020`
3. `src/code/client/cl_cgame.c` now mirrors the browser catcher producer side:
   `QLWebCore_Update` arms `KEYCATCH_BROWSER` while the retained browser host is
   active, while `QLWebHost_HideBrowser` and `CL_WebHost_ResetRuntime` clear it.
4. `CL_MouseEvent` now follows the observed retail routing order:
   - ignore events while `cg_ignoreMouseInput` is set
   - forward raw event payloads to `CL_WebView_OnMouseMove` when browser capture
     is active
   - forward raw event payloads to UI and cgame VM mouse handlers
   - accumulate raw payloads into gameplay mouse totals only when the catcher
     mask is clear except for `0x10`
5. The previous retained absolute cursor helper pair,
   `CL_ResetMouseCursorPosition` / `CL_UpdateMouseCursorPosition`, was removed
   from this dispatcher path because no matching branch exists in the recovered
   retail control flow.
6. The standalone input-translation harness remains in place for keyboard
   translation and CPI helper samples, but `CL_MouseEvent` no longer uses that
   helper as a UI/cgame dispatch step.

## Open Questions

1. `sub_4F22E0` is still only represented in the source through the existing
   advertisement bridge compatibility surface. The input dispatcher does not yet
   model that delay gate directly because the writable source does not expose
   the same deadline global.
2. `sub_4EAB80` is a one-return helper over `data_12cfc70` in the full HLIL
   corpus. Its surrounding ownership remains unclear, so this round did not add
   a speculative local gate.
3. The `0x10` keycatcher bit is preserved only as
   `KEYCATCH_RETAIL_MOUSEPASS`. The behavior is observed, but the public retail
   name is not present in the committed corpus.

## Validation

Commands run:

- `python -m pytest tests/test_input_translation.py tests/test_awesomium_browser_parity.py tests/test_engine_cvar_retail_parity.py tests/test_engine_client_command_parity.py -q --tb=short`
  - Result: `74 passed in 0.79s`
- `python -m pytest tests/test_platform_services.py -q --tb=short`
  - Result: `76 passed in 7.69s`
- `python -m pytest tests/test_client_full_parity_gate.py tests/test_client_config_parity.py tests/test_engine_netcode_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `88 passed, 1 skipped in 7.86s`
- `git diff --check`
  - Result: no whitespace errors; existing LF-to-CRLF normalization warnings
    were reported for dirty text files.
- `python -m json.tool references/analysis/quakelive_symbol_aliases.json > $null`
  - Result: alias JSON parsed successfully.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
  - Result: touched client files, including `client\cl_cgame.c`,
    `client\cl_input.c`, and `client\cl_main.c`, compiled; the project still
    stops in the pre-existing
    `src/code/win32/win_net.c` `WSAEVENT` / `ip_socket_event` errors.

No runtime launch was performed. Static HLIL/Ghidra evidence and automated
tests were sufficient for this dispatcher reconstruction.

## Parity Estimate

Strict engine `client` parity remains **100% -> 100%**. This round does not
raise the already closed client score, but it removes one compatibility
inference from a high-traffic input path and replaces it with direct
HLIL-backed behavior.

Repo-wide retail parity remains **98% -> 98%** because the remaining gaps are
outside this focused engine-client dispatcher lane.
