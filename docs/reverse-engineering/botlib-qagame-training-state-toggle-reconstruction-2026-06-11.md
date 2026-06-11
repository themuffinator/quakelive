# Botlib qagame training state toggle reconstruction - 2026-06-11

## Scope

This pass reconstructs `BotSetTrainingBotState` at
`qagamex86.dll:0x100245C0`, the qagame tutorial/training helper used by the
late teammate-follow and lead-teammate tutorial nodes.

The helper mutates the trainer bot's `gentity_t` flags and selected
`playerState_t` weapon/ammo fields so the scripted training bot can act as a
durable guide during tutorial flow and then unwind back toward normal state.

## Evidence

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/symbol-maps/qagame.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/game/g_local.h`
- `src/code/game/q_shared.h`
- `src/code/game/bg_public.h`
- `src/code/game/ai_main.c`
- `src/code/game/ai_main.h`
- `tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`

## Observed Retail Behavior

Binary Ninja HLIL for `0x100245C0` indexes the trainer entity through
`bs->client`, then writes:

- `gentity_t.flags |= 0x10010` on enable;
- `client->ps.ammo[WP_ROCKET_LAUNCHER] = 9999` on enable;
- `client->ps.stats[STAT_WEAPONS] |= 0x20` on enable;
- `gentity_t.flags |= 0x20800` on enable;
- `client->ps.stats[STAT_WEAPONS] |= 0x8000` on enable;
- `gentity_t.flags &= 0xFFFEFFEF`, `client->ps.ammo[WP_SHOTGUN] = 10`, and
  `gentity_t.flags &= 0xFFFDF7FF` on disable.

The named portions of the entity masks are `FL_GODMODE` and
`FL_NO_KNOCKBACK`. The remaining `0x00010000` and `0x00020000` entity flag bits
are preserved as local retail training masks because this pass did not find a
stable broader gameplay name for them. The extra weapon bit `0x00008000` is
also kept as a local retail training constant rather than being assigned to a
public weapon enum.

## Source Reconstruction

`src/code/game/ai_main.c` now includes:

- `BOT_TRAINING_ENTITY_GODMODE_FLAGS`;
- `BOT_TRAINING_ENTITY_NO_KNOCKBACK_FLAGS`;
- `BOT_TRAINING_EXTRA_WEAPON_BIT`;
- `BotSetTrainingBotState(bot_state_t *bs, qboolean enabled)`;
- enable-path writes for entity flags, rocket-launcher ammo, weapon bits, and
  the retail extra weapon bit;
- disable-path writes for clearing both entity flag groups and restoring
  shotgun ammo to `10`.

`src/code/game/ai_main.h` exposes the helper prototype.

## Follow-Up Closure

The dynamic-skill boundary retained by this pass was closed by
`botlib-qagame-dynamic-skill-reconstruction-2026-06-11.md`, which adds the
retail history slab to `bot_state_t` and reconstructs
`BotAppendDynamicSkillSample` plus `BotUpdateDynamicSkill`.

## Verification

```text
python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py -q --tb=short
3 passed in 0.18s

python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_instagib_target_goal_parity.py tests/test_botlib_qagame_ai_dmnet_goal_parity.py -q --tb=short
13 passed in 0.37s

$tests = Get-ChildItem tests -Filter 'test_botlib_*.py' | ForEach-Object { $_.FullName }
python -m pytest $tests -q --tb=short
201 passed in 5.48s

git diff --check -- src/code/game/ai_main.c src/code/game/ai_main.h src/code/game/ai_dmq3.c src/code/game/ai_dmq3.h references/symbol-maps/qagame.json tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py docs/reverse-engineering/botlib-qagame-training-state-toggle-reconstruction-2026-06-11.md docs/reverse-engineering/botlib-qagame-ai-main-lifecycle-training-mapping-2026-06-06.md docs/reverse-engineering/botlib-qagame-beyondreality-travel-flags-reconstruction-2026-06-11.md docs/reverse-engineering/botlib-qagame-entity-bounds-gap-reconstruction-2026-06-11.md docs/reverse-engineering/botlib-qagame-training-leaf-reconstruction-2026-06-11.md IMPLEMENTATION_PLAN.md
clean apart from existing LF-to-CRLF working-copy warnings
```

No runtime launch was needed. This was static reverse-engineering and source
reconstruction against the committed HLIL, Ghidra, symbol-map, and source
layout evidence. Native `Debug|x86` compile validation was not available in
this shell because neither `msbuild` nor `cl` is on `PATH`.

## Parity Estimate

- Focused `BotSetTrainingBotState` source reconstruction confidence:
  **before 0% -> after 93%**.
- Focused ai_main training-helper source coverage:
  **before 93% -> after 95%**.
- Overall botlib plus adjacent qagame AI execution wiring confidence:
  **before 99.2% -> after 99.3%**.
