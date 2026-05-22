# Qagame Spectator Follow Reconstruction - 2026-05-22

## Scope

This pass focused on the qagame side of Quake Live spectating: follow command
dispatch, stop-follow state restoration, end-frame fallback when followed
targets disappear, and the cgame HUD auto-follow command shape that feeds those
server paths.

It intentionally did not edit `src/ui/`, which remains read-only for agents,
and did not launch the game because the recovered gap was settled by static
source/reference evidence and focused parity tests.

## Evidence

Observed retail/reference signals:

1. `references/symbol-maps/qagame.json` maps:
   - `SpectatorThink` at `0x10033E30`, including the attack-edge follow-cycle
     path.
   - `SpectatorClientEndFrame` at `0x10035470`, including followed-player
     mirroring and fallback when follow targets disappear.
   - `StopFollowing` at `0x10040D10`, described as restoring the caller's
     persisted team into playerstate, clearing follow state, resetting the
     spectator client to self, and dropping follow-only flags.
   - `Cmd_Follow_f` at `0x10040F30`, with the `follow1` and `follow2`
     shortcuts plus player-string resolution.
   - `FollowCycle` at `0x10041130`, with the retail diagnostics and race info
     side payload.
2. `references/symbol-maps/cgame.json` maps the HUD auto-follow command seam:
   cgame emits `follow %d%s`, with the `" pw"` suffix used when
   `cg_followPowerup == 2` and the tracked event is a powerup.
3. Existing source already matched the shared movement side for spectator
   flight: `PM_Friction`, `PM_BuildWishMove3D`, `PM_FlyMove`, and
   `PmoveSingle` are covered by the qagame/cgame symbol maps and existing
   pmove parity tests.

## Reconstruction

Source changes:

1. Added `G_DefaultSpectatorState()` as the shared qagame fallback for leaving
   a follow camera. It preserves the repository's documented
   `g_teamSpecFreeCam` policy while keeping the retail stop-follow handoff in
   one place.
2. Reworked `StopFollowing()` so it no longer overwrites
   `sess.sessionTeam` with `TEAM_SPECTATOR`. It now restores
   `ps.persistant[PERS_TEAM]` from the saved session team, resets
   `sess.spectatorClient` to the caller's own client slot, clears
   `PMF_FOLLOW`, updates `PMF_SCOREBOARD` according to the fallback state, and
   restores `ps.clientNum`.
3. Reworked `Cmd_Follow_f()` so it accepts the retail cgame command surface:
   no-arg `follow` stops an active follow camera, `follow1` and `follow2`
   select the active-player shortcuts, normal names/slots still pass through
   `ClientNumberFromString`, and extra command tokens such as the cgame
   `" pw"` suffix no longer turn the command into a stop-follow request.
4. Reworked `SpectatorClientEndFrame()` so unresolved `FOLLOW_ACTIVE1` /
   `FOLLOW_ACTIVE2`, removed POIs, and invalid explicit follow targets drop
   through `StopFollowing()` instead of leaving stale negative
   `spectatorClient` state.

## Tests

Added static parity coverage in `tests/test_game_spectator_connection_parity.py`
for:

- scoreboard spectators consuming command time without moving,
- scoreboard spectator spawn state,
- stop-follow team/self-client restoration,
- retail follow command shortcuts plus optional powerup suffix tolerance,
- end-frame missing-target fallback through `StopFollowing()`.

Focused verification command:

```powershell
python -m pytest tests/test_game_spectator_connection_parity.py tests/test_cgame_spectator_parity.py tests/test_pmove_helper_parity.py -q --tb=short
```

## Parity Estimate

Scoped qagame spectator follow/stop-follow parity: **before 88% -> after 96%**.

The remaining gap is mostly live-behavior confidence rather than known source
shape: POI follow is a Quake Live-only extension in the current reconstruction,
and a future reduced-runtime probe can verify the exact client snapshot
experience when a POI or followed player disappears. Repo-wide parity remains
**98%** because this is a narrow qagame spectator closure.
