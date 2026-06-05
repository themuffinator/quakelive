# Network Protocol Parity Ledger - 2026-06-05

## Scope

This note is the human-readable companion for
`docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json`.
It closes the first implementation-plan entry in
`docs/plans/2026-06-05-networking-2.md`: build a source-of-truth ledger that
maps each networking focus area to writable source, retail function addresses,
packet offsets, struct offsets, field counts, confidence, and follow-up gaps.

No runtime launch was required. This pass used static source inspection plus
the committed retail evidence corpus.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`

Writable source inspected:

- `src/code/qcommon/qcommon.h`
- `src/code/qcommon/common.c`
- `src/code/qcommon/msg.c`
- `src/code/qcommon/net_chan.c`
- `src/code/client/cl_input.c`
- `src/code/client/cl_net_chan.c`
- `src/code/client/cl_main.c`
- `src/code/client/cl_parse.c`
- `src/code/server/sv_client.c`
- `src/code/server/sv_main.c`
- `src/code/server/sv_net_chan.c`
- `src/code/server/sv_snapshot.c`
- `src/code/game/q_shared.h`

## Ledger Summary

The JSON ledger now covers these focus areas:

| Focus area | Status | Main retail anchors | Main source anchors |
| --- | --- | --- | --- |
| Protocol gates and packet headers | Mapped | `CL_WritePacket` `0x004B5F70`, `SV_ExecuteClientMessage` `0x004E05C0` | `qcommon.h`, `common.c`, `cl_input.c`, `sv_client.c` |
| Netchan transport | Mapped | `Netchan_TransmitNextFragment` `0x004D7370`, `Netchan_Transmit` `0x004D74E0`, `Netchan_Process` `0x004D7640` | `net_chan.c`, `qcommon.h` |
| XOR netchan encoding | Mapped | `CL_Netchan_Encode` `0x004BCE30`, `CL_Netchan_Decode` `0x004BCEF0`, `SV_Netchan_Encode` `0x004E4CD0`, `SV_Netchan_Decode` `0x004E4D70` | `cl_net_chan.c`, `sv_net_chan.c`, `qcommon.h` |
| `usercmd_t` deltas | Mapped | `MSG_WriteDeltaUsercmdKey` `0x004D51A0`, `MSG_ReadDeltaUsercmdKey` `0x004D54A0`, `SV_UserMove` `0x004E0320` | `q_shared.h`, `msg.c`, `cl_input.c`, `sv_client.c` |
| `playerStateFields` | Mapped | `MSG_WriteDeltaPlayerstate` `0x004D5D50`, `MSG_ReadDeltaPlayerstate` `0x004D66C0` | `q_shared.h`, `msg.c`, `sv_snapshot.c`, `cl_parse.c` |
| `entityStateFields` | Gap found | `MSG_WriteDeltaEntity` `0x004D5780`, `MSG_ReadDeltaEntity` `0x004D5AC0` | `q_shared.h`, `msg.c`, `sv_snapshot.c`, `cl_parse.c` |
| Client message parser | Mapped with external conflict | `CL_WritePacket` `0x004B5F70`, `SV_ExecuteClientMessage` `0x004E05C0` | `cl_input.c`, `sv_client.c`, `qcommon.h` |
| OOB/connect/auth | Completed by OOB matrix | `MSG_WriteBits` `0x004D4AF0`, `MSG_ReadBits` `0x004D4C70`, `MSG_InitOOB` `0x004D6C50`, `NET_OutOfBandPrint` `0x004D7080`, `NET_OutOfBandData` `0x004D7120` | `msg.c`, `net_chan.c`, `cl_main.c`, `sv_main.c`, `sv_client.c` |

## Observed Facts

Protocol and packet headers:

- The active source protocol is `QL_RETAIL_PROTOCOL_VERSION == 91`.
- The source profile gates client qport, netchan qport, reliable XOR, and
  compressed connect behavior through protocol helpers.
- `CL_WritePacket` writes the client message body as `serverId`,
  `serverMessageSequence`, `serverCommandSequence`, one retail sideband byte,
  optional reliable client commands, then `clc_move` or `clc_moveNoDelta`.
- Retail `SV_ExecuteClientMessage` at `0x004E05C0` reads three leading
  packet-body longs, consumes one unassigned byte, and then starts byte-opcode
  parsing. The parser grammar pass corrected the earlier local conclusion that
  no extra byte was present.

Transport and XOR:

- The classic netchan sequence/qport/fragment shape is address-mapped through
  the retail `0x004D7370` to `0x004D7640` band.
- Client-to-server XOR starts at byte `12` of the message body and uses
  `challenge ^ serverId ^ messageAcknowledge` plus the acknowledged server
  command string.
- Server-to-client XOR starts at byte `4` of the server message body and uses
  `challenge ^ outgoingSequence` plus `lastClientCommandString`.
- Both XOR paths sanitize percent and high-bit command-string bytes to `'.'`
  before key folding.

Struct and field tables:

- Retail `usercmd_t` HLIL confirms the Quake Live tail fields at offsets
  `0x15` and `0x16`, matching `weaponPrimary` and `fov`.
- Retail `playerStateFields` loops over `0x3a` entries, and the source table
  currently has `58` entries. Key fields include `pm_flags` at `24` bits,
  `weaponPrimary` at `8` bits, `location` at `8` bits, `fov` at `8` bits, and
  signed movement mirrors serialized as byte payloads.
- Superseded by the entitystate pass: retail `entityStateFields` also loops
  over `0x3a` entries, and the current source table now has `58` entries
  reconstructed from the raw `0x00542220` table.
- Retail `MSG_ReadDeltaEntity` copies an entity state size of `0xEC`, matching
  the recovered extended `entityState_t` storage band.

OOB behavior:

- `MSG_InitOOB` and OOB scalar read/write paths remain raw byte-oriented
  message primitives, not adaptive-Huffman bitstream primitives.
- Compressed connect is now confirmed as the narrow profile-91 OOB Huffman
  exception: retail and source keep `connect ` clear through offset `11` and
  compress/decompress from offset `12`.
- Steam-era `getchallenge` auth payloads use a raw binary OOB send path. Live
  auth behavior stays subject to the repository policy: keep it behind
  `QL_BUILD_ONLINE_SERVICES`, default disabled.

## New Gaps And Conflicts

`NET2-G01`: entity field-count mismatch - resolved by the entitystate pass

- Observed retail evidence: entity delta HLIL uses `0x3a` as the field-table
  count in both write and read paths.
- Resolved source state: `entityStateFields[]` now has `58` entries and ends
  at `{ NETF(location), 8 }`.
- The raw retail table added `pos.gravity`, `apos.gravity`, `jumpTime`,
  `doubleJumped`, `health`, `armor`, and `location`; the former source-only
  terminal `retailEventData` row is retained as a source alias of the retail
  `generic1` storage slot instead of as a separate network field.

`NET2-Q01`: retail client-message sideband byte confirmed

- External claim imported by the June 5 plan: retail server parsing needs an
  extra byte after the three client-message header longs.
- Observed committed evidence: retail `SV_ExecuteClientMessage` at
  `0x004E05C0` reads the three longs, consumes one unassigned byte, then reads
  byte opcodes. Retail `CL_WritePacket` at `0x004B5F70` writes the matching
  byte as `sub_4AF4D0() ^ serverCommandSequence`.
- Required next step: recover the sideband flag producers behind
  `sub_4AF4D0` / `data_565948`; the parser-compatible source stub writes zero
  flag bits until that cgame/native-state pass is complete.

## Parity Estimate

Focused networking-ledger task:

- Before: **0%** for the new networking-2 source-of-truth ledger.
- After: **100%** for the ledger deliverable itself, with follow-up
  implementation gaps explicitly carried forward.

Strict gameplay wire behavior was not changed by the original ledger pass.
Repo-wide parity remains **98%**. Later June 5 passes have since closed the
playerstate table, entitystate table, parser-sideband, XOR, usercmd, and
OOB/connect-auth evidence gaps tracked by this ledger while leaving capture
replay and live-service policy work as separate follow-ups.
