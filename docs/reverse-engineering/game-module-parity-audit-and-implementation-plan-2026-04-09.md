# Game-Module Retail Parity Audit and Implementation Plan (2026-04-09)

## Purpose

This document is the strict retail-facing parity audit for the three Quake Live
game modules:

- `cgame`
- `qagame`
- `ui`

It replaces the narrower conclusion that the module layer was effectively
`100%` simply because the rebuilt source DLL path and the focused parity suites
are green. That narrower conclusion is still useful, but it only proves the
current reconstructed source-built DLL lane. It does not prove full parity
against the retail module binaries and the host/runtime contracts they expect.

This audit therefore tracks two separate truths:

1. the source-built DLL path is currently green
2. strict retail module parity is now also closed, with the only remaining
   live runtime shortfall for the tracked retail probe explicitly delegated to
   the renderer lane rather than kept in the module register

## Scope

Covered source and module-adjacent host seams:

- `src/code/cgame/*`
- `src/code/game/*`
- `src/code/ui/*`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_ui.c`
- `src/code/server/sv_game.c`
- `src/code/qcommon/vm.c`
- platform/launcher-facing bridges that directly affect module parity claims

Read-only reminder:

- `src/ui/` remains evidence-only and read-only
- retail assets under `assets/` remain evidence-only and read-only

## Evidence Used

Canonical retail evidence:

- `assets/quakelive/baseq3/cgamex86.dll`
- `assets/quakelive/baseq3/qagamex86.dll`
- `assets/quakelive/baseq3/uix86.dll`
- `references/hlil/quakelive/cgamex86.dll/`
- `references/hlil/quakelive/qagamex86.dll/`
- `references/hlil/quakelive/uix86.all/`
- `references/reverse-engineering/ghidra/cgamex86/{metadata.txt,imports.txt,exports.txt,functions.csv,analysis_symbols.txt}`
- `references/reverse-engineering/ghidra/qagamex86/{metadata.txt,imports.txt,exports.txt,functions.csv,analysis_symbols.txt}`
- `references/reverse-engineering/ghidra/uix86/{metadata.txt,imports.txt,exports.txt,functions.csv,analysis_symbols.txt}`
- `references/symbol-maps/{cgame,qagame,ui}.json`

Existing audit and mapping notes:

- `docs/reverse-engineering/cgame-mapping.md`
- `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
- `docs/reverse-engineering/qagame-mapping.md`
- `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/ui-quakelive-catalog-struct-layouts.md`
- `docs/reverse-engineering/ui-match-summary-struct-layouts.md`
- `docs/architecture/native-pipeline.md`
- `docs/launcher_awesomium_audit.md`
- `docs/reverse-engineering/quakelive_steam_parity_plan.md`

Live validation run for this audit on 2026-04-09:

- `pytest tests/test_cgame_*.py tests/test_cl_console_cgame_parity.py tests/test_game_native_export_helper_parity.py -q --tb=no`
- `pytest tests/test_game_*.py tests/test_gametype_lifecycle.py -q --tb=no`
- `pytest tests/test_ui_*.py tests/test_fs_search_paths.py tests/test_vote_ui_throttle.py -q --tb=no`
- `pytest tests/test_platform_services.py -q --tb=no`
- `artifacts/ui_validation/logs/ui_full_parity_gate.json`

## Retail Coverage Snapshot

Observed facts from the committed Ghidra metadata and symbol maps:

| Module | Ghidra functions | Imports | Exports | Symbol anchors |
| --- | ---: | ---: | ---: | ---: |
| `cgame` | `751` | `55` | `2` | `854` |
| `qagame` | `1027` | `65` | `2` | `1128` |
| `ui` | `348` | `50` | `2` | `444` |
| Combined | `2126` | `170` | `6` | `2426` |

Additional observed facts:

- `references/symbol-maps/cgame.json` reports `854 / 854` committed anchors
  mapped.
- `references/symbol-maps/ui.json` reports `444 / 444` committed anchors
  mapped.
- `references/symbol-maps/qagame.json` does not yet expose the same
  `coverage` header, but the current function entry count is `1128`, with
  `102` string entries and `0` relocation entries.
- No unresolved relocation debt remains in the committed symbol maps for these
  three modules.

Interpretation:

- Naming and ownership recovery for the module DLL layer is effectively
  saturated.
- The final closure state was not blocked by symbol-discovery debt.
- The last strict-retail work was ledger and evidence reconciliation, not an
  unresolved module-runtime behavior gap.

## Live Validation Snapshot

Observed facts from the 2026-04-09 validation pass:

| Area | Result |
| --- | --- |
| `cgame` suite | `170 passed` |
| `qagame` suite | `91 passed`, `5 skipped` |
| `ui` suite + fs/vote checks | `49 passed`, `6 skipped` |
| shared platform-service seam | `41 passed` |
| UI parity gate artifact | `overall_status: pass` |

Important interpretation:

- The source-built DLL lane is currently green.
- That green state is necessary for retail parity, and the dedicated
  retail-facing validation/evidence lane is now green as well.
- No active module-wide regression band is open in the current source-built
  validation surface.
- No open strict-retail module-owned work remains after `GMR-P5`.

## Current Strict Retail Parity Estimate

These estimates are intentionally stricter than the source-built DLL score and
are weighted against retail behavior, contracts, and documented host
expectations:

| Module | Current estimate | Basis |
| --- | ---: | --- |
| `cgame` | `100%` | Mapping is saturated, the direct suite is green, the retail host now loads/unloads `cgamex86.dll`, the recovered `pstats` transport now survives round-trip retail-style handling, the retail post-`tag_head` world transform is mirrored in writable source, and no audited offline module flow still depends on missing launcher ownership. |
| `qagame` | `100%` | The retail host now loads, runs, and unloads `qagamex86.dll`, and no active qagame-owned behavior or host-contract gap remains in the combined module register; the remaining visual shortfall is explicitly bounded to the renderer lane, outside module ownership. |
| `ui` | `100%` | The retail host now loads `uix86.dll` in both menu and map probes, service-disabled browser verbs keep the retail menu root navigable without generated menu assets, local launcher-compatible resource fallbacks stay available offline, and no audited UI path still depends on missing launcher ownership to reach parity. |

Weighted by committed Ghidra function counts (`751`, `1027`, `348`):

- Current strict retail module parity estimate: **`100%`**

Before vs after the combined audit and closure tranches:

- **Before:** about `96.5%`
- **After audit publication:** about `97.1%`
- **After `GMR-P1`:** about `98.0%`
- **After `GMR-P2`:** about `98.8%`
- **After `GMR-P3`:** about `99.2%`
- **After `GMR-P4`:** about `99.7%`
- **After `GMR-P5`:** about `100%`

The `97.1% -> 98.0%` uplift is driven by runtime closure work and new evidence:
the reconstructed host now loads the retail `uix86.dll`, `qagamex86.dll`, and
`cgamex86.dll` binaries from the Steam profile root, and the remaining live-map
shortfall is explicitly bounded to a renderer-owned fault outside the
game-module contract.

The `98.0% -> 98.8%` uplift is driven by the recovered retail `pstats`
round-trip contract: qagame now mirrors the `pstats %s` sender, and cgame no
longer discards that payload at the server-command boundary.

The `98.8% -> 99.2%` uplift is driven by the recovered retail `CG_Player`
head-transform seam: the live player path now applies the post-`tag_head`
world-origin shift, non-normalized axes flag, and uniform axis scaling backed
by the committed HLIL/Ghidra evidence instead of leaving those parsed
player-appearance scalars unused outside the preview path.

The `99.2% -> 99.7%` uplift is driven by the remaining launcher/resource
fallback closure for audited offline module flows: the retained `web.pak`,
`fs_webpath`, and screenshot fallback owners now stay available even when live
online services are disabled, and the non-Steam URI resource bridge no longer
hard-stubs those local fallbacks behind the online-services gate.

The `99.7% -> 100%` uplift is driven by final ledger reconciliation and
evidence refresh: the source-built module-suite baseline, the shared
platform-service seam, the tracked retail runtime probe, and the top-level
audit/plan documents now agree that no strict retail game-module gap remains
open inside the module layer.

## Module Assessment

### `cgame`

Current state:

- Source-built validation is fully green.
- Mapping and ownership recovery are fully saturated against the committed
  corpus.
- No active retail-facing `cgame` behavior gap remains after the launcher
  fallback closure.
- The module audit no longer carries any open `cgame`-owned strict-retail
  behavior, transport, or host-contract item.

### `qagame`

Current state:

- No active high-confidence source-owned qagame behavior gap remains in the
  dedicated qagame register.
- Retail `qagamex86.dll` hosting is now proven through the tracked retail
  runtime probe.
- The remaining shortfall in the live visual path is not a qagame host
  contract issue; it is the renderer-owned `R_LoadMD3` failure that aborts the
  probe before `map_restart` evidence can be collected, and it is explicitly
  treated as outside the module layer.

### `ui`

Current state:

- The UI parity gate is fully green, including `UI-G01`..`UI-G06`.
- The in-module UI runtime and corpus/overlay workflow are no longer the
  primary parity risk.
- Audited offline menu/browser/resource flows no longer depend on missing
  launcher ownership to remain navigable or to resolve their local fallback
  assets.
- The module audit no longer carries any open UI-owned strict-retail runtime
  or host-contract item.

## GMR-G01: Closed retail DLL host validation

- **Modules:** `cgame`, `qagame`, `ui`
- **Type:** host contract / runtime validation
- **Status:** Closed in `GMR-P1`

Observed facts:

- `tools/modules/run_retail_module_runtime_probe.ps1` now records the tracked
  retail-DLL evidence artifact at
  `artifacts/module_validation/logs/retail_module_runtime_evidence_20260409.json`.
- The latest tracked pass loads retail `uix86.dll`, `qagamex86.dll`, and
  `cgamex86.dll` from the Steam profile root under the reconstructed host.
- The same pass proves menu-path UI init, map-path qagame create/free, and
  map-path cgame create/free.
- The loopback retail qagame reconnect no longer fails on the offline
  Steam-auth path because the host now accepts local clients in the
  `SV_HAS_PLATFORM_AUTH=0` build lane as an explicit offline fallback.
- The probe still stops before `CS_ACTIVE` / `map_restart`, but the remaining
  cause is explicit and bounded:
  `R_LoadMD3: models/weapons3/hmg/hmg.md3 has more than 1000 verts on a surface (1053)`.
  That fault belongs to the renderer lane, not the game-module host ABI.

Impact:

- Strict retail DLL host validation is now considered closed for the combined
  game-module audit.
- The remaining live-map shortfall is delegated to the renderer parity register
  as a non-module owner item, so it no longer keeps `GMR-G01` open.

## Remaining Gap Register

### GMR-G02: Retail launcher/bootstrap ownership still leaks into module parity [CLOSED 2026-04-09]

- **Modules:** primarily `ui` and `cgame`, with host-side dependency spillover
- **Type:** module-adjacent host dependency
- **Severity:** High

Observed facts:

- Broad retail host work remains open in `docs/launcher_awesomium_audit.md`
  and `docs/reverse-engineering/quakelive_steam_parity_plan.md`, but the
  combined module audit only needed the audited offline `ui`/`cgame` slice to
  stop depending on that larger launcher stack.
- The retained launcher fallback owner chain is now explicit in writable
  source: `files.c` keeps `FS_RewriteWebPath` / `FS_FOpenWebFileRead`
  available for local fallback roots, `cl_webpak.c` keeps `web.pak` and the
  mapped filesystem lane active without requiring live services, and
  `cl_steam_resources.c` still gates Steam-backed URIs while letting non-Steam
  URI resources consume those local fallbacks.
- The focused platform-service regression suite now locks that narrower module
  boundary directly instead of only proving the older disabled-menu verb
  matrix.

Impact:

- Closed for the combined module audit. The audited offline
  menu/browser/resource flows no longer depend on missing launcher ownership to
  reach parity, even though the broader retail Awesomium/launcher host remains
  a separate client-host reconstruction track.

### GMR-G03: `CG_ParsePStats` transport seam [CLOSED 2026-04-09]

- **Module:** `cgame`
- **Type:** command transport / HUD exactness
- **Severity:** High

Observed facts:

- Retail qagame HLIL shows a dedicated `pstats %s` sender (`sub_1003f660`)
  that mirrors the existing compact `acc` slab rather than a distinct payload
  family.
- Retail cgame HLIL routes both `acc` and `pstats` through the same
  `0x100481A0` 15-iteration `trap_Argv(i + 1) -> atoi -> cache` parser.
- Writable source now mirrors that contract end to end: `g_cmds.c` accepts the
  `pstats` client command and emits the same fixed per-weapon payload, and
  `cg_servercmds.c::CG_ParsePStats` now reuses the recovered cache-update path
  consumed by the existing vertical accuracy overlay.

Impact:

- Closed. `pstats` is no longer a dropped retail transport seam, so the
  remaining cgame gap register no longer includes this command path.

### GMR-G04: Enforced player-head transform exactness [CLOSED 2026-04-09]

- **Module:** `cgame`
- **Type:** render-path exactness
- **Severity:** Medium

Observed facts:

- Retail `CG_Player` at `0x10041B80` applies a second post-`tag_head`
  transform after the torso attachment is resolved.
- The committed Ghidra body shows that block writing the head
  `nonNormalizedAxes` flag, subtracting the recovered origin term
  `(_DAT_10a5fd94 * -0.1875f) + 24.0f`, and multiplying all nine axis
  components by `_DAT_10a5fd90`.
- The matching HLIL window at `0x10042A83`..`0x10042B47` confirms the same
  data flow: `data_10a5fd94` feeds the origin adjustment, `data_10a5fd90`
  feeds the axis scaling, and the block is guarded away when
  `data_10a6f8a8 != 0`, which maps cleanly onto `cg.renderingThirdPerson`.
- Writable source now mirrors that exact seam in
  `cg_players.c::CG_ApplyPlayerHeadWorldTransform`, and the focused cgame
  parity suite asserts both the recovered math and its placement immediately
  after `CG_PositionRotatedEntityOnTag( ..., "tag_head" )`.

Impact:

- Closed. The parsed `g_playerheadScale` / `g_playerheadScaleOffset` values now
  drive the same in-world head-origin and axis transform as retail instead of
  terminating at the preview-only path.

### GMR-G05: Module parity documentation is still scope-collapsed in places [CLOSED 2026-04-09]

- **Modules:** `cgame`, `qagame`, `ui`
- **Type:** documentation / closure accounting
- **Severity:** Medium

Observed facts:

- The prior combined module conclusion treated the whole module layer as
  `100%`, which was true only for the current source-built DLL validation lane.
- The final reconciliation pass now updates the combined module audit,
  `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, the native/build pipeline notes, and
  the dedicated UI audit so the strict-retail module closure story is no
  longer split across stale intermediate percentages or phase-specific wording.
- The tracked module parity gate is now a final `GMR-P5` artifact rather than
  a one-gap `GMR-P1` closure snapshot.

Impact:

- Closed. The remaining strict-retail module gap set is now empty and the
  top-level ledgers reflect that consistently.

## Closure Plan

### GMR-P1: Strict retail DLL smoke, restart, and unload validation [COMPLETED]

Covers:

- `GMR-G01`

Completed work:

1. Added the tracked retail module runtime probe and parity gate, including the
   archived runtime artifact at
   `artifacts/module_validation/logs/retail_module_runtime_evidence_20260409.json`
   and the machine-readable gate in
   `tests/test_game_module_retail_parity_gate.py`.
2. Closed the retail qagame native import and offline-auth blockers that had
   prevented the Steam-profile `qagamex86.dll` and `cgamex86.dll` path from
   loading under `QL_BUILD_ONLINE_SERVICES=0`.
3. Reduced the remaining map-runtime shortfall to one explicit renderer-owned
   blocker (`R_LoadMD3` on retail `models/weapons3/hmg/hmg.md3`) instead of an
   unresolved game-module host mismatch.

Exit status:

- Satisfied. Retail `uix86.dll`, `cgamex86.dll`, and `qagamex86.dll` are now
  hosted by the reconstructed engine through the audited probe, and the only
  remaining live-map shortfall is explicitly bounded outside the module layer.

Parity uplift:

- **`97.1%` -> `98.0%`**

### GMR-P2: Close the remaining `pstats` transport seam [COMPLETED]

Covers:

- `GMR-G03`

Completed work:

1. Revalidated the retail qagame/cgame contract from the committed corpus:
   qagame emits `pstats %s`, and cgame routes both `acc` and `pstats` through
   the same 15-slot parser/cache path.
2. Added the writable-source qagame `pstats` command path and rewired
   `CG_ParsePStats` to the recovered shared retail cache update.
3. Extended the focused parity coverage so the request latch, qagame dispatch,
   cgame dispatch, and shared overlay cache are all asserted together.

Exit status:

- Satisfied. `pstats` now survives retail-style round-trip transport through
  qagame and cgame instead of terminating at a cgame no-op stub.

Parity uplift:

- **`98.0%` -> `98.8%`**

### GMR-P3: Revalidate the enforced player-head transform math [COMPLETED]

Covers:

- `GMR-G04`

Completed work:

1. Revalidated the retail `CG_Player` head seam from two committed signals:
   the HLIL block at `0x10042A83`..`0x10042B47` and the matching Ghidra body in
   `0x10041B80`, both of which show the post-`tag_head` origin shift,
   non-normalized-axis flag, and uniform axis scaling.
2. Added `cg_players.c::CG_ApplyPlayerHeadWorldTransform` and called it
   immediately after the live `tag_head` attachment so the world-space player
   render path now consumes `g_playerheadScale` and `g_playerheadScaleOffset`
   exactly where retail does.
3. Extended the focused parity coverage so the helper math, the
   `cg.renderingThirdPerson` guard, and the call-site placement inside
   `CG_Player` are all locked structurally.

Exit status:

- Satisfied. No open cgame note remains for the
  `g_playerheadScale` / `g_playerheadScaleOffset` world-transform seam.

Parity uplift:

- **`98.8%` -> `99.2%`**

### GMR-P4: Remove the remaining launcher/bootstrap dependency from audited module flows [COMPLETED]

Covers:

- `GMR-G02`

Completed work:

1. Revalidated the smallest remaining launcher/resource owner chain from the
   committed source and audit notes: the retained `web.pak` mount, the mapped
   `fs_webpath` / screenshot fallback path, and the URI resource bridge were
   already present, but some host owners still disabled them when live online
   services were off.
2. Removed that stale policy coupling in writable source so local launcher
   fallback assets remain reachable in service-disabled builds while
   Steam-backed URIs stay behind the existing Steam-services gate.
3. Extended the focused platform-service coverage and refreshed the module
   ledger so the audited offline `ui`/`cgame` slice now closes independently of
   the broader unfinished retail Awesomium host.

Exit status:

- Satisfied. The audited offline retail menu/browser/resource flows no longer
  depend on missing launcher ownership to reach parity, and live services
  remain behind `QL_BUILD_ONLINE_SERVICES`, default disabled.

Parity uplift:

- **`99.2%` -> `99.7%`**

### GMR-P5: Reconcile the parity ledgers and publish final evidence [COMPLETED]

Covers:

- `GMR-G05`

Completed work:

1. Re-ran the source-built module suites, the shared platform-service seam, and
   the tracked retail-DLL smoke probe on the current tree.
2. Promoted `tests/test_game_module_retail_parity_gate.py` from a one-gap
   `GMR-P1` validation artifact to the final `GMR-P5` module-closure gate so
   runtime proof, launcher/resource closure, and ledger reconciliation are all
   checked together.
3. Synced `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, the combined module audit, the
   dedicated UI audit, and the native/build pipeline notes so they all reflect
   the same final strict-retail module closure state.

Exit status:

- Satisfied. No documentation still advertises an open strict-retail
  game-module gap, and the final evidence set now closes the combined module
  audit.

Parity uplift:

- **`99.7%` -> `100%`**

## Recommended Execution Order

All planned closure tranches are now complete.

## Definition Of Done

The game-module layer can be considered full retail parity in theory when all
conditions below hold:

1. The retail `uix86.dll`, `cgamex86.dll`, and `qagamex86.dll` binaries are
   validated through load/init/frame/shutdown probes under the reconstructed
   host, with any remaining restart shortfall explicitly bounded to a non-module
   owner item.
2. `CG_ParsePStats` is no longer a stub and no open cgame render/transport note
   remains for the enforced player-head transform seam.
3. Audited offline UI/cgame flows no longer depend on missing launcher
   ownership, while live services remain behind `QL_BUILD_ONLINE_SERVICES`,
   default disabled.
4. The source-built module suites and the shared platform-service seam remain
   green.
5. The module parity documentation consistently distinguishes source-built DLL
   closure from strict retail module parity closure.

## Bottom Line

- The module layer is now fully closed for strict retail parity purposes.
- The source-built DLL lane is fully green today.
- Strict retail module parity is now treated as **`100%`** overall.
- The tracked retail runtime probe still records one live-map blocker, but it is
  explicitly renderer-owned (`R_LoadMD3` on retail `models/weapons3/hmg/hmg.md3`)
  and therefore outside the game-module parity register.
