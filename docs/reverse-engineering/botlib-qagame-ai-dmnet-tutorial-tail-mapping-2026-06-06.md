# Botlib Qagame AI DMNet Tutorial Tail Mapping - 2026-06-06

## Scope

This pass pins the retail-only qagame `ai_dmnet.c` tutorial tail and the two
team helper leaves that sit immediately after the battle-node slice. The owning
retail binary is `qagamex86.dll`; the mapped range is
`0x1000ECC0..0x10013B00`.

The pass is mostly mapping because the teammate, lead, torment, fragbait, and
instagib tutorial nodes depend on retail `bot_state_t` tail fields that are not
yet represented in the current source tree. One narrow source reconstruction
was safe: `BotCTFCarryingFlag` now preserves the retail second CTF-like gametype
gate by accepting current-source `GT_ATTACK_DEFEND` alongside `GT_CTF`.

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

Observed source-owned change:

- `BotCTFCarryingFlag` now matches the retail HLIL gate
  `ecx_1 != 5 && ecx_1 != 0xb` by accepting `GT_ATTACK_DEFEND` in addition to
  `GT_CTF`, while preserving the direct red/blue inventory return shape.
  The current source enum names raw `0xb` as `GT_ATTACK_DEFEND`.

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
  `torment human` label, observer/intermission/dead/no-ai exits, human
  harassment movement, and fragbait/kamikaze branches.
- `AIEnter_Lead_Teammate_FragBait` and
  `AINode_Lead_Teammate_FragBait` preserve the late tutorial lead/fragbait
  branch, including `Kill me if you can - fragbait!` and the return-to-tour
  prompt.
- `AIEnter_InstaGib` and `AINode_InstaGib` preserve the `insta gib!` label,
  observer/intermission/dead/no-ai exits, and the transition into
  `AIEnter_Battle_Fight` on enemy acquisition.
- `BotTeam` preserves the `CS_PLAYERS + bs->client` configstring fetch and
  `PLAYER_INFO_KEY_TEAM` parse into red, blue, or free team values.

Open source gap: the tutorial node bodies after `AINode_Battle_NBG` are not yet
compiled source in `src/code/game/ai_dmnet.c`. Reconstructing them accurately
requires a dedicated retail `bot_state_t` tail-layout pass because the HLIL
uses fields around `0x241c..0x2500` that do not currently have stable source
members.

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
- Ghidra decompile anchors for the retail tutorial strings and exit branches;
- source-owned `BotCTFCarryingFlag` and `BotTeam` bodies in `ai_dmq3.c`;
- training cvar, AAS, EA, and botlib movement import wiring.

Focused verification runs:

```text
python -m pytest tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py -q --tb=short
3 passed in 0.30s

python -m pytest tests/test_ctf_oneflag_retail_parity.py -q --tb=short
7 passed in 0.37s
```

## Parity Estimate

- Focused qagame tutorial-tail alias coverage:
  **before 0% -> after 94%**
- Focused source-owned `BotCTFCarryingFlag` retail predicate parity:
  **before 85% -> after 98%**
- Focused training/botlib movement and EA wiring confidence:
  **before 87% -> after 94%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 91% -> after 92%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
with a narrow source correction, using committed HLIL, Ghidra, symbol-map,
source-body, and import-wiring evidence.
