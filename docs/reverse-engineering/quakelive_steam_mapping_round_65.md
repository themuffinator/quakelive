# Quake Live Steam Host Mapping Round 65

## Scope

This round closes the next retained Quake III server-owned tranche after
round 64:

- the retained `server/sv_main.c` server-command, connectionless, and frame
  owners
- the retained `server/sv_net_chan.c` encode/decode and transmit helpers
- the retained `server/sv_snapshot.c` snapshot build/send pipeline
- the retained `server/sv_world.c` world-sector and link/unlink owners

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/server/sv_main.c`
- `src/code/server/sv_net_chan.c`
- `src/code/server/sv_snapshot.c`
- `src/code/server/sv_world.c`
- `assets/quake3/src/code/server/sv_main.c`
- `assets/quake3/src/code/server/sv_net_chan.c`
- `assets/quake3/src/code/server/sv_snapshot.c`
- `assets/quake3/src/code/server/sv_world.c`

## Retained `sv_main.c` / `sv_net_chan.c` Closures

The next server-control tranche still follows the stock Quake III ownership:

- `sub_4E4060 -> SV_ExpandNewlines`
- `sub_4E40C0 -> SV_AddServerCommand`
- `sub_4E4170 -> SV_SendServerCommand`
- `sub_4E4340 -> SV_ConnectionlessPacket`
- `sub_4E4500 -> SV_PacketEvent`
- `sub_4E46B0 -> SV_CalcPings`
- `sub_4E47E0 -> SV_CheckTimeouts`
- `sub_4E4950 -> SV_CheckPaused`
- `sub_4E49D0 -> SV_Frame`
- `sub_4E4CD0 -> SV_Netchan_Encode`
- `sub_4E4D70 -> SV_Netchan_Decode`
- `sub_4E4E20 -> SV_Netchan_TransmitNextFragment`
- `sub_4E4EE0 -> SV_Netchan_Transmit`
- `sub_4E4F80 -> SV_Netchan_Process`

Observed facts:

1. `sub_4E4060` rewrites embedded newlines into the same static escape buffer
   pattern as retained `SV_ExpandNewlines`.
2. `sub_4E40C0` preserves the reliable-sequence increment, the
   `Server command overflow` drop, and the retained
   `===== pending server commands =====` debug dump from `SV_AddServerCommand`.
3. `sub_4E4170` still formats with `Q_vsnprintf`, echoes `broadcast: %s` on
   dedicated servers, and fans out through `SV_AddServerCommand`, which is the
   retained `SV_SendServerCommand` flow.
4. `sub_4E4340` keeps the retained `MSG_BeginReadingOOB` /
   `Huff_Decompress(msg, 12)` / `Cmd_TokenizeString` connectionless dispatch
   with the canonical `getchallenge` and `connect` handling.
5. `sub_4E4500` preserves the translated-port fixup string and the retained
   `SV_Netchan_Process` -> `SV_ExecuteClientMessage` packet path.
6. `sub_4E46B0`, `sub_4E47E0`, `sub_4E4950`, and `sub_4E49D0` retain the stock
   ping averaging, timeout checks, pause gate, and full `SV_Frame` server tick
   sequence.
7. `sub_4E4CD0` and `sub_4E4D70` match the retained
   `SV_Netchan_Encode` / `SV_Netchan_Decode` byte-XOR logic over the client
   command strings, challenge, sequence, serverId, and message-ack fields.
8. `sub_4E4E20`, `sub_4E4EE0`, and `sub_4E4F80` preserve the retained queued
   fragment transmit path and the final `SV_Netchan_Decode` wrapper.

## Retained `sv_snapshot.c` Snapshot Pipeline Closures

The adjacent snapshot tranche also closes directly from the Quake III source:

- `sub_4E4FC0 -> SV_EmitPacketEntities`
- `sub_4E50E0 -> SV_WriteSnapshotToClient`
- `sub_4E5240 -> SV_UpdateServerCommandsToClient`
- `sub_4E52C0 -> SV_QsortEntityNumbers`
- `sub_4E5300 -> SV_AddEntToSnapshot`
- `sub_4E5330 -> SV_AddEntitiesVisibleFromPoint`
- `sub_4E5680 -> SV_BuildClientSnapshot`
- `sub_4E5900 -> SV_SendMessageToClient`
- `sub_4E5AC0 -> SV_SendClientSnapshot`
- `sub_4E5B90 -> SV_SendClientMessages`

Observed facts:

1. `sub_4E4FC0` is the retained old/new entity merge loop ending with the
   `MAX_GENTITIES - 1` sentinel write from `SV_EmitPacketEntities`.
2. `sub_4E50E0` still writes `svc_snapshot`, server time, delta-frame metadata,
   areabits, playerstate, and packet entities in the retained order.
3. `sub_4E5240` emits pending reliable commands as `svc_serverCommand`, which
   matches retained `SV_UpdateServerCommandsToClient`.
4. `sub_4E52C0` preserves the retained duplicate-entity fatal string from
   `SV_QsortEntityNumbers`.
5. `sub_4E5300`, `sub_4E5330`, and `sub_4E5680` still implement the retained
   snapshot-counter guard, PVS/portal visibility walk, areabits inversion, and
   `svs.nextSnapshotEntities wrapped` check from the stock snapshot build path.
6. `sub_4E5900`, `sub_4E5AC0`, and `sub_4E5B90` preserve the retained rate
   control, snapshot emit, fragment-drain, and per-client send loop.
7. The 2026-05-25 snapshot playerState transport re-audit keeps the source
   bridge pinned across the same path. `SV_BuildClientSnapshot` copies the live
   `SV_GameClientNum` playerState into `frame->ps`, suppresses the client's own
   entity because cgame regenerates it from playerState, derives the viewpoint
   from `ps->origin + viewheight`, and gathers snapshot entities before
   `SV_WriteSnapshotToClient` writes the area mask, `MSG_WriteDeltaPlayerstate`,
   and `SV_EmitPacketEntities` in retail order.

## Retained `sv_world.c` World-Sector Closures

The next world-management owners are also retained Quake III code:

- `sub_4E5C40 -> SV_ClipHandleForEntity`
- `sub_4E5D20 -> SV_SectorList_f`
- `sub_4E5D60 -> SV_CreateworldSector`
- `sub_4E5E80 -> SV_ClearWorld`
- `sub_4E5EE0 -> SV_UnlinkEntity`
- `sub_4E5F50 -> SV_LinkEntity`

Observed facts:

1. `sub_4E5C40` keeps the retained `CM_InlineModel` vs `CM_TempBoxModel`
   decision tree, including the `SVF_CAPSULE` branch from
   `SV_ClipHandleForEntity`.
2. `sub_4E5D20` preserves the exact retained `sector %i: %i entities` console
   print from `SV_SectorList_f`.
3. `sub_4E5D60` and `sub_4E5E80` retain the world-sector recursion, split-axis
   selection, world-bounds query, and sector reset sequence from
   `SV_CreateworldSector` and `SV_ClearWorld`.
4. `sub_4E5EE0` keeps the retained unlink warning
   `SV_UnlinkEntity: not found in worldSector`.
5. `sub_4E5F50` preserves the stock solid encoding, area/cluster discovery,
   `CM_BoxLeafnums` path, and final node insertion from `SV_LinkEntity`.
6. `0x004E5CB0` is a second compiler-emitted clone of the retained
   `SV_ClipHandleForEntity` body rather than a new logical server owner, so it
   remains only as a raw `functions.csv` start and not as a separate promoted
   alias.

## Completion Summary

This round promotes `30` new aliases:

- retained `sv_main.c` owners: `SV_ExpandNewlines`, `SV_AddServerCommand`,
  `SV_SendServerCommand`, `SV_ConnectionlessPacket`, `SV_PacketEvent`,
  `SV_CalcPings`, `SV_CheckTimeouts`, `SV_CheckPaused`, `SV_Frame`
- retained `sv_net_chan.c` owners: `SV_Netchan_Encode`,
  `SV_Netchan_Decode`, `SV_Netchan_TransmitNextFragment`,
  `SV_Netchan_Transmit`, `SV_Netchan_Process`
- retained `sv_snapshot.c` owners: `SV_EmitPacketEntities`,
  `SV_WriteSnapshotToClient`, `SV_UpdateServerCommandsToClient`,
  `SV_QsortEntityNumbers`, `SV_AddEntToSnapshot`,
  `SV_AddEntitiesVisibleFromPoint`, `SV_BuildClientSnapshot`,
  `SV_SendMessageToClient`, `SV_SendClientSnapshot`,
  `SV_SendClientMessages`
- retained `sv_world.c` owners: `SV_ClipHandleForEntity`,
  `SV_SectorList_f`, `SV_CreateworldSector`, `SV_ClearWorld`,
  `SV_UnlinkEntity`, `SV_LinkEntity`

Focused band results after this pass:

- retained `sv_main.c` + `sv_net_chan.c` band `0x4E4060-0x4E4F80`: raw/true
  gaps `14 -> 0`
- retained `sv_snapshot.c` + `sv_world.c` band `0x4E4FC0-0x4E5F50`: raw gaps
  `16 -> 1`, true gaps `15 -> 0`
- combined retained server tranche `0x4E4060-0x4E5F50`: raw gaps `30 -> 1`,
  true gaps `29 -> 0`

Extra HLIL-only promotion not present as a standalone `functions.csv` start:

- `0x004E5D20 -> SV_SectorList_f`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `914 -> 944`
- address-backed aliases: `913 -> 943`
- Ghidra function coverage: `16.682% -> 17.230%` of `5473`

The only remaining raw `functions.csv` start inside the focused tranche is:

- `0x004E5CB0`

That start is the duplicate retained `SV_ClipHandleForEntity` clone noted
above, so this pass fully closes the next true retained Quake III server-owned
tranche.
