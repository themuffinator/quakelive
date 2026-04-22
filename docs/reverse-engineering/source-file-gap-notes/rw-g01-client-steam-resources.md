# `src/code/client/cl_steam_resources.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; live resource resolution is still a bounded bridge or stub lane.

## Why this file is still open

The client resource bridge reconstructs the menu-facing resource flow, but Steam-backed requests still devolve into stubs or fallback launch-resource paths whenever live services are disabled or unavailable.

## Observed facts

- `CL_Steam_RegisterShader()` now logs stubbed `steam://` requests with the
  active overlay provider/policy pair when the compatibility lane is disabled
  or unavailable.
- `CL_SteamDataSource_Request()` and `QLResourceInterceptor_OnRequest()` now
  keep the fallback story explicit by labeling Steam-resource failures and the
  launcher/web fallback owner with the same overlay provider/policy pair,
  rather than generic “Steam backend unavailable” wording.
- `QLResourceInterceptor_OnRequest()` falls back from SteamDataSource to launcher/web filesystem owners instead of proving a retail-equivalent live resource path.
- `CL_InitSteamResources()` now reports that the Steam resource bridge is
  disabled for the current overlay provider/policy pair while keeping the
  launcher/web fallback resource bridge active.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
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
| `CL_SteamDataSource_Request` | `gap owner` | Live resource requests still depend on bounded Steam or launcher compatibility backends. |
| `QLResourceInterceptor_OnRequest` | `gap owner` | Routes URI resources through the current fallback bridge instead of a closed retail-equivalent lane. |
| `CL_Steam_RegisterShader` | `gap owner` | Resource registration still stubs or falls back when the live service lane is disabled. |
| `CL_ClearSteamResourceCache` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `CL_InitSteamResources` | `bounded compatibility` | Publishes the build/runtime-disabled status of the bridge. |
| `CL_ShutdownSteamResources` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |
| `Sys_Steam_RequestURL` | `gap owner` | Public request bridge still returns launcher-backed compatibility data rather than a closed retail service surface. |
| `Sys_Steam_FreeRequestBuffer` | `helper closed` | Utility parser or cache helper; not the direct remaining parity blocker on its own. |

## Closure target

- Do not close this file until Steam-backed menu resources are either intentionally retained as bounded compatibility behavior or supported by a real open replacement path.
- If the lane remains bounded, keep the fallback and stub logging explicit so callers do not over-claim parity.
