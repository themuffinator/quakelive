# Botlib Qagame Item Delay Time Reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame-side training item-delay helper and its
frame-tail wiring:

- `qagamex86.dll:0x10024640`, promoted as `BotUpdateItemDelayTime`.

## Retail Evidence

- Binary Ninja HLIL identifies `sub_10024640` with the promoted signature
  `void BotUpdateItemDelayTime(int time)`.
- `BotAIStartFrame` calls the helper at `0x10023BD3`, immediately before
  `BotUpdateDynamicSkill(time)` and `BotUpdateTrainingState()`.
- The helper no-ops unless the retail training cvar is active, reads
  `g_spSkill`, resets `bot_itemDelayTime` to `0`, and only applies staged
  item delays when skill is above `3.0`.
- The staged elapsed-time thresholds are `60`, `120`, `180`, and `240`
  seconds, mapping to the visible training delay values `10`, `15`, `20`, and
  `25`.

## Reconstruction

- Changed `BotUpdateItemDelayTime` in `src/code/game/ai_main.c` from a no-arg
  source shim to the retail time-input form `BotUpdateItemDelayTime(int time)`.
- Moved the call out of `BotUpdateTrainingState` and into `BotAIStartFrame`
  before `BotUpdateDynamicSkill(time)`, matching the HLIL frame-tail order.
- Switched elapsed-seconds calculation from `level.time - level.startTime` to
  the explicit `time - level.startTime` input.
- Strengthened the lifecycle/training and game-helper parity gates around
  the new signature, frame-tail order, HLIL thresholds, and source anchors.

## Confidence

High for function identity, call order, `g_training` guard, `g_spSkill` gate,
elapsed-time source, threshold ladder, cvar key, and staged delay values. The
larger `BotUpdateTrainingState` tutorial tail still has broader retail-only
state transitions and remains a separate reconstruction target.

## Validation

- `python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_game_helper_seam_parity.py -q --tb=short`
  - `36 passed in 0.83s`
