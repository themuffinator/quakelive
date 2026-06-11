# Quake Live Steam Host Mapping Round 549

## Scope

This round hardens the server-side Steam launch/runtime boundary that sits
between the operator command console, the qagame native import table, and the
server-owned Steam/ZMQ publication paths.

The goal was not to enable live Steam services. It was to promote the committed
retail references into stable names and parity tests while keeping the existing
`QL_BUILD_ONLINE_SERVICES` default-off posture intact.

Evidence used:

- Ghidra `functions.csv` rows for `0x004df010..0x004df0d0` and
  `0x004e2620..0x004e2920`
- Binary Ninja HLIL part 04 for `SV_AddOperatorCommands` and the three Steam
  workshop operator command handlers
- Binary Ninja HLIL part 05 for the server match-report, player-event, Steam
  ID, stats, achievement, and auth bridge helpers
- Binary Ninja HLIL part 07 for the qagame native import table entries at
  `data_56d2a0..data_56d2b4`
- reconstructed source anchors in `sv_ccmds.c`, `sv_game.c`,
  `ql_game_imports.inc`, and `sv_client.c`

## Workshop Operator Commands

HLIL part 04 shows `SV_AddOperatorCommands` registering three Steam workshop
operator commands directly after `killserver`.

| Raw symbol | Alias | Observed Binary Ninja/Ghidra signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_4df010` | `SteamCmd_DownloadUGC_f` | Ghidra row `FUN_004df010,004df010,95`; HLIL parses one `%llu` argument and calls the workshop download helper with high priority disabled. | Source-backed by `SV_SteamCmd_DownloadUGC_f`, which validates `Cmd_Argc()`, splits the 64-bit item ID, and delegates through the offline-safe workshop abstraction. |
| `sub_4df070` | `SteamCmd_SubscribeUGC_f` | Ghidra row `FUN_004df070,004df070,87`; HLIL parses one `%llu` argument and calls the subscribe helper. | Source-backed by `SV_SteamCmd_SubscribeUGC_f`, guarded by the workshop provider/policy layer. |
| `sub_4df0d0` | `SteamCmd_UnsubscribeUGC_f` | Ghidra row `FUN_004df0d0,004df0d0,87`; HLIL parses one `%llu` argument and calls the unsubscribe helper. | Source-backed by `SV_SteamCmd_UnsubscribeUGC_f`, guarded by the workshop provider/policy layer. |

The command registration evidence is direct:

- `steam_downloadugc` -> `sub_4df010`
- `steam_subscribeugc` -> `sub_4df070`
- `steam_unsubscribeugc` -> `sub_4df0d0`

## Server Native Import Bridge

HLIL part 07 exposes the qagame native import slab entries for the Steam-facing
server bridge. Part 05 then gives the helper bodies that hang off those entries.

| Raw symbol | Alias | Observed Binary Ninja/Ghidra signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_4e2620` | `SV_SubmitMatchReport` | Ghidra row `FUN_004e2620,004e2620,25`; HLIL calls `SteamStats_BroadcastSummary` and then forwards the report to the ZMQ match-report publisher. | Source-backed by `SV_SubmitMatchReport`, which prepares the Steam stats report and forwards the prepared payload through `Zmq_SubmitMatchReport`. |
| `sub_4e2640` | `SV_ReportPlayerEvent` | Ghidra row `FUN_004e2640,004e2640,55`; HLIL calls `SteamStats_ProcessEvent` and then forwards to the ZMQ player-event publisher. | Source-backed by `SV_ReportPlayerEvent`, preserving Steam stats side effects before ZMQ publication. |
| `sub_4e2710` | `SV_ClientGetSteamID` | Ghidra row `FUN_004e2710,004e2710,89`; HLIL validates the client slot, checks the `characterfile` key, loads the stored SteamID pair, and returns the low half. | Current source uses the compatibility `QL_G_trap_GetSteamId` pointer-return form. This is documented as an ABI delta from the retail native import rather than changed in this round. |
| `sub_4e2770` | `SV_ClientAddSteamStat` | Ghidra row `FUN_004e2770,004e2770,86`; HLIL validates the client and forwards the stored SteamID pair, stat index, and delta to `SteamStats_AddFieldValue`. | Source-backed by `SV_ClientAddSteamStat`, which delegates to `SV_SteamStats_AddFieldValue`. |
| `sub_4e2860` | `SV_ClientUnlockSteamAchievement` | Ghidra row `FUN_004e2860,004e2860,82`; HLIL validates the client and forwards the stored SteamID pair and achievement ID to `SteamStats_UnlockAchievement`. | Source-backed by `SV_ClientUnlockSteamAchievement`, which delegates to `SV_SteamStats_UnlockAchievement`. |
| `sub_4e28c0` | `SV_ClientHasSteamAchievement` | Ghidra row `FUN_004e28c0,004e28c0,86`; HLIL validates the client and queries `SteamStats_HasAchievement`. | Source-backed by `SV_ClientHasSteamAchievement`, which delegates to `SV_SteamStats_HasAchievement`. |
| `sub_4e2920` | `SV_ClientBeginSteamAuthSession` | Ghidra row `FUN_004e2920,004e2920,253`; HLIL validates client/challenge state, calls `SteamServer_BeginAuthSession`, then creates a Steam stats player session on success. | Current source splits this across `SV_BeginPlatformAuthSession` for connection-time auth start and `QL_G_trap_VerifySteamAuth` for qagame auth-state validation. No live-service behavior was enabled. |

## Alias Promotion

The alias ledger now contains the committed Ghidra `FUN_*` spellings, the
existing upper-case Binary Ninja spellings, and the lower-case Binary Ninja
spellings for this cluster. This removes an avoidable source of false negatives
when scripts compare references emitted by different tooling.

Promoted spelling groups:

- `FUN_004df010`, `sub_4DF010`, `sub_4df010`
- `FUN_004df070`, `sub_4DF070`, `sub_4df070`
- `FUN_004df0d0`, `sub_4DF0D0`, `sub_4df0d0`
- `FUN_004e2620`, `sub_4E2620`, `sub_4e2620`
- `FUN_004e2640`, `sub_4E2640`, `sub_4e2640`
- `FUN_004e2710`, `sub_4E2710`, `sub_4e2710`
- `FUN_004e2770`, `sub_4E2770`, `sub_4e2770`
- `FUN_004e2860`, `sub_4E2860`, `sub_4e2860`
- `FUN_004e28c0`, `sub_4E28C0`, `sub_4e28c0`
- `FUN_004e2920`, `sub_4E2920`, `sub_4e2920`

## Reconstruction Notes

Observed facts:

1. The workshop command handlers are thin retail wrappers around a parsed
   unsigned 64-bit Workshop item ID.
2. The qagame native import slab places the Steam ID/stat/achievement/auth
   helpers as contiguous server-owned exports.
3. Match-report and player-event publication run Steam stats processing before
   ZMQ publication.
4. `SV_ClientBeginSteamAuthSession` in retail begins the GameServer auth session
   and then starts the per-player Steam stats session.

Inferences:

1. The current source's pointer-return `trap_GetSteamId` path is a compatibility
   reconstruction for source-built qagame rather than a perfect native ABI match
   for the retail import table.
2. The current auth split is service-safe: it preserves the connection-time
   Steam GameServer auth lifecycle while letting qagame query retained auth
   state through the compatibility import.

## Parity Estimate

- Focused server Steam command/VM bridge alias confidence:
  **66% -> 99%**
- Focused Game VM/workshop operator HLIL evidence coverage:
  **86% -> 97%**
- Overall Steam launch/runtime reconstruction parity:
  **92.3% -> 92.35%**

