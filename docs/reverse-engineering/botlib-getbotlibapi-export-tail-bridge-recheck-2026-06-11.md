# Botlib GetBotLibAPI Export Tail Bridge Recheck - 2026-06-11

## Scope

This round rechecked the retail Quake Live botlib export surface rooted at
`GetBotLibAPI` (`sub_4A83C0`) and focused on the public `botlib_export_t`
tail after the nested AAS, EA, and AI export tables.

Primary reconstructed files:

- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`
- `tests/test_botlib_internal_parity.py`

Primary evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- Ghidra functions table:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Promoted aliases:
  `references/analysis/quakelive_symbol_aliases.json`

## Observed Retail Facts

- `sub_4A83C0` copies the botlib import callback slab from the caller into
  `data_16dd800` with a `0x58` byte copy before clearing the export table at
  `data_16dd860` with a `0x224` byte memset.
- The API gate compares the requested version against literal `2`, prints the
  `Mismatched BOTLIB_API_VERSION` diagnostic on mismatch, and returns `0`.
- The retail initializer fills the nested export groups first:
  `sub_4A7FC0(&data_16dd860)`, `sub_4A8060(&data_16dd8b8)`, and
  `sub_4A8110(&data_16dd91c)`.
- The core export tail then assigns, in order:
  `Export_BotLibSetup`, `Export_BotLibShutdown`, `Export_BotLibVarSet`,
  `Export_BotLibVarGet`, `PC_AddGlobalDefine`, `PC_LoadSourceHandle`,
  `PC_FreeSourceHandle`, `PC_ReadTokenHandle`, `PC_SourceFileAndLine`,
  `Export_BotLibStartFrame`, `Export_BotLibLoadMap`,
  `Export_BotLibUpdateEntity`, and the tiny `sub_4D7970` test stub.
- Ghidra function rows are available for `sub_4A83C0` and most of the tail
  helpers, including the `PC_*` helpers and the `sub_4D7970` three-byte stub.
  The first two lifecycle wrappers are pinned here through HLIL and promoted
  alias evidence.

## Reconstruction Decision

The reconstructed source already matches this retail order:

- `BOTLIB_API_VERSION` remains `2`.
- `GetBotLibAPI` clears `be_botlib_export`, rejects mismatched API versions,
  fills `aas`, `ea`, and `ai`, then assigns the same tail helpers in the same
  order.
- `botlib_export_t` exposes the tail fields in the same order consumed by
  server/game botlib bridge code.

No source-code reconstruction was necessary for this lane. The useful closure
was a tighter parity gate:
`test_get_botlib_api_core_export_tail_matches_retail_table_order`.

## Confidence And Open Questions

- Focused `GetBotLibAPI` core export-tail confidence:
  **before 90% -> after 99%**.
- Focused botlib public export/import bridge coverage:
  **before 98% -> after 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.86% -> 83.90%**.

Remaining uncertainty is limited to live-map runtime behavior outside this
static export table; static source, Binary Ninja HLIL, Ghidra rows, and alias
evidence now agree for this public botlib API tail.
