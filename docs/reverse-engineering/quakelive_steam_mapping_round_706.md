# Quake Live Steam Mapping Round 706: Mock SteamMatchmakingServers Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the test-harness `SteamMatchmakingServers` mock vtable that
backs the native server-browser wrappers. Round 696 named the production
`QL_STEAM_MATCHMAKING_SERVERS_*` slots, but the harness still installed those
same methods through raw `0x?? / 4` indices. That left the opt-in test double
harder to audit than the production wrapper it verifies.

Focused parity estimate: **before 88% -> after 99%** for focused
SteamMatchmakingServers harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.94% -> 93.96%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves `FUN_00461f70,00461f70,107,0,unknown` for
  `JSBrowserDetails_RequestServerDetails`.
- `functions.csv` preserves `FUN_00462e80,00462e80,34,0,unknown` for
  `SteamBrowser_RefreshList`.
- `functions.csv` preserves `FUN_00462eb0,00462eb0,451,0,unknown` for
  `JSBrowser_RequestServers`.
- `functions.csv` preserves `FUN_00463090,00463090,20,0,unknown` for
  `SteamBrowser_RequestServers`.
- `functions.csv` preserves `FUN_004630b0,004630b0,87,0,unknown` for
  `SteamBrowser_RequestServerDetails`.
- `imports.txt` confirms the owning interface import:
  `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`.
- `references/analysis/quakelive_symbol_aliases.json` maps the same five
  functions, plus their `sub_*` spellings, to the promoted browser aliases.

Observed Binary Ninja HLIL facts:

- `JSBrowserDetails_RequestServerDetails` calls `SteamMatchmakingServers +
  0x34`, `+0x3c`, and `+0x38` for ping, rules, and player details.
- `JSBrowser_OnServerResponded` calls `SteamMatchmakingServers + 0x1c` to read
  the list-row `gameserveritem_t`.
- `SteamBrowser_RefreshList` calls `SteamMatchmakingServers + 0x24` to refresh
  the retained list request.
- `JSBrowser_RequestServers` calls `SteamMatchmakingServers + 0x18` when
  replacing an existing retained request.
- The list request owner selects `+0x04`, `+0x08`, `+0x0c`, `+0x10`, and
  `+0x00` for LAN, friends, favorites, history, and internet request modes.

Inference: once production names the retail interface slots, the harness should
mirror that vocabulary instead of retaining a second raw offset table. Keeping
`QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_INTERNET_SERVER_LIST_SLOT`,
`QLR_STEAM_MATCHMAKING_SERVERS_VTABLE_SLOT_COUNT`, and the related mock slot
macros local to `tests/steamworks_harness.c` preserves the test double's
independence while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the mock
`SteamMatchmakingServers` vtable slots:

- `QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_INTERNET_SERVER_LIST_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_LAN_SERVER_LIST_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_FRIENDS_SERVER_LIST_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_FAVORITES_SERVER_LIST_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_HISTORY_SERVER_LIST_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_RELEASE_REQUEST_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_GET_SERVER_DETAILS_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_REFRESH_QUERY_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_PING_SERVER_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_PLAYER_DETAILS_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_SERVER_RULES_SLOT`
- `QLR_STEAM_MATCHMAKING_SERVERS_CANCEL_SERVER_QUERY_SLOT`

The mock vtable array is now sized by
`QLR_STEAM_MATCHMAKING_SERVERS_VTABLE_SLOT_COUNT`, derived from the terminal
cancel-query slot. `QLR_SteamAPI_SteamMatchmakingServers` installs every mock
method through the named harness slots, matching the production
`QL_STEAM_MATCHMAKING_SERVERS_*` constants without sharing private production
macros across the test boundary.

No production wrapper behavior, browser request sequencing, live Steamworks
initialization, or online-service policy changed in this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_matchmaking_servers_mock_slot_mirroring_round_706 or steam_matchmaking_servers_slot_constants_round_696" --tb=short` - 2 passed, 243 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py::test_server_browser_helpers_use_mapped_matchmaking_servers_slots tests/test_steamworks_harness.py::test_server_browser_response_projection_matches_retail_jsbrowser_payload_shape tests/test_steamworks_harness.py::test_server_browser_detail_reader_projects_retail_gameserveritem_row tests/test_steamworks_harness.py::test_server_browser_ping_response_projection_matches_retail_jsbrowserdetails_payload_shape --tb=short` - 8 passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 244 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
