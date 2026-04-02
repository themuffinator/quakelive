# Quake Live Steam Host Mapping Round 99

## Scope

This round continues the Win32 host pass from
[Round 98](./quakelive_steam_mapping_round_98.md), but moves one layer lower
into the exact `win_main.c` platform wrappers:

1. the small filesystem/default-path wrappers near the top of the file
2. the recursive directory scanning and file-list sorting/free helpers
3. the DLL unload/load pair
4. the retained Win32 event-queue pair

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/`
- writable terminology in
  [win_main.c](../../src/code/win32/win_main.c) and
  [qcommon.h](../../src/code/qcommon/qcommon.h)

Unlike the retail-only browser and ZMQ leftovers, every alias promoted here has
an exact GPL owner and a behavior match tight enough to treat as a direct
source reconstruction.

## Filesystem and Path Wrappers

The first group is straightforward:

- `sub_4EC810` tailcalls `_mkdir`, matching `Sys_Mkdir`
- `sub_4EC820` was already promoted in Round 98 as `Sys_Cwd`
- `sub_4EC840` is the pure retained empty-string return used for the default
  CD path, matching `Sys_DefaultCDPath`

The next block then matches the directory scan helpers exactly:

- `sub_4EC850` recursively walks `basedir\\subdirs\\*`, filters through
  `Com_FilterPath`, and appends matches into a retained list/count pair, which
  is the GPL `Sys_ListFilteredFiles`
- `sub_4ECA60` is the local lexical comparison helper used by the bubble sort
  in `Sys_ListFiles`, matching the static `strgtr`
- `sub_4ECAC0` implements both the filtered recursive list path and the normal
  `_findfirst` / `_findnext` list path, then sorts the copy through `strgtr`,
  which is the GPL `Sys_ListFiles`
- `sub_4ECD40` frees each copied string and then the outer list owner, matching
  `Sys_FreeFileList`

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4EC810` (`0x004EC810`) | `Sys_Mkdir` | Observed + exact source match | Thin Win32 path wrapper that tailcalls `_mkdir`. |
| `sub_4EC840` (`0x004EC840`) | `Sys_DefaultCDPath` | Observed + exact source match | Returns the retained empty default CD path string. |
| `sub_4EC850` (`0x004EC850`) | `Sys_ListFilteredFiles` | Observed + exact source match | Recursively walks subdirectories, filters names through `Com_FilterPath`, and appends retained path copies into the caller-owned list/count pair. |
| `sub_4ECA60` (`0x004ECA60`) | `strgtr` | Observed + exact source match | Local lexical helper used by the file-list sort pass. |
| `sub_4ECAC0` (`0x004ECAC0`) | `Sys_ListFiles` | Observed + exact source match | Builds filtered or extension-based file lists with `_findfirst64i32`, copies them into a retained result array, and sorts the result through `strgtr`. |
| `sub_4ECD40` (`0x004ECD40`) | `Sys_FreeFileList` | Observed + exact source match | Frees each copied file-list entry and then releases the outer list owner. |

## DLL and Event Queue Owners

The next exact source-match cluster sits immediately below those filesystem
helpers:

- `sub_4ECE80` frees a loaded module and raises the same fatal
  `"Sys_UnloadDll FreeLibrary failed"` path as the GPL source, matching
  `Sys_UnloadDll`
- `sub_4ECEB0` builds the `"%sx86.dll"` name, searches `fs_basepath`,
  `fs_homepath`, and `fs_cdpath`, loads the DLL, resolves `dllEntry`, and
  calls it, matching `Sys_LoadDll`
- `sub_4ED050` enqueues retained `sysEvent_t` records into the ring buffer,
  handles overflow by freeing the discarded event payload, and stamps the
  current time when the caller passes `0`, matching `Sys_QueEvent`
- `sub_4ED0E0` returns queued events first, pumps the Windows message loop,
  translates pending console text into `SE_CONSOLE`, translates packets into
  `SE_PACKET`, and otherwise emits an empty timed event, matching `Sys_GetEvent`

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4ECE80` (`0x004ECE80`) | `Sys_UnloadDll` | Observed + exact source match | Releases a loaded module through `FreeLibrary` and routes failure into the fatal `Sys_UnloadDll` error path. |
| `sub_4ECEB0` (`0x004ECEB0`) | `Sys_LoadDll` | Observed + exact source match | Searches the standard Win32 DLL roots, loads the target `x86.dll`, resolves `dllEntry`, and invokes the returned module entry contract. |
| `sub_4ED050` (`0x004ED050`) | `Sys_QueEvent` | Observed + exact source match | Pushes a retained event record into the Win32 event ring and frees the discarded payload on overflow. |
| `sub_4ED0E0` (`0x004ED0E0`) | `Sys_GetEvent` | Observed + exact source match | Returns queued events, pumps the message loop, translates console input and packets into queued events, and otherwise returns an empty timed event. |

Two practical takeaways from this pass:

- the Win32 host block around `0x004EC810` through `0x004ED0E0` still tracks
  the GPL `win_main.c` layout very closely
- the remaining uncertainty in this region is now mostly retail extensions
  rather than core platform wrappers

## New High-Confidence Aliases Added This Round

- filesystem/path wrappers:
  - `sub_4EC810`
  - `sub_4EC840`
  - `sub_4EC850`
  - `sub_4ECA60`
  - `sub_4ECAC0`
  - `sub_4ECD40`
- DLL and event queue owners:
  - `sub_4ECE80`
  - `sub_4ECEB0`
  - `sub_4ED050`
  - `sub_4ED0E0`

## Open Questions

1. `sub_4ECD80` is close to the GPL `Sys_GetClipboardData`, but the current
   retail body lacks the exact trailing newline/control-character strip that
   the writable source applies, so I left it unnamed.
2. `sub_4ECDF0` is a retail Unicode clipboard helper adjacent to the ANSI path,
   but there is no exact GPL owner name for it yet.
3. `sub_4F1290`, `sub_4F2900`, and `sub_4F4640` remain the most promising
   unmapped helpers from the earlier Win32/browser/ZMQ passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1003` raw alias entries, `1002` address-backed
  alias entries

## Completion Stats After Round 99

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1003` raw alias entries, `1002` address-backed
  aliases
- Address-backed coverage: `18.308%` of `5473` functions
- Alias delta this round: `10`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the next exact `win_main.c` wrapper
cluster, but it does not change the writable-source parity estimate by itself.
