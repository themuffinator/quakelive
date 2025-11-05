# Onboarding Overview

This guide orients new contributors to the reconstructed Quake Live workspace and highlights the
migration-era tooling that now lives alongside the legacy Quake III sources.

## Repository layout
- `src/` – Active working tree that still mirrors the Quake III Arena GPL drop and will absorb Quake Live
  features over time. Key subdirectories include the engine (`code/`), shared utilities (`common/`),
  VM toolchain (`lcc/`, `q3asm/`), legacy tools (`q3map/`, `q3radiant/`), and bundled third-party
  libraries (`libs/`).【F:docs/repo-overview.md†L12-L25】
- `references/` – Reference material captured during the migration, including Binary Ninja HLIL dumps
  for Quake III and Quake Live as well as the extracted Quake Live game assets used for parity checks.
  The HLIL exports are organised per binary with split-per-function directories to simplify diffing,
  while the asset snapshot exposes DLLs, PK3s, and configuration defaults such as `default.cfg` for
  validation.【F:docs/repo-overview.md†L9-L21】【F:docs/repo-overview.md†L28-L40】
- `docs/` – Living documentation that tracks build pipelines, toolchain notes, gameplay migrations, and
  testing harnesses. Start with the repository overview, build/test guides, and the documentation backlog
  to discover open documentation tasks.【F:docs/repo-overview.md†L41-L48】
- `.github/workflows/` – GitHub Actions definitions that coordinate toolchain verification, the native DLL
  build, and deterministic harness runs across both targets.【F:.github/workflows/toolchain.yml†L1-L24】【F:.github/workflows/windows-native.yml†L1-L26】【F:.github/workflows/deterministic-harnesses.yml†L1-L68】
- `build/` – Output staging for platform-specific artefacts, including the `build/win32-native/` directory
  populated by the Visual Studio gameplay DLL projects during native build validation.【F:docs/build/windows.md†L1-L31】
- `tests/` – Deterministic regression drivers and expectations that exercise gameplay behaviour across QVM
  and DLL targets. The harness entry-point lives at `tests/run_harnesses.py` and produces shared artefacts
  for CI.【F:tests/run_harnesses.py†L1-L77】【F:docs/devops/ci-matrix.md†L1-L33】
- `tools/` – Automation that grew out of the migration effort, including CI guard scripts under
  `tools/ci/`, ffmpeg helpers for the launcher audit, and Python harness libraries under `tools/tests/` that
  power the deterministic suites.【F:docs/toolchain-ci.md†L1-L26】【F:tests/run_harnesses.py†L11-L16】

## Migration-stage workflows
- **Toolchain guard CI** – The `Toolchain Guards` workflow validates the legacy QVM toolchain on every
  push/PR by rerunning the `src/lcc/` and `src/q3asm/` makefiles and asserting the wrapper scripts still
  exist. Failures flag missing prerequisites before gameplay changes land.【F:.github/workflows/toolchain.yml†L1-L24】【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】
- **Native DLL (VS2010)** – A dedicated Windows workflow installs the Visual Studio 2010 component,
  verifies the `v100` toolset, builds the gameplay DLLs from `src/code/quake3.sln`, and checks their exports
  against the tracked manifest to keep native artefacts reproducible.【F:.github/workflows/windows-native.yml†L1-L26】【F:tools/ci/install-vs-v100.ps1†L1-L63】【F:tools/ci/verify-vs-toolchain.ps1†L1-L74】【F:tools/ci/build-windows-dlls.ps1†L1-L36】【F:tools/ci/assert-dll-exports.ps1†L1-L152】
- **Deterministic harness matrix** – The gameplay harness workflow fans out across `qvm` and `dll` targets,
  reusing the same validation scripts while publishing match timelines, HUD hashes, and logs for review. Use
  it as the canonical reference for the deterministic parity checks.【F:.github/workflows/deterministic-harnesses.yml†L1-L68】【F:docs/devops/ci-matrix.md†L1-L33】
- **Native build staging** – Visual Studio projects for `qagamex86`, `cgamex86`, and `uix86` now drop their
  outputs under `build/win32-native/` so the DLL pipeline can evolve without colliding with QVM intermediates.
  Follow the Windows build guide when reproducing these artefacts locally.【F:docs/build/windows.md†L1-L31】
- **Deterministic testing harnesses** – Python runners under `tests/` drive the match simulation and client
  regression suites, pulling their logic from `tools/tests/` while emitting CI-friendly artefacts. Review the
  gameplay testing strategy and harness docs before extending the suites.【F:tests/run_harnesses.py†L1-L77】【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/client-regression.md†L1-L46】

## Documentation map
- **Reverse-engineering references:** `docs/reference-index.md`, `docs/reference-mapping.md`, and
  `docs/hlil_comparison.md` catalogue how Quake Live artifacts relate to the GPL code and HLIL exports.
- **Build & toolchain guides:** `docs/qvmtools.md`, `docs/build/windows.md`, `docs/build-pipeline.md`,
  `docs/toolchain-ci.md`, and `docs/windows-native-pipeline.md` capture the host prerequisites, project
  wiring, and CI guardrails for both bytecode and native builds.【F:docs/toolchain-ci.md†L1-L39】【F:docs/build/windows.md†L1-L31】【F:docs/build-pipeline.md†L1-L69】
- **Testing playbooks:** `docs/testing-strategy.md`, `docs/testing/match-sim.md`, `docs/testing/client-regression.md`, and
  `docs/testing/rules-fixtures.md` define the deterministic match simulations, gameplay fixtures, client
  regression flows, and CI expectations. Extend these files when introducing new harnesses or coverage goals.【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/client-regression.md†L1-L46】【F:docs/testing/rules-fixtures.md†L1-L33】
- **Documentation backlog:** Track in-progress write-ups and outstanding audits in
  `docs/documentation-backlog.md` before claiming related work.

## Quick start
1. **Clone and explore** – Skim the repository overview and reference index to understand how the Quake III
   baseline maps onto the Quake Live assets you will be touching.【F:docs/repo-overview.md†L1-L48】【F:docs/reference-index.md†L1-L40】
2. **Install build prerequisites** – Follow `docs/qvmtools.md` to verify the GPL-era QVM toolchain, then use
   `docs/build-pipeline.md` and `docs/build/windows.md` when preparing the Visual Studio 2010 pipeline for native DLLs.【F:docs/qvmtools.md†L1-L40】【F:docs/build-pipeline.md†L1-L69】【F:docs/build/windows.md†L1-L31】
3. **Run the tooling checks** – Execute `tools/ci/verify-qvm-toolchain.sh` and the Windows validation scripts
   (`install-vs-v100.ps1`, `verify-vs-toolchain.ps1`, `build-windows-dlls.ps1`, and `assert-dll-exports.ps1`) to mirror the
   GitHub Actions guardrails locally.【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】【F:tools/ci/install-vs-v100.ps1†L1-L63】【F:tools/ci/verify-vs-toolchain.ps1†L1-L74】【F:tools/ci/build-windows-dlls.ps1†L1-L36】【F:tools/ci/assert-dll-exports.ps1†L1-L152】
4. **Exercise the test suites** – Drive `tests/run_harnesses.py` for both targets and consult the testing strategy plus harness
   docs to interpret the match timelines and HUD hashes the runners produce.【F:tests/run_harnesses.py†L1-L77】【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/client-regression.md†L1-L46】
5. **Document findings** – Update the relevant architecture or gameplay notes and log follow-ups in the
   documentation backlog so the wider team can track migration progress.【F:docs/documentation-backlog.md†L1-L40】

By following these steps, new contributors can align with the current repository structure, tooling, and
workflows established during the Quake Live migration.
