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
- `tools/` – Automation that grew out of the migration effort, including CI guard scripts under
  `tools/ci/`, ffmpeg helpers for the launcher audit, and Python harnesses under `tools/tests/` that power
  the deterministic match simulations.【F:docs/toolchain-ci.md†L7-L22】【F:docs/testing/match-sim.md†L1-L17】

## Migration-stage workflows
- **Toolchain guard CI** – The `Toolchain Guards` GitHub Actions workflow runs on every push/PR and
  ensures both the historical QVM toolchain and the new native DLL references stay reproducible. The
  Ubuntu job re-validates `src/q3asm` and `src/lcc` makefiles and checks that the VM wrapper scripts still
  exist, while the Windows job enforces the Visual Studio 2010 toolset and inspects the archived Quake Live
  DLL exports.【F:.github/workflows/toolchain.yml†L1-L24】【F:tools/ci/verify-qvm-toolchain.sh†L1-L41】【F:tools/ci/verify-vs-toolchain.ps1†L1-L58】【F:tools/ci/verify-dll-exports.ps1†L1-L69】
- **Native build staging** – Visual Studio projects for `qagamex86`, `cgamex86`, and `uix86` now drop their
  outputs under `build/win32-native/` so the DLL pipeline can evolve without colliding with QVM intermediates.
  Use the MSBuild targets documented in the Windows build guide when reproducing these artifacts locally.【F:docs/build/windows.md†L1-L31】
- **Deterministic testing harnesses** – Python and C test runners live under `tools/tests/` and
  `src/code/game/tests/` to keep gameplay validations in sync across QVM and DLL builds. Consult the testing
  strategy and harness documentation before extending the suites.【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/rules-fixtures.md†L1-L33】

## Documentation map
- **Reverse-engineering references:** `docs/reference-index.md`, `docs/reference-mapping.md`, and
  `docs/hlil_comparison.md` catalogue how Quake Live artifacts relate to the GPL code and HLIL exports.
- **Build & toolchain guides:** `docs/qvmtools.md`, `docs/build/windows.md`, `docs/toolchain-ci.md`, and
  `docs/windows-native-pipeline.md` capture the host prerequisites, project wiring, and CI guardrails for
  both bytecode and native builds.【F:docs/toolchain-ci.md†L1-L24】【F:docs/build/windows.md†L1-L31】
- **Testing playbooks:** `docs/testing-strategy.md`, `docs/testing/match-sim.md`, and
  `docs/testing/rules-fixtures.md` define the deterministic match simulations, gameplay fixtures, and CI
  expectations. Extend these files when introducing new harnesses or coverage goals.【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/rules-fixtures.md†L1-L33】
- **Documentation backlog:** Track in-progress write-ups and outstanding audits in
  `docs/documentation-backlog.md` before claiming related work.

## Quick start
1. **Clone and explore** – Skim the repository overview and references to understand how the Quake III
   baseline maps onto the Quake Live assets you will be touching.【F:docs/repo-overview.md†L1-L40】
2. **Install build prerequisites** – Follow `docs/qvmtools.md` to verify the GPL-era QVM toolchain, then use
   `docs/build/windows.md` if you need the Visual Studio 2010 pipeline for native DLLs.【F:docs/qvmtools.md†L1-L40】【F:docs/build/windows.md†L1-L31】
3. **Run the tooling checks** – Execute `tools/ci/verify-qvm-toolchain.sh` (or inspect the CI run) and the
   Windows verification scripts to ensure your host matches the expectations baked into the GitHub workflow.【F:tools/ci/verify-qvm-toolchain.sh†L1-L41】【F:tools/ci/verify-vs-toolchain.ps1†L1-L58】
4. **Exercise the test suites** – Use the testing strategy and harness docs to drive the Python match
   simulations and gameplay fixtures before landing changes. The deterministic runners keep the bytecode and
   native implementations aligned.【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/rules-fixtures.md†L1-L33】
5. **Document findings** – Update the relevant architecture or gameplay notes and log follow-ups in the
   documentation backlog so the wider team can track migration progress.【F:docs/documentation-backlog.md†L1-L40】

By following these steps, new contributors can align with the current repository structure, tooling, and
workflows established during the Quake Live migration.
