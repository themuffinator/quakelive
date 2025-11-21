# Reverse Engineering Track Onboarding Guide

Welcome to the Quake Live reverse-engineering track. This guide walks you through the
required environment setup, curated reading order, and starter tasks that will help
you contribute effectively to the reconstruction effort.

## Environment setup checklist

1. **Clone the repository**
   ```bash
   git clone https://github.com/quakelive-reverse/quakelive-reverse.git
   cd quakelive-reverse
   ```
   Using the HTTPS URL avoids SSH key prompts for newcomers who have not yet
   configured GitHub authentication.
2. **Install and verify the QVM toolchain**
   - Follow the Linux build instructions in [`docs/qvmtools.md`](../qvmtools.md) to
     install `gcc-multilib`, `make`, and the patched LCC toolchain, then execute
     `tools/ci/verify-qvm-toolchain.sh` to confirm the bytecode compilers match the
     CI reference output.【F:docs/qvmtools.md†L1-L38】【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】
   - Review the guardrails captured in [`docs/toolchain-ci.md`](../toolchain-ci.md)
     so you understand how CI enforces toolchain parity on every push.【F:docs/toolchain-ci.md†L1-L24】
3. **Provision native build prerequisites (recommended)**
   - Work through [`docs/build/windows.md`](../build/windows.md) and the pipeline
     notes in [`docs/windows-native-pipeline.md`](../windows-native-pipeline.md) to
     prepare the Visual Studio 2010 environment.【F:docs/build/windows.md†L1-L31】【F:docs/windows-native-pipeline.md†L1-L64】
   - Validate the host by running `tools/ci/install-vs-v100.ps1` followed by
     `tools/ci/verify-vs-toolchain.ps1`; the scripts mirror the CI workflow so
     local DLL builds stay aligned.【F:tools/ci/install-vs-v100.ps1†L1-L63】【F:tools/ci/verify-vs-toolchain.ps1†L1-L74】
   - If you cannot provision a Windows host, build against the container recipes
     in [`tools/containers/msvc-2010.Dockerfile`](../../tools/containers/msvc-2010.Dockerfile)
     or partner with a teammate who can validate the DLL artefacts.【F:docs/reverse-engineering/build-recapture.md†L41-L70】
4. **Set up analysis tooling**
   - Install Ghidra 10.3 or later for binary diffing and HLIL export comparison,
     and configure Binary Ninja with the Quake-specific HLIL projects stored under
     `references/hlil/` for side-by-side analysis.【F:docs/reverse-engineering/handbook.md†L7-L24】
   - Review the deterministic trace harness overview so you know how the logs in
     `artifacts/tests/` and `logs/` are produced during reconstruction work.【F:docs/reverse-engineering/handbook.md†L15-L33】
5. **Bootstrap deterministic testing harnesses**
   - Create a Python virtual environment, install harness dependencies with
     `pip install -r tools/tests/requirements.txt`, and familiarise yourself with
     the entry point in `tests/run_harnesses.py` that powers the CI matrix.【F:tests/run_harnesses.py†L27-L116】
   - Execute `python tests/run_harnesses.py --target qvm` (or the DLL/reverse
     variants) to validate your environment matches the deterministic harness
     workflow documented in [`docs/devops/ci-matrix.md`](../devops/ci-matrix.md).【F:docs/devops/ci-matrix.md†L1-L34】

## Recommended reading order

1. **Onboarding overview** – Start with [`docs/onboarding/overview.md`](overview.md)
   for the high-level workflow summary, repository layout, and migration-era
   automation now wired into CI.【F:docs/onboarding/overview.md†L1-L53】
2. **Repository overview** – Continue with [`docs/repo-overview.md`](../repo-overview.md)
   to understand how Quake Live artefacts map onto the GPL code drop and where
   the reconstructed sources, logs, and artefacts live today.【F:docs/repo-overview.md†L6-L41】
3. **Reverse-engineering handbook** – Dive into [`docs/reverse-engineering/handbook.md`](../reverse-engineering/handbook.md)
   plus the reconstruction tracker to see stage outputs, clean-room drops, and
   review cadence expectations.【F:docs/reverse-engineering/handbook.md†L1-L60】
4. **Build, toolchain, and CI guides** – Work through [`docs/qvmtools.md`](../qvmtools.md),
   [`docs/build/windows.md`](../build/windows.md), [`docs/windows-native-pipeline.md`](../windows-native-pipeline.md), and
   [`docs/toolchain-ci.md`](../toolchain-ci.md) so you understand the guardrails
   that keep bytecode, DLL, and reverse builds aligned.【F:docs/qvmtools.md†L1-L38】【F:docs/build/windows.md†L1-L31】【F:docs/windows-native-pipeline.md†L1-L64】【F:docs/toolchain-ci.md†L1-L24】
5. **Deterministic testing playbooks** – Finish with [`docs/testing-strategy.md`](../testing-strategy.md),
   [`docs/testing/match-sim.md`](../testing/match-sim.md), [`docs/testing/client-regression.md`](../testing/client-regression.md),
   [`docs/testing/rules-fixtures.md`](../testing/rules-fixtures.md), and the
   harness matrix in [`docs/devops/ci-matrix.md`](../devops/ci-matrix.md) to see
   how gameplay fixtures and trace captures prove functional parity.【F:docs/testing-strategy.md†L1-L43】【F:docs/testing/match-sim.md†L1-L45】【F:docs/testing/client-regression.md†L1-L55】【F:docs/testing/rules-fixtures.md†L1-L33】【F:docs/devops/ci-matrix.md†L1-L34】

## Starter tasks

- **Baseline parity audit** – Choose a gameplay system (e.g., weapon prediction or
  item respawn logic) and confirm the reconstructed source matches the Quake Live
  HLIL dump. Capture findings in `docs/reverse-engineering/` with before/after
  snippets and note any unknown branches in the reconstruction tracker.【F:docs/reverse-engineering/reconstruction-tracker.md†L1-L40】
- **Harness enrichment** – Extend the deterministic harness suite (match simulation,
  client regression, rules fixtures, or trace harness) with an additional edge
  case, update `tests/run_harnesses.py`, and document the scenario in the testing
  playbooks so CI publishes new artefacts for review.【F:tests/run_harnesses.py†L27-L116】【F:docs/devops/ci-matrix.md†L1-L34】【F:docs/testing/match-sim.md†L1-L45】
- **Toolchain guard upkeep** – Exercise the helper scripts under `tools/ci/` to
  refresh expectations or capture new regressions, and cross-check any findings
  against the build recapture notes before filing follow-ups.【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】【F:tools/ci/build-cleanroom.sh†L1-L44】【F:docs/reverse-engineering/build-recapture.md†L41-L75】
- **Documentation traceability** – For any functions you investigate, annotate
  the mapping spreadsheet in `docs/reference-mapping.md` and log follow-ups in
  `docs/documentation-backlog.md` to keep the team aligned on outstanding gaps.【F:docs/reference-mapping.md†L1-L42】【F:docs/documentation-backlog.md†L1-L40】
- **Mentorship sync** – Pair with your assigned mentor from the rotation schedule
  in the repository root README to review findings, unblock questions, and plan
  next steps; the rotation restarts every four weeks.【F:README.md†L8-L31】

Stay in sync with the #reverse-engineering channel in Slack for daily stand-ups,
and reference the refreshed onboarding overview and handbook whenever processes,
artefact locations, or review cadence shift.【F:docs/onboarding/overview.md†L1-L89】【F:docs/reverse-engineering/handbook.md†L1-L60】
