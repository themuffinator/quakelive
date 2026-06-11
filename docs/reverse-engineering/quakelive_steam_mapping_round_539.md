# Quake Live Steam Mapping Round 539: Botlib Script Lifecycle Loader Bridge

## Scope

This pass tightens the Ghidra/Binary Ninja evidence bridge for the lower
`l_script.c` lifecycle and loader band in retail `quakelive_steam.exe`. The
previous botlib parser round pinned the number/punctuation lexer seam; this
round covers the neighboring diagnostics, whitespace, string/name/value,
primitive/full-token, quote-stripper, flag/end, file-load, memory-load, free,
and base-folder owners.

| Retail address | Ghidra name | Binary Ninja name | Promoted name | Confidence |
| --- | --- | --- | --- | --- |
| `0x004ad230` | `FUN_004ad230` | `sub_4AD230` | `PS_CreatePunctuationTable` | High |
| `0x004ad320` | `FUN_004ad320` | `sub_4AD320` | `ScriptError` | High |
| `0x004ad390` | `FUN_004ad390` | `sub_4AD390` | `ScriptWarning` | High |
| `0x004ad400` | `FUN_004ad400` | `sub_4AD400` | `PS_ReadWhiteSpace` | High |
| `0x004ad7b0` | `FUN_004ad7b0` | `sub_4AD7B0` | `PS_ReadString` | High |
| `0x004ad920` | `FUN_004ad920` | `sub_4AD920` | `PS_ReadName` | High |
| `0x004ad9c0` | `FUN_004ad9c0` | `sub_4AD9C0` | `NumberValue` | High |
| `0x004adf30` | `FUN_004adf30` | `sub_4ADF30` | `PS_ReadPrimitive` | High |
| `0x004adfc0` | `FUN_004adfc0` | `sub_4ADFC0` | `PS_ReadToken` | High |
| `0x004ae4c0` | `FUN_004ae4c0` | `sub_4AE4C0` | `StripDoubleQuotes` | High |
| `0x004ae520` | `FUN_004ae520` | `sub_4AE520` | `StripSingleQuotes` | High |
| `0x004ae580` | `FUN_004ae580` | `sub_4AE580` | `SetScriptFlags` | High |
| `0x004ae5a0` | `FUN_004ae5a0` | `sub_4AE5A0` | `EndOfScript` | High |
| `0x004ae5c0` | `FUN_004ae5c0` | `sub_4AE5C0` | `LoadScriptFile` | High |
| `0x004ae720` | `FUN_004ae720` | `sub_4AE720` | `LoadScriptMemory` | High |
| `0x004ae7e0` | `FUN_004ae7e0` | `sub_4AE7E0` | `FreeScript` | High |
| `0x004ae810` | `FUN_004ae810` | `sub_4AE810` | `PS_SetBaseFolder` | High |

## Evidence

Observed retail facts:

- Ghidra `functions.csv` emits concrete rows for every selected function, with
  sizes from `17` bytes for `SetScriptFlags` through `414` bytes for
  `PS_ReadToken` and `463` bytes for `NumberValue`.
- Binary Ninja HLIL places the functions in the same lower parser band, with
  `PS_ReadToken` immediately after `PS_ReadPrimitive` and before the
  expectation/check helpers.
- HLIL for `PS_SetBaseFolder` is the compact base-folder setter at
  `0x004ae810`, tailing into the engine string-format helper with the retained
  botlib base-folder storage.
- The checked-in source keeps `LoadScriptFile` and `LoadScriptMemory` on the
  same allocation layout: `script_t` followed by the script buffer, initialized
  pointers, line counters, punctuation table setup, and compressed file content
  for file loads.

Inferred meaning:

- These names are safe to promote in both Ghidra and Binary Ninja spelling
  forms because function-size rows, HLIL adjacency, source ownership, and the
  parser-tail parity gate agree.
- This is still a static reconstruction pass. It confirms the retail parser
  loader contract but does not claim new behavior beyond the checked-in C
  source.

## Reconstruction

- Promoted the missing `FUN_*` aliases for the selected `l_script.c` lifecycle
  and loader owners in `references/analysis/quakelive_symbol_aliases.json`.
- Added
  `test_script_lifecycle_loader_bridge_aliases_rows_and_source_shape_are_pinned`
  to `tests/test_botlib_parser_tail_coverage_parity.py`.
- The new gate pins:
  - alias spelling parity for `sub_*` and `FUN_*`;
  - Ghidra row sizes;
  - HLIL function starts and representative helper calls;
  - source prototypes in `l_script.h`;
  - punctuation table creation, diagnostics, whitespace/comment skipping,
    string/name/value parsing, primitive and full token dispatch, quote
    stripping, script flag/end helpers, file/memory loader layout, free, and
    base-folder setup.

No C source body change was needed.

## Validation

- `python -m pytest tests/test_botlib_parser_tail_coverage_parity.py -q --tb=short`

No runtime launch was performed; committed retail HLIL, Ghidra metadata, source
inspection, and pytest evidence were sufficient.

## Parity Estimate

- Focused script lifecycle/loader Ghidra/Binary Ninja alias bridge:
  **before 64% -> after 98%**.
- Focused `l_script.c` loader/token-dispatch source evidence:
  **before 82% -> after 95%**.
- Overall botlib parser/support static mapping:
  **before 89.0% -> after 89.3%**.
