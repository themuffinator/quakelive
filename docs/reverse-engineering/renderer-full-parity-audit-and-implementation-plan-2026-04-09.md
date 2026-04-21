# `renderer` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-21

Scope: `src/code/renderer/*` plus renderer-facing Win32 and client glue in `src/code/win32/*` and `src/code/client/*` versus retail `quakelive_steam.exe`

Purpose: perform a fresh, evidence-backed parity audit of the renderer against the committed retail Quake Live corpus, verify which earlier closure tranches still hold, and turn every confirmed remaining renderer gap into an executable closure plan.

## Audit Method And Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Canonical committed evidence used for this audit:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Symbol and mapping support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `references/symbol-maps/client.json`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_37.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_38.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_42.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_43.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_66.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_98.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_100.md`
- Renderer and font notes:
  - `docs/platform/retail-font-stack.md`
  - `docs/reverse-engineering/renderer-font-cache-and-atlas-ownership-2026-04-10.md`
  - `docs/renderer_cvar_matrix.md`
  - `docs/hud_render_baseline.md`
  - `docs/launcher_awesomium_audit.md`
- Validation artifacts:
  - `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json`
  - `artifacts/renderer_validation/logs/renderer_full_parity_gate.json`
  - `tools/ci/audit-retail-font-stack.ps1`
  - `tests/test_renderer_font_build_lane_parity.py`
  - `tests/test_renderer_export_tail_parity.py`
  - `tests/test_renderer_font_exactness_parity.py`
  - `tests/test_renderer_memory_image_parity.py`
  - `tests/test_renderer_post_process_parity.py`
  - `tests/test_renderer_text_runtime_validation_parity.py`
  - `tests/test_renderer_win32_host_glue_parity.py`
  - `tests/test_renderer_internal_helper_mapping_parity.py`
  - `tests/test_renderer_full_parity_gate.py`

Method:

1. Start with the owning retail host binary and the committed metadata/import/export/function inventories.
2. Use promoted aliases and mapping rounds to bound file ownership before assuming an open parity gap.
3. Cross-check behavior claims against HLIL strings and call shapes when the current source still looks compatibility-biased.
4. Re-run the low-cost validation surface and compare it to the tracked runtime artifact rather than assuming the 2026-04-09 report is still current.

## Committed Corpus Snapshot

Retail `quakelive_steam.exe` metadata still reports:

- function corpus: `5473`
- imports: `351`
- exports: `2`
- promoted analysis symbols: `4377`

Renderer-adjacent alias coverage in `references/analysis/quakelive_symbol_aliases.json` remains materially strong. The `quakelive_steam` alias bucket currently contains at least these non-overlapping promoted prefix families:

- `106` `R_*` aliases
- `24` `RE_*` aliases
- `56` `RB_*` aliases
- `3` `GL_*` aliases
- `44` `QLUIImport_*` aliases
- `80` `QLCGImport_*` aliases
- `23` `AdvertisementBridge_*` aliases

Observed fact:

- The committed alias ledger is not sparse in the renderer core. It already bounds the world/model/shader/frame pipeline, the client-facing import slabs, and the advertisement bridge.

Inference:

- The renderer is no longer in a state where every uncovered helper should be treated as an active parity blocker. Most unresolved risk is now concentrated in a narrow text/font lane.

## Fresh Verification Snapshot

Validation rerun on 2026-04-10:

1. The tracked renderer test suite, the unified renderer parity gate, and the
   focused build-lane plus runtime-validation tests now run against the fully
   closed renderer gap set.
2. `tools/ci/audit-retail-font-stack.ps1 -RepoRoot <workspace>` now completes
   without unresolved warnings on the current source tree.
3. The renderer build metadata no longer points at a missing in-tree `ft2`
   vendor tree; the committed replacement lane is now the explicit external
   FreeType SDK or `pkg-config freetype2` path.
4. The tracked runtime artifact alias
   `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json`
   now proves:
   - forced-windowed UI bootstrap
   - forced-windowed retained-atlas debug rendering with `r_debugFontAtlas 1`
   - forced-windowed live `bloodrun` map runtime
   - no `RE_RegisterFont` fallback-lane hit in the tracked runtime logs
   - authoritative engine screenshots plus process-bound window captures
   - expected renderer init markers including `R_Init: InitOpenGL`,
     `R_Init: InitImages`, `R_Init: InitShaders`, `R_Init: InitFreeType`, and
     `R_Init: InitFontStash`
   The stable alias was refreshed on 2026-04-21 from the clean
   `renderer_runtime_evidence_20260421.json` bundle.

Observed fact:

- No current validation signal reopened any previously closed renderer tranche outside the already-documented text/font tail.

Inference:

- The 2026-04-09 strict estimate correction remains directionally correct, but
  the remaining renderer-text tail is now fully closed rather than still open.

## Current Subsystem Coverage Matrix

| Area | Current status | Writable files in scope | Strongest retail evidence | Audit conclusion |
| --- | --- | --- | --- | --- |
| Export ABI and loading bridge | Closed | `tr_public.h`, `tr_init.c`, `tr_scene.c`, `cl_main.c`, `cl_cgame.c` | mapping rounds 37, 38, and 43; alias `AdvertisementBridge_UpdateLoadingViewParameters`; parity gate `RG-G01` | The `GetRefAPI` tail still matches the retail contract, and the old mistaken `RegisterFont` export reading remains closed. |
| Memory-image ingestion and live resource registration | Closed | `tr_image.c`, `tr_local.h`, `cl_main.c`, `cl_steam_resources.c` | mapping round 42; aliases `R_CreateImageWithTarget`, `R_DetectImageTypeFromMemory`, `R_LoadImageFromMemory`; parity gate `RG-G02` | The retail in-memory image lane remains reconstructed and actively used by launcher or Steam resource ingestion. |
| Post-process and color correction | Closed | `tr_backend.c`, `tr_init.c`, `tr_local.h` | HLIL strings for `brightpass`, `downsample1`, `blurvertical`, `blurhoriz`, `combine`, and `colorcorrect`; parity gate `RG-G03` | The recovered shader-backed rectangle-texture pipeline still matches the committed retail shader family. |
| World, model, surface, and scene runtime | Closed with bounded helper uncertainty | `tr_bsp.c`, `tr_curve.c`, `tr_light.c`, `tr_main.c`, `tr_marks.c`, `tr_mesh.c`, `tr_model.c`, `tr_scene.c`, `tr_shader.c`, `tr_shade*.c`, `tr_sky.c`, `tr_surface.c`, `tr_world.c` | `R_*`, `RE_*`, and `RB_*` alias families; mapping rounds 37 and 100; runtime probe on `bloodrun` | No new retail evidence pushed these files back into the open gap register. The remaining unmapped leaves are bounded helpers beneath already-promoted runtime owners. |
| Win32 renderer host glue | Closed | `win_wndproc.c`, `win_glimp.c`, `win_syscon.c`, `win_main.c`, `win_local.h` | mapping rounds 98 and 100; runtime capture artifact; parity gates `RG-G04` and `RG-G07` | Resize sync, maximized-window retention, and loading-window ownership remain aligned with the committed retail host. |
| Classic renderer font lane | Closed | `tr_font.c`, `tr_init.c`, `tr_local.h` | `docs/platform/retail-font-stack.md`; `docs/reverse-engineering/renderer-font-cache-and-atlas-ownership-2026-04-10.md`; parity gate `RG-G05` | The classic FreeType-backed lane is now bounded: retail-backed cache/page/atlas behavior is separated from compatibility-only fallbacks, and deterministic tests pin the resulting proof surface. |
| Renderer-owned host text core | Closed | `tr_font.c`, `tr_init.c`, `tr_local.h` | HLIL `0x004420A4`, `0x00442313`, `0x00443720`, `0x00443BE0`, `0x00444360`, `0x00444049`..`0x004442E3`; `docs/platform/retail-font-stack.md`; `docs/reverse-engineering/renderer-host-text-core-ownership-2026-04-10.md` | The retained `*fontstash` atlas, retail-style atlas overflow callback, five-face host text table, UTF-8 codepoint decode, and retained fallback-face glyph probing now exist in writable renderer source. |
| Native UI and cgame host text imports | Closed | `cl_ui.c`, `cl_cgame.c`, `cl_main.c`, `tr_font.c` | HLIL `QLUIImport_DrawScaledText`, `QLUIImport_MeasureText`; mapping rounds 14 and 19; `docs/reverse-engineering/renderer-host-text-import-switchover-and-debug-atlas-2026-04-10.md` | The native `ui` and `cgame` import wrappers now route through the shared renderer-owned host text helpers instead of iterating `fontInfo_t` glyphs locally. |
| Font build reproducibility and strict text validation | Closed | `renderer.vcxproj`, `renderer.vcxproj.filters`, `renderer.vcproj`, `quakelive_steam.vcxproj`, `.vscode/build.ps1`, `src/code/unix/Makefile`, `tools/ci/audit-retail-font-stack.ps1`, `tools/renderer/run_renderer_runtime_probe.ps1`, `tests/test_renderer_full_parity_gate.py` | repo-managed FreeType replacement lane, strict font audit, and tracked `RG-P11` runtime artifact | The renderer now has a reproducible FreeType build lane and a text-specific strict runtime proof, so `RG-G09` is closed. |

## What Still Holds From `RG-P1`..`RG-P6`

The earlier `RG-P1`..`RG-P6` work remains valid.

The following earlier closure tranches still hold after the fresh audit pass:

- `RG-G01` stays closed. The retail renderer export-tail ABI remains restored, and `AdvertisementBridge_UpdateLoadingViewParameters` is still the proven slot between `RenderScene` and `SetColor`.
- `RG-G02` stays closed. The target-aware image constructor and memory decode lane remain present and structurally validated.
- `RG-G03` stays closed. The shader-backed post-process family and recovered `r_contrast` lane remain in writable source.
- `RG-G04` stays closed. The retail Win32 resize, restart, and loading-window behavior remains reconstructed and runtime-backed.
- `RG-G06` stays closed. The dense helper bands in `tr_backend.c`, `tr_bsp.c`, `tr_curve.c`, `tr_flares.c`, and `win_glimp.c` are still bounded compatibility decompositions rather than active-runtime unknowns.
- `RG-G07` stays closed. The renderer still has a dedicated parity gate, tracked runtime artifact, and CI-visible validation wiring.

Observed fact:

- No new committed source or validation result justified reopening scene submission, world traversal, post-process, Win32 host glue, or runtime gating as active renderer-core gaps.

Inference:

- No confirmed renderer gap remains downstream of the host text engine, the
  build lane, or the strict runtime-evidence surface after the 2026-04-17 font
  audit refresh reclosed the hidden retained-host exactness tail.

## Refreshed Strict Parity Estimate

- Previous strict renderer estimate before the 2026-04-09 correction: **98%**
- Strict renderer estimate after the 2026-04-09 correction: **94%**
- Strict renderer estimate after this 2026-04-10 re-audit: **94%**
- Strict renderer estimate after `RG-P7` closure: **95%**
- Strict renderer estimate after `RG-P8` closure: **97%**
- Strict renderer estimate after `RG-P9` closure: **98%**
- Strict renderer estimate after `RG-P10` closure: **99%**
- Strict renderer estimate after `RG-P11` closure: **100%**

This audit does not introduce another confidence correction. It confirms that
the previous strict estimate was the honest baseline, that `RG-P7` closed the
classic font lane, that `RG-P8` closed the retained renderer-side host-text
core half of `RG-G08`, that `RG-P9` closed the active native-import plus
debug-atlas half, that `RG-P10` closed the build-lane half of `RG-G09`, and
that `RG-P11` closed the final strict-validation half.

The 2026-04-17 full font audit reopened one hidden renderer-host exactness tail
inside the earlier `RG-P8` closure and closed it in the same pass:

- UTF-8 host text had still been decoded as raw bytes in source.
- Retained glyph lookup had still been keyed as a fixed 256-entry atlas instead
  of decoded codepoint plus rounded size tenths.
- The recovered fallback faces were retained in state but not automatically
  probed during host glyph resolution.
- The host draw helper still consumed non-digit caret sequences and still drew
  recognized color escapes literally when `forceColor` was set.

The strict percentages above therefore remain unchanged, but the font/text
closure now has direct source-backed proof for the remaining Unicode and
fallback behavior that retail exposes.

Confidence:

- high for the renderer core
- high for the final text/font closure state

## Gap Register

## RG-G05 - Classic renderer font/cache/atlas exactness remains partially source-biased

**Type:** Behavioral + ownership confidence  
**Priority:** P1  
**Status:** Closed

Retail evidence anchors:

- `docs/reverse-engineering/quakelive_steam_mapping_round_37.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_38.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_43.md`
- `docs/platform/retail-font-stack.md`
- `docs/reverse-engineering/renderer-font-cache-and-atlas-ownership-2026-04-10.md`
- current source in `src/code/renderer/tr_font.c`

Closure summary:

1. `tr_font.c` now has an explicit retail-backed helper family for the classic baked-font lane:
   - `R_BuildFontCacheStem`
   - `R_BuildFontCacheName`
   - `R_BuildFontPageName`
   - `R_FindCachedFontDataName`
   - `R_RegisterCachedFontShaders`
   - `R_FlushFontAtlasPage`
2. The compatibility-only branches that remain are now explicit rather than mixed into an open-ended ownership bucket:
   - point-size-only cache fallback
   - built-in glyph fallback
   - absolute-path host font reads
3. Deterministic proof now exists for the classic lane:
   - normalized cache stems
   - face-specific cache/page names
   - inclusive cached-font shader rebinding across `GLYPH_START..GLYPH_END`
   - inclusive final atlas-page assignment including glyph `255`
   - representative compatibility glyph metrics

Result:

- `RG-G05` is now closed. The remaining renderer text debt is no longer in the classic `tr_font.c` cache or atlas ownership chain.

## RG-G08 - retail host text import switchover and debug-atlas closure

**Type:** Behavioral + host text renderer  
**Priority:** P0  
**Status:** Closed

Retail evidence anchors:

- `docs/platform/retail-font-stack.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`
- `docs/reverse-engineering/renderer-host-text-core-ownership-2026-04-10.md`
- `docs/reverse-engineering/renderer-host-text-import-switchover-and-debug-atlas-2026-04-10.md`
- HLIL at `0x004420A4`, `0x00442313`, `0x0044D0EB`, and the `r_debugFontAtlas` registration block
- current source in `src/code/client/cl_ui.c`, `src/code/client/cl_cgame.c`, `src/code/renderer/tr_font.c`, `src/code/renderer/tr_backend.c`, and `src/code/renderer/tr_init.c`

Observed facts:

1. Mapping rounds 14 and 19 prove that native `ui` and native `cgame` import shared host `DrawScaledText` and `MeasureText` helpers.
2. `tr_font.c` now contains shared `RE_DrawScaledText` and `RE_MeasureScaledText` helpers plus the retained `*fontstash` debug-info bridge.
3. `cl_ui.c` and `cl_cgame.c` now satisfy the native imports by forwarding directly into those shared renderer helpers instead of by resolving `fontInfo_t` locally and iterating glyphs in client code.
4. `tr_backend.c` now contains a retained-atlas draw path guarded by `r_debugFontAtlas`.
5. The focused renderer gate and font audit now both report `RG-G08` as closed,
   and the downstream `RG-G09` tail has since been closed by `RG-P10` and
   `RG-P11`.

Result:

- retail host text import switchover and debug-atlas closure are now complete.
- `RG-G08` is now closed. Native host-text ownership is no longer an open
  renderer gap, and the downstream build-lane plus strict-validation tail
  recorded under `RG-G09` is now also closed.

## RG-G09 - Renderer font build reproducibility and strict validation are now complete

**Type:** Build/source parity + validation  
**Priority:** P1  
**Status:** Closed

Retail evidence anchors:

- `src/code/renderer/renderer.vcxproj`
- `src/code/renderer/renderer.vcproj`
- `docs/platform/retail-font-stack.md`
- `tools/ci/audit-retail-font-stack.ps1`
- `tests/test_renderer_full_parity_gate.py`

Observed facts:

1. `renderer.vcxproj`, `renderer.vcxproj.filters`, and `renderer.vcproj` no
   longer reference `..\ft2\*`.
2. `renderer.vcxproj`, `quakelive_steam.vcxproj`, `.vscode/build.ps1`, and
   `src/code/unix/Makefile` now describe one explicit repo-managed FreeType
   replacement lane, with codec dependencies bootstrapped from
   `src/libs/_deps`, instead of probing external SDK or Vcpkg installs.
3. `tools/ci/audit-retail-font-stack.ps1` now validates the final build-lane
   and runtime-evidence surface without unresolved warnings.
4. The renderer parity gate now passes `RG-G01` through `RG-G09`.
5. The tracked runtime artifact alias
   `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json`
   now proves text-specific behavior through distinct startup/bootstrap,
   debug-atlas, and live-map captures plus a no-fallback runtime log surface.

Inference:

- The renderer now has a complete source, build, validation, and tracked
  runtime story for the retail text stack.

Closure summary:

1. The stale in-tree `ft2` project references were removed and replaced with a
   documented repo-managed FreeType lane plus repo-managed codec bootstrap.
2. The font audit and renderer parity gate now treat the final font/text
   conditions as strict closure checks.
3. The final runtime artifact now explicitly exercises retained-atlas debug
   rendering instead of only generic menu or map startup.

## Dependency Map

No current evidence suggests reopening `RG-G01` through `RG-G08` as
prerequisites, and no confirmed open renderer gap remains.

## Closure Plan (Executable Tranches)

## RG-P7 - Classic renderer font exactness and atlas proof [COMPLETED]

Covers: `RG-G05`

Outcome: complete. The classic `tr_font.c` proof work is now strong enough to close `RG-G05`.

Completed deliverables:

1. Published `docs/reverse-engineering/renderer-font-cache-and-atlas-ownership-2026-04-10.md`, which separates retail-backed cache/page/atlas behavior from compatibility-only fallbacks.
2. Tightened `tr_font.c` so the classic font lane now has explicit cache-stem, cached-font reload, and atlas-flush ownership helpers with inclusive glyph coverage.
3. Added deterministic renderer tests that pin representative cache names, page names, atlas assignment, and compatibility glyph metrics.

Exit criteria:

- satisfied

Projected parity uplift: **94% -> 95%**

## RG-P8 - Host text-engine core recovery [COMPLETED]

Covers: first half of `RG-G08`

Outcome: complete. The renderer now owns the retained host text core that retail uses beneath the native `ui` and `cgame` imports.

Completed deliverables:

1. A committed source lane that owns the `*fontstash` texture lifecycle.
2. A committed `R_fonsErrorCallback` or equivalent recovered error path.
3. Retail face-table ownership for `normal`, `sans`, `mono`, `sans-fallback`, and `sans-windows-fallback`.
4. The 2026-04-17 audit refresh completed the exact retained behavior inside that core:
   - UTF-8 codepoint decode in host draw/measure
   - decoded codepoint plus rounded size-tenths glyph caching
   - automatic retained fallback-face probing
   - digit-only host color-escape consumption with retail `forceColor` handling

Exit criteria:

- satisfied

Projected parity uplift: **95% -> 97%**

## RG-P9 - Native import switchover and debug-atlas closure [COMPLETED]

Covers: second half of `RG-G08`

Outcome: complete. The retained host text core is now the active native `ui` and `cgame` import path, and the retained atlas now has a debug draw surface.

Completed deliverables:

1. `QL_UI_trap_DrawScaledText` and `QL_UI_trap_MeasureText` routed through the host text engine.
2. `QL_CG_trap_DrawScaledText` and `QL_CG_trap_MeasureText` routed through the same host engine.
3. Working `r_debugFontAtlas` visualization for the recovered retained atlas.

Exit criteria:

- satisfied

Projected parity uplift: **97% -> 98%**

## RG-P10 - Font build-lane recovery [COMPLETED]

Covers: build reproducibility half of `RG-G09`

Outcome: complete. The renderer build description is now coherent again.

Completed deliverables:

1. Landed the explicit repo-managed FreeType replacement lane across
   `tr_font.c`, `renderer.vcxproj`, `quakelive_steam.vcxproj`,
   `.vscode/build.ps1`, and `src/code/unix/Makefile`.
2. Removed the stale `..\ft2\*` entries from the legacy renderer project
   descriptions and published
   `docs/reverse-engineering/renderer-freetype-build-lane-recovery-2026-04-10.md`.

Exit criteria:

- satisfied

Projected parity uplift: **98% -> 99%**

## RG-P11 - Strict validation and final runtime evidence [COMPLETED]

Covers: remaining validation half of `RG-G09`

Outcome: complete. The final renderer parity claim is now strict and
runtime-backed.

Completed deliverables:

1. Upgraded `tools/ci/audit-retail-font-stack.ps1` so the final font/text
   closure conditions are machine-checked.
2. Aligned `tests/test_renderer_full_parity_gate.py` and the focused renderer
   font/runtime tests with the fully closed gap set.
3. Refreshed the runtime probe and tracked
   `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json`
   so the retained-atlas debug pass is now part of the closure proof.
4. Closed the remaining runtime blocker in the classic `RE_RegisterFont`
   atlas builder so uncached UI font generation now bounds-checks glyph copies
   before they can overrun the 256x256 page buffer.

Exit criteria:

- satisfied

Projected parity uplift: **99% -> 100%**

## Recommended Execution Order

1. `RG-P10` landed first so the intended text engine had a reproducible
   committed build lane.
2. `RG-P11` landed second so the final parity claim is backed by strict
   validation and text-specific runtime artifacts.

## Bottom Line

This audit does not find a new broad renderer-core regression. The renderer
core remains in strong shape, and the previously closed export, image,
post-process, Win32, helper-ownership, and runtime-gate tranches still hold.

No confirmed renderer gaps remain after `RG-P11`.

So the current strict renderer estimate is now **100%**.
