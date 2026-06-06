# Botlib Server Import Bridge Recheck - 2026-06-05

## Scope

This pass rechecked the server-owned botlib import bridge in
`src/code/server/sv_bot.c` against the retail `quakelive_steam.exe` Binary
Ninja HLIL and Ghidra companion corpus. It covers the `BotImport_*` family,
`SV_BotInitBotLib`, debug polygon/line wiring, and the legacy qagame syscall
entry points that expose the bridge.

The 2026-06-05 source body already matched the recovered retail behavior, so
that round added parity evidence and notes instead of changing C code. A
2026-06-06 follow-up tightened one callback-table identity: retail assigns both
debug-line delete and debug-polygon delete to the same `sub_4dd430` thunk, so
`SV_BotInitBotLib` now assigns `DebugLineDelete` directly to
`BotImport_DebugPolygonDelete`.

## Observed Retail Facts

- Host HLIL at `0x004DD940` builds the `botlib_import_t` table in the same order
  as `src/code/game/botlib.h`: print, world trace, entity trace, point
  contents, PVS, BSP entity data, BSP model bounds, bot client commands, zone
  memory, available-memory, high-hunk allocation, filesystem calls, debug line
  calls, and debug polygon calls. It passes `2` as the botlib API version to
  the retail `GetBotLibAPI` analogue.
- `BotImport_Trace` and `BotImport_EntityTrace` call the retained server trace
  helpers with the final boolean argument set to `0`, then copy the same
  `bsp_trace_t` fields that the source writes: solid flags, fraction, endpos,
  plane, surface flags, entity number, and zeroed `exp_dist`, `sidenum`, and
  `contents`.
- The BSP entity data import is a direct retail tailcall from `0x004DD240` to
  `CM_EntityString`, matching the source wrapper `return CM_EntityString();`.
- `BotImport_BSPModelMinsMaxsOrigin` resolves the inline model, reads model
  bounds, expands rotated models with the radius-from-bounds path, writes
  optional mins/maxs, and clears optional origin to zero.
- The debug polygon allocator starts at slot `1`, respects
  `bot_maxdebugpolys`, writes the in-use/color/point-count fields, and copies
  `numPoints * sizeof(vec3_t)`. The debug line creator delegates to the same
  allocator with a zero-point polygon, and debug-line show stores a four-point
  quad after expanding the line by two units along the perpendicular vector.
- Retail initializes both the debug-line delete callback (`var_14`) and the
  debug-polygon delete callback (`var_8`) to `sub_4dd430`, the promoted
  `BotImport_DebugPolygonDelete` helper.
- `BotDrawDebugPolygons` forwards `bot_highlightarea` through the botlib var
  import and calls botlib `Test` with the attack, reachability, and ground-only
  bitmask before drawing active debug polygons.

## Source Confirmation

No source reconstruction was required in this pass. The following source owners
already match the retail evidence:

- `SV_BotInitBotLib`, including the shared retail delete-thunk assignment for
  `DebugLineDelete` and `DebugPolygonDelete`
- `BotImport_Trace`
- `BotImport_EntityTrace`
- `BotImport_BSPEntityData`
- `BotImport_BSPModelMinsMaxsOrigin`
- `BotImport_DebugPolygonCreate`
- `BotImport_DebugLineCreate`
- `BotImport_DebugLineShow`
- `BotDrawDebugPolygons`
- `SV_GameSystemCallsImpl` cases for qagame debug polygon and botlib setup

## Changes

- Added
  `test_engine_cvar_thirtyfourth_server_botlib_import_bridge_matches_retail_contracts`
  in `tests/test_engine_cvar_retail_parity.py`.
- Added the 2026-06-06 focused callback-surface gate
  `tests/test_botlib_import_callback_surface_parity.py`.
- The test pins:
  - the alias map entries from `sub_4DD0B0` through `sub_4DD940`,
  - the `botlib_import_t` source field order,
  - the source import assignment order in `SV_BotInitBotLib`,
  - the retail HLIL import table at `0x004DD940`,
  - the trace and entity-trace copy contract,
  - the direct `CM_EntityString` tailcall,
  - the debug polygon and debug line storage behavior,
  - the qagame legacy syscall bridge for debug polygons and `BOTLIB_SETUP`.
- The follow-up callback-surface gate also pins the shared
  `sub_4dd430` delete thunk and keeps the source assignment from drifting back
  to a separate wrapper pointer.

## Open Questions

- This round did not re-open `SV_BotAllocateClient` or `SV_BotFreeClient`.
  Those owners remain covered by the earlier mapping round and by the active bot
  entity-state reconstruction work.
- The import bridge is host/server-owned; deeper botlib internal helpers still
  need separate evidence when new discrepancies are suspected.

## Parity Estimate

- Focused server botlib import bridge evidence: `82% -> 96%`.
- Overall botlib plus related wiring: approximately `65% -> 66%`.
