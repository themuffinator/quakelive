# Renderer Font Cache And Atlas Ownership (2026-04-10)

This note records the `RG-P7` closure outcome for the classic renderer-backed
font lane in `src/code/renderer/tr_font.c`.

The conclusion is deliberately narrow:

- the classic baked-font path is now bounded strongly enough to close `RG-G05`
- the remaining renderer text debt is no longer in the classic cache/atlas lane
- the still-open text work is the separate host FontStash system and its build
  or validation tail (`RG-G08`, `RG-G09`)

## Evidence Anchors

Committed evidence used for this ownership pass:

- `docs/platform/retail-font-stack.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_37.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_38.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_43.md`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- current writable source in `src/code/renderer/tr_font.c`

## Retail-Backed Classic Font Behaviors

These behaviors are now treated as retail-backed within the classic
`fontInfo_t` path:

1. Font alias normalization:
   - `R_NormalizeFontSourcePath` maps the Quake Live face aliases used by the
     classic path onto concrete TTF sources:
     - `normal` / `fonts/font` / `fonts/bigfont` -> `fonts/handelgothic.ttf`
     - `sans` / `fonts/smallfont` -> `fonts/notosans-regular.ttf`
     - `mono` / `fonts/monofont` -> `fonts/droidsansmono.ttf`
     - `sans-fallback` / `sans-windows-fallback` -> `fonts/droidsansfallbackfull.ttf`
2. Face-specific cache and atlas naming:
   - `R_BuildFontCacheStem`, `R_BuildFontCacheName`, and `R_BuildFontPageName`
     now define one normalized lowercase stem shared by the `.dat` cache file
     and the generated atlas page names.
3. Cached-font reload ownership:
   - `R_FindCachedFontDataName` probes the face-specific cache first and only
     falls back to the older point-size-only cache name explicitly.
   - `R_RegisterCachedFontShaders` now rebinds cached page shaders across the
     full inclusive glyph range `GLYPH_START..GLYPH_END`.
4. Atlas page ownership:
   - `R_FlushFontAtlasPage` now owns the classic `256x256` page flush, shader
     registration, and inclusive glyph-range assignment for each emitted page.
   - The final page assignment now includes glyph `255` instead of stopping one
     entry early.
5. Classic glyph metrics contract:
   - The FreeType path still maps metrics into the legacy `glyphInfo_t` space:
     `top`, `bottom`, `height`, `pitch`, `xSkip`, image size, and the shared
     `glyphScale = 48 / pointSize` contract expected by Quake III-era UI and
     cgame draw code.

## Compatibility-Only Scaffolding That Remains Intentional

These branches are intentionally retained compatibility behavior, not claimed as
retail-owned classic renderer logic:

1. Point-size-only cache fallback:
   - `fonts/fontImage_%i.dat` is still probed as a compatibility path for older
     pre-Quake Live baked data after the face-specific cache name misses.
2. Built-in glyph fallback:
   - `RE_RegisterFontFallback` still synthesizes a fixed-cell `16x16` glyph
     grid from `gfx/2d/bigchars` and then `white` if cached or FreeType-backed
     data is unavailable.
3. Absolute host-path file reads:
   - `R_ReadAbsoluteFontFile` remains a compatibility bridge that lets the
     current host-side text wrappers feed resolved Windows font paths through
     the classic renderer lane when needed.

These compatibility branches are now explicit enough that they no longer keep
the classic font lane in an open-ended ownership bucket.

## Closure Outcome

RG-G05 is now considered closed.

`RG-G05` is now considered closed because:

1. The retail-backed cache/page/atlas path is explicitly separated from the
   compatibility-only branches in writable source.
2. Deterministic renderer tests can now pin:
   - normalized cache stems
   - face-specific cache/page names
   - inclusive cached-font shader rebinding
   - inclusive final-page atlas assignment
   - representative compatibility glyph metrics
3. The remaining renderer text gaps are now cleanly outside this lane:
   - host FontStash reconstruction (`RG-G08`)
   - font build reproducibility and strict text validation (`RG-G09`)

## Residual Risk

Residual risk for the classic baked-font lane is now low.

Remaining medium-risk renderer text work is entirely upstream of the host text
engine and validation pipeline, not in the classic `tr_font.c` cache or atlas
ownership chain.
