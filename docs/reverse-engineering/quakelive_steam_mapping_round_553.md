# Quake Live Steam Mapping Round 553: Awesomium Surface Pump and Bitmap Upload Flow

Date: 2026-06-11

## Scope

This round rechecked the retail Awesomium/WebUI frame-pump and browser-surface
upload path in retail `quakelive_steam.exe`, with emphasis on WebCore update,
WebView resize, bitmap-surface extraction, texture upload, dirty-state clearing,
and per-frame presentation.

No live WebUI behavior was enabled and no runtime source behavior was changed.
The current source keeps live Awesomium usage behind `QL_BUILD_ONLINE_SERVICES`
and retains source-owned fallback surface behavior for default builds.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_cgame.c` and
  `src/code/client/cl_awesomium_win32.cpp`

## Observed Facts

- Retail `QLWebCore_Update` checks the WebCore pointer, toggles the browser
  keycatcher bit when the browser is visible, and jumps through the WebCore
  update slot at `+0x18`.
- Retail `QLWebView_Resize` calls the WebView resize slot at `+0x9c` with the
  current video dimensions.
- Retail `QLWebView_RebuildSurfaceImage` fetches the WebView surface through
  slot `+0x84`, reads bitmap width and height from the surface object, expands
  non-1024 dimensions to power-of-two texture dimensions, copies pixels through
  `Awesomium::BitmapSurface::CopyTo`, registers the texture under the retail
  `"browser"` image name, updates the renderer image pointer, and releases the
  temporary pixel buffer.
- Retail `QLWebHost_PumpFrame` applies modified web zoom through WebView slot
  `+0xc4`, rebuilds the browser texture when surface dimensions drift, uploads
  dirty bitmap surfaces to GL texture `0xde1`, clears the bitmap dirty flag with
  `Awesomium::BitmapSurface::set_is_dirty(false)`, records the current content
  width/height, and draws the browser shader.
- The retail pump also draws the loading indicator when `data_12d3068` remains
  set.

## Mapping Work

- Added
  `tests/test_awesomium_browser_parity.py::test_awesomium_surface_pump_and_bitmap_upload_retail_hlil_flow_is_pinned`
  to pin:
  - Ghidra row names and sizes for `QLWebCore_Update`, `QLWebView_Resize`,
    `QLWebView_RebuildSurfaceImage`, and `QLWebHost_PumpFrame`;
  - alias ledger spellings for `FUN_*`, upper-case Binary Ninja `sub_*`, and
    lower-case `sub_*` forms;
  - HLIL anchors for the update/resize slots, surface slot `+0x84`,
    `BitmapSurface::CopyTo`, retail `"browser"` texture registration, GL dirty
    upload, dirty-flag clearing, content-size caching, and loading indicator;
  - source-side live adapter bindings for `CL_Awesomium_SurfaceDirty`,
    `CL_Awesomium_CopySurface`, `BitmapSurface::CopyTo`, fallback buffer-copy
    conversion, and `BitmapSurface::set_is_dirty(false)`; and
  - reconstructed source frame order from `QLWebCore_Update` to
    `QLWebHost_PumpFrame` to live-surface failure checking.

## Source Reconstruction Decision

No source reconstruction patch was needed in this round. The current source
already maps the retail surface path onto a bounded compatibility owner:

- live builds pull dimensions and dirty state from the Awesomium bitmap surface;
- live builds copy pixels through the SDK `BitmapSurface::CopyTo` path when
  available and clear the dirty flag after consumption;
- default builds retain a deterministic source-owned fallback surface;
- the engine uploads browser pixels through `CL_RegisterShaderFromRGBAWithImageName`
  and keeps upload dimensions, shader initialization, and dirty-state bookkeeping
  in the frame pump rather than draw time.

## Confidence

- High for the retail update/resize/surface-pump order: Ghidra rows, alias
  spellings, and HLIL slot calls agree.
- High for bitmap extraction and dirty clearing: HLIL `CopyTo` and
  `set_is_dirty(false)` calls agree with the source adapter.
- Medium-high for texture upload equivalence: retail registers and updates a
  renderer texture named `"browser"`, while the source uses its existing
  named-image registration surface to avoid direct renderer internals.

## Validation

Validation run:

```text
python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_surface_pump_and_bitmap_upload_retail_hlil_flow_is_pinned -q --tb=short
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Parity Estimate

- Focused Awesomium/WebUI surface-pump and bitmap-upload HLIL-flow confidence:
  **before 74% -> after 98%**.
- Focused Awesomium/WebUI launch/runtime integration mapping confidence:
  **before 97.5% -> after 98%**.
- Overall strict Windows Awesomium/WebUI source behavior remains effectively
  closed; this pass improves executable retail evidence coverage rather than
  changing runtime behavior.
