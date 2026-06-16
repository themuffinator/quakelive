# Quake Live Steam Mapping Round 699: SteamApps And Workshop UGC Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the retained SteamApps, SteamUGC, SteamGameServerUGC, and
SteamGameServerUtils wrapper surface used by subscription checks, GetAllUGC,
workshop startup mounts, workshop subscribe/unsubscribe/download commands, and
server app-id lookup. The reconstruction goal was to replace raw production
vtable indices with named ABI slot constants while preserving the mock vtable
layout as the ABI control sample.

Focused parity estimate: **before 90% -> after 99%** for focused
SteamApps/Workshop UGC ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.80% -> 93.82%**.
Repo-wide parity remains **99%** because this pass names retained Steamworks
wrapper boundaries without changing the strict-retail Windows replacement
score and does not enable live Steam behavior by default.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `FUN_00460590` / `sub_460590` | `SteamApps_BIsSubscribedApp` | High | Calls `SteamApps + 0x1c` for app subscription checks. |
| `FUN_00460660` / `sub_460660` | `SteamUGC_GetItemDownloadInfo` | High | Calls `SteamUGC + 0xd8` for workshop download progress. |
| `FUN_00460dc0` / `sub_460dc0` | `SteamWorkshop_GetAllUGC` | High | Creates and sends the retained all-UGC query through `SteamUGC + 0x04` and `+0x0c`. |
| `FUN_00469260` / `sub_469260` | `SteamWorkshop_SubscribeItem` | High | Calls `SteamUGC + 0xc0`, then tests item state through `SteamUGC + 0xd0`. |
| `FUN_004692b0` / `sub_4692b0` | `SteamWorkshop_UnsubscribeItem` | High | Calls `SteamUGC + 0xc4`. |
| `FUN_00469400` / `sub_469400` | `SteamWorkshop_AdvanceDownloadQueue` | High | Advances queued downloads through `SteamUGC + 0xdc`. |
| `FUN_00469470` / `sub_469470` | `SteamWorkshop_FinalizeItem` | High | Reads install info and state through `SteamUGC + 0xd4` and `+0xd0`. |
| `FUN_004697a0` / `sub_4697a0` | `SteamWorkshop_Init` | High | Enumerates subscribed items through `SteamUGC + 0xcc`, `+0xc8`, and `+0xd4`. |
| `FUN_004699c0` / `sub_4699c0` | `SteamWorkshop_RequestDownload` | High | Checks state and requests downloads through `SteamUGC + 0xd0` and `+0xdc`. |

Observed Binary Ninja HLIL anchors:

- `004605b7` calls `SteamApps + 0x1c` for `BIsSubscribedApp`.
- `00460689` calls `SteamUGC + 0xd8` for item download info.
- `00460df3` and `00460e04` call `SteamUGC + 0x04` and `+0x0c` for the
  GetAllUGC query.
- `0045fd88`, `0045fdaa`, `0045feb2`, and `0045fd60` call `SteamUGC + 0x10`,
  `+0x14`, and `+0x34` for query result, preview URL, and release.
- `0046794f` calls `SteamGameServerUtils + 0x24` for server app id.
- `0046927b`, `0046928d`, and `004692cc` cover subscribe, state, and
  unsubscribe at `SteamUGC + 0xc0`, `+0xd0`, and `+0xc4`.
- `00469466`, `004694ca`, `004694dc`, `004698c6`, `004698d6`, `00469944`,
  `00469a66`, and `00469ad0` cover download, install-info, state,
  subscribed-list, subscribed-count, and startup mount paths.

Observed Ghidra companion facts:

- `imports.txt` imports `SteamApps`, `SteamUGC`, `SteamGameServerUGC`, and
  `SteamGameServerUtils`.
- `functions.csv` contains the promoted app, UGC, and workshop owner rows at
  `00460590`, `00460660`, `00460dc0`, `00469260`, `004692b0`, `00469400`,
  `00469470`, `004697a0`, and `004699c0`.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners to
  the retained wrapper names.
- `tests/steamworks_harness.c` mirrors the mock `SteamUGC`,
  `SteamGameServerUGC`, and `SteamGameServerUtils` vtable assignments; Round
  707 later promoted that mirror from raw offsets to named harness-local
  constants. Round 714 later added the missing harness `SteamApps` mirror for
  the `BIsSubscribedApp` slot.

Inference: these offsets are stable Steam SDK ABI slots for the retail
SteamApps, SteamUGC, SteamGameServerUGC, and SteamGameServerUtils interfaces
used by Quake Live. Naming them in production source keeps the retained
workshop and app-id wrappers reviewable without changing their runtime policy.

## Source Reconstruction

The production wrapper layer now names these slots:

- `QL_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT`
- `QL_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT`
- `QL_STEAM_UGC_CREATE_QUERY_ALL_UGC_REQUEST_SLOT`
- `QL_STEAM_UGC_SEND_QUERY_UGC_REQUEST_SLOT`
- `QL_STEAM_UGC_GET_QUERY_UGC_RESULT_SLOT`
- `QL_STEAM_UGC_GET_QUERY_UGC_PREVIEW_URL_SLOT`
- `QL_STEAM_UGC_RELEASE_QUERY_UGC_REQUEST_SLOT`
- `QL_STEAM_UGC_SUBSCRIBE_ITEM_SLOT`
- `QL_STEAM_UGC_UNSUBSCRIBE_ITEM_SLOT`
- `QL_STEAM_UGC_GET_NUM_SUBSCRIBED_ITEMS_SLOT`
- `QL_STEAM_UGC_GET_SUBSCRIBED_ITEMS_SLOT`
- `QL_STEAM_UGC_GET_ITEM_STATE_SLOT`
- `QL_STEAM_UGC_GET_ITEM_INSTALL_INFO_SLOT`
- `QL_STEAM_UGC_GET_ITEM_DOWNLOAD_INFO_SLOT`
- `QL_STEAM_UGC_DOWNLOAD_ITEM_SLOT`

The mapped wrapper surface is:

- `QL_Steamworks_IsSubscribedApp`
- `QL_Steamworks_GetItemDownloadInfo`
- `QL_Steamworks_RequestAllUGCQuery`
- `QL_Steamworks_GetQueryUGCResult`
- `QL_Steamworks_GetQueryUGCPreviewURL`
- `QL_Steamworks_ReleaseQueryUGCRequest`
- `QL_Steamworks_GetNumSubscribedItems`
- `QL_Steamworks_GetSubscribedItems`
- `QL_Steamworks_GetItemInstallInfo`
- `QL_Steamworks_GetItemState`
- `QL_Steamworks_SubscribeItem`
- `QL_Steamworks_UnsubscribeItem`
- `QL_Steamworks_DownloadItem`
- `QL_Steamworks_ServerGetAppID`

SteamFriends avatar image slots, legacy SteamNetworking P2P slots, and
GameServer/GameServerStats slots are outside this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_ugc_apps_workshop_slot_constants_round_699 or steam_ugc_query_call_result_publication_lifecycle_tracks_round_619 or steam_ugc_get_all_query_appid_order_tracks_round_637 or client_steam_wrapper_cluster_reconstructs_retail_subscription_workshop_country_surface or server_game_server_wrappers_reconstruct_mapped_server_slots or workshop_mount_startup_reconstructs_retail_subscribed_item_import_path or operator_workshop_commands_reconstruct_retail_ugc_surface or steam_workshop_queue_helpers_track_retail_reference_rows" --tb=short` - 8 passed, 230 deselected.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 237 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
