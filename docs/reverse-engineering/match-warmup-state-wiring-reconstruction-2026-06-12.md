# Match Warmup State Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the shared match warmup state rather than a single
gametype: qagame warmup publication, `g_gameState` mirroring, ready-up
deadline publication, auto-record coupling, duel lifecycle warmup resets,
round-controller countdowns, timeout pause adjustment, auto-shuffle countdown
clamping, admin abort reset, and the cgame configstring consumers that draw
warmup and ready-up HUD state.

## Evidence Used

- Owning retail binary: `qagamex86.dll`.
- Ghidra corpus entry points:
  - `references/reverse-engineering/ghidra/qagamex86/metadata.txt`
  - `references/reverse-engineering/ghidra/qagamex86/imports.txt`
  - `references/reverse-engineering/ghidra/qagamex86/exports.txt`
  - `references/reverse-engineering/ghidra/qagamex86/functions.csv`
  - `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- qagame symbol map:
  - `0x10059C10 -> G_SetWarmupTime`
  - `0x100632D0 -> G_CheckAutoRecord`
  - `0x10058580 -> G_CheckReadyUpDelayAction`
  - `0x100586E0 -> CheckTournament`
  - `0x10045BD0 -> Cmd_ReadyUp_f`
  - `0x10061800 -> Cmd_AllReady_f`
  - `0x10068140 -> Team_HasMinimumPlayersForWarmup`
  - `0x10066440 -> SP_worldspawn`
- cgame symbol map:
  - `CG_ParseWarmup` consumes `CS_WARMUP`, resets warmup countdown caches,
    stores the optional warmup gametype override, and mirrors to `ui_warmup`.
  - `CG_ParseReadyUpStatus` and `CG_ParseWarmupReadyStatus` consume the
    source-side ready-up deadline and readiness snapshot.

## Observed Wiring

| Surface | Retail-backed mapping | Source state after this pass |
| --- | --- | --- |
| Warmup latch | `G_SetWarmupTime` is descriptive but stable: it writes the live warmup deadline, republishes `CS_WARMUP`, runs the auto-record controller, and derives `g_gameState` from negative/countdown/zero. | Public warmup deadline mutations now route through `G_SetWarmupTime` across duel lifecycle, round controllers, timeout resume, auto-shuffle clamp, Freeze expiration, and abort reset. |
| Worldspawn bootstrap | Ghidra `SP_worldspawn` shows the warmup slot reset to waiting, optional `Warmup:` log, and `g_gameState` set to `PRE_GAME` or `IN_PROGRESS` on restarted maps. | `SP_worldspawn` already used `G_SetWarmupTime`; this pass preserved that shape. |
| Ready-up deadline | Retail ready-up helpers share the warmup countdown and duel ready-delay deadline surfaces. | `G_UpdateReadyUpConfigstring` remains the single source-side deadline publisher and is reached through `G_SetWarmupTime` for public warmup changes. |
| Warmup-ready snapshot | Retail/server-visible metadata includes `sv_warmupReadyPercentage`; source-side qagame publishes count/eligible/pct for HUD consumers. | `G_WarmupReadyToStart` still computes eligible/ready counts, clamps percent, writes `CS_WARMUP_READY`, and mirrors the ready mask into `STAT_CLIENTS_READY`. |
| Duel lifecycle | Retail tournament helpers reset warmup to waiting when player count drops and start countdown only after ready gates pass. | `G_DuelInit` and `G_DuelClientBegin` now call `G_SetWarmupTime` instead of hand-writing `level.warmupTime` and `CS_WARMUP`. |
| Round controllers | CA, Freeze, Red Rover, and generic round controllers publish waiting, countdown, and live transitions through the shared warmup slot. | Insufficient-player resets, round warmup scheduling, and Freeze countdown expiry now use `G_SetWarmupTime`. Compact `CS_MATCH_STATE` payloads remain owned by `g_match_state.c`. |
| Timeout pause | Retail timeout resume shifts finite absolute timers while preserving live match state. | Warmup countdown extension during timeout resume now goes through `G_SetWarmupTime( level.warmupTime + msec )` so `CS_WARMUP`, ready-up, auto-record, and `g_gameState` stay coherent. |
| Auto-shuffle clamp | Retail warmup is extended when the team shuffle countdown would otherwise outlive it. | `Team_ClampWarmupToShuffleCountdown` now uses `G_SetWarmupTime( targetTime )` for the extended deadline. |
| Admin abort | Retail abort returns the match to pre-game and restarts after the recovered print/pcp path. | `Cmd_Abort_f` now resets timeout state and calls `G_SetWarmupTime( -1 )` before refreshing match-state configstrings and queuing `map_restart 3`. |
| Cgame consumers | Retail cgame parses warmup and match-state side channels separately: `CS_WARMUP` drives countdown/prepare sounds and `ui_warmup`; ready-up slots drive the prompt deadline and readiness counters. | No cgame source change was required; existing parsers and HUD tests were revalidated against the qagame publication cleanup. |

## Source Reconstruction

- Routed public warmup deadline changes through `G_SetWarmupTime` in:
  - `src/code/game/g_active.c`
  - `src/code/game/g_main.c`
  - `src/code/game/g_cmds.c`
  - `src/code/game/g_team.c`
  - `src/code/game/g_gametype_lifecycle.inc`
- Preserved the existing direct `level.warmupTime += 10000` in
  `G_RequestWarmupMapRestart` as an internal pre-`map_restart` grace bump,
  not a newly published public countdown state.
- Added a lifecycle-harness `G_SetWarmupTime` shim so the included duel
  lifecycle source exercises the same boundary while keeping the focused
  harness small.
- Strengthened static parity tests for timeout pause, auto-shuffle clamp, duel
  lifecycle countdown, round warmup scheduling, Freeze warmup expiration, and
  admin abort reset.

## Verification

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py::test_match_flow_warmup_timeout_cvars_keep_retail_behavioral_wiring tests/test_game_active_pmove_wiring_parity.py::test_round_freeze_timing_cvars_keep_retail_behavioral_wiring tests/test_game_helper_seam_parity.py::test_timeout_race_and_direct_command_helpers_match_recovered_boundaries tests/test_gametype_lifecycle.py -q`
  - `11 passed`
- `python -m pytest tests/test_gametype_lifecycle.py tests/test_game_duel_ready_delay_parity.py tests/test_game_readyup_parity.py tests/test_match_state_configstring.py tests/test_game_team_count_parity.py -q --tb=short`
  - `26 passed, 8 skipped`

## Open Questions

- `G_SetWarmupTime` remains a descriptive source boundary. The symbol-map row
  and neighboring decompile evidence pin the side effects, but the committed
  top decompile does not expose the exact body at `0x10059C10`.
- The cgame warmup HUD path was revalidated statically, not visually. No client
  launch was required because the changed behavior is server-side publication
  and existing parser/HUD parity gates cover the consumers.
- The pre-restart `level.warmupTime += 10000` grace bump remains intentionally
  direct. A future single-step runtime trace could decide whether that should
  also publish through the helper, but existing tests and map-restart timing
  evidence keep it isolated for now.

## Parity Estimate

Focused match warmup state and wiring moves approximately **94% -> 98%**. The
remaining uncertainty is exact retail helper body shape and visual freshness for
the cgame warmup overlays, not the qagame publication/control-flow wiring.
Repo-wide parity remains approximately **99%**.
