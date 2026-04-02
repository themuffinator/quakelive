# Quake Live Steam Host Mapping Round 95

## Scope

This round closes the long-open server-side summary/report wrapper question
from [Round 04](./quakelive_steam_mapping_round_04.md) and extends the ZMQ
mapping from [Round 94](./quakelive_steam_mapping_round_94.md) into the
`idZMQ` runtime itself:

1. the engine-facing `SV_SubmitMatchReport` / `SV_ReportPlayerEvent` wrappers
2. the matching `idZMQ` / `Zmq_` publication layer for match reports and
   player events
3. the RCON runtime path that pumps inbound commands and broadcasts console
   output back to connected peers

The evidence order stayed the same:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`
- writable terminology in
  [sv_game.c](../../src/code/server/sv_game.c)

The key ownership anchor that Round 04 still lacked is now explicit in the
committed companion corpus:

- `analysis_symbols.txt` exposes RTTI for `idZMQ`
- `data_5756fc` is typed as `idZMQ::vftable`
- `sub_4F5080` writes that vtable and tears down the retained object state

That makes the surrounding helpers stable enough to name as one coherent seam.

## Engine-Facing Summary / Event Wrappers

Round 04 left `sub_4E2620` and `sub_4E2640` unnamed because they looked like
container front ends without a stable owner. The wrapper chain is now clear:

- `004E2628` calls `SteamStats_BroadcastSummary`
- `004E2638` immediately tailcalls into the ZMQ match-report publisher
- `004E265A` calls `SteamStats_ProcessEvent`
- `004E2676` immediately tailcalls into the ZMQ player-event publisher

That behavior matches the writable server terminology already retained in
[sv_game.c](../../src/code/server/sv_game.c).

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4E2620` (`0x004E2620`) | `SV_SubmitMatchReport` | Observed | Calls `SteamStats_BroadcastSummary` and then publishes the same JSON-like report through the ZMQ report path. |
| `sub_4E2640` (`0x004E2640`) | `SV_ReportPlayerEvent` | Observed | Calls `SteamStats_ProcessEvent` and then forwards the event into the ZMQ event-publication path. |

This closes the remaining Round 04 note cleanly: these are not generic
container helpers, they are the server-side host exports for match-report and
player-event publication.

## `idZMQ` Match-Report / Event Publisher Layer

The internal publisher pair directly under those wrappers now has enough
ownership evidence to name.

The signals are compact and strong:

- `sub_4F4C30` hardcodes `"MATCH_REPORT"` into the serialized object
- `sub_4F4B20` builds a JSON-like object with `"TYPE"` and `"DATA"` keys, then
  writes it through the retained socket at `this + 8`
- `sub_4F4E40` and `sub_4F4E10` are global wrappers that forward into the
  retained `data_5756fc` `idZMQ` instance

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F4B20` (`0x004F4B20`) | `idZMQ_ReportPlayerEvent` | Observed | Serializes a JSON-like object with `"TYPE"` and `"DATA"` fields and publishes it through the retained stats/report socket. |
| `sub_4F4C30` (`0x004F4C30`) | `idZMQ_SubmitMatchReport` | Observed | Serializes `{ "TYPE": "MATCH_REPORT", "DATA": ... }` and publishes it through the same retained socket. |
| `sub_4F4E10` (`0x004F4E10`) | `Zmq_ReportPlayerEvent` | Observed | Global wrapper that forwards the player-event publish call into the retained `idZMQ` instance at `data_5756fc`. |
| `sub_4F4E40` (`0x004F4E40`) | `Zmq_SubmitMatchReport` | Observed | Global wrapper that forwards match-report publication into the retained `idZMQ` instance at `data_5756fc`. |

Two practical takeaways from this seam:

- the ZMQ stats publisher is not just a socket bootstrap; it has a stable
  higher-level publication contract for match reports and typed player events
- the retail host keeps the Steam stats accumulation path and the ZMQ
  publication path adjacent but separate

## `idZMQ` RCON Runtime

The RCON side of the same object is also now stable enough to name.

The frame and logging callsites matter:

- `004CC906` calls `sub_4F4FD0()` once per main-frame iteration
- `004C9942` calls `sub_4F4E60(&var_1008)` from the normal console print path

The method bodies then anchor the semantics:

- `sub_4F4ED0` polls the retained RCON socket, receives peer identity and
  command frames, logs `zmq RCON client connected: %s\n` /
  `zmq RCON command from %s: %s\n`, tracks peers in the retained tree at
  `this + 0x14`, and executes inbound commands through `sub_4C7CF0`
- `sub_4F4D40` walks that same peer tree and writes console output back to the
  RCON socket, logging `zmq RCON client disconnected: %s\n` when a peer send
  fails and removing dead peers
- `sub_4F5080` writes `idZMQ::vftable`, clears the retained peer tree, and
  frees the object when requested, which is the expected retained destroy path

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F4D40` (`0x004F4D40`) | `idZMQ_BroadcastRconOutput` | Observed | Walks the retained RCON peer table, sends console output back to each peer, and removes peers whose send path fails. |
| `sub_4F4E60` (`0x004F4E60`) | `Zmq_BroadcastRconOutput` | Observed | Global wrapper used from the console print path to forward output into `idZMQ_BroadcastRconOutput`. |
| `sub_4F4ED0` (`0x004F4ED0`) | `idZMQ_PumpRcon` | Observed | Polls the retained RCON socket, records newly seen peers, logs inbound commands, and executes the received command text. |
| `sub_4F4FD0` (`0x004F4FD0`) | `Zmq_PumpRcon` | Observed | Global wrapper used from the main frame loop to pump the retained `idZMQ` RCON runtime once per frame. |
| `sub_4F5080` (`0x004F5080`) | `idZMQ_Destroy` | Observed | `idZMQ` destructor path; writes the class vftable, clears the retained peer tree, releases the sentinel node, and optionally deletes the object itself. |

This gives the retained object a clean behavioral split:

- stats/report publication via the socket at `this + 8`
- RCON command pump and console-output broadcast via the socket at `this + 0xc`
- peer tracking in the red-black tree rooted at `this + 0x14`

## New High-Confidence Aliases Added This Round

- engine-facing wrappers:
  - `sub_4E2620`
  - `sub_4E2640`
- `idZMQ` publication path:
  - `sub_4F4B20`
  - `sub_4F4C30`
  - `sub_4F4E10`
  - `sub_4F4E40`
- `idZMQ` RCON runtime:
  - `sub_4F4D40`
  - `sub_4F4E60`
  - `sub_4F4ED0`
  - `sub_4F4FD0`
  - `sub_4F5080`

## Open Questions

1. The peer-table helpers at `sub_4F4910`, `sub_4F49C0`, `sub_4F4E80`, and
   `sub_4F4FE0` are now clearly `idZMQ` ownership helpers, but they are still
   mostly STL/tree mechanics rather than stable subsystem-level behaviors.
2. `sub_4F2590` remains the main browser-runtime helper that still needs one
   more pass before promotion.
3. The `sub_4F3DD0` / `sub_4F3DF0` shutdown split still needs one more
   ownership pass to distinguish socket teardown from actor/context teardown.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `963` raw alias entries, `962` address-backed alias
  entries

## Completion Stats After Round 95

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `963` raw alias entries, `962` address-backed
  aliases
- Address-backed coverage: `17.577%` of `5473` functions
- Alias delta this round: `11`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It resolves a previously deferred wrapper seam
and expands the documented `idZMQ` ownership surface, but it does not change
the writable-source parity estimate by itself.
