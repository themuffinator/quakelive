# Contributor Checklist

This checklist sets expectations for local validation before submitting a pull request. Completing these steps keeps the reverse engineering effort reproducible and protects the shared baselines.

Before opening a pull request you should be able to hand a reviewer everything they need to deterministically replay your work: the exact harness command lines (with seeds), the refreshed baselines, and a pointer to the syscall contract changelog when behaviour crosses that boundary.

## UI Retail Assets Are Frozen
- The retail menu sources in `src/ui/` are immutable; CI checks will block any pull request that modifies files in that path.
- Route UI tweaks through code-driven hooks or layered asset overrides (for example, extend the packaging manifest consumed by `tools/build_ui_bundle.sh` instead of patching the retail menus directly).
- When a change truly requires a new UI asset, add it as an overlay package so reviewers can isolate the delta without disturbing the upstream retail files.

## 1. Prepare Your Workspace
- Sync with the latest `main` branch and rebase your work.
- Install or update required toolchains (see `docs/toolchain-ci.md`).
- Ensure large assets or proprietary references are mounted if your change depends on them.

## 2. Run the Relevant Harnesses Locally
- Identify the harness suites that cover your change area (engine, UI, syscall boundary, etc.).
- Execute the suites locally before pushing for review. Record the full command (including deterministic seed/fixture flags), the git revision, and the host you executed on.
- Verify the run is deterministic by re-executing at least once and confirming the emitted hashes, traces, or match timelines are identical.
- Export the run artifacts to a durable location (CI dashboard, shared drive, or local HTML report) that reviewers can open.
- Capture the resulting URL or artifact path—you must paste this into the **Harness run(s)** field of the PR template.
- Store the raw command output or HTML bundle in `artifacts/harness-runs/` (or the team SharePoint) so it remains accessible for at least 30 days.
- If a suite cannot be executed locally, document why (e.g. missing hardware target) and escalate to the module owner before opening the PR.
- Marking `N/A` in the PR template is acceptable only after the module owner confirms the exemption and you note the reason.

## 3. Update Baselines When Behaviour Changes
- Regenerate golden assets, network traces, or expected outputs when your change modifies behaviour.
- Compare the regenerated artefacts against the prior version to confirm the delta reflects your change and remains deterministic between runs.
- Stage the baseline updates in the same commit set and link the comparison in your PR so reviewers can diff the behaviour.
- When no baselines change, explicitly note "N/A – no behaviour deltas" in the template so reviewers know the check was performed.

## 4. Document Syscall Contract Changes
- When altering syscall signatures, parameter semantics, or return values, record the change in the syscall contract documentation.
- Spell out any determinism-sensitive expectations (ordering, timeouts, retries) introduced by the change so harness owners can update their fixtures.
- Notify dependent teams (launcher, UI, and tooling) of the change and capture acknowledgement.
- Link the contract update in the PR template to provide reviewers with context.
- Include the date and reviewer acknowledgement in the contract log entry so downstream maintainers can audit the change.

## 5. Final Verification Before Opening the PR
- Run static analysis or linting relevant to your subsystem.
- Re-run smoke harnesses after rebasing to catch integration issues and confirm deterministic artefacts remain stable.
- Fill in every required field of the pull request template, including links to harness runs, baseline updates, and syscall contract edits (use "N/A" only with justification).
- Double-check that every link you provide resolves for the reviewer (test in an incognito browser session when possible).

Sticking to this checklist ensures reviewers can trust that the incoming changes respect the shared baselines and syscall guarantees.
