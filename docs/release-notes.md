# Release Notes

## Process Updates – August 2024
- Updated the pull request template to require reviewer-accessible links for harness run results, baseline diffs, and syscall contract records.
- Published refreshed contributor guidance describing the local harness execution expectations and when `N/A` justifications are acceptable.
- Announced the verification policy changes here and in the internal ops channel so every team can adapt their workflows.

## Documentation Updates – July 2024
- Centralised the gameplay parity documentation under `docs/gameplay/parity/README.md`, including owner contact links and a verification checklist for cross-team reviews.

## Documentation Updates – May 2024
- Added the **Gameplay Parity Ledger** (`docs/gameplay/parity/parity-ledger.md`) outlining porting status, HLIL references, and code owner contacts for core gameplay systems.
- Published a **Regression Rationale Template** (`docs/gameplay/parity/regression-rationale-template.md`) to standardise post-mortems and ensure sign-off from gameplay, QA, and release owners.
- Logged **HLIL Mapping Updates** (`docs/gameplay/parity/hlil-mapping-updates.md`) so feature teams can trace gameplay changes back to the latest decompilation references.

Contributors should review the new parity documentation before merging gameplay-affecting changes and tag the listed owners in their pull requests for verification.

## Process Updates – July 2024
- Tightened the pull request template to require reviewer-accessible links for harness runs, baseline diffs, and syscall contract updates (with `N/A` allowed only when justified).
- Expanded the contributor checklist with concrete expectations for documenting local harness executions and link validation before review.
- Posted an internal announcement and updated these release notes so every team is aware of the new verification requirements.
