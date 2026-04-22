# Steam Platform Abstraction Plan

## Referenced `steam_api` Surface

Symbols imported by the stock launcher (`quakelive_steam.exe`) were extracted with `objdump -p assets/quakelive/quakelive_steam.exe`. The table groups the discovered entry points by the runtime feature they service.

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

Quake Live-only online services are now an explicit divergence from the parity-first reconstruction goal and stay build-disabled by default. Three compile definitions govern whether any service provider is allowed to exist:

- `QL_BUILD_ONLINE_SERVICES=0` – default; disables advert fetching, Awesomium/web menu fetching, Steamworks, and open-Steam adapters, forcing the client onto offline fallbacks and stubs.
- `QL_BUILD_STEAMWORKS=1` – when the master flag is also enabled, links against the proprietary Steamworks runtime and enables the Steam-authored feature stubs.
- `QL_BUILD_OPEN_STEAM=1` – when the master flag is also enabled, substitutes the open adapters. When both provider flags are present the build operates in *hybrid* mode, preferring Steamworks but transparently falling back to the open implementations.

`src/common/platform/platform_config.h` normalises the flags, forcing the provider-specific toggles off whenever `QL_BUILD_ONLINE_SERVICES=0` and exposing convenience predicates (`QL_PLATFORM_HAS_ONLINE_SERVICES`, `QL_PLATFORM_HAS_STEAMWORKS`, `QL_PLATFORM_HAS_OPEN_STEAM`, `QL_PLATFORM_BUILD_HYBRID`) for use across the tree.【F:src/common/platform/platform_config.h†L1-L40】 The concrete authentication providers live in `src/common/platform/backends/platform_backend_steamworks.c` and `src/common/platform/backends/platform_backend_open_steam.c`; each translation unit compiles only when its corresponding `QL_BUILD_*` definition is set, and otherwise resolves to a lightweight stub provided by `platform_backend_auth.h`.【F:src/common/platform/backends/platform_backend_steamworks.c†L1-L31】【F:src/common/platform/backends/platform_backend_open_steam.c†L1-L47】【F:src/common/platform/platform_backend_auth.h†L1-L26】 The service table exported by `src/common/platform/platform_services.c` publishes either the selected providers or the build-disabled policy marker for authentication, matchmaking, workshop, overlay, and statistics, so gameplay modules can query support without embedding Steam-specific knowledge. `QL_DescribePlatformFeaturePolicy(...)` now provides the companion short policy label consumed by the auth logs and the client-side browser/workshop bridges, which keeps bounded compatibility-only surfaces explicit at runtime instead of silently reading like retail service owners.【F:src/common/platform/platform_services.c†L16-L110】

### Enabling Backends

Define the macros through your build system to toggle the desired providers:

- **MSBuild / Visual Studio** – the project defines user macros `QLBuildOnlineServices`, `QLBuildSteamworks`, and `QLBuildOpenSteam`, all defaulting to `0`. Override them on the command line (for example, `msbuild src\\code\\quakelive_steam.vcxproj /p:Configuration=Release /p:QLBuildOnlineServices=1 /p:QLBuildSteamworks=1 /p:QLBuildOpenSteam=0`) to control which backend files compile; each `ClCompile` entry forwards the values into `QL_BUILD_*` preprocessor definitions and skips translation units that are disabled.【F:src/code/quakelive_steam.vcxproj†L101-L706】
- **GNU Make (Unix)** – pass the make variables `QL_BUILD_ONLINE_SERVICES=<0|1>`, `QL_BUILD_STEAMWORKS=<0|1>`, and `QL_BUILD_OPEN_STEAM=<0|1>` when invoking `make`. The shared makefile forwards the toggles to every compile command, forces the provider flags off when the master flag is `0`, and only adds the relevant backend objects to the link step, so both the dynamic and static client builds stay in sync.【F:src/code/unix/Makefile†L1-L1708】

When the flags change, the service table automatically advertises the active providers and `QL_Auth_ExecuteRequest` logs both the provider name and the companion policy label reported by the table (for example, “Steamworks [compatibility-only]”, “Build-disabled (QL_BUILD_ONLINE_SERVICES=0) [compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)]”, or “Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS [compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)]”).【F:src/common/platform/platform_services.c†L16-L110】【F:src/code/client/ql_auth.c†L200-L273】

The browser/advert bridge now mirrors the active overlay descriptor into the ROM cvars `ui_browserAwesomiumProvider` and `ui_browserAwesomiumPolicy`, and the client overlay commands route blocked-command diagnostics through provider-aware log helpers. The workshop bootstrap likewise refuses to pretend that non-Steam-UGC compatibility providers own the retained Steam bootstrap path: it logs the active workshop provider/policy pair and falls back to the existing compatibility lane when the current descriptor is build-disabled, runtime-disabled, or otherwise not a Steam UGC owner.【F:src/code/client/cl_cgame.c†L3215-L3490】【F:src/code/client/cl_main.c†L108-L2140】

The retained live-resource bridge now follows the same overlay descriptor too.
`steam://` resource requests, avatar fetch failures, launcher/web fallback
failures, and the disabled resource-bridge startup path all log the active
overlay provider/policy pair instead of generic “Steam backend unavailable”
messages, which keeps the compatibility-only browser/resource lane explicit
when the menu falls back to launcher-backed data sources or stubs.

The dedicated-server owner now mirrors the same labeling into the ROM cvars
`sv_platformAuthProvider`, `sv_platformAuthPolicy`,
`sv_steamServerProvider`, and `sv_steamServerPolicy`. Steam GameServer
bootstrap fallback logs, callback-registration diagnostics, connect/disconnect
notifications, and server auth telemetry all include the active provider/policy
pair, while the structured auth telemetry intentionally preserves the legacy
`credential=steam` field so existing log consumers keep their stable contract.

## Mocked End-to-End Flow

`QL_Auth_ExecuteRequest` (implemented in `src/code/client/ql_auth.c`) now owns the end-to-end flow. Steam tickets and standalone launcher tokens are forwarded to the active backend discovered via `QL_GetPlatformServices`, so the dispatcher honours Steamworks-only, open-only, and hybrid builds without code changes.【F:src/code/client/ql_auth.c†L200-L273】 Each backend emits lifecycle logs that now include both the provider label and the companion compatibility policy label, and classifies the result as success, retry, or failure using the heuristics defined alongside the dispatcher.【F:src/code/client/ql_auth.c†L111-L225】 `QL_RequestExternalAuth` clears the response, invokes the dispatcher, and reports structured outcomes back to the caller, replacing the earlier mock helper entirely.【F:src/common/auth_credentials.c†L120-L154】

## QA Matrix

Quality assurance must validate four build flavours:

1. **Default offline build** (`QL_BUILD_ONLINE_SERVICES=0`): confirm the service table reports `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)`, advert/web fetch paths short-circuit cleanly, and Steam/auth requests fail with policy messages instead of live-service attempts.
2. **Steamworks-enabled** (`QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=0`): confirm Steam APIs initialise, callbacks fire, and tickets trigger the Steam handler inside `QL_Auth_ExecuteRequest`. Validate matchmaking delegates to Steam-only descriptors.
3. **Open-source-only** (`QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=0`, `QL_BUILD_OPEN_STEAM=1`): ensure REST payloads follow the documented schemas, open adapters advertise support for all five features, and overlay commands surface through the JSON RPC bridge.
4. **Hybrid** (`QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1`): simulate Steam downtime by providing a ticket flagged for retry and observe the fallback to the open adapter. Expect the client log `[auth] Hybrid result -> … Hybrid fallback accepted credential via open adapter …` while the service table advertises combined providers (e.g., matchmaking lists “Hybrid: Steamworks + GameNetworkingSockets”).【F:src/common/platform/platform_services.c†L16-L89】【F:src/code/client/ql_auth.c†L152-L225】【F:src/code/client/ql_auth.c†L200-L273】

Each scenario should capture logs of the response payloads plus assertions that feature availability flags match expectations.
