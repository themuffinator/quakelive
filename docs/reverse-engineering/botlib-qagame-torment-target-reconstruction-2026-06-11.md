# Botlib Qagame Torment Target Reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame-side tutorial torment target selector:

- `qagamex86.dll:0x1001F9C0`, promoted as `BotSelectTormentTarget`.

The function is called from the mapped `AINode_Torment_Human` tutorial node at
`0x100119AF` with `500.0f` as the cached-target distance limit.

## Retail Evidence

- Binary Ninja HLIL identifies `sub_1001f9c0` with a 1262-byte function body
  and the promoted signature `int BotSelectTormentTarget(bot_state_t *bs,
  float maxDist)`.
- The cached-target branch reads `bs->enemy` at `+0x196c`, tests 360-degree
  visibility through `BotEntityVisible`, computes distance from `bs->origin`,
  resolves an AAS point area, and checks travel time with flags `0x011C0FBE`.
- The first full scan walks exactly 64 client/entity slots, skips `bs->client`,
  requires a valid AAS entity, copies player state when the entity number is a
  client, requires `pm_type == PM_NORMAL`, rejects entities carrying the
  retail `SVF_BOT` mask, and accepts the nearest directly reachable human.
- The second scan repeats the valid non-bot human filter, then uses
  `trap_AAS_PointReachabilityAreaIndex` with a `trap_AAS_TraceAreas` fallback
  that probes 24 units upward before checking travel time.
- The final scan keeps the valid non-bot human filter but accepts the nearest
  target even if no reachable area was found.

## Reconstruction

- Added local torment-target constants to `src/code/game/ai_dmq3.c`:
  `100000000.0f` best-distance sentinel, 24-unit trace height, 10 traced areas,
  and travel flags `0x011C0FBE`.
- Added source helpers for active-human client-state filtering, non-bot
  candidate filtering, distance measurement, travel-time checks,
  trace-assisted area recovery, and the three candidate acceptance modes.
- Added `BotSelectTormentTarget` to `ai_dmq3.c` and exposed it through
  `ai_dmq3.h`.
- Promoted `BotSelectTormentTarget` from mapped-only to source-owned in the
  deathmatch/setup parity gate.
- Updated the qagame symbol map and adjacent tutorial-tail notes so
  `AINode_Torment_Human` now points at a source-backed leaf helper.

## Confidence

High for function identity, caller relationship, client-slab bounds, cached
target visibility, `PM_NORMAL` first-pass filtering, non-bot human selection,
direct and trace-assisted AAS travel checks, trace height, travel flags, return
values, and fallback order. Remaining uncertainty is limited to retail compiler
stack-local artifacts and the larger still-mapped `AINode_Torment_Human` state
tail that consumes this selector.

## Validation

- `tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py`
- `tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py`

Focused verification:

```text
python -m pytest tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py -q --tb=short
5 passed in 0.20s

python -m pytest tests -k botlib -q --tb=short
205 passed, 1861 deselected in 20.79s
```
