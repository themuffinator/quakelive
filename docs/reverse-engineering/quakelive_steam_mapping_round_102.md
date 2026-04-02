# Quake Live Steam Host Mapping Round 102

## Scope

This round continues directly from
[Round 101](./quakelive_steam_mapping_round_101.md) and closes the adjacent
early `cl_main.c` owner block immediately after the retained input/key seam.

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- writable terminology in
  [cl_main.c](../../src/code/client/cl_main.c)

The existing anchors that made this pass stable were:

- `sub_4B8200 -> CL_AddReliableCommand`
- `sub_4B7B00 -> CL_KeyEvent`
- `sub_4B80E0 -> Key_ClearStates`

From those anchors, the next client-runtime seam breaks cleanly into:

1. reliable command and demo recording helpers
2. demo-loop, disconnect, and forwarding owners
3. pure-checksum helpers and PK3/config inspection commands

## Reliable Command And Demo Helpers

The first block after `CL_AddReliableCommand` is a direct run through the
reliable-command mutator and the retained demo recording helpers.

Observed local facts:

1. `sub_4B8250` indexes the current reliable command slot, caps the string
   length, and appends `'\n'` plus `'\0'`, which is the exact
   `CL_ChangeReliableCommand` contract.
2. `sub_4B82A0` writes the server message sequence, then the post-header
   message length, then the payload bytes into `clc.demofile`, matching
   `CL_WriteDemoMessage`. The retail body does not currently show the writable
   diagnostic print gated by `cl_demoRecordMessage >= 2`.
3. `sub_4B8300` closes the active demo file, writes the `-1/-1` terminator,
   clears the demo-recording flags, and prints `"Stopped demo.\n"`. That is the
   `CL_StopRecord_f` owner, with a small retail body delta around the writable
   `cl_demoRecordMessage` gate.
4. `sub_4B8390` is the literal `demo%i%i%i%i` formatter with the `demo9999.tga`
   fallback, which is an exact `CL_DemoFilename` match.
5. `sub_4B8430` is the retained `CL_Record_f` owner: it validates state,
   chooses a free demo filename, opens the demo, serializes configstrings,
   baselines, client num, and checksum feed, then writes the first demo packet.
   The retail body is still source-identical at the owner level, but it does
   not currently show the writable synchronous-clients warning path.
6. `sub_4B87A0` is the static `CL_WalkDemoExt` helper that iterates the demo
   protocol list, tries `demos/%s.dm_%d`, and prints either `"Demo file: %s\n"`
   or `"Not found: %s\n"`.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B8250` (`0x004B8250`) | `CL_ChangeReliableCommand` | Observed + exact source match | Appends a trailing newline to the current reliable command slot. |
| `sub_4B82A0` (`0x004B82A0`) | `CL_WriteDemoMessage` | Observed + source-owner match | Writes the current server message sequence and payload bytes into the active demo file. |
| `sub_4B8300` (`0x004B8300`) | `CL_StopRecord_f` | Observed + source-owner match | Stops active demo recording, writes the trailer markers, closes the file, and clears the retained recording flags. |
| `sub_4B8390` (`0x004B8390`) | `CL_DemoFilename` | Observed + exact source match | Formats numbered demo names as `demo####`. |
| `sub_4B8430` (`0x004B8430`) | `CL_Record_f` | Observed + source-owner match | Starts demo recording and serializes the retained initial gamestate packet. |
| `sub_4B87A0` (`0x004B87A0`) | `CL_WalkDemoExt` | Observed + exact source match | Tries the supported demo protocol extensions until a readable demo file is found. |

## Demo Loop, Disconnect, And Forwarding Owners

The next block resolves the retained client lifecycle and command-forwarding
owners.

Observed local facts:

1. `sub_4B8810` queues `"d1\n"` and clears the catcher flags, which is the
   exact `CL_StartDemoLoop` owner.
2. `sub_4B8830` loads `nextdemo`, logs `CL_NextDemo: %s`, clears the cvar, and
   executes the queued command, matching `CL_NextDemo`.
3. `sub_4B88E0` disables sound, shuts down cgame and UI, conditionally calls
   the renderer shutdown callback with `0`, and clears the retained
   started/registered flags, matching `CL_ShutdownAll`.
4. `sub_4B8920` is the exact `Com_Memset( &cl, 0, sizeof( cl ) )` owner for
   `CL_ClearState`.
5. `sub_4B8940` matches the retained `CL_Disconnect` owner: fullscreen UI
   enable, demo/download cleanup, Steam auth-ticket cancellation, optional UI
   menu handoff, reliable `"disconnect"` queuing, triple packet flush, state
   clear, `clc` wipe, and `sv_cheats` reset.
6. `sub_4B8A70` is the retained `CL_ForwardCommandToServer` owner, including
   the leading `'-'` ignore path and the `"Unknown command \"%s\"\n"` failure
   branch for demos, disconnected state, or button commands.
7. `sub_4B8AD0`, `sub_4B8B30`, `sub_4B8C70`, and `sub_4B8CB0` are exact
   owners for `CL_ForwardToServer_f`, `CL_Setenv_f`, `CL_Disconnect_f`, and
   `CL_Reconnect_f`.
8. `sub_4B8D30` is the retained `CL_Connect_f` owner. The main connection flow
   matches the writable source exactly; retail Quake Live adds browser-facing
   side effects after the address has been stored and the new state selected.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B8810` (`0x004B8810`) | `CL_StartDemoLoop` | Observed + exact source match | Restarts the demo loop by queueing `d1` and clearing catchers. |
| `sub_4B8830` (`0x004B8830`) | `CL_NextDemo` | Observed + exact source match | Executes the `nextdemo` cvar command after demo completion. |
| `sub_4B88E0` (`0x004B88E0`) | `CL_ShutdownAll` | Observed + exact source match | Shuts down sound, cgame, UI, and the renderer, then clears retained startup flags. |
| `sub_4B8920` (`0x004B8920`) | `CL_ClearState` | Observed + exact source match | Clears the retained `cl` state block before a new gamestate is parsed. |
| `sub_4B8940` (`0x004B8940`) | `CL_Disconnect` | Observed + exact source match | Disconnects the client, flushes queued disconnect packets, clears connection state, and resets local cheat allowance. |
| `sub_4B8A70` (`0x004B8A70`) | `CL_ForwardCommandToServer` | Observed + source-owner match | Forwards the current console command to the server-side reliable-command channel when allowed. |
| `sub_4B8AD0` (`0x004B8AD0`) | `CL_ForwardToServer_f` | Observed + exact source match | Console command wrapper that forwards `Cmd_Args()` to the server when active. |
| `sub_4B8B30` (`0x004B8B30`) | `CL_Setenv_f` | Observed + exact source match | Console command owner for querying or setting environment variables. |
| `sub_4B8C70` (`0x004B8C70`) | `CL_Disconnect_f` | Observed + exact source match | Console command owner that stops cinematics, clears single-player UI state, and raises `ERR_DISCONNECT` when needed. |
| `sub_4B8CB0` (`0x004B8CB0`) | `CL_Reconnect_f` | Observed + exact source match | Console command owner that queues a reconnect unless the current server is `localhost`. |
| `sub_4B8D30` (`0x004B8D30`) | `CL_Connect_f` | Observed + source-owner match | Console command owner that resolves the target server, disconnects current state, and enters the retained connect/challenge flow. |

## Pure Checksums And Inspection Commands

The next retained block resolves the pure-checksum queue helpers and the small
client inspection commands.

Observed local facts:

1. `sub_4B8F20` pulls `FS_ReferencedPakPureChecksums`, validates the
   `cgamex86.dll` pak checksum, builds the encoded `"Yf "` pure-checksum
   command, mutates the first two bytes by `+10`, and queues the result through
   `CL_AddReliableCommand`, matching `CL_SendPureChecksums`.
2. `sub_4B9000` enqueues the literal `vdr` reliable command, which is the
   exact `CL_ResetPureClientAtServer` owner.
3. `sub_4B9070` and `sub_4B9090` are exact string/report wrappers around
   `FS_LoadedPakNames` and `FS_ReferencedPakNames`, matching
   `CL_OpenedPK3List_f` and `CL_ReferencedPK3List_f`.
4. `sub_4B90B0` prints the retained configstring table only when the client is
   active, which is the exact `CL_Configstrings_f` owner.
5. `sub_4B9100` prints the retained client state header, server name, and user
   info settings, which is the exact `CL_Clientinfo_f` owner.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B8F20` (`0x004B8F20`) | `CL_SendPureChecksums` | Observed + exact source match | Builds and queues the encoded pure-checksum reliable command. |
| `sub_4B9000` (`0x004B9000`) | `CL_ResetPureClientAtServer` | Observed + exact source match | Queues the retained `vdr` reset command. |
| `sub_4B9070` (`0x004B9070`) | `CL_OpenedPK3List_f` | Observed + exact source match | Prints the loaded PK3 list. |
| `sub_4B9090` (`0x004B9090`) | `CL_ReferencedPK3List_f` | Observed + exact source match | Prints the referenced PK3 list. |
| `sub_4B90B0` (`0x004B90B0`) | `CL_Configstrings_f` | Observed + exact source match | Dumps active configstrings to the console. |
| `sub_4B9100` (`0x004B9100`) | `CL_Clientinfo_f` | Observed + exact source match | Prints the retained client state, server name, and userinfo. |

## New High-Confidence Aliases Added This Round

- reliable command and demo helpers:
  - `sub_4B8250`
  - `sub_4B82A0`
  - `sub_4B8300`
  - `sub_4B8390`
  - `sub_4B8430`
  - `sub_4B87A0`
- demo loop and disconnect/forwarding:
  - `sub_4B8810`
  - `sub_4B8830`
  - `sub_4B88E0`
  - `sub_4B8920`
  - `sub_4B8940`
  - `sub_4B8A70`
  - `sub_4B8AD0`
  - `sub_4B8B30`
  - `sub_4B8C70`
  - `sub_4B8CB0`
  - `sub_4B8D30`
- pure checksum and inspection commands:
  - `sub_4B8F20`
  - `sub_4B9000`
  - `sub_4B9070`
  - `sub_4B9090`
  - `sub_4B90B0`
  - `sub_4B9100`

## Open Questions

1. `sub_4B81F0` is still just a tiny retained state toggle next to the
   reliable-command seam. The write target is clear, but I do not yet have a
   stable source owner name for it.
2. `sub_4B9150` is the next large networking seam and clearly overlaps the
   resend/challenge path, but I have not yet bounded the full owner split
   tightly enough to promote names from it in this round.
3. `sub_4ECDF0`, `sub_4F1290`, `sub_4F2900`, and `sub_4F4640` remain the
   highest-value unresolved leftovers across the recent host/client/browser
   passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1049` raw alias entries, `1048` address-backed
  alias entries

## Completion Stats After Round 102

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1049` raw alias entries, `1048` address-backed
  aliases
- Address-backed coverage: `19.149%` of `5473` functions
- Alias delta this round: `23`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes most of the early retained client
command/runtime surface, but it does not change the writable-source parity
estimate by itself.
