# Botlib Offscreen Enemy Reconstruction - 2026-06-11

## Scope

This pass reconstructs the Quake Live qagame enemy-acquisition side path that
accepts an unseen client after `BotFindEnemy` fails the direct
`BotEntityVisible` test. The owning retail binary is `qagamex86.dll`.

## Retail Evidence

- `BotFindEnemy` at `0x10019290` calls `sub_10020c10` at `0x10019729` only
  after `BotEntityVisible` returns non-positive.
- `sub_10020c10` at `0x10020C10` checks that `bs->enemy == -1`, rejects
  retreat decisions through `BotWantsToRetreat`, requires a positive
  `BotWantsToChase`, samples the top and second botlib goal stack entries, and
  requires skill at least `4.0`.
- The native import slab offsets used inside the helper are `+0x248` and
  `+0x24c`, which correspond to slots `146` and `147`:
  `trap_BotGetTopGoal` and `trap_BotGetSecondGoal`.
- `BotCheckEvents` at `0x1001E4C0` resets the retail `bs+0x2488` mask for a
  new entity event and sets a client bit for local movement, fall, jump, water,
  item pickup, no-ammo, weapon-change, fire, and taunt events.
- `BotFindEnemy` stores the helper result in the retail marker at `bs+0x248C`.
  `BotPublishDebugInfoString` later publishes the same marker through the final
  `eh\\%i\\` selected-bot debug field.

## Reconstruction

- Added `bot_state_t::heardClientMask` and `bot_state_t::enemyFromGoalStack`.
- Added `BotRememberHeardClient` and wired it from `BotCheckEvents` for the
  retail heard-event cases.
- Added `BotGoalBlocksOffscreenEnemyCandidate`,
  `BotHasBlockingOffscreenGoal`, and `BotAcceptOffscreenEnemyCandidate`.
- Updated `BotFindEnemy` to call the helper only after failed visibility and
  to preserve the resulting marker on accepted enemies.
- Updated `BotWantsToChase` with the retail invalid-enemy guard needed when
  the helper probes chase intent before `bs->enemy` is assigned.
- Updated `BotPublishDebugInfoString` to publish `eh` from the stored marker.

## Confidence

High for the helper placement, state fields, import-slot identity, skill gate,
retreat/chase checks, heard-client mask, and telemetry marker. Medium for the
exact goal entity classifier because the decompiler exposes it through local
type/model tests; the source reconstruction preserves the observed top/second
goal-stack gate and blocks the same broad entity classes while leaving the
constant isolated as `BOT_OFFSCREEN_GOAL_MIN_MODEL`.

## Validation

- `tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py`
- `tests/test_botlib_qagame_ai_dmq3_visibility_parity.py`
- `tests/test_botlib_qagame_ai_dmq3_support_parity.py`
- `tests/test_botlib_qagame_ai_dmq3_activate_obstacle_parity.py`
- `tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`
