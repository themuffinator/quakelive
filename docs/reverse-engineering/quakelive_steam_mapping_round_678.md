# Quake Live Steam Mapping Round 678: GameServer Lifecycle And Published-State Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the retail Steam GameServer lifecycle and published-state
wrappers, then named the remaining GameServer vtable slots used by SRP's
production Steamworks shim. Earlier rounds reconstructed the initialized guard
shape and auth-session slots. This round closes the source-shape gap where the
same wrappers still carried raw `0x04` through `0x9c` vtable indices.

Focused parity estimate: **before 91% -> after 99%** for GameServer
lifecycle/published-state ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.68% -> 93.70%**.
Repo-wide parity remains **99%** because this pass clarifies the opt-in
Steamworks lane without changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Observed slot evidence |
| --- | --- | --- |
| `FUN_00465a60` / `sub_465a60` | `SteamServer_SetKeyValuesFromInfoString` | Iterates server-info pairs and dispatches each key/value through `SteamGameServer + 0x50`. |
| `FUN_00465b00` / `sub_465b00` | `SteamServer_PublishSteamID` | Reads the server identity through `SteamGameServer + 0x28`. |
| `FUN_00465db0` / `sub_465db0` | `SteamServer_EnableHeartbeats` | Toggles heartbeats through `SteamGameServer + 0x9c`. |
| `FUN_00465df0` / `sub_465df0` | `SteamServer_CreateUnauthenticatedUserConnection` | Creates the temporary server-owned identity through `SteamGameServer + 0x64`. |
| `FUN_00465e80` / `sub_465e80` | `SteamServer_GetPublicIP` | Tail-calls `SteamGameServer + 0x90`. |
| `FUN_00466260` / `sub_466260` | `SteamServer_UpdatePublishedState` | Publishes max players, password state, server name, map name, game description, bot count, game tags, key/value pairs, and user data through GameServer slots. |
| `FUN_00466ed0` / `sub_466ed0` | `SteamServer_Init` | Sets dedicated state, account login/anonymous login, initial heartbeat state, product, and game dir through GameServer slots after `SteamGameServer_Init`. |

Observed facts:

- `functions.csv` contains the mapped retail owners at `00465a60`,
  `00465b00`, `00465db0`, `00465df0`, `00465e80`, `00466260`, and
  `00466ed0`.
- `imports.txt` confirms the retail GameServer import and
  `SteamGameServer_Init` import.
- Binary Ninja HLIL shows the lifecycle and published-state owners dispatching
  through `SteamGameServer + 0x04`, `+0x08`, `+0x0c`, `+0x10`, `+0x14`,
  `+0x18`, `+0x20`, `+0x28`, `+0x30`, `+0x34`, `+0x38`, `+0x3c`, `+0x40`,
  `+0x50`, `+0x54`, `+0x64`, `+0x6c`, `+0x90`, and `+0x9c`.
- The Steamworks harness exposes the same mock GameServer vtable layout.
  Round 712 later promoted that mock layout from raw offsets to named
  harness-local `QLR_STEAM_GAMESERVER_*` constants, which keeps the constants
  a source reconstruction improvement rather than a behavior change.

Inference: these wrappers should continue calling the same vtable entries, but
the production shim should name each GameServer slot so later work can reason
about the ABI directly instead of rediscovering offset meaning from each call
site.

## Source Reconstruction

SRP now names the GameServer lifecycle and published-state slots:

- `QL_STEAM_GAMESERVER_SET_PRODUCT_SLOT`
- `QL_STEAM_GAMESERVER_SET_GAME_DESCRIPTION_SLOT`
- `QL_STEAM_GAMESERVER_SET_GAME_DIR_SLOT`
- `QL_STEAM_GAMESERVER_SET_DEDICATED_SLOT`
- `QL_STEAM_GAMESERVER_LOG_ON_SLOT`
- `QL_STEAM_GAMESERVER_LOG_ON_ANONYMOUS_SLOT`
- `QL_STEAM_GAMESERVER_BLOGGED_ON_SLOT`
- `QL_STEAM_GAMESERVER_GET_STEAM_ID_SLOT`
- `QL_STEAM_GAMESERVER_SET_MAX_PLAYER_COUNT_SLOT`
- `QL_STEAM_GAMESERVER_SET_BOT_PLAYER_COUNT_SLOT`
- `QL_STEAM_GAMESERVER_SET_SERVER_NAME_SLOT`
- `QL_STEAM_GAMESERVER_SET_MAP_NAME_SLOT`
- `QL_STEAM_GAMESERVER_SET_PASSWORD_PROTECTED_SLOT`
- `QL_STEAM_GAMESERVER_SET_KEY_VALUE_SLOT`
- `QL_STEAM_GAMESERVER_SET_GAME_TAGS_SLOT`
- `QL_STEAM_GAMESERVER_CREATE_UNAUTHENTICATED_USER_SLOT`
- `QL_STEAM_GAMESERVER_UPDATE_USER_DATA_SLOT`
- `QL_STEAM_GAMESERVER_GET_PUBLIC_IP_SLOT`
- `QL_STEAM_GAMESERVER_ENABLE_HEARTBEATS_SLOT`

The public wrappers now resolve through those names while retaining the same
guard order, fastcall signatures, and harness-backed mock behavior.

This pass does not enable live Steam behavior by default. It preserves the
existing `QL_BUILD_STEAMWORKS` and default-disabled `QL_BUILD_ONLINE_SERVICES`
policy.

## Validation

Completed 2026-06-16:

- `python -m pytest -q tests/test_platform_services.py -k "steam_gameserver_lifecycle_published_state_slot_constants_round_678 or steam_gameserver_published_state_wrapper_guards_track_round_631 or steam_gameserver_bootstrap_setter_wrapper_guards_track_round_632 or steam_gameserver_utility_public_ip_wrapper_guards_track_round_636" --tb=short`
  - `4 passed, 219 deselected in 7.24s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `223 passed in 16.82s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `132 passed in 2.63s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
