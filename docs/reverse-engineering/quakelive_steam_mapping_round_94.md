# Quake Live Steam Host Mapping Round 94

## Scope

This round closes two adjacent `quakelive_steam.exe` seams that were still
missing stable names after the earlier browser-host passes:

1. the live browser runtime helpers between `QLWebHost_HideBrowser` and
   `QLWebHost_ClearCache_f`
2. the undocumented ZeroMQ host block rooted at `zmq\\id_zmq.cpp`

The evidence order stayed the same:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/`
- earlier browser notes in
  [Round 02](./quakelive_steam_mapping_round_02.md) and
  [Round 03](./quakelive_steam_mapping_round_03.md)

The names promoted here stay on the high-confidence side of the repo bar.
`sub_4F2590`, `sub_4F2900`, and the `sub_4F3DD0` / `sub_4F3DF0` shutdown split
remain intentionally unnamed.

## Browser Runtime Helpers

Round 02 and Round 03 already named the higher-level browser publishers and
console command handlers. The missing runtime seam sat immediately below that
surface in the active input, resize, and texture-refresh path.

The stable callsite evidence is compact:

- `004BB8B7` and `004BB976` both execute `sub_4F25F0(sub_4F25C0())` during the
  renderer/UI restart path
- `004B551A` forwards native pointer motion into `sub_4F2750(arg1, arg2)`
- `004F1D5A` routes the browser keyboard capture path through `sub_4F28A0(...)`

That is enough to promote four aliases.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F25C0` (`0x004F25C0`) | `QLWebView_Resize` | Observed | Calls the active `WebView` slot at `+0x9c` with the live browser viewport dimensions `data_1743bcc` / `data_1743bd0`. |
| `sub_4F25F0` (`0x004F25F0`) | `QLWebView_RebuildSurfaceImage` | Observed | Pulls the current `Awesomium::BitmapSurface`, copies it into a temporary RGBA buffer, recreates renderer image `"browser"` through `R_CreateImage`, and rebinds the cached material/image owner. |
| `sub_4F2750` (`0x004F2750`) | `QLWebView_InjectMouseMove` | Observed | Scales native window coordinates into browser-surface coordinates, caches them in `data_12d3054` / `data_12d3048`, and injects pointer motion through the `WebView` slot at `+0xd0` when browser capture is live. |
| `sub_4F28A0` (`0x004F28A0`) | `QLWebView_InjectKeyboardEvent` | Observed | Constructs an `Awesomium::WebKeyboardEvent` and injects it through the `WebView` slot at `+0xe0` when browser key capture (`bit 0x20`) is armed and the conflicting input flag (`bit 0x1`) is clear. |

Two practical takeaways from this seam:

- the heavyweight browser image refresh path is separate from
  `QLWebHost_PumpFrame`; `sub_4F25F0` recreates the renderer image while
  `QLWebHost_PumpFrame` only uploads dirty surface contents into that retained
  image
- the host owns direct browser input injection for mouse movement and keyboard
  events; that behavior is not hidden inside the generic publisher suite

## ZMQ Host Seam

The block at `0x004F3D70` through `0x004F43A0` was still absent from the alias
map even though the HLIL exposes a clean subsystem boundary with strings from
`zmq\\id_zmq.cpp`.

The key retail signals line up cleanly:

- startup calls `sub_4F4140()` at `004ED8C1`, which tailcalls into
  `sub_4F3F80(...)`
- server initialization calls `sub_4F43A0()` at `004E354C`, which tailcalls
  into `sub_4F4210(...)`
- the main frame loop checks password-cvar modification counters and calls
  `sub_4F4130()` at `004CC8EF`, which tailcalls into `sub_4F3F20(...)`
- the string set includes `zmq_rcon_enable`, `zmq_stats_enable`,
  `zmq_rcon_password`, `zmq_stats_password`, `zmq RCON socket: %s\n`,
  `zmq PUB socket: %s\n`, and
  `zmq stats and rcon passwords updated\n`

That gives a stable subsystem split between password application, startup/RCON
bootstrap, and server-side stats publishing.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F3D70` (`0x004F3D70`) | `Zmq_ApplyPasswords` | Observed | Snapshots the `zmq_stats_password` and `zmq_rcon_password` cvar modification counters and, when the shared ZMQ actor/socket owner exists, applies `PLAIN` auth credentials to it. |
| `sub_4F3F20` (`0x004F3F20`) | `Zmq_UpdatePasswords` | Observed | Refreshes the cached password strings from both cvars, reapplies them through `Zmq_ApplyPasswords`-equivalent logic when the shared owner is live, and logs `zmq stats and rcon passwords updated`. |
| `sub_4F3F80` (`0x004F3F80`) | `Zmq_RegisterCvarsAndInitRcon` | Observed | Registers the full `zmq_*` cvar family, creates the shared actor/context when needed, enables verbose auth, applies passwords, and binds the `rcon` socket at `tcp://%s:%i`. |
| `sub_4F4210` (`0x004F4210`) | `Zmq_InitStatsPublisher` | Observed | Reuses the shared actor/context, applies passwords, resolves `zmq_stats_*` with `net_ip` / `net_port` fallbacks, creates the `stats` PUB socket, and binds/logs the resulting endpoint. |

Two practical takeaways from this seam:

- `quakelive_steam.exe` owns an engine-local ZeroMQ service split into an RCON
  listener and a stats PUB publisher; this is not a Steamworks or browser
  subsystem
- the stats publisher is server-startup-owned while the shared password/RCON
  bootstrap runs during the broader host initialization path

## New High-Confidence Aliases Added This Round

- browser runtime helpers:
  - `sub_4F25C0`
  - `sub_4F25F0`
  - `sub_4F2750`
  - `sub_4F28A0`
- ZMQ host seam:
  - `sub_4F3D70`
  - `sub_4F3F20`
  - `sub_4F3F80`
  - `sub_4F4210`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `952` raw alias entries, `951` address-backed alias
  entries

## Open Questions

1. `sub_4F2590` still looks like a thin `WebCore::Update()` wrapper called once
   per rendered client frame, but the current evidence is still only a single
   vtable jump plus callsite context, so I left it unnamed.
2. `sub_4F2900` injects one fixed browser keyboard event (`0x11`,
   `0x1d0001`), which looks like a synthetic modifier-key path, but the exact
   semantic needs one more input trace.
3. `sub_4F3DD0` and `sub_4F3DF0` clearly tear down `zmq\\id_zmq.cpp` lifetime
   owners, but the exact split between socket lifetime and actor/context
   lifetime still needs one more pass.

## Completion Stats After Round 94

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `952` raw alias entries, `951` address-backed
  aliases
- Address-backed coverage: `17.376%` of `5473` functions
- Alias delta this round: `8`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. Alias coverage improved, but writable source
parity against the retail host remained unchanged.
