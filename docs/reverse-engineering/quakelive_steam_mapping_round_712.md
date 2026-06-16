# Quake Live Steam Mapping Round 712: Mock SteamGameServer Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the SteamGameServer mock vtable used by the Steamworks
harness. Rounds 670, 675, and 678 named the production GameServer packet,
auth-session, lifecycle, and published-state ABI slots, but the harness still
installed the implemented mock methods through raw `0x?? / 4` indices. This
round promotes the mock interface to the same auditable vocabulary without
changing production behavior.

Focused parity estimate: **before 88% -> after 99%** for focused
SteamGameServer harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.06% -> 94.08%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `metadata.txt`, `exports.txt`, `imports.txt`, and `functions.csv` keep the
  retail GameServer owner boundary in the `quakelive_steam` binary.
- `functions.csv` preserves the GameServer owners at `00465a30`,
  `00465a40`, `00465a60`, `00465b00`, `00465d50`, `00465db0`, `00465df0`,
  `00465e80`, `00465fd0`, `004661e0`, `00466260`, `00466850`, `00466b90`,
  and `00466ed0`.
- `imports.txt` confirms the retained `SteamGameServer`,
  `SteamGameServerNetworking`, `SteamGameServerStats`, `SteamGameServerUGC`,
  `SteamGameServerUtils`, `SteamGameServer_Init`,
  `SteamGameServer_RunCallbacks`, and `SteamGameServer_Shutdown` imports.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners,
  plus their `sub_*` spellings, to the promoted GameServer aliases.

Observed Binary Ninja HLIL facts:

- `SteamServer_IsInitialized` returns the retained `data_e30358` initialized
  flag.
- `SteamServer_SetMaxPlayerCount` dispatches through `SteamGameServer + 0x30`.
- `SteamServer_SetKeyValuesFromInfoString` dispatches key/value pairs through
  `SteamGameServer + 0x50`.
- `SteamServer_PublishSteamID` reads server identity through
  `SteamGameServer + 0x28`.
- `SteamServer_HandleIncomingPacket` guards on initialization, then forwards
  host UDP data through `SteamGameServer + 0x94`.
- `SteamServer_EnableHeartbeats`, `SteamServer_CreateUnauthenticatedUserConnection`,
  and `SteamServer_GetPublicIP` use `SteamGameServer + 0x9c`, `+0x64`, and
  `+0x90`.
- `SteamServer_BeginAuthSession`, `SteamServer_EndAuthSession`, and
  `SteamServer_EndOrphanedAuthSessions` use `SteamGameServer + 0x74` and
  `+0x78`.
- `SteamServer_UpdatePublishedState` publishes max players, password state,
  server name, map name, game description, user data, bot count, and game tags
  through the retained GameServer slots.
- `SteamServer_Frame` drains outgoing packets through `SteamGameServer + 0x98`.
- `SteamServer_Init` initializes the GameServer interface and sets dedicated
  state, account login or anonymous login, heartbeat state, product, and game
  dir through the retained GameServer slots.

Inference: once production source names the `ISteamGameServer` ABI slots, the
harness should mirror that vocabulary instead of retaining a second raw-offset
table. Keeping `QLR_STEAM_GAMESERVER_SET_PRODUCT_SLOT` and
`QLR_STEAM_GAMESERVER_VTABLE_SLOT_COUNT` local to the harness preserves the
mock boundary while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the mock SteamGameServer slots:

- `QLR_STEAM_GAMESERVER_SET_PRODUCT_SLOT`
- `QLR_STEAM_GAMESERVER_SET_GAME_DESCRIPTION_SLOT`
- `QLR_STEAM_GAMESERVER_SET_GAME_DIR_SLOT`
- `QLR_STEAM_GAMESERVER_SET_DEDICATED_SLOT`
- `QLR_STEAM_GAMESERVER_LOG_ON_SLOT`
- `QLR_STEAM_GAMESERVER_LOG_ON_ANONYMOUS_SLOT`
- `QLR_STEAM_GAMESERVER_BLOGGED_ON_SLOT`
- `QLR_STEAM_GAMESERVER_GET_STEAM_ID_SLOT`
- `QLR_STEAM_GAMESERVER_SET_MAX_PLAYER_COUNT_SLOT`
- `QLR_STEAM_GAMESERVER_SET_BOT_PLAYER_COUNT_SLOT`
- `QLR_STEAM_GAMESERVER_SET_SERVER_NAME_SLOT`
- `QLR_STEAM_GAMESERVER_SET_MAP_NAME_SLOT`
- `QLR_STEAM_GAMESERVER_SET_PASSWORD_PROTECTED_SLOT`
- `QLR_STEAM_GAMESERVER_SET_KEY_VALUE_SLOT`
- `QLR_STEAM_GAMESERVER_SET_GAME_TAGS_SLOT`
- `QLR_STEAM_GAMESERVER_CREATE_UNAUTHENTICATED_USER_SLOT`
- `QLR_STEAM_GAMESERVER_UPDATE_USER_DATA_SLOT`
- `QLR_STEAM_GAMESERVER_BEGIN_AUTH_SESSION_SLOT`
- `QLR_STEAM_GAMESERVER_END_AUTH_SESSION_SLOT`
- `QLR_STEAM_GAMESERVER_GET_PUBLIC_IP_SLOT`
- `QLR_STEAM_GAMESERVER_HANDLE_INCOMING_PACKET_SLOT`
- `QLR_STEAM_GAMESERVER_GET_NEXT_OUTGOING_PACKET_SLOT`
- `QLR_STEAM_GAMESERVER_ENABLE_HEARTBEATS_SLOT`

`QLR_SteamAPI_SteamGameServer` now sizes the mock vtable with
`QLR_STEAM_GAMESERVER_VTABLE_SLOT_COUNT`, derived from the terminal heartbeat
slot, and installs the implemented lifecycle, identity, published-state,
auth-session, packet, and heartbeat methods through named slots.

SteamGameServerStats remains outside this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_gameserver_mock_slot_mirroring_round_712 or steam_gameserver_auth_session_vtable_slots_round_675 or steam_gameserver_lifecycle_published_state_slot_constants_round_678 or legacy_steam_p2p_voice_packet_slot_constants_round_670" --tb=short`
  - `4 passed, 247 deselected in 4.15s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `132 passed in 1.22s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `250 passed, 1 failed in 11.00s`; the failure is the pre-existing ZMQ Round 698 gate referencing missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
