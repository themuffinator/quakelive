# `src/code/client/cl_steam_resources.c` Divergence Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Documented repo-wide divergence; live resource resolution remains a bounded bridge or stub lane.

## Why this file remains a documented divergence

The client resource bridge reconstructs the menu-facing resource flow, but Steam-backed requests still devolve into stubs or fallback launch-resource paths whenever live services are disabled or unavailable.

## Observed facts

- `CL_Steam_RegisterShader()` logs `UI: Steam resource request stubbed` when Steam services are disabled by build or runtime policy.
- `QLResourceInterceptor_OnRequest()` falls back from SteamDataSource to launcher/web filesystem owners instead of proving a retail-equivalent live resource path.
- `CL_InitSteamResources()` explicitly reports that the Steam resource bridge is disabled by build/runtime policy when the lane is unavailable.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `CL_GetSteamResourceServiceDescriptor` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_GetSteamResourceServiceProviderLabel` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_GetSteamResourceServicePolicyLabel` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_LogSteamResourceBridgeUnavailable` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_LogLauncherResourceFallbackUnavailable` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_LogSteamResourceRequestStubbed` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_RefreshSteamResourceBridgeCvars` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_IsSteamURL` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_IsURIResource` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_IsAvatarURL` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_ParseAvatarSizeToken` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_ParseAvatarURL` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_FindSlot` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_AssignSlot` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_BuildRendererName` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_ClearSlot` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamResources_RequestAvatarRGBA` | `bounded compatibility` | Still depends on the Steam-facing compatibility bridge rather than a repo-wide-closed live path. |
| `CL_SteamDataSource_ClearResponse` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamDataSource_GuessMimeType` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_SteamDataSource_Request` | `divergence owner` | Live resource requests still depend on bounded Steam or launcher compatibility backends. |
| `QLResourceInterceptor_OnRequest` | `divergence owner` | Routes URI resources through the current fallback bridge instead of a closed retail-equivalent lane. |
| `CL_Steam_RegisterShader` | `divergence owner` | Resource registration still stubs or falls back when the live service lane is disabled. |
| `CL_ClearSteamResourceCache` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_InitSteamResources` | `bounded compatibility` | Publishes the build/runtime-disabled status of the bridge. |
| `CL_ShutdownSteamResources` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `Sys_Steam_RequestURL` | `divergence owner` | Public request bridge still returns launcher-backed compatibility data rather than a closed retail service surface. |
| `Sys_Steam_FreeRequestBuffer` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |

## Maintenance expectations

- Keep the fallback and stub logging explicit while Steam-backed menu resources remain an intentional bounded compatibility story.
- If a real open replacement path is adopted later, refresh the request bridge and note accordingly.
