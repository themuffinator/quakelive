# Quake Live Steam Host Mapping Round 100

## Scope

This round is a focused `RG-P5` recheck of the dense internal renderer helper
bands that were still carrying the highest "unmatched helper" counts after the
behavioral renderer tranches landed.

The goal here is narrower than the earlier export, image, post-process, and
Win32 restart passes:

- revalidate the remaining helper-density hot spots in `tr_backend.c`,
  `tr_bsp.c`, `tr_curve.c`, `tr_flares.c`, and `win_glimp.c`
- separate true ownership uncertainty from source-backed compatibility
  decompositions and compiler-shaped helper splits
- close the open-ended `RG-G06` risk without inventing aliases that the
  committed retail corpus still does not bound strongly enough

The primary evidence for this round is:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- `docs/reverse-engineering/quakelive_steam_mapping_round_36.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_38.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_44.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_46.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_98.md`
- `src/code/renderer/tr_backend.c`
- `src/code/renderer/tr_bsp.c`
- `src/code/renderer/tr_curve.c`
- `src/code/renderer/tr_flares.c`
- `src/code/win32/win_glimp.c`

## What Was Rechecked

Observed local facts:

1. The committed alias ledger already anchors the most behavior-critical
   renderer-internal owners that sit around these files:
   `RE_BeginFrame`, `RE_EndFrame`, `R_TransformClipToWindow`,
   `RB_StageIteratorGeneric`, `RB_StageIteratorVertexLitTexture`,
   `RB_StageIteratorLightmappedMultitexture`, `RB_CheckOverflow`,
   `RB_SurfacePolychain`, `RB_SurfaceTriangles`, `RB_SurfaceMesh`,
   `RB_SurfaceFace`, `RB_SurfaceGrid`, `R_CullGrid`, `R_CullSurface`,
   `R_DlightFace`, `R_DlightGrid`, `R_DlightSurface`,
   `R_AddBrushModelSurfaces`, `R_RecursiveWorldNode`, `R_PointInLeaf`,
   `R_ClusterPVS`, `R_inPVS`, `R_MarkLeaves`, `R_AddWorldSurfaces`,
   `InitOpenGL`, `R_GetMode`, and `R_GetModeInfo`.
2. The helper-density hot spots still called out by the renderer audit are now
   dominated by static helpers that sit inside already-bounded runtime owners
   instead of by large missing public seams.
3. The strongest remaining concentrations separate cleanly into three buckets:
   - source-backed Quake Live decompositions such as the `RBPP_*`
     post-process/resource helpers in `tr_backend.c`
   - classic GPL-era math and parser kernels such as the patch/curve helpers in
     `tr_bsp.c` and `tr_curve.c`
   - small Win32 bootstrap utilities in `win_glimp.c` whose outer behavior is
     already bounded by the `RG-P4` restart and loading-window recovery

## What Still Is Not Promoted

This round intentionally did not fabricate new retail aliases for the inner
file-local helpers that still lack a stable two-signal standalone owner in the
committed corpus.

The bounded watchlist now looks like this:

- `tr_backend.c`
  - `RBPP_*` post-process setup, resource, and submission helpers
  - split GL/2D/state utilities such as the local `GL_Bind` and `RB_SetGL2D`
    decomposition
- `tr_bsp.c`
  - parser/stitching/load-lump kernels such as `ParseFace`,
    `R_StitchPatches`, and the patch-hunk movers
- `tr_curve.c`
  - patch subdivision math helpers such as `LerpDrawVert`,
    `MakeMeshNormals`, and the error-table transforms
- `tr_flares.c`
  - the flare-only leaf helpers that remain source-local beneath the already
    mapped projection/view owners
- `win_glimp.c`
  - local PFD/bootstrap/render-thread wrappers beneath the already-recovered
    window-mode and restart behavior

The reason not to promote them yet is now explicit rather than vague: the
committed retail corpus does not give a stronger standalone boundary than the
current source decomposition already does.

## Phase 5 Closure Update (2026-04-09)

The targeted `RG-P5` recheck did not justify any additional alias promotions in
these file bands. A fresh pass across the committed HLIL, the Ghidra function
starts, the existing renderer mapping rounds, and the current writable source
still does not expose new two-signal standalone retail owners for the remaining
inner helpers, so no new aliases were promoted in this pass.

That negative result is still enough to close the active ownership gap. The
outer active runtime paths in the `RG-G06` band are already bounded by promoted
retail owners such as the scene frame lifecycle, the world/PVS traversal slab,
the surface-iterator family, the clip-to-window projection helper, the
post-process bootstrap closure from `RG-P3`, and the Win32 restart/loading
closure from `RG-P4`. The correct `RG-P5` outcome is therefore to document the
remaining helper families explicitly as source-backed compatibility
decompositions or compiler-shaped micro-splits rather than to keep them in an
open-ended "missing retail owner" bucket.

No unresolved high-impact ownership gap remains in an active runtime path.
What remains is a bounded future-evidence watchlist: only promote an additional
renderer-internal alias later if a future committed retail pass yields at least
two independent signals for a concrete standalone owner.

## Result

This round raises the quality of the renderer ownership notes without inventing
new aliases. The effective result is that the renderer's remaining open work is
no longer the backend/BSP/curve/flare helper-density band; it is now limited to
the still-open font helper-family proof work and the missing renderer-wide
validation/evidence gate.
