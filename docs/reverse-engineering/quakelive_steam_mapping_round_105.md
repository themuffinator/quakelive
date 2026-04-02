# Quake Live Steam Host Mapping Round 105

## Scope

This round continues directly from
[Round 104](./quakelive_steam_mapping_round_104.md) and closes the adjacent
demo playback, restart, download/init, and packet-dispatch seam in
`cl_main.c`.

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- writable terminology in
  [cl_main.c](../../src/code/client/cl_main.c)

The existing anchors that made this pass stable were:

- `sub_4B87A0 -> CL_WalkDemoExt`
- `sub_4B8940 -> CL_Disconnect`
- `sub_4B9150 -> CL_CheckForResend`
- `sub_4BC690 -> CL_Init`

From those anchors, the next client-runtime seam breaks cleanly into:

1. demo playback owners
2. flush/restart/download owners
3. connectionless and packet/frame dispatch owners

## Demo Playback Owners

The first retained block after the server-browser helpers is the demo playback
runtime.

Observed local facts:

1. `sub_4BB2A0` prints the timedemo FPS summary when enabled, disconnects the
   client, executes `CL_NextDemo`, and conditionally queues `"quit\n"` when
   the retained quit-on-demo cvar is set. That is the retained
   `CL_DemoCompleted` owner; the extra quit branch is a Quake Live addition on
   top of the GPL owner.
2. `sub_4BB330` is the exact `CL_ReadDemoMessage` owner: it reads the server
   message sequence and payload size from `clc.demofile`, rejects oversized demo
   messages through `"CL_ReadDemoMessage: demoMsglen > MAX_MSGLEN"`, prints
   `"Demo file was truncated.\n"` on short reads, and hands the decoded buffer
   to `CL_ParseServerMessage`.
3. `sub_4BB450` is the retained `CL_PlayDemo_f` owner. It validates the
   command usage with `"playdemo <demoname>\n"`, prints `"Starting Demo.\n"`,
   resolves the demo path, opens the demo, sets the retained demo playback
   state, and repeatedly calls `sub_4BB330` until the client reaches the primed
   state.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BB2A0` (`0x004BB2A0`) | `CL_DemoCompleted` | Observed + source-owner match | Finishes demo playback, prints timedemo stats, disconnects, and advances the next-demo path. |
| `sub_4BB330` (`0x004BB330`) | `CL_ReadDemoMessage` | Observed + exact source match | Reads and parses one retained demo message from `clc.demofile`. |
| `sub_4BB450` (`0x004BB450`) | `CL_PlayDemo_f` | Observed + exact source match | Opens the requested demo and drives initial playback state until primed. |

## Flush, Restart, And Download Owners

The next block resolves the client-memory reset, restart, and download/init
owners.

Observed local facts:

1. `sub_4BB690` disables sound/UI/cgame/renderer state through
   `sub_4B88E0`, clears either the full hunk or just the client mark depending
   on `com_sv_running`, and finally tailcalls `sub_4B9B40`, which is the exact
   `CL_FlushMemory` owner.
2. `sub_4BB6F0` is the exact `CL_MapLoading` owner: it closes the console,
   preserves the localhost fast path when already connected locally, otherwise
   clears `nextmap`, disconnects, forces `"localhost"`, sets the challenge
   state, redraws, seeds the reconnect timer, resolves the localhost address,
   and tailcalls `CL_CheckForResend`.
3. `sub_4BB7E0` is the retained `CL_Vid_Restart_f` owner. The fast restart
   branch updates width/height/fullscreen state, queues
   `"postprocess_restart\n"`, refreshes the display contexts, and returns; the
   slow path tears down UI/cgame/renderer state, restarts pak references,
   rebuilds renderer state, restarts hunk users, and resends pure checksums.
4. `sub_4BB9B0` is the exact `CL_Snd_Restart_f` owner: it restarts sound and
   then tailcalls `sub_4BB7E0`.
5. `sub_4BB9C0` is the exact `CL_DownloadsComplete` owner. It sets the loading
   state, pumps the event loop, exits if the state changed, clears
   `r_uiFullScreen`, flushes client memory, starts cgame, sends pure checksums,
   and emits three packets.
6. `sub_4BBA30` is the retained `CL_InitDownloads` owner. In the Steam build,
   the GPL pak-compare gate has been extended into a Workshop-item requirement
   path that prints `"Server requires the following workshop items..."`, seeds
   the retained download cvars, and falls back to `sub_4BB9C0` once no workshop
   downloads are needed.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BB690` (`0x004BB690`) | `CL_FlushMemory` | Observed + exact source match | Flushes client runtime state and restarts hunk users after a map/demo transition. |
| `sub_4BB6F0` (`0x004BB6F0`) | `CL_MapLoading` | Observed + exact source match | Prepares the client for a local map load and re-enters the localhost connect path. |
| `sub_4BB7E0` (`0x004BB7E0`) | `CL_Vid_Restart_f` | Observed + exact source match | Restarts the retained renderer/UI/cgame stack, with a Win32 fast-restart path first. |
| `sub_4BB9B0` (`0x004BB9B0`) | `CL_Snd_Restart_f` | Observed + exact source match | Restarts sound and then forces the retained video restart owner. |
| `sub_4BB9C0` (`0x004BB9C0`) | `CL_DownloadsComplete` | Observed + exact source match | Finalizes retained download/setup state and enters the loading/cgame init path. |
| `sub_4BBA30` (`0x004BBA30`) | `CL_InitDownloads` | Observed + source-owner match | Initializes retained download requirements; Steam extends this owner with workshop-item handling before the normal download-complete path. |

## Packet And Frame Dispatch Owners

The next stable block resolves the retained packet dispatch surface and the
main frame owner.

Observed local facts:

1. `sub_4BBBE0` starts by printing `"CL packet %s: %s\n"`, handles the
   retained `challengeResponse`, `connectResponse`, `infoResponse`,
   `statusResponse`, `disconnect`, `echo`, `motd`, `print`, and
   `getserversResponse` commands, and ends on
   `"Unknown connectionless packet command.\n"`. That is the exact
   `CL_ConnectionlessPacket` owner.
2. `sub_4BC190` stamps the last-packet time, routes OOB packets to
   `sub_4BBBE0`, rejects runt packets through `"%s: Runt packet\n"`, rejects
   non-matching sequenced packets through
   `"%s:sequenced packet without connection\n"`, processes the netchan,
   updates the server message sequence, parses the server message, and writes a
   demo message when recording. That is the exact `CL_PacketEvent` owner.
3. `sub_4BC3E0` is the retained `CL_Frame` owner. The outer structure matches
   the writable source exactly: early return when the client is not running,
   AVI-demo fixed timestep handling, realtime/frame accumulation, userinfo
   update, timeout check, sendcmd, resend, cgame time update, screen/audio
   update, console run, and framecount increment. Quake Live adds the adjacent
   Steam/workshop completion helper `sub_4BC320` into this owner before the
   retained resend path.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BBBE0` (`0x004BBBE0`) | `CL_ConnectionlessPacket` | Observed + exact source match | Dispatches retained connectionless client packet commands. |
| `sub_4BC190` (`0x004BC190`) | `CL_PacketEvent` | Observed + exact source match | Handles one incoming packet from the main event loop, including OOB routing and sequenced parsing. |
| `sub_4BC3E0` (`0x004BC3E0`) | `CL_Frame` | Observed + source-owner match | Advances one retained client frame; Steam adds a workshop-download completion helper inside the owner. |

## New High-Confidence Aliases Added This Round

- demo playback owners:
  - `sub_4BB2A0`
  - `sub_4BB330`
  - `sub_4BB450`
- flush/restart/download owners:
  - `sub_4BB690`
  - `sub_4BB6F0`
  - `sub_4BB7E0`
  - `sub_4BB9B0`
  - `sub_4BB9C0`
  - `sub_4BBA30`
- packet and frame dispatch owners:
  - `sub_4BBBE0`
  - `sub_4BC190`
  - `sub_4BC3E0`

## Open Questions

1. `sub_4BC320` is now clearly the Steam-specific workshop/download completion
   helper that `CL_Frame` calls before the resend path, but I have not yet
   found a stable writable owner name for it.
2. The retained `showip` command still registers through a jump stub rather
   than a normal local function, so I kept only the true target
   `sub_4EE690 -> Sys_ShowIP` from Round 104.
3. `sub_4B9DA0`, `sub_4B9430`, `sub_4B9450`, `sub_4B9940`, `sub_4B81F0`,
   `sub_4ECDF0`, `sub_4F1290`, `sub_4F2900`, and `sub_4F4640` remain the
   highest-value unresolved leftovers across the recent client and host passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1087` raw alias entries, `1086` address-backed
  alias entries

## Completion Stats After Round 105

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1087` raw alias entries, `1086` address-backed
  aliases
- Address-backed coverage: `19.843%` of `5473` functions
- Alias delta this round: `12`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes most of the retained demo, restart,
download, and packet/frame dispatch seam, but it does not change the
writable-source parity estimate by itself.
