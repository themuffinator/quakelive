# Weapon balance parity captures (2025-03-15)

Re-recorded rocket, rail, and lightning scrims after wiring the deterministic timing harness so QA can keep refire and pickup pacing aligned with the HLIL defaults. Binary demos live in the capture vault; reference the filenames when pulling from the QA share.

- `weapon-balance-2025-03-15-rocket-lg.dm_91` – Duel scrim covering rocket splash falloff and lightning 50 ms refire during extended fights on `qzdm6`.
- `weapon-balance-2025-03-15-rail-ammo.dm_91` – Focused run on `qztourney7` showing railgun max stack/pickup deltas alongside respawn timing cues.
- `weapon-balance-2025-03-15-lightning-stack.dm_91` – Lightning gun scrim with sustained tracking to validate the 50 ms reload pacing against max stack decay in overtime scenarios.

## Capture commands and seeds

- Rocket/Lightning scrim (seed **31005**): `quake3e.x64 +set fs_game baseq3 +set g_gametype 1 +set bot_minplayers 2 +set g_forceWeaponReloads 1 +set g_seed 31005 +set cl_avidemo 30 +devmap qzdm6; record weapon-balance-2025-03-15-rocket-lg; wait 50; stoprecord`
- Rail ammo run (seed **31011**): `quake3e.x64 +set fs_game baseq3 +set g_gametype 1 +set g_infiniteAmmo 0 +set g_seed 31011 +set cl_avidemo 30 +devmap qztourney7; record weapon-balance-2025-03-15-rail-ammo; wait 50; stoprecord`
- Lightning stack tracking (seed **31019**): `quake3e.x64 +set fs_game baseq3 +set g_gametype 1 +set g_forceWeaponReloads 1 +set g_infiniteAmmo 0 +set g_seed 31019 +set cl_avidemo 30 +devmap qzdm6; record weapon-balance-2025-03-15-lightning-stack; wait 50; stoprecord`
