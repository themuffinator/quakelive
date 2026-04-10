# Renderer Host Text Import Switchover And Debug Atlas Closure

This note records the writable-source closure for the second half of renderer
gap `RG-G08`: native host-text import switchover plus the retained
`r_debugFontAtlas` draw path.

## Retail-Backed Behaviors Closed Here

Observed from the committed retail corpus and mirrored in writable source:

- native `ui` import `94` and native `cgame` import `0x1EC` both route through
  the same shared host `DrawScaledText` owner
- native `ui` import `95` and native `cgame` import `0x1F0` both route through
  the same shared host `MeasureText` owner
- the retained `*fontstash` atlas now has an in-source draw path behind
  `r_debugFontAtlas`

## Source Closure

- `src/code/renderer/tr_font.c` now owns shared `RE_DrawScaledText`,
  `RE_MeasureScaledText`, and `R_GetFontStashDebugInfo` helpers so native host
  text no longer depends on duplicated client-side glyph loops
- `src/code/client/cl_ui.c` and `src/code/client/cl_cgame.c` now route native
  `DrawScaledText` / `MeasureText` through the shared renderer host-text
  helpers instead of resolving `fontInfo_t` locally
- `src/code/renderer/tr_backend.c` now draws the retained atlas when
  `r_debugFontAtlas` is enabled

## Remaining Tail

RG-P9 is now considered complete.

- The remaining renderer text debt is `RG-G09`: reproducible in-tree `ft2`
  source, stricter text-specific validation, and final runtime evidence.
