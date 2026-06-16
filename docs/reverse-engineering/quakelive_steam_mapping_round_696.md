# Quake Live Steam Mapping Round 696: Client SteamMatchmakingServers Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the client `SteamMatchmakingServers` server-browser and
server-detail wrapper surface. The reconstruction goal was to replace raw
production vtable indices with named ABI slot constants for list requests,
request release/refresh, list-row detail reads, direct ping/player/rule probes,
and query cancellation.

Focused parity estimate: **before 90% -> after 99%** for focused client
SteamMatchmakingServers ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.78% -> 93.80%**.
Repo-wide parity remains **99%** because this pass names retained Steamworks
wrapper boundaries without changing the strict-retail Windows replacement
score and does not enable live Steam behavior by default.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `FUN_00461f70` / `sub_461f70` | `JSBrowserDetails_RequestServerDetails` | High | Starts the retained detail probes through `SteamMatchmakingServers + 0x34`, `+0x3c`, and `+0x38`. |
| `FUN_00462e80` / `sub_462e80` | `SteamBrowser_RefreshList` | High | Refreshes an active retained browser request through `SteamMatchmakingServers + 0x24`. |
| `FUN_00462eb0` / `sub_462eb0` | `JSBrowser_RequestServers` | High | Cancels the old request with `+0x18`, prepares `gamedir=baseq3`, and selects the list request slot. |
| `FUN_00463090` / `sub_463090` | `SteamBrowser_RequestServers` | High | Thin JS-facing wrapper that forwards into the retained request owner. |
| `FUN_004630b0` / `sub_4630b0` | `SteamBrowser_RequestServerDetails` | High | Thin JS-facing wrapper around the direct detail-query owner. |

Observed Binary Ninja HLIL anchors:

- `00461fab` calls `SteamMatchmakingServers + 0x34` for the ping query.
- `00461fbd` calls `SteamMatchmakingServers + 0x3c` for server rules.
- `00461fd8` calls `SteamMatchmakingServers + 0x38` for player details.
- `00462a8c` calls `SteamMatchmakingServers + 0x1c` to read a
  `gameserveritem_t`-style list row.
- `00462e9e` calls `SteamMatchmakingServers + 0x24` to refresh an active
  list request.
- `00462eeb` calls `SteamMatchmakingServers + 0x18` before replacing a
  retained list request.
- `00462f77`, `00462fad`, `00462fe3`, `00463016`, and `0046304c` cover the
  LAN, friends, favorites, history, and internet request slots at `+0x04`,
  `+0x08`, `+0x0c`, `+0x10`, and `+0x00`.

Observed Ghidra companion facts:

- `imports.txt` imports `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`.
- `functions.csv` contains the promoted browser and detail owner rows at
  `00461f70`, `00462e80`, `00462eb0`, `00463090`, and `004630b0`.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners to
  the retained browser and detail names.
- `tests/steamworks_harness.c` mirrors the mock `SteamMatchmakingServers`
  vtable assignments for the mocked list, detail, refresh, release, and cancel
  slots; Round 706 later promoted that mirror from raw offsets to named
  harness-local constants.

Inference: these offsets are stable `ISteamMatchmakingServers` ABI slots for
the retail SDK vintage used by Quake Live. Naming them in production source
makes the wrapper ownership auditable while preserving the harness vtable
assignments as the ABI control sample.

## Source Reconstruction

The production wrapper layer now names these `SteamMatchmakingServers` slots:

- `QL_STEAM_MATCHMAKING_SERVERS_REQUEST_INTERNET_SERVER_LIST_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_REQUEST_LAN_SERVER_LIST_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_REQUEST_FRIENDS_SERVER_LIST_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_REQUEST_FAVORITES_SERVER_LIST_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_REQUEST_HISTORY_SERVER_LIST_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_RELEASE_REQUEST_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_GET_SERVER_DETAILS_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_REFRESH_QUERY_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_PING_SERVER_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_PLAYER_DETAILS_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_SERVER_RULES_SLOT`
- `QL_STEAM_MATCHMAKING_SERVERS_CANCEL_SERVER_QUERY_SLOT`

The mapped wrapper surface is:

- `QL_Steamworks_RequestServerListForApp`
- `QL_Steamworks_GetServerListDetails`
- `QL_Steamworks_ReleaseServerListRequest`
- `QL_Steamworks_RefreshServerListRequest`
- `QL_Steamworks_RequestServerDetails`
- `QL_Steamworks_CancelServerQuery`

`SteamMatchmaking` lobby/favorite slots, `SteamFriends`, `SteamUser`,
`SteamUtils`, client stats, UGC, and GameServer slots are outside this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_matchmaking_servers_slot_constants_round_696 or client_browser_server_shims_reconstruct_retail_server_browser_surface" --tb=short` - 2 passed, 234 deselected.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 236 passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py -k "steam_matchmaking_servers_slot_constants_round_696" --tb=short` - 1 passed, 235 deselected after this note update.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
