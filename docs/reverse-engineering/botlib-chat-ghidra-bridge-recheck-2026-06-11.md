# Botlib Chat Ghidra Bridge Recheck - 2026-06-11

## Scope

This recheck covers the `be_ai_chat.c` retail corridor in
`quakelive_steam.exe`: console-message heap helpers, text cleanup, string
matching, synonym replacement, chat-message loading, match-piece parsing,
reply/initial chat loading, chat construction, public chat APIs, and chat AI
setup/shutdown.

The source reconstruction did not require C changes. The useful parity gain was
making the alias ledger and tests express both reference dialects:
Binary Ninja `sub_*` owner names and Ghidra `FUN_*` function rows.

## Observed Facts

- Binary Ninja HLIL keeps stable chat-owner names from `sub_497B00` through
  `sub_49C5F0`, with `sub_49C440` visible as `BotAllocChatState`.
- Ghidra `functions.csv` has committed rows for the same chat corridor except
  `0x0049C440`.
- The checked-in alias ledger already had Binary Ninja `sub_*` names for the
  corridor but was missing the corresponding Ghidra `FUN_*` names.
- Existing source tests already pin retail behavior for the chat searchers,
  synonym replacement, match loading, reply and initial chat loaders, chat
  construction, public exports, and native import split.

## Reconstruction Decision

Promote Ghidra `FUN_*` aliases only where the committed Ghidra corpus has a
row. Leave `BotAllocChatState` as a Binary Ninja-only mapping because no
Ghidra row exists for `0049c440`.

That means the bridge now treats `sub_49C440 -> BotAllocChatState` as observed
retail evidence, but intentionally rejects `FUN_0049c440` until the committed
Ghidra evidence changes.

## Test Coverage

`tests/test_botlib_chat_parity.py` now has a central
`test_botlib_chat_ghidra_alias_bridge_rows_are_pinned` gate that:

- walks the full chat Ghidra row set,
- checks `sub_*` and `FUN_*` aliases resolve to the same source owner,
- verifies row name, size, thunk, and calling-convention metadata, and
- proves the `BotAllocChatState` no-row boundary remains explicit.

## Confidence

High for static ownership and wiring. The remaining uncertainty is live chat
data behavior across retail bot chat files, not the source-owner mapping or
export/import wiring covered by this recheck.

## Parity Estimate

- Focused chat Ghidra/Binary Ninja alias bridge: `63% -> 98%`.
- Focused chat source/wiring evidence: `91% -> 96%`.
- Overall botlib static mapping: `89.3% -> 89.5%`.
