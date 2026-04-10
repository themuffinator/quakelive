# `Engine` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-10

Scope: engine-owned executable surfaces in `src/code/qcommon/*`,
`src/code/client/*`, `src/code/server/*`, `src/code/renderer/*`, and the
remaining executable-owned host/support surface (`src/code/win32/*`,
`src/common/platform/*`, `src/code/botlib/*`) versus retail
`quakelive_steam.exe`. The game-module layer (`ui`, `cgame`, `qagame`) is
tracked separately as a dependency because the end-state replacement target
requires the engine host and the retail/native module contract to agree at the
same time.

Purpose: publish one authoritative current-worktree engine-wide parity audit
that aggregates the dedicated subsystem audits, the machine-readable parity
gates, the runtime evidence bundles, and the retail module-host proof into a
single closure ledger.

## Audit Method And Evidence

Owning retail executable:

- `assets/quakelive/quakelive_steam.exe`

Canonical committed evidence used for this engine-wide audit:

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
  - `docs/reverse-engineering/quakelive_steam_mapping_round_*.md`
- Dedicated subsystem audits:
  - `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
  - `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
  - `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
  - `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
  - `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Machine-readable engine gate artifacts:
  - `artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json`
  - `artifacts/client_validation/logs/client_full_parity_gate.json`
  - `artifacts/server_validation/logs/server_full_parity_gate.json`
  - `artifacts/renderer_validation/logs/renderer_full_parity_gate.json`
  - `artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json`
- Engine runtime/evidence artifacts:
  - `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
  - `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
  - `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`
  - `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260410.json`
  - `artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json`
- Dependent module evidence used to bound the replacement target:
  - `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
  - `artifacts/module_validation/logs/retail_module_parity_gate.json`
  - `artifacts/ui_validation/logs/ui_full_parity_gate.json`
  - `artifacts/module_validation/logs/retail_module_runtime_evidence_20260409.json`

Method:

1. Treat the dedicated 2026-04-09/10 subsystem audits as the primary ownership
   ledgers for their respective surfaces.
2. Reconfirm that each engine register has both a narrative closure document
   and a machine-readable gate reporting `overall_status: pass`.
3. Reconfirm that each register also has either a dedicated runtime bundle or a
   focused evidence bundle that is already accepted by the owning audit.
4. Aggregate engine gap counts directly from the gate artifacts instead of
   inventing a new synthetic scoring model.
5. Keep compatibility-only host/support surfaces explicit rather than quietly
   blending them into the strict-retail score.
6. Cross-check the retail module-host seam separately so the engine-wide
   replacement claim does not overstep the direct retail-DLL evidence.

## Committed Retail Corpus Snapshot

Retail `quakelive_steam.exe` metadata currently reports:

- function corpus: `5473`
- imports: `351`
- exports: `2`
- promoted analysis symbols: `4377`

Cross-check:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains `5473` function rows, matching the metadata snapshot.

Interpretation:

- the current engine-wide closure claim still rests on a large committed retail
  corpus, not on a narrow hint set
- the closure story is now primarily about verified owner recovery and proof
  discipline, not missing binary discovery

## Current Engine-Wide Conclusion

- Current strict engine-owned parity estimate: **100%**.
- All five engine-owned machine-readable gate artifacts report
  `overall_status: pass`.
- The aggregated engine gap surface is **31 / 31** passing gap IDs.
- The strict-retail-counted engine gap surface is **29 / 29** passing gap IDs
  once the remaining host/support compatibility-only exclusions (`EH-G03`,
  `EH-G05`) are removed per the boundary contract.
- No open engine-owned parity gap remains in the audited register for the
  current worktree.
- The module dependency layer is also closed separately at **100%**, with
  `retail_module_parity_gate.json` and `ui_full_parity_gate.json` both passing
  and the archived retail-DLL runtime probe still providing direct retail
  module-host evidence.

Important scope note:

- this document does not claim a fresh runtime uplift beyond the dedicated
  subsystem closures; it consolidates the already-closed engine registers into
  one authoritative ledger

## Engine Register Scorecard

| Register | Audit document | Current estimate | Gap status | Machine-readable gate | Runtime or evidence bundle | Current conclusion |
| --- | --- | ---: | --- | --- | --- | --- |
| `qcommon` | `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md` | `100%` | `5 / 5` passing | `artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json` | `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json` | Bootstrap, filesystem, message transport, collision leaf ownership, and VM host/fallback behavior are closed. |
| `client` | `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md` | `100%` | `5 / 5` passing | `artifacts/client_validation/logs/client_full_parity_gate.json` | `artifacts/client_validation/logs/client_runtime_evidence_20260410.json` | Browser-host runtime, Steam callback lifetime, workshop bootstrap, config persistence, and final client proof are closed. |
| `server` | `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md` | `100%` | `6 / 6` passing | `artifacts/server_validation/logs/server_full_parity_gate.json` | `artifacts/server_validation/logs/server_runtime_evidence_20260410.json` | Steam GameServer lifecycle, `idZMQ`, stat/achievement ownership, rankings compatibility, control-plane cvars, and dedicated proof are closed. |
| `renderer` | `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md` | `100%` | `9 / 9` passing | `artifacts/renderer_validation/logs/renderer_full_parity_gate.json` | `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260410.json` | Export ABI, memory-image ingestion, post-process, Win32 glue, classic font lane, host text core, build lane, and strict validation are closed. |
| Remaining engine host/support | `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md` | `100%` | `6 / 6` passing (`4 / 4` strict-retail-counted) | `artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json` | `artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json` | Win32 clipboard/raw-input, loading-window glue, botlib internal proof, and boundary formalisation are closed; compatibility-only lanes are explicit exclusions. |

## Historical Uplift By Register

No synthetic historical whole-engine percentage is published here because the
five audited registers closed on different dates and with different scoped
boundaries. The honest history is the per-register uplift shown below.

| Register | Historical strict estimate at audit publication | Current strict estimate | Final closure phase |
| --- | ---: | ---: | --- |
| `qcommon` | `87%` | `100%` | `QC-P6` |
| `client` | `90%` | `100%` | `CL-P6` |
| `server` | `74%` | `100%` | `SV-P7` |
| `renderer` | `94%` | `100%` | `RG-P11` |
| Remaining engine host/support | `79%` | `100%` | `EH-P5` plus `EH-P1` and `EH-P6` governance closure |

Interpretation:

- the engine-wide closure story is real progress across every engine-owned
  register, not a score-only reframing of one subsystem
- the lowest historical register was the server at `74%`; the current register
  set is now uniformly closed

## Detailed Findings

## 1. `qcommon`

Observed facts:

1. The dedicated qcommon audit closes `QC-G01` through `QC-G05` and tracks the
   current strict `qcommon` estimate at **100%**.
2. The ownership story is backed by the committed alias ledger plus mapping
   rounds `34`, `55`, `56`, `63`, `78`, `79`, `84`, `91`, `99`, `107`, `108`,
   and `109`.
3. `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
   proves:
   - `qzconfig.cfg` and `repconfig.cfg` execution
   - the active search-path roots
   - service-disabled launcher/resource markers
   - writable-homepath DLL loading for `ui`, `qagame`, and `cgame`
4. `artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json` records
   `5 / 5` passing tranches with no non-passing gap IDs.

Conclusion:

- no open `qcommon` gap remains in the audited engine register

## 2. `client`

Observed facts:

1. The dedicated client audit closes `CL-G01` through `CL-G05` and tracks the
   current strict `client` estimate at **100%**.
2. The writable client host now retains:
   - browser-host runtime ownership
   - `qz_instance` JS bridge and `EnginePublish` event-publication seams
   - Steam client/lobby/micro callback bundles and frame pumping
   - workshop-aware join/bootstrap ownership
   - retail `qzconfig.cfg` / `repconfig.cfg` bootstrap plus
     `writeClientConfig`
3. `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
   proves:
   - windowed main-menu UI bootstrap
   - live `qzconfig.cfg`, `repconfig.cfg`, and `writeClientConfig` output
   - explicit service-disabled browser-policy behavior
   - a live `bloodrun` local-map pass with screenshots and a flushed demo
   - clean lifecycle-end markers
4. `artifacts/client_validation/logs/client_full_parity_gate.json` records
   `5 / 5` passing tranches with no non-passing gap IDs.

Conclusion:

- no open `client` gap remains in the audited engine register
- live online services remain correctly policy-gated behind
  `QL_BUILD_ONLINE_SERVICES`; that is now an explicit repo policy surface, not
  silent missing client ownership

## 3. `server`

Observed facts:

1. The dedicated server audit closes `SV-G01` through `SV-G06` and tracks the
   current strict `server` estimate at **100%**.
2. The writable server host now retains:
   - Steam GameServer bootstrap/logon/shutdown ownership
   - server-side callback/auth-session lifetime
   - retained `idZMQ` stats-publication and remote-RCON runtime
   - qagame-facing Steam stat and achievement ownership
   - reconstructed control-plane cvar and policy surface
   - a documented default-disabled rankings compatibility contract
3. `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`
   proves:
   - dedicated startup
   - qagame load
   - network-visible `getstatus` publication
   - local `rcon` status and clean quit
   - optional Steam and `idZMQ` markers recorded honestly as environment-driven
     booleans
4. `artifacts/server_validation/logs/server_full_parity_gate.json` records
   `6 / 6` passing tranches with no non-passing gap IDs.

Conclusion:

- no open `server` gap remains in the audited engine register

## 4. `renderer`

Observed facts:

1. The dedicated renderer audit closes `RG-G01` through `RG-G09` and tracks the
   current strict `renderer` estimate at **100%**.
2. The writable renderer now retains:
   - the retail `GetRefAPI` export tail
   - in-memory image/resource ingestion
   - shader-backed post-process and color-correction passes
   - Win32 resize/loading-window glue
   - the classic font/cache/atlas lane
   - the retained `*fontstash` host text engine
   - native `ui` and `cgame` host text import switchover
   - an explicit external FreeType build lane
3. `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260410.json`
   proves:
   - windowed main-menu bootstrap
   - retained-atlas debug rendering through `r_debugFontAtlas`
   - live `bloodrun` runtime
   - expected renderer init markers including `InitFreeType` and
     `InitFontStash`
   - no fallback to compatibility-only `RE_RegisterFont` runtime paths
4. `artifacts/renderer_validation/logs/renderer_full_parity_gate.json`
   records `9 / 9` passing tranches with no non-passing gap IDs.

Conclusion:

- no open `renderer` gap remains in the audited engine register

## 5. Remaining Engine Host/Support

Observed facts:

1. The dedicated remaining host/support audit closes `EH-G01` through
   `EH-G06` and tracks the current strict remaining-engine host/support
   estimate at **100%**.
2. The writable host now retains:
   - Unicode-first clipboard fetch with ANSI fallback
   - active Win32 raw-input registration and `WM_INPUT` dispatch
   - retained loading-window and bootstrap wrapper ownership
   - representative botlib internal proof for AAS/reachability/goal-state
     helpers
3. `artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json`
   binds those closures to focused tests and source owners instead of relying
   on broad narrative confidence alone.
4. `artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json`
   records:
   - `6 / 6` passing tranches overall
   - explicit scope boundary metadata
   - `EH-G03` and `EH-G05` as compatibility-only exclusions
   - `EH-G01`, `EH-G02`, `EH-G04`, and `EH-G06` as the strict-retail-counted
     host/support set

Conclusion:

- no open strict-retail host/support gap remains outside `qcommon`,
  `client`, `server`, and `renderer`
- the compatibility-only platform-service abstractions and the Unix/null trees
  remain visible, but they are now documented exclusions rather than open
  engine parity debt

## 6. Module Dependency Snapshot

Observed facts:

1. `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
   tracks the current strict retail module estimate at **100%**.
2. `artifacts/module_validation/logs/retail_module_parity_gate.json` records
   `3 / 3` passing module tranches with `overall_status: pass`.
3. `artifacts/ui_validation/logs/ui_full_parity_gate.json` records
   `6 / 6` passing UI tranches with `overall_status: pass`.
4. `artifacts/module_validation/logs/retail_module_runtime_evidence_20260409.json`
   still proves direct retail-DLL host loading for retail `uix86.dll`,
   `qagamex86.dll`, and `cgamex86.dll` under the reconstructed host.
5. The only bounded live-map shortfall archived in that retail module runtime
   probe was explicitly renderer-owned, and the renderer register is now closed
   separately in the current worktree.

Conclusion:

- the module dependency layer is not an active blocker for the current
  engine-wide replacement target
- the authoritative current state is that both the engine-owned registers and
  the module dependency registers are closed, even though the direct retail
  module runtime artifact remains archived under its 2026-04-09 filename

## Open Gap Register

Open engine-owned strict-retail gaps:

- none

Explicit non-gap exclusions that remain visible:

- `EH-G03`: compatibility-only platform-service abstractions
- `EH-G05`: Unix/null compatibility ports
- live online-service activation remains policy-gated behind
  `QL_BUILD_ONLINE_SERVICES`

Active remaining repo work outside this engine register:

- `IMPLEMENTATION_PLAN.md` Task 23: ownerdraw/stat payload completion and
  runtime validation
- `IMPLEMENTATION_PLAN.md` Task 24: targeted gameplay validation sweep

## Implementation Plan

No open engine-specific closure phase remains. The correct execution plan after
this audit is maintenance and evidence discipline, not another broad engine
reconstruction tranche.

Standing execution order:

1. Keep the five engine gates authoritative. Whenever engine-owned code changes
   one of the audited contracts, refresh the owning gate artifact first.
2. Refresh runtime evidence only when the active host contract changes, and use
   the dedicated subsystem probes instead of ad-hoc broad reruns:
   - qcommon: `tools/qcommon/run_qcommon_runtime_probe.ps1`
   - client: `tools/client/run_client_runtime_probe.ps1`
   - server: `tools/server/run_server_runtime_probe.ps1`
   - renderer: `tools/renderer/run_renderer_runtime_probe.ps1`
   - remaining host/support: focused harness surface plus
     `artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json`
3. Reopen only the owning subsystem register when a gate fails or new retail
   evidence contradicts the current source owner; do not reopen the whole
   engine ledger speculatively.
4. Keep compatibility-only lanes explicitly out of the strict-retail score
   unless repo policy changes:
   - `src/common/platform/platform_services.c`
   - `src/common/platform/backends/platform_backend_open_steam.c`
   - `src/common/platform/backends/platform_backend_steamworks.c`
   - `src/code/unix/*`
   - `src/code/null/*`
   - live online services behind `QL_BUILD_ONLINE_SERVICES`
5. Keep the top-level active queue focused on non-engine remaining work:
   ownerdraw/stat payload completion, targeted gameplay validation, and normal
   gate/runtime refresh whenever audited contracts change.

## Bottom Line

The reconstructed engine executable no longer has an open strict-retail parity
gap in the current audited register. `qcommon`, `client`, `server`,
`renderer`, and the remaining engine host/support scope are all closed with
machine-readable gates and runtime or focused-evidence bundles, and the module
dependency layer is also closed separately.

The practical next step is no longer broad engine reconstruction. It is
disciplined maintenance: keep the subsystem gates green, refresh the dedicated
probes when audited contracts change, and spend active development effort on
the remaining gameplay/ownerdraw validation work outside this engine register.
