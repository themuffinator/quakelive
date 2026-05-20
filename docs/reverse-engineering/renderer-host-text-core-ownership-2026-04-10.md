# Renderer Host Text Core Ownership Note

Last updated: 2026-05-20

This note records the renderer-owned host text-engine core now present in
writable source after `RG-P8`.

## Retail-Backed Host Text Core Behaviors

Observed facts now mirrored in source:

- `src/code/renderer/tr_font.c` owns a retained atlas named `*fontstash`
  through the normal renderer image or shader path.
- The retained atlas starts at `512 x 512`, uses the retail
  `R_fonsErrorCallback: error %d val %d\n` callback string, expands toward the
  retail `2048 x 1024` ceiling, and flushes once that ceiling is reached.
- The renderer now retains the five recovered host-text faces in one table:
  - `normal`
  - `sans`
  - `mono`
  - `sans-fallback`
  - `sans-windows-fallback`
- The dedicated Windows fallback face mirrors the retail host search order:
  `ARIALUNI.TTF`, `segoeui.ttf`, then `l_10646.ttf`.
- The retained core also tracks the recovered preferred face slots for the
  primary sans lane, the packaged fallback lane, and the Windows fallback lane.

Inference:

- The repo now has a direct renderer-owned lifetime for the retail host text
  core instead of only compatibility wrappers built on baked `fontInfo_t`.

## 2026-04-17 Audit Refresh

Observed facts from the committed retail host draw/measure lane:

- HLIL `0x00443BE0` and `0x00444360` walk UTF-8 DFA-style decode tables before
  probing host glyphs.
- HLIL `0x00443720` keys retained glyphs by decoded codepoint plus rounded
  size tenths.
- The same glyph helper probes the requested face first and then walks the
  three retained fallback-face slots stored on the host text context.
- Retail host color handling only consumes `^0` through `^7`, and the
  `forceColor` path still consumes those escapes without repainting the color
  state.

Observed facts now mirrored in source:

- `src/code/renderer/tr_font.c` now decodes retained host text as UTF-8
  codepoints instead of indexing raw bytes.
- Retained `*fontstash` glyphs are now cached by codepoint plus rounded size
  tenths instead of through a fixed 256-entry byte table.
- Retained glyph lookup now probes the requested face, then the recovered
  primary sans, packaged fallback, and Windows fallback slots before using the
  classic compatibility-font lane.
- Host draw/measure now consume only `^0`..`^7` color escapes and keep the
  retail `forceColor` behavior where recognized color escapes are swallowed
  without recoloring.

Inference:

- The hidden byte-oriented exactness tail inside the earlier `RG-P8` host-core
  closure is now closed. The retained renderer-owned host-text core matches the
  retail glyph-ownership split and the retail Unicode/fallback behavior much
  more closely.

## 2026-05-20 Wiring Refresh

Observed facts from the committed retail `R_InitFontStash` HLIL:

- The initialization path creates the `512 x 512` retained context, installs
  `R_fonsErrorCallback`, loads the five recovered faces, and assigns the
  preferred sans/fallback pointers.
- The initialization path does not perform a startup sweep across
  `GLYPH_START..GLYPH_END` for every retained face.
- The atlas resize and flush callbacks are reached from the retained glyph
  cache path as glyphs are requested, not from an eager all-face prebuild.
- Retail atlas expansion copies the previous alpha buffer into the larger
  atlas before rebinding the `*fontstash` image, while the max-size flush path
  clears the atlas and glyph-cache state.
- The retained texture callback uses `GL_ALPHA` storage/upload for the
  one-byte atlas after the initial renderer image handle has been created.

Observed facts now mirrored in source:

- `R_InitFontStash` now stops after image creation and face initialization.
- Retained host glyphs are cached lazily by `RE_DrawScaledText` and
  `RE_MeasureScaledText` through `R_GetFontStashGlyph`.
- The previous eager prebuild loop was removed because it could saturate and
  flush the atlas before retail modules reached live map rendering.
- `R_ResizeFontStashAtlas` now copies the old atlas rows into the expanded
  buffer and rescales cached glyph UVs to the new dimensions instead of
  throwing away the retained glyph cache during normal expansion.
- `R_UploadFontStashAtlas` now mirrors the retail texture-storage callback by
  uploading the retained buffer as `GL_ALPHA`, leaving the RGBA seed image only
  for initial renderer image creation.
- The retail `refexport_t` legacy font slot is now represented as a no-op in
  the renderer export table; native UI/cgame font registration still reaches
  the classic `RE_RegisterFont` compatibility lane through client import
  wrappers, not through that private tail slot.

Inference:

- The renderer-owned host text core is closer to the retail FontStash lifetime:
  the atlas starts empty, expands only under demand, preserves useful retained
  glyphs across growth, keeps the GL object as an alpha texture, and remains a
  runtime cache instead of a startup-baked glyph atlas.

## Downstream Closure

The `RG-P8` closure only covered the retained host-text core itself. The
downstream native-import switchover plus debug-atlas draw path were closed
separately in `RG-P9`; see
`docs/reverse-engineering/renderer-host-text-import-switchover-and-debug-atlas-2026-04-10.md`.

RG-P8 is now considered complete.
