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

The structural online-service lane now also exposes an overall mode/policy
summary in addition to the feature-by-feature descriptors. The common helpers
`QL_GetOnlineServicesModeLabel()` and `QL_GetOnlineServicesPolicyLabel()`
collapse the cached auth/service-table view into labels such as
`Build-disabled default (QL_BUILD_ONLINE_SERVICES=0)`,
`Steamworks compatibility lane`, `Open-adapter compatibility lane`,
`Hybrid compatibility lane`, or `Externally-disabled compatibility lane`,
paired with policy labels like
`compatibility-opt-in heuristic steamworks` or
`compatibility-opt-in heuristic hybrid`. The client and dedicated server mirror
those summary labels through the ROM cvars `cl_onlineServicesMode`,
`cl_onlineServicesPolicy`, `sv_onlineServicesMode`, and
`sv_onlineServicesPolicy` so the repo-wide online-service boundary is visible
without inspecting each per-feature provider cvar individually.【F:src/common/platform/platform_services.c†L16-L164】【F:src/code/client/cl_main.c†L368-L379】【F:src/code/server/sv_init.c†L114-L126】

That same structural summary now feeds the auth dispatcher's early exits too.
Policy-blocked Steam or standalone requests emit an explicit
`policy-blocked` lifecycle stage before transport dispatch, and failed Steam
ticket acquisition reports `ticket-request-failed`, with both response paths
naming the active overall mode/policy lane rather than falling back to generic
build/runtime wording.【F:src/code/client/ql_auth.c†L139-L325】

The browser/advert bridge now mirrors the active overlay descriptor into the
ROM cvars `ui_browserAwesomiumProvider`,
`ui_browserAwesomiumPolicy`, `ui_advertisementBridgeProvider`, and
`ui_advertisementBridgePolicy`. The retained advert lifecycle hooks also emit
provider-aware debug logs such as `Advert bridge init-ui ... via <provider>
[<policy>]` or `Advert bridge set-active ... via <provider> [<policy>]`, so
the compatibility-only advert bridge no longer hides behind the browser cvars
alone. The client overlay commands route blocked-command diagnostics through
the same provider-aware helpers. The workshop bootstrap likewise refuses to
pretend that non-Steam-UGC compatibility providers own the retained Steam
bootstrap path: it now mirrors the retained workshop seam through the ROM
cvars `cl_workshopProvider` and `cl_workshopPolicy`, logs the active workshop
provider/policy pair when the server publishes required workshop items, and
threads that same pair through download start, completion, callback-ignore,
filesystem-restart, and non-Steam bootstrap fallback messages when the current
descriptor is build-disabled, runtime-disabled, or otherwise not a Steam UGC
owner.【F:src/code/client/cl_cgame.c†L3215-L3490】【F:src/code/client/cl_main.c†L108-L2142】

The retained client matchmaking, stats, and social-overlay seams now follow the
same contract. `CL_Init` and `CL_Steam_InitCallbacks` mirror the active
descriptor labels through the ROM cvars `cl_matchmakingProvider`,
`cl_matchmakingPolicy`, `cl_statsProvider`, `cl_statsPolicy`,
`cl_socialOverlayProvider`, and `cl_socialOverlayPolicy`, while
`stats_clear`, `connect_lobby`, `clientviewprofile`, `clientfriendinvite`, the
main-menu and first-snapshot rich-presence seeds, and the client
callback-bundle fallback logs all spell out the current provider/policy pair
instead of silently reading like the retail Steam owner lane. The
`stats_clear` registration gate now also emits explicit provider-aware skip
diagnostics when the current compatibility lane cannot own that command during
bootstrap, rather than silently leaving the command unregistered. The retained
client P2P session-request callback now also emits explicit matchmaking
provider/policy-aware acceptance and accept-failure diagnostics instead of a
raw generic Steam trace line. The retained browser-event publish lane now also
uses the mirrored overlay provider/policy pair when events are queued before a
live view or bound window object exists, and its queue trace now reports the
named browser event plus payload/sequence detail instead of a raw `steam_event`
dump. The retained microtransaction authorization callback now also emits an
explicit overlay provider/policy-aware callback diagnostic before forwarding
its purchase update into that browser-event queue, instead of logging a raw
generic payload dump line.【F:src/code/client/cl_main.c†L176-L2397】【F:src/code/client/cl_cgame.c†L5410-L5441】

The retained client web-host export lane now carries the same boundary through
the browser-facing data contracts. `GetConfig` includes the overall
online-service mode/policy plus matchmaking and workshop provider/policy
labels, the friend-list and UGC export helpers log provider-aware fallback
diagnostics when Steam identity is unavailable, and `web.ugc.failed` includes
the workshop provider/policy pair instead of returning a bare failure result.
That keeps the Steam-authored social and UGC exports visibly bounded while
preserving the legacy array payload shape for browser callers.【F:src/code/client/cl_cgame.c†L350-L3165】

The retained client voice seam now mirrors the overall online-services lane
through the ROM cvars `cl_voiceServiceMode` and `cl_voiceServicePolicy`.
`+voice` and `-voice` keep the retail local speaking-state bridge as the
bounded fallback when Steam voice is unavailable, but they now emit explicit
`voice fallback` diagnostics naming the active overall mode/policy lane rather
than silently degrading to the local-only path. The retained voice transport
lane now also emits explicit mode/policy-aware diagnostics when the Steam voice
packet send, packet read, or decompress path fails, and it routes the
zero-byte-decompress diagnostic through that same compatibility label instead
of a raw generic trace line.【F:src/code/client/cl_main.c†L176-L2397】

The retained client identity/bootstrap and UI subscription seams now follow
that same structural summary too. `CL_Init` mirrors the current mode/policy
through the ROM cvars `cl_identityBootstrapMode`,
`cl_identityBootstrapPolicy`, `ui_subscriptionBridgeMode`, and
`ui_subscriptionBridgePolicy`, while the Steam persona-name seed, Steam
country seed, and the UI `IsSubscribedApp` import emit explicit
compatibility-lane diagnostics instead of silently short-circuiting as though
the retail Steam owner still existed. Persona lookup still falls back to
`anon`, and the country seed still leaves the userinfo field unchanged when no
country is available, but those retained compatibility outcomes are now named
at runtime too.【F:src/code/client/cl_main.c†L176-L2478】【F:src/code/client/cl_ui.c†L1556-L1594】

The retained live-resource bridge now follows the same overlay descriptor too.
`steam://` resource requests, avatar fetch failures, launcher/web fallback
failures, and the disabled resource-bridge startup path all log the active
overlay provider/policy pair instead of generic “Steam backend unavailable”
messages, which keeps the compatibility-only browser/resource lane explicit
when the menu falls back to launcher-backed data sources or stubs. The client
now also mirrors that retained lane through the ROM cvars
`ui_resourceBridgeProvider` and `ui_resourceBridgePolicy`, and the cgame
avatar import no longer short-circuits ahead of the provider-aware stub path,
so disabled `steam://avatar/...` lookups still report the current
compatibility owner instead of failing silently.【F:src/code/client/cl_steam_resources.c†L31-L733】【F:src/code/client/cl_cgame.c†L5046-L5063】

The dedicated-server owner now mirrors the same labeling into the ROM cvars
`sv_platformAuthProvider`, `sv_platformAuthPolicy`,
`sv_steamServerProvider`, `sv_steamServerPolicy`, `sv_workshopProvider`,
`sv_workshopPolicy`, `sv_statsProvider`, and `sv_statsPolicy`. Steam GameServer
bootstrap fallback logs, callback-registration diagnostics, connect/disconnect
notifications, and server auth telemetry all include the active provider/policy
pair. The retained server-side Steam P2P session-request path now uses that
same provider/policy pair for ignored unauthenticated requests and accept-call
failures too. The retained Steam GameServer networking maintenance lane now
also emits provider/policy-aware diagnostics when keepalive sends fail, inbound
relay reads fail, relay senders cannot be matched back to a live client, or
relay forwards fail. The retained published-state owner now also emits
provider/policy-aware diagnostics when max-player, password, hostname, map,
description, tag, score-key, player-data, or bot-count publication writes fail
instead of silently assuming the Steam GameServer owner is always writable. The
retained dedicated-server workshop operator lane now mirrors the workshop
descriptor too: the `steam_downloadugc`, `steam_subscribeugc`, and
`steam_unsubscribeugc` commands emit provider/policy-aware workshop lifecycle
diagnostics, and they now stop early when the current compatibility lane does
not include a Steam UGC owner instead of pretending that a non-Steam workshop
provider can service those Steam-specific commands. The retained GameServerStats lane now mirrors the same stats
descriptor and uses it in request/session lifecycle diagnostics too, while the
structured auth telemetry intentionally preserves the legacy `credential=steam`
field so existing log consumers keep their stable contract. The retained
auth-session bootstrap now also emits provider/policy-aware connection-reject
diagnostics when session setup fails, while keeping the outward
`Failed to authenticate with Steam: ...` drop message stable for existing
consumers. The callback-registration bootstrap now emits that same
provider/policy-aware fallback even in the build-disabled stub path, so the
dedicated-server callback lane no longer disappears silently before startup
diagnostics are emitted. The build-disabled `SV_SteamStats_AddFieldValue`,
`SV_SteamStats_UnlockAchievement`, and `SV_SteamStats_HasAchievement` stubs now
also emit stats provider/policy-aware diagnostics instead of silently no-oping
when the retained stats owner is unavailable.

## Mocked End-to-End Flow

`QL_Auth_ExecuteRequest` (implemented in `src/code/client/ql_auth.c`) now owns the end-to-end flow. Steam tickets and standalone launcher tokens are forwarded to the active backend discovered via `QL_GetPlatformServices`, so the dispatcher honours Steamworks-only, open-only, and hybrid builds without code changes.【F:src/code/client/ql_auth.c†L200-L325】 Each backend emits lifecycle logs that now include both the provider label and the companion compatibility policy label, classifies the result as success, retry, or failure using the heuristics defined alongside the dispatcher, and returns response payloads that explicitly identify the heuristic compatibility backend that produced them instead of reading like retail service verdicts. The policy-blocked and ticket-request-failed early exits now also surface the structural overall online-services mode/policy label, while hybrid fallback traces log the handoff into the open adapter before the fallback credential is dispatched, which keeps the bounded compatibility-only auth lane explicit during scripted QA capture too.【F:src/code/client/ql_auth.c†L111-L325】【F:src/common/platform/backends/platform_backend_steamworks.c†L1-L31】【F:src/common/platform/backends/platform_backend_open_steam.c†L1-L47】 `QL_RequestExternalAuth` clears the response, invokes the dispatcher, and reports structured outcomes back to the caller, replacing the earlier mock helper entirely.【F:src/common/auth_credentials.c†L120-L154】

## QA Matrix

Quality assurance must validate four build flavours:

1. **Default offline build** (`QL_BUILD_ONLINE_SERVICES=0`): confirm the service table reports `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)`, advert/web fetch paths short-circuit cleanly, and Steam/auth requests fail with policy messages instead of live-service attempts.
2. **Steamworks-enabled** (`QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=0`): confirm Steam APIs initialise, callbacks fire, and tickets trigger the Steam handler inside `QL_Auth_ExecuteRequest`. Validate matchmaking delegates to Steam-only descriptors.
3. **Open-source-only** (`QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=0`, `QL_BUILD_OPEN_STEAM=1`): ensure REST payloads follow the documented schemas, open adapters advertise support for all five features, and overlay commands surface through the JSON RPC bridge.
4. **Hybrid** (`QL_BUILD_ONLINE_SERVICES=1`, `QL_BUILD_STEAMWORKS=1`, `QL_BUILD_OPEN_STEAM=1`): simulate Steam downtime by providing a ticket flagged for retry and observe the fallback to the open adapter. Expect the client log to include an explicit `hybrid-fallback` handoff stage plus the final result `Hybrid fallback accepted credential via heuristic open adapter …` while the service table advertises combined providers (e.g., matchmaking lists “Hybrid: Steamworks + GameNetworkingSockets”).【F:src/common/platform/platform_services.c†L16-L89】【F:src/code/client/ql_auth.c†L152-L225】【F:src/code/client/ql_auth.c†L200-L273】

Each scenario should capture logs of the response payloads plus assertions that feature availability flags match expectations.
