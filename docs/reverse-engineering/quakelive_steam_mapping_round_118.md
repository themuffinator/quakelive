# Quake Live Steam Host Mapping Round 118

## Scope

This round continues directly from
[Round 117](./quakelive_steam_mapping_round_117.md) and takes an expanded pass
over the refreshed largest-unaliased `quakelive_steam.exe` queue. The pass
began with `sub_41D720`, `sub_43E030`, and `sub_4A4A50`, then continued
through the next largest high-confidence candidates before opening any source
debt.

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
- matching owners under `src/code/renderer/`, `src/code/win32/`,
  `src/code/botlib/`, and `src/libs/_deps/zlib/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_41D720` | `2096` | `platform-service-owned` | `zmq_signaler_t_make_fdpair` alias added | High | No engine debt; bundled ZeroMQ signaler support. |
| 2 | `sub_43E030` | `2080` | `engine-owned` | `R_SubdividePatchToGrid` alias added | High | No new debt; source owner already exists in `tr_curve.c`. |
| 3 | `sub_4A4A50` | `2056` | `engine-owned` | `BotMoveToGoal` alias added | High | No new debt; source owner already exists in `be_ai_move.c`. |
| 4 | `sub_4FF4D0` | `2014` | `CRT/STL` | `deflate` alias added | High | No engine debt; bundled zlib compression support. |
| 5 | `sub_43D350` | `1991` | `engine-owned` | `MakeMeshNormals` alias added | High | No new debt; source owner already exists in `tr_curve.c`. |
| 6 | `sub_4423E0` | `1872` | `CRT/STL` | `stbtt__GetGlyphShapeTT` alias added | Medium-high | No engine debt; fontstash/stb TrueType support. |
| 7 | `sub_4957F0` | `1858` | `engine-owned` | `AAS_TraceClientBBox` alias added | High | No new debt; source owner already exists in `be_aas_sample.c`. |
| 8 | `sub_4401E0` | `1851` | `CRT/STL` | `stbtt__fill_active_edges_new` alias added | Medium-high | No engine debt; fontstash/stb raster support. |
| 9 | `sub_46B060` | `1849` | `engine-owned` | `GLW_InitExtensions` alias added | High | No new debt opened in this mapping pass; GPL-era source owner is `win_glimp.c`, with QL extension-tail behavior mirrored by renderer post-process support. |
| 10 | `sub_490550` | `1822` | `engine-owned` | `AAS_Reachability_Grapple` alias added | High | No new debt; source owner already exists in `be_aas_reach.c`. |

Bucket summary:

- `engine-owned`: 6 of 10
- `platform-service-owned`: 1 of 10
- `CRT/STL`: 3 of 10
- `Awesomium`: 0 of 10
- `Steam SDK support`: 0 of 10

## Evidence Notes

### `sub_41D720 -> zmq_signaler_t_make_fdpair`

`sub_41D720` is a Windows ZeroMQ signaler helper. The decompile constructs or
opens the named event `Global\zmq-signaler-port-sync`, reports assertion
locations in `..\..\..\src\signaler.cpp`, then creates a localhost TCP pair by
binding, listening, connecting, accepting, and setting `TCP_NODELAY` and
handle flags. That is not engine gameplay or renderer logic; it is retained
Quake Live platform service support around the bundled ZeroMQ runtime.

### `sub_43E030 -> R_SubdividePatchToGrid`

`sub_43E030` matches renderer curved-surface subdivision. The function uses
`MAX_GRID_SIZE == 65`, builds the `ctrl` and two-row error table, evaluates
midpoint error against `r_subdivisions`, inserts columns, transposes twice,
places approximating points on the curve, culls colinear rows or columns,
reorients the final grid, calls `MakeMeshNormals`, and returns the created
grid mesh. The local source owner is `src/code/renderer/tr_curve.c:360`.

### `sub_4A4A50 -> BotMoveToGoal`

`sub_4A4A50` matches the bot movement coordinator. The preserved diagnostics
include `on func_plat without reachability`, `on func_bobbing without
reachability`, `didn't find jumppad reachability`, and both default travel
type fatal messages. The body validates the movement state, handles
func_plat/func_bobbing/top-of-entity cases, refreshes reachability state, then
dispatches the same travel-type switch used by `BotMoveToGoal` in
`src/code/botlib/be_ai_move.c:3055`.

### `sub_4FF4D0 -> deflate`

`sub_4FF4D0` is zlib `deflate`. The function validates the stream and flush
mode, emits `stream_error` and `buffer_error`, handles INIT/GZIP/BUSY/FINISH
states, writes gzip header bytes `0x1f, 0x8b, 8`, streams optional extra/name
and comment fields, calls CRC/adler helpers, dispatches the compression
strategy table, and writes the trailer. The local bundled zlib owner is
`src/libs/_deps/zlib/deflate.c:946`.

### `sub_43D350 -> MakeMeshNormals`

`sub_43D350` is the renderer mesh-normal builder for patch grids. It detects
wrapped width and height by comparing edge columns/rows, walks eight neighbor
directions up to distance three, ignores degenerate edges via `VectorNormalize2`,
accumulates cross products, and normalizes the resulting vertex normal. That
matches `MakeMeshNormals` in `src/code/renderer/tr_curve.c:112`.

### `sub_4423E0 -> stbtt__GetGlyphShapeTT`

`sub_4423E0` is the TrueType glyph-outline extractor used by the retained
fontstash/stb lane. The function reads `numberOfContours`, parses simple glyph
end-point arrays, repeated flags, and compressed x/y deltas into 10-byte
`stbtt_vertex` records, and handles composite glyphs when the contour count is
`-1` by following component flags, transforms, recursion, and `MORE_COMPONENTS`.
The nearby HLIL fontstash region references the `*fontstash` atlas and bundled
TTF loading, which keeps this in support-library ownership rather than engine
debt.

### `sub_4957F0 -> AAS_TraceClientBBox`

`sub_4957F0` matches the AAS client-bounding-box trace through the BSP tree.
The decompile builds a 127-entry trace stack, starts at node `1`, handles area
leaves lacking the requested presence type, handles solid leaf hits, checks
entity collision when `passent >= 0`, emits the preserved
`AAS_TraceBoundingBox: stack overflow` diagnostic, and returns the same
9-field `aas_trace_t` consumed by the reachability code. The source owner is
`src/code/botlib/be_aas_sample.c:449`.

### `sub_4401E0 -> stbtt__fill_active_edges_new`

`sub_4401E0` is the fontstash/stb scanline fill helper. The body walks active
edges, derives `y_top`/`y_bottom`, clips vertical and sloped edges to scanline
pixel spans, calls the clipped-edge accumulator helper, and updates scanline
coverage/fill arrays. Its placement immediately before the glyph-shape parser
and the surrounding HLIL fontstash evidence classifies it as bundled
font-rendering support, not engine source debt.

### `sub_46B060 -> GLW_InitExtensions`

`sub_46B060` matches the Win32 OpenGL extension initializer. The preserved
diagnostics cover `*** IGNORING OPENGL EXTENSIONS ***`, `Initializing OpenGL
extensions`, `GL_S3_s3tc`, `EXT_texture_env_add`, `WGL_EXT_swap_control`,
`GL_ARB_multitexture`, compiled vertex arrays, 3DFX gamma control, occlusion
queries, shader-object support, framebuffer-object support, and non-power-of-two
texture detection. The GPL-era source owner is
`src/code/win32/win_glimp.c:1284`; the extra Quake Live extension tail also
aligns with the renderer post-process extension support currently carried in
`src/code/renderer/tr_backend.c`.

### `sub_490550 -> AAS_Reachability_Grapple`

`sub_490550` matches the botlib grapple reachability builder. The body rejects
invalid source/target areas, traces down from the area center, tests high solid
faces at a minimum grapple angle, rejects sky surfaces and traces whose hit is
too far from the AAS wall, performs client-bbox and fall traces, rejects
lava/slime, existing reachabilities, non-grounded targets, and cluster-portal
paths, then emits `TRAVEL_GRAPPLEHOOK` reachabilities with
`rs_startgrapple + distance * 0.25`. The source owner is
`src/code/botlib/be_aas_reach.c:3793`.

## New High-Confidence Aliases Added This Round

- `sub_41D720 -> zmq_signaler_t_make_fdpair`
- `sub_43E030 -> R_SubdividePatchToGrid`
- `sub_4A4A50 -> BotMoveToGoal`
- `sub_4FF4D0 -> deflate`
- `sub_43D350 -> MakeMeshNormals`
- `sub_4423E0 -> stbtt__GetGlyphShapeTT`
- `sub_4957F0 -> AAS_TraceClientBBox`
- `sub_4401E0 -> stbtt__fill_active_edges_new`
- `sub_46B060 -> GLW_InitExtensions`
- `sub_490550 -> AAS_Reachability_Grapple`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1178` raw alias entries, `1177` address-keyed
  alias entries
- top remaining unaliased function by size: `sub_5099C0` at `1780` bytes

## Completion Stats After Round 118

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1178` raw alias entries, `1177` address-keyed
  aliases
- Address-keyed coverage: `21.506%` of `5473` functions
- Alias delta this round: `10`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the top queue as
six retained engine/source-owned functions, one ZeroMQ service helper, and
three bundled third-party support-library functions, leaving the next host
queue headed by `sub_5099C0`, `sub_5076D0`, and `sub_491050`.
