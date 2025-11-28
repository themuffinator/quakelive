# Weapon balance parity captures (2024-11-09)

The demo captures listed below were regenerated to re-verify rocket, rail, and lightning pacing after refreshing the deterministic harness baselines. Binary demos remain in the internal capture vault; use the filenames to retrieve them from the QA share.

- `weapon-balance-2024-11-09-rocket-lg.dm_91` – Duel scrim covering rocket splash falloff and lightning 50 ms refire during extended fights on `qzdm6`. Captured with `exec capture_rocket_lg.cfg; set capture_seed 20241109; set cl_avidemo 30; timedemoquit`.
- `weapon-balance-2024-11-09-rail-ammo.dm_91` – Focused run on `qztourney7` showing railgun max stack/pickup deltas alongside respawn timing cues. Captured with `exec capture_rail_ammo.cfg; set capture_seed 20241109; set cl_avidemo 30; timedemoquit`.
- `weapon-balance-2024-11-09-lg-clip.dm_91` – Lightning-only scrim validating 50 ms refire cadence, ammo drain, and pickup refresh on `qzpractice1`. Captured with `exec capture_lightning_clip.cfg; set capture_seed 20241109; set cl_avidemo 30; timedemoquit`.

Attach these demos to parity tickets or replay them with `cl_avidemo` logging enabled to cross-check damage ticks against `bg_pmove.c` and `bg_misc.c` defaults.
