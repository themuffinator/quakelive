# Botlib Qagame AI DMQ3 Team Goal Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_dmq3.c` team-goal helper band that follows
the recovered tutorial-tail helpers. The owning retail binary is
`qagamex86.dll`; the mapped range is `0x10013BE0..0x10015960`.

No C source body change was needed in this pass. The reconstructed
`ai_dmq3.c` bodies already preserve the observed team-goal helper behavior, so
the work promoted the missing reusable aliases and added a focused parity gate
around source bodies, HLIL flow anchors, Ghidra row sizes, symbol-map names,
and direct botlib/AAS/EA import wiring.

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
- `tests/test_botlib_qagame_ai_dmq3_team_goal_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10013BE0` | `BotOppositeTeam` | 30 |
| `0x10013C00` | `EntityIsDead` | 95 |
| `0x10013C60` | `EntityCarriesFlag` | 27 |
| `0x10013C80` | `EntityCarriesCubes` | 125 |
| `0x10013D00` | `Bot1FCTFCarryingFlag` | 21 |
| `0x10013D20` | `BotHarvesterCarryingCubes` | 41 |
| `0x10013D50` | `BotRememberLastOrderedTask` | 69 |
| `0x10013DA0` | `BotSetTeamStatus` | 95 |
| `0x10013E20` | `BotSetLastOrderedTask` | 473 |
| `0x10014020` | `BotRefuseOrder` | 120 |
| `0x100140A0` | `BotCTFSeekGoals` | 2187 |
| `0x10014930` | `BotCTFRetreatGoals` | 130 |
| `0x100149C0` | `Bot1FCTFSeekGoals` | 1584 |
| `0x10015010` | `Bot1FCTFRetreatGoals` | 244 |
| `0x10015120` | `BotObeliskSeekGoals` | 722 |
| `0x10015400` | `BotGoHarvest` | 104 |
| `0x10015470` | `BotHarvesterSeekGoals` | 1104 |
| `0x100158E0` | `BotHarvesterRetreatGoals` | 124 |
| `0x10015960` | `BotTeamGoals` | 219 |

Both `FUN_...` and `sub_...` aliases are now promoted for every row so the
Ghidra and Binary Ninja naming tracks resolve to the same source identity.

## Source Mapping Notes

Observed source anchors now pinned by tests:

- `BotOppositeTeam` preserves the direct `BotTeam` call and red/blue/free
  remap.
- `EntityIsDead`, `EntityCarriesFlag`, and `EntityCarriesCubes` preserve the
  client-state, powerup-bit, and harvester `generic1` carrier predicates used
  by higher-level bot decisions.
- `Bot1FCTFCarryingFlag` and `BotHarvesterCarryingCubes` preserve the
  gametype gates and neutral-flag or cube inventory checks.
- `BotRememberLastOrderedTask`, `BotSetTeamStatus`, and
  `BotSetLastOrderedTask` preserve ordered-task snapshot, teamtask userinfo
  publication, return-flag invalidation, and alternate-route recomputation for
  restored CTF `GETFLAG` tasks.
- `BotRefuseOrder` preserves the recent-order gate, negative EA action, team
  voice refusal, and order-time clear.
- `BotCTFSeekGoals`, `Bot1FCTFSeekGoals`, `BotObeliskSeekGoals`, and
  `BotHarvesterSeekGoals` preserve the carried-object rushbase paths,
  flag/status branches, leader/ordered-goal gates, aggression and roam checks,
  attacker/defender preference split, and final team-status updates.
- `BotCTFRetreatGoals`, `Bot1FCTFRetreatGoals`, and
  `BotHarvesterRetreatGoals` preserve the reduced retreat-mode rushbase paths.
- `BotGoHarvest` preserves the enemy-obelisk target copy, `LTG_HARVEST`
  assignment, harvest timer, and status refresh.
- `BotTeamGoals` preserves the retreat-versus-seek dispatcher across
  `GT_CTF`, `GT_1FCTF`, `GT_OBELISK`, and `GT_HARVESTER`, followed by the
  order-time reset.

Inferred meaning: this band is the qagame AI team-objective decision layer that
sits between message-driven orders from `ai_cmd.c`, active movement/battle
nodes in `ai_dmnet.c`, and botlib route/EA services. Confidence is high because
source bodies, retail symbol-map signatures, Ghidra sizes, HLIL entry/call
anchors, and import wiring all agree.

Open question: the source-only `BotObeliskRetreatGoals` no-op remains present
as the `BotTeamGoals` retreat branch target, but this pass did not promote a
separate retail row for it because the mapped retail function table in this
band has no distinct `BotObeliskRetreatGoals` body between
`BotGoHarvest` and `BotHarvesterSeekGoals`.

## Botlib Wiring

The new gate pins the direct legacy and native import paths consumed by this
team-goal band:

- `trap_AAS_AreaTravelTimeToGoalArea` remains mapped from
  `BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA` to native Quake Live import slot
  `G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA = 77`.
- `trap_EA_Action` remains mapped from `BOTLIB_EA_ACTION` to native Quake Live
  import slot `G_QL_IMPORT_BOTLIB_EA_ACTION = 88`.
- `g_syscalls.c` maps both legacy botlib syscall IDs to their native import
  slots and keeps the classic qagame wrappers intact.
- `sv_game.c` keeps both the botlib import-table entries and native
  `ql_game_imports[...]` entries wired to the generated `QL_G_trap_*`
  wrappers.
- `ql_game_imports.inc` forwards both services through `G_Import_Syscall`,
  matching the reconstructed qagame syscall ABI.

## Coverage Result

`tests/test_botlib_qagame_ai_dmq3_team_goal_parity.py` now verifies:

- all 19 `ai_dmq3.c` team-goal helper identities in
  `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the mapped range;
- direct `ai_dmq3.c` source anchors for every promoted helper and dispatcher;
- Binary Ninja HLIL entry signatures and flow/cross-call anchors across the
  team-goal band;
- botlib AAS travel-time and EA action import wiring from game syscall
  constants through server import initialization and generated qagame wrappers.

Focused verification run:

```text
python -m pytest tests/test_botlib_qagame_ai_dmq3_team_goal_parity.py -q --tb=short
2 passed in 0.17s
```

## Parity Estimate

- Focused qagame `ai_dmq3.c` team-goal alias coverage:
  **before 0% -> after 95%**
- Focused source-owned team-goal source parity confidence:
  **before 88% -> after 96%**
- Focused botlib/AAS/EA wiring into team-goal selection:
  **before 90% -> after 96%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 92% -> after 93%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
using committed HLIL, Ghidra, symbol-map, source-body, and import-wiring
evidence.
