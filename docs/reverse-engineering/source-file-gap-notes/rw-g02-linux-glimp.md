# `src/code/unix/linux_glimp.c` Gap Note

Last updated: 2026-05-17

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; this legacy X11/GLX client host path is not currently closed as a retail-equivalent portability surface.

## Why this file is still open

The file is the retained Linux OpenGL/input host implementation, but the repo-wide audit still treats the Linux client, renderer, and input runtime as compatibility-only rather than part of the closed Windows replacement target.

## Observed facts

- The file still owns the Linux GLX window, gamma, input-grab, and renderer-thread glue path.
- `GLimp_Shutdown()` now no longer returns early solely because `ctx` is missing; it deactivates mouse state, detaches the current GLX context when the loader is still present, destroys partial contexts/windows only when present, restores VidMode/gamma state, closes the QGL log file, clears GLX globals, and always releases QGL state.
- `GLimp_EndFrame()` now refuses to swap when the display, window, or GLX swap pointer is absent, keeping shutdown and partial-init failure paths from falling through into stale GLX state.
- The input owner now deactivates retained X mouse grabs before clearing mouse availability, then forwards shutdown and latched `in_joystick` restarts through `IN_ShutdownJoystick()` / `IN_StartupJoystick()`, keeping the Linux mouse-active flag, joystick descriptor, and `ui_joyavail` state bounded while the broader input path remains compatibility-only.
- No current repo-wide claim says the Linux client/runtime is equivalent to the closed Windows target.
- The portability work completed so far has focused on bounded Unix helper restoration rather than on closing this renderer/input host lane.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `Q_stristr` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `XLateKey` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `CreateNullCursor` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `install_grabs` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `uninstall_grabs` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `X11_PendingInput` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `repeated_press` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `HandleEvents` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `KBD_Init` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `KBD_Close` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_ActivateMouse` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_DeactivateMouse` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_SetGamma` | `open portability owner` | Renderer gamma host path remains inside the still-open Linux client/runtime lane. |
| `GLimp_Shutdown` | `bounded compatibility` | Linux GL teardown now handles partial-init state, restores retained VidMode/gamma state, closes the QGL log, and releases QGL before clearing renderer state. |
| `GLimp_LogComment` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_StartDriverAndSetMode` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_SetMode` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_InitExtensions` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_InitGamma` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLW_LoadOpenGL` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `qXErrorHandler` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_Init` | `open portability owner` | Top-level Linux GL init path remains inside the unresolved portability lane. |
| `GLimp_EndFrame` | `bounded compatibility` | Linux swap/end-frame now guards missing display/window/swap state, but the GLX renderer host remains compatibility-only. |
| `GLimp_RenderThreadWrapper` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_SpawnRenderThread` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_RendererSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_FrontEndSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_WakeRenderer` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_RenderThreadWrapper` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_SpawnRenderThread` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_RendererSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_FrontEndSleep` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `GLimp_WakeRenderer` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_Init` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_Shutdown` | `bounded compatibility` | Linux input teardown now releases the retained X mouse grab, calls the joystick shutdown bridge, and clears mouse availability/activity state, but the broader Linux input host remains open. |
| `IN_Frame` | `open portability owner` | Linux input pump remains part of the unresolved non-Windows client path, now with bounded latched joystick restart handling. |
| `IN_Activate` | `open portability owner` | Linux active/inactive input state remains portability-owned. |
| `Sys_SendKeyEvents` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |
| `IN_StartupJoystick` | `open portability owner` | Linux joystick startup remains part of the unresolved portability lane. |
| `IN_JoyMove` | `bounded compatibility` | Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner. |

## Closure target

- Close the broader Linux client/runtime portability decision first, then rerun this file function-by-function with the chosen target in mind.
- If Linux client/runtime parity is not a target, keep this file explicitly classified as a compatibility-only host carry.
