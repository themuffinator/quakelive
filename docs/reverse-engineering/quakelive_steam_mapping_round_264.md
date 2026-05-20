# Quake Live Steam Host Mapping Round 264

## Scope

This pass stayed in the `cgame/cg_main.c` scoreboard feeder corridor that sits
between the HUD menu parser and the richer feeder text leaves.

The directly checked helpers were:

- `0x10025E60 -> CG_OwnerDrawHandleKey`
- `0x10025F60 -> CG_SetScoreSelection`
- `0x100260E0 -> CG_InfoFromScoreIndex`

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` maps these retail starts
  to the current recovered names.
- `references/symbol-maps/cgame.json` records the same helpers and signatures.
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows
  `0x10025E60` as the pure zero-return stub assigned into both the ownerdraw
  key slot and the feeder-image slot by `CG_InitDisplayContext`.
- The `0x10025F60` HLIL block resolves the local client's absolute score row
  into the selected score cache, then drives the menu feeder selection path.
- The `0x100260E0` HLIL block is the feeder row resolver: it walks score rows in
  team modes, writes the absolute score index through the out-param, and returns
  the owning `clientInfo_t` block.

## Source Updates

- Added the required function header above `CG_OwnerDrawHandleKey`.
- Normalized `CG_OwnerDrawHandleKey` to repository parameter spacing.
- Added the required function header above `CG_SetScoreSelection` and normalized
  its declaration in both `cg_main.c` and `cg_local.h`.
- Added the required function header above `CG_InfoFromScoreIndex`, normalized
  its declaration, and cleaned the local team-row loop formatting.
- Preserved behavior: no feeder ids, row-selection rules, or cgame/UI bridge
  calls were changed.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the normalized
  `CG_SetScoreSelection` prototype, source-side `CG_InfoFromScoreIndex`
  scoreboard/team-row mapping, and the committed HLIL anchors for
  `0x10025F60` / `0x100260E0`.

## Parity Estimate

- Before: scoreboard feeder selection declaration/evidence parity was about
  97%.
- After: about 98%.

This was a source-compliance and evidence-lock round, not a behavioral rewrite.
