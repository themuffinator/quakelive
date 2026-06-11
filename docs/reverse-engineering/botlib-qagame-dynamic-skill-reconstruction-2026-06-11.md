# Botlib qagame dynamic-skill reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame training dynamic-skill island:

- `BotAppendDynamicSkillSample` at `qagamex86.dll:0x10024700`;
- `BotUpdateDynamicSkill` at `qagamex86.dll:0x100247C0`;
- the retail `BotAIStartFrame` call from the lifecycle tail into the
  dynamic-skill updater before broader training-state maintenance.

The retail code adjusts the trainer bot skill from the score delta between the
local player and the bot, reloads character/item/weapon weights when the skill
changes, refreshes bot userinfo, and stores a bounded history of adjustment
samples.

## Evidence

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/symbol-maps/qagame.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/game/ai_main.c`
- `src/code/game/ai_main.h`
- `src/code/game/g_local.h`
- `src/code/game/g_team.c`
- `tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`

## Observed Retail Behavior

`BotAppendDynamicSkillSample` indexes the active bot through the bot-state
array, maintains a capped `32`-entry triplet history, shifts existing entries
when the cap is reached, appends the newest score delta, skill, and elapsed
seconds, and increments the sample count while below the cap.

`BotUpdateDynamicSkill` is gated by:

- `bot_dynamicSkill`;
- `cl_running`;
- no active warmup;
- a five-second elapsed-level update throttle;
- a valid local client;
- recent local-client activity.

For each active bot, the helper:

- compares local-player score against bot score;
- tracks score-delta changes and the elapsed second for the last change;
- starts a negative skill nudge when the local player trails by more than one
  point;
- starts a positive skill nudge when the local player leads by more than two
  points;
- cancels or advances pending nudges based on later score-delta movement;
- cancels stalled nudges after `30` seconds;
- clamps the resulting skill to `[1.0, 5.0]`;
- reloads the bot character, item weights, and weapon weights when the skill or
  walker state changes;
- refreshes userinfo keys `skill` and `handicap`;
- toggles predictable item pickup through the adjacent training helper;
- calls `ClientUserinfoChanged`;
- mirrors the adjusted skill back to `g_spSkill`.

## Source Reconstruction

`src/code/game/ai_main.h` now carries the retail dynamic-skill state slab:

- `BOT_DYNAMIC_SKILL_MAX_SAMPLES`;
- `bot_dynamic_skill_sample_t`;
- pending adjustment, reference score delta, last score delta, last score time,
  history samples, and sample count fields in `bot_state_t`.

`src/code/game/ai_main.c` now carries:

- retail threshold constants for five-second updates, `30`-second stalls,
  negative and positive score-delta thresholds, and the `0.083333336f` skill
  adjustment step;
- `BotAppendDynamicSkillSample`;
- `BotRefreshDynamicSkillCharacter`, a source-local helper that collects the
  character/userinfo refresh side effects from the retail update body;
- `BotUpdateDynamicSkill`;
- the `BotAIStartFrame` call to `BotUpdateDynamicSkill( time )` before
  `BotUpdateTrainingState()`.

## Boundaries Retained

This pass reconstructs the dynamic-skill island but keeps these conservative
boundaries:

- the sample ring is represented with named source fields rather than trying to
  force retail byte offsets into the GPL `bot_state_t` layout;
- score reads go through `G_GetClientScore`, the current source abstraction for
  the same `PERS_SCORE` value observed in retail;
- the character reload error path returns early after the same failed-load
  report shape, but no runtime launch was performed.

## Verification

```text
python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py -q --tb=short
3 passed in 0.09s

python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_instagib_target_goal_parity.py tests/test_botlib_qagame_ai_dmnet_goal_parity.py -q --tb=short
13 passed in 0.65s

$tests = Get-ChildItem tests -Filter 'test_botlib_*.py' | ForEach-Object { $_.FullName }
python -m pytest $tests -q --tb=short
201 passed in 8.09s

git diff --check -- src/code/game/ai_main.c src/code/game/ai_main.h references/symbol-maps/qagame.json tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py docs/reverse-engineering/botlib-qagame-dynamic-skill-reconstruction-2026-06-11.md docs/reverse-engineering/botlib-qagame-ai-main-lifecycle-training-mapping-2026-06-06.md docs/reverse-engineering/botlib-qagame-training-state-toggle-reconstruction-2026-06-11.md docs/reverse-engineering/botlib-qagame-entity-bounds-gap-reconstruction-2026-06-11.md docs/reverse-engineering/botlib-qagame-beyondreality-travel-flags-reconstruction-2026-06-11.md docs/reverse-engineering/botlib-qagame-training-leaf-reconstruction-2026-06-11.md IMPLEMENTATION_PLAN.md
clean apart from existing LF-to-CRLF working-copy warnings
```

No runtime launch was needed for this static reverse-engineering and source
reconstruction pass. Native `Debug|x86` compile validation was not available in
this shell because neither `msbuild` nor `cl` is on `PATH`.

## Parity Estimate

- Focused `BotAppendDynamicSkillSample` source reconstruction confidence:
  **before 0% -> after 94%**.
- Focused `BotUpdateDynamicSkill` source reconstruction confidence:
  **before 0% -> after 86%**.
- Focused ai_main training/dynamic-skill source coverage:
  **before 95% -> after 98%**.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 99.3% -> after 99.4%**.
