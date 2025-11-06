# Reverse Engineering Track Onboarding Guide

Welcome to the Quake Live reverse-engineering track. This guide walks you through the
required environment setup, curated reading order, and starter tasks that will help
you contribute effectively to the reconstruction effort.

## Environment setup checklist

1. **Clone the repository**
   ```bash
   git clone git@github.com:id-software/quakelive-reverse.git
   cd quakelive-reverse
   ```
2. **Install QVM toolchain prerequisites**
   - Follow the Linux build instructions in [`docs/qvmtools.md`](../qvmtools.md) to
     install `gcc-multilib`, `make`, and the patched LCC toolchain.
   - Run `tools/ci/verify-qvm-toolchain.sh` to ensure the bytecode compilers match
     the CI reference output.
3. **Configure native Windows build tooling (optional but recommended)**
   - Review [`docs/build/windows.md`](../build/windows.md) for Visual Studio 2010
     prerequisites and MSBuild targets.
   - If you do not have a Windows host, provision the documented VM image or
     coordinate with a teammate who can validate DLL builds.
4. **Set up analysis tooling**
   - Install Ghidra 10.3 or later for binary diffing and HLIL export comparison.
   - Configure Binary Ninja with the Quake-specific HLIL projects stored under
     `references/hlil/` for side-by-side analysis.
5. **Bootstrap testing harnesses**
   - Create a Python virtual environment and install harness dependencies with
     `pip install -r tools/tests/requirements.txt`.
   - Execute the deterministic match simulation smoke test via
     `python tools/tests/match_sim.py --demo samples/ffa_8p.dm_73` to validate your
     environment matches CI expectations.

## Recommended reading order

1. **Repository Overview** – Start with [`docs/repo-overview.md`](../repo-overview.md)
   to understand how Quake Live artifacts map onto the GPL code drop.
2. **Onboarding Overview** – Skim [`docs/onboarding/overview.md`](overview.md) for the
   high-level workflow summary and key documentation entry points.
3. **Reverse-engineering references** – Read [`docs/reverse-engineering/reconstruction-tracker.md`](../reverse-engineering/reconstruction-tracker.md)
   followed by the Binary Ninja comparison in [`docs/hlil_comparison.md`](../hlil_comparison.md)
   to learn how we diff HLIL output against the reconstructed sources.
4. **Build & Toolchain guides** – Work through [`docs/qvmtools.md`](../qvmtools.md),
   [`docs/build/windows.md`](../build/windows.md), and [`docs/toolchain-ci.md`](../toolchain-ci.md)
   so you understand the guardrails that keep bytecode and native builds aligned.
5. **Testing harness documentation** – Finish with [`docs/testing-strategy.md`](../testing-strategy.md),
   [`docs/testing/match-sim.md`](../testing/match-sim.md), and [`docs/testing/rules-fixtures.md`](../testing/rules-fixtures.md)
   to learn how gameplay fixtures prove functional parity.

## Starter tasks

- **Baseline parity audit** – Choose a gameplay system (e.g., weapon prediction or
  item respawn logic) and confirm the reconstructed source matches the Quake Live
  HLIL dump. Capture findings in `docs/reverse-engineering/` with before/after
  snippets and note any unknown branches.
- **Harness enrichment** – Extend the deterministic match simulation fixtures with
  an additional edge case, such as sudden-death overtime or multi-weapon loadouts.
  Update `tools/tests/match_sim.py` and document the scenario in
  `docs/testing/match-sim.md`.
- **Documentation traceability** – For any functions you investigate, annotate
  the mapping spreadsheet in `docs/reference-mapping.md` and file follow-ups in
  `docs/documentation-backlog.md` to keep the team aligned on outstanding gaps.
- **Mentorship sync** – Pair with your assigned mentor from the rotation schedule
  in the repository root README to review findings, unblock questions, and plan
  next steps.

Stay in sync with the #reverse-engineering channel in Slack for daily stand-ups
and reach out to the mentorship rotation if blockers surface.
