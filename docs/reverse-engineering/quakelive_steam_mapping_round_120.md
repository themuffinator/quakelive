# Quake Live Steam Host Mapping Round 120

## Scope

This round continues directly from
[Round 119](./quakelive_steam_mapping_round_119.md) and consumes the refreshed
largest-unaliased `quakelive_steam.exe` queue from `sub_49EDA0` through
`sub_417130`. The pass classified every candidate before treating it as source
debt; no source debt was opened.

Evidence sources:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- source counterparts under `src/code/botlib/`, `src/code/qcommon/`,
  `src/code/server/`, `src/code/win32/`, `src/libs/_deps/libpng/`,
  `src/libs/_deps/libvorbis/`, and `src/libs/_deps/zlib/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_49EDA0` | `1562` | `engine-owned` | `BotChooseNBGItem` alias added | High | No new debt; source owner exists in `be_ai_goal.c`. |
| 2 | `sub_4C72A0` | `1554` | `engine-owned` | `CM_Trace` alias added | High | No new debt; source owner exists in `cm_trace.c`. |
| 3 | `sub_4DE050` | `1551` | `engine-owned` | `SV_Arena_f` alias added | High | No new debt; source owner exists in `sv_ccmds.c`. |
| 4 | `sub_4EAEF0` | `1536` | `engine-owned` | `IN_JoyMove` alias added | High | No new debt; source owner exists in `win_input.c`. |
| 5 | `sub_4890E0` | `1526` | `engine-owned` | `AAS_Reachability_EqualFloorHeight` alias added | High | No new debt; source owner exists in `be_aas_reach.c`. |
| 6 | `sub_4A6B40` | `1524` | `engine-owned` | `ReadWeightConfig` alias added | High | No new debt; source owner exists in `be_ai_weight.c`. |
| 7 | `sub_524D70` | `1497` | `CRT/STL` | `floor1_encode` alias added | High | No engine debt; bundled libvorbis support. |
| 8 | `sub_49A960` | `1487` | `engine-owned` | `BotLoadInitialChat` alias added | High | No new debt; source owner exists in `be_ai_chat.c`. |
| 9 | `sub_4A3410` | `1467` | `engine-owned` | `BotTravel_FuncBobbing` alias added | High | No new debt; source owner exists in `be_ai_move.c`. |
| 10 | `sub_49A3A0` | `1438` | `engine-owned` | `BotLoadReplyChat` alias added | High | No new debt; source owner exists in `be_ai_chat.c`. |
| 11 | `sub_42DAB0` | `1418` | `CRT/STL` | `JsonReader_decodeString` alias added | Medium-high | No engine debt; bundled JsonCpp reader support. |
| 12 | `sub_436EC0` | `1417` | `engine-owned` | `RBPP_ApplyBloom` alias added | High | No new debt; source owner exists in `tr_backend.c`. |
| 13 | `sub_4CE5B0` | `1400` | `platform-service-owned` | `idZMQ_DecodeEmbeddedBlob` alias added | Medium | No engine debt; obfuscated ZMQ service blob initializer. |
| 14 | `sub_49D3C0` | `1395` | `engine-owned` | `BotInitLevelItems` alias added | High | No new debt; source owner exists in `be_ai_goal.c`. |
| 15 | `sub_401600` | `1375` | `platform-service-owned` | `zmq_poll` alias added | High | No engine debt; ZeroMQ polling support. |
| 16 | `sub_4E78C0` | `1351` | `CRT/STL` | `inflate_table` alias added | High | No engine debt; bundled zlib table builder. |
| 17 | `sub_4A2BC0` | `1346` | `engine-owned` | `BotTravel_Elevator` alias added | High | No new debt; source owner exists in `be_ai_move.c`. |
| 18 | `sub_4F8060` | `1339` | `platform-service-owned` | `zrex_match_program` alias added | Medium-high | No engine debt; CZMQ regex support. |
| 19 | `sub_420D90` | `1325` | `platform-service-owned` | `zmq_trie_t_rm` alias added | High | No engine debt; ZeroMQ subscription trie support. |
| 20 | `sub_505C70` | `1324` | `CRT/STL` | `png_read_row` alias added | High | No engine debt; bundled libpng sequential reader support. |
| 21 | `sub_485860` | `1321` | `engine-owned` | `AAS_LoadAASFile` alias added | High | No new debt; source owner exists in `be_aas_file.c`. |
| 22 | `sub_49E870` | `1315` | `engine-owned` | `BotChooseLTGItem` alias added | High | No new debt; source owner exists in `be_ai_goal.c`. |
| 23 | `sub_4ACBC0` | `1312` | `engine-owned` | `PC_Directive_define` alias added | High | No new debt; source owner exists in `l_precomp.c`. |
| 24 | `sub_4C66B0` | `1305` | `engine-owned` | `CM_TraceThroughVerticalCylinder` alias added | High | No new debt; source owner exists in `cm_trace.c`. |
| 25 | `sub_417130` | `1304` | `platform-service-owned` | `zmq_xpub_t_xread_activated` alias added | High | No engine debt; ZeroMQ XPUB subscription intake. |

Bucket summary:

- `engine-owned`: 16 of 25
- `platform-service-owned`: 5 of 25
- `CRT/STL`: 4 of 25
- `Awesomium`: 0 of 25
- `Steam SDK support`: 0 of 25

## Evidence Notes

The engine-owned tranche is mostly classic Quake III botlib, collision, server,
renderer, and Win32 input code with direct source counterparts. Strong signals
included preserved diagnostics such as `goal state handle %d out of range`,
`No arena name passed`, `trying to load %s`, `#define without name`,
`sv_cylinderScale`, and the botlib item, reachability, and travel-mode control
flow.

The support-library tranche maps to retained static dependencies:
`floor1_encode` in libvorbis, `Json::Reader` string escape decoding,
`inflate_table` in zlib, and `png_read_row` in libpng. These are host-binary
support functions rather than Quake engine source debt.

The platform-service tranche is ZeroMQ/CZMQ support or Quake Live service glue:
`zmq_poll`, `zmq_trie_t_rm`, `zmq_xpub_t_xread_activated`, the `zrex.c` regex VM,
and the inferred `idZMQ_DecodeEmbeddedBlob` initializer. The embedded-blob name
is intentionally conservative because the observed body only decodes a service
blob into `data_1208a90`; the nearby evidence ties it to the `zmqpass.txt` and
`id_zmq` service region.

## New High-Confidence Aliases Added This Round

- `sub_49EDA0 -> BotChooseNBGItem`
- `sub_4C72A0 -> CM_Trace`
- `sub_4DE050 -> SV_Arena_f`
- `sub_4EAEF0 -> IN_JoyMove`
- `sub_4890E0 -> AAS_Reachability_EqualFloorHeight`
- `sub_4A6B40 -> ReadWeightConfig`
- `sub_524D70 -> floor1_encode`
- `sub_49A960 -> BotLoadInitialChat`
- `sub_4A3410 -> BotTravel_FuncBobbing`
- `sub_49A3A0 -> BotLoadReplyChat`
- `sub_42DAB0 -> JsonReader_decodeString`
- `sub_436EC0 -> RBPP_ApplyBloom`
- `sub_4CE5B0 -> idZMQ_DecodeEmbeddedBlob`
- `sub_49D3C0 -> BotInitLevelItems`
- `sub_401600 -> zmq_poll`
- `sub_4E78C0 -> inflate_table`
- `sub_4A2BC0 -> BotTravel_Elevator`
- `sub_4F8060 -> zrex_match_program`
- `sub_420D90 -> zmq_trie_t_rm`
- `sub_505C70 -> png_read_row`
- `sub_485860 -> AAS_LoadAASFile`
- `sub_49E870 -> BotChooseLTGItem`
- `sub_4ACBC0 -> PC_Directive_define`
- `sub_4C66B0 -> CM_TraceThroughVerticalCylinder`
- `sub_417130 -> zmq_xpub_t_xread_activated`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`
- recount after this pass: `1215` raw alias entries, `1209` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- top remaining unaliased function by size: `sub_49E070` at `1292` bytes

## Completion Stats After Round 120

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1215` raw alias entries, `1209` address-keyed
  aliases
- Address-keyed coverage: `22.090%` of `5473` functions
- Alias delta this round: `25`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. The next refreshed queue is
headed by `sub_49E070`, `sub_5021E0`, and `sub_40E0E0`.
