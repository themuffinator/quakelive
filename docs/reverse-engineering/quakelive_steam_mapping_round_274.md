# Quake Live Reverse Engineering Mapping Round 274

## Scope

- Continued the `src/code/cgame/cg_main.c` reconstruction around the cvar registration and update seam.
- Focused on `CG_RegisterCvars`, `CG_UpdateCvars`, the source `cvarTable_t` descriptor, and the recovered retail cvar table slice containing automation and crosshair settings.

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
  - `0x10020BB0` walks the retail table from `data_10076A14` with count `0x127`, using register and bounded-register import slots before registering `model`, `headmodel`, and `cg_version`, then clearing `ui_voteactive`.
  - `0x10020CA0` walks the same table from `data_10076A00` with count `0x127`, calls the cvar update import, compares cached modification state, and triggers the player-refresh path when tracked model/color cvars move.
  - `data_10076AD8` through `data_10076DA0` preserves the recovered `cg_autoAction`, `cg_autoHop`, `cg_autoProjectileNudge`, and crosshair cvar family.

## Source Notes

- Made `cvarTable_t` string fields `const char *`, matching their use as string-literal-backed table metadata.
- Added explicit source headers for `CG_RegisterCvars` and `CG_UpdateCvars`.
- Fixed a stray space-indented brace in the `CG_UpdateCvars` dead-body color branch.
- No retail-online-service behavior was introduced.

## Guardrail

- `tests/test_cgame_displaycontext_parity.py::test_register_cvars_publishes_retail_version_and_vote_reset` now checks:
  - const-correct source table metadata;
  - the latched automation and crosshair cvar entries in source;
  - `CG_RegisterCvars` registration, local-server probe, `cg_version`, `ui_voteactive`, and `ui_votestring`;
  - `CG_UpdateCvars` table update walk and derived setting refresh calls;
  - HLIL register/update loop count `0x127`;
  - the recovered automation/crosshair `.data` cvar names.

## Parity Estimate

- Before: cvar registration/update parity was functionally reconstructed but lightly guarded, about 96%.
- After: table shape, core retail loops, and high-risk Quake Live cvar families are explicitly guarded, about 97%.
