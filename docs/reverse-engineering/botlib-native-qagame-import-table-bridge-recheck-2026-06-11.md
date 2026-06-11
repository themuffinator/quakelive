# Botlib native qagame import table bridge recheck - 2026-06-11

## Scope

This pass rechecked the host-to-native-qagame botlib import bridge rather than
individual bot behavior. The target was the retail Quake Live native import
table range that begins with bot client allocation/debug helpers and continues
through the full botlib, AAS, EA, character/chat, goal, movement, weapon, and
genetic-selection wrapper surface.

## Retail evidence

Observed Binary Ninja HLIL evidence in
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`:

- Native qagame slot `43` is table row `0x0056d02c`, pointing at
  `j_sub_4dcd30`.
- Native qagame slot `184` is table row `0x0056d260`, pointing at
  `sub_4e2600`.
- The full botlib bridge range is contiguous: slots `43..184`, table rows
  `0x0056d02c..0x0056d260`, 142 rows total.
- Sentinel rows match the expected subsystem boundaries:
  `BOTLIB_UPDATE_ENTITY` at slot `56`, AAS at slot `61`, debug draw at slot
  `83`, EA at slot `85`, AI character loading at slot `110`, goal reset at slot
  `137`, movement reset at slot `166`, weapon choice at slot `178`, and genetic
  parent/child selection at slot `184`.
- Slot `185` immediately leaves the botlib bridge and points at the qagame
  match-report import (`sub_4e2620`), confirming the upper boundary.

Companion Ghidra evidence remains the per-wrapper function-row corpus in
`references/reverse-engineering/ghidra/quakelive_steam/functions.csv`, already
pinned by the narrower AAS, EA, movement, weapon, and server bridge tests. This
round adds the missing whole-range table guard across those individual slices.

## Source reconstruction status

`src/code/game/g_public.h` already exposes the native import ordinals from
`G_QL_IMPORT_BOT_ALLOCATE_CLIENT = 43` through
`G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION = 184`.

`src/code/server/sv_game.c` already initializes each corresponding
`ql_game_imports[...]` entry in the same order. No source change was needed.

The reconstruction change is a stronger executable parity gate in
`tests/test_botlib_server_game_bridge_parity.py`:

- parses the native bridge enum rows from `g_public.h`;
- verifies slots `43..184` are contiguous and count to `142`;
- verifies every slot has a matching `SV_InitGameImports` assignment;
- verifies every slot has a matching retail HLIL table row;
- pins representative table sentinels and the slot-185 post-botlib boundary.

## Confidence

- Focused native qagame botlib import-table bridge: **88% -> 99%**.
- Focused server/qagame botlib wiring coverage: **98% -> 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.82% -> 83.86%**.

Remaining uncertainty lies in behavior inside later qagame AI decision helpers,
not in this native import-table bridge.
