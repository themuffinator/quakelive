# Quake Live Steam Mapping Round 559: Awesomium Input Injection and Comm Notice Flow

Date: 2026-06-11

## Scope

This round rechecked the retail Awesomium/WebUI input-injection corridor in
`quakelive_steam.exe`, covering mouse movement, mouse button remapping, mouse
wheel delivery, keyboard event injection, focus-activation injection, and the
communication-notice JavaScript callback path.

No live WebUI or Steam behavior was enabled and no runtime source behavior was
changed. The current source keeps live Awesomium input delivery behind
`QL_BUILD_ONLINE_SERVICES`, with inert stubs for default builds.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_cgame.c`, `src/code/client/cl_input.c`,
  `src/code/client/cl_keys.c`, `src/code/client/cl_main.c`, and
  `src/code/client/cl_awesomium_win32.cpp`

## Observed Facts

| Retail address | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `0x004f2750` | `QLWebView_InjectMouseMove` | Scales native coordinates from `vidWidth`/`vidHeight` into browser content dimensions, caches cursor position, and calls WebView slot `+0xd0` when the browser owns input. | Source-backed by `QLWebView_InjectMouseMove` and `QLWebView_InjectMappedMouseMove`. |
| `0x004f27c0` | `QLWebView_InjectMouseDown` | Remaps retail mouse key IDs from the `K_MOUSE1..3` band into Awesomium button IDs, refreshes the cached cursor position, and calls WebView slot `+0xd4`. | Source-backed by `CL_WebHost_MapMouseButton` and the live `CL_Awesomium_InjectMouseDown` adapter. |
| `0x004f2820` | `QLWebView_InjectMouseUp` | Uses the same mouse-button remap and calls WebView slot `+0xd8`. | Source-backed by `QLWebView_InjectMouseUp` and the live adapter. |
| `0x004f2870` | `QLWebView_InjectMouseWheel` | Calls WebView slot `+0xdc` with `direction * 0x1e` and zero horizontal delta. | Source-backed by `CL_Awesomium_InjectMouseWheel`, which multiplies the direction by `30`. |
| `0x004f28a0` | `QLWebView_InjectKeyboardEvent` | Constructs an Awesomium `WebKeyboardEvent` and injects it through WebView slot `+0xe0` while the browser keycatcher is active and the console bit is clear. | Partially source-backed: source captures browser key routing and key-capture publication, while full normal-key live field synthesis remains an open follow-up. |
| `0x004f2900` | `QLWebView_InjectActivationKeyboardEvent` | Constructs a synthetic `WebKeyboardEvent(0, 0x11, 0x1d0001)` and injects it through slot `+0xe0` when the native window regains focus. | Source-backed by `QLWebView_InjectActivationKeyboardEvent` and `QLWebView_InjectKeyboardEventFields`. |
| `0x004f2950` | `QLWebView_InvokeCommNotice` | Builds a JavaScript argument array and invokes `OnCommNotice` asynchronously on the cached window object. | Source-backed by `CL_WebView_InvokeCommNotice` routing retained payloads through the browser event lane. |

## Mapping Work

Added
`tests/test_awesomium_browser_parity.py::test_awesomium_input_injection_retail_hlil_flow_is_pinned`
to pin:

- Ghidra row names and sizes for the seven input/comm-notice owners;
- alias ledger spellings for `FUN_*`, upper-case Binary Ninja `sub_*`, and
  lower-case `sub_*` forms;
- HLIL anchors for coordinate scaling, cached cursor storage, WebView slot
  offsets `+0xd0`, `+0xd4`, `+0xd8`, `+0xdc`, and `+0xe0`, activation-key
  constants, and `OnCommNotice` invocation;
- source mouse-button remapping for `K_MOUSE1`, `K_MOUSE2`, and `K_MOUSE3`;
- browser keycatcher routing from `CL_MouseEvent` and
  `CL_DispatchBrowserKeyEvent`; and
- live Awesomium adapter calls for mouse movement, button, wheel, and
  constructed keyboard-event delivery.

## Source Reconstruction Decision

No source patch was made in this round. The existing source already reconstructs
the mouse and activation-key lanes with enough evidence:

- browser-owned mouse motion is routed from `CL_MouseEvent` to
  `CL_WebView_OnMouseMove`;
- browser-owned mouse buttons and wheel keys are routed through
  `CL_DispatchBrowserKeyEvent`;
- `K_MOUSE1`, `K_MOUSE2`, and `K_MOUSE3` map to the retail Awesomium button
  IDs `0`, `2`, and `1`;
- live builds forward movement, button, and wheel events through the Awesomium
  C-export adapter; and
- activation focus injects the retail `(0, 0x11, 0x1d0001)` keyboard event.

The normal-key live `WebKeyboardEvent` lane is deliberately left as an open
source-reconstruction question. Retail clearly forwards constructed key events
through slot `+0xe0`, but the committed source currently receives normalized
Quake key/down events at `CL_WebView_OnKeyEvent`. Reconstructing exact
Awesomium `eventType`, `virtualKeyCode`, and native scancode fields for normal
keys needs a tighter Win32-key evidence pass instead of a guessed translation.

## Confidence

- High for mouse move/button/wheel ownership and slot offsets: Ghidra rows,
  aliases, HLIL calls, and source adapter mappings agree.
- High for focus-activation injection: retail constants match the source
  activation event fields exactly.
- Medium for normal keyboard event parity: retail slot ownership is pinned, but
  full source-side normal-key event-field synthesis remains unimplemented.
- Medium-high for comm-notice ownership: retail invokes `OnCommNotice`
  directly, while the source routes the same retained payload through the
  browser event publication lane.

## Inference Boundary

Observed facts:

1. Retail browser mouse movement uses scaled content coordinates and stores
   both cursor components before calling WebView slot `+0xd0`.
2. Retail maps mouse buttons by subtracting `0xb2`, then swapping the middle and
   right button IDs before calling down/up slots.
3. Retail mouse wheel sends vertical delta `direction * 0x1e`.
4. Retail activation focus injects `WebKeyboardEvent(0, 0x11, 0x1d0001)`.
5. Retail communication notices call `OnCommNotice` asynchronously on the
   cached window object.

Inferences:

1. The source mouse-button map is equivalent to the retail subtract-and-swap
   sequence for the `K_MOUSE1..3` band.
2. Routing comm notices through `CL_WebView_PublishEvent` is source-equivalent
   for default builds because the live window-object dispatch remains behind
   the browser event lane.

Open questions:

1. Normal-key live Awesomium injection should receive a dedicated Win32-key
   mapping pass before source code synthesizes the full `WebKeyboardEvent`
   fields for arbitrary keys.
2. If a later UI bug requires byte-level callback parity, the source
   `web.commNotice` bridge may need a direct `OnCommNotice` invocation path for
   live builds.

## Validation

- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_input_injection_retail_hlil_flow_is_pinned -q --tb=short`
- `python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short`

## Parity Estimate

- Focused input-injection and comm-notice HLIL-flow confidence:
  **before 70% -> after 96%**.
- Focused Awesomium/WebUI launch/runtime integration mapping confidence:
  **before 98.5% -> after 98.7%**.
- Full normal-key live `WebKeyboardEvent` source parity remains open until the
  dedicated key-field reconstruction pass is complete.
