# Botlib Script Lifecycle Loader Bridge Recheck - 2026-06-11

## Scope

This pass rechecks the `l_script.c` lifecycle and loader band that surrounds
the lower token scanner. It follows the number/punctuation bridge work by
pinning the neighboring script diagnostics, whitespace/comment reader,
string/name/value readers, primitive/full token dispatch, quote strippers,
script flags/end helpers, file and memory loaders, script free, and base-folder
setter.

No source behavior was changed. The work is a Ghidra/Binary Ninja evidence
bridge and parity-gate hardening pass.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Source and tests checked:

- `src/code/botlib/l_script.c`
- `src/code/botlib/l_script.h`
- `tests/test_botlib_parser_tail_coverage_parity.py`

## Retail Evidence

Observed facts:

- Ghidra emits row-backed `FUN_*` names for the selected band:
  - `FUN_004ad230 -> PS_CreatePunctuationTable`, size `240`
  - `FUN_004ad320 -> ScriptError`, size `99`
  - `FUN_004ad390 -> ScriptWarning`, size `99`
  - `FUN_004ad400 -> PS_ReadWhiteSpace`, size `220`
  - `FUN_004ad7b0 -> PS_ReadString`, size `367`
  - `FUN_004ad920 -> PS_ReadName`, size `146`
  - `FUN_004ad9c0 -> NumberValue`, size `463`
  - `FUN_004adf30 -> PS_ReadPrimitive`, size `123`
  - `FUN_004adfc0 -> PS_ReadToken`, size `414`
  - `FUN_004ae4c0 -> StripDoubleQuotes`, size `85`
  - `FUN_004ae520 -> StripSingleQuotes`, size `85`
  - `FUN_004ae580 -> SetScriptFlags`, size `17`
  - `FUN_004ae5a0 -> EndOfScript`, size `23`
  - `FUN_004ae5c0 -> LoadScriptFile`, size `345`
  - `FUN_004ae720 -> LoadScriptMemory`, size `182`
  - `FUN_004ae7e0 -> FreeScript`, size `38`
  - `FUN_004ae810 -> PS_SetBaseFolder`, size `24`
- Binary Ninja HLIL has the matching `sub_*` starts in the same parser-support
  corridor.
- Retail HLIL keeps `PS_ReadToken` after `PS_ReadPrimitive` and before the
  expectation/check helpers, matching the checked-in source dispatch order.
- Retail HLIL keeps `PS_SetBaseFolder` as a compact base-folder string setter,
  matching source behavior under the botlib build.

## Source Confirmation

The checked-in source preserves the retail lane:

- `PS_CreatePunctuationTable` allocates a 256-entry punctuation table, clears
  it, and inserts punctuation definitions sorted by descending string length.
- `ScriptError` and `ScriptWarning` honor `SCFL_NOERRORS` /
  `SCFL_NOWARNINGS` and print filename/line diagnostics through `botimport`.
- `PS_ReadWhiteSpace` skips spaces and C-style `//` / `/* */` comments while
  maintaining the script line counter.
- `PS_ReadString` handles string/literal type selection, escape characters,
  adjacent strings separated by whitespace, missing trailing quotes, and
  newline-in-string diagnostics.
- `PS_ReadName`, `NumberValue`, and `PS_ReadPrimitive` keep the lower reader
  behavior that feeds `PS_ReadToken`.
- `PS_ReadToken` preserves the retail dispatch order: unread token,
  whitespace, string, literal, number, primitive, name, punctuation, then token
  cache copy.
- `LoadScriptFile` and `LoadScriptMemory` allocate `script_t` plus buffer,
  initialize cursor and line fields, install default punctuation tables, and
  either read/compress file content or copy caller-provided memory.
- `FreeScript` releases the punctuation table when present and then frees the
  script allocation.

Inference:

- This band is a coherent script lifetime contract. It owns how botlib script
  input is allocated, normalized, tokenized, and released before higher
  precompiler and structure parsers consume it.

## Changes

- Promoted `FUN_*` aliases for the selected lifecycle/loader band in
  `references/analysis/quakelive_symbol_aliases.json`.
- Added
  `test_script_lifecycle_loader_bridge_aliases_rows_and_source_shape_are_pinned`
  to `tests/test_botlib_parser_tail_coverage_parity.py`.
- Added `docs/reverse-engineering/quakelive_steam_mapping_round_539.md`.
- Updated `docs/reverse-engineering/botlib-parser-tail-coverage-mapping-2026-06-06.md`
  with the lifecycle/loader bridge closure.

## Boundary

This pass does not alter parser code and does not require a runtime launch.
The remaining uncertainty in this area is live-data parser coverage with real
retail bot resources, not static source identity.

## Validation

- `python -m pytest tests/test_botlib_parser_tail_coverage_parity.py -q --tb=short`

## Parity Estimate

- Focused script lifecycle/loader Ghidra/Binary Ninja alias bridge:
  **before 64% -> after 98%**.
- Focused `l_script.c` loader/token-dispatch source evidence:
  **before 82% -> after 95%**.
- Overall botlib parser/support static mapping:
  **before 89.0% -> after 89.3%**.
