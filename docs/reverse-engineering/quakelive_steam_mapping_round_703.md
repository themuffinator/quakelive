# Quake Live Steam Mapping Round 703: UGC Details Layout Constants

Date: 2026-06-16

## Scope

This pass rechecked the retained Steam Workshop `GetAllUGC` detail-record
layout used by `SteamCallbacks_OnGetAllUGCQueryCompleted` and
`QL_Steamworks_GetQueryUGCResult`. The source already used the retail
SteamUGC result/preview/release slots, but the published-file-id field and
GetAllUGC query/matching integers were still implicit in the C code.

Focused parity estimate: **before 92% -> after 99%** for focused Steam UGC
detail-record source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.88% -> 93.90%**.
Repo-wide parity remains **99%** because this pass clarifies opt-in
Steamworks UGC wiring without changing the strict-retail Windows replacement
score and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and symbol-map facts:

- `references/analysis/quakelive_symbol_aliases.json` maps
  `FUN_0045fd00` to `SteamCallbacks_OnGetAllUGCQueryCompleted`,
  `FUN_004606b0` to `SteamCallbacks_RunUGCQueryCompleted`,
  `FUN_004606d0` to `SteamCallbacks_RunUGCQueryCompletedCallResult`, and
  `FUN_00460dc0` to `SteamWorkshop_GetAllUGC`.
- `functions.csv` preserves those function rows at `0045fd00`, `004606b0`,
  `004606d0`, and `00460dc0`.
- `imports.txt` confirms the retained SteamUGC, SteamUtils,
  `SteamAPI_RegisterCallResult`, and `SteamAPI_UnregisterCallResult` imports.
- `analysis_symbols.txt` exposes the
  `CCallResult<class_SteamCallbacks,struct_SteamUGCQueryCompleted_t>` vtable
  and RTTI metadata.

Observed Binary Ninja HLIL anchors:

- `sub_460dc0` calls `SteamUtils + 0x24` for the AppID, then calls
  `SteamUGC + 0x04` with `(1, 0, appId, appId, filter)` before sending the
  query through `SteamUGC + 0x0c`.
- `sub_45fd00` reads each result through `SteamUGC + 0x10` into a stack detail
  record at `&var_2a44`.
- The same callback reads preview URLs through `SteamUGC + 0x14` into a
  `0x400` buffer.
- The JSON fields read `title` from `&var_2a2c` and `description` from
  `&var_29ab`; relative to the detail record base `&var_2a44`, those are
  offsets `0x18` and `0x99`.
- The `%llu` id field is formed from `var_2a44`/`var_2a40`, giving an
  8-byte published-file-id field at detail offset `0x00`.
- Success and failure paths release the query through `SteamUGC + 0x34`, and
  the retained strings are `GetAllUGC`, `web.ugc.results`, and
  `web.ugc.failed`.

Inference: the retail callback consumes an SDK `SteamUGCDetails_t`-style
record without naming it in our source. SRP should keep that SDK header-free
raw buffer, but the field offsets and query handoff integers should be named
so the source reads as a deliberate ABI projection rather than a loose byte
copy.

The query type and matching type constants intentionally use neutral names:
`QL_STEAM_UGC_GET_ALL_QUERY_TYPE` and
`QL_STEAM_UGC_GET_ALL_MATCHING_TYPE`. The retail evidence proves the numeric
handoff (`1`, `0`) and AppID/filter ordering; it does not require promoting
every Steamworks enum name as a source claim.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now names the UGC detail layout:

- `QL_STEAM_UGC_DETAILS_BUFFER_SIZE`
- `QL_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_OFFSET`
- `QL_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_SIZE`
- `QL_STEAM_UGC_DETAILS_TITLE_OFFSET`
- `QL_STEAM_UGC_DETAILS_DESCRIPTION_OFFSET`

The GetAllUGC query creation path now uses:

- `QL_STEAM_UGC_GET_ALL_QUERY_TYPE`
- `QL_STEAM_UGC_GET_ALL_MATCHING_TYPE`

`QL_Steamworks_GetQueryUGCResult` now copies the published file id from the
named `0x00` detail-record offset and uses the named 8-byte field size. The
title and description reads continue to use the already mapped `0x18` and
`0x99` offsets.

`tests/steamworks_harness.c` mirrors the published-file-id offset and size so
the mock SteamUGC result writer remains an explicit ABI control sample for
the platform wrapper tests.

No callback id, vtable slot, JSON publication event, release behavior,
opt-in Steamworks guard, or live service policy changed in this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_ugc_details_layout_constants_round_703 or steam_ugc_query_call_result_publication_lifecycle_tracks_round_619 or steam_ugc_get_all_query_appid_order_tracks_round_637 or steam_ugc_apps_workshop_slot_constants_round_699" --tb=short` - 4 passed, 238 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 241 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
