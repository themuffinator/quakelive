# `src/code/unix/linux_glimp.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; this legacy X11/GLX client host path is not currently closed as a retail-equivalent portability surface.

## Why this file is still open

The file is the retained Linux OpenGL/input host implementation, but the repo-wide audit still treats the Linux client, renderer, and input runtime as compatibility-only rather than part of the closed Windows replacement target.

## Observed facts

- The file still owns the Linux GLX window, gamma, input-grab, and renderer-thread glue path.
- No current repo-wide claim says the Linux client/runtime is equivalent to the closed Windows target.
- The portability work completed so far has focused on bounded Unix helper restoration rather than on closing this renderer/input host lane.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `Q_stristr` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `XLateKey` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `CreateNullCursor` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `install_grabs` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `uninstall_grabs` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `X11_PendingInput` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `repeated_press` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `HandleEvents` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `KBD_Init` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `KBD_Close` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `IN_ActivateMouse` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `IN_DeactivateMouse` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_SetGamma` | `open portability owner` | Renderer gamma host path remains inside the still-open Linux client/runtime lane. |
| `GLimp_Shutdown` | `open portability owner` | Linux GL teardown still belongs to the unresolved portability host surface. |
| `GLimp_LogComment` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLW_StartDriverAndSetMode` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLW_SetMode` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLW_InitExtensions` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLW_InitGamma` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLW_LoadOpenGL` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `qXErrorHandler` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_Init` | `open portability owner` | Top-level Linux GL init path remains inside the unresolved portability lane. |
| `GLimp_EndFrame` | `open portability owner` | Linux swap/end-frame host path is not closed repo-wide. |
| `GLimp_RenderThreadWrapper` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_SpawnRenderThread` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_RendererSleep` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_FrontEndSleep` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_WakeRenderer` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_RenderThreadWrapper` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_SpawnRenderThread` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_RendererSleep` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_FrontEndSleep` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `GLimp_WakeRenderer` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `IN_Init` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `IN_Shutdown` | `open portability owner` | Linux input teardown stays in the open portability lane. |
| `IN_Frame` | `open portability owner` | Linux input pump remains part of the unresolved non-Windows client path. |
| `IN_Activate` | `open portability owner` | Linux active/inactive input state remains portability-owned. |
| `Sys_SendKeyEvents` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |
| `IN_StartupJoystick` | `open portability owner` | Linux joystick startup remains part of the unresolved portability lane. |
| `IN_JoyMove` | `queued function walk` | Legacy Linux host function inside the still-open portability tree. |

## Closure target

- Close the broader Linux client/runtime portability decision first, then rerun this file function-by-function with the chosen target in mind.
- If Linux client/runtime parity is not a target, keep this file explicitly classified as a compatibility-only host carry.
