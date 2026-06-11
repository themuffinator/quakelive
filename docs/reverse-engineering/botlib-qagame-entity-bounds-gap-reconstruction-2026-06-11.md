# Botlib qagame entity bounds gap reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame training/tutorial helper
`BotEntityBoundsGap` at `qagamex86.dll:0x100243D0`. The helper sits in the
botlib-adjacent `ai_main.c` lifecycle/training island and is reused by late
tutorial nodes as a proximity predicate before stopping, talking, or continuing
to guide the local player.

## Evidence

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/symbol-maps/qagame.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/game/be_aas.h`
- `src/code/game/ai_main.c`
- `src/code/game/ai_main.h`
- `tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`

## Observed Retail Behavior

The Binary Ninja HLIL for `0x100243D0` shows two direct
`trap_AAS_EntityInfo` calls through the qagame botlib import table, first for
the first entity argument and then for the second. The accessed local offsets
line up with `aas_entityinfo_t.origin`, `mins`, and `maxs` in
`src/code/game/be_aas.h`.

The helper computes absolute entity bounds from `origin + mins` and
`origin + maxs`, then returns a positive separating gap when the two boxes are
apart. The HLIL also preserves a `4.0` horizontal cushion before the X/Y gap
predicate succeeds. A zero return means the boxes overlap or are close enough
for the tutorial proximity check.

## Source Reconstruction

`src/code/game/ai_main.c` now includes:

- `BotEntityBoundsGap(int ent1, int ent2)`;
- two named `BotEntityInfo` snapshots;
- absolute mins/maxs construction for both entity boxes;
- vertical-first separation, horizontal checks with the observed `4.0f`
  cushion, and a final `0.0f` overlap return.

`src/code/game/ai_main.h` now exposes the helper prototype for adjacent AI code.

## Follow-Up Closure

The dynamic-skill boundary retained by this pass was closed by
`botlib-qagame-dynamic-skill-reconstruction-2026-06-11.md`, which adds the
retail history slab to `bot_state_t` and reconstructs
`BotAppendDynamicSkillSample` plus `BotUpdateDynamicSkill`.

## Verification

```text
python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py -q --tb=short
3 passed in 0.19s

python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_instagib_target_goal_parity.py tests/test_botlib_qagame_ai_dmnet_goal_parity.py tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py -q --tb=short
13 passed in 0.29s

$tests = Get-ChildItem tests -Filter 'test_botlib_*.py' | ForEach-Object { $_.FullName }; python -m pytest $tests -q --tb=short
201 passed in 8.47s
```

No runtime launch was needed. This was static reverse-engineering and source
reconstruction against the committed HLIL, Ghidra, symbol-map, and source
layout evidence.

## Parity Estimate

- Focused `BotEntityBoundsGap` source reconstruction confidence:
  **before 0% -> after 88%**.
- Focused ai_main training-helper source coverage:
  **before 89% -> after 91%**.
- Overall botlib plus adjacent qagame AI execution wiring confidence:
  **before 99.0% -> after 99.1%**.
