# Renderer Text Strict Validation And Runtime Evidence

Last updated: 2026-04-10

Scope: `RG-P11`

## Why this tranche remained open

Even after the classic font lane, retained host text core, native import
switchover, and debug-atlas draw path were reconstructed, the remaining
renderer parity claim was still too loose:

- the unified gate still hard-coded `RG-G09` as failing
- the runtime artifact was still the earlier `RG-P6` renderer snapshot
- no tracked runtime bundle proved that the retained font atlas changed rendered
  output under `r_debugFontAtlas`

## Validation changes landed

1. `tools/renderer/run_renderer_runtime_probe.ps1` now writes the `RG-P11`
   artifact `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260410.json`.
2. That artifact now captures three distinct passes:
   - windowed UI-bootstrap render pass
   - retained-atlas debug render with `r_debugFontAtlas 1`
   - live `bloodrun` map runtime
3. The artifact now records engine-screenshot SHA256 hashes in addition to the
   existing process-bound window hashes, so the debug-atlas pass is proven to
   change rendered output instead of only producing another screenshot file.
4. The runtime artifact now fails strict closure when any pass logs
   `RE_RegisterFont: FreeType code not available` or the built-in bigchars
   compatibility fallback, which keeps `RG-P11` pinned to the real
   `BUILD_FREETYPE` lane instead of to the compatibility path.
5. `tests/test_renderer_full_parity_gate.py`,
   `tests/test_renderer_font_build_lane_parity.py`, and
   `tests/test_renderer_text_runtime_validation_parity.py` now treat the
   renderer as fully closed only when the new build-lane and runtime evidence
   surface is present and clean.
6. `tools/ci/audit-retail-font-stack.ps1` now validates the same final
   conditions instead of reproducing the old missing-`ft2` warning.
7. Dump-backed runtime triage also recovered a classic `RE_RegisterFont`
   overflow in `RE_ConstructGlyphInfo`, so the old 256x256 atlas path now
   rejects out-of-bounds glyph copies before any row write can trample the next
   zone block.

## Closure result

Observed facts after the change:

- the tracked runtime artifact phase is now `RG-P11`
- the retained debug-atlas pass is present and hash-distinct from the normal
  UI-bootstrap pass
- the runtime artifact no longer treats the `RE_RegisterFont` compatibility
  fallback as an acceptable strict-validation result
- the classic `RE_RegisterFont` path no longer corrupts heap state while
  generating uncached font pages for the `ui` bootstrap fonts
- the unified renderer parity gate no longer reports any non-passing gap IDs

Inference:

- The renderer parity claim is now backed by strict source, build, CI, and
  tracked runtime evidence for the full text stack instead of by warning-based
  notes.

RG-P11 is now considered complete.
