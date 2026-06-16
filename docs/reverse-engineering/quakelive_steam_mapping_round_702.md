# Quake Live Steam Mapping Round 702: Steam Callback Payload Size Constants

Date: 2026-06-16

## Scope

This pass rechecked the Steamworks callback and call-result payload-size
surface. The source already retained raw payload structs and static size
assertions, but callback registration still passed anonymous raw `sizeof`
expressions. This round names those sizes with source constants so the
registration surface reads like the retail CCallback vtable contract exposed
by HLIL.

Focused parity estimate: **before 90% -> after 99%** for focused Steam
callback payload-size source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.86% -> 93.88%**.
Repo-wide parity remains **99%** because this pass clarifies the opt-in
Steamworks callback wiring without changing the strict-retail Windows
replacement score and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra function rows and symbol aliases:

| Retail address | Alias | HLIL return | Consumers |
| --- | --- | --- | --- |
| `00461060` | `SteamCallback_GetPayloadSize264` | `0x108` | `CCallback<class SteamCallbacks, struct GameRichPresenceJoinRequested_t, 0>` |
| `00461070` | `SteamCallback_GetPayloadSize16` | `0x10` | persona, lobby-created, game-lobby-join, item-installed callbacks |
| `00461080` | `SteamCallback_GetPayloadSize8` | `8` | client and server `P2PSessionRequest_t` callbacks |
| `00461090` | `SteamCallback_GetPayloadSize128` | `0x80` | game-server-change callback |
| `00463600` | `SteamCallback_GetPayloadSize20` | `0x14` | avatar image loaded and validate-auth-ticket callbacks |
| `00465680` | `SteamCallback_GetPayloadSize24` | `0x18` | UGC query call result, lobby enter/message/data/game/kicked, microtransaction, workshop download callbacks |
| `00465690` | `SteamCallback_GetPayloadSize32` | `0x20` | lobby chat update callback |
| `00465ea0` | `SteamCallback_GetPayloadSize4` | `4` | server connect failure and servers disconnected callbacks |
| `00467450` | `SteamCallback_GetPayloadSize1` | `1` | Steam servers connected callbacks |
| `00467480` | `SteamCallback_GetPayloadSize12` | `0x0c` | friend rich presence and game-server stats callbacks |

Observed Binary Ninja HLIL anchors:

- `sub_461050` loads a retained function pointer from the callback object and
  jumps through it for call-result dispatch.
- `sub_469310` calls the retained run function pointer at `arg1 + 0x10`.
- The client Steam callback vtables at `0053283c` through `0053288c` point
  their `vFunc_2` slots at the size thunks for rich-presence join,
  user-stats, persona-state, P2P session, game-server-change, and
  friend-rich-presence payloads.
- The Steam data-source avatar vtable at `00532b68` uses the 20-byte thunk.
- The lobby vtables at `00532e74` through `00532ee4` use the 16, 24, and
  32-byte thunks according to each retail payload type.
- The microtransaction vtable at `00532f1c`, server callback vtables at
  `005332ec` through `0053332c`, idSteamStats vtables at `005336c0` through
  `005336e0`, and workshop vtables at `0053385c` and `0053386c` use the same
  thunk family.

Inference: the retail source shape was a family of callback classes whose
third vtable function returned a fixed payload byte count. SRP's retained C
callback object uses a single `QL_Steamworks_CallbackGetSize` implementation
with a stored `payloadSize`, so named constants are the closest C
reconstruction of the observed C++ callback-size contract.

Compatibility note: `QL_STEAM_CALLBACK_SIZE_GET_TICKET_FOR_WEB_API_RESPONSE`
is a modern SDK adapter payload size, not a retail Quake Live import-table
fact. It is kept in the same source constant group because
`QL_Steamworks_RegisterWebApiAuthTicketCallback` uses the same retained
callback object path, while remaining optional and default-disabled.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now defines callback payload-size
constants for every retained raw Steamworks payload, including:

- `QL_STEAM_CALLBACK_SIZE_GAME_RICH_PRESENCE_JOIN_REQUESTED`
- `QL_STEAM_CALLBACK_SIZE_USER_STATS_RECEIVED`
- `QL_STEAM_CALLBACK_SIZE_PERSONA_STATE_CHANGE`
- `QL_STEAM_CALLBACK_SIZE_P2P_SESSION_REQUEST`
- `QL_STEAM_CALLBACK_SIZE_GAME_SERVER_CHANGE_REQUESTED`
- `QL_STEAM_CALLBACK_SIZE_FRIEND_RICH_PRESENCE_UPDATE`
- `QL_STEAM_CALLBACK_SIZE_AVATAR_IMAGE_LOADED`
- `QL_STEAM_CALLBACK_SIZE_UGC_QUERY_COMPLETED`
- `QL_STEAM_CALLBACK_SIZE_LOBBY_CHAT_UPDATE`
- `QL_STEAM_CALLBACK_SIZE_MICROTXN_AUTHORIZATION_RESPONSE`
- `QL_STEAM_CALLBACK_SIZE_VALIDATE_AUTH_TICKET_RESPONSE`
- `QL_STEAM_CALLBACK_SIZE_GS_STATS_RECEIVED`
- `QL_STEAM_CALLBACK_SIZE_GS_STATS_STORED`

The compile-time raw payload assertions now compare against those constants,
and all retained callback registrations pass the same constants into
`QL_Steamworks_PrepareCallbackObject`. This keeps the callback bundle,
avatar callback, server callback, lobby callback, microtransaction callback,
workshop callback, UGC call-result, and optional Web API auth-ticket callback
on one named payload-size vocabulary.

No callback ID, dispatch body, opt-in Steamworks guard, or live service policy
changed in this pass.

Round 716 later extended the `GetTicketForWebApiResponse_t` harness coverage so
missing callbacks, mismatched handles, non-OK Steam results, and oversized
callback ticket lengths exercise the same retained callback object and
cancellation paths.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_callback_payload_size_constants_round_702 or steam_callback_payload_size_thunks_and_server_max_players_track_retail_refs or platform_steamworks_reconstructs_retail_callback_bundle_registration_surface or steam_user_stats_presence_callbacks_track_round_616 or steam_lobby_callback_publication_lifecycle_tracks_round_617 or steam_workshop_callback_bootstrap_finalization_tracks_round_618 or steam_server_callback_registration_dispatch_lifecycle_tracks_round_620 or steam_datasource_avatar_response_lifecycle_tracks_round_621 or client_microtransaction_authorization_callback_tracks_retail_browser_payload" --tb=short` - 9 passed, 232 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 240 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
