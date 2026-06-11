# Botlib Parser Tail Coverage Mapping - 2026-06-06

## Scope

This pass closes the remaining direct botlib test-coverage gap in the parser
and support tail from `0x004A83C0` through `0x004AF820`. The earlier parser
rounds had already promoted the four names below, but they were still missing
direct `test_botlib_*.py` mentions in the current alias scan.

No C source body change or alias JSON change was needed. The checked-in parser
source already matches the committed retail evidence for this static slice.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/botlib/l_precomp.c`
- `src/code/botlib/l_script.c`
- `src/code/botlib/l_script.h`
- `tests/test_botlib_parser_tail_coverage_parity.py`

## Pinned Parser Tail

| Address | Alias | Size | Source owner | Role |
| --- | --- | ---: | --- | --- |
| `0x004AA610` | `PC_EvaluateTokens` | `2689` | `l_precomp.c` | `#if` / `#elif` expression evaluator with operator precedence, `defined`, ternary, and divide-by-zero diagnostics. |
| `0x004AD4F0` | `PS_ReadEscapeCharacter` | `564` | `l_script.c` | Script string escape decoder for standard C escapes, hex escapes, and decimal character codes. |
| `0x004ADBA0` | `PS_ReadNumber` | `710` | `l_script.c` | Script lexer numeric scanner for hex, binary, octal/decimal, float, long, unsigned, and computed token values. |
| `0x004ADE70` | `PS_ReadPunctuation` | `176` | `l_script.c` | Script lexer punctuation scanner that walks the punctuation table, copies the matched syntax token, and records the punctuation subtype. |
| `0x004AE160` | `PS_ExpectTokenType` | `858` | `l_script.c` | Script token type/subtype validator and diagnostic formatter. |
| `0x004AE8A0` | `ReadNumber` | `1062` | `l_struct.c` | Structure-reader numeric conversion bridge for signed/unsigned, float, bounded char/int, and bounded float fields. |

## Source Findings

- `PC_EvaluateTokens` uses fixed local operator and value heaps, resets caller
  outputs before evaluation, accepts `defined` against the source define table,
  tracks unary minus and parentheses depth, rejects illegal float bitwise
  operators, evaluates the full arithmetic/logical/bitwise operator set, and
  preserves the ternary `? :` state machine visible in the HLIL.
- `PC_Evaluate` and `PC_DollarEvaluate` are the two source callers that feed
  expanded token lists into `PC_EvaluateTokens`, matching the retail callsites
  at `0x004AB3B0` and `0x004AB730`.
- `PS_ReadEscapeCharacter` performs the same pointer stepping and output-byte
  clamping shown in HLIL, including the distinct hex and decimal escape paths
  and the `unknown escape char` diagnostic.
- `PS_ReadNumber` matches the retained scanner shape, including the source's
  uppercase-hex branch, `BINARYNUMBERS` support, octal demotion when `8` or `9`
  appears, suffix handling, `NUMBERVALUE`, and final integer tagging for
  non-float values.
- 2026-06-11 recheck: `PS_ReadPunctuation` is now pinned directly. Retail HLIL
  walks the punctuation-table bucket for the current byte, compares candidate
  punctuation strings, copies the matching text, advances `script_p`, writes
  `TT_PUNCTUATION`, and records the punctuation subtype. The source keeps the
  same `PUNCTABLE` fast path plus fallback punctuation-list loop.
- `PS_ExpectTokenType` keeps the retail diagnostic map for token classes and
  numeric subtypes, plus the punctuation-subtype error path.
- 2026-06-11 recheck: the structure-reader `ReadNumber` row is tied back into
  this lower lexer gate so unsigned-minus rejection, unexpected punctuation,
  float/integer bounds, and typed numeric stores stay connected to
  `PS_ReadNumber` / `PS_ReadPunctuation` token semantics.

## 2026-06-11 Ghidra Bridge Recheck

The parser-tail gate now requires both Binary Ninja `sub_*` and Ghidra
`FUN_*` spellings for the selected rows:

- `FUN_004aa610` / `sub_4AA610 -> PC_EvaluateTokens`
- `FUN_004ad4f0` / `sub_4AD4F0 -> PS_ReadEscapeCharacter`
- `FUN_004adba0` / `sub_4ADBA0 -> PS_ReadNumber`
- `FUN_004ade70` / `sub_4ADE70 -> PS_ReadPunctuation`
- `FUN_004ae160` / `sub_4AE160 -> PS_ExpectTokenType`
- `FUN_004ae8a0` / `sub_4AE8A0 -> ReadNumber`

Detailed note:
`docs/reverse-engineering/botlib-parser-lexer-number-punctuation-bridge-recheck-2026-06-11.md`.

## 2026-06-11 Script Lifecycle/Loader Bridge

Follow-up mapping pinned the neighboring `l_script.c` lifecycle and loader band
with both Binary Ninja `sub_*` and Ghidra `FUN_*` spellings:

- `FUN_004ad230` / `sub_4AD230 -> PS_CreatePunctuationTable`
- `FUN_004ad320` / `sub_4AD320 -> ScriptError`
- `FUN_004ad390` / `sub_4AD390 -> ScriptWarning`
- `FUN_004ad400` / `sub_4AD400 -> PS_ReadWhiteSpace`
- `FUN_004ad7b0` / `sub_4AD7B0 -> PS_ReadString`
- `FUN_004ad920` / `sub_4AD920 -> PS_ReadName`
- `FUN_004ad9c0` / `sub_4AD9C0 -> NumberValue`
- `FUN_004adf30` / `sub_4ADF30 -> PS_ReadPrimitive`
- `FUN_004adfc0` / `sub_4ADFC0 -> PS_ReadToken`
- `FUN_004ae4c0` / `sub_4AE4C0 -> StripDoubleQuotes`
- `FUN_004ae520` / `sub_4AE520 -> StripSingleQuotes`
- `FUN_004ae580` / `sub_4AE580 -> SetScriptFlags`
- `FUN_004ae5a0` / `sub_4AE5A0 -> EndOfScript`
- `FUN_004ae5c0` / `sub_4AE5C0 -> LoadScriptFile`
- `FUN_004ae720` / `sub_4AE720 -> LoadScriptMemory`
- `FUN_004ae7e0` / `sub_4AE7E0 -> FreeScript`
- `FUN_004ae810` / `sub_4AE810 -> PS_SetBaseFolder`

The parity gate now checks the Ghidra row sizes, representative HLIL starts,
`l_script.h` prototypes, and source shapes for punctuation table construction,
diagnostics, whitespace/comment skipping, string/name/value parsing, primitive
and full token dispatch, quote stripping, script flags/end checks, file/memory
loader initialization, script freeing, and base-folder setup.

Detailed note:
`docs/reverse-engineering/botlib-script-lifecycle-loader-bridge-recheck-2026-06-11.md`.

## Coverage Result

`tests/test_botlib_parser_tail_coverage_parity.py` now includes a final scan
over promoted aliases in the support-tail band. After this pass there are no
promoted names in `0x004A83C0..0x004AF820` without a direct
`test_botlib_*.py` mention.

The much larger native cgame import slab after this range remains a separate
related-wiring surface and was intentionally not conflated with this botlib
parser pass.

## Parity Estimate

- Focused parser-tail promoted-alias coverage:
  **before 82% -> after 100%**
- Focused `PC_EvaluateTokens` source-shape coverage:
  **before 78% -> after 97%**
- Focused `l_script.c` escape/number/expect-type source-shape coverage:
  **before 74% -> after 96%**
- Overall botlib parser/support static mapping:
  **before 88% -> after 89%**

The overall movement is small because this pass closes evidence coverage over
already-reconstructed source rather than changing runtime behavior.
