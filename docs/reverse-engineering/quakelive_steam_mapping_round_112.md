# Quake Live Steam Host Mapping Round 112

## Scope

This round continues directly from
[Round 111](./quakelive_steam_mapping_round_111.md) and takes the refreshed
largest-unaliased `quakelive_steam.exe` queue beginning with `sub_4B1100`,
`sub_48B0E0`, and `sub_48BD40`. Each candidate was classified before opening
source debt.

Classification buckets for this round:

- `engine-owned`: retained Quake III or Quake Live engine behavior with a
  matching source owner.
- `platform-service-owned`: Quake Live service glue outside normal engine
  ownership.
- `CRT/STL`: CRT, STL, or bundled third-party support-library code statically
  linked into the host binary.
- `Awesomium`: browser runtime or Awesomium support code.
- `Steam SDK support`: Steamworks SDK callback, helper, or support code.

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- matching owners under `src/code/client/` and `src/code/botlib/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4B1100` | `3172` | `engine-owned` | `decodeCodeBook` alias added | High | No debt opened; retained client RoQ cinematic codebook owner exists. |
| 2 | `sub_48B0E0` | `3155` | `engine-owned` | `AAS_ClosestEdgePoints` alias added | High | No debt opened; retained botlib reachability geometry owner exists. |
| 3 | `sub_48BD40` | `3118` | `engine-owned` | `AAS_Reachability_Jump` alias added | High | No debt opened; retained botlib jump-reachability owner exists. |

Bucket summary:

- `engine-owned`: 3 of 3
- `platform-service-owned`: 0 of 3
- `CRT/STL`: 0 of 3
- `Awesomium`: 0 of 3
- `Steam SDK support`: 0 of 3

## Evidence Notes

### `sub_4B1100 -> decodeCodeBook`

`sub_4B1100` matches the retained client RoQ `decodeCodeBook` helper. The
caller dispatches the cinematic chunk ID `0x1002` (`ROQ_CODEBOOK`) to this
function, and the body expands 2x2 VQ codebook entries into `vq2`, `vq4`, and
`vq8` tables. It branches on the cinematic handle's `half`,
`smootheddouble`, and `samplesPerPixel` fields and uses the retained
`yuv_to_rgb`, `yuv_to_rgb24`, gray-table, and `VQ2TO4` paths.

The source owner is `src/code/client/cl_cin.c:1116`. The source caller is
`RoQInterrupt`, which dispatches `ROQ_CODEBOOK` to `decodeCodeBook` at
`src/code/client/cl_cin.c:1641`. This is engine-owned client cinematic code,
and the retained source owner is already present.

### `sub_48B0E0 -> AAS_ClosestEdgePoints`

`sub_48B0E0` matches botlib `AAS_ClosestEdgePoints`. The body subtracts the
two edge vectors, projects the edge endpoints onto the opposite edge, restores
z from the two face planes, checks whether projected points lie between the
edge endpoints, and updates the paired best-start/best-end ranges when
distances fall within the retained `0.5` tolerance.

The source owner is `src/code/botlib/be_aas_reach.c:1831`. Its call shape in
the host binary is the same as the retained jump-reachability path: area edge
vertices, two face planes, paired best-start/best-end vectors, and the current
best distance. This is engine-owned botlib geometry code, and the retained
source owner is already present.

### `sub_48BD40 -> AAS_Reachability_Jump`

`sub_48BD40` matches botlib `AAS_Reachability_Jump`. The body requires both
areas to be grounded, rejects crouch areas, computes maximum jump distance and
height from `phys_jumpvel`, walks ground faces and edges in both areas, calls
`AAS_ClosestEdgePoints`, tests walkoff/jump feasibility with
`AAS_HorizontalVelocityForJump`, traces the candidate endpoints, predicts
movement with jump or walkoff commands, and allocates a reachability link with
`TRAVEL_JUMP` or `TRAVEL_WALKOFFLEDGE`.

The source owner is `src/code/botlib/be_aas_reach.c:2109`. The source
reachability builder calls it from `src/code/botlib/be_aas_reach.c:4417`,
matching the host caller sequence around the neighboring ladder and step
reachability functions. This is engine-owned botlib reachability code, and the
retained source owner is already present.

## New High-Confidence Aliases Added This Round

- `sub_48B0E0 -> AAS_ClosestEdgePoints`
- `sub_48BD40 -> AAS_Reachability_Jump`
- `sub_4B1100 -> decodeCodeBook`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1153` raw alias entries, `1152` address-backed
  alias entries
- top remaining unaliased function by size: `sub_514550` at `2980` bytes

## Completion Stats After Round 112

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1153` raw alias entries, `1152` address-backed
  aliases
- Address-backed coverage: `21.049%` of `5473` functions
- Alias delta this round: `3`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the former top
three unaliased entries as retained engine-owned client cinematic and botlib
reachability code with existing source owners, leaving the next host queue
headed by `sub_514550`.
