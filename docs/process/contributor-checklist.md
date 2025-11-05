# Contributor Checklist

This checklist sets expectations for local validation before submitting a pull request. Completing these steps keeps the reverse engineering effort reproducible and protects the shared baselines.

## 1. Prepare Your Workspace
- Sync with the latest `main` branch and rebase your work.
- Install or update required toolchains (see `docs/toolchain-ci.md`).
- Ensure large assets or proprietary references are mounted if your change depends on them.

## 2. Run the Relevant Harnesses Locally
- Identify the harness suites that cover your change area (engine, UI, syscall boundary, etc.).
- Execute the suites locally and capture the output URL or artifact path that you will link in the PR template.
- If a suite cannot be executed locally, document why and escalate to the module owner before opening the PR.

## 3. Update Baselines When Behaviour Changes
- Regenerate golden assets, network traces, or expected outputs when your change modifies behaviour.
- Review diffs to confirm they only include intentional updates.
- Stage the baseline updates in the same commit set and link the comparison in your PR.

## 4. Document Syscall Contract Changes
- When altering syscall signatures, parameter semantics, or return values, record the change in the syscall contract documentation.
- Notify dependent teams (launcher, UI, and tooling) of the change and capture acknowledgement.
- Link the contract update in the PR template to provide reviewers with context.

## 5. Final Verification Before Opening the PR
- Run static analysis or linting relevant to your subsystem.
- Re-run smoke harnesses after rebasing to catch integration issues.
- Fill in every required field of the pull request template, including links to harness runs, baseline updates, and syscall contract edits (use "N/A" only with justification).

Sticking to this checklist ensures reviewers can trust that the incoming changes respect the shared baselines and syscall guarantees.
