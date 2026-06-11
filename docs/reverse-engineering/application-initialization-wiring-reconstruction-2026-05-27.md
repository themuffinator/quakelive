# Application Initialization Wiring Reconstruction - 2026-05-27

Scope: Windows executable host startup, common initialization, and the adjacent
client/server service-bootstrap handoffs for `quakelive_steam.exe`.

## Evidence Inputs

- Canonical binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- Ghidra companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`,
  `imports.txt`, `functions.csv`, and `decompile_top_functions.c`
- Symbol ledger:
  `references/analysis/quakelive_symbol_aliases.json`

## Primary Retail Owner Map

| Address | Alias | Size | Owner role |
| --- | --- | ---: | --- |
| `0x004ED830` | `WinMain` | `598` | Process entry after CRT startup; owns loading/console window setup, common/net bootstrap handoff, keyboard hook, tooltip common-control shell, browser root launch, and frame loop. |
| `0x004CBFD0` | `Com_Init` | `1773` | Common subsystem bootstrap: command/cvar/file/config/hunk setup, host cvars, `Sys_Init`, network channels, VMs, server/client init, profile pid, and default startup commands. |
| `0x004ED400` | `Sys_Init` | `898` | Windows system init: timer precision, restart commands, OS/CPU cvars, crash-relevant process cvars, and input init. |
| `0x004EF320` | `NET_Init` | `156` | Winsock startup, local address discovery, and network config enablement. |
| `0x004BC690` | `CL_Init` | `1951` | Client cvars/commands, browser command registration, Steam persona/country bridge, renderer/screen init, and client-ready flag. |
| `0x004E3AD0` | `SV_Init` | `1015` | Server cvars, map-pool data, Quake Live server policy cvars, and botlib setup. |
| `0x004EC580` | `Sys_WinkeyHookProc` | `117` | Low-level keyboard hook that conditionally consumes left/right Windows keydown events. |
| `0x004F4140` | `Zmq_RegisterCvarsAndInitRcon` | `10` | Global ZMQ RCON/runtime registration wrapper. |

## Observed Retail Startup Spine

Retail `WinMain` stores `hInstance`, parses the command line into the retail
wide-argv form, resets the millisecond base, creates the loading window, creates
the console, sets `SEM_FAILCRITICALERRORS`, destroys the loading window, then
calls:

1. `Com_Init(...)`
2. `NET_Init()`
3. `Zmq_RegisterCvarsAndInitRcon()`
4. `_getcwd(...)` and prints the working directory
5. hides the early console when neither dedicated nor `viewlog`
6. `SetWindowsHookExA(WH_KEYBOARD_LL, sub_4EC580, hInstance, 0)`
7. registers `winkey_disable` with flag `0x80000`
8. initializes a `tooltips_class32` common-control shell
9. opens `asset://ql/index.html` when Steam/browser service state allows it
10. loops through input frame work and `Com_Frame()`

The checked-in source already mirrored the high-level host sequence. Earlier
rounds reconstructed the explicit Windows-key hook and its shutdown unhook as
`Sys_WinkeyHookProc`, `Sys_InitWinkeyHook`, and `Sys_ShutdownWinkeyHook`.
Mapping round 487 reconstructs the adjacent native tooltip common-control shell
observed immediately after the hook and before the Steam web-menu URL launch.

## Reconstructed Source Behavior

- `WinMain` now installs the retail low-level keyboard hook after `Com_Init`,
  `NET_Init`, working-directory reporting, and early-console hiding.
- The hook registers `winkey_disable` with `CVAR_CLOUD`, matching retail flag
  `0x80000`.
- `Sys_WinkeyHookProc` follows the HLIL predicate: negative hook codes pass to
  `CallNextHookEx`; otherwise `HC_ACTION` plus enabled `winkey_disable` plus
  `WM_SYSKEYDOWN` or `WM_KEYDOWN` consumes `VK_LWIN` and `VK_RWIN` by returning
  `1`.
- `Sys_Error` and `Sys_Quit` now both call `Sys_ShutdownWinkeyHook()` after
  input shutdown and before the error message loop or console destruction,
  matching the retail unhook sites at `0x004EC755` and `0x004EC7C0`.
- `WinMain` now initializes a `tooltips_class32` common-control shell after
  the Windows-key hook, using the observed `ICC_BAR_CLASSES`, popup tooltip
  style, `HWND_NOTOPMOST` placement, desktop tool rectangle, `TTM_ADDTOOLA`,
  and inactive `TTM_ACTIVATE` message.
- `Sys_Error` and `Sys_Quit` destroy the tooltip shell after unhooking the
  Windows-key hook and before entering the fatal message loop or destroying the
  console.
- `references/analysis/quakelive_symbol_aliases.json` now promotes
  `sub_4EC580` to `Sys_WinkeyHookProc`.

## Intentional Policy-Aware Divergences

These are observed retail behaviors that remain deliberately source-adjusted:

- Retail `Com_Init` calls `SteamClient_Init()` before filesystem initialization
  when not dedicated, then fatals later if Steam is unavailable. The source
  keeps online service startup behind the repo policy gates, now refreshes the
  bounded platform-service table before `FS_InitFilesystem()` so SteamID-based
  homepath selection can work, and still calls the retained `SteamClient_Init()`
  once in the primary non-dedicated client startup path before `CL_Init()`.
- Retail `WinMain` calls `Zmq_RegisterCvarsAndInitRcon()` directly after
  `NET_Init()`. The source keeps the registration in `SV_Init()` so dedicated
  server policy cvars and server-owned service fallbacks are established
  together before botlib startup.
- Retail `WinMain` opens `asset://ql/index.html` directly after the native
  tooltip shell. The source now reconstructs the native tooltip shell but still
  opens the same URL through
  `CL_WebHost_BootstrapAwesomiumMenu()` after `SCR_Init()` so renderer
  dimensions exist, and keeps the path behind `QL_PLATFORM_HAS_ONLINE_SERVICES`.

## Confidence

High for the Windows-key hook: HLIL, imports, function size, string/cvar flag,
shutdown unhook sites, and `WinMain` call order all agree.

High for the startup owner map: aliases, `functions.csv`, HLIL call order, and
checked-in source owners align.

Medium for any later tooltip text-mutation work: shell creation is observed
directly, but no committed evidence yet shows downstream tooltip text mutation
outside the existing browser bridge callback. Round 487 therefore reconstructs
the shell and its empty desktop tool without changing browser tooltip
publication.

## Parity Estimate

Before the keyboard-hook reconstruction round, the scoped application-
initialization wiring lane was about `96.5%`: the main
host/common/client/server spine was already mapped, but the WinMain-owned
keyboard hook and shutdown unhook were absent.

After round 487, the scoped lane is about `98.4%`: the executable-owned hook
and native tooltip shell are reconstructed and statically guarded. Remaining
gaps are any later decision to move ZMQ/browser calls closer to retail without
violating the disabled-by-default online-services policy.

The repo-wide parity estimate remains **98%**.
