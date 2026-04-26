# Client CVar Notes

The client registration table now mirrors the Quake Live HLIL defaults:

- Networking and input
  - `cl_maxpackets` defaults to 125 and is marked cheat-protected, while `cl_timeout` is tightened to 40s and `cl_timeNudge` is clamped server-side to the HLIL [-20, 0] window.
  - Input filtering follows Quake Live defaults (`m_filter 0`) and exposes mouse acceleration helpers (`cl_mouseAccel*`, `cl_mouseSensCap`, `m_cpi`).
- Demo and sound-adjacent
  - Avidemo helpers (`cl_avidemo_latch`, `cl_avidemo_mintime`, `cl_avidemo_maxtime`) and `cl_demoRecordMessage` mirror the HLIL flags so demo capture matches Quake Live behavior.
- User info
  - Customization CVars now use Quake Live defaults (`color1 7`, `color2 25`, `sensitivity 4`, `rate 25000`) with protected/cloud flags to match the HLIL table.

## Platform-specific CVars

These CVars are only meaningful on Steam-enabled builds and should be stubbed or conditionally compiled on other platforms:

- `cl_platform` is a ROM marker describing the active platform (HLIL defaults it to `1` for Steam).
- Workshop/bootstrap request bookkeeping (`cl_downloadItem`, `cl_downloadName`, `cl_downloadTime`) matches the recovered `CL_InitDownloads` and `uix86` surface: the retained client bootstrap seeds those CVars, and the UI progress import reads `cl_downloadItem`, calls the native `GetItemDownloadInfo` probe with the parsed item-ID low/high words, and consults `cl_downloadTime`.
- `cl_downloadCount` and `cl_downloadSize` still exist because Quake Live UI strings reference them, but the recovered workshop queue/progress owner no longer treats them as authoritative progress state.
- Non-Steam targets should keep the whole download-cvar cluster as inert temp CVars.
- `cl_allowConsoleChat` and the cloud/protected flags (`CVAR_PROTECTED`, `CVAR_VM_CREATED`, `CVAR_CLOUD`) are Quake Live-specific; other targets can treat them as no-op guards.
