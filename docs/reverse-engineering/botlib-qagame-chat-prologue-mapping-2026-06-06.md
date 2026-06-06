# Botlib Qagame Chat Prologue Mapping - 2026-06-06

## Scope

This pass pins the qagame-side bot chat and ranking prologue that feeds botlib
chat behavior. The owning retail binary is `qagamex86.dll`; the mapped range is
`0x10001000..0x100033F0` and corresponds to the front of `src/code/game/ai_chat.c`.

No C source body change was needed. The work promotes aliases and adds a parity
gate that keeps the qagame chat helpers tied to committed retail evidence.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/metadata.txt`
- `references/reverse-engineering/ghidra/qagamex86/imports.txt`
- `references/reverse-engineering/ghidra/qagamex86/exports.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_chat.c`
- `tests/test_botlib_chat_parity.py`

Observed binary metadata: `program_name=qagamex86.dll`, `function_count=1027`,
`import_count=65`, `export_count=2`, and `analysis_symbol_count=1965`.
`imports.txt` includes the `MSVCR100.DLL!rand` dependency used by the chat
probability branches. `exports.txt` exposes only `dllEntry` and `entry`, so this
slice is identified by internal call and source-shape evidence rather than by
exports.

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10001000` | `BotNumActivePlayers` | 230 |
| `0x100010F0` | `BotIsFirstInRankings` | 332 |
| `0x10001240` | `BotIsLastInRankings` | 332 |
| `0x10001390` | `BotFirstClientInRankings` | 340 |
| `0x100014F0` | `BotLastClientInRankings` | 340 |
| `0x10001650` | `BotRandomOpponentName` | 372 |
| `0x100017D0` | `BotMapTitle` | 110 |
| `0x10001840` | `BotWeaponNameForMeansOfDeath` | 122 |
| `0x10001930` | `BotRandomWeaponName` | 131 |
| `0x100019E0` | `BotVisibleEnemies` | 290 |
| `0x10001B10` | `BotValidChatPosition` | 506 |
| `0x10001D10` | `BotChat_EnterGame` | 374 |
| `0x10001E90` | `BotChat_ExitGame` | 297 |
| `0x10001FC0` | `BotChat_StartLevel` | 311 |
| `0x10002100` | `BotChat_EndLevel` | 587 |
| `0x10002350` | `BotChat_Death` | 1102 |
| `0x100027A0` | `BotChat_Kill` | 665 |
| `0x10002A40` | `BotChat_EnemySuicide` | 326 |
| `0x10002B90` | `BotChat_HitTalking` | 422 |
| `0x10002D40` | `BotChat_HitNoDeath` | 476 |
| `0x10002F20` | `BotChat_HitNoKill` | 421 |
| `0x100030D0` | `BotChat_Random` | 724 |
| `0x100033B0` | `BotChatTime` | 42 |
| `0x100033F0` | `BotChatTest` | 4693 |

Both `FUN_...` and `sub_...` aliases were promoted for each row so the Ghidra
and Binary Ninja naming tracks resolve to the same source identity.

## Source Reconstruction Notes

Observed source anchors now pinned by tests:

- Active-player and ranking helpers keep the lazy `sv_maxclients` cache,
  `CS_PLAYERS` configstring sweep, empty-name rejection, spectator exclusion,
  and `PERS_SCORE` comparisons.
- `BotRandomOpponentName` excludes the bot itself, empty client slots,
  spectators, and teammates before selecting a random opponent with the retail
  fallback to `opponents[0]`.
- `BotMapTitle`, `BotWeaponNameForMeansOfDeath`, and `BotRandomWeaponName`
  preserve the Quake Live map-info key and expanded Quake Live weapon/death
  strings, including Proximity Launcher, Kamikaze, Prox mine, and Grapple.
- `BotVisibleEnemies` and `BotValidChatPosition` preserve visibility, invisibility
  plus shooting, same-team, powerup, lava/slime, water, and world-ground trace
  gates.
- The chat handlers preserve the retail `game_*`, `level_*`, `death_*`,
  `kill_*`, `hit_*`, `enemy_suicide`, `random_misc`, and `random_insult` key
  fan-out, including teamplay `vtaunt` fallbacks and the `BotChatTime` constant
  `2.0` return.
- `BotChatTest` remains an exerciser over the same initial-chat keys and
  `trap_BotEnterChat(..., CHAT_ALL)` emission path.

Inferred meaning: this prologue is qagame AI source rather than botlib internal
source. The inference is high confidence because the symbol map, Ghidra row
sizes, HLIL entry/call anchors, and reconstructed `ai_chat.c` function bodies
all agree.

## Coverage Result

`tests/test_botlib_chat_parity.py::test_qagame_bot_chat_prologue_aliases_source_and_hlil_are_pinned`
now verifies:

- qagame owner metadata and export/import context;
- all 24 function identities in `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the prologue;
- direct `ai_chat.c` source anchors for each helper and chat handler;
- HLIL entry signatures and cross-calls among ranking, chat-position,
  visibility, random-opponent, map-title, weapon-name, and botlib chat-entry
  paths.

Focused verification run:

```text
python -m pytest tests/test_botlib_chat_parity.py -q --tb=short
6 passed in 0.67s
```

## Parity Estimate

- Focused qagame bot chat/ranking prologue alias coverage:
  **before 0% -> after 96%**
- Focused botlib plus qagame chat wiring confidence:
  **before 90% -> after 93%**
- Overall botlib plus adjacent qagame AI/chat wiring:
  **before 87% -> after 88%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
with committed HLIL, Ghidra, symbol-map, and source-body evidence.
