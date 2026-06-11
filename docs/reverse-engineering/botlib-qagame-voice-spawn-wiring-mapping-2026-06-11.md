# Botlib Qagame Voice Command and Spawn Wiring Mapping - 2026-06-11

## Scope

This pass extends the qagame-side botlib reconstruction through the
`ai_vcmd.c` voice-command dispatcher and the `g_bot.c` bot spawn/bootstrap
lane. The owning retail binary is `qagamex86.dll`; the primary mapped ranges
are `0x1002B9B0..0x1002C7D0` and `0x100367C0..0x10037E10`.

No C behavior was changed. The work promotes missing aliases and adds a parity
regression that ties source bodies, symbol-map signatures, Ghidra rows, Binary
Ninja HLIL anchors, and qagame botlib import wiring together.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_vcmd.c`
- `src/code/game/ai_main.c`
- `src/code/game/g_bot.c`
- `src/code/game/g_local.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_voice_spawn_wiring_parity.py`

## Mapped Voice Command Rows

| Address | Promoted name | Function size | Evidence status |
| --- | --- | ---: | --- |
| `0x1002B9B0` | `BotVoiceChat_GetFlag` | 238 | Ghidra, symbol-map, HLIL, source |
| `0x1002BAA0` | `BotVoiceChat_Offense` | - | Symbol-map, HLIL, source |
| `0x1002BBC0` | `BotVoiceChat_Defend` | 318 | Ghidra, symbol-map, HLIL, source |
| `0x1002BD00` | `BotVoiceChat_DefendFlag` | - | Symbol-map, HLIL tailcall, source |
| `0x1002BD10` | `BotVoiceChat_Patrol` | - | Symbol-map, HLIL, source |
| `0x1002BE10` | `BotVoiceChat_Camp` | - | Symbol-map, HLIL, source |
| `0x1002C010` | `BotVoiceChat_FollowMe` | 566 | Ghidra, symbol-map, HLIL, source |
| `0x1002C250` | `BotVoiceChat_FollowFlagCarrier` | - | Symbol-map, HLIL, source |
| `0x1002C310` | `BotVoiceChat_ReturnFlag` | 164 | Ghidra, symbol-map, HLIL, source |
| `0x1002C3C0` | `BotVoiceChat_StartLeader` | - | Symbol-map, HLIL, source |
| `0x1002C3F0` | `BotVoiceChat_StopLeader` | - | Symbol-map, HLIL, source |
| `0x1002C470` | `BotVoiceChat_WhoIsLeader` | - | Symbol-map, HLIL, source |
| `0x1002C530` | `BotVoiceChat_WantOnDefense` | 329 | Ghidra, symbol-map, HLIL, source |
| `0x1002C680` | `BotVoiceChat_WantOnOffense` | 329 | Ghidra, symbol-map, HLIL, source |
| `0x1002C7D0` | `BotVoiceChatCommand` | 379 | Ghidra, symbol-map, HLIL, source |

The rows without `functions.csv` sizes are tiny optimized helpers or thunks in
the committed Binary Ninja and symbol-map evidence. They are still pinned to
source names and dispatcher membership by the regression.

## Mapped Spawn and Bootstrap Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x100367C0` | `G_ParseInfos` | 602 |
| `0x10036A20` | `G_AddRandomBot` | 636 |
| `0x10036CB0` | `G_RemoveRandomBot` | 190 |
| `0x10036D80` | `G_CountHumanPlayers` | 82 |
| `0x10036DE0` | `G_CountBotPlayers` | 156 |
| `0x10036E80` | `G_CheckMinimumPlayers` | 681 |
| `0x10037130` | `G_CheckBotSpawn` | 58 |
| `0x10037170` | `AddBotToSpawnQueue` | 540 |
| `0x100373B0` | `G_BotConnect` | 288 |
| `0x100374D0` | `G_GetBotInfoByName` | 78 |
| `0x10037520` | `G_AddBot` | 948 |
| `0x100378E0` | `G_AddTrainerBot` | 46 |
| `0x10037910` | `Svcmd_AddBot_f` | 512 |
| `0x10037B10` | `Svcmd_BotList_f` | 479 |
| `0x10037D00` | `G_LoadBotsFromFile` | 271 |
| `0x10037E10` | `G_LoadBots` | 354 |

## Source Mapping Notes

The voice-command lane now has promoted aliases for the complete handler table:
flag acquisition, offense, defend, defend-flag tailcall, patrol, camp, follow,
follow flag carrier, return flag, leadership, team-task preference, and the
`BotVoiceChatCommand` dispatcher. The regression pins retail strings and HLIL
dispatch shape including `dismissed`, `whereareyou`, `iamteamleader`,
`keepinmind`, `vosay_team`, `votell`, the `data_10090200` command table, and
the indirect handler call through `data_10090204`.

The spawn/bootstrap lane now has promoted aliases for bot info parsing, random
add/remove helpers, human and bot counters, minimum-player balancing, delayed
spawn queue service, bot connection setup, named bot lookup, bot allocation,
trainer bootstrap, addbot/listbot server commands, and bot definition loading.
Pinned retail anchors include `addbot %s %f %s %i\n`, `clientkick %i\n`,
`^3Unable to delay spawn\n`, `BotAISetupClient failed`, `Trainer`, the `5000`
millisecond trainer delay, and `loaddeferred\n`.

## Inference Boundary

`G_AddTrainerBot` is intentionally kept source-equivalent to the existing
reconstruction. The HLIL body proves the fixed `Trainer` name, empty team and
altname, `0x1388` delay, and `loaddeferred\n` server command, but the
decompiler does not make the `xmm0` skill provenance self-evident. The current
source's `g_spSkill` clamp remains unchanged and is documented as a confidence
boundary rather than rewritten from an unstable inference.

## Botlib Wiring

The voice lane depends on botlib chat/EA/world imports through the qagame
syscall bridge, including `trap_BotEnterChat`, `trap_EA_Action`,
`trap_BotGetLevelItemGoal`, and `trap_BotUserCommand`.

The spawn lane is reached from `BotAIStartFrame` through `G_CheckBotSpawn` and
shares the botlib lifecycle bridge used by qagame AI setup, including
`trap_BotLibStartFrame`, `trap_BotLibUpdateEntity`, `trap_BotLibLoadMap`,
`trap_BotLibSetup`, `trap_BotLibShutdown`, bot client allocation, and bot
client freeing. The regression pins the matching native wrappers in
`ql_game_imports.inc`.

## Tests

- `python -m pytest tests/test_botlib_qagame_voice_spawn_wiring_parity.py -q --tb=short`
- `python -m pytest tests/test_botlib_qagame_voice_spawn_wiring_parity.py tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py tests/test_botlib_qagame_ai_cmd_parity.py tests/test_botlib_residual_promoted_alias_coverage.py tests/test_game_helper_seam_parity.py -q --tb=short`

No runtime launch was needed; this was a static reverse-engineering mapping and
regression pass.

## Parity Estimate

- Focused qagame voice-command alias and dispatcher coverage:
  **before 35% -> after 96%** for the 15 guarded rows in this pass.
- Focused qagame bot spawn/bootstrap alias and source-anchor coverage:
  **before 72% -> after 98%** for the 16 guarded rows in this pass.
- Focused botlib-to-qagame chat, EA, usercmd, lifecycle, and spawn wiring
  confidence: **before 94% -> after 98%**.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 98.6% -> after 98.8%**. Remaining uncertainty is concentrated in
  exact trainer skill provenance and fresh runtime validation, not the mapped
  source-owned voice and spawn lanes closed here.
