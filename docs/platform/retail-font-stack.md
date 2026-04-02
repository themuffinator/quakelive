# Retail Font Stack Audit

This note records what the committed retail Quake Live evidence shows about the
Windows font stack, which parts of that stack are now reconstructed in writable
source, and which pieces are still missing.

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
- The project files and Unix makefile still reference an in-tree `src/code/ft2/`
  vendor drop, but that directory is currently absent from the repo.
- No committed source file currently implements the retail host `*fontstash`
  subsystem; the only remaining `r_debugFontAtlas` references are the cvar
  declaration and registration.

## Source alignment landed in this pass

- `src/code/renderer/tr_font.c` now recognizes the retail Quake Live font
  aliases, builds face-specific cache and page names, and can read absolute
  Windows font paths when the caller resolves a host fallback face.
- `src/code/client/cl_ui.c` now honors the retail native font-handle buckets
  instead of always forcing `fonts/notosans-regular.ttf`.
- `src/code/client/cl_cgame.c` now mirrors the same handle-to-face mapping and
  the same Windows fallback order.

Inference:

- The source tree now matches the retail face selection and per-face cache
  behavior much more closely for the renderer-backed compatibility path.
- The repo still does not contain a direct reconstruction of the launcher-side
  FontStash-style text engine itself.

## Remaining gaps

- `src/code/ft2/` is still missing, so the historic in-tree FreeType build used
  by the renderer project files cannot be reproduced from committed source yet.
- The retail host `*fontstash` subsystem remains unreconstructed:
  - no committed source registers a `*fontstash` texture
  - no committed source implements `R_fonsErrorCallback`
  - `r_debugFontAtlas` has no atlas-draw implementation behind its cvar wiring
- The current native `DrawScaledText` / `MeasureText` host wrappers remain a
  compatibility shim built on `fontInfo_t`; they are not yet the direct retail
  FontStash implementation recovered from the launcher HLIL.

## Verification

Run:

```powershell
pwsh tools\ci\audit-retail-font-stack.ps1
```

Use `-Strict` to fail the audit when the unresolved retail font-source gaps are
still present.
