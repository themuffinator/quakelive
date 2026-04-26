# Quake Live Steam Host Mapping Round 124

## Scope

This round continues directly from
[Round 123](./quakelive_steam_mapping_round_123.md) and consumes the refreshed
largest-unaliased `quakelive_steam.exe` queue from `sub_4CDD30` through
`sub_4F7380`. Every candidate was classified before being considered as source
debt; no source debt was opened.

Evidence sources:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- source counterparts under `src/code/botlib/`, `src/code/qcommon/`,
  `src/code/renderer/`, `src/code/jpeg-6/`, `src/libs/_deps/libpng/`,
  and `src/libs/_deps/libvorbis/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4CDD30` | `923` | `engine-owned` | `Cvar_GetBounded` alias added | High | No new debt; source owner exists in `cvar.c`. |
| 2 | `sub_50E410` | `914` | `CRT/STL` | `png_decompress_chunk` alias added | High | No engine debt; bundled libpng zTXt decompression support. |
| 3 | `sub_4E98A0` | `913` | `CRT/STL` | `unzip_inflate` alias added | High | No engine debt; retained qcommon/zlib unzip support. |
| 4 | `sub_508DD0` | `913` | `CRT/STL` | `png_do_gamma` alias added | High | No engine debt; bundled libpng row transform support. |
| 5 | `sub_4FD3F0` | `909` | `CRT/STL` | `ov_read` alias added | High | No engine debt; bundled libvorbisfile PCM read support. |
| 6 | `sub_493BA0` | `908` | `engine-owned` | `AAS_UpdateAreaRoutingCache` alias added | High | No new debt; source owner exists in `be_aas_route.c`. |
| 7 | `sub_484E20` | `907` | `engine-owned` | `AAS_UpdateEntity` alias added | High | No new debt; source owner exists in `be_aas_entity.c`. |
| 8 | `sub_4C44E0` | `898` | `engine-owned` | `ChopWindingInPlace` alias added | High | No new debt; source owner exists in `cm_polylib.c`. |
| 9 | `sub_4C2AE0` | `897` | `engine-owned` | `CM_GeneratePatchCollide` alias added | High | No new debt; source owner exists in `cm_patch.c`. |
| 10 | `sub_415C30` | `893` | `platform-service-owned` | `zmq_router_t_identify_peer` alias added | High | No engine debt; bundled libzmq router support. |
| 11 | `sub_51C910` | `892` | `CRT/STL` | `vorbis_book_init_decode` alias added | High | No engine debt; bundled libvorbis codebook support. |
| 12 | `sub_4269D0` | `886` | `platform-service-owned` | `zmq_null_mechanism_t_receive_and_process_zap_reply` alias added | High | No engine debt; bundled libzmq ZAP mechanism support. |
| 13 | `sub_428020` | `886` | `platform-service-owned` | `zmq_plain_mechanism_t_receive_and_process_zap_reply` alias added | High | No engine debt; bundled libzmq ZAP mechanism support. |
| 14 | `sub_443FE0` | `885` | `engine-owned` | `R_InitFontStash` alias added | High | No new debt; source owner exists in `tr_font.c`. |
| 15 | `sub_4FC690` | `882` | `CRT/STL` | `_bisect_forward_serialno` alias added | High | No engine debt; bundled libvorbisfile seek/index support. |
| 16 | `sub_404010` | `879` | `platform-service-owned` | `zmq_ctx_t_connect_inproc_sockets` alias added | High | No engine debt; bundled libzmq inproc context support. |
| 17 | `sub_512DE0` | `878` | `CRT/STL` | `png_write_IHDR` alias added | High | No engine debt; bundled libpng write support. |
| 18 | `sub_4C6F30` | `877` | `engine-owned` | `CM_TraceThroughTree` alias added | High | No new debt; source owner exists in `cm_trace.c`. |
| 19 | `sub_442C10` | `871` | `CRT/STL` | `stbtt__rasterize_sorted_edges` alias added | Medium-high | No engine debt; bundled STB/FontStash rasterization support. |
| 20 | `sub_43EFB0` | `870` | `engine-owned` | `RB_RenderFlare` alias added | High | No new debt; source owner exists in `tr_flares.c`. |
| 21 | `sub_443BE0` | `870` | `CRT/STL` | `fonsTextBounds` alias added | Medium-high | No engine debt; retained FontStash text bounds support. |
| 22 | `sub_4C61B0` | `870` | `engine-owned` | `CM_TraceThroughSphere` alias added | High | No new debt; source owner exists in `cm_trace.c`. |
| 23 | `sub_51BB10` | `869` | `CRT/STL` | `_vp_couple_quantize_normalize` alias added | High | No engine debt; bundled libvorbis psychoacoustic coupling support. |
| 24 | `sub_4770A0` | `866` | `CRT/STL` | `jpeg_gen_optimal_table` alias added | High | No engine debt; bundled IJG/libjpeg entropy optimizer support. |
| 25 | `sub_4F7380` | `859` | `platform-service-owned` | `zsys_init` alias added | High | No engine debt; bundled CZMQ system/context initialization support. |

Bucket summary:

- `engine-owned`: 9 of 25
- `platform-service-owned`: 5 of 25
- `CRT/STL`: 11 of 25
- `Awesomium`: 0 of 25
- `Steam SDK support`: 0 of 25

## Evidence Notes

The engine-owned tranche is direct Quake Live host code with source
counterparts. Strong signals included bounded cvar registration and clamp
behavior, AAS entity relinking and route-cache updates, collision patch/trace
math, FontStash face initialization in the renderer, BSP tree tracing, and
flare quad emission through the tessellation surface path.

The platform-service tranche is retained ZeroMQ/CZMQ support. The libzmq
helpers are anchored by router identity insertion, inproc socket connection,
and NULL/PLAIN ZAP reply processing against the adjacent `mechanism.cpp`
aliases. `zsys_init` is anchored by the `ZSYS_*` environment family, CZMQ
shutdown registration, global mutex setup, and creation of the shared libzmq
context before later `zsys_socket` setup.

The support-library tranche maps to retained static dependencies. Libpng owns
zTXt inflation, gamma row transformation, and IHDR writing; libvorbis owns
Vorbisfile read/seek helpers plus codebook and psychoacoustic coupling code;
IJG/libjpeg owns optimal Huffman table generation; STB/FontStash owns raster
edge walking and text bounds. These are host binary support functions rather
than Quake engine source debt.

## New Aliases Added This Round

- `sub_4CDD30 -> Cvar_GetBounded`
- `sub_50E410 -> png_decompress_chunk`
- `sub_4E98A0 -> unzip_inflate`
- `sub_508DD0 -> png_do_gamma`
- `sub_4FD3F0 -> ov_read`
- `sub_493BA0 -> AAS_UpdateAreaRoutingCache`
- `sub_484E20 -> AAS_UpdateEntity`
- `sub_4C44E0 -> ChopWindingInPlace`
- `sub_4C2AE0 -> CM_GeneratePatchCollide`
- `sub_415C30 -> zmq_router_t_identify_peer`
- `sub_51C910 -> vorbis_book_init_decode`
- `sub_4269D0 -> zmq_null_mechanism_t_receive_and_process_zap_reply`
- `sub_428020 -> zmq_plain_mechanism_t_receive_and_process_zap_reply`
- `sub_443FE0 -> R_InitFontStash`
- `sub_4FC690 -> _bisect_forward_serialno`
- `sub_404010 -> zmq_ctx_t_connect_inproc_sockets`
- `sub_512DE0 -> png_write_IHDR`
- `sub_4C6F30 -> CM_TraceThroughTree`
- `sub_442C10 -> stbtt__rasterize_sorted_edges`
- `sub_43EFB0 -> RB_RenderFlare`
- `sub_443BE0 -> fonsTextBounds`
- `sub_4C61B0 -> CM_TraceThroughSphere`
- `sub_51BB10 -> _vp_couple_quantize_normalize`
- `sub_4770A0 -> jpeg_gen_optimal_table`
- `sub_4F7380 -> zsys_init`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`
- recount after this pass: `1315` raw alias entries, `1309` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- address-keyed coverage moved from `1284 / 5473` (`23.461%`) to
  `1309 / 5473` (`23.917%`)
- top remaining unaliased functions by size: `sub_49B170`,
  `sub_4AE160`, and `sub_522520`
- no game/runtime launch was performed; this was a static mapping pass

## Completion Stats After Round 124

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1315` raw alias entries, `1309` address-keyed
  aliases
- Address-keyed coverage: `23.917%` of `5473` functions
- Alias delta this round: `25`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. The next refreshed queue is
headed by `sub_49B170`, `sub_4AE160`, and `sub_522520`.
