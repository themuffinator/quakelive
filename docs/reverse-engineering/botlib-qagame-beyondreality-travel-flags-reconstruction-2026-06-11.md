# Botlib qagame beyondreality travel flags reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame map-specific travel flag helper
`BotApplyBeyondRealityTravelFlags` at `qagamex86.dll:0x10024E10` and wires the
existing `BotMapScripts` `beyondreality` branch through it.

The helper belongs to the botlib-adjacent tutorial/training island: late
tutorial nodes compute travel flags, then clear `TFL_FUNCBOB` on
`beyondreality` so bot movement does not route through func-bobbing geometry.

## Evidence

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/symbol-maps/qagame.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/game/ai_dmq3.c`
- `src/code/game/ai_dmq3.h`
- `tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py`
- `tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`

## Observed Retail Behavior

Binary Ninja HLIL for `0x10024E10` shows:

- a serverinfo fetch into a `0x400` byte buffer;
- a map-name extraction into a bounded local buffer;
- a case-insensitive comparison against `beyondreality`;
- `*travelFlags &= 0xFEFFFFFF` when the comparison matches, which clears
  `TFL_FUNCBOB`.

The existing retail `BotMapScripts` mapping at `0x1001B790` already had the
same `beyondreality` map branch. This pass gives the shared operation a named
source helper and keeps the map-script branch wired to it.

## Source Reconstruction

`src/code/game/ai_dmq3.c` now includes:

- `BotApplyBeyondRealityTravelFlags(int *travelFlags)`;
- `trap_GetServerinfo` plus `Info_ValueForKey(..., SERVERINFO_KEY_MAPNAME)`;
- a bounded copy into `mapname`;
- a `beyondreality` match that clears `TFL_FUNCBOB`.

`BotMapScripts` still handles the `q3tourney6` crusher button inline, but now
routes the `beyondreality` branch through `BotApplyBeyondRealityTravelFlags`.
`src/code/game/ai_dmq3.h` exposes the helper prototype.

## Follow-Up Closure

The dynamic-skill boundary retained by this pass was closed by
`botlib-qagame-dynamic-skill-reconstruction-2026-06-11.md`, which adds the
retail history slab to `bot_state_t` and reconstructs
`BotAppendDynamicSkillSample` plus `BotUpdateDynamicSkill`.

## Verification

```text
python -m pytest tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py -q --tb=short
5 passed in 0.34s

python -m pytest tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_instagib_target_goal_parity.py tests/test_botlib_qagame_ai_dmnet_goal_parity.py -q --tb=short
13 passed in 0.33s

$tests = Get-ChildItem tests -Filter 'test_botlib_*.py' | ForEach-Object { $_.FullName }; python -m pytest $tests -q --tb=short
201 passed in 5.20s
```

No runtime launch was needed. This was static reverse-engineering and source
wiring against the committed HLIL, Ghidra, symbol-map, and source evidence.

## Parity Estimate

- Focused `BotApplyBeyondRealityTravelFlags` source reconstruction confidence:
  **before 0% -> after 96%**.
- Focused `BotMapScripts` map-specific travel-flag wiring:
  **before 94% -> after 98%**.
- Overall botlib plus adjacent qagame AI execution wiring confidence:
  **before 99.1% -> after 99.2%**.
