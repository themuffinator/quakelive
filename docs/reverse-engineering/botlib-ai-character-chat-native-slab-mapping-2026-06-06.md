# Botlib AI Character/Chat Native Slab Mapping - 2026-06-06

## Scope

This pass closes the qagame native bot-AI character/chat import slab from
`G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER = 110` through
`G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME = 136`.

The source reconstruction point is that the retail native table has direct
slots for `BOTLIB_AI_CHAT_LENGTH` and `BOTLIB_AI_STRING_CONTAINS`. Older local
coverage treated those IDs as compatibility-only because no retained qagame
HLIL callsite to the corresponding offsets was observed. The engine host table
evidence is stronger for the import surface itself: slot 126 points at
`sub_4e1e90`, and slot 129 points at `sub_4e1ef0`.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_ai_character_chat_native_slab_parity.py`
- `tests/test_botlib_chat_parity.py`
- `tests/test_game_native_export_helper_parity.py`

## Findings

- Native slots 110 through 136 are now pinned against the retail import table,
  Ghidra row sizes, source native enum values, legacy syscall remapping, the
  server native import initializer, and the legacy `ql_import_f` dispatch array.
- `BOTLIB_AI_CHAT_LENGTH` is reconstructed as
  `G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH = 126`, bound to
  `QL_G_trap_BotChatLength`, and mapped through `G_MapNativeImport`.
- `BOTLIB_AI_STRING_CONTAINS` is reconstructed as
  `G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS = 129`, bound to
  `QL_G_trap_StringContains`, and mapped through `G_MapNativeImport`.
- `BotAllocChatState` appears in the retail table as raw code address
  `0x4e1d80`, not as an ordinary Ghidra function row. The parity gate checks
  the raw bytes and table entry without inventing a promoted symbol.
- Float marshaling details remain intact for `BotLoadCharacter`,
  `Characteristic_Float`, and `Characteristic_BFloat`.

## Coverage Result

`tests/test_botlib_ai_character_chat_native_slab_parity.py` prevents these
regressions:

- dropping direct native slots 126 and 129 back to the compatibility slab;
- reordering the character/chat native wrapper table around the two recovered
  holes;
- treating raw thunk `0x4e1d80` as a normal promoted function row;
- losing the float pass/return marshaling on character skill and
  characteristic wrappers.

## Parity Estimate

- Focused AI character/chat native slab mapping:
  **before 74% -> after 99%**
- Focused botlib native import direct-vs-compat classification:
  **before 88% -> after 95%**
- Overall botlib plus qagame native import wiring:
  **before 93% -> after 94%**

No runtime launch was needed. The committed retail HLIL table and source import
wiring settle this slice statically.
