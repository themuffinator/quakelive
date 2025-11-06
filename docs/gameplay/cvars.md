# Gameplay CVar Notes

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

### Regression checklist

* Use `cvarlist helptext_*` after the VM loads to confirm each help string registered with the expected description.
* Include a weapon in `g_startingWeapons` (for example `set g_startingWeapons RL`) and run `map_restart` to verify the spawn ammo mirrors `g_startingAmmo_rl`.
* Tweak a selection of cvars (for example `g_startingAmmo_rl` and `g_startingAmmo_pg`) and restart the map to confirm the new values drive the spawn stack.
* Persist a modified value (e.g. `seta g_startingAmmo_rl 25`) and restart the server to ensure the archived setting survives a relaunch.
* Ensure gauntlet and grapple defaults remain infinite (`-1`) after a `cvar_restart`.
