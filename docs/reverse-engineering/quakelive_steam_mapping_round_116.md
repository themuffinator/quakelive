# Quake Live Steam Host Mapping Round 116

## Scope

This round continues directly from
[Round 115](./quakelive_steam_mapping_round_115.md) and takes the refreshed
largest-unaliased `quakelive_steam.exe` queue beginning with `sub_4C2170`,
`sub_521270`, and `sub_48FC10`. Each candidate was classified before opening
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
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- matching owners under `src/code/qcommon/`, `src/code/botlib/`, and
  `src/libs/_deps/libvorbis/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4C2170` | `2388` | `engine-owned` | `CM_PatchCollideFromGrid` alias added | High | No new debt opened; source owner already exists in `cm_patch.c`. |
| 2 | `sub_521270` | `2362` | `CRT/STL` | `mapping0_forward` alias added | High | No engine debt; bundled libvorbis mapping encoder support. |
| 3 | `sub_48FC10` | `2330` | `engine-owned` | `AAS_Reachability_JumpPad` alias added | High | No new debt opened; source owner already exists in `be_aas_reach.c`. |

Bucket summary:

- `engine-owned`: 2 of 3
- `platform-service-owned`: 0 of 3
- `CRT/STL`: 1 of 3
- `Awesomium`: 0 of 3
- `Steam SDK support`: 0 of 3

## Evidence Notes

### `sub_4C2170 -> CM_PatchCollideFromGrid`

`sub_4C2170` is the collision patch facet builder called by the next HLIL
function, `sub_4C2AE0`, after it validates `CM_GeneratePatchFacets` parameters
and constructs the `cGrid_t` working grid. The body resets the global patch
plane/facet counters, fills `gridPlanes[MAX_GRID_SIZE][MAX_GRID_SIZE][2]`,
creates top/bottom/left/right border planes, emits `MAX_FACETS`, validates and
bevels facets, then copies the generated facets and planes into the output
`patchCollide_t`.

The local source owner is `src/code/qcommon/cm_patch.c:980`, where
`CM_PatchCollideFromGrid` performs the same `CM_FindPlane`,
`CM_EdgePlaneNum`, `CM_SetBorderInward`, `CM_ValidateFacet`, and
`CM_AddFacetBevels` sequence before allocating `pf->facets` and `pf->planes`
with `Hunk_Alloc`. This is retained engine collision behavior.

### `sub_521270 -> mapping0_forward`

`sub_521270` is the fourth callback in the libvorbis mapping backend table:
`data_583BB0` through `data_583BC0` line up as pack, unpack, free, forward,
and inverse. Its body matches `mapping0_forward`, not `mapping0_inverse`: it
allocates per-channel MDCT/log-mask work arrays, applies the Vorbis analysis
window, runs MDCT/FFT analysis, computes noise and tone masks, performs floor1
fits and bitrate-management interpolation, writes packet blobs, quantizes and
couples channels, and dispatches residue `class` and `forward` callbacks.

The local source owner is `src/libs/_deps/libvorbis/lib/mapping0.c:230`.
Because this is statically linked bundled libvorbis support, it is classified
as `CRT/STL` for this audit lane and does not open engine source debt.

### `sub_48FC10 -> AAS_Reachability_JumpPad`

`sub_48FC10` matches botlib jump-pad reachability generation. The HLIL and
Ghidra decompile start by reading `bot_visualizejumppads`, enumerate BSP
entities with `classname == "trigger_push"`, call the jump-pad info helper,
link the trigger bounds into AAS areas, require an `AREACONTENTS_JUMPPAD`
area, emit the preserved diagnostics for missing jump-pad areas and trigger
velocity, then build `TRAVEL_JUMPPAD` reachabilities including team filters and
the normal/air-controlled jump-pad travel times.

The local source owner is `src/code/botlib/be_aas_reach.c:3499`. The
reachability scheduler calls it during the final storage phase after walk-off
ledge reachabilities and before teleporter, elevator, and func_bobbing
reachabilities, matching the host caller chain around `sub_48FC10`.

## New High-Confidence Aliases Added This Round

- `sub_4C2170 -> CM_PatchCollideFromGrid`
- `sub_521270 -> mapping0_forward`
- `sub_48FC10 -> AAS_Reachability_JumpPad`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1165` raw alias entries, `1164` address-backed
  alias entries
- top remaining unaliased function by size: `sub_470200` at `2317` bytes

## Completion Stats After Round 116

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1165` raw alias entries, `1164` address-backed
  aliases
- Address-backed coverage: `21.268%` of `5473` functions
- Alias delta this round: `3`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the former top
three unaliased entries as two retained engine functions with existing source
owners and one bundled libvorbis mapping-encoder function, leaving the next
host queue headed by `sub_470200`.
