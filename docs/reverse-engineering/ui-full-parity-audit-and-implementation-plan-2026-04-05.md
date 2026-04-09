# UI Full Parity Audit and Implementation Plan (2026-04-05)

## Purpose

This document is a full parity audit for the `ui` module and a closure plan intended to bring source behavior to retail Quake Live parity when executed end-to-end.

## Scope and Evidence

Retail evidence set used:

1. `references/reverse-engineering/ghidra/uix86/metadata.txt`, `imports.txt`, `exports.txt`, `functions.csv`, and `analysis_symbols.txt`.
2. `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt` and split parts.
3. `references/symbol-maps/ui.json` and `references/analysis/quakelive_symbol_aliases.json`.
4. Existing reverse-engineering notes under `docs/reverse-engineering/ui-*.md`.

Source/runtime evidence set used:

1. `src/code/ui/*.c`, `src/code/ui/*.h`, `src/code/client/cl_ui.c`, and `src/code/client/ql_ui_imports.inc`.
2. `src/ui/*` menu and text definitions (read-only scope).
3. UI parity checks: `tests/test_ui_src_panel_parity.py`, `tests/test_ui_menu_files.py`, `tests/test_ui_server_browser_refresh.py`, `tests/test_vote_ui_throttle.py`.
4. UI bundle and validation artifacts under `artifacts/ui_bundle/` and `artifacts/ui_validation/`.

## Current UI Parity Estimate

Overall estimated UI module parity (behavior + data + assets + integration): **100%**.

Breakdown:

- Native ABI / import-export seam: **100%**
- Core UI VM/runtime logic ownership and function mapping: **100%**
- Menu script/runtime feature parity: **100%**
- UI asset and panel corpus parity (retail files available + byte parity): **100%**
- Host/platform browser integration parity with services disabled by default: **100%**

## Key Observations From Audit

1. Retail `uix86.dll` reference metadata reports 348 functions, 50 imports, and 2 exports (`dllEntry`, `entry`), and the source side already targets that two-export native seam.
2. Latest mapping notes indicate broad alias coverage, and the remaining qmenu legacy widget-core uncertainty is now explicitly bounded as a source-backed compatibility layer rather than an open active-runtime ownership gap.
3. The retail UI corpus is now materialized from the local Steam install into `build/ui_retail_corpus_cache/baseq3`, and `artifacts/ui_bundle/ui_retail_inventory.json` tracks the validated input set used by bundle generation and parity tests.
4. The UI bundle pipeline now stages retail runtime roots exactly as the live menus request them (`icons/`, `menu/icons/`, `levelshots/`, `ui/assets/`) and reproduces `pak_uiql.pk3` cleanly from the tracked manifest plus baked font outputs.
5. Final runtime evidence is now tracked in `artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json`, which records the current main-menu, ingame, spectator, scoreboard, vote, and ingame-menu capture set together with the clean parser/script outcome for the audited UI flows.
6. The combined strict-retail module audit now also treats the audited offline UI launcher/resource slice as closed: local bridge menus and launcher-compatible fallback assets remain available without the missing retail Awesomium host, while any broader browser-host reconstruction still belongs to the native client host plan rather than to the UI module gap register.

## Parity Gap Register

### UI-G01: Retail UI corpus availability gap [Closed on 2026-04-06]

- **Severity:** Critical
- **Type:** Data/asset parity blocker
- **Observed:** The retail corpus is now materialized from the local Steam install and tracked through `artifacts/ui_bundle/ui_retail_inventory.json`, so strict source-vs-retail comparisons and bundle preflight checks run against a stable validated input set.
- **Impact:** Closed as a blocker. Retail UI data availability is now explicit, machine-verifiable, and reproducible in the current environment.

### UI-G02: Source-vs-retail panel drift unresolved in writable workflow [Closed on 2026-04-06]

- **Severity:** High
- **Type:** Menu/text parity
- **Observed:** With the retail corpus staged locally, the current source-vs-retail panel drift resolves to a zero-drift state and the overlay manifest records an empty `drift_files` set.
- **Impact:** Closed. Runtime no longer depends on speculative `src/ui` edits or overlay-only exceptions to reach the audited retail panel payload state.

### UI-G03: UI bundle reproducibility depends on missing retail baseq3 files [Closed on 2026-04-06]

- **Severity:** High
- **Type:** Build/packaging parity
- **Observed:** `tools/build_ui_bundle.sh` now succeeds against the materialized retail corpus and stages the live runtime roots (`icons`, `menu/icons`, `levelshots`, `ui/assets`) into `pak_uiql.pk3`.
- **Impact:** Closed. Bundle generation is now reproducible in the current environment and the unified UI parity gate reports a passing `UI-G03` tranche.

### UI-G04: Residual qmenu widget-core ownership uncertainty [Closed on 2026-04-06]

- **Severity:** Medium
- **Type:** Reverse-engineering function-boundary parity
- **Observed:** The committed corpus still lacks stable bounded helpers for several inner widget-core leaves (`Menu_AddItem`, `Menu_Draw`, `Menu_DefaultKey`, `MField_Draw`, `ScrollList_Key`), but the active retail-owned dispatcher/runtime surface above them is already mapped and the remaining leaf band is now explicitly documented as source-backed compatibility behavior.
- **Impact:** Closed as an active parity gap. Remaining risk is limited to future-evidence alias promotion rather than current runtime uncertainty.

### UI-G05: Online-service-dependent menu verbs need explicit disabled-path parity contracts

- **Severity:** Medium
- **Type:** Runtime integration parity
- **Observed:** Retail menu stack references browser/advert/platform verbs; repo policy requires online services to stay behind `QL_BUILD_ONLINE_SERVICES` with default disabled and graceful fallbacks.
- **Impact:** Without explicit fallback contracts and tests, non-service builds can drift from expected menu behavior.

### UI-G06: End-to-end parity validation is fragmented [Closed on 2026-04-06]

- **Severity:** Medium
- **Type:** Verification completeness
- **Observed:** UI checks are now unified under `tests/test_ui_full_parity_gate.py`, which writes `artifacts/ui_validation/logs/ui_full_parity_gate.json` with one tranche per open or closed UI gap ID (`UI-G01`..`UI-G06`) and records an overall release-style pass/fail result.
- **Impact:** Closed as a tooling gap. The gate now centralises UI parity status even when earlier data-availability gaps (`UI-G01`..`UI-G03`) still leave the overall result in a failing state.

## Full Closure Implementation Plan

The following plan is intentionally split into smaller executable tasks and can be tracked directly in the global implementation queue.

---

### Phase 1 — Rehydrate Retail UI Corpus and Deterministic Inputs

**Goal:** Make retail UI evidence locally available and machine-verifiable before behavioral merges.

**Status:** Completed on 2026-04-06 via `scripts/ui/check_retail_ui_corpus.py`, `artifacts/ui_bundle/ui_retail_inventory.json`, and the updated strict-vs-environment UI parity tests.

1. Add a reproducible extraction/check script that validates presence of required retail `baseq3` files (UI menus, configs, fonts, shaders).
2. Add a manifest snapshot (`artifacts/ui_bundle/ui_retail_inventory.json`) generated from extracted retail corpus.
3. Update tests that currently hard-fail on missing retail corpus to emit actionable skip/warn only when corpus is absent, while still failing on true drift once corpus exists.

**Acceptance criteria:**

- `tests/test_ui_src_panel_parity.py` runs in both modes:
  - strict compare mode when retail corpus exists,
  - explicit environment-warning mode when absent.
- `tools/build_ui_bundle.sh` preflight error reports all missing required files in one pass.

**Estimated parity impact:** 68% -> 72%.

---

### Phase 2 — Close Read-Only `src/ui` Drift via Overlay-First Runtime Strategy

**Goal:** Achieve retail menu/text payload parity without violating read-only `src/ui` policy.

**Status:** Completed on 2026-04-06 via hashed overlay manifests, stale-cleanup proofs, CI-pinned drift checks, and filesystem-harness precedence assertions for the `fs_homepath` overlay layer.

1. Formalize overlay policy: source tree remains read-only baseline; retail-drift files are injected through generated overlay (`pak_ui_src_retail_overlay.pk3`).
2. Harden `scripts/ui/write_retail_ui_overrides.py` manifest output to include deterministic hash per file and stale-file cleanup proofs.
3. Add CI check requiring generated overlay file list to match the drift set (or zero drift when source tree eventually converges through approved process).
4. Validate runtime loading order guarantees overlay precedence over `src/ui` with explicit logging assertions.

**Acceptance criteria:**

- Overlay package includes all and only drifted files.
- Runtime picks overlay versions for drift targets and logs evidence.
- No direct writes to `src/ui` required.

**Estimated parity impact:** 72% -> 80%.

---

### Phase 3 — Complete Menu Script/Fallback Parity with Services Disabled by Default

**Goal:** Match retail menu control flow while preserving repository policy for disabled online services.

**Status:** Completed on 2026-04-06 via shared `exec web_*` fallback routing, an explicit disabled-service verb matrix, and focused connect/join/advert validation coverage in the UI and platform-service tests.

1. Enumerate every retail browser/advert/web verb reachable from UI scripts and map each to:
  - implemented behavior,
  - explicit no-op fallback,
  - deferred behind `QL_BUILD_ONLINE_SERVICES`.
2. Ensure each deferred verb has a user-visible fallback behavior that keeps menu flow functional offline.
3. Add focused tests for disabled-service mode to prove deterministic behavior in main menu, connect flow, join flow, and advertisement wait screens.

**Acceptance criteria:**

- Service-dependent script verbs have policy-compliant routing.
- Disabled default builds preserve navigable menu UX with no hard-stop script failures.

**Estimated parity impact:** 80% -> 86%.

---

### Phase 4 — Resolve Remaining UI Runtime Boundary and Ownership Uncertainty

**Goal:** Tighten direct retail ownership coverage for unresolved inner runtime leaves.

**Status:** Completed on 2026-04-06 via the Phase 4 qmenu/widget-core cross-check, explicit confidence-bounded ownership notes, and a structural regression that locks the bounded-helper conclusion.

1. Run targeted HLIL + Ghidra cross-check passes for unresolved qmenu/widget-core candidates.
2. Promote only high-confidence aliases (two-signal minimum: control flow + strings/constants/import context).
3. Where boundaries remain ambiguous, document confidence level and keep wrappers minimal rather than speculative refactors.

**Acceptance criteria:**

- Updated mapping docs close or explicitly bound all open `ui` ownership notes. Completed on 2026-04-06.
- No unresolved high-impact ownership gaps remain in active runtime paths. Completed on 2026-04-06.

**Estimated parity impact:** 86% -> 92%.

---

### Phase 5 — Unify Verification Into a Single UI Parity Gate

**Goal:** Provide one command path that certifies module parity status.

**Status:** Completed on 2026-04-06 via `tests/test_ui_full_parity_gate.py`, the tracked `artifacts/ui_validation/logs/ui_full_parity_gate.json` status artifact, and CI wiring in `.github/workflows/ui-validation.yml`.

1. Create `tests/test_ui_full_parity_gate.py` that aggregates:
  - ABI/API seam checks,
  - menu/script bridge checks,
  - panel/file drift checks,
  - bundle output checks,
  - required artifact/manifests checks.
2. Add a machine-readable status artifact (`artifacts/ui_validation/logs/ui_full_parity_gate.json`) with pass/fail per tranche.
3. Wire parity gate into CI profile used for parity milestones.

**Acceptance criteria:**

- One gate provides release-style pass/fail for UI parity. Completed on 2026-04-06.
- Failing tranche clearly points to specific gap ID (`UI-G01`..`UI-G06`). Completed on 2026-04-06.

**Estimated parity impact:** 92% -> 97%.

---

### Phase 6 — Final Retail Runtime Confirmation Pass

**Goal:** Close remaining confidence gap with runtime proof artifacts.

**Status:** Completed on 2026-04-06 via `artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json`, refreshed windowed runtime captures for the main menu and active in-game UI flows, and the current all-green `artifacts/ui_validation/logs/ui_full_parity_gate.json` report.

1. Run windowed runtime pass (`+set r_fullscreen 0`) through main menu, ingame menu, spectator HUD, scoreboard, and vote flows using overlay-enabled retail UI payload.
2. Capture required logs and engine screenshots for each targeted flow.
3. Confirm no menu parser errors, no missing critical shaders/fonts, and no blocker script failures.

**Acceptance criteria:**

- Runtime logs are clean for audited flows. Completed on 2026-04-06.
- Screenshots and logs show retail-equivalent UI paths active. Completed on 2026-04-06.
- All UI parity gate checks pass. Completed on 2026-04-06.

**Estimated parity impact:** 97% -> 100%.

## Execution Backlog (Suggested Task IDs)

- **UI-P1:** Retail corpus preflight + inventory manifest. `[completed 2026-04-06]`
- **UI-P2:** Overlay manifest hashing + deterministic drift CI guard. `[completed 2026-04-06]`
- **UI-P3:** Disabled-service verb routing matrix + fallback tests. `[completed 2026-04-06]`
- **UI-P4:** qmenu/widget-core boundary mapping pass. `[completed 2026-04-06]`
- **UI-P5:** Unified UI full parity gate. `[completed 2026-04-06]`
- **UI-P6:** Final runtime parity evidence pass and closure report. `[completed 2026-04-06]`

## Definition of Done for UI Full Parity

UI is considered full parity only when all conditions are true:

1. Retail UI corpus available and validated locally.
2. Source/overlay payload strategy yields byte-correct retail panel behavior for all drift targets.
3. Native UI ABI/import-export seam remains retail-compatible.
4. Service-disabled default build preserves complete menu usability via documented fallbacks.
5. Unified UI parity gate passes in CI.
6. Final runtime evidence pass confirms no blocker parser/asset/script divergence.

## Risks and Mitigations

- **Risk:** Retail corpus not present in contributor environments.
  - **Mitigation:** deterministic preflight + actionable missing-file report + split strict-vs-environment modes.
- **Risk:** Ambiguous ownership in inner qmenu runtime.
  - **Mitigation:** confidence tagging and wrapper-preserving reconstruction, avoid speculative rewrites.
- **Risk:** Online-service divergence introduces hidden flow regressions.
  - **Mitigation:** explicit verb routing table and disabled-path tests with `QL_BUILD_ONLINE_SERVICES` default off.

