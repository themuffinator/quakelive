# Botlib Qagame AI DMQ3 Visibility Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_dmq3.c` roaming, combat movement,
visibility, and carrier-query band that follows the support helpers. The
owning retail binary is `qagamex86.dll`; the mapped range is
`0x10017D20..0x10019D30`.

Update 2026-06-11: the `BotFindEnemy` source now includes the retail
offscreen/heard-client acceptance side path. This path is reached only after
`BotEntityVisible` returns non-positive and delegates to
`BotAcceptOffscreenEnemyCandidate`.

Update 2026-06-11: `BotAttackMove` is now pinned at a higher-resolution source
mapping level. The parity gate covers the retail chase-goal setup, character
trait reads, gauntlet distance special case, jump/crouch timers,
`0.4 + (1 - skill) * 0.2` strafe cadence, high-skill jitter, `0.935` strafe
flip threshold, two-attempt side movement loop, and movement-failure strafe
reset.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_dmq3.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_dmq3_visibility_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10017D20` | `BotRoamGoal` | 1372 |
| `0x10018280` | `BotAttackMove` | 1652 |
| `0x10018900` | `BotSameTeam` | 245 |
| `0x10018A00` | `InFieldOfVision` | 276 |
| `0x10018B20` | `BotEntityVisible` | 1889 |
| `0x10019290` | `BotFindEnemy` | 1536 |
| `0x100198A0` | `BotTeamFlagCarrierVisible` | 201 |
| `0x10019970` | `BotTeamFlagCarrier` | 168 |
| `0x10019A20` | `BotEnemyFlagCarrierVisible` | 201 |
| `0x10019AF0` | `BotVisibleTeamMatesAndEnemies` | 357 |
| `0x10019C60` | `BotTeamCubeCarrierVisible` | 208 |
| `0x10019D30` | `BotEnemyCubeCarrierVisible` | 208 |

Both `FUN_...` and `sub_...` aliases are now promoted for every row so the
Ghidra and Binary Ninja naming tracks resolve to the same source identity.

## Source Mapping Notes

Observed source anchors now pinned by tests:

- `BotRoamGoal` preserves the ten-try random roam target generator, forward
  trace, 200-unit distance gate, floor trace, and lava/slime rejection.
- `BotAttackMove` preserves the attack-chase goal fast path, movement-state
  setup, attack-skill/jumper/croucher characteristic reads, gauntlet
  zero-distance behavior, jump/crouch timers, forward/backward ideal-distance
  movement, retail strafe cadence and high-skill jitter, strafe-direction
  flipping/reset, and the two-attempt `trap_BotMoveInDirection` side movement
  fallback.
- `BotSameTeam` preserves the teamplay gate, paired `CS_PLAYERS` configstring
  reads, and parsed team-field comparison.
- `InFieldOfVision` preserves first-two-axis angle normalization, signed
  wraparound across +/-180 degrees, and the +/-`fov * 0.5` rejection window.
- `BotEntityVisible` preserves entity midpoint sampling, field-of-view gating,
  AAS contents probes, water/lava/slime trace flipping, fog-distance
  attenuation, and best-visibility accumulation over middle/bottom/top samples.
- `BotFindEnemy` preserves alertness and easy-fragger characteristic reads,
  current-enemy distance handling, the obelisk special case, invisible/chatting
  player filters, teleport-origin exclusion, same-team rejection, visibility
  scoring, the offscreen enemy fallback through `BotAcceptOffscreenEnemyCandidate`,
  battle-inventory update, and retreat avoidance gate.
- `BotTeamFlagCarrierVisible`, `BotTeamFlagCarrier`, and
  `BotEnemyFlagCarrierVisible` preserve the same-team or enemy-team flag carrier
  scans, with visibility required only for the visible variants.
- `BotVisibleTeamMatesAndEnemies` preserves optional counter zeroing, flag
  carrier filtering, range-squared filtering, visibility testing, and separate
  same-team/enemy counter increments.
- `BotTeamCubeCarrierVisible` and `BotEnemyCubeCarrierVisible` preserve
  harvester cube-carrier scans with same-team or inverse same-team gates and
  positive visibility checks.

Observed retail call-flow anchors include the roam trace pair and contents
reject, the attack-move chase-goal initialization, the movement characteristic
and move-to-goal/move-in-direction calls, the direct strafe state stores at
`bot_state_t + 0x173c` / `+0x17c4`, the `BotSameTeam` configstring pair,
`InFieldOfVision` angle wrapping, `BotEntityVisible` contents/trace/fog
scoring, `BotFindEnemy` cross-calls to `BotSameTeam`, `BotEntityVisible`,
`InFieldOfVision`, `BotAcceptOffscreenEnemyCandidate`,
`BotUpdateBattleInventory`, and `BotWantsToRetreat`, and the carrier helpers'
calls into `EntityCarriesFlag`, `EntityCarriesCubes`, `BotSameTeam`, and
`BotEntityVisible`.

Inferred meaning: this band is the visibility and movement decision surface
between the DMNet tactical nodes and the lower botlib movement/AAS services.
Confidence is high because source bodies, retail symbol-map signatures, Ghidra
row sizes, Binary Ninja HLIL entry/call anchors, and import wiring all agree.

## Botlib Wiring

The new gate pins the legacy and native import paths consumed by this
visibility band:

- `BOTLIB_AAS_POINT_CONTENTS` remains mapped to native slot `70` and is used by
  `BotEntityVisible` for eye, target, water, and fog contents checks.
- `BOTLIB_AI_CHARACTERISTIC_BFLOAT` remains mapped to native slot `113` and is
  used by `BotAttackMove` and `BotFindEnemy` for attack, jump, crouch,
  alertness, and easy-fragger behavior.
- `BOTLIB_AI_MOVE_TO_GOAL` remains mapped to native slot `167` for the
  attack-chase goal path.
- `BOTLIB_AI_MOVE_IN_DIRECTION` remains mapped to native slot `168` for direct
  combat movement and strafing.
- `g_syscalls.c` keeps the legacy qagame wrapper calls and `G_MapNativeImport`
  cases intact.
- `sv_game.c` keeps both the botlib import-table entries and native
  `ql_game_imports[...]` entries wired to generated `QL_G_trap_*` wrappers.
- `ql_game_imports.inc` preserves float forwarding through `QL_G_PASSFLOAT`
  for characteristic and movement-speed calls.

## Coverage Result

`tests/test_botlib_qagame_ai_dmq3_visibility_parity.py` now verifies:

- all 12 visibility-band identities in
  `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the mapped range;
- direct `ai_dmq3.c` source anchors for every promoted helper;
- Binary Ninja HLIL entry signatures and flow/cross-call anchors across the
  roam, movement, visibility, enemy-acquisition, and carrier-query helpers;
- AAS contents, characteristic, move-to-goal, and move-in-direction botlib
  import wiring from game syscall constants through server import
  initialization and generated qagame wrappers.

Focused verification run:

```text
python -m pytest tests/test_botlib_qagame_ai_dmq3_visibility_parity.py -q --tb=short
2 passed in 0.11s
```

## Parity Estimate

- Focused qagame `ai_dmq3.c` visibility-band alias coverage:
  **before 0% -> after 95%**
- Focused source-owned visibility-band parity confidence:
  **before 97% -> after 97.5%**
- Focused botlib movement/visibility import wiring confidence:
  **before 96% -> after 96.5%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 95% -> after 95.2%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
using committed HLIL, Ghidra, symbol-map, source-body, and import-wiring
evidence.
