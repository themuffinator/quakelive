# Quake Live Steam Host Parity Plan

## Scope

This plan summarizes what the `quakelive_steam.exe` HLIL shows is still missing and maps each subsystem to a proposed source location inside `src/code/`. It also outlines integration points with the existing engine startup flow.

## HLIL subsystem inventory (missing platform behaviors)

The HLIL parts for `quakelive_steam.exe` include a native Windows host that wires up Steam APIs, embeds a browser layer, and performs platform bootstrapping. The following behaviors are missing from the open-source tree:

- **Steam API loader/bindings**: direct imports of `SteamAPI_Init`, `SteamAPI_RunCallbacks`, `SteamAPI_RegisterCallback`, `SteamApps`, `SteamFriends`, `SteamUser`, `SteamMatchmaking`, `SteamNetworking`, `SteamUGC`, and the GameServer equivalents.
- **Steam client callbacks and presence**: callback registrations for rich presence, join requests, persona state, P2P session requests, and Steam overlay triggers.
- **Steam server auth / VAC flow**: GameServer auth ticket validation, VAC checks, Begin/EndAuthSession logging, and server connection state callbacks.
- **Lobby and matchmaking glue**: lobby callbacks and Steam server list response handlers used for browser queries.
- **Workshop/UGC download management**: callbacks for UGC query completion, item download/install, and explicit commands for download/subscribe/unsubscribe.
- **Microtransaction authorization**: callback handling for Steam microtransaction authorization.
- **Awesomium browser host + Steam data source**: initialization of `Awesomium::WebCore`, custom `SteamDataSource`, and Windows host font fallbacks.
- **Windows bootstrap / host glue**: COM initialization, common controls setup, Windows-only font fallback selection, and native event loop duties not represented in `src/code/`.

## HLIL subsystem → proposed source mapping

| HLIL subsystem | Example HLIL signals | Proposed source location | Notes |
| --- | --- | --- | --- |
| Steam API loader & shared bindings | `SteamAPI_Init`, `SteamAPI_RunCallbacks`, import table entries for Steam interfaces | `src/code/platform/steam/steam_api.c` + `src/code/platform/steam/steam_api.h` (new module) | Centralize dynamic loading, handle missing Steam DLL gracefully, expose feature flags to engine. |
| Steam client callbacks & presence | `CCallback<SteamCallbacks,...>`, rich presence join, persona state change | `src/code/platform/steam/steam_client.c` | Own callback registration and per-frame dispatch; interface with `cl_main.c` for UI updates. |
| Steam GameServer lifecycle | `SteamGameServer_Init`, `SteamGameServer_RunCallbacks`, `SteamGameServer_Shutdown` | `src/code/platform/steam/steam_server.c` | Integrate with server startup/shutdown and `sv_running`. |
| Auth/VAC handling | "VAC check timed out", "BeginAuthSession", "ValidateAuthTicketResponse" | `src/code/platform/steam/steam_auth.c` | Connect to `sv_vac`, `sv_referencedSteamworks`, and `sv_setSteamAccount`. |
| Lobby & matchmaking | `ISteamMatchmakingServerListResponse`, lobby callbacks | `src/code/platform/steam/steam_matchmaking.c` | Feed server browser and lobby UI; link with `cl_main.c` server list data. |
| Workshop/UGC downloads | `SteamUGCQueryCompleted_t`, `DownloadItemResult_t`, commands `steam_downloadugc` | `src/code/platform/steam/steam_workshop.c` | Wire commands to `Cmd_AddCommand`, map to content download flow. |
| Microtransactions | `MicroTxnAuthorizationResponse_t` callback | `src/code/platform/steam/steam_microtxn.c` | Required for store flow; likely feeds UI scripting. |
| Awesomium + Steam data source | `Awesomium::WebCore::Initialize`, `SteamDataSource` RTTI | `src/code/platform/steam/steam_web.c` (or `src/code/client/cl_web.c`) | Wrap Awesomium init, register custom data source, and expose to UI. |
| Windows host glue | COM init, common controls, font fallbacks from host | `src/code/win32/win_host.c` (new) | Own Windows-only bootstrap before `Com_Init`. |

> Note: The location names are **proposed**. If the team prefers consolidating platform code inside existing `src/code/win32/` or `src/code/client/`, adjust module placement accordingly.

## Integration points with engine startup

### Proposed initialization order (Windows launcher)

1. **Native host entry (new)**
	- Initialize Windows platform prerequisites (COM, common controls, DPI awareness, font fallbacks).
	- Determine Steam availability (load `steam_api.dll`) and set a boolean "steam enabled" state.
	- Initialize Awesomium WebCore and register the `SteamDataSource`.
	- Initialize Steam API core and register client/server callbacks.
	- Pass sanitized command line into `Com_Init`.

2. **Engine bootstrap (`Com_Init` → `Sys_Init` → `SV_Init`/`CL_Init`)**
	- Maintain current ordering in `src/code/qcommon/common.c` (Sys init, server init, client init).
	- Insert platform hooks before `SV_Init` and `CL_Init` to ensure Steam services are ready.
	- Register Steam-related cvars and commands before `CL_Init` runs its cvar setup so that `cl_platform` and Steam cache settings are visible.

3. **Per-frame callbacks**
	- Call `SteamAPI_RunCallbacks` and `SteamGameServer_RunCallbacks` from the main frame loop (`Com_Frame` or `CL_Frame`).
	- Feed network/auth state updates into `SV_` and `CL_` state machines.

4. **Shutdown**
	- Call `SteamAPI_Shutdown` and `SteamGameServer_Shutdown` during `Com_Shutdown` or `Sys_Quit`.

### Required/observed cvars

HLIL shows the following cvars that must exist and be registered during initialization:

- `cl_platform` (defaults to `1` in HLIL; already present in `src/code/client/cl_main.c`)
- `steam_maxLobbyClients` (default `16`)
- `sv_referencedSteamworks` (server info or system info flag)
- `sv_setSteamAccount` (server-side account token/identifier)

Existing Steam-adjacent cvars that should be wired into the platform layer:

- `cl_steamCachePersist`, `cl_steamCachePath` (from `src/code/client/cl_steam_resources.c`)
- `sv_vac` (already in `src/code/server/sv_init.c`, should map to VAC enforcement)

### Commands surfaced by the host

The HLIL shows explicit console commands that should be registered if the Steam workshop layer is reintroduced:

- `steam_downloadugc <itemid>`
- `steam_subscribeugc <itemid>`
- `steam_unsubscribeugc <itemid>`

## Next steps

- Break down the Steam host recovery into incremental modules (loader, client callbacks, server auth, workshop) to align with the engine reconstruction pace.
- Validate HLIL signals against existing `cl_steam_resources.c` and any Quake Live-specific VM changes before creating platform stubs.
- Decide whether platform glue should live under a new `src/code/platform/steam/` tree or be folded into `src/code/win32/` and `src/code/client/`.
