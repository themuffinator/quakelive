# `src/common/platform/platform_services.c` Gap Note

Last updated: 2026-04-23

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; strict-retail Windows closure intentionally excludes this compatibility-only build lane.

## Why this file is still open

This file publishes build-disabled, externally-disabled, Steamworks, open-adapter, and hybrid descriptors. That keeps the repo honest, but it also means the file still encodes a bounded compatibility story instead of a retail-equivalent live-service surface.

## Observed facts

- Default builds return `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)` provider labels for auth, matchmaking, workshop, overlay, and stats.
- Runtime environment variables can also force the descriptor table into a disabled external-ecosystem mode.
- Hybrid and open-adapter provider labels remain explicit compatibility descriptors, not evidence of a retail live-service implementation.
- The common service layer now also publishes overall mode/policy summary labels for the online-service lane, and the client/server mirror those through ROM cvars instead of leaving the repo-wide boundary implicit.
- The client browser/advert bridge now mirrors the overlay descriptor through
  both the browser (`ui_browserAwesomiumProvider` /
  `ui_browserAwesomiumPolicy`) and advert
  (`ui_advertisementBridgeProvider` /
  `ui_advertisementBridgePolicy`) ROM cvars, with bounded advert lifecycle
  logs carrying the same provider/policy pair.
- The retained live-resource/avatar lane now mirrors the same descriptor
  through `ui_resourceBridgeProvider` and `ui_resourceBridgePolicy`, and the
  cgame avatar import now routes through the provider-aware resource stub path
  instead of silently returning before the compatibility diagnostics fire.
- The retained client identity/bootstrap lane now mirrors the overall
  mode/policy through `cl_identityBootstrapMode`,
  `cl_identityBootstrapPolicy`, `ui_subscriptionBridgeMode`, and
  `ui_subscriptionBridgePolicy`, with persona/country seed and UI
  app-subscription diagnostics naming the same compatibility lane instead of
  silently short-circuiting.
- The retained client voice lane now mirrors the overall online-services
  mode/policy through `cl_voiceServiceMode` and `cl_voiceServicePolicy`, and
  its `+voice` / `-voice` fallback diagnostics no longer leave the
  compatibility-only local speaking-state bridge implicit. The retained voice
  transport lane now also emits mode/policy-aware send/receive failure
  diagnostics instead of raw generic trace wording.
- The retained client workshop lane now mirrors the workshop descriptor
  through `cl_workshopProvider` and `cl_workshopPolicy`, and its bootstrap,
  download, callback-ignore, and filesystem-restart logs now carry the same
  provider/policy pair instead of generic Steam-only wording.
- The retained client rich-presence lane now also uses the matchmaking
  descriptor for both the main-menu bootstrap seed and first-snapshot
  match-start seed, and both paths log provider/policy-aware fallback
  diagnostics instead of silently skipping those updates when the current
  compatibility lane is disabled or unavailable.
- The retained client callback/bootstrap lane now also logs the active
  matchmaking/stats provider pair when the callback bundle stays on the
  compatibility fallback path, and the `stats_clear` registration gate now
  emits stats provider/policy-aware skip diagnostics instead of silently
  leaving that command unavailable. The retained client P2P session-request
  callback now also emits matchmaking provider/policy-aware acceptance and
  accept-failure diagnostics instead of a raw generic Steam trace line. The
  retained browser-event publish lane now also logs the mirrored overlay
  provider/policy pair when events are queued without a live view or bound
  window object, and its steady-state queue trace names the browser event and
  queue metadata instead of a raw `steam_event` dump. The retained
  microtransaction authorization callback now also emits an overlay
  provider/policy-aware callback diagnostic instead of a raw generic payload
  dump before forwarding its purchase update into that queue.
- The retained client web-host social/UGC export lane now includes the overall
  online-service mode/policy plus matchmaking and workshop provider/policy
  labels in `GetConfig`, logs provider-aware fallback diagnostics when Steam
  identity is unavailable for friend-list or UGC export calls, and includes the
  workshop provider/policy pair in `web.ugc.failed` instead of a bare failure
  payload.
- The retained dedicated-server auth lane now also emits provider/policy-aware
  connection-rejection diagnostics during auth-session bootstrap while keeping
  the legacy outward `Failed to authenticate with Steam: ...` message stable
  for existing consumers and log contracts.
- The retained dedicated-server Steam GameServer lane now also uses its
  mirrored provider/policy pair for callback-registration fallback diagnostics
  even in the build-disabled stub path, and it also uses that same pair for
  server-side P2P session-request ignored and accept-failure diagnostics
  instead of raw Steam-only wording. Its networking maintenance lane now also
  emits provider/policy-aware keepalive-send, relay-read, unknown-sender, and
  relay-send failure diagnostics instead of silently dropping those failures.
  Its published-state owner now also emits provider/policy-aware publication
  failure diagnostics for server metadata, score key-values, player data, and
  bot-count updates instead of silently assuming that the write surface always
  succeeds.
- The retained dedicated-server workshop lane now mirrors the workshop
  descriptor through `sv_workshopProvider` and `sv_workshopPolicy`, and the
  manual `steam_downloadugc`, `steam_subscribeugc`, and
  `steam_unsubscribeugc` command surfaces now emit provider/policy-aware
  diagnostics instead of generic Steam-only wording. Those commands also stop
  early when the current compatibility lane does not include a Steam UGC
  owner, which keeps the bounded workshop seam explicit instead of pretending
  that non-Steam workshop providers can satisfy Steam-specific operator flows.
- The retained dedicated-server stats lane now mirrors the stats descriptor
  through `sv_statsProvider` and `sv_statsPolicy`, and its request/session
  lifecycle diagnostics now carry the same provider/policy pair instead of raw
  Steam-only wording. Its build-disabled stat-delta and achievement
  owner/query stubs now also emit the same stats provider/policy-aware
  fallback diagnostics instead of silently returning.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `QL_StringRepresentsTrue` | `helper closed` | Helper-only function; not the primary remaining parity blocker by itself. |
| `QL_PlatformExternalEcosystemsDisabled` | `bounded compatibility` | Runtime kill-switch for the non-retail external ecosystem lane. |
| `QL_FinaliseDescriptor` | `bounded compatibility` | Normalises fallback labels for compatibility descriptors. |
| `QL_GetOnlineServicesModeLabel` | `gap owner` | Publishes the overall retained online-service mode label for runtime diagnostics. |
| `QL_GetOnlineServicesPolicyLabel` | `gap owner` | Publishes the overall retained online-service policy label for runtime diagnostics. |
| `QL_PlatformSteamworks_InitOnce` | `bounded compatibility` | Caches wrapper initialisation, but still sits under the bounded online-service policy. |
| `QL_BuildServiceTable` | `gap owner` | Builds the service descriptor table that still advertises build-disabled and compatibility-only providers. |
| `QL_GetPlatformServices` | `helper closed` | Helper-only function; not the primary remaining parity blocker by itself. |

## Closure target

- Keep the current explicit compatibility labels if the lane stays bounded, or replace them with a real open implementation backed by refreshed runtime proof.
- Do not close this note until the descriptor table and the auth, workshop,
  browser, advert, live-resource/avatar, voice, identity-bootstrap, and UI
  subscription callers all agree on the same policy and evidence story.
