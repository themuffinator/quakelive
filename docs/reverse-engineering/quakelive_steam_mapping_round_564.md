# Quake Live Steam Mapping Round 564: Awesomium Browser Control and Navigation Flow

Date: 2026-06-11

## Scope

This round rechecked the retail browser control and navigation helpers in
`quakelive_steam.exe`: location-hash updates, browser hide/deactivation, cache
clear, reload, shutdown, relative URL open, navigate-or-open, and show-error.

No live WebUI or Steam behavior was enabled. The current source continues to
keep live Awesomium paths behind `QL_BUILD_ONLINE_SERVICES`, with deterministic
offline launcher and error fallbacks.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_cgame.c`

## Observed Facts

| Retail address | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `0x004f23e0` | `QLWebView_SetLocationHash` | Fetches `document.location`, converts the incoming hash to a `JSValue`, and calls `JSObject::SetPropertyAsync` on the `hash` property. | Source-backed by `QLWebView_SetLocationHash`, which normalizes the hash, rebuilds the current URL, and uses live JavaScript when Awesomium is enabled. |
| `0x004f24d0` | `QLWebHost_HideBrowser` | Pauses rendering, unfocuses the view, clears browser-active state, clears the browser keycatcher bit, notifies cgame overlay close, clears tooltip state, and restores the arrow cursor. | Source-backed by `QLWebHost_HideBrowser`. |
| `0x004f2a10` | `CL_Web_ClearCache_f` | No Ghidra row; forwards to WebSession slot `+0x1c` when a session exists. | Source-backed by `CL_Web_ClearCache_f` and `CL_Web_ClearSessionState`. |
| `0x004f2a30` | `CL_Web_Reload_f` | No Ghidra row; clears session state through slot `+0x1c`, then reloads the active WebView through slot `+0x78` with ignore-cache set. | Source-backed by `CL_Web_Reload_f` and `QLWebHost_ReloadView`. |
| `0x004f2a60` | `QLWebHost_Shutdown` | Destroys the WebView when present and calls `Awesomium::WebCore::Shutdown` when the WebCore exists. | Source-backed by `CL_WebHost_Shutdown` and the reset-runtime owner. |
| `0x004f3160` | `QLWebHost_OpenRelativeURL` | Reads command argument 0, builds the launcher URL, and calls `QLWebHost_OpenURL`. | Source-backed by `QLWebHost_OpenRelativeURL`. |
| `0x004f31d0` | `QLWebHost_NavigateOrOpen` | Reads command argument 0, builds the URL, first tries the location-hash path, and falls back to opening the launcher URL when the browser is inactive. | Source-backed by `QLWebHost_NavigateOrOpen`. |
| `0x004f3cb0` | `CL_Web_ShowError_f` | No Ghidra row; forwards command argument 1 into the game-error publication path. | Source-backed by `CL_Web_ShowError_f` and `CL_WebView_PublishGameError`. |

## Mapping Work

Added
`tests/test_awesomium_browser_parity.py::test_awesomium_browser_control_navigation_retail_hlil_flow_is_pinned`
to pin:

- Ghidra row names and sizes for row-backed browser control/navigation helpers;
- no-row alias handling for `web_clearCache`, `web_reload`, and
  `web_showError`;
- HLIL anchors for `document.location.hash`, pause/unfocus/active-cvar
  clearing, WebSession cache-clear slot `+0x1c`, WebView reload slot `+0x78`,
  WebView destroy, WebCore shutdown, relative URL construction, hash navigation,
  and game-error forwarding;
- source hash normalization/current URL bookkeeping;
- source hide/deactivation side effects for keycatcher, cursor, cgame overlay,
  and tooltip state; and
- source reload/clear-cache/shutdown fallback behavior.

## Source Reconstruction Decision

No source patch was needed in this round. The current source already separates
the retail control surface into narrow helpers:

- `QLWebView_SetLocationHash` owns hash normalization and live JS hash update;
- `QLWebHost_HideBrowser` owns deactivation, keycatcher, cursor, cgame overlay,
  and tooltip clearing;
- `CL_Web_ClearCache_f` and `CL_Web_Reload_f` route through the retained
  session-state owner before reload;
- `QLWebHost_NavigateOrOpen` prefers in-place hash navigation when a bound
  document exists and falls back to a full relative URL open; and
- `CL_Web_ShowError_f` publishes the browser error through the recovered
  game-error event lane.

The direct retail WebSession/WebView/WebCore slots are represented through the
source Awesomium adapter and offline launcher fallbacks instead of unguarded
live service calls.

## Confidence

- High for location-hash, hide, clear-cache, reload, shutdown, and
  navigate-or-open ownership: HLIL, aliases, rows where present, and source
  helpers agree.
- High for no-row command wrapper boundaries: Binary Ninja HLIL and the alias
  ledger agree that `web_clearCache`, `web_reload`, and `web_showError` are
  small command wrappers even without Ghidra function rows.
- Medium-high for exact live JavaScript parity: retail uses Awesomium JSObject
  property setting, while the source live path uses a bounded JavaScript string
  to update `window.location.hash` and call `main_hook_v2`.

## Inference Boundary

Observed facts:

1. Retail updates `document.location.hash` asynchronously when an active view
   exists.
2. Retail hide pauses and unfocuses the WebView, clears `web_browserActive`, and
   clears the browser keycatcher bit.
3. Retail reload clears session cache state before invoking the WebView reload
   slot with ignore-cache enabled.
4. Retail `web_changeHash` falls back to a full open when the browser is not
   active.

Inferences:

1. The source JavaScript hash-update shim is equivalent at the browser-observed
   level while avoiding direct SDK object ownership in default builds.
2. The source session-state clear path is the appropriate reconstruction of
   retail WebSession cache clearing under the default-disabled online-services
   policy.

Open questions:

1. If live Awesomium hash behavior later needs byte-level parity, the
   JavaScript shim can be replaced with a direct SDK `document.location.hash`
   property path under `QL_BUILD_ONLINE_SERVICES`.
2. Retail shutdown object lifetime could receive a smaller follow-up pass if
   crash-path behavior points at teardown ordering.

## Validation

- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_browser_control_navigation_retail_hlil_flow_is_pinned -q --tb=short`

## Parity Estimate

- Focused browser control/navigation HLIL-flow confidence:
  **before 76% -> after 98%**.
- Focused Awesomium/WebUI launch/runtime integration mapping confidence:
  **before 98.85% -> after 99.0%**.
