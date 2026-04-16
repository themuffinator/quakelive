# Renderer FreeType Build-Lane Recovery

Last updated: 2026-04-10

Scope: `RG-P10`

## Retail-backed problem statement

Observed facts before this closure pass:

- `src/code/renderer/renderer.vcxproj`
- `src/code/renderer/renderer.vcxproj.filters`
- `src/code/renderer/renderer.vcproj`
- `src/code/unix/Makefile`

all still described a historic in-tree `ft2` vendor lane even though
`src/code/ft2/` was absent from committed source.

Inference:

- The renderer text stack itself was largely reconstructed, but the committed
  build story was still inaccurate because the source tree advertised missing
  FreeType ownership.

## Source changes landed

1. `src/code/renderer/tr_font.c` now uses the repo-managed FreeType header lane
   (`ft2build.h` plus the `FT_*_H` include macros) instead of relative
   `../ft2/*` includes.
2. `src/code/renderer/renderer.vcxproj` now exposes an explicit
   `QLEnableFreeType` repo-managed build toggle, validates headers and import
   libraries, and defines `BUILD_FREETYPE` only when that lane is enabled.
3. `src/code/quakelive_steam.vcxproj` now carries the matching link-time
   FreeType validation and dependency wiring so the real game build can satisfy
   renderer FreeType symbols.
4. `.vscode/build.ps1` now stays on repo-managed dependency roots only, and
   the Windows build path now bootstraps `libogg`, `libvorbis`, `zlib`, and
   `libpng` from `src/libs/_deps` instead of probing external SDK or Vcpkg
   installs.
5. `src/code/unix/Makefile` no longer carries the dead in-tree `ft2` object
   list. It now uses an explicit external `freetype2` `pkg-config` lane and
   defines `BUILD_FREETYPE` only when `QL_ENABLE_FREETYPE=1`.
6. The stale `..\ft2\*` entries were removed from the legacy renderer project
   descriptions (`renderer.vcxproj`, `renderer.vcxproj.filters`, and
   `renderer.vcproj`).

## Closure result

Observed facts after the change:

- No renderer build file under `src/code/renderer/` still points at
  `..\ft2\*`.
- The renderer now has one explicit, reviewable repo-managed FreeType
  replacement path instead of a dead vendor-tree assumption.
- The remaining renderer work is no longer build-lane ownership.

RG-P10 is now considered complete.
