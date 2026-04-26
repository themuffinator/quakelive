# Quake Live Steam Host Mapping Round 126

## Scope

This round continues directly from
[Round 125](./quakelive_steam_mapping_round_125.md) and consumes the refreshed
largest-unaliased `quakelive_steam.exe` queue from `sub_46A610` through
`sub_415770`. Every candidate was classified before being considered as source
debt; no source debt was opened.

Evidence sources:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- source counterparts under `src/code/botlib/`, `src/code/client/`,
  `src/code/qcommon/`, `src/code/renderer/`, `src/code/win32/`,
  `src/libs/_deps/libpng/`, `src/libs/_deps/zlib/`, and
  `src/libs/_deps/libvorbis/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_46A610` | `805` | `engine-owned` | `GLW_CreateWindow` alias added | High | No new debt; source owner exists in `win_glimp.c`. |
| 2 | `sub_4B5F70` | `802` | `engine-owned` | `CL_WritePacket` alias added | High | No new debt; source owner exists in `cl_input.c`. |
| 3 | `sub_4AB450` | `801` | `engine-owned` | `PC_DollarEvaluate` alias added | High | No new debt; source owner exists in `l_precomp.c`. |
| 4 | `sub_51D970` | `801` | `CRT/STL` | `dradf2` alias added | High | No engine debt; bundled libvorbis small FFT support. |
| 5 | `sub_486740` | `798` | `engine-owned` | `AAS_InitSettings` alias added | High | No new debt; source owner exists in `be_aas_move.c`. |
| 6 | `sub_482D90` | `797` | `engine-owned` | `AAS_ParseBSPEntities` alias added | High | No new debt; source owner exists in `be_aas_bspq3.c`. |
| 7 | `sub_4EFD70` | `795` | `engine-owned` | `SNDDMA_InitDS` alias added | High | No new debt; source owner exists in `win_snd.c`. |
| 8 | `sub_4FA0C0` | `794` | `platform-service-owned` | `zdir_new` alias added | High | No engine debt; bundled CZMQ recursive directory helper. |
| 9 | `sub_4C0BF0` | `791` | `engine-owned` | `CM_SubdivideGridColumns` alias added | High | No new debt; source owner exists in `cm_patch.c`. |
| 10 | `sub_500170` | `791` | `CRT/STL` | `deflate_fast` alias added | Medium-high | No engine debt; bundled zlib deflate fast compressor path. |
| 11 | `sub_4AC710` | `790` | `engine-owned` | `PC_ExpectTokenType` alias added | High | No new debt; source owner exists in `l_precomp.c`. |
| 12 | `sub_5071F0` | `790` | `CRT/STL` | `png_do_read_filler` alias added | High | No engine debt; bundled libpng read-transform support. |
| 13 | `sub_4B3CC0` | `789` | `engine-owned` | `CL_ConsolePrint` alias added | High | No new debt; source owner exists in `cl_console.c`. |
| 14 | `sub_4E8030` | `787` | `CRT/STL` | `inflate_fast` alias added | High | No engine debt; bundled zlib fast inflate decoder. |
| 15 | `sub_40FD50` | `786` | `platform-service-owned` | `zmq_pipepair` alias added | High | No engine debt; bundled libzmq pipe construction support. |
| 16 | `sub_491840` | `784` | `engine-owned` | `AAS_ContinueInitReachability` alias added | High | No new debt; source owner exists in `be_aas_reach.c`. |
| 17 | `sub_43B810` | `783` | `engine-owned` | `R_LoadFogs` alias added | High | No new debt; source owner exists in `tr_bsp.c`. |
| 18 | `sub_4C9B60` | `782` | `engine-owned` | `Com_Error` alias added | High | No new debt; source owner exists in `common.c`. |
| 19 | `sub_42FF70` | `780` | `CRT/STL` | `Json_valueToQuotedString` alias added | High | No engine debt; bundled JsonCpp writer string escaping helper. |
| 20 | `sub_411A10` | `778` | `platform-service-owned` | `zmq_tcp_address_t_resolve_interface` alias added | High | No engine debt; bundled libzmq TCP bind/interface resolver. |
| 21 | `sub_50C470` | `778` | `CRT/STL` | `png_set_filter_heuristics` alias added | High | No engine debt; bundled libpng weighted-filter heuristic setter. |
| 22 | `sub_42D460` | `774` | `CRT/STL` | `JsonReader_decodeNumber` alias added | High | No engine debt; bundled JsonCpp numeric decoder. |
| 23 | `sub_41A7C0` | `770` | `platform-service-owned` | `zmq_tcp_listener_t_in_event` alias added | High | No engine debt; bundled libzmq listener accept path. |
| 24 | `sub_42E9E0` | `770` | `CRT/STL` | `std_deque_insert_json_errorinfo` alias added | Medium | No engine debt; compiler STL deque helper for JsonCpp error storage. |
| 25 | `sub_415770` | `769` | `platform-service-owned` | `zmq_router_t_xrecv` alias added | High | No engine debt; bundled libzmq ROUTER socket receive path. |

Bucket summary:

- `engine-owned`: 12 of 25
- `platform-service-owned`: 5 of 25
- `CRT/STL`: 8 of 25
- `Awesomium`: 0 of 25
- `Steam SDK support`: 0 of 25

## Evidence Notes

The engine-owned tranche is Quake Live host, client, renderer, qcommon,
botlib, and Win32 code with direct source counterparts. Strong signals
included `Quake Live` window class creation, `CL_WritePacket` reliable command
and usercmd packing, `$evalint`/`$evalfloat` precompiler diagnostics, AAS BSP
entity parsing and physics libvars, DirectSound initialization messages,
collision grid subdivision, console `[skipnotify]` handling, reachability
progress messages, fog lump validation, and `Com_Error` recursive/error-log
control flow.

The platform-service tranche is retained ZeroMQ/CZMQ support. `pipe.cpp`,
`tcp_address.cpp`, `tcp_listener.cpp`, `router.cpp`, and `zdir.c` file strings,
assertion line anchors, `accept`/`getaddrinfo`/`SetHandleInformation` calls,
ROUTER identity frame handling, and CZMQ directory walk allocation/error
strings keep these out of Quake engine source debt.

The support-library tranche maps to retained static dependencies. Libvorbis
owns the radix-2 small FFT kernel; zlib owns fast deflate and fast inflate;
libpng owns read-filler expansion and the deprecated weighted-filter heuristic
setter; JsonCpp owns number decoding and quoted-string emission; the deque
helper is compiler-emitted STL support for JsonCpp error storage.

## New Aliases Added This Round

- `sub_46A610 -> GLW_CreateWindow`
- `sub_4B5F70 -> CL_WritePacket`
- `sub_4AB450 -> PC_DollarEvaluate`
- `sub_51D970 -> dradf2`
- `sub_486740 -> AAS_InitSettings`
- `sub_482D90 -> AAS_ParseBSPEntities`
- `sub_4EFD70 -> SNDDMA_InitDS`
- `sub_4FA0C0 -> zdir_new`
- `sub_4C0BF0 -> CM_SubdivideGridColumns`
- `sub_500170 -> deflate_fast`
- `sub_4AC710 -> PC_ExpectTokenType`
- `sub_5071F0 -> png_do_read_filler`
- `sub_4B3CC0 -> CL_ConsolePrint`
- `sub_4E8030 -> inflate_fast`
- `sub_40FD50 -> zmq_pipepair`
- `sub_491840 -> AAS_ContinueInitReachability`
- `sub_43B810 -> R_LoadFogs`
- `sub_4C9B60 -> Com_Error`
- `sub_42FF70 -> Json_valueToQuotedString`
- `sub_411A10 -> zmq_tcp_address_t_resolve_interface`
- `sub_50C470 -> png_set_filter_heuristics`
- `sub_42D460 -> JsonReader_decodeNumber`
- `sub_41A7C0 -> zmq_tcp_listener_t_in_event`
- `sub_42E9E0 -> std_deque_insert_json_errorinfo`
- `sub_415770 -> zmq_router_t_xrecv`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`
- recount after this pass: `1365` raw alias entries, `1359` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- address-keyed coverage moved from `1334 / 5473` (`24.374%`) to
  `1359 / 5473` (`24.831%`)
- top remaining unaliased functions by size: `sub_4038B0`,
  `sub_47E730`, and `sub_50E810`
- no game/runtime launch was performed; this was a static mapping pass

## Completion Stats After Round 126

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1365` raw alias entries, `1359` address-keyed
  aliases
- Address-keyed coverage: `24.831%` of `5473` functions
- Alias delta this round: `25`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. The next refreshed queue is
headed by `sub_4038B0`, `sub_47E730`, and `sub_50E810`.
