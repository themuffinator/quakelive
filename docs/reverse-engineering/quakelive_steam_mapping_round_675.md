# Quake Live Steam Mapping Round 675: GameServer Auth Session Vtable Slots

Date: 2026-06-16

## Scope

This pass rechecked the retail Steam GameServer authentication-session wrappers
and tightened SRP's source reconstruction around the actual GameServer vtable
ABI. The previous guard reconstruction already matched the retail initialized
checks. This round names and uses the retail `SteamGameServer` auth-session
slots for the server wrappers themselves.

Focused parity estimate: **before 90% -> after 99%** for GameServer
BeginAuthSession/EndAuthSession ABI source-shape confidence. Overall Steam
launch/runtime integration mapping confidence moves from **93.66% -> 93.68%**.
Repo-wide parity remains **99%** because this pass closes a Steamworks
source-shape gap inside the opt-in online-service lane without changing the
strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Observed slot evidence |
| --- | --- | --- |
| `FUN_00465fd0` / `sub_465fd0` | `SteamServer_BeginAuthSession` | Guards on `data_e30358`, rejects duplicate auth sessions, then dispatches through `SteamGameServer + 0x74`. |
| `FUN_004661e0` / `sub_4661e0` | `SteamServer_EndAuthSession` | Guards on `data_e30358`, dispatches through `SteamGameServer + 0x78`, erases the auth-session tree entry, and logs completion. |
| `FUN_00466b90` / `sub_466b90` | `SteamServer_EndOrphanedAuthSessions` | Uses the same `SteamGameServer + 0x78` auth-session close slot while draining stale client-owned Steam IDs. |

Observed facts:

- `functions.csv` contains the mapped retail owners at `00465fd0`,
  `004661e0`, and `00466b90`.
- `imports.txt` confirms the retail GameServer interface import through
  `STEAM_API.DLL!SteamGameServer`.
- Binary Ninja HLIL shows the server begin path calling
  `(*(*SteamGameServer() + 0x74))`.
- Binary Ninja HLIL shows the server end path loading `*SteamGameServer()` and
  calling `(*(edx + 0x78))`.
- Binary Ninja HLIL shows orphan cleanup using `SteamGameServer + 0x78` for
  retained auth-session drain.

Inference: SRP's public server auth wrappers should use the GameServer vtable
slots for server-owned authentication, while the separate client-side
`QL_Steamworks_ValidateTicket` helper may continue using the loaded flat
`SteamAPI_ISteamUser_BeginAuthSession` and `SteamAPI_ISteamUser_EndAuthSession`
exports.

## Source Reconstruction

SRP now names the GameServer auth-session slots:

- `QL_STEAM_GAMESERVER_BEGIN_AUTH_SESSION_SLOT`
- `QL_STEAM_GAMESERVER_END_AUTH_SESSION_SLOT`

`QL_Steamworks_ServerBeginAuthSession` still keeps the existing guard order:
input validation, `state.gameServerInitialised`, logged-on check, GameServer
interface lookup, ticket decode, result mapping, and the return value. The
actual auth call now resolves `QL_SteamGameServer_BeginAuthSessionFn` from the
GameServer vtable and invokes it as a GameServer method.

`QL_Steamworks_ServerEndAuthSession` now resolves
`QL_SteamGameServer_EndAuthSessionFn` from the GameServer vtable before closing
the session.

The Steamworks harness exposes matching mock GameServer vtable entries at
`0x74` and `0x78`, delegating to the same mock auth result and lifecycle
helpers used by the flat-export path. Round 712 later promoted those mock
entries from raw offsets to the named harness-local
`QLR_STEAM_GAMESERVER_BEGIN_AUTH_SESSION_SLOT` and
`QLR_STEAM_GAMESERVER_END_AUTH_SESSION_SLOT` constants.

This pass does not enable live Steam behavior by default. It preserves the
existing `QL_BUILD_STEAMWORKS` and default-disabled `QL_BUILD_ONLINE_SERVICES`
policy.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k steam_gameserver_auth_session_vtable_slots_round_675`
- `python -m pytest -q tests/test_platform_services.py -k steam_gameserver_auth_session_wrapper_guards_track_round_628`
- `python -m pytest -q tests/test_steamworks_harness.py`
- `python -m pytest -q tests/test_platform_services.py`
- `git diff --check`
