# Quake Live Steam Mapping Round 628: GameServer Auth Session Initialized Guards

Date: 2026-06-12

## Scope

This round maps the retail Steam GameServer auth-session wrappers and
reconstructs their initialized-state guards in the SRP platform layer. The
focused owners are `SteamServer_BeginAuthSession` and
`SteamServer_EndAuthSession`, promoted from `sub_465fd0` and `sub_4661e0`.

This is a launch/runtime fidelity repair only. It does not enable live Steam
behavior outside the existing `QL_BUILD_ONLINE_SERVICES` boundary.

## Retail Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `FUN_00465fd0`, `sub_465FD0`, and `sub_465fd0` to
  `SteamServer_BeginAuthSession`.
- The same alias map promotes `FUN_004661e0`, `sub_4661E0`, and `sub_4661e0`
  to `SteamServer_EndAuthSession`.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00465fd0,00465fd0,230,0,unknown` and
  `FUN_004661e0,004661e0,126,0,unknown`.
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  confirms the Steam GameServer import lane through
  `STEAM_API.DLL!SteamGameServer @ 0015918a`.
- Binary Ninja HLIL shows `sub_465fd0` checking `data_e30358 == 0` before the
  `SteamGameServer()` vtable slot `0x74` dispatch.
- Binary Ninja HLIL shows `sub_4661e0` checking `data_e30358 == 0` before the
  `SteamGameServer()` vtable slot `0x78` dispatch.

Observed fact: both retail auth-session wrappers gate on the retained
GameServer initialized flag before touching the GameServer auth API.

Inferred mapping: SRP's `state.gameServerInitialised` is the source-side mirror
for retail `data_e30358`, already set by the reconstructed GameServer init
owner and cleared by the reconstructed shutdown owner.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now makes the retail gate explicit
inside both public GameServer auth-session wrappers:

1. `QL_Steamworks_ServerBeginAuthSession` rejects missing Steam ID or ticket
   input, then rejects calls while `state.gameServerInitialised` is false,
   before resolving the GameServer interface and decoding the ticket.
2. `QL_Steamworks_ServerEndAuthSession` rejects a missing Steam ID, then
   rejects calls while `state.gameServerInitialised` is false, before resolving
   the GameServer interface.

The shared `QL_Steamworks_GetGameServer` helper still carries its own
`state.initialised`, `state.gameServerInitialised`, and `SteamGameServer`
guards. The new wrapper-level checks match the retail control-flow boundary
more directly and keep these public wrappers self-contained.

Follow-up Round 675 moves the public server auth wrappers from the older
dynamic flat-symbol bridge to the retail GameServer vtable slots. The flat
`SteamAPI_ISteamUser_BeginAuthSession` and
`SteamAPI_ISteamUser_EndAuthSession` exports remain loaded for the separate
client-side validation helper.

## Server Wiring

The existing server wiring remains unchanged:

- `SV_BeginPlatformAuthSession` calls
  `QL_Steamworks_ServerBeginAuthSession` before creating the retained stats
  session.
- `SV_SteamServerEndOrphanedAuthSessions` calls
  `QL_Steamworks_ServerEndAuthSession` while cleaning up stale client-owned
  Steam IDs.
- `SV_SteamServerValidateAuthTicketResponseCallback` remains the callback owner
  that accepts or drops clients after the async auth response.

## Validation

Added `test_steam_gameserver_auth_session_wrapper_guards_track_round_628` to
pin:

- promoted aliases for `sub_465fd0` and `sub_4661e0`;
- Ghidra function rows;
- Binary Ninja initialized-guard-to-auth-dispatch ordering;
- source wrapper guard ordering;
- the source GameServer vtable bridge for BeginAuthSession/EndAuthSession; and
- server call sites that begin, finalize, and clean up Steam auth sessions.

## Parity Estimate

Focused GameServer auth-session wrapper guard confidence:
**86% -> 99%**.

Focused Steam GameServer auth-session wiring confidence:
**93% -> 99%**.

overall Steam launch/runtime integration mapping confidence **93.58% -> 93.60%**.
