# Quake Live Steam Host Mapping Round 109

## Scope

This round continues directly from
[Round 108](./quakelive_steam_mapping_round_108.md) and closes the next stable
`common.c` tranche in `quakelive_steam.exe`:

- the retained command-completion helper cluster
- the hunk-init and event-loop owners
- the large startup and per-frame common owners

The evidence order for this pass was:

- `src/code/qcommon/common.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- retail disassembly from `assets/quakelive/quakelive_steam.exe`

The existing anchors that made this pass stable were:

- `sub_4B7030 -> CL_InitKeyCommands`
- `sub_4BC190 -> CL_PacketEvent`
- `sub_4BC3E0 -> CL_Frame`
- `sub_4BC690 -> CL_Init`
- `sub_4B9E10 -> CL_Shutdown`
- `sub_4C81D0 -> Cmd_AddCommand`
- `sub_4CB440 -> Com_WriteConfiguration`
- `sub_4CB710 -> Com_ModifyMsec`
- `sub_4D3520 -> FS_InitFilesystem`
- `sub_4D35E0 -> FS_Restart`
- `sub_4ED400 -> Sys_Init`
- `sub_4F05B0 -> Sys_ShowConsole`
- `sub_4F2590 -> QLWebCore_Update`
- `sub_4F4130 -> Zmq_UpdatePasswords`
- `sub_4F4FD0 -> Zmq_PumpRcon`

## Command Completion Helpers

The first stable block is the retained tab-completion helper cluster in
`common.c`.

Observed local facts:

1. `sub_4C9700` compares candidates against the retained completion prefix in
   `data_1205de0`, increments `data_11ff9cc`, copies the first match into
   `data_11ff9d0`, and then shortens that buffer by case-insensitive common
   prefix when later matches arrive. That is the exact static `FindMatches`
   owner.
2. `sub_4CB900` prints only those candidates that still share the retained
   `shortestMatch` prefix held in `data_11ff9d0`, using the exact
   `"    %s\n"` output from the writable `PrintMatches` helper.
3. `sub_4CB950` tokenizes the field buffer, strips a leading slash or
   backslash from the command token, runs both command and cvar completion with
   `sub_4C9700` and `sub_4CB900`, emits `"]%s\n"` on multi-match results, and
   appends any remaining arguments into the caller field buffer. That is the
   retained `Field_CompleteCommand` owner. The small writable helpers
   `keyConcatArgs` and `ConcatRemaining` are folded into this retail body
   rather than surviving as standalone emitted functions.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4C9700` (`0x004C9700`) | `FindMatches` | Observed + exact source match | Static completion callback that tracks the common prefix across command and cvar matches. |
| `sub_4CB900` (`0x004CB900`) | `PrintMatches` | Observed + exact source match | Static completion callback that prints only retained prefix-sharing matches. |
| `sub_4CB950` (`0x004CB950`) | `Field_CompleteCommand` | Observed + exact source match | Performs command/cvar tab completion and updates the target edit field. |

## Hunk Init And Event Loop Owners

The second stable block is the adjacent hunk-init and event-loop seam.

Observed local facts:

1. `sub_4CBBA0` validates `FS_LoadStack() == 0`, reads `com_hunkMegs`,
   preserves the dedicated versus client minimum-allocation split, allocates
   and cacheline-aligns the hunk buffer, calls `Hunk_Clear`, and registers the
   retained `"meminfo"` command. That is the exact `Com_InitHunkMemory`
   owner.
2. `sub_4CBC90` initializes a stack `msg_t`, repeatedly pulls events from the
   retained `Com_GetEvent` path, dispatches the exact `SE_KEY`, `SE_CHAR`,
   `SE_MOUSE`, `SE_JOYSTICK_AXIS`, `SE_CONSOLE`, and `SE_PACKET` handlers, and
   preserves the stock `Com_EventLoop: bad event type %i` and
   `Com_EventLoop: oversize packet\n` diagnostics. That is the exact
   `Com_EventLoop` owner.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4CBBA0` (`0x004CBBA0`) | `Com_InitHunkMemory` | Observed + exact source match | Initializes the retained hunk allocator and registers `meminfo`. |
| `sub_4CBC90` (`0x004CBC90`) | `Com_EventLoop` | Observed + exact source match | Dispatches retained sys events, loopback packets, and packet processing. |

## Startup And Frame Owners

The last stable block is the large retained startup and frame pair in
`common.c`.

Observed local facts:

1. `sub_4CBFD0` prints the version banner, establishes the retained abort
   frame `setjmp`, initializes push events, zone memory, command parsing, key
   commands, the filesystem, journaling/bootstrap config execution, the hunk,
   cvars, commands, networking, VM/server/client startup, startup commands, UI
   fullscreen setup, and the final `--- Common Initialization Complete ---`
   banner. That is the retained `Com_Init` owner.
2. `sub_4CC6C0` begins with the same abort-frame `setjmp`, writes modified
   configuration, handles `viewlog`, computes the frame sleep budget, pumps
   the event loop, applies `Com_ModifyMsec`, runs server and client frames,
   emits `com_speeds` and `com_showtrace` diagnostics, and increments the
   retained frame counter. That is the retained `Com_Frame` owner.
3. Both bodies carry Quake Live retail expansions on top of the Quake III
   owner: `sub_4CBFD0` preserves the `qzconfig.cfg` / `repconfig.cfg`
   bootstrap, `writeClientConfig`, Steam/bootstrap checks, and extra startup
   cvars; `sub_4CC6C0` adds browser/ZMQ upkeep plus dedicated idle-sleep and
   performance logging. Those deltas change the body, not the owner identity.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4CBFD0` (`0x004CBFD0`) | `Com_Init` | Observed + retained owner match | Performs retained common startup, bootstrap config execution, cvar/command init, and VM/client/server bring-up. |
| `sub_4CC6C0` (`0x004CC6C0`) | `Com_Frame` | Observed + retained owner match | Runs the retained main frame loop, config flush, timing clamp, server/client frames, and diagnostics. |

## New High-Confidence Aliases Added This Round

- `sub_4C9700 -> FindMatches`
- `sub_4CB900 -> PrintMatches`
- `sub_4CB950 -> Field_CompleteCommand`
- `sub_4CBBA0 -> Com_InitHunkMemory`
- `sub_4CBC90 -> Com_EventLoop`
- `sub_4CBFD0 -> Com_Init`
- `sub_4CC6C0 -> Com_Frame`

## Open Questions

1. `sub_4CB630` remains intentionally unnamed. The retail command string
   `"writeClientConfig"` is clear, but the repo still does not have a
   writable owner name for that Quake Live-only helper.
2. `sub_4B9430`, `sub_4B9940`, `sub_4B81F0`, `sub_4ECDF0`, `sub_4F1290`,
   `sub_4F2900`, and `sub_4F4640` remain the highest-value unresolved client
   and host leftovers outside this seam.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1138` raw alias entries, `1137` address-backed
  alias entries

## Completion Stats After Round 109

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1138` raw alias entries, `1137` address-backed
  aliases
- Address-backed coverage: `20.775%` of `5473` functions
- Alias delta this round: `7`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the retained `common.c` completion,
hunk/event-loop, and startup/frame owners, but it does not change the
writable-source parity estimate by itself.
