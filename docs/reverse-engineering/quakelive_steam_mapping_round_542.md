# Quake Live Steam Mapping Round 542

## Scope

This round rechecked the engine-owned botlib chat corridor in
`quakelive_steam.exe`, from console-message heap setup through chat resource
loading, match helpers, public chat exports, and chat AI shutdown. The goal was
not to rewrite source bodies; the checked-in `be_ai_chat.c` reconstruction
already matches the observed retail body shapes. The gap was the evidence
bridge between Binary Ninja `sub_*` names and committed Ghidra `FUN_*`
function rows.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source and wiring:
  `src/code/botlib/be_ai_chat.c`,
  `src/code/botlib/be_interface.c`,
  `src/code/game/botlib.h`,
  `src/code/game/g_syscalls.c`, and `src/code/server/sv_game.c`

## Promoted Alias Bridge

Promoted Ghidra-style aliases now mirror the already-mapped Binary Ninja
owners for the chat corridor rows that have committed Ghidra function entries:

- Console-message heap helpers:
  `FUN_00497b00`, `FUN_00497bd0`, `FUN_00497cb0`,
  `FUN_00497de0`, and `FUN_00497e60`.
- Text cleanup and string search:
  `FUN_00497eb0`, `FUN_00497f00`, `FUN_00498020`, and
  `FUN_00498100`.
- Synonym, chat-message, random-string, match-piece, and reply-chat helpers:
  `FUN_00498210`, `FUN_00498710`, `FUN_00498890`,
  `FUN_00498a70`, `FUN_00498bb0`, `FUN_00498dd0`,
  `FUN_004990d0`, `FUN_00499170`, `FUN_004991c0`,
  `FUN_00499510`, `FUN_00499580`, `FUN_00499880`,
  `FUN_004999c0`, `FUN_00499bf0`, `FUN_00499c60`,
  `FUN_00499e70`, `FUN_0049a080`, `FUN_0049a160`,
  `FUN_0049a3a0`, `FUN_0049a960`, `FUN_0049af40`, and
  `FUN_0049afb0`.
- Public construction/export/lifecycle owners:
  `FUN_0049b170`, `FUN_0049b4d0`, `FUN_0049b610`,
  `FUN_0049b6c0`, `FUN_0049bae0`, `FUN_0049c1b0`,
  `FUN_0049c210`, `FUN_0049c300`, `FUN_0049c370`,
  `FUN_0049c3d0`, `FUN_0049c480`, `FUN_0049c560`, and
  `FUN_0049c5f0`.

`BotAllocChatState` remains intentionally Binary Ninja-only at
`sub_49C440`. The HLIL and AI export assignment both show the owner, but the
committed Ghidra `functions.csv` has no `0049c440` row. This pass keeps that
absence explicit instead of inventing a fake `FUN_0049c440` alias.

## Source/Wiring Reconstruction Notes

- `be_ai_chat.c` source shape remains unchanged: the chat string matchers,
  synonym replacement, match-template parser, reply/initial chat loaders,
  message construction, and state lifecycle already match the retail anchors
  covered by the existing chat tests.
- `be_interface.c::Init_AI_Export` continues to expose the public chat family,
  including `BotInitialChat`, `BotReplyChat`, `BotChatLength`,
  `BotEnterChat`, `BotGetChatMessage`, `StringContains`, `BotFindMatch`,
  `BotMatchVariable`, `UnifyWhiteSpaces`, `BotReplaceSynonyms`,
  `BotLoadChatFile`, `BotSetChatGender`, and `BotSetChatName`.
- The qagame native-import split remains unchanged: direct retail evidence
  supports `BotEnterChat`, `BotGetChatMessage`, `BotFindMatch`,
  `BotMatchVariable`, `UnifyWhiteSpaces`, `BotSetChatGender`, and
  `BotSetChatName`; compatibility slots still cover `BotChatLength` and
  `StringContains`.

## Validation

Added a central gate in `tests/test_botlib_chat_parity.py` that verifies every
promoted chat `FUN_*` alias maps to the same source owner as the existing
Binary Ninja `sub_*` alias, checks the committed Ghidra row name/size/thunk
metadata, and preserves the no-row boundary for `BotAllocChatState`.

Observed validation for this pass:

```text
python -m pytest tests/test_botlib_chat_parity.py -q --tb=short
7 passed in 0.33s

python -m pytest tests -k botlib -q --tb=short
208 passed, 1864 deselected in 4.16s

python -m json.tool references/analysis/quakelive_symbol_aliases.json | Out-Null
passed
```

No game launch is required. Static HLIL, Ghidra row metadata, source shape, and
pytest coverage answer this mapping question.

## Parity Estimate

- Focused botlib chat Ghidra/Binary Ninja alias bridge:
  approximately `63% -> 98%`.
- Focused botlib chat source/wiring evidence confidence:
  approximately `91% -> 96%`.
- Overall botlib static mapping confidence:
  approximately `89.3% -> 89.5%`.
