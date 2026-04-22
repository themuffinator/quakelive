# `src/common/platform/platform_services.c` Gap Note

Last updated: 2026-04-22

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
  compatibility-only local speaking-state bridge implicit.

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
