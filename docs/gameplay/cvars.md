# Gameplay CVar Notes

## Match Timeout Controls

Competitive duel and team modes now expose Quake Live–style match pauses. Players call `timeout` (alias `pause`) to consume one of their team's `g_timeoutCount` allotments, freezing play, logging the owner, and sharing the pause state through `CS_MATCH_STATE` for HUD parity.【F:src/code/game/g_cmds.c†L1593-L1675】【F:src/code/game/g_main.c†L2100-L2149】 The server starts the countdown using `g_timeoutLen` and remembers when the break began so resuming can credit the lost time back to warmup and intermission timers.【F:src/code/game/g_cmds.c†L1657-L1670】【F:src/code/game/g_main.c†L2133-L2149】

`timein` (aliases `resume`, `unpause`) returns the match to live play either on demand or after the configured duration expires. The resume path shifts warmup countdowns, queued exits, and intermission delays by the paused interval so countdowns continue smoothly once action resumes, mirroring Quake Live's behaviour.【F:src/code/game/g_cmds.c†L1678-L1712】【F:src/code/game/g_main.c†L2133-L2149】【F:src/code/game/g_main.c†L2295-L2316】

| Command | Aliases | Notes |
| --- | --- | --- |
| `timeout` | `pause` | Pauses the match if the caller's side has timeouts remaining; sets up `timeoutOwner`, `timeoutStartTime`, and an optional auto-expiry from `g_timeoutLen`.【F:src/code/game/g_cmds.c†L1632-L1670】 |
| `timein` | `resume`, `unpause` | Resumes play for the calling side, reapplies the paused duration to warmup/exit timers, and clears the match state configstring flags.【F:src/code/game/g_cmds.c†L1678-L1712】【F:src/code/game/g_main.c†L2133-L2149】 |

| CVar | Default | Notes |
| --- | --- | --- |
| `g_timeoutCount` | `0` | Number of timeouts each team receives per match; initialised into `level.timeoutRemaining` and published via `CS_MATCH_STATE` for client HUDs.【F:src/code/game/g_main.c†L1093-L1121】【F:src/code/game/g_main.c†L2100-L2131】 |
| `g_timeoutLen` | `60` | Timeout duration in seconds; values ≤0 hold the pause until a manual `timein`, while positive values trigger an automatic resume with broadcast messaging.【F:src/code/game/g_cmds.c†L1657-L1670】【F:src/code/game/g_main.c†L2295-L2316】 |

## Starting Ammo Controls

The server now registers the full Quake Live `g_startingAmmo_*` family so per-weapon spawn loadouts can be tuned without touching code. Each cvar exposes the amount of ammunition players receive when a weapon is granted through `g_startingWeapons`, factories, or scripted loadouts, and publishes a `helptext_*` mirror for in-console discovery. The defaults are defined once in `g_main.c`, ensuring the archived fallback used by `G_InitStartingAmmoConfig` matches the string advertised to administrators and mirrors the retail Quake Live DLL when no overrides are present.

| CVar | Default | Notes |
| --- | --- | --- |
| `g_startingAmmo_bfg` | `10` | BFG cells granted on spawn when the weapon is enabled. |
| `g_startingAmmo_cg` | `100` | Chaingun bullet count applied at spawn. |
| `g_startingAmmo_g` | `-1` | Gauntlet swings; `-1` keeps the melee weapon infinite. |
| `g_startingAmmo_gh` | `-1` | Grappling hook ammo; `-1` preserves Quake Live's unlimited grapple. |
| `g_startingAmmo_gl` | `10` | Grenade launcher rounds granted on spawn. |
| `g_startingAmmo_hmg` | `50` | Heavy machinegun bullet stack for supported mods. |
| `g_startingAmmo_lg` | `100` | Lightning gun cell pool on spawn. |
| `g_startingAmmo_mg` | `100` | Machinegun bullets; aligns with the stock FFA start. |
| `g_startingAmmo_ng` | `10` | Nailgun spikes for spawn loadouts. |
| `g_startingAmmo_pg` | `50` | Plasma gun cell count on spawn. |
| `g_startingAmmo_pl` | `5` | Proximity launcher mines granted when enabled. |
| `g_startingAmmo_rg` | `5` | Railgun slugs granted on spawn. |
| `g_startingAmmo_rl` | `5` | Rocket launcher rockets applied on spawn. |
| `g_startingAmmo_sg` | `10` | Shotgun shell count on spawn. |

### Usage notes

* `G_InitStartingAmmoConfig` reads every `g_startingAmmo_*` value into `g_startingAmmoConfig`, so factory scripts and spawn handlers resolve the configured counts without requiring per-weapon code edits.【F:src/code/game/g_main.c†L564-L596】
* Values persist via archived CVars, allowing event scripts and competitive configs to pre-bake spawn stacks for tournaments while still matching Quake Live's default numbers when unset.【F:src/code/game/g_main.c†L347-L380】【F:src/code/game/g_main.c†L564-L596】

## Weapon Reload Controls

Quake Live exposes a `weapon_reload_*` family that lets operators retime each gun's refire delay in milliseconds. The VM loads Quake Live's defaults into `g_weaponReloadConfig` on startup, ensuring the runtime table always matches the shipping DLL even if the archive is missing or malformed.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L508】

| CVar | Default (ms) | Notes |
| --- | --- | --- |
| `weapon_reload_gauntlet` | `400` | Melee swing delay; higher values slow successive punches.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L498】 |
| `weapon_reload_mg` | `100` | Machinegun refire duration, impacting both spawn weapons and pickups.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_sg` | `1000` | Shotgun pump cycle between blasts.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_gl` | `800` | Grenade launcher refire gate for direct grenades.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_rl` | `800` | Rocket launcher refire delay; applies to splash and direct hits.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_lg` | `50` | Lightning gun tick spacing for continuous fire.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_rg` | `1500` | Railgun cooldown between slugs.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L501】 |
| `weapon_reload_pg` | `100` | Plasma gun cooldown driving bolt cadence.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L494-L502】 |
| `weapon_reload_bfg` | `300` | BFG refire delay before another tracer can be launched.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L502-L504】 |
| `weapon_reload_gh` | `100` | Grappling hook firing delay; negative knockback pairs well with this cadence.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L502-L505】 |
| `weapon_reload_hook` | `100` | Hook pull rate for movement mods that separate pull timing.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L502-L505】 |
| `weapon_reload_ng` | `1000` | Nailgun bolt spacing used in missionpack modes.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L507】 |
| `weapon_reload_prox` | `800` | Proximity launcher mine placement delay.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L507】 |
| `weapon_reload_cg` | `50` | Chaingun refire rate for Team Arena loadouts.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L507】 |
| `weapon_reload_hmg` | `75` | Heavy machinegun spin-up cadence as seen in PQL/CA variants.【F:src/code/game/g_main.c†L52-L66】【F:src/code/game/g_main.c†L505-L508】 |

### Usage notes

* `G_InitWeaponReloadConfig` refreshes the reload table whenever CVars change, so weapon think code can re-query during warmup or between rounds without a restart.【F:src/code/game/g_main.c†L494-L508】
* `G_PmoveStoreWeaponReloads` copies the parsed durations into `g_pmoveSettings.weaponReloadTimes`, keeping server prediction and client pmove in sync after reload CVars change.【F:src/game/g_config.c†L303-L315】【F:src/code/game/g_pmove.c†L170-L259】
* Tuning refire timings is most visible in spawn loadouts from `g_startingWeapons` and in weapon pickup dominance during duel/CA rotations, making it a complementary knob to the spawn ammo controls documented above.【F:docs/gameplay/cvars.md†L5-L34】

## Ammo Pack Pickup Controls

The Quake Live VM reads `g_ammoPack_*` values to determine how much ammunition each pickup grants. The defaults below mirror the retail DLL so that arenas with scripted factories or `ammo_pack` entities award the same payloads players expect.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L556】

| CVar | Default (rounds) | Notes |
| --- | --- | --- |
| `g_ammoPack_mg` | `50` | Machinegun bullet box pickup value.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_sg` | `10` | Shotgun shell pickup from shell boxes.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_gl` | `5` | Grenade launcher ammo pack payload.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_rl` | `5` | Rockets awarded by rocket ammo boxes.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_lg` | `60` | Lightning gun cell pickup amount.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_rg` | `10` | Railgun slug quantity from rail ammo.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_pg` | `30` | Plasma gun cell stack delivered by plasma packs.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_bfg` | `15` | BFG cell reserve per ammo canister.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L539-L546】 |
| `g_ammoPack_hmg` | `50` | Heavy machinegun belt pickup amount for Clan Arena and instagib mods.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L372-L379】【F:src/code/game/g_main.c†L539-L556】 |
| `g_ammoPack_ng` | `20` | Nailgun spikes provided per pickup.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L375-L378】【F:src/code/game/g_main.c†L553-L556】 |
| `g_ammoPack_pl` | `10` | Proximity launcher mines from ammo packs.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L376-L378】【F:src/code/game/g_main.c†L553-L556】 |
| `g_ammoPack_cg` | `100` | Chaingun bullet reserve delivered by Team Arena ammo belts.【F:src/code/game/g_main.c†L88-L99】【F:src/code/game/g_main.c†L369-L380】【F:src/code/game/g_main.c†L553-L556】 |

### Usage notes

* `G_InitAmmoPackConfig` copies these CVars into `g_ammoPackConfig.weaponPickup[]`, which item pickups and factories consult when calling `G_AddAmmo` so gameplay scripts can adjust drop sizes without touching code.【F:src/code/game/g_main.c†L515-L556】
* Pair ammo pack tuning with spawn ammo overrides to balance weapon sustain across duel, TDM, and Clan Arena—lower pickup values encourage map control, while higher stacks reduce dry-fire downtime after respawns.【F:docs/gameplay/cvars.md†L5-L34】【F:src/code/game/g_main.c†L515-L556】

## Knockback Controls

`g_knockback` remains the global scalar, but Quake Live extends it with per-weapon `g_knockback_*` hooks that influence how far targets (and players who self-damage) are launched. Defaults mirror the shipping DLL and are loaded into `g_knockbackConfig` during `G_InitKnockbackConfig`.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L297-L317】【F:src/code/game/g_main.c†L603-L620】

| CVar | Default | Notes |
| --- | --- | --- |
| `g_knockback_g` | `1.0` | Gauntlet knockback multiplier applied to melee hits.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L297-L305】 |
| `g_knockback_mg` | `1.0` | Machinegun knockback scaling for bullet hits.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L298-L305】 |
| `g_knockback_sg` | `1.0` | Shotgun pellet knockback multiplier.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L298-L305】 |
| `g_knockback_gl` | `1.10` | Grenade launcher knockback scaling for direct and splash damage.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L300-L307】 |
| `g_knockback_rl` | `0.90` | Rocket launcher enemy knockback multiplier.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L300-L308】 |
| `g_knockback_rl_self` | `1.10` | Self-inflicted rocket knockback used for rocket jumps.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L300-L308】 |
| `g_knockback_lg` | `1.75` | Lightning gun knockback multiplier per beam tick.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L304-L306】 |
| `g_knockback_rg` | `0.85` | Railgun knockback scaling, affecting enemy displacement after hits.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L304-L307】 |
| `g_knockback_pg` | `1.10` | Plasmagun enemy knockback multiplier.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L305-L308】 |
| `g_knockback_pg_self` | `1.30` | Self-inflicted plasmagun knockback for plasma climbing.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L305-L308】 |
| `g_knockback_bfg` | `1.0` | BFG knockback scalar across splash and tracer hits.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L306-L309】 |
| `g_knockback_gh` | `-5.0` | Grappling hook pull strength; negative values reel players inward.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L306-L309】 |
| `g_knockback_ng` | `1.0` | Nailgun knockback multiplier for Team Arena modes.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L309-L312】 |
| `g_knockback_pl` | `1.0` | Proximity mine knockback scalar for explosions.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L309-L312】 |
| `g_knockback_cg` | `1.0` | Chaingun knockback multiplier.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L310-L312】 |
| `g_knockback_hmg` | `1.0` | Heavy machinegun knockback control for PQL/CA weapons.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L311-L313】 |
| `g_knockback_z` | `24.0` | Additional vertical lift applied after weapon scaling.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L313-L315】 |
| `g_knockback_z_self` | `24.0` | Vertical boost when self-damaging for trick jumps.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L313-L316】 |
| `g_knockback_cripple` | `0.0` | Modifier used when cripple effects are active.【F:src/code/game/g_main.c†L68-L86】【F:src/code/game/g_main.c†L316-L318】 |

### Usage notes

* `G_KnockbackScaleForMOD` in `g_combat.c` consumes the `g_knockbackConfig` scalars for both enemy and self-damage cases, tying the CVars directly to rocket jumping, plasma climbing, and grapple pulls.【F:src/code/game/g_combat.c†L804-L862】
* Adjust the vertical boosters (`g_knockback_z*`) in tandem with weapon-specific scalars to keep trick-jump heights consistent while experimenting with combat knockback changes.【F:src/code/game/g_combat.c†L804-L862】【F:src/code/game/g_main.c†L313-L320】

### Regression checklist

* Use `cvarlist helptext_*` after the VM loads to confirm each help string registered with the expected description.
* Include a weapon in `g_startingWeapons` (for example `set g_startingWeapons RL`) and run `map_restart` to verify the spawn ammo mirrors `g_startingAmmo_rl`.
* Tweak a selection of cvars (for example `g_startingAmmo_rl` and `g_startingAmmo_pg`) and restart the map to confirm the new values drive the spawn stack.
* Persist a modified value (e.g. `seta g_startingAmmo_rl 25`) and restart the server to ensure the archived setting survives a relaunch.
* Ensure gauntlet and grapple defaults remain infinite (`-1`) after a `cvar_restart`.
* Change multiple `weapon_reload_*` CVars, issue a `map_restart`, and observe the new refire cadence in a live match to confirm `g_weaponReloadConfig` picked up the overrides.【F:src/code/game/g_main.c†L494-L508】
* Adjust `weapon_reload_rl` and `weapon_reload_lg`, trigger a `map_restart`, and ensure rockets and lightning ticks adopt the new delays immediately via `PM_GetWeaponReloadTime` and the pmove cache.【F:src/code/game/bg_pmove.c†L211-L250】【F:src/code/game/bg_pmove.c†L2398-L2417】【F:src/code/game/g_pmove.c†L170-L259】
* Override `g_ammoPack_*` values, pick up the corresponding ammo entities, and verify the awarded counts match the configured integers across base maps and factory scripts.【F:src/code/game/g_main.c†L515-L556】
* Adjust `g_knockback_*` scalars (including the self variants), perform rocket and plasma jumps, and check that `G_KnockbackScaleForMOD` applies the updated force for both enemy hits and self-damage.【F:src/code/game/g_combat.c†L804-L862】
