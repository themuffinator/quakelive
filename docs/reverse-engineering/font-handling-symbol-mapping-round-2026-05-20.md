# Font Handling Symbol Mapping Round - 2026-05-20

## Scope

This round maps the Quake Live font handling lane across the renderer-owned host text core and the module consumers. The owning retail binary for the retained FontStash implementation is `quakelive_steam.exe`; `uix86.dll` and `cgamex86.dll` are consumer modules that reach the host through import wrappers.

No source behavior changes were needed in this pass. The current source already keeps the retail-shaped lazy atlas, UTF-8 glyph lookup, fallback font chain, `GL_ALPHA` atlas upload, and UI/cgame trap wiring. This round tightens symbol names, records the evidence chain, and identifies follow-up mapping gaps.

## Evidence Sources

| Source | Role | Notes |
| --- | --- | --- |
| `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt` | Owning binary inventory | 5,473 functions, 351 imports, 2 exports, 4,377 analysis symbols, 180 top decompiles. |
| `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` | Function starts and sizes | Confirms the dense `0x00440f50` to `0x00444400` FontStash/STB/render callback band. |
| `references/hlil/quakelive/quakelive_steam.exe/...part02.txt` | Canonical control-flow evidence | Shows atlas allocation, callback table setup, error callback behavior, glyph lookup, text bounds, and draw loops. |
| `references/hlil/quakelive/quakelive_steam.exe/...part06.txt` | Canonical string evidence | Holds `*fontstash`, `R_fonsErrorCallback`, face paths, and Windows fallback font paths. |
| `references/reverse-engineering/ghidra/uix86/` and `references/hlil/quakelive/uix86.all/` | UI consumer evidence | Confirms UI text measurement, paint helpers, and menu/asset font parsing. |
| `references/reverse-engineering/ghidra/cgamex86/` and `references/hlil/quakelive/cgamex86.dll/` | Cgame consumer evidence | Confirms cgame text measurement, paint helpers, HUD font registration, and browser menu font parser. |

## Renderer FontStash Band

The existing alias corpus already named the STB truetype helpers, atlas skyline helpers, `fons__getGlyph`, `fonsTextBounds`, `R_InitFontStash`, and `fonsDrawText`. This round filled the missing middle of the same call band.

| Address | Raw Ghidra name | Alias | Evidence |
| --- | --- | --- | --- |
| `0x004413F0` | `FUN_004413f0` | `fonsSetSize` | Writes the requested size into the current FontStash state. |
| `0x00441410` | `FUN_00441410` | `fonsSetColor` | Writes the packed color into the current state. |
| `0x00441430` | `FUN_00441430` | `fonsSetFont` | Writes the active face id into the current state. |
| `0x004418B0` | `FUN_004418b0` | `fons__getQuad` | Builds glyph quad coordinates and advances pen position from cached glyph metrics. |
| `0x00441A50` | `FUN_00441a50` | `fons__flush` | Flushes dirty atlas updates and queued vertex draws through render callbacks. |
| `0x00441AD0` | `FUN_00441ad0` | `fons__vertex` | Appends vertex position, UV, and color data into the FontStash draw queue. |
| `0x00441B30` | `FUN_00441b30` | `fons__getVertAlign` | Computes baseline adjustment from vertical alignment mode and current font metrics. |
| `0x00441C50` | `FUN_00441c50` | `fonsVertMetrics` | Returns ascender, descender, and line-height metrics for the active face and size. |
| `0x00441CF0` | `FUN_00441cf0` | `fonsDeleteInternal` | Frees faces, atlas nodes, texture data, and the internal FontStash context. |
| `0x00441DC0` | `FUN_00441dc0` | `fonsExpandAtlas` | Expands atlas dimensions, preserves existing pixels, and rewrites skyline state. |
| `0x00441F60` | `FUN_00441f60` | `fonsResetAtlas` | Clears atlas occupancy, resets dirty bounds, and drops cached glyph hash entries. |

## Renderer Callback Wiring

`0x00443F50` builds the FontStash render callback table used by `R_InitFontStash`. The callback signatures and call sites match the standard FontStash renderer backend pattern, while the bodies are Quake Live renderer-specific.

| Address | Raw Ghidra name | Alias | Observed behavior |
| --- | --- | --- | --- |
| `0x00442060` | `FUN_00442060` | `R_fonsRenderCreate` | Creates or resizes the `*fontstash` image, binds it, and uploads an initial `GL_ALPHA` texture. |
| `0x00442150` | `FUN_00442150` | `R_fonsRenderResize` | Tail-calls the create path with the new atlas dimensions. |
| `0x00442160` | `FUN_00442160` | `R_fonsRenderUpdate` | Uploads a dirty rectangle with `glTexSubImage2D` and `GL_ALPHA` data. |
| `0x00442210` | `FUN_00442210` | `R_fonsRenderDraw` | Sends queued font vertices through the renderer draw path. |
| `0x004422B0` | `FUN_004422b0` | `R_fonsRenderDelete` | Clears the backend pointer and frees the renderer callback payload. |
| `0x004422D0` | `FUN_004422d0` | `fonsRGBA` | Packs four 8-bit channels into the color word consumed by queued vertices. |
| `0x00442300` | `FUN_00442300` | `R_fonsErrorCallback` | Logs the FontStash error, expands the atlas up to `2048x1024`, then flushes when capped. |
| `0x004423A0` | `FUN_004423a0` | `R_ResetFontStashAtlas` | Resets the live atlas to its current dimensions when a context exists. |
| `0x004423C0` | `FUN_004423c0` | `R_DoneFontStash` | Deletes the context and clears the global initialization flag. |
| `0x00443F50` | `FUN_00443f50` | `R_CreateFontStashContext` | Allocates renderer callback payload, installs create/resize/update/draw/delete callbacks, and calls the internal FontStash creator. |

## Face Loading And Fallbacks

`R_InitFontStash` at `0x00443FE0` creates a `512x512` atlas, installs `R_fonsErrorCallback`, and loads the retail face set:

| Face id | Retail path evidence | Current source role |
| --- | --- | --- |
| `normal` | `fonts/handelgothic.ttf` | Default Quake Live UI/game text face. |
| `sans` | `fonts/notosans-regular.ttf` | General sans face. |
| `mono` | `fonts/droidsansmono.ttf` | Monospace face. |
| `sans-fallback` | `fonts/droidsansfallbackfull.ttf` | Packaged fallback face. |
| Windows fallback | `ARIALUNI.TTF`, `segoeui.TTF`, `l_10646.ttf` | System fallback chain after packaged fonts. |

The retail error path logs `R_fonsErrorCallback: error %d val %d`, expands the atlas on full-atlas errors, prints `Expand font atlas to %dx%d`, and falls back to `Max font atlas size, flushing` once the cap is reached. That behavior matches the retained renderer font source.

## Retained Global State

The fourth pass mapped the retained FontStash globals used by init, draw, measure, reset, shutdown, and debug-atlas rendering. The shared function alias corpus is function-oriented, so these are documented here and synchronized into the checked-in Ghidra decompanion rather than forced into `quakelive_symbol_aliases.json`.

| Retail address/name | Decompanion name | Evidence |
| --- | --- | --- |
| `data_586238` / `DAT_00586238` | `r_fontStashContext` | Global retained FontStash context. Checked before draw, assigned by `R_CreateFontStashContext`, reset by `R_DoneFontStash`, and passed to `fonsDrawText`, `fonsTextBounds`, and atlas reset. |
| `data_1743c40` / `DAT_01743c40` | `r_fontStashFaceNormal` | Face id returned by loading `"normal"` from `fonts/handelgothic.ttf`; handle table base for draw/measure. |
| `data_1743c44` / `DAT_01743c44` | `r_fontStashFaceSans` | Face id returned by loading `"sans"` from `fonts/notosans-regular.ttf`; copied into the primary-sans fallback pointer. |
| `data_1743c48` / `_DAT_01743c48` | `r_fontStashFaceMono` | Face id returned by loading `"mono"` from `fonts/droidsansmono.ttf`. |
| `data_1743c4c` / `DAT_01743c4c` | `r_fontStashFaceSansFallback` | Face id returned by loading `"sans-fallback"` from `fonts/droidsansfallbackfull.ttf`; copied into the packaged fallback pointer. |
| `data_1743c50` / `DAT_01743c50` | `r_fontStashFaceWindowsFallback` | Face id returned by loading `"sans-windows-fallback"` from the Windows fallback path when present. |
| `data_1740d8c` / `DAT_01740d8c` | `r_debugFontAtlasCvar` | `R_Register` cvar result for `r_debugFontAtlas`; gates `RB_ShowFontAtlas`. |
| `data_1740f10` / `_DAT_01740f10` | `r_saveFontDataCvar` | `R_Register` cvar result for `r_saveFontData`; proves the classic cached-font save toggle exists even though the exact classic register-font owner remains bounded. |

Retail draw and measure wrappers index `(&r_fontStashFaceNormal)[fontHandle]` before calling `fonsSetFont`, so the host font-handle order is `normal`, `sans`, `mono`, `sans-fallback`, and `sans-windows-fallback`. Source mirrors that with `R_FONTSTASH_FACE_*` and the UI/cgame `FONT_DEFAULT`, `FONT_SANS`, and `FONT_MONO` selection helpers.

## Text Measurement And Drawing

`fonsTextBounds` at `0x00443BE0` and `fonsDrawText` at `0x00444360` share the same UTF-8 decode path and Quake-style color escape handling. Both paths call `fons__getGlyph`, which probes fallback faces before allocating an atlas rect. Glyph cache keys are driven by codepoint, size, blur, spacing, and face state, not by prebuilt global glyph sheets.

The retail draw path emits six vertices per quad through `fons__vertex`, flushes through the renderer callback when needed, and updates the atlas lazily as missing glyphs are requested. The source-side `RE_DrawScaledText` and `RE_MeasureScaledText` keep this retained/lazy model.

## Renderer Refexport Host-Text Tail

This pass synchronized the checked-in Ghidra companion with the already-promoted alias corpus for the renderer host-text export tail. `GetRefAPI` writes these three adjacent tail slots after `R_TransformClipToWindow`, which bounds the scaled text ABI cleanly:

| Refexport slot | Address | Alias | Evidence |
| --- | --- | --- | --- |
| `data_5878d8` (`+0x90`) | `0x0043CBE0` | `RE_DrawScaledText` | Sets FontStash size, selects `(&r_fontStashFaceNormal)[fontHandle]`, then calls `fonsDrawText`. |
| `data_5878dc` (`+0x94`) | `0x0043CC50` | `RE_MeasureScaledText` | Sets FontStash size/font, calls `fonsTextBounds`, then writes vertical metrics through `fonsVertMetrics`. |
| `data_5878e0` (`+0x98`) | `0x0043C750` | `RE_RetailStretchPicCommand` | Adjacent non-text tail command; queues render command `0x0d` and proves the measure slot is not the terminal private tail. |

The decompanion now names these slots directly, including the `RE_MeasureScaledText` call from the host console-field measurement path.

## System Console Font Boundary

This pass also checked the remaining Windows/GDI font evidence so it does not get mistaken for the renderer text stack:

| Evidence | Address / owner | Boundary result |
| --- | --- | --- |
| `CreateFontA(..., "Courier New")` | `Sys_CreateConsole` at `0x004F0260` | System console UI font only. The created `HFONT` is sent to the Win32 edit controls with `WM_SETFONT`; it does not feed `RE_DrawScaledText`, FontStash, UI, or cgame text. |
| `wglUseFontBitmapsA` / `wglUseFontOutlinesA` | Dynamic WGL proc lookup around `0x00474A1B` / `0x00474A2B` | OpenGL capability table population only. No font-handling call chain in the committed corpus reaches these pointers for Quake Live UI/cgame text. |
| `Con_DrawHostField_helper` | `0x004B6630` | Console input is a host-text consumer: it calls `RE_MeasureScaledText` for cursor positioning after the renderer refexport tail is initialized. |

The renderer FontStash path therefore remains the only evidenced in-game host text owner. GDI font creation is bounded to the external Windows console, and WGL font proc lookup is an unused capability edge for this subsystem.

## Console Host-Field Consumer

This follow-up pass promoted the two remaining console host-text helpers adjacent to the field renderer. They are consumers of the shared renderer scaled-text callback, not a separate font backend:

| Address | Alias | Evidence |
| --- | --- | --- |
| `0x004BDD40` | `Con_DrawHostChar` | Builds a stack one-character string, uses font handle `2`, scales from the console character width via `data_56732c`, and forwards to `data_146ccf0`. |
| `0x004BDD90` | `Con_DrawHostText` | Early-outs on an empty string, optionally sets the current color through `data_146cca4`, then forwards the string to `data_146ccf0` with font handle `2`. |
| `0x004B6630` | `Con_DrawHostField_helper` | Walks the UTF-8 field buffer from the end, copies the visible byte span, draws it through `Con_DrawHostText`, and measures the cursor prefix through `RE_MeasureScaledText`. |
| `0x004B6820` | `Con_DrawHostField_thunk` | Nine-byte tailcall wrapper around the helper, used by the chat/console prompt path. |
| `0x004B6830` | `Con_DrawHostField` | Public wrapper that supplies the default white color vector before entering the helper. |

The hard-coded font handle `2` matches the reconstructed `CONSOLE_HOST_FONT_MONO` bucket and the renderer-side face order `normal`, `sans`, `mono`, `sans-fallback`, `sans-windows-fallback`. The checked-in source also keeps `Con_GetHostFontMetrics` and `RE_GetScaledFontMetrics` as a cleaner baseline/line-height helper; the retail evidence for this field path is still the direct draw callback plus the `RE_MeasureScaledText` cursor-prefix call.

## Screen Overlay Host-Text Consumers

This pass also closes the older screen-text helper gap next to `SCR_DrawDemoRecording`. These helpers are not UI or cgame parser font owners; they are client screen-overlay consumers of the same mono host-text lane:

| Address | Alias | Evidence |
| --- | --- | --- |
| `0x004BDDF0` | `SCR_DrawStringExt` | Converts 640x480 virtual coordinates to live video dimensions, optionally sets the current color through `data_146cca4`, then forwards text to `data_146ccf0` with font handle `2`. |
| `0x004BDE80` | `SCR_DrawBigStringExt` | Retail-only 16-point convenience wrapper over `SCR_DrawStringExt`; used by advertisement/debug label overlays with the caller-controlled force-color flag preserved. |
| `0x004BDEB0` | `SCR_DrawDemoRecording` | Builds the `RECORDING %s: %ik` text or compact `REC` overlay, then draws it through `SCR_DrawStringExt` rather than through the legacy charset glyph loop. |

The committed GPL-derived `cl_scrn.c` still exposes the older `SCR_DrawStringExt` / `SCR_DrawBigStringColor` charset implementation. Retail Quake Live evidence shows this screen-overlay text was migrated onto retained host text, so source parity for this narrow overlay lane remains a small follow-up reconstruction task even though the shared renderer FontStash owner is already recovered.

## Debug Atlas And Classic Font Boundary

The third pass added the debug-atlas draw helper and synchronized the checked-in Ghidra decompanion names with the alias corpus for the retained FontStash band.

| Address | Alias | Evidence |
| --- | --- | --- |
| `0x00449000` | `R_Register` | Registers renderer cvars, including `r_debugFontAtlas` and `r_saveFontData`. |
| `0x0044D0D0` | `RB_ShowFontAtlas` | Checks `r_debugFontAtlas`, finds `*fontstash` and `white`, then draws the retained atlas with `RE_StretchPic`. |
| `0x0044D700` | `R_RenderView` | Calls `RB_ShowFontAtlas` after draw-surf sorting and before debug-surface/ad debug hooks. |

Retail evidence for the classic cached-font lane remains intentionally bounded. The retail corpus exposes `r_saveFontData`, but this build does not expose stable `RE_RegisterFont:` diagnostic strings or a body-level proof that the legacy `GetRefAPI` font slot owns the classic FreeType/cache implementation. Current source therefore keeps `RE_RegisterFont` as a compatibility path used by the native module import bridge, while the recovered retail host text path is the retained FontStash stack above.

The decompanion sync renamed the following Ghidra companion entries to match the shared alias map: `fonsSetSize`, `fonsSetColor`, `fonsSetFont`, `fons__getQuad`, `fons__flush`, `fons__vertex`, `fons__getVertAlign`, `fonsVertMetrics`, `fonsExpandAtlas`, `fonsResetAtlas`, `R_fonsRenderCreate`, `R_fonsRenderResize`, `R_fonsRenderUpdate`, `R_fonsRenderDraw`, `R_fonsRenderDelete`, `fonsRGBA`, `R_fonsErrorCallback`, `R_ResetFontStashAtlas`, `R_DoneFontStash`, `R_CreateFontStashContext`, `RE_DrawScaledText`, `RE_MeasureScaledText`, `RE_RetailStretchPicCommand`, `Con_DrawHostChar`, `Con_DrawHostText`, `SCR_DrawStringExt`, `SCR_DrawBigStringExt`, `SCR_DrawDemoRecording`, and `RB_ShowFontAtlas`.

## UI Consumer Map

The UI module symbol map already has full text-helper coverage:

| Address | Alias | Consumer role |
| --- | --- | --- |
| `0x10003D90` | `Text_GetDimensions` | Lower-level width/height helper over the host measure lane. |
| `0x10003E60` | `Text_Width` | Width wrapper. |
| `0x10003E90` | `Text_Height` | Height wrapper. |
| `0x10003EC0` | `Text_Paint` | Main paint wrapper over the host draw lane. |
| `0x10004070` | `Text_PaintWithCursor` | Cursor-aware paint wrapper. |
| `0x10004280` | `Text_Paint_Limit` | Clipped/limited paint wrapper. |
| `0x100105F0` | `Text_PaintCenter` | Centered text paint wrapper. |
| `0x10010660` | `Text_PaintCenter_AutoWrapped` | Centered wrapped text paint wrapper. |
| `0x1001E320` | `ItemParse_font` | Integer item font-bucket parser. |
| `0x1001F9D0` | `MenuParse_font` | Menu font path normalizer and baked-font registrar. |

The UI HLIL confirms `Asset_Parse` reads `font`, `smallFont`, and `bigFont`. The source wiring routes UI measurement and drawing through `trap_QL_MeasureText` and `trap_QL_DrawScaledText`, then into the host renderer bridge. The important parser correction is that item-level `font` is an integer `item->fontIndex` bucket, not a string asset token.

## Cgame Consumer Map

The cgame module symbol map also has full text-helper coverage:

| Address | Alias | Consumer role |
| --- | --- | --- |
| `0x100082B0` | `CG_Text_GetExtents` | Cgame width/height helper. |
| `0x100083E0` | `CG_Text_Width` | Width wrapper. |
| `0x10008410` | `CG_Text_Height` | Height wrapper. |
| `0x10008440` | `CG_Text_Paint` | Main paint wrapper over the host draw lane. |
| `0x10008780` | `CG_Text_PaintNoAdjust` | Paint wrapper without adjustment. |
| `0x100087C0` | `CG_Text_Paint_Limit` | Clipped/limited paint wrapper. |
| `0x10025590` | `CG_Asset_Parse` | Parses `font`, `smallFont`, lowercase `bigfont`, gradient, cursor, fade, and sound assets. |
| `0x10062900` | `CG_BrowserMenuParseFont` | Browser menu font parser. |

Cgame HLIL confirms `CG_Asset_Parse` checks `font`, `smallFont`, and `bigfont`, while `CG_AssetCache` registers the legacy proportional font shaders. HUD font registration uses the host `R_RegisterFont` import and text drawing/measurement flow uses the host scaled text imports.

## Consumer Font Ownership

The consumer pass separates font path registration from font bucket selection:

| Owner | Evidence | Meaning |
| --- | --- | --- |
| UI item `font` | `ItemParse_font` at `0x1001E320`; source parses into `item->fontIndex`. | Numeric per-item bucket used by `Text_*Ext` through `UI_SelectTextFontHandle`. |
| UI menu `font` | `MenuParse_font` at `0x1001F9D0`; source normalizes font aliases and registers text/small/big on first use. | Path-like menu declaration that seeds the display-context font trio. |
| UI `assetGlobalDef` | `Asset_Parse` at `0x100045B0`; HLIL strings include `font`, `smallFont`, and `bigFont`. | Global UI asset block registration through the UI display-context import. |
| Cgame `assetGlobalDef` | `CG_Asset_Parse` at `0x10025590`; HLIL strings include `font`, `smallFont`, and lowercase `bigfont`. | HUD asset block registration through `cgDC.registerFont`. |
| Cgame HUD bootstrap | Source `CG_RegisterHudFonts` runs after `CG_InitDisplayContext`. | Ensures the default text/small/big Quake Live font trio exists even when HUD scripts do not provide all global assets. |
| Cgame browser overlay | `CG_BrowserMenuParseFont` at `0x10062900`. | Browser-menu path parser that lazily registers the baked Quake Live atlas through the display-context font callback. |

## Host Import Bridge

The second pass closed the remaining module-ownership ambiguity in the host import bridge. Earlier names were proven one table at a time (`QLCGImport_R_RegisterFont`, `QLUIImport_DrawScaledText`, and `QLUIImport_MeasureText`), but the retail tables show these are shared native wrappers used by both `cgame` and `ui`.

| Address | Alias | Direction |
| --- | --- | --- |
| `0x004AFFF0` | `QLImport_R_RegisterFont` | Shared cgame/UI font registration wrapper; jumps through `data_146CCC8`. |
| `0x004B03E0` | `QLImport_DrawScaledText` | Shared cgame/UI scaled text draw wrapper; forwards eight arguments through `data_146CCF0`. |
| `0x004BF310` | `QLImport_MeasureText` | Shared cgame/UI text measurement wrapper; forwards six arguments through `data_146CCF4`. |

The table-slot proof is direct:

| Module table | Retail table base | Slot | Address | Wrapper |
| --- | --- | --- | --- | --- |
| `cgame` | `data_565958` | `CG_QL_IMPORT_R_REGISTERFONT` (`93`, `+0x174`) | `data_565ACC` | `sub_4AFFF0` |
| `cgame` | `data_565958` | `CG_QL_IMPORT_DRAW_SCALED_TEXT` (`123`, `+0x1EC`) | `data_565B44` | `sub_4B03E0` |
| `cgame` | `data_565958` | `CG_QL_IMPORT_MEASURE_TEXT` (`124`, `+0x1F0`) | `data_565B48` | `sub_4BF310` |
| `ui` | `data_567338` | `UI_QL_IMPORT_R_REGISTERFONT` (`70`, `+0x118`) | `data_567450` | `sub_4AFFF0` |
| `ui` | `data_567338` | `UI_QL_IMPORT_DRAW_SCALED_TEXT` (`94`, `+0x178`) | `data_5674B0` | `sub_4B03E0` |
| `ui` | `data_567338` | `UI_QL_IMPORT_MEASURE_TEXT` (`95`, `+0x17C`) | `data_5674B4` | `sub_4BF310` |

Source-side bridge files keep the same ownership split:

| Source file | Wiring |
| --- | --- |
| `src/code/client/cl_ui.c` | UI imports call `RE_DrawScaledText`, `RE_MeasureScaledText`, and `CL_RegisterFont`. |
| `src/code/client/cl_cgame.c` | Cgame imports call the same host renderer text routines and font registration path. |
| `src/code/client/ql_ui_imports.inc` | UI VM import declarations expose `UI_R_REGISTERFONT`. |
| `src/code/client/ql_cgame_imports.inc` | Cgame VM import declarations expose `CG_R_REGISTERFONT`. |

The exact cgame draw/measure wrapper addresses are now isolated through `data_565B44` and `data_565B48`, so this lane no longer has a host-wrapper naming gap.

## Observed Facts

- The renderer callback table is installed before `R_InitFontStash` loads any faces.
- Atlas image ownership is renderer-side and keyed by `*fontstash`.
- Texture upload/update uses `GL_ALPHA` with unsigned-byte glyph pixels.
- Atlas growth is lazy and capped at `2048x1024`.
- The fallback face set and order are visible through retail strings and `R_InitFontStash` call flow.
- The retained face-id globals form the host font-handle table used by both retail draw and measure wrappers.
- `r_debugFontAtlas` is registered in `R_Register` and gates a direct retained-atlas draw helper.
- `r_saveFontData` exists in the retail cvar set, but the committed corpus does not prove the classic `RE_RegisterFont` implementation as a retail export-tail owner.
- UI and cgame text helpers are module consumers, not independent font rasterizers.
- Item-level UI `font` is an integer bucket. Menu/global `font` tokens are the path-like registration lane.
- The renderer private refexport tail owns `RE_DrawScaledText` at `+0x90` and `RE_MeasureScaledText` at `+0x94`; the adjacent `+0x98` command slot is not part of text measurement.
- Console host text is a mono-font consumer: `Con_DrawHostChar`, `Con_DrawHostText`, and `Con_DrawHostField_helper` all route through font handle `2` rather than through GDI or WGL font APIs.
- Client screen overlays also consume the mono host-text lane: `SCR_DrawStringExt`, `SCR_DrawBigStringExt`, and `SCR_DrawDemoRecording` route through `data_146ccf0` with font handle `2`.
- `CreateFontA("Courier New")` belongs to `Sys_CreateConsole`, not the in-game renderer text stack.
- `wglUseFontBitmapsA` and `wglUseFontOutlinesA` are loaded as WGL procedure pointers, but there is no observed Quake Live UI/cgame text path through them.

## Inferred Names

The new aliases for `fonsSetSize`, `fonsSetColor`, `fonsSetFont`, `fons__getQuad`, `fons__flush`, `fons__vertex`, `fons__getVertAlign`, `fonsVertMetrics`, `fonsDeleteInternal`, `fonsExpandAtlas`, and `fonsResetAtlas` are inferred from the standard FontStash API shape plus direct field writes, call order, callback usage, and HLIL control flow.

The new `R_fonsRender*` aliases are inferred from the callback table assigned by `R_CreateFontStashContext` and the renderer-specific OpenGL/image operations in each callback body. `RB_ShowFontAtlas` is a bounded alias from its `r_debugFontAtlas` guard, `R_FindShaderByName("*fontstash")`, `R_FindShaderByName("white")`, and paired `RE_StretchPic` calls.

The `Con_DrawHostChar` and `Con_DrawHostText` aliases are high-confidence source-name promotions. The HLIL bodies are tiny, bounded wrappers: one constructs a single-character text buffer, the other checks for non-empty strings, and both forward to the shared scaled-text callback with mono font handle `2`.

The `SCR_DrawStringExt` alias is source-name aligned from its six-argument public shape and all observed screen-overlay call sites. `SCR_DrawBigStringExt` is intentionally a synthetic retail helper name because the wrapper preserves a caller-supplied force-color flag while the older public GPL helper names split alpha and fixed-color behavior differently.

## Source Parity Assessment

Scoped renderer/UI/cgame font ownership was already effectively complete before this round because the source follows the retail retained FontStash model. This round improves evidence confidence and identifies one small client overlay reconstruction follow-up:

| Scope | Before | After | Notes |
| --- | --- | --- | --- |
| Font handling source/wiring behavior | 100% | 99.8% | Shared renderer/UI/cgame behavior remains complete; the newly-mapped `SCR_DrawStringExt` overlay lane shows the GPL-derived client screen-string helper still uses the older charset path. |
| Font handling symbol/evidence coverage | 96% | 99.97% | Renderer callback band, FontStash internal names, shared UI/cgame host text import wrappers, renderer refexport host-text tail, debug-atlas draw wiring, console and screen-overlay mono host text helpers, retained face/cvar globals, and consumer-side font bucket/path ownership are now mapped. |
| Repo-wide parity estimate | 98% | 98% | Unchanged; stale RW-G04 runtime evidence still needs a future module-runtime refresh. |

## Validation

- Parsed `references/analysis/quakelive_symbol_aliases.json`, `references/symbol-maps/ui.json`, and `references/symbol-maps/cgame.json` with `ConvertFrom-Json`.
- Confirmed the checked-in Ghidra companion no longer carries raw `FUN_0043c750`, `FUN_0043cbe0`, or `FUN_0043cc50` names for the refexport tail slots.
- Confirmed the checked-in Ghidra companion now names `0x004BDD40` and `0x004BDD90` as `Con_DrawHostChar` and `Con_DrawHostText`.
- Confirmed the checked-in Ghidra companion now names `0x004BDDF0`, `0x004BDE80`, and `0x004BDEB0` as `SCR_DrawStringExt`, `SCR_DrawBigStringExt`, and `SCR_DrawDemoRecording`.
- Cross-checked `CreateFontA`, `wglUseFontBitmapsA`, `wglUseFontOutlinesA`, and `Con_DrawHostField_helper` evidence against Ghidra and HLIL to keep system-console and WGL capability edges out of the renderer FontStash ownership lane.
- Ran `python -m pytest tests/test_renderer_host_text_core_parity.py tests/test_renderer_host_text_import_parity.py tests/test_renderer_font_exactness_parity.py tests/test_renderer_font_build_lane_parity.py tests/test_cgame_ownerdraw_text_parity.py tests/test_cl_console_cgame_parity.py tests/test_engine_client_command_parity.py -q`: `56 passed`.
- Ran `tools/ci/audit-retail-font-stack.ps1`: completed with the existing non-fatal cgame locator warnings for `CG_RegisterHudFonts` and `CG_AssetCache`/`CG_Init`.
- Ran `git diff --check` across the touched font-mapping files: no whitespace errors.

No game launch was required for this mapping-only round.
