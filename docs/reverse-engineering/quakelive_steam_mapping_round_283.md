# Quake Live Steam Host Mapping Round 283

Date: 2026-05-20

## Scope

This client round closes the remaining compact BSP collision-model load island
that sits under the client/cgame `CM_LoadMap` bridge, then names three adjacent
client wiring helpers that were still opaque in the Ghidra export:

- the `CMod_Load*` lump loaders at `0x004BF710..0x004BFE80`
- the small `CM_*` accessors/init helpers immediately after `CMod_LoadPatches`
- client configstring, pause, and advertisement visibility-trace helpers

Rounds 281 and 282 are already occupied by renderer command-buffer notes in
this worktree, so this client continuation uses round 283. No source behavior
changed.

## Evidence Used

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/qcommon/cm_load.c`
- `src/code/qcommon/cm_patch.c`
- `src/code/client/cl_main.c`
- `src/code/client/cl_cgame.c`
- `docs/reverse-engineering/quakelive_steam_mapping_round_13.md`

## Collision-Model Load Island

`CM_LoadMap` at `0x004C0580` calls the newly-promoted helpers in the same order
as the source loader:

1. shaders
2. leafs
3. leaf brushes
4. leaf surfaces
5. planes
6. brush sides
7. brushes
8. submodels
9. nodes
10. entity-string copy inlined inside `CM_LoadMap`
11. visibility
12. patches

The HLIL strings and table writes make these names high confidence. Examples:
`0x004BF710` emits `CMod_LoadShaders: funny lump size`, `0x004BF7A0` checks
`MAX_SUBMODELS exceeded`, `0x004BF9C0` reports
`CMod_LoadBrushes: bad shaderNum`, `0x004BFDD0` reports
`CMod_LoadBrushSides: bad shaderNum`, and `0x004BFE80` implements the
zero-length visibility fallback by allocating `(numClusters + 31) & ~31` bytes
and filling them with `0xff`.

## Promoted Symbols

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4B9430` | `CL_GetConfigStringValue` | High | Returns `cl.gameState.stringData + cl.gameState.stringOffsets[index]`; source now has the same helper shape for client configstring consumers. |
| `sub_4B9940` | `CL_IsClientPaused` | Medium-high | Reads `cl_paused` integer/value fields and returns whether the client pause cvar is active; consumed by `CL_SetCGameTime` and the timeout gate. |
| `sub_4B9DA0` | `CL_AdvertisementBridge_VisibilityTraceCallback` | Medium-high | Registered during client init through `AdvertisementBridge_SetVisibilityTraceCallback`; performs a `CM_BoxTrace` between two vectors and returns whether the trace fraction is below `1.0`. |
| `sub_4BF710` | `CMod_LoadShaders` | High | Validates `dshader_t` lump size `0x48`, rejects maps with no shaders, copies shader records, and fixes flags. |
| `sub_4BF7A0` | `CMod_LoadSubmodels` | High | Validates `dmodel_t` lump size `0x28`, expands mins/maxs by one unit, allocates per-model leaf brush/surface indexes, and enforces `MAX_SUBMODELS`. |
| `sub_4BF910` | `CMod_LoadNodes` | High | Validates node lump size `0x24`, requires at least one node, stores plane pointers and children. |
| `sub_4BF9C0` | `CMod_LoadBrushes` | High | Allocates brush records, resolves sides and shader numbers, validates shader bounds, copies contents, and derives bounds from side planes. |
| `sub_4BFAD0` | `CMod_LoadLeafs` | High | Validates leaf lump size `0x30`, requires leaves, copies cluster/area and leaf index spans, then allocates area portal tables. |
| `sub_4BFBD0` | `CMod_LoadPlanes` | High | Validates plane lump size `0x10`, copies normal/dist, computes plane type and signbits. |
| `sub_4BFCF0` | `CMod_LoadLeafBrushes` | High | Validates 4-byte index lump and copies leaf brush indexes. |
| `sub_4BFD60` | `CMod_LoadLeafSurfaces` | High | Validates 4-byte index lump and copies leaf surface indexes. |
| `sub_4BFDD0` | `CMod_LoadBrushSides` | High | Validates 8-byte side lump, resolves plane pointers, validates shader numbers, and stores surface flags. |
| `sub_4BFE80` | `CMod_LoadVisibility` | High | Implements both no-vis fallback and vis-header copy path for clusters and cluster bytes. |
| `sub_4C0160` | `CM_ClearMap` | High | Clears the clip map state and tailcalls `CM_ClearLevelPatches`. |
| `sub_4C0240` | `CM_NumInlineModels` | High | Returns the inline/submodel count directly. |
| `sub_4C0260` | `CM_LeafCluster` | High | Bounds-checks leaf index and returns the leaf cluster, with the exact `CM_LeafCluster: bad number` error. |
| `sub_4C02A0` | `CM_LeafArea` | High | Bounds-checks leaf index and returns the leaf area, with the exact `CM_LeafArea: bad number` error. |
| `sub_4C02E0` | `CM_InitBoxHull` | High | Builds the six-plane box hull, appends the body brush, and writes `CONTENTS_BODY`. |
| `sub_4C0830` | `CM_ClearLevelPatches` | Medium-high | Clears the two retained patch debug globals; source `CM_ClearLevelPatches` has the same debug-patch reset responsibility. |

## Wiring Notes

- `CMod_LoadEntityString` is not a separate retail function in this build. The
  entity-string allocation, copy, and count store are inlined inside
  `CM_LoadMap` immediately between `CMod_LoadNodes` and `CMod_LoadVisibility`.
- `CM_NumInlineModels` was already documented as a cgame native slot in round
  33; this round promotes the tiny host helper now that the call chain is
  anchored by the surrounding collision-model load table.
- `CL_AdvertisementBridge_VisibilityTraceCallback` is a synthetic source-style
  name. The registration and `CM_BoxTrace` behavior are observed, but the exact
  original C++ symbol name is not recoverable from the committed corpus.

## Guard Coverage

`tests/test_engine_client_command_parity.py` now checks the round 283 alias
set, validates the CSV-backed Ghidra rows, anchors the `CM_LoadMap` call order,
and cross-checks the source owners in `cm_load.c`, `cm_patch.c`, `cl_main.c`,
and `cl_cgame.c`.

## Parity Estimate

- Client/cgame collision-model load symbol coverage: before 86%, after 96%.
- Client host wiring symbol coverage for this tranche: before 91%, after 94%.
- Retail behavior parity: unchanged by this mapping-only round.
