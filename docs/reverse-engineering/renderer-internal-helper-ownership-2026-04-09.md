# Renderer Internal Helper Ownership (2026-04-09)

## Phase 5 Ownership Closure

This note records the `RG-P5` ownership outcome for the highest-density
renderer-internal helper bands in writable source.

The key conclusion is narrow and deliberate:

- the active runtime above these helpers is already retail-bounded
- the remaining file-local helpers are now treated as source-backed
  compatibility decompositions or compiler-shaped splits
- future alias promotion is still allowed, but it is no longer required to keep
  these files out of an open-ended risk bucket

## File-Band Conclusions

| File | Strongest observed retail signal | Confidence | Phase 5 conclusion |
| --- | --- | --- | --- |
| `tr_backend.c` | The committed alias ledger already owns the renderer frame lifecycle, the stage-iterator family, the surface submission band, and the Quake Live post-process block above `InitOpenGL`. `RG-P3` also closed the retail behavioral exactness of the post-process/resource lane. | Medium | Treat the remaining `RBPP_*`, split GL state helpers, and 2D setup helpers as source-backed decompositions of already-bounded retail runtime owners. Do not keep this file in a broad "unknown renderer owner" bucket. |
| `tr_bsp.c` | The committed corpus already owns `RE_LoadWorldMap`, `RE_SetWorldVisData`, the world/PVS traversal slab, the brush-model lighting band, and the world-surface submission path. | Medium | Treat the remaining parser, patch-stitch, and lump-loader leaves as inner helpers inside an already-bounded world-load/runtime owner chain. Additional alias promotion is optional future evidence work, not an active runtime blocker. |
| `tr_curve.c` | The patch path is already bounded by the mapped grid-surface submission owner and the anchored world/patch load chain. The remaining helpers are isolated math and control-point transforms. | Medium | Keep the curve kernels as source-backed compatibility helpers until a future retail pass yields stronger standalone boundaries. Their ownership uncertainty is now low risk because the active runtime above them is already bounded. |
| `tr_flares.c` | The flare path is bounded by the mapped projection helper `R_TransformClipToWindow`, the anchored scene/view submission slab, and the current source reconstruction of the flare fade/readback path. | Medium | Treat the flare-only leaves as a bounded local helper family rather than an unresolved active-runtime ownership gap. Promote a direct alias later only if the committed retail corpus exposes a stronger standalone owner. |
| `win_glimp.c` | `RG-P4` already recovered the exact windowed resize/restart/loading behavior, while the renderer bootstrap band is additionally anchored by `InitOpenGL`, `R_GetMode`, `R_GetModeInfo`, and the committed HLIL strings for the PFD/bootstrap error paths. | Medium | Keep the remaining PFD chooser, driver bootstrap, and render-thread utility leaves as source-backed wrappers beneath already-bounded host/runtime behavior. The file no longer carries an open ownership-risk label. |

No unresolved high-impact ownership gap remains in an active runtime path. The
remaining uncertainty in these files is now explicitly bounded as future-evidence
alias-promotion work rather than a current renderer parity blocker.

## Future Evidence Watchlist

1. Only promote an additional helper alias in these files if a future committed
   HLIL or Ghidra pass yields at least two independent signals for a concrete
   standalone retail owner.
2. Keep treating `RBPP_*` as a source-level decomposition of the already-closed
   Quake Live post-process band unless a stronger retail split is recovered.
3. Revisit the local patch/curve kernels only if a later renderer validation
   pass finds a behavioral mismatch that cannot be explained by the already
   bounded outer owners.
