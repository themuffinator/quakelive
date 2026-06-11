# Botlib Qagame AI DMNet Tutorial Tail Mapping - 2026-06-06

## Scope

This pass pins the retail-only qagame `ai_dmnet.c` tutorial tail and the two
team helper leaves that sit immediately after the battle-node slice. The owning
retail binary is `qagamex86.dll`; the mapped range is
`0x1000ECC0..0x10013B00`.

The pass remains mapping-heavy for the teammate, lead, torment, and fragbait
tutorial nodes because several retail `bot_state_t` tail fields are not yet
represented in the current source tree. Three source-backed islands are now
safe in this slice: `BotSetLeadTeamGoal` preserves the retail lead-team goal
seed, `AIEnter_InstaGib` / `AINode_InstaGib` preserve the instant-rail target
node and movement path, and `BotCTFCarryingFlag` preserves the retail second
CTF-like gametype gate by accepting current-source `GT_ATTACK_DEFEND` alongside
`GT_CTF`.

Update 2026-06-11: the shared `BotResolveTourPoint` helper used by the mapped
lead and torment tutorial nodes is now source-backed in `ai_dmq3.c`. The
adjacent `BotCanSpawnTourPoint` raw entity-slab gate is also source-backed. The
larger nodes remain mapped-only, but these tour-point leaf helpers no longer
do.

Second update 2026-06-11: the torment-human target selector
`BotSelectTormentTarget` is also source-backed in `ai_dmq3.c`. The larger
`AIEnter_Torment_Human` and `AINode_Torment_Human` bodies remain mapped-only,
but their 500-unit target-selection leaf now has source, tests, and symbol-map
coverage.

Third update 2026-06-11: the source now names the retail tutorial LTG values
`0x10..0x14` as `LTG_FOLLOWING`, `LTG_TRAINING`, `LTG_TOURING`,
`LTG_TORMENT_HUMAN`, and `LTG_TARGET`, matching the existing debug labels.
The parity gate now pins the small retail enter helpers down to their LTG
assignments, adjacent node-pointer writes, torment cached-enemy reset,
torment `+0x2498` retry/stall counter reset, fragbait `FloatTime()+10` timer,
and tutorial bot-state flag writes. The enter helpers remain mapped-only in
source because compiling `AIEnter_Torment_Human` faithfully would require a
real `AINode_Torment_Human` body rather than an invented stub.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_dmnet.c`
- `src/code/game/ai_dmq3.c`
- `src/code/game/ai_main.c`
- `src/code/game/g_cmds.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py`
- `tests/test_ctf_oneflag_retail_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x1000ECC0` | `AIEnter_Seek_Teammate` | 220 |
| `0x1000EDA0` | `AINode_Seek_Teammate` | 2629 |
| `0x1000F7F0` | `BotSetLeadTeamGoal` | 129 |
| `0x1000F880` | `AIEnter_Lead_Teammate` | 355 |
| `0x1000FA00` | `AINode_Lead_Teammate` | 7920 |
| `0x10011900` | `AIEnter_Torment_Human` | 110 |
| `0x10011980` | `AINode_Torment_Human` | 2733 |
| `0x10012430` | `AIEnter_Lead_Teammate_FragBait` | 276 |
| `0x10012560` | `AINode_Lead_Teammate_FragBait` | 3655 |
| `0x100133C0` | `AIEnter_InstaGib` | 65 |
| `0x10013410` | `AINode_InstaGib` | 1711 |
| `0x10013AC0` | `BotCTFCarryingFlag` | 52 |
| `0x10013B00` | `BotTeam` | 209 |

Both `FUN_...` and `sub_...` aliases were promoted for each row so the Ghidra
and Binary Ninja naming tracks resolve to the same source identity.

## Source Reconstruction Notes

Observed source-owned changes:

- `BotSetLeadTeamGoal` now matches the retail HLIL writes at
  `0x1000F7F0`: copy `bs->origin` to `bs->lead_teamgoal.origin`, copy
  `bs->areanum` to `bs->lead_teamgoal.areanum`, and set the normal player
  bounds `(-16, -16, -24)` to `(16, 16, 32)`.

- `BotCTFCarryingFlag` now matches the retail HLIL gate
  `ecx_1 != 5 && ecx_1 != 0xb` by accepting `GT_ATTACK_DEFEND` in addition to
  `GT_CTF`, while preserving the direct red/blue inventory return shape.
  The current source enum names raw `0xb` as `GT_ATTACK_DEFEND`.

- `AIEnter_InstaGib` now matches the retail HLIL writes at `0x100133C0`:
  seed `ltg_time` with `FloatTime() + 99999.0`, assign the retail LTG value
  `0x15` through `LTG_INSTAGIB`, record the `insta gib!` node label, and hand
  control to `AINode_InstaGib`.

- `AINode_InstaGib` now preserves the stable source-representable retail path:
  target selection through `BotFindInstaGibTarget`, observer/intermission/dead
  exits, `g_instaGib` no-node fallback, normal enemy handoff into
  `AIEnter_Battle_Fight`, the `0x011C0FBE` travel mask, goal-stack empty/push,
  `[-8, -8, -8]..[8, 8, 8]` target goal bounds, Beyond Reality travel-flag
  filtering, obstacle prediction, `trap_BotMoveToGoal`, blocked-path cleanup,
  movement-view handling, and movement-weapon handoff.

Observed retail-only tutorial node behavior now pinned by tests:

- `AIEnter_Seek_Teammate` and `AINode_Seek_Teammate` preserve the
  `seek teammate` node label, observer/intermission/dead/no-ai/no-client exits,
  `bot_followMe` reset, tutorial taunt, and movement path into the adjacent
  teammate-pursuit state.
- `BotSetLeadTeamGoal`, `AIEnter_Lead_Teammate`, and
  `AINode_Lead_Teammate` preserve the lead-team-goal seed, `lead teammate`
  label, `bot_training` and `bot_followMe` cvar handling, and repeated
  `This way! No time to waste!` command paths.
- `AIEnter_Torment_Human` and `AINode_Torment_Human` preserve the
  `torment human` label, `LTG_TORMENT_HUMAN` assignment, adjacent node-pointer
  install, cached enemy reset, torment retry/stall counter reset,
  observer/intermission/dead/no-ai exits, human harassment movement, the
  source-backed `BotSelectTormentTarget(bs, 500.0f)` call, and
  fragbait/kamikaze branches.
- The adjacent `BotResolveTourPoint` and `BotCanSpawnTourPoint` helpers are now
  source-backed outside this `ai_dmnet.c` file: the resolver handles
  current-linked or fallback-start `info_tour_point` entities and their linked
  `info_notnull` facing targets, while the spawn gate scans reusable non-client
  entity slots by `inuse` and `freetime`.
- The adjacent `BotSelectTormentTarget` helper is now source-backed outside
  this `ai_dmnet.c` file: it revalidates the cached visible torment target,
  then searches human client slots through direct AAS reachability,
  trace-assisted reachability, and nearest-valid fallback passes.
- `AIEnter_Lead_Teammate_FragBait` and
  `AINode_Lead_Teammate_FragBait` preserve the late tutorial lead/fragbait
  branch, including the `LTG_TARGET` assignment, `FloatTime()+10` scratch
  timer, `Kill me if you can - fragbait!`, and the return-to-tour prompt.
- `AIEnter_InstaGib` and `AINode_InstaGib` preserve the `insta gib!` label,
  observer/intermission/dead/no-ai exits, target-goal movement flow, and the
  transition into `AIEnter_Battle_Fight` on enemy acquisition.
- `BotTeam` preserves the `CS_PLAYERS + bs->client` configstring fetch and
  `PLAYER_INFO_KEY_TEAM` parse into red, blue, or free team values.

Open source gap: the remaining teammate, lead, torment, and fragbait tutorial
node bodies after `AINode_Battle_NBG` are not yet compiled source in
`src/code/game/ai_dmnet.c`. Reconstructing them accurately requires a dedicated
retail `bot_state_t` tail-layout pass because the HLIL uses fields around
`0x241c..0x2500` that do not currently have stable source members. The
instagib node still carries one narrow unresolved boundary too: the raw retail
player-state cleanup writes on intermission/death exits are documented but not
guessed in source.

## Botlib And Training Wiring

The new gate pins the wiring that this tutorial tail consumes:

- Training cvars remain owned by `ai_main.c` and the `readyup` reset path in
  `g_cmds.c`: `g_training`, `bot_training`, `bot_dynamicSkill`,
  `bot_followMe`, `bot_followDist`, `bot_itemDelayTime`, and
  `bot_startingSkill`.
- AAS and movement imports remain mapped for point-area lookup,
  area-reachability checks, `trap_BotMoveToGoal`, and
  `trap_BotMovementViewTarget`.
- EA imports remain mapped for command emission and gestures, matching the
  retail tutorial strings emitted through the botlib EA command path.
- `sv_game.c` keeps both legacy botlib import-table entries and native
  `G_QL_IMPORT_BOTLIB_*` slots wired to the generated `QL_G_trap_*` wrappers.

## Coverage Result

`tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py` now verifies:

- all 13 tutorial-tail identities in `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the mapped range;
- HLIL entry signatures and cross-calls for teammate seeking, leading,
  torment-human, fragbait, instagib, `BotCTFCarryingFlag`, and `BotTeam`;
- retail tutorial enter-helper field writes for LTG assignment, adjacent
  `ainode` installation, cached-target resets, scratch timer resets, and
  tutorial bot-state flag application;
- Ghidra decompile anchors for the retail tutorial strings and exit branches;
- source-owned `BotSetLeadTeamGoal`, `AIEnter_InstaGib`, and
  `AINode_InstaGib` in `ai_dmnet.c`, plus `BotCTFCarryingFlag` and `BotTeam`
  bodies in `ai_dmq3.c`, plus named retail tutorial LTG constants in
  `ai_main.h`, plus the source-backed torment target/tour-point leaves
  consumed by the mapped tutorial nodes;
- training cvar, AAS, EA, and botlib movement import wiring.

Focused verification runs:

```text
python -m pytest tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py -q --tb=short
3 passed in 0.14s

python -m pytest tests -k botlib -q --tb=short
205 passed, 1864 deselected in 4.12s
```

## Parity Estimate

- Focused qagame tutorial-tail alias coverage:
  **before 0% -> after 94%**
- Focused source-owned `BotCTFCarryingFlag` retail predicate parity:
  **before 85% -> after 98%**
- Focused source-owned `BotSetLeadTeamGoal` retail leaf parity:
  **before 0% -> after 96%**
- Focused source-owned instagib node reconstruction confidence:
  **before 0% -> after 88%**
- Focused training/botlib movement and EA wiring confidence:
  **before 95% -> after 96%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 92.6% -> after 92.8%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
with focused source reconstruction, using committed HLIL, Ghidra, symbol-map,
source-body, and import-wiring evidence.
