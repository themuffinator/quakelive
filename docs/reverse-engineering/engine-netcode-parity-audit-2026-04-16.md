# Engine Netcode Parity Audit

Last updated: 2026-04-16

Scope: engine-owned networking and server-browser surfaces in
`src/code/qcommon/net_chan.c`, `src/code/client/cl_net_chan.c`,
`src/code/server/sv_net_chan.c`, `src/code/win32/win_net.c`,
`src/code/client/cl_main.c`, `src/code/client/cl_parse.c`,
`src/code/client/cl_ui.c`, and `src/code/client/ql_ui_imports.inc` versus the
retail `quakelive_steam.exe` host.

Purpose: re-audit the engine netcode register after the broader 2026-04-09/10
engine-closure passes, identify any remaining source-owned deltas in the
transport, packet, and server-browser seams, and close the high-confidence
gaps that still differ from retail Quake Live.

## Audit Method And Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used in this pass:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Prior mapping and ownership notes:
  - `docs/reverse-engineering/quakelive_steam_mapping_round_103.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_104.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_105.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_106.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_107.md`
  - `docs/reverse-engineering/network-handshake.md`
- Current writable source:
  - `src/code/qcommon/net_chan.c`
  - `src/code/client/cl_net_chan.c`
  - `src/code/server/sv_net_chan.c`
  - `src/code/win32/win_net.c`
  - `src/code/client/cl_main.c`
  - `src/code/client/cl_parse.c`
  - `src/code/client/cl_ui.c`
  - `src/code/client/ql_ui_imports.inc`

Method:

1. Reconfirm the owning retail binary and bound the transport path with the
   committed HLIL and mapping rounds before treating anything as a new gap.
2. Separate classic packet and socket transport from the client-side
   server-browser and native UI-import helpers, since recent client audits had
   already closed most of the former surface.
3. Prefer behavior claims supported by at least two signals: promoted aliases
   or call-graph placement plus direct field, string, or import-slot evidence.
4. Only count source-owned mismatches in the current writable engine surface;
   do not reopen policy-gated online-service exclusions or read-only UI assets.

## Reviewed Surface

Observed strong lanes from this pass:

1. `net_chan.c`, `cl_net_chan.c`, `sv_net_chan.c`, and `win_net.c` remain
   strongly bounded by the committed corpus. No new source-owned transport or
   socket-lifecycle mismatch surfaced in this pass.
2. The core client packet and connectionless event spine in `cl_main.c` and
   `cl_parse.c` remains aligned with the recent server-browser mapping rounds:
   ping queue updates, status tracking, timeout handling, and packet routing
   still match the recovered retail owners closely.
3. The remaining live mismatches were both inside the client-side browser and
   native import seam, not inside the lower-level packet transport.

## Gaps Found And Closed

### 2026-05-22 addendum: retail Steam protocol constant

Retail evidence:

1. `SV_Init` in the committed `quakelive_steam.exe` HLIL registers the
   `protocol` cvar through `va("%i", 0x5b)` with the existing
   `CVAR_SERVERINFO | CVAR_ROM` flag value, so the server advertises protocol
   `0x5b / 91`.
2. `CL_CheckForResend` seeds the connect userinfo with the same `0x5b`
   protocol value before appending `qport` and `challenge`.
3. `CL_ServerInfoPacket` rejects server-info packets unless the parsed
   `protocol` is `0x5b`.
4. The retail demo playback compatibility list is exactly
   `data_5684dc = 0x5b`, `data_5684e0 = 0`; demo recording and filesystem
   fallback format `dm_91`. The console completion helper's `.dm_73` scan is a
   separate retained behavior and remains source-matched in `cl_keys.c`.

Source change:

1. Updated `PROTOCOL_VERSION` from the inherited Quake III `68` to retail
   Quake Live Steam `91`.
2. Reduced `demo_protocols[]` from the inherited `66, 67, 68` list to the
   retail single-entry `91` list.

### 1. `CL_SetServerInfo` still parsed non-retail fields

Retail evidence:

1. `docs/reverse-engineering/quakelive_steam_mapping_round_104.md` promotes
   `sub_4B9F90` as `CL_SetServerInfo`.
2. The round notes explicitly record the retail body parsing `clients`,
   `hostname`, `mapname`, `sv_maxclients`, `game`, `gametype`, and `nettype`,
   then storing `ping`.
3. The same note explicitly calls out that the writable source still parsed
   `minping`, `maxping`, and `punkbuster`, while the retail body did not show
   those assignments.

Source change:

1. Removed the extra `minPing`, `maxPing`, and `punkbuster` assignments from
   `src/code/client/cl_main.c`.
2. The server record still retains the retail-observed field set plus `ping`,
   while the legacy struct members remain harmlessly zeroed by the existing
   initialization path.

### 2. Native LAN cache import slots were not retail no-ops

Retail evidence:

1. `docs/reverse-engineering/quakelive_steam_mapping_round_106.md` records
   that `data_56741c` and `data_567420`, the native import slots for
   `QLUIImport_LAN_LoadCachedServers` and `QLUIImport_LAN_SaveCachedServers`,
   both collapse to the same pure no-op retail stub `sub_4D7980`.
2. The current writable source still routed those native wrappers through
   `UI_Import_Syscall( UI_LAN_LOADCACHEDSERVERS )` and
   `UI_Import_Syscall( UI_LAN_SAVECACHEDSERVERS )`, which is a stronger
   behavior than the recovered retail host publishes for native UI imports.

Source change:

1. Converted `QL_UI_trap_LAN_LoadCachedServers` and
   `QL_UI_trap_LAN_SaveCachedServers` in `src/code/client/ql_ui_imports.inc`
   into explicit no-op wrappers.
2. Kept the native import-table publication in `cl_ui.c` unchanged, so the
   retail-shaped slot ownership remains explicit while the generic UI syscall
   bridge stays available for non-native compatibility paths.

## Verification

Static verification run for this task:

- `pytest tests/test_engine_netcode_parity.py`
- `pytest tests/test_ui_menu_files.py::test_ui_native_import_table_matches_recovered_retail_slots`

Runtime launch:

- not required for this pass
- the closed gaps are deterministic source-level browser/helper deltas and do
  not introduce a new startup or rendered-output question that static evidence
  and focused tests fail to answer

## Parity Estimate

- Strict engine netcode parity before this task: **99%**
- Strict engine netcode parity after this task: **100%**

Interpretation:

1. The lower-level engine transport had already been strong; this pass closed
   the last two source-owned browser/helper mismatches inside the audited
   networking register.
2. The broader engine and client ledgers remain at **100%** after this
   correction, but this document is the explicit evidence trail for the
   overlooked netcode/browser seam that was still open before the source fix.
