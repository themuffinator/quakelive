# Quake Live Steam Host Mapping Round 280

## Scope

- Continued the client-host mapping pass around the post-frame parse, screen,
  netchan, and UI/LAN bridge surface in `quakelive_steam.exe`.
- Focused on the `CL_Frame` adjacent Steam workshop completion helper, client
  netchan encode/decode wrappers, server-message parse owner, screen update
  helpers, and UI-facing LAN server-list helpers.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  confirms address-backed rows for every promoted owner in this pass:
  - `FUN_004bc320`, `FUN_004bce30`, `FUN_004bcef0`,
    `FUN_004bcf80`, `FUN_004bcf90`, `FUN_004bcfc0`
  - `FUN_004bd620`, `FUN_004bda00`, `FUN_004bdb90`,
    `FUN_004bdc00`, `FUN_004bdcb0`, `FUN_004bdeb0`
  - `FUN_004be040`, `FUN_004be080`, `FUN_004be3a0`,
    `FUN_004be460`, `FUN_004be4c0`, `FUN_004be520`,
    `FUN_004be6b0`, `FUN_004be7f0`, `FUN_004beb00`,
    `FUN_004beb80`, `FUN_004bed10`, and `FUN_004bede0`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  provides the host-side behavior:
  - `0x004BC320` checks the Steamworks/workshop download-settled state, emits
    the retail completion strings, conditionally restarts the filesystem, and
    calls `CL_DownloadsComplete`.
  - `0x004BCE30` and `0x004BCEF0` are the client netchan encode/decode pair:
    they preserve message cursor state, read the same header fields as source,
    seed the XOR key from `clc.challenge`, and walk acknowledged reliable
    command strings.
  - `0x004BCF80`, `0x004BCF90`, and `0x004BCFC0` wrap the common netchan
    fragment transmit, transmit, and process helpers.
  - `0x004BD620` parses the systeminfo configstring, updates `sv_serverid`,
    clears cheat cvars for non-demo clients, applies pure-server pak strings,
    mirrors systeminfo cvars locally, and clears `fs_game` when absent.
  - `0x004BDA00` is the top-level `CL_ParseServerMessage` owner with the
    bitstream switch over `svc_*`, including the recovered retail drop strings.
  - `0x004BDB90`, `0x004BDC00`, `0x004BDCB0`, `0x004BDEB0`,
    `0x004BE040`, `0x004BE080`, and `0x004BE3A0` cover the screen
    coordinate, fill/draw, demo-recording overlay, debug graph, init, and
    update-screen helpers.
  - `0x004BE460` backs the UI client-state copy helper used by the
    `QLUIImport_GetClientState` wrapper.
  - `0x004BE4C0`, `0x004BE520`, `0x004BE6B0`, `0x004BE7F0`,
    `0x004BEB00`, `0x004BEB80`, `0x004BED10`, and `0x004BEDE0` are the
    LAN server-list helpers for reset pings, add/remove, address string, ping,
    compare, visible marking, and visibility query.
- Source-side cross-checks:
  - `src/code/client/cl_main.c` owns `CL_Workshop_Frame`.
  - `src/code/client/cl_net_chan.c` owns the client netchan wrappers.
  - `src/code/client/cl_parse.c` owns `CL_SystemInfoChanged` and
    `CL_ParseServerMessage`.
  - `src/code/client/cl_scrn.c` owns the screen helpers.
  - `src/code/client/cl_ui.c` owns the UI client-state and LAN server-list
    helpers.

## Promoted Aliases

Updated `references/analysis/quakelive_symbol_aliases.json`:

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4BC320` | `CL_Workshop_Frame` | High | Steamworks completion helper called from `CL_Frame`, with retail completion strings. |
| `sub_4BCE30` | `CL_Netchan_Encode` | High | Reads server id, message ack, and reliable ack before XOR encoding payload bytes. |
| `sub_4BCEF0` | `CL_Netchan_Decode` | High | Reads reliable ack and XOR decodes with the acknowledged client command. |
| `sub_4BCF80` | `CL_Netchan_TransmitNextFragment` | High | Tail wrapper to `Netchan_TransmitNextFragment`. |
| `sub_4BCF90` | `CL_Netchan_Transmit` | High | Writes `clc_EOF`, encodes, then calls `Netchan_Transmit`. |
| `sub_4BCFC0` | `CL_Netchan_Process` | High | Calls `Netchan_Process`, decodes accepted packets, and updates size accounting. |
| `sub_4BD620` | `CL_SystemInfoChanged` | High | Parses `sv_serverid`, pure pak strings, systeminfo cvars, and `fs_game` fallback. |
| `sub_4BDA00` | `CL_ParseServerMessage` | High | Main `svc_*` server-message loop with retail parse/drop strings. |
| `sub_4BDB90` | `SCR_AdjustFrom640` | High | Scales x/y/w/h by `vidWidth / 640` and `vidHeight / 480`. |
| `sub_4BDC00` | `SCR_FillRect` | High | Sets color, scales coordinates, draws white shader rect, then clears color. |
| `sub_4BDCB0` | `SCR_DrawPic` | High | Scales coordinates and draws the supplied shader with full texcoords. |
| `sub_4BDEB0` | `SCR_DrawDemoRecording` | High | Draws `RECORDING %s: %ik` when demo recording is active. |
| `sub_4BE040` | `SCR_DebugGraph` | High | Stores value/color in the circular graph sample buffer. |
| `sub_4BE080` | `SCR_Init` | High | Registers `timegraph`, `debuggraph`, `graphheight`, `graphscale`, and `graphshift`. |
| `sub_4BE3A0` | `SCR_UpdateScreen` | High | Recursion guard and stereo/center `SCR_DrawScreenField` dispatch. |
| `sub_4BE460` | `CL_GetClientState` | High | Copies connection state, server name, update string, message string, and client number for UI. |
| `sub_4BE4C0` | `LAN_ResetPings` | High | Selects the server source slab and writes `-1` pings across the list. |
| `sub_4BE520` | `LAN_AddServer` | High | Parses address, de-duplicates, copies host name, marks visible, and increments source count. |
| `sub_4BE6B0` | `LAN_RemoveServer` | High | Finds matching address and compacts the selected server list. |
| `sub_4BE7F0` | `LAN_GetServerAddressString` | High | Source-bounded address-string getter for local/mplayer/global/favorites. |
| `sub_4BEB00` | `LAN_GetServerPing` | High | Returns stored ping or `-1` for invalid source/index. |
| `sub_4BEB80` | `LAN_CompareServers` | High | Compares host, map, client count, game type, or ping with sort-direction handling. |
| `sub_4BED10` | `LAN_MarkServerVisible` | High | Marks one server or all servers visible/invisible by source. |
| `sub_4BEDE0` | `LAN_ServerIsVisible` | High | Source-bounded visibility query. |

## Source Notes

- No runtime source behavior was changed in this round.
- `sub_4BE460` is promoted as `CL_GetClientState` to distinguish the client
  owner from the existing `QLUIImport_GetClientState` wrapper at `sub_4BF060`.
  The source helper remains the file-local `GetClientState`.
- The LAN helpers are source-private in `cl_ui.c`; their retail addresses are
  still useful because adjacent QL UI import wrappers call into this exact
  surface.

## Still Open

- The older screen text helpers at `0x004BDDF0` and `0x004BDE80` remain
  unpromoted in this pass. They are adjacent to `SCR_DrawDemoRecording`, but
  the current source text path has been reconstructed through retained
  renderer text exports, so their exact source names should be recovered in a
  dedicated screen-text pass. Neighboring `0x004BDD40` and `0x004BDD90`
  already carry separate host-text aliases in the current ledger and were not
  revalidated by this round.
- `sub_4BF0E0` remains recorded under the existing UI import-facing name even
  though it also has the body shape of `LAN_GetServerCount`; this pass avoided
  renaming existing aliases outside the focused unmapped tranche.

## Guardrail

- Added
  `tests/test_engine_client_command_parity.py::test_client_parse_screen_ui_mapping_round_280_promotes_hlil_backed_symbols`.
- The guard checks:
  - promoted aliases in `quakelive_symbol_aliases.json`;
  - matching Ghidra function rows;
  - HLIL snippets for workshop completion, netchan encode/decode/transmit,
    systeminfo parsing, server-message parsing, screen helpers, and LAN helper
    behavior;
  - source-side owner signatures for `cl_main.c`, `cl_net_chan.c`,
    `cl_parse.c`, `cl_scrn.c`, and `cl_ui.c`;
  - this mapping note's key alias rows and open-question notes.

## Parity Estimate

- Before: focused parse/screen/UI bridge symbol confidence was good for the
  large public owners but had many stable helper bodies missing from the alias
  ledger, about `88%` for this focused lane.
- After: the workshop frame, netchan wrappers, systeminfo/server-message
  parse owners, screen helpers, and LAN server-list helpers are explicitly
  mapped and guarded, about `95%` for this focused lane.
- Overall strict Windows replacement parity remains `100%`; repo-wide parity
  remains `98%`. This pass improves evidence freshness and symbol precision
  rather than closing a new runtime gap.
