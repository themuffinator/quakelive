# Quake Live Steam Host Mapping Round 284

Date: 2026-05-20

## Scope

This renderer pass closes the remaining unnamed helper corridor around curved
surface patch grids in `tr_curve.c`. Earlier rounds already promoted the large
owners, including `R_SubdividePatchToGrid`, `MakeMeshNormals`,
`R_GridInsertColumn`, and `R_GridInsertRow`; this round maps the internal
helpers that interpolate drawverts, transpose and invert the grid, place
approximating points on the curve, and allocate or free `srfGridMesh_t`
instances.

No source behavior changed in this round.

## Evidence Used

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/renderer/tr_curve.c`
- `src/code/renderer/tr_local.h`
- `src/code/renderer/tr_bsp.c`

## Promoted Symbols

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_43D160` | `LerpDrawVert` | High | Averages drawvert xyz, st, lightmap, and color channels, and is called by subdivision plus row/column insertion paths. |
| `sub_43D200` | `Transpose` | High | Swaps/copies `0x2c` byte drawverts across a `MAX_GRID_SIZE` stride and is called after each subdivision direction pass. |
| `sub_43DB20` | `InvertCtrl` | High | Reverses each row in the control grid after the longest-tristrip flip. |
| `sub_43DBB0` | `InvertErrorTable` | High | Copies the two-row LOD error table, swaps width/height lanes, and reverses the height side. |
| `sub_43DCB0` | `PutPointsOnCurve` | High | Runs two passes of nested `LerpDrawVert` calls over odd rows and columns before colinear culling. |
| `sub_43DE30` | `R_CreateSurfaceGridMesh` | High | Allocates `(width * height * sizeof(drawVert_t)) + grid header`, copies width and height LOD error arrays, sets `SF_GRID`, accumulates bounds, and derives local/lod radius. |
| `sub_43E000` | `R_FreeSurfaceGridMesh` | High | Frees `widthLodError`, `heightLodError`, and the grid allocation in that order. |

## Wiring Notes

Observed facts:

- `sub_43E030` calls `sub_43D200` during the two-axis subdivision loop, then
  calls `sub_43DCB0`, `sub_43DBB0`, `sub_43DB20`, `MakeMeshNormals`, and
  `sub_43DE30` before returning the final grid.
- `sub_43E870` and `sub_43EB70` both call `sub_43D160`, rebuild the LOD error
  tables from an existing grid, free the old grid storage, and then call
  `sub_43DE30` for the replacement grid.
- `tr_bsp.c` also reaches `R_FreeSurfaceGridMesh` after cloning patch grids into
  hunk storage during BSP surface finalization.
- `tr_local.h` exposes only the patch-grid entry points and the free helper;
  the interpolation, transpose, inversion, and placement helpers remain
  file-local implementation details in `tr_curve.c`.

Inference:

- The retail compiler preserved all of the meaningful `tr_curve.c` helper
  boundaries except the high-level row/column replacement comments and local
  variable names. The recovered call graph now matches the source ownership
  boundaries without needing source edits.

## Open Follow-Up

- The renderer command ABI follow-up from round 282 remains open:
  `R_AddAdvertisementQueryCmd` is still not proven as a standalone retail
  function. Current HLIL shows the advertisement-query backend consumer and the
  render-view update/debug path, but not a distinct enqueue helper.
- The next renderer mapping pass can continue just past this address band into
  the flare pool/test helpers at `sub_43EE30` and `sub_43EE70`, which sit after
  the patch-grid row insertion function.

## Guard Coverage

`tests/test_renderer_internal_helper_mapping_parity.py` now checks this round's
patch-grid aliases against the alias ledger, Ghidra `functions.csv`, HLIL
function entries and call-chain evidence, and the local source owners in
`tr_curve.c`, `tr_local.h`, and `tr_bsp.c`.

## Parity Estimate

- Renderer patch/curve helper symbol coverage: before 82%, after 96%.
- Renderer internal helper map overall: before 98%, after 99%.
- Retail behavior parity: unchanged by this mapping-only round.
