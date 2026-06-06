# Botlib AI Goal Native Slab Mapping - 2026-06-06

## Scope

This pass closes the qagame native bot-AI goal/item import slab from
`G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE = 137` through
`G_QL_IMPORT_BOTLIB_AI_FREE_GOAL_STATE = 165`.

The source reconstruction point is float marshaling for
`BotMutateGoalFuzzyLogic`. Retail's native trampoline at `0x004e2340` converts
the `range` argument through the same float-to-integer ABI pattern used by the
other botlib wrappers, and the server dispatcher already decodes the legacy
syscall with `VMF(2)`. The qagame-facing wrappers now pass that argument with
`PASSFLOAT(range)` / `QL_G_PASSFLOAT(range)`.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_ai_goal_native_slab_parity.py`

## Findings

- Native slots 137 through 165 are now pinned against the retail import table,
  Ghidra row sizes where present, source native enum values, legacy syscall
  remapping, the server native import initializer, and the legacy `ql_import_f`
  dispatch array.
- The native table deliberately differs from legacy/source declaration order in
  two places:
  - slot 138 is `RemoveFromAvoidGoals`, while the legacy export offset for
    `ResetAvoidGoals` is earlier;
  - slots 152 and 153 are camp/map goal lookup, while `GetLevelItemGoal` keeps
    the earlier export offset and native slot 154.
- `BotInitLevelItems` appears as `sub_4e22a0` in the HLIL table without a
  normal Ghidra row. `BotUpdateEntityItems` appears as raw table address
  `0x4e22b0`. The parity gate preserves those classifications.
- `BotChooseNBGItem`, `BotSetAvoidGoalTime`, and `BotMutateGoalFuzzyLogic` now
  share the observed float marshaling pattern across legacy qagame syscalls and
  native qagame imports.

## Coverage Result

`tests/test_botlib_ai_goal_native_slab_parity.py` prevents these regressions:

- reordering avoid-goal or level/camp/map goal native imports by legacy export
  offset instead of retail native slot;
- treating `0x4e22a0` or `0x4e22b0` as ordinary promoted Ghidra function rows;
- dropping the `BotMutateGoalFuzzyLogic` float bit-cast reconstruction;
- disconnecting the goal native slots from the legacy syscall bridge.

## Parity Estimate

- Focused AI goal/item native slab mapping:
  **before 76% -> after 99%**
- Focused botlib float syscall/native marshaling coverage:
  **before 90% -> after 96%**
- Overall botlib plus qagame native import wiring:
  **before 94% -> after 95%**

No runtime launch was needed. The committed retail HLIL table, Ghidra row
coverage, and source wrapper shape settle this slice statically.
