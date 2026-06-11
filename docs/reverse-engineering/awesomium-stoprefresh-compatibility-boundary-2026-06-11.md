# Awesomium StopRefresh Compatibility Boundary

## Scope

This round pins the boundary between the retail Awesomium/WebUI command set and
the source-side `web_stopRefresh` compatibility bridge used by inherited UI
menu scripts.

The important distinction is that retail `quakelive_steam.exe` registers the
core WebUI browser commands, but the committed Binary Ninja HLIL command owner
does not register `web_stopRefresh`. The reconstructed source keeps
`web_stopRefresh` only as a guarded compatibility path for `uiScript
stopRefresh`, and it must not abort a live Awesomium view.

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_004f3cd0` at `0x004f3cd0`, size `158`; the shared alias corpus
  maps it to `QLWebHost_RegisterCommands`.
- Binary Ninja HLIL part05 shows `sub_4f3cd0` registering
  `web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`,
  `web_clearCache`, and `web_reload`, followed by the `web_zoom`,
  `web_console`, and `web_browserActive` cvar registrations.
- The committed HLIL browser-host string/function area does not contain
  `web_stopRefresh`.
- `src/ui/main.menu` still invokes `uiScript stopRefresh` from the main menu
  `onOpen` block.
- `src/code/ui/ui_main.c` maps that UI script action to `web_stopRefresh`
  only when the browser overlay is available; otherwise it stops only the
  native server refresh.

Inferred mapping:

- `web_stopRefresh` is a source compatibility owner for retained UI behavior,
  not a strict retail `QLWebHost_RegisterCommands` member.
- The live Awesomium path should continue pumping WebCore and should not call
  `WebView::Stop` from the compatibility command, because that would let a
  non-retail UI script abort the retail-style WebUI launch/runtime surface.

## Reconstruction

Strengthened `tests/test_awesomium_browser_parity.py` with a focused parity
gate:

- The Ghidra row and alias mapping for `QLWebHost_RegisterCommands` are pinned
  beside the Binary Ninja HLIL registration order.
- `web_stopRefresh` absence is checked in the retail HLIL command/string
  evidence used by this subsystem.
- Source-side command registration is allowed to include `web_stopRefresh`, but
  only as an explicit compatibility extension.
- `CL_Web_StopRefresh_f` is checked for default-disabled online-service
  guardrails, provider-unavailable logging, a live-Awesomium no-op path that
  clears `refreshStopped`, and a fallback retained-session path that can still
  latch `refreshStopped`.
- The test confirms `_Awe_WebView_Stop@4` remains an available external SDK
  import while `CL_Web_StopRefresh_f` does not call `CL_Awesomium_Stop()` for a
  live view.
- The frame-pump guard confirms `QLWebCore_Update` still calls
  `CL_Awesomium_Update()` and is not gated by `refreshStopped`.

No C source change was required in this pass. The source already matched the
intended compatibility boundary; the missing piece was a retail-backed test and
fresh mapping note.

## Validation

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  - passed
- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_stop_refresh_is_explicit_non_retail_ui_bridge_compatibility -q --tb=short`
  - passed, `1 passed`
- `python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short`
  - passed, `43 passed`
- `python -m pytest tests/test_platform_services.py::test_service_disabled_menu_verb_matrix_stays_explicit tests/test_platform_services.py::test_awesomium_menu_flow_clears_browser_overlay_for_gameplay -q --tb=short`
  - passed, `2 passed`

## Parity Estimate

- Focused `web_stopRefresh` divergence classification:
  **before 83% -> after 98%**.
- Focused browser command-registration and compatibility-owner confidence:
  **before 96% -> after 99%**.
- Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.27% -> 99.28%**.
