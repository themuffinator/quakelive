# `cgame` / `bg_*` Retail Parity Audit And Multi-Agent Plan

Last updated: 2026-05-20

Scope: `src/code/cgame/*`, `src/code/game/bg_misc.c`, `src/code/game/bg_pmove.c`, `src/code/game/bg_slidemove.c`

Purpose: supplement [IMPLEMENTATION_PLAN.md](../../IMPLEMENTATION_PLAN.md) with a concurrency-safe retail parity ledger for the writable `cgame` and shared `bg_*` seams.

## Audit Method

- Canonical parity evidence:
  - `references/reverse-engineering/ghidra/cgamex86/{metadata.txt,functions.csv,decompile_top_functions.c,analysis_symbols.txt}`
  - `references/reverse-engineering/ghidra/qagamex86/{metadata.txt,functions.csv,decompile_top_functions.c,analysis_symbols.txt}`
  - `references/symbol-maps/cgame.json`
  - `references/symbol-maps/qagame.json`
  - `docs/reverse-engineering/cgame-mapping.md`
  - `docs/reverse-engineering/qagame-mapping.md`
- Current source inspected:
  - `src/code/cgame/*`
  - `src/code/game/bg_misc.c`
  - `src/code/game/bg_pmove.c`
  - `src/code/game/bg_slidemove.c`
- Static scan snapshot:
  - `cgamex86.dll` committed Ghidra corpus: `751` functions, `55` imports, `2` exports.
  - `qagamex86.dll` committed Ghidra corpus: `1027` functions, `65` imports, `2` exports.
  - Historical audit note: the opening 2026-04-05 direct owner-token scan found `156` normalized `CG_*` names from `references/symbol-maps/cgame.json` with no direct source owner token, including `116` browser/widget/overlay names and `10` placement-ownerdraw helpers.
  - After the closures recorded below, no active direct-owner gaps remain in the writable `cgame` lanes tracked by this plan.
  - Direct owner-token scan against `bg_misc.c`, `bg_pmove.c`, and `bg_slidemove.c` found `0` missing normalized `BG_*` or `PM_*` names from the mapped shared gameplay seam.
- Interpretation rule:
  - Missing direct owners in `cgame` are not automatically missing behavior. Many are retail-only split boundaries that current source folds into larger helpers.
  - `bg_*` is the inverse case: the mapped function surface is already present in source, so remaining work is mostly transport, preset selection, validation, and source-boundary cleanup.
- Current worktree note:
  - This audit reflects the already-dirty tree present on 2026-04-05. It does not assume unrelated local edits should be reverted.

## Overall Assessment

- `cgame` is now in the `high mapping coverage / high source parity` range for the writable lanes covered by this plan.
- The retail browser/widget/overlay lane is now closed at the direct-owner boundary too: the runtime surface, parser/bootstrap seam, and the remaining draw/control/script/capture leaf families are all source-owned in `cgame`, while the verified shared `ui_shared.c` bodies remain underneath where retail behavior is shared.
- The event-band realignment between qagame and cgame is source-backed end to end: the direct temp-entity payload slots, the Freeze thaw-temp-entity band plus its cgame thaw consumers, the Red Rover survival-bonus broadcast, and the prediction-transition validation seam are all closed. No active writable `cgame` lane remains open in this plan.
- `bg_*` is in the `high source parity` range. No mapped `BG_*` or `PM_*` functions are outright absent from the writable source.
- The remaining `bg_*` work is now future-only. The current shared pickup, trajectory, and movement seams are covered closely enough that further `bg_*` changes should wait for a concrete later retail diff rather than speculative boundary splitting.

## Parallel Execution Rules

- One agent per lane. Do not split a lane across multiple agents unless the lane explicitly says it is safe.
- `src/code/cgame/cg_newdraw.c`, `src/code/cgame/cg_servercmds.c`, and `src/code/game/bg_pmove.c` are single-writer hotspots.
- `src/ui/` is read-only and out of bounds for this plan.
- When a task depends on qagame, host, or UI work outside this scope, keep the cgame/bg change behind a compatibility bridge until the dependency lands.
- Boundary-only refactors must not land ahead of behavioral parity on the same seam.

## Lane Index

| Lane | Status | Write set | Primary theme | Parallel notes |
| --- | --- | --- | --- | --- |
| `CG-A` | `CLOSED` | `src/code/cgame/cg_newdraw.c`, `src/code/cgame/cg_main.c`, `src/code/cgame/cg_local.h` | Retail browser/widget/overlay runtime | Closed 2026-04-05 after restoring the remaining browser leaf owner split beneath the shared UI runtime |
| `CG-B` | `CLOSED` | `src/code/cgame/cg_servercmds.c`, `src/code/cgame/cg_players.c`, `src/code/game/g_main.c` | Configstring and scoreboard transport parity | Closed 2026-04-05 after restoring the live `teamsize` serverinfo transport for player-count ownerdraw caps |
| `CG-C` | `CLOSED` | `src/code/cgame/cg_event.c`, `src/code/cgame/cg_snapshot.c`, `src/code/cgame/cg_playerstate.c`, `src/code/cgame/cg_predict.c` | Event payload and prediction-side transport parity | Closed 2026-04-05 after restoring the Red Rover survival-bonus `EV_GLOBAL_TEAM_SOUND` broadcast and clearing the last `CG-C2` compatibility note |
| `CG-D` | `CLOSED` | `src/code/cgame/cg_draw.c`, `src/code/cgame/cg_effects.c`, `src/code/cgame/cg_ents.c`, `src/code/cgame/cg_localents.c` | POI, queued world markers, projected timers, effects exactness | Closed 2026-04-05 after restoring the projected item-respawn timer owner and rechecking the queued-world-marker split |
| `CG-E` | `CLOSED` | `src/code/cgame/cg_main.c`, `src/code/cgame/cg_consolecmds.c`, `src/code/cgame/cg_screen.c`, `src/code/cgame/cg_local.h` | Social sidecar, native export tail, command-overlay parity | Closed 2026-04-05 after revalidating the identity-backed native mute callbacks and closing the last social sidecar fallback note |
| `BG-A` | `CLOSED` | `src/code/game/bg_pmove.c`, `src/code/game/bg_slidemove.c`, `src/code/game/bg_pmove_jump.h` | Movement tuning, jump, step, and air-control parity | Closed 2026-04-05 after retail-backed runtime validation of the merged step and air-control seams |
| `BG-B` | `CLOSED` | `src/code/game/bg_misc.c`, `src/code/game/bg_public.h`, `src/code/game/bg_local.h` | Shared pickup/trajectory validation and boundary cleanup | Closed 2026-04-05 after runtime-backed pickup validation and explicit acceptance of the current merged helper boundaries |

## Gap Catalog

### Closed In This Pass

| ID | Lane | Type | Evidence | Closure |
| --- | --- | --- | --- | --- |
| `CG-D4` | `CG-D` | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`tests/test_cgame_spectator_parity.py`](../../tests/test_cgame_spectator_parity.py), `docs/reverse-engineering/cgame-mapping.md:310-314` | Closed on `2026-04-05`. `cg_newdraw.c` now restores the retail competitive scorebox owner split by routing the local, red, and blue score slots through `CG_DrawScoreValue` and by drawing the primary or secondary duel-status labels through the dedicated `CG_DrawSpectatorPrimaryStatus` and `CG_DrawSpectatorSecondaryStatus` owners instead of the older merged placement-text fallback. |
| `CG-A1` | `CG-A` | Behavioral | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`cg_draw.c`](../../src/code/cgame/cg_draw.c), [`cg_screen.c`](../../src/code/cgame/cg_screen.c), [`cg_local.h`](../../src/code/cgame/cg_local.h), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md) | Closed on `2026-04-05`. Cgame now owns the retail browser runtime surface at the behavioral boundary: key dispatch first checks the captured overlay root, out-of-bounds clicks route through a named cgame wrapper, widget-state allocation and root or widget draw dispatch are explicit cgame owners, and the live cached-overlay, scoreboard, stats, join-game, and generic browser draw callsites no longer paint through raw `Menu_Paint*` calls. The shared `ui_shared.c` frame pump and leaf painters remain the verified implementation underneath those cgame runtime wrappers. |
| `CG-A3` | `CG-A` | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`cg_main.c`](../../src/code/cgame/cg_main.c), [`cg_local.h`](../../src/code/cgame/cg_local.h), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md) | Closed on `2026-04-05`. `cg_newdraw.c` now restores the remaining retail browser leaf-owner surface for list metrics, fade/transition/orbit and advert verbs, overlay activation/cinematic shutdown, multi/preset/bind/slider/text/model painters, and the remaining control-key or capture wrappers, while `cg_main.c` exports the preset/layout refresh and overlay-activation bridge that the live open path now uses instead of direct `Menus_OpenByName` calls. The shared `ui_shared.c` helpers remain the verified implementation underneath those cgame owners. |
| `CG-E4a` | `CG-E` | Boundary-only | [`cg_main.c`](../../src/code/cgame/cg_main.c), [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), `docs/reverse-engineering/cgame-mapping.md:525-528`, `docs/reverse-engineering/cgame-mapping.md:1021-1031`, [`tests/test_cgame_announcer_timer_helper_parity.py`](../../tests/test_cgame_announcer_timer_helper_parity.py) | Closed on `2026-04-05`. The source now owns the retail announcer-path stem builder plus the `CG_FormatMinutesSeconds` / `CG_FormatSignedWholeSeconds` helper pair, and the live scorebox or team-time-held ownerdraw callers route through the named minute-seconds helper instead of open-coded `"%i:%i%i"` formatting. |
| `CG-E4b` | `CG-E` | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`cg_players.c`](../../src/code/cgame/cg_players.c), `docs/reverse-engineering/cgame-mapping.md:1069-1070`, `docs/reverse-engineering/cgame-mapping.md:1110`, [`tests/test_cgame_ownerdraw_text_parity.py`](../../tests/test_cgame_ownerdraw_text_parity.py), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py) | Closed on `2026-04-05`. `cg_newdraw.c` now mirrors the retail boxed 3D client preview with legs, torso, head, attached weapon or barrel, optional grapple ammo, and the preview-only light pair, while `cg_players.c` retains the direct `CG_ResolveClientModelColorBytes` owner beneath the merged player-color application seam. |
| `CG-E1` | `CG-E` | Transport | [`cg_main.c`](../../src/code/cgame/cg_main.c), [`tests/test_cl_console_cgame_parity.py`](../../tests/test_cl_console_cgame_parity.py), `docs/reverse-engineering/cgame-mapping.md:247-249`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:22878-22910`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:43319-43589`, `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt:84049-84068` | Closed on `2026-04-05`. `CG_CopyClientIdentity` now makes the copied retail ABI explicit by zeroing `identityTransport`; the committed retail player parser only rebuilds the identity-word pair plus avatar cache, no committed cgame producer materializes a non-zero write to `0x10A42400`, and the recovered host overlay consumer only branches on the low/high identity words. |
| `CG-E2` | `CG-E` | Transport | [`cg_consolecmds.c`](../../src/code/cgame/cg_consolecmds.c), [`cg_main.c`](../../src/code/cgame/cg_main.c), [`cg_servercmds.c`](../../src/code/cgame/cg_servercmds.c), [`cl_cgame.c`](../../src/code/client/cl_cgame.c), [`tests/test_cgame_scoreboard_social_parity.py`](../../tests/test_cgame_scoreboard_social_parity.py), `docs/reverse-engineering/cgame-mapping.md:245-250` | Closed on `2026-04-05`. The source no longer relies on the earlier client-slot mute toggle fallback: `CG_ClientMute_f` forwards the retail identity-word pair through `trap_QL_ToggleClientMute`, scoreboard and chat consumers refresh `cg.clientMuted[]` from `trap_QL_IsClientMuted`, and the host-side cgame import slab stores muted identities in an identity-keyed set without inventing new public import enums. |
| `BG-A1` | `BG-A` | Behavioral | [`bg_pmove.c:379-449`](../../src/code/game/bg_pmove.c), [`bg_pmove.c:730-768`](../../src/code/game/bg_pmove.c), [`bg_pmove.c:1433-1500`](../../src/code/game/bg_pmove.c), `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt:30683-30712`, `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt:32131-32276` | Closed on `2026-04-05`. The source now preserves planar speed through the retail `PM_AirControl` reverse-dot path, and executable fixtures cover alternate bundle selection, non-stock override preservation, air-stop accel, pure-strafe wishspeed clamp, and one-shot air double-jump reuse in [`tests/test_pmove_air_control_runtime_parity.py`](../../tests/test_pmove_air_control_runtime_parity.py). |
| `BG-A2` | `BG-A` | Boundary-only | `docs/reverse-engineering/qagame-mapping.md:419-423`, [`bg_pmove.c:996-1095`](../../src/code/game/bg_pmove.c), [`bg_slidemove.c:320-560`](../../src/code/game/bg_slidemove.c), [`tests/test_step_jump_gate_parity.py`](../../tests/test_step_jump_gate_parity.py), [`tests/test_crouch_step_prediction.py`](../../tests/test_crouch_step_prediction.py), [`tests/test_pmove_validation_fixtures.py`](../../tests/test_pmove_validation_fixtures.py) | Closed on `2026-04-05`. The source keeps the merged `PM_ApplyStepJump` wrapper, but the retail-adjacent leaves `PM_CanStepJump`, `PM_CanCrouchStepJump`, and `PM_ApplyJumpTakeoff` are now explicitly verified as equivalent through structural tests, supported or unsupported step probes, and direct step-jump takeoff fixtures. |
| `BG-A3` | `BG-A` | Boundary-only | `references/symbol-maps/qagame.json` comment for `PM_StepSlideMove`, [`bg_slidemove.c:432-578`](../../src/code/game/bg_slidemove.c), [`tests/test_step_jump_gate_parity.py`](../../tests/test_step_jump_gate_parity.py), [`tests/test_pmove_validation_fixtures.py`](../../tests/test_pmove_validation_fixtures.py), [`tests/pmove_validation_harness.c`](../../tests/pmove_validation_harness.c) | Closed on `2026-04-05`. `PM_StepSlideMove` remains the public one-argument retail boundary, the configurable step-height helper stays internal to `bg_slidemove.c`, and stock-step-height behavior is runtime-validated through the supported versus unsupported public-entry fixtures. |
| `CG-E3` | `CG-E` | Behavioral | [`cg_consolecmds.c:506-560`](../../src/code/cgame/cg_consolecmds.c), [`bg_public.h:257-265`](../../src/code/game/bg_public.h), `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt:5024-5036`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt:35534-35545` | Closed on `2026-04-05`. The retail `readyup` bypass is now keyed off `PM_INTERMISSION` instead of tutorial configstring proxies, with the source reading the live or predicted `pm_type` while preserving the recovered warmup window and spectator gate. |
| `BG-B1` | `BG-B` | Validation | `references/symbol-maps/qagame.json` comments for `BG_PlayerTouchesItem`, `BG_CanItemBeGrabbed`, and `BG_FindItemForPowerup`, [`bg_misc.c`](../../src/code/game/bg_misc.c), [`tests/test_bg_misc_helper_parity.py`](../../tests/test_bg_misc_helper_parity.py), [`tests/test_bg_itemlist_indexes.py`](../../tests/test_bg_itemlist_indexes.py), [`tests/bg_misc_validation_harness.c`](../../tests/bg_misc_validation_harness.c), [`tests/test_bg_misc_validation_fixtures.py`](../../tests/test_bg_misc_validation_fixtures.py), [`tests/test_bg_misc_runtime_parity.py`](../../tests/test_bg_misc_runtime_parity.py) | Closed on `2026-04-05`. The shared pickup seam is now backed by executable fixtures for the invulnerability, TA-rune, and team-item lookup routes, the retail pickup-touch bounds for normal items versus flags, and representative weapon or health pickup gates including dropped-weapon self-lockout plus the small-health upper bound. |
| `BG-B2` | `BG-B` | Boundary-only | `docs/reverse-engineering/qagame-mapping.md:568-579`, [`bg_misc.c`](../../src/code/game/bg_misc.c), [`tests/test_bg_misc_helper_parity.py`](../../tests/test_bg_misc_helper_parity.py), [`tests/test_bg_misc_validation_fixtures.py`](../../tests/test_bg_misc_validation_fixtures.py), [`tests/test_bg_misc_runtime_parity.py`](../../tests/test_bg_misc_runtime_parity.py) | Closed on `2026-04-05`. No later retail diff currently justifies splitting the shared pickup helpers beyond the current `BG_FindItemForPowerup`, `BG_PlayerTouchesItem`, and `BG_CanItemBeGrabbed` family, so the existing merged helper surface is now treated as a deliberate verified source merge rather than a live parity gap. |
| `CG-B1` | `CG-B` | Transport | [`g_main.c`](../../src/code/game/g_main.c), [`cg_servercmds.c`](../../src/code/cgame/cg_servercmds.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `docs/reverse-engineering/cgame-mapping.md:784-788`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:49496-49534`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:78809-78813` | Closed on `2026-04-05`. The source now mirrors the player-count-cap transport through a serverinfo-facing `teamsize` alias for `g_teamSizeMin`, cgame consumes that live key directly in `CG_ParseServerinfo`, and the older dual-key best-effort path has been removed so intro/status ownerdraws stay synchronized with live teamsize changes. |
| `CG-B1a` | `CG-B` | Transport | [`bg_public.h`](../../src/code/game/bg_public.h), [`g_main.c`](../../src/code/game/g_main.c), [`g_match_config.c`](../../src/game/g_match_config.c), [`cg_servercmds.c`](../../src/code/cgame/cg_servercmds.c), [`tests/test_ui_menu_files.py`](../../tests/test_ui_menu_files.py), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:49954`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:50307-50309`, `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt:58362`, `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt:60991` | Closed on `2026-04-05`. Retail slot `0x2A2` is now source-owned as `CS_PLAYER_CYLINDERS`: qagame publishes `g_playerCylinders` there, cgame consumes it through `CG_ParsePlayerCylindersConfigString`, and the old factory-title collision has been removed by keeping `g_factoryTitle` on the serverinfo path while `CS_FACTORY_FLAGS` retains the numeric factory mask. |
| `CG-B4` | `CG-B` | Transport | [`cg_servercmds.c:2672-2692`](../../src/code/cgame/cg_servercmds.c), [`cg_servercmds.c:3426-3463`](../../src/code/cgame/cg_servercmds.c), [`cg_servercmds.c:3512-3568`](../../src/code/cgame/cg_servercmds.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `references/symbol-maps/cgame.json` comment for `CG_ParseArmorTieredConfigString` | Closed on `2026-04-05`. `CG_ParseArmorTieredConfigString` is now a direct source-owned parser boundary in `cg_servercmds.c`, sourced from `CS_SERVER_SETTINGS_INFO_A`, mirrored through `cg_armorTiered`, and re-entered from both `CG_SetConfigValues` and `CG_ConfigStringModified`; focused structural tests keep the older `CS_SERVERINFO` path out of the seam. |
| `CG-B5` | `CG-B` | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `docs/reverse-engineering/cgame-mapping.md:313`, `references/symbol-maps/cgame.json` comments for `CG_DrawPlacementPingOwnerDraw`, `CG_DrawPlacementAccuracyOwnerDraw`, `CG_DrawPlacementWeaponFragsOwnerDraw`, `CG_DrawPlacementWeaponHitsOwnerDraw`, `CG_DrawPlacementWeaponShotsOwnerDraw`, `CG_DrawPlacementWeaponDamageOwnerDraw`, `CG_DrawPlacementWeaponAccuracyOwnerDraw`, `CG_DrawPlacementPickupCountOwnerDraw`, `CG_DrawPlacementPickupAverageOwnerDraw`, and `CG_DrawPlacementAwardCountOwnerDraw` | Closed on `2026-04-05`. `cg_newdraw.c` now routes the remaining placement scorebox metric slots through dedicated retail-named ping, total-accuracy, per-weapon, pickup, and medal ownerdraw wrappers instead of falling through the generic placement-text path, while keeping the shared builder as the verified implementation underneath. |
| `CG-B3a` | `CG-B` | Boundary-only | [`cg_servercmds.c`](../../src/code/cgame/cg_servercmds.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `references/symbol-maps/cgame.json` comment for `CG_ParseFFAScores` | Closed on `2026-04-05`. The source now exposes the retail-owned `CG_ParseFFAScores` boundary and routes the dedicated `scores_ffa` command through it while preserving the separate legacy `CG_ParseScores` parser for the generic `scores` transport. |
| `CG-B3` | `CG-B` | Boundary-only | [`cg_draw.c`](../../src/code/cgame/cg_draw.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt:10212-10240`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt:12559-12810` | Closed on `2026-04-05`. `cg_draw.c` now owns the recovered `CG_DrawADRoundScoreboard` helper, `CG_DrawWarmupStatusText` routes the Attack and Defend warmup path through that direct owner before the offense or defense banner text, and a focused regression locks the retail 240x48 round grid, active-team and active-round highlights, `Round`/`Red`/`Blue`/`Score` labels, and the retained `Match Point`, `Last Chance`, and `Red Wins! Good Game` status strings. |
| `CG-D1` | `CG-D` | Behavioral | [`cg_draw.c:612-641`](../../src/code/cgame/cg_draw.c), [`cg_main.c:798-799`](../../src/code/cgame/cg_main.c), [`tests/test_cgame_poi_parity.py`](../../tests/test_cgame_poi_parity.py), `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:75114-75126`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:84249-84260` | Closed on `2026-04-05`. HLIL now anchors the hidden `cg_poiMinWidth` / `cg_poiMaxWidth` defaults at `16.0` / `32.0`, and the source keeps the same `256..768` linear width falloff; a focused regression test now guards the cvar registrations and interpolation path so the POI marker clamp is tracked as exact instead of approximate. |
| `CG-D2` | `CG-D` | Boundary-only | [`cg_ents.c`](../../src/code/cgame/cg_ents.c), [`cg_main.c`](../../src/code/cgame/cg_main.c), [`g_items.c`](../../src/code/game/g_items.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `references/symbol-maps/cgame.json` comment for `CG_DrawItemRespawnTimer` | Closed on `2026-04-05`. The queued-world-marker trio was already source-owned in `cg_draw.c`; this pass restores the missing retail `CG_DrawItemRespawnTimer` boundary in `cg_ents.c`, keeps the dedicated `gfx/2d/timer/*` media family registered in `cg_main.c`, and routes `CG_Item` through the helper before the later skip-item or `EF_NODRAW` exits while consuming the qagame-published `time2` duration and only falling back to the retail 25/35/60/120-second item buckets when older emitters do not provide it. |
| `CG-C1a` | `CG-C` | Transport | [`g_combat.c`](../../src/code/game/g_combat.c), [`cg_event.c`](../../src/code/cgame/cg_event.c), [`tests/test_cgame_event_transport_parity.py`](../../tests/test_cgame_event_transport_parity.py), `references/symbol-maps/qagame.json` comment for `G_AddDamagePlum`, `docs/reverse-engineering/cgame-mapping.md:589-594` | Closed on `2026-04-05`. `g_combat.c` now restores the retail single-recipient `EV_DAMAGEPLUM` temp-entity seam through `G_AddDamagePlum`, and `cg_event.c` consumes the recovered recipient, raw damage, and weapon payload slots directly instead of falling back to GPL `eventParm` transport or predicted-weapon bridges. |
| `CG-C1` | `CG-C` | Transport | [`q_shared.h`](../../src/code/game/q_shared.h), [`msg.c`](../../src/code/qcommon/msg.c), [`g_utils.c`](../../src/code/game/g_utils.c), [`g_combat.c`](../../src/code/game/g_combat.c), [`g_client.c`](../../src/code/game/g_client.c), [`g_main.c`](../../src/code/game/g_main.c), [`g_team.c`](../../src/code/game/g_team.c), [`g_weapon.c`](../../src/code/game/g_weapon.c), [`cg_event.c`](../../src/code/cgame/cg_event.c), [`tests/test_cgame_event_transport_parity.py`](../../tests/test_cgame_event_transport_parity.py) | Closed on `2026-04-05`. The source now restores the recovered retail temp-entity and global-team-sound payload slots directly: recipient through `entityState_t.solid`, raw damage through the `0x5C` integer payload over `origin[0]`, award or damage-plum data through the restored `retailEventData` slot at `0xE0`, and the global-team-sound code/tracked-client/team/index through `weapon`, `groundEntityNum`, `frame`, and `legsAnim`. Qagame emitters and cgame consumers no longer rely on the older `eventParm` / `clientNum` / `generic1` bridge fields for this seam. |
| `CG-C2a` | `CG-C` | Validation | [`bg_public.h`](../../src/code/game/bg_public.h), [`g_client.c`](../../src/code/game/g_client.c), [`g_freeze.c`](../../src/code/game/g_freeze.c), [`cg_event.c`](../../src/code/cgame/cg_event.c), [`tests/test_game_native_export_helper_parity.py`](../../tests/test_game_native_export_helper_parity.py), [`tests/test_cgame_event_transport_parity.py`](../../tests/test_cgame_event_transport_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md), [`docs/reverse-engineering/qagame-mapping.md`](../../docs/reverse-engineering/qagame-mapping.md) | Closed on `2026-04-05`. Freeze thaw-progress visibility now guards the live `ET_EVENTS + EV_THAW_TICK` temp-entity band, qagame emits thaw-complete and thaw-progress through `EV_THAW_PLAYER` / `EV_THAW_TICK`, and cgame consumes those cases directly in `CG_EntityEvent` without the older synthetic thaw-alias compatibility path. |
| `CG-C2` | `CG-C` | Validation | [`g_client.c`](../../src/code/game/g_client.c), [`cg_event.c`](../../src/code/cgame/cg_event.c), [`tests/test_cgame_event_transport_parity.py`](../../tests/test_cgame_event_transport_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md), [`docs/reverse-engineering/qagame-mapping.md`](../../docs/reverse-engineering/qagame-mapping.md), `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt:72298-72304` | Closed on `2026-04-05`. `G_RRApplySurvivalBonus` now emits the retail Red Rover survival-bonus broadcast through `G_BroadcastGlobalTeamSound( vec3_origin, GTS_SURVIVOR_WARNING, -1, TEAM_BLUE, 0 )`, and the existing `EV_GLOBAL_TEAM_SOUND` consumer already gates `GTS_SURVIVOR_WARNING` on the local team before queuing `survivorWarningSound`. |
| `CG-C3a` | `CG-C` | Validation | [`cg_predict.c`](../../src/code/cgame/cg_predict.c), [`cg_snapshot.c`](../../src/code/cgame/cg_snapshot.c), [`cg_servercmds.c`](../../src/code/cgame/cg_servercmds.c), [`tests/test_cgame_snapshot_parity.py`](../../tests/test_cgame_snapshot_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md) | Closed on `2026-04-05`. Prediction now tracks follow and team context through `CG_UpdateClientInfoContext`, local `CS_PLAYERS + cg.clientNum` updates queue the same refresh before `CG_NewClientInfo`, and snapshot handoff re-enters only `CG_ApplyModelOverrides` plus `CG_LoadDeferredPlayers` instead of rebuilding clientinfo inline or forcing immediate refresh from the servercmd path. |
| `CG-C3` | `CG-C` | Validation | [`cg_predict.c`](../../src/code/cgame/cg_predict.c), [`cg_playerstate.c`](../../src/code/cgame/cg_playerstate.c), [`cg_snapshot.c`](../../src/code/cgame/cg_snapshot.c), [`tests/test_cgame_snapshot_parity.py`](../../tests/test_cgame_snapshot_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md) | Closed on `2026-04-05`. Focused structural coverage now locks the remaining retail transition chain after the event-payload cleanup: `CG_PredictPlayerState` keeps the demo/follow and no-predict interpolation fallbacks ahead of local pmove, `CG_TransitionSnapshot` only replays playerstate transitions on non-predicted paths, `CG_RecordCrosshairHitFeedback` preserves the `( armor >> 6 ) + 1` bucket clamp, and `CG_TransitionPlayerState`, `CG_CheckLocalSounds`, and `CG_CheckPlayerstateEvents` keep the follow-reset, reward, event, and duck-smoothing order. |
| `CG-A3a` | `CG-A` | Boundary-only | [`cg_main.c`](../../src/code/cgame/cg_main.c), [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`cg_screen.c`](../../src/code/cgame/cg_screen.c), [`cg_local.h`](../../src/code/cgame/cg_local.h), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md) | Closed on `2026-04-05`. Cgame now owns the next browser direct-owner boundary slice for overlay lookup/open/close, preset-label refresh, widget-position refresh, focus clear/set, hover enter/leave, mouse-over state, mouse-move dispatch, and cursor walking, and the live scoreboard-cache plus spectator `joingame_menu` seams route through those owners while the verified shared `ui_shared.c` runtime remains underneath. |
| `CG-A3b` | `CG-A` | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md) | Closed on `2026-04-05`. `cg_newdraw.c` now owns the adjacent browser runtime-state and simple script-owner slice for rect hit tests, name or group lookup, widget lookup, script dispatch, enable/show cvar gating, show or hide item groups, and the `show` / `hide` / `open` / `conditionalopen` / `close` / `toggle` / `setfocus` verb wrappers, while the focus and hover bodies route through those cgame-owned helpers instead of thin `Item_*` pass-throughs. |

### `CG-A` Browser / Widget / Overlay Runtime

| ID | Priority | Type | Evidence | Current state | Exit criteria |
| --- | --- | --- | --- | --- | --- |
| `CG-A1` | Completed 2026-04-05 | Behavioral | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`cg_draw.c`](../../src/code/cgame/cg_draw.c), [`cg_screen.c`](../../src/code/cgame/cg_screen.c), [`cg_local.h`](../../src/code/cgame/cg_local.h), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `docs/reverse-engineering/cgame-mapping.md:449-528` | Cgame now owns the retail overlay-root lifecycle, captured-overlay key dispatch, widget-state allocation, and root/widget draw dispatch surface through explicit browser runtime wrappers, while the shared `ui_shared.c` capture pump and control painters remain the verified implementation underneath those owners. | Completed. |
| `CG-A2` | Completed 2026-04-05 | Transport | [`cg_main.c:3872-4074`](../../src/code/cgame/cg_main.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `docs/reverse-engineering/cgame-mapping.md:502-515` | Cgame now owns explicit browser bootstrap wrappers for overlay init, item/menu keyword-hash rebuilds, and item/menu parse entry points, while the shared `ui_shared.c` parser bodies remain the verified implementation underneath. | Completed. |
| `CG-A3` | Completed 2026-04-05 | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`cg_main.c`](../../src/code/cgame/cg_main.c), [`cg_local.h`](../../src/code/cgame/cg_local.h), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py) | The remaining browser leaf-owner seam is now source-owned too: cgame exposes the retail-named list metrics, draw leaf painters, fade/transition/orbit and advert verbs, overlay activation/cinematic shutdown, the remaining control-key and capture wrappers, and the cross-file preset/layout refresh bridge used by the live open path, while the verified `ui_shared.c` bodies stay underneath as shared implementations. | Completed. |

### `CG-B` Configstring / Scoreboard / Playerinfo Transport

| ID | Priority | Type | Evidence | Current state | Exit criteria |
| --- | --- | --- | --- | --- | --- |
| `CG-B1` | Completed 2026-04-05 | Transport | [`g_main.c`](../../src/code/game/g_main.c), [`cg_servercmds.c`](../../src/code/cgame/cg_servercmds.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `docs/reverse-engineering/cgame-mapping.md:784-788` | qagame now mirrors `g_teamSizeMin` through a serverinfo-facing `teamsize` alias, and `CG_ParseServerinfo` consumes that live key directly so the player-count ownerdraw cap no longer depends on the old best-effort dual-key parse. | Completed. |
| `CG-B1a` | Completed 2026-04-05 | Transport | [`bg_public.h`](../../src/code/game/bg_public.h), [`g_main.c`](../../src/code/game/g_main.c), [`g_match_config.c`](../../src/game/g_match_config.c), [`cg_servercmds.c`](../../src/code/cgame/cg_servercmds.c), [`tests/test_ui_menu_files.py`](../../tests/test_ui_menu_files.py), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py) | Retail slot `0x2A2` is now source-owned as the dedicated player-cylinder transport: qagame publishes `g_playerCylinders` there, cgame consumes it through `CG_ParsePlayerCylindersConfigString`, and factory titles stay on the serverinfo-backed `g_factoryTitle` path while `CS_FACTORY_FLAGS` retains the numeric factory mask. | Completed. |
| `CG-B2` | Completed 2026-04-05 | Transport | [`cg_servercmds.c:2700-2764`](../../src/code/cgame/cg_servercmds.c) | `CG_ParsePlayerAppearanceConfigString` now treats `CS_PLAYER_APPEARANCE` as the sole retail transport after the matching `qagame` publisher landed, and the older `CS_SERVERINFO` mirror has been removed. | Completed. |
| `CG-B3` | Completed 2026-04-05 | Boundary-only | [`cg_draw.c`](../../src/code/cgame/cg_draw.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py) | `CG_DrawADRoundScoreboard` is now a direct source-owned warmup HUD helper in `cg_draw.c`, restoring the retail 240x48 round grid, active-team and active-round highlights, and the dedicated A/D round-history strip instead of folding that path into the wider banner-only flow. | Completed. |
| `CG-B4` | Completed 2026-04-05 | Transport | [`cg_servercmds.c:2672-2692`](../../src/code/cgame/cg_servercmds.c), [`cg_servercmds.c:3426-3463`](../../src/code/cgame/cg_servercmds.c), [`cg_servercmds.c:3512-3568`](../../src/code/cgame/cg_servercmds.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py) | `CG_ParseArmorTieredConfigString` is source-owned, fed from `CS_SERVER_SETTINGS_INFO_A`, and regression-guarded against drift back into `CG_ParseServerinfo` or broader fallback parsing. | Completed. |
| `CG-B5` | Completed 2026-04-05 | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py), `docs/reverse-engineering/cgame-mapping.md:308-314` | The remaining placement scorebox ping, total-accuracy, per-weapon, pickup, and medal metrics now route through their dedicated retail-named ownerdraw wrappers in `cg_newdraw.c`, clearing the last non-browser Appendix B direct-owner gap outside the browser runtime while preserving the shared placement-text builder underneath. | Completed. |

### `CG-C` Event Payload / Prediction / Snapshot Bridges

| ID | Priority | Type | Evidence | Current state | Exit criteria |
| --- | --- | --- | --- | --- | --- |
| `CG-C1` | Completed 2026-04-05 | Transport | [`q_shared.h`](../../src/code/game/q_shared.h), [`msg.c`](../../src/code/qcommon/msg.c), [`g_utils.c`](../../src/code/game/g_utils.c), [`g_combat.c`](../../src/code/game/g_combat.c), [`g_client.c`](../../src/code/game/g_client.c), [`g_main.c`](../../src/code/game/g_main.c), [`g_team.c`](../../src/code/game/g_team.c), [`g_weapon.c`](../../src/code/game/g_weapon.c), [`cg_event.c`](../../src/code/cgame/cg_event.c), [`tests/test_cgame_event_transport_parity.py`](../../tests/test_cgame_event_transport_parity.py) | The shared entity-state seam now mirrors the recovered retail payload slots directly for single-recipient temp entities plus global-team-sound transport, including the restored `0xE0` event-data slot and the retail award/infected qagame emitters. | Completed. |
| `CG-C2` | Completed 2026-04-05 | Validation | [`g_client.c`](../../src/code/game/g_client.c), [`cg_event.c`](../../src/code/cgame/cg_event.c), [`tests/test_cgame_event_transport_parity.py`](../../tests/test_cgame_event_transport_parity.py), [`docs/reverse-engineering/cgame-mapping.md`](../../docs/reverse-engineering/cgame-mapping.md), [`docs/reverse-engineering/qagame-mapping.md`](../../docs/reverse-engineering/qagame-mapping.md) | The remaining Red Rover event-band seam is now closed: qagame emits the survival-bonus broadcast through the retail `EV_GLOBAL_TEAM_SOUND` / `GTS_SURVIVOR_WARNING` `TEAM_BLUE` payload, and cgame already consumes that path directly through the recovered global-team-sound slots. | Completed. |
| `CG-C3` | Completed 2026-04-05 | Validation | [`cg_predict.c`](../../src/code/cgame/cg_predict.c), [`cg_playerstate.c`](../../src/code/cgame/cg_playerstate.c), [`cg_snapshot.c`](../../src/code/cgame/cg_snapshot.c), [`tests/test_cgame_snapshot_parity.py`](../../tests/test_cgame_snapshot_parity.py) | Focused structural coverage now re-validates the remaining retail prediction and transition seam after the direct event-transport cleanup, including the snapshot-only non-predicted handoff into `CG_TransitionPlayerState`, the prediction interpolation fallbacks, reward ordering, crosshair-hit latching, and the final ammo/event/duck transition order. | Completed. |

### `CG-D` Draw / POI / World-Marker / Effects Exactness

| ID | Priority | Type | Evidence | Current state | Exit criteria |
| --- | --- | --- | --- | --- | --- |
| `CG-D1` | Completed 2026-04-05 | Behavioral | [`cg_draw.c:612-641`](../../src/code/cgame/cg_draw.c), [`cg_main.c:798-799`](../../src/code/cgame/cg_main.c), [`tests/test_cgame_poi_parity.py`](../../tests/test_cgame_poi_parity.py), `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:75114-75126`, `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt:84249-84260` | `CG_POIMarkerSizeForOrigin` now records the exact retail hidden-cvar semantics: `cg_poiMinWidth = 16.0`, `cg_poiMaxWidth = 32.0`, and the marker width clamps across the recovered `256..768` distance window. | Completed. |
| `CG-D2` | Completed 2026-04-05 | Boundary-only | [`cg_ents.c`](../../src/code/cgame/cg_ents.c), [`cg_main.c`](../../src/code/cgame/cg_main.c), [`g_items.c`](../../src/code/game/g_items.c), [`tests/test_cgame_displaycontext_parity.py`](../../tests/test_cgame_displaycontext_parity.py) | `CG_DrawItemRespawnTimer` is now source-owned, `CG_Item` invokes it before the later skip-item and hidden-item early exits, and qagame now publishes the respawn deadline or `time2` duration while cgame keeps the retail 25/35/60/120-second class buckets as a compatibility fallback for older emitters. | Completed. |
| `CG-D3` | Completed 2026-04-05 | Boundary-only | Appendix B | Restored the retail big-explode / tracer / juiced helper split by adding direct `CG_SpawnBigExplodeEffects`, `CG_DetonateJuicedPlayer`, and `CG_AddTracerFragmentTrail` owners and routing the juiced event or timeout through the shared detonation wrapper. | Completed. |
| `CG-D4` | Completed 2026-04-05 | Boundary-only | [`cg_newdraw.c`](../../src/code/cgame/cg_newdraw.c), [`tests/test_cgame_spectator_parity.py`](../../tests/test_cgame_spectator_parity.py), `docs/reverse-engineering/cgame-mapping.md:310-314` | `cg_newdraw.c` now exposes the retail competitive scorebox wrappers `CG_DrawScoreValue`, `CG_DrawSpectatorPrimaryStatus`, and `CG_DrawSpectatorSecondaryStatus`; the duel strip no longer backfills the ready slots through the generic placement-text builder. | Completed. |

### `CG-E` Social Sidecar / Native Export / Command Overlay

| ID | Priority | Type | Evidence | Current state | Exit criteria |
| --- | --- | --- | --- | --- | --- |
| `CG-E1` | Completed 2026-04-05 | Transport | [`cg_main.c`](../../src/code/cgame/cg_main.c), [`tests/test_cl_console_cgame_parity.py`](../../tests/test_cl_console_cgame_parity.py), `docs/reverse-engineering/cgame-mapping.md:241-249` | The committed retail corpus never materializes a non-zero producer for `0x10A42400`: the player parser rebuilds only the identity-word pair plus avatar cache, and the recovered host overlay consumer ignores the transport word. Source now preserves that observed zero discriminator explicitly in `CG_CopyClientIdentity`. | Completed. |
| `CG-E2` | Completed 2026-04-05 | Transport | [`cg_consolecmds.c:337-363`](../../src/code/cgame/cg_consolecmds.c), [`cg_main.c:4473-4525`](../../src/code/cgame/cg_main.c), [`cg_servercmds.c:4323-4336`](../../src/code/cgame/cg_servercmds.c), [`cl_cgame.c:1690-1729`](../../src/code/client/cl_cgame.c), [`tests/test_cgame_scoreboard_social_parity.py`](../../tests/test_cgame_scoreboard_social_parity.py) | `clientmute`, scoreboard social icons, and muted-chat suppression now all route through the reconstructed identity-backed native mute imports, while the host-side cgame import slab keeps mute state in a 64-bit identity set rather than a client-slot authority cache. | Completed. |
| `CG-E3` | Completed 2026-04-05 | Behavioral | [`cg_consolecmds.c:506-560`](../../src/code/cgame/cg_consolecmds.c), [`bg_public.h:257-265`](../../src/code/game/bg_public.h), `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt:5024-5036` | `CG_ReadyUp_f` now uses the recovered retail `PM_INTERMISSION` discriminator instead of the earlier `g_training` / tutorial configstring proxy, while keeping the retail-style warmup-window and spectator checks intact. | Completed. |
| `CG-E4` | Completed 2026-04-05 | Boundary-only | Appendix B | Retail announcer and timer-format helpers are now source-owned, and the remaining direct-owner gap in the client-model preview plus packed player-color leaves has been closed by restoring the full 3D `CG_DrawClientModelPreview` scene alongside the direct `CG_ResolveClientModelColorBytes` owner. | Completed. |

### `BG-A` Movement / Jump / Step / Air-Control

| ID | Priority | Type | Evidence | Current state | Exit criteria |
| --- | --- | --- | --- | --- | --- |
| `BG-A2` | Completed 2026-04-05 | Boundary-only | `docs/reverse-engineering/qagame-mapping.md:419-423`, [`bg_pmove.c:996-1095`](../../src/code/game/bg_pmove.c), [`bg_slidemove.c:516-560`](../../src/code/game/bg_slidemove.c) | The current merged `PM_ApplyStepJump` path is now documented and test-backed as behaviorally equivalent to the adjacent retail leaves, including the rechecked general gate, crouch-clearance branch, and shared jump-takeoff body. | Completed. |
| `BG-A3` | Completed 2026-04-05 | Boundary-only | `references/symbol-maps/qagame.json` comment for `PM_StepSlideMove`, [`bg_slidemove.c:436-575`](../../src/code/game/bg_slidemove.c) | `PM_StepSlideMove` remains the only public movement-step boundary, while `PM_StepSlideMoveWithStepHeight` stays private and is validated at the stock 22-unit step height through the public supported or unsupported air-step fixtures. | Completed. |
| `BG-A4` | Low | Validation | [`bg_pmove.c`](../../src/code/game/bg_pmove.c), [`bg_slidemove.c`](../../src/code/game/bg_slidemove.c) | Closed 2026-04-05: focused pytest fixtures now cover jump timing, circle-strafe friction, step-jump gating, unsupported air-step suppression, and double-jump reuse across the shared movement seam. | Completed. |

#### 2026-05-20 BG Pmove Symbol Re-Audit

The qagame and cgame Ghidra rows for the shared pmove tail remain a one-to-one source island: qagame `FUN_10031920` / cgame `FUN_10005df0` map to `PM_FinishWeaponChange`, qagame `FUN_10031990` / cgame `FUN_10005e60` map to `PM_Weapon`, and qagame `FUN_1006f290` maps to the server-only `FireWeapon` dispatcher. The HLIL in both client and game modules clears playerState offset `+0xe0` when a new weapon is raised, then `PM_Weapon` increments that same slot for WP_CHAINGUN while firing and drains it on release.

Source now names that shared slot as `STAT_CHAINGUN_SPINUP`; `PM_FinishWeaponChange` resets it, `PM_Weapon` owns the retail 0..1000 spin accumulator and below-cap doubled reload-time path, and `g_weapon.c::FireWeapon` derives chaingun spread from the recovered stat rather than from `weaponTime`. Focused structural and executable coverage lives in [`tests/test_pmove_helper_parity.py`](../../tests/test_pmove_helper_parity.py), [`tests/test_pmove_movement_fixtures.py`](../../tests/test_pmove_movement_fixtures.py), and [`tests/test_game_weapon_parity.py`](../../tests/test_game_weapon_parity.py).

The same round tightened the symbol-map notes for nearby non-weapon edges: `PM_FootstepForSurface` records the noFootsteps plus no-step/metal/snow/wood/default branches, `PM_CrashLand` records the gib-health fall-event gate and double-jump latch clear, `PM_WaterEvents` records the PM_DEAD head-water suppression plus invulnerability clear suppression, and `PmoveSingle` records the command-to-playerState mirrors after the PMF_NO_MOVE early return and before the movement dispatch.

The follow-up symbol pass aligned the cgame step-jump helper names with the qagame/source names: cgame `0x10002790`, `0x10002990`, and `0x100029E0` now map to `PM_ApplyJumpTakeoff`, `PM_CanCrouchStepJump`, and `PM_CanStepJump`, matching qagame `0x1002E2C0`, `0x1002E4C0`, and `0x1002E510`. `PM_Friction` symbol prose now also records the recovered crouch-slide, diagonal circle-strafe, and PM_FREEZE/PMF_SCOREBOARD drop-multiplier branches shared by both binaries.

The step-jump source follow-up rechecked qagame `0x1002EFE0` and cgame `0x100034B0` against the Ghidra `PM_StepSlideMove` decompile. Source now uses the retail `cmd.serverTime - jumpTime >= jumpTimeDeltaMin` delay check for the step-jump gates, rechecks `PM_CanStepJump` only for the general launch, and lets the crouch fallback run through `PM_CanCrouchStepJump` plus the shrunken-box clearance trace even when the general upmove gate rejects the command. The cgame symbol signature was also corrected back to the one-argument `PM_StepSlideMove(qboolean gravity)` boundary shown by HLIL.

The jump-release source follow-up rechecked qagame `0x1002E510` / `0x1002E590` and cgame `0x100029E0` / `0x10002A60` against the compact pmove-setting parse order. Both binaries consult the recovered `autoHop` slot for held-jump release bypasses and do not use the following `bunnyHop` slot for that decision, so the shared source now keeps bunny-hop tuning out of `PM_ShouldRequireJumpRelease` and `PM_ShouldRequireStepJumpRelease`.

The jump-takeoff velocity follow-up rechecked qagame `0x1002E2C0` and cgame
`0x10002790` against the adjacent step-jump callers. Source now keeps the
vertical velocity decision inside the shared takeoff preparation: normal chain
jumps use the retail gradient scaler, PMF_AIR_CONTROL switches to the additive
chain/step branch keyed by `pmove_JumpVelocityTimeThresholdOffset`, and
ramp-jump accumulation applies to vertical velocity before the max clamp rather
than using the old source-only planar boost.

The 2026-05-22 corrective step/chain audit rechecked the same takeoff leaf
against the `PM_StepSlideMove` latches. The normal step-jump path now feeds the
step-aware additive branch just like the crouch-step fallback, PMF_AIR_CONTROL
overrides `pmove_ChainJump` mode `0`, the air-control addend fades across the
post-offset window to the base threshold, and the max clamp applies after both
plain additive and ramp-accumulated takeoff velocity.

The air-move follow-up rechecked qagame `0x1002FCB0` and cgame `0x10004180` against the current source and tests. The mode-specific airstop, strafe, and `pm_wishspeed` handling belongs to `PM_AirMove` before the generic `PM_Accelerate` call, while `PM_AirControl`, `PM_StepSlideMove(qtrue)`, `PM_InvulnerabilityMove`, and the trailing `PMF_DOUBLE_JUMP` probe remain in the same tail order in both binaries.

The neighboring walk-move symbols now call out the same retail handoff shape: `PM_WalkMove` owns the early `PM_ShouldUseInvulnerabilityMove` branch through `PM_StepSlideMove(qfalse)` and `PM_InvulnerabilityMove`, then continues through jump handling, crouch-slide timer refresh, duck/wade speed clamps, slick/knockback acceleration selection, and the final grounded step move. The cgame `PM_InvulnerabilityMove` prose was also refreshed to remove the old minimal-stub caveat now that the reconstructed source owns the retail activation/timer/animation behavior.

The invulnerability timer follow-up rechecked qagame `0x1002FA80` and cgame `0x10003F50` against the committed HLIL. The dispatch gate now preserves the retail exact-zero stale state (`STAT_PLAYER_ITEM_RECHARGE != 0 && STAT_PLAYER_ITEM_TIME == 0`) instead of a broader signed range test, and the holdable slot clear is tied to the timer-collapse block only when the recharge-rate stat is zero. Structural coverage in [`tests/test_invulnerability_move_parity.py`](../../tests/test_invulnerability_move_parity.py) and executable fixture coverage in [`tests/test_pmove_movement_fixtures.py`](../../tests/test_pmove_movement_fixtures.py) pin the three edge cases: exact zero with a recharge rate, negative decay with a recharge rate, and zero with no recharge rate.

The 3D movement leaf sweep rechecked water, ladder, fly, and noclip paths against both pmove islands. `PM_WaterMove` now records the shared `PM_BuildWishMove3D` vector builder plus the idle `-60` sink fallback, `PM_LadderMove` records the explicit `0.66 * speed` climb/descent cap, `PM_FlyMove` records the spectator and flight-powerup dispatch into the shared 3D wish-vector path, and `PM_NoclipMove` records the default-viewheight plus 1.5x friction/no-trace integration path. The 2026-05-22 fixture follow-up adds executable coverage for the water-jump solid-lip/clearance sequence, the water idle sink, the `MASK_PLAYERSOLID` + `SURF_LADDER` probe, and the ladder vertical clamp.

The same dispatcher-tail audit rechecked `PM_Weapon`, `PM_Animate`, and the
`PmoveSingle` tail calls against qagame/cgame evidence. Production source was
unchanged, but the pmove fixture harness now pins `PM_Animate` directly:
gesture wins over simultaneous voice buttons, queues `EV_TAUNT`, and uses
`TIMER_GESTURE`, while voice commands follow the retail
getflag/guardbase/patrol/followme/affirmative/negative order with the 600 ms
timer and no predictable event. Active torso timers suppress both paths.

The following torso-idle pass rechecked qagame `0x1002DB80` and cgame
`0x10002050`. Source stayed unchanged, and executable fixtures now cover
`PM_TorsoAnimation` restoring `TORSO_STAND2` for a ready gauntlet,
`TORSO_STAND` for other ready weapons, leaving active torso timers untouched,
returning for non-ready weapon states, and inheriting the `PM_DEAD` no-start
gate through `PM_ContinueTorsoAnim` / `PM_StartTorsoAnim`.

The timer-tail pass then rechecked qagame `0x10031E30` and cgame `0x10006300`.
Source again matched the retail helper, and the fixture harness now covers
`PM_DropTimers` partial `pm_time` decay, exact/overrun expiry, `PMF_ALL_TIMES`
clearing without disturbing unrelated flags, independent legs/torso timer
clamps, and the crouch-slide ground-plane decay gate.

The queue-helper pass rechecked qagame `0x1002DAF0` / `0x1002DB20` and cgame
`0x10001FC0` / `0x10001FF0`. Source stayed unchanged, and executable fixtures
now cover `PM_AddEvent` writing zero event parms through the two-slot
predictable-event wrap plus `PM_AddTouchEnt` skipping `ENTITYNUM_WORLD`,
deduplicating touched entities, and enforcing the `MAXTOUCH` cap.

The low-level animation pass rechecked qagame `0x1002DB60` /
`0x1002DBE0` / `0x1002DC20` and cgame `0x10002030` / `0x100020B0` /
`0x100020F0`. Source stayed unchanged, and executable fixtures now cover
torso toggle-bit writes, `PM_DEAD` suppression, legs high-priority timer
no-ops, current-animation no-ops, torso timer no-ops, and the
`PM_ForceLegsAnim` timer clear before the live/dead start gate.

The command/vector math pass rechecked qagame `0x1002DC50`,
`0x1002DEF0`, `0x1002E070`, and `0x1002E1F0` against cgame
`0x10002120`, `0x100023C0`, `0x10002540`, and `0x100026C0`. Source stayed
unchanged, and executable fixtures now cover `PM_ClipVelocity` inward/outward
overbounce branches, `PM_Accelerate` clamp and overspeed no-op behavior,
`PM_CmdScale` zero/axial/2D/3D input scaling, and `PM_SetMovementDir`'s full
0..7 command ring plus idle side-strafe diagonal snaps.

The ground-contact and footstep follow-up rechecked qagame `0x10030BE0`/`0x10030DA0`/`0x10030ED0`/`0x10031140`/`0x100314D0` and cgame `0x100050B0`/`0x10005270`/`0x100053A0`/`0x10005610`/`0x100059A0` against the Ghidra/HLIL pmove islands. `PM_CorrectAllSolid` now records the 0.25-unit recovery trace and groundEntityNum clearing, `PM_GroundTraceMissed` records the 64-unit lift probe plus forward/back jump animation split, `PM_GroundTrace` records the kickoff/steep/land timer/touch-entity edges without a replicated ground-trace history cache, `PM_SetWaterLevel` records the exact `MASK_WATER` sample heights, and `PM_Footsteps` records the airborne invulnerability, swim, idle-bob, ducked-suppression, and splash/swim event split.

The ground-trace source follow-up rechecked cgame `0x100053A0` and qagame `0x10030ED0` against the surrounding `PM_CheckDuck` offsets. Source now removes the reconstruction-only `groundTraceHistory*` and `groundTraceLatest*` playerState fields plus their delta replication, keeping only the retail `groundEntityNum` playerState store while ramp-jump reconstruction reads the current frame's `pml.groundTrace` normal.

The playerState wiring follow-up rechecked the retail engine netfield table plus qagame `0x10031FA0` and cgame `0x10006470`. Source now keeps `clientNum` at `0x88`, restores the replicated `location` byte at `0x8c`, stores the command mirrors as signed bytes at `0x1dc..0x1de`, and moves local-only sidecars after the retail replicated prefix. The same pass moves the progress-backed holdable timer into `stats[10]`, `stats[11]`, and `stats[12]`, matching the HLIL offsets `+0xe8`, `+0xec`, and `+0xf0`, and adds executable delta-codec coverage for both the byte mirrors and timer stat triplet.

The 2026-05-22 wiring pass closed the remaining pmove-settings transport
divergence called out by cgame `0x10048F30`. The server now publishes the
retail compact 33-token pmove core in `CS_PMOVE_SETTINGS`, ordered as the
Ghidra parser consumes it: air acceleration, air-step friction/steps,
auto/bunny/chain jump flags, jump timing and velocity terms, no-player-clip,
ramp/step jump controls, strafe/walk friction and acceleration, water scales,
weapon raise/drop timing, and wishspeed. The source cgame parses that compact
form first, keeps a JSON fallback for older reconstruction artifacts, and only
uses trailing compact extension tokens for source-only prediction knobs such as
`airControl`, `crouchSlide`, `doubleJump`, and Quad Hog HUD metadata that
retail did not consume through the compact core. A later `PM_FlyMove` recheck
confirmed that retail registers `g_flightThrust` with a `1200` default in
qagame's cvar table but does not feed that cvar into either shared pmove
flight leaf, so source now keeps the cvar registration for parity while
removing the old pmove settings transport and movement override.

The pmove cvar reconstruction pass then cross-checked the qagame retail cvar
table at `0x1008F7C4..0x1008FB20`. Source registration in `g_pmove.c` now keeps
the recovered defaults and cvar flag groups for all 36 `pmove_*` entries instead
of registering the split-out reconstruction cvars with flag `0`; the compact
transport and cgame parser continue to consume the resulting cached settings.
The subsequent callback/cache recheck walked retail `G_InitPublishedCvarState`
and `G_UpdateCvars`, confirming the pmove slab's callback-backed mirrors. Source
now preserves the callback/no-callback split for the profile toggles and clamps
the published `pmove_velocity_gh`, `pmove_JumpVelocityTimeThreshold`, and
`pmove_JumpVelocityTimeThresholdOffset` values to the retail `0.001` minimum
before cgame prediction consumes them.
The follow-up grapple-speed audit separated the two similarly named hook
surfaces: retail `PM_GrappleMove` consumes the `pmove_velocity_gh` cache, while
`g_velocity_gh` defaults to `1800` for the projectile-speed path and custom
settings. Source now mirrors that split instead of letting `g_velocity_gh`
mask the dedicated pmove pull speed.
The subsequent full-name sweep keeps `pmove_fixed` and `pmove_msec` classified
as legacy fixed-timestep controls rather than QL factory-managed movement
tuning entries. They remain registered in the game/cgame cvar tables with
defaults `0` and `8`, the server-side copy carries `CVAR_SYSTEMINFO`, both
prediction paths clamp `pmove_msec` to `8..33`, and the shared `Pmove` outer
loop consumes the resulting struct fields to choose `pmove_msec` slices or the
normal 66 ms chunk cap.

The same evidence round rechecked qagame `ClientSpawn` at `0x1003BC30` and the
shared `PmoveSingle` entrypoints at qagame `0x10031FA0` / cgame `0x10006470`.
Retail seeds `PMF_CROUCH_SLIDE`, `PMF_DOUBLE_JUMP`, and `PMF_AIR_CONTROL`
from the active movement globals during spawn, then `PmoveSingle` consumes
those replicated profile bits instead of deriving or clearing them from the
settings block every frame. Source now mirrors that ownership through
`G_PmoveApplyProfileFlags`, keeps crouch-slide friction keyed by the replicated
flag, and leaves air double-jump acceptance to the profile flag plus the
existing `doubleJumped` latch.

The follow-up dispatcher audit rechecked the same shared `PmoveSingle` body at
qagame `0x10031FA0` / cgame `0x10006470` and closed the dead-player collision
edge at the top of the frame. Retail clears `CONTENTS_BODY` from the pmove trace
mask only when `STAT_HEALTH <= 0` and the replicated `PW_INVULNERABILITY` slot
is clear; invulnerable dead players keep body collision through that early gate.
Source now mirrors the paired health/powerup condition and has executable
coverage for both tracemask outcomes.

### `BG-B` Shared Pickup / Trajectory / Boundary Cleanup

| ID | Priority | Type | Evidence | Current state | Exit criteria |
| --- | --- | --- | --- | --- | --- |
| `BG-B1` | Completed 2026-04-05 | Validation | `references/symbol-maps/qagame.json` comments for `BG_PlayerTouchesItem`, `BG_CanItemBeGrabbed`, and `BG_FindItemForPowerup`; direct scan found `0` missing normalized names | Closed 2026-04-05: structural and executable fixtures now cover the mapped powerup lookup seam, the retail pickup-touch envelopes, and representative weapon or health pickup gates in [`tests/test_bg_misc_helper_parity.py`](../../tests/test_bg_misc_helper_parity.py), [`tests/test_bg_itemlist_indexes.py`](../../tests/test_bg_itemlist_indexes.py), [`tests/bg_misc_validation_harness.c`](../../tests/bg_misc_validation_harness.c), and [`tests/test_bg_misc_validation_fixtures.py`](../../tests/test_bg_misc_validation_fixtures.py). | Completed. |
| `BG-B2` | Completed 2026-04-05 | Boundary-only | `docs/reverse-engineering/qagame-mapping.md:568-579`, [`bg_misc.c`](../../src/code/game/bg_misc.c), [`tests/test_bg_misc_runtime_parity.py`](../../tests/test_bg_misc_runtime_parity.py) | The shared pickup/touch helpers remain a deliberate verified source merge; no current retail evidence requires extra boundary splitting beyond the existing source-owned family. | Completed. |

#### 2026-05-19 BG Misc Armor Pickup Re-Audit

The qagame `FUN_1002ced0` and cgame `FUN_10001560` decompiles both split the `IT_ARMOR` pickup branch on the armor-tiered cvar parameter: classic armor returns `STAT_ARMOR < STAT_MAX_HEALTH * 2` directly from `BG_CanItemBeGrabbed`, while the nonzero tiered path enters the recovered `BG_CanGrabArmorItem` leaf. That leaf owns only the retail 100/50/25 quantity thresholds and does not consult `PW_SCOUT` or `STAT_PERSISTANT_POWERUP`.

Source now mirrors that wiring in [`bg_misc.c`](../../src/code/game/bg_misc.c), with structural coverage in [`tests/test_bg_misc_helper_parity.py`](../../tests/test_bg_misc_helper_parity.py) and executable coverage in [`tests/bg_misc_validation_harness.c`](../../tests/bg_misc_validation_harness.c), [`tests/test_bg_misc_validation_fixtures.py`](../../tests/test_bg_misc_validation_fixtures.py), and [`tests/test_bg_misc_runtime_parity.py`](../../tests/test_bg_misc_runtime_parity.py). The runtime fixtures now exercise classic armor capacity with Scout present plus the tiered red, yellow, and green armor boundaries.

The follow-up pass corrected the qagame symbol map label for `0x1002CE00` from a stale health-helper name to `BG_CanGrabArmorItem`. The Binary Ninja HLIL at that address recovers the exact tier thresholds (`armor * 0.75 <= 99.0`, `armor * 0.66 <= 50.0`, and `armor * 0.75 <= 50.0`), and [`tests/test_bg_misc_validation_fixtures.py`](../../tests/test_bg_misc_validation_fixtures.py) now also covers `BG_ApplyArmorPickup`, `BG_UpdateArmorTierFromCurrentArmor`, and `BG_GetArmorRegenTarget` through the reusable C harness.

The same round rechecked `BG_PlayerTouchesItem` in both qagame (`FUN_1002cd30`) and cgame (`FUN_100013c0`) Binary Ninja HLIL. The corrected qagame symbol-map prose now records the exact shared touch envelope: `+/-36` horizontal bounds, `-50` lower vertical tolerance, a `29` unit normal upward window, and a `64` unit upward window for red, blue, and neutral team flags.

The subsequent trajectory audit found the remaining shared `bg_misc` mismatch: qagame `FUN_1002d210` / `FUN_1002d3e0` and cgame `FUN_100018a0` / `FUN_10001a70` both keep a type-`6` `TR_QL_ACCEL` trajectory path. Source now names that enum value and mirrors the retail formula by reading the extra acceleration scalar from the dword immediately after `trDelta`, while preserving the current 36-byte `trajectory_t` source layout.

The item-helper follow-up rechecked the top-of-file weapon/holdable tag bridges and the cgame `FUN_10001170` item lookup leaf. No new source behavior mismatch was isolated; the cgame symbol map now uses the public `BG_FindItemByTypeAndTag` name consistently with qagame/source, and helper tests pin the retail HMG item-tag append plus the invulnerability holdable tag gap.

The prediction-state follow-up corrected the cgame `0x10001560` pickup-gate prose from stale handler-table wording to the direct item-type switch recovered in qagame/source. The same pass added executable fixtures for `BG_AddPredictableEventToPlayerstate`, `BG_TouchJumpPad`, and `BG_PlayerStateToEntityState` event projection, plus a structural guard that keeps the `eventnames[]` debug table aligned with `entity_event_t` through `EV_NEW_HIGH_SCORE = 99`.

The next playerstate-projection follow-up kept production source unchanged after rechecking the qagame/cgame `BG_PlayerStateToEntityState` symbols against the source bridge. The reusable harness now covers external-event precedence, spectator/intermission/gib visibility, `EF_DEAD` projection, number/clientNum mirroring, weapon and ground projection, loop sound and generic payload copying, animation fields, and powerup-bit packing.

The top-helper follow-up rechecked the remaining source-side bridges above `bg_itemlist`: weapon names, weapon max ammo, ammo-pack quantities, handicap scalar lookups, weapon/item tag roundtrips, and holdable/item tag roundtrips. No new retail mismatch was isolated; the reusable C harness now exercises the local enum to retail tag mapping directly, including Heavy Machinegun as local `WP_HEAVY_MACHINEGUN` but retail item tag `14`, and the intentional empty holdable tag `5` before invulnerability tag `6`.

The lookup/stat-table follow-up expanded that coverage from representative samples to the full recovered weapon-stat table. The harness now checks every shared weapon row against the qagame HLIL ammo pickup/max-stack evidence plus the source-side handicap scalar table, and separately exercises pickup-name, classname, and type/tag item lookup paths for the qagame `BG_FindItem`, `BG_FindItemByTypeAndTag`, and cgame `BG_FindItemByTypeAndTag` mappings.

The small-policy-helper follow-up kept production source unchanged after confirming `BG_PlayerHasPersistantPowerup`, `BG_GetArmorUpperBound`, `BG_GetHealthUpperBound`, and `BG_ClearArmorTierIfEmpty` are source-side helper splits rather than standalone nearby retail function boundaries in the qagame/cgame corridors. The C harness now exercises persistent-powerup guard behavior, health/armor upper bounds, and armor-tier clearing for stripped or non-tiered states.

## Recommended Execution Order

None currently. Re-open this list only when a new retail-backed writable parity seam is discovered.

## Appendix A: Browser / Overlay Families Missing Direct `cgame` Owners

No remaining browser/overlay direct-owner gaps are currently tracked in the writable `cgame` tree. The earlier `CG-A3` families are now source-owned, while the shared `ui_shared.c` implementations remain the verified runtime underneath those cgame wrappers.

## Appendix B: Remaining Non-Browser Direct-Owner Gaps In `cgame`

These are the remaining mapped retail names that still do not have direct writable source owners. Keep them in the owning lanes listed here.

| Lane | Missing direct-owner names |
| --- | --- |
| `CG-B` | None |
| `CG-D` | None |
| `CG-E` | None |
| `CG-A` | None |
| `CG-A` or `CG-E` after `CG-A1` | None |
| `CG-A` or `CG-B` after scoreboard parity | None |
