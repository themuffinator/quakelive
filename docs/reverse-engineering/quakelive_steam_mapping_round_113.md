# Quake Live Steam Host Mapping Round 113

## Scope

This round continues directly from
[Round 112](./quakelive_steam_mapping_round_112.md) and takes the refreshed
largest-unaliased `quakelive_steam.exe` queue beginning with `sub_514550`,
`sub_519D10`, and `sub_48F0C0`. Each candidate was classified before opening
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
- matching owners under `src/libs/_deps/libpng/`, `src/libs/_deps/libvorbis/`,
  and `src/code/botlib/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_514550` | `2980` | `CRT/STL` | `png_write_find_filter` alias added | High | No debt opened; bundled libpng write-filter support code. |
| 2 | `sub_519D10` | `2917` | `CRT/STL` | `bark_noise_hybridmp` alias added | High | No debt opened; bundled libvorbis psychoacoustic noise-mask support code. |
| 3 | `sub_48F0C0` | `2847` | `engine-owned` | `AAS_Reachability_FuncBobbing` alias added | High | No debt opened; retained botlib func_bobbing reachability owner exists. |

Bucket summary:

- `engine-owned`: 1 of 3
- `platform-service-owned`: 0 of 3
- `CRT/STL`: 2 of 3
- `Awesomium`: 0 of 3
- `Steam SDK support`: 0 of 3

## Evidence Notes

### `sub_514550 -> png_write_find_filter`

`sub_514550` matches bundled libpng `png_write_find_filter`. The body reads
PNG row metadata, computes `bpp = (pixel_depth + 7) >> 3`, tests the write
filter mask, evaluates `SUB`, `UP`, `AVG`, and `PAETH` candidate rows, and
selects the lowest-cost filtered row before handing it to the write path.

The source owner is `src/libs/_deps/libpng/pngwutil.c:2594`. The retained
source performs the same write-filter selection and candidate-row scoring.
This is bundled third-party support-library code, not engine-owned Quake Live
behavior.

### `sub_519D10 -> bark_noise_hybridmp`

`sub_519D10` matches bundled libvorbis `bark_noise_hybridmp`. The function
allocates five `n`-sized float work arrays, builds cumulative weighted sums for
the input curve after applying an offset and a minimum value of `1.0`, derives
least-squares line coefficients over bark-window ranges, clamps negative
results, writes `noise[i] = R - offset`, and optionally applies the fixed
window pass when `fixed > 0`.

The source owner is `src/libs/_deps/libvorbis/lib/psy.c:543`. Its caller
`_vp_noisemask` invokes it first with `offset = 140.0` and `fixed = -1`, then
again with `offset = 0.0` and `p->vi->noisewindowfixed`, matching the HLIL
call sites around `sub_51a990`. This is bundled third-party support-library
code, not engine-owned Quake Live behavior.

### `sub_48F0C0 -> AAS_Reachability_FuncBobbing`

`sub_48F0C0` matches botlib `AAS_Reachability_FuncBobbing`. The body iterates
BSP entities, filters for `classname == "func_bobbing"`, reads `height`,
`model`, optional origin, and `spawnflags`, derives the mover start/end bounds,
logs `funcbob` reachability diagnostics, finds start/end areas, allocates
reachability records, sets `TRAVEL_FUNCBOB`, and uses
`aassettings.rs_funcbob` for travel time.

The source owner is `src/code/botlib/be_aas_reach.c:3285`. The reachability
builder calls it from `src/code/botlib/be_aas_reach.c:4471`, matching the host
caller sequence among other AAS reachability constructors. This is retained
engine-owned botlib behavior with an existing source owner.

## New High-Confidence Aliases Added This Round

- `sub_48F0C0 -> AAS_Reachability_FuncBobbing`
- `sub_514550 -> png_write_find_filter`
- `sub_519D10 -> bark_noise_hybridmp`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1156` raw alias entries, `1155` address-backed
  alias entries
- top remaining unaliased function by size: `sub_4AA610` at `2689` bytes

## Completion Stats After Round 113

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1156` raw alias entries, `1155` address-backed
  aliases
- Address-backed coverage: `21.104%` of `5473` functions
- Alias delta this round: `3`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the former top
three unaliased entries as two bundled support-library functions and one
retained engine-owned botlib reachability function with an existing source
owner, leaving the next host queue headed by `sub_4AA610`.
