# Botlib Debug Draw Native Micro-Slab Mapping - 2026-06-06

## Scope

This pass closes the two qagame native botlib debug draw imports:

- `G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS = 83`
- `G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS = 84`

No C source body change is justified in this slice. The source already models
these as direct native imports without legacy syscall IDs, and the server
native import slab already forwards them to the botlib AI export table.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/game/ai_main.c`
- `src/code/game/botlib.h`
- `src/code/server/sv_game.c`
- `src/code/botlib/be_interface.c`
- `src/code/botlib/be_ai_move.c`
- `tests/test_botlib_debug_draw_native_micro_slab_parity.py`

## Observed Facts

- The retail HLIL native import table places `sub_4e2680` at
  `data_56d0cc` and `sub_4e26a0` at `data_56d0d0`, directly between
  `sub_4e1980` (`AAS_PredictClientMovement`) and `sub_4e19d0`
  (`EA_Say`).
- Ghidra records `FUN_004e2680` as a 17-byte wrapper and `FUN_004e26a0` as
  an 18-byte wrapper.
- Binary Ninja HLIL shows `sub_4e2680` jumping through
  `data_13e1844 + 0x1e8` and `sub_4e26a0` jumping through
  `data_13e1844 + 0x1ec`.
- Source qagame uses `G_GetDirectImport` for both draw helpers instead of
  routing through `G_MapNativeImport`.
- Server native imports 83 and 84 are initialized to
  `QL_G_trap_BotDrawDebugAreas` and `QL_G_trap_BotDrawAvoidSpots`, which call
  `botlib_export->ai.BotDrawDebugAreas` and
  `botlib_export->ai.BotDrawAvoidSpots`.
- `BotTestAAS` updates the debug cvars, draws area polygons first, and then
  optionally draws avoid spots for the selected bot move state.

## Inference

The two draw helpers are engine-owned botlib debug affordances exposed to the
retail qagame through native slots 83 and 84. Their export offsets follow the
AI movement/weapon/genetic export tail (`0x1e4`, `0x1e8`, `0x1ec`), while
their native import table slots are inserted before the EA action slab. That
non-linear relationship is intentional retail layout, not a reason to reorder
either side of the source reconstruction.

Confidence: high. The slot numbers, table addresses, wrapper sizes, export
offsets, source direct-import shape, server bridge, qagame caller, and botlib
AI export bodies all agree.

Open questions: none for this micro-slab. The remaining botlib uncertainty is
in adjacent export-body behavior, not in the qagame native import wiring for
these two helpers.

## Coverage Result

`tests/test_botlib_debug_draw_native_micro_slab_parity.py` prevents these
regressions:

- treating slots 83 and 84 as legacy syscall-compatible imports;
- reordering them around the AAS tail or EA action slab;
- losing the unusual export offset placement after the AI genetic slot;
- bypassing the server `botlib_export->ai` bridge;
- drifting the `BotTestAAS`, `BotDrawDebugAreas`, or `BotDrawAvoidSpots`
  source behavior away from the mapped retail shape.

## Parity Estimate

- Focused botlib debug draw native micro-slab mapping:
  **before 72% -> after 99%**
- Focused direct-only botlib native import classification:
  **before 90% -> after 97%**
- Overall botlib plus qagame native import wiring:
  **before 96% -> after 97%**

No runtime launch was needed. The committed retail HLIL table, Ghidra row
coverage, qagame source wrappers, server native import slab, and botlib export
bodies settle this slice statically.
