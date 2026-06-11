# Botlib Selected-Bot Telemetry Reconstruction - 2026-06-05

## Scope

This pass reconstructs the qagame-side selected-bot debug telemetry path used by `bot_report`/`bot_developer`. The path is botlib-adjacent rather than botlib-internal: qagame records the bot AI node name, samples botlib goal state, then publishes a compact configstring payload for the selected bot.

## Evidence

Canonical Binary Ninja HLIL in `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt` shows:

- `BotRecordNodeSwitch` (`sub_10008460`) writes the node-switch history entry to the global `nodeswitch` buffer.
- The same function then writes the current node string to `arg1 + 0x23cc` with a bounded `0x50` byte `Com_sprintf`-style call.
- `BotPublishDebugInfoString` (`sub_10022ee0`) later passes `param_1 + 0x23cc` as the `ainode` field in the payload.
- The same payload ends with `eh\\%i\\`; after the 2026-06-11 offscreen enemy reconstruction this field is backed by the `enemyFromGoalStack` state written by `BotFindEnemy`.
- `BotResetState` (`sub_10022c60`) clears the full `0x2698` byte `bot_state_t` and restores only the same preserved state group as the source helper, so the node-name string is normal scratch state rather than a preserved reset field.

Structured Ghidra companion evidence in `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c` shows the selected-bot payload format:

`e\\%s\\ed\\%.1f\\tg\\%s\\tgd\\%.1f\\sg\\%s\\sgd\\%.1f\\ainode\\%s\\ltg\\%s\\ban\\%i\\gan\\%i\\bh\\%i\\ba\\%i\\sk\\%.1f\\eh\\%i\\`

The Ghidra decompile also shows the `ainode` argument as `param_1 + 0x23cc` and the final configstring call through the qagame import table. The committed symbol map names the participating functions as `BotRecordNodeSwitch`, `BotPublishDebugInfoString`, `BotResetState`, and `BotAIStartFrame`.

## Reconstruction

- Added `MAX_AINODENAME` as the retail `0x50` byte storage size.
- Added `bot_state_t::ainodename` as qagame scratch state.
- Updated `BotRecordNodeSwitch` to copy the current AI node label into `bs->ainodename` using `Com_sprintf( ..., "%s", node )`, matching the retail call shape.
- Updated `BotPublishDebugInfoString` to publish `bs->ainodename` directly instead of inferring a display string from the `ainode` function pointer.
- Updated `BotPublishDebugInfoString` to publish the offscreen enemy marker from `bs->enemyFromGoalStack`, matching the marker written by the reconstructed retail `BotFindEnemy` side path.
- Removed the source-only `BotDebugAINodeName` helper because retail keeps the display text as recorded state.

## Validation

`tests/test_game_helper_seam_parity.py::test_bot_selected_debug_info_uses_retail_node_name_storage` now ties the reconstruction to:

- retail symbol names and addresses,
- the HLIL `arg1 + 0x23cc` / `0x50` write,
- the HLIL full-state reset,
- the Ghidra payload format and `param_1 + 0x23cc` publisher argument,
- source-side field storage, node-switch update, configstring publishing, and `BotAIStartFrame` gating.

`tests/test_botlib_internal_parity.py::test_qagame_bot_ai_aliases_cover_recent_botlib_mapping_round` also pins the alias coverage for `BotRecordNodeSwitch`, `BotResetState`, `BotPublishDebugInfoString`, and `BotAIStartFrame` in `references/analysis/quakelive_symbol_aliases.json`, while the storage and payload behavior remains guarded by `tests/test_game_helper_seam_parity.py`.

## Confidence

High for the node-name storage and selected-bot payload wiring. The field offset, field size, writer, reader, payload shape, reset behavior, and configstring publish gate are all present in the committed retail reference corpus.
