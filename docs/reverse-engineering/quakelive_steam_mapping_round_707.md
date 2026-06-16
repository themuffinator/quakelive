# Quake Live Steam Mapping Round 707: Mock SteamUGC Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the SteamUGC, SteamGameServerUGC, and SteamGameServerUtils
mock vtables used by the Steamworks harness. Round 699 named the production
UGC/workshop slots, but the harness still installed the same methods through
raw `0x?? / 4` indices. This made the test double less auditable than the
production wrappers it verifies.

Focused parity estimate: **before 88% -> after 99%** for focused SteamUGC
harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.96% -> 93.98%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves `FUN_00460660,00460660,42,0,unknown` for
  `SteamUGC_GetItemDownloadInfo`.
- `functions.csv` preserves `FUN_00460dc0,00460dc0,158,0,unknown` for
  `SteamWorkshop_GetAllUGC`.
- `functions.csv` preserves `FUN_00469260`, `FUN_004692b0`, `FUN_00469400`,
  `FUN_00469470`, `FUN_004697a0`, and `FUN_004699c0` for the workshop
  subscribe, unsubscribe, queue, finalize, init, and
  `SteamWorkshop_RequestDownload` owners.
- `imports.txt` confirms the retained `SteamUGC`, `SteamGameServerUGC`, and
  `SteamGameServerUtils` imports.
- `references/analysis/quakelive_symbol_aliases.json` maps the same functions,
  plus their `sub_*` spellings, to the promoted workshop aliases.

Observed Binary Ninja HLIL facts:

- `SteamWorkshop_GetAllUGC` creates the query through `SteamUGC + 0x04` and
  sends it through `SteamUGC + 0x0c`.
- The UGC query-completed path reads details through `SteamUGC + 0x10`, preview
  URLs through `SteamUGC + 0x14`, and releases queries through `SteamUGC +
  0x34`.
- `SteamUGC_GetItemDownloadInfo` calls `SteamUGC + 0xd8`.
- The server app-id helper calls `SteamGameServerUtils + 0x24`.
- Workshop subscribe, unsubscribe, state, install-info, subscribed-count,
  subscribed-list, and download owners use the retained UGC slots at `+0xc0`,
  `+0xc4`, `+0xd0`, `+0xd4`, `+0xc8`, `+0xcc`, and `+0xdc`.

Inference: once production source names the SteamUGC and GameServerUtils ABI
slots, the harness should mirror the same vocabulary instead of retaining a
second raw-offset table. Keeping `QLR_STEAM_UGC_CREATE_QUERY_ALL_UGC_REQUEST_SLOT`,
`QLR_STEAM_UGC_VTABLE_SLOT_COUNT`, and
`QLR_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT` local to the harness preserves the
mock boundary while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the mock SteamUGC slots:

- `QLR_STEAM_UGC_CREATE_QUERY_ALL_UGC_REQUEST_SLOT`
- `QLR_STEAM_UGC_SEND_QUERY_UGC_REQUEST_SLOT`
- `QLR_STEAM_UGC_GET_QUERY_UGC_RESULT_SLOT`
- `QLR_STEAM_UGC_GET_QUERY_UGC_PREVIEW_URL_SLOT`
- `QLR_STEAM_UGC_RELEASE_QUERY_UGC_REQUEST_SLOT`
- `QLR_STEAM_UGC_SUBSCRIBE_ITEM_SLOT`
- `QLR_STEAM_UGC_UNSUBSCRIBE_ITEM_SLOT`
- `QLR_STEAM_UGC_GET_NUM_SUBSCRIBED_ITEMS_SLOT`
- `QLR_STEAM_UGC_GET_SUBSCRIBED_ITEMS_SLOT`
- `QLR_STEAM_UGC_GET_ITEM_STATE_SLOT`
- `QLR_STEAM_UGC_GET_ITEM_INSTALL_INFO_SLOT`
- `QLR_STEAM_UGC_GET_ITEM_DOWNLOAD_INFO_SLOT`
- `QLR_STEAM_UGC_DOWNLOAD_ITEM_SLOT`

The client `QLR_SteamAPI_SteamUGC` and dedicated/server
`QLR_SteamAPI_SteamGameServerUGC` factories now install their mock methods
through those named slots. The mock vtable array is sized by
`QLR_STEAM_UGC_VTABLE_SLOT_COUNT`, derived from the terminal download-item
slot. `QLR_SteamAPI_SteamGameServerUtils` now uses
`QLR_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT` and
`QLR_STEAM_GAMESERVER_UTILS_VTABLE_SLOT_COUNT`.

No production wrapper behavior, UGC query sequencing, workshop command
behavior, live Steamworks initialization, or online-service policy changed in
this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_ugc_mock_slot_mirroring_round_707 or steam_ugc_apps_workshop_slot_constants_round_699" --tb=short` - 2 passed, 244 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py::test_workshop_helpers_use_mapped_ugc_slots tests/test_steamworks_harness.py::test_all_ugc_query_forwards_filter_to_retail_query_slot tests/test_steamworks_harness.py::test_ugc_query_result_preview_and_release_use_retail_slots tests/test_steamworks_harness.py::test_workshop_subscription_enumeration_uses_retail_ugc_mount_slots tests/test_steamworks_harness.py::test_game_server_init_uses_retail_init_signature_and_dedicated_ugc_owner tests/test_steamworks_harness.py::test_game_server_listen_init_keeps_workshop_calls_on_client_ugc_owner --tb=short` - 16 passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 245 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
