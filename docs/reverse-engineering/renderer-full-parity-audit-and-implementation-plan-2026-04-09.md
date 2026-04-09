# `renderer` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-09

Scope: `src/code/renderer/*` plus renderer-facing Win32 and client glue in `src/code/win32/*` and `src/code/client/*` versus retail `quakelive_steam.exe`

Purpose: refresh the renderer parity assessment after the earlier `RG-P1`..`RG-P6` closure passes by re-auditing the current source tree against the committed retail renderer, text-host, and mapping evidence. The goal is to keep the documented renderer parity level honest, not just to preserve the previous best-case estimate.

## Audit Method And Evidence

Canonical evidence used for this refresh:

- Retail binary ownership: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL corpus: `references/hlil/quakelive/quakelive_steam.exe/`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Symbol/name support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `references/symbol-maps/client.json`
- Renderer mapping notes:
  - `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_37.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_38.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_42.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_43.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_44.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_66.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_98.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_100.md`
- Renderer/font-specific source notes:
  - `docs/platform/retail-font-stack.md`
  - `docs/renderer_cvar_matrix.md`
  - `docs/hud_render_baseline.md`
  - `docs/launcher_awesomium_audit.md`
- Validation evidence:
  - `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260409.json`
  - `artifacts/renderer_validation/logs/renderer_full_parity_gate.json`
  - `tools/ci/audit-retail-font-stack.ps1`
  - `pytest tests/test_renderer_*.py -q --tb=no`

Static committed-corpus snapshot:

- `quakelive_steam.exe` function corpus: `5473`
- imports: `351`
- exports: `2`
- analysis symbols: `4377`

## Current Verified State

The earlier renderer closure phases are still materially valid.

Observed verification facts on 2026-04-09:

1. `pytest tests/test_renderer_*.py -q --tb=no` completed with `20 passed, 1 skipped`.
2. `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260409.json` is still clean and continues to prove forced-windowed main-menu plus live `bloodrun` renderer startup/runtime coverage, including process-bound captures and engine screenshots.
3. `tools/ci/audit-retail-font-stack.ps1` now makes the remaining renderer-font debt explicit. It verifies the retail face-name mapping and Windows fallback probing already present in writable source, but it also emits three still-open warnings:
   - project files still reference missing in-tree FreeType sources under `src/code/ft2`
   - no committed source currently implements the retail `*fontstash` / `R_fonsErrorCallback` host text engine
   - `r_debugFontAtlas` is still only declaration/registration wiring, not an atlas draw implementation

That means the earlier renderer report overstated the amount of remaining renderer work by treating the entire residual text stack as only `tr_font.c` proof debt.

## What Still Holds From `RG-P1`..`RG-P6`

The following earlier closures remain supported by the committed evidence and the current test/runtime surface:

- `RG-G01` stays closed: the retail `GetRefAPI` export tail and the loading-view bridge slot remain restored.
- `RG-G02` stays closed: in-memory image loading and target-aware image creation remain present and used by the live resource bridge.
- `RG-G03` stays closed: the shader-backed rectangle-texture post-process path remains wired, and `r_contrast` remains registered and consumed.
- `RG-G04` stays closed: the retail Win32 resize/restart/loading-window behavior remains reconstructed and backed by runtime evidence.
- `RG-G06` stays closed: the dense backend/BSP/curve/flare/Win32 helper clusters remain explicitly bounded rather than open-ended ownership debt.
- `RG-G07` stays closed: the renderer still has a unified parity gate, tracked runtime evidence, and CI-visible validation wiring.

The important correction is narrower: those six closures are not enough to claim strict end-to-end retail renderer parity while the retail host text engine and the font build/source lane remain unreconstructed.

## Refreshed `renderer` Parity Estimate

- Previous public renderer estimate after `RG-P6`: **98%**
- Refreshed strict renderer estimate after this audit refresh: **94%**

This is a confidence correction, not a runtime regression.

Rationale:

1. The previous `98%` figure still reasonably describes the closed classic renderer core: export ABI, scene submission, image ingestion, post-process, Win32 restart path, helper-band ownership, and runtime validation.
2. Retail Quake Live also carries a second renderer-adjacent text engine in the host executable. That engine owns `*fontstash`, `R_fonsErrorCallback`, five named retail faces, Windows fallback probing, and the host `DrawScaledText` / `MeasureText` lane used by native `ui` and `cgame`.
3. The current source tree still satisfies those host imports through compatibility shims built on `fontInfo_t`, while the actual host FontStash-style engine remains absent. On top of that, the renderer project files still point at a missing in-tree FreeType vendor directory.

Confidence: medium-high.

## Open Gap Register

## RG-G05 - Classic renderer font/cache/atlas exactness remains partially source-biased

**Type:** Behavioral + ownership confidence  
**Priority:** P1  
**Retail evidence anchors:** `docs/reverse-engineering/quakelive_steam_mapping_round_37.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_38.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_43.md`, `docs/platform/retail-font-stack.md`, and `src/code/renderer/tr_font.c`  
**Status:** Open

### Gap

The classic renderer-backed font lane is functional, but it still mixes retail-backed behavior with explicit compatibility scaffolding that has not yet been fully partitioned.

Observed source-side facts:

1. `tr_font.c` still carries multiple non-trivial fallback behaviors at once: built-in glyph fallback, point-size-only legacy cache-name fallback, face-name normalization, and direct absolute-path file loading.
2. `RE_RegisterFont` remains reachable only through the proven UI/cgame import/syscall lanes, which is correct after `RG-P1`, but the helper-family ownership around cache naming, page naming, cached font loading, atlas build/layout, and fallback registration is still only partially mapped.
3. The unified renderer parity gate already treats this tranche as non-passing on purpose, which means the repo itself still classifies the classic font lane as unfinished.

### Closure target

1. Finish the focused `tr_font.c` ownership pass using the committed HLIL/Ghidra corpus and the retail font-stack note.
2. Separate retail-observed font/cache/atlas behavior from explicit compatibility-only scaffolding.
3. Add deterministic checks for cache names, atlas page names, and representative font metrics so future changes cannot silently drift.

## RG-G08 - Retail host FontStash text subsystem is still missing

**Type:** Behavioral + host-text renderer  
**Priority:** P0  
**Retail evidence anchors:** `docs/platform/retail-font-stack.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`, HLIL around `0x004420A4`, `0x00442313`, `0x00444049`..`0x004442E3`, and the current source in `src/code/client/cl_ui.c`, `src/code/client/cl_cgame.c`, and `src/code/renderer/tr_init.c`  
**Status:** Open

### Gap

Retail Quake Live owns a host-side text engine that the current source tree still does not reconstruct directly.

Observed retail facts from the committed corpus:

1. HLIL shows host-side creation of a texture named `*fontstash`, then immediate registration of that surface through the normal renderer image/shader path.
2. HLIL also exposes the error callback string `R_fonsErrorCallback: error %d val %d\n`, which is specific to that retained text engine.
3. The retail host initializes a five-face table:
   - `normal` -> `fonts/handelgothic.ttf`
   - `sans` -> `fonts/notosans-regular.ttf`
   - `mono` -> `fonts/droidsansmono.ttf`
   - `sans-fallback` -> `fonts/droidsansfallbackfull.ttf`
   - `sans-windows-fallback` -> `%WINDIR%\\fonts\\ARIALUNI.TTF`, `%WINDIR%\\fonts\\segoeui.ttf`, or `%WINDIR%\\fonts\\l_10646.ttf`
4. Mapping rounds 14 and 19 already prove that native `ui` and native `cgame` call shared host `DrawScaledText` / `MeasureText` helpers through the import seam.

Observed current-source facts:

1. `cl_ui.c` and `cl_cgame.c` now mirror the retail face-handle names and Windows fallback order, but both still satisfy `DrawScaledText` / `MeasureText` by resolving a `fontInfo_t` and manually iterating glyphs.
2. No committed source file currently references `*fontstash`, `R_fonsErrorCallback`, or a FontStash-like retained-text implementation.
3. `r_debugFontAtlas` is registered in `tr_init.c` and declared in `tr_local.h`, but there is still no atlas-draw implementation behind that cvar.

This is a real renderer parity gap, not just a naming gap. The source tree currently emulates the host text contract instead of reconstructing the host text engine that retail actually used.

### Closure target

1. Reconstruct the host-side retained text engine, including `*fontstash` texture ownership, error callback, and face-table lifetime.
2. Route the native `DrawScaledText` / `MeasureText` wrappers through that host engine instead of keeping the current `fontInfo_t` compatibility implementation as the primary path.
3. Implement the `r_debugFontAtlas` draw/debug path recovered from the host text subsystem.

## RG-G09 - Renderer font build reproducibility and strict validation remain incomplete

**Type:** Build/source parity + validation  
**Priority:** P1  
**Retail evidence anchors:** `src/code/renderer/renderer.vcxproj`, `src/code/renderer/renderer.vcproj`, `docs/platform/retail-font-stack.md`, `tools/ci/audit-retail-font-stack.ps1`, and the current renderer validation artifacts  
**Status:** Open

### Gap

Even after the host/text findings above, the repo still cannot reproduce the renderer font build shape that its own project files describe.

Observed facts:

1. `renderer.vcxproj` and `renderer.vcproj` still list a large `..\\ft2\\*` source and header inventory.
2. `src/code/ft2/` is currently absent from the repo.
3. The non-strict retail font audit already fails the remaining source debt explicitly when run in warning mode, which means the missing vendor drop and missing debug-atlas implementation are known gaps rather than hypothetical ones.
4. The current renderer runtime probe proves menu/map rendering, but it does not yet act as a strict text-engine parity proof for host font faces, font fallback, or atlas debugging.

### Closure target

1. Restore the renderer font build inputs in a committed, reviewable form that matches the intended project/build shape, or replace them with a documented equivalent without leaving stale project references behind.
2. Extend the renderer parity gate and the dedicated font audit so the open text/font gaps are machine-readable and strict-mode enforceable.
3. Capture final runtime evidence that specifically exercises host-text rendering and fallback faces, not only generic renderer startup.

## Closure Plan (Executable Tranches)

## RG-P7 - Classic renderer font exactness and atlas-output proof

Covers: `RG-G05`  
Goal: finish the old `tr_font.c` proof work so the classic renderer-backed font path is no longer carried as a mixed retail-plus-compatibility black box.

Deliverables:

1. A focused `tr_font.c` mapping pass that reconciles cache/page naming, cached-font loading, atlas build/layout, and fallback registration against the committed corpus.
2. Explicit documentation separating retail-backed behavior from compatibility-only fallbacks that the repo keeps intentionally.
3. Deterministic regression coverage for face-specific cache names, page names, and representative font metrics/atlas expectations.

Exit criteria:

- `RG-G05` no longer depends on prose alone to explain why a given fallback remains.
- The classic renderer font lane has deterministic structural or metric checks beyond the current "function exists" level.

Projected parity uplift: **94% -> 96%**

## RG-P8 - Host FontStash reconstruction and import-lane switchover

Covers: `RG-G08`  
Goal: replace the current compatibility-only host text wrappers with a reconstruction of the retail host text engine.

Deliverables:

1. Host-side retained text-engine lifetime, including `*fontstash` surface ownership and the recovered error callback path.
2. Retail face-table reconstruction for `normal`, `sans`, `mono`, `sans-fallback`, and `sans-windows-fallback`, with the observed Windows fallback order.
3. `QL_UI_trap_DrawScaledText`, `QL_UI_trap_MeasureText`, `QL_CG_trap_DrawScaledText`, and `QL_CG_trap_MeasureText` routed through the reconstructed host engine instead of the current glyph-loop compatibility implementation.
4. Working `r_debugFontAtlas` atlas visualization for the recovered host text lane.

Exit criteria:

- The source tree contains a direct `*fontstash`-owning text engine instead of only compatibility wrappers.
- Native `ui` and `cgame` no longer satisfy the text import seam purely through `fontInfo_t` glyph iteration.
- `r_debugFontAtlas` produces a real atlas-draw path.

Projected parity uplift: **96% -> 99%**

## RG-P9 - FreeType source recovery, strict font validation, and final runtime evidence

Covers: `RG-G09` and any residual font/text debt from `RG-P7`/`RG-P8`  
Goal: make the recovered renderer font/text stack reproducible, enforceable, and finally evidence-backed.

Deliverables:

1. The missing in-tree FreeType vendor source lane restored, or an explicitly documented replacement landed with the stale project references removed or corrected.
2. `tools/ci/audit-retail-font-stack.ps1` and `tests/test_renderer_full_parity_gate.py` upgraded so the remaining font/text gaps are strict-mode enforceable instead of warning-only.
3. Updated runtime evidence covering host text rendering in the main menu or HUD with multiple face handles and at least one Windows fallback case.

Exit criteria:

- The renderer project/build files no longer point at missing font-engine source.
- The dedicated font audit can run in strict mode without unresolved warnings.
- The final renderer parity gate can represent the font/text stack as fully passing.

Projected parity uplift: **99% -> 100%**

## Recommended Execution Order

1. Start with `RG-P7`. It is the cheapest remaining tranche and it removes ambiguity from the classic renderer-backed font lane before any larger host-text rewrite happens.
2. Move to `RG-P8` next. The strict parity correction in this audit is driven mainly by the unreconstructed host FontStash text engine, so that is now the highest-value remaining renderer implementation tranche.
3. Finish with `RG-P9`. Build reproducibility, strict audit enforcement, and final runtime evidence should be done after the actual text/font engine behavior is in place.

## Bottom Line

The renderer is not back at the old Quake III GPL baseline. The earlier `RG-P1`..`RG-P6` work remains valid and keeps the classic renderer core in strong shape. But strict retail Quake Live renderer parity is not accurately described by the older `98%` figure.

The refreshed open renderer gap set is now:

- `RG-G05`: classic renderer font/cache/atlas exactness is still partially source-biased
- `RG-G08`: the retail host FontStash text engine is still missing
- `RG-G09`: the renderer font build/source lane and strict text validation are still incomplete

So the current strict renderer estimate is best recorded as **94%**, with a three-phase remaining closure path (`RG-P7`..`RG-P9`) focused entirely on the retail font/text stack rather than on the rest of the renderer core.
