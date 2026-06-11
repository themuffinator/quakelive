# Botlib Qagame Attack-Move Wiring Recheck - 2026-06-11

## Scope

This pass tightens the qagame-side combat movement helper and botlib movement
import evidence:

- `qagamex86.dll:0x10018280`, promoted as `BotAttackMove`.
- Botlib movement imports used by the helper:
  `BOTLIB_AI_MOVE_TO_GOAL`, `BOTLIB_AI_MOVE_IN_DIRECTION`, and
  `BOTLIB_AI_CHARACTERISTIC_BFLOAT`.

## Retail Evidence

- Ghidra `functions.csv` reports `FUN_10018280` at `0x10018280`, size `1652`.
- The shared alias corpus maps both `FUN_10018280` and `sub_10018280` to
  `BotAttackMove`.
- Binary Ninja HLIL shows the attack-chase fast path zeroing the moveresult,
  reading attack/jumper/croucher characteristics, using the `0.2` low-skill
  early return, maintaining jump/crouch timers, using direct move-in-direction
  calls for low attack skill, and then entering the two-pass side-strafe
  fallback.
- HLIL stores the strafe flag and timer through the same offsets used by the
  reconstructed `bot_state_t` fields: `BFL_STRAFERIGHT` and
  `attackstrafe_time`.

## Mapping Result

- The source body in `src/code/game/ai_dmq3.c` already matches the retail
  behavior shape, so no behavior change was made.
- The focused parity test now pins the chase-goal `8x8x8` bounds, the
  `CHARACTERISTIC_ATTACK_SKILL`, `CHARACTERISTIC_JUMPER`, and
  `CHARACTERISTIC_CROUCHER` reads, the gauntlet zero-distance branch, the
  `IDEAL_ATTACKDIST` / `40` range branch, the `0.4 + (1 - attack_skill) * 0.2`
  cadence, the high-skill random jitter, the `0.935` strafe flip threshold, the
  `0.9` random back-step branch, and the movement-failure strafe reset.
- The botlib import gate remains tied from qagame syscall constants through
  `g_syscalls.c`, `sv_game.c`, generated `QL_G_trap_*` wrappers, and
  `ql_game_imports.inc` float forwarding.

## Confidence

High for function identity, source ownership, movement import wiring,
characteristic import ownership, strafe-state fields, and the core combat
movement branch structure. Remaining uncertainty is live-tuning behavior under
real maps and bot character files rather than the static reconstruction shape.

## Validation

- `python -m pytest tests/test_botlib_qagame_ai_dmq3_visibility_parity.py -q --tb=short`
  - `2 passed in 0.10s`
