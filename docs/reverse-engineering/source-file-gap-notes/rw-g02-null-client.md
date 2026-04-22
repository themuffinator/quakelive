# `src/code/null/null_client.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; the file is a retained compatibility shim for browser, advert, and client entry points.

## Why this file is still open

This file carries the modern null-client contract more honestly than the older stubs did, but almost every browser, advert, and client-owner entry point still resolves to a no-op or compatibility-safe default.

## Observed facts

- Browser state is forced off through `ui_browserAwesomium` and `web_browserActive` cvars.
- Live-view, bound-window-object, cursor, event-publication, and advert-bridge entry points remain null-host stubs.
- The repo-wide audit still treats the null client/browser/advert lane as compatibility-only rather than closed parity.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `CL_NullResetAdvertisementBridgeState` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_NullRefreshBrowserCvars` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Shutdown` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Init` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_MouseEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `Key_WriteBindings` | `bounded compatibility` | Null-client compatibility shim. |
| `Key_EnumerateBindings` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Frame` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_PacketEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_CharEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_Disconnect` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_MapLoading` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_GameCommand` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_KeyEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `UI_GameCommand` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_RefreshOnlineServicesBridgeState` | `open portability owner` | Explicitly forces the browser/online-service cvars into the null-host state. |
| `CL_WebHost_Init` | `open portability owner` | Initialises only the null browser-host compatibility state. |
| `CL_WebHost_Shutdown` | `open portability owner` | Shuts down only the null browser-host compatibility state. |
| `CL_WebHost_Frame` | `open portability owner` | No-op browser-host frame pump for the null runtime. |
| `CL_WebHost_HasLiveView` | `open portability owner` | Always false in the null compatibility host. |
| `CL_WebHost_HasBoundWindowObject` | `open portability owner` | Always false in the null compatibility host. |
| `CL_WebHost_GetCursorHandle` | `open portability owner` | Always returns `NULL`. |
| `CL_WebHost_NotifyAppActivation` | `bounded compatibility` | No-op null-host activation shim. |
| `CL_WebView_PublishEvent` | `open portability owner` | Null-host publication stub for browser events. |
| `CL_WebView_InvokeCommNotice` | `open portability owner` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameError` | `open portability owner` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameEnd` | `open portability owner` | Null-host browser bridge stub. |
| `CL_WebView_PublishCvarChange` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_WebView_PublishBindChanged` | `open portability owner` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameStart` | `open portability owner` | Null-host browser bridge stub. |
| `CL_WebView_PublishGameDemo` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_WebView_PublishGameScreenshot` | `open portability owner` | Null-host browser bridge stub. |
| `CL_WebView_OnMouseMove` | `open portability owner` | Null-host input bridge stub. |
| `CL_WebView_OnMouseButtonEvent` | `open portability owner` | Null-host input bridge stub. |
| `CL_WebView_OnMouseWheelEvent` | `open portability owner` | Null-host input bridge stub. |
| `CL_WebView_OnKeyEvent` | `open portability owner` | Null-host input bridge stub. |
| `CL_AdvertisementBridge_RefreshLoadingViewParameters` | `open portability owner` | Null advert bridge shim. |
| `CL_AdvertisementBridge_UpdateLoadingViewParameters` | `open portability owner` | Null advert bridge shim. |
| `CL_AdvertisementBridge_InitUI` | `open portability owner` | Null advert bridge shim. |
| `CL_AdvertisementBridge_ActivateAdvert` | `open portability owner` | Null advert bridge shim. |
| `CL_AdvertisementBridge_SetActiveAdvert` | `open portability owner` | Null advert bridge shim. |
| `CL_ForwardCommandToServer` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_ConsolePrint` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_JoystickEvent` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_InitKeyCommands` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_CDDialog` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_FlushMemory` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_StartHunkUsers` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_ShutdownAll` | `bounded compatibility` | Null-client compatibility shim. |
| `CL_CDKeyValidate` | `bounded compatibility` | Null-client compatibility shim. |

## Closure target

- If the null client remains only a portability shim, keep these no-op bridges explicit and leave the repo-wide portability gap open.
- Do not close the file unless the repo begins claiming a richer null-host parity target than the current compatibility boundary.
