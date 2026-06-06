# Botlib Import Callback Surface Mapping - 2026-06-06

## Scope

This pass rechecked the engine-to-botlib callback table built by
`SV_BotInitBotLib` and consumed by `GetBotLibAPI`. The slice covers the
`botlib_import_t` layout, server callback assignment order, retail HLIL local
table at `0x004DD940`, and the debug line/polygon callback identity.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/game/botlib.h`
- `src/code/server/sv_bot.c`
- `tests/test_botlib_import_callback_surface_parity.py`

## Source Reconstruction

Retail `SV_BotInitBotLib` initializes both the debug-line delete callback
(`var_14`) and debug-polygon delete callback (`var_8`) to `sub_4dd430`.
`sub_4dd430` is the promoted `BotImport_DebugPolygonDelete` thunk.

The source previously assigned `DebugLineDelete` to the trivial
`BotImport_DebugLineDelete` wrapper, which then called
`BotImport_DebugPolygonDelete`. That was behaviorally equivalent, but it did
not preserve the retail callback-table function identity. The source now sets:

```c
botlib_import.DebugLineDelete = BotImport_DebugPolygonDelete;
```

The wrapper remains available as a compatibility helper, but the botlib import
table now matches the retail pointer identity.

## Observed Facts

- `0x004DD940` builds the callback table in `botlib_import_t` order and passes
  API version `2` to the retail `GetBotLibAPI` analogue at `0x004A83C0`.
- The table locals map to print, trace, entity trace, point contents, PVS,
  BSP entity data, BSP model bounds, bot client command, memory, filesystem,
  debug line, and debug polygon callbacks.
- `BotImport_BSPEntityData` is a tailcall to the engine entity string owner.
- `BotImport_BSPModelMinsMaxsOrigin` resolves an inline model, expands rotated
  bounds with `RadiusFromBounds`, writes optional mins/maxs, and clears
  optional origin.
- `BotImport_HunkAlloc` rejects allocation while hunk marks are set and then
  allocates from the high hunk.
- `BotImport_DebugLineCreate` creates a zero-point polygon, and
  `BotImport_DebugLineShow` updates that line id through
  `BotImport_DebugPolygonShow` with a four-point polygon widened by two units
  along the perpendicular.

## Coverage Result

`tests/test_botlib_import_callback_surface_parity.py` now pins:

- promoted aliases and Ghidra row sizes for the callback surface;
- the retail HLIL local callback table at `0x004DD940`;
- `botlib_import_t` declaration order;
- `SV_BotInitBotLib` assignment order;
- the shared retail delete thunk for line and polygon delete;
- source body anchors for trace copying, BSP metadata, memory, and debug
  line/polygon callbacks.

The broader botlib parity gates were also normalized to read Ghidra
`functions.csv` rows from the committed
`references/reverse-engineering/ghidra/quakelive_steam/` corpus. Alias-map
lookups remain on `quakelive_steam_srp`, which is the promoted symbol key
present in `references/analysis/quakelive_symbol_aliases.json`.

## Parity Estimate

- Focused botlib import callback surface:
  **before 94% -> after 99%**
- Focused debug line/polygon callback identity:
  **before 85% -> after 99%**
- Overall botlib plus related server/game wiring:
  **before 97% -> after 97%**

No runtime launch was needed. The committed HLIL, Ghidra rows, alias map, and
source callback table settle this bridge statically.
