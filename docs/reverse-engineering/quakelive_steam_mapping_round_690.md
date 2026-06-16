# Quake Live Steam Mapping Round 690: Client Identity, Friends, And Utils Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the client Steamworks identity, social, and utility wrapper
surface owned by `SteamUser`, `SteamFriends`, and `SteamUtils`. The goal was
source-shape reconstruction rather than live-service expansion: replace raw
production vtable indices with named ABI slot constants while preserving the
existing guards, default outputs, SteamID word split, and opt-in online-service
policy.

Focused parity estimate: **before 90% -> after 99%** for focused client
identity/friends/utils ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.74% -> 93.76%**.
Repo-wide parity remains **99%** because this pass names retained Steamworks
wrapper boundaries without changing the strict-retail Windows replacement
score and does not enable live Steam behavior by default.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `FUN_00460610` / `sub_460610` | `SteamClient_SyncPersonaNameCvar` | High | Pulls `SteamFriends()` persona name slot 0 into the retained name cvar path. |
| `FUN_00460690` / `sub_460690` | `SteamUtils_GetIPCountry` | High | Tail-calls `SteamUtils + 0x10`. |
| `FUN_00460800` / `sub_460800` | `SteamCallbacks_OnPersonaStateChange` | High | Reads relationship, persona state/name, game info, nickname, and rich presence through `SteamFriends`. |
| `FUN_00460e60` / `sub_460e60` | `CL_Steam_OverlayCommand_f` | High | Activates user overlay through `SteamFriends + 0x74`. |
| `FUN_00461500` / `sub_461500` | `SteamClient_Init` | High | Seeds main-menu rich presence through `SteamFriends + 0xac`. |
| `FUN_00464b10` / `sub_464b10` | `SteamLobby_SetLobbyServer` | High | Uses `SteamUser + 0x08` for local identity before owner/server updates. |
| `FUN_00464bb0` / `sub_464bb0` | `SteamLobby_ShowInviteOverlay` | High | Uses the lobby invite overlay path through `SteamFriends`. |

Observed Binary Ninja HLIL anchors:

- `00460578` calls `SteamUser + 0x08` to fetch the local SteamID.
- `00460621` reaches `SteamFriends()` for persona-name sync.
- `004606a6` jumps through `SteamUtils + 0x10` for country lookup.
- `00460dd6` calls `SteamUtils + 0x24` for the app id.
- `0046096b`, `00460996`, `004609d7`, `00460a12`, `00460a61`,
  `00460a8e`, and `00460ad3` cover friend name, persona state,
  relationship, nickname, rich presence, and game-played summary fields.
- `00460f12` activates the friend/user overlay through `SteamFriends + 0x74`.
- `004615c3` seeds main-menu rich presence through `SteamFriends + 0xac`.
- `00464b34` and `00464bc7` anchor the lobby server and invite helper owners
  to `SteamUser` and `SteamFriends`.

Observed Ghidra companion facts:

- `imports.txt` imports `SteamFriends`, `SteamUser`, and `SteamUtils`.
- `functions.csv` contains the promoted owners at `00460610`, `00460690`,
  `00460800`, `00460e60`, `00461500`, `00464b10`, and `00464bb0`.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners to
  the retained client identity, overlay, init, and lobby names.
- `tests/steamworks_harness.c` mirrors mock vtable assignments at the same
  retail byte offsets; Round 708 later promoted the SteamFriends and
  SteamUtils mirror from raw offsets to named harness-local constants.

Inference: these offsets are stable Steamworks ABI slots within the retail
SDK vintage used by Quake Live. Naming them in production source makes the
retained wrapper ownership auditable while avoiding any claim that the
default-disabled online-service lane should contact live Steam services.

## Source Reconstruction

The production wrapper layer now names these client identity/social utility
slots:

- `QL_STEAM_USER_BLOGGED_ON_SLOT`
- `QL_STEAM_USER_GET_STEAM_ID_SLOT`
- `QL_STEAM_FRIENDS_GET_PERSONA_NAME_SLOT`
- `QL_STEAM_FRIENDS_GET_FRIEND_COUNT_SLOT`
- `QL_STEAM_FRIENDS_GET_FRIEND_BY_INDEX_SLOT`
- `QL_STEAM_FRIENDS_GET_FRIEND_RELATIONSHIP_SLOT`
- `QL_STEAM_FRIENDS_GET_FRIEND_PERSONA_STATE_SLOT`
- `QL_STEAM_FRIENDS_GET_FRIEND_PERSONA_NAME_SLOT`
- `QL_STEAM_FRIENDS_GET_FRIEND_GAME_PLAYED_SLOT`
- `QL_STEAM_FRIENDS_GET_PLAYER_NICKNAME_SLOT`
- `QL_STEAM_FRIENDS_SET_IN_GAME_VOICE_SPEAKING_SLOT`
- `QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_USER_SLOT`
- `QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_WEB_PAGE_SLOT`
- `QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_INVITE_DIALOG_SLOT`
- `QL_STEAM_FRIENDS_SET_RICH_PRESENCE_SLOT`
- `QL_STEAM_FRIENDS_GET_FRIEND_RICH_PRESENCE_SLOT`
- `QL_STEAM_FRIENDS_INVITE_USER_TO_GAME_SLOT`
- `QL_STEAM_UTILS_GET_IP_COUNTRY_SLOT`
- `QL_STEAM_UTILS_GET_APP_ID_SLOT`

The mapped wrapper surface is:

- `QL_Steamworks_GetPersonaName`
- `QL_Steamworks_GetIPCountry`
- `QL_Steamworks_GetAppID`
- `QL_Steamworks_IsUserLoggedOn`
- `QL_Steamworks_GetUserSteamID`
- `QL_Steamworks_SetInGameVoiceSpeaking`
- `QL_Steamworks_GetFriendCount`
- `QL_Steamworks_GetFriendByIndex`
- `QL_Steamworks_GetFriendSummary`
- `QL_Steamworks_GetFriendPersonaName`
- `QL_Steamworks_SetRichPresence`
- `QL_Steamworks_ActivateOverlayToUser`
- `QL_Steamworks_ActivateOverlayToWebPage`
- `QL_Steamworks_SetLobbyServer` for the `SteamUser + 0x08` local-ID lookup
- `QL_Steamworks_ShowInviteOverlay`
- `QL_Steamworks_InviteUserToGame`

The SteamUser production identity slots are named here, while the harness
SteamUser mirror remained outside this pass and was later promoted by Round
709. Matchmaking, UGC, server-browser, and game-server utility slots are left
for separate focused rounds where needed.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_client_identity_social_slot_constants_round_690 or steam_friends_enumeration_round_372 or steam_client_identity_utils_round_373 or client_main_menu_presence_seed_reconstructs_retail_bootstrap_status or steam_identity_bootstrap_persona_country_lifecycle_tracks_round_611 or lobby_social_wrappers_reconstruct_mapped_matchmaking_slots" --tb=short` - 6 passed, 225 deselected.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 231 passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
