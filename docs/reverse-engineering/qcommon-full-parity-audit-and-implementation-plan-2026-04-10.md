# `qcommon` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-21

Scope: `src/code/qcommon/*` against retail `quakelive_steam.exe`, with adjacent ownership checks in `src/code/win32/win_net.c`, `src/common/platform/platform_steamworks.c`, and the current module/runtime validation surface where those owners are required to prove the `qcommon` host contract.

Purpose: publish a strict retail-facing audit for the engine `qcommon` layer, separate the strongly recovered common/filesystem/message/VM host spine from the smaller remaining confidence and validation gaps, and turn the still-open qcommon debt into an execution-ordered closure plan.

## Audit Method And Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Canonical committed evidence used for this audit:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Symbol and mapping support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_21.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_25.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_33.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_34.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_55.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_56.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_57.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_58.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_63.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_65.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_78.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_79.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_84.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_91.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_99.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_107.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_108.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_109.md`
- Writable source under audit:
  - `src/code/qcommon/common.c`
  - `src/code/qcommon/cmd.c`
  - `src/code/qcommon/cvar.c`
  - `src/code/qcommon/files.c`
  - `src/code/qcommon/msg.c`
  - `src/code/qcommon/net_chan.c`
  - `src/code/qcommon/huffman.c`
  - `src/code/qcommon/md4.c`
  - `src/code/qcommon/cm_*.c`
  - `src/code/qcommon/vm.c`
  - `src/code/qcommon/vm_interpreted.c`
  - `src/code/qcommon/vm_x86.c`
  - `src/code/win32/win_net.c`
  - `src/common/platform/platform_steamworks.c`
- Existing validation surface:
  - `tests/test_cvar_parity.py`
  - `tests/test_cvar_alias_console.py`
  - `tests/test_fs_search_paths.py`
  - `tests/test_qcommon_collision_leaf_parity.py`
  - `tests/test_qcommon_vm_fallback_parity.py`
  - `tests/test_client_config_parity.py`
  - `tests/test_platform_services.py`
  - `tests/test_playerstate_replication.py`
  - `tests/test_cgame_event_transport_parity.py`
  - `tests/test_game_module_retail_parity_gate.py`

Method:

1. Start with the owning Windows host binary and the committed metadata/import/export/function inventories.
2. Use promoted aliases and mapping rounds to bound `Com_*`, `FS_*`, `CM_*`, `MSG_*`, `NET_*`, `Netchan_*`, and VM-loader ownership before calling anything a parity gap.
3. Treat exact source-match tests and runtime/module-gate evidence as strong secondary proof when the alias ledger is intentionally sparse for `Cvar_*` or fallback VM code.
4. Distinguish between closed active-runtime owners, source-backed but still heuristic helpers, and compatibility carries that are outside the owning retail Windows binary.

## Committed Corpus Snapshot

Retail `quakelive_steam.exe` metadata still reports:

- function corpus: `5473`
- imports: `351`
- exports: `2`
- promoted analysis symbols: `4377`

Observed qcommon-adjacent alias coverage in `references/analysis/quakelive_symbol_aliases.json`:

- `19` `Com_*` aliases
- `48` `FS_*` aliases
- `8` `CM_*` aliases
- `2` `Cmd_*` aliases
- `29` `MSG_*` aliases
- `9` `NET_*` aliases
- `5` `Netchan_*` aliases
- `10` `Huff_*` aliases

Observed fact:

- the promoted alias ledger is materially strong for the high-traffic `common.c`, `files.c`, `msg.c`, and `net_chan.c` owners
- it is intentionally much sparser for `Cvar_*` and fallback VM backends, which means those lanes depend more heavily on mapping rounds and exact source-match verification

Observed source snapshot:

- tracked `qcommon` files in scope: `27`
- tracked `qcommon` line count in scope: `27907`

Low-confidence file bands from the committed corpus snapshot:

- none inside the strict Windows parity score after `QC-P5`
- `vm_x86.c` remains documented as a bounded compatibility carry beneath the closed `vm.c` host seam

Interpretation:

- `qcommon` is no longer in a broad discovery phase
- the remaining debt is concentrated in the final cross-doc/runtime-evidence tail rather than in an open helper-confidence band

## Validation Snapshot

Validation rerun for this audit on 2026-04-10:

1. `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/qcommon/run_qcommon_runtime_probe.ps1`
2. `python -m pytest tests/test_cvar_parity.py tests/test_cvar_alias_console.py tests/test_fs_search_paths.py tests/test_qcommon_collision_leaf_parity.py tests/test_qcommon_vm_fallback_parity.py tests/test_playerstate_replication.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_cgame_event_transport_parity.py tests/test_qcommon_full_parity_gate.py -q`

Observed result:

- tracked runtime artifact refreshed at `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
- focused qcommon-facing suite plus parity gate: `101 passed`, `2 skipped`

Skip classification:

1. `tests/test_cvar_parity.py`: skipped because the current HLIL corpus does not expose cvar/dvar registration rows to that extractor
2. `tests/test_qcommon_full_parity_gate.py::test_qcommon_full_parity_gate_release_mode`: skipped because `QCOMMON_FULL_PARITY_GATE_ENFORCE=1` was not enabled

Interpretation:

- the current qcommon validation surface is materially stronger than the repo’s top-level ledgers implied before this audit
- the final ledger/runtime-evidence tail is now closed as well, so no open qcommon gap remains inside the audited register

## Current Verified State

The current `qcommon` layer is now a fully closed audited register rather than a partially open active-runtime spine with a remaining helper tail.

Observed source-backed strengths:

1. The main common/bootstrap owners are strongly bounded:
   - `Com_InitHunkMemory`
   - `Com_EventLoop`
   - `Com_Init`
   - `Com_Frame`
   - `Com_WriteConfiguration`
   - `Com_WriteConfig_f`
   - `Com_WriteClientConfig_f`
   - `Com_InitSteamGameServer`
2. The filesystem core is materially strong and carries the key Quake Live deltas now expected by the current repo policy:
   - retail `qzconfig.cfg` / `repconfig.cfg` restart/bootstrap
   - retail-shaped Win32 `fs_homepath` selection through the active Steam user ID
   - `fs_webpath` rewrite and local web fallback reads
   - workshop mount startup with retained item IDs
   - referenced workshop publication via `FS_ReferencedSteamworks()`
   - exact `Sys_LoadDll` root search and `dllEntry` loading contract
3. The network/message spine is strongly recovered:
   - retained Huffman init/setup
   - delta entity and delta playerstate serialization
   - retained Quake Live event payload extension in `msg.c`
   - early `NET_*` / `Netchan_*` addressing, OOB, fragment, and process helpers
4. The structured native DLL loader boundary is in strong shape:
   - required export-table count validation for `ui`, `cgame`, and `qagame`
   - reserved null-slot handling for `cgame`
   - retail restart ordering through `NET_Restart()` and `Com_InitSteamGameServer()`
5. Multiple qcommon-owned Quake Live deltas are already machine-checked:
   - config split and legacy CD-key placeholder handling
   - launcher/resource fallback path ownership
   - workshop publication
   - playerstate/event transport

Observed residual note:

1. `vm_x86.c` remains a deliberate compatibility carry, but it is explicitly bounded beneath the closed `vm.c` host-selection seam instead of remaining an open strict-retail gap.
2. No additional source-owned or ledger-owned qcommon gap remains inside the audited strict-retail register after `QC-P6`.

## Refreshed Strict `qcommon` Parity Estimate

- Strict `qcommon` estimate before `QC-P2`: **87%**
- Strict `qcommon` estimate after `QC-P2`: **90%**
- Strict `qcommon` estimate after `QC-P3`: **92%**
- Strict `qcommon` estimate after `QC-P4`: **95%**
- Strict `qcommon` estimate after `QC-P5`: **98%**
- Strict `qcommon` estimate after `QC-P6`: **100%**

This now closes the final qcommon ledger/runtime-evidence tail on top of the earlier validation, Win32 filesystem startup, collision-leaf, and fallback-VM closures.

Rationale:

1. The high-traffic qcommon owners used by the live engine bootstrap, filesystem, packet transport, and native module loader are already strongly recovered.
2. The former remaining losses were narrow but real:
   - stale cross-doc closure notes plus the last runtime-evidence tail
3. `QC-P6` now closes that tail with reconciled mapping notes plus a tracked runtime bundle, so the audited qcommon register can now honestly claim strict `100%` closure.

Confidence:

- high for the full audited qcommon register, including the final ledger/runtime-evidence lane

## Subsystem Coverage Matrix

| Area | Current status | Writable files in scope | Strongest retail evidence | Audit conclusion |
| --- | --- | --- | --- | --- |
| Common bootstrap, command surface, and config persistence | High parity | `common.c`, `cmd.c`, `cvar.c` | mapping rounds `78`, `79`, `108`, `109`; `tests/test_client_config_parity.py`; `tests/test_platform_services.py` | `Com_Init`, `Com_Frame`, retail config split, `writeClientConfig`, and Steam game-server bootstrap ordering are strongly source-backed. |
| Filesystem core, workshop mounts, and local launcher-resource fallbacks | High parity | `files.c`, `unzip.c`, `qcommon.h` | mapping rounds `34`, `55`, `56`, `91`, `99`; `references/analysis/quakelive_symbol_aliases.json`; retail HLIL around `FS_Startup`; `tests/test_platform_services.py`; `tests/test_fs_search_paths.py`; module parity gate | Core search-path, pack, workshop, local web/resource fallback behavior, and Win32 Steam-ID-backed homepath selection are now strongly source-backed. |
| Message serialization, Huffman, and event/playerstate transport | High parity | `msg.c`, `huffman.c`, `net_chan.c` | mapping rounds `56`, `57`, `58`, `65`; `tests/test_playerstate_replication.py`; `tests/test_cgame_event_transport_parity.py` | The live delta/message path is one of the strongest qcommon lanes in the current repo. The 2026-05-25 playerState delta-codec re-audit now pins the Quake Live scalar netfield order, signed command-axis mirror serialization, and all four playerState array-mask round trips. |
| Collision-model public ABI and cgame/server bridge | High parity | `cm_load.c`, `cm_test.c`, `cm_trace.c`, `cm_patch.c`, `cm_polylib.c` | mapping rounds `25`, `33`, `65`; `docs/reverse-engineering/qcommon-collision-leaf-ownership-2026-04-10.md`; `tests/test_qcommon_collision_leaf_parity.py` | The public `CM_*` interface and the retained patch/polylib leaf family are now bounded by a dedicated ownership note plus deterministic curved-patch, point-trace, overlap, winding, and facet-plane probes. |
| Structured native DLL loader and VM host boundary | High parity | `vm.c`, `win_net.c`, `qcommon.h` | mapping rounds `63`, `79`, `84`, `99`, `107`; `tests/test_platform_services.py`; `tests/test_game_module_retail_parity_gate.py` | The native DLL path is strongly recovered and retail-compatible at the active host boundary. |
| Windows fallback QVM path | High parity at the owning host seam | `vm.c`, `vm_interpreted.c`, `vm_x86.c` | mapping rounds `63`, `84`, `99`, `107`; `docs/reverse-engineering/qcommon-vm-fallback-ownership-2026-04-10.md`; `tests/test_qcommon_vm_fallback_parity.py` | Fallback selection, native-load failure handling, interpreted syscall logging, restart fallback, and compiled handoff are now explicitly bounded; `vm_x86.c` remains documented as a compatibility carry beneath that closed host seam. |
| Unified parity gate and runtime evidence lane | Closed parity lane | `tests/test_qcommon_full_parity_gate.py`, `tests/compiler_support.py`, `tools/qcommon/run_qcommon_runtime_probe.ps1` | `artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json`; `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`; `.github/workflows/qcommon-validation.yml`; `docs/reverse-engineering/qcommon-validation-and-runtime-evidence-2026-04-10.md` | qcommon now has a dedicated parity gate, Windows-friendly harness coverage, collision probes, fallback-VM probes, and a tracked runtime bundle for bootstrap config execution, search-path roots, writable-homepath DLL loading, and service-disabled launcher/resource markers. |

## What Already Looks Closed

The fresh audit did not reopen these qcommon-owned tranches:

- retail `qzconfig.cfg` / `repconfig.cfg` bootstrap and writeback ownership
- legacy placeholder `q3key` handling and `writeClientConfig` command ownership
- Steam game-server bootstrap and `net_restart` ordering through `Com_InitSteamGameServer()`
- Win32 `fs_homepath` selection through the retail Steam-ID-backed startup contract
- `fs_webpath` rewrite, `web.pak`-compatible local fallback reads, and screenshot/homepath fallback routing
- workshop mount startup, retained workshop item metadata on packs, and `FS_ReferencedSteamworks()` publication
- Quake Live event/playerstate transport slots in `msg.c`
- structured native DLL validation and the `dllEntry` host contract in `vm.c` / `Sys_LoadDll`
- the retained `cm_patch.c` / `cm_polylib.c` leaf band beneath the already-mapped public `CM_*` ABI
- the retained fallback VM owner family beneath `vm.c`, including native-to-qvm fallback, interpreted syscall logging, restart fallback, and pointer-boundary handling

Observed fact:

- no confirmed source-owned qcommon loss remains below or inside the already-closed active runtime owners

Inference:

- future qcommon work should treat the audited strict-retail register as closed and only reopen it when new retail evidence or a real regression lands

## Gap Register

## QC-G01 - Filesystem startup and Steam-home discovery still depend on a heuristic helper

**Type:** Behavioral + ownership confidence  
**Priority:** P1  
**Status:** Closed on 2026-04-10

### Closure

Retail evidence anchors used for closure:

- `docs/reverse-engineering/quakelive_steam_mapping_round_34.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_55.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_56.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_91.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_99.md`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- current source in `src/code/qcommon/files.c`
- `tests/test_fs_search_paths.py`

Observed retail facts after the HLIL re-check:

1. The core retail filesystem/bootstrap owners are strongly mapped:
   - `FS_FOpenFileByMode`
   - `FS_Read`
   - `FS_Write`
   - `FS_GetFileList`
   - `FS_InitFilesystem`
   - `FS_Restart`
   - `FS_ConditionalRestart`
   - `FS_RewriteWebPath`
   - `Sys_LoadDll`
2. The alias ledger now directly binds:
   - `sub_4D30A0` -> `FS_Startup`
   - `sub_460510` -> `SteamClient_IsInitialized`
   - `sub_460550` -> `SteamClient_GetSteamID`
3. Retail HLIL shows `FS_Startup()` defaulting `fs_homepath` to `fs_basepath` until Steam exposes an active user, then switching to `va( "%s/%llu", fs_basepath, SteamClient_GetSteamID() )`.
4. The same HLIL corpus continues to build screenshot and local resource paths from `fs_homepath` plus `screenshots/`, so correct root selection still matters to active retail behavior.

Observed current-source facts after `QC-P3`:

1. `FS_Startup()` now calls `FS_ResolveHomePath( fs_basepath->string )` instead of falling back to the source-owned `FS_DetectSteamHomePath()` directory scan.
2. `FS_ResolveHomePath()` mirrors the retail Win32 contract: it keeps `fs_homepath == fs_basepath` until `QL_Steamworks_GetUserSteamID()` returns a non-zero Steam ID, then pivots to `fs_basepath/<steamid>`.
3. `tests/test_fs_search_paths.py` now directly guards the Win32 basepath default, the retail Steam-ID suffix, mapped `fs_webpath` fallback reads, and screenshot/homepath fallback routing.
4. While landing those probes, `FS_FOpenFileReadForRoot()` also stopped truncating the final character of resolved filenames, which restored correct fallback reads for mapped local web resources.

Conclusion:

- the heuristic directory scan is gone from active qcommon startup, and Win32 homepath selection now follows the retail Steam-ID-backed `FS_Startup` path, so `QC-G01` is closed

### Residual note

1. Non-Windows platforms still keep `Sys_DefaultHomePath()` as an explicit compatibility path outside the strict retail Win32 parity score.

## QC-G02 - Collision-model patch and polylib leaves remain only indirectly bounded

**Type:** Ownership confidence + validation  
**Priority:** P1  
**Status:** Closed on 2026-04-10

### Closure

Retail evidence anchors used for closure:

- `docs/reverse-engineering/quakelive_steam_mapping_round_25.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_33.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_65.md`
- current source in `src/code/qcommon/cm_*.c`
- `docs/reverse-engineering/qcommon-collision-leaf-ownership-2026-04-10.md`
- `tests/cm_collision_harness.c`
- `tests/test_qcommon_collision_leaf_parity.py`

Observed retail facts after the ownership pass:

1. The public collision-model owners are strongly mapped:
   - `CM_LoadMap`
   - `CM_InlineModel`
   - `CM_TempBoxModel`
   - `CM_PointContents`
   - `CM_TransformedPointContents`
   - `CM_BoxTrace`
   - `CM_TransformedBoxTrace`
   - `CM_MarkFragments`
2. `QLCGImport_CM_MarkFragments` remains the retained cgame import row for mark-fragment generation, and the current Win32 host still routes `CG_CM_MARKFRAGMENTS` through `re.MarkFragments` inside `src/code/client/cl_cgame.c`.
3. Both cgame imports and server entity-link/world logic still rely on the same retained collision-model subsystem.

Observed current-source facts after `QC-P4`:

1. `docs/reverse-engineering/qcommon-collision-leaf-ownership-2026-04-10.md` now bounds the writable helper family explicitly instead of treating the band below the public `CM_*` ABI as an open-ended confidence bucket. That note records the honest ownership split: `CM_MarkFragments` stays on the retained renderer seam for the strict Win32 host, while `cm_patch.c` owns helpers such as `CM_GeneratePatchCollide`, `CM_TraceThroughPatchCollide`, `CM_PositionTestInPatchCollide`, and `CM_CheckFacetPlane`, and `cm_polylib.c` owns `BaseWindingForPlane`, `ChopWindingInPlace`, `WindingArea`, `WindingBounds`, and `AddWindingToConvexHull`.
2. `tests/cm_collision_harness.c` now builds a dedicated native collision leaf probe against `cm_patch.c` and `cm_polylib.c`, exposing deterministic entrypoints for curved-patch statistics, flat patch point traces, flat patch position tests, representative winding clipping, and direct `CM_CheckFacetPlane` behavior.
3. `tests/test_qcommon_collision_leaf_parity.py` now keeps those leaf behaviors pinned with deterministic assertions:
   - curved patch generation reports `36` planes, `4` facets, and the expected `[-17, -17, -1, 17, 17, 33]` bounds
   - flat patch traces hit at the retained `SURFACE_CLIP_EPSILON` fraction
   - flat patch position tests distinguish overlap versus no-overlap cases
   - `BaseWindingForPlane` plus `ChopWindingInPlace` reproduces the expected mark-fragment-style clipped bounds and area
   - `CM_CheckFacetPlane` reports the expected enter fraction and hit state
4. Present confidence therefore no longer depends only on the already-mapped public `CM_*` owners and downstream runtime behavior; it now includes bounded leaf ownership plus focused native probes.

Conclusion:

- the collision-model ABI is still the primary retail anchor, but the lower-level patch/polylib helper family is now directly bounded enough that `QC-G02` can close without over-claiming a new public `CM_MarkFragments` owner

## QC-G03 - The Windows fallback QVM path was much less bounded than the native DLL path

**Type:** Ownership confidence + validation  
**Priority:** P1  
**Status:** Closed on 2026-04-10

### Closure

Retail evidence anchors used for closure:

- `docs/reverse-engineering/quakelive_steam_mapping_round_63.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_84.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_99.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_107.md`
- current source in `src/code/qcommon/vm.c`, `src/code/qcommon/vm_interpreted.c`, `src/code/qcommon/vm_x86.c`
- `docs/reverse-engineering/qcommon-vm-fallback-ownership-2026-04-10.md`
- `tests/vm_fallback_harness.c`
- `tests/test_qcommon_vm_fallback_parity.py`

Observed retail facts:

1. The active Windows host path is strongly mapped through the native DLL loader boundary:
   - `VM_Create` native path
   - `VM_ValidateNativeDllInterface`
   - `Sys_LoadDll`
   - retained UI/game VM lifecycle owners
2. `VM_Init()` defaults `vm_cgame`, `vm_game`, and `vm_ui` to `0`, matching the retail “native modules by default” story.

Observed current-source facts after `QC-P5`:

1. `docs/reverse-engineering/qcommon-vm-fallback-ownership-2026-04-10.md` now bounds the fallback owner family explicitly instead of leaving it as a lightly described tail below the native DLL lane. That note records the honest split: `vm.c` remains the owning Windows host-selection seam, `vm_interpreted.c` remains part of strict fallback parity because the host still dispatches into it, and `vm_x86.c` is kept as a compatibility carry beneath the closed seam instead of reopening strict Windows parity on its own.
2. `tests/vm_fallback_harness.c` now builds a dedicated native fallback harness against `vm.c` and `vm_interpreted.c`, exposing deterministic entrypoints for native-load failure fallback, `fs_restrict` forcing compiled fallback, missing-qvm hard failure, interpreted add/syscall execution, restart fallback, and `VM_ArgPtr` or `VM_ExplicitArgPtr` boundary behavior.
3. `tests/test_qcommon_vm_fallback_parity.py` now keeps those lanes pinned with deterministic assertions:
   - native DLL failure falls back to compiled qvm execution
   - `fs_restrict` forces compiled fallback without attempting a native load
   - missing qvm content after native failure stays a hard failure with the retained fallback log
   - the real interpreter path executes bytecode and preserves `vm-interpreted` syscall-contract logging
   - restart re-enters the native-first host seam before falling back again
   - native and qvm pointer-boundary helpers stay distinct
   - `vm.c`, `vm_interpreted.c`, and `vm_x86.c` still contain the expected host-selection/backend anchors
4. Present confidence therefore no longer depends only on the already-strong native DLL path. It now includes focused proof for the fallback owner family beneath it.

Conclusion:

- the fallback Windows QVM/JIT path is no longer an open blind spot beneath the native DLL path, so `QC-G03` is closed

### Residual note

1. `vm_x86.c` remains an explicit compatibility carry. `QC-P5` closes the owning host-selection seam and the fallback execution boundaries without claiming that every legacy x86 backend detail is a distinct active-runtime retail owner.

## QC-G04 - qcommon validation is fragmented and partially non-portable on the default Windows host

**Type:** Verification infrastructure  
**Priority:** P0  
**Status:** Closed on 2026-04-10

### Closure

Qcommon now has the same dedicated machine-readable validation lane that the renderer, client, and strict module audits already use, and its native harness probes now run on the default Windows host without assuming `gcc`.

Observed current-source facts after `QC-P2`:

1. `tests/test_qcommon_full_parity_gate.py` now writes `artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json`, keeping the active qcommon gap register machine-readable even while `QC-G01`, `QC-G02`, `QC-G03`, and `QC-G05` remain open.
2. `tests/compiler_support.py` now gives the qcommon-facing native probes one shared Windows-friendly compiler-selection path, and `tests/test_cvar_alias_console.py`, `tests/test_fs_search_paths.py`, and `tests/test_playerstate_replication.py` now all route through it instead of hard-requiring `gcc` or force-skipping Windows.
3. `tests/fs_searchpath_harness.c` now exports a Windows-capable filesystem harness lane, including native directory enumeration and harness-owned log capture so the search-path/source-selection assertions no longer depend on pytest intercepting DLL `stdout`.
4. `.github/workflows/qcommon-validation.yml`, `docs/build-pipeline.md`, and `docs/windows-native-pipeline.md` now document and run the dedicated qcommon validation lane on `windows-latest`.

### Residual note

1. Validation fragmentation and Windows-host portability remain closed after `QC-P2`; the `QC-P6` runtime bundle now turns that validation lane into a fully closed parity proof surface rather than a staged partial gate.

## QC-G05 - qcommon ledger and mapping documentation still lag recovered source in a few places

**Type:** Documentation + closure tracking  
**Priority:** P2  
**Status:** Closed on 2026-04-10

Retail evidence anchors:

- `docs/reverse-engineering/quakelive_steam_mapping_round_108.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_109.md`
- current source in `src/code/qcommon/common.c`
- `tests/test_client_config_parity.py`
- `tools/qcommon/run_qcommon_runtime_probe.ps1`
- `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
- `docs/reverse-engineering/qcommon-validation-and-runtime-evidence-2026-04-10.md`

Observed closure facts after `QC-P6`:

1. Mapping rounds `108` and `109` now explicitly mark their old `writeClientConfig` owner caveat as historical-only wording instead of an active repo gap.
2. The current source still carries `Com_WriteClientConfig_f()` in `common.c` and registers `writeClientConfig` inside `Com_Init()`, with `tests/test_client_config_parity.py` guarding that owner and its output contract.
3. `tools/qcommon/run_qcommon_runtime_probe.ps1` now archives the final low-cost qcommon runtime evidence bundle at `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`, covering:
   - bootstrap `qzconfig.cfg` / `repconfig.cfg` execution
   - the active filesystem search-path roots
   - writable-homepath DLL loading for `ui`, `qagame`, and `cgame`
   - service-disabled launcher/resource policy markers from the current debug build, including the current `game.error` publication and native `stopRefresh` fallback markers
4. `docs/reverse-engineering/qcommon-validation-and-runtime-evidence-2026-04-10.md` now records that runtime bundle plus the dedicated gate artifact as the final qcommon closure proof lane.

Conclusion:

- qcommon ledger state, mapping notes, and tracked runtime evidence are now reconciled on one closed `QC-P6` story, so `QC-G05` is closed

## Closure Plan

## QC-P1 - Publish the dedicated qcommon audit and closure ledger [COMPLETED 2026-04-10]

**Closes:** initial qcommon ledger gap and establishes the explicit register for `QC-G01`..`QC-G05`  
**Priority:** High  
**Parity estimate:** **87% -> 87%**

Completed work:

1. Re-audited `src/code/qcommon/*` against the committed retail `quakelive_steam.exe` HLIL/Ghidra corpus, the promoted alias ledger, the relevant mapping rounds, the current writable source, and the qcommon-facing validation surface.
2. Published this dedicated qcommon audit to separate the already-strong common/filesystem/message/native-loader story from the smaller remaining helper-confidence and validation gaps.
3. Turned the remaining qcommon debt into an explicit gap register (`QC-G01`..`QC-G05`) and a dependency-ordered closure plan (`QC-P2`..`QC-P6`) instead of leaving it spread across mapping rounds, client/module/server notes, and top-level ledgers.

Validation:

- `python -m pytest tests/test_cvar_parity.py tests/test_fs_search_paths.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_playerstate_replication.py tests/test_cgame_event_transport_parity.py tests/test_game_module_retail_parity_gate.py -q -rs --tb=no`
- Result: `67 passed`, `8 skipped`
- Additional portability check: `python -m pytest tests/test_cvar_alias_console.py -vv --maxfail=1`
- Result: `1 failed` because `gcc` was not installed on the current Windows host

## QC-P2 - Add a unified qcommon parity gate and make the harness set Windows-friendly [COMPLETED 2026-04-10]

**Closes:** `QC-G04`, sets up closure proof for the remaining gaps  
**Priority:** Critical
**Parity estimate:** **87% -> 90%**

Completed work:

1. Added `tests/test_qcommon_full_parity_gate.py`, the committed `artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json` artifact, and the dedicated `.github/workflows/qcommon-validation.yml` lane so qcommon closure state is visible in one machine-readable report instead of only across scattered focused suites.
2. Added `tests/compiler_support.py` and converted the qcommon-facing harness probes to use it, making the legacy cvar alias probe, filesystem search-path harness, and playerstate replication transport test fully runnable on the default Windows host.
3. Updated the qcommon audit, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, and the build/pipeline docs so `QC-P2` and `QC-G04` are recorded as complete and the remaining open work is narrowed to `QC-G01`, `QC-G02`, `QC-G03`, and `QC-G05`.

Validation:

- `python -m pytest tests/test_cvar_parity.py tests/test_cvar_alias_console.py tests/test_fs_search_paths.py tests/test_playerstate_replication.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_cgame_event_transport_parity.py tests/test_qcommon_full_parity_gate.py -q`
- Result: `75 passed`, `2 skipped`

## QC-P3 - Replace or explicitly bound the heuristic Steam-home/profile discovery path [COMPLETED 2026-04-10]

**Closes:** `QC-G01`  
**Priority:** High
**Parity estimate:** **90% -> 92%**

Completed work:

1. Re-checked the retail startup/root-selection path against the committed alias ledger and HLIL corpus, confirming that retail Win32 `FS_Startup()` does not scan the filesystem for profile directories and instead pivots from `fs_basepath` to `fs_basepath/<steamid>` only when Steam exposes an active user.
2. Replaced the source-owned `FS_DetectSteamHomePath()` heuristic in `src/code/qcommon/files.c` with `FS_ResolveHomePath()`, which now uses `QL_Steamworks_GetUserSteamID()` to mirror the retail Win32 homepath contract while leaving the non-Windows `Sys_DefaultHomePath()` compatibility path explicit.
3. Extended `tests/fs_searchpath_harness.c` and `tests/test_fs_search_paths.py` so qcommon now has focused regression coverage for the basepath default, the retail Steam-ID suffix, mapped `fs_webpath` fallback reads, and screenshot/homepath fallback routing.
4. Fixed a real fallback-read bug discovered by the new harness coverage: `FS_FOpenFileReadForRoot()` no longer truncates the final character of the resolved filename before opening the file.

Validation:

- `python -m pytest tests/test_cvar_parity.py tests/test_cvar_alias_console.py tests/test_fs_search_paths.py tests/test_playerstate_replication.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_cgame_event_transport_parity.py tests/test_qcommon_full_parity_gate.py -q`
- Result: `81 passed`, `2 skipped`

## QC-P4 - Add direct ownership notes and focused probes for collision patch/polylib leaves [COMPLETED 2026-04-10]

**Closes:** `QC-G02`  
**Priority:** High
**Parity estimate:** **92% -> 95%**

Completed work:

1. Published `docs/reverse-engineering/qcommon-collision-leaf-ownership-2026-04-10.md`, which bounds the retained `cm_patch.c` / `cm_polylib.c` helper family under the already-mapped `CM_*` ABI and records the honest Win32 host seam where `CG_CM_MARKFRAGMENTS` still dispatches through `re.MarkFragments`.
2. Added `tests/cm_collision_harness.c` plus `tests/test_qcommon_collision_leaf_parity.py`, giving qcommon deterministic native probes for curved-patch generation, flat patch trace fractions, flat patch overlap checks, representative mark-fragment-style winding clipping, and direct `CM_CheckFacetPlane` behavior.
3. Refreshed the qcommon parity gate and ledgers so `QC-G02` is recorded as closed and the remaining strict qcommon gap is narrowed to the fallback VM and stale-ledger tails.

Validation:

- `python -m pytest tests/test_cvar_parity.py tests/test_cvar_alias_console.py tests/test_fs_search_paths.py tests/test_qcommon_collision_leaf_parity.py tests/test_playerstate_replication.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_cgame_event_transport_parity.py tests/test_qcommon_full_parity_gate.py -q`
- Result: `88 passed`, `2 skipped`

## QC-P5 - Bound the Windows fallback QVM/JIT path beneath the already-closed native DLL path [COMPLETED 2026-04-10]

**Closes:** `QC-G03`  
**Priority:** High
**Parity estimate:** **95% -> 98%**

Completed work:

1. Published `docs/reverse-engineering/qcommon-vm-fallback-ownership-2026-04-10.md`, which ties the fallback owner family back to the committed retail evidence in mapping rounds `63`, `84`, `99`, and `107`, keeps `vm.c` as the active Windows host-selection owner, and records `vm_x86.c` as a bounded compatibility carry instead of an open strict-retail blind spot.
2. Added `tests/vm_fallback_harness.c` plus `tests/test_qcommon_vm_fallback_parity.py`, giving qcommon deterministic native proof for native-load failure fallback, `fs_restrict` compiled selection, missing-qvm hard failure, interpreted bytecode and syscall dispatch, restart fallback, and `VM_ArgPtr` or `VM_ExplicitArgPtr` boundary behavior.
3. Refreshed the qcommon parity gate, workflow lane, Windows/build pipeline docs, and repo ledgers so `QC-G03` is recorded as closed and the remaining open qcommon work is narrowed to `QC-P6`.

Validation:

- `python -m pytest tests/test_cvar_parity.py tests/test_cvar_alias_console.py tests/test_fs_search_paths.py tests/test_qcommon_collision_leaf_parity.py tests/test_qcommon_vm_fallback_parity.py tests/test_playerstate_replication.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_cgame_event_transport_parity.py tests/test_qcommon_full_parity_gate.py -q`
- Result: `98 passed`, `2 skipped`

## QC-P6 - Reconcile stale mapping notes and publish final qcommon runtime evidence [COMPLETED 2026-04-10]

**Closes:** remaining `QC-G05` and final closure-proof tail  
**Priority:** Medium
**Parity estimate:** **98% -> 100%**

Completed work:

1. Reconciled the stale `writeClientConfig` owner caveat in mapping rounds `108` and `109`, preserving the historical “unnamed in that round” context while explicitly marking the old missing-owner wording as stale now that `Com_WriteClientConfig_f()` is present in writable source and guarded by `tests/test_client_config_parity.py`.
2. Added `tools/qcommon/run_qcommon_runtime_probe.ps1`, which now runs low-cost windowed qcommon probes and records:
   - bootstrap config execution
   - chosen filesystem roots
   - retail DLL load roots
   - service-disabled local launcher/resource fallback behavior
3. Published the tracked runtime bundle at `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`, the dedicated closure note at `docs/reverse-engineering/qcommon-validation-and-runtime-evidence-2026-04-10.md`, and refreshed the gate/workflow/top-level ledgers so qcommon closure status is tracked like the renderer/client/server/module lanes.

Validation:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/qcommon/run_qcommon_runtime_probe.ps1`
  - Result: `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json` refreshed with clean bootstrap/search-path/DLL-root/service-policy evidence plus authoritative engine screenshots, the current `map <name> ffa` launch contract, and the current default-disabled browser-policy markers
- `python -m pytest tests/test_cvar_parity.py tests/test_cvar_alias_console.py tests/test_fs_search_paths.py tests/test_qcommon_collision_leaf_parity.py tests/test_qcommon_vm_fallback_parity.py tests/test_playerstate_replication.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_cgame_event_transport_parity.py tests/test_qcommon_full_parity_gate.py -q`
  - Result: `101 passed`, `2 skipped`

## Recommended execution order

1. No remaining qcommon closure phase.

Rationale:

- `QC-P2` through `QC-P6` are now complete.
- No open gap remains in the audited qcommon register.

## Final Assessment

The engine `qcommon` module is no longer mainly missing broad retail Quake Live behavior. Its active runtime spine is source-backed and heavily cross-checked: common bootstrap/config persistence, filesystem startup and local launcher fallbacks, workshop metadata publication, message and netchan transport, and the structured native DLL loader boundary are all recovered strongly enough to treat the audited strict-retail register as closed.

The module now also has a dedicated parity gate, a Windows-friendly harness lane, a bounded collision leaf note, a bounded fallback-VM note, reconciled mapping rounds for `writeClientConfig`, and a tracked runtime bundle proving bootstrap config execution, chosen filesystem roots, writable-homepath DLL loading, and service-disabled launcher/resource policy behavior.

That puts qcommon on the same closed-ledger footing as the renderer, client, and server audits for the current worktree. No open gap remains in the audited qcommon register after `QC-P6`.
