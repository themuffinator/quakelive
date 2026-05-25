# Quake Live Steam Mapping Round 293

Date: 2026-05-25

Scope: core cvar handling, flag cleanup, console `set` guard wiring, and
WebView cvar-change publication.

## Evidence

Primary retail signals:

- `references/analysis/quakelive_symbol_aliases.json` promotes
  `sub_4CCE90 -> Cvar_Set2`, `sub_4CDD30 -> Cvar_GetBounded`,
  `sub_4CE0D0 -> Cvar_Get`, and
  `sub_4F3630 -> QLWebView_PublishCvarChange`.
- HLIL for `sub_4CCE90` shows the retail debug string
  `Cvar_Set2: %s (%s)\n`, the normal missing-cvar path through
  `Cvar_Get(..., 0x80)`, promotion of user-created cvars with the `0x800`
  replicated/protected bit, and a follow-up call to
  `QLWebView_PublishCvarChange`.
- The same `Cvar_Set2` body publishes cvar changes after latched-value updates
  and after immediate value updates, and the retail latch notice is
  `%s will be changed to %s upon restarting.\n`.
- The retail helper at `sub_4CCE40` drops conflicting `CVAR_CHEAT` combinations
  with archive and replicated/protected flags, backed by the string table
  warnings for `CVAR_ARCHIVE` and `CVAR_REPLICATED`.
- HLIL for `sub_4CD680` shows `Cvar_Set_f` refusing initialization-time client
  writes to existing `0x100000` GAMERULE cvars when the client is not fully
  initialized and `dedicated` is false.
- HLIL for `sub_4CE0D0` shows the retail static cvar slot cap at `0x800`
  entries, matching `2048` `cvar_t` slots.

## Source Reconstruction

`src/code/qcommon/cvar.c` now carries the recovered core wiring:

- `MAX_CVARS` is restored to the retail `2048` slot cap.
- `Cvar_UpdateFlagConflicts()` applies the retail `CVAR_CHEAT` conflict cleanup
  for archived and replicated/protected cvars.
- `Cvar_Set2()` uses the retail debug string, promotes non-forced user-created
  cvars with `CVAR_PROTECTED`, publishes created cvars, publishes latched
  values, and preserves the retail write guard surface of ROM, INIT, LATCH, and
  CHEAT only.
- `Cvar_PublishChange()` centralizes the source-visible bridge to
  `CL_WebView_PublishCvarChange()` and forwards the effective latched value
  when the retail path would publish it.
- `Cvar_Set_f()` now refuses `CVAR_GAMERULE` writes during client
  initialization unless the process is dedicated, matching the retail
  `com_fullyInitialized` and `dedicated` gate.
- `Cvar_SetA_f()` re-runs the retail flag cleanup after adding archive status.

`src/code/game/q_shared.h` now exposes `CVAR_GAMERULE` as `0x100000`.

The source still intentionally keeps the repo-owned `sets`, `setu`, and
`setcloud` helpers because they support existing compatibility/profile config
plumbing and are outside this strict core-cvar reconstruction slice.

## Guardrails

`tests/test_cvar_console_write_parity.py` now pins:

- the retail aliases and HLIL/string evidence for `Cvar_Set2`, `Cvar_Get`, and
  `QLWebView_PublishCvarChange`;
- the retail `2048` slot cap and `CVAR_GAMERULE` flag;
- the absence of direct `CVAR_PROTECTED` / `CVAR_VM_CREATED` console write
  guards inside `Cvar_Set2`;
- the created/latched/immediate publish bridge;
- the CHEAT/archive/replicated conflict cleanup warnings; and
- the initialization-time GAMERULE refusal path.

## Parity Movement

Before this round, the scoped core cvar-management lane was about `92%`
source-visible: bounded cvars, config persistence, and basic console write
guards were present, but retail slot sizing, flag conflict cleanup,
user-created replication promotion, latched publish behavior, and the GAMERULE
initialization guard were either absent or only partially represented.

After this round, the scoped lane is about `97%` source-visible and `98%`
mapped.  Remaining deltas are bounded to compatibility-only command helpers and
any future byte-for-byte investigation of small formatting/order differences
outside the reconstructed core call paths.
