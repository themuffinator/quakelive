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

Observed facts from the writable source tree:

- The classic renderer FreeType path still lives in `src/code/renderer/tr_font.c`.
- The renderer no longer depends on a missing in-tree `src/code/ft2/` vendor
  drop. The build now uses an explicit external FreeType SDK replacement lane
  on Windows and `pkg-config freetype2` on Unix when `BUILD_FREETYPE` is
  enabled.
- `src/code/renderer/tr_font.c` now contains a renderer-owned retained host text
  core that creates `*fontstash`, installs `R_fonsErrorCallback`, and retains
  the five recovered host-text faces plus the preferred sans/fallback face
  slots.
- native `DrawScaledText` / `MeasureText` now route through the shared
  renderer host-text helpers instead of through duplicated client-side glyph
  loops.
- `r_debugFontAtlas` now has an in-source draw path in `tr_backend.c`.

## Source alignment landed in this pass

- `src/code/renderer/tr_font.c` now recognizes the retail Quake Live font
  aliases, builds face-specific cache and page names, and can read absolute
  Windows font paths when the caller resolves a host fallback face.
- `src/code/renderer/tr_font.c` now also owns the renderer-side retained host
  text core: a renderer-owned retained host text core that keeps the
  `*fontstash` atlas alive, installs the retail expansion or flush callback,
  and retains `normal`, `sans`, `mono`, `sans-fallback`, and
  `sans-windows-fallback` in one face table.
- `src/code/renderer/tr_font.c` now also owns the shared host draw/measure
  helpers used by the native `ui` and `cgame` import wrappers.
- `src/code/client/cl_ui.c` and `src/code/client/cl_cgame.c` now route native
  `DrawScaledText` / `MeasureText` through the shared renderer host-text
  helpers instead of resolving `fontInfo_t` locally.
- `src/code/renderer/tr_backend.c` now exposes the retained atlas through the
  debug draw path guarded by `r_debugFontAtlas`.

Inference:

- The source tree now matches the retail face selection and per-face cache
  behavior much more closely for the retained host-text lane itself.
- The renderer font stack now has a coherent source, build, and runtime parity
  story instead of a missing-vendor plus warning-only tail.

## Closure status

- `RG-P10` is now complete:
  - the renderer build metadata no longer points at `..\ft2\*`
  - `BUILD_FREETYPE` is now tied to an explicit external FreeType SDK lane,
    with the local Windows build script able to forward explicit include/lib
    overrides or auto-discover `vcpkg`'s `x86-windows` FreeType install
- `RG-P11` is now complete:
  - the tracked runtime artifact is
    `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260410.json`
  - that artifact now proves a windowed UI-bootstrap pass, retained-atlas
    debug rendering, and live `bloodrun` runtime with distinct engine/window
    capture hashes, while rejecting `RE_RegisterFont` fallback-lane logs
- No confirmed renderer font-stack gap remains after `RG-P11`.

## Verification

Run:

```powershell
pwsh tools\ci\audit-retail-font-stack.ps1
```

Use `-Strict` to turn any reopened font-stack or runtime-evidence regression
into a hard failure.
