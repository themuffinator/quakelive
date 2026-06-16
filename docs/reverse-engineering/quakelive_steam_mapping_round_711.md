# Quake Live Steam Mapping Round 711: Mock SteamMatchmaking Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the SteamMatchmaking mock vtable used by the Steamworks
harness. Round 693 named the production lobby and favorite-server ABI slots,
but the harness still installed the implemented mock methods through raw
`0x?? / 4` indices. This pass promotes the mock interface to the same
auditable vocabulary without changing production behavior.

Focused parity estimate: **before 88% -> after 99%** for focused
SteamMatchmaking harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.04% -> 94.06%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves the lobby owners at `004645a0`, `004649b0`,
  `004649e0`, `00464ac0`, `00464b10`, `00464bf0`, `00464d90`, `00465630`,
  and `00465840`.
- `imports.txt` confirms the retained `SteamMatchmaking` import.
- `analysis_symbols.txt` preserves the lobby callback vtables for
  `LobbyCreated_t`, `LobbyEnter_t`, `LobbyChatMsg_t`, and
  `GameLobbyJoinRequested_t`.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners,
  plus their `sub_*` spellings, to the promoted lobby callback and command
  aliases.

Observed Binary Ninja HLIL facts:

- `SteamLobbyCallbacks_OnLobbyChatMessage` reads chat payloads through
  `SteamMatchmaking + 0x6c`.
- `SteamLobby_CreateLobby` calls `SteamMatchmaking + 0x34`.
- `SteamLobby_LeaveLobby` calls `SteamMatchmaking + 0x3c`.
- `SteamLobby_SayLobby` sends lobby chat through `SteamMatchmaking + 0x68`.
- `SteamLobby_SetLobbyServer` checks owner through `SteamMatchmaking + 0x8c`
  and publishes server data through `SteamMatchmaking + 0x74`.
- `SteamLobbyCallbacks_OnLobbyCreated` seeds lobby data through
  `SteamMatchmaking + 0x50`.
- `SteamLobbyCallbacks_OnLobbyEnter` reads owner, data count, data pairs,
  member count, member limit, and member IDs through the retained lobby slots.
- `SteamLobby_JoinLobby` calls `SteamMatchmaking + 0x38`.
- The favorite-server lane reaches `SteamMatchmaking` after the app-id lookup
  and uses the add/remove favorite slots.

Inference: once production source names the `ISteamMatchmaking` ABI slots, the
harness should mirror the vocabulary instead of retaining a second raw-offset
table. Keeping `QLR_STEAM_MATCHMAKING_CREATE_LOBBY_SLOT` and
`QLR_STEAM_MATCHMAKING_VTABLE_SLOT_COUNT` local to the harness preserves the
mock boundary while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the mock SteamMatchmaking slots:

- `QLR_STEAM_MATCHMAKING_ADD_FAVORITE_GAME_SLOT`
- `QLR_STEAM_MATCHMAKING_REMOVE_FAVORITE_GAME_SLOT`
- `QLR_STEAM_MATCHMAKING_CREATE_LOBBY_SLOT`
- `QLR_STEAM_MATCHMAKING_JOIN_LOBBY_SLOT`
- `QLR_STEAM_MATCHMAKING_LEAVE_LOBBY_SLOT`
- `QLR_STEAM_MATCHMAKING_INVITE_USER_TO_LOBBY_SLOT`
- `QLR_STEAM_MATCHMAKING_GET_NUM_LOBBY_MEMBERS_SLOT`
- `QLR_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_BY_INDEX_SLOT`
- `QLR_STEAM_MATCHMAKING_SET_LOBBY_DATA_SLOT`
- `QLR_STEAM_MATCHMAKING_GET_LOBBY_DATA_COUNT_SLOT`
- `QLR_STEAM_MATCHMAKING_GET_LOBBY_DATA_BY_INDEX_SLOT`
- `QLR_STEAM_MATCHMAKING_SEND_LOBBY_CHAT_MSG_SLOT`
- `QLR_STEAM_MATCHMAKING_GET_LOBBY_CHAT_ENTRY_SLOT`
- `QLR_STEAM_MATCHMAKING_SET_LOBBY_GAME_SERVER_SLOT`
- `QLR_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_LIMIT_SLOT`
- `QLR_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT`

`QLR_SteamAPI_SteamMatchmaking` now sizes the mock vtable with
`QLR_STEAM_MATCHMAKING_VTABLE_SLOT_COUNT`, derived from the terminal
get-lobby-owner slot, and installs the implemented favorite, lobby lifecycle,
invite, chat, server-publication, and owner methods through named slots.

SteamGameServer and SteamGameServerStats mock vtables remain outside this
pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_matchmaking_mock_slot_mirroring_round_711 or steam_matchmaking_lobby_slot_constants_round_693 or lobby_social_wrappers_reconstruct_mapped_matchmaking_slots or client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner" --tb=short` - 4 passed, 246 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 249 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
