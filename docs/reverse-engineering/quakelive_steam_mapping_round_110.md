# Quake Live Steam Host Mapping Round 110

## Scope

This round continues directly from
[Round 109](./quakelive_steam_mapping_round_109.md) and takes the largest
currently unaliased `quakelive_steam.exe` functions first. The pass classifies
each candidate before opening source debt, so large retained library bodies do
not get mistaken for missing engine code.

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
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- matching owners under `src/code/` and `src/libs/_deps/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4728D0` | `8865` | `engine-owned` | `QGL_Init` alias added | High | No debt opened; retained Win32 QGL loader owner exists. |
| 2 | `sub_470B40` | `7528` | `engine-owned` | `QGL_EnableLogging` alias added | High | No debt opened; retained QGL logging owner exists. |
| 3 | `sub_4896E0` | `6429` | `engine-owned` | `AAS_Reachability_Step_Barrier_WaterJump_WalkOffLedge` alias added | High | No debt opened; retained botlib reachability owner exists. |
| 4 | `sub_4FDE10` | `5466` | `CRT/STL` | `inflate` alias added | High | No engine debt; zlib support-library body. |
| 5 | `sub_51E4F0` | `5099` | `CRT/STL` | Deferred exact alias | Medium | No engine debt opened; likely codec FFT/MDCT support helper, but exact upstream name is not proven. |
| 6 | `sub_5049D0` | `4761` | `CRT/STL` | `png_read_info` alias added | High | No engine debt; libpng support-library body. |
| 7 | `sub_507DD0` | `4001` | `CRT/STL` | `png_do_compose` alias added | High | No engine debt; libpng row-transform helper. |
| 8 | `sub_439E20` | `3882` | `engine-owned` | `R_StitchPatches` alias added | High | No debt opened; retained renderer BSP patch-stitch owner exists. |
| 9 | `sub_48C980` | `3809` | `engine-owned` | `AAS_Reachability_Ladder` alias added | High | No debt opened; retained botlib ladder-reachability owner exists. |
| 10 | `sub_4872E0` | `3752` | `engine-owned` | `AAS_ClientMovementPrediction` alias added | High | No debt opened; retained botlib movement prediction owner exists. |

Bucket summary:

- `engine-owned`: 6 of 10
- `platform-service-owned`: 0 of 10
- `CRT/STL`: 4 of 10
- `Awesomium`: 0 of 10
- `Steam SDK support`: 0 of 10

## Evidence Notes

### QGL Loader Pair

`sub_4728D0` is the retained `QGL_Init` owner. HLIL shows the Win32 OpenGL load
path with `GetSystemDirectoryA`, `LoadLibraryA`, the `"opengl32"` and
`"3dfxvgl"` branches, `Glide3X` handling, and the long `GetProcAddress` table
for `glAccum`, `glAlphaFunc`, and the rest of the QGL entrypoints. The source
owner is `src/code/win32/win_qgl.c:3235`.

`sub_470B40` is the retained `QGL_EnableLogging` owner. Its evidence is the
`r_logFile` toggle, `fs_basepath/gl.log` write path, the
`"*** CLOSING LOG ***\n"` close marker, and pointer swaps between normal QGL
entrypoints and logging wrappers. The source owner is
`src/code/win32/win_qgl.c:3647`.

### AAS Reachability And Movement

`sub_4896E0` matches
`AAS_Reachability_Step_Barrier_WaterJump_WalkOffLedge`. It walks AAS area
faces and edges, creates local reachability records, checks
`AAS_MAX_REACHABILITYSIZE`, and emits the retained walk, waterjump,
barrier-jump, and walk-off-ledge travel types. The source owner is
`src/code/botlib/be_aas_reach.c:1059`.

`sub_48C980` matches `AAS_Reachability_Ladder`. The body requires ladder area
flags on both candidate areas, searches the shared ladder edge/face geometry,
checks vertical ladder-plane constraints, and creates retained ladder and
fallback travel reachabilities. The source owner is
`src/code/botlib/be_aas_reach.c:2380`.

`sub_4872E0` matches `AAS_ClientMovementPrediction`. The body consumes the
retained `aassettings` movement constants, initializes prediction state, runs
the movement loop, traces the client bounds, and preserves the
`"PredictMovement: start solid\n"` diagnostic. The source owner is
`src/code/botlib/be_aas_move.c:505`.

### Renderer BSP Patch Stitching

`sub_439E20` matches `R_StitchPatches`. The local caller cluster walks
`SF_GRID` surfaces and prints `"stitched %d LoD cracks\n"` after repeated
stitch attempts. The function itself compares grid edge control points,
applies the retained `MAX_GRID_SIZE` guard, calls the row/column insertion
helpers, and clears the patch stitch state after a successful repair. The
source owner is `src/code/renderer/tr_bsp.c:726`.

### Bundled Support Libraries

`sub_4FDE10` is zlib `inflate`. The body is the large inflate state machine and
carries the retained zlib diagnostics including `"incorrect header check"`,
`"unknown compression method"`, `"invalid block type"`, `"incorrect data check"`,
and `"incorrect length check"`. The source owner is
`src/libs/_deps/zlib/inflate.c:590`.

`sub_5049D0` is libpng `png_read_info`. It reads and validates the PNG
signature, recognizes the retained chunk set (`IHDR`, `IDAT`, `IEND`, `PLTE`,
`gAMA`, `iCCP`, `sRGB`, `tEXt`, `zTXt`, and others), and emits the retained
PNG sequencing errors. The source owner is `src/libs/_deps/libpng/pngread.c:91`.

`sub_507DD0` is libpng `png_do_compose`. It applies the retained transparency
and background-composition transform over gray, RGB, gray-alpha, and RGBA rows,
including bit-depth-specific paths and gamma-table use. The source owner is
`src/libs/_deps/libpng/pngrtran.c:3320`.

`sub_51E4F0` is classified as `CRT/STL` support-library code, but it remains
unnamed. HLIL shows a large floating-point transform helper called from a
factorized transform dispatcher with radix-specific neighbors and `_CIcos` /
`_CIsin` twiddle-factor work. That points to bundled audio codec transform
support rather than engine behavior, but this round does not have enough exact
upstream evidence to assign a stable symbol name.

## New High-Confidence Aliases Added This Round

- `sub_439E20 -> R_StitchPatches`
- `sub_470B40 -> QGL_EnableLogging`
- `sub_4728D0 -> QGL_Init`
- `sub_4872E0 -> AAS_ClientMovementPrediction`
- `sub_4896E0 -> AAS_Reachability_Step_Barrier_WaterJump_WalkOffLedge`
- `sub_48C980 -> AAS_Reachability_Ladder`
- `sub_4FDE10 -> inflate`
- `sub_5049D0 -> png_read_info`
- `sub_507DD0 -> png_do_compose`

## Deferred Candidate

`sub_51E4F0` should stay in the largest-unaliased queue until a future audio
support-library pass can anchor the exact symbol name. The important outcome
for this round is that it is not engine-owned source debt.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1147` raw alias entries, `1146` address-backed
  alias entries
- top remaining unaliased function by size: `sub_51E4F0` at `5099` bytes

## Completion Stats After Round 110

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1147` raw alias entries, `1146` address-backed
  aliases
- Address-backed coverage: `20.939%` of `5473` functions
- Alias delta this round: `9`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It closes six retained engine
owners and three support-library owners, and it classifies one remaining large
support-library body for later naming.
