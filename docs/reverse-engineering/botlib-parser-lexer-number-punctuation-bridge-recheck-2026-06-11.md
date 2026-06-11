# Botlib Parser Lexer Number/Punctuation Bridge Recheck - 2026-06-11

## Scope

This pass rechecks the lower botlib lexer and the numeric structure-reader
bridge beneath the precompiler source-handle and directive/token layers. It is
an evidence and mapping hardening pass: the checked-in C source already matches
the retail shape, so no parser body rewrite was made.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`

Source and tests checked:

- `src/code/botlib/l_script.c`
- `src/code/botlib/l_script.h`
- `src/code/botlib/l_struct.c`
- `src/code/botlib/l_precomp.c`
- `tests/test_botlib_parser_tail_coverage_parity.py`

## Retail Evidence

Observed facts:

- `FUN_004aa610` is the row-backed Ghidra spelling for
  `PC_EvaluateTokens`, size `2689`.
- `FUN_004ad4f0` is the row-backed Ghidra spelling for
  `PS_ReadEscapeCharacter`, size `564`.
- `FUN_004adba0` is the row-backed Ghidra spelling for `PS_ReadNumber`,
  size `710`.
- `FUN_004ade70` is the row-backed Ghidra spelling for
  `PS_ReadPunctuation`, size `176`.
- `FUN_004ae160` is the row-backed Ghidra spelling for
  `PS_ExpectTokenType`, size `858`.
- `FUN_004ae8a0` is the row-backed Ghidra spelling for structure
  `ReadNumber`, size `1062`.
- HLIL for `0x004ade70` walks the punctuation-table bucket for the current
  script byte, compares candidate punctuation strings, copies the matching text
  into the token buffer, advances the script pointer, writes token type `5`,
  and writes the punctuation subtype.
- HLIL for `0x004ae8a0` consumes a token through `PC_ExpectAnyToken`, handles
  punctuation-minus state, rejects unsigned negative values, checks float and
  integer bounds, and stores the parsed value by field type.

## Source Confirmation

The checked-in source preserves the retail scanner lane:

- `PS_ReadNumber` handles hexadecimal, binary, octal/decimal, float, long, and
  unsigned suffixes before tagging non-float numbers as integers.
- `PS_ReadPunctuation` uses the `PUNCTABLE` fast path when compiled, retains the
  fallback punctuation-list loop, bounds the match by `script->end_p`, copies
  the punctuation text with `strncpy`, advances `script_p`, sets
  `TT_PUNCTUATION`, and stores `punc->n` as the subtype.
- `PS_ReadToken` dispatches numeric input to `PS_ReadNumber`, primitive scripts
  to `PS_ReadPrimitive`, names to `PS_ReadName`, and all remaining syntax
  through `PS_ReadPunctuation`.
- `l_struct.c::ReadNumber` is the numeric conversion bridge for parser-backed
  structures, including the unsigned-minus rejection, unexpected punctuation
  diagnostic, float-only field guard, bounded char/int ranges, bounded float
  ranges, and final typed store.
- `PC_EvaluateTokens` and `PS_ExpectTokenType` remain pinned in the same test
  because they are the higher precompiler and diagnostic consumers of the
  token subtype contract.

Inference:

- The selected row set closes a coherent lower parser bridge: primitive script
  lexing, punctuation classification, number classification, precompiler
  expression evaluation, and structure numeric conversion all agree with the
  retail function-size and HLIL evidence.

## Changes

- Promoted:
  - `FUN_004aa610 -> PC_EvaluateTokens`
  - `FUN_004ad4f0 -> PS_ReadEscapeCharacter`
  - `FUN_004adba0 -> PS_ReadNumber`
  - `FUN_004ade70 -> PS_ReadPunctuation`
  - `FUN_004ae160 -> PS_ExpectTokenType`
  - `FUN_004ae8a0 -> ReadNumber`
- Extended `tests/test_botlib_parser_tail_coverage_parity.py` to require both
  `sub_*` and `FUN_*` spellings for the selected rows.
- Added `PS_ReadPunctuation` source and HLIL anchors to the parser-tail parity
  gate.
- Added `ReadNumber` row and HLIL anchors to the same gate so the lower lexer
  and structure numeric conversion bridge stay connected.
- Added `docs/reverse-engineering/quakelive_steam_mapping_round_537.md`.

## Boundary

This round intentionally leaves runtime parsing behavior unchanged. It also
does not touch `src/ui/`, which remains read-only under the repository
instructions.

## Validation

- `python -m pytest tests/test_botlib_parser_tail_coverage_parity.py -q --tb=short`

No runtime launch was needed.

## Parity Estimate

- Focused parser-tail Ghidra/Binary Ninja alias bridge:
  **before 82% -> after 99%**.
- Focused `PS_ReadPunctuation` source/HLIL coverage:
  **before 45% -> after 96%**.
- Focused lower botlib lexer/structure-number bridge:
  **before 88% -> after 90%**.
