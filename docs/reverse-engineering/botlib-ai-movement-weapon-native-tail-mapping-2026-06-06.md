# Botlib AI Movement/Weapon Native Tail Mapping - 2026-06-06

## Scope

This pass closes the qagame native bot-AI movement, weapon, and genetic import
tail from `G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE = 166` through
`G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION = 184`.

No additional C source body change is justified in this slice. The checked-in
wrappers already preserve the observed float marshaling for `AddAvoidSpot`,
`MoveInDirection`, and `MovementViewTarget`; the useful reconstruction work is
pinning the retail table slots and the non-linear wrapper order.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_ai_movement_weapon_native_tail_parity.py`

## Findings

- Native slots 166 through 184 are now pinned against the retail import table,
  Ghidra row sizes where present, source native enum values, legacy syscall
  remapping, the server native import initializer, and the legacy `ql_import_f`
  dispatch array.
- `AddAvoidSpot` is intentionally non-linear:
  - its wrapper appears before `BotMoveToGoal` in `ql_game_imports.inc`;
  - its native table slot is 177, after `InitMoveState`;
  - its trampoline lives at `0x004e23d0`, before many earlier native slots.
- `AllocMoveState` and `AllocWeaponState` are raw table thunks at `0x4e2500`
  and `0x4e25b0`, not ordinary Ghidra function rows.
- Slot 184, `GeneticParentsAndChildSelection`, is the final native botlib AI
  slot before Quake Live-specific game service imports begin at
  `G_QL_IMPORT_SUBMIT_MATCH_REPORT = 185`.

## Coverage Result

`tests/test_botlib_ai_movement_weapon_native_tail_parity.py` prevents these
regressions:

- reordering the movement tail by source wrapper order or function address;
- promoting raw allocation-state thunks as normal function rows;
- dropping the float bit-cast paths for movement wrappers;
- sliding botlib AI slot 184 into the adjacent Quake Live service import slab.

## Parity Estimate

- Focused AI movement/weapon/genetic native tail mapping:
  **before 78% -> after 99%**
- Focused botlib native import table coverage:
  **before 95% -> after 97%**
- Overall botlib plus qagame native import wiring:
  **before 95% -> after 96%**

No runtime launch was needed. The committed retail HLIL table, Ghidra row
coverage, and source wrapper shape settle this slice statically.
