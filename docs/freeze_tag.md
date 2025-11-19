# Freeze Tag Gameplay Notes

Freeze Tag extends the round controller and client lifecycle so that deaths immobilize players until a teammate thaws them. The following cvars control the cadence that the new flow follows.

## Freeze configuration cache

The freeze controller snapshots every `g_freeze*` CVar into `level.freezeConfig` whenever the round state changes. `G_FreezeSyncCvars` copies the sanitized values during initialization and before warmup/active transitions so modules such as `g_team.c` and `g_client.c` can share consistent timing data without rereading the console variables each frame.【F:src/code/game/g_active.c†L1238-L1314】【F:src/code/game/g_local.h†L608-L747】

## `g_roundWarmupDelay`

`g_roundWarmupDelay` determines how long the server waits before transitioning from warmup to an active freeze round. `G_FreezeScheduleWarmupDelay` in `g_active.c` reads the cvar whenever warmup begins and publishes the new countdown via `CS_WARMUP` and `CS_READYUP_STATUS`, so changing the delay updates both the server state machine and the HUD clock immediately. UI code should consume `CS_READYUP_STATUS` for ready-up deadlines instead of inferring them from `CS_WARMUP`.【F:src/code/game/g_active.c†L1438-L1462】【F:src/code/game/bg_public.h†L94-L109】

## `g_freezeResetWeaponsOnRound`

When `g_freezeResetWeaponsOnRound` is non-zero the round controller respawns every player with the factory loadout at the start of a round. `G_FreezeResetClientsForRound` calls `G_RequestClientSpawn` for each client so their inventory, ammo, and factory tweaks are reapplied even if the player never left the map between rounds.【F:src/code/game/g_active.c†L1322-L1362】

## `g_freezeProtectedSpawnTime`

`g_freezeProtectedSpawnTime` adds a temporary shield to players who just spawned or thawed. `G_FreezeInitClient` and `G_FreezeThawClient` stamp the protection expiry time on the client, and `G_Damage` suppresses incoming damage from other players while the flag is active. The timer automatically clears in `G_FreezeClientEndFrame`, so protection ends cleanly even if nobody attacks.【F:src/code/game/g_client.c†L31-L104】【F:src/code/game/g_client.c†L1493-L1605】【F:src/code/game/g_combat.c†L1270-L1280】

## `g_freezeAutoThawTime`

`g_freezeAutoThawTime` lets frozen players thaw automatically after waiting out the configured delay. `G_FreezeApplyFreezeState` stamps the auto-thaw deadline using the cached round config and `G_FreezeClientEndFrame` watches the timestamp so the thaw occurs even if no teammate is nearby.【F:src/code/game/g_client.c†L31-L104】【F:src/code/game/g_client.c†L1521-L1560】

## `g_freezeEnvironmentalRespawnDelay`

Environmental deaths (lava, void, and similar hazards) honor `g_freezeEnvironmentalRespawnDelay`. When `G_FreezeApplyFreezeState` detects an environmental kill it records the respawn deadline, and `G_FreezeClientEndFrame` thaws the player once that timer elapses, ensuring they are eventually released even if teammates cannot reach the hazard site.【F:src/code/game/g_client.c†L31-L104】【F:src/code/game/g_client.c†L1521-L1560】

## `g_freezeResetHealthOnRound`, `g_freezeResetArmorOnRound`, and `g_freezeRemovePowerupsOnRound`

The freeze round cache also carries the inventory reset toggles. `G_FreezeResetClientsForRound` consults the flags to decide whether to heal, rearm, and strip powerups when a new round begins, and `G_FreezeThawClient` applies the same rules whenever a teammate thaws someone mid-round. This keeps the entire team synchronized with the factory loadout configuration, even if the cvars change between rounds.【F:src/code/game/g_active.c†L1326-L1362】【F:src/code/game/g_client.c†L1569-L1605】
