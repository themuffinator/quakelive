# Botlib Qagame Tour Point Resolver Reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame-side tutorial tour-point resolver and spawn
gate:

- `qagamex86.dll:0x1001FEC0`, promoted as `BotResolveTourPoint`;
- `qagamex86.dll:0x10020EC0`, promoted as `BotCanSpawnTourPoint`.

## Retail Evidence

- Binary Ninja HLIL identifies `sub_1001fec0` with the promoted signature
  `BotResolveTourPoint(int currentEntnum, vec3_t origin, vec3_t targetOrigin)`.
- The helper initializes the target-origin output from the zero vector, then
  splits on the current entity number range `0x40..0x3ff`.
- For valid current entities, retail verifies the entity is in use, searches
  `targetname` matches for the current entity's `target`, requires
  `classname == "info_tour_point"`, and rejects the current entity itself.
- For currentless or invalid calls, retail searches `classname ==
  "info_tour_point"` and accepts the first point with spawnflag bit `1`.
- The chosen tour point is traced down by `8192.0` units through the qagame
  trace import and the returned origin is lifted by `16.0`.
- The optional facing target searches the tour point's linked target name and
  copies the first `classname == "info_notnull"` origin to the target output.
- Binary Ninja HLIL for `sub_10020ec0` is a short raw slab scan: index `0x40`
  through `0x3fe`, stride `0x384`, `inuse == 0`, and `freetime + 0x7d0 <=
  level.time`. These offsets line up with `gentity_t.inuse`,
  `gentity_t.freetime`, and the retail entity size.

## Reconstruction

- Added `BotResolveTourPoint` to `src/code/game/ai_dmq3.c`.
- Added small local helpers for tour-point classname tests, floor-origin trace,
  and linked `info_notnull` target-origin resolution.
- Added `BotCanSpawnTourPoint` to `src/code/game/ai_dmq3.c`; it preserves the
  retail `MAX_CLIENTS <= i < ENTITYNUM_MAX_NORMAL` scan rather than using
  `level.num_entities`.
- Added public declarations to `src/code/game/ai_dmq3.h`.
- Promoted the parity gate from mapped-only to source-owned for
  `BotResolveTourPoint` and `BotCanSpawnTourPoint`. A later 2026-06-11 pass
  also promoted `BotSelectTormentTarget` to source-owned.

## Confidence

High for branch structure, classnames, spawnflag bit, trace distance, origin
lift, target lookup, return value, spawn-gate entity index bounds, reuse delay,
and `inuse`/`freetime` predicates. The larger lead/torment tutorial nodes still
remain mapped-only because their complete state-tail layout needs a separate
reconstruction pass.

## Validation

- `tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py`
- `tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py`
