# Race and CTF timer verification (2024-12-09)

The following captured demos were replayed against the updated HUD/scoreboard timer wiring to confirm parity with the Quake Live references:

- **demo_race_overtime_01.dm_73** – Race clock advanced from `00:00` at the start gate to `01:32.847` on finish, matching the checkpoint split overlay and the scoreboard time column for the local runner. Spectator overlays displayed the leader delta as `-0.22` on the final checkpoint, consistent with the recorded splits.
- **demo_ctf_suddendeath_02.dm_91** – CTF match with a `15:00` regulation limit and two-minute overtime segments. The scoreboard timer rolled through `15:00` into `Overtime 1` without pausing on the board transition, and the sudden-death warning ticked at `17:00` with a `30s` next-tick countdown matching the factory config.
- **demo_ctf_timeout_resume_03.dm_73** – Mid-round timeout frozen the HUD and scoreboard clocks at `08:14`; both resumed from the same timestamp once play restarted, and the overtime counter remained on schedule, confirming the timeout clamp logic.

QA and HUD taskforce reviewers signed off on the captures after cross-checking the on-screen timestamps against the demo frame indices. The playback notes remain attached to the demo manifests for future regression reviews.
