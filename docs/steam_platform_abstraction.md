# Steam Platform Abstraction Plan

## Referenced `steam_api` Surface

Symbols imported by the stock launcher (`quakelive_steam.exe`) were extracted with `objdump -p references/original-assets/quakelive/quakelive_steam.exe`. The table groups the discovered entry points by the runtime feature they service.

| Feature | Symbols |
| --- | --- |
| Authentication & Session Bootstrap | `SteamAPI_Init`, `SteamAPI_Shutdown`, `SteamAPI_RunCallbacks`, `SteamAPI_RegisterCallback`, `SteamAPI_UnregisterCallback`, `SteamAPI_RegisterCallResult`, `SteamAPI_UnregisterCallResult`, `SteamApps`, `SteamUser`, `SteamFriends` |
| Matchmaking & Connectivity | `SteamMatchmaking`, `SteamMatchmakingServers`, `SteamGameServer`, `SteamGameServer_Init`, `SteamGameServer_RunCallbacks`, `SteamGameServer_Shutdown`, `SteamNetworking`, `SteamGameServerNetworking`, `SteamGameServerUtils` |
| Workshop & UGC | `SteamUGC`, `SteamGameServerUGC` |
| Overlay & Client Utilities | `SteamUtils` |
| Statistics & Telemetry | `SteamUserStats`, `SteamGameServerStats` |

These imports mirror the interfaces the original launcher expected from `steam_api.dll`, and inform which subsystems must be abstracted to remain functional without the proprietary runtime.

## Alternative Services and Data Contracts

For each feature class, the table below recommends an open substitute (or adapter layer) and documents the payload formats exchanged with the Quake Live launcher when Steamworks is not present.

| Feature | Steamworks Interface | Open Substitute | Request / Response Format |
| --- | --- | --- | --- |
| Authentication | `SteamAPI_*`, `SteamUser`, `SteamApps` | REST adapter exposing `/auth/ticket` backed by `OpenID` or JWT validation service | **Request** – JSON `{ "namespace": "steam" | "standalone", "ticket": "<base64>" }`; **Response** – JSON `{ "status": "accepted" | "denied", "user": { "id": "...", "entitlements": [...] } }` |
| Matchmaking | `SteamMatchmaking`, `SteamGameServer*`, `SteamNetworking` | [GameNetworkingSockets](https://github.com/ValveSoftware/GameNetworkingSockets) relay coupled with a lightweight lobby REST directory | **Lobby create/join** – JSON `{ "map": "<id>", "rules": {...}, "transport": "gns" }`; **Heartbeat** – protobuf frame mirroring GNS `CMsgSteamDatagramRelayAuthTicket` fields for NAT punch-through |
| Workshop | `SteamUGC`, `SteamGameServerUGC` | UGC REST service backed by object storage (e.g., S3-compatible) | **Query** – JSON `{ "owner": "<id>", "tag": ["..."], "page": n }`; **Download manifest** – YAML with SHA256 digests and CDN URLs |
| Overlay | `SteamUtils`, `SteamFriends` | In-process UI overlay rendered via Dear ImGui or HTML/CefSharp host | **Command channel** – JSON RPC `{ "op": "overlay.show", "view": "friends" }`; overlay responds with `{ "op": "overlay.event", "event": "view.closed" }` |
| Statistics | `SteamUserStats`, `SteamGameServerStats` | Metrics REST endpoint (e.g., Prometheus pushgateway adapter) | **Submit** – JSON `{ "match_id": "...", "metrics": { "frags": 12, "accuracy": 0.35 } }`; **Query** – JSON `{ "player": "<id>", "range": { "from": "ISO-8601", "to": "ISO-8601" } }` |

Each adapter is intentionally transport-agnostic—REST payloads can be served locally during development while production deployments point at hardened equivalents.

## Build-Time Configuration Flags

Two opt-in compile definitions govern which provider set is compiled:

- `QL_BUILD_STEAMWORKS=1` – links against the proprietary Steamworks runtime and enables the Steam-authored feature stubs.
- `QL_BUILD_OPEN_STEAM=1` – substitutes the open adapters. When both flags are present the build operates in *hybrid* mode, preferring Steamworks but transparently falling back to the open implementations.

`src/common/platform/platform_config.h` normalises the flags, ensuring at least one backend is active and exposing convenience predicates (`QL_PLATFORM_HAS_STEAMWORKS`, `QL_PLATFORM_HAS_OPEN_STEAM`, `QL_PLATFORM_BUILD_HYBRID`) for use across the tree.【F:src/common/platform/platform_config.h†L1-L34】 The service table exported by `src/common/platform/platform_services.c` publishes the selected providers for authentication, matchmaking, workshop, overlay, and statistics, so gameplay modules can query support without embedding Steam-specific knowledge.【F:src/common/platform/platform_services.c†L120-L207】

### Enabling Backends

Define the macros through your build system to toggle the desired providers:

- **MSBuild / Visual Studio** – pass `/DQL_BUILD_STEAMWORKS=<0|1>` and `/DQL_BUILD_OPEN_STEAM=<0|1>` via `/p:AdditionalOptions` when invoking `msbuild.exe` so the definitions reach the translation units compiled by `quake3.vcxproj`, which includes the authentication dispatcher and platform service table.【F:src/code/quake3.vcxproj†L563-L705】
- **GNU Make (Unix)** – export `CFLAGS="-DQL_BUILD_STEAMWORKS=<0|1> -DQL_BUILD_OPEN_STEAM=<0|1>"` before running `make`; the shared makefile feeds `$(CFLAGS)` into every compilation unit, including `platform_services.c`.【F:src/code/unix/Makefile†L325-L667】

When the flags change, the service table automatically advertises the active providers and `QL_Auth_ExecuteRequest` logs the provider name reported by the table (for example, “Steamworks”, “Open Steam Adapter”, or “Hybrid”).【F:src/common/platform/platform_services.c†L120-L191】【F:src/code/client/ql_auth.c†L86-L163】

## Mocked End-to-End Flow

`QL_Auth_ExecuteRequest` (implemented in `src/code/client/ql_auth.c`) now owns the end-to-end flow. Steam tickets and standalone launcher tokens are forwarded to the active backend discovered via `QL_GetPlatformServices`, so the dispatcher honours Steamworks-only, open-only, and hybrid builds without code changes.【F:src/code/client/ql_auth.c†L86-L163】 Each backend emits lifecycle logs and classifies the result as success, retry, or failure using the heuristics defined in `platform_services.c`.【F:src/common/platform/platform_services.c†L1-L118】 `QL_RequestExternalAuth` clears the response, invokes the dispatcher, and reports structured outcomes back to the caller, replacing the earlier mock helper entirely.【F:src/common/auth_credentials.c†L119-L151】

## QA Matrix

Quality assurance must validate three build flavours:

1. **Steamworks-enabled** (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=0`): confirm Steam APIs initialise, callbacks fire, and tickets trigger the Steam handler inside `QL_Auth_ExecuteRequest`. Validate matchmaking delegates to Steam-only descriptors.
2. **Open-source-only** (`QL_BUILD_STEAMWORKS=0`, `QL_BUILD_OPEN_STEAM=1`): ensure REST payloads follow the documented schemas, open adapters advertise support for all five features, and overlay commands surface through the JSON RPC bridge.
3. **Hybrid** (`QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1`): simulate Steam downtime by forcing `QL_Steamworks_AuthFlow` to reject a ticket and observe the fallback to the open adapter. Expect the client log `[auth] Hybrid result -> … Hybrid fallback accepted credential via open adapter …` while the service table advertises combined providers (e.g., matchmaking lists “Hybrid: Steamworks + GameNetworkingSockets”).【F:src/common/platform/platform_services.c†L165-L205】【F:src/code/client/ql_auth.c†L84-L150】

Each scenario should capture logs of the response payloads plus assertions that feature availability flags match expectations.
