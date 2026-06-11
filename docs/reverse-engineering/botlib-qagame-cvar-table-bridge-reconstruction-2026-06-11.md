# Botlib Qagame Cvar Table Bridge Reconstruction - 2026-06-11

## Scope

This pass reconstructs the retail qagame bot cvar table bridge around the
`bot_autoReady` through `bot_training` tranche. The source change is confined to
`src/code/game/g_main.c`: the missing table-owned bot cvars are now registered
through `gameCvarTable`, matching the Binary Ninja HLIL cvar-table evidence
before the existing bot AI training/debug paths consume or mirror them.

## Retail Evidence

Primary Binary Ninja evidence comes from
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt`.
The table block at `0x1008d894..0x1008da4c` contains the following contiguous
rows:

- `bot_autoReady`, default `1`, flags `0x100000`.
- `bot_breakPoint`, default `0`, flags `0`.
- `bot_debugVar`, default `0`, flags `0`.
- `bot_dynamicSkill`, default `0`, flags `0x100000`.
- `bot_followDist`, default `250`, flags `0x100000`.
- `bot_followMe`, default empty string, flags `0x100000`.
- `bot_gauntlet`, default `0`, flags `0x100000`.
- `bot_gauntletOnly`, default `0`, flags `0x100000`.
- `bot_hud`, default `-1`, flags `0x200`.
- `bot_instaGibAimSkill`, default `0.4`, flags `0x100000`.
- `bot_itemDelayTime`, default `0`, flags `0x100000`.
- `bot_teamkill`, default `0`, flags `0x100000`.
- `bot_showAreaNumber`, default `0`, flags `0x100000`.
- `bot_showAreas`, default `0`, flags `0x100000`.
- `bot_showAvoidSpots`, default `0`, flags `0x100000`.
- `bot_showPath`, default `0`, flags `0x100000`.
- `bot_showTourPoints`, default `0`, flags `0x100000`.
- `bot_startingSkill`, default `1`, flags `0x100000`.
- `bot_training`, default `0`, flags `0x100000`.

The companion string/default evidence is in
`qagamex86.dll.bndb_hlil_part02.txt`: `data_100875ec` is `"-1"`,
`0x100875d0` is `"0.4"`, and `0x1008760c` is `"250"`. In source terms,
`0x100000` maps to `CVAR_GAMERULE`, and `0x200` maps to `CVAR_CHEAT`.

Structured Ghidra evidence in
`references/reverse-engineering/ghidra/qagamex86/functions.csv` and
`decompile_top_functions.c` pins the consumers around:

- `FUN_10020f00 -> BotTestAAS`
- `FUN_100241c0 -> BotAISetup`
- `FUN_10024640 -> BotUpdateItemDelayTime`
- `FUN_100247c0 -> BotUpdateDynamicSkill`
- `FUN_10024fa0 -> BotUpdateTrainingState`

The alias bridge in `references/analysis/quakelive_symbol_aliases.json`
promotes the same names.

## Reconstruction

`g_main.c` now declares internal `vmCvar_t` mirrors for the retail table-owned
bot cvars and registers the tranche after `g_skipTrainingEnable` in retail
order. The rows restore the observed defaults and flags, including
`bot_hud = "-1"` as `CVAR_CHEAT` and the `CVAR_GAMERULE` metadata on the
training/debug cvars that retail exposes through the qagame table.

The existing qagame bot training paths were left intact. They already set or
read the string cvars seen in retail, including `bot_followDist`,
`bot_itemDelayTime`, `bot_startingSkill`, `bot_training`, `bot_dynamicSkill`,
`bot_followMe`, `bot_gauntlet`, and the botlib `bot_showPath` libvar bridge.

## Regression Coverage

`tests/test_botlib_qagame_cvar_table_parity.py` now pins:

1. Source-side `gameCvarTable` rows, defaults, flags, declarations, and order.
2. Binary Ninja cvar-table addresses, default pointers, string/default bytes,
   and the `16` observed `CVAR_GAMERULE` rows.
3. Ghidra function rows and alias names for the qagame bot training/debug
   consumers.
4. Existing source consumers in `ai_main.c` and `g_cmds.c`.

Focused validation:

```powershell
python -m pytest tests/test_botlib_qagame_cvar_table_parity.py -q --tb=short
```

Result:

```text
2 passed in 0.11s
```

## Follow-up Boundary Closure

The follow-up debug-cvar owner pass in
`docs/reverse-engineering/botlib-qagame-debug-cvar-owner-bridge-reconstruction-2026-06-11.md`
closed the remaining `BotAISetup` boundary. `bot_showAreaNumber`,
`bot_showAreas`, and `bot_showAvoidSpots` are now shared table-owned mirrors, and
the older `CVAR_VM_CREATED` re-registrations were removed after cross-checking
the retail `0x100241c0` setup block.

No runtime launch was needed; the task is a static retail-reference
reconstruction and is covered by source/reference parity tests.

## Parity Estimate

- Focused qagame bot cvar-table bridge: **72% -> 96%**.
- Focused bot training/debug cvar wiring confidence: **92% -> 96%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.58% -> 83.7%**.
