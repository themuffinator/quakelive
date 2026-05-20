# Quake Live Steam Host Mapping Round 265

## Scope

This pass stayed on the `cg_main.c` display-context callback seam immediately
after the scoreboard feeder text dispatcher.

The directly checked helpers were:

- `CG_FeederItemImage`
- `0x10028B10 -> CG_FeederSelection`
- `0x10028D30 -> CG_Text_PaintWithCursor`

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows the
  display-context bootstrap assigning:
  - `data_10a256A4 = sub_10025e60` for the feeder-image null callback
  - `data_10a256A0 = sub_10028830` for the feeder-text dispatcher
  - `data_10a256A8 = sub_10028b10` for feeder selection
  - `data_10a25688 = sub_10028d30` for cursor-text drawing
- The `0x10028B10` HLIL block references `playerlistRED` and `playerlistBLUE`,
  updates the selected score cache, writes the active team-list cursor, and
  clears the opposite list cursor to `-1`.
- The `0x10028D30` HLIL body is still the thin cursor-signature text wrapper
  that forwards into the shared cgame text painter.
- `references/analysis/quakelive_symbol_aliases.json` and
  `references/symbol-maps/cgame.json` already carry the recovered callback names
  for `CG_FeederSelection` and `CG_Text_PaintWithCursor`.

## Source Updates

- Normalized `CG_FeederItemImage` to repository parameter spacing.
- Normalized `CG_FeederSelection` to repository parameter spacing.
- Normalized `CG_Text_PaintWithCursor` to repository parameter spacing.
- Preserved behavior: the feeder-image callback remains a null stub, selection
  still mirrors through cached `playerlistRED` / `playerlistBLUE` items, and the
  cursor-text wrapper still forwards through `CG_Text_PaintWithCursorExt`.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now locks the normalized callback
  signatures and checks the HLIL display-context assignments for the feeder and
  cursor-text slots.
- The scoreboard-selection guard also checks the retail `playerlistRED` /
  `playerlistBLUE` strings and the `-1` clear path in the `0x10028B10` block.

## Parity Estimate

- Before: display-context callback declaration/evidence parity for this seam was
  about 98%.
- After: about 98.5%.

This round was source-shape and evidence-lock work only; it intentionally did
not change runtime behavior.
