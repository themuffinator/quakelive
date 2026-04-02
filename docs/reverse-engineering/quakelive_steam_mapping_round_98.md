# Quake Live Steam Host Mapping Round 98

## Scope

This round shifts away from the remaining browser/ZMQ stragglers and closes a
larger Win32 host seam instead:

1. the shared `Q3 WinConsole` frontend in `win_syscon.c`
2. the nearby `win_wndproc.c` helpers that still match the GPL source almost
   one-for-one
3. the small `win_main.c` wrappers that feed the console frontend during error
   and shutdown paths
4. the two retail-only loading-window helpers layered on top of the shared
   console class

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/`
- writable terminology in
  [win_syscon.c](../../src/code/win32/win_syscon.c),
  [win_wndproc.c](../../src/code/win32/win_wndproc.c), and
  [win_main.c](../../src/code/win32/win_main.c)

Most of these names are exact source matches. The only new names that are not
present in the GPL tree are the retail loading-window helpers at `0x004F0220`
and `0x004F0D70`; those are still constrained by direct call order, window
title, and ownership over `data_12d16f4`.

## `win_main.c` Console Feed Wrappers

The higher-level wrappers are straightforward and still line up exactly with
the writable Win32 host source:

- `sub_4EC6E0` appends the formatted fatal text into the console buffer, sets
  the error box text, shows the console, shuts input down, and pumps a Windows
  message loop forever, which is the retail `Sys_Error` path
- `sub_4EC7A0` tears platform state down and then exits on the normal path,
  which matches `Sys_Quit`
- `sub_4EC7F0` is the one-step wrapper that forwards into the console append
  path, matching `Sys_Print`
- `sub_4EC820` snapshots the process current working directory into a retained
  static buffer and returns it, matching `Sys_Cwd`

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4EC6E0` (`0x004EC6E0`) | `Sys_Error` | Observed + exact source match | Fatal Win32 error dialog path; appends the error text to the console buffer, populates the retained error box, shows the console, shuts input down, and pumps messages until quit. |
| `sub_4EC7A0` (`0x004EC7A0`) | `Sys_Quit` | Observed + exact source match | Normal Win32 process shutdown path; tears platform state down, destroys the console frontend, and exits unless the caller asked to return. |
| `sub_4EC7F0` (`0x004EC7F0`) | `Sys_Print` | Observed + exact source match | Thin wrapper that forwards one console line into `Conbuf_AppendText`. |
| `sub_4EC820` (`0x004EC820`) | `Sys_Cwd` | Observed + exact source match | Copies the process current working directory into the retained static buffer and returns it. |

## Shared `Q3 WinConsole` Frontend

The next block is the shared console frontend anchored in `win_syscon.c`.
The class name, child controls, button labels, and message handling all match
the writable source closely:

- `sub_4F0260` creates the `"Quake Live Console"` top-level window, installs
  the `copy` / `clear` / `quit` buttons, subclasses the input line, creates
  the scrollback edit control, and stores the retained handles
- `sub_4F0540`, `sub_4F05B0`, `sub_4F06A0`, `sub_4F06D0`, `sub_4F0850`,
  `sub_4F08F0`, and `sub_4F00F0` then match the GPL `Sys_DestroyConsole`,
  `Sys_ShowConsole`, `Sys_ConsoleInput`, `Conbuf_AppendText`,
  `Sys_SetErrorText`, `ConWndProc`, and `InputLineWndProc` owners

Retail extends this same class with an early loading window:

- `sub_4F0D70` registers `Q3 WinConsole` with `sub_4F08F0`, creates a centered
  popup titled `"Loading Quake Live"`, and stores its handle in `data_12d16f4`
- `sub_4F0220` hides, closes, and destroys that retained loading-window handle
- `sub_4F08F0` therefore still reads most cleanly as `ConWndProc`, but now
  with an added loading-window branch that loads `splash.bmp` and paints it
  during startup

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F00F0` (`0x004F00F0`) | `InputLineWndProc` | Observed + exact source match | Input-line subclass procedure for the retained console edit control; captures Enter, appends the line to the console text ring, clears the edit box, and otherwise tailcalls the saved original WndProc. |
| `sub_4F0220` (`0x004F0220`) | `Sys_DestroyLoadingWindow` | Observed + inferred | Retail startup helper that hides, closes, destroys, and clears the retained loading window at `data_12d16f4`. |
| `sub_4F0260` (`0x004F0260`) | `Sys_CreateConsole` | Observed + exact source match | Creates the retained `Q3 WinConsole` frontend, fonts, input line, buttons, and scrollback buffer, then installs the input-line subclass owner. |
| `sub_4F0540` (`0x004F0540`) | `Sys_DestroyConsole` | Observed + exact source match | Destroys the retained console child windows and top-level `Q3 WinConsole` window and unregisters the shared class. |
| `sub_4F05B0` (`0x004F05B0`) | `Sys_ShowConsole` | Observed + exact source match | Applies the retained console visibility level `0/1/2`, tracks `quitOnClose`, and hides, shows, or minimizes the console window accordingly. |
| `sub_4F06A0` (`0x004F06A0`) | `Sys_ConsoleInput` | Observed + exact source match | Returns the retained pending console input line when one is present and clears the producer buffer afterward. |
| `sub_4F06D0` (`0x004F06D0`) | `Conbuf_AppendText` | Observed + exact source match | Normalizes line endings, strips Quake color escapes, tracks the scrollback character budget, and appends the text into the retained console buffer edit control. |
| `sub_4F0850` (`0x004F0850`) | `Sys_SetErrorText` | Observed + exact source match | Copies the retained fatal error string, creates the top error box on first use, populates it, and destroys the interactive input line. |
| `sub_4F08F0` (`0x004F08F0`) | `ConWndProc` | Observed + exact source match | Shared `Q3 WinConsole` window procedure; handles copy/clear/quit commands, retained error-box coloring, console close/show behavior, and the retail loading-window splash branches. |
| `sub_4F0D70` (`0x004F0D70`) | `Sys_CreateLoadingWindow` | Observed + inferred | Retail startup helper that registers the shared `Q3 WinConsole` class and creates the centered popup loading window titled `"Loading Quake Live"`. |

Two practical takeaways from this seam:

- the retail host still keeps the Quake III Win32 console frontend largely
  intact, even though it now doubles as the early loading/splash surface
- the loading window is not a separate UI subsystem; it is a retained wrapper
  layered on top of the same `Q3 WinConsole` class and `ConWndProc`

## `win_wndproc.c` Activation and Key Helpers

The adjacent activation and keyboard helpers also match the GPL source
directly:

- `sub_4F11C0` / `sub_4F1230` implement the Alt-Tab disable/enable pair
- `sub_4F1530` logs `VID_AppActivate: %i\n`, updates the active/minimized
  flags, and forwards into the input-activation path
- `sub_4F15C0` translates Win32 scan-code state into Quake keynums through the
  retained translation table

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F11C0` (`0x004F11C0`) | `WIN_DisableAltTab` | Observed + exact source match | Disables Alt-Tab handling through `RegisterHotKey` on WinNT or `SPI_SETSCREENSAVERRUNNING` on older Windows, then marks the retained flag as armed. |
| `sub_4F1230` (`0x004F1230`) | `WIN_EnableAltTab` | Observed + exact source match | Restores the normal Alt-Tab/screensaver state and clears the retained disable flag. |
| `sub_4F1530` (`0x004F1530`) | `VID_AppActivate` | Observed + exact source match | Updates the retained active/minimized video state on app activation changes and forwards that state into the input-activation owner. |
| `sub_4F15C0` (`0x004F15C0`) | `MapKey` | Observed + exact source match | Maps Win32 keyboard scan codes and extended-key state into Quake keynums. |

## New High-Confidence Aliases Added This Round

- `win_main.c` wrappers:
  - `sub_4EC6E0`
  - `sub_4EC7A0`
  - `sub_4EC7F0`
  - `sub_4EC820`
- shared `Q3 WinConsole` frontend:
  - `sub_4F00F0`
  - `sub_4F0220`
  - `sub_4F0260`
  - `sub_4F0540`
  - `sub_4F05B0`
  - `sub_4F06A0`
  - `sub_4F06D0`
  - `sub_4F0850`
  - `sub_4F08F0`
  - `sub_4F0D70`
- `win_wndproc.c` helpers:
  - `sub_4F11C0`
  - `sub_4F1230`
  - `sub_4F1530`
  - `sub_4F15C0`

## Open Questions

1. `sub_4F1290` is now clearly the retail-only windowed-size sync helper that
   re-reads the live client rect, updates `r_windowedMode` /
   `r_windowedWidth` / `r_windowedHeight`, and queues `vid_restart fast`, but
   the exact source-level name is still not anchored.
2. `sub_4F2900` remains the small browser-input helper that injects one fixed
   keyboard event into the retained `Awesomium::WebView` during activation.
3. `sub_4F4640` still looks like the retained `idZMQ` RCON peer-node allocator
   or constructor, but the current decompiler signature still hides the peer
   identity argument behind stack artifacts.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `993` raw alias entries, `992` address-backed alias
  entries

## Completion Stats After Round 98

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `993` raw alias entries, `992` address-backed
  aliases
- Address-backed coverage: `18.125%` of `5473` functions
- Alias delta this round: `18`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the next Win32 host-console seam and a
matching set of activation/input helpers, but it does not change the writable
source parity estimate by itself.
