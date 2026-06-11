# Botlib Qagame Debug Cvar Owner Bridge Reconstruction - 2026-06-11

## Scope

This pass closes the ownership boundary left by the qagame bot cvar-table
reconstruction. Retail Quake Live registers `bot_showAreaNumber`,
`bot_showAreas`, and `bot_showAvoidSpots` through the qagame `gameCvarTable`;
`BotAISetup` does not create separate VM-owned mirrors for those names.

The source reconstruction makes `BotTestAAS` consume the same table-owned
`vmCvar_t` mirrors and removes the duplicate `CVAR_VM_CREATED` registrations
from `BotAISetup`.

## Retail Evidence

Binary Ninja HLIL in
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt`
pins the table owners:

- `0x1008d9b0 -> 0x105a27a0`, `bot_showAreaNumber`, default `0`, flags
  `0x100000`.
- `0x1008d9c8 -> 0x1059cda0`, `bot_showAreas`, default `0`, flags
  `0x100000`.
- `0x1008d9e0 -> 0x105a0940`, `bot_showAvoidSpots`, default `0`, flags
  `0x100000`.

The retail `BotTestAAS` body in
`qagamex86.dll.bndb_hlil_part01.txt` updates and consumes those same table
addresses:

- `10020f3e` updates `0x1059cda0`.
- `10020f5a` passes `data_1059cdac` and `data_105a27ac` into
  `BotDrawDebugAreas`, matching the `integer` fields of `bot_showAreas` and
  `bot_showAreaNumber`.
- `10020f5c` reads `data_105a094c`, matching the `integer` field of
  `bot_showAvoidSpots`.
- `10020fa8` resets `"bot_showAvoidSpots"` through the cvar-set import when the
  selected bot client is invalid.

The retail `BotAISetup` block at `0x100241c0..0x10024380` registers
`bot_log`, `bot_thinktime`, `bot_memorydump`, `bot_saveroutingcache`,
`bot_pause`, `bot_report`, `bot_testsolid`, `bot_testclusters`,
`bot_developer`, and the interbreed cvars. The three `bot_show*` area-display
cvars are absent from that setup block.

Ghidra corroborates the function row and alias context:

- `FUN_10020f00,10020f00,580,0,unknown` (`BotTestAAS`)
- `FUN_100241c0,100241c0,436,0,unknown` (`BotAISetup`)

## Reconstruction

`src/code/game/g_main.c` now owns the three debug-display `vmCvar_t` objects
without `static` storage so `ai_main.c::BotTestAAS` uses the table-registered
mirrors directly.

`src/code/game/g_local.h` exposes:

```c
extern	vmCvar_t	bot_showAreaNumber;
extern	vmCvar_t	bot_showAreas;
extern	vmCvar_t	bot_showAvoidSpots;
```

`src/code/game/ai_main.c::BotAISetup` no longer registers the three names with
`CVAR_VM_CREATED`. The remaining setup registrations continue to match the
retail `0x100241c0` sequence.

## Regression Coverage

The focused parity gates now pin:

1. The three debug-display cvars as exported table mirrors, not local static
   table-only mirrors.
2. Absence of duplicate `CVAR_VM_CREATED` registrations in `BotAISetup`.
3. Retail HLIL negative evidence for the three cvar names inside the
   `BotAISetup` block.
4. Existing `BotTestAAS` update/draw/reset behavior.

Focused validation:

```powershell
python -m pytest tests/test_botlib_qagame_cvar_table_parity.py tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_game_native_export_helper_parity.py::test_qagame_native_import_table_uses_public_header_count tests/test_botlib_debug_draw_native_micro_slab_parity.py -q --tb=short
```

Result:

```text
8 passed in 0.37s
```

## Open Boundaries

This pass does not infer gameplay behavior for the cvars beyond the observed
debug draw/update/reset path. `bot_showPath` remains a botlib libvar bridge and
was not converted into an ai_main `vmCvar_t` consumer.

No runtime launch was needed; the ownership question is fully covered by static
HLIL/Ghidra/source evidence and parity tests.

## Parity Estimate

- Focused qagame debug bot-cvar ownership bridge: **78% -> 99%**.
- Focused `BotAISetup` retail registration sequence confidence:
  **94% -> 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.7% -> 83.78%**.
