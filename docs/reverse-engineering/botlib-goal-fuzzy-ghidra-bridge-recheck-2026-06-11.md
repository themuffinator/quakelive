# Botlib Goal/Fuzzy Ghidra Bridge Recheck - 2026-06-11

## Scope

This recheck covers the `0x0049C6C0..0x0049F920` botlib goal band in
`quakelive_steam.exe`: genetic parent/child selection, goal fuzzy-logic
mutation helpers, item config and level-item management, avoid-goal helpers,
goal-stack helpers, LTG/NBG selection, item weights, and goal-state lifecycle.

## Observed Facts

- Binary Ninja HLIL already supports stable `sub_*` owner names across the
  band, and the existing source tests pin representative body shape and
  wiring.
- Ghidra `functions.csv` has committed function rows for all 39 selected
  owners, including sizes from `FUN_0049c6c0,0049c6c0,321,0,unknown`
  through `FUN_0049f920,0049f920,153,0,unknown`.
- The alias ledger previously had only the Binary Ninja `sub_*` names for this
  band.

## Reconstruction Decision

Promote the matching Ghidra `FUN_*` aliases for every committed row in the
goal/fuzzy/item band. No source rewrite is justified: the current source and
wiring are already covered by the goal-item, genetic selection, and weight
runtime tests.

## Test Coverage

`tests/test_botlib_goal_item_parity.py` now requires every selected address to
have both:

- `sub_<address> -> source owner`, and
- `FUN_00<address> -> same source owner`,

while also checking the committed Ghidra row size. The surrounding tests
continue to pin source behavior and wiring through `Init_AI_Export`, qagame
syscalls, server VM dispatch, and `ql_game_imports.inc`.

## Confidence

High for static ownership, source shape, and game/server wiring. Remaining
uncertainty is live map-specific AAS item behavior and tactical weight quality,
not the mapping or exported API surface.

## Parity Estimate

- Focused goal/fuzzy/item Ghidra/Binary Ninja alias bridge: `58% -> 98%`.
- Focused goal-item source/wiring confidence: `95% -> 97%`.
- Overall botlib static mapping confidence: `89.5% -> 89.7%`.
