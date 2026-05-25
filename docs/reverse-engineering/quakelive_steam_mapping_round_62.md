# Quake Live Steam Host Mapping Round 62

## Scope

This round closes the next large retained Quake III server tranche after the
botlib seam from round 61:

- the retained `server/sv_ccmds.c` operator-command block
- the retained early `server/sv_client.c` connect, client-command, and
  usermove path
- the retained `server/sv_game.c` entity-accessor and brush-model helpers

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/server/sv_ccmds.c`
- `src/code/server/sv_client.c`
- `src/code/server/sv_game.c`
- `assets/quake3/src/code/server/sv_ccmds.c`
- `assets/quake3/src/code/server/sv_client.c`
- `assets/quake3/src/code/server/sv_game.c`

## Retained `sv_ccmds.c` Operator-Command Closures

The operator-command seam maps cleanly from the already-identified
`SV_AddOperatorCommands` registration table:

- `sub_4DDB20 -> SV_GetPlayerByName`
- `sub_4DDC20 -> SV_GetPlayerByNum`
- `sub_4DDCE0 -> SV_Map_f`
- `sub_4DE670 -> SV_MapRestart_f`
- `sub_4DEA40 -> SV_Kick_f`
- `sub_4DEBE0 -> SV_KickNum_f`
- `sub_4DEC60 -> SV_Status_f`
- `sub_4DEEA0 -> SV_ConSay_f`
- `sub_4DEF40 -> SV_Serverinfo_f`
- `sub_4DEFA0 -> SV_DumpUser_f`
- `sub_4DF000 -> SV_KillServer_f`

Observed facts:

1. `sub_4DDB20` and `sub_4DDC20` preserve the exact retained validation and
   fatal strings from Quake III, including `No player specified.\n`,
   `Bad slot number: %s\n`, `Bad client slot: %i\n`, and
   `Player %s is not on the server\n`.
2. `sub_4DDCE0` preserves the retained `SV_Map_f` ownership: it expands the
   requested BSP path, prints `Can't find map %s\n` on failure, handles the
   `devmap` cheat path, and ultimately restarts the server on the selected map.
   The Quake Live host adds factory-aware behavior around the same retained
   core ownership.
3. `sub_4DE670` matches the retained `SV_MapRestart_f` control flow directly,
   including `Server is not running.\n`, `variable change -- restarting.\n`,
   warmup delay handling, and the in-place game restart path.
4. `sub_4DEA40`, `sub_4DEBE0`, `sub_4DEC60`, `sub_4DEEA0`, `sub_4DEF40`,
   `sub_4DEFA0`, and `sub_4DF000` all preserve the retained operator command
   strings and side effects from Quake III, including the formatted status
   table, console chat relay, userinfo dump, and `killserver` shutdown path.

## Retained Early `sv_client.c` Closures

The adjacent early client-management block also maps cleanly against Quake III:

- `sub_4DF270 -> SV_UserinfoChanged`
- `sub_4DF430 -> SV_GetChallenge`
- `sub_4DF660 -> SV_DropClient`
- `sub_4DF850 -> SV_SendClientGameState`
- `sub_4DFA20 -> SV_ClientEnterWorld`
- `sub_4DFAC0 -> SV_DoneDownload_f`
- `sub_4DFAF0 -> SV_Disconnect_f`
- `sub_4DFB10 -> SV_VerifyPaks_f`
- `sub_4DFEC0 -> SV_ResetPureClient_f`
- `sub_4DFEE0 -> SV_UpdateUserinfo_f`
- `sub_4E0090 -> SV_ExecuteClientCommand`
- `sub_4E0180 -> SV_ClientCommand`
- `sub_4E02D0 -> SV_ClientThink`
- `sub_4E0320 -> SV_UserMove`
- `sub_4E05C0 -> SV_ExecuteClientMessage`
- `sub_4E0750 -> SV_DirectConnect`

Observed facts:

1. `sub_4DF270` preserves the retained `SV_UserinfoChanged` role, including
   `name`, `rate`, `handicap`, `snaps`, and `ip` reconciliation exactly where
   the stock source expects them.
2. `sub_4DF430` retains the `SV_GetChallenge` ownership: it scans the
   challenge table, allocates a new challenge when needed, and returns
   `challengeResponse %i`. The Quake Live host adds a Steam-auth-token copy to
   the challenge record, but the owning function role remains the same.
3. `sub_4DF660`, `sub_4DF850`, and `sub_4DFA20` preserve the core retained
   client lifecycle with the exact strings
   `Going to CS_ZOMBIE for %s\n`,
   `SV_SendClientGameState() for %s\n`,
   `Going from CS_CONNECTED to CS_PRIMED for %s\n`, and
   `Going from CS_PRIMED to CS_ACTIVE for %s\n`.
4. `sub_4DFB10` is the retained pure-validation owner from Quake III
   `SV_VerifyPaks_f`, with the expected outdated-checksum-feed guard, the
   duplicate-checksum rejection path, and the final
   `Unpure client detected. Invalid .PK3 files referenced!` drop path. Quake
   Live changes the first checksum owner from `cgame.qvm` / `ui.qvm` to the
   host binary pack, but the function ownership is unchanged.
5. `sub_4E0090`, `sub_4E0180`, `sub_4E0320`, and `sub_4E05C0` preserve the
   retained command and movement path with the exact strings
   `client text ignored for %s: %s\n`,
   `clientCommand: %s : %i : %s\n`,
   `Lost reliable commands`,
   `cmdCount < 1\n`,
   `cmdCount > MAX_PACKET_USERCMDS\n`, and
   `WARNING: bad command byte for client %i\n`.
6. The 2026-05-25 usercmd movement-transport re-audit keeps the retained
   `SV_UserMove` / `SV_ClientThink` lane pinned beyond strings: server-side
   source now pins the same command replay shape recovered in HLIL, including
   delta-message selection, checksum-feed/user-command hash keys,
   `MSG_ReadDeltaUsercmdKey`, pure-client gates, first-command
   `SV_ClientEnterWorld`, stale-command suppression, `lastUsercmd`, and
   `GAME_CLIENT_THINK` dispatch into qagame.
7. `sub_4E0750` is the retained `SV_DirectConnect` owner: it parses the
   `connect` userinfo blob, validates protocol and challenge state, searches
   for reconnect or free client slots, and sends `connectResponse` on success.
   The Quake Live host adds VAC / Steam-oriented policy checks around the same
   retained connection-management spine.

## Retained `sv_game.c` Helper Closures

The next helper block also matches the retained server/game bridge directly:

- `sub_4E10B0 -> SV_GentityNum`
- `sub_4E10D0 -> SV_GameClientNum`
- `sub_4E10F0 -> SV_SvEntityForGentity`
- `sub_4E1130 -> SV_GEntityForSvEntity`
- `sub_4E1160 -> SV_SetBrushModel`
- `sub_4E12C0 -> SV_inPVSIgnorePortals`

Observed facts:

1. `sub_4E10B0` and `sub_4E10D0` are the retained pointer-arithmetic helpers
   over `sv.gentities` and `sv.gameClients`.
2. `sub_4E10F0` preserves the retained fatal guard
   `SV_SvEntityForGentity: bad gEnt`.
3. `sub_4E1160` matches `SV_SetBrushModel` exactly, including the fatal strings
   `SV_SetBrushModel: NULL` and
   `SV_SetBrushModel: %s isn't a brush model`, then the retained inline-model
   bounds setup and final entity relink.
4. `sub_4E12C0` is the retained `SV_inPVSIgnorePortals` variant because it
   performs the cluster/PVS test but omits the area-connectivity rejection that
   remains present in the already-mapped `SV_inPVS`.

## Completion Summary

This round promotes `33` retained aliases:

- `sv_ccmds.c`: `SV_GetPlayerByName`, `SV_GetPlayerByNum`, `SV_Map_f`,
  `SV_MapRestart_f`, `SV_Kick_f`, `SV_KickNum_f`, `SV_Status_f`,
  `SV_ConSay_f`, `SV_Serverinfo_f`, `SV_DumpUser_f`, `SV_KillServer_f`
- `sv_client.c`: `SV_UserinfoChanged`, `SV_GetChallenge`, `SV_DropClient`,
  `SV_SendClientGameState`, `SV_ClientEnterWorld`, `SV_DoneDownload_f`,
  `SV_Disconnect_f`, `SV_VerifyPaks_f`, `SV_ResetPureClient_f`,
  `SV_UpdateUserinfo_f`, `SV_ExecuteClientCommand`, `SV_ClientCommand`,
  `SV_ClientThink`, `SV_UserMove`, `SV_ExecuteClientMessage`,
  `SV_DirectConnect`
- `sv_game.c`: `SV_GentityNum`, `SV_GameClientNum`,
  `SV_SvEntityForGentity`, `SV_GEntityForSvEntity`, `SV_SetBrushModel`,
  `SV_inPVSIgnorePortals`

Focused band results after this pass:

- retained `sv_ccmds` core `0x4DDB20-0x4DF010`: raw gaps `8 -> 2`, true gaps
  `7 -> 1`
- retained `sv_client` lifecycle `0x4DF270-0x4DFB20`: `9 -> 1`
- retained `sv_client` command/message core `0x4DFEC0-0x4E05D0`: `9 -> 2`
- retained `sv_game` helper block `0x4E10B0-0x4E12D0`: `6 -> 0`
- broad retained server tranche `0x4DDB20-0x4E12D0`: raw gaps `38 -> 5`

Extra HLIL-only promotions not present as standalone `functions.csv` starts:

- `0x004DEA40 -> SV_Kick_f`
- `0x004DEBE0 -> SV_KickNum_f`
- `0x004DEF40 -> SV_Serverinfo_f`
- `0x004DEFA0 -> SV_DumpUser_f`
- `0x004DF000 -> SV_KillServer_f`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `828 -> 861`
- address-backed aliases: `827 -> 860`
- Ghidra function coverage: `15.111% -> 15.714%` of `5473`

The remaining raw starts in this broader retained tranche are:

- `0x004DDB62` (Ghidra split inside `SV_GetPlayerByName`)
- `0x004DE050`
- `0x004DF830`
- `0x004DFF30`
- `0x004DFF80`

The first of those is not a true standalone retained function. The others sit
in Quake Live-specific arena-command or small helper/wrapper code around the
challenge/admin seam rather than in the retained Quake III ownership already
closed here.
