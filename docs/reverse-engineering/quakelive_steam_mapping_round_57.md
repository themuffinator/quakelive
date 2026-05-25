# Quake Live Steam Host Mapping Round 57

## Scope

This round continues the retained Quake III `qcommon` pass immediately after
the wrapper-layer closures from round 56:

- keyed `msg.c` usercmd delta helpers
- retained entity and playerstate delta serialization
- `MSG_initHuffman` plus the `MSG_Init*` entry points
- the early retained `net_chan.c` initialization, addressing, loopback, and
  fragmentation path

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/qcommon/msg.c`
- `src/code/qcommon/net_chan.c`
- `assets/quake3/src/code/qcommon/msg.c`
- `assets/quake3/src/code/qcommon/net_chan.c`

## Keyed Usercmd Delta Closures

The next retained `msg.c` block closes the keyed usercmd delta pair:

- `sub_4D51A0 -> MSG_WriteDeltaUsercmdKey`
- `sub_4D54A0 -> MSG_ReadDeltaUsercmdKey`

Observed facts:

1. `sub_4D51A0` preserves the Quake III compact `serverTime` encoding, writing
   an 8-bit delta when the new command time is within `256` and otherwise
   falling back to a full `32`-bit write.
2. The helper preserves the stock "no change" fast path, including the
   `oldsize += 7` accounting side effect before returning.
3. The body then XORs the key with `to->serverTime` and serializes the retained
   Quake III movement core plus the Quake Live command tail: `angles[3]`,
   `forwardmove`, `rightmove`, `upmove`, `buttons`, `weapon`,
   `weaponPrimary`, and `fov`.
4. `sub_4D54A0` mirrors the same layout on read, reconstructing either the
   copied-from baseline or the keyed deltas depending on the change bit.

## Delta Entity And Playerstate Closures

The following retained Quake III message-delta bodies are now source-aligned:

- `sub_4D5750 -> MSG_ReportChangeVectors_f`
- `sub_4D5780 -> MSG_WriteDeltaEntity`
- `sub_4D5AC0 -> MSG_ReadDeltaEntity`
- `sub_4D5D50 -> MSG_WriteDeltaPlayerstate`
- `sub_4D66C0 -> MSG_ReadDeltaPlayerstate`

Observed facts:

1. `sub_4D5750` is the exact debug command handler registered under
   `changeVectors`, iterating `pcount[256]` and printing `%d used %d\n`.
2. `sub_4D5780` preserves the stock `MSG_WriteDeltaEntity` ownership:
   validation against `MAX_GENTITIES`, `MSG_WriteDeltaEntity: Bad entity number`
   fatal, change-vector generation over the retained field table, and the same
   compact float packing with the `13`-bit integral-float path.
3. `sub_4D5AC0` mirrors the Quake III read path with the exact retained
   `Bad delta entity number: %i`, remove-entity handling, shownet print path,
   and the same float reconstruction rules.
4. `sub_4D5D50` and `sub_4D66C0` are the playerstate delta pair. Their field
   tables reflect Quake Live's expanded `playerState_t`, but the function roles
   and control flow remain the Quake III `MSG_WriteDeltaPlayerstate` and
   `MSG_ReadDeltaPlayerstate` implementations, including the `PS_STATS`,
   `PS_PERSISTANT`, `PS_AMMO`, and `PS_POWERUPS` array-mask sections.
5. The 2026-05-25 playerState delta-codec re-audit keeps that closure pinned
   in source: `msg.c::playerStateFields` preserves the Quake Live scalar order
   through the movement-critical command-time, origin/velocity/viewangle,
   jump/crouch, weapon-primary, location, fov, and command-axis mirror fields;
   the signed `forwardmove`, `rightmove`, and `upmove` tail fields are compared
   as signed bytes, serialized as byte payloads, and restored through the same
   scalar helper path; and the four array-mask sections now have executable
   round-trip coverage in `tests/test_playerstate_replication.py`.
6. The 2026-05-25 usercmd movement-transport re-audit keeps the keyed usercmd
   pair pinned against source and HLIL offsets. Quake Live extends the keyed
   usercmd tail with `weaponPrimary` and `fov`, so the focused guard now checks
   those two bytes alongside the signed movement axes in both the changed-field
   and copied-from-baseline read paths.

The `MSG_ReportChangeVectors_f` helper is an HLIL-backed closure rather than a
standalone `functions.csv` start, but its role is still unambiguous from the
command registration and loop body.

## Message Init And Huffman Bootstrap Closures

The tail of the retained `msg.c` tranche also closes:

- `sub_4D6BB0 -> MSG_initHuffman`
- `sub_4D6C10 -> MSG_Init`
- `sub_4D6C50 -> MSG_InitOOB`

Observed facts:

1. `sub_4D6BB0` sets the retained `msgInit` guard, calls `Huff_Init`, and then
   walks the `msg_hData` frequency table, feeding every symbol into both the
   compressor and decompressor trees with `Huff_addRef`.
2. `sub_4D6C10` and `sub_4D6C50` preserve the stock Quake III lazy-init
   behavior by calling `MSG_initHuffman` when needed, zeroing the `msg_t`,
   wiring `data` and `maxsize`, and setting `oob = qtrue` only in the OOB
   initializer.

## Early Netchan Closures

The next retained `net_chan.c` slice closes cleanly as Quake III networking
core:

- `sub_4D6C90 -> Netchan_Init`
- `sub_4D6D00 -> Netchan_Setup`
- `sub_4D6D60 -> NET_CompareBaseAdr`
- `sub_4D6DD0 -> NET_AdrToString`
- `sub_4D6EB0 -> NET_CompareAdr`
- `sub_4D6F30 -> NET_IsLocalAddress`
- `sub_4D6F40 -> NET_GetLoopPacket`
- `sub_4D6FD0 -> NET_SendPacket`
- `sub_4D7080 -> NET_OutOfBandPrint`
- `sub_4D7120 -> NET_OutOfBandData`
- `sub_4D7250 -> NET_StringToAdr`
- `sub_4D7370 -> Netchan_TransmitNextFragment`
- `sub_4D74E0 -> Netchan_Transmit`
- `sub_4D7640 -> Netchan_Process`

Observed facts:

1. `sub_4D6C90` initializes `showpackets`, `showdrop`, and `net_qport` exactly
   like `Netchan_Init`, including the masked `port &= 0xffff`.
2. `sub_4D6D60`, `sub_4D6DD0`, `sub_4D6EB0`, `sub_4D6F30`, and `sub_4D6F40`
   preserve the stock address helpers and loopback queue semantics, including
   the exact `NET_CompareBaseAdr: bad address type\n` and
   `NET_CompareAdr: bad address type\n` diagnostics.
3. `sub_4D6FD0`, `sub_4D7080`, and `sub_4D7120` preserve Quake III OOB packet
   handling, including the `-1` header setup and the loopback-vs-system send
   split.
4. `sub_4D7250` is the retained `NET_StringToAdr` path, preserving the
   `localhost` special case, optional `:<port>` split, and fallback to the
   default Quake port when no port suffix is supplied.
5. `sub_4D7370`, `sub_4D74E0`, and `sub_4D7640` preserve the fragmentation
   path, the exact `Netchan_Transmit: length = %i` fatal, and the stock
   out-of-order / dropped-fragment diagnostics used by Quake III
   `Netchan_Process`.

## Completion Summary

This round promotes `24` retained Quake III aliases:

- keyed usercmd deltas: `MSG_WriteDeltaUsercmdKey`,
  `MSG_ReadDeltaUsercmdKey`
- delta/message core: `MSG_ReportChangeVectors_f`, `MSG_WriteDeltaEntity`,
  `MSG_ReadDeltaEntity`, `MSG_WriteDeltaPlayerstate`,
  `MSG_ReadDeltaPlayerstate`, `MSG_initHuffman`, `MSG_Init`, `MSG_InitOOB`
- early netchan: `Netchan_Init`, `Netchan_Setup`, `NET_CompareBaseAdr`,
  `NET_AdrToString`, `NET_CompareAdr`, `NET_IsLocalAddress`,
  `NET_GetLoopPacket`, `NET_SendPacket`, `NET_OutOfBandPrint`,
  `NET_OutOfBandData`, `NET_StringToAdr`, `Netchan_TransmitNextFragment`,
  `Netchan_Transmit`, `Netchan_Process`

Focused band results after this pass:

- `0x4D51A0-0x4D6C90`: `9 -> 0` remaining standalone gaps
- `0x4D6C90-0x4D7650`: `14 -> 0`
- `0x4D51A0-0x4D7650`: `23 -> 0`
- transmit/process tail `0x4D74E0-0x4D7650`: `2 -> 0`
- extra HLIL-only helper closed outside standalone `functions.csv` starts:
  `0x004D5750 -> MSG_ReportChangeVectors_f`

The next nearby unresolved standalone starts begin at:

- `0x004D7970`
- `0x004D7980`
- `0x004D7990`
- `0x004D79C0`
- `0x004D79E0`

That adjacent band appears to transition out of `net_chan.c` and into a
math/helper cluster rather than continuing the retained message-networking
tranche mapped here.
