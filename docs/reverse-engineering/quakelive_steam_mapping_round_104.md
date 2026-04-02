# Quake Live Steam Host Mapping Round 104

## Scope

This round continues directly from
[Round 103](./quakelive_steam_mapping_round_103.md) and closes the adjacent
client init/shutdown block plus the retained server-browser runtime helpers in
`cl_main.c`.

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- writable terminology in
  [cl_main.c](../../src/code/client/cl_main.c)

The existing anchors that made this pass stable were:

- `sub_4B9BF0 -> CL_InitRef`
- `sub_4B95D0 -> CL_InitServerInfo`
- `sub_4B9640 -> CL_ServersResponsePacket`

From those anchors, the next client-runtime seam breaks cleanly into:

1. client init/shutdown owners
2. server-browser state and status owners
3. the retained `showip` host helper

## Client Init And Shutdown Owners

The first stable block after the renderer bootstrap seam is the retained client
lifecycle setup and teardown path.

Observed local facts:

1. `sub_4B9D10` is the exact `CL_SetModel_f` owner: it reads `Cmd_Argv(1)`,
   updates both `model` and `headmodel` when an argument is present, and
   otherwise prints `"model is set to %s\n"`.
2. `sub_4B9E10` is the retained `CL_Shutdown` owner. It prints
   `"----- CL_Shutdown -----\n"`, enforces the recursive guard, disconnects the
   client, tears down sound, renderer, WebPak, UI, and Steam resources,
   removes the retained command set, clears `cl_running`, zeroes `cls`, and
   ends with `"-----------------------\n"`.
3. `sub_4BC690` is the retained `CL_Init` owner. It prints the client init
   banner, initializes the console and input, clears client state, registers
   the retained Quake Live cvar set, installs the client command table,
   initializes Steam/WebPak/renderer state, sets `cl_running`, and ends with
   `"----- Client Initialization Complete -----\n"`. The owner is stable even
   though the retail cvar and command lists diverge from the current writable
   source in several Quake Live-specific spots.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B9D10` (`0x004B9D10`) | `CL_SetModel_f` | Observed + exact source match | Console command owner for querying or updating `model` and `headmodel`. |
| `sub_4B9E10` (`0x004B9E10`) | `CL_Shutdown` | Observed + source-owner match | Tears down the retained client runtime and clears global client state. |
| `sub_4BC690` (`0x004BC690`) | `CL_Init` | Observed + source-owner match | Initializes retained client cvars, commands, subsystems, and startup state. |

## Server-Browser State And Status Owners

The next dense block is the retained server-browser runtime surface: info
parsing, status request tracking, and ping queue updates.

Observed local facts:

1. `sub_4B9F90` parses `clients`, `hostname`, `mapname`, `sv_maxclients`,
   `game`, `gametype`, and `nettype` from an info string and stores the ping on
   the destination server record, which is the retained `CL_SetServerInfo`
   owner. The current writable source also parses `minping`, `maxping`, and
   `punkbuster`; the retail body does not show those extra assignments.
2. `sub_4BA060` iterates the local, mplayer, global, and favorites server
   tables and applies `sub_4B9F90` to any address match. That is the exact
   `CL_SetServerInfoByAddress` owner.
3. `sub_4BA230` parses the incoming info string, rejects mismatched protocol
   packets through `"Different protocol info packet: %s\n"`, updates pending
   ping slots, stamps the net type, calls `sub_4BA060`, and retains the local
   broadcast fallback path with `"MAX_OTHER_SERVERS hit, dropping infoResponse"`.
   That is the retained `CL_ServerInfoPacket` owner.
4. `sub_4BA620` first searches for a matching retained server-status entry,
   then a retrieved slot, then the oldest start time, and finally falls back to
   the ring index, matching `CL_GetServerStatus` exactly.
5. `sub_4BA760` is the retained `CL_ServerStatus` owner: it resets all status
   requests when the address is null, resolves the server address, looks up the
   server-status slot, returns the cached string when available, and resends
   `"getstatus"` after the retained resend interval.
6. `sub_4BA990` is the retained `CL_ServerStatusResponse` owner. It finds the
   matching status slot, appends the settings line, optionally prints
   `"Server settings:\n"` plus the formatted key/value rows, appends the player
   rows, optionally prints `"num: score: ping: name:\n"`, and clears the
   pending flag while stamping the reply time.
7. `sub_4BACB0` is the exact `CL_GetPing` owner: it formats the address into
   the output buffer, computes the live timeout value when no reply has been
   received yet, refreshes retained server info through `sub_4BA060`, and
   writes the ping result back through the out pointer.
8. `sub_4BADB0`, `sub_4BADF0`, and `sub_4BAE10` are exact owners for
   `CL_GetPingInfo`, `CL_ClearPing`, and `CL_GetPingQueueCount`.
9. `sub_4BAE60` is the retained `CL_UpdateVisiblePings_f` owner. It selects the
   current server source, queues new `"getinfo xxx"` requests for visible
   unpinged servers, preserves the global overflow replacement path via
   `sub_4B95D0`, consumes completed ping slots through `sub_4BACB0`, and
   returns the retained status flag.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B9F90` (`0x004B9F90`) | `CL_SetServerInfo` | Observed + source-owner match | Parses retained server-info keys into one `serverInfo_t` record and stores the ping value. |
| `sub_4BA060` (`0x004BA060`) | `CL_SetServerInfoByAddress` | Observed + exact source match | Applies server-info updates to any matching address across the retained server lists. |
| `sub_4BA230` (`0x004BA230`) | `CL_ServerInfoPacket` | Observed + source-owner match | Handles incoming info responses and local-broadcast server discovery. |
| `sub_4BA620` (`0x004BA620`) | `CL_GetServerStatus` | Observed + exact source match | Chooses the retained status slot for one server address. |
| `sub_4BA760` (`0x004BA760`) | `CL_ServerStatus` | Observed + exact source match | Manages retained getstatus requests, cache reuse, and resend timing. |
| `sub_4BA990` (`0x004BA990`) | `CL_ServerStatusResponse` | Observed + exact source match | Stores and optionally prints the retained getstatus reply body. |
| `sub_4BACB0` (`0x004BACB0`) | `CL_GetPing` | Observed + exact source match | Returns the printable address and current ping value for one ping slot. |
| `sub_4BADB0` (`0x004BADB0`) | `CL_GetPingInfo` | Observed + exact source match | Copies the retained ping info string for one ping slot. |
| `sub_4BADF0` (`0x004BADF0`) | `CL_ClearPing` | Observed + exact source match | Clears one retained ping slot by zeroing its port. |
| `sub_4BAE10` (`0x004BAE10`) | `CL_GetPingQueueCount` | Observed + exact source match | Counts active retained ping requests. |
| `sub_4BAE60` (`0x004BAE60`) | `CL_UpdateVisiblePings_f` | Observed + source-owner match | Queues and harvests visible server ping requests for the selected source list. |

## ShowIP Owner

The retained `showip` console entry is still registered through a local jump
stub, but the real target resolves cleanly.

Observed local facts:

1. `sub_4BC690` registers `"showip"` against `data_4BB1A0`.
2. `data_4BB1A0` is a direct jump thunk to `sub_4EE690`.
3. `sub_4EE690` iterates the retained local IP table and prints
   `"IP: %i.%i.%i.%i\n"` for each address, which is the exact `Sys_ShowIP`
   owner.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4EE690` (`0x004EE690`) | `Sys_ShowIP` | Observed + exact source match | Prints the retained local IP address list used by the `showip` command. |

## New High-Confidence Aliases Added This Round

- client lifecycle owners:
  - `sub_4B9D10`
  - `sub_4B9E10`
  - `sub_4BC690`
- server-browser state and status owners:
  - `sub_4B9F90`
  - `sub_4BA060`
  - `sub_4BA230`
  - `sub_4BA620`
  - `sub_4BA760`
  - `sub_4BA990`
  - `sub_4BACB0`
  - `sub_4BADB0`
  - `sub_4BADF0`
  - `sub_4BAE10`
  - `sub_4BAE60`
- showip target:
  - `sub_4EE690`

## Open Questions

1. I did not find a distinct retained owner for `CL_UpdateServerInfo`; the
   current behavior may have been inlined or laid out elsewhere in the Steam
   build.
2. The writable `cl_main.c` command table still diverges from the retail
   `CL_Init`/`CL_Shutdown` bodies around the server-browser and Quake Live-only
   command set, so I left the unresolved wrapper seam itself unforced.
3. `sub_4B9DA0` is still just a tiny callback-sized helper registered near the
   end of `CL_Init`; its concrete owner is not yet stable.
4. `sub_4B9430`, `sub_4B9450`, `sub_4B9940`, `sub_4B81F0`, `sub_4ECDF0`,
   `sub_4F1290`, `sub_4F2900`, and `sub_4F4640` remain the highest-value
   unresolved leftovers across the recent client and host passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1075` raw alias entries, `1074` address-backed
  alias entries

## Completion Stats After Round 104

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1075` raw alias entries, `1074` address-backed
  aliases
- Address-backed coverage: `19.624%` of `5473` functions
- Alias delta this round: `15`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the retained client lifecycle and most
of the adjacent server-browser runtime seam, but it does not change the
writable-source parity estimate by itself.
