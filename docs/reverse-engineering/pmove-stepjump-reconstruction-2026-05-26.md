# PMove Step-Jump Reconstruction - 2026-05-26

## Scope

This note maps the Quake Live PMove step-jump seam across qagame, cgame, and
the reconstructed shared source. It focuses on the wiring around
`PM_StepSlideMove`, the general step-jump gate, the crouch-step fallback gate,
the shared jump takeoff leaf, and the server/client tuning transport that feeds
those paths.

## Evidence Inventory

Primary retail binary: `qagamex86.dll`.

Companion cross-check binary: `cgamex86.dll`.

Committed evidence used:

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/symbol-maps/qagame.json`
- `references/symbol-maps/cgame.json`

## Retail Address Map

| Retail role | qagame address | cgame address | Reconstructed source |
| --- | ---: | ---: | --- |
| Shared jump takeoff leaf | `0x1002E2C0` | `0x10002790` | `bg_pmove.c::PM_ApplyJumpTakeoff` plus prepare helpers |
| Crouch-step gate | `0x1002E4C0` | `0x10002990` | `bg_slidemove.c::PM_CanCrouchStepJump` |
| General step-jump gate | `0x1002E510` | `0x100029E0` | `bg_slidemove.c::PM_CanStepJump` |
| General jump gate | `0x1002E590` | `0x10002A60` | `bg_pmove.c::PM_CheckJump` / `PM_PrepareJumpTakeoff` |
| Slide move leaf | `0x1002E670` | `0x10002B40` | `bg_slidemove.c::PM_SlideMove` |
| Step-slide wrapper | `0x1002EFE0` | `0x100034B0` | `bg_slidemove.c::PM_StepSlideMove` |

## Observed Facts

`PM_StepSlideMove` owns the step-jump seam. The HLIL calls `PM_SlideMove`, then
does the classic step-up retry, down trace, final velocity/origin selection,
and only then checks step-jump launch eligibility when the final vertical delta
is positive.

The retail down-trace collision clip is not unconditional. After the step retry
is pushed back down, qagame and cgame both compute `velocity dot plane.normal`
and only call `PM_ClipVelocity` when the player is moving into the plane or is
within the small `0.001` near-parallel threshold. A positive separating dot above
that threshold keeps the stepped velocity intact.

Retail also runs a direct trace from the original origin to the stepped endpoint
after the down trace. The stepped origin remains in use either way, but the
trace result gates the step side effects: `pml.stepUp`, air-step friction,
debug `stepped` logging, and the step-jump/crouch-step probes only run when the
direct path is obstructed (`fraction < 1.0`).

The retail public step-slide boundary has one argument, `gravity`. The
reconstructed source keeps `PM_StepSlideMove( qboolean gravity )` public and
keeps the configurable `pm_stepHeight` indirection private inside
`PM_StepSlideMoveWithStepHeight`.

The general step-jump gate is checked twice. Retail first calls
`PM_CanStepJump` before the projected support trace, then rechecks it
immediately before the shared takeoff leaf. If the second general check fails,
the crouch branch can still run through `PM_CanCrouchStepJump` and the extra
shrunken-box clearance trace.

The projected support trace beneath the step-jump launch checks both
`!startsolid` and `!allsolid` before accepting a walkable normal. The old source
only tested `allsolid`; the 2026-05-27 step-move reconstruction restored the
paired retail gate.

The general gate uses the compact `autoHop` tuning slot for the held-jump
release bypass. It does not use `bunnyHop`. If the release gate rejects a held
jump or the jump-time delay rejects an otherwise queued jump, the gate clears
`cmd.upmove`.

The crouch-step gate is a distinct leaf. It requires `PMF_DUCKED`, rejects
ground-plane state, rejects descending vertical velocity, and checks
`cmd.serverTime - ps->jumpTime >= pmove_JumpTimeDeltaMin`. It does not require
queued jump input and does not apply the held-jump release gate.

## Latch Mapping

The two step paths set different retail latches before entering the shared
jump takeoff body:

| Latch role | qagame global | cgame global | Set by | Takeoff effect |
| --- | ---: | ---: | --- | --- |
| Normal step-jump velocity selector | `data_1009096c` | `data_10079814` | General step-jump branch | Selects `pmove_StepJumpVelocity` for additive and air-control addends |
| Crouch-step ramp suppression | `data_10090964` | `data_1007980c` | Crouch-step fallback branch | Suppresses ramp-jump accumulation |

This distinction is the important correction from the 2026-05-26 audit. The
crouch-step fallback does not set the normal step-jump velocity selector.
Therefore, in additive mode and in the PMF_AIR_CONTROL additive/fade path,
crouch-step uses `pmove_ChainJumpVelocity`, while normal step-jump uses
`pmove_StepJumpVelocity`. Crouch-step still suppresses ramp accumulation.

The PMF_AIR_CONTROL post-offset branch is intentionally not a smooth fade over
the remaining outer threshold window. Both qagame `0x1002E338..0x1002E378` and
cgame `0x10002808..0x10002848` multiply
`pmove_JumpVelocityTimeThreshold` by `pmove_JumpVelocityTimeThresholdOffset`,
then divide the late-window addend by that offset threshold. With retail
defaults, a chain jump at `400ms` after the previous jump is therefore
`275 + (((300 - 400) / 300) * 110 + 110) = 348.333...`, while `500ms` returns
directly to base jump velocity.

## Tuning Globals

The qagame HLIL global defaults around `0x1008FE7C..0x1008FE98` anchor the
jump takeoff math:

| qagame global | Default | Meaning |
| ---: | ---: | --- |
| `data_1008FE7C` | `110.0` | `pmove_ChainJumpVelocity` |
| `data_1008FE80` | `48.0` | `pmove_StepJumpVelocity` |
| `data_1008FE84` | `275.0` | `pmove_JumpVelocity` |
| `data_1008FE88` | `700.0` | `pmove_JumpVelocityMax` |
| `data_1008FE8C` | `100.0` | `pmove_JumpTimeDeltaMin` |
| `data_1008FE90` | `0.4` | `pmove_JumpVelocityScaleAdd` |
| `data_1008FE94` | `500.0` | `pmove_JumpVelocityTimeThreshold` |
| `data_1008FE98` | `0.6` | `pmove_JumpVelocityTimeThresholdOffset` |

The server owns the cvar mirrors in `g_pmove.c`, serializes the compact
`CS_PMOVE_SETTINGS` payload, and cgame parses the same token order into
`cg_pmoveSettings`. Both server `ClientThink_real`/`SpectatorThink` and cgame
prediction pass a `pmove_settings_t` pointer into shared PMove.

## Source Reconstruction

The current source keeps the retail leaves split where it matters:

- `bg_slidemove.c::PM_CanStepJump` reconstructs the general step-jump gate.
- `bg_slidemove.c::PM_CanCrouchStepJump` reconstructs the crouch fallback gate.
- `bg_slidemove.c::PM_CanPerformCrouchStepJump` owns the 1-unit shrunken-box,
  64-unit downward clearance trace.
- `bg_slidemove.c::PM_StepSlideMoveWithStepHeight` reconstructs the retail
  step-up/down trace seam, including the guarded down-trace clip, the final
  direct-path side-effect gate, and the projected-support `startsolid` reject,
  while preserving the public one-argument wrapper.
- `bg_pmove.c::PM_PrepareStepJumpTakeoff` sets the normal step velocity path.
- `bg_pmove.c::PM_PrepareCrouchStepJumpTakeoff` uses the chain velocity path
  and suppresses ramp accumulation.
- `bg_pmove.c::PM_EvaluateJumpTakeoffVelocity` preserves the retail
  offset-threshold denominator in the PMF_AIR_CONTROL branch.
- `bg_pmove.c::PM_ApplyJumpTakeoff` owns the common state mutation: ground
  clear, jump-held flag, crouch-slide timer clear, `jumpTime`, velocity Z,
  `EV_JUMP`, and forward/back jump animation selection.

## Confidence

High confidence:

- qagame and cgame addresses have matching HLIL structure and matching call
  relationships.
- Ghidra top-function decompiles show the same `PM_StepSlideMove` branch shape
  and latch assignments.
- The cvar names/defaults in the qagame table match the reconstructed server
  cvar cache and the cgame compact parser.

Remaining caveat:

- The committed source intentionally expresses the takeoff leaf through
  prepare helpers instead of byte-for-byte retail globals. This is a source
  reconstruction choice, not a behavior divergence, and is now covered by
  structural and executable fixtures.

## Validation Anchors

Focused tests:

- `tests/test_step_jump_gate_parity.py`
- `tests/test_pmove_helper_parity.py`
- `tests/test_pmove_validation_fixtures.py`
- `tests/test_pmove_movement_fixtures.py`
- `tests/test_pmove_selected_cvar_parity.py`
- `tools/tests/test_pmove_settings_configstring.py`

Useful focused command:

```powershell
python -m pytest tests/test_step_jump_gate_parity.py tests/test_pmove_helper_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_movement_fixtures.py tests/test_pmove_selected_cvar_parity.py tools/tests/test_pmove_settings_configstring.py -q --tb=short
```
