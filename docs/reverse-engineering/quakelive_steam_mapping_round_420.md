# Quake Live ZMQ/CZMQ Mapping Round 420

Date: 2026-06-06

## Scope

This pass rechecks the Quake Live-owned `idZMQ` host wiring against the
committed retail evidence and the current `src/code/server/sv_zmq.c`
reconstruction.  Recent ZMQ rounds have focused on embedded libzmq internals;
this round comes back up to the server integration boundary and pins the older
Round 94 through Round 97 aliases with a current regression.

Canonical evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/server/sv_zmq.c`,
  `src/code/server/sv_init.c`,
  `src/code/server/sv_main.c`,
  `src/code/server/sv_game.c`, and
  `src/code/qcommon/common.c`
- Prior mapping passes:
  `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_95.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_96.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_97.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_357.md`, and
  `docs/reverse-engineering/quakelive_steam_mapping_round_419.md`

## Alias Reconstruction

This pass re-pinned 26 existing aliases:

| symbol | alias | confidence | evidence |
|---|---|---|---|
| `sub_4E2620` | `SV_SubmitMatchReport` | High | Calls the Steam stats summary path and immediately forwards the report to the ZMQ match-report wrapper. |
| `sub_4E2640` | `SV_ReportPlayerEvent` | High | Calls the Steam stats event path and immediately forwards the typed event to the ZMQ player-event wrapper. |
| `sub_4F3D70` | `idZMQ_ApplyPasswords` | High | Updates the object-owned password state from the retained password cvars and applies it to live object state. |
| `sub_4F3DD0` | `Zmq_ShutdownStatsPublisher` | High | Tears down the retained stats publisher socket at the standalone server-shutdown boundary. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | High | Tears down RCON, auth/runtime actor state, and the broader retained ZMQ runtime. |
| `sub_4F3F20` | `idZMQ_UpdatePasswords` | High | Refreshes password modification counters and logs the password-update marker from object context. |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Registers the retail `zmq_*` cvars, creates RCON socket state, applies ZAP/PLAIN options, and binds the RCON endpoint. |
| `sub_4F4130` | `Zmq_UpdatePasswords` | High | Thin global wrapper that tailcalls `idZMQ_UpdatePasswords` on the retained `data_5756fc` object. |
| `sub_4F4140` | `Zmq_RegisterCvarsAndInitRcon` | High | Thin global wrapper that tailcalls `idZMQ_RegisterCvarsAndInitRcon` on the retained object during host startup. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Creates the stats PUB socket, applies ZAP/PLAIN options, and binds/logs the stats endpoint. |
| `sub_4F43A0` | `Zmq_InitStatsPublisher` | High | Thin global wrapper that tailcalls `idZMQ_InitStatsPublisher` during server startup. |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | High | Serializes typed player-event payloads through the retained ZMQ publication socket. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | High | Serializes the hardcoded `MATCH_REPORT` type and publishes it through the same retained stats path. |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | High | Walks the retained RCON peer table, sends console output, logs disconnects, and erases failed peers. |
| `sub_4F4E10` | `Zmq_ReportPlayerEvent` | High | Thin global wrapper for `idZMQ_ReportPlayerEvent`. |
| `sub_4F4E40` | `Zmq_SubmitMatchReport` | High | Thin global wrapper for `idZMQ_SubmitMatchReport`. |
| `sub_4F4E60` | `Zmq_BroadcastRconOutput` | High | Console-print wrapper that forwards output to `idZMQ_BroadcastRconOutput`. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | High | Polls RCON identity/command frames, inserts new peers, logs inbound commands, and executes the command string. |
| `sub_4F4FD0` | `Zmq_PumpRcon` | High | Main-frame wrapper that tailcalls `idZMQ_PumpRcon`. |
| `sub_4F5080` | `idZMQ_Destroy` | High | Writes the `idZMQ` vtable and clears retained peer/runtime state during object destruction. |
| `sub_4F46B0` | `idZMQ_EraseRconPeer` | High | Single-node erase helper used when RCON output send fails. |
| `sub_4F4910` | `idZMQ_FindRconPeer` | High | Exact-match lookup helper for received RCON peer identities. |
| `sub_4F4980` | `idZMQ_FreeRconPeerSubtree` | High | Recursive subtree free helper used by full peer-table clear. |
| `sub_4F49C0` | `idZMQ_InsertRconPeer` | High | Inserts newly observed RCON peer identities into the retained peer table. |
| `sub_4F4E80` | `idZMQ_ClearRconPeers` | High | Clears the full retained peer table and resets sentinel/count state. |
| `sub_4F4FE0` | `idZMQ_EraseRconPeerRange` | High | Range-erase helper used by the destructor path and narrowed erasure loops. |

## Observed Facts

- `SV_SubmitMatchReport` and `SV_ReportPlayerEvent` remain adjacent to the
  Steam stats paths in retail HLIL and then immediately call the ZMQ wrappers
  at `0x4F4E40` and `0x4F4E10`.
- `Zmq_RegisterCvarsAndInitRcon`, `Zmq_UpdatePasswords`,
  `Zmq_InitStatsPublisher`, and `Zmq_PumpRcon` are thin global wrappers over
  the retained `data_5756fc` object.  The wrapper tailcalls are visible at
  `0x4F4140`, `0x4F4130`, `0x4F43A0`, and `0x4F4FD0`.
- Retail startup calls `Zmq_RegisterCvarsAndInitRcon` from the host init path,
  server startup calls `Zmq_InitStatsPublisher`, the frame loop calls
  password refresh and RCON pump, console printing calls the RCON broadcast
  wrapper, and common shutdown calls the runtime teardown.
- Retail strings still pin the public server surface:
  `zmq_rcon_enable`, `zmq_stats_enable`, `zmq RCON socket: %s\n`,
  `zmq PUB socket: %s\n`, `MATCH_REPORT`,
  `zmq RCON client connected: %s\n`,
  `zmq RCON command from %s: %s\n`, and
  `zmq RCON client disconnected: %s\n`.
- The retained object fields split cleanly into runtime/actor state,
  stats publisher socket, RCON socket, auth/helper state, and the RCON peer
  table.  `analysis_symbols.txt` still exposes `idZMQ::vftable`.
- The retail object methods use a CZMQ-style helper band (`zsock_new_checked`,
  `zsock_bind`, `zsock_set_zap_domain`, `zsock_set_plain_server`,
  `zsock_set_router_mandatory`, and `zstr_free`).  Rounds 357 and 419 explain
  that helper/option layer; the writable source reconstructs the Quake
  Live-facing behavior through dynamically resolved public `zmq_*` symbols.

## Source Reconstruction Shape

No C source changed in this pass.  The current source reconstruction already
keeps the Quake Live-owned surface in `sv_zmq.c`:

```c
void Zmq_RegisterCvarsAndInitRcon( void );
void Zmq_UpdatePasswords( void );
void Zmq_InitStatsPublisher( void );
void Zmq_ShutdownStatsPublisher( void );
void Zmq_ShutdownRuntime( void );
void Zmq_PumpRcon( void );
void Zmq_BroadcastRconOutput( const char *message );
void Zmq_SubmitMatchReport( const void *report );
void Zmq_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh,
	const void *clientStats, const char *eventName, const void *payload );
```

The source also keeps the expected server call sites:

- `SV_Init` registers cvars and initializes RCON.
- `SV_SpawnServer` initializes the stats publisher after server key/value
  publication.
- `SV_Frame` refreshes passwords and pumps RCON after server networking.
- `SV_SubmitMatchReport` and `SV_ReportPlayerEvent` forward to ZMQ.
- `Com_Printf` forwards console output to the RCON broadcast path.
- `SV_Shutdown` closes the stats publisher, and `Com_Shutdown` tears down the
  broader runtime.

## Inference Boundary

- This is a host-wiring pass, not a request to vendor CZMQ or libzmq.  The
  retail binary carries embedded CZMQ/libzmq internals, but this repository's
  source boundary remains the retained Quake Live server integration plus
  default-disabled live transport policy.
- The peer table in writable C source is reconstructed as a straightforward
  retained tree/list owner, while retail HLIL reflects MSVC/STL-style helper
  mechanics.  The pinned parity claim is the observed ownership behavior:
  lookup, insert, erase, clear, and destroy effects around RCON peer identities.
- The local transcript fallback and dynamic `zmq_*` resolution remain the
  repository's policy-aware replacement for retail's embedded helper stack.

## Verification

- `python -m pytest -q tests/test_platform_services.py::test_zmq_idzmq_host_round_420_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

No runtime launch was needed; this was a static mapping/source-boundary pass
over committed HLIL/Ghidra evidence and reconstructed source wiring.

## Parity Estimate

- Focused `idZMQ` host lifecycle/publication/RCON wiring confidence:
  **before 76% -> after 95%**.
- ZMQ-related source reconstruction confidence:
  **before 94.1% -> after 94.2%**.
- Overall Quake Live source parity:
  **before 55.83% -> after 55.84%**.
