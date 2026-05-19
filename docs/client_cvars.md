# Client CVar Notes

The client registration table now mirrors the Quake Live HLIL defaults:

- Networking and input
  - `cl_maxpackets` defaults to 125 and is marked cheat-protected, while `cl_timeout` is tightened to 40s and `cl_timeNudge` is clamped server-side to the HLIL [-20, 0] window.
  - `cl_autoTimeNudge` follows the recovered `CL_SetCGameTime` gate: spectators and LAN/local servers force a zero nudge, disabled auto mode uses `cl_timeNudge`, and enabled auto mode derives a negative half-ping nudge while preserving the previous nonzero value before the same [-20, 0] clamp.
  - The engine registers the ROM `cg_spectating` cvar as part of the client timing contract, matching the retail `CL_Init` cvar table before cgame keeps it updated during play.
  - The engine also registers the ROM `cg_ignoreMouseInput` cvar before input dispatch reads it, matching the retail `CL_MouseEvent` gate.
  - Input filtering follows Quake Live defaults (`m_filter 0`) and exposes mouse acceleration helpers (`cl_mouseAccel*`, `cl_mouseSensCap`, `m_cpi`).
  - `cl_mouseAccelDebug` mirrors the retail file-backed diagnostic path: enabling it opens `mouse.log` under `fs_homepath`, writes the `mx my frame_msec rate power` header plus per-frame rows, and disabling it closes the file.
  - Gameplay mouse movement now follows the recovered `CL_MouseMove` math: `m_cpi` converts raw counts through the retail inches-per-centimeter scale, CPI-enabled view axes use the matching `45.4545` multiplier, `cl_mouseAccel` can add or subtract sensitivity depending on sign, and `cl_mouseSensCap` only caps while acceleration is active.
  - `m_filter` now maps to the retail view-angle history filter rather than averaging the previous two raw mouse-delta buckets.
  - `CL_MouseEvent` now follows the recovered raw dispatcher: `cg_ignoreMouseInput` blocks event routing, browser capture uses the recovered `0x20` keycatcher bit, UI/cgame handlers receive the raw event payload, and gameplay accumulation stays separate from the CPI/acceleration path. The retained browser frame path arms that bit while the browser is active, and hide/reset clear it.
  - The source-only `cl_mouseAccelStyle` cvar has been removed from the client table; no matching string or registration appears in the committed retail HLIL/Ghidra corpus.
- Demo and sound-adjacent
  - Avidemo helpers (`cl_avidemo_latch`, `cl_avidemo_mintime`, `cl_avidemo_maxtime`) and `cl_demoRecordMessage` mirror the HLIL flags so demo capture matches Quake Live behavior.
  - `CL_KeyEvent` now owns the retail demo-playback shortcuts for `cl_freezeDemo`, `timescale`, and `cg_drawDemoHUD` while `clc.demoplaying` is active and no input catcher owns the event apart from the recovered `0x10` pass-through bit.
- HUD and match prompts
  - `cg_complaintWarning` defaults to `1` with archive persistence and gates the team-kill complaint overlay restored in `CG_DrawVote`.
- User info
  - Customization CVars now use Quake Live defaults (`color1 7`, `color2 25`, `sensitivity 4`, `rate 25000`) with protected/cloud flags to match the HLIL table.

## Platform-specific CVars

These CVars are only meaningful on Steam-enabled builds and should be stubbed or conditionally compiled on other platforms:

- `cl_platform` is a ROM marker describing the active platform (HLIL defaults it to `1` for Steam).
- Workshop/bootstrap request bookkeeping (`cl_downloadItem`, `cl_downloadName`, `cl_downloadTime`) matches the recovered `CL_InitDownloads` and `uix86` surface: the retained client bootstrap seeds those CVars, and the UI progress import reads `cl_downloadItem`, calls the native `GetItemDownloadInfo` probe with the parsed item-ID low/high words, and consults `cl_downloadTime`.
- `cl_downloadCount` and `cl_downloadSize` still exist because Quake Live UI strings reference them, but the recovered workshop queue/progress owner no longer treats them as authoritative progress state.
- Non-Steam targets should keep the whole download-cvar cluster as inert temp CVars.
- `cl_allowConsoleChat` and the cloud/protected flags (`CVAR_PROTECTED`, `CVAR_VM_CREATED`, `CVAR_CLOUD`) are Quake Live-specific; other targets can treat them as no-op guards.
