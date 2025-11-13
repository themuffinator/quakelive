# Gameplay CVar Integration and Steam Connection Notes

## Gameplay CVar Inventory

| Quake Live CVar family | Purpose in Quake Live | Quake III entry point / notes |
| --- | --- | --- |
| `g_infiniteAmmo` toggle | Enables limitless ammo for practice factories and is read alongside other gameplay knobs in the DLL cvar table. | Needs a new `vmCvar_t` in `g_main.c` next to the other global gameplay flags so spawn logic can consult it before decrementing ammo in `ClientSpawn` / `PM_Weapon` paths. |
| `g_ammoPack`, `g_ammoPackHack`, `g_ammoRespawn` | Control ammo pack drops and respawn cadence used by Quake Live factories; the DLL enumerates these strings for runtime tuning. | Add mirrored cvars in `gameCvarTable` and feed them into item respawn logic in `g_items.c` where ammo timers and drop quantities are computed. |
| `g_startingAmmo_%s` (per weapon) | Allows factories/mutators to override the spawn stack for each weapon slot; Quake Live iterates a matrix of these names at init. | Introduce a per-weapon ammo table (mirroring `g_weaponConfig`) and consume it in `ClientSpawn` when populating `client->ps.ammo[]`, replacing hard-coded 50/100 defaults. |
| `g_startingHealth`, `g_startingHealthBonus`, `g_startingArmor` | Control the base spawn health, bonus stack, and armor applied to players when they enter the arena. | Cache the values alongside the other factory knobs in `g_config.c` and seed the spawn stats inside `ClientSpawn` so handicap and sudden-death logic continue to function. |
| `weapon_reload_*` | Exposes per-weapon reload timings to script, iterating the family of strings on startup. | Map to a new reload-duration table parallel to `g_weaponConfig`; hook the values in weapon state handling (e.g., `PM_Weapon` raise/drop timers) and validate via `G_ReadWeaponCvar`-style helpers. |
| `g_knockback`, `g_knockback_*`, `g_knockback_*_self`, `g_knockback_z(_self)`, `g_max_knockback` | Registers global and per-weapon knockback scalars, including self-damage tweaks and vertical boosts. | Expand Quake III's single `g_knockback` cvar by introducing a struct of weapon-specific scalars and self-hit overrides; consume them in `G_Damage` where knockback force is derived from damage. |

## Validation, Persistence, and Defaults

- **Registration and persistence**: Declare each cvar as a `vmCvar_t` in `g_main.c` and append them to `gameCvarTable` so they inherit the existing tracking, latching, and archival flags.
- **Structured storage**: Extend the `weaponConfig_t` pattern to host companion structs for starting ammo, reload timings, and knockback multipliers. Refresh the tables through `G_InitWeaponConfig()`/`G_UpdateWeaponConfig()` style helpers that read the bound cvars on restart or vote-driven gameplay changes.
- **Spawn and item hooks**: Apply the validated values in `ClientSpawn` (for starting ammo and infinite-ammo toggles) and in `g_items.c` (for ammo pack drop counts and respawn delays), preserving Quake III's clamping logic such as the 200 ammo cap.
- **Movement and combat integration**: Adjust knockback multipliers while computing weapon kick in `G_Damage`, respecting `g_knockback_*_self` and `g_knockback_z` overrides before applying the final velocity delta.
- **Factory defaults**: Seed sane defaults that match Quake Live presets (for example, 50 rockets and 1.10 plasma knockback) so gameplay remains unchanged unless a script overrides the cvars.

## Steam-Aware Client Connection Handling

1. **Initialize and advertise Steam presence**: Follow the startup flow used by Quake Live (e.g., `sub_465b00`, `sub_466800`) that calls `SteamGameServer()` to publish the lobby, logs "Connected to Steam servers", and turns on periodic callback pumping via `SteamGameServer_RunCallbacks`. Tie this to `ClientConnect`/`ClientBegin` so the server only accepts players after Steam auth is live.
2. **Runtime bookkeeping and callbacks**: Integrate a server-frame hook similar to `sub_466850` to pump Steam callbacks, refresh bot masking roughly every 10 seconds, and poll the networking interface for P2P packets. Trigger the hook from `G_RunFrame` and clear the guard flag on `SteamGameServer_Shutdown`, mirroring Quake Live's "Disconnected from Steam servers" handling.
3. **Bot masking in analytics**: When composing server analytics payloads, log a `botPlayers` field alongside counts such as `numPlayers` and `maxPlayers`. Enumerate `g_entities` for `SVF_BOT` clients before dispatch so downstream services can distinguish human slots from bots.
4. **Steam ticket validation and bans**: Mirror `OnValidateAuthTicketResponse` (`sub_465c50`) so Steam validation and VAC/fake-ban settings are checked before completing `ClientConnect`. Reject invalid tickets with the proper message, while bypassing the path for bot clients flagged with `SVF_BOT`.
5. **Analytics logging and rule publication**: Update server metadata emission (e.g., master server or telemetry payloads) to include the new CVar-driven ammo and knockback fields when building `servers.rules`/`servers.players` responses, keeping Quake Live parity for downstream consumers.
