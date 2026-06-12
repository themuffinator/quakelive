# Steam Retail Server-Browser AppID Interop - 2026-06-06

## Scope

Focused investigation and fix for the WebUI server list remaining empty when
the native `ISteamMatchmakingServers` path is available but the legacy Quake III
master fallback is disabled by the online-services policy.

## Evidence

- `CL_WEB_METHOD_REQUEST_SERVERS` dispatches to `CL_Steam_RequestServers`, and
  `CL_WEB_METHOD_REFRESH_LIST` dispatches to `CL_Steam_RefreshServerList`.
- `CL_Steam_RequestServers` already prefers the native Steam server-browser
  owner and only falls back to source LAN/global/favorites lists when the native
  provider is unavailable or cannot start a request.
- The source global fallback is intentionally disabled unless
  `QL_BUILD_ONLINE_SERVICES` and `QL_ENABLE_LEGACY_Q3_SERVICES` are both enabled,
  so a failed native browser request leaves the WebUI with no Internet rows in
  default policy builds.
- The previous native browser request and row readers used
  `QL_Steamworks_GetAppID()` for both request app id and returned-row
  validation. That preserves recovered current-app behavior but rejects public
  retail rows when the running Steam context is not the public Quake Live app.
- Public retail Quake Live server discovery is represented by Steam app id
  `282440`; the recovered/current-app `0x54100` path is retained for existing
  stats/workshop/current-app wrappers.
- Retail `SteamBrowser_RefreshList` (`0x00462E80`) only checks the retained
  list request handle and invokes `ISteamMatchmakingServers::RefreshQuery`
  through vtable offset `0x24`. It does not publish
  `servers.refresh.start`, does not set the browser active flag, and does not
  restart the request.
- Retail list-row callbacks publish response/failed events when the callback
  object and retained request are valid. They are not gated by the active
  refresh flag.
- Retail `RefreshComplete` (`0x00462E60`) clears the active flag and publishes
  `servers.refresh.end`, so a retained-handle refresh may produce an end event
  without a new start event.
- Retail Steam GameServer bootstrap at `0x00466FC1..0x004670A0` calls
  `SteamGameServer_Init(ip, 0, gamePort, 0xffff, mode, version)`, applies
  account/logon policy, disables heartbeats during bootstrap, sets product
  `"Quake Live"`, and sets game dir `"baseq3"`. The recovered call does not
  pass an app id parameter; the active GameServer app id is only observable
  later through `SteamGameServerUtils::GetAppID()`.

## Change

- Added `QL_STEAM_APPID_PUBLIC_RETAIL` and current-reference app-id constants.
- Split Steam browser helpers into current-app wrappers and explicit `ForApp`
  variants for list requests, list-row reads, browser response projection, ping
  response projection, and favorite add/remove.
- Added `cl_steamServerBrowserAppId`, defaulting to the public retail app id,
  plus `CL_SteamBrowser_GetDiscoveryAppID()`.
- Stored the selected app id on native list/detail request state so callbacks
  validate rows against the same app id that started the request.
- Relaxed returned-row validation only for the documented public retail
  (`282440`) and reference (`0x54100`) Quake Live app-id pair, so a valid row
  from either side of the SRP interop lane is not discarded after Steam has
  already produced it.
- Routed WebUI favorite add/remove through the same discovery app id used by
  Favorites/History browser requests.
- Matched retained-handle `RefreshList` behavior: native refresh now calls the
  existing Steam query handle without synthesizing `servers.refresh.start`,
  without rearming SRP's compatibility timeout, and without changing the active
  refresh state.
- List response and failure callbacks now rely on the callback object and
  retained request handle checks, matching retail's lack of an active-flag
  gate. `RefreshComplete` still publishes `servers.refresh.end` for callback
  completions even when the retained-handle refresh did not mark the browser
  active again.
- Re-audited the server publication side for the "vice versa" requirement.
  `Com_InitSteamGameServer`, `QL_Steamworks_ServerInitWithVersion`,
  `SV_SteamServerConnectedCallback`, and `SV_SteamServerUpdatePublishedState`
  already mirror the retail GameServer init, identity, metadata, and heartbeat
  publication lane. No additional source-side app-id override was added because
  the retail bootstrap has no such argument.

## Interop Notes

SRP clients now request and accept public retail Quake Live server rows by
default while preserving current-app Steam wrappers for recovered retail
surfaces that still need them. The only cross-app acceptance is the explicit
public/reference Quake Live pair; unrelated app ids are still rejected.

SRP servers already publish through the Steam GameServer heartbeat path when
online services are explicitly enabled and `sv_master` or `sv_masterN` is
configured. Retail-client visibility still depends on launching the server in a
Steam GameServer context whose app id is public Quake Live (`282440`), because
the retail GameServer init path does not provide an app-id parameter for the
wrapper to override. This keeps the source reconstruction retail-shaped while
making the runtime requirement explicit.

## Verification

- `python -m pytest tests/test_steamworks_harness.py -q`
- `python -m pytest tests/test_steamworks_harness.py::test_server_browser_detail_reader_projects_retail_gameserveritem_row tests/test_steamworks_harness.py::test_server_browser_response_projection_matches_retail_jsbrowser_payload_shape tests/test_steamworks_harness.py::test_server_browser_ping_response_projection_matches_retail_jsbrowserdetails_payload_shape -q --tb=short`
- `python -m pytest tests/test_platform_services.py::test_client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner tests/test_platform_services.py::test_client_browser_server_shims_reconstruct_retail_server_browser_surface -q`
- `python -m pytest tests/test_netcode_parity_manifest.py -q`
