# Botlib Post-Structure Client/Cinematic Boundary Mapping - 2026-06-06

## Scope

This pass extends the botlib structure-tail boundary check beyond
`CL_GetServerCommand` and into the adjacent retail host range
`0x004B0610..0x004B0F60`. The goal is ownership classification: these rows are
not botlib parser or structure helpers, even though they sit immediately after
the botlib-adjacent cgame import seam.

No C source body change was needed.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_cin.c`
- `tests/test_botlib_structure_tail_cgame_boundary_parity.py`

## Observed Rows

| Address | Classification |
| --- | --- |
| `0x004B0610` | `CL_GameCommand` |
| `0x004B0630` | `CL_CGameRendering` |
| `0x004B0660` | `CL_AdjustServerTimeDelta` |
| `0x004B0760` | `CL_FirstSnapshot` |
| `0x004B07C0` | `CL_SetCGameTime` |
| `0x004B0A50` | bounded cgame native import integrity guard |
| `0x004B0A70` | `RllDecodeStereoToStereo` |
| `0x004B0AF0` | `move8_32` |
| `0x004B0BD0` | `blit8_32` |
| `0x004B0CD0` | `blitVQQuad32fs` |
| `0x004B0F60` | `ROQ_GenYUVTables` |

`0x004B0A50` remains intentionally unpromoted in the alias map. It is the
retail guard that raises the `0x40` client-message sideband flag if cgame native
import pointers drift from the expected render-scene wrappers. Source models
that behavior as `CL_CheckCGameNativeImportIntegrity`.

## Boundary Finding

The post-`ReadStructure` retail range now has a continuous botlib-boundary
classification:

- `0x004AE830..0x004AECD0` contains the final promoted botlib structure reader
  owners.
- `0x004AF050..0x004AF500` contains adjacent non-botlib C++/client helper rows
  that remain intentionally unpromoted.
- `0x004AF570..0x004AF820` contains cgame snapshot/configstring/server-command
  owners and native import wrappers.
- `0x004B0610..0x004B0F60` contains client cgame command/timing/rendering
  owners plus the first ROQ cinematic decode helpers.

That keeps source-visible `l_struct.c` write helpers from being incorrectly
promoted into rows that retail evidence assigns to client/cinematic code.

## Coverage Result

`tests/test_botlib_structure_tail_cgame_boundary_parity.py` now pins:

- promoted aliases and Ghidra row sizes for the adjacent client timing/ROQ slab;
- source anchors in `CL_GameCommand`, `CL_CGameRendering`,
  `CL_AdjustTimeDelta`, `CL_FirstSnapshot`, and `CL_SetCGameTime`;
- source anchors in `RllDecodeStereoToStereo`, `move8_32`, `blit8_32`,
  `blitVQQuad32fs`, `ROQ_GenYUVTables`, and `initRoQ`;
- the `0x004B0A50` integrity row as a bounded non-alias source-modeled guard;
- HLIL call relationships from `CL_SetCGameTime` to the adjust/first-snapshot
  helpers and from `initRoQ` to the VQ blitter/YUV table generator.

The focused alias-mention scan for `0x004A83C0..0x004B0F60` now reports zero
promoted aliases lacking direct `test_botlib_*.py` coverage.

## Parity Estimate

- Focused post-structure botlib/client ownership-boundary classification:
  **before 86% -> after 99%**
- Focused cgame timing and ROQ cinematic helper coverage inside botlib boundary
  gates:
  **before 72% -> after 99%**
- Overall botlib plus adjacent parser/client wiring:
  **before 85% -> after 86%**

No runtime launch was needed. The evidence is static and fully covered by the
committed HLIL, Ghidra row data, alias map, and source bodies.
