# Quake Live Steam Mapping Round 693: Client SteamMatchmaking Lobby Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the client `SteamMatchmaking` lobby and favorite-server
wrapper surface. The reconstruction goal was to replace raw production vtable
indices with named ABI slot constants for lobby create/join/leave, lobby
membership/data access, lobby server publication, lobby invites, lobby chat,
and favorite-server mutation.

Focused parity estimate: **before 90% -> after 99%** for focused client
SteamMatchmaking lobby ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.76% -> 93.78%**.
Repo-wide parity remains **99%** because this pass names retained Steamworks
wrapper boundaries without changing the strict-retail Windows replacement
score and does not enable live Steam behavior by default.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `FUN_004645a0` / `sub_4645a0` | `SteamLobbyCallbacks_OnLobbyChatMessage` | High | Reads chat payloads through `SteamMatchmaking + 0x6c`. |
| `FUN_004649b0` / `sub_4649b0` | `SteamLobby_CreateLobby` | High | Calls `SteamMatchmaking + 0x34` with private lobby type 2. |
| `FUN_004649e0` / `sub_4649e0` | `SteamLobby_LeaveLobby` | High | Calls `SteamMatchmaking + 0x3c` for the active lobby. |
| `FUN_00464ac0` / `sub_464ac0` | `SteamLobby_SayLobby` | High | Sends NUL-terminated lobby chat through `SteamMatchmaking + 0x68`. |
| `FUN_00464b10` / `sub_464b10` | `SteamLobby_SetLobbyServer` | High | Checks owner through `SteamMatchmaking + 0x8c`, then publishes server data through `SteamMatchmaking + 0x74`. |
| `FUN_00464bf0` / `sub_464bf0` | `SteamLobbyCallbacks_OnLobbyCreated` | High | Seeds created lobby data through `SteamMatchmaking + 0x50`. |
| `FUN_00464d90` / `sub_464d90` | `SteamLobbyCallbacks_OnLobbyEnter` | High | Reads owner, data count, data pairs, member count, member limit, and member IDs. |
| `FUN_00465630` / `sub_465630` | `SteamLobby_JoinLobby` | High | Calls `SteamMatchmaking + 0x38`. |
| `FUN_00465840` / `sub_465840` | `SteamLobby_Init` | High | Registers the retained lobby command/callback surface. |

Observed Binary Ninja HLIL anchors:

- `004645ec` loads `SteamMatchmaking + 0x6c` for lobby chat entry reads.
- `004649d2` calls `SteamMatchmaking + 0x34` for lobby creation.
- `00464a0f` calls `SteamMatchmaking + 0x3c` for leaving the active lobby.
- `00464aff` calls `SteamMatchmaking + 0x68` for lobby chat send.
- `00464b71` and `00464ba2` call `SteamMatchmaking + 0x8c` and
  `SteamMatchmaking + 0x74` for lobby owner and lobby game-server update.
- `00464cc4` calls `SteamMatchmaking + 0x50` to seed lobby data.
- `00464fd6`, `0046503e`, `0046507e`, `004650c9`, `00465116`, and
  `0046519b` cover lobby owner, data count, data by index, member count,
  member limit, and member-by-index reads.
- `00465674` calls `SteamMatchmaking + 0x38` for lobby join.
- `00432742`, `00432798`, `004326bb`, and `00432729` anchor the
  favorite-server add/remove path to `SteamMatchmaking` after app-id lookup.

Observed Ghidra companion facts:

- `imports.txt` imports `SteamMatchmaking`.
- `functions.csv` contains the promoted lobby owner rows at `004645a0`,
  `004649b0`, `004649e0`, `00464ac0`, `00464b10`, `00464bf0`, `00464d90`,
  `00465630`, and `00465840`.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners to
  the retained lobby command/callback names.
- `tests/steamworks_harness.c` mirrors the same mock `SteamMatchmaking`
  vtable layout for the mocked favorite, create/join/leave, invite, chat,
  server-publication, and owner slots; Round 711 later promoted that mirror
  from raw offsets to named harness-local constants.

Inference: these offsets are stable `ISteamMatchmaking` ABI slots for the
retail SDK vintage used by Quake Live. Naming them in production source makes
the wrapper ownership auditable, and the later harness mirror keeps the same
ABI shape explicit without changing live-service behavior.

## Source Reconstruction

The production wrapper layer now names these `SteamMatchmaking` slots:

- `QL_STEAM_MATCHMAKING_ADD_FAVORITE_GAME_SLOT`
- `QL_STEAM_MATCHMAKING_REMOVE_FAVORITE_GAME_SLOT`
- `QL_STEAM_MATCHMAKING_CREATE_LOBBY_SLOT`
- `QL_STEAM_MATCHMAKING_JOIN_LOBBY_SLOT`
- `QL_STEAM_MATCHMAKING_LEAVE_LOBBY_SLOT`
- `QL_STEAM_MATCHMAKING_INVITE_USER_TO_LOBBY_SLOT`
- `QL_STEAM_MATCHMAKING_GET_NUM_LOBBY_MEMBERS_SLOT`
- `QL_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_BY_INDEX_SLOT`
- `QL_STEAM_MATCHMAKING_SET_LOBBY_DATA_SLOT`
- `QL_STEAM_MATCHMAKING_GET_LOBBY_DATA_COUNT_SLOT`
- `QL_STEAM_MATCHMAKING_GET_LOBBY_DATA_BY_INDEX_SLOT`
- `QL_STEAM_MATCHMAKING_SEND_LOBBY_CHAT_MSG_SLOT`
- `QL_STEAM_MATCHMAKING_GET_LOBBY_CHAT_ENTRY_SLOT`
- `QL_STEAM_MATCHMAKING_SET_LOBBY_GAME_SERVER_SLOT`
- `QL_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_LIMIT_SLOT`
- `QL_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT`

The mapped wrapper surface is:

- `QL_Steamworks_ReadLobbyChatMessage`
- `QL_Steamworks_CreateLobby`
- `QL_Steamworks_SetFavoriteServerForApp`
- `QL_Steamworks_LeaveLobby`
- `QL_Steamworks_JoinLobby`
- `QL_Steamworks_GetLobbyOwner`
- `QL_Steamworks_GetLobbyDataCount`
- `QL_Steamworks_SetLobbyData`
- `QL_Steamworks_GetLobbyDataByIndex`
- `QL_Steamworks_GetNumLobbyMembers`
- `QL_Steamworks_GetLobbyMemberLimit`
- `QL_Steamworks_GetLobbyMemberByIndex`
- `QL_Steamworks_SetLobbyServer`
- `QL_Steamworks_InviteUserToLobby`
- `QL_Steamworks_SayLobby`

`SteamFriends` invite overlay/game invite, `SteamUser` local-ID lookup, client
stats, UGC, server-browser, and GameServerUtils slots are outside this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_matchmaking_lobby_slot_constants_round_693 or lobby_social_wrappers_reconstruct_mapped_matchmaking_slots or client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner" --tb=short` - 3 passed, 231 deselected.
- `python -m pytest -q tests/test_platform_services.py -k "steam_matchmaking_lobby_slot_constants_round_693 or lobby_social_wrappers_reconstruct_mapped_matchmaking_slots or client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner or zmq_external_runtime_export_names_round_692" --tb=short` - 4 passed, 230 deselected.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 234 passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
