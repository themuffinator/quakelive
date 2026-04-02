# Quake Live Steam Host Mapping Round 100

## Scope

This round continues the Win32 host pass from
[Round 99](./quakelive_steam_mapping_round_99.md), but closes the next stable
owner names immediately above and below the already-mapped DLL/event block:

1. the retained ANSI clipboard helper used by the engine paste paths
2. the command-bound input/network restart thunks
3. the main `Sys_Init` entry point that registers those commands and publishes
   the Win32 runtime environment

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- writable terminology in
  [win_main.c](../../src/code/win32/win_main.c)

Three aliases in this round are exact GPL owner matches. The clipboard helper
is also a stable source owner, but the retail body has a small behavioral delta
from the writable GPL implementation, so I am marking that one as an observed
owner match rather than an exact body clone.

## Clipboard Owner

The ANSI clipboard helper at `0x004ECD80` is now stable enough to promote as
`Sys_GetClipboardData`.

Observed local facts:

1. `sub_4ECD80` opens the Win32 clipboard, requests `CF_TEXT`, locks the
   clipboard handle, allocates a retained heap buffer sized from
   `GlobalSize(hMem) + 1`, copies the clipboard bytes, unlocks the handle, and
   closes the clipboard.
2. The writable owner in
   [win_main.c](../../src/code/win32/win_main.c) is `Sys_GetClipboardData`,
   and it performs the same Win32 clipboard-open / `CF_TEXT` / heap-copy flow
   in the same host source region.
3. The engine paste wrapper at `0x004BF024` calls `sub_4ECD80`, copies the
   returned text into a caller buffer, and frees the temporary allocation,
   matching the retained `CL_UI_GetClipboardData` / key-paste contract that
   consumes `Sys_GetClipboardData`.

The remaining caveat is body parity: the retail helper does not currently show
the trailing `strtok( data, "\n\r\b" )` cleanup that appears in the writable
GPL source. That is a behavior difference, but it does not change the owning
function identity.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4ECD80` (`0x004ECD80`) | `Sys_GetClipboardData` | Observed + source-owner match | Retained Win32 clipboard text fetch helper used by the engine paste paths; the retail body omits the GPL trailing newline/control-character scrub. |

## Restart Commands and `Sys_Init`

The next three host entry points are exact source matches.

Observed local facts:

1. `sub_4ED3E0` calls the already-retained input shutdown helper and then
   tailcalls the already-retained input init helper, matching
   `Sys_In_Restart_f`.
2. `sub_4ED3F0` is a pure tailcall into the retained network restart helper,
   matching `Sys_Net_Restart_f`.
3. `sub_4ED400` calls `timeBeginPeriod(1)`, registers `"in_restart"` with
   `sub_4ED3E0`, registers `"net_restart"` with `sub_4ED3F0`, fills the OS
   version structure, raises the same fatal strings:
   - `"Couldn't get OS info"`
   - `"Quake3 requires Windows version 4 or greater"`
   - `"Quake3 doesn't run on Win32s"`
4. The same body then selects the `arch` cvar from the Win32 platform/build,
   publishes `win_hinstance` and `win_wndproc`, initializes crash-dump setup,
   performs CPU detection, publishes the username, and initializes input,
   matching `Sys_Init` line-for-line at the ownership level.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4ED3E0` (`0x004ED3E0`) | `Sys_In_Restart_f` | Observed + exact source match | Command handler that shuts down and reinitializes the input subsystem. |
| `sub_4ED3F0` (`0x004ED3F0`) | `Sys_Net_Restart_f` | Observed + exact source match | Command handler that tailcalls the retained network restart helper. |
| `sub_4ED400` (`0x004ED400`) | `Sys_Init` | Observed + exact source match | Main Win32 host initialization entry point that registers restart commands, validates OS state, publishes ROM cvars, initializes crash handling, detects CPU type, and starts input. |

## New High-Confidence Aliases Added This Round

- clipboard owner:
  - `sub_4ECD80`
- restart/init owners:
  - `sub_4ED3E0`
  - `sub_4ED3F0`
  - `sub_4ED400`

## Open Questions

1. `sub_4ECDF0` is still a retail-only Unicode clipboard helper. The body is
   clear, but I do not yet have a stable retail owner name strong enough to
   promote.
2. `sub_4ED020` remains adjacent to this seam, but its current evidence only
   proves that it is a thin filesystem read helper layered over the already
   promoted `FS_Read`; it is not the Win32 `Sys_StreamedRead` owner.
3. `sub_4F1290`, `sub_4F2900`, and `sub_4F4640` remain the highest-value
   unmapped leftovers from the recent Win32/browser/ZMQ passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1007` raw alias entries, `1006` address-backed
  alias entries

## Completion Stats After Round 100

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1007` raw alias entries, `1006` address-backed
  aliases
- Address-backed coverage: `18.381%` of `5473` functions
- Alias delta this round: `4`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the next Win32 host ownership seam, but
it does not change the writable-source parity estimate by itself.
