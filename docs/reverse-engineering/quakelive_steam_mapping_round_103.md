# Quake Live Steam Host Mapping Round 103

## Scope

This round continues directly from
[Round 102](./quakelive_steam_mapping_round_102.md) and closes the adjacent
`cl_main.c` resend, master-server response, and renderer-bootstrap seam.

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- writable terminology in
  [cl_main.c](../../src/code/client/cl_main.c)

The existing anchors that made this pass stable were:

- `sub_4B8940 -> CL_Disconnect`
- `sub_4B8D30 -> CL_Connect_f`
- `sub_4B9100 -> CL_Clientinfo_f`

From those anchors, the next client-runtime seam breaks cleanly into:

1. resend, MOTD, and master-server list owners
2. timeout handling
3. renderer bootstrap and renderer glue helpers

## Resend, MOTD, And Master-Server Owners

The first block after the early `cl_main.c` command seam is the retained
connect/challenge resend path plus the adjacent MOTD and server-list helpers.

Observed local facts:

1. `sub_4B9150` returns early when demo playback is active, only runs in the
   two connect states, enforces the retransmit timeout, increments the connect
   packet count, sends either `"getchallenge "` or the quoted `"connect "`
   payload, and ends in the literal fatal string
   `"CL_CheckForResend: bad cls.state"`. That is the exact
   `CL_CheckForResend` owner.
2. `sub_4B94F0` compares the packet source against the retained update-server
   address, parses `Cmd_Argv(1)`, validates the `"challenge"` key against the
   retained challenge buffer, extracts `"motd"`, copies the full info string,
   and sets `cl_motdString`. That is the retained `CL_MotdPacket` owner.
3. `sub_4B95D0` is the struct initializer that writes `NA_IP`, copies four IP
   bytes and the port, zeros the string and counter fields, and sets `ping` to
   `-1`, matching `CL_InitServerInfo` exactly.
4. `sub_4B9640` prints `"CL_ServersResponsePacket\n"`, initializes the
   retained global and mplayer counts, parses backslash-delimited IP/port
   pairs, logs `server: %d ip: %d.%d.%d.%d:%d\n`, fills either the global or
   alternate server tables through `sub_4B95D0`, spills overflow addresses into
   the retained extra-address list, and finally prints
   `"%d servers parsed (total %d)\n"`. This is the exact
   `CL_ServersResponsePacket` owner.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B9150` (`0x004B9150`) | `CL_CheckForResend` | Observed + exact source match | Retransmits the getchallenge/connect request during the retained connect and challenge states. |
| `sub_4B94F0` (`0x004B94F0`) | `CL_MotdPacket` | Observed + exact source match | Validates the retained MOTD challenge and publishes the returned MOTD string. |
| `sub_4B95D0` (`0x004B95D0`) | `CL_InitServerInfo` | Observed + exact source match | Initializes one retained server-info record from the parsed server address bytes. |
| `sub_4B9640` (`0x004B9640`) | `CL_ServersResponsePacket` | Observed + exact source match | Parses the retained getservers response and populates the server browser lists. |

## Timeout And Renderer Bootstrap Owners

The next block closes the retained timeout handler and the renderer bootstrap
glue that follows immediately after it.

Observed local facts:

1. `sub_4B9960` checks `cl_paused` and `sv_paused`, requires an active
   connected state other than cinematics, compares the retained timeout cvar
   against `cls.realtime - clc.lastPacketTime`, increments the timeout counter,
   and terminates through the literal `"Server connection timed out"` string
   once the threshold exceeds five. That is the exact `CL_CheckTimeout`
   owner.
2. `sub_4B99F0` formats the variadic message into a stack buffer, then routes
   it through the retained `PRINT_ALL`, `PRINT_DEVELOPER`, and
   `PRINT_WARNING` branches using `%s`, `^1%s`, and `^3%s`. That is the exact
   `CL_RefPrintf` renderer-print bridge.
3. `sub_4B9AA0` begins renderer registration, registers the retained
   `gfx/2d/bigchars`, `white`, `console`, `icons/record`, `browserShader`, and
   related startup shaders, then recomputes the console field width from the
   video width. This is the Quake Live-retained `CL_InitRenderer` owner; the
   shader set is broader than the GPL baseline, but the ownership is stable.
4. `sub_4B9B40` is the retained startup gate that checks `com_cl_running`,
   lazily starts the renderer, sound, sound registration, and UI, and does so
   in the same order as `CL_StartHunkUsers`.
5. `sub_4B9BB0` is the one-line `Z_TagMalloc( size, TAG_RENDERER )` wrapper,
   which is the exact `CL_RefMalloc` owner.
6. `sub_4B9BD0` returns `Sys_Milliseconds() * com_timescale->value`, matching
   `CL_ScaledMilliseconds` exactly.
7. `sub_4B9BF0` prints `"----- Initializing Renderer ----\n"`, fills the
   retained `refimport_t` table with the renderer callback set, calls
   `GetRefAPI`, prints the closing dashed separator, fatals on
   `"Couldn't initialize refresh"`, copies the returned export table, and
   clears `cl_paused`. That is the exact `CL_InitRef` owner.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B9960` (`0x004B9960`) | `CL_CheckTimeout` | Observed + exact source match | Drops the retained client connection after repeated packet timeout checks. |
| `sub_4B99F0` (`0x004B99F0`) | `CL_RefPrintf` | Observed + exact source match | Renderer DLL print bridge that maps `PRINT_*` levels onto the console printers. |
| `sub_4B9AA0` (`0x004B9AA0`) | `CL_InitRenderer` | Observed + source-owner match | Starts renderer registration and loads the retained startup shader set. |
| `sub_4B9B40` (`0x004B9B40`) | `CL_StartHunkUsers` | Observed + exact source match | Lazily restarts renderer, sound, sound registration, and UI after hunk clears. |
| `sub_4B9BB0` (`0x004B9BB0`) | `CL_RefMalloc` | Observed + exact source match | Renderer allocation bridge to `Z_TagMalloc(..., TAG_RENDERER)`. |
| `sub_4B9BD0` (`0x004B9BD0`) | `CL_ScaledMilliseconds` | Observed + exact source match | Returns scaled milliseconds using the retained `com_timescale` multiplier. |
| `sub_4B9BF0` (`0x004B9BF0`) | `CL_InitRef` | Observed + exact source match | Builds the renderer import table, resolves the renderer export table, and clears `cl_paused`. |

## New High-Confidence Aliases Added This Round

- resend, MOTD, and master-server owners:
  - `sub_4B9150`
  - `sub_4B94F0`
  - `sub_4B95D0`
  - `sub_4B9640`
- timeout and renderer bootstrap owners:
  - `sub_4B9960`
  - `sub_4B99F0`
  - `sub_4B9AA0`
  - `sub_4B9B40`
  - `sub_4B9BB0`
  - `sub_4B9BD0`
  - `sub_4B9BF0`

## Open Questions

1. `sub_4B9430` is still only a retained table accessor returning an interior
   pointer into the adjacent `cl_main.c` client data seam. I do not yet have a
   stable source owner name for it.
2. `sub_4B9450` still overlaps the dropped-connection/disconnect path, but the
   current evidence does not cleanly explain the Quake Live control-flow delta
   versus the GPL `CL_DisconnectPacket` owner, so I left it unmapped.
3. `sub_4B9940` remains a tiny pause-state helper used by the timeout seam; the
   behavior is clear, but the exact writable owner name is not.
4. `sub_4B81F0`, `sub_4ECDF0`, `sub_4F1290`, `sub_4F2900`, and `sub_4F4640`
   remain the highest-value unresolved leftovers across the recent client and
   host passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1060` raw alias entries, `1059` address-backed
  alias entries

## Completion Stats After Round 103

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1060` raw alias entries, `1059` address-backed
  aliases
- Address-backed coverage: `19.35%` of `5473` functions
- Alias delta this round: `11`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes most of the retained resend and
renderer-bootstrap seam, but it does not change the writable-source parity
estimate by itself.
