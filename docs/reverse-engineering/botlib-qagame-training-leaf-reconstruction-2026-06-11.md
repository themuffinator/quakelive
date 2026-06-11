# Botlib qagame training leaf reconstruction - 2026-06-11

## Scope

This pass reconstructs two small qagame botlib-adjacent helper leaves whose
retail Quake Live behavior is clear in the committed Binary Ninja HLIL and
Ghidra corpora:

- `BotSetLeadTeamGoal` at `qagamex86.dll:0x1000F7F0`, owned by the
  `ai_dmnet.c` tutorial/lead-teammate tail.
- `BotSetIdealViewAnglesToPoint` at `qagamex86.dll:0x10024530`, owned by the
  `ai_main.c` lifecycle/training helper island.

The broader tutorial-node body remains mapped-only because its retail field
writes still need a dedicated node-level pass.

Follow-up note: `BotEntityBoundsGap` was reconstructed afterward in
`docs/reverse-engineering/botlib-qagame-entity-bounds-gap-reconstruction-2026-06-11.md`.
Follow-up note: `BotAppendDynamicSkillSample` and `BotUpdateDynamicSkill` were
reconstructed afterward in
`docs/reverse-engineering/botlib-qagame-dynamic-skill-reconstruction-2026-06-11.md`.

## Evidence

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/symbol-maps/qagame.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/game/ai_dmnet.c`
- `src/code/game/ai_dmnet.h`
- `src/code/game/ai_main.c`
- `src/code/game/ai_main.h`
- `tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py`
- `tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`

## Observed Retail Behavior

`BotSetLeadTeamGoal`:

- copies the bot origin at offsets `0x130c..0x1314` to the lead-team goal
  origin at `0x24b0..0x24b8`;
- copies the bot AAS area number at `0x1334` to the lead-team goal area at
  `0x24bc`;
- writes goal mins `(-16, -16, -24)` and maxs `(16, 16, 32)`;
- does not write `entitynum`, `flags`, `number`, or item metadata in this leaf.

`BotSetIdealViewAnglesToPoint`:

- subtracts `bs->origin` from the target point;
- calls the angle conversion helper with that direction and
  `bs->ideal_viewangles`;
- halves `bs->ideal_viewangles[ROLL]` after the conversion.

## Source Reconstruction

`src/code/game/ai_dmnet.c` now includes:

- `BotSetLeadTeamGoal(bot_state_t *bs)`, using `VectorCopy` and `VectorSet`
  against the existing `bs->lead_teamgoal` field.
- A public prototype in `src/code/game/ai_dmnet.h`.

`src/code/game/ai_main.c` now includes:

- `BotSetIdealViewAnglesToPoint(bot_state_t *bs, vec3_t target)`, using the
  same `VectorSubtract` and `vectoangles` pattern already present in nearby
  qagame AI code.
- A public prototype in `src/code/game/ai_main.h`.

## Follow-Up Closure

The dynamic-skill boundary retained by this pass was closed by
`botlib-qagame-dynamic-skill-reconstruction-2026-06-11.md`, which adds the
retail history slab to `bot_state_t` and reconstructs
`BotAppendDynamicSkillSample` plus `BotUpdateDynamicSkill`.

## Verification

```text
python -m pytest tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py -q --tb=short
6 passed in 0.38s

python -m pytest tests/test_botlib_qagame_ai_dmnet_goal_parity.py tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_instagib_target_goal_parity.py -q --tb=short
13 passed in 0.28s

$tests = Get-ChildItem tests -Filter 'test_botlib_*.py' | ForEach-Object { $_.FullName }; python -m pytest $tests -q --tb=short
201 passed in 8.34s
```

No game launch was needed. This was a static reverse-engineering and source
reconstruction pass using the committed HLIL, Ghidra, symbol-map, and source
evidence.

## Parity Estimate

- Focused `BotSetLeadTeamGoal` source reconstruction confidence:
  **before 0% -> after 96%**.
- Focused `BotSetIdealViewAnglesToPoint` source reconstruction confidence:
  **before 0% -> after 97%**.
- Focused tutorial/training leaf alias and source-body guard coverage:
  **before 94% -> after 98%**.
- Overall botlib plus adjacent qagame AI execution wiring confidence:
  **before 98.9% -> after 99.0%**.
