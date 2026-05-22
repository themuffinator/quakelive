# Quake Live Steam Host Mapping Round 73

## Scope

This round closes the next bounded Steam game-server bootstrap seam that was
still missing in writable source after the earlier frame/public-IP pass:

- the direct `SteamGameServer()->GetSteamID` wrapper from round 04
- the spawn-time Steam game-server identity publication path
- the spawn/shutdown heartbeat enable/disable ownership in `sv_init.c`

The evidence base for this pass stayed inside the committed corpus:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_04.md`
- `src/code/server/sv_init.c`
- `src/common/platform/platform_steamworks.c`

## `sub_465DF0`: `SteamServer_GetSteamID`

Round 04 already bounded `00465DF0` as the direct Steam game-server identity
wrapper:

1. It checks the shared server-init gate.
2. It calls `SteamGameServer()->vtable[0x28 / 4]`.
3. It returns the resulting `CSteamID` pair through split low/high words.

The writable source now reconstructs that wrapper directly as
`QL_Steamworks_ServerGetSteamID( outIdLow, outIdHigh )` in
`src/common/platform/platform_steamworks.c`, pinned to
`vtable[0x28 / 4]`.

## `sub_465B00`: `SteamServer_PublishSteamID`

The HLIL for `00465B00` is stable enough to close as a writable host helper:

1. It calls the mapped game-server SteamID wrapper.
2. It formats the identity as an unsigned decimal string.
3. It publishes that value into configstrings `0x2CA` and `0x2CB`.
4. It mirrors the same value into the `sv_referencedSteamworks` cvar.

The writable source now reconstructs this path in `src/code/server/sv_init.c`
as `SV_SteamServerPublishIdentity()`. The round also restores the retail cvar
registration in `SV_Init()`:

- `Cvar_Get( "sv_referencedSteamworks", "", CVAR_ROM )`

This keeps the reconstruction bounded to the exact server-owned publication path
visible in the retail host rather than inventing new configstring names or a
broader Steam server metadata layer.

## `sub_465DB0`: Spawn / Shutdown Heartbeat Ownership

Round 72 already reconstructed the direct `SteamServer_EnableHeartbeats`
platform wrapper. The remaining missing source ownership was where the retail
host actually uses it:

1. `SV_SpawnServer` publishes the server SteamID.
2. It enables heartbeats using the current `sv_master` state.
3. `SV_Shutdown` later disables heartbeats with `0`.

The retail executable uses a single `sv_master` cvar. The writable source now
registers that retained cvar as `sv_masterAdvertise` and lets
`SV_SteamServerHasConfiguredMasters()` use it as the primary heartbeat gate.
The older Quake III multi-master array remains only as a compatibility lane for
explicitly configured legacy targets.

The writable source now mirrors the retail ownership shape in `sv_init.c`:

- `SV_SpawnServer()` calls `SV_SteamServerPublishIdentity()`
- `SV_SpawnServer()` then calls
  `QL_Steamworks_ServerEnableHeartbeats( SV_SteamServerHasConfiguredMasters() )`
- `SV_Shutdown()` calls `QL_Steamworks_ServerEnableHeartbeats( qfalse )`

2026-05-22 follow-up: the Quake III hostname endpoints
`update.quake3arena.com`, `master.quake3arena.com`, and
`authorize.quake3arena.com` are now isolated behind
`QL_ENABLE_LEGACY_Q3_SERVICES`, which is forced off whenever
`QL_BUILD_ONLINE_SERVICES=0`. Default builds keep `PORT_SERVER == 27960` and
the LAN scan range, but they no longer resolve the retired Q3 update, master,
or authorize servers.

## Verification

The updated source is covered by:

- `tests/test_steamworks_harness.py`
- `tests/test_platform_services.py`
- `tests/test_ui_menu_files.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `64 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped
`quakelive_steam.exe` ownership in three ways:

- the shared Steamworks layer now includes a writable
  `ServerGetSteamID` wrapper at the mapped `SteamGameServer` slot
- the retained server bootstrap now republishes the game-server SteamID into
  the retail configstring/cvar seam
- the retained server spawn/shutdown path now owns the mapped Steam heartbeat
  enable/disable transitions instead of leaving them as uncalled wrappers
