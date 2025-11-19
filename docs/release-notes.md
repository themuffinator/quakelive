# Release Notes

## Gameplay Parity Updates – October 2024
- **BG_CanItemBeGrabbed parity tables** – The shared `bg_misc.c` implementation that backs both qagame and cgame prediction now reads from the same HLIL-derived case tables, so any change to the handler list must keep both modules in sync (`CG_TouchItem` still delegates to `BG_CanItemBeGrabbed`). The regenerated tables live alongside the Binary Ninja exports under `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/` (`sub_1002ced0` and its `data_100809e4` block) and `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/` (`sub_10001560` and its `data_10067294` block). When the HLIL artifacts change: 1) re-export the qagame and cgame DLLs and replace the `_hlil_part*.txt` files in those directories, 2) diff the updated case tables against `src/code/game/bg_misc.c`'s `bg_itemGrabHandlers` wiring and adjust the helper implementations, and 3) rebuild both qagame and cgame (verifying `src/code/cgame/cg_predict.c::CG_TouchItem` still calls into the shared helper) so server and client prediction stay identical.

## Process Updates – September 2024
- Re-emphasised deterministic harness expectations, baseline refresh discipline, and syscall contract logging in the contributor checklist.
- Cross-linked the checklist from the PR template and onboarding overview so new contributors see the requirements before their first submission.
- Posted an announcement in the `#reverse-maintenance` Slack channel summarising the stricter pre-flight requirements and linking back to the updated documentation.

## Process Updates – August 2024
- Updated the pull request template to require reviewer-accessible links for harness run results, baseline diffs, and syscall contract records.
- Published refreshed contributor guidance describing the local harness execution expectations and when `N/A` justifications are acceptable.
- Announced the verification policy changes here and in the internal ops channel so every team can adapt their workflows.

## Documentation Updates – August 2024
- Gameplay parity documents (`docs/gameplay/parity/`) now include owner cross-check banners so teams know who last validated the content and who to ping for follow-up.
- The parity hub README records the expected review cadence, ensuring changes to the ledger, regression rationale template, and HLIL mapping log are acknowledged within one business day.
- Release managers should circulate this update in the contributor newsletter to highlight the new verification flow.

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
