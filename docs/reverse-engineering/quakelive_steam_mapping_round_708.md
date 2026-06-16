# Quake Live Steam Mapping Round 708: Mock SteamFriends And SteamUtils Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the SteamFriends and SteamUtils mock vtables used by the
Steamworks harness. Rounds 690 and 700 named the production identity, social,
overlay, rich-presence, avatar, country, app-id, and image-load slots, but the
harness still installed those same methods through raw `0x?? / 4` indices.
This pass promotes the test double to the same auditable vocabulary without
changing production behavior.

Focused parity estimate: **before 88% -> after 99%** for focused
SteamFriends/SteamUtils harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.98% -> 94.00%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves `FUN_00460610,00460610,70,0,unknown` for
  `SteamClient_SyncPersonaNameCvar`.
- `functions.csv` preserves `FUN_00460690,00460690,27,0,unknown` for
  `SteamUtils_GetIPCountry`.
- `functions.csv` preserves `FUN_00460800,00460800,948,0,unknown` for
  `SteamCallbacks_OnPersonaStateChange`.
- `functions.csv` preserves `FUN_00460e60,00460e60,195,0,unknown` for
  `CL_Steam_OverlayCommand_f`.
- `functions.csv` preserves `FUN_00460f30,00460f30,278,0,unknown` for
  `SteamClient_GetAvatarImageHandle`.
- `functions.csv` preserves `FUN_00461500,00461500,209,0,unknown` for
  `SteamClient_Init`, and `FUN_00464bb0,00464bb0,56,0,unknown` for
  `SteamLobby_ShowInviteOverlay`.
- `imports.txt` confirms the retained `SteamFriends` and `SteamUtils` imports.
- `analysis_symbols.txt` preserves the SteamDataSource and avatar callback
  vtable symbols used by the avatar response lane.
- `references/analysis/quakelive_symbol_aliases.json` maps the same functions,
  plus their `sub_*` spellings, to the promoted client identity, overlay,
  avatar, and lobby aliases.

Observed Binary Ninja HLIL facts:

- `SteamClient_SyncPersonaNameCvar` reaches `SteamFriends()` for the local
  persona name.
- `SteamUtils_GetIPCountry` calls `SteamUtils + 0x10`, and the app-id helper
  calls `SteamUtils + 0x24`.
- `SteamCallbacks_OnPersonaStateChange` reads friend persona name, persona
  state, relationship, nickname, rich presence, and game-played data through
  the retained SteamFriends slots.
- `CL_Steam_OverlayCommand_f` activates the user overlay through
  `SteamFriends + 0x74`.
- `SteamClient_Init` writes main-menu rich presence through `SteamFriends +
  0xac`.
- `SteamClient_GetAvatarImageHandle` requests the large avatar through
  `SteamFriends + 0x90`, reads dimensions through `SteamUtils + 0x14`, and
  copies pixels through `SteamUtils + 0x18`.

Inference: once production source names the SteamFriends and SteamUtils ABI
slots, the harness should mirror that vocabulary instead of retaining a second
raw-offset table. Keeping `QLR_STEAM_FRIENDS_GET_PERSONA_NAME_SLOT`,
`QLR_STEAM_FRIENDS_VTABLE_SLOT_COUNT`, and
`QLR_STEAM_UTILS_GET_IMAGE_RGBA_SLOT` local to the harness preserves the mock
boundary while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the mock SteamFriends slots:

- `QLR_STEAM_FRIENDS_GET_PERSONA_NAME_SLOT`
- `QLR_STEAM_FRIENDS_GET_FRIEND_COUNT_SLOT`
- `QLR_STEAM_FRIENDS_GET_FRIEND_BY_INDEX_SLOT`
- `QLR_STEAM_FRIENDS_GET_FRIEND_RELATIONSHIP_SLOT`
- `QLR_STEAM_FRIENDS_GET_FRIEND_PERSONA_STATE_SLOT`
- `QLR_STEAM_FRIENDS_GET_FRIEND_PERSONA_NAME_SLOT`
- `QLR_STEAM_FRIENDS_GET_FRIEND_GAME_PLAYED_SLOT`
- `QLR_STEAM_FRIENDS_GET_PLAYER_NICKNAME_SLOT`
- `QLR_STEAM_FRIENDS_SET_IN_GAME_VOICE_SPEAKING_SLOT`
- `QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_USER_SLOT`
- `QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_WEB_PAGE_SLOT`
- `QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_INVITE_DIALOG_SLOT`
- `QLR_STEAM_FRIENDS_GET_SMALL_FRIEND_AVATAR_SLOT`
- `QLR_STEAM_FRIENDS_GET_MEDIUM_FRIEND_AVATAR_SLOT`
- `QLR_STEAM_FRIENDS_GET_LARGE_FRIEND_AVATAR_SLOT`
- `QLR_STEAM_FRIENDS_SET_RICH_PRESENCE_SLOT`
- `QLR_STEAM_FRIENDS_GET_FRIEND_RICH_PRESENCE_SLOT`
- `QLR_STEAM_FRIENDS_INVITE_USER_TO_GAME_SLOT`

`QLR_SteamAPI_SteamFriends` now sizes the mock vtable with
`QLR_STEAM_FRIENDS_VTABLE_SLOT_COUNT`, derived from the terminal
invite-user-to-game slot, and installs every method through the named harness
slots.

`tests/steamworks_harness.c` also names the mock SteamUtils slots:

- `QLR_STEAM_UTILS_GET_IP_COUNTRY_SLOT`
- `QLR_STEAM_UTILS_GET_IMAGE_SIZE_SLOT`
- `QLR_STEAM_UTILS_GET_IMAGE_RGBA_SLOT`
- `QLR_STEAM_UTILS_GET_APP_ID_SLOT`

`QLR_SteamAPI_SteamUtils` now sizes the mock vtable with
`QLR_STEAM_UTILS_VTABLE_SLOT_COUNT`, derived from the app-id slot.

SteamUser, SteamUserStats, SteamNetworking, SteamMatchmaking, and GameServer
mock vtables remain outside this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_friends_utils_mock_slot_mirroring_round_708 or steam_client_identity_social_slot_constants_round_690 or steam_avatar_image_slot_constants_round_700" --tb=short` - 3 passed, 244 deselected.
- `python -m pytest -q tests/test_platform_services.py -k "steam_friends_utils_mock_slot_mirroring_round_708 or steam_client_identity_social_slot_constants_round_690 or steam_avatar_image_slot_constants_round_700 or steam_friends_voice_speaking_round_368 or steam_friends_enumeration_round_372 or steam_client_identity_utils_round_373" --tb=short` - 6 passed, 241 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py::test_load_avatar_returns_expected_rgba_payload tests/test_steamworks_harness.py::test_load_avatar_uses_requested_size_slot tests/test_steamworks_harness.py::test_activate_overlay_routes_dialog_and_identity tests/test_steamworks_harness.py::test_activate_overlay_to_web_page_routes_url tests/test_steamworks_harness.py::test_set_rich_presence_uses_mapped_friends_slot tests/test_steamworks_harness.py::test_steam_friends_enumeration_and_summary_use_mapped_slots tests/test_steamworks_harness.py::test_steam_friends_voice_speaking_wrapper_uses_retail_slot --tb=short` - 14 passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 246 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
