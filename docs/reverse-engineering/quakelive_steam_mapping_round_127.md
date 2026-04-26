# quakelive_steam.exe Mapping Round 127

Date: 2026-04-26

Scope: refreshed largest-unaliased queue after round 126, beginning at
`sub_4038B0`, `sub_47E730`, and `sub_50E810`.

## Summary

This round mapped `25` large unaliased `quakelive_steam.exe` functions from the
refreshed queue. Classification mix:

- `10` engine-owned functions
- `2` platform-service-owned functions
- `13` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

No source debt was opened. The engine-owned rows all match existing source
owners, the platform rows are bundled ZeroMQ support, and the CRT/STL rows are
MSVC locale/STL, JsonCpp, IJG JPEG, libpng, and libvorbis support code.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4038B0` | `764` | CRT/STL | `std_Locinfo_copy_ctor` | Medium-High | No engine debt; MSVC locale/`std::money_get` support copy helper. |
| 2 | `sub_47E730` | `764` | CRT/STL | `get_sof` | High | No engine debt; IJG JPEG SOF marker parser in `jdmarker.c`. |
| 3 | `sub_50E810` | `764` | CRT/STL | `png_combine_row` | High | No engine debt; libpng interlace row combine helper. |
| 4 | `sub_520920` | `763` | CRT/STL | `mdct_backward` | High | No engine debt; libvorbis MDCT inverse transform. |
| 5 | `sub_430790` | `755` | CRT/STL | `JsonStyledWriter_writeArrayValue` | High | No engine debt; bundled JsonCpp writer support. |
| 6 | `sub_499580` | `753` | engine-owned | `BotLoadMatchTemplates` | High | Source owner exists in botlib `be_ai_chat.c`; no new debt. |
| 7 | `sub_50F180` | `753` | CRT/STL | `png_read_start_row` | High | No engine debt; libpng row-start/read-buffer setup. |
| 8 | `sub_4190C0` | `749` | platform-service-owned | `zmq_stream_t_xsend` | High | No engine debt; bundled libzmq STREAM socket send path. |
| 9 | `sub_4C4180` | `749` | engine-owned | `BaseWindingForPlane` | High | Source owner exists in qcommon `cm_polylib.c`; no new debt. |
| 10 | `sub_412180` | `747` | platform-service-owned | `zmq_tcp_address_t_to_string` | High | No engine debt; bundled libzmq TCP address formatting. |
| 11 | `sub_42A9C0` | `747` | CRT/STL | `JsonValueObjectValues_erase_node` | Medium-High | No engine debt; JsonCpp/MSVC tree erase helper. |
| 12 | `sub_43E870` | `744` | engine-owned | `R_GridInsertColumn` | High | Source owner exists in renderer `tr_curve.c`; no new debt. |
| 13 | `sub_498DD0` | `742` | engine-owned | `BotLoadRandomStrings` | High | Source owner exists in botlib `be_ai_chat.c`; no new debt. |
| 14 | `sub_50BCE0` | `741` | CRT/STL | `png_write_info` | High | No engine debt; libpng info-chunk write orchestration. |
| 15 | `sub_4C8E70` | `740` | engine-owned | `Com_FilterPath` | High | Source owner exists in qcommon `common.c`; no new debt. |
| 16 | `sub_47EA30` | `733` | CRT/STL | `get_sos` | High | No engine debt; IJG JPEG SOS marker parser. |
| 17 | `sub_4811C0` | `733` | CRT/STL | `jpeg_fdct_float` | High | No engine debt; IJG floating-point FDCT. |
| 18 | `sub_42C2E0` | `732` | CRT/STL | `JsonReader_readValue` | High | No engine debt; bundled JsonCpp parser support. |
| 19 | `sub_46C2E0` | `731` | engine-owned | `GLimp_Init` | High | Source owner exists in the Win32 OpenGL layer; no new debt. |
| 20 | `sub_4AB160` | `731` | engine-owned | `PC_Evaluate` | High | Source owner exists in botlib `l_precomp.c`; no new debt. |
| 21 | `sub_4A2620` | `726` | engine-owned | `BotFinishTravel_WalkOffLedge` | High | Source owner exists in botlib `be_ai_move.c`; no new debt. |
| 22 | `sub_4A1510` | `724` | engine-owned | `BotWalkInDirection` | High | Source owner exists in botlib `be_ai_move.c`; no new debt. |
| 23 | `sub_522D40` | `718` | CRT/STL | `vorbis_residue_01forward` | High | No engine debt; libvorbis residue encode helper. |
| 24 | `sub_4BD350` | `713` | engine-owned | `CL_ParseSnapshot` | High | Source owner exists in client `cl_parse.c`; no new debt. |
| 25 | `sub_4ADBA0` | `710` | engine-owned | `PS_ReadNumber` | High | Source owner exists in botlib `l_script.c`; no new debt. |

## Evidence Notes

- `sub_4038B0` was classified as CRT/STL after cross-checking its
  `std::money_get`/locale cache neighborhood and object-copy behavior.
- `sub_47E730`, `sub_47EA30`, and `sub_4811C0` match the checked-in IJG JPEG
  source paths for SOF parsing, SOS parsing, and floating-point FDCT.
- `sub_50BCE0`, `sub_50E810`, and `sub_50F180` match libpng write-info,
  interlace row combine, and read-row startup helpers.
- `sub_520920` and `sub_522D40` match libvorbis MDCT and residue encode
  support, not Quake engine-owned code.
- `sub_412180` and `sub_4190C0` are ZeroMQ support paths and stay classified as
  platform-service-owned.
- The botlib, renderer, client, and qcommon rows all have existing checked-in
  source owners, so this round did not open implementation debt.

## Aliases Added

- `sub_4038B0` -> `std_Locinfo_copy_ctor`
- `sub_412180` -> `zmq_tcp_address_t_to_string`
- `sub_4190C0` -> `zmq_stream_t_xsend`
- `sub_42A9C0` -> `JsonValueObjectValues_erase_node`
- `sub_42C2E0` -> `JsonReader_readValue`
- `sub_430790` -> `JsonStyledWriter_writeArrayValue`
- `sub_43E870` -> `R_GridInsertColumn`
- `sub_46C2E0` -> `GLimp_Init`
- `sub_47E730` -> `get_sof`
- `sub_47EA30` -> `get_sos`
- `sub_4811C0` -> `jpeg_fdct_float`
- `sub_498DD0` -> `BotLoadRandomStrings`
- `sub_499580` -> `BotLoadMatchTemplates`
- `sub_4A1510` -> `BotWalkInDirection`
- `sub_4A2620` -> `BotFinishTravel_WalkOffLedge`
- `sub_4AB160` -> `PC_Evaluate`
- `sub_4ADBA0` -> `PS_ReadNumber`
- `sub_4BD350` -> `CL_ParseSnapshot`
- `sub_4C4180` -> `BaseWindingForPlane`
- `sub_4C8E70` -> `Com_FilterPath`
- `sub_50BCE0` -> `png_write_info`
- `sub_50E810` -> `png_combine_row`
- `sub_50F180` -> `png_read_start_row`
- `sub_520920` -> `mdct_backward`
- `sub_522D40` -> `vorbis_residue_01forward`

## Next Queue Head

After this round, the refreshed largest-unaliased queue should begin around
`sub_405EF0`, `sub_406430`, `sub_439440`, `sub_43C120`, and `sub_47A620`.
Refresh the queue before the next mapping pass so ties and newly resolved aliases
are handled from the current JSON corpus.
