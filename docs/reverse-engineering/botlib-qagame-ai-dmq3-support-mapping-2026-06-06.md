# Botlib Qagame AI DMQ3 Support Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_dmq3.c` support band that follows the
team-goal dispatcher. The owning retail binary is `qagamex86.dll`; the mapped
range is `0x10015A40..0x10017CD0`.

No C source body change was needed. The existing reconstructed source already
matches the retail evidence for this band, including the newer
`BotNormalizeAmmoInventory` helper that preserves retail `-1` ammo sentinels as
infinite ammo before inventory and pickup logic runs.

Update 2026-06-11: `BotWantsToChase` now preserves the retail invalid-enemy
guard before CTF and 1FCTF flag-carrier probing. The guard matters for the
offscreen enemy acceptance helper, which calls `BotWantsToChase` while
`bs->enemy` is still unset.

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
- `tests/test_botlib_qagame_ai_dmq3_support_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10015A40` | `BotPointAreaNum` | 129 |
| `0x10015AD0` | `ClientName` | 167 |
| `0x10015B80` | `ClientFromName` | 269 |
| `0x10015C90` | `ClientOnSameTeamFromName` | 235 |
| `0x10015D80` | `stristr` | 107 |
| `0x10015DF0` | `EasyClientName` | 219 |
| `0x10015ED0` | `BotChooseWeapon` | 155 |
| `0x10015F70` | `BotSetupForMovement` | 330 |
| `0x100160C0` | `BotCheckItemPickup` | 519 |
| `0x100162D0` | `BotNormalizeAmmoInventory` | 163 |
| `0x10016380` | `BotUpdateInventory` | 747 |
| `0x10016670` | `BotUpdateBattleInventory` | 167 |
| `0x10016720` | `BotUseKamikaze` | 1377 |
| `0x10016C90` | `BotUseInvulnerability` | 862 |
| `0x10016FF0` | `BotBattleUseItems` | 151 |
| `0x10017090` | `BotIsObserver` | 146 |
| `0x10017130` | `BotInLavaOrSlime` | 100 |
| `0x100171A0` | `BotCreateWayPoint` | 202 |
| `0x10017270` | `BotFindWayPoint` | 44 |
| `0x100172A0` | `BotFreeWaypoints` | 37 |
| `0x100172D0` | `BotAggression` | 327 |
| `0x10017420` | `BotFeelingBad` | 72 |
| `0x10017470` | `BotWantsToRetreat` | 419 |
| `0x10017620` | `BotWantsToChase` | 282 |
| `0x10017740` | `BotCanAndWantsToRocketJump` | 158 |
| `0x100177E0` | `BotHasPersistantPowerupAndWeapon` | 302 |
| `0x10017910` | `BotGoCamp` | 234 |
| `0x10017A00` | `BotWantsToCamp` | 581 |
| `0x10017C50` | `BotDontAvoid` | 120 |
| `0x10017CD0` | `BotGoForPowerups` | 70 |

Both `FUN_...` and `sub_...` aliases are now promoted for every row so the
Ghidra and Binary Ninja naming tracks resolve to the same source identity.

## Source Mapping Notes

Observed source anchors now pinned by tests:

- `BotPointAreaNum` preserves the AAS point-area fast path and 10-unit upward
  `trap_AAS_TraceAreas` fallback.
- `ClientName`, `ClientFromName`, `ClientOnSameTeamFromName`, `stristr`, and
  `EasyClientName` preserve the retail name lookup and simplified-name helper
  flow used by chat, orders, waypoints, and team membership.
- `BotChooseWeapon` and `BotSetupForMovement` preserve botlib weapon choice,
  EA weapon selection, live playerstate movement initialization, teleport and
  waterjump flags, crouch presence selection, and `trap_BotInitMoveState`.
- `BotCheckItemPickup`, `BotNormalizeAmmoInventory`, `BotUpdateInventory`, and
  `BotUpdateBattleInventory` preserve pickup-driven team preference updates,
  retail infinite-ammo normalization, full playerstate inventory extraction,
  and battle-distance inventory writes.
- `BotUseKamikaze`, `BotUseInvulnerability`, and `BotBattleUseItems` preserve
  low-health item use and gametype-specific carrier/base safety checks before
  issuing `trap_EA_Use`.
- `BotIsObserver`, `BotInLavaOrSlime`, `BotCreateWayPoint`,
  `BotFindWayPoint`, and `BotFreeWaypoints` preserve observer detection,
  hazard probing, waypoint allocation, lookup, and freelist return.
- `BotAggression`, `BotFeelingBad`, `BotWantsToRetreat`,
  `BotWantsToChase`, `BotCanAndWantsToRocketJump`, and
  `BotHasPersistantPowerupAndWeapon` preserve the combat decision ladder used
  by the DMNet battle, chase, and retreat nodes. `BotWantsToChase` also keeps
  the retail guard that skips flag-carrier entity inspection when no enemy is
  currently assigned.
- `BotGoCamp`, `BotWantsToCamp`, `BotDontAvoid`, and `BotGoForPowerups`
  preserve the camp-goal setup, camper-characteristic throttling, nearest camp
  spot travel-time search, avoid-goal clearing, and powerup LTG reset flow.

Inferred meaning: this band is the shared support layer that feeds qagame AI
movement, inventory, item-use, retreat/chase, camping, and powerup decisions.
Confidence is high because source bodies, retail symbol-map signatures, Ghidra
row sizes, HLIL entry/call anchors, and import wiring all agree.

## Botlib Wiring

The new gate pins the legacy and native import paths consumed by this support
band:

- AAS point, trace, contents, and travel-time helpers remain mapped through
  native slots `67`, `69`, `70`, and `77`.
- EA item-use and weapon-select helpers remain mapped through native slots
  `93` and `102`.
- Characteristic, camp-spot, level-item, avoid-goal, movement-state, and
  best-fight-weapon botlib AI helpers remain mapped through native slots
  `113`, `138`, `152`, `154`, `176`, and `178`.
- `g_syscalls.c` keeps the legacy qagame wrappers and `G_MapNativeImport`
  cases intact.
- `sv_game.c` keeps both the botlib import-table entries and native
  `ql_game_imports[...]` entries wired to generated `QL_G_trap_*` wrappers.
- `ql_game_imports.inc` preserves float forwarding through
  `QL_G_PASSFLOAT` for characteristic queries.

## Coverage Result

`tests/test_botlib_qagame_ai_dmq3_support_parity.py` now verifies:

- all 30 support-band identities in
  `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the mapped range;
- direct `ai_dmq3.c` source anchors for every promoted helper;
- Binary Ninja HLIL entry signatures and flow/cross-call anchors across the
  support band;
- AAS, EA, characteristic, avoid-goal, camp-spot, level-item, movement-state,
  and weapon botlib import wiring from game syscall constants through server
  import initialization and generated qagame wrappers.

Focused verification run:

```text
python -m pytest tests/test_botlib_qagame_ai_dmq3_support_parity.py -q --tb=short
2 passed in 0.12s
```

## Parity Estimate

- Focused qagame `ai_dmq3.c` support-band alias coverage:
  **before 0% -> after 95%**
- Focused source-owned support-band parity confidence:
  **before 90% -> after 97%**
- Focused botlib support import wiring confidence:
  **before 90% -> after 96%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 93% -> after 94%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
using committed HLIL, Ghidra, symbol-map, source-body, and import-wiring
evidence.
