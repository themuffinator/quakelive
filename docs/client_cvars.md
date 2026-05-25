# Client CVar Notes

The client registration table now mirrors the Quake Live HLIL defaults:

## Focused CL CVar Parity Tranche

The 2026-05-25 pass rechecked these ten client-owned `cl_*` CVars against
retail `CL_Init` evidence plus their source-visible owners: `cl_allowConsoleChat`,
`cl_demoRecordMessage`, `cl_freezeDemo`, `cl_maxpackets`, `cl_packetdup`,
`cl_timeNudge`, `cl_autoTimeNudge`, `cl_quitOnDemoCompleted`,
`cl_serverStatusResendTime`, and `cl_showTimeDelta`.

- `cl_allowConsoleChat` keeps the retail default `0` and
  archive/protected/cloud flags; the console enter path now uses it as the
  owner for deciding whether bare console text may become `cmd say`.
- The demo/network timing CVars keep the recovered defaults, flags, clamps, and
  local wiring: demo recording overlay modes, demo freeze shortcuts and cgame
  time freeze, `cl_maxpackets`/`cl_packetdup` runtime clamps, bounded
  time-nudge selection, demo-complete quit, server-status resend cadence, and
  time-delta diagnostics.
- A second 2026-05-25 pass rechecked the demo/input cvar tranche:
  `cl_avidemo`, `cl_avidemo_latch`, `cl_avidemo_mintime`,
  `cl_avidemo_maxtime`, `cl_forceavidemo`, `cl_anglespeedkey`,
  `cl_yawspeed`, `cl_pitchspeed`, `cl_run`, and `cl_freelook`.
  The existing source already matched the retail default values, flags, and
  source-visible owners: avidemo latch/start/stop/screenshot/fixed-msec
  handling, keyboard and joystick angle speed scaling, run/walk move-speed
  selection, and freelook center-view/mouse pitch gating.
- A third 2026-05-25 pass rechecked the debug/identity/mouse tranche:
  `cl_shownet`, `cl_showSend`, `cl_anonymous`, `cl_platform`, `cl_maxPing`,
  `cl_mouseAccel`, `cl_mouseAccelDebug`, `cl_mouseAccelOffset`,
  `cl_mouseAccelPower`, and `cl_mouseSensCap`. The current source already
  matched retail defaults, flags, and wiring: network/message debug prints,
  packet-send diagnostics, anonymous-auth userinfo, the Steam platform ROM
  marker, ping timeout filtering, retail mouse acceleration math, debug
  `mouse.log` lifecycle, and sensitivity capping.
- A fourth 2026-05-25 pass rechecked the lifecycle/MOTD/workshop tranche:
  `cl_motd`, `cl_motdString`, `cl_timeout`, `cl_nodelta`, `cl_debugMove`,
  `cl_paused`, `cl_running`, `cl_downloadItem`, `cl_downloadName`, and
  `cl_downloadTime`. The current source already matched the recovered defaults,
  flags, and wiring: MOTD enable/ROM publication, timeout disconnect checks,
  delta suppression and movement diagnostics, paused/running ROM state, command
  routing, and the retained workshop request surface consumed by the native UI
  bridge.
- A fifth 2026-05-25 pass rechecked the native-UI bridge tranche:
  `cl_maxpackets`, `cl_packetdup`, `cl_serverStatusResendTime`, `cl_maxPing`,
  `cl_motdString`, `cl_downloadItem`, `cl_downloadName`, `cl_downloadTime`,
  `cl_downloadCount`, and `cl_downloadSize`. The current source already matched
  the recovered defaults, flags, and bridge behavior: network preset writes,
  packet clamps, server-browser resend/max-ping filtering, MOTD display, native
  workshop progress reads, and the legacy QVM byte-count fallback kept
  non-authoritative.
- A sixth 2026-05-25 pass rechecked the service-disclosure tranche:
  `cl_onlineServicesMode`, `cl_onlineServicesPolicy`,
  `cl_onlineServicesParityScope`, `cl_onlineServicesParityReason`,
  `cl_identityBootstrapMode`, `cl_identityBootstrapPolicy`,
  `cl_voiceServiceMode`, `cl_voiceServicePolicy`, `cl_workshopProvider`, and
  `cl_workshopPolicy`. These are intentional non-retail ROM diagnostics for
  the bounded online-services divergence: their defaults stay disabled or
  unclassified, their refresh owner publishes the active compatibility labels,
  and no matching registration appears in the recovered retail client cvar slab.

- Networking and input
  - `cl_maxpackets` defaults to 125 and is marked cheat-protected, while `cl_timeout` is tightened to 40s and `cl_timeNudge` is clamped server-side to the HLIL [-20, 0] window.
  - `cl_autoTimeNudge` follows the recovered `CL_SetCGameTime` gate: spectators and LAN/local servers force a zero nudge, disabled auto mode uses `cl_timeNudge`, and enabled auto mode derives a negative half-ping nudge while preserving the previous nonzero value before the same [-20, 0] clamp.
  - The engine registers the ROM `cg_spectating` cvar as part of the client timing contract, matching the retail `CL_Init` cvar table before cgame keeps it updated during play.
  - The engine also registers the ROM `cg_ignoreMouseInput` cvar before input dispatch reads it, matching the retail `CL_MouseEvent` gate.
  - Input filtering follows Quake Live defaults (`m_filter 0`) and exposes mouse acceleration helpers (`cl_mouseAccel*`, `cl_mouseSensCap`, `m_cpi`).
  - `cl_mouseAccelDebug` mirrors the retail file-backed diagnostic path: enabling it opens `mouse.log` under `fs_homepath`, writes the `mx my frame_msec rate power` header plus per-frame rows, and disabling it closes the file.
  - Gameplay mouse movement now follows the recovered `CL_MouseMove` math: `m_cpi` converts raw counts through the retail inches-per-centimeter scale, CPI-enabled view axes use the matching `45.4545` multiplier, `cl_mouseAccel` can add or subtract sensitivity depending on sign, and `cl_mouseSensCap` only caps while acceleration is active.
  - `m_filter` now maps to the retail view-angle history filter rather than averaging the previous two raw mouse-delta buckets.
  - `CL_MouseEvent` now follows the recovered raw dispatcher: the advertisement delay gate runs before `cg_ignoreMouseInput`, browser capture uses the recovered `0x20` keycatcher bit, UI/cgame handlers receive the host-queued event payload, and gameplay accumulation stays separate from the CPI/acceleration path. The Win32 host queues relative deltas for captured gameplay and client-area absolute coordinates for browser/UI/cgame/no-grab lanes; the retained browser frame path arms the browser bit while active, and hide/reset clear it.
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
