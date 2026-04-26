# Quake Live Steam Host Mapping Round 123

## Scope

This round continues directly from
[Round 122](./quakelive_steam_mapping_round_122.md) and consumes the refreshed
largest-unaliased `quakelive_steam.exe` queue from `sub_402790` through
`sub_4EA690`. Every candidate was classified before being considered as source
debt; no source debt was opened.

Evidence sources:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- source counterparts under `src/code/botlib/`, `src/code/client/`,
  `src/code/qcommon/`, `src/code/renderer/`, `src/code/win32/`,
  `src/libs/_deps/libpng/`, and `src/libs/_deps/libvorbis/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_402790` | `1031` | `platform-service-owned` | `zmq_ctx_t_term` alias added | High | No engine debt; ZeroMQ context teardown support. |
| 2 | `sub_4EE890` | `1025` | `engine-owned` | `NET_OpenSocks` alias added | High | No new debt; source owner exists in `win_net.c`. |
| 3 | `sub_4A8E20` | `1012` | `engine-owned` | `PC_ReadDefineParms` alias added | High | No new debt; source owner exists in `l_precomp.c`. |
| 4 | `sub_407F40` | `1010` | `platform-service-owned` | `zmq_socket_base_t_bind` alias added | High | No engine debt; ZeroMQ socket bind support. |
| 5 | `sub_513870` | `990` | `CRT/STL` | `png_write_cHRM_fixed` alias added | High | No engine debt; bundled libpng write support. |
| 6 | `sub_490C70` | `978` | `engine-owned` | `AAS_Reachability_WeaponJump` alias added | High | No new debt; source owner exists in `be_aas_reach.c`. |
| 7 | `sub_43B230` | `976` | `engine-owned` | `R_LoadSurfaces` alias added | High | No new debt; source owner exists in `tr_bsp.c`. |
| 8 | `sub_485DD0` | `970` | `engine-owned` | `AAS_WriteAASFile` alias added | High | No new debt; source owner exists in `be_aas_file.c`. |
| 9 | `sub_511880` | `970` | `CRT/STL` | `png_read_finish_row` alias added | High | No engine debt; bundled libpng read support. |
| 10 | `sub_494460` | `968` | `engine-owned` | `AAS_AreaRouteToGoalArea` alias added | High | No new debt; source owner exists in `be_aas_route.c`. |
| 11 | `sub_4B5800` | `968` | `engine-owned` | `CL_MouseMove` alias added | High | No new debt; source owner exists in `cl_input.c`. |
| 12 | `sub_469E40` | `961` | `engine-owned` | `GLW_ChoosePFD` alias added | High | No new debt; source owner exists in `win_glimp.c`. |
| 13 | `sub_4CCE90` | `959` | `engine-owned` | `Cvar_Set2` alias added | High | No new debt; source owner exists in `cvar.c`. |
| 14 | `sub_5041E0` | `959` | `CRT/STL` | `png_free_data` alias added | High | No engine debt; bundled libpng allocation cleanup. |
| 15 | `sub_4AF820` | `958` | `engine-owned` | `CL_GetServerCommand` alias added | High | No new debt; source owner exists in `cl_cgame.c`. |
| 16 | `sub_439080` | `949` | `engine-owned` | `ParseMesh` alias added | High | No new debt; source owner exists in `tr_bsp.c`. |
| 17 | `sub_40E690` | `948` | `platform-service-owned` | `zmq_options_t_getsockopt` alias added | High | No engine debt; ZeroMQ socket option support. |
| 18 | `sub_4A97B0` | `947` | `engine-owned` | `PC_ExpandDefine` alias added | High | No new debt; source owner exists in `l_precomp.c`. |
| 19 | `sub_495F40` | `940` | `engine-owned` | `AAS_TraceAreas` alias added | High | No new debt; source owner exists in `be_aas_sample.c`. |
| 20 | `sub_4303C0` | `938` | `CRT/STL` | `JsonStyledWriter_writeValue` alias added | High | No engine debt; bundled JsonCpp writer support. |
| 21 | `sub_46BC70` | `936` | `engine-owned` | `GLW_ChangeWindowMode` alias added | High | No new debt; source owner exists in `win_glimp.c`. |
| 22 | `sub_4380F0` | `934` | `engine-owned` | `RBPP_InitBloomResources` alias added | Medium-high | No new debt; post-process bloom resource setup is represented in renderer source. |
| 23 | `sub_4F5FC0` | `932` | `platform-service-owned` | `zauth_self_handle_pipe` alias added | High | No engine debt; bundled CZMQ authentication actor support. |
| 24 | `sub_516F90` | `929` | `CRT/STL` | `_vds_shared_init` alias added | High | No engine debt; bundled libvorbis DSP setup. |
| 25 | `sub_4EA690` | `926` | `engine-owned` | `IN_DIMouse` alias added | High | No new debt; source owner exists in `win_input.c`. |

Bucket summary:

- `engine-owned`: 16 of 25
- `platform-service-owned`: 4 of 25
- `CRT/STL`: 5 of 25
- `Awesomium`: 0 of 25
- `Steam SDK support`: 0 of 25

## Evidence Notes

The engine-owned tranche is Quake III/Quake Live client, renderer, win32,
qcommon, and botlib code with direct source counterparts. Strong signals
included SOCKS negotiation diagnostics, preprocessor define parameter
expansion, AAS reachability and route-cache traversal, EAAS file writing,
surface-type dispatch, DirectInput mouse polling, `Cvar_Set2` validation and
latched/cheat handling, `CL_GetServerCommand` reliable command checks,
post-process bloom shader names, and GL window/pixel-format transitions.

The platform-service tranche is retained ZeroMQ/CZMQ support. `zmq_ctx_t_term`
matches context teardown over live sockets and `done` commands,
`zmq_socket_base_t_bind` is anchored by the C API bind wrapper and inproc/tcp/ipc
bind behavior, `zmq_options_t_getsockopt` mirrors the adjacent setsockopt switch,
and `zauth_self_handle_pipe` is the CZMQ authentication actor's pipe command
handler for `ALLOW`, `DENY`, `PLAIN`, `CURVE`, `GSSAPI`, `VERBOSE`, and `$TERM`.

The support-library tranche maps to retained static dependencies: libpng chunk,
row, and allocation helpers; JsonCpp styled writer recursion; and libvorbis DSP
shared initialization. These are host binary support functions rather than
Quake engine source debt.

## New Aliases Added This Round

- `sub_402790 -> zmq_ctx_t_term`
- `sub_4EE890 -> NET_OpenSocks`
- `sub_4A8E20 -> PC_ReadDefineParms`
- `sub_407F40 -> zmq_socket_base_t_bind`
- `sub_513870 -> png_write_cHRM_fixed`
- `sub_490C70 -> AAS_Reachability_WeaponJump`
- `sub_43B230 -> R_LoadSurfaces`
- `sub_485DD0 -> AAS_WriteAASFile`
- `sub_511880 -> png_read_finish_row`
- `sub_494460 -> AAS_AreaRouteToGoalArea`
- `sub_4B5800 -> CL_MouseMove`
- `sub_469E40 -> GLW_ChoosePFD`
- `sub_4CCE90 -> Cvar_Set2`
- `sub_5041E0 -> png_free_data`
- `sub_4AF820 -> CL_GetServerCommand`
- `sub_439080 -> ParseMesh`
- `sub_40E690 -> zmq_options_t_getsockopt`
- `sub_4A97B0 -> PC_ExpandDefine`
- `sub_495F40 -> AAS_TraceAreas`
- `sub_4303C0 -> JsonStyledWriter_writeValue`
- `sub_46BC70 -> GLW_ChangeWindowMode`
- `sub_4380F0 -> RBPP_InitBloomResources`
- `sub_4F5FC0 -> zauth_self_handle_pipe`
- `sub_516F90 -> _vds_shared_init`
- `sub_4EA690 -> IN_DIMouse`

## Verification

Alias artifact validation:

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`
- recount after this pass: `1290` raw alias entries, `1284` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
- top remaining unaliased function by size: `sub_4CDD30` at `923` bytes
- no game/runtime launch was performed; this was a static mapping pass

## Completion Stats After Round 123

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1290` raw alias entries, `1284` address-keyed
  aliases
- Address-keyed coverage: `23.461%` of `5473` functions
- Alias delta this round: `25`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. The next refreshed queue is
headed by `sub_4CDD30`, `sub_50E410`, and `sub_4E98A0`.
