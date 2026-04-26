# Quake Live Steam Host Mapping Round 122

## Scope

This round continues directly from
[Round 121](./quakelive_steam_mapping_round_121.md) and consumes the refreshed
largest-unaliased `quakelive_steam.exe` queue from `sub_4B4300` through
`sub_4886A0`. Every candidate was classified before being considered as source
debt; no source debt was opened.

Evidence sources:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- source counterparts under `src/code/botlib/`, `src/code/client/`,
  `src/code/qcommon/`, `src/code/renderer/`, `src/libs/_deps/libpng/`,
  `src/libs/_deps/libvorbis/`, `src/libs/_deps/zlib/`, and `src/code/jpeg-6/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4B4300` | `1178` | `engine-owned` | `Con_DrawSolidConsole` alias added | High | No new debt; source owner exists in `cl_console.c`. |
| 2 | `sub_4C3BD0` | `1166` | `engine-owned` | `CM_DrawDebugSurface` alias added | High | No new debt; source owner exists in `cm_patch.c`. |
| 3 | `sub_521BC0` | `1163` | `CRT/STL` | `mapping0_inverse` alias added | High | No engine debt; bundled libvorbis support. |
| 4 | `sub_483B90` | `1136` | `engine-owned` | `AAS_CheckAreaForPossiblePortals` alias added | High | No new debt; source owner exists in `be_aas_cluster.c`. |
| 5 | `sub_428650` | `1134` | `platform-service-owned` | `zmq_mechanism_t_parse_metadata` alias added | High | No engine debt; ZeroMQ ZMTP metadata parsing support. |
| 6 | `sub_444360` | `1133` | `CRT/STL` | `fonsDrawText` alias added | Medium-high | No new debt; bundled FontStash host text support. |
| 7 | `sub_492100` | `1126` | `engine-owned` | `AAS_SetWeaponJumpAreaFlags` alias added | High | No new debt; source owner exists in `be_aas_reach.c`. |
| 8 | `sub_5093E0` | `1125` | `CRT/STL` | `png_do_expand` alias added | High | No engine debt; bundled libpng read-transform support. |
| 9 | `sub_50EB10` | `1123` | `CRT/STL` | `png_do_read_interlace` alias added | High | No engine debt; bundled libpng Adam7 support. |
| 10 | `sub_420920` | `1118` | `platform-service-owned` | `zmq_trie_t_add` alias added | High | No engine debt; ZeroMQ trie subscription support. |
| 11 | `sub_42CD60` | `1090` | `CRT/STL` | `JsonReader_readObject` alias added | High | No engine debt; bundled JsonCpp reader support. |
| 12 | `sub_407050` | `1083` | `platform-service-owned` | `zmq_socket_base_t_create` alias added | High | No engine debt; ZeroMQ socket factory support. |
| 13 | `sub_478A50` | `1081` | `CRT/STL` | `jpeg_validate_script` alias added | High | No engine debt; bundled JPEG progressive scan validation support. |
| 14 | `sub_51C280` | `1075` | `CRT/STL` | `_book_unquantize` alias added | High | No engine debt; bundled libvorbis codebook support. |
| 15 | `sub_435300` | `1070` | `engine-owned` | `RB_SurfaceAnim` alias added | High | No new debt; source owner exists in `tr_animation.c`. |
| 16 | `sub_4C2E70` | `1065` | `engine-owned` | `CM_TracePointThroughPatchCollide` alias added | High | No new debt; source owner exists in `cm_patch.c`. |
| 17 | `sub_4AE8A0` | `1062` | `engine-owned` | `ReadNumber` alias added | High | No new debt; source owner exists in `l_struct.c`. |
| 18 | `sub_4FCF80` | `1055` | `CRT/STL` | `ov_raw_seek` alias added | High | No engine debt; bundled libvorbis/vorbisfile support. |
| 19 | `sub_47D470` | `1053` | `CRT/STL` | `jpeg_decode_mcu` alias added | High | No engine debt; bundled JPEG Huffman decode support. |
| 20 | `sub_49C810` | `1047` | `engine-owned` | `GeneticParentsAndChildSelection` alias added | High | No new debt; source owner exists in `be_ai_gen.c`. |
| 21 | `sub_49B6C0` | `1044` | `engine-owned` | `BotInitialChat` alias added | High | No new debt; source owner exists in `be_ai_chat.c`. |
| 22 | `sub_4C14E0` | `1039` | `engine-owned` | `CM_SetBorderInward` alias added | High | No new debt; source owner exists in `cm_patch.c`. |
| 23 | `sub_494DB0` | `1036` | `engine-owned` | `AAS_AlternativeRouteGoals` alias added | High | No new debt; source owner exists in `be_aas_routealt.c`. |
| 24 | `sub_502950` | `1035` | `CRT/STL` | `compress_block` alias added | High | No engine debt; bundled zlib deflate tree support. |
| 25 | `sub_4886A0` | `1033` | `engine-owned` | `AAS_GetJumpPadInfo` alias added | High | No new debt; source owner exists in `be_aas_reach.c`. |

Bucket summary:

- `engine-owned`: 12 of 25
- `platform-service-owned`: 3 of 25
- `CRT/STL`: 10 of 25
- `Awesomium`: 0 of 25
- `Steam SDK support`: 0 of 25

## Evidence Notes

The engine-owned tranche is Quake III/Quake Live client console, renderer,
collision, and botlib code with direct source counterparts. Strong signals
included console scrollback and `Con_DrawInput` calls, `r_debugSurface` and
`cm_debugSize` patch-collision debug flow, MD4 animation bone interpolation,
`CM_SetBorderInward` mixed-plane diagnostics, botlib possible-portal flags,
weapon-jump item classnames, jump-pad `trigger_push` diagnostics, alternative
route `midrange area` logging, and botlib initial-chat/genetic selection
messages.

The platform-service tranche is ZeroMQ internals. `zmq_socket_base_t_create`
matches the socket-type allocation switch and `EINVAL` fallback,
`zmq_trie_t_add` matches sparse subscription trie growth, and
`zmq_mechanism_t_parse_metadata` is anchored by ZMTP metadata names
`Identity` and `Socket-Type`.

The support-library tranche maps to retained static dependencies: libvorbis
mapping/codebook/vorbisfile paths, libpng expand/interlace transforms, zlib
block compression, JsonCpp object parsing, JPEG progressive scan and Huffman MCU
helpers, and FontStash text drawing. These are host binary support functions
rather than Quake engine source debt.

## New Aliases Added This Round

- `sub_4B4300 -> Con_DrawSolidConsole`
- `sub_4C3BD0 -> CM_DrawDebugSurface`
- `sub_521BC0 -> mapping0_inverse`
- `sub_483B90 -> AAS_CheckAreaForPossiblePortals`
- `sub_428650 -> zmq_mechanism_t_parse_metadata`
- `sub_444360 -> fonsDrawText`
- `sub_492100 -> AAS_SetWeaponJumpAreaFlags`
- `sub_5093E0 -> png_do_expand`
- `sub_50EB10 -> png_do_read_interlace`
- `sub_420920 -> zmq_trie_t_add`
- `sub_42CD60 -> JsonReader_readObject`
- `sub_407050 -> zmq_socket_base_t_create`
- `sub_478A50 -> jpeg_validate_script`
- `sub_51C280 -> _book_unquantize`
- `sub_435300 -> RB_SurfaceAnim`
- `sub_4C2E70 -> CM_TracePointThroughPatchCollide`
- `sub_4AE8A0 -> ReadNumber`
- `sub_4FCF80 -> ov_raw_seek`
- `sub_47D470 -> jpeg_decode_mcu`
- `sub_49C810 -> GeneticParentsAndChildSelection`
- `sub_49B6C0 -> BotInitialChat`
- `sub_4C14E0 -> CM_SetBorderInward`
- `sub_494DB0 -> AAS_AlternativeRouteGoals`
- `sub_502950 -> compress_block`
- `sub_4886A0 -> AAS_GetJumpPadInfo`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`
- recount after this pass: `1265` raw alias entries, `1259` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- top remaining unaliased function by size: `sub_402790` at `1031` bytes
- no game/runtime launch was performed; this was a static mapping pass

## Completion Stats After Round 122

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1265` raw alias entries, `1259` address-keyed
  aliases
- Address-keyed coverage: `23.004%` of `5473` functions
- Alias delta this round: `25`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. The next refreshed queue is
headed by `sub_402790`, `sub_4EE890`, and `sub_4A8E20`.
