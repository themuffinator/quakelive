# Release Notes

## Documentation Updates – May 2024
- Added the **Gameplay Parity Ledger** (`docs/gameplay/parity/parity-ledger.md`) outlining porting status, HLIL references, and code owner contacts for core gameplay systems.
- Published a **Regression Rationale Template** (`docs/gameplay/parity/regression-rationale-template.md`) to standardise post-mortems and ensure sign-off from gameplay, QA, and release owners.
- Logged **HLIL Mapping Updates** (`docs/gameplay/parity/hlil-mapping-updates.md`) so feature teams can trace gameplay changes back to the latest decompilation references.

Contributors should review the new parity documentation before merging gameplay-affecting changes and tag the listed owners in their pull requests for verification.

## Process Updates – June 2024
- Added a mandatory pull request template requiring links to harness runs, baseline diffs, and syscall contract documentation.
- Published a contributor checklist outlining local validation expectations before opening a PR.
- Announced these changes internally so feature teams know where to find the new process docs.
