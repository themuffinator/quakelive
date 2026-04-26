# Quake Live Steam Host Mapping Round 121

## Scope

This round continues directly from
[Round 120](./quakelive_steam_mapping_round_120.md) and consumes the refreshed
largest-unaliased `quakelive_steam.exe` queue from `sub_49E070` through
`sub_41EF10`. The pass classified every candidate before treating it as source
debt; no source debt was opened.

Evidence sources:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- source counterparts under `src/code/botlib/`, `src/code/client/`,
  `src/code/qcommon/`, `src/code/renderer/`, `src/code/win32/`,
  `src/libs/_deps/libpng/`, `src/libs/_deps/libvorbis/`, and
  `src/libs/_deps/zlib/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_49E070` | `1292` | `engine-owned` | `BotUpdateEntityItems` alias added | High | No new debt; source owner exists in `be_ai_goal.c`. |
| 2 | `sub_5021E0` | `1285` | `CRT/STL` | `send_tree` alias added | High | No engine debt; bundled zlib support. |
| 3 | `sub_40E0E0` | `1282` | `platform-service-owned` | `zmq_options_t_setsockopt` alias added | High | No engine debt; ZeroMQ socket option support. |
| 4 | `sub_4264D0` | `1277` | `platform-service-owned` | `zmq_null_mechanism_t_send_zap_request` alias added | High | No engine debt; ZeroMQ ZAP authentication support. |
| 5 | `sub_4A5A90` | `1273` | `engine-owned` | `LoadWeaponConfig` alias added | High | No new debt; source owner exists in `be_ai_weap.c`. |
| 6 | `sub_498210` | `1272` | `engine-owned` | `BotLoadSynonyms` alias added | High | No new debt; source owner exists in `be_ai_chat.c`. |
| 7 | `sub_496B40` | `1271` | `engine-owned` | `BotLoadCharacterFromFile` alias added | High | No new debt; source owner exists in `be_ai_char.c`. |
| 8 | `sub_5247B0` | `1260` | `CRT/STL` | `floor1_fit` alias added | High | No engine debt; bundled libvorbis support. |
| 9 | `sub_51ACD0` | `1257` | `CRT/STL` | `_vp_offset_and_mix` alias added | High | No engine debt; bundled libvorbis support. |
| 10 | `sub_501360` | `1256` | `CRT/STL` | `zlib_inflate_table` alias added | High | No engine debt; bundled zlib/libpng support. |
| 11 | `sub_41FA70` | `1255` | `platform-service-owned` | `zmq_mtrie_t_rm` alias added | High | No engine debt; ZeroMQ subscription trie support. |
| 12 | `sub_4B29D0` | `1253` | `engine-owned` | `RoQInterrupt` alias added | High | No new debt; source owner exists in `cl_cin.c`. |
| 13 | `sub_46AB80` | `1244` | `engine-owned` | `GLW_SetMode` alias added | High | No new debt; source owner exists in `win_glimp.c`. |
| 14 | `sub_48EBE0` | `1233` | `engine-owned` | `AAS_FindFaceReachabilities` alias added | High | No new debt; source owner exists in `be_aas_reach.c`. |
| 15 | `sub_50AED0` | `1227` | `CRT/STL` | `png_do_read_transformations` alias added | High | No engine debt; bundled libpng support. |
| 16 | `sub_402C50` | `1227` | `platform-service-owned` | `zmq_ctx_t_create_socket` alias added | High | No engine debt; ZeroMQ context/socket allocation support. |
| 17 | `sub_4C5BB0` | `1225` | `engine-owned` | `CM_TraceThroughBrush` alias added | High | No new debt; source owner exists in `cm_trace.c`. |
| 18 | `sub_503860` | `1224` | `CRT/STL` | `longest_match` alias added | High | No engine debt; bundled zlib deflate support. |
| 19 | `sub_443720` | `1201` | `CRT/STL` | `fons__getGlyph` alias added | Medium-high | No engine debt; bundled FontStash/STB glyph cache support. |
| 20 | `sub_4C33E0` | `1189` | `engine-owned` | `CM_TraceThroughPatchCollide` alias added | High | No new debt; source owner exists in `cm_patch.c`. |
| 21 | `sub_439910` | `1186` | `engine-owned` | `R_FixSharedVertexLodError_r` alias added | High | No new debt; source owner exists in `tr_bsp.c`. |
| 22 | `sub_4A3DE0` | `1183` | `engine-owned` | `BotTravel_Grapple` alias added | High | No new debt; source owner exists in `be_ai_move.c`. |
| 23 | `sub_50FBB0` | `1183` | `CRT/STL` | `png_handle_cHRM` alias added | High | No engine debt; bundled libpng support. |
| 24 | `sub_4A66A0` | `1180` | `engine-owned` | `ReadFuzzySeperators_r` alias added | High | No new debt; source owner exists in `be_ai_weight.c`. |
| 25 | `sub_41EF10` | `1178` | `platform-service-owned` | `zmq_mtrie_t_add` alias added | High | No engine debt; ZeroMQ subscription trie support. |

Bucket summary:

- `engine-owned`: 12 of 25
- `platform-service-owned`: 5 of 25
- `CRT/STL`: 8 of 25
- `Awesomium`: 0 of 25
- `Steam SDK support`: 0 of 25

## Evidence Notes

The engine-owned tranche is classic Quake III/Quake Live renderer, botlib,
collision, cinematic, and Win32 GL code with direct source counterparts. Strong
signals included botlib parser diagnostics such as `max_weaponinfo`,
`synonym must have at least two entries`, `more than 32 context levels`, and
`switch without default`, collision trace plane/fraction writes, RoQ chunk IDs,
and the preserved Win32 display-mode diagnostics around `r_aspectRatio` and
`ChangeDisplaySettings`.

The platform-service tranche is ZeroMQ internals. `zmq_options_t_setsockopt`
matches the large socket-option switch and `EINVAL` exits; the `mtrie.cpp`
entries match recursive subscription add/remove and sparse child-table pruning;
`zmq_ctx_t_create_socket` matches context slot/socket allocation; and
`zmq_null_mechanism_t_send_zap_request` is anchored by the `NULL` mechanism ZAP
frame sequence.

The support-library tranche maps to retained static dependencies:
zlib tree and deflate helpers, libpng read-transform/chunk handlers, libvorbis
psy/floor helpers, and the FontStash/STB glyph lookup path. These are host
binary support functions rather than Quake engine source debt. The
`zlib_inflate_table` name is intentionally qualified because another
inflate-table implementation is already present in this host alias map.

## New Aliases Added This Round

- `sub_49E070 -> BotUpdateEntityItems`
- `sub_5021E0 -> send_tree`
- `sub_40E0E0 -> zmq_options_t_setsockopt`
- `sub_4264D0 -> zmq_null_mechanism_t_send_zap_request`
- `sub_4A5A90 -> LoadWeaponConfig`
- `sub_498210 -> BotLoadSynonyms`
- `sub_496B40 -> BotLoadCharacterFromFile`
- `sub_5247B0 -> floor1_fit`
- `sub_51ACD0 -> _vp_offset_and_mix`
- `sub_501360 -> zlib_inflate_table`
- `sub_41FA70 -> zmq_mtrie_t_rm`
- `sub_4B29D0 -> RoQInterrupt`
- `sub_46AB80 -> GLW_SetMode`
- `sub_48EBE0 -> AAS_FindFaceReachabilities`
- `sub_50AED0 -> png_do_read_transformations`
- `sub_402C50 -> zmq_ctx_t_create_socket`
- `sub_4C5BB0 -> CM_TraceThroughBrush`
- `sub_503860 -> longest_match`
- `sub_443720 -> fons__getGlyph`
- `sub_4C33E0 -> CM_TraceThroughPatchCollide`
- `sub_439910 -> R_FixSharedVertexLodError_r`
- `sub_4A3DE0 -> BotTravel_Grapple`
- `sub_50FBB0 -> png_handle_cHRM`
- `sub_4A66A0 -> ReadFuzzySeperators_r`
- `sub_41EF10 -> zmq_mtrie_t_add`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`
- recount after this pass: `1240` raw alias entries, `1234` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- top remaining unaliased function by size: `sub_4B4300` at `1178` bytes
- no game/runtime launch was performed; this was a static mapping pass

## Completion Stats After Round 121

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1240` raw alias entries, `1234` address-keyed
  aliases
- Address-keyed coverage: `22.547%` of `5473` functions
- Alias delta this round: `25`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. The next refreshed queue is
headed by `sub_4B4300`, `sub_4C3BD0`, and `sub_521BC0`.
