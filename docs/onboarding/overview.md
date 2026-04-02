# Onboarding Overview

This guide orients new contributors to the reconstructed Quake Live workspace and highlights the
migration-era tooling that now lives alongside the legacy Quake III sources.

## Repository layout
- `src/` – Active working tree that mirrors the Quake III Arena GPL drop and will absorb Quake Live
  features over time. Key subdirectories include the engine (`code/`), the shared utility and
  platform/auth layer (`common/`), the writable gameplay support layer (`game/`), the VM toolchain
  (`lcc/`, `q3asm/`), legacy tools (`q3map/`, `q3radiant/`), and bundled third-party libraries
  (`libs/`).【F:docs/repo-overview.md†L10-L25】
- `src-re/` – Clean-room reconstruction space used during reverse-engineering stages. It houses
  annotated walkthroughs, prototype shims, and the signed-off clean sources that are compiled via the
  clean-room build helpers and traced against Quake Live baselines. `src-re/include/` also contains
  reverse-engineered headers already consumed by parts of `src/code/`, so do not treat the whole tree
  as dead scaffolding. Use [`docs/reverse-engineering/src-re-workspace.md`](../reverse-engineering/src-re-workspace.md)
  for the promotion rules and the per-subdirectory breakdown.【F:docs/reverse-engineering/handbook.md†L7-L27】
- `tests/` – Deterministic harness entry point (`tests/run_harnesses.py`) plus reverse expectations that
  back the CI matrix for QVM, native DLL, and reverse builds.【F:tests/run_harnesses.py†L27-L111】【F:docs/devops/ci-matrix.md†L1-L18】
- `references/` – Reference material captured during the migration, including Binary Ninja HLIL dumps
  for Quake III and Quake Live as well as extracted Quake Live assets used for parity checks.【F:docs/repo-overview.md†L6-L21】
- `docs/` – Living documentation covering build pipelines, reverse-engineering stages, gameplay audits,
  and test harnesses. Start with the repository overview, the [Reverse-Engineering Handbook](../reverse-engineering/handbook.md),
  the [Deterministic CI Matrix](../devops/ci-matrix.md), and the [documentation backlog](../documentation-backlog.md) to discover
  current processes and open documentation tasks.【F:docs/repo-overview.md†L6-L38】【F:docs/reverse-engineering/handbook.md†L1-L56】【F:docs/devops/ci-matrix.md†L1-L38】【F:docs/documentation-backlog.md†L1-L29】
- `tools/` – Automation that grew out of the migration effort, including CI guard scripts under
  `tools/ci/`, deterministic harness code beneath `tools/tests/`, and container definitions used to
  reproduce historical toolchains.【F:docs/toolchain-ci.md†L1-L22】【F:tools/ci/build-cleanroom.sh†L1-L44】【F:docs/reverse-engineering/handbook.md†L21-L37】
- `artifacts/` & `logs/` – Captured outputs from deterministic harnesses, trace runs, and reverse build
  shims. CI publishes match timelines, HUD hashes, and trace diffs here so reviewers can inspect
  evidence without reproducing runs locally.【F:docs/reverse-engineering/handbook.md†L11-L27】【F:docs/devops/ci-matrix.md†L11-L18】

## Migration-stage workflows
- **Deterministic harness matrix** – The `Deterministic Harnesses` workflow fans out across QVM, DLL, and
  reverse clean-room builds. Its QVM lane validates the legacy toolchain, its DLL lane validates the
  retail-aligned Windows native pipeline, and every target runs `tests/run_harnesses.py` before
  publishing match timelines, HUD hashes, and trace diffs.【F:.github/workflows/deterministic-harnesses.yml†L10-L89】【F:tools/ci/build-cleanroom.sh†L1-L44】【F:tests/run_harnesses.py†L27-L111】
- **Filesystem regression guard** – The `Filesystem Search Paths` workflow runs the dedicated
  `FS_FOpenFileRead` regression test so PK3-vs-directory precedence changes fail fast on Ubuntu.【F:.github/workflows/filesystem-search.yml†L1-L20】【F:tests/test_fs_search_paths.py†L1-L115】
- **UI freeze guard** – The `UI Freeze Guard` workflow blocks writes to the retail `src/ui/` tree, keeping
  the read-only asset baseline intact during normal reconstruction work.【F:.github/workflows/ui-freeze.yml†L1-L17】
- **UI validation** – The `UI Validation` workflow builds the staged UI bundle, runs the headless bundle
  validator, and publishes the generated artefacts for inspection when UI-adjacent changes land.【F:.github/workflows/ui-validation.yml†L1-L37】【F:tests/run_ui_validation.py†L1-L66】
- **Reverse clean-room iterations** – Reverse targets compile the `src-re/prototypes/` shims into
  loadable modules, replay them through the trace harness, and diff the output against committed
  expectations so reconstruction work stays deterministic.【F:tools/ci/build-cleanroom.sh†L1-L44】【F:docs/reverse-engineering/handbook.md†L12-L27】【F:docs/devops/ci-matrix.md†L7-L18】

## Documentation map
- **Reverse-engineering stages:** Use `docs/reverse-engineering/handbook.md` as the index for stage
  outputs, prototype shims, clean-room drops, and review cadence, then drill into the linked notes for
  detailed walkthroughs.【F:docs/reverse-engineering/handbook.md†L1-L56】
- **Reference catalogues:** `docs/reference-index.md`, `docs/reference-mapping.md`, and
  `docs/hlil_comparison.md` map Quake Live artefacts back to the GPL code and HLIL exports.
- **Build & toolchain guides:** `docs/qvmtools.md`, `docs/build/windows.md`, `docs/build-pipeline.md`,
  `docs/toolchain-ci.md`, `docs/windows-native-pipeline.md`, and
  `docs/platform/toolchain-matrix.md` capture host prerequisites, project wiring, and CI guardrails for
  bytecode, native DLL, and reverse builds.【F:docs/build-pipeline.md†L1-L89】【F:docs/toolchain-ci.md†L1-L24】【F:docs/build/windows.md†L1-L31】【F:docs/platform/toolchain-matrix.md†L1-L27】
- **Testing playbooks:** `docs/testing-strategy.md`, `docs/testing/match-sim.md`,
  `docs/testing/client-regression.md`, `docs/testing/rules-fixtures.md`, `docs/testing/cosmetics-training.md`, and the deterministic trace
  notes in `docs/reverse-engineering/trace-harness.md` document the harness behaviours and extension
  hooks.【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/client-regression.md†L1-L55】【F:docs/testing/rules-fixtures.md†L1-L33】【F:docs/testing/cosmetics-training.md†L1-L73】【F:docs/reverse-engineering/trace-harness.md†L1-L92】
- **CI & artefact indexing:** The [Deterministic CI Matrix](../devops/ci-matrix.md) explains the harness
  matrix, emitted artefacts, and badges that surface build health across targets.【F:docs/devops/ci-matrix.md†L1-L38】
- **Documentation backlog:** Track in-progress write-ups and outstanding audits in
  `docs/documentation-backlog.md` before claiming related work.

## Quick start
1. **Clone and explore** – Skim the repository overview and the [Reverse-Engineering Handbook](../reverse-engineering/handbook.md)
   to understand how the Quake III baseline maps onto the staged Quake Live reconstructions and artefact archives.【F:docs/repo-overview.md†L1-L38】【F:docs/reverse-engineering/handbook.md†L1-L27】
2. **Install build prerequisites** – Follow `docs/qvmtools.md` to verify the GPL-era QVM toolchain, review
   the migration plan in `docs/build-pipeline.md`, and use `docs/build/windows.md` plus the native pipeline
   notes when setting up the Visual Studio 2010 workflow.【F:docs/qvmtools.md†L1-L40】【F:docs/build-pipeline.md†L1-L89】【F:docs/build/windows.md†L1-L31】【F:docs/windows-native-pipeline.md†L1-L80】
   Install the Vorbis SDKs alongside the core compiler toolchains so the client’s Ogg decoder always links:
   Linux builders can `apt install libogg-dev libvorbis-dev` (or export custom `OGG_CFLAGS`/`OGG_LDFLAGS`),
   while Windows contributors should drop the SDK headers and `vorbisfile.lib;vorbis.lib;ogg.lib` imports
   under `src/libs/vorbis` (or override the `VorbisSdkDir` property). Dedicated-only builds can set
   `QL_ENABLE_OGG=0` to skip the dependency entirely.
3. **Run the tooling checks** – Execute the CI helpers (`tools/ci/verify-qvm-toolchain.sh`,
   `tools/ci/install-vs-v100.ps1`, `tools/ci/verify-vs-toolchain.ps1`, `tools/ci/validate-windows-native.ps1`,
   and `tools/ci/build-cleanroom.sh`) or inspect the `Deterministic Harnesses`, `Filesystem Search Paths`,
   `UI Freeze Guard`, and `UI Validation` workflows to confirm your host matches the enforced
   prerequisites.【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】【F:tools/ci/install-vs-v100.ps1†L1-L63】【F:tools/ci/verify-vs-toolchain.ps1†L1-L74】【F:tools/ci/validate-windows-native.ps1†L1-L124】【F:tools/ci/build-cleanroom.sh†L1-L44】【F:.github/workflows/deterministic-harnesses.yml†L10-L89】【F:.github/workflows/filesystem-search.yml†L1-L20】【F:.github/workflows/ui-freeze.yml†L1-L17】【F:.github/workflows/ui-validation.yml†L1-L37】
4. **Exercise the test suites** – Drive the deterministic harness entry point (`python tests/run_harnesses.py`)
   alongside the match simulation, client regression, rules fixtures, and trace harness guides so bytecode,
   native DLL, and reverse builds stay in lockstep.【F:tests/run_harnesses.py†L27-L111】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/client-regression.md†L1-L55】【F:docs/testing/rules-fixtures.md†L1-L33】【F:docs/testing/cosmetics-training.md†L1-L73】【F:docs/reverse-engineering/trace-harness.md†L1-L92】
5. **Document findings** – Update the relevant architecture, gameplay, or reverse-engineering notes and log
   follow-ups in the documentation backlog so the wider team can track migration progress.【F:docs/reverse-engineering/handbook.md†L1-L56】【F:docs/documentation-backlog.md†L1-L40】
6. **Validate against the contributor checklist** – Before opening your first PR, walk through the [Contributor Checklist](../process/contributor-checklist.md) so you understand the deterministic harness, baseline refresh, and syscall contract expectations reviewers will look for.【F:docs/process/contributor-checklist.md†L1-L45】

By following these steps, new contributors can align with the current repository structure, tooling, and
workflows established during the Quake Live migration.
