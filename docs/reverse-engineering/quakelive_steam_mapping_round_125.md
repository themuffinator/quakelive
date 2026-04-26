# Quake Live Steam Host Mapping Round 125

## Scope

This round continues directly from
[Round 124](./quakelive_steam_mapping_round_124.md) and consumes the refreshed
largest-unaliased `quakelive_steam.exe` queue from `sub_49B170` through
`sub_4D2750`. Every candidate was classified before being considered as source
debt; no source debt was opened.

Evidence sources:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- source counterparts under `src/code/botlib/`, `src/code/client/`,
  `src/code/qcommon/`, `src/code/renderer/`, `src/code/jpeg-6/`,
  `src/libs/_deps/libpng/`, and `src/libs/_deps/libvorbis/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_49B170` | `858` | `engine-owned` | `BotConstructChatMessage` alias added | High | No new debt; source owner exists in `be_ai_chat.c`. |
| 2 | `sub_4AE160` | `858` | `engine-owned` | `PS_ExpectTokenType` alias added | High | No new debt; source owner exists in `l_script.c`. |
| 3 | `sub_522520` | `856` | `CRT/STL` | `local_book_besterror` alias added | High | No engine debt; bundled libvorbis residue encoder support. |
| 4 | `sub_43F790` | `851` | `CRT/STL` | `stbtt_FindGlyphIndex` alias added | Medium-high | No engine debt; bundled STB truetype cmap lookup support. |
| 5 | `sub_4AECD0` | `851` | `engine-owned` | `ReadStructure` alias added | High | No new debt; source owner exists in `l_struct.c`. |
| 6 | `sub_47F2B0` | `847` | `CRT/STL` | `get_dht` alias added | High | No engine debt; bundled IJG/libjpeg marker parser support. |
| 7 | `sub_4991C0` | `847` | `engine-owned` | `BotLoadMatchPieces` alias added | High | No new debt; source owner exists in `be_ai_chat.c`. |
| 8 | `sub_484580` | `841` | `engine-owned` | `AAS_ShowFacePolygon` alias added | High | No new debt; source owner exists in `be_aas_debug.c`. |
| 9 | `sub_404710` | `838` | `CRT/STL` | `std_tree_erase_zmq_endpoint_node` alias added | Medium | No engine debt; compiler STL tree erase for retained ZeroMQ maps. |
| 10 | `sub_404E60` | `838` | `CRT/STL` | `std_tree_erase_zmq_pending_connection_node` alias added | Medium | No engine debt; compiler STL tree erase for retained ZeroMQ maps. |
| 11 | `sub_415420` | `835` | `platform-service-owned` | `zmq_router_t_xsend` alias added | High | No engine debt; bundled libzmq ROUTER socket send path. |
| 12 | `sub_421A30` | `831` | `platform-service-owned` | `zmq_stream_engine_t_plug` alias added | High | No engine debt; bundled libzmq stream engine attachment. |
| 13 | `sub_494870` | `830` | `engine-owned` | `AAS_PredictRoute` alias added | High | No new debt; source owner exists in `be_aas_route.c`. |
| 14 | `sub_4E7170` | `830` | `CRT/STL` | `unzlocal_GetCurrentFileInfoInternal` alias added | High | No engine debt; retained unzip central-directory reader. |
| 15 | `sub_4C55D0` | `829` | `engine-owned` | `CM_TraceCapsuleThroughCapsule` alias added | High | No new debt; source owner exists in `cm_trace.c`. |
| 16 | `sub_4BD000` | `827` | `engine-owned` | `CL_ParsePacketEntities` alias added | High | No new debt; source owner exists in `cl_parse.c`. |
| 17 | `sub_428AE0` | `826` | `platform-service-owned` | `zmq_mechanism_t_check_socket_type` alias added | High | No engine debt; bundled libzmq ZMTP metadata validation. |
| 18 | `sub_4C3890` | `817` | `engine-owned` | `CM_PositionTestInPatchCollide` alias added | High | No new debt; source owner exists in `cm_patch.c`. |
| 19 | `sub_438990` | `816` | `engine-owned` | `R_LoadLightmaps` alias added | High | No new debt; source owner exists in `tr_bsp.c`. |
| 20 | `sub_41BB60` | `815` | `platform-service-owned` | `zmq_session_base_t_zap_connect` alias added | High | No engine debt; bundled libzmq ZAP session plumbing. |
| 21 | `sub_50CB40` | `815` | `CRT/STL` | `png_set_cHRM` alias added | High | No engine debt; bundled libpng chromaticity setter. |
| 22 | `sub_41A490` | `813` | `platform-service-owned` | `zmq_tcp_listener_t_set_address` alias added | High | No engine debt; bundled libzmq TCP listener bind/listen setup. |
| 23 | `sub_4FCAB0` | `812` | `CRT/STL` | `_fetch_and_process_packet` alias added | High | No engine debt; bundled libvorbisfile packet/page decode loop. |
| 24 | `sub_4CE0D0` | `811` | `engine-owned` | `Cvar_Get` alias added | High | No new debt; source owner exists in `cvar.c`. |
| 25 | `sub_4D2750` | `810` | `engine-owned` | `FS_ExtractGamecode` alias added | High | No new debt; filesystem/native gamecode extraction path already tracked as engine-owned. |

Bucket summary:

- `engine-owned`: 12 of 25
- `platform-service-owned`: 5 of 25
- `CRT/STL`: 8 of 25
- `Awesomium`: 0 of 25
- `Steam SDK support`: 0 of 25

## Evidence Notes

The engine-owned tranche is direct Quake Live host behavior with source
counterparts. Strong signals included bot chat construction error strings,
script parser token-type diagnostics, structure-field parser errors, AAS
debug polygon and route prediction flow, packet entity delta/baseline parsing,
collision capsule/patch traces, BSP lightmap lump loading, canonical `Cvar_Get`
control flow, and the `FS_ExtractGamecode` fatal read/write strings.

The platform-service tranche is retained ZeroMQ support. `router.cpp`,
`stream_engine.cpp`, `mechanism.cpp`, `session_base.cpp`, and
`tcp_listener.cpp` path strings, assertion line anchors, socket type names,
bind/listen syscalls, ZAP pipe setup, and adjacent promoted RTTI/vtable symbols
keep these out of Quake engine source debt.

The support-library tranche maps to retained static dependencies. Libvorbis
owns residue codebook search and Vorbisfile packet processing; STB owns the
truetype glyph-index lookup; IJG/libjpeg owns DHT marker parsing; unzip owns
central directory file-info reads; libpng owns the cHRM setter. The two
`std_tree_erase_*` aliases are compiler-emitted STL red-black tree erasers
serving ZeroMQ maps, so they are documented as support code rather than
engine-owned behavior.

## New Aliases Added This Round

- `sub_49B170 -> BotConstructChatMessage`
- `sub_4AE160 -> PS_ExpectTokenType`
- `sub_522520 -> local_book_besterror`
- `sub_43F790 -> stbtt_FindGlyphIndex`
- `sub_4AECD0 -> ReadStructure`
- `sub_47F2B0 -> get_dht`
- `sub_4991C0 -> BotLoadMatchPieces`
- `sub_484580 -> AAS_ShowFacePolygon`
- `sub_404710 -> std_tree_erase_zmq_endpoint_node`
- `sub_404E60 -> std_tree_erase_zmq_pending_connection_node`
- `sub_415420 -> zmq_router_t_xsend`
- `sub_421A30 -> zmq_stream_engine_t_plug`
- `sub_494870 -> AAS_PredictRoute`
- `sub_4E7170 -> unzlocal_GetCurrentFileInfoInternal`
- `sub_4C55D0 -> CM_TraceCapsuleThroughCapsule`
- `sub_4BD000 -> CL_ParsePacketEntities`
- `sub_428AE0 -> zmq_mechanism_t_check_socket_type`
- `sub_4C3890 -> CM_PositionTestInPatchCollide`
- `sub_438990 -> R_LoadLightmaps`
- `sub_41BB60 -> zmq_session_base_t_zap_connect`
- `sub_50CB40 -> png_set_cHRM`
- `sub_41A490 -> zmq_tcp_listener_t_set_address`
- `sub_4FCAB0 -> _fetch_and_process_packet`
- `sub_4CE0D0 -> Cvar_Get`
- `sub_4D2750 -> FS_ExtractGamecode`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`
- recount after this pass: `1340` raw alias entries, `1334` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- address-keyed coverage moved from `1309 / 5473` (`23.917%`) to
  `1334 / 5473` (`24.374%`)
- top remaining unaliased functions by size: `sub_46A610`,
  `sub_4B5F70`, and `sub_4AB450`
- no game/runtime launch was performed; this was a static mapping pass

## Completion Stats After Round 125

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1340` raw alias entries, `1334` address-keyed
  aliases
- Address-keyed coverage: `24.374%` of `5473` functions
- Alias delta this round: `25`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. The next refreshed queue is
headed by `sub_46A610`, `sub_4B5F70`, and `sub_4AB450`.
