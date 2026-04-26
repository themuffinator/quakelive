# quakelive_steam.exe Mapping Round 128

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 127, beginning at
`sub_405EF0`, `sub_406430`, and `sub_439440`.

## Summary

This round mapped `25` large unaliased `quakelive_steam.exe` functions from the
refreshed queue. Classification mix:

- `11` engine-owned functions
- `3` platform-service-owned functions
- `11` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. Engine-owned rows map to existing renderer, botlib,
server, and Win32 input owners. Platform rows are bundled ZeroMQ/WinSock support,
and CRT/STL rows are MSVC STL, JsonCpp, IJG JPEG, libpng, and libvorbis support.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_405EF0` | `701` | CRT/STL | `std_tree_insert_zmq_endpoint_node` | Medium-High | No engine debt; MSVC red-black tree insert for ZeroMQ endpoint map nodes. |
| 2 | `sub_406430` | `701` | CRT/STL | `std_tree_insert_zmq_pending_connection_node` | Medium-High | No engine debt; MSVC red-black tree insert for ZeroMQ pending-connection map nodes. |
| 3 | `sub_439440` | `695` | engine-owned | `ParseTriSurf` | High | Source owner exists in renderer `tr_bsp.c`; triangle-surface parser with bad-index guard. |
| 4 | `sub_43C120` | `692` | engine-owned | `R_PerformanceCounters` | High | Source owner exists in renderer `tr_cmds.c`; `r_speeds` counter print/reset path. |
| 5 | `sub_47A620` | `691` | CRT/STL | `encode_mcu_AC_refine` | High | No engine debt; IJG JPEG progressive Huffman AC-refine encoder helper. |
| 6 | `sub_43EB70` | `687` | engine-owned | `R_GridInsertRow` | High | Source owner exists in renderer `tr_curve.c`; paired grid row insertion beside the round 127 column helper. |
| 7 | `sub_506850` | `684` | CRT/STL | `png_do_strip_channel` | High | No engine debt; libpng channel-stripping row transform. |
| 8 | `sub_4A39D0` | `683` | engine-owned | `BotFinishTravel_FuncBobbing` | High | Source owner exists in botlib `be_ai_move.c`; func_bobbing travel completion logic. |
| 9 | `sub_438DD0` | `682` | engine-owned | `ParseFace` | High | Source owner exists in renderer `tr_bsp.c`; BSP face parser and `MAX_FACE_POINTS` warning path. |
| 10 | `sub_4E63A0` | `682` | engine-owned | `SV_AreaEntities_r` | High | Source owner exists in server `sv_world.c`; recursive world-sector area query. |
| 11 | `sub_491BE0` | `681` | engine-owned | `AAS_BestReachableFromJumpPadArea` | High | Source owner exists in botlib `be_aas_reach.c`; jump-pad reachability selection. |
| 12 | `sub_42D1B0` | `680` | CRT/STL | `JsonReader_readArray` | High | No engine debt; bundled JsonCpp array parser. |
| 13 | `sub_41A020` | `679` | platform-service-owned | `zmq_tcp_listener_t_in_event` | High | No engine debt; ZeroMQ listener accept event creates stream engine/session wiring. |
| 14 | `sub_511E10` | `678` | CRT/STL | `png_text_compress` | High | No engine debt; libpng text compression helper around zlib deflate. |
| 15 | `sub_4024E0` | `677` | platform-service-owned | `zmq_ctx_t_dtor` | High | No engine debt; ZeroMQ context destructor/cleanup path. |
| 16 | `sub_512AF0` | `677` | CRT/STL | `png_do_write_interlace` | High | No engine debt; libpng Adam7 write-pass row compactor. |
| 17 | `sub_516730` | `675` | CRT/STL | `_vorbis_unpack_books` | High | No engine debt; libvorbis setup header unpack for books, floors, residues, mappings, and modes. |
| 18 | `sub_4A8110` | `674` | engine-owned | `Init_AI_Export` | High | Source owner exists in botlib `be_interface.c`; botlib export table initializer. |
| 19 | `sub_437E40` | `673` | engine-owned | `RBPP_CreateBloomRenderTargets` | Medium-High | No new debt; retail bloom target-chain allocation is represented inside current renderer post-process setup. |
| 20 | `sub_51B860` | `672` | CRT/STL | `noise_normalize` | High | No engine debt; libvorbis psychoacoustic noise normalization helper. |
| 21 | `sub_522AA0` | `672` | CRT/STL | `_2class` | High | No engine debt; libvorbis residue class selection helper. |
| 22 | `sub_4051B0` | `669` | CRT/STL | `std_tree_lower_bound_zmq_pending_connection_node` | Medium-High | No engine debt; MSVC tree lookup for ZeroMQ pending-connection nodes. |
| 23 | `sub_401D10` | `668` | platform-service-owned | `zmq_wsa_error_no` | High | No engine debt; ZeroMQ WinSock error-code string mapper. |
| 24 | `sub_4841D0` | `667` | engine-owned | `AAS_InitClustering` | High | Source owner exists in botlib `be_aas_cluster.c`; portal/cluster initialization. |
| 25 | `sub_4EBBA0` | `663` | engine-owned | `IN_InitDIMouse` | High | Source owner exists in Win32 input `win_input.c`; DirectInput mouse initialization/acquire support. |

## Evidence Notes

- Renderer rows were anchored by retail strings and state writes: `ParseFace`,
  `ParseTriSurf`, `R_PerformanceCounters`, `R_GridInsertRow`, and the bloom
  render-target chain all cross-check against checked-in renderer owners.
- Botlib and server rows match existing source names and control flow:
  `BotFinishTravel_FuncBobbing`, `AAS_BestReachableFromJumpPadArea`,
  `AAS_InitClustering`, `Init_AI_Export`, and `SV_AreaEntities_r`.
- ZeroMQ rows are platform-service-owned: `sub_4024E0` tears down the context,
  `sub_41A020` is the TCP listener input event, and `sub_401D10` formats
  WinSock errors for that support layer.
- `sub_41A7C0` was corrected from `zmq_tcp_listener_t_in_event` to
  `zmq_tcp_listener_t_accept`; the HLIL body performs the raw `accept()` and
  access-filter checks called by the true listener event method.
- Support-library rows map to bundled sources rather than Quake engine debt:
  JsonCpp array parsing, IJG JPEG progressive Huffman encode, libpng text and
  row transforms, libvorbis setup/residue/psychoacoustic helpers, and MSVC STL
  tree helpers emitted around ZeroMQ containers.

## Aliases Added

- `sub_401D10` -> `zmq_wsa_error_no`
- `sub_4024E0` -> `zmq_ctx_t_dtor`
- `sub_4051B0` -> `std_tree_lower_bound_zmq_pending_connection_node`
- `sub_405EF0` -> `std_tree_insert_zmq_endpoint_node`
- `sub_406430` -> `std_tree_insert_zmq_pending_connection_node`
- `sub_41A020` -> `zmq_tcp_listener_t_in_event`
- `sub_42D1B0` -> `JsonReader_readArray`
- `sub_437E40` -> `RBPP_CreateBloomRenderTargets`
- `sub_438DD0` -> `ParseFace`
- `sub_439440` -> `ParseTriSurf`
- `sub_43C120` -> `R_PerformanceCounters`
- `sub_43EB70` -> `R_GridInsertRow`
- `sub_47A620` -> `encode_mcu_AC_refine`
- `sub_4841D0` -> `AAS_InitClustering`
- `sub_491BE0` -> `AAS_BestReachableFromJumpPadArea`
- `sub_4A39D0` -> `BotFinishTravel_FuncBobbing`
- `sub_4A8110` -> `Init_AI_Export`
- `sub_4E63A0` -> `SV_AreaEntities_r`
- `sub_4EBBA0` -> `IN_InitDIMouse`
- `sub_506850` -> `png_do_strip_channel`
- `sub_511E10` -> `png_text_compress`
- `sub_512AF0` -> `png_do_write_interlace`
- `sub_516730` -> `_vorbis_unpack_books`
- `sub_51B860` -> `noise_normalize`
- `sub_522AA0` -> `_2class`

## Alias Corrected

- `sub_41A7C0`: `zmq_tcp_listener_t_in_event` -> `zmq_tcp_listener_t_accept`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `python -m json.tool`
- recount after this pass: `1415` raw alias entries, `1409` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- address-keyed coverage: `25.745%` of `5473` functions
- no game/runtime launch was performed; this was a static mapping pass

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x0049FC30` | `FUN_0049fc30` | `659` |
| 2 | `0x00408EC0` | `FUN_00408ec0` | `659` |
| 3 | `0x00525370` | `FUN_00525370` | `658` |
| 4 | `0x00501AD0` | `FUN_00501ad0` | `657` |
| 5 | `0x0047ED10` | `FUN_0047ed10` | `655` |
| 6 | `0x004B0CD0` | `FUN_004b0cd0` | `654` |
| 7 | `0x0047B710` | `FUN_0047b710` | `654` |
| 8 | `0x004FBB00` | `FUN_004fbb00` | `647` |
| 9 | `0x00435FF0` | `FUN_00435ff0` | `647` |
| 10 | `0x0049CD80` | `FUN_0049cd80` | `646` |
| 11 | `0x0040A8F0` | `FUN_0040a8f0` | `645` |
| 12 | `0x0040A660` | `FUN_0040a660` | `645` |
| 13 | `0x0040A3D0` | `FUN_0040a3d0` | `645` |
| 14 | `0x00409F20` | `FUN_00409f20` | `645` |
| 15 | `0x00515250` | `FUN_00515250` | `643` |
| 16 | `0x00474D90` | `FUN_00474d90` | `642` |
| 17 | `0x004B07C0` | `FUN_004b07c0` | `641` |
| 18 | `0x004193B0` | `FUN_004193b0` | `641` |
| 19 | `0x0051D0A0` | `FUN_0051d0a0` | `639` |
| 20 | `0x0047AE50` | `FUN_0047ae50` | `639` |

Refresh the queue before the next mapping pass so ties and newly resolved aliases
are handled from the current JSON corpus.
