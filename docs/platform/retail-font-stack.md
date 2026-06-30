# Retail Font Stack Audit

This note records what the committed retail Quake Live evidence shows about the
Windows font stack and how that stack is now reconstructed and validated in the
current writable source tree.

## Evidence summary

Observed facts from the committed retail launcher HLIL:

- `quakelive_steam.exe` contains a second text system beyond the classic
  renderer `RE_RegisterFont` path.
- That host text system creates a texture named `*fontstash`, installs the
  error callback string `R_fonsErrorCallback: error %d val %d\n`, and exposes a
  debug atlas path guarded by `r_debugFontAtlas`.
- The host initializes five named faces in a contiguous handle table:
  - `normal` -> `fonts/handelgothic.ttf`
  - `sans` -> `fonts/notosans-regular.ttf`
  - `mono` -> `fonts/droidsansmono.ttf`
  - `sans-fallback` -> `fonts/droidsansfallbackfull.ttf`
  - `sans-windows-fallback` -> `%WINDIR%\fonts\ARIALUNI.TTF`,
    `%WINDIR%\fonts\segoeui.ttf`, or `%WINDIR%\fonts\l_10646.ttf`
- Retail host `DrawScaledText` / `MeasureText` wrappers index that handle table
  directly, instead of collapsing every call to a single baked `fontInfo_t`.
- Retail host `DrawScaledText` / `MeasureText` consume UTF-8 text through the
  retained host lane instead of indexing raw bytes. HLIL `0x00443BE0` and
  `0x00444360` walk the same DFA-style decode tables before probing glyphs.
- Retail glyph lookup caches entries by decoded codepoint plus the rounded
  tenths-sized request and probes the requested face before the retained
  fallback-face slots. HLIL `0x00443720` shows the current face search, the
  three retained fallback slots, and the size-tenths key in the same helper.
- Retail `R_InitFontStash` creates the retained `512 x 512` atlas, installs the
  callback, loads the face table, and leaves glyph population lazy; no
  initialization-time loop prebuilds every byte glyph for every face.
- Retail atlas expansion preserves the existing alpha atlas contents while
  growing the retained image, and it only clears cached glyph state on the
  maximum-size flush path.
- Retail `*fontstash` texture refreshes rebind the renderer image as
  `GL_ALPHA` storage and upload the retained one-byte alpha buffer directly.
- Retail host draw only treats `^0` through `^7` as color escapes. Other caret
  pairs stay visible in the glyph stream, while `forceColor` still consumes the
  recognized color escapes without recoloring.
- UI HLIL `sub_10003d90` / `sub_10003ec0` computes host text scale as
  `(vidHeight / 768) * 96`. Against the source UI/cgame `yscale =
  vidHeight / 480`, that matches a `QL_FONT_HOST_POINT_SIZE` baseline of
  `60.0f`.

Observed facts from the writable source tree:

- The classic renderer FreeType path still lives in `src/code/renderer/tr_font.c`.
- The renderer no longer depends on a missing in-tree `src/code/ft2/` vendor
  drop. The build now uses a repo-managed FreeType replacement lane on Windows
  and `pkg-config freetype2` on Unix when `BUILD_FREETYPE` is enabled. The
  Win32 build now defaults that lane on, bootstraps FreeType into
  `src/libs/freetype` from an official upstream cache when needed, and no
  longer silently compiles the tiny bitmap fallback path on clean checkouts.
- `src/code/renderer/tr_font.c` now contains a renderer-owned retained host text
  core that creates `*fontstash`, installs `R_fonsErrorCallback`, and retains
  the five recovered host-text faces plus the preferred sans/fallback face
  slots.
- `src/code/renderer/tr_font.c` now also decodes UTF-8 host text into
  codepoints, caches retained glyphs by codepoint plus rounded size tenths, and
  probes the recovered retained fallback-face chain before dropping to the
  classic baked-font compatibility lane.
- `src/code/renderer/tr_font.c` now leaves retained host glyphs lazy: glyphs
  are cached lazily as text is measured or drawn, matching the retail
  `R_InitFontStash` ownership path and avoiding startup atlas saturation.
- `src/code/renderer/tr_font.c` now also preserves the previous atlas pixels
  and cached glyph coordinates when `R_fonsErrorCallback` expands the retained
  atlas, keeping cache invalidation reserved for the retail max-size flush.
- `src/code/renderer/tr_font.c` now flushes queued renderer text quads before
  a retained atlas resize or max-size reset, matching the retail FontStash
  draw-queue boundary so loading-screen text cannot sample a newer atlas
  generation than the one used for its UVs.
- `src/code/renderer/tr_font.c` now refreshes the retained `*fontstash`
  texture as a `GL_ALPHA` atlas instead of expanding the alpha buffer into
  RGBA on every upload.
- native `DrawScaledText` / `MeasureText` now route through the shared
  renderer host-text helpers instead of through duplicated client-side glyph
  loops.
- `r_debugFontAtlas` now has an in-source draw path in `tr_backend.c`.
- The retail `GetRefAPI` table still carries a legacy font slot after
  `ModelBounds`, but the current source keeps that slot as a no-op and routes
  native UI/cgame font registration through the client compatibility wrappers
  that call the classic `RE_RegisterFont` lane directly.

## Source alignment landed in this pass

- `src/code/renderer/tr_font.c` now recognizes the retail Quake Live font
  aliases, builds face-specific cache and page names, and can read absolute
  Windows font paths when the caller resolves a host fallback face.
- `src/code/renderer/tr_font.c` now also owns the renderer-side retained host
  text core: a renderer-owned retained host text core that keeps the
  `*fontstash` atlas alive, installs the retail expansion or flush callback,
  and retains `normal`, `sans`, `mono`, `sans-fallback`, and
  `sans-windows-fallback` in one face table.
- The retained host text core now drains pending renderer commands before the
  expansion/reset callback mutates `*fontstash`, preserving already-queued UI
  and loading-screen text against the old atlas contents.
- `src/code/renderer/tr_font.c` now also owns the shared host draw/measure
  helpers used by the native `ui` and `cgame` import wrappers.
- Those shared helpers now resolve glyphs from the retained `*fontstash` face
  table first and only fall back to the classic `RE_RegisterFont` cache lane
  when the retained atlas path is unavailable for the requested face.
- Those same helpers now consume UTF-8 codepoints, treat only `^0`..`^7` as
  host color escapes, and keep the retail `forceColor` behavior where valid
  color escapes are consumed but do not recolor the active draw state.
- The renderer host helpers are now gate-checked for their core draw/measure
  contract: face handles fall back through the retained normal/sans faces,
  requested sizes are rounded and clamped to tenths, the integer draw/measure
  slot is treated as the retail visible-character limit, pointer-based max-X
  clipping happens before drawing the overflowing glyph, and measurement
  preserves the retail bounds packet while still reporting the retained font
  ascent for height.
- `src/code/client/cl_ui.c` and `src/code/client/cl_cgame.c` now route native
  `DrawScaledText` / `MeasureText` through the shared renderer host-text
  helpers instead of resolving `fontInfo_t` locally.
- The native UI/cgame font import slots are now parity-gated as a trio:
  `RegisterFont` remains on the compatibility registration lane, while
  `DrawScaledText` and `MeasureText` fail closed through the recovered host
  text import wrappers.
- The native draw wrappers also preserve the module current-color sidecar and
  normalize `forceColor` before entering `RE_DrawScaledText`; the measure
  wrappers populate the retail five-float bounds packet (`left`, `top`,
  `right`, `bottom`, `ascent`) while also returning packed width/height floats
  for source-side callers.
- UI and cgame clipped text helpers now have explicit max-X projection gates:
  `Text_Paint_Limit` and `CG_Text_Paint_Limit` project both draw coordinates
  and clip bounds into screen space, draw through host text, then convert the
  returned `outMaxX` back into 640-space coordinates.
- UI and cgame host text metrics/span helpers are gated as retained-text
  consumers too: measurement uses `trap_QL_MeasureText` at
  `scale * QL_FONT_HOST_POINT_SIZE`, span drawing uses
  `trap_QL_DrawScaledText`, and UI cursor painting measures the prefix through
  the same host lane before drawing the cursor glyph.
- `src/code/client/cl_console.c` now keeps the console prompt, chat prompt,
  scrollback, and editable field cursor on the retained mono host-text lane.
  The strict audit checks the UTF-8 cursor windowing, host metrics lookup, and
  packed console color-cell conversion into host text color escapes.
- `src/code/client/cl_scrn.c` now routes client screen-overlay helpers such as
  `SCR_DrawStringExt`, `SCR_DrawBigString`, `SCR_DrawBigStringColor`, and the
  demo-recording overlay through the same retained mono host-text lane used by
  retail, instead of the legacy charset glyph loop.
- `src/code/renderer/tr_backend.c` now exposes the retained atlas through the
  debug draw path guarded by `r_debugFontAtlas`.
- Renderer advertisement debug labels in `src/code/renderer/tr_world.c` also
  draw through retained host text at the recovered `16 / 48` debug scale.

## Interface font helpers and registered sizes

Observed facts from the committed retail UI and cgame references:

- UI `AssetCache` is an art-only cache; the committed retail reconstruction for
  `uix86.dll` registers gradient, FX, scrollbar, slider, and crosshair art
  there, but not fonts.
- UI `MenuParse_font` normalizes legacy tokens onto the Quake Live baked font
  buckets, stores the resolved token on the menu, and seeds the shared display
  context fonts on first use.
- cgame `CG_AssetCache` is described in the committed symbol map as the shared
  HUD art cache, while `CG_RegisterHudFonts` remains the explicit HUD font
  bootstrap helper.

Observed facts from the writable source tree:

- The shared baked font buckets are now defined as:
  - `fonts/font` at `24`
  - `fonts/smallfont` at `16`
  - `fonts/bigfont` at `48`
  - `fonts/monofont` at `16`
- UI menu asset globals use two retail size tiers:
  - gameplay and HUD menus such as `src/ui/hud.menu` register
    `24 / 16 / 48`
  - `src/ui/main.menu` registers `16 / 12 / 20`
- UI font registration now stays in `Asset_Parse` and `MenuParse_font`, while
  `AssetCache` remains art-only.
- UI `Asset_Parse` now normalizes the global `font`, `smallFont`, and
  `bigFont` declarations before registering the retained text, small, and big
  buckets, while `MenuParse_font` bootstraps that trio once from the resolved
  menu token.
- UI item-level `font` stays a retail integer bucket: `ItemParse_font` writes
  `item->fontIndex`, and the shared item width, height, paint, and cursor
  wrappers forward that bucket into the extended host-text callbacks.
- cgame HUD font registration stays in `CG_RegisterHudFonts`, while
  `CG_AssetCache` remains art-only.
- cgame `CG_Asset_Parse` is now parity-gated for the retail token spelling:
  `font`, `smallFont`, and lowercase `bigfont` route through
  `cgDC.registerFont`, while the one-time HUD bootstrap keeps the default
  text/small/big trio available when scripts omit a bucket.
- cgame browser/HUD menu parsing is now gated through the shared menu parser:
  `CG_SetupBrowserMenuKeywordHash` rebuilds the keyword hash containing
  `font -> MenuParse_font`, `CG_ParseBrowserMenu` enters `Menu_Parse`, and both
  `CG_Init` and `loadhud` rebuild that parser state before HUD menu font
  declarations are replayed.

Inference:

- The source tree now matches the retail face selection and per-face cache
  behavior much more closely for the retained host-text lane itself.
- The hidden exactness tail inside that retained lane is now also closed:
  host text is no longer byte-oriented, and Unicode fallback probing no longer
  depends on the caller choosing the fallback face manually.
- The UI and cgame font helpers now also match the retail ownership split more
  closely: asset caches own shaders, while dedicated font parse/bootstrap
  helpers own the registered Quake Live font buckets and their point sizes.
- The renderer font stack now has a coherent source, build, and runtime parity
  story instead of a missing-vendor plus warning-only tail.

## Closure status

- `RG-P10` is now complete:
  - the renderer build metadata no longer points at `..\ft2\*`
  - `BUILD_FREETYPE` is now tied to a repo-managed FreeType lane, while the
    non-retail codec stack is bootstrapped from repo-managed sources instead of
    from system SDK or Vcpkg discovery
- `RG-P11` is now complete:
  - the tracked runtime artifact is
    `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json`
  - the stable alias was refreshed on 2026-04-21 from the clean
    `renderer_runtime_evidence_20260421.json` bundle
  - that artifact now proves a windowed UI-bootstrap pass, retained-atlas
    debug rendering, and live `bloodrun` runtime with distinct engine/window
    capture hashes, while rejecting `RE_RegisterFont` fallback-lane logs
- The 2026-04-17 full font audit reopened one hidden renderer-host gap
  inside the earlier `RG-P8` closure:
  - raw-byte host glyph lookup instead of UTF-8 decode
  - point-size-only retained glyph caching instead of codepoint-plus-size cache
  - retained fallback faces that were stored but not automatically probed
  - over-permissive caret color parsing in the host draw helper
- That reopened gap is now reclosed in source, tests, and the strict audit
  script.
- No confirmed renderer or client screen-overlay font-stack gap remains after
  `RG-P11`, the 2026-04-17 audit refresh, and the retained mono overlay wiring
  follow-up.
- The strict audit also now covers the native UI/cgame font import slot values,
  import-table assignments, fail-closed trap wrappers, the VM-side
  `RegisterFont` compatibility wrappers, cgame `Q3_VM` host-text stubs, cgame
  snapshot/FPS upper-right host text, module current-color/packed-measure bridge semantics,
  renderer face/scale/color/max-X/out-left core semantics, UI/cgame metrics,
  cursor, span, and clipped max-X text, renderer advertisement debug labels,
  console/chat host-text consumers, UI asset/menu parser bootstrap ownership,
  UI item integer font buckets, UI legacy font alias normalization, cgame
  lowercase-`bigfont` HUD asset parsing, and cgame browser-menu font parser
  routing plus HUD reload ordering.

## Verification

Run:

```powershell
pwsh tools\ci\audit-retail-font-stack.ps1
```

Use `-Strict` to turn any reopened font-stack or runtime-evidence regression
into a hard failure.
